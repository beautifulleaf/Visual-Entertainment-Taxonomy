"""R3 collections cross-reference, step 3: leaf × institution table from the label mappings.

Reads taxonomy/r3/collections/out_col_*.csv (label key → leaf / general / missing / exclude),
objects_norm.csv.gz (per-object institution) and in_col_met.csv (Met/AIC culture counts) and writes
  leaf_institutions.json  {leaf: [[institution, objects, search_url], ...]} ranked
  missing_traditions.csv  candidate traditions with no leaf (label, family, objects, institutions)
  family_general.json     objects per family that map to no single leaf
Institution search links use each institution's real search pattern with the institution's own label as the
query; institutions without a known pattern get no link (their home page is not guessed).
"""
import csv, gzip, json, os, re, collections, urllib.parse
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
O = os.path.join(ROOT, "taxonomy", "r3", "collections")
csv.field_size_limit(10**9)
SEARCH = [  # (institution name pattern, search URL template with {q})
    (r"^The Metropolitan Museum of Art", "https://www.metmuseum.org/art/collection/search?q={q}"),
    (r"^Victoria and Albert Museum|^V&A", "https://collections.vam.ac.uk/search/?q={q}"),
    (r"^British Museum", "https://www.britishmuseum.org/collection/search?keyword={q}"),
    (r"^Art Institute of Chicago", "https://www.artic.edu/collection?q={q}"),
    (r"^Cleveland Museum of Art", "https://www.clevelandart.org/art/collection/search?search={q}"),
    (r"^Rijksmuseum", "https://www.rijksmuseum.nl/en/search?q={q}"),
    (r"^Museum Volkenkunde|^Tropenmuseum|^Wereldmuseum|^Afrika Museum", "https://collectie.wereldculturen.nl/#/query/{q}"),
    (r"^Smithsonian \(NMAI\)|^Smithsonian National Museum of the American Indian", "https://collections.si.edu/search/results.htm?q={q}&fq=data_source%3A%22National+Museum+of+the+American+Indian%22"),
    (r"^Smithsonian \(NMAA\)", "https://asia.si.edu/explore-art-culture/collections/search/?edan_q={q}"),
    (r"^Smithsonian \(SAAM\)", "https://americanart.si.edu/search?query={q}"),
    (r"^Smithsonian", "https://collections.si.edu/search/results.htm?q={q}"),
    (r"^Tokyo National Museum|^Kyoto National Museum|^Nara National Museum|^Kyushu National Museum|National Research Institute for Cultural Properties", "https://colbase.nich.go.jp/collection_items?locale=en&q={q}"),
    (r"^Penn Museum|^University of Pennsylvania", "https://www.penn.museum/collections/search.php?term={q}"),
    (r"^Museum of New Zealand Te Papa", "https://collections.tepapa.govt.nz/search/{q}"),
    (r"^Minneapolis Institute of Art", "https://collections.artsmia.org/search/{q}"),
    (r"^Yale University", "https://artgallery.yale.edu/collection?q={q}"),
    (r"^Cooper Hewitt", "https://collection.cooperhewitt.org/search/collection/?query={q}"),
    (r"^Rubin Museum|^Zanabazar|^Private", "https://www.himalayanart.org/search/results.cfm?searchterm={q}"),
    (r"^Bibliothèque nationale de France", "https://gallica.bnf.fr/services/engine/search/sru?operation=searchRetrieve&query=(gallica%20all%20%22{q}%22)"),
    (r"^British Library", "https://www.bl.uk/manuscripts/Search.aspx?q={q}"),
    (r"^Bodleian Library", "https://digital.bodleian.ox.ac.uk/search/?q={q}"),
    (r"goskatalog|^Федеральное|^Государственное|^Бюджетное|^Краевое|Музей|музей", "https://goskatalog.ru/portal/#/collections?q={q}"),
    (r"^국립|^National Museum of Korea", "https://www.emuseum.go.kr/search?keyword={q}"),
    (r"^National Palace Museum", "https://digitalarchive.npm.gov.tw/Collection/Search?keyword={q}"),
]
def canon(inst):
    """One row per museum: departments merge into the museum (Smithsonian units are separate museums)."""
    inst = (inst or "").strip()
    if inst.startswith("Smithsonian"): return inst
    if inst in ("V&A",): return "Victoria and Albert Museum"
    return re.sub(r"\s*\((?:SSEA|EAS|Indian and Southeast Asian Art|[^)]*Department[^)]*)\)$", "", inst)

def link(inst, q):
    for rx, t in SEARCH:
        if re.search(rx, inst or ""): return t.replace("{q}", urllib.parse.quote(q))
    return ""

STOP = {"art", "ware", "wares", "pottery", "painting", "sculpture", "of", "the", "and", "school", "style", "work", "works", "ceramics", "textiles"}
def words(t): return {w for w in re.findall(r"[a-zà-ÿ]+", (t or "").lower()) if len(w) > 2 and w not in STOP}

def main():
    leaves = {r["code"]: r for r in csv.DictReader(open(os.path.join(O, "va_leaves.tsv")), delimiter="\t")}
    M = {}
    for f in glob_outs():
        for r in csv.DictReader(open(f)): M[(r["file"], r["label"], r["family"])] = r["map"].strip()
    LI = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, collections.Counter()]))
    general = collections.Counter(); missing = collections.defaultdict(lambda: [0, collections.Counter()])
    with gzip.open(os.path.join(O, "objects_norm.csv.gz"), "rt") as f:
        for r in csv.DictReader(f):
            m = M.get((r["file"], r["label"], r["family"]), "")
            if not m or m.startswith("exclude"): continue
            if m.startswith("general"): general[m.split(":", 1)[1]] += 1; continue
            if m.startswith("missing"):
                x = missing[(m.split(":", 1)[1], r["family"])]; x[0] += 1; x[1][canon(r["institution"])] += 1; continue
            cell = LI[m][canon(r["institution"]) or "(institution not recorded)"]; cell[0] += 1; cell[1][r["label"]] += 1
    for r in csv.DictReader(open(os.path.join(O, "in_col_met.csv"))):  # Met/AIC culture counts
        m = M.get((r["file"], r["label"], r["family"]), "")
        if not m or ":" in m or m not in leaves: continue
        L = leaves[m]
        if len(words(r["label"])) < 2 and "," not in r["label"]: continue  # bare culture or period ("Egyptian", "Roman")
        if not (words(r["label"]) & (words(L["label"]) | words(L["aliases"]) | words(L["defn"][:160]))):
            continue  # Met guard: a broad culture label ("Egyptian", "American", "Archaic") does not count for one leaf
        n = int(r["objects"]); LI[m]["The Metropolitan Museum of Art"][0] += n; LI[m]["The Metropolitan Museum of Art"][1][r["label"]] += n
    out = {}
    for leaf, insts in LI.items():
        rows = sorted(insts.items(), key=lambda x: -x[1][0])
        q = leaves[leaf]["label"] if leaf in leaves else c0(rows)
        out[leaf] = [[i, c[0], link(i, q)] for i, c in rows if c[0] >= 3][:25]
    json.dump(out, open(os.path.join(O, "leaf_institutions.json"), "w"), ensure_ascii=False, indent=0)
    json.dump(general, open(os.path.join(O, "family_general.json"), "w"), indent=1)
    mi = collections.defaultdict(collections.Counter)
    for (t, fam), (n, ic) in missing.items(): mi[t].update(ic)
    json.dump({t: [[i, n, link(i, t)] for i, n in c.most_common(25) if n >= 3] for t, c in mi.items()},
              open(os.path.join(O, "missing_institutions.json"), "w"), ensure_ascii=False, indent=0)
    with open(os.path.join(O, "missing_traditions.csv"), "w", newline="") as fo:
        w = csv.writer(fo); w.writerow(["tradition", "family", "objects", "institutions", "top_institutions"])
        for (t, fam), (n, ic) in sorted(missing.items(), key=lambda x: -x[1][0]):
            w.writerow([t, fam, n, len(ic), "; ".join(f"{i} ({c})" for i, c in ic.most_common(4))])
    print("leaves with holdings", len(out), "| missing traditions", len(missing), "| general by family", dict(general))

def c0(rows): return rows[0][1][1].most_common(1)[0][0] if rows else ""

def glob_outs():
    import glob
    return sorted(glob.glob(os.path.join(O, "out_col_*.csv")))

if __name__ == "__main__":
    main()
