"""Reference (positive) artists for a region: calibrate_depth.py matches plus hand overrides.

calibrate_depth.py writes data/interim/depth_reference_matched.csv (one row per
reference name, with the Wikidata match it picked). Wrong or missing picks are
corrected in the committed seeds/visual-art/depth_reference_overrides.csv:
  name,qid,note
An empty qid drops the name (no Wikidata item, or not an individual artist);
"Q1|Q2" splits an entry that fuses two artists.
"""
import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MATCHED = os.path.join(ROOT, "data", "interim", "depth_reference_matched.csv")
OVERRIDES = os.path.join(ROOT, "seeds", "visual-art", "depth_reference_overrides.csv")


def load_overrides():
    if not os.path.exists(OVERRIDES):
        return {}
    with open(OVERRIDES, encoding="utf-8") as f:
        return {r["name"]: r["qid"].strip() for r in csv.DictReader(f)}


def load_reference(region_cfg):
    """Rows {movement, name, qid} for the region's reference list; qid '' when unresolved."""
    seed = os.path.basename(region_cfg["reference"])
    overrides = load_overrides()
    rows = []
    with open(MATCHED, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("list") and r["list"] != seed:
                continue
            qids = overrides.get(r["name"], r.get("qid") or "")
            # "Q1|Q2" splits an entry that fuses two artists into two positives.
            for qid in qids.split("|"):
                rows.append({"movement": r["movement"], "name": r["name"], "qid": qid})
    return rows
