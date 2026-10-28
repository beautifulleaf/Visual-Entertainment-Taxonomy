"""Apply the decided scripted-TV inclusion rule (sourcing-plan.md §3, §8).

Only series routed to the scripted-TV database (tv_routed.csv, database =
scripted_tv) are considered. A series is selected when any of these holds
(reasons are listed together):
  imdb    IMDb votes >= --min-votes (2,500);
  topup   regional top-up: per origin country x decade of the first year, the
          top max(--topup-min, ceil(--topup-share x cell size)) series by IMDb
          votes, each with >= --topup-floor (200) votes. Cell size = all scripted
          series in the cell (>= 100 votes, the harvest floor). Series with no
          origin country (about 4,500, mostly low-vote) have no cell;
  award   won a major award (tv_awards.csv, won = 1, joined by IMDb ID).
          Nominations are a signal only: counted in `nominations`, never a reason.
serial_tradition (telenovela / dizi / Indian soap / teleserye / Ramadan series)
is carried over from route.py.

Inputs:  data/interim/tv_routed.csv, data/interim/tv_awards.csv
Output:  data/interim/tv_selected.csv
           tconst, tmdb_id, title, imdb_title_type, start_year, end_year, episodes, country,
           language, imdb_votes, serial_tradition, reasons, awards, nominations

Usage:
  python3 pipelines/tv/select.py [--min-votes 2500] [--topup-share 0.05] [--topup-min 3] [--topup-floor 200]
"""
import argparse
import collections
import csv
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, "data", "interim")
ROUTED = os.path.join(D, "tv_routed.csv")
AWARDS = os.path.join(D, "tv_awards.csv")
OUT = os.path.join(D, "tv_selected.csv")
COLS = ["tconst", "tmdb_id", "title", "imdb_title_type", "start_year", "end_year", "episodes", "country",
        "language", "imdb_votes", "serial_tradition", "reasons", "awards", "nominations"]
REASONS = ("imdb", "topup", "award")
SPOT = {"tt0306414": "The Wire", "tt0098936": "Twin Peaks", "tt0092337": "Dekalog", "tt0108906": "Riget",
        "tt0087400": "Heimat", "tt0080196": "Berlin Alexanderplatz", "tt1848220": "Muhtesem Yüzyil",
        "tt1534360": "Ezel", "tt0268093": "Ramayan", "tt0158417": "Mahabharat",
        "tt0278212": "Kyunki Saas Bhi Kabhi Bahu Thi", "tt0229889": "El Chavo del Ocho",
        "tt0211858": "Rosa salvaje", "tt0142036": "Escrava Isaura", "tt2303077": "Avenida Brasil",
        "tt0233127": "Yo soy Betty, la fea", "tt1999065": "Bab al-Hara", "tt0086798": "Shaka Zulu",
        "tt9839146": "Blood & Water", "tt0088580": "Neighbours"}


def to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-votes", type=int, default=2500)
    ap.add_argument("--topup-share", type=float, default=0.05)
    ap.add_argument("--topup-min", type=int, default=3)
    ap.add_argument("--topup-floor", type=int, default=200)
    args = ap.parse_args()

    with open(ROUTED, encoding="utf-8") as f:
        routed = list(csv.DictReader(f))
    series = {}
    for r in routed:
        if r["database"] != "scripted_tv":
            continue
        series[r["tconst"]] = {
            "tconst": r["tconst"], "tmdb_id": r["tmdb_id"], "title": r["mdblist_title"],
            "imdb_title_type": r["imdb_title_type"], "start_year": r["start_year"] or r["year"],
            "end_year": r["end_year"], "episodes": r["episodes"], "country": r["country"],
            "language": r["language"], "imdb_votes": to_int(r["imdb_votes"]),
            "serial_tradition": r["serial_tradition"], "reasons": [], "awards": [], "nominations": 0,
        }

    other_db = collections.Counter()
    db_of = {r["tconst"]: r["database"] for r in routed}
    n_win = set()
    with open(AWARDS, encoding="utf-8") as f:
        for a in csv.DictReader(f):
            t = a["tconst"]
            if not t:
                continue
            if t not in series:
                if a["won"] == "1":
                    other_db[db_of.get(t, "not in harvest")] += 1
                continue
            if a["won"] == "1":
                n_win.add(t)
                label = f"{a['award']} {a['year']}"
                if label not in series[t]["awards"]:
                    series[t]["awards"].append(label)
            else:
                series[t]["nominations"] += 1

    cells = collections.defaultdict(list)
    for s in series.values():
        if s["imdb_votes"] >= args.min_votes:
            s["reasons"].append("imdb")
        y = to_int(s["start_year"])
        if s["country"] and y:
            cells[(s["country"], y // 10 * 10)].append(s)
    for cell in cells.values():
        cell.sort(key=lambda s: -s["imdb_votes"])
        take = max(args.topup_min, math.ceil(args.topup_share * len(cell)))
        for s in cell[:take]:
            if s["imdb_votes"] >= args.topup_floor:
                s["reasons"].append("topup")
    for s in series.values():
        if s["awards"]:
            s["reasons"].append("award")
        s["reasons"] = [r for r in REASONS if r in s["reasons"]]

    selected = sorted((s for s in series.values() if s["reasons"]), key=lambda s: (-s["imdb_votes"], s["tconst"]))
    with open(OUT, "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=COLS)
        w.writeheader()
        for s in selected:
            row = {c: s[c] for c in COLS}
            row["reasons"] = ";".join(s["reasons"])
            row["awards"] = "; ".join(s["awards"])
            w.writerow(row)

    # ---------------------------------------------------------------- report
    print(f"scripted series: {len(series)} ({sum(1 for s in series.values() if not s['country'])} without a country); "
          f"cells: {len(cells)}")
    print(f"winning award rows for series outside scripted TV (by database): {dict(other_db)}")
    print(f"selected: {len(selected)}")
    print("  by reason (any):", dict(collections.Counter(r for s in selected for r in s["reasons"])))
    print("  by reason combination:", dict(collections.Counter(";".join(s["reasons"]) for s in selected).most_common()))
    below = [s for s in selected if "imdb" not in s["reasons"]]
    print(f"  below the IMDb bar: {len(below)} (top-up {sum('topup' in s['reasons'] for s in below)}, "
          f"award {sum('award' in s['reasons'] for s in below)}, award only "
          f"{sum(s['reasons'] == ['award'] for s in below)})")
    print(f"  serial_tradition: {sum(s['serial_tradition'] == '1' for s in selected)} selected of "
          f"{sum(s['serial_tradition'] == '1' for s in series.values())}; by country: "
          + ", ".join(f"{c} {n}" for c, n in collections.Counter(
              s["country"] for s in selected if s["serial_tradition"] == "1").most_common()))
    print(f"  by type:", dict(collections.Counter(s["imdb_title_type"] for s in selected)))
    by_c = collections.Counter(s["country"] or "?" for s in selected)
    add_c = collections.Counter(s["country"] or "?" for s in below)
    print("  by country (total / below the IMDb bar):")
    print("    " + " · ".join(f"{c} {n} (+{add_c[c]})" for c, n in by_c.most_common(45)))
    print(f"    ... {len(by_c)} countries in all")
    dec = collections.Counter((to_int(s["start_year"]) // 10 * 10) if to_int(s["start_year"]) else "?" for s in selected)
    print("  by decade:", " · ".join(f"{d}s {n}" for d, n in sorted(dec.items(), key=lambda x: str(x[0]))))
    print("spot checks:")
    for t, label in SPOT.items():
        s = series.get(t)
        if not s:
            print(f"    {label}: not scripted TV ({db_of.get(t, 'not in harvest')})")
            continue
        print(f"    {label} ({s['start_year']}) {t} {s['country'] or '?'} {s['imdb_votes']:,} votes "
              f"serial={s['serial_tradition']}: {';'.join(s['reasons']) or 'NOT SELECTED'}"
              + (f" [{s['awards'][0]}{' ...' if len(s['awards']) > 1 else ''}]" if s["awards"] else "")
              + (f" nominations {s['nominations']}" if s["nominations"] else ""))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    sys.exit(main())
