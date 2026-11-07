"""Fetch the reference universes for the VA coverage crosswalk (owner, 2026-11-07: "this is humanity's entire history
of visual artistic expression"; measure the tree against an independent reference, not only against what was gathered).

  aat_styles.json   Getty AAT Styles and Periods facet (aat:300015646): every concept and guide term below it, with its
                    English preferred label, alternative labels, preferred parent and estimated start/end dates
  wd_ich.json       UNESCO Intangible Cultural Heritage elements (Wikidata items with that heritage designation)
  wd_styles.json    Wikidata art movements and art styles that have an English Wikipedia article

Run: python3 pipelines/r3/ref_fetch.py   (writes data/reference/, gitignored; the crosswalk output is committed)
"""
import json, os, time, urllib.parse, urllib.request
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
OUT = os.path.join(ROOT, "data", "reference")
UA = "VE-Taxonomy-coverage/1.0 (research; taxonomy completeness check)"


def sparql(endpoint, q):
    url = endpoint + "?" + urllib.parse.urlencode({"query": q, "format": "json"})
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
            return json.load(urllib.request.urlopen(req, timeout=180))["results"]["bindings"]
        except Exception as e:
            err = e; time.sleep(5 * (i + 1))
    raise err


def aat():
    q = """PREFIX gvp: <http://vocab.getty.edu/ontology#> PREFIX xl: <http://www.w3.org/2008/05/skos-xl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#> PREFIX aat: <http://vocab.getty.edu/aat/>
SELECT ?c ?type ?label ?parent ?start ?end (GROUP_CONCAT(DISTINCT ?alt; separator="|") AS ?alts) WHERE {
  ?c gvp:broaderExtended aat:300015646 ; a ?type ; gvp:broaderPreferred ?parent .
  FILTER(?type IN (gvp:Concept, gvp:GuideTerm))
  OPTIONAL { ?c gvp:prefLabelGVP/xl:literalForm ?label }
  OPTIONAL { ?c xl:altLabel/xl:literalForm ?alt . FILTER(langMatches(lang(?alt), "en")) }
  OPTIONAL { ?c gvp:estStart ?start } OPTIONAL { ?c gvp:estEnd ?end }
} GROUP BY ?c ?type ?label ?parent ?start ?end"""
    rows = sparql("https://vocab.getty.edu/sparql.json", q)
    out = [{"id": r["c"]["value"].rsplit("/", 1)[1], "guide": r["type"]["value"].endswith("GuideTerm"),
            "label": r.get("label", {}).get("value", ""), "parent": r["parent"]["value"].rsplit("/", 1)[1],
            "start": r.get("start", {}).get("value"), "end": r.get("end", {}).get("value"),
            "alts": [a for a in r.get("alts", {}).get("value", "").split("|") if a]} for r in rows]
    json.dump(out, open(os.path.join(OUT, "aat_styles.json"), "w"), ensure_ascii=False)
    return len(out)


def wd(q, name):
    rows = sparql("https://query.wikidata.org/sparql", q)
    json.dump([{k: v["value"] for k, v in r.items()} for r in rows], open(os.path.join(OUT, name), "w"), ensure_ascii=False)
    return len(rows)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("aat", aat())
    print("ich", wd("""SELECT ?x ?xLabel ?xDescription ?list (SAMPLE(?cl) AS ?countryLabel) WHERE {
  ?x wdt:P1435 ?list . ?list rdfs:label ?ll . FILTER(lang(?ll)="en" && CONTAINS(?ll, "Intangible Cultural Heritage"))
  OPTIONAL { ?x wdt:P17 ?c . ?c rdfs:label ?cl . FILTER(lang(?cl)="en") }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } } GROUP BY ?x ?xLabel ?xDescription ?list""", "wd_ich.json"))
    print("styles", wd("""SELECT ?x ?xLabel ?xDescription ?article (SAMPLE(?cl) AS ?countryLabel) WHERE {
  VALUES ?cls { wd:Q968159 wd:Q1792644 } ?x wdt:P31 ?cls .
  ?article schema:about ?x ; schema:isPartOf <https://en.wikipedia.org/> .
  OPTIONAL { ?x wdt:P495 ?c . ?c rdfs:label ?cl . FILTER(lang(?cl)="en") }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } } GROUP BY ?x ?xLabel ?xDescription ?article""", "wd_styles.json"))
