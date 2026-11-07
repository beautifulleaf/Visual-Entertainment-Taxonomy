import csv, json, re, sys, collections, os
sys.path.insert(0, os.path.dirname(__file__))
from ov5 import O, put
put("29", "Rabbit Hole")
put("22.4", "Gannibal; The Village: Achiara's Secret; The Chalet; Happy Town")
put("4.3", "Happy Valley")
put("21.1", "Mouse")
put("22.5", "Reset")
put("1.2", "Gone")
put("26.4", "Below the Surface")
put("26.5", "RUN; Blood Sisters")
put("33", "The Head")
put("22.1", "Wanted")
exec(open(os.path.join(os.path.dirname(__file__), "ov6.py")).read()) if os.path.exists(os.path.join(os.path.dirname(__file__), "ov6.py")) else None
from leaves import LEAVES

ROOT = "/home/user/Visual-Entertainment-Taxonomy"
rows = list(csv.DictReader(open(ROOT + "/taxonomy/r3/ft_in/tv_crime_thriller.csv")))
titles = {r["title"] for r in rows} | {r["title"] + "@" + r["year"][:4] for r in rows}
unused = [k for k in O if k not in titles and not k.startswith("@")]

def kw(r): return (r["keywords"] + " " + r["overview"] + " " + r["wd_genre"]).lower()
def default(r):
    k = kw(r); ol = r["old_leaf"]
    if ol == "C3-1":
        if "forensic" in k or "pathologist" in k or "coroner" in k: return "3.1"
        if "fbi" in k or "special unit" in k or "task force" in k: return "1.3"
        if "profil" in k: return "1.4"
        if "cold case" in k or "cold-case" in k: return "1.5"
        if "undercover" in k or "corrupt" in k: return "1.6"
        if "time travel" in k or "supernatural" in k or "ghost" in k: return "1.7"
        if "partner" in k and "buddy" in k: return "2.1"
        return "1.2"
    if ol == "C3-2":
        if "private detective" in k or "private-detective" in k or "private investigator" in k or "private-investigator" in k: return "13.1"
        if "village" in k: return "10.1"
        return "8.4" if r["who"][:2] in ("JP", "KR", "CN", "TW") else "8.3"
    if ol == "C3-3":
        if "prison" in k: return "19"
        if "drug" in k or "cartel" in k or "narco" in k: return "16.1"
        if "heist" in k or "robbery" in k: return "17.1"
        if "con artist" in k or "con-artist" in k or "swindl" in k or "scam" in k: return "17.2"
        if "mafia" in k or "mob" in k: return "15.1"
        if "gang" in k: return "15.3"
        if "lawyer" in k or "court" in k or "trial" in k: return "14.1"
        if "hitman" in k or "assassin" in k or "contract killer" in k: return "18.3"
        return "18.1"
    if ol == "C3-4": return "5.1"
    if ol == "C3-5":
        if "cold war" in k: return "27.1"
        if "world war" in k: return "27.2"
        return "27.3"
    if ol == "C3-7":
        if "fraud" in k or "scam" in k: return "20.2"
        if "heist" in k or "robbery" in k: return "20.3"
        if "drug" in k or "gang" in k: return "20.4"
        return "20.1"
    if ol == "C3-8":
        if "neighbo" in k: return "23.4"
        if "affair" in k or "husband" in k or "wife" in k or "marriage" in k: return "23.1"
        return "23.2"
    # C3-6 thriller
    if "serial killer" in k or "serial-killer" in k: return "21.2"
    if "revenge" in k or "vengeance" in k: return "25.2"
    if "vigilante" in k: return "25.1"
    if "terroris" in k: return "26.1"
    if "hostage" in k or "hijack" in k: return "26.4"
    if "kidnap" in k or "missing" in k or "disappear" in k or "abduct" in k: return "22.1"
    if "hacker" in k or "hacking" in k or "artificial intelligence" in k: return "30"
    if "conspiracy" in k: return "29.2"
    if "politic" in k or "president" in k or "government" in k: return "28"
    if "high school" in k or "student" in k or "teenager" in k: return "32.1"
    if "game" in k and "death" in k: return "31"
    if "time" in k and ("loop" in k or "travel" in k): return "22.5"
    if "fugitive" in k or "on the run" in k: return "26.5"
    if "bodyguard" in k: return "26.3"
    if "stalk" in k or "obsess" in k: return "22.2"
    if "amnesia" in k or "memory" in k or "identity" in k: return "22.3"
    if "affair" in k or "marriage" in k or "husband" in k: return "23.1"
    if "murder" in k or "small town" in k or "village" in k: return "22.4"
    return "22.4?"

out = []
for r in rows:
    c = O.get(r["title"] + "@" + r["year"][:4]) or O.get(r["title"])
    src = "ov"
    if not c: c = default(r); src = "def"
    out.append((r, c, src))

if __name__ == "__main__":
    print("unused keys:", unused)
    mode = sys.argv[1] if len(sys.argv) > 1 else "list"
    by = collections.defaultdict(list)
    for r, c, s in out: by[c].append((r, s))
    def keyf(c):
        a = c.rstrip("?").replace("ROUTE:B8","99").split(".")
        return (int(a[0]), int(a[1]) if len(a) > 1 and a[1] else 0, c)
    for c in sorted(by, key=keyf):
        if mode == "def":
            items = [x for x in by[c] if x[1] == "def"]
            if not items: continue
            print(f"\n## {c} ({len(items)} default)")
            print("; ".join(f"{r['title']}@{r['year'][:4]} [{r['old_leaf'][3:]}] {r['overview'][:70]}" for r, s in items))
        else:
            print(f"\n## {c} ({len(by[c])})")
            print("; ".join(f"{r['title']}@{r['year'][:4]}{'*' if s=='def' else ''}" for r, s in by[c]))
