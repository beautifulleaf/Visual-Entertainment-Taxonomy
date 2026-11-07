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

json.dump(dict(leaves={}, new_leaves=L, moves_out=[], dropped=[]),
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "result.json"), "w"), ensure_ascii=False, indent=1)
print(len(L), "new leaves")
