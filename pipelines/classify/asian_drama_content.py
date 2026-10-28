"""Content features for the Asian drama selection, via MDBList search.

MyDramaList refuses this cloud IP (403), and only ~600 selected dramas carry an
IMDb ID, so each drama is looked up by title and year with MDBList's search
(first the English title, then the native title), keeping a hit within one year.
The IMDb or TMDB ID it returns feeds the same batch call as content_features.py
(TMDB keywords, overview, genres). Searches and batches are cached.

    python3 pipelines/classify/asian_drama_content.py

Writes data/interim/asian_drama_content.csv: mdl_id, imdb, tmdb, matched_title,
keywords, overview, genres, language.
"""
import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.mdblist import api_key, items_of, UA, MIN_INTERVAL  # noqa: E402

D = os.path.join(os.path.dirname(__file__), "..", "..", "data", "interim")
SEARCH = os.path.join(D, "asian_drama_search.jsonl")
RAW = os.path.join(D, "asian_drama_content_raw.jsonl")


def get(url, body=None):
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, data=body, headers={"User-Agent": UA, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            print("retry", attempt, e, file=sys.stderr)
            time.sleep(min(60, 3 * 2 ** attempt))
    return None


def main():
    key = api_key()
    sel = list(csv.DictReader(open(os.path.join(D, "asian_drama_selected.csv"))))
    done = {}
    if os.path.exists(SEARCH):
        for line in open(SEARCH):
            j = json.loads(line)
            done[j["mdl_id"]] = j
    def search(r):
            hit = None
            for q in (r["title"], r["native_title"]):
                if not q:
                    continue
                res = get("https://api.mdblist.com/search/show?" + urllib.parse.urlencode({"query": q, "apikey": key})) or {}
                time.sleep(MIN_INTERVAL)
                for s in res.get("search", []):
                    if s.get("year") and r["year"] and abs(int(s["year"]) - int(r["year"])) <= 1:
                        hit = {"title": s["title"], "imdb": s["ids"].get("imdbid"), "tmdb": s["ids"].get("tmdbid")}
                        break
                if hit:
                    break
            return {"mdl_id": r["mdl_id"], "hit": hit}

    todo = [r for r in sel if r["mdl_id"] not in done]
    with open(SEARCH, "a") as out, ThreadPoolExecutor(4) as ex:  # four requests in flight, each paced
        for i, j in enumerate(ex.map(search, todo)):
            done[j["mdl_id"]] = j
            out.write(json.dumps(j, ensure_ascii=False) + "\n")
            out.flush()
            if i % 200 == 0:
                print(i, len(todo), file=sys.stderr)
    tmdb = sorted({j["hit"]["tmdb"] for j in done.values() if j["hit"] and j["hit"].get("tmdb")})
    have = set()
    if os.path.exists(RAW):
        for line in open(RAW):
            have.update(json.loads(line)["requested"])
    todo = [t for t in tmdb if t not in have]
    with open(RAW, "a") as out:
        for k in range(0, len(todo), 200):
            b = todo[k:k + 200]
            resp = get(f"https://api.mdblist.com/tmdb/show?apikey={key}",
                       json.dumps({"ids": b, "append_to_response": ["keyword"]}).encode())
            out.write(json.dumps({"requested": b, "response": resp}) + "\n")
            out.flush()
            time.sleep(MIN_INTERVAL)
    info = {}
    for line in open(RAW):
        for it in items_of(json.loads(line)["response"] or []):
            t = (it.get("ids") or {}).get("tmdb")
            kw = [k.get("name") if isinstance(k, dict) else k for k in it.get("keywords") or []]
            info[t] = {"keywords": "|".join(k for k in kw if k), "overview": (it.get("description") or "").replace("\n", " "),
                       "genres": "|".join(g.get("title", "") for g in it.get("genres") or [] if isinstance(g, dict)),
                       "language": it.get("language") or ""}
    with open(os.path.join(D, "asian_drama_content.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["mdl_id", "imdb", "tmdb", "matched_title", "keywords", "overview", "genres", "language"])
        w.writeheader()
        for r in sel:
            h = done[r["mdl_id"]]["hit"]
            if not h:
                continue
            w.writerow({"mdl_id": r["mdl_id"], "imdb": h.get("imdb") or "", "tmdb": h.get("tmdb") or "",
                        "matched_title": h["title"], **info.get(h.get("tmdb"), {})})
    print(sum(1 for j in done.values() if j["hit"]), "of", len(sel), "matched;", len(info), "with content", file=sys.stderr)


if __name__ == "__main__":
    main()
