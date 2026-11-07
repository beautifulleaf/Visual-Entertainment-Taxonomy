import json,sys
d=json.load(open('../../va_in/small_K.json'))
for l in d['leaves']:
    if sys.argv[1:] and not any(l['code'].startswith(p) for p in sys.argv[1:]): continue
    arch=[r[0] for r in l['rows'] if r[1]=='Architects' or r[4]]
    print(f"## {l['code']} {l['label']} | aliases: {l['aliases'][:80]} | AR: {l['alias_rows']} | {len(arch)} archs")
    for r in l['rows']:
        if r[1]=='Architects' or r[4]: continue
        print(f"   {r[0][:60]} | {r[1]} | {r[2][:90]} | {r[3][:40]}")
