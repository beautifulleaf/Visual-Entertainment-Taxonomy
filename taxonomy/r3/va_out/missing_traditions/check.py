import json,csv,re,urllib.parse as up,subprocess,os
D=os.path.dirname(os.path.abspath(__file__))
R=json.load(open(D+'/result.json'))
C=[r['tradition'] for r in csv.DictReader(open(D+'/../../collections/missing_candidates.csv')) if int(r['objects'])>=50]
allc=[r['tradition'] for r in csv.DictReader(open(D+'/../../collections/missing_candidates.csv'))]
cf=[t for l in R['new_leaves'] for t in l['collections_from']]
mg=[r['tradition'] for r in csv.DictReader(open(D+'/merges.csv'))]
cov=set(cf)|set(mg)
print('uncovered:',[c for c in C if c not in cov]); print('not in csv:',[t for t in cf+mg if t not in allc])
import collections; print('dups:',[k for k,v in collections.Counter(cf+mg).items() if v>1])
urls=set()
for l in R['new_leaves']:
    for s in l['src']: urls.add(s[0])
    for k in l['kinds']: urls.add(k[3][3:])
t=[up.unquote(u.split('/wiki/')[1]) for u in urls if 'wikipedia.org/wiki/' in u]
open(D+'/_t.txt','w').write('\n'.join(t))
out=subprocess.run(['python3',D+'/titles.py',D+'/_t.txt'],capture_output=True,text=True).stdout
print([l for l in out.splitlines() if l.startswith('NO')])
labels=[l['label'] for l in R['new_leaves']]
import csv as c2
ex={r['label'].lower() for r in c2.DictReader(open(D+'/../../va_leaf_index.tsv'),delimiter='\t')}
print('label clash:',[x for x in labels if x.lower() in ex])
