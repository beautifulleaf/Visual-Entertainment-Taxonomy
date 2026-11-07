import sys; from lib import *
# usage: chk.py "Title|year" ...  or file with lines Title|year
args=sys.argv[1:]
if len(args)==1 and os.path.exists(args[0]): args=[l.strip() for l in open(args[0]) if l.strip()]
for a in args:
    t,_,y=a.partition("|")
    tc=lk(t.strip(), y.strip() or None)
    if tc:
        i=INFO[tc]; print(f"{t[:40]:40} {y:5} {tc:11} {i['title'][:35]:35} {i['year']} lb={i['lb']} {where(tc)}")
    else: print(f"{t[:40]:40} {y:5} --")
