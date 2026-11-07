import re, sys, json, collections
sys.path.insert(0, __import__('os').path.dirname(__file__))
from files import SPEC, rows
KW = [l.strip() for l in open(sys.argv[1]) if l.strip()]
rx = [(k, re.compile(k, re.I)) for k in KW]
out = {k: collections.Counter() for k in KW}
for name in SPEC:
    for r, cult, typ in rows(name):
        for k, x in rx:
            if x.search(cult):
                key = (r.get(SPEC[name][0][0]) or '')[:70]
                out[k][name + ': ' + key] += 1
for k in KW:
    tot = sum(out[k].values())
    print('###', k, tot, '|', '; '.join(f'{a} ({b})' for a, b in out[k].most_common(10)))
