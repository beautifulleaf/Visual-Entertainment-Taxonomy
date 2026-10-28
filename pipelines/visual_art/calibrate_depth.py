"""Calibrate artist-inclusion depth against the hand-picked reference lists.

Matches every name in seeds/visual-art/*_depth_reference.txt to a Wikidata
person, then reports per movement how "famous" the reference artists are
(Wikipedia sitelink counts). The low percentiles of that distribution become
the inclusion cutoff applied to other regions and periods.

Matching: first an exact English label/alias match among humans born
BORN_MIN..BORN_MAX via batched SPARQL (the person with the most sitelinks wins when a label is ambiguous);
names still unmatched then go through the wbsearchentities API, which is
heavily rate-limited on shared IPs, so it runs slowly and results are cached.

Outputs:
  data/interim/depth_reference_matched.csv  one row per reference name
  stdout                                    per-movement sitelink percentiles

Usage: python3 pipelines/visual_art/calibrate_depth.py [--no-search]
"""
import argparse
import csv
import glob
import json
import os
import re
import statistics
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://www.wikidata.org/w/api.php"
SPARQL = "https://query.wikidata.org/sparql"
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"
HUMAN = "Q5"
# Guards against exact-label matches to a more famous namesake (e.g. "Henry
# Moore" the sculptor instead of the marine painter): the reference lists
# span roughly 1350-1900 births. Widen when adding lists for other periods.
BORN_MIN, BORN_MAX = 1300, 1900
# Same guard by occupation (e.g. Thomas Hardy the painter, not the novelist).
ART_OCCUPATIONS = " ".join("wd:" + q for q in (
    "Q1028181",   # painter
    "Q1281618",   # sculptor
    "Q42973",     # architect
    "Q3391743",   # visual artist
    "Q483501",    # artist
    "Q15296811",  # draftsperson
    "Q1925963",   # graphic artist
    "Q11569986",  # printmaker
    "Q644687",    # illustrator
    "Q33231",     # photographer
    "Q329439",    # engraver
    "Q10862983",  # etcher
    "Q1114448",   # cartoonist
    "Q211423",    # goldsmith
    "Q2519376",   # jeweler
    "Q1734662",   # cartographer
    "Q16947657",  # lithographer
    "Q3303330",   # calligrapher
    "Q5322166",   # designer
    "Q7541856",   # ceramicist
))

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEEDS = os.path.join(ROOT, "seeds", "visual-art", "*_depth_reference.txt")
OUT_PATH = os.path.join(ROOT, "data", "interim", "depth_reference_matched.csv")
CACHE = os.path.join(ROOT, "data", "raw", "wikidata", "name_matches.json")


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            # Wikimedia rate-limits shared IPs; honour Retry-After when given.
            wait = int(e.headers.get("Retry-After") or 0) or min(120, 5 * 2 ** attempt)
            print(f"    HTTP {e.code}, retrying in {wait}s")
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"    {e}, retrying")
            time.sleep(min(120, 5 * 2 ** attempt))
    raise RuntimeError(f"request failed: {url[:200]}")


def read_seeds():
    rows = []
    for path in sorted(glob.glob(SEEDS)):
        parent = None
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"^(\*\s*)?([^:]+):\s*(.+)$", line)
            if not m:
                continue
            sub, movement, names = m.groups()
            if not sub:
                parent = movement.strip()
            label = f"{parent} > {movement.strip()}" if sub else movement.strip()
            rows += [{"list": os.path.basename(path), "movement": label, "name": n.strip()} for n in names.split(",") if n.strip()]
    return rows


def sparql_label_match(names):
    """Exact English label/alias matches among humans. Returns {name: record}."""
    found = {}
    for i in range(0, len(names), 80):
        chunk = names[i:i + 80]
        values = " ".join(json.dumps(n, ensure_ascii=False) + "@en" for n in chunk)
        q = f"""SELECT ?name ?p ?s (SAMPLE(?b) AS ?birth) (SAMPLE(?w) AS ?wikiart) WHERE {{
          VALUES ?name {{ {values} }}
          ?p rdfs:label|skos:altLabel ?name ; wdt:P31 wd:Q5 ; wikibase:sitelinks ?s ; wdt:P569 ?b .
          FILTER(YEAR(?b) >= {BORN_MIN} && YEAR(?b) <= {BORN_MAX})
          FILTER EXISTS {{ ?p wdt:P106 ?occ . VALUES ?occ {{ {ART_OCCUPATIONS} }} }}
          OPTIONAL {{ ?p wdt:P6002 ?w }}
        }} GROUP BY ?name ?p ?s"""
        data = fetch_json(SPARQL + "?" + urllib.parse.urlencode({"query": q, "format": "json"}))
        for b in data["results"]["bindings"]:
            name, sl = b["name"]["value"], int(b["s"]["value"])
            n_cands = found[name]["candidates"] + 1 if name in found else 1
            if name in found and found[name]["sitelinks"] >= sl:
                found[name]["candidates"] = n_cands
                continue
            birth = b.get("birth", {}).get("value", "")
            found[name] = {
                "qid": b["p"]["value"].rsplit("/", 1)[1],
                "sitelinks": sl,
                "birth_year": int(birth[:4]) if birth[:4].isdigit() else None,
                "has_wikiart_id": "wikiart" in b,
                "via": "label",
                "candidates": n_cands,  # >1 means ambiguous: review by hand
            }
        print(f"  SPARQL: {len(found)} matched after {i + len(chunk)} names")
        time.sleep(2)
    return found


def search_match(name):
    """First wbsearchentities hit that is a human, or None."""
    hits = fetch_json(API + "?" + urllib.parse.urlencode({
        "action": "wbsearchentities", "search": name, "language": "en", "type": "item", "limit": 7, "format": "json"})).get("search", [])
    if not hits:
        return None
    ents = fetch_json(API + "?" + urllib.parse.urlencode({
        "action": "wbgetentities", "ids": "|".join(h["id"] for h in hits), "props": "claims|sitelinks", "format": "json"})).get("entities", {})
    for h in hits:
        ent = ents.get(h["id"], {})
        claims = ent.get("claims", {})
        if HUMAN not in [c["mainsnak"].get("datavalue", {}).get("value", {}).get("id") for c in claims.get("P31", [])]:
            continue
        birth = next((c["mainsnak"].get("datavalue", {}).get("value", {}).get("time") for c in claims.get("P569", [])), None)
        return {
            "qid": h["id"],
            "sitelinks": len(ent.get("sitelinks", {})),
            "birth_year": int(birth[1:5]) if birth and birth[1:5].isdigit() else None,
            "has_wikiart_id": bool(claims.get("P6002")),
            "via": "search",
        }
    return None


def pct(values, p):
    values = sorted(values)
    return values[min(len(values) - 1, int(p / 100 * len(values)))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-search", action="store_true", help="skip the slow search-API fallback")
    args = ap.parse_args()

    rows = read_seeds()
    names = sorted({r["name"] for r in rows})
    print(f"{len(rows)} reference entries, {len(names)} distinct names")
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}

    pending = [n for n in names if n not in cache]
    if pending:
        cache.update(sparql_label_match(pending))
        json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)

    if not args.no_search:
        pending = [n for n in names if n not in cache]
        print(f"search fallback for {len(pending)} names")
        for i, n in enumerate(pending, 1):
            cache[n] = search_match(n)  # None is cached too, so it isn't retried
            if i % 10 == 0:
                json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
                print(f"  searched {i}/{len(pending)}")
            time.sleep(1)
        json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)

    fields = ["list", "movement", "name", "qid", "sitelinks", "birth_year", "has_wikiart_id", "via", "candidates"]
    for r in rows:
        r.update(cache.get(r["name"]) or {})
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as out:
        w = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    print(f"\n{'movement':45} {'n':>4} {'matched':>7}  sitelinks p10 / p25 / median")
    by_mv = {}
    for r in rows:
        by_mv.setdefault(r["movement"], []).append(r)
    all_sl = []
    for mv, rs in by_mv.items():
        sl = [r["sitelinks"] for r in rs if r.get("qid")]
        all_sl += sl
        if sl:
            print(f"{mv:45} {len(rs):>4} {len(sl):>7}  {pct(sl, 10):>3} / {pct(sl, 25):>3} / {statistics.median(sl):>5}")
    print(f"{'ALL':45} {len(rows):>4} {len(all_sl):>7}  {pct(all_sl, 10):>3} / {pct(all_sl, 25):>3} / {statistics.median(all_sl):>5}")
    ambiguous = [f'{r["name"]} ({r["candidates"]})' for r in rows if (r.get("candidates") or 0) > 1]
    print(f"\nambiguous, review by hand ({len(ambiguous)}): {', '.join(ambiguous)}")
    unmatched = [r["name"] for r in rows if not r.get("qid")]
    print(f"\nunmatched ({len(unmatched)}): {', '.join(unmatched)}")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
