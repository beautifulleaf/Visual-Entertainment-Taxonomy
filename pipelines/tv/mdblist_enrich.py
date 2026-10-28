"""Enrich series candidates via MDBList (IMDb/TMDB/Trakt votes, country, genres, MAL id).

Reads data/interim/tv_candidates.csv, fetches every candidate through MDBList's
show batch endpoint (pipelines/common/mdblist.py; raw responses cached), then
writes data/interim/tv_ratings.csv. Origin country and the MAL id are what
route.py uses to split series between the databases; Trakt watcher votes are a
secondary audience signal (sourcing-plan.md §3).

Requires the MDBLIST_API_KEY environment variable.

Usage:
  python3 pipelines/tv/mdblist_enrich.py --probe
  python3 pipelines/tv/mdblist_enrich.py
  python3 pipelines/tv/mdblist_enrich.py --parse-only
"""
import argparse
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "common"))
import mdblist  # noqa: E402

SOURCES = ("imdb", "tmdb", "trakt", "tomatoes", "metacritic")
CANDIDATES = os.path.join(ROOT, "data", "interim", "tv_candidates.csv")
CACHE = os.path.join(ROOT, "data", "raw", "mdblist", "show_batch.jsonl")
OUT_PATH = os.path.join(ROOT, "data", "interim", "tv_ratings.csv")


def parse():
    with open(CANDIDATES, encoding="utf-8") as f:
        imdb = {row["tconst"]: row for row in csv.DictReader(f)}
    shows = {}
    for item in mdblist.cached_items(CACHE):
        tconst = mdblist.imdb_id_of(item)
        if not tconst:
            continue
        cand = imdb.get(tconst, {})
        row = mdblist.base_row(item, cand)
        row.update({"start_year": cand.get("start_year"), "end_year": cand.get("end_year"),
                    "episodes": cand.get("episodes"), "seasons": cand.get("seasons"),
                    "companies": "|".join(c.get("name", "") for c in item.get("production_companies") or [] if isinstance(c, dict))})
        shows[tconst] = mdblist.add_ratings(row, item, SOURCES)
    # Candidates MDBList did not return still go to route.py with their IMDb data.
    for tconst, cand in imdb.items():
        if tconst not in shows:
            shows[tconst] = {"tconst": tconst, "mdblist_title": cand["title"], "year": cand["start_year"],
                             "imdb_title_type": cand["title_type"], "start_year": cand["start_year"],
                             "end_year": cand["end_year"], "episodes": cand["episodes"], "seasons": cand["seasons"],
                             "imdb_genres": (cand["genres"] or "").replace(",", "|"), "imdb_votes": cand["imdb_votes"]}
    cols = ["tconst", "tmdb_id", "mal_id", "mdblist_title", "year", "start_year", "end_year", "imdb_title_type",
            "episodes", "seasons", "runtime", "country", "language", "companies", "imdb_genres", "mdblist_genres"] + \
        [f"{s}_{k}" for s in SOURCES for k in ("value", "votes")]
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as out:
        w = csv.DictWriter(out, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(shows.values())
    returned = sum(1 for r in shows.values() if r.get("tmdb_id") or r.get("country"))
    print(f"{len(imdb)} candidates; MDBList returned {returned}; with a country: {sum(1 for r in shows.values() if r.get('country'))}")
    print(f"wrote {OUT_PATH}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--parse-only", action="store_true")
    args = ap.parse_args()
    if not args.parse_only:
        with open(CANDIDATES, encoding="utf-8") as f:
            # Most-voted first, so a run cut short by the daily limit covers the important titles.
            ids = [r["tconst"] for r in sorted(csv.DictReader(f), key=lambda r: -int(r["imdb_votes"]))]
        key = mdblist.api_key()
        if args.probe:
            mdblist.probe(key, ids, "show")
            return
        mdblist.fetch_all(key, ids, CACHE, "show")
    parse()


if __name__ == "__main__":
    main()
