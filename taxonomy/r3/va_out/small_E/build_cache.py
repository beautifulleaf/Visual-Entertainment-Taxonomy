"""Normalise ceramic-looking rows of the gathered regional object files into one pickle.
record: (src, title, ctext, dbeg, inst, url, otype)"""
import csv, os, pickle, re, sys
csv.field_size_limit(10**9)
R = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "interim", "regional")
CER = re.compile(r"ceram|pott|porcel|stoneware|earthenware|fa[iy]ence|terra ?cott|clay|glaz|celadon|majolica|maiolica|\bwares?\b|vase|tile|bowl|\bjar|kiln|sherd|lustre|luster|slip|vessel|ewer|jug|dish|plate|bottle|teapot|tea ?bowl|cup|figurine|amulet|scarab|shabti|ushabti|vessel|陶|磁|窯|焼|瓷|土器|埴輪|碗|壺|皿|瓶|鉢|自기|자기|도기|청자|백자|분청|керам|фаянс|фарфор|глин|изразц|майолик|гончар", re.I)
def num(x):
    try: return int(float(x))
    except: return None
out = []
def add(src, title, ctext, dbeg, inst, url, otype, filt, dtext=""):
    if not url: return
    if not CER.search(filt): return
    out.append((src, (title or "").strip(), ctext, dbeg, inst, url, otype, dtext))
def rd(f):
    return csv.DictReader(open(os.path.join(R, f), encoding="utf-8"))
for f in ["africa_objects.csv", "africa_oceania_targeted_objects.csv", "americas_oceania_objects.csv", "south_southeast_asia_objects.csv"]:
    for r in rd(f):
        ct = " | ".join([r["culture"], r["culture_group"], r["place"], r["labels_recorded"], r["period"], r["materials"]])
        add(f.split("_objects")[0], r["title"], ct, num(r["date_begin"]), r["institution"], r["url"], r["object_type"] or r["object_group"],
            " ".join([r["object_group"], r["object_type"], r["materials"], r["title"]]), r["date_text"])
for r in rd("east_asia_objects.csv"):
    t = r["title_en"] or r["title"]
    ct = " | ".join([r["country"], r["period_original"], r["period_en"], r["object_subtype"], r["designation_en"], r["title"], r["artist_romanised"], r["artist_original"]])
    add("east_asia", t, ct, num(r["date_begin"]), r["holder"], r["url"], r["object_type"],
        " ".join([r["object_type"], r["object_subtype"], r["title"], r["title_en"]]), r["period_en"])
UNIT = {"NMAI": "National Museum of the American Indian", "CHNDM": "Cooper Hewitt, Smithsonian Design Museum", "SAAM": "Smithsonian American Art Museum",
        "NMAA": "National Museum of Asian Art (Freer|Sackler)", "HMSG": "Hirshhorn Museum", "NMAfA": "National Museum of African Art"}
for r in rd("smithsonian_objects.csv"):
    ct = " | ".join([r["culture"], r["culture_indexed"], r["nmai_culture_area"], r["nmai_culture_subarea"], r["nmai_archeol_1"], r["nmai_archeol_2"], r["nmai_archeol_3"], r["place"], r["countries"], r["period"], r["school_style"], r["makers"], r["medium"][:300]])
    add("smithsonian", r["title"], ct, num(r["begin_year"]), UNIT.get(r["unit"], r["unit"]), r["record_link"], r["object_type_indexed"] or r["object_type"],
        " ".join([r["object_type"], r["object_name"], r["object_type_indexed"], r["medium"][:300], r["title"]]), r["date"])
for r in rd("islamic_objects.csv"):
    ct = " | ".join([r["dynasty_recorded"], r["dynasty"], r["culture_place"], r["school_workshop"], r["production_centre"], r["materials_technique"], r["techniques"], r["makers"]])
    add("islamic", r["title"], ct, num(r["date_begin"]), r["institution"], r["url"], r["object_type"],
        " ".join([r["object_type"], r["materials_technique"], r["techniques"], r["title"]]), r["date_text"])
for r in rd("europe_folk_objects.csv"):
    ct = " | ".join(["NODE:" + r["node_key"], r["culture"], r["medium"]])
    add("europe_folk", r["title"], ct, num((re.findall(r"\d{4}", r["date"]) or [None])[0]), r["institution"], r["url"], r["medium"],
        r["medium"] + " " + r["title"], r["date"])
for r in rd("world_folk_objects.csv"):
    ct = " | ".join(["NODE:" + r["node_label"], r["culture"], r["medium"]])
    add("world_folk", r["title"], ct, num((re.findall(r"-?\d{3,4}", r["date"]) or [None])[0]), r["institution"], r["url"], r["medium"],
        r["medium"] + " " + r["title"] + " " + r["node_label"], r["date"])
for r in rd("gap_sweep_objects.csv"):
    ct = " | ".join(["NODE:" + r["node_label"], r["place"], r["labels"]])
    add("gap_sweep", r["title"], ct, num(r["date_begin"]), r["institution"], r["url"], r["object_group"],
        r["object_group"] + " " + r["title"], r["date_text"])
for r in rd("world_extra_objects.csv"):
    ct = " | ".join([r["culture_label"], r["culture_path"], r["place"], r["country"], r["period"], r["maker"], r["materials"]])
    add("world_extra", r["title"], ct, num(r["date_begin"]), r["institution"], r["url"], r["object_type"],
        " ".join([r["object_group"], r["object_type"], r["materials"], r["title"]]), r["period"])
print(len(out))
pickle.dump(out, open(os.path.join(os.path.dirname(__file__), "cache.pkl"), "wb"))
