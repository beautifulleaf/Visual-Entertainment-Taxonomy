"""Fetch the film canon/curation lists and match them to IMDb title IDs.

A film enters the taxonomy if it is on any canon list, whatever its Letterboxd
count (docs/sourcing-plan.md section 2). Lists fetched:

  sight_and_sound_critics_2022    BFI page (embedded JSON): the full published
                                  critics' list, 264 films (top 250 with ties)
  sight_and_sound_directors_2022  BFI page: directors' top 100 (104 with ties)
  tspdt_1000                      theyshootpictures.com, 1000 Greatest Films
  tspdt_21st_century_1000         theyshootpictures.com, 21st Century's 1000
  criterion                       Wikipedia "List of films in the Criterion
                                  Collection": individual spines, box sets,
                                  director box sets (criterion.com returns 403)
  criterion_eclipse               same page, Eclipse series
  palme_dor, golden_lion,         Wikipedia winner tables (all co-winners kept)
  golden_bear
  oscar_best_picture              Wikipedia, winners only
  oscar_international_feature     Wikipedia, winners (incl. 1947-55 honorary)
  national_film_registry          Wikipedia "National Film Registry" table

Every page is cached under data/raw/canon/ (delete a file to refetch it);
requests go out one at a time, at least 1 s apart.

Matching is local, against IMDb's datasets in data/raw/imdb/ (run
build_candidates.py first): normalised title (primaryTitle or originalTitle,
accent-, case-, punctuation- and leading-article-insensitive) and year +-1,
preferring titleType movie, then the most IMDb votes. Alternative titles a
source gives (original title, title before a colon) are tried next, then
IMDb's alternative titles (title.akas, English-language regions plus original
titles; downloaded on first run, ~500 MB), then a +-2 year window.

Output: data/interim/film_canon.csv, one row per (list, film):
  list, rank_or_award, title, year, director, tconst, match_method
tconst is empty when no match was found. A summary (per-list counts and match
rates, unmatched titles, distinct films, films added beyond the >=10k
Letterboxd rule from data/interim/film_ratings.csv) is printed.

Usage: python3 pipelines/film/canon_lists.py [--lists criterion,palme_dor] [--refresh]
"""
import argparse
import csv
import gzip
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"
MIN_INTERVAL = 1.0

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE_DIR = os.path.join(ROOT, "data", "raw", "canon")
IMDB_DIR = os.path.join(ROOT, "data", "raw", "imdb")
RATINGS_PATH = os.path.join(ROOT, "data", "interim", "film_ratings.csv")
OUT_PATH = os.path.join(ROOT, "data", "interim", "film_canon.csv")

# Lower is preferred. Series types are kept because a few canon entries are
# miniseries on IMDb (Dekalog, Berlin Alexanderplatz, Histoire(s) du cinema).
TYPE_RANK = {"movie": 0, "tvMovie": 1, "video": 1, "tvSpecial": 1, "short": 2,
             "tvMiniSeries": 3, "tvShort": 3, "tvSeries": 4}

AKA_REGIONS = {"US", "GB", "XWW", "CA", "AU", "IE", "IN"}

WIKI = "https://en.wikipedia.org/wiki/{}?action=raw"

_last_request = [0.0]


# ---------------------------------------------------------------- fetching

def fetch(url, cache_name, refresh=False):
    """Return the page text, from the cache when present."""
    path = os.path.join(CACHE_DIR, cache_name)
    if os.path.exists(path) and not refresh:
        with open(path, encoding="utf-8") as f:
            return f.read()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(6):
        wait = _last_request[0] + MIN_INTERVAL - time.time()
        if wait > 0:
            time.sleep(wait)
        _last_request[0] = time.time()
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                text = r.read().decode("utf-8")
            break
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                delay = int(e.headers.get("Retry-After") or 0) or 15 * (attempt + 1)
                print(f"  HTTP {e.code} for {url}; retrying in {delay}s", file=sys.stderr)
                time.sleep(delay)
            else:
                raise
        except urllib.error.URLError:
            time.sleep(2 ** attempt)
    else:
        raise RuntimeError(f"giving up on {url}")
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return text


def wiki(title, refresh):
    return fetch(WIKI.format(urllib.parse.quote(title)), "wiki_" + re.sub(r"\W+", "_", title) + ".wikitext", refresh)


# ---------------------------------------------------------------- wikitext

def _resolve_link(m):
    inner = m.group(1)
    if re.match(r"(?i)(file|image|category):", inner):
        return ""
    return inner.split("|")[-1]


def _resolve_template(m):
    parts = [p.strip() for p in m.group(1).split("|")]
    name = parts[0].lower()
    args = [p for p in parts[1:] if not re.match(r"^[\w-]+\s*=", p)]
    if name == "sort":
        return args[-1] if args else ""
    if name == "sortname":
        if len(args) >= 3 and args[2]:
            return args[2]
        return " ".join(args[:2])
    if name in ("small", "nowrap", "nobold", "center", "abbr", "lang-fr"):
        return args[0] if args else ""
    if name == "lang":
        return args[1] if len(args) > 1 else ""
    return ""  # efn, dagger, asterisk, cite..., refn: drop


def clean(raw):
    """Wikitext cell -> plain text."""
    s = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    s = re.sub(r"<ref[^>/]*/>", "", s)
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"<small>.*?</small>", "", s, flags=re.S)
    for _ in range(10):
        s2 = re.sub(r"\[\[([^\[\]]*)\]\]", _resolve_link, s)
        s2 = re.sub(r"\{\{([^{}]*)\}\}", _resolve_template, s2)
        if s2 == s:
            break
        s = s2
    s = re.sub(r"\[https?://\S+\s*([^\]]*)\]", r"\1", s)
    s = s.replace("'''", "").replace("''", "")
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip()


def _split_top(s, sep):
    """Split on sep outside [[...]] and {{...}}."""
    out, depth, cur, i = [], 0, [], 0
    while i < len(s):
        if s.startswith("[[", i) or s.startswith("{{", i):
            depth += 1; cur.append(s[i:i + 2]); i += 2; continue
        if (s.startswith("]]", i) or s.startswith("}}", i)) and depth:
            depth -= 1; cur.append(s[i:i + 2]); i += 2; continue
        if depth == 0 and s.startswith(sep, i):
            out.append("".join(cur)); cur = []; i += len(sep); continue
        cur.append(s[i]); i += 1
    out.append("".join(cur))
    return out


ATTR_RE = re.compile(r'^\s*([\w-]+\s*=\s*("[^"]*"|\'[^\']*\'|[^\s"]+)\s*)+$')


def _cell(text, is_header):
    parts = _split_top(text, "|")
    attrs, content = "", text
    if len(parts) > 1 and (ATTR_RE.match(parts[0]) or re.match(r"^\s*data-sort-value\s*=", parts[0])):
        attrs, content = parts[0], "|".join(parts[1:])
    span = lambda k: int((re.search(k + r'\s*=\s*"?(\d+)', attrs) or [0, 1])[1])
    return {"raw": content.strip(), "text": clean(content), "rowspan": span("rowspan"),
            "colspan": span("colspan"), "header": is_header}


def wikitables(text):
    """Parse every top-level wikitable into {'headers': [...], 'rows': [...]}.
    Each row is {'attrs': str, 'cells': [cell...]}, with rowspan/colspan expanded."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    tables, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        if not lines[i].startswith("{|"):
            i += 1
            continue
        raw_rows, cur, depth = [], None, 0
        i += 1
        while i < len(lines):
            ln = lines[i]
            if ln.startswith("{|"):
                depth += 1
            if ln.startswith("|}"):
                if depth == 0:
                    break
                depth -= 1
            if depth == 0:
                if ln.startswith("|-"):
                    cur = {"attrs": ln[2:], "cells": []}
                    raw_rows.append(cur)
                elif ln.startswith("|+"):
                    pass
                elif ln.startswith("!") or ln.startswith("|"):
                    if cur is None:
                        cur = {"attrs": "", "cells": []}
                        raw_rows.append(cur)
                    hdr = ln.startswith("!")
                    body = ln[1:]
                    pieces = _split_top(body, "!!") if hdr else [body]
                    for p in pieces:
                        for q in _split_top(p, "||"):
                            cur["cells"].append([q, hdr])
                elif cur is not None and cur["cells"]:
                    cur["cells"][-1][0] += "\n" + ln
            i += 1
        i += 1
        headers, rows, pending = None, [], {}
        for r in raw_rows:
            if not r["cells"]:
                continue
            cells = [_cell(t, h) for t, h in r["cells"]]
            if headers is None and all(c["header"] for c in cells):
                headers = [c["text"] for c in cells for _ in range(c["colspan"])]
                continue
            out, col = [], 0
            queue = list(cells)
            while queue or col in pending:
                if col in pending:
                    left, c = pending[col]
                    out.append(c)
                    if left <= 1:
                        del pending[col]
                    else:
                        pending[col] = (left - 1, c)
                    col += 1
                    continue
                c = queue.pop(0)
                for _ in range(c["colspan"]):
                    out.append(c)
                    if c["rowspan"] > 1:
                        pending[col] = (c["rowspan"] - 1, c)
                    col += 1
            rows.append({"attrs": r["attrs"], "cells": out})
        tables.append({"headers": headers or [], "rows": rows})
    return tables


def col_index(headers, *keys):
    for k in keys:
        for j, h in enumerate(headers):
            if h.lower().startswith(k.lower()):
                return j
    return None


def first_year(s):
    m = re.search(r"\b(1[89]\d\d|20\d\d)\b", s or "")
    return int(m.group(1)) if m else None


def entry(lst, rank, title, year, director="", alts=()):
    # drop Wikipedia disambiguators ("Diva (film)") and TSPDT ones ("Heat [1995]")
    title = re.sub(r"\s*(\((\d{4} )?film\)|\[(\d{4}|TV)\])$", "", title.strip())
    return {"list": lst, "rank_or_award": str(rank), "title": title, "year": year,
            "director": director, "alts": [a for a in alts if a and a != title]}


# ---------------------------------------------------------------- sources

def bfi(lst, url, cache, refresh):
    page = fetch(url, cache, refresh)
    start = page.index("var initialPageState = ") + len("var initialPageState = ")
    blob = page[start:page.index("</script>", start)].strip().rstrip(";")
    results = json.loads(blob)["componentState"]["results"]
    out = []
    for r in sorted(results, key=lambda r: r["rank"]):
        f = r["film"]
        rank = f"{r['rank']}{'=' if r.get('tied') else ''}"
        director = (f.get("credits") or {}).get("director") or ""
        out.append(entry(lst, rank, f["name"].strip(), first_year(f.get("year")), director))
    return out


ARTICLES = r"The|A|An|Le|La|Les|L'|Il|Lo|I|Gli|Der|Die|Das|El|Los|Las|Un|Une|O|Os|As|De|Het|Een|Den|Det|Ett|En"


def uninvert(title):
    m = re.match(rf"^(.*), ({ARTICLES})$", title)
    if not m:
        return title
    return m.group(2) + ("" if m.group(2).endswith("'") else " ") + m.group(1)


def tspdt(lst, url, cache, refresh):
    page = fetch(url, cache, refresh)
    tbody = page[page.index("<tbody>"):page.index("</tbody>")]
    out = []
    for tr in re.findall(r"<tr>(.*?)</tr>", tbody, re.S):
        cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
                 for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(cells) < 5:
            continue
        pos, _, title, director, year = cells[:5]
        if "," in director and "/" not in director and "&" not in director:
            last, first = director.split(",", 1)
            director = f"{first.strip()} {last.strip()}"
        title = re.sub(r"\s*\[(\d{4}|TV)\]$", "", title)
        out.append(entry(lst, pos, uninvert(title), first_year(year), director, alts=[title]))
    return out


def criterion(refresh):
    text = wiki("List of films in the Criterion Collection", refresh)
    out = []
    for t in wikitables(text):
        h = t["headers"]
        ti = col_index(h, "Included films", "Film")
        if ti is None or (h and h[ti] == "Film Release Year"):
            continue
        yi, di = col_index(h, "Film Release Year", "Year"), col_index(h, "Director")
        eclipse = col_index(h, "Series") is not None
        spine_i = col_index(h, "Series") if eclipse else col_index(h, "Spine number (of film)", "Spine")
        box_i = col_index(h, "Name of")
        for r in t["rows"]:
            c = r["cells"]
            if len(c) <= max(ti, yi or 0):
                continue
            title = c[ti]["text"]
            if not title:
                continue
            spine = c[spine_i]["text"] if spine_i is not None else ""
            spine = re.sub(r"[^\d]", "", spine.split()[0]) if spine and spine[0].isdigit() else ""
            box = c[box_i]["text"] if box_i is not None else ""
            if eclipse:
                rank = f"Eclipse {spine} ({box})"
            elif spine:
                rank = f"spine {spine}" + (" (LaserDisc only)" if "FBE9F7" in r["attrs"].upper() else "")
            else:
                rank = f"box set: {box}"
            out.append(entry("criterion_eclipse" if eclipse else "criterion", rank, title,
                             first_year(c[yi]["text"]) if yi is not None else None,
                             c[di]["text"] if di is not None else ""))
    return out


def festival(lst, page, award, refresh):
    out = []
    for t in wikitables(wiki(page, refresh)):
        h = t["headers"]
        yi = col_index(h, "Year")
        ti = col_index(h, "English title", "Title", "Film")
        oi = col_index(h, "Original title")
        di = col_index(h, "Director", "Recipient")
        if yi is None or ti is None or di is None:
            continue
        for r in t["rows"]:
            c = r["cells"]
            if len(c) <= max(yi, ti, di) or c[ti] is c[yi] or c[ti] is c[di]:
                continue  # e.g. a "festival cancelled" / "no award" row spanning the table
            title = c[ti]["text"]
            year = first_year(c[yi]["text"])
            if not title or not year:
                continue
            orig = c[oi]["text"] if oi is not None and c[oi] is not c[ti] else ""
            out.append(entry(lst, f"{award} {year}", title, year, c[di]["text"], alts=[orig]))
    return out


def oscar_best_picture(refresh):
    out = []
    for t in wikitables(wiki("Academy Award for Best Picture", refresh)):
        h = t["headers"]
        yi, fi = col_index(h, "Year of film release"), col_index(h, "Film")
        if yi is None or fi is None:
            continue
        for r in t["rows"]:
            c = r["cells"]
            if len(c) <= fi or "FAEB86" not in r["attrs"].upper():
                continue
            label = c[yi]["text"].split("(")[0].strip()
            out.append(entry("oscar_best_picture", f"Best Picture {label}", c[fi]["text"], first_year(label)))
    return out


def oscar_international(refresh):
    text = wiki("Academy Award for Best International Feature Film", refresh)
    sec = text[text.index("== Winners =="):]
    sec = sec[:sec.index("{{div col end}}")]
    out = []
    for ln in sec.split("\n"):
        if not ln.startswith("*"):
            continue
        year_part, _, film = clean(ln[1:]).partition(":")
        film, year = film.strip(), first_year(year_part)
        if year and film and film != "N/A":
            out.append(entry("oscar_international_feature", f"Intl Feature {year}", film, year))
    return out


def national_film_registry(refresh):
    out = []
    for t in wikitables(wiki("National Film Registry", refresh)):
        h = t["headers"]
        ti, yi, ii = col_index(h, "Film title"), col_index(h, "Year of release"), col_index(h, "Year of induction")
        if ti is None or yi is None:
            continue
        for r in t["rows"]:
            c = r["cells"]
            if len(c) <= max(ti, yi, ii):
                continue
            out.append(entry("national_film_registry", f"inducted {c[ii]['text']}", c[ti]["text"],
                             first_year(c[yi]["text"])))
    return out


SOURCES = {
    "sight_and_sound_critics_2022": lambda rf: bfi("sight_and_sound_critics_2022",
        "https://www.bfi.org.uk/sight-and-sound/greatest-films-all-time", "bfi_critics_2022.html", rf),
    "sight_and_sound_directors_2022": lambda rf: bfi("sight_and_sound_directors_2022",
        "https://www.bfi.org.uk/sight-and-sound/directors-100-greatest-films-all-time", "bfi_directors_2022.html", rf),
    "tspdt_1000": lambda rf: tspdt("tspdt_1000",
        "https://theyshootpictures.com/gf1000_all1000films_table.php", "tspdt_1000.html", rf),
    "tspdt_21st_century_1000": lambda rf: tspdt("tspdt_21st_century_1000",
        "https://theyshootpictures.com/21stcentury_allfilms_table.php", "tspdt_21st_century.html", rf),
    "criterion": criterion,  # also yields criterion_eclipse rows
    "palme_dor": lambda rf: festival("palme_dor", "Palme d'Or", "Palme d'Or", rf),
    "golden_lion": lambda rf: festival("golden_lion", "Golden Lion", "Golden Lion", rf),
    "golden_bear": lambda rf: festival("golden_bear", "Golden Bear", "Golden Bear", rf),
    "oscar_best_picture": oscar_best_picture,
    "oscar_international_feature": oscar_international,
    "national_film_registry": national_film_registry,
}


# ---------------------------------------------------------------- matching

ART_RE = re.compile(r"^(the|a|an|le|la|les|l|il|lo|gli|der|die|das|el|los|las|un|une|os|het|een) ")


def norm(title):
    s = unicodedata.normalize("NFKD", title)
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    s = s.replace("&", " and ").replace("½", " 1/2")
    s = re.sub(r"[^\w]+", " ", s).replace("_", " ")
    s = re.sub(r"our(s?)\b", r"or\1", s)  # British/American spelling: colour, neighbour, honour
    s = re.sub(r"\bblvd\b", "boulevard", s)
    s = re.sub(r"\s+", " ", s).strip()
    # drop spaces last, so "Blowup" = "Blow-Up" and "Harlan County, USA" = "Harlan County U.S.A."
    return ART_RE.sub("", s).replace(" ", "")


class Imdb:
    def __init__(self):
        self.index, self.info = {}, {}
        with gzip.open(os.path.join(IMDB_DIR, "title.basics.tsv.gz"), "rt", encoding="utf-8") as f:
            next(f)
            for line in f:
                p = line.rstrip("\n").split("\t")
                if p[1] not in TYPE_RANK or p[5] == "\\N" or p[4] == "1":  # p[4] = isAdult
                    continue
                self.info[p[0]] = (p[1], int(p[5]), p[2])
                for t in {norm(p[2]), norm(p[3])}:
                    self.index.setdefault(t, []).append(p[0])
        self.votes = {}
        with gzip.open(os.path.join(IMDB_DIR, "title.ratings.tsv.gz"), "rt", encoding="utf-8") as f:
            next(f)
            for line in f:
                tc, _, n = line.rstrip("\n").split("\t")
                if tc in self.info:
                    self.votes[tc] = int(n)
        # Alternative titles (English-language markets, worldwide, original).
        # Used only when the primary/original title fails.
        self.akas = {}
        akas_path = os.path.join(IMDB_DIR, "title.akas.tsv.gz")
        if not os.path.exists(akas_path):
            print("downloading title.akas.tsv.gz (~500 MB)")
            urllib.request.urlretrieve("https://datasets.imdbws.com/title.akas.tsv.gz", akas_path)
        with gzip.open(akas_path, "rt", encoding="utf-8") as f:
            next(f)
            for line in f:
                p = line.rstrip("\n").split("\t")  # titleId ordering title region language types attributes isOriginalTitle
                if p[0] in self.votes and (p[3] in AKA_REGIONS or p[7] == "1"):
                    self.akas.setdefault(norm(p[2]), set()).add(p[0])

    def lookup(self, title, year, window, index):
        best = None
        for tc in index.get(norm(title), ()):
            ttype, y, _ = self.info[tc]
            if year is not None and abs(y - year) > window:
                continue
            key = (TYPE_RANK[ttype], -self.votes.get(tc, 0))
            if best is None or key < best[0]:
                best = (key, tc, y)
        return best

    def match(self, e):
        """Return (tconst, method) or ("", "unmatched")."""
        titles = [e["title"]] + e["alts"]
        extra = []
        for t in titles:
            for sep in (": ", " - ", " – ", " (", " / ", " aka "):
                if sep in t:
                    extra.append(t.split(sep)[0])
        for window in (1, 2):
            for group, kind in ((titles, "title"), (extra, "short_title")):
                for index, src in ((self.index, ""), (self.akas, "aka_")):
                    for i, t in enumerate(group):
                        hit = self.lookup(t, e["year"], window, index)
                        if hit:
                            k = "alt_title" if kind == "title" and i > 0 else kind
                            yr = "year" if hit[2] == e["year"] else f"year+-{window}"
                            return hit[1], f"imdb_{src}{k}_{yr}"
        return "", "unmatched"


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lists", help="comma-separated subset of: " + ",".join(SOURCES))
    ap.add_argument("--refresh", action="store_true", help="refetch pages even if cached")
    args = ap.parse_args()
    names = args.lists.split(",") if args.lists else list(SOURCES)

    entries = []
    for name in names:
        try:
            got = SOURCES[name](args.refresh)
        except Exception as ex:  # report and carry on with the other lists
            print(f"FAILED {name}: {ex!r}", file=sys.stderr)
            continue
        print(f"fetched {name}: {len(got)} entries")
        entries.extend(got)

    print("loading IMDb datasets ...")
    imdb = Imdb()
    for e in entries:
        e["tconst"], e["match_method"] = imdb.match(e)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    fields = ["list", "rank_or_award", "title", "year", "director", "tconst", "match_method"]
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(entries)
    print(f"wrote {len(entries)} rows to {OUT_PATH}\n")

    lists = list(dict.fromkeys(e["list"] for e in entries))
    print(f"{'list':34} {'entries':>7} {'matched':>7} {'rate':>6} {'distinct':>8}")
    for l in lists:
        es = [e for e in entries if e["list"] == l]
        m = [e for e in es if e["tconst"]]
        print(f"{l:34} {len(es):7} {len(m):7} {len(m) / len(es):6.1%} {len({e['tconst'] for e in m}):8}")

    canon = {e["tconst"] for e in entries if e["tconst"]}
    print(f"\ndistinct matched films on any list: {len(canon)}")
    if os.path.exists(RATINGS_PATH):
        lb = {}
        with open(RATINGS_PATH, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                lb[r["tconst"]] = int(r["letterboxd_votes"]) if r["letterboxd_votes"] else None
        big = {t for t, v in lb.items() if v is not None and v >= 10000}
        added = canon - big
        print(f"of which NOT already in film_ratings.csv with letterboxd_votes >= 10000: {len(added)}")
        print(f"  in film_ratings.csv with < 10k Letterboxd votes: {sum(1 for t in added if lb.get(t) is not None)}")
        print(f"  in film_ratings.csv with no Letterboxd figure:   {sum(1 for t in added if t in lb and lb[t] is None)}")
        print(f"  not in film_ratings.csv (not a candidate):       {sum(1 for t in added if t not in lb)}")

    print("\nunmatched:")
    for e in entries:
        if not e["tconst"]:
            print(f"  [{e['list']}] {e['rank_or_award']}: {e['title']} ({e['year']})")


if __name__ == "__main__":
    main()
