"""Merge pilot placements, run the census, and write the artifact data.

Inputs
  taxonomy/pilot/islamic_pool.csv               rule dispositions (pilot_islamic.py)
  taxonomy/pilot/review/makers_*_out.csv         reviewed maker dispositions
  taxonomy/pilot/review/jp_films_*_out.csv       film placements
  seeds/classify/film_overrides.csv              hand corrections (tconst, leaf, see_also, note)
Outputs
  taxonomy/pilot/islamic_placements.csv          one row per candidate, final disposition
  taxonomy/pilot/japan_placements.csv            one row per selected Japanese film
  taxonomy/pilot/census.json                     counts per leaf, disposition, flags
  artifact/pilot-data.json                       page data
"""
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
import tree_visual_art as VA  # noqa: E402
import tree_film as FT  # noqa: E402
from attest import resolve  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
P = os.path.join(ROOT, "taxonomy", "pilot")
R = os.path.join(P, "review")
D = os.path.join(ROOT, "data", "interim")


def rd(path):
    return list(csv.DictReader(open(path, encoding="utf-8"))) if os.path.exists(path) else []


def strip(s):
    return re.sub(r"<[^>]+>", "", s)


# ---------------------------------------------------------------- Visual Art
def islamic():
    pool = rd(os.path.join(P, "islamic_pool.csv"))
    rev = {}
    for i in (1, 2, 3):
        for r in rd(os.path.join(R, f"makers_{i}_out.csv")):
            rev[r["pool_id"]] = r
    for r in rd(os.path.join(ROOT, "seeds", "classify", "maker_overrides.csv")):
        rev[r["pool_id"]] = r
    for r in pool:
        if r["pool_id"] in rev:
            r["disposition"] = rev[r["pool_id"]]["disposition"].strip()
            r["note"] = rev[r["pool_id"]].get("note", "")
            r["by"] = "review"
    with open(os.path.join(P, "islamic_placements.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(pool[0]))
        w.writeheader()
        w.writerows(pool)
    return pool


def leaf_index(tree):
    out = {}
    for fam in tree.FAMILIES:
        for s, lab, ax in fam["subs"]:
            for l in tree.LEAVES.get(s, []):
                out[l[0]] = (fam["code"], s, l)
    return out


def va_data(pool):
    LI = leaf_index(VA)
    kinds = defaultdict(list)
    aliases = defaultdict(list)
    attest_rows = defaultdict(list)
    for r in pool:
        d = r["disposition"]
        typ, _, rest = d.partition(":")
        code, _, grp = rest.partition("/")
        if typ == "kind" and code in LI:
            kinds[code].append({"n": r["label"], "g": grp, "note": r["note"], "src": r["source"], "id": r["pool_id"],
                                "maker": r["type"] in ("maker", "architect")})
        elif typ == "alias" and code in LI:
            aliases[code].append(r["label"] + (f" → {grp}" if grp else ""))
        elif typ == "leaf" and code in LI:
            attest_rows[code].append(f"{r['label']} ({r['source']})")
    # attestation for leaves
    names = [n for l in (x[2] for x in LI.values()) for n in l[6].split("|")]
    res = resolve(names)
    fams = []
    for fam in VA.FAMILIES:
        subs = []
        for s, lab, ax in fam["subs"]:
            leaves = []
            for l in VA.LEAVES.get(s, []):
                code = l[0]
                hit = next((res[n] for n in l[6].split("|") if res.get(n) and res[n]["qid"] not in VA.BAD_QID), None)
                src = []
                if hit:
                    src.append(["https://www.wikidata.org/wiki/" + hit["qid"], f"Wikidata {hit['qid']} ({hit['label']})"])
                    if hit.get("enwiki"):
                        src.append(["https://en.wikipedia.org/wiki/" + hit["enwiki"].replace(" ", "_"), "Wikipedia"])
                if code in VA.ATTEST_URLS:
                    src.append([VA.ATTEST_URLS[code], "source page"])
                ks = kinds.get(code, [])
                # group kinds: schools/sub-types first, makers under their group
                groups = []
                for k in ks:
                    if k["g"] and k["g"] not in groups:
                        groups.append(k["g"])
                leaves.append({"code": code, "label": l[1], "breadth": l[2], "defn": l[3], "aliases": l[4], "see": l[5],
                               "src": src, "weak": VA.WEAK.get(code, ""), "gathered": attest_rows.get(code, []),
                               "alias_rows": aliases.get(code, []),
                               "kinds": [[k["n"], k["g"], k["note"], k["src"], 1 if k["maker"] else 0] for k in ks],
                               "groups": groups, "n": len(ks)})
            subs.append({"code": s, "label": lab, "axis": ax, "leaves": leaves, "n": sum(x["n"] for x in leaves)})
        fams.append({"code": fam["code"], "label": fam["label"], "test": fam["test"], "key": fam["key"], "subs": subs,
                     "n": sum(x["n"] for x in subs), "nleaves": sum(len(x["leaves"]) for x in subs)})
    return fams


# ---------------------------------------------------------- Film & Television
def japan():
    fs = {r["tconst"]: r for r in rd(os.path.join(D, "film_selected.csv")) if "JP" in r["countries"].split("|")}
    wd = {r["tconst"]: r for r in rd(os.path.join(D, "film_wikidata.csv"))}
    out = {}
    for i in (1, 2):
        for r in rd(os.path.join(R, f"jp_films_{i}_out.csv")):
            out[r["tconst"]] = {"tconst": r["tconst"], "leaf": r["leaf"].strip(), "see_also": r.get("see_also", ""),
                                "key_step": r.get("key_step", ""), "note": r.get("note", ""), "by": "review"}
    for r in rd(os.path.join(R, "jp_anime.csv")):
        out[r["tconst"]] = {"tconst": r["tconst"], "leaf": "route:FT-E", "see_also": "", "key_step": "family 1",
                            "note": "Japanese animation → Anime family (F8)", "by": "rule"}
    for r in rd(os.path.join(R, "jp_short.csv")):
        out[r["tconst"]] = {"tconst": r["tconst"], "leaf": "route:FT-B", "see_also": "", "key_step": "family 6",
                            "note": "under 40 minutes → Short Film family", "by": "rule"}
    for r in rd(os.path.join(ROOT, "seeds", "classify", "film_overrides.csv")):
        out[r["tconst"]] = {"tconst": r["tconst"], "leaf": r["leaf"], "see_also": r.get("see_also", ""),
                            "key_step": r.get("key_step", ""), "note": r.get("note", ""), "by": "owner-pass"}
    rows = []
    for t, f in fs.items():
        o = out.get(t, {"leaf": "unplaced", "see_also": "", "key_step": "", "note": "", "by": ""})
        w = wd.get(t, {})
        d = "; ".join(v.split(":", 1)[1] for v in w.get("director", "").split("|") if v)
        rows.append({"tconst": t, "title": f["title"], "year": f["year"], "countries": f["countries"], "director": d,
                     "qid": w.get("qid", ""), "leaf": o["leaf"], "see_also": o["see_also"], "key_step": o["key_step"],
                     "note": o["note"], "by": o["by"]})
    with open(os.path.join(P, "japan_placements.csv"), "w", newline="", encoding="utf-8") as f:
        wtr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wtr.writeheader()
        wtr.writerows(rows)
    return rows


def ft_data(rows):
    LI = leaf_index(FT)
    by = defaultdict(list)
    for r in rows:
        code = r["leaf"].split()[0]
        if code in LI:
            by[code].append(r)
    names = [n for l in (x[2] for x in LI.values()) for n in l[6].split("|")]
    res = resolve(names)
    fams = []
    for fam in FT.FAMILIES:
        subs = []
        for s, lab, ax in fam["subs"]:
            leaves = []
            for l in FT.LEAVES.get(s, []):
                ks = sorted(by.get(l[0], []), key=lambda r: int(r["year"] or 0))
                hit = next((res[n] for n in l[6].split("|") if res.get(n)), None)
                src = []
                if hit:
                    src.append(["https://www.wikidata.org/wiki/" + hit["qid"], f"Wikidata {hit['qid']} ({hit['label']})"])
                    if hit.get("enwiki"):
                        src.append(["https://en.wikipedia.org/wiki/" + hit["enwiki"].replace(" ", "_"), "Wikipedia"])
                leaves.append({"code": l[0], "label": l[1], "breadth": l[2], "defn": l[3], "aliases": l[4], "see": l[5],
                               "src": src, "weak": "" if hit else "no Wikidata item found for this label",
                               "kinds": [[k["title"], k["year"], k["director"], k["see_also"], k["note"], k["tconst"], k["qid"]] for k in ks],
                               "n": len(ks)})
            subs.append({"code": s, "label": lab, "axis": ax, "leaves": leaves, "n": sum(x["n"] for x in leaves)})
        fams.append({"code": fam["code"], "label": fam["label"], "test": fam["test"], "key": fam["key"], "subs": subs,
                     "n": sum(x["n"] for x in subs), "nleaves": sum(len(x["leaves"]) for x in subs)})
    return fams


def main():
    pool = islamic()
    jrows = japan()
    va = va_data(pool)
    ft = ft_data(jrows)
    disp = Counter(r["disposition"].split(":")[0] for r in pool)
    bysrc = defaultdict(Counter)
    for r in pool:
        bysrc[r["source"]][r["disposition"].split(":")[0]] += 1
    fdisp = Counter(("route" if r["leaf"].startswith("route") else "leaf" if r["leaf"][:2] in ("A1", "A2") or re.match(r"A\d", r["leaf"]) else r["leaf"]) for r in jrows)
    census = {"va": {"rows": len(pool), "dispositions": disp, "by_source": {k: dict(v) for k, v in bysrc.items()},
                     "leaves": sum(f["nleaves"] for f in va), "kinds": sum(f["n"] for f in va),
                     "empty_leaves": [l["code"] for f in va for s in f["subs"] for l in s["leaves"] if l["n"] == 0]},
              "ft": {"rows": len(jrows), "dispositions": fdisp, "leaves": sum(f["nleaves"] for f in ft),
                     "per_leaf": {l["code"]: l["n"] for f in ft for s in f["subs"] for l in s["leaves"]},
                     "unplaced": [r["title"] for r in jrows if r["leaf"] == "unplaced"]}}
    json.dump(census, open(os.path.join(P, "census.json"), "w"), indent=1, default=dict)
    os.makedirs(os.path.join(ROOT, "artifact"), exist_ok=True)
    data = {"va": {"fams": va, "familyKey": VA.FAMILY_KEY, "precedence": VA.PRECEDENCE, "modifiers": VA.MODIFIERS},
            "ft": {"fams": ft, "familyKey": FT.FAMILY_KEY, "precedence": FT.PRECEDENCE, "modifiers": FT.MODIFIERS},
            "census": census}
    json.dump(data, open(os.path.join(ROOT, "artifact", "pilot-data.json"), "w"), ensure_ascii=False, default=dict)
    print(json.dumps(census, default=dict)[:1500])


if __name__ == "__main__":
    main()
