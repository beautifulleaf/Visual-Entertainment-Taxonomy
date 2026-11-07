"""Per-leaf catalogue specs: which in_situ_exemplars traditions feed the leaf, noise exclusions, and the sectioning axis."""
import re

def kw(rules, default, field="site"):
    """section by first matching regex on name+description(+place)"""
    def f(r):
        s = r["site"] + " || " + r["description"] + " || " + r["place"]
        for pat, lab in rules:
            if re.search(pat, s, re.I): return lab
        return default
    return f

def by_country(labels, default="Other countries"):
    def f(r):
        c = (r["country"] or "").split("|")[0]
        return labels.get(c, default if default else c or "Location not recorded")
    return f

def by_place(rules, default):
    def f(r):
        p = r["place"] + "|" + r["country"]
        for pat, lab in rules:
            if re.search(pat, p): return lab
        return default
    return f

def by_date(bands, default="Undated"):
    def f(r):
        try: y = int(float(r["date"]))
        except Exception: return default
        for hi, lab in bands:
            if y < hi: return lab
        return bands[-1][1]
    return f

S = {}
def add(code, trad, **kw_): S[code] = dict(trad=trad, **kw_)

# ---------------- L1 Rock art ----------------
add("L1-1", ["Bhimbetka and Central Indian rock shelters"], group="Central Indian painted rock shelters",
    section=kw([(r"Bhimbetka", "Bhimbetka World Heritage Site")], "Central Indian painted rock shelters"),
    group_order=["Bhimbetka World Heritage Site", "Central Indian painted rock shelters"])
add("L1-2", ["Mongolian Altai petroglyphs"], excl=r"Inscription on the Ceremonial|Duut Rock Inscription",
    section=kw([(r"Petroglyphic Complexes|Tsagaan Salaa|Upper Tsagaan|Aral Tolgoi", "Petroglyphic Complexes of the Mongolian Altai (UNESCO components)")], "Other Mongolian petroglyph sites"),
    group_order=["Petroglyphic Complexes of the Mongolian Altai (UNESCO components)", "Other Mongolian petroglyph sites"])
add("L1-3", ["Tamgaly / Semirechye petroglyphs", "Central Asian petroglyphs (Sarmishsay, Zarautsoy, Saimaly-Tash)"], excl=r"Kandahar Bilingual",
    section=by_country({"Kazakhstan": "Semirechye and Kazakhstan petroglyphs", "Kyrgyzstan": "Kyrgyz petroglyphs (Saimaly-Tash, Cholpon-Ata)", "Uzbekistan": "Uzbek petroglyphs (Sarmishsay)"}),
    group_order=["Semirechye and Kazakhstan petroglyphs", "Kyrgyz petroglyphs (Saimaly-Tash, Cholpon-Ata)", "Uzbek petroglyphs (Sarmishsay)"])
add("L1-4", ["Maros-Pangkep (Sulawesi) cave art"], group="Maros-Pangkep caves")
add("L1-5", ["Borneo cave art (Sangkulirang-Mangkalihat)"], group="Borneo painted caves")
add("L1-6", ["Zuojiang Huashan rock paintings", "Southern Chinese rock art (Cangyuan, Lianyungang, Jiangjunya)"],
    excl=r"Dazu|Baoding|Cliffside Carvings|大佛|Buddhist Sculptures|Shuining",
    section=kw([(r"Hong Kong|Wong Chuk|Po Toi|Shek Pik|Kau Sai|Cheung Chau|Lung Ha|Tung Lung|Big Wave|Collinson", "Hong Kong rock carvings (comparanda)")], "Zuojiang Huashan rock-art cultural landscape"),
    group_order=["Zuojiang Huashan rock-art cultural landscape", "Hong Kong rock carvings (comparanda)"],
    note="Dazu and other Buddhist cliff sculptures in the source bucket are excluded (sculpture, not rock art)")
add("L1-7", ["Korean petroglyphs (Bangudae, Cheonjeon-ri)"], excl=r"Buddha|Bodhisattva|Bell Carved|도로수축|Seongbulsa",
    group="Korean petroglyph sites", note="rock-cut Buddhas and inscriptions in the source bucket are excluded")
add("L1-8", ["Japanese rock carvings (Fugoppe, Temiya)"], group="Hokkaido and Ryukyu rock-carving sites")
add("L1-9", ["Helan, Yinshan and northern Chinese petroglyphs"], group="Northern Chinese petroglyph sites")
add("L1-10", ["Saharan rock art (Tassili, Acacus, Messak, Ennedi, Aïr)", "Gilf Kebir and Uweinat (Eastern Sahara) rock art",
              "Egyptian and Nubian rock art (Eastern Desert, Wadi Hammamat, Nile cataracts)"], excl=r"^rock art of Tunisia|^Tinda|^Tuosc",
    section=by_country({"Algeria": "Central Sahara and Algerian Atlas", "Libya": "Central Sahara and Algerian Atlas", "Niger": "Aïr and Ténéré",
                        "Chad": "Ennedi and Tibesti", "Morocco": "Moroccan and Western Saharan sites", "Western Sahara": "Moroccan and Western Saharan sites",
                        "Egypt": "Eastern Sahara: Gilf Kebir, Uweinat and the Nile Valley"}),
    group_order=["Central Sahara and Algerian Atlas", "Aïr and Ténéré", "Ennedi and Tibesti", "Moroccan and Western Saharan sites", "Eastern Sahara: Gilf Kebir, Uweinat and the Nile Valley"])
add("L1-11", ["San (Bushman) rock art"], excl=r"^Kimberley$|Blombos",
    section=by_country({"South Africa": "South Africa and Lesotho (Drakensberg, Maloti)", "Lesotho": "South Africa and Lesotho (Drakensberg, Maloti)",
                        "Namibia": "Namibia (Twyfelfontein, Brandberg, Erongo)", "Botswana": "Botswana and Zimbabwe (Tsodilo, Matobo)", "Zimbabwe": "Botswana and Zimbabwe (Tsodilo, Matobo)"}),
    group_order=["South Africa and Lesotho (Drakensberg, Maloti)", "Namibia (Twyfelfontein, Brandberg, Erongo)", "Botswana and Zimbabwe (Tsodilo, Matobo)"])
add("L1-12", ["Sasanian and Achaemenid rock reliefs", "rock relief - Afghanistan (undated)"],
    section=kw([(r"Behistun|Qizkapan", "Achaemenid and Median reliefs"),
                (r"Vologases|Gotarzes|Khong-e Azhdar|Qimmat|Harir|Tang-e Vashi(?!.)", "Parthian and Elymaean reliefs"),
                (r"Fath-Ali|Naser al-Din|Teymur Mirza|Tang-e Vashi", "Qajar revival reliefs"),
                (r"Elamite|Anobanini|Naram|Darband|Khinnis|Rabana|Kurangun", "Pre-Achaemenid reliefs (Elamite, Lullubi, Assyrian)"),
                (r"Qir and Karzin", "Other Iranian rock carvings")], "Sasanian reliefs"),
    group_order=["Pre-Achaemenid reliefs (Elamite, Lullubi, Assyrian)", "Achaemenid and Median reliefs", "Parthian and Elymaean reliefs", "Sasanian reliefs", "Qajar revival reliefs", "Other Iranian rock carvings"])
add("L1-13", ["rock relief - Turkey (ancient)"], group="Hittite Imperial rock reliefs", order="date")
add("L1-14", ["Gobustan petroglyphs", "rock art - Azerbaijan (undated)"],
    section=kw([(r"Gobustan|Qobustan|Garadagh", "Gobustan Rock Art Cultural Landscape")], "Other Azerbaijani rock-art sites (Gamigaya, Nakhchivan)"),
    group_order=["Gobustan Rock Art Cultural Landscape", "Other Azerbaijani rock-art sites (Gamigaya, Nakhchivan)"],
    note="the ~1,050 numbered Azerbaijani heritage-register entries are left to the register")
add("L1-15", ["Arabian rock art (Ha'il, Shuwaymis, Bir Hima, Wadi Rum)"],
    section=kw([(r"Hail|Jubbah|Umm Sinman|Manjor|Raat", "Ha'il region: Jubbah and Shuwaymis"), (r"Bir Hima|Ikmah", "Najran and Al-Ula (Bir Hima, Jabal Ikmah)")], "Other Arabian rock-art sites"),
    group_order=["Ha'il region: Jubbah and Shuwaymis", "Najran and Al-Ula (Bir Hima, Jabal Ikmah)", "Other Arabian rock-art sites"])
add("L1-16", ["Patagonian rock art (Cueva de las Manos, Río Pinturas)"], group="Río Pinturas and Santa Cruz sites")
add("L1-17", ["Serra da Capivara and Brazilian Nordeste rock art", "Brazilian and southern South American rock art (other)"], excl=r"Vigirima",
    section=kw([(r"Capivara|Pedra Furada", "Serra da Capivara National Park")], "Other Nordeste rock-art sites"),
    group_order=["Serra da Capivara National Park", "Other Nordeste rock-art sites"])
add("L1-18", ["Andean rock art (Toro Muerto, Chile's Norte Grande)"],
    section=kw([(r"Toro Muerto", "Toro Muerto (Arequipa)")], "Other Andean rock-art sites"), group_order=["Toro Muerto (Arequipa)", "Other Andean rock-art sites"])
add("L1-19", ["Amazonian and Orinoco petroglyphs (Chiribiquete, Monte Alegre)"], group="Amazonian rock-art sites")
add("L1-20", ["Lower Pecos rock art"], group="Lower Pecos Canyonlands sites")
add("L1-21", ["Barrier Canyon Style"], group="Barrier Canyon Style panels")
add("L1-22", ["Chumash rock painting"], group="Chumash and South-Central California painted sites")
add("L1-23", ["Coso Range rock art", "Great Basin rock art"],
    section=kw([(r"Coso", "Coso Range")], "Other Great Basin petroglyph sites"), group_order=["Coso Range", "Other Great Basin petroglyph sites"])
add("L1-24", ["Plains and Rocky Mountain rock art (Writing-on-Stone)"], group="Northwestern Plains rock-art sites")
add("L1-25", ["Great Murals of Baja California"], group="Great Mural sites of the Baja California sierras")
add("L1-26", ["Arnhem Land and Kakadu rock art"], group="Kakadu and western Arnhem Land galleries")
add("L1-27", ["Kimberley rock art (Gwion Gwion / Bradshaw, Wanjina)"], group="Kimberley rock-art sites")
add("L1-28", ["Murujuga (Burrup) petroglyphs"], group="Murujuga cultural landscape")
add("L1-29", ["Sydney Basin rock engravings"], excl=r"Northmead European|Gosford Glyphs", group="Sydney Basin engraving sites",
    note="colonial-era carvings and the Gosford 'glyphs' are excluded")
add("L1-30", ["Quinkan / Laura (Cape York) rock art"], group="Quinkan country sites")
add("L1-31", ["Central Australian rock art (Uluru, Ewaninga)"], group="Panaramitee-style engraving sites")
add("L1-32", ["Māori rock art"], group="South Canterbury and North Otago shelters")
add("L1-33", ["Franco-Cantabrian Palaeolithic cave art"],
    section=by_place([(r"Dordogne", "Vézère Valley and Périgord (Dordogne)"), (r"Ariège|Haute-Garonne|Hautes-Pyrénées|Pyrénées-Atlantiques|Aude|Lot\b|Occitania", "French Pyrenees and Quercy"),
                      (r"Ardèche|Gard|Bouches-du-Rhône|Auvergne-Rhône|Provence", "Rhône and Provence (Chauvet, Cosquer)"),
                      (r"Nouvelle-Aquitaine|Charente|Vienne|Gironde|Burgundy|Yonne|Centre", "Other French sites"),
                      (r"Cantabria", "Cantabria (Altamira, Monte Castillo)"), (r"Asturias", "Asturias"), (r"Basque|Gipuzkoa|Biscay|Álava|Navarre", "Basque Country"),
                      (r"Spain", "Other Spanish sites (Mediterranean and interior Palaeolithic)"), (r"France", "Other French sites")], "Other sites"),
    group_order=["Vézère Valley and Périgord (Dordogne)", "French Pyrenees and Quercy", "Rhône and Provence (Chauvet, Cosquer)", "Other French sites",
                 "Cantabria (Altamira, Monte Castillo)", "Asturias", "Basque Country", "Other Spanish sites (Mediterranean and interior Palaeolithic)", "Other sites"])
add("L1-34", ["Côa / Siega Verde open-air Palaeolithic rock art"],
    section=kw([(r"Siega Verde", "Siega Verde (Spain)"), (r"Escoural|Mazouco|Vale da Casa", "Other Portuguese Palaeolithic sites")], "Côa Valley rock-art nuclei"),
    group_order=["Côa Valley rock-art nuclei", "Siega Verde (Spain)", "Other Portuguese Palaeolithic sites"])
_IB = [(r"Valencian Community|Castellón|Province of Valencia|Alicante", "Valencian Community"), (r"Aragon|Teruel|Huesca|Zaragoza", "Aragon"),
       (r"Catalonia|Tarragona|Lleida|Terres de l'Ebre|Ponent|Priorat|Barcelona", "Catalonia"), (r"Murcia", "Region of Murcia"),
       (r"Castilla-La Mancha|Albacete|Cuenca|Guadalajara|Ciudad Real|Toledo", "Castilla-La Mancha"), (r"Andalusia|Jaén|Almería|Granada|Málaga|Córdoba|Cádiz|Seville|Huelva", "Andalusia"),
       (r"Galicia|Pontevedra|Ourense|Lugo|A Coruña", "Galicia"), (r"Castile and León|Salamanca|Zamora|Burgos|Soria|León|Ávila|Segovia|Palencia", "Castile and León"),
       (r"Extremadura|Badajoz|Cáceres", "Extremadura"), (r"Madrid", "Community of Madrid"), (r"Cantabria|Asturias|Basque|Navarre|La Rioja", "Northern Spain"),
       (r"Portugal", "Portugal")]
_IB_ORDER = ["Valencian Community", "Aragon", "Catalonia", "Region of Murcia", "Castilla-La Mancha", "Andalusia", "Extremadura", "Castile and León", "Community of Madrid", "Galicia", "Northern Spain", "Portugal", "Other Iberian sites"]
add("L1-35", ["Levantine rock art (Mediterranean Basin of Iberia)"], section=by_place(_IB, "Other Iberian sites"), group_order=_IB_ORDER,
    note="the ~650 UNESCO-listed shelters of 'Rock Art of the Mediterranean Basin' without their own article are left to the UNESCO list")
add("L1-36", ["Iberian Schematic rock art"], section=by_place(_IB, "Other Iberian sites"), group_order=_IB_ORDER)
add("L1-37", ["Atlantic rock art (cup-and-ring marks)"],
    section=by_place([(r"Northumberland", "Northumberland"), (r"Yorkshire|Bradford|Ilkley", "Yorkshire (Rombalds Moor and the Dales)"), (r"Durham|Cumbria|Lancashire", "Cumbria and County Durham"),
                      (r"Scotland|Argyll|Kilmartin|Perth|Dumfries|Galloway|Aberdeen|Highland|Fife|Stirling", "Scotland"), (r"Ireland", "Ireland"), (r"Wales", "Wales")], "Other British sites"),
    group_order=["Northumberland", "Yorkshire (Rombalds Moor and the Dales)", "Cumbria and County Durham", "Other British sites", "Scotland", "Wales", "Ireland"],
    rule=1, note="tightened because nearly all of the ~390 records are unnamed scheduled-monument entries")
add("L1-38", ["Tanum / Bohuslän Bronze Age rock carvings", "Scandinavian rock carvings (hällristningar / helleristninger)"],
    section=lambda r: ("Tanum World Heritage area (Bohuslän)" if r["tradition"].startswith("Tanum") else
                       {"Sweden": "Other Swedish rock carvings (hällristningar)", "Norway": "Norwegian rock carvings (helleristninger)",
                        "Finland": "Finnish rock paintings (kalliomaalaukset)", "Denmark": "Danish rock carvings (helleristninger)"}.get(r["country"].split("|")[0], "Other Nordic sites")),
    group_order=["Tanum World Heritage area (Bohuslän)", "Other Swedish rock carvings (hällristningar)", "Norwegian rock carvings (helleristninger)", "Danish rock carvings (helleristninger)", "Finnish rock paintings (kalliomaalaukset)", "Other Nordic sites"],
    note="Swedish Fornsök and Norwegian register entries (about 20,000, numbered like 'Tanum 72:4') inflate the count and are left to the registers")
add("L1-39", ["Alta rock art (Finnmark)"], excl=r"Rock Art of Alta Collection",
    section=kw([(r"Hjemmeluft|Jiepmaluokta", "Hjemmeluft (Jiepmaluokta)"), (r"Alta\b|Amtmannsnes|Storsteinen|Transf|Kåfjord|Isnestoften|Kongeneset|Aldafjellet|Aldofjellet|Tollevik|Steenland|Mathisdalen", "Other Alta localities")], "Other Finnmark sites"),
    group_order=["Hjemmeluft (Jiepmaluokta)", "Other Alta localities", "Other Finnmark sites"])
add("L1-40", ["Onega and White Sea petroglyphs (Karelia)"], section=kw([(r"Onega", "Lake Onega"), (r"White Sea|Belomorsk|Zalavruga", "White Sea (Belomorsk)")], "Lake Onega"),
    group_order=["Lake Onega", "White Sea (Belomorsk)"])
add("L1-41", ["Ural rock paintings (pisanitsy)"],
    section=kw([(r"Kapova|Ignateva", "Palaeolithic painted caves of the Southern Urals"), (r"Varvarina|Shishkin|Byrkin", "Siberian pisanitsy (comparanda)")], "Ural pisanitsy"),
    group_order=["Palaeolithic painted caves of the Southern Urals", "Ural pisanitsy", "Siberian pisanitsy (comparanda)"])
add("L1-42", ["Valcamonica and Alpine rock art"], group="Valcamonica rock-art parks")

# ---------------- L2 Wall painting ----------------
add("L2-1", ["Umayyad palace painting (Qusayr 'Amra)"], group="Umayyad desert palaces")
add("L2-2", ["Safavid and Qajar palace wall painting (Isfahan)"], group="Safavid palaces and pavilions")
add("L2-4", ["Ajanta cave murals", "Early Indian cave-temple murals (Bagh, Ellora, Badami, Sittanavasal)"],
    section=kw([(r"Ajanta", "Ajanta Caves")], "Related Indian cave-temple murals"), group_order=["Ajanta Caves", "Related Indian cave-temple murals"])
add("L2-5", ["Sigiriya frescoes"], group="Sigiriya")
add("L2-6", ["Kerala mural painting"], section=kw([(r"Palace", "Palace murals")], "Temple murals"), group_order=["Temple murals", "Palace murals"])
add("L2-7", ["Kandyan-era temple frescoes (Dambulla, Degaldoruwa)"], group="Kandyan temple sites")
add("L2-8", ["Rajasthani haveli and palace murals (Shekhawati)"], group="Painted havelis and palaces")
add("L2-13", ["Tibetan Buddhist wall painting", "Western Himalayan Buddhist murals (Alchi, Tabo, Guge)"],
    section=by_country({"People's Republic of China": "Central Tibet (Ü-Tsang)", "India": "Western Himalaya (Ladakh, Spiti)"}),
    group_order=["Western Himalaya (Ladakh, Spiti)", "Central Tibet (Ü-Tsang)"])
add("L2-14", ["Dunhuang (Mogao and Yulin) cave murals"], excl=r"Yongle", group="Dunhuang cave complexes")
add("L2-15", [("Kucha (Kizil) and Turfan (Bezeklik) cave murals", r"Kizil")], group="Kucha cave temples")
add("L2-16", [("Kucha (Kizil) and Turfan (Bezeklik) cave murals", r"Bezeklik")], group="Turfan cave temples")
add("L2-17", ["Sogdian and Bactrian wall painting (Panjakent, Afrasiyab, Bamiyan)"], group="Sogdian sites")
add("L2-18", ["Bagan temple murals", "Burmese temple murals (Konbaung, Ava, Sagaing)"],
    section=kw([(r"Bagan|Ananda", "Bagan temples")], "Later Burmese temple murals"), group_order=["Bagan temples", "Later Burmese temple murals"])
add("L2-19", ["Thai temple murals"], section=kw([(r"Phumin|Ta Mon|Buppharam", "Lanna and Nan murals")], "Rattanakosin (Bangkok) murals"),
    group_order=["Rattanakosin (Bangkok) murals", "Lanna and Nan murals"])
add("L2-20", ["Chinese Buddhist and Daoist temple murals (Yongle Palace, Fahai)", ("Dunhuang (Mogao and Yulin) cave murals", r"Yongle")],
    section=kw([(r"Yongle", "Yongle Palace (Daoist)")], "Ming Buddhist temple murals"), group_order=["Yongle Palace (Daoist)", "Ming Buddhist temple murals"])
add("L2-21", ["Japanese tomb and temple wall painting (Takamatsuzuka, Kitora, Hōryū-ji)"],
    section=kw([(r"Horyu|Hōryū", "Hōryū-ji Kondō murals")], "Asuka decorated tombs (kofun)"), group_order=["Asuka decorated tombs (kofun)", "Hōryū-ji Kondō murals"])
add("L2-22", ["Goguryeo tomb murals", "Korean tomb and temple wall painting"],
    section=kw([(r"Goguryeo", "Goguryeo tombs")], "Later Korean temple murals (comparanda)"), group_order=["Goguryeo tombs", "Later Korean temple murals (comparanda)"])
add("L2-24", ["Ethiopian church wall painting (Gondarine, Lake Tana)"], group="Painted churches")
add("L2-28", ["Egyptian tomb and temple painting"], order="date",
    section=kw([(r"Meidum", "Old Kingdom")], "New Kingdom Thebes and Abydos"), group_order=["Old Kingdom", "New Kingdom Thebes and Abydos"])
add("L2-29", ["Aegean Bronze Age wall painting (Thera, Knossos)"], order="date",
    section=kw([(r"Akrotiri", "Akrotiri (Thera)")], "Knossos (Crete)"), group_order=["Knossos (Crete)", "Akrotiri (Thera)"])
add("L2-30", ["Etruscan tomb painting"], excl=r"Iti and Neferu", group="Painted tombs of Tarquinia and Cerveteri", order="date")
add("L2-31", ["Macedonian and Thracian tomb painting (Vergina, Kazanlak, Sveshtari)", "Paestum and Lucanian tomb painting"],
    section=kw([(r"Philip|Vergina", "Macedonian tombs"), (r"Kazanlak|Sveshtari", "Thracian tombs"), (r"Diver|Lucania|Paestum", "Paestan and Lucanian tombs")], "Macedonian tombs"),
    group_order=["Macedonian tombs", "Thracian tombs", "Paestan and Lucanian tombs"])
add("L2-32", ["Roman wall painting (Pompeian Styles I-IV)"],
    section=by_place([(r"Ercolano|Herculaneum", "Herculaneum"), (r"Castellammare|Stabia", "Stabiae"), (r"Torre Annunziata|Oplont", "Oplontis"), (r"Boscoreale", "Boscoreale"),
                      (r"Naples", "Pompeii and Vesuvian sites: works now in the Naples Archaeological Museum"), (r"Pompei", "Pompeii"), (r"Rome|Lazio", "Rome"), (r"Germany", "Roman provinces")], "Pompeii"),
    group_order=["Pompeii", "Herculaneum", "Stabiae", "Oplontis", "Boscoreale", "Pompeii and Vesuvian sites: works now in the Naples Archaeological Museum", "Rome", "Roman provinces"],
    collections=True)
add("L2-33", ["Roman and late-antique wall painting (catacombs, provincial)", "mural - United States (ancient)"], order="date",
    section=kw([(r"Dura|Synagogue|Mithra|Yale|YUAG", "Dura-Europos (Syria)"), (r"Catacomb|Rome|Vatican", "Roman catacombs and Rome")], "Provincial Roman wall painting"),
    note="Italian rows outside Rome are listed under Provincial and other Roman wall painting",
    group_order=["Roman catacombs and Rome", "Dura-Europos (Syria)", "Provincial Roman wall painting"], collections=True)
add("L2-34", ["Byzantine church painting (Greece, Anatolia)", "Cappadocian rock-cut church painting", "Troödos painted churches (Cyprus)",
              "Macedonian (Ohrid) medieval fresco (Nerezi, Kurbinovo, St Sophia Ohrid)", "Mount Athos and Late Byzantine Macedonian school (Panselinos)",
              "Serbian medieval fresco (Raška, Morava schools)", "Bulgarian medieval fresco (Boyana, Ivanovo)", "Kyivan Rus' fresco (St Sophia, Kyiv)",
              "Russian medieval church fresco (Novgorod, Vladimir, Theophanes, Rublev, Dionisius)", "Yaroslavl and Muscovite church painting (17th c.)",
              "Romanian church painting (Wallachia, Transylvania, Maramureș)", "Post-Byzantine Greek church painting (Cretan school)",
              "Ukrainian, Belarusian and Polish-Lithuanian church painting"],
    excl=r"Habib Gerez|Bedri Rahmi|Beccafumi|Ikony Revolutsii|murals in Kyiv|^ceiling$|^Pictură religioasă$|Fra Angelico|Chișinău|Moldova|Palatul de cultur|Casa de cultur|Spitalului|Primăriei|Royal Theatre|Makurian|Bishop Marianus|Apostle Saints Peter and John|Marea",
    trad_groups={"Byzantine church painting (Greece, Anatolia)": "Middle and Late Byzantine Greece", "Cappadocian rock-cut church painting": "Cappadocian rock-cut churches",
                 "Troödos painted churches (Cyprus)": "Troödos painted churches (Cyprus)", "Macedonian (Ohrid) medieval fresco (Nerezi, Kurbinovo, St Sophia Ohrid)": "Komnenian Macedonia (Nerezi, Kurbinovo, Ohrid)",
                 "Mount Athos and Late Byzantine Macedonian school (Panselinos)": "Late Byzantine: Mount Athos, Mystras and Meteora", "Serbian medieval fresco (Raška, Morava schools)": "Serbian schools (Raška, Palaiologan, Morava)",
                 "Bulgarian medieval fresco (Boyana, Ivanovo)": "Bulgarian churches", "Kyivan Rus' fresco (St Sophia, Kyiv)": "Kyivan Rus'",
                 "Russian medieval church fresco (Novgorod, Vladimir, Theophanes, Rublev, Dionisius)": "Novgorod, Vladimir and Muscovy", "Yaroslavl and Muscovite church painting (17th c.)": "Yaroslavl school (17th c.)",
                 "Romanian church painting (Wallachia, Transylvania, Maramureș)": "Post-Byzantine Romania (Wallachia, Moldavia)", "Post-Byzantine Greek church painting (Cretan school)": "Post-Byzantine Greece (Cretan school, Meteora)",
                 "Ukrainian, Belarusian and Polish-Lithuanian church painting": "Ruthenian and Polish-Lithuanian church painting"},
    group_order=["Middle and Late Byzantine Greece", "Cappadocian rock-cut churches", "Troödos painted churches (Cyprus)", "Komnenian Macedonia (Nerezi, Kurbinovo, Ohrid)", "Late Byzantine: Mount Athos, Mystras and Meteora",
                 "Serbian schools (Raška, Palaiologan, Morava)", "Bulgarian churches", "Kyivan Rus'", "Novgorod, Vladimir and Muscovy", "Yaroslavl school (17th c.)",
                 "Post-Byzantine Greece (Cretan school, Meteora)", "Post-Byzantine Romania (Wallachia, Moldavia)", "Ruthenian and Polish-Lithuanian church painting"],
    note="modern murals and Nubian (Faras) items mis-filed in the source buckets are excluded or moved to Faras")
add("L2-35", ["Nubian Christian wall painting (Faras)",
              ("Ukrainian, Belarusian and Polish-Lithuanian church painting", r"Makurian|Bishop Marianus|Apostle Saints Peter and John")],
    section=kw([(r"^Faras$", "Faras cathedral site")], "Faras paintings in the National Museum, Warsaw"), group_order=["Faras cathedral site", "Faras paintings in the National Museum, Warsaw"])
add("L2-36", ["Maya mural painting (San Bartolo, Calakmul)", "Murals of Bonampak"], group="Maya painted sites")
add("L2-37", ["Teotihuacan mural painting (Tepantitla, Tetitla)"], group="Teotihuacan")
add("L2-38", ["Cacaxtla and Epiclassic mural painting"], group="Epiclassic sites")
add("L2-39", ["Andean pre-Columbian mural painting (Moche, Lambayeque)"], group="Moche huacas")
add("L2-40", ["Mexican muralism"], order="date", modern=True,
    section=by_date([(1934, "First murals (1921-1933)"), (1955, "Mature phase (1934-1954)"), (3000, "Late muralism (after 1955)")]),
    group_order=["First murals (1921-1933)", "Mature phase (1934-1954)", "Late muralism (after 1955)", "Undated"])
add("L2-41", ["Chilean muralism"], order="date", modern=True,
    section=by_date([(1970, "Early murals (1940s-1960s)"), (1974, "Popular Unity brigades (1970-1973)"), (3000, "Post-dictatorship murals")]),
    group_order=["Early murals (1940s-1960s)", "Popular Unity brigades (1970-1973)", "Post-dictatorship murals", "Undated"])
add("L2-43", ["Romanesque wall painting", "Catalan Romanesque wall painting (Taüll, Boí)", "Italian medieval wall painting", "mural - United States (medieval)"],
    excl=r"Bhaishajyaguru|Murals ceràmics|Buddha|Tjepu", order="date",
    section=lambda r: ("Detached frescoes in American museums" if r["country"] == "United States" else
                       "Catalonia and Aragon (Boí Valley, Pyrenees)" if r["tradition"].startswith("Catalan") or "Andorra" in r["country"] else
                       {"France": "France", "Spain": "Castile and León and other Spanish churches", "Italy": "Italy", "Vatican City": "Italy", "Germany": "Germany (Reichenau, Rhineland)"}.get(r["country"].split("|")[0], "Other countries")),
    group_order=["France", "Catalonia and Aragon (Boí Valley, Pyrenees)", "Castile and León and other Spanish churches", "Italy", "Germany (Reichenau, Rhineland)", "Other countries", "Detached frescoes in American museums"],
    collections=True)
add("L2-44", ["Gothic wall painting", "Nordic church wall painting (kalkmålningar, Albertus Pictor)"], order="date",
    section=lambda r: ("Nordic church painting (kalkmålningar)" if r["tradition"].startswith("Nordic") or r["country"].split("|")[0] in ("Sweden", "Finland", "Norway", "Denmark") else
                       {"France": "France", "Germany": "Germany and Switzerland", "Switzerland": "Germany and Switzerland", "Czech Republic": "Bohemia and Central Europe", "Slovenia": "Bohemia and Central Europe",
                        "Spain": "Spain", "United Kingdom": "England", "Belgium": "Low Countries", "Italy": "France"}.get(r["country"].split("|")[0], "Other countries")),
    group_order=["France", "Germany and Switzerland", "Low Countries", "England", "Spain", "Bohemia and Central Europe", "Nordic church painting (kalkmålningar)", "Other countries"], collections=True)
add("L2-45", ["Painted monasteries of Bukovina (northern Moldavia)"], group="Painted churches")
add("L2-46", ["Scottish Renaissance painted ceilings"], excl=r"Isobel Gowdie", group="Painted ceilings")
add("L2-49", ["Baroque and Rococo ceiling and quadratura painting"], order="date",
    excl=r"Ceramic panel|Last Judgment",
    section=lambda r: (lambda c, y: ("Italy and Rome" if c in ("Italy", "Vatican City") else
                                     ("German-speaking lands, Baroque (to 1730)" if y < 1730 else "German-speaking lands, Rococo (1730 onward)") if c in ("Germany", "Austria", "Switzerland") else
                                     "Bohemia" if c == "Czech Republic" else "Spain and Portugal" if c in ("Spain", "Portugal") else
                                     "France" if c == "France" else "Britain and the Low Countries" if c in ("United Kingdom", "Netherlands", "Belgium") else "Other countries"))
                      ((r["country"] or "").split("|")[0], int(float(r["date"])) if r["date"] else 9999),
    group_order=["Italy and Rome", "France", "Britain and the Low Countries", "Spain and Portugal", "German-speaking lands, Baroque (to 1730)", "German-speaking lands, Rococo (1730 onward)", "Bohemia", "Other countries"])
add("L2-50", ["Italian Trecento and Renaissance fresco (Giotto, Masaccio, Michelangelo)"], order="date",
    section=by_date([(1400, "Trecento (14th century)"), (1490, "Early Renaissance (1400-1490)"), (1530, "High Renaissance (1490-1530)"), (3000, "Late Renaissance and Mannerism (after 1530)")]),
    group_order=["Trecento (14th century)", "Early Renaissance (1400-1490)", "High Renaissance (1490-1530)", "Late Renaissance and Mannerism (after 1530)", "Undated"],
    collections=True)

# ---------------- L3 Mosaic & tile ----------------
add("L3-1", ["Umayyad mosaics (Dome of the Rock, Great Mosque of Damascus)"], excl=r"Alcázar de los Reyes", order="date",
    section=kw([(r"Cordoba|Córdoba", "Umayyads of al-Andalus")], "Umayyad Syria and Palestine"), group_order=["Umayyad Syria and Palestine", "Umayyads of al-Andalus"])
add("L3-2", ["Maghrebi and Andalusi zellige"], excl=r"Tile panel|olambrilla|Alicatat",
    section=kw([(r"Alhambra", "Nasrid al-Andalus")], "Marinid and Saadian Morocco"), group_order=["Nasrid al-Andalus", "Marinid and Saadian Morocco"])
add("L3-3", ["Persian and Timurid architectural tilework"], order="date",
    section=kw([(r"Uzbekistan|Samarkand", "Timurid Samarkand")], "Safavid Isfahan", field="place"), group_order=["Timurid Samarkand", "Safavid Isfahan"])
add("L3-4", ["Mughal and Punjabi tile mosaic (kashi kari)"], group="Lahore")
add("L3-6", ["Hellenistic and Greek pebble mosaics"], group="Greek mosaic sites")
_RM = {"Tunisia": "Africa Proconsularis (Tunisia)", "Algeria": "Numidia and Mauretania (Algeria, Morocco)", "Morocco": "Numidia and Mauretania (Algeria, Morocco)", "Libya": "Tripolitania (Libya)",
       "Turkey": "Roman East (Antioch, Zeugma, Anatolia)", "Syria": "Roman East (Antioch, Zeugma, Anatolia)", "Cyprus": "Roman East (Antioch, Zeugma, Anatolia)", "Israel": "Roman East (Antioch, Zeugma, Anatolia)",
       "Jordan": "Roman East (Antioch, Zeugma, Anatolia)", "Lebanon": "Roman East (Antioch, Zeugma, Anatolia)", "Greece": "Roman East (Antioch, Zeugma, Anatolia)", "Georgia": "Roman East (Antioch, Zeugma, Anatolia)",
       "Italy": "Italy", "Vatican City": "Italy", "Spain": "Hispania (Spain, Portugal)", "Portugal": "Hispania (Spain, Portugal)", "France": "Gaul (France)",
       "United Kingdom": "Britannia", "Germany": "Germania and the Danube provinces", "Switzerland": "Germania and the Danube provinces", "Austria": "Germania and the Danube provinces",
       "Hungary": "Germania and the Danube provinces", "Croatia": "Germania and the Danube provinces", "Bulgaria": "Germania and the Danube provinces", "Serbia": "Germania and the Danube provinces",
       "Albania": "Germania and the Danube provinces", "North Macedonia": "Germania and the Danube provinces", "Romania": "Germania and the Danube provinces"}
add("L3-7", ["Roman mosaics", "Roman mosaics of the East (Antioch, Zeugma)", "Roman North African mosaics", "Villa Romana del Casale and Roman Sicily mosaics", "mosaic - France (ancient)"],
    excl=r"Ceramic panel|Greco-Georgian",
    section=lambda r: ("Africa Proconsularis (Tunisia)" if "Bardo" in r["description"] else _RM.get((r["country"] or "").split("|")[0], "Location not recorded" if not r["country"] else "Other provinces")),
    group_order=["Italy", "Africa Proconsularis (Tunisia)", "Numidia and Mauretania (Algeria, Morocco)", "Tripolitania (Libya)", "Roman East (Antioch, Zeugma, Anatolia)", "Hispania (Spain, Portugal)",
                 "Gaul (France)", "Britannia", "Germania and the Danube provinces", "Other provinces", "Location not recorded"],
    collections=True, note="Roman emblemata in museums count as works where they have their own Wikidata item")
add("L3-8", ["Byzantine mosaics (other)", "Middle Byzantine mosaics (Hagia Sophia, Hosios Loukas, Daphni, Nea Moni)", "Early Christian and medieval mosaics of Rome",
             "Ravenna Early Christian and Byzantine mosaics", "Norman Sicilian mosaics (Palermo, Monreale, Cefalù)", "Venetian Byzantine mosaics (San Marco, Torcello)",
             "Kyivan Rus' mosaics", "Levantine church floor mosaics (Madaba school)"],
    excl=r"Venus and Cupid among sea creatures|Mosaic of Orpheus|Villa Romana|Siena Cathedral|Palazzo Massimo|combattimento",
    trad_groups={"Early Christian and medieval mosaics of Rome": "Early Christian and medieval Rome", "Ravenna Early Christian and Byzantine mosaics": "Ravenna",
                 "Levantine church floor mosaics (Madaba school)": "Levantine floor mosaics (Madaba school)", "Middle Byzantine mosaics (Hagia Sophia, Hosios Loukas, Daphni, Nea Moni)": "Constantinople and Middle Byzantine Greece",
                 "Kyivan Rus' mosaics": "Kyivan Rus'", "Norman Sicilian mosaics (Palermo, Monreale, Cefalù)": "Norman Sicily", "Venetian Byzantine mosaics (San Marco, Torcello)": "Venice and the Adriatic",
                 },
    section=lambda r: S["L3-8"]["trad_groups"].get(r["tradition"]) or {"Turkey": "Constantinople and Middle Byzantine Greece", "Greece": "Constantinople and Middle Byzantine Greece",
                      "Italy": "Other Italian medieval mosaics", "Ukraine": "Kyivan Rus'", "Jordan": "Levantine floor mosaics (Madaba school)", "Israel": "Levantine floor mosaics (Madaba school)"}.get((r["country"] or "").split("|")[0], "Other regions"),
    group_order=["Early Christian and medieval Rome", "Ravenna", "Levantine floor mosaics (Madaba school)", "Constantinople and Middle Byzantine Greece", "Kyivan Rus'", "Norman Sicily", "Venice and the Adriatic", "Other Italian medieval mosaics", "Other regions"],
    collections=True)
add("L3-9", ["Portuguese azulejo panels", "Spanish azulejo and alicatado"],
    section=by_country({"Portugal": "Portugal", "Brazil": "Brazil (colonial and 19th-century façades)", "Spain": "Spain (Seville, Valencia)"}),
    group_order=["Portugal", "Brazil (colonial and 19th-century façades)", "Spain (Seville, Valencia)"])
add("L3-10", ["Catalan trencadís (modernisme)"], group="Modernista works in trencadís", modern=True)
add("L3-12", ["Soviet monumental mosaics"], modern=True, order="date",
    section=by_country({"Ukraine": "Ukrainian SSR", "Armenia": "Armenian SSR", "Russia": "Russian SFSR", "Azerbaijan": "Azerbaijan SSR", "Moldova": "Moldavian SSR"}),
    group_order=["Russian SFSR", "Ukrainian SSR", "Armenian SSR", "Azerbaijan SSR", "Moldavian SSR"], excl=r"Arnautoff|Mouradyan|Khanjyan|Որմնանկար")

# ---------------- L4 Geoglyphs ----------------
add("L4-1", ["Steppe geoglyphs (Turgai)"], excl=r"Pavilion|Снеговики|Valley of Hares|Границы|Грачи|Дом над|Маяк|Медиа|Сенная|Hyperbolic", group="Southern Urals",
    note="the source bucket's Nikolay Polissky land-art works are excluded")
add("L4-3", ["Nazca and Palpa lines"],
    section=kw([(r"Paracas", "Paracas Peninsula"), (r"Palpa", "Palpa geoglyphs"), (r"Spiral|Trapezoid|Mandala|Star|Starburst|Sundial|Delta|Needles|Symbols|Interlinked", "Nazca geometric figures and lines"),
                (r"^Nazca Lines$", "Nazca and Palpa (UNESCO site)")], "Nazca biomorphs (animal and plant figures)"),
    group_order=["Nazca and Palpa (UNESCO site)", "Nazca biomorphs (animal and plant figures)", "Nazca geometric figures and lines", "Palpa geoglyphs", "Paracas Peninsula"])
add("L4-4", ["Atacama geoglyphs (Tarapacá, Pintados)", "Andean geoglyphs (other)"],
    section=kw([(r"Chile", "Atacama Desert (Chile)")], "Other Andean geoglyphs (Peru, Bolivia, Argentina)", field="country"),
    group_order=["Atacama Desert (Chile)", "Other Andean geoglyphs (Peru, Bolivia, Argentina)"])
S["L4-4"]["section"] = lambda r: "Atacama Desert (Chile)" if r["country"] == "Chile" else "Other Andean geoglyphs (Peru, Bolivia, Argentina)"
add("L4-5", ["Amazonian (Acre) geoglyphs"], group="Acre geoglyph fields")
add("L4-6", [("North American intaglios and effigy figures (Blythe)", r"Serpent Mound|Effigy Tumuli")],
    section=kw([(r"Tumuli", "Modern effigy earthworks")], "Ancient effigy mounds"), group_order=["Ancient effigy mounds", "Modern effigy earthworks"])
add("L4-7", [("North American intaglios and effigy figures (Blythe)", r"Blythe")], group="Lower Colorado River intaglios")
add("L4-8", ["English chalk hill figures", "geoglyph - United Kingdom (undated)"],
    section=kw([(r"Giant|Long Man", "Human figures"), (r"Horse", "White horses"), (r"Cross|Memorial|Kiwi|Vessel|Battalion", "Crosses and memorial figures")], "Other animals and emblems"),
    group_order=["Human figures", "White horses", "Other animals and emblems", "Crosses and memorial figures"])

# ---------------- L5 Body art: sub-types from Wikidata items ----------------
for code, trad, inc in [("L5-1", "Deq (Kurdish and Arab facial tattooing)", None), ("L5-2", "Indian tattooing (godna, Naga, Apatani)", None),
                        ("L5-3", "Mehndi (henna body art)", None), ("L5-4", "Mainland and Indonesian SE Asian tattooing (sak yant, Mentawai, Chin)", r"Yantra|Myanmar"),
                        ("L5-5", "Mainland and Indonesian SE Asian tattooing (sak yant, Mentawai, Chin)", r"Mentawai"), ("L5-6", "Philippine and Bornean tattooing (batok, Iban)", None),
                        ("L5-7", "Irezumi and Japanese tattooing (incl. hajichi, Ainu)", None), ("L5-8", "African scarification traditions", r"Yoruba|African scarification"),
                        ("L5-9", "Inuit tattooing (kakiniit)", None), ("L5-10", "Tā moko (Māori)", None), ("L5-11", "Polynesian tatau (Samoa, Tahiti, Marquesas, Hawai'i, Tonga, Fiji)", r"tattoo|tatau|female|male"),
                        ("L5-12", "Western sailor, prison and modern tattooing", r"American traditional|sailor|Prison")]:
    S[code] = dict(trad=[(trad, inc) if inc else trad], group="Sub-types", rule=0, bodyart=True)

SPEC = S
