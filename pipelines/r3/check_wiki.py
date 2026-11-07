"""R3: check that every en.wikipedia URL cited by a leaf (src, catalogues) names an existing article.

    python3 pipelines/r3/check_wiki.py <tree.json>  -> taxonomy/r3/wiki_check.csv (url, status, resolved)
Uses the MediaWiki query API in batches of 50 titles (redirects followed), so it is cheap and polite.
"""
import csv, json, os, sys, time, urllib.parse, urllib.request
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
UA = "VE-Taxonomy-R3-linkcheck/1.0 (reference-work maintenance)"

def titles_of(tree):
    out = {}
    for tab in ("va", "ft"):
        for f in tree[tab]["fams"]:
            for s in f["subs"]:
                for l in s["leaves"]:
                    for x in (l.get("src") or []) + (l.get("catalogues") or []):
                        u = x[0]
                        if "en.wikipedia.org/wiki/" in u:
                            t = urllib.parse.unquote(u.split("/wiki/", 1)[1].split("#")[0]).replace("_", " ")
                            out.setdefault(t, []).append((tab.upper(), l["code"], u))
    return out

def query(batch):
    q = urllib.parse.urlencode({"action": "query", "format": "json", "redirects": 1, "titles": "|".join(batch)})
    for attempt in range(5):
        try:
            req = urllib.request.Request("https://en.wikipedia.org/w/api.php?" + q, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            time.sleep(5 * (attempt + 1))
    raise SystemExit("API unreachable")

def main(path):
    tree = json.load(open(path)); T = titles_of(tree); names = sorted(T)
    status = {}
    for i in range(0, len(names), 50):
        b = names[i:i + 50]; j = query(b)["query"]
        norm = {x["from"]: x["to"] for x in j.get("normalized", [])}
        red = {x["from"]: x["to"] for x in j.get("redirects", [])}
        pages = {p["title"]: p for p in j.get("pages", {}).values()}
        for t in b:
            n = norm.get(t, t); r = red.get(n, n); p = pages.get(r, {})
            status[t] = ("missing" if "missing" in p or "invalid" in p or not p else ("redirect" if r != n else "ok"), r)
        time.sleep(1)
    with open(os.path.join(ROOT, "taxonomy/r3/wiki_check.csv"), "w", newline="") as fo:
        w = csv.writer(fo); w.writerow(["tab", "leaf", "url", "status", "resolved"])
        for t in names:
            for tab, code, u in T[t]: w.writerow([tab, code, u, status[t][0], status[t][1]])
    c = {}
    for v, _ in status.values(): c[v] = c.get(v, 0) + 1
    print(len(names), "titles", c)
    for t in names:
        if status[t][0] == "missing": print("MISSING", t, [x[:2] for x in T[t]][:3])

if __name__ == "__main__":
    main(sys.argv[1])
