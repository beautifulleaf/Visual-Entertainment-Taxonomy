"""Assemble result.json for pass small_K from the input, catalog.json, subrows.py and cats.py."""
import csv, json, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.join(HERE, "../../../..")
from subrows import R as SUB
from cats import catalogues, AXIS_NOTE, DEFN
from config import S

inp = json.load(open(os.path.join(ROOT, "taxonomy/r3/va_in/small_K.json")))["leaves"]
CAT = json.load(open(os.path.join(HERE, "catalog.json")))
ARCH = {}
for r in csv.DictReader(open(os.path.join(ROOT, "data/interim/architecture_architects.csv"))):
    ARCH.setdefault(r["label"], r); ARCH.setdefault(r["qid"], r)

MAKER_GLOSS = {
    "Musō Soseki": "Zen monk and garden designer (1275–1351): Saihō-ji and Tenryū-ji, Kyoto",
    "Pirro Ligorio": "Architect and antiquarian (c. 1512–1583), designer of the Villa d'Este gardens, Tivoli",
    "Niccolò Tribolo": "Sculptor and garden designer (1497–1550): Villa di Castello and the first Boboli plan",
    "Bernardo Buontalenti": "Architect (1531–1608): Pratolino garden and the Boboli Grotto, Florence",
    "André Le Nôtre": "Royal gardener of Louis XIV (1613–1700): Vaux-le-Vicomte, Versailles, Chantilly",
    "William Kent": "Architect and garden designer (c. 1685–1748): Rousham, Stowe, Chiswick",
    "Capability Brown": "Landscape architect (1716–1783) of some 170 parks: Blenheim, Petworth, Croome",
    "Humphry Repton": "Landscape gardener (1752–1818), author of the Red Books",
    "Al-Hakim bi-Amr Allah": "Fatimid caliph (r. 996–1021), completer and patron of the al-Hakim Mosque, Cairo",
    "Mehmed II": "Ottoman sultan (r. 1444–46, 1451–81), patron of the Fatih Mosque and Topkapı Palace",
    "Prince Albert of Saxe-Coburg and Gotha": "Prince consort (1819–1861), co-designer of Osborne House",
    "Bess of Hardwick": "Builder of Hardwick Hall and the first Chatsworth House (c. 1527–1608)",
}
MOVES = {("I. M. Pei", "K2-12"): "K6-22"}
RELOC = {("Helmut Jahn", "K2-13"): "K6-19", ("Werner Sobek", "K2-13"): "K6-19"}

def clean_arch_gloss(name, g):
    if name in MAKER_GLOSS: return MAKER_GLOSS[name]
    g = g or ""
    m = re.match(r"\d+ exemplar building\(s\): (.*)", g)
    if m:
        b = re.sub(r"\s*\|.*$", "", m.group(1)); b = re.sub(r"\s*\(Q\d+\)\s*$", "", b).strip()
        a = ARCH.get(name)
        life = f" ({a['birth'][:4]}–{a['death'][:4]})" if a and a.get("birth") else ""
        return (f"Architect{life}; " + b)[:140]
    m = re.search(r"architecture_architects\.csv (Q\d+)", g)
    a = ARCH.get(m.group(1)) if m else ARCH.get(name)
    if m or not g:
        if a:
            life = f"{a['birth'][:4]}–{a['death'][:4]}" if a.get("birth") else ""
            cit = a["citizenship"].split("|")[0]
            works = "; ".join(a["buildings_label"].split("|")[:2])
            s = ", ".join(x for x in (f"{cit} architect" if cit else "Architect", life) if x)
            return (s + (f"; {works}" if works else ""))[:140]
        return "Architect" if not g or m else g
    g = re.sub(r"cleaned name [^;]*;?\s*", "", g); g = re.sub(r";?\s*see-also \S+", "", g)
    g = g.replace("; uncertain", " (attribution uncertain)").strip(" ;")
    return g[:140]

def birth(name):
    a = ARCH.get(name)
    try: return int(a["birth"][:4]) if a and a.get("birth") else 9999
    except ValueError: return 9999

def clean_poss(g, src):
    url = None
    m = re.search(r"\s*·\s*(https?://\S+)", g)
    if m: url = m.group(1); g = g.replace(m.group(0), "")
    m = re.search(r"owned as (.+?) \(Possession (\w+)\)", g)
    if m: g = re.sub(r"\s*·?\s*owned as .+? \(Possession \w+\)", "", g).strip(" ·") + f" · Possession: {m.group(1)} ({m.group(2)})"
    g = g.strip(" ·")
    if url and "http" not in src: src = f"{src} {url}"
    return g[:140], src

def is_maker(r): return bool(r[4]) or r[1] in ("Architects", "Makers", "Artists", "makers")
SUBGROUPS = ("Sub-styles", "Sub-types", "Centres & workshops")

out = {"leaves": {}, "new_leaves": [], "moves_out": [], "dropped": []}
reloc_rows = collections.defaultdict(list)
for l in inp:
    code = l["code"]
    rows = l["rows"]; byname = {}
    for r in rows: byname.setdefault(r[0], r)
    used = set()
    sub, extra = [], []
    for name, grp, gloss, ref in SUB.get(code, []):
        if ref.startswith("http"):
            row = [name, grp, gloss, f"r3 {ref}", 1 if grp == "Makers" else 0]
        else:
            if ref not in byname: print(f"MISSINGREF {code}: {ref!r}"); continue
            src = byname[ref][3]
            if src.startswith("possession"): _, src = clean_poss(byname[ref][2], src)
            row = [name, grp, gloss, src, 0]; used.add(ref)
        (sub if grp in SUBGROUPS else extra).append(row)
    archs, aliases = [], list(dict.fromkeys(l["alias_rows"]))
    for r in rows:
        if r[0] in used: continue
        if is_maker(r):
            if (r[0], code) in MOVES: out["moves_out"].append([r[0], code, MOVES[(r[0], code)]]); continue
            row = [r[0], "Makers" if code.startswith(("K13", "K14")) else "Architects", clean_arch_gloss(r[0], r[2]), r[3], 1]
            if (r[0], code) in RELOC: reloc_rows[RELOC[(r[0], code)]].append(row); continue
            archs.append(row); continue
        if r[3].startswith("possession"):
            g, src = clean_poss(r[2], r[3])
            sub.append([r[0], "Sub-types", g, src, 0]); continue
        if r[1].startswith("Gathered rows") and r[3].startswith("architecture"):
            if " — " in r[0] or "/" in r[0] or "(" in r[0]:
                out["dropped"].append([code, r[0], "internal bucket label of the gathered data; its buildings are listed in the catalogue sections"])
            elif r[0] not in aliases: aliases.append(r[0])
            continue
        if r[3].startswith("architecture") and r[0].lower() in (l["label"].lower(), l["label"].lower().replace(" architecture", "")):
            if r[0] not in aliases: aliases.append(r[0])
            continue
        out["dropped"].append([code, r[0], "style or bucket label of the gathered data, duplicated by a named sub-style row or by the catalogue sections"])
    # catalogue sections
    cat = CAT.get(code, {"sections": []})
    names_present = {x[0].lower() for x in sub + extra}
    works = []
    for lab, items in cat["sections"]:
        seen_lab = collections.Counter(b["label"] for b in items)
        for b in items:
            nm = b["label"]
            if nm.lower() in names_present: continue
            if seen_lab[nm] > 1: nm = f"{nm} ({b['country']})" if b["country"] else nm
            works.append([nm, lab, b["gloss"], f"r3 https://www.wikidata.org/wiki/{b['qid']}", 0])
    # knowledge rows that fall into a catalogue-section name go right after that section; others after all sections
    order = {"Sub-styles": 0, "Sub-types": 1, "Centres & workshops": 2}
    sub.sort(key=lambda r: order[r[1]])
    makers_extra = [r for r in extra if r[1] == "Makers"]
    extra = [r for r in extra if r[1] != "Makers"]
    archs.sort(key=lambda r: (birth(r[0]), r[0]))
    secmap = collections.OrderedDict()
    for r in works: secmap.setdefault(r[1], []).append(r)
    tail = collections.OrderedDict()
    for r in extra:
        (secmap if r[1] in secmap else tail).setdefault(r[1], []).append(r)
    works = [r for v in secmap.values() for r in v] + [r for v in tail.values() for r in v]
    kinds = sub + works + archs + makers_extra
    # dedupe identical names within a group
    seen = set(); final = []
    for r in kinds:
        k = (r[0], r[1])
        if k in seen and not r[4]: continue
        seen.add(k); final.append(r)
    out["leaves"][code] = {"axis": AXIS_NOTE(code, l, cat, final), "catalogues": catalogues(code, l), "kinds": final, "alias_rows": aliases}
    if code in DEFN: out["leaves"][code]["defn"] = DEFN[code]
for code, rows in reloc_rows.items():
    k = out["leaves"][code]["kinds"]; k.extend(rows)
json.dump(out, open(os.path.join(HERE, "result.json"), "w"), ensure_ascii=False, indent=1)
n = sum(len(v["kinds"]) for v in out["leaves"].values())
print("leaves", len(out["leaves"]), "kinds", n, "dropped", len(out["dropped"]), "moves", len(out["moves_out"]))
