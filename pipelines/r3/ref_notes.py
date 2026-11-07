"""Sort the Getty AAT terms the crosswalk leaves uncovered (no leaf, entry, mention, variant, inherited home, decision
or gathered records) by what Getty's own scope note says they are, so that only the art styles need a decision.

  note-placed  the scope note names a leaf (label or alias, whole words) of the term's region: "Sakya School (painting) ...
               Tibetan school of painting ... Ngor" names the leaf that holds Ngor painting; the term becomes an entry there
  parent-placed  the nearest AAT parent, stripped of "pottery styles" and the like, is the name of a leaf of the same
               region and medium ("Mimbres corrugated" under "Mimbres pottery styles" -> Mimbres Pottery)
  grouping     a heading of Getty's hierarchy ("Styles belonging to Pre-Columbian Ohio Valley cultures", "... regional
               styles"); a container, not a tradition
  nationality  a nationality or polity ("Nationality and culture of territories over which the Pope had sovereignty")
  ideology     political ideologies, religions and attitudes AAT files in this facet; not visual traditions
  polity       a dynasty, beylik or empire named as a style without a medium: served by the period and region facets
  people       a people or ethnic group with no gathered records and no covered AAT parent: a gap in the sources
  archaeology  an archaeological culture, phase or site known from excavation (lithic and pottery phases); its art,
               where any is published, belongs with the leaf of the region's period when one exists
  art          everything else: a named style, school, movement or ware; this is the list that needs a decision
Notes: data/reference/aat_notes.json (Getty SPARQL, English scope notes). Writes taxonomy/audit/reference/notes_sort.csv.
"""
import csv, json, os, re, collections, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ref_crosswalk import fold, GENERIC  # noqa: E402
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")

PEOPLE = re.compile(r"\b(ethnic group|people of the same name|peoples? (?:of|living|inhabiting|native)|indigenous|tribe|tribal|"
                    r"inhabitants of|describes works created by the|nation\b|first nations?|band of)", re.I)
ARCH = re.compile(r"\b(archaeolog|excavat|site of|type site|projectile|lithic|point type|phase\b|horizon\b|neolithic|chalcolithic|"
                  r"bronze age|iron age|paleo|mesolithic|bce\b|b\.c\.)", re.I)
NATION = re.compile(r"\bnationality\b|\bpolity\b|\bkingdom of\b|\bsovereign", re.I)
IDEO = re.compile(r"political ideolog|gnostic|multicultural|religio|denomination|sect\b", re.I)
GROUP = re.compile(r"^(?:[a-z ]{0,20})styles belonging to|^cultures,? (?:and )?styles|^cultures, styles,? and periods", re.I)
POLITY = re.compile(r"\b(dynasty|dynastic|beylik|sultanate|ruled|rulers?|clan that ruled|empire)\b", re.I)
PEOPLE2 = re.compile(r"culture of (?:the )?[A-Z][\w' -]+ (?:people|peoples)\b|aboriginal people|culture and style of the [\w' -]+ peoples?", re.I)
MEDIUM = [("E", r"potter|ceramic|\bwares?\b|porcelain|celadon|stoneware|faience"), ("K", r"architect|building"),
          ("A", r"painting|painters?\b"), ("D", r"sculpt|carving"), ("H", r"textile|carpet|rug\b|weav|embroider"),
          ("G", r"metalwork|silver|goldsmith|jewel")]


# note placements read and rejected: the note names the leaf only in passing
REJECT = {("300440778", "A5-81"), ("300403937", "I3-15")}
REJECT_PARENT = {"Chinese Baroque", "Baroque Classicism"}   # Straits shophouse style; a Late Baroque current, not Rococo


def medium(t):
    return [f for f, rx in MEDIUM if re.search(rx, t, re.I)]


def main():
    tree = json.load(open(os.path.join(ROOT, "artifact/full/data/tree.json")))["va"]
    leaves = {l["code"]: l for f in tree["fams"] for s in f["subs"] for l in s["leaves"]}
    names = collections.defaultdict(set)
    for c, l in leaves.items():
        for n in [l["label"]] + [a for a in re.split(r";\s*", l.get("aliases") or "") if a]:
            n = fold(re.sub(r"\s*\([^)]*\)", "", n))
            if len(n) >= 5 and n not in GENERIC and not all(w in GENERIC for w in n.split()): names[n].add(c)
    MEDW = re.compile(r"\b(pottery|ware|wares|ceramics|painting|paintings|sculpture|architecture|textiles?|carving|porcelain|prints?)\b", re.I)
    bases = collections.defaultdict(set)
    for c, l in leaves.items():
        b = fold(MEDW.sub(" ", re.sub(r"\s*\([^)]*\)", "", l["label"])))
        if len(b) >= 4 and b not in GENERIC: bases[b].add(c)
    rx = re.compile(r"\b(" + "|".join(sorted(map(re.escape, names), key=len, reverse=True)) + r")\b")
    N = json.load(open(os.path.join(ROOT, "data/reference/aat_notes.json")))
    A = {a["id"]: a for a in json.load(open(os.path.join(ROOT, "data/reference/aat_styles.json")))}
    SUF = re.compile(r"\s*\((?:[^)]*)\)|\b(?:pottery|ceramics?|painting|printmaking|sculpture|architecture|architectural|textile|ware|glyptic|decorative arts|fine arts)?\s*styles?\b", re.I)
    def parent_home(i, reg, med):
        """the nearest AAT ancestor whose name, stripped of 'pottery styles' etc., is a leaf of the region and medium"""
        a = A.get(i)
        for _ in range(4):
            a = A.get(a["parent"]) if a else None
            if not a: return []
            n = fold(SUF.sub(" ", a["label"]))
            if not n or n in GENERIC: continue
            pm = medium(a["label"])
            # a stripped leaf name ("korean" from Korean Architecture) only counts when the term or parent names the medium
            pool = names.get(n, set()) | (bases.get(n, set()) if (pm or med) else set())
            cs = [c for c in pool if leaves[c].get("region") == reg and (not med or c[0] in med)]
            cs = [c for c in cs if not pm or c[0] in pm]
            if cs: return sorted(cs)[:2]
        return []
    out = []
    for r in csv.DictReader(open(os.path.join(ROOT, "taxonomy/audit/reference/aat_crosswalk.csv"))):
        if r["coverage"] != "uncovered": continue
        note = N.get(r["id"], ""); lab = r["label"]; low = (r["top"] + " " + r["path"]).lower()
        hits = []
        first = re.split(r"(?<=[a-z\)])\.\s", note, maxsplit=1)[0]
        if re.search(r"against|contrast|reaction|unlike|instead|opposed|rather than|rejected", first, re.I): first = ""
        for m in rx.finditer(fold(first)):
            hits += [c for c in names[m.group(1)] if leaves[c].get("region") == r["region"]]
        med = medium(lab + " " + note[:160] + " " + r["path"].split(" > ")[-1])
        hits = [c for c in dict.fromkeys(hits) if (not med or c[0] in med) and (r["id"], c) not in REJECT]
        artish = re.search(r"potter|ceramic|\bwares?\b|porcelain|painting|sculpt|architect|textile|carpet|school|movement|style of", note[:200] + " " + lab, re.I)
        if IDEO.search(r["top"] + " " + lab) or IDEO.search(note[:80]): s = "ideology"
        elif re.search(r"\bstyles\b|regional", lab, re.I) or GROUP.search(note.strip()): s = "grouping"
        elif hits and len(hits) <= 2 and not PEOPLE.search(note): s = "note-placed"
        elif lab not in REJECT_PARENT and parent_home(r["id"], r["region"], med): s, hits = "parent-placed", parent_home(r["id"], r["region"], med)
        elif NATION.search(note) or "(of modern" in lab: s = "nationality"
        elif POLITY.search(note[:200]) and not re.search(r"potter|ceramic|\bwares?\b|painting|school", note[:200] + lab, re.I): s = "polity"
        elif PEOPLE.search(note) or PEOPLE2.search(note) or (r["kind"] == "culture") or re.search(r"\((?:[^)]*culture[^)]*)\)", lab): s = "people"
        elif not artish and (ARCH.search(note) or (not note and re.search(r"pre-columbian|paleo-indian|archaic|prehistoric|paleolithic|neolithic", low))): s = "archaeology"
        elif not note and re.search(r"native|african|oceanic|melanesian|polynesian|micronesian|siberian|aboriginal|tuareg|berber|ancient", low): s = "people"
        elif not note: s = "art (no note)"
        else: s = "art"
        out.append(dict(aat_id=r["id"], label=lab, region=r["region"], sort=s, leaves=" ".join(hits[:2]) if s in ("note-placed", "parent-placed") else "",
                        parent=r["path"].split(" > ")[-1], note=note[:300]))
    with open(os.path.join(ROOT, "taxonomy/audit/reference/notes_sort.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    print(collections.Counter(o["sort"] for o in out))
    return out


if __name__ == "__main__":
    main()
