import json, urllib.parse, urllib.request, time, re
r=json.load(open('../result.json'))
titles=set()
for c,v in r['leaves'].items():
    for k in v['kinds']:
        m=re.match(r'r3 https://en\.wikipedia\.org/wiki/(.+)$',k[3])
        if m: titles.add(urllib.parse.unquote(m.group(1)).replace('_',' '))
    for cat in v['catalogues']:
        m=re.match(r'https://en\.wikipedia\.org/wiki/(.+)$',cat[0])
        if m: titles.add(urllib.parse.unquote(m.group(1)).replace('_',' '))
titles=sorted(titles); print(len(titles))
res={}
for i in range(0,len(titles),50):
    b=titles[i:i+50]
    q='https://en.wikipedia.org/w/api.php?action=query&format=json&formatversion=2&redirects=1&titles='+urllib.parse.quote('|'.join(b))
    req=urllib.request.Request(q,headers={'User-Agent':'VETaxonomyCheck/1.0 (taxonomy research)'})
    for attempt in range(5):
        try: d=json.load(urllib.request.urlopen(req,timeout=30)); break
        except Exception as e: print('retry',e); time.sleep(10)
    norm={x['from']:x['to'] for x in d['query'].get('normalized',[])}
    red={x['from']:x['to'] for x in d['query'].get('redirects',[])}
    pages={p['title']:('missing' not in p) for p in d['query']['pages']}
    for t in b:
        t2=norm.get(t,t); t3=red.get(t2,t2)
        res[t]={'exists':pages.get(t3,False),'target':t3}
    time.sleep(1.5)
json.dump(res,open('wikicheck.json','w'),ensure_ascii=False,indent=0)
miss=[t for t,v in res.items() if not v['exists']]
print('missing',len(miss)); print(miss)
red=[(t,v['target']) for t,v in res.items() if v['exists'] and v['target']!=t]
print('redirects',len(red)); print(red)
