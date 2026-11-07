"""R3 collections cross-reference, step 1: normalise every gathered object record.

One row per object: file, institution, label (the source's own tradition label: culture / dynasty /
tradition / period / node), family (VA medium family letter from the object type), url.
Writes taxonomy/r3/collections/objects_norm.csv.gz and label_keys.csv (distinct label × family with
counts, top institutions, a sample title and the seed mapping from taxonomy/visual_art/va_placements.csv).
"""
import csv, gzip, os, re, collections
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
I = os.path.join(ROOT, "data", "interim"); OUT = os.path.join(ROOT, "taxonomy", "r3", "collections")
csv.field_size_limit(10**9)
FAM = [(r"manuscript|album|folio|book|qur|calligraph|codex|sutra|scroll paint|miniature", "C"),
       (r"paint|thangka|icon|fresco|mural", "A"), (r"print|woodblock|drawing|etching|engraving|lithograph|poster", "B"),
       (r"photo", "J"), (r"ceramic|pottery|porcelain|earthenware|stoneware|tile|terracotta|vase|bowl|jar|dish|plate|ewer|celadon|faience|majolica", "E"),
       (r"glass", "F"), (r"textile|carpet|rug|kilim|cloth|costume|dress|garment|robe|embroider|lace|weav|tapestry|shawl|sari|batik|ikat|quilt|hat|shoe|bead|basket|feather|bark", "H"),
       (r"jewel|ornament|necklace|bracelet|earring|ring\b|brooch|amulet", "G"), (r"arms|armou?r|sword|dagger|helmet|shield|spear|gun", "G"),
       (r"metal|bronze|silver|gold|brass|copper|iron|coin|mirror", "G"), (r"lacquer|furniture|wood|chest|cabinet|musical|instrument|drum|box", "I"),
       (r"sculpt|statue|figure|figurine|relief|mask|carving|ivory|jade|stone|idol|stele|puppet", "D")]
def fam_of(t):
    t = (t or "").lower()
    for rx, f in FAM:
        if re.search(rx, t): return f
    return "?"
def rows():
    def R(fn): return csv.DictReader(open(os.path.join(I, fn), encoding="utf-8", errors="replace"))
    for f in ("africa", "africa_oceania_targeted", "americas_oceania", "south_southeast_asia"):
        for r in R(f"regional/{f}_objects.csv"):
            yield f, r["institution"], r["culture"] or r["culture_group"] or r["place"], r["object_type"] + " " + r["object_group"] + " " + r["materials"], r["url"], r["title"], r["date_begin"]
    for r in R("regional/east_asia_objects.csv"):
        yield "east_asia", r["holder"], (r["country"] + " · " + (r["period_en"] or r["period_original"])), r["object_type"] + " " + r["object_subtype"], r["url"], r["title_en"] or r["title"], r["date_begin"]
    for r in R("regional/europe_folk_objects.csv"):
        yield "europe_folk", r["institution"], r["node_key"], r["medium"] + " " + r["title"], r["url"], r["title"], ""
    for r in R("regional/world_folk_objects.csv"):
        yield "world_folk", r["institution"], r["node_label"], r["medium"] + " " + r["title"], r["url"], r["title"], ""
    for r in R("regional/gap_sweep_objects.csv"):
        yield "gap_sweep", r["institution"], r["node_label"], r["object_group"] + " " + r["title"], r["url"], r["title"], r["date_begin"]
    for r in R("regional/himalaya_central_asia_objects.csv"):
        yield "himalaya_central_asia", r["institution"], r["tradition"] or r["tradition_recorded"], r["object_type"] + " " + r["medium"] + " " + r["materials"], r["url"], r["title"], r["date_begin"]
    for r in R("regional/islamic_objects.csv"):
        lab = r["dynasty"] or r["dynasty_recorded"] or r["culture_place"]
        if r["school_workshop"]: lab += " · " + r["school_workshop"]
        yield "islamic", r["institution"], lab, r["object_type"] + " " + r["materials_technique"] + (" manuscript" if r["book_arts"] in ("1", "True", "true") else ""), r["url"], r["title"], r["date_begin"]
    for r in R("regional/smithsonian_objects.csv"):
        yield "smithsonian", "Smithsonian (" + r["unit"] + ")", r["culture"] or r["culture_indexed"] or r["school_style"], r["object_type"] + " " + r["object_name"] + " " + r["medium"], r["record_link"], r["title"], r["begin_year"]
    for r in R("regional/world_extra_objects.csv"):
        yield "world_extra", r["institution"], r["culture_label"], r["object_type"] + " " + r["object_group"] + " " + r["materials"], r["url"], r["title"], r["date_begin"]
    for r in R("manuscripts_items.csv"):
        yield "manuscripts", (r["collections"] or "").split(";")[0].strip(), r["tradition"], "manuscript", "https://www.wikidata.org/wiki/" + r["qid"], r["label"], r["year"]

def main():
    os.makedirs(OUT, exist_ok=True)
    seed = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "taxonomy/visual_art/va_placements.csv"))):
        d = r["disposition"]
        if r["source"] in ("artists", "possession", "evidence"): continue
        seed[(r["source"], r["label"].strip().lower())] = d
    src_alias = {"islamic": "islamic_makers", "east_asia": "east_asia", "himalaya_central_asia": "himalaya_central_asia"}
    keys = collections.defaultdict(lambda: [0, collections.Counter(), ""])
    n = 0
    with gzip.open(os.path.join(OUT, "objects_norm.csv.gz"), "wt", newline="") as fo:
        w = csv.writer(fo); w.writerow(["file", "institution", "label", "family", "url", "title", "date_begin"])
        for file, inst, lab, kind, url, title, d in rows():
            lab = (lab or "").strip(); fam = fam_of(kind)
            if not lab: continue
            w.writerow([file, inst, lab, fam, url, title, d]); n += 1
            k = keys[(file, lab, fam)]; k[0] += 1; k[1][inst] += 1
            if not k[2] and title: k[2] = title[:80]
    with open(os.path.join(OUT, "label_keys.csv"), "w", newline="") as fo:
        w = csv.writer(fo); w.writerow(["file", "label", "family", "objects", "institutions", "top_institutions", "sample_title", "seed"])
        for (file, lab, fam), (c, insts, sample) in sorted(keys.items(), key=lambda x: -x[1][0]):
            sd = seed.get((file, lab.lower())) or seed.get(("met/aic", lab.lower())) or ""
            w.writerow([file, lab, fam, c, len(insts), "; ".join(f"{i} ({m})" for i, m in insts.most_common(4)), sample, sd])
    print("objects", n, "label keys", len(keys))

if __name__ == "__main__":
    main()
