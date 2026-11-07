import csv, re, sys, collections, json
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import als_leaves as leaves
csv.field_size_limit(10**9)
ROOT = "/home/user/Visual-Entertainment-Taxonomy/"
B = "anime_life_sports_drama_comedy"
rows = list(csv.DictReader(open(ROOT + f"taxonomy/r3/ft_in/{B}.csv")))
out, CODE = leaves.build()
SECS = {}
for s in out["subs"]:
    for l in s["leaves"]: SECS[l["code"]] = l.get("secs", [])

# title-regex rules: (regex, key, sec, see_also, note)  -- first match wins
R = []
def r(rx, key, sec=0, see="", note=""): R.append((re.compile(rx, re.I), key, sec, see, note))
exec(open(__file__.rsplit('/', 1)[0] + "/als_rules.py").read())

def tags(x): return set(k for k in x["keywords"].split("|") if k[:1].isupper())
def gen(x): return set(x["genres"].split("|"))

def fallback(x):
    t, g, ol = tags(x), gen(x), x["old_leaf"]
    H = lambda *a: any(k in t for k in a)
    if ol == "E6-1":
        if H("Animals"): return "iyashikei", 3
        if H("Travel", "Camping", "Outdoor Activities", "Motorcycles"): return "iyashikei", 4
        if H("Post-Apocalyptic", "Isekai", "Magic", "Witch", "Ghost", "Youkai", "Elf") or "Fantasy" in g or "Sci-Fi" in g or "Supernatural" in g: return "iyashikei", 2
        return "iyashikei", 1
    if ol == "E6-2":
        if H("Military", "Tanks", "Ships", "Guns", "Robots"): return "cgdct", 5
        if H("Nekomimi", "Kemonomimi") or "Ecchi" in g: return "cgdct", 6
        if "Fantasy" in g or "Supernatural" in g: return "cgdct", 4
        if H("Work", "Restaurant"): return "cgdct", 3
        if H("School Club", "Outdoor Activities", "Fishing", "Board Game", "Astronomy", "Drawing", "Motorcycles", "Mountaineering"): return "cgdct", 2
        return "cgdct", 1
    if ol == "E6-4":
        if H("Male Harem", "Cute Boys Doing Cute Things"): return "idol", 2
        if H("Zombie", "Ghost", "Magic", "Surreal Comedy", "Parody") or "Supernatural" in g or "Fantasy" in g: return "idol", 3
        return "idol", 1
    if ol == "E6-5":
        if H("Classical Music"): return "music", 3
        if H("Band", "Rock Music", "Metal Music"): return "music", 1
        return "music", 4
    if ol == "E6-6": return "food", 0
    if ol == "E6-7": return "perform", 0
    if ol == "E6-3":
        if H("Work"): return "work", 1
        if H("Family Life", "Parenthood", "Adoption"): return "family", 0
        if H("Monster Girl"): return "monster", 0
        return "cgdct", 1
    if ol in ("E7-1", "E7-2"):
        if H("Baseball"): return "baseball", 0
        if H("Football"): return "football", 1
        if H("American Football", "Rugby"): return "football", 2
        if H("Basketball"): return "basketball", 0
        if H("Volleyball"): return "volleyball", 0
        if H("Tennis", "Badminton", "Table Tennis"): return "racket", 0
        if H("Boxing", "Wrestling", "Judo", "Sumo", "Martial Arts"): return "combat", 0
        if H("Cycling"): return "racing", 3
        if H("Cars", "Motorcycles"): return "racing", 1
        if H("Swimming", "Surfing", "Scuba Diving"): return "swim", 0
        if H("Ice Sports"): return "ice", 0
        if H("Kemonomimi") and H("Athletics"): return "horse", 0
        if H("Archery", "Golf"): return "individual", 3
        if H("Cheerleading", "Acrobatics", "Dancing"): return "individual", 2
        if H("Skateboarding", "Parkour"): return "individual", 4
        if H("Airsoft", "Tanks", "Guns"): return "individual", 5
        if H("Athletics", "Fitness"): return "individual", 1
        if H("Go", "Shogi"): return "board", 1
        if H("Karuta"): return "board", 2
        if H("Mahjong"): return "board", 3
        if H("Card Battle"): return "card", 0
        if H("E-Sports", "Video Games"): return "esports", 0
        return "individual", 1
    if ol == "E8-1":
        if H("Death Game", "Battle Royale"): return "deathgame", 2
        if H("Gambling"): return "deathgame", 1
        if H("Dissociative Identities", "Memory Manipulation", "Amnesia"): return "psych", 2
        if H("Conspiracy", "Terrorism") or "Sci-Fi" in g: return "psych", 3
        if H("Coming of Age", "Bullying", "Primarily Teen Cast"): return "psych", 4
        return "psych", 1
    if ol == "E8-2":
        if H("Ghost", "Demons", "Magic", "Gods", "Vampire", "Youkai") or "Supernatural" in g: return "mystery", 4
        if H("Historical", "Ancient China"): return "mystery", 5
        if "Sci-Fi" in g or H("Police"): return "mystery", 6
        if H("School", "School Club"): return "mystery", 2
        return "mystery", 3
    if ol == "E8-4":
        if H("War", "Military"): return "war", 2
        if H("Ancient China") or x["who"] in ("CN",): return "historical", 2
        if H("Foreign"): return "historical", 3
        return "historical", 1
    if ol == "E8-5":
        if H("Police"): return "crime", 3
        if H("Mafia", "Gangs", "Yakuza", "Assassins", "Triads"): return "crime", 2
        return "crime", 1
    if ol == "E8-6":
        if H("Gambling"): return "deathgame", 1
        return "deathgame", 2
    if ol == "E8-7": return "art", 0
    if ol == "E8-3": return "coming", 1
    if ol == "E9-1":
        if H("Vampire"): return "vampire", 0
        if H("Zombie"): return "zombie", 0
        if H("Body Horror", "Cosmic Horror", "Ero Guro", "Gore"): return "body", 0
        if H("Rural"): return "folk", 0
        if "Comedy" in g: return "comhorror", 0
        if H("Anthology", "Episodic"): return "ghost", 1
        if H("School"): return "ghost", 2
        if H("Revenge", "Curses"): return "ghost", 3
        return "ghost", 4
    if ol == "E10-2":
        if H("Female Harem"):
            if H("Aliens") or "Sci-Fi" in g: return "harem", 2
            if H("Demons", "Vampire", "Youkai", "Gods", "Angels", "Ghost", "Monster Girl", "Zombie", "Succubus") or "Supernatural" in g: return "harem", 1
            if "Fantasy" in g or "Action" in g: return "harem", 3
            return "harem", 4
        if "Sports" in g: return "ecchi", 4
        if "Action" in g: return "ecchi", 1
        if H("POV", "Feet") or "Comedy" not in g: return "ecchi", 3
        return "ecchi", 2
    if ol.startswith("E10"):
        if H("Chibi") and not H("Surreal Comedy"): return "spinoff", 1
        if H("Parody"): return "parody", 2
        if "Supernatural" in g or "Fantasy" in g: return "fantasy", 1
        if "Sci-Fi" in g: return "scifi", 0
        if H("School", "School Club"): return "school", 2
        if H("Work"): return "work", 2
        if "Action" in g: return "action", 1
        return "gag", 1 if H("Surreal Comedy") else 2
    if ol == "E11-1":
        if H("Proxy Battle", "Card Battle", "Creature Taming"): return "toy", 0
        if H("Animals", "Primarily Animal Cast"): return "kodomo", 2
        if "Fantasy" in g or "Adventure" in g or "Sci-Fi" in g: return "kodomo", 3
        return "kodomo", 1
    if ol == "E11-2": return "wmt", 0
    if ol == "E11-3": return "early", 0
    raise Exception(ol)

def classify(x):
    hit = None
    for rx, key, sec, see, note in R:
        if rx.search(x["title"]): hit = (key, sec, see, note)
    if hit: return hit
    k, s = fallback(x)
    return k, s, "", ""

def subsec(x, k, s):
    t, g = tags(x), gen(x); H = lambda *a: any(z in t for z in a)
    if k == "fantasy" and s in (0, 1):
        if H("Isekai", "Video Games", "Dungeon", "Medieval", "Elf", "Reincarnation"): s = 3
        elif H("Vampire", "Youkai", "Ghost", "Mythology", "Afterlife") and not H("Demons"): s = 2
        elif H("Witch") or (H("Magic") and not H("Demons", "Gods", "Angels")): s = 4
        else: s = 1
    if k == "scifi" and s == 0:
        if H("Space"): s = 3
        elif H("Aliens"): s = 1
        elif H("Robots", "Artificial Intelligence", "Medicine", "Cyborg"): s = 2
        else: s = 4
    if k == "family" and s == 0:
        if "Fantasy" in g or "Supernatural" in g or "Sci-Fi" in g or H("Witch", "Magic"): s = 3
        elif H("Parenthood", "Adoption", "Found Family", "Age Gap", "Maids", "Primarily Child Cast") and not H("Twins"): s = 1
        else: s = 2
    return k, s

res = []
for x in rows:
    o = OVR.get(x["id"])
    if o is not None:
        k, s, see, note = (list(o) + ["", "", ""])[:4] if isinstance(o, tuple) else (o, 0, "", "")
    else:
        k, s, see, note = classify(x)
    k, s = subsec(x, k, s)
    route = ""
    if k.startswith("ROUTE:"):
        route = k[6:]; leaf = ""; s = 0
    else:
        leaf = CODE[k]
        if SECS[leaf]:
            if not s: s = 1
        else: s = 0
    see = " ".join(CODE.get(z, z) for z in see.split()) if see else ""
    if not note and x["note"] and not route: note = x["note"]
    res.append(dict(id=x["id"], leaf=leaf, sec=str(s) if s else "", see_also=see, note=note, route=route, title=x["title"], old=x["old_leaf"]))

if __name__ == "__main__":
    od = ROOT + f"taxonomy/r3/ft_out/{B}/"
    json.dump(out, open(od + "leaves.json", "w"), indent=1, ensure_ascii=False)
    with open(od + "assign.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "leaf", "sec", "see_also", "note", "route"], extrasaction="ignore")
        w.writeheader(); w.writerows(res)
    with open(__file__.rsplit('/', 1)[0] + "/review.txt", "w") as f:
        for z in sorted(res, key=lambda z: (z["leaf"], z["sec"], z["title"])):
            f.write(f"{z['leaf']}|{z['sec']}|{z['route']}|{z['id']}|{z['title'][:50]}|{z['old']}\n")
    print("written", len(res))
