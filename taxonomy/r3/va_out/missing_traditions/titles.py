import gzip,sys
want=set(l.strip().replace(' ','_') for l in open(sys.argv[1]) if l.strip())
found=set()
with gzip.open('/home/user/Visual-Entertainment-Taxonomy/data/enwiki-all-titles-in-ns0.gz','rt',encoding='utf-8',errors='replace') as f:
    for line in f:
        t=line.rstrip('\n')
        if t in want: found.add(t)
for w in sorted(want): print('OK ' if w in found else 'NO ', w)
