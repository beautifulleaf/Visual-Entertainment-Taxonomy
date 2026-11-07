"""Register of the AAT terms that remain without a home after every pass (owner, 2026-11-07: "look at what the
remaining terms are and if there would be any dedicated useful sources").

Each open term is listed with its AAT cluster, what has been searched (the 1.24M gathered museum records; the Smithsonian
anthropology collections for peoples), and the dedicated source for its cluster, with whether that source answered from
this environment on 2026-11-07. Reopen a term by finding it in that source; the term then goes through aat_decisions.csv.
Writes taxonomy/audit/reference/open_register.csv and open_register.md.
"""
import csv, json, os, re, collections
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
OUT = os.path.join(ROOT, "taxonomy/audit/reference")
# cluster pattern (matched against the AAT ancestor chain) -> (cluster name, dedicated source, reachable from here)
SOURCES = [
    (r"Chad subfamily|Benue-Congo|Adamawa|Katab|Nupe|Northeastern Nigerian|Jos|Plateau", "Nigeria Middle Belt and North-East",
     "Berns, Fardon & Kasfir, Central Nigeria Unmasked: Arts of the Benue River Valley (Fowler Museum 2011) and the Arnold Rubin archive, Fowler Museum", "catalogue not online; Fowler pages reachable"),
    (r"\bGur\b|Gurunsi|Frafra|Senufo", "Volta basin (Gur)", "Roy & Wheelock, Land of the Flying Masks (2007); University of Iowa, Art & Life in Africa", "Iowa site did not answer"),
    (r"Lake Chad|Sara\b|Central Sudanese", "Lake Chad and Central Sudan", "Musée du quai Branly – Jacques Chirac collections", "reachable"),
    (r"Lagoon", "Côte d'Ivoire lagoon peoples", "Musée du quai Branly collections; Smithsonian National Museum of African Art", "reachable"),
    (r"Congo|Maniema|Luba|Mongo|Kasai|Kwango|Kuba|Ngiri", "Congo basin", "Royal Museum for Central Africa (AfricaMuseum), Tervuren, collections and ethnographic archive", "reachable"),
    (r"Cameroon|Grassfields|Tikar|Bamileke", "Cameroon", "Musée du quai Branly; Ethnologisches Museum, Staatliche Museen zu Berlin", "reachable (quai Branly)"),
    (r"Sotho|Tswana|Nguni|Zulu|Southern African|Shona|Tsonga|Venda", "Southern Africa", "Wits Art Museum; Iziko Museums of South Africa", "not tested"),
    (r"Oromo|Sidamo|Ethiopia|Turkana|Rift|Eastern African|Swahili|Nilotic", "Horn and East Africa", "Institute of Ethiopian Studies museum; National Museums of Kenya", "not tested"),
    (r"West Atlantic|Mande|Kru|Guinea Coast|Akan|Ewe|Ga-Adangme|West African|Western Sudanese|Hausa|Fulbe", "West Africa (other)", "Musée du quai Branly; Musée Théodore Monod (IFAN), Dakar", "reachable (quai Branly)"),
    (r"Ancient African|Ancient West African|Ancient Southern African|ancient East African|Rozwi", "Ancient Africa", "UNESCO World Heritage nominations; Great Zimbabwe and Mapungubwe site museums", "reachable (UNESCO)"),
    (r"Amazonian|Eastern Brazilian|Tupí|Guaraní|Chaco|Pampean|Fuegian|Caribbean Coast|Native South American", "Lowland South America",
     "Instituto Socioambiental, Povos Indígenas no Brasil (per-people pages with arts sections); Museu do Índio; Museo del Barro, Asunción (Chaco)", "ISA list PDF reachable; people pages intermittent"),
    (r"Andean|Ecuadorian|Colombian", "Andes", "Museo Chileno de Arte Precolombino; Museo del Oro, Bogotá", "reachable (Precolombino)"),
    (r"Middle American|Mexican|Central American|Yucatan|Maya", "Mesoamerica and Central America", "INAH Mediateca; Museo Nacional de Antropología", "not tested"),
    (r"Pre-Columbian|Paleo-Indian|Archaic|Woodland|Eskimo|Aleutian|Kodiak|Choris|Patayan|Mogollon", "North American archaeology",
     "tDAR (Digital Archaeological Record); state archaeological surveys; Smithsonian Handbook of North American Indians", "not tested; Smithsonian API sparse for phases"),
    (r"Native North American|Native American|First Nations|Salish|Athapaskan|Plains|Plateau|Californian|Great Basin|Southeastern Native|Eastern Woodland", "Native North America",
     "National Museum of the American Indian (Smithsonian API, done); Handbook of North American Indians", "API done"),
    (r"Australian", "Aboriginal Australia", "ANKA and Desart art-centre directories (language groups per art centre); AIATSIS AustLang", "ANKA, Desart reachable; AIATSIS refused"),
    (r"Melanesian|Polynesian|Micronesian|Oceanic|Papua|Irian|Vanuatu|Solomon", "Oceania", "Te Papa collections; Australian Museum; Pacific Collection Access Project", "Te Papa, Australian Museum reachable"),
    (r"Southeast Asian|Thai|Burmese|Vietnam|Lao|Malay|Indonesian|Philippine", "Southeast Asia", "Vietnam Museum of Ethnology; Museum Volkenkunde (Wereldmuseum) Leiden", "Wereldmuseum redirects"),
    (r"Siberian|Altai|Tungus|Early Nomads|Tagar", "Siberia and the steppe", "Kunstkamera (Peter the Great Museum of Anthropology and Ethnography); State Hermitage", "Kunstkamera did not answer"),
    (r"Ancient Italian|Etruscan|Italic", "Ancient Italy", "British Museum and Met essays; Villa Giulia", "Met throttled; BM refused"),
    (r"Indian|South Asian|Himalayan|Sri Lankan", "South Asia", "Indira Gandhi Rashtriya Manav Sangrahalaya (National Museum of Mankind), Bhopal", "not tested"),
]


def main():
    A = {a["id"]: a for a in json.load(open(os.path.join(ROOT, "data/reference/aat_styles.json")))}
    def anc(i):
        a = A.get(i); o = []
        while a and a["parent"] in A:
            a = A[a["parent"]]; o.append(a["label"])
        return o
    D = {d["aat_id"]: d for d in csv.DictReader(open(os.path.join(ROOT, "taxonomy/r3/aat_decisions.csv")))}
    si = os.path.join(ROOT, "data/reference/si_peoples.json")
    SI = {i for v in (json.load(open(si)).values() if os.path.exists(si) else []) for i in v["aat_ids"]}
    out = []
    for r in csv.DictReader(open(os.path.join(OUT, "aat_crosswalk.csv"))):
        held = r["coverage"] == "recorded" and "held" in D.get(r["id"], {}).get("note", "")
        if r["coverage"] not in ("people", "archaeology") and not held: continue
        ch = " | ".join(anc(r["id"]))
        cl, src, reach = next(((c, s, ok) for rx, c, s, ok in SOURCES if re.search(rx, ch + " " + r["label"])), ("other", "", ""))
        out.append(dict(aat_id=r["id"], label=r["label"], status="held tradition" if held else r["coverage"], region=r["region"], cluster=cl,
                        aat_parent=(anc(r["id"]) or [""])[0], searched="gathered records" + ("; Smithsonian anthropology" if r["id"] in SI else ""),
                        dedicated_source=src, reachable=reach))
    with open(os.path.join(OUT, "open_register.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    c = collections.Counter((o["cluster"], o["dedicated_source"], o["reachable"]) for o in out)
    L = ["# Open register: AAT terms with no home after every pass", "",
         f"{len(out)} terms: " + ", ".join(f"{v} {k}" for k, v in collections.Counter(o['status'] for o in out).items()) + ".",
         "Every term was searched in the 1.24M gathered museum records; peoples also in the Smithsonian anthropology collections.",
         "A term leaves this register when its cluster's source shows a visual tradition for it.", "",
         "| Cluster | Terms | Dedicated source | From here |", "|---|---:|---|---|"]
    L += [f"| {k[0]} | {v} | {k[1]} | {k[2]} |" for k, v in c.most_common()]
    open(os.path.join(OUT, "open_register.md"), "w").write("\n".join(L) + "\n")
    print(len(out)); print("\n".join(L[7:]))


if __name__ == "__main__":
    main()
