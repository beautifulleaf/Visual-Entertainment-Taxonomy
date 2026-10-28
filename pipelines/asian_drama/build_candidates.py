"""Build the Asian live-action drama candidate set (sourcing-plan.md §5).

Union of
  - series routed to `asian_drama` by pipelines/tv/route.py (IMDb + MDBList origin country), and
  - Wikidata TV series, miniseries and web series that carry a MyDramaList ID (P3868),
joined on IMDb ID. Wikidata supplies the MDL ID where it has one; mdl_fetch.py
resolves the rest through MDL's own search.

Output: data/interim/asian_drama_candidates.csv (input for mdl_fetch.py)

Usage: python3 pipelines/asian_drama/build_candidates.py
"""
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "visual_art"))
from wikidata import sparql, year_of  # noqa: E402

ROUTED = os.path.join(ROOT, "data", "interim", "tv_routed.csv")
OUT_PATH = os.path.join(ROOT, "data", "interim", "asian_drama_candidates.csv")
SERIES_CLASSES = "wd:Q5398426 wd:Q1259759 wd:Q526877 wd:Q15416"  # TV series, miniseries, web series, TV programme


def wikidata_mdl():
    rows = sparql(f"""SELECT ?x ?mdl ?imdb ?label ?s (SAMPLE(?c) AS ?country) (MIN(?d) AS ?start) WHERE {{
      ?x wdt:P3868 ?mdl ; wdt:P31 ?cls ; wikibase:sitelinks ?s .
      VALUES ?cls {{ {SERIES_CLASSES} }}
      OPTIONAL {{ ?x wdt:P345 ?imdb }}
      OPTIONAL {{ ?x wdt:P495/wdt:P297 ?c }}
      OPTIONAL {{ ?x wdt:P580|wdt:P577 ?d }}
      OPTIONAL {{ ?x rdfs:label ?label FILTER(LANG(?label) = "en") }}
    }} GROUP BY ?x ?mdl ?imdb ?label ?s""")
    return rows


def main():
    with open(ROUTED, encoding="utf-8") as f:
        tv = [r for r in csv.DictReader(f) if r["database"] == "asian_drama"]
    by_imdb = {r["tconst"]: r for r in tv}
    out = {}
    for r in tv:
        out[r["tconst"]] = {
            "key": r["tconst"], "tconst": r["tconst"], "wikidata": "", "mdl_id": "", "title": r["mdblist_title"],
            "year": r["start_year"] or r["year"], "country": r["country"], "episodes": r["episodes"],
            "imdb_votes": r.get("imdb_votes"), "tmdb_votes": r.get("tmdb_votes"), "trakt_votes": r.get("trakt_votes"),
            "sitelinks": "", "source": "imdb",
        }
    wd = wikidata_mdl()
    n_new = 0
    for w in wd:
        key = w.get("imdb") if w.get("imdb") in by_imdb else w.get("imdb") or w["x"]
        row = out.get(key)
        if row is None:
            n_new += 1
            row = out[key] = {"key": key, "tconst": w.get("imdb", ""), "title": w.get("label", ""),
                              "year": year_of(w.get("start")), "country": w.get("country", ""), "source": "wikidata"}
        else:
            row["source"] = "imdb+wikidata"
        row.update({"wikidata": w["x"], "mdl_id": w["mdl"], "sitelinks": w["s"]})
    cols = ["key", "tconst", "wikidata", "mdl_id", "title", "year", "country", "episodes", "imdb_votes",
            "tmdb_votes", "trakt_votes", "sitelinks", "source"]
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(out.values())
    print(f"{len(tv)} from the TV harvest, {len(wd)} Wikidata series with an MDL ID ({n_new} not in the TV harvest); "
          f"{len(out)} candidates, {sum(1 for r in out.values() if r.get('mdl_id'))} with a known MDL ID")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
