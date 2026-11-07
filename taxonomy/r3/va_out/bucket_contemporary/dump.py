import json
d=json.load(open('../../va_in/bucket_contemporary.json'))
out=[]
for l in d['leaves']:
  for r in l['rows']:
    if not r[4]: continue
    m=r[5] if len(r)>5 else {}
    c=m.get('countries','')
    mv=(m.get('movements') or '').replace('contemporary art','').strip('| ')
    g='' if r[1]=='Artists' else r[1]
    out.append((c.split(',')[0],m.get('birth',''),l['code'],r[0],c,m.get('medium','')[:12],mv,g))
out.sort()
with open('dump.tsv','w') as f:
  for o in out: f.write('\t'.join([o[2].replace('A5-111','A').replace('D5-119','S').replace('M1-1','I').replace('M1-2','C').replace('M2-5','N').replace('L2-51','St'),o[3],o[1],o[4][:30],o[5],o[6],o[7]]).rstrip('\t')+'\n')
print(len(out))
