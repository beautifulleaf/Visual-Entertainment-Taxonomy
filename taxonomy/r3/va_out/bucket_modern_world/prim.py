import sys,csv
M={'Empire of Japan':'Japan','British Raj':'India','Dominion of India':'India',"People's Republic of China":'China','Republic of China':'China','Qing dynasty':'China','Taiwan':'Taiwan','Ottoman Empire':'Turkey'}
def prim(c):
    cs=[x.strip() for x in c.split(',') if x.strip()]
    if not cs: return '?'
    nonw=[x for x in cs if x not in ('France','United Kingdom','Germany','Spain','Switzerland','Italy','United Kingdom of Great Britain and Ireland','Kingdom of the Netherlands','Belgium','Austria','Kingdom of Italy','German Empire','Norway')]
    x=(nonw or cs)[0]
    return M.get(x,x)
if __name__=='__main__':
    want=sys.argv[1]
    rows=[l.rstrip('\n').split('\t') for l in open('dump.tsv')]
    sel=[r for r in rows if (prim(r[5])==want) == (not want.startswith('!'))] if not want.startswith('!') else [r for r in rows if prim(r[5]) not in want[1:].split('|')]
    sel.sort(key=lambda r:r[4])
    for r in sel:
        extra=' '.join(x for x in (r[2],r[7]) if x)
        med='' if r[6]=='painting' else r[6]
        print(f"{r[1]}|{r[4]}|{r[5] if prim(r[5])!=r[5] else ''}|{med}|{extra}")
