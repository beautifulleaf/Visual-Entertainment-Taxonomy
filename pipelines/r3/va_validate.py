"""Validate one R3 Visual Art pass: python3 pipelines/r3/va_validate.py <pass>"""
import json, os, sys, collections
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")

def is_maker(r): return bool(r[4]) or r[1] in ("Artists", "Architects", "Makers")

def main(p):
    inp = json.load(open(os.path.join(ROOT, "taxonomy/r3/va_in", p + ".json")))["leaves"]
    out = json.load(open(os.path.join(ROOT, "taxonomy/r3/va_out", p, "result.json")))
    codes = {l["code"] for l in inp}
    allcodes = {line.split("\t")[0] for line in open(os.path.join(ROOT, "taxonomy/r3/va_leaf_index.tsv"))}
    hard, soft = [], []
    L = out.get("leaves", {})
    for c in codes - set(L): hard.append(f"leaf {c} missing from output")
    for c in set(L) - codes: hard.append(f"leaf {c} is not in this pass")
    makers_in = collections.Counter(r[0] for l in inp for r in l["rows"] if is_maker(r) and str(r[0]).strip())  # blank-name rows are junk
    makers_out = collections.Counter()
    def check_rows(where, rows, axis):
        groups = collections.Counter()
        for r in rows:
            if not (isinstance(r, list) and len(r) == 5): hard.append(f"{where}: bad row {str(r)[:80]}"); continue
            if not r[0] or not r[1]: hard.append(f"{where}: row without name or group {r[:2]}")
            if len(str(r[2])) > 200: soft.append(f"{where}: long gloss for {r[0]}")
            if any(x in str(r[2]) for x in ("Gathered rows", "now T1", "now T2", "excluded rows")): hard.append(f"{where}: machine gloss left: {r[0]}")
            if r[1].startswith("Gathered rows"): hard.append(f"{where}: group 'Gathered rows' left")
            if str(r[3]).startswith("r3") and "http" not in str(r[3]): hard.append(f"{where}: new row {r[0]} has no URL")
            groups[r[1]] += 1
            if is_maker(r): makers_out[r[0]] += 1
        if len(rows) > 40 and not axis: hard.append(f"{where}: {len(rows)} kinds and no axis")
        if len(rows) > 400:
            for g, n in groups.items():
                if n > 300: soft.append(f"{where}: group '{g}' has {n} rows")
        return len(rows)
    def check_cats(where, cats):
        if not cats: soft.append(f"{where}: no catalogues (View all) links"); return
        for x in cats:
            if not (isinstance(x, list) and len(x) == 3 and str(x[0]).startswith("http")): hard.append(f"{where}: bad catalogue entry {str(x)[:80]}")
    sizes = {}
    for c, v in L.items(): sizes[c] = check_rows(c, v.get("kinds", []), v.get("axis")); check_cats(c, v.get("catalogues"))
    for nl in out.get("new_leaves", []): check_cats(nl.get("key", "?"), nl.get("catalogues"))
    for i, nl in enumerate(out.get("new_leaves", [])):
        k = nl.get("key", f"new{i}")
        for f in ("sub", "label", "breadth", "defn", "src", "kinds"):
            if not nl.get(f): hard.append(f"new leaf {k} missing {f}")
        sizes[k + " " + nl.get("label", "")] = check_rows(k, nl.get("kinds", []), nl.get("axis"))
    for m in out.get("moves_out", []):
        if len(m) != 3: hard.append(f"bad move {m}"); continue
        if m[2] not in allcodes: hard.append(f"move target {m[2]} unknown")
        if m[2] in codes: hard.append(f"move target {m[2]} is inside this pass: put the row in that leaf's kinds instead")
        makers_out[m[0]] += 1
    lost = [n for n, c in makers_in.items() if makers_out[n] < c]
    dup = [n for n, c in makers_out.items() if c > makers_in.get(n, 0) and n in makers_in]
    if lost: hard.append(f"{len(lost)} makers lost, e.g. {lost[:8]}")
    if dup: soft.append(f"{len(dup)} makers placed more often than in input, e.g. {dup[:8]}")
    small = [c for c, n in sizes.items() if n <= 4]
    print(f"pass {p}: {len(L)} leaves, {len(out.get('new_leaves', []))} new, {len(out.get('moves_out', []))} moved out, "
          f"{sum(sizes.values())} kinds; leaves with <=4 kinds: {len(small)}")
    for s in soft[:40]: print("WARN", s)
    for h in hard[:60]: print("ERROR", h)
    sys.exit(1 if hard else 0)

if __name__ == "__main__":
    main(sys.argv[1])
