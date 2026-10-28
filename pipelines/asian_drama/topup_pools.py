"""Per-country MDL popularity pools for the Asian-drama top-up (sourcing-plan.md §8).

The top-5,000 popularity ranking (mdl_fetch.py) ends at ~2,850 watchers, so
almost every country x decade cell inside it is already above the 5,000-watcher
bar and a top-up taken from it adds nothing. Under-counted industries need
their own pools. MDL's advanced search lists dramas filtered by country and
release-year range, sorted by popularity, with a result total:

  /search?adv=titles&ty=68&co=<country>&re=<from>,<to>&so=popular&page=<n>

The top-up is defined operationally (decided 2026-10-28) as: per country x
decade, the top max(--topup-min, --topup-share x result total) entries by MDL
popularity. Listing entries of type Special count toward the total and the
rank but are not picked (select.py keeps Drama only). Title pages are fetched
only for picks not already cached (for watchers, year and native title).

Cells: Japanese, Taiwanese, Hong Kong and Filipino dramas for every decade
from the 1960s; Korean and Chinese dramas before the 2010s.

Polite rules as mdl_fetch.py (one request at a time, --delay seconds apart, floor 1 s,
identifying User-Agent, stop on 403/429/challenge, everything cached in
data/raw/mdl/), with at most --max-requests new requests.

Output: data/interim/asian_drama_mdl_pools.csv
  country, decade, result_total, quota, pool_rank, pick, mdl_id, title, type, year,
  native_title, watchers

Usage:
  python3 pipelines/asian_drama/topup_pools.py [--max-requests 1000] [--offline]
"""
import argparse
import collections
import csv
import gzip
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "asian_drama"))
import mdl_fetch  # noqa: E402
from mdl_fetch import Blocked, Missing, parse_details, parse_listing, parse_title  # noqa: E402

RAW = mdl_fetch.RAW
OUT = os.path.join(ROOT, "data", "interim", "asian_drama_mdl_pools.csv")
MDL_COUNTRY = {"JP": 1, "CN": 2, "KR": 3, "HK": 4, "TW": 5, "PH": 140}
DECADES = {c: [1960, 1970, 1980, 1990, 2000, 2010, 2020] for c in ("JP", "TW", "HK", "PH")}
DECADES.update({c: [1960, 1970, 1980, 1990, 2000] for c in ("KR", "CN")})
PER_PAGE = 20


def listing_path(country, decade, page):
    return (f"/search?adv=titles&ty=68&co={MDL_COUNTRY[country]}&re={decade},{decade + 9}"
            f"&so=popular&page={page}")


def cache_path(path):
    return os.path.join(RAW, re.sub(r"[^\w.-]", "_", path.strip("/")) + ".html.gz")


class Budget:
    def __init__(self, n, offline):
        self.left, self.used, self.offline = n, 0, offline

    def get(self, path):
        """Cached page, else one polite request while the budget lasts; None when not allowed."""
        cp = cache_path(path)
        if os.path.exists(cp):
            with gzip.open(cp, "rt", encoding="utf-8") as f:
                return f.read()
        if self.offline or self.left <= 0:
            return None
        self.left -= 1
        self.used += 1
        return mdl_fetch.get(path)


def result_total(page):
    m = re.search(r"([\d,]+)\s+results", page)
    return int(m.group(1).replace(",", "")) if m else 0


def cached_title_page(mdl_id):
    num = re.match(r"\d+", mdl_id).group(0)
    for fn in (mdl_id, num):
        p = os.path.join(RAW, re.sub(r"[^\w.-]", "_", fn) + ".html.gz")
        if os.path.exists(p):
            return p
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-requests", type=int, default=1000)
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--topup-share", type=float, default=0.15)
    ap.add_argument("--topup-min", type=int, default=5)
    ap.add_argument("--delay", type=float, default=mdl_fetch.DELAY)
    args = ap.parse_args()
    mdl_fetch._delay[0] = max(mdl_fetch.MIN_DELAY, args.delay)
    b = Budget(args.max_requests, args.offline)
    cells = [(c, d) for c in MDL_COUNTRY for d in DECADES[c]]
    rows = []
    try:
        # 1. first page of every cell: result total -> quota
        first = {}
        for c, d in cells:
            page = b.get(listing_path(c, d, 1))
            if page is not None:
                first[(c, d)] = page
        quota = {}
        for cell, page in first.items():
            n = result_total(page)
            quota[cell] = (n, min(n, max(args.topup_min, math.ceil(args.topup_share * n))))
        need = sum(math.ceil(q / PER_PAGE) for _, q in quota.values())
        print(f"cells: {len(first)}/{len(cells)}; listing pages needed: {need}; requests so far: {b.used}")
        # 2. walk each cell's listing until its quota of Drama entries is reached
        #    (smallest cells first, so a short budget still finishes whole cells)
        for cell in sorted(quota, key=lambda k: quota[k][1]):
            c, d = cell
            n, q = quota[cell]
            entries, page_no, page = [], 1, first[cell]
            while page is not None:
                got = parse_listing(page)
                entries += [e for e in got if e["year"] and d <= int(e["year"]) <= d + 9]
                if sum(e["type"] == "Drama" for e in entries) >= q or len(got) < PER_PAGE:
                    break
                page_no += 1
                page = b.get(listing_path(c, d, page_no))
            dramas = 0
            for rank, e in enumerate(entries, 1):
                pick = e["type"] == "Drama" and dramas < q
                dramas += e["type"] == "Drama"
                rows.append({"country": c, "decade": d, "result_total": n, "quota": q, "pool_rank": rank,
                             "pick": int(pick), **{k: e[k] for k in ("mdl_id", "title", "type", "year")}})
            print(f"  {c} {d}s: {n:5d} titles, quota {q:4d}, listed {len(entries):4d}, "
                  f"pages {page_no}{'' if page is not None else ' (budget out)'}")
        # 3. title pages of picks (watchers, native title, year)
        picks = [r for r in rows if r["pick"]]
        picks.sort(key=lambda r: r["pool_rank"])
        for r in picks:
            p = cached_title_page(r["mdl_id"])
            page = None
            if p:
                with gzip.open(p, "rt", encoding="utf-8") as f:
                    page = f.read()
            else:
                try:
                    page = b.get("/" + r["mdl_id"])
                except Missing:
                    page = None
            if page:
                r["native_title"] = parse_details(page)["native_title"]
                r["watchers"] = parse_title(page)["watchers"] or ""
    except Blocked as e:
        print(f"stopped: {e}. Cached pages are kept; re-run to resume.")

    cols = ["country", "decade", "result_total", "quota", "pool_rank", "pick", "mdl_id", "title", "type",
            "year", "native_title", "watchers"]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    picks = [r for r in rows if r["pick"]]
    print(f"new MDL requests: {b.used}; picks: {len(picks)} "
          f"({sum(bool(r.get('watchers')) for r in picks)} with watchers)")
    print("picks by country:", dict(collections.Counter(r["country"] for r in picks)))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    sys.exit(main())
