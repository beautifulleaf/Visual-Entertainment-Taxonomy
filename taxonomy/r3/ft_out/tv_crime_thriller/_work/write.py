import csv, json, sys, os, collections
sys.argv = ["x", "none"]
import run
from leaves import LEAVES
OD = "/home/user/Visual-Entertainment-Taxonomy/taxonomy/r3/ft_out/tv_crime_thriller"
import re
from leaves import POLICE_DRAMA
def shift(t): return re.sub(r"B7-(\d+)", lambda m: "B7-%d" % (int(m.group(1)) + (1 if int(m.group(1)) >= 2 else 0)), t)
L2 = [LEAVES[0], POLICE_DRAMA] + LEAVES[1:]
for l in L2[2:]:
    l["defn"] = shift(l["defn"]); l["see"] = shift(l["see"])
leaves = []
for i, l in enumerate(L2, 1):
    d = {"code": f"B7-{i}", "label": l["label"], "breadth": l["breadth"], "defn": l["defn"], "aliases": l["aliases"], "see": l["see"], "src": l["src"]}
    if l.get("secs"): d["axis"] = l["axis"]; d["secs"] = l["secs"]
    leaves.append(d)
json.dump({"subs": [{"code": "B7", "label": "Crime & Thriller Series",
  "axis": "Axis: by the series' engine, from who investigates (police, detectives, sleuths, lawyers), to who commits the crime (gangs, dealers, crews, antiheroes, real criminals), to what threatens the protagonist (killers, minds, households, avengers, agents, states, games)",
  "leaves": leaves}]}, open(OD + "/leaves.json", "w"), ensure_ascii=False, indent=1)
SEEALSO = {"Only Murders in the Building": "B8", "Psych": "B8", "Dirk Gently's Holistic Detective Agency": "B9", "Lucifer": "B9", "Forever": "B9",
  "Squid Game": "B9", "Alice in Borderland": "B9", "Riverdale": "B1", "Breaking Bad": "B7-18", "Justified": "B7-18", "Babylon Berlin": "B7-1",
  "Peaky Blinders": "B7-11", "Narcos": "B7-16", "Mindhunter": "B7-21", "MINDHUNTER": "B7-21", "Dexter": "B7-1", "Killing Eve": "B7-21",
  "Prison Break": "B7-26", "Bodyguard": "B7-28", "Homeland": "B7-28", "Line of Duty": "B7-29", "True Detective": "B7-4", "Fargo": "B7-18"}
w = csv.writer(open(OD + "/assign.csv", "w", newline=""))
w.writerow(["id", "leaf", "sec", "see_also", "note", "route"])
cnt = collections.Counter()
for r, c, s in run.out:
    c = c.rstrip("?")
    if c.startswith("ROUTE:"):
        w.writerow([r["id"], "", "", "", "sitcom, not a crime series", c[6:]]); continue
    a = c.split(".")
    n = int(a[0]); sec = a[1] if len(a) > 1 else ""
    if n == 1:
        if sec in ("1", "6"): n = 2; sec = {"1": "1", "6": "2"}[sec]
        else: sec = {"2": "1", "3": "2", "4": "3", "5": "4", "7": "5"}[sec]
    else: n += 1
    leaf = "B7-%d" % n
    L = L2[n - 1]
    assert bool(L.get("secs")) == bool(sec), (r["title"], c)
    w.writerow([r["id"], leaf, sec, shift(SEEALSO.get(r["title"], "")), r["note"][:120], ""])
    cnt[c] += 1
