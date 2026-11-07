import json,collections as C,sys
d=json.load(open('../../va_in/bucket_modern_west.json'))
rows=d['leaves'][0]['rows']
g=C.defaultdict(list)
for r in rows:
  if len(r)<6: continue
  c=r[5]['countries'].split(',')[0].strip()
  g[c].append(r)
want=sys.argv[1].split(';')
for c in want:
  print('##',c,len(g[c]))
  print('; '.join(f"{r[0]}|{r[5]['birth'][2:]}"+('|'+r[1] if r[1]!='Artists' else '')+('|M:'+r[5]['movements'] if r[5]['movements'] else '') for r in sorted(g[c],key=lambda r:r[5]['birth'])))
