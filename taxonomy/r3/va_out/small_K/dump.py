import json,sys
d=json.load(open('../../va_in/small_K.json'))
for l in d['leaves']:
    if sys.argv[1:] and not any(l['code'].startswith(p) for p in sys.argv[1:]): continue
    print(f"## {l['code']} {l['label']} | defn: {l['defn'][:200]} | aliases: {l['aliases'][:100]} | alias_rows: {l['alias_rows']}")
    for r in l['rows']:
        print(f"   {r[0][:60]} | {r[1]} | {r[2][:110]} | {r[3][:50]} | {r[4]}")
