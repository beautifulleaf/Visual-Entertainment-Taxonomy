"""Architectural styles, their exemplar buildings and architects (visual-art-plan.md §2.1, §2A).

Decided 2026-10-28: architecture is organised by *style*, not by architect. The
node is the architectural style; buildings with that style (P149) are its
representative works, ranked by heritage designation and sitelinks; named
architects (P84) hang under the style via those buildings.

Steps (every SPARQL result is cached under data/raw/wikidata/architecture/,
keyed by a hash of the query, so a re-run resumes where it stopped):
1. Style set:
   - class:    instance of architectural style (Q32880) or of a subclass of it;
   - subclass: subclass (P279+) of such a style without being an instance of one;
   - p149:     any other value of architectural style (P149) whose instance-of
               type is style-like (art movement, art style, art style of an
               area, style, cultural movement, architecture of geographic
               location, historical period, ... see P149_TYPES).
2. Style facts: en / native (P1705) labels, sitelinks, P571/P580/P582, P495/P17/
   P30, P279/P361/P737, Getty AAT (P1014), P31.
3. Every building with P149 = a style: sitelinks, country (P17), inception,
   UNESCO (P757 or P1435 = World Heritage Site Q9259), part of (P361) a UNESCO
   site, any heritage designation (P1435). Aggregated per style: building
   counts, heritage counts, summed sitelinks, building inception percentiles,
   building countries -> continents (country_continents cache shared with
   pipelines/visual_art/build_pool.py).
4. Exemplars: per style the top --per-style (15) buildings ranked
   tier 0 = UNESCO site itself (P757 / P1435 Q9259),
   tier 1 = part of a UNESCO site (P361 -> item with P757),
   tier 2 = other heritage designation (P1435),
   tier 3 = none; then sitelinks. Plus "unstyled heritage": UNESCO items with
   no P149 at all (style empty), so major sites aren't lost.
5. Exemplar details (label, countries, coordinates, inception, architects,
   designations, P31) and architects (P84) of the exemplars.

Outputs:
  data/interim/architecture_styles.csv
  data/interim/architecture_exemplars.csv
  data/interim/architecture_architects.csv

Usage: python3 pipelines/architecture/build_styles.py [--workers 2] [--per-style 15]
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

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "visual_art"))
from wikidata import sparql, year_of  # noqa: E402

RAW = os.path.join(ROOT, "data", "raw", "wikidata", "architecture")
POOL_RAW = os.path.join(ROOT, "data", "raw", "wikidata", "pool")
OUT_DIR = os.path.join(ROOT, "data", "interim")
CHUNK = 200
BUILDING_BUDGET = 6000  # buildings per per-style-chunk query

ARCH_STYLE = "Q32880"
WHS = "Q9259"  # World Heritage Site (P1435 value)
CONTINENTS = {"Q46": "Europe", "Q48": "Asia", "Q15": "Africa", "Q49": "North America",
              "Q18": "South America", "Q55643": "Oceania", "Q538": "Oceania", "Q3960": "Oceania",
              "Q51": "Antarctica"}
# Instance-of types that make a P149 value count as a style when it is not in the
# architectural-style class tree (measured 2026-10-28: types of P149 values).
P149_TYPES = {
    "Q968159": "art movement", "Q1792644": "art style", "Q65266274": "art style of an area",
    "Q1292119": "style", "Q3326717": "literary movement", "Q2198855": "cultural movement",
    "Q99527323": "architecture of geographic location", "Q65442304": "architecture by ethnic group",
    "Q1792379": "art genre", "Q11514315": "historical period", "Q3326867": "painting movement",
    "Q111676757": "aspect in a historical period", "Q25679497": "art of an area",
    "Q2736610": "artistic school", "Q11042": "culture", "Q6428674": "era",
    "Q465299": "archaeological culture", "Q4787070": "architectural technology",
}

WORKERS = 2


def q(query):
    """Cached SPARQL (one JSON file per distinct query text)."""
    h = hashlib.sha1(query.encode()).hexdigest()[:16]
    path = os.path.join(RAW, f"q_{h}.json")
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    rows = sparql(query)
    tmp = path + ".tmp"
    json.dump(rows, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
    os.replace(tmp, path)
    return rows


def run_all(queries, label):
    """Run queries with at most WORKERS concurrent; returns their results in order."""
    out = []
    with ThreadPoolExecutor(WORKERS) as pool:
        for i, rows in enumerate(pool.map(q, queries), 1):
            out.append(rows)
            if i % 10 == 0 or i == len(queries):
                print(f"  {label}: {i}/{len(queries)}")
    return out


def chunks(items, n=CHUNK):
    return [items[i:i + n] for i in range(0, len(items), n)]


def values(qids):
    return " ".join("wd:" + x for x in qids)


def is_qid(x):
    return bool(x) and re.fullmatch(r"Q\d+", x) is not None


# ---------------------------------------------------------------- 1. style set

def style_set():
    cls = {r["s"] for r in q(f"SELECT DISTINCT ?s WHERE {{ ?s wdt:P31/wdt:P279* wd:{ARCH_STYLE} }}")}
    sub = {r["s"] for r in q(f"""SELECT DISTINCT ?s WHERE {{ ?x wdt:P31/wdt:P279* wd:{ARCH_STYLE} . ?s wdt:P279+ ?x . }}""")} - cls
    used = {r["st"]: int(r["n"]) for r in q("SELECT ?st (COUNT(DISTINCT ?b) AS ?n) WHERE { ?b wdt:P149 ?st } GROUP BY ?st")
            if is_qid(r["st"])}
    other = sorted(set(used) - cls - sub)
    types = collections.defaultdict(set)
    for rows in run_all([f"SELECT ?s ?t WHERE {{ VALUES ?s {{ {values(c)} }} ?s wdt:P31 ?t }}" for c in chunks(other)], "P149 value types"):
        for r in rows:
            types[r["s"]].add(r["t"])
    source = {s: "class" for s in cls}
    source.update({s: "subclass" for s in sub})
    for s in other:
        hit = sorted(P149_TYPES[t] for t in types[s] if t in P149_TYPES)
        if hit:
            source[s] = "p149:" + "|".join(hit)
    skipped = [s for s in other if s not in source]
    print(f"styles: {len(cls)} class, {len(sub)} subclass-only, {len(source) - len(cls) - len(sub)} other P149 values; "
          f"{len(skipped)} P149 values skipped ({sum(used[s] for s in skipped)} uses)")
    return source


# ---------------------------------------------------------------- 2. style facts

STYLE_PROPS = ["P571", "P580", "P582", "P495", "P17", "P30", "P279", "P361", "P737", "P1014", "P31", "P1705"]


def style_facts(styles):
    props = " ".join("wdt:" + p for p in STYLE_PROPS)
    facts = {s: {"claims": collections.defaultdict(list)} for s in styles}
    for rows in run_all([f"""SELECT ?s ?prop ?v WHERE {{ VALUES ?s {{ {values(c)} }}
              VALUES ?prop {{ {props} }} ?s ?prop ?v . }}""" for c in chunks(styles)], "style claims"):
        for r in rows:
            p = r["prop"].rsplit("/", 1)[-1]
            if r["v"] not in facts[r["s"]]["claims"][p]:
                facts[r["s"]]["claims"][p].append(r["v"])
    for rows in run_all([f"""SELECT ?s ?sl (SAMPLE(?en) AS ?label) (SAMPLE(?any) AS ?anylabel) (SAMPLE(?al) AS ?anylang) WHERE {{
              VALUES ?s {{ {values(c)} }} ?s wikibase:sitelinks ?sl .
              OPTIONAL {{ ?s rdfs:label ?en FILTER(LANG(?en) = "en") }}
              OPTIONAL {{ ?s rdfs:label ?any BIND(LANG(?any) AS ?al) }}
            }} GROUP BY ?s ?sl""" for c in chunks(styles)], "style labels"):
        for r in rows:
            facts[r["s"]].update(r)
    return facts


# ---------------------------------------------------------------- 3. buildings

def building_rows(style_counts):
    """All (building, style) pairs with ranking flags, chunked by building budget."""
    batches, cur, n = [], [], 0
    for s, c in sorted(style_counts.items(), key=lambda x: -x[1]):
        if cur and (n + c > BUILDING_BUDGET or len(cur) >= CHUNK):
            batches.append(cur)
            cur, n = [], 0
        cur.append(s)
        n += c
    if cur:
        batches.append(cur)
    queries = [f"""SELECT ?b ?st ?sl (SAMPLE(?c) AS ?country) (MIN(?inc) AS ?inception)
              (MAX(?w) AS ?unesco) (MAX(?pw) AS ?unesco_part) (COUNT(DISTINCT ?h) AS ?n_her) WHERE {{
              VALUES ?st {{ {values(b)} }} ?b wdt:P149 ?st ; wikibase:sitelinks ?sl .
              OPTIONAL {{ ?b wdt:P17 ?c }}
              OPTIONAL {{ ?b wdt:P571 ?inc }}
              OPTIONAL {{ {{ ?b wdt:P757 [] }} UNION {{ ?b wdt:P1435 wd:{WHS} }} BIND(1 AS ?w) }}
              OPTIONAL {{ ?b wdt:P361 ?part . ?part wdt:P757 [] . BIND(1 AS ?pw) }}
              OPTIONAL {{ ?b wdt:P1435 ?h }}
            }} GROUP BY ?b ?st ?sl""" for b in batches]
    out = []
    for rows in run_all(queries, "building batches"):
        out.extend(rows)
    return out


def unstyled_heritage_rows():
    out = {}
    for pat in ("?b wdt:P757 []", f"?b wdt:P1435 wd:{WHS}"):
        for r in q(f"""SELECT ?b ?sl (SAMPLE(?c) AS ?country) (MIN(?inc) AS ?inception)
              (COUNT(DISTINCT ?h) AS ?n_her) (MAX(?pw) AS ?unesco_part) WHERE {{
              {pat} . ?b wikibase:sitelinks ?sl .
              FILTER NOT EXISTS {{ ?b wdt:P149 [] }}
              OPTIONAL {{ ?b wdt:P17 ?c }}
              OPTIONAL {{ ?b wdt:P571 ?inc }}
              OPTIONAL {{ ?b wdt:P1435 ?h }}
              OPTIONAL {{ ?b wdt:P361 ?part . ?part wdt:P757 [] . BIND(1 AS ?pw) }}
            }} GROUP BY ?b ?sl"""):
            r["unesco"] = "1"
            r["st"] = ""
            out.setdefault(r["b"], r)
    return list(out.values())


def tier(r):
    if r.get("unesco"):
        return 0
    if r.get("unesco_part"):
        return 1
    if int(r.get("n_her") or 0):
        return 2
    return 3


# ---------------------------------------------------------------- helpers

def fetch_country_continents(countries):
    """Continent(s) per country QID; same cache and paths as visual_art/build_pool.py."""
    path = os.path.join(POOL_RAW, "country_continents.json")
    os.makedirs(POOL_RAW, exist_ok=True)
    known = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    for prop_path in ["wdt:P30", "wdt:P17/wdt:P30", "wdt:P1366/wdt:P30", "wdt:P36/wdt:P17/wdt:P30"]:
        todo = [c for c in countries if c not in known or not known[c]]
        if not todo:
            break
        for c in todo:
            known.setdefault(c, [])
        for rows in run_all([f"SELECT ?c ?cont WHERE {{ VALUES ?c {{ {values(ch)} }} ?c {prop_path} ?cont . }}"
                             for ch in chunks(todo, 100)], f"continents {prop_path}"):
            for r in rows:
                if r["cont"] not in known[r["c"]]:
                    known[r["c"]].append(r["cont"])
        json.dump(known, open(path, "w", encoding="utf-8"))
    return known


def fetch_labels(qids):
    path = os.path.join(RAW, "labels.json")
    labels = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    todo = sorted({x for x in qids if is_qid(x)} - set(labels))
    for rows in run_all([f"""SELECT ?x (SAMPLE(?en) AS ?l) (SAMPLE(?any) AS ?a) WHERE {{ VALUES ?x {{ {values(c)} }}
              OPTIONAL {{ ?x rdfs:label ?en FILTER(LANG(?en) = "en") }} OPTIONAL {{ ?x rdfs:label ?any }} }} GROUP BY ?x"""
                         for c in chunks(todo, 400)], "labels"):
        for r in rows:
            labels[r["x"]] = r.get("l") or r.get("a") or ""
    json.dump(labels, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    return labels


def entity_claims(qids, props, label):
    """{qid: {prop: [values]}} for the given direct properties."""
    out = {x: collections.defaultdict(list) for x in qids}
    pv = " ".join("wdt:" + p for p in props)
    for rows in run_all([f"""SELECT ?s ?prop ?v WHERE {{ VALUES ?s {{ {values(c)} }}
              VALUES ?prop {{ {pv} }} ?s ?prop ?v . }}""" for c in chunks(qids)], label):
        for r in rows:
            p = r["prop"].rsplit("/", 1)[-1]
            if r["v"] not in out[r["s"]][p]:
                out[r["s"]][p].append(r["v"])
    return out


def years(vals):
    return sorted(y for y in (year_of(v) for v in vals) if y is not None)


def pct(sorted_vals, p):
    if not sorted_vals:
        return ""
    return sorted_vals[min(len(sorted_vals) - 1, int(p * (len(sorted_vals) - 1) + 0.5))]


def continent_names(country_list, continents):
    names = []
    for c in country_list:
        for cont in continents.get(c, []):
            n = CONTINENTS.get(cont)
            if n and n not in names:
                names.append(n)
    return names


# ---------------------------------------------------------------- main

def main():
    global WORKERS
    ap = argparse.ArgumentParser()
    # The query service allows 5 concurrent queries per IP; other jobs use 3.
    ap.add_argument("--workers", type=int, default=2, choices=range(1, 4))
    ap.add_argument("--per-style", type=int, default=15)
    args = ap.parse_args()
    WORKERS = args.workers
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    source = style_set()
    styles = sorted(source)
    facts = style_facts(styles)

    print("fetching buildings")
    used = {r["st"]: int(r["n"]) for r in q("SELECT ?st (COUNT(DISTINCT ?b) AS ?n) WHERE { ?b wdt:P149 ?st } GROUP BY ?st")
            if is_qid(r["st"])}
    brows = building_rows({s: used[s] for s in styles if s in used})
    by_style = collections.defaultdict(list)
    for r in brows:
        by_style[r["st"]].append(r)
    unstyled = unstyled_heritage_rows()
    print(f"  {len(brows)} building-style pairs, {len({r['b'] for r in brows})} buildings; {len(unstyled)} unstyled UNESCO items")

    # Country -> continent for building countries and style countries.
    countries = {r["country"] for r in brows + unstyled if is_qid(r.get("country"))}
    for f in facts.values():
        countries.update(c for p in ("P495", "P17") for c in f["claims"].get(p, []) if is_qid(c))
    continents = fetch_country_continents(sorted(countries))

    # Substyle tree (P279 within the style set) for counts including substyles.
    children = collections.defaultdict(set)
    for s in styles:
        for p in facts[s]["claims"].get("P279", []):
            if p in source:
                children[p].add(s)

    def descendants(s):
        seen, stack = {s}, [s]
        while stack:
            for c in children[stack.pop()]:
                if c not in seen:
                    seen.add(c)
                    stack.append(c)
        return seen

    # ---- exemplar selection
    selected = []  # (style, row, rank)
    for s in styles:
        ranked = sorted(by_style.get(s, []), key=lambda r: (tier(r), -int(r["sl"]), r["b"]))
        for i, r in enumerate(ranked[:args.per_style], 1):
            selected.append((s, r, i))
    for i, r in enumerate(sorted(unstyled, key=lambda r: (-int(r["sl"]), r["b"])), 1):
        selected.append(("", r, i))
    ex_qids = sorted({r["b"] for _, r, _ in selected})
    print(f"{len(selected)} exemplar rows, {len(ex_qids)} distinct items; fetching details")
    details = entity_claims(ex_qids, ["P17", "P625", "P571", "P84", "P1435", "P757", "P31"], "exemplar claims")
    architects = sorted({a for d in details.values() for a in d.get("P84", []) if is_qid(a)})
    arch_claims = entity_claims(architects, ["P569", "P570", "P27"], "architect claims")
    arch_sl = {}
    for rows in run_all([f"SELECT ?s ?sl WHERE {{ VALUES ?s {{ {values(c)} }} ?s wikibase:sitelinks ?sl }}"
                         for c in chunks(architects)], "architect sitelinks"):
        arch_sl.update({r["s"]: r["sl"] for r in rows})
    more_countries = {c for d in details.values() for c in d.get("P17", []) if is_qid(c)} - set(continents)
    if more_countries:
        continents.update(fetch_country_continents(sorted(more_countries)))

    want_labels = set(styles) | set(ex_qids) | set(architects) | countries | set(continents)
    for f in facts.values():
        for p in ("P279", "P361", "P737", "P30", "P31"):
            want_labels.update(f["claims"].get(p, []))
    for d in details.values():
        for p in ("P17", "P1435", "P31"):
            want_labels.update(d.get(p, []))
    for d in arch_claims.values():
        want_labels.update(d.get("P27", []))
    labels = fetch_labels(want_labels)

    def lab(x):
        return labels.get(x, "")

    def qlist(xs):
        return "|".join(x for x in xs if is_qid(x))

    def llist(xs):
        return "|".join(lab(x) for x in xs if is_qid(x))

    # ---- styles CSV
    style_rows = []
    for s in styles:
        f, c = facts[s], facts[s]["claims"]
        bs = by_style.get(s, [])
        start = years(c.get("P571", []) + c.get("P580", []))
        end = years(c.get("P582", []))
        incs = sorted(y for y in (year_of(r.get("inception")) for r in bs) if y is not None)
        bcountries = collections.Counter(r["country"] for r in bs if is_qid(r.get("country")))
        bconts = collections.Counter()
        for cty, n in bcountries.items():
            for name in continent_names([cty], continents):
                bconts[name] += n
        n_with_country = sum(bcountries.values())
        explicit_c = [x for x in c.get("P495", []) + c.get("P17", []) if is_qid(x)]
        explicit_cont = continent_names(explicit_c, continents)
        for x in c.get("P30", []):
            n = CONTINENTS.get(x)
            if n and n not in explicit_cont:
                explicit_cont.append(n)
        dom_cont, dom_share = "", ""
        if bconts:
            dom_cont, n = bconts.most_common(1)[0]
            dom_share = round(n / n_with_country, 2)
        region = "|".join(explicit_cont) if explicit_cont else dom_cont
        region_source = "explicit" if explicit_cont else ("buildings" if dom_cont else "")
        if start:
            p_start, p_src = start[0], "explicit"
        elif len(incs) >= 3:
            p_start, p_src = pct(incs, 0.1), "buildings_p10"
        elif incs:
            p_start, p_src = incs[0], "buildings_min"
        else:
            p_start, p_src = "", ""
        p_end = end[-1] if end else (pct(incs, 0.9) if len(incs) >= 3 else "")
        desc = descendants(s)
        incl = {r["b"] for d in desc for r in by_style.get(d, [])}
        uniq = {r["b"]: r for r in bs}
        native = c.get("P1705", [])
        style_rows.append({
            "qid": s, "label": f.get("label") or f.get("anylabel", ""),
            "label_lang": "en" if f.get("label") else f.get("anylang", ""),
            "native_label": native[0] if native else "",
            "sitelinks": f.get("sl", "0"), "source": source[s],
            "instance_of": llist(c.get("P31", [])),
            "inception": start[0] if start else "", "end": end[-1] if end else "",
            "buildings_inception_p10": pct(incs, 0.1), "buildings_inception_median": pct(incs, 0.5),
            "buildings_inception_p90": pct(incs, 0.9), "buildings_with_inception": len(incs),
            "period_start": p_start, "period_end": p_end, "period_source": p_src,
            "century": (p_start // 100 + (1 if p_start > 0 else 0)) if isinstance(p_start, int) else "",
            "country_explicit": qlist(explicit_c), "country_explicit_label": llist(explicit_c),
            "continent_explicit": "|".join(explicit_cont),
            "buildings_top_countries": "|".join(f"{lab(k)} ({n})" for k, n in bcountries.most_common(3)),
            "buildings_dominant_continent": dom_cont, "buildings_dominant_continent_share": dom_share,
            "region": region, "region_source": region_source,
            "parent_subclass_of": qlist(c.get("P279", [])), "parent_subclass_of_label": llist(c.get("P279", [])),
            "part_of": qlist(c.get("P361", [])), "part_of_label": llist(c.get("P361", [])),
            "influenced_by": qlist(c.get("P737", [])), "influenced_by_label": llist(c.get("P737", [])),
            "aat_id": "|".join(c.get("P1014", [])),
            "n_buildings": len(uniq),
            "n_buildings_incl_substyles": len(incl),
            "n_unesco": sum(1 for r in uniq.values() if r.get("unesco")),
            "n_unesco_or_part": sum(1 for r in uniq.values() if tier(r) <= 1),
            "n_heritage": sum(1 for r in uniq.values() if tier(r) <= 2),
            "buildings_sitelinks": sum(int(r["sl"]) for r in uniq.values()),
        })
    style_rows.sort(key=lambda r: -int(r["sitelinks"]))
    write_csv(os.path.join(OUT_DIR, "architecture_styles.csv"), style_rows)

    # ---- exemplars CSV
    ex_rows = []
    arch_links = collections.defaultdict(lambda: {"buildings": [], "styles": []})
    for s, r, rank in selected:
        d = details[r["b"]]
        coords = d.get("P625", [])
        m = re.match(r"Point\(([-\d.eE]+) ([-\d.eE]+)\)", coords[0]) if coords else None
        incs = years(d.get("P571", []))
        arch = [a for a in d.get("P84", []) if is_qid(a)]
        des = [x for x in d.get("P1435", []) if is_qid(x)]
        ctys = [x for x in d.get("P17", []) if is_qid(x)]
        ex_rows.append({
            "qid": r["b"], "label": lab(r["b"]), "style_qid": s, "style_label": lab(s) if s else "",
            "list": "style" if s else "unstyled_heritage", "rank": rank, "tier": tier(r),
            "tier_label": ["unesco", "part_of_unesco", "heritage", "none"][tier(r)],
            "country": qlist(ctys), "country_label": llist(ctys),
            "continent": "|".join(continent_names(ctys, continents)),
            "lat": m.group(2) if m else "", "lon": m.group(1) if m else "",
            "inception": incs[0] if incs else "",
            "architects": qlist(arch), "architects_label": llist(arch),
            "unesco_id": "|".join(d.get("P757", [])),
            "heritage": qlist(des), "heritage_label": llist(des),
            "sitelinks": r["sl"],
            "instance_of": qlist(d.get("P31", [])), "instance_of_label": llist(d.get("P31", [])),
        })
        for a in arch:
            if r["b"] not in arch_links[a]["buildings"]:
                arch_links[a]["buildings"].append(r["b"])
            if s and s not in arch_links[a]["styles"]:
                arch_links[a]["styles"].append(s)
    write_csv(os.path.join(OUT_DIR, "architecture_exemplars.csv"), ex_rows)

    # ---- architects CSV
    arch_rows = []
    for a, link in arch_links.items():
        c = arch_claims.get(a, {})
        b, dth = years(c.get("P569", [])), years(c.get("P570", []))
        arch_rows.append({
            "qid": a, "label": lab(a), "sitelinks": arch_sl.get(a, ""),
            "birth": b[0] if b else "", "death": dth[0] if dth else "",
            "citizenship": llist(c.get("P27", [])),
            "n_buildings": len(link["buildings"]), "buildings": qlist(link["buildings"]),
            "buildings_label": llist(link["buildings"]),
            "n_styles": len(link["styles"]), "styles": qlist(link["styles"]), "styles_label": llist(link["styles"]),
        })
    arch_rows.sort(key=lambda r: (-r["n_buildings"], -int(r["sitelinks"] or 0)))
    write_csv(os.path.join(OUT_DIR, "architecture_architects.csv"), arch_rows)

    n5 = sum(1 for r in style_rows if int(r["sitelinks"]) >= 5)
    print(f"done: {len(style_rows)} styles ({n5} with >=5 sitelinks), {len(ex_rows)} exemplar rows, {len(arch_rows)} architects")


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"  wrote {path} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
