"""Open-access museum holdings per pooled artist (visual-art-plan.md §2.1 features).

Sources (downloaded once to data/raw/museums/):
  Met       MetObjects.csv (CC0). Carries the artist's Wikidata QID, so it joins
            directly; also gives Heilbrunn Timeline works ("Is Timeline Work")
            and highlights.
  AIC       the Art Institute of Chicago's full API data dump (CC0). Agents carry no
            QID or ULAN, so they are matched on normalised name + birth/death year.
  Cleveland Cleveland Museum of Art open-access API (CC0), matched the same way.

  East Asia the East Asia sweep (pipelines/regional/east_asia.py ->
            data/interim/regional/east_asia_artists.csv: ColBase, designated
            properties, NPM, e-Museum), reused rather than refetched. Its makers
            carry no QID; they are matched on their original-script name against the
            Chinese/Japanese/Korean Wikidata labels of East Asian pooled artists
            (cached), then on romanised name + birth year. Cleveland and AIC objects
            are subtracted (counted above).

Met objects without an artist QID made before 1500 ("Attributed to the Berlin
Painter") are matched on the display name to pooled pre-1500 artists, when the
name is unique among them.

Output: data/interim/visual_art/holdings.csv with, per QID in any pool file:
  met_objects, met_timeline_works, met_highlights, aic_objects, cma_objects, eastasia_objects
A source added here as <key>_objects becomes usable by any region that lists
<key> in its `collections` (regions.py); regional collections (ColBase, the
National Palace Museum, the National Museum of Asian Art, ...) slot in this way.

Usage: python3 pipelines/visual_art/museum_holdings.py
"""
import collections
import csv
import glob
import json
import os
import re
import tarfile
import time
import unicodedata
import urllib.request
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wikidata import sparql  # noqa: E402

csv.field_size_limit(1 << 24)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw", "museums")
EAST_ASIA_ARTISTS = os.path.join(ROOT, "data", "interim", "regional", "east_asia_artists.csv")
CJK_LABELS = os.path.join(ROOT, "data", "raw", "wikidata", "pool", "cjk_labels.json")
CJK_LANGS = ["zh", "zh-hant", "zh-hans", "zh-tw", "zh-hk", "zh-cn", "lzh", "ja", "ko"]
OUT_DIR = os.path.join(ROOT, "data", "interim", "visual_art")
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"

MET_URL = "https://media.githubusercontent.com/media/metmuseum/openaccess/master/MetObjects.csv"
AIC_URL = "https://artic-api-data.s3.amazonaws.com/artic-api-data.tar.bz2"
CMA_API = "https://openaccess-api.clevelandart.org/api/artworks/"
CMA_PAGE = 1000


def download(url, path):
    if not os.path.exists(path):
        print(f"downloading {url}")
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=600) as r, open(path + ".part", "wb") as f:
            while chunk := r.read(1 << 20):
                f.write(chunk)
        os.replace(path + ".part", path)
    return path


def norm(name):
    s = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\(.*?\)", " ", s)
    return " ".join(re.sub(r"[^a-z ]", " ", s).split())


def to_int(v):
    try:
        return int(str(v).strip()[:5])
    except ValueError:
        return None


class NameIndex:
    """Matches museum creator records to pooled artists on name + life dates."""

    def __init__(self, pool):
        self.full, self.last = collections.defaultdict(set), collections.defaultdict(set)
        for q, (label, birth, death) in pool.items():
            n = norm(label)
            if not n:
                continue
            self.full[(n, birth)].add(q)
            if birth is not None and death is not None:
                self.last[(n.split()[-1], birth, death)].add(q)

    def match(self, names, birth, death):
        for name in names:
            n = norm(name)
            if not n or birth is None:
                continue
            for b in (birth, birth - 1, birth + 1):
                hits = self.full.get((n, b))
                if hits and len(hits) == 1:
                    return next(iter(hits))
            if death is not None:
                hits = self.last.get((n.split()[-1], birth, death))
                if hits and len(hits) == 1:
                    return next(iter(hits))
        return None


def met_counts(early_names=None):
    """Per-QID Met counts. early_names: {normalised name: QID} for pre-1500 pooled
    artists with a unique name, used for objects made before 1500 whose artist has
    no Wikidata link ("Attributed to the Berlin Painter")."""
    path = download(MET_URL, os.path.join(RAW, "MetObjects.csv"))
    objects, timeline, highlights = collections.Counter(), collections.Counter(), collections.Counter()
    by_name = 0
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            qids = {u.rsplit("/", 1)[-1] for u in row["Artist Wikidata URL"].split("|") if "/Q" in u}
            if not qids and early_names and row["Artist Display Name"] and (to_int(row["Object End Date"]) or 9999) < 1500:
                qids = {early_names[n] for n in map(norm, row["Artist Display Name"].split("|")) if n in early_names}
                by_name += bool(qids)
            for q in qids:
                objects[q] += 1
                timeline[q] += row["Is Timeline Work"] == "True"
                highlights[q] += row["Is Highlight"] == "True"
    print(f"  Met: {by_name} pre-1500 objects matched by artist name (no Wikidata link)")
    return objects, timeline, highlights


def early_name_index(pool, active_start):
    """{normalised label: QID} for pooled artists active before 1500 whose name is unique there."""
    names = collections.defaultdict(set)
    for q, (label, _, _) in pool.items():
        if active_start.get(q) is not None and active_start[q] < 1500 and norm(label):
            names[re.sub(r"^the ", "", norm(label))].add(q)
    return {n: next(iter(qs)) for n, qs in names.items() if len(qs) == 1}


def cjk_labels(qids):
    """Chinese/Japanese/Korean labels per QID (cached), for matching the East Asia sweep."""
    known = json.load(open(CJK_LABELS, encoding="utf-8")) if os.path.exists(CJK_LABELS) else {}
    todo = [q for q in qids if q not in known]
    langs = ", ".join(f'"{lang}"' for lang in CJK_LANGS)
    for i in range(0, len(todo), 250):
        chunk = todo[i:i + 250]
        for q in chunk:
            known[q] = []
        values = " ".join("wd:" + q for q in chunk)
        for r in sparql(f"""SELECT ?p ?l WHERE {{ VALUES ?p {{ {values} }}
              {{ ?p rdfs:label ?l }} UNION {{ ?p skos:altLabel ?l }} FILTER(LANG(?l) IN ({langs})) }}"""):
            if r["l"] not in known[r["p"]]:
                known[r["p"]].append(r["l"])
        json.dump(known, open(CJK_LABELS, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"  CJK labels: {min(i + 250, len(todo))}/{len(todo)}")
    return known


def cjk_norm(name):
    return re.sub(r"[\s　・·]|[(（].*?[)）]", "", name or "")


def east_asia_counts(pool, ea_qids):
    """Objects per QID from the East Asia sweep, minus its Cleveland and AIC objects."""
    if not os.path.exists(EAST_ASIA_ARTISTS):
        print("  East Asia sweep: no east_asia_artists.csv, skipped")
        return collections.Counter()
    labels = cjk_labels(sorted(ea_qids))
    native = collections.defaultdict(set)
    for q in ea_qids:
        for lab in labels.get(q, []):
            native[cjk_norm(lab)].add(q)
    roman = collections.defaultdict(set)
    for q in ea_qids:
        roman[norm(pool[q][0])].add(q)
    counts, matched = collections.Counter(), 0
    with open(EAST_ASIA_ARTISTS, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            names = {cjk_norm(n) for n in [r["artist_original"]] + re.split(r"[;|,、]", r["other_names"]) if cjk_norm(n)}
            hits = set().union(*(native.get(n, set()) for n in names)) if names else set()
            birth = to_int(r["birth_year"])
            if len(hits) > 1 and birth is not None:
                hits = {q for q in hits if pool[q][1] is not None and abs(pool[q][1] - birth) <= 2}
            if not hits and birth is not None and r["artist_romanised"]:
                hits = {q for q in roman.get(norm(r["artist_romanised"]), set())
                        if pool[q][1] is not None and abs(pool[q][1] - birth) <= 2}
            if len(hits) == 1:
                n = int(r["objects_total"] or 0) - int(r["objects_cma"] or 0) - int(r["objects_aic"] or 0)
                counts[next(iter(hits))] += max(n, 0)
                matched += 1
    print(f"  East Asia sweep: {matched} makers matched to {len(counts)} pooled artists")
    return counts


def aic_counts(index):
    path = download(AIC_URL, os.path.join(RAW, "artic-api-data.tar.bz2"))
    base = os.path.join(RAW, "aic", "artic-api-data", "json")
    if not os.path.isdir(base):
        print("extracting AIC dump")
        with tarfile.open(path) as t:
            t.extractall(os.path.join(RAW, "aic"), filter="data")
    agent_qid = {}
    for p in glob.glob(os.path.join(base, "agents", "*.json")):
        a = json.load(open(p, encoding="utf-8"))
        q = index.match([a.get("title")] + (a.get("alt_titles") or []), to_int(a.get("birth_date")), to_int(a.get("death_date")))
        if q:
            agent_qid[a["id"]] = q
    counts = collections.Counter()
    for p in glob.glob(os.path.join(base, "artworks", "*.json")):
        w = json.load(open(p, encoding="utf-8"))
        for q in {agent_qid[i] for i in w.get("artist_ids") or [] if i in agent_qid}:
            counts[q] += 1
    print(f"  AIC: {len(agent_qid)} agents matched to pooled artists")
    return counts


def cma_records():
    path = os.path.join(RAW, "cma_creators.jsonl")
    if not os.path.exists(path):
        with open(path + ".part", "w", encoding="utf-8") as out:
            # Advance by the page size, not by len(data): some pages come back one
            # short, and requesting the "missing" offset returns total=0 and no data.
            skip, total, seen = 0, 0, set()
            while skip == 0 or skip < total:
                url = f"{CMA_API}?limit={CMA_PAGE}&skip={skip}&fields=id,creators"
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=300) as r:
                    page = json.load(r)
                total = max(total, page["info"].get("total") or 0)
                for w in page["data"]:
                    if w["id"] not in seen:
                        seen.add(w["id"])
                        out.write(json.dumps({"id": w["id"], "creators": w.get("creators") or []}) + "\n")
                skip += CMA_PAGE
                print(f"  Cleveland: {len(seen)} of {total} artworks")
                time.sleep(1)
        os.replace(path + ".part", path)
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def cma_counts(index):
    counts, creator_qid = collections.Counter(), {}
    for w in cma_records():
        qs = set()
        for c in w["creators"]:
            if c["id"] not in creator_qid:
                name = (c.get("description") or "").split(" (", 1)[0]
                creator_qid[c["id"]] = index.match([name], to_int(c.get("birth_year")), to_int(c.get("death_year")))
            if creator_qid[c["id"]]:
                qs.add(creator_qid[c["id"]])
        for q in qs:
            counts[q] += 1
    print(f"  Cleveland: {sum(1 for v in creator_qid.values() if v)} creators matched to pooled artists")
    return counts


def load_pools():
    """{qid: (label, birth, death)}, {qid: active_start}, and the QIDs in East Asian pools."""
    pool, active_start, east_asia = {}, {}, set()
    for path in glob.glob(os.path.join(OUT_DIR, "pool_*.csv")):
        with open(path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                pool[r["qid"]] = (r["label"], to_int(r["birth"]), to_int(r["death"]))
                if r.get("active_start"):
                    active_start[r["qid"]] = int(float(r["active_start"]))
                if "east_asia" in os.path.basename(path):
                    east_asia.add(r["qid"])
    return pool, active_start, east_asia


def main():
    os.makedirs(RAW, exist_ok=True)
    pool, active_start, east_asia = load_pools()
    print(f"{len(pool)} pooled artists")
    index = NameIndex(pool)
    met_obj, met_tl, met_hl = met_counts(early_name_index(pool, active_start))
    aic = aic_counts(index)
    cma = cma_counts(index)
    ea = east_asia_counts(pool, east_asia)
    out = os.path.join(OUT_DIR, "holdings.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["qid", "met_objects", "met_timeline_works", "met_highlights", "aic_objects", "cma_objects", "eastasia_objects"])
        for q in sorted(pool):
            w.writerow([q, met_obj[q], met_tl[q], met_hl[q], aic[q], cma[q], ea[q]])
    print("pooled artists held by: Met", sum(1 for q in pool if met_obj[q]), "· AIC", sum(1 for q in pool if aic[q]),
          "· Cleveland", sum(1 for q in pool if cma[q]), "· Met Timeline", sum(1 for q in pool if met_tl[q]))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
