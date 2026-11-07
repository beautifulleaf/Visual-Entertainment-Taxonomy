import json,urllib.parse,urllib.request,sys,time,subprocess
d=json.load(open("../result.json"))
urls=set()
for nl in d["new_leaves"]:
    for k in nl["kinds"]:
        if "wikipedia.org/wiki/" in k[3]: urls.add(k[3].split()[-1])
    for s in nl["src"]: urls.add(s[0])
titles=sorted({urllib.parse.unquote(u.split("/wiki/")[1]) for u in urls if "wikipedia" in u})
bad=[]
for i in range(0,len(titles),50):
    q="|".join(titles[i:i+50])
    u="https://en.wikipedia.org/w/api.php?action=query&format=json&redirects=1&prop=pageprops&ppprop=disambiguation&titles="+urllib.parse.quote(q)
    for a in range(8):
        time.sleep(4+a*5); t=subprocess.run(["curl","-s","-A","TaxonomyCheck/1.0 (research)",u],capture_output=True,text=True).stdout
        if t.startswith("{"): break
    r=json.loads(t)
    for x in r["query"].get("redirects",[]): print("REDIR",x["from"],"->",x["to"])
    for p in r["query"]["pages"].values():
        if "missing" in p or "invalid" in p or "pageprops" in p: bad.append(p.get("title"))
print(len(titles),"bad:",bad)
