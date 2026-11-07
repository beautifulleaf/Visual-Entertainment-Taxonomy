import pandas as pd, re, pickle, sys
sys.path.insert(0,'/home/user/Visual-Entertainment-Taxonomy/taxonomy/r3/va_out/small_D_F/work')
from pats import P
W='/home/user/Visual-Entertainment-Taxonomy/taxonomy/r3/va_out/small_D_F/work/'
A=pd.read_pickle(W+'all.pkl')
T=(A.ot+' | '+A.title+' | '+A.mat)
res={}
only=sys.argv[1:]
for c,(ck,tp,ex) in P.items():
    if only and c not in only: continue
    if not ck and not tp: res[c]=A.iloc[0:0]; continue
    m=pd.Series(True,index=A.index)
    if ck: m&=A.ck.str.contains(ck,case=False,regex=True)
    if tp: m&=T.str.contains(tp,case=False,regex=True)
    if ex: m&=~A.ck.str.contains(ex,case=False,regex=True)
    res[c]=A[m].copy()
    S=res[c]
    print(c,len(S),dict(S.f.value_counts()),'|',', '.join(f'{a[:30]}={b}' for a,b in S.inst.value_counts().head(4).items()),flush=True)
if not only: pickle.dump(res,open(W+'matches.pkl','wb'))
