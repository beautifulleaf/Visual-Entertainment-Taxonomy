"""R3: check every en.wikipedia link cited by a leaf (src, catalogues) offline.

One download of Wikipedia's title list (enwiki-latest-all-titles-in-ns0.gz, ~100 MB, includes
redirects) replaces thousands of rate-limited API calls; cached under data/ (gitignored).

    python3 pipelines/r3/check_wiki.py <tree.json>  -> taxonomy/r3/wiki_check.csv (tab, leaf, url, status)
status: ok (title exists, as article or redirect) / missing.
"""
import csv, gzip, json, os, sys, urllib.parse, urllib.request
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
DUMP = os.path.join(ROOT, "data", "enwiki-all-titles-in-ns0.gz")
URL = "https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-all-titles-in-ns0.gz"

def titles():
    if not os.path.exists(DUMP):
        os.makedirs(os.path.dirname(DUMP), exist_ok=True)
        urllib.request.urlretrieve(URL, DUMP)
    with gzip.open(DUMP, "rt", encoding="utf-8", errors="replace") as f:
        next(f)  # header
        return {line.rstrip("\n") for line in f}

def main(path):
    tree = json.load(open(path)); T = titles(); rows = []; c = {"ok": 0, "missing": 0}
    for tab in ("va", "ft"):
        for f in tree[tab]["fams"]:
            for s in f["subs"]:
                for l in s["leaves"]:
                    for x in (l.get("src") or []) + (l.get("catalogues") or []):
                        u = x[0]
                        if "en.wikipedia.org/wiki/" not in u: continue
                        t = urllib.parse.unquote(u.split("/wiki/", 1)[1].split("#")[0]).replace(" ", "_")
                        t = t[:1].upper() + t[1:]
                        st = "ok" if t in T else "missing"; c[st] += 1
                        rows.append([tab.upper(), l["code"], u, st])
    with open(os.path.join(ROOT, "taxonomy/r3/wiki_check.csv"), "w", newline="") as fo:
        w = csv.writer(fo); w.writerow(["tab", "leaf", "url", "status"]); w.writerows(rows)
    print(c)

if __name__ == "__main__":
    main(sys.argv[1])
