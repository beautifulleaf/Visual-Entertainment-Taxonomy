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
            for i in range(k):
                chunk = lst[i * size:(i + 1) * size]
                if not chunk:
                    continue
                b0, b1 = birth(chunk[0][1]), birth(chunk[-1][1])
                out_groups.append((f'{c}, {gen_label} {b0}–{b1}', chunk))
        else:
            out_groups.append((c, lst))
    kinds = []
    for g, lst in out_groups:
        lst = sorted(lst, key=lambda x: (birth(x[1]) or 9999, x[0][0])) if not g.startswith(tuple(COUNTRY_ORDER)) else lst
        for row, raw in lst:
            r = list(row)
            r[1] = g
            kinds.append(r)
    axis = axis_named + ' Then the remaining artists by country of activity (historic states folded into present-day countries; groups over 150 split by birth year; countries with fewer than 3 artists pooled by region), each group ordered by birth year.'
    return kinds
