"""Visual Art scale-up: per-region candidate pools with the inclusion rule applied.

Each tradition row the coverage audit placed in a region (va_pool.py) is joined
back to its source row for evidence, then gets the §2.3 inclusion rule (base
culture or tradition with ≥50 objects or any Met Timeline work; thresholds
scaled for smaller collections; curated and designated nodes kept). Rows below
the rule get `exclude:below inclusion rule (§2.3)` here; the rest go to a
region's design-and-placement review.

    python3 pipelines/classify/va_regions.py

Writes taxonomy/visual_art/regions/<slice>_pool.csv (pool_id, source, label,
type, region, era, objects, medium, evidence, disposition).
"""
import collections
import csv
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
D = os.path.join(ROOT, "data", "interim")
REG = os.path.join(D, "regional")
OUT = os.path.join(ROOT, "taxonomy", "visual_art", "regions")

SLICES = {  # slice → audit regions (Islamic world: built in the pilot)
    "south_asia": ["South Asia"], "southeast_asia": ["Southeast Asia"],
    "east_asia": ["China", "Japan", "Korea"], "himalaya_central_asia": ["Himalaya", "Central Asia & Silk Road"],
    "africa": ["Sub-Saharan Africa"], "north_america_indigenous": ["North America (Indigenous)"],
    "mesoamerica_south_america": ["Mesoamerica & Caribbean", "South America"],
    "oceania_australia": ["Oceania (Pacific)", "Australia (Aboriginal)"],
    "ancient_world": ["Ancient Egypt & Nubia", "Ancient Near East", "Greco-Roman & Byzantine Mediterranean"],
    "europe": ["Western Europe", "Central & Eastern Europe", "North America (settler)"],
}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8"))) if os.path.exists(p) else []


def n(x):
    try:
        return float(x or 0)
    except ValueError:
        return 0.0


def ev(r, cols):
    return "; ".join(f"{c}: {r[c][:110]}" for c in cols if r.get(c))


def sources():
    """(source, label) → (type, objects, keep, evidence) from the raw source rows."""
    out = {}
    for r in rd(os.path.join(D, "unattributed_cultures.csv")):
        if r["kind"] in ("culture", "period"):
            keep = n(r["objects"]) >= 50 or n(r["timeline_works"]) > 0
            out["met/aic", r["label"]] = (f"met {r['kind']}", r["objects"], keep,
                                          ev(r, ["parent", "top_classifications", "top_periods", "timeline_works", "begin_median", "aic_objects"]))
    for r in rd(os.path.join(REG, "smithsonian_cultures.csv")):
        if r["kind"] == "culture":
            out["smithsonian", r["culture"]] = (f"smithsonian {r['unit']}", r["objects"], n(r["objects"]) >= 50,
                                                ev(r, ["unit", "period", "top_object_types", "top_media", "begin_median"]))
    for name, src in (("africa_traditions.csv", "africa"), ("americas_oceania_traditions.csv", "americas_oceania"),
                      ("south_southeast_asia_traditions.csv", "south_southeast_asia"),
                      ("africa_oceania_targeted_traditions.csv", "africa_oceania_targeted")):
        for r in rd(os.path.join(REG, name)):
            if r["kind"] == "culture":
                lab = r["culture"] or r["culture_group"]
                out[src, lab] = ("culture", r["objects"], n(r["objects"]) >= 20,
                                 ev(r, ["culture_group", "top_object_groups", "top_periods", "top_cultures", "named_makers", "subregions"]))
    for r in rd(os.path.join(REG, "east_asia_traditions.csv")):
        out["east_asia", f'{r["country"]} {r["period_en"]}'] = ("country × period", r["all_objects"], n(r["all_objects"]) >= 50,
                                                               ev(r, ["object_type", "top_kilns_workshops", "attributed_share", "examples"]))
    for r in rd(os.path.join(REG, "himalaya_central_asia_traditions.csv")):
        if r["kind"] == "tradition":
            out["himalaya_central_asia", r["tradition"]] = ("tradition", r["objects"], True,
                                                            ev(r, ["region", "top_object_types", "top_places", "named_makers", "mid_median"]))
    for r in rd(os.path.join(REG, "world_extra_cultures.csv")):
        if r["kind"] != "place":
            out["rijks/wereldmuseum", r["label"]] = (f"rijks {r['level']}", r["objects"], n(r["objects"]) >= 30 and r["level"] == "base",
                                                     ev(r, ["parent", "countries", "object_groups", "top_makers", "culture_path"]))
    for r in rd(os.path.join(REG, "europe_folk_traditions.csv")):
        keep = n(r["total_objects"]) >= 50 or bool(r["ich_designation"]) or n(r.get("wd_sitelinks")) >= 10
        out["europe_folk", r["label"]] = (f"folk {r['kind']}", r["total_objects"], keep,
                                          ev(r, ["qid", "country", "people", "medium", "ich_designation", "wd_description", "wd_classes"]))
    for r in rd(os.path.join(REG, "world_folk_traditions.csv")):
        keep = r["status"] != "alias-of-existing-cell" and (r["kind"] == "curated" or n(r["total_objects_distinct"]) >= 20
                                                            or bool(r["ich_designation"]) or n(r["wd_sitelinks"]) >= 10)
        out["world_folk", r["label"]] = (f"folk {r['kind']}", r["total_objects_distinct"], keep,
                                         ev(r, ["qid", "aliases", "country", "people", "medium", "status", "ich_designation", "wd_description", "alias_of"]))
    for r in rd(os.path.join(REG, "gap_sweep_traditions.csv")):
        out["gap_sweep", r["label"]] = (f"gap {r['kind']}", r["objects"], True,
                                        ev(r, ["qid", "qid_label", "qid_description", "medium", "era_nominal", "top_named_makers", "wd_top_artists"]))
    for r in rd(os.path.join(D, "in_situ_traditions.csv")):
        out["in_situ", r["label"]] = (f"in situ {r['kind']}", r["n_sites"], True,
                                      ev(r, ["qid", "kind", "country", "era", "n_unesco", "top_exemplars"]))
    for r in rd(os.path.join(D, "manuscripts_traditions.csv")):
        out["manuscripts", r["label"]] = (f"manuscript {r['kind']}", r["n_manuscripts"], True,
                                          ev(r, ["qid", "script_language", "era_rule", "named_illuminators", "sample_manuscripts", "covered_elsewhere"]))
    return out


def main():
    src = sources()
    pool = rd(os.path.join(ROOT, "taxonomy", "visual_art", "pool_traditions.csv"))
    region_slice = {reg: s for s, regs in SLICES.items() for reg in regs}
    os.makedirs(OUT, exist_ok=True)
    rows = collections.defaultdict(list)
    seen = set()
    stats = collections.Counter()
    for p in pool:
        if p["kind"] != "tradition" or p["source"] in ("islamic", "architecture", "architecture_nonwestern"):
            continue
        sl = region_slice.get(p["region"])
        if not sl:
            stats["no region / Islamic world (pilot)"] += 1
            continue
        k = (p["source"], p["label"])
        if (sl, k) in seen:
            continue
        seen.add((sl, k))
        typ, objs, keep, evid = src.get(k, ("", p["objects"], n(p["objects"]) >= 50, ""))
        if p["source"] == "himalaya_central_asia" and k not in src:
            continue  # tradition × period rows: their tradition row carries them
        disp = "" if keep else "exclude:below inclusion rule (§2.3)"
        stats[sl, "review" if keep else "excluded"] += 1
        rows[sl].append({"pool_id": f"{p['source']}:{p['label']}", "source": p["source"], "label": p["label"], "type": typ,
                         "region": p["region"], "era": p["era"], "objects": objs, "medium": p["medium"],
                         "evidence": evid, "disposition": disp})
    for sl, rs in rows.items():
        rs.sort(key=lambda r: (r["disposition"] != "", -n(r["objects"])))
        with open(os.path.join(OUT, f"{sl}_pool.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rs[0]))
            w.writeheader()
            w.writerows(rs)
    for k, v in sorted(stats.items(), key=str):
        print(k, v)


if __name__ == "__main__":
    main()
