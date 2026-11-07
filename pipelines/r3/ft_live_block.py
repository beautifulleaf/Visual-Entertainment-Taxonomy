"""R3: build the input of the new live-event and sports television block (B16).

Run after ft_inputs.py. Moves stand-up specials (old C4-7) and professional-wrestling
programmes (old G3 rows naming WWE/AEW/NJPW or wrestling) out of their blocks into
taxonomy/r3/ft_in/tv_live_sports.csv. The block pass adds the rest from knowledge
(additions.csv), since live and sports television was never gathered.
"""
import csv, glob, os, re
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
csv.field_size_limit(10**9)

def main():
    take = []
    for fn in glob.glob(os.path.join(ROOT, "taxonomy/r3/ft_in/*.csv")):
        if fn.endswith("tv_live_sports.csv"): continue
        rows = list(csv.DictReader(open(fn))); out = []
        for r in rows:
            t = (r["title"] + " " + r["note"] + " " + r["keywords"] + " " + r["wd_genre"]).lower()
            if r["old_leaf"] == "C4-7" or (r["old_leaf"].startswith("G3") and re.search(r"wrestl|wwe|\baew\b|njpw", t)):
                take.append(r)
            else:
                out.append(r)
        if len(out) != len(rows):
            with open(fn, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(out)
    with open(os.path.join(ROOT, "taxonomy/r3/ft_in/tv_live_sports.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(take[0].keys())); w.writeheader(); w.writerows(take)
    print("live block input", len(take))

if __name__ == "__main__":
    main()
