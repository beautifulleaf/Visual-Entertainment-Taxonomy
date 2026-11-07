"""Validate a resize batch: python3 pipelines/r3/resize_validate.py <batch>"""
import json, os, sys, collections
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
D = os.path.join(ROOT, "taxonomy/r3/resize")
def main(b):
    inp = {l["code"]: l for l in json.load(open(os.path.join(D, f"in_{b}.json")))["leaves"]}
    out = json.load(open(os.path.join(D, f"out_{b}.json")))
    hard = []
    for code, l in inp.items():
        o = out.get(code)
        if not o: hard.append(f"{code} missing"); continue
        keys = {"self": o.get("secs") or []}
        for nl in o.get("new_leaves", []):
            for k in ("key", "label", "breadth", "defn", "src"):
                if not nl.get(k): hard.append(f"{code} new leaf {nl.get('key')} missing {k}")
            keys[nl["key"]] = nl.get("secs") or []
        ids = [t["id"] for t in l["titles"]]; A = o.get("assign", {}); moved = {m[0] for m in o.get("moves", [])}
        miss = [i for i in ids if i not in A and i not in moved]
        if miss: hard.append(f"{code}: {len(miss)} titles unassigned, e.g. {miss[:3]}")
        size = collections.Counter(); secn = collections.Counter()
        for i, (k, s) in A.items():
            if k not in keys: hard.append(f"{code}: {i} → unknown key {k}"); continue
            if keys[k] and not (isinstance(s, int) and 1 <= s <= len(keys[k])): hard.append(f"{code}: {i} bad section {s} for {k}")
            size[k] += 1; secn[(k, s)] += 1
        for k, n in size.items():
            if n > 230: hard.append(f"{code} part {k}: {n} titles (> 230)")
            if n > 40 and not keys[k]: hard.append(f"{code} part {k}: {n} titles, no sections")
        print(code, l["label"], len(ids), "→", dict(size), "| max section", max(secn.values()) if secn else 0)
    for h in hard[:40]: print("ERROR", h)
    sys.exit(1 if hard else 0)
if __name__ == "__main__":
    main(sys.argv[1])
