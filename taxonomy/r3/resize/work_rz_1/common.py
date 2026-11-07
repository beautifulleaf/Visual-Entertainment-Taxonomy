import json,re
D='/home/user/Visual-Entertainment-Taxonomy/taxonomy/r3/resize/'
inp={l['code']:l for l in json.load(open(D+'in_rz_1.json'))['leaves']}
def yr(t):
    m=re.search(r'\d{4}',str(t['year'] or '')); return int(m.group()) if m else 0
def rows(code):
    L=[l for l in open(D+'work_rz_1/'+code+'.txt')]
    return [dict(n=i+1,id=x.split('|')[0],sec=x.split('|')[1],y=yr({'year':x.split('|')[2]}),title=x.split('|')[3],who=x.split('|')[4],c=x.split('|')[5]) for i,x in enumerate(L)]
