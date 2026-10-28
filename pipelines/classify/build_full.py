"""Build the data for the first full release of the taxonomy page.

Inputs
  Visual Art   pilot Islamic pool (build_pilot.islamic), taxonomy/visual_art/va_placements.csv (region slices,
               artists), tree_visual_art.py (pilot + scale-up leaves)
  Film & TV    taxonomy/film/film_placements.csv, taxonomy/series/{anime,tv,unscripted}_placements.csv, tree_film.py
  Audits       taxonomy/audit/*
Outputs (artifact/full/data/)
  tree.json            families, sub-families and leaves (no members), keys, precedence, modifiers, census, report
  m-<tab>-<fam>.json   members per leaf of one family: {leaf: [[...], ...]}, fetched when a leaf opens
  find.json            finder index: [name, tab, leaf, what]
Audience counts never leave the repository: members carry titles, years, makers, IDs and notes only.
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
from attest import resolve, by_enwiki  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
OUT = os.path.join(ROOT, "artifact", "full", "data")
TAX = os.path.join(ROOT, "taxonomy")


def rd(path):
    return list(csv.DictReader(open(path, encoding="utf-8"))) if os.path.exists(path) else []


def strip(s):
    return re.sub(r"<[^>]+>", "", s or "")


# ---------------------------------------------------------------- attestation
def sources(tree, scaleup_attest=None):
    """code → (src list, weak note). Order: explicit enwiki title, explicit QID, label resolution; URLs added."""
    scaleup_attest = scaleup_attest or {}
    wiki = dict(getattr(tree, "ATTEST_WIKI", {}))
    qids = dict(getattr(tree, "ATTEST_QID", {}))
    urls = dict(getattr(tree, "ATTEST_URLS", {}))
    for code, a in scaleup_attest.items():
        for part in re.split(r"[;|]\s*", a or ""):
            part = part.strip()
            if part.startswith("wiki:"):
                wiki[code] = (wiki.get(code, "") + "|" if wiki.get(code) else "") + part[5:].strip()
            elif re.fullmatch(r"Q\d+", part):
                qids.setdefault(code, part)
            elif part.startswith("http"):
                urls.setdefault(code, part)
    titles = sorted({t for v in wiki.values() for t in v.split("|") if t})
    hits = by_enwiki(titles) if titles else {}
    leaves = {l[0]: l for v in tree.LEAVES.values() for l in v}
    labels = [n for code, l in leaves.items() if code not in wiki and code not in qids for n in l[6].split("|") if n]
    res = resolve(labels) if labels else {}
    bad = getattr(tree, "BAD_QID", set())
    out = {}
    for code, l in leaves.items():
        src = []
        hit = next((hits[t] for t in wiki.get(code, "").split("|") if t in hits), None)
        if not hit and code in qids:
            src.append(["https://www.wikidata.org/wiki/" + qids[code], "Wikidata " + qids[code]])
        if not hit and not src and code not in wiki:
            hit = next((res[n] for n in l[6].split("|") if res.get(n) and res[n]["qid"] not in bad), None)
        if hit:
            src.append(["https://www.wikidata.org/wiki/" + hit["qid"], f"Wikidata {hit['qid']} ({hit['label']})"])
            if hit.get("enwiki"):
                src.append(["https://en.wikipedia.org/wiki/" + hit["enwiki"].replace(" ", "_"), "Wikipedia"])
        elif code in wiki and not src:
            t = wiki[code].split("|")[0]
            src.append(["https://en.wikipedia.org/wiki/" + t.replace(" ", "_"), "Wikipedia"])
        if code in urls:
            src.append([urls[code], "source page"])
        weak = getattr(tree, "WEAK", {}).get(code, "")
        if not src:
            weak = weak or "no source found for this label yet"
        out[code] = (src, weak)
    return out


def fams_json(tree, members, src, unit):
    fams = []
    for fam in tree.FAMILIES:
        subs = []
        for s, lab, ax in fam["subs"]:
            leaves = []
            for l in tree.LEAVES.get(s, []):
                sr, weak = src.get(l[0], ([], ""))
                leaves.append({"code": l[0], "label": l[1], "breadth": l[2], "defn": l[3], "aliases": l[4], "see": l[5],
                               "src": sr, "weak": weak, "n": len(members.get(l[0], []))})
            subs.append({"code": s, "label": lab, "axis": ax, "leaves": leaves, "n": sum(x["n"] for x in leaves)})
        fams.append({"code": fam["code"], "label": fam["label"], "test": fam["test"], "key": fam["key"], "subs": subs,
                     "n": sum(x["n"] for x in subs), "nleaves": sum(len(x["leaves"]) for x in subs), "unit": unit.get(fam["code"], "items")})
    return fams


# ---------------------------------------------------------------- Film & TV
def ft_members():
    """leaf → member rows [title, year, maker/country, see_also, note, id, movement, kind]."""
    m = defaultdict(list)
    disp = Counter()
    for r in rd(os.path.join(TAX, "film", "film_placements.csv")):
        leaf = r["leaf"].split()[0] if r["leaf"] else "unplaced"
        disp["film", leaf.split(":")[0] if ":" in leaf else "leaf"] += 1
        m[leaf].append([r["title"], r["year"], r["director"] or r["countries"], r["see_also"], strip(r["note"]),
                        r["tconst"], r["movement"], "film"])
    for name in ("tv", "anime", "unscripted"):
        for r in rd(os.path.join(TAX, "series", f"{name}_placements.csv")):
            leaf = r["leaf"].split()[0] if r["leaf"] else "unplaced"
            disp[name, leaf.split(":")[0] if ":" in leaf else "leaf"] += 1
            m[leaf].append([r["title"], r["year"], r["country"], r["see_also"], strip(r["note"]), r["id"], "", name])
    for v in m.values():
        v.sort(key=lambda x: (str(x[1])[:4] or "9999", x[0]))
    return m, disp


# ---------------------------------------------------------------- Visual Art
def va_members():
    """leaf → member rows [name, group, note, source, maker(0/1)] from the pilot pool, region slices and artists."""
    import build_pilot
    m = defaultdict(list)
    alias = defaultdict(list)
    disp = Counter()
    pool = build_pilot.islamic()
    for r in pool:
        d = r["disposition"]
        typ, _, rest = d.partition(":")
        code, _, grp = rest.partition("/")
        disp["islamic pilot", typ] += 1
        if typ == "kind":
            label = build_pilot.SCHOOL.get(r["label"], r["label"]) if r["source"] in ("islamic_schools", "world_folk") else r["label"]
            m[code].append([label, build_pilot.SCHOOL.get(grp, grp), strip(r["note"]), r["source"],
                            1 if r["type"] in ("maker", "architect") else 0])
        elif typ == "alias":
            alias[code].append(r["label"])
    for r in rd(os.path.join(TAX, "visual_art", "va_placements.csv")):
        d = r["disposition"]
        typ, _, rest = d.partition(":")
        code, _, grp = rest.partition("/")
        disp[r["slice"], typ] += 1
        if typ == "kind":
            maker = 1 if r["type"] in ("maker", "architect", "artist") else 0
            m[code].append([r["label"], grp or ("Artists" if r["type"] == "artist" else ""), strip(r["note"]),
                            r["source"], maker])
        elif typ == "alias":
            alias[code].append(r["label"])
        elif typ == "leaf" and code:
            m[code].append([r["label"], "Gathered rows (the leaf's own evidence)", strip(r["note"]), r["source"], 0])
    for code, v in m.items():
        seen, out = set(), []
        for k in v:
            if k[0].lower() in seen:
                continue
            seen.add(k[0].lower())
            out.append(k)
        m[code] = out
    return m, alias, disp


# ---------------------------------------------------------------- write
def main():
    os.makedirs(OUT, exist_ok=True)
    ftm, ftd = ft_members()
    vam, vaal, vad = va_members()
    scaleup = {r["code"]: r["attest"] for r in rd(os.path.join(TAX, "visual_art", "leaves_scaleup.csv"))}
    fsrc = sources(FT)
    vsrc = sources(VA, scaleup)
    WEAKRE = re.compile(r"weak|only (a|an|the|through|by)|no (english )?(wikipedia )?article|blog|redirect|could not|not verified|unverified|rests on", re.I)
    for r in rd(os.path.join(TAX, "visual_art", "leaves_scaleup.csv")):
        if r["code"] in vsrc and WEAKRE.search(r.get("note", "")) and not vsrc[r["code"]][1]:
            vsrc[r["code"]] = (vsrc[r["code"]][0], strip(r["note"])[:220])
    ft = fams_json(FT, ftm, fsrc, {"A": "films", "B": "films", "C": "series", "D": "serials", "E": "titles", "G": "formats"})
    va = fams_json(VA, vam, vsrc, {})
    for f in va:
        for s in f["subs"]:
            for l in s["leaves"]:
                l["alias_rows"] = vaal.get(l["code"], [])
    find = []
    for tab, fams, mem in (("VA", va, vam), ("FT", ft, ftm)):
        sizes = {}
        for f in fams:
            part = {l["code"]: mem.get(l["code"], []) for s in f["subs"] for l in s["leaves"]}
            fn = f"m-{tab.lower()}-{f['code']}.json"
            json.dump(part, open(os.path.join(OUT, fn), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
            sizes[f["code"]] = os.path.getsize(os.path.join(OUT, fn))
            for s in f["subs"]:
                for l in s["leaves"]:
                    find.append([l["label"], tab, l["code"], "leaf", l["aliases"]])
                    for k in mem.get(l["code"], []):
                        what = (f"{k[1]} {k[7]}" if tab == "FT" else (k[1] or ("maker" if k[4] else "kind")))
                        find.append([k[0], tab, l["code"], what.strip(), (k[2].replace(";", " ;") if tab == "FT" and k[7] == "film" else "")])
        print(tab, "member files (KB):", {k: v // 1024 for k, v in sizes.items()})
    json.dump(find, open(os.path.join(OUT, "find.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    census = {
        "va": {"leaves": sum(f["nleaves"] for f in va), "kinds": sum(f["n"] for f in va),
               "families_built": sum(1 for f in va if f["nleaves"]),
               "dispositions": {f"{a}|{b}": v for (a, b), v in vad.items()},
               "empty_leaves": [l["code"] for f in va for s in f["subs"] for l in s["leaves"] if l["n"] == 0],
               "weak": [l["code"] for f in va for s in f["subs"] for l in s["leaves"] if l["weak"]]},
        "ft": {"leaves": sum(f["nleaves"] for f in ft), "placed": sum(f["n"] for f in ft),
               "dispositions": {f"{a}|{b}": v for (a, b), v in ftd.items()},
               "per_family": {f["code"]: f["n"] for f in ft},
               "empty_leaves": [l["code"] for f in ft for s in f["subs"] for l in s["leaves"] if l["n"] == 0],
               "weak": [l["code"] for f in ft for s in f["subs"] for l in s["leaves"] if l["weak"]]},
    }
    json.dump(census, open(os.path.join(TAX, "audit", "census.json"), "w"), indent=1)
    import report_full
    tree = {"va": {"fams": va, "familyKey": VA.FAMILY_KEY, "precedence": VA.PRECEDENCE, "modifiers": VA.MODIFIERS},
            "ft": {"fams": ft, "familyKey": FT.FAMILY_KEY, "precedence": FT.PRECEDENCE, "modifiers": FT.MODIFIERS},
            "census": census, "report": report_full.build(census)}
    json.dump(tree, open(os.path.join(OUT, "tree.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("tree.json KB", os.path.getsize(os.path.join(OUT, "tree.json")) // 1024, "find.json KB",
          os.path.getsize(os.path.join(OUT, "find.json")) // 1024)
    print(json.dumps({k: {x: (len(y) if isinstance(y, list) else y) for x, y in v.items() if x != "dispositions"} for k, v in census.items()}))


if __name__ == "__main__":
    main()
