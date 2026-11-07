"""Build result.json for pass small_A_B_C.  Run: python3 build.py  (from any cwd)."""
import json, os, re, csv, sys, collections, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
INP = json.load(open(os.path.join(ROOT, "taxonomy/r3/va_in/small_A_B_C.json")))["leaves"]
csv.field_size_limit(10**9)
WIKI = "https://en.wikipedia.org/wiki/"

# ---------------------------------------------------------------- config
CFG = {}
for m in ("cfg_a1", "cfg_a234", "cfg_a5", "cfg_a6", "cfg_b", "cfg_c"):
    try:
        mod = importlib.import_module(m)
        for k, v in mod.CFG.items():
            CFG.setdefault(k, {}).update(v)
    except ModuleNotFoundError:
        pass

# ---------------------------------------------------------------- helpers
CTRY = {
    "German Reich": "Germany", "German Empire": "Germany", "Kingdom of Prussia": "Germany", "Kingdom of Bavaria": "Germany",
    "Lübeck": "Germany", "Duchy of Holstein": "Germany", "West Germany": "Germany", "East Germany": "Germany",
    "Weimar Republic": "Germany", "Nazi Germany": "Germany", "Kingdom of Saxony": "Germany", "Kingdom of Württemberg": "Germany",
    "Kingdom of Hanover": "Germany", "Holy Roman Empire": "Germany", "Electorate of Saxony": "Germany", "German Confederation": "Germany",
    "Kingdom of Italy": "Italy", "Republic of Venice": "Italy", "Papal States": "Italy", "Republic of Siena": "Italy",
    "Republic of Florence": "Italy", "Grand Duchy of Tuscany": "Italy", "Kingdom of Naples": "Italy", "Kingdom of Sardinia": "Italy",
    "Duchy of Milan": "Italy", "Kingdom of the Two Sicilies": "Italy", "Republic of Genoa": "Italy", "Duchy of Mantua": "Italy",
    "Duchy of Ferrara": "Italy", "Duchy of Urbino": "Italy",
    "United Kingdom of Great Britain and Ireland": "United Kingdom", "Kingdom of Great Britain": "United Kingdom",
    "Kingdom of England": "United Kingdom", "England": "United Kingdom", "Scotland": "United Kingdom", "Kingdom of Scotland": "United Kingdom",
    "Kingdom of the Netherlands": "Netherlands", "Dutch Republic": "Netherlands", "Northern Low Countries": "Netherlands",
    "Habsburg Netherlands": "Southern Netherlands", "Burgundian Netherlands": "Southern Netherlands", "Spanish Netherlands": "Southern Netherlands",
    "Kingdom of France": "France", "French Third Republic": "France", "Kingdom of Denmark": "Denmark", "Denmark–Norway": "Denmark",
    "Russian Empire": "Russia", "Soviet Union": "Soviet Union", "Russian Soviet Federative Socialist Republic": "Soviet Union",
    "Russian Socialist Federative Soviet Republic": "Soviet Union", "Russian Republic": "Russia", "Tsardom of Russia": "Russia",
    "Austria–Hungary": "Austria-Hungary", "Austrian Empire": "Austria", "Cisleithania": "Austria", "Archduchy of Austria": "Austria",
    "Kingdom of Serbia": "Serbia", "Kingdom of Portugal": "Portugal", "Crown of Aragon": "Spain", "Kingdom of Castile": "Spain",
    "Crown of Castile": "Spain", "Kingdom of Georgia": "Georgia", "British Raj": "India", "Kingdom of Hungary": "Hungary",
    "Kingdom of Romania": "Romania", "Kingdom of Yugoslavia": "Yugoslavia", "Socialist Federal Republic of Yugoslavia": "Yugoslavia",
    "Kingdom of Sweden": "Sweden", "Swedish Empire": "Sweden", "Kingdom of Norway": "Norway", "Qajar Iran": "Iran",
    "Pahlavi Iran": "Iran", "Kingdom of Iraq": "Iraq", "Empire of Japan": "Japan", "Republic of China": "China", "Qing dynasty": "China",
    "People's Republic of China": "China", "Taiwan": "Taiwan", "Czech Republic": "Czechia", "Czechoslovakia": "Czechoslovakia",
    "Kingdom of Bohemia": "Czechia", "Kingdom of Belgium": "Belgium", "Polish–Lithuanian Commonwealth": "Poland", "Second Polish Republic": "Poland",
    "Polish People's Republic": "Poland", "Congress Poland": "Poland", "Kingdom of Poland": "Poland", "Grand Duchy of Finland": "Finland",
    "Ottoman Empire": "Ottoman Empire", "Mandatory Palestine": "Israel", "Kingdom of Egypt": "Egypt", "Kingdom of Greece": "Greece",
    "Second Hellenic Republic": "Greece", "Joseon": "Korea", "Korean Empire": "Korea", "South Korea": "South Korea",
    "Mexican Empire": "Mexico", "New Spain": "Mexico", "Viceroyalty of Peru": "Peru", "Viceroyalty of New Spain": "Mexico",
    "Kingdom of Bulgaria": "Bulgaria", "Kingdom of Croatia": "Croatia", "Independent State of Croatia": "Croatia",
    "Q1006": "Guinea", "Kingdom of Spain": "Spain", "Francoist Spain": "Spain", "Second Spanish Republic": "Spain",
}
MACHINE = re.compile(r"(movement |other movements|country group|P1066|P106\b|now T\d|route resolved|excluded row|artist_placements|"
                     r"Gathered rows|makers_\d|canonical|wiki:|\bQ\d{3,}|named maker|named illuminator|pilot leaf|seeded|blind test|"
                     r"in evidence|alias list|\brow\b|rows\b|routed |pool sample|sample manuscript|\(\d+\)$|school art-name|dup of|"
                     r"Possession|^\s*uncertain\s*$|see-also|their L\d|kind under|kinds under|\bL\d+\b|\bT\d{2,3}\b|\b[A-M]\d+-\d+\b|"
                     r"label not attested|mis-linked|noise|cleaned name|role unclear|islamic_world|evidence)", re.I)


def norm_ctry(s):
    out = []
    for c in [x.strip() for x in (s or "").split(",") if x.strip()]:
        c = CTRY.get(c, c)
        if c not in out:
            out.append(c)
    return out


def clean_gloss(g):
    """Drop machine segments from a gloss; keep human text."""
    if not g:
        return ""
    g = re.sub(r"<[^>]+>", "", g)
    segs = re.split(r";\s*|\s+·\s+", g)
    keep = [s.strip() for s in segs if s.strip() and not MACHINE.search(s)]
    out = "; ".join(keep)
    return out[:140]


def possession(g, src):
    """Return (gloss, source) with Possession backlink normalised."""
    m = re.search(r"owned as (.+?) \(Possession ([A-Z]\d+)\)", g or "")
    url = re.search(r"https?://\S+", g or "")
    base = re.split(r"\s*·\s*owned as", g or "")[0].strip(" ·")
    base = clean_gloss(base)
    if m:
        tail = f"Possession: {m.group(1)} ({m.group(2)})"
        base = (base[: 138 - len(tail) - 3] + " · " + tail) if base else tail
    s = src
    if url and "http" not in src:
        s = f"{src} {url.group(0)}"
    return base, s


def artist_gloss(r, label):
    ev = r[5] if len(r) > 5 and isinstance(r[5], dict) else {}
    g = r[2] or ""
    human = "" if MACHINE.search(g) else clean_gloss(g)
    if r[3].startswith("possession"):
        return None
    parts = []
    if human:
        parts.append(human)
    med = ev.get("medium", "")
    if med and med != "visual art (unspecified)" and not human:
        parts.append(med)
    cs = norm_ctry(ev.get("countries", ""))
    if cs and not human:
        parts.append(", ".join(cs[:3]))
    if ev.get("birth"):
        parts.append("b. " + ev["birth"])
    mv = [m for m in (ev.get("movements") or "").split("|") if m and not re.match(r"Q\d+", m) and m.lower() != label.lower()]
    if mv and not human:
        parts.append("also " + ", ".join(mv[:2]))
    return " · ".join(parts)[:140]


GROUP_STD = {
    "sub-type": "Sub-types", "type": "Sub-types", "format": "Sub-types", "genre": "Sub-types", "style": "Sub-types",
    "people": "Sub-types", "school": "Schools & phases", "phase": "Schools & phases", "movement": "Schools & phases",
    "sub-school": "Schools & phases", "centre": "Centres & workshops", "centres": "Centres & workshops",
    "workshop": "Centres & workshops", "art centre": "Centres & workshops", "scribe": "Makers", "maker": "Makers",
    "makers": "Makers", "Artists": "Makers", "maker (painting)": "Makers", "maker (sculpture)": "Makers",
}

MS = None


def load_ms():
    global MS
    if MS is None:
        MS = list(csv.DictReader(open(os.path.join(ROOT, "data/interim/manuscripts_items.csv"))))
        for x in MS:
            try:
                x["_sl"] = int(x["sitelinks"] or 0)
            except ValueError:
                x["_sl"] = 0
            try:
                x["_y"] = int(x["year"]) if x["year"] else None
            except ValueError:
                x["_y"] = None
    return MS


def fmt_year(y):
    if y is None:
        return ""
    return f"{-y} BC" if y < 0 else f"c. {y}" if y % 50 == 0 else str(y)


def ms_works(spec):
    """Every manuscript of the tradition(s) passing the rule, sectioned."""
    ms = load_ms()
    trad = set(spec.get("trad", []))
    minsl = spec.get("minsl", 1)
    flt = spec.get("filter", lambda x: True)
    sect = spec.get("section", lambda x: spec.get("group", "Named manuscripts"))
    rows, seen = [], set()
    for x in ms:
        if trad and x["tradition"] not in trad:
            continue
        if x["_sl"] < minsl or not flt(x):
            continue
        lab = x["label"].strip()
        if not lab or re.fullmatch(r"Q\d+", lab) or lab.lower() in seen:
            continue
        seen.add(lab.lower())
        g = sect(x)
        if not g:
            continue
        place = (x["origin"] or "").split(";")[0].strip()
        coll = "; ".join(c.strip() for c in (x["collections"] or "").split(";")[:2] if c.strip())
        bits = [b for b in (place, fmt_year(x["_y"])) if b]
        gl = ", ".join(bits)
        if coll:
            gl = (gl + "; " if gl else "") + coll
        rows.append([lab[:120], g, gl[:140], "r3 https://www.wikidata.org/wiki/" + x["qid"], 0, x["_y"] if x["_y"] is not None else 9999, -x["_sl"]])
    order = spec.get("order")
    rows.sort(key=lambda r: ((order.index(r[1]) if order and r[1] in order else 99), r[5], r[6]))
    return [r[:5] for r in rows]


def ms_collections(spec, n=8, minc=10):
    ms = load_ms()
    trad = set(spec.get("trad", []))
    flt = spec.get("cfilter", spec.get("filter", lambda x: True))
    c = collections.Counter()
    for x in ms:
        if trad and x["tradition"] not in trad:
            continue
        if not flt(x):
            continue
        for k in (x["collections"] or "").split(";"):
            k = k.strip()
            if k:
                c[k] += 1
    return c


OBJ = {}


def load_obj(fn):
    if fn not in OBJ:
        OBJ[fn] = list(csv.DictReader(open(os.path.join(ROOT, "data/interim/regional", fn))))
    return OBJ[fn]


INST_COL = {"europe_folk_objects.csv": "institution", "world_folk_objects.csv": "institution", "east_asia_objects.csv": "holder",
            "smithsonian_objects.csv": "unit"}
SI_UNITS = {"CHNDM": "Cooper Hewitt, Smithsonian Design Museum, New York", "FSG": "National Museum of Asian Art (Freer|Sackler), Washington",
            "NMAI": "National Museum of the American Indian, Washington", "NMAfA": "National Museum of African Art, Washington",
            "SAAM": "Smithsonian American Art Museum, Washington", "NMAH": "National Museum of American History, Washington",
            "NMNHAnthro": "National Museum of Natural History (Anthropology), Washington", "HMSG": "Hirshhorn Museum, Washington",
            "NPG": "National Portrait Gallery, Washington", "NMNH": "National Museum of Natural History, Washington", "ACM": "Anacostia Community Museum, Washington"}


def obj_collections(specs):
    c = collections.Counter()
    for fn, flt in specs:
        col = INST_COL.get(fn, "institution")
        for x in load_obj(fn):
            try:
                ok = flt(x)
            except Exception:
                ok = False
            if ok:
                inst = (x.get(col) or "").strip()
                if fn == "smithsonian_objects.csv":
                    inst = SI_UNITS.get(inst, inst)
                if inst:
                    c[inst] += 1
    return c


def coll_rows(counter, what="objects", n=8, minc=10):
    items = counter.most_common()
    big = [(k, v) for k, v in items if v >= minc]
    if len(big) < n:
        big = items[:n]
    rows = []
    for k, v in big:
        if v < 2 and len(rows) >= 3:
            break
        rows.append([k[:110], "Collections", f"{v} {what if v != 1 else what.rstrip('s')} in the gathered records", "r3 https://www.wikidata.org/wiki/Special:Search?search=" + k.replace(" ", "+")[:80], 0])
    return rows


# ---------------------------------------------------------------- per leaf
def build_leaf(l):
    code, label = l["code"], l["label"]
    cfg = CFG.get(code, {})
    kinds, alias, dropped, moves = [], list(cfg.get("alias", [])), [], []
    regroup = cfg.get("regroup", {})
    gloss_fix = cfg.get("gloss", {})
    rename = cfg.get("rename", {})
    drop = cfg.get("drop", {})
    mv = cfg.get("moves", {})
    to_alias = set(cfg.get("to_alias", []))
    home = cfg.get("home")
    artist_led = cfg.get("artist_led", False)
    for r in l["rows"]:
        name, grp, gl, src, ism = r[0], r[1], r[2], r[3], r[4]
        maker_in = bool(ism) or grp in ("Artists", "Architects", "Makers")
        if not name.strip():
            moves.append([name, code, "A5-111"])
            continue
        if name in mv:
            moves.append([name, code, mv[name]])
            continue
        if name in drop:
            if maker_in:
                raise SystemExit(f"cannot drop maker {name} in {code}")
            dropped.append([code, name, drop[name]])
            continue
        if (name in to_alias or grp.startswith("Gathered rows")) and name not in regroup and not maker_in:
            alias.append(name)
            continue
        # gloss
        if src.startswith("possession"):
            g2, src2 = possession(gl, src)
        else:
            g2, src2 = None, src
        if g2 is None:
            if src == "artists" or (maker_in and len(r) > 5):
                g2 = artist_gloss(r, label) or ""
            else:
                g2 = clean_gloss(gl)
        if name in gloss_fix:
            g2 = gloss_fix[name]
        # maker flag
        person = maker_in or grp in ("maker", "makers", "scribe", "maker (painting)", "maker (sculpture)") or name in cfg.get("persons", ())
        if name in cfg.get("nonpersons", ()):
            person = False if not maker_in else True
        # group
        if name in regroup:
            g = regroup[name]
        elif person and artist_led:
            ev = r[5] if len(r) > 5 and isinstance(r[5], dict) else {}
            keepg = grp not in ("Artists", "", "maker", "makers", "Makers")
            if keepg and not grp.startswith("Gathered"):
                g = cfg.get("grp_map", {}).get(grp, grp)
            else:
                cs = norm_ctry(ev.get("countries", ""))
                g = home if home and home in cs else (cs[0] if cs else cfg.get("default_group", home or "Makers"))
                g = cfg.get("ctry_map", {}).get(g, g)
        elif person:
            g = cfg.get("grp_map", {}).get(grp, cfg.get("maker_group", "Makers")) if grp not in ("", "Artists", "maker", "makers") else cfg.get("maker_group", "Makers")
        else:
            g = cfg.get("grp_map", {}).get(grp) or GROUP_STD.get(grp) or cfg.get("default_nonmaker", "Sub-types")
        name2 = rename.get(name, name)
        kinds.append([name2, g, g2, src2, 1 if person else 0])
    # added rows
    for a in cfg.get("add", []):
        nm, g, gl, url, im = a
        if not url.startswith("http"):
            url = WIKI + url.replace(" ", "_")
        kinds.append([nm, g, gl[:140], "r3 " + url, im])
    # works
    if cfg.get("ms"):
        kinds += ms_works(cfg["ms"])
    # collections
    if cfg.get("coll_ms") or cfg.get("coll_obj"):
        c = collections.Counter()
        what = cfg.get("coll_what", "objects")
        if cfg.get("coll_ms"):
            c += ms_collections(cfg["coll_ms"])
            what = cfg.get("coll_what", "manuscripts")
        if cfg.get("coll_obj"):
            c += obj_collections(cfg["coll_obj"])
        kinds += coll_rows(c, what, minc=cfg.get("coll_min", 10))
    # dedupe exact names (non-makers only)
    seen, out = set(), []
    for k in kinds:
        key = (k[0].lower(), k[4])
        if key in seen and not k[4]:
            dropped.append([code, k[0], "duplicate of another row"])
            continue
        seen.add(key)
        out.append(k)
    kinds = out
    # order groups
    order = cfg.get("order") or []
    std = ["Sub-types", "Schools & phases", "Centres & workshops"]
    def gkey(k):
        g = k[1]
        if g in order:
            return (order.index(g),)
        if g in std:
            return (-10 + std.index(g),)
        if g == "Collections":
            return (900,)
        if g == "Makers":
            return (950,)
        return (500,)
    first_seen = {}
    for i, k in enumerate(kinds):
        first_seen.setdefault(k[1], i)
    kinds = sorted(kinds, key=lambda k: (gkey(k), first_seen[k[1]]))
    leaf = {"axis": cfg.get("axis", ""), "catalogues": [list(c) for c in cfg.get("cat", [])], "kinds": kinds,
            "alias_rows": sorted(set(alias), key=alias.index)}
    if cfg.get("defn"):
        leaf["defn"] = cfg["defn"]
    return leaf, dropped, moves


def main():
    res = {"leaves": {}, "new_leaves": [], "moves_out": [], "dropped": []}
    for l in INP:
        leaf, dr, mv = build_leaf(l)
        res["leaves"][l["code"]] = leaf
        res["dropped"] += dr
        res["moves_out"] += mv
    json.dump(res, open(os.path.join(HERE, "result.json"), "w"), ensure_ascii=False, indent=1)
    print("leaves", len(res["leaves"]), "kinds", sum(len(v["kinds"]) for v in res["leaves"].values()),
          "moves", len(res["moves_out"]), "dropped", len(res["dropped"]))


if __name__ == "__main__":
    main()
