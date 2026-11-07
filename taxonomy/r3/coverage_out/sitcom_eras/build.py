"""Era re-sectioning of sitcom leaves (B8-1, B8-5, B8-9). Assigns by start year + country."""
import csv, json, re, collections, os
HERE = os.path.dirname(os.path.abspath(__file__))
R3 = os.path.abspath(os.path.join(HERE, '..', '..'))
rows = list(csv.DictReader(open(os.path.join(R3, 'ft_title_index.tsv')), delimiter='\t'))
# country fixes for blank/miscoded rows (US network productions)
FIX = {'tt0052461': 'US',   # Dennis the Menace (CBS)
       'tt1948541': 'US',   # Broad City web series
       'tt0299348': 'TR'}   # Mahallenin Muhtarlari
def yr(r): return int(re.match(r'\d{4}', r['year']).group())
def ctry(r): return FIX.get(r['id'], r['who'])

US7 = ["US early network sitcom (1947–1959)", "US classic network era (1960s)",
       "US relevancy era (1970s): Lear & MTM", "US 1980s network era",
       "US Must See TV era (1990s)", "US 2000s network era", "US streaming era (2010s–)"]
def us7(y):
    return 1 if y < 1960 else 2 if y <= 1970 else 3 if y < 1980 else 4 if y < 1990 else 5 if y < 2000 else 6 if y < 2010 else 7

def b8_1(r):
    y, c = yr(r), ctry(r)
    if c == 'US': return us7(y)
    if c == 'GB': return 8
    return 9 if y < 2000 else 10
B81 = US7 + ["British family sitcoms", "Other national family sitcoms (to 1999)",
             "Other national family sitcoms (2000s–)"]

B85 = ["US network era (1960s–1980s)", "US Must See TV era (1990s)", "US 2000s network era",
       "US streaming era (2010s–)", "British sitcoms (1970s–1980s)",
       "British post-alternative sitcoms (1990s–2000s)", "British sitcoms since 2010",
       "Other national sitcoms (to 1999)", "Other national sitcoms (2000s–)"]
def b8_5(r):
    y, c = yr(r), ctry(r)
    if c == 'US': return 1 if y < 1990 else 2 if y < 2000 else 3 if y < 2010 else 4
    if c == 'GB': return 5 if y < 1990 else 6 if y < 2010 else 7
    return 8 if y < 2000 else 9

B89 = ["British golden age (1960s–1970s)", "British sitcom 1980s–1990s",
       "British sitcom 2000s (post-Office turn)", "British sitcom since 2010",
       "Other national character comedies (to 1999)", "Other national character comedies (2000s–)"]
def b8_9(r):
    y, c = yr(r), ctry(r)
    if c == 'GB': return 1 if y < 1980 else 2 if y < 2000 else 3 if y < 2010 else 4
    return 5 if y < 2000 else 6

SPEC = {
 'B8-1': ("era of the network sitcom, by national tradition (start year)", B81, b8_1),
 'B8-5': ("era of the sitcom, by national tradition (start year)", B85, b8_5),
 'B8-9': ("era of the sitcom, by national tradition (start year)", B89, b8_9),
}
out = {}
for leaf, (axis, secs, f) in SPEC.items():
    titles = [r for r in rows if r['leaf'] == leaf]
    assign = {r['id']: f(r) for r in titles}
    assert len(assign) == len(titles) and all(1 <= v <= len(secs) for v in assign.values())
    cnt = collections.Counter(assign.values())
    assert all(cnt[i] for i in range(1, len(secs) + 1)), (leaf, cnt)
    out[leaf] = {'axis': axis, 'secs': secs, 'assign': dict(sorted(assign.items()))}
    print(leaf, len(titles), [cnt[i] for i in range(1, len(secs) + 1)])
json.dump(out, open(os.path.join(HERE, 'resections.json'), 'w'), ensure_ascii=False, indent=1)
