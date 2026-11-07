"""R3 restructure: write the Visual Art pass inputs.

taxonomy/r3/va_in/<group>.json  {"leaves": [{code, family, sub, sub_label, label, defn, aliases, see, n, rows}]}
where rows are the published kind rows [name, group, gloss, source, is_maker] plus, for artists,
a dict of evidence {birth, countries, medium, movements} from taxonomy/visual_art/artist_placements.csv.
taxonomy/r3/va_leaf_index.tsv  every VA leaf: code, label, family label, sub label, n.
"""
import csv, glob, json, os, collections
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
D = os.path.join(ROOT, "artifact", "full", "data")
OUT = os.path.join(ROOT, "taxonomy", "r3", "va_in")

GROUPS = {
    # bucket passes (big artist-led leaves)
    "bucket_modern_west": {"leaves": ["A5-110"], "region": "Western Europe"},
    "bucket_modern_world": {"leaves": ["A5-110"], "region": "!Western Europe"},
    "bucket_contemporary": {"leaves": ["A5-111", "D5-119", "M1-1", "M1-2", "M2-5", "L2-51"]},
    "bucket_academic_19c": {"leaves": ["A5-38", "D5-115", "A5-31", "A5-30", "D5-114", "A5-40", "A5-45"]},
    "bucket_modsculpture_photo": {"leaves": ["D5-118", "J1-13", "J1-12", "J1-9", "J1-7", "J1-8"]},
    "bucket_named_movements": {"leaves": ["A5-25", "A5-29", "A5-28", "A5-22", "A5-20", "A5-23", "A5-27", "A5-16", "A5-18",
                                          "D5-113", "D5-112", "D5-111", "B2-13", "A5-56", "A5-47", "A5-81", "A5-51", "A5-49",
                                          "A5-89", "A5-66", "A5-42", "A5-108", "A2-13", "A2-1", "A2-3", "A1-4", "C1-9"]},
    "bucket_print_arch_misc": {"leaves": ["B1-5", "B1-6", "B2-14", "B2-15", "K6-22", "K6-26", "K4-13", "K5-23", "K5-22", "K6-21",
                                          "K2-17", "K2-6", "K2-10", "K6-15", "K5-24", "I3-16", "I3-15", "E1-27", "E1-28", "H1-1", "C2-29"]},
    "design": {"leaves": ["I3-19", "I3-20"]},
}
SMALL = {  # small-leaf passes by family (every leaf with <= 60 kinds that no bucket owns)
    "small_A_B_C": "ABC", "small_D_F": "DF", "small_E": "E", "small_G_I_J_M": "GIJM", "small_H": "H", "small_K": "K", "small_L": "L",
}

def main():
    os.makedirs(OUT, exist_ok=True)
    tree = json.load(open(os.path.join(D, "tree.json")))
    M = {}
    for fn in glob.glob(os.path.join(D, "m-va-*.json")):
        M.update(json.load(open(fn)))
    labels = dict(l.rstrip("\n").split("\t", 1) for l in open(os.path.join(ROOT, "data/interim/visual_art/labels.tsv")) if "\t" in l)
    ev = collections.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(ROOT, "taxonomy/visual_art/artist_placements.csv"))):
        ev[r["label"]].append(r)
    info = {}
    idx = []
    for f in tree["va"]["fams"]:
        for s in f["subs"]:
            for l in s["leaves"]:
                info[l["code"]] = dict(code=l["code"], family=f["label"], sub=s["code"], sub_label=s["label"], label=l["label"],
                                       defn=l["defn"], aliases=l.get("aliases", ""), see=l.get("see", ""), n=l["n"],
                                       alias_rows=l.get("alias_rows", []))
                idx.append([l["code"], l["label"], f["label"], s["label"], str(l["n"])])
    with open(os.path.join(ROOT, "taxonomy/r3/va_leaf_index.tsv"), "w") as fo:
        fo.write("code\tlabel\tfamily\tsub_family\tn\n")
        for r in idx: fo.write("\t".join(r) + "\n")

    def rows_of(code, region=None):
        out = []
        for k in M.get(code, []):
            r = list(k)
            if k[4] or k[1] in ("Artists", "Architects", "Makers"):
                cands = ev.get(k[0], [])
                if cands:
                    e = cands[0]
                    if region:
                        want = region.lstrip("!"); neg = region.startswith("!")
                        if (e["region"] == want) == neg: continue
                    r.append(dict(birth=e["birth"], countries=", ".join(labels.get(q, q) for q in e["countries"].split("|") if q),
                                  medium=e["medium"], movements=e["movement_tags"]))
                elif region and not region.startswith("!"):
                    continue  # unmatched artists go to the world pass
            elif region and region.startswith("!"):
                continue  # non-artist rows go to the West pass only
            out.append(r)
        return out

    owned = set()
    for g, spec in GROUPS.items():
        leaves = []
        for c in spec["leaves"]:
            d = dict(info[c]); d["rows"] = rows_of(c, spec.get("region")); leaves.append(d); owned.add(c)
        json.dump({"leaves": leaves}, open(os.path.join(OUT, g + ".json"), "w"), ensure_ascii=False)
        print(g, len(leaves), sum(len(x["rows"]) for x in leaves))
    for g, fams in SMALL.items():
        leaves = []
        for c, d0 in info.items():
            if c in owned or c[0] not in fams or c[0] == "N": continue
            d = dict(d0); d["rows"] = rows_of(c); leaves.append(d)
        json.dump({"leaves": leaves}, open(os.path.join(OUT, g + ".json"), "w"), ensure_ascii=False)
        print(g, len(leaves), sum(len(x["rows"]) for x in leaves), "empty", sum(1 for x in leaves if not x["rows"]))

if __name__ == "__main__":
    main()
