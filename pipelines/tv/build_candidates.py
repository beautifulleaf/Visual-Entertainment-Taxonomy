"""Build the series candidate set from IMDb's non-commercial datasets.

Keeps tvSeries and tvMiniSeries with at least MIN_VOTES IMDb votes, with
episode counts from title.episode (long-running serials such as telenovelas,
dizi and Indian daily soaps stand out by these). The vote floor is far below
the inclusion bar (sourcing-plan.md §3) so the regional-percentile rule has
under-voted traditions to work with.

The output feeds mdblist_enrich.py, then route.py, which splits series into the
scripted-TV, anime, Asian-drama and unscripted databases.

Usage: python3 pipelines/tv/build_candidates.py [--min-votes 100]
"""
import argparse
import collections
import csv
import gzip
import os
import urllib.request

IMDB_BASE = "https://datasets.imdbws.com/"
FILES = ("title.basics.tsv.gz", "title.ratings.tsv.gz", "title.episode.tsv.gz")
SERIES_TYPES = {"tvSeries", "tvMiniSeries"}

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DIR = os.path.join(ROOT, "data", "raw", "imdb")
OUT_PATH = os.path.join(ROOT, "data", "interim", "tv_candidates.csv")


def download(name):
    path = os.path.join(RAW_DIR, name)
    if not os.path.exists(path):
        print(f"downloading {name}")
        urllib.request.urlretrieve(IMDB_BASE + name, path)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-votes", type=int, default=100)
    args = ap.parse_args()

    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    basics_path, ratings_path, episode_path = (download(f) for f in FILES)

    votes = {}
    with gzip.open(ratings_path, "rt", encoding="utf-8") as f:
        next(f)
        for line in f:
            tconst, avg, num = line.rstrip("\n").split("\t")
            if int(num) >= args.min_votes:
                votes[tconst] = (avg, int(num))

    episodes, seasons = collections.Counter(), collections.defaultdict(set)
    with gzip.open(episode_path, "rt", encoding="utf-8") as f:
        next(f)
        for line in f:
            _, parent, season, _ = line.rstrip("\n").split("\t")
            if parent in votes:
                episodes[parent] += 1
                if season != "\\N":
                    seasons[parent].add(season)

    n = collections.Counter()
    with gzip.open(basics_path, "rt", encoding="utf-8") as f, open(OUT_PATH, "w", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        w.writerow(["tconst", "title_type", "title", "original_title", "start_year", "end_year", "runtime",
                    "genres", "imdb_rating", "imdb_votes", "episodes", "seasons"])
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[1] not in SERIES_TYPES or p[0] not in votes or p[4] == "1":  # p[4] = isAdult
                continue
            avg, num = votes[p[0]]
            clean = [None if v == "\\N" else v for v in p]
            w.writerow([p[0], p[1], p[2], p[3], clean[5], clean[6], clean[7], clean[8], avg, num,
                        episodes[p[0]], len(seasons[p[0]])])
            n[p[1]] += 1
    print(f"wrote {sum(n.values())} candidates (>= {args.min_votes} IMDb votes: {dict(n)}) to {OUT_PATH}")


if __name__ == "__main__":
    main()
