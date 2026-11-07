"""R3 collections cross-reference, step 2b: resolve single objects whose label is only a culture.

The label mapping (out_col_*.csv) sends a label such as "Indonesian" + textiles, or "Japan · Edo" +
painting, to general:<family>, because the label alone names no single tradition. Many of those
objects still name their tradition in their own title ("Batik sarong", "Kris with sheath", "Imari dish").
This step resolves such objects one by one:

  an object in a general:<family> key resolves to leaf L when
  - its title contains, as whole words, a name of L (label, alias, alias row, or an entry of L's
    Sub-types, Centres & workshops, Schools & phases or Sub-styles groups), L in the same family;
  - that name belongs to only one leaf of the family (ambiguous names are not used); failing that, a
    name that belongs to only one leaf in the whole tree resolves across families, because the family
    of an object is guessed from its object-type words and is often wrong (netsuke typed as woodwork,
    haniwa from Kofun tombs typed as metalwork);
  - plurals and the Dutch spellings of the Dutch world-culture collections count (VARIANTS);
  - L is in an object family (A–J; architecture, art in place, new media and design hold no museum objects);
  - the object's culture is compatible with L: labels of that culture already map to L, or L's label,
    aliases or sub-family name the culture, or L's definition names it and L's label names no other
    culture (Goryeo Buddhist Painting is not Japanese because its definition mentions Japan), and
  - when both are known, the object's date falls within L's span (±50 years).

Used by collections_build.py (resolved objects count for the leaf's holding institutions) and by
the completeness audit (V3: label-coarse versus real gaps). Run alone for the report:
    python3 pipelines/r3/collections_resolve.py
writes taxonomy/r3/collections/object_resolve.csv (file,label,family,leaf,objects) and
taxonomy/audit/va_completeness/v3_cells.csv.
"""
import ast, collections, csv, glob, gzip, json, os, re, unicodedata
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
O = os.path.join(ROOT, "taxonomy", "r3", "collections")
DATA = os.path.join(ROOT, "artifact", "full", "data")
csv.field_size_limit(10**9)

NAME_GROUPS = {"Sub-types", "Centres & workshops", "Schools & phases", "Sub-styles", "leaf"}
GENERIC = set("""art arts ware wares pottery painting paintings sculpture ceramics ceramic textile textiles weaving
embroidery carving carvings metalwork jewellery jewelry glass lacquer furniture manuscript manuscripts folk
court style school period early late classical modern ancient traditional bowl dish jar vase cloth
figure figures mask masks box plate tile tiles panel book books print prints drawing drawings
portrait landscape flowers birds gold silver bronze iron wood stone ivory jade silk cotton wool
dragon lotus temple palace royal village tribal popular religious ritual""".split())
STEM = {"japan": "japan", "china": "chin", "india": "indi", "korea": "kore", "iran": "iran|persia", "egypt": "egypt",
        "turkey": "turk|ottoman", "france": "fren|franc", "italy": "ital", "germany": "germ", "spain": "spa", "britain": "engl|brit",
        "netherlands": "dutch|nether", "greece": "greek|greec|attic", "rome": "roman", "indonesia": "indones|java|bali|sumat|borne|sulaw|lampung|batak|dayak|toraja|aceh",
        "mexico": "mexic", "peru": "peru|andean|inca|moche|nazca|chimu|wari|paracas"}


# spelling variants in the source titles (Dutch transliteration of Indonesian/Japanese/Tibetan names, Dutch terms)
VARIANTS = {"wajang": "wayang", "wajangpop": "wayang", "tanka": "thangka", "thanka": "thangka", "zwaardstootplaat": "tsuba",
            "kriskling": "kris", "keris": "kris", "songket": "songket", "tapis": "tapis", "netsukes": "netsuke"}


def fold(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower().replace("’", "'")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9' ]+", " ", s)).strip()


def head(label):
    lab = label or ""
    if lab.startswith(("people:", "node:", "wd:")):
        parts = lab.split(":")
        lab = parts[1] if len(parts) > 1 else lab
    h = fold(re.split(r"[,·(;/:]| - ", lab, maxsplit=1)[0].replace("_", " "))
    for k, v in (("japanese", "japan"), ("chinese", "china"), ("indian", "india"), ("korean", "korea"), ("persian", "iran"),
                 ("iranian", "iran"), ("egyptian", "egypt"), ("turkish", "turkey"), ("french", "france"), ("italian", "italy"),
                 ("german", "germany"), ("spanish", "spain"), ("english", "britain"), ("british", "britain"), ("dutch", "netherlands"),
                 ("greek", "greece"), ("roman", "rome"), ("indonesian", "indonesia"), ("javanese", "indonesia"), ("balinese", "indonesia"),
                 ("mexican", "mexico"), ("peruvian", "peru")):
        if h == k:
            return v
    return h


def lit(v, d):
    if isinstance(v, (list, dict)):
        return v
    try:
        return ast.literal_eval(v) if v else d
    except Exception:
        return d


CENT = re.compile(r"(\d{1,2})(?:st|nd|rd|th)(?:\s*(?:[–-]|to(?: the)?)\s*(?:early |mid-?|late )?(\d{1,2})(?:st|nd|rd|th))?\s*(?:-|\s)?centur(?:y|ies)(\s*(?:BCE|BC))?", re.I)
YEARS = re.compile(r"(?<![\d.])(\d{3,4})(?:\s*[–-]\s*(\d{2,4}))?(\s*(?:BCE|BC))?(?![\d])")


def span(text):
    if not text:
        return None
    t = re.sub(r"<[^>]+>", "", text); pts = []
    for m in CENT.finditer(t):
        a = int(m.group(1)); b = int(m.group(2) or a)
        pts += [-100 * a, -100 * (b - 1)] if m.group(3) else [100 * (a - 1), 100 * b]
    for m in YEARS.finditer(CENT.sub(" ", t)):
        a = int(m.group(1))
        if not (300 <= a <= 2030) and not m.group(3):
            continue
        b = int(m.group(2)) if m.group(2) else a
        if m.group(2) and b < 100:
            b = (a // 100) * 100 + b
        if m.group(3):
            a, b = -a, -b
        pts += [a, b]
    return (min(pts), max(pts)) if pts else None


class Resolver:
    def __init__(self):
        t = json.load(open(os.path.join(DATA, "tree.json")))["va"]
        rows = {}
        for p in glob.glob(os.path.join(DATA, "m-va-*.json")):
            rows.update(json.load(open(p)))
        self.leaves = {}
        for f in t["fams"]:
            for s in f["subs"]:
                for l in s["leaves"]:
                    self.leaves[l["code"]] = dict(l, fam=f["code"], sub_label=s["label"])
        # culture compatibility: leaf text, plus cultures whose labels already map to the leaf
        self.text = {c: fold(" ".join([l["label"], l.get("aliases") or "", l.get("defn") or "", l["sub_label"]] + lit(l.get("alias_rows"), [])))
                     for c, l in self.leaves.items()}
        self.mapped_heads = collections.defaultdict(set)
        for f in glob.glob(os.path.join(O, "out_col_*.csv")):
            for r in csv.DictReader(open(f)):
                if r["map"] in self.leaves:
                    self.mapped_heads[r["map"]].add(head(r["label"]))
        self.span = {c: span(l.get("defn")) for c, l in self.leaves.items()}
        names = collections.defaultdict(lambda: collections.defaultdict(set))  # fam -> name -> leaves
        # which cultures each label word belongs to ("goryeo" -> korea, "edo" -> japan), from labels with >= 200 objects
        self.word_heads = collections.defaultdict(set)
        for r in csv.DictReader(open(os.path.join(O, "label_keys.csv"))):
            if int(r["objects"] or 0) >= 200:
                h = head(r["label"])
                for w in fold(r["label"]).split():
                    if len(w) > 3 and w not in GENERIC:
                        self.word_heads[w].add(h)
        self.labeltext = {c: fold(" ".join([l["label"], l.get("aliases") or "", l["sub_label"]] + lit(l.get("alias_rows"), [])))
                          for c, l in self.leaves.items()}
        for c, l in self.leaves.items():
            if l["fam"] not in "ABCDEFGHIJ":
                continue
            cand = [l["label"]] + [a for a in re.split(r";\s*", l.get("aliases") or "") if a] + lit(l.get("alias_rows"), [])
            cand += [r[0] for r in rows.get(c, []) if r[1] in NAME_GROUPS and not r[4]]
            for n in cand:
                for v in {fold(n), fold(re.sub(r"\s*\(.*?\)", "", n))}:
                    w = v.split()
                    if not w or len(v) < 4 or v in GENERIC or all(x in GENERIC for x in w):
                        continue
                    names[l["fam"]][v].add(c)
        self.rx = {}
        self.name_leaf = {}
        for fam, d in names.items():
            uniq = {n: next(iter(cs)) for n, cs in d.items() if len(cs) == 1}
            self.name_leaf[fam] = uniq
            self.rx[fam] = self._rx(uniq)
        allnames = collections.defaultdict(set)
        for fam, d in names.items():
            for n, cs in d.items():
                allnames[n] |= cs
        self.name_leaf["*"] = {n: next(iter(cs)) for n, cs in allnames.items() if len(cs) == 1}
        self.rx["*"] = self._rx(self.name_leaf["*"])

    @staticmethod
    def _rx(names):
        # longest names first, so "Imari ware" wins over "Imari"; plural endings allowed
        alt = "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
        return re.compile(rf"\b({alt})(?:s|es|en)?\b") if alt else None

    def culture_ok(self, code, h):
        if not h:
            return True
        if h in self.mapped_heads.get(code, ()):
            return True
        stem = STEM.get(h, re.escape(h[:5]))
        if re.search(rf"\b({stem})", self.labeltext[code]):
            return True
        if not re.search(rf"\b({stem})", self.text[code]):
            return False
        other = [w for w in self.labeltext[code].split() if self.word_heads.get(w) and h not in self.word_heads[w]]
        return not other

    def resolve(self, fam, label, title, date):
        t = fold(title)
        if not t:
            return None
        t = " ".join(VARIANTS.get(w, w) for w in t.split())
        return self._match(fam, label, t, date) or self._match("*", label, t, date)

    def _match(self, fam, label, t, date):
        rx = self.rx.get(fam)
        if not rx:
            return None
        h = head(label)
        try:
            y = int(str(date).strip()[:5]) if str(date).strip() else None
        except ValueError:
            y = None
        for m in rx.finditer(t):
            code = self.name_leaf[fam][m.group(1)]
            if not self.culture_ok(code, h):
                continue
            sp = self.span.get(code)
            if y is not None and sp and not (sp[0] - 50 <= y <= sp[1] + 50):
                continue
            return code
        return None


def load_maps():
    M = {}
    for f in glob.glob(os.path.join(O, "out_col_*.csv")):
        for r in csv.DictReader(open(f)):
            M[(r["file"], r["label"], r["family"])] = r["map"].strip()
    return M


def main():
    R = Resolver(); M = load_maps()
    agg = collections.Counter()
    cells = collections.defaultdict(lambda: [0, 0, collections.Counter(), collections.Counter()])  # total, resolved, leaves, residual words
    STOPW = GENERIC | set("with from and for the van een met het voor uit der des les del con part fragment piece pair set two one model unknown untitled".split())
    with gzip.open(os.path.join(O, "objects_norm.csv.gz"), "rt") as fh:
        for r in csv.DictReader(fh):
            m = M.get((r["file"], r["label"], r["family"]), "")
            if not m.startswith("general:"):
                continue
            fam = m.split(":", 1)[1]
            code = R.resolve(fam, r["label"], r["title"], r["date_begin"])
            cell = cells[(head(r["label"]), fam)]; cell[0] += 1
            if code:
                agg[(r["file"], r["label"], r["family"], code)] += 1; cell[1] += 1; cell[2][code] += 1
            else:
                cell[3].update({w for w in fold(r["title"]).split() if len(w) > 3 and w not in STOPW and not w.isdigit()})
    with open(os.path.join(O, "object_resolve.csv"), "w", newline="") as fo:
        w = csv.writer(fo); w.writerow(["file", "label", "family", "leaf", "objects"])
        for k, n in sorted(agg.items(), key=lambda x: -x[1]):
            w.writerow(list(k) + [n])
    os.makedirs(os.path.join(ROOT, "taxonomy/audit/va_completeness"), exist_ok=True)
    with open(os.path.join(ROOT, "taxonomy/audit/va_completeness/v3_cells.csv"), "w", newline="") as fo:
        w = csv.writer(fo); w.writerow(["culture", "family", "general_objects", "resolved", "resolved_share", "top_leaves", "residual_title_words"])
        for (cu, fam), (n, k, lv, res) in sorted(cells.items(), key=lambda x: -x[1][0]):
            if n < 500:
                continue
            w.writerow([cu, fam, n, k, f"{k / n:.0%}", "; ".join(f"{c} {R.leaves[c]['label']} ({x})" for c, x in lv.most_common(5)),
                        "; ".join(f"{x} ({c})" for x, c in res.most_common(25))])
    tot = sum(c[0] for c in cells.values()); res = sum(c[1] for c in cells.values())
    print(f"general objects {tot:,}; resolved to a leaf by title {res:,} ({res / tot:.1%}); leaves gaining objects {len({k[3] for k in agg})}")


if __name__ == "__main__":
    main()
