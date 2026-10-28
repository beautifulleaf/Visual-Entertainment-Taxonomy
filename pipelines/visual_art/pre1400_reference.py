"""Era-own reference and model for the pre-1400 passes (visual-art-plan.md §2.1).

The Europe 1400-1900 model is an example of the depth wanted, not a calibrator
every era must use. This script:
1. builds a small pre-1400 reference from Wikidata, cheaply: pooled artists whose
   movement (P135, already in the pools) is a pre-1400 school, workshop or style
   (Sienese school, International Gothic, Palaeologan Renaissance, Kei school,
   Archaic Greek sculpture, red-figure pottery, ...);
   -> data/interim/visual_art/pre1400_reference.csv (movement, region, name, qid)
2. measures how much of it the Europe model's selection recovers (scores_R.csv
   from `depth_model.py apply`);
3. fits an era model on it (NonNegativeLogit on the same within-cell percentile
   features, all four pre-1400 regions together, architecture left out as in
   select()), takes the cutoff at --recall of the reference, and writes
   pipelines/visual_art/models/pre1400.json and scores_<R>_era.csv per region.
   The selection rule is depth_model.select(): every reference artist plus
   pool-rule artists at or above the cutoff (score x art_factor).
4. cleans the era selection (decided 2026-10-28, the era selection is the one used):
   - literati filter (east_asia_pre1400, islamic_pre1400): people whose only art
     occupation is calligrapher and who are also poets, writers, politicians or
     rulers stay only if the Europe model selects them or some museum holds their
     work (n_museums >= 1, which counts the East Asia sweep there);
   - vase "Group" / "Class" / "Workshop" / "Circle" items (typed notname on Wikidata)
     are not artists: they leave the selection and go to
     data/interim/visual_art/pre1400_workshop_groups.csv as tradition evidence;
   - manual includes from seeds/visual-art/pre1400_manual_includes.csv (artists the
     model cannot select: no dates on Wikidata, or architecture as primary medium).
   The final choice is the `final` column of scores_<R>_era.csv, with `note`.

Usage: python3 pipelines/visual_art/pre1400_reference.py [--recall 0.9]
(after run_pre1400.sh)
"""
import argparse
import collections
import csv
import json
import os
import sys

import re

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from depth_model import (DATA, FEATURES, MODELS, NonNegativeLogit, art_factor,  # noqa: E402
                         assign_cells, load_features, percentile_matrix, select)
from regions import MEDIA, PRE1400_EXTRA_OCCUPATIONS, REGIONS  # noqa: E402

ART_OCCS = {o for occs in MEDIA.values() for o in occs} | {o for occs in PRE1400_EXTRA_OCCUPATIONS.values() for o in occs}

PRE1400 = ["antiquity_mediterranean", "europe_medieval_500-1400", "east_asia_pre1400", "islamic_pre1400"]

# Pre-1400 art schools, workshops and styles found as P135 in the pools (QIDs
# verified by label). Literary and philosophical movements and architecture styles
# are left out.
MOVEMENTS = {
    # antiquity
    "Q632355": "Archaic Greek sculpture", "Q221375": "Hellenistic art", "Q16064885": "art of Classical Greece",
    "Q271834": "Archaic Greece", "Q2096208": "Pioneer Group", "Q629602": "black-figure pottery",
    "Q633683": "red-figure pottery", "Q763709": "white ground technique", "Q738680": "pottery of ancient Greece",
    "Q1777842": "severe style", "Q622339": "Apulian vase painting", "Q1747618": "ancient Greek art",
    "Q830331": "Etruscan art", "Q131701861": "School of Chios",
    # medieval Europe and Byzantium
    "Q1332178": "Sienese school", "Q46825": "Gothic art", "Q867769": "International Gothic",
    "Q3773652": "International Gothic art in Italy", "Q947129": "Gothic painting", "Q979160": "Proto-Renaissance",
    "Q856643": "Trecento", "Q1263842": "Duecento", "Q2046861": "Palaeologan Renaissance",
    "Q2864613": "Komnenian art", "Q1378978": "Cretan school", "Q4123682": "icon painting of Vologda",
    "Q1520763": "Ottonian illumination", "Q2478178": "Umbrian school", "Q3578530": "Veronese school",
    "Q3578338": "Roman school", "Q443153": "Early Netherlandish painting", "Q1472236": "Early Renaissance",
    # East Asia
    "Q3079516": "Kei school", "Q16934127": "Northern Landscape style", "Q1142000": "Southern School",
    "Q11448989": "Takuma school", "Q11394807": "En school", "Q22127329": "Fujiwara no Takanobu school",
    "Q11362029": "Sesonji-ryu (calligraphy)",
}
REF_PATH = os.path.join(DATA, "pre1400_reference.csv")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(DATA)))
GROUPS_PATH = os.path.join(DATA, "pre1400_workshop_groups.csv")
MANUAL = os.path.join(REPO, "seeds", "visual-art", "pre1400_manual_includes.csv")
OCCUPATIONS = os.path.join(REPO, "data", "raw", "wikidata", "pool", "occupations.json")
LITERATI_REGIONS = {"east_asia_pre1400", "islamic_pre1400"}
CALLIGRAPHER = "Q3303330"
# poet, writer, politician, monarch, emperor, king, ruler, sovereign, statesperson (verified by label)
LITERATI_OCCS = {"Q49757", "Q36180", "Q82955", "Q116", "Q39018", "Q12097", "Q1097498", "Q2304859", "Q372436"}
GROUP_LABEL = re.compile(r"\b(Group|Class|Workshop|Circle)\b")


def build_reference():
    rows = []
    for region in PRE1400:
        with open(os.path.join(DATA, f"pool_{region}.csv"), encoding="utf-8") as f:
            for r in csv.DictReader(f):
                ms = [m for m in r["movements"].split("|") if m in MOVEMENTS]
                if int(r["in_pool_rule"]) and ms and r["medium"] != "architecture":
                    rows.append({"movement": MOVEMENTS[ms[0]], "region": region, "name": r["label"], "qid": r["qid"]})
    with open(REF_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["movement", "region", "name", "qid"])
        w.writeheader()
        w.writerows(rows)
    print(f"reference: {len(rows)} artists ({', '.join(f'{k} {v}' for k, v in collections.Counter(r['region'] for r in rows).items())}); wrote {REF_PATH}")
    return rows


def europe_recall(ref):
    """Share of the reference the Europe model's selection (scores_R.csv) recovers."""
    print("\nEurope 1400-1900 model (apply) on the pre-1400 reference:")
    tot = hit = 0
    for region in PRE1400:
        with open(os.path.join(DATA, f"scores_{region}.csv"), encoding="utf-8") as f:
            sel = {r["qid"]: r["selected"] == "1" for r in csv.DictReader(f)}
        qs = [r["qid"] for r in ref if r["region"] == region]
        h = sum(sel.get(q, False) for q in qs)
        tot, hit = tot + len(qs), hit + h
        print(f"  {region:28} {h:>4}/{len(qs):<4}")
    print(f"  {'all':28} {hit:>4}/{tot:<4} = {hit / max(tot, 1):.0%}")


def fit_era(ref, recall):
    ref_q = {r["qid"] for r in ref}
    rows, Xs = [], []
    for region in PRE1400:
        rs = load_features(region)
        assign_cells(rs)
        for r in rs:
            r["region"], r["is_reference"] = region, int(r["qid"] in ref_q)
        rows += rs
        Xs.append(percentile_matrix(rs))  # percentiles within each region's own cells
    X = np.vstack(Xs)
    y = np.array([r["is_reference"] for r in rows])
    # Architecture is not selected by the model (styles and buildings instead).
    train = np.array([r["medium"] != "architecture" for r in rows])
    model = NonNegativeLogit().fit(X[train], y[train])
    scores = model.predict_proba(X)[:, 1]
    adj = np.array([s * art_factor(r) for r, s in zip(rows, scores)])
    cutoff = float(np.quantile(adj[y == 1], 1 - recall))
    print(f"\nera model on {train.sum()} artists, {y.sum()} reference positives; coefficients (within-cell percentiles):")
    for f, c in sorted(zip(FEATURES, model.coef_[0]), key=lambda t: -t[1]):
        print(f"  {f:20} {c:+.2f}")
    print(f"  {'intercept':20} {model.intercept_[0]:+.2f}")
    print(f"cutoff for {recall:.0%} reference recall: score >= {cutoff:.4f}")
    os.makedirs(MODELS, exist_ok=True)
    path = os.path.join(MODELS, "pre1400.json")
    json.dump({
        "fitted_on": "+".join(PRE1400), "reference": os.path.relpath(REF_PATH, REPO),
        "features": FEATURES, "feature_transform": "within-cell mid-rank percentile",
        "coef": [round(float(c), 6) for c in model.coef_[0]], "intercept": round(float(model.intercept_[0]), 6),
        "recall_target": recall, "cutoff": round(cutoff, 6), "n_artists": len(rows), "n_reference": int(y.sum()),
    }, open(path, "w"), indent=1)
    print(f"wrote {path}")

    occupations = json.load(open(OCCUPATIONS, encoding="utf-8"))
    manual = list(csv.DictReader(open(MANUAL, encoding="utf-8"))) if os.path.exists(MANUAL) else []
    groups, totals = [], collections.Counter()
    print(f"\n{'region':28} {'pool':>5} {'ref':>4} {'Europe model':>13} {'era model':>10} {'final':>6}")
    for region in PRE1400:
        idx = [i for i, r in enumerate(rows) if r["region"] == region]
        rs = [rows[i] for i in idx]
        sel = select(rs, scores[idx], cutoff, REGIONS[region])
        with open(os.path.join(DATA, f"scores_{region}.csv"), encoding="utf-8") as f:
            eu_sel = {r["qid"] for r in csv.DictReader(f) if r["selected"] == "1"}
        dropped, kept = [], []
        for r, s, c in zip(rs, scores[idx], sel):
            r["final"], r["note"] = int(c), ""
            if GROUP_LABEL.search(r["label"] or ""):
                r["final"], r["note"] = 0, "vase group/class/workshop: tradition evidence, not an artist"
                groups.append({"qid": r["qid"], "label": r["label"], "region": region, "cell": r["cell"],
                               "sitelinks": int(r["sitelinks"]), "museum_objects": int(r["museum_objects"]), "era_score": round(float(s), 5)})
                continue
            occ = set(occupations.get(r["qid"], []))
            if (c and region in LITERATI_REGIONS and CALLIGRAPHER in occ and occ & LITERATI_OCCS
                    and not (occ - {CALLIGRAPHER, "Q483501"}) & ART_OCCS):
                if r["qid"] in eu_sel or r["n_museums"] >= 1:
                    r["note"] = "literati calligrapher kept: " + ("Europe model selects" if r["qid"] in eu_sel else "museum holdings")
                    kept.append(r["label"])
                else:
                    r["final"], r["note"] = 0, "literati calligrapher dropped: no Europe-model selection, no museum holdings"
                    dropped.append(r["label"])
        have = {r["qid"] for r in rs}
        for m in manual:
            if m["region"] != region:
                continue
            hit = next((r for r in rs if r["qid"] == m["qid"]), None)
            if hit:
                hit["final"], hit["note"] = 1, "manual include: " + m["note"]
            elif m["qid"] not in have:
                rs.append({"qid": m["qid"], "label": m["name"], "medium": "", "cell": "", "in_pool_rule": 0, "is_reference": 0,
                           "final": 1, "note": "manual include (outside the pool): " + m["note"], **{f: "" for f in FEATURES}})
        final = [r for r in rs if r["final"]]
        totals[region] = len(final)
        print(f"{region:28} {sum(r['in_pool_rule'] for r in rs):>5} {sum(r['is_reference'] for r in rs):>4} {len(eu_sel):>13} {int(sel.sum()):>10} {len(final):>6}")
        by_medium = collections.Counter(r["medium"] or "(manual, outside pool)" for r in final)
        print("    final by medium: " + ", ".join(f"{m} {n}" for m, n in by_medium.most_common()))
        if kept or dropped:
            print(f"    literati kept ({len(kept)}): {', '.join(kept)}")
            print(f"    literati dropped ({len(dropped)}): {', '.join(dropped)}")
        out = os.path.join(DATA, f"scores_{region}_era.csv")
        cols = ["qid", "label", "birth", "medium", "cell", "in_pool_rule", "is_reference", "art_occ_share", "score",
                "selected", "final", "note"] + FEATURES
        score_of = {rows[i]["qid"]: float(scores[i]) for i in idx}
        sel_of = {r["qid"]: int(c) for r, c in zip(rs, sel)}
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for r in sorted(rs, key=lambda r: -score_of.get(r["qid"], 9)):
                w.writerow({**r, "score": round(score_of[r["qid"]], 5) if r["qid"] in score_of else "",
                            "selected": sel_of.get(r["qid"], 0)})
    with open(GROUPS_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["qid", "label", "region", "cell", "sitelinks", "museum_objects", "era_score"])
        w.writeheader()
        w.writerows(sorted(groups, key=lambda g: -g["era_score"]))
    print(f"\n{len(groups)} vase groups/classes/workshops moved to {GROUPS_PATH}")
    print(f"final pre-1400 selection: {sum(totals.values())} rows across regions")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recall", type=float, default=0.90)
    args = ap.parse_args()
    ref = build_reference()
    europe_recall(ref)
    fit_era(ref, args.recall)


if __name__ == "__main__":
    main()
