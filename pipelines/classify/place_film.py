"""Film placement for the full tab: evidence, rule proposals, review batches, merge.

    python3 pipelines/classify/place_film.py batches   # evidence + rule proposal → taxonomy/film/review/films_NN.csv
    python3 pipelines/classify/place_film.py merge     # reviewed *_out.csv + overrides → taxonomy/film/film_placements.csv

Rules first: a proposal per film from runtime, IMDb/TMDB genres, TMDB keywords,
Wikidata genres and movement-article links; then agents review each batch
against the leaf list (taxonomy/film/review/ft_leaves.txt) and write
films_NN_out.csv. Japanese films keep their reviewed pilot placements
(taxonomy/pilot/japan_placements.csv). Hand corrections go in
seeds/classify/film_overrides.csv; extra films in seeds/classify/film_additions.csv.
"""
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
import tree_film as FT  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
D = os.path.join(ROOT, "data", "interim")
S = os.path.join(ROOT, "seeds", "classify")
OUT = os.path.join(ROOT, "taxonomy", "film")
R = os.path.join(OUT, "review")
BATCH = 220
REPLACE = set()


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8"))) if os.path.exists(p) else []


# Movement articles whose links attest membership (D1 tag), by leaf.
MOVEMENT_ARTICLES = {
    "Japanese New Wave": "A1-1", "German expressionist cinema": "A1-2", "Soviet montage theory": "A1-3",
    "French impressionist cinema": "A1-4", "Poetic realism": "A1-5", "Italian neorealism": "A1-6",
    "French New Wave": "A1-7", "Left Bank (film)": "A1-8", "British New Wave": "A1-9",
    "Czechoslovak New Wave": "A1-10", "Polish Film School": "A1-11", "Yugoslav Black Wave": "A1-12",
    "Cinema Novo": "A1-13", "Third Cinema": "A1-14", "New Hollywood": "A1-15", "New German Cinema": "A1-16",
    "Parallel cinema": "A1-17", "Iranian New Wave": "A1-18", "Taiwan New Cinema": "A1-19", "Hong Kong New Wave": "A1-20",
    "Dogme 95": "A1-23", "List of Dogme 95 films": "A1-23", "Romanian New Wave": "A1-24",
    "Berlin School (filmmaking)": "A1-25", "New queer cinema": "A1-26", "Mumblecore": "A1-27", "L.A. Rebellion": "A1-28",
    "Australian New Wave": "A1-29", "Greek Weird Wave": "A1-30", "New Argentine Cinema": "A1-31",
    "Cinéma du look": "A1-32", "Slow cinema": "A1-33",
}
CYCLE_ARTICLES = {"Giallo": "A3-8", "Poliziotteschi": "A2-9", "Heroic bloodshed": "A8-5", "Spaghetti Western": "A17-2",
                  "Blaxploitation": "A2-10", "Hood film": "A2-11", "Masala film": "A18-1", "Pinky violence": "A2-6",
                  "Mondo film": "A13-8", "Ostern": "A17-5", "Partisan film": "A7-10", "Commedia all'italiana": "A10-8"}

# Signals → leaf. Each is (leaf, wikidata genre labels, TMDB keywords). Order = priority
# (named cycles first, as in key step 3).
SIGNALS = [
    ("A3-8", ["giallo"], ["giallo"]),
    ("A2-9", ["poliziottesco", "poliziotteschi"], ["poliziottesco", "poliziotteschi"]),
    ("A2-10", ["blaxploitation", "blaxploitation film"], ["blaxploitation"]),
    ("A2-11", ["hood film"], ["hood-film"]),
    ("A8-5", ["heroic bloodshed"], ["heroic-bloodshed"]),
    ("A8-3", ["wuxia", "wuxia film"], ["wuxia"]),
    ("A8-4", ["kung fu film"], ["kung-fu"]),
    ("A17-2", ["spaghetti western"], ["spaghetti-western"]),
    ("A17-5", ["Ostern"], ["ostern"]),
    ("A17-3", ["revisionist Western"], ["revisionist-western"]),
    ("A17-4", ["neo-Western", "contemporary western"], ["neo-western", "modern-western"]),
    ("A5-1", ["kaiju", "kaiju film", "giant monster film"], ["kaiju", "giant-monster"]),
    ("A2-5", ["film noir", "neo-noir"], ["film-noir", "neo-noir"]),
    ("A18-1", ["masala film"], ["masala"]),
    ("A4-17", ["cannibal film"], ["cannibal-film"]),
    ("A13-8", ["mondo film"], ["mondo"]),
    ("A10-8", ["commedia all'italiana"], ["commedia-all-italiana"]),
    ("A7-6", ["sword-and-sandal film", "peplum"], ["sword-and-sandal", "peplum"]),
    ("A12-5", ["pornographic film"], ["golden-age-of-porn"]),
    ("A12-4", ["sexploitation film"], ["sexploitation"]),
    ("A4-8", ["slasher film"], ["slasher"]),
    ("A4-6", ["zombie film"], ["zombie"]),
    ("A4-11", ["vampire film"], ["vampire"]),
    ("A4-10", ["folk horror"], ["folk-horror"]),
    ("A4-7", ["found footage film"], ["found-footage"]),
    ("A4-4", ["body horror"], ["body-horror"]),
    ("A6-3", ["superhero film"], ["superhero"]),
    ("A3-7", ["spy film", "spy thriller"], ["spy", "espionage"]),
    ("A2-7", ["heist film"], ["heist"]),
    ("A8-7", ["buddy cop film"], ["buddy-cop"]),
    ("A10-4", ["screwball comedy"], ["screwball-comedy"]),
    ("A10-11", ["mockumentary"], ["mockumentary"]),
    ("A10-6", ["parody film"], ["parody", "spoof"]),
    ("A19-2", ["Christmas film"], ["christmas"]),
    ("A7-9", ["Holocaust film"], ["holocaust"]),
    ("A7-8", ["biographical film"], ["biography", "biopic"]),
    ("A5-6", ["space opera"], ["space-opera"]),
    ("A5-4", ["cyberpunk", "cyberpunk film"], ["cyberpunk"]),
    ("A14-11", ["road movie"], ["road-movie"]),
    ("A14-10", ["legal drama", "courtroom drama"], ["courtroom-drama"]),
    ("A14-7", ["sports film"], ["sports-film"]),
    ("A2-8", ["prison film"], ["prison-escape"]),
    ("A3-4", ["erotic thriller"], ["erotic-thriller"]),
    ("A4-16", ["comedy horror"], ["horror-comedy"]),
    ("A6-6", ["swashbuckler film"], ["swashbuckler"]),
    ("A11-2", ["dance film"], ["dance-film"]),
    ("A2-1", ["yakuza film"], ["yakuza"]),
    ("A7-2", ["samurai cinema"], ["samurai"]),
    ("A7-1", ["jidaigeki"], ["jidaigeki"]),
    ("A5-2", ["tokusatsu"], ["tokusatsu"]),
    ("A7-10", ["partisan film"], []),
    ("A16-2", ["surrealist film"], []),
    ("A16-1", ["experimental film"], ["experimental-film"]),
    ("A13-6", ["essay film"], []),
    ("A14-12", ["christian film"], ["christian-film"]),
    ("A4-15", ["science fiction horror film"], []),
    ("A4-13", ["gothic film", "gothic horror film"], []),
    ("A4-14", ["werewolf film", "natural horror film", "monster film"], ["werewolf", "creature-feature", "natural-horror"]),
    ("A4-12", [], ["haunted-house"]),
    ("A4-3", ["ghost film", "supernatural horror film"], []),
    ("A3-5", ["rape and revenge film", "vigilante film"], ["rape-and-revenge"]),
    ("A5-9", ["time-travel film"], ["time-travel"]),
    ("A5-7", ["dystopian film"], ["dystopia"]),
    ("A5-5", ["post-apocalyptic film", "disaster film", "apocalyptic film"], ["post-apocalyptic", "disaster"]),
    ("A5-8", ["alien invasion"], ["alien-invasion"]),
    ("A6-4", ["sword and sorcery film"], ["sword-and-sorcery", "high-fantasy"]),
    ("A6-6", ["pirate film"], ["pirate"]),
    ("A6-5", ["cinematic fairy tale"], ["fairy-tale"]),
    ("A8-6", ["girls with guns"], []),
    ("A13-2", ["concert film", "music documentary film", "rockumentary"], ["concert-film"]),
    ("A10-12", ["stand-up comedy"], ["stand-up-comedy"]),
    ("A10-10", ["crime comedy film"], []),
    ("A10-9", ["action comedy film"], []),
    ("A10-3", ["black comedy film", "satirical film", "black comedy", "political satire"], ["black-comedy", "satire"]),
    ("A10-7", ["sex comedy"], ["sex-comedy", "teen-comedy"]),
    ("A2-3", ["police procedural film", "police film", "detective film"], ["police-procedural"]),
    ("A2-2", ["gangster film"], ["gangster"]),
    ("A14-7", ["sport film", "boxing film", "american football film", "association football film", "american basketball film"], []),
    ("A14-10", ["trial film", "legal thriller"], ["trial"]),
    ("A8-1", ["ninja film", "martial arts film"], ["martial-arts"]),
]


def cell(s):
    return (s or "").replace("\n", " ").strip()


def evidence():
    fs = rd(os.path.join(D, "film_selected.csv"))
    have = {r["tconst"] for r in fs}
    rt = {r["tconst"]: r for r in rd(os.path.join(D, "film_ratings.csv"))}
    for a in rd(os.path.join(S, "film_additions.csv")):
        if a["tconst"] not in have:
            m = rt.get(a["tconst"], {})
            fs.append({"key": a["tconst"], "tconst": a["tconst"], "title": a["title"], "year": a["year"],
                       "title_type": m.get("imdb_title_type", "movie"), "countries": a["countries"],
                       "reasons": "addition", "note": a["reason"]})
    ct = {r["tconst"]: r for r in rd(os.path.join(D, "film_content.csv"))}
    wd = {r["tconst"]: r for r in rd(os.path.join(D, "film_wikidata.csv"))}
    ew = {r["tconst"]: r["enwiki"] for r in rd(os.path.join(D, "film_enwiki.csv"))}
    links = {}
    p = os.path.join(D, "movement_article_links.json")
    if os.path.exists(p):
        for art, ls in json.load(open(p)).items():
            for t in ls:
                links.setdefault(t, set()).add(art)
    rows = []
    for f in fs:
        t = f["tconst"]
        m, c, w = rt.get(t, {}), ct.get(t, {}), wd.get(t, {})
        lab = lambda col: "; ".join(v.split(":", 1)[1] for v in w.get(col, "").split("|") if ":" in v)
        arts = sorted(links.get(ew.get(t, ""), set()))
        rows.append({
            "tconst": t, "title": f["title"], "year": f["year"], "type": f.get("title_type") or m.get("imdb_title_type", ""),
            "runtime": m.get("runtime", ""), "countries": f["countries"], "language": c.get("language") or m.get("language", ""),
            "director": lab("director"), "wd_genre": lab("genre"), "wd_movement": lab("movement"),
            "imdb_genres": m.get("imdb_genres", ""), "tmdb_genres": c.get("genres", ""),
            "keywords": "|".join(k for k in c.get("keywords", "").split("|")
                                 if k and not re.search(r"blu-ray|dvd|fresh|rotten|certified|nominated|winner|dolby|imax|duringcredits|aftercredits|collection|woman-director|metacritic|^(kiss|cigarette-smoking|telephone-call|photograph|watching-tv|cell-phone)$", k))[:320],
            "overview": cell(c.get("overview", ""))[:420],
            "linked_from": "; ".join(a for a in arts if a in MOVEMENT_ARTICLES or a in CYCLE_ARTICLES),
            "based_on": lab("based_on")[:120], "enwiki": ew.get(t, ""),
        })
    return rows


def propose(r):
    """Rule proposal: (leaf or route, key step, reason)."""
    g = set(r["imdb_genres"].split("|")) | set(r["tmdb_genres"].split("|"))
    kw = set(r["keywords"].split("|"))
    wg = {x.strip().lower() for x in r["wd_genre"].split(";")}
    try:
        rtm = int(r["runtime"] or 0)
    except ValueError:
        rtm = 0
    jp = "JP" in r["countries"].split("|")
    anim = "Animation" in g
    short = (0 < rtm < 40) or (r["type"] == "short" and rtm < 40)
    if anim and jp and r["tconst"] not in REPLACE:
        return "route:FT-E", "family 1", "Japanese animation"
    if short:
        if anim:
            if "stop-motion" in kw or "claymation" in kw:
                return "B1-3", "B 1", "animated short (stop-motion)"
            if "computer-animation" in kw or "cgi" in kw or "pixar" in kw:
                return "B1-4", "B 1", "animated short (CGI)"
            return ("B1-1" if int(r["year"] or 0) < 1970 else "B1-2"), "B 1", "animated short"
        if "Documentary" in g:
            return ("B3-1" if int(r["year"] or 0) < 1906 else "B3-2"), "B 2", "non-fiction short"
        if "experimental-film" in kw or "avant-garde" in kw or "experimental film" in wg:
            return "B4-1", "B 3", "experimental short"
        if int(r["year"] or 0) < 1910 and ("Fantasy" in g or "trick-film" in kw):
            return "B2-1", "B 4", "trick film"
        if "Comedy" in g and int(r["year"] or 0) < 1940:
            return "B2-2", "B 4", "silent/early comedy short"
        return "B2-3", "B 4", "live-action short"
    if "Documentary" in g:
        for k, leaf in (("concert-film", "A13-2"), ("concert", "A13-2"), ("nature-documentary", "A13-3"), ("wildlife", "A13-3"),
                        ("true-crime", "A13-5"), ("essay-film", "A13-6"), ("city-symphony", "A13-7"), ("mondo", "A13-8"),
                        ("cinema-verite", "A13-4"), ("direct-cinema", "A13-4"), ("stand-up-comedy", "A10-12")):
            if k in kw:
                return leaf, "1", f"documentary ({k})"
        if "stand-up comedy" in wg:
            return "A10-12", "1", "stand-up special"
        return "A13-1", "1", "documentary"
    if anim:
        if "adult-animation" in kw or "adult animation" in wg:
            return "A15-4", "2", "adult animation"
        if "stop-motion" in kw or "claymation" in kw or "stop-motion animation" in wg:
            return "A15-3", "2", "stop-motion"
        if "computer-animation" in kw or "cgi-animation" in kw or "computer animation" in wg or int(r["year"] or 0) >= 2006:
            return "A15-2", "2", "CGI (keyword or post-2005)"
        return "A15-1", "2", "hand-drawn"
    for a in r["linked_from"].split("; "):
        if a in CYCLE_ARTICLES:
            return CYCLE_ARTICLES[a], "3", f"linked from cycle article {a}"
    for leaf, wgs, kws in SIGNALS:
        if wg & {x.lower() for x in wgs} or kw & set(kws):
            return leaf, "3+", f"signal {leaf}"
    for a in r["linked_from"].split("; "):
        if a in MOVEMENT_ARTICLES:
            return MOVEMENT_ARTICLES[a], "3", f"linked from movement article {a}"
    order = [("Horror", "A4-3"), ("Sci-Fi", "A5-3"), ("Science Fiction", "A5-3"), ("Fantasy", "A6-1"), ("Western", "A17-1"),
             ("War", "A7-3"), ("History", "A7-4"), ("Biography", "A7-8"), ("Crime", "A2-4"), ("Thriller", "A3-9"),
             ("Mystery", "A3-2"), ("Action", "A8-2"), ("Adventure", "A6-2"), ("Musical", "A11-1"), ("Music", "A11-1"),
             ("Comedy", "A10-1"), ("Romance", "A9-1"), ("Sport", "A14-7"), ("Family", "A19-1")]
    for gg, leaf in order:
        if gg in g:
            if leaf == "A10-1" and "Drama" in g:
                leaf = "A10-2"
            if leaf == "A10-1" and "Romance" in g:
                leaf = "A9-2"
            return leaf, "fallback", f"genre {gg}"
    return "A14-5", "fallback", "drama"


def leaves_text():
    out = ["TAB KEY"] + [re.sub(r"<[^>]+>", "", k) for k in FT.FAMILY_KEY]
    for fam in FT.FAMILIES:
        if fam["code"] not in ("A", "B"):
            continue
        out.append(f"\n## {fam['code']} {fam['label']} — test: {fam['test']}")
        out += ["  key: " + re.sub(r"<[^>]+>", "", k) for k in fam["key"]]
        for s, lab, ax in fam["subs"]:
            out.append(f"### {s} {lab} — {ax}")
            for l in FT.LEAVES.get(s, []):
                out.append(f"{l[0]} {l[1]}: {re.sub(r'<[^>]+>', '', l[3])} [aka {l[4]}]")
    out.append("\nPRECEDENCE")
    out += [f"{c} {n}: {re.sub(r'<[^>]+>', '', s)}" for c, n, s in FT.PRECEDENCE]
    return "\n".join(out)


def batches():
    os.makedirs(R, exist_ok=True)
    replace = {r["tconst"] for r in rd(os.path.join(S, "film_replace.csv"))}
    pilot = {r["tconst"] for r in rd(os.path.join(ROOT, "taxonomy", "pilot", "japan_placements.csv"))} - replace
    REPLACE.update(replace)
    rows = [r for r in evidence() if r["tconst"] not in pilot]
    for r in rows:
        r["proposal"], r["rule_step"], r["rule_reason"] = propose(r)
    json.dump(Counter(r["proposal"] for r in rows), open(os.path.join(OUT, "rule_proposals.json"), "w"), indent=0)
    open(os.path.join(R, "ft_leaves.txt"), "w").write(leaves_text())
    # batch by first country, then year, so a reviewer sees one national cinema at a time
    rows.sort(key=lambda r: (r["countries"].split("|")[0] or "ZZ", int(r["year"] or 0), r["title"]))
    cols = ["tconst", "title", "year", "type", "runtime", "countries", "language", "director", "wd_genre", "wd_movement",
            "imdb_genres", "tmdb_genres", "linked_from", "based_on", "keywords", "overview", "proposal", "rule_reason"]
    n = 0
    for k in range(0, len(rows), BATCH):
        n += 1
        with open(os.path.join(R, f"films_{n:02d}.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows[k:k + BATCH])
    with open(os.path.join(OUT, "film_evidence.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols + ["rule_step", "enwiki"], extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "films in", n, "batches;", Counter(r["proposal"][:3] for r in rows).most_common(40))



def merge():
    """Pilot placements + reviewed batches + overrides → one row per film."""
    ev = {r["tconst"]: r for r in rd(os.path.join(OUT, "film_evidence.csv"))}
    wd = {r["tconst"]: r for r in rd(os.path.join(D, "film_wikidata.csv"))}
    replace = {r["tconst"] for r in rd(os.path.join(S, "film_replace.csv"))}
    names = {l[1]: l[0] for v in FT.LEAVES.values() for l in v if l[0].startswith("A1-")}
    rows = {}
    for r in rd(os.path.join(ROOT, "taxonomy", "pilot", "japan_placements.csv")):
        if r["tconst"] in replace:
            continue
        rows[r["tconst"]] = {"tconst": r["tconst"], "title": r["title"], "year": r["year"], "countries": r["countries"],
                             "director": r["director"], "leaf": r["leaf"], "see_also": r["see_also"], "key_step": r["key_step"],
                             "movement": names.get(r["movement"], r["movement"]), "confidence": "", "note": r["note"],
                             "by": r["by"] or "pilot"}
    missing = []
    for f in sorted(os.listdir(R)):
        if not re.match(r"films_\d+_out\.csv$", f):
            continue
        for r in rd(os.path.join(R, f)):
            e = ev.get(r["tconst"], {})
            rows[r["tconst"]] = {"tconst": r["tconst"], "title": e.get("title", r["title"]), "year": e.get("year", ""),
                                 "countries": e.get("countries", ""), "director": e.get("director", ""),
                                 "leaf": r["leaf"].strip(), "see_also": r.get("see_also", ""), "key_step": r.get("key_step", ""),
                                 "movement": r.get("movement", ""), "confidence": r.get("confidence", ""),
                                 "note": r.get("note", ""), "by": "review"}
    for r in rd(os.path.join(S, "film_overrides.csv")):
        if r["tconst"] in rows:
            rows[r["tconst"]].update({"leaf": r["leaf"], "see_also": r.get("see_also", ""), "note": r.get("note", ""), "by": "override"})
    for t, e in ev.items():
        if t not in rows:
            missing.append(t)
    for r in rows.values():
        r["qid"] = wd.get(r["tconst"], {}).get("qid", "")
    cols = ["tconst", "title", "year", "countries", "director", "qid", "leaf", "see_also", "key_step", "movement", "confidence", "note", "by"]
    with open(os.path.join(OUT, "film_placements.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(sorted(rows.values(), key=lambda r: (r["leaf"], r["year"])))
    known = {l[0] for v in FT.LEAVES.values() for l in v}
    bad = [r for r in rows.values() if not (r["leaf"] in known or r["leaf"].startswith(("route:", "exclude:")))]
    print(len(rows), "placed;", len(missing), "not yet reviewed;", len(bad), "with an unknown leaf",
          Counter(r["leaf"] for r in bad).most_common(10))


if __name__ == "__main__":
    {"batches": batches, "merge": merge}[sys.argv[1]]()
