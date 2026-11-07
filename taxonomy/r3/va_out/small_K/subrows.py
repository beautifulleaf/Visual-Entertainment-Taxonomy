# Curated sub-style / sub-type / centre rows and knowledge-based works, per leaf.
# (name, group, gloss, ref): ref = exact input-row name (keeps that row's source) or a URL (new row, source "r3 <url>").
W = "https://en.wikipedia.org/wiki/"
SS, ST, CE = "Sub-styles", "Sub-types", "Centres & workshops"
R = {}
def add(code, *rows): R.setdefault(code, []).extend(rows)

# K1
add("K1-2", ("Aghlabid architecture", SS, "Abbasid-vassal emirate of Ifriqiya, 800–909: Great Mosque of Kairouan, Ribat of Sousse", "Early Islamic Maghreb (Aghlabid / Idrisid / Zirid)"),
    ("Samarra", CE, "Abbasid capital 836–892 on the Tigris, Iraq; Great Mosque and Malwiya minaret · UNESCO", W + "Samarra"))
add("K1-4", ("Caliphal (Umayyad) architecture of Córdoba", SS, "Umayyad emirate and caliphate of al-Andalus, 756–1031: Mezquita, Madinat al-Zahra", "art of the Umayyads of Cordoba"),
    ("Taifa architecture", SS, "11th-century taifa kingdoms of al-Andalus: Aljafería (Zaragoza), Alcazaba of Málaga", "Taifa art"),
    ("Zirid architecture", SS, "Zirid and Hammadid Ifriqiya and the central Maghreb, 10th–12th century", "Early Islamic Maghreb (Aghlabid / Idrisid / Zirid)"),
    ("Almoravid architecture", SS, "Almoravid empire, 1040–1147: Great Mosques of Tlemcen and Algiers, Qubba Ba'adiyn", "Almoravid architecture"),
    ("Almoravid and Almohad architecture", SS, "Berber empires of the Maghreb and al-Andalus, 11th–13th century", "art of Almoravides and Almohades"),
    ("Almohad architecture", SS, "Almohad caliphate, 1121–1269: Kutubiyya, Giralda, Hassan Tower, Tinmel", "Almohad architecture"),
    ("Nasrid architecture", SS, "Nasrid emirate of Granada, 1232–1492: the Alhambra and Generalife", "Nasrid art"),
    ("Marinid architecture", SS, "Marinid Morocco, 13th–15th century: madrasas of Fez (Bou Inania, al-Attarine), Chellah", "Marinid architecture"),
    ("Saadian architecture", SS, "Saadian Morocco, 1549–1659: Saadian Tombs and El Badi Palace, Marrakesh", "Saadian"),
    ("Alaouite architecture", SS, "Alaouite Morocco, from 1631: Meknes of Moulay Ismail, Bahia Palace", "Alaouite"),
    ("Riad", ST, "Inward-looking courtyard house round a garden with fountain, Morocco and al-Andalus, from the 12th century", "Riad"))
add("K1-5", ("Mudéjar of Aragon", SS, "Brick and glazed-tile towers and churches of Teruel, Zaragoza and Calatayud, 12th–17th century · UNESCO", "Mudéjar architecture of Aragon"),
    ("Artesonado", ST, "Carved and inlaid wooden ceiling of Mudéjar carpentry, Spain and Portugal", W + "Artesonado"))
add("K1-6", ("Razi style", SS, "Pirnia's Razi style of Persian architecture, Seljuk era (10th–13th century)", "Razi style"),
    ("Khwarazmian architecture", SS, "Khwarazm (Khorezm), Kunya-Urgench and Khiva oasis, 11th–13th century", "Khwarazmian architecture"),
    ("Samanid and Ghaznavid architecture", SS, "Pre-Seljuk Persianate dynasties: Samanid Mausoleum (Bukhara), Ghaznavid Ghazni", "Persian — early Islamic (Samanid / Buyid / Ghaznavid)"),
    ("Shirvan–Absheron architectural school", SS, "Medieval school of Shirvan and the Absheron peninsula, Azerbaijan, 12th–17th century", "Azerbaijani (Shirvan–Absheron)"))
add("K1-7", ("Traditional Ahlat stonework", ST, "Carved tombstones and kümbets of Ahlat, Lake Van, Seljuk and beylik periods", "Traditional Ahlat stonework"),
    ("Caravanserai (han)", ST, "Seljuk road inns with carved portals: Sultan Han (Aksaray), Sultanhanı (Kayseri)", W + "Caravanserai"))
add("K1-8", ("Ayyubid architecture", SS, "Ayyubid Egypt and Syria, 1171–1250, precursor of Mamluk building (Citadel of Cairo, Aleppo)", "Ayyubid architecture"),
    ("Ablaq", ST, "Alternating light and dark courses of masonry, hallmark of Mamluk façades", W + "Ablaq"))
add("K1-9", ("Azari style", SS, "Pirnia's Azari style of Persian architecture, Ilkhanid to Timurid period", "Azari style"),
    ("Jalayirid architecture", SS, "Jalayirid sultanate of Iraq and Azerbaijan, 1335–1432", "Iraqi Islamic (Ilkhanid / Jalayirid)"))
add("K1-10", ("Shaybanid and khanate architecture", SS, "Post-Timurid Central Asia (Bukhara, Khiva, Kokand), 16th–19th century, continuing the Timurid idiom", "Central Asian — Shaybanid / khanates (Bukhara, Khiva, Kokand)"),
     ("Samarkand", CE, "Timur's capital: Registan, Gur-e-Amir, Bibi-Khanym Mosque, Shah-i-Zinda · UNESCO", W + "Samarkand"),
     ("Herat", CE, "Timurid capital under Shah Rukh: Musalla complex and Gawhar Shad mausoleum", W + "Herat"))
add("K1-11", ("Naqsh-e Jahan Square", CE, "Safavid royal square, Isfahan, 1598–1629: Shah Mosque, Sheikh Lotfollah, Ali Qapu · UNESCO", W + "Naqsh-e_Jahan_Square"))
add("K1-12", ("Early Ottoman architecture", SS, "Bursa and Edirne phase, 1299–1453: Green Mosque, Bursa; Üç Şerefeli Mosque", "early Ottoman architecture"),
     ("Classical Ottoman architecture", SS, "Domed mosques of Sinan and his school, c. 1500–1700: Süleymaniye, Selimiye", "classical Ottoman architecture"),
     ("Ottoman Baroque", SS, "18th-century Istanbul style with Baroque curves: Nuruosmaniye Mosque", "Ottoman Baroque"),
     ("Ottoman architecture in Egypt", SS, "Ottoman-period buildings of Cairo, 1517–1867", "Ottoman architecture in Egypt"),
     ("Late Ottoman architecture", SS, "Westernised Ottoman building of the 19th–20th century: Dolmabahçe Palace", "Ottoman architecture in the 19th–20th centuries"),
     ("Ottoman architecture of the Arab provinces", SS, "Ottoman mosques, khans and palaces of Egypt, Syria, Iraq and the Maghreb", "Ottoman (Arab provinces)"))
add("K1-13", ("Zand architecture", SS, "Zand Iran, 1751–1794, centred on Shiraz: Vakil Mosque and Bazaar", "Zand architecture"),
     ("Afsharid architecture", SS, "Afsharid Iran under Nader Shah, 1736–1796", "Afsharid architecture"))
add("K1-14", ("Delhi Sultanate architecture", SS, "Mamluk, Khalji, Tughlaq, Sayyid and Lodi Delhi, 1206–1526: Qutb Minar, Tughlaqabad", "Indo-Islamic (Delhi Sultanate)"),
     ("Tughlaq architecture", SS, "Battered-wall fortress and tomb style of the Tughlaq dynasty, 1320–1414", "Tughlaq architecture style"),
     ("Gujarat Sultanate architecture", SS, "Ahmedabad and Champaner, 1407–1573: Jama Mosque of Ahmedabad, Sidi Saiyyed", "Gujarat Sultanate"),
     ("Bengal Sultanate architecture", SS, "Brick and terracotta mosques of Gaur, Pandua and Bagerhat, 1352–1576", "Bengal Sultanate"),
     ("Deccan Sultanate architecture", SS, "Bahmani, Adil Shahi and Qutb Shahi Deccan: Gol Gumbaz, Charminar", "Deccan Sultanates (Bahmani / Qutb Shahi / Adil Shahi)"))
add("K1-15", ("Mughal gardens", ST, "Charbagh gardens of the Mughals (Shalimar Bagh, Nishat Bagh); see Mughal Garden leaf", "Mughal gardens"),
     ("Agra", CE, "Mughal capital: Taj Mahal, Agra Fort, Fatehpur Sikri nearby · UNESCO", W + "Agra"))
add("K1-16", ("Inland Niger Delta towns", SS, "Djenné-Djenno and the tells of the Inland Niger Delta, Mali, incl. pre-Islamic phases", "Sudano-Sahelian (urban sites)"))
add("K1-17", ("Swahili coast arts (doors, furniture)", ST, "Carved Swahili doors, Lamu and Zanzibar furniture of the coral-stone towns", "Swahili coast (Kilwa, Lamu, Zanzibar) arts"))

# K2
add("K2-1", ("Moorish Revival in Bosnia and Herzegovina", SS, "Austro-Hungarian pseudo-Moorish public buildings of Sarajevo, 1880s–1910s", "Moorish Revival architecture in Bosnia and Herzegovina"),
    ("Moorish Revival in Hungary", SS, "Hungarian Moorish Revival synagogues and baths, 19th century (Dohány Street Synagogue)", "Moorish Revival architecture in Hungary"),
    ("Heliopolis style", SS, "Neo-Moorish and Neo-Mamluk suburb style of Heliopolis, Cairo, 1905–1930s", "Heliopolis style"))
add("K2-7", ("Jacobethan", SS, "Victorian revival mixing Elizabethan and Jacobean motifs, 1830s onward", "Jacobethan"),
    ("English Cottage style", SS, "American suburban revival of English vernacular cottages, 1920s–30s", "English Cottage architecture"))
add("K2-8", ("Rundbogenstil", SS, "German round-arch style, 1830s–1870s (Friedrich von Gärtner, Heinrich Hübsch)", "Rundbogenstil"),
    ("Bristol Byzantine", SS, "Polychrome brick warehouse style of Bristol, 1850–1880", "Bristol Byzantine"),
    ("Richardsonian Romanesque", SS, "H. H. Richardson's massive rough-stone Romanesque, United States, 1870s–1890s", "Richardsonian Romanesque"))
add("K2-9", ("Serbo-Byzantine Revival", SS, "Serbian national revival of medieval Serbian church forms, 1880s–1940s", "Serbo-Byzantine style (modern architecture)"),
    ("Neo-Byzantine architecture in the Russian Empire", SS, "Officially favoured Byzantine-revival churches of the Russian Empire, 1850s–1917", "Neo-Byzantine architecture in the Russian Empire"))
add("K2-12", ("Haussmannian architecture", SS, "Uniform stone apartment blocks of Haussmann's Paris, 1853–1870", "Haussmannian architecture"))
add("K2-13", ("Rococo Revival", SS, "19th-century revival of Louis XV forms in interiors and buildings", "Rococo Revival"),
    ("Edwardian Baroque", SS, "British imperial Baroque revival, 1885–1920 (Belcher, Lanchester & Rickards)", "Edwardian architecture"))
add("K2-14", ("Neo-Pompeian style", SS, "Revival of Pompeian wall decoration and villas, 19th century (Maison pompéienne)", "neo-pompeian style"),
    ("Antebellum architecture", SS, "Greek Revival plantation houses of the American South before 1861", "Antebellum architecture"),
    ("Néo-Grec", SS, "French Second Empire Neo-Greek style (Labrouste, Duc, Hittorff), 1840s–1870s", "Neo-Grec"))
add("K2-16", ("City Beautiful movement", SS, "American civic planning movement of the 1890s–1900s using Beaux-Arts monumentality", "City Beautiful movement"),
    ("American Renaissance", SS, "American Beaux-Arts and classical revival period, 1876–1917", "American Renaissance"))
add("K2-18", ("Stick style", SS, "American timber style with expressed stickwork, 1860–1890", "Stick style"),
    ("Folk Victorian", SS, "Vernacular American houses with mass-produced Victorian trim, 1870–1910", "Folk Victorian"),
    ("Late Victorian Plain", SS, "Plain Canadian late-Victorian house type", "Late Victorian Plain"),
    ("Victorian Free Classical", SS, "Australian late-Victorian free classical style, 1880–1900", "Victorian Free Classical"),
    ("Gingerbread houses", SS, "Fretwork-ornamented timber houses of Port-au-Prince, Haiti, 1880s–1920s", "Gingerbread house"),
    ("New Zealand villa", ST, "Ornate timber suburban house with central hall, sash and bay windows, New Zealand, 1870s–1910s", "New Zealand villa"))
add("K2-19", ("Eastlake movement", SS, "Decorative style after Charles Eastlake's Hints on Household Taste, 1870s–1890s", "Eastlake Movement"))
add("K2-21", ("Dutch Colonial Revival", SS, "American gambrel-roofed revival of Dutch colonial houses, 1890s–1930s", "Dutch Colonial Revival architecture"),
    ("Georgian Revival", SS, "Revival of Georgian and Federal forms in Britain and North America, 1880s–1950s", "Georgian Revival architecture"))
add("K2-22", ("Mediterranean Revival", SS, "Florida and California resort style mixing Spanish and Italian forms, 1920s", "Mediterranean Revival architecture"),
    ("Spanish Eclectic", SS, "American Spanish-derived period-revival houses, 1915–1940", "Spanish Eclectic architecture"))
add("K2-24", ("Territorial style", SS, "New Mexico adobe with brick coping and Greek Revival trim, 1846–1912", "Territorial architecture"),
    ("Territorial Revival", SS, "20th-century revival of the New Mexico Territorial style", "Territorial Revival architecture"),
    ("Pueblo Deco", SS, "Art Deco blended with Pueblo and Navajo motifs, 1920s–30s (KiMo Theater)", "Pueblo Deco architecture"))
add("K2-27", ("Brick style", SS, "Russian exposed-brick style (kirpichny stil), 1870s–1910s", "brick style"),
    ("Russian-Byzantine style", SS, "Konstantin Thon's official church style, 1830s–1860s (Cathedral of Christ the Saviour)", "Russian-Byzantine architecture"))
add("K2-30", ("Dragestil", SS, "Norwegian 'dragon style' of timber buildings with Viking-age ornament, 1880–1910", "dragestil"),
    ("Northern Modern", SS, "Russian northern Art Nouveau of St Petersburg, 1900s–1910s", "Northern modern"),
    ("Polish national style", SS, "Polish 1920s national style drawing on manor and vernacular forms", "national style"),
    ("Manor style (styl dworkowy)", SS, "Polish revival of the noble manor house, 1900s–1930s", "styl dworkowy"))
add("K2-34", ("Adirondack Great Camps", SS, "Log and bark lodges of the Adirondacks, New York, 1870s–1930s", "Adirondack Architecture"),
    ("National Park Service rustic", SS, "Parkitecture of US national parks, 1916–1942 (Old Faithful Inn)", "National Park Service rustic"),
    ("WPA Rustic", SS, "Rustic park buildings built under the Works Progress Administration, 1935–43", "WPA Rustic"),
    ("Forest Service rustic", SS, "Rustic buildings of the US Forest Service, 1930s", "Forest Service rustic"))

# K3
add("K3-2", ("Elamite architecture", SS, "Elam in southwestern Iran, 3rd–1st millennium BC (Chogha Zanbil ziggurat)", "Elamite architecture"),
    ("Ziggurat", ST, "Stepped temple platform of Mesopotamia and Elam", W + "Ziggurat"),
    ("Ziggurat of Ur", "Mesopotamian cities, temples and gates", "Ur, Dhi Qar, Iraq, c. 2100 BC (Ur-Nammu); part of UNESCO Ahwar of Southern Iraq", W + "Ziggurat_of_Ur"),
    ("Uruk", "Mesopotamian cities, temples and gates", "Sumerian city, Iraq, 4th millennium BC onwards; Eanna and Anu districts", W + "Uruk"),
    ("Babylon", "Mesopotamian cities, temples and gates", "Capital of Babylonia, Iraq, 2nd–1st millennium BC · UNESCO World Heritage Site", W + "Babylon"),
    ("Etemenanki", "Mesopotamian cities, temples and gates", "Ziggurat of Marduk at Babylon, Iraq, rebuilt 7th–6th century BC", W + "Etemenanki"),
    ("Ishtar Gate", "Mesopotamian cities, temples and gates", "Glazed-brick gate of Babylon, c. 575 BC; reconstructed in the Pergamon Museum, Berlin", W + "Ishtar_Gate"),
    ("Assur", "Mesopotamian cities, temples and gates", "First Assyrian capital, Iraq · UNESCO World Heritage Site", W + "Assur"),
    ("Nimrud", "Mesopotamian cities, temples and gates", "Assyrian capital (Kalhu), Iraq, 9th century BC; Northwest Palace", W + "Nimrud"),
    ("Dur-Sharrukin", "Mesopotamian cities, temples and gates", "Sargon II's capital (Khorsabad), Iraq, c. 717–706 BC", W + "Dur-Sharrukin"),
    ("Nineveh", "Mesopotamian cities, temples and gates", "Assyrian capital, Mosul, Iraq; Sennacherib's Southwest Palace, c. 700 BC", W + "Nineveh"))
add("K3-3", ("Median architecture", SS, "Architecture of the Medes, 8th–6th century BC (Ecbatana, Tepe Nush-i Jan)", "Median architecture"),
    ("Apadana", ST, "Achaemenid columned audience hall (Persepolis, Susa)", W + "Apadana"))
add("K3-6", ("Knossos", "Minoan palaces and sites", "Largest Minoan palace, Heraklion, Crete, c. 1900–1375 BC", W + "Knossos"),
    ("Phaistos", "Minoan palaces and sites", "Minoan palace, southern Crete, c. 2000–1450 BC", W + "Phaistos"),
    ("Zakros", "Minoan palaces and sites", "Minoan palace, eastern Crete, c. 1900–1450 BC", W + "Zakros"),
    ("Hagia Triada", "Minoan palaces and sites", "Minoan villa and settlement near Phaistos, Crete", W + "Hagia_Triada"),
    ("Gournia", "Minoan palaces and sites", "Minoan town, eastern Crete, Late Minoan I", W + "Gournia"),
    ("Palaikastro", "Minoan palaces and sites", "Minoan town, eastern Crete", W + "Palaikastro"),
    ("Akrotiri (prehistoric city)", "Minoan palaces and sites", "Bronze Age town buried by the Thera eruption, Santorini, c. 1600 BC", W + "Akrotiri_(prehistoric_city)"))
add("K3-7", ("Cyclopean masonry", ST, "Unworked massive limestone walling of Mycenaean citadels", "Cyclopean masonry"),
    ("Tholos tomb", ST, "Mycenaean beehive tomb with corbelled dome", W + "Beehive_tomb"),
    ("Mycenae", "Mycenaean citadels and tombs", "Citadel, Argolid, Greece, c. 1600–1100 BC · UNESCO World Heritage Site", W + "Mycenae"),
    ("Lion Gate", "Mycenaean citadels and tombs", "Main gate of the Mycenae citadel, c. 1250 BC", W + "Lion_Gate"),
    ("Treasury of Atreus", "Mycenaean citadels and tombs", "Tholos tomb at Mycenae, c. 1250 BC", W + "Treasury_of_Atreus"),
    ("Grave Circle A, Mycenae", "Mycenaean citadels and tombs", "Royal shaft-grave cemetery, Mycenae, 16th century BC", W + "Grave_Circle_A,_Mycenae"),
    ("Tiryns", "Mycenaean citadels and tombs", "Cyclopean citadel, Argolid, Greece · UNESCO World Heritage Site", W + "Tiryns"),
    ("Palace of Nestor", "Mycenaean citadels and tombs", "Mycenaean palace at Pylos, Messenia, 13th century BC", W + "Palace_of_Nestor"),
    ("Gla", "Mycenaean citadels and tombs", "Mycenaean fortress, Boeotia, 13th century BC", W + "Gla"))
add("K3-8", ("Doric order", ST, "Plainest Greek order, mainland Greece and the western colonies", "Doric order"),
    ("Ionic order", ST, "Volute-capital order of eastern Greece and Ionia", "Ionic order"),
    ("Aeolic order", ST, "Early order with palmette capitals, Aeolis and Lesbos", "Aeolic order"),
    ("Corinthian order", ST, "Acanthus-capital order, from the late 5th century BC", "Corinthian order"),
    ("Peripteral temple", ST, "Temple surrounded by a single colonnade", "peripteral"),
    ("Amphiprostyle temple", ST, "Temple with porticoes at front and rear only", "amphiprostyle"),
    ("Tetrastyle portico", ST, "Portico of four columns", "tetrastyle"),
    ("Hellenistic architecture", SS, "Greek architecture after Alexander, 323–31 BC (Pergamon, Priene, Didyma)", "Hellenistic architecture"))
add("K3-9", ("Banditaccia", "Etruscan buildings and tombs", "Necropolis of Cerveteri, Lazio, 9th–3rd century BC · UNESCO World Heritage Site", W + "Cerveteri"),
    ("Monterozzi necropolis", "Etruscan buildings and tombs", "Painted-tomb necropolis of Tarquinia, Lazio · UNESCO World Heritage Site", W + "Monterozzi_necropolis"),
    ("Tomb of the Reliefs", "Etruscan buildings and tombs", "Stucco-relief chamber tomb, Banditaccia, Cerveteri, 4th century BC", W + "Tomb_of_the_Reliefs"),
    ("Tomb of the Leopards", "Etruscan buildings and tombs", "Painted tomb, Monterozzi, Tarquinia, c. 480–450 BC", W + "Tomb_of_the_Leopards"))
add("K3-10", ("Tuscan order", ST, "Roman simplified Doric order with unfluted shaft", "Tuscan order"),
     ("Composite order", ST, "Roman order combining Ionic volutes and Corinthian acanthus", "Composite order"),
     ("Tetrapylon", ST, "Four-way monumental arch at a crossroads", "tetrapylon"))
add("K3-11", ("Petra", "Nabataean cities, tombs and temples", "Nabataean capital, Ma'an, Jordan, 4th century BC – 2nd century AD · UNESCO World Heritage Site", W + "Petra"),
     ("Al-Khazneh", "Nabataean cities, tombs and temples", "Rock-cut tomb façade ('Treasury'), Petra, Jordan, 1st century AD", W + "Al-Khazneh"),
     ("Ed-Deir, Petra", "Nabataean cities, tombs and temples", "Rock-cut 'Monastery' monument, Petra, Jordan, 1st century AD", W + "Ed-Deir,_Petra"),
     ("Qasr al-Bint", "Nabataean cities, tombs and temples", "Free-standing temple, Petra, Jordan, 1st century BC", W + "Qasr_al-Bint"),
     ("Little Petra", "Nabataean cities, tombs and temples", "Nabataean suburb of Siq al-Barid, Jordan", W + "Little_Petra"),
     ("Hegra (Mada'in Salih)", "Nabataean cities, tombs and temples", "Nabataean tomb city, AlUla, Saudi Arabia, 1st century BC – 1st century AD · UNESCO World Heritage Site", W + "Hegra"),
     ("Avdat", "Nabataean cities, tombs and temples", "Nabataean town on the Incense Route, Negev, Israel · UNESCO World Heritage Site", W + "Avdat"),
     ("Mamshit", "Nabataean cities, tombs and temples", "Nabataean town, Negev, Israel · UNESCO (Incense Route)", W + "Mampsis"),
     ("Shivta", "Nabataean cities, tombs and temples", "Nabataean–Byzantine town, Negev, Israel · UNESCO (Incense Route)", W + "Shivta"))

# K4
add("K4-2", ("Cross-in-square", ST, "Middle Byzantine church plan with central dome on four supports", "cross-in-square"),
    ("Tarnovo school", SS, "Second Bulgarian Empire school of church building, 13th–14th century", "Architecture of the Tarnovo Artistic School"))
add("K4-3", ("Raška school", SS, "Serbian Romanesque-Byzantine school, 12th–13th century (Studenica, Sopoćani)", "Rascian architecture"),
    ("Morava school", SS, "Late Serbian school with rich façade ornament, 1370s–1459 (Ravanica, Kruševac Lazarica)", "Morava architectural school"))
add("K4-4", ("Hrodna school", SS, "12th-century Black Ruthenian school with majolica-studded walls (Kalozha Church)", "architectural school of Hrodna"),
    ("Vladimir-Suzdal school", SS, "White-stone churches of Vladimir-Suzdal, 12th–13th century · UNESCO", "Vladimir-Suzdal school (art)"),
    ("Pskov school", SS, "Pskov limestone churches with belfries, 14th–16th century · UNESCO", "Pskov architectural style"),
    ("Polotsk school", SS, "Polotsk school of the 11th–12th century (St Sophia Cathedral, Polotsk)", "Architectural school of Polock"),
    ("Russian Romanesque", SS, "Romanesque-influenced carved white-stone churches of Vladimir-Suzdal", "Russian Romanesque"))
add("K4-7", ("Merovingian architecture", SS, "Frankish Gaul, 5th–8th century (Baptistery of Saint-Jean, Poitiers)", "Merovingian art"),
    ("Anglo-Saxon architecture", SS, "England, c. 600–1066 (Escomb, Brixworth, Earls Barton)", "Anglo-Saxon architecture"),
    ("Asturian architecture", SS, "Kingdom of Asturias, 8th–10th century · UNESCO (Santa María del Naranco)", "Asturian architecture"),
    ("Lombard architecture", SS, "Lombard Italy, 568–774 (Tempietto longobardo, Cividale) · UNESCO", "Lombard architecture"),
    ("Repoblación architecture", SS, "Churches of the Christian resettlement of the Duero valley, 10th century", "Repoblación art and architecture"),
    ("Visigothic architecture", SS, "Visigothic Hispania, 5th–8th century (San Juan de Baños, San Pedro de la Nave)", "Visigothic architecture"),
    ("Mozarabic architecture", SS, "Iberian Christian building with horseshoe arches, 9th–11th century", "Mozarabic architecture"))
add("K4-10", ("Norman architecture", SS, "Romanesque of Normandy and Anglo-Norman England (Durham Cathedral)", "Norman architecture"),
     ("Florentine Romanesque (Proto-Renaissance)", SS, "Classicising marble-inlaid Romanesque of Florence (San Miniato, Baptistery)", "Proto-Renaissance"),
     ("First Romanesque", SS, "Lombard-band Romanesque of Catalonia, Lombardy and Burgundy, c. 1000–1100", "First Romanesque"),
     ("Cistercian architecture", SS, "Austere abbeys of the Cistercian order, 12th–13th century (Fontenay)", "Cistercian architecture"),
     ("Pisan Romanesque", SS, "Arcaded marble Romanesque of Pisa and Lucca (Piazza dei Miracoli)", "romanesque arte in Pisa"),
     ("Sardinian Romanesque", SS, "Pisan- and Tuscan-influenced churches of Sardinia, 11th–13th century", "Romanesque architecture in Sardinia"),
     ("Catalan Romanesque", SS, "Romanesque of Catalonia (Vall de Boí churches · UNESCO)", "Romanesque art in Catalonia"),
     ("Apulian Romanesque", SS, "Romanesque cathedrals of Apulia (Bari, Trani)", "Romanesque art in Apulia"),
     ("Brick Romanesque", SS, "Brick-built Romanesque of northern Germany and the Baltic", "Brick Romanesque Architecture"),
     ("Provençal Romanesque", SS, "Romanesque of Provence (Saint-Trophime, Arles; Le Thoronet)", "Romanesque art of Provence"))
add("K4-11", ("Norman architecture of Sicily", SS, "Norman kingdom of Sicily, 1071–1194", "Norman architecture of Sicily"))
add("K4-12", ("Voroneț Monastery", "Painted churches and monasteries of Moldavia", "Suceava County, Romania, 1488 (Stephen the Great), exterior frescoes 1547 · UNESCO", W + "Voroneț_Monastery"),
     ("Humor Monastery", "Painted churches and monasteries of Moldavia", "Suceava County, Romania, 1530 · UNESCO (Churches of Moldavia)", W + "Humor_Monastery"),
     ("Moldovița Monastery", "Painted churches and monasteries of Moldavia", "Suceava County, Romania, 1532 · UNESCO (Churches of Moldavia)", W + "Moldovița_Monastery"),
     ("Sucevița Monastery", "Painted churches and monasteries of Moldavia", "Suceava County, Romania, 1585 · UNESCO (Churches of Moldavia)", W + "Sucevița_Monastery"),
     ("Arbore Church", "Painted churches and monasteries of Moldavia", "Suceava County, Romania, 1503 · UNESCO (Churches of Moldavia)", W + "Arbore_Church"),
     ("Probota Monastery", "Painted churches and monasteries of Moldavia", "Suceava County, Romania, 1530 · UNESCO (Churches of Moldavia)", W + "Probota_Monastery"),
     ("Putna Monastery", "Painted churches and monasteries of Moldavia", "Suceava County, Romania, founded 1466 by Stephen the Great", W + "Putna_Monastery"),
     ("Neamț Monastery", "Painted churches and monasteries of Moldavia", "Neamț County, Romania, church of 1497", W + "Neamț_Monastery"),
     ("Dragomirna Monastery", "Painted churches and monasteries of Moldavia", "Suceava County, Romania, 1609", W + "Dragomirna_Monastery"),
     ("Trei Ierarhi Monastery", "Painted churches and monasteries of Moldavia", "Iași, Romania, 1637–39, carved-stone façade", W + "Trei_Ierarhi_Monastery"))

# K5
add("K5-1", ("Elizabethan architecture", SS, "Late Tudor prodigy houses, 1558–1603 (Hardwick Hall, Longleat)", "Elizabethan architecture"))
add("K5-6", ("Chinoiserie", SS, "Chinese-inspired pavilions and interiors, 18th century", "chinoiserie"),
    ("Frederician Rococo", SS, "Rococo of Frederick the Great's Prussia (Sanssouci, Potsdam)", "Frederician Rococo"),
    ("Régence", SS, "Transitional French style, 1715–1723, between Louis XIV and Louis XV", "Regence style"))
add("K5-7", ("Tented-roof church", ST, "Russian church crowned by a tall shatyor (tent) roof", "tented-roof church"),
    ("Yaroslavl school", SS, "Tiled and frescoed merchant churches of Yaroslavl, 17th century · UNESCO", "Yaroslavl school"))
add("K5-9", ("Jeffersonian architecture", SS, "Thomas Jefferson's Palladian-classical style (Monticello, University of Virginia)", "Jeffersonian architecture"))
add("K5-10", ("Regency architecture", SS, "Late Georgian style of 1811–1837 (Nash terraces, Brighton)", "Regency architecture"))
add("K5-11", ("Russian Empire style", SS, "Russian Empire style of Alexander I and Nicholas I (Rossi, Stasov)", "Russian Empire style"))
add("K5-14", ("Zheravna house", ST, "Timber Revival-period house type of Zheravna, Bulgaria", "Жеравненска къща"))
add("K5-15", ("Saltbox", ST, "New England timber house with long rear roof slope", "saltbox"),
     ("Cape Cod house", ST, "Low one-and-a-half-storey New England cottage", "Cape Cod"),
     ("First Period", SS, "New England colonial building before c. 1725", "First Period"),
     ("Tidewater architecture", SS, "Colonial houses of the Chesapeake Tidewater, Virginia and Maryland", "Tidewater architecture"))
add("K5-16", ("Hispanic Baroque", SS, "Baroque of Spain's American and Asian colonies", "Hispanic baroque"),
     ("New Spanish Baroque", SS, "Baroque of the Viceroyalty of New Spain (Mexico), 1650–1780", "New Spanish Baroque"),
     ("Monterey Colonial", SS, "Two-storey adobe houses with balconies, Alta California, 1830s–1840s", "Monterey Colonial architecture"),
     ("Earthquake Baroque", SS, "Massive buttressed Baroque churches of the Philippines · UNESCO", "Earthquake Baroque"))
add("K5-18", ("Brazilian colonial architecture", SS, "Portuguese colonial building in Brazil (Salvador, Ouro Preto, Olinda)", "colonial architecture of Brazil"),
     ("Brazilian Baroque", SS, "Baroque of colonial Brazil, incl. barroco mineiro of Minas Gerais", "Brazilian baroque"))
add("K5-19", ("Creole case", ST, "Timber Creole house of the French Antilles and Réunion", "Creole case"),
     ("Creole architecture (Louisiana)", SS, "French Creole buildings of Louisiana and the Gulf Coast", "Creole architecture in the United States"),
     ("Creole cottage", ST, "Gulf Coast house with full front gallery and high gabled roof, Louisiana, c. 1790–1850", "Creole cottage"))
add("K5-20", ("Dutch colonial architecture of Indonesia", SS, "Dutch East Indies building, 17th–20th century (Indies Empire, New Indies styles)", "colonial architecture of Indonesia"))

# K6
add("K6-1", ("Cottage style", SS, "Arts and Crafts cottage style of the Low Countries", "cottage style"),
    ("English mansion style (Netherlands)", SS, "Dutch landhuis style after the English free-style house, 1900–1930", "English mansion style in the Netherlands"),
    ("American Craftsman", SS, "American Arts and Crafts houses, 1905–1930 (Greene and Greene)", "American Craftsman"),
    ("California bungalow", ST, "One-storey Craftsman bungalow, California and beyond, 1905–1930", "California bungalow"))
add("K6-4", ("Rondocubism", SS, "Czech post-war 'national style' with rounded Cubist forms, 1918–1925", "Rondocubism"))
add("K6-5", ("Amsterdam School", SS, "Dutch Expressionist brick architecture, 1910–1930 (Michel de Klerk, Piet Kramer)", "Amsterdam School"),
    ("Brick Expressionism", SS, "German brick Expressionism, 1920s (Chilehaus, Hamburg)", "Brick Expressionism"),
    ("Dudok style", SS, "Willem Marinus Dudok's cubic brick style (Hilversum Town Hall)", "Dudok-trant"),
    ("Dom Bellot style", SS, "Dom Paul Bellot's brick church style, Netherlands, France and Canada, 1920s–30s", "dombellotisme"))
add("K6-6", ("Googie", SS, "Space-age roadside commercial architecture, US, 1945–1970", "Googie"),
    ("Neo-futurism", SS, "Late 20th–21st-century futurist architecture (Zaha Hadid, Santiago Calatrava)", "neo-futurism"))
add("K6-7", ("Streamline Moderne", SS, "Late Art Deco with curves and horizontal bands, 1930s", "Streamline Moderne"),
    ("PWA Moderne", SS, "US federal public-works Moderne, 1933–1944", "PWA Moderne"),
    ("Wedding-cake style", SS, "Setback skyscraper massing of 1920s New York", "wedding-cake style"))
add("K6-11", ("Heimatschutz architecture", SS, "German homeland-protection style, 1904 onward", "Heimatschutz architecture"),
     ("Heimatstil", SS, "Swiss and German regionalist style, 1890–1950", "Heimatstil"),
     ("Um 1800", SS, "Reform movement reviving the plain classicism around 1800 (Paul Mebes)", "Um 1800"),
     ("Gruppenbau", SS, "Grouped housing estates of the reform movement", "Gruppenbau"))
add("K6-12", ("Bossche School", SS, "Dutch post-war traditionalism of Dom Hans van der Laan's circle", "Bossche School"),
    ("Delft School", SS, "Dutch traditionalist school of M. J. Granpré Molière, 1925–1955", "Delftse School"))
add("K6-16", ("Novecento", SS, "Italian Novecento architecture, Milan, 1920s (Giovanni Muzio)", "Novecento Italiano"),
     ("Monumentalism", SS, "Italian monumental classicism of the 1930s (EUR, Rome)", "monumentalism in architecture"))
add("K6-18", ("Sarasota School", SS, "Florida regional modernism, 1941–1966 (Paul Rudolph, Ralph Twitchell)", "Sarasota School of Architecture"),
     ("Northwest Regional style", SS, "Pacific Northwest timber modernism, 1930s–60s (Pietro Belluschi)", "Northwest Regional style"),
     ("Miami Modern (MiMo)", SS, "Resort modernism of Miami Beach, 1945–1970s (Morris Lapidus)", "Miami Modern architecture"))
add("K6-24", ("New Urbanism", SS, "Traditional neighbourhood planning movement, from the 1980s (Seaside, Florida)", "New Urbanism"),
     ("Radical period", SS, "Italian radical architecture, 1960s–70s (Archizoom, Superstudio)", "Radical period"))

# K7
add("K7-1", ("Bhumija", SS, "Nagara sub-style with miniature spires in rows, Malwa and Deccan, 11th–13th century", "Nagara — Bhumija / Hemadpanti (Deccan)"),
    ("Himalayan hill temples", SS, "Kath-kuni and pagoda-roofed temples of Himachal and Uttarakhand (Hidimba Devi)", "Nagara — Himalayan (Himachal / Uttarakhand)"),
    ("Ahom temple architecture", SS, "Ahom-period temples of Assam (Nilachal type), 16th–18th century", "Assamese / Ahom temple"),
    ("Kashmiri temple architecture", SS, "Karkota and Utpala temples with pyramidal roofs and trefoil arches (Martand)", "Kashmiri (Karkota / Utpala)"),
    ("Chandela architecture", SS, "Chandela temples of Khajuraho, 950–1050", "Nagara — Chandela (Khajuraho)"),
    ("Khajuraho", CE, "Khajuraho Group of Monuments, Madhya Pradesh, c. 950–1050 · UNESCO", "Khajuraho"),
    ("Bodh Gaya (Mahabodhi Temple)", CE, "Mahabodhi Temple, Bihar, brick Nagara tower, 5th–6th century, rebuilt · UNESCO", "Bodh Gaya (Mahabodhi Temple)"))
add("K7-2", ("Deul", ST, "Odishan and Bengali temple tower (rekha, pidha and khakhara deul)", "Deul"),
    ("Bhubaneswar", CE, "Temple city of Odisha: Lingaraja, Mukteshvara, Rajarani", "Bhubaneswar"),
    ("Konark", CE, "Konark Sun Temple, Odisha, 13th century · UNESCO", "Konark"),
    ("Puri", CE, "Jagannath Temple, Puri, Odisha, 12th century", "Puri"))
add("K7-3", ("Jain temples", ST, "Jain temples of Gujarat and Rajasthan (Dilwara, Ranakpur, Palitana)", "Jain temples"),
    ("Pavagadh", CE, "Hill temples and Jain temples, Champaner-Pavagadh, Gujarat · UNESCO", "Pavagadh"))
add("K7-4", ("Pallava architecture", SS, "Pallava temples, 600–900 (Mahabalipuram, Kanchipuram)", "Dravidian — Pallava"),
    ("Chola architecture", SS, "Chola temples, 850–1250 (Brihadisvara, Thanjavur)", "Dravidian — Chola"),
    ("Pandya architecture", SS, "Pandya temples and gopurams of Madurai country", "Pandya"),
    ("Vijayanagara architecture", SS, "Vijayanagara empire, 1336–1646 (Hampi)", "Dravidian — Vijayanagara"),
    ("Nayak architecture", SS, "Madurai and Thanjavur Nayak temples, 16th–18th century", "Nayak"),
    ("Kakatiya architecture", SS, "Kakatiya Telangana, 12th–14th century (Ramappa Temple · UNESCO)", "Kakatiya"),
    ("Sri Lankan kovil", ST, "Tamil Hindu temples of Sri Lanka", "Sri Lankan Dravidian (kovil)"),
    ("Mahabalipuram", CE, "Group of Monuments at Mahabalipuram, Tamil Nadu, 7th–8th century · UNESCO", "Mahabalipuram"),
    ("Hampi", CE, "Vijayanagara capital, Karnataka · UNESCO", "Hampi"))
add("K7-5", ("Hoysala architecture", SS, "Hoysala star-plan temples, Karnataka, 1100–1340 · UNESCO (Belur, Halebidu, Somanathapura)", "Hoysala architecture"),
    ("Western Chalukya architecture", SS, "Kalyani Chalukya temples, 11th–12th century (Lakkundi, Itagi)", "Western Chalukya architecture"),
    ("Badami Chalukya architecture", SS, "Early Chalukya temples, 6th–8th century (Aihole, Badami, Pattadakal)", "Badami Chalukya architecture"),
    ("Pattadakal", CE, "Group of Monuments at Pattadakal, Karnataka, 7th–8th century · UNESCO", "Pattadakal"),
    ("Lakkundi", CE, "Western Chalukya temples and stepwells, Karnataka, 11th–12th century", "Lakkundi"))
add("K7-7", ("At-chala", ST, "Eight-roofed Bengal temple", "At-chala"), ("Char-chala", ST, "Four-roofed Bengal temple", "Char-chala"),
    ("Do-chala", ST, "Two-roofed (hut-roof) Bengal temple", "Do-chala"), ("Jor-bangla", ST, "Paired do-chala temple", "Jor-bangla"),
    ("Ek-ratna", ST, "Single-pinnacle ratna temple", "Ek-ratna"), ("Pancharatna", ST, "Five-pinnacle ratna temple", "Pancharatna"),
    ("Navaratna", ST, "Nine-pinnacle ratna temple", "Navaratna"), ("Panchabimsati-ratna", ST, "Twenty-five-pinnacle ratna temple", "Panchabimsati-ratna"),
    ("Dalan", ST, "Flat-roofed dalan temple", "dalan"),
    ("Bishnupur", CE, "Malla-period terracotta temples, Bankura, West Bengal, 17th–18th century", "Bishnupur"))
add("K7-8", ("Gandharan Buddhist architecture", SS, "Stupas and monasteries of Gandhara, 1st–7th century (Takht-i-Bahi · UNESCO)", "Gandharan Buddhist"),
    ("Stupa", ST, "Hemispherical Buddhist reliquary mound (Sanchi, Dhamek)", "Stupa"),
    ("Mahavihara", ST, "Great monastic university (Nalanda · UNESCO)", "Mahavihara"),
    ("Pala architecture", SS, "Pala-period monasteries of Bengal and Bihar, 8th–12th century", "Pala"))
add("K7-9", ("Ellora", CE, "Ellora Caves, Maharashtra, 6th–10th century; Kailasa Temple · UNESCO", "Ellora"))
add("K7-10", ("Kandyan architecture", SS, "Kingdom of Kandy, 1469–1815 (Temple of the Tooth)", "Sinhalese — Kandyan"),
     ("Anuradhapura period", SS, "Anuradhapura kingdom, 4th century BC – 1017 AD", "Sinhalese — Anuradhapura"),
     ("Polonnaruwa period", SS, "Polonnaruwa kingdom, 1017–1232", "Sinhalese — Polonnaruwa"),
     ("Dagoba", ST, "Sinhalese stupa (Ruwanweli Maha Saya, Jetavanaramaya)", "Dagoba"))
add("K7-11", ("Stupa", ST, "Newar and Tibetan stupas of the valley (Boudhanath, Swayambhunath · UNESCO)", "Stupa"),
     ("Pagoda temple", ST, "Multi-roofed Newar temple (Pashupatinath, Changu Narayan · UNESCO)", "Pagoda temple"))
add("K7-12", ("Kumbum", ST, "Multi-chapelled stupa (Gyantse Kumbum)", "Kumbum"),
     ("Gompa", ST, "Tibetan Buddhist monastery complex", "Monastery (gompa)"),
     ("Palace-fortress", ST, "Dzong-type palace-fortress (Potala Palace · UNESCO)", "Palace-fortress"))
add("K7-14", ("Maratha forts", SS, "Hill and sea forts of the Maratha era, Deccan and Konkan, 17th–18th century", "Deccan hill and sea forts (Maratha era)"),
     ("Hill Forts of Rajasthan", ST, "Amber, Kumbhalgarh, Chittorgarh, Jaisalmer, Gagron, Ranthambore · UNESCO", "Hill forts"))
add("K7-18", 
     ("Bagore-ki-Haveli", "Havelis", "Haveli on Gangaur Ghat, Udaipur, Rajasthan, 18th century; museum", W + "Bagore_Ki_Haveli"),
     ("Haveli of Nau Nihal Singh", "Havelis", "Sikh-period haveli, Walled City of Lahore, Pakistan, 19th century", W + "Haveli_of_Nau_Nihal_Singh"),
     ("Shekhawati", CE, "Region of painted merchant havelis (Mandawa, Nawalgarh, Fatehpur), Rajasthan", W + "Shekhawati"))
add("K7-19", ("Dal Lake", CE, "Srinagar lake with the largest fleet of moored houseboats", W + "Dal_Lake"),
     ("Nigeen Lake", CE, "Srinagar lake with moored houseboats north of Dal Lake", W + "Nigeen_Lake"),
     ("Shikara", ST, "Kashmiri wooden water taxi serving the houseboats", W + "Shikara"))
add("K7-20", ("Shillong", CE, "Hill station of Meghalaya with Assam-type colonial bungalows", W + "Shillong"))

# K8
add("K8-1", ("Paifang", ST, "Chinese memorial or decorative gateway arch", "paifang"),
    ("Chinese palaces", ST, "Imperial palace compounds (Forbidden City, Mukden Palace · UNESCO)", "Chinese Palaces"),
    ("Pagoda", ST, "Chinese Buddhist tower (Small Wild Goose, Liuhe, Iron, Songyue pagodas)", "Pagoda"),
    ("Buddhist temple", ST, "Chinese Buddhist temple complex (Foguang Temple, White Horse Temple)", "Buddhist temple"),
    ("Taoist temple", ST, "Taoist temple (Beijing Dongyue Temple, Xuanmiao Temple)", "Taoist temple"),
    ("Tibeto-Chinese temple", ST, "Qing imperial temples in Tibetan style, Chengde (Putuo Zongcheng, Puning)", "Tibeto-Chinese temple"))
add("K8-2", ("Sanheyuan", ST, "Three-sided courtyard house, northern China and Taiwan", "sanheyuan"),
    ("Hutong", CE, "Beijing alleys of siheyuan courtyard houses", W + "Hutong"))
add("K8-3", ("Yan'an", CE, "Shaanxi city of cliffside yaodong, CCP headquarters 1937–47", W + "Yan%27an"),
    ("Loess Plateau", CE, "Loess region of Shaanxi, Shanxi, Gansu and Henan where yaodong are dug", W + "Loess_Plateau"))
add("K8-4", ("Fujian tulou", ST, "Earthen communal round or square buildings of Hakka and Minnan Fujian · UNESCO", "Fujian tulou"),
    ("Tianluokeng Tulou cluster", "Tulou and walled villages", "Four round and one square tulou, Nanjing County, Fujian · UNESCO", W + "Tianluokeng_Tulou_cluster"),
    ("Tsang Tai Uk", "Tulou and walled villages", "Hakka walled village, Sha Tin, Hong Kong, 1847", W + "Tsang_Tai_Uk"),
    ("Sam Tung Uk Museum", "Tulou and walled villages", "Hakka walled village (1786) turned museum, Tsuen Wan, Hong Kong", W + "Sam_Tung_Uk_Museum"))
add("K8-6", ("Qilou", ST, "Arcaded shophouse of Lingnan and Southeast Asia", W + "Tong_lau"),
    ("Chen Clan Ancestral Hall", "Lingnan buildings and gardens", "Clan academy with ceramic and wood carving, Guangzhou, 1894", W + "Chen_Clan_Ancestral_Hall"),
    ("Foshan Ancestral Temple", "Lingnan buildings and gardens", "Taoist temple, Foshan, Guangdong, rebuilt 1372", W + "Foshan_Ancestral_Temple"),
    ("Qinghui Garden", "Lingnan buildings and gardens", "Lingnan garden, Shunde, Foshan, Ming–Qing", W + "Qinghui_Garden"),
    ("Kaiping Diaolou and Villages", "Lingnan buildings and gardens", "Fortified multi-storey towers of Kaiping, Guangdong, 1900s–1930s · UNESCO", W + "Diaolou"))
add("K8-7", ("Taiwanese temple architecture", SS, "Minnan temples of Taiwan with cut-and-paste ceramic roof ridges", "Taiwanese (Minnan) temple"))
add("K8-9", ("Lilong", ST, "Shanghai alley neighbourhood of shikumen rows", W + "Lilong"),
    ("Xintiandi", "Shikumen neighbourhoods and buildings", "Restored shikumen quarter, Huangpu, Shanghai, 1920s", W + "Xintiandi"),
    ("Tianzifang", "Shikumen neighbourhoods and buildings", "Shikumen lanes of Taikang Road, Shanghai, turned arts quarter", W + "Tianzifang"),
    ("Site of the First National Congress of the Chinese Communist Party", "Shikumen neighbourhoods and buildings", "Shikumen house of 1921, Xintiandi, Shanghai; museum", W + "Site_of_the_First_National_Congress_of_the_Chinese_Communist_Party"))
add("K8-10", ("Nagare-zukuri", ST, "Asymmetrical gabled honden with extended front roof, the commonest shrine style", "nagare-zukuri"),
     ("Gongen-zukuri (ishi-no-ma-zukuri)", ST, "Honden and haiden joined by a stone-floored hall (Nikkō Tōshō-gū)", "Ishi-no-ma-zukuri"),
     ("Shinmei-zukuri", ST, "Archaic raised storehouse style of Ise Grand Shrine", "Shinmei-zukuri"),
     ("Sumiyoshi-zukuri", ST, "Archaic style of Sumiyoshi Taisha, Osaka", "Sumiyoshi-zukuri"),
     ("Taisha-zukuri", ST, "Archaic style of Izumo Taisha", "Taisha-zukuri"),
     ("Kasuga-zukuri", ST, "Small honden with front-gabled roof, after Kasuga Taisha, Nara", "Kasuga-zukuri"),
     ("Hachiman-zukuri", ST, "Two parallel gabled halls, after Usa Jingū", "Hachiman-zukuri"),
     ("Sengen-zukuri", ST, "Two-storey honden of Fujisan Hongū Sengen Taisha", "Sengen-zukuri"))
add("K8-11", ("Azekura-zukuri", ST, "Log storehouse of triangular timbers (Shōsōin)", "azekura-zukuri"),
     ("Karamon", ST, "Gate with cusped Chinese-style gable", "karamon"),
     ("Rōmon", ST, "Two-storey gate with balcony", "rōmon"),
     ("Daibutsuyō", SS, "'Great Buddha style' of Chōgen, Kamakura period (Tōdai-ji Nandaimon)", "Daibutsuyō"),
     ("Sayadō", ST, "Protective sheath hall enclosing an older building", "さやと"),
     ("Setchūyō", SS, "Eclectic mix of wayō, daibutsuyō and zenshūyō, from the 14th century", "Setchūyō"),
     ("Wayō", SS, "Native Japanese temple style descended from Nara and Heian building", "Wayō"),
     ("Kakezukuri", ST, "Hall on a stage of tall piles over a slope (Kiyomizu-dera)", "kakezukuri"),
     ("Japanese pagoda", ST, "Three- and five-storey pagodas and tahōtō", "Pagoda"),
     ("Zenshūyō", SS, "Zen style from Song China, Kamakura period (Engaku-ji Shariden)", "Zenshūyō"))
add("K8-14", ("Chashitsu", ST, "Tea-ceremony room or house", "chashitsu"),
     ("Kindai wafū (modern Japanese-style architecture)", SS, "Meiji–Shōwa traditional building in modern materials", "modern Japanese-style architecture"))
add("K8-15", ("Machiya", ST, "Wooden urban townhouse (Kyoto machiya)", "machiya"),
     ("Nagaya", ST, "Row house under one roof", "nagaya"),
     ("Gasshō-zukuri", ST, "Steep thatched farmhouse of Shirakawa-gō and Gokayama · UNESCO", "gasshō-zukuri"),
     ("Magariya", ST, "L-shaped farmhouse with stable wing, Iwate", "magariya"),
     ("Dozō", ST, "Fireproof clay-walled storehouse (kura)", "dozō"))
add("K8-17", ("Zenpō-kōen-fun", ST, "Keyhole-shaped kofun (Daisen Kofun)", "zenpō-kōen-fun"),
     ("Square kofun", ST, "Square-plan mound (hōfun)", "square kofun"),
     ("Round kofun", ST, "Round mound (enpun), the commonest kofun shape", "round-topped burial mound"),
     ("Octagonal kofun", ST, "Octagonal royal mounds of the late 7th century", "octagonal kofun"),
     ("Zenpō-kōhō-fun", ST, "Square-fronted, square-backed double mound", "Zenpō-kōhō-fun"),
     ("Scallop-shaped kofun", ST, "Round mound with a short square projection (hotategaigata)", "scallop-shaped kofun"))
add("K8-18", ("Hafu-baka", ST, "Gable-roofed stone family tomb of Okinawa", "hahubaka"),
     ("Gusuku", ST, "Ryukyuan stone castle (Shuri, Nakijin, Katsuren · UNESCO)", W + "Gusuku"))
add("K8-19", ("Japanese-Western eclectic architecture", SS, "Wayō-setchū blends of Japanese and Western forms, Meiji–Taishō", "Japanese-Western Eclectic Architecture"))
add("K8-20", ("Korean Buddhist temple", ST, "Sansa mountain monasteries of Korea · UNESCO (Sansa, 2018)", "Korean Buddhist (undated)"),
     ("Korean palaces", ST, "Joseon palaces of Seoul (Gyeongbokgung, Changdeokgung · UNESCO)", "Palaces"))
add("K8-21", ("Ondol", ST, "Underfloor heating system of the hanok", W + "Ondol"),
     ("Bukchon Hanok Village", "Hanok villages and houses", "Joseon-era hanok neighbourhood, Jongno, Seoul", W + "Bukchon_Hanok_Village"),
     ("Namsangol Hanok Village", "Hanok villages and houses", "Five relocated Joseon hanok, Jung District, Seoul", W + "Namsangol_Hanok_Village"),
     ("Jeonju Hanok Village", "Hanok villages and houses", "Some 700 hanok in Jeonju, North Jeolla", W + "Jeonju_Hanok_Village"),
     ("Hahoe Folk Village", "Hanok villages and houses", "Clan village of the Ryu, Andong · UNESCO (Historic Villages of Korea)", W + "Hahoe_Folk_Village"),
     ("Yangdong Folk Village", "Hanok villages and houses", "Clan village, Gyeongju · UNESCO (Historic Villages of Korea)", W + "Yangdong_Folk_Village"),
     ("Korean Folk Village", "Hanok villages and houses", "Open-air museum of relocated houses, Yongin, Gyeonggi", W + "Korean_Folk_Village"),
     ("Unhyeongung", "Hanok villages and houses", "Residence of the Heungseon Daewongun, Seoul, 19th century", W + "Unhyeongung"))

# K9
add("K9-1", ("Pre-Angkorian architecture", SS, "Funan and Chenla temples, 6th–8th century (Sambor Prei Kuk · UNESCO)", "Pre-Angkorian Khmer"),
    ("Post-Angkorian architecture", SS, "Cambodian Buddhist buildings after 1431", "Cambodian Buddhist (post-Angkor)"),
    ("Provincial Angkorian architecture", SS, "Khmer temples in Thailand and Laos (Vat Phou, Phimai, Phanom Rung)", "Khmer (Angkorian, provincial)"),
    ("Banteay Srei style", SS, "Fine pink-sandstone style of the late 10th century", "Banteay Srei"),
    ("Angkor", CE, "Angkor Archaeological Park, Siem Reap · UNESCO (Angkor Wat, Bayon)", "Angkor"),
    ("Koh Ker", CE, "Capital of Jayavarman IV, 928–944 · UNESCO", "Koh Ker"))
add("K9-2", ("Central Javanese candi", SS, "Mataram kingdom, 8th–10th century (Borobudur, Prambanan · UNESCO)", "Javanese candi — Central Java (Mataram)"),
    ("East Javanese candi", SS, "Kediri, Singhasari and Majapahit, 10th–15th century (Penataran, Singhasari)", "Javanese candi — East Java (Kediri / Singhasari / Majapahit)"),
    ("Sumatran candi", SS, "Srivijaya and Melayu brick temples (Muaro Jambi, Muara Takus)", "Sumatran candi (Srivijaya / Melayu)"))
add("K9-3", ("Pura", ST, "Balinese Hindu temple with split gate and meru towers", "Balinese (pura)"))
add("K9-4", ("Pendopo", ST, "Open columned pavilion of the Javanese house and palace", "Pendopo"),
    ("Joglo", ST, "Javanese house with high central roof on four soko guru pillars", W + "Javanese_traditional_house"),
    ("Kraton Ngayogyakarta Hadiningrat", "Kraton and houses", "Sultan's palace of Yogyakarta, 1755", W + "Kraton_Ngayogyakarta_Hadiningrat"),
    ("Pura Mangkunegaran", "Kraton and houses", "Palace of the Mangkunegara princes, Surakarta, 1757", W + "Pura_Mangkunegaran"),
    ("Kotagede", "Kraton and houses", "Old Mataram capital with joglo houses, Yogyakarta", W + "Kotagede"))
add("K9-5", ("Pagan architecture", SS, "Pagan kingdom, 11th–13th century (Ananda, Shwezigon, Thatbyinnyu) · UNESCO", "Burmese — Pagan"),
    ("Mrauk U architecture", SS, "Arakanese kingdom of Mrauk U, 15th–18th century", "Arakanese (Mrauk U)"),
    ("Bagan", CE, "Over 2,000 surviving temples on the Irrawaddy plain · UNESCO", "Bagan"))
add("K9-6", ("Lanna architecture", SS, "Northern Thai kingdom of Lanna, 13th–18th century (Chiang Mai)", "Thai — Lanna"),
    ("Ayutthaya architecture", SS, "Ayutthaya kingdom, 1351–1767 · UNESCO", "Thai — Ayutthaya"),
    ("Sukhothai architecture", SS, "Sukhothai kingdom, 13th–15th century · UNESCO", "Thai — Sukhothai"),
    ("Rattanakosin architecture", SS, "Bangkok period from 1782 (Wat Phra Kaew, Wat Arun)", "Thai — Rattanakosin"))
add("K9-7", ("Luang Prabang", CE, "Royal town of Lan Xang (Wat Xieng Thong) · UNESCO", "Luang Prabang"),
    ("Vientiane", CE, "Pha That Luang, Wat Si Saket", "Vientiane"))
add("K9-8", ("Mỹ Sơn", CE, "Cham sanctuary, Quảng Nam, 4th–13th century · UNESCO", "Mỹ Sơn"))
add("K9-9", ("Chùa (Buddhist pagoda)", ST, "Vietnamese Buddhist pagoda complexes, Lý to Nguyễn period", "Vietnamese Buddhist (Lý – Nguyễn)"),
    ("Imperial City of Huế", CE, "Nguyễn dynasty citadel, Huế, 1804–1945 · UNESCO", W + "Imperial_City_of_Huế"))
add("K9-10", ("Rumah Bolon", ST, "Large Toba Batak family house with saddle roof", W + "Batak_architecture"),
     ("Samosir", CE, "Island in Lake Toba with Toba Batak house villages", W + "Samosir"))
add("K9-11", ("Bahay na bato", ST, "Colonial stone-and-wood house developed from the bahay kubo", W + "Bahay_na_bato"))

# K10
add("K10-1", ("Stele", ST, "Monolithic granite stelae of Aksum carved as multi-storey buildings", W + "Obelisk_of_Axum"),
     ("Obelisk of Axum", "Aksumite sites", "Granite stele, Northern Stelae Park, Aksum, 4th century; returned from Rome 2005", W + "Obelisk_of_Axum"),
     ("King Ezana's Stele", "Aksumite sites", "Standing stele, Aksum, Ethiopia, 4th century · UNESCO (Aksum)", W + "King_Ezana%27s_Stele"),
     ("Dungur", "Aksumite sites", "Aksumite elite mansion, Aksum, 6th century", W + "Dungur"),
     ("Yeha", "Aksumite sites", "Pre-Aksumite Great Temple, Tigray, c. 700 BC", W + "Yeha"),
     ("Debre Damo", "Aksumite sites", "Monastery church in Aksumite timber-and-stone style, Tigray, 6th century", W + "Debre_Dammo"))
add("K10-2", ("Lalibela", CE, "Eleven monolithic churches, Amhara, 12th–13th century · UNESCO", "Lalibela"))
add("K10-4", ("Meroë", CE, "Meroitic royal city and pyramid fields · UNESCO (Island of Meroe)", "Meroë"),
     ("Napata", CE, "Jebel Barkal, El-Kurru, Nuri, Sanam · UNESCO (Gebel Barkal)", "Napata"))
add("K10-5", ("Khami", CE, "Torwa capital, Zimbabwe, 15th–17th century · UNESCO", "Khami"),
     ("Mapungubwe", CE, "Kingdom of Mapungubwe, Limpopo, South Africa · UNESCO", "Mapungubwe"),
     ("Naletale", CE, "Rozvi dry-stone ruin with decorated walls, Zimbabwe", "Naletale"),
     ("Great Zimbabwe", "Zimbabwe culture dry-stone sites", "Hill Complex and Great Enclosure, Masvingo, 11th–15th century · UNESCO", W + "Great_Zimbabwe"))
add("K10-6", ("Kasbah", ST, "Fortified earthen residence of southern Morocco", W + "Kasbah"),
     ("Mauritanian ksour", SS, "Stone ksour of Ouadane, Chinguetti, Tichitt and Oualata · UNESCO", "Saharan stone (Mauritania ksour)"))
add("K10-7", ("Gidan Rumfa", "Hausa palaces and mosques", "Emir's palace, Kano, Nigeria, 15th century", W + "Gidan_Rumfa"),
     ("Gobarau Minaret", "Hausa palaces and mosques", "Mud-brick minaret, Katsina, Nigeria, 15th century", W + "Gobarau_Minaret"),
     ("Zaria", CE, "Hausa city of Zazzau, famed for decorated mud architecture", W + "Zaria"),
     ("Kano", CE, "Hausa city with walls, gates and Kurmi market", W + "Kano"))

# K11
add("K11-1", ("Puuc", SS, "Northern Yucatán style of veneer masonry and mosaic friezes (Uxmal, Kabah)", "Maya — Puuc"),
     ("Río Bec", SS, "Campeche style of false towers, 8th–9th century", "Maya — Río Bec"),
     ("Chenes", SS, "Campeche style of monster-mouth doorways", "Maya — Chenes"),
     ("Usumacinta style", SS, "Palenque, Yaxchilan and Piedras Negras", "Usumacinta"),
     ("Petén style", SS, "Central Petén lowland style (Tikal, Uaxactún)", "Maya — southern lowlands (Petén / Usumacinta / Belize)"))
add("K11-2", ("Zapotec and Mixtec architecture", SS, "Oaxaca: Monte Albán, Mitla, Yagul", "Zapotec / Mixtec (Oaxaca)"),
     ("Classic Veracruz architecture", SS, "El Tajín and Gulf Coast sites", "Classic Veracruz / Totonac"),
     ("Teotihuacan architecture", SS, "Teotihuacan, 1st–6th century", "Teotihuacan"),
     ("Olmec architecture", SS, "Gulf Coast Olmec centres (La Venta, San Lorenzo)", "Olmec"),
     ("Toltec architecture", SS, "Toltec Tula and related sites, 10th–12th century", "Toltec"),
     ("Talud-tablero", ST, "Sloping-panel-and-tablet terrace profile of Teotihuacan pyramids", "Talud-tablero"))
add("K11-3", ("Templo Mayor", "Aztec temples and cities", "Twin-temple pyramid of Tenochtitlan, Mexico City, 1325–1521", W + "Templo_Mayor"),
     ("Tlatelolco (altepetl)", "Aztec temples and cities", "Twin city of Tenochtitlan with ceremonial precinct, Mexico City", W + "Tlatelolco_(altepetl)"),
     ("Malinalco", "Aztec temples and cities", "Rock-cut eagle and jaguar warrior temple, State of Mexico, c. 1500", W + "Malinalco"),
     ("Tenayuca", "Aztec temples and cities", "Pyramid with serpent wall, Tlalnepantla, State of Mexico", W + "Tenayuca"),
     ("Teopanzolco", "Aztec temples and cities", "Tlahuica twin-temple pyramid, Cuernavaca, Morelos", W + "Teopanzolco"))
add("K11-4", ("Cusco", CE, "Inca capital (Coricancha, Sacsayhuamán) · UNESCO", "Cusco"),
     ("Inca road system", ST, "Qhapaq Ñan road network and bridges · UNESCO", "Inca road and bridges"),
     ("Ashlar masonry", ST, "Fitted polygonal and coursed stonework of the Incas", W + "Inca_architecture"))
add("K11-5", ("Chavín", SS, "Chavín de Huántar, 1200–500 BC · UNESCO", "Chavín"),
     ("Moche", SS, "Adobe huacas of the Moche, 1st–8th century (Huaca del Sol, Huaca de la Luna)", "Moche"),
     ("Wari", SS, "Wari administrative centres, 6th–11th century (Pikillaqta)", "Wari"),
     ("Chimú", SS, "Chan Chan adobe city, 9th–15th century · UNESCO", "Chimú"),
     ("Chachapoya", SS, "Kuélap fortress and cliff tombs, 9th–15th century", "Chachapoya"),
     ("Caral / Norte Chico", SS, "Platform mounds of Caral-Supe, c. 2600 BC · UNESCO", "Caral / Norte Chico"),
     ("Muisca architecture", SS, "Muisca of the Colombian highlands", "Muisca architecture"),
     ("Regional Andean cultures", SS, "Recuay, Lima, Sicán and other regional cultures", "Andean regional (Recuay, Lima, Sicán, ...)"),
     ("Tiwanaku", CE, "Tiwanaku, Pumapunku, Kalasasaya, Akapana, Bolivia · UNESCO", "Tiwanaku"))
add("K11-6", ("Mesa Verde", CE, "Cliff dwellings, Colorado, 600–1300 · UNESCO", "Mesa Verde"),
     ("Chacoan great house", ST, "Planned multi-storey masonry great houses of Chaco Canyon and its outliers · UNESCO", "Chacoan great houses"),
     ("Taos Pueblo", CE, "Living multi-storey adobe pueblo, New Mexico · UNESCO", "Taos Pueblo"))
add("K11-7", ("Mississippian culture", SS, "Platform-mound towns, 800–1600 (Cahokia · UNESCO, Moundville, Etowah, Spiro)", "Mississippian"),
     ("Hopewell tradition", SS, "Geometric earthworks of Ohio, 1st–5th century · UNESCO", "Hopewell"),
     ("Poverty Point", SS, "Archaic earthworks, Louisiana, c. 1700–1100 BC · UNESCO", "Poverty Point"))

# K12
add("K12-1", ("Whare whakairo", ST, "Carved meeting house, the full form of the wharenui", W + "Wharenui"),
     ("Hinemihi", "Wharenui (meeting houses)", "Meeting house of 1881 from Te Wairoa, now at Clandon Park, Surrey", W + "Hinemihi"),
     ("Rangiātea Church", "Wharenui (meeting houses)", "Māori church, Ōtaki, 1849–51 (destroyed 1995, rebuilt)", W + "Rangiātea_Church"),
     ("Raharuhi Rukupō", "Makers", "Ngāti Kaipoho master carver of Te Hau ki Tūranga (d. 1873)", W + "Raharuhi_Rukup%C5%8D"))
add("K12-2", ("Fale tele", ST, "Large round Samoan guest house of the village", W + "Architecture_of_Samoa"),
     ("Faleo'o", ST, "Small Samoan house, now often a beach fale", W + "Architecture_of_Samoa"))
add("K12-3", ("Kiribati", CE, "Gilbert Islands, where the maneaba is the village meeting house", W + "Kiribati"))
add("K12-4", ("Sepik River", CE, "Region of the tambaran haus (spirit houses) of Papua New Guinea", W + "Sepik"))
add("K12-5", ("Ahu Tongariki", "Ahu and marae", "Largest ahu of Rapa Nui, 15 moai, Chile · UNESCO", W + "Ahu_Tongariki"),
     ("Taputapuātea marae", "Ahu and marae", "Marae complex, Raiatea, French Polynesia · UNESCO World Heritage Site", W + "Taputapuatea_marae"),
     ("Haʻamonga ʻa Maui", "Ahu and marae", "Trilithon, Tongatapu, Tonga, c. 1200", W + "Ha%CA%BBamonga_%CA%BBa_Maui"),
     ("Heiau", ST, "Hawaiian temple platform, counterpart of the marae", W + "Heiau"),
     ("Puʻukoholā Heiau National Historic Site", "Ahu and marae", "Heiau built by Kamehameha I, Hawaii, 1790–91", W + "Pu%CA%BBukohol%C4%81_Heiau_National_Historic_Site"))
add("K12-6", ("Leluh (Kosrae)", CE, "Basalt-walled royal city, Kosrae, Micronesia, 13th–19th century", "Leluh (Kosrae)"),
     ("Nan Madol", "Saudeleur megalithic sites", "Basalt islet city off Pohnpei, Micronesia, c. 1180–1628 · UNESCO World Heritage Site", W + "Nan_Madol"))
add("K12-7", ("Churches of Chiloé", "Churches of Chiloé", "Sixteen wooden churches of the Chiloé archipelago, Chile, 18th–19th century · UNESCO World Heritage Site", W + "Churches_of_Chilo%C3%A9"),
     ("Palafito", ST, "Timber stilt house over the water, Castro, Chiloé", W + "Stilt_house"))
add("K12-8", ("Wealden hall house", ST, "Timber-framed open-hall house with jettied end bays, Kent and Sussex, 14th–16th century", "Wealden hall house"),
     ("Weald and Downland Living Museum", CE, "Open-air museum of rescued vernacular buildings, Singleton, West Sussex", W + "Weald_and_Downland_Living_Museum"),
     ("Avoncroft Museum of Historic Buildings", CE, "Open-air museum of rescued buildings, Bromsgrove, Worcestershire", W + "Avoncroft_Museum_of_Historic_Buildings"),
     ("St Fagans National Museum of History", CE, "Open-air museum of Welsh buildings, Cardiff", W + "St_Fagans_National_Museum_of_History"))
add("K12-9", ("German Fachwerk", ST, "Exposed timber framing with infill (half-timbering), Germany and Alsace, from the 14th century", "German Fachwerk"),
     ("Quedlinburg", CE, "Town of over 1,300 half-timbered houses, Saxony-Anhalt · UNESCO", W + "Quedlinburg"))
add("K12-10", 
     ("Kosovo", CE, "Dukagjini plain (Deçan, Junik, Gjakova), heartland of the kulla", W + "Kosovo"))
add("K12-11", ("Vainakh tower architecture", SS, "Battle and residential towers of Chechnya and Ingushetia, 12th–17th century", W + "Vainakh_tower_architecture"),
     ("Vovnushki", "Vainakh towers", "Tower complex on cliffs, Dzheyrakhsky District, Ingushetia", W + "Vovnushki"),
     ("Erzi", "Vainakh towers", "Fortified tower village, Dzheyrakhsky District, Ingushetia", W + "Erzi"),
     ("Egikal", "Vainakh towers", "Tower village, Dzheyrakhsky District, Ingushetia", W + "Egikal"))
add("K12-12", ("Hórreo", ST, "Raised granary on pillars, Galicia and Asturias", W + "H%C3%B3rreo"),
     ("Palloza", ST, "Round stone hut with thatched roof, Ancares, León and Galicia", W + "Palloza"),
     ("Cortijo", ST, "Andalusian farmstead with courtyard", W + "Cortijo"))
add("K12-13", ("Trullo", ST, "Corbelled dry-stone hut, Apulia", W + "Trullo"),
     ("Alberobello", CE, "Town of trulli, Apulia · UNESCO (Trulli of Alberobello)", W + "Alberobello"),
     ("Sassi di Matera", CE, "Cave dwellings of Matera, Basilicata · UNESCO", W + "Sassi_di_Matera"))
add("K12-14", ("Shotgun house", ST, "Narrow one-room-wide house with rooms in line front to back, US South, c. 1865–1920s", "Shotgun house"))
add("K12-15", 
     ("Røros", CE, "Mining town of turf-roofed log houses, Norway · UNESCO", W + "R%C3%B8ros"),
     ("Gammelstad Church Town", CE, "Church town of log cottages, Luleå, Sweden · UNESCO", W + "Gammelstad_Church_Town"),
     ("Skansen", CE, "Open-air museum of Swedish log buildings, Stockholm, founded 1891", W + "Skansen"),
     ("Norsk Folkemuseum", CE, "Open-air museum of Norwegian log buildings, Bygdøy, Oslo", W + "Norwegian_Museum_of_Cultural_History"),
     ("Petäjävesi Old Church", "Log churches and buildings", "Log church, Central Finland, 1763–65 · UNESCO World Heritage Site", W + "Pet%C3%A4j%C3%A4vesi_Old_Church"),
     ("Old Rauma", CE, "Wooden town, Finland · UNESCO", W + "Old_Rauma"))
add("K12-16", ("Ballenberg", CE, "Swiss Open-Air Museum of rural buildings, Brienz, Bern", W + "Ballenberg"))
add("K12-17", ("Longère", ST, "Long, narrow single-storey longhouse of farmers and artisans, Brittany and Normandy", "Longère"),
     ("Borie", ST, "Dry-stone hut of Provence (Village des Bories, Gordes)", W + "Borie"))
add("K12-18", ("Oia, Greece", CE, "Cave and whitewashed houses of Santorini", W + "Oia,_Greece"))
add("K12-19", ("George Washington House (Barbados)", CE, "18th-century plantation house in Bridgetown, setting of chattel-house villages", W + "George_Washington_House_(Barbados)"))
add("K12-20", ("Miegunyah", "Queenslanders", "Queenslander house, Bowen Hills, Brisbane, 1886; museum", W + "Miegunyah"),
     ("Newstead House", "Queenslanders", "Oldest surviving residence in Brisbane, 1846; verandahed house museum", W + "Newstead_House,_Brisbane"))

# K13 gardens
add("K13-1", ("Charbagh", ST, "Fourfold garden divided by water channels", "Charbagh"),
     ("Pasargadae", "Persian gardens", "Achaemenid royal garden of Cyrus the Great, Fars, Iran, 6th century BC · UNESCO", W + "Pasargadae"),
     ("Fin Garden", "Persian gardens", "Safavid garden, Kashan, Iran, 1590 · UNESCO (The Persian Garden)", W + "Fin_Garden"),
     ("Eram Garden", "Persian gardens", "Qajar garden, Shiraz, Iran · UNESCO (The Persian Garden)", W + "Eram_Garden"),
     ("Chehel Sotoun", "Persian gardens", "Safavid pavilion garden, Isfahan, 1647 · UNESCO (The Persian Garden)", W + "Chehel_Sotoun"),
     ("Shazdeh Garden", "Persian gardens", "Qajar terraced garden, Mahan, Kerman, Iran · UNESCO (The Persian Garden)", W + "Shazdeh_Garden"),
     ("Dowlatabad Garden", "Persian gardens", "Zand garden with tallest windcatcher, Yazd, Iran · UNESCO (The Persian Garden)", W + "Dowlatabad_Garden"),
     ("Akbarieh Garden", "Persian gardens", "Garden, Birjand, South Khorasan · UNESCO (The Persian Garden)", W + "Akbarieh_Garden"))
add("K13-2", ("Charbagh", ST, "Fourfold garden divided by water channels, the Mughal garden's basic plan", W + "Charbagh"),
     ("Bagh-e Babur", "Mughal gardens", "Babur's terraced garden and tomb, Kabul, Afghanistan, c. 1528", W + "Gardens_of_Babur"),
     ("Ram Bagh", "Mughal gardens", "Earliest Mughal garden in India (Aram Bagh), Agra, 1528", W + "Ram_Bagh"),
     ("Humayun's Tomb", "Mughal gardens", "Tomb garden, Delhi, 1570 · UNESCO World Heritage Site", W + "Humayun%27s_tomb"),
     ("Shalimar Bagh, Srinagar", "Mughal gardens", "Jahangir's terraced garden on Dal Lake, Srinagar, 1619", W + "Shalimar_Bagh,_Srinagar"),
     ("Nishat Bagh", "Mughal gardens", "Twelve-terrace garden on Dal Lake, Srinagar, 1633", W + "Nishat_Bagh"),
     ("Achabal Gardens", "Mughal gardens", "Spring-fed Mughal garden, Anantnag, Kashmir, 1620", W + "Achabal_Gardens"),
     ("Shalimar Gardens, Lahore", "Mughal gardens", "Shah Jahan's terraced garden, Lahore, 1641–42 · UNESCO World Heritage Site", W + "Shalamar_Gardens,_Lahore"),
     ("Mehtab Bagh", "Mughal gardens", "Moonlight garden facing the Taj Mahal, Agra, c. 1631–35", W + "Mehtab_Bagh"),
     ("Pinjore Gardens", "Mughal gardens", "Yadavindra Gardens, terraced Mughal garden, Pinjore, Haryana, 17th century", W + "Yadavindra_Gardens"))
add("K13-3", ("Classical Gardens of Suzhou", CE, "Nine scholar gardens of Suzhou, Jiangsu, 11th–19th century · UNESCO", "Classical Gardens of Suzhou"),
     ("Lingnan garden", SS, "Cantonese garden style of Guangdong (Yuyin Shanfang, Qinghui Garden)", "Lingnan garden"),
     ("Humble Administrator's Garden", "Suzhou and Jiangnan gardens", "Suzhou, 1509 · UNESCO (Classical Gardens of Suzhou)", W + "Humble_Administrator%27s_Garden"),
     ("Lingering Garden", "Suzhou and Jiangnan gardens", "Suzhou, 1593 · UNESCO (Classical Gardens of Suzhou)", W + "Lingering_Garden"),
     ("Master of the Nets Garden", "Suzhou and Jiangnan gardens", "Suzhou, 12th century, rebuilt 1770 · UNESCO (Classical Gardens of Suzhou)", W + "Master_of_the_Nets_Garden"),
     ("Canglang Pavilion", "Suzhou and Jiangnan gardens", "Suzhou, 1044, oldest of the Suzhou gardens · UNESCO", W + "Canglang_Pavilion"),
     ("Lion Grove Garden", "Suzhou and Jiangnan gardens", "Suzhou, 1342, famed for rockery · UNESCO (Classical Gardens of Suzhou)", W + "Lion_Grove_Garden"),
     ("Yu Garden", "Suzhou and Jiangnan gardens", "Shanghai, 1559–77", W + "Yu_Garden"),
     ("Ge Garden", "Suzhou and Jiangnan gardens", "Yangzhou salt-merchant garden, 1818", W + "Geyuan"),
     ("Summer Palace", "Imperial gardens", "Qing imperial garden, Beijing, 1750 · UNESCO World Heritage Site", W + "Summer_Palace"),
     ("Old Summer Palace", "Imperial gardens", "Yuanmingyuan, Qing imperial garden, Beijing, destroyed 1860", W + "Old_Summer_Palace"),
     ("Chengde Mountain Resort", "Imperial gardens", "Qing summer palace and park, Hebei, 1703–92 · UNESCO", W + "Chengde_Mountain_Resort"))
add("K13-4", ("Japanese dry garden (karesansui)", ST, "Dry landscape of raked gravel and rocks", "Japanese dry garden (karesansui)"),
     ("Stroll garden (kaiyū-shiki teien)", ST, "Promenade garden round a pond", "Stroll garden (kaiyū-shiki teien)"),
     ("Roji", ST, "Tea garden leading to the tea house", W + "Roji"),
     ("Ryōan-ji", "Japanese gardens", "Zen dry garden of 15 rocks, Kyoto, late 15th century · UNESCO (Kyoto)", W + "Ry%C5%8Dan-ji"),
     ("Daisen-in", "Japanese gardens", "Karesansui of Daitoku-ji subtemple, Kyoto, 1509", W + "Daisen-in"),
     ("Saihō-ji (Kyoto)", "Japanese gardens", "Moss garden by Musō Soseki, Kyoto, 1339 · UNESCO (Kyoto)", W + "Saih%C5%8D-ji_(Kyoto)"),
     ("Tenryū-ji", "Japanese gardens", "Pond garden by Musō Soseki, Arashiyama, Kyoto · UNESCO (Kyoto)", W + "Tenry%C5%AB-ji"),
     ("Katsura Imperial Villa", "Japanese gardens", "Stroll garden and villa, Kyoto, 17th century", W + "Katsura_Imperial_Villa"),
     ("Kenroku-en", "Japanese gardens", "Daimyō stroll garden, Kanazawa, 17th–19th century; Three Great Gardens", W + "Kenroku-en"),
     ("Kōraku-en", "Japanese gardens", "Daimyō stroll garden, Okayama, 1700; Three Great Gardens", W + "K%C5%8Draku-en"),
     ("Kairaku-en", "Japanese gardens", "Plum garden, Mito, 1842; Three Great Gardens", W + "Kairaku-en"),
     ("Ritsurin Garden", "Japanese gardens", "Daimyō stroll garden, Takamatsu, 17th century", W + "Ritsurin_Garden"),
     ("Koishikawa Kōrakuen", "Japanese gardens", "Daimyō garden, Tokyo, 1629", W + "Koishikawa-K%C5%8Drakuen"))
add("K13-5", ("Villa d'Este", "Italian Renaissance gardens", "Terraced water garden by Pirro Ligorio, Tivoli, 1560–72 · UNESCO", W + "Villa_d%27Este"),
     ("Villa Lante", "Italian Renaissance gardens", "Mannerist water garden, Bagnaia, Viterbo, 1566 onward", W + "Villa_Lante"),
     ("Boboli Gardens", "Italian Renaissance gardens", "Medici garden behind the Palazzo Pitti, Florence, 1550 onward", W + "Boboli_Gardens"),
     ("Villa di Castello", "Italian Renaissance gardens", "Medici villa garden by Niccolò Tribolo, Florence, 1538 · UNESCO (Medici Villas)", W + "Villa_di_Castello"),
     ("Gardens of Bomarzo", "Italian Renaissance gardens", "Park of monsters, Bomarzo, Lazio, 1552", W + "Gardens_of_Bomarzo"),
     ("Villa Farnese", "Italian Renaissance gardens", "Palazzo and gardens, Caprarola, 1559–75", W + "Villa_Farnese"),
     ("Villa Medici at Pratolino", "Italian Renaissance gardens", "Buontalenti's lost wonder garden, Vaglia, Florence, 1569", W + "Villa_di_Pratolino"),
     ("Villa Aldobrandini", "Italian Renaissance gardens", "Water theatre garden, Frascati, 1598–1603", W + "Villa_Aldobrandini"),
     ("Orto botanico di Padova", "Italian Renaissance gardens", "Oldest academic botanical garden, Padua, 1545 · UNESCO", W + "Orto_botanico_di_Padova"))
add("K13-6", ("Vaux-le-Vicomte", "French formal gardens", "Le Nôtre's first great garden, Maincy, Seine-et-Marne, 1656–61", W + "Vaux-le-Vicomte"),
     ("Gardens of Versailles", "French formal gardens", "Le Nôtre's royal gardens, Versailles, 1661–1700 · UNESCO", W + "Gardens_of_Versailles"),
     ("Tuileries Garden", "French formal gardens", "Royal garden redesigned by Le Nôtre, Paris, 1664", W + "Tuileries_Garden"),
     ("Château de Chantilly", "French formal gardens", "Le Nôtre's parterres and Grand Canal, Chantilly, 1663 onward", W + "Ch%C3%A2teau_de_Chantilly"),
     ("Château de Villandry", "French formal gardens", "Restored Renaissance-style formal and kitchen gardens, Indre-et-Loire", W + "Ch%C3%A2teau_de_Villandry"),
     ("Château de Sceaux", "French formal gardens", "Le Nôtre's park for Colbert, Sceaux, 1670s", W + "Ch%C3%A2teau_de_Sceaux"),
     ("Château de Saint-Cloud", "French formal gardens", "Domaine national with Le Nôtre's Grande Cascade, Saint-Cloud", W + "Ch%C3%A2teau_de_Saint-Cloud"),
     ("Herrenhausen Gardens", "French formal gardens", "Baroque formal garden, Hanover, 1666–1714", W + "Herrenhausen_Gardens"),
     ("Claude Mollet", "Makers", "Royal gardener of Henri IV, inventor of the parterre de broderie (c. 1564–1649)", W + "Claude_Mollet"))
add("K13-7", ("Stourhead", "English landscape gardens", "Henry Hoare's lakeside landscape garden, Wiltshire, 1741–80", W + "Stourhead"),
     ("Stowe House", "English landscape gardens", "Landscape garden by Bridgeman, Kent and Brown, Buckinghamshire, 1710s–1770s", W + "Stowe_House"),
     ("Rousham House", "English landscape gardens", "William Kent's landscape garden, Oxfordshire, 1738–41", W + "Rousham_House"),
     ("Studley Royal Park", "English landscape gardens", "Water garden with Fountains Abbey, North Yorkshire · UNESCO", W + "Studley_Royal_Park"),
     ("Blenheim Palace", "English landscape gardens", "Capability Brown's park, Woodstock, Oxfordshire, 1760s · UNESCO", W + "Blenheim_Palace"),
     ("Painshill", "English landscape gardens", "Charles Hamilton's landscape garden, Cobham, Surrey, 1738–73", W + "Painshill"),
     ("Chiswick House", "English landscape gardens", "Early landscape garden by Lord Burlington and Kent, London, 1720s", W + "Chiswick_House"),
     ("Wörlitz Park", "English landscape gardens", "Garden Kingdom of Dessau-Wörlitz, Germany, 1769–1800 · UNESCO", W + "Dessau-W%C3%B6rlitz_Garden_Realm"),
     ("Charles Bridgeman", "Makers", "Royal gardener, pioneer of the ha-ha and the landscape style (1690–1738)", W + "Charles_Bridgeman"))

# K14
add("K14-1", ("Omiya Bonsai Village", CE, "Bonsai nursery village, Saitama, from 1925", W + "%C5%8Cmiya_Bonsai_Village"),
     ("National Bonsai & Penjing Museum", "Collections", "US National Arboretum, Washington, D.C., from 1976", W + "National_Bonsai_Foundation"),
     ("Yamaki Pine", "Bonsai trees", "Japanese white pine that survived Hiroshima; National Bonsai & Penjing Museum", W + "Yamaki_Pine"),
     ("John Y. Naka", "Makers", "Japanese-American bonsai master (1914–2004)", W + "John_Naka"),
     ("Masahiko Kimura", "Makers", "Japanese bonsai artist, 'magician' of deadwood styling (b. 1940)", W + "Masahiko_Kimura"))
add("K14-2", ("Shanshui penjing", ST, "Rock landscape penjing", W + "Penjing"),
     ("Shumu penjing", ST, "Tree penjing", W + "Penjing"),
     ("Shuihan penjing", ST, "Water-and-land penjing combining trees, rocks and water", W + "Penjing"),
     ("Hòn non bộ", ST, "Vietnamese counterpart of rock penjing (separate leaf)", W + "H%C3%B2n_non_b%E1%BB%99"),
     ("Wu Yee-sun", "Makers", "Hong Kong penjing master and author, Man Lung Garden (1900–2005)", W + "Wu_Yee-sun"))
add("K14-3", ("Bonsai", ST, "Japanese tree art, related to hòn non bộ through penjing", W + "Bonsai"))
add("K14-4", ("Ikenobō", "Schools", "Oldest school, Rokkaku-dō, Kyoto, from the 15th century (rikka, shōka)", W + "Ikenob%C5%8D"),
     ("Ohara-ryū", "Schools", "School founded by Ohara Unshin, 1895 (moribana)", W + "Ohara-ry%C5%AB"),
     ("Sōgetsu-ryū", "Schools", "Modern free-style school founded by Sōfū Teshigahara, 1927", W + "S%C5%8Dgetsu-ry%C5%AB"),
     ("Rikka", ST, "Standing-flower formal style of Ikenobō", W + "Ikebana"),
     ("Moribana", ST, "Piled-up style in a shallow container", W + "Ikebana"),
     ("Nageire", ST, "Thrown-in style in a tall vase", W + "Ikebana"),
     ("Sōfū Teshigahara", "Makers", "Founder of the Sōgetsu school (1900–1979)", W + "S%C5%8Df%C5%AB_Teshigahara"))

# second round (titles verified against enwiki sitelinks on Wikidata)
add("K1-11", ("Isfahani style", SS, "Pirnia's Isfahani style of Persian architecture, Safavid to Qajar period", W + "Isfahani_style"))
add("K7-19", ("Srinagar", CE, "Capital of Kashmir; houseboats moored on Dal and Nigeen lakes and the Jhelum", W + "Srinagar"),
     ("Jhelum River", CE, "River through Srinagar lined with older doonga and houseboat moorings", W + "Jhelum_River"))
add("K7-20", ("Guwahati", CE, "Assam's chief city, with surviving Assam-type houses", W + "Guwahati"))
add("K8-3", ("Liangjiahe", CE, "Yaodong village, Yanchuan County, Shaanxi, where Xi Jinping lived 1969–75", W + "Liangjiahe"),
    ("Sanmenxia", CE, "Henan city of sunken-courtyard (dikengyuan) yaodong villages", W + "Sanmenxia"))
add("K8-9", ("Shikumen Open House Museum", "Shikumen neighbourhoods and buildings", "Furnished 1920s shikumen house museum, Xintiandi, Shanghai", W + "Shikumen_Open_House_Museum"))
add("K9-10", ("Siwaluh Jabu", ST, "Karo Batak longhouse for eight families", W + "Siwaluh_Jabu"))
add("K9-11", ("Torogan", ST, "Maranao royal house on stilts, Lanao, related Filipino stilt-house tradition", W + "Torogan"))
add("K9-13", ("Shophouse", ST, "Two-storey shop-house with five-foot way, the basic Sino-Portuguese building", W + "Shophouse"),
     ("George Town, Penang", CE, "Straits port with Sino-Portuguese shophouses · UNESCO (Melaka and George Town)", W + "George_Town,_Penang"),
     ("Malacca City", CE, "Straits port with Peranakan shophouses · UNESCO (Melaka and George Town)", W + "Malacca_City"),
     ("Phuket Old Town", CE, "Sino-Portuguese shophouses of Thalang and Dibuk roads, Phuket, Thailand", W + "Phuket_Old_Town"),
     ("Cheong Fatt Tze Mansion", "Sino-Portuguese buildings", "Blue Mansion, courtyard house of a Hakka magnate, George Town, Penang, 1904", W + "Cheong_Fatt_Tze_Mansion"),
     ("Baba House", "Sino-Portuguese buildings", "Peranakan terrace house of the 1890s, Neil Road, Singapore; museum", W + "Baba_House"))
add("K9-14", ("Istana Jahar", "Malay houses and palaces", "Timber-and-brick royal palace, Kota Bharu, Kelantan, 1887; museum", W + "Istana_Jahar"),
     ("Kampung Morten", CE, "Malay village of traditional timber houses, Malacca City", W + "Kampung_Morten"))
add("K10-7", ("Ancient Kano City Walls", "Hausa palaces and mosques", "Earthen city walls and gates of Kano, Nigeria, from the 11th century", W + "Ancient_Kano_City_Walls"),
     ("Kurmi Market", "Hausa palaces and mosques", "Market of Kano, Nigeria, founded in the 15th century", W + "Kurmi_Market"))
add("K12-2", ("Samoa", CE, "Islands where the fale is still the main village building", W + "Samoa"),
     ("Falekaupule", ST, "Tuvaluan meeting house, the counterpart of the fale fono", W + "Falekaupule"))
add("K12-3", ("Tarawa", CE, "Kiribati atoll and capital, with village and parliament maneaba", W + "Tarawa"),
     ("Falekaupule", ST, "Tuvaluan meeting house, the Polynesian counterpart of the maneaba", W + "Falekaupule"))
add("K12-4", ("Abelam people", SS, "Abelam style: Sepik people who build painted tambaran houses with towering gables, Maprik area", W + "Abelam_people"),
     ("Iatmul people", SS, "Iatmul style: middle Sepik people whose men's houses (ngego) are carved spirit houses", W + "Iatmul_people"))
add("K12-6", ("Pohnpei", CE, "Island of the Saudeleur state, Nan Madol on its eastern reef", W + "Pohnpei"),
     ("Saudeleur dynasty", SS, "Centralised dynasty of Pohnpei, c. 1100–1628, builders of Nan Madol", W + "Saudeleur_dynasty"))
add("K12-10", ("Architecture of Albania", SS, "Albanian architecture, incl. the stone kulla tower houses", W + "Architecture_of_Albania"),
     ("Junik", CE, "Kosovo village with a dense group of kulla tower houses", W + "Junik"),
     ("Deçan", CE, "Kosovo town with kulla houses of the Dukagjini plain", W + "Deçan"),
     ("Gjakova", CE, "Kosovo town with kulla houses and an Ottoman bazaar", W + "Gjakova"))
add("K12-11", ("Ingush towers", SS, "Battle and residential towers of Ingushetia", W + "Ingush_towers"),
     ("Khamkhi", "Vainakh towers", "Tower village, Dzheyrakhsky District, Ingushetia", W + "Khamkhi"),
     ("Targim", "Vainakh towers", "Tower settlement, Dzheyrakhsky District, Ingushetia", W + "Targim"),
     ("Itum-Kale", CE, "Chechen mountain district of medieval tower settlements", W + "Itum-Kale"))
add("K12-16", ("Chalet", ST, "Alpine timber house with low pitched roof and broad eaves", W + "Chalet"),
     ("Bernese Oberland", CE, "Region of large timbered farmhouses (Frutighaus, Simmental house)", W + "Bernese_Oberland"),
     ("Appenzell", CE, "Region of Appenzell houses with joined house and barn", W + "Appenzell"))
add("K12-17", ("Colombage", ST, "French timber framing (half-timbering), Normandy, Alsace, Champagne", W + "Colombage"),
     ("Village des Bories", CE, "Restored dry-stone hamlet, Gordes, Vaucluse", W + "Village_des_Bories"),
     ("Écomusée d'Alsace", CE, "Open-air museum of Alsatian timber-framed houses, Ungersheim", W + "%C3%89comus%C3%A9e_d%27Alsace"))
add("K12-19", ("Barbados", CE, "Island of the chattel house, built on rented plantation land after emancipation", W + "Barbados"))
add("K14-3", ("Saikei", ST, "Japanese planted tray landscape, kin to hòn non bộ", W + "Saikei"))
add("K12-5", ("Rapa Nui ahu", SS, "Stone platforms carrying moai, Easter Island, c. 1250–1600 · UNESCO (Rapa Nui)", "Rapa Nui (ahu / moai)"),
     ("Tongan langi and trilithon", SS, "Royal terraced tombs (langi) and the Haʻamonga trilithon, Tongatapu", "Tongan megalithic (langi / trilithon)"))
