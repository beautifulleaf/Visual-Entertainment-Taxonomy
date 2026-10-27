"""Artist-depth model: learn "reference-list depth" and apply it region by region.

visual-art-plan.md §2.1. The reference list (seeds/visual-art/*_depth_reference.txt)
gives the positives; every other pooled artist is unlabelled (treated as negative).
Each feature is converted to a percentile within its region x period cell, so a
model fitted on Europe 1400-1900, where Wikipedia and museum coverage is dense,
can be applied to cells where coverage is thin without emptying them.

  fit    --region R  fit logistic regression on R's pool + reference list, choose
                     the score cutoff that recovers --recall of the reference,
                     save the model to pipelines/visual_art/models/R.json
  apply  --region R --model M  score R's pool with model M and select by its cutoff
                     (for regions that have no reference list yet)

Inputs: data/interim/visual_art/pool_R.csv, holdings.csv, pageviews.csv
Output: data/interim/visual_art/scores_R.csv (all pooled artists, score, selected)
"""
import argparse
import csv
import json
import os
import sys

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reference import load_reference  # noqa: E402
from regions import PERIOD_BUCKET, REGIONS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data", "interim", "visual_art")
MODELS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

FEATURES = [
    "sitelinks", "pageviews", "museum_objects", "n_museums", "met_timeline_works",
    "has_ulan", "has_wikiart", "has_rkd", "has_artuk", "n_other_ids",
]
MIN_CELL = 50  # cells smaller than this are merged with the following period


def num(v):
    return float(v) if v not in (None, "") else 0.0


def load_table(path, key="qid"):
    if not os.path.exists(path):
        sys.exit(f"missing {path}; run the earlier pipeline steps first")
    with open(path, encoding="utf-8") as f:
        return {r[key]: r for r in csv.DictReader(f)}


def load_features(region):
    pool = load_table(os.path.join(DATA, f"pool_{region}.csv"))
    holdings = load_table(os.path.join(DATA, "holdings.csv"))
    views = load_table(os.path.join(DATA, "pageviews.csv"))
    rows = []
    for q, p in pool.items():
        h, v = holdings.get(q, {}), views.get(q, {})
        rows.append({
            "qid": q, "label": p["label"], "birth": p["birth"], "period": p["period"],
            "in_pool_rule": int(p["in_pool_rule"]), "is_reference": int(p["is_reference"]),
            "sitelinks": num(p["sitelinks"]),
            "pageviews": num(v.get("pageviews")),
            "museum_objects": num(h.get("met_objects")) + num(h.get("aic_objects")) + num(h.get("cma_objects")),
            "n_museums": num(h.get("n_museums")),
            "met_timeline_works": num(h.get("met_timeline_works")),
            "has_ulan": float(bool(p["ulan_id"])), "has_wikiart": float(bool(p["wikiart_id"])),
            "has_rkd": float(bool(p["rkd_id"])), "has_artuk": float(bool(p["artuk_id"])),
            "n_other_ids": num(p["n_other_ids"]),
        })
    return rows


def assign_cells(rows):
    """Cell = period bucket, with small buckets merged into the following one."""
    periods = sorted({int(r["period"]) for r in rows if r["period"]})
    sizes = {pd: sum(1 for r in rows if r["period"] and int(r["period"]) == pd) for pd in periods}
    groups = []
    for pd in periods:
        if not groups or sum(sizes[x] for x in groups[-1]) >= MIN_CELL:
            groups.append([])
        groups[-1].append(pd)
    if len(groups) > 1 and sum(sizes[x] for x in groups[-1]) < MIN_CELL:
        groups[-2] += groups.pop()  # a small tail joins the previous cell
    cell_of = {pd: f"{g[0]}-{g[-1] + PERIOD_BUCKET - 1}" for g in groups for pd in g}
    for r in rows:
        r["cell"] = cell_of.get(int(r["period"])) if r["period"] else "undated"


def percentile_matrix(rows):
    """Feature matrix of within-cell mid-rank percentiles (ties share a rank)."""
    X = np.zeros((len(rows), len(FEATURES)))
    cells = {}
    for i, r in enumerate(rows):
        cells.setdefault(r["cell"], []).append(i)
    for idx in cells.values():
        for j, feat in enumerate(FEATURES):
            vals = np.array([rows[i][feat] for i in idx])
            order = np.sort(vals)
            below = np.searchsorted(order, vals, side="left")
            upto = np.searchsorted(order, vals, side="right")
            X[idx, j] = (below + upto) / 2 / len(vals)
    return X


def write_scores(region, rows, scores, cutoff):
    out = os.path.join(DATA, f"scores_{region}.csv")
    cols = ["qid", "label", "birth", "cell", "in_pool_rule", "is_reference", "score", "selected"] + FEATURES
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r, s in sorted(zip(rows, scores), key=lambda t: -t[1]):
            w.writerow({**r, "score": round(float(s), 5), "selected": int(s >= cutoff)})
    return out


def report_cells(rows, scores, cutoff):
    print(f"\n{'cell':12} {'pool':>6} {'ref':>5} {'selected':>8} {'ref recovered':>13}")
    for cell in sorted({r["cell"] for r in rows}):
        idx = [i for i, r in enumerate(rows) if r["cell"] == cell]
        ref = [i for i in idx if rows[i]["is_reference"]]
        sel = sum(1 for i in idx if scores[i] >= cutoff and (rows[i]["in_pool_rule"] or rows[i]["is_reference"]))
        rec = sum(1 for i in ref if scores[i] >= cutoff)
        print(f"{cell:12} {len(idx):>6} {len(ref):>5} {sel:>8} {rec:>6}/{len(ref):<6}")


def fit(region, recall):
    cfg = REGIONS[region]
    if not cfg.get("reference"):
        sys.exit(f"{region} has no reference list; use `apply --model <fitted region>`")
    rows = load_features(region)
    assign_cells(rows)
    X = percentile_matrix(rows)
    y = np.array([r["is_reference"] for r in rows])
    print(f"{region}: {len(rows)} artists ({sum(r['in_pool_rule'] for r in rows)} by the pool rule), {y.sum()} reference positives")

    model = LogisticRegression(C=1.0, max_iter=2000).fit(X, y)
    scores = model.predict_proba(X)[:, 1]
    cutoff = float(np.quantile(scores[y == 1], 1 - recall))

    # Honest check: out-of-fold scores, same recall target.
    oof = np.zeros(len(y))
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=0).split(X, y):
        oof[te] = LogisticRegression(C=1.0, max_iter=2000).fit(X[tr], y[tr]).predict_proba(X[te])[:, 1]
    oof_cut = float(np.quantile(oof[y == 1], 1 - recall))
    in_rule = np.array([r["in_pool_rule"] for r in rows]) == 1

    selected = (scores >= cutoff) & (in_rule | (y == 1))
    print("\ncoefficients (features are within-cell percentiles, 0-1):")
    for f, c in sorted(zip(FEATURES, model.coef_[0]), key=lambda t: -abs(t[1])):
        print(f"  {f:20} {c:+.2f}")
    print(f"  {'intercept':20} {model.intercept_[0]:+.2f}")
    print(f"\ncutoff for {recall:.0%} reference recall: score >= {cutoff:.4f}")
    print(f"  selects {int(selected.sum())} artists ({int((selected & (y == 0)).sum())} beyond the reference list)")
    print(f"  pool-rule artists at or above the cutoff: {int((in_rule & (scores >= cutoff)).sum())}")
    print(f"  cross-validated: cutoff {oof_cut:.4f} recovers {recall:.0%} out-of-fold and selects "
          f"{int(((oof >= oof_cut) & (in_rule | (y == 1))).sum())}; the fitted cutoff recovers {(oof[y == 1] >= cutoff).mean():.1%} out-of-fold")
    report_cells(rows, scores, cutoff)

    ref_rows = load_reference(cfg)
    by_q = {r["qid"]: s for r, s in zip(rows, scores)}
    print("\nreference recall by movement:")
    mv = {}
    for r in ref_rows:
        if r["qid"] in by_q:
            mv.setdefault(r["movement"], []).append(by_q[r["qid"]] >= cutoff)
    for m, hits in mv.items():
        print(f"  {m:45} {sum(hits):>4}/{len(hits)}")
    missed = sorted(((s, r["label"]) for r, s in zip(rows, scores) if r["is_reference"] and s < cutoff))
    print(f"\nlowest-scoring reference artists (below cutoff, {len(missed)}): " + ", ".join(f"{n} ({s:.3f})" for s, n in missed[:25]))
    extra = [(s, r["label"], r["birth"]) for r, s in zip(rows, scores) if not r["is_reference"] and r["in_pool_rule"]]
    extra.sort(reverse=True)
    print("\nhighest-scoring artists not on the reference list: " + ", ".join(f"{n} ({b})" for _, n, b in extra[:30]))

    os.makedirs(MODELS, exist_ok=True)
    path = os.path.join(MODELS, f"{region}.json")
    json.dump({
        "fitted_on": region, "features": FEATURES, "feature_transform": "within-cell mid-rank percentile",
        "coef": [round(float(c), 6) for c in model.coef_[0]], "intercept": round(float(model.intercept_[0]), 6),
        "recall_target": recall, "cutoff": round(cutoff, 6),
        "n_artists": len(rows), "n_reference": int(y.sum()), "n_selected": int(selected.sum()),
    }, open(path, "w"), indent=1)
    print(f"\nwrote {path}\nwrote {write_scores(region, rows, scores, cutoff)}")


def apply(region, model_name):
    m = json.load(open(os.path.join(MODELS, f"{model_name}.json")))
    if m["features"] != FEATURES:
        sys.exit("model was fitted on a different feature list; refit it")
    rows = load_features(region)
    assign_cells(rows)
    X = percentile_matrix(rows)
    scores = 1 / (1 + np.exp(-(X @ np.array(m["coef"]) + m["intercept"])))
    in_rule = np.array([r["in_pool_rule"] for r in rows]) == 1
    print(f"{region}: {len(rows)} artists; model {model_name}, cutoff {m['cutoff']}")
    print(f"selects {int((in_rule & (scores >= m['cutoff'])).sum())} artists")
    report_cells(rows, scores, m["cutoff"])
    print(f"wrote {write_scores(region, rows, scores, m['cutoff'])}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fit")
    f.add_argument("--region", required=True, choices=sorted(REGIONS))
    f.add_argument("--recall", type=float, default=0.95)
    a = sub.add_parser("apply")
    a.add_argument("--region", required=True, choices=sorted(REGIONS))
    a.add_argument("--model", required=True)
    args = ap.parse_args()
    if args.cmd == "fit":
        fit(args.region, args.recall)
    else:
        apply(args.region, args.model)


if __name__ == "__main__":
    main()
