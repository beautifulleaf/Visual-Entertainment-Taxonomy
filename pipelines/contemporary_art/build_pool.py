"""Build the candidate pool of contemporary artists (visual-art-plan.md §3, §4).

Contemporary = active after 1960 (decision 2); scale = maximise coverage (decision 1).
An entity is in the pool if either rule holds:

  occupation rule  a human with any visual-art occupation (regions.MEDIA plus the
                   contemporary groups in CONTEMPORARY_MEDIA below), born >= 1920
                   (or with no birth date but died >= 1965 / floruit >= 1960 / no
                   dates at all), with >= 3 sitelinks;
  market rule      any human with an Artnet (P3782), Artsy (P2042) or MoMA (P2174)
                   artist ID, born >= 1920 (or no birth date and no death before
                   1965), with >= 1 sitelink. These market/institution signals catch
                   artists Wikipedia under-covers.
Artist collectives (teamLab, Gelitin, ...) are added when founded >= 1950 (or
undated) and they meet either rule's sitelink threshold; their inception year is
used as `birth`.

Steps
1. Fetch candidates from Wikidata by medium group x birth decade and by market ID
   x birth decade, each query cached under data/raw/wikidata/contemporary/.
2. Fetch, per candidate (cached per QID): occupations, citizenship and birth
   country, authority / museum / market IDs, galleries (P1875), awards (P166),
   exhibition history (P608), Instagram (P2003), English aliases and Wikipedia
   article titles.
3. Countries -> continents (same approach as visual_art/build_pool.py, seeded from
   its cache data/raw/wikidata/pool/country_continents.json) -> region.
4. If data/interim/contemporary_lists.csv exists (canon_lists.py), match its names
   to the pool (normalised name, birth year when given) and add n_lists / lists.

Output: data/interim/contemporary_pool.csv       one row per artist
        data/interim/contemporary_sitelinks.tsv  qid, wiki, title (the format of
            data/interim/visual_art/sitelinks.tsv, so pageviews.py can read it)
        data/interim/contemporary_lists_matched.csv  each list row with its matched QID

Usage: python3 pipelines/contemporary_art/build_pool.py [--workers 3]
"""
import argparse
import collections
import csv
from concurrent.futures import ThreadPoolExecutor
import json
import os
import re
import sys
import threading
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "visual_art"))
from regions import (AFRICA, ASIA, AUSTRALIA, EUROPE, INSULAR_OCEANIA, MEDIA,  # noqa: E402
                     NORTH_AMERICA, OCEANIA, SOUTH_AMERICA)
from wikidata import sparql as _sparql, year_of  # noqa: E402
import time  # noqa: E402


def sparql(query, attempts=6):
    """wikidata.sparql plus retries on errors it does not catch (IncompleteRead,
    connection resets, truncated JSON, its own RuntimeError after repeated failures)."""
    for attempt in range(attempts):
        try:
            return _sparql(query)
        except Exception as e:  # noqa: BLE001 - network errors of many kinds
            if attempt == attempts - 1:
                raise
            wait = min(300, 15 * 2 ** attempt)
            print(f"    SPARQL failed ({type(e).__name__}: {str(e)[:80]}), retrying in {wait}s")
            time.sleep(wait)

RAW = os.path.join(ROOT, "data", "raw", "wikidata", "contemporary")
SHARED_CONTINENTS = os.path.join(ROOT, "data", "raw", "wikidata", "pool", "country_continents.json")
INTERIM = os.path.join(ROOT, "data", "interim")
OUT_PATH = os.path.join(INTERIM, "contemporary_pool.csv")
SITELINKS_PATH = os.path.join(INTERIM, "contemporary_sitelinks.tsv")
LISTS_PATH = os.path.join(INTERIM, "contemporary_lists.csv")
LISTS_MATCHED_PATH = os.path.join(INTERIM, "contemporary_lists_matched.csv")

MIN_BIRTH = 1920          # born >= 1920, so active after 1960
LAST_DECADE = 2010        # birth decades fetched: 1920s .. 2010s
OCC_MIN_SL = 3
ID_MIN_SL = 1
CHUNK = 250

# Contemporary occupations (QIDs checked by English label on 2026-10-28). Street art
# goes first so a graffiti artist who also paints is placed under street art; the
# other two groups come after the classical media.
STREET = {"street art and muralism": [
    "Q2914170",    # street artist
    "Q137575377",  # street art artist
    "Q15095148",   # graffiti artist
    "Q3374326",    # muralist
]}
CONTEMPORARY_MEDIA = {
    "installation, performance and conceptual": [
        "Q18074503",   # installation artist
        "Q10774753",   # performance artist
        "Q21550489",   # conceptual artist
        "Q33123562",   # land artist
        "Q69320328",   # environmental artist
        "Q111363164",  # body artist
        "Q111853588",  # object artist
        "Q69319917",   # assemblage artist
        "Q22343478",   # collagist
        "Q130213361",  # mixed-media artist
        "Q19850998",   # sound artist
        "Q21477194",   # contemporary artist
    ],
    "video, new media and digital": [
        "Q18216771",   # video artist
        "Q106227216",  # video installation artist
        "Q7016454",    # new media artist
        "Q6934789",    # multimedia artist
        "Q11079476",   # digital artist
        "Q106208189",  # computer artist
        "Q110453707",  # NFT artist
        "Q137537423",  # AI artist
        "Q108818918",  # light artist
        "Q21000481",   # kinetic artist
    ],
}
UNSPECIFIED = "visual art (unspecified)"
# Primary medium = first group in this order matching any occupation.
GROUPS = dict(STREET)
GROUPS.update({m: q for m, q in MEDIA.items() if m != UNSPECIFIED})
GROUPS.update(CONTEMPORARY_MEDIA)
GROUPS[UNSPECIFIED] = MEDIA[UNSPECIFIED]
COLLECTIVE_TYPES = ["Q1400264", "Q4502119"]  # artist collective, art group
# Groups typed "art group" that are not contemporary artist collectives: art movements
# and schools (Barbizon school, Fluxus), music groups (The Residents).
NOT_COLLECTIVE_TYPES = {"Q968159", "Q215380", "Q2088357", "Q5741069"}
VISUAL_ARTIST = "Q3391743"
ARTIST = "Q483501"

# Market / institution IDs used by the market rule, and all IDs reported as columns.
MARKET_IDS = {"P3782": "artnet", "P2042": "artsy", "P2174": "moma"}
ID_COLUMNS = {
    "P3782": "artnet", "P2042": "artsy", "P2174": "moma", "P245": "ulan", "P2741": "tate",
    "P6714": "whitney", "P6323": "pompidou", "P4936": "sfmoma", "P8434": "artprice",
    "P13700": "artfacts", "P8943": "artfacts_old", "P6578": "mutualart",
}
# Further museum artist IDs, counted into n_museum_ids (with MoMA, Tate, Whitney,
# Pompidou, SFMOMA above). There is no Guggenheim artist ID on Wikidata (only P4737,
# an artwork ID).
MUSEUM_IDS = {
    "P2174": "MoMA", "P2741": "Tate", "P6714": "Whitney", "P6323": "Centre Pompidou",
    "P4936": "SFMOMA", "P1795": "Smithsonian American Art Museum", "P2252": "National Gallery of Art",
    "P6295": "Art Institute of Chicago", "P10882": "Met", "P3603": "Minneapolis Institute of Art",
    "P5368": "National Gallery of Canada", "P8909": "National Gallery of Australia",
    "P2041": "National Gallery of Victoria", "P3544": "Te Papa", "P3372": "Auckland Art Gallery",
    "P6645": "Stedelijk", "P4439": "Museo Reina Sofia", "P3888": "Boijmans",
    "P4580": "Berlinische Galerie", "P4177": "Finnish National Gallery", "P7681": "Israel Museum",
    "P5567": "Tobunken (Japan)", "P4611": "LACMA", "P6525": "Fondation Maeght",
    "P5403": "CNAP", "P2399": "British Council", "P9468": "LIMA media art",
}
FACT_PROPS = sorted(set(ID_COLUMNS) | set(MUSEUM_IDS) | {"P27", "P106", "P1875", "P166", "P608", "P2003", "P31"})

CONTINENT_PATHS = ["wdt:P30", "wdt:P17/wdt:P30", "wdt:P1366/wdt:P30", "wdt:P36/wdt:P17/wdt:P30"]
CONTINENT_NAMES = {EUROPE: "Europe", NORTH_AMERICA: "North America", SOUTH_AMERICA: "South America",
                   ASIA: "Asia", AFRICA: "Africa", OCEANIA: "Oceania", INSULAR_OCEANIA: "Oceania",
                   AUSTRALIA: "Oceania"}
# Finer regions from ISO 3166-1 alpha-2 codes; countries not listed fall back to
# their continent (Europe, Sub-Saharan Africa, Latin America and Caribbean, Oceania).
REGION_BY_ISO = {}
for _region, _codes in {
    "North America": "US CA GL BM PM",
    "East Asia": "CN JP KR KP MN TW HK MO",
    "South Asia": "IN PK BD LK NP BT MV AF",
    "Southeast Asia": "ID TH VN PH MY SG MM KH LA BN TL",
    "Central Asia": "KZ UZ TM KG TJ",
    "Middle East and North Africa": "IR IQ SY LB JO IL PS SA AE QA KW BH OM YE TR EG LY TN DZ MA SD EH",
    "Europe": "RU GE AM AZ CY",
}.items():
    for _c in _codes.split():
        REGION_BY_ISO[_c] = _region
CONTINENT_REGION = {"Europe": "Europe", "Africa": "Sub-Saharan Africa", "South America": "Latin America and Caribbean",
                    "North America": "Latin America and Caribbean", "Oceania": "Oceania",
                    "Asia": "Asia (other)"}

_lock = threading.Lock()


def cached(name, fn):
    path = os.path.join(RAW, name)
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    data = fn()
    with open(path + ".part", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(path + ".part", path)
    return data


def dt(year):
    return f'"{year:04d}-01-01T00:00:00Z"^^xsd:dateTime'


def by_occupation_born(occs, start, end):
    values = " ".join("wd:" + o for o in occs)
    return sparql(f"""SELECT ?p ?s (MIN(?b) AS ?birth) (MIN(?d) AS ?death) (SAMPLE(?lab) AS ?label) WHERE {{
      VALUES ?occ {{ {values} }}
      ?p wdt:P106 ?occ ; wdt:P31 wd:Q5 ; wdt:P569 ?b ; wikibase:sitelinks ?s .
      FILTER(?s >= {OCC_MIN_SL})
      FILTER(?b >= {dt(start)} && ?b < {dt(end)})
      OPTIONAL {{ ?p wdt:P570 ?d }}
      OPTIONAL {{ ?p rdfs:label ?lab FILTER(LANG(?lab) = "en") }}
    }} GROUP BY ?p ?s""")


def by_occupation_nobirth(occs):
    values = " ".join("wd:" + o for o in occs)
    return sparql(f"""SELECT ?p ?s (MIN(?d) AS ?death) (MIN(?f) AS ?floruit) (SAMPLE(?lab) AS ?label) WHERE {{
      VALUES ?occ {{ {values} }}
      ?p wdt:P106 ?occ ; wdt:P31 wd:Q5 ; wikibase:sitelinks ?s .
      FILTER(?s >= {OCC_MIN_SL})
      FILTER NOT EXISTS {{ ?p wdt:P569 [] }}
      OPTIONAL {{ ?p wdt:P570 ?d }} OPTIONAL {{ ?p wdt:P1317 ?f }}
      FILTER((!BOUND(?d) && !BOUND(?f)) || COALESCE(?d, ?f) >= {dt(1960)})
      OPTIONAL {{ ?p rdfs:label ?lab FILTER(LANG(?lab) = "en") }}
    }} GROUP BY ?p ?s""")


def by_id_born(pid, start, end):
    return sparql(f"""SELECT ?p ?s (MIN(?b) AS ?birth) (MIN(?d) AS ?death) (SAMPLE(?lab) AS ?label) WHERE {{
      ?p wdt:{pid} [] ; wdt:P31 wd:Q5 ; wdt:P569 ?b ; wikibase:sitelinks ?s .
      FILTER(?s >= {ID_MIN_SL})
      FILTER(?b >= {dt(start)} && ?b < {dt(end)})
      OPTIONAL {{ ?p wdt:P570 ?d }}
      OPTIONAL {{ ?p rdfs:label ?lab FILTER(LANG(?lab) = "en") }}
    }} GROUP BY ?p ?s""")


def by_id_nobirth(pid):
    return sparql(f"""SELECT ?p ?s (MIN(?d) AS ?death) (SAMPLE(?lab) AS ?label) WHERE {{
      ?p wdt:{pid} [] ; wdt:P31 wd:Q5 ; wikibase:sitelinks ?s .
      FILTER(?s >= {ID_MIN_SL})
      FILTER NOT EXISTS {{ ?p wdt:P569 [] }}
      OPTIONAL {{ ?p wdt:P570 ?d }}
      FILTER(!BOUND(?d) || ?d >= {dt(1965)})
      OPTIONAL {{ ?p rdfs:label ?lab FILTER(LANG(?lab) = "en") }}
    }} GROUP BY ?p ?s""")


def collectives():
    types = " ".join("wd:" + t for t in COLLECTIVE_TYPES)
    ids = " ".join("wdt:" + p for p in MARKET_IDS)
    return sparql(f"""SELECT ?p ?s (MIN(?i) AS ?birth) (MIN(?e) AS ?death) (SAMPLE(?lab) AS ?label)
                             (MAX(?hasid) AS ?market) WHERE {{
      VALUES ?t {{ {types} }}
      ?p wdt:P31 ?t ; wikibase:sitelinks ?s .
      FILTER(?s >= {ID_MIN_SL})
      OPTIONAL {{ ?p wdt:P571 ?i }} OPTIONAL {{ ?p wdt:P576 ?e }}
      FILTER(!BOUND(?i) || ?i >= {dt(1950)})
      OPTIONAL {{ VALUES ?idp {{ {ids} }} ?p ?idp [] . BIND(1 AS ?hasid) }}
      OPTIONAL {{ ?p rdfs:label ?lab FILTER(LANG(?lab) = "en") }}
    }} GROUP BY ?p ?s""")


def fetch_candidates(workers):
    jobs = []
    for medium, occs in GROUPS.items():
        key = re.sub(r"\W+", "_", medium)
        for dec in range(MIN_BIRTH, LAST_DECADE + 1, 10):
            jobs.append(("occ", f"occ_{key}_born_{dec}_s{OCC_MIN_SL}.json",
                         lambda o=occs, d=dec: by_occupation_born(o, d, d + 10)))
        jobs.append(("occ", f"occ_{key}_nobirth_s{OCC_MIN_SL}.json", lambda o=occs: by_occupation_nobirth(o)))
    for pid in MARKET_IDS:
        for dec in range(MIN_BIRTH, LAST_DECADE + 1, 10):
            jobs.append(("id", f"id_{pid}_born_{dec}_s{ID_MIN_SL}.json", lambda p=pid, d=dec: by_id_born(p, d, d + 10)))
        jobs.append(("id", f"id_{pid}_nobirth_s{ID_MIN_SL}.json", lambda p=pid: by_id_nobirth(p)))
    jobs.append(("collective", "collectives.json", collectives))

    def run(job):
        kind, name, fn = job
        return kind, cached(name, fn)

    people = {}
    with ThreadPoolExecutor(workers) as pool:
        for i, (kind, rows) in enumerate(pool.map(run, jobs), 1):
            for r in rows:
                rec = people.setdefault(r["p"], dict(r, rules=set()))
                if kind == "occ":
                    rec["rules"].add("occupation")
                elif kind == "id":
                    rec["rules"].add("market")
                elif int(r["s"]) >= OCC_MIN_SL or r.get("market"):
                    rec["rules"].add("collective")
                    rec["is_collective"] = True
            if i % 25 == 0 or i == len(jobs):
                print(f"  {i}/{len(jobs)} candidate queries, {len(people)} candidates")
    return {q: p for q, p in people.items() if p["rules"]}


def art_occupations():
    """Occupations that make a market-rule person an artist: GROUPS, artist, and every
    subclass of visual artist. Artnet / MoMA / Artsy also hold IDs for sitters,
    writers, musicians and film makers (Donald Trump, Lionel Messi, Federico Fellini)."""
    rows = cached("visual_artist_subclasses.json", lambda: sparql(
        f"SELECT DISTINCT ?o WHERE {{ ?o wdt:P279* wd:{VISUAL_ARTIST} . }}"))
    return {r["o"] for r in rows} | {q for qs in GROUPS.values() for q in qs} | {ARTIST}


def collective_countries(qids):
    """{collective QID: [country QIDs]} from P17, P495, P159/P17 and P740/P17 (cached)."""
    values = " ".join("wd:" + q for q in sorted(qids))
    rows = cached(f"collective_countries_{len(qids)}.json", lambda: sparql(f"""SELECT ?p ?c WHERE {{
      VALUES ?p {{ {values} }}
      {{ ?p wdt:P17 ?c }} UNION {{ ?p wdt:P495 ?c }} UNION {{ ?p wdt:P159/wdt:P17 ?c }}
      UNION {{ ?p wdt:P740/wdt:P17 ?c }} }}"""))
    out = collections.defaultdict(list)
    for r in rows:
        if r["c"] not in out[r["p"]]:
            out[r["p"]].append(r["c"])
    return out


def screen(people, facts):
    """Drop market-rule non-artists and collectives that are movements, schools or bands."""
    art = art_occupations()
    dropped = collections.Counter()
    for q in list(people):
        p, cl = people[q], facts.get(q, {}).get("claims", {})
        if p.get("is_collective"):
            if set(cl.get("P31", [])) & NOT_COLLECTIVE_TYPES:
                dropped["collective: movement or music group"] += 1
                del people[q]
            elif not p.get("birth") and not p.get("market"):
                dropped["collective: undated, no market ID"] += 1
                del people[q]
        elif p["rules"] == {"market"} and cl.get("P106") and not set(cl["P106"]) & art:
            dropped["market rule: no art occupation"] += 1
            del people[q]
    print("  screened out: " + ", ".join(f"{k} {v}" for k, v in dropped.items()))
    return people


def fetch_facts(qids, workers):
    """Statements, birth country, English aliases and Wikipedia titles, cached per QID."""
    path = os.path.join(RAW, "facts.json")
    props_path = path + ".props"
    facts = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    if facts and os.path.exists(props_path):
        missing = set(FACT_PROPS) - set(json.load(open(props_path)))
        if missing:
            sys.exit(f"{path} was fetched without {sorted(missing)}; delete it and re-run")
    json.dump(FACT_PROPS, open(props_path, "w"))
    todo = [q for q in qids if q not in facts]
    props = " ".join("wdt:" + p for p in FACT_PROPS)

    def chunk_facts(chunk):
        values = " ".join("wd:" + q for q in chunk)
        rec = {q: {"claims": {}, "titles": {}, "aliases": []} for q in chunk}
        for r in sparql(f"""SELECT ?p ?prop ?v WHERE {{
              VALUES ?p {{ {values} }}
              {{ VALUES ?prop {{ {props} }} ?p ?prop ?v . }}
              UNION {{ ?p wdt:P19/wdt:P17 ?v . BIND("birth_country" AS ?prop) }}
            }}"""):
            prop = r["prop"].rsplit("/", 1)[-1]
            rec[r["p"]]["claims"].setdefault(prop, []).append(r["v"])
        for r in sparql(f"""SELECT ?p ?site ?title WHERE {{
              VALUES ?p {{ {values} }}
              ?a schema:about ?p ; schema:isPartOf ?site ; schema:name ?title .
              FILTER(STRENDS(STR(?site), ".wikipedia.org/"))
            }}"""):
            wiki = r["site"].split("//", 1)[1].split(".wikipedia.org", 1)[0]
            rec[r["p"]]["titles"][wiki] = r["title"]
        for r in sparql(f"""SELECT ?p ?a WHERE {{ VALUES ?p {{ {values} }}
              ?p skos:altLabel ?a FILTER(LANG(?a) = "en") }}"""):
            rec[r["p"]]["aliases"].append(r["a"])
        return rec

    chunks = [todo[i:i + CHUNK] for i in range(0, len(todo), CHUNK)]
    with ThreadPoolExecutor(workers) as pool:
        for i, rec in enumerate(pool.map(chunk_facts, chunks), 1):
            facts.update(rec)
            if i % 10 == 0 or i == len(chunks):
                with open(path + ".part", "w", encoding="utf-8") as f:
                    json.dump(facts, f, ensure_ascii=False)
                os.replace(path + ".part", path)
                print(f"  facts: {min(i * CHUNK, len(todo))}/{len(todo)}")
    return facts


def fetch_countries(countries):
    """{country QID: {"continents": [...], "iso": "XX"}}; continents seeded from visual_art's cache."""
    path = os.path.join(RAW, "countries.json")
    known = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    shared = json.load(open(SHARED_CONTINENTS, encoding="utf-8")) if os.path.exists(SHARED_CONTINENTS) else {}
    for c in countries:
        rec = known.setdefault(c, {"continents": [], "iso": None})
        if not rec["continents"] and shared.get(c):
            rec["continents"] = list(shared[c])
    for prop_path in CONTINENT_PATHS:
        todo = [c for c in countries if not known[c]["continents"] and not known[c].get(f"tried {prop_path}")]
        for i in range(0, len(todo), 100):
            values = " ".join("wd:" + q for q in todo[i:i + 100])
            for r in sparql(f"SELECT ?c ?cont WHERE {{ VALUES ?c {{ {values} }} ?c {prop_path} ?cont . }}"):
                if r["cont"] not in known[r["c"]]["continents"]:
                    known[r["c"]]["continents"].append(r["cont"])
        for c in todo:
            known[c][f"tried {prop_path}"] = True
    todo = [c for c in countries if "iso_tried" not in known[c]]
    for i in range(0, len(todo), 200):
        values = " ".join("wd:" + q for q in todo[i:i + 200])
        for r in sparql(f"SELECT ?c ?iso WHERE {{ VALUES ?c {{ {values} }} ?c wdt:P297 ?iso . }}"):
            known[r["c"]]["iso"] = r["iso"]
    for c in todo:
        known[c]["iso_tried"] = True
    json.dump(known, open(path, "w", encoding="utf-8"))
    print(f"  {len(countries)} countries, {sum(1 for c in countries if not known[c]['continents'])} without a continent")
    return known


def region_of(country, cinfo):
    rec = cinfo.get(country) or {}
    iso = rec.get("iso")
    if iso in REGION_BY_ISO:
        return REGION_BY_ISO[iso]
    conts = [CONTINENT_NAMES[c] for c in rec.get("continents", []) if c in CONTINENT_NAMES]
    if not conts:
        return None
    # Transcontinental countries without an ISO entry above: prefer Europe, then the first.
    cont = "Europe" if "Europe" in conts else conts[0]
    return CONTINENT_REGION[cont]


def continent_of(country, cinfo):
    conts = sorted({CONTINENT_NAMES[c] for c in (cinfo.get(country) or {}).get("continents", []) if c in CONTINENT_NAMES})
    return conts


def norm(name):
    name = unicodedata.normalize("NFKD", name)
    name = "".join(ch for ch in name if not unicodedata.combining(ch)).lower()
    name = name.replace("&", " and ").replace("ø", "o").replace("ł", "l").replace("ß", "ss")
    name = re.sub(r"\(.*?\)", " ", name)
    return " ".join(re.findall(r"[a-z0-9]+", name))


def join_lists(rows, facts):
    """Add n_lists / lists (and n_list_entries) from contemporary_lists.csv; returns a summary or None."""
    if not os.path.exists(LISTS_PATH):
        return None
    index = collections.defaultdict(set)
    by_q = {r["qid"]: r for r in rows}
    for r in rows:
        f = facts.get(r["qid"], {})
        names = {r["label"], *f.get("aliases", []), f.get("titles", {}).get("en", "")}
        for n in names:
            if n:
                k = norm(n)
                index[k].add(r["qid"])
                index[" ".join(sorted(k.split()))].add(r["qid"])

    def match(name, birth):
        k = norm(name)
        cands = index.get(k) or index.get(" ".join(sorted(k.split()))) or set()
        if birth:
            exact = {q for q in cands if by_q[q]["birth"] not in (None, "") and abs(int(by_q[q]["birth"]) - birth) <= 1}
            if exact:
                cands = exact
            elif any(by_q[q]["birth"] not in (None, "") for q in cands):
                cands = {q for q in cands if by_q[q]["birth"] in (None, "")}
        if not cands:
            return None
        return max(cands, key=lambda q: by_q[q]["sitelinks"])

    entries = collections.defaultdict(list)
    matched_rows, n_artist, n_matched = [], 0, 0
    with open(LISTS_PATH, encoding="utf-8") as f:
        for lr in csv.DictReader(f):
            by = re.search(r"\d{4}", lr.get("birth_year") or "")
            q = match(lr["name"], int(by.group()) if by else None)
            is_artist = lr.get("is_artist") != "0"
            if is_artist:
                n_artist += 1
                n_matched += q is not None
            if q:
                entries[q].append(lr)
            matched_rows.append(dict(lr, qid=q or ""))
    with open(LISTS_MATCHED_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(matched_rows[0]))
        w.writeheader()
        w.writerows(matched_rows)
    for r in rows:
        es = entries.get(r["qid"], [])
        lists = sorted({e["list"] for e in es})
        r["n_lists"] = len(lists)
        r["n_list_entries"] = len(es)
        r["lists"] = "|".join(lists)
    per_list = collections.Counter(e["list"] for es in entries.values() for e in es)
    return {"entries_artist": n_artist, "matched_artist": n_matched, "per_list": per_list,
            "lists_in_file": sorted({r["list"] for r in matched_rows})}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    # Wikidata allows 5 concurrent queries per IP; other jobs may be using the rest.
    ap.add_argument("--workers", type=int, default=3, choices=range(1, 4))
    args = ap.parse_args()
    os.makedirs(RAW, exist_ok=True)

    print("fetching candidates")
    people = fetch_candidates(args.workers)
    print(f"{len(people)} candidates")
    facts = fetch_facts(sorted(people), args.workers)
    people = screen(people, facts)
    coll_c = collective_countries([q for q, p in people.items() if p.get("is_collective")])
    for q, cs in coll_c.items():
        facts[q]["claims"].setdefault("P27", cs)

    countries = sorted({c for q in people for f in [facts[q]] for k in ("P27", "birth_country")
                        for c in f["claims"].get(k, []) if re.fullmatch(r"Q\d+", c)})
    cinfo = fetch_countries(countries)

    rows = []
    for q, p in people.items():
        f = facts.get(q, {"claims": {}, "titles": {}})
        cl = f["claims"]
        birth, death = year_of(p.get("birth")), year_of(p.get("death"))
        occs = set(cl.get("P106", []))
        media = [m for m, qs in GROUPS.items() if occs & set(qs)]
        cits = [c for c in dict.fromkeys(cl.get("P27", [])) if re.fullmatch(r"Q\d+", c)]
        bcs = [c for c in dict.fromkeys(cl.get("birth_country", [])) if re.fullmatch(r"Q\d+", c)]
        countries_ = cits or bcs
        regions = list(dict.fromkeys(r for r in (region_of(c, cinfo) for c in countries_) if r))
        # Primary region: the birth country's region if it is among the citizenship
        # regions (dual citizens are placed where they come from), else the first.
        primary = next((r for r in (region_of(c, cinfo) for c in bcs) if r in regions), regions[0] if regions else "")
        conts = sorted({c for x in countries_ for c in continent_of(x, cinfo)})
        primary_cont = next((c for x in bcs if region_of(x, cinfo) == primary for c in continent_of(x, cinfo)), "")
        if not primary_cont and countries_:
            primary_cont = next((c for x in countries_ if region_of(x, cinfo) == primary
                                 for c in continent_of(x, cinfo)), "")
        row = {
            "qid": q, "label": p.get("label", ""), "birth": birth if birth is not None else "",
            "death": death if death is not None else "",
            # No death date counts as living, except for people born before 1926
            # (over 100: almost always a missing death date) and collectives.
            "living": int(death is None and not p.get("is_collective") and (birth is None or birth >= 1926)),
            "is_collective": int(bool(p.get("is_collective"))),
            "pool_rules": "|".join(sorted(p["rules"])),
            "countries": "|".join(countries_),
            "country_codes": "|".join(filter(None, ((cinfo.get(c) or {}).get("iso") or "" for c in countries_))),
            "region": primary, "regions": "|".join(regions),
            "continent": primary_cont, "continents": "|".join(conts),
            "medium": media[0] if media else UNSPECIFIED, "media": "|".join(media),
            "sitelinks": int(p["s"]), "wikipedias": len(f["titles"]),
        }
        for pid, name in ID_COLUMNS.items():
            row[f"{name}_id"] = (cl.get(pid) or [""])[0]
        row["n_museum_ids"] = sum(1 for pid in MUSEUM_IDS if cl.get(pid))
        row["museum_ids"] = "|".join(MUSEUM_IDS[pid] for pid in MUSEUM_IDS if cl.get(pid))
        row["n_galleries"] = len(set(cl.get("P1875", [])))
        row["galleries"] = "|".join(sorted(set(cl.get("P1875", []))))
        row["n_awards"] = len(set(cl.get("P166", [])))
        row["awards"] = "|".join(sorted(set(cl.get("P166", []))))
        row["n_exhibitions"] = len(set(cl.get("P608", [])))
        row["instagram"] = int(bool(cl.get("P2003")))
        rows.append(row)

    summary = join_lists(rows, facts)
    if summary is None:
        print(f"{LISTS_PATH} not found; skipping the list join")
        for r in rows:
            r.update(n_lists="", n_list_entries="", lists="")

    rows.sort(key=lambda r: -r["sitelinks"])
    os.makedirs(INTERIM, exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(SITELINKS_PATH, "w", encoding="utf-8") as f:
        for q in sorted(r["qid"] for r in rows):
            for wiki, title in sorted(facts.get(q, {}).get("titles", {}).items()):
                f.write(f"{q}\t{wiki}\t{title}\n")

    n = len(rows)
    print(f"\npool: {n} (occupation rule {sum('occupation' in r['pool_rules'] for r in rows)}, "
          f"market rule {sum('market' in r['pool_rules'] for r in rows)}, "
          f"collectives {sum(r['is_collective'] for r in rows)})")
    print(f"living: {sum(r['living'] for r in rows)}")
    for col in ("region", "continent", "medium"):
        c = collections.Counter(r[col] or "(unknown)" for r in rows)
        print(f"by {col}: " + ", ".join(f"{k} {v}" for k, v in c.most_common()))
    for name in ("artnet", "artsy", "moma", "ulan", "tate", "whitney", "pompidou", "sfmoma", "artprice", "artfacts"):
        print(f"  with {name} id: {sum(1 for r in rows if r[name + '_id'])}")
    print(f"  with gallery (P1875): {sum(1 for r in rows if r['n_galleries'])}; "
          f"awards: {sum(1 for r in rows if r['n_awards'])}; P608: {sum(1 for r in rows if r['n_exhibitions'])}; "
          f"instagram: {sum(r['instagram'] for r in rows)}")
    if summary:
        print(f"lists: {summary['matched_artist']}/{summary['entries_artist']} artist entries matched; "
              f"lists in file: {', '.join(summary['lists_in_file'])}; "
              f"pool artists on >= 1 list: {sum(1 for r in rows if r['n_lists'])}")
    print(f"wrote {OUT_PATH}\nwrote {SITELINKS_PATH}")


if __name__ == "__main__":
    main()
