"""Unified Visual Art candidate pool for the scale-up, region by region.

Reuses the gathering's coverage audit (pipelines/visual_art/coverage_audit.py),
which already reads every tradition, maker and artist source once and assigns
each to the 20-region grid and an era: a recording Grid keeps every call as a
pool row instead of only counting it. Culture × medium cells (the audit's
media_trad) become object-tradition rows, the leaf grain of D7.

    python3 pipelines/classify/va_pool.py

Writes taxonomy/visual_art/pool_traditions.csv (source, label, region, era,
objects, medium, kind) and pool_people.csv (source, key, region, era, kind).
"""
import collections
import csv
import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "pipelines", "visual_art"))
import coverage_audit as CA  # noqa: E402

OUT = os.path.join(ROOT, "taxonomy", "visual_art")
TRAD, PEOPLE = [], []


class RecordingGrid(CA.Grid):
    def tradition(self, source, label, region, year, objects=0, medium=None):
        super().tradition(source, label, region, year, objects, medium)
        r = CA.era_fix(region, year, label)
        TRAD.append({"source": source, "label": label, "region": r or "", "era": CA.fine_era(year) or "",
                     "year": "" if year is None else int(year), "objects": int(CA.num(objects) or 0),
                     "medium": medium or "", "kind": "tradition"})

    def artist(self, source, key, region, year=None, fe=None):
        super().artist(source, key, region, year, fe)
        PEOPLE.append({"source": source, "key": key, "region": region or "", "era": fe or CA.fine_era(year) or "", "kind": "artist"})

    def maker(self, source, key, region, year):
        super().maker(source, key, region, year)
        PEOPLE.append({"source": source, "key": key, "region": CA.era_fix(region, year) or "", "era": CA.fine_era(year) or "", "kind": "maker"})


def main():
    CA.Grid = RecordingGrid
    g = CA.build_grid()
    seen = collections.Counter()
    for (reg, med), labels in g.media_trad.items():
        for lab in labels:
            TRAD.append({"source": "media_cell", "label": lab, "region": reg, "era": "", "year": "", "objects": "",
                         "medium": med, "kind": "culture_medium"})
    os.makedirs(OUT, exist_ok=True)
    for name, rows, cols in (("pool_traditions.csv", TRAD, ["source", "label", "region", "era", "year", "objects", "medium", "kind"]),
                             ("pool_people.csv", PEOPLE, ["source", "key", "region", "era", "kind"])):
        with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
    c = collections.Counter((r["region"], r["kind"]) for r in TRAD)
    print(len(TRAD), "tradition rows;", len(PEOPLE), "people rows")
    for reg in CA.REGIONS + [""]:
        print(f"{reg[:30]:30} trad {c[reg, 'tradition']:6} cells {c[reg, 'culture_medium']:6}")


if __name__ == "__main__":
    main()
