import csv
R=list(csv.DictReader(open('../in_sl_crime_thriller.csv')))
M={}
for f in ['c1.txt','c2.txt','c3.txt','c4.txt']:
    for ln in open(f,encoding='utf-8'):
        ln=ln.rstrip('\n')
        if not ln.strip(): continue
        p=ln.split(' ',3)
        i=int(p[0]); leaf=p[1]; sec=''; note=''
        rest=ln.split(' ',2)[2] if len(p)>2 else ''
        if rest.startswith('new:'):
            sec=rest  # whole remainder
        elif rest:
            a=rest.split(' ',1); s=a[0]; note=a[1] if len(a)>1 else ''
            if s=='-': s=''
            elif not s.isdigit(): note=rest; s=''
            sec=s
        assert i not in M,i
        M[i]=(leaf,sec,note)
miss=[i for i in range(len(R)) if i not in M]; print('missing',miss)
with open('../out_sl_crime_thriller.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['id','leaf','sec','note'])
    for i,r in enumerate(R):
        l,s,n=M[i]; w.writerow([r['id'],l,s,n])
