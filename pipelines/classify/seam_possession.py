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
    F = jload("find.json")
    fams = {f["code"]: f for f in T["va"]["fams"]}
    M = {c: jload(f"m-va-{c}.json") for c in fams}
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
