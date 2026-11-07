"""Build result.json for pass small_E from the input, spec_*.py and the gathered object cache."""
import json, os, re, pickle, csv, collections, urllib.parse, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..", "..")
sys.path.insert(0, HERE)
from spec_lib import SPEC
import spec_a, spec_b, spec_c  # noqa
from insts import INST

CAP = 50
inp = json.load(open(os.path.join(ROOT, "taxonomy/r3/va_in/small_E.json")))["leaves"]
D = pickle.load(open(os.path.join(HERE, "cache.pkl"), "rb"))
# Met culture-label aggregates
MET = {}
for r in csv.DictReader(open(os.path.join(ROOT, "data/interim/unattributed_cultures.csv"))):
    n = 0
    for m in re.finditer(r"([a-z ]+) \((\d+)\)", r["top_classifications"]):
        if m.group(1).strip() in ("vases", "ceramics", "terracottas"): n += int(m.group(2))
    if n: MET[r["label"]] = n

CORE = re.compile(r"ceram|pott|porcel|stoneware|earthenware|fa[iy]ence|terra ?cott|celadon|majolica|maiolica|fritware|frit\b|stone.?paste|陶|磁|瓷|焼|土器|埴輪|자기|청자|백자|분청|керам|фаянс|фарфор|глин|майолик|изразц|kwarts-fritgoed|aardewerk|steengoed", re.I)
WEAK = re.compile(r"glaz|slip|clay|vase|tile|窯|lustre", re.I)
NONCER = re.compile(r"\bsilk\b|\bwool\b|cotton|\bpaper\b|parchment|\bglass\b|bronze|copper|brass|silver|lacquer|\bwood|ivory|\bjade|textile|velvet|embroider|\bink\b|leather|basket|\bbone\b|stone\b(?!ware)|marble|響銅|金銅|漆|絹|紙", re.I)
def is_cer(r):
    t = r[2] + " " + (r[6] or "") + " " + r[1]
    if r[0] == "east_asia":
        return r[6] in ("ceramics",) or (r[6] == "archaeology" and bool(CORE.search(t)))
    if CORE.search(t): return True
    return bool(WEAK.search(t)) and not NONCER.search(t)

def prep(r):
    ct = r[2]; node = ""
    if ct.startswith("NODE:"):
        node, _, ct = ct.partition(" | ")
    return (r, node, ct + " | " + r[1])
def match(spec, x):
    r, node, text = x
    if spec["src"] and r[0] not in spec["src"]: return False
    ok = False
    if spec["node"] and node and re.search(spec["node"], node, re.I): ok = True
    if not ok:
        for alt in spec["pat"]:
            alts = (alt,) if isinstance(alt, str) else alt
            if all(re.search(a, text, re.I) for a in alts): ok = True; break
    if not ok: return False
    if spec["excl"] and re.search(spec["excl"], text, re.I): return False
    return True

GEN = set("""bowl bowls dish dishes jar jars vase vases plate plates cup cups saucer saucers tile tiles fragment fragments sherd sherds potsherd potsherds shard
vessel vessels pot pots pottery ewer ewers jug jugs pitcher pitchers bottle bottles flask flasks figure figures figurine figurines lid lids cover covers covered with and of a an the
small large miniature pair two three four set part piece pieces base rim neck handle handles body foot spout spouted tea teabowl teapot teacup coffee water wine sake incense burner censer
box boxes basin basins tray trays cylindrical round square rectangular oval octagonal hexagonal deep shallow footed lobed lidded tall rounded globular spherical ovoid pear shaped oblong stem
stemmed effigy whistle spindle whorl ladle spoon albarello stand jarlet kendi kettle flower lamp ornament panel panels border frieze star cross mug tankard beaker goblet chalice canteen pilgrim
amphora krater kylix hydria oinochoe lekythos aryballos skyphos olpe pyxis alabastron rhyton kantharos stamnos pelike dinos psykter phiale lebes loutrophoros pithos stirrup double ring
mould mold wall floor roof eave end funerary cinerary urn burial ceremonial ritual offering storage cooking dropper brush rest washer plaque sculpture statuette head mask animal
earthenware stoneware porcelain glazed glaze unglazed celadon blue white green brown black red yellow turquoise cobalt polychrome monochrome painted underglaze overglaze enamelled enameled
incised carved moulded molded stamped impressed decorated decoration design designs type style ware wares in on for from or to as fritware stonepaste lustre luster lustreware
chawan mizusashi chaire tokkuri hanaike kogo kōgō futamono mukozuke mukōzuke sara hachi tsubo kame wan jarra plato olla cuenco vasija cazuela cántaro
object objects item model tablet sample samples specimen specimens shards waster wasters kiln kilns unknown unidentified miscellaneous container containers food serving drinking
""".split())
DUTCH = re.compile(r"\b(met|van|aardewerken?|schaal|kom|bord|vaas|kan|beker|deksel|kopje|schotel|theepot|beeldje|tegel|scherf|porseleinen|stenen)\b")
CJK = re.compile(r"[぀-ヿ㐀-鿿가-힯]")
def clean_title(t):
    t = re.sub(r"\((image withheld[^)]*)\)", "", t, flags=re.I)
    t = t.strip().strip('"').strip()
    t = re.sub(r"\s+", " ", t)
    if t.isupper() and re.search(r"[А-Яа-я]", t): t = t[0] + t[1:].lower()
    return t
def descriptive(t, extra):
    if not t or CJK.search(t): return False
    lat = re.sub(r"[^A-Za-z]", "", t)
    if lat and t.upper() == t and len(lat) > 6: return False      # catalogue-style capitals (NMVW)
    if DUTCH.search(t): return False
    toks = [x for x in re.split(r"[^\w']+", re.sub(r"\([^)]*\)", " ", t).lower()) if x]
    rest = [x for x in toks if x not in GEN and x not in extra and len(x) > 2 and not x.isdigit()]
    return len(rest) >= 1

TYPES = [("Tiles and architectural ceramics", r"\btiles?\b|panel|revetment|mihrab|frieze|plaque|brick|eave|finial|ridge|stove|kachel|изразец|изразц|mosque|palace|pyramid"),
         ("Dishes and plates", r"\bdish|plate|platter|charger|saucer|tray|basin|\bsara\b|блюд|тарел"),
         ("Bowls and cups", r"\bbowl|\bcup|beaker|goblet|chalice|tea ?bowl|chawan|kylix|skyphos|kantharos|mug|tankard|чаш|кружк|стакан|cups\b|wan\b"),
         ("Jars, vases and bottles", r"\bjar|vase|bottle|flask|amphora|krater|hydria|pithos|urn|albarello|pot\b|tsubo|stamnos|pelike|lekythos|aryballos|olpe|pyxis|alabastron|pilgrim|кувшин|горш|ваз|бутыл|корчаг|крынк"),
         ("Ewers, jugs and teapots", r"\bewer|jug|pitcher|teapot|kettle|oinochoe|spout|kendi|tokkuri|чайник|квасник|кумган"),
         ("Figures and models", r"figure|figurine|statuette|sculpture|effigy|model|toy|whistle|head\b|lion|horse|bull|dog|camel|guardian|dogū|haniwa|vessel in the form|игрушк|фигур|свистул"),
         ]
WORK_GROUPS = [t[0] for t in TYPES] + ["Other works"]
def wtype(name):
    for g, p in TYPES:
        if re.search(p, name, re.I): return g
    return "Other works"

ORDER = ["Sub-types", "Schools & phases", "Centres & workshops"] + WORK_GROUPS + ["Collections", "Makers"]
GROUPMAP = {"sub-type": "Sub-types", "type": "Sub-types", "palette": "Sub-types", "sub-group": "Sub-types", "style": "Sub-types", "fabric": "Sub-types",
            "ware": "Sub-types", "monochrome": "Sub-types", "technique": "Sub-types", "pattern": "Sub-types", "figurines": "Sub-types",
            "phase": "Schools & phases", "branch": "Schools & phases", "centre": "Centres & workshops", "kiln": "Centres & workshops", "manufactory": "Centres & workshops"}

def wurl(t):
    if t.startswith("http") or t.startswith("r3 "): return t if t.startswith("r3 ") else "r3 " + t
    return "r3 https://en.wikipedia.org/wiki/" + urllib.parse.quote(t.replace(" ", "_"), safe="_(),'%-.")

def q(s): return urllib.parse.quote_plus(s)
def catalogues(sp, label):
    kw = sp["kw"] or label
    P = sp["prof"]
    met = [f"https://www.metmuseum.org/art/collection/search?q={q(kw)}", "The Met collection search", f"Metropolitan Museum objects matching '{kw}'"]
    vam = [f"https://collections.vam.ac.uk/search/?q={q(kw)}", "V&A Collections search", f"Victoria and Albert Museum objects matching '{kw}'"]
    bm = [f"https://www.britishmuseum.org/collection/search?keyword={q(kw)}", "British Museum collection search", f"British Museum objects matching '{kw}'"]
    rijks = [f"https://www.rijksmuseum.nl/en/collection/search?query={q(kw)}", "Rijksmuseum collection search", f"Rijksmuseum objects matching '{kw}'"]
    freer = [f"https://asia.si.edu/explore-art-culture/collections/search/?edan_q={q(kw)}", "National Museum of Asian Art (Freer|Sackler) collection search", f"Freer and Sackler objects matching '{kw}'"]
    si = [f"https://collections.si.edu/search/results.htm?q={q(kw)}", "Smithsonian collections search", f"Smithsonian (incl. National Museum of the American Indian) records matching '{kw}'"]
    cma = [f"https://www.clevelandart.org/art/collection/search?search={q(kw)}", "Cleveland Museum of Art collection search", f"Cleveland Museum of Art objects matching '{kw}'"]
    out = []
    if sp["ich"]: out.append(list(sp["ich"]))
    if P == "china":
        if sp["zh"]: out.append([f"https://digitalarchive.npm.gov.tw/Collection/Search?Keyword={q(sp['zh'])}", "National Palace Museum Digital Archive (Taipei)", f"National Palace Museum objects matching '{sp['zh']}'"])
        if sp["jp"]: out.append([f"https://colbase.nich.go.jp/collection_items?locale=en&keyword={q(sp['jp'])}", "ColBase (Japan's National Museums)", f"Tokyo, Kyoto, Nara and Kyushu National Museum objects matching '{sp['jp']}'"])
        out += [freer, met, bm, vam]
    elif P == "japan":
        if sp["jp"]: out.append([f"https://colbase.nich.go.jp/collection_items?locale=en&keyword={q(sp['jp'])}", "ColBase (Japan's National Museums)", f"Tokyo, Kyoto, Nara and Kyushu National Museum objects matching '{sp['jp']}'"])
        out += [freer, met, bm]
    elif P == "korea":
        if sp["jp"]: out.append([f"https://colbase.nich.go.jp/collection_items?locale=en&keyword={q(sp['jp'])}", "ColBase (Japan's National Museums)", f"Tokyo National Museum and other national museum objects matching '{sp['jp']}'"])
        out += [freer, met, cma, bm]
    elif P == "greek":
        out.append(["https://www.beazley.ox.ac.uk/carc/pottery", "Beazley Archive Pottery Database", "over 120,000 figure-decorated Greek vases, searchable by fabric, shape and painter"])
        out.append(["https://www.cvaonline.org/cva/", "Corpus Vasorum Antiquorum online", "the CVA fascicules: museum-by-museum catalogues of ancient vases"])
        out += [met, bm]
    elif P == "americas": out += [si, met, bm]
    elif P == "europe": out += [vam, met, bm, rijks]
    elif P == "seasia": out += [freer, met, vam, bm]
    elif P == "antiq": out += [met, bm]
    elif P == "folk": out += [vam, met, bm]
    else: out += [vam, met, bm]          # islam
    return out[:5]

def inst_info(name):
    if name in INST: return INST[name]
    m = re.search(r'"([^"]+)', name)
    if m: return (m.group(1), "Russia", None)
    return (name, None, None)

def fmt_date(r):
    dt = (r[7] or "").strip()
    if dt and not CJK.search(dt) and len(dt) < 50: return dt
    if r[3] is None: return ""
    y = r[3]
    return f"c. {-y} BC" if y < 0 else f"c. {y}"

DX = [prep(r) for r in D if is_cer(r)]
print("ceramic records", len(DX))
result = {"leaves": {}, "new_leaves": [], "moves_out": [], "dropped": []}
report = []
for l in inp:
    code = l["code"]; sp = SPEC.get(code)
    if sp is None: report.append(f"NO SPEC {code}"); sp = dict(pat=[], kw=None, prof="islam", excl=None, node=None, src=None, met=[], rows=[], ov={}, zh=None, jp=None, ich=None, defn=None)
    kinds, alias = [], list(l.get("alias_rows") or [])
    seen = set()
    for r in l["rows"]:
        name, grp, gloss, src, mk = r[:5]
        o = sp["ov"].get(name)
        if o == "alias": alias.append(name); continue
        if isinstance(o, str) and o.startswith("drop:"): result["dropped"].append([code, name, o[5:]]); continue
        if src == "possession":
            m = re.search(r"https?://\S+", gloss)
            if m: src = "possession " + m.group(0)
        if isinstance(o, tuple):
            nn, ng, gl = o[0], o[1], o[2]
            s2 = o[3] if len(o) > 3 and o[3] else src
            mk2 = o[4] if len(o) > 4 else mk
        else:
            if mk or grp in ("Artists", "Architects", "Makers"): nn, ng, gl, s2, mk2 = name, "Makers", gloss, src, 1
            elif grp.startswith("Gathered rows"): alias.append(name); continue
            else:
                nn, ng, s2, mk2 = name, GROUPMAP.get(grp, grp), src, mk
                gl = gloss; report.append(f"UNREVIEWED {code} {name} [{grp}] {gloss}")
        if (mk or grp in ("Artists", "Architects", "Makers")) and nn != name: report.append(f"MAKER RENAMED {code} {name}")
        if nn in seen and not mk: continue
        seen.add(nn)
        kinds.append([nn, ng, gl, s2, mk2])
    for (nn, ng, gl, w, mk) in sp["rows"]:
        if nn in seen: continue
        seen.add(nn)
        kinds.append([nn, wtype(nn) if ng == "W" else ng, gl, wurl(w), mk])
    # gathered objects
    ms, urls = [], set()
    if sp["pat"] or sp["node"]:
        for x in DX:
            r = x[0]
            if r[5] in urls: continue
            if match(sp, x): ms.append(r); urls.add(r[5])
    extra = set(re.findall(r"[a-zà-ÿ']+", (l["label"] + " " + (sp["kw"] or "") + " " + l.get("aliases", "")).lower()))
    cands, tseen = [], set()
    for r in sorted(ms, key=lambda r: (r[3] is None, r[3] if r[3] is not None else 0, r[1])):
        t = clean_title(r[1])
        if not descriptive(t, extra): continue
        if t.lower() in tseen or t in seen: continue
        tseen.add(t.lower()); cands.append((t, r))
    nworks_all = len(cands)
    for t, r in cands[:CAP]:
        en, city, _ = inst_info(r[4])
        d = fmt_date(r)
        gl = "; ".join(x for x in [d, en + (", " + city if city else "")] if x)
        kinds.append([t[:150], wtype(t), gl[:140], "r3 " + r[5], 0]); seen.add(t)
    # collections
    cnt = collections.Counter(r[4] for r in ms if r[4] and r[4] not in ("個人", "Private", "", "国（文化庁）"))
    metn = sum(MET.get(x, 0) for x in sp["met"])
    if metn: cnt["The Metropolitan Museum of Art"] = max(cnt.get("The Metropolitan Museum of Art", 0), metn)
    merged = collections.Counter()
    for k, v in cnt.items(): merged[inst_info(k)[0]] += v
    ranked = merged.most_common()
    sel = [x for x in ranked if x[1] >= 10]
    if len(sel) < 8:
        two = [x for x in ranked if x[1] >= 2]
        sel = (two if len(two) >= 3 else ranked)[:8]
    for en, n in sel:
        info = next((INST[k] for k in INST if INST[k][0] == en), (en, None, None))
        city, url = info[1], info[2]
        if not url:
            url = next((r[5] for r in ms if inst_info(r[4])[0] == en), None)
            report.append(f"NO INST URL {en}")
        note = " (incl. Met culture-label counts)" if en == "The Metropolitan Museum of Art" and metn else ""
        gl = (city + " — " if city else "") + f"{n} objects in the gathered records{note}"
        if url: kinds.append([en, "Collections", gl, "r3 " + url, 0])
    # order
    kinds.sort(key=lambda k: ORDER.index(k[1]) if k[1] in ORDER else 2.5)
    nw = sum(1 for k in kinds if k[1] in WORK_GROUPS)
    axis = ("sub-types and phases first, then centres and workshops; works: every gathered object of the ware with a descriptive title and a museum page "
            "(bare object names such as 'Bowl' or 'Tile' excluded)" + (f", the {CAP} earliest-dated of {nworks_all}" if nworks_all > CAP else "") +
            ", by object type (tiles, dishes, bowls, jars and vases, ewers and jugs, figures, other), plus named works from the literature; "
            "Collections ranked by the number of the ware's objects in the gathered object files; makers last")
    ent = {"axis": axis, "catalogues": catalogues(sp, l["label"]), "kinds": kinds, "alias_rows": sorted(set(alias), key=alias.index)}
    if sp["defn"]: ent["defn"] = sp["defn"]
    result["leaves"][code] = ent
    report.append(f"{code} {l['label']}: matched {len(ms)}, works {min(nworks_all, CAP)}/{nworks_all}, kinds {len(kinds)}, coll {sum(1 for k in kinds if k[1]=='Collections')}")
json.dump(result, open(os.path.join(HERE, "result.json"), "w"), ensure_ascii=False, indent=1)
open(os.path.join(HERE, "report.txt"), "w").write("\n".join(report))
print("\n".join(x for x in report if not x.startswith(("E1", "E2", "E3", "E4")))[:5000])
