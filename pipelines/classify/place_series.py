"""Series placement: anime (E), scripted TV and Asian drama (C, D), unscripted (G).

    python3 pipelines/classify/place_series.py batches   # evidence → taxonomy/series/review/{anime,tv,unscripted}_NN.csv
    python3 pipelines/classify/place_series.py merge     # *_out.csv + overrides → taxonomy/series/*_placements.csv

Evidence per item: anime — MAL/AniList genres and tags, demographic, studio,
format; scripted TV — IMDb/TMDB genres, TMDB keywords and overview, Wikidata
genres, network, episodes, serial-tradition flag; Asian drama — native title and
TMDB content found by title search (asian_drama_content.py) and Wikidata genres
(MyDramaList ID, P3868); unscripted — format family, cluster, versions.
Agents review each batch against taxonomy/series/review/series_leaves.txt.
Japanese animated films from the film selection join the anime evidence by
their MAL ID (taxonomy/pilot/jp_anime_films_matched.csv).
"""
import csv
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
import tree_film as FT  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
D = os.path.join(ROOT, "data", "interim")
OUT = os.path.join(ROOT, "taxonomy", "series")
R = os.path.join(OUT, "review")
BATCH = 230


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8"))) if os.path.exists(p) else []


def lab(v):
    return "; ".join(x.split(":", 1)[1] for x in (v or "").split("|") if ":" in x)


def kwclean(s, n=300):
    return "|".join(k for k in (s or "").split("|") if k and not re.search(
        r"blu-ray|dvd|fresh|rotten|certified|nominated|winner|dolby|imax|collection|woman-director|metacritic", k))[:n]


def sortkey(title):
    t = re.sub(r"[^a-z0-9 ]", "", title.lower())
    return re.sub(r"\b(season|the movie|movie|ova|specials?|part|2nd|3rd|\d+(st|nd|rd|th)?)\b.*", "", t).strip()


def anime_rows():
    sel = rd(os.path.join(D, "anime_selected.csv"))
    pop = {r["mal_id"]: r for r in rd(os.path.join(D, "anime_popularity.csv"))}
    cand = {r["mal_id"]: r for r in rd(os.path.join(D, "anime_candidates.csv"))}
    films = {r["mal_id"]: r for r in rd(os.path.join(ROOT, "taxonomy", "pilot", "jp_anime_films_matched.csv")) if r["mal_id"]}
    have = {r["mal_id"] for r in sel}
    for m, f in films.items():  # anime films selected as film but not as anime
        if m not in have:
            c = cand.get(m, {})
            sel.append({"mal_id": m, "title": c.get("title") or f["title"], "type": c.get("type", "MOVIE"), "year": f["year"],
                        "episodes": c.get("episodes", "1"), "country": "JP", "is_adult": "False", "main_studio": c.get("studios", ""),
                        "reasons": "film selection"})
    rows = []
    for r in sel:
        p, c = pop.get(r["mal_id"], {}), cand.get(r["mal_id"], {})
        tags = c.get("tags", "")
        rows.append({"id": r["mal_id"], "title": r["title"], "english": next((s for s in c.get("synonyms", "").split("|") if re.match(r"^[A-Za-z0-9 :'!?.,&-]+$", s)), "")[:80],
                     "type": r["type"], "year": r["year"], "episodes": r.get("episodes", ""), "country": r.get("country", ""),
                     "is_adult": r.get("is_adult", ""), "studio": r.get("main_studio", ""),
                     "genres": p.get("genres", ""), "top_tags": p.get("top_tags", ""), "tags": "|".join(tags.split("|")[:25]),
                     "film_tconst": films.get(r["mal_id"], {}).get("tconst", ""), "sort": sortkey(r["title"])})
    rows.sort(key=lambda r: (r["sort"], r["year"]))
    return rows


def tv_rows():
    sel = rd(os.path.join(D, "tv_selected.csv"))
    ct = {r["tconst"]: r for r in rd(os.path.join(D, "tv_content.csv"))}
    wd = {r["tconst"]: r for r in rd(os.path.join(D, "tv_wikidata.csv"))}
    routed = {r["tconst"]: r for r in rd(os.path.join(D, "tv_routed.csv"))}
    rows = []
    for r in sel:
        c, w, m = ct.get(r["tconst"], {}), wd.get(r["tconst"], {}), routed.get(r["tconst"], {})
        rows.append({"id": r["tconst"], "title": r["title"], "native_title": "", "type": r["imdb_title_type"],
                     "years": f"{r['start_year']}–{r['end_year']}", "episodes": r["episodes"], "country": r["country"],
                     "language": r["language"], "network": "|".join((c.get("companies") or m.get("companies", "")).split("|")[:3]),
                     "serial_flag": r["serial_tradition"], "imdb_genres": m.get("imdb_genres", ""), "tmdb_genres": c.get("genres", ""),
                     "wd_genre": lab(w.get("genre")), "keywords": kwclean(c.get("keywords")), "overview": (c.get("overview") or "")[:420],
                     "source": "tv"})
    return rows


def drama_rows(tv_ids):
    sel = rd(os.path.join(D, "asian_drama_selected.csv"))
    cand = {r["mdl_id"]: r for r in rd(os.path.join(D, "asian_drama_candidates.csv")) if r["mdl_id"]}
    con = {r["mdl_id"]: r for r in rd(os.path.join(D, "asian_drama_content.csv"))}
    wdg = {}
    p = os.path.join(D, "asian_drama_wikidata.json")
    if os.path.exists(p):
        for b in json.load(open(p)):
            if b.get("gLabel"):
                wdg.setdefault(b["mdl"].split("-")[0], set()).add(b["gLabel"])
    rows = []
    for r in sel:
        t = cand.get(r["mdl_id"], {}).get("tconst") or con.get(r["mdl_id"], {}).get("imdb", "")
        if t and t in tv_ids:
            continue  # already in the scripted TV selection: one home
        c = con.get(r["mdl_id"], {})
        rows.append({"id": "mdl:" + r["mdl_id"], "title": r["title"], "native_title": r["native_title"], "type": "drama",
                     "years": r["year"], "episodes": cand.get(r["mdl_id"], {}).get("episodes", ""), "country": r["country"],
                     "language": c.get("language", ""), "network": "", "serial_flag": "", "imdb_genres": "",
                     "tmdb_genres": c.get("genres", ""), "wd_genre": "; ".join(sorted(wdg.get(r["mdl_id"].split("-")[0], ()))),
                     "keywords": kwclean(c.get("keywords")), "overview": (c.get("overview") or "")[:420], "source": "asian_drama"})
    return rows


def unscripted_rows():
    rows = []
    for r in rd(os.path.join(D, "unscripted_formats.csv")):
        if r["kind"] != "unscripted":
            continue
        rows.append({"id": r["format_qid"], "title": r["format"], "cluster": r["cluster"], "n_versions": r["n_versions"],
                     "n_countries": r["n_countries"], "first_year": r["first_year"], "source": "format"})
    for r in rd(os.path.join(D, "asian_unscripted_mdl.csv")):
        rows.append({"id": "mdl:" + r["mdl_id"], "title": r["title"], "cluster": r["native_title"], "n_versions": "",
                     "n_countries": r["country"], "first_year": r["year"], "source": "asian_variety"})
    return rows


def leaves_text(fams):
    out = ["TAB KEY"] + [re.sub(r"<[^>]+>", "", k) for k in FT.FAMILY_KEY]
    for fam in FT.FAMILIES:
        if fam["code"] not in fams:
            continue
        out.append(f"\n## {fam['code']} {fam['label']} — test: {fam['test']}")
        out += ["  key: " + re.sub(r"<[^>]+>", "", k) for k in fam["key"]]
        for s, lab_, ax in fam["subs"]:
            out.append(f"### {s} {lab_} — {ax}")
            for l in FT.LEAVES.get(s, []):
                out.append(f"{l[0]} {l[1]}: {re.sub(r'<[^>]+>', '', l[3])} [aka {l[4]}]")
    out.append("\nPRECEDENCE")
    out += [f"{c} {n}: {re.sub(r'<[^>]+>', '', s)}" for c, n, s in FT.PRECEDENCE if c[:2] in ("AN", "TV") or c in ("F1", "F2", "F10")]
    return "\n".join(out)


def write(name, rows, cols, size=BATCH):
    n = 0
    for k in range(0, len(rows), size):
        n += 1
        with open(os.path.join(R, f"{name}_{n:02d}.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows[k:k + size])
    return n


def batches(only=None):
    os.makedirs(R, exist_ok=True)
    open(os.path.join(R, "anime_leaves.txt"), "w").write(leaves_text(("E",)))
    open(os.path.join(R, "tv_leaves.txt"), "w").write(leaves_text(("C", "D")))
    open(os.path.join(R, "unscripted_leaves.txt"), "w").write(leaves_text(("G",)))
    a = anime_rows()
    na = write("anime", a, ["id", "title", "english", "type", "year", "episodes", "country", "is_adult", "studio", "genres", "top_tags", "tags", "film_tconst"])
    tv = tv_rows()
    dr = drama_rows({r["id"] for r in tv})
    cols = ["id", "title", "native_title", "type", "years", "episodes", "country", "language", "network", "serial_flag",
            "imdb_genres", "tmdb_genres", "wd_genre", "keywords", "overview", "source"]
    nt = write("tv", sorted(tv, key=lambda r: (r["country"] or "ZZ", r["years"])), cols)
    nt += write("drama", sorted(dr, key=lambda r: (r["country"], r["years"])), cols)
    u = unscripted_rows()
    nu = write("unscripted", u, ["id", "title", "cluster", "n_versions", "n_countries", "first_year", "source"])
    print(f"anime {len(a)} in {na}; tv {len(tv)} + drama {len(dr)} in {nt}; unscripted {len(u)} in {nu}")


if __name__ == "__main__":
    {"batches": batches}[sys.argv[1]]()
