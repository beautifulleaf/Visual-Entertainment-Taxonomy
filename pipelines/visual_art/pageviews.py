"""Wikipedia pageviews per pooled artist, from the Wikimedia monthly bulk dumps.

Uses the `pageview_complete` monthly "user" files (human traffic only), not the
REST API, which rate-limits shared IPs. Each dump (~6 GB bz2) is downloaded to
data/raw/pageviews/ and streamed through lbzip2 (parallel) or bzip2; lines are
"wiki title page_id access_method views hourly", one per access method, so views
are summed per article and then over every language edition an artist has.

Input:  data/interim/visual_art/sitelinks.tsv (qid, wiki, title; from build_pool.py)
Output: data/interim/visual_art/pageviews.csv (qid, views_<month>..., pageviews = monthly mean)

Usage: python3 pipelines/visual_art/pageviews.py [--months 2026-09 2026-08 ...] [--sitelinks TSV --out CSV]
"""
import argparse
import collections
import csv
import hashlib
import os
import shutil
import subprocess
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw", "pageviews")
SITELINKS = os.path.join(ROOT, "data", "interim", "visual_art", "sitelinks.tsv")
OUT_PATH = os.path.join(ROOT, "data", "interim", "visual_art", "pageviews.csv")
DUMP = "https://dumps.wikimedia.org/other/pageview_complete/monthly/{y}/{y}-{m}/pageviews-{y}{m}-user.bz2"
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"


def dump_path(month):
    y, m = month.split("-")
    path = os.path.join(RAW, f"pageviews-{y}{m}-user.bz2")
    if not os.path.exists(path):
        print(f"downloading {month} dump")
        req = urllib.request.Request(DUMP.format(y=y, m=m), headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=600) as r, open(path + ".part", "wb") as f:
            shutil.copyfileobj(r, f, 1 << 22)
        os.replace(path + ".part", path)
    return path


def month_views(month, articles):
    """{qid: views} for one month, using a per-month cache."""
    # Keyed on the article set too: a later region adds artists, and a per-month
    # cache would silently return counts that omit them.
    digest = hashlib.sha1("\n".join(sorted(f"{w.decode()} {t.decode()}" for w, t in articles)).encode()).hexdigest()[:12]
    cache = os.path.join(RAW, f"views-{month}-{digest}.tsv")
    if os.path.exists(cache):
        with open(cache, encoding="utf-8") as f:
            return {q: int(v) for q, v in (line.rstrip("\n").split("\t") for line in f)}
    decoder = ["lbzip2", "-dc"] if shutil.which("lbzip2") else ["bzip2", "-dc"]
    proc = subprocess.Popen(decoder + [dump_path(month)], stdout=subprocess.PIPE)
    views = collections.Counter()
    wikis = {w for w, _ in articles}
    for n, raw in enumerate(proc.stdout):
        wiki, _, rest = raw.partition(b" ")
        if wiki not in wikis:
            continue
        title, _, rest = rest.partition(b" ")
        q = articles.get((wiki, title))
        if q:
            views[q] += int(rest.split(b" ", 3)[2])
        if n % 100_000_000 == 0 and n:
            print(f"  {month}: {n // 1_000_000}M lines")
    if proc.wait() != 0:
        raise RuntimeError(f"decompressing the {month} dump failed")
    with open(cache, "w", encoding="utf-8") as f:
        f.writelines(f"{q}\t{v}\n" for q, v in views.items())
    return views


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--months", nargs="+", default=["2026-09"])
    # Other pools (e.g. contemporary art) pass their own sitelinks file and output.
    ap.add_argument("--sitelinks", default=SITELINKS)
    ap.add_argument("--out", default=OUT_PATH)
    args = ap.parse_args()
    os.makedirs(RAW, exist_ok=True)

    articles, qids = {}, set()
    with open(args.sitelinks, encoding="utf-8") as f:
        for line in f:
            q, wiki, title = line.rstrip("\n").split("\t")
            articles[(f"{wiki}.wikipedia".encode(), title.replace(" ", "_").encode())] = q
            qids.add(q)
    print(f"{len(articles)} articles for {len(qids)} artists")

    per_month = {m: month_views(m, articles) for m in args.months}
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["qid"] + [f"views_{m}" for m in args.months] + ["pageviews"])
        for q in sorted(qids):
            vs = [per_month[m].get(q, 0) for m in args.months]
            w.writerow([q] + vs + [round(sum(vs) / len(vs))])
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
