import csv,re,sys
W='work_sl_romance_musical_erotic_exp/'
R=list(csv.DictReader(open('in_sl_romance_musical_erotic_exp.csv')))
m={}
for f in ['c0','c1','c2','c3','fix']:
    for line in open(W+f+'.txt'):
        p=line.rstrip('\n').split(' ',3)
        if not p[0]: continue
        i=int(p[0]); leaf=p[1]; sec=''; note=''
        rest=p[2:]
        if rest and re.fullmatch(r'\d+',rest[0]): sec=rest[0]; note=' '.join(rest[1:])
        else: note=' '.join(rest)
        if leaf not in('out','NEW1') and not leaf[0].isalpha(): leaf='A'+leaf
        m[i]=(leaf,sec,note)
miss=[i for i in range(len(R)) if i not in m]; print('missing',miss)
with open('out_sl_romance_musical_erotic_exp.csv','w',newline='') as fh:
    w=csv.writer(fh); w.writerow(['id','leaf','sec','note'])
    for i,r in enumerate(R):
        l,s,n=m[i]; w.writerow([r['id'],l,s,n])
import collections; print(collections.Counter(v[0] for v in m.values())['NEW1'])
