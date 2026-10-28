"""MyDramaList popularity ranking with watcher counts (sourcing-plan.md §5).

Like anime (MAL), the Asian-drama candidates come from the platform's own
ranking rather than from IMDb: MDL's "popular shows" list (20 per page, 250
pages, so the top 5,000 by popularity, which MDL derives from watchers) is
walked in order, then each listed drama's title page is fetched for its exact
watchers, score, rating count and episodes, so the cutoff can be set on
watchers. The IMDb/Wikidata candidates (build_candidates.py) become a
cross-reference for IMDb and Wikidata IDs.

Rules (decided 2026-10-27):
  - one request at a time, DELAY seconds apart (--delay, floor MIN_DELAY), identifying User-Agent;
  - on HTTP 403/429 or a Cloudflare challenge page: stop (a 404, or a 5xx that
    repeats once, only skips that title). Never work around a block. Re-run
    later; everything is cached in data/raw/mdl/;
  - store only ID, title, country, type, year, watchers, score, rating count, episodes;
  - refresh at most quarterly; counts stay internal and are never used to
    train models (MDL's robots.txt content signal: ai-train=no).

Output: data/interim/asian_drama_mdl.csv (one row per ranked drama)

Usage:
  python3 pipelines/asian_drama/mdl_fetch.py [--pages 250] [--ranking-only] [--delay 1.0]
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
RAW = os.path.join(ROOT, "data", "raw", "mdl")
OUT_PATH = os.path.join(ROOT, "data", "interim", "asian_drama_mdl.csv")


class Blocked(Exception):
    pass


_last = [0.0]
_delay = [DELAY]
_net_retries = [0]


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
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        # Network drop (not a refusal from MDL): wait and retry a few times.
        if retry is not False and _net_retries[0] < 5:
            _net_retries[0] += 1
            time.sleep(30 * _net_retries[0])
            return get(path, retry=retry)
        raise Blocked(f"network unavailable ({e}) for {path}")
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


COUNTRY_CODES = {"South Korea": "KR", "Korea": "KR", "China": "CN", "Taiwan": "TW", "Japan": "JP",
                 "Hong Kong": "HK", "Thailand": "TH", "Philippines": "PH", "Singapore": "SG",
                 "Malaysia": "MY", "Indonesia": "ID", "Vietnam": "VN", "Macau": "MO",
                 # adjectival forms, as in the ranking and search listings
                 "Korean": "KR", "Chinese": "CN", "Taiwanese": "TW", "Japanese": "JP",
                 "Thai": "TH", "Filipino": "PH", "Singaporean": "SG", "Malaysian": "MY",
                 "Indonesian": "ID", "Vietnamese": "VN"}


def parse_details(page):
    """Identity fields of a title page: native title, also-known-as titles, country, type, year.

    Read from the details box ("Native Title:", "Also Known As:", "Country:",
    "Type:", "Aired:") with the JSON-LD block (alternateName, countryOfOrigin,
    datePublished) as a fallback. Works on every cached page; no requests.
    """
    def field(label):
        m = re.search(r'<b class="inline">' + re.escape(label) + r':</b>(.*?)</li>', page, re.S)
        return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", m.group(1))).split()) if m else ""

    native = field("Native Title")
    aka_m = re.search(r'<span class="mdl-aka-titles">(.*?)</span>', page, re.S)
    akas = [a.strip() for a in html.unescape(aka_m.group(1)).split(" , ")] if aka_m else []
    if not akas:
        alt = re.search(r'"alternateName":\[(.*?)\]', page)
        if alt:
            akas = [html.unescape(a) for a in re.findall(r'"((?:[^"\\]|\\.)*)"', alt.group(1))]
    akas = [" ".join(a.split()).strip(" ,") for a in akas if a.strip(" ,")]
    country = field("Country")
    if not country:
        c = re.search(r'"countryOfOrigin":\{[^}]*"name":"([^"]+)"', page)
        country = c.group(1) if c else ""
    year = re.search(r"(\d{4})", field("Aired") or field("Release Date"))
    if not year:
        year = re.search(r'"datePublished":"(\d{4})', page)
    og = (re.search(r'<meta property="og:title" content="([^"]+)"', page) or [None, ""])[1]
    return {
        "title": re.sub(r"\s*\(\d{4}\)\s*$", "", html.unescape(og)).strip(),
        "native_title": native,
        "aka": akas,
        "country": COUNTRY_CODES.get(country, country),
        "type": field("Type"),
        "year": year.group(1) if year else "",
    }


def parse_listing(page):
    """Entries of one "popular shows" page, in MDL's popularity order."""
    out = []
    parts = re.split(r'id="mdl-(\d+)"', page)
    for mdl_num, block in zip(parts[1::2], parts[2::2]):
        slug = re.search(r'href="/(' + mdl_num + r'-[^"]+)"', block)
        title = re.search(r'<h6 class="[^"]*title[^"]*">\s*<a[^>]*>([^<]+)</a>', block)
        muted = re.search(r'<span class="text-muted">([^<]+)</span>', block)
        kind = re.match(r"\s*(.+?) (Drama|Movie|TV Show|Special)\s*-\s*(\d{4})(?:,\s*(\d+) episodes?)?",
                        html.unescape(muted.group(1))) if muted else None
        out.append({
            "mdl_id": slug.group(1) if slug else mdl_num,
            "title": html.unescape(title.group(1)).strip() if title else "",
            "country": kind.group(1) if kind else "", "type": kind.group(2) if kind else "",
            "year": kind.group(3) if kind else "", "episodes_listed": kind.group(4) if kind else "",
        })
    return out


def walk_ranking(max_pages):
    ranked = []
    for page_no in range(1, max_pages + 1):
        entries = parse_listing(get(f"/shows/popular?page={page_no}"))
        if not entries:
            break
        for e in entries:
            e["popularity_rank"] = len(ranked) + 1
            ranked.append(e)
        if page_no % 25 == 0:
            print(f"  ranking page {page_no}: {len(ranked)} dramas")
    return ranked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=250, help="ranking pages to walk (20 per page; MDL lists 250)")
    ap.add_argument("--ranking-only", action="store_true", help="walk the ranking, skip the title pages")
    ap.add_argument("--delay", type=float, default=DELAY, help=f"seconds between requests (min {MIN_DELAY})")
    args = ap.parse_args()
    _delay[0] = max(MIN_DELAY, args.delay)
    os.makedirs(RAW, exist_ok=True)

    cols = ["popularity_rank", "mdl_id", "title", "country", "type", "year", "episodes_listed",
            "mdl_title", "watchers", "score", "rating_count", "episodes_mdl", "error"]
    ranked = []
    try:
        ranked = walk_ranking(args.pages)
        print(f"MDL popularity ranking: {len(ranked)} entries")
        if not args.ranking_only:
            for i, row in enumerate(ranked, 1):
                try:
                    row.update(parse_title(get("/" + row["mdl_id"])))
                except Missing as e:
                    row["error"] = str(e)
                if i % 250 == 0:
                    print(f"  title pages: {i}/{len(ranked)}")
    except Blocked as e:
        print(f"stopped: {e}. Everything fetched so far is cached; re-run to resume.")
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(ranked)
    watchers = [r["watchers"] for r in ranked if r.get("watchers")]
    for th in (5_000, 10_000, 25_000, 50_000, 100_000):
        print(f"  watchers >= {th:>7,}: {sum(v >= th for v in watchers):,}")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    sys.exit(main())
