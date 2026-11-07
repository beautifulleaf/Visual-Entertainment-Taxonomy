"""Lookup helpers for the film coverage pass."""
import csv, os, re, unicodedata, collections, sys
csv.field_size_limit(10**9)
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
I = os.path.join(R, "data/interim")
T = os.path.join(R, "taxonomy/r3")

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = s.replace("&", "and")
    s = re.sub(r"^(the|a|an|la|le|les|il|el|der|die|das) ", "", s)
    return re.sub(r"[^a-z0-9]", "", s)

LEAVES = {r["code"]: r for r in csv.DictReader(open(f"{T}/ft_leaf_index.tsv"), delimiter="\t")}
PLACED = {r["id"]: r for r in csv.DictReader(open(f"{T}/ft_title_index.tsv"), delimiter="\t")}
INFO = {}   # tconst -> dict(title, year, votes, lb, country, dir)
BYT = collections.defaultdict(set)

def _add(tc, title, year, **kw):
    if not tc: return
    d = INFO.setdefault(tc, {"title": title, "year": year, "votes": 0, "lb": 0, "country": "", "dir": ""})
    for k, v in kw.items():
        if v and not d.get(k): d[k] = v
    if title: BYT[norm(title)].add(tc)

for r in csv.DictReader(open(f"{I}/film_candidates.csv")):
    _add(r["tconst"], r["title"], r["year"], votes=int(r["imdb_votes"] or 0))
    if r["original_title"]: BYT[norm(r["original_title"])].add(r["tconst"])
for f in ("film_ratings.csv", "film_candidates_extra.csv"):
    for r in csv.DictReader(open(f"{I}/{f}")):
        tc = r["tconst"]
        if not tc.startswith("tt"): continue
        _add(tc, r["mdblist_title"], r["year"], country=r["country"])
        try: INFO[tc]["lb"] = max(INFO[tc]["lb"], int(float(r["letterboxd_votes"] or 0)))
        except ValueError: pass
        if not INFO[tc]["votes"]:
            try: INFO[tc]["votes"] = int(float(r["imdb_votes"] or 0))
            except ValueError: pass
TSP = collections.defaultdict(set)
for r in csv.DictReader(open(f"{T}/tspdt/entries.csv")):
    tc = r["tconst"]
    if not tc: continue
    _add(tc, r["title"], r["year"], dir=r["director"], country=r["country"])
    TSP[tc].add(r["list_id"])
for tc, r in PLACED.items():
    _add(tc, r["title"], r["year"], dir=r["who"])

def where(tc):
    return PLACED[tc]["leaf"] if tc in PLACED else ("pool" if tc in INFO else "?")

def lk(title, year=None, d=None):
    """best tconst for title/year (year ±1)."""
    c = BYT.get(norm(title), set())
    res = []
    for tc in c:
        i = INFO[tc]
        try: y = int(i["year"])
        except (ValueError, TypeError): y = None
        if year and y and abs(y - int(year)) > 1: continue
        if d and i["dir"] and norm(d.split()[-1]) not in norm(i["dir"]): continue
        res.append((tc in PLACED, i["lb"] + i["votes"], tc))
    res.sort(reverse=True)
    return res[0][2] if res else None

def show(tcs):
    for tc in tcs:
        i = INFO.get(tc, {})
        print(f"{tc}\t{i.get('title')}\t{i.get('year')}\t{i.get('dir','')[:30]}\t{i.get('country')}\tlb={i.get('lb')}\tv={i.get('votes')}\t{where(tc)}\ttspdt={len(TSP.get(tc,()))}")

def bydir(name, minyear=0, maxyear=9999):
    n = norm(name)
    out = [tc for tc, i in INFO.items() if i["dir"] and n in norm(i["dir"]) and minyear <= int(i["year"] or 0) <= maxyear]
    out.sort(key=lambda t: (INFO[t]["year"]))
    return out

def search(q, year=None):
    n = norm(q)
    out = [tc for tc, i in INFO.items() if n in norm(i["title"]) and (not year or str(year) == str(i["year"]))]
    out.sort(key=lambda t: -(INFO[t]["lb"] + INFO[t]["votes"]))
    return out[:15]

def leaf(code):
    l = LEAVES[code]
    print(code, l["label"], l["n"], "|", l["secs"])
    for tc, r in PLACED.items():
        if r["leaf"] == code: print("  ", tc, r["title"], r["year"], r["who"][:30], "lb=", INFO.get(tc, {}).get("lb"))

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "dir": show(bydir(sys.argv[2], *map(int, sys.argv[3:5])) if len(sys.argv) > 3 else bydir(sys.argv[2]))
    elif cmd == "s": show(search(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
    elif cmd == "leaf":
        for c in sys.argv[2:]: leaf(c)
