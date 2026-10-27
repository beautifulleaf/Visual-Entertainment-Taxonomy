"""Small Wikidata SPARQL helper shared by the visual-art pipelines."""
import json
import time
import urllib.error
import urllib.parse
import urllib.request

SPARQL = "https://query.wikidata.org/sparql"
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"


def sparql(query, retries=8):
    """Run a SELECT query; returns a list of {var: value} dicts (entity URIs shortened to QIDs)."""
    body = urllib.parse.urlencode({"query": query, "format": "json"}).encode()
    req = urllib.request.Request(SPARQL, data=body, headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.load(r)
            break
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
