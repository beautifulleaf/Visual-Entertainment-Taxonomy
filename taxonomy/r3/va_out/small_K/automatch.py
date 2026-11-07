import json,csv,collections,re
d=json.load(open('../../va_in/small_K.json'))
A=list(csv.DictReader(open('../../../../data/interim/architecture_exemplars.csv')))
N=list(csv.DictReader(open('../../../../data/interim/architecture_nonwestern_exemplars.csv')))
wl=collections.Counter(r['style_label'] for r in A if r['style_label'])
nl=collections.Counter(r['proposed_style'] for r in N if r['proposed_style'])
wlow={k.lower():k for k in wl}; nlow={k.lower():k for k in nl}
out={}
for l in d['leaves']:
    cands=[l['label']]+[l['label'].replace(' Architecture',' architecture')]+l['alias_rows']+[a.strip() for a in re.split('[;,]',l['aliases']) if a.strip()]
    cands+= [r[0] for r in l['rows'] if r[3].startswith('architecture') ]
    W=[];Nn=[]
    for c in cands:
        k=c.lower()
        for kk in (k,k+' architecture',k.replace(' style',''),k+' style'):
            if kk in wlow and wlow[kk] not in W: W.append(wlow[kk])
            if kk in nlow and nlow[kk] not in Nn: Nn.append(nlow[kk])
    out[l['code']]={'label':l['label'],'W':W,'N':Nn}
    print(l['code'],l['label'],'| W:',[(w,wl[w]) for w in W],'| N:',[(n,nl[n]) for n in Nn])
json.dump(out,open('automatch.json','w'),ensure_ascii=False,indent=0)
