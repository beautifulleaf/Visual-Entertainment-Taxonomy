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


WORK_RX = re.compile(r"wikidata\.org/wiki/Q|metmuseum\.org/art/collection/search/\d|collections\.vam\.ac\.uk/item|colbase\.nich|clevelandart\.org/art/\d|artic\.edu/artworks|hdl\.handle\.net|n2t\.net|penn\.museum/collections/object|tepapa\.govt\.nz/object|artsmia\.org/art/|britishmuseum\.org/collection/object|goskatalog|digitalarchive\.npm|emuseum\.go\.kr|himalayanart\.org/items|rijksmuseum\.nl/[a-z]+/collect|asia\.si\.edu/object|collections\.si\.edu/search/detail|kunishitei\.bunka")
KEEP_SITE_RX = re.compile(r"UNESCO|World Heritage|National Treasure|designated|Grade I|listed|Monument historique|heritage", re.I)


def apply_collections(M, leafobj, replaced, report):
    """Owner, 2026-11-07: for traditions not centred on named artists, where the works can be seen is the primary
    organisation. Per-object works rows are removed (architecture and art in place keep only UNESCO and nationally
    designated sites) and the pass-made Collections rows are replaced by Holding institutions computed from the
    leaf × institution table (taxonomy/r3/collections/leaf_institutions.json), each with its search link."""
    fp = os.path.join(R3, "collections", "leaf_institutions.json")
    if not os.path.exists(fp): return
    LI = json.load(open(fp)); st = collections.Counter()
    for code, rows in list(M.items()):
        if code not in leafobj: continue
        makers = sum(1 for r in rows if r[4])
        tradition_led = makers < 0.5 * max(1, len(rows)) or code in LI
        if not tradition_led: continue
        keep = []
        insitu = code[0] in "KL"
        for r in rows:
            src = str(r[3])
            if r[1] == "Collections": st["old_collections_rows"] += 1; continue
            if not r[4] and WORK_RX.search(src):
                if insitu and KEEP_SITE_RX.search(str(r[2])): keep.append(r); st["sites_kept"] += 1; continue
                st["work_rows_removed"] += 1; continue
            keep.append(r)
        inst = [[i, "Holding institutions", f"{n:,} objects of this tradition in the gathered records", ("link " + u) if u else "", 0]
                for i, n, u in LI.get(code, [])]
        # holding institutions sit after sub-types, schools and centres, before makers
        pos = next((k for k, r in enumerate(keep) if r[4]), len(keep))
        M[code] = keep[:pos] + inst + keep[pos:]; replaced[code] = M[code]
        st["leaves"] += 1; st["institution_rows"] += len(inst)
    report["collections"] = dict(st)


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
    junk = 0
    for code, rows in replaced.items():
        keep = [r for r in rows if str(r[0]).strip() and r[1] != "Unverified list entries"]
        junk += len(rows) - len(keep)
        M[code] = keep
    report["va_junk_rows_dropped"] = junk
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
            if not str(name).strip(): continue  # nameless input rows are junk
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
    fx = json.load(open(os.path.join(R3, "fixes.json")))
    for old, new in fx.get("va_rename", {}).items():
        for rs in M.values():
            for r in rs:
                if r[0] == old: r[0] = new
    for m in fx.get("va_merge", []):
        if m["from"] in M and m["to"] in leafobj:
            M.setdefault(m["to"], []).extend(M.pop(m["from"])); replaced[m["to"]] = M[m["to"]]
            f0, s0, l0 = leafobj[m["from"]]; s0["leaves"].remove(l0); del leafobj[m["from"]]
            report.setdefault("va_fix_merged", []).append([m["from"], m["to"]])
    for nl in fx.get("va_new_leaves", []):
        sub = subobj[nl["sub"]]; code = f"{nl['sub']}-{max(int(l['code'].split('-')[1]) for l in sub['leaves']) + 1}"
        kinds = []
        for frm, prefix in nl.get("take_groups", []):
            keep = []
            for r in M.get(frm, []):
                if r[1].startswith(prefix):
                    r = list(r); r[1] = r[1].replace(prefix, "").strip().capitalize() or "Designers"; r[1] = r[1][0].upper() + r[1][1:]; kinds.append(r)
                else:
                    keep.append(r)
            M[frm] = keep
        order = ["France", "Italy", "United kingdom", "United states", "Japan", "Other countries"]
        kinds.sort(key=lambda r: order.index(r[1]) if r[1] in order else 99)
        for r in kinds: r[1] = {"United kingdom": "United Kingdom", "United states": "United States", "Other countries": "Other countries"}.get(r[1], r[1])
        leaf = dict(code=code, label=nl["label"], breadth=nl["breadth"], defn=nl["defn"], aliases=nl["aliases"], see=nl["see"],
                    src=nl["src"], weak="", n=0, alias_rows=[], new="R3", axis=nl["axis"], catalogues=nl["catalogues"])
        sub["leaves"].append(leaf); M[code] = kinds; leafobj[code] = (None, sub, leaf); replaced[code] = kinds; added.append(code)
        report.setdefault("va_fix_new_leaves", []).append([code, nl["label"], len(kinds)])
    apply_collections(M, leafobj, replaced, report)
    # one home per maker: primary = the leaf where the row came from the gathered data (not an "r3" addition),
    # else the first named-school leaf seen; other leaves keep a cross-reference row (not a maker)
    seen_in = collections.defaultdict(list)
    for code in list(M):
        uniq, keys = [], set()
        for r in M[code]:
            key = (r[0], r[1], r[4])
            if r[4] and (r[0], r[4]) in keys: continue
            keys.add((r[0], r[4])); uniq.append(r)
            if r[4]: seen_in[r[0]].append(code)
        M[code] = uniq
    xref = 0
    label_of = {c: o[2]["label"] for c, o in leafobj.items()}
    for name, codes in seen_in.items():
        if len(codes) < 2: continue
        def rank(c):
            r = next(x for x in M[c] if x[0] == name and x[4])
            return (str(r[3]).startswith("r3"), c in ("A5-110", "A5-111", "A5-38", "D5-118", "D5-119"), codes.index(c))
        prim = min(codes, key=rank)
        for c in codes:
            if c == prim: continue
            for r in M[c]:
                if r[0] == name and r[4]:
                    r[2] = (f"→ primary home {prim} {label_of.get(prim, '')}" + (f" · {r[2]}" if r[2] else ""))[:200]
                    r[4] = 0; xref += 1
    report["va_maker_xrefs"] = xref
    # owner, 2026-11-07: "Remove retired leaves". A leaf emptied by R3 (its kinds moved to other leaves
    # or to N Design) is dropped from the page, not marked retired; the record is va_migration.csv.
    gone = []
    for f in tree["va"]["fams"]:
        for s in f["subs"]:
            for l in s["leaves"]:  # final recount after fixes and the one-home rule
                rows_ = M.get(l["code"], []); l["n"] = len(rows_)
                if l["code"] in replaced or l["code"] in added:
                    order = list(dict.fromkeys(r[1] for r in rows_))
                    if l.get("secs"): order = [g for g in l["secs"] if g in order] + [g for g in order if g not in l["secs"]]
                    l["secs"] = order
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
    if not any(p[0] == "S3" for p in tree["va"]["precedence"]):
        tree["va"]["precedence"].append(["S3", "Erotic art or pornography", "Explicitness alone never decides. A work made for the art or mainstream circuit (studios, patrons, galleries, museums, the regular print and publishing trades) is placed here by its tradition even when explicit (shunga under Ukiyo-e, Khajuraho sculpture, Courbet, Koons's Made in Heaven, Mapplethorpe). An explicit work made for the adult trade (adult magazines and photo trades, adult imprints, adult doujinshi, Tijuana bibles) belongs to the Pleasure Taxonomies, with a finder row here; the circuit of first publication decides, not later museum acquisition (docs/ruling-s3-erotic-line.md)."])
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


def apply_resize(subs, rows, report):
    """Leaves over the 200-title ceiling after the Starting List: split into attested sub-leaves and/or re-sectioned
    (taxonomy/r3/resize/out_<batch>.json)."""
    leafobj = {l["code"]: (s, l) for s in subs.values() for l in s["leaves"]}
    st = collections.Counter()
    for f in sorted(glob.glob(os.path.join(R3, "resize", "out_*.json"))):
        for code, o in json.load(open(f)).items():
            if code not in leafobj: st["missing_leaf"] += 1; continue
            sub, L = leafobj[code]
            if o.get("label"): L["label"] = o["label"]
            if o.get("defn"): L["defn"] = o["defn"]
            L["secs"] = list(o.get("secs") or []); L["axis"] = o.get("axis", "")
            key2 = {"self": code}; pos = sub["leaves"].index(L) + 1
            for nl in o.get("new_leaves", []):
                n = max(int(l["code"].split("-")[1]) for l in sub["leaves"]) + 1
                nc = f"{sub['code']}-{n}"
                NL = dict(code=nc, label=nl["label"], breadth=nl.get("breadth", "medium"), defn=nl["defn"], aliases=nl.get("aliases", ""),
                          see=f"{code} {L['label']}", src=nl.get("src", []), weak="", secs=list(nl.get("secs") or []), axis=nl.get("axis", ""))
                sub["leaves"].insert(pos, NL); pos += 1; key2[nl["key"]] = nc; leafobj[nc] = (sub, NL); st["new_leaves"] += 1
            byid = {k[5]: k for k in rows.get(code, [])}
            keep = []
            for idv, k in byid.items():
                a = o.get("assign", {}).get(idv)
                if not a: keep.append(k); continue
                tgt = key2.get(a[0], code); k[8] = str(a[1]) if a[1] else ""
                if tgt == code: keep.append(k)
                else: rows[tgt].append(k); st["moved_to_new"] += 1
            rows[code] = keep; st["leaves"] += 1
    report["resize"] = dict(st)


def apply_startlist(subs, rows, report):
    """TSPDT Starting List films (owner: every one gets a home): rule placements (decided.csv) and pass
    placements (out_<batch>.csv, new_leaves_<batch>.json); 'out' rows become finder notes."""
    O = os.path.join(R3, "startlist")
    if not os.path.exists(os.path.join(O, "decided.csv")): return
    leafobj = {l["code"]: l for s in subs.values() for l in s["leaves"]}
    placed = {k[5] for rs in rows.values() for k in rs}
    info = collections.defaultdict(list)  # per batch: id -> input rows (a few id-less films share an id)
    for f in glob.glob(os.path.join(O, "in_*.csv")):
        for r in csv.DictReader(open(f)): info[(os.path.basename(f)[3:-4], r["id"])].append(r)
    st = collections.Counter(); outs = []
    restore = json.load(open(os.path.join(R3, "fixes.json"))).get("startlist_restore", {})
    def add(r, leaf, sec, note):
        key = r["id"] if r["id"].startswith("tt") else (r["id"], r["title"], r["who"])
        if key in placed or (r["id"].startswith("tt") and r["id"] in placed): st["dup"] += 1; return
        L = leafobj[leaf]; sec = (sec or "").strip()
        if sec.startswith("new:"):
            lab = sec[4:].strip(); L.setdefault("secs", [])
            if lab not in L["secs"]: L["secs"].append(lab)
            sec = str(L["secs"].index(lab) + 1)
        kind = "tv" if leaf[0] == "B" else "film"
        country = (r.get("country") or "")
        rows[leaf].append([r["title"], r["year"], r["who"], "", (note or "").strip(), r["id"],
                           "", kind, sec if (L.get("secs") and sec) else "", country])
        placed.add(key); st["placed"] += 1
    for r in csv.DictReader(open(os.path.join(O, "decided.csv"))):
        if r["leaf"] in leafobj: add(r, r["leaf"], "", "")
    for f in sorted(glob.glob(os.path.join(O, "out_*.csv"))):
        b = os.path.basename(f)[4:-4]; key2code = {}
        nf = os.path.join(O, f"new_leaves_{b}.json")
        for nl in (json.load(open(nf)) if os.path.exists(nf) else []):
            sub = subs.get(nl["sub"])
            if not sub: continue
            code = f"{nl['sub']}-{max(int(l['code'].split('-')[1]) for l in sub['leaves']) + 1}"
            L = dict(code=code, label=nl["label"], breadth=nl.get("breadth", "narrow"), defn=nl["defn"], aliases=nl.get("aliases", ""),
                     see=nl.get("see", ""), src=nl.get("src", []), weak="", secs=list(nl.get("secs") or []), axis=nl.get("axis", ""))
            sub["leaves"].append(L); leafobj[code] = L; key2code[nl["key"]] = code; st["new_leaf"] += 1
        for a in csv.DictReader(open(f)):
            lf = key2code.get(a["leaf"].strip(), a["leaf"].strip())
            for r in info.get((b, a["id"]), []):
                if lf == "out" and r["id"] in restore:
                    lf2, sec2 = restore[r["id"]]; add(r, lf2, sec2, "restored: TSPDT-listed, in scope (S3 / streaming)"); st["restored"] += 1; continue
                if lf == "out": outs.append([r["title"], a.get("note", "")]); st["out"] += 1; continue
                if lf in leafobj: add(r, lf, a.get("sec", ""), a.get("note", ""))
                else: st["bad_leaf"] += 1
    report["startlist"] = dict(st); report["startlist_out"] = outs[:200]


DROP_COVERAGE_LEAVES = {"news & current affairs"}  # news is not entertainment (B16 decision)


def apply_coverage(subs, rows, cc, report):
    """Apply taxonomy/r3/coverage_out/<part>/: new leaves, new sections, re-sectioning, moves, adds."""
    leafobj = {l["code"]: l for s in subs.values() for l in s["leaves"]}
    where = {}
    for lf, rs in rows.items():
        for k in rs: where[k[5]] = lf
    stats = collections.Counter(); pending_resections = []; origin = {}
    for d in sorted(glob.glob(os.path.join(R3, "coverage_out", "*"))):
        part = os.path.basename(d); key2code = {}
        f = os.path.join(d, "new_leaves.json")
        for nl in (json.load(open(f)) if os.path.exists(f) else []):
            if any(nl["label"].strip().lower().startswith(x) for x in DROP_COVERAGE_LEAVES):
                key2code[nl["key"]] = None; stats["dropped_leaf"] += 1; continue
            s = subs.get(nl["sub"])
            if not s: report.setdefault("cov_bad_sub", []).append([part, nl["sub"]]); continue
            n = max(int(l["code"].split("-")[1]) for l in s["leaves"]) + 1 if s["leaves"] else 1
            code = f"{nl['sub']}-{n}"
            L = dict(code=code, label=nl["label"], breadth=nl.get("breadth", "medium"), defn=nl["defn"], aliases=nl.get("aliases", ""),
                     see=nl.get("see", ""), src=nl.get("src", []), weak="", secs=list(nl.get("secs") or []), axis=nl.get("axis", ""))
            s["leaves"].append(L); leafobj[code] = L; key2code[nl["key"]] = code; stats["new_leaf"] += 1
        def tgt(t): return key2code.get(t, t) if t in key2code else t
        def secidx(code, sec):
            L = leafobj[code]; sec = (sec or "").strip()
            if not sec: return ""
            if sec.isdigit(): return sec
            L.setdefault("secs", [])
            if sec not in L["secs"]: L["secs"].append(sec)
            return str(L["secs"].index(sec) + 1)
        f = os.path.join(d, "new_sections.csv")
        for r in (csv.DictReader(open(f)) if os.path.exists(f) else []):
            if r["leaf"] in leafobj: secidx(r["leaf"], r["label"]); stats["new_section"] += 1
        f = os.path.join(d, "resections.json")
        if os.path.exists(f): pending_resections.append((part, json.load(open(f))))
        f = os.path.join(d, "moves.csv")
        for r in (csv.DictReader(open(f)) if os.path.exists(f) else []):
            to = tgt(r["to"]); frm = where.get(r["id"])
            if not to or to not in leafobj or not frm: stats["move_skipped"] += 1; continue
            k = next(x for x in rows[frm] if x[5] == r["id"]); rows[frm].remove(k)
            k[8] = secidx(to, r.get("sec")); k[4] = (r.get("note") or k[4]).strip()
            rows[to].append(k); where[r["id"]] = to; origin[r["id"]] = part; stats["moved"] += 1
        f = os.path.join(d, "adds.csv")
        for i, r in enumerate(csv.DictReader(open(f)) if os.path.exists(f) else [], 1):
            to = tgt(r["to"])
            if not to or to not in leafobj: stats["add_skipped"] += 1; continue
            idv = r["id"].strip() or f"r3:{part}-{i}"
            if idv in where: stats["add_dup"] += 1; continue
            rows[to].append([r["title"], r["year"], r.get("who", ""), "", r.get("note", "").strip(), idv, "", r.get("kind", "film"),
                             secidx(to, r.get("sec")), cc(idv, r.get("who", ""), r.get("kind", "film"))])
            where[idv] = to; origin[idv] = part; stats["added"] += 1
    # re-sectioning last, after every part's moves and adds; titles a scheme does not list go to "Unsectioned"
    for rpart, R in pending_resections:
        for code, v in R.items():
            if code not in leafobj: continue
            old = list(leafobj[code].get("secs") or [])
            leafobj[code]["secs"] = list(v["secs"]); leafobj[code]["axis"] = v.get("axis", leafobj[code].get("axis", ""))
            for k in rows.get(code, []):
                if k[5] in v["assign"]:
                    k[8] = str(v["assign"][k[5]]); continue
                if origin.get(k[5]) == rpart and k[8].isdigit() and 0 < int(k[8]) <= len(v["secs"]):
                    stats["resection_own_rows"] += 1; continue  # numbered against this pass's own new scheme
                # not listed by the scheme (added later): keep its section by label, else a named last section
                lab = old[int(k[8]) - 1] if k[8].isdigit() and 0 < int(k[8]) <= len(old) else ""
                if lab and lab in leafobj[code]["secs"]:
                    k[8] = str(leafobj[code]["secs"].index(lab) + 1); stats["resection_kept_by_label"] += 1
                else:
                    if lab and lab not in leafobj[code]["secs"]:
                        leafobj[code]["secs"].append(lab); k[8] = str(len(leafobj[code]["secs"]))
                    else:
                        tail = "Added in the coverage pass"
                        if tail not in leafobj[code]["secs"]: leafobj[code]["secs"].append(tail)
                        k[8] = str(leafobj[code]["secs"].index(tail) + 1)
                    stats["resection_unlisted"] += 1
            stats["resectioned"] += 1
    report["coverage"] = dict(stats)


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
    # country of origin for the page filters (owner: era, country, director as fundamentals)
    I = os.path.join(ROOT, "data", "interim"); CC = {}
    for r in csv.DictReader(open(os.path.join(I, "film_selected.csv"))): CC[r["key"]] = r["countries"].replace(";", "|").replace(",", "|")
    for r in csv.DictReader(open(os.path.join(I, "tv_selected.csv"))): CC.setdefault(r["tconst"], r["country"])
    for r in csv.DictReader(open(os.path.join(I, "anime_selected.csv"))): CC.setdefault(r["mal_id"], r["country"])
    for r in csv.DictReader(open(os.path.join(I, "asian_drama_selected.csv"))): CC.setdefault("mdl:" + r["mdl_id"], r["country"])
    def cc(idv, who, kind):
        if idv in CC and CC[idv]: return CC[idv]
        w = (who or "").strip()
        return w if kind != "film" and re.fullmatch(r"[A-Z]{2}(\|[A-Z]{2})*", w) else ""
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
                                    r["id"], r["movement_tag"], r["kind"], a.get("sec", "").strip(), cc(r["id"], r["who"], r["kind"])])
            old2new[r["old_leaf"]][a["leaf"]] += 1
        for i, a in enumerate(o["AD"], 1):
            idv = a["id"].strip() or f"r3:{a['leaf']}-{i}"
            rows[a["leaf"]].append([a["title"], a["year"], a.get("who", ""), a.get("see_also", "").strip(), a.get("note", "").strip(),
                                    idv, "", "tv", a.get("sec", "").strip(), cc(idv, a.get("who", ""), "tv")])
    # routed titles: the leaf of the target sub-family that took most titles of the same old leaf, else its largest leaf
    for a, r in routed:
        tgt = a["route"].strip().split("-")[0]
        if tgt not in subs:
            report.setdefault("ft_bad_routes", []).append([r["id"], a["route"]]); continue
        cand = [(n, lf) for lf, n in old2new[r["old_leaf"]].items() if lf.split("-")[0] == tgt]
        if not cand:
            cand = [(len(rows[l["code"]]), l["code"]) for l in subs[tgt]["leaves"]]
        lf = max(cand)[1]
        rows[lf].append([r["title"], r["year"], r["who"], "", (a.get("note") or "routed").strip(), r["id"], r["movement_tag"], r["kind"], "", cc(r["id"], r["who"], r["kind"])])
        old2new[r["old_leaf"]][lf] += 1
    report["ft_routed"] = len(routed); report["ft_web_override"] = len(web_extra)
    apply_coverage(subs, rows, cc, report)
    apply_startlist(subs, rows, report)
    apply_resize(subs, rows, report)
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
    fx = json.load(open(os.path.join(R3, "fixes.json")))
    L = {l["code"]: (F, sub, l) for F in fams for sub in F["subs"] for l in sub["leaves"]}
    merged = {}
    for m in fx.get("ft_merge", []):
        if m["from"] not in L or m["to"] not in L: report.setdefault("fix_skipped", []).append(m); continue
        _, fsub, fl = L[m["from"]]; _, tsub, tl = L[m["to"]]
        moved = rows.pop(m["from"], [])
        if tl.get("secs"):
            if m["section"] not in tl["secs"]: tl["secs"].append(m["section"])
            for k in moved: k[8] = str(tl["secs"].index(m["section"]) + 1)
        else:
            for k in moved: k[8] = ""
        rows[m["to"]].extend(moved); tl["n"] = len(rows[m["to"]])
        fsub["leaves"].remove(fl); merged[m["from"]] = m["to"]; leafmap[m["from"]] = m["to"]
    for code, lab in fx.get("ft_relabel", {}).items():
        if code in L: L[code][2]["label"] = lab
    where = {k[5]: lf for lf, rs in rows.items() for k in rs}
    for idv, to in fx.get("ft_move", []):
        frm = where.get(idv)
        if frm and to in L and frm != to:
            k = next(x for x in rows[frm] if x[5] == idv); rows[frm].remove(k); k[8] = ""; rows[to].append(k)
    for F in fams:
        for sub in F["subs"]:
            for l in sub["leaves"]:
                l["n"] = len(rows.get(l["code"], []))
                for a2, b2 in merged.items(): l["see"] = l.get("see", "").replace(a2, b2)
            sub["n"] = sum(l["n"] for l in sub["leaves"])
        F["n"] = sum(sub["n"] for sub in F["subs"]); F["nleaves"] = sum(len(sub["leaves"]) for sub in F["subs"])
    for rs in rows.values():
        for k in rs:
            for a2, b2 in merged.items(): k[3] = k[3].replace(a2, b2)
    report["ft_fixes"] = {"merged": merged, "relabelled": fx.get("ft_relabel", {}), "moved": len(fx.get("ft_move", []))}
    ft = tree["ft"]
    prec = []
    for p in ft["precedence"]:
        txt = remap_text(p[2], leafmap)
        txt = re.sub(r"[^.]*\bweb (series|show)[^.]*\.\s*", "", txt).strip()
        if txt: prec.append([p[0], p[1], txt])
    mods = [remap_text(m, leafmap).replace(", web series", "") for m in ft["modifiers"]]
    prec.append(["S3", "Erotic work or pornography", "Two questions about the work as made: is it explicit (unsimulated sex or genitals in sexual use), and was it made for the art or mainstream circuit or for the adult trade? Not explicit → here, by genre (a non-explicit adult-trade segment only when the field names it as a genre with a canon: pink film, Roman Porno, sexploitation; otherwise the Pleasure Taxonomies). Explicit and made for the art or mainstream circuit (In the Realm of the Senses, Nymphomaniac) → here, by genre. Explicit and made for the adult trade (hardcore features, hentai, adult video) → the Pleasure Taxonomies, with a finder row here. The circuit at making decides, not later fame (docs/ruling-s3-erotic-line.md)."])
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
    M = collections.defaultdict(dict); live = {l["code"] for f in fams for s in f["subs"] for l in s["leaves"]}
    orphan = sum(len(rs) for lf, rs in rows.items() if lf not in live)
    if orphan: report["ft_orphan_rows"] = orphan
    for lf, rs in rows.items():
        if lf in live: M[lf.split("-")[0][0]][lf] = rs
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


def fix_links(tree, report):
    """Apply the offline Wikipedia check (taxonomy/r3/wiki_check.csv): known corrections from link_fixes.json;
    other missing article links are dropped when the leaf has another source, else turned into a Wikipedia search
    link. Category pages are not in the article-title list and are kept."""
    import urllib.parse as up
    chk = os.path.join(R3, "wiki_check.csv")
    if not os.path.exists(chk): return
    missing = {r["url"] for r in csv.DictReader(open(chk)) if r["status"] == "missing" and "/Category:" not in r["url"]}
    fixes = json.load(open(os.path.join(R3, "link_fixes.json")))
    st = collections.Counter()
    for tab in ("va", "ft"):
        for f in tree[tab]["fams"]:
            for s in f["subs"]:
                for l in s["leaves"]:
                    for field in ("src", "catalogues"):
                        lst = l.get(field) or []; out = []
                        for x in lst:
                            u = x[0]
                            if u in missing:
                                t = up.unquote(u.split("/wiki/", 1)[1])
                                if t in fixes:
                                    x = [u.split("/wiki/")[0] + "/wiki/" + fixes[t]] + list(x[1:]); st["corrected"] += 1
                                elif field == "src" and len(lst) > 1:
                                    st["dropped"] += 1; continue
                                else:
                                    x = ["https://en.wikipedia.org/w/index.php?search=" + up.quote(t.replace("_", " "))] + list(x[1:]); st["search"] += 1
                            out.append(x)
                        if lst: l[field] = out
    report["links"] = dict(st)


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
    fix_links(tree, report)
    rp = os.path.join(R3, "report_r3.html")
    if os.path.exists(rp) and '<h2 id="r3">' not in tree["report"]: tree["report"] += "\n" + open(rp).read()
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
