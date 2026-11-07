import csv,sys,re
R='/home/user/Visual-Entertainment-Taxonomy/'
csv.field_size_limit(10**9)
placed={}
for r in csv.DictReader(open(R+'taxonomy/r3/ft_title_index.tsv'),delimiter='\t'): placed.setdefault(r['title'].lower(),[]).append(r)
cand=list(csv.DictReader(open(R+'data/interim/tv_candidates.csv')))
rat={r['tconst']:r for r in csv.DictReader(open(R+'data/interim/tv_ratings.csv'))}
pid={}
for r in csv.DictReader(open(R+'taxonomy/r3/ft_title_index.tsv'),delimiter='\t'): pid[r['id']]=r
def n(s): return re.sub(r'[^a-z0-9]','',s.lower())
for q in sys.argv[1:]:
    nq=n(q); out=[]
    for r in cand:
        if n(r['title'])==nq or n(r['original_title'])==nq:
            p=pid.get(r['tconst']); c=rat.get(r['tconst'],{}).get('country','')
            out.append((int(r['imdb_votes'] or 0),f"{r['tconst']}|{r['title']}|{r['start_year']}|{c}|{r['genres']}|v{r['imdb_votes']}|{'PLACED '+p['leaf'] if p else ''}"))
    out.sort(reverse=True)
    pl=[f"{p['id']} {p['leaf']}" for p in placed.get(q.lower(),[]) if not p['id'].startswith('tt')]
    print(q,'=>',' ;; '.join(x[1] for x in out[:3]) or 'NONE', pl if pl else '')
