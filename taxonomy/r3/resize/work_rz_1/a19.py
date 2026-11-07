from common import *
import collections
R=rows('A19-1')
CL=['Wiseman','Maysles','Pennebaker','Hegedus','Drew','Leacock','Allan King','Depardon','Perrault','Brault','Rouch','Broomfield','Apted','Junge','Koenig']
def cls(r):
    if r['y']<=1989 or any(x in r['who'] for x in CL): return 'self'
    if r['sec'] in ('1','2','4'): return 'NEW1'
    if r['sec'] in ('3','5'): return 'NEW2'
    # unsectioned post-1990 non-classic
    return 'NEW1'
A={r['id']:cls(r) for r in R}
print(collections.Counter(A.values()))
for k in ('self','NEW1','NEW2'):
    print(k, collections.Counter((r['sec'], 'pre' if r['y']<2005 else 'post') for r in R if A[r['id']]==k))
