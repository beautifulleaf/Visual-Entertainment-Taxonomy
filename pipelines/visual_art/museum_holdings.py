"""Open-access museum holdings per pooled artist (visual-art-plan.md §2.1 features).

Sources (downloaded once to data/raw/museums/):
  Met       MetObjects.csv (CC0). Carries the artist's Wikidata QID, so it joins
            directly; also gives Heilbrunn Timeline works ("Is Timeline Work")
            and highlights.
  AIC       the Art Institute of Chicago's full API data dump (CC0). Agents carry no
            QID or ULAN, so they are matched on normalised name + birth/death year.
  Cleveland Cleveland Museum of Art open-access API (CC0), matched the same way.

Output: data/interim/visual_art/holdings.csv with, per QID in any pool file:
  met_objects, met_timeline_works, met_highlights, aic_objects, cma_objects, n_museums

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

csv.field_size_limit(1 << 24)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw", "museums")
OUT_DIR = os.path.join(ROOT, "data", "interim", "visual_art")
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"

MET_URL = "https://media.githubusercontent.com/media/metmuseum/openaccess/master/MetObjects.csv"
AIC_URL = "https://artic-api-data.s3.amazonaws.com/artic-api-data.tar.bz2"
CMA_API = "https://openaccess-api.clevelandart.org/api/artworks/"


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


def met_counts():
    path = download(MET_URL, os.path.join(RAW, "MetObjects.csv"))
    objects, timeline, highlights = collections.Counter(), collections.Counter(), collections.Counter()
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            qids = {u.rsplit("/", 1)[-1] for u in row["Artist Wikidata URL"].split("|") if "/Q" in u}
            for q in qids:
                objects[q] += 1
                timeline[q] += row["Is Timeline Work"] == "True"
                highlights[q] += row["Is Highlight"] == "True"
    return objects, timeline, highlights


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
            skip = 0
            while True:
                url = f"{CMA_API}?limit=1000&skip={skip}&fields=id,creators"
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=300) as r:
                    data = json.load(r)["data"]
                if not data:
                    break
                for w in data:
                    out.write(json.dumps({"id": w["id"], "creators": w.get("creators") or []}) + "\n")
                skip += len(data)
                print(f"  Cleveland: {skip} artworks")
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
    pool = {}
    for path in glob.glob(os.path.join(OUT_DIR, "pool_*.csv")):
        with open(path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                pool[r["qid"]] = (r["label"], to_int(r["birth"]), to_int(r["death"]))
    return pool


def main():
    os.makedirs(RAW, exist_ok=True)
    pool = load_pools()
    print(f"{len(pool)} pooled artists")
    index = NameIndex(pool)
    met_obj, met_tl, met_hl = met_counts()
    aic = aic_counts(index)
    cma = cma_counts(index)
    out = os.path.join(OUT_DIR, "holdings.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["qid", "met_objects", "met_timeline_works", "met_highlights", "aic_objects", "cma_objects", "n_museums"])
        for q in sorted(pool):
            row = [met_obj[q], met_tl[q], met_hl[q], aic[q], cma[q]]
            w.writerow([q] + row + [sum(1 for v in (met_obj[q], aic[q], cma[q]) if v)])
    print("pooled artists held by: Met", sum(1 for q in pool if met_obj[q]), "· AIC", sum(1 for q in pool if aic[q]),
          "· Cleveland", sum(1 for q in pool if cma[q]), "· Met Timeline", sum(1 for q in pool if met_tl[q]))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
