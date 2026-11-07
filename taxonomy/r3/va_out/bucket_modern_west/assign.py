import json,glob,collections as C,sys
d=json.load(open('../../va_in/bucket_modern_west.json'))
rows=d['leaves'][0]['rows']
names={r[0] for r in rows}
amap={};bad=[];dup=[]
for f in sorted(glob.glob('asg/*.txt')):
  for line in open(f):
    line=line.strip()
    if not line or line.startswith('#'): continue
    t,ns=line.split(' | ',1)
    for n in ns.split(';'):
      n=n.strip()
      if not n: continue
      if n not in names: bad.append((f,n))
      elif n in amap: dup.append((n,amap[n],t))
      else: amap[n]=t.strip()
if __name__=='__main__':
  print('assigned',len(amap),'of',len(names)); print('BAD',bad); print('DUP',dup)
  print(C.Counter(v.split('|')[0] for v in amap.values()).most_common())
