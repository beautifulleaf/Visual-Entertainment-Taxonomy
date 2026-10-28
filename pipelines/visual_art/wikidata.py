"""Small Wikidata SPARQL helper shared by the visual-art pipelines."""
import http.client
import json
import time
import urllib.error
import urllib.parse
import urllib.request

SPARQL = "https://query.wikidata.org/sparql"
# QLever mirror of Wikidata: much faster on broad scans (e.g. every artist born in a
# 50-year bucket), and a fallback when WDQS is down. Needs explicit prefixes.
QLEVER = "https://qlever.dev/api/wikidata"
PREFIXES = """PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX schema: <http://schema.org/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"


def sparql(query, retries=8, endpoint=SPARQL):
    """Run a SELECT query; returns a list of {var: value} dicts (entity URIs shortened to QIDs)."""
    if endpoint == QLEVER:
        query = PREFIXES + query
    body = urllib.parse.urlencode({"query": query, "format": "json"}).encode()
    req = urllib.request.Request(endpoint, data=body, headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.load(r)
            break
        except (http.client.IncompleteRead, ConnectionError, json.JSONDecodeError) as e:
            # Dropped or truncated responses: retry like other network errors.
            print(f"    SPARQL {type(e).__name__}, retrying")
            time.sleep(min(120, 5 * 2 ** attempt))
        except urllib.error.HTTPError as e:
            wait = int(e.headers.get("Retry-After") or 0) or min(120, 5 * 2 ** attempt)
            print(f"    SPARQL HTTP {e.code}, retrying in {wait}s")
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"    SPARQL {e}, retrying")
            time.sleep(min(120, 5 * 2 ** attempt))
    else:
        raise RuntimeError("SPARQL query failed repeatedly")
    out = []
    for b in data["results"]["bindings"]:
        row = {}
        for k, v in b.items():
            val = v["value"]
            if v["type"] == "uri" and val.startswith("http://www.wikidata.org/entity/"):
                val = val.rsplit("/", 1)[1]
            row[k] = val
        out.append(row)
    return out


def year_of(value):
    """Year from an xsd:dateTime string such as '1606-07-15T00:00:00Z' or '-0450-...'."""
    if not value:
        return None
    digits = value.lstrip("-+").split("-", 1)[0]
    if not digits.isdigit():
        return None
    return -int(digits) if value.startswith("-") else int(digits)
