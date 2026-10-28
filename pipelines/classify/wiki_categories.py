"""Wikipedia category members, for attesting movement and cycle membership.

The Wikipedia API rate-limits this cloud IP, so requests are paced (one every
few seconds, backing off on 429) and cached in data/interim/wiki_categories.json
({category: {"pages": [...], "subcats": [...]}}). Subcategories are followed to
the given depth.

    python3 pipelines/classify/wiki_categories.py seeds/classify/film_categories.txt [depth]
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
CACHE = os.path.join(ROOT, "data", "interim", "wiki_categories.json")
UA = "VisualEntertainmentTaxonomy/0.1 (research; classifying)"


def members(cat):
    pages, subs, cont = [], [], None
    while True:
        p = {"action": "query", "list": "categorymembers", "cmtitle": "Category:" + cat, "cmlimit": "500",
             "cmtype": "page|subcat", "format": "json"}
        if cont:
            p["cmcontinue"] = cont
        url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(p)
        for attempt in range(10):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
                    j = json.load(r)
                break
            except Exception as e:
                print("  wait", attempt, e, file=sys.stderr)
                time.sleep(20 + 20 * attempt)
        else:
            raise SystemExit("giving up")
        for m in j.get("query", {}).get("categorymembers", []):
            (subs if m["ns"] == 14 else pages).append(m["title"].replace("Category:", "") if m["ns"] == 14 else m["title"])
        time.sleep(6)
        cont = j.get("continue", {}).get("cmcontinue")
        if not cont:
            return pages, subs


def main():
    cats = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    frontier = [(c, 0) for c in cats]
    while frontier:
        c, d = frontier.pop(0)
        if c not in cache:
            p, s = members(c)
            cache[c] = {"pages": p, "subcats": s}
            json.dump(cache, open(CACHE, "w"), ensure_ascii=False)
            print(f"{c}: {len(p)} pages, {len(s)} subcats", file=sys.stderr)
        if d < depth:
            frontier += [(s, d + 1) for s in cache[c]["subcats"]]


if __name__ == "__main__":
    main()
