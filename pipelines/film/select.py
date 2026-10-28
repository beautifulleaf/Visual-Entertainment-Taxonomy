"""Apply the decided film inclusion rule (sourcing-plan.md §2, §8).

A film is selected when any of these holds (reasons are listed together):
  letterboxd  MDBList Letterboxd rating count >= --min-letterboxd (10,000);
  gap         no MDBList Letterboxd figure, but the user-sample estimate
              (letterboxd_sample.py) is >= 10,000 (§2 step 4). The gap films
              with >= 20k IMDb votes and no estimate are a manual-review list
              (printed, not selected); Man (2012) is flagged for a hand check;
  canon       on a canon/curation list (film_canon.csv, which already applies
              seeds/film/canon_overrides.csv); canon films that are not
              candidates enter with the list's title and year;
  topup       regional top-up: per country x decade, the top
              max(--topup-min, ceil(--topup-share x cell size)) candidates by
              MDBList Letterboxd count, each with at least --floor (1,000)
              ratings, or --floor-low (100) in under-covered countries (fewer
              than 200 original candidates by MDBList country). The country is
              Wikidata's P495 where film_country_reattribution.csv gives it
              (replacing MDBList's), the target country for the extra
              candidates, else MDBList's; a co-production counts in each of its
              countries. Cell size = all candidates in the cell (original +
              extra), whether or not they have a Letterboxd count.

Inputs:  data/interim/film_candidates.csv, film_ratings.csv, film_candidates_extra.csv,
         film_canon.csv, film_letterboxd_estimates.csv, film_country_reattribution.csv
Output:  data/interim/film_selected.csv
           key, tconst, tmdb_id, wikidata, title, year, title_type, mdblist_country,
           countries (regional-rule countries), letterboxd_votes, letterboxd_estimate,
           imdb_votes, reasons, canon_lists, note

Usage:
  python3 pipelines/film/select.py [--min-letterboxd 10000] [--topup-share 0.05] [--topup-min 3]
                                   [--floor 1000] [--floor-low 100] [--undercovered 200]
"""
import argparse
import collections
import csv
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, "data", "interim")
CANDIDATES = os.path.join(D, "film_candidates.csv")
RATINGS = os.path.join(D, "film_ratings.csv")
EXTRA = os.path.join(D, "film_candidates_extra.csv")
CANON = os.path.join(D, "film_canon.csv")
ESTIMATES = os.path.join(D, "film_letterboxd_estimates.csv")
REATTR = os.path.join(D, "film_country_reattribution.csv")
OUT = os.path.join(D, "film_selected.csv")
COLS = ["key", "tconst", "tmdb_id", "wikidata", "title", "year", "title_type", "mdblist_country", "countries",
        "letterboxd_votes", "letterboxd_estimate", "imdb_votes", "reasons", "canon_lists", "note"]
REASONS = ("letterboxd", "gap", "canon", "topup")

AFRICA = set("DZ AO BJ BW BF BI CV CM CF TD KM CG CD CI DJ EG GQ ER SZ ET GA GM GH GN GW KE LS LR LY MG MW ML "
             "MR MU MA MZ NA NE NG RW ST SN SC SL SO ZA SS SD TZ TG TN UG ZM ZW".split())
NORTH_AFRICA = {"DZ", "EG", "LY", "MA", "TN"}
HAND_CHECK = {"tt3175218": "gap estimate matched on the generic slug 'man': hand check"}
SPOT = {"tt0063268": "Mandabi", "tt0094349": "Yeelen", "tt0046438": "Tokyo Story", "tt0048473": "Pather Panchali",
        "tt0100234": "Close-Up", "tt0063555": "The Color of Pomegranates", "tt0073915": "Xala",
        "tt0416991": "Moolaadé", "tt0111341": "Sátántangó", "tt0055852": "Cléo from 5 to 7",
        "tt0104467": "Hyenas", "tt0070820": "Touki Bouki", "tt0060758": "Black Girl", "tt5978822": "The Wedding Party",
        "tt1284592": "Teza", "tt2611390": "Difret", "tt1823672": "Chappie", "tt27719898": "Kaiva",
        "tt3175218": "Man"}


def to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def read(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-letterboxd", type=int, default=10_000)
    ap.add_argument("--topup-share", type=float, default=0.05)
    ap.add_argument("--topup-min", type=int, default=3)
    ap.add_argument("--floor", type=int, default=1000)
    ap.add_argument("--floor-low", type=int, default=100)
    ap.add_argument("--undercovered", type=int, default=200, help="original candidates below which the low floor applies")
    ap.add_argument("--review-imdb", type=int, default=20_000, help="gap films at this many IMDb votes go to manual review")
    args = ap.parse_args()

    ratings = {r["tconst"]: r for r in read(RATINGS)}
    estimates = {r["tconst"]: to_int(r["estimated_letterboxd_votes"]) for r in read(ESTIMATES)
                 if r["estimated_letterboxd_votes"]}
    reattr = {r["tconst"]: [c for c in r["wikidata_countries"].split("|") if c] for r in read(REATTR)}
    original = collections.Counter(r["country"] for r in ratings.values())

    films = {}
    for c in read(CANDIDATES):
        r = ratings.get(c["tconst"], {})
        t = c["tconst"]
        films[t] = {
            "key": t, "tconst": t, "tmdb_id": r.get("tmdb_id", ""), "wikidata": "",
            "title": c["title"], "year": r.get("year") or c["year"], "title_type": c["title_type"],
            "mdblist_country": r.get("country", ""), "countries": reattr.get(t) or [r.get("country", "")],
            "letterboxd_votes": to_int(r.get("letterboxd_votes")), "has_lb": bool(r.get("letterboxd_votes")),
            "letterboxd_estimate": estimates.get(t, 0), "imdb_votes": to_int(c["imdb_votes"]),
            "source": "candidates", "reasons": [], "canon_lists": [], "note": HAND_CHECK.get(t, ""),
        }
    n_extra = 0
    for r in read(EXTRA):
        k = r["tconst"] or f"tmdb:{r['tmdb_id']}"
        if k in films:
            continue
        n_extra += 1
        films[k] = {
            "key": k, "tconst": r["tconst"], "tmdb_id": r["tmdb_id"], "wikidata": r["wikidata"],
            "title": r["mdblist_title"], "year": r["year"], "title_type": r["imdb_title_type"],
            "mdblist_country": r["country"], "countries": [r["target_country"]],
            "letterboxd_votes": to_int(r["letterboxd_votes"]), "has_lb": bool(r["letterboxd_votes"]),
            "letterboxd_estimate": 0, "imdb_votes": to_int(r["imdb_votes"]),
            "source": "extra", "reasons": [], "canon_lists": [], "note": "",
        }
    n_canon_only = 0
    for r in read(CANON):
        t = r["tconst"]
        if not t:
            continue
        if t not in films:
            n_canon_only += 1
            films[t] = {
                "key": t, "tconst": t, "tmdb_id": "", "wikidata": "", "title": r["title"], "year": r["year"],
                "title_type": "", "mdblist_country": "", "countries": [], "letterboxd_votes": 0, "has_lb": False,
                "letterboxd_estimate": 0, "imdb_votes": 0, "source": "canon_only",
                "reasons": [], "canon_lists": [], "note": "not a film candidate (canon list only)",
            }
        if r["list"] not in films[t]["canon_lists"]:
            films[t]["canon_lists"].append(r["list"])

    # main bar, gap rule, canon
    for f in films.values():
        if f["letterboxd_votes"] >= args.min_letterboxd:
            f["reasons"].append("letterboxd")
        elif not f["has_lb"] and f["letterboxd_estimate"] >= args.min_letterboxd:
            f["reasons"].append("gap")
        if f["canon_lists"]:
            f["reasons"].append("canon")

    # regional top-up (canon-only films are not candidates and take no part)
    cells = collections.defaultdict(list)
    for f in films.values():
        y = to_int(f["year"])
        if f["source"] == "canon_only" or not y:
            continue
        for c in dict.fromkeys(f["countries"]):
            if c:
                cells[(c, y // 10 * 10)].append(f)
    low_floor_adds = set()
    for (c, d), cell in cells.items():
        floor = args.floor_low if original[c] < args.undercovered else args.floor
        cell.sort(key=lambda f: -f["letterboxd_votes"])
        take = max(args.topup_min, math.ceil(args.topup_share * len(cell)))
        for f in cell[:take]:
            if f["letterboxd_votes"] >= floor:
                if "topup" not in f["reasons"]:
                    f["reasons"].append("topup")
                if f["letterboxd_votes"] < args.floor:
                    low_floor_adds.add(f["key"])
    for f in films.values():  # keep the reasons in a fixed order
        f["reasons"] = [r for r in REASONS if r in f["reasons"]]

    selected = sorted((f for f in films.values() if f["reasons"]),
                      key=lambda f: (-f["letterboxd_votes"], -f["letterboxd_estimate"], f["key"]))
    with open(OUT, "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=COLS)
        w.writeheader()
        for f in selected:
            row = {c: f[c] for c in COLS}
            row["countries"] = "|".join(c for c in dict.fromkeys(f["countries"]) if c)
            row["reasons"] = ";".join(f["reasons"])
            row["canon_lists"] = "|".join(f["canon_lists"])
            row["letterboxd_votes"] = f["letterboxd_votes"] if f["has_lb"] else ""
            row["letterboxd_estimate"] = f["letterboxd_estimate"] or ""
            w.writerow(row)

    # ---------------------------------------------------------------- report
    under = {c for c, n in original.items() if n < args.undercovered and c}
    under |= {c for (c, _d) in cells if original[c] < args.undercovered}
    print(f"films: {len(films)} ({len(films) - n_extra - n_canon_only} candidates, {n_extra} extra, "
          f"{n_canon_only} canon-only); under-covered countries (< {args.undercovered} original candidates, "
          f"incl. those with none): {len(under)}")
    print(f"selected: {len(selected)}")
    print("  by reason (any):", dict(collections.Counter(r for f in selected for r in f["reasons"])))
    print("  by reason combination:", dict(collections.Counter(";".join(f["reasons"]) for f in selected).most_common()))
    main_bar = [f for f in selected if "letterboxd" in f["reasons"]]
    add_gap = [f for f in selected if "gap" in f["reasons"]]
    add_canon = [f for f in selected if "canon" in f["reasons"] and not {"letterboxd", "gap"} & set(f["reasons"])]
    add_topup = [f for f in selected if f["reasons"] == ["topup"]]
    topup_new = [f for f in selected if "topup" in f["reasons"] and not {"letterboxd", "gap"} & set(f["reasons"])]
    print(f"  incremental: Letterboxd >= {args.min_letterboxd:,} {len(main_bar)} · + gap {len(add_gap)} · "
          f"+ canon {len(add_canon)} ({sum(f['source'] == 'canon_only' for f in add_canon)} not candidates) · "
          f"+ top-up only {len(add_topup)}")
    afr = [f for f in topup_new if AFRICA & set(f["countries"])]
    ssa = [f for f in topup_new if (AFRICA - NORTH_AFRICA) & set(f["countries"])]
    print(f"  top-up picks below the Letterboxd bar: {len(topup_new)} (of them also canon: "
          f"{sum('canon' in f['reasons'] for f in topup_new)}); African {len(afr)} (sub-Saharan {len(ssa)}); "
          f"via the low floor (100-999 ratings): {len(low_floor_adds)}")
    print(f"  by title type:", dict(collections.Counter(f["title_type"] or "?" for f in selected).most_common()))
    first = lambda f: next((c for c in f["countries"] if c), "?")  # noqa: E731
    by_c = collections.Counter(first(f) for f in selected)
    print("  by country (first regional country; total / added by top-up below the bar):")
    tc = collections.Counter(first(f) for f in topup_new)
    print("    " + " · ".join(f"{c} {n} (+{tc[c]})" for c, n in by_c.most_common(40)))
    print(f"    ... {len(by_c)} countries in all")
    dec = collections.Counter((to_int(f["year"]) // 10 * 10) if to_int(f["year"]) else "?" for f in selected)
    print("  by decade:", " · ".join(f"{d}s {n}" for d, n in sorted(dec.items(), key=lambda x: str(x[0]))))
    reg = collections.Counter()
    for f in selected:
        cs = set(f["countries"])
        reg["Africa"] += bool(cs & AFRICA)
    print(f"  African films selected (any regional country in Africa): {reg['Africa']}")

    gaps_review = sorted((f for f in films.values() if f["source"] == "candidates" and not f["has_lb"]
                          and f["imdb_votes"] >= args.review_imdb and not f["letterboxd_estimate"]),
                         key=lambda f: -f["imdb_votes"])
    print(f"manual-review gap films (no Letterboxd figure, no estimate, >= {args.review_imdb:,} IMDb votes): "
          f"{len(gaps_review)}; selected through canon: {sum(bool(f['reasons']) for f in gaps_review)}")
    print("    " + "; ".join(f"{f['title']} ({f['year']}, {f['imdb_votes']:,})" for f in gaps_review))

    print("spot checks:")
    for key, label in SPOT.items():
        f = films.get(key)
        if not f:
            print(f"    {label}: not a candidate")
            continue
        print(f"    {label} ({f['year']}) {key} {'|'.join(c for c in f['countries'] if c) or '?'} "
              f"LB {f['letterboxd_votes'] if f['has_lb'] else '-'}: {';'.join(f['reasons']) or 'NOT SELECTED'}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    sys.exit(main())
