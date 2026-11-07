import json, re, math, collections
IN = json.load(open('../../va_in/bucket_academic_19c.json'))['leaves']
CODES = {l['code'] for l in IN}
RENAME = {
    'Academia Imperial de Belas Artes (Brazil)': 'Imperial Academy of Fine Arts (Brazil)',
    'Weimar Saxon-Grand Ducal Art School': 'Grand-Ducal Saxon Art School, Weimar',
    'Art of the American Old West': 'Western American Art',
    'Nagybánya artists\' colony': "Nagybánya artists' colony",
}
MAP = {}
for line in open('map.tsv', encoding='utf-8'):
    line = line.rstrip('\n')
    if not line.strip():
        continue
    n, t = line.split('\t')
    MAP[n] = t

# ---------------- country normalisation ----------------
SPECIFIC = [
    ('Poland', ['Poland', 'Congress Poland', 'Second Polish Republic', 'Duchy of Warsaw', 'Free City of Kraków', 'Kingdom of Galicia and Lodomeria', 'Polish–Lithuanian Commonwealth']),
    ('Hungary', ['Hungary', 'Kingdom of Hungary']),
    ('Czech lands', ['Czech Republic', 'Czechoslovakia', 'Kingdom of Bohemia', 'Slovakia']),
    ('Finland', ['Finland', 'Grand Duchy of Finland']),
    ('Baltic provinces', ['Estonia', 'Latvia', 'Lithuania']),
    ('Georgia, Armenia and Azerbaijan', ['Georgia', 'Azerbaijan Democratic Republic', 'Qajar Iran']),
    ('Ukraine', ['Ukraine', 'Ukrainian Soviet Socialist Republic']),
    ('South Slavic lands', ['Serbia', 'Principality of Serbia', 'Kingdom of Serbs', 'Kingdom of Yugoslavia', "Federal People's Republic of Yugoslavia", 'Socialist Federal Republic of Yugoslavia', 'Croatia', 'Slovenia', 'Bulgaria', 'Principality of Bulgaria']),
    ('Romania', ['Romania', 'Kingdom of Romania', 'Principality of Wallachia', 'Principality of Moldavia']),
    ('Greece', ['Greece', 'Kingdom of Greece']),
    ('Norway', ['Norway']),
    ('Ireland', ['Ireland', 'Kingdom of Ireland']),
    ('Switzerland', ['Switzerland', 'Republic of Geneva', 'Three Leagues']),
    ('Belgium', ['Belgium', 'Southern Netherlands', 'Austrian Netherlands', 'Habsburg Netherlands']),
]
GENERAL = [
    ('France', ['France', 'Kingdom of France', 'Monaco']),
    ('United Kingdom', ['United Kingdom', 'United Kingdom of Great Britain and Ireland', 'Kingdom of Great Britain', 'England', 'Scotland', 'Cornwall', 'British Empire']),
    ('Germany', ['Germany', 'German Empire', 'German Reich', 'Kingdom of Prussia', 'Kingdom of Bavaria', 'Kingdom of Saxony', 'Kingdom of Württemberg', 'Kingdom of Hanover', 'Grand Duchy of Baden', 'Grand Duchy of Hesse', 'Grand Duchy of Oldenburg', 'Grand Duchy of Mecklenburg-Strelitz', 'Grand Duchy of Mecklenburg-Schwerin', 'Hamburg', 'Bremen', 'Lübeck', 'Anhalt', 'Anhalt-Dessau', 'Anhalt-Köthen', 'Duchy of Anhalt', 'Duchy of Brunswick', 'Duchy of Saxe-Weimar-Eisenach', 'Duchy of Saxe-Coburg and Gotha', 'Duchy of Saxe-Meiningen', 'Duchy of Holstein', 'Duchy of Schleswig', 'Principality of Waldeck', 'Principality of Reuss-Gera', 'Electorate of Hesse', 'Landgraviate of Hesse-Kassel', 'Electoral Palatinate', 'Free City of Frankfurt', 'North German Confederation', 'Confederation of the Rhine', 'Holy Roman Empire', 'Duchy of Württemberg', 'German Confederation', 'Weimar Republic', 'Swedish Pomerania', 'Nazi Germany']),
    ('Austria', ['Austria', 'Austrian Empire', 'Austria–Hungary', 'Cisleithania', 'Habsburg monarchy', 'Archduchy of Austria below the Enns', 'Prince-Bishopric of Trent']),
    ('Italy', ['Italy', 'Kingdom of Italy', 'Papal States', 'Republic of Venice', 'Grand Duchy of Tuscany', 'Kingdom of Sardinia', 'Kingdom of the Two Sicilies', 'Duchy of Milan', 'Duchy of Parma and Piacenza', 'Kingdom of Lombardy–Venetia', 'Duchy of Florence', 'Crown Colony of Malta', 'Malta']),
    ('Netherlands', ['Kingdom of the Netherlands', 'Dutch Republic', 'United Kingdom of the Netherlands']),
    ('Spain', ['Spain']),
    ('Portugal', ['Portugal', 'Kingdom of Portugal']),
    ('Denmark', ['Kingdom of Denmark']),
    ('Sweden', ['Sweden']),
    ('Russia', ['Russian Empire', 'Soviet Union', 'Russia', 'Russian Republic', 'Russian Soviet Federative Socialist Republic', 'Russian Socialist Federative Soviet Republic']),
    ('Ottoman Empire', ['Ottoman Empire', 'Turkey', 'Lebanon', 'Albania', 'Kingdom of Iraq']),
    ('United States', ['United States', 'Thirteen Colonies']),
    ('Canada', ['Canada']),
    ('Mexico', ['Mexico', 'New Spain']),
    ('Brazil', ['Brazil']),
    ('Australia', ['Australia', 'Colony of New South Wales']),
    ('New Zealand', ['New Zealand', 'Colony of New Zealand']),
]
REGION = {
    'Argentina': 'Latin America', 'Chile': 'Latin America', 'Peru': 'Latin America', 'Viceroyalty of Peru': 'Latin America', 'Colombia': 'Latin America',
    'Venezuela': 'Latin America', 'Uruguay': 'Latin America', 'Cuba': 'Latin America', 'Ecuador': 'Latin America', 'Federal Republic of Central America': 'Latin America',
    'Guatemala': 'Latin America', 'Trinidad and Tobago': 'Latin America', 'Philippines': 'Asia and Africa', 'British Raj': 'Asia and Africa', 'Kingdom of Thiruvithamkoor': 'Asia and Africa',
    'Dutch East Indies': 'Asia and Africa', 'Japan': 'Asia and Africa', 'Qing dynasty': 'Asia and Africa', 'South Africa': 'Asia and Africa', 'Cameroon': 'Asia and Africa', 'Nigeria': 'Asia and Africa',
    'Israel': 'Asia and Africa', 'Vietnam': 'Asia and Africa', 'Dominion of India': 'Asia and Africa', 'India': 'Asia and Africa',
}
OVR = {}
for n in ['Antonín Mánes', 'Josef Mánes', 'Quido Mánes', 'Amalie Mánesová', 'Karel Svoboda', 'Josef Matyáš Trenkwald', 'Adolf Kosárek', 'Jaroslav Čermák', 'Karel Purkyně', 'Karel Klíč', 'Hermína Laukotová', 'Václav Sochor', 'Zdenka Braunerová', 'Jaroslav Věšín', 'Jakub Husník', 'Václav Jansa', 'Hanuš Schwaiger', 'Emanuel Max', 'Václav Levý', 'Josef Navrátil', 'Antonín Langweil', 'František Tkadlík', 'Antonín Machek', 'Karel Hynek Mácha', 'Bohuslav Schnirch', 'Josef Václav Myslbek', 'Ludwig Kohl', 'Antonín Chittussi', 'Felix Jenewein', 'Julius Mařák', 'Alois Delug', 'Jakub Obrovský', 'František Rint', 'Emanuel Krescenc Liška', 'Ivan Mrkvička', 'Josef Fanta', 'Maximilian Pirner', 'Soběslav Pinkas', 'Peter Michal Bohúň', 'Döme Skuteczky', 'Karl Kaufmann', 'Johann Kautsky', 'Albert Schindler', 'Joseph von Führich']:
    OVR[n] = 'Czech lands'
for n in ['Henryk Rodakowski', 'Artur Grottger', 'Juliusz Kossak', 'Teodor Talowski', 'Tadeusz Barącz', 'Franciszek Wyspiański', 'Teodora Matejko', 'Bronislaw Abramowicz', 'Jan Matejko', 'Aleksander Kotsis', 'Aleksander Gryglewski', 'Andrzej Grabowski', 'Zofia Szeptycka', 'Piotr Stachiewicz', 'Leon Kapliński', 'Józef Szermentowski', 'Feliks Sypniewski', 'Leonard Marconi', 'Wincenty Sleńdziński', 'Józef Chełmoński', 'Teofil Lenartowicz', 'Jan Wnęk', 'Wiktor Brodzki', 'Tomasz Oskar Sosnowski', 'Kazimierz Jelski', 'Jakub Tatarkiewicz', 'Walenty Wańkowicz', 'Kanuty Rusiecki', 'Napoleon Orda', 'Józef Ignacy Kraszewski', 'January Suchodolski', 'Jan Ksawery Kaniewski', 'Kazimierz Alchimowicz', 'Michał Elwiro Andriolli', 'Samuel Hirszenberg', 'Maurycy Trębacz', 'Stanisław Grocholski', 'Tadeusz Ajdukiewicz', 'Zygmunt Ajdukiewicz']:
    OVR[n] = 'Poland'
for n in ['Izidor Kršnjavi', 'Mato Celestin Medović', 'Ivan Rendić', 'Mihael Stroj', 'Ivana Kobilca', 'Stevan Todorović', 'Mina Karadžić', 'Giuseppe Tominz', 'Novak Radonić']:
    OVR[n] = 'South Slavic lands'
for n in ['Mișu Popp', 'Constantin Daniel Rosenthal', 'Constantin Lecca', 'Karl Storck']:
    OVR[n] = 'Romania'
for n in ['Taras Shevchenko', 'Ivan Soshenko', 'Serhii Vasylkivsky', 'Serhiy Svetoslavsky', 'Opanas Slastion', 'Wilhelm Kotarbiński', 'Eliza Krasińska', 'Vladimir Orlovsky', 'Nikolay Gritsenko']:
    OVR[n] = 'Ukraine'
for n in ['Hakob Mkrtum Hovnatanyan', 'Gevorg Bashinjaghian', 'Mirza Gadim Iravani', 'Mir Mohsun Navvab', 'Nino Chavchavadze', 'Gigo Gabashvili', 'Kosta Khetagurov']:
    OVR[n] = 'Georgia, Armenia and Azerbaijan'
for n in ['Johann Köler', 'Julie Wilhelmine Hagen-Schwarz', 'Carl Timoleon von Neff', 'August Matthias Hagen', 'Gustav Adolf Hippius', 'Otto Friedrich Theodor von Möller', 'Ernst von Liphart', 'Paul Raud', 'Johann Walter-Kurau', 'Yehuda Pen', 'August Weizenberg', 'Amandus Adamson', 'Eduard Hau', 'Woldemar Hau', 'Karl Gottlieb Wenig', 'Julius Fedders']:
    OVR[n] = 'Baltic provinces'
for n in ['Caspar David Friedrich', 'Philipp Otto Runge', 'Theude Grønland', 'Louise of Hesse-Kassel', 'Carl Wilhelm von Heideck', 'Ludwig Thiersch']:
    OVR[n] = 'Germany'
for n in ['Fyodor Bruni', 'Alexander Brullov', 'Karl Bryullov']:
    OVR[n] = 'Russia'
for n in ['Elisabeth Baumann', 'Bertha Wegmann', 'Geskel Saloman']:
    OVR[n] = 'Denmark'
for n in ['Federico de Madrazo y Kuntz', 'Raimundo de Madrazo y Garreta', 'Carlos Luis de Ribera y Fieve', 'Ramón Tusquets Maignon']:
    OVR[n] = 'Spain'
for n in ['Charles Gleyre', 'Jean Victor Schnetz', 'Karl Girardet', 'Henri Lehmann', 'Ary Scheffer', 'Hendrik Scheffer', 'Rodolphe Töpffer']:
    OVR[n] = 'France'
for n in ['Frans Vervloet', 'Antonie Sminck Pitloo']:
    OVR[n] = 'Italy'
for n in ['Louis Buvelot', 'Eugene von Guerard']:
    OVR[n] = 'Australia'
for n in ['John James Audubon', 'Emanuel Leutze', 'Severin Roesen', 'Charles Dellschau']:
    OVR[n] = 'United States'


def country(name, cstr):
    if name in OVR:
        return OVR[name]
    cs = [c.strip() for c in (cstr or '').split(',') if c.strip()]
    for lab, keys in SPECIFIC:
        if any(c in keys for c in cs):
            if lab == 'Belgium' and cs and cs[0] in ('France',) and len(cs) > 1:
                continue
            return lab
    for c in cs:
        for lab, keys in GENERAL:
            if c in keys:
                return lab
        if c in REGION:
            return REGION[c]
    return 'Other'


def gloss_for(r):
    e = r[5] if len(r) > 5 else {}
    med = e.get('medium', '')
    who = {'painting': 'Painter', 'sculpture': 'Sculptor'}.get(med, 'Artist')
    cs = []
    for c in (e.get('countries') or '').split(','):
        c = c.strip()
        if c and c not in cs:
            cs.append(c)
    s = who
    if e.get('birth'):
        s += ', b. ' + e['birth']
    if cs:
        s += '; ' + ', '.join(cs[:3])
    return s[:140]

# ---------------- collect placements ----------------
leaf_rows = collections.defaultdict(list)   # code -> list of (group or None, row)
new_rows = collections.defaultdict(list)    # newkey -> list of (group or None, row, fromcode)
moves, dropped = [], []
for l in IN:
    code = l['code']
    for r in l['rows']:
        name = r[0]
        maker = bool(r[4]) or r[1] in ('Artists', 'Architects', 'Makers')
        if not maker:
            if name.startswith('rock relief'):
                leaf_rows[code].append(('Rock-cut monuments', ['Lion of the Bavarians (Nafplio, 1836–1841)', 'Rock-cut monuments', 'Rock-cut lion commemorating Bavarian soldiers of King Otto who died at Nafplio, Greece, 1833–34', r[3], 0], None))
            continue
        if not name:
            moves.append(['', code, 'A5-111'])
            continue
        t = MAP.get(name)
        grp0 = r[1] if r[1] not in ('Artists', 'Makers', 'Architects', '') else None
        row = [name, None, gloss_for(r), r[3], 1]
        if t is None:
            leaf_rows[code].append((grp0, row, r))
        elif t.startswith('G:'):
            leaf_rows[code].append((t[2:], row, r))
        elif t.startswith('NEW:'):
            new_rows[t[4:]].append((None, row, r))
        elif t.startswith('X:'):
            parts = t.split(':')
            tc = parts[1]
            g = parts[2] if len(parts) > 2 else None
            if tc == code:
                leaf_rows[code].append((g or grp0, row, r))
            else:
                leaf_rows[tc].append((g, row, r))
        else:
            if t in CODES:
                leaf_rows[t].append((None, row, r))
            else:
                moves.append([name, code, t])


def birth(raw):
    try:
        return int((raw[5] if raw and len(raw) > 5 else {}).get('birth') or 0)
    except Exception:
        return 0

COUNTRY_ORDER = ['France', 'United Kingdom', 'Ireland', 'Germany', 'Austria', 'Italy', 'Belgium', 'Netherlands', 'Spain', 'Portugal', 'Switzerland',
                 'Denmark', 'Norway', 'Sweden', 'Finland', 'Russia', 'Baltic provinces', 'Ukraine', 'Poland', 'Czech lands', 'Hungary', 'South Slavic lands',
                 'Romania', 'Greece', 'Ottoman Empire', 'Georgia, Armenia and Azerbaijan', 'United States', 'Canada', 'Mexico', 'Brazil', 'Latin America',
                 'Australia', 'New Zealand', 'Asia and Africa', 'Other']


def finish(code, items, named_order, axis_named, cap=150, minsize=3, gen_label='born'):
    """items: list of (group or None, row, raw). Returns kinds list and axis."""
    named = collections.OrderedDict((g, []) for g in named_order)
    bycountry = collections.defaultdict(list)
    for g, row, raw in items:
        g = RENAME.get(g, g) if g else g
        if g:
            named.setdefault(g, []).append((row, raw))
        else:
            e = raw[5] if raw and len(raw) > 5 else {}
            bycountry[country(row[0], e.get('countries'))].append((row, raw))
    # merge tiny country groups into regional buckets
    out_groups = []
    for g, lst in named.items():
        if lst:
            out_groups.append((g, lst))
    small = []
    ordered = sorted(bycountry, key=lambda c: (COUNTRY_ORDER.index(c) if c in COUNTRY_ORDER else 99))
    merged = collections.OrderedDict()
    for c in ordered:
        lst = bycountry[c]
        if len(lst) < minsize and c not in ('Other',):
            region = {'Ireland': 'Other Europe', 'Portugal': 'Other Europe', 'Switzerland': 'Other Europe', 'Greece': 'Other Europe', 'Romania': 'Other Europe',
                      'South Slavic lands': 'Other Europe', 'Baltic provinces': 'Other Europe', 'Ukraine': 'Other Europe', 'Czech lands': 'Other Europe', 'Hungary': 'Other Europe',
                      'Poland': 'Other Europe', 'Finland': 'Other Europe', 'Norway': 'Other Europe', 'Sweden': 'Other Europe', 'Denmark': 'Other Europe', 'Netherlands': 'Other Europe',
                      'Belgium': 'Other Europe', 'Spain': 'Other Europe', 'Italy': 'Other Europe', 'Austria': 'Other Europe', 'Germany': 'Other Europe', 'France': 'Other Europe',
                      'United Kingdom': 'Other Europe', 'Russia': 'Other Europe', 'Ottoman Empire': 'Asia and Africa', 'Georgia, Armenia and Azerbaijan': 'Asia and Africa',
                      'United States': 'Americas', 'Canada': 'Americas', 'Mexico': 'Americas', 'Brazil': 'Americas', 'Latin America': 'Americas',
                      'Australia': 'Oceania', 'New Zealand': 'Oceania', 'Asia and Africa': 'Asia and Africa'}.get(c, 'Other')
            merged.setdefault(region, []).extend(lst)
        else:
            merged.setdefault(c, []).extend(lst)
    # keep Americas/Oceania/Other Europe at end in order
    tail = [k for k in ('Other Europe', 'Americas', 'Oceania', 'Asia and Africa', 'Other') if k in merged]
    main = [k for k in merged if k not in tail]
    for c in main + tail:
        lst = sorted(merged[c], key=lambda x: (birth(x[1]) or 9999, x[0][0]))
        if len(lst) > cap:
            k = math.ceil(len(lst) / cap)
            size = math.ceil(len(lst) / k)
            chunks, cur = [], []
            for x in lst:
                if len(cur) >= size and birth(x[1]) != birth(cur[-1][1]) and len(chunks) < k - 1:
                    chunks.append(cur); cur = []
                cur.append(x)
            chunks.append(cur)
            for j, chunk in enumerate(chunks):
                b0, b1 = birth(chunk[0][1]), birth(chunk[-1][1])
                lab = f'{c}, born before {birth(chunks[1][0][1])}' if j == 0 else (f'{c}, born {b0} and later' if j == len(chunks) - 1 else f'{c}, born {b0}–{b1}')
                out_groups.append((lab, chunk))
        else:
            out_groups.append((c, lst))
    # pool tiny regional tails
    TAILS = ('Other Europe', 'Americas', 'Oceania', 'Asia and Africa', 'Other')
    tails = [x for x in out_groups if x[0] in TAILS]
    if any(len(x[1]) < 3 for x in tails):
        out_groups = [x for x in out_groups if x[0] not in TAILS]
        allp = [y for x in tails for y in x[1]]
        out_groups.append(('Other regions', sorted(allp, key=lambda x: (birth(x[1]) or 9999, x[0][0]))))
    kinds = []
    for g, lst in out_groups:
        lst = sorted(lst, key=lambda x: (birth(x[1]) or 9999, x[0][0])) if not g.startswith(tuple(COUNTRY_ORDER)) else lst
        for row, raw in lst:
            r = list(row)
            r[1] = g
            kinds.append(r)
    axis = axis_named + ' Then the remaining artists by country of activity (historic states folded into present-day countries; groups over 150 split by birth year; countries with fewer than 3 artists pooled by region), each group ordered by birth year.'
    return kinds

W = 'https://en.wikipedia.org/wiki/'
WA = 'https://www.wikiart.org/en/artists-by-art-movement/'
CFG = {
 'A5-38': (['Lyon School', "École d'Écouen", 'Victorian classicism', 'The Clique', "St John's Wood Clique", 'Fairy painting', 'Grand-Ducal Saxon Art School, Weimar', 'Biedermeier',
            'Tervuren School', 'Generation of the National Theatre', 'Tinerimea artistică and the Official Salon (Romania)', 'American Renaissance', 'Western American Art',
            'Academy of San Carlos (Mexico)', 'Imperial Academy of Fine Arts (Brazil)'],
           'by named academy, school or circle first (Écouen, Victorian classicism, The Clique, St John\'s Wood Clique, fairy painting, Weimar, Tervuren, Generation of the National Theatre, Romanian Official Salon, American Renaissance, Western American Art, San Carlos, Imperial Academy of Brazil); Salon painters already in named school leaves (Munich, Düsseldorf, Hague, Barbizon, Neo-Grec, Orientalism...) moved out.',
           [['https://salons.musee-orsay.fr/', 'Base Salons (Musée d\'Orsay)', 'every work exhibited at the Paris Salons, 1673–1914'],
            [WA + 'academicism', 'WikiArt: Academicism', 'artists and works tagged Academicism'],
            ['https://www.pop.culture.gouv.fr/', 'POP – Joconde', 'French national catalogue of museum collections'],
            ['https://commons.wikimedia.org/wiki/Category:Academic_art', 'Wikimedia Commons: Academic art', 'images of academic paintings by artist and museum']]),
 'D5-115': (['French Romantic sculpture', 'Berlin school of sculpture', 'American Renaissance', 'White Marmorean Flock'],
            'by named school or circle first (French Romantic sculptors, Berlin school of sculpture, American Renaissance, the White Marmorean Flock of American women sculptors in Rome); animaliers, New Sculpture and architects moved out.',
            [['https://sculpture.gla.ac.uk/', 'Mapping Sculpture 1851–1951', 'sculptors, works and firms in Britain and Ireland'],
             ['https://www.pop.culture.gouv.fr/', 'POP – Joconde', 'French national catalogue of museum collections, incl. Salon sculpture'],
             ['https://salons.musee-orsay.fr/', 'Base Salons (Musée d\'Orsay)', 'every sculpture shown at the Paris Salons, 1673–1914']]),
 'A5-31': (['Troubadour style', 'Juste milieu', 'German Romanticism', 'Biedermeier', 'The Ancients', 'Bristol School', 'Society of Painters in Water Colours', 'Norwegian romantic nationalism',
            'School of Posillipo', 'Scapigliatura', 'Venetsianov school', 'Western American Art'],
           'by named circle or national school first (Troubadour style, juste milieu, German Romanticism, Biedermeier, the Ancients, Bristol School, Society of Painters in Water Colours, Norwegian romantic nationalism, School of Posillipo, Scapigliatura, Venetsianov school, Western American Art); Nazarenes, Düsseldorf, Danish Golden Age, Norwich, Hudson River, Luminism, Lyon and Orientalist painters moved to their own leaves.',
           [[WA + 'romanticism', 'WikiArt: Romanticism', 'artists and works tagged Romanticism'],
            ['https://www.tate.org.uk/search?q=romanticism', 'Tate collection search', 'British Romantic painting incl. the Turner Bequest'],
            ['https://collections.louvre.fr/en/', 'Louvre collections', 'complete online catalogue of the Louvre, incl. French Romantic painting'],
            ['https://commons.wikimedia.org/wiki/Category:Romanticism', 'Wikimedia Commons: Romanticism', 'images of Romantic works by artist']]),
 'A5-30': (['Atelier of Jacques-Louis David', 'Ingres and his pupils', 'Troubadour style', 'Deutschrömer', 'Society of Painters in Water Colours', 'Peale family'],
           'by atelier or circle first (David\'s atelier, Ingres and his pupils, the Troubadour painters, the Deutschrömer in Rome, the founders of the Society of Painters in Water Colours, the Peale family); sculptors and architects moved to Neoclassical Sculpture and Neoclassical Architecture.',
           [[WA + 'neoclassicism', 'WikiArt: Neoclassicism', 'artists and works tagged Neoclassicism'],
            ['https://collections.louvre.fr/en/', 'Louvre collections', 'complete online catalogue, incl. David and his school'],
            ['https://commons.wikimedia.org/wiki/Category:Neoclassical_paintings', 'Wikimedia Commons: Neoclassical paintings', 'images of Neoclassical paintings']]),
 'D5-114': (['Canova and his school', 'Thorvaldsen and his workshop', 'Berlin school of sculpture'],
            'by workshop or school first (Canova and his school, Thorvaldsen and his workshop, Berlin school of sculpture); then a works section (rock-cut monuments).',
            [['https://www.museocanova.it/', 'Museo Gypsotheca Antonio Canova', 'Canova\'s plaster models and studio collection, Possagno'],
             ['https://www.thorvaldsensmuseum.dk/', 'Thorvaldsens Museum', 'Thorvaldsen\'s works and collections, Copenhagen'],
             ['https://commons.wikimedia.org/wiki/Category:Neoclassical_sculptures', 'Wikimedia Commons: Neoclassical sculptures', 'images of Neoclassical sculpture by sculptor']]),
 'A5-40': (["École d'Écouen", 'Volcano School', 'Molse School', 'Verismo (painting)'],
           'by named school or colony first (École d\'Écouen, Volcano School, Molse School, Verismo); Peredvizhniki moved to their own leaf, Soviet painters to Socialist Realism and 20th-century realists to their movements.',
           [[WA + 'realism', 'WikiArt: Realism', 'artists and works tagged Realism'],
            ['https://www.pop.culture.gouv.fr/', 'POP – Joconde', 'French national catalogue of museum collections'],
            ['https://www.tretyakovgallery.ru/en/collection/', 'Tretyakov Gallery collection', 'Russian realist painting']]),
 'A5-45': (['Grupo do Leão', 'Cranbrook Colony', 'Idyllic school', 'École de Concarneau', 'Étaples art colony', 'Wissant school', 'Nagybánya artists\' colony', 'École de Murol'],
           'by artists\' colony or group first (Grupo do Leão, Cranbrook Colony, Idyllic school, Concarneau, Étaples, Wissant, Nagybánya); Newlyn and Skagen painters moved to their own leaves.',
           [[WA + 'naturalism', 'WikiArt: Naturalism', 'artists and works tagged Naturalism'],
            ['https://www.pop.culture.gouv.fr/', 'POP – Joconde', 'French national catalogue of museum collections']]),
}
RENAME.update({'Society of Painters in Tempera': None, 'École de Murol': None, 'Official Salon (Romania)': 'Tinerimea artistică and the Official Salon (Romania)', 'Verismo': 'Verismo (painting)', 'Kalmthout School': None,
               'American realism': None, 'Kristiania Bohème': None, 'Skagen Painters': None, 'Newlyn School': None, 'Nagybánya art colony': "Nagybánya artists' colony",
               'Wissant school': 'Wissant school'})

out = {'leaves': {}, 'new_leaves': [], 'moves_out': moves, 'dropped': dropped}
for l in IN:
    code = l['code']
    named, axis, cats = CFG[code]
    items = []
    for g, row, raw in leaf_rows[code]:
        if g in RENAME:
            g = RENAME[g]
        items.append((g, row, raw))
    kinds = finish(code, items, named, axis)
    out['leaves'][code] = {'axis': axis + ' Then the remaining artists by country of activity (historic states folded into present-day countries, Czech, Polish, South Slavic and Baltic artists of the empires listed separately; groups over 150 split by birth year; countries with fewer than 3 artists pooled by region); each group ordered by birth year.',
                           'catalogues': cats, 'kinds': kinds, 'alias_rows': []}

def nk(name, group, gloss, url):
    return [name, group, gloss, 'r3 ' + url, 1]

NEWDEF = {
 'Orientalism': dict(breadth='broad', defn='Western painting of North Africa, the Ottoman lands, the Middle East and India, c. 1780–1914, from travel sketches to Salon harem and street scenes: <i>Delacroix\'s Women of Algiers</i>, <i>Gérôme\'s The Snake Charmer</i>, <i>Lewis\'s The Hhareem</i>. Membership: painters known chiefly for such subjects (or tagged Orientalist in Wikidata) whom no narrower school claims.',
                     aliases='Orientalist painting;Orientalist art', see='T40 Academic Art;T33 Romanticism', src=[[W + 'Orientalism', 'Wikipedia'], [W + 'List_of_Orientalist_artists', 'Wikipedia list']],
                     cats=[[W + 'List_of_Orientalist_artists', 'Wikipedia: List of Orientalist artists', 'Orientalist painters by country'], [WA + 'orientalism', 'WikiArt: Orientalism', 'artists and works tagged Orientalism'],
                           ['https://www.metmuseum.org/art/collection/search?q=Orientalism', 'The Met collection search', 'Orientalist paintings and works on paper'], ['https://commons.wikimedia.org/wiki/Category:Orientalist_paintings', 'Wikimedia Commons: Orientalist paintings', 'images by artist and subject']],
                     named=[], axis='by country of activity of the painter (France first, then Britain, Italy, Spain, Germany and Austria, Belgium and the Netherlands, eastern Europe, the Americas and the Ottoman world); each group ordered by birth year.'),
 'Peredvizhniki': dict(breadth='medium', defn='The Russian realist artists\' cooperative (Society for Travelling Art Exhibitions, 1870–1923) that toured exhibitions of national genre, history and landscape painting: <i>Repin\'s Barge Haulers on the Volga</i>, <i>Savrasov\'s The Rooks Have Come Back</i>, <i>Surikov\'s Boyarynya Morozova</i>. Membership: members or regular exhibitors of the Society.',
                     aliases='Wanderers;Itinerants;Society for Travelling Art Exhibitions', see='T42 Realism', src=[[W + 'Peredvizhniki', 'Wikipedia']],
                     cats=[['https://www.tretyakovgallery.ru/en/collection/', 'Tretyakov Gallery collection', 'the main collection of Peredvizhniki painting, Moscow'], ['https://rusmuseumvrm.ru/', 'Russian Museum virtual branch', 'collection of the State Russian Museum, St Petersburg'],
                           ['https://commons.wikimedia.org/wiki/Category:Peredvizhniki', 'Wikimedia Commons: Peredvizhniki', 'images of works by members']],
                     named=['Founding generation (born before 1840)', 'Second generation (born 1840–1854)', 'Younger members (born 1855 and later)'],
                     axis='by generation of membership: founding generation of 1870 (born before 1840), second generation (born 1840–1854), younger members (born 1855 and later); each group ordered by birth year.'),
 'Skagen Painters': dict(breadth='narrow', defn='The Scandinavian artists\' colony at Skagen in northern Jutland, c. 1875–1910, painting fishermen, beaches and the summer light: <i>Krøyer\'s Summer Evening on Skagen\'s Southern Beach</i>, <i>Michael Ancher\'s Will He Round the Point?</i>. Membership: painters who worked at Skagen as part of the colony.',
                     aliases='Skagen school', see='T47 Naturalism;T49 Impressionism', src=[[W + 'Skagen_Painters', 'Wikipedia']],
                     cats=[['https://skagenskunstmuseer.dk/en/', 'Art Museums of Skagen', 'the Skagens Museum collection of the colony'], ['https://open.smk.dk/en/art?q=skagen', 'SMK Open (Statens Museum for Kunst)', 'Danish national gallery works on Skagen'],
                           ['https://commons.wikimedia.org/wiki/Category:Skagen_Painters', 'Wikimedia Commons: Skagen Painters', 'images of works by the colony']],
                     named=['Danish Skagen Painters', 'Norwegian and Swedish members'], axis='by nationality within the colony: Danish core members first, then Norwegian and Swedish members; each group ordered by birth year.'),
 'Newlyn School': dict(breadth='narrow', defn='The colony of plein-air naturalist painters at Newlyn and Lamorna in Cornwall, from c. 1882: <i>Stanhope Forbes\'s A Fish Sale on a Cornish Beach</i>, <i>Langley\'s Never Morning Wore to Evening</i>, <i>Bramley\'s A Hopeless Dawn</i>. Membership: painters who settled or worked at Newlyn as part of the colony.',
                     aliases='Newlyn colony', see='T47 Naturalism', src=[[W + 'Newlyn_School', 'Wikipedia']],
                     cats=[['https://penleehouse.org.uk/', 'Penlee House Gallery & Museum', 'the principal public collection of Newlyn School painting, Penzance'],
                           ['https://commons.wikimedia.org/wiki/Category:Newlyn_School', 'Wikimedia Commons: Newlyn School', 'images of works by the colony']],
                     named=['Newlyn colony painters'], axis='one group: painters of the Newlyn colony from its founding in the early 1880s, ordered by birth year.'),
 'Lyon School': dict(breadth='narrow', defn='The school of painting of Lyon, from the Troubadour painters around Révoil and Richard to the religious and idealist painters of the July Monarchy and Second Empire: <i>Révoil\'s Joan of Arc in Prison</i>, <i>Janmot\'s The Poem of the Soul</i>, <i>Orsel\'s Good and Evil</i>. Membership: painters trained at or working from the École des Beaux-Arts of Lyon.',
                     aliases='École lyonnaise;Lyonnais school', see='T33 Romanticism;T40 Academic Art', src=[[W + 'Lyon_School', 'Wikipedia']],
                     cats=[['https://www.pop.culture.gouv.fr/', 'POP – Joconde', 'French museum collections incl. the Musée des Beaux-Arts de Lyon'], ['https://www.mba-lyon.fr/', 'Musée des Beaux-Arts de Lyon', 'the principal collection of the school']],
                     named=['Troubadour founders', 'Religious and idealist painters', 'Landscape and genre'],
                     axis='by phase and subject: the Troubadour founders of c. 1800, the religious and idealist painters of the 1830s–1860s, then landscape, flower and genre painters; each group ordered by birth year.'),
 'Golden Age of Finnish Art': dict(breadth='narrow', defn='Finnish painting of c. 1880–1910, from Paris-trained naturalism to national romanticism and the Kalevala: <i>Edelfelt\'s Conveying the Child\'s Coffin</i>, <i>Gallen-Kallela\'s The Defence of the Sampo</i>, <i>Schjerfbeck\'s The Convalescent</i>. Membership: Finnish painters active in that generation.',
                     aliases='Finnish Golden Age', see='T47 Naturalism;T53 Symbolism', src=[[W + 'Golden_Age_of_Finnish_Art', 'Wikipedia']],
                     cats=[['https://www.kansallisgalleria.fi/en/search', 'Finnish National Gallery collections', 'Ateneum and national collections online'], [W + 'Golden_Age_of_Finnish_Art', 'Wikipedia: Golden Age of Finnish Art', 'overview with the painters of the period']],
                     named=['Paris-trained naturalists', 'National romanticism'], axis='by phase: Paris-trained naturalists of the 1880s first, then national-romantic painters of the 1890s; each group ordered by birth year.'),
}
LYON_T = {'Pierre Révoil', 'François Fleury-Richard', 'Antoine Berjon', 'Claudius Jacquand'}
LYON_R = {'Victor Orsel', 'Paul Chenavard', 'Louis Janmot', 'Louis Lamothe', 'Claudius Lavergne', 'Jean-Claude Bonnefond', 'Joseph Guichard'}
EXTRA = {
 'Skagen Painters': [nk('Peder Severin Krøyer', 'Danish Skagen Painters', 'Painter, b. 1851; leading figure of the colony (Summer Evening on Skagen\'s Southern Beach)', W + 'Peder_Severin_Kr%C3%B8yer'),
                     nk('Anna Ancher', 'Danish Skagen Painters', 'Painter, b. 1859 in Skagen; interiors and light; wife of Michael Ancher', W + 'Anna_Ancher'),
                     nk('Holger Drachmann', 'Danish Skagen Painters', 'Poet and marine painter, b. 1846; early member of the colony', W + 'Holger_Drachmann'),
                     nk('Marie Krøyer', 'Danish Skagen Painters', 'Painter, b. 1867; wife of P. S. Krøyer', W + 'Marie_Kr%C3%B8yer'),
                     nk('Oscar Björck', 'Norwegian and Swedish members', 'Swedish painter, b. 1860; worked at Skagen in the 1880s', W + 'Oscar_Bj%C3%B6rck'),
                     nk('Frits Thaulow', 'Norwegian and Swedish members', 'Norwegian painter, b. 1847; at Skagen 1879–80', W + 'Frits_Thaulow')],
 'Newlyn School': [nk('Thomas Cooper Gotch', 'Newlyn colony painters', 'Painter, b. 1854; settled at Newlyn 1887', W + 'Thomas_Cooper_Gotch'),
                   nk('Albert Chevallier Tayler', 'Newlyn colony painters', 'Painter, b. 1862; Newlyn genre scenes of the 1880s', W + 'Albert_Chevallier_Tayler')],
 'Golden Age of Finnish Art': [nk('Eero Järnefelt', 'National romanticism', 'Painter, b. 1863; Koli landscapes and Burning the Brushwood', W + 'Eero_J%C3%A4rnefelt'),
                               nk('Pekka Halonen', 'National romanticism', 'Painter, b. 1865; Tuusula winter landscapes', W + 'Pekka_Halonen')],
 'Peredvizhniki': [nk('Nikolai Ge', 'Founding generation (born before 1840)', 'Painter, b. 1831; founding member (What Is Truth?)', W + 'Nikolai_Ge'),
                   nk('Viktor Vasnetsov', 'Second generation (born 1840–1854)', 'Painter, b. 1848; member from 1874 (Bogatyrs)', W + 'Viktor_Vasnetsov')],
}
NAT_SK = {'Christian Krohg'}
NEWLYN_LATE = {'Harold Harvey'}
FIN_NR = {'Akseli Gallen-Kallela', 'Ellen Thesleff'}
for i, (key, d) in enumerate(NEWDEF.items(), 1):
    items = []
    for _, row, raw in new_rows.get(key, []):
        b = birth(raw); n = row[0]; g = None
        if key == 'Peredvizhniki':
            g = d['named'][0] if b < 1840 else d['named'][1] if b < 1855 else d['named'][2]
        elif key == 'Skagen Painters':
            g = d['named'][1] if n in NAT_SK else d['named'][0]
        elif key == 'Newlyn School':
            g = d['named'][0]
        elif key == 'Lyon School':
            g = d['named'][0] if n in LYON_T else d['named'][1] if n in LYON_R else d['named'][2]
        elif key == 'Golden Age of Finnish Art':
            g = d['named'][1] if n in FIN_NR else d['named'][0]
        items.append((g, row, raw))
    for ex in EXTRA.get(key, []):
        b = int(re.search(r'b\. (\d{4})', ex[2]).group(1))
        items.append((ex[1], ex, [None] * 5 + [{'birth': str(b)}]))
    kinds = finish(key, items, d['named'], '', cap=150, minsize=3)
    out['new_leaves'].append({'key': f'NEW{i}', 'sub': 'A5', 'label': key, 'breadth': d['breadth'], 'defn': d['defn'], 'aliases': d['aliases'], 'see': d['see'],
                              'src': d['src'], 'catalogues': d['cats'], 'axis': d['axis'], 'kinds': kinds})
json.dump(out, open('result.json', 'w'), ensure_ascii=False, indent=0)
print({k: len(v['kinds']) for k, v in out['leaves'].items()}, [(n['label'], len(n['kinds'])) for n in out['new_leaves']], len(moves))
