"""Smithsonian Open Access lookup for the AAT peoples left open by ref_close.py (no gathered records, no covered parent).

For each people, searches the anthropology collections (NMNH Anthropology, National Museum of African Art, National
Museum of the American Indian) for the name, keeps only records whose culture field carries the name as a word, and
stores the object count, object types, titles and dates. The key is injected by the session's network proxy
(api.data.gov); no key is read from the environment. Writes data/reference/si_peoples.json (gitignored data).
"""
import csv, json, os, re, time, urllib.parse, urllib.request, concurrent.futures as cf
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
UA = "VE-Taxonomy-coverage/1.0 (research)"
UNITS = "(unit_code:NMNHANTHRO OR unit_code:NMAfA OR unit_code:NMAI)"


def get(q, start=0):
    url = "https://api.si.edu/openaccess/api/v1.0/search?" + urllib.parse.urlencode({"q": q, "rows": 100, "start": start})
    for i in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60))["response"]
        except Exception as e:
            err = e; time.sleep(3 * (i + 1))
    raise err


def look(name):
    resp = get(f'"{name}" AND {UNITS}')
    rows, n = resp.get("rows", []), resp.get("rowCount", 0)
    if n > 100:
        for st in range(100, min(n, 500), 100): rows += get(f'"{name}" AND {UNITS}', st).get("rows", [])
    rx = re.compile(rf"\b{re.escape(name)}\b", re.I)
    keep = []
    for x in rows:
        ix = (x.get("content") or {}).get("indexedStructured") or {}
        cul = " | ".join(ix.get("culture") or [])
        if rx.search(cul):
            keep.append(dict(title=x.get("title", ""), unit=x.get("unitCode"), culture=cul, type=(ix.get("object_type") or [""])[0],
                             date=(ix.get("date") or [""])[0], place=(ix.get("geoLocation") and "") or ""))
    return name, dict(hits=n, matched=len(keep), objects=keep)


def main():
    X = [r for r in csv.DictReader(open(os.path.join(ROOT, "taxonomy/audit/reference/aat_crosswalk.csv"))) if r["coverage"] == "people"]
    names = {}
    for r in X:
        nm = re.sub(r"\s*\([^)]*\)", "", r["label"]).strip()
        names.setdefault(nm, []).append(r["id"])
    out_p = os.path.join(ROOT, "data/reference/si_peoples.json")
    out = json.load(open(out_p)) if os.path.exists(out_p) else {}
    todo = [n for n in names if n not in out]
    with cf.ThreadPoolExecutor(4) as ex:
        for i, (nm, res) in enumerate(ex.map(look, todo)):
            res["aat_ids"] = names[nm]; out[nm] = res
            if i % 50 == 0:
                json.dump(out, open(out_p, "w"), ensure_ascii=False); print(i, "done", flush=True)
    json.dump(out, open(out_p, "w"), ensure_ascii=False)
    print(len(out), "peoples;", sum(1 for v in out.values() if v["matched"]), "with matched objects")


if __name__ == "__main__":
    main()
