"""Dossier for the Getty AAT terms the crosswalk leaves uncovered although museum records carry their name.

For each such term: its AAT label, region and parent, the records counted by the crosswalk, the medium families of the
records whose culture label names it (objects_norm.csv.gz), their median start date and the commonest title words.
The decisions read off this dossier are in taxonomy/r3/aat_decisions.csv (entry / new leaf / facet / recorded),
applied by ref_crosswalk.py and va_out/sweep_ref. Run ref_crosswalk.py once before this (it writes the crosswalk).
Writes taxonomy/audit/reference/dossier.csv.
"""
import csv, gzip, os, re, collections, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def fold(s): return re.sub(r"\s+", " ", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().replace("'", "").strip())


def main():
    X = [x for x in csv.DictReader(open(os.path.join(ROOT, "taxonomy/audit/reference/aat_crosswalk.csv")))
         if x["coverage"] in ("uncovered", "decided", "recorded") and int(x["records"] or 0) > 0]
    names = {fold(re.sub(r"\s*\([^)]*\)", "", x["label"])) for x in X}
    fam = collections.defaultdict(collections.Counter); tit = collections.defaultdict(collections.Counter); dates = collections.defaultdict(list)
    for r in csv.DictReader(gzip.open(os.path.join(ROOT, "taxonomy/r3/collections/objects_norm.csv.gz"), "rt")):
        for n in {fold(w) for w in re.split(r"[,;|·/()\[\]]+", r["label"])} & names:
            fam[n][r["family"]] += 1
            for w in re.findall(r"[a-z]{4,}", fold(r["title"])): tit[n][w] += 1
            if r["date_begin"].lstrip("-").isdigit(): dates[n].append(int(r["date_begin"]))
    with open(os.path.join(ROOT, "taxonomy/audit/reference/dossier.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["aat_id", "label", "region", "aat_parent", "records", "families", "median_start", "title_words", "coverage"])
        for x in sorted(X, key=lambda x: -int(x["records"])):
            n = fold(re.sub(r"\s*\([^)]*\)", "", x["label"])); d = sorted(dates[n])
            w.writerow([x["id"], x["label"], x["region"], x["path"].split(" > ")[-1], x["records"],
                        " ".join(f"{k}{v}" for k, v in fam[n].most_common(4)), d[len(d) // 2] if d else "",
                        " ".join(t for t, _ in tit[n].most_common(8)), x["coverage"]])


if __name__ == "__main__":
    main()
