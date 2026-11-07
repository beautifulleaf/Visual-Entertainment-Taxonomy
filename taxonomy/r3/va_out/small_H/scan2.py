"""Scan gathered object files for every leaf's match spec -> objects.json"""
import csv, re, json, os, sys
csv.field_size_limit(10**9)
HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "../../../../data/interim/regional")
spec = []
for line in open(os.path.join(HERE, "spec.tsv"), encoding="utf-8"):
    if not line.strip(): continue
    p = line.rstrip("\n").split("\t")
    code, rx, need = p[0], p[1], (p[2] if len(p) > 2 else "")
    spec.append((code, re.compile(rx, re.I), re.compile(need, re.I) if need else None))
pre = re.compile("|".join("(?:%s)" % s[1].pattern for s in spec), re.I)

# file -> (match fields, need fields, title, date, inst, url, source-ish)
F = {
 "world_folk_objects.csv": (["node_label", "title", "culture"], ["title", "medium", "node_label"], "title", "date", "institution", "url"),
 "europe_folk_objects.csv": (["node_key", "title", "culture"], ["title", "medium", "node_key"], "title", "date", "institution", "url"),
 "gap_sweep_objects.csv": (["node_label", "title", "labels", "place"], ["title", "labels", "object_group", "node_label"], "title", "date_begin", "institution", "url"),
 "africa_objects.csv": (["title", "culture", "culture_group", "place"], ["title", "object_type", "object_group", "materials"], "title", "date_begin", "institution", "url"),
 "africa_oceania_targeted_objects.csv": (["title", "culture", "culture_group", "place"], ["title", "object_type", "object_group", "materials"], "title", "date_begin", "institution", "url"),
 "americas_oceania_objects.csv": (["title", "culture", "culture_group", "place"], ["title", "object_type", "object_group", "materials"], "title", "date_begin", "institution", "url"),
 "south_southeast_asia_objects.csv": (["title", "culture", "culture_group", "place"], ["title", "object_type", "object_group", "materials"], "title", "date_begin", "institution", "url"),
 "east_asia_objects.csv": (["title", "title_en", "object_subtype"], ["title", "title_en", "object_type", "object_subtype"], "title_en|title", "date_begin", "holder", "url"),
 "himalaya_central_asia_objects.csv": (["title", "tradition", "place_recorded"], ["title", "object_type", "medium", "materials"], "title", "date_begin", "institution", "url"),
 "islamic_objects.csv": (["title", "dynasty", "culture_place", "production_centre"], ["title", "object_type", "materials_technique", "techniques"], "title", "date_begin", "institution", "url"),
 "smithsonian_objects.csv": (["title", "culture", "place", "school_style"], ["title", "object_type", "object_name", "medium", "technique"], "title", "begin_year", "unit", "record_link"),
 "world_extra_objects.csv": (["title", "culture_label", "place"], ["title", "object_type", "object_group", "materials"], "title", "date_begin", "institution", "url"),
}
UNITS = {"CHNDM": "Cooper Hewitt, Smithsonian Design Museum", "NMAI": "National Museum of the American Indian", "NMAH": "National Museum of American History",
         "NMNHANTHRO": "National Museum of Natural History", "NMAfA": "National Museum of African Art", "FSG": "National Museum of Asian Art", "SAAM": "Smithsonian American Art Museum",
         "NMNH": "National Museum of Natural History", "NMNHANTH": "National Museum of Natural History", "HMSG": "Hirshhorn Museum", "NPG": "National Portrait Gallery", "ACM": "Anacostia Community Museum", "NMAAHC": "National Museum of African American History and Culture"}
out = {s[0]: {} for s in spec}
ONLY = sys.argv[1:] or list(F)
for fn, (mf, nf, tf, df, inf, uf) in [(k, F[k]) for k in ONLY]:
    path = os.path.join(REG, fn)
    n = 0
    with open(path, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            n += 1
            vals = [r.get(k) or "" for k in mf]
            joined = " | ".join(vals)
            if not pre.search(joined): continue
            needtxt = " | ".join(r.get(k) or "" for k in nf)
            url = r.get(uf) or ""
            if not url: continue
            for code, rx, need in spec:
                if any(rx.search(v) for v in vals if v) and (need is None or need.search(needtxt)):
                    if url in out[code]: continue
                    t = ""
                    for k in tf.split("|"):
                        if r.get(k): t = r[k]; break
                    inst = r.get(inf) or ""
                    inst = UNITS.get(inst, inst)
                    d = r.get(df) or ""
                    out[code][url] = [t, d, inst, fn.split("_objects")[0], (r.get("culture") or r.get("culture_label") or r.get("dynasty") or r.get("node_label") or "")[:60]]
    print(fn, n, file=sys.stderr)
json.dump(out, open(os.path.join(HERE, "objects_" + ("all" if not sys.argv[1:] else sys.argv[1].split("_")[0]) + ".json"), "w"), ensure_ascii=False)
for c in out: print(c, len(out[c]))
