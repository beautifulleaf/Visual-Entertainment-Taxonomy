"""Visual Art scale-up merge: region proposals → coded leaves and placements.

Each region review (REGION_BRIEF.md) writes <slice>_leaves.csv (temporary ids
L1, L2 …), <slice>_disp.csv (one disposition per open pool row) and
<slice>_kinds.csv (kinds seeded from the evidence). This script gives the new
leaves codes, appended after the pilot leaves of each sub-family in a fixed
slice order (so codes are reproducible), resolves temporary ids and
cross-slice routes ("route:<slice>" with "(L22)" in the note → a kind of that
slice's leaf), and writes:

  taxonomy/visual_art/leaves_scaleup.csv   leaves for tree_visual_art.py
  taxonomy/visual_art/va_placements.csv    one row per pool row and evidence kind

    python3 pipelines/classify/va_merge.py
"""
import csv
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
VA = os.path.join(ROOT, "taxonomy", "visual_art")
R = os.path.join(VA, "review")
SCALEUP = os.path.join(VA, "leaves_scaleup.csv")
SLICES = ["south_asia", "himalaya_central_asia", "southeast_asia", "east_asia", "africa", "ancient_world",
          "mesoamerica_south_america", "north_america_indigenous", "oceania_australia", "europe_other",
          "europe_folk_west", "europe_folk_east", "gapsweep_europe", "architecture_west", "architecture_nonwest", "artists"]
# slices whose input is their own disposition file rather than a region pool
NOPOOL = {"gapsweep_europe", "architecture_west", "architecture_nonwest"}


def ref(codes, sl, r):
    """Resolve a leaf reference: L<n> (this slice), <slice>:L<n>, artists:T<n>, T<n>, or an existing code."""
    r = r.strip()
    if ":" in r and not r.startswith(("http",)):
        osl, tmp = r.split(":", 1)
        return codes.get((osl, tmp.strip()), r)
    if re.fullmatch(r"T\d+", r):
        return codes.get(("artists", r), r)
    return codes.get((sl, r), r)


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8"))) if os.path.exists(p) else []


def pilot_max():
    # pilot leaves only: read the tree without the scale-up file
    if os.path.exists(SCALEUP):
        os.rename(SCALEUP, SCALEUP + ".bak")
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        import tree_visual_art as V
        mx = defaultdict(int)
        for sub, rows in V.LEAVES.items():
            for l in rows:
                mx[sub] = max(mx[sub], int(l[0].rsplit("-", 1)[1]))
        return mx
    finally:
        if os.path.exists(SCALEUP + ".bak"):
            os.rename(SCALEUP + ".bak", SCALEUP)


# the same tradition proposed by two slices: (dropped slice, label) → (kept slice, label)
DUPS = {("artists", "Balinese Painting"): ("southeast_asia", "Balinese Painting"),
        ("artists", "Ancient Greek Painting"): ("ancient_world", "Ancient Greek Painting"),
        ("artists", "Geometric Art"): ("ancient_world", "Geometric Pottery"),
        ("artists", "Black-Figure Pottery"): ("ancient_world", "Black-Figure Pottery"),
        ("artists", "Red-Figure Pottery"): ("ancient_world", "Red-Figure Pottery"),
        ("europe_folk_east", "Blaudruck"): ("europe_folk_west", "Blaudruck"),
        ("east_asia", "Dunhuang Murals"): ("himalaya_central_asia", "Dunhuang Murals"),
        ("artists", "Mexican Muralism"): ("mesoamerica_south_america", "Mexican Muralism"),
        ("artists", "Tingatinga"): ("africa", "Tingatinga Painting"),
        ("artists", "Roman Sculpture"): ("ancient_world", "Roman Sculpture"),
        ("artists", "Cretan School"): ("ancient_world", "Cretan School")}


def main():
    mx = pilot_max()
    codes, leaves = {}, []
    dropped = {}
    for sl in SLICES:
        name = "artist_leaves.csv" if sl == "artists" else f"{sl}_leaves.csv"
        for r in rd(os.path.join(R, name)):
            if (sl, r["label"].strip()) in DUPS:
                dropped[sl, r["tmp"].strip()] = DUPS[sl, r["label"].strip()]
                continue
            sub = r["sub"].strip()
            mx[sub] += 1
            code = f"{sub}-{mx[sub]}"
            codes[sl, r["tmp"].strip()] = code
            leaves.append({"code": code, "sub": sub, "label": r["label"], "breadth": r["breadth"] or "medium",
                           "defn": r["defn"], "aliases": r["aliases"], "see": r["see"], "attest": r["attest"], "slice": sl})
    bylabel = {(l["slice"], l["label"]): l for l in leaves}
    for (sl, tmp), keep in dropped.items():
        k = bylabel.get(keep)
        if k:
            codes[sl, tmp] = k["code"]
    # resolve tmp ids inside 'see' text
    for l in leaves:
        l["see"] = re.sub(r"\bL(\d+)\b", lambda m: codes.get((l["slice"], "L" + m.group(1)), m.group(0)), l["see"])
    with open(SCALEUP, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(leaves[0]))
        w.writeheader()
        w.writerows(leaves)

    def res(sl, d, note):
        typ, _, rest = d.partition(":")
        if typ in ("leaf", "kind", "alias"):
            tgt, _, grp = rest.partition("/")
            tgt = ref(codes, sl, tgt)
            return f"{typ}:{tgt}" + (f"/{grp}" if grp else "")
        if typ == "route":
            other = rest.strip()
            m = re.search(r"\(L(\d+)\)", note or "")
            if other in SLICES and m and (other, "L" + m.group(1)) in codes:
                k = re.search(r"kind ([^,;)]+)", note or "")
                return f"kind:{codes[other, 'L' + m.group(1)]}" + (f"/{k.group(1).strip()}" if k else "")
        return d

    out, stats = [], Counter()
    routes = {(r["slice"], r["pool_id"]): r for r in rd(os.path.join(R, "route_resolution.csv"))}
    for sl in SLICES:
        if sl == "artists":
            continue
        disp = {r["pool_id"]: r for r in rd(os.path.join(R, f"{sl}_disp.csv"))}
        pool = rd(os.path.join(VA, "regions", f"{sl}_pool.csv")) if sl not in NOPOOL else [
            {"pool_id": r["pool_id"], "source": sl, "label": r.get("label", ""), "type": "style" if sl.startswith("arch") else "gap sweep",
             "region": "", "era": "", "objects": "", "disposition": ""} for r in disp.values()]
        for p in pool:
            if sl in NOPOOL and disp.get(p["pool_id"], {}).get("disposition", "") in ("route:west", "route:nonwest"):
                continue  # the other architecture slice holds this row
            d = p["disposition"]
            note = ""
            if not d:
                r = disp.get(p["pool_id"])
                d, note = (r["disposition"], r.get("note", "")) if r else ("unplaced", "")
                d = res(sl, d, note)
                if d.startswith("route") and (sl, p["pool_id"]) in routes:
                    rr = routes[sl, p["pool_id"]]
                    d, note = res(sl, rr["disposition"], rr.get("note", "")), (note + "; " if note else "") + "route resolved: " + rr.get("note", "")
            if sl in NOPOOL and d.startswith("route:"):
                note = (note + "; " if note else "") + f"no home yet ({d[6:]})"
                d = "tag:place"
            out.append({"slice": sl, "pool_id": p["pool_id"], "source": p["source"], "label": p["label"], "type": p["type"],
                        "region": p["region"], "era": p["era"], "objects": p["objects"], "disposition": d, "note": note})
            stats[sl, d.split(":")[0]] += 1
        for k in rd(os.path.join(R, f"{sl}_kinds.csv")):
            code = ref(codes, sl, k["tmp"])
            code = code if re.fullmatch(r"[A-M]\d+-\d+", code or "") else None
            if code:
                out.append({"slice": sl, "pool_id": f"evidence:{sl}:{k['kind']}", "source": "evidence", "label": k["kind"],
                            "type": "kind from evidence", "region": "", "era": "", "objects": "",
                            "disposition": f"kind:{code}" + (f"/{k['group']}" if k.get("group") else ""), "note": k.get("basis", "")})
                stats[sl, "kind (evidence)"] += 1
    # artists: one kind row per placed artist, under its leaf (T… tmp ids, slice:L… ids or existing codes)
    for a in rd(os.path.join(VA, "artist_placements.csv")):
        leaf = a["leaf"].strip()
        if leaf.startswith("exclude"):
            d = leaf
        else:
            if ":" in leaf:
                sl, tmp = leaf.split(":", 1)
                code = codes.get((sl, tmp))
            elif re.fullmatch(r"T\d+", leaf):
                code = codes.get(("artists", leaf))
            else:
                code = leaf
            d = f"kind:{code}/{a['kind'] or 'Artists'}" if code else "unplaced"
        out.append({"slice": "artists", "pool_id": a["qid"], "source": "artists", "label": a["label"], "type": "artist",
                    "region": a["region"], "era": a["birth"], "objects": "", "disposition": d,
                    "note": "; ".join(x for x in (a.get("movement_tags", ""), a.get("note", "") if a.get("confidence") != "low" else "") if x)})
        stats["artists", d.split(":")[0]] += 1
    with open(os.path.join(VA, "va_placements.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(len(leaves), "scale-up leaves;", Counter(l["sub"][0] for l in leaves))
    for k, v in sorted(stats.items()):
        print(k, v)


if __name__ == "__main__":
    main()
