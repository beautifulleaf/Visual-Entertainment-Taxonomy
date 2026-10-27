"""Look up Letterboxd rating counts for film candidates via the MDBList API.

Reads data/interim/film_candidates.csv, POSTs IMDb IDs in batches of 200 to
MDBList's Media Info Batch endpoint, and caches every raw response (one JSON
object per line), so an interrupted run resumes where it stopped.
Then writes data/interim/film_ratings.csv with Letterboxd/IMDb/TMDB/Trakt
values and vote counts per film, plus genres (IMDb and MDBList), country,
language and runtime for the later genre and regional organisation.

Requires the MDBLIST_API_KEY environment variable.

Usage:
  python3 pipelines/film/mdblist_enrich.py --probe      # one small batch, prints the raw shape
  python3 pipelines/film/mdblist_enrich.py              # full run
  python3 pipelines/film/mdblist_enrich.py --parse-only # rebuild the CSV from the cache
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.mdblist.com/imdb/movie"
BATCH = 200
# Every tier allows 1,000 reads per 5 minutes; stay well under it.
MIN_INTERVAL = 0.4
# Cloudflare in front of the API rejects urllib's default User-Agent (error 1010).
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"
SOURCES = ("letterboxd", "imdb", "tmdb", "trakt")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CANDIDATES = os.path.join(ROOT, "data", "interim", "film_candidates.csv")
CACHE = os.path.join(ROOT, "data", "raw", "mdblist", "media_batch.jsonl")
OUT_PATH = os.path.join(ROOT, "data", "interim", "film_ratings.csv")


def post_batch(key, ids):
    body = json.dumps({"ids": ids, "append_to_response": ["ratings"]}).encode()
    req = urllib.request.Request(f"{API}?apikey={key}", data=body, headers={"Content-Type": "application/json", "User-Agent": UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                remaining = r.headers.get("X-RateLimit-Remaining")
                return json.load(r), remaining
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = int(e.headers.get("Retry-After", "60"))
                if wait > 600:
                    sys.exit(f"daily limit reached; resets in {wait}s. Re-run later to resume.")
                time.sleep(wait)
            elif e.code >= 500:
                time.sleep(2 ** attempt)
            else:
                sys.exit(f"HTTP {e.code}: {e.read()[:300]!r}")
        except urllib.error.URLError:
            time.sleep(2 ** attempt)
    sys.exit("giving up after repeated network errors")


def items_of(payload):
    """The batch response is a list of media objects; tolerate a wrapping dict."""
    if isinstance(payload, list):
        return payload
    for k in ("items", "results", "data"):
        if isinstance(payload, dict) and isinstance(payload.get(k), list):
            return payload[k]
    return []


def imdb_id_of(item):
    ids = item.get("ids") or {}
    return ids.get("imdb") or item.get("imdbid") or item.get("imdb_id")


def done_ids():
    seen = set()
    if os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as f:
            for line in f:
                seen.update(json.loads(line)["requested"])
    return seen


def fetch(key, probe):
    with open(CANDIDATES, encoding="utf-8") as f:
        ids = [row["tconst"] for row in csv.DictReader(f)]
    if probe:
        payload, remaining = post_batch(key, ids[:5])
        print(json.dumps(payload, indent=1)[:4000])
        print(f"X-RateLimit-Remaining: {remaining}")
        return

    seen = done_ids()
    todo = [i for i in ids if i not in seen]
    print(f"{len(ids)} candidates, {len(seen)} cached, {len(todo)} to fetch ({-(-len(todo) // BATCH)} requests)")
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "a", encoding="utf-8") as cache:
        for start in range(0, len(todo), BATCH):
            chunk = todo[start:start + BATCH]
            t0 = time.time()
            payload, remaining = post_batch(key, chunk)
            cache.write(json.dumps({"requested": chunk, "response": payload}) + "\n")
            cache.flush()
            print(f"  {start + len(chunk)}/{len(todo)}  remaining today: {remaining}")
            time.sleep(max(0, MIN_INTERVAL - (time.time() - t0)))


def parse():
    # IMDb genres come from the candidate file. MDBList's genres are mostly TMDB's
    # plus a few of its own (e.g. "Sci-Fi" next to "Science Fiction", "Anime: Seinen").
    # Both feed the later genre -> cluster organisation, so keep both raw.
    with open(CANDIDATES, encoding="utf-8") as f:
        imdb = {row["tconst"]: row for row in csv.DictReader(f)}
    films = {}
    with open(CACHE, encoding="utf-8") as f:
        for line in f:
            for item in items_of(json.loads(line)["response"]):
                tconst = imdb_id_of(item)
                if not tconst:
                    continue
                cand = imdb.get(tconst, {})
                row = {
                    "tconst": tconst,
                    "tmdb_id": (item.get("ids") or {}).get("tmdb"),
                    "mdblist_title": item.get("title"),
                    "year": item.get("year"),
                    "imdb_title_type": cand.get("title_type"),
                    "runtime": item.get("runtime"),
                    "country": (item.get("country") or "").upper(),
                    "language": item.get("language"),
                    "imdb_genres": (cand.get("genres") or "").replace(",", "|").replace("\\N", ""),
                    "mdblist_genres": "|".join(g["title"] for g in item.get("genres") or [] if g.get("title")),
                }
                for r in item.get("ratings") or []:
                    if r.get("source") in SOURCES:
                        row[f"{r['source']}_value"] = r.get("value")
                        row[f"{r['source']}_votes"] = r.get("votes")
                films[tconst] = row
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
        key = os.environ.get("MDBLIST_API_KEY")
        if not key:
            sys.exit("MDBLIST_API_KEY is not set")
        fetch(key, args.probe)
        if args.probe:
            return
    parse()


if __name__ == "__main__":
    main()
