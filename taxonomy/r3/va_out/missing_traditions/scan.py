import csv,re
L=list(csv.DictReader(open('collections/va_leaves.tsv'),delimiter='\t'))
C=[r for r in csv.DictReader(open('collections/missing_candidates.csv')) if int(r['objects'])>=50]
stop=set('pottery ceramics ware textiles basketry beadwork painting sculpture carving manuscript illumination masks goldwork glass and the of figures lace embroidery'.split())
for c in C:
    toks=[t for t in re.findall(r"[\w'ʻāäéúíō]+",c['tradition'].lower()) if t not in stop and len(t)>2]
    hits=[]
    for l in L:
        txt=(l['label']+' '+l['aliases']+' '+l['defn']).lower()
        sc=sum(1 for t in toks if re.search(r'\b'+re.escape(t),txt))
        if sc: hits.append((sc, l['label'] in txt, l['code'],l['label']))
    hits.sort(key=lambda h:-h[0])
    print('##',c['tradition'],c['families'],c['objects'],'->',' ; '.join(f"{h[2]} {h[3]}" for h in hits[:6]))
