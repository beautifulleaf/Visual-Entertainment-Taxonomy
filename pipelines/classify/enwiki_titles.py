"""English Wikipedia article titles for selected titles, by IMDb ID (P345).

Used to match titles against the links of movement and cycle articles
(movement_article_links.json), which attests membership.

    python3 pipelines/classify/enwiki_titles.py film|tv

Writes data/interim/<db>_enwiki.csv: tconst, qid, enwiki.
"""
import csv
import os
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(__file__))
from attest import _run  # noqa: E402

D = os.path.join(os.path.dirname(__file__), "..", "..", "data", "interim")
Q = """SELECT ?imdb ?item ?art WHERE {
  VALUES ?imdb { %s }
  ?item wdt:P345 ?imdb .
  ?art schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> .
}"""


def main(db):
    src = {"film": "film_selected.csv", "tv": "tv_selected.csv"}[db]
    ids = [r["tconst"] for r in csv.DictReader(open(os.path.join(D, src))) if r["tconst"].startswith("tt")]
    if db == "film":
        add = os.path.join(D, "..", "..", "seeds", "classify", "film_additions.csv")
        ids += [r["tconst"] for r in csv.DictReader(open(add))]
    out = {}
    for k in range(0, len(ids), 250):
        for b in _run(Q % " ".join(f'"{i}"' for i in ids[k:k + 250])):
            out[b["imdb"]["value"]] = (b["item"]["value"].rsplit("/", 1)[1],
                                       urllib.parse.unquote(b["art"]["value"].rsplit("/", 1)[1]).replace("_", " "))
        print(f"{k + 250}/{len(ids)}", file=sys.stderr)
        time.sleep(1)
    with open(os.path.join(D, f"{db}_enwiki.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tconst", "qid", "enwiki"])
        for t in ids:
            if t in out:
                w.writerow([t, *out[t]])
    print(f"{len(out)} of {len(ids)} with an English article", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1])
