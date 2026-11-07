"""VA completeness audit: is the Visual Art tree complete with respect to what was gathered?

Logic only, no new searching. The reference is the collections cross-reference
(every gathered museum record, grouped by source label x medium family and mapped to
leaf / general:<family> / missing:<tradition> / exclude:<reason>), the coverage
probes, and the published tree itself.

Checks
  V1 mass balance        share of gathered objects that resolve to a leaf, per family
  V2 qualified general   labels that name a period, school or ware but resolved only to
                         general:<family>: a mapping miss (a leaf matches the qualifier)
                         or a gap (none does)
  V3 culture x medium    cultures with many objects in a family that their source labels
                         cannot place on any leaf: a missing leaf, or a label coarser than
                         the leaves (culture- or period-only); needs object-level data to tell
  V4 missing residue     named traditions with objects and no leaf (open unless a leaf
                         now carries the name)
  V5 chronology          holes in the date span of a culture's leaves within one family
  V6 leaf completeness   every leaf: definition, source, View-all catalogues, a way to
                         see the works (holding institutions, or makers/artists), no
                         leftover per-object works lists, no empty leaf
  V7 probes              coverage probes still weak or missing

Writes taxonomy/audit/va_completeness/{flags.csv, summary.md}.
Run: python3 pipelines/r3/va_completeness_audit.py
"""
import ast, collections, csv, glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "artifact/full/data")
COL = os.path.join(ROOT, "taxonomy/r3/collections")
OUT = os.path.join(ROOT, "taxonomy/audit/va_completeness")

OBJECT_FAMS = "ABCDEFGHIJ"  # families the museum records are typed into
STANDARD_SECS = {"Sub-types", "Centres & workshops", "Holding institutions", "Makers", "Artists",
                 "Schools & phases", "Architects", "Sub-styles", "Founders", "Movements",
                 "Designers", "Photographers", "Studios", "Sites to visit", "Registers & databases"}
MAKER_SECS = {"Makers", "Artists", "Architects", "Founders", "Designers", "Photographers"}


def lit(v, default):
    if isinstance(v, (list, dict)):
        return v
    if not v:
        return default
    try:
        return ast.literal_eval(v)
    except Exception:
        return default


def norm(s):
    s = s.lower().replace("’", "'")
    s = re.sub(r"[^a-z0-9' ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def head(label):
    """The culture part of a source label: 'Greek, Attic' -> 'greek'; 'Japan · Edo' -> 'japan'."""
    h = re.split(r"[,·(;/]| - ", label, maxsplit=1)[0]
    h = norm(h)
    for a, b in (("japanese", "japan"), ("chinese", "china"), ("indian", "india"), ("korean", "korea"),
                 ("persian", "iran"), ("iranian", "iran"), ("egyptian", "egypt"), ("turkish", "turkey"),
                 ("french", "france"), ("italian", "italy"), ("german", "germany"), ("spanish", "spain"),
                 ("english", "britain"), ("british", "britain"), ("dutch", "netherlands"), ("greek", "greece"),
                 ("roman", "rome"), ("indonesian", "indonesia"), ("mexican", "mexico"), ("peruvian", "peru")):
        if h == a:
            return b
    return h


def qualifier(label):
    parts = re.split(r"[,·(;]", label, maxsplit=1)
    q = norm(parts[1]) if len(parts) > 1 else ""
    return q


CENT = re.compile(r"(\d{1,2})(?:st|nd|rd|th)(?:\s*(?:[–-]|to(?: the)?)\s*(?:early |mid-?|late )?(\d{1,2})(?:st|nd|rd|th))?\s*(?:-|\s)?centur(?:y|ies)(\s*(?:BCE|BC))?", re.I)
YEARS = re.compile(r"(?<![\d.])(\d{3,4})(?:\s*[–-]\s*(\d{2,4}))?(\s*(?:BCE|BC))?(?![\d])")


def span(text):
    """Rough date span (start, end) from a definition; None if no dates."""
    if not text:
        return None
    t = re.sub(r"<[^>]+>", "", text)
    pts = []
    for m in CENT.finditer(t):
        a = int(m.group(1)); b = int(m.group(2) or a); bce = bool(m.group(3))
        if bce:
            pts += [-100 * a, -100 * (b - 1)]
        else:
            pts += [100 * (a - 1), 100 * b]
    t2 = CENT.sub(" ", t)
    for m in YEARS.finditer(t2):
        a = int(m.group(1))
        if not (300 <= a <= 2030) and not m.group(3):
            continue
        b = m.group(2)
        b = int(b) if b else a
        if b < 100 and m.group(2):  # 1780–95
            b = (a // 100) * 100 + b
        if m.group(3):
            a, b = -a, -b
        pts += [a, b]
    if not pts:
        return None
    return min(pts), max(pts)


def load_tree():
    t = json.load(open(os.path.join(DATA, "tree.json")))["va"]
    leaves = {}
    for f in t["fams"]:
        for s in f["subs"]:
            for l in s["leaves"]:
                l = dict(l); l["fam"] = f["code"]; l["sub"] = s["code"]; l["sub_label"] = s["label"]
                l["secs"] = lit(l.get("secs"), []); l["catalogues"] = lit(l.get("catalogues"), [])
                l["src"] = lit(l.get("src"), []); l["n"] = int(l.get("n") or 0)
                leaves[l["code"]] = l
    rows = {}
    for p in glob.glob(os.path.join(DATA, "m-va-*.json")):
        rows.update(json.load(open(p)))
    return t, leaves, rows


def load_keys():
    keys = []
    for f in sorted(glob.glob(os.path.join(COL, "out_col_*.csv"))):
        b = f.split("out_col_")[1][:-4]
        inn = {(r["file"], r["label"], r["family"]): r for r in csv.DictReader(open(os.path.join(COL, f"in_col_{b}.csv")))}
        for r in csv.DictReader(open(f)):
            i = inn.get((r["file"], r["label"], r["family"]))
            if not i:
                continue
            mp = r["map"].strip()
            kind = mp.split(":", 1)[0] if ":" in mp else "leaf"
            keys.append(dict(batch=b, file=r["file"], label=r["label"], family=r["family"], map=mp, kind=kind,
                             objects=int(i["objects"] or 0), institutions=int(i["institutions"] or 0),
                             top=i["top_institutions"], sample=i.get("sample_title", "")))
    return keys


def main():
    os.makedirs(OUT, exist_ok=True)
    tree, leaves, rows = load_tree()
    keys = load_keys()
    flags = []

    def flag(check, severity, where, what, evidence, objects=""):
        flags.append(dict(check=check, severity=severity, where=where, what=what, evidence=evidence, objects=objects))

    # name index of leaves: label + aliases (+ alias rows), by family
    names = collections.defaultdict(list)
    for c, l in leaves.items():
        for n in [l["label"]] + [a for a in re.split(r";\s*", l.get("aliases") or "") if a] + lit(l.get("alias_rows"), []):
            nn = norm(n)
            if nn:
                names[nn].append(c)

    for c, l in leaves.items():
        for n in lit(l.get("collections_from"), []):
            names[norm(n)].append(c)
    mf = os.path.join(ROOT, "taxonomy/r3/va_out/missing_traditions/merges.csv")
    if os.path.exists(mf):
        for r in csv.DictReader(open(mf)):
            names[norm(r["tradition"])].append(r["leaf_code"])

    def leaf_for(text, fam=None):
        """Leaves whose name contains, or is contained in, the text (word-bounded)."""
        t = norm(text)
        if len(t) < 4:
            return []
        hits = set()
        for n, cs in names.items():
            if len(n) < 4:
                continue
            if re.search(rf"\b{re.escape(n)}\b", t) or re.search(rf"\b{re.escape(t)}\b", n):
                hits.update(c for c in cs if fam is None or fam == "?" or leaves[c]["fam"] == fam)
        return sorted(hits)

    # ---- V1 mass balance -------------------------------------------------
    mass = collections.defaultdict(collections.Counter)
    for k in keys:
        fam = k["family"] if k["family"] in OBJECT_FAMS else "?"
        if k["kind"] == "leaf" and k["map"] in leaves:
            fam = leaves[k["map"]]["fam"] if fam == "?" else fam
        mass[fam][k["kind"]] += k["objects"]
    tot = collections.Counter()
    for c in mass.values():
        tot.update(c)

    # ---- V2 qualified general --------------------------------------------
    v2 = collections.Counter()
    rv = os.path.join(OUT, "v2_review.csv")
    reviewed = {(r["label"], r["family"]) for r in csv.DictReader(open(rv))} if os.path.exists(rv) else set()
    for k in keys:
        if k["kind"] != "general":
            continue
        q = qualifier(k["label"])
        q = " ".join(w for w in q.split() if w not in VAGUE and not w.isdigit())
        if not q or k["objects"] < 200:
            continue
        fam = k["map"].split(":", 1)[1] if ":" in k["map"] else k["family"]
        hit = leaf_for(q, fam)
        if (k["label"], k["family"]) in reviewed:
            v2["reviewed: kept general"] += k["objects"]
            continue
        if hit:
            v2["mapping miss"] += k["objects"]
            flag("V2", "high" if k["objects"] >= 2000 else "medium", f"{k['label']} [{fam}]",
                 "label names a leaf: remap if that leaf holds the whole key", f"qualifier '{q}' matches {', '.join(hit[:4])}", k["objects"])
        else:
            v2["gap candidate"] += k["objects"]
            flag("V2", "medium" if k["objects"] >= 2000 else "low", f"{k['label']} [{fam}]",
                 "label names a period/school/ware but resolves only to general; no leaf carries it",
                 f"qualifier '{q}'; top: {k['top'][:90]}", k["objects"])

    # ---- V3 culture x medium grid ------------------------------------------
    grid = collections.defaultdict(lambda: collections.Counter())  # (culture, fam) -> kind -> objects
    culture_leaf_fams = collections.defaultdict(set)
    for k in keys:
        cu = head(k["label"])
        if not cu:
            continue
        if k["kind"] == "leaf" and k["map"] in leaves:
            fam = leaves[k["map"]]["fam"]
            culture_leaf_fams[cu].add(fam)
        else:
            fam = k["map"].split(":", 1)[1] if k["kind"] == "general" and ":" in k["map"] else k["family"]
        if fam not in OBJECT_FAMS:
            continue
        grid[(cu, fam)][k["kind"]] += k["objects"]
    resolved_cell = collections.Counter()
    vc = os.path.join(OUT, "v3_cells.csv")
    if os.path.exists(vc):  # written by collections_resolve.py: general objects whose own title names a leaf
        for r in csv.DictReader(open(vc)):
            resolved_cell[(r["culture"], r["family"])] = int(r["resolved"])
    for (cu, fam), c in sorted(grid.items(), key=lambda x: -sum(x[1].values())):
        inscope = c["leaf"] + c["general"] + c["missing"]
        if inscope < 1000:
            continue
        share = (c["leaf"] + resolved_cell[(cu, fam)]) / inscope
        if share < 0.10:
            other = sorted(culture_leaf_fams[cu] - {fam})
            sev = "high" if other and inscope >= 5000 else ("medium" if other or inscope >= 5000 else "low")
            flag("V3", sev, f"{cu} × {fam}", "coverage not verifiable from the records: the label names only a culture and the titles name no tradition (see residual title words in v3_cells.csv); a coarse label, not a missing leaf, unless those words name one",
                 f"leaf {share:.0%} of {inscope:,} in scope (incl. {resolved_cell[(cu, fam)]:,} resolved by title); general {c['general']:,}, missing {c['missing']:,}; "
                 f"leaves in other families: {''.join(other) or 'none'}", inscope)

    # ---- V4 missing residue ----------------------------------------------
    miss = collections.defaultdict(lambda: dict(objects=0, inst=0, fams=set(), labels=set()))
    for k in keys:
        if k["kind"] != "missing":
            continue
        n = k["map"].split(":", 1)[1].strip()
        m = miss[n]; m["objects"] += k["objects"]; m["inst"] = max(m["inst"], k["institutions"])
        m["fams"].add(k["family"]); m["labels"].add(k["label"])
    resolved = 0
    for n, m in sorted(miss.items(), key=lambda x: -x[1]["objects"]):
        hit = [c for c in names.get(norm(n), [])]
        if hit:
            resolved += 1
            continue
        sev = "high" if m["objects"] >= 1000 and m["inst"] >= 2 else ("medium" if m["objects"] >= 200 else "low")
        flag("V4", sev, n, "named tradition with gathered objects and no leaf",
             f"families {''.join(sorted(m['fams']))}; max institutions per key {m['inst']}; labels: {'; '.join(sorted(m['labels']))[:100]}", m["objects"])

    # ---- V5 chronology holes ---------------------------------------------
    chains = collections.defaultdict(set)
    for k in keys:
        if k["kind"] == "leaf" and k["map"] in leaves and k["objects"] >= 50:
            chains[(head(k["label"]), leaves[k["map"]]["fam"])].add(k["map"])
    for (cu, fam), codes in sorted(chains.items()):
        sp = sorted((s, c) for c in codes if (s := span(leaves[c].get("defn"))))
        if len(sp) < 3:
            continue
        reach = sp[0][0][1]; prev = sp[0][1]
        for (a, b), c in sp[1:]:
            if a - reach >= 150:
                flag("V5", "low", f"{cu} × {fam}", "hole in the dated chain of this culture's leaves",
                     f"{reach}–{a}: nothing between {prev} {leaves[prev]['label']} and {c} {leaves[c]['label']}")
            if b > reach:
                reach, prev = b, c

    # ---- V6 leaf completeness ---------------------------------------------
    leftover = 0
    for c, l in leaves.items():
        r = rows.get(c, [])
        groups = collections.Counter(x[1] for x in r)
        if not r:
            flag("V6", "medium" if l["catalogues"] else "high", f"{c} {l['label']}",
                 "leaf has no rows: the card shows only the definition" + (" and View-all links" if l["catalogues"] else ""), "n = 0")
        if not (l.get("defn") or "").strip():
            flag("V6", "high", f"{c} {l['label']}", "no definition", "")
        if not l["src"]:
            flag("V6", "medium", f"{c} {l['label']}", "no attesting source", "")
        if not l["catalogues"]:
            flag("V6", "medium", f"{c} {l['label']}", "no View-all catalogue", "")
        has_inst = groups.get("Holding institutions", 0) > 0
        has_makers = any(groups.get(g, 0) for g in MAKER_SECS)
        if r and l["fam"] in OBJECT_FAMS and l["fam"] != "J" and not has_inst and not has_makers:
            flag("V6", "low" if l["catalogues"] else "high", f"{c} {l['label']}", "no way to see the works: neither holding institutions nor makers",
                 f"groups: {dict(groups)}")
        for g, n in groups.items():
            if g in STANDARD_SECS or g in COUNTRY_SECS:
                continue
            # a non-standard group whose rows carry object-style notes (museum, accession) is a leftover works list
            objs = sum(1 for x in r if x[1] == g and re.search(r"museum|collection|accession|\bAD\b|Hegira", x[2] or "", re.I))
            if objs >= max(2, n // 2):
                leftover += n
                flag("V6", "low", f"{c} {l['label']}", "per-object works list left after the collections-first rule",
                     f"group '{g}': {n} rows")
        empty = [s for s in l["secs"] if not groups.get(s)]
        if empty:
            flag("V6", "low", f"{c} {l['label']}", "declared section with no rows", "; ".join(empty))

    # ---- V7 probes ---------------------------------------------------------
    probes = list(csv.DictReader(open(os.path.join(ROOT, "taxonomy/audit/coverage_probes_va.csv"))))
    for p in probes:
        st = (p.get("status") or "").strip()
        home = (p.get("home") or "").strip()
        code = home.split(" ")[0] if home else ""
        if st in ("weak", "missing"):
            now = leaf_for(p["probe"])
            flag("V7", "medium" if st == "missing" else "low", p["probe"], f"probe {st} at audit time",
                 f"home then: {home or '-'}; leaf names matching now: {', '.join(now[:4]) or 'none'}; {p.get('comment','')[:80]}")
        elif st == "ok" and code and code not in leaves:
            flag("V7", "medium", p["probe"], "probe home no longer exists", home)

    # ---- write -----------------------------------------------------------
    order = {"high": 0, "medium": 1, "low": 2}
    flags.sort(key=lambda f: (f["check"], order[f["severity"]], -(f["objects"] or 0) if isinstance(f["objects"], int) else 0))
    with open(os.path.join(OUT, "flags.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["check", "severity", "where", "what", "evidence", "objects"])
        w.writeheader(); w.writerows(flags)

    byc = collections.defaultdict(collections.Counter)
    for f in flags:
        byc[f["check"]][f["severity"]] += 1
    famlabel = {f["code"]: f["label"] for f in tree["fams"]}
    L = ["# VA completeness audit", "",
         "Reference: the gathered museum records as mapped by the collections cross-reference "
         "(object counts are per source label × medium key), the coverage probes, and the published tree. "
         "No new searching. Flags in `flags.csv`.", "",
         "## V1 Mass balance: where gathered objects resolve", "",
         "| Family | Leaf | General only | Named, no leaf | Excluded | Leaf share of in-scope |",
         "|---|---:|---:|---:|---:|---:|"]
    for fam in sorted(mass, key=lambda x: (x == "?", x)):
        c = mass[fam]; ins = c["leaf"] + c["general"] + c["missing"]
        L.append(f"| {fam} {famlabel.get(fam, 'unknown type')} | {c['leaf']:,} | {c['general']:,} | {c['missing']:,} | {c['exclude']:,} | {c['leaf'] / ins:.0%} |" if ins else
                 f"| {fam} {famlabel.get(fam, 'unknown type')} | 0 | 0 | 0 | {c['exclude']:,} | – |")
    ins = tot["leaf"] + tot["general"] + tot["missing"]
    L += [f"| **All** | {tot['leaf']:,} | {tot['general']:,} | {tot['missing']:,} | {tot['exclude']:,} | **{tot['leaf'] / ins:.0%}** |", "",
          f"Of the general-only objects, {v2['reviewed: kept general']:,} sit under labels reviewed and kept general "
          f"(`v2_review.csv`: the named leaf does not hold the whole label), {v2['mapping miss']:,} under unreviewed labels whose "
          f"qualifier names a leaf, and {v2['gap candidate']:,} under qualified labels no leaf carries. "
          f"V3 counts general objects resolved by their own titles (`v3_cells.csv`, `pipelines/r3/collections_resolve.py`).", "",
          "## Flags by check", "", "| Check | High | Medium | Low |", "|---|---:|---:|---:|"]
    for ch in sorted(byc):
        L.append(f"| {ch} | {byc[ch]['high']} | {byc[ch]['medium']} | {byc[ch]['low']} |")
    L += ["", f"V4: {len(miss)} named missing traditions in the mapping, {resolved} now carried by a leaf name, "
          f"{len(miss) - resolved} open. V6: {leftover:,} rows in leftover per-object works lists.", ""]
    for ch, title in (("V2", "Qualified labels resolved only to general (top 15)"), ("V3", "Culture × medium gaps (top 15)"),
                      ("V4", "Open named traditions (top 15)"), ("V6", "Leaf completeness (high and medium, top 15)")):
        sel = [f for f in flags if f["check"] == ch and (ch != "V6" or f["severity"] != "low")][:15]
        if not sel:
            continue
        L += [f"### {title}", "", "| Severity | Where | What | Evidence | Objects |", "|---|---|---|---|---:|"]
        for f in sel:
            ob = f"{f['objects']:,}" if isinstance(f["objects"], int) else ""
            L.append(f"| {f['severity']} | {f['where']} | {f['what']} | {f['evidence'].replace('|', '/')} | {ob} |")
        L.append("")
    open(os.path.join(OUT, "summary.md"), "w").write("\n".join(L))
    print("\n".join(L[:40]))
    print(f"\n{len(flags)} flags -> {os.path.relpath(OUT, ROOT)}/")


COUNTRY_SECS = set()
VAGUE = {"undated", "unlocalised", "unlocalized", "unknown", "probably", "possibly", "attributed", "early", "late",
         "mid", "modern", "period", "archaeological", "culture", "style", "and", "or", "the", "of", "c"}

if __name__ == "__main__":
    _, _lv, _rows = load_tree()
    # country-named groups (Art Nouveau by country etc.) are standard sections, not works lists
    _all = collections.Counter(x[1] for v in _rows.values() for x in v)
    COUNTRY_SECS.update(g for g in _all if re.fullmatch(r"[A-Z][a-z]+(?: [A-Z][a-z]+)*", g) and _all[g] >= 5 and len(g.split()) <= 3)
    main()
