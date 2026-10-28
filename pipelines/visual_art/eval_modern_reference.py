"""Experimental: evaluate the modern reference candidate against the modern pools.

Reads data/interim/modern_reference_candidate.csv (build_modern_reference.py) and
the modern pass outputs (pool_modern_<r>.csv, scores_modern_<r>.csv from
run_modern.sh), then reports:
  1. per region: reference artists, how many are in the region's pool, and the
     Europe 1400-1900 model's recall of them at its cutoff ('selected');
  2. a refit: depth_model.NonNegativeLogit fitted on modern_europe +
     modern_north_america with the candidate as positives (painting cells plus
     every reference artist, as in depth_model.fit), the cutoff at --recall of the
     training positives, and the cutoff applied to all nine regions.
     Variant "no_tate_moma_ids" drops the Tate (P2741) and MoMA (P2174) IDs from
     n_regional_ids, since the reference is ranked partly on Tate holdings.

Nothing is written to pipelines/visual_art/models/; the refit coefficients go to
data/interim/visual_art/model_modern_refit_<variant>.json.

Usage: python3 pipelines/visual_art/eval_modern_reference.py [--recall 0.9]
"""
import argparse
import copy
import csv
import json
import os
import sys

import numpy as np
from sklearn.model_selection import StratifiedKFold

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import depth_model as dm  # noqa: E402
from regions import MODERN_REGIONS, REGIONS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CANDIDATE = os.path.join(ROOT, "data", "interim", "modern_reference_candidate.csv")
TRAIN = ["modern_europe", "modern_north_america"]
ALL = [f"modern_{r}" for r in MODERN_REGIONS]


def load_region(region, ref, drop_ids=()):
    saved = REGIONS[region]
    cfg = copy.deepcopy(saved)
    cfg["authority_ids"] = [p for p in cfg["authority_ids"] if p not in drop_ids]
    REGIONS[region] = cfg
    try:
        rows = dm.load_features(region)
    finally:
        REGIONS[region] = saved
    for r in rows:
        r["is_reference"] = int(r["qid"] in ref)
    dm.assign_cells(rows)
    return rows, dm.percentile_matrix(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--recall", type=float, default=0.90)
    args = ap.parse_args()
    ref = {}
    with open(CANDIDATE, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ref[r["qid"]] = r
    available = [r for r in ALL if os.path.exists(os.path.join(dm.DATA, f"scores_{r}.csv"))]
    print(f"{len(ref)} reference artists; scored regions: {', '.join(available)}")

    # 1. Europe-model recall of the reference, per region.
    pooled = {}
    print(f"\n{'region':28} {'ref':>5} {'in pool':>8} {'pool-rule':>9} {'selected':>8} {'recall':>7} {'region selects':>14}")
    for region in available:
        name = region[len("modern_"):]
        with open(os.path.join(dm.DATA, f"scores_{region}.csv"), encoding="utf-8") as f:
            sc = {r["qid"]: r for r in csv.DictReader(f)}
        for q in sc:
            pooled.setdefault(q, region)
        mine = [q for q, r in ref.items() if r["region"] == name]
        inpool = [q for q in mine if q in sc]
        rule = [q for q in inpool if sc[q]["in_pool_rule"] == "1"]
        sel = [q for q in inpool if sc[q]["selected"] == "1"]
        n_sel = sum(r["selected"] == "1" for r in sc.values())
        print(f"{region:28} {len(mine):>5} {len(inpool):>8} {len(rule):>9} {len(sel):>8} "
              f"{len(sel) / max(1, len(mine)):>7.1%} {n_sel:>14}")
    missing = [r for q, r in ref.items() if q not in pooled and f"modern_{r['region']}" in available]
    if missing:
        print(f"\n{len(missing)} reference artists in no scored pool, e.g.: "
              + ", ".join(f"{r['name']} ({r['region']}, {r['movement']})" for r in missing[:25]))

    # 2. Refit on Europe + North America.
    if not all(r in available for r in TRAIN):
        print("\nrefit skipped: training regions not scored yet")
        return
    for variant, drop in (("all_features", ()), ("no_tate_moma_ids", ("P2741", "P2174"))):
        data = {r: load_region(r, ref, drop) for r in available}
        X = np.vstack([data[r][1] for r in TRAIN])
        rows = [row for r in TRAIN for row in data[r][0]]
        y = np.array([row["is_reference"] for row in rows])
        train = np.array([row["medium"] == "painting" or row["is_reference"] for row in rows], dtype=bool)
        model = dm.NonNegativeLogit().fit(X[train], y[train])
        s = model.predict_proba(X)[:, 1]
        cutoff = float(np.quantile(s[y == 1], 1 - args.recall))
        oof = np.zeros(len(y))
        ti = np.flatnonzero(train)
        for tr, te in StratifiedKFold(5, shuffle=True, random_state=0).split(X[train], y[train]):
            oof[ti[te]] = dm.NonNegativeLogit().fit(X[train][tr], y[train][tr]).predict_proba(X[train][te])[:, 1]
        print(f"\nrefit [{variant}] on {' + '.join(TRAIN)}: {len(rows)} artists, {int(y.sum())} positives, "
              f"training on {int(train.sum())}")
        for f_, c in sorted(zip(dm.FEATURES, model.coef_[0]), key=lambda t: -t[1]):
            print(f"  {f_:20} {c:+.2f}")
        print(f"  {'intercept':20} {model.intercept_[0]:+.2f}")
        print(f"  cutoff for {args.recall:.0%} recall: {cutoff:.4f}; out-of-fold recall at that cutoff "
              f"{(oof[y == 1] >= cutoff).mean():.1%}")
        print(f"  {'region':28} {'pool':>6} {'ref':>5} {'ref>=cut':>8} {'selected':>8} {'Europe-model sel.':>17}")
        for region in available:
            rws, Xr = data[region]
            sr = model.predict_proba(Xr)[:, 1]
            sel = dm.select(rws, sr, cutoff, REGIONS[region])
            refidx = [i for i, r in enumerate(rws) if r["is_reference"]]
            with open(os.path.join(dm.DATA, f"scores_{region}.csv"), encoding="utf-8") as f:
                old = sum(r["selected"] == "1" for r in csv.DictReader(f))
            print(f"  {region:28} {len(rws):>6} {len(refidx):>5} {sum(sr[i] >= cutoff for i in refidx):>8} "
                  f"{int(sel.sum()):>8} {old:>17}")
        out = os.path.join(dm.DATA, f"model_modern_refit_{variant}.json")
        json.dump({"fitted_on": TRAIN, "features": dm.FEATURES, "dropped_ids": list(drop),
                   "coef": [round(float(c), 6) for c in model.coef_[0]],
                   "intercept": round(float(model.intercept_[0]), 6), "recall_target": args.recall,
                   "cutoff": round(cutoff, 6), "n_reference": int(y.sum())}, open(out, "w"), indent=1)
        print(f"  wrote {out}")


if __name__ == "__main__":
    main()
