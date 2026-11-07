"""Build result.json for pass small_L (Art in Place, smaller leaves).
Run from repo root: python3 taxonomy/r3/va_out/small_L/build.py
"""
import csv, json, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
from spec import SPEC          # per-leaf catalogue spec (traditions, filters, sections)
from extras import EXTRA, EXIST, NEW_LEAVES, MOVES  # hand-written, attested additions

inp = json.load(open(os.path.join(ROOT, "taxonomy/r3/va_in/small_L.json")))["leaves"]
rows = list(csv.DictReader(open(os.path.join(ROOT, "data/interim/in_situ_exemplars.csv"))))
by = collections.defaultdict(list)
for r in rows: by[r["tradition"]].append(r)

def sl(r): return int(r["sitelinks"] or 0)
def U(r): return r["tier"] in ("unesco_site", "part_of_unesco")
RULES = [
    ("every gathered site with a Wikipedia/Wikimedia article (sitelinks >= 1) or a UNESCO or national heritage listing", lambda r: sl(r) >= 1 or r["tier"] != "none"),
    ("tightened (heritage-register records exceed ~300): every gathered site with a Wikimedia article (sitelinks >= 1) or a UNESCO listing", lambda r: sl(r) >= 1 or U(r)),
    ("tightened (UNESCO component listings exceed ~300): every gathered site with its own Wikimedia article (sitelinks >= 1)", lambda r: sl(r) >= 1),
    ("tightened (single-sitelink fresco records exceed ~300): every gathered item with sitelinks >= 2 or a UNESCO listing", lambda r: sl(r) >= 2 or U(r)),
]
LIMIT = 300

def fmt_date(d):
    try: y = int(float(d))
    except Exception: return ""
    if y < 0: return f"c. {-y} BC"
    return f"c. {y}"

MUSEUM_RE = re.compile(r"\b(?:in|at) (?:the )?((?:[A-Z][\w'’.-]*\s?)*(?:Museum|Museo|Musée|Museu|Muzeum|Gallery|Galleria|Pinacoteca|Bardo|Louvre)(?:[\w\s'’.-]*?)?)(?:,|;| in |$)")

def museum_of(r):
    m = MUSEUM_RE.search(r["description"] or "")
    if not m: return ""
    name = m.group(1).strip().rstrip(".")
    name = re.sub(r"\s+(of|de|di)$", "", name)
    return name

def gloss(r, spec):
    parts = []
    place = (r["place"] or "").split("|")
    country = (r["country"] or "").split("|")[0]
    loc = place[0].strip() if place and place[0] and place[0] != r["site"] else ""
    if re.match(r"^Q\d+$", loc): loc = ""
    locs = ", ".join(x for x in (loc, country) if x)
    if locs: parts.append(locs)
    dt = r["date"]
    try: y = int(float(dt))
    except Exception: y = None
    if y is not None and (y < 1850 or spec.get("modern")):
        parts.append(fmt_date(dt))
    if r["tier"] == "unesco_site": parts.append("UNESCO World Heritage Site")
    elif r["tier"] == "part_of_unesco":
        u = r["unesco"] if r["unesco"].startswith("part of") else "part of a UNESCO World Heritage Site"
        parts.append(u[:70])
    elif r["heritage"]:
        h = r["heritage"].split("|")[0]
        h = {"monument in Fornminnesregistret": "Swedish heritage register (Fornsök)",
             "bien de interés cultural": "Bien de Interés Cultural", "classified historical monument": "Monument historique (classé)",
             "registered historical monument": "Monument historique (inscrit)", "Iranian National Heritage": "Iranian national heritage"}.get(h, h)
        parts.append(h[:60])
    desc = (r["description"] or "").strip()
    w = (r["works"] or "").split("|")[0]
    w = re.sub(r"\s*\(Q\d+\)\s*$", "", w).strip()
    if desc and len(desc) > 6 and not re.search(r"(Q\d{3,}|ACT ID|photo by|unidentified)", desc) and desc.lower() not in ("cave", "mural", "fresco", "monument"):
        if not re.match(r"^(cultural property in|cultural heritage monument in|archaeological site in|rock art in)", desc):
            parts.append(desc[:70])
    elif w and w != r["site"] and len(w) < 70 and not re.search(r"(unide|Q\d{4,})", w):
        parts.append(w)
    g = "; ".join(parts)
    if len(g) > 140: g = g[:137].rsplit(" ", 1)[0] + "..."
    return g

def section_of(r, spec):
    s = spec.get("section")
    if callable(s): return s(r)
    lab = spec.get("trad_groups", {}).get(r["tradition"])
    if lab: return lab
    return spec.get("group", "Sites")

def build_sites(code, spec):
    pool, seen = [], set()
    for t in spec["trad"]:
        lab, inc = (t, None) if isinstance(t, str) else t
        for r in by[lab]:
            if inc and not re.search(inc, r["site"] + " " + r["description"], re.I): continue
            if spec.get("excl") and re.search(spec["excl"], r["site"] + " || " + r["description"], re.I): continue
            if r["qid"] in seen: continue
            seen.add(r["qid"]); pool.append(r)
    rule_i = 0
    sel = [r for r in pool if RULES[0][1](r)]
    while len(sel) > LIMIT and rule_i < len(RULES) - 1:
        rule_i += 1
        sel = [r for r in pool if RULES[rule_i][1](r)]
    if spec.get("rule") is not None:
        rule_i = spec["rule"]; sel = [r for r in pool if RULES[rule_i][1](r)]
    # names: disambiguate duplicates
    cnt = collections.Counter(r["site"].strip() for r in sel)
    out = []
    for r in sel:
        name = r["site"].strip()
        if cnt[name] > 1:
            p = (r["place"] or "").split("|")[0]
            if p and p != name: name = f"{name} ({p})"
            else: name = f"{name} ({r['qid']})"
        out.append((r, name))
    order = spec.get("order", "sitelinks")
    def key(x):
        r = x[0]
        if order == "date":
            try: y = int(float(r["date"]))
            except Exception: y = 99999
            return (y, -sl(r))
        return (-sl(r), not U(r), x[1])
    out.sort(key=key)
    kinds = [[n, section_of(r, spec), gloss(r, spec), f"r3 https://www.wikidata.org/wiki/{r['qid']}", 0] for r, n in out]
    # stable group order
    gorder = spec.get("group_order")
    if gorder:
        rank = {g: i for i, g in enumerate(gorder)}
        kinds.sort(key=lambda k: rank.get(k[1], len(rank)))
    # collections
    coll = []
    if spec.get("collections"):
        mc = collections.Counter(museum_of(r) for r, _ in out if museum_of(r))
        top = [(m, n) for m, n in mc.most_common() if n >= 3][:8]
        for m, n in top:
            coll.append([m, "Collections", f"{m}: {n} detached works in the gathered records", f"r3 https://en.wikipedia.org/wiki/{m.replace(' ', '_')}", 0])
    return kinds, coll, RULES[rule_i][0], len(pool)

def clean_existing(code, r):
    key = (code, r[0])
    if key in EXIST: return EXIST[key]
    g = r[1]
    if g.startswith("Gathered rows"): return ("alias", None)
    return None

def main():
    res = {"leaves": {}, "new_leaves": NEW_LEAVES, "moves_out": MOVES, "dropped": []}
    report = []
    for l in inp:
        code = l["code"]
        ex = EXTRA.get(code, {})
        spec = SPEC.get(code)
        kinds, coll, rule_txt, npool = ([], [], "", 0)
        if spec: kinds, coll, rule_txt, npool = build_sites(code, spec)
        site_names = {k[0].lower() for k in kinds}
        alias_rows = list(l.get("alias_rows", []))
        keep = []
        for r in l["rows"]:
            v = clean_existing(code, r)
            if r[4] == 1 or r[1] in ("Artists", "Architects", "Makers"):
                if v and v[0] == "move": continue  # handled in MOVES
                grp, gl = (v if v and v[0] not in ("drop", "alias", "dup") else (None, None))
                keep.append([r[0], grp or "Makers", gl if gl is not None else re.sub(r";?\s*now T\d+.*$", "", r[2]), r[3], 1])
                continue
            if v is None:
                if r[0].lower() in site_names:
                    res["dropped"].append([code, r[0], "duplicate of the same site in the rule-based catalogue"]); continue
                report.append(f"UNHANDLED {code} {r[:4]}"); continue
            kind = v[0]
            if kind == "alias":
                if r[0] not in alias_rows: alias_rows.append(r[0])
            elif kind == "drop":
                res["dropped"].append([code, r[0], v[1]])
            elif kind == "dup":
                res["dropped"].append([code, r[0], "duplicate of the same site in the rule-based catalogue"])
            else:
                keep.append([v[2] if len(v) > 2 and v[2] else r[0], v[0], v[1], r[3], 0])
        add = ex.get("kinds", [])
        # assemble in section order: Sub-types, Schools & phases, Centres & workshops, (extra pre groups), works, Collections, Makers
        pre_groups = ex.get("pre", ["Sub-types", "Schools & phases", "Centres & workshops"])
        allk = keep + add
        names = set()
        final = []
        def push(k):
            if k[0].lower() in names and k[4] == 0: return
            names.add(k[0].lower()); final.append(k)
        for g in pre_groups:
            for k in allk:
                if k[1] == g: push(k)
        kn = ex.get("knowledge_sites", [])
        # knowledge sites go into their section; merged with data sites by group order
        site_kinds = [k for k in kinds if k[0].lower() not in {x[0].lower() for x in final}]
        for k in site_kinds + [k for k in kn if k[0].lower() not in site_names]:
            push(k)
        for k in allk:
            if k[1] not in pre_groups and k[1] not in ("Makers",) and k[4] == 0 and k[1] != "Collections": push(k)
        for k in coll: push(k)
        for k in allk:
            if k[1] == "Collections" and k[4] == 0: push(k)
        for k in allk:
            if k[4] == 1: push(k)
        axis = ex.get("axis", "")
        if spec and spec.get("bodyart"):
            axis = (axis + " " if axis else "") + "Sub-types include every gathered Wikidata item of the practice (sitelinks >= 1)."
        elif spec and rule_txt:
            axis = (axis + " " if axis else "") + f"Sites catalogue: {rule_txt}" + (f"; {spec['note']}" if spec.get("note") else "") + "."
        entry = {"axis": axis, "catalogues": ex.get("catalogues", []), "kinds": final}
        if ex.get("defn"): entry["defn"] = ex["defn"]
        if alias_rows: entry["alias_rows"] = alias_rows
        res["leaves"][code] = entry
        report.append(f"{code} {l['label'][:30]}: pool {npool} -> {len(kinds)} sites, {len(final)} kinds, cats {len(entry['catalogues'])}")
    json.dump(res, open(os.path.join(HERE, "result.json"), "w"), ensure_ascii=False, indent=1)
    open(os.path.join(HERE, "report.txt"), "w").write("\n".join(report))
    print("\n".join(x for x in report if x.startswith("UNHANDLED")))
    print(len([x for x in report if not x.startswith("UNH")]), "leaves written")

if __name__ == "__main__":
    main()
