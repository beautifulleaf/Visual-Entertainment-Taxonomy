"""Seam ruling S2 with the Possession taxonomy (owner, 2026-10-31 and 2026-11-01; applied 2026-11-01).

The Possession taxonomy keeps the thing you buy and who makes and sells it; the way something is made or decorated as an
art goes to Visual Entertainment (VE); ways of using things stay in Possession. Following that rubric the Possession
repository handed over, as they stood:
  framework/handover/VE_craft_traditions.json      553 craft and artistic traditions from 30 categories
  framework/handover/VE_A1_clothing_traditions.json  92 clothing craft and dress traditions
  rebuild/work/TRADITIONS_RETIRED/to_ve.json        13 garden and flower traditions
  rebuild/work/V4_F2/ve_register.json, ve_names.json  122 artists and 194 works taken out of the art category (F2)
  rebuild/reader/A1.json ("ve" link-outs)           named cloths the clothing category points to VE for
Every row was placed with VE's family key and precedence (one decision per row, with its reason) in
taxonomy/seams/possession_handover.csv; new leaves are in taxonomy/seams/possession_new_leaves.csv.

What this does
  sources   taxonomy/visual_art/leaves_scaleup.csv  the new leaves (slice seam_possession)
            taxonomy/visual_art/va_placements.csv   new kinds (kind:<leaf>/<group>) and Possession names of traditions VE
                                                    already holds (alias:<leaf>), slice seam_possession
            tree_visual_art.py reads possession_handover.csv itself for precedence S2 and the "See also" back-links to
                                                    the Possession products, so a full rebuild keeps them
  published artifact/full/data/  the same changes patched into tree.json, m-va-*.json and find.json (a full rebuild needs
                                                    data/interim; after one, run this script again for the finder rows)
Idempotent: a second run changes nothing.
Usage: python3 pipelines/classify/seam_possession.py
"""
import csv
import io
import json
import os
import re
import unicodedata
from collections import Counter, defaultdict

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
OUT = os.path.join(ROOT, "artifact", "full", "data")
SEAMS = os.path.join(ROOT, "taxonomy", "seams")
HANDOVER = os.path.join(SEAMS, "possession_handover.csv")
NEW_LEAVES = os.path.join(SEAMS, "possession_new_leaves.csv")
PLACEMENTS = os.path.join(ROOT, "taxonomy", "visual_art", "va_placements.csv")
SCALEUP = os.path.join(ROOT, "taxonomy", "visual_art", "leaves_scaleup.csv")
POSSESSION = "https://claude.ai/artifact/C1cQq1ygVd7bWfw7Duem6n"
SLICE = "seam_possession"

S2 = ("S2", "Seam with Possession",
      "The thing a person buys and owns, and who makes and sells it, is the Possession taxonomy's (a Persian rug, a "
      "Murano vase, Harris Tweed cloth, a bonsai tree); the tradition of making or decorating it to be looked at is "
      "placed here (Persian carpet weaving, Murano glassblowing, bonsai as an art). Ways of using things stay in "
      "Possession. A leaf that holds a tradition whose products Possession files names them under <i>See also</i>. "
      "Brands, sellers and product versions are never kinds here; artists and works taken out of Possession's art "
      "category are placed by P11 and P15.")

# Owner follow-up rulings on S2 (2026-11-01): (1) a sub-family of its own for the plant and floral arts; (2) a leather
# sub-family; (3) leaves named after an object become finder rows (Clocks and Watches and Cutlery give way to their named
# schools); (5) a Design section for the museum design collections, structure only, gathered later.
NEW_SUBS = {
    "K": [("K14", "Plant & Floral Arts", "Axis: tradition. Living plants and cut flowers shaped and arranged as works to "
           "be looked at: trees and landscapes in containers (bonsai, penjing, saikei, hòn non bộ) and flower "
           "arrangement (ikebana).")],
    "H": [("H10", "Leatherwork", "Axis: tradition. Leather tooled, carved, stamped, embroidered or appliquéd where the "
           "decorated leather is the work (Western saddle carving, Moroccan leather, jutti). Leather mosaic sewn as a "
           "textile stays H4; bindings are C3; shadow puppets D4.")],
}
FAMILY_TEXT = {
    "K": (" The plant and floral arts of the garden traditions (bonsai, penjing, ikebana) are K14.",
          "4. A living plant shaped in a container, or a flower arrangement, made as a work (bonsai, penjing, ikebana)? "
          "→ <b>K14</b>."),
    "H": (" Decorated leather is H10.",
          "10. Decorated leather (tooled, carved, stamped, embroidered or appliquéd) where the leather is the work? → "
          "<b>H10</b>."),
}
DESIGN = {
    "code": "N", "label": "Design",
    "test": "an object or graphic designed for serial production and held as a landmark of its field by a design "
            "collection or a major design award (a chair, a lamp, an appliance, a poster), placed by the design "
            "movement or school that canonised it; the designed object is the kind, with designer, maker, year and "
            "holding collection.",
    "key": ["1. Furniture or a light fitting designed for serial production? → <b>N1</b>.",
            "2. A product, appliance, tool, vessel or vehicle designed for industry? → <b>N2</b>.",
            "3. A poster, identity, information graphic or book jacket designed for print? → <b>N3</b>. A typeface is "
            "C1-12; a poster made and studied as a print is B2 (P17)."],
    "subs": [("N1", "Furniture & Lighting Design", "Axis: design movement or school. Not gathered yet: the collections "
              "are listed in the report (Design section)."),
             ("N2", "Product & Industrial Design", "Axis: design movement or school. Not gathered yet."),
             ("N3", "Graphic Design", "Axis: design movement or school. Not gathered yet.")],
}
DESIGN_SOURCES = ("MoMA (Architecture and Design), the V&A, Cooper Hewitt, the Design Museum (London), the Vitra Design "
                  "Museum, Die Neue Sammlung, the ADI Design Museum (Compasso d'Oro) and Red Dot Best of the Best")
FAMILY_KEY_DESIGN = ("Is it a <b>design for serial production</b> held as a landmark of design (a chair, lamp, appliance "
                     "or poster in a design collection)? → <b>N Design</b> (P17).")
FAMILY_KEY_PLANT = "Living plant and floral arts (bonsai, ikebana) are K14."
P17 = ("P17", "Design and the decorative arts",
       "N holds designs for serial production by the design movement or school that canonised them, the designed "
       "object being the kind. I3 keeps the period styles of furniture and the decorative arts with their designers "
       "and makers; a designer stays a kind of I3 while N is being gathered. A poster made and studied as a print is "
       "B2, a typeface C1-12, and studio crafts made by hand (studio pottery, studio glass) stay with their material.")
FIXES = [("T158 Quilts of Gee's Bend", "H4-93 Quilts of Gee's Bend"), ("H4-91 Quilts of Gee's Bend", "H4-93 Quilts of Gee's Bend")]


def structure(fams, family_key, precedence, as_tuples):
    """Add K14, H10 and family N, their key lines, and P17 to a family list (published dicts or the source module's).
    Idempotent. as_tuples: sub-families are (code, label, axis) tuples (sources) instead of dicts (published)."""
    by = {f["code"]: f for f in fams}
    for fc, subs in NEW_SUBS.items():
        f = by[fc]
        have = {(s[0] if as_tuples else s["code"]) for s in f["subs"]}
        for code, label, axis in subs:
            if code not in have:
                f["subs"].append((code, label, axis) if as_tuples else
                                 {"code": code, "label": label, "axis": axis, "leaves": [], "n": 0})
        test_add, key_add = FAMILY_TEXT[fc]
        if test_add.strip() not in f["test"]:
            f["test"] = f["test"].rstrip() + test_add
        if key_add not in f["key"]:
            f["key"].append(key_add)
    if "N" not in by:
        n = {k: (list(v) if isinstance(v, list) else v) for k, v in DESIGN.items()}
        if not as_tuples:
            n["subs"] = [{"code": c, "label": l, "axis": a, "leaves": [], "n": 0} for c, l, a in DESIGN["subs"]]
            n.update(n=0, nleaves=0, unit="items")
        fams.append(n)
    for i, k in enumerate(family_key):
        if k.startswith("1.") and FAMILY_KEY_PLANT not in k:
            family_key[i] = k.rstrip() + " " + FAMILY_KEY_PLANT
        if k.startswith("3.") and "N Design" not in k:
            family_key[i] = k.rstrip() + " " + FAMILY_KEY_DESIGN
        if k.startswith("8.") and "decorated leather" not in k:
            family_key[i] = k.replace("felted textiles, dress)", "felted textiles, dress, decorated leather)")
    if not any(p[0] == "P17" for p in precedence):
        precedence.append(P17 if as_tuples else list(P17))


def norm(s):
    s = unicodedata.normalize("NFKD", re.sub(r"<[^>]+>", "", s or "")).encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s).split())


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8"))) if os.path.exists(p) else []


def wr(p, rows, fields=None):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields or list(rows[0].keys()))  # csv default \r\n, as the pipelines write
    w.writeheader()
    w.writerows(rows)
    open(p + ".tmp", "w", encoding="utf-8", newline="").write(buf.getvalue())
    os.replace(p + ".tmp", p)


def jload(fn):
    return json.load(open(os.path.join(OUT, fn), encoding="utf-8"))


def jsave(fn, obj):
    p = os.path.join(OUT, fn)
    json.dump(obj, open(p + ".tmp", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    os.replace(p + ".tmp", p)


def backlinks(rows):
    """leaf → ordered Possession products ("Persian rug (B2 Soft Furnishings)") for the leaf's See-also line."""
    out = defaultdict(list)
    for r in rows:
        if r["action"] not in ("exists", "kind", "new_leaf", "finder") or not r["forms"] or r["kind"] in ("artist", "work"):
            continue
        for f in r["forms"].split("; ")[:3]:
            item = f"{f} ({r['possession_cat']} {r['possession_cat_name']})"
            if item not in out[r["ve_code"]]:
                out[r["ve_code"]].append(item)
    return out


def see_with_links(see, items, cap=8):
    see = re.sub(r"\s*Possession taxonomy: .*$", "", see or "").rstrip()
    if not items:
        return see
    more = len(items) - cap
    tail = "; ".join(items[:cap]) + (f"; and {more} more" if more > 0 else "")
    if see and not see.endswith((".", "!", "?")):
        see += "."
    return (see + " " if see else "") + "Possession taxonomy: " + tail + "."


def kind_note(r):
    note = r["gloss"].strip().rstrip(".")
    if r["forms"] and r["kind"] not in ("artist", "work"):
        note += f" · owned as {r['forms'].split('; ')[0]} (Possession {r['possession_cat']})"
    return note + " · " + r["source_url"] if r["source_url"] else note


# ---------------------------------------------------------------- sources
def sources(rows, leaves):
    su = rd(SCALEUP)
    have = {r["code"] for r in su}
    for nl in leaves:
        if nl["code"] not in have:
            su.append({k: nl.get(k, "") for k in su[0].keys()})
    for r in su:
        for a, b in FIXES:
            r["see"] = r["see"].replace(a, b)
    wr(SCALEUP, su)
    pl = [r for r in rd(PLACEMENTS) if r["slice"] != SLICE]
    for r in rows:
        if r["action"] == "kind":
            disp = f"kind:{r['ve_code']}/{r['ve_group']}" if r["ve_group"] else f"kind:{r['ve_code']}"
            label = r["ve_label"]
        elif r["action"] == "new_leaf":
            disp, label = f"leaf:{r['ve_code']}", r["possession_name"]
        elif r["action"] == "exists" and r["kind"] not in ("artist", "work") \
                and norm(r["possession_name"]) != norm(r["ve_label"]):
            disp, label = f"alias:{r['ve_code']}", r["possession_name"]
        else:
            continue
        pl.append({"slice": SLICE, "pool_id": f"possession:{r['pid']}", "source": "possession", "label": label,
                   "type": "artist" if r["kind"] == "artist" else "possession " + r["kind"], "region": r["region"],
                   "era": "", "objects": "", "disposition": disp,
                   "note": kind_note(r) if r["action"] in ("kind", "new_leaf") else ""})
    wr(PLACEMENTS, pl)


# ---------------------------------------------------------------- published
def published(rows, leaves):
    T = jload("tree.json")
    structure(T["va"]["fams"], T["va"]["familyKey"], T["va"]["precedence"], False)
    F = jload("find.json")
    fams = {f["code"]: f for f in T["va"]["fams"]}
    M = {c: (jload(f"m-va-{c}.json") if os.path.exists(os.path.join(OUT, f"m-va-{c}.json")) else {}) for c in fams}
    L = {}
    for f in T["va"]["fams"]:
        for sb in f["subs"]:
            for l in sb["leaves"]:
                L[l["code"]] = (f, sb, l)
    # new leaves
    for nl in leaves:
        if nl["code"] in L:
            continue
        f = fams[nl["code"][0]]
        sb = next(s for s in f["subs"] if s["code"] == nl["sub"])
        l = {"code": nl["code"], "label": nl["label"], "breadth": nl["breadth"], "defn": nl["defn"],
             "aliases": nl["aliases"].replace(";", "; ").replace(";  ", "; "), "see": nl["see"],
             "src": [[nl["attest"], "source page"]], "weak": "", "n": 0, "alias_rows": []}
        sb["leaves"].append(l)
        M[f["code"]].setdefault(nl["code"], [])
        L[nl["code"]] = (f, sb, l)
        F.append([l["label"], "VA", l["code"], "leaf", l["aliases"]])
    fkeys = {(e[0], e[2]) for e in F if e[1] == "VA"}

    def find(name, code, what, al=""):
        if (name, code) not in fkeys:
            F.append([name, "VA", code, what, al])
            fkeys.add((name, code))

    added = Counter()
    for r in rows:
        code, act = r["ve_code"], r["action"]
        if act == "decline" or code not in L:
            continue
        f, sb, l = L[code]
        mem = M[f["code"]].setdefault(code, [])
        known = {norm(k[0]) for k in mem} | {norm(l["label"])} | {norm(a) for a in re.split(r";\s*", l["aliases"]) if a}
        if act == "kind":
            if norm(r["ve_label"]) not in known:
                mem.append([r["ve_label"], r["ve_group"], kind_note(r), "possession", 1 if r["kind"] == "artist" else 0])
                added["kind"] += 1
            find(r["ve_label"], code, r["ve_group"] or ("maker" if r["kind"] == "artist" else "kind"))
        elif act == "new_leaf":
            if norm(r["possession_name"]) not in {norm(k[0]) for k in mem}:
                mem.append([r["possession_name"], "Gathered rows (the leaf's own evidence)", kind_note(r), "possession", 0])
                added["leaf evidence"] += 1
        elif act == "exists":
            if r["kind"] not in ("artist", "work") and norm(r["possession_name"]) not in known \
                    and r["possession_name"] not in l["alias_rows"]:
                l["alias_rows"].append(r["possession_name"])
                added["alias"] += 1
            if norm(r["possession_name"]) not in known:
                find(r["possession_name"], code, "Possession hand-off" + (f" = {r['ve_label']}" if r["ve_label"] else ""))
        elif act == "finder":
            find(r["ve_label"] or r["possession_name"], code, r["what"] or "finder")
            if r["ve_label"] and norm(r["possession_name"]) != norm(r["ve_label"]):
                find(r["possession_name"], code, r["what"] or "finder")
            added["finder"] += 1
    for code, items in backlinks(rows).items():
        if code in L:
            L[code][2]["see"] = see_with_links(L[code][2]["see"], items)
    for f in T["va"]["fams"]:
        for sb in f["subs"]:
            for l in sb["leaves"]:
                l["n"] = len(M[f["code"]].get(l["code"], []))
            sb["n"] = sum(x["n"] for x in sb["leaves"])
        f["n"] = sum(sb["n"] for sb in f["subs"])
        f["nleaves"] = sum(len(sb["leaves"]) for sb in f["subs"])
    if not any(p[0] == "S2" for p in T["va"]["precedence"]):
        T["va"]["precedence"].append(list(S2))
    c = T["census"]["va"]
    for f in T["va"]["fams"]:
        for sb in f["subs"]:
            for l in sb["leaves"]:
                for a, b in FIXES:
                    l["see"] = l["see"].replace(a, b)
    c["families_built"] = sum(1 for f in T["va"]["fams"] if f["nleaves"])
    c["leaves"] = sum(f["nleaves"] for f in T["va"]["fams"])
    c["kinds"] = sum(f["n"] for f in T["va"]["fams"])
    c["empty_leaves"] = [l["code"] for f in T["va"]["fams"] for s in f["subs"] for l in s["leaves"] if l["n"] == 0]
    acts = Counter(r["action"] for r in rows)
    for k in [k for k in c["dispositions"] if k.startswith(SLICE + "|")]:
        del c["dispositions"][k]
    for a, n in acts.items():
        c["dispositions"][f"{SLICE}|{a}"] = n
    T["report"] = re.sub(r'<h2 id="seam-possession">.*?(?=<h2 |$)', "", T["report"], flags=re.S)
    T["report"] += report(rows, leaves, acts)
    jsave("tree.json", T)
    for code, m in M.items():
        jsave(f"m-va-{code}.json", m)
    jsave("find.json", F)
    page = os.path.join(OUT, "..", "index.html")
    html = open(page, encoding="utf-8").read()
    html2 = html.replace("of the 13 families", "of the ${T.fams.length} families")
    if html2 != html:
        open(page, "w", encoding="utf-8").write(html2)
    print("published:", dict(acts), "| added", dict(added), "| new leaves", len(leaves), "| VA leaves", c["leaves"],
          "kinds", c["kinds"])


def report(rows, leaves, acts):
    by = Counter(r["kind"] for r in rows)
    kinds = ", ".join(f"{n} {k}{'s' if n != 1 else ''}" for k, n in by.most_common())
    nl = "; ".join(f"{l['code']} {l['label']}" for l in leaves)
    dec = [r for r in rows if r["action"] == "decline"]
    return ("<h2 id=\"seam-possession\">Seam with Possession (S2, November 2026)</h2>"
            f"<p>By the owner's rubric the <a href=\"{POSSESSION}\">Possession taxonomy</a> keeps the things a person buys and "
            "who makes and sells them; the traditions of making and decorating them as art come here. Possession handed "
            f"over {len(rows):,} rows ({kinds}). Each was placed with the family key and precedence: "
            f"{acts.get('exists', 0):,} were already here under the same or another name (their Possession names are added "
            f"as aliases and finder rows), {acts.get('kind', 0):,} became new kinds of existing leaves, "
            f"{acts.get('new_leaf', 0):,} became new leaves, {acts.get('finder', 0):,} are finder rows (works, named cloths "
            f"and technique names routed to their leaf), and {len(dec)} were declined as not visual art.</p>"
            + (f"<p>New leaves: {nl}.</p>" if leaves else "")
            + (f"<p>Declined: {'; '.join(r['possession_name'] + ' (' + r['reason'] + ')' for r in dec)}.</p>" if dec else "")
            + "<p>Owner follow-up (November 2026): the plant and floral arts have their own sub-family, K14; decorated "
            "leather has H10; leaves named after an object became finder rows (Clocks and Watches and Cutlery gave way to "
            "their named schools: Jura, Black Forest, London, Glashütte, Comtoise, Mora, Vienna and Connecticut clockmaking, "
            "wadokei; Solingen, Thiers and Sheffield cutlery); and a <b>Design</b> family, N, is set up for the landmark "
            "designs held by the design collections, structure only: N1 Furniture &amp; Lighting Design, N2 Product &amp; "
            "Industrial Design, N3 Graphic Design, with precedence P17 against I3. It will be gathered from " + DESIGN_SOURCES
            + "; a design enters when a fetched page shows it held by such a collection or given such an award.</p>"
            + "<p>A leaf whose tradition makes things Possession files names those products under <i>See also</i> "
            "(precedence S2). The row-by-row record is <code>taxonomy/seams/possession_handover.csv</code>; the decision "
            "record is <code>docs/seam-possession.md</code>.</p>")


def main():
    rows = rd(HANDOVER)
    leaves = rd(NEW_LEAVES)
    sources(rows, leaves)
    published(rows, leaves)


if __name__ == "__main__":
    main()
