"""Scan gathered object files: python3 scan3.py OUTNAME file1.csv ... -> objects_OUTNAME.json
Match regex on title + culture/node fields; need regex on title + object type; drop regex on title + culture."""
import csv, re, json, os, sys
csv.field_size_limit(10**9)
HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "../../../../data/interim/regional")
spec = []
for line in open(os.path.join(HERE, "spec.tsv"), encoding="utf-8"):
    if not line.strip(): continue
    p = line.rstrip("\n").split("\t") + ["", ""]
    spec.append((p[0], re.compile(p[1], re.I), re.compile(p[2], re.I) if p[2] else None, re.compile(p[3], re.I) if p[3] else None))
pre = re.compile("|".join("(?:%s)" % s[1].pattern for s in spec), re.I)
F = {
 "world_folk_objects.csv": (["node_label", "title", "culture"], ["title"], "title", "date", "institution", "url"),
 "europe_folk_objects.csv": (["node_key", "title", "culture"], ["title", "node_key"], "title", "date", "institution", "url"),
 "gap_sweep_objects.csv": (["node_label", "title"], ["title", "object_group"], "title", "date_begin", "institution", "url"),
 "africa_objects.csv": (["title", "culture", "culture_group"], ["title", "object_type", "object_group"], "title", "date_begin", "institution", "url"),
 "africa_oceania_targeted_objects.csv": (["title", "culture", "culture_group"], ["title", "object_type", "object_group"], "title", "date_begin", "institution", "url"),
 "americas_oceania_objects.csv": (["title", "culture", "culture_group"], ["title", "object_type", "object_group"], "title", "date_begin", "institution", "url"),
 "south_southeast_asia_objects.csv": (["title", "culture", "culture_group"], ["title", "object_type", "object_group"], "title", "date_begin", "institution", "url"),
 "east_asia_objects.csv": (["title", "title_en"], ["title", "title_en", "object_type", "object_subtype"], "title_en|title", "date_begin", "holder", "url"),
 "himalaya_central_asia_objects.csv": (["title", "tradition"], ["title", "object_type"], "title", "date_begin", "institution", "url"),
 "islamic_objects.csv": (["title", "dynasty", "culture_place"], ["title", "object_type", "techniques"], "title", "date_begin", "institution", "url"),
 "smithsonian_objects.csv": (["title", "culture", "school_style"], ["title", "object_type", "object_name"], "title", "begin_year", "unit", "record_link"),
 "world_extra_objects.csv": (["title", "culture_label"], ["title", "object_type", "object_group"], "title", "date_begin", "institution", "url"),
}
UNITS = {"CHNDM": "Cooper Hewitt, Smithsonian Design Museum", "NMAI": "National Museum of the American Indian", "NMAH": "National Museum of American History",
         "NMNHANTHRO": "National Museum of Natural History", "NMNH": "National Museum of Natural History", "NMAfA": "National Museum of African Art",
         "FSG": "National Museum of Asian Art", "NMAA": "National Museum of Asian Art", "SAAM": "Smithsonian American Art Museum", "HMSG": "Hirshhorn Museum",
         "NPG": "National Portrait Gallery", "ACM": "Anacostia Community Museum", "NMAAHC": "National Museum of African American History and Culture",
         "Smithsonian National Museum of the American Indian": "National Museum of the American Indian", "The British Museum": "British Museum",
         "Metropolitan Museum of Art": "The Metropolitan Museum of Art", "Wereldmuseum (NMVW)": "Wereldmuseum"}
name = sys.argv[1]
out = {s[0]: {} for s in spec}
for fn in sys.argv[2:]:
    mf, nf, tf, df, inf, uf = F[fn]
    with open(os.path.join(REG, fn), encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            vals = [r.get(k) or "" for k in mf]
            if not pre.search(" | ".join(vals)): continue
            url = r.get(uf) or ""
            if not url: continue
            needtxt = " | ".join(r.get(k) or "" for k in nf)
            t = ""
            for k in tf.split("|"):
                if r.get(k): t = r[k]; break
            cul = " ".join(v for v in vals[1:] if v)[:80] if mf[0] != "title" else " ".join(v for v in vals[1:] if v)[:80]
            droptxt = t + " | " + " ".join(vals)
            for code, rx, need, drop in spec:
                if url in out[code]: continue
                if any(rx.search(v) for v in vals if v) and (need is None or need.search(needtxt)) and (drop is None or not drop.search(droptxt)):
                    inst = r.get(inf) or ""
                    out[code][url] = [t, r.get(df) or "", UNITS.get(inst, inst), fn.split("_objects")[0], cul]
    print(fn, "done", file=sys.stderr, flush=True)
json.dump(out, open(os.path.join(HERE, "objects_%s.json" % name), "w"), ensure_ascii=False)
