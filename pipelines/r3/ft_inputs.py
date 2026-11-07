"""R3 restructure: write one input CSV per Film & Television block for the block passes.

Reads the published data (artifact/full/data) and the gathered evidence
(taxonomy/film/film_evidence.csv, taxonomy/series/review/*.csv), writes
taxonomy/r3/ft_in/<block>.csv with one row per placed title.
"""
import csv, glob, json, os, re

# Owner, 2026-11-07: web series leave this taxonomy for the future Interactive Entertainment
# Taxonomy (internet content, organised by its format). A title is a web series when it sits in
# the web leaves or its evidence (Wikidata genre, keywords, note) calls it a web series / web drama.
WEB_LEAVES = {"G3-6", "C1-17"}
WEB_RE = re.compile(r"web (series|drama|show|serial|television)|webseries|web-series|youtube series|internet series")

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
D = os.path.join(ROOT, "artifact", "full", "data")
OUT = os.path.join(ROOT, "taxonomy", "r3", "ft_in")
csv.field_size_limit(10**9)

# block -> (old sub-family prefixes)
BLOCKS = {
    "film_movements_doc_exp_short": ["A1", "A13", "A16", "B2", "B3", "B4"],
    "film_crime_thriller": ["A2", "A3"],
    "film_horror_scifi": ["A4", "A5"],
    "film_history_war_western_biopic": ["A7", "A17"],
    "film_fantasy_action_family_popular": ["A6", "A8", "A18", "A19"],
    "film_comedy": ["A10"],
    "film_romance_musical_erotic": ["A9", "A11", "A12"],
    "film_drama": ["A14"],
    "tv_drama_serial": ["C1", "D1", "D2", "D3", "D4", "D5", "D6"],
    "tv_korean_japanese": ["C2-1", "C2-2", "C2-3", "C2-7", "C2-8", "C2-9"],
    "tv_chinese_thai_bl": ["C2-4", "C2-5", "C2-6", "C2-10", "C2-11", "C2-12", "C2-13", "C2-14"],
    "tv_crime_thriller": ["C3"],
    "tv_comedy_children_doc": ["C4", "C7", "C8"],
    "tv_genre_unscripted": ["C5", "G1", "G2", "G3"],
    "anime_action_mecha": ["E1", "E2"],
    "anime_fantasy_magical_romance": ["E3", "E4", "E5"],
    "anime_life_sports_drama_comedy": ["E6", "E7", "E8", "E9", "E10", "E11"],
    "animation_non_japanese": ["A15", "B1", "C6"],
}

def web_reason(leaf, k, e):
    """Internet-native series only. Subscription streaming series (Netflix, iQIYI, Tencent, Indian OTT
    'web series') are television and stay; MDL's 'web series' tag alone does not decide."""
    if leaf in WEB_LEAVES:
        return "web leaf " + leaf
    wd = (e.get("wd") or "").lower()
    if WEB_RE.search(wd):
        return "Wikidata genre: " + WEB_RE.search(wd).group(0)
    blob = " ".join([e.get("kw", ""), k[4]]).lower()
    if k[2] == "KR" and k[7] == "tv" and WEB_RE.search(blob):
        return "Korean web drama (" + WEB_RE.search(blob).group(0) + ")"
    return ""

def sub_of(leaf):
    return leaf.split("-")[0]

def trim(s, n):
    s = (s or "").replace("\n", " ").strip()
    return s if len(s) <= n else s[: n - 1] + "…"

def evidence():
    ev = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "taxonomy/film/film_evidence.csv"))):
        ev[r["tconst"]] = dict(genres=r["imdb_genres"] or r["tmdb_genres"], wd=r["wd_genre"],
                               kw=r["keywords"], ov=r["overview"], country=r["countries"], runtime=r["runtime"])
    for fn in glob.glob(os.path.join(ROOT, "taxonomy/series/review/*.csv")):
        if fn.endswith("_out.csv") or "sweep" in fn:
            continue
        for r in csv.DictReader(open(fn)):
            i = r.get("id")
            if not i or i in ev:
                continue
            if "top_tags" in r:  # anime
                ev[i] = dict(genres=r.get("genres", ""), wd=r.get("type", ""), kw=r.get("top_tags", "") + "|" + r.get("tags", ""),
                             ov=r.get("english", ""), country=r.get("country", ""), runtime=r.get("studio", ""))
            else:
                ev[i] = dict(genres=r.get("imdb_genres") or r.get("tmdb_genres", "") or r.get("cluster", ""), wd=r.get("wd_genre", ""),
                             kw=r.get("keywords", ""), ov=r.get("overview", ""), country=r.get("country", ""),
                             runtime=r.get("network", ""))
    return ev

def main():
    os.makedirs(OUT, exist_ok=True)
    ev = evidence()
    pre2block = {p: b for b, ps in BLOCKS.items() for p in ps}
    rows = {b: [] for b in BLOCKS}
    tree = json.load(open(os.path.join(D, "tree.json")))
    label = {l["code"]: l["label"] for f in tree["ft"]["fams"] for s in f["subs"] for l in s["leaves"]}
    miss = 0
    web = []
    for fn in sorted(glob.glob(os.path.join(D, "m-ft-*.json"))):
        for leaf, items in json.load(open(fn)).items():
            b = pre2block.get(leaf) or pre2block.get(sub_of(leaf))
            if not b:
                print("no block", leaf, len(items)); continue
            for k in items:
                e = ev.get(k[5], {})
                if not e: miss += 1
                reason = web_reason(leaf, k, e)
                if reason:
                    web.append(dict(id=k[5], title=k[0], year=k[1], who=k[2], old_leaf=leaf, reason=reason))
                    continue
                rows[b].append(dict(id=k[5], title=k[0], year=k[1], who=k[2], old_leaf=leaf, old_leaf_label=label.get(leaf, ""),
                                    old_see=k[3], note=k[4], movement_tag=k[6], kind=k[7],
                                    genres=e.get("genres", ""), wd_genre=trim(e.get("wd", ""), 160),
                                    keywords=trim(e.get("kw", ""), 260), overview=trim(e.get("ov", ""), 260),
                                    extra=e.get("runtime", "")))
    for b, rs in rows.items():
        with open(os.path.join(OUT, b + ".csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rs[0].keys())); w.writeheader(); w.writerows(rs)
        print(b, len(rs))
    print("no evidence", miss)
    with open(os.path.join(ROOT, "taxonomy", "r3", "web_series_removed.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "title", "year", "who", "old_leaf", "reason"]); w.writeheader(); w.writerows(web)
    print("web series removed", len(web))

if __name__ == "__main__":
    main()
