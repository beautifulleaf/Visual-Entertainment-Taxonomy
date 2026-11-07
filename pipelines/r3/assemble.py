"""R3 assembly: build the published data (artifact/full/data) from the R3 pass outputs.

    python3 pipelines/r3/assemble.py [--src DIR] [--out DIR]

--src defaults to snapshots of the S2 release (artifact/r2/data, written on first run from
artifact/full/data), so the script is re-runnable. Film & Television is rebuilt from
taxonomy/r3/ft_out/<block>/ (leaves.json, assign.csv, additions.csv); Visual Art is the S2 data
with taxonomy/r3/va_out/<pass>/result.json applied. Passes with no output are skipped and
reported (their leaves stay as in S2 for VA; for FT a missing block is an error unless --partial).
Writes tree.json, m-*.json, find.json, and taxonomy/r3/ft_migration.csv.
"""
import argparse, collections, csv, glob, json, os, re, shutil, sys
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
R3 = os.path.join(ROOT, "taxonomy", "r3")
csv.field_size_limit(10**9)

FAMS = {
    "A": dict(label="Film", unit="films",
              test="a film made as a single work for cinema, festival, television or streaming release, in live action or as documentary: features of more than 40 minutes (A1–A20, by movement and genre) and short films of 40 minutes or less (A21). An animated film of any length is C Animation."),
    "B": dict(label="Television", unit="titles",
              test="a series, serial, programme or live broadcast made for television or subscription streaming: scripted series and miniseries (B1–B11), the long-running serial traditions (B12), unscripted formats (B13–B15) and live event and sports television (B16). Internet-native series — web series, online video channels, app micro-dramas — are not here: they belong to the future Interactive Entertainment Taxonomy."),
    "C": dict(label="Animation", unit="titles",
              test="animation in any format and from anywhere: anime, Japanese animation in any format (C1–C11, by genre; TV, film, OVA and ONA are a filter), and non-Japanese animated features (C12), series (C13) and shorts (C14)."),
}
FAMILY_KEY = [
    "1. Is it <b>animated</b>, in any format? → <b>C Animation</b>: Japanese animation (anime) by genre in C1–C11; other animation as C12 feature, C13 series or C14 short.",
    "2. Is it <b>internet-native</b> — a web series, an online video channel or show, an app micro-drama? → not classified here: it belongs to the future Interactive Entertainment Taxonomy (the finder keeps a row). A series made for subscription streaming (Netflix, Prime, iQIYI, Tencent, Indian streaming 'web series') is television.",
    "3. Is it a <b>single film</b>? → <b>A Film</b>: 40 minutes or less → A21 Short Film; otherwise by movement and genre (A1–A20).",
    "4. Otherwise it is <b>television</b> → <b>B</b>: a live event or sports broadcast → B16; an unscripted format → B13–B15; a long-running serial in a named serial tradition (telenovela, soap opera, dizi, Indian daily soap, musalsal, teleserye) → B12; a series in a named East or Southeast Asian drama tradition → B2–B6; any other scripted series or documentary series → its genre sub-family (B1, B7–B11).",
]
OLD_SUB = {"A1": "A1", "A2": "A2", "A3": "A3", "A4": "A4", "A5": "A5", "A6": "A6", "A7": "A8–A11", "A8": "A7", "A9": "A13", "A10": "A12",
           "A11": "A14", "A12": "A15", "A13": "A19", "A14": "A16", "A15": "C12", "A16": "A20", "A17": "A10", "A18": "A18", "A19": "A17",
           "B1": "C14", "B2": "A21", "B3": "A21", "B4": "A21", "C1": "B1", "C2": "B2–B6", "C3": "B7", "C4": "B8", "C5": "B9", "C6": "C13",
           "C7": "B10", "C8": "B11", "D1": "B12", "D2": "B12", "D3": "B12", "D4": "B12", "D5": "B12", "D6": "B12",
           "G1": "B13", "G2": "B14", "G3": "B15"}
OLD_SUB.update({f"E{i}": f"C{i}" for i in range(1, 12)})


def load_va_results():
    res = {}
    for d in sorted(glob.glob(os.path.join(R3, "va_out", "*"))):
        f = os.path.join(d, "result.json")
        if os.path.exists(f):
            res[os.path.basename(d)] = json.load(open(f))
    return res


def build_va(src, tree, M, find_old, report):
    results = load_va_results()
    passes = [os.path.basename(f)[:-5] for f in glob.glob(os.path.join(R3, "va_in", "*.json"))]
    report["va_passes_missing"] = sorted(set(passes) - set(results))
    leafobj = {l["code"]: (f, s, l) for f in tree["va"]["fams"] for s in f["subs"] for l in s["leaves"]}
    inrows = {}
    for p in passes:
        for l in json.load(open(os.path.join(R3, "va_in", p + ".json")))["leaves"]:
            for r in l["rows"]:
                inrows.setdefault((l["code"], r[0]), r[:5])
    replaced = collections.defaultdict(list); meta = {}
    for p, R in results.items():
        for code, v in R.get("leaves", {}).items():
            replaced[code].extend(v.get("kinds", []))
            m = meta.setdefault(code, {"alias_rows": []})
            for k in ("axis", "defn", "catalogues"):
                if v.get(k): m[k] = v[k]
            m["alias_rows"] += v.get("alias_rows", [])
    for code, rows in replaced.items():
        M[code] = rows
    # new leaves: merge by (sub, label) across passes, codes appended per sub-family
    newl = collections.OrderedDict()
    for p, R in results.items():
        for nl in R.get("new_leaves", []):
            k = (nl["sub"], nl["label"].strip().lower())
            if k in newl:
                newl[k]["kinds"].extend(nl.get("kinds", []))
            else:
                newl[k] = dict(nl, kinds=list(nl.get("kinds", [])))
    subobj = {s["code"]: s for f in tree["va"]["fams"] for s in f["subs"]}
    nextn = {}
    for sc, s in subobj.items():
        nextn[sc] = max([int(l["code"].split("-")[1]) for l in s["leaves"]] + [0]) + 1
    added = []
    for (sc, _), nl in newl.items():
        if sc not in subobj:
            report.setdefault("va_bad_sub", []).append(sc); continue
        code = f"{sc}-{nextn[sc]}"; nextn[sc] += 1
        leaf = dict(code=code, label=nl["label"], breadth=nl.get("breadth", "medium"), defn=nl["defn"], aliases=nl.get("aliases", ""),
                    see=nl.get("see", ""), src=nl.get("src", []), weak="", n=0, alias_rows=[], new="R3")
        if nl.get("axis"): leaf["axis"] = nl["axis"]
        if nl.get("catalogues"): leaf["catalogues"] = nl["catalogues"]
        subobj[sc]["leaves"].append(leaf); M[code] = nl["kinds"]; added.append(code)
        leafobj[code] = (None, subobj[sc], leaf)
    report["va_new_leaves"] = added
    moved = 0
    for p, R in results.items():
        for name, frm, to in R.get("moves_out", []):
            r = inrows.get((frm, name))
            if not r or to not in leafobj:
                report.setdefault("va_bad_moves", []).append([name, frm, to]); continue
            r = list(r); r[1] = r[1] if r[1] in ("Artists", "Architects", "Makers", "Designers") else ("Artists" if r[4] else r[1])
            M.setdefault(to, []).append(r); moved += 1
    report["va_moved"] = moved
    # leaf metadata, sections, counts
    orig_n = {code: l["n"] for code, (f, s, l) in leafobj.items()}
    moved_from = {frm for R in results.values() for _, frm, _ in R.get("moves_out", [])}
    for code, (f, s, l) in leafobj.items():
        m = meta.get(code, {})
        for k in ("axis", "defn", "catalogues"):
            if m.get(k): l[k] = m[k]
        if m.get("alias_rows"):
            l["alias_rows"] = list(dict.fromkeys((l.get("alias_rows") or []) + m["alias_rows"]))
        rows = M.get(code, [])
        order = list(dict.fromkeys(r[1] for r in rows))
        if code in replaced or code in added: l["secs"] = order
        l["n"] = len(rows)
    # owner, 2026-11-07: "Remove retired leaves". A leaf emptied by R3 (its kinds moved to other leaves
    # or to N Design) is dropped from the page, not marked retired; the record is va_migration.csv.
    gone = []
    for f in tree["va"]["fams"]:
        for s in f["subs"]:
            keep = []
            for l in s["leaves"]:
                emptied = l["code"] in replaced and l["n"] == 0 and orig_n.get(l["code"], 0) > 0 and l["code"] in moved_from
                if emptied or "retired" in l["label"].lower():
                    gone.append([l["code"], l["label"]])
                else:
                    keep.append(l)
            s["leaves"] = keep
    report["va_leaves_removed"] = gone
    with open(os.path.join(R3, "va_migration.csv"), "w", newline="") as fo:
        w = csv.writer(fo); w.writerow(["code", "label", "status"])
        for c, lab in gone: w.writerow([c, lab, "removed in R3 (emptied: kinds moved)"])
        for c in added: w.writerow([c, leafobj[c][2]["label"], "new in R3"])
    for f in tree["va"]["fams"]:
        for s in f["subs"]:
            s["n"] = sum(l["n"] for l in s["leaves"])
        f["n"] = sum(s["n"] for s in f["subs"]); f["nleaves"] = sum(len(s["leaves"]) for s in f["subs"])
    c = tree["census"]["va"]
    c["leaves"] = sum(f["nleaves"] for f in tree["va"]["fams"]); c["kinds"] = sum(f["n"] for f in tree["va"]["fams"])
    c["families_built"] = sum(1 for f in tree["va"]["fams"] if f["nleaves"])
    c["empty_leaves"] = [l["code"] for f in tree["va"]["fams"] for s in f["subs"] for l in s["leaves"] if not l["n"]]
    # finder: leaves, aliases and kinds rebuilt from the data; keep other seam rows that still resolve
    find = []
    for f in tree["va"]["fams"]:
        for s in f["subs"]:
            for l in s["leaves"]:
                find.append([l["label"], "VA", l["code"], "leaf", "; ".join(x for x in [l.get("aliases", "")] + (l.get("alias_rows") or []) if x)])
                for r in M.get(l["code"], []):
                    find.append([r[0], "VA", l["code"], "maker" if r[4] else (r[1] or "kind"), ""])
    have = {(e[0], e[2]) for e in find}
    codes = set(leafobj)
    for e in find_old:
        if e[1] == "VA" and e[3].startswith("→") and e[2] in codes and (e[0], e[2]) not in have:
            find.append(e)
    return find


def remap_text(s, leafmap):
    def sub(m):
        c = m.group(0)
        if "-" in c:
            return leafmap.get(c, c)
        if c[0] == "D":  # bare D1–D8 are the owner's rulings, not old family-D sub-families
            return c
        return OLD_SUB.get(c, c)
    return re.sub(r"\b[ABCDEG]\d{1,2}(?:-\d{1,3})?\b", sub, s)


def build_ft(src, tree, partial, report):
    blocks = json.load(open(os.path.join(R3, "ft_blocks.json")))
    ins = {}; outs = {}
    for b in blocks:
        ins[b] = {r["id"]: r for r in csv.DictReader(open(os.path.join(R3, "ft_in", b + ".csv")))}
        d = os.path.join(R3, "ft_out", b)
        if os.path.exists(os.path.join(d, "leaves.json")) and os.path.exists(os.path.join(d, "assign.csv")):
            outs[b] = dict(L=json.load(open(os.path.join(d, "leaves.json"))),
                           A=list(csv.DictReader(open(os.path.join(d, "assign.csv")))),
                           AD=list(csv.DictReader(open(os.path.join(d, "additions.csv")))) if os.path.exists(os.path.join(d, "additions.csv")) else [])
    missing = sorted(set(blocks) - set(outs))
    report["ft_blocks_missing"] = missing
    if missing and not partial:
        sys.exit(f"FT blocks without output: {missing} (use --partial to build anyway)")
    subs = {}
    for b, o in outs.items():
        for s in o["L"]["subs"]:
            subs[s["code"]] = s
    OV = {r["id"]: r for r in csv.DictReader(open(os.path.join(R3, "overrides.csv")))}
    b16_ids = {a["id"] for o in outs.values() for a in o["AD"] if a["id"]}
    web_extra = []
    rows = collections.defaultdict(list); old2new = collections.defaultdict(collections.Counter); routed = []
    for b, o in outs.items():
        for a in o["A"]:
            r = ins[b].get(a["id"])
            if r is None: continue
            ov = OV.get(a["id"])
            if ov:
                if ov["action"] == "web":
                    web_extra.append(dict(id=r["id"], title=r["title"], year=r["year"], who=r["who"], old_leaf=r["old_leaf"], reason=ov["reason"])); continue
                if ov["action"] == "to_b16" and a["id"] in b16_ids: continue
                a = dict(a, route=ov["target"] or "B16")
            if a.get("route", "").strip():
                routed.append((a, r)); continue
            rows[a["leaf"]].append([r["title"], r["year"], r["who"], a.get("see_also", "").strip(), (a.get("note") or "").strip(),
                                    r["id"], r["movement_tag"], r["kind"], a.get("sec", "").strip()])
            old2new[r["old_leaf"]][a["leaf"]] += 1
        for i, a in enumerate(o["AD"], 1):
            idv = a["id"].strip() or f"r3:{a['leaf']}-{i}"
            rows[a["leaf"]].append([a["title"], a["year"], a.get("who", ""), a.get("see_also", "").strip(), a.get("note", "").strip(),
                                    idv, "", "tv", a.get("sec", "").strip()])
    # routed titles: the leaf of the target sub-family that took most titles of the same old leaf, else its largest leaf
    for a, r in routed:
        tgt = a["route"].strip().split("-")[0]
        if tgt not in subs:
            report.setdefault("ft_bad_routes", []).append([r["id"], a["route"]]); continue
        cand = [(n, lf) for lf, n in old2new[r["old_leaf"]].items() if lf.split("-")[0] == tgt]
        if not cand:
            cand = [(len(rows[l["code"]]), l["code"]) for l in subs[tgt]["leaves"]]
        lf = max(cand)[1]
        rows[lf].append([r["title"], r["year"], r["who"], "", (a.get("note") or "routed").strip(), r["id"], r["movement_tag"], r["kind"], ""])
        old2new[r["old_leaf"]][lf] += 1
    report["ft_routed"] = len(routed); report["ft_web_override"] = len(web_extra)
    if web_extra:
        with open(os.path.join(R3, "web_series_removed.csv"), "a", newline="") as fo:
            w = csv.DictWriter(fo, fieldnames=["id", "title", "year", "who", "old_leaf", "reason"])
            known = {x["id"] for x in csv.DictReader(open(os.path.join(R3, "web_series_removed.csv")))}
            w.writerows([x for x in web_extra if x["id"] not in known])
    # leaves left empty by the overrides (e.g. Web Animation, Television Special) are dropped
    for sc, s in subs.items():
        s["leaves"] = [l for l in s["leaves"] if rows.get(l["code"]) or not any(OV.get(a["id"]) for o in outs.values() for a in o["A"] if a.get("leaf") == l["code"])]
    leafmap = {o: c.most_common(1)[0][0] for o, c in old2new.items()}
    # see-also from S2 (old codes) on unrouted rows is replaced by the block's own; leave as given
    fams = []
    for fc in "ABC":
        F = dict(code=fc, label=FAMS[fc]["label"], test=FAMS[fc]["test"], unit=FAMS[fc]["unit"], key=[], subs=[])
        for sc in sorted((c for c in subs if c[0] == fc), key=lambda c: int(c[1:])):
            s = subs[sc]
            leaves = []
            for l in s["leaves"]:
                rs = rows.get(l["code"], [])
                if l.get("secs"):  # keep section order, then year
                    rs.sort(key=lambda k: (int(k[8]) if k[8].isdigit() else 99, str(k[1])))
                else:
                    rs.sort(key=lambda k: str(k[1]))
                rows[l["code"]] = rs
                L = dict(code=l["code"], label=l["label"], breadth=l["breadth"], defn=l["defn"], aliases=l.get("aliases", ""),
                         see=l.get("see", ""), src=[list(x) for x in l.get("src", [])], weak=l.get("weak", ""), n=len(rs))
                if l.get("secs"): L["secs"] = l["secs"]; L["axis"] = l.get("axis", "")
                leaves.append(L)
            F["subs"].append(dict(code=sc, label=s["label"], axis=s["axis"], leaves=leaves, n=sum(x["n"] for x in leaves)))
            F["key"].append(f"<b>{sc} {s['label']}</b> — {s['axis'].replace('Axis:', '').strip()}")
        F["n"] = sum(s["n"] for s in F["subs"]); F["nleaves"] = sum(len(s["leaves"]) for s in F["subs"])
        fams.append(F)
    ft = tree["ft"]
    prec = []
    for p in ft["precedence"]:
        txt = remap_text(p[2], leafmap)
        txt = re.sub(r"[^.]*\bweb (series|show)[^.]*\.\s*", "", txt).strip()
        if txt: prec.append([p[0], p[1], txt])
    mods = [remap_text(m, leafmap).replace(", web series", "") for m in ft["modifiers"]]
    tree["ft"] = dict(fams=fams, familyKey=FAMILY_KEY, precedence=prec, modifiers=mods)
    placed = sum(f["n"] for f in fams)
    tree["census"]["ft"] = dict(leaves=sum(f["nleaves"] for f in fams), placed=placed,
                                per_family={f["code"]: f["n"] for f in fams},
                                empty_leaves=[l["code"] for f in fams for s in f["subs"] for l in s["leaves"] if not l["n"]],
                                weak=[l["code"] for f in fams for s in f["subs"] for l in s["leaves"] if l.get("weak")],
                                dispositions=tree["census"]["ft"].get("dispositions", {}))
    # migration table
    old_label = {l["code"]: l["label"] for f in json.load(open(os.path.join(src, "tree.json")))["ft"]["fams"] for s in f["subs"] for l in s["leaves"]}
    newlab = {l["code"]: l["label"] for f in fams for s in f["subs"] for l in s["leaves"]}
    with open(os.path.join(R3, "ft_migration.csv"), "w", newline="") as fo:
        w = csv.writer(fo); w.writerow(["old_code", "old_label", "new_code", "new_label", "titles"])
        for o in sorted(old_label, key=lambda c: (c[0], int(c.split("-")[0][1:]), int(c.split("-")[1]))):
            if o not in old2new:
                w.writerow([o, old_label[o], "", "retired" if "retired" in old_label[o] or o in ("G3-6", "C1-17") else "no titles", 0]); continue
            for nc, n in old2new[o].most_common():
                w.writerow([o, old_label[o], nc, newlab.get(nc, ""), n])
    M = collections.defaultdict(dict)
    for lf, rs in rows.items():
        M[lf.split("-")[0][0]][lf] = rs
    find = []
    for f in fams:
        for s in f["subs"]:
            for l in s["leaves"]:
                find.append([l["label"], "FT", l["code"], "leaf", l.get("aliases", "")])
                for k in rows.get(l["code"], []):
                    find.append([k[0], "FT", l["code"], f"{str(k[1])[:4]} {k[7]}", k[2]])
    old_find = json.load(open(os.path.join(src, "find.json")))
    for e in old_find:
        if e[1] == "FT" and e[3].startswith("→"):
            find.append([e[0], "FT", "", e[3], e[4]])
    for r in csv.DictReader(open(os.path.join(R3, "web_series_removed.csv"))):
        find.append([r["title"], "FT", "", "→ Interactive Entertainment Taxonomy (web series, R3)", r["who"]])
    for lab in ("web series", "web show", "YouTube channel", "vertical short drama", "app micro-drama"):
        find.append([lab, "FT", "", "→ Interactive Entertainment Taxonomy (R3)", ""])
    return M, find


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--src"); ap.add_argument("--out"); ap.add_argument("--partial", action="store_true")
    a = ap.parse_args()
    snap = os.path.join(ROOT, "artifact", "r2", "data")
    if not os.path.exists(snap):
        shutil.copytree(os.path.join(ROOT, "artifact", "full", "data"), snap)
    src = a.src or snap; out = a.out or os.path.join(ROOT, "artifact", "full", "data")
    tree = json.load(open(os.path.join(src, "tree.json")))
    find_old = json.load(open(os.path.join(src, "find.json")))
    MV = {}
    for fn in glob.glob(os.path.join(src, "m-va-*.json")):
        MV.update(json.load(open(fn)))
    report = {}
    find_va = build_va(src, tree, MV, find_old, report)
    MF, find_ft = build_ft(src, tree, a.partial, report)
    os.makedirs(out, exist_ok=True)
    for fn in glob.glob(os.path.join(out, "m-*.json")): os.remove(fn)
    byfam = collections.defaultdict(dict)
    for code, rows in MV.items(): byfam[code[0]][code] = rows
    for f in tree["va"]["fams"]:
        json.dump(byfam.get(f["code"], {}), open(os.path.join(out, f"m-va-{f['code']}.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    for f in tree["ft"]["fams"]:
        json.dump(MF.get(f["code"], {}), open(os.path.join(out, f"m-ft-{f['code']}.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    json.dump(find_va + find_ft, open(os.path.join(out, "find.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    json.dump(tree, open(os.path.join(out, "tree.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    json.dump(report, open(os.path.join(R3, "assemble_report.json"), "w"), indent=1)
    print(json.dumps({k: (v if not isinstance(v, list) or len(v) < 12 else f"{len(v)} items") for k, v in report.items()}, indent=1))
    print("VA", tree["census"]["va"]["leaves"], "leaves", tree["census"]["va"]["kinds"], "kinds; FT", tree["census"]["ft"]["leaves"], "leaves", tree["census"]["ft"]["placed"], "titles")

if __name__ == "__main__":
    main()
