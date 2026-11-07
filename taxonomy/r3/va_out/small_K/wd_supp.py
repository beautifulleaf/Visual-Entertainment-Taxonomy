"""Supplementary Wikidata catalogues for leaves the gathered CSVs barely cover (same inclusion rule)."""
import json, time
from wdq import sparql
# code: [(section label, triple pattern on ?i, extra filter)]
JOBS = {
 "K4-12": [("Painted churches and monasteries of Moldavia", "?i wdt:P361 wd:Q387687 .", "")],
 "K7-15": [("Stepwells", "?i wdt:P31 wd:Q1473950 .", "")],
 "K7-18": [("Havelis", "?i wdt:P31 wd:Q7882520 .", "")],
 "K8-4": [("Tulou and walled villages", "{ ?i wdt:P31 wd:Q15094777 } UNION { ?i wdt:P31 wd:Q10925819 } .", "")],
 "K8-21": [("Hanok villages and houses", "?i wdt:P31 wd:Q699813 .", "")],
 "K12-1": [("Wharenui (meeting houses)", "{ ?i wdt:P31 wd:Q7990652 } UNION { ?i wdt:P31 wd:Q6807904 . ?i wdt:P17 wd:Q664 } .", "")],
 "K12-5": [("Marae", "?i wdt:P31 wd:Q186685 .", "")],
 "K12-6": [("Saudeleur megalithic sites", "?i wdt:P361 wd:Q846967 .", "")],
 "K12-7": [("Churches of Chiloé", "?i wdt:P361 wd:Q27964 .", "")],
 "K12-12": [("Hórreos", "?i wdt:P31 wd:Q265764 .", "")],
 "K12-13": [("Trulli", "?i wdt:P31 wd:Q323069 .", "")],
 "K13-1": [("Persian gardens", "{ ?i wdt:P31 wd:Q4460 } UNION { ?i wdt:P361 wd:Q10624489 } .", "")],
 "K13-2": [("Mughal gardens", "?i wdt:P31 wd:Q2429892 .", "")],
 "K13-3": [("Chinese gardens", "{ ?i wdt:P31 wd:Q47692 } UNION { ?i wdt:P361 wd:Q1144337 } .", "")],
 "K13-4": [("Japanese gardens", "?i wdt:P31 wd:Q15835 .", "")],
 "K13-5": [("Italian Renaissance gardens", "?i wdt:P31 wd:Q12781 .", "")],
 "K13-6": [("French formal gardens", "?i wdt:P31 wd:Q12774 .", "")],
 "K13-7": [("English landscape gardens", "?i wdt:P31 wd:Q12783 .", "")],
}
Q = """SELECT ?i ?label ?sl ?enwiki ?countryLabel ?admLabel ?inc ?herLabel ?wh WHERE {
  %s
  ?i rdfs:label ?label FILTER(lang(?label)="en")
  ?i wikibase:sitelinks ?sl .
  OPTIONAL { ?enwiki schema:about ?i ; schema:isPartOf <https://en.wikipedia.org/> }
  OPTIONAL { ?i wdt:P17 ?country } OPTIONAL { ?i wdt:P131 ?adm } OPTIONAL { ?i wdt:P571 ?inc }
  OPTIONAL { ?i wdt:P1435 ?her } OPTIONAL { ?i wdt:P757 ?wh }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}"""
out = {}
for code, jobs in JOBS.items():
    secs = []
    for lab, pat, _ in jobs:
        res = sparql(Q % pat); time.sleep(2)
        items = {}
        for r in res:
            qid = r["i"]["value"].rsplit("/", 1)[1]
            b = items.setdefault(qid, dict(qid=qid, label=r["label"]["value"], sl=int(r["sl"]["value"]), enwiki=r.get("enwiki", {}).get("value", ""),
                                           country=r.get("countryLabel", {}).get("value", ""), place=r.get("admLabel", {}).get("value", ""),
                                           year=None, her=r.get("herLabel", {}).get("value", ""), unesco=bool(r.get("wh"))))
            inc = r.get("inc", {}).get("value", "")
            if inc and b["year"] is None:
                try: b["year"] = int(inc[:5].lstrip("+").split("-")[0]) if not inc.startswith("-") else -int(inc[1:5])
                except ValueError: pass
        secs.append((lab, list(items.values())))
        print(code, lab, len(items), sum(1 for b in items.values() if b["sl"] >= 1 or b["her"]))
    out[code] = secs
json.dump(out, open("wd_extra.json", "w"), ensure_ascii=False, indent=0)
