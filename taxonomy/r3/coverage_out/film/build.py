"""Assemble film coverage outputs from spec modules s_a*.py.
Each spec defines NEW (list of new-leaf dicts), SECS (list of (leaf,label)),
ITEMS (text block: target | sec | title | year | who | id?), RESEC (dict leaf -> {axis, secs, fn or map}).
"""
import csv, json, glob, importlib, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import LEAVES, PLACED, INFO, lk, norm
D = os.path.dirname(os.path.abspath(__file__))

mods = [importlib.import_module(os.path.basename(f)[:-3]) for f in sorted(glob.glob(f"{D}/s_a*.py"), key=lambda p: int(os.path.basename(p)[3:-3]))]
NEW, SECS, RES = [], [], {}
items = []
for m in mods:
    NEW += getattr(m, "NEW", [])
    SECS += getattr(m, "SECS", [])
    RES.update(getattr(m, "RESEC", {}))
    for ln in getattr(m, "ITEMS", "").strip().splitlines():
        if not ln.strip() or ln.strip().startswith("#"): continue
        p = [x.strip() for x in ln.split("|")]
        p += [""] * (6 - len(p))
        items.append((m.__name__,) + tuple(p[:6]))
newkeys = {n["key"]: n for n in NEW}
seckeys = collections.defaultdict(list)
for l, s in SECS: seckeys[l].append(s)

def secs_of(to):
    if to in RES: return RES[to]["secs"]
    if to in newkeys: return newkeys[to].get("secs", [])
    base = [s.strip() for s in LEAVES[to]["secs"].split("|") if s.strip()]
    return base + seckeys.get(to, [])

warn = []
used = {}
moves, adds = [], []
for mod, to, sec, title, year, who, tid in items:
    if to not in LEAVES and to not in newkeys: warn.append(f"unknown target {to} ({title})"); continue
    tc = tid or lk(title, year or None, None)
    if tid == "-": tc = ""
    if tc and tc in PLACED and not PLACED[tc]["leaf"].startswith("A"): warn.append(f"NONFILM match {title} -> {tc} {PLACED[tc]['leaf']}"); continue
    if tc and tc in used:
        warn.append(f"dup {tc} {title} ({used[tc]} vs {to})"); continue
    ss = secs_of(to)
    if sec:
        if sec.isdigit(): si = sec
        elif sec in ss: si = str(ss.index(sec) + 1)
        else: warn.append(f"sec '{sec}' not in {to} {ss}"); si = sec
    else:
        si = ""
        if ss and to not in RES: warn.append(f"no sec for {title} -> {to} (has secs)")
    if tc: used[tc] = to
    if tc and tc in PLACED:
        if PLACED[tc]["leaf"] == to and not si: continue
        moves.append({"id": tc, "to": to, "sec": si, "note": f"{PLACED[tc]['title']} ({PLACED[tc]['year']}) from {PLACED[tc]['leaf']}"})
    else:
        if not tc: warn.append(f"NOID {to}: {title} {year}")
        i = INFO.get(tc, {}) if tc else {}
        adds.append({"id": tc or "", "title": title if not tc else (i.get("title") or title), "year": year or i.get("year", ""),
                     "who": who or i.get("dir", "") or i.get("country", ""), "kind": "film", "to": to, "sec": si, "note": mod})

# resections: every title of leaf must be assigned
resout = {}
moved_out = {m["id"] for m in moves if m["to"] not in RES or True}
for leaf, spec in RES.items():
    secs = spec["secs"]; assign = {}
    members = [tc for tc, r in PLACED.items() if r["leaf"] == leaf]
    for tc in members:
        if tc in used and used[tc] != leaf: continue  # moved out
        if any(m["id"] == tc and m["to"] == leaf for m in moves): continue
        lab = spec["map"].get(tc) if "map" in spec else None
        if lab is None and "fn" in spec: lab = spec["fn"](tc, PLACED[tc], INFO.get(tc, {}))
        if lab is None or lab not in secs: warn.append(f"RESEC {leaf} unassigned {tc} {PLACED[tc]['title']} {PLACED[tc]['year']} {PLACED[tc]['who']} -> {lab}"); continue
        assign[tc] = secs.index(lab) + 1
    resout[leaf] = {"axis": spec["axis"], "secs": secs, "assign": assign}

json.dump(NEW, open(f"{D}/new_leaves.json", "w"), ensure_ascii=False, indent=1)
with open(f"{D}/new_sections.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["leaf", "label"]); w.writerows(SECS)
for name, rows, cols in (("moves.csv", moves, ["id", "to", "sec", "note"]), ("adds.csv", adds, ["id", "title", "year", "who", "kind", "to", "sec", "note"])):
    with open(f"{D}/{name}", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
json.dump(resout, open(f"{D}/resections.json", "w"), ensure_ascii=False, indent=1)
for x in warn: print("WARN", x)
c = collections.Counter(m["to"] for m in moves + adds)
print(f"moves {len(moves)} adds {len(adds)} (noid {sum(1 for a in adds if not a['id'])}) new leaves {len(NEW)} new secs {len(SECS)} resections {len(resout)}")
if "-v" in sys.argv:
    for k, v in sorted(c.items()): print(" ", k, v)
