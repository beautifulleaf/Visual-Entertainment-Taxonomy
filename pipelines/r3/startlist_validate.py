"""Validate a Starting List placement batch: python3 pipelines/r3/startlist_validate.py <batch>"""
import csv, os, sys, collections
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
O = os.path.join(ROOT, "taxonomy/r3/startlist")
def main(b):
    L = {r["code"]: r for r in csv.DictReader(open(os.path.join(O, "leaves.tsv")), delimiter="\t")}
    ids = [r["id"] for r in csv.DictReader(open(os.path.join(O, f"in_{b}.csv")))]
    A = list(csv.DictReader(open(os.path.join(O, f"out_{b}.csv"))))
    import json
    nf = os.path.join(O, f"new_leaves_{b}.json"); NL = json.load(open(nf)) if os.path.exists(nf) else []
    for nl in NL:
        for k in ("key", "sub", "label", "defn", "src"):
            if not nl.get(k): print("ERROR new leaf missing", k, nl.get("key")); sys.exit(1)
        L[nl["key"]] = {"sub": nl["sub"], "secs": " | ".join(nl.get("secs") or [])}
    hard = []; c = collections.Counter(a["id"] for a in A)
    miss = [i for i in ids if i not in c]; dup = [i for i, n in c.items() if n > 1]; extra = [i for i in c if i not in set(ids)]
    if miss: hard.append(f"{len(miss)} ids missing, e.g. {miss[:5]}")
    if dup: hard.append(f"{len(dup)} ids twice, e.g. {dup[:5]}")
    if extra: hard.append(f"{len(extra)} unknown ids")
    per = collections.Counter()
    for a in A:
        lf = a["leaf"].strip()
        if lf == "out": per["out"] += 1; continue
        if lf not in L: hard.append(f"{a['id']}: unknown leaf {lf}"); continue
        per[L[lf]["sub"]] += 1
        secs = [x for x in L[lf]["secs"].split(" | ") if x]
        s = a.get("sec", "").strip()
        if s.startswith("new:"): continue
        if s and (not s.isdigit() or not 1 <= int(s) <= len(secs)): hard.append(f"{a['id']}: bad sec '{s}' for {lf}")
    print(f"batch {b}: {len(ids)} input, {len(A)} rows; per sub-family {dict(per.most_common())}")
    for h in hard[:40]: print("ERROR", h)
    sys.exit(1 if hard else 0)
if __name__ == "__main__":
    main(sys.argv[1])
