"""Build TV-format clusters from Wikidata: each format with its national adaptations.

sourcing-plan.md §6: the unit of unscripted TV is the *format* (Idol, Big Brother,
Bake Off, ...), with national versions as children, under genre clusters.

A parent is a format if at least MIN_ADAPTATIONS TV programmes link to it by
  P144  based on            (Family Feud, Bake Off, The Million Pound Drop, ...)
  P8345 media franchise     (Got Talent, Idol, Big Brother, ...)
  P179  part of the series
Genres (P136) of the parent and its children decide the genre cluster; formats
without an unscripted genre are kept as `scripted` (remakes such as Yo soy Betty,
la fea or The Office), which scripted TV can use for its remake links.
IMDb votes per adaptation come from the IMDb ratings file (pipelines/tv/build_candidates.py).

Output: data/interim/unscripted_formats.csv      one row per format
        data/interim/unscripted_adaptations.csv  one row per national version

Usage: python3 pipelines/unscripted/build_formats.py [--min-adaptations 3]
"""
import argparse
import collections
import csv
import gzip
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "visual_art"))
from wikidata import sparql, year_of  # noqa: E402

IMDB_RATINGS = os.path.join(ROOT, "data", "raw", "imdb", "title.ratings.tsv.gz")
OUT_FORMATS = os.path.join(ROOT, "data", "interim", "unscripted_formats.csv")
OUT_ADAPT = os.path.join(ROOT, "data", "interim", "unscripted_adaptations.csv")

PROGRAMME_CLASSES = "wd:Q5398426 wd:Q15416 wd:Q1259759 wd:Q526877"  # TV series, TV programme, miniseries, web series
LINKS = {"P144": "based on", "P8345": "media franchise", "P179": "part of the series"}
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


def adaptations(prop):
    return sparql(f"""SELECT ?f ?a ?al ?s ?imdb (SAMPLE(?cc) AS ?country) (MIN(?d) AS ?start) WHERE {{
      ?a wdt:{prop} ?f ; wdt:P31 ?c ; wikibase:sitelinks ?s .
      VALUES ?c {{ {PROGRAMME_CLASSES} }}
      {{ SELECT ?f WHERE {{ ?x wdt:{prop} ?f ; wdt:P31 ?c2 . VALUES ?c2 {{ {PROGRAMME_CLASSES} }} }}
         GROUP BY ?f HAVING(COUNT(DISTINCT ?x) >= 2) }}
      OPTIONAL {{ ?a wdt:P345 ?imdb }}
      OPTIONAL {{ ?a wdt:P495/wdt:P297 ?cc }}
      OPTIONAL {{ ?a wdt:P580|wdt:P577 ?d }}
      OPTIONAL {{ ?a rdfs:label ?al FILTER(LANG(?al) = "en") }}
    }} GROUP BY ?f ?a ?al ?s ?imdb""")


def labels_and_sitelinks(qids):
    out = {}
    qids = sorted(qids)
    for i in range(0, len(qids), 300):
        values = " ".join("wd:" + q for q in qids[i:i + 300])
        for r in sparql(f"""SELECT ?x ?l ?s WHERE {{ VALUES ?x {{ {values} }} ?x wikibase:sitelinks ?s .
              OPTIONAL {{ ?x rdfs:label ?l FILTER(LANG(?l) = "en") }} }}"""):
            out[r["x"]] = (r.get("l", ""), int(r["s"]))
    return out


def genre_clusters(qids):
    """{qid: set of cluster names} from P136 genres, following genre subclasses."""
    roots = " ".join(f"wd:{q}" for _, q in CLUSTERS)
    root_name = {q: n for n, q in CLUSTERS}
    out = collections.defaultdict(set)
    qids = sorted(qids)
    for i in range(0, len(qids), 300):
        values = " ".join("wd:" + q for q in qids[i:i + 300])
        for r in sparql(f"""SELECT DISTINCT ?x ?root WHERE {{ VALUES ?x {{ {values} }} VALUES ?root {{ {roots} }}
              ?x wdt:P136 ?g . ?g wdt:P279* ?root . }}"""):
            out[r["x"]].add(root_name[r["root"]])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-adaptations", type=int, default=3)
    args = ap.parse_args()

    children = collections.defaultdict(dict)  # format -> {adaptation qid: row}
    link_of = collections.defaultdict(set)
    for prop, name in LINKS.items():
        rows = adaptations(prop)
        print(f"  {name} ({prop}): {len(rows)} links")
        for r in rows:
            children[r["f"]].setdefault(r["a"], r)
            link_of[r["f"]].add(prop)
    # A version can itself be a parent (Got Talent -> Britain's Got Talent -> ...): keep the top.
    child_set = {a for kids in children.values() for a in kids}
    formats = {f: kids for f, kids in children.items()
               if len(kids) >= args.min_adaptations and not (f in child_set and len(kids) < 2 * args.min_adaptations)}
    print(f"{len(formats)} formats with >= {args.min_adaptations} adaptations")

    votes = {}
    with gzip.open(IMDB_RATINGS, "rt", encoding="utf-8") as f:
        next(f)
        for line in f:
            t, _, n = line.rstrip("\n").split("\t")
            votes[t] = int(n)
    meta = labels_and_sitelinks(formats)
    clusters = genre_clusters(set(formats) | {a for kids in formats.values() for a in kids})

    frows, arows = [], []
    for f, kids in formats.items():
        label, sl = meta.get(f, ("", 0))
        cl = collections.Counter(c for q in [f, *kids] for c in clusters.get(q, ()))
        cluster = next((n for n, _ in CLUSTERS if cl[n]), "")
        countries = {k.get("country") for k in kids.values() if k.get("country")}
        years = [y for y in (year_of(k.get("start")) for k in kids.values()) if y]
        frows.append({
            "format_qid": f, "format": label, "kind": "unscripted" if cluster else "scripted",
            "cluster": cluster, "links": "|".join(sorted(link_of[f])), "n_adaptations": len(kids),
            "n_countries": len(countries), "first_year": min(years) if years else "",
            "format_sitelinks": sl, "adaptation_sitelinks": sum(int(k["s"]) for k in kids.values()),
            "imdb_votes_total": sum(votes.get(k.get("imdb"), 0) for k in kids.values()),
        })
        for a, k in kids.items():
            arows.append({"format_qid": f, "format": label, "qid": a, "title": k.get("al", ""),
                          "country": k.get("country", ""), "start_year": year_of(k.get("start")) or "",
                          "tconst": k.get("imdb", ""), "imdb_votes": votes.get(k.get("imdb"), ""), "sitelinks": k["s"]})
    frows.sort(key=lambda r: -r["n_adaptations"])
    for path, rows in ((OUT_FORMATS, frows), (OUT_ADAPT, arows)):
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    kinds = collections.Counter(r["kind"] for r in frows)
    print(f"formats: {dict(kinds)}; adaptations: {len(arows)}")
    print("clusters:", dict(collections.Counter(r["cluster"] for r in frows if r["cluster"])))
    print("largest:", ", ".join(f"{r['format']} ({r['n_adaptations']})" for r in frows[:15]))
    print(f"wrote {OUT_FORMATS}\nwrote {OUT_ADAPT}")


if __name__ == "__main__":
    main()
