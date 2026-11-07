import json,re
d=json.load(open('../../va_in/bucket_academic_19c.json'))
def cc(c):
    c=(c or '').split(',')[0].strip()
    return c
out=open('dump.tsv','w')
for l in d['leaves']:
    rows=sorted(l['rows'],key=lambda r:(cc(r[5].get('countries') if len(r)>5 else ''),(r[5].get('birth') if len(r)>5 else '') or ''))
    for r in rows:
        e=r[5] if len(r)>5 else {}
        g=r[2]
        g=re.sub(r'movement academic art|movement Romanticism|movement Neoclassicism|movement realism|movement Naturalism','',g).strip('; ')
        out.write('\t'.join([l['code'],r[0],e.get('birth',''),e.get('countries','')[:40],e.get('medium','')[:12] if e.get('medium') not in ('painting','sculpture') else '',r[1] if r[1]!='Artists' else '',g[:50]])+'\n')
