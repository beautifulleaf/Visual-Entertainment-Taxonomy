import json, os
D = "/home/user/Visual-Entertainment-Taxonomy/taxonomy/r3/resize"
INP = {l["code"]: l for l in json.load(open(f"{D}/in_rz_5.json"))["leaves"]}
OUTF = f"{D}/work_rz_5/out_parts.json"
def load():
    return json.load(open(OUTF)) if os.path.exists(OUTF) else {}
def save(o):
    json.dump(o, open(OUTF, "w"), ensure_ascii=False, indent=1)
def yr(t):
    try: return int(str(t["year"])[:4])
    except: return 0
def sec(t):
    s = t["sec"]
    return int(s) if str(s).isdigit() else 0
def WP(p): return [[f"https://en.wikipedia.org/wiki/{p}", "Wikipedia"]]
