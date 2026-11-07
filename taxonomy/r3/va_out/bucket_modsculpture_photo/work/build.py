import json, sys, collections, importlib
sys.path.insert(0, '.')
from common import *
import meta; importlib.reload(meta)
try:
    import assign; A = assign.A
except ImportError:
    A = {}
leaves = load()
incodes = {l['code'] for l in leaves}
REGION = {}
for c in ['Argentina','Brazil','Chile','Colombia','Cuba','Mexico','Peru','Uruguay','Venezuela','El Salvador','Nicaragua','Paraguay','Haiti','Jamaica','The Bahamas']: REGION[c]='Latin America and the Caribbean'
for c in ['Ghana','Ivory Coast','Zimbabwe','Nigeria','Senegal','Benin','Democratic Republic of the Congo','Angola','Uganda','Kenya','Cameroon','Ethiopia','Sudan','South Africa']: REGION[c]='Sub-Saharan Africa'
for c in ['Egypt','Iraq','Lebanon','Turkey','Iran','Morocco','Jordan','Bahrain','Kuwait','Saudi Arabia','Palestine','Syria','Tunisia','Afghanistan','Israel']: REGION[c]='Middle East and North Africa'
for c in ['India','Pakistan','Bangladesh','Vietnam','Philippines','Indonesia','Singapore','Thailand','China','Taiwan','South Korea','Japan']: REGION[c]='Asia'
for c in ['Estonia','Latvia','Lithuania']: REGION[c]='Baltic states'
for c in ['Yugoslavia','Serbia','Croatia','Slovenia','North Macedonia','Bosnia and Herzegovina','Albania','Greece','Bulgaria','Romania','Moldova']: REGION[c]='Southeast Europe'
for c in ['Ukraine','Armenia','Kazakhstan','Kyrgyzstan','Azerbaijan','Turkmenistan','Uzbekistan','Belarus','Georgia']: REGION[c]='Russia'  # placeholder merge
for c in ['Australia','New Zealand']: REGION[c]='Australia and New Zealand'
for c in ['Iceland','Luxembourg','Malta','Ireland']: REGION[c]=None
out = {'leaves': {}, 'new_leaves': [], 'moves_out': [], 'dropped': []}
buckets = collections.defaultdict(list)   # (code, group) -> rows
countrygroups = collections.defaultdict(list)  # code -> list of (row, country)
MED = {'D5-118':'Sculptor','J1-7':'Photographer','J1-8':'Photographer','J1-9':'Photographer','J1-12':'Photographer','J1-13':'Photographer'}
def gloss(r, code):
    if r[2]: return r[2]
    e = r[5] if len(r) > 5 else {}
    cs = countries(e.get('countries', ''))
    cs = [c for c in cs if not (c == 'Soviet Union' and len(cs) > 1)]
    g = MED[code]
    if cs: g += ', ' + ' / '.join(cs[:3])
    if e.get('birth'): g += ', b. ' + e['birth']
    return g
seen = set()
for l in leaves:
    code = l['code']
    for r in l['rows']:
        row = [r[0], None, gloss(r, code), r[3], r[4]]
        a = A.get(r[0])
        if isinstance(a, str) and a in incodes: a = (a, None)
        if a is None:
            countrygroups[code].append((row, r))
        elif isinstance(a, str):
            if a == 'DROP': out['dropped'].append([code, r[0], 'not a kind'])
            elif a.startswith('NEW') or a in incodes: buckets[(a, None)].append((row, r))
            else: out['moves_out'].append([r[0], code, a])
        else:
            tgt, grp = a
            if tgt == 'G': tgt = code
            if grp is None: countrygroups[tgt].append((row, r))
            else: buckets[(tgt, grp)].append((row, r))
def birth(r):
    e = r[5] if len(r) > 5 else {}
    try: return int(e.get('birth', '') or 9999)
    except: return 9999
# country residue
for code, items in list(countrygroups.items()):
    cnt = collections.Counter(main_country(r[5].get('countries','') if len(r)>5 else '') for _, r in items)
    for row, r in items:
        c = main_country(r[5].get('countries','') if len(r)>5 else '') or 'Country not recorded'
        if cnt[c] < 3:
            reg = REGION.get(c, 'Other European countries') if c != 'Country not recorded' else c
            if reg == 'Russia': reg = 'Russia and the Soviet Union'
            c = reg or 'Other European countries'
        if c in ('Russia',): c = 'Russia and the Soviet Union'
        buckets[(code, ('C', c))].append((row, r))
# order and emit
M = meta.META
for code in [l['code'] for l in leaves] + [n['key'] for n in meta.NEW]:
    grpkeys = [k for k in buckets if k[0] == code]
    named = [k for k in grpkeys if not isinstance(k[1], tuple)]
    ctry = [k for k in grpkeys if isinstance(k[1], tuple)]
    order = M.get(code, {}).get('order', [])
    named.sort(key=lambda k: (order.index(k[1]) if k[1] in order else 999, k[1] or ''))
    ctry.sort(key=lambda k: -len(buckets[k]))
    kinds = []
    for k in named + ctry:
        g = k[1] if not isinstance(k[1], tuple) else k[1][1]
        rows = sorted(buckets[k], key=lambda x: birth(x[1]))
        if g is None: g = 'Members'
        if isinstance(k[1], tuple) and len(rows) > 150:
            # split by generation
            for row, r in rows:
                b = birth(r)
                row[1] = f"{g} (born before 1900)" if b < 1900 else (f"{g} (born 1900–1939)" if b < 1940 else f"{g} (born 1940 or later)")
                if code in ('J1-13',): row[1] = f"{g} (born before 1960)" if b < 1960 else f"{g} (born 1960 or later)"
                if code in ('J1-7','J1-8'): row[1] = f"{g} (born before 1830)" if b < 1830 else f"{g} (born 1830 or later)"
                kinds.append(row)
        else:
            for row, r in rows: row[1] = g; kinds.append(row)
    kinds += M.get(code, {}).get('extra', [])
    ent = {'axis': M.get(code, {}).get('axis', ''), 'catalogues': M.get(code, {}).get('catalogues', []), 'kinds': kinds}
    if M.get(code, {}).get('defn'): ent['defn'] = M[code]['defn']
    if code in incodes:
        ent['alias_rows'] = []
        out['leaves'][code] = ent
    else:
        nl = dict(next(n for n in meta.NEW if n['key'] == code)); nl.update(ent); out['new_leaves'].append(nl)
json.dump(out, open(ROOT + '/taxonomy/r3/va_out/bucket_modsculpture_photo/result.json', 'w'), ensure_ascii=False, indent=1)
for code in out['leaves']: 
    c = collections.Counter(k[1] for k in out['leaves'][code]['kinds']); print(code, len(out['leaves'][code]['kinds']), c.most_common(60))
for n in out['new_leaves']: print(n['key'], n['label'], len(n['kinds']))
print('moves', len(out['moves_out']), collections.Counter(m[2] for m in out['moves_out']).most_common())
