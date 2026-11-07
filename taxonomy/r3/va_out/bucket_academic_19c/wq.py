import sys,json,urllib.request,urllib.parse,time
UA={'User-Agent':'VET-taxonomy-research/1.0 (contact: none)'}
def get(url):
    for i in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30))
        except Exception as e:
            time.sleep(2+i*3)
    return None
mode=sys.argv[1]
for s in sys.argv[2:]:
    if mode=='s':
        d=get('https://en.wikipedia.org/w/api.php?action=query&list=search&srlimit=4&format=json&srsearch='+urllib.parse.quote(s))
        print(s,'=>',[x['title'] for x in d['query']['search']] if d else 'ERR')
    else:
        d=get('https://en.wikipedia.org/w/api.php?action=query&redirects&format=json&titles='+urllib.parse.quote(s))
        if not d: print(s,'ERR'); continue
        q=d['query']; p=list(q['pages'].values())[0]
        print(s,'=>', 'MISSING' if 'missing' in p else p['title'], q.get('redirects',''))
    time.sleep(1)
