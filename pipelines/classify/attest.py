"""Trace node names to Wikidata: label or alias match, best item by sitelinks.

Used for leaves (attest strings) and for genre leaves in Film & TV. Each attest
string may hold several candidate names separated by "|"; the first that
resolves wins. Results are cached in data/interim/attest_cache.json.

    from attest import resolve
    resolve(["Mina'i ware", "Kufic"]) -> {name: {qid, label, sitelinks, enwiki}}
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
CACHE = os.path.join(ROOT, "data", "interim", "attest_cache.json")
EP = "https://query.wikidata.org/sparql"
UA = "VisualEntertainmentTaxonomy/0.1 (research; classifying)"

Q = """SELECT ?s ?item ?itemLabel ?sl ?art WHERE {
  VALUES ?s { %s }
  ?item %s ?s .
  ?item wikibase:sitelinks ?sl .
  OPTIONAL { ?art schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}"""


def _run(query):
    data = urllib.parse.urlencode({"query": query}).encode()
    for attempt in range(6):
        try:
            req = urllib.request.Request(EP, data=data, headers={"Accept": "application/sparql-results+json", "User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)["results"]["bindings"]
        except Exception as e:
            print("retry", attempt, e, file=sys.stderr)
            time.sleep(min(90, 5 * 2 ** attempt))
    raise SystemExit("SPARQL giving up")


def _lit(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"@en'


def resolve(names):
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    todo = sorted({n for n in names if n and n not in cache})
    variants = {}
    for n in todo:
        for v in {n, n[0].lower() + n[1:], n[0].upper() + n[1:]}:
            variants.setdefault(v, n)
    vs = sorted(variants)
    for pred in ("rdfs:label", "skos:altLabel"):
        for k in range(0, len(vs), 60):
            chunk = [v for v in vs[k:k + 60] if variants[v] not in cache or cache[variants[v]] is None]
            if not chunk:
                continue
            for b in _run(Q % (" ".join(_lit(v) for v in chunk), pred)):
                n = variants[b["s"]["value"]]
                cand = {"qid": b["item"]["value"].rsplit("/", 1)[1], "label": b.get("itemLabel", {}).get("value", ""),
                        "sitelinks": int(b["sl"]["value"]),
                        "enwiki": urllib.parse.unquote(b["art"]["value"].rsplit("/", 1)[1]).replace("_", " ") if "art" in b else "",
                        "via": pred}
                cur = cache.get(n)
                if cur is None or (cur.get("via") == pred and cand["sitelinks"] > cur["sitelinks"]):
                    cache[n] = cand
            time.sleep(1)
        for n in todo:
            cache.setdefault(n, None)
    json.dump(cache, open(CACHE, "w"), ensure_ascii=False, indent=0)
    return {n: cache.get(n) for n in names}


QT = """SELECT ?s ?item ?itemLabel ?sl WHERE {
  VALUES ?s { %s }
  ?art schema:name ?s ; schema:isPartOf <https://en.wikipedia.org/> ; schema:about ?item .
  ?item wikibase:sitelinks ?sl .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}"""

QD = """SELECT ?item ?itemLabel ?d WHERE {
  VALUES ?item { %s }
  OPTIONAL { ?item schema:description ?d . FILTER(lang(?d)="en") }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}"""


def by_enwiki(titles):
    """Resolve English Wikipedia article titles to items (exact title)."""
    out = {}
    for k in range(0, len(titles), 60):
        for b in _run(QT % " ".join(_lit(t) for t in titles[k:k + 60])):
            out[b["s"]["value"]] = {"qid": b["item"]["value"].rsplit("/", 1)[1], "label": b.get("itemLabel", {}).get("value", ""),
                                    "sitelinks": int(b["sl"]["value"]), "enwiki": b["s"]["value"], "via": "enwiki"}
    return out


def describe(qids):
    out = {}
    for k in range(0, len(qids), 150):
        for b in _run(QD % " ".join("wd:" + q for q in qids[k:k + 150])):
            out[b["item"]["value"].rsplit("/", 1)[1]] = (b.get("itemLabel", {}).get("value", ""), b.get("d", {}).get("value", ""))
    return out
