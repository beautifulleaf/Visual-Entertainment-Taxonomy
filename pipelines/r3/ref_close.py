"""Close the remaining AAT gaps by rule (owner, 2026-11-07: "cover those remaining gaps"), after ref_notes.py.

1. Subgroup default (peoples). AAT lists peoples down to clans and sub-groups; art history and museums collect at the
   level of the people or style area. A people with no gathered records takes the home of its nearest AAT ancestor that
   is a named people or tradition (not a language family, region or "(general)" heading) and is strongly covered (leaf,
   entry, variant, held, inherited, decided). Absence from the culture labels of all 1.24M gathered museum records is the
   evidence that no source treats the sub-group as a style of its own; a source that does reopens it.
2. The rest of the peoples: named people with no covered parent. Their medium is unknown, so they cannot be placed;
   they are counted by region as the open list for the sources (step 3 of the plan: museum APIs by culture name).
3. Archaeology: a phase or type site is a dating label unless it produced decorated work. Its era is read from its
   scope note (centuries, BCE dates) or, failing that, from its AAT ancestors (Paleo-Indian, Archaic, Woodland,
   Neolithic, Bronze/Iron Age, Pre-Columbian); the term is covered by the era facet when the tree has a leaf in its
   region whose period lies in its window ("era-populated": the cell holds work, which says nothing about this phase),
   and marks an empty region x era cell otherwise ("era-empty"): those cells are the real archaeological gaps.
0. Before both: a people or phase whose nearest named AAT ancestor (a culture, not a heading) is the label or an alias of
   a leaf of the same region takes that leaf ("ancestor-named": Mogollon phases -> Mogollon Pottery).
Writes taxonomy/audit/reference/close.csv (aat_id, label, region, rule, leaves, era, note).
"""
import csv, json, os, re, collections, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import va_facets as VF  # noqa: E402
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
STRONG = {"leaf", "entry", "variant", "held", "inherited", "decided"}
BROAD = re.compile(r"^<|\(general|general\)|styles?\b|language|subfamily|branch|cultures\b|regional|native american$|^native |"
                   r"african$|^(west|east|central|southern|northern) african|^ancient |american$|oceanic|melanesian|polynesian|"
                   r"micronesian|^gur$|benue-congo|^bantu|^mande|^kwa\b|chadic|nilotic|cushitic|lake chad|guinea coast|"
                   r"sudanese|sahel|siberian|arctic|subarctic|plains indian|woodland|plateau|great basin|californian|southwestern|"
                   r"southeastern|northeastern|northwest coast", re.I)
# era from ancestor names when the note gives no dates (year ranges are conventional, North America unless stated)
ERA_HINT = [(r"paleo-indian|paleolithic|clovis|folsom|plano", (-12000, -8000)), (r"\barchaic\b", (-8000, -1000)),
            (r"mesolithic", (-9000, -5000)), (r"neolithic", (-7000, -3000)), (r"chalcolithic", (-4500, -3000)),
            (r"bronze age", (-3000, -1100)), (r"iron age", (-1100, 0)), (r"woodland", (-1000, 1000)),
            (r"mississipp", (800, 1600)), (r"pre-columbian", (-1000, 1500)), (r"prehistoric", (-10000, -1000)),
            (r"early nomads|scyth|kurgan", (-900, 300))]


def main():
    A = {a["id"]: a for a in json.load(open(os.path.join(ROOT, "data/reference/aat_styles.json")))}
    X = {r["id"]: r for r in csv.DictReader(open(os.path.join(ROOT, "taxonomy/audit/reference/aat_crosswalk.csv")))}
    N = json.load(open(os.path.join(ROOT, "data/reference/aat_notes.json")))
    FAC = list(csv.DictReader(open(os.path.join(ROOT, "taxonomy/r3/va_facets.csv"))))
    REG = {f["code"]: f["region"] for f in FAC}
    tree = json.load(open(os.path.join(ROOT, "artifact/full/data/tree.json")))["va"]
    import glob
    MV = {}
    for pth in glob.glob(os.path.join(ROOT, "artifact/full/data/m-va-*.json")): MV.update(json.load(open(pth)))
    TXT = {l["code"]: (" ".join([l["label"], l.get("aliases") or "", l.get("defn") or ""] + [x[0] for x in MV.get(l["code"], [])])).lower()
           for f in tree["fams"] for s_ in f["subs"] for l in s_["leaves"]}
    NATIVE = {"North America (Indigenous)", "Mesoamerica & Caribbean", "South America", "Oceania (Pacific)", "Australia (Aboriginal)", "Sub-Saharan Africa"}
    byreg = collections.defaultdict(list)
    for f in FAC:
        if f["start"]: byreg[f["region"]].append((int(f["start"]), int(f["end"]), f["code"]))

    def anc(i):
        a = A.get(i); out = []
        while a and a["parent"] in A:
            a = A[a["parent"]]; out.append(a)
        return out

    LABS = {l["code"]: (l["label"] + "; " + (l.get("aliases") or "")).lower() for f in tree["fams"] for s_ in f["subs"] for l in s_["leaves"]}
    DEFN = {l["code"]: (l["label"] + "; " + (l.get("aliases") or "") + "; " + re.sub(r"<[^>]+>", " ", l.get("defn") or "")).lower()
            for f in tree["fams"] for s_ in f["subs"] for l in s_["leaves"]}
    SUF = re.compile(r"\s*\([^)]*\)|\b(?:pottery|ceramics?|ware|painting|sculpture|architecture|textile|fine arts|decorative arts)?\s*styles?\b|\b(?:culture|phase|stage|tradition|period)\b", re.I)
    FIXREG = {}
    for r in X.values():
        pth = " ".join(a["label"] for a in anc(r["id"]))
        if re.search(r"native north american|pre-columbian.*north american|paleo-indian|mogollon|anasazi|hohokam|pueblo", pth, re.I): FIXREG[r["id"]] = "North America (Indigenous)"
    def named_home(r, reg):
        """the nearest AAT ancestor (up to 5 levels) whose name is the label or an alias word-group of a leaf in the region"""
        for a in anc(r["id"])[:5]:
            n = re.sub(r"\s+", " ", SUF.sub(" ", a["label"])).strip().lower()
            if len(n) < 4 or BROAD.search(a["label"]) or NATIONAL.search(n) or n in ("native", "african", "american", "ancient"): continue
            cs = [c for c, t in LABS.items() if REG.get(c) == reg and re.search(rf"(?:^|; |\b){re.escape(n)}\b", t)]
            if 0 < len(cs) <= 3: return a["label"], cs
        return None

    # national and regional headings are not cultures: a sub-group of "Iranian" or "Vanuatu" has no single home
    NATIONAL = re.compile(r"^(asian|mediterranean|iranian|persian|central asian|east asian|south asian|aegean|egyptian|australian|sri lankan|yemeni|"
                          r"cross river|gansu|vanuatu|chinese|japanese|korean|indian|arab|turkic|mongol|berber)\b")
    SKIP = {"Birnin Gazargamo"}   # AAT files this Kanuri capital under Igbo-Ukwu
    out = []
    for r in X.values():
        if r["coverage"] in ("people", "archaeology") and r["label"] not in SKIP:
            nh = named_home(r, FIXREG.get(r["id"], r["region"]))
            if nh:
                out.append(dict(aat_id=r["id"], label=r["label"], region=FIXREG.get(r["id"], r["region"]), rule="ancestor-named",
                                leaves=" ".join(nh[1][:2]), era="", note=f"under {nh[0]}"))
                continue
        if r["coverage"] == "people" or r["label"] in SKIP:
            home = None
            for a in anc(r["id"])[:4]:
                lab = re.sub(r"\s*\([^)]*\)", "", a["label"]).strip()
                if BROAD.search(a["label"]) or BROAD.search(lab): continue
                x = X.get(a["id"])
                if x and x["coverage"] in STRONG - {"variant"} and x["leaves"]:
                    # the parent's own leaves, in the people's region, that carry the parent's name (label or entry)
                    pn = re.sub(r"^(?:coastal|central|northern|southern|eastern|western|upper|lower)\s+", "", VF.fold(lab))  # "Coastal Akan" -> akan
                    cs = [c for c in x["leaves"].split() if REG.get(c) == r["region"] and len(pn) >= 4 and re.search(rf"\b{re.escape(pn)}\b", DEFN.get(c, ""))]
                    if cs: home = (a["label"], " ".join(cs)); break
            if home:
                out.append(dict(aat_id=r["id"], label=r["label"], region=r["region"], rule="subgroup", leaves=" ".join(home[1].split()[:2]),
                                era="", note=f"sub-group of {home[0]}"))
            else:
                out.append(dict(aat_id=r["id"], label=r["label"], region=r["region"], rule="people-open", leaves="", era="", note=""))
        elif r["coverage"] == "archaeology":
            note = N.get(r["id"], "")
            per = VF.period_of(note) if note else None
            path = " > ".join(a["label"] for a in anc(r["id"])) + " " + r["label"]
            if not per:
                for rx, p in ERA_HINT:
                    if re.search(rx, path, re.I): per = p; break
            reg = FIXREG.get(r["id"], r["region"])   # AAT's North American branch mixes settler and pre-contact terms
            # a populated cell: a leaf of the region whose own period lies within the term's window (not merely overlaps a
            # leaf that runs to the present)
            cells = [c for s, e, c in byreg.get(reg, []) if per and s <= per[1] and s >= per[0] - 500 and e >= per[0]]
            out.append(dict(aat_id=r["id"], label=r["label"], region=reg, rule=("era-populated" if cells else "era-empty") if per else "undated",
                            leaves=" ".join(cells[:3]), era=f"{per[0]}–{per[1]}" if per else "", note=""))
    with open(os.path.join(ROOT, "taxonomy/audit/reference/close.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    print(collections.Counter(o["rule"] for o in out))
    return out


if __name__ == "__main__":
    main()
