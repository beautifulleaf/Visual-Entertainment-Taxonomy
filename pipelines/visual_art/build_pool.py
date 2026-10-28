"""Build the candidate artist pool for one region x period (visual-art-plan.md §2.1).

1. Fetch every person in any of the region's media (occupation groups in
   regions.MEDIA: painting, sculpture, architecture, printmaking, design and
   decorative arts, ...) with >= min_sitelinks from Wikidata, worldwide, by birth
   decade (cached under data/raw/wikidata/pool/, so other regions reuse it).
   People with no birth date are fetched by death date. Each person's full
   occupation list then sets their primary medium and all their media.
2. Fetch, for those people plus the region's reference artists: citizenship and
   birth/death countries, genres (P136), movements (P135), ULAN and WikiArt IDs,
   every region's authority IDs (regions.py) and their Wikipedia
   article titles (for pageviews.py).
3. Keep people whose active span overlaps the region's years and whose country
   falls in the region (see regions.py).

Output: data/interim/visual_art/pool_<region>.csv
        data/interim/visual_art/sitelinks.tsv   (qid, wiki, title; all regions)
        data/interim/visual_art/labels.tsv      (labels of genre/movement/country QIDs)

Usage: python3 pipelines/visual_art/build_pool.py --region europe_1400-1900
"""
import argparse
import collections
import csv
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reference import load_reference  # noqa: E402
from regions import (ASIA, EURASIA, EUROPE, GLOBAL_IDS, HOME_CONTINENT_ORDER, MEDIA, REGIONS, active_span,  # noqa: E402
                     media_occupations, period_of)
from wikidata import QLEVER, sparql, year_of  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw", "wikidata", "pool")
OUT_DIR = os.path.join(ROOT, "data", "interim", "visual_art")

ART_OCCUPATIONS = ({o for occs in MEDIA.values() for o in occs} | {"Q483501"}  # + "artist"
                   | {o for cfg in REGIONS.values() for occs in cfg.get("extra_occupations", {}).values() for o in occs})
# Union over all regions, so one cached fetch serves every pass.
AUTHORITY_IDS = sorted({p for cfg in REGIONS.values() for p in cfg["authority_ids"]})
FACT_PROPS = ["P27", "P136", "P135"] + list(GLOBAL_IDS) + AUTHORITY_IDS
CHUNK = 250


def cached(name, fn):
    path = os.path.join(RAW, name)
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    data = fn()
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    return data


def people_born(occs, start, end, min_sl):
    values = " ".join("wd:" + o for o in occs)
    return sparql(f"""SELECT ?p ?s (MIN(?b) AS ?birth) (MIN(?d) AS ?death) (SAMPLE(?lab) AS ?label) WHERE {{
      VALUES ?occ {{ {values} }}
      ?p wdt:P106 ?occ ; wdt:P569 ?b ; wikibase:sitelinks ?s .
      FILTER(?s >= {min_sl})
      FILTER(?b >= "{start:04d}-01-01T00:00:00Z"^^xsd:dateTime && ?b < "{end:04d}-01-01T00:00:00Z"^^xsd:dateTime)
      OPTIONAL {{ ?p wdt:P570 ?d }}
      OPTIONAL {{ ?p rdfs:label ?lab FILTER(LANG(?lab) = "en") }}
    }} GROUP BY ?p ?s""")


def people_died_no_birth(occs, start, end, min_sl):
    values = " ".join("wd:" + o for o in occs)
    return sparql(f"""SELECT ?p ?s (MIN(?d) AS ?death) (MIN(?f) AS ?floruit) (SAMPLE(?lab) AS ?label) WHERE {{
      VALUES ?occ {{ {values} }}
      ?p wdt:P106 ?occ ; wikibase:sitelinks ?s .
      FILTER(?s >= {min_sl})
      FILTER NOT EXISTS {{ ?p wdt:P569 [] }}
      {{ ?p wdt:P570 ?d }} UNION {{ ?p wdt:P1317 ?f }}
      FILTER(COALESCE(?d, ?f) >= "{start:04d}-01-01T00:00:00Z"^^xsd:dateTime && COALESCE(?d, ?f) < "{end:04d}-01-01T00:00:00Z"^^xsd:dateTime)
      OPTIONAL {{ ?p rdfs:label ?lab FILTER(LANG(?lab) = "en") }}
    }} GROUP BY ?p ?s""")


def xsd_year(y):
    """xsd:dateTime literal for 1 January of year y (BCE years as -0450)."""
    return f'"{"-" if y < 0 else ""}{abs(y):04d}-01-01T00:00:00Z"^^xsd:dateTime'


# Who counts as a person in the pre-1400 passes: humans, conventional-name artists
# ("notname": Berlin Painter, Amasis Painter; most are also typed human) and humans
# whose existence is disputed. Excludes vase "Groups"/"Classes", characters, categories.
PERSON_CLASSES = "wd:Q5 wd:Q1747829 wd:Q21070568"  # human, notname, human whose existence is disputed


def people_born_any(occs, start, end, min_sl):
    """people_born for any year, BCE included."""
    values = " ".join("wd:" + o for o in occs)
    return sparql(f"""SELECT ?p ?s (MIN(?b) AS ?birth) (MIN(?d) AS ?death) (SAMPLE(?lab) AS ?label) WHERE {{
      VALUES ?occ {{ {values} }}
      ?p wdt:P106 ?occ ; wdt:P569 ?b ; wikibase:sitelinks ?s .
      FILTER(?s >= {min_sl})
      FILTER EXISTS {{ VALUES ?cls {{ {PERSON_CLASSES} }} ?p wdt:P31 ?cls }}
      FILTER(?b >= {xsd_year(start)} && ?b < {xsd_year(end)})
      OPTIONAL {{ ?p wdt:P570 ?d }}
      OPTIONAL {{ ?p rdfs:label ?lab FILTER(LANG(?lab) = "en") }}
    }} GROUP BY ?p ?s""", endpoint=QLEVER)


def people_dated_no_birth(occs, start, end, min_sl):
    """People with no birth date, by death, floruit (P1317) or work period (P2031/P2032).

    Pre-1400 makers are often dated only by floruit or work period (Greek vase
    painters, medieval masters)."""
    values = " ".join("wd:" + o for o in occs)
    return sparql(f"""SELECT ?p ?s (MIN(?d) AS ?death) (MIN(?f) AS ?floruit) (MIN(?ws) AS ?work_start)
        (MAX(?we) AS ?work_end) (SAMPLE(?lab) AS ?label) WHERE {{
      VALUES ?occ {{ {values} }}
      ?p wdt:P106 ?occ ; wikibase:sitelinks ?s .
      FILTER(?s >= {min_sl})
      FILTER NOT EXISTS {{ ?p wdt:P569 [] }}
      FILTER EXISTS {{ VALUES ?cls {{ {PERSON_CLASSES} }} ?p wdt:P31 ?cls }}
      {{ ?p wdt:P570 ?d }} UNION {{ ?p wdt:P1317 ?f }} UNION {{ ?p wdt:P2031 ?ws }} UNION {{ ?p wdt:P2032 ?we }}
      BIND(COALESCE(?d, ?f, ?ws, ?we) AS ?t)
      FILTER(?t >= {xsd_year(start)} && ?t < {xsd_year(end)})
      OPTIONAL {{ ?p rdfs:label ?lab FILTER(LANG(?lab) = "en") }}
    }} GROUP BY ?p ?s""", endpoint=QLEVER)


def merge_person(people, r):
    """One record per QID across buckets (a person's death, floruit and work period
    can fall in different buckets): earliest dates, latest work-period end."""
    old = people.setdefault(r["p"], dict(r))

    def yr(v):  # unknown-value dates (blank nodes) sort last
        y = year_of(v)
        return y if y is not None else 10 ** 6

    for k, v in r.items():
        if not v or k in ("p", "s", "label"):
            continue
        if not old.get(k):
            old[k] = v
        elif k != "work_end":
            old[k] = min(old[k], v, key=yr)
        else:
            old[k] = max(old[k], v, key=lambda x: yr(x) if yr(x) < 10 ** 6 else -10 ** 6)


def fetch_people_grouped(cfg, workers):
    """Pre-1400 passes: one query per time bucket for all the region's occupations
    (results are small), with BCE dates and floruit/work-period dating. These broad
    scans time out on WDQS, so they run on the QLever mirror."""
    lo, hi = cfg["active"]
    sl, step = cfg["min_sitelinks"], cfg["fetch_bucket"]
    occs = sorted({o for v in media_occupations(cfg).values() for o in v})
    key = "occ" + hashlib.sha1(" ".join(occs).encode()).hexdigest()[:8]
    jobs = []
    for a in range((lo - 70) // step * step, hi - 20 + 1, step):
        jobs.append((f"{key}_born_{a}_w{step}_s{sl}.json", people_born_any, a))
    for a in range(lo // step * step, hi + step, step):
        jobs.append((f"{key}_dated_{a}_w{step}_s{sl}.json", people_dated_no_birth, a))

    def run(job):
        name, fn, a = job
        return cached(name, lambda: fn(occs, a, a + step, sl))

    people = {}
    with ThreadPoolExecutor(workers) as pool:
        for i, rows in enumerate(pool.map(run, jobs), 1):
            for r in rows:
                merge_person(people, r)
            if i % 10 == 0 or i == len(jobs):
                print(f"  {i}/{len(jobs)} period queries, {len(people)} people")
    return people


def fetch_people(cfg, workers=3):
    """Worldwide people in any of the region's media, keyed by QID (queries run in parallel)."""
    if cfg.get("fetch_bucket"):
        return fetch_people_grouped(cfg, workers)
    lo, hi = cfg["active"]
    sl = cfg["min_sitelinks"]
    jobs = []
    for medium in cfg["media"]:
        occs = MEDIA[medium]
        # Single-occupation groups keep the per-occupation cache names (painting reuses its fetch).
        key = occs[0] if len(occs) == 1 else re.sub(r"\W+", "_", medium)
        # Born up to 70 years before the period starts, up to 20 before it ends.
        for dec in range((lo - 70) // 10 * 10, hi - 20 + 1, 10):
            jobs.append((f"{key}_born_{dec}_s{sl}.json", people_born, occs, dec, dec + 10))
        for start in range(lo // 50 * 50, hi + 50, 50):
            jobs.append((f"{key}_nobirth_{start}_s{sl}.json", people_died_no_birth, occs, start, start + 50))

    def run(job):
        name, fn, occs, a, b = job
        return name, cached(name, lambda: fn(occs, a, b, sl))

    people = {}
    with ThreadPoolExecutor(workers) as pool:
        for i, (name, rows) in enumerate(pool.map(run, jobs), 1):
            for r in rows:
                people.setdefault(r["p"], r)
            if i % 50 == 0:
                print(f"  {i}/{len(jobs)} occupation-period queries, {len(people)} people")
    return people


def fetch_occupations(qids):
    """{qid: [occupation QIDs]} for assigning media, cached per QID."""
    path = os.path.join(RAW, "occupations.json")
    occ = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    todo = [q for q in qids if q not in occ]
    for i in range(0, len(todo), CHUNK):
        chunk = todo[i:i + CHUNK]
        for q in chunk:
            occ[q] = []
        values = " ".join("wd:" + q for q in chunk)
        for r in sparql(f"SELECT ?p ?o WHERE {{ VALUES ?p {{ {values} }} ?p wdt:P106 ?o }}"):
            occ[r["p"]].append(r["o"])
        if (i // CHUNK) % 20 == 19 or i + CHUNK >= len(todo):
            json.dump(occ, open(path, "w", encoding="utf-8"))
            print(f"  occupations: {min(i + CHUNK, len(todo))}/{len(todo)}")
    return occ


def people_by_qid(qids):
    """Base records for specific QIDs (reference artists outside the occupation query)."""
    out = {}
    for i in range(0, len(qids), CHUNK):
        values = " ".join("wd:" + q for q in qids[i:i + CHUNK])
        for r in sparql(f"""SELECT ?p ?s (MIN(?b) AS ?birth) (MIN(?d) AS ?death) (MIN(?f) AS ?floruit) (SAMPLE(?lab) AS ?label) WHERE {{
              VALUES ?p {{ {values} }} ?p wikibase:sitelinks ?s .
              OPTIONAL {{ ?p wdt:P569 ?b }} OPTIONAL {{ ?p wdt:P570 ?d }} OPTIONAL {{ ?p wdt:P1317 ?f }}
              OPTIONAL {{ ?p rdfs:label ?lab FILTER(LANG(?lab) = "en") }}
            }} GROUP BY ?p ?s"""):
            out[r["p"]] = r
    return out


def fetch_facts(qids):
    """Statement values, birth/death countries and Wikipedia titles, cached per QID."""
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
    for i in range(0, len(todo), CHUNK):
        chunk = todo[i:i + CHUNK]
        values = " ".join("wd:" + q for q in chunk)
        rec = {q: {"claims": {}, "titles": {}} for q in chunk}
        for r in sparql(f"""SELECT ?p ?prop ?v WHERE {{
              VALUES ?p {{ {values} }}
              {{ VALUES ?prop {{ {props} }} ?p ?prop ?v . }}
              UNION {{ ?p wdt:P19/wdt:P17 ?v . BIND("birth_country" AS ?prop) }}
              UNION {{ ?p wdt:P20/wdt:P17 ?v . BIND("death_country" AS ?prop) }}
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
        facts.update(rec)
        json.dump(facts, open(path, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"  facts: {min(i + CHUNK, len(todo))}/{len(todo)}")
    return facts


def fetch_extra_places(qids):
    """Fallback place evidence for people with no citizenship or birth/death country
    (pre-1400 passes): work location (P937) and its country, culture (P2596) and
    languages (P1412). Cached per QID."""
    path = os.path.join(RAW, "extra_places.json")
    known = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    todo = [q for q in qids if q not in known]
    for i in range(0, len(todo), CHUNK):
        chunk = todo[i:i + CHUNK]
        for q in chunk:
            known[q] = {"work_country": [], "culture": []}
        values = " ".join("wd:" + q for q in chunk)
        for r in sparql(f"""SELECT ?p ?k ?v WHERE {{ VALUES ?p {{ {values} }}
              {{ ?p wdt:P937 ?v . BIND("work_country" AS ?k) }} UNION {{ ?p wdt:P937/wdt:P17 ?v . BIND("work_country" AS ?k) }}
              UNION {{ ?p wdt:P2596 ?v . BIND("culture" AS ?k) }} UNION {{ ?p wdt:P1412 ?v . BIND("culture" AS ?k) }} }}"""):
            if re.fullmatch(r"Q\d+", r["v"]) and r["v"] not in known[r["p"]][r["k"]]:
                known[r["p"]][r["k"]].append(r["v"])
        json.dump(known, open(path, "w", encoding="utf-8"))
        print(f"  extra places: {min(i + CHUNK, len(todo))}/{len(todo)}")
    return known


# Tried in order for countries still without a continent: the country's own
# continent, then that of its country (subnational/historical places), its
# successor state, and its capital's country. Separate simple queries, because
# one property-path union over all four times out on the public endpoint.
CONTINENT_PATHS = ["wdt:P30", "wdt:P17/wdt:P30", "wdt:P1366/wdt:P30", "wdt:P36/wdt:P17/wdt:P30"]


def fetch_country_continents(countries):
    """Continent(s) per country QID."""
    path = os.path.join(RAW, "country_continents.json")
    known = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    for prop_path in CONTINENT_PATHS:
        todo = [c for c in countries if not known.get(c)]
        for i in range(0, len(todo), 100):
            values = " ".join("wd:" + q for q in todo[i:i + 100])
            for r in sparql(f"SELECT ?c ?cont WHERE {{ VALUES ?c {{ {values} }} ?c {prop_path} ?cont . }}"):
                known.setdefault(r["c"], [])
                if r["cont"] not in known[r["c"]]:
                    known[r["c"]].append(r["cont"])
        json.dump(known, open(path, "w", encoding="utf-8"))
    for c in countries:
        known.setdefault(c, [])
    missing = sum(1 for c in countries if not known[c])
    print(f"  {len(countries)} countries, {missing} without a continent")
    return known


LABEL_LANG_RANK = {"en": 0, "mul": 1, "en-gb": 2, "en-us": 2, "fr": 3, "de": 3, "es": 3, "it": 3, "nl": 3,
                   "pt": 3, "sv": 3, "da": 3, "nb": 3, "pl": 3, "cs": 3, "id": 3, "tr": 3}


def fallback_labels(qids):
    """{qid: label} for items with no English label: 'mul' (the language-neutral label
    Wikidata moved many English labels to), then another Latin-script language, then
    any language. Cached in RAW/fallback_labels.json; '' when the item has no label."""
    path = os.path.join(RAW, "fallback_labels.json")
    cache = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    todo = [q for q in qids if q not in cache and re.fullmatch(r"Q\d+", q)]
    for i in range(0, len(todo), CHUNK):
        chunk = todo[i:i + CHUNK]
        values = " ".join("wd:" + q for q in chunk)
        best = {}
        try:
            for r in sparql(f"""SELECT ?x ?l (LANG(?l) AS ?lang) WHERE {{ VALUES ?x {{ {values} }} ?x rdfs:label ?l }}"""):
                rank = LABEL_LANG_RANK.get(r.get("lang", ""), 9)
                if r["x"] not in best or rank < best[r["x"]][0]:
                    best[r["x"]] = (rank, r["l"])
        except RuntimeError as e:
            print(f"  fallback labels: skipped a batch ({e})")
            continue
        cache.update({q: best.get(q, (9, ""))[1] for q in chunk})
        json.dump(cache, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    return {q: cache.get(q, "") for q in qids}


def fetch_labels(qids):
    path = os.path.join(OUT_DIR, "labels.tsv")
    labels = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            labels = dict(line.rstrip("\n").split("\t", 1) for line in f if "\t" in line)
    # Only real items (claims can hold "unknown value" blank nodes), and labels are
    # cosmetic: a failing label query must not abort the pool build.
    todo = [q for q in qids if q not in labels and re.fullmatch(r"Q\d+", q)]
    for i in range(0, len(todo), CHUNK):
        values = " ".join("wd:" + q for q in todo[i:i + CHUNK])
        try:
            for r in sparql(f"""SELECT ?x ?l WHERE {{ VALUES ?x {{ {values} }}
                  ?x rdfs:label ?l FILTER(LANG(?l) = "en") }}"""):
                labels[r["x"]] = r["l"]
        except RuntimeError as e:
            print(f"  labels: skipped a batch ({e})")
    for q, lab in fallback_labels([q for q in todo if q not in labels]).items():
        if lab:
            labels[q] = lab
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(f"{k}\t{v}\n" for k, v in sorted(labels.items()))
    return labels


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", required=True, choices=sorted(REGIONS))
    # Wikidata's query service allows 5 concurrent queries per IP; leave room if
    # other Wikidata jobs are running.
    ap.add_argument("--workers", type=int, default=3, choices=range(1, 6))
    args = ap.parse_args()
    cfg = REGIONS[args.region]
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    print("fetching people")
    people = fetch_people(cfg, args.workers)
    ref_qids = []
    if cfg.get("reference"):
        ref_qids = sorted({r["qid"] for r in load_reference(cfg) if r["qid"]})
        extra = [q for q in ref_qids if q not in people]
        print(f"  {len(extra)} reference artists not returned by the occupation query; fetching them directly")
        people.update(people_by_qid(extra))
    # Manual includes (seeds/visual-art/<era>_manual_includes.csv, rows for this region):
    # always pooled and always selected (depth_model.select), like reference artists.
    manual = set()
    if cfg.get("manual_includes"):
        mpath = os.path.join(ROOT, cfg["manual_includes"])
        if os.path.exists(mpath):
            with open(mpath, encoding="utf-8") as f:
                manual = {r["qid"] for r in csv.DictReader(f) if r["region"] == args.region and r["qid"]}
        extra = [q for q in sorted(manual) if q not in people]
        if extra:
            print(f"  {len(extra)} manual includes not returned by the occupation query; fetching them directly")
            people.update(people_by_qid(extra))
    print(f"{len(people)} people")

    facts = fetch_facts(sorted(people))
    occupations = fetch_occupations(sorted(people))
    # Skip "unknown value" claims, which come back as genid blank-node IRIs.
    extra = {}
    if cfg.get("place_any"):
        unplaced = [q for q in sorted(people) if not any(
            facts.get(q, {}).get("claims", {}).get(k) for k in ("P27", "birth_country", "death_country"))]
        extra = fetch_extra_places(unplaced)
    countries = sorted({c for f in facts.values() for k in ("P27", "birth_country", "death_country")
                        for c in f["claims"].get(k, []) if re.fullmatch(r"Q\d+", c)}
                       | {c for e in extra.values() for c in e["work_country"]})
    continents = fetch_country_continents(countries)
    region_continents, region_countries = set(cfg["continents"]), set(cfg["countries"])
    excluded = set(cfg.get("exclude_countries", []))

    def country_continents(c):
        conts = continents.get(c, [])
        # Some states record "Eurasia" instead of Europe and Asia (the Russian Empire:
        # North America via Alaska + Eurasia), which made North America its home
        # continent and dropped every Russian-Empire artist from Europe.
        if EURASIA in conts:
            conts = [x for x in conts if x != EURASIA] + [x for x in (EUROPE, ASIA) if x not in conts]
        if cfg.get("home_continent") and len(conts) > 1:
            # Imperial and transcontinental states list every continent they reached
            # (France: South America, Oceania; German Empire: Africa, Oceania), which
            # put French and German artists into Latin America, Oceania and Africa.
            # Use one home continent instead.
            conts = [next(h for h in HOME_CONTINENT_ORDER + conts if h in conts)]
        return set(conts)

    def hit(c):
        return c in region_countries or (c not in excluded and bool(region_continents & country_continents(c)))

    fallback_cultures = set(cfg.get("fallback_cultures", []))

    def in_region(claims, q=None):
        if cfg.get("place_any"):
            # Pre-1400: citizenship is a historical state (Tang dynasty, Delian League,
            # Cilicia) and birth/death places resolve to modern countries, so any of
            # them may place the artist; overlaps between regions are unioned later.
            cs = [c for k in ("P27", "birth_country", "death_country") for c in claims.get(k, [])]
            if cs:
                return any(hit(c) for c in cs)
            e = extra.get(q, {})
            if e.get("work_country"):  # then where they worked
                return any(hit(c) for c in e["work_country"])
            if e.get("culture"):       # then culture or language (Ancient Greek, Etruscan)
                return bool(fallback_cultures & set(e["culture"]))
            return None
        if cfg.get("place_by_birth_death"):
            # Secondary or honorary citizenships (Max Ernst: Cuba; Leni Riefenstahl:
            # Sudan) put famous Europeans at the top of other regions' rankings. Use
            # where the artist was born or died (both count: émigrés belong to both).
            # Requiring a matching citizenship as well keeps colonial-era Europeans
            # (Tolkien, born in South Africa; Thackeray, born in Calcutta) out of the
            # colonies' rankings, while émigrés (Gorky) still count for both regions.
            places = claims.get("birth_country", []) + claims.get("death_country", [])
            cits = [c for c in claims.get("P27", []) if re.fullmatch(r"Q\d+", c)]
            if places:
                return any(hit(c) for c in places) and (not cits or any(hit(c) for c in cits))
        for key in ("P27", "birth_country", "death_country"):
            cs = claims.get(key, [])
            if cs:  # first property that has any country decides
                return any(hit(c) for c in cs)
        return None  # no country information at all

    lo, hi = cfg["active"]
    ref_set = set(ref_qids)
    rows, n_unknown_place = [], 0
    for q, p in people.items():
        birth, death, floruit = year_of(p.get("birth")), year_of(p.get("death")), year_of(p.get("floruit"))
        span = active_span(birth, death, floruit, year_of(p.get("work_start")), year_of(p.get("work_end")))
        claims = facts.get(q, {}).get("claims", {})
        region_hit = in_region(claims, q)
        n_unknown_place += region_hit is None
        in_pool = bool(span and span[0] <= hi and span[1] >= lo and region_hit and int(p["s"]) >= cfg["min_sitelinks"])
        if not (in_pool or q in ref_set or q in manual):
            continue
        row = {
            "qid": q, "label": p.get("label", ""), "birth": birth, "death": death,
            "active_start": span[0] if span else None, "active_end": span[1] if span else None,
            "period": period_of(span) if span else None,
            "sitelinks": int(p["s"]), "wikipedias": len(facts.get(q, {}).get("titles", {})),
            "countries": "|".join(claims.get("P27") or claims.get("birth_country") or claims.get("death_country") or []),
            "genres": "|".join(sorted(set(claims.get("P136", [])))),
            "movements": "|".join(sorted(set(claims.get("P135", [])))),
            "in_pool_rule": int(in_pool), "is_reference": int(q in ref_set), "manual_include": int(q in manual),
        }
        # Primary medium = first matching group in MEDIA order; all matches kept for placement.
        media = [m for m, occs in media_occupations(cfg).items() if set(occs) & set(occupations.get(q, []))]
        row["medium"] = media[0] if media else "visual art (unspecified)"
        row["media"] = "|".join(media)
        # Share of the person's occupations that are art occupations; depth_model
        # down-weights people for whom art is incidental (writers, politicians...).
        occ = set(occupations.get(q, []))
        row["art_occ_share"] = round(len(occ & ART_OCCUPATIONS) / len(occ), 3) if occ else ""
        for pid, name in GLOBAL_IDS.items():
            row[f"{name}_id"] = (claims.get(pid) or [""])[0]
        # Which authority IDs the artist has; depth_model.py counts the region's own.
        row["authority_ids"] = "|".join(pid for pid in AUTHORITY_IDS if claims.get(pid))
        rows.append(row)

    # Items whose English label moved to 'mul' (Georgia O'Keeffe) come back unlabelled.
    unlabelled = [r["qid"] for r in rows if not r["label"]]
    found = fallback_labels(unlabelled)
    for r in rows:
        if not r["label"]:
            r["label"] = found.get(r["qid"], "")
    if unlabelled:
        print(f"  {len(unlabelled)} artists had no English label; {sum(1 for r in rows if r['qid'] in set(unlabelled) and r['label'])} "
              "labelled from 'mul' or another language")

    out = os.path.join(OUT_DIR, f"pool_{args.region}.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: -r["sitelinks"]))
    with open(os.path.join(OUT_DIR, "sitelinks.tsv"), "w", encoding="utf-8") as f:
        for q in sorted(facts):
            for wiki, title in sorted(facts[q]["titles"].items()):
                f.write(f"{q}\t{wiki}\t{title}\n")
    fetch_labels(sorted({v for r in rows for k in ("genres", "movements", "countries") for v in r[k].split("|") if v}))

    by_medium = collections.Counter(r["medium"] for r in rows if r["in_pool_rule"])
    print("by primary medium:", ", ".join(f"{m} {n}" for m, n in by_medium.most_common()))
    n_pool = sum(r["in_pool_rule"] for r in rows)
    n_ref_out = sum(1 for r in rows if r["is_reference"] and not r["in_pool_rule"])
    print(f"pool {args.region}: {n_pool} artists by the pool rule; {len(ref_set)} reference artists, "
          f"{n_ref_out} of them outside the pool rule (kept as positives)")
    print(f"people with no country information: {n_unknown_place}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
