"""Match the Asian TV-award rows to MyDramaList dramas (sourcing-plan.md §3, §5, §8).

About 460 award winners have no IMDb ID, mostly Chinese, Taiwanese and older
Korean titles. The Asian-drama database admits award winners (§8), so this
gives every Asian award row an MDL ID where one can be found.

Rows taken from data/interim/tv_awards.csv:
  - every row of Baeksang, Golden Eagle, Flying Apsaras, Magnolia, Golden Bell
    and the Asian Television Awards;
  - rows of the other awards whose country is East or Southeast Asian.

Matching, first hit wins:
  1. wikidata  the row's QID carries MyDramaList ID P3868 (one SPARQL query,
               cached), or the QID / IMDb ID is linked to an MDL ID in
               data/interim/asian_drama_candidates.csv;
  2. title     normalised title equals the MDL English title, native title or
               an "Also Known As" title of a cached MDL title page (the 5,000
               ranked dramas plus any other cached page), country compatible,
               award year - MDL year within +-1 ("title"), or 2..3 for
               late or biennial ceremonies ("title_loose");
  3. search    MDL search (adv=titles) for the award title; a drama result is
               accepted when its listed title, or the native/AKA titles of its
               title page, match under the same country and year rules
               ("search" / "search_loose"). Polite: one request at a time,
               >= 1.5 s apart, identifying User-Agent, stop on 403/429/challenge,
               all pages cached in data/raw/mdl/, at most --max-requests new
               requests (winners are searched before nominees).
Matched titles outside the ranking get watchers, native title, country, type
and year from their title page.

Output: data/interim/asian_drama_awards.csv (one row per award row)
  award, category, year, won, title, qid, tconst, country, mdl_id, match,
  mdl_title, native_title, mdl_country, mdl_type, mdl_year, watchers, in_ranking

Usage:
  python3 pipelines/asian_drama/match_awards.py [--max-requests 500] [--offline] [--delay 1.5]
"""
import argparse
import collections
import csv
import gzip
import json
import os
import re
import sys
import unicodedata
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "asian_drama"))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "visual_art"))
import mdl_fetch  # noqa: E402
from mdl_fetch import Blocked, Missing, parse_details, parse_listing, parse_title  # noqa: E402

RAW = mdl_fetch.RAW
AWARDS = os.path.join(ROOT, "data", "interim", "tv_awards.csv")
MDL = os.path.join(ROOT, "data", "interim", "asian_drama_mdl.csv")
CANDIDATES = os.path.join(ROOT, "data", "interim", "asian_drama_candidates.csv")
OUT = os.path.join(ROOT, "data", "interim", "asian_drama_awards.csv")
P3868_CACHE = os.path.join(RAW, "wikidata_p3868.json")

ASIAN_AWARDS = {"Baeksang Arts Awards", "Golden Eagle (China)", "Flying Apsaras", "Magnolia",
                "Golden Bell", "Asian Television Awards"}
ASIAN_COUNTRIES = {"KR", "JP", "CN", "TW", "HK", "MO", "TH", "PH", "SG", "MY", "ID", "VN"}
CHINESE = {"CN", "TW", "HK", "MO", "SG"}  # co-productions and cross-strait credits are common
# Country assumed when an award row has none (Magnolia lists mainland series; it has no fallback).
AWARD_COUNTRY = {"Magnolia": "CN", "Golden Eagle (China)": "CN", "Flying Apsaras": "CN",
                 "Golden Bell": "TW", "Baeksang Arts Awards": "KR"}


def mdl_num(mdl_id):
    m = re.match(r"(\d+)", mdl_id or "")
    return m.group(1) if m else ""


def norm(s):
    """Lower-case, width-folded, punctuation- and space-free key; drops a trailing year."""
    s = unicodedata.normalize("NFKC", s or "").lower()
    s = re.sub(r"\(\s*\d{4}\s*\)$", "", s.strip())
    s = re.sub(r"^the\s+", "", s)
    s = s.replace("&", "and")
    return re.sub(r"[\W_]+", "", s)


def keys_of(*titles):
    """Normalised keys of titles, also of the parts of 'A - B' / 'A: B' native titles."""
    out = set()
    for t in titles:
        if not t:
            continue
        out.add(norm(t))
        for part in re.split(r"\s+[-–:]\s+|：", t):
            if len(norm(part)) >= 2 and part != t:
                out.add(norm(part))
    out.discard("")
    return out


def country_ok(award_c, mdl_c):
    if not award_c or not mdl_c:
        return True
    if award_c == mdl_c:
        return True
    return award_c in CHINESE and mdl_c in CHINESE


def year_class(award_year, mdl_year):
    """'strict' (|diff| <= 1), 'loose' (award 2-3 years after airing) or None."""
    try:
        d = int(award_year) - int(mdl_year)
    except (TypeError, ValueError):
        return None
    if -1 <= d <= 1:
        return "strict"
    if 2 <= d <= 3:
        return "loose"
    return None


def cache_path(path):
    return os.path.join(RAW, re.sub(r"[^\w.-]", "_", path.strip("/")) + ".html.gz")


def read_cached(path):
    with gzip.open(cache_path(path), "rt", encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------- MDL index

def load_index():
    """mdl number -> info for every cached title page, with the ranking's listing fields."""
    ranked = {}
    with open(MDL, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ranked[mdl_num(r["mdl_id"])] = r
    index = {}
    for fn in os.listdir(RAW):
        m = re.match(r"(\d+)(?:-.*)?\.html\.gz$", fn)
        if not m:
            continue
        with gzip.open(os.path.join(RAW, fn), "rt", encoding="utf-8") as f:
            page = f.read()
        index[m.group(1)] = make_info(fn[:-len(".html.gz")], page, ranked.get(m.group(1)))
    return index, ranked


def make_info(slug, page, rank_row=None):
    d = parse_details(page)
    t = parse_title(page)
    page_type = {"TV Program": "TV Show"}.get(d["type"], d["type"])
    info = {
        "mdl_id": rank_row["mdl_id"] if rank_row else slug,
        "mdl_title": (rank_row or {}).get("title") or d["title"],
        "native_title": d["native_title"], "aka": d["aka"],
        "mdl_country": mdl_fetch.COUNTRY_CODES.get((rank_row or {}).get("country", ""), "") or d["country"],
        "mdl_type": (rank_row or {}).get("type") or page_type,
        "mdl_year": (rank_row or {}).get("year") or d["year"],
        "watchers": (rank_row or {}).get("watchers") or t["watchers"] or "",
        "in_ranking": "1" if rank_row else "0",
    }
    info["keys"] = keys_of(info["mdl_title"], d["title"], d["native_title"], *d["aka"])
    return info


def by_key(index):
    k = collections.defaultdict(list)
    for num, info in index.items():
        for key in info["keys"]:
            k[key].append(num)
    return k


def pick(row, nums, index, require_drama=True):
    """Best MDL candidate for an award row among nums: (num, 'strict'|'loose') or None."""
    best = None
    for num in set(nums):
        info = index[num]
        if require_drama and info["mdl_type"] not in ("Drama", ""):
            continue
        if not country_ok(row["_country"], info["mdl_country"]):
            continue
        yc = year_class(row["year"], info["mdl_year"])
        if not yc:
            continue
        try:
            dist = abs(int(row["year"]) - int(info["mdl_year"]))
        except ValueError:
            dist = 9
        score = (yc == "strict", -dist, int(info["watchers"] or 0))
        if best is None or score > best[0]:
            best = (score, num, yc)
    return (best[1], best[2]) if best else None


# ---------------------------------------------------------------- Wikidata

def wikidata_links(offline):
    """QID -> MDL number from P3868 (cached query) and the candidates cross-reference; tconst -> MDL number."""
    qid_map, tconst_map = {}, {}
    if os.path.exists(CANDIDATES):
        with open(CANDIDATES, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                n = mdl_num(r["mdl_id"])
                if n:
                    if r["wikidata"]:
                        qid_map.setdefault(r["wikidata"], r["mdl_id"])
                    if r["tconst"]:
                        tconst_map.setdefault(r["tconst"], r["mdl_id"])
    rows = None
    if os.path.exists(P3868_CACHE):
        with open(P3868_CACHE, encoding="utf-8") as f:
            rows = json.load(f)
    elif not offline:
        from wikidata import sparql
        rows = sparql("SELECT ?x ?mdl WHERE { ?x wdt:P3868 ?mdl }")
        with open(P3868_CACHE, "w", encoding="utf-8") as f:
            json.dump(rows, f)
    for r in rows or []:
        if mdl_num(r["mdl"]):
            qid_map.setdefault(r["x"], r["mdl"])
    return qid_map, tconst_map


# ---------------------------------------------------------------- search

class Budget:
    def __init__(self, n):
        self.left = n
        self.used = 0


def fetch(path, budget, offline):
    """Page from cache, else one polite request if the budget allows; None when unavailable."""
    if os.path.exists(cache_path(path)):
        return read_cached(path)
    if offline or budget.left <= 0:
        return None
    budget.left -= 1
    budget.used += 1
    return mdl_fetch.get(path)  # raises Blocked / Missing


def search(row, index, keymap, budget, offline):
    """MDL search for one award row; returns (num, 'search'|'search_loose') or None."""
    q = row["title"]
    path = "/search?" + urllib.parse.urlencode({"q": q, "adv": "titles"})
    page = fetch(path, budget, offline)
    if page is None:
        return "skipped"
    key = norm(q)
    hits = [e for e in parse_listing(page)
            if e["type"] in ("Drama", "") and country_ok(row["_country"], mdl_fetch.COUNTRY_CODES.get(e["country"], ""))
            and (not e["year"] or year_class(row["year"], e["year"]))]
    # listed English title equals the award title: accept; otherwise verify on the title page
    hits.sort(key=lambda e: (norm(e["title"]) != key, abs(int(row["year"]) - int(e["year"] or 0))))
    for e in hits[:3]:
        num = mdl_num(e["mdl_id"])
        if num not in index:
            if norm(e["title"]) != key and len(hits) > 1 and e is not hits[0]:
                continue  # spend title-page requests only on the best candidate unless titles match
            try:
                tp = fetch("/" + e["mdl_id"], budget, offline)
            except Missing:
                continue
            if tp is None:
                continue
            index[num] = make_info(e["mdl_id"], tp)
            for k in index[num]["keys"]:
                keymap[k].append(num)
        info = index[num]
        if key in info["keys"] or norm(e["title"]) == key:
            yc = year_class(row["year"], info["mdl_year"] or e["year"])
            if yc:
                return num, "search" if yc == "strict" else "search_loose"
    return None


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-requests", type=int, default=500, help="new MDL requests allowed (search + title pages)")
    ap.add_argument("--offline", action="store_true", help="cached pages only, no MDL or Wikidata requests")
    ap.add_argument("--delay", type=float, default=mdl_fetch.DELAY,
                    help=f"seconds between MDL requests (min {mdl_fetch.DELAY})")
    args = ap.parse_args()
    mdl_fetch._delay[0] = max(mdl_fetch.DELAY, args.delay)

    with open(AWARDS, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f)
                if r["award"] in ASIAN_AWARDS or r["country"] in ASIAN_COUNTRIES]
    for r in rows:
        r["_country"] = r["country"] if r["country"] in ASIAN_COUNTRIES else (
            "" if r["country"] else AWARD_COUNTRY.get(r["award"], ""))
    print(f"Asian award rows: {len(rows)} ({sum(r['won'] == '1' for r in rows)} winners)")

    index, ranked = load_index()
    keymap = by_key(index)
    print(f"MDL title pages indexed: {len(index)} ({len(ranked)} in the ranking)")
    qid_map, tconst_map = wikidata_links(args.offline)
    print(f"Wikidata/candidate MDL links: {len(qid_map)} QIDs, {len(tconst_map)} IMDb IDs")

    for r in rows:
        r["mdl_num"], r["match"] = "", "none"
        r["_slug"] = qid_map.get(r["qid"]) or tconst_map.get(r["tconst"])
        if r["_slug"]:
            r["mdl_num"], r["match"] = mdl_num(r["_slug"]), "wikidata"
            continue
        hit = pick(r, keymap.get(norm(r["title"]), []), index)
        if hit:
            r["mdl_num"], r["match"] = hit[0], "title" if hit[1] == "strict" else "title_loose"
    print("offline pass:", dict(collections.Counter(r["match"] for r in rows)))

    budget = Budget(0 if args.offline else args.max_requests)
    todo = [r for r in rows if r["match"] == "none"]
    todo.sort(key=lambda r: r["won"] != "1")  # winners first
    seen = {}
    try:
        for i, r in enumerate(todo, 1):
            sk = (norm(r["title"]), r["year"], r["_country"])
            if sk not in seen:
                seen[sk] = search(r, index, keymap, budget, args.offline)
            hit = seen[sk]
            if hit and hit != "skipped":
                r["mdl_num"], r["match"] = hit
            if i % 50 == 0:
                print(f"  searched {i}/{len(todo)}, new requests {budget.used}")
    except Blocked as e:
        print(f"stopped searching: {e}. Cached pages are kept; re-run to resume.")
    print(f"new MDL requests: {budget.used}")

    # fetch title pages for Wikidata-linked dramas that are not cached (watchers, native title)
    try:
        for r in rows:
            n = r["mdl_num"]
            if n and n not in index:
                try:
                    page = fetch("/" + r["_slug"], budget, args.offline)
                except Missing:
                    page = None
                if page:
                    index[n] = make_info(r["_slug"], page)
    except Blocked as e:
        print(f"stopped fetching title pages: {e}")

    cols = ["award", "category", "year", "won", "title", "qid", "tconst", "country", "mdl_id", "match",
            "mdl_title", "native_title", "mdl_country", "mdl_type", "mdl_year", "watchers", "in_ranking"]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            info = index.get(r["mdl_num"]) or {}
            out = dict(r)
            out.update({k: v for k, v in info.items() if k in cols})
            if r["mdl_num"] and not info:
                out["mdl_id"] = r["mdl_num"]
            w.writerow(out)

    # report
    won = [r for r in rows if r["won"] == "1"]
    print("\nwinners matched by award:")
    for a in sorted({r["award"] for r in won}):
        sub = [r for r in won if r["award"] == a]
        print(f"  {a:28s} {sum(bool(r['mdl_num']) for r in sub):4d} / {len(sub)}")
    print("winners matched by country:")
    for c in sorted({r["_country"] for r in won}):
        sub = [r for r in won if r["_country"] == c]
        print(f"  {c or '?':4s} {sum(bool(r['mdl_num']) for r in sub):4d} / {len(sub)}")
    print("all rows by match:", dict(collections.Counter(r["match"] for r in rows)))
    print("winners by match:", dict(collections.Counter(r["match"] for r in won)))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    sys.exit(main())
