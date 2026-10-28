"""Fit the modern-era depth model on its own reference and apply it to the nine regions.

visual-art-plan.md §2.4 (decided 2026-10-28): the modern pass (active 1860-1960) is
calibrated on its own reference, built from data by build_modern_reference.py
(data/interim/modern_reference_candidate.csv; seeds/visual-art/modern_1860-1960_depth_reference.txt).

- Rows: every modern_<region> pool (pool_modern_*.csv), plus the reference artists
  below the pool rule as positives (refextra_* files from modern_reference_extras.py,
  until build_pool.py adds them itself on the next pool rebuild). Features are the usual
  within-cell percentiles, computed inside each region (depth_model.load_features,
  assign_cells, percentile_matrix), so each modernism is ranked against its peers.
- Positives: reference artists, in whichever regional pool they appear (an émigré
  pooled in two regions is a positive in both). Training rows: the painting cells
  plus every reference artist, as in depth_model.fit.
- One NonNegativeLogit over all nine regions. Candidate cutoffs at 90 / 85 / 80%
  out-of-fold reference recall (5-fold), reviewed on the marginal artists each adds.
  Decided 2026-10-28: 80%, plus a Europe-only selection guard (regions.py); a refit
  keeps that decision and recomputes the 80% cutoff. Selection is written by
  `depth_model.py apply --model modern_1860-1960` per region.
- Selection is depth_model.select (every reference artist, plus pool-rule artists at
  or above the cutoff after the art_occ_share factor, architecture excluded).

Output: pipelines/visual_art/models/modern_1860-1960.json (coefficients, candidate cutoffs)
        data/interim/visual_art/modern_cutoff_review.csv (30 marginal artists per region
        and candidate cutoff, for Europe, North America, Latin America, East Asia,
        Sub-Saharan Africa)
The shared scores_modern_<region>.csv (Europe-model scores) are left untouched.

Usage: python3 pipelines/visual_art/fit_modern.py
"""
import argparse
import collections
import csv
import json
import os
import sys

import numpy as np
from sklearn.model_selection import StratifiedKFold

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_modern_reference as bmr  # noqa: E402
import depth_model as dm  # noqa: E402
from reference import load_reference  # noqa: E402
from regions import MODERN_REGIONS, REGIONS  # noqa: E402

NAME = "modern_1860-1960"
ALL = [f"modern_{r}" for r in MODERN_REGIONS]
# Spot checks: modernists across regions, by QID (some pool labels are empty).
SPOT = {
    'Abanindranath Tagore': 'Q691796', 'Nandalal Bose': 'Q3348980', 'Jamini Roy': 'Q3595454',
    'Amrita Sher-Gil': 'Q150312', 'Rabindranath Tagore': 'Q7241', 'M. F. Husain': 'Q558522',
    'S. H. Raza': 'Q3105774', 'F. N. Souza': 'Q5482041', 'Ramkinkar Baij': 'Q3345966',
    'Benode Behari Mukherjee': 'Q380226', 'Ben Enwonwu': 'Q4885605', 'Uche Okeke': 'Q15461959',
    'Bruce Onobrakpeya': 'Q3645490', 'Gerard Sekoto': 'Q3103960', 'Irma Stern': 'Q281203',
    'Ibrahim El-Salahi': 'Q2662098', 'Qi Baishi': 'Q369608', 'Xu Beihong': 'Q714152',
    'Lin Fengmian': 'Q986362', 'Pan Yuliang': 'Q148400', 'Wu Changshuo': 'Q715400',
    'Gao Jianfu': 'Q3083171', 'Yokoyama Taikan': 'Q2034441', 'Kishida Ryusei': 'Q3021493',
    'Tsuguharu Foujita': 'Q261846', 'Lee Jung-seob': 'Q3789181', 'Diego Rivera': 'Q171128',
    'Frida Kahlo': 'Q5588', 'Jose Clemente Orozco': 'Q332041', 'Tarsila do Amaral': 'Q466627',
    'Wifredo Lam': 'Q465342', 'Joaquin Torres-Garcia': 'Q520713', 'Mahmoud Mokhtar': 'Q1459134',
    'Mahmoud Said': 'Q6734398', 'Jewad Selim': 'Q2720307', 'Shakir Hassan Al Said': 'Q7462952',
    'Albert Namatjira': 'Q560086', 'Affandi': 'Q2826050', 'Fernando Amorsolo': 'Q1943091',
    'Sidney Nolan': 'Q381031', 'Tom Roberts': 'Q1291901', 'Claude Monet': 'Q296',
    'Pablo Picasso': 'Q5593', "Georgia O'Keeffe": 'Q46408', 'Ivan Shishkin': 'Q193064',
}


_load_table = dm.load_table


def load_table_with_extras(path, key="qid"):
    """depth_model.load_table plus the refextra_* side file next to it, if any
    (modern_reference_extras.py: reference artists below the pool rule)."""
    table = _load_table(path, key)
    extra = os.path.join(os.path.dirname(path), "refextra_" + os.path.basename(path))
    if os.path.exists(extra):
        table.update({k: v for k, v in _load_table(extra, key).items() if k not in table})
    return table


dm.load_table = load_table_with_extras


RECALLS = (0.90, 0.85, 0.80)
REVIEW_REGIONS = ["modern_europe", "modern_north_america", "modern_latin_america", "modern_east_asia",
                  "modern_subsaharan_africa"]
N_SAMPLE = 30


def side_info():
    """Labels (pool labels can be empty), movement labels, Tate works and MoMA membership."""
    labels = {}
    for name in ("artists.json",):
        for q, r in json.load(open(os.path.join(bmr.RAW, name), encoding="utf-8")).items():
            labels[q] = r["label"]
    fb = os.path.join(bmr.RAW, "fallback_labels.json")
    if os.path.exists(fb):
        labels.update({q: l for q, l in json.load(open(fb, encoding="utf-8")).items() if not labels.get(q)})
    tsv = os.path.join(dm.DATA, "labels.tsv")
    mlabels = dict(line.rstrip("\n").split("\t", 1) for line in open(tsv, encoding="utf-8") if "\t" in line)
    tate_works, tate_by_name = bmr.load_tate()
    moma = bmr.load_moma()
    return labels, mlabels, tate_works, tate_by_name, moma


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    args = ap.parse_args()
    ref_rows = [r for reg in ALL for r in load_reference(REGIONS[reg]) if r["qid"]]
    ref = {r["qid"] for r in ref_rows}
    with open(os.path.join(dm.ROOT, REGIONS[ALL[0]]["reference_qids"]), encoding="utf-8") as f:
        ref_csv = list(csv.DictReader(f))

    data = {}
    for region in ALL:
        rows = dm.load_features(region)
        for r in rows:
            r["is_reference"] = int(r["qid"] in ref)
        dm.assign_cells(rows)
        data[region] = (rows, dm.percentile_matrix(rows))
    rows = [row for reg in ALL for row in data[reg][0]]
    X = np.vstack([data[reg][1] for reg in ALL])
    y = np.array([r["is_reference"] for r in rows])
    train = np.array([r["medium"] in REGIONS[ALL[0]]["train_media"] or bool(r["is_reference"]) for r in rows], dtype=bool)
    print(f"{len(rows)} artists in {len(ALL)} regions, {int(y.sum())} reference positives "
          f"({len(ref)} reference QIDs); training on {int(train.sum())}")

    model = dm.NonNegativeLogit().fit(X[train], y[train])
    oof = np.zeros(len(y))
    ti = np.flatnonzero(train)
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=0).split(X[train], y[train]):
        oof[ti[te]] = dm.NonNegativeLogit().fit(X[train][tr], y[train][tr]).predict_proba(X[train][te])[:, 1]
    scores = model.predict_proba(X)[:, 1]
    cutoffs = {rc: float(np.quantile(oof[y == 1], 1 - rc)) for rc in RECALLS}
    print("coefficients (within-cell percentiles):")
    for f, c in sorted(zip(dm.FEATURES, model.coef_[0]), key=lambda t: -t[1]):
        print(f"  {f:20} {c:+.2f}")
    print(f"  {'intercept':20} {model.intercept_[0]:+.2f}")
    for rc, cut in cutoffs.items():
        print(f"cutoff for {rc:.0%} out-of-fold recall: {cut:.4f} (in-sample recall {(scores[y == 1] >= cut).mean():.1%})")

    # Selected totals per region at each candidate cutoff (nothing is written to the
    # shared scores_modern_*.csv: the cutoff is chosen on review).
    region_scores = {reg: model.predict_proba(data[reg][1])[:, 1] for reg in ALL}
    print(f"\n{'region':28} {'pool':>6} {'ref':>5} " + " ".join(f"{'sel@' + format(rc, '.0%'):>9}" for rc in RECALLS)
          + f" {'Europe model':>12}")
    totals = collections.Counter()
    for reg in ALL:
        rws, sr = data[reg][0], region_scores[reg]
        keep = os.path.join(dm.DATA, f"scores_{reg}.csv")
        with open(keep, encoding="utf-8") as f:
            old = sum(r["selected"] == "1" for r in csv.DictReader(f))
        sels = [int(dm.select(rws, sr, cutoffs[rc], REGIONS[reg]).sum()) for rc in RECALLS]
        for rc, n in zip(RECALLS, sels):
            totals[rc] += n
        totals["old"] += old
        print(f"{reg:28} {len(rws):>6} {sum(r['is_reference'] for r in rws):>5} "
              + " ".join(f"{n:>9}" for n in sels) + f" {old:>12}")
    print(f"{'total':28} {'':>6} {'':>5} " + " ".join(f"{totals[rc]:>9}" for rc in RECALLS) + f" {totals['old']:>12}")

    # Core of each movement: the top third (by rank) of the reference artists listed under it.
    best = {}
    for r, s in zip(rows, scores):
        best[r["qid"]] = max(best.get(r["qid"], 0), s)
    by_mv = collections.defaultdict(list)
    for r in ref_csv:
        by_mv[(r["movement_region"], r["movement"])].append(r)
    core = []
    for (mreg, mv), rs in by_mv.items():
        rs.sort(key=lambda r: int(r["rank_in_movement"]))
        core += [(mreg, mv, r["qid"]) for r in rs[:max(1, -(-len(rs) // 3))] if r["qid"] in best]
    print("\nrecall of each movement's core (top third of its listed reference artists), by movement region:")
    print(f"  {'region':20} {'core':>5} " + " ".join(f"{'@' + format(rc, '.0%'):>7}" for rc in RECALLS))
    for mreg in sorted({c[0] for c in core}):
        cs = [c for c in core if c[0] == mreg]
        print(f"  {mreg:20} {len(cs):>5} " + " ".join(
            f"{sum(best[q] >= cutoffs[rc] for _, _, q in cs) / len(cs):>7.1%}" for rc in RECALLS))
    print(f"  {'all':20} {len(core):>5} " + " ".join(
        f"{sum(best[q] >= cutoffs[rc] for _, _, q in core) / len(core):>7.1%}" for rc in RECALLS))
    weak = collections.defaultdict(list)
    for mreg, mv, q in core:
        weak[(mreg, mv)].append(best[q] >= cutoffs[0.80])
    worst = sorted(((sum(v) / len(v), len(v), k) for k, v in weak.items() if len(v) >= 3))[:12]
    print("  movements whose core is least recovered even at 80%: "
          + "; ".join(f"{mv} ({mreg}) {share:.0%} of {n}" for share, n, (mreg, mv) in worst))

    # Review samples: the marginal band just above each cutoff (lowest-scoring 10% of
    # the non-reference artists it selects), 30 per region and band, evenly spaced.
    labels, mlabels, tate_works, tate_by_name, moma = side_info()
    m_q, m_u, m_n = moma if moma else (set(), set(), set())
    pools = {}
    for reg in REVIEW_REGIONS:
        with open(os.path.join(dm.DATA, f"pool_{reg}.csv"), encoding="utf-8") as f:
            pools.update({r["qid"]: r for r in csv.DictReader(f)})
    out = os.path.join(dm.DATA, "modern_cutoff_review.csv")
    cols = ["region", "recall_band", "qid", "label", "birth", "medium", "movements", "sitelinks", "pageviews",
            "n_museums", "tate", "moma", "score"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for reg in REVIEW_REGIONS:
            rws, sr = data[reg][0], region_scores[reg]
            excl = set(REGIONS[reg].get("model_excluded_media", []))
            adj = [(s * dm.art_factor(r), r) for r, s in zip(rws, sr)
                   if not r["is_reference"] and r["in_pool_rule"] and r["medium"] not in excl]
            for rc in RECALLS:
                sel = sorted((a for a in adj if a[0] >= cutoffs[rc]), key=lambda t: t[0])
                band = sel[:max(N_SAMPLE, len(sel) // 10)]
                idx = np.unique(np.linspace(0, len(band) - 1, min(N_SAMPLE, len(band))).round().astype(int)) if band else []
                for i in idx:
                    s, r = band[i]
                    p = pools.get(r["qid"], {})
                    label = r["label"] or labels.get(r["qid"], "")
                    tid = next((x for x in [tate_by_name.get((bmr.name_key(label), str(r["birth"] or "")))] if x), None)
                    w.writerow({
                        "region": reg[7:], "recall_band": f"{rc:.0%}", "qid": r["qid"], "label": label,
                        "birth": r["birth"], "medium": r["medium"],
                        "movements": "|".join(mlabels.get(m, m) for m in p.get("movements", "").split("|") if m),
                        "sitelinks": int(r["sitelinks"]), "pageviews": int(r["pageviews"]),
                        "n_museums": int(r["n_museums"]),
                        "tate": tate_works.get(tid, 0) if tid else ("id" if "P2741" in p.get("authority_ids", "") else 0),
                        "moma": int(r["qid"] in m_q or (bmr.name_key(label), str(r["birth"] or "")) in m_n
                                    or "P2174" in p.get("authority_ids", "")),
                        "score": round(float(s), 4),
                    })
    print(f"\nwrote {out}")

    os.makedirs(dm.MODELS, exist_ok=True)
    path = os.path.join(dm.MODELS, f"{NAME}.json")
    decided = {}
    if os.path.exists(path):
        prev = json.load(open(path, encoding="utf-8"))
        if str(prev.get("cutoff_status", "")).startswith("decided"):
            # Keep the decided recall level (now 80%) and its guard; the cutoff value
            # follows the refit at that recall.
            rc = prev["recall_target"]
            decided = {"cutoff": round(float(np.quantile(oof[y == 1], 1 - rc)), 6), "recall_target": rc,
                       "cutoff_status": prev["cutoff_status"], "selection_guard": prev.get("selection_guard")}
    json.dump({
        "fitted_on": ALL, "features": dm.FEATURES, "feature_transform": "within-cell mid-rank percentile (per region)",
        "coef": [round(float(c), 6) for c in model.coef_[0]], "intercept": round(float(model.intercept_[0]), 6),
        "cutoff": None, "cutoff_status": "under review (modern_cutoff_review.csv); candidates by out-of-fold recall",
        "candidate_cutoffs": {f"{rc:.2f}": round(c, 6) for rc, c in cutoffs.items()},
        "selected_at_candidates": {f"{rc:.2f}": totals[rc] for rc in RECALLS},
        "reference": REGIONS[ALL[0]]["reference_qids"], "n_artists": len(rows), "n_reference": int(y.sum()),
        **decided,
    }, open(path, "w"), indent=1)
    print(f"wrote {os.path.join(dm.MODELS, NAME + '.json')}")

    print("\nspot checks: best score over the artist's regions, selected at 90 / 85 / 80% recall?")
    for name, q in SPOT.items():
        if q not in best:
            print(f"  {name:28} not in any modern pool")
            continue
        flags = " ".join("y" if best[q] >= cutoffs[rc] else "n" for rc in RECALLS)
        print(f"  {name:28} {best[q]:.3f} {flags}{'  (reference)' if q in ref else ''}")


if __name__ == "__main__":
    main()
