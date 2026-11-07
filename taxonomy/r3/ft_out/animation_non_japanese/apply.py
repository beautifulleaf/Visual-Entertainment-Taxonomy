import csv,collections,sys
csv.field_size_limit(10**9)
R=list(csv.DictReader(open('../../ft_in/animation_non_japanese.csv')))
asg={}; errs=[]
for fn in ['map_features.txt','map_shorts.txt','map_series.txt']:
    cur=None
    for line in open(fn):
        line=line.rstrip('\n')
        if not line.strip(): continue
        if line.startswith('=='):
            p=line.split(); cur=(p[1],p[2] if len(p)>2 else ''); continue
        t,_,y=line.partition('@')
        c=[x for x in R if x['title']==t and (not y or x['year']==y)]
        if not c: c=[x for x in R if len(t)>=12 and x['title'].startswith(t) and (not y or x['year']==y)]
        if not c: errs.append(f'NOMATCH {fn}:{line}'); continue
        if len(c)>1 and not t.startswith('Justice League: Crisis on Infinite'):
            errs.append(f'MULTI {line} {[x["year"] for x in c]}')
        for x in c:
            if x['id'] in asg: errs.append(f'DUP {line} {asg[x["id"]]} {cur}')
            asg[x['id']]=cur
for e in errs: print(e)
miss=[x for x in R if x['id'] not in asg]
print('missing',len(miss))
for x in miss: print(' ',x['title'],x['year'],x['old_leaf'])
import json
json.dump(asg,open('asg.json','w'))
