# Spec part A: E1-1 .. E1-60.  S(code, pat, kw, prof, ...) ; rows: (name, group, gloss, wiki_title_or_url, is_maker)
# group 'W' = a named work, placed by object type; ov: overrides of input rows by name
from spec_lib import S

ISL = "islam"
S("E1-1", pat=[(r"abbasid|basra|samarra|\biraq", r"opaque|tin.glaz|white glaze|cobalt|blue")], excl=r"lustre|luster|splash", kw="Abbasid ceramic",
  rows=[("Basra", "Centres & workshops", "port city of southern Iraq, the main centre of opaque-white tin-glazed ware, 9th c.", "Basra", 0),
        ("Samarra", "Centres & workshops", "Abbasid capital (836–892) whose excavations yielded the ware alongside imported Chinese stoneware", "Samarra", 0),
        ("Cobalt-blue painted ware", "Sub-types", "white-glazed bowls painted in cobalt blue, often with Kufic words or palmettes; the first Islamic blue-and-white", "Islamic pottery", 0),
        ("Green-and-blue splashed white ware", "Sub-types", "opaque-white ware with green splashes and cobalt motifs, Iraq, 9th c.", "Islamic pottery", 0)],
  ov={"Ibrahim al-Nasrani": ("Ibrahim al-Nasrani", "Makers", "Abbasid potter known from a signed tin-glazed bowl, 9th c. (attribution uncertain)")})
S("E1-2", pat=[(r"abbasid|basra|samarra|\biraq", r"lustre|luster")], kw="Abbasid lustre",
  rows=[("Polychrome lustre", "Sub-types", "earliest lustre phase, several metallic tones on one vessel, Iraq, 9th c.", "Lustreware", 0),
        ("Monochrome lustre", "Sub-types", "later single-tone (olive-gold) lustre, often with figures, Iraq, 10th c.", "Lustreware", 0),
        ("Basra", "Centres & workshops", "southern Iraqi city, the probable main centre of Abbasid lustre production", "Basra", 0),
        ("Samarra", "Centres & workshops", "Abbasid capital whose palace excavations yielded lustre tiles and vessels", "Samarra", 0),
        ("Lustre tiles of the mihrab, Great Mosque of Kairouan", "W", "Iraqi lustre tiles framing the mihrab, c. 862–863; in situ, Kairouan (Tunisia), UNESCO site", "Mosque of Uqba", 0)],
  ov={"Abu Nasr of Basra": ("Abu Nasr of Basra", "Makers", "Basra potter known from a signed lustre dish, 9th c. (attribution uncertain)")})
S("E1-3", pat=[(r"fatimid", r"lustre|luster")], kw="Fatimid lustre",
  rows=[("Fustat", "Centres & workshops", "the old city of Cairo, centre of Fatimid lustre production; its kiln debris fills museum study collections", "Fustat", 0),
        ("Figural lustre bowls", "Sub-types", "bowls with musicians, drinkers, wrestlers and animals in lustre on white, Egypt, 11th c.", "Lustreware", 0)],
  ov={"Possibly, ‘Sa‘d’": ("Possibly, ‘Sa‘d’", "Makers", "Sa'd, Fatimid lustre potter whose signature appears on several vessels; tentative attribution")})
S("E1-4", pat=[(r"samanid|nishapur|samarqand|samarkand|afrasiyab|afrasiab", r"slip")], excl=r"splash|sgraff", kw="Nishapur slipware",
  rows=[("Epigraphic slipware", "Sub-types", "white-slipped bowls inscribed in black Kufic with Arabic aphorisms, Nishapur and Samarqand, 10th c.", "Islamic pottery", 0),
        ("Buff ware", "Sub-types", "Nishapur ware painted in black, green and yellow slips on a buff ground, with figures and birds", "Islamic pottery", 0),
        ("Nishapur", "Centres & workshops", "Khorasan city whose excavations (Metropolitan Museum, 1935–40) defined the ware", "Nishapur", 0),
        ("Samarqand (Afrasiyab)", "Centres & workshops", "the old site of Samarqand, the other great centre of Samanid slipware", "Afrasiyab (Samarkand)", 0)])
S("E1-5", pat=[r"splash"], excl=r"japan|日本|江戸", kw="splashware",
  rows=[("Sgraffiato splashware", "Sub-types", "splashware incised through the slip before glazing, Iraq, Iran and Central Asia, 9th–11th c.", "Sgraffito", 0),
        ("Tang sancai", "Sub-types", "the Chinese lead-glazed splashed ware that splashware imitates", "Sancai", 0),
        ("Samarkand", "Centres & workshops", "Afrasiyab kilns produced splashed and incised wares in the Samanid period", "Afrasiyab (Samarkand)", 0)])
S("E1-6", pat=[(r"sgraff|garrus|aghkand|amol|champlev", r"iran|persia|aghkand|garrus|amol|azerbaijan|caucas")], kw="sgraffito Iran",
  rows=[("Garrus ware", "Sub-types", "carved champlevé ware of north-west Iran, dark ground cut away to a white slip, 12th–13th c.", "Sgraffito", 0),
        ("Aghkand ware", "Sub-types", "incised ware painted in green, yellow and brown glazes, north-west Iran/Azerbaijan, 12th–13th c.", "Sgraffito", 0),
        ("Amol ware", "Sub-types", "sgraffito ware of Mazandaran with green and brown splashes, 13th–14th c.", "Amol", 0),
        ("Champlevé ware", "Sub-types", "slip carved back in broad areas to reveal the body, a variant of Garrus ware", "Champlevé", 0)])
S("E1-7", pat=[r"unglazed|barbotine|water.?filter|jug.?filter|\bfilter\b"], src=("islamic",), kw="Islamic unglazed",
  rows=[("Jug filters", "Sub-types", "pierced clay strainers in the necks of water jugs, carved with animals and inscriptions, Egypt and Syria, 10th–14th c.", "Islamic pottery", 0),
        ("Barbotine ware", "Sub-types", "unglazed jars with applied clay relief, Syria and Iraq, 12th–14th c.", "Islamic pottery", 0),
        ("Stamped and moulded ware", "Sub-types", "unglazed vessels with impressed or mould-made ornament, Iraq and Iran", "Islamic pottery", 0)],
  ov={"Yahya bin Umayya": ("Yahya bin Umayya", "Makers", "early Abbasid potter known from a signed jar, 8th c. (attribution uncertain)")})
S("E1-8", pat=[(r"hispano|manises|paterna|m[aá]laga|nasrid|mud[eé]jar|muel|valencia", r"lustre|luster|tin.glaz|earthenware|ceramic|pottery|maiolica")], excl=r"valencioid|malagasy|madagascar", kw="Hispano-Moresque",
  met=["Spanish, Valencia", "Spanish, Manises", "Spanish, Valencia, Manises"],
  rows=[("Málaga", "Centres & workshops", "Nasrid centre of lustreware, 13th–15th c., source of the Alhambra vases", "Málaga", 0),
        ("Manises", "Centres & workshops", "village near Valencia, the leading centre from the 14th c.", "Manises", 0),
        ("Paterna", "Centres & workshops", "Valencian centre of green-and-manganese ware and early lustre, 13th–14th c.", "Paterna", 0),
        ("Muel", "Centres & workshops", "Aragonese centre of later lustreware, 16th–17th c.", "Muel", 0),
        ("Alhambra vases", "Sub-types", "monumental winged Nasrid lustre amphorae, Málaga, 14th c.", "Alhambra vase", 0)],
  ov={"Spanish, Valencia": "alias"})
S("E1-9", pat=[r"[cç]anakkale|chanak"], kw="Canakkale",
  rows=[("Çanakkale", "Centres & workshops", "Dardanelles town whose workshops made the ware from the 17th to the early 20th c.", "Çanakkale", 0)])
S("E1-10", pat=[r"\bfez\b|\bfès\b|\bfes\b|fassi|\bsafi\b|tamegroute|morocc|maroc"], kw="Fez pottery",
  rows=[("Fez", "Centres & workshops", "city of the blue-and-white and polychrome tin-glazed urban wares", "Fez, Morocco", 0),
        ("Safi", "Centres & workshops", "Atlantic port whose potters' hill has made glazed wares since the 19th c.", "Safi, Morocco", 0),
        ("Tamegroute", "Centres & workshops", "Draa valley village of green-glazed pottery", "Tamegroute", 0),
        ("Zellij", "Sub-types", "glazed tile mosaic cut by hand, made in Fez and Meknes", "Zellij", 0)])
S("E1-11", pat=[r"kabyl"], kw="Kabyle pottery",
  rows=[("Kabylia", "Centres & workshops", "Berber region of northern Algeria where women hand-build and paint the ware", "Kabylia", 0)])
S("E1-12", pat=[r"sejnane"], kw="Sejnane", ich=("https://ich.unesco.org/en/RL/pottery-skills-of-the-women-of-sejnane-01504", "UNESCO ICH: Pottery skills of the women of Sejnane", "Representative List element (2018) with documentation"),
  rows=[("Sejnane", "Centres & workshops", "town in Bizerte governorate, northern Tunisia, home of the women potters", "Sejnane", 0)])
S("E1-13", pat=[(r"risht|gijduv|ghijduv|uzbek|fergana|ferghana|khorezm|samarkand ceramics", r"ceram|pott|earthenware|glaz|bowl|dish|plate|lagan")], kw="Rishtan ceramics",
  rows=[("Rishton", "Centres & workshops", "Fergana valley town, the main centre of ishkor-glazed blue ware", "Rishton", 0),
        ("Gijduvan", "Centres & workshops", "Bukhara region centre of brown-and-yellow glazed ware", "Gʻijduvon", 0)])
S("E1-14", pat=[r"ban chiang"], kw="Ban Chiang",
  rows=[("Ban Chiang", "Centres & workshops", "burial site in Udon Thani, north-east Thailand; UNESCO World Heritage Site (1992)", "Ban Chiang", 0),
        ("Late period red-on-buff ware", "Schools & phases", "painted swirl-decorated jars of c. 300 BC–AD 200, the best-known Ban Chiang pottery", "Ban Chiang", 0)])
S("E1-15", pat=[r"\bch[aă]m\b|b[aà]u tr[uú]c"], node=r"Ch[aă]m", kw="Cham pottery", ich=("https://ich.unesco.org/en/USL/art-of-pottery-making-of-cham-people-01574", "UNESCO ICH: Art of pottery-making of Chăm people", "Urgent Safeguarding List element (2022)"),
  rows=[("Bàu Trúc", "Centres & workshops", "Cham pottery village in Ninh Thuận province, Vietnam", "Bàu Trúc", 0)])
S("E1-16", pat=[r"kasongan"], kw="Kasongan")
S("E1-17", pat=[r"yangshao|majiayao|banshan|machang|banpo|kansu|gansu|仰韶|馬家窯|彩陶"], kw="Yangshao", prof="china", zh="彩陶",
  rows=[("Banpo phase", "Schools & phases", "early Yangshao phase (c. 4800–4300 BC) named after the Banpo village site near Xi'an", "Banpo", 0),
        ("Miaodigou phase", "Schools & phases", "middle Yangshao phase with painted petal and dot motifs, c. 4000–3500 BC", "Yangshao culture", 0),
        ("Majiayao culture", "Schools & phases", "western successor in Gansu and Qinghai, with Majiayao, Banshan and Machang phases", "Majiayao culture", 0),
        ("Banshan phase", "Schools & phases", "Majiayao phase of large spiral-painted storage jars, c. 2600–2300 BC", "Majiayao culture", 0)],
  ov={"Majiayao": "drop:duplicate of the Majiayao culture row"})
S("E1-18", pat=[r"j[oō]mon|縄文|조몬"], kw="Jomon", prof="japan", jp="縄文土器",
  rows=[("Flame-style pottery (kaen-gata doki)", "Sub-types", "Middle Jōmon vessels with flame-like rims, Niigata, c. 3000 BC; Sasayama examples are a National Treasure", "Jōmon pottery", 0),
        ("Incipient Jōmon", "Schools & phases", "the earliest phase, c. 14,000–8000 BC, among the oldest pottery in the world", "Jōmon period", 0),
        ("Middle Jōmon", "Schools & phases", "c. 3000–2000 BC, the phase of the most elaborate sculptural vessels", "Jōmon period", 0),
        ("Jōmon Venus", "W", "dogū figure from Tanabatake, Chino (Nagano), c. 3000–2000 BC; National Treasure", "Jōmon Venus", 0),
        ("Shakōki-dogū", "Sub-types", "'goggle-eyed' Final Jōmon figures, Kamegaoka culture, northern Honshu", "Dogū", 0)],
  ov={"Dogū": ("Dogū", "Sub-types", "clay figurines of the Jōmon period, from slab figures to hollow 'goggle-eyed' types")})
S("E1-19", pat=[r"yayoi|弥生"], kw="Yayoi pottery", prof="japan", jp="弥生土器",
  rows=[("Yoshinogari site", "Centres & workshops", "large moated Yayoi settlement in Saga prefecture, a Special Historic Site", "Yoshinogari site", 0),
        ("Karako-Kagi site", "Centres & workshops", "Yayoi settlement in Nara whose pottery bears incised pictures of buildings", "Karako-Kagi site", 0)])
S("E1-20", pat=[(r"sancai|san.?ts.?ai|三彩|three.colou?r", r"\btang\b|唐")], excl=r"liao|遼|奈良|nara|japan|日本", kw="sancai", prof="china", zh="三彩",
  rows=[("Tang tomb figures", "Sub-types", "sancai-glazed burial figures of horses, camels, guardians and courtiers, 7th–8th c.", "Tang dynasty tomb figures", 0),
        ("Liao sancai", "Sub-types", "later three-colour ware of the Khitan Liao dynasty, 10th–12th c.", "Sancai", 0),
        ("Nara sancai", "Sub-types", "Japanese imitation of Tang sancai, 8th c., preserved in the Shōsōin", "Sancai", 0),
        ("Gongxian kilns", "Centres & workshops", "Henan kilns (Gongyi) that produced much Tang sancai and early white ware", "Gongyi", 0)],
  ov={"sancai": "alias", "Huanan sancai": ("Huanan sancai", "Sub-types", "south Chinese (Fujian) three-colour lead-glazed ware of the late Ming, exported to Japan as Kōchi ware")})
S("E1-21", pat=[r"\braku\b|楽焼|楽茶碗|赤楽|黒楽|長次郎|chojiro|chōjirō|ノンコウ|nonk[oō]"], kw="Raku ware", prof="japan", jp="楽茶碗",
  rows=[("Black raku (kuro-raku)", "Sub-types", "iron-black glazed tea bowls fired and pulled hot from the kiln", "Raku ware", 0),
        ("Red raku (aka-raku)", "Sub-types", "lower-fired tea bowls of red clay under clear glaze", "Raku ware", 0),
        ("Western raku", "Sub-types", "American post-firing reduction raku developed by Paul Soldner from the 1960s", "Raku ware", 0),
        ("Chōjirō", "Makers", "founder of raku, potter to Sen no Rikyū, Kyoto, d. 1589", "Chōjirō", 1),
        ("Hon'ami Kōetsu", "Makers", "Kyoto artist whose hand-built raku tea bowls include the National Treasure 'Fuji-san', 1558–1637", "Hon'ami Kōetsu", 1),
        ("Raku Dōnyū (Nonkō)", "Makers", "third Raku head, celebrated for glossy black glazes, 1599–1656", "Raku ware", 1),
        ("Raku Kichizaemon XV", "Makers", "fifteenth head of the Raku family (b. 1949), now Raku Jikinyū", "Raku ware", 1)])
S("E1-22", pat=[r"satsuma|薩摩"], kw="Satsuma ware", prof="japan", jp="薩摩焼",
  rows=[("Kyō-Satsuma", "Sub-types", "gilded, enamelled export Satsuma decorated in Kyoto, Osaka and Tokyo, late 19th c.", "Satsuma ware", 0),
        ("Kuro-Satsuma", "Sub-types", "black-glazed everyday stoneware of Satsuma kilns", "Satsuma ware", 0),
        ("Shiro-Satsuma", "Sub-types", "crackled ivory ware for the Shimazu lords, later the base of export painting", "Satsuma ware", 0),
        ("Yabu Meizan", "Makers", "Osaka decorator of fine export Satsuma, 1853–1934", "Yabu Meizan", 1),
        ("Kinkōzan", "Makers", "Kyoto family workshop, the largest maker of Kyō-Satsuma export ware", "Kinkōzan Sōbei", 1)],
  ov={"Satsuma ware": "alias", "Toyosai": ("Toyosai", "Makers", "decorator of Satsuma export ware, Meiji period; the commonest Satsuma signature in the Rijksmuseum", None, 1)})
S("E1-23", pat=[r"onggi|옹기"], kw="onggi", prof="korea",
  rows=[("Jangdokdae", "Sub-types", "terrace of onggi jars for fermenting soy sauce, gochujang and kimchi", "Jangdokdae", 0)],
  ov={"onggi": "alias"})
S("E1-24", pat=[r"kgatleng|bakgatla|botswana"], kw="Botswana pottery", ich=("https://ich.unesco.org/en/USL/earthenware-pottery-making-skills-in-botswanas-kgatleng-district-00753", "UNESCO ICH: Earthenware pottery-making skills in Botswana's Kgatleng District", "Urgent Safeguarding List element (2012)"),
  rows=[("Kgatleng District", "Centres & workshops", "district of south-eastern Botswana, home of the Bakgatla ba Kgafela potters", "Kgatleng District", 0),
        ("Mochudi", "Centres & workshops", "Bakgatla capital, a centre of the women potters", "Mochudi", 0)],
  ov={"Earthenware pottery-making skills in Botswana’s Kgatleng District": "alias"})

GRK = "greek"
S("E1-25", pat=[(r"geometric|dipylon", r"greek|attic|athen|argive|boeot")], kw="Geometric Greek", prof=GRK,
  rows=[("Protogeometric style", "Schools & phases", "c. 1050–900 BC, compass-drawn circles on Attic amphorae", "Protogeometric style", 0),
        ("Late Geometric", "Schools & phases", "c. 760–700 BC, figured funeral scenes on monumental grave vases", "Geometric art", 0),
        ("Dipylon Amphora", "W", "monumental Late Geometric grave amphora with a prothesis scene, c. 760–750 BC; National Archaeological Museum, Athens", "Dipylon Amphora", 0),
        ("Dipylon krater", "W", "Late Geometric funerary krater by the Hirschfeld workshop, c. 750–735 BC; Metropolitan Museum, New York", "Dipylon krater", 0)],
  ov={"Subgeometric": ("Subgeometric", "Schools & phases", "lingering Geometric decoration in peripheral Greek workshops after c. 700 BC")})
S("E1-26", pat=[r"corinth"], excl=r"etrusco", kw="Corinthian", prof=GRK, met=["Greek, Corinthian"],
  rows=[("Transitional Corinthian", "Schools & phases", "c. 640–625 BC, between Protocorinthian and Early Corinthian", "Corinthian vase painting", 0),
        ("Early, Middle and Late Corinthian", "Schools & phases", "the animal-frieze and later figured phases, c. 625–550 BC", "Corinthian vase painting", 0),
        ("Chigi vase", "W", "Protocorinthian olpe with a hoplite battle, c. 650–640 BC; Villa Giulia, Rome", "Chigi vase", 0),
        ("Chigi Painter", "Makers", "Protocorinthian painter of the Chigi vase, mid-7th c. BC", "Chigi Painter", 1),
        ("Timonidas", "Makers", "Corinthian painter who signed his works, c. 580–570 BC", "Timonidas", 1)],
  ov={"Greek, Corinthian": "alias", "Protocorinthian": ("Protocorinthian", "Schools & phases", "c. 720–640 BC, miniaturist animal friezes and early black-figure")})
S("E1-29", pat=[r"laconian|lakonian|sparta"], kw="Laconian", prof=GRK, met=["Greek, Laconian"],
  rows=[("Arkesilas Painter", "Makers", "Laconian black-figure painter, c. 565–560 BC", "Arkesilas Painter", 1),
        ("Hunt Painter", "Makers", "Laconian cup painter, c. 565–530 BC", "Hunt Painter", 1),
        ("Naucratis Painter", "Makers", "Laconian painter, first half of the 6th c. BC", "Naucratis Painter", 1),
        ("Boreads Painter", "Makers", "Laconian painter named for a cup with the Boreads, c. 575–565 BC", "Boreads Painter", 1),
        ("Rider Painter", "Makers", "Laconian cup painter, c. 550–530 BC", "Rider Painter", 1),
        ("Arkesilas Cup", "W", "Laconian cup showing King Arkesilas II weighing goods, c. 565–560 BC; Bibliothèque nationale, Paris", "Arkesilas Cup", 0)],
  ov={"Greek, Laconian": "alias"})
S("E1-30", pat=[(r"east greek|clazomen|klazomen|fikellura|wild goat|rhodian|chian|chiot|ionian|samian|milesian", r"greek|archaic|b\.?c")], kw="East Greek", prof=GRK, met=["Greek, East Greek", "East Greek"],
  rows=[("Euphorbos plate", "W", "Rhodian Wild Goat Style plate with Menelaus and Hector over Euphorbos, c. 600 BC; British Museum, London", "Euphorbos plate", 0),
        ("Northampton Group", "Sub-types", "black-figure amphorae made by East Greek painters, probably in Italy, c. 540 BC", "Northampton Group", 0)],
  ov={"Greek, East Greek": "alias",
      "East Greek, Clazomenian": ("Clazomenian vase painting", "Sub-types", "black-figure pottery of Klazomenai, c. 560–520 BC, with sarcophagi of the same style"),
      "Wild Goat Style": ("Wild Goat Style", "Sub-types", "orientalising animal-frieze style of the East Aegean, c. 650–550 BC"),
      "Fikellura": ("Fikellura style", "Sub-types", "Milesian/Samian style with crescents and running figures on a pale ground, c. 560–494 BC"),
      "Rhodian": ("Rhodes", "Centres & workshops", "island centre long credited with the Wild Goat Style; the label survives in museum records"),
      "Chian": ("Chios", "Centres & workshops", "island producing a white-slipped fine ware, chalices and black-figure, 7th–6th c. BC")})
S("E1-31", pat=[r"apulian|campanian|lucanian|paestan|italiote|south italian.*(vase|krater|red.figure)|canosan"], kw="Apulian", prof=GRK,
  met=["Greek, Apulian", "Greek, Campanian", "Greek, South Italian", "Greek, Lucanian", "Greek, Paestan", "Greek, Sicilian", "Greek, Canosan"],
  rows=[("Darius Painter", "Makers", "Apulian red-figure painter of the Darius Vase, active c. 340–320 BC", "Darius Painter", 1),
        ("Underworld Painter", "Makers", "late Apulian painter of Hades scenes, c. 330–310 BC", "Underworld Painter", 1),
        ("Lycurgus Painter", "Makers", "Apulian Ornate-style painter, c. 360–340 BC", "Lycurgus Painter", 1),
        ("Asteas", "Makers", "Paestan vase painter who signed his works, c. 360–330 BC", "Asteas", 1),
        ("Python", "Makers", "Paestan vase painter, colleague of Asteas, c. 360–320 BC", "Python (painter)", 1),
        ("Pisticci Painter", "Makers", "the earliest Lucanian red-figure painter, c. 440–420 BC", "Pisticci Painter", 1),
        ("Darius Vase", "W", "Apulian volute krater with the Persian council of Darius, c. 340–320 BC; Museo Archeologico Nazionale, Naples", "Darius Vase", 0)],
  ov={"Greek, Apulian": ("Apulian vase painting", "Sub-types", "red-figure of Taranto and Apulia, Plain and Ornate styles, c. 430–300 BC"),
      "Greek, South Italian": "alias",
      "Greek, Campanian": ("Campanian vase painting", "Sub-types", "red-figure of Capua and Cumae, c. 380–300 BC"),
      "Lucanian": ("Lucanian vase painting", "Sub-types", "the first South Italian red-figure fabric, Metapontion and inland Lucania, from c. 440 BC"),
      "Paestan": ("Paestan vase painting", "Sub-types", "red-figure of Paestum, the workshops of Asteas and Python, c. 360–300 BC"),
      "Sicilian": ("Sicilian vase painting", "Sub-types", "red-figure of Syracuse, Gela and the Lipari islands, c. 400–300 BC")})
S("E1-32", pat=[r"gnathia|gnathian"], kw="Gnathia", prof=GRK, met=["Greek, Gnathian"],
  rows=[("Taranto", "Centres & workshops", "Greek Taras, the main centre of Gnathia production from c. 370 BC", "Taranto", 0),
        ("Egnazia", "Centres & workshops", "Apulian site (ancient Gnathia) where the ware was first found and that gave it its name", "Egnazia", 0)],
  ov={"Greek, Gnathian": "alias"})
S("E1-33", pat=[r"centuripe"], kw="Centuripe", prof=GRK, met=["Greek, Centuripe"],
  rows=[("Centuripe", "Centres & workshops", "hill town in eastern Sicily whose 3rd–2nd c. BC workshops made the ware", "Centuripe", 0)],
  ov={"Greek, Centuripe": "alias"})
S("E1-34", pat=[(r"etrusc|faliscan|caeretan|pontic|genucilia", r"vase|pott|ceram|terracotta|amphora|krater|kylix|hydria|cup|oinochoe|plate")], excl=r"bucchero", kw="Etruscan vase", prof=GRK,
  met=["Etruscan, Etrusco-Corinthian", "Etruscan, Italo-geometric", "Etruscan, Genucilia", "Etruscan, Faliscan", "Etruscan, Caeretan", "Greek, Caeretan"],
  rows=[("Pontic vases", "Sub-types", "Etruscan black-figure of the Paris Painter's circle, c. 550–500 BC", "Pontic vases", 0),
        ("Etruscan red-figure", "Sub-types", "Etruscan red-figure, first in added colour (pseudo-red-figure), then true red-figure, c. 480–300 BC", "Etruscan vase painting", 0),
        ("Micali Painter", "Makers", "prolific Etruscan black-figure painter at Vulci, c. 520–490 BC", "Micali Painter", 1),
        ("Paris Painter", "Makers", "leading painter of Pontic vases, c. 550–530 BC", "Paris Painter", 1),
        ("Eagle Painter", "Makers", "one of the two painters of the Caeretan hydriae, c. 530–510 BC", "Eagle Painter", 1)],
  ov={"Etruscan, Etrusco-Corinthian": ("Etrusco-Corinthian", "Sub-types", "Etruscan imitations of Corinthian animal-frieze ware, c. 630–540 BC"),
      "Etruscan, Italo-geometric": ("Italo-Geometric", "Schools & phases", "Geometric-style painted ware of Etruria and Latium, 8th–7th c. BC"),
      "Caeretan hydriae": ("Caeretan hydriae", "Sub-types", "lively black-figure hydriae made at Caere by East Greek immigrant painters, c. 530–510 BC"),
      "Genucilia plates": ("Genucilia plates", "Sub-types", "red-figure plates with a female head or star, Caere and Falerii, 4th c. BC"),
      "Faliscan red-figure": ("Faliscan red-figure", "Centres & workshops", "red-figure of Falerii Veteres, the finest of the Etruscan red-figure fabrics, 4th c. BC")})
S("E1-35", pat=[r"bucchero"], kw="bucchero", prof=GRK,
  rows=[("Bucchero sottile", "Sub-types", "thin-walled fine bucchero of the 7th c. BC, often incised", "Bucchero", 0),
        ("Bucchero pesante", "Sub-types", "heavy, relief-decorated bucchero of the 6th c. BC, Chiusi and inland Etruria", "Bucchero", 0),
        ("Cerveteri", "Centres & workshops", "Etruscan Caere, the main early centre of bucchero", "Cerveteri", 0),
        ("Chiusi", "Centres & workshops", "inland Etruscan city, centre of bucchero pesante", "Chiusi", 0)])
S("E1-36", pat=[r"minoan|kamares|knossos|phaistos"], kw="Minoan", prof=GRK, met=["Minoan"],
  rows=[("Vasiliki ware", "Sub-types", "mottled red-black Early Minoan ware from Vasiliki, eastern Crete", "Minoan pottery", 0),
        ("Kamares ware", "Sub-types", "polychrome eggshell-thin Middle Minoan palace ware, c. 2100–1700 BC", "Kamares ware", 0),
        ("Marine Style", "Sub-types", "Late Minoan IB vessels covered with octopus and sea life, c. 1500 BC", "Marine Style", 0),
        ("Floral Style", "Sub-types", "Late Minoan IA style of grasses and lilies, c. 1600 BC", "Minoan pottery", 0),
        ("Palace Style", "Sub-types", "formal LM II jars of Knossos, c. 1450 BC", "Minoan pottery", 0),
        ("Knossos", "Centres & workshops", "the great palace site, source of most Palace Style pottery", "Knossos", 0)])
S("E1-37", pat=[r"mycenae|helladic"], kw="Mycenaean", prof=GRK, met=["Mycenaean", "Helladic, Mycenaean", "Helladic"],
  rows=[("Pictorial style", "Sub-types", "LH III kraters with chariots and bulls, many exported to Cyprus, 14th–13th c. BC", "Mycenaean pottery", 0),
        ("Stirrup jar", "Sub-types", "the characteristic closed jar for oil and wine traded across the Mediterranean", "Stirrup jar", 0),
        ("Ephyraean goblets", "Sub-types", "LH IIB goblets with a single motif on each side", "Mycenaean pottery", 0),
        ("Close Style", "Sub-types", "densely decorated LH IIIC ware of the Argolid", "Mycenaean pottery", 0),
        ("Warrior Vase", "W", "LH IIIC krater with a file of soldiers, c. 1200 BC; National Archaeological Museum, Athens", "Warrior Vase", 0)],
  ov={"Mycenaean": "alias"})
S("E1-38", pat=[r"sigillata|samian ware|arretine|arezzo|graufesenque|lezoux|rheinzabern"], excl=r"east greek|archaic|maya|mexic|peru|india", kw="terra sigillata", prof="europe",
  rows=[("Arretine ware", "Centres & workshops", "the first Italian sigillata, Arezzo, c. 30 BC–AD 30", "Arretine ware", 0),
        ("La Graufesenque", "Centres & workshops", "southern Gaulish production centre, 1st c. AD", "La Graufesenque", 0),
        ("Lezoux", "Centres & workshops", "central Gaulish production centre, 2nd c. AD", "Lezoux", 0),
        ("Rheinzabern", "Centres & workshops", "East Gaulish centre on the Rhine, 2nd–3rd c. AD", "Rheinzabern", 0),
        ("African red slip ware", "Sub-types", "late Roman successor made in North Africa, 1st–7th c. AD", "African red slip ware", 0)],
  ov={"South Gaulish samian": ("South Gaulish samian", "Sub-types", "decorated and plain samian of La Graufesenque and Montans, exported across the Empire, 1st c. AD")})
S("E1-39", pat=[r"hadra"], kw="Hadra hydria", prof=GRK, met=["Greek, Alexandria-Hadra"],
  rows=[("Alexandria", "Centres & workshops", "the Ptolemaic capital whose Hadra cemetery gave the vases their name; many were made in Crete", "Alexandria", 0)])
S("E1-40", pat=[r"\bkerma\b"], node=r"Kerma culture", kw="Kerma", prof="americas_off",
  rows=[("Black-topped red ware", "Sub-types", "polished red vessels with a black rim band from reduction firing", "Kerma culture", 0),
        ("Kerma", "Centres & workshops", "capital of the kingdom of Kerma in Upper Nubia, c. 2500–1500 BC", "Kerma", 0)],
  ov={"Kerma culture (Nubia)": "alias"})
S("E1-41", pat=[r"meroitic|mero[eë]"], node=r"Napatan and Meroitic", mindate=-300, kw="Meroitic", prof="americas_off",
  rows=[("Meroë", "Centres & workshops", "royal city of Kush and source of its fine painted ware; UNESCO World Heritage Site", "Meroë", 0),
        ("Faras", "Centres & workshops", "Lower Nubian site whose cemeteries yielded much Meroitic painted pottery", "Faras", 0)],
  ov={"Napatan and Meroitic Kush": "alias"})
S("E1-42", pat=[r"nabat"], kw="Nabataean", prof="americas_off", met=["Nabataean"],
  rows=[("Petra", "Centres & workshops", "Nabataean capital whose az-Zurraba kilns made the eggshell ware; UNESCO World Heritage Site", "Petra", 0)],
  ov={"Nabataean": "alias"})

AM = "americas"
S("E1-43", pat=[r"\bmaya\b|\bmayan\b|usulut|plumbate"], kw="Maya ceramics", prof=AM,
  rows=[("Codex-style vases", "Sub-types", "black-line on cream vessels of the Mirador basin, Late Classic", "Maya ceramics", 0),
        ("Ik' style", "Sub-types", "Late Classic polychrome of the Motul de San José court", "Maya ceramics", 0),
        ("Princeton Vase", "W", "codex-style cylinder with a court scene, c. 670–750; Princeton University Art Museum", "Princeton Vase", 0),
        ("Vase of the Seven Gods", "W", "black-background cylinder with God L and six deities, Late Classic", "Vase of the Seven Gods", 0),
        ("Blom Plate", "W", "Late Classic plate of the Hero Twins shooting the bird deity", "Blom Plate", 0)],
  ov={"probably Maya (archaeological culture) (attributed)": "alias",
      "probably Mesoamerican: Usulután style (archaeological culture) (attributed)": ("Usulután ware", "Sub-types", "resist-decorated ware of the south-eastern Maya area, Late Preclassic"),
      "Plumbate ware": ("Plumbate ware", "Sub-types", "glossy, vitrified trade ware of the Pacific coast, traded into the Maya area, c. 900–1200")})
S("E1-44", pat=[r"teotihuac"], kw="Teotihuacan ceramic", prof=AM,
  rows=[("Cylindrical tripod vessels", "Sub-types", "lidded tripod cylinders, often stuccoed and painted, the signature Teotihuacan form", "Teotihuacan", 0),
        ("Thin Orange ware", "Sub-types", "fine trade ware made in Puebla and distributed by Teotihuacan", "Teotihuacan", 0),
        ("Theatre censers", "Sub-types", "composite incense burners with mould-made appliqués", "Teotihuacan", 0)],
  ov={"probably Teotihuacán (archaeological culture) (attributed)": "alias"})
S("E1-45", pat=[r"cocl[eé]|cont[eé] style|macaracas|parita|tonos[ií]|el hatillo|cubit[aá]|la mula"], kw="Coclé", prof=AM,
  rows=[("Sitio Conte", "Centres & workshops", "cemetery in Coclé province excavated by Harvard and the Penn Museum, the type site", "Sitio Conte", 0),
        ("El Caño", "Centres & workshops", "ceremonial cemetery near Sitio Conte with rich burials", "El Caño", 0)],
  ov={"probably Gran Coclé Tradition: Conté style (archaeological culture) (attributed)": ("Conté style", "Schools & phases", "c. 700–900, the classic polychrome style of Sitio Conte"),
      "probably Gran Coclé Tradition: Macaracas style (archaeological culture) (attributed)": ("Macaracas style", "Schools & phases", "c. 900–1100, red and purple painted animal designs"),
      "Parita style": ("Parita style", "Schools & phases", "c. 1100–1300, effigy and polychrome vessels"),
      "El Hatillo style": ("El Hatillo style", "Schools & phases", "c. 1300–1520, the last Gran Coclé style"),
      "Cubitá style": ("Cubitá style", "Schools & phases", "c. 550–700, early polychrome"),
      "Tonosí style": ("Tonosí style", "Schools & phases", "c. 200–550, the earliest polychrome style"),
      "La Mula style": ("La Mula style", "Schools & phases", "c. 200 BC–AD 200, precursor of the polychrome tradition")})
S("E1-46", pat=[r"nicoya|guanacaste"], kw="Nicoya polychrome", prof=AM,
  rows=[("Papagayo Polychrome", "Sub-types", "white-slipped polychrome of c. 800–1350, the best-known Nicoya type", "Greater Nicoya", 0),
        ("Pataky Polychrome", "Sub-types", "orange-slipped jaguar effigy vessels, c. 1000–1350", "Greater Nicoya", 0),
        ("Vallejo Polychrome", "Sub-types", "later polychrome with Mexican-style motifs, c. 1000–1350", "Greater Nicoya", 0)],
  ov={"probably Guanacaste-Nicoya (archaeological culture) (attributed)": "alias"})
S("E1-47", pat=[r"\bmoche|mochica"], kw="Moche ceramic", prof=AM,
  rows=[("Portrait vessels", "Sub-types", "mould-made stirrup-spout head vessels of individuals, Moche IV", "Moche culture", 0),
        ("Fine-line painted vessels", "Sub-types", "red-on-cream narrative scenes of the Sacrifice Ceremony and warriors", "Moche culture", 0),
        ("Larco Museum", "Centres & workshops", "Lima museum with the largest Moche ceramics collection; Rafael Larco Hoyle's five-phase sequence", "Larco Museum", 0)],
  ov={"Moche": "alias"})
S("E1-48", pat=[r"\bnasca|\bnazca"], kw="Nasca ceramic", prof=AM,
  rows=[("Monumental style", "Schools & phases", "Early Nasca (phases 3–4) with large clear mythical figures", "Nazca culture", 0),
        ("Proliferous style", "Schools & phases", "Middle–Late Nasca (phases 5–7) with rays and appendages", "Nazca culture", 0),
        ("Cahuachi", "Centres & workshops", "ceremonial centre of the Nazca, a source of much fine pottery", "Cahuachi", 0)],
  ov={"probably Nasca (Nazca) (archaeological culture) (attributed)": "alias"})
S("E1-49", pat=[r"chim[uú]"], kw="Chimu blackware", prof=AM,
  rows=[("Chan Chan", "Centres & workshops", "Chimú capital, UNESCO World Heritage Site", "Chan Chan", 0),
        ("Stirrup-spout blackware", "Sub-types", "mould-made reduction-fired vessels with a monkey at the spout base", "Chimú culture", 0)],
  ov={"probably Chimú (archaeological culture) (attributed)": "alias",
      "probably Central Andes: Chimú-Inka style (archaeological) (attributed)": ("Chimú-Inka style", "Sub-types", "blackware combining Chimú technique with Inca forms such as the aryballos, after c. 1470")})
S("E1-50", pat=[r"shipibo|conibo"], kw="Shipibo", prof=AM,
  rows=[("Chomo", "Sub-types", "large painted jars for masato beer", "Shipibo-Conibo people", 0)],
  ov={"Shipibo": "alias"})
S("E1-51", pat=[(r"talavera|puebla|tlaxcala", r"mexic|puebla|tlaxcala|poblana")], node=r"Talavera poblana", excl=r"reina|arzobispo", kw="Talavera Puebla", prof="folk",
  ich=("https://ich.unesco.org/en/RL/artisanal-talavera-of-puebla-and-tlaxcala-mexico-and-ceramics-of-talavera-de-la-reina-and-el-puente-del-arzobispo-spain-making-process-01462", "UNESCO ICH: Artisanal talavera of Puebla and Tlaxcala and ceramics of Talavera de la Reina", "Representative List element (2019)"),
  rows=[("Puebla", "Centres & workshops", "the city whose potters' guild (ordinances of 1653) defines the ware", "Puebla (city)", 0),
        ("Uriarte Talavera", "Centres & workshops", "Puebla workshop founded 1824, one of the certified Talavera makers", "Uriarte Talavera", 0)],
  ov={"Talavera poblana": "alias"})
S("E1-52", pat=[r"barro negro|coyotepec"], node=r"Barro negro", kw="barro negro", prof="folk",
  rows=[("Doña Rosa (Rosa Real Mateo)", "Makers", "Coyotepec potter who devised the burnished shine, 1900–1980", "Barro negro pottery", 1),
        ("Carlomagno Pedro Martínez", "Makers", "Coyotepec sculptor in barro negro, b. 1965", "Carlomagno Pedro Martínez", 1)],
  ov={"Barro negro (Oaxaca black pottery)": "alias", "San Bartolo Coyotepec": ("San Bartolo Coyotepec", "Centres & workshops", "Oaxaca town of the black pottery")})
S("E1-53", pat=[r"tonal[aá]|tlaquepaque"], node=r"Tonala", kw="Tonala pottery", prof="folk",
  rows=[("Jorge Wilmot", "Makers", "Tonalá ceramist who revived high-fired stoneware and old designs, 1928–2012", "Jorge Wilmot", 1),
        ("Barro bandera", "Sub-types", "Tonalá ware painted in the red, white and green of the flag", "Tonalá, Jalisco", 0)],
  ov={"Tonala and Tlaquepaque pottery": "alias",
      "bruñido": ("Bruñido", "Sub-types", "burnished, low-fired painted ware of Tonalá"),
      "petatillo": ("Petatillo", "Sub-types", "Tonalá ware with a fine cross-hatched 'mat' ground"),
      "Tlaquepaque": ("Tlaquepaque", "Centres & workshops", "neighbouring Jalisco pottery town and market")})
S("E1-54", pat=[r"mata ortiz|quezada"], node=r"Mata Ortiz", kw="Mata Ortiz", prof="folk",
  rows=[("Mata Ortiz", "Centres & workshops", "village in Chihuahua near Paquimé, home of some 400 potters", "Juan Mata Ortiz", 0)],
  ov={"Mata Ortiz pottery": "alias", "Juan Quezada": ("Juan Quezada", "Makers", "self-taught potter who revived Paquimé-style pottery from the 1970s, b. 1940", None, 1)})
S("E1-55", pat=[r"tree of life|[aá]rbol de la vida|metepec|iz[uú]car"], node=r"Arbol de la vida", kw="tree of life Metepec", prof="folk",
  rows=[("Izúcar de Matamoros", "Centres & workshops", "Puebla town of brightly painted trees of life", "Izúcar de Matamoros", 0)],
  ov={"Arbol de la vida (Metepec tree of life)": "alias", "Metepec": ("Metepec", "Centres & workshops", "State of Mexico town, the leading centre of the trees of life")})
S("E1-56", pat=[r"pucar[aá]|pupuja"], node=r"Pucara bulls", kw="Pucara bull", prof="folk",
  rows=[("Pucará", "Centres & workshops", "town in Puno where the bulls are sold; Santiago de Pupuja makes them", "Pucará District, Lampa", 0)],
  ov={"Pucara bulls (toritos de Pucara)": "alias"})
S("E1-57", pat=[r"chulucanas"], node=r"Chulucanas", kw="Chulucanas", prof="folk",
  rows=[("Chulucanas", "Centres & workshops", "town in Piura whose ware has a Peruvian denomination of origin", "Chulucanas", 0)],
  ov={"Chulucanas pottery": "alias"})
S("E1-58", pat=[r"quinchamal"], node=r"Quinchamal", kw="Quinchamali", prof="folk",
  ich=("https://ich.unesco.org/en/USL/quinchamali-and-santa-cruz-de-cuca-pottery-01847", "UNESCO ICH: Quinchamalí and Santa Cruz de Cuca pottery", "Urgent Safeguarding List element (2022)"),
  rows=[("Guitarrera", "Sub-types", "figure of a peasant woman with a guitar, the emblem of Quinchamalí pottery", "Quinchamalí", 0),
        ("Quinchamalí", "Centres & workshops", "village near Chillán (Ñuble), Chile", "Quinchamalí", 0)],
  ov={"Quinchamalí and Santa Cruz de Cuca pottery": "alias"})
S("E1-59", pat=[r"awaj[uú]n|aguaruna"], node=r"Awaj", kw="Awajun", prof="folk",
  ich=("https://ich.unesco.org/en/RL/pottery-related-values-knowledge-lore-and-practices-of-the-awajun-people-01557", "UNESCO ICH: Pottery-related values, knowledge, lore and practices of the Awajún people", "Representative List element (2021)"),
  ov={"Awajún pottery": "alias"})
S("E1-60", pat=[r"goiabeiras"], node=r"Goiabeiras", kw="Goiabeiras", prof="folk",
  rows=[("Vitória", "Centres & workshops", "capital of Espírito Santo whose Goiabeiras district is home to the paneleiras", "Vitória, Espírito Santo", 0)],
  ov={"the craft of the clay pot makers of Goiabeiras": "alias"})
