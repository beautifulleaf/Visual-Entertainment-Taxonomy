"""Build the rule-based building catalogues for every leaf of pass small_K (writes catalog.json)."""
import csv, json, os, re, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from config import S, yr

ROOT = os.path.join(os.path.dirname(__file__), "../../../..")
A = list(csv.DictReader(open(os.path.join(ROOT, "data/interim/architecture_exemplars.csv"))))
N = list(csv.DictReader(open(os.path.join(ROOT, "data/interim/architecture_nonwestern_exemplars.csv"))))
WI = collections.defaultdict(list); NI = collections.defaultdict(list)
for r in A:
    if r["style_label"]: WI[r["style_label"]].append(r)
for r in N:
    if r["proposed_style"]: NI[r["proposed_style"]].append(r)
II = collections.defaultdict(list)
for r in A:
    for i in r["instance_of_label"].split("|"):
        if i: II[i].append(r)

JREG = {}
for reg, prefs in {
    "Hokkaidō and Tōhoku": "Hokkaido Aomori Iwate Miyagi Akita Yamagata Fukushima",
    "Kantō": "Ibaraki Tochigi Gunma Saitama Chiba Tokyo Kanagawa",
    "Chūbu": "Niigata Toyama Ishikawa Fukui Yamanashi Nagano Gifu Shizuoka Aichi",
    "Kansai": "Mie Shiga Kyoto Osaka Hyōgo Hyogo Nara Wakayama",
    "Chūgoku": "Tottori Shimane Okayama Hiroshima Yamaguchi",
    "Shikoku": "Tokushima Kagawa Ehime Kōchi Kochi",
    "Kyūshū and Okinawa": "Fukuoka Saga Nagasaki Kumamoto Ōita Oita Miyazaki Kagoshima Okinawa",
}.items():
    for p in prefs.split(): JREG[p] = reg

NONLATIN = re.compile(r"[԰-᷿⺀-￿]")
CLASSNAME = {"hindu_temple": "temple", "buddhist_temple": "temple", "shinto_shrine": "shrine", "tibetan_monastery": "monastery", "japanese_castle": "castle",
             "chinese_temple": "temple", "taoist_temple": "Taoist temple", "korean_temple": "temple", "khmer_temple": "temple", "jain_temple": "Jain temple",
             "archaeological_site": "archaeological site", "ancient_city": "ancient city", "rock_cut": "rock-cut monument", "cave_temple": "cave temple",
             "cliff_dwelling": "cliff dwelling", "meso_pyramid": "pyramid", "chinese_pagoda": "pagoda", "monolithic_church": "monolithic church", "rock_cut_church": "rock-cut church"}

def norm(r, src):
    if src == "W":
        her = r["heritage_label"].split("|")
        her = [h for h in her if h and h != "World Heritage Site"]
        typ = (r["instance_of_label"].split("|")[0] or "").strip()
        return dict(qid=r["qid"], label=r["label"], sl=int(r["sitelinks"] or 0), unesco=bool(r["unesco_id"]),
                    her=bool(r["heritage_label"]) or bool(r["unesco_id"]), herlabel=her[0] if her else "", place="", country=r["country_label"].split("|")[0],
                    continent=r["continent"], region="", year=yr(r), typ=typ, cls=typ, unesco_site="", tier=r["tier_label"], inception=r["inception"])
    cls = [c for c in r["class"].split("|") if c]
    spec = [c for c in cls if c in CLASSNAME] or cls
    typ = CLASSNAME.get(spec[0], spec[0].replace("_", " ")) if spec else ""
    adm = [a for a in r["admin"].split("|") if a and a != r["country"]]
    return dict(qid=r["qid"], label=r["label"], sl=int(r["sitelinks"] or 0), unesco=r["tier"] in ("unesco_site", "part_of_unesco"),
                her=bool(r["heritage"]) or r["tier"] in ("unesco_site", "part_of_unesco"), herlabel=(r["heritage"].split("|")[0] if r["heritage"] else ""),
                place=(adm[0] if adm and adm[0] != r["country"].split("|")[0] else ""), adm=adm, country=r["country"].split("|")[0], continent="", region=r["region"], year=yr(r), typ=typ, cls=typ,
                unesco_site=r["unesco_site"], tier=r["tier"], inception=r["inception"])

def passes(b, t):
    if NONLATIN.search(b["label"]) or re.fullmatch(r"Q\d+", b["label"]) or not b["label"].strip():
        return False
    if t == 1:
        return b["sl"] >= 1 or b["her"]
    return b["sl"] >= t or b["unesco"]

def gloss(b):
    parts = []
    t = b["typ"]
    loc = ", ".join(x for x in (b["place"], b["country"]) if x)
    head = (t[:1].upper() + t[1:]) if t else ""
    s = ", ".join(x for x in (head, loc) if x)
    if b["year"] is not None:
        y = b["year"]; s += f", {abs(y)} BC" if y < 0 else f", {y}"
    parts.append(s or "Building")
    if b["tier"] == "unesco_site" or (b["tier"] == "unesco"):
        parts.append("UNESCO World Heritage Site")
    elif b["unesco"]:
        parts.append("part of UNESCO site" + (f" {b['unesco_site']}" if b["unesco_site"] else ""))
    elif b["herlabel"]:
        parts.append(b["herlabel"])
    g = " · ".join(parts)
    if len(g) > 140: g = parts[0]
    return g[:140]

def key_for(b, mode):
    if mode == "country": return b["country"] or "other"
    if mode == "class": return b["cls"] or "other"
    if mode == "region": return b["region"] or "region unassigned"
    if mode == "place":
        ds = [a for a in b.get("adm", []) if "district" in a.lower() or "department" in a.lower() or "province" in a.lower()]
        return ds[0] if ds else "region unassigned"
    if mode == "century":
        y = b["year"]
        if y is None: return "region unassigned"
        c = (y - 1) // 100 + 1 if y > 0 else 0
        suf = "th" if 10 <= c % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(c % 10, "th")
        return f"{c}{suf} century"
    if mode == "jregion":
        reg = b["region"].replace(" Prefecture", "").replace("Prefecture", "").strip()
        for p, R in JREG.items():
            if reg.startswith(p): return R
        return "region unassigned"
    return ""

def build(code, threshold=None):
    cfg = S.get(code)
    if not cfg or not cfg["secs"]:
        return dict(t=None, total=0, sections=[])
    def collect(t):
        seen = set(); secs = []
        for sec in cfg["secs"]:
            lab, srcs = sec[0], sec[1]; f = sec[2] if len(sec) > 2 else None
            items = []
            for s in srcs:
                kind, name = s.split(":", 1)
                pool = WI.get(name, []) if kind == "W" else NI.get(name, []) if kind == "N" else II.get(name, [])
                for r in pool:
                    if f and not f(r): continue
                    b = norm(r, "N" if kind == "N" else "W")
                    if b["qid"] in seen: continue
                    if any(x.lower() in b["label"].lower() for x in cfg["black"]): continue
                    if not passes(b, t): continue
                    seen.add(b["qid"]); items.append(b)
            secs.append((lab, items))
        return secs
    ts = [threshold] if threshold else [1, 3, 5, 8, 12, 20, 30]
    for t in ts:
        secs = collect(t)
        total = sum(len(i) for _, i in secs)
        if total <= 400: break
    out = []
    for lab, items in secs:
        if not items: continue
        items.sort(key=lambda b: (b["year"] is None, b["year"] or 0, -b["sl"], b["label"]))
        done = False
        modes = cfg["split"] if isinstance(cfg["split"], list) else ([cfg["split"]] if cfg["split"] else [])
        for mode in (modes if len(items) > 60 else []):
            groups = collections.OrderedDict()
            for b in items: groups.setdefault(key_for(b, mode), []).append(b)
            okk = lambda k, v: len(v) >= 5 and k not in ("other", "region unassigned", "")
            big = [(k, v) for k, v in groups.items() if okk(k, v)]
            small = [b for k, v in groups.items() if not okk(k, v) for b in v]
            big.sort(key=lambda kv: (kv[0] if mode == 'century' else '', -len(kv[1])))
            if len(big) >= 2 and len(big[0][1]) < 0.85 * len(items):
                for k, v in big: out.append((f"{lab}: {k}", v))
                if small:
                    small.sort(key=lambda b: (b["year"] is None, b["year"] or 0, -b["sl"], b["label"]))
                    out.append((f"{lab}: other " + ("types" if mode == "class" else "dates and undated" if mode == "century" else "regions"), small))
                done = True
                break
        if done: continue
        out.append((lab, items))
    return dict(t=t, total=total, sections=out)

if __name__ == "__main__":
    res = {}
    for code in S:
        r = build(code)
        res[code] = r
        print(code, "t=", r["t"], "total", r["total"], "|", "; ".join(f"{l} {len(i)}" for l, i in r["sections"])[:400])
    json.dump({c: dict(t=r["t"], total=r["total"], sections=[(l, [dict(qid=b["qid"], label=b["label"], gloss=gloss(b), year=b["year"], sl=b["sl"], country=b["country"]) for b in i]) for l, i in r["sections"]]) for c, r in res.items()},
              open(os.path.join(os.path.dirname(__file__), "catalog.json"), "w"), ensure_ascii=False, indent=0)
