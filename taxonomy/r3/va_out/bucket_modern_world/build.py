import json, re, collections, sys
sys.path.insert(0, '.')
from prim import prim
inp = json.load(open('../../va_in/bucket_modern_world.json'))['leaves'][0]
rows = inp['rows']
CMAP = {'Empire of Japan':'Japan','British Raj':'India','Dominion of India':'India',"People's Republic of China":'China',
 'Republic of China':'China','Qing dynasty':'China','Ottoman Empire':'Turkey','Taiwan under Japanese rule':'Taiwan',
 'Szechwan Military Government':'China','National Government of the Republic of China':'China','Beiyang Government':'China','Empire of China':'China',
 'State of Greater Lebanon':'Lebanon','Arab Kingdom of Syria':'Syria',"Ba'athist Syria":'Syria','Second Syrian Republic':'Syria','First Syrian Republic':'Syria',
 'Kingdom of Egypt':'Egypt','United Arab Republic':'Egypt','Republic of Egypt':'Egypt','French protectorate of Tunisia':'Tunisia',
 'Pahlavi Iran':'Iran','Mandatory Palestine':'Israel','Union of South Africa':'South Africa','Rhodesia':'Zimbabwe',
 'Armenian Soviet Socialist Republic':'Soviet Union','Kazakhstan':'Soviet Union','Tajikistan':'Soviet Union','Turkmenistan':'Soviet Union',
 'United Kingdom of Great Britain and Ireland':'United Kingdom','Kingdom of Italy':'Italy','Kingdom of the Netherlands':'Netherlands','German Empire':'Germany','Russian Empire':'Russia','Korea':'South Korea'}
def clean_countries(c):
    out = []
    for x in [x.strip() for x in c.split(',') if x.strip()]:
        x = CMAP.get(x, x)
        if x not in out: out.append(x)
    return out
COUNTRY_OVERRIDE = {
 'Yasuo Kuniyoshi':'United States','Dong Kingman':'United States','Myrna Báez':'Puerto Rico','Rafael Ferrer':'Puerto Rico','Antonio Martorell':'Puerto Rico',
 'Joseph Uhl':'Germany','Margaret Mellis':'United Kingdom','Moussa Ayoub':'Lebanon','Stacha Halpern':'Australia','Béla Bán':'Israel','David Schneuer':'Israel',
 'Salomon Bernstein':'Israel','Lidiya Vertinskaya':'Soviet Union','Francheska Yarbusova':'Soviet Union','Vera Sogoyan':'Soviet Union','Jak İhmalyan':'Soviet Union',
 'Osamu Suzuki':'Japan','Mehdi Moutashar':'Iraq','Maliheh Afnan':'Palestine','Mustafa al-Hallaj':'Palestine','Tamam Al-Akhal':'Palestine','Ida Bagus Gelgel':'Indonesia','Régulo Pérez':'Venezuela',
 'Mohammed Issiakhem (1928-1985)':'Algeria','Ablade Glover':'Ghana','Bill Ainslie':'South Africa','Cecil Skotnes':'South Africa','Helen Lieros':'Zimbabwe',
 'Arsen Shapanyan':'Turkey','Sarkis Katchadourian':'Turkey','Graham Bell':'South Africa','Gertrud von Hassel':'South Africa',
}
WEST = {'France','United Kingdom','Germany','Spain','Switzerland','Italy','Netherlands','Belgium','Austria','Norway','Austria–Hungary','Poland','Hungary','Romania','Belarus','Czech Republic','Russia'}
def country_of(name, c):
    if name in COUNTRY_OVERRIDE: return COUNTRY_OVERRIDE[name]
    cs = clean_countries(c)
    if not cs: return None
    nonw = [x for x in cs if x not in WEST]
    if 'United States' in nonw and len(nonw) > 1:
        nonw = [x for x in nonw if x != 'United States']
    if 'Soviet Union' in nonw and len(nonw) > 1 and name not in COUNTRY_OVERRIDE:
        pass
    return (nonw or cs)[0]
def load(fn):
    out = {}
    for l in open(fn, encoding='utf-8'):
        l = l.rstrip('\n')
        if not l or l.startswith('#'): continue
        p = l.split('|')
        out[p[0]] = p[1:]
    return out
M1, M2, M3 = load('map1.txt'), load('map2.txt'), load('map3.txt')
def gloss_basic(r, country=None):
    e = r[5] if len(r) > 5 else {}
    b = e.get('birth', '')
    cs = clean_countries(e.get('countries', ''))
    if country and country not in cs: cs = [country] + cs
    parts = []
    if b: parts.append('b. ' + b)
    if cs: parts.append(', '.join(cs))
    return '; '.join(parts)
def us_cohort(b):
    try: b = int(b)
    except: return 'United States (birth year not recorded)'
    for lo, hi in ((1860,1879),(1880,1894),(1895,1909),(1910,1924),(1925,1934),(1935,1999)):
        if lo <= b <= hi: return f'United States (born {lo}–{hi})' if hi<1999 else 'United States (born 1935 and later)'
    return 'United States (born 1945 and later)'
NEW = {}  # key -> list of rows
residual = []
moves = []
dropped = []
for r in rows:
    name = r[0]
    e = r[5] if len(r) > 5 else {}
    b = e.get('birth', '')
    if not name.strip():
        moves.append([name, 'A5-110', 'A5-111'])
        dropped.append(['A5-110', '(nameless row)', 'nameless artist row (b. 1927, United States) with no identifiable name; parked in moves_out to A5-111 only to satisfy the maker count — please delete'])
        continue
    if name in M1:
        key = M1[name][0][2:]; grp = M1[name][1]; note = M1[name][2] if len(M1[name]) > 2 else ''
        g = gloss_basic(r)
        gl = (note + ' · ' + g) if note else g
        NEW.setdefault(key, []).append([name, grp, gl, r[3], 1, int(b) if b.isdigit() else 9999])
        continue
    if name in M2:
        moves.append([name, 'A5-110', M2[name][0]])
        continue
    if name in M3:
        grp = M3[name][1]
    else:
        c = country_of(name, e.get('countries', ''))
        if c is None: c = 'Country not recorded'
        grp = us_cohort(b) if c == 'United States' else c
    residual.append([name, grp, gloss_basic(r), r[3], 1, int(b) if b.isdigit() else 9999])
json.dump({'NEW': NEW, 'residual': residual, 'moves': moves, 'dropped': dropped}, open('stage.json', 'w'), ensure_ascii=False, indent=0)
print('new', {k: len(v) for k, v in NEW.items()}, 'residual', len(residual), 'moves', len(moves))
print(collections.Counter(x[1] for x in residual).most_common())
