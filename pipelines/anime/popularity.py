"""Audience size per anime: MyAnimeList members (primary) and AniList popularity (cross-check).

MAL members (decided metric, sourcing-plan.md §4) come from MAL's public
"most popular" ranking pages (myanimelist.net/topanime.php?type=bypopularity),
50 titles per page with member counts, walked from the top until a whole page
falls below --min-members. Rules as for MyDramaList: one request at a time,
DELAY seconds apart, identifying User-Agent; stop on 403/429 or a challenge page;
pages cached; counts stay internal and are never used to train models.
robots.txt allows these pages for general crawlers. (Jikan, the unofficial MAL
API, was unreachable from the cloud environment; the official MAL API needs a
client ID, set MAL_CLIENT_ID to use it instead in future.)

AniList `popularity` (users with the title on their list) comes from AniList's
free GraphQL API, 50 titles per query, by AniList ID or, for entries with only a
MAL ID, by MAL ID. It also supplies favourites, mean score, country of origin
(CN = donghua), genres, top tags and main studio.

Input:  data/interim/anime_candidates.csv
Output: data/interim/anime_popularity.csv (one row per candidate)

Usage: python3 pipelines/anime/popularity.py [--min-members 1000] [--no-anilist]
"""
import argparse
import csv
import gzip
import html
import json
import os
import re
import time
import urllib.error
import urllib.request

ANILIST = "https://graphql.anilist.co"
MAL_RANKING = "https://myanimelist.net/topanime.php?type=bypopularity&limit={offset}"
DELAY = 2.0
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"
QUERY = """query ($ids: [Int], $mal: [Int]) { Page(page: 1, perPage: 50) {
  media(id_in: $ids, idMal_in: $mal, type: ANIME) {
    id idMal popularity favourites meanScore format countryOfOrigin isAdult genres
    tags { name rank } studios(isMain: true) { nodes { name } } } } }"""

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CANDIDATES = os.path.join(ROOT, "data", "interim", "anime_candidates.csv")
RAW = os.path.join(ROOT, "data", "raw", "anime")
OUT_PATH = os.path.join(ROOT, "data", "interim", "anime_popularity.csv")


def post(query, variables):
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(ANILIST, data=body, headers={
        "Content-Type": "application/json", "Accept": "application/json", "User-Agent": UA})
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                remaining = int(r.headers.get("X-RateLimit-Remaining") or 30)
                return json.load(r), remaining
        except urllib.error.HTTPError as e:
            wait = int(e.headers.get("Retry-After") or 0) or 5 * 2 ** attempt
            print(f"    AniList HTTP {e.code}, waiting {wait}s")
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"    AniList {e}, retrying")
            time.sleep(5 * 2 ** attempt)
    raise RuntimeError("AniList requests keep failing")


def anilist_all(rows):
    cache_path = os.path.join(RAW, "anilist_media.jsonl")
    done_al, done_mal = set(), set()
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                done_al.update(rec["requested"].get("ids") or [])
                done_mal.update(rec["requested"].get("mal") or [])
    by_al = sorted({int(r["anilist_id"]) for r in rows if r["anilist_id"]} - done_al)
    by_mal = sorted({int(r["mal_id"]) for r in rows if r["mal_id"] and not r["anilist_id"]} - done_mal)
    batches = [{"ids": by_al[i:i + 50]} for i in range(0, len(by_al), 50)] + \
              [{"mal": by_mal[i:i + 50]} for i in range(0, len(by_mal), 50)]
    print(f"AniList: {len(batches)} queries to run ({len(by_al)} by AniList ID, {len(by_mal)} by MAL ID)")
    with open(cache_path, "a", encoding="utf-8") as cache:
        for n, variables in enumerate(batches, 1):
            data, remaining = post(QUERY, variables)
            media = ((data.get("data") or {}).get("Page") or {}).get("media") or []
            cache.write(json.dumps({"requested": variables, "media": media}) + "\n")
            cache.flush()
            if n % 25 == 0:
                print(f"  {n}/{len(batches)} (rate limit remaining {remaining})")
            time.sleep(0.8 if remaining > 10 else 3)
    media = {}
    with open(cache_path, encoding="utf-8") as f:
        for line in f:
            for m in json.loads(line)["media"]:
                media[m["id"]] = m
    return media


def mal_members(min_members):
    """{mal_id: members} from MAL's popularity ranking, cached page by page."""
    cache_dir = os.path.join(RAW, "mal_ranking")
    os.makedirs(cache_dir, exist_ok=True)
    members, offset, last = {}, 0, 0.0
    while True:
        path = os.path.join(cache_dir, f"bypopularity_{offset:06d}.html.gz")
        if os.path.exists(path):
            with gzip.open(path, "rt", encoding="utf-8") as f:
                page = f.read()
        else:
            time.sleep(max(0.0, DELAY - (time.time() - last)))
            req = urllib.request.Request(MAL_RANKING.format(offset=offset), headers={"User-Agent": UA})
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    page = r.read().decode("utf-8", "replace")
            except urllib.error.HTTPError as e:
                if e.code in (403, 429):
                    print(f"stopped: MAL returned HTTP {e.code} at offset {offset}; re-run later to resume")
                    break
                raise
            finally:
                last = time.time()
            if "_Incapsula_Resource" in page or "challenges.cloudflare.com" in page:
                print(f"stopped: challenge page at offset {offset}; re-run later to resume")
                break
            with gzip.open(path, "wt", encoding="utf-8") as f:
                f.write(page)
        rows = re.findall(r'<tr class="ranking-list">(.*?)</tr>', page, re.S)
        got = {}
        for row in rows:
            mid = re.search(r"/anime/(\d+)/", row)
            mem = re.search(r"([\d,]+) members", " ".join(html.unescape(re.sub(r"<[^>]+>", " ", row)).split()))
            if mid and mem:
                got[int(mid.group(1))] = int(mem.group(1).replace(",", ""))
        members.update(got)
        if offset % 2500 == 0:
            print(f"  MAL ranking offset {offset}: {len(members)} titles, lowest on page {min(got.values()) if got else '-'}")
        if not got or max(got.values()) < min_members:
            break
        offset += 50
    print(f"MAL: {len(members)} titles with member counts")
    return members


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-members", type=int, default=1000, help="stop walking MAL's ranking below this")
    ap.add_argument("--no-anilist", action="store_true")
    args = ap.parse_args()
    os.makedirs(RAW, exist_ok=True)
    with open(CANDIDATES, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    members = mal_members(args.min_members)
    media = {} if args.no_anilist else anilist_all(rows)
    by_mal = {m["idMal"]: m for m in media.values() if m.get("idMal")}

    cols = ["mal_id", "anilist_id", "title", "type", "year", "anilist_popularity", "anilist_favourites",
            "anilist_mean_score", "mal_members", "country_of_origin", "is_adult", "genres", "top_tags", "main_studio"]
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as out:
        w = csv.DictWriter(out, fieldnames=cols)
        w.writeheader()
        for r in rows:
            m = media.get(int(r["anilist_id"])) if r["anilist_id"] else by_mal.get(int(r["mal_id"])) if r["mal_id"] else None
            m = m or {}
            w.writerow({
                "mal_id": r["mal_id"] or m.get("idMal"), "anilist_id": r["anilist_id"] or m.get("id"),
                "title": r["title"], "type": r["type"], "year": r["year"],
                "anilist_popularity": m.get("popularity"), "anilist_favourites": m.get("favourites"),
                "anilist_mean_score": m.get("meanScore"),
                "mal_members": members.get(int(r["mal_id"])) if r["mal_id"] else None,
                "country_of_origin": m.get("countryOfOrigin"), "is_adult": m.get("isAdult"),
                "genres": "|".join(m.get("genres") or []),
                "top_tags": "|".join(t["name"] for t in sorted(m.get("tags") or [], key=lambda t: -t["rank"])[:8]),
                "main_studio": "|".join(s["name"] for s in ((m.get("studios") or {}).get("nodes") or [])),
            })
    print(f"{len(rows)} candidates; {sum(1 for r in rows if r['mal_id'] and int(r['mal_id']) in members)} with MAL members, "
          f"{len(media)} found on AniList")
    for th in (5_000, 10_000, 25_000, 50_000, 100_000):
        print(f"  MAL members >= {th:>7,}: {sum(v >= th for v in members.values()):,}")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
