import pickle, re, sys, collections
D = pickle.load(open("cache.pkl", "rb"))
for pat in sys.argv[1:]:
    p = re.compile(pat, re.I)
    m = [r for r in D if p.search(r[2] + " | " + r[1])]
    print("=====", pat, len(m))
    print("  src", collections.Counter(r[0] for r in m).most_common(8))
    print("  inst", collections.Counter(r[4] for r in m).most_common(8))
    for r in m[:: max(1, len(m)//6)][:6]: print("   ", r[1][:60], "||", r[2][:150], "||", r[3])
