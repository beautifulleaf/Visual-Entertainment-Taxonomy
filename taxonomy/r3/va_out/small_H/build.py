"""Build result.json for pass small_H from input, kn*.txt knowledge, objects*.json and urlcheck.json.
   python3 build.py urls   -> write urls_needed.txt
   python3 build.py        -> write result.json"""
import json, os, re, sys, glob, collections, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "../../../..")
INP = json.load(open(os.path.join(ROOT, "taxonomy/r3/va_in/small_H.json")))["leaves"]
W = "https://en.wikipedia.org/wiki/"
GMAP = {"S": "Sub-types", "P": "Schools & phases", "C": "Centres & workshops", "M": "Makers"}
ORDER = ["Sub-types", "Schools & phases", "Centres & workshops", "Named works"]

# ---------- knowledge ----------
KN = {}
for fn in sorted(glob.glob(os.path.join(HERE, "kn*.txt"))):
    cur = None
    for line in open(fn, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip(): continue
        if line.startswith("@"):
            p = [x.strip() for x in line[1:].split("|")]
            cur = KN.setdefault(p[0], {"wiki": p[1], "q": p[2], "codes": p[3] if len(p) > 3 else "MVB", "rules": {}, "adds": [], "cats": [], "axis": None})
        elif line.startswith("= "):
            old, new = line[2:].split(" => ", 1)
            cur["rules"][old.strip()] = new.strip()
        elif line.startswith("+ "):
            p = [x.strip() for x in line[2:].split("|")]
            while len(p) < 5: p.append("")
            cur["adds"].append(p)
        elif line.startswith("cat:"):
            cur["cats"].append([x.strip() for x in line[4:].split("|")])
        elif line.startswith("axis:"):
            cur["axis"] = line[5:].strip()
        else:
            raise SystemExit("bad line in %s: %s" % (fn, line))

def wurl(a): return W + a.replace(" ", "_")
def guess(name): return wurl(re.sub(r"\s*\(.*?\)", "", name).strip())

URLCHECK = json.load(open(os.path.join(HERE, "urlcheck.json"))) if os.path.exists(os.path.join(HERE, "urlcheck.json")) else {}
def ok(u):
    return URLCHECK.get(u, None)

def resolve_src(leafwiki, name, src, group, is_maker):
    """return url or None (drop)"""
    cands = []
    if src.startswith("w:"): cands.append(wurl(src[2:]))
    elif src.startswith("http"): cands.append(src)
    if is_maker or group == "Named works":
        cands.append(guess(name))
    elif leafwiki != "-":
        cands.append(wurl(leafwiki))
    else:
        cands.append(guess(name))
    if leafwiki != "-" and not (is_maker or group == "Named works"):
        cands.append(wurl(leafwiki))
    for u in cands:
        if ok(u): return u
    return None

def all_urls():
    s = set()
    for code, k in KN.items():
        if k["wiki"] != "-": s.add(wurl(k["wiki"]))
        for g, name, gl, src, m in k["adds"]:
            if src.startswith("w:"): s.add(wurl(src[2:]))
            elif src.startswith("http"): s.add(src)
            s.add(guess(name))
    return s

if len(sys.argv) > 1 and sys.argv[1] == "urls":
    open(os.path.join(HERE, "urls_needed.txt"), "w").write("\n".join(sorted(u for u in all_urls() if u not in URLCHECK)))
    print(len(all_urls())); sys.exit()

# ---------- objects ----------
OBJ = collections.defaultdict(dict)
for fn in glob.glob(os.path.join(HERE, "objects_*.json")):
    for c, d in json.load(open(fn)).items():
        OBJ[c].update(d)

GENERIC = set("""rug rugs carpet carpets kilim kilims mat mats textile textiles fragment fragments of from the a an and or with in on for to piece pieces part
cloth cloths panel panels border borders band bands sample samples swatch swatches length lengths section sections square strip strips
woman women woman's women's man men man's men's child children child's girl girl's boy boy's female male bride bride's bridal wedding ceremonial unidentified
robe robes dress dresses tunic tunics coat coats jacket jackets skirt skirts shirt shirts blouse blouses kimono kosode furisode sari saree saris shawl shawls scarf scarves
sash sashes belt belts cap caps hat hats headdress headcloth shoe shoes slipper slippers boot boots mantle mantles cloak cloaks poncho ponchos vest apron veil
hanging hangings cover covers curtain curtains cushion cushions pillow quilt quilts coverlet bedcover bedspread tablecloth towel towels napkin napkins banner flag flags
bag bags basket baskets box pouch purse container tray jar bowl bowls olla lid lidded miniature model doll dolls trapping trappings
lace collar collars cuff cuffs flounce lappet lappets insertion edging edge handkerchief kerchief headscarf
embroidery embroidered woven weave weaving printed painted dyed brocade brocaded tapestry tapestries velvet silk cotton wool linen
prayer saddle saddlebag bag-face face fragmentary small large long short pair one two three four
huipil huipiles rebozo serape sarape blanket blankets wrapper wrappers loincloth sarong tube sampot hol
untitled unknown various object objects item
doek hoofddoek omslagdoek draagdoek schouderdoek heupdoek lendendoek borstdoek rok jas jasje baadje broek tas mand mandje sjabloon kleed tafelkleed wandkleed deken
slendang selendang kain panjang stof lap van een met op en de het der des katoenen zijden wollen geweven gebatikte jurk muts kap kant strook
ковер коврик полотенце платок рубаха рубашка рушник шаль кружево фрагмент образец ткани ткань фартук пояс головной убор юбка сарафан покрывало подзор""".lower().split())

def titled(t, leafwords):
    w = re.findall(r"[a-zA-ZÀ-ɏ'Ā-￿]+", t.lower())
    rest = [x for x in w if x not in GENERIC and x not in leafwords and len(x) >= 4 and not x.endswith("'s")]
    return len(rest) >= 1

TYPES = [("Carpets and rugs", r"\b(rugs?|carpets?|kilims?|mats?|gelims?|soumak)\b"),
         ("Garments and dress", r"\b(robes?|dress(es)?|tunics?|coats?|jackets?|skirts?|shirts?|huipil(es)?|blouses?|kimonos?|kosode|furisode|uchikake|katabira|haori|saris?|sarees?|shawls?|scarf|scarves|sash(es)?|belts?|caps?|hats?|headdress|shoes?|slippers?|boots?|mantles?|cloaks?|ponchos?|vests?|aprons?|veils?|kaftan|caftan|trousers|socks?|mittens?|gloves?|collars?|cuffs?|uncu|chullo|thob|garment|costume)\b"),
         ("Hangings and covers", r"\b(hangings?|covers?|curtains?|cushions?|pillows?|quilts?|coverlets?|bedcover|bedspread|tablecloth|towels?|napkins?|banners?|flags?|screens?|tapestr(y|ies)|valance|palampore|panels?|frontal|altar)\b"),
         ("Bags, baskets and containers", r"\b(bags?|baskets?|box(es)?|pouch|purse|containers?|trays?|jars?|bowls?|ollas?|plaque|wallet)\b"),
         ("Fragments and samples", r"\b(fragments?|samples?|borders?|bands?|swatch|strip)\b")]
def otype(t):
    for g, rx in TYPES:
        if re.search(rx, t, re.I): return g
    return "Other titled objects"

CITY = {"The Metropolitan Museum of Art": "New York", "Metropolitan Museum of Art": "New York", "Victoria and Albert Museum": "London", "British Museum": "London",
 "The British Museum": "London", "Cleveland Museum of Art": "Cleveland", "Art Institute of Chicago": "Chicago", "Cooper Hewitt, Smithsonian Design Museum": "New York",
 "Rijksmuseum": "Amsterdam", "Tropenmuseum": "Amsterdam", "Museum Volkenkunde": "Leiden", "Wereldmuseum Rotterdam": "Rotterdam", "Afrika Museum": "Berg en Dal",
 "Tokyo National Museum": "Tokyo", "Kyoto National Museum": "Kyoto", "Nara National Museum": "Nara", "Kyushu National Museum": "Dazaifu",
 "National Palace Museum, Taipei": "", "National Museum of the American Indian": "Washington", "National Museum of American History": "Washington",
 "National Museum of Natural History": "Washington", "National Museum of African Art": "Washington", "National Museum of Asian Art": "Washington",
 "Smithsonian American Art Museum": "Washington", "Los Angeles County Museum of Art": "Los Angeles", "Brooklyn Museum": "New York",
 "Museum of Fine Arts, Boston": "Boston", "Harvard Art Museums": "Cambridge, Mass.", "Yale University Art Gallery": "New Haven",
 "Philadelphia Museum of Art": "Philadelphia", "Minneapolis Institute of Art": "Minneapolis", "National Gallery of Art": "Washington",
 "Walters Art Museum": "Baltimore", "Princeton University Art Museum": "Princeton", "Museum of New Zealand Te Papa Tongarewa": "Wellington",
 "Musée du quai Branly": "Paris", "Statens museum for Kunst": "Copenhagen", "Nationalmuseum": "Stockholm", "Finnish Heritage Agency": "Helsinki"}
def where(ins):
    c = CITY.get(ins, "")
    return ins + (", " + c if c and c not in ins else "")

def yr(d):
    m = re.search(r"-?\d{3,4}", str(d))
    return int(m.group()) if m else None

def nicetitle(t):
    t = re.sub(r"\s+", " ", t).strip().rstrip(".")
    if t.isupper(): t = t.capitalize()
    return t[:110]

# ---------- catalogues ----------
def cats(code, k, label, sub):
    q = urllib.parse.quote_plus(k["q"] or label)
    qq = k["q"] or label
    D = {"M": ("https://www.metmuseum.org/art/collection/search?q=" + q, "The Met Collection search", "Metropolitan Museum objects matching '%s'" % qq),
         "V": ("https://collections.vam.ac.uk/search/?q=" + q, "V&A Collections search", "Victoria and Albert Museum objects matching '%s'" % qq),
         "B": ("https://www.britishmuseum.org/collection/search?keyword=" + q, "British Museum Collection search", "British Museum objects matching '%s'" % qq),
         "C": ("https://collection.cooperhewitt.org/search/collection/?query=" + q, "Cooper Hewitt Collection search", "Smithsonian design museum textiles and lace matching '%s'" % qq),
         "L": ("https://www.clevelandart.org/art/collection/search?search=" + q, "Cleveland Museum of Art collection search", "Cleveland Museum of Art objects matching '%s'" % qq),
         "S": ("https://collections.si.edu/search/results.htm?q=" + q, "Smithsonian Collections Search", "all Smithsonian units (NMAI, NMAH, NMNH, NMAfA, Cooper Hewitt) matching '%s'" % qq),
         "E": ("https://www.europeana.eu/en/search?query=" + q, "Europeana", "European museum and archive records matching '%s'" % qq),
         "A": ("https://www.artic.edu/collection?q=" + q, "Art Institute of Chicago collection search", "Art Institute of Chicago objects matching '%s'" % qq),
         "G": ("https://artsandculture.google.com/search?q=" + q, "Google Arts & Culture", "partner-museum objects and stories matching '%s'" % qq),
         "T": ("https://museum.gwu.edu/", "The George Washington University Museum and The Textile Museum", "the Textile Museum's collection of carpets and textiles, Washington"),
         "Q": ("https://quiltindex.org/", "The Quilt Index", "online database of tens of thousands of documented quilts"),
         "K": ("https://www.kci.or.jp/en/archives/digital_archives/", "Kyoto Costume Institute Digital Archives", "the KCI collection of dress and textiles"),
         "F": ("https://www.europeana.eu/en/collections/topic/55-fashion", "Europeana Fashion", "European museum dress and fashion collections")}
    codes = k["codes"]
    if sub == "H7" and "E" in codes and "F" not in codes: codes += "F"
    out = [list(D[c]) for c in codes if c in D]
    out += [c for c in k["cats"]]
    if len(out) < 2: out.append(list(D["G"]))
    return out[:5]

POSS = re.compile(r"owned as (.+?) \(Possession ([A-Z]\d+)\)")
URLRX = re.compile(r"https?://\S+")
def clean_gloss(g):
    g = re.sub(r"\s*·?\s*owned as .+?\(Possession [A-Z]\d+\)", "", g)
    g = URLRX.sub("", g)
    g = re.sub(r"\s*·\s*$", "", g).strip(" ·;")
    return g

res = {"leaves": {}, "new_leaves": [], "moves_out": [], "dropped": []}
REPORT = collections.Counter()
for l in INP:
    code, label, sub = l["code"], l["label"], l["sub"]
    k = KN.get(code)
    if not k: raise SystemExit("no knowledge block for " + code)
    rules = k["rules"]
    kinds, aliases = [], []
    used = set()
    for r in l["rows"]:
        name, grp, gl, src, mk = r[:5]
        maker = bool(mk) or grp in ("Artists", "Architects", "Makers")
        rule = rules.get(name)
        if rule is None:
            if grp.startswith("Gathered rows") and not maker:
                rule = "ALIAS"
            else:
                print("UNMAPPED", code, r[:4]); rule = ". | %s | %s" % ("M" if maker else "S", clean_gloss(gl))
        used.add(name)
        pm = POSS.search(gl or "")
        purl = URLRX.search(gl or "")
        if rule == "ALIAS" or rule.startswith("DROP"):
            if maker: raise SystemExit("maker lost: %s %s" % (code, name))
            if pm:  # keep possession link as a kind
                kinds.append([pm.group(1), "Sub-types", "the owned item of this tradition · Possession: %s (%s)" % (pm.group(1), pm.group(2)),
                              "possession " + purl.group() if purl else src, 0])
                REPORT["poss_kept"] += 1
            if rule == "ALIAS":
                if name not in aliases and name != label: aliases.append(name)
            else:
                res["dropped"].append([code, name, rule.split("|", 1)[1].strip() if "|" in rule else "noise"])
            continue
        p = [x.strip() for x in rule.split("|")]
        nn = name if p[0] == "." else p[0]
        g = GMAP.get(p[1], p[1])
        if maker: g = "Makers"
        ng = p[2] if len(p) > 2 and p[2] else clean_gloss(gl)
        if pm and "Possession:" not in ng:
            ng = (ng + " · Possession: %s (%s)" % (pm.group(1), pm.group(2))).strip(" ·")
        s = src
        if src == "possession" and purl: s = "possession " + purl.group()
        kinds.append([nn, g, ng[:200], s, 1 if (maker or g == "Makers") else 0])
    for old in rules:
        if old not in used: print("RULE UNUSED", code, old)
    for g, name, gl, src, m in k["adds"]:
        g = GMAP.get(g, g)
        is_m = m.strip() == "1"
        u = resolve_src(k["wiki"], name, src, g, is_m)
        if not u:
            REPORT["add_dropped_nourl"] += 1; print("NOURL", code, name); continue
        kinds.append([name, g, gl, "r3 " + u, 1 if is_m else 0]); REPORT["added"] += 1
    # computed works + collections
    objs = OBJ.get(code, {})
    leafwords = set(re.findall(r"[a-z]+", (label + " " + (k["q"] or "")).lower()))
    inst = collections.Counter(); firsturl = {}
    for u, (t, d, ins, f, cu) in objs.items():
        if ins:
            inst[ins] += 1; firsturl.setdefault(ins, u)
    cand = []
    for u, (t, d, ins, f, cu) in objs.items():
        if t and ins and titled(t, leafwords):
            cand.append((yr(d) if yr(d) is not None else 99999, nicetitle(t), d, ins, u))
    cand.sort()
    seen = set(); works = []
    for y, t, d, ins, u in cand:
        if t.lower() in seen: continue
        seen.add(t.lower())
        works.append((t, d, ins, u, y))
        if len(works) >= 30: break
    for t, d, ins, u, y in works:
        ds = str(d) if d and y != 99999 else ""
        nm = "%s (%s)" % (t, ds) if ds else t
        kinds.append([nm, otype(t), ("%s%s" % (where(ins), ", " + ds if ds else ""))[:140], "r3 " + u, 0]); REPORT["works"] += 1
    coll = [(n, c) for c, n in inst.most_common() if n >= 10] or [(n, c) for c, n in inst.most_common(8)]
    for n, c in coll:
        kinds.append([c, "Collections", "%s — %d objects in the gathered records" % (where(c), n), "r3 " + firsturl[c], 0]); REPORT["collections"] += 1
    # order groups
    def gk(r):
        g = r[1]
        if g in ORDER: return (ORDER.index(g), 0)
        if g == "Collections": return (90, 0)
        if g == "Makers": return (95, 0)
        if g in [x[0] for x in TYPES] + ["Other titled objects"]: return (50, [x[0] for x in TYPES].index(g) if g != "Other titled objects" else 9)
        return (40, 0)
    kinds.sort(key=gk)  # stable: keeps row order within group
    gs = []
    for r in kinds:
        if r[1] not in gs: gs.append(r[1])
    parts = []
    lead = [g for g in gs if g in ORDER[:3]]
    if lead: parts.append(", ".join(g.lower() for g in lead) + " first")
    other = [g for g in gs if gk([0, g])[0] == 40]
    if other: parts.append("then " + ", ".join(other))
    if "Named works" in gs or works:
        parts.append("works: named works with a Wikipedia article or museum page, then every gathered object with a specific title and a museum page, up to 30, earliest-dated first, sectioned by object type")
    if coll: parts.append("collections: institutions ranked by number of gathered objects of the tradition (all with >= 10, else the top 8)")
    if "Makers" in gs: parts.append("makers last, by date")
    axis = k["axis"] or ("; ".join(parts) if parts else "single sub-types list")
    entry = {"axis": axis, "catalogues": cats(code, k, label, sub), "kinds": kinds}
    al = list(l.get("alias_rows", []))
    for a in aliases:
        if a not in al: al.append(a)
    if al: entry["alias_rows"] = al
    res["leaves"][code] = entry
json.dump(res, open(os.path.join(HERE, "result.json"), "w"), ensure_ascii=False, indent=1)
print(dict(REPORT))
