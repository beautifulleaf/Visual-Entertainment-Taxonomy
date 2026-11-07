import json,sys
d=json.load(open('../../va_in/bucket_print_arch_misc.json'))
for l in d['leaves']:
    if sys.argv[1]!=l['code']: continue
    for r in l['rows']:
        e=r[5] if len(r)>5 else {}
        print('\t'.join([r[0],r[1],str(r[4]),e.get('birth',''),e.get('countries','')[:40],e.get('movements','')[:60],r[2][:80]]))
