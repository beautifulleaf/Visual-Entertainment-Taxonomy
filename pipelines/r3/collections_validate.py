"""Validate a collections label-mapping batch: python3 pipelines/r3/collections_validate.py <batch>"""
import csv, os, sys, collections
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
O = os.path.join(ROOT, "taxonomy/r3/collections")
def main(b):
    L = {r["code"] for r in csv.DictReader(open(os.path.join(O, "va_leaves.tsv")), delimiter="\t")}
    inp = [(r["file"], r["label"], r["family"]) for r in csv.DictReader(open(os.path.join(O, f"in_{b}.csv")))]
    out = list(csv.DictReader(open(os.path.join(O, f"out_{b}.csv"))))
    got = collections.Counter((r["file"], r["label"], r["family"]) for r in out)
    hard = []
    miss = [k for k in inp if k not in got]
    if miss: hard.append(f"{len(miss)} keys missing, e.g. {miss[:3]}")
    dup = [k for k, n in got.items() if n > 1]
    if dup: hard.append(f"{len(dup)} keys twice")
    c = collections.Counter()
    for r in out:
        m = r["map"].strip()
        kind = m.split(":")[0] if ":" in m else "leaf"
        if kind == "leaf" and m not in L: hard.append(f"unknown leaf {m} for {r['label']}")
        if kind not in ("leaf", "general", "missing", "exclude"): hard.append(f"bad map {m}")
        c[kind] += 1
    print(f"batch {b}: {len(inp)} keys, outcomes {dict(c)}")
    for h in hard[:30]: print("ERROR", h)
    sys.exit(1 if hard else 0)
if __name__ == "__main__":
    main(sys.argv[1])
