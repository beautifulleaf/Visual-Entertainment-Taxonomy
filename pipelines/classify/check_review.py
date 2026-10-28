"""Check reviewed batches: every *_out.csv must list exactly its input's IDs, in order.

    python3 pipelines/classify/check_review.py taxonomy/film/review films tconst
    python3 pipelines/classify/check_review.py taxonomy/series/review anime id
"""
import csv
import os
import sys

d, prefix, key = sys.argv[1:4]
bad = 0
for f in sorted(os.listdir(d)):
    if f.startswith(prefix + "_") and f.endswith("_out.csv"):
        inp = os.path.join(d, f.replace("_out", ""))
        a = [r[key] for r in csv.DictReader(open(inp, encoding="utf-8"))]
        b = [r.get(key, r.get("tconst", r.get("id"))) for r in csv.DictReader(open(os.path.join(d, f), encoding="utf-8"))]
        if a != b:
            bad += 1
            print(f, "MISMATCH", len(a), len(b), len(set(a) & set(b)))
print("checked;", bad, "bad")
