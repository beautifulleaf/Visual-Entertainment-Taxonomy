"""Build the candidate artist pool for one region x period (visual-art-plan.md §2.1).

1. Fetch every person with the region's occupations and >= min_sitelinks from
   Wikidata, worldwide, by birth decade (cached under data/raw/wikidata/pool/,
   so other regions reuse it). People with no birth date are fetched by death date.
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
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reference import load_reference  # noqa: E402
from regions import GLOBAL_IDS, REGIONS, active_span, period_of  # noqa: E402
from wikidata import sparql, year_of  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw", "wikidata", "pool")
OUT_DIR = os.path.join(ROOT, "data", "interim", "visual_art")

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


def people_born(occ, start, end, min_sl):
    return sparql(f"""SELECT ?p ?s (MIN(?b) AS ?birth) (MIN(?d) AS ?death) (SAMPLE(?lab) AS ?label) WHERE {{
      ?p wdt:P106 wd:{occ} ; wdt:P569 ?b ; wikibase:sitelinks ?s .
      FILTER(?s >= {min_sl})
      FILTER(?b >= "{start:04d}-01-01T00:00:00Z"^^xsd:dateTime && ?b < "{end:04d}-01-01T00:00:00Z"^^xsd:dateTime)
      OPTIONAL {{ ?p wdt:P570 ?d }}
      OPTIONAL {{ ?p rdfs:label ?lab FILTER(LANG(?lab) = "en") }}
    }} GROUP BY ?p ?s""")


def people_died_no_birth(occ, start, end, min_sl):
    return sparql(f"""SELECT ?p ?s (MIN(?d) AS ?death) (MIN(?f) AS ?floruit) (SAMPLE(?lab) AS ?label) WHERE {{
      ?p wdt:P106 wd:{occ} ; wikibase:sitelinks ?s .
      FILTER(?s >= {min_sl})
      FILTER NOT EXISTS {{ ?p wdt:P569 [] }}
      {{ ?p wdt:P570 ?d }} UNION {{ ?p wdt:P1317 ?f }}
      FILTER(COALESCE(?d, ?f) >= "{start:04d}-01-01T00:00:00Z"^^xsd:dateTime && COALESCE(?d, ?f) < "{end:04d}-01-01T00:00:00Z"^^xsd:dateTime)
      OPTIONAL {{ ?p rdfs:label ?lab FILTER(LANG(?lab) = "en") }}
    }} GROUP BY ?p ?s""")


def fetch_people(cfg):
    """Worldwide people with the region's occupations, keyed by QID."""
    lo, hi = cfg["active"]
    people = {}
    for occ in cfg["occupations"]:
        # Born up to 70 years before the period starts, up to 20 before it ends.
        for dec in range((lo - 70) // 10 * 10, hi - 20 + 1, 10):
            rows = cached(f"{occ}_born_{dec}_s{cfg['min_sitelinks']}.json",
                          lambda: people_born(occ, dec, dec + 10, cfg["min_sitelinks"]))
            print(f"  {occ} born {dec}s: {len(rows)}")
            for r in rows:
                people.setdefault(r["p"], r)
        for start in range(lo // 50 * 50, hi + 50, 50):
            rows = cached(f"{occ}_nobirth_{start}_s{cfg['min_sitelinks']}.json",
                          lambda: people_died_no_birth(occ, start, start + 50, cfg["min_sitelinks"]))
            print(f"  {occ} no birth date, died/floruit {start}-{start + 49}: {len(rows)}")
            for r in rows:
                people.setdefault(r["p"], r)
    return people


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


def fetch_labels(qids):
    path = os.path.join(OUT_DIR, "labels.tsv")
    labels = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            labels = dict(line.rstrip("\n").split("\t", 1) for line in f if "\t" in line)
    todo = [q for q in qids if q not in labels]
    for i in range(0, len(todo), CHUNK):
        values = " ".join("wd:" + q for q in todo[i:i + CHUNK])
        for r in sparql(f"""SELECT ?x ?l WHERE {{ VALUES ?x {{ {values} }}
              ?x rdfs:label ?l FILTER(LANG(?l) = "en") }}"""):
            labels[r["x"]] = r["l"]
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(f"{k}\t{v}\n" for k, v in sorted(labels.items()))
    return labels


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", required=True, choices=sorted(REGIONS))
    args = ap.parse_args()
    cfg = REGIONS[args.region]
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    print("fetching people")
    people = fetch_people(cfg)
    ref_qids = []
    if cfg.get("reference"):
        ref_qids = sorted({r["qid"] for r in load_reference(cfg) if r["qid"]})
        extra = [q for q in ref_qids if q not in people]
        print(f"  {len(extra)} reference artists not returned by the occupation query; fetching them directly")
        people.update(people_by_qid(extra))
    print(f"{len(people)} people")

    facts = fetch_facts(sorted(people))
    countries = sorted({c for f in facts.values() for k in ("P27", "birth_country", "death_country")
                        for c in f["claims"].get(k, [])})
    continents = fetch_country_continents(countries)
    region_continents, region_countries = set(cfg["continents"]), set(cfg["countries"])

    def in_region(claims):
        for key in ("P27", "birth_country", "death_country"):
            cs = claims.get(key, [])
            if cs:  # first property that has any country decides
                return any(c in region_countries or region_continents & set(continents.get(c, [])) for c in cs)
        return None  # no country information at all

    lo, hi = cfg["active"]
    ref_set = set(ref_qids)
    rows, n_unknown_place = [], 0
    for q, p in people.items():
        birth, death, floruit = year_of(p.get("birth")), year_of(p.get("death")), year_of(p.get("floruit"))
        span = active_span(birth, death, floruit)
        claims = facts.get(q, {}).get("claims", {})
        region_hit = in_region(claims)
        n_unknown_place += region_hit is None
        in_pool = bool(span and span[0] <= hi and span[1] >= lo and region_hit and int(p["s"]) >= cfg["min_sitelinks"])
        if not (in_pool or q in ref_set):
            continue
        row = {
            "qid": q, "label": p.get("label", ""), "birth": birth, "death": death,
            "active_start": span[0] if span else None, "active_end": span[1] if span else None,
            "period": period_of(span) if span else None,
            "sitelinks": int(p["s"]), "wikipedias": len(facts.get(q, {}).get("titles", {})),
            "countries": "|".join(claims.get("P27") or claims.get("birth_country") or claims.get("death_country") or []),
            "genres": "|".join(sorted(set(claims.get("P136", [])))),
            "movements": "|".join(sorted(set(claims.get("P135", [])))),
            "in_pool_rule": int(in_pool), "is_reference": int(q in ref_set),
        }
        for pid, name in GLOBAL_IDS.items():
            row[f"{name}_id"] = (claims.get(pid) or [""])[0]
        # Which authority IDs the artist has; depth_model.py counts the region's own.
        row["authority_ids"] = "|".join(pid for pid in AUTHORITY_IDS if claims.get(pid))
        rows.append(row)

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

    n_pool = sum(r["in_pool_rule"] for r in rows)
    n_ref_out = sum(1 for r in rows if r["is_reference"] and not r["in_pool_rule"])
    print(f"pool {args.region}: {n_pool} artists by the pool rule; {len(ref_set)} reference artists, "
          f"{n_ref_out} of them outside the pool rule (kept as positives)")
    print(f"people with no country information: {n_unknown_place}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
