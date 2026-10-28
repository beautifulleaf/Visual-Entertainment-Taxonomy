"""Pool rows, holdings and pageviews for modern reference artists below the pool rule.

The Europe 1400-1900 pass adds reference artists the occupation/sitelink query
misses to its pool as positives (build_pool.py, people_by_qid). The modern regions
now carry the same reference config (regions.py), so a future build_pool.py run
does this natively. Until then, this script computes the same rows for the
reference artists missing from the current pool_modern_<region>.csv, in side files
that fit_modern.py merges in (it never touches the shared pool, holdings or
pageviews files):

  data/interim/visual_art/refextra_pool_modern_<region>.csv   (build_pool.py columns)
  data/interim/visual_art/refextra_holdings.csv               (Met / AIC / Cleveland, museum_holdings.py matchers)
  data/interim/visual_art/refextra_sitelinks.tsv + refextra_pageviews.csv  (pageviews.py --sitelinks/--out)

Wikidata via build_modern_reference.sparql (QLever by default), one query at a time.

Usage: python3 pipelines/visual_art/modern_reference_extras.py [--skip-pageviews]
"""
import argparse
import collections
import csv
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_modern_reference as bmr  # noqa: E402
import museum_holdings as mh  # noqa: E402
from build_pool import ART_OCCUPATIONS, AUTHORITY_IDS  # noqa: E402
from reference import load_reference  # noqa: E402
from regions import GLOBAL_IDS, MEDIA, MODERN_REGIONS, REGIONS, active_span, period_of  # noqa: E402

ROOT = bmr.ROOT
DATA = os.path.join(ROOT, "data", "interim", "visual_art")
ALL = [f"modern_{r}" for r in MODERN_REGIONS]


def fetch_extra_facts(qids):
    """Sitelinks, ULAN/WikiArt/authority IDs and Wikipedia titles per QID (cached)."""
    props = " ".join("wdt:" + p for p in list(GLOBAL_IDS) + AUTHORITY_IDS)

    def q(chunk):
        values = " ".join("wd:" + a for a in chunk)
        out = {a: {"sitelinks": 0, "claims": {}, "titles": {}} for a in chunk}
        for r in bmr.sparql(f"SELECT ?a ?s WHERE {{ VALUES ?a {{ {values} }} ?a wikibase:sitelinks ?s }}"):
            out[r["a"]]["sitelinks"] = int(r["s"])
        for r in bmr.sparql(f"""SELECT ?a ?p ?v WHERE {{ VALUES ?a {{ {values} }} VALUES ?p {{ {props} }} ?a ?p ?v }}"""):
            out[r["a"]]["claims"].setdefault(r["p"].rsplit("/", 1)[-1], []).append(r["v"])
        for r in bmr.sparql(f"""SELECT ?a ?site ?title WHERE {{ VALUES ?a {{ {values} }}
              ?art schema:about ?a ; schema:isPartOf ?site ; schema:name ?title .
              FILTER(STRENDS(STR(?site), ".wikipedia.org/")) }}"""):
            wiki = r["site"].split("//", 1)[1].split(".wikipedia.org", 1)[0]
            out[r["a"]]["titles"][wiki] = r["title"]
        return out
    return bmr.chunked_cache("refextra_facts.json", qids, q)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--skip-pageviews", action="store_true")
    args = ap.parse_args()
    info = json.load(open(os.path.join(bmr.RAW, "artists.json"), encoding="utf-8"))
    missing = {}
    for region in ALL:
        with open(os.path.join(DATA, f"pool_{region}.csv"), encoding="utf-8") as f:
            pooled = {r["qid"] for r in csv.DictReader(f)}
        for r in load_reference(REGIONS[region]):
            if r["qid"] and r["qid"] not in pooled and r["qid"] in info:
                missing.setdefault(region, []).append(r["qid"])
    allq = sorted({q for qs in missing.values() for q in qs})
    print(f"{len(allq)} reference artists missing from their region's pool: "
          + ", ".join(f"{r[7:]} {len(qs)}" for r, qs in missing.items()))
    facts = fetch_extra_facts(allq)

    pool = {}
    for region, qs in missing.items():
        rows = []
        for q in qs:
            a, fct = info[q], facts.get(q, {"sitelinks": 0, "claims": {}, "titles": {}})
            span = active_span(a["birth"], a["death"])
            occ = set(a["P106"])
            media = [m for m in MEDIA if set(MEDIA[m]) & occ]
            claims = fct["claims"]
            rows.append({
                "qid": q, "label": a["label"], "birth": a["birth"], "death": a["death"],
                "active_start": span[0] if span else None, "active_end": span[1] if span else None,
                "period": period_of(span) if span else None, "sitelinks": fct["sitelinks"],
                "wikipedias": len(fct["titles"]), "countries": "|".join(a["P27"] or a["birth_country"]),
                "genres": "", "movements": "", "in_pool_rule": 0, "is_reference": 1,
                "medium": media[0] if media else "visual art (unspecified)", "media": "|".join(media),
                **{f"{name}_id": (claims.get(pid) or [""])[0] for pid, name in GLOBAL_IDS.items()},
                "authority_ids": "|".join(p for p in AUTHORITY_IDS if claims.get(p)),
                "art_occ_share": round(len(occ & ART_OCCUPATIONS) / len(occ), 3) if occ else "",
            })
            pool[q] = (a["label"], a["birth"], a["death"])
        out = os.path.join(DATA, f"refextra_pool_{region}.csv")
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {out} ({len(rows)})")

    # Holdings with the museum_holdings.py matchers, restricted to these artists.
    index = mh.NameIndex(pool)
    met_obj, met_tl, met_hl = mh.met_counts()
    aic, cma = mh.aic_counts(index), mh.cma_counts(index)
    out = os.path.join(DATA, "refextra_holdings.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["qid", "met_objects", "met_timeline_works", "met_highlights", "aic_objects", "cma_objects", "eastasia_objects"])
        for q in sorted(pool):
            w.writerow([q, met_obj[q], met_tl[q], met_hl[q], aic[q], cma[q], 0])
    print(f"wrote {out}: Met {sum(1 for q in pool if met_obj[q])}, AIC {sum(1 for q in pool if aic[q])}, "
          f"Cleveland {sum(1 for q in pool if cma[q])}")

    sl = os.path.join(DATA, "refextra_sitelinks.tsv")
    with open(sl, "w", encoding="utf-8") as f:
        for q in sorted(pool):
            for wiki, title in sorted(facts[q]["titles"].items()):
                f.write(f"{q}\t{wiki}\t{title}\n")
    if not args.skip_pageviews:
        subprocess.run([sys.executable, "-u", os.path.join(os.path.dirname(os.path.abspath(__file__)), "pageviews.py"),
                        "--sitelinks", sl, "--out", os.path.join(DATA, "refextra_pageviews.csv")], check=True)


if __name__ == "__main__":
    main()
