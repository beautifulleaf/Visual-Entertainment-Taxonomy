import sys, json, urllib.request, urllib.parse, time
titles=[t.strip() for t in sys.stdin.read().split('\n') if t.strip()]
for i in range(0,len(titles),40):
    chunk=titles[i:i+40]
    url="https://en.wikipedia.org/w/api.php?action=query&format=json&redirects=1&titles="+urllib.parse.quote('|'.join(chunk))
    for a in range(5):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'taxonomy-check/1.0 (research)'})
            d=json.load(urllib.request.urlopen(req))['query']; break
        except Exception as e:
            time.sleep(15)
    norm={n['from']:n['to'] for n in d.get('normalized',[])}
    red={r['from']:r['to'] for r in d.get('redirects',[])}
    pages={p['title']:p for p in d['pages'].values()}
    for t in chunk:
        n=norm.get(t,t); r=red.get(n,n)
        p=pages.get(r)
        st='MISSING' if (p is None or 'missing' in p) else 'OK'
        print(f"{st}\t{t}\t{r if r!=t else ''}")
    time.sleep(3)
