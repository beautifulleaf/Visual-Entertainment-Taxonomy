"""Apply the decided anime inclusion rule (sourcing-plan.md §4, §8).

An anime-offline-database entry is selected when any of these holds (reasons
are listed together):
  mal       MAL members >= --min-members (25,000);
  decade    pre-2000 per-decade top-up: for each decade before 2000, the top
            max(--decade-min, ceil(--decade-share x n)) titles by MAL members,
            where n = titles of that decade with a MAL members figure (MAL's
            popularity ranking was walked down to ~1,000 members, so n counts
            titles on the ranking); MAL's audience skews recent;
  country   per-country top-up: titles from --topup-countries (CN, donghua)
            with MAL members >= --country-min-members (10,000).
Country of origin is AniList's (anime_popularity.csv). Adult titles are kept
and flagged (is_adult), as the plan does not exclude them.

Inputs:  data/interim/anime_popularity.csv, data/interim/anime_candidates.csv
Output:  data/interim/anime_selected.csv
           mal_id, anilist_id, title, type, year, episodes, country, mal_members,
           anilist_popularity, is_adult, main_studio, reasons

Usage:
  python3 pipelines/anime/select.py [--min-members 25000] [--decade-share 0.2] [--decade-min 5]
                                    [--topup-countries CN] [--country-min-members 10000]
"""
import argparse
import collections
import csv
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, "data", "interim")
POPULARITY = os.path.join(D, "anime_popularity.csv")
CANDIDATES = os.path.join(D, "anime_candidates.csv")
OUT = os.path.join(D, "anime_selected.csv")
COLS = ["mal_id", "anilist_id", "title", "type", "year", "episodes", "country", "mal_members",
        "anilist_popularity", "is_adult", "main_studio", "reasons"]
REASONS = ("mal", "decade", "country")
SPOT = {"2747": "Tetsuwan Atom (1963)", "47": "Akira", "501": "Doraemon (1973)", "2471": "Doraemon (1979)",
        "2406": "Sazae-san", "164": "Mononoke Hime", "2246": "Mononoke (2007)", "4513": "Hakujaden",
        "3220": "Kanashimi no Belladonna", "1441": "Ginga Tetsudou no Yoru", "2765": "Momotarou: Umi no Shinpei",
        "28053": "Kumo no Ito", "1650": "Uchuu Senkan Yamato", "2253": "Mazinger Z", "37208": "Mo Dao Zu Shi",
        "44074": "Shiguang Dailiren (Link Click)", "40111": "Nezha Zhi Mo Tong Jiang Shi",
        "8783": "Nezha Nao Hai (1979)", "6609": "Pucca (TV)"}


def to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-members", type=int, default=25_000)
    ap.add_argument("--decade-share", type=float, default=0.2)
    ap.add_argument("--decade-min", type=int, default=5)
    ap.add_argument("--decade-before", type=int, default=2000)
    ap.add_argument("--topup-countries", default="CN", help="comma-separated AniList countries of origin")
    ap.add_argument("--country-min-members", type=int, default=10_000)
    args = ap.parse_args()
    topup_countries = {c.strip() for c in args.topup_countries.split(",") if c.strip()}

    episodes = {}
    with open(CANDIDATES, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["mal_id"]:
                episodes[r["mal_id"]] = r["episodes"]
    with open(POPULARITY, encoding="utf-8") as f:
        titles = [{
            "mal_id": r["mal_id"], "anilist_id": r["anilist_id"], "title": r["title"], "type": r["type"],
            "year": r["year"], "episodes": episodes.get(r["mal_id"], ""), "country": r["country_of_origin"],
            "mal_members": to_int(r["mal_members"]), "has_mal": bool(r["mal_members"]),
            "anilist_popularity": r["anilist_popularity"], "is_adult": r["is_adult"],
            "main_studio": r["main_studio"], "reasons": [],
        } for r in csv.DictReader(f)]

    decades = collections.defaultdict(list)
    for t in titles:
        if t["mal_members"] >= args.min_members:
            t["reasons"].append("mal")
        y = to_int(t["year"])
        if t["has_mal"] and y and y < args.decade_before:
            decades[y // 10 * 10].append(t)
        if t["country"] in topup_countries and t["mal_members"] >= args.country_min_members:
            t["reasons"].append("country")
    decade_report = {}
    for d, cell in sorted(decades.items()):
        cell.sort(key=lambda t: -t["mal_members"])
        take = max(args.decade_min, math.ceil(args.decade_share * len(cell)))
        for t in cell[:take]:
            t["reasons"].append("decade")
        decade_report[d] = (len(cell), take, sum(t["reasons"] == ["decade"] for t in cell[:take]),
                            cell[min(take, len(cell)) - 1]["mal_members"])
    for t in titles:
        t["reasons"] = [r for r in REASONS if r in t["reasons"]]

    selected = sorted((t for t in titles if t["reasons"]), key=lambda t: (-t["mal_members"], t["title"]))
    with open(OUT, "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=COLS)
        w.writeheader()
        for t in selected:
            row = {c: t[c] for c in COLS}
            row["reasons"] = ";".join(t["reasons"])
            w.writerow(row)

    # ---------------------------------------------------------------- report
    print(f"titles: {len(titles)} ({sum(t['has_mal'] for t in titles)} with MAL members)")
    print(f"selected: {len(selected)}")
    print("  by reason (any):", dict(collections.Counter(r for t in selected for r in t["reasons"])))
    print("  by reason combination:", dict(collections.Counter(";".join(t["reasons"]) for t in selected).most_common()))
    print(f"  pre-{args.decade_before} decade top-up (titles on MAL / taken / added below the bar / cutoff members):")
    print("    " + " · ".join(f"{d}s {n}/{k}/+{a}/{c:,}" for d, (n, k, a, c) in decade_report.items()))
    print("  by format:", dict(collections.Counter(t["type"] for t in selected).most_common()))
    print("  by country:", dict(collections.Counter(t["country"] or "?" for t in selected).most_common()))
    print(f"  adult titles kept: {sum(t['is_adult'] == 'True' for t in selected)}")
    dec = collections.Counter((to_int(t["year"]) // 10 * 10) if to_int(t["year"]) else "?" for t in selected)
    print("  by decade:", " · ".join(f"{d}s {n}" for d, n in sorted(dec.items(), key=lambda x: str(x[0]))))
    by_fd = collections.Counter((t["type"], (to_int(t["year"]) // 10 * 10) if to_int(t["year"]) else "?")
                                for t in selected)
    fmts = [f for f, _ in collections.Counter(t["type"] for t in selected).most_common()]
    ds = sorted({d for _, d in by_fd}, key=str)
    print("  format x decade:\n    " + f"{'':8}" + "".join(f"{str(d):>7}" for d in ds))
    for fm in fmts:
        print("    " + f"{fm:8}" + "".join(f"{by_fd[(fm, d)]:>7}" for d in ds))
    other = collections.Counter(t["country"] for t in titles if t["country"] not in ("JP", "", *topup_countries)
                                and t["mal_members"] >= args.country_min_members)
    if other:
        print(f"  note: other non-JP titles at >= {args.country_min_members:,} MAL members not covered by the "
              f"country top-up: {dict(other)} (selected anyway through the main bar: "
              f"{sum(1 for t in selected if t['country'] in other and 'mal' in t['reasons'])})")
    print("spot checks:")
    by_mal = {t["mal_id"]: t for t in titles if t["mal_id"]}
    for m, label in SPOT.items():
        t = by_mal.get(m)
        if not t:
            print(f"    {label}: not a candidate")
            continue
        print(f"    {label} [{t['type']} {t['year']} {t['country'] or '?'}] MAL {m}: "
              f"{t['mal_members']:,} members: {';'.join(t['reasons']) or 'NOT SELECTED'}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    sys.exit(main())
