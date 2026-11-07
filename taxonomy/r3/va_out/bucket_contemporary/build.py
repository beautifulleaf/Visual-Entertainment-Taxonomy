import json, csv, collections, re, sys
sys.path.insert(0, '.')
import mapping as M

d = json.load(open('../../va_in/bucket_contemporary.json'))
LEAVES = [l['code'] for l in d['leaves']]
info = json.load(open('info.json'))
la = {}
for r in csv.DictReader(open('../../../../data/interim/contemporary_list_artists.csv')):
    la.setdefault(r['name'], r)

QMAP = {'Q878': 'United Arab Emirates', 'Q1020': 'Malawi', 'Q986': 'Eritrea', 'Q1007': 'Guinea-Bissau', 'Q1000': 'Gabon',
        'Q34020': 'Niue', 'Q819': 'Laos', 'Q8646': 'Hong Kong', 'Q15': 'Africa', 'Q3908': 'Galicia', 'Q105113856': 'Chile',
        'Q130276': 'Uzbekistan', 'Q82112': 'United States', 'Q407199': 'Palestine', 'Q80338': 'Pakistan', 'Q18129046': '', 'Q33296': '',
        'Q3457190': ''}
RENAME = {"People's Republic of China": 'China', 'Kingdom of the Netherlands': 'Netherlands', 'Kingdom of Denmark': 'Denmark',
          'British Hong Kong': 'Hong Kong', 'East Germany': 'Germany', 'Czechoslovakia': 'Czech Republic',
          'Polish People\'s Republic': 'Poland', 'Georgian SSR': 'Georgia', 'England': 'United Kingdom', 'Korea': 'South Korea',
          'Republic of the Congo': 'Republic of the Congo', 'Democratic Republic of the Congo': 'DR Congo',
          'Ivory Coast': "Côte d'Ivoire", 'Northern Cyprus': 'Cyprus'}
HIST = {'Soviet Union', 'British Raj', 'Dominion of India', 'Pahlavi Iran', 'Qajar Iran', 'Empire of Japan', 'Kingdom of Italy',
        'Yugoslavia', 'Socialist Federal Republic of Yugoslavia', 'Mandatory Palestine', 'Dominion of Pakistan',
        'French protectorate of Tunisia', 'Kingdom of Great Britain', 'Russian Empire', 'Ottoman Empire'}
FRENCH_PROT = {'French protectorate of Tunisia': 'Tunisia', 'British Raj': 'India', 'Dominion of India': 'India', 'Pahlavi Iran': 'Iran',
               'Qajar Iran': 'Iran', 'Empire of Japan': 'Japan', 'Kingdom of Italy': 'Italy', 'Kingdom of Great Britain': 'United Kingdom',
               'Russian Empire': 'Russia', 'Yugoslavia': 'Yugoslavia', 'Soviet Union': 'Soviet Union'}

CITY = {'buenos aires':'Argentina','harare':'Zimbabwe','london':'United Kingdom','paris':'France','berlin':'Germany','accra':'Ghana','lagos':'Nigeria','lima':'Peru','manaus':'Brazil','luanda':'Angola','brussels':'Belgium','montreal':'Canada','mexico city':'Mexico','los angeles':'United States','new york':'United States','new york city':'United States','amsterdam':'Netherlands','rosario':'Argentina','rome':'Italy','faenza':'Italy','palermo':'Italy','cochabamba':'Bolivia','masaya':'Nicaragua','comalapa':'Guatemala','cuajinicuilapa':'Mexico','comunidad la puntana':'Argentina','lanus':'Argentina','seoul':'South Korea','cairo':'Egypt','ga-rankuwa':'South Africa','casablanca':'Morocco','kranj':'Slovenia'}
CLEAN = {'USA':'United States','UK':'United Kingdom','Great Britain':'United Kingdom','New-Zealand':'New Zealand','Irak':'Iraq','Suede':'Sweden','Macedonia':'North Macedonia','People’s Republic of China':'China','in Japan':'Japan','Qing dynasty':'China','Jerusalem':'','Korea':'South Korea','Deutschland':'Germany','Schweiz':'Switzerland','Österreich':'Austria','Frankreich':'France','Italien':'Italy','Grossbritannien':'United Kingdom','Großbritannien':'United Kingdom','Belgien':'Belgium','Japan':'Japan','Indien':'India','Brasilien':'Brazil','China':'China','Polen':'Poland','Kanada':'Canada','Spanien':'Spain','Niederlande':'Netherlands','Dänemark':'Denmark','Südafrika':'South Africa','Schweden':'Sweden','Norwegen':'Norway','Mexiko':'Mexico','Argentinien':'Argentina','Kolumbien':'Colombia','Russland':'Russia','Rumänien':'Romania','Türkei':'Turkey','Libanon':'Lebanon','Ägypten':'Egypt','Südkorea':'South Korea','Thailand':'Thailand'}
def clean1(x):
    x = x.strip()
    m = re.match(r'(?i)(lives|based) in ([^,/]+?)(?: and .*| until .*)?$', x)
    if m: return CITY.get(m.group(2).strip().lower(), '')
    if x.lower() in CITY: return CITY[x.lower()]
    x = re.sub(r'\s*/\s*b$', '', x)
    if x in ('/b', '') or '[Unknown]' in x or x.startswith('/'): return ''
    return CLEAN.get(x, x)

def country(raw):
    raw = ','.join(clean1(p) for p in re.split(r'[,;]', raw))
    parts = []
    for x in raw.split(','):
        x = x.strip()
        if x.startswith('French protectorat'): x = 'French protectorate of Tunisia'
        if x.startswith('Croatia, Yugoslavi'): x = 'Croatia'
        x = QMAP.get(x, x)
        if x: parts.append(x)
    if not parts: return ''
    modern = [p for p in parts if p not in HIST]
    c = modern[0] if modern else FRENCH_PROT.get(parts[0], parts[0])
    return RENAME.get(c, c)

REGION = {}
for reg, cs in {
    'Africa': "Algeria;Angola;Benin;Botswana;Cameroon;DR Congo;Republic of the Congo;Côte d'Ivoire;Egypt;Eritrea;Ethiopia;Gabon;Ghana;Guinea-Bissau;Kenya;Liberia;Madagascar;Malawi;Mali;Morocco;Mozambique;Namibia;Nigeria;Senegal;Sierra Leone;South Africa;Sudan;Togo;Tunisia;Uganda;Zambia;Zimbabwe;Africa;Burkina Faso;Rwanda;Tanzania;Cape Verde;São Tomé and Príncipe",
    'Middle East and Central Asia': "Afghanistan;Bahrain;Iran;Iraq;Israel;Jordan;Kuwait;Lebanon;Palestine;Saudi Arabia;Syria;Turkey;United Arab Emirates;Qatar;Kazakhstan;Tajikistan;Uzbekistan;Kyrgyzstan;Armenia;Azerbaijan;Georgia;Oman;Yemen",
    'Asia': "Bangladesh;Cambodia;China;Hong Kong;India;Indonesia;Japan;Laos;Malaysia;Mongolia;Myanmar;Nepal;Bhutan;Pakistan;Philippines;Singapore;South Korea;Sri Lanka;Taiwan;Thailand;Vietnam;North Korea",
    'Europe': "Albania;Austria;Belarus;Belgium;Bosnia and Herzegovina;Bulgaria;Croatia;Cyprus;Czech Republic;Denmark;Estonia;Finland;France;Germany;Greece;Hungary;Iceland;Ireland;Italy;Kosovo;Latvia;Lithuania;Luxembourg;Monaco;Netherlands;North Macedonia;Norway;Poland;Portugal;Romania;Russia;Serbia;Slovakia;Slovenia;Spain;Sweden;Switzerland;Ukraine;United Kingdom;Galicia;Soviet Union;Yugoslavia;Montenegro;Moldova;Malta;North Macedonia",
    'Americas and Caribbean': "Argentina;Barbados;Brazil;Canada;Chile;Colombia;Costa Rica;Cuba;Dominican Republic;El Salvador;Guatemala;Guyana;Haiti;Jamaica;Mexico;Paraguay;Peru;Puerto Rico;Saint Lucia;Suriname;The Bahamas;Trinidad and Tobago;United States;Uruguay;Venezuela;Bolivia;Ecuador;Nicaragua;Honduras;Panama",
    'Oceania': "Australia;New Zealand;Niue;Samoa;Fiji;Papua New Guinea;Tonga"}.items():
    for c in cs.split(';'): REGION[c] = reg

MED = {'painting': 'painter', 'sculpture': 'sculptor', 'installation, performance and conceptual': 'installation and performance',
       'video, new media and digital': 'video and new media', 'street art and muralism': 'street art and murals', 'photography': 'photographer',
       'drawing and illustration': 'drawing and illustration', 'design and decorative arts': 'design', 'visual art (unspecified)': ''}
LISTNAME = {'sharjah_biennial': 'Sharjah Biennial', 'documenta': '', 'dakart': "Dak'Art", 'kochi_muziris_biennale': 'Kochi-Muziris Biennale',
            'sao_paulo_bienal': 'São Paulo Bienal', 'gwangju_biennale': 'Gwangju Biennale', 'artprice_top500': 'Artprice Top 500',
            'istanbul_biennial': 'Istanbul Biennial', 'artprice_ultra100': 'Artprice Ultra 100', 'venice_biennale': 'Venice Biennale',
            'prize_jameel': 'Jameel Prize', 'artprice_ultra_debuts_top10': 'Artprice Ultra debuts', 'artreview_power100': 'ArtReview Power 100',
            'prize_turner': 'Turner Prize', 'prize_venice_lions': 'Venice Biennale Golden Lion', 'prize_marcel_duchamp': 'Prix Marcel Duchamp',
            'prize_future_generation': 'Future Generation Art Prize', 'kunstkompass': 'Kunstkompass', 'prize_prince_claus': 'Prince Claus Award',
            'prize_hugo_boss': 'Hugo Boss Prize', 'prize_praemium_imperiale': 'Praemium Imperiale'}

def edition(name):
    x = la.get(name)
    if not x or not x['editions']: return ''
    e = x['editions'].split('|')[0]
    lst, _, ed = e.partition(':')
    base = LISTNAME.get(lst, lst)
    if lst == 'documenta': return ed.replace('documenta', 'documenta').strip()
    if lst == 'sharjah_biennial': ed = ed.replace('SB', '')
    if lst == 'istanbul_biennial': ed = ed.split(',')[0]
    return f"{base} {ed}".strip()

def ed_group(e):
    if not e: return 'Country not recorded'
    if e.startswith('Artprice'): return 'Art-market lists (Artprice), country not recorded'
    return f"{e} participants, country not recorded"

def gloss(name, meta, code):
    i = info.get(name, {})
    b = i.get('b') or (meta or {}).get('birth', '')
    c = country(i.get('c') or (meta or {}).get('countries', ''))
    med = MED.get((meta or {}).get('medium', ''), '')
    bits = []
    if b and b.isdigit() and int(b) > 1800 and int(b) < 2000 and not re.search(r'collective|group|company|studio|archive|lab', name, re.I): bits.append(f"b. {b}")
    elif b and b.isdigit() and int(b) >= 1900: bits.append(f"active from {b}")
    if c: bits.append(c)
    s = ', '.join(bits)
    if med: s = (s + '; ' if s else '') + med
    if not c:
        e = edition(name)
        if e: s = (s + ' · ' if s else '') + e
    return s

ALLIN = {l['code']: l for l in d['leaves']}
rows_for = collections.defaultdict(list)  # leaf -> list of (name, group, gloss, source, is_maker, birth, country)
moves_out, dropped, new_rows = [], [], collections.defaultdict(list)

for l in d['leaves']:
    code = l['code']
    for r in l['rows']:
        name = r[0]; meta = r[5] if len(r) > 5 else {}
        if not r[4]:
            continue
        if not name.strip():
            moves_out.append([name, code, 'A5-110']); continue
        i = info.get(name, {})
        b = i.get('b') or meta.get('birth', '')
        c = country(i.get('c') or meta.get('countries', ''))
        g = gloss(name, meta, code)
        src = r[3]
        if name in M.OUT:
            tgt, grp = M.OUT[name]
            if tgt.startswith('NEW:'):
                new_rows[tgt[4:]].append([name, grp, g, src, 1, b]); continue
            if tgt in ALLIN:
                rows_for[tgt].append([name, grp or c, g, src, 1, b, c, 'named' if grp else 'country']); continue
            moves_out.append([name, code, tgt]); continue
        if name in M.JUNK:
            rows_for[code].append([name, 'Unverified list entries', g or 'entry carried over from a contemporary-art list; not verified as an artist', src, 1, b, c, 'junk']); continue
        if name in M.GROUP:
            rows_for[code].append([name, M.GROUP[name], g, src, 1, b, c, 'named']); continue
        rows_for[code].append([name, None, g, src, 1, b, c, 'country'])

# non-maker rows
dropped += [['A5-111', 'Cree [Cold Lake First Nations]', 'museum culture label for a lot of ink drawings, not a kind of contemporary art'],
            ['A5-111', 'Potawatomi [Oklahoma]', 'museum culture label for a lot of ink drawings, not a kind of contemporary art'],
            ['L2-51', 'mural - Ukraine (modern)', 'generic in-situ route label with no named work'],
            ['L2-51', 'mural - Kosovo (modern)', 'generic in-situ route label with no named work'],
            ['L2-51', 'mural - Lithuania (modern)', 'generic in-situ route label with no named work']]
WP = 'r3 https://en.wikipedia.org/wiki/'
SUBTYPES = {
 'A5-111': [['Toyism', 'Dutch movement (1990s) of painting with toy-like figures and a mock-naive manner', 'europe_folk'],
            ['Neo-geo', 'New York, mid-1980s: geometric, commodity-referencing painting and objects (Halley, Bickerton)', WP + 'Neo-geo_(art)'],
            ['New Leipzig School', 'figurative painters trained at the Leipzig Academy (HGB) from the 1990s, around Neo Rauch', WP + 'New_Leipzig_School'],
            ['New Glasgow Boys', 'figurative painters from Glasgow School of Art in the 1980s', WP + 'New_Glasgow_Boys'],
            ['Stars Art Group', 'Beijing unofficial artists group, 1979–1983', WP + 'Stars_Art_Group'],
            ['Scar art', 'Chinese painting of the late 1970s on the trauma of the Cultural Revolution', WP + 'Scar_art'],
            ['Cynical realism', 'Beijing painting of the early 1990s (Fang Lijun, Yue Minjun)', WP + 'Cynical_realism'],
            ['Political pop', 'Chinese painting of the late 1980s–90s mixing Mao-era imagery and consumer brands', WP + 'Political_pop'],
            ['Beijing East Village', 'performance-art community in Beijing, 1993–1994', WP + 'Beijing_East_Village'],
            ['Sots Art', 'Soviet pop art from 1972 (Komar and Melamid)', WP + 'Sots_Art'],
            ['Chicano art movement', 'Mexican-American art of the civil-rights era and after', WP + 'Chicano_art_movement'],
            ['Feminist art movement', 'art of the women\'s movement from the late 1960s', WP + 'Feminist_art_movement']],
 'L2-51': [['Graffiti', 'name-writing and pieces with spray paint and markers, from Philadelphia and New York c. 1970', WP + 'Graffiti'],
           ['Stencil graffiti', 'images sprayed through cut stencils (Blek le Rat, Banksy)', WP + 'Stencil_graffiti'],
           ['Wheatpaste', 'paper posters and paste-ups glued to walls (JR, Swoon)', WP + 'Wheatpaste'],
           ['Sticker art', 'printed or drawn stickers placed in public space', WP + 'Sticker_art'],
           ['Yarn bombing', 'knitted or crocheted covers on street furniture (Olek)', WP + 'Yarn_bombing'],
           ['Reverse graffiti', 'images made by cleaning dirt from surfaces', WP + 'Reverse_graffiti'],
           ['Street installations', 'three-dimensional works placed in public space', WP + 'Street_installations']],
 'M1-1': [['Site-specific art', 'work made for, and inseparable from, a particular place', WP + 'Site-specific_art'],
          ['Sound installation', 'installation in which sound shapes the space', WP + 'Sound_installation'],
          ['Video installation', 'multi-screen or spatial presentation of video', WP + 'Video_installation'],
          ['Light art', 'art in which light is the main medium (Turrell, Elíasson)', WP + 'Light_art'],
          ['Immersive art', 'environments that surround the visitor (teamLab, Kusama)', WP + 'Immersive_art']],
 'M2-5': [['Digital art', 'art made or presented with digital technology', WP + 'Digital_art'],
          ['Post-internet', 'art of the late 2000s–2010s about the internet\'s effect on culture', WP + 'Post-Internet'],
          ['Software art', 'art in which the software itself is the work', WP + 'Software_art'],
          ['Glitch art', 'art made from digital or analogue errors (Rosa Menkman)', WP + 'Glitch_art'],
          ['Interactive art', 'work completed by the viewer\'s participation', WP + 'Interactive_art'],
          ['Bio art', 'art working with living tissue, bacteria or organisms (Eduardo Kac)', WP + 'Bio_art'],
          ['Crypto art', 'digital art issued and traded as blockchain tokens (NFTs)', WP + 'Crypto_art']],
}
alias = {'M2-5': [], 'L2-51': []}
# M2-5 group rows that restate sub-types
for code in ('M2-5',):
    pass

def order_key(r):
    b = r[5]
    return (int(b) if b and b.isdigit() else 9999, r[0].lower())

GEN = [(0, 1954, 'born before 1955'), (1955, 1964, 'born 1955–64'), (1965, 1974, 'born 1965–74'), (1975, 1984, 'born 1975–84'), (1985, 9998, 'born 1985 and later'), (9999, 9999, 'birth year not recorded')]

def finalize(code, rows):
    named = collections.OrderedDict(); country_rows = collections.defaultdict(list); junk = []
    for r in rows:
        if r[7] == 'named': named.setdefault(r[1], []).append(r)
        elif r[7] == 'junk': junk.append(r)
        else: country_rows[r[6]].append(r)
    out_groups = []
    # named groups, in mapping order
    order = list(dict.fromkeys([g for _, g in M.OUT.values() if g] + list(M.GROUP.values())))
    for g in sorted(named, key=lambda g: order.index(g) if g in order else 999):
        out_groups.append((g, named[g]))
    pooled = collections.defaultdict(list); unknown = collections.defaultdict(list)
    big = []
    for c, rs in country_rows.items():
        if not c:
            for r in rs: unknown[ed_group(edition(r[0]))].append(r)
        elif len(rs) < 3:
            pooled['Other countries: ' + REGION.get(c, 'elsewhere')].extend(rs)
        else:
            big.append((c, rs))
    big.sort(key=lambda x: -len(x[1]))
    for c, rs in big:
        if len(rs) > 150:
            for lo, hi, lab in GEN:
                sub = [r for r in rs if (int(r[5]) if r[5] and r[5].isdigit() else 9999) >= lo and (int(r[5]) if r[5] and r[5].isdigit() else 9999) <= hi]
                if sub: out_groups.append((f"{c}, {lab}", sub))
        else:
            out_groups.append((c, rs))
    RO = ['Europe', 'Americas and Caribbean', 'Asia', 'Middle East and Central Asia', 'Africa', 'Oceania', 'elsewhere']
    for k in sorted(pooled, key=lambda k: RO.index(k.split(': ')[1])):
        out_groups.append((k, pooled[k]))
    small_unknown = []
    for k in sorted(unknown, key=lambda k: -len(unknown[k])):
        if len(unknown[k]) < 5 and k != 'Country not recorded': small_unknown.extend(unknown[k])
        else: out_groups.append((k, unknown[k]))
    if small_unknown: out_groups.append(('Other biennial and prize lists, country not recorded', small_unknown))
    if junk: out_groups.append(('Unverified list entries', junk))
    kinds = []
    for g, rs in out_groups:
        for r in sorted(rs, key=order_key):
            gl = r[2]
            if g.startswith('Other countries') or g.startswith(r[6] + ',') or g == r[6]:
                pass
            kinds.append([r[0], g, gl, r[3], 1])
    return kinds

result = {'leaves': {}, 'new_leaves': [], 'moves_out': moves_out, 'dropped': dropped}
DEFN = json.load(open('texts.json'))
for code in LEAVES:
    rows = rows_for.get(code, [])
    kinds = []
    for name, gl, src in SUBTYPES.get(code, []):
        kinds.append([name, 'Sub-types', gl, src, 0])
    if code == 'D5-119':
        kinds.append(['Statue of Decebalus (1994–2004)', 'Monumental works', 'rock sculpture of the Dacian king above the Danube near Orșova, Romania; 40 m high', 'in_situ', 0])
    kinds += finalize(code, rows)
    t = DEFN[code]
    result['leaves'][code] = {'axis': t['axis'], 'defn': t.get('defn', ALLIN[code]['defn']), 'catalogues': t['catalogues'], 'kinds': kinds, 'alias_rows': t.get('alias_rows', [])}

for key, t in DEFN['_new'].items():
    rs = new_rows[key]
    gorder = list(dict.fromkeys(g for _, g in M.OUT.values() if g))
    rs.sort(key=lambda r: (gorder.index(r[1]), int(r[5]) if r[5] and r[5].isdigit() else 9999))
    kinds = [[n, g, gl, s, 1] for n, g, gl, s, _, b in rs]
    nl = dict(t); nl['key'] = key; nl['kinds'] = kinds
    result['new_leaves'].append(nl)

json.dump(result, open('result.json', 'w'), ensure_ascii=False, indent=1)
for code, v in result['leaves'].items():
    c = collections.Counter(k[1] for k in v['kinds'])
    print(code, len(v['kinds']), len(c), 'max', c.most_common(3))
for nl in result['new_leaves']: print(nl['key'], len(nl['kinds']))
print('moves', len(moves_out))
