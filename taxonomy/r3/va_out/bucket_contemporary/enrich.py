import json,csv,collections
d=json.load(open('../../va_in/bucket_contemporary.json'))
la={}
for r in csv.DictReader(open('../../../../data/interim/contemporary_list_artists.csv')):
    la.setdefault(r['name'],r)
    la.setdefault(r['label'],r)
lists={}
for r in csv.DictReader(open('../../../../data/interim/contemporary_lists.csv')):
    lists.setdefault(r['name'],r)
info={}
for l in d['leaves']:
  for r in l['rows']:
    if not r[4]: continue
    m=r[5] if len(r)>5 else {}
    c=m.get('countries',''); b=m.get('birth',''); reg=''
    x=la.get(r[0]); y=lists.get(r[0])
    if x:
        c=c or x['country']; b=b or x['birth_year']; reg=x['region']
    if y:
        c=c or y['country']; b=b or y['birth_year']
    info[r[0]]=dict(c=c,b=b,reg=reg,list=(x or {}).get('lists',''))
json.dump(info,open('info.json','w'))
print(collections.Counter(bool(v['c']) for v in info.values()), collections.Counter(v['reg'] for v in info.values() if not v['c']))
