import csv,gzip,collections,pickle,re
keys={(r['file'],r['label'],r['family']) for r in csv.DictReader(open('in_col_GI.csv'))}
T=collections.defaultdict(collections.Counter)
for r in csv.DictReader(gzip.open('objects_norm.csv.gz','rt')):
    k=(r['file'],r['label'],r['family'])
    if k in keys:
        t=re.sub(r'\s*\((Image withheld|No image)[^)]*\)','',r['title']).strip().lower()
        T[k][t[:40]]+=1
pickle.dump(dict(T),open('work_col_GI/titles.pkl','wb'))
print(len(T))
