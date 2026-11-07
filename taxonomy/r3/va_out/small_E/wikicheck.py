"""Check that every en.wikipedia URL in result.json resolves to an existing article; print the missing ones."""
import json, os, re, urllib.parse, urllib.request, sys
HERE = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(HERE, "result.json")))
urls = set()
for c, v in res["leaves"].items():
    for k in v["kinds"]:
        m = re.search(r"https://en\.wikipedia\.org/wiki/(\S+)", str(k[3]))
        if m: urls.add(m.group(1))
titles = sorted(urllib.parse.unquote(u).replace("_", " ") for u in urls)
missing = []
for i in range(0, len(titles), 40):
    batch = titles[i:i + 40]
    u = "https://en.wikipedia.org/w/api.php?action=query&format=json&redirects=1&titles=" + urllib.parse.quote("|".join(batch))
    req = urllib.request.Request(u, headers={"User-Agent": "va-taxonomy-check/1.0"})
    d = json.load(urllib.request.urlopen(req, timeout=60))["query"]
    norm = {x["from"]: x["to"] for x in d.get("normalized", [])}
    for p in d["pages"].values():
        if "missing" in p or "invalid" in p: missing.append(p.get("title"))
print(len(titles), "titles checked;", len(missing), "missing")
for m in missing: print("MISSING", m)
