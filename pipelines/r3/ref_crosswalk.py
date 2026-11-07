"""VA coverage against independent references (owner, 2026-11-07: "this is humanity's entire history of visual artistic
expression"). The completeness audit measures the tree against what was gathered; this measures it against references
built independently of the gathering:

  Getty AAT, Styles and Periods facet (6,205 terms: cultures, peoples, periods, dynasties, styles, schools, movements,
  arranged by region), fetched by ref_fetch.py
  UNESCO Intangible Cultural Heritage elements whose names name a visual craft (148 of 849; a keyword selection, since
  UNESCO's own craftsmanship filter is paginated)

Each reference term gets the strongest coverage the tree gives it:
  leaf       a leaf's label, alias, absorbed tradition (collections_from) or alias row bears the name
  entry      an entry (sub-type, centre, school, maker...) bears the name
  mentioned  a leaf's definition or aliases mention the name (word-bounded, names of 4+ letters), also after dropping
             period modifiers (early, middle, late, upper, lower, northern ...): "Middle Mississippian" -> Mississippian
  held       the gathered museum records that carry the name are mapped to leaves: the tree holds this people's work
             without naming it; the name is written into those leaves as a "Peoples & cultures" entry (va_peoples.csv,
             applied by structure_fix.py), so later runs read it as entry
  variant    a regional or phase variant of a leaf: the term's qualifier names the leaf ("Arte Nova (Portuguese Art
             Nouveau)") or its words, stemmed, are a leaf's label words within the same region ("Analytical Cubist")
  out        a religion, denomination or religious order (AAT files them here): belief systems, not visual traditions
  inherited  Getty's own grouping places it: its direct AAT parent, a named tradition rather than a broad grouping, is covered (leaf,
             variant or held) by a leaf of the same region, and an ancient term never goes to a leaf starting after 500
  facet      a period, dynasty, modern nationality, or AAT regional or state designation: served by the period and region facets (the tree has leaves in
             that region), not a tradition
  uncovered  none of these; most have no gathered records: the gap is in the sources, not the tree
AAT terms are mapped to the project's 20 regions (va_facets / coverage grid) from the term and its ancestors in the AAT
hierarchy; the AAT type (culture, period, style...) is read from the label's qualifier. The uncovered backlog is ranked:
styles, schools and movements first, then by the gathered museum records whose labels carry the name.

Writes taxonomy/audit/reference/{aat_crosswalk.csv, unesco_crosswalk.csv, backlog.csv, summary.md}.
Run: python3 pipelines/r3/ref_fetch.py (once), then python3 pipelines/r3/ref_crosswalk.py
"""
import ast, collections, csv, glob, json, os, re, sys, unicodedata

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
REF = os.path.join(ROOT, "data", "reference")
OUT = os.path.join(ROOT, "taxonomy", "audit", "reference")
DATA = os.path.join(ROOT, "artifact", "full", "data")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import va_facets as VF  # noqa: E402

TOP = "300015646"
GENERIC = {"style", "styles", "period", "periods", "culture", "cultures", "art", "school", "movement", "dynasty", "general",
           "early", "late", "middle", "ancient", "modern", "classic", "classical", "new", "old", "great", "people", "peoples"}


def fold(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower().replace("’", "'")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9' ]+", " ", s)).strip()


def lst(v):
    return ast.literal_eval(v) if isinstance(v, str) and v else (v or [])


def kind_of(label):
    q = " ".join(re.findall(r"\(([^)]*)\)", label)).lower()
    for k, rx in (("movement", r"movement"), ("school", r"school"), ("style", r"style"), ("dynasty", r"dynast"),
                  ("period", r"period|era|phase|horizon|age\b"), ("culture", r"culture|people|tradition|language")):
        if re.search(rx, q):
            return k
    return "other"


def base(label):
    return fold(re.sub(r"\s*\([^)]*\)", "", label))


def main():
    os.makedirs(OUT, exist_ok=True)
    tree = json.load(open(os.path.join(DATA, "tree.json")))["va"]
    rows = {}
    for p in glob.glob(os.path.join(DATA, "m-va-*.json")):
        rows.update(json.load(open(p)))
    leaves = {l["code"]: l for f in tree["fams"] for s in f["subs"] for l in s["leaves"]}
    leafname = collections.defaultdict(set); entryname = collections.defaultdict(set); text = {}
    for c, l in leaves.items():
        for n in [l["label"]] + [a for a in re.split(r";\s*", l.get("aliases") or "") if a] + lst(l.get("alias_rows")) + lst(l.get("collections_from")):
            for v in {fold(n), base(n)}:
                if v: leafname[v].add(c)
        for r in rows.get(c, []):
            if r[1] != "Holding institutions":
                for v in {fold(r[0]), base(r[0])}:
                    if v: entryname[v].add(c)
        text[c] = " " + fold(" ".join([l["label"], l.get("aliases") or "", re.sub(r"<[^>]+>", " ", l.get("defn") or "")])) + " "
    alltext = "\n".join(f"{c}\t{t}" for c, t in text.items())

    MOD = r"^(?:early|middle|late|upper|lower|northern|southern|eastern|western|central|classic|proto|post|pre|neo|old|new)\s+"
    def cover(names):
        names = [n for n in dict.fromkeys(names) if n and n not in GENERIC]
        names += [re.sub(MOD, "", n) for n in names if re.match(MOD, n) and len(re.sub(MOD, "", n)) >= 5]
        for n in names:
            if n in leafname: return "leaf", sorted(leafname[n])[:3]
        for n in names:
            if n in entryname: return "entry", sorted(entryname[n])[:3]
        for n in names:
            if len(n) >= 4 and not all(w in GENERIC for w in n.split()):
                hits = re.findall(rf"^([A-N]\d+-\d+)\t.*\b{re.escape(n)}\b", alltext, re.M)
                if hits: return "mentioned", hits[:3]
        return "uncovered", []

    # evidence: gathered record labels carrying the name
    labmass = collections.Counter()
    for r in csv.DictReader(open(os.path.join(ROOT, "taxonomy/r3/collections/label_keys.csv"))):
        for w in set(re.split(r"[,;|·/()]+", r["label"])):
            w = fold(w)
            if w: labmass[w] += int(r["objects"] or 0)

    leafstems = {c: ({w[:5] for w in fold(l["label"]).split() if len(w) >= 5 and w not in GENERIC},) for c, l in leaves.items()}
    # records -> leaves: which leaves hold the objects whose source label carries a name
    held = collections.defaultdict(collections.Counter)
    for f in glob.glob(os.path.join(ROOT, "taxonomy/r3/collections/out_col_*.csv")):
        b = f.split("out_col_")[1][:-4]
        inn = {(r["file"], r["label"], r["family"]): int(r["objects"] or 0) for r in csv.DictReader(open(os.path.join(ROOT, f"taxonomy/r3/collections/in_col_{b}.csv")))}
        for r in csv.DictReader(open(f)):
            m = r["map"].strip()
            if m in leaves:
                for w in set(re.split(r"[,;|·/()\[\]]+", r["label"])):
                    w = fold(w)
                    if w: held[w][m] += inn.get((r["file"], r["label"], r["family"]), 0)
    REGWORDS = re.compile(r"national designation|american regions|<[a-z ]*regions>|regional designation", re.I)
    PERIODS = re.compile(r"period|dynast|reign|\bera\b|modern japanese|kingdoms|empire", re.I)
    peoples = []

    # ---- AAT ----------------------------------------------------------------
    A = json.load(open(os.path.join(REF, "aat_styles.json"))); byid = {a["id"]: a for a in A}
    def path(a):
        out = []; x = a
        while x and x["id"] != TOP and len(out) < 20:
            out.append(x["label"]); x = byid.get(x["parent"])
        return out
    arows = []
    for a in A:
        if a["guide"] or not a["label"]: continue
        p = path(a)
        if any("generic" in s or "by general era" in s or "geologic" in s or "three-age" in s for s in p): continue
        reg = None
        for s in p:
            reg = VF.region_of(s)
            if reg: break
        top = p[-1] if p else ""
        if not reg:
            reg = {"African (general, continental cultures)": "Sub-Saharan Africa", "Oceanic": "Oceania (Pacific)",
                   "Islamic World, The": "Islamic world (MENA, Iran, Anatolia)", "European": "Western Europe",
                   "The Americas": "North America (Indigenous)", "Asian": "South Asia"}.get(top, "Transnational")
        names = [base(a["label"])] + [base(x) for x in a["alts"]]
        how, codes = cover(names)
        if re.search(r"religio|belief|christian order|judaism|buddhis[mt] (school|sect)|monastic|denomination|\bsects?\b", " ".join(p).lower()):
            how, codes = "out", []
        if how == "uncovered":
            for q in re.findall(r"\(([^)]*)\)", a["label"]):
                qn = fold(re.sub(r"\b(culture|style|styles|period|or|and|of|the|general)\b", " ", q))
                if qn and qn in leafname: how, codes = "variant", sorted(leafname[qn])[:3]; break
        if how == "uncovered":
            stems = {w[:5] for w in base(a["label"]).split() if len(w) >= 5 and w not in GENERIC}
            if stems:
                for lc, ln in leafstems.items():
                    if stems <= ln[0] and leaves[lc].get("region") == reg:
                        how, codes = "variant", [lc]; break
        ev = max([labmass.get(n, 0) for n in names] + [0])
        kind = kind_of(a["label"])
        if how == "uncovered":
            h = collections.Counter()
            for n in names: h.update(held.get(n, {}))
            tot = sum(h.values())
            topl = [(c, n) for c, n in h.most_common() if n >= 10 and n >= 0.2 * tot][:3]
            if topl and kind not in ("period", "dynasty") and not PERIODS.search(" ".join(p[:2])):
                how, codes = "held", [c for c, _ in topl]
                for c, n in topl:
                    peoples.append([a["id"], re.sub(r"\s*\([^)]*\)", "", a["label"]).strip(), c, n, "held", ""])
            elif PERIODS.search(a["label"] + " " + " ".join(p[1:3])) or kind in ("period", "dynasty"):
                how = "facet"; kind = "period"
            elif REGWORDS.search(" ".join(p[1:3])) and "(" not in a["label"]:
                how = "facet"; kind = "nationality"
        arows.append(dict(id=a["id"], label=a["label"], kind=kind, region=reg, top=top.replace("<", "").replace(">", ""),
                          path=" > ".join(reversed(p[1:5])), coverage=how, leaves=" ".join(codes), records=ev))
    # ---- second pass: facet designations, inheritance through the AAT hierarchy, placement by records ----------
    X = {r["id"]: r for r in arows}
    kids = collections.defaultdict(list)
    for a in A: kids[a["parent"]].append(a["id"])
    FAC = {r["code"]: r for r in csv.DictReader(open(os.path.join(ROOT, "taxonomy/r3/va_facets.csv")))}
    def strong(i, reg):
        x = X.get(i)
        if not (x and x["coverage"] in ("leaf", "variant", "held") and x["leaves"]): return []
        return [l for l in x["leaves"].split() if FAC.get(l, {}).get("region") == reg]
    fam_of = collections.defaultdict(collections.Counter)  # name -> families of its culture-only records
    for f in glob.glob(os.path.join(ROOT, "taxonomy/r3/collections/out_col_*.csv")):
        b = f.split("out_col_")[1][:-4]
        inn = {(r["file"], r["label"], r["family"]): int(r["objects"] or 0) for r in csv.DictReader(open(os.path.join(ROOT, f"taxonomy/r3/collections/in_col_{b}.csv")))}
        for r in csv.DictReader(open(f)):
            fam = r["map"].split(":", 1)[1] if r["map"].startswith("general:") else (r["family"] if r["map"].startswith("missing:") else None)
            if fam and fam in "ABCDEFGHIJ":
                for w in set(re.split(r"[,;|·/()\[\]]+", r["label"])):
                    w = fold(w)
                    if w: fam_of[w][fam] += inn.get((r["file"], r["label"], r["family"]), 0)
    for r in arows:
        if r["coverage"] != "uncovered": continue
        a = byid[r["id"]]; pth = path(a); low = " > ".join(pth[1:4]).lower()
        if re.search(r"regional styles|regional designation|modern u\.s\. state|american regions|national designation|<[^>]*regions>", low) or "(of modern" in r["label"]:
            r["coverage"], r["kind"] = "facet", "nationality"; continue
        reg = r["region"]; par = a["parent"]
        ancient = re.search(r"ancient|pre-columbian|early western|prehistoric|neolithic|bronze age|iron age", (r["path"] + " " + r["label"]).lower())
        # only the direct parent counts, and only when it is a named tradition rather than a broad grouping: a vote of
        # covered siblings sent members of "Japanese painting styles" to Yamato-e and "Southeast Asian" to Khmer Architecture
        broad = re.search(r"^<|styles$|styles and movements|^(early|late|middle) |southeast asian|north american", byid[par]["label"].lower()) if par in byid else True
        c = collections.Counter() if broad else collections.Counter({l: 3 for l in strong(par, reg)})
        living = "(culture" in byid.get(par, {}).get("label", "") and not ancient   # a people under a culture heading: not into a leaf that closed before 1600
        cand = [l for l, _ in c.most_common(2) if not (ancient and FAC[l]["start"] and int(FAC[l]["start"]) >= 500)
                and not (living and FAC[l]["end"] and int(FAC[l]["end"]) < 1600)]
        if re.match(r"modern\b", r["label"], re.I) or r["label"].startswith("Nanyang"): cand = []   # facet / 20th-c. movement without a leaf
        nm = re.sub(r"\s*\([^)]*\)", "", r["label"]).strip()
        if cand:
            r["coverage"], r["leaves"] = "inherited", " ".join(cand)
            for l in cand: peoples.append([r["id"], nm, l, 0, "inherited", byid[par]["label"]])
            continue
        # (placement by the medium of a people's records and word overlap with its AAT cluster was tried and dropped:
        # it sent Amazonian peoples to Nasca Textiles and Ewe to Kanga; peoples with records but no inherited home
        # stay in the backlog for a decision)
    with open(os.path.join(OUT, "aat_crosswalk.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(arows[0].keys())); w.writeheader(); w.writerows(arows)

    # cumulative: placements applied in earlier runs are now entries in the tree and must stay in the file
    pp = os.path.join(ROOT, "taxonomy/r3/va_peoples.csv")
    if os.path.exists(pp):
        have = {(r[0], r[2]) for r in peoples}
        for r in csv.DictReader(open(pp)):
            if (r["aat_id"], r["leaf"]) not in have and r.get("how") != "placed":
                peoples.append([r["aat_id"], r["name"], r["leaf"], r["objects"], r.get("how") or "held", r.get("aat_group") or ""])
    with open(pp, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["aat_id", "name", "leaf", "objects", "how", "aat_group"]); w.writerows(peoples)

    # ---- UNESCO -------------------------------------------------------------
    U = json.load(open(os.path.join(REF, "unesco_crafts.json")))
    urows = []
    for u in U:
        nm = fold(u["name"])
        hit = []
        for n, cs in leafname.items():
            if len(n) >= 4 and n not in GENERIC and re.search(rf"\b{re.escape(n)}\b", nm):
                hit += sorted(cs)
        how = "leaf" if hit else None
        if not how:
            words = [w for w in nm.split() if len(w) >= 5 and w not in GENERIC and w not in
                     {"traditional", "craftsmanship", "making", "skills", "knowledge", "techniques", "practices", "associated", "weaving",
                      "embroidery", "pottery", "carving", "culture", "region", "district", "transmission", "safeguarding", "programme",
                      "village", "community", "people", "heritage", "traditions", "national", "related", "production"}]
            for wd in words:
                h = re.findall(rf"^([A-N]\d+-\d+)\t.*\b{re.escape(wd)}\b", alltext, re.M)
                if h: hit = h[:3]; how = "mentioned"; break
        urows.append(dict(ref=u["ref"], name=u["name"], list=u["list"], coverage=how or "uncovered", leaves=" ".join(dict.fromkeys(hit)), url=u["url"]))
    with open(os.path.join(OUT, "unesco_crosswalk.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(urows[0].keys())); w.writeheader(); w.writerows(urows)

    # ---- backlog and summary -------------------------------------------------
    rank = {"movement": 0, "school": 0, "style": 1, "culture": 2, "other": 3, "dynasty": 4, "period": 5, "nationality": 6}
    back = sorted([r for r in arows if r["coverage"] == "uncovered"], key=lambda r: (rank[r["kind"]], -r["records"], r["region"], r["label"]))
    with open(os.path.join(OUT, "backlog.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(arows[0].keys())); w.writeheader(); w.writerows(back)
    byreg = collections.defaultdict(collections.Counter); bykind = collections.defaultdict(collections.Counter)
    for r in arows:
        byreg[r["region"]][r["coverage"]] += 1; bykind[r["kind"]][r["coverage"]] += 1
    def pct(c, keys=("leaf", "entry", "mentioned", "variant", "held", "inherited", "placed", "facet")): return sum(c[k] for k in keys) / max(1, sum(c.values()) - c["out"])
    L = ["# Visual Art against independent references", "",
         f"Getty AAT Styles and Periods: {len(arows):,} named cultures, periods, dynasties, styles, schools and movements "
         f"(generic and geological terms left out). UNESCO: {len(urows)} Intangible Cultural Heritage elements naming a visual craft.", "",
         "Coverage: **leaf** (a leaf bears the name), **entry** (an entry inside a leaf bears it), **mentioned** (a definition names it), "
         "**uncovered**. Mentioned is weak coverage: the tree knows the name but gives it no place of its own.", "",
         f"Overall: {pct(sum(byreg.values(), collections.Counter())):.0%} of in-scope AAT terms are covered (leaf, entry, mention, variant, held or facet); "
         f"{pct(sum(byreg.values(), collections.Counter()), ('leaf', 'entry')):.0%} have a leaf or entry.", "",
         "## By region", "", "| Region | Terms | Leaf | Entry | Mentioned | Variant | Held | Inherited | Placed | Facet | Out of scope | Uncovered | of which with records | Covered |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for reg, c in sorted(byreg.items(), key=lambda x: -sum(x[1].values())):
        ev = sum(1 for r in arows if r["region"] == reg and r["coverage"] == "uncovered" and r["records"])
        L.append(f"| {reg} | {sum(c.values())} | {c['leaf']} | {c['entry']} | {c['mentioned']} | {c['variant']} | {c['held']} | {c['inherited']} | {c['placed']} | {c['facet']} | {c['out']} | {c['uncovered']} | {ev} | {pct(c):.0%} |")
    L += ["", "## By kind of term", "", "| Kind | Terms | Leaf | Entry | Mentioned | Variant | Held | Facet | Out of scope | Uncovered | Covered |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for k, c in sorted(bykind.items(), key=lambda x: rank[x[0]]):
        L.append(f"| {k} | {sum(c.values())} | {c['leaf']} | {c['entry']} | {c['mentioned']} | {c['variant']} | {c['held']} | {c['facet']} | {c['out']} | {c['uncovered']} | {pct(c):.0%} |")
    uc = collections.Counter(r["coverage"] for r in urows)
    L += ["", f"## UNESCO crafts: {uc['leaf']} named by a leaf, {uc['mentioned']} mentioned, {uc['uncovered']} uncovered (of {len(urows)})", "",
          "| Element | List |", "|---|---|"]
    L += [f"| {r['name']} | {r['list']} |" for r in urows if r["coverage"] == "uncovered"]
    L += ["", "## Backlog: uncovered styles, schools and movements (all) and cultures with gathered records (top 60)", "",
          "| AAT term | Kind | Region | AAT path | Records |", "|---|---|---|---|---:|"]
    sel = [r for r in back if r["kind"] in ("style", "school", "movement")] + [r for r in back if r["kind"] not in ("style", "school", "movement") and r["records"] >= 50][:60]
    L += [f"| {r['label']} | {r['kind']} | {r['region']} | {r['path']} | {r['records']:,} |" for r in sel]
    open(os.path.join(OUT, "summary.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L[:40]))
    print(len(back), "uncovered AAT terms;", len(sel), "in the summary backlog")


if __name__ == "__main__":
    main()
