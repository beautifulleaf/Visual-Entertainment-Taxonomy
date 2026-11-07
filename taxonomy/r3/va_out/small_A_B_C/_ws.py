import sys, json, subprocess, urllib.parse, time, ast
items=[ast.literal_eval(l) for l in open('_missing.txt') if l.strip()]
for it in items:
    q=it[2] if len(it)>2 else it[1].split('/wiki/')[1].replace('_',' ')
    u="https://en.wikipedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","list":"search","srsearch":q,"srlimit":3,"format":"json"})
    out=subprocess.run(["curl","-sS","-m","30","-A","VisualEntertainmentTaxonomy/0.1","%s"%u],capture_output=True,text=True).stdout
    try: hits=[h['title'] for h in json.loads(out)['query']['search']]
    except Exception: hits=['ERR']
    print(it[0], '|', q, '=>', hits)
    time.sleep(0.3)
