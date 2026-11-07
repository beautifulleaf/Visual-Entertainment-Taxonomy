import re, sys, json, os, collections
sys.path.insert(0, os.path.dirname(__file__))
from files import SPEC, rows
from specs import S
GX = re.compile(r'folio|manuscript|painting|\bpage\b|illustration|drawing|\bprints?\b|photograph|kimono|furisode|kosode|textile|\bcoins?\b|dinar|\bfils\b|woodblock|calligraphy|\bQur.an\b(?! (box|stand|chest))|books and manuscripts|documents and historical', re.I)
KEEPMS = {'I2-6'}
comp = collections.defaultdict(list)
for code, lst in S.items():
    for f, d in lst:
        comp[f].append((code, {k: re.compile(v, re.I) for k, v in d.items()}))
out = collections.defaultdict(list)
for f in SPEC:
    if f not in comp: continue
    s = SPEC[f]
    for r, cult, typ in rows(f):
        title = (r.get('title_en') or r.get(s[2]) or '').strip() if f == 'east_asia' else (r.get(s[2]) or '').strip()
        allt = cult + ' | ' + typ + ' | ' + title + ' | ' + (r.get('object_type') or '') + ' | ' + (r.get('collection') or '')
        for code, d in comp[f]:
            if 'c' in d and not d['c'].search(cult): continue
            if 't' in d and not d['t'].search(typ): continue
            if 'ti' in d and not (d['ti'].search(title) or d['ti'].search(r.get('title') or '')): continue
            if 'a' in d and not d['a'].search(allt): continue
            if 'n' in d and d['n'].search(allt): continue
            if 'i' in d and not d['i'].search(r.get(s[4], '')): continue
            if GX.search(title + ' | ' + typ + ' | ' + (r.get('object_type') or '')): continue
            dt = r.get(s[3][0]) or ''
            db = r.get(s[3][1]) if s[3][1] else ''
            out[code].append(dict(f=f, title=title, title_orig=r.get('title', ''), date=dt, db=db, inst=r.get(s[4], ''), url=r.get(s[5], ''),
                                  place=r.get(s[6], ''), typ=typ[:120], cult=cult[:160], desig=r.get('designation_en', ''), makers=(r.get('makers') or r.get('maker') or r.get('artist_romanised') or '')[:120]))
json.dump(out, open(os.path.join(os.path.dirname(__file__), 'matches.json'), 'w'), ensure_ascii=False)
for c in sorted(out): print(c, len(out[c]), collections.Counter(x['f'] for x in out[c]).most_common())
