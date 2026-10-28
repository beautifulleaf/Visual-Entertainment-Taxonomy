"""Place every selected Visual Art artist on one artist-led leaf (or exclude a non-artist).

Inputs
  taxonomy/visual_art/artists.csv                      31,551 selected artists
  data/interim/visual_art/pool_*.csv, refextra_pool_*.csv  `countries` (Wikidata P27) per qid
  data/interim/contemporary_pool.csv (+ _additions)    P27 for contemporary-only artists absent
                                                       from the visual_art pools
  taxonomy/visual_art/review/artist_leaves.csv         leaves T1… (sub-family per leaf)
  taxonomy/visual_art/review/movement_map.csv          P135 movement → leaf / kind / tag / exclude
  taxonomy/visual_art/review/period_rules.csv          medium × region × country × birth → leaf
                                                       (first match wins)
  taxonomy/visual_art/review/*_leaves.csv              region-slice leaves (`<slice>:L<n>`)
  pipelines/classify/tree_visual_art.py                pilot leaves (A1-3, C1-4 …)

Order of placement (column `rule`)
  1. exclude:<reason>      non-artists (EXCLUDE: scientists, writers, film directors … whose
                           visual-art occupation share is marginal; reviewed by hand)
  2. evidence:<source>     per-artist evidence tables below (EVIDENCE): attested community
                           tradition for Aboriginal artists, members named in a leaf's
                           attesting article (Dansaekhwa), a few Japanese/Korean premodern
                           masters.
  3. movement:<qid>        the artist's own P135 movement mapped to a leaf (or a kind = group
                           under a leaf) whose sub-family fits the artist's medium. Among
                           several, the most specific (fewest artists) wins.
  4. jp:<evidence>         Japanese painters/printmakers with no movement: Wikidata occupation
                           (ukiyo-e artist, Nihonga painter, P106), then teacher (P1066) whose
                           school is known (TEACHER_SCHOOL, fetched from Wikidata 2026-10-28),
                           then an art-name school prefix (Kanō, Utagawa, Tosa …, before 1868).
  5. period:<row>          period_rules.csv, first matching row (row = line number in the file).

Confidence: high = own movement or named in the leaf's attesting source; medium = country rule,
teacher/occupation, hand evidence or a medium-crossing movement; low = generic medium × birth band
or era fallback.

    python3 pipelines/classify/va_place_artists.py

Writes taxonomy/visual_art/artist_placements.csv:
qid,label,birth,medium,region,countries,leaf,kind,movement_tags,rule,confidence,note
"""
import csv
import glob
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
VA = os.path.join(ROOT, "taxonomy", "visual_art")
REV = os.path.join(VA, "review")
INT = os.path.join(ROOT, "data", "interim")
sys.path.insert(0, HERE)

PAINT = {"painting", "visual art (unspecified)", ""}
# movement leaves that define their own medium: an artist recorded under another medium still goes there
CROSS = {"T150", "T151", "T152"}

# medium -> sub-families a movement leaf may have for an artist of that medium
COMPAT = {
    "painting": ("A",),
    "visual art (unspecified)": None,  # any
    "": None,
    "sculpture": ("D",),
    "photography": ("J1",),
    "drawing and illustration": ("B1", "B2"),
    "printmaking": ("B2", "B1"),
    "book arts": ("C", "A1"),
    "vase painting": ("E1",),
    "design and decorative arts": ("I", "G", "H", "E", "F"),
    "architecture": ("K",),
    "installation, performance and conceptual": ("M", "D5"),
    "video, new media and digital": ("M",),
    "street art and muralism": ("L2", "A5"),
}

# --- non-artists (reviewed: art_occ_share <= 0.15 in the gathering pools, plus two East Asia rows)
EXCLUDE = {
    "Q184366": "biologist", "Q191026": "scientist", "Q229264": "naturalist", "Q231360": "traveller and archaeologist",
    "Q504": "novelist", "Q5816": "politician", "Q264918": "writer", "Q298581": "astronomer", "Q46096": "composer",
    "Q6711": "poet", "Q5879": "poet", "Q23810": "chemist and industrialist", "Q9095": "physicist", "Q529": "scientist",
    "Q72292": "explorer", "Q131761": "chemist", "Q93996": "physicist", "Q59945": "art historian", "Q182847": "philosopher",
    "Q20710": "neurologist", "Q310192": "general and politician", "Q318840": "composer", "Q350420": "explorer",
    "Q464879": "spiritual teacher", "Q234530": "novelist", "Q154759": "explorer", "Q158765": "patron of archaeology",
    "Q298766": "industrialist", "Q45661": "fashion designer (Possession taxonomy)", "Q275785": "patron",
    "Q677769": "sociologist", "Q203623": "writer", "Q767": "poet", "Q501": "poet", "Q336467": "poet",
    "Q133855": "poet", "Q183167": "writer", "Q37327": "writer", "Q515845": "writer", "Q919277": "writer",
    "Q1444002": "writer", "Q2579425": "writer", "Q126596": "essayist", "Q194363": "dancer", "Q318364": "choreographer",
    "Q2061698": "actress and poet", "Q462604": "writer", "Q288210": "traveller", "Q437356": "writer and Egyptologist",
    "Q772064": "colonial administrator", "Q319962": "politician and astronomer", "Q721000": "geographer",
    "Q731829": "orientalist", "Q717391": "colonial administrator", "Q2959074": "journalist", "Q381848": "town planner",
    "Q696704": "diplomat", "Q311115": "physicist", "Q472490": "scientist", "Q51545": "film director (film tab)",
    "Q7371": "film director (film tab)", "Q295855": "film director (film tab)", "Q263148": "film director (film tab)",
    "Q60637": "film director (film tab)", "Q72685": "film director (film tab)", "Q1390108": "film director (film tab)",
    "Q474262": "film director (film tab)", "Q1962284": "film pioneer (film tab)", "Q61654": "film pioneer (film tab)",
    "Q465350": "film pioneer (film tab)", "Q703759": "animator (film tab)", "Q339892": "musician", "Q212632": "poet",
    "Q150526": "neuroscientist", "Q2355375": "poet", "Q3306241": "poet", "Q150471": "writer and composer",
    "Q2004984": "surgeon", "Q157100": "patron and regent", "Q451727": "anatomist", "Q3087508": "writer", "Q1046410": "martial artist", "Q33772": "poet",
}

# --- per-artist evidence: qid -> (leaf, kind, source, confidence, note)
WD = "Wikidata description/P172, 2026-10-28"
EVIDENCE = {
    # Aboriginal and Torres Strait Islander artists with a community tradition (oceania_australia slice)
    "Q440221": ("oceania_australia:L1", "Papunya Tula Artists", "aboriginal", "high", f"Papunya; {WD}"),
    "Q1928724": ("oceania_australia:L1", "Papunya Tula Artists", "aboriginal", "high", "Papunya painter (Five Dreamings)"),
    "Q3361222": ("oceania_australia:L1", "Papunya Tula Artists", "aboriginal", "high", f"Kintore (Walungurru); {WD}"),
    "Q3569414": ("oceania_australia:L1", "Papunya Tula Artists", "aboriginal", "high", f"Pintupi, Kintore; {WD}"),
    "Q132923980": ("oceania_australia:L1", "Papunya Tula Artists", "aboriginal", "medium", "Pintupi painter of Papunya Tula"),
    "Q1352939": ("oceania_australia:L1", "Warlayirti Artists (Balgo)", "aboriginal", "medium", "Balgo (Wirrimanu) painter"),
    "Q21455188": ("oceania_australia:L1", "Warlukurlangu Artists (Yuendumu)", "aboriginal", "medium", f"Warlpiri painter; {WD}"),
    "Q113541025": ("oceania_australia:L1", "Mimili Maku Arts (APY Lands)", "aboriginal", "medium", f"APY Lands, Mimili; {WD}"),
    "Q453890": ("oceania_australia:L2", "Utopia (Urapuntja)", "aboriginal", "medium", f"Utopia, Northern Territory; {WD}; Utopia is Anmatyerre/Alyawarre country east of the Western Desert"),
    "Q1736286": ("oceania_australia:L2", "Utopia (Urapuntja)", "aboriginal", "medium", "Utopia painter (Petyarre sisters)"),
    "Q5571443": ("oceania_australia:L2", "Utopia (Urapuntja)", "aboriginal", "medium", f"Utopia; {WD}"),
    "Q777909": ("oceania_australia:L2", "Warmun Art Centre", "aboriginal", "high", "Warmun (Turkey Creek), East Kimberley"),
    "Q168302": ("oceania_australia:L2", "Warmun Art Centre", "aboriginal", "high", f"Warmun, East Kimberley; {WD}"),
    "Q17318490": ("oceania_australia:L2", "Warmun Art Centre", "aboriginal", "high", "Warmun, East Kimberley"),
    "Q27924655": ("oceania_australia:L2", "Warmun Art Centre", "aboriginal", "high", "Warmun, East Kimberley"),
    "Q24735218": ("oceania_australia:L2", "Mornington Island Art", "aboriginal", "high", f"Kaiadilt (P172), Bentinck/Mornington Island; {WD}"),
    "Q89697567": ("oceania_australia:L2", "Iwantja Arts (Indulkana)", "aboriginal", "medium", "Arrernte (P172); Iwantja Arts, APY Lands"),
    "Q951510": ("oceania_australia:L2", "", "aboriginal", "low", "Wurundjeri leader whose 19th-century ceremony drawings are held as art; no colonial-era leaf exists (see problems)"),
    "Q560086": ("oceania_australia:L3", "", "aboriginal", "high", "Arrernte (P172), Hermannsburg; founder of the Hermannsburg School"),
    "Q125253027": ("oceania_australia:L4", "Buku-Larrnggay Mulka Centre (Yirrkala)", "aboriginal", "high", f"Yirrkala; {WD}"),
    "Q5617919": ("oceania_australia:L4", "Buku-Larrnggay Mulka Centre (Yirrkala)", "aboriginal", "high", "Yirrkala bark and larrakitj painter"),
    "Q50376679": ("oceania_australia:L4", "Buku-Larrnggay Mulka Centre (Yirrkala)", "aboriginal", "high", "Yirrkala bark painter"),
    "Q1175462": ("oceania_australia:L4", "Bula'bula Arts (Ramingining)", "aboriginal", "high", "Ramingining bark painter, Central Arnhem Land"),
    # Dansaekhwa: members named in the attesting enwiki article
    "Q4984536": ("T205", "", "wiki:Dansaekhwa", "high", "named in the Dansaekhwa article"),
    "Q73668649": ("T205", "", "wiki:Dansaekhwa", "high", "named in the Dansaekhwa article"),
    "Q20630837": ("T205", "", "wiki:Dansaekhwa", "high", "named in the Dansaekhwa article"),
    "Q51593288": ("T205", "", "wiki:Dansaekhwa", "high", "named in the Dansaekhwa article"),
    "Q23068024": ("T205", "", "wiki:Dansaekhwa", "high", "named in the Dansaekhwa article"),
    "Q399775": ("T205", "", "wiki:Dansaekhwa", "high", "named in the Dansaekhwa article; also Mono-ha (see T193 kind)"),
    "Q6409518": ("T205", "", "wiki:Dansaekhwa", "medium", "named in the Dansaekhwa article"),
    # Japanese painters: school from the standard biographies (art-historian review, 2026-10-28)
    "Q11365580": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q11388657": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q11418113": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q11459874": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q11465868": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q11469444": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q11473962": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q11528565": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q11533148": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q11568738": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q11619283": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q11656069": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q11664624": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q1290786": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q1750511": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q18280945": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q3128069": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q3128077": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q3572680": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q544404": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q735978": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q74674": ("T110", "", "hand", "medium", "Western-style (Yōga) training"),
    "Q11388955": ("T13", "", "hand", "medium", "Nihonga painter"),
    "Q11395169": ("T13", "", "hand", "medium", "Nihonga painter"),
    "Q11531485": ("T13", "", "hand", "medium", "Nihonga painter"),
    "Q11619739": ("T13", "", "hand", "medium", "Nihonga painter"),
    "Q11645939": ("T13", "", "hand", "medium", "Nihonga painter"),
    "Q1624222": ("T13", "", "hand", "medium", "Nihonga painter"),
    "Q7674339": ("T13", "", "hand", "medium", "Nihonga painter"),
    "Q6358490": ("T10", "", "hand", "high", "Kamisaka Sekka, the last major Rinpa designer-painter"),
    "Q11395355": ("T8", "Fukko Yamato-e", "hand", "medium", "Fukko Yamato-e (Yamato-e revival) painter"),
    "Q3514212": ("T8", "", "hand", "high", "court painter of the Kasuga Gongen Genki emaki"),
    "Q3192800": ("T204", "", "hand", "high", "early Zen ink painter (Kaō Ninga)"),
    "Q1324419": ("T9", "", "hand", "medium", "trained in the Kanō school before turning to photography"),
    "Q20040829": ("T12", "", "hand", "medium", "Shijō-school painter"),
    "Q3146355": ("T12", "", "hand", "medium", "Shijō-school painter (Nishiyama Hōen)"),
    "Q3121142": ("T127", "", "hand", "high", "ukiyo-e (kōsen-ga) print designer"),
    # premodern East Asian sculptors outside Kei
    "Q1446925": ("T22", "Umbrian school", "hand", "high", "Umbrian painter (Giovanni di Pietro, called Lo Spagna), pupil of Perugino"),
    "Q2027523": ("T142", "", "hand", "high", "Valencian/Aragonese sculptor of retables; recorded medium is painting"),
    "Q3331432": ("east_asia:L21", "En school", "hand", "high", "En-school busshi (Myōen), not Kei"),
    "Q847250": ("east_asia:L20", "", "hand", "high", "Silla minister credited with Seokguram and Bulguksa"),
    "Q17214954": ("east_asia:L19", "", "hand", "medium", "Song Chinese caster who recast the Tōdai-ji Great Buddha"),
}
# Urban Aboriginal artists: no community tradition -> medium's contemporary period leaf (note only)
URBAN_ABORIGINAL = {"Q1225061", "Q1724725", "Q1284772", "Q4974307", "Q19872801", "Q1825603", "Q118359711",
                    "Q87281233", "Q21682595", "Q63313371", "Q5585307", "Q2116507", "Q64617506", "Q86666005"}

# --- Japanese painters: school of a recorded teacher (P1066 fetched from Wikidata 2026-10-28)
TEACHER_SCHOOL = {
    "Q317736": "T127", "Q3121142": "T127", "Q467337": "T127", "Q3087294": "T127", "Q3154222": "T127",
    "Q11400282": "T127", "Q1358636": "T127", "Q3075025": "T127",                                   # ukiyo-e
    "Q11479106": "T13", "Q3514329": "T13", "Q11627892": "T13", "Q3128092": "T13", "Q11459528": "T13",
    "Q700019": "T13", "Q6563405": "T13", "Q27195853": "T13", "Q11365548": "T13", "Q11465396": "T13",  # Nihonga
    "Q20040829": "T12", "Q3201302": "T12", "Q3122703": "T12", "Q26254229": "T12", "Q18011598": "T12",
    "Q11645615": "T12",                                                                              # Maruyama–Shijō
    "Q11509541": "T11", "Q1358543": "T11", "Q3541614": "T11", "Q11434757": "T11", "Q11383402": "T11",
    "Q11552479": "T11", "Q11576703": "T11", "Q11531144": "T11",                                     # Nanga
    "Q11571474": "T9", "Q3192789": "T9",                                                             # Kanō
    "Q11459900": "T110", "Q347220": "T110", "Q11478804": "T110", "Q720550": "T110", "Q11477503": "T110",
    "Q18818435": "T110", "Q3192710": "T110", "Q1673887": "T110", "Q3847009": "T110", "Q11473409": "T110",
    "Q708568": "T110", "Q1081011": "T110", "Q1063382": "T110", "Q170259": "T110", "Q1066490": "T110",
    "Q375814": "T110", "Q663837": "T110", "Q39931": "T110", "Q519925": "T110",                       # Yōga / Western teachers
}
TEACHER_CHINA = {"Q3083171": "T7", "Q3083166": "T7", "Q3028266": "T6", "Q715400": "T6", "Q3424695": "T6", "Q3080169": "T6"}
# Wikidata P1066 per East Asian artist without movement (fetched 2026-10-28)
TEACHERS = {}  # filled from TEACHERS_RAW below
OCC_UKIYOE, OCC_NIHONGA = set(), set()
NAME_SCHOOL = [("Kanō ", "T9"), ("Tosa ", "T8"), ("Utagawa ", "T127"), ("Toyohara ", "T127"), ("Katsukawa ", "T127"),
               ("Katsushika ", "T127"), ("Kitagawa ", "T127"), ("Torii ", "T127"), ("Tsukioka ", "T127"),
               ("Kikugawa ", "T127"), ("Keisai ", "T127"), ("Hiroshige", "T127")]
JAPAN = {"Q17", "Q188712", "Q205662"}
KOREA = {"Q884", "Q18097", "Q28456", "Q715257"}
CHINA = {"Q148", "Q29520", "Q13426199", "Q865", "Q8646", "Q8733", "Q9903", "Q7313", "Q7462", "Q9683"}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def countries():
    c = defaultdict(set)
    fs = glob.glob(os.path.join(INT, "visual_art", "pool_*.csv")) + glob.glob(os.path.join(INT, "visual_art", "refextra_pool_*.csv"))
    fs += [os.path.join(INT, "contemporary_pool.csv"), os.path.join(INT, "contemporary_pool_additions.csv")]
    for f in fs:
        if os.path.exists(f):
            for r in rd(f):
                c[r["qid"]].update(x for x in (r.get("countries") or "").split("|") if x)
    return c


def subs():
    """leaf code -> sub-family code."""
    s = {r["tmp"]: r["sub"] for r in rd(os.path.join(REV, "artist_leaves.csv"))}
    for f in glob.glob(os.path.join(REV, "*_leaves.csv")):
        sl = os.path.basename(f)[:-len("_leaves.csv")]
        if sl == "artist":
            continue
        for r in rd(f):
            s[f"{sl}:{r['tmp']}"] = r["sub"]
    try:
        import tree_visual_art as t
        for sub, ls in t.LEAVES.items():
            for l in ls:
                s.setdefault(l[0], sub)
    except Exception as e:  # pragma: no cover
        print("warning: pilot leaves not loaded:", e)
    return s


def fits(medium, sub):
    c = COMPAT.get(medium, ("A",))
    return c is None or any(sub.startswith(x) for x in c)


def birth_int(b):
    try:
        return int(b)
    except (TypeError, ValueError):
        return None


def match_rule(r, a, cty):
    if r["medium"] != a["medium"]:
        return False
    if r["region"] != "*" and r["region"] != a["region"]:
        return False
    if r["country"] != "*" and not (set(r["country"].split("|")) & cty):
        return False
    b = birth_int(a["birth"])
    if r["birth_from"].startswith("era:"):
        return b is None and r["birth_from"][4:] == a["era"]
    return b is not None and int(r["birth_from"]) <= b <= int(r["birth_to"])


def main():
    A = rd(os.path.join(VA, "artists.csv"))
    C = countries()
    S = subs()
    M = {m["qid"]: m for m in rd(os.path.join(REV, "movement_map.csv"))}
    R = rd(os.path.join(REV, "period_rules.csv"))
    for q, ts in TEACHERS_RAW.items():
        TEACHERS[q] = ts.split("|")
    OCC_UKIYOE.update(OCC_UKIYOE_RAW.split())
    OCC_NIHONGA.update(OCC_NIHONGA_RAW.split())

    def target(disp):
        kind, rest = disp.split(":", 1)
        if kind == "leaf":
            return rest, ""
        leaf, _, grp = rest.rpartition("/")
        return leaf, grp

    # specificity: number of artists per target leaf
    n_leaf = Counter()
    for a in A:
        for x in filter(None, a["movements"].split("|")):
            m = M.get(x.split(":")[0])
            if m and m["disposition"].startswith(("leaf:", "kind:")):
                n_leaf[target(m["disposition"])[0]] += 1

    out, placed = [], {}
    # pass 1: everything except the teacher rule (needs teachers' placements)
    pending = []
    for a in A:
        q = a["qid"]
        cty = C.get(q, set())
        b = birth_int(a["birth"])
        tags, cands, cross = [], [], []
        for x in filter(None, a["movements"].split("|")):
            mq, _, ml = x.partition(":")
            m = M.get(mq)
            d = m["disposition"] if m else "tag"
            if d.startswith(("leaf:", "kind:")):
                leaf, grp = target(d)
                sub = S.get(leaf, "")
                ok = fits(a["medium"], sub)
                if leaf == "T153" and not (cty & JAPAN and (b is None or 1140 <= b <= 1299)):
                    ok = False  # Kei only for Japanese Kamakura sculptors
                if ok:
                    cands.append((n_leaf[leaf], len(cands), leaf, grp, mq, ml))
                elif leaf in CROSS or S.get(leaf, "").startswith("M"):
                    cross.append((n_leaf[leaf], len(cands) + len(cross), leaf, grp, mq, ml))
                else:
                    tags.append(ml or mq)
            elif d.startswith("tag"):
                tags.append(ml or mq)
        row = dict(qid=q, label=a["label"], birth=a["birth"], medium=a["medium"], region=a["region"],
                   countries="|".join(sorted(cty)), leaf="", kind="", movement_tags="", rule="", confidence="", note="")
        if q in EXCLUDE:
            row.update(leaf=f"exclude:{EXCLUDE[q]}", rule="exclude", confidence="medium",
                       note="non-artist: visual-art occupation marginal (reviewed)")
        elif q in EVIDENCE:
            leaf, kind, src, conf, note = EVIDENCE[q]
            row.update(leaf=leaf, kind=kind, rule=f"evidence:{src}", confidence=conf, note=note)
            tags += [c[5] or c[4] for c in cands + cross]
        elif cands or (cross and a["medium"] not in ("architecture", "vase painting")):
            medium_note = ""
            if not cands:
                cands, cross = cross, []
                medium_note = "; medium-defining movement (installation, conceptual, minimal, kinetic, media art) overrides the recorded medium"
            tags += [c[5] or c[4] for c in cross]
            cands.sort()
            _, _, leaf, grp, mq, ml = cands[0]
            row.update(leaf=leaf, kind=grp, rule=f"movement:{mq}", confidence="high",
                       note=f"movement {ml}" + (f"; other movements: {', '.join(c[5] for c in cands[1:])}" if len(cands) > 1 else "") + medium_note)
            if medium_note:
                row["confidence"] = "medium"
            tags += [c[5] or c[4] for c in cands[1:]]
        else:
            tags += [c[5] or c[4] for c in cross]
            pending.append(row)
        row["movement_tags"] = "|".join(dict.fromkeys(t for t in tags if t))
        if q in URBAN_ABORIGINAL:
            row["note"] = (row["note"] + "; " if row["note"] else "") + "Aboriginal artist working outside a community art-centre tradition: medium's period leaf"
        out.append(row)
        placed[q] = row

    by_q = {a["qid"]: a for a in A}

    def rule_leaf(row):
        a = by_q[row["qid"]]
        cty = C.get(a["qid"], set())
        for i, r in enumerate(R, start=2):
            if match_rule(r, a, cty):
                conf = "medium" if r["country"] != "*" and not r["birth_from"].startswith("era:") else "low"
                return r["leaf"], f"period:{i}", conf, r["note"]
        return None

    # pass 2: Japanese/Chinese school evidence, then period rules
    for row in pending:
        a = by_q[row["qid"]]
        cty = C.get(a["qid"], set())
        b = birth_int(a["birth"])
        med = a["medium"]
        hit = None
        if cty & JAPAN and med in PAINT | {"printmaking"}:
            if a["qid"] in OCC_UKIYOE:
                hit = ("T127", "jp:occupation", "ukiyo-e artist (P106)")
            elif a["qid"] in OCC_NIHONGA and med in PAINT:
                hit = ("T13", "jp:occupation", "Nihonga painter (P106)")
            if not hit:
                ls = [TEACHER_SCHOOL[t] for t in TEACHERS.get(a["qid"], []) if t in TEACHER_SCHOOL]
                ls = [l for l in ls if fits(med, S.get(l, ""))]
                if ls:
                    l = Counter(ls).most_common(1)[0][0]
                    hit = (l, "jp:teacher", "school of recorded teacher (P1066)")
            if not hit and b is not None and b < 1868:
                for pre, l in NAME_SCHOOL:
                    if a["label"].startswith(pre) and (l == "T127" or fits(med, S.get(l, ""))):
                        hit = (l, "jp:art-name", f"school art-name '{pre.strip()}'")
                        break
        elif cty & CHINA and med in PAINT:
            ls = [TEACHER_CHINA[t] for t in TEACHERS.get(a["qid"], []) if t in TEACHER_CHINA]
            if ls:
                hit = (ls[0], "cn:teacher", "school of recorded teacher (P1066)")
        if hit:
            row.update(leaf=hit[0], rule=hit[1], confidence="medium", note=hit[2])
            continue
        r = rule_leaf(row)
        if r is None:
            row.update(leaf="", rule="unplaced", confidence="", note="no rule matched")
            continue
        row.update(leaf=r[0], rule=r[1], confidence=r[2], note=(r[3] + ("; " + row["note"] if row["note"] else "")))
        if r[0] == "T24":
            g = {"German": "German Renaissance", "French": "French Renaissance", "Dutch and Flemish": "Dutch and Flemish Renaissance"}
            for k, v in g.items():
                if f"kind: {k}" in r[3]:
                    row["kind"] = v

    path = os.path.join(VA, "artist_placements.csv")
    cols = ["qid", "label", "birth", "medium", "region", "countries", "leaf", "kind", "movement_tags", "rule", "confidence", "note"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(out)

    # report
    def sub_of(l):
        return "exclude" if l.startswith("exclude") else S.get(l, "?" + l)
    print("artists", len(out), "unplaced", sum(1 for r in out if not r["leaf"]))
    print("by rule type", Counter(r["rule"].split(":")[0] for r in out).most_common())
    print("by sub-family", sorted(Counter(sub_of(r["leaf"]) for r in out).items()))
    print("wrote", os.path.relpath(path, ROOT))


# Wikidata evidence for East Asian artists without a movement (fetched 2026-10-28)
TEACHERS_RAW = {
    "Q11093919": "Q347220",
    "Q11178858": "Q3083171",
    "Q11355693": "Q3514329",
    "Q11365478": "Q11627892",
    "Q11365757": "Q11365548",
    "Q11372959": "Q3121142|Q467337",
    "Q11376888": "Q20040829",
    "Q11425358": "Q1063382|Q11459900",
    "Q11459528": "Q27195853",
    "Q11459900": "Q1081011|Q11477503",
    "Q11465396": "Q11479106",
    "Q11466315": "Q11645615|Q18011598",
    "Q11483462": "Q11479106",
    "Q11518970": "Q11479106",
    "Q11531144": "Q11383402|Q11552479|Q700019",
    "Q11541091": "Q3087294",
    "Q11545174": "Q317736",
    "Q11563937": "Q11459900|Q18818435|Q708568",
    "Q11565094": "Q11434757",
    "Q11572595": "Q3154222",
    "Q11577245": "Q1358543|Q6563405",
    "Q11585149": "Q11459900",
    "Q11606622": "Q11479106",
    "Q11608247": "Q11478804",
    "Q11621987": "Q11465396",
    "Q11628513": "Q3514329",
    "Q11637083": "Q11509541",
    "Q11645148": "Q11509541",
    "Q1279685": "Q11473409|Q347220",
    "Q17221327": "Q1066490|Q1081011|Q170259",
    "Q2270045": "Q11531144",
    "Q23061148": "Q3192710",
    "Q2346122": "Q3128092",
    "Q2384056": "Q3192789",
    "Q2386947": "Q11400282|Q1358636|Q26254229",
    "Q2482193": "Q317736",
    "Q2784105": "Q11571474",
    "Q2838030": "Q11571474|Q317736",
    "Q3028266": "Q3080169|Q3424695",
    "Q3075041": "Q317736",
    "Q3122701": "Q3122703",
    "Q3128088": "Q3514329",
    "Q3178301": "Q317736",
    "Q3194352": "Q11459528",
    "Q3335331": "Q11459900|Q375814|Q708568",
    "Q3482111": "Q11576703|Q3541614",
    "Q3541642": "Q3201302",
    "Q3566605": "Q700019",
    "Q3847009": "Q11478804|Q1673887|Q519925|Q720550",
    "Q467337": "Q317736",
    "Q5072748": "Q3083166",
    "Q6037450": "Q11627892",
    "Q6441301": "Q20040829",
    "Q707301": "Q3847009",
    "Q714152": "Q663837",
    "Q7360123": "Q708568",
    "Q931356": "Q3075025",
    "Q934438": "Q39931|Q720550",
    "Q994549": "Q3028266|Q715400",
}
OCC_UKIYOE_RAW = """
    Q11372959 Q11465396 Q11487491 Q11538906 Q11541091 Q11545174 Q11572595 Q11621076 Q2346122 Q2420218 Q2482193 
    Q2574296 Q2738241 Q2784105 Q2838030 Q2972135 Q3075041 Q3075554 Q3087294 Q3178301 Q467337 Q653454 Q653932 
    Q931356 
"""  # P106 ukiyo-e artist (Q33082999)
OCC_NIHONGA_RAW = """
    Q11365757 Q11530016 
"""  # P106 Nihonga painter (Q16485594)

if __name__ == "__main__":
    main()
