"""VA facets (owner, 2026-11-07): every Visual Art leaf gets a region and a period, so that culture and period work as
the filters the page promises ("dynasties, periods, places and cultures are filters, not nodes") and so that large
sub-families can be shown in region groups.

Region: the project's 20 regions (pipelines/visual_art/coverage_audit.py, used for the sourcing coverage grid), from
its country and keyword mapping applied to the leaf's label, then definition, then aliases (the earliest match in the
text wins), corrected by era
(era_fix); "Transnational" for international modes with no single origin. Leaves the mapping cannot place are
assigned by origin in taxonomy/r3/va_facets_overrides.csv, which wins over the rule.
Period: (start, end) years from the definition: years, centuries, millennia, decades and the names of dynasties and
periods (DYN); failing that, the 10th–90th percentile of the dates of the museum objects mapped to the leaf (at least
5 dated objects), then of the dates in the leaf's own entries (at least 4); leaves still undated are living traditions
whose sources give no dates and are listed as "undated"; overrides as above. Era (the coverage grid's): antiquity < 500, early 500–1399, late 1400–1859,
modern 1860–1959, contemporary 1960 on.

Writes taxonomy/r3/va_facets.csv (code, label, region, start, end, how) and prints what the rules could not decide.
assemble.py calls compute() on the tree it builds and attaches region, period and eras to every leaf;
python3 pipelines/r3/va_facets.py runs it on the published data for review.
"""
import csv, json, os, re, unicodedata

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
R3 = os.path.join(ROOT, "taxonomy", "r3")

import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "visual_art"))
import coverage_audit as CA  # noqa: E402
REGIONS = CA.REGIONS + ["Transnational"]
ERAS = [("antiquity", -99999, 499), ("early", 500, 1399), ("late", 1400, 1859), ("modern", 1860, 1959), ("contemporary", 1960, 9999)]


DYN = {  # names of dynasties and periods -> (start, end)
 "shang": (-1600, -1046), "zhou": (-1046, -256), "warring states": (-475, -221), "qin": (-221, -206), "han": (-206, 220),
 "six dynasties": (220, 589), "sui": (581, 618), "tang": (618, 907), "five dynasties": (907, 979), "liao": (907, 1125),
 "song": (960, 1279), "northern song": (960, 1127), "southern song": (1127, 1279), "jin": (1115, 1234), "yuan": (1271, 1368),
 "ming": (1368, 1644), "qing": (1644, 1912), "jomon": (-14000, -300), "yayoi": (-300, 300), "kofun": (300, 538),
 "asuka": (538, 710), "nara": (710, 794), "heian": (794, 1185), "kamakura": (1185, 1333), "muromachi": (1336, 1573),
 "momoyama": (1573, 1615), "edo": (1615, 1868), "meiji": (1868, 1912), "taisho": (1912, 1926), "showa": (1926, 1989),
 "three kingdoms": (-57, 668), "silla": (-57, 935), "unified silla": (668, 935), "goryeo": (918, 1392), "joseon": (1392, 1897),
 "achaemenid": (-550, -330), "parthian": (-247, 224), "sasanian": (224, 651), "umayyad": (661, 750), "abbasid": (750, 1258),
 "fatimid": (909, 1171), "seljuk": (1037, 1308), "seljuq": (1037, 1308), "ilkhanid": (1256, 1353), "mamluk": (1250, 1517),
 "timurid": (1370, 1507), "safavid": (1501, 1736), "ottoman": (1299, 1922), "qajar": (1789, 1925), "mughal": (1526, 1857),
 "nasrid": (1238, 1492), "gupta": (320, 550), "kushan": (30, 375), "pala": (750, 1174), "chola": (848, 1279),
 "vijayanagara": (1336, 1646), "angkor": (802, 1431), "khmer": (802, 1431), "ayutthaya": (1351, 1767), "sukhothai": (1238, 1438),
 "majapahit": (1293, 1527), "byzantine": (330, 1453), "carolingian": (751, 888), "ottonian": (919, 1024),
 "romanesque": (1000, 1200), "gothic": (1140, 1500), "renaissance": (1400, 1600), "baroque": (1600, 1750), "rococo": (1720, 1780),
 "neoclassical": (1750, 1850), "victorian": (1837, 1901), "minoan": (-3000, -1100), "mycenaean": (-1750, -1050),
 "cycladic": (-3200, -2000), "hellenistic": (-323, -31), "old kingdom": (-2686, -2181), "middle kingdom": (-2055, -1650), "new kingdom": (-1550, -1069),
 "predynastic": (-4400, -3100), "inca": (1438, 1533), "aztec": (1325, 1521), "moche": (100, 800), "nazca": (-100, 800),
 "paracas": (-800, -100), "wari": (600, 1000), "chimu": (900, 1470), "olmec": (-1500, -400), "teotihuacan": (-100, 550),
 "classic maya": (250, 900), "toltec": (900, 1168), "nok": (-1500, 500), "ife": (1000, 1450),
}
CENT = re.compile(r"(\d{1,2})(?:st|nd|rd|th)(?:\s*(?:[–-]|to(?: the)?|and(?: the)?)\s*(?:early |mid-?|late )?(\d{1,2})(?:st|nd|rd|th))?\s*(?:-|\s)?centur(?:y|ies)(\s*(?:BCE|BC))?", re.I)
MILL = re.compile(r"(\d)(?:st|nd|rd|th)\s+millennium(\s*(?:BCE|BC))?", re.I)
YEARS = re.compile(r"(?<![\d.])(\d{3,4})(s)?(?:\s*[–-]\s*(\d{2,4}))?(\s*(?:BCE|BC))?(?![\d])")


def fold(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9' ]+", " ", s)).strip()


def region_of(*texts):
    """Earliest place or culture word in the label, else the aliases, else the definition (the coverage grid's own
    country and keyword patterns; the first one in the text wins, so 'Jingdezhen ... shipped by the Dutch' is China)."""
    for txt in texts:
        f = CA.fold(re.sub(r"<[^>]+>", " ", txt or ""))
        best = None
        for pat, reg in CA.COUNTRY_KEYWORDS + CA.KEYWORDS:
            m = pat.search(f)
            if m and (best is None or m.start() < best[0]): best = (m.start(), reg)
        if best: return best[1]
    return None


def period_of(text):
    t = re.sub(r"<[^>]+>", " ", text or "")
    t = re.sub(r"\(?\b(?:UNESCO|inscribed|proclaimed|listed|registered|designated|recognised|recognized)[^.;)]*?\b\d{4}\)?", " ", t, flags=re.I)
    pts = []
    for m in MILL.finditer(t):
        a = int(m.group(1)); pts += [-1000 * a, -1000 * (a - 1)] if m.group(2) else [1000 * (a - 1), 1000 * a]
    t = MILL.sub(" ", t)
    for m in CENT.finditer(t):
        a = int(m.group(1)); b = int(m.group(2) or a)
        pts += [-100 * a, -100 * (b - 1)] if m.group(3) else [100 * (a - 1), 100 * b]
    t = CENT.sub(" ", t)
    for m in YEARS.finditer(t):
        a = int(m.group(1))
        if not (300 <= a <= 2030) and not m.group(4): continue
        b = a + 9 if m.group(2) else a
        if m.group(3):
            b = int(m.group(3)); b = (a // 100) * 100 + b if b < 100 else b
        if m.group(4): a, b = -a, -b
        pts += [a, b]
    if not pts:
        ft = " " + fold(t) + " "
        for name, (a, b) in sorted(DYN.items(), key=lambda x: -len(x[0])):
            if f" {name} " in ft: pts += [a, b]
    if not pts: return None
    a, b = min(pts), max(pts)
    if re.search(r"\bto the present|\bto this day|\btoday\b|\bstill (?:made|practi[sc]ed|produced|active|worked)|\bliving tradition", t, re.I) and b >= 1900:
        b = 2026
    return a, b


def object_periods():
    """(p10, p90) of object dates per leaf, from the collection records mapped to the leaf."""
    import glob, gzip
    O = os.path.join(R3, "collections")
    M = {}
    for f in glob.glob(os.path.join(O, "out_col_*.csv")):
        for r in csv.DictReader(open(f)): M[(r["file"], r["label"], r["family"])] = r["map"].strip()
    ys = {}
    p = os.path.join(O, "objects_norm.csv.gz")
    if not os.path.exists(p): return {}
    csv.field_size_limit(10**9)
    with gzip.open(p, "rt") as fh:
        for r in csv.DictReader(fh):
            m = M.get((r["file"], r["label"], r["family"]), "")
            if not m or ":" in m: continue
            try: y = int(float(r["date_begin"]))
            except (TypeError, ValueError): continue
            if -5000 <= y <= 2026: ys.setdefault(m, []).append(y)
    out = {}
    for c, v in ys.items():
        if len(v) >= 5:
            v.sort(); out[c] = (v[len(v) // 10], v[(len(v) * 9) // 10])
    return out


def era_names(a, b):
    return [n for n, lo, hi in ERAS if not (b < lo or a > hi)]


def main():
    tree = json.load(open(os.path.join(ROOT, "artifact/full/data/tree.json")))["va"]
    import glob as _g
    rows_ = {}
    for pth in _g.glob(os.path.join(ROOT, "artifact/full/data/m-va-*.json")): rows_.update(json.load(open(pth)))
    compute(tree, rows_, verbose=True)


def compute(tree, ROWS, verbose=False):
    """Facets for every leaf of the VA tab tree; writes va_facets.csv; returns {code: (region, start, end)}."""
    ov = {}
    op = os.path.join(R3, "va_facets_overrides.csv")
    if os.path.exists(op):
        for r in csv.DictReader(open(op)): ov[r["code"]] = r
    rows = []; miss_r = []; miss_p = []
    OBJ = object_periods()
    for f in tree["fams"]:
        for s in f["subs"]:
            for l in s["leaves"]:
                lab, al, de = l["label"], l.get("aliases") or "", l.get("defn") or ""
                reg = region_of(lab, de, al); per = period_of(de); how = "rule"
                if not per and l["code"] in OBJ: per = OBJ[l["code"]]; how = "objects"
                if not per:  # dates in the leaf's own entries (sub-types, centres, makers), 10th–90th percentile
                    pts = sorted(y for r in ROWS.get(l["code"], []) if r[1] != "Holding institutions"
                                 for y in (period_of(str(r[2])) or ()) if -5000 <= y <= 2026)
                    if len(pts) >= 4: per = (pts[len(pts) // 10], pts[(len(pts) * 9) // 10]); how = "entries"
                if reg and per: reg = CA.era_fix(reg, per[0], lab + " " + al)
                # ancient Greek, Roman, Etruscan, Aegean and Byzantine work is the Mediterranean region, not modern Europe
                if reg in ("Western Europe", "Central & Eastern Europe") and per and per[0] < 1453 and \
                        (re.search(r"\b(greek|greece|hellen|roman empire|ancient rom|etrusc|minoan|mycen|cycladic|late antique|attic|corinth|laconian|apulian|south italian|campanian)", fold(lab + " " + de[:200])) or re.search(r"\bbyzant", fold(lab))) and \
                        not re.search(r"\b(romanesque|gothic|carolingian|ottonian|revival|neo)", fold(lab)):
                    reg = "Greco-Roman & Byzantine Mediterranean"; how = how + "+mediterranean"
                o = ov.get(l["code"])
                if o:
                    if o.get("region"): reg = o["region"]; how = "override"
                    if o.get("start"): per = (int(o["start"]), int(o["end"])); how = "override"
                if not reg: miss_r.append(f"{l['code']} {lab}")
                if not per: miss_p.append(f"{l['code']} {lab}")
                rows.append([l["code"], lab, reg or "", per[0] if per else "", per[1] if per else "", how])
    with open(os.path.join(R3, "va_facets.csv"), "w", newline="") as fo:
        w = csv.writer(fo); w.writerow(["code", "label", "region", "start", "end", "how"]); w.writerows(rows)
    if verbose:
        print(len(rows), "leaves;", len(miss_r), "without region;", len(miss_p), "without period")
        print("NO REGION:", "; ".join(miss_r))
        print("NO PERIOD:", "; ".join(miss_p[:80]))
    return {r[0]: (r[2], r[3], r[4]) for r in rows}


if __name__ == "__main__":
    main()
