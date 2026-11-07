import csv,gzip,random,collections
keys={}
inp=list(csv.DictReader(open('in_col_ABJ.csv')))
for i,r in enumerate(inp): keys[(r['file'],r['label'],r['family'])]=i
S=collections.defaultdict(list); N=collections.Counter()
random.seed(1)
for r in csv.DictReader(gzip.open('objects_norm.csv.gz','rt')):
    k=(r['file'],r['label'],r['family'])
    if k in keys:
        i=keys[k]; N[i]+=1
        if len(S[i])<5: S[i].append(r['title'][:28])
        elif random.random()<5/N[i]: S[i][random.randrange(5)]=r['title'][:28]
with open('work_col_ABJ/view2.txt','w') as f:
    for i,r in enumerate(inp):
        ti=r['top_institutions'].split(' (')[0][:22]
        f.write(f"{i}|{r['file'][:6]}|{r['label'][:60]}|{r['family']}|{r['objects']}|{ti}|{' / '.join(set(S[i]))}|{r['seed']}\n")
