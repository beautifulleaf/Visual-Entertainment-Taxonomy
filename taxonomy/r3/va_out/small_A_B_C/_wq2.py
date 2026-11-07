import sys, json, subprocess, urllib.parse, time
lang=sys.argv[1]
titles=[l.strip() for l in sys.stdin if l.strip()]
q=urllib.parse.urlencode({"action":"query","titles":"|".join(titles),"format":"json","redirects":1})
for a in range(8):
    out=subprocess.run(["curl","-sS","-m","60","-A","VisualEntertainmentTaxonomy/0.1",f"https://{lang}.wikipedia.org/w/api.php?"+q],capture_output=True,text=True).stdout
    try: d=json.loads(out)["query"]; break
    except Exception: time.sleep(6*(a+1))
norm={n["from"]:n["to"] for n in d.get("normalized",[])}; red={n["from"]:n["to"] for n in d.get("redirects",[])}
ex={p["title"] for p in d["pages"].values() if "missing" not in p and "invalid" not in p}
for t in titles:
    t3=red.get(norm.get(t,t),norm.get(t,t)); print(('OK ' if t3 in ex else '-- ')+t)
