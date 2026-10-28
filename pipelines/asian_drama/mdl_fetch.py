"""Polite MyDramaList fetcher: watchers, rating and rating count per drama.

Rules (sourcing-plan.md §5, decided 2026-10-27):
  - one request at a time, DELAY seconds apart (--delay, floor MIN_DELAY), identifying User-Agent;
  - on HTTP 403/429 or a Cloudflare challenge page: stop (a 404, or a 5xx that
    repeats once, only skips that title). Never work around it
    (no proxies, no headless browsers). Re-run later; everything is cached;
  - fetch only candidates' title pages (plus one search page for a candidate
    with no known MDL ID); store only ID, watchers, score, rating count, episodes;
  - refresh at most quarterly; counts stay internal and are never used to
    train models (MDL's robots.txt content signal: ai-train=no).

MDL serves a Cloudflare challenge to datacenter IPs, so this has to run from an
ordinary connection. The page parser matches MDL's label text ("Watchers:",
"Episodes:", "scored by N users"); run --probe first and check its output, as
it could not be tested against live pages where it was written.

Input:  data/interim/asian_drama_candidates.csv
Output: data/interim/asian_drama_mdl.csv; raw pages cached in data/raw/mdl/

Usage:
  python3 pipelines/asian_drama/mdl_fetch.py --probe        # 3 titles, prints parsed fields
  python3 pipelines/asian_drama/mdl_fetch.py [--limit N]    # most-voted candidates first
"""
import argparse
import csv
import gzip
import html
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://mydramalist.com"
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"
DELAY = 1.5
MIN_DELAY = 1.0  # floor: one connection, never faster than 1 request/second

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CANDIDATES = os.path.join(ROOT, "data", "interim", "asian_drama_candidates.csv")
RAW = os.path.join(ROOT, "data", "raw", "mdl")
OUT_PATH = os.path.join(ROOT, "data", "interim", "asian_drama_mdl.csv")


class Blocked(Exception):
    pass


_last = [0.0]
_delay = [DELAY]


class Missing(Exception):
    """This one page is unavailable (404, or a 5xx twice); skip the title, keep going."""


def get(path, retry=True):
    """Cached, rate-limited GET; raises Blocked on a refusal, Missing on a dead page."""
    cache = os.path.join(RAW, re.sub(r"[^\w.-]", "_", path.strip("/")) + ".html.gz")
    if os.path.exists(cache):
        with gzip.open(cache, "rt", encoding="utf-8") as f:
            return f.read()
    time.sleep(max(0.0, _delay[0] - (time.time() - _last[0])))
    req = urllib.request.Request(BASE + path, headers={"User-Agent": UA, "Accept-Language": "en"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            page = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            raise Blocked(f"HTTP {e.code} for {path}")
        if e.code >= 500 and retry:
            time.sleep(10)
            _last[0] = time.time()
            return get(path, retry=False)
        raise Missing(f"HTTP {e.code} for {path}")
    finally:
        _last[0] = time.time()
    if "challenges.cloudflare.com" in page or "<title>Just a moment" in page:
        raise Blocked(f"Cloudflare challenge for {path}")
    with gzip.open(cache, "wt", encoding="utf-8") as f:
        f.write(page)
    return page


def text_of(page):
    return html.unescape(re.sub(r"<[^>]+>", " ", page))


def number_after(label, text):
    m = re.search(re.escape(label) + r"\s*([\d,]+)", text)
    return int(m.group(1).replace(",", "")) if m else None


def parse_title(page):
    t = " ".join(text_of(page).split())
    score = re.search(r"Score:\s*([\d.]+)\s*\(scored by\s*([\d,]+)\s*users?\)", t)
    return {
        "watchers": number_after("Watchers:", t),
        "episodes_mdl": number_after("Episodes:", t),
        "score": float(score.group(1)) if score else None,
        "rating_count": int(score.group(2).replace(",", "")) if score else None,
        "mdl_title": (re.search(r'<meta property="og:title" content="([^"]+)"', page) or [None, None])[1],
    }


def resolve(title, year):
    """MDL ID from MDL's search: the first drama result whose year matches."""
    page = get("/search?" + urllib.parse.urlencode({"q": title, "adv": "titles"}))
    for m in re.finditer(r'href="/(\d+-[a-z0-9-]+)"[^>]*>(.*?)</a>(.{0,400})', page, re.S):
        slug, _, tail = m.groups()
        years = re.findall(r"\b(19\d\d|20\d\d)\b", text_of(tail))
        if not year or not years or str(year) in years:
            return slug
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--delay", type=float, default=DELAY, help=f"seconds between requests (min {MIN_DELAY})")
    args = ap.parse_args()
    _delay[0] = max(MIN_DELAY, args.delay)
    os.makedirs(RAW, exist_ok=True)
    with open(CANDIDATES, encoding="utf-8") as f:
        cands = sorted(csv.DictReader(f), key=lambda r: -int(float(r["imdb_votes"] or 0)))
    if args.probe:
        cands = [c for c in cands if c["mdl_id"]][:3]
    elif args.limit:
        cands = cands[:args.limit]

    done = {}
    if os.path.exists(OUT_PATH) and not args.probe:
        with open(OUT_PATH, encoding="utf-8") as f:
            done = {r["key"]: r for r in csv.DictReader(f)}
    cols = ["key", "tconst", "mdl_id", "mdl_title", "watchers", "score", "rating_count", "episodes_mdl", "error"]
    try:
        for i, c in enumerate(cands, 1):
            if c["key"] in done:
                continue
            row = {"key": c["key"], "tconst": c["tconst"], "mdl_id": c["mdl_id"]}
            try:
                slug = c["mdl_id"] or resolve(c["title"], c["year"])
                row["mdl_id"] = slug or ""
                if slug:
                    # Wikidata stores either "12345" or "12345-slug"; both resolve on MDL.
                    row.update(parse_title(get("/" + slug)))
            except Missing as e:
                row["error"] = str(e)
            done[c["key"]] = row
            if args.probe:
                print(c["title"], row)
            elif i % 50 == 0:
                print(f"  {i}/{len(cands)}")
    except Blocked as e:
        print(f"stopped: {e}. Everything fetched so far is cached; re-run later from an ordinary connection.")
    if not args.probe:
        with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(done.values())
        print(f"{len(done)} candidates processed; wrote {OUT_PATH}")


if __name__ == "__main__":
    sys.exit(main())
