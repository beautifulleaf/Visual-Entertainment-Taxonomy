import json, re, pickle, collections, os, sys, glob
ROOT = '/home/user/Visual-Entertainment-Taxonomy/'
W = ROOT + 'taxonomy/r3/va_out/small_D_F/work/'
OUT = ROOT + 'taxonomy/r3/va_out/small_D_F/result.json'
inp = json.load(open(ROOT + 'taxonomy/r3/va_in/small_D_F.json'))['leaves']
LEAF = {l['code']: l for l in inp}
CODES = list(LEAF)
WIKICHK = json.load(open(W + 'wikicheck.json')) if os.path.exists(W + 'wikicheck.json') else {}

def wurl(x):
    x = x.strip()
    if x.startswith('http'): return x
    return 'https://en.wikipedia.org/wiki/' + x.replace(' ', '_')

# ---------------- parse knowledge files ----------------
K = {}
for f in sorted(glob.glob(W + 'k*.txt')):
    cur = None
    for line in open(f, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line.strip(): continue
        if line.startswith('@'):
            cur = line[1:].strip()
            if cur in K: continue
            K[cur] = dict(axis='', defn='', cats=[], add=[], eq={}, drop={}, alias=[], move={}, G=[]); continue
        k = K[cur]
        if line.startswith('axis:'): k['axis'] = line[5:].strip()
        elif line.startswith('defn:'): k['defn'] = line[5:].strip()
        elif line.startswith('cat:'):
            p = [x.strip() for x in line[4:].split(' | ')]; k['cats'].append(p)
        elif line.startswith('+ '):
            p = [x.strip() for x in line[2:].split(' | ')]
            assert len(p) == 5, (cur, line)
            k['add'].append(p)
        elif line.startswith('= '):
            p = [x.strip() for x in line[2:].split(' | ')]
            assert len(p) >= 3, (cur, line)
            k['eq'][p[0]] = p
        elif line.startswith('- '):
            p = [x.strip() for x in line[2:].split(' | ')]; k['drop'][p[0]] = p[1] if len(p) > 1 else 'noise'
        elif line.startswith('a '): k['alias'].append(line[2:].strip())
        elif line.startswith('> ') or line.startswith('M '):
            p = [x.strip() for x in line[2:].split(' | ')]; k['move'][p[0]] = p[1]
        elif line.startswith('G '):
            p = [x.strip() for x in line[2:].split(' | ')]
            k['G'].append((p[0], [n.strip() for n in p[1].split(';') if n.strip()]))
        else: raise SystemExit(f'bad line in {cur}: {line}')

missingK = [c for c in CODES if c not in K]
if missingK: print('WARN no knowledge for', missingK)

# ---------------- helpers ----------------
POSS = re.compile(r'owned as (.+?) \(Possession ([A-Z]\d+)\)')
URL = re.compile(r'https?://\S+')
def poss_info(gloss):
    m = POSS.search(gloss or '')
    if not m: return None, None
    u = URL.search(gloss); return f'{m.group(1)} ({m.group(2)})', (u.group(0) if u else None)

def strip_poss(g):
    return re.sub(r'\s*·\s*Possession:.*$', '', g).strip()

def maker_gloss(r):
    ev = r[5] if len(r) > 5 and isinstance(r[5], dict) else {}
    parts = []
    if ev.get('birth'): parts.append('born ' + str(ev['birth'])[:4])
    if ev.get('countries'): parts.append('active in ' + ev['countries'].replace('|', ', '))
    return '; '.join(parts)

def clean_gloss(g, src):
    g = g or ''
    if src == 'evidence': return ''
    g = re.sub(r'\s*·?\s*owned as .*$', '', g)
    if re.search(r'Gathered rows|now T\d|excluded rows?|\brow\b|\brows\b|\bL\d+\b|seeded|route resolved|dominant|\b\d+ of \d+\b|\w+ \d{2,}\b', g): return ''
    return g.strip(' ;·')

GROUPMAP = {'maker': 'Makers', 'makers': 'Makers', 'Artists': 'Makers', 'Makers': 'Makers',
            'centre': 'Centres & workshops', 'Centres': 'Centres & workshops', 'workshop': 'Centres & workshops',
            'workshop/centre': 'Centres & workshops', 'art centre': 'Centres & workshops', 'Studios': 'Centres & workshops',
            'sub-type': 'Sub-types', 'type': 'Sub-types', 'sub-group': 'Sub-types', 'sub-style': 'Sub-types', 'style': 'Schools & phases',
            'phase': 'Schools & phases', 'school': 'Schools & phases', 'successor school': 'Schools & phases', 'regional style': 'Schools & phases',
            'people': 'Sub-types'}

# ---------------- object works & collections ----------------
MATCH = pickle.load(open(W + 'matches.pkl', 'rb'))
INSTMAP = {
 'NMAI': 'National Museum of the American Indian (Smithsonian), Washington DC',
 'Smithsonian National Museum of the American Indian': 'National Museum of the American Indian (Smithsonian), Washington DC',
 'NMAA': 'National Museum of Asian Art (Smithsonian), Washington DC',
 'NMAfA': 'National Museum of African Art (Smithsonian), Washington DC',
 'Smithsonian National Museum of African Art': 'National Museum of African Art (Smithsonian), Washington DC',
 'CHNDM': 'Cooper Hewitt, Smithsonian Design Museum, New York',
 'Cooper Hewitt, Smithsonian Design Museum': 'Cooper Hewitt, Smithsonian Design Museum, New York',
 'SAAM': 'Smithsonian American Art Museum, Washington DC', 'Smithsonian American Art Museum': 'Smithsonian American Art Museum, Washington DC',
 'NMNH': 'National Museum of Natural History (Smithsonian), Washington DC',
 'Smithsonian National Museum of Natural History': 'National Museum of Natural History (Smithsonian), Washington DC',
 'NMAH': 'National Museum of American History (Smithsonian), Washington DC',
 'HMSG': 'Hirshhorn Museum (Smithsonian), Washington DC',
 'The Metropolitan Museum of Art': 'Metropolitan Museum of Art, New York',
 'The British Museum': 'British Museum, London', 'British Museum': 'British Museum, London',
 'Victoria and Albert Museum': 'Victoria and Albert Museum, London',
 'Penn Museum': 'Penn Museum, Philadelphia', 'Art Institute of Chicago': 'Art Institute of Chicago',
 'Cleveland Museum of Art': 'Cleveland Museum of Art', 'Minneapolis Institute of Art': 'Minneapolis Institute of Art',
 'Museum Volkenkunde': 'Museum Volkenkunde, Leiden', 'Tropenmuseum': 'Tropenmuseum, Amsterdam',
 'Wereldmuseum Rotterdam': 'Wereldmuseum Rotterdam', 'Wereldmuseum (NMVW)': 'Wereldmuseum (NMVW), Netherlands',
 'Afrika Museum': 'Afrika Museum, Berg en Dal', 'Rijksmuseum': 'Rijksmuseum, Amsterdam',
 'Yale University (LUX)': 'Yale University collections (LUX), New Haven',
 'Tokyo National Museum': 'Tokyo National Museum', 'Kyoto National Museum': 'Kyoto National Museum',
 'Nara National Museum': 'Nara National Museum', 'Kyushu National Museum': 'Kyushu National Museum',
 '独立行政法人国立文化財機構': 'National Institutes for Cultural Heritage, Japan', '국립중앙박물관': 'National Museum of Korea, Seoul',
 'Museum of New Zealand Te Papa Tongarewa': 'Museum of New Zealand Te Papa Tongarewa, Wellington',
 'Rubin Museum of Art': 'Rubin Museum of Art, New York', 'Zanabazar Museum of Fine Arts': 'Zanabazar Museum of Fine Arts, Ulaanbaatar',
 'The David Collection': 'David Collection, Copenhagen', 'Benaki Museum': 'Benaki Museum, Athens', 'Aga Khan Museum': 'Aga Khan Museum, Toronto',
 'National Palace Museum': 'National Palace Museum, Taipei', 'Museo Nacional de Arte': 'Museo Nacional de Arte, Mexico City',
 'MKG Museum for Applied Arts': 'Museum für Kunst und Gewerbe, Hamburg',
 'Museum of Islamic Art at the Pergamon Museum': 'Museum of Islamic Art, Pergamonmuseum, Berlin',
}
def norm_inst(i):
    i = (i or '').strip()
    if i in INSTMAP: return INSTMAP[i]
    b = re.sub(r'\s*\([^)]*\)$', '', i).strip()
    if b in INSTMAP: return INSTMAP[b]
    if b != i and b: return b
    return i[:90]

GENERIC = set('''a an the of with and or in on at from for to by its his her their two three four pair set small large miniature little
mask masks headdress headcrest helmet face figure figures figurine figurines statue statuette statuettes sculpture image icon head heads bust
standing seated kneeling female male woman women man men child children mother couple boy girl human animal bird fragment fragments piece part
bowl cup vessel jar pot bottle box casket container lid cover plate dish vase ewer jug beaker flask basin
relief panel plaque plaques stele stela tablet slab tile ornament pendant amulet bead beads necklace bracelet ring earring ornaments jewellery jewelry
puppet puppets doll dolls toy toys marionette carving carvings carved object objects item model models comb spoon ladle staff stool seat chair pipe
fetish charm power reliquary guardian door post pole lamp shade cylinder seal stamp disc disk ivory wood wooden stone bronze brass copper iron gold silver clay terracotta
glass glazed painted ceramic earthenware stoneware porcelain jade nephrite hardstone shell bone antler horn tooth tusk leather textile
untitled unknown possibly probably attributed style type form decoration decorated design inscribed fragmentary
with of de het een van en met voorstellende beeld beeldje masker pop poppen wajangpop schaal kom hanger kist doos figuur mannelijk vrouwelijk
staande zittende hoofd fragment deel snijwerk houten stenen imitatie
'''.split())
CATS = [('Masks and headdresses', r'mask|headdress|headcrest|helmet|masker|okuyi|kanaga|kifwebe|sowo|tatanua|topeng'),
        ('Puppets and dolls', r'puppet|marionette|doll|wayang|pop\b|poppen|ningy|kokeshi|kachina|katsina|tihu'),
        ('Heads and busts', r'\bhead\b|\bbust\b|hoofd'),
        ('Figures and statuettes', r'figur|statue|statuette|image|buddha|bodhisattva|deity|god\b|goddess|beeld|idol|tiki|bulul|nkisi|nkondi|ibeji|akua|haniwa|santo|bulto|ancestor|warrior|horse|lion|dog|bird|animal'),
        ('Reliefs, panels and plaques', r'relief|panel|plaque|stele|stela|lintel|slab|tablet|pilaster|roundel|frieze|window|inscription'),
        ('Vessels and containers', r'bowl|cup|vessel|jar|bottle|box|casket|pyxis|ewer|jug|beaker|flask|vase|basin|dish|plate|lamp|container|kom|schaal|pot\b'),
        ('Ornaments and jewellery', r'pendant|amulet|bead|necklace|bracelet|ring\b|earring|ornament|gorget|brooch|cameo|comb|hanger|netsuke|toggle|seal'),
        ('Tools, weapons and regalia', r'staff|stool|chair|seat|club|knife|dagger|sword|spear|harpoon|pipe|tool|spoon|ladle|whistle|drum|instrument|shield|paddle|door|post|pole')]
NONLATIN = re.compile(r'[^\x00-ɏ\s\d\W]')

def fmt_date(d):
    try: y = int(float(d))
    except Exception: return ''
    return f'c. {-y} BC' if y < 0 else f'c. {y}'

def obj_works(code, label_words):
    df = MATCH.get(code)
    if df is None or len(df) == 0: return [], [], 0
    df = df.copy()
    df['instn'] = df.inst.map(norm_inst)
    good = df[~df.instn.str.lower().isin(['private', '', 'unknown', 'nan']) & df.url.str.startswith('http')]
    # collections
    vc = good.instn.value_counts()
    sel = [i for i, n in vc.items() if n >= 10]
    if len(sel) < 8: sel = list(vc.index[:8])
    coll = []
    for i in sel:
        n = int(vc[i]); u = good[good.instn == i].url.iloc[0]
        coll.append([i, 'Collections', f'{i} — {n} object{"s" if n != 1 else ""} in the gathered records'[:140], 'r3 ' + u, 0])
    # works
    stop = GENERIC | label_words
    cand = []
    seen = set()
    for _, r in good.iterrows():
        t = re.sub(r'\s+', ' ', str(r.title or '')).strip().strip('.')
        if not t or len(t) > 110: continue
        if t.isupper(): t = t.capitalize()
        low = t.lower()
        latin = not NONLATIN.search(t)
        if re.search(r'[Ѐ-ӿ]', t):
            if not re.search(r'[«"“].+[»"”]', t): continue
        elif latin:
            toks = [w for w in re.findall(r"[a-zà-ÿāēīōūɛɔ'’]+", low) if len(w) > 2]
            rest = [w for w in toks if w not in stop and w.rstrip('s') not in stop]
            if not rest: continue
        key = low
        if key in seen: continue
        seen.add(key)
        try: d = int(float(r.date))
        except Exception: d = 99999
        cand.append((0 if latin else 1, d, t, r))
    cand.sort(key=lambda x: (x[0], x[1]))
    nall = len(cand)
    cand = cand[:40]
    cand.sort(key=lambda x: x[1])
    works = []
    for _, d, t, r in cand:
        tt = t + ' ' + str(r.ot) + ' ' + str(r.mat)
        grp = 'Other titled objects'
        for g, pat in CATS:
            if re.search(pat, tt, re.I): grp = g; break
        gl = '; '.join(x for x in [fmt_date(r.date) if d != 99999 else '', r.instn] if x)
        works.append([t, 'Titled objects: ' + grp.lower() if False else 'Titled objects: ' + grp, gl[:140], 'r3 ' + r.url, 0])
    return works, coll, nall

ORDER = ['Sub-types', 'Sub-styles', 'Sub-groups', 'Schools & phases', 'Related styles', 'Centres & workshops', 'Named giants', 'Relief series', 'Named works']
def grank(g, Gorder):
    if g in Gorder: return (1, Gorder.index(g))
    if g in ORDER: return (0, ORDER.index(g)) if g not in ('Named works', 'Relief series', 'Named giants') else (2, ORDER.index(g))
    if g.startswith('Titled objects'): return (3, 0)
    if g == 'Collections': return (4, 0)
    if g == 'Makers': return (5, 0)
    return (1, 99)

# ---------------- assemble ----------------
out = {'leaves': {}, 'new_leaves': [], 'moves_out': [], 'dropped': []}
placed = collections.defaultdict(list)   # target code -> rows moved in from other pass leaves
report = collections.Counter()
unmentioned = []
allrows = {}
for c in CODES:
    for r in LEAF[c]['rows']: allrows.setdefault(r[0], (c, r))

# first pass: moves
for c in CODES:
    k = K.get(c, {})
    for r in LEAF[c]['rows']:
        if r[0] in k.get('move', {}):
            t = k['move'][r[0]]
            if t in LEAF: placed[t].append((c, r))
            else: out['moves_out'].append([r[0], c, t]); report['moved_out'] += 1

for c in CODES:
    L = LEAF[c]; k = K.get(c, dict(axis='', defn='', cats=[], add=[], eq={}, drop={}, alias=[], move={}, G=[]))
    gmap = {}
    for g, names in k['G']:
        for n in names: gmap[n] = g
    Gorder = [g for g, _ in k['G']]
    kinds = []; aliases = list(k['alias'])
    for d in ('eq', 'drop'):
        for key in list(k[d]):
            if key not in {r[0] for r in L['rows']}:
                full = [r[0] for r in L['rows'] if r[0].startswith(key)]
                if full: k[d][full[0]] = k[d].pop(key)
                else: print('WARN unmatched key', c, d, key)
    rows = [(c, r) for r in L['rows'] if r[0] not in k['move']] + placed.get(c, [])
    for src_leaf, r in rows:
        name, grp, gloss, src, ism = r[0], r[1], r[2] or '', r[3] or '', r[4]
        if name == '' and (ism or grp == 'Artists'):
            continue  # handled below
        pinfo, purl = poss_info(gloss)
        isM = bool(ism) or grp in ('Artists', 'Makers', 'Architects', 'maker', 'makers')
        if name in k['drop'] and not isM:
            rs = k['drop'][name]
            if re.search(r'restat|duplicate|label', rs):
                if name not in aliases: aliases.append(name)
                report['alias'] += 1; continue
            out['dropped'].append([c, name, rs]); report['dropped'] += 1; continue
        if name in k['eq']:
            e = k['eq'][name]; ng, gl = e[1], e[2]
            if ng == 'Makers': isM = True
        elif name in gmap:
            ng, gl = gmap[name], maker_gloss(r) or clean_gloss(gloss, src)
        elif isM:
            ng, gl = 'Makers', maker_gloss(r) or clean_gloss(gloss, src)
            if src_leaf == c and not k['G']: pass
            unmentioned.append((c, name, 'maker'))
        elif grp.startswith('Gathered rows'):
            if name not in aliases: aliases.append(name)
            report['alias'] += 1; continue
        else:
            ng, gl = GROUPMAP.get(grp, grp or 'Sub-types'), clean_gloss(gloss, src)
            unmentioned.append((c, name, grp))
        gl = strip_poss(gl)
        if pinfo: gl = (gl + ' · Possession: ' + pinfo) if gl else 'Possession: ' + pinfo
        nsrc = src
        if src.startswith('possession') and purl: nsrc = 'possession ' + purl
        elif src.startswith('possession'): nsrc = 'possession'
        kinds.append([name, ng, gl[:200], nsrc, 1 if isM else 0])
    # empty-name maker rows
    for r in L['rows']:
        if r[0] == '' and (r[4] or r[1] == 'Artists'):
            out['moves_out'].append(['', c, 'D5-118']); report['empty_moved'] += 1
    for a in k['add']:
        g, n, gl, s, m = a
        if g == 'Works': g = 'Named works'
        kinds.append([n, g, gl[:200], 'r3 ' + wurl(s), int(m)])
        report['added'] += 1
    # computed works and collections
    lw = set(w for w in re.findall(r"[a-zà-ÿ']+", (L['label'] + ' ' + (L['aliases'] or '')).lower()) if len(w) > 2)
    works, coll, nall = obj_works(c, lw)
    existing = {x[0].lower() for x in kinds}
    works = [w for w in works if w[0].lower() not in existing]
    kinds += works + coll
    report['works'] += len(works); report['coll'] += len(coll)
    # order
    idx = {id(x): i for i, x in enumerate(kinds)}
    kinds.sort(key=lambda x: (grank(x[1], Gorder), idx[id(x)]))
    axis = k['axis'] or 'sub-types first, then centres and makers'
    axis = axis.replace('titled works (rule below)', 'titled museum objects')
    if works:
        axis += (f'. Titled museum objects: every object in the gathered museum files for this tradition whose title names more than its object type or culture '
                 f'(one per title, museum page required), the 40 earliest-dated ({nall} qualify), grouped by object type')
    if coll:
        axis += '. Collections: holding institutions ranked by objects in the gathered files (all with 10 or more, else the top 8)'
    entry = {'axis': axis, 'catalogues': [[x[0], x[1], x[2]] for x in k['cats']], 'kinds': kinds, 'alias_rows': aliases}
    if k['defn']: entry['defn'] = k['defn']
    out['leaves'][c] = entry

json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=0)
print(dict(report))
print('unmentioned rows:', len(unmentioned))
for u in unmentioned: print('  ', u)
