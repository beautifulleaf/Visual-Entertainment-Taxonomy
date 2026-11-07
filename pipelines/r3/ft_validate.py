"""Validate one R3 Film & Television block pass.

    python3 pipelines/r3/ft_validate.py <block>

Checks taxonomy/r3/ft_out/<block>/leaves.json and assign.csv against
taxonomy/r3/ft_in/<block>.csv: every input id placed exactly once, leaf codes
and section indexes exist, sub-family codes are the block's own, sizes and
section rules. Prints problems and a size table; exit 1 on hard errors.
"""
import csv, json, os, sys, collections
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
csv.field_size_limit(10**9)

def main(b):
    blocks = json.load(open(os.path.join(ROOT, "taxonomy/r3/ft_blocks.json")))
    subs_ok = {c for c, _ in blocks[b]["subs"]}
    inp = [r["id"] for r in csv.DictReader(open(os.path.join(ROOT, "taxonomy/r3/ft_in", b + ".csv")))]
    od = os.path.join(ROOT, "taxonomy/r3/ft_out", b)
    L = json.load(open(os.path.join(od, "leaves.json")))
    hard, soft = [], []
    leaves = {}
    for s in L["subs"]:
        if s["code"] not in subs_ok: hard.append(f"sub-family {s['code']} not in block")
        if not s.get("axis", "").startswith("Axis:"): soft.append(f"{s['code']} axis should start 'Axis:'")
        for i, l in enumerate(s["leaves"], 1):
            if l["code"] != f"{s['code']}-{i}": hard.append(f"leaf code {l['code']} should be {s['code']}-{i} (number in order)")
            for k in ("label", "breadth", "defn", "src"):
                if not l.get(k): hard.append(f"{l['code']} missing {k}")
            if l.get("breadth") not in ("broad", "medium", "narrow"): hard.append(f"{l['code']} breadth")
            leaves[l["code"]] = l
    A = list(csv.DictReader(open(os.path.join(od, "assign.csv"))))
    seen = collections.Counter(r["id"] for r in A)
    dup = [i for i, n in seen.items() if n > 1]
    missing = [i for i in inp if i not in seen]
    extra = [i for i in seen if i not in set(inp)]
    if dup: hard.append(f"{len(dup)} ids placed twice, e.g. {dup[:5]}")
    if missing: hard.append(f"{len(missing)} input ids not placed, e.g. {missing[:5]}")
    if extra: hard.append(f"{len(extra)} unknown ids, e.g. {extra[:5]}")
    n = collections.Counter(); ns = collections.defaultdict(collections.Counter)
    for r in A:
        lf = r["leaf"].strip()
        if r.get("route", "").strip():
            if r["route"].strip()[0] not in "ABC": hard.append(f"bad route {r['route']} for {r['id']}")
            continue
        if lf not in leaves: hard.append(f"{r['id']}: unknown leaf {lf}"); continue
        n[lf] += 1
        secs = leaves[lf].get("secs") or []
        sec = r.get("sec", "").strip()
        if secs:
            if not sec.isdigit() or not 1 <= int(sec) <= len(secs): hard.append(f"{r['id']}: sec '{sec}' out of range for {lf}")
            else: ns[lf][int(sec)] += 1
        elif sec: hard.append(f"{r['id']}: sec given but {lf} has no secs")
    for c, l in leaves.items():
        k = n[c]; secs = l.get("secs") or []
        if k > 200: hard.append(f"{c} {l['label']}: {k} titles > 200 — split it")
        elif k > 150: soft.append(f"{c} {l['label']}: {k} titles > 150")
        if k > 40 and not secs: hard.append(f"{c} {l['label']}: {k} titles and no sections")
        if secs and not l.get("axis"): hard.append(f"{c} has secs but no axis")
        for i, lab in enumerate(secs, 1):
            if ns[c][i] == 0: soft.append(f"{c} section {i} '{lab}' is empty")
        if k == 0: soft.append(f"{c} {l['label']} has 0 titles")
    addf = os.path.join(od, "additions.csv")
    if os.path.exists(addf):
        if not blocks[b].get("additions"): hard.append("additions.csv is only allowed in blocks that add titles")
        AD = list(csv.DictReader(open(addf)))
        ids = collections.Counter(r["id"] for r in AD if r["id"])
        for i, c in ids.items():
            if c > 1 or i in seen: hard.append(f"added id {i} duplicated")
            if not (i.startswith("tt") or i.startswith("Q")): hard.append(f"added id {i} must be tt... or Q... (or blank)")
        for r in AD:
            if not r.get("title") or not r.get("year"): hard.append(f"addition without title/year: {r}")
            lf = r["leaf"].strip()
            if lf not in leaves: hard.append(f"addition {r['title']}: unknown leaf {lf}"); continue
            n[lf] += 1; secs = leaves[lf].get("secs") or []; sec = r.get("sec", "").strip()
            if secs:
                if not sec.isdigit() or not 1 <= int(sec) <= len(secs): hard.append(f"addition {r['title']}: sec '{sec}' out of range")
                else: ns[lf][int(sec)] += 1
        print(f"additions: {len(AD)}")
        for c, l in leaves.items():
            k = n[c]; secs = l.get("secs") or []
            if k > 40 and not secs: hard.append(f"{c} {l['label']}: {k} titles and no sections")
    routed = sum(1 for r in A if r.get("route", "").strip())
    print(f"block {b}: {len(inp)} input, {len(A)} rows, {len(leaves)} leaves, routed {routed}")
    sizes = sorted(n.values())
    if sizes: print("leaf sizes: max", sizes[-1], "median", sizes[len(sizes)//2], "leaves<5:", sum(1 for x in sizes if x < 5))
    for c, l in leaves.items(): print(f"  {c:8} {n[c]:4}  {l['label']}  secs={len(l.get('secs') or [])}")
    for s in soft: print("WARN", s)
    for h in hard[:60]: print("ERROR", h)
    sys.exit(1 if hard else 0)

if __name__ == "__main__":
    main(sys.argv[1])
