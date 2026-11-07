"""Structure-audit fixes applied at assembly (owner, 2026-11-07: "fix the FT structural flags", "fix the VA structural
flags as well"). Called by assemble.py after both tabs are built and before fix_structure / fix_links.

Decisions are listed in DECISIONS (each one a judgement recorded here, with its reason); everything else is a rule:

FT
  1  one home: a title in two leaves keeps the leaf of its form (series in B, film in A, short in A21)
  2  duplicate labels within a family: the same concept in two sub-families merges into the larger leaf (titles move,
     the label survives, the code maps in ft_migration.csv); a real facet split is renamed with a qualifier
  3  rank: a section whose label is a leaf of the same family gives its titles to that leaf; form and tradition splits
     (shorts, TVB, features versus series) keep the section under a qualified name
  4  leaves over 40 titles without sections are sectioned by rule: movements by filmmaker; documentary, experimental,
     short and animation leaves by era of release; other genres by era, else by country, else by filmmaker. Era bins
     are film-history decades merged until each holds at least max(8, n/8) titles (at most 7 sections)
  5  loose titles go to the section of their director's other titles in the leaf; else, in date-sectioned leaves, to the
     one section whose dates (and nationality, if named) fit; else to the section of their country; else to a final
     "Other" section named for the leaf
  6  a title outside its date-band section moves to the one section whose dates contain its year
  7  small repairs: empty declared sections dropped, missing axes written, broken codes corrected, year order
VA
  8  an entry name in two leaves: kept in its own leaf and removed from the sibling that only notes it; where two
     cultures share a term, qualified by culture
  10 country of production (FT): TSPDT country names ("USA", "West Germany", "France-Italy") become the codes the other
     rows use (US, DE, FR|IT), from taxonomy/r3/country_codes.json; UK becomes GB; "---" (unknown) becomes empty
  11 one id given to two different titles (TSPDT slugs): the second keeps a slug of its own title
  9  see references (both tabs): pass-name prefixes and suffixes removed; a code with a label is pointed at the leaf
     with that label; a label that names an entry rather than a leaf is written as "Label (in CODE Leaf)"; codes that
     resolve to nothing are dropped and the label kept
"""
import collections, csv, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from structure_audit import era_range, fold, year  # noqa: E402

R3 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "taxonomy", "r3")

DECISIONS = {
    # 1 one home: (title id, leaf to remove it from, reason)
    "ft_remove": [
        ("tt1321865", "A11-13", "Carlos: made as a three-part television serial; B7-21 keeps it"),
        ("tt0161382", "A11-6", "Cartesius: Rossellini's television film in two parts; B1-27 keeps it"),
        ("tt0783612", "A19-10", "When the Levees Broke: HBO documentary in four acts; B11-3 keeps it"),
        ("tt0070904", "A1-15", "World on a Wire: Fassbinder's two-part television film; B9-6 keeps it"),
    ],
    # one id shared by two different films (TSPDT slug): the second gets its own id
    "ft_reid": [],  # handled by rule 11 (e.g. Festival (2010): Lee Hae-yeong's and Jean-Claude Rousseau's are two films)
    # 2 same concept in two sub-families: (from, to)
    "ft_merge": [
        ("A15-2", "A3-9"),    # Erotic Thriller
        ("A17-5", "A12-35"),  # Family Comedy
        ("A6-9", "A12-28"),   # Fantasy Comedy
        ("A7-6", "A2-5"),     # Hitman Film
        ("A2-20", "A16-25"),  # Legal Drama (film)
        ("A6-8", "A13-23"),   # Romantic Fantasy
        ("A12-29", "A5-22"),  # Science Fiction Comedy
        ("A12-40", "A13-13"), # Sex Comedy
        ("B7-31", "B9-5"),    # Techno-thriller
        ("B10-5", "B1-7"),    # Teen Drama
        ("C9-3", "C1-7"),     # Vampire Anime
        ("A12-36", "A13-20"), # Wedding Comedy
    ],
    # 2 real facet splits: (leaf, new label)
    "ft_rename": [
        ("A12-48", "Buddy Cop Comedy"),
        ("A21-19", "Found-Footage Short"),
        ("A21-18", "Structural Short"),
        ("B2-10", "Korean Legal Drama"),
        ("B2-9", "Korean Medical Drama"),
        ("A8-11", "Historical Political Drama"),
        ("A2-22", "Crime Social Problem Film"),
        ("A8-12", "Historical Social Problem Film"),
    ],
    # 3 rank: section of one leaf that is another leaf of the same family
    # (A2-22's 'Juvenile Delinquency Film' section stays, renamed: moving it would put A16-15 over the 230-title cap)
    "ft_section_to_leaf": [("A3-10", "Vigilante Film", "A7-3")],
    "ft_section_rename": [
        ("A21-15", "Surrealist Film", "Surrealist Shorts"),
        ("A2-22", "Juvenile Delinquency Film", "Juvenile Crime"),
        ("B4-21", "Costume Drama", "TVB Costume Drama"),
        ("C12-19", "Adult Animated Comedy", "Adult Animated Comedy Features"),
        ("A6-12", "Soviet Skazka Films (Ptushko & Rou)", "Soviet Skazka Films"),
    ],
    # 7 small repairs
    "ft_axis": [
        ("A15-5", "by cycle and studio, in order of emergence: the first independent wave, Nikkatsu Roman Porno, the Pink Shitennō and Seven Lucky Gods directors, the Roman Porno reboot"),
        ("B9-17", "by setting and mode: steampunk and gaslamp fantasy first, other historical fantasy after"),
    ],
    "ft_text": [("A13-12", "defn", "A farcical screwball goes to A13-10.", "A farcical screwball goes to A12-4."),
                ("B15-1", "see", "; B15-6 Television Special", "")],
    # A1 movements defined by a genre or form leave A1 (owner, 2026-11-07: "most of these movements are in a certain
    # genre"; measured: 42 of 46 are mostly drama, 4 are not). (leaf, target sub-family, insert after leaf or "first"/"last")
    "ft_move_leaf": [("A1-46", "A18", "first"),    # Golden Age of Hindi Cinema: 96% musical; the forerunner of masala
                     ("A1-40", "A21", "A21-2"),    # Free Cinema: documentary shorts, beside the nonfiction short forms
                     ("A1-45", "A21", "last"),     # Cinema of Transgression: underground shorts, with the avant-garde shorts
                     ("A1-17", "A20", "A20-2")],   # Cinema Marginal: Brazilian underground features, beside Underground Film
    "ft_sub_rename": {"A1": ("Art-Cinema Movements",
        "Axis: by named art-cinema movement or school, in rough order of emergence; Slow Cinema, a transnational style, last. "
        "These movements are mainly drama; a movement defined by another genre or form sits in that sub-family "
        "(popular musical cinema A18, underground features A20, documentary and underground shorts A21).")},
    "ft_precedence": [["F32", "Art-cinema movement before drama genre",
        "A film of a named art-cinema movement (A1) goes to the movement before its drama genre, unless F1 or F2 sends it "
        "to a named cycle. A movement defined by another genre or form is a leaf of that sub-family, not of A1."]],
    # sections by explicit decision where no rule fits: leaf -> (axis, [(section, [titles])], other section)
    "ft_sections": {
        "A12-1": ("by clown, the four great silent clowns first in order of their first feature; other clowns and comedies last",
                  [("Charlie Chaplin", ["The Kid", "The Gold Rush", "The Circus", "City Lights", "Modern Times"]),
                   ("Harold Lloyd", ["Grandma's Boy", "Safety Last!", "Girl Shy", "For Heaven's Sake", "The Kid Brother", "Speedy", "Hot Water", "The Freshman"]),
                   ("Buster Keaton", ["Our Hospitality", "Three Ages", "Sherlock Jr.", "The Navigator", "Seven Chances", "The General",
                                      "Battling Butler", "College", "Steamboat Bill, Jr.", "The Cameraman", "Spite Marriage", "Go West"]),
                   ("Harry Langdon", ["Tramp, Tramp, Tramp", "The Strong Man", "Long Pants", "The Chaser"])],
                  "Other clowns and comedies"),
    },
    "va_text": [("N1-3", "defn", " See also I3-17 Bauhaus.", "")],
    # 8 VA entries in two leaves: drop from (leaf, name) / qualify (leaf, name, new name)
    "va_drop": [
        ("E1-28", "Apulian vase painting"), ("E1-28", "Campanian vase painting"), ("E1-28", "Lucanian vase painting"),
        ("E1-28", "Paestan vase painting"), ("K12-3", "Falekaupule"), ("H4-21", "Four Great Embroideries of China"),
        ("H4-22", "Four Great Embroideries of China"), ("H4-23", "Four Great Embroideries of China"),
        ("D2-13", "Guksi"), ("K14-2", "Hòn non bộ"), ("C4-11", "Katagami"), ("K14-3", "Saikei"),
        ("D3-5", "Stamp seals"), ("C4-5", "Wycinanki"),
    ],
    "va_qualify": [
        ("E1-144", "Black-topped red ware", "Egyptian black-topped red ware"), ("K13-2", "Charbagh", "Mughal charbagh"),
        ("H2-8", "Chuspa", "Taquile chuspa"), ("F2-4", "Glass snuff bottles", "Peking glass snuff bottles"),
        ("L1-4", "Hand stencils", "Maros-Pangkep hand stencils"), ("L1-5", "Hand stencils", "Sangkulirang hand stencils"),
        ("A1-21", "Painted manuscript covers", "Nepalese painted manuscript covers"),
        ("A1-22", "Painted manuscript covers", "Pala painted manuscript covers"),
        ("I2-10", "Raden", "Japanese raden"), ("I2-11", "Raden", "Ryukyuan raden"),
        ("A1-13", "Samut khoi", "Samut khoi painting"), ("D3-13", "Stamp seals", "Sasanian stamp seals"),
        ("K7-11", "Stupa", "Newar stupa"), ("G1-29", "Tupu", "Inca tupu"), ("G3-14", "Tupu", "Mapuche tupu"),
        ("A6-18", "X-ray style", "Arnhem Land bark x-ray style"), ("L1-26", "X-ray style", "Arnhem Land rock x-ray style"),
    ],
}

NATION = {"american": {"US"}, "us": {"US"}, "hollywood": {"US"}, "british": {"GB", "UK"}, "uk": {"GB", "UK"}, "english": {"GB", "UK"},
          "french": {"FR"}, "italian": {"IT"}, "german": {"DE"}, "japanese": {"JP"}, "hong": {"HK"}, "chinese": {"CN", "HK", "TW"},
          "taiwanese": {"TW"}, "korean": {"KR"}, "indian": {"IN"}, "soviet": {"SU", "RU"}, "russian": {"RU", "SU"},
          "mexican": {"MX"}, "spanish": {"ES"}, "european": None}
ERA_BINS = [(-9999, 1899), (1900, 1909), (1910, 1919), (1920, 1929), (1930, 1945), (1946, 1959), (1960, 1969), (1970, 1979),
            (1980, 1989), (1990, 1999), (2000, 2009), (2010, 9999)]


def cname(c):
    try:
        import pycountry  # noqa: F401
    except Exception:
        pass
    NAMES = {"US": "United States", "GB": "United Kingdom", "UK": "United Kingdom", "FR": "France", "IT": "Italy", "DE": "Germany",
             "JP": "Japan", "HK": "Hong Kong", "CN": "China", "TW": "Taiwan", "KR": "South Korea", "IN": "India", "SU": "Soviet Union",
             "RU": "Russia", "MX": "Mexico", "ES": "Spain", "CA": "Canada", "AU": "Australia", "BR": "Brazil", "AR": "Argentina",
             "SE": "Sweden", "DK": "Denmark", "PL": "Poland", "CZ": "Czechoslovakia", "CS": "Czechoslovakia", "IR": "Iran", "PH": "Philippines",
             "TR": "Turkey", "EG": "Egypt", "BE": "Belgium", "NL": "Netherlands", "AT": "Austria", "CH": "Switzerland", "HU": "Hungary",
             "NO": "Norway", "FI": "Finland", "GR": "Greece", "PT": "Portugal", "IE": "Ireland", "NZ": "New Zealand", "TH": "Thailand"}
    return NAMES.get(c, c)


def countries(r):
    return {c for c in str(r[9] or "").split("|") if c}


def bin_label(a, b, first, last):
    if first and a == -9999:
        return f"to {b}" if b < 9999 else "all years"
    if last and b == 9999:
        return f"{a} onward"
    if b - a == 9 and a % 10 == 0:
        return f"{a}s"
    return f"{a}–{b}"


def era_sections(rows):
    ys = [(year(r[1]), r) for r in rows]
    if any(y is None for y, _ in ys):
        return None
    bins = [[a, b, []] for a, b in ERA_BINS]
    for y, r in ys:
        for bn in bins:
            if bn[0] <= y <= bn[1]:
                bn[2].append(r); break
    bins = [bn for bn in bins if bn[2]]
    need = max(8, len(rows) // 8)
    while len(bins) > 1 and (min(len(b[2]) for b in bins) < need or len(bins) > 7):
        i = min(range(len(bins)), key=lambda k: len(bins[k][2]))
        j = i - 1 if i == len(bins) - 1 or (i > 0 and len(bins[i - 1][2]) <= len(bins[i + 1][2])) else i + 1
        a, b = sorted((i, j))
        bins[a] = [bins[a][0], bins[b][1], bins[a][2] + bins[b][2]]; del bins[b]
    if len(bins) < 3 and not (len(bins) == 2 and min(len(b[2]) for b in bins) >= 15):
        return None
    # tighten open ends to the data, then label
    out = []
    for k, (a, b, rs) in enumerate(bins):
        lo = a if a != -9999 else -9999
        out.append((bin_label(lo, b, k == 0, k == len(bins) - 1), rs))
    return out, "by era of release, earliest first"


def group_sections(rows, key, minn, label, other, axis):
    c = collections.Counter(k for r in rows for k in key(r))
    big = [k for k, n in c.most_common() if n >= minn]
    if len(big) < 2:
        return None
    secs = collections.OrderedDict((k, []) for k in big); rest = []
    for r in rows:
        ks = [k for k in key(r) if k in secs]
        (secs[ks[0]] if ks else rest).append(r)
    named = sum(len(v) for v in secs.values())
    if named / len(rows) < 0.5 or len(secs) + (1 if rest else 0) < 2:
        return None
    out = [(label(k), v) for k, v in secs.items()]
    if rest:
        out.append((other, rest))
    return out, axis


def section_leaf(l, rows, fam, sub):
    lab = l["label"]
    def first_dir(d):  # the first credited director: "Buster Keaton; John G. Blystone", "Keaton, Buster & James W. Horne"
        d = re.split(r"\s*(?:;|&|/| and )\s*", d)[0].strip()
        m = re.fullmatch(r"([^,]+),\s*([^,]+)", d)
        return f"{m.group(2)} {m.group(1)}" if m else d
    by_dir = lambda r: [first_dir(r[2])] if r[2] and not re.fullmatch(r"[A-Z]{2}(\|[A-Z]{2})*", r[2]) else []
    dirs = lambda: group_sections(rows, by_dir, 3, lambda k: k, "Other filmmakers",
                                  "by filmmaker, in order of first film in the leaf; other filmmakers last")
    ctry = lambda: group_sections(rows, lambda r: sorted(countries(r)), 5, cname, "Other countries",
                                  "by country of production, largest first; other countries last")
    if sub == "A1":
        order = [dirs, lambda: era_sections(rows), ctry]
    else:
        order = [lambda: era_sections(rows), ctry, dirs]
    for f in order:
        res = f()
        if res:
            secs, axis = res
            if axis.startswith("by filmmaker"):  # order of first film
                head = [s for s in secs if s[0] != "Other filmmakers"]
                head.sort(key=lambda s: min(year(r[1]) or 9999 for r in s[1]))
                secs = head + [s for s in secs if s[0] == "Other filmmakers"]
            return secs, axis
    return None


def sort_rows(rows):
    rows.sort(key=lambda k: (int(k[8]) if str(k[8]).isdigit() else 99, str(k[1])))


def apply(tree, MV, MF, report):
    st = collections.Counter(); log = collections.defaultdict(list)
    ft_leaves = {}
    for f in tree["ft"]["fams"]:
        for s in f["subs"]:
            for l in s["leaves"]:
                ft_leaves[l["code"]] = (f, s, l)
    rows = lambda c: MF.setdefault(ft_leaves[c][0]["code"], {}).setdefault(c, [])

    def secs_of(c):
        return ft_leaves[c][2].setdefault("secs", []) if ft_leaves[c][2].get("secs") else []

    # 10 country codes, 11 shared ids (before anything that reads them)
    import json as _json
    CC = _json.load(open(os.path.join(R3, "country_codes.json")))
    def norm_c(v):
        out = []
        for x in str(v or "").split("|"):
            if not x: continue
            if re.fullmatch(r"[A-Z]{2}", x): out.append("GB" if x == "UK" else x); continue
            if x in CC: out += [c for c in CC[x].split("|") if c]; continue
            parts = re.split(r"-(?!Herzegovina|Bissau|Leste)", x)
            if all(p in CC for p in parts): out += [c for p in parts for c in CC[p].split("|") if c]
            else: out.append(x); st["country_unmapped"] += 1
        return "|".join(dict.fromkeys(out))
    seen = {}
    names = lambda d: {w for w in fold(d).split() if len(w) > 2}
    slug = lambda x: re.sub(r"[^a-z0-9]+", "-", fold(x)).strip("-")[:40] or "x"
    for c in ft_leaves:
        keep = []
        for r in rows(c):
            nv = norm_c(r[9])
            if nv != r[9]: r[9] = nv; st["country_normalised"] += 1
            if r[5] in seen and str(r[5]).startswith("tspdt:"):
                t0, d0, c0 = seen[r[5]]
                if fold(r[0]) == t0 and (names(r[2]) & d0 or not d0):
                    if c0 == c: st["duplicate_rows_dropped"] += 1; continue  # the same film listed twice in one leaf
                elif fold(r[0]) != t0:
                    r[5] = r[5] + "-" + re.sub(r"[^a-z0-9]+", "-", fold(r[0])).strip("-")[-24:].strip("-"); st["ids_split"] += 1
                else:
                    r[5] = r[5] + "-" + slug(r[2]); st["ids_split"] += 1
            else:
                seen[r[5]] = (fold(r[0]), names(r[2]), c)
            keep.append(r)
        MF[ft_leaves[c][0]["code"]][c] = keep
    # A1 redistribution: move leaves between sub-families (new code in the target; old code mapped)
    moved_codes = {}
    subs_by = {s_["code"]: (f, s_) for f in tree["ft"]["fams"] for s_ in f["subs"]}
    for c, to, where in DECISIONS["ft_move_leaf"]:
        if c not in ft_leaves or to not in subs_by: continue
        f0, s0, l = ft_leaves[c]; f1, s1 = subs_by[to]
        nc = f"{to}-{max(int(x['code'].split('-')[1]) for x in s1['leaves']) + 1}"
        s0["leaves"].remove(l)
        pos = 0 if where == "first" else len(s1["leaves"]) if where == "last" else \
            next((i + 1 for i, x in enumerate(s1["leaves"]) if x["code"] == where), len(s1["leaves"]))
        s1["leaves"].insert(pos, l)
        MF[f1["code"]][nc] = MF[f0["code"]].pop(c); l["code"] = nc
        del ft_leaves[c]; ft_leaves[nc] = (f1, s1, l); moved_codes[c] = nc
        st["leaves_moved"] += 1; log["moved"].append(f"{c} {l['label']} → {nc} ({s1['label']})")
    for sc, (lab, axis) in DECISIONS["ft_sub_rename"].items():
        if sc in subs_by:
            f, s_ = subs_by[sc]; old_lab = s_["label"]; s_["label"] = lab; s_["axis"] = axis
            f["key"] = [k.replace(f"<b>{sc} {old_lab}</b>", f"<b>{sc} {lab}</b>").split(" — ")[0] + " — " + axis.replace("Axis: ", "")
                        if k.startswith(f"<b>{sc} ") else k for k in f["key"]]
    have = {p[0] for p in tree["ft"].get("precedence", [])}
    for p in DECISIONS["ft_precedence"]:
        if p[0] not in have: tree["ft"].setdefault("precedence", []).append(p)
    if moved_codes:
        rxm = re.compile(r"\b(" + "|".join(re.escape(k) for k in moved_codes) + r")\b")
        for c, (f, s_, l) in ft_leaves.items():
            for fld in ("defn", "see"):
                if l.get(fld) and rxm.search(l[fld]): l[fld] = rxm.sub(lambda m: moved_codes[m.group(1)], l[fld])
        for fam in MF.values():  # finder rows and see-also columns of titles
            for rs_ in fam.values():
                for r in rs_:
                    if r[3] and rxm.search(str(r[3])): r[3] = rxm.sub(lambda m: moved_codes[m.group(1)], str(r[3]))
    # 1 one home
    for tid, c, why in DECISIONS["ft_remove"]:
        if c in ft_leaves:
            n0 = len(rows(c)); MF[ft_leaves[c][0]["code"]][c] = [r for r in rows(c) if r[5] != tid]
            if len(rows(c)) < n0: st["two_homes_resolved"] += 1; log["one home"].append(why)
    for old, c, new, why in DECISIONS["ft_reid"]:
        for r in rows(c):
            if r[5] == old: r[5] = new; st["ids_split"] += 1; log["one home"].append(why)
    # 2 merges and renames
    merged = {}; came_from = {}
    for frm, to in DECISIONS["ft_merge"]:
        if frm not in ft_leaves or to not in ft_leaves: continue
        moved = rows(frm)
        have = {r[5] for r in rows(to)}
        f0, s0, l0 = ft_leaves[frm]
        for r in moved:
            if r[5] in have: continue
            r = list(r); r[8] = ""; rows(to).append(r); came_from[r[5]] = s0["label"]
        l1 = ft_leaves[to][2]
        if l0.get("aliases"):
            l1["aliases"] = "; ".join(dict.fromkeys([a for a in (l1.get("aliases") or "").split("; ") if a] + l0["aliases"].split("; ")))
        s0["leaves"].remove(l0); MF[f0["code"]].pop(frm, None); del ft_leaves[frm]
        merged[frm] = to; st["leaves_merged"] += 1; log["merged"].append(f"{frm} → {to} {l1['label']} ({len(moved)} titles)")
    for c, new in DECISIONS["ft_rename"]:
        if c in ft_leaves:
            log["renamed"].append(f"{c} {ft_leaves[c][2]['label']} → {new}"); ft_leaves[c][2]["label"] = new; st["leaves_renamed"] += 1
    # 3 rank
    for c, sec, to in DECISIONS["ft_section_to_leaf"]:
        l = ft_leaves[c][2]; ss = l.get("secs") or []
        if sec not in ss: continue
        i = ss.index(sec) + 1
        go = [r for r in rows(c) if str(r[8]) == str(i)]
        keep = [r for r in rows(c) if str(r[8]) != str(i)]
        have = {r[5] for r in rows(to)}
        for r in go:
            if r[5] not in have: r = list(r); r[8] = ""; rows(to).append(r)
        for r in keep:  # renumber the remaining sections
            if str(r[8]).isdigit() and int(r[8]) > i: r[8] = str(int(r[8]) - 1)
        ss.pop(i - 1); MF[ft_leaves[c][0]["code"]][c] = keep
        st["sections_to_leaf"] += 1; log["rank"].append(f"{c} section '{sec}' ({len(go)} titles) → leaf {to}")
    for c, old, new in DECISIONS["ft_section_rename"]:
        ss = ft_leaves[c][2].get("secs") or [] if c in ft_leaves else []
        if old in ss: ss[ss.index(old)] = new; st["sections_renamed"] += 1; log["rank"].append(f"{c} section '{old}' → '{new}'")
    # 7 small repairs
    for c, axis in DECISIONS["ft_axis"]:
        if c in ft_leaves and not (ft_leaves[c][2].get("axis") or "").strip(): ft_leaves[c][2]["axis"] = axis; st["axes_written"] += 1
    for c, field, old, new in DECISIONS["ft_text"]:
        if c in ft_leaves and old in (ft_leaves[c][2].get(field) or ""):
            ft_leaves[c][2][field] = ft_leaves[c][2][field].replace(old, new); st["text_fixed"] += 1
    for c, (f, s, l) in ft_leaves.items():
        ss = l.get("secs") or []
        if not ss: continue
        used = {int(r[8]) for r in rows(c) if str(r[8]).isdigit()}
        empty = [i for i in range(1, len(ss) + 1) if i not in used]
        if empty:
            remap = {}; k = 0
            for i in range(1, len(ss) + 1):
                if i in used: k += 1; remap[i] = k
            for r in rows(c):
                if str(r[8]).isdigit() and int(r[8]) in remap: r[8] = str(remap[int(r[8])])
            l["secs"] = [x for i, x in enumerate(ss, 1) if i in used]
            st["empty_sections_dropped"] += len(empty)
    for c, (axis, groups, other) in DECISIONS["ft_sections"].items():
        if c not in ft_leaves or ft_leaves[c][2].get("secs"): continue
        l = ft_leaves[c][2]; secs = [g for g, _ in groups] + [other]
        idx = {fold(t): i for i, (_, ts) in enumerate(groups, 1) for t in ts}
        for r in rows(c): r[8] = str(idx.get(fold(r[0]), len(secs)))
        l["secs"] = secs; l["axis"] = axis; st["leaves_sectioned"] += 1
        log["sectioned"].append(f"{c} {l['label']}: by decision ({len(secs)} sections)")
    # 4 section large unsectioned leaves
    for c, (f, s, l) in ft_leaves.items():
        rs = rows(c)
        if l.get("secs") or len(rs) <= 40: continue
        res = section_leaf(l, rs, f["code"], s["code"])
        if not res: log["not sectioned"].append(f"{c} {l['label']}"); continue
        secs, axis = res
        l["secs"] = [x for x, _ in secs]; l["axis"] = axis
        for i, (_, g) in enumerate(secs, 1):
            for r in g: r[8] = str(i)
        st["leaves_sectioned"] += 1; log["sectioned"].append(f"{c} {l['label']}: {axis.split(',')[0]} ({len(secs)} sections)")
    # 5 and 6 loose titles and date misfits
    for c, (f, s, l) in ft_leaves.items():
        ss = l.get("secs") or []
        if not ss: continue
        rs = rows(c)
        setting = re.search(r"period|historical|history|war\b|epic|setting|set in", (l["label"] + " " + (l.get("axis") or "")).lower())
        rng = [era_range(x) for x in ss]
        dated = sum(1 for r in rng if r) >= max(2, len(ss) // 2) and not setting
        nat = [None] * len(ss)
        for i, x in enumerate(ss):
            for w in fold(x).split():
                if w in NATION and NATION[w]: nat[i] = NATION[w]; break
        bydir = collections.defaultdict(collections.Counter)
        for r in rs:
            if str(r[8]).isdigit() and r[2]: bydir[r[2]][int(r[8])] += 1
        def fits(r):
            y = year(r[1])
            return [i for i, g in enumerate(rng) if g and y is not None and g[0] <= y <= g[1] and (nat[i] is None or countries(r) & nat[i])]
        loose = [r for r in rs if not (str(r[8]).isdigit() and 0 < int(r[8]) <= len(ss))]
        other = None
        for r in loose:
            d = bydir.get(r[2])
            if d:
                r[8] = str(d.most_common(1)[0][0]); st["loose_by_director"] += 1; continue
            if dated:
                cand = fits(r)
                if len(cand) == 1: r[8] = str(cand[0] + 1); st["loose_by_date"] += 1; continue
            cand = [i for i, n in enumerate(nat) if n and countries(r) & n]
            if len(cand) == 1: r[8] = str(cand[0] + 1); st["loose_by_country"] += 1; continue
            if r[5] in came_from:  # titles merged in from a sibling leaf keep that leaf's angle as a section
                lab = came_from[r[5]]
                if lab not in ss: ss.append(lab)
                r[8] = str(ss.index(lab) + 1); st["merged_titles_sectioned"] += 1; continue
            if other is None:
                ax = (l.get("axis") or "").lower()
                other = ("Other filmmakers" if re.search(r"filmmaker|director|auteur", ax) else
                         "Other countries" if re.search(r"countr|national", ax) else f"Other {l['label']}")
                other = next((x for x in ss if x.lower() == other.lower()), other)
                if other not in ss: ss.append(other)
            r[8] = str(ss.index(other) + 1); st["loose_to_other"] += 1
        # created sections ("Other ...", merged-in sub-family) that end with 1–2 titles: those titles join the section
        # nearest them, by shared country first, then by distance from the section's median year
        made = [x for x in ss if x == other or x in set(came_from.get(r[5]) for r in rs if r[5] in came_from)]
        for x in made:
            i = ss.index(x) + 1
            few = [r for r in rs if str(r[8]) == str(i)]
            if 0 < len(few) <= 2 and len(ss) > 1:
                for r in few:
                    best = None
                    for j in range(1, len(ss) + 1):
                        if j == i: continue
                        mem = [q for q in rs if str(q[8]) == str(j)]
                        if not mem: continue
                        share = sum(1 for q in mem if countries(q) & countries(r)) / len(mem)
                        ys = sorted(year(q[1]) for q in mem if year(q[1]) is not None)
                        dist = abs((ys[len(ys) // 2] if ys else 0) - (year(r[1]) or 0))
                        key = (-share, dist)
                        if best is None or key < best[0]: best = (key, j)
                    if best: r[8] = str(best[1]); st["small_created_sections_folded"] += 1
        used = {int(r[8]) for r in rs if str(r[8]).isdigit()}
        if any(i not in used for i in range(1, len(ss) + 1)):
            remap = {}; k = 0
            for i in range(1, len(ss) + 1):
                if i in used: k += 1; remap[i] = k
            for r in rs:
                if str(r[8]).isdigit() and int(r[8]) in remap: r[8] = str(remap[int(r[8])])
            l["secs"] = ss = [x for i, x in enumerate(ss, 1) if i in used]
            rng = [era_range(x) for x in ss]
        if dated:  # 6 date misfits in pure date bands
            for r in rs:
                i = int(r[8]) - 1 if str(r[8]).isdigit() else None
                if i is None or i >= len(rng) or not rng[i]: continue
                y = year(r[1]); g = rng[i]
                if y is None or g[0] <= y <= g[1]: continue
                cand = fits(r)
                if len(cand) == 1: r[8] = str(cand[0] + 1); st["date_misfits_moved"] += 1
        sort_rows(rs)
    for c, (f, s, l) in ft_leaves.items():
        sort_rows(rows(c)); l["n"] = len(rows(c))
    for f in tree["ft"]["fams"]:
        for s in f["subs"]:
            s["n"] = sum(l["n"] for l in s["leaves"])
        f["nleaves"] = sum(len(s["leaves"]) for s in f["subs"]); f["n"] = sum(s["n"] for s in f["subs"])
    c = tree.get("census", {}).get("ft")
    if c is not None:
        c["leaves"] = len(ft_leaves); c["placed"] = sum(len(rows(x)) for x in ft_leaves)
    # migration: merged codes point at their new home
    mp = os.path.join(R3, "ft_migration.csv")
    if (merged or moved_codes) and os.path.exists(mp):
        rr = list(csv.DictReader(open(mp)))
        for r in rr:
            if r["new_code"] in moved_codes:
                r["new_code"] = moved_codes[r["new_code"]]
            if r["new_code"] in merged:
                to = merged[r["new_code"]]; r["new_code"] = to; r["new_label"] = ft_leaves[to][2]["label"]
        with open(mp, "w", newline="") as fo:
            w = csv.DictWriter(fo, fieldnames=list(rr[0].keys())); w.writeheader(); w.writerows(rr)
    if merged:  # definitions and see fields that name a merged code name its new home
        rx = re.compile(r"\b(" + "|".join(re.escape(k) for k in merged) + r")\b")
        for c, (f, s_, l) in ft_leaves.items():
            for fld in ("defn", "see"):
                if l.get(fld) and rx.search(l[fld]):
                    l[fld] = rx.sub(lambda m: merged[m.group(1)], l[fld]); st["merged_codes_in_text"] += 1
    for f in tree["va"]["fams"]:
        for s_ in f["subs"]:
            for l in s_["leaves"]:
                for c, fld, old, new in DECISIONS["va_text"]:
                    if l["code"] == c and old in (l.get(fld) or ""): l[fld] = l[fld].replace(old, new); st["text_fixed"] += 1
    # 8 VA entries
    for c, name in DECISIONS["va_drop"]:
        if c in MV:
            n0 = len(MV[c]); MV[c] = [r for r in MV[c] if fold(r[0]) != fold(name)]
            st["va_entries_dropped"] += n0 - len(MV[c])
    for c, name, new in DECISIONS["va_qualify"]:
        for r in MV.get(c, []):
            if fold(r[0]) == fold(name): r[0] = new; st["va_entries_qualified"] += 1
    SEARCH = "https://en.wikipedia.org/w/index.php?search="
    NOSRC = {"E2-13": "Qallaline tiles", "I1-5": "Islamic woodwork", "I2-3": "Edirnekari lacquer", "K1-19": "Javanese mosque architecture"}
    for f in tree["va"]["fams"]:
        for s in f["subs"]:
            for l in s["leaves"]:
                if l["code"] in MV:
                    l["n"] = len(MV[l["code"]])
                    have = {r[1] for r in MV[l["code"]]}
                    secs = l.get("secs")
                    if isinstance(secs, list) and any(x not in have for x in secs):  # sections emptied by the drops above
                        l["secs"] = [x for x in secs if x in have]; st["va_empty_sections_dropped"] += 1
                if not l.get("src") and l["code"] in NOSRC:  # never sourced: a Wikipedia search, the pipeline's fallback
                    l["src"] = [[SEARCH + NOSRC[l["code"]].replace(" ", "+"), "Wikipedia search"]]; st["va_sources_added"] += 1
            s["n"] = sum(int(l.get("n") or 0) for l in s["leaves"])
        f["n"] = sum(s["n"] for s in f["subs"])
    # peoples and cultures from the AAT crosswalk (ref_crosswalk.py): the tree holds their work in these leaves
    pp = os.path.join(R3, "va_peoples.csv")
    if os.path.exists(pp):
        for r in csv.DictReader(open(pp)):
            rows_ = MV.get(r["leaf"])
            if rows_ is None or any(fold(x[0]) == fold(r["name"]) for x in rows_): continue
            how = r.get("how") or "held"
            nobj = int(r["objects"] or 0)
            # a style, school or ware placed from its Getty scope note (no gathered records) is not a people
            grp = "Peoples & cultures" if (nobj or how != "decided") else "Schools & phases"
            note = (f"grouped by Getty AAT under {r['aat_group']}" if how == "inherited" else
                    f"Getty AAT, under {r['aat_group']}" if not nobj else
                    f"{nobj:,} objects in the gathered records" + (f"; Getty AAT: {r['aat_group']}" if r.get("aat_group") else ""))
            rows_.append([r["name"], grp, note,
                          "r3 http://vocab.getty.edu/page/aat/" + r["aat_id"], 0])
            st["va_peoples_added"] += 1
        for f in tree["va"]["fams"]:
            for s_ in f["subs"]:
                for l in s_["leaves"]:
                    rs_ = MV.get(l["code"], [])
                    for g_ in ("Schools & phases", "Peoples & cultures"):
                        if any(x[1] == g_ for x in rs_) and isinstance(l.get("secs"), list) and l["secs"] and g_ not in l["secs"]:
                            l["secs"].append(g_)
                    l["n"] = len(rs_)
                s_["n"] = sum(int(l.get("n") or 0) for l in s_["leaves"])
            f["n"] = sum(s_["n"] for s_ in f["subs"])
    cv = tree.get("census", {}).get("va")
    if cv is not None: cv["kinds"] = sum(len(v) for v in MV.values())
    # 9 see references, both tabs
    for tab, M in (("va", MV), ("ft", None)):
        lv = [l for f in tree[tab]["fams"] for s in f["subs"] for l in s["leaves"]]
        bycode = {l["code"]: l for l in lv}
        subs = {s["code"]: s for f in tree[tab]["fams"] for s in f["subs"]}
        bylab = collections.defaultdict(list)
        for l in lv: bylab[fold(l["label"])].append(l["code"])
        kinds = collections.defaultdict(list)
        if M is not None:
            for c, rs in M.items():
                for r in rs:
                    if not r[4]: kinds[fold(r[0])].append(c)
        for l in lv:
            see = l.get("see") or ""
            if not see: continue
            head, sep, tail = see.partition(". Possession taxonomy")
            parts = [p.strip() for p in re.split(r"\s*[;,]\s*", head.rstrip(". ")) if p.strip()]
            out = []
            for p in parts:
                p = re.sub(r"^[a-z]+(?:_[a-z]+)+[: ]\s*", "", p)            # pass-name prefix
                p = re.sub(r"\s*\((?:[a-z]+(?:_[a-z]+)+|artist)\)\s*$", "", p)  # pass-name suffix
                m = re.match(r"^([A-NT]\d{1,3}(?:-\d{1,3})?)\s*(.*)$", p)
                if not m: out.append(p); continue
                code, lab = m.group(1), m.group(2).strip()
                if not lab:
                    if code in bycode or code in subs or code in merged: out.append(merged.get(code, code))
                    else: st["see_dropped"] += 1
                    continue
                cur = bycode.get(code) or subs.get(code)
                if cur and (fold(cur["label"]) == fold(lab) or fold(cur["label"]).startswith(fold(lab)) or fold(lab).startswith(fold(cur["label"]))):
                    out.append(f"{code} {lab}"); continue
                hits = [c for c in bylab.get(fold(lab), []) if c != l["code"]]
                if len(hits) == 1:
                    out.append(f"{hits[0]} {lab}"); st["see_relinked"] += 1; continue
                kh = [c for c in kinds.get(fold(lab), []) if c != l["code"]]
                if len(set(kh)) == 1:
                    out.append(f"{lab} (in {kh[0]} {bycode[kh[0]]['label']})"); st["see_to_entry"] += 1; continue
                out.append(lab); st["see_code_dropped"] += 1
            new = "; ".join(dict.fromkeys(out)) + (sep + tail if sep else "")
            if new != see: l["see"] = new
    report["structure_fix"] = dict(st)
    report["structure_fix_codes"] = {**merged, **moved_codes}
    report["structure_fix_log"] = {k: v for k, v in log.items()}
