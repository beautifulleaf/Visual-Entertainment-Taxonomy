"""Content features for genre placement: TMDB keywords and overview via MDBList.

MDBList's batch Media Info endpoint returns TMDB keywords when asked with
append_to_response=["keyword"], plus TMDB's plot overview (`description`) and
production companies. This closes the gathering gap noted in
docs/classifying-plan.md. Raw responses are cached (one JSON line per batch),
so an interrupted run resumes.

    python3 pipelines/classify/content_features.py film   # film_selected.csv
    python3 pipelines/classify/content_features.py show   # tv_selected.csv

Writes data/interim/<db>_content.csv: tconst, keywords (|-joined), overview,
companies, genres, language, spoken.
"""
import csv
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.mdblist import api_key, items_of, UA, MIN_INTERVAL  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
D = os.path.join(ROOT, "data", "interim")


def post(key, ids, kind):
    body = json.dumps({"ids": ids, "append_to_response": ["keyword"]}).encode()
    url = f"https://api.mdblist.com/imdb/{kind}?apikey={key}"
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except Exception as e:  # rate limits and transient errors: back off
            print("retry", attempt, e, file=sys.stderr)
            time.sleep(min(60, 2 ** attempt * 3))
    sys.exit("giving up")


def main(kind):
    src = {"movie": "film_selected.csv", "show": "tv_selected.csv"}[kind]
    db = {"movie": "film", "show": "tv"}[kind]
    ids = [r["tconst"] for r in csv.DictReader(open(os.path.join(D, src))) if r.get("tconst", "").startswith("tt")]
    cache = os.path.join(D, f"{db}_content_raw.jsonl")
    done = set()
    if os.path.exists(cache):
        for line in open(cache):
            done.update(json.loads(line)["requested"])
    todo = [i for i in ids if i not in done]
    key = api_key()
    with open(cache, "a") as out:
        for k in range(0, len(todo), 200):
            batch = todo[k:k + 200]
            resp = post(key, batch, kind)
            out.write(json.dumps({"requested": batch, "response": resp}) + "\n")
            out.flush()
            print(f"{k + len(batch)}/{len(todo)}", file=sys.stderr)
            time.sleep(MIN_INTERVAL)
    rows = {}
    for line in open(cache):
        for it in items_of(json.loads(line)["response"]):
            t = (it.get("ids") or {}).get("imdb")
            if not t:
                continue
            kw = []
            for k in it.get("keywords") or []:
                n = k.get("name") if isinstance(k, dict) else k
                if n and n not in kw and n != "has-trailer":
                    kw.append(n)
            rows[t] = {
                "tconst": t,
                "keywords": "|".join(kw),
                "overview": (it.get("description") or "").replace("\n", " "),
                "companies": "|".join(c.get("name", "") for c in it.get("production_companies") or [] if isinstance(c, dict)),
                "genres": "|".join(g.get("title", "") for g in it.get("genres") or [] if isinstance(g, dict)),
                "language": it.get("language") or "",
                "spoken": it.get("spoken_language") or "",
            }
    with open(os.path.join(D, f"{db}_content.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["tconst", "keywords", "overview", "companies", "genres", "language", "spoken"])
        w.writeheader()
        for t in ids:
            if t in rows:
                w.writerow(rows[t])
    print(f"{len(rows)} of {len(ids)} with a record; {sum(1 for r in rows.values() if r['keywords'])} with keywords", file=sys.stderr)


if __name__ == "__main__":
    main({"film": "movie", "tv": "show", "movie": "movie", "show": "show"}[sys.argv[1]])
