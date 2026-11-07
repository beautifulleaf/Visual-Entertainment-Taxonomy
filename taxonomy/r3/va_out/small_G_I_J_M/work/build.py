import json, re, os, sys, csv, html, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.join(HERE, '../../../../..')
from kutil import U
import k1, k2, k3
K = {**k1.K, **k2.K, **k3.K}
OV = {**k1.OV, **k2.OV, **k3.OV}
AG = k3.AG
inp = json.load(open(os.path.join(ROOT, 'taxonomy/r3/va_in/small_G_I_J_M.json')))['leaves']
CODES = {l['code'] for l in inp}
M = json.load(open(os.path.join(HERE, 'matches.json')))
SUB, SCH, CEN, MAK, COL = 'Sub-types', 'Schools & phases', 'Centres & workshops', 'Makers', 'Collections'
ARTIST_LED = {'I3-6', 'I3-7', 'I3-8', 'I3-9', 'I3-10', 'I3-11', 'I3-12', 'I3-13', 'I3-14', 'I3-17', 'I3-18'} | {c for c in CODES if c[0] in 'JM'}
# moves of makers: name -> target code
MOVES = {'Alfred A. Hart': 'J1-7', 'Dennis Oppenheim': 'M1-6', 'Stuart Brisley': 'M1-8', 'Agostino Scilla': 'A5-25',
         'Gustav Fabergé': 'G3-20', 'Peter Carl Fabergé': 'G3-20', 'Michael Perkhin': 'G3-20', 'Henrik Wigström': 'G3-20', 'Johan Victor Aarne': 'G3-20',
         'Anders Nevalainen': 'G3-20', 'Erik August Kollin': 'G3-20', 'Feodor Rückert': 'G3-20', 'Hester Bateman': 'G1-45', 'John Harrison': 'G1-52',
         'Matthew Boulton': 'G1-37', 'Kwaku Benpoh': 'D5-48', '': 'I3-20'}
MOVE_GLOSS = {'Gustav Fabergé': 'founder of the House of Fabergé in St Petersburg, 1814–93', 'Peter Carl Fabergé': 'head of the House of Fabergé, 1846–1920',
              'Michael Perkhin': 'Fabergé head workmaster, maker of Imperial eggs, 1860–1903', 'Henrik Wigström': 'Fabergé head workmaster after Perkhin, 1862–1923',
              'Johan Victor Aarne': 'Fabergé workmaster in gold and enamel, 1863–1934', 'Anders Nevalainen': 'Fabergé workmaster, 1858–1933',
              'Erik August Kollin': 'Fabergé first head workmaster, 1836–1901', 'Feodor Rückert': 'Moscow enameller supplying Fabergé, 1840–1917',
              'Hester Bateman': 'London silversmith, 1708–94', 'John Harrison': 'clockmaker, inventor of the marine chronometer (H4, 1759), 1693–1776',
              'Matthew Boulton': 'Birmingham manufacturer of ormolu and silver at the Soho Manufactory, 1728–1809', 'Nicholas of Verdun': 'Mosan goldsmith and enameller, c. 1130–1205',
              'Dennis Oppenheim': 'American land and body artist, 1938–2011', 'Stuart Brisley': 'British performance artist, b. 1933'}
ADDC = {'Benvenuto Cellini': 'Italy', 'Wenzel Jamnitzer': 'Germany', 'Charles Le Brun': 'France', 'Jean Berain the Elder': 'France', 'Juste-Aurèle Meissonnier': 'France',
        'Charles Cressent': 'France', 'Charles Percier': 'France', 'Pierre-François-Léonard Fontaine': 'France', 'François-Honoré-Georges Jacob-Desmalter': 'France',
        'Josef Danhauser': 'Austria', 'Augustus Pugin': 'United Kingdom', 'William Morris': 'United Kingdom', 'C. R. Ashbee': 'United Kingdom', 'Ernest Gimson': 'United Kingdom',
        'Walter Gropius': 'Bauhaus masters and students', 'Marcel Breuer': 'Bauhaus masters and students', 'Marianne Brandt': 'Bauhaus masters and students',
        'Wilhelm Wagenfeld': 'Bauhaus masters and students', 'Gunta Stölzl': 'Bauhaus masters and students', 'Anni Albers': 'Bauhaus masters and students',
        'Yanagi Sōetsu': 'Founding circle', 'Bernard Leach': 'Founding circle', 'Munakata Shikō': 'Mingei potters and craftsmen', 'Serizawa Keisuke': 'Mingei potters and craftsmen'}
CN = {'United States of America': 'United States', 'Francia': 'France', 'Republic of Venice': 'Italy', 'Republic of Siena': 'Italy', 'Kingdom of Scotland': 'United Kingdom',
      'Kingdom of England': 'United Kingdom', 'Kingdom of Great Britain': 'United Kingdom', 'Holy Roman Empire': 'Germany', 'Kingdom of Prussia': 'Germany', 'Russian Empire': 'Russia',
      'Soviet Union': 'Russia', 'Empire of Japan': 'Japan', 'Austrian Empire': 'Austria', 'Austria-Hungary': 'Austria', 'German Reich': 'Germany', 'Grand Duchy of Finland': 'Finland',
      'Dutch Republic': 'Netherlands', 'Kingdom of the Netherlands': 'Netherlands', 'Duchy of Milan': 'Italy', 'Grand Duchy of Tuscany': 'Italy', 'Papal States': 'Italy',
      'Kingdom of Naples': 'Italy', 'Kingdom of Sardinia': 'Italy', 'Kingdom of Bavaria': 'Germany', 'Kingdom of Saxony': 'Germany', 'Kingdom of Württemberg': 'Germany',
      'Electorate of Saxony': 'Germany', 'Kingdom of Bohemia': 'Czech Republic', 'Kingdom of Hungary': 'Hungary', 'Kingdom of Denmark': 'Denmark', 'Denmark–Norway': 'Denmark',
      'Kingdom of Sweden': 'Sweden', 'Kingdom of France': 'France', 'First French Empire': 'France', 'Second French Empire': 'France', 'Kingdom of Portugal': 'Portugal',
      'Spanish Empire': 'Spain', 'Kingdom of Spain': 'Spain', 'Ottoman Empire': 'Turkey', 'Habsburg monarchy': 'Austria', 'Archduchy of Austria': 'Austria',
      "People's Republic of China": 'China', 'Czechoslovakia': 'Czech Republic', 'East Germany': 'Germany', 'West Germany': 'Germany', 'Weimar Republic': 'Germany', 'Nazi Germany': 'Germany',
      'Kingdom of Italy': 'Italy', 'Kingdom of Belgium': 'Belgium', 'Southern Netherlands': 'Belgium', 'Austrian Netherlands': 'Belgium', 'Kingdom of Poland': 'Poland',
      'Polish–Lithuanian Commonwealth': 'Poland', 'Second Polish Republic': 'Poland', 'Polish People\'s Republic': 'Poland', 'Swiss Confederation': 'Switzerland', 'Savoy': 'France', 'Geneva': 'Switzerland', 'Republic of Geneva': 'Switzerland', 'England': 'United Kingdom', 'Ferrara': 'Italy', 'Duchy of Ferrara': 'Italy', 'Saxe-Weimar-Eisenach': 'Germany', 'Baden': 'Germany', 'Grand Duchy of Baden': 'Germany', 'Duchy of Savoy': 'France', 'Old Swiss Confederacy': 'Switzerland'}
def country(ev):
    c = (ev or {}).get('countries') or ''
    c = c.split(',')[0].strip()
    if c.startswith('United Kingdom'): return 'United Kingdom'
    return CN.get(c, re.sub(r'^(Kingdom|Republic|Empire|Grand Duchy|Duchy) of (the )?', '', c)) or 'Country unrecorded'
ROLE = {'photography': 'photographer', 'painting': 'painter', 'design and decorative arts': 'designer and craftsman', 'sculpture': 'sculptor',
        'installation, performance and conceptual': 'artist', 'video, new media and digital': 'media artist', 'drawing and illustration': 'artist'}
ROLEKW = re.compile(r'photograph|journalist|artist|pioneer|maker|metalworker|painter|carpenter|engraver|designer|smith|potter|craftsm|weaver|jewel', re.I)
BAD = re.compile(r'now T\d|^movement |medium-defining|other movements|country group|blind test|\bQ\d{3,}|artist_placements|route resolved|excluded row|wiki:|row label|Met \d|Cooper Hewitt \d|Timeline|placements', re.I)
LROLE = {'M1-3': 'Fluxus artist', 'M1-4': 'mail artist', 'M1-5': 'Arte Povera artist', 'M1-6': 'land artist', 'M1-7': 'Actionist', 'M1-8': 'performance artist', 'M2-4': 'video artist',
         'I3-18': 'Mingei craftsman', 'I3-17': 'designer', 'J1-10': 'photographer', 'J1-11': 'humanist photographer', 'G1-49': 'Mosan goldsmith'}
CUR = [None]
def artist_gloss(r, ev):
    parts = [p.strip() for p in (r[2] or '').split(';')]
    role = next((p for p in parts if p and not BAD.search(p) and ROLEKW.search(p)), None)
    if not role:
        role = LROLE.get(CUR[0]) or ROLE.get((ev or {}).get('medium', ''), 'artist')
        if role == 'designer and craftsman': role = 'maker in the decorative arts'
    role = re.sub(r'\s*\(medium recorded as [^)]*\)', '', role)
    b = (ev or {}).get('birth')
    g = role
    if b and not re.search(r'\d{3,4}', role): g += ', b. ' + b
    c = country(ev)
    if ev and c != 'Country unrecorded' and c.lower() not in g.lower(): g += ' (' + c + ')'
    return g[:140]
def poss(r, label):
    g = r[2] or ''
    m = re.search(r'owned as (.+?) \(Possession (\w+)\)', g)
    url = re.search(r'https?://\S+', g)
    desc = g.split(' · owned as')[0].strip(' ·')
    if not desc: desc = 'the ' + label + ' tradition as a whole'
    gl = desc + (' · Possession: %s (%s)' % (m.group(1), m.group(2)) if m else '')
    return gl, ('possession ' + url.group(0)) if url else r[3]
INST = {'NMAI': 'Smithsonian National Museum of the American Indian, Washington and New York', 'CHNDM': 'Cooper Hewitt, Smithsonian Design Museum, New York',
        'SAAM': 'Smithsonian American Art Museum, Washington', 'NMAA': 'National Museum of Asian Art (Smithsonian), Washington', 'HMSG': 'Hirshhorn Museum, Washington',
        'NMAfA': 'National Museum of African Art (Smithsonian), Washington', 'Victoria and Albert Museum': 'Victoria and Albert Museum, London', 'V&A': 'Victoria and Albert Museum, London',
        'Victoria and Albert Museum (SSEA)': 'Victoria and Albert Museum, London', 'Victoria and Albert Museum (EAS)': 'Victoria and Albert Museum, London',
        'Cleveland Museum of Art': 'Cleveland Museum of Art', 'Cleveland Museum of Art (Indian and Southeast Asian Art)': 'Cleveland Museum of Art', 'Art Institute of Chicago': 'Art Institute of Chicago',
        'The Metropolitan Museum of Art': 'Metropolitan Museum of Art, New York', 'Rijksmuseum': 'Rijksmuseum, Amsterdam', 'Museum Volkenkunde': 'Museum Volkenkunde, Leiden',
        'Tropenmuseum': 'Tropenmuseum, Amsterdam', 'Wereldmuseum Rotterdam': 'Wereldmuseum Rotterdam', 'Wereldmuseum (NMVW)': 'Wereldmuseum (NMVW), Netherlands', 'Afrika Museum': 'Afrika Museum, Berg en Dal',
        'Penn Museum': 'Penn Museum, Philadelphia', 'Museum of New Zealand Te Papa Tongarewa': 'Museum of New Zealand Te Papa Tongarewa, Wellington', 'Yale University (LUX)': 'Yale University collections, New Haven',
        'Minneapolis Institute of Art': 'Minneapolis Institute of Art', '국립중앙박물관': 'National Museum of Korea, Seoul', '국립경주박물관': 'Gyeongju National Museum', '국립공주박물관': 'Gongju National Museum',
        'Private': 'Private collections', '個人': 'Private collections', 'British Museum': 'British Museum, London', 'Smithsonian National Museum of the American Indian': 'Smithsonian National Museum of the American Indian, Washington and New York',
        'Cooper Hewitt, Smithsonian Design Museum': 'Cooper Hewitt, Smithsonian Design Museum, New York', 'National Gallery of Australia': 'National Gallery of Australia, Canberra', 'National Gallery of Victoria': 'National Gallery of Victoria, Melbourne',
        '独立行政法人国立文化財機構': 'National Institutes for Cultural Heritage, Japan'}
def inst_name(x):
    x = (x or '').strip()
    if x in INST: return INST[x]
    q = re.findall(r'"([^"]+)"', x)
    if q and re.search(r'[А-Яа-я]', x): return q[-1].strip('"') if len(q) == 1 else '"'.join(q[-1:]).strip()
    return x or 'Institution unrecorded'
def clean_title(t):
    t = html.unescape(html.unescape(t or ''))
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'\s*\((Image withheld[^)]*|uncertain)\)', '', t, flags=re.I).strip(' .;,')
    t = re.sub(r'\s+', ' ', t)
    if t.isupper() and len(t) > 3: t = t[0] + t[1:].lower()
    return t
EXB = re.compile(r'Book of|\\bfrom (a|an|the)\\b.*(book|nama|manuscript|album|anthology|divan|khamsa)|Shahnam|Khamsa|Divan|Diwan|Gulistan|Bustan|Anthology', re.I)
GENERIC = re.compile(r'^(fragment|part|piece|object|sample|specimen)\b', re.I)
def descriptive(t):
    return len(re.findall(r"[\w'’-]+", t)) >= 3 and not GENERIC.search(t)
SECT = [('Cutlery and tableware', r'spoon|\bfork|ladle|\bsalts?\b|caster|cutlery|tea urn|cake basket|knife with|sugar tongs'),
        ('Lighting', r'candlestick|candle|lamp|lantern|candelabr|torch|светильник|подсвечник|лампа'),
        ('Arms and armour', r'sword|dagger|knife|blade|tachi|katana|wakizashi|tant[oō]|helmet|armou?r|shield|\bclub|kris|scabbard|sheath|\baxe|spear|\bbow\b|quiver|tumi|топор|нож|кинжал|шашк|zwaard|knots|kling|dolk'),
        ('Boxes and cases', r'\bbox|casket|\bcase\b|chest|container|coffer|inkwell|qalamdan|kogo|incense container|шкатулк|коробоч|ларец|ларчик|сундук|пудрениц|doos|tobacco'),
        ('Vessels', r'ewer|jug|basin|bowl|\bcup|beaker|vase|\bjar|bottle|\bdish|plate|tray|\bpot\b|bucket|kettle|vessel|goblet|tankard|teapot|coffee|salver|porringer|\bmug|flask|pitcher|cauldron|\bkero|tureen|caster|sugar|cream|котел|ваз|чаш|кувшин|блюд|поднос|стакан|рюмк|сахарниц|ковш|kom\b|schaal|beker'),
        ('Jewellery and ornaments', r'earring|necklace|pendant|\bring\b|bracelet|brooch|ornament|\bpin\b|pectoral|bead|labret|nose|ear spool|ear ornament|chain|buckle|bolo|concho|hairpin|comb|kanzashi|amulet|charm|armlet|anklet|tiara|diadem|crown|headdress|button|пуговиц|брош|серьг|украшен|tie |hair'),
        ('Figures and animals', r'figure|figurine|statuette|tunjo|animal|bird|goldweight|gold weight|weight|horse|deer|lion|monkey|antelope|crocodile|fish|скульпту|статуэтк|фигур'),
        ('Instruments', r'astrolabe|globe|qibla|instrument|drum|gong|koto|biwa|lute|flute|veena|vina|sarangi|taus|zither|trom'),
        ('Crosses and liturgical objects', r'cross|reliquary|icon|chalice|censer|incense burner|mosque|qur|икон|венец|крест|оклад'),
        ('Furniture and fittings', r'door|panel|screen|minbar|throne|\btable\b|chair|cabinet|stand|lectern|shelf|fountain|стол|кресл|панно|доска|mirror')]
SECT = [(a, re.compile(b, re.I)) for a, b in SECT]
CUSTOM = {
 'G1-20': ([('Kuduo, forowa and gold-dust equipment', r'kuduo|forowa|box|spoon|scale|vessel|container'), ('Geometric goldweights', r'geometric|abstract|square|rectang|spiral|cross|disc|swastika|stud')], 'Figurative goldweights'),
 'G2-2': ([('Balinese krisses', r'bali'), ('Madurese krisses', r'madura'), ('Sumatran krisses', r'sumat|aceh|atjeh|minangkabau|palembang|batak|riau'), ('Krisses of Sulawesi (Bugis and Makassar)', r'sulawesi|celebes|bugi|makass|boegi'),
          ('Krisses of Lombok and Sumbawa', r'lombok|sumbawa|bima'), ('Philippine kalis (Moro)', r'philipp|moro|mindanao|sulu|maguindanao'), ('Malay krisses', r'malay|malaka|johor|patani|kelantan|semenanjung'), ('Javanese krisses', r'jav|jawa|surakarta|solo|yogya|djokja|madjapahit')], 'Krisses of unrecorded region'),
 'I1-15': ([('Throwing clubs (i ula)', r'ula|throwing|werpknots'), ('Totokia (pineapple clubs)', r'totokia|pineapple'), ('Gunstock clubs (gata, kiakavo)', r'gata|kiakavo|gunstock'), ('Rootstock and pole clubs', r'root|pole|madrali|wortel|staff'), ('Paddle and spurred clubs', r'culacula|paddle|blad|spur|sali')], 'Other clubs'),
 'G2-3': ([('Mountings (koshirae)', r'mount|koshirae|拵|scabbard'), ('Tantō (daggers)', r'tant|短刀'), ('Katana', r'katana|^刀'), ('Ken and chokutō (straight swords)', r'^剣|ken\b|straight|大刀|直刀')], 'Tachi'),
}
JPP = [('飛鳥', 'Asuka'), ('奈良', 'Nara'), ('平安', 'Heian'), ('鎌倉', 'Kamakura'), ('南北朝', 'Nanbokuchō'), ('室町', 'Muromachi'), ('桃山', 'Momoyama'), ('安土', 'Azuchi'), ('江戸', 'Edo'), ('明治', 'Meiji'), ('時代', ' period'), ('世紀', 'th century'), ('・', ', '), ('～', '–')]
def jp(t):
    for a, b in JPP: t = t.replace(a, b)
    return t
PERNOUN = {'G2-12': 'armour', 'I2-9': 'maki-e', 'I2-10': 'lacquer'}
def section(t, code=None, x=None):
    if code in PERNOUN and x is not None:
        p = jp((x.get('cult') or '').split('|')[0].strip() or x.get('date') or '')
        for era in ['Asuka', 'Nara', 'Heian', 'Kamakura', 'Nanbokuchō', 'Muromachi', 'Momoyama', 'Azuchi', 'Edo', 'Meiji', 'Taishō', 'Shōwa']:
            if era in p or era in jp(x.get('date') or ''): return era + '-period ' + PERNOUN[code]
        return 'Undated ' + PERNOUN[code]
    if code in CUSTOM:
        for a, r in CUSTOM[code][0]:
            if re.search(r, t, re.I): return a
        return CUSTOM[code][1]
    tt = t.split(' || ')[0]
    for a, xx in SECT:
        if xx.search(tt): return a
    for a, xx in SECT:
        if xx.search(t): return a
    return 'Other objects'
def yr(x):
    try: return int(float(x))
    except: return None
# Japanese leaves catalogued by designation
DESIG = {'G2-3', 'G2-12', 'I2-9', 'I2-10'}
def works_and_collections(code, label):
    L = M.get(code, [])
    seen, objs = set(), []
    for x in L:
        if x['url'] in seen or not x['url'] or EXB.search(x['title'] or ''): continue
        seen.add(x['url']); objs.append(x)
    if not objs: return [], [], None
    cnt = collections.Counter(inst_name(x['inst']) for x in objs)
    sample = {}
    for x in objs: sample.setdefault(inst_name(x['inst']), x['url'])
    top = [(i, n) for i, n in cnt.most_common() if n >= 10 and i != 'Institution unrecorded']
    if len(top) < 3: top = [(i, n) for i, n in cnt.most_common(8) if i != 'Institution unrecorded']
    cols = [[i, COL, '%s — %d object%s in the gathered records' % (i, n, '' if n == 1 else 's'), 'r3 ' + sample[i], 0] for i, n in top]
    # works
    if code in DESIG:
        cand = [x for x in objs if 'National Treasure (Japan)' in x['desig']]
        rule = 'every gathered object designated a National Treasure of Japan'
        if len(cand) < 8:
            cand = [x for x in objs if 'National Treasure' in x['desig'] or 'Important Cultural Property' in x['desig']]
            rule = 'every gathered object designated a National Treasure or Important Cultural Property of Japan'
    else:
        cand = objs
        rule = 'every gathered object with a descriptive museum title (three or more words, bare object names excluded), one per title'
    best = {}
    for x in cand:
        t = clean_title(x['title'] or x.get('title_orig', ''))
        if not t: continue
        if code not in DESIG and not descriptive(t): continue
        k = t.lower()
        y = yr(x['db'])
        if k not in best or (y is not None and (best[k][1] is None or y < best[k][1])): best[k] = (x, y, t)
    items = sorted(best.values(), key=lambda v: (v[1] is None, v[1] or 0, v[2]))
    cap = 40
    if len(items) > cap:
        items = items[:cap]; rule += ', the %d earliest-dated' % cap
    works = []
    for x, y, t in items:
        date = clean_title(x['date']) if x['date'] else ''
        place = clean_title(x['place']) if x['place'] and not re.search(r'[А-Яа-я]', x['place']) else ''
        if place.lower() in t.lower(): place = ''
        bits = ', '.join(b for b in [place[:40], date[:40]] if b)
        gl = (bits + '; ' if bits else '') + inst_name(x['inst'])
        if 'National Treasure' in x['desig'] or 'Important Cultural' in x['desig']: gl += '; ' + x['desig'].replace(' (Japan)', '')
        works.append([t[:150], section(t + ' || ' + x['typ'][:60] + ' ' + (x['place'] or ''), code, x), jp(gl)[:140], 'r3 ' + x['url'], 0])
    return works, cols, (rule if works else None)
def landart():
    out = []
    for r in csv.DictReader(open(os.path.join(ROOT, 'data/interim/in_situ_exemplars.csv'))):
        if r['tradition'].startswith('Modern land art') and int(r['sitelinks'] or 0) >= 2 and (r['place'] or r['date']):
            place = r['place'].split('|')[0] if r['place'] else r['country']
            out.append((yr(r['date']) or 9999, [r['site'], 'Earthworks and sites', ', '.join(b for b in [place, r['country'] if r['country'] != place else '', r['date']] if b) + (' · ' + r['description'][:60] if r['description'] else ''), 'r3 https://www.wikidata.org/wiki/' + r['qid'], 0]))
    return [x for _, x in sorted(out, key=lambda v: v[0])]
GROUPMAP = {'sub-type': SUB, 'type': SUB, 'technique': SUB, 'regional form': SUB, 'style': SCH, 'pattern book': SUB, 'system': SUB, 'agency': SCH, 'group': SCH,
            'centre': CEN, 'workshop': CEN, 'Centres': CEN, 'phase': SCH, 'style phase': SCH, 'school': SCH, 'phase (1960s–1970s)': SCH,
            'maker': MAK, 'makers': MAK, 'enameller': MAK, 'goldsmith': MAK, 'Huguenot silversmith': MAK, 'silversmith': MAK, 'ébéniste': MAK, 'Artists': MAK, '': MAK,
            'representative works': 'Named works'}
def build():
    res = {'leaves': {}, 'new_leaves': [], 'moves_out': [], 'dropped': []}
    extra = collections.defaultdict(list)   # code -> rows moved in
    per = {}
    for l in inp:
        code, label = l['code'], l['label']
        ov = OV.get(code, {}); CUR[0] = code
        kinds, alias = [], list(l['alias_rows'])
        for r in l['rows']:
            name, grp, gl, src, mk = r[:5]
            ev = r[5] if len(r) > 5 else None
            o = ov.get(name)
            if name in MOVES and (mk or grp in ('Artists', 'Makers', 'maker')):
                tgt = MOVES[name]
                if tgt in CODES: extra[tgt].append([name, MAK, MOVE_GLOSS.get(name) or artist_gloss(r, ev), src, 1])
                else: res['moves_out'].append([name, code, tgt])
                continue
            if o and o[0] == 'DROP': res['dropped'].append([code, name, o[1]]); continue
            if o and o[0] == 'ALIAS': alias.append(name); continue
            if o and o[0] == 'MOVEIN': extra[o[1]].append([name, MAK, MOVE_GLOSS.get(name, ''), src, 1]); continue
            if o and o[0] == 'MOVEOUT': res['moves_out'].append([name, code, o[1]]); continue
            if o and o[0] == 'MOVE': res['moves_out'].append([name, code, MOVES[name]]); continue
            nm = o[2] if o and len(o) > 2 else name
            if src == 'possession':
                g2, s2 = poss(r, label)
                group = o[0] if o else (SUB if grp in ('', "Gathered rows (the leaf's own evidence)") else GROUPMAP.get(grp, grp))
                kinds.append([nm, group, (o[1] if o and o[1] else g2)[:200], s2, 0]); continue
            if grp.startswith('Gathered rows') and not o:
                alias.append(name); continue
            is_artist = bool(mk) or grp in ('Artists', 'Makers')
            if is_artist:
                gloss = o[1] if o and o[1] else (gl if src == 'islamic_makers' and gl else artist_gloss(r, ev))
                if src == 'islamic_makers': gloss = re.sub(r';?\s*uncertain$', ' (attribution uncertain)', gloss).replace('; not Lucknow Ahmad al-Husaini', '')
                group = o[0] if o else None
                kinds.append([nm, group, gloss, src, 1]); continue
            group = o[0] if o else GROUPMAP.get(grp, grp or SUB)
            if o and o[1]: gloss = o[1]
            else: gloss = '' if BAD.search(gl or '') or re.search(r'https?://|Met |row|evidence|\d+ of \d+|metalwork \d|enamels \d', gl or '') else gl
            ismk = 1 if group == MAK or (o and o[0] not in (SUB, SCH, CEN) and grp in ('maker', 'makers', 'enameller', 'goldsmith', 'Huguenot silversmith', 'silversmith', 'ébéniste')) else 0
            kinds.append([nm, group, gloss, src, ismk])
        per[code] = (l, kinds, alias)
    for code, (l, kinds, alias) in per.items():
        label = l['label']
        kinds += extra.get(code, [])
        kd = K.get(code, {})
        names = {k[0] for k in kinds}
        for a in kd.get('add', []):
            if a[0] in names: continue
            kinds.append([a[0], a[1], a[2], 'r3 ' + U(a[3]), a[4]])
        al = code in ARTIST_LED
        # artist grouping
        agmap = {}
        for g, ns in AG.get(code, []):
            for n in ns: agmap[n] = g
        evs = {r[0]: (r[5] if len(r) > 5 else None) for r in l['rows']}
        for k in kinds:
            if k[4] == 1 or k[1] is None:
                if k[1] in (None, MAK) and al:
                    k[1] = agmap.get(k[0]) or ADDC.get(k[0]) or (country(evs.get(k[0])) if evs.get(k[0]) else (MAK if k[1] == MAK else MAK))
                elif k[1] is None:
                    k[1] = agmap.get(k[0], MAK)
        works, cols, rule = works_and_collections(code, label)
        if code == 'M1-6':
            works = landart(); rule = None
        kn = {k[0].lower() for k in kinds}
        works = [w for w in works if w[0].lower() not in kn]
        kinds += works + cols
        # order groups
        named = [k[1] for k in kinds if k[1].startswith('Named') or k[1].startswith('Tenka') or k[1] in ('Imperial Easter eggs', 'Minbars', 'Champlevé reliquaries', 'Earthworks and sites')]
        dsec = [a for a, _ in SECT] + ['Other objects'] + [a for a, _ in CUSTOM.get(code, ([], ''))[0]] + ([CUSTOM[code][1]] if code in CUSTOM else []) + [e + '-period ' + PERNOUN.get(code, '') for e in ['Asuka', 'Nara', 'Heian', 'Kamakura', 'Nanbokuchō', 'Muromachi', 'Momoyama', 'Azuchi', 'Edo', 'Meiji', 'Taishō', 'Shōwa']] + ['Undated ' + PERNOUN.get(code, '')]
        def gkey(g):
            if g == SUB: return (0, 0)
            if g == SCH: return (1, 0)
            if g == CEN: return (2, 0)
            if al and g not in named and g not in dsec and g != COL:
                order = [x for x, _ in AG.get(code, [])]
                if g in order: return (3, order.index(g))
                if g == MAK: return (3, 999)
                return (3, 500 - sum(1 for k in kinds if k[1] == g) / 1000)
            if g in named: return (4, 0)
            if g in dsec: return (5, dsec.index(g))
            if g == COL: return (6, 0)
            if g == MAK: return (8, 0)
            return (7, 0)
        groups = []
        for k in kinds:
            if k[1] not in groups: groups.append(k[1])
        groups.sort(key=gkey)
        def ykey(k):
            m = re.search(r'b\. (\d{3,4})|(?<!\d)(\d{3,4})(?:[–-]\d{2,4})', k[2]) or re.search(r'(?<!\d)(1\d{3}|[5-9]\d{2})(?!\d)', k[2])
            return int(next(x for x in m.groups() if x)) if m else 9999
        out = []
        for g in groups:
            rows = [k for k in kinds if k[1] == g]
            if all(k[4] == 1 for k in rows): rows.sort(key=ykey)
            out += rows
        kinds = out
        # axis
        if al:
            axis = kd.get('axis') or ('artist-led: makers by country of activity (named groups first where the literature has them); named works after the makers' if not AG.get(code) else 'artist-led: makers by named circle or phase, then by country of activity')
            if rule: axis += '; works: ' + rule + ', by object type'
            if any(k[1] == COL for k in kinds): axis += '; collections ranked by gathered objects'
        else:
            parts = []
            if any(k[1] == SUB for k in kinds): parts.append('sub-types')
            if any(k[1] == SCH for k in kinds): parts.append('schools and phases')
            if any(k[1] == CEN for k in kinds): parts.append('centres and workshops')
            if any(k[1] in named for k in kinds): parts.append('named works (attested masterpieces)')
            if rule: parts.append('works: ' + rule + ', by object type then date')
            if any(k[1] == COL for k in kinds): parts.append('collections ranked by number of gathered objects (≥ 10, or the top 8)')
            if any(k[1] == MAK for k in kinds): parts.append('makers')
            axis = 'tradition-led: ' + ', then '.join(parts) if parts else ''
        ent = {'axis': axis, 'catalogues': kd.get('cats', []), 'kinds': kinds, 'alias_rows': sorted(set(alias), key=alias.index)}
        if kd.get('defn'): ent['defn'] = kd['defn']
        res['leaves'][code] = ent
    return res
if __name__ == '__main__':
    res = build()
    out = os.path.join(HERE, '..', 'result.json')
    json.dump(res, open(out, 'w'), ensure_ascii=False, indent=0)
    n = sum(len(v['kinds']) for v in res['leaves'].values())
    small = [c for c, v in res['leaves'].items() if len(v['kinds']) <= 4]
    print('kinds', n, 'moves', len(res['moves_out']), 'dropped', len(res['dropped']), 'small', len(small), small)
    print('nocats', [c for c, v in res['leaves'].items() if not v['catalogues']])
