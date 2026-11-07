"""Fallback homes for the AAT terms left in the open register (owner, 2026-11-07: "the keywords that can't be placed
could at least be kinds under existing regional leafs"). A term placed here is NOT claimed as a maker of the leaf's
tradition: it goes in its own group, "Related peoples & phases (Getty AAT)", with the reason.

Host leaf, in order:
  1. siblings  the leaf where most of its AAT siblings (same parent, same region) already sit
  2. cousins   the same, one level up (children of the grandparent)
  3. cluster   a hand map from the term's AAT cluster to the region's leaf for that cluster (below)
Held traditions (named, attestation pending) stay in the register. Writes taxonomy/audit/reference/related.csv.
"""
import csv, json, os, re, collections
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
OUT = os.path.join(ROOT, "taxonomy/audit/reference")
PLACED = {"leaf", "entry", "decided", "held"}   # variant and inherited are too weak to vouch for a neighbour
# cluster (regex on AAT ancestor chain) -> host leaf, for terms with no placed siblings or cousins
CLUSTER = [
    (r"Mississippi Valley", "E1-70"), (r"Eastern Woodland|Northeastern North American|Great Lakes|Middle Atlantic|Ohio Valley", "E1-137"),
    (r"Southeastern North American|Southeastern Native", "E1-139"), (r"Eskimo|Choris|Maritime area|Aleutian|Kodiak|Denbigh|Arctic", "D2-9"),
    (r"Northwest Coast", "I1-31"), (r"Californian", "H8-13"), (r"Great Basin", "H8-47"), (r"Plains", "H9-6"), (r"Plateau", "H8-17"),
    (r"Southwestern|Patayan|Hohokam|Mogollon|Anasazi|Pueblo", "E1-61"), (r"Subarctic|Athapaskan", "H9-12"),
    (r"Amazonian|Tupí|Eastern Brazilian|Caribbean Coast", "H9-14"), (r"Chaco", "E1-156"), (r"Pampean|Fuegian", "A4-19"),
    (r"Andean|Ecuadorian|Colombian", "H2-7"), (r"Middle American|Mexican|Central American|Yucatan", "D4-33"),
    (r"Australian", "A5-13"), (r"Gur\b|Gurunsi", "D4-34"), (r"Benue-Congo|Chad subfamily|Adamawa|Northeastern Nigerian|Katab|Nupe", "D5-142"),
    (r"Lake Chad|Central Sudanese|Sara\b", "D5-38"), (r"Cameroon|Grassfields|Tikar|Bamileke", "D5-148"), (r"Lagoon", "D5-46"),
    (r"Mande|West Atlantic|Kru|Western Sudanese|Hausa|Fulbe", "H3-64"), (r"Akan|Guinea Coast|Ewe|Ga-Adangme", "D5-48"),
    (r"Luba|Maniema|Lega", "D5-50"), (r"Mongo|Congo|Kasai|Kwango|Kuba|Ngiri", "I1-32"), (r"Kongo", "D6-2"),
    (r"Sotho|Tswana|Southern African|Nguni|Zulu|Tsonga|Venda|Shona", "H9-1"), (r"Swahili|Coastal East African", "K1-17"),
    (r"Oromo|Sidamo|Ethiopia|Turkana|Rift|Eastern African|Nilotic|Maasai", "H9-2"), 
    (r"Ancient Southern African|Rozwi", "K10-5"), (r"ancient East African", "K1-17"),
    (r"Melanesian|Papua|Irian|Solomon|Vanuatu", "D5-85"), (r"Polynesian", "H8-24"), (r"Micronesian", "K12-3"),
    (r"Southeast Asian", "H4-28"), (r"Early Nomads|Tagar|Bol'shaia|Karasuk", "G1-12"), (r"Siberian|Altai|Tungus", "D2-15"),
    (r"Ancient Italian|Italic", "D5-59"), (r"Anatolian Paleolithic", "L1-43"), (r"Orientalizing", "E1-26"),
    (r"Diaguita", "E1-121"), (r"Berber|Tamazight|North African", "G3-4"),
]


def main():
    A = {a["id"]: a for a in json.load(open(os.path.join(ROOT, "data/reference/aat_styles.json")))}
    X = {r["id"]: r for r in csv.DictReader(open(os.path.join(OUT, "aat_crosswalk.csv")))}
    FAC = {r["code"]: r for r in csv.DictReader(open(os.path.join(ROOT, "taxonomy/r3/va_facets.csv")))}
    kids = collections.defaultdict(list)
    for a in A.values(): kids[a["parent"]].append(a["id"])
    def anc(i):
        a = A.get(i); o = []
        while a and a["parent"] in A:
            a = A[a["parent"]]; o.append(a)
        return o
    def desc(i, depth):
        out = []
        for c in kids[i]:
            out.append(c)
            if depth > 1: out += desc(c, depth - 1)
        return out
    def era_ok(i, l):
        """an ancient or pre-contact term never goes to a leaf of a later age; a living people never to one that closed
        before 1600"""
        st, en = FAC.get(l, {}).get("start"), FAC.get(l, {}).get("end")
        chain = " ".join(x["label"] for x in anc(i)) + " " + X[i]["label"]
        old = re.search(r"\bancient|pre-columbian|prehistoric|neolithic|bronze age|iron age|paleo|archaic|phase\b", chain, re.I) or X[i]["coverage"] == "archaeology"
        if old: return bool(st) and int(st) < (1500 if re.search(r"pre-columbian|native american", chain, re.I) else 500)   # undated leaf: no proof
        if not old and en: return int(en) >= 1600
        return True
    def host_from(ids, reg, i):
        c = collections.Counter()
        for j in ids:
            x = X.get(j)
            if x and x["coverage"] in PLACED and x["leaves"]:
                for l in x["leaves"].split():
                    if FAC.get(l, {}).get("region") == reg and era_ok(i, l): c[l] += 1
        return c.most_common(1)[0] if c else None
    # national or generic designations and named art movements misfiled under peoples stay in the register
    NOHOST = re.compile(r"^(Bosnian|Yugoslav|Great Basin Native American|Athapaskan|Madras Art Movement|Revivalism|Native )|Kingdom$")
    # hosts read and rejected: the siblings that sit there were themselves placed on thin grounds
    VETO = {"K10-1", "H4-107", "G3-14", "I2-16", "D2-15"}   # Aksumite Arch., Kutch Embroidery, Mapuche Silverwork, Barniz de Pasto, Tobolsk Bone
    out = []
    for i, r in X.items():
        if r["coverage"] not in ("people", "archaeology") or NOHOST.search(r["label"]): continue
        a = A[i]; reg = r["region"]; ch = anc(i)
        h = host_from([s for s in kids[a["parent"]] if s != i], reg, i); how = "siblings"
        if not h and ch:
            h = host_from([s for s in desc(ch[0]["parent"], 2) if s != i], reg, i); how = "cousins"
        if h and h[1] < 2 and how == "cousins": h = None   # a single cousin is too thin
        if h and h[0] in VETO: h = None
        if h:
            out.append(dict(aat_id=i, label=r["label"], region=reg, host=h[0], how=how, group_of=ch[0]["label"] if ch else "")); continue
        chain = " | ".join(x["label"] for x in ch) + " " + r["label"]
        host = next((l for rx, l in CLUSTER if re.search(rx, chain) and era_ok(i, l) and l not in VETO), None)
        out.append(dict(aat_id=i, label=r["label"], region=reg, host=host or "", how="cluster" if host else "none", group_of=ch[0]["label"] if ch else ""))
    with open(os.path.join(OUT, "related.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    print(collections.Counter(o["how"] for o in out))
    return out


if __name__ == "__main__":
    main()
