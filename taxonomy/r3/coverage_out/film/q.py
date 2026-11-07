import sys; from lib import *
for a in sys.argv[1:]:
    if a.startswith("d:"): show(bydir(a[2:]))
    else: print("##", a); show(search(a))
