import json, urllib.parse, urllib.request, time, sys
ts=[l.strip() for l in sys.stdin if l.strip()]
for i in range(0,len(ts),45):
    b=ts[i:i+45]
    q='https://en.wikipedia.org/w/api.php?action=query&format=json&formatversion=2&redirects=1&titles='+urllib.parse.quote('|'.join(b))
    req=urllib.request.Request(q,headers={'User-Agent':'VETaxonomyCheck/1.0 (taxonomy research; low volume)'})
    for a in range(12):
        try: d=json.load(urllib.request.urlopen(req,timeout=30)); break
        except Exception as e: time.sleep(15)
    else: print('FAILED batch'); continue
    norm={x['from']:x['to'] for x in d['query'].get('normalized',[])}
    red={x['from']:x['to'] for x in d['query'].get('redirects',[])}
    pages={p['title']:('missing' not in p) for p in d['query']['pages']}
    for t in b:
        t2=norm.get(t,t); t3=red.get(t2,t2); print(('OK ' if pages.get(t3) else 'NO ')+t+(' -> '+t3 if t3!=t else ''))
    time.sleep(5)
