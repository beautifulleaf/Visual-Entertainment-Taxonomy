import sys, json, subprocess, urllib.parse, time
titles=[l.strip() for l in sys.stdin if l.strip()]
res={}
for i in range(0,len(titles),50):
    ch=titles[i:i+50]
    q=urllib.parse.urlencode({"action":"query","titles":"|".join(ch),"format":"json","redirects":1})
    for a in range(6):
        out=subprocess.run(["curl","-sS","-m","60","-A","VisualEntertainmentTaxonomy/0.1","https://en.wikipedia.org/w/api.php?"+q],capture_output=True,text=True).stdout
        try: d=json.loads(out)["query"]; break
        except Exception: time.sleep(5*(a+1))
    norm={n["from"]:n["to"] for n in d.get("normalized",[])}; red={n["from"]:n["to"] for n in d.get("redirects",[])}
    ex={p["title"] for p in d["pages"].values() if "missing" not in p and "invalid" not in p}
    for t in ch:
        t3=red.get(norm.get(t,t),norm.get(t,t)); res[t]=t3 in ex
    time.sleep(0.5)
for t in titles: print(('OK ' if res[t] else '-- ')+t)
