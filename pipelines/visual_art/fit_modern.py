"""Fit the modern-era depth model on its own reference and apply it to the nine regions.

visual-art-plan.md §2.4 (decided 2026-10-28): the modern pass (active 1860-1960) is
calibrated on its own reference, built from data by build_modern_reference.py
(data/interim/modern_reference_candidate.csv; seeds/visual-art/modern_1860-1960_depth_reference.txt).

- Rows: every modern_<region> pool (pool_modern_*.csv, with the reference artists
  below the pool rule added as positives by build_pool.py). Features are the usual
  within-cell percentiles, computed inside each region (depth_model.load_features,
  assign_cells, percentile_matrix), so each modernism is ranked against its peers.
- Positives: reference artists, in whichever regional pool they appear (an émigré
  pooled in two regions is a positive in both). Training rows: the painting cells
  plus every reference artist, as in depth_model.fit.
- One NonNegativeLogit over all nine regions. The cutoff is the 10th percentile of
  the reference artists' 5-fold out-of-fold scores (90% out-of-fold recall).
- Selection is depth_model.select (every reference artist, plus pool-rule artists at
  or above the cutoff after the art_occ_share factor, architecture excluded).

Output: pipelines/visual_art/models/modern_1860-1960.json
        data/interim/visual_art/scores_modern_<region>.csv (overwritten; the previous
        Europe-model scores are kept once as scores_modern_<region>_europe_model.csv)

Usage: python3 pipelines/visual_art/fit_modern.py [--recall 0.9]
"""
import argparse
import csv
import json
import os
import shutil
import sys

import numpy as np
from sklearn.model_selection import StratifiedKFold

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import depth_model as dm  # noqa: E402
from reference import load_reference  # noqa: E402
from regions import MODERN_REGIONS, REGIONS  # noqa: E402

NAME = "modern_1860-1960"
ALL = [f"modern_{r}" for r in MODERN_REGIONS]
# Spot checks: modernists across regions (labels as in the pools).
SPOT = [
    "Abanindranath Tagore", "Nandalal Bose", "Jamini Roy", "Amrita Sher-Gil", "Rabindranath Tagore",
    "M. F. Husain", "S. H. Raza", "Francis Newton Souza", "Ramkinkar Baij", "Benode Behari Mukherjee",
    "Ben Enwonwu", "Uche Okeke", "Bruce Onobrakpeya", "Yusuf Grillo", "Gerard Sekoto", "Irma Stern",
    "Ibrahim El-Salahi", "Qi Baishi", "Xu Beihong", "Lin Fengmian", "Pan Yuliang", "Wu Changshuo",
    "Gao Jianfu", "Yokoyama Taikan", "Kishida Ryūsei", "Tsuguharu Foujita", "Lee Jung-seob",
    "Diego Rivera", "Frida Kahlo", "José Clemente Orozco", "Tarsila do Amaral", "Wifredo Lam",
    "Joaquín Torres García", "Mahmoud Mokhtar", "Mahmoud Saïd", "Jewad Selim", "Shakir Hassan Al Said",
    "Albert Namatjira", "Affandi", "Fernando Amorsolo", "Sidney Nolan", "Tom Roberts",
    "Claude Monet", "Pablo Picasso", "Georgia O'Keeffe", "Ivan Shishkin",
]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--recall", type=float, default=0.90)
    args = ap.parse_args()
    ref = {r["qid"] for reg in ALL for r in load_reference(REGIONS[reg]) if r["qid"]}

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
    cutoff = float(np.quantile(oof[y == 1], 1 - args.recall))
    scores = model.predict_proba(X)[:, 1]
    print("coefficients (within-cell percentiles):")
    for f, c in sorted(zip(dm.FEATURES, model.coef_[0]), key=lambda t: -t[1]):
        print(f"  {f:20} {c:+.2f}")
    print(f"  {'intercept':20} {model.intercept_[0]:+.2f}")
    print(f"cutoff (90% out-of-fold recall): {cutoff:.4f}; in-sample reference recall at it "
          f"{(scores[y == 1] >= cutoff).mean():.1%}")

    os.makedirs(dm.MODELS, exist_ok=True)
    n_sel = 0
    print(f"\n{'region':28} {'pool':>6} {'ref':>5} {'ref>=cut':>8} {'selected':>8} {'Europe model':>12}")
    old_sel, new_sel = {}, {}
    for region in ALL:
        rws, Xr = data[region]
        sr = model.predict_proba(Xr)[:, 1]
        sel = dm.select(rws, sr, cutoff, REGIONS[region])
        cur = os.path.join(dm.DATA, f"scores_{region}.csv")
        keep = os.path.join(dm.DATA, f"scores_{region}_europe_model.csv")
        if os.path.exists(cur) and not os.path.exists(keep):
            shutil.copy(cur, keep)
        old = {}
        if os.path.exists(keep):
            with open(keep, encoding="utf-8") as f:
                old = {r["qid"]: r["selected"] == "1" for r in csv.DictReader(f)}
        refidx = [i for i, r in enumerate(rws) if r["is_reference"]]
        print(f"{region:28} {len(rws):>6} {len(refidx):>5} {sum(sr[i] >= cutoff for i in refidx):>8} "
              f"{int(sel.sum()):>8} {sum(old.values()):>12}")
        n_sel += int(sel.sum())
        dm.write_scores(region, rws, sr, cutoff)
        for r, s, c in zip(rws, sr, sel):
            new_sel.setdefault(r["label"], []).append((region, c, s, r["is_reference"]))
            old_sel.setdefault(r["label"], []).append(old.get(r["qid"]))
    print(f"total selected: {n_sel}")

    json.dump({
        "fitted_on": ALL, "features": dm.FEATURES, "feature_transform": "within-cell mid-rank percentile (per region)",
        "coef": [round(float(c), 6) for c in model.coef_[0]], "intercept": round(float(model.intercept_[0]), 6),
        "recall_target": args.recall, "cutoff": round(cutoff, 6), "cutoff_method": "out-of-fold (5-fold) reference recall",
        "reference": "data/interim/modern_reference_candidate.csv",
        "n_artists": len(rows), "n_reference": int(y.sum()), "n_selected": n_sel,
    }, open(os.path.join(dm.MODELS, f"{NAME}.json"), "w"), indent=1)
    print(f"wrote {os.path.join(dm.MODELS, NAME + '.json')}")

    print("\nspot checks (region: modern model selected? score / Europe model selected?):")
    for name in SPOT:
        if name not in new_sel:
            print(f"  {name:28} not in any modern pool")
            continue
        parts = [f"{reg[7:]}: {'yes' if c else 'no'} {s:.3f}{' ref' if isref else ''} / {'yes' if o else 'no' if o is not None else '-'}"
                 for (reg, c, s, isref), o in zip(new_sel[name], old_sel[name])]
        print(f"  {name:28} " + "; ".join(parts))


if __name__ == "__main__":
    main()
