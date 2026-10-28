"""Look up Letterboxd rating counts for film candidates via the MDBList API.

Reads data/interim/film_candidates.csv, fetches every candidate through MDBList's
Media Info Batch endpoint (pipelines/common/mdblist.py; raw responses cached, so
an interrupted run resumes), then writes data/interim/film_ratings.csv with
Letterboxd/IMDb/TMDB/Trakt values and vote counts per film, plus genres (IMDb
and MDBList), country, language and runtime for the later genre and regional
organisation.

Requires the MDBLIST_API_KEY environment variable.

Usage:
  python3 pipelines/film/mdblist_enrich.py --probe      # one small batch, prints the raw shape
  python3 pipelines/film/mdblist_enrich.py              # full run
  python3 pipelines/film/mdblist_enrich.py --parse-only # rebuild the CSV from the cache
"""
import argparse
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "common"))
import mdblist  # noqa: E402

SOURCES = ("letterboxd", "imdb", "tmdb", "trakt")
CANDIDATES = os.path.join(ROOT, "data", "interim", "film_candidates.csv")
CACHE = os.path.join(ROOT, "data", "raw", "mdblist", "media_batch.jsonl")
OUT_PATH = os.path.join(ROOT, "data", "interim", "film_ratings.csv")


def parse():
    # IMDb genres come from the candidate file. MDBList's genres are mostly TMDB's
    # plus a few of its own (e.g. "Sci-Fi" next to "Science Fiction", "Anime: Seinen").
    # Both feed the later genre -> cluster organisation, so keep both raw.
    with open(CANDIDATES, encoding="utf-8") as f:
        imdb = {row["tconst"]: row for row in csv.DictReader(f)}
    films = {}
    for item in mdblist.cached_items(CACHE):
        tconst = mdblist.imdb_id_of(item)
        if tconst:
            films[tconst] = mdblist.add_ratings(mdblist.base_row(item, imdb.get(tconst, {})), item, SOURCES)
    cols = ["tconst", "tmdb_id", "mdblist_title", "year", "imdb_title_type", "runtime", "country", "language",
            "imdb_genres", "mdblist_genres"] + [f"{s}_{k}" for s in SOURCES for k in ("value", "votes")]
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as out:
        w = csv.DictWriter(out, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(films.values())

    lb = [int(r["letterboxd_votes"]) for r in films.values() if r.get("letterboxd_votes")]
    print(f"parsed {len(films)} films; {len(lb)} have Letterboxd vote counts")
    for th in (1_000, 5_000, 10_000, 25_000, 100_000):
        print(f"  Letterboxd ratings >= {th:>7,}: {sum(v >= th for v in lb):,}")
    missing = len(imdb) - len(lb)
    print(f"candidates without a Letterboxd count: {missing:,} ({len(imdb) - len(films):,} not returned by MDBList at all)")
    print(f"wrote {OUT_PATH}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--parse-only", action="store_true")
    args = ap.parse_args()
    if not args.parse_only:
        with open(CANDIDATES, encoding="utf-8") as f:
            ids = [row["tconst"] for row in csv.DictReader(f)]
        key = mdblist.api_key()
        if args.probe:
            mdblist.probe(key, ids, "movie")
            return
        mdblist.fetch_all(key, ids, CACHE, "movie")
    parse()


if __name__ == "__main__":
    main()
