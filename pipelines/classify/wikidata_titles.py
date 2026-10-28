"""Wikidata facts for selected titles, by IMDb ID (P345), via SPARQL.

Fetches genre (P136), director (P57), movement (P135), based on (P144),
country of origin (P495), production company (P272) and main subject (P921)
with English labels. Cached per batch in data/interim/wikidata_titles_raw.jsonl.

    python3 pipelines/classify/wikidata_titles.py film [--country JP]
    python3 pipelines/classify/wikidata_titles.py tv

Writes data/interim/<db>_wikidata.csv (one row per tconst; |-joined "QID:label").
"""
import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
D = os.path.join(ROOT, "data", "interim")
EP = "https://query.wikidata.org/sparql"
UA = "VisualEntertainmentTaxonomy/0.1 (research; classifying)"
PROPS = {"genre": "P136", "director": "P57", "movement": "P135", "based_on": "P144",
         "country": "P495", "company": "P272", "subject": "P921"}

Q = """SELECT ?imdb ?item ?itemLabel ?p ?v ?vLabel WHERE {
  VALUES ?imdb { %s }
  ?item wdt:P345 ?imdb .
  VALUES ?p { %s }
  OPTIONAL { ?item ?p ?v . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,ja,mul". }
}"""


def run(query):
    data = urllib.parse.urlencode({"query": query}).encode()
    for attempt in range(6):
        try:
            req = urllib.request.Request(EP, data=data, headers={"Accept": "application/sparql-results+json", "User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)["results"]["bindings"]
        except Exception as e:
            print("retry", attempt, e, file=sys.stderr)
            time.sleep(min(90, 5 * 2 ** attempt))
    sys.exit("SPARQL giving up")


def main():
    db = sys.argv[1]
    country = sys.argv[sys.argv.index("--country") + 1] if "--country" in sys.argv else None
    src = {"film": "film_selected.csv", "tv": "tv_selected.csv"}[db]
    rows = list(csv.DictReader(open(os.path.join(D, src))))
    if country:
        rows = [r for r in rows if country in (r.get("countries") or r.get("country") or "").split("|")]
    ids = [r["tconst"] for r in rows if r.get("tconst", "").startswith("tt")]
    cache = os.path.join(D, "wikidata_titles_raw.jsonl")
    done = set()
    if os.path.exists(cache):
        for line in open(cache):
            done.update(json.loads(line)["requested"])
    todo = [i for i in ids if i not in done]
    pv = " ".join("wdt:" + p for p in PROPS.values())
    with open(cache, "a") as out:
        for k in range(0, len(todo), 150):
            b = todo[k:k + 150]
            res = run(Q % (" ".join(f'"{i}"' for i in b), pv))
            out.write(json.dumps({"requested": b, "bindings": res}) + "\n")
            out.flush()
            print(f"{k + len(b)}/{len(todo)}", file=sys.stderr)
            time.sleep(1.5)
    inv = {"http://www.wikidata.org/prop/direct/" + p: name for name, p in PROPS.items()}
    facts = {}
    for line in open(cache):
        for b in json.loads(line)["bindings"]:
            t = b["imdb"]["value"]
            f = facts.setdefault(t, {"tconst": t, "qid": b["item"]["value"].rsplit("/", 1)[1], **{n: [] for n in PROPS}})
            if "v" in b and b.get("p"):
                name = inv.get(b["p"]["value"])
                val = b["v"]["value"].rsplit("/", 1)[1] + ":" + b.get("vLabel", {}).get("value", "")
                if name and val not in f[name]:
                    f[name].append(val)
    out = os.path.join(D, f"{db}_wikidata.csv")
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["tconst", "qid", *PROPS])
        w.writeheader()
        for t in sorted(facts):
            w.writerow({k: ("|".join(v) if isinstance(v, list) else v) for k, v in facts[t].items()})
    print(f"{len(facts)} titles with a Wikidata item", file=sys.stderr)


if __name__ == "__main__":
    main()
