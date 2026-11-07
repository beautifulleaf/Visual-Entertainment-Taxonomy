# Spec part C: E3 (stoneware) and E4 (porcelain)
from spec_lib import S
JP = r"japan|日本|江戸|室町|鎌倉|桃山|安土|明治|平安|momoyama|\bedo\b|muromachi|kamakura|meiji|heian|nanbokucho"
CN = r"china|chinese|中国|宋|元|明|清|唐|五代|\bsong\b|\byuan\b|\bming\b|\bqing\b|\btang\b|northern song|southern song|jin dynasty"
S("E3-1", pat=[(r"khmer|angkor|buriram", r"ceram|stoneware|glaz|pott|jar|jarlet|vessel")], kw="Khmer ceramics", prof="seasia",
  rows=[("Phnom Kulen kilns", "Centres & workshops", "kilns near Angkor making pale green-glazed ware, 9th–11th c.", "Phnom Kulen", 0),
        ("Brown-glazed ware", "Sub-types", "iron-brown glazed jars and zoomorphic vessels, 11th–13th c.", "Khmer ceramics", 0)],
  ov={"Buriram kilns": ("Buriram kilns", "Centres & workshops", "Angkorian kiln sites of Buriram Province, north-east Thailand, 11th–13th c.")})
S("E3-2", pat=[r"sawankhalok|satchanalai|ko noi|pa yang"], kw="Sawankhalok", prof="seasia",
  rows=[("Si Satchanalai", "Centres & workshops", "Sukhothai-period city; part of the UNESCO site Historic Town of Sukhothai and Associated Historic Towns", "Si Satchanalai Historical Park", 0)],
  ov={"Thai: Sawankhalok ware": "alias", "Thai, Si Satchanalai": "alias",
      "Ko Noi": ("Ko Noi", "Centres & workshops", "kiln site on the Yom river, celadons and underglaze-black ware"),
      "Pa Yang": ("Pa Yang", "Centres & workshops", "Ban Pa Yang kilns near Si Satchanalai"),
      "Sukhothai kilns": ("Sukhothai kilns", "Sub-types", "related iron-painted ware made at Sukhothai itself")})
S("E3-3", pat=[(r"vietnam|annam|b[aá]t tr[aà]ng|chu [dđ][aậ]u|hai duong|h[aả]i d[uư][oơ]ng", r"ceram|stoneware|porcelain|glaz|pott|jar|dish|bowl")], excl=r"\bch[aă]m\b", kw="Vietnamese ceramics", prof="seasia",
  rows=[("Topkapı vase", "W", "Vietnamese blue-and-white bottle dated 1450 by the potter Bùi Thị Hý; Topkapı Palace Museum, Istanbul", "Vietnamese ceramics", 0)],
  ov={"Bat Trang ceramics": ("Bát Tràng", "Centres & workshops", "village near Hanoi making ceramics since the 14th c."),
      "Hải Dương (Chu Đậu) kilns": ("Chu Đậu kilns", "Centres & workshops", "Hải Dương kilns of 15th–16th c. export blue-and-white"),
      "Lý–Trần wares": ("Lý–Trần wares", "Schools & phases", "white, brown and green wares of the Lý and Trần dynasties, 11th–14th c.")})
S("E3-4", pat=[r"越窯|越州窯|越州|\byue\b|秘色"], kw="Yue ware", prof="china", zh="越窯",
  rows=[("Shanglinhu kilns", "Centres & workshops", "Shanglin Lake kilns near Cixi, Zhejiang, the core of Yue production", "Yue ware", 0),
        ("Famen Temple mise ware", "W", "secret-colour bowls from the crypt of Famen Temple, sealed 874; Famen Temple Museum", "Famen Temple", 0)],
  ov={"Mise (secret-colour ware)": ("Mise (secret-colour ware)", "Sub-types", "the finest Yue ware reserved for the court, 9th–10th c."),
      "Chicken-head ewers": ("Chicken-head ewers", "Sub-types", "early Yue ewers with a cockerel-head spout, 4th–6th c.")})
S("E3-5", pat=[r"耀州|yaozhou|yao-chou|黄堡"], kw="Yaozhou", prof="china", zh="耀州窯",
  rows=[("Huangbao", "Centres & workshops", "kiln town in Tongchuan, Shaanxi; the Yaozhou Kiln Museum", "Yaozhou ware", 0),
        ("Carved celadon", "Sub-types", "Northern Song bowls deeply carved with peonies under olive glaze", "Yaozhou ware", 0)])
S("E3-6", pat=[r"龍泉|龙泉|longquan|砧青磁|kinuta|天龍寺青磁|七官青磁"], node=r"Longquan", kw="Longquan celadon", prof="china", zh="龍泉窯",
  ich=("https://ich.unesco.org/en/RL/traditional-firing-technology-of-longquan-celadon-00205", "UNESCO ICH: Traditional firing technology of Longquan celadon", "Representative List element (2009)"),
  rows=[("Kinuta celadon", "Sub-types", "bluish Southern Song Longquan, Japanese 'mallet' type", "Longquan celadon", 0),
        ("Tenryūji celadon", "Sub-types", "yellower Yuan–Ming Longquan in Japanese classification", "Longquan celadon", 0),
        ("Bakōhan", "W", "Southern Song Longquan tea bowl repaired with staples, Muromachi legend; Tokyo National Museum", "Bakōhan", 0)],
  ov={"Longquan celadon": "alias"})
S("E3-7", pat=[r"汝窯|汝窑|汝官窯|\bru ware|\bru-type|\bru kiln"], kw="Ru ware", prof="china", zh="汝窯",
  rows=[("Qingliangsi", "Centres & workshops", "kiln site in Baofeng county, Henan, identified as the Ru kiln in 1986", "Ru ware", 0),
        ("Narcissus basin", "W", "Ru ware oval basin, Northern Song; National Palace Museum, Taipei", "Ru ware", 0),
        ("Percival David Collection", "Centres & workshops", "London collection (now in the British Museum) with seven Ru pieces", "Percival David Foundation of Chinese Art", 0)])
S("E3-8", pat=[r"官窯|官窑|guan ware|guan-type|\bguan\b|郊壇|修内司"], excl=r"汝|哥窯", kw="Guan ware", prof="china", zh="官窯",
  rows=[("Ge ware", "Sub-types", "crackled 'elder brother' ware closely related to Guan", "Ge ware", 0),
        ("Jiaotanxia kiln", "Centres & workshops", "Southern Song official kiln at the Altar of Heaven, Hangzhou; Southern Song Guan Kiln Museum", "Guan ware", 0),
        ("Xiuneisi kiln", "Centres & workshops", "the earlier Southern Song palace kiln at Laohudong, Hangzhou", "Guan ware", 0)])
S("E3-9", pat=[r"鈞窯|钧窑|鈞|钧|jun ware|\bjun\b|chün"], kw="Jun ware", prof="china", zh="鈞窯",
  rows=[("Numbered Jun", "Sub-types", "flowerpots and stands with incised numerals, for the court", "Jun ware", 0),
        ("Yuzhou (Juntai)", "Centres & workshops", "Henan city whose Juntai and Shenhou kilns are the core Jun sites", "Yuzhou, Henan", 0)])
S("E3-10", pat=[r"建窯|建盞|曜変|油滴|禾目|jian ware|\bjian\b|hare.s.fur|oil.spot", (r"天目|tenmoku|temmoku", CN)], kw="Jian ware", prof="china", zh="建窯", jp="建盞",
  rows=[("Yōhen tenmoku", "Sub-types", "Jian bowls with iridescent spots; three survive, all National Treasures in Japan", "Yōhen tenmoku", 0),
        ("Inaba Tenmoku", "W", "yōhen tenmoku tea bowl, Southern Song; Seikadō Bunko Art Museum, Tokyo; National Treasure", "Yōhen tenmoku", 0),
        ("Jianyang", "Centres & workshops", "Fujian county whose Shuiji kilns made the bowls", "Jianyang, Nanping", 0)],
  ov={"Hare's-fur and oil-spot bowls": ("Hare's-fur and oil-spot bowls", "Sub-types", "the two classic Jian glaze effects, streaked and silver-spotted")})
S("E3-11", pat=[r"磁州|cizhou|tz.u.chou"], kw="Cizhou ware", prof="china", zh="磁州窯",
  rows=[("Guantai", "Centres & workshops", "kiln site near Handan, Hebei", "Cizhou ware", 0),
        ("Pengcheng", "Centres & workshops", "Handan town, the main later Cizhou centre", "Cizhou ware", 0),
        ("Cizhou pillows", "Sub-types", "ceramic headrests painted with poems and scenes", "Cizhou ware", 0)])
S("E3-12", pat=[r"宜興|宜兴|yixing|紫砂|i-hsing|zisha"], kw="Yixing", prof="china", zh="宜興",
  rows=[("Gong Chun", "Makers", "legendary first Yixing teapot maker, early 16th c.", "Gong Chun", 1),
        ("Shi Dabin", "Makers", "late Ming Yixing master, c. 1573–1648", "Shi Dabin", 1),
        ("Chen Mingyuan", "Makers", "Kangxi-era maker of naturalistic Yixing pots", "Chen Mingyuan", 1),
        ("Gu Jingzhou", "Makers", "20th-c. Yixing master, 1915–1996", "Gu Jingzhou", 1)],
  ov={"Yixing zisha ware": "alias"})
S("E3-13", pat=[(r"goryeo|koryo|koryŏ|高麗|고려", r"celadon|青磁|청자|inlaid|sanggam|象嵌")], kw="Goryeo celadon", prof="korea", jp="高麗青磁",
  rows=[("Sanggam", "Sub-types", "inlaid celadon with black and white clay, Goryeo's own invention, 12th c.", "Korean pottery", 0),
        ("Gangjin kilns", "Centres & workshops", "South Jeolla kilns of the finest Goryeo celadon; Gangjin Celadon Museum", "Gangjin County", 0),
        ("Buan kilns", "Centres & workshops", "North Jeolla kilns of inlaid celadon", "Buan County", 0)])
S("E3-14", pat=[r"粉青|분청|buncheong|punch.?ong|三島|mishima|刷毛目|hakeme|粉引|kohiki"], kw="buncheong", prof="korea", jp="粉青",
  rows=[("Gyeryongsan buncheong", "Sub-types", "iron-painted buncheong of Gyeryongsan, South Chungcheong", "Buncheong", 0)],
  ov={"Mishima": ("Mishima", "Sub-types", "stamped and inlaid buncheong, so named by Japanese tea masters"),
      "Kohiki": ("Kohiki", "Sub-types", "buncheong dipped all over in white slip"),
      "Hakeme": ("Hakeme", "Sub-types", "buncheong with brushed white slip")})
S("E3-15", pat=[(r"瀬戸|\bseto\b", JP)], excl=r"瀬戸内", kw="Seto ware", prof="japan", jp="瀬戸",
  rows=[("Ko-Seto", "Schools & phases", "medieval glazed Seto ware imitating Chinese celadon, 13th–15th c.", "Seto ware", 0)],
  ov={"Ki-Seto": ("Ki-Seto", "Sub-types", "'yellow Seto', Mino ware with a pale yellow ash glaze, Momoyama period"),
      "Setoguro": ("Setoguro", "Sub-types", "'Seto black' tea bowls pulled from the kiln, Mino, Momoyama period"),
      "Seto sometsuke (blue-and-white)": ("Seto sometsuke", "Sub-types", "Seto blue-and-white porcelain, from 1807"),
      "Katō Shirōzaemon (Tōshirō)": ("Katō Shirōzaemon (Tōshirō)", "Makers", "legendary founder of Seto glazed ware, 13th c.", None, 1)})
S("E3-16", pat=[r"志野|shino"], node=r"Shino", kw="Shino ware", prof="japan", jp="志野",
  rows=[("E-Shino", "Sub-types", "Shino with iron-painted designs under the glaze", "Shino ware", 0),
        ("Nezumi-Shino", "Sub-types", "'grey Shino' with designs scratched through iron slip", "Shino ware", 0),
        ("Unohanagaki", "W", "Shino tea bowl, Momoyama period; Mitsui Memorial Museum, Tokyo; National Treasure", "Shino ware", 0),
        ("Arakawa Toyozō", "Makers", "potter who rediscovered Momoyama Shino kiln sites; Living National Treasure, 1894–1985", "Arakawa Toyozō", 1)],
  ov={"Shino ware": "alias"})
S("E3-17", pat=[r"織部|oribe"], kw="Oribe ware", prof="japan", jp="織部",
  rows=[("Ao-Oribe", "Sub-types", "'green Oribe' with copper-green glaze and iron painting", "Oribe ware", 0),
        ("Narumi-Oribe", "Sub-types", "red and white clays joined under green glaze", "Oribe ware", 0),
        ("Kuro-Oribe", "Sub-types", "black-glazed Oribe tea bowls with painted panels", "Oribe ware", 0),
        ("Motoyashiki kiln", "Centres & workshops", "climbing kiln at Toki where Oribe was made; National Historic Site", "Oribe ware", 0),
        ("Furuta Oribe", "Makers", "warrior and tea master whose taste named the ware, 1544–1615", "Furuta Oribe", 1)])
S("E3-18", pat=[r"備前|bizen|伊部"], kw="Bizen ware", prof="japan", jp="備前",
  rows=[("Hidasuki", "Sub-types", "'fire cord' red scorch lines left by straw wrapping", "Bizen ware", 0),
        ("Kaneshige Tōyō", "Makers", "Bizen revivalist; Living National Treasure, 1896–1967", "Kaneshige Tōyō", 1),
        ("Fujiwara Kei", "Makers", "Bizen potter; Living National Treasure, 1899–1983", "Fujiwara Kei", 1)],
  ov={"Bizen ware": "alias", "Bizen": "alias",
      "Yaheita": ("Yaheita", "Makers", "Bizen potter name recorded on figure and vessel pieces in the Rijksmuseum", None, 1)})
S("E3-19", pat=[r"信楽|shigaraki"], kw="Shigaraki ware", prof="japan", jp="信楽",
  rows=[("Six Ancient Kilns", "Sub-types", "Japan's medieval kiln group (Seto, Tokoname, Echizen, Shigaraki, Tamba, Bizen)", "Six Ancient Kilns", 0),
        ("Tanuki figures", "Sub-types", "raccoon-dog figures set outside shops, Shigaraki's best-known modern product", "Japanese raccoon dog", 0)])
S("E3-20", pat=[r"伊賀|\biga\b"], excl=r"伊賀上野", kw="Iga ware", prof="japan", jp="伊賀",
  rows=[("Iga Ueno", "Centres & workshops", "Mie castle town near the Iga kilns at Marubashira", "Iga, Mie", 0)])
S("E3-21", pat=[(r"丹波|\btamba|tanba|立杭|tachikui", JP)], kw="Tamba ware", prof="japan", jp="丹波",
  rows=[("Tachikui", "Centres & workshops", "Sasayama village of the Tamba kilns, in Hyōgo", "Tamba-Sasayama", 0)])
S("E3-22", pat=[r"常滑|tokoname"], kw="Tokoname ware", prof="japan", jp="常滑",
  rows=[("Tokoname kyūsu", "Sub-types", "unglazed red-clay side-handled teapots", "Tokoname ware", 0),
        ("Tokoname", "Centres & workshops", "city on the Chita peninsula, Aichi", "Tokoname", 0)])
S("E3-23", pat=[r"越前|echizen"], excl=r"越前国|越前守", kw="Echizen ware", prof="japan", jp="越前焼",
  rows=[("Echizen (Fukui)", "Centres & workshops", "the Ozowara kilns in Echizen town, Fukui", "Echizen, Fukui (town)", 0)])
S("E3-24", pat=[r"唐津|karatsu"], kw="Karatsu ware", prof="japan", jp="唐津",
  rows=[("E-Garatsu", "Sub-types", "iron-painted Karatsu", "Karatsu ware", 0),
        ("Madara-Garatsu", "Sub-types", "Karatsu with mottled straw-ash glaze", "Karatsu ware", 0),
        ("Chōsen-Garatsu", "Sub-types", "'Korean Karatsu' with black and white glazes run together", "Karatsu ware", 0),
        ("Nakazato Tarōemon XII", "Makers", "Karatsu potter; Living National Treasure, 1895–1985", "Nakazato Tarōemon", 1)])
S("E3-25", pat=[r"萩焼|萩茶|hagi"], kw="Hagi ware", prof="japan", jp="萩",
  rows=[("Miwa Kyūsetsu X", "Makers", "Hagi potter; Living National Treasure, 1895–1981", "Miwa Kyūsetsu", 1),
        ("Hagi", "Centres & workshops", "castle town in Yamaguchi, seat of the Mōri lords' kiln", "Hagi, Yamaguchi", 0)],
  ov={"Hagi ware": "alias"})
S("E3-26", pat=[r"高取|takatori"], kw="Takatori ware", prof="japan", jp="高取",
  rows=[("Takatori Hachizō", "Makers", "Korean potter who founded Takatori ware for the Kuroda lords, early 17th c.", "Takatori ware", 1)])
S("E3-27", pat=[r"上野焼|上野茶|agano"], kw="Agano ware", prof="japan", jp="上野焼",
  rows=[("Sonkai (Agano Kizō)", "Makers", "Korean potter who founded Agano ware for Hosokawa Tadaoki, 1602", "Agano ware", 1)])
S("E3-28", pat=[r"京焼|仁清|乾山|\bkyo[- ]?ware|\bkyō[- ]ware|kyo-yaki|kiyomizu|清水焼|awata|粟田|ninsei|kenzan|mokubei|木米|dohachi|道八|eiraku|永楽|rengetsu|蓮月|mizoro"], kw="Kyo ware", prof="japan", jp="京焼",
  rows=[("Nonomura Ninsei", "Makers", "founder of enamelled Kyō ware at Omuro, active 1640s–1690s", "Nonomura Ninsei", 1),
        ("Ogata Kenzan", "Makers", "painter-potter of Narutaki and Nijō Chōjiya, 1663–1743", "Ogata Kenzan", 1),
        ("Okuda Eisen", "Makers", "first Kyoto maker of porcelain, 1753–1811", "Okuda Eisen", 1),
        ("Aoki Mokubei", "Makers", "literati potter of Chinese-style wares, 1767–1833", "Aoki Mokubei", 1),
        ("Eiraku Hozen", "Makers", "Kyoto potter of kinrande and kōchi wares, 1795–1854", "Eiraku Hozen", 1),
        ("Nin'ami Dōhachi", "Makers", "Kyoto potter of overglaze and raku wares, 1783–1855", "Nin'ami Dōhachi", 1)],
  ov={"Awata ware": ("Awata ware", "Centres & workshops", "Kyoto kilns of the Awataguchi district, overglaze-enamelled ware, from the 17th c."),
      "Kiyomizu ware": ("Kiyomizu ware", "Centres & workshops", "kilns of the Gojōzaka–Kiyomizu district, the main Kyoto centre"),
      "Mizoro ware": ("Mizoro ware", "Centres & workshops", "small Kyoto kiln of the 17th c. near Mizorogaike"),
      "Otagaki Rengetsu": ("Otagaki Rengetsu", "Makers", "Buddhist nun and poet who inscribed her waka on her own wares, 1791–1875", None, 1)})
S("E3-29", pat=[r"小鹿田|\bonta\b(?! \w*indian)"], excl=r"montana|native american|ontario", kw="Onta ware", prof="japan", jp="小鹿田",
  rows=[("Tobikanna", "Sub-types", "'chattering' — rhythmic notches cut with a trembling blade", "Onta ware", 0),
        ("Sarayama", "Centres & workshops", "the Onta potters' hamlet in Hita, Ōita", "Onta ware", 0)],
  ov={"Onta ware": "alias"})
S("E3-30", pat=[r"小石原|koishiwara"], kw="Koishiwara ware", prof="japan", jp="小石原",
  rows=[("Tōhō", "Centres & workshops", "village in Fukuoka where the Koishiwara kilns stand", "Tōhō, Fukuoka", 0)],
  ov={"Koishiwara ware": "alias"})
S("E3-31", pat=[r"無名異|mumy"], kw="Mumyoi ware", prof="japan", jp="無名異",
  rows=[("Itō Sekisui V", "Makers", "Sado potter; Living National Treasure for mumyōi ware, b. 1941", "Itō Sekisui V", 1)],
  ov={"Mumyōi ware": "alias"})
S("E3-32", pat=[(r"siegburg|raeren|frechen|cologne|köln|westerwald|bartmann|bellarmine|höhr|grenzhausen|rhenish|rhineland", r"stoneware|salt.glaz|jug|tankard|pott|ceram")], node=r"rhenish_stoneware", kw="Rhenish stoneware", prof="europe",
  met=["German, Westerwald"],
  rows=[("Siegburg", "Centres & workshops", "centre of white stoneware Schnellen, 16th c.", "Siegburg", 0),
        ("Raeren", "Centres & workshops", "brown salt-glazed jugs, the Mennicken workshops, 16th c.", "Raeren", 0),
        ("Frechen", "Centres & workshops", "main producer of Bartmann jugs for export, 16th–17th c.", "Frechen", 0),
        ("Bartmann jug", "Sub-types", "salt-glazed jug with a bearded mask, 'Bellarmine' in English", "Bellarmine", 0),
        ("Jan Emens Mennicken", "Makers", "Raeren potter of relief friezes, fl. 1566–1594", "Jan Emens Mennicken", 1)],
  ov={"Rhenish stoneware": "alias",
      "Pottery Tradition of Westerwald’s Stoneware in Höhr-Grenzhausen and Breitscheid": ("Westerwald", "Centres & workshops", "Höhr-Grenzhausen and Breitscheid, grey-and-blue stoneware since the 16th c.")})
S("E3-33", pat=[r"萬古|万古|banko"], excl=r"bankole|bankoni", kw="Banko ware", prof="japan", jp="萬古",
  rows=[("Nunami Rōzan", "Makers", "Ise merchant who founded Banko ware, 1718–1777", "Banko ware", 1),
        ("Yokkaichi", "Centres & workshops", "Mie city, the modern centre of Banko donabe and teapots", "Yokkaichi", 0)],
  ov={"Banko ware (Banko-yaki)": ("Donabe", "Sub-types", "heat-resistant clay casserole, Banko's main modern product · Possession: Donabe (B5)")})
S("E3-34", pat=[(r"美濃|\bmino\b", JP)], kw="Mino ware", prof="japan", jp="美濃",
  rows=[("Tajimi", "Centres & workshops", "Gifu city at the heart of the Mino kilns", "Tajimi", 0),
        ("Toki", "Centres & workshops", "Gifu city of the Motoyashiki and other Momoyama kilns", "Toki, Gifu", 0)],
  ov={"Mino ware": ("Shino", "Sub-types", "white-glazed Mino tea ware of the Momoyama period · Possession: Shino (B5)")})

S("E4-1", pat=[r"bencharong|benjarong|lai nam thong"], node=r"Bencharong", kw="Bencharong", prof="seasia",
  rows=[("Lai nam thong", "Sub-types", "Bencharong with gold added to the enamels, for the Siamese court", "Bencharong", 0)],
  ov={"Bencharong porcelain": "alias"})
S("E4-2", pat=[(r"定窯|定窑|\bding\b|ting ware", CN)], kw="Ding ware", prof="china", zh="定窯",
  rows=[("Jiancicun", "Centres & workshops", "kiln site at Quyang, Hebei", "Ding ware", 0),
        ("Black Ding", "Sub-types", "rare black- and brown-glazed Ding ware", "Ding ware", 0)],
  ov={"Ding ware": "alias"})
S("E4-3", pat=[(r"邢窯|邢州|xing ware|\bxing\b", CN)], kw="Xing ware", prof="china", zh="邢窯",
  rows=[("Neiqiu", "Centres & workshops", "Hebei county of the main Xing kiln sites", "Xing ware", 0)])
S("E4-4", pat=[r"青白磁|青白瓷|影青|qingbai|yingqing|ch.ing-?pai"], kw="qingbai", prof="china", zh="青白",
  rows=[("Hutian kiln", "Centres & workshops", "Jingdezhen kiln site of the finest Song qingbai", "Qingbai ware", 0),
        ("Fonthill Vase", "W", "Yuan qingbai vase, the first Chinese porcelain known in Europe (1338); National Museum of Ireland, Dublin", "Fonthill Vase", 0)])
S("E4-5", pat=[(r"青花|blue.and.white|underglaze blue|染付|cobalt", CN)], excl=r"kraak|芙蓉手|export|呉須|swatow|japan|日本|伊万里", kw="Chinese blue and white porcelain", prof="china", zh="青花",
  rows=[("David Vases", "W", "pair of Yuan blue-and-white temple vases dated 1351; British Museum, London", "David Vases", 0),
        ("Yuan blue-and-white", "Schools & phases", "the first mature phase, Jingdezhen, c. 1320–1368", "Blue and white pottery", 0),
        ("Xuande blue-and-white", "Schools & phases", "classic imperial blue-and-white of the Xuande reign, 1426–1435", "Blue and white pottery", 0)],
  ov={"Transitional porcelain": ("Transitional porcelain", "Schools & phases", "Jingdezhen ware of c. 1620–1683 between Ming and Qing imperial control"),
      "Tianqi porcelain (ko-sometsuke)": ("Tianqi porcelain (ko-sometsuke)", "Schools & phases", "rough-edged blue-and-white of the 1620s made for the Japanese tea market")})
S("E4-6", pat=[r"鬥彩|闘彩|鬭彩|doucai|tou-?ts.ai|chicken cup"], kw="doucai", prof="china", zh="鬥彩",
  rows=[("Chenghua doucai", "Schools & phases", "the classic doucai of the Chenghua reign, 1465–1487", "Chenghua Emperor", 0)],
  ov={"Chicken cups": ("Chicken cups", "Sub-types", "small Chenghua doucai wine cups with hens and chicks")})
S("E4-7", pat=[(r"五彩|wucai|wu-?ts.ai", r"明|ming|万暦|萬暦|嘉靖|wanli|jiajing|china|中国")], excl=r"康熙|kangxi|famille|日本|japan|伊万里", kw="wucai", prof="china", zh="五彩",
  rows=[("Jiajing wucai", "Schools & phases", "imperial wucai of the Jiajing reign, 1522–1566", "Wucai", 0),
        ("Wanli wucai", "Schools & phases", "dense imperial wucai of the Wanli reign, 1573–1620", "Wucai", 0)])
S("E4-8", pat=[r"famille verte|康熙五彩|famille noire|famille jaune"], kw="famille verte", prof="china", zh="康熙 五彩",
  ov={"Famille jaune": ("Famille jaune", "Sub-types", "famille verte on a yellow ground"),
      "Famille noire": ("Famille noire", "Sub-types", "famille verte on a black ground, much prized in the 19th c.")})
S("E4-9", pat=[r"famille rose|粉彩|琺瑯彩|珐琅彩|fencai|falangcai|yangcai|洋彩"], kw="famille rose", prof="china", zh="粉彩",
  rows=[("Tang Ying", "Makers", "superintendent of the Jingdezhen imperial kilns, 1682–1756", "Tang Ying", 1)],
  ov={"Falangcai": ("Falangcai", "Sub-types", "palace-enamelled porcelain painted in Beijing on Jingdezhen blanks, Kangxi–Qianlong"),
      "Yangcai": ("Yangcai", "Sub-types", "'foreign colours', Jingdezhen famille rose with European-derived enamels")})
S("E4-10", pat=[r"景德鎮|景德镇|景徳鎮|jingdezhen|ching-?te-?chen"], excl=r"青花|blue.and.white|kraak|famille|doucai|wucai|五彩|粉彩|青白|qingbai|underglaze blue|cobalt|export", kw="Jingdezhen", prof="china", zh="景德鎮",
  rows=[("Imperial kilns of Jingdezhen", "Centres & workshops", "the Imperial Ware Factory at Zhushan, 1369–1911", "Jingdezhen", 0),
        ("Langyao (sang de boeuf)", "Sub-types", "copper-red glaze of the Kangxi supervisor Lang Tingji", "Sang de boeuf glaze", 0)],
  ov={"Peachbloom glaze": ("Peachbloom glaze", "Sub-types", "mottled pink copper-red monochrome for scholars' objects, Kangxi"),
      "Robin's-egg glaze": ("Robin's-egg glaze", "Sub-types", "speckled turquoise-blue monochrome, Yongzheng–Qianlong"),
      "Tea-dust glaze": ("Tea-dust glaze", "Sub-types", "iron-crystalline green-brown monochrome"),
      "Underglaze red": ("Underglaze red", "Sub-types", "copper-red painting under the glaze, Hongwu and Xuande"),
      "Anhua decoration": ("Anhua decoration", "Sub-types", "'secret' incised or slip decoration visible only against light")})
S("E4-11", pat=[r"kraak|芙蓉手|carrack"], kw="kraak porcelain", prof="china", zh="克拉克",
  rows=[("Witte Leeuw", "W", "Dutch East Indiaman sunk off St Helena in 1613 with a cargo of kraak; Rijksmuseum, Amsterdam", "Witte Leeuw", 0)],
  ov={"Kraak porcelain": "alias"})
S("E4-12", pat=[r"swatow|zhangzhou|漳州|呉須赤絵|呉須染付|gosu"], kw="Swatow", prof="china", zh="漳州窯",
  rows=[("Pinghe kilns", "Centres & workshops", "Zhangzhou kiln sites in Pinghe county, Fujian", "Swatow ware", 0),
        ("Gosu-akae", "Sub-types", "Zhangzhou red-and-green enamelled ware prized in Japan", "Swatow ware", 0)])
S("E4-13", pat=[(r"export|chine de commande|armorial|canton|rose medallion|rose mandarin|jesuit", r"china|chinese|中国|canton|jingdezhen")], kw="Chinese export porcelain", prof="china", zh="外銷",
  met=["Chinese, Export"],
  rows=[("Nanking Cargo", "W", "porcelain from the Geldermalsen, sunk 1752, sold at Christie's 1986", "Nanking Cargo", 0)],
  ov={"Chinese, Export": "alias",
      "Canton porcelain": ("Canton porcelain", "Centres & workshops", "Jingdezhen blanks enamelled in Guangzhou for the trade"),
      "Rose Medallion": ("Rose Medallion", "Sub-types", "Canton famille rose pattern of figure and bird panels"),
      "Rose Mandarin": ("Rose Mandarin", "Sub-types", "Canton pattern of mandarin figures"),
      "Armorial porcelain": ("Armorial porcelain", "Sub-types", "services painted with European coats of arms"),
      "Jesuit porcelain": ("Jesuit porcelain", "Sub-types", "Christian subjects in grisaille after European prints"),
      "Chine de commande with Dutch decoration": ("Chine de commande with Dutch decoration", "Sub-types", "Chinese porcelain decorated (often over-decorated) in the Netherlands")})
S("E4-14", pat=[r"德化|徳化|dehua|blanc de chine|te-?hua"], kw="blanc de Chine", prof="china", zh="德化",
  rows=[("Guanyin figures", "Sub-types", "white figures of the bodhisattva, the classic Dehua subject", "Dehua porcelain", 0)],
  ov={"Blanc de Chine": "alias", "He Chaozong": ("He Chaozong", "Makers", "late Ming Dehua modeller of Buddhist figures, signed with seals", None, 1)})
S("E4-15", pat=[(r"joseon|chos[oŏ]n|朝鮮|조선", r"白磁|백자|white porcelain|porcelain|青花|染付|청화")], excl=r"粉青|분청|buncheong|三島", kw="Joseon porcelain", prof="korea", jp="朝鮮 白磁",
  rows=[("Moon jar", "Sub-types", "large round white jar of the 17th–18th c.", "Moon jar", 0),
        ("Bunwon", "Centres & workshops", "the royal kiln at Gwangju, Gyeonggi province", "Gwangju, Gyeonggi", 0)],
  ov={"Sagijang": ("Sagijang", "Sub-types", "the craft of porcelain making, Korea's National Intangible Cultural Heritage"),
      "Cheonghwa baekja (blue-and-white)": ("Cheonghwa baekja (blue-and-white)", "Sub-types", "Joseon blue-and-white, from the 15th c.")})
S("E4-16", pat=[r"有田|伊万里|arita|imari|金襴手|kinrande"], excl=r"柿右衛門|kakiemon|鍋島|nabeshima", kw="Imari", prof="japan", jp="伊万里", met=["Japanese, Export"],
  rows=[("Shoki-Imari", "Schools & phases", "early Arita blue-and-white, c. 1610–1640s", "Imari ware", 0),
        ("Ko-Imari", "Schools & phases", "'old Imari' export ware in underglaze blue, red and gold, late 17th–18th c.", "Imari ware", 0),
        ("Ri Sampei", "Makers", "Korean potter credited with finding porcelain stone at Izumiyama, d. 1655", "Yi Sam-pyeong", 1),
        ("Izumiyama quarry", "Centres & workshops", "Arita porcelain-stone quarry discovered c. 1616", "Arita ware", 0)],
  ov={"Japanese, Export": "alias", "Imari ware": "alias", "Arita ware": "alias",
      "Kinrande": ("Kinrande", "Sub-types", "'gold brocade' Imari with dense red and gold")})
S("E4-17", pat=[r"柿右衛門|kakiemon"], kw="Kakiemon", prof="japan", jp="柿右衛門",
  rows=[("Nigoshide", "Sub-types", "the milky-white body that sets off Kakiemon enamels", "Kakiemon", 0),
        ("Sakaida Kakiemon I", "Makers", "founder of the family style, credited with the first overglaze enamels at Arita, 1596–1666", "Sakaida Kakiemon", 1)],
  ov={"Kakiemon": "alias", "Sakaida Kakiemon XV": ("Sakaida Kakiemon XV", "Makers", "present head of the Kakiemon kiln, b. 1968", None, 1)})
S("E4-18", pat=[r"鍋島|nabeshima"], kw="Nabeshima ware", prof="japan", jp="鍋島",
  rows=[("Iro-Nabeshima", "Sub-types", "Nabeshima in underglaze blue with overglaze red, yellow and green", "Nabeshima ware", 0),
        ("Ōkawachi", "Centres & workshops", "the clan kiln village near Imari", "Nabeshima ware", 0),
        ("Imaizumi Imaemon XIII", "Makers", "Iro-Nabeshima potter; Living National Treasure, 1926–2001", "Imaizumi Imaemon XIII", 1)],
  ov={"Nabeshima ware": "alias"})
S("E4-19", pat=[r"平戸|三川内|hirado|mikawachi"], kw="Hirado ware", prof="japan", jp="三川内",
  rows=[("Mikawachi", "Centres & workshops", "kiln village in Sasebo, Nagasaki", "Hirado ware", 0),
        ("Karako design", "Sub-types", "Chinese boys playing under pines, the classic Hirado motif", "Hirado ware", 0)])
S("E4-20", pat=[r"九谷|kutani"], kw="Kutani ware", prof="japan", jp="九谷",
  rows=[("Ko-Kutani", "Schools & phases", "bold 17th-c. enamelled porcelain; its Kutani origin is debated", "Kutani ware", 0),
        ("Yoshidaya kiln", "Centres & workshops", "revival kiln of 1824–1831 in deep green and yellow", "Kutani ware", 0),
        ("Kutani Shōza", "Makers", "Meiji decorator of red-and-gold export Kutani, 1816–1883", "Kutani Shōza", 1),
        ("Tokuda Yasokichi III", "Makers", "Kutani potter of saiyū glazes; Living National Treasure, 1933–2009", "Tokuda Yasokichi III", 1)],
  ov={"Kutani ware": "alias"})
S("E4-21", pat=[(r"limoges", r"porcelain")], kw="Limoges porcelain", prof="europe",
  rows=[("Bernardaud", "Centres & workshops", "Limoges porcelain firm, founded 1863", "Bernardaud", 0),
        ("Saint-Yrieix-la-Perche", "Centres & workshops", "town south of Limoges where kaolin was found in 1768", "Saint-Yrieix-la-Perche", 0)],
  ov={"Limoges porcelain": "alias", "Haviland & Co.": ("Haviland & Co.", "Centres & workshops", "American-owned Limoges firm founded 1842 by David Haviland")})
S("E4-22", pat=[r"gzhel|гжел"], kw="Gzhel", prof="europe",
  rows=[("Gzhel", "Centres & workshops", "village district south-east of Moscow", "Gzhel", 0)],
  ov={"Gzhel ceramics": "alias"})
S("E4-23", pat=[r"meissen|meißen|kändler|kandler|höroldt|horoldt|böttger|мейсен"], kw="Meissen", prof="europe", met=["German, Meissen"],
  rows=[("Johann Friedrich Böttger", "Makers", "alchemist who achieved European hard-paste porcelain, 1682–1719", "Johann Friedrich Böttger", 1),
        ("Böttger stoneware", "Sub-types", "red stoneware made at Meissen before porcelain, from 1708", "Böttger stoneware", 0),
        ("Swan Service", "W", "Kändler's table service for Count Brühl, 1737–1743; dispersed (Dresden and elsewhere)", "Swan Service", 0)],
  ov={"Johann Joachim Kändler": ("Johann Joachim Kändler", "Makers", "chief modeller at Meissen, 1706–1775", "r3 https://en.wikipedia.org/wiki/Johann_Joachim_K%C3%A4ndler", 1),
      "Johann Gregorius Höroldt": ("Johann Gregorius Höroldt", "Makers", "Meissen enamel painter and chinoiserie designer, 1696–1775", "r3 https://en.wikipedia.org/wiki/Johann_Gregorius_H%C3%B6roldt", 1)})
S("E4-24", pat=[(r"s[eè]vres|vincennes", r"porcelain|biscuit|ceram|vase|cup|plate|saucer|tea")], kw="Sevres porcelain", prof="europe", met=["French, Sèvres", "French, Vincennes"],
  rows=[("Jean-Claude Duplessis", "Makers", "goldsmith and designer of Vincennes–Sèvres forms, c. 1695–1774", "Jean-Claude Chambellan Duplessis", 1),
        ("Étienne Maurice Falconet", "Makers", "director of the Sèvres sculpture workshop, biscuit figures, 1716–1791", "Étienne Maurice Falconet", 1)],
  ov={"Vincennes": ("Vincennes", "Schools & phases", "1740–1756, the manufactory before its move to Sèvres"),
      "Alexandre Brachard": ("Alexandre Brachard", "Makers", "Sèvres modeller of biscuit medallions and figures", None, 1)})
S("E4-25", pat=[(r"soft.paste|chelsea|\bbow\b|worcester|derby|longton hall|caughley|saint.cloud|chantilly|mennecy|capodimonte|lowestoft|buen retiro", r"porcelain")], kw="soft-paste porcelain", prof="europe",
  ov={"Chelsea": ("Chelsea", "Centres & workshops", "London factory, c. 1745–1784, raised- , red- and gold-anchor periods"),
      "Worcester": ("Worcester", "Centres & workshops", "factory founded 1751, later Royal Worcester"),
      "Derby": ("Derby", "Centres & workshops", "factory founded c. 1750, later Royal Crown Derby"),
      "Bow": ("Bow", "Centres & workshops", "east London factory, c. 1747–1776, early bone-ash paste (Thomas Frye)"),
      "Longton Hall": ("Longton Hall", "Centres & workshops", "Staffordshire's first porcelain factory, 1750–1760"),
      "Caughley": ("Caughley", "Centres & workshops", "Shropshire factory of blue-printed ware, 1775–1799"),
      "Saint-Cloud": ("Saint-Cloud", "Centres & workshops", "early French soft-paste factory, c. 1690–1766"),
      "Chantilly": ("Chantilly", "Centres & workshops", "Prince de Condé's factory with Kakiemon-style decoration, 1730–1800"),
      "Mennecy": ("Mennecy", "Centres & workshops", "factory of the Duc de Villeroy, 1734–1806"),
      "Capodimonte": ("Capodimonte", "Centres & workshops", "Naples royal factory of Charles of Bourbon, 1743–1759")})
S("E4-26", pat=[(r"hard.paste|du paquier|nymphenburg|bustelli|\bkpm\b|berlin|fürstenberg|furstenberg|frankenthal|höchst|hochst|ludwigsburg|wallendorf|potschappel|doccia|ginori|cozzi|imperial porcelain|copenhagen|herend|gustavsberg|vienna", r"porcelain")],
  node=r"danish_copenhagen|russian_st_petersburg", kw="porcelain manufactory", prof="europe",
  met=["German, Nymphenburg", "German, Höchst", "Danish, Copenhagen", "Hungarian, Herend", "Austrian, Vienna"],
  ov={"Vienna (Du Paquier)": ("Vienna (Du Paquier)", "Centres & workshops", "Vienna factory founded by Claudius du Paquier, 1718, the second in Europe"),
      "Nymphenburg": ("Nymphenburg", "Centres & workshops", "Munich manufactory founded 1747, Bustelli's figures"),
      "Franz Anton Bustelli": ("Franz Anton Bustelli", "Makers", "Nymphenburg modeller of rococo commedia figures, 1723–1763", "r3 https://en.wikipedia.org/wiki/Franz_Anton_Bustelli", 1),
      "Berlin (KPM)": ("Berlin (KPM)", "Centres & workshops", "Royal Porcelain Manufactory, Berlin, from 1763"),
      "Fürstenberg": ("Fürstenberg", "Centres & workshops", "Brunswick factory on the Weser, founded 1747"),
      "Frankenthal": ("Frankenthal", "Centres & workshops", "Palatinate factory of the Hannongs, 1755–1800"),
      "Höchst": ("Höchst", "Centres & workshops", "Mainz electoral factory, 1746–1796, modeller J. P. Melchior"),
      "Ludwigsburg": ("Ludwigsburg", "Centres & workshops", "Württemberg ducal factory, 1758–1824"),
      "Wallendorf": ("Wallendorf", "Centres & workshops", "Thuringian factory founded 1764"),
      "Carl Thieme Potschappel": ("Carl Thieme Potschappel", "Centres & workshops", "Dresden decorating factory founded 1872"),
      "Doccia": ("Doccia", "Centres & workshops", "Ginori family factory near Florence, founded 1737"),
      "Cozzi": ("Cozzi", "Centres & workshops", "Venetian factory of Geminiano Cozzi, 1764–1812"),
      "Imperial Porcelain Factory, St Petersburg": ("Imperial Porcelain Factory, St Petersburg", "Centres & workshops", "Russian imperial manufactory founded 1744"),
      "Royal Copenhagen": ("Royal Copenhagen", "Centres & workshops", "Danish royal manufactory founded 1775, Flora Danica service"),
      "Herend": ("Herend", "Centres & workshops", "Hungarian manufactory founded 1826"),
      "Gustavsberg": ("Gustavsberg", "Centres & workshops", "Swedish porcelain and ceramics manufactory near Stockholm, founded 1825; Parian figures, later studio ware", None, 1)})
S("E4-27", pat=[r"波佐見|hasami"], kw="Hasami ware", prof="japan", jp="波佐見",
  rows=[("Hasami", "Centres & workshops", "town in Nagasaki prefecture with the Nakao-yama kilns", "Hasami, Nagasaki", 0),
        ("Kurawanka bowls", "Sub-types", "cheap thick blue-and-white rice bowls sold on Osaka river boats, Edo period", "Hasami ware", 0)],
  ov={"Hasami ware": ("Everyday bowls and plates", "Sub-types", "mass-produced Hasami tableware · Possession: everyday bowls and plates (B5)")})
