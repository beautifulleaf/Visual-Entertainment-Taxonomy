"""Estimate Letterboxd rating counts for film candidates MDBList has no figure for.

Sourcing plan §2, pipeline step 4 ("Gaps"). About 11,500 candidates have no
MDBList Letterboxd count. For those, use a public Letterboxd user sample as a
relative signal:

  Hugging Face titouann/letterboxd-10m-movies-ratings-2025 (CC BY-NC-SA 4.0):
  10.46M ratings by the 6,519 most popular Letterboxd users, Dec 2025.
  Columns: user, movie_id (Letterboxd internal numeric id), title (actually the
  Letterboxd film slug, e.g. "parasite-2019"), rating. No TMDB or IMDb id.

Steps:
  1. Count distinct users per film slug in the sample.
  2. Map sample slugs to tconst. Primary: the slug in MDBList's Letterboxd URL
     (/film/<slug>/), from the raw cache. Fallback for gap films whose MDBList
     slug is absent from the sample (alternative-title misses, or films MDBList
     did not return): slugs built Letterboxd-style from the IMDb title and the
     original title, skipping any slug MDBList already assigns to a different
     film. Where MDBList has a slug, only an alternative-title "<title>-<year>"
     slug is accepted; a bare "<title>" slug only for films with no MDBList
     slug, and only when no other candidate shares the title. The sample has
     no TMDB/IMDb ids, so no id-based join is possible.
  3. Calibrate on films that do have MDBList letterboxd_votes:
     log10(letterboxd_votes) ~ log10(sample_users), OLS. Report r, R² and the
     sample-user count whose prediction is 10k ratings.
  4. Apply the fit to the gap films and write
     data/interim/film_letterboxd_estimates.csv
     (tconst, sample_users, estimated_letterboxd_votes, method, letterboxd_slug).
     method: mdblist_slug | title_year_slug | title_slug | not_in_sample.
     Films absent from the sample get sample_users 0 and no estimate.

The sample is downloaded (no account needed) to data/raw/letterboxd_sample/.

Usage:
  python3 pipelines/film/letterboxd_sample.py              # download if missing, then run
  python3 pipelines/film/letterboxd_sample.py --min-users 3  # calibrate only on films with >= 3 sample users
"""
import argparse
import csv
import json
import math
import os
import re
import sys
import unicodedata
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "common"))
import mdblist  # noqa: E402

DATASET_URL = "https://huggingface.co/datasets/titouann/letterboxd-10m-movies-ratings-2025/resolve/main/train.csv"
SAMPLE = os.path.join(ROOT, "data", "raw", "letterboxd_sample", "train.csv")
CANDIDATES = os.path.join(ROOT, "data", "interim", "film_candidates.csv")
RATINGS = os.path.join(ROOT, "data", "interim", "film_ratings.csv")
CANON = os.path.join(ROOT, "data", "interim", "film_canon.csv")
CACHE = os.path.join(ROOT, "data", "raw", "mdblist", "media_batch.jsonl")
OUT_PATH = os.path.join(ROOT, "data", "interim", "film_letterboxd_estimates.csv")
TARGET = 10_000


def download():
    if os.path.exists(SAMPLE):
        return
    os.makedirs(os.path.dirname(SAMPLE), exist_ok=True)
    print(f"downloading {DATASET_URL}")
    tmp = SAMPLE + ".part"
    urllib.request.urlretrieve(DATASET_URL, tmp)
    os.replace(tmp, SAMPLE)


def sample_users():
    """Distinct users per Letterboxd slug. The file is grouped by user, so a
    film counts once per user block; a re-appearing user is detected and fails."""
    counts, last = {}, {}
    seen_users, cur, rows = set(), None, 0
    with open(SAMPLE, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows += 1
            u, slug = row["user"], row["title"]
            if u != cur:
                if u in seen_users:
                    sys.exit("sample is not grouped by user; distinct-user counting needs a set")
                seen_users.add(u)
                cur = u
            if last.get(slug) != u:
                last[slug] = u
                counts[slug] = counts.get(slug, 0) + 1
    print(f"sample: {rows:,} ratings, {len(seen_users):,} users, {len(counts):,} films")
    return counts


def slugify(text):
    """Approximate Letterboxd's slug rule: ASCII-fold, lowercase, drop
    apostrophes, every other non-alphanumeric run becomes a hyphen."""
    t = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()
    t = t.replace("&", " ").replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def mdblist_slugs():
    out = {}
    for item in mdblist.cached_items(CACHE):
        tconst = mdblist.imdb_id_of(item)
        for r in item.get("ratings") or []:
            if r.get("source") == "letterboxd" and r.get("url"):
                m = re.match(r"^/?film/([^/]+)/?$", r["url"].strip())
                if tconst and m:
                    out[tconst] = m.group(1)
    return out


def ols(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    a = my - b * mx
    r = sxy / math.sqrt(sxx * syy)
    resid = math.sqrt(sum((y - a - b * x) ** 2 for x, y in zip(xs, ys)) / (n - 2))
    return a, b, r, resid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-users", type=int, default=1, help="calibrate on films with at least this many sample users")
    args = ap.parse_args()
    download()
    users = sample_users()

    with open(CANDIDATES, encoding="utf-8") as f:
        cands = {row["tconst"]: row for row in csv.DictReader(f)}
    with open(RATINGS, encoding="utf-8") as f:
        lb_votes = {r["tconst"]: int(r["letterboxd_votes"]) for r in csv.DictReader(f) if r["letterboxd_votes"]}
    canon = set()
    if os.path.exists(CANON):
        with open(CANON, encoding="utf-8") as f:
            canon = {r["tconst"] for r in csv.DictReader(f) if r["tconst"]}
    slugs = mdblist_slugs()
    claimed = {}
    for t, s in slugs.items():
        claimed.setdefault(s, set()).add(t)

    # --- mapping rate on all candidates via MDBList slugs ---
    with_slug = [t for t in cands if t in slugs]
    in_sample = [t for t in with_slug if slugs[t] in users]
    mapped_slugs = {slugs[t] for t in in_sample}
    print(f"candidates: {len(cands):,}; with an MDBList Letterboxd slug: {len(with_slug):,}; "
          f"slug found in sample: {len(in_sample):,} ({len(in_sample) / len(with_slug):.1%})")
    print(f"sample films mapped to a candidate: {len(mapped_slugs):,} of {len(users):,}; "
          f"they hold {sum(users[s] for s in mapped_slugs) / sum(users.values()):.1%} of sample user-film pairs")

    # --- calibration ---
    cal = [(users[slugs[t]], lb_votes[t]) for t in in_sample if t in lb_votes and users[slugs[t]] >= args.min_users]
    xs = [math.log10(u) for u, _ in cal]
    ys = [math.log10(v) for _, v in cal]
    a, b, r, resid = ols(xs, ys)
    thresh = 10 ** ((math.log10(TARGET) - a) / b)
    print(f"\ncalibration on {len(cal):,} films with MDBList votes and >= {args.min_users} sample users:")
    print(f"  log10(lb_votes) = {a:.3f} + {b:.3f} * log10(sample_users)   r = {r:.3f}  R² = {r * r:.3f}  "
          f"resid sd = {resid:.3f} dex (x{10 ** resid:.2f})")
    print(f"  10k Letterboxd ratings <-> {thresh:.1f} sample users")
    # empirical view per sample-user bucket: share of films clearing 10k
    with_count = [t for t in cands if t in lb_votes]
    absent = [t for t in with_count if t in slugs and slugs[t] not in users]
    print(f"  films with MDBList votes but absent from sample: {len(absent):,}; "
          f">=10k among them: {sum(lb_votes[t] >= TARGET for t in absent):,}")
    print("  sample users | films | median lb votes | share >= 10k")
    buckets = [(1, 1), (2, 2), (3, 4), (5, 7), (8, 11), (12, 19), (20, 34), (35, 59), (60, 99), (100, 10 ** 9)]
    for lo, hi in buckets:
        vs = sorted(v for u, v in cal if lo <= u <= hi) if args.min_users <= lo else []
        if vs:
            print(f"  {lo:>5}-{hi if hi < 10 ** 9 else '':<5} | {len(vs):>6,} | {vs[len(vs) // 2]:>10,} | "
                  f"{sum(v >= TARGET for v in vs) / len(vs):.0%}")
    # classification check of the threshold on the calibration set
    cut = math.ceil(thresh)
    tp = sum(u >= cut and v >= TARGET for u, v in cal)
    fp = sum(u >= cut and v < TARGET for u, v in cal)
    fn = sum(u < cut and v >= TARGET for u, v in cal)
    print(f"  as a rule 'sample_users >= {cut}' on the calibration set: precision {tp / (tp + fp):.0%}, "
          f"recall {tp / (tp + fn):.0%} (tp {tp:,}, fp {fp:,}, fn {fn:,})")

    # --- gap films ---
    gap = [t for t in cands if t not in lb_votes]
    title_count = {}
    for row in cands.values():
        for s in {slugify(row["title"]), slugify(row["original_title"])}:
            title_count[s] = title_count.get(s, 0) + 1
    rows = []
    for t in gap:
        c = cands[t]
        slug, method = slugs.get(t), "not_in_sample"
        if slug and slug in users:
            method = "mdblist_slug"
        else:
            year = c["year"] if c["year"] not in ("", "\\N") else ""
            titles = [x for x in dict.fromkeys([slugify(c["original_title"]), slugify(c["title"])]) if x]
            found = None
            if slug and re.sub(r"-\d+$", "", slug) in titles:
                # MDBList's slug is the title-based one and is simply not in the sample: Letterboxd
                # only adds "-<year>" to disambiguate, so the bare title slug belongs to another film.
                titles = []
            for base in titles:
                for s, m in ((f"{base}-{year}", "title_year_slug"), (base, "title_slug")):
                    if not year and m == "title_year_slug":
                        continue
                    if slug and m == "title_slug":
                        # alternative-title miss: trust only the year-qualified slug
                        continue
                    if s in users and not (claimed.get(s, set()) - {t}):
                        # a bare title slug is only trusted when no other candidate shares the title
                        if m == "title_slug" and title_count.get(base, 0) > 1:
                            continue
                        found = (s, m)
                        break
                if found:
                    break
            if found:
                slug, method = found
        n = users.get(slug, 0) if method != "not_in_sample" else 0
        est = round(10 ** (a + b * math.log10(n))) if n else ""
        rows.append({"tconst": t, "sample_users": n, "estimated_letterboxd_votes": est, "method": method,
                     "letterboxd_slug": slug or ""})

    with open(OUT_PATH, "w", newline="", encoding="utf-8") as out:
        w = csv.DictWriter(out, fieldnames=["tconst", "sample_users", "estimated_letterboxd_votes", "method",
                                            "letterboxd_slug"])
        w.writeheader()
        w.writerows(rows)

    print(f"\ngap films (no MDBList Letterboxd count): {len(gap):,}")
    for m in ("mdblist_slug", "title_year_slug", "title_slug", "not_in_sample"):
        print(f"  {m:<16} {sum(r['method'] == m for r in rows):>6,}")
    est = [r for r in rows if r["estimated_letterboxd_votes"] != ""]
    over = [r for r in est if r["estimated_letterboxd_votes"] >= TARGET]
    print(f"  with an estimate: {len(est):,}; estimated >= 10k: {len(over):,} "
          f"(of which canon: {sum(r['tconst'] in canon for r in over):,})")
    for th in (1_000, 5_000, 25_000):
        print(f"  estimated >= {th:>6,}: {sum(r['estimated_letterboxd_votes'] >= th for r in est):,}")
    print("\ntop gap films by sample users:")
    for r in sorted(est, key=lambda r: -r["sample_users"])[:25]:
        c = cands[r["tconst"]]
        print(f"  {r['tconst']:<11} {c['title'][:40]:<40} {c['year']:<5} {c['title_type']:<9} imdb {int(c['imdb_votes']):>7,}  "
              f"users {r['sample_users']:>4}  est {r['estimated_letterboxd_votes']:>8,}  {r['method']}  {r['letterboxd_slug']}")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
