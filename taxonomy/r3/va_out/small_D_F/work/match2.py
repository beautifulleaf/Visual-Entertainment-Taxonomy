import pandas as pd, re, pickle, sys
sys.path.insert(0,'/home/user/Visual-Entertainment-Taxonomy/taxonomy/r3/va_out/small_D_F/work')
from pats import P, X
W='/home/user/Visual-Entertainment-Taxonomy/taxonomy/r3/va_out/small_D_F/work/'
A=pd.read_pickle(W+'all.pkl')
T=(A.ot+' | '+A.title+' | '+A.mat); T2=(A.ot+' | '+A.title)
D=pd.to_numeric(A.date,errors='coerce')
res=pickle.load(open(W+'matches.pkl','rb'))
for c in sys.argv[1:]:
    v=P[c]; o=X.get(c,{})
    ck=o.get('ck',v[0]); tp=o.get('tp',v[1]); ex=o.get('ex',v[2]); tx=o.get('tx',v[3] if len(v)>3 else '')
    if not ck and not tp: res[c]=A.iloc[0:0]; print(c,0); continue
    m=pd.Series(True,index=A.index)
    if o.get('fx'): m&=~A.f.isin(o['fx'])
    if ck: m&=A.ck.str.contains(ck,case=False,regex=True)
    TT=T2 if o.get('tonly') else T
    if tp: m&=TT.str.contains(tp,case=False,regex=True)
    if ex: m&=~A.ck.str.contains(ex,case=False,regex=True)
    if tx: m&=~T.str.contains(tx,case=False,regex=True)
    if 'dmin' in o: m&=D>=o['dmin']
    if 'dmax' in o: m&=D<=o['dmax']
    res[c]=A[m].copy(); S=res[c]
    print(c,len(S),dict(S.f.value_counts()),'|',', '.join(f'{a[:30]}={b}' for a,b in S.inst.value_counts().head(4).items()),flush=True)
pickle.dump(res,open(W+'matches.pkl','wb'))
