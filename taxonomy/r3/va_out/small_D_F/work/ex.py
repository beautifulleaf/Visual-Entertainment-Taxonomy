import pandas as pd, sys, re
A=pd.read_pickle('/home/user/Visual-Entertainment-Taxonomy/taxonomy/r3/va_out/small_D_F/work/all.pkl')
for pat in sys.argv[1:]:
    p,_,t=pat.partition('@@')
    m=A.ck.str.contains(p,case=False,regex=True)
    if t: m&=(A.ot+' '+A.title+' '+A.mat).str.contains(t,case=False,regex=True)
    S=A[m]
    print(f'=== {pat}: {len(S)}', dict(S.f.value_counts()))
    print('  ck:', '; '.join(f'{a[:70]}={b}' for a,b in S.ck.value_counts().head(8).items()))
    print('  ot:', '; '.join(f'{a[:40]}={b}' for a,b in S.ot.value_counts().head(6).items()))
    print('  inst:', '; '.join(f'{a[:40]}={b}' for a,b in S.inst.value_counts().head(8).items()))
