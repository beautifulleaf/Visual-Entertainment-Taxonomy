"""Era re-sectioning of B8-3 Workplace Comedy (TV). Adds a 'B8-3' entry to resections.json."""
import csv, json, re, collections, os, sys
D = '/home/user/Visual-Entertainment-Taxonomy/taxonomy/r3'
OUT = os.path.join(D, 'coverage_out/sitcom_eras/resections.json')
rows = [r for r in csv.DictReader(open(os.path.join(D, 'ft_title_index.tsv')), delimiter='\t') if r['leaf'] == 'B8-3']
FIX = {'tt1588221': 'GB',   # Rev. (BBC Two), miscoded DE
       'tt0296348': 'TR',   # Hastane, blank
       'tt10324166': 'US',  # Unbreakable Kimmy Schmidt special, director in who
       'tt11867650': 'IN'}  # Maddam Sir (Sony SAB), miscoded IO
def yr(r): return int(re.match(r'\d{4}', r['year']).group())
def ctry(r): return FIX.get(r['id'], r['who'])
SECS = ["US early network and classic eras (1947–1969)",
        "US relevancy era (1970s): Lear & MTM",
        "US 1980s network era",
        "US Must See TV era (1990s)",
        "US 2000s single-camera turn",
        "US streaming era (2010s–)",
        "British golden age (1960s–1970s)",
        "British sitcom 1980s–1990s",
        "British sitcom 2000s (post-Office mockumentary turn)",
        "British sitcom since 2010",
        "Other national workplace comedies (to 1999)",
        "Other national workplace comedies (2000s–)"]
def f(r):
    y, c = yr(r), ctry(r)
    if c == 'US': return 1 if y < 1970 else 2 if y < 1980 else 3 if y < 1990 else 4 if y < 2000 else 5 if y < 2010 else 6
    if c == 'GB': return 7 if y < 1980 else 8 if y < 2000 else 9 if y < 2010 else 10
    return 11 if y < 2000 else 12
assign = {r['id']: f(r) for r in rows}
assert len(assign) == len(rows) == 197 and all(1 <= v <= len(SECS) for v in assign.values())
cnt = collections.Counter(assign.values())
assert all(cnt[i] for i in range(1, len(SECS) + 1)), cnt
out = json.load(open(OUT))
out['B8-3'] = {'axis': "era of the workplace sitcom, by national tradition (start year)",
               'secs': SECS, 'assign': dict(sorted(assign.items()))}
json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=1)
print('B8-3', len(rows), [cnt[i] for i in range(1, len(SECS) + 1)])
for r in rows: print(assign[r['id']], ctry(r), r['year'], r['title'], file=sys.stderr)
