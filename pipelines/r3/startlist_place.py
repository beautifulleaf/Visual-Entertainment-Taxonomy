"""R3: place the TSPDT Starting List films (owner: every Starting List film gets a home).

Rules first (owner's choice), passes for the rest. Cascade per film, most fixed evidence first:
  1 already placed in the tab → skip
  2 form: Animation → C (Japan → anime pending; ≤ 40 min → C14; else C12 pending); ≤ 40 min → A21 pending
  3 director prior: the director's films already placed sit ≥ 60% (and ≥ 2 films) in one leaf of the form's
    family → that leaf (rule 'director')
  4 effect → sub-family from the first decisive TSPDT genre word; leaf left to a pass
Writes taxonomy/r3/startlist/decided.csv and pending_<sub>.csv (one per sub-family) plus stats.
"""
import csv, collections, json, os, re, unicodedata
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
R3 = os.path.join(ROOT, "taxonomy", "r3"); OUT = os.path.join(R3, "startlist")
D = os.path.join(ROOT, "artifact", "full", "data")
csv.field_size_limit(10**9)
EFFECT = [("Horror", "A4"), ("Science Fiction", "A5"), ("Western", "A10"), ("War", "A9"), ("Biography", "A11"),
          ("Musical", "A14"), ("Music", "A14"), ("Martial Arts", "A7"), ("Action", "A7"), ("Fantasy", "A6"), ("Adventure", "A6"),
          ("Crime", "A2"), ("Thriller", "A3"), ("Mystery", "A3"), ("Film Noir", "A2"), ("Family", "A17"), ("Children", "A17"),
          ("Experimental", "A20"), ("Avant-Garde", "A20"), ("Erotic", "A15"), ("History", "A8"), ("Historical", "A8"),
          ("Comedy", "A12"), ("Romance", "A13"), ("Drama", "A16")]

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()

def main():
    os.makedirs(OUT, exist_ok=True)
    tree = json.load(open(os.path.join(D, "tree.json")))
    leaves = {l["code"]: l for f in tree["ft"]["fams"] for s in f["subs"] for l in s["leaves"]}
    placed, by_dir = set(), collections.defaultdict(collections.Counter)
    for fam in "ABC":
        for lf, rows in json.load(open(os.path.join(D, f"m-ft-{fam}.json"))).items():
            for k in rows:
                placed.add(k[5]); placed.add(("t", norm(k[0]), str(k[1])[:4]))
                if k[7] == "film":
                    for d in re.split(r";|,| & ", k[2]): by_dir[norm(d)][lf] += 1
    seen = set(); films = []
    for r in csv.DictReader(open(os.path.join(R3, "tspdt", "entries.csv"))):
        if r["list_id"] not in ("tspdt_starting_list", "tspdt_21st_starting_list"): continue
        key = r["tconst"] or ("t", norm(r["title"]), r["year"][:4], norm(r["director"]))
        if key in seen: continue
        seen.add(key); films.append(r)
    dec, pend, st = [], collections.defaultdict(list), collections.Counter()
    for r in films:
        if (r["tconst"] and r["tconst"] in placed) or ("t", norm(r["title"]), r["year"][:4]) in placed:
            st["already"] += 1; continue
        g = r["genre"] if r["genre"] != "---" else ""
        toks = [t.strip() for t in g.split("-") if t.strip()]
        mins = int(r["mins"]) if (r["mins"] or "").isdigit() else 0
        short = 0 < mins <= 40 or "Short" in toks
        anim = "Animation" in toks
        jp = "japan" in norm(r["country"])
        fam = "C" if anim else "A"
        row = dict(id=r["tconst"] or f"tspdt:{norm(r['title'])[:40].replace(' ', '-')}-{r['year'][:4]}", title=r["title"], year=r["year"],
                   who=r["director"], country=r["country"], genre=g, mins=r["mins"], lists=r["list_id"])
        # director prior within the family
        dirs = [norm(d) for d in re.split(r";|,| & ", r["director"]) if d.strip()]
        prior = collections.Counter()
        for d in dirs: prior.update({lf: n for lf, n in by_dir.get(d, {}).items() if lf[0] == fam})
        tot = sum(prior.values())
        if tot >= 2:
            lf, n = prior.most_common(1)[0]
            if n / tot >= 0.6 and not (short and fam == "A" and not lf.startswith("A21")):
                dec.append(dict(row, leaf=lf, rule=f"director ({n}/{tot})")); st["director"] += 1; continue
        if anim:
            sub = "C14" if short else ("anime" if jp else "C12")
        elif short:
            sub = "A21"
        elif "Documentary" in toks:
            sub = "A19"
        else:
            sub = next((s for w, s in EFFECT if w in toks), "A16")
        pend[sub].append(row); st["pending_" + sub] += 1
    with open(os.path.join(OUT, "decided.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(dec[0].keys())); w.writeheader(); w.writerows(dec)
    for sub, rows in pend.items():
        with open(os.path.join(OUT, f"pending_{sub}.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(len(films), "distinct Starting List films;", dict(st))
    json.dump(dict(st), open(os.path.join(OUT, "stats.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
