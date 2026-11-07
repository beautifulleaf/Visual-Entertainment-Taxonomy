import csv, re, os
D = os.path.dirname(os.path.abspath(__file__))
rows = []
for fn in ("add_sport.txt", "add_event.txt"):
    for line in open(os.path.join(D, fn), encoding="utf-8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"): continue
        f = (line.split("|") + [""] * 8)[:8]
        t, y, who, lf, sec, see, note, i = f
        if re.fullmatch(r"(Q\d+|tt\d+)", note.strip()): i, note = note.strip(), ""
        rows.append({"id": i.strip(), "title": t, "year": y, "who": who, "leaf": "B16-" + lf.strip(), "sec": sec.strip(), "see_also": see.strip(), "note": note.strip()})
w = csv.DictWriter(open(os.path.join(D, "additions.csv"), "w", newline="", encoding="utf-8"), fieldnames=["id","title","year","who","leaf","sec","see_also","note"])
w.writeheader(); w.writerows(rows)
from collections import Counter
c = Counter(r["title"] for r in rows); print(len(rows), [k for k,v in c.items() if v>1])
