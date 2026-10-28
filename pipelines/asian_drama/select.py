"""Apply the decided Asian-drama inclusion rule (sourcing-plan.md §5, §8).

A drama is selected when any of these holds (reasons are listed together):
  watchers  MDL type Drama with watchers >= --min-watchers (5,000);
  topup     in the top --topup-share (15%) by watchers of its country x decade
            cell of the MDL ranking (Drama type only), at least --topup-min (5)
            per cell, or the whole cell when it is smaller;
  award     won an Asian TV award (or an Asian winner of another award), as
            matched by match_awards.py; the drama may lie outside the ranking.
MDL's "TV Show" entries (variety, reality, documentary) do not enter the drama
database: they go to a separate file for the unscripted database, with award
winners of that type added. "Special" entries are left out of both.

Inputs:  data/interim/asian_drama_mdl.csv, data/interim/asian_drama_awards.csv,
         cached title pages in data/raw/mdl/ (native title, missing type/country/year)
Outputs: data/interim/asian_drama_selected.csv
           mdl_id, title, native_title, country, year, watchers, popularity_rank, reasons, awards
         data/interim/asian_unscripted_mdl.csv (same columns)

Usage:
  python3 pipelines/asian_drama/select.py [--min-watchers 5000] [--topup-share 0.15] [--topup-min 5]
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
from mdl_fetch import COUNTRY_CODES, RAW, parse_details  # noqa: E402

MDL = os.path.join(ROOT, "data", "interim", "asian_drama_mdl.csv")
AWARDS = os.path.join(ROOT, "data", "interim", "asian_drama_awards.csv")
OUT = os.path.join(ROOT, "data", "interim", "asian_drama_selected.csv")
OUT_UNSCRIPTED = os.path.join(ROOT, "data", "interim", "asian_unscripted_mdl.csv")
COLS = ["mdl_id", "title", "native_title", "country", "year", "watchers", "popularity_rank", "reasons", "awards"]


def num(mdl_id):
    m = re.match(r"(\d+)", mdl_id or "")
    return m.group(1) if m else ""


def page_details(mdl_id):
    path = os.path.join(RAW, re.sub(r"[^\w.-]", "_", mdl_id) + ".html.gz")
    if not os.path.exists(path):
        return None
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return parse_details(f.read())


def to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-watchers", type=int, default=5000)
    ap.add_argument("--topup-share", type=float, default=0.15)
    ap.add_argument("--topup-min", type=int, default=5)
    args = ap.parse_args()

    # ranked MDL entries, completed from their title pages
    items = {}
    with open(MDL, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = page_details(r["mdl_id"]) or {}
            typ = r["type"] or {"TV Program": "TV Show"}.get(d.get("type", ""), d.get("type", ""))
            items[num(r["mdl_id"])] = {
                "mdl_id": r["mdl_id"], "title": r["title"], "native_title": d.get("native_title", ""),
                "country": COUNTRY_CODES.get(r["country"], "") or d.get("country", ""),
                "year": r["year"] or d.get("year", ""), "watchers": to_int(r["watchers"]),
                "popularity_rank": r["popularity_rank"], "type": typ, "reasons": [], "awards": [],
            }

    # award winners (match_awards.py); some lie outside the ranking
    n_award_rows = 0
    if os.path.exists(AWARDS):
        with open(AWARDS, encoding="utf-8") as f:
            for a in csv.DictReader(f):
                if a["won"] != "1" or not a["mdl_id"]:
                    continue
                n_award_rows += 1
                k = num(a["mdl_id"])
                if k not in items:
                    items[k] = {
                        "mdl_id": a["mdl_id"], "title": a["mdl_title"] or a["title"],
                        "native_title": a["native_title"], "country": a["mdl_country"] or a["country"],
                        "year": a["mdl_year"], "watchers": to_int(a["watchers"]), "popularity_rank": "",
                        "type": a["mdl_type"] or "Drama", "reasons": [], "awards": [],
                    }
                label = f"{a['award']} {a['year']}"
                if label not in items[k]["awards"]:
                    items[k]["awards"].append(label)
    else:
        print(f"note: {AWARDS} missing; run match_awards.py for the award route")

    # rules
    cells = collections.defaultdict(list)
    for k, it in items.items():
        if it["type"] != "Drama":
            continue
        if it["watchers"] >= args.min_watchers:
            it["reasons"].append("watchers")
        if it["popularity_rank"] and it["country"] and it["year"]:
            cells[(it["country"], int(it["year"]) // 10 * 10)].append(it)
    for cell in cells.values():
        cell.sort(key=lambda it: -it["watchers"])
        take = min(len(cell), max(args.topup_min, math.ceil(args.topup_share * len(cell))))
        for it in cell[:take]:
            it["reasons"].append("topup")
    for it in items.values():
        if it["awards"]:
            it["reasons"].append("award")

    def row(it):
        out = {c: it[c] for c in COLS if c not in ("reasons", "awards")}
        out["reasons"] = ";".join(it["reasons"])
        out["awards"] = "; ".join(it["awards"])
        return out

    order = sorted(items.values(), key=lambda it: -it["watchers"])
    selected = [it for it in order if it["type"] in ("Drama", "") and it["reasons"]]
    unscripted = [it for it in order if it["type"] == "TV Show"]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(row(it) for it in selected)
    with open(OUT_UNSCRIPTED, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(row(it) for it in unscripted)

    # report
    by_type = collections.Counter(it["type"] or "?" for it in items.values())
    print(f"MDL entries: {len(items)} {dict(by_type)}; winning award rows matched: {n_award_rows}")
    print(f"selected dramas: {len(selected)}")
    print("  by reason (any):", dict(collections.Counter(r for it in selected for r in it["reasons"])))
    print("  by reason combination:", dict(collections.Counter(";".join(it["reasons"]) for it in selected)))
    print("  by country (total / watchers bar / added by top-up only / added by award only / added by both):")
    for c, n in collections.Counter(it["country"] or "?" for it in selected).most_common():
        sub = [it for it in selected if (it["country"] or "?") == c]
        base = sum("watchers" in it["reasons"] for it in sub)
        add = [it for it in sub if "watchers" not in it["reasons"]]
        only_t = sum(it["reasons"] == ["topup"] for it in add)
        only_a = sum(it["reasons"] == ["award"] for it in add)
        both = sum(set(it["reasons"]) == {"topup", "award"} for it in add)
        print(f"    {c:3s} {n:5d}  {base:5d}  +{only_t:4d}  +{only_a:4d}  +{both:3d}")
    print(f"unscripted (MDL TV Show): {len(unscripted)} ({sum(bool(it['awards']) for it in unscripted)} award winners)")
    skipped = [it for it in items.values() if it["awards"] and it["type"] not in ("Drama", "", "TV Show")]
    if skipped:
        print(f"award winners of other MDL types left out: {[(it['title'], it['type']) for it in skipped]}")
    print(f"wrote {OUT}\nwrote {OUT_UNSCRIPTED}")


if __name__ == "__main__":
    sys.exit(main())
