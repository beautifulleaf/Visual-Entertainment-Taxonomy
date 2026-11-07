"""Build result.json for pass bucket_named_movements from assignment modules in this folder."""
import json, os, re, sys, glob, collections, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(OUT, "..", "..", "..", ".."))
inp = json.load(open(os.path.join(ROOT, "taxonomy/r3/va_in/bucket_named_movements.json")))["leaves"]
CODES = {l["code"] for l in inp}

A, META, MOVES, DROPS, GLOSS, EXTRA, FALLBACK, ALIAS, REGROUP = {}, {}, {}, {}, {}, {}, {}, {}, {}
for f in sorted(glob.glob(os.path.join(HERE, "a_*.py"))):
    spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    A.update(getattr(m, "A", {})); META.update(getattr(m, "META", {}))
    MOVES.update(getattr(m, "MOVES", {})); DROPS.update(getattr(m, "DROPS", {}))
    GLOSS.update(getattr(m, "GLOSS", {})); EXTRA.update(getattr(m, "EXTRA", {}))
    FALLBACK.update(getattr(m, "FALLBACK", {})); ALIAS.update(getattr(m, "ALIAS", {}))
    REGROUP.update(getattr(m, "REGROUP", {}))

CMAP = [  # substring -> country label (first match on the first listed country)
 ("Habsburg Netherlands", "Flanders"), ("Southern Netherlands", "Flanders"), ("Spanish Netherlands", "Flanders"), ("Austrian Netherlands", "Flanders"),
 ("Burgundian Netherlands", "Flanders"), ("Flanders", "Flanders"), ("Brabant", "Flanders"), ("Seventeen Provinces", "Flanders"),
 ("Dutch Republic", "Netherlands"), ("Kingdom of the Netherlands", "Netherlands"), ("Northern Low Countries", "Netherlands"),
 ("Netherlands", "Netherlands"), ("Holland", "Netherlands"),
 ("Belgium", "Belgium"), ("Liège", "Belgium"),
 ("Venice", "Italy"), ("Venezia", "Italy"), ("Papal States", "Italy"), ("Naples", "Italy"), ("Sicily", "Italy"), ("Genoa", "Italy"),
 ("Tuscany", "Italy"), ("Florence", "Italy"), ("Milan", "Italy"), ("Modena", "Italy"), ("Urbino", "Italy"), ("Bologna", "Italy"),
 ("Siena", "Italy"), ("Pisa", "Italy"), ("Lucca", "Italy"), ("Mantua", "Italy"), ("Sardinia", "Italy"), ("Italy", "Italy"),
 ("Kingdom of France", "France"), ("France", "France"), ("Lorraine", "France"), ("Burgundy", "France"),
 ("Spain", "Spain"), ("Aragon", "Spain"), ("Castile", "Spain"), ("Granada", "Spain"), ("Valencia", "Spain"), ("Majorca", "Spain"), ("Mallorquina", "Spain"),
 ("Portugal", "Portugal"), ("Brazil", "Brazil"),
 ("Great Britain", "United Kingdom"), ("United Kingdom", "United Kingdom"), ("England", "United Kingdom"), ("Scotland", "United Kingdom"),
 ("Ireland", "Ireland"),
 ("German", "Germany"), ("Prussia", "Germany"), ("Bavaria", "Germany"), ("Saxony", "Germany"), ("Württemberg", "Germany"), ("Hanover", "Germany"),
 ("Holy Roman Empire", "Germany"), ("Weimar", "Germany"), ("Hamburg", "Germany"), ("Lübeck", "Germany"), ("Frankfurt", "Germany"), ("Baden", "Germany"),
 ("Austria", "Austria"), ("Cisleithania", "Austria"), ("Habsburg monarchy", "Austria"), ("Switzerland", "Switzerland"), ("Geneva", "Switzerland"),
 ("Czech", "Czech lands"), ("Bohemia", "Czech lands"), ("Slovakia", "Slovakia"), ("Hungary", "Hungary"), ("Poland", "Poland"), ("Polish", "Poland"),
 ("Russia", "Russia"), ("Soviet", "Russia"), ("Ukrain", "Ukraine"), ("Sweden", "Sweden"), ("Denmark", "Denmark"), ("Norway", "Norway"), ("Finland", "Finland"),
 ("United States", "United States"), ("Thirteen Colonies", "United States"), ("Canada", "Canada"), ("Australia", "Australia"), ("New Zealand", "New Zealand"),
 ("Japan", "Japan"), ("China", "China"), ("Song dynasty", "China"), ("Tang dynasty", "China"), ("Yuan dynasty", "China"), ("Ming dynasty", "China"), ("Qing dynasty", "China"),
]
def country(c):
    first = (c or "").split(",")[0].strip()
    for k, v in CMAP:
        if k in first: return v
    for part in (c or "").split(","):
        for k, v in CMAP:
            if k in part: return v
    return first or "Other"

def medium_word(m):
    m = (m or "").lower()
    if "painting" in m: return "Painter"
    if "sculpt" in m: return "Sculptor"
    if "print" in m or "engrav" in m: return "Printmaker"
    if "draw" in m: return "Draughtsman"
    if "calligraph" in m: return "Calligrapher"
    if "photo" in m: return "Photographer"
    if "architect" in m: return "Architect"
    return "Artist"

MACHINE = re.compile(r"(^movement |country group|Gathered rows|; Italy and the Italian states|route resolved|now T\d|excluded rows)", re.I)
def clean_countries(c):
    seen = []
    for p in (c or "").split(","):
        p = p.strip()
        if p and p not in seen and not re.match(r"Q\d+$", p): seen.append(p)
    return ", ".join(seen[:2])

def auto_gloss(name, ev, leaf_label):
    b = ev.get("birth") or ""
    parts = [medium_word(ev.get("medium"))]
    if b: parts[0] += f", b. {b}" if not b.startswith("-") else ""
    cc = clean_countries(ev.get("countries"))
    s = parts[0] + (f" · {cc}" if cc else "")
    return s

def main():
    res = {"leaves": {}, "new_leaves": [], "moves_out": [], "dropped": []}
    incoming = collections.defaultdict(list)  # code -> rows moved in from other leaves in pass
    unassigned = collections.defaultdict(list)
    leafrows = {}
    for l in inp:
        code = l["code"]; groups = A.get(code, [])
        lookup = {}
        for gi, (g, names) in enumerate(groups):
            for n in [x.strip() for x in names.split(";") if x.strip()]:
                lookup.setdefault(n, g)
        rows_out = []
        for r in l["rows"]:
            name = r[0]; ev = r[5] if len(r) > 5 else {}
            if not name.strip():
                continue  # handled below (blank record)
            key = (code, name)
            if key in DROPS:
                res["dropped"].append([code, name, DROPS[key]]); continue
            g0 = r[1]
            src = r[3]
            gloss = GLOSS.get((code, name)) or GLOSS.get(name)
            if not gloss:
                gl = r[2] or ""
                gloss = "" if (MACHINE.search(gl) or ev) else gl
                if ev:
                    gloss = auto_gloss(name, ev, l["label"])
                gloss = re.sub(r"\s*\(P\d+\)", "", gloss)
                gloss = re.sub(r"\s*·?\s*owned as ([^·(]+?) \(Possession (\w+)\)", r" · Possession: \1(\2)", gloss)
                gloss = re.sub(r"\s*·\s*https?://\S+", "", gloss).strip()
            is_maker = 1 if (r[4] or g0 in ("Artists", "Architects", "Makers")) else 0
            if key in MOVES:
                tgt = MOVES[key]
                if tgt in CODES:
                    incoming[tgt].append((name, gloss, src, is_maker, ev, code))
                else:
                    res["moves_out"].append([name, code, tgt])
                continue
            g = lookup.get(name)
            if not g:
                g = REGROUP.get((code, g0)) or (FALLBACK[code](name, ev, g0) if code in FALLBACK else None) or (country(ev.get("countries")) if ev else (g0 or "Other"))
                unassigned[code].append((name, g, ev.get("birth", ""), ev.get("countries", "")))
            rows_out.append([name, g, gloss[:200], src, is_maker, ev.get("birth", "")])
        leafrows[code] = (rows_out, lookup, groups)
    for code, items in incoming.items():
        rows_out, lookup, groups = leafrows[code]
        for name, gloss, src, mk, ev, frm in items:
            g = lookup.get(name) or (FALLBACK[code](name, ev, "") if code in FALLBACK else None) or country(ev.get("countries"))
            if name not in lookup: unassigned[code].append((name, g, ev.get("birth", ""), "(moved in from " + frm + ")"))
            rows_out.append([name, g, gloss, src, mk, ev.get("birth", "")])
    for l in inp:
        code = l["code"]; rows_out, lookup, groups = leafrows[code]
        for row in EXTRA.get(code, []):
            rows_out.append(list(row) + [row[5] if len(row) > 5 else ""] if len(row) == 5 else list(row))
        order = [g for g, _ in groups]
        extra_groups = [g for g in dict.fromkeys(r[1] for r in rows_out) if g not in order]
        meta = META.get(code, {})
        tail = meta.get("tail_groups", [])
        allg = order + sorted([g for g in extra_groups if g not in tail], key=lambda g: -sum(1 for r in rows_out if r[1] == g)) + [g for g in tail if g in extra_groups]
        if meta.get("group_order"):
            go = meta["group_order"]; allg = [g for g in go if g in allg] + [g for g in allg if g not in go]
        def bkey(r):
            b = str(r[5]) if len(r) > 5 else ""
            try: return int(b) if b else 99999
            except: return 99999
        kinds = []
        for g in allg:
            grp = [r for r in rows_out if r[1] == g]
            if not meta.get("keep_order"):
                grp.sort(key=bkey)
            kinds += [r[:5] for r in grp]
        out = {"axis": meta.get("axis", ""), "catalogues": meta.get("catalogues", []), "kinds": kinds}
        if meta.get("defn"): out["defn"] = meta["defn"]
        ar = list(l.get("alias_rows") or []) + ALIAS.get(code, [])
        if ar: out["alias_rows"] = list(dict.fromkeys(ar))
        res["leaves"][code] = out
    json.dump(res, open(os.path.join(OUT, "result.json"), "w"), ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "unassigned.txt"), "w") as f:
        for code, lst in unassigned.items():
            f.write(f"== {code} ({len(lst)})\n")
            for x in lst: f.write("|".join(map(str, x)) + "\n")
    print({c: len(v) for c, v in unassigned.items()})

main()
