"""R3: check the leaves' "View all" catalogue links once per URL template.

A template = host + path with digits collapsed + sorted query keys. Each template is tested with up
to two of its URLs (GET, 20 s, browser-like UA); its status applies to all its links. Writes
taxonomy/r3/catalogue_check.csv (template, n_links, status, example) and prints a summary.
    python3 pipelines/r3/check_catalogues.py <tree.json>
"""
import csv, json, os, re, sys, urllib.parse, urllib.request, concurrent.futures as cf
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
UA = "Mozilla/5.0 (X11; Linux x86_64) VE-Taxonomy-R3-linkcheck"

def template(u):
    p = urllib.parse.urlsplit(u)
    path = re.sub(r"\d+", "#", p.path)
    if "wikipedia.org" in p.netloc or "wikidata.org" in p.netloc: path = "/wiki/*"
    keys = ",".join(sorted(urllib.parse.parse_qs(p.query).keys()))
    return f"{p.netloc}{path}?{keys}"

def fetch(u):
    try:
        req = urllib.request.Request(u, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r: return r.status
    except urllib.error.HTTPError as e: return e.code
    except Exception as e: return type(e).__name__

def main(path):
    tree = json.load(open(path)); groups = {}
    for tab in ("va", "ft"):
        for f in tree[tab]["fams"]:
            for s in f["subs"]:
                for l in s["leaves"]:
                    for x in l.get("catalogues") or []:
                        if "wikipedia.org" in x[0]: continue  # checked offline by check_wiki.py
                        groups.setdefault(template(x[0]), []).append(x[0])
    def test(item):
        t, us = item; sts = [fetch(u) for u in list(dict.fromkeys(us))[:2]]
        ok = any(s == 200 for s in sts if isinstance(s, int))
        return t, len(us), "ok" if ok else "|".join(map(str, sts)), us[0]
    with cf.ThreadPoolExecutor(8) as ex: res = list(ex.map(test, groups.items()))
    res.sort(key=lambda r: -r[1])
    with open(os.path.join(ROOT, "taxonomy/r3/catalogue_check.csv"), "w", newline="") as fo:
        w = csv.writer(fo); w.writerow(["template", "n_links", "status", "example"]); w.writerows(res)
    n = sum(r[1] for r in res); bad = [r for r in res if r[2] != "ok"]
    print(f"{len(res)} templates for {n} links; failing templates {len(bad)} covering {sum(r[1] for r in bad)} links")
    for r in bad[:40]: print("  ", r[1], r[2], r[3][:110])

if __name__ == "__main__":
    main(sys.argv[1])
