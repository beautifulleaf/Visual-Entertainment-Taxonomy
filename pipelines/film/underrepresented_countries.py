"""Extra film candidates for under-represented countries (sourcing-plan.md §8, "African film").

The IMDb >=500-vote floor leaves whole film industries almost empty (Nigeria 19
candidates, Ghana 3, Kenya 1). For every country with fewer than MIN_CANDIDATES
films in data/interim/film_ratings.csv (country = MDBList's ISO-2 code), this adds:

  a) IMDb films with 100-499 votes that look like they come from one of those
     countries: an alternative title (title.akas) for a target region, an akas
     language typical of it, or an original title in a script or orthography
     typical of it (Ethiopic, Georgian, Yoruba dot-below letters, ...). MDBList
     then confirms the country; only films whose MDBList country is a target
     country are kept. --no-prefilter skips the guess and checks every
     100-499-vote film through MDBList instead (about 550 requests).
  b) Wikidata films (instances of film or a subclass) whose country of origin
     (P495) is a target country and that carry an IMDb (P345) or TMDB (P4947)
     ID, whatever their vote count. One query per country, run one at a time,
     cached under data/raw/wikidata/film_by_country/.

New IMDb IDs are enriched through MDBList (cache data/raw/mdblist/media_batch_extra.jsonl;
TMDB-only Wikidata films use media_batch_extra_tmdb.jsonl). Films already in
film_ratings.csv are not repeated.

Output: data/interim/film_candidates_extra.csv, film_ratings.csv's columns plus
  source         imdb_100 | wikidata | imdb_100+wikidata
  target_country the under-represented country the film was added for
                 (Wikidata's P495 where it gave one, else MDBList's country)
  wikidata       QID, if found through Wikidata
film_ratings.csv itself is left untouched.

Requires MDBLIST_API_KEY.

Usage:
  python3 pipelines/film/underrepresented_countries.py [--min-candidates 200] [--min-votes 100]
  python3 pipelines/film/underrepresented_countries.py --parse-only   # no network for MDBList
"""
import argparse
import collections
import csv
import gzip
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "common"))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "visual_art"))
import mdblist  # noqa: E402
from wikidata import sparql, year_of  # noqa: E402

RATINGS = os.path.join(ROOT, "data", "interim", "film_ratings.csv")
IMDB_DIR = os.path.join(ROOT, "data", "raw", "imdb")
WD_CACHE = os.path.join(ROOT, "data", "raw", "wikidata", "film_by_country")
CACHE = os.path.join(ROOT, "data", "raw", "mdblist", "media_batch_extra.jsonl")
CACHE_TMDB = os.path.join(ROOT, "data", "raw", "mdblist", "media_batch_extra_tmdb.jsonl")
OUT_PATH = os.path.join(ROOT, "data", "interim", "film_candidates_extra.csv")

FILM_TYPES = {"movie", "tvMovie", "short", "video", "tvSpecial"}
SOURCES = ("letterboxd", "imdb", "tmdb", "trakt")
COLS = ["tconst", "tmdb_id", "mdblist_title", "year", "imdb_title_type", "runtime", "country", "language",
        "imdb_genres", "mdblist_genres"] + [f"{s}_{k}" for s in SOURCES for k in ("value", "votes")]

# MDBList codes that are not countries with a Wikidata ISO-2 (P297) entry.
# UR is MDBList's code for some Pakistani films (Urdu?), XI is Northern Ireland,
# SJ/AQ are a handful of expedition films: no country query for them.
HISTORICAL = {
    "YU": ["Q83286", "Q191077", "Q838261"],  # SFR Yugoslavia, Kingdom of Yugoslavia, FR Yugoslavia
    "XC": ["Q33946"],                         # Czechoslovakia
    "XG": ["Q16957"],                         # East Germany
    "CS": ["Q37024"],                         # Serbia and Montenegro
    "AN": ["Q25227"],                         # Netherlands Antilles
    "XK": ["Q1246"],                          # Kosovo
    "SU": ["Q15180"],                         # Soviet Union
}
NO_QUERY = {"", "UR", "XI", "SJ", "AQ"}
# IMDb akas region codes for historical states, mapped to MDBList's.
AKAS_REGION = {"XYU": "YU", "YUCS": "YU", "CSHH": "XC", "DDDE": "XG", "CSXX": "CS", "SUHH": "SU", "ANHH": "AN",
               "XKO": "XK", "XKV": "XK", "BUMM": "MM", "VDVN": "VN", "ZRCD": "CD"}

# akas `language` codes typical of one country (broad ones like en/fr/ar/es/pt/zh are left out
# on purpose: they would pull in every Egyptian, Brazilian or mainland Chinese film).
LANGS = {
    "NG": "yo ig ha pcm", "GH": "ak tw ee gaa", "KE": "sw ki luo", "TZ": "sw", "ET": "am om ti", "ER": "ti",
    "SN": "wo ff", "ML": "bm", "BF": "mos", "ZA": "af zu xh st tn nso ts", "ZW": "sn nd", "UG": "lg",
    "RW": "rw", "SO": "so", "MG": "mg", "CD": "ln", "BD": "bn", "NP": "ne", "LK": "si", "PK": "ur",
    "UR": "ur", "GE": "ka", "AM": "hy", "AZ": "az", "KZ": "kk", "KG": "ky", "TJ": "tg", "UZ": "uz",
    "MN": "mn", "KH": "km", "LA": "lo", "MM": "my", "VN": "vi", "MY": "ms", "EE": "et", "LV": "lv",
    "LT": "lt", "IS": "is", "SI": "sl", "SK": "sk", "CZ": "cs", "XC": "cs", "MK": "mk", "BG": "bg",
    "HR": "hr", "RS": "sr", "BA": "bs", "UA": "uk", "BY": "be", "AL": "sq", "XK": "sq", "IL": "he yi",
    "MT": "mt", "LU": "lb", "BT": "dz", "AF": "ps", "TW": "nan", "MD": "ro", "HT": "ht", "PH": "tl",
}
# Scripts and orthographies of the original title that point to a country.
SCRIPTS = [
    (re.compile(r"[ሀ-፿]"), ("ET", "ER")),        # Ethiopic
    (re.compile(r"[Ⴀ-ჿ]"), ("GE",)),             # Georgian
    (re.compile(r"[԰-֏]"), ("AM",)),             # Armenian
    (re.compile(r"[඀-෿]"), ("LK",)),             # Sinhala
    (re.compile(r"[ក-៿]"), ("KH",)),             # Khmer
    (re.compile(r"[຀-໿]"), ("LA",)),             # Lao
    (re.compile(r"[က-႟]"), ("MM",)),             # Myanmar
    (re.compile(r"[ঀ-৿]"), ("BD",)),             # Bengali
    (re.compile(r"[֐-׿]"), ("IL",)),             # Hebrew
    (re.compile(r"[ༀ-࿿]"), ("BT",)),             # Tibetan / Dzongkha
    (re.compile(r"[ẸẹỌọṢṣ]|̣"), ("NG",)),  # Yoruba/Igbo dot-below letters
    (re.compile(r"[ɔɛƆƐ]"), ("GH",)),  # Akan/Ewe open o, open e
]


def candidate_counts():
    with open(RATINGS, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows, collections.Counter(r["country"] for r in rows)


# ---------------------------------------------------------------- Wikidata

def country_qids(codes):
    """ISO-2 code -> Wikidata country QIDs (P297), plus historical states."""
    path = os.path.join(WD_CACHE, "_iso2.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            iso = json.load(f)
    else:
        iso = collections.defaultdict(list)
        for r in sparql("SELECT ?c ?code WHERE { ?c wdt:P297 ?code }", retries=4):
            iso[r["code"].upper()].append(r["c"])
        os.makedirs(WD_CACHE, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(iso, f)
    return {c: HISTORICAL.get(c) or iso.get(c, []) for c in codes if c not in NO_QUERY}


FILM_QUERY = """SELECT ?film (SAMPLE(?imdb) AS ?tconst) (SAMPLE(?tmdb) AS ?tmdb_id) (SAMPLE(?l) AS ?label) (MIN(?d) AS ?date)
WHERE {{
  VALUES ?country {{ {countries} }}
  ?film wdt:P495 ?country ; {cls} .
  OPTIONAL {{ ?film wdt:P345 ?imdb }} OPTIONAL {{ ?film wdt:P4947 ?tmdb }}
  FILTER(BOUND(?imdb) || BOUND(?tmdb))
  OPTIONAL {{ ?film rdfs:label ?l FILTER(LANG(?l) = "en") }} OPTIONAL {{ ?film wdt:P577 ?d }}
}} GROUP BY ?film"""
# Fallback when the subclass walk times out: the common film classes, directly.
FILM_CLASSES = ("wd:Q11424 wd:Q24869 wd:Q24862 wd:Q93204 wd:Q202866 wd:Q506240 wd:Q226730 wd:Q130232 "
                "wd:Q157443 wd:Q2484376 wd:Q17013749 wd:Q842256 wd:Q1054574 wd:Q200092")


def wikidata_films(code, qids):
    """Films from one country, cached per country; None if Wikidata keeps failing."""
    path = os.path.join(WD_CACHE, f"{code}.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    countries = " ".join(f"wd:{q}" for q in qids)
    rows = None
    for cls in ("wdt:P31/wdt:P279* wd:Q11424", f"wdt:P31 ?cls . VALUES ?cls {{ {FILM_CLASSES} }}"):
        try:
            rows = sparql(FILM_QUERY.format(countries=countries, cls=cls), retries=3)
            break
        except RuntimeError:
            print(f"    {code}: query failed, trying the simpler class filter")
    if rows is None:
        print(f"    {code}: Wikidata unavailable, skipped (not cached; re-run to retry)")
        return None
    os.makedirs(WD_CACHE, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f)
    return rows


def harvest_wikidata(targets):
    """tconst/tmdb key -> {qid, label, year, countries}. Strictly one query at a time."""
    qids = country_qids(targets)
    films = {}
    for code in sorted(qids, key=lambda c: targets[c]):
        if not qids[code]:
            print(f"    {code}: no Wikidata country item, skipped")
            continue
        rows = wikidata_films(code, qids[code])
        if rows is None:
            continue
        for r in rows:
            tconst = r.get("tconst", "")
            if tconst and not re.fullmatch(r"tt\d+", tconst):
                tconst = ""
            key = tconst or f"tmdb:{r.get('tmdb_id')}"
            f = films.setdefault(key, {"qid": r["film"], "tconst": tconst, "tmdb_id": r.get("tmdb_id", ""),
                                       "label": r.get("label", ""), "year": year_of(r.get("date")),
                                       "countries": []})
            f["countries"].append(code)
    print(f"Wikidata: {len(films)} films with an IMDb or TMDB ID across {len(qids)} countries")
    return films


# ---------------------------------------------------------------- IMDb

def imdb_pool(min_votes, max_votes, extra_ids):
    """Votes for 100-499-vote titles, and basics for those plus the Wikidata IDs."""
    votes = {}
    with gzip.open(os.path.join(IMDB_DIR, "title.ratings.tsv.gz"), "rt", encoding="utf-8") as f:
        next(f)
        for line in f:
            t, avg, n = line.rstrip("\n").split("\t")
            votes[t] = (avg, int(n))
    basics = {}
    with gzip.open(os.path.join(IMDB_DIR, "title.basics.tsv.gz"), "rt", encoding="utf-8") as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            in_pool = min_votes <= votes.get(p[0], (0, 0))[1] < max_votes
            if (in_pool or p[0] in extra_ids) and p[1] in FILM_TYPES and p[4] != "1":
                basics[p[0]] = {"title_type": p[1], "title": p[2], "original_title": p[3], "year": p[5],
                                "runtime": p[7], "genres": p[8], "in_pool": in_pool}
    return votes, basics


def akas_hints(pool, targets):
    """tconst -> set of target countries suggested by akas region or language."""
    lang_to = collections.defaultdict(set)
    for c, langs in LANGS.items():
        if c in targets:
            for lang in langs.split():
                lang_to[lang].add(c)
    hints = collections.defaultdict(set)
    with gzip.open(os.path.join(IMDB_DIR, "title.akas.tsv.gz"), "rt", encoding="utf-8") as f:
        next(f)
        for line in f:
            t = line[:line.index("\t")]
            if t not in pool:
                continue
            p = line.rstrip("\n").split("\t")
            region = AKAS_REGION.get(p[3], p[3])
            if region in targets:
                hints[t].add(region)
            if p[4] in lang_to:
                hints[t] |= lang_to[p[4]]
            for rx, cs in SCRIPTS:
                if rx.search(p[2]):
                    hints[t] |= {c for c in cs if c in targets}
    return hints


# ---------------------------------------------------------------- MDBList

def enrich(tconsts, tmdb_ids, key):
    if tconsts:
        mdblist.fetch_all(key, sorted(tconsts), CACHE, "movie")
    if tmdb_ids:
        saved = mdblist.API
        mdblist.API = "https://api.mdblist.com/tmdb/{kind}"
        try:
            mdblist.fetch_all(key, sorted(tmdb_ids), CACHE_TMDB, "movie")
        finally:
            mdblist.API = saved


def load_items():
    by_imdb, by_tmdb = {}, {}
    for path in (CACHE, CACHE_TMDB):
        if os.path.exists(path):
            for item in mdblist.cached_items(path):
                if mdblist.imdb_id_of(item):
                    by_imdb[mdblist.imdb_id_of(item)] = item
                tmdb = (item.get("ids") or {}).get("tmdb")
                if tmdb:
                    by_tmdb[str(tmdb)] = item
    return by_imdb, by_tmdb


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-candidates", type=int, default=200)
    ap.add_argument("--min-votes", type=int, default=100)
    ap.add_argument("--max-votes", type=int, default=500, help="the main candidate floor (exclusive)")
    ap.add_argument("--no-prefilter", action="store_true", help="send every 100-499-vote film to MDBList")
    ap.add_argument("--parse-only", action="store_true", help="use the MDBList caches only")
    args = ap.parse_args()

    existing, before = candidate_counts()
    have = {r["tconst"] for r in existing}
    targets = {c: n for c, n in before.items() if n < args.min_candidates and c not in NO_QUERY}
    print(f"{len(targets)} countries with < {args.min_candidates} candidates:")
    print("  " + ", ".join(f"{c} {n}" for c, n in sorted(targets.items(), key=lambda x: -x[1])))

    wd = harvest_wikidata(targets)
    wd_ids = {f["tconst"] for f in wd.values() if f["tconst"]}
    votes, basics = imdb_pool(args.min_votes, args.max_votes, wd_ids)
    pool = {t for t, b in basics.items() if b["in_pool"] and t not in have}
    print(f"IMDb: {len(pool)} film-like titles with {args.min_votes}-{args.max_votes - 1} votes not yet candidates")
    hints = akas_hints(pool, targets)
    for t in pool:  # original title script / orthography
        for rx, cs in SCRIPTS:
            if rx.search(basics[t]["original_title"]):
                hints[t] |= {c for c in cs if c in targets}
    imdb_ids = pool if args.no_prefilter else {t for t in pool if hints.get(t)}
    print(f"  {len(hints)} with a target-country hint; sending {len(imdb_ids)} to MDBList")

    # Wikidata films that are TV series etc. in IMDb are dropped; IDs IMDb lacks are kept.
    wd_new = {k: f for k, f in wd.items()
              if (f["tconst"] and f["tconst"] not in have and (f["tconst"] in basics or f["tconst"] not in votes))
              or (not f["tconst"] and f["tmdb_id"])}
    tmdb_only = {f["tmdb_id"] for f in wd_new.values() if not f["tconst"]}
    if not args.parse_only:
        enrich(imdb_ids | {f["tconst"] for f in wd_new.values() if f["tconst"]}, tmdb_only, mdblist.api_key())
    by_imdb, by_tmdb = load_items()

    out = {}
    for t in imdb_ids:
        item = by_imdb.get(t)
        if item and (item.get("country") or "").upper() in targets:
            row = mdblist.add_ratings(mdblist.base_row(item, basics[t]), item, SOURCES)
            row.update(source="imdb_100", target_country=row["country"], wikidata="")
            out[t] = row
    for f in wd_new.values():
        item = by_imdb.get(f["tconst"]) if f["tconst"] else by_tmdb.get(str(f["tmdb_id"]))
        tconst = f["tconst"] or (mdblist.imdb_id_of(item) if item else "")
        if tconst and tconst in have:
            continue
        b = basics.get(tconst, {})
        if item:
            row = mdblist.add_ratings(mdblist.base_row(item, b), item, SOURCES)
        else:  # not in MDBList: keep what IMDb and Wikidata give
            row = {"tmdb_id": f["tmdb_id"], "mdblist_title": f["label"] or b.get("title", ""),
                   "year": b.get("year") if b.get("year", "\\N") != "\\N" else (f["year"] or ""),
                   "imdb_title_type": b.get("title_type", ""), "country": "",
                   "imdb_genres": b.get("genres", "").replace(",", "|").replace("\\N", "")}
            if tconst in votes:
                row["imdb_value"], row["imdb_votes"] = votes[tconst]
        row["tconst"] = tconst
        k = tconst or f"tmdb:{f['tmdb_id']}"
        tc = row.get("country") if row.get("country") in f["countries"] else f["countries"][0]
        if k in out:
            out[k].update(source="imdb_100+wikidata", wikidata=f["qid"])
        else:
            row.update(source="wikidata", target_country=tc, wikidata=f["qid"])
            out[k] = row

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=COLS + ["source", "target_country", "wikidata"], extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted(out.values(), key=lambda r: (r["target_country"], str(r.get("year") or ""))))

    # Report
    rows = list(out.values())
    added = collections.Counter(r["target_country"] for r in rows)
    lb = collections.Counter(r["target_country"] for r in rows if r.get("letterboxd_votes"))
    lb1k = collections.Counter(r["target_country"] for r in rows if int(r.get("letterboxd_votes") or 0) >= 1000)
    src = collections.Counter(r["source"] for r in rows)
    print(f"\n{len(rows)} extra candidates ({dict(src)}); "
          f"{sum(lb.values())} with a Letterboxd count, {sum(lb1k.values())} with >= 1k")
    print(f"{'country':8}{'before':>8}{'added':>8}{'after':>8}{'LB':>7}{'LB>=1k':>8}")
    for c in sorted(targets, key=lambda c: -(targets[c] + added[c])):
        print(f"{c:8}{targets[c]:>8}{added[c]:>8}{targets[c] + added[c]:>8}{lb[c]:>7}{lb1k[c]:>8}")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
