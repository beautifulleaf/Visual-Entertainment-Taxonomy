from common import *
import csv, re
R = os.path.join(HERE, '..', '..', '..', '..', 'data', 'interim')

CARPET_CENTRES = [
    ('Sub-types', [('court carpet', 'carpets woven in royal workshops for the Safavid court, 16th–17th c.'), ('Safavid carpet', 'the classical carpets of the Safavid period, 1501–1736'),
                   ('Lechek-Turunj carpet', 'medallion-and-corner design of Tabriz and NW Iran'), ('hunting carpet', 'carpets with mounted hunters and game, a Safavid court type'),
                   ('animal carpet', 'carpets with animal combats and figures among scrolling vines'), ('Salting carpet', 'group of silk-and-metal-thread prayer and medallion carpets named after the Salting gift to the V&A'),
                   ('Polonais carpet', 'silk and metal-thread Isfahan and Kashan carpets of c. 1600, once thought Polish'), ('Four Seasons carpet', 'classical design of garden and seasons compartments'),
                   ('Herat carpet', 'the classical Khorasan carpet of Herat, with the Herati pattern'), ('mir', 'Mir (Mir-i-Bota) small-boteh field design of Saraband and Sarouk'),
                   ('Shiraki pich', 'twisting-vine design associated with Fars'), ('sofra kordi', 'Kurdish flat-woven food cloth (sofreh)')]),
    ('Centres of Iranian Azerbaijan (Tabriz, Heriz)', ['Tabriz carpet', 'Tabriz rug', 'Heriz rug', 'Gorevan carpet', 'Bakshaish rug', 'Ahar rug', 'Karadagh rug', 'Sarab carpet', 'Meshkin rug', 'Ardabil rug',
        'Ardabil carpet weaving', 'Khoi carpet', 'Azarshahr carpet', 'Sardroud carpet', 'Karaja carpet', 'Afshar carpet of Azerbaijan', 'Shahsevan rug', 'Zanjan rug']),
    ('Centres of Kurdistan and Hamadan', ['Bijar rug', 'Sanandaj rug', 'Mahabad rug', 'Bukan carpet', 'Hamadan rug', 'Enjilas carpet', 'Qazvin rug']),
    ('Centres of Arak and the west (Sarouk, Feraghan)', ['Arak rug', 'Saruq rug', 'Feraghan carpet', 'Seraband rug', 'Mushkabad rug', 'Viss carpet', 'Jozan rug', 'Borujerd rug', 'Lorestan rug']),
    ('Centres of central Iran (Kashan, Isfahan, Nain, Qom)', ['Kashan rug', 'Isfahan rug', 'Nain rug', 'Qom rug', 'Joshaghan rug', 'Varamin rug', 'Semnan rug', 'Yazd rug']),
    ('Centres of Khorasan (Mashhad, Qaen)', ['Mashhad rug', 'Khorasan carpet', 'Kashmar carpet', 'Nishapur rug', 'Qaen rug', 'Dorukhsh carpet', 'Moud rug']),
    ('Centres of Kerman and the south-east', ['Kerman carpet', 'Afshar Kerman rug', 'Afshar Sirjan rug', 'Afshar Baft rug', 'Afshar Jiroft rug']),
    ('Fars and tribal weaving (Qashqai, Bakhtiari)', ['Shiraz rug', 'Qashqai rug', 'Abadeh rug', 'Yalameh rug', 'Mamasani carpet', 'Bakhtiari', 'Shahrekord carpet', 'Afshar Khuzestan carpet']),
]
GENERIC = re.compile(r'^(carpet|rug|fragment|carpet fragment|carpet end|carpet border|carpet border fragment|carpet weight|carpet loom|prayer rug|drug jar)$', re.I)
def carpet_works():
    rows = []
    for r in csv.DictReader(open(os.path.join(R, 'regional', 'islamic_objects.csv'))):
        s = r['title'] + ' ' + r['object_type']
        if not re.search(r'carpet|rug', s, re.I):
            continue
        if not (r['dynasty'] in ('Safavid', 'Qajar', 'Timurid', 'Afsharid', 'Zand', 'Ilkhanid', 'Seljuq') or re.search('Iran|Persia', r['culture_place'])):
            continue
        rows.append(r)
    inst = collections.Counter(r['institution'] for r in rows)
    works, seen = [], set()
    for r in rows:
        t = r['title'].strip(" '")
        if GENERIC.match(t) or re.search(r'Caucasian|Karabagh|Baluch|Dervish|Dragon', t):
            continue
        key = (re.sub(r'^the ', '', t.lower()), r['institution'])
        if key in seen:
            continue
        seen.add(key)
        dt = r['date_text']
        m = re.search(r'(\d{3,4})', re.sub(r'Hegira[^/]*/|Hejira[^/]*/|AH [^/]*/', '', dt))
        y = int(m.group(1)) if m else 1800
        if re.search(r'1100s', dt): y = 1100
        if re.search(r'^1[0-9]th century', dt): y = int(dt[:2]) * 100 - 100
        per = 'Seljuq and Timurid carpets' if y < 1500 else 'Safavid carpets, 16th century' if y < 1600 else 'Safavid carpets, 17th century' if y < 1736 else 'Qajar carpets'
        works.append((y, [t if t[0].isupper() else t.capitalize(), per, f"{dt}; {r['institution']}"[:140], 'r3 ' + r['url'], 0]))
    order = ['Seljuq and Timurid carpets', 'Safavid carpets, 16th century', 'Safavid carpets, 17th century', 'Qajar carpets']
    works.sort(key=lambda x: (order.index(x[1][1]), x[0]))
    return [w for _, w in works], inst, len(rows)

def build(out):
    leaf = LEAVES['H1-1']
    names = {r[0]: r for r in leaf['rows']}
    k, used = [], set()
    for g, items in CARPET_CENTRES:
        for it in items:
            n, gl = (it if isinstance(it, tuple) else (it, ''))
            if n in ('Tabriz rug', 'Ardabil carpet weaving') and n in names:
                DROPPED.append(['H1-1', n, 'duplicate of %s' % ('Tabriz carpet' if n == 'Tabriz rug' else 'Ardabil rug')]); used.add(n); continue
            if n in names:
                k.append([n, g, gl or ('weaving centre or type, ' + g.split('(')[0].replace('Centres of ', '').strip()), names[n][3], 0]); used.add(n)
    for n, r in names.items():
        if n not in used and not is_maker(r):
            DROPPED.append(['H1-1', n, 'not placed'])
    works, inst, n = carpet_works()
    add(k, 'Named carpets (from Wikipedia)', [
        ('Pazyryk carpet', 'oldest surviving pile carpet, c. 400 BC, from a Scythian burial; possibly Achaemenid Persian; State Hermitage, St Petersburg', wp('Pazyryk carpet')),
        ('Ardabil Carpet', 'pair of Safavid medallion carpets dated 1539–40, signed Maqsud Kashani; V&A, London, and LACMA, Los Angeles', wp('Ardabil Carpet')),
        ('Chelsea Carpet', 'Safavid animal carpet, Tabriz or Kerman, c. 1500–1550; V&A, London', wp('Chelsea Carpet')),
        ('Coronation Carpet', 'Safavid silk-and-wool medallion carpet, c. 1520–30, used at Edward VII\'s coronation; LACMA, Los Angeles', wp('Coronation Carpet')),
        ('Emperor\'s Carpet', 'Safavid animal-and-tree carpet, Herat, mid-16th c.; Metropolitan Museum of Art, New York', wp("Emperor's Carpet")),
        ('Clark Sickle-Leaf carpet', 'Safavid Kerman vase-technique carpet, 17th c.; record auction price in 2013', wp('Clark Sickle-Leaf carpet')),
    ])
    k += works
    for i, (name, c) in enumerate(inst.most_common(8)):
        k.append([name, 'Collections', f'{c} Persian carpets in the gathered Islamic-object records', 'r3 ' + wp(name.split(' (')[0].split(' – ')[0]), 0])
    for r in leaf['rows']:
        if is_maker(r):
            g = 'Kerman weavers' if 'Kirmani' in r[0] else 'Safavid court workshop'
            gl = 'signatory of the Ardabil Carpet (1539–40); his role as designer or patron is debated' if 'Maqsud' in r[0] else 'master weaver of Kerman, signed carpets'
            k.append([r[0], 'Makers', gl, r[3], 1])
    out['leaves']['H1-1'] = dict(
        axis='sub-types (court and design types) first, then weaving centres by region (Azerbaijan, Kurdistan–Hamadan, Arak, central Iran, Khorasan, Kerman, Fars and the tribes); works: named carpets with Wikipedia articles, then every titled (non-generic) Persian carpet in the gathered Islamic-object records with its museum page, by period; collections ranked by gathered objects; makers last',
        catalogues=[['https://collections.vam.ac.uk/search/?q=persian%20carpet', 'V&A collections: Persian carpets', 'the largest museum holding of Persian carpets, with the Ardabil'],
                    ['https://www.metmuseum.org/art/collection/search?q=Safavid%20carpet', 'The Met collection: Safavid carpets', 'Persian carpets at the Met, including the Emperor\'s Carpet'],
                    ['https://islamicart.museumwnf.org/', 'Discover Islamic Art (Museum With No Frontiers)', 'carpets and other objects from Islamic collections across Europe and the Middle East'],
                    ['https://www.carpetmuseum.ir/', 'Carpet Museum of Iran, Tehran', 'the national collection of Persian carpets']],
        kinds=k, alias_rows=list(leaf['alias_rows']))

    # ---------------- C2-29 Gothic Book Illustration ----------------
    leaf = LEAVES['C2-29']
    SCH = {'Gothic: Parisian': ('Parisian court school (Pucelle and after)', 'Parisian'), 'Gothic: French and Northern French': ('French and Northern French', 'French'),
           'Gothic: English': ('English', 'English'), 'Gothic: Low Countries': ('Low Countries', 'Low Countries'), 'Gothic: German and Austrian': ('German and Austrian', 'German'),
           'Gothic: Bohemian': ('Bohemian (Luxembourg court)', 'Bohemian'), 'Gothic: Central European (Poland, Hungary)': ('Central European (Poland, Hungary)', 'Central European'),
           'Gothic: Italian (Bologna, Florence, Siena, Lombardy)': ('Italian (Bologna, Florence, Siena, Lombardy)', 'Italian'), 'Gothic: Iberian': ('Iberian', 'Iberian'),
           'International Gothic': ('International Gothic', 'International Gothic'), 'Bibles moralisées and illustrated Bibles': ('Bibles moralisées', 'Bible moralisée')}
    k = []
    for r in leaf['rows']:
        if r[0] in SCH:
            g = 'Sub-types' if r[0].startswith('Bibles') else 'Schools'
            gl = {'Bibles moralisées and illustrated Bibles': 'picture Bibles pairing scenes with moral commentary, Paris 13th c.', 'International Gothic': 'courtly style c. 1380–1430 (Limbourg brothers, Boucicaut Master)'}.get(r[0], 'Gothic illumination of this region, 13th–15th c.')
            k.append([SCH[r[0]][0], g, gl, r[3], 0])
    k.sort(key=lambda x: x[1] != 'Sub-types')
    add(k, 'Sub-types', [('Book of hours', 'the lay prayer book, the commonest Gothic illuminated manuscript', wp('Book of hours')),
                         ('Psalter', 'the illuminated book of psalms, chief luxury book before the book of hours', wp('Psalter')),
                         ('Grisaille', 'monochrome grey painting, the Parisian manner of Pucelle', wp('Grisaille'))])
    # works from gathered data
    rows = []
    for r in csv.DictReader(open(os.path.join(R, 'manuscripts_items.csv'))):
        t = r['tradition']
        if not (t.startswith('Gothic') or t == 'International Gothic'):
            continue
        if int(r['sitelinks'] or 0) < 1:
            continue
        if t == 'International Gothic' and r['label'] in ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'):
            continue
        rows.append(r)
    MAP = {'Gothic (style recorded)': 'French and Northern French'}
    known = [  # canonical named manuscripts with Wikipedia articles (knowledge)
        ('Psalter of Saint Louis', 'Parisian court school (Pucelle and after)', 'Paris, c. 1270; Bibliothèque nationale de France, Paris', 'Psalter of Saint Louis', 1270),
        ('Hours of Jeanne d\'Evreux (Jean Pucelle)', 'Parisian court school (Pucelle and after)', 'Paris, c. 1324–28; Metropolitan Museum of Art (The Cloisters), New York', "Hours of Jeanne d'Evreux", 1325),
        ('Belleville Breviary (Jean Pucelle)', 'Parisian court school (Pucelle and after)', 'Paris, c. 1323–26; Bibliothèque nationale de France, Paris', 'Belleville Breviary', 1324),
        ('Petites Heures of Jean de Berry', 'Parisian court school (Pucelle and after)', 'Paris, c. 1375–90; Bibliothèque nationale de France, Paris', 'Petites Heures of Jean de Berry', 1380),
        ('Grandes Heures of Jean de Berry', 'Parisian court school (Pucelle and after)', 'Paris, 1409; Bibliothèque nationale de France, Paris', 'Grandes Heures of Jean de Berry', 1409),
        ('Belles Heures of Jean de France, Duc de Berry', 'International Gothic', 'Limbourg brothers, c. 1405–09; Metropolitan Museum of Art (The Cloisters), New York', 'Belles Heures of Jean de France, Duc de Berry', 1407),
        ('Rohan Hours', 'International Gothic', 'Rohan Master, Paris or Angers, c. 1430; Bibliothèque nationale de France, Paris', 'Rohan Hours', 1430),
        ('Bedford Hours', 'International Gothic', 'Bedford Master, Paris, c. 1410–30; British Library, London', 'Bedford Hours', 1420),
        ('Morgan Bible (Maciejowski Bible)', 'French and Northern French', 'Paris, c. 1250; Morgan Library & Museum, New York', 'Morgan Bible', 1250),
        ('Douce Apocalypse', 'English', 'England, c. 1265–70; Bodleian Library, Oxford', 'Douce Apocalypse', 1268),
        ('Tickhill Psalter', 'English', 'England, c. 1310; New York Public Library', 'Tickhill Psalter', 1310),
        ('Queen Mary Psalter', 'English', 'London, c. 1310–20; British Library, London', 'Queen Mary Psalter', 1315),
        ('Gorleston Psalter', 'English', 'East Anglia, c. 1310–24; British Library, London', 'Gorleston Psalter', 1317),
        ('Ormesby Psalter', 'English', 'East Anglia, c. 1310–25; Bodleian Library, Oxford', 'Ormesby Psalter', 1318),
        ('Luttrell Psalter', 'English', 'Lincolnshire, c. 1325–40; British Library, London', 'Luttrell Psalter', 1330),
        ('Sherborne Missal', 'English', 'Sherborne Abbey, c. 1400; British Library, London', 'Sherborne Missal', 1400),
        ('Codex Manesse', 'German and Austrian', 'Zurich, c. 1300–40; Heidelberg University Library', 'Codex Manesse', 1310),
        ('Liber viaticus of Jan of Středa', 'Bohemian (Luxembourg court)', 'Prague, c. 1360; National Museum Library, Prague', 'Liber viaticus', 1360),
        ('Wenceslas Bible', 'Bohemian (Luxembourg court)', 'Prague, c. 1390–1400; Austrian National Library, Vienna', 'Wenceslas Bible', 1395),
        ('Hours of Catherine of Cleves', 'Low Countries', 'Utrecht, c. 1440; Morgan Library & Museum, New York', 'Hours of Catherine of Cleves', 1440),
        ('Chronicon Pictum', 'Central European (Poland, Hungary)', 'Buda, c. 1358–70; National Széchényi Library, Budapest', 'Chronicon Pictum', 1360),
        ('Catalan Atlas (Cresques Abraham)', 'Iberian', 'Majorca, 1375; Bibliothèque nationale de France, Paris', 'Catalan Atlas', 1375),
    ]
    have = set()
    W = []
    for r in rows:
        g = SCH.get(r['tradition'], (MAP.get(r['tradition'], 'French and Northern French'),))[0]
        lab = r['label'].replace('&#32;', '').replace('  ', ' ')
        if lab.lower() in have:
            continue
        have.add(lab.lower())
        coll = r['collections'].split(';')[0].strip()
        W.append((g, int(re.match(r'-?\d+', r['year']).group()) if re.match(r'-?\d+', r['year'] or '') else 1400,
                  [lab, g + ' manuscripts', f"{r['year']}; {coll}" if coll else r['year'], 'r3 https://www.wikidata.org/wiki/' + r['qid'], 0]))
    for n, g, gl, art, y in known:
        if n.lower() in have:
            continue
        W.append((g, y, [n, g + ' manuscripts', gl, 'r3 ' + wp(art), 0]))
    order = ['Parisian court school (Pucelle and after)', 'French and Northern French', 'English', 'Low Countries', 'German and Austrian', 'Bohemian (Luxembourg court)', 'Central European (Poland, Hungary)',
             'Italian (Bologna, Florence, Siena, Lombardy)', 'Iberian', 'International Gothic']
    W.sort(key=lambda x: (order.index(x[0]), x[1]))
    k += [w for _, _, w in W]
    c = collections.Counter()
    for r in csv.DictReader(open(os.path.join(R, 'manuscripts_items.csv'))):
        t = r['tradition']
        if t.startswith('Gothic') or t == 'International Gothic':
            for x in set(x.strip() for x in r['collections'].split(';') if x.strip()):
                c[x] += 1
    for name, n in c.most_common():
        if n < 10:
            break
        k.append([name, 'Collections', f'{n} Gothic manuscripts or leaves in the gathered records (Wikidata, much from Digital Scriptorium)', 'r3 ' + wp(name), 0])
    MG = [
        ('Parisian court illuminators', ['Jean Pucelle', 'Master of 1328', 'Anastasia', 'Pseudo-Jacquemart', 'First Master of the Bible Historiale of Jean de Berry', 'Master of the Boqueteaux',
            'Master of the Livre du Sacre', 'Bourgot', 'Master of the Berry Apocalypse', 'Master of Berry’s Cleres Femmes', 'Master of the City of Ladies', 'Virgil Master', 'Orosius Master', 'Luçon Master', 'Mazarine Master',
            'Master of the Breviary of John the Fearless', 'Master of Egerton', 'Master of the Harvard Hannibal', 'Spitz Master', 'Maître Frana']),
        ('Provincial French masters (Loire, Picardy)', ['Maître de Marguerite d\'Orléans', 'Master of the Cardinal de Bourbon', 'Rambures Master', 'Master of the Grisailles fleurdelisées']),
        ('English illuminators', ['William de Brailes', 'Herman Scheerre']),
        ('Burgundian Netherlands (Flemish) workshops', ['Jacques Daliwe', 'Master of the Champion des Dames', 'Master of Mansel', 'Master of Fitzwilliam 268', 'Master of the London Wavrin', 'Master of the Vienna and Copenhagen Toison d’Or',
            'Master of the Vraie Cronicque descoce', 'Master of the Getty Froissart', 'Master of the Vienna Chronique d\'Angleterre', 'Master of the Flemish Boethius', 'Master of Edward IV', 'Bruges Master of 1482',
            'Master of the Moral Treatises', 'Master of the Houghton Miniatures', 'Colard Mansion', 'Richard of Verdun']),
        ('Italian illuminators', ['Maria Ormani']),
        ('Central European illuminators', ['Márk Kálti']),
        ('Iberian illuminators and cartographers', ['Cresques Abraham']),
        ('Eastern Christian illuminators in the data', ['Toros Roslin', 'Mikael Modrekili']),
    ]
    MV = {'Vigila': 'C2-23', 'Ende': 'C2-23', 'Folchardus': 'C2-20', 'Bartolomeo Sanvito': 'C2-25', 'Cristoforo de Predis': 'C2-25'}
    gl = {}
    for r in leaf['rows']:
        b = ev(r).get('birth', '')
        if b:
            gl[r[0]] = 'active c. %s' % b if not b.startswith('-') else ''
    GD = {'Parisian court illuminators': 'Gothic illuminator active in Paris', 'Provincial French masters (Loire, Picardy)': 'Gothic illuminator of provincial France',
          'English illuminators': 'Gothic illuminator active in England', 'Burgundian Netherlands (Flemish) workshops': 'illuminator of the Burgundian Netherlands, 15th c.',
          'Italian illuminators': 'Florentine illuminator-scribe, 15th c.', 'Central European illuminators': 'Hungarian illuminator of the Chronicon Pictum, 14th c.',
          'Iberian illuminators and cartographers': 'Majorcan cartographer-illuminator of the Catalan Atlas, 1375', 'Eastern Christian illuminators in the data': 'illuminator of the Armenian or Georgian tradition'}
    mk = assign(leaf, MG, MV)
    for x in mk:
        x[2] = GD.get(x[1], x[2])
    k += mk
    out['leaves']['C2-29'] = dict(
        axis='sub-types, then regional schools; works: every named Gothic manuscript in the gathered manuscript records with a Wikipedia article (sitelinks >= 1; calendar leaves merged into their book), plus canonical named manuscripts with Wikipedia articles from the literature, by school then date; collections ranked by gathered items; illuminators by school (Paris court, provincial France, England, Burgundian Netherlands, Italy, Central Europe, Iberia)',
        catalogues=[['https://www.bl.uk/manuscripts/', 'British Library: Digitised Manuscripts', 'the BL\'s fully digitised Gothic psalters, Apocalypses and books of hours'],
                    ['https://gallica.bnf.fr/services/engine/search/sru?operation=searchRetrieve&query=%28gallica%20all%20%22enluminure%22%29', 'Gallica (BnF): illuminated manuscripts', 'the Bibliothèque nationale de France\'s digitised manuscripts'],
                    ['https://digital.bodleian.ox.ac.uk/', 'Digital Bodleian', 'Oxford\'s digitised manuscripts, including the Douce Apocalypse'],
                    ['https://www.digital-scriptorium.org/', 'Digital Scriptorium', 'union catalogue of medieval manuscripts in American collections'],
                    ['https://www.getty.edu/art/collection/search?q=manuscript', 'Getty Museum: manuscripts', 'the Getty\'s collection of illuminated manuscripts and leaves']],
        kinds=k)
