"""Validate an R3 coverage pass: python3 pipelines/r3/coverage_validate.py <part>"""
import csv, json, os, sys, collections
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
csv.field_size_limit(10**9)

def main(p):
    d = os.path.join(ROOT, "taxonomy/r3/coverage_out", p)
    leaves = {r["code"]: r for r in csv.DictReader(open(os.path.join(ROOT, "taxonomy/r3/ft_leaf_index.tsv")), delimiter="\t")}
    placed = {r["id"]: r for r in csv.DictReader(open(os.path.join(ROOT, "taxonomy/r3/ft_title_index.tsv")), delimiter="\t")}
    hard = []
    NL = json.load(open(os.path.join(d, "new_leaves.json"))) if os.path.exists(os.path.join(d, "new_leaves.json")) else []
    keys = {}
    for nl in NL:
        for f in ("key", "sub", "label", "breadth", "defn", "src"):
            if not nl.get(f): hard.append(f"new leaf {nl.get('key')} missing {f}")
        keys[nl["key"]] = nl
    NS = list(csv.DictReader(open(os.path.join(d, "new_sections.csv")))) if os.path.exists(os.path.join(d, "new_sections.csv")) else []
    for r in NS:
        if r["leaf"] not in leaves: hard.append(f"new section on unknown leaf {r['leaf']}")
    def target_ok(to, where):
        if to not in leaves and to not in keys: hard.append(f"{where}: unknown target {to}")
    n = collections.Counter(); ids = collections.Counter()
    for r in csv.DictReader(open(os.path.join(d, "moves.csv"))) if os.path.exists(os.path.join(d, "moves.csv")) else []:
        if r["id"] not in placed: hard.append(f"move of unplaced id {r['id']}")
        target_ok(r["to"], "move " + r["id"]); n[r["to"]] += 1; ids[r["id"]] += 1
    for r in csv.DictReader(open(os.path.join(d, "adds.csv"))) if os.path.exists(os.path.join(d, "adds.csv")) else []:
        if r["id"] and r["id"] in placed: hard.append(f"add of already-placed id {r['id']} ({r['title']}): use moves.csv")
        if not r["title"] or not r["year"]: hard.append(f"add without title/year {r}")
        if r.get("kind") not in ("film", "tv", "anime"): hard.append(f"add {r['title']}: kind must be film/tv/anime")
        target_ok(r["to"], "add " + r["title"]); n[r["to"]] += 1
        if r["id"]: ids[r["id"]] += 1
    dup = [i for i, c in ids.items() if c > 1]
    if dup: hard.append(f"ids used twice: {dup[:8]}")
    for k, nl in keys.items():
        if n[k] < 3: hard.append(f"new leaf {k} {nl['label']} has {n[k]} titles (need ≥3, aim ≥5)")
    for c, l in leaves.items():
        if l["n"] == "0" and n[c] == 0 and c.split("-")[0] in {x for x in [os.environ.get('COV_SUBS','')] if x}: pass
    print(f"part {p}: {len(NL)} new leaves, {len(NS)} new sections, moves+adds {sum(n.values())}")
    for k, nl in keys.items(): print(f"  {k} {nl['sub']} {nl['label']}: {n[k]}")
    for h in hard[:60]: print("ERROR", h)
    sys.exit(1 if hard else 0)

if __name__ == "__main__":
    main(sys.argv[1])
