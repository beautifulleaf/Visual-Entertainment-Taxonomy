"""Structure audit of the published tree (both tabs): mechanical checks of leaves and sections.

Logic only; every check is computed from artifact/full/data (tree.json, m-*.json).

  S1 sections      leaves over 40 entries without sections; sections without an axis; declared sections
                   with no members; one-member sections; members outside any section of a sectioned leaf
  S2 era axis      sections whose labels carry dates: ranges must be ordered and must not overlap, and every
                   member's year must fall inside its own section's range (FT)
  S3 order         members within a section in year order (FT; the page's declared order)
  S4 disjointness  one title in two FT leaves; one VA entry name in two leaves' Sub-types
  S5 rank          a section label that is also a leaf label (a thing is a leaf or a section, not both);
                   two leaves with one label
  S6 balance       per sub-family: leaf-size inequality (Gini), leaves of 1–2 entries, leaves over 230
  S7 references    every code named in 'see' and in definitions exists; a code given with a label names
                   that leaf
  S8 arithmetic    leaf n = its rows; sub-family n = sum of its leaves; family leaf counts
  S9 axis kinds    the kind of axis each sectioned leaf uses (era, country, auteur, form/theme), per
                   sub-family, so analogous sub-families can be compared (isomorphism)
  S10 axis purity  country-axis sections: share of members whose country matches the section's majority;
                   auteur-axis sections: share whose director field names the section's filmmaker

Writes taxonomy/audit/structure/{flags.csv, summary.md}.
Run: python3 pipelines/r3/structure_audit.py
"""
import ast, collections, csv, glob, json, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "artifact/full/data")
OUT = os.path.join(ROOT, "taxonomy/audit/structure")


def lit(v, d):
    if isinstance(v, (list, dict)):
        return v
    try:
        return ast.literal_eval(v) if v else d
    except Exception:
        return d


def fold(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s)).strip()


def year(v):
    m = re.match(r"\s*(\d{4})", str(v or ""))
    return int(m.group(1)) if m else None


def era_range(label):
    """(start, end) from a section label, or None. '1990–2004', '(to 1959)', '2020 onward', '1970s', 'Pre-Code (1929–1934)'."""
    t = label.replace("—", "–")
    m = re.search(r"(\d{4})s?\s*[–-]\s*(?:\)|$|,|;)", t)  # "2010s–", "(1994–)": open-ended
    if m:
        return int(m.group(1)), 9999
    m = re.search(r"(\d{4})s?\s*[–-]\s*(\d{2,4})s?", t)
    if m:
        a, b = int(m.group(1)), m.group(2)
        b = int(b) if len(b) == 4 else (a // 100) * 100 + int(b)
        if re.search(rf"{m.group(2)}s", t):
            b += 9
        return a, b
    m = re.search(r"(?:to|until|before|pre-)\s*(\d{4})", t, re.I)
    if m:
        return -9999, int(m.group(1)) - (1 if re.search(r"before|pre-", t, re.I) else 0)
    m = re.search(r"(\d{4})s?\s*(?:onward|onwards|on\b|and after|\+|–\s*$|-\s*$|to present|to date)", t, re.I) or re.search(r"(?:since|from|after)\s*(\d{4})", t, re.I)
    if m:
        return int(m.group(1)), 9999
    m = re.search(r"\b(\d{3})0s\b", t)
    if m:
        a = int(m.group(1)) * 10
        return a, a + 9
    return None


def gini(xs):
    xs = sorted(xs)
    n = len(xs); s = sum(xs)
    if n < 2 or s == 0:
        return 0.0
    return sum((2 * i - n + 1) * x for i, x in enumerate(xs)) / (n * s)


def axis_kind(axis, secs):
    a = (axis or "").lower()
    if re.search(r"\bera\b|period|decade|by date|chronolog|generation|wave|phase|centur|cycle", a) or \
            (secs and sum(1 for s in secs if era_range(s)) >= max(2, len(secs) // 2)):
        return "era"
    if re.search(r"countr|nation|region|by place|geograph|tradition of", a):
        return "country/region"
    if re.search(r"auteur|director|filmmaker|by maker|by artist|studio|school", a):
        return "auteur/school"
    return "form/theme"


def main():
    os.makedirs(OUT, exist_ok=True)
    tree = json.load(open(os.path.join(DATA, "tree.json")))
    rows = {"ft": {}, "va": {}}
    for p in glob.glob(os.path.join(DATA, "m-*.json")):
        tab = os.path.basename(p).split("-")[1]
        rows[tab].update(json.load(open(p)))
    flags = []

    def flag(check, sev, tab, where, what, evidence=""):
        flags.append(dict(check=check, severity=sev, tab=tab.upper(), where=where, what=what, evidence=evidence))

    leaves = {}
    for tab in ("ft", "va"):
        for f in tree[tab]["fams"]:
            for s in f["subs"]:
                for l in s["leaves"]:
                    l = dict(l); l["secs"] = lit(l.get("secs"), []); l["fam"] = f["code"]; l["sub"] = s["code"]; l["tab"] = tab
                    l["n"] = int(l.get("n") or 0)
                    leaves[(tab, l["code"])] = l
    labels = collections.defaultdict(list)
    for (tab, c), l in leaves.items():
        labels[(tab, fold(l["label"]))].append(c)

    # ---- S8 arithmetic -----------------------------------------------------------------------------
    for tab in ("ft", "va"):
        for f in tree[tab]["fams"]:
            nl = sum(len(s["leaves"]) for s in f["subs"])
            if f.get("nleaves") is not None and int(f["nleaves"]) != nl:
                flag("S8", "medium", tab, f"{f['code']} {f['label']}", "family leaf count differs from its leaves", f"stated {f['nleaves']}, counted {nl}")
            for s in f["subs"]:
                tot = sum(int(l.get("n") or 0) for l in s["leaves"])
                if s.get("n") is not None and int(s["n"]) != tot:
                    flag("S8", "low", tab, f"{s['code']} {s['label']}", "sub-family count differs from the sum of its leaves", f"stated {s['n']}, sum {tot}")
    for (tab, c), l in leaves.items():
        r = rows[tab].get(c, [])
        if l["n"] != len(r):
            flag("S8", "low", tab, f"{c} {l['label']}", "leaf count differs from its rows", f"n {l['n']}, rows {len(r)}")

    # ---- S1, S2, S3, S10 per leaf --------------------------------------------------------------------
    axis_by_sub = collections.defaultdict(collections.Counter)
    era_bad_members = 0
    for (tab, c), l in leaves.items():
        r = rows[tab].get(c, [])
        secs = l["secs"]
        name = f"{c} {l['label']}"
        if tab == "ft":
            if len(r) > 40 and not secs:
                flag("S1", "medium", tab, name, "over 40 titles and no sections", f"{len(r)} titles")
            if not secs:
                continue
            if not (l.get("axis") or "").strip():
                flag("S1", "medium", tab, name, "sections without a stated axis", "; ".join(secs[:6]))
            groups = collections.defaultdict(list); loose = []
            for x in r:
                i = str(x[8]).strip()
                if i.isdigit() and 0 < int(i) <= len(secs):
                    groups[int(i) - 1].append(x)
                else:
                    loose.append(x)
            if loose:
                flag("S1", "medium" if len(loose) > 3 else "low", tab, name, "titles outside every section of a sectioned leaf",
                     f"{len(loose)}: " + "; ".join(f"{x[0]} ({x[1]})" for x in loose[:4]))
            for i, sname in enumerate(secs):
                g = groups.get(i, [])
                if not g:
                    flag("S1", "low", tab, name, "declared section with no titles", sname)
                elif len(g) == 1 and len(secs) > 1:
                    flag("S1", "low", tab, name, "one-title section", f"{sname}: {g[0][0]} ({g[0][1]})")
            kind = axis_kind(l.get("axis"), secs); axis_by_sub[(tab, l["sub"])][kind] += 1
            # S2 era validity
            rng = {i: era_range(s) for i, s in enumerate(secs)}
            dated = [(i, rg) for i, rg in rng.items() if rg]
            def pure(x):  # a date band: nothing but dates and era words once the dates are removed
                rest = re.sub(r"\(?\b(?:to|until|before|since|from|after|onward|onwards|pre|the|and|early|late|mid|era|years|period|s)\b\)?|\d{2,4}s?|[–\-()+,]", " ", x.lower())
                return not rest.strip()
            bands = [(i, rg) for i, rg in dated if pure(secs[i])]
            if len(bands) >= 2:
                seq = [rg for _, rg in sorted(bands)]
                for (a1, b1), (a2, b2) in zip(seq, seq[1:]):
                    if a2 < a1:
                        flag("S2", "medium", tab, name, "era sections out of chronological order", f"{a1}–{b1} before {a2}–{b2}")
                    elif a2 <= b1:
                        flag("S2", "medium", tab, name, "era sections overlap", f"{a1}–{b1} and {a2}–{b2}")
                setting = re.search(r"period|historical|history|war\b|epic|setting|set in", (l["label"] + " " + (l.get("axis") or "")).lower())
                for i, (a, b) in ([] if setting else dated):
                    out = [x for x in groups.get(i, []) if (y := year(x[1])) is not None and not (a <= y <= b)]
                    if out:
                        era_bad_members += len(out)
                        flag("S2", "medium" if len(out) > 2 else "low", tab, name, "titles outside their era section's dates",
                             f"{secs[i]}: " + "; ".join(f"{x[0]} ({x[1]})" for x in out[:4]) + (f" (+{len(out) - 4})" if len(out) > 4 else ""))
            # S3 order within each section
            for i, g in groups.items():
                ys = [year(x[1]) for x in g if year(x[1]) is not None]
                if any(b < a for a, b in zip(ys, ys[1:])):
                    flag("S3", "low", tab, name, "section not in year order", secs[i])
            # S10 purity
            if re.search(r"country of production|national cinema|by country\b", (l.get("axis") or "").lower()):
                for i, g in groups.items():
                    cs = collections.Counter(cc for x in g for cc in set(str(x[9] or "").split("|")) if cc)
                    if len(g) >= 5 and cs and not secs[i].lower().startswith("other"):
                        top, n = cs.most_common(1)[0]
                        if n / len(g) < 0.6:
                            flag("S10", "low", tab, name, "country section with mixed countries", f"{secs[i]}: top {top} {n}/{len(g)}; {dict(cs.most_common(4))}")
            if re.search(r"filmmaker|director|auteur", (l.get("axis") or "").lower()):
                for i, g in groups.items():
                    sur = [w for w in fold(secs[i]).split() if len(w) > 3]
                    if not sur or len(g) < 3 or secs[i].lower().startswith("other"):
                        continue
                    hit = sum(1 for x in g if any(w in fold(x[2]) for w in sur))
                    if 0 < hit / len(g) < 0.6:
                        flag("S10", "low", tab, name, "filmmaker section whose titles are mostly by others", f"{secs[i]}: {hit}/{len(g)} by the named filmmaker")
        else:
            groups = collections.Counter(x[1] for x in r)
            if secs:
                kind = axis_kind(l.get("axis"), [s for s in secs if s not in ("Holding institutions",)]); axis_by_sub[(tab, l["sub"])][kind] += 1
            for g, n in groups.items():
                if n == 1 and g not in ("Holding institutions",) and len(groups) > 1 and len(r) > 10:
                    pass  # single-entry groups are common and legitimate in VA (one founder, one centre)

    # ---- S4 disjointness ---------------------------------------------------------------------------
    where = collections.defaultdict(set)
    for c, r in rows["ft"].items():
        for x in r:
            if x[5]:
                where[x[5]].add(c)
    multi = {k: v for k, v in where.items() if len(v) > 1}
    title = {x[5]: f"{x[0]} ({x[1]})" for r in rows["ft"].values() for x in r}
    for k, v in sorted(multi.items(), key=lambda x: title.get(x[0], "")):
        flag("S4", "medium", "ft", title.get(k, k), "one title in two leaves", ", ".join(sorted(v)))
    vk = collections.defaultdict(set)
    for c, r in rows["va"].items():
        for x in r:
            if x[1] == "Sub-types":
                vk[fold(x[0])].add(c)
    for k, v in vk.items():
        if len(v) > 1 and len(k) > 3:
            flag("S4", "low", "va", k, "one sub-type name in two leaves", ", ".join(sorted(v)))

    # ---- S5 rank -------------------------------------------------------------------------------------
    for (tab, lab), cs in labels.items():
        byfam = collections.defaultdict(list)
        for c in cs:
            byfam[c[0]].append(c)
        for fam, same in byfam.items():  # film and television leaves may share a genre name: the form split is deliberate
            if len(same) > 1:
                flag("S5", "medium", tab, lab, "two leaves with one label in one family", ", ".join(same))
    for (tab, c), l in leaves.items():
        if tab != "ft":
            continue
        for s in l["secs"]:
            hit = [x for x in labels.get((tab, fold(s)), []) if x != c and x[0] == c[0]]  # same family; form splits are deliberate
            if hit:
                flag("S5", "medium", tab, f"{c} {l['label']}", "section label is also a leaf elsewhere", f"section '{s}' = leaf {', '.join(hit)}")

    # ---- S6 balance ----------------------------------------------------------------------------------
    bal = []
    for tab in ("ft", "va"):
        for f in tree[tab]["fams"]:
            for s in f["subs"]:
                ns = [int(l.get("n") or 0) for l in s["leaves"]]
                if len(ns) >= 3:
                    g = gini(ns); top = max(ns) / max(1, sum(ns))
                    bal.append((tab, s["code"], s["label"], len(ns), sum(ns), g, top))
                    if g > 0.6 or (top > 0.5 and len(ns) >= 4):
                        flag("S6", "low", tab, f"{s['code']} {s['label']}", "uneven sub-family: one or few leaves hold most entries",
                             f"Gini {g:.2f}; largest leaf {top:.0%} of {sum(ns)} across {len(ns)} leaves")
                for l in s["leaves"]:
                    n = int(l.get("n") or 0)
                    if tab == "ft" and 0 < n <= 2:
                        flag("S6", "low", tab, f"{l['code']} {l['label']}", "leaf of 1–2 titles", f"n {n}")
                    if tab == "ft" and n > 230:
                        flag("S6", "medium", tab, f"{l['code']} {l['label']}", "leaf over the 230-title cap", f"n {n}")

    # ---- S7 references ------------------------------------------------------------------------------
    code_rx = re.compile(r"\b([A-N]\d{1,2}(?:-\d{1,3})?)\b(?:\s+([A-Z][^;,.()]*))?")
    subs = {(tab, s["code"]): s["label"] for tab in ("ft", "va") for f in tree[tab]["fams"] for s in f["subs"]}
    for (tab, c), l in leaves.items():
        for field in ("see", "defn"):
            text = re.sub(r"<[^>]+>", "", l.get(field) or "")
            if re.search(r"possession taxonom|pleasure taxonom|interactive entertainment|culinary", text, re.I):
                text = re.split(r"(?i)possession taxonom|pleasure taxonom|interactive entertainment|culinary", text)[0]
            for m in code_rx.finditer(text):
                ref, lab = m.group(1), (m.group(2) or "").strip()
                own = (tab, ref) in leaves or (tab, ref) in subs
                other = ("va" if tab == "ft" else "ft", ref)
                if not own:
                    if other in leaves or other in subs:
                        continue  # cross-tab reference
                    flag("S7", "medium", tab, f"{c} {l['label']}", f"{field} names a code that does not exist", ref + (f" {lab}" if lab else ""))
                    continue
                target = leaves[(tab, ref)]["label"] if (tab, ref) in leaves else subs[(tab, ref)]
                if lab and len(lab) > 3:
                    a, b = fold(lab), fold(target)
                    if not (a.startswith(b[:8]) or b.startswith(a[:8]) or set(a.split()) & set(b.split())):
                        flag("S7", "medium", tab, f"{c} {l['label']}", f"{field} gives a code with another leaf's label",
                             f"{ref} '{lab}' but {ref} is '{target}'")

    # ---- write ---------------------------------------------------------------------------------------
    order = {"high": 0, "medium": 1, "low": 2}
    flags.sort(key=lambda f: (f["check"], order[f["severity"]], f["tab"], f["where"]))
    with open(os.path.join(OUT, "flags.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["check", "severity", "tab", "where", "what", "evidence"]); w.writeheader(); w.writerows(flags)
    byc = collections.defaultdict(collections.Counter)
    for f in flags:
        byc[(f["check"], f["what"])][f["severity"]] += 1
    nsec = sum(1 for (t, c), l in leaves.items() if t == "ft" and l["secs"])
    L = ["# Structure audit", "",
         f"Computed from the published data: FT {sum(1 for k in leaves if k[0] == 'ft')} leaves ({nsec} sectioned), "
         f"VA {sum(1 for k in leaves if k[0] == 'va')} leaves. Flags in `flags.csv`.", "",
         "| Check | Finding | High | Medium | Low |", "|---|---|---:|---:|---:|"]
    for (ch, what), c in sorted(byc.items()):
        L.append(f"| {ch} | {what} | {c['high']} | {c['medium']} | {c['low']} |")
    L += ["", f"S2: {era_bad_members} titles fall outside the dates of their era section.", "",
          "## S9 Axis kinds per sub-family (sectioned leaves)", "", "| Tab | Sub-family | era | country/region | auteur/school | form/theme |", "|---|---|---:|---:|---:|---:|"]
    sublab = {(tab, s["code"]): s["label"] for tab in ("ft", "va") for f in tree[tab]["fams"] for s in f["subs"]}
    for (tab, sc), c in sorted(axis_by_sub.items(), key=lambda x: (x[0][0], [int(p) if p.isdigit() else p for p in re.findall(r"\d+|\D+", x[0][1])])):
        L.append(f"| {tab.upper()} | {sc} {sublab.get((tab, sc), '')} | {c['era']} | {c['country/region']} | {c['auteur/school']} | {c['form/theme']} |")
    L += ["", "## S6 Most uneven sub-families", "", "| Tab | Sub-family | Leaves | Entries | Gini | Largest leaf |", "|---|---|---:|---:|---:|---:|"]
    for tab, sc, lab, n, tot, g, top in sorted(bal, key=lambda x: -x[5])[:15]:
        L.append(f"| {tab.upper()} | {sc} {lab} | {n} | {tot:,} | {g:.2f} | {top:.0%} |")
    for ch, title in (("S2", "Era sections: examples"), ("S4", "One title in two leaves (FT)"), ("S5", "Rank conflicts"), ("S7", "Broken references")):
        sel = [f for f in flags if f["check"] == ch and f["severity"] != "low"][:15] or [f for f in flags if f["check"] == ch][:10]
        if sel:
            L += ["", f"## {title}", "", "| Tab | Where | What | Evidence |", "|---|---|---|---|"]
            L += [f"| {f['tab']} | {f['where']} | {f['what']} | {f['evidence'].replace('|', '/')[:220]} |" for f in sel]
    open(os.path.join(OUT, "summary.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L[:40]))
    print(len(flags), "flags")


if __name__ == "__main__":
    main()
