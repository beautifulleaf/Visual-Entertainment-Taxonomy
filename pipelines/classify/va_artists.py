"""Selected artists of the Visual Art tab, unioned by QID, with their movements.

Sources: the four final artist selections (Europe 1400–1900, modern 1860–1960 by
region, pre-1400 eras, contemporary incl. list-only names). Region and era come
from the coverage audit's placement (taxonomy/visual_art/pool_people.csv, built
by va_pool.py). Movements (P135) and occupations are fetched fresh for every QID
from Wikidata (SPARQL), with English labels; cached in
data/interim/va_artist_movements.json.

    python3 pipelines/classify/va_artists.py

Writes taxonomy/visual_art/artists.csv: qid, label, birth, medium, media,
region, era, sources, movements (QID:label|...), contemporary list key.
"""
import csv
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from attest import _run  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
D = os.path.join(ROOT, "data", "interim")
VA = os.path.join(D, "visual_art")
OUT = os.path.join(ROOT, "taxonomy", "visual_art")
CACHE = os.path.join(D, "va_artist_movements.json")


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8"))) if os.path.exists(p) else []


def main():
    art = {}

    def add(qid, label, birth, medium, media, source):
        a = art.setdefault(qid, {"qid": qid, "label": label, "birth": birth, "medium": medium, "media": media, "sources": []})
        a["label"] = a["label"] or label
        a["birth"] = a["birth"] or birth
        a["medium"] = a["medium"] or medium
        a["media"] = a["media"] or media
        if source not in a["sources"]:
            a["sources"].append(source)

    pool = {r["qid"]: r for r in rd(os.path.join(VA, "pool_europe_1400-1900.csv"))}
    for r in rd(os.path.join(VA, "scores_europe_1400-1900.csv")):
        if r["selected"] in ("1", "True"):
            p = pool.get(r["qid"], {})
            add(r["qid"], r["label"], r["birth"], r["medium"], p.get("media", ""), "europe_1400-1900")
    for path in sorted(glob.glob(os.path.join(VA, "scores_modern_*.csv"))):
        key = os.path.basename(path)[len("scores_modern_"):-4]
        pool = {r["qid"]: r for r in rd(os.path.join(VA, f"pool_modern_{key}.csv"))}
        for r in rd(path):
            if r["selected"] in ("1", "True"):
                add(r["qid"], r["label"], r["birth"], r["medium"], pool.get(r["qid"], {}).get("media", ""), "modern_" + key)
    for key in ("antiquity_mediterranean", "europe_medieval_500-1400", "east_asia_pre1400", "islamic_pre1400"):
        for r in rd(os.path.join(VA, f"scores_{key}_era.csv")):
            if r["final"] in ("1", "True"):
                add(r["qid"], r["label"], r["birth"], r["medium"], "", "pre1400_" + key)
    cpool = {}
    for n in ("contemporary_pool.csv", "contemporary_pool_additions.csv"):
        for r in rd(os.path.join(D, n)):
            cpool.setdefault(r["qid"], r)
    for r in rd(os.path.join(D, "contemporary_scores.csv")):
        if r["selected"] == "1":
            p = cpool.get(r["qid"], {})
            add(r["qid"] or r["key"], r["label"], p.get("birth", ""), r["medium"], p.get("media", ""), "contemporary")
    place = {}
    for r in rd(os.path.join(OUT, "pool_people.csv")):
        if r["kind"] == "artist":
            place.setdefault(r["key"], (r["region"], r["era"]))
    qids = sorted(q for q in art if q.startswith("Q"))
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    todo = [q for q in qids if q not in cache]
    Q = """SELECT ?a ?m ?mLabel WHERE { VALUES ?a { %s } OPTIONAL { ?a wdt:P135 ?m . }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }"""
    for k in range(0, len(todo), 300):
        b = todo[k:k + 300]
        for q in b:
            cache.setdefault(q, [])
        for x in _run(Q % " ".join("wd:" + q for q in b)):
            q = x["a"]["value"].rsplit("/", 1)[1]
            if "m" in x:
                v = x["m"]["value"].rsplit("/", 1)[1] + ":" + x.get("mLabel", {}).get("value", "")
                if v not in cache[q]:
                    cache[q].append(v)
        json.dump(cache, open(CACHE, "w"))
        print(f"{k + len(b)}/{len(todo)}", file=sys.stderr)
        time.sleep(1)
    with open(os.path.join(OUT, "artists.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["qid", "label", "birth", "medium", "media", "region", "era", "sources", "movements"])
        w.writeheader()
        for q, a in sorted(art.items()):
            reg, era = place.get(q, ("", ""))
            w.writerow({**a, "sources": "|".join(a["sources"]), "region": reg, "era": era, "movements": "|".join(cache.get(q, []))})
    print(len(art), "artists", file=sys.stderr)


if __name__ == "__main__":
    main()
