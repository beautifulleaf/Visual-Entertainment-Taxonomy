import json, os, re
W = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(W)
IN = {l["code"]: l for l in json.load(open(os.path.join(D, "in_rz_4.json")))["leaves"]}
OUTF = os.path.join(W, "parts.json")
def load():
    return json.load(open(OUTF)) if os.path.exists(OUTF) else {}
def save(code, obj):
    d = load(); d[code] = obj; json.dump(d, open(OUTF, "w"), ensure_ascii=False, indent=1)
def yr(t):
    m = re.match(r"\d{4}", str(t.get("year") or "")); return int(m.group()) if m else 0
EAST = {"JP","Japan","KR","South Korea","Korea","CN","China","TW","Taiwan","HK","Hong Kong","MN","Mongolia","Korea-Japan"}
def cc(t):
    c = (t.get("country") or "").strip()
    return re.split(r"[-|/,]", c)[0].strip() if c else ""
REG = {
 "east": "JP Japan KR South Korea Korea CN China TW Taiwan HK Hong Kong MN Mongolia",
 "na": "US USA CA Canada",
 "latam": "MX Mexico AR Argentina BR Brazil CL Chile PE Peru CO Colombia CU Cuba BO Bolivia PY Paraguay VE Venezuela DO Dominican CR Costa EC Ecuador UY Uruguay PR Puerto",
 "west": "FR France BE Belgium CH Switzerland IT Italy ES Spain PT Portugal GB UK Ireland IE NL Netherlands Netherland DE Germany West Austria AT DK Denmark SE Sweden NO Norway FI Finland IS Iceland LU Luxembourg GR Greece Greece CY Cyprus",
 "eastEu": "RU Russia USSR SU PL Poland HU Hungary CZ Czech Czechoslov Czechoslovakia XC SK Slovakia YU Yugoslavia RS Serbia HR Croatia SI Slovenia BG Bulgaria RO Romania EE Estonia LV Latvia LT Lithuania UA Ukraine BY Belarus GE Georgia AM Armenia AZ Azerbaijan KZ Kazakhstan UZ Uzbekistan Uzbekistan KG Kyrgyzstan TM Turkmenist MD Moldova MK Macedonia XK Kosovo BA Bosnia East XG Kazakh",
}
REGMAP = {}
for k, v in REG.items():
    for w in v.split(): REGMAP[w] = k
def region(t):
    c = cc(t)
    if c in REGMAP: return REGMAP[c]
    first = c.split()[0] if c else ""
    return REGMAP.get(first, "other")
def build(code, secmap, override, default=None, unassigned=None):
    """secmap: current sec str -> (key, sec); override: id -> (key, sec) ; returns assign"""
    A = {}
    for t in IN[code]["titles"]:
        i = t["id"]
        if i in override: A[i] = list(override[i]); continue
        f = secmap.get(t["sec"])
        if callable(f): f = f(t)
        if f is None: raise SystemExit(f"no mapping for {i} {t['title']} sec={t['sec']}")
        A[i] = list(f)
    return A
def ids_by_title(code):
    m = {}
    for t in IN[code]["titles"]:
        m.setdefault(t["title"], []).append(t["id"])
    return m
def T(code, *titles, year=None):
    """resolve titles to ids (all matches)."""
    m = ids_by_title(code); out = []
    for ti in titles:
        if ti not in m: raise SystemExit(f"{code}: title not found: {ti}")
        out += m[ti]
    return out
def W_(code, key, sec, *titles):
    return {i: (key, sec) for i in T(code, *titles)}
def report(code, A):
    import collections
    c = collections.Counter((k, s) for k, s in A.values())
    print(code, sorted(c.items()))
