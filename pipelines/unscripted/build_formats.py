"""Build TV-format families from Wikidata: each format with its national versions.

sourcing-plan.md §6: the unit of unscripted TV is the *format* (Idol, Big Brother,
Bake Off, ...), with national versions as children, under genre clusters.

Wikidata models a format family inconsistently: the Idol family alone is spread
over Pop Idol, an "Idols" franchise item and dozens of national items, joined
by any of
  P144  based on               (version -> original)
  P8345 media franchise        (version -> franchise)
  P179  part of the series     (version -> series)
  P4969 derivative work        (original -> version)
So every such link between TV programmes is treated as an edge, and each
connected family is one format. Its name is taken from the member with the most
incoming links (the franchise or original), ties broken by sitelinks.

A family counts as a format if it has >= MIN_VERSIONS programmes from
>= MIN_COUNTRIES countries, no country holding more than MAX_TOP_SHARE of them
unless it spans 5+ (formats are sold across borders; this drops broadcast slots
and anthology strands such as Asadora or Christmas calendars).
Genres (P136) of its members pick the genre cluster. Families without an
unscripted genre are kept as `scripted` (remakes such as Yo soy Betty, la fea
or The Office), which scripted TV can use for remake links.
seeds/unscripted/formats_checklist.txt lists well-known formats; each run
reports which of them were not found. seeds/unscripted/format_additions.csv adds
hand-curated families whose versions Wikidata does not link to each other.

Output: data/interim/unscripted_formats.csv      one row per format
        data/interim/unscripted_adaptations.csv  one row per version

Usage: python3 pipelines/unscripted/build_formats.py
"""
import collections
import csv
import gzip
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "visual_art"))
from wikidata import sparql, year_of  # noqa: E402

IMDB_RATINGS = os.path.join(ROOT, "data", "raw", "imdb", "title.ratings.tsv.gz")
CHECKLIST = os.path.join(ROOT, "seeds", "unscripted", "formats_checklist.txt")
ADDITIONS = os.path.join(ROOT, "seeds", "unscripted", "format_additions.csv")
OUT_FORMATS = os.path.join(ROOT, "data", "interim", "unscripted_formats.csv")
OUT_ADAPT = os.path.join(ROOT, "data", "interim", "unscripted_adaptations.csv")

PROGRAMME_CLASSES = "wd:Q5398426 wd:Q15416 wd:Q1259759 wd:Q526877"  # TV series, TV programme, miniseries, web series
MIN_VERSIONS, MIN_COUNTRIES = 3, 2
# Broadcast slots (Nichiyo Gekijo, NHK Special) pass the country test on a stray
# co-production; a format is not dominated by one country unless it is in 5+.
MAX_TOP_SHARE = 0.8
# (property, True if the subject is the version and the object the parent)
EDGES = [("P144", True), ("P8345", True), ("P179", True), ("P4969", False)]
# Genre clusters (§6), matched on P136 and its subclasses. First match wins.
CLUSTERS = [
    ("talent competition", "Q1484397"),
    ("cooking", "Q1457145"),
    ("dating", "Q5227671"),         # dating game show
    ("game show", "Q846662"),
    ("talk and late night", "Q622812"),
    ("reality competition", "Q111812458"),
    ("reality / docusoap", "Q182415"),
]
CHUNK = 300


def edges(prop, version_is_subject):
    """(version, parent) pairs where the version is a TV programme."""
    if version_is_subject:
        q = f"SELECT ?v ?p WHERE {{ ?v wdt:{prop} ?p ; wdt:P31 ?c . VALUES ?c {{ {PROGRAMME_CLASSES} }} }}"
    else:
        q = f"SELECT ?v ?p WHERE {{ ?p wdt:{prop} ?v . ?v wdt:P31 ?c . VALUES ?c {{ {PROGRAMME_CLASSES} }} }}"
    return [(r["v"], r["p"]) for r in sparql(q) if r["v"].startswith("Q") and r["p"].startswith("Q")]


def node_meta(qids):
    """Label, sitelinks, country, IMDb id, start year and whether the item is a TV programme."""
    out = {}
    qids = sorted(qids)
    for i in range(0, len(qids), CHUNK):
        values = " ".join("wd:" + q for q in qids[i:i + CHUNK])
        for r in sparql(f"""SELECT ?x ?l ?s (SAMPLE(?cc) AS ?country) (SAMPLE(?imdb) AS ?tconst) (MIN(?d) AS ?start)
              (MAX(IF(?c IN ({PROGRAMME_CLASSES.replace(' ', ', ')}), 1, 0)) AS ?prog) WHERE {{
              VALUES ?x {{ {values} }} ?x wikibase:sitelinks ?s .
              OPTIONAL {{ ?x wdt:P31 ?c }}
              OPTIONAL {{ ?x rdfs:label ?l FILTER(LANG(?l) = "en") }}
              OPTIONAL {{ ?x wdt:P495/wdt:P297 ?cc }}
              OPTIONAL {{ ?x wdt:P345 ?imdb }}
              OPTIONAL {{ ?x wdt:P580|wdt:P577 ?d }}
            }} GROUP BY ?x ?l ?s"""):
            out[r["x"]] = {"label": r.get("l", ""), "sitelinks": int(r["s"]), "country": r.get("country", ""),
                           "tconst": r.get("tconst", ""), "start_year": year_of(r.get("start")),
                           "programme": r.get("prog") == "1"}
    return out


def genre_clusters(qids):
    """{qid: set of cluster names} from P136 genres, following genre subclasses."""
    roots = " ".join(f"wd:{q}" for _, q in CLUSTERS)
    root_name = {q: n for n, q in CLUSTERS}
    out = collections.defaultdict(set)
    qids = sorted(qids)
    for i in range(0, len(qids), CHUNK):
        values = " ".join("wd:" + q for q in qids[i:i + CHUNK])
        for r in sparql(f"""SELECT DISTINCT ?x ?root WHERE {{ VALUES ?x {{ {values} }} VALUES ?root {{ {roots} }}
              ?x wdt:P136 ?g . ?g wdt:P279* ?root . }}"""):
            out[r["x"]].add(root_name[r["root"]])
    return out


def components(pairs):
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in pairs:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    groups = collections.defaultdict(set)
    for x in list(parent):
        groups[find(x)].add(x)
    return list(groups.values())


def main():
    pairs, indegree = [], collections.Counter()
    for prop, version_is_subject in EDGES:
        e = edges(prop, version_is_subject)
        print(f"  {prop}: {len(e)} links")
        pairs += e
        indegree.update(p for _, p in e)
    if os.path.exists(ADDITIONS):
        # Hand-curated families whose versions Wikidata does not link (Wife Swap, ...).
        with open(ADDITIONS, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                extra = [(m, row["root_qid"]) for m in row["member_qids"].split("|") if m]
                pairs += extra
                indegree[row["root_qid"]] += len(extra)
    families = [g for g in components(pairs) if len(g) >= MIN_VERSIONS]
    print(f"{len(families)} linked families with >= {MIN_VERSIONS} members")

    meta = node_meta({q for g in families for q in g})
    votes = {}
    with gzip.open(IMDB_RATINGS, "rt", encoding="utf-8") as f:
        next(f)
        for line in f:
            t, _, n = line.rstrip("\n").split("\t")
            votes[t] = int(n)

    kept = []
    for g in families:
        versions = [q for q in g if meta.get(q, {}).get("programme")]
        per_country = collections.Counter(meta[q]["country"] for q in versions if meta[q]["country"])
        countries = set(per_country)
        top_share = max(per_country.values()) / sum(per_country.values()) if per_country else 1
        if (len(versions) >= MIN_VERSIONS and len(countries) >= MIN_COUNTRIES
                and (top_share <= MAX_TOP_SHARE or len(countries) >= 5)):
            kept.append((g, versions, countries))
    clusters = genre_clusters({q for g, _, _ in kept for q in g})

    frows, arows = [], []
    for g, versions, countries in kept:
        root = max(g, key=lambda q: (indegree[q], meta.get(q, {}).get("sitelinks", 0)))
        cl = collections.Counter(c for q in g for c in clusters.get(q, ()))
        cluster = next((n for n, _ in CLUSTERS if cl[n]), "")
        years = [meta[q]["start_year"] for q in versions if meta[q]["start_year"]]
        name = meta.get(root, {}).get("label") or root
        frows.append({
            "format_qid": root, "format": name, "kind": "unscripted" if cluster else "scripted", "cluster": cluster,
            "n_versions": len(versions), "n_countries": len(countries), "first_year": min(years) if years else "",
            "format_sitelinks": meta.get(root, {}).get("sitelinks", 0),
            "versions_sitelinks": sum(meta[q]["sitelinks"] for q in versions),
            "imdb_votes_total": sum(votes.get(meta[q]["tconst"], 0) for q in versions),
            "members": "|".join(sorted(g)),
        })
        for q in versions:
            m = meta[q]
            arows.append({"format_qid": root, "format": name, "qid": q, "title": m["label"], "country": m["country"],
                          "start_year": m["start_year"] or "", "tconst": m["tconst"],
                          "imdb_votes": votes.get(m["tconst"], ""), "sitelinks": m["sitelinks"]})
    frows.sort(key=lambda r: -r["n_versions"])
    for path, rows in ((OUT_FORMATS, frows), (OUT_ADAPT, arows)):
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)

    kinds = collections.Counter(r["kind"] for r in frows)
    print(f"formats: {dict(kinds)} from >= {MIN_COUNTRIES} countries; versions: {len(arows)}")
    print("clusters:", dict(collections.Counter(r["cluster"] for r in frows if r["cluster"])))
    print("largest:", ", ".join(f"{r['format']} ({r['n_versions']})" for r in frows[:20]))
    if os.path.exists(CHECKLIST):
        names = [l.strip() for l in open(CHECKLIST, encoding="utf-8") if l.strip() and not l.startswith("#")]
        member_labels = collections.defaultdict(set)
        for r in frows:
            for q in r["members"].split("|"):
                member_labels[r["format"]].add((meta.get(q, {}).get("label") or "").lower())
        missing = [n for n in names if not any(any(alt.lower() in lab for lab in labs)
                                               for labs in member_labels.values() for alt in n.split("|"))]
        print(f"checklist: {len(names) - len(missing)}/{len(names)} found; missing: {', '.join(missing) or 'none'}")
    print(f"wrote {OUT_FORMATS}\nwrote {OUT_ADAPT}")


if __name__ == "__main__":
    main()
