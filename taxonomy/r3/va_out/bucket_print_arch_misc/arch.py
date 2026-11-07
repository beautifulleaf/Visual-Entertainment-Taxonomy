"""Architecture leaves: complete works catalogues from architecture_exemplars.csv and
architect grouping from architecture_architects.csv."""
import csv, re, collections, os
R = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
E = list(csv.DictReader(open(os.path.join(R, 'data/interim/architecture_exemplars.csv'))))
A = {r['qid']: r for r in csv.DictReader(open(os.path.join(R, 'data/interim/architecture_architects.csv')))}
AL = {}
for r in A.values():
    AL.setdefault(r['label'], r)
byS = collections.defaultdict(list)
for e in E:
    if e['list'] == 'style':
        byS[e['style_label'].lower()].append(e)

TYPES = [
    ('cathedrals, churches and monasteries', r'cathedral|church|basilica|chapel|abbey|monaster|convent|priory|minster|collegiate|charterhouse|friary|oratory|parish|sanctuary|bell tower|campanile|religious|synagogue|baptist|temple|seminary|mosque'),
    ('palaces, castles and houses', r'palace|castle|château|chateau|villa|house|manor|residence|mansion|hôtel|hotel particulier|palazzo|country house|fort|tower house|apartment|dwelling|building complex'),
    ('civic and public buildings', r'town hall|city hall|rathaus|hall|theatre|theater|opera|museum|library|university|college|school|hospital|exchange|lonja|market|bank|station|court|parliament|government|office|gate|bridge|monument|fountain|belfry|tower|stadium|pavilion|cinema|department store|factory|commercial|skyscraper|high-rise'),
]

def btype(e):
    s = e['instance_of_label'].lower() + ' ' + e['label'].lower()
    for name, rx in TYPES:
        if re.search(rx, s):
            return name
    return 'buildings of other or unrecorded type'

def gloss(e):
    bits = [e['country_label'].split('|')[0] or '']
    y = e['inception']
    if y:
        bits[-1] = (bits[-1] + ', ' if bits[-1] else '') + y
    tail = []
    if e['unesco_id']:
        tail.append('UNESCO World Heritage (part of site %s)' % e['unesco_id'] if e['tier_label'] == 'part_of_unesco' else 'UNESCO World Heritage site %s' % e['unesco_id'])
    elif e['tier_label'] == 'part_of_unesco':
        tail.append('part of a UNESCO World Heritage site')
    h = [x for x in e['heritage_label'].split('|') if x and x != 'World Heritage Site']
    if h:
        tail.append(h[0])
    arch = [x for x in e['architects_label'].split('|') if x and x != 'architectural ensemble']
    if arch:
        tail.insert(0, 'by ' + ', '.join(arch[:2]))
    g = '; '.join([b for b in bits if b] + tail)
    return g[:140]

def works(sections, generic, prefix, hi=None, exclude=()):
    """sections: list of (group_name, [style labels]); generic: [style labels] split by building type.
    Rule: every gathered exemplar with sitelinks>=1 or a heritage/UNESCO listing; inception <= hi."""
    seen = set(exclude)
    out = []
    def ok(e):
        if e['qid'] in seen:
            return False
        if not (int(e['sitelinks'] or 0) >= 1 or e['heritage'] or e['unesco_id'] or e['tier_label'] in ('unesco', 'part_of_unesco')):
            return False
        y = e['inception']
        if hi and y and re.match(r'^\d{3,4}$', y) and int(y) > hi:
            return False
        return True
    def key(e):
        y = e['inception']
        return int(y) if re.match(r'^-?\d+$', y or '') else 9999
    for gname, labels in sections:
        rows = []
        for lab in labels:
            for e in byS.get(lab.lower(), []):
                if ok(e):
                    seen.add(e['qid']); rows.append(e)
        for e in sorted(rows, key=key):
            out.append([e['label'], gname, gloss(e), 'r3 https://www.wikidata.org/wiki/' + e['qid'], 0])
    gen = collections.defaultdict(list)
    for lab in generic:
        for e in byS.get(lab.lower(), []):
            if ok(e):
                seen.add(e['qid']); gen[btype(e)].append(e)
    for name, _ in TYPES + [('buildings of other or unrecorded type', '')]:
        for e in sorted(gen.get(name, []), key=key):
            out.append([e['label'], prefix + ' ' + name, gloss(e), 'r3 https://www.wikidata.org/wiki/' + e['qid'], 0])
    return out

def architect_info(row):
    m = re.search(r'\((Q\d+)\)\s*$', row[2])
    if m and m.group(1) in A:
        return A[m.group(1)]
    return AL.get(row[0])

def arch_gloss(row, info):
    g = row[2]
    m = re.match(r'(\d+) exemplar building\(s\): ([^|(]*)', g)
    bits = []
    if info:
        b = info['birth'] or ''
        d = info['death'] or ''
        if b and d:
            bits.append(f"{b}–{d}")
        elif b or d:
            bits.append(f"b. {b}" if b else f"d. {d}")
        if info['citizenship']:
            bits.append(info['citizenship'].split('|')[0])
    if m:
        bl = m.group(2).strip().rstrip(';').strip()
        bits.append(bl)
    return ', '.join(bits)[:140] if bits else ''

ARCH_BLD = collections.defaultdict(list)
for e in E:
    for q in e['architects'].split('|'):
        if q:
            ARCH_BLD[q].append(e)

def architect_group(row, regmap, cutoff, revival_group, fallback_prefix=''):
    """regmap: country -> group name. Architects born after cutoff go to revival_group."""
    info = architect_info(row)
    m = re.search(r'\((Q\d+)\)\s*$', row[2])
    q = m.group(1) if m else (info['qid'] if info else None)
    b = None
    if info and re.match(r'^-?\d+$', info['birth'] or ''):
        b = int(info['birth'])
    if b is not None and cutoff and b > cutoff:
        return revival_group
    cs = collections.Counter(e['country_label'].split('|')[0] for e in ARCH_BLD.get(q, []))
    c = cs.most_common(1)[0][0] if cs else ''
    if not c and info:
        c = info['citizenship'].split('|')[0]
    return regmap.get(c, c or 'Other')
