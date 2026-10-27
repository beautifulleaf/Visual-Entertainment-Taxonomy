"""Build the film candidate set from IMDb's non-commercial datasets.

Downloads title.basics and title.ratings (refreshed daily by IMDb) and keeps
film-like titles with at least MIN_VOTES IMDb votes. The output is the input
for mdblist_enrich.py, which looks up Letterboxd rating counts.

Usage: python3 pipelines/film/build_candidates.py [--min-votes 500]
"""
import argparse
import csv
import gzip
import os
import urllib.request

IMDB_BASE = "https://datasets.imdbws.com/"
FILES = ("title.basics.tsv.gz", "title.ratings.tsv.gz")
FILM_TYPES = {"movie", "tvMovie", "short", "video", "tvSpecial"}

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DIR = os.path.join(ROOT, "data", "raw", "imdb")
OUT_PATH = os.path.join(ROOT, "data", "interim", "film_candidates.csv")


def download(name):
    path = os.path.join(RAW_DIR, name)
    if not os.path.exists(path):
        print(f"downloading {name}")
        urllib.request.urlretrieve(IMDB_BASE + name, path)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-votes", type=int, default=500)
    args = ap.parse_args()

    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    basics_path, ratings_path = (download(f) for f in FILES)

    votes = {}
    with gzip.open(ratings_path, "rt", encoding="utf-8") as f:
        next(f)
        for line in f:
            tconst, avg, num = line.rstrip("\n").split("\t")
            if int(num) >= args.min_votes:
                votes[tconst] = (avg, int(num))

    n = 0
    with gzip.open(basics_path, "rt", encoding="utf-8") as f, open(OUT_PATH, "w", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        w.writerow(["tconst", "title_type", "title", "original_title", "year", "runtime", "genres", "imdb_rating", "imdb_votes"])
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[1] not in FILM_TYPES or p[0] not in votes or p[4] == "1":  # p[4] = isAdult
                continue
            avg, num = votes[p[0]]
            w.writerow([p[0], p[1], p[2], p[3], p[5], p[7], p[8], avg, num])
            n += 1
    print(f"wrote {n} candidates (>= {args.min_votes} IMDb votes) to {OUT_PATH}")


if __name__ == "__main__":
    main()
