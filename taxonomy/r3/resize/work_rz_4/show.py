import json,sys;d=json.load(open('taxonomy/r3/resize/in_rz_4.json'))
l=[x for x in d['leaves'] if x['code']==sys.argv[1]][0]
for t in sorted(l['titles'],key=lambda t:(t['sec'],t['year'] or 0)): print(t['id'],t['sec'],t['title'][:38],t['year'],t['who'][:16],t['country'][:10],t['note'][:25],sep='|')
