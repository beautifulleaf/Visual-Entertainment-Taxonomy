"""VA completeness sweep (2026-11-07): new leaves for the open named traditions of the collections mapping.

Source: taxonomy/audit/va_completeness (V4). The Met/AIC culture counts were never part of
missing_traditions.csv, so the R3 vetting pass (va_out/missing_traditions) did not see them.
Rule, applied to every open tradition with >= 50 objects:
  new leaf  iff  (1) an established name attested by an English Wikipedia article (checked by web search,
                     2026-11-07; the article or the section that treats the tradition is the leaf's source),
                 (2) >= 200 objects after de-duplicating overlapping Met labels (largest single label),
                 (3) the records show the medium, and
                 (4) no existing leaf covers it.
Held (rule 1 not confirmed from this environment; for the owner): see summary.md.
Writes result.json in the va_out pass format (new_leaves with collections_from).
"""
import json, os
W = "https://en.wikipedia.org/wiki/"
MET = "https://www.metmuseum.org/art/collection/search?q="
BM = "https://www.britishmuseum.org/collection/search?keyword="


def k(name, group, note, url):
    return [name, group, note, "r3 " + url, 0]


def met(q, what):
    return [MET + q.replace(" ", "+"), f"The Met collection search: {q}", what]


def bm(q, what):
    return [BM + q.replace(" ", "+"), f"British Museum collection search: {q}", what]


L = [
    dict(key="CYPPOT", sub="E1", label="Ancient Cypriot Pottery", breadth="medium",
         defn="The pottery of ancient Cyprus from the Chalcolithic to the Cypro-Classical period: Red-on-White and Red Polished "
              "handmade wares of the Chalcolithic and Early–Middle Bronze Age, the Late Bronze Age Base Ring and White Slip wares "
              "exported across the Levant, and the Iron Age White Painted, Bichrome and Black-on-Red wares with free-field figural jugs "
              "and barrel-shaped jugs.",
         aliases="Cypriot pottery; Pottery of ancient Cyprus", see="D5-137 Ancient Cypriot Sculpture; E1-25 Geometric Pottery",
         src=[[W + "Pottery_of_ancient_Cyprus", "Wikipedia"], [W + "Ancient_Cypriot_art", "Wikipedia"]],
         catalogues=[met("Cypriot", "the Cesnola Collection and other Cypriot objects in the Metropolitan Museum"),
                     bm("Cypriot pottery", "Cypriot pottery in the British Museum")],
         axis="wares in order of appearance (Chalcolithic to Cypro-Classical), then holding institutions",
         kinds=[k("Red-on-White ware", "Sub-types", "Chalcolithic painted pottery, red designs on a light slip", W + "Pottery_of_ancient_Cyprus"),
                k("Red Polished ware", "Sub-types", "handmade burnished ware of the Philia phase and Early–Middle Cypriot Bronze Age", W + "Philia_culture"),
                k("Base Ring ware", "Sub-types", "Late Cypriot thin-walled handmade ware, widely exported", W + "Pottery_of_ancient_Cyprus"),
                k("White Slip ware", "Sub-types", "Late Cypriot ware with dark painted ladder patterns on a white slip", W + "Pottery_of_ancient_Cyprus"),
                k("White Painted ware", "Sub-types", "the long-lived painted ware of the Bronze and Iron Ages", W + "Pottery_of_ancient_Cyprus"),
                k("Bichrome ware", "Sub-types", "red and black painted ware, Late Bronze and Iron Age", W + "Cypriot_Bichrome_ware"),
                k("Barrel-shaped jug", "Sub-types", "Iron Age jug type of eastern Cypriot tombs, 10th century BCE onward", W + "Barrel-shaped_jug"),
                k("Free-field style", "Schools & phases", "Cypro-Archaic figural decoration on jugs, birds and figures set free in the field", W + "Pottery_of_ancient_Cyprus")],
         collections_from=["Cypriot Pottery"]),
    dict(key="CYPSCU", sub="D5", label="Ancient Cypriot Sculpture", breadth="medium",
         defn="The sculpture of ancient Cyprus: Chalcolithic picrolite cruciform figurines, Bronze Age terracotta plank figures, and the "
              "limestone and terracotta votive statues dedicated in the island's sanctuaries from the Cypro-Archaic to the Hellenistic "
              "period, in a local style that absorbed Near Eastern, Egyptian and Greek forms.",
         aliases="Cypriot sculpture; Cypro-Archaic sculpture", see="E1-143 Ancient Cypriot Pottery; D5-57 Ancient Greek Sculpture",
         src=[[W + "Ancient_Cypriot_art", "Wikipedia"]],
         catalogues=[met("Cypriot sculpture", "Cypriot limestone and terracotta sculpture in the Metropolitan Museum (Cesnola Collection)"),
                     bm("Cypriot sculpture", "Cypriot sculpture in the British Museum")],
         axis="phases from the Chalcolithic to the Hellenistic period, then holding institutions",
         kinds=[k("Cruciform figurines", "Sub-types", "Chalcolithic picrolite and clay figures with outstretched arms", W + "Prehistoric_Cyprus"),
                k("Plank figures", "Sub-types", "flat terracotta figures of the Early and Middle Cypriot Bronze Age tombs", W + "Ancient_Cypriot_art"),
                k("Cypro-Archaic votive statues", "Schools & phases", "limestone and terracotta votaries of the sanctuaries, 7th–6th century BCE", W + "Ancient_Cypriot_art"),
                k("Cypro-Classical and Hellenistic sculpture", "Schools & phases", "votive and funerary sculpture under growing Greek influence", W + "Ancient_Cypriot_art")],
         collections_from=["Cypriot Sculpture"]),
    dict(key="SELSTU", sub="D1", label="Seljuk Stucco", breadth="narrow",
         defn="Carved, moulded and painted stucco of the Seljuk lands (11th–13th century): the stucco figures of courtiers, guards and "
              "rulers and the ornamented friezes that lined the inner walls of Seljuk palaces, with the stucco revetments of mosques and tombs.",
         aliases="Seljuk stucco figures; Saljuq stucco", see="D1-1 Samarra Stucco; K1-6 Seljuk Architecture; E2-1 Seljuk Pottery",
         src=[[W + "Seljuk_stucco_figures", "Wikipedia"]],
         catalogues=[met("Seljuq stucco", "Seljuq stucco in the Metropolitan Museum")],
         axis="sub-types (figures, friezes, architectural revetment), then holding institutions",
         kinds=[k("Royal and courtly figures", "Sub-types", "standing and seated stucco figures with crowns, caftans and tiraz bands", W + "Seljuk_stucco_figures"),
                k("Palace friezes", "Sub-types", "ornamented and figural stucco friezes of palace interiors", W + "Seljuk_stucco_figures")],
         collections_from=["Seljuk Stucco"]),
    dict(key="PREPOT", sub="E1", label="Predynastic Egyptian Pottery", breadth="narrow",
         defn="The pottery of prehistoric Upper Egypt, c. 4400–3000 BCE, in Petrie's sequence: Badarian and Naqada black-topped red ware, "
              "the White Cross-lined ware of Naqada I, and the Decorated ware of Naqada II–III painted in red on buff marl clay with "
              "boats, figures and spirals, with the wavy-handled jars used to date the sequence.",
         aliases="Naqada pottery; Amratian pottery; Gerzean pottery", see="E2-15 Egyptian Faience; D5-55 Ancient Egyptian Sculpture",
         src=[[W + "Naqada_culture", "Wikipedia"], [W + "Ancient_Egyptian_pottery", "Wikipedia"]],
         catalogues=[met("Predynastic", "Predynastic Egyptian objects in the Metropolitan Museum"),
                     bm("Naqada", "Naqada finds in the British Museum")],
         axis="wares in the Badarian–Naqada sequence, then holding institutions",
         kinds=[k("Black-topped red ware", "Sub-types", "red burnished pots with blackened rims, Badarian to Naqada II", W + "Naqada_I"),
                k("White Cross-lined ware", "Sub-types", "C-ware: red pottery painted with white lines and figures, Naqada I", W + "Naqada_I"),
                k("Decorated ware", "Sub-types", "D-ware: buff marl pottery painted in red with boats and figures, Naqada II–III", W + "Ancient_Egyptian_pottery"),
                k("Wavy-handled jars", "Sub-types", "the jar type on which Petrie built his sequence dating", W + "Ancient_Egyptian_pottery"),
                k("Badarian", "Schools & phases", "c. 4400–4000 BCE", W + "Art_of_ancient_Egypt"),
                k("Naqada I (Amratian)", "Schools & phases", "c. 4000–3500 BCE", W + "Naqada_I"),
                k("Naqada II–III (Gerzean to Protodynastic)", "Schools & phases", "c. 3500–3000 BCE", W + "Naqada_culture")],
         collections_from=["Predynastic Egyptian Pottery"]),
    dict(key="PARPOT", sub="E1", label="Paracas Pottery", breadth="narrow",
         defn="The pottery of the Paracas culture of the south coast of Peru (first millennium BCE): incised vessels painted after firing "
              "with resin-based colours, double-spout-and-bridge bottles and feline-face bottles, in geometric, zoomorphic and abstract "
              "designs; the forerunner of Nazca polychrome.",
         aliases="Paracas ceramics", see="H4-32 Paracas Textiles; E1-48 Nazca Pottery",
         src=[[W + "Paracas_culture", "Wikipedia"]],
         catalogues=[met("Paracas", "Paracas objects in the Metropolitan Museum"),
                     ["https://www.museolarco.org/", "Museo Larco, Lima", "major Peruvian collection of ancient Andean ceramics, online catalogue"]],
         axis="sub-types, then holding institutions",
         kinds=[k("Post-fire resin-painted ware", "Sub-types", "incised outlines filled with resin-based colours after firing", W + "Paracas_culture"),
                k("Double-spout-and-bridge bottles", "Sub-types", "the characteristic Paracas closed vessel", W + "Paracas_culture")],
         collections_from=["Paracas Pottery"]),
    dict(key="BYZSIL", sub="G1", label="Byzantine Silver", breadth="narrow",
         defn="Silver plate of the Byzantine Empire: domestic tableware with classical and biblical scenes (4th–7th century), church "
              "silver (chalices, patens, processional crosses) and the imperial control stamps that dated it; about 1,500 plates and "
              "crosses survive.",
         aliases="Byzantine silverwork; Byzantine metalwork", see="G1-46 Byzantine Enamel; G1-24 Sasanian Silver; D2-8 Byzantine Ivories",
         src=[[W + "Byzantine_silver", "Wikipedia"]],
         catalogues=[met("Byzantine silver", "Byzantine silver in the Metropolitan Museum"),
                     bm("Byzantine silver", "Byzantine silver in the British Museum")],
         axis="sub-types (domestic plate, church silver, crosses), then holding institutions",
         kinds=[k("Domestic plate", "Sub-types", "dishes and vessels with mythological and biblical scenes, 4th–7th century", W + "Byzantine_silver"),
                k("Liturgical silver", "Sub-types", "chalices, patens and church furnishings", W + "Byzantine_silver"),
                k("Silver crosses", "Sub-types", "processional and altar crosses", W + "Byzantine_silver"),
                k("Imperial control stamps", "Sub-types", "the stamps that regulated and date Byzantine silver", W + "Byzantine_silver")],
         collections_from=["Byzantine Metalwork"]),
    dict(key="ETRBRZ", sub="G1", label="Etruscan Bronzes", breadth="medium",
         defn="The cast and hammered bronze work of Etruria (8th–1st century BCE), widely exported in antiquity: votive statuettes, "
              "vessels and tripods, candelabra and furniture fittings, chariot and armour fittings; engraved mirrors are G1-25.",
         aliases="Etruscan bronzework; Etruscan metalwork", see="G1-25 Etruscan Mirrors; D5-59 Etruscan Sculpture; E1-34 Etruscan Vase Painting",
         src=[[W + "Etruscan_art", "Wikipedia"]],
         catalogues=[met("Etruscan bronze", "Etruscan bronzes in the Metropolitan Museum"),
                     bm("Etruscan bronze", "Etruscan bronzes in the British Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Votive statuettes", "Sub-types", "small cast figures dedicated in sanctuaries", W + "Etruscan_art"),
                k("Vessels and tripods", "Sub-types", "bronze vessels, stands and tripods for elite use and burial", W + "Etruscan_art"),
                k("Candelabra and furniture fittings", "Sub-types", "cast lamp stands and fittings", W + "Etruscan_art"),
                k("Chariot and armour fittings", "Sub-types", "hammered bronze chariot panels, helmets and armour", W + "Etruscan_art")],
         collections_from=["Etruscan Bronzes"]),
    dict(key="ROMMET", sub="G1", label="Roman Metalwork", breadth="medium",
         defn="Metalwork of the Roman world: the silver tableware known from the great hoards of the late empire, bronze vessels, "
              "figurines and household shrine images, and cast fittings for furniture and lamps.",
         aliases="Roman silver; Roman bronzes", see="D5-61 Roman Sculpture; F1-3 Roman Glass; G1-46 Byzantine Enamel",
         src=[[W + "Ancient_Roman_art", "Wikipedia"]],
         catalogues=[met("Roman bronze", "Roman bronzes in the Metropolitan Museum"),
                     bm("Roman silver", "Roman silver and hoards in the British Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Silver tableware and hoards", "Sub-types", "dining silver known from late Roman hoards", W + "Ancient_Roman_art"),
                k("Bronze vessels", "Sub-types", "cast and hammered bronze vessels", W + "Ancient_Roman_art"),
                k("Bronze figurines", "Sub-types", "small cast figures, including household shrine images", W + "Ancient_Roman_art"),
                k("Furniture and lamp fittings", "Sub-types", "cast fittings of couches, lamps and stands", W + "Ancient_Roman_art")],
         collections_from=["Roman Metalwork"]),
    dict(key="EGYJEW", sub="G3", label="Ancient Egyptian Jewellery & Amulets", breadth="medium",
         defn="The jewellery and amulets of pharaonic Egypt, in gold, silver, semi-precious stones and faience: scarabs and scaraboids, "
              "protective amulets of deities and symbols, broad collars, pectorals, rings, bracelets and bead jewellery. Faience as a "
              "material and its vessels are E2-15.",
         aliases="Ancient Egyptian jewelry; Egyptian amulets; Scarabs", see="E2-15 Egyptian Faience; D5-55 Ancient Egyptian Sculpture",
         src=[[W + "Art_of_ancient_Egypt", "Wikipedia"], [W + "Egyptian_faience", "Wikipedia"]],
         catalogues=[met("Egyptian amulet", "Egyptian amulets and scarabs in the Metropolitan Museum"),
                     bm("Egyptian jewellery", "Egyptian jewellery in the British Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Scarabs and scaraboids", "Sub-types", "the commonest Egyptian amulet, often of faience or steatite", W + "Egyptian_faience"),
                k("Protective amulets", "Sub-types", "amulets of deities and symbols worn by the living and the dead", W + "Egyptian_faience"),
                k("Collars, pectorals and bead jewellery", "Sub-types", "broad collars, pectorals and strung bead jewellery", W + "Art_of_ancient_Egypt"),
                k("Flint jewellery", "Sub-types", "flint bracelets and armlets of the prehistoric to early dynastic periods", W + "Ancient_Egyptian_flint_jewelry")],
         collections_from=["Ancient Egyptian Jewellery and Metalwork"]),
    dict(key="PALPNT", sub="A1", label="Pala Painting", breadth="narrow",
         defn="The manuscript painting of Bengal and Bihar under the Pala dynasty (c. 10th–12th century), the earliest surviving Indian "
              "book painting: small panels of Buddhist deities and scenes on the palm leaves and painted wooden covers of Buddhist texts, "
              "above all the Prajnaparamita; the style was carried on in Nepal and Tibet. The manuscripts as books are C2-5.",
         aliases="Pala manuscript painting; Pala-period painting", see="C2-5 Palm-Leaf Manuscripts; D5-4 Pala Art; A4-7 Thangka",
         src=[[W + "Indian_art", "Wikipedia"], [W + "Palm-leaf_manuscript", "Wikipedia"]],
         catalogues=[met("Pala period painting", "Pala-period manuscript pages and covers in the Metropolitan Museum"),
                     bm("Pala manuscript", "Pala manuscripts in the British Museum")],
         axis="sub-types (leaf paintings, painted covers), then holding institutions",
         kinds=[k("Illustrated palm leaves", "Sub-types", "panels of deities and Buddha-life scenes set into the text of the leaves", W + "Palm-leaf_manuscript"),
                k("Painted manuscript covers", "Sub-types", "painted wooden boards that bound the leaves", W + "Indian_art")],
         collections_from=["Pala Manuscript Painting"]),
    dict(key="JAVSCU", sub="D5", label="Classical Javanese Sculpture", breadth="medium",
         defn="The Hindu and Buddhist sculpture of Java from the 8th to the 15th century, in stone and in bronze, silver and gold: the "
              "Central Javanese period of the Sailendra and Mataram kingdoms (Borobudur, Prambanan) and the East Javanese period of "
              "Singhasari and Majapahit (the Prajnaparamita of Java). The temples as buildings are K9-2.",
         aliases="Classical Indonesian sculpture; Hindu-Buddhist art of Java; Central Javanese art; East Javanese art",
         see="K9-2 Candi Architecture; G3-5 Javanese Gold Jewellery",
         src=[[W + "Indonesian_art", "Wikipedia"], [W + "Ancient_monuments_of_Java", "Wikipedia"]],
         catalogues=[met("Javanese sculpture", "Javanese sculpture in the Metropolitan Museum"),
                     bm("Java sculpture", "Javanese sculpture in the British Museum")],
         axis="periods (Central Javanese, East Javanese), then holding institutions",
         kinds=[k("Central Javanese period", "Schools & phases", "8th–10th century, Sailendra and Mataram; Borobudur and Prambanan", W + "Ancient_monuments_of_Java"),
                k("East Javanese period", "Schools & phases", "10th–15th century, Kediri, Singhasari and Majapahit", W + "Archaeology_of_Indonesia"),
                k("Bronze and precious-metal images", "Sub-types", "cast devotional images, as in the Sambas Treasure and the Wonoboyo Hoard", W + "Archaeology_of_Indonesia")],
         collections_from=["Javanese Hindu-Buddhist Sculpture"]),
]

# Held traditions, added on the owner's instruction (2026-11-07, "add held traditions"). Vicús, Turkmen jewellery,
# Greek bronzes and Mughal textiles were attested in a second search; Mamluk pottery, Sasanian seals and Lydian
# pottery cite the parent article; Kwoma bark painting has no article found and carries a Wikipedia search link.
SEARCH = "https://en.wikipedia.org/w/index.php?search="
L += [
    dict(key="MAMPOT", sub="E2", label="Mamluk Pottery", breadth="narrow",
         defn="The pottery of the Mamluk Sultanate of Egypt and Syria (1250–1517): underglaze-painted fritware of Damascus and Cairo, "
              "often in blue and black on white after Chinese porcelain, and the incised and slip-painted sgraffito earthenware with "
              "heraldic blazons and inscriptions naming amirs.",
         aliases="Mamluk ceramics; Mamluk sgraffito; Mamluk blue-and-white", see="G1-3 Mamluk Metalwork; F3-1 Mamluk Enamelled Glass; H1-3 Mamluk Carpet",
         src=[[W + "Mamluk_Sultanate", "Wikipedia (parent article; no article on the pottery found)"]],
         catalogues=[met("Mamluk ceramics", "Mamluk ceramics in the Metropolitan Museum"), bm("Mamluk pottery", "Mamluk pottery in the British Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Underglaze-painted fritware", "Sub-types", "Syrian and Egyptian fritware painted under the glaze, often blue and black on white", W + "Mamluk_Sultanate"),
                k("Sgraffito ware", "Sub-types", "incised slipped earthenware with heraldic blazons and inscriptions", W + "Mamluk_Sultanate")],
         collections_from=["Mamluk Pottery"]),
    dict(key="MUGTEX", sub="H3", label="Mughal Textiles", breadth="medium",
         defn="The court and luxury textiles of Mughal India (16th–18th century): silk and gold-thread brocades and velvets, "
              "embroidered and painted cottons, patka sashes and Kashmir-type shawls, with the flowering-plant designs of Shah Jahan's reign "
              "shared with every other Mughal medium. Carpets are H1-8.",
         aliases="Mughal silks; Mughal velvets; patka", see="H1-8 Mughal Carpet; A1-4 Mughal Painting; G3-2 Mughal Jewellery; H5-3 Indian Chintz",
         src=[[W + "Mughal_clothing", "Wikipedia"]],
         catalogues=[met("Mughal textile", "Mughal textiles in the Metropolitan Museum"),
                     ["https://collections.vam.ac.uk/search/?q=Mughal+textile", "V&A collection search: Mughal textile", "Mughal textiles in the Victoria and Albert Museum"]],
         axis="sub-types, then holding institutions",
         kinds=[k("Brocades and velvets", "Sub-types", "silk and gold-thread figured silks and velvets of the court workshops", W + "Mughal_clothing"),
                k("Patka sashes", "Sub-types", "the long court sash, woven or painted, with floral end panels", W + "Mughal_clothing"),
                k("Embroidered textiles", "Sub-types", "silk and metal-thread embroidery on satin and cotton", W + "Mughal_clothing")],
         collections_from=["Mughal Textiles"]),
    dict(key="GRKBRZ", sub="G1", label="Ancient Greek Bronzes", breadth="medium",
         defn="The bronze work of ancient Greece from the Geometric to the Hellenistic period, apart from monumental statuary (D5-57): "
              "votive figurines, tripods and cauldrons, hydriae, kraters and other vessels exported as far as the Celts (the Vix Krater), "
              "polished mirrors with caryatid handles and later folding mirrors, and armour.",
         aliases="Greek bronzes; Greek metalwork", see="D5-57 Ancient Greek Sculpture; G1-70 Etruscan Bronzes; G1-25 Etruscan Mirrors",
         src=[[W + "Ancient_Greek_art", "Wikipedia"]],
         catalogues=[met("Greek bronze", "Greek bronzes in the Metropolitan Museum"), bm("Greek bronze", "Greek bronzes in the British Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Votive figurines", "Sub-types", "small cast figures dedicated in sanctuaries, from the Geometric period", W + "Ancient_Greek_art"),
                k("Vessels", "Sub-types", "tripods, cauldrons, hydriae and kraters, among them the Vix Krater", W + "Ancient_Greek_art"),
                k("Mirrors", "Sub-types", "stand mirrors with caryatid handles and later folding mirrors", W + "Ancient_Greek_art")],
         collections_from=["Ancient Greek Bronzes"]),
    dict(key="SASSEA", sub="D3", label="Sasanian Seals", breadth="narrow",
         defn="The engraved stamp seals and seal impressions of Sasanian Iran (224–651): hemispherical and ring-set stamp seals in "
              "chalcedony, carnelian and other hardstones cut with portraits, animals, monograms and Middle Persian inscriptions, and the "
              "clay bullae that carry their impressions.",
         aliases="Sasanian glyptic; Sasanian stamp seals; Sasanian gems", see="D3-5 Cylinder Seals; G1-24 Sasanian Silver; L1-12 Sasanian Rock Reliefs",
         src=[[W + "Sasanian_art", "Wikipedia (parent article; no article on the seals found)"]],
         catalogues=[met("Sasanian seal", "Sasanian seals in the Metropolitan Museum"), bm("Sasanian seal", "Sasanian seals in the British Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Stamp seals", "Sub-types", "hardstone stamp seals cut with portraits, animals and inscriptions", W + "Sasanian_art"),
                k("Bullae", "Sub-types", "clay sealings carrying seal impressions", W + "Sasanian_art")],
         collections_from=["Sasanian Stamp Seals"]),
    dict(key="LYDPOT", sub="E1", label="Lydian Pottery", breadth="narrow",
         defn="The pottery of Lydia in western Anatolia, centred on Sardis (8th–6th century BCE): streaked and marbled wares, "
              "black-on-red and bichrome painted vessels in an East Greek-related style, and the lydion, the footed spherical perfume jar "
              "named after Lydia and adopted by Greek potters.",
         aliases="Lydian ware; Sardis pottery; lydion", see="E1-30 East Greek Vase Painting; K3 Ancient Mediterranean & Near Eastern Architecture",
         src=[[W + "Lydion", "Wikipedia"], [W + "Lydia", "Wikipedia (parent article)"]],
         catalogues=[met("Lydian", "Lydian objects in the Metropolitan Museum (Sardis excavation share)")],
         axis="sub-types, then holding institutions",
         kinds=[k("Lydion", "Sub-types", "the footed spherical perfume jar of Lydian origin", W + "Lydion"),
                k("Streaked and marbled ware", "Sub-types", "Lydian fine ware with streaked or marbled slip", W + "Lydia")],
         collections_from=["Lydian Pottery"]),
    dict(key="TURJEW", sub="G3", label="Turkmen Jewellery", breadth="narrow",
         defn="The silver jewellery of the Turkmen of Central Asia and northeast Iran (19th–early 20th century), made by men for "
              "women and horses: fire-gilded silver set with carnelian and turquoise, crowns and headbands, braid ornaments, cordiform "
              "pendants, amulet holders, collar studs and armbands; worn as wealth, rank and protection, with tribal styles (Teke, Yomut).",
         aliases="Turkmen jewelry; Turkmen silver", see="H1-5 Turkmen Carpet; H4-16 Turkmen Needlework",
         src=[[W + "Turkmen_jewelry", "Wikipedia"]],
         catalogues=[met("Turkmen jewelry", "Turkmen jewellery in the Metropolitan Museum (Wolf collection)")],
         axis="sub-types and tribal styles, then holding institutions",
         kinds=[k("Cordiform pendants", "Sub-types", "large heart-shaped dorsal ornaments", W + "Turkmen_jewelry"),
                k("Amulet holders", "Sub-types", "triangular and tubular silver amulet cases", W + "Turkmen_jewelry"),
                k("Crowns and headbands", "Sub-types", "women's headgear jewellery", W + "Turkmen_jewelry"),
                k("Teke jewellery", "Schools & phases", "Merv oasis: bold fire-gilded and plain silver with table-cut carnelians", W + "Turkmen_jewelry"),
                k("Yomut jewellery", "Schools & phases", "Yomut tribal style", W + "Turkmen_jewelry")],
         collections_from=["Turkmen Jewellery"]),
    dict(key="VICMET", sub="G1", label="Vicús Metalwork", breadth="narrow",
         defn="The metalwork of the Vicús culture of the upper Piura valley, far north coast of Peru (c. 200 BCE–600 CE): hammered and "
              "gilt copper and gold ornaments, masks, crowns, nose and ear ornaments and plaques for high-ranking individuals, in a style "
              "of its own beside the Moche.",
         aliases="Vicús gold; Vicús copper", see="E1-57 Chulucanas Pottery",
         src=[[W + "Vicús_culture", "Wikipedia"]],
         catalogues=[met("Vicús", "Vicús metalwork in the Metropolitan Museum"),
                     ["https://www.museolarco.org/", "Museo Larco, Lima", "major Peruvian collection of ancient Andean ceramics, online catalogue"]],
         axis="sub-types, then holding institutions",
         kinds=[k("Gilt copper ornaments", "Sub-types", "hammered and gilt copper plaques, pectorals and nose ornaments", W + "Vicús_culture"),
                k("Masks and crowns", "Sub-types", "copper masks and metal crowns of rank", W + "Vicús_culture")],
         collections_from=["Vicús Metalwork"]),
    dict(key="KWOBRK", sub="A6", label="Kwoma Bark Painting", breadth="narrow",
         defn="The painted sago-palm bark panels of the Kwoma of the Washkuk Hills, upper Sepik, Papua New Guinea, made to line the "
              "ceilings of ceremonial houses with clan designs and spirit figures in ochre, white and black. Arnhem Land bark painting is A6-18.",
         aliases="Kwoma ceiling paintings; Kwoma painted panels", see="A6-18 Bark Painting; D5-85 Sepik Carving",
         src=[[SEARCH + "Kwoma+painting", "Wikipedia search (no article found)"]],
         catalogues=[met("Kwoma", "Kwoma painted panels in the Metropolitan Museum")],
         axis="holding institutions",
         kinds=[],
         collections_from=["Kwoma Bark Painting"]),
]

# Region x medium sweep (owner, 2026-11-07, "vet the 15 flagged cells"; completeness check V8). Each leaf answers a
# medium x region cell where the museum records or the sourcing grid show a body of work and the tree had none.
L += [
    dict(key="INDCHR", sub="B2", label="Indian Chromolithographs", breadth="medium",
         defn="Colour lithographs of gods, epics and national heroes printed in India from the 1870s for the popular market: "
              "the Calcutta Art Studio, the Chitrashala Press of Pune and the Ravi Varma Press (Bombay 1894, then Malavli), whose "
              "prints after Raja Ravi Varma fixed the modern image of the Hindu gods; the source of the later calendar and bazaar print.",
         aliases="Indian oleographs; bazaar prints; calendar art; Ravi Varma prints", see="A6 Folk & Popular Painting; A5 Easel Painting",
         src=[[W + "Raja_Ravi_Varma", "Wikipedia"]],
         catalogues=[bm("Ravi Varma Press", "Ravi Varma Press prints in the British Museum"),
                     ["https://collections.vam.ac.uk/search/?q=chromolithograph+India", "V&A collection search: Indian chromolithographs", "Indian popular prints in the Victoria and Albert Museum"]],
         axis="presses in order of founding, then holding institutions",
         kinds=[k("Calcutta Art Studio", "Centres & workshops", "Calcutta, from the 1870s", W + "Raja_Ravi_Varma"),
                k("Chitrashala Press", "Centres & workshops", "Pune, from 1878", W + "Raja_Ravi_Varma"),
                k("Ravi Varma Press", "Centres & workshops", "Bombay 1894, Malavli 1899", W + "Raja_Ravi_Varma")],
         collections_from=["Indian Chromolithographs"]),
    dict(key="DEIPHO", sub="J1", label="Photography in the Dutch East Indies", breadth="medium",
         defn="Photography made in the Dutch East Indies (Indonesia) from the 1850s to 1949: the studio and topographic work of "
              "Woodbury & Page and Isidore van Kinsbergen, archaeological survey photographs of Borobudur and Prambanan, colonial "
              "ethnographic photography, and Kassian Cephas, court photographer at Yogyakarta and the first Indonesian professional.",
         aliases="Netherlands Indies photography; colonial photography of Indonesia", see="J1-7 Early Photography; J1-12 Documentary Photography",
         src=[[W + "Kassian_Cephas", "Wikipedia"], ["http://www.photo-web.com.au/gote/01-GN/index.html", "Garden of the East: Photography in Indonesia 1850s–1940s"]],
         catalogues=[["https://collectie.wereldculturen.nl/#/query/foto%20Indonesi%C3%AB", "Wereldmuseum (Tropenmuseum) collection search", "the national collection of Dutch East Indies photographs"],
                     ["https://digitalcollections.universiteitleiden.nl/", "Leiden University Digital Collections (KITLV)", "the KITLV photograph collection of the Indies"]],
         axis="photographers and studios in order of activity, then holding institutions",
         kinds=[k("Woodbury & Page", "Makers", "British studio in Batavia from 1857", "http://www.photo-web.com.au/gote/01-GN/index.html"),
                k("Isidore van Kinsbergen", "Makers", "photographer of Javanese antiquities, 1860s", "http://www.photo-web.com.au/gote/01-GN/index.html"),
                k("Kassian Cephas", "Makers", "Yogyakarta court photographer, 1845–1912", W + "Kassian_Cephas")],
         collections_from=["Photography in the Dutch East Indies"]),
    dict(key="LAPPOT", sub="E1", label="Lapita Pottery", breadth="narrow",
         defn="Low-fired earthenware of the Lapita culture of the western Pacific (c. 1500–500 BCE), tempered with shell or sand and "
              "decorated with dentate-stamped geometric designs, carried from the Bismarck Archipelago to Fiji, Tonga and Samoa by "
              "the ancestors of the Polynesians; plain ware followed it before pottery ceased in Western Polynesia.",
         aliases="Lapita ware; dentate-stamped pottery", see="E1 Sepik Pottery",
         src=[[W + "Lapita_culture", "Wikipedia"]],
         catalogues=[["https://collections.tepapa.govt.nz/search/Lapita", "Te Papa collections search: Lapita", "Lapita sherds and vessels at Te Papa"]],
         axis="sub-types, then holding institutions",
         kinds=[k("Dentate-stamped ware", "Sub-types", "geometric designs pressed with a toothed stamp", W + "Lapita_culture"),
                k("Plain ware", "Sub-types", "the undecorated pottery that followed Lapita", W + "Lapita_culture")],
         collections_from=[]),
    dict(key="SEPPOT", sub="E1", label="Sepik Pottery", breadth="narrow",
         defn="Coiled earthenware of the Sepik River region of Papua New Guinea: the incised and painted storage jars, sago bowls "
              "and hooks of the Sawos and the modelled, face-decorated pots of Aibom on Chambri Lake, traded along the river.",
         aliases="Aibom pottery; Sawos pottery", see="D5-85 Sepik Carving; E1 Lapita Pottery",
         src=[[W + "Sepik", "Wikipedia (the region; no article on the pottery found)"]],
         catalogues=[met("Sepik pottery", "Sepik pottery in the Metropolitan Museum")],
         axis="centres, then holding institutions",
         kinds=[k("Aibom", "Centres & workshops", "Chambri Lake pottery village", W + "Sepik"),
                k("Sawos", "Centres & workshops", "villages north of the middle Sepik", W + "Sepik")],
         collections_from=["Sepik pottery"]),
    dict(key="LBAGLA", sub="F1", label="Late Bronze Age Glass", breadth="narrow",
         defn="The first glass vessels, made in Mesopotamia and New Kingdom Egypt c. 1500–1100 BCE by core-forming over a removable "
              "core, by casting and as mosaic glass, for temples, palaces and elite burials; the Mediterranean core-formed industry of "
              "the 6th–1st century BCE is F1-4.",
         aliases="Mesopotamian glass; New Kingdom glass; core-formed glass (Bronze Age)", see="F1-4 Hellenistic Glass; E2-15 Egyptian Faience",
         src=[["https://resources.metmuseum.org/resources/metpublications/pdf/Ars_Vitraria_Glass_in_The_Metropolitan_Museum_of_Art_The_Metropolitan_Museum_of_Art_Bulletin_v_59_no_1_Summer_2001.pdf", "The Met, Ars Vitraria (2001)"],
              ["https://www.getty.edu/publications/ancient-glass/", "Getty, Ancient Glass in the J. Paul Getty Museum"]],
         catalogues=[met("core-formed glass", "core-formed glass in the Metropolitan Museum"), bm("Egyptian glass", "Egyptian glass in the British Museum")],
         axis="techniques, then holding institutions",
         kinds=[k("Bronze Age core-formed vessels", "Sub-types", "glass trailed over a removable core", "https://www.getty.edu/publications/ancient-glass/"),
                k("Cast and mosaic glass", "Sub-types", "glass cast in moulds or fused from coloured canes", "https://www.getty.edu/publications/ancient-glass/")],
         collections_from=[]),
    dict(key="TIBARM", sub="G2", label="Tibetan Arms and Armour", breadth="narrow",
         defn="The decorated arms, armour and horse equipment of Tibet's elite (12th–19th century): lamellar armour, helmets, "
              "swords with chased and pierced iron and silver mounts, saddles and stirrups in damascened iron, many made for "
              "aristocrats, monasteries and ceremonial cavalry.",
         aliases="Tibetan armor; Tibetan weapons", see="D5-11 Tibetan Buddhist Sculpture; H1-13 Tibetan Rug",
         src=[[W + "Tibetan_art", "Wikipedia (secular art)"]],
         catalogues=[met("Tibetan arms and armor", "Tibetan arms and armour in the Metropolitan Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Lamellar armour", "Sub-types", "armour of laced iron plates", W + "Tibetan_art"),
                k("Horse equipment", "Sub-types", "saddles, stirrups and bridles in decorated iron", W + "Tibetan_art")],
         collections_from=["Tibetan Arms and Armour"]),
    dict(key="KULVAL", sub="G3", label="Kula Valuables", breadth="narrow",
         defn="The shell valuables exchanged in the Kula ring of the Massim islands of Papua New Guinea: mwali armshells travelling "
              "one way round the ring and soulava necklaces of red spondylus shell discs travelling the other, each with its own "
              "history of owners.",
         aliases="mwali; soulava; bagi", see="H9 Beadwork, Quillwork & Featherwork",
         src=[[W + "Kula_ring", "Wikipedia"]],
         catalogues=[bm("Massim armshell", "Massim armshells and necklaces in the British Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Mwali", "Sub-types", "white conus-shell armshells", W + "Kula_ring"),
                k("Soulava", "Sub-types", "necklaces of red spondylus shell discs", W + "Kula_ring")],
         collections_from=[]),
    dict(key="BYZSLK", sub="H3", label="Byzantine Silk", breadth="narrow",
         defn="Silk woven in the Byzantine Empire from about the 4th century to 1453, Constantinople being Europe's first great "
              "silk-weaving centre: imperial and church samites with lions, eagles, hunters and charioteers, used as diplomatic gifts "
              "and as shrouds for relics, and regulated as an imperial monopoly.",
         aliases="Byzantine samite; Constantinople silk", see="H3-27 Coptic Textiles; G1-69 Byzantine Silver; G1-46 Byzantine Enamel",
         src=[[W + "Byzantine_silk", "Wikipedia"]],
         catalogues=[met("Byzantine silk", "Byzantine silks in the Metropolitan Museum"),
                     ["https://collections.vam.ac.uk/search/?q=Byzantine+silk", "V&A collection search: Byzantine silk", "Byzantine silks in the Victoria and Albert Museum"]],
         axis="sub-types, then holding institutions",
         kinds=[k("Samite", "Sub-types", "weft-faced compound twill of the imperial workshops", W + "Byzantine_silk")],
         collections_from=[]),
    dict(key="BHUTEX", sub="H3", label="Bhutanese Textiles", breadth="medium",
         defn="The handwoven textiles of Bhutan, woven by women on backstrap and frame looms for the kira and gho and for gifts that "
              "mark births, deaths, weddings and honours: plain weaves, warp-pattern weaves, and the continuous (sapma) and "
              "discontinuous (tigma) supplementary-weft patterns of the silk kishuthara and woollen yathra.",
         aliases="kishuthara; yathra; kira; gho", see="A4 Cloth & Scroll Painting; H1-13 Tibetan Rug",
         src=[[W + "Textiles_of_Bhutan", "Wikipedia"], [W + "Bhutanese_art", "Wikipedia"]],
         catalogues=[["https://www.textile.gov.bt/", "Royal Textile Academy of Bhutan", "the national textile museum in Thimphu"],
                     met("Bhutanese textile", "Bhutanese textiles in the Metropolitan Museum")],
         axis="weaves, then holding institutions",
         kinds=[k("Kishuthara", "Sub-types", "silk kira with dense supplementary-weft patterns", W + "Textiles_of_Bhutan"),
                k("Yathra", "Sub-types", "vegetable-dyed woollen cloth of Bumthang", W + "Bhutanese_art"),
                k("Warp-pattern weaves", "Sub-types", "patterns made by the warp", W + "Textiles_of_Bhutan"),
                k("Sapma and tigma", "Sub-types", "continuous and discontinuous supplementary-weft patterns", W + "Textiles_of_Bhutan")],
         collections_from=[]),
    dict(key="GLKBEA", sub="H9", label="Great Lakes Floral Beadwork", breadth="medium",
         defn="Floral glass-bead embroidery of the Anishinaabe (Ojibwe, Odawa, Potawatomi), Ho-Chunk and Menominee of the Great Lakes, "
              "learned in part from Ursuline nuns' floral needlework: bandolier bags (gashkibidaagan), moccasins, leggings, garters and "
              "shirts, with loom-woven as well as spot-stitched work.",
         aliases="Woodlands floral beadwork; Ojibwe beadwork; bandolier bags", see="H9-6 Plains Beadwork; H9-7 Haudenosaunee Raised Beadwork; H4-39 Ribbonwork",
         src=[[W + "Beadwork", "Wikipedia (Great Lakes tribes)"]],
         catalogues=[["https://collections.si.edu/search/results.htm?q=Ojibwe+beadwork&fq=data_source%3A%22National+Museum+of+the+American+Indian%22", "Smithsonian NMAI search: Ojibwe beadwork", "Great Lakes beadwork in the National Museum of the American Indian"]],
         axis="peoples, then holding institutions",
         kinds=[k("Bandolier bags (gashkibidaagan)", "Sub-types", "fully beaded shoulder bags", W + "Beadwork")],
         collections_from=["Great Lakes floral beadwork"]),
    dict(key="SUBBEA", sub="H9", label="Subarctic Floral Beadwork", breadth="medium",
         defn="Floral glass-bead embroidery on hide and stroud of the Cree, Dene and Métis of the Canadian Subarctic, the Métis being "
              "known as the Flower Beadwork People: moccasins, mittens, gauntlets, octopus bags and tunics, from the 19th century, "
              "alongside moosehair and porcupine-quill embroidery.",
         aliases="Métis floral beadwork; Flower Beadwork People; Cree beadwork; Dene beadwork", see="H4-40 Moosehair Embroidery; H9-6 Plains Beadwork",
         src=[[W + "Beadwork", "Wikipedia (Métis Nation)"], [W + "Indigenous_peoples_of_the_Subarctic", "Wikipedia"], [W + "Métis_Art", "Wikipedia"]],
         catalogues=[["https://collections.si.edu/search/results.htm?q=Cree+beadwork&fq=data_source%3A%22National+Museum+of+the+American+Indian%22", "Smithsonian NMAI search: Cree beadwork", "Subarctic beadwork in the National Museum of the American Indian"]],
         axis="peoples, then holding institutions",
         kinds=[k("Métis", "Sub-types", "the Flower Beadwork People", W + "Métis_Art"),
                k("Cree and Dene", "Sub-types", "Subarctic First Nations floral beadwork", W + "Indigenous_peoples_of_the_Subarctic")],
         collections_from=["Subarctic beadwork"]),
]

# Ceramics x Ancient Near East (V8, 34 traditions in the sourcing grid against 2 leaves): the prehistoric painted wares
# of Mesopotamia, each with its own article.
L += [
    dict(key="SAMWAR", sub="E1", label="Samarra Ware", breadth="narrow",
         defn="Painted pottery of the Samarra culture of northern and central Mesopotamia (c. 6200–5700 BCE): fine buff wares "
              "painted in dark brown with geometric bands and whirling figures of women, birds, fish and scorpions, named after the "
              "finds at Samarra on the Tigris.",
         aliases="Samarran pottery", see="E1 Halaf Pottery; E1 Ubaid Pottery",
         src=[[W + "Samarra_culture", "Wikipedia"]],
         catalogues=[bm("Samarra pottery", "Samarra pottery in the British Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Whirl-motif bowls", "Sub-types", "bowls painted with whirling women, birds, fish and scorpions", W + "Samarra_culture"),
                k("Geometric banded ware", "Sub-types", "buff ware with dark geometric bands", W + "Samarra_culture")], collections_from=[]),
    dict(key="HALPOT", sub="E1", label="Halaf Pottery", breadth="narrow",
         defn="The polychrome painted pottery of the Halaf culture of northern Mesopotamia and Syria (c. 6100–5100 BCE), fired in "
              "two-chambered kilns: thin-walled bowls and jars painted in red, black and white with bucrania, rosettes, Maltese "
              "squares and checker patterns.",
         aliases="Halafian pottery", see="E1 Samarra Ware; E1 Ubaid Pottery",
         src=[[W + "Halaf_culture", "Wikipedia"]],
         catalogues=[met("Halaf", "Halaf pottery in the Metropolitan Museum"), bm("Halaf", "Halaf pottery in the British Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Polychrome bowls", "Sub-types", "thin-walled bowls painted in red, black and white", W + "Halaf_culture"),
                k("Bucranium motif", "Sub-types", "bull's-head decoration", W + "Halaf_culture")], collections_from=[]),
    dict(key="UBAPOT", sub="E1", label="Ubaid Pottery", breadth="narrow",
         defn="The greenish-buff pottery of the Ubaid period of Mesopotamia (c. 5500–3700 BCE), painted in dark geometric designs and "
              "increasingly made on the slow wheel, spread from southern Iraq to the Gulf and Anatolia before the Uruk period.",
         aliases="Ubaid ware", see="E1 Samarra Ware; E1 Halaf Pottery",
         src=[[W + "Ubaid_period", "Wikipedia"]],
         catalogues=[bm("Ubaid", "Ubaid pottery in the British Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Painted buff ware", "Sub-types", "greenish-buff ware with dark geometric painting", W + "Ubaid_period"),
                k("Slow-wheel ware", "Sub-types", "later Ubaid pottery made on the tournette", W + "Ubaid_period")], collections_from=[]),
]

# Remaining open traditions (owner, 2026-11-07, "fill the remaining gaps"): open names from the collections mapping with
# >= 50 objects that are attested, and the Pacific clubs left partly covered by I1-15. Not attested here, so not added:
# Mezcala sculpture, Fon brass, Irish cut glass, Shipibo-Conibo textiles, kava bowls, Pacific headrests; Gupta sculpture
# is D5-2 Art of Mathura.
L += [
    dict(key="BMACMT", sub="G1", label="Bactria–Margiana Metalwork", breadth="narrow",
         defn="Metalwork of the Bronze Age Oxus civilisation (Bactria–Margiana Archaeological Complex, c. 2300–1700 BCE) of southern "
              "Central Asia: cast copper-alloy shaft-hole axes and pins with animal and demon finials, compartmented seals and "
              "animal figurines, beside the composite chlorite figures of 'Bactrian princesses'.",
         aliases="BMAC metalwork; Oxus civilisation bronzes", see="G1-23 Achaemenid Metalwork; D3-5 Cylinder Seals",
         src=[[W + "Bactria–Margiana_Archaeological_Complex", "Wikipedia"]],
         catalogues=[met("Bactria-Margiana", "Bactria–Margiana objects in the Metropolitan Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Shaft-hole axes", "Sub-types", "ceremonial axes with animal and demon heads", W + "Bactria–Margiana_Archaeological_Complex"),
                k("Compartmented seals", "Sub-types", "cast metal stamp seals", W + "Bactria–Margiana_Archaeological_Complex"),
                k("Animal figurines", "Sub-types", "cast camels and other animals", W + "Bactria–Margiana_Archaeological_Complex")],
         collections_from=["Bactria-Margiana Metalwork"]),
    dict(key="LACLEA", sub="G1", label="Laconian Lead Votives", breadth="narrow",
         defn="Small cast lead figurines dedicated by the tens of thousands at the sanctuary of Artemis Orthia and other shrines of "
              "Sparta (7th–5th century BCE): warriors, women, deities including a winged goddess, musicians, dancers and horsemen.",
         aliases="Laconian lead figurines; Spartan lead votives", see="E1-29 Laconian Vase Painting; D5-58 Greek Terracotta Figurines",
         src=[[W + "Sanctuary_of_Artemis_Orthia", "Wikipedia"]],
         catalogues=[met("Laconian lead", "Laconian lead figurines in the Metropolitan Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Warriors", "Sub-types", "the most common type", W + "Sanctuary_of_Artemis_Orthia"),
                k("Winged goddess", "Sub-types", "possibly Artemis Orthia", W + "Sanctuary_of_Artemis_Orthia"),
                k("Musicians and dancers", "Sub-types", "flute, lyre and cymbal players", W + "Sanctuary_of_Artemis_Orthia")],
         collections_from=["Laconian Lead Figurines"]),
    dict(key="VILBRZ", sub="G1", label="Villanovan Bronzes", breadth="narrow",
         defn="Bronze work of the Villanovan culture of Iron Age Italy (c. 900–700 BCE), the forerunner of the Etruscans: crested "
              "helmets, hut-shaped and biconical cinerary urns in bronze, fibulae, razors and belts with incised geometric ornament.",
         aliases="Italic bronzes; Early Iron Age Italian bronzes", see="G1-70 Etruscan Bronzes; D5-59 Etruscan Sculpture",
         src=[[W + "Villanovan_culture", "Wikipedia"]],
         catalogues=[met("Villanovan", "Villanovan objects in the Metropolitan Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Crested helmets", "Sub-types", "hammered bronze helmets", W + "Villanovan_culture"),
                k("Fibulae and razors", "Sub-types", "personal bronzes from cremation graves", W + "Villanovan_culture")],
         collections_from=["Italic Bronzes"]),
    dict(key="SHUSCU", sub="D5", label="Shunga Sculpture", breadth="narrow",
         defn="Sculpture of the Shunga period in north and central India (2nd–1st century BCE), more indigenous in style than the "
              "imperial Mauryan: yakshas and yakshis, the railing reliefs of the stupa at Bharhut, and terracotta plaques of couples "
              "and royal families, notably from West Bengal (Chandraketugarh).",
         aliases="Sunga art; Shunga terracottas", see="D5-2 Art of Mathura; K7-8 Buddhist Architecture",
         src=[[W + "Shunga_Empire", "Wikipedia (art)"]],
         catalogues=[met("Shunga", "Shunga objects in the Metropolitan Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Yakshas and yakshis", "Sub-types", "nature-spirit figures", W + "Shunga_Empire"),
                k("Bharhut railing reliefs", "Sub-types", "carved stupa railing", W + "Shunga_Empire"),
                k("Terracotta plaques", "Sub-types", "couples and royal families", W + "Shunga_Empire")],
         collections_from=["Shunga Art"]),
    dict(key="BATSCU", sub="D5", label="Batak Sculpture", breadth="narrow",
         defn="Wood and stone sculpture of the Batak of North Sumatra: the sigale-gale funeral puppet, singa heads on houses and "
              "sarcophagi, ancestor figures and the carved finials of priests' staffs.",
         aliases="Toba Batak carving; sigale-gale", see="K9-10 Batak Architecture; C2-9 Pustaha",
         src=[[W + "Sigalegale", "Wikipedia"], [W + "Indonesian_art", "Wikipedia"]],
         catalogues=[met("Batak", "Batak objects in the Metropolitan Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Sigale-gale", "Sub-types", "life-size wooden funeral puppet", W + "Sigalegale"),
                k("Ancestor figures", "Sub-types", "wood and stone figures", W + "Indonesian_art")],
         collections_from=["Batak Sculpture"]),
    dict(key="DAYSCU", sub="D5", label="Dayak Sculpture", breadth="narrow",
         defn="Wood carving of the Dayak peoples of Borneo: guardian and ancestor figures set before houses and graves, carved "
              "masks such as the hudoq of the Bahau and Modang, and ornamented burial structures.",
         aliases="hampatong; Dayak carving", see="D4 Masks & Puppets",
         src=[[W + "Indonesian_art", "Wikipedia"]],
         catalogues=[met("Dayak", "Dayak objects in the Metropolitan Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Guardian figures", "Sub-types", "figures before houses and graves", W + "Indonesian_art"),
                k("Hudoq masks", "Sub-types", "masks of the hudoq dance", W + "Indonesian_art")],
         collections_from=["Dayak Sculpture"]),
    dict(key="CHALAC", sub="H4", label="Chantilly Lace", breadth="narrow",
         defn="Handmade bobbin lace named after Chantilly in France, from the 17th century: above all black silk lace with floral "
              "patterns shaded by half-stitch and whole-stitch fillings, for shawls, scarves and mantillas, revived under Napoleon I "
              "and later made at Bayeux and Caen.",
         aliases="Point de Chantilly; black silk lace", see="H4-53 Alençon Lace; H4-44 Bucks Point Lace",
         src=[[W + "Chantilly_lace", "Wikipedia"]],
         catalogues=[met("Chantilly lace", "Chantilly lace in the Metropolitan Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Black silk lace", "Sub-types", "the best-known Chantilly", W + "Chantilly_lace"),
                k("Shawls and mantillas", "Sub-types", "large Chantilly pieces", W + "Chantilly_lace")],
         collections_from=["Chantilly Lace"]),
    dict(key="LYOSLK", sub="H3", label="Lyon Silk", breadth="medium",
         defn="The figured silks of Lyon, France's silk capital from the 16th century: brocades, damasks and velvets for dress and "
              "furnishing designed by pattern draughtsmen, woven by the canuts of the Croix-Rousse, from the 19th century on Jacquard looms.",
         aliases="soieries lyonnaises; Lyonnais silk", see="H3 Woven Silks & Figured Textiles",
         src=[[W + "Silk_industry_in_Lyon", "Wikipedia"], [W + "Canut", "Wikipedia"]],
         catalogues=[["https://collections.vam.ac.uk/search/?q=Lyon+silk", "V&A collection search: Lyon silk", "Lyon silks in the Victoria and Albert Museum"],
                     met("Lyon silk", "Lyon silks in the Metropolitan Museum")],
         axis="sub-types and phases, then holding institutions",
         kinds=[k("Brocades and damasks", "Sub-types", "figured dress and furnishing silks", W + "Silk_industry_in_Lyon"),
                k("Canuts of the Croix-Rousse", "Centres & workshops", "the weavers' district", W + "Canut"),
                k("Jacquard weaving", "Schools & phases", "from the early 19th century", W + "Silk_industry_in_Lyon")],
         collections_from=["Lyon Silk"]),
    dict(key="TRIPOT", sub="E1", label="Triana Pottery", breadth="narrow",
         defn="The tin-glazed pottery and tiles of Triana, the potters' quarter of Seville across the Guadalquivir: cuerda seca and "
              "cuenca (arista) tiles and later painted azulejos and maiolica, the tile industry that clad Seville's buildings.",
         aliases="Seville pottery; Sevillian azulejos", see="L3 Mosaic & Tile Revetment; E1-81 Talavera de la Reina Pottery",
         src=[[W + "Triana,_Seville", "Wikipedia (pottery and tile industry)"]],
         catalogues=[["https://collections.vam.ac.uk/search/?q=Seville+tile", "V&A collection search: Seville tiles", "Seville tiles and pottery in the Victoria and Albert Museum"]],
         axis="sub-types, then holding institutions",
         kinds=[k("Azulejos", "Sub-types", "painted and moulded tiles", W + "Triana,_Seville"),
                k("Triana", "Centres & workshops", "Seville", W + "Triana,_Seville")],
         collections_from=["Seville Pottery"]),
    dict(key="SESPOT", sub="E1", label="Sesklo Pottery", breadth="narrow",
         defn="The painted pottery of the Neolithic Sesklo culture of Thessaly (7th–6th millennium BCE), among the earliest in Europe: "
              "red-on-white wares with geometric designs turning to flame motifs late in the culture, followed by the Dimini wares.",
         aliases="Thessalian Neolithic pottery; Sesklo ware", see="E1-25 Geometric Pottery",
         src=[[W + "Late_Neolithic", "Wikipedia (Sesklo culture)"]],
         catalogues=[bm("Sesklo", "Thessalian Neolithic pottery in the British Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Sesklo red-on-white ware", "Sub-types", "geometric painted ware", W + "Late_Neolithic"),
                k("Flame-motif ware", "Schools & phases", "late Sesklo", W + "Late_Neolithic")],
         collections_from=["Thessalian Neolithic Pottery"]),
    dict(key="HARPOT", sub="E1", label="Harappan Pottery", breadth="narrow",
         defn="The wheel-made pottery of the Indus Valley Civilisation (c. 3300–1300 BCE): fine red ware painted in black with "
              "intersecting circles, pipal leaves and fish-scale patterns, large storage jars, dishes-on-stand and perforated jars.",
         aliases="Indus pottery; black-on-red ware", see="K7-17 Harappan Architecture",
         src=[[W + "Pottery_in_the_Indian_subcontinent", "Wikipedia (Indus Valley Civilisation)"]],
         catalogues=[met("Harappan", "Harappan objects in the Metropolitan Museum")],
         axis="sub-types, then holding institutions",
         kinds=[k("Black-on-red painted ware", "Sub-types", "fine red ware painted in black", W + "Pottery_in_the_Indian_subcontinent"),
                k("Dish-on-stand", "Sub-types", "characteristic Harappan form", W + "Pottery_in_the_Indian_subcontinent"),
                k("Perforated jars", "Sub-types", "characteristic Harappan form", W + "Pottery_in_the_Indian_subcontinent")],
         collections_from=["Harappan Pottery"]),
    dict(key="POLCLB", sub="I1", label="Polynesian Clubs", breadth="narrow",
         defn="The carved hardwood, bone and stone clubs of Polynesia beyond Fiji (I1-15): the Marquesan u'u with its carved head, "
              "the Māori long clubs (taiaha, tewhatewha, pouwhenua) and short clubs (patu, wahaika, kotiate), and the clubs of Tonga and Samoa.",
         aliases="u'u; taiaha; patu; Māori weapons", see="I1-15 Fijian Clubs; D3-9 Hei-tiki",
         src=[[W + "U'u", "Wikipedia"], [W + "Taiaha", "Wikipedia"], [W + "Patu", "Wikipedia"]],
         catalogues=[["https://collections.tepapa.govt.nz/search/taiaha", "Te Papa collections search: taiaha", "Māori clubs at Te Papa"],
                     bm("Polynesian club", "Polynesian clubs in the British Museum")],
         axis="island groups, then holding institutions",
         kinds=[k("U'u", "Sub-types", "Marquesan war club", W + "U'u"),
                k("Taiaha", "Sub-types", "Māori long club", W + "Taiaha"),
                k("Patu", "Sub-types", "Māori short club of wood, bone or stone", W + "Patu")],
         collections_from=[]),
]

json.dump(dict(leaves={}, new_leaves=L, moves_out=[], dropped=[]),
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "result.json"), "w"), ensure_ascii=False, indent=1)
print(len(L), "new leaves")
