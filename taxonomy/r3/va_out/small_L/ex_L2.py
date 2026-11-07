from xh import *
E, X = {}, {}
D = ("dup",)
def drop(r): return ("drop", r)
LBL = drop("tradition bucket label from the gathered data; its sites are expanded in the catalogue")
AX = "Sub-types and phases first, then the sites catalogue sectioned by region, phase or site type, then collections and named painters."
FOLK = "Sub-types first, then centres and communities, then named painters."

E["L2-1"] = dict(axis=AX, catalogues=[UN(327, "Quseir Amra"), ARCHNET, WP("Qusayr 'Amra", "site article")],
    kinds=[W("Bath-house fresco cycles", "Sub-types", "hunting, bathing, crafts and the Six Kings painted on the vaults of a desert bath", "Qusayr 'Amra"),
           W("Zodiac dome", "Sub-types", "the earliest surviving depiction of the night sky on a dome, Qusayr 'Amra caldarium", "Qusayr 'Amra")],
    knowledge_sites=[W("Qasr al-Hayr al-Gharbi", "Umayyad desert palaces", "Homs desert, Syria; c. 727; painted floors now in the National Museum of Damascus"),
                     W("Hisham's Palace", "Umayyad desert palaces", "Jericho; c. 740s; Khirbat al-Mafjar, painted plaster and the Tree of Life mosaic")])

E["L2-2"] = dict(axis=AX, catalogues=[ARCHNET, IAH, UN(1422, "Golestan Palace"), MET("Qajar wall painting", "detached Qajar and Safavid wall paintings in the Met")],
    knowledge_sites=[W("Ali Qapu", "Safavid palaces and pavilions", "Isfahan; c. 1600; palace with figural murals and the music-room stucco"),
                     W("Hasht Behesht", "Safavid palaces and pavilions", "Isfahan; 1669; pavilion with painted figural and floral decoration"),
                     W("Golestan Palace", "Qajar palaces", "Tehran; Qajar royal palace with figural murals and mirror halls; UNESCO World Heritage Site")])

E["L2-3"] = dict(axis=FOLK, catalogues=[ICH, WP("Al-Qatt Al-Asiri", "tradition article"), COM("Al-Qatt Al-Asiri")],
    kinds=[W("Interior wall decoration (nagash)", "Sub-types", "geometric bands painted by women in reception rooms of Asir houses", "Al-Qatt Al-Asiri"),
           W("Rijal Almaa", "Centres & workshops", "Asir, Saudi Arabia; heritage village of painted stone houses"),
           W("Abha", "Centres & workshops", "Asir capital; centre of the revival of al-qatt painting"),
           MS("Fatima Abou Gahas", "Makers", "Asiri painter (1920-2010), best-known master of al-qatt")])

E["L2-4"] = dict(axis=AX, catalogues=[UN(242, "Ajanta Caves"), HUNT, WP("Ajanta Caves", "site article with cave-by-cave list")],
    kinds=[W("Satavahana phase", "Schools & phases", "2nd-1st century BC paintings of Caves 9 and 10", "Ajanta Caves"),
           W("Vakataka phase", "Schools & phases", "late 5th century AD: the great Jataka cycles of Caves 1, 2, 16 and 17", "Ajanta Caves"),
           W("Padmapani and Vajrapani (Ajanta Cave 1)", "Ajanta Caves", "Ajanta, c. 475-480; the bodhisattva pair flanking the shrine antechamber", "Ajanta Caves")],
    knowledge_sites=[W("Bagh Caves", "Related Indian cave-temple murals", "Dhar, Madhya Pradesh; 5th-6th c. Buddhist cave murals"),
                     W("Badami cave temples", "Related Indian cave-temple murals", "Karnataka; 6th c.; fragments of Chalukya painting in Cave 3"),
                     W("Sittanavasal Cave", "Related Indian cave-temple murals", "Pudukkottai, Tamil Nadu; Jain cave with lotus-pond ceiling murals")])
X[("L2-4", "Ajanta")] = drop("duplicate of the Ajanta Caves site row")
X[("L2-4", "Early Indian cave-temple murals (Bagh, Ellora, Badami, Sittanavasal)")] = LBL
X[("L2-4", "John Griffiths")] = ("Copyists", "Bombay School of Art principal who copied the Ajanta murals 1872-1885 (copies in the V&A)", None, 1)

E["L2-5"] = dict(axis=AX, catalogues=[UN(202, "Ancient City of Sigiriya"), WP("Sigiriya", "site article"), HUNT],
    kinds=[W("Sigiriya maidens", "Sub-types", "half-length female figures (apsaras or queens) in a rock pocket, late 5th century", "Sigiriya"),
           W("Mirror Wall graffiti", "Sub-types", "Sinhala verses left by visitors 8th-10th century praising the paintings", "Sigiriya"),
           W("Kashyapa I period", "Schools & phases", "paintings of the palace-fortress of Kashyapa I (r. 477-495)", "Kashyapa I of Anuradhapura")])

E["L2-6"] = dict(axis=AX, catalogues=[WP("Kerala mural painting", "tradition article"), COM("Kerala mural painting")],
    kinds=[W("Panchavarna technique", "Sub-types", "five-colour natural pigments on lime plaster, 16th-19th century", "Kerala mural painting"),
           W("Guruvayur Institute of Mural Painting", "Centres & workshops", "Guruvayur Devaswom school reviving the tradition since 1989", "Guruvayur Temple")])

E["L2-7"] = dict(axis=AX, catalogues=[UN(561, "Golden Temple of Dambulla"), WP("Dambulla cave temple", "site article"), COM("Degaldoruwa")],
    knowledge_sites=[W("Degaldoruwa Raja Maha Vihara", "Kandyan temple sites", "Kandy; 1771; cave temple with the finest Kandyan jataka paintings"),
                     W("Ridi Viharaya", "Kandyan temple sites", "Kurunegala; temple with Kandyan-period murals and Dutch tiles"),
                     W("Temple of the Tooth", "Kandyan temple sites", "Kandy; royal temple with Kandyan-period paintings; UNESCO (Sacred City of Kandy)")])

E["L2-8"] = dict(axis=AX, catalogues=[WP("Shekhawati", "region article on the painted havelis"), COM("Shekhawati haveli frescoes")],
    knowledge_sites=[W("Mandawa", "Painted havelis and palaces", "Jhunjhunu district, Rajasthan; town of painted Marwari havelis, 18th-20th c."),
                     W("Nawalgarh", "Painted havelis and palaces", "Jhunjhunu district; painted havelis incl. Poddar and Morarka havelis"),
                     W("Fatehpur, Rajasthan", "Painted havelis and palaces", "Sikar district; havelis incl. the Nadine Le Prince haveli")])

E["L2-9"] = dict(axis=FOLK, catalogues=[SAHA, COM("Pithora painting")],
    kinds=[SR("Pithora wall painting", "Sub-types", "ritual horse-and-rider murals painted by lakhara painters for the deity Pithora", "Pithora painting"),
           W("Rathwa people", "Centres & workshops", "adivasi community of Chhota Udaipur whose houses carry Pithora paintings"),
           W("Chhota Udaipur", "Centres & workshops", "Gujarat; centre of Rathwa Pithora painting"),
           MS("Pema Fatya", "Makers", "Rathwa Pithora painter, Padma Shri 2017")])

E["L2-10"] = dict(axis=FOLK, catalogues=[SAHA, COM("Saura painting")],
    kinds=[SR("Idital (ittal) wall icons", "Sub-types", "white rice-paste figures on red earth walls, painted for the spirits", "Saura painting"),
           W("Saura people", "Centres & workshops", "adivasi people of southern Odisha who paint idital"),
           W("Rayagada district", "Centres & workshops", "Odisha; main area of Saura painting with Gajapati district")])

E["L2-11"] = dict(axis=FOLK, catalogues=[SAHA, COM("Sohrai painting")],
    kinds=[SR("Sohrai painting", "Sub-types", "harvest-festival wall painting of animals and plants in earth colours", "Sohrai painting"),
           SR("Khovar painting", "Sub-types", "marriage-season comb-cut murals, black over white clay", "Khovar painting"),
           W("Hazaribagh", "Centres & workshops", "Jharkhand; centre of Sohrai-Khovar painting (GI tag 2020)")])

E["L2-12"] = dict(axis=FOLK, catalogues=[SAHA, WP("Rangoli", "tradition article with regional names"), COM("Rangoli")],
    kinds=[W("Mandana", "Sub-types", "Rajasthan and Madhya Pradesh: white geometric floor and wall drawings on red earth", "Mandana painting"),
           SR("Aripan", "Sub-types", "Mithila (Bihar) floor painting in rice paste", "Aripan")])
X[("L2-12", "Alpana")] = ("Sub-types", "Bengal: rice-paste floor painting for festivals")
X[("L2-12", "Kolam")] = ("Sub-types", "Tamil Nadu: rice-flour line and dot patterns drawn daily at thresholds")
X[("L2-12", "Kalamezhuthu")] = ("Sub-types", "Kerala: ritual floor drawings of deities in coloured powders")

E["L2-13"] = dict(axis=AX, catalogues=[HAR, HUNT, COM("Tibetan Buddhist murals")],
    kinds=[W("Kashmiri-influenced Western Himalayan style", "Schools & phases", "10th-13th c. murals of Tabo and Alchi", "Alchi Monastery"),
           W("Newar-influenced Central Tibetan style", "Schools & phases", "13th-15th c. murals of Shalu and Gyantse", "Shalu Monastery"),
           SR("Menri school", "Schools & phases", "15th c. onward style founded by Menla Döndrub", "Menri painting style")],
    knowledge_sites=[W("Tsaparang", "Western Tibet (Guge)", "Ngari; Guge kingdom capital with 15th-16th c. temple murals"),
                     W("Tholing Monastery", "Western Tibet (Guge)", "Ngari; founded 996 by Rinchen Zangpo; murals of the White and Red temples"),
                     W("Palcho Monastery", "Central Tibet (Ü-Tsang)", "Gyantse; 15th c. Kumbum stupa with tens of thousands of painted figures"),
                     W("Lukhang", "Central Tibet (Ü-Tsang)", "Lhasa; 17th-18th c. temple with yogic and tantric murals"),
                     W("Samye", "Central Tibet (Ü-Tsang)", "Dranang; first Tibetan monastery, with later murals"),
                     MS("Menla Döndrub", "Makers", "Tibetan painter (b. 1440), founder of the Menri style", "Menla Dondrub")])
for n in ("Western Himalayan Buddhist murals (Alchi, Tabo, Guge)", "Nepalese and Bhutanese wall painting"): X[("L2-13", n)] = LBL
for n in ("Alchi", "Tabo", "Shalu"): X[("L2-13", n)] = D

E["L2-14"] = dict(axis=AX, catalogues=[UN(440, "Mogao Caves"), IDP, ["https://www.e-dunhuang.com/", "Digital Dunhuang", "Dunhuang Academy digitisation of the Mogao caves"]],
    kinds=[W("Northern Liang to Western Wei caves", "Schools & phases", "5th-6th c.: jataka friezes and Thousand Buddha walls", "Mogao Caves"),
           W("Sui and Tang caves", "Schools & phases", "581-907: Pure Land paradise tableaux and donor portraits", "Mogao Caves"),
           W("Five Dynasties, Song, Western Xia and Yuan caves", "Schools & phases", "10th-14th c.: Cao family donor caves and esoteric mandalas", "Mogao Caves")],
    knowledge_sites=[W("Western Thousand Buddha Caves", "Dunhuang cave complexes", "Dunhuang, Gansu; 22 caves with murals from Northern Wei to Yuan")])
X[("L2-14", "Mogao Caves")] = D
X[("L2-14", "Yulin Caves")] = D

E["L2-15"] = dict(axis=AX, catalogues=[UN(1442, "Silk Roads: the Routes Network of Chang'an-Tianshan Corridor (incl. Kizil)"), IDP, WP("Kizil Caves", "site article")],
    kinds=[W("First Indo-Iranian style", "Schools & phases", "Grünwedel's earlier Kucha style, softer modelling, c. 4th-5th c.", "Kizil Caves"),
           W("Second Indo-Iranian style", "Schools & phases", "lapis-blue and green style with diamond-shaped landscape lozenges, c. 6th-7th c.", "Kizil Caves")],
    knowledge_sites=[SR("Kumtura Caves", "Kucha cave temples", "Kuqa, Xinjiang; c. 100 caves with Kuchean and Tang-style murals"),
                     SR("Kizilgaha Caves", "Kucha cave temples", "Kuqa, Xinjiang; cave temples near the Kizilgaha beacon tower"),
                     SR("Simsim Caves", "Kucha cave temples", "Kuqa, Xinjiang; Buddhist caves with Kuchean murals")],
    pre=["Sub-types", "Schools & phases", "Centres & workshops"])
X[("L2-15", "Kumtura")] = D
X[("L2-15", "Mingoi")] = drop("ambiguous name (ming-oi, 'thousand houses', is applied to several Kucha cave groups)")
X[("L2-15", "Kucha / northern Tarim")] = LBL

E["L2-16"] = dict(axis=AX, catalogues=[IDP, WP("Bezeklik Thousand Buddha Caves", "site article"), COM("Bezeklik murals")],
    kinds=[W("Uyghur praṇidhi (vow) scenes", "Sub-types", "large panels of the Buddha's past vows with donor princes, 9th-13th c.", "Bezeklik Thousand Buddha Caves"),
           SR("Museum für Asiatische Kunst, Berlin", "Collections", "holds the Bezeklik murals removed by Albert von Le Coq in 1905-06", "Museum für Asiatische Kunst")],
    knowledge_sites=[W("Gaochang", "Turfan cave temples", "Turpan; Qocho, Uyghur capital whose temples yielded painted banners and murals"),
                     SR("Toyuq Caves", "Turfan cave temples", "Turpan; early Buddhist caves of the Gaochang kingdom", "Tuyoq caves")])
X[("L2-16", "Qocho (Karakhoja)")] = D
X[("L2-16", "Uyghur (Turfan, Qocho)")] = LBL

E["L2-17"] = dict(axis=AX, catalogues=[UN(603, "Samarkand: Crossroad of Cultures (incl. Afrasiyab)"), WP("Panjakent", "site article"), COM("Sogdian wall painting")],
    kinds=[SR("Ambassadors' Painting (Afrasiyab, c. 660)", "Sogdian sites", "Hall of the Ambassadors, Afrasiyab, Samarkand; Afrasiyab Museum", "Afrasiyab murals"),
           SR("Hermitage Museum", "Collections", "holds the largest group of detached Panjakent and Varakhsha murals", "Hermitage Museum")],
    knowledge_sites=[W("Varakhsha", "Sogdian sites", "Bukhara oasis; palace with murals of elephant-riders fighting beasts, 7th-8th c."),
                     W("Bamyan", "Bactrian comparanda", "Afghanistan; cave murals of the Bamiyan Buddhas; UNESCO World Heritage Site", "Buddhas of Bamiyan")])
X[("L2-17", "Panjikent")] = D
X[("L2-17", "Bamiyan")] = drop("replaced by the Bamyan site row with a source")

E["L2-18"] = dict(axis=AX, catalogues=[UN(1588, "Bagan"), WP("Bagan", "site article"), COM("Bagan murals")],
    knowledge_sites=[W("Gubyaukgyi Temple (Myinkaba)", "Bagan temples", "Myinkaba, Bagan; 1113; jataka murals with Old Mon captions"),
                     W("Abeyadana Temple", "Bagan temples", "Myinkaba; late 11th c.; Mahayana and Hindu deities painted inside"),
                     W("Sulamani Temple", "Bagan temples", "Bagan; 1183; later Konbaung-era murals over earlier painting"),
                     W("Payathonzu Temple", "Bagan temples", "Minnanthu; 13th c.; Mahayana-tantric murals")])
X[("L2-18", "Ananda Temple")] = D
X[("L2-18", "Burmese temple murals (Konbaung, Ava, Sagaing)")] = LBL

E["L2-19"] = dict(axis=AX, catalogues=[WP("Thai art", "survey article"), COM("Thai temple murals")],
    kinds=[MS("Khrua In Khong", "Makers", "Thai monk-painter of the Rama IV era who introduced Western perspective (Wat Bowonniwet)")],
    knowledge_sites=[W("Wat Suthat", "Rattanakosin (Bangkok) murals", "Bangkok; early 19th c. vihara murals of the Buddha's lives"),
                     W("Wat Bowonniwet Vihara", "Rattanakosin (Bangkok) murals", "Bangkok; ubosot murals by Khrua In Khong, 1850s-60s"),
                     SR("Buddhaisawan Chapel", "Rattanakosin (Bangkok) murals", "Bangkok National Museum; 1795; Life of the Buddha murals")])
X[("L2-19", "Lanna")] = ("Sub-types", "Lanna and Nan mural style of northern Thailand, 19th century (Wat Phumin, Wat Luang Wiang Ta Mon)", "Lanna mural style")

E["L2-20"] = dict(axis=AX, catalogues=[WP("Yongle Palace", "site article"), COM("Yongle Palace murals"), MET("Chinese wall painting", "detached Yuan and Ming temple murals")],
    kinds=[W("Daoist pantheon procession (Chaoyuan tu)", "Sub-types", "Hall of the Three Purities: 286 deities in audience, 1325", "Yongle Palace"),
           SR("Royal Ontario Museum", "Collections", "Toronto; Yuan temple murals from Xinghua Si and the Daoist 'Homage to the Highest Power'", "Royal Ontario Museum Chinese murals"),
           SR("Zhu Haogu", "Makers", "Yuan muralist of the Hall of the Three Purities, Yongle Palace", "Yongle Palace", 1),
           SR("Ma Junxiang", "Makers", "Yuan muralist of the Hall of Chunyang, Yongle Palace", "Yongle Palace", 1)],
    knowledge_sites=[SR("Pilu Temple", "Ming Buddhist temple murals", "Shijiazhuang, Hebei; Ming water-land ritual murals", "Pilu Temple Shijiazhuang")])
X[("L2-20", "Fahai Temple murals")] = D

E["L2-21"] = dict(axis=AX, catalogues=[BUNKA, WP("Takamatsuzuka Tomb", "site article"), COM("Takamatsuzuka Tomb mural")],
    kinds=[W("Four Gods and constellations", "Sub-types", "Asuka tomb murals of the Four Symbols and star charts, c. 700", "Kitora Tomb")],
    knowledge_sites=[SR("Takehara Kofun", "Decorated tombs of Kyushu (comparanda)", "Miyawaka, Fukuoka; 6th c. painted chamber with horse and dragon", "Takehara Kofun"),
                     SR("Mezurashizuka Kofun", "Decorated tombs of Kyushu (comparanda)", "Ukiha, Fukuoka; painted chamber with boat and archer", "Mezurashizuka Kofun")])
X[("L2-21", "Kitora Tomb")] = D
X[("L2-21", "Hōryū-ji Golden Hall murals")] = D

E["L2-22"] = dict(axis=AX, catalogues=[UN(1091, "Complex of Koguryo Tombs"), UN(1135, "Capital Cities and Tombs of the Ancient Koguryo Kingdom"), COM("Goguryeo tomb murals")],
    kinds=[W("Portrait and daily-life tombs", "Schools & phases", "4th-5th c.: tomb owner portraits, processions and banquets (Anak Tomb No. 3)", "Anak Tomb No. 3"),
           W("Four Guardians tombs", "Schools & phases", "6th-7th c.: walls given to the Four Symbols (Gangseo Great Tomb)", "Goguryeo tombs")],
    knowledge_sites=[W("Anak Tomb No. 3", "Goguryeo tombs", "South Hwanghae; 357; earliest dated Goguryeo mural tomb"),
                     SR("Muyongchong (Tomb of the Dancers)", "Goguryeo tombs", "Ji'an, Jilin; 5th c.; dancers and hunting scenes", "Muyongchong"),
                     SR("Gangseo Great Tomb", "Goguryeo tombs", "Nampo; 7th c.; Four Guardian murals", "Gangseo tombs"),
                     SR("Deokheung-ri Tomb", "Goguryeo tombs", "Nampo; 408; inscribed mural tomb", "Deokheung-ri tomb")])

E["L2-23"] = dict(axis=FOLK, catalogues=[WP("Dancheong", "tradition article"), COM("Dancheong")],
    kinds=[SR("Geum-dancheong", "Sub-types", "the richest scheme, all surfaces covered, for main halls of palaces and temples", "Dancheong"),
           SR("Moru-dancheong", "Sub-types", "patterns only at beam ends, with plain centres", "Dancheong"),
           SR("Gachil-dancheong", "Sub-types", "single-colour ground coat with simple lines, for secondary buildings", "Dancheong"),
           W("Gyeongbokgung", "Centres & workshops", "Seoul; Joseon palace, the reference set of palace dancheong"),
           W("Bulguksa", "Centres & workshops", "Gyeongju; temple with Buddhist dancheong; UNESCO World Heritage Site")])

E["L2-24"] = dict(axis=AX, catalogues=[UN(18, "Rock-Hewn Churches, Lalibela"), COM("Ethiopian church murals"), WP("Ethiopian art", "survey article")],
    kinds=[W("First and Second Gondarine styles", "Schools & phases", "17th-18th c. court style: large-eyed figures on painted canvas walls", "Ethiopian art")],
    knowledge_sites=[SR("Ura Kidane Mehret", "Painted churches", "Zege Peninsula, Lake Tana; 16th c. church with 18th-19th c. murals", "Ura Kidane Mehret"),
                     W("Abuna Yemata Guh", "Painted churches", "Tigray; cliff church with 15th c. murals of the apostles"),
                     SR("Narga Selassie", "Painted churches", "Dek Island, Lake Tana; 18th c. church painted for Empress Mentewab", "Narga Selassie")])
X[("L2-24", "Debre Berhan Selassie")] = D

E["L2-25"] = dict(axis=FOLK, catalogues=[WP("Litema", "tradition article"), COM("Litema")],
    kinds=[W("Engraved litema", "Sub-types", "patterns combed or incised in wet mud plaster", "Litema"),
           W("Painted litema", "Sub-types", "geometric and floral designs painted in earth pigments", "Litema"),
           W("Basotho people", "Centres & workshops", "Sesotho-speaking people of Lesotho and the Free State whose women make litema"),
           W("Free State (province)", "Centres & workshops", "eastern Free State: main area of litema homesteads")])
X[("L2-25", "Litema and Sotho / Ndebele house painting")] = LBL

E["L2-26"] = dict(axis=FOLK, catalogues=[WP("Southern Ndebele people", "people article with house-painting section"), COM("Ndebele house painting")],
    kinds=[W("Geometric house painting", "Sub-types", "bold black-outlined geometric façades painted by women", "Southern Ndebele people"),
           W("KwaNdebele", "Centres & workshops", "former homeland, Mpumalanga; the main area of painted homesteads"),
           M("Esther Mahlangu", "Makers", "Ndebele painter (b. 1935) who carried the style to canvas and the BMW Art Car"),
           MS("Francina Ndimande", "Makers", "Ndebele house painter (b. 1940) of KwaNdebele")])

E["L2-27"] = dict(axis=FOLK, catalogues=[WP("Imigongo", "tradition article"), COM("Imigongo")],
    kinds=[W("Cow-dung relief panels", "Sub-types", "raised geometric ridges of dung and ash painted black, white and red", "Imigongo"),
           SR("Kingdom of Gisaka", "Centres & workshops", "eastern Rwanda; origin of imigongo, attributed to Prince Kakira", "Gisaka"),
           W("Kirehe District", "Centres & workshops", "eastern Rwanda; Nyakarambi cooperatives that revived imigongo after 1994")])
X[("L2-27", "Rwandan agaseke and imigongo")] = LBL

E["L2-28"] = dict(axis=AX, catalogues=[["https://thebanmappingproject.com/", "Theban Mapping Project", "atlas of every tomb in the Theban necropolis"], ["https://www.osirisnet.net/", "OsirisNet", "tomb-by-tomb photographic documentation of Egyptian painted tombs"], UN(87, "Ancient Thebes with its Necropolis")],
    kinds=[W("Theban Necropolis", "Centres & workshops", "Luxor west bank: Valley of the Kings, Valley of the Queens and the Tombs of the Nobles"),
           W("Deir el-Medina", "Centres & workshops", "Luxor; village of the royal tomb painters and their own painted tombs"),
           W("British Museum", "Collections", "London; holds the Nebamun tomb paintings (c. 1350 BC)")],
    knowledge_sites=[W("KV17", "New Kingdom Thebes and Abydos", "Valley of the Kings; tomb of Seti I, the longest and most fully painted royal tomb"),
                     W("TT1", "New Kingdom Thebes and Abydos", "Deir el-Medina; tomb of Sennedjem with the Fields of Iaru, 19th Dynasty")])
X[("L2-28", "Theban tombs")] = D

E["L2-29"] = dict(axis=AX, catalogues=[WP("Minoan art", "survey article"), COM("Minoan frescoes"), WP("Akrotiri (prehistoric city)", "site article")])
X[("L2-29", "Akrotiri (Thera)")] = D

E["L2-30"] = dict(axis=AX, catalogues=[UN(1158, "Etruscan Necropolises of Cerveteri and Tarquinia"), WP("Monterozzi necropolis", "Tarquinia painted tombs article"), COM("Etruscan tomb painting")],
    knowledge_sites=[W("Tomb of Orcus", "Painted tombs of Tarquinia and Cerveteri", "Tarquinia; 4th c. BC; Velcha family, underworld and Velia portrait"),
                     W("François Tomb", "Painted tombs of Tarquinia and Cerveteri", "Vulci; 4th c. BC; Trojan prisoners and Mastarna; paintings in Villa Albani, Rome"),
                     SR("Tomb of the Triclinium", "Painted tombs of Tarquinia and Cerveteri", "Tarquinia; c. 470 BC; banqueters and dancers", "Tomb of the Triclinium"),
                     SR("Tomb of Hunting and Fishing", "Painted tombs of Tarquinia and Cerveteri", "Tarquinia; c. 520 BC; seascape with fishermen and divers", "Tomb of Hunting and Fishing")])

GR = "Greek painters recorded by Pliny and Pausanias"
E["L2-31"] = dict(axis="Painted tombs by region (Macedonia, Thrace, Paestum), then the named Greek painters known from literary sources, by period and school.",
    catalogues=[UN(44, "Thracian Tomb of Kazanlak"), UN(780, "Archaeological Site of Aigai (Vergina)"), UN(359, "Thracian Tomb of Sveshtari"), WP("Ancient Greek painting", "survey article")],
    knowledge_sites=[W("Vergina", "Macedonian tombs", "Aigai, Imathia; royal tombs incl. Tomb II and the Tomb of Persephone, 4th c. BC; UNESCO")])
for n in ("Macedonian tombs (Vergina)", "Thracian tombs (Kazanlak, Sveshtari)"): X[("L2-31", n)] = D
X[("L2-31", "Paestum and Lucanian tomb painting")] = LBL
GRP = {"Archaic painters": "Aridices|Damophilus|Gorgasus|Milonidas|Taleides|Aregon|Eumares|Cimon of Cleonae|Aglaophon|Timagoras of Chalcis",
       "Classical painters of the 5th century": "Polygnotus of Thasos|Aglaophon the Younger of Thasos|Aristophon|Panaenus|Agatharchus|Apollodorus|Zeuxis|Parrhasius|Evenor|Timanthes|Androcydes|Dionysius of Colophon|Cydias|Pyrrho",
       "Sicyonian school": "Eupompus|Pamphilus of Amphipolis|Pausias|Nealces of Sikyon|Timanthes of Sicyon",
       "Theban-Attic school": "Aristidis of Thebes II|Nicomachus of Thebes|Philoxenus of Eretria|Nicias|Ariston",
       "Ionian and Hellenistic court painters": "Apelles|Protogenes|Antiphilus|Artemon|Heraclides|Pasias",
       "Women painters recorded by Pliny": "Timarete|Eirene|Calypso|Aristarete|Iaia|Helena of Egypt|Kora of Sicyon"}
for g, ns in GRP.items():
    for n in ns.split("|"): X[("L2-31", n)] = (g, "Greek painter known from Pliny, Pausanias and other ancient sources; no works survive")
for n in ("Famulus", "Gaius Fabius Pictor", "Pacuvius", "Quintus Pedius", "Cornelius Pinus", "Furius Dionysius Filocalus"):
    X[("L2-31", n)] = ("reloc", "L2-32", "Roman painters", "Roman painter recorded in ancient sources")

E["L2-32"] = dict(axis="Pompeian Styles first, then the sites catalogue by Vesuvian site, then Rome and the provinces, collections and the Roman painters named in the sources.",
    catalogues=[UN(829, "Archaeological Areas of Pompei, Herculaneum and Torre Annunziata"), ["https://pompeiiinpictures.com/", "Pompeii in Pictures", "house-by-house photographic record of Pompeii and its paintings"],
                ["https://pompeiisites.org/", "Parco Archeologico di Pompei", "official site with the houses of Pompeii and the Vesuvian villas"], WP("Pompeian Styles", "survey of the four styles")],
    kinds=[MS("Studius", "Roman painters", "Augustan painter credited by Pliny with landscape wall painting (also Ludius)", "Studius painter")])
X[("L2-32", "First Style")] = ("Schools & phases", "Masonry or Incrustation style, c. 200-80 BC: painted stucco imitating marble blocks")
X[("L2-32", "Second Style")] = ("Schools & phases", "Architectural style, c. 80-20 BC: illusionistic architecture and megalographies (Villa of the Mysteries)")
X[("L2-32", "Third Style")] = ("Schools & phases", "Ornate style, c. 20 BC-AD 40: flat monochrome walls with delicate candelabra and small panels")
X[("L2-32", "Fourth Style")] = ("Schools & phases", "Intricate style, c. AD 40-79: fantastic architecture and framed mythological panels")

E["L2-33"] = dict(axis=AX, catalogues=[WP("Catacombs of Rome", "list of the Roman catacombs"), WP("Dura-Europos synagogue", "the painted synagogue"), COM("Catacomb paintings Rome")],
    kinds=[W("Dura-Europos", "Centres & workshops", "Syria; garrison town with the painted synagogue, church and Mithraeum, before 256; paintings now in Damascus and Yale"),
           W("Yale University Art Gallery", "Collections", "New Haven; holds the Dura-Europos house-church and Mithraeum paintings")],
    knowledge_sites=[W("Catacomb of Priscilla", "Roman catacombs and Rome", "Via Salaria, Rome; 3rd c.; earliest image of the Virgin and Child"),
                     W("Catacomb of Callixtus", "Roman catacombs and Rome", "Via Appia, Rome; papal crypt and Sacrament chapels, 3rd c."),
                     W("Catacomb of Marcellinus and Peter", "Roman catacombs and Rome", "Via Labicana; 4th c. frescoes, agapes and Christ between Peter and Paul"),
                     SR("Via Latina Catacomb", "Roman catacombs and Rome", "Rome; 4th c. private hypogeum with Old Testament and pagan scenes", "Via Latina catacomb")])
X[("L2-33", "Dura-Europos")] = D
X[("L2-33", "mural - United States (ancient)")] = LBL

E["L2-34"] = dict(axis="Sites catalogue by school and region of the Byzantine commonwealth, roughly by date, then named painters.",
    catalogues=[UN(537, "Monasteries of Daphni, Hosios Loukas and Nea Moni of Chios"), UN(351, "Painted Churches in the Troodos Region"), UN(724, "Medieval Monuments in Kosovo"), PRINCETON,
                COM("Byzantine frescoes")],
    kinds=[M("Michael Astrapas and Eutychios", "Painters", "Thessalonian workshop, c. 1295-1320: Peribleptos Ohrid, Staro Nagoričane, Gračanica"),
           M("Manuel Panselinos", "Painters", "Thessalonian painter of the Protaton, Karyes, c. 1290"),
           M("Theophanes the Greek", "Painters", "Byzantine painter in Novgorod and Moscow, fl. 1370s-1405 (Church of the Transfiguration, Novgorod)"),
           M("Andrei Rublev", "Painters", "Muscovite painter, frescoes of the Dormition Cathedral, Vladimir (1408)"),
           M("Dionisius", "Painters", "Muscovite painter of the Ferapontov Monastery frescoes (1502)"),
           M("Theophanes the Cretan", "Painters", "post-Byzantine painter of the Meteora and Mount Athos (Great Lavra, 1535)"),
           M("Pârvu Mutu", "Painters", "Wallachian church painter (1657-1735), Brâncovenesc style")])
for n in ["Byzantine church painting (Greece, Anatolia)", "Mount Athos and Late Byzantine Macedonian school (Panselinos)", "Troödos painted churches (Cyprus)", "Cappadocian rock-cut church painting",
          "Macedonian (Ohrid) medieval fresco (Nerezi, Kurbinovo, St Sophia Ohrid)", "Serbian medieval fresco (Raška, Morava schools)", "Bulgarian medieval fresco (Boyana, Ivanovo)",
          "Kyivan Rus' fresco (St Sophia, Kyiv)", "Russian medieval church fresco (Novgorod, Vladimir, Theophanes, Rublev, Dionisius)", "Yaroslavl and Muscovite church painting (17th c.)"]:
    X[("L2-34", n)] = LBL

E["L2-35"] = dict(axis=AX, catalogues=[WP("Faras", "site article"), ["https://cyfrowe.mnw.art.pl/", "National Museum in Warsaw digital collection", "catalogue incl. the Faras Gallery paintings"]],
    kinds=[W("National Museum in Warsaw", "Collections", "Faras Gallery: c. 67 paintings from the cathedral, saved 1961-64"),
           W("Sudan National Museum", "Collections", "Khartoum; the other half of the Faras cathedral paintings")],
    knowledge_sites=[W("Old Dongola", "Other Makurian sites", "Northern State, Sudan; Makurian capital, church and monastery wall paintings"),
                     W("Banganarti", "Other Makurian sites", "near Old Dongola; pilgrimage church with royal portraits, 11th-14th c.")])
X[("L2-35", "Nubian Christian wall painting (Faras)")] = LBL

E["L2-36"] = dict(axis=AX, catalogues=[WP("Maya art", "survey article"), COM("Maya murals")],
    knowledge_sites=[W("Calakmul", "Maya painted sites", "Campeche; Chiik Nahb acropolis murals of market life, c. 620-700; UNESCO"),
                     W("Xultun", "Maya painted sites", "Petén, Guatemala; 9th c. painted room with astronomical tables"),
                     W("Tulum", "Maya painted sites", "Quintana Roo; Postclassic Temple of the Frescoes")])
X[("L2-36", "Murals of Bonampak")] = LBL
X[("L2-36", "San Bartolo")] = D
X[("L2-36", "Calakmul")] = D

E["L2-37"] = dict(axis=AX, catalogues=[UN(414, "Pre-Hispanic City of Teotihuacan"), WP("Teotihuacan", "site article"), COM("Teotihuacan murals")],
    kinds=[W("Great Goddess of Teotihuacan", "Sub-types", "frontal deity with nose-pendant and streams, Tepantitla and Tetitla", "Teotihuacan Spider Woman")],
    knowledge_sites=[SR("Tepantitla", "Teotihuacan", "apartment compound with the 'Tlalocan' paradise mural, c. 550", "Tepantitla"),
                     SR("Tetitla", "Teotihuacan", "apartment compound with over 120 mural fragments", "Tetitla"),
                     SR("Atetelco", "Teotihuacan", "apartment compound with warrior and coyote murals", "Atetelco")])
X[("L2-37", "Tepantitla")] = D
X[("L2-37", "Tetitla")] = D

E["L2-38"] = dict(axis=AX, catalogues=[WP("Cacaxtla", "site article"), COM("Cacaxtla murals")],
    kinds=[W("Battle Mural (Cacaxtla, c. 650-700)", "Epiclassic sites", "Building B: jaguar warriors defeating bird-costumed warriors", "Cacaxtla"),
           W("Bird Man and Jaguar Man (Cacaxtla Building A)", "Epiclassic sites", "door-jamb figures in Maya-influenced style", "Cacaxtla"),
           W("Red Temple murals (Cacaxtla)", "Epiclassic sites", "maize, cacao and the old merchant god", "Cacaxtla")])

E["L2-39"] = dict(axis=AX, catalogues=[WP("Moche culture", "culture article"), COM("Huaca de la Luna murals")],
    knowledge_sites=[W("El Brujo", "Moche huacas", "Chicama Valley; Huaca Cao Viejo with painted reliefs and the Lady of Cao"),
                     SR("Pañamarca", "Moche huacas", "Nepeña Valley; southern Moche centre with polychrome murals", "Pañamarca"),
                     SR("Huaca Ventarrón", "Moche huacas", "Lambayeque; pre-Moche temple with c. 4,000-year-old murals", "Huaca Ventarrón")])
X[("L2-39", "Andean pre-Columbian mural painting (Moche, Lambayeque)")] = LBL

E["L2-40"] = dict(axis="Murals by phase (first SEP and San Ildefonso murals, mature phase, late muralism), then muralists by generation; independents last.",
    catalogues=[UN(1250, "Central University City Campus of UNAM"), UN(815, "Hospicio Cabañas, Guadalajara"), WP("Mexican muralism", "movement article"), COM("Mexican murals")],
    kinds=[M("Gerardo Murillo (Dr. Atl)", "Precursors", "painter and theorist (1875-1964) who promoted public murals before 1921", "Dr. Atl"),
           M("Diego Rivera", "Los Tres Grandes", "(1886-1957) Secretaría de Educación Pública, Palacio Nacional, Detroit Industry Murals"),
           M("José Clemente Orozco", "Los Tres Grandes", "(1883-1949) San Ildefonso, Hospicio Cabañas, Dartmouth"),
           M("David Alfaro Siqueiros", "Los Tres Grandes", "(1896-1974) Polyforum, Chapultepec, Retrato de la burguesía"),
           M("Fernando Leal", "First generation (San Ildefonso and SEP)", "(1896-1964) Fiesta of the Lord of Chalma, San Ildefonso 1922"),
           M("Jean Charlot", "First generation (San Ildefonso and SEP)", "(1898-1979) Massacre in the Templo Mayor, San Ildefonso 1922"),
           M("Roberto Montenegro", "First generation (San Ildefonso and SEP)", "(1885-1968) murals at San Pedro y San Pablo, 1922"),
           M("Fermín Revueltas", "First generation (San Ildefonso and SEP)", "(1901-1935) Alegoría de la Virgen de Guadalupe, San Ildefonso"),
           M("Ramón Alva de la Canal", "First generation (San Ildefonso and SEP)", "(1892-1985) Landing of the Cross, San Ildefonso"),
           M("Xavier Guerrero", "First generation (San Ildefonso and SEP)", "(1896-1974) Rivera's assistant at Chapingo and the SEP"),
           M("Rufino Tamayo", "Second generation", "(1899-1991) murals at the Palacio de Bellas Artes and the National Museum of Anthropology"),
           M("Juan O'Gorman", "Second generation", "(1905-1982) mosaic library façade, UNAM; Chapultepec murals"),
           M("Pablo O'Higgins", "Second generation", "(1904-1983) Abelardo Rodríguez market murals"),
           M("Jorge González Camarena", "Second generation", "(1908-1980) Presencia de América Latina, Concepción, Chile"),
           M("José Chávez Morado", "Second generation", "(1909-2002) Guanajuato Alhóndiga murals; UNAM mosaics"),
           M("Aurora Reyes", "Second generation", "(1908-1985) first woman muralist of Mexico, Centro Escolar Revolución"),
           M("Alfredo Zalce", "Second generation", "(1908-2003) Morelia government palace murals"),
           M("Arnold Belkin", "Late muralism", "(1930-1992) Canadian-born muralist, Los hermanos Serdán")])
X[("L2-40", "Andrea Gómez")] = ("Second generation", "(1926-2012) muralist and printmaker of the Taller de Gráfica Popular")
X[("L2-40", "José Ignacio Bermúdez Vázquez")] = ("Late muralism", "Cuban-born muralist active in Mexico")

E["L2-41"] = dict(axis="Murals by phase (early, Popular Unity brigades, post-dictatorship), then brigades and muralists.",
    catalogues=[WP("Chilean muralism", "movement article") , COM("Chilean murals"), WP("Brigada Ramona Parra", "the principal mural brigade")],
    kinds=[M("Brigada Ramona Parra", "Brigades and muralists", "Communist Youth mural brigade founded 1968"),
           MS("Alejandro 'Mono' González", "Brigades and muralists", "(b. 1947) co-founder and lead designer of the Brigada Ramona Parra", "Mono González muralist"),
           MS("Julio Escámez", "Brigades and muralists", "(1925-2015) Historia de la medicina y la farmacia en Chile, Concepción", "Julio Escámez"),
           M("Roberto Matta", "Brigades and muralists", "painted El primer gol del pueblo chileno with the BRP, La Granja 1971")])

E["L2-42"] = dict(axis="Centres first, then muralists.", catalogues=[[surl("Murals of Revolutionary Nicaragua"), "Wikipedia search: Murals of Revolutionary Nicaragua", "articles on Sandinista-era murals (1979-1990)"], COM("Nicaragua murals Managua")],
    kinds=[SR("Escuela Nacional de Arte Público Monumental", "Centres & workshops", "Managua, 1985-1990; national school of public mural art", "Escuela Nacional de Arte Público Monumental Nicaragua"),
           SR("Parque Luis Alfonso Velásquez murals", "Centres & workshops", "Managua; children's park murals of the 1980s, largely painted over in 1990", "Parque Luis Alfonso Velásquez"),
           MS("Sergio Michilini", "Makers", "Italian muralist (b. 1948), director of the Managua public-art school, Santa María de los Ángeles church murals")])

E["L2-43"] = dict(axis=AX, catalogues=[["https://www.museunacional.cat/en", "Museu Nacional d'Art de Catalunya (MNAC)", "the main collection of detached Catalan Romanesque murals"], UN(988, "Catalan Romanesque Churches of the Vall de Boí"), POP, PRINCETON],
    kinds=[M("Master of Taüll", "Painters", "painter of the apse of Sant Climent de Taüll, 1123 (MNAC)"),
           MS("Master of Pedret", "Painters", "Catalan workshop of Sant Quirze de Pedret and Santa Maria d'Àneu, c. 1100", "Master of Pedret"),
           MS("Master of San Baudelio de Berlanga", "Painters", "painter of the Berlanga hermitage murals, c. 1125 (Prado, Met, Cincinnati)", "San Baudelio de Berlanga")])
for n in ("mural - United States (medieval)", "Catalan Romanesque wall painting (Taüll, Boí)", "Italian medieval wall painting"): X[("L2-43", n)] = LBL

E["L2-44"] = dict(axis=AX, catalogues=[POP, PRINCETON, ["https://medeltidensbildvarld.se/", "Medeltidens bildvärld", "database of Swedish medieval church paintings"], WP("Albertus Pictor", "the Swedish church painter")],
    kinds=[W("Dance of Death murals", "Sub-types", "Danse macabre friezes: La Chaise-Dieu, Hrastovlje, Beram", "Danse Macabre"),
           M("Albertus Pictor", "Painters", "(c. 1440-1509) Swedish church painter, Täby and Härkeberga"),
           M("Vincent of Kastav", "Painters", "Istrian painter of St Mary at Beram, 1474"),
           M("John of Kastav", "Painters", "Istrian painter of Holy Trinity, Hrastovlje, 1490"),
           M("Master Theodoric", "Painters", "Bohemian court painter of the Holy Cross Chapel, Karlštejn, 1360s")],
    knowledge_sites=[W("Church of the Holy Trinity, Hrastovlje", "Bohemia and Central Europe", "Slovenia; 1490 fresco cycle with the Dance of Death"),
                     W("Beram", "Bohemia and Central Europe", "Istria; St Mary on the Rocks, 1474 Dance of Death by Vincent of Kastav")])
X[("L2-44", "Nordic church wall painting (kalkmålningar, Albertus Pictor)")] = LBL
X[("L2-44", "Istrian and Slovene Gothic frescoes (Beram, Hrastovlje)")] = drop("bucket label without gathered sites; Beram and Hrastovlje added as sites")
X[("L2-44", "Albertus Pictor")] = drop("duplicate: added as a named painter with a source")

E["L2-45"] = dict(axis=AX, catalogues=[UN(598, "Churches of Moldavia"), WP("Painted churches of northern Moldavia", "group article"), COM("Painted monasteries Bukovina")],
    kinds=[W("Exterior fresco programmes", "Sub-types", "Last Judgement, Tree of Jesse, Siege of Constantinople and Akathist on outer walls, 1530s-1600", "Voroneț Monastery"),
           MS("Toma of Suceava", "Painters", "painter of Humor Monastery, 1535", "Toma of Suceava")],
    knowledge_sites=[W("Sucevița Monastery", "Painted churches", "Suceava county; 1580s-1601; the last and fullest painted church"),
                     W("Moldovița Monastery", "Painted churches", "Suceava county; 1537 exterior frescoes incl. the Siege of Constantinople"),
                     W("Arbore Church", "Painted churches", "Suceava county; 1541 frescoes by Dragoș Coman"),
                     W("Probota Monastery", "Painted churches", "Suceava county; 1532; necropolis of Petru Rareș")])
X[("L2-45", "Voroneț")] = D
X[("L2-45", "Humor")] = D

E["L2-46"] = dict(axis="Sites catalogue from knowledge (the gathered record holds none): every painted-ceiling house with a Wikipedia article; by date.",
    catalogues=[CANMORE, ["https://www.historicenvironment.scot/", "Historic Environment Scotland", "properties in care incl. painted ceilings at Aberdour, Huntly and Kinneil"], WP("Scottish Renaissance painted ceilings", "type article")],
    kinds=[W("Tempera board-and-beam ceilings", "Sub-types", "tempera on pine boards and joists with emblems, grotesques and Virtues, c. 1550-1650", "Scottish Renaissance painted ceilings")],
    knowledge_sites=[W("Kinneil House", "Painted ceilings", "Bo'ness; 1550s murals of the Parable of the Good Samaritan and Samson"),
                     W("Crathes Castle", "Painted ceilings", "Aberdeenshire; Chamber of the Nine Nobles, Muses and Green Lady ceilings, 1590s-1602"),
                     W("Earlshall Castle", "Painted ceilings", "Leuchars, Fife; long-gallery heraldic ceiling, 1620"),
                     W("Aberdour Castle", "Painted ceilings", "Fife; 1630s painted ceiling in the east range"),
                     W("Culross Palace", "Painted ceilings", "Fife; painted ceiling with emblems and verses, early 17th c."),
                     W("Gladstone's Land", "Painted ceilings", "Edinburgh; tenement with painted ceilings, 1620")])
X[("L2-46", "Scottish Renaissance painted ceilings")] = drop("restates the leaf label")

E["L2-47"] = dict(axis="Sites catalogue from knowledge (the gathered record holds none): named mural sites with a Wikipedia article; republican, loyalist and post-conflict.",
    catalogues=[["https://cain.ulster.ac.uk/murals/", "CAIN: Murals in Northern Ireland", "Conflict Archive on the Internet photographic survey of murals"], WP("Murals in Northern Ireland", "tradition article"), COM("Murals in Northern Ireland")],
    kinds=[M("The Bogside Artists", "Makers", "Tom Kelly, William Kelly and Kevin Hasson: People's Gallery murals, Derry, 1994-2008", "Bogside Artists")],
    knowledge_sites=[W("Free Derry Corner", "Republican murals", "Bogside, Derry; 1969 gable slogan 'You are now entering Free Derry'"),
                     SR("International Wall", "Republican murals", "Falls Road, Belfast; changing wall of solidarity murals", "International Wall Belfast"),
                     SR("People's Gallery (Derry)", "Republican murals", "Rossville Street, Derry; 12 murals by the Bogside Artists", "People's Gallery Bogside")])
X[("L2-47", "Murals in Northern Ireland")] = drop("restates the leaf label")

E["L2-48"] = dict(axis=FOLK, catalogues=[COM("Samchyky painting"), [surl("Samchyky painting"), "Wikipedia search: Samchyky painting", "articles on the tradition and the village"]],
    kinds=[SR("Samchyky (village)", "Centres & workshops", "Khmelnytskyi oblast, Ukraine; village and estate where the floral decorative painting developed", "Samchyky")])
X[("L2-48", "Samchyky decorative painting")] = ("alias",)

E["L2-49"] = dict(axis="Sub-types first, then ceilings by country and phase (Italy, France, Britain, Iberia, the German lands before and after 1730, Bohemia), then painters by school.",
    catalogues=[WGA, ["https://www.deckenmalerei.eu/", "Corpus der barocken Deckenmalerei in Deutschland (CbDD)", "catalogue of Baroque ceiling paintings in Germany"], POP, ICCD],
    kinds=[W("Quadratura", "Sub-types", "painted architecture extending the real walls into fictive storeys", "Quadratura"),
           W("Di sotto in sù", "Sub-types", "figures foreshortened to be seen from below", "Di sotto in sù"),
           M("Andrea Mantegna", "Renaissance precursors", "Camera degli Sposi oculus, Mantua, 1465-74"),
           M("Correggio", "Renaissance precursors", "domes of San Giovanni Evangelista and Parma Cathedral, 1520-30"),
           M("Annibale Carracci", "Roman Baroque", "Farnese Gallery, Rome, 1597-1608"),
           M("Pietro da Cortona", "Roman Baroque", "Triumph of Divine Providence, Palazzo Barberini, 1633-39"),
           M("Giovanni Lanfranco", "Roman Baroque", "dome of Sant'Andrea della Valle, 1625-27"),
           M("Giovanni Battista Gaulli", "Roman Baroque", "Triumph of the Name of Jesus, Il Gesù, 1676-79"),
           M("Luca Giordano", "Roman Baroque", "Palazzo Medici Riccardi gallery, Florence; Escorial vaults"),
           M("Giovanni Battista Tiepolo", "Venetian Rococo", "Würzburg Residence staircase, 1752-53; Royal Palace of Madrid"),
           M("Charles Le Brun", "French and British ceiling painters", "Hall of Mirrors, Versailles, 1678-84"),
           M("Johann Michael Rottmayr", "Central European Baroque and Rococo", "Karlskirche dome, Vienna, 1725-30"),
           M("Cosmas Damian Asam", "Central European Baroque and Rococo", "Weltenburg Abbey; Asamkirche, Munich"),
           M("Johann Baptist Zimmermann", "Central European Baroque and Rococo", "Wieskirche ceiling, 1753-54"),
           M("Paul Troger", "Central European Baroque and Rococo", "Melk Abbey library and marble hall, 1731-32"),
           M("Daniel Gran", "Central European Baroque and Rococo", "Prunksaal of the Austrian National Library, 1726-30"),
           M("Franz Anton Maulbertsch", "Central European Baroque and Rococo", "Piarist church, Vienna; Sümeg parish church")])
X[("L2-49", "Andrea Pozzo")] = ("Bolognese and Jesuit quadraturisti", "(1642-1709) Glorification of St Ignatius, Sant'Ignazio, Rome, 1685-94", None, 1)
X[("L2-49", "Agostino Tassi")] = ("Bolognese and Jesuit quadraturisti", "(1578-1644) quadratura in Roman palaces, teacher of Claude", None, 1)
X[("L2-49", "Agostino Mitelli and Angelo Michele Colonna")] = drop("duplicate: the two painters are listed individually")
X[("L2-49", "Agostino Mitelli")] = ("Bolognese and Jesuit quadraturisti", "(1609-1660) Bolognese quadraturista, partner of Colonna (Palazzo Pitti)")
X[("L2-49", "Angelo Michele Colonna")] = ("Bolognese and Jesuit quadraturisti", "(1604-1687) Bolognese figure and quadratura painter")
X[("L2-49", "James Thornhill")] = ("French and British ceiling painters", "(1675-1734) Painted Hall, Greenwich; dome of St Paul's")
X[("L2-49", "Antonio Verrio")] = ("French and British ceiling painters", "(c. 1636-1707) Heaven Room, Burghley; Windsor and Hampton Court")

E["L2-50"] = dict(axis="Sites and cycles by period (Trecento, Early, High and Late Renaissance), dated by the cycle; then fresco painters by period.",
    catalogues=[WGA, ICCD, WP("Fresco", "technique article with major Italian cycles"), COM("Italian Renaissance frescoes")],
    kinds=[M("Giotto", "Trecento fresco painters", "(c. 1267-1337) Scrovegni Chapel, Padua; Bardi and Peruzzi chapels, Florence"),
           M("Pietro Lorenzetti", "Trecento fresco painters", "(c. 1280-1348) Lower Church, Assisi"),
           M("Ambrogio Lorenzetti", "Trecento fresco painters", "(c. 1290-1348) Allegory of Good and Bad Government, Siena"),
           M("Simone Martini", "Trecento fresco painters", "(c. 1284-1344) Maestà, Palazzo Pubblico, Siena"),
           M("Taddeo Gaddi", "Trecento fresco painters", "(c. 1300-1366) Baroncelli Chapel, Santa Croce"),
           M("Altichiero", "Trecento fresco painters", "(c. 1330-1390) Oratory of San Giorgio, Padua"),
           M("Masaccio", "Early Renaissance fresco painters", "(1401-1428) Brancacci Chapel; Holy Trinity, Santa Maria Novella"),
           M("Masolino", "Early Renaissance fresco painters", "(c. 1383-1447) Brancacci Chapel; Castiglione Olona", "Masolino da Panicale"),
           M("Fra Angelico", "Early Renaissance fresco painters", "(c. 1395-1455) San Marco convent cells; Niccoline Chapel"),
           M("Paolo Uccello", "Early Renaissance fresco painters", "(1397-1475) Chiostro Verde; John Hawkwood"),
           M("Andrea del Castagno", "Early Renaissance fresco painters", "(c. 1419-1457) Last Supper, Sant'Apollonia"),
           M("Piero della Francesca", "Early Renaissance fresco painters", "(c. 1415-1492) Legend of the True Cross, Arezzo"),
           M("Benozzo Gozzoli", "Early Renaissance fresco painters", "(c. 1421-1497) Magi Chapel, Palazzo Medici Riccardi"),
           M("Domenico Ghirlandaio", "Early Renaissance fresco painters", "(1448-1494) Tornabuoni Chapel, Santa Maria Novella"),
           M("Pinturicchio", "High Renaissance fresco painters", "(c. 1452-1513) Borgia Apartments; Piccolomini Library, Siena"),
           M("Luca Signorelli", "High Renaissance fresco painters", "(c. 1450-1523) San Brizio Chapel, Orvieto"),
           M("Filippino Lippi", "High Renaissance fresco painters", "(c. 1457-1504) Carafa Chapel; Strozzi Chapel"),
           M("Michelangelo", "High Renaissance fresco painters", "(1475-1564) Sistine Chapel ceiling and Last Judgment"),
           M("Raphael", "High Renaissance fresco painters", "(1483-1520) Raphael Rooms, Vatican"),
           M("Andrea del Sarto", "High Renaissance fresco painters", "(1486-1530) Chiostro dello Scalzo; Santissima Annunziata"),
           M("Giulio Romano", "Late Renaissance and Mannerist fresco painters", "(c. 1499-1546) Palazzo del Te, Mantua"),
           M("Pontormo", "Late Renaissance and Mannerist fresco painters", "(1494-1557) Poggio a Caiano lunette; Certosa del Galluzzo")])
for n in ("Scrovegni (Arena) Chapel", "Brancacci Chapel", "Sistine Chapel ceiling"): X[("L2-50", n)] = None
