from xh import *
E, X = {}, {}
D = ("dup",)
def drop(r): return ("drop", r)
LBL = drop("tradition bucket label from the gathered data; its sites are expanded in the catalogue")

RA_AX = "Sub-types and phases first, then the sites catalogue sectioned by region of the tradition, then makers where named."

E["L1-1"] = dict(axis=RA_AX, catalogues=[UN(925, "Rock Shelters of Bhimbetka"), ASI, WP("Bhimbetka rock shelters", "site article with phases and shelter numbering"), BRAD],
    kinds=[W("Upper Palaeolithic phase", "Schools & phases", "green and dark-red linear figures of large animals; earliest layer at Bhimbetka", "Bhimbetka rock shelters"),
           W("Mesolithic phase", "Schools & phases", "the bulk of the paintings: hunting, dancing and honey-gathering scenes in red and white", "Bhimbetka rock shelters"),
           W("Chalcolithic phase", "Schools & phases", "scenes of contact with farming communities, cattle and exchange", "Bhimbetka rock shelters"),
           W("Early historic and medieval phases", "Schools & phases", "riders, warriors and religious symbols in red, white and yellow", "Bhimbetka rock shelters")])
X[("L1-1", "Central Indian rock shelters")] = drop("section label; the Central Indian shelters are listed individually")

E["L1-2"] = dict(axis=RA_AX, catalogues=[UN(1382, "Petroglyphic Complexes of the Mongolian Altai"), WP("Petroglyphic Complexes of the Mongolian Altai", "site article"), BRAD],
    kinds=[W("Late Pleistocene and early Holocene phase", "Schools & phases", "large wild-animal figures (mammoth, ibex, aurochs) at Tsagaan Salaa and Aral Tolgoi", "Petroglyphic Complexes of the Mongolian Altai"),
           W("Bronze Age phase", "Schools & phases", "chariots, deer stones-style deer and herders; the densest layer", "Petroglyphic Complexes of the Mongolian Altai"),
           W("Early Iron Age and Turkic phase", "Schools & phases", "horse riders, hunters and tamga signs, to the 8th century", "Petroglyphic Complexes of the Mongolian Altai")])
X[("L1-2", "Tsagaan Salaa")] = D

E["L1-3"] = dict(axis=RA_AX, catalogues=[UN(1145, "Petroglyphs within the Archaeological Landscape of Tamgaly"), WP("Tamgaly", "site article"), BRAD],
    kinds=[W("Sun-headed deities", "Sub-types", "Bronze Age anthropomorphs with radiate heads, the emblem of Tamgaly", "Tamgaly"),
           W("Bronze Age (Andronovo) phase", "Schools & phases", "the main engraved panels, c. 1500-1000 BC", "Tamgaly"),
           W("Saka and Turkic phases", "Schools & phases", "Early Iron Age animal style and medieval Turkic additions", "Tamgaly")])
X[("L1-3", "Akkainar and Zhartas")] = D

E["L1-4"] = dict(axis=RA_AX, catalogues=[WP("Leang Tedongnge", "article on the oldest dated figurative painting of the karst"), COM("Maros-Pangkep cave art"), BRAD],
    kinds=[W("Hand stencils", "Sub-types", "sprayed red-ochre hand outlines, some dated to over 39,900 years ago", "Cave painting"),
           W("Figurative animal paintings", "Sub-types", "Sulawesi warty pig and babirusa figures in red ochre", "Leang Tedongnge"),
           W("Narrative hunting scenes", "Sub-types", "therianthropes hunting anoa and pigs, Leang Bulu' Sipong 4, c. 44,000 years ago", "Leang Bulu' Sipong 4")],
    knowledge_sites=[SR("Leang Karampuang", "Maros-Pangkep caves", "Maros, South Sulawesi; figurative scene dated to at least 51,200 years ago (2024)")])

E["L1-5"] = dict(axis=RA_AX, catalogues=[WP("Lubang Jeriji Saléh", "article on the principal dated cave"), UNS("Niah", "UNESCO entry for the Niah National Park caves complex"), BRAD],
    kinds=[W("Hand stencils", "Sub-types", "red and mulberry hand stencils, some joined by lines and dots; earliest c. 37,000 years ago", "Lubang Jeriji Saléh"),
           W("Figurative animal painting", "Sub-types", "banteng-like animal figure at Lubang Jeriji Saléh, at least 40,000 years old", "Lubang Jeriji Saléh"),
           W("Painted Cave (Niah)", "Borneo painted caves", "Niah, Sarawak; haematite paintings of figures and death-ships over boat coffins", "Niah National Park")])
X[("L1-5", "Niah")] = D

E["L1-6"] = dict(axis=RA_AX, catalogues=[UN(1508, "Zuojiang Huashan Rock Art Cultural Landscape"), WP("Zuojiang Huashan Rock Art Cultural Landscape", "site article"), BRAD],
    kinds=[W("Luoyue ritual figures", "Sub-types", "frontal red-ochre human figures with raised arms, bronze drums and dogs", "Zuojiang Huashan Rock Art Cultural Landscape"),
           W("Warring States to Eastern Han phase", "Schools & phases", "paintings dated c. 5th century BC to 2nd century AD", "Zuojiang Huashan Rock Art Cultural Landscape")])

E["L1-7"] = dict(axis=RA_AX, catalogues=[UNS("Bangucheon", "UNESCO entry: Petroglyphs along the Bangucheon Stream (inscribed 2025)"), WP("Bangudae Petroglyphs", "site article"), BRAD],
    kinds=[W("Whale-hunting scenes", "Sub-types", "boats, harpoons and whales at Bangudae: among the earliest whaling images known", "Bangudae Petroglyphs"),
           W("Geometric and abstract motifs", "Sub-types", "concentric circles, lozenges and spirals at Cheonjeon-ri", "Cheonjeon-ri Petroglyphs")],
    knowledge_sites=[W("Cheonjeon-ri Petroglyphs", "Korean petroglyph sites", "Ulju, Ulsan; Neolithic to Silla geometric carvings and inscriptions; National Treasure")])
X[("L1-7", "Cheonjeon-ri petroglyphs")] = D

E["L1-8"] = dict(axis=RA_AX, catalogues=[WP("Fugoppe Cave", "site article"), BUNKA, COM("Fugoppe Cave")],
    kinds=[W("Incised winged and horned figures", "Sub-types", "c. 800 engraved figures of the Zoku-Jōmon period on the cave walls", "Fugoppe Cave"),
           W("Zoku-Jōmon (Epi-Jōmon) phase", "Schools & phases", "c. 2nd-7th century AD, Hokkaido", "Fugoppe Cave")])

E["L1-9"] = dict(axis=RA_AX, catalogues=[WP("Helan Mountains", "range article"), COM("Helan Mountains rock art"), BRAD],
    kinds=[W("Face (mask) petroglyphs", "Sub-types", "human and sun-god faces, the signature motif of Helankou", "Helan Mountains"),
           W("Hunting and herding scenes", "Sub-types", "ibex, deer, horses and archers pecked by steppe peoples", "Yin Mountains")],
    knowledge_sites=[W("Helankou", "Northern Chinese petroglyph sites", "Helan Mountains, Ningxia; gorge with thousands of pecked figures and masks", "Helan Mountains"),
                     W("Yinshan petroglyphs", "Northern Chinese petroglyph sites", "Yin Mountains, Inner Mongolia; animal and hunting carvings of steppe peoples", "Yin Mountains")])

E["L1-10"] = dict(axis=RA_AX, catalogues=[UN(179, "Tassili n'Ajjer"), UN(287, "Rock-Art Sites of Tadrart Acacus"), UN(1475, "Ennedi Massif"), TARA, BMRA, BRAD],
    kinds=[W("Bubaline (Large Wild Fauna) period", "Schools & phases", "large engravings of extinct buffalo, elephant and rhino, early Holocene", "Tassili n'Ajjer"),
           W("Round Head period", "Schools & phases", "painted floating human figures with round heads, central Sahara", "Tassili n'Ajjer"),
           W("Bovidian (Pastoral) period", "Schools & phases", "polychrome cattle-herding scenes, c. 5th-3rd millennium BC", "Tassili n'Ajjer"),
           W("Horse and Camel periods", "Schools & phases", "chariots, riders and camels with Libyco-Berber script, 1st millennium BC onward", "Tassili n'Ajjer")])
X[("L1-10", "Gilf Kebir and Uweinat (Eastern Sahara) rock art")] = LBL
X[("L1-10", "Tazina style")] = ("Sub-types", "stylised engravings with long flowing lines, South Oran and Moroccan Atlas")
X[("L1-10", "Tassili n'Ajjer")] = D
X[("L1-10", "Tadrart Acacus")] = D

E["L1-11"] = dict(axis=RA_AX, catalogues=[UN(985, "Maloti-Drakensberg Park"), UN(1255, "Twyfelfontein or /Ui-//aes"), UN(1021, "Tsodilo"), TARA,
                                          ["https://www.wits.ac.za/rockart/", "Rock Art Research Institute, University of the Witwatersrand", "SARADA archive of southern African rock art"], BRAD],
    kinds=[W("Fine-line paintings", "Sub-types", "shaded polychrome eland, rain-animals and trance figures, Drakensberg and Cederberg", "San rock art"),
           W("Engravings (petroglyphs)", "Sub-types", "pecked and incised animals and spoor on open rocks of the interior plateau", "Twyfelfontein"),
           W("Therianthropes and rain-animals", "Sub-types", "part-human figures and rain-creatures read as images of shamanic trance", "San rock art")],
    knowledge_sites=[W("Brandberg Mountain", "Namibia (Twyfelfontein, Brandberg, Erongo)", "Erongo, Namibia; over 45,000 paintings incl. the 'White Lady' shelter"),
                     W("Game Pass Shelter", "South Africa and Lesotho (Drakensberg, Maloti)", "Kamberg, KwaZulu-Natal; eland panel known as the 'Rosetta Stone' of San art")])
for n in ("Maloti-Drakensberg", "Twyfelfontein", "Tsodilo"): X[("L1-11", n)] = D

E["L1-12"] = dict(axis="Phases first, then reliefs sectioned by dynasty (pre-Achaemenid, Achaemenid, Parthian, Sasanian, Qajar revival).",
    catalogues=[UN(1222, "Bisotun"), UNS("Sassanid Archaeological Landscape", "UNESCO entry for the Sasanian sites of Fars (Firuzabad, Bishapur, Sarvestan)"), WP("Rock relief", "survey article with lists of Iranian reliefs"), COM("Sasanian rock relief")],
    kinds=[W("Investiture reliefs", "Sub-types", "the king receiving the diadem from Ahura Mazda or Anahita", "Naqsh-e Rostam"),
           W("Triumph reliefs", "Sub-types", "the king over defeated Roman emperors (Valerian, Philip the Arab)", "Naqsh-e Rostam")],
    knowledge_sites=[W("Naqsh-e Rostam", "Sasanian reliefs", "Marvdasht, Fars; Achaemenid tombs with eight Sasanian royal reliefs"),
                     W("Naqsh-e Rajab", "Sasanian reliefs", "near Persepolis; investiture reliefs of Ardashir I and Shapur I"),
                     W("Taq-e Bostan", "Sasanian reliefs", "Kermanshah; rock-cut iwans with hunting and investiture reliefs, 4th-7th century"),
                     W("Bishapur", "Sasanian reliefs", "Fars; Tang-e Chowgan gorge with six reliefs of Shapur I and successors")])
X[("L1-12", "rock relief - Afghanistan (undated)")] = LBL
X[("L1-12", "Achaemenid rock reliefs")] = drop("phase label; now a section of the catalogue")
X[("L1-12", "Qajar rock reliefs")] = drop("phase label; now a section of the catalogue")

E["L1-13"] = dict(axis="Sites catalogue of Hittite Imperial rock reliefs, by date; Neo-Hittite reliefs after.",
    catalogues=[UN(377, "Hattusha: the Hittite Capital (incl. Yazılıkaya)"), WP("Hittites", "survey article"), COM("Hittite rock relief")],
    knowledge_sites=[W("Yazılıkaya", "Hittite Imperial rock reliefs", "Boğazkale, Çorum; rock sanctuary of Hattusa with the procession of the gods, 13th c. BC"),
                     W("Eflatun Pınar", "Hittite Imperial rock reliefs", "Beyşehir, Konya; spring sanctuary with carved god figures, 13th c. BC"),
                     W("Sirkeli Höyük", "Hittite Imperial rock reliefs", "Adana; relief of Muwatalli II, the oldest Hittite rock relief known"),
                     W("İvriz relief", "Neo-Hittite rock reliefs", "Konya; King Warpalawas before the storm god Tarhunzas, 8th c. BC")])

E["L1-14"] = dict(axis=RA_AX, catalogues=[UN(1076, "Gobustan Rock Art Cultural Landscape"), WP("Gobustan National Park", "site article"), BRAD],
    kinds=[W("Yallı dance scenes", "Sub-types", "lines of linked dancers engraved on the Gobustan boulders", "Gobustan National Park"),
           W("Reed-boat engravings", "Sub-types", "boats with rowers and sun-discs on the Beyukdash and Kichikdash boulders", "Gobustan National Park"),
           W("Gaval daşı", "Sub-types", "the 'tambourine stone', a resonant boulder struck as a percussion instrument", "Gaval dash")])

E["L1-15"] = dict(axis=RA_AX, catalogues=[UN(1472, "Rock Art in the Hail Region of Saudi Arabia"), WP("Rock Art in the Hail Region of Saudi Arabia", "site article"), COM("Jubbah petroglyphs")],
    kinds=[W("Thamudic-period camel and human figures", "Sub-types", "engraved camels, horses and armed figures with Thamudic inscriptions", "Rock Art in the Hail Region of Saudi Arabia"),
           W("Neolithic life-size figures", "Sub-types", "life-size human and animal figures of the early Holocene, Jubbah and Shuwaymis", "Rock Art in the Hail Region of Saudi Arabia")])
X[("L1-15", "Bir Hima")] = D

E["L1-16"] = dict(axis=RA_AX, catalogues=[UN(936, "Cueva de las Manos, Río Pinturas"), WP("Cueva de las Manos", "site article"), BRAD],
    kinds=[W("Negative hand stencils", "Sub-types", "over 800 hands, mostly left, sprayed in red, ochre, white and black", "Cueva de las Manos"),
           W("Guanaco hunting scenes", "Sub-types", "dynamic hunting scenes of the earliest group, c. 7300 BC", "Cueva de las Manos"),
           W("Group A, B and C styles", "Schools & phases", "Gradin's sequence: hunting scenes, stylised figures, then geometric motifs", "Cueva de las Manos")])

E["L1-17"] = dict(axis=RA_AX, catalogues=[UN(606, "Serra da Capivara National Park"), WP("Serra da Capivara National Park", "park article"), BRAD],
    kinds=[W("Nordeste tradition", "Schools & phases", "lively red scenes of dance, sex, hunting and ritual, c. 12,000-6,000 BP", "Serra da Capivara National Park"),
           W("Agreste tradition", "Schools & phases", "larger, static figures and graphic signs of later date", "Serra da Capivara National Park"),
           W("Itacoatiara (engraving) tradition", "Schools & phases", "pecked geometric engravings on riverside rocks, e.g. the Ingá Stone", "Ingá Stone")],
    knowledge_sites=[W("Serra das Confusões National Park", "Other Nordeste rock-art sites", "Piauí; neighbouring park with painted shelters of the Nordeste tradition")])
X[("L1-17", "Pedra Furada")] = D

E["L1-18"] = dict(axis=RA_AX, catalogues=[COM("Toro Muerto petroglyphs"), BRAD, WP("Petroglyph", "survey article")],
    kinds=[W("Dancing figures (danzantes)", "Sub-types", "masked dancers, felines, camelids and birds pecked on c. 5,000 boulders at Toro Muerto", "Petroglyph")])
X[("L1-18", "Toquepala Caves")] = D
X[("L1-18", "Miculla petroglyphs")] = D

E["L1-19"] = dict(axis=RA_AX, catalogues=[UN(1174, "Chiribiquete National Park, The Maloca of the Jaguar"), WP("Chiribiquete National Park", "park article"), BRAD],
    kinds=[W("Jaguar-centred painted panels", "Sub-types", "over 75,000 red figures of jaguars, hunters and dancers on tepui walls", "Chiribiquete National Park")],
    knowledge_sites=[SR("Serranía de La Lindosa", "Amazonian rock-art sites", "Guaviare, Colombia; painted cliffs with Ice Age fauna, publicised 2020"),
                     W("Caverna da Pedra Pintada", "Amazonian rock-art sites", "Monte Alegre, Pará, Brazil; painted cave with Paleoindian occupation")])

E["L1-20"] = dict(axis=RA_AX, catalogues=[["https://shumla.org/", "SHUMLA Archaeological Research and Education Center", "documentation archive of Lower Pecos rock-art sites"], WP("Seminole Canyon State Park and Historic Site", "park article"), NRHP],
    kinds=[W("Pecos River Style", "Schools & phases", "polychrome shamanic murals, c. 4,000 years old; the classic style", "Seminole Canyon State Park and Historic Site"),
           W("Red Linear style", "Schools & phases", "small red stick figures, later Archaic", "Seminole Canyon State Park and Historic Site"),
           W("Red Monochrome style", "Schools & phases", "late prehistoric red figures with bows", "Seminole Canyon State Park and Historic Site")],
    knowledge_sites=[SR("White Shaman Preserve", "Lower Pecos Canyonlands sites", "Val Verde County, Texas; the White Shaman mural, c. 2000 BC"),
                     SR("Panther Cave", "Lower Pecos Canyonlands sites", "Seminole Canyon, Texas; mural with a large red panther", "Panther Cave Seminole Canyon")])
X[("L1-20", "Fate Bell Shelter")] = D

E["L1-21"] = dict(axis=RA_AX, catalogues=[["https://www.nps.gov/cany/", "Canyonlands National Park (NPS)", "park site incl. the Horseshoe Canyon unit and the Great Gallery"], WP("Canyonlands National Park", "park article"), BRAD],
    kinds=[W("Anthropomorphic spirit figures", "Sub-types", "tall, tapering, armless painted figures with bug-eyes, Archaic period", "Canyonlands National Park")],
    knowledge_sites=[W("Canyonlands National Park", "Barrier Canyon Style panels", "Utah; its Horseshoe Canyon unit holds the Great Gallery, type site of the style")])
X[("L1-21", "Horseshoe Canyon (Great Gallery)")] = D

E["L1-22"] = dict(axis=RA_AX, catalogues=[WP("Chumash Painted Cave State Historic Park", "type-site article"), NRHP, BRAD],
    kinds=[W("Polychrome circular motifs", "Sub-types", "red, black and white rayed discs and figures read as solstice and shamanic imagery", "Chumash Painted Cave State Historic Park")],
    knowledge_sites=[W("Carrizo Plain National Monument", "Chumash and South-Central California painted sites", "San Luis Obispo County; holds Painted Rock, Chumash and Yokuts pictographs")])
X[("L1-22", "Chumash Painted Cave")] = D

E["L1-23"] = dict(axis=RA_AX, catalogues=[WP("Coso Rock Art District", "site article"), NRHP, BRAD],
    kinds=[W("Bighorn sheep petroglyphs", "Sub-types", "thousands of pecked bighorn sheep in Big and Little Petroglyph Canyons", "Coso Rock Art District"),
           W("Patterned-body anthropomorphs", "Sub-types", "figures with decorated bodies and headdresses, Coso Range", "Coso Rock Art District")])

E["L1-24"] = dict(axis=RA_AX, catalogues=[UN(1597, "Writing-on-Stone / Áísínai'pi"), WP("Writing-on-Stone Provincial Park", "park article"), NRHP],
    kinds=[W("Ceremonial tradition", "Schools & phases", "shield-bearing warriors and V-necked figures, pre-contact", "Writing-on-Stone Provincial Park"),
           W("Biographic tradition", "Schools & phases", "narrative battle and horse-raid scenes, post-contact, akin to ledger art", "Writing-on-Stone Provincial Park")])

E["L1-25"] = dict(axis=RA_AX, catalogues=[UN(714, "Rock Paintings of the Sierra de San Francisco"), WP("Rock Paintings of Sierra de San Francisco", "site article"), BRAD],
    kinds=[W("Great Mural style", "Sub-types", "life-size red-and-black human figures (monos) and animals on rock-shelter ceilings", "Rock Paintings of Sierra de San Francisco")],
    knowledge_sites=[SR("Cueva Pintada (Baja California)", "Great Mural sites of the Baja California sierras", "Sierra de San Francisco; 150 m painted shelter, the type site", "Cueva Pintada Sierra de San Francisco"),
                     W("El Vizcaíno Biosphere Reserve", "Great Mural sites of the Baja California sierras", "Baja California Sur; reserve enclosing the painted canyons")])

E["L1-26"] = dict(axis=RA_AX, catalogues=[UN(147, "Kakadu National Park"), WP("Kakadu National Park", "park article"), BRAD],
    kinds=[W("X-ray style", "Sub-types", "fish, turtles and figures painted with skeleton and organs visible", "X-ray style"),
           W("Mimi (Dynamic figure) style", "Sub-types", "fine red running figures of the pre-estuarine period", "Kakadu National Park"),
           W("Rainbow Serpent paintings", "Sub-types", "ancestral serpent images, a long-lived motif of western Arnhem Land", "Kakadu National Park"),
           W("Contact-period paintings", "Sub-types", "ships, guns and Europeans, 17th-20th century", "Kakadu National Park")],
    knowledge_sites=[W("Nawarla Gabarnmang", "Kakadu and western Arnhem Land galleries", "Jawoyn country, Arnhem Land; painted rock-shelter ceiling, occupied 45,000+ years")])
for n in ("Ubirr", "Burrungkuy (Nourlangie)", "Nanguluwur"): X[("L1-26", n)] = D
E["L1-26"]["kinds"].append(M("Nayombolmi", "Makers", "Aboriginal artist (c. 1895-1967) who repainted the Anbangbang gallery at Burrungkuy in 1964"))

E["L1-27"] = dict(axis=RA_AX, catalogues=[["https://www.kimberleyfoundation.org.au/", "Kimberley Foundation Australia", "research and image archive of Kimberley rock art"], WP("Gwion Gwion rock paintings", "tradition article"), BRAD],
    kinds=[W("Tassel figures", "Sub-types", "Gwion figures with tassels at arms and waist, the classic early type", "Gwion Gwion rock paintings"),
           W("Sash figures", "Sub-types", "Gwion figures with three-pointed sashes, later phase", "Gwion Gwion rock paintings"),
           W("Irregular Infill Animal period", "Schools & phases", "large naturalistic animals, before the Gwion phase", "Gwion Gwion rock paintings"),
           W("Gwion (Bradshaw) period", "Schools & phases", "elegant ochre human figures, c. 12,000 years ago", "Gwion Gwion rock paintings"),
           W("Wandjina period", "Schools & phases", "mouthless cloud and rain spirits, latest phase, repainted into the 20th century", "Wandjina")])
X[("L1-27", "Wandjina rock paintings")] = ("Sub-types", "white-faced, mouthless ancestral beings painted and repainted by Worrorra, Ngarinyin and Wunambal")

E["L1-28"] = dict(axis=RA_AX, catalogues=[UNS("Murujuga", "UNESCO entry: Murujuga Cultural Landscape (inscribed 2025)"), WP("Murujuga National Park", "park article"), BRAD],
    kinds=[W("Pecked petroglyphs", "Sub-types", "over a million engravings of fauna, faces and tracks on the Dampier Archipelago", "Murujuga National Park"),
           W("Archaic faces", "Sub-types", "early pecked human faces, among Australia's oldest motifs", "Murujuga National Park"),
           W("Extinct fauna engravings", "Sub-types", "thylacine and fat-tailed kangaroo figures", "Murujuga National Park")])

E["L1-29"] = dict(axis=RA_AX, catalogues=[WP("Ku-ring-gai Chase National Park", "park article"), COM("Sydney rock engravings"), BRAD],
    kinds=[W("Outline engravings", "Sub-types", "large outline figures of whales, fish, kangaroos and ancestral beings (Daramulan) on sandstone", "Ku-ring-gai Chase National Park")],
    knowledge_sites=[W("Brisbane Water National Park", "Sydney Basin engraving sites", "Central Coast NSW; Bulgandry engraving site"),
                     W("Baiame Cave", "Sydney Basin engraving sites", "Milbrodale, NSW; painted figure of the creator Baiame in a shelter of the Hunter Valley")])

E["L1-30"] = dict(axis=RA_AX, catalogues=[WP("Laura, Queensland", "town article with the Quinkan galleries"), COM("Quinkan rock art"), BRAD],
    kinds=[W("Quinkan spirit figures", "Sub-types", "Imjim and Timara spirit beings, the emblem of the Laura galleries", "Laura, Queensland"),
           W("Split Rock gallery", "Quinkan country sites", "Laura, Cape York; publicly accessible painted shelters", "Laura, Queensland")])

E["L1-31"] = dict(axis=RA_AX, catalogues=[WP("Petroglyph", "survey article"), COM("Panaramitee petroglyphs"), BRAD],
    kinds=[W("Track-and-circle motifs", "Sub-types", "pecked bird and macropod tracks, circles and dots, arid Australia", "Petroglyph")],
    knowledge_sites=[W("N'Dhala Gorge Nature Park", "Panaramitee-style engraving sites", "East MacDonnell Ranges, NT; thousands of pecked engravings"),
                     W("Ikara-Flinders Ranges National Park", "Panaramitee-style engraving sites", "South Australia; Sacred Canyon and Arkaroo Rock engravings")])
X[("L1-31", "Central Australian rock art (Uluru, Ewaninga)")] = LBL

E["L1-32"] = dict(axis=RA_AX, catalogues=[COM("Māori rock art"), WP("Māori rock art", "tradition article"), BRAD],
    kinds=[W("Charcoal and red-ochre drawings", "Sub-types", "birds, fish, taniwha and human figures on limestone shelters", "Māori rock art"),
           W("Birdman figures", "Sub-types", "bird-headed human figures characteristic of South Canterbury", "Māori rock art")])

E["L1-33"] = dict(axis=RA_AX, catalogues=[UN(85, "Prehistoric Sites and Decorated Caves of the Vézère Valley"), UN(310, "Cave of Altamira and Paleolithic Cave Art of Northern Spain"), UN(1426, "Decorated Cave of Pont d'Arc (Chauvet)"), BRAD,
                                          WP("List of Stone Age art", "list article")],
    kinds=[W("Aurignacian phase", "Schools & phases", "c. 40,000-30,000 BP: Chauvet, El Castillo hand stencils", "Chauvet Cave"),
           W("Gravettian phase", "Schools & phases", "c. 30,000-22,000 BP: Cosquer, Gargas hand stencils, Pech Merle", "Gargas"),
           W("Solutrean phase", "Schools & phases", "c. 22,000-17,000 BP: Roc-de-Sers, Parpalló", "Solutrean"),
           W("Magdalenian phase", "Schools & phases", "c. 17,000-12,000 BP: Lascaux, Altamira, Niaux, Font-de-Gaume", "Magdalenian")])

E["L1-34"] = dict(axis=RA_AX, catalogues=[UN(866, "Prehistoric Rock Art Sites in the Côa Valley and Siega Verde"), WP("Côa Valley Paleolithic Art", "site article"), BRAD],
    kinds=[W("Open-air engraved panels", "Sub-types", "pecked and fine-incised aurochs, horses and ibex on schist outcrops, Gravettian to Magdalenian", "Côa Valley Paleolithic Art")])

E["L1-35"] = dict(axis="Sub-types first, then the shelters by autonomous community, Valencian core first.", catalogues=[UN(874, "Rock Art of the Mediterranean Basin on the Iberian Peninsula"), WP("Rock Art of the Iberian Mediterranean Basin", "tradition article"), BRAD],
    kinds=[W("Hunting scenes", "Sub-types", "archers driving deer and ibex, e.g. Cova dels Cavalls", "Rock Art of the Iberian Mediterranean Basin"),
           W("Honey-gathering scenes", "Sub-types", "the honey hunter of the Cuevas de la Araña, Bicorp", "Cuevas de la Araña"),
           W("Battle and execution scenes", "Sub-types", "groups of archers in combat, Les Dogues; executed figure at Cova Remigia", "Rock Art of the Iberian Mediterranean Basin")])

E["L1-36"] = dict(axis="Sub-types first, then sites by autonomous community.", catalogues=[UN(874, "Rock Art of the Mediterranean Basin on the Iberian Peninsula"), WP("Schematic art", "tradition article"), BRAD],
    kinds=[W("Schematic anthropomorphs and idols", "Sub-types", "reduced human figures, 'oculados' (eye-idols) and zig-zags in red, Neolithic to Bronze Age", "Schematic art"),
           W("Galician petroglyphs", "Sub-types", "Atlantic-type cup-and-ring, deer and weapon carvings of Galicia filed with schematic art in the data", "Galician petroglyphs")])

E["L1-37"] = dict(axis="Sub-types first, then carved rocks by region (England, Scotland, Wales, Ireland).", catalogues=[HIST_ENG, CANMORE, ["https://www.rockart.scot/", "Scotland's Rock Art Project", "national database of Scottish carved rocks"], WP("Cup and ring mark", "type article")],
    kinds=[W("Cup marks", "Sub-types", "simple pecked hollows, the commonest motif", "Cup and ring mark"),
           W("Cup-and-ring marks", "Sub-types", "cups enclosed by concentric rings, often with radial grooves, Neolithic-Bronze Age", "Cup and ring mark")],
    knowledge_sites=[W("Kilmartin Glen", "Scotland", "Argyll; the densest concentration of cup-and-ring carved rocks in Scotland (Achnabreck, Cairnbaan)"),
                     W("Roughting Linn", "Northumberland", "Doddington, Northumberland; the largest decorated rock in northern England")])

E["L1-38"] = dict(axis="Sites: Tanum (Bohuslän) first, then other Nordic sites by country; Finnish rock paintings last.",
    catalogues=[UN(557, "Rock Carvings in Tanum"), ["https://shfa.dh.gu.se/", "Swedish Rock Art Research Archives (SHFA)", "documentation archive of Scandinavian rock carvings"],
                ["https://app.raa.se/open/fornsok/", "Fornsök (Swedish National Heritage Board)", "register of every recorded Swedish ancient monument incl. c. 20,000 rock-carving entries"],
                ["https://www.kulturminnesok.no/", "Kulturminnesøk (Norway)", "Norwegian heritage register incl. helleristninger"], ["https://www.kyppi.fi/", "Kyppi (Finnish Heritage Agency)", "Finnish register of ancient monuments incl. rock paintings"]],
    kinds=[W("Ship carvings", "Sub-types", "Bronze Age ships with crews, the commonest Bohuslän motif", "Rock Carvings in Tanum"),
           W("Cult and warrior scenes", "Sub-types", "axe-wielders, lur-blowers, weddings and ploughing scenes", "Rock Carvings in Tanum"),
           W("Nordic Bronze Age phase", "Schools & phases", "c. 1700-500 BC; the main period of the southern carvings", "Nordic Bronze Age")],
    knowledge_sites=[W("Vitlycke Museum", "Tanum World Heritage area (Bohuslän)", "Tanum; museum and the Vitlycke panel with the 'Bridal Couple'", "Vitlycke Museum")])

E["L1-39"] = dict(axis=RA_AX, catalogues=[UN(352, "Rock Art of Alta"), ["https://www.altamuseum.no/", "Alta Museum", "museum and documentation of the Alta rock carvings"], WP("Rock carvings at Alta", "site article")],
    kinds=[W("Hunter-fisher carvings", "Sub-types", "reindeer, elk, bears, boats and fishing scenes, c. 5000-0 BC", "Rock carvings at Alta"),
           W("Shoreline-dated phases", "Schools & phases", "carvings dated by land-uplift shorelines into successive phases (Alta I-V)", "Rock carvings at Alta")])

E["L1-40"] = dict(axis=RA_AX, catalogues=[UN(1654, "Petroglyphs of Lake Onega and the White Sea"), WP("Onega petroglyphs", "site article"), BRAD],
    kinds=[W("Swans and solar signs", "Sub-types", "swans, lunar and solar signs and the 'Demon' figure of Besov Nos, Lake Onega", "Onega petroglyphs"),
           W("Hunting and boat scenes", "Sub-types", "beluga hunts, skiers and boats at Zalavruga, White Sea", "Zalavruga")])

E["L1-41"] = dict(axis=RA_AX, catalogues=[WP("Kapova Cave", "Palaeolithic painted cave article"), UNS("Shulgan-Tash", "UNESCO entry for the Shulgan-Tash (Kapova) cave"), BRAD],
    kinds=[W("Red-ochre pisanitsy", "Sub-types", "Neolithic-Eneolithic red ochre figures, elk and signs on riverside cliffs of the Urals", "Kapova Cave"),
           W("Palaeolithic cave paintings", "Sub-types", "mammoths, horses and signs in Kapova and Ignateva caves", "Kapova Cave")])

E["L1-42"] = dict(axis=RA_AX, catalogues=[UN(94, "Rock Drawings in Valcamonica"), WP("Rock Drawings in Valcamonica", "site article"), BRAD],
    kinds=[W("Camunian rose", "Sub-types", "the four-armed rose motif, emblem of Lombardy", "Camunian rose"),
           W("Praying figures and duellists", "Sub-types", "oranti and duelling warriors of the Iron Age", "Rock Drawings in Valcamonica"),
           W("Neolithic to Iron Age phases", "Schools & phases", "c. 8000 BC-1st century BC; most carvings Iron Age", "Rock Drawings in Valcamonica")],
    knowledge_sites=[W("Naquane", "Valcamonica rock-art parks", "Capo di Ponte; national park of rock engravings with the Great Rock", "Naquane National Park"),
                     W("Vallée des Merveilles", "Alpine comparanda", "Mont Bégo, Alpes-Maritimes, France; c. 40,000 Bronze Age carvings")])
