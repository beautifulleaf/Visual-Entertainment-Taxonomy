"""MDBList Media Info Batch client shared by the film and TV pipelines.

POSTs IMDb IDs in batches of 200 and caches every raw response (one JSON object
per line: {"requested": [...], "response": [...]}), so an interrupted run
resumes where it stopped. Requires the MDBLIST_API_KEY environment variable.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.mdblist.com/imdb/{kind}"  # kind: movie | show
BATCH = 200
# Every tier allows 1,000 reads per 5 minutes; stay well under it.
MIN_INTERVAL = 0.4
# Cloudflare in front of the API rejects urllib's default User-Agent (error 1010).
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"


def api_key():
    key = os.environ.get("MDBLIST_API_KEY")
    if not key:
        sys.exit("MDBLIST_API_KEY is not set")
    return key


def post_batch(key, ids, kind):
    body = json.dumps({"ids": ids, "append_to_response": ["ratings"]}).encode()
    req = urllib.request.Request(f"{API.format(kind=kind)}?apikey={key}", data=body,
                                 headers={"Content-Type": "application/json", "User-Agent": UA})
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


def probe(key, ids, kind):
    payload, remaining = post_batch(key, ids[:5], kind)
    print(json.dumps(payload, indent=1)[:4000])
    print(f"X-RateLimit-Remaining: {remaining}")


def fetch_all(key, ids, cache_path, kind):
    seen = set()
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            for line in f:
                seen.update(json.loads(line)["requested"])
    todo = [i for i in ids if i not in seen]
    print(f"{len(ids)} candidates, {len(seen)} cached, {len(todo)} to fetch ({-(-len(todo) // BATCH)} requests)")
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "a", encoding="utf-8") as cache:
        for start in range(0, len(todo), BATCH):
            chunk = todo[start:start + BATCH]
            t0 = time.time()
            payload, remaining = post_batch(key, chunk, kind)
            cache.write(json.dumps({"requested": chunk, "response": payload}) + "\n")
            cache.flush()
            print(f"  {start + len(chunk)}/{len(todo)}  remaining today: {remaining}")
            time.sleep(max(0, MIN_INTERVAL - (time.time() - t0)))


def cached_items(cache_path):
    """Every media object in the cache (later responses win for repeated IDs)."""
    with open(cache_path, encoding="utf-8") as f:
        for line in f:
            yield from items_of(json.loads(line)["response"])


def base_row(item, cand):
    """Fields shared by film and TV outputs; `cand` is the IMDb candidate row."""
    return {
        "tconst": imdb_id_of(item),
        "tmdb_id": (item.get("ids") or {}).get("tmdb"),
        "mal_id": (item.get("ids") or {}).get("mal"),
        "mdblist_title": item.get("title"),
        "year": item.get("year"),
        "imdb_title_type": cand.get("title_type"),
        "runtime": item.get("runtime"),
        "country": (item.get("country") or "").upper(),
        "language": item.get("language"),
        "imdb_genres": (cand.get("genres") or "").replace(",", "|").replace("\\N", ""),
        "mdblist_genres": "|".join(g["title"] for g in item.get("genres") or [] if g.get("title")),
    }


def add_ratings(row, item, sources):
    for r in item.get("ratings") or []:
        if r.get("source") in sources:
            row[f"{r['source']}_value"] = r.get("value")
            row[f"{r['source']}_votes"] = r.get("votes")
    return row
