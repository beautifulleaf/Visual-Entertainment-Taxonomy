import csv,json,collections
d=json.load(open('../../va_in/bucket_print_arch_misc.json'))
E=list(csv.DictReader(open('../../../../data/interim/architecture_exemplars.csv')))
byS=collections.defaultdict(list)
for e in E: byS[e['style_label'].lower()].append(e)
def labels(l):
    s=set(a.lower() for a in l['alias_rows'])
    for r in l['rows']:
        if r[3]=='architecture_west' : s.add(r[0].lower())
    return s
if __name__=='__main__':
  for l in d['leaves']:
    if l['family']!='Architecture': continue
    ls=labels(l); tot=0; seen=set()
    parts=[]
    for x in sorted(ls):
        n=len(byS.get(x,[])); 
        for e in byS.get(x,[]): seen.add(e['qid'])
        parts.append(f"{x}:{n}")
    print(l['code'],l['label'],len(seen),' '.join(parts))
