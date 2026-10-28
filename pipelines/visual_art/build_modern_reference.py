"""Build a candidate modern-art depth reference (active 1860-1960) from data.

visual-art-plan.md §2.4: the modern pass has no reference list, so it is scored
with the Europe 1400-1900 model. This script derives a WikiArt-style reference
("Movement: name, name, ...") without using any of the depth model's features
(sitelinks, pageviews, Met/AIC/Cleveland holdings, Met Timeline, ULAN, regional
authority IDs), so that refitting on it is not circular.

1. Skeleton = movements. Wikidata items of an art-movement-like type (art
   movement, painting movement, art style, art group, artist collective, school
   of painting, art colony, ...) with visual-artist members via P135 (movement)
   or P463 (member of), worldwide. A movement is kept when it has >= 3 members
   active 1860-1960 and is modern: inception (P571/P580) 1855-1960 if dated, and
   median member birth 1800-1922 (later medians belong to the contemporary pass).
   Umbrella terms (modern art, abstract art, avant-garde, ...) are dropped.
2. Curatorial signal per member, independent of the model's features:
     tate_works      Tate collection open data (CC0), joined on the Tate ID (P2741)
                     or name + birth year
     moma_works      MoMA collection open data (CC0), joined on Wikidata QID; used
                     only if data/raw/curatorial/moma/Artists.json + Artworks.json exist
     wd_collections  distinct collections (P195) holding works by the artist on
                     Wikidata, excluding the Met, AIC, Cleveland (model features)
                     and "private collection"
     regional_objects  objects in the regional sweeps (ColBase, Bunka Isan, NPM,
                     V&A, Rijksmuseum, Smithsonian units; never the Met/AIC/CMA columns)
   score = sum of log1p over the four. Members with no curatorial signal are
   ordered by their number of kept movement memberships (fallback).
3. Reference = per movement, the top 30% of members by score (min 3, max 60).
   Poorly covered non-Western movements (region outside Europe / North America,
   under half the members with any signal) keep every member up to a cap of 25,
   since they are curatorially defined groups. Artists are deduplicated across
   movements: each is listed under the movement where it ranks best.

Output: data/interim/modern_reference_candidate.txt   (seeds format)
        data/interim/modern_reference_candidate.csv   (one row per artist)
        data/interim/modern_reference_movements.csv   (every candidate movement)
Cache:  data/raw/wikidata/modern_reference/ (one SPARQL query at a time)

Usage: python3 pipelines/visual_art/build_modern_reference.py
"""
import argparse
import collections
import csv
import glob
import json
import math
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from regions import HOME_CONTINENT_ORDER, MEDIA, MODERN_REGIONS, active_span  # noqa: E402
import wikidata  # noqa: E402
from wikidata import UA, year_of  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw", "wikidata", "modern_reference")
POOL_RAW = os.path.join(ROOT, "data", "raw", "wikidata", "pool")
CURATORIAL = os.path.join(ROOT, "data", "raw", "curatorial")
REGIONAL = os.path.join(ROOT, "data", "interim", "regional")
OUT = os.path.join(ROOT, "data", "interim")

ACTIVE = (1860, 1960)
BIRTH_RANGE = (1790, 1936)        # anyone who can be active inside ACTIVE
INCEPTION_RANGE = (1855, 1960)
MEDIAN_BIRTH_RANGE = (1815, 1925)   # for movements with no inception date
MAX_BIRTH_WESTERN = 1925            # members of European / North American movements
MAX_BIRTH_NONWESTERN = 1940         # the modern pool's own limit (active by 1960)
MAX_ASSOCIATION = 40              # P463-only groups larger than this are professional associations
MIN_MEMBERS = 3
SHARE, MIN_K, MAX_K = 0.30, 3, 60
SMALL_CAP = 25
CHUNK = 200

MOVEMENT_TYPES = {
    "Q968159": "art movement", "Q3326867": "painting movement", "Q1792644": "art style",
    "Q17399019": "style of painting", "Q4502119": "art group", "Q1400264": "artist collective",
    "Q1887220": "school of painting", "Q2736610": "artistic school", "Q1558054": "art colony",
    "Q65266274": "art style of an area", "Q2198855": "cultural movement", "Q1292119": "style",
}
GROUP_TYPES = ["Q4502119", "Q1400264", "Q1887220", "Q2736610", "Q1558054"]
# Umbrella terms, not movements in the WikiArt sense (members number in the thousands
# and span every style). Filled in from the data on first run.
UMBRELLA = {
    "Q38166": "modern art", "Q186030": "contemporary art", "Q128115": "abstract art",
    "Q1414236": "modernism", "Q215592": "avant-garde", "Q1640824": "figurative art",
    "Q2111604": "post-war art", "Q878985": "modernism", "Q102932": "avant-garde",
    "Q47783": "postmodernism",
}
# P31 values that mark an organisation rather than a movement (unions, salons, academies).
NON_MOVEMENT = {
    "Q178790": "trade union", "Q1151067": "professional association", "Q955824": "learned society",
    "Q4671277": "academic institution", "Q3918": "university", "Q1664720": "institute",
    "Q48204": "voluntary association", "Q163740": "nonprofit organization", "Q2085381": "publisher",
    "Q3152824": "cultural institution", "Q1785733": "environmental organization", "Q988108": "club",
    "Q15911314": "association", "Q667276": "art exhibition", "Q464980": "exhibition",
}
WESTERN = ("europe", "north_america")
# Collections that are model features (Met, AIC, Cleveland) or not curatorial.
EXCLUDED_COLLECTIONS = {"Q160236", "Q239303", "Q657415", "Q768717"}
ART_OCCUPATIONS = {o for m, occs in MEDIA.items() for o in occs}
ARCHITECTURE = set(MEDIA["architecture"])


ENDPOINTS = {"qlever": "https://qlever.dev/api/wikidata", "wdqs": "https://query.wikidata.org/sparql"}
ENDPOINT = ["qlever"]
CACHED_LINKS_ONLY = [False]
PREFIXES = """PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""


def sparql(query, retries=8):
    """One query at a time, to WDQS or (default, during the WDQS outage) QLever's Wikidata mirror."""
    if ENDPOINT[0] == "wdqs":
        return wikidata.sparql(query, retries)
    body = urllib.parse.urlencode({"query": PREFIXES + query}).encode()
    req = urllib.request.Request(ENDPOINTS["qlever"], data=body, headers={
        "User-Agent": UA, "Accept": "application/sparql-results+json",
        "Content-Type": "application/x-www-form-urlencoded"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.loads(r.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as e:
            wait = int(e.headers.get("Retry-After") or 0) or min(120, 5 * 2 ** attempt)
            print(f"    QLever HTTP {e.code}: {e.read()[:150]!r}, retrying in {wait}s")
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError, json.JSONDecodeError) as e:
            print(f"    QLever {type(e).__name__}, retrying")
            time.sleep(min(120, 5 * 2 ** attempt))
    else:
        raise RuntimeError("SPARQL query failed repeatedly")
    time.sleep(1)
    out = []
    for b in data["results"]["bindings"]:
        row = {}
        for k, v in b.items():
            val = v["value"]
            if v["type"] == "uri" and val.startswith("http://www.wikidata.org/entity/"):
                val = val.rsplit("/", 1)[1]
            row[k] = val
        out.append(row)
    return out


def cached(name, fn):
    path = os.path.join(RAW, name)
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    data = fn()
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    return data


def chunked_cache(name, keys, query_fn):
    """{key: value} filled chunk by chunk, saved after every chunk (resumable)."""
    path = os.path.join(RAW, name)
    data = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    todo = [k for k in keys if k not in data]
    for i in range(0, len(todo), CHUNK):
        data.update(query_fn(todo[i:i + CHUNK]))
        json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"  {name}: {min(i + CHUNK, len(todo))}/{len(todo)}")
    return data


def date_filter(var, lo, hi):
    return (f'FILTER(?{var} >= "{lo:04d}-01-01T00:00:00Z"^^xsd:dateTime && '
            f'?{var} < "{hi:04d}-01-01T00:00:00Z"^^xsd:dateTime)')


# ---------------------------------------------------------------- Wikidata

def fetch_memberships():
    """(artist, movement, property) for visual artists born in BIRTH_RANGE."""
    occ = " ".join("wd:" + o for o in sorted(ART_OCCUPATIONS))
    types = " ".join("wd:" + t for t in MOVEMENT_TYPES)
    groups = " ".join("wd:" + t for t in GROUP_TYPES)
    rows = []
    rows += [dict(r, prop="P135") for r in cached("members_P135.json", lambda: sparql(f"""
        SELECT DISTINCT ?a ?m WHERE {{
          VALUES ?t {{ {types} }} ?m wdt:P31/wdt:P279? ?t .
          ?a wdt:P135 ?m ; wdt:P569 ?b . {date_filter("b", *BIRTH_RANGE)}
          FILTER EXISTS {{ VALUES ?o {{ {occ} }} ?a wdt:P106 ?o }} }}"""))]
    # Groups only, and no date or occupation filter (that combination times out on
    # P463, a huge property); members are filtered locally once their facts are in.
    rows += [dict(r, prop="P463") for r in cached("members_P463.json", lambda: sparql(f"""
        SELECT DISTINCT ?a ?m WHERE {{
          VALUES ?t {{ {groups} }} ?m wdt:P31 ?t .
          ?a wdt:P463 ?m ; wdt:P31 wd:Q5 . }}"""))]
    return rows


def fetch_movement_meta(movements):
    def q(chunk):
        values = " ".join("wd:" + m for m in chunk)
        out = {m: {"label": "", "types": [], "start": [], "end": [], "countries": []} for m in chunk}
        for r in sparql(f"""SELECT ?m ?k ?v WHERE {{ VALUES ?m {{ {values} }}
              {{ ?m rdfs:label ?v FILTER(LANG(?v) = "en") BIND("label" AS ?k) }}
              UNION {{ ?m wdt:P31 ?v BIND("types" AS ?k) }}
              UNION {{ ?m wdt:P571|wdt:P580 ?v BIND("start" AS ?k) }}
              UNION {{ ?m wdt:P576|wdt:P582 ?v BIND("end" AS ?k) }}
              UNION {{ ?m wdt:P495|wdt:P17 ?v BIND("countries" AS ?k) }} }}"""):
            if r["k"] == "label":
                out[r["m"]]["label"] = r["v"]
            else:
                out[r["m"]][r["k"]].append(r["v"])
        return out
    return chunked_cache("movements_meta.json", movements, q)


def fetch_artists(qids):
    """Label, dates, countries, occupations, Tate and MoMA IDs per artist."""
    def q(chunk):
        values = " ".join("wd:" + a for a in chunk)
        out = {a: {"label": "", "birth": None, "death": None, "P27": [], "birth_country": [],
                   "death_country": [], "P106": [], "P2741": [], "P2174": []} for a in chunk}
        for r in sparql(f"""SELECT ?a ?k ?v WHERE {{ VALUES ?a {{ {values} }}
              {{ ?a rdfs:label ?v FILTER(LANG(?v) = "en") BIND("label" AS ?k) }}
              UNION {{ ?a wdt:P569 ?v BIND("birth" AS ?k) }}
              UNION {{ ?a wdt:P570 ?v BIND("death" AS ?k) }}
              UNION {{ VALUES ?p {{ wdt:P27 wdt:P106 wdt:P2741 wdt:P2174 }} ?a ?p ?v
                       BIND(STRAFTER(STR(?p), "direct/") AS ?k) }}
              UNION {{ ?a wdt:P19/wdt:P17 ?v BIND("birth_country" AS ?k) }}
              UNION {{ ?a wdt:P20/wdt:P17 ?v BIND("death_country" AS ?k) }} }}"""):
            rec, k, v = out[r["a"]], r["k"], r["v"]
            if k in ("label",):
                rec[k] = rec[k] or v
            elif k in ("birth", "death"):
                y = year_of(v)
                if y is not None and (rec[k] is None or y < rec[k]):
                    rec[k] = y
            elif v not in rec[k]:
                rec[k].append(v)
        return out
    return chunked_cache("artists.json", qids, q)


def fetch_fallback_labels(qids):
    """A label for artists with no English one: 'mul', else any Latin-script language, else any."""
    def q(chunk):
        values = " ".join("wd:" + a for a in chunk)
        best = {}
        for r in sparql(f"""SELECT ?a ?l (LANG(?l) AS ?lang) WHERE {{ VALUES ?a {{ {values} }} ?a rdfs:label ?l }}"""):
            lang = r.get("lang", "")
            rank = 0 if lang == "mul" else 1 if lang in ("fr", "de", "es", "pt", "it", "nl", "id", "tr", "sv", "pl") else 2
            if r["a"] not in best or rank < best[r["a"]][0]:
                best[r["a"]] = (rank, r["l"])
        return {a: best.get(a, (9, a))[1] for a in chunk}
    return chunked_cache("fallback_labels.json", qids, q)


def fetch_collections(qids):
    """Distinct collections (P195) and works on Wikidata per artist."""
    excl = ", ".join("wd:" + c for c in sorted(EXCLUDED_COLLECTIONS))

    def q(chunk):
        values = " ".join("wd:" + a for a in chunk)
        out = {a: [0, 0] for a in chunk}
        for r in sparql(f"""SELECT ?a (COUNT(DISTINCT ?c) AS ?nc) (COUNT(DISTINCT ?w) AS ?nw) WHERE {{
              VALUES ?a {{ {values} }} ?w wdt:P170 ?a ; wdt:P195 ?c .
              FILTER(?c NOT IN ({excl})) }} GROUP BY ?a"""):
            out[r["a"]] = [int(r["nc"]), int(r["nw"])]
        return out
    return chunked_cache("collections.json", qids, q)


def fetch_nonwestern_candidates():
    """Movement-type items with an English Wikipedia article: title, countries, inception."""
    types = " ".join("wd:" + t for t in MOVEMENT_TYPES)
    rows = cached("movement_items_enwiki.json", lambda: sparql(f"""
        SELECT ?m ?title (GROUP_CONCAT(DISTINCT STRAFTER(STR(?c), "entity/"); separator="|") AS ?countries)
               (MIN(?s) AS ?start) WHERE {{
          VALUES ?t {{ {types} }} ?m wdt:P31 ?t .
          ?art schema:about ?m ; schema:isPartOf <https://en.wikipedia.org/> ; schema:name ?title .
          OPTIONAL {{ ?m wdt:P495|wdt:P17 ?c }} OPTIONAL {{ ?m wdt:P571|wdt:P580 ?s }}
        }} GROUP BY ?m ?title"""))
    # Many movement items have no country (P495/P17): add the country of their
    # location / headquarters / place of formation, the English description, and
    # sitelinks (only to order the slow Wikipedia fetches, not as a signal).
    extra = chunked_cache("movement_items_extra.json", sorted({r["m"] for r in rows}), lambda chunk: {
        m: v for m, v in _extra(chunk).items()})
    for r in rows:
        e = extra.get(r["m"], {})
        r["loc_countries"], r["description"], r["sitelinks"] = e.get("c", []), e.get("d", ""), e.get("s", 0)
    return rows


def _extra(chunk):
    values = " ".join("wd:" + m for m in chunk)
    out = {m: {"c": [], "d": "", "s": 0} for m in chunk}
    for r in sparql(f"""SELECT ?m ?c ?d ?s WHERE {{ VALUES ?m {{ {values} }}
          OPTIONAL {{ ?m wdt:P276|wdt:P159|wdt:P740|wdt:P131 ?loc . ?loc wdt:P17 ?c }}
          OPTIONAL {{ ?m schema:description ?d FILTER(LANG(?d) = "en") }}
          OPTIONAL {{ ?m wikibase:sitelinks ?s }} }}"""):
        o = out[r["m"]]
        if r.get("c") and r["c"] not in o["c"]:
            o["c"].append(r["c"])
        o["d"] = r.get("d", o["d"])
        o["s"] = int(r.get("s") or 0)
    return out


# Last resort for movements with no country at all: place names and demonyms in the
# English label or description ("group of Nigerian artists", "Indian painting").
REGION_WORDS = {
    "south_asia": ["india", "bengal", "calcutta", "kolkata", "bombay", "mumbai", "madras", "pakistan", "lahore",
                   "sri lank", "ceylon", "bangladesh", "nepal", "rajput", "mughal"],
    "east_asia": ["china", "chinese", "shanghai", "beijing", "canton", "japan", "tokyo", "kyoto", "osaka", "korea",
                  "taiwan", "hong kong"],
    "southeast_asia": ["indonesia", "java", "bali", "philippin", "filipino", "thai", "siam", "vietnam", "burm",
                       "malay", "singapore", "cambodia", "khmer"],
    "mena_central_asia": ["arab", "iraq", "baghdad", "egypt", "cairo", "iran", "persia", "turk", "ottoman",
                          "istanbul", "syria", "leban", "morocc", "algeri", "tunisi", "israel", "palestin", "uzbek"],
    "subsaharan_africa": ["nigeria", "ghana", "senegal", "dakar", "congo", "kenya", "ethiopia", "uganda",
                          "south africa", "zimbabwe", "sudan", "cameroon", "mozambique", "angola", "tanzania",
                          "yoruba", "igbo", "zaria", "nsukka", "oshogbo", "osogbo"],
    "latin_america": ["mexic", "brazil", "argentin", "cuba", "chile", "peru", "colombia", "venezuela", "uruguay",
                      "latin america", "haiti", "puerto ric", "guatemala", "ecuador", "bolivia", "paraguay"],
    "oceania": ["australia", "new zealand", "aborigin", "maori", "pacific island"],
}


def region_from_text(text):
    t = text.lower().replace("african-american", "").replace("african american", "")
    hits = {reg for reg, words in REGION_WORDS.items() if any(w in t for w in words)}
    return hits.pop() if len(hits) == 1 else None


def wiki_get(params):
    """English Wikipedia API call, paced and honouring Retry-After."""
    url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({**params, "format": "json"})
    for attempt in range(40):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
                data = json.load(r)
            time.sleep(1)
            return data
        except urllib.error.HTTPError as e:
            wait = int(e.headers.get("Retry-After") or 0) or min(300, 10 * 2 ** min(attempt, 5))
            print(f"    Wikipedia HTTP {e.code}, retrying in {wait}s")
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError) as e:
            print(f"    Wikipedia {e}, retrying")
            time.sleep(min(300, 10 * 2 ** attempt))
    raise RuntimeError("Wikipedia API failed repeatedly")


def article_link_qids(titles):
    """{title: [QIDs of the articles it links to]} (cached; namespace 0 only)."""
    def q(chunk):
        out = {}
        for title in chunk:
            qids, cont = [], {}
            while True:
                data = wiki_get({"action": "query", "titles": title, "redirects": 1, "generator": "links",
                                 "gplnamespace": 0, "gpllimit": "max", "prop": "pageprops",
                                 "ppprop": "wikibase_item", **cont})
                for page in data.get("query", {}).get("pages", {}).values():
                    q_ = page.get("pageprops", {}).get("wikibase_item")
                    if q_:
                        qids.append(q_)
                if "continue" not in data:
                    break
                cont = {k: v for k, v in data["continue"].items()}
            out[title] = sorted(set(qids))
        return out
    path = os.path.join(RAW, "enwiki_links.json")
    data = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    todo = [t for t in titles if t not in data]
    if CACHED_LINKS_ONLY[0]:
        print(f"  --cached-links-only: {len(todo)} of {len(titles)} articles not fetched")
        todo = []
    for i, t in enumerate(todo, 1):   # saved per article: the API is often rate-limited
        data.update(q([t]))
        json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False)
        if i % 20 == 0 or i == len(todo):
            print(f"  enwiki_links: {i}/{len(todo)}")
    return data


def filter_artists(qids):
    """{qid: bool}: is a person with a visual-art occupation born inside BIRTH_RANGE."""
    occ = " ".join("wd:" + o for o in sorted(ART_OCCUPATIONS))

    def q(chunk):
        values = " ".join("wd:" + a for a in chunk)
        hits = {r["a"] for r in sparql(f"""SELECT DISTINCT ?a WHERE {{ VALUES ?a {{ {values} }}
              ?a wdt:P569 ?b . {date_filter("b", *BIRTH_RANGE)}
              FILTER EXISTS {{ VALUES ?o {{ {occ} }} ?a wdt:P106 ?o }} }}""")}
        return {a: a in hits for a in chunk}
    return chunked_cache("link_targets_artists.json", qids, q)


def fetch_continents(countries):
    """Continents per country: the pool cache first, then Wikidata (own cache file)."""
    known = {}
    for path in (os.path.join(POOL_RAW, "country_continents.json"), os.path.join(RAW, "country_continents.json")):
        if os.path.exists(path):
            known.update({k: v for k, v in json.load(open(path, encoding="utf-8")).items() if v})
    todo = [c for c in countries if c not in known]
    for prop_path in ["wdt:P30", "wdt:P17/wdt:P30", "wdt:P1366/wdt:P30", "wdt:P36/wdt:P17/wdt:P30"]:
        todo = [c for c in todo if not known.get(c)]
        for i in range(0, len(todo), 100):
            values = " ".join("wd:" + c for c in todo[i:i + 100])
            for r in sparql(f"SELECT ?c ?cont WHERE {{ VALUES ?c {{ {values} }} ?c {prop_path} ?cont }}"):
                known.setdefault(r["c"], [])
                if r["cont"] not in known[r["c"]]:
                    known[r["c"]].append(r["cont"])
    json.dump(known, open(os.path.join(RAW, "country_continents.json"), "w", encoding="utf-8"))
    return known


def home_continents(c, continents):
    """One home continent for multi-continent (imperial, transcontinental) countries, as build_pool.py."""
    conts = continents.get(c, [])
    if len(conts) > 1:
        conts = [next(h for h in HOME_CONTINENT_ORDER + conts if h in conts)]
    return set(conts)


def region_of_countries(cs, continents):
    for name, geo in MODERN_REGIONS.items():
        inc, exc, conts = set(geo.get("countries", [])), set(geo.get("exclude_countries", [])), set(geo.get("continents", []))
        if any(c in inc or (c not in exc and conts & home_continents(c, continents)) for c in cs):
            return name
    return "other"


def modern_regions(rec, continents):
    """Every region the artist belongs to, as build_pool.py places modern artists: by
    country of birth and of death (both count), else by citizenship. First = primary."""
    out = []
    for key in ("birth_country", "death_country"):
        cs = [c for c in rec.get(key, []) if re.fullmatch(r"Q\d+", c)]
        if cs:
            reg = region_of_countries(cs, continents)
            if reg not in out:
                out.append(reg)
    return out or [modern_region(rec, continents)]


def modern_region(rec, continents):
    """First MODERN_REGIONS entry matching by citizenship, then birth/death country."""
    for key in ("P27", "birth_country", "death_country"):
        cs = [c for c in rec.get(key, []) if re.fullmatch(r"Q\d+", c)]
        if not cs:
            continue
        for name, geo in MODERN_REGIONS.items():
            inc, exc, conts = set(geo.get("countries", [])), set(geo.get("exclude_countries", [])), set(geo.get("continents", []))
            if any(c in inc or (c not in exc and conts & home_continents(c, continents)) for c in cs):
                return name
        return "other"
    return "unknown"


# ---------------------------------------------------------------- curatorial sources

def norm(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z ]", " ", s).split()


def name_key(name):
    """Order-free key: 'Picasso, Pablo' and 'Pablo Picasso' match."""
    return " ".join(sorted(norm(name)))


def load_tate():
    """{tate_id: works}, {(name_key, birth): tate_id}."""
    base = os.path.join(CURATORIAL, "tate")
    if not os.path.exists(os.path.join(base, "artwork_data.csv")):
        print("  Tate data missing (data/raw/curatorial/tate/); tate_works = 0")
        return {}, {}
    works = collections.Counter()
    with open(os.path.join(base, "artwork_data.csv"), encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            works[r["artistId"]] += 1
    by_name = {}
    with open(os.path.join(base, "artist_data.csv"), encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            by_name[(name_key(r["name"]), r["yearOfBirth"])] = r["id"]
    return works, by_name


def load_moma():
    """{qid: works} from MoMA's Artists.json + Artworks.json, if present."""
    base = os.path.join(CURATORIAL, "moma")
    a_path, w_path = os.path.join(base, "Artists.json"), os.path.join(base, "Artworks.json")
    if not (os.path.exists(a_path) and os.path.getsize(a_path) and os.path.exists(w_path)):
        print("  MoMA data missing (data/raw/curatorial/moma/Artists.json, Artworks.json); moma_works = 0")
        return None
    qid_of = {}
    for a in json.load(open(a_path, encoding="utf-8")):
        if a.get("Wiki QID"):
            qid_of[a["ConstituentID"]] = a["Wiki QID"]
    works = collections.Counter()
    for w in json.load(open(w_path, encoding="utf-8")):
        for cid in w.get("ConstituentID") or []:
            if cid in qid_of:
                works[qid_of[cid]] += 1
    return works


def load_regional():
    """{(name_key, birth or ''): (objects, source)} from the regional sweeps.

    Only columns from collections that are not model features (ColBase, Bunka Isan,
    NPM, e-museum, V&A, Rijksmuseum, Smithsonian units)."""
    out = {}

    def add(key, n, src):
        if n > 0 and n > out.get(key, (0, ""))[0]:
            out[key] = (n, src)

    path = os.path.join(REGIONAL, "east_asia_artists.csv")
    if os.path.exists(path):
        cols = ["objects_colbase", "objects_bunka", "objects_npm", "objects_emuseum"]
        for r in csv.DictReader(open(path, encoding="utf-8")):
            n = sum(int(r.get(c) or 0) for c in cols)
            for nm in [r["artist_romanised"], r["artist_original"]] + r["other_names"].split(";"):
                if nm.strip():
                    add((name_key(nm), r["birth_year"]), n, "regional:east_asia")
    path = os.path.join(REGIONAL, "smithsonian_makers.csv")
    if os.path.exists(path):
        for r in csv.DictReader(open(path, encoding="utf-8")):
            if r.get("placeholder") == "1":
                continue
            add((name_key(r["name"]), r["birth"]), int(r["objects"] or 0), "regional:smithsonian")
    for path in glob.glob(os.path.join(REGIONAL, "*_makers.csv")):
        if path.endswith("smithsonian_makers.csv"):
            continue
        src = "regional:" + os.path.basename(path)[:-len("_makers.csv")]
        for r in csv.DictReader(open(path, encoding="utf-8")):
            if r.get("maker_kind", "person") != "person":
                continue
            n = sum(int(r.get(c) or 0) for c in r if c.startswith("objects_") and c not in ("objects_cma", "objects_aic"))
            add((name_key(r["maker"]), ""), n, src)
    return out


# ---------------------------------------------------------------- build

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--share", type=float, default=SHARE, help="share of each movement's members kept")
    ap.add_argument("--endpoint", choices=sorted(ENDPOINTS), default="qlever",
                    help="SPARQL endpoint (QLever's Wikidata mirror by default: WDQS was rate-limited)")
    ap.add_argument("--cached-links-only", action="store_true",
                    help="use only the Wikipedia article links already cached (the API is often rate-limited)")
    args = ap.parse_args()
    ENDPOINT[0] = args.endpoint
    CACHED_LINKS_ONLY[0] = args.cached_links_only
    os.makedirs(RAW, exist_ok=True)

    print("memberships")
    pairs = fetch_memberships()

    # Non-Western movements are thinly linked on Wikidata (the Bengal School, the
    # Progressive Artists' Group and the Nsukka group have no P135/P463 members), so
    # for movements based outside Europe and North America the artists linked from
    # the movement's English Wikipedia article count as members too, if they are
    # visual artists from the movement's own region.
    print("non-Western movements: Wikipedia article links")
    cands = fetch_nonwestern_candidates()
    ccountries = sorted({c for r in cands for c in r.get("countries", "").split("|") + r["loc_countries"]
                         if re.fullmatch(r"Q\d+", c)})
    ccont = fetch_continents(ccountries)
    nonwestern = {}
    for r in sorted(cands, key=lambda r: -r["sitelinks"]):
        reg = modern_region({"P27": r.get("countries", "").split("|"), "birth_country": r["loc_countries"]}, ccont)
        if reg == "unknown":
            reg = region_from_text(r["title"] + " " + r["description"]) or "unknown"
        start = year_of(r.get("start"))
        if reg not in WESTERN + ("unknown", "other") and (start is None or INCEPTION_RANGE[0] <= start <= INCEPTION_RANGE[1]):
            nonwestern[r["m"]] = (r["title"], reg)
    print(f"  {len(nonwestern)} non-Western movement items with an English article")
    links = article_link_qids(list(dict.fromkeys(t for t, _ in nonwestern.values())))  # most sitelinks first
    targets = sorted({q for t, _ in nonwestern.values() for q in links.get(t, [])})
    is_artist = filter_artists(targets)
    link_pairs = [{"a": q, "m": m, "prop": "enwiki", "region": reg}
                  for m, (t, reg) in nonwestern.items() for q in links.get(t, []) if is_artist.get(q)]
    print(f"  {len(link_pairs)} artist links before the region check")
    pairs = pairs + link_pairs
    movements = sorted({p["m"] for p in pairs})
    artists = sorted({p["a"] for p in pairs})
    print(f"  {len(pairs)} artist-movement pairs, {len(movements)} movements, {len(artists)} artists")
    meta = fetch_movement_meta(movements)
    info = fetch_artists(artists)
    fallback = fetch_fallback_labels(sorted(a for a, r in info.items() if not r["label"]))
    for a, lab in fallback.items():
        info[a]["label"] = lab
    countries = sorted({c for a in info.values() for k in ("P27", "birth_country", "death_country")
                        for c in a[k] if re.fullmatch(r"Q\d+", c)})
    continents = fetch_continents(countries)

    # Members: visual artists (not primarily architects) active inside ACTIVE.
    def eligible(a):
        rec = info.get(a)
        if not rec:
            return False
        occs = set(rec["P106"]) & ART_OCCUPATIONS
        if not occs or occs <= ARCHITECTURE:
            return False
        span = active_span(rec["birth"], rec["death"])
        return bool(span and span[0] <= ACTIVE[1] and span[1] >= ACTIVE[0])

    members = collections.defaultdict(set)
    via = collections.defaultdict(set)
    regions_of = {a: modern_regions(info[a], continents) for a in artists if a in info}
    region_of = {a: r[0] for a, r in regions_of.items()}
    for p in pairs:
        if eligible(p["a"]) and (p["prop"] != "enwiki" or p["region"] in regions_of.get(p["a"], [])):
            members[p["m"]].add(p["a"])
            via[p["m"]].add(p["prop"])

    # Movement filter.
    mrows = []
    for m in movements:
        md, mem = meta.get(m, {}), members.get(m, set())
        births = sorted(info[a]["birth"] for a in mem if info[a]["birth"])
        starts = [y for y in map(year_of, md.get("start", [])) if y is not None]
        start = min(starts) if starts else None
        median_birth = births[len(births) // 2] if births else None
        regions = collections.Counter(region_of[a] for a in mem)
        reasons = []
        if m in UMBRELLA:
            reasons.append("umbrella term")
        if len(mem) < MIN_MEMBERS:
            reasons.append(f"<{MIN_MEMBERS} members")
        if start is not None and not INCEPTION_RANGE[0] <= start <= INCEPTION_RANGE[1]:
            reasons.append(f"inception {start}")
        if start is None and median_birth is not None and not MEDIAN_BIRTH_RANGE[0] <= median_birth <= MEDIAN_BIRTH_RANGE[1]:
            reasons.append(f"undated, median birth {median_birth}")
        bad = [NON_MOVEMENT[t] for t in md.get("types", []) if t in NON_MOVEMENT]
        if bad:
            reasons.append("organisation: " + ", ".join(bad))
        if via.get(m) == {"P463"} and len(mem) > MAX_ASSOCIATION:
            reasons.append(f"association (P463 only, {len(mem)} members)")
        types = [MOVEMENT_TYPES[t] for t in md.get("types", []) if t in MOVEMENT_TYPES]
        mrows.append({
            "movement_qid": m, "movement": md.get("label") or m, "types": "|".join(types) or "subclass",
            "via": "|".join(sorted(via.get(m, []))), "inception": start, "median_birth": median_birth,
            "members": len(mem),
            "region": regions.most_common(1)[0][0] if regions else "",
            "regions": "; ".join(f"{r} {n}" for r, n in regions.most_common()),
            "kept": int(not reasons), "excluded_because": "; ".join(reasons),
        })
    kept = {r["movement_qid"]: r for r in mrows if r["kept"]}
    print(f"  {len(kept)} of {len(movements)} movements kept")
    # Western movements: members born after 1925 are left to the contemporary pass
    # (Rosenquist and Twombly are tagged abstract expressionism). Non-Western 1950s
    # modernisms (Zaria, Nsukka, Bombay PAG) keep members up to the pool's limit.
    for m, mr in kept.items():
        cap = MAX_BIRTH_WESTERN if mr["region"] in WESTERN else MAX_BIRTH_NONWESTERN
        members[m] = {a for a in members[m] if info[a]["birth"] is None or info[a]["birth"] <= cap}
        mr["members_in_reference_span"] = len(members[m])
    kept = {m: mr for m, mr in kept.items() if members[m]}

    # Curatorial signal for every member of a kept movement.
    pool = sorted({a for m in kept for a in members[m]})
    coll = fetch_collections(pool)
    tate_works, tate_by_name = load_tate()
    moma = load_moma()
    regional = load_regional()
    n_memberships = collections.Counter(a for m in kept for a in members[m])

    sig = {}
    for a in pool:
        rec = info[a]
        tid = next((t.rsplit("-", 1)[-1] for t in rec["P2741"]), None)
        if tid is None:
            tid = tate_by_name.get((name_key(rec["label"]), str(rec["birth"] or "")))
        tate = tate_works.get(tid, 0) if tid else 0
        mw = moma.get(a, 0) if moma else 0
        nc, nw = coll.get(a, [0, 0])
        key = name_key(rec["label"])
        reg, reg_src = regional.get((key, str(rec["birth"] or "")), regional.get((key, ""), (0, "")))
        sources = [s for s, v in (("tate", tate), ("moma", mw), ("wd_collections", nc), (reg_src, reg)) if v]
        score = math.log1p(tate) + math.log1p(mw) + math.log1p(nc) + math.log1p(reg)
        sig[a] = {"tate_works": tate, "moma_works": mw, "wd_collections": nc, "wd_collection_works": nw,
                  "regional_objects": reg, "score": score,
                  "source_signal": "+".join(sources) if sources else "membership-fallback"}

    # Per-movement selection.
    picks = collections.defaultdict(list)   # artist -> [(relative rank, movement, rank)]
    for m, mr in kept.items():
        ranked = sorted(members[m], key=lambda a: (-sig[a]["score"], -n_memberships[a], info[a]["label"]))
        covered = sum(1 for a in ranked if sig[a]["score"] > 0) / len(ranked)
        western = mr["region"] in ("europe", "north_america")
        if not western and covered < 0.5:
            k, rule = min(len(ranked), SMALL_CAP), "all members (non-Western, thin curatorial coverage)"
        else:
            k = max(MIN_K, min(MAX_K, round(args.share * len(ranked))))
            rule = f"top {args.share:.0%}"
        mr.update({"curatorial_coverage": round(covered, 2), "quota": min(k, len(ranked)), "rule": rule})
        for i, a in enumerate(ranked[:k], 1):
            picks[a].append((m, i))

    # Deduplicate: each artist goes to the movement where it ranks best (ties -> smaller movement).
    rows = []
    for a, ps in picks.items():
        # Listed once, WikiArt-style: under a movement of the artist's own region if
        # any, preferring P135 (declared movement) over group membership, then the
        # movement where the artist ranks highest relative to its quota (Matisse under
        # Fauvism, not Impressionism), then the larger movement; the rest go to also_in.
        def pref(p):
            mm = p[0]
            return (kept[mm]["region"] != region_of[a], "P135" not in via[mm] and "enwiki" not in via[mm],
                    (p[1] - 1) / kept[mm]["quota"], -kept[mm]["members"])
        ps = sorted(ps, key=pref)
        m, rank = ps[0]
        rec = info[a]
        rows.append({"movement": kept[m]["movement"], "movement_qid": m, "movement_region": kept[m]["region"],
                     "region": region_of[a], "name": rec["label"] or a, "qid": a, "birth": rec["birth"],
                     "death": rec["death"], "rank_in_movement": rank,
                     "also_in": "|".join(kept[x]["movement"] for x, _ in ps[1:]), **sig[a]})
    rows.sort(key=lambda r: (r["movement_region"], r["movement"], r["rank_in_movement"]))

    picked = collections.Counter(m for ps in picks.values() for m, _ in ps)
    for mr in mrows:
        mr["reference_artists"] = picked.get(mr["movement_qid"], 0)
        mr["listed_under"] = sum(1 for r in rows if r["movement_qid"] == mr["movement_qid"])
    with open(os.path.join(OUT, "modern_reference_movements.csv"), "w", newline="", encoding="utf-8") as f:
        cols = list(mrows[0]) + ["members_in_reference_span", "curatorial_coverage", "quota", "rule", "listed_under"]
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(cols)))
        w.writeheader()
        w.writerows(sorted(mrows, key=lambda r: (-r["kept"], r["region"], -r["members"])))
    cols = ["movement", "region", "name", "qid", "moma_works", "tate_works", "rank_in_movement", "source_signal",
            "movement_qid", "movement_region", "birth", "death", "wd_collections", "wd_collection_works",
            "regional_objects", "score", "also_in"]
    with open(os.path.join(OUT, "modern_reference_candidate.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({**r, "score": round(r["score"], 3)})
    with open(os.path.join(OUT, "modern_reference_candidate.txt"), "w", encoding="utf-8") as f:
        f.write("# Depth reference candidate: modern art, active 1860-1960 (visual-art-plan.md §2.4).\n"
                "# Generated by pipelines/visual_art/build_modern_reference.py from Wikidata movement\n"
                "# membership (P135/P463) ranked by Tate / MoMA / Wikidata-collection / regional-sweep\n"
                "# holdings; none of these are depth-model features. Format: \"Movement: name, name, ...\".\n")
        by_region = collections.defaultdict(lambda: collections.defaultdict(list))
        for r in rows:
            by_region[r["movement_region"]][r["movement"]].append(r["name"])
        for reg in list(MODERN_REGIONS) + ["other", "unknown"]:
            if reg not in by_region:
                continue
            f.write(f"\n## {reg.replace('_', ' ').title()}\n")
            for mv, names in sorted(by_region[reg].items()):
                f.write(f"{mv}: {', '.join(names)}\n")

    # Report.
    print(f"\nreference: {len(rows)} artists from {len({r['movement_qid'] for r in rows})} movements")
    print("\nby movement region:  movements kept / with reference artists / reference artists")
    for reg in list(MODERN_REGIONS) + ["other", "unknown"]:
        mk = [m for m, mr in kept.items() if mr["region"] == reg]
        print(f"  {reg:20} {len(mk):>4} {sum(1 for m in mk if kept[m]['reference_artists']):>4} "
              f"{sum(1 for r in rows if r['movement_region'] == reg):>6}")
    print("\nby artist region:", ", ".join(f"{k} {v}" for k, v in collections.Counter(r["region"] for r in rows).most_common()))
    print("by source signal:", ", ".join(f"{k} {v}" for k, v in collections.Counter(r["source_signal"] for r in rows).most_common(12)))
    print("wrote data/interim/modern_reference_candidate.{txt,csv} and modern_reference_movements.csv")


if __name__ == "__main__":
    main()
