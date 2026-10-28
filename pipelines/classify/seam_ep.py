"""Seam ruling S1 with the Erotic Pleasure taxonomy (owner, 2026-10-28).

Rule, applied in order: (1) explicit works made to arouse are classified in the Pleasure Taxonomies (EP); an explicit
work made and received as art or mainstream cinema is placed here by its genre. (2) Non-explicit erotic works that film
or art history names as a genre, cycle, movement or tradition stay here. (3) Adult-trade segments with no canon are EP.
(4) The side that does not hold a category keeps a pointer. Record: Pleasure-Taxonomy repo, verify/out/SEAM-VE-EP.md.

What this does here
  sources   taxonomy/film/film_placements.csv  Caligula (1979) A12-5 → A7-6 (explicit inserts in a Roman epic: rule 1
                                               exception), A12-3 kept as see-also
            taxonomy/series/anime_placements.csv  the E12-1 hentai titles → exclude (rule 1, EP II-K-12)
            taxonomy/visual_art/va_placements.csv  Shunga added as a kind of B2-17 Ukiyo-e (rule 2)
            pipelines/classify/tree_film.py  A12-5 and E12-1 retired (codes kept, never reused), anime key step 1,
                                               AN8 and the new precedence sentence S1
  published artifact/full/data/  the same changes patched into tree.json, m-ft-A.json, m-ft-E.json, m-va-B.json and
                                               find.json, because a full rebuild needs data/interim (see the handover)
Idempotent: a second run changes nothing.
Usage: python3 pipelines/classify/seam_ep.py
"""
import csv
import io
import json
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
OUT = os.path.join(ROOT, "artifact", "full", "data")
EP = "https://claude.ai/artifact/N7rBgCKAyKhaBiAbqJS6Z5"
HENTAI_EXCLUDE = "exclude:explicit hentai made to arouse; classified in the Pleasure Taxonomies, EP II-K-12 (S1)"
SHUNGA_SRC = ("https://www.ngv.vic.gov.au/essay/interpreting-shunga-scroll-sex-and-desire-between-women-in-edos-floating-world/; "
              "https://hyperallergic.com/240689/intricate-beautiful-raunchy-japan-embraces-its-ancient-erotic-print-tradition/")

A12_5_DEFN = ("<b>Retired (S1).</b> Hardcore pornography is classified in the Pleasure Taxonomies (EP II-K-1 Watching "
              "Pornography: theatrical, home-video and internet eras), not here; an explicit film made and received as "
              "cinema is placed by its genre (<i>Caligula</i> → A7-6). The code is not reused.")
E12_1_DEFN = ("<b>Retired (S1).</b> Explicit hentai made to arouse is classified in the Pleasure Taxonomies (EP II-K-12 "
              "Drawn &amp; Animated Erotic Media), not here; an adult-flagged anime made as drama, horror or art is placed "
              "by its genre (AN8), and ecchi stays E10-2. The code is not reused.")
S1 = ("S1", "Seam with Erotic Pleasure",
      "Explicit works made to arouse (hardcore pornography, hentai) are classified in the Pleasure Taxonomies, not "
      "here; an explicit work made and received as art or mainstream cinema is placed by its genre (<i>In the Realm of "
      "the Senses</i>, <i>Caligula</i>). Non-explicit erotic genres and cycles with their own canon stay here (pink "
      "film, Roman Porno, erotic drama, sexploitation, erotic thriller, ecchi; shunga in VA-B2-17). Segments of the "
      "adult trade with no canon (amateur and creator content, adult magazines, glamour and pin-up photography, "
      "late-night cable softcore) are the Pleasure Taxonomies'. Retired here: A12-5, E12-1.")
AN8 = ("AN8", "Adult flag",
       "Explicit hentai is classified in the Pleasure Taxonomies (S1; E12-1 retired); an adult-flagged art film or "
       "erotic drama (<i>Cleopatra</i> 1970, <i>Shoujo Tsubaki</i>) is placed by its genre. A gag series about everyday "
       "life is E10 (comedy first, AN5); a gentle everyday series without gag structure is E6.")
E_KEY1 = ("1. Explicit sexual content made for the adult market (hentai)? → not placed here: the Pleasure Taxonomies "
          "(S1). An adult-flagged drama, horror or art anime goes on by its genre (AN8).")
# EP-held names a reader may look for here: Finder rows to the retired cards that say where they went
FINDER_FT = [("Golden Age of Porn", "A12-5"), ("hardcore pornography", "A12-5"), ("amateur pornography", "A12-5"),
             ("creator and subscription content", "A12-5"), ("late-night cable softcore", "A12-5"),
             ("adult anime", "E12-1"), ("hentai OVA", "E12-1")]


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def wr(p, rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))  # csv default \r\n, as the pipelines write
    w.writeheader()
    w.writerows(rows)
    tmp = p + ".tmp"
    open(tmp, "w", encoding="utf-8", newline="").write(buf.getvalue())
    os.replace(tmp, p)


def jload(fn):
    return json.load(open(os.path.join(OUT, fn), encoding="utf-8"))


def jsave(fn, obj):
    p = os.path.join(OUT, fn)
    json.dump(obj, open(p + ".tmp", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    os.replace(p + ".tmp", p)


def sources():
    p = os.path.join(ROOT, "taxonomy", "film", "film_placements.csv")
    rows = rd(p)
    for r in rows:
        if r["tconst"] == "tt0080491" and r["leaf"] == "A12-5":
            r["leaf"], r["see_also"] = "A7-6", "A12-3"
            r["note"] = "Hardcore inserts in Roman epic; placed by genre (S1)"
    wr(p, rows)
    p = os.path.join(ROOT, "taxonomy", "series", "anime_placements.csv")
    rows = rd(p)
    for r in rows:
        if r["leaf"] == "E12-1":
            r["leaf"] = HENTAI_EXCLUDE
    wr(p, rows)
    p = os.path.join(ROOT, "taxonomy", "visual_art", "va_placements.csv")
    rows = rd(p)
    if not any(r["label"] == "Shunga" and r["disposition"].startswith("kind:B2-17") for r in rows):
        rows.append({"slice": "seam_ep", "pool_id": "evidence:seam_ep:Shunga", "source": "evidence", "label": "Shunga",
                     "type": "kind from evidence", "region": "Japan", "era": "traditional", "objects": "",
                     "disposition": "kind:B2-17/sub-type", "note": SHUNGA_SRC})
    wr(p, rows)
    p = os.path.join(ROOT, "pipelines", "classify", "tree_film.py")
    s = open(p, encoding="utf-8").read()
    old5 = re.search(r'\("A12-5", "Pornographic Film", "narrow",\n\s+"[^\n]*",\n', s)
    if old5:
        s = s.replace(old5.group(0), '("A12-5", "Pornographic Film (retired)", "narrow",\n     "' + A12_5_DEFN.replace('"', '\\"') + '",\n')
    old1 = re.search(r'\("E12-1", "Hentai", "narrow",\n\s+"[^\n]*",\n', s)
    if old1:
        s = s.replace(old1.group(0), '("E12-1", "Hentai (retired)", "narrow",\n     "' + E12_1_DEFN.replace('"', '\\"') + '",\n')
    s = s.replace('"1. Explicit sexual content made for the adult market (hentai)? → <b>E12 Adult Anime</b>.",',
                  json.dumps(E_KEY1, ensure_ascii=False) + ",")
    s = re.sub(r'\("AN8", "Adult flag", "[^\n]*"\),', "(" + ", ".join(json.dumps(x, ensure_ascii=False) for x in AN8) + "),", s)
    if '("S1", "Seam with Erotic Pleasure"' not in s:
        s = s.rstrip("\n") + "\n\n# Seam ruling S1 with the Erotic Pleasure taxonomy (owner, 2026-10-28; pipelines/classify/seam_ep.py)\n" \
            "PRECEDENCE.append((" + ", ".join(json.dumps(x, ensure_ascii=False) for x in S1) + "))\n"
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)


def leaf_of(T, tab, code):
    for f in T[tab]["fams"]:
        for sb in f["subs"]:
            for l in sb["leaves"]:
                if l["code"] == code:
                    return f, sb, l
    raise KeyError(code)


def published():
    T = jload("tree.json")
    MA, ME, MB = jload("m-ft-A.json"), jload("m-ft-E.json"), jload("m-va-B.json")
    F = jload("find.json")
    # Caligula → A7-6
    moved = [r for r in MA.get("A12-5", []) if r[5] == "tt0080491"]
    if moved:
        MA["A12-5"] = [r for r in MA["A12-5"] if r[5] != "tt0080491"]
        r = moved[0]
        r[3], r[4] = "A12-3", "Hardcore inserts in Roman epic; placed by genre (S1)"
        MA.setdefault("A7-6", []).append(r)
        MA["A7-6"].sort(key=lambda x: str(x[1]))
        for e in F:
            if e[1] == "FT" and e[0] == "Caligula" and e[2] == "A12-5":
                e[2] = "A7-6"
    # hentai titles leave
    gone = len(ME.get("E12-1", []))
    titles = {r[0] for r in ME.get("E12-1", [])}
    ME["E12-1"] = []
    F = [e for e in F if not (e[1] == "FT" and e[2] == "E12-1" and e[3] != "leaf" and e[0] in titles)]
    # shunga kind
    row = ["Shunga", "sub-type", "erotic prints, painted handscrolls and illustrated books of the floating world; "
           "sources: NGV essay, Hyperallergic", "seam_ep", 0]
    added = 0
    if not any(k[0] == "Shunga" for k in MB.get("B2-17", [])):
        MB.setdefault("B2-17", []).insert(1, row)
        added = 1
        F.append(["Shunga", "VA", "B2-17", "sub-type", "spring pictures; shunga"])
    # leaf cards
    fa, sa, l5 = leaf_of(T, "ft", "A12-5")
    l5.update(label="Pornographic Film (retired)", defn=A12_5_DEFN, n=0,
              see="EP II-K-1 Watching Pornography (Pleasure Taxonomies); A12-4 Sexploitation.")
    fe, se, l1 = leaf_of(T, "ft", "E12-1")
    l1.update(label="Hentai (retired)", defn=E12_1_DEFN, n=0,
              see="EP II-K-12 Drawn & Animated Erotic Media (Pleasure Taxonomies); E10-2 Ecchi.")
    _, _, l76 = leaf_of(T, "ft", "A7-6")
    l76["n"] = len(MA["A7-6"])
    fb, sbb, lb = leaf_of(T, "va", "B2-17")
    lb["n"] = len(MB["B2-17"])
    for f in T["ft"]["fams"] + T["va"]["fams"]:
        for sb in f["subs"]:
            sb["n"] = sum(x["n"] for x in sb["leaves"])
        f["n"] = sum(sb["n"] for sb in f["subs"])
    fe["key"] = [E_KEY1 if k.startswith("1. Explicit sexual content") else k for k in fe["key"]]
    T["ft"]["precedence"] = [list(AN8) if p[0] == "AN8" else p for p in T["ft"]["precedence"]]
    if not any(p[0] == "S1" for p in T["ft"]["precedence"]):
        T["ft"]["precedence"].append(list(S1))
    c = T["census"]["ft"]
    if gone:
        c["placed"] -= gone
        c["per_family"]["E"] -= gone
        c["dispositions"]["anime|exclude"] = c["dispositions"].get("anime|exclude", 0) + gone
        c["dispositions"]["anime|leaf"] -= gone
    for code in ("A12-5", "E12-1"):
        if code not in c["empty_leaves"]:
            c["empty_leaves"].append(code)
    if added:
        T["census"]["va"]["kinds"] += 1
        T["census"]["va"]["dispositions"]["seam_ep|kind"] = 1
    for term, code in FINDER_FT:
        if not any(e[0] == term and e[2] == code for e in F):
            F.append([term, "FT", code, "→ Pleasure Taxonomies (S1)", ""])
    if "Seam with Erotic Pleasure" not in T["report"]:
        T["report"] += ("<h2 id=\"seam-ep\">Seam with Erotic Pleasure (S1, October 2026)</h2><p>By owner ruling S1 "
                        "explicit works made to arouse are classified in the <a href=\"" + EP + "\">Pleasure Taxonomies</a> "
                        "and the non-explicit erotic genres with their own canon stay here. Retired: A12-5 Pornographic "
                        "Film (its one title, <i>Caligula</i>, placed by genre in A7-6) and E12-1 Hentai (" + str(gone) +
                        " titles leave the selection). Added: Shunga as a kind of B2-17 Ukiyo-e. The decision record is "
                        "<code>verify/out/SEAM-VE-EP.md</code> in the Pleasure-Taxonomy repository.</p>")
    for fn, obj in (("tree.json", T), ("m-ft-A.json", MA), ("m-ft-E.json", ME), ("m-va-B.json", MB), ("find.json", F)):
        jsave(fn, obj)
    print(f"published: Caligula moved {bool(moved)}, hentai titles removed {gone}, shunga added {added}")


if __name__ == "__main__":
    sources()
    published()
