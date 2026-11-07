# Spec part B: E1-61 .. E1-98 and E2
from spec_lib import S
AM = "americas"
S("E1-61", pat=[r"ancestral pueblo|anasazi|basketmaker|mesa verde|\bchaco|kayenta|cibola|northern san juan|virgin branch"], kw="Ancestral Pueblo pottery", prof=AM,
  rows=[("Mesa Verde Black-on-white", "Sub-types", "carbon-painted white ware of the northern San Juan, c. 1200–1300", "Mesa Verde National Park", 0),
        ("Chaco Canyon", "Centres & workshops", "great-house centre of Chaco Black-on-white, c. 850–1150; UNESCO World Heritage Site", "Chaco Culture National Historical Park", 0)],
  ov={"possibly Ancestral Pueblo (Anasazi): Northern San Juan (archaeological) (attributed)": ("Northern San Juan (Mesa Verde) wares", "Sub-types", "white and grey wares of the Mesa Verde region"),
      "probably Ancestral Pueblo (Anasazi): Northern San Juan (archaeological) (attributed)": ("Northern San Juan (Mesa Verde) wares", "Sub-types", "white and grey wares of the Mesa Verde region"),
      "possibly Ancestral Pueblo (Anasazi): Cibola (archaeological) (attributed)": ("Cibola White Ware", "Sub-types", "mineral-painted white ware of the Zuni–Little Colorado region, c. 600–1300"),
      "probably Ancestral Pueblo (Anasazi): Cibola (archaeological) (attributed)": ("Cibola White Ware", "Sub-types", "mineral-painted white ware of the Zuni–Little Colorado region, c. 600–1300"),
      "probably Ancestral Pueblo (Anasazi): Chaco (archaeological) (attributed)": ("Chaco Black-on-white", "Sub-types", "hatched black-on-white ware of Chaco Canyon, c. 1050–1150"),
      "probably Ancestral Pueblo (Anasazi): Kayenta (archaeological) (attributed)": ("Kayenta wares", "Sub-types", "dense-painted black-on-white and polychromes of north-eastern Arizona, c. 1150–1300"),
      "probably Ancestral Pueblo (Anasazi): Rio Grande (archaeological) (attributed)": ("Rio Grande wares", "Sub-types", "Rio Grande white wares and glaze wares, c. 1150–1600"),
      "Ancestral Pueblo": "alias",
      "Basketmaker": ("Basketmaker phase", "Schools & phases", "Basketmaker III (c. 500–750) brought the first fired grey and painted pottery"),
      "Virgin Branch": ("Virgin Branch", "Schools & phases", "western Ancestral Puebloan branch of southern Utah and Nevada")})
S("E1-62", pat=[r"mimbres"], kw="Mimbres", prof=AM,
  rows=[("Mimbres Classic Black-on-white", "Schools & phases", "Style III, c. 1000–1130, bowls with figurative scenes, often 'killed' for burial", "Mimbres pottery", 0),
        ("Mimbres Boldface Black-on-white", "Schools & phases", "Style I–II, c. 750–1000, bold geometric designs", "Mimbres pottery", 0)],
  ov={"possibly Mogollon Tradition: Mimbres (archaeological culture) (attributed)": "alias",
      "probably Mogollon Tradition: Mimbres (archaeological culture) (attributed)": "alias", "Mimbres": "alias"})
S("E1-63", pat=[r"hohokam"], kw="Hohokam", prof=AM,
  rows=[("Sacaton Red-on-buff", "Schools & phases", "Sedentary-period type, c. 950–1150", "Hohokam", 0),
        ("Santa Cruz Red-on-buff", "Schools & phases", "Colonial-period type, c. 850–950", "Hohokam", 0),
        ("Snaketown", "Centres & workshops", "Hohokam village on the Gila River, the type site", "Snaketown", 0)],
  ov={"probably Hohokam Tradition (archaeological culture) (attributed)": "alias", "possibly Hohokam Tradition (archaeological culture) (attributed)": "alias"})
S("E1-64", pat=[r"salado|roosevelt red|gila polychrome|tonto polychrome|pinto polychrome"], kw="Salado polychrome", prof=AM,
  rows=[("Pinto Polychrome", "Sub-types", "the earliest Salado type, c. 1280–1330", "Salado culture", 0),
        ("Gila Polychrome", "Sub-types", "the most widespread type, c. 1300–1450", "Salado culture", 0),
        ("Tonto Polychrome", "Sub-types", "with red-slipped zones, c. 1350–1450", "Salado culture", 0),
        ("Tonto National Monument", "Centres & workshops", "Salado cliff dwellings in the Tonto Basin, Arizona", "Tonto National Monument", 0)],
  ov={"possibly Salado (archaeological culture) (attributed)": "alias"})
S("E1-65", pat=[r"casas grandes|paquim[eé]|ramos polychrome"], excl=r"mata ortiz", kw="Casas Grandes", prof=AM,
  rows=[("Ramos Polychrome", "Sub-types", "the finest Medio-period polychrome, c. 1280–1450", "Casas Grandes", 0),
        ("Paquimé", "Centres & workshops", "the Medio-period town in Chihuahua; UNESCO World Heritage Site", "Paquimé", 0)],
  ov={"probably Casas Grandes Tradition (archaeological culture) (attributed)": "alias"})
S("E1-66", pat=[r"\bpueblo\b|\bzuni\b|a:shiwi|\bkewa\b|santo domingo|\btaos\b|\bjemez\b|\blaguna\b|\bzia\b|\bisleta\b|tesuque|cochiti|ohkay|pojoaque|nambe|picuris|hawikku|san felipe"], node=r"Pueblo pottery",
  excl=r"ancestral|anasazi|acoma|\bhopi|ildefonso|santa clara|k.apovi|mimbres|mogollon|hohokam|basketmaker|casas grandes", kw="Pueblo pottery", prof=AM,
  rows=[("Cochiti Pueblo", "Centres & workshops", "Keresan pueblo, home of the storyteller figure", "Cochiti Pueblo, New Mexico", 0),
        ("Storyteller figures", "Sub-types", "seated clay figures covered with children, Cochiti, from 1964", "Helen Cordero", 0),
        ("Helen Cordero", "Makers", "Cochiti potter who created the storyteller figure, 1915–1994", "Helen Cordero", 1)],
  ov={"probably A:shiwi (Zuni) (archaeological) (attributed)": ("Zuni Pueblo", "Centres & workshops", "A:shiwi pottery including the Hawikku glaze wares and later Zuni polychrome"),
      "Kewa (Santo Domingo Pueblo)": ("Santo Domingo (Kewa) Pueblo", "Centres & workshops", "Keresan pueblo of bold black-and-cream geometric pottery"),
      "Taos Pueblo": ("Taos Pueblo", "Centres & workshops", "northern Tiwa pueblo of micaceous cooking pottery"),
      "Jemez Pueblo": ("Jemez Pueblo", "Centres & workshops", "Towa pueblo whose pottery revived in the 20th c."),
      "Laguna Pueblo": ("Laguna Pueblo", "Centres & workshops", "Keresan pueblo of white-slipped polychrome close to Acoma"),
      "Zia Pueblo": ("Zia Pueblo", "Centres & workshops", "Keresan pueblo of red-based polychrome with birds"),
      "Isleta Pueblo": ("Isleta Pueblo", "Centres & workshops", "southern Tiwa pueblo of red-and-white polychrome"),
      "Tesuque Pueblo": ("Tesuque Pueblo", "Centres & workshops", "Tewa pueblo known for 'rain god' figures for the tourist trade")})
S("E1-67", pat=[r"acoma|a:ak.u"], kw="Acoma pottery", prof=AM,
  rows=[("Lucy M. Lewis", "Makers", "Acoma potter who revived ancient fine-line designs, c. 1898–1992", "Lucy M. Lewis", 1),
        ("Marie Z. Chino", "Makers", "Acoma potter of fine-line and Mimbres-inspired designs, 1907–1982", "Marie Z. Chino", 1)],
  ov={"Acoma Pueblo": "alias", "Pueblo: Acoma": "alias",
      "Diane Lewis": ("Diane Lewis", "Makers", "Acoma potter of the Lewis family, fine-line painted jars", None, 1),
      "Rebecca Lucario": ("Rebecca Lucario", "Makers", "Acoma potter of thin-walled fine-line jars", None, 1),
      "Rose Chino Garcia": ("Rose Chino Garcia", "Makers", "Acoma potter, daughter of Marie Z. Chino", None, 1)})
S("E1-68", pat=[r"\bhopi|sikyatki|sikyátki|jeddito|nampeyo"], kw="Hopi pottery", prof=AM,
  rows=[("Fannie Nampeyo", "Makers", "Hopi-Tewa potter, daughter of Nampeyo, 1900–1987", "Fannie Nampeyo", 1),
        ("Dextra Quotskuyva", "Makers", "Hopi-Tewa potter, great-granddaughter of Nampeyo, 1928–2019", "Dextra Quotskuyva", 1)],
  ov={"Hopi-Tewa": ("Hopi-Tewa pottery", "Sub-types", "painted yellow-ware of the Tewa village on First Mesa"),
      "probably Hopi Pueblo (archaeological) (attributed)": ("Sikyátki Polychrome", "Schools & phases", "yellow-fired polychrome of c. 1375–1625 that inspired the Sikyatki Revival"),
      "Nampeyo": ("Nampeyo", "Makers", "Hopi-Tewa potter who led the Sikyatki Revival, c. 1859–1942", "r3 https://en.wikipedia.org/wiki/Nampeyo", 1),
      "Joy Navasie": ("Joy Navasie", "Makers", "Hopi-Tewa potter, 'Frog Woman', known for white-slipped ware, 1919–2012", None, 1)})
S("E1-69", pat=[(r"san ildefonso|santa clara|k.apovi|martinez|tafoya|popovi", r"black")], kw="black-on-black pottery", prof=AM,
  rows=[("Maria Martinez", "Makers", "San Ildefonso potter who developed black-on-black ware c. 1918, 1887–1980", "Maria Martinez", 1),
        ("Julian Martinez", "Makers", "San Ildefonso painter of Maria's pots, 1879–1943", "Julian Martinez", 1),
        ("Popovi Da", "Makers", "San Ildefonso potter and painter, Maria's son, 1922–1971", "Popovi Da", 1),
        ("Margaret Tafoya", "Makers", "Santa Clara potter of large carved blackware, 1904–2001", "Margaret Tafoya", 1)],
  ov={"San Ildefonso Pueblo": ("San Ildefonso Pueblo", "Centres & workshops", "Tewa pueblo where Maria and Julian Martinez created the ware"),
      "Pueblo: San Ildefonso": "alias",
      "K'apovi (Santa Clara Pueblo)": ("Santa Clara Pueblo", "Centres & workshops", "Tewa pueblo of carved and polished blackware and redware")})
S("E1-70", pat=[r"mississippian|caddo|\blamar\b|moundville|cahokia|spiro|fort ancient|plaquemine|nodena"], kw="Mississippian pottery", prof=AM,
  rows=[("Cahokia", "Centres & workshops", "the largest Mississippian centre, Illinois; UNESCO World Heritage Site", "Cahokia", 0),
        ("Moundville", "Centres & workshops", "Mississippian centre in Alabama with engraved fineware", "Moundville Archaeological Site", 0),
        ("Head pots", "Sub-types", "human-head effigy jars of the central Mississippi valley, c. 1400–1600", "Mississippian culture pottery", 0)],
  ov={"probably Caddoan (archaeological) (attributed)": ("Caddo pottery", "Sub-types", "engraved fine ware of the Caddo of the Red River region"),
      "possibly South Appalachian Mississippian: Lamar (archaeological culture) (attributed)": ("Lamar culture pottery", "Sub-types", "complicated-stamped and incised ware of Georgia, c. 1350–1600"),
      "Mississippian": "alias"})
S("E1-71", pat=[r"swift creek"], kw="Swift Creek", prof=AM,
  rows=[("Kolomoki Mounds", "Centres & workshops", "Woodland mound centre in Georgia with Swift Creek and Weeden Island pottery", "Kolomoki Mounds Historic Park", 0)],
  ov={"possibly Swift Creek (archaeological culture) (attributed)": "alias"})
S("E1-72", pat=[r"weeden island"], kw="Weeden Island", prof=AM,
  rows=[("McKeithen site", "Centres & workshops", "Weeden Island mound complex in northern Florida", "McKeithen Site", 0)],
  ov={"possibly Weeden Island (archaeological culture) (attributed)": "alias"})
S("E1-73", pat=[r"catawba"], kw="Catawba pottery", prof=AM,
  rows=[("Georgia Harris", "Makers", "Catawba master potter, NEA National Heritage Fellow 1997, 1905–1997", "Georgia Harris", 1)],
  ov={"Catawba": "alias"})
S("E1-74", pat=[r"hermannsburg|ntaria"], node=r"Hermannsburg", kw="Hermannsburg Potters", prof="folk",
  rows=[("Hermannsburg", "Centres & workshops", "Lutheran mission community (Ntaria) west of Alice Springs", "Hermannsburg, Northern Territory", 0)],
  ov={"Hermannsburg Potters": "alias"})

EU = "europe"
S("E1-75", pat=[(r"maiolica|majolica|deruta|urbino|faenza|gubbio|pesaro|castel ?durante|montelupo|cafaggiolo|castelli|istoriato|albarello", r"ital|deruta|urbino|faenza|gubbio|pesaro|durante|montelupo|cafaggiolo|castelli|savona|venice|venetian|siena")], node=r"deruta_maiolica|Q622753",
  excl=r"mexic|puebla|minton|english|victorian", kw="maiolica", prof=EU, met=["Italian, Deruta", "Italian, Urbino", "Italian, Pesaro", "Italian, Faenza", "Italian, Gubbio"],
  rows=[("Faenza", "Centres & workshops", "Romagna town whose name gave 'faience'; Museo Internazionale delle Ceramiche", "Faenza", 0),
        ("Castel Durante", "Centres & workshops", "the present Urbania, centre of istoriato and grotesque ware", "Urbania", 0),
        ("Montelupo Fiorentino", "Centres & workshops", "Florentine centre of everyday and armorial maiolica", "Montelupo Fiorentino", 0),
        ("Istoriato", "Sub-types", "narrative painting covering the whole surface, Urbino and Castel Durante, from c. 1500", "Istoriato", 0),
        ("Albarello", "Sub-types", "cylindrical pharmacy jar, a staple maiolica form", "Albarello", 0),
        ("Nicola da Urbino", "Makers", "istoriato painter of Urbino, c. 1480–1537/38", "Nicola da Urbino", 1),
        ("Francesco Xanto Avelli", "Makers", "Urbino istoriato painter who signed and dated his works, c. 1487–c. 1542", "Francesco Xanto Avelli", 1),
        ("Giorgio Andreoli", "Makers", "Maestro Giorgio of Gubbio, lustre painter, c. 1465–1553", "Giorgio Andreoli", 1)],
  ov={"Italian, Deruta": ("Deruta", "Centres & workshops", "Umbrian town of lustred and blue maiolica, from the 15th c."),
      "Italian, Urbino": ("Urbino", "Centres & workshops", "ducal city, the centre of istoriato painting"),
      "Italian, Pesaro": ("Pesaro", "Centres & workshops", "Adriatic centre of maiolica, 15th–16th c."),
      "Gubbio": ("Gubbio", "Centres & workshops", "lustring centre of Maestro Giorgio Andreoli"),
      "Deruta maiolica": "drop:duplicate of the Deruta row", "maiolica": "alias"})
S("E1-76", pat=[(r"fa[iï]ence|tin.glaz|earthenware", r"rouen|nevers|moustiers|marseille|strasbourg|quimper|lun[eé]ville|sceaux|sinceny|niderviller|\blille\b|french|france")],
  excl=r"egypt|porcelain|longwy|scarab|amulet", kw="faience French", prof=EU,
  met=["French, Rouen", "French, Nevers", "French, Moustiers", "French, Sceaux", "French, Strasbourg", "French, Lille", "French, Marseille"],
  rows=[("Quimper faience", "Centres & workshops", "Breton faience of Quimper with peasant figures, from 1690", "Quimper faience", 0),
        ("Strasbourg", "Centres & workshops", "Hannong family factory, pioneer of low-fired enamel colours, 1721–1781", "Paul Hannong", 0),
        ("Lunéville", "Centres & workshops", "Lorraine faience factory founded by Jacques Chambrette, 1730", "Lunéville", 0),
        ("Paul Hannong", "Makers", "Strasbourg faience maker, 1700–1760", "Paul Hannong", 1),
        ("Joseph Clérissy", "Makers", "Moustiers faiencier who founded the town's production, 1679", "Moustiers-Sainte-Marie", 1)],
  ov={"French, Rouen": ("Rouen", "Centres & workshops", "Normandy centre of lambrequin blue-and-red faience, from 1640s"),
      "French, Nevers": ("Nevers", "Centres & workshops", "the first French faience centre, Italian-trained potters from the 1580s"),
      "French, Moustiers": ("Moustiers", "Centres & workshops", "Provençal centre of fine Bérain-style faience, from 1679")})
S("E1-77", pat=[r"delft"], node=r"Q1184151", kw="delftware", prof=EU, met=["Dutch, Delft"],
  rows=[("De Porceleyne Fles", "Centres & workshops", "Delft factory founded 1653, the only one still working (Royal Delft)", "Royal Delft", 0),
        ("English delftware", "Sub-types", "tin-glazed ware of London, Bristol and Liverpool, 16th–18th c.", "English delftware", 0),
        ("Tulip vases", "Sub-types", "multi-spouted flower pyramids made for Mary II at Hampton Court", "Delftware", 0),
        ("Frederik van Frijtom", "Makers", "Delft painter of landscape plaques, c. 1632–1702", "Frederik van Frijtom", 1),
        ("Adrianus Kocx", "Makers", "owner of De Grieksche A, supplier to William and Mary, d. 1701", "Adrianus Kocx", 1)],
  ov={"Dutch, Delft": "alias", "delftware": "alias"})
S("E1-78", pat=[r"saint.porchaire|henri ii ware"], kw="Saint-Porchaire", prof=EU, met=["French, Saint-Porchaire"],
  ov={"French, Saint-Porchaire": "alias"})
S("E1-79", pat=[(r"staffordshire|wedgwood|spode|minton|burslem|stoke.on.trent|whieldon|astbury|jasper|creamware|toby jug", r"pott|ceram|earthenware|stoneware|jasper|creamware|basalt|porcelain|ware")], excl=r"south staffordshire|enamel", kw="Staffordshire pottery", prof=EU,
  met=["British, Staffordshire"],
  rows=[("Creamware", "Sub-types", "lead-glazed cream earthenware perfected by Wedgwood (Queen's ware), from the 1760s", "Creamware", 0),
        ("Staffordshire figures", "Sub-types", "flat-backed earthenware mantelpiece figures, 19th c.", "Staffordshire figure", 0),
        ("Toby jug", "Sub-types", "jug in the form of a seated drinker, from the 1760s", "Toby jug", 0),
        ("Josiah Wedgwood", "Makers", "potter-industrialist of Etruria, 1730–1795", "Josiah Wedgwood", 1),
        ("Thomas Whieldon", "Makers", "Fenton potter of tortoiseshell ware, Wedgwood's partner, 1719–1795", "Thomas Whieldon", 1)],
  ov={"British, Staffordshire": "alias",
      "Jasperware": ("Jasperware", "Sub-types", "unglazed coloured stoneware with white reliefs, Wedgwood, 1775"),
      "Wedgwood": ("Wedgwood", "Centres & workshops", "the firm founded by Josiah Wedgwood in 1759, Etruria works from 1769"),
      "Spode": ("Spode", "Centres & workshops", "Stoke firm of blue transfer-printed earthenware and bone china, from 1770"),
      "Minton": ("Minton", "Centres & workshops", "Stoke firm founded 1793, majolica and encaustic tiles")})
S("E1-80", pat=[(r"pennsylvania", r"redware|earthenware|sgraffito|slip|pottery")], node=r"Pennsylvania German", kw="Pennsylvania German redware", prof=EU,
  ov={"Pennsylvania German decorated redware and painted chests": "alias",
      "Painted dower chests": "drop:furniture, not a kind of this ceramic ware"})
S("E1-81", pat=[(r"talavera|puente del arzobispo", r"spain|spanish|reina|arzobispo")], node=r"talavera_de_la_reina|El Puente", kw="Talavera de la Reina", prof=EU,
  ich=("https://ich.unesco.org/en/RL/artisanal-talavera-of-puebla-and-tlaxcala-mexico-and-ceramics-of-talavera-de-la-reina-and-el-puente-del-arzobispo-spain-making-process-01462", "UNESCO ICH: Artisanal talavera of Puebla and Tlaxcala and ceramics of Talavera de la Reina", "Representative List element (2019)"),
  rows=[("Juan Ruiz de Luna", "Makers", "potter who revived Talavera ware in the 20th c., 1863–1945; Museo Ruiz de Luna", "Museo Ruiz de Luna", 1)],
  ov={"Talavera de la Reina ceramics": "alias",
      "Ceramics from El Puente del Arzobispo": ("El Puente del Arzobispo", "Centres & workshops", "neighbouring Toledo town with its own green-and-brown painted ware"),
      "Artisanal talavera of Puebla and Tlaxcala (Mexico) and ceramics of Talavera de la Reina and El Puente del Arzobispo (Spain) making process": "alias"})
S("E1-82", pat=[r"bisalh"], kw="Bisalhaes", prof="folk", ich=("https://ich.unesco.org/en/USL/bisalhaes-black-pottery-manufacturing-process-01199", "UNESCO ICH: Bisalhães black pottery manufacturing process", "Urgent Safeguarding List element (2016)"),
  rows=[("Vila Real", "Centres & workshops", "district town in Trás-os-Montes whose parish of Mondrões includes Bisalhães", "Vila Real, Portugal", 0)],
  ov={"Bisalhães black pottery": "alias"})
S("E1-83", pat=[r"gmund"], kw="Gmundner Keramik", prof=EU,
  rows=[("Gmunden", "Centres & workshops", "town on the Traunsee, Upper Austria", "Gmunden", 0)],
  ov={"Traditional Craftsmanship in Gmunden: Pottery Flaming": "alias",
      "Geflammt (flamed) decoration": ("Geflammt (flamed) decoration", "Sub-types", "green or blue trailed 'flame' pattern on white, the classic Gmunden decor")})
S("E1-84", pat=[r"longwy"], kw="Longwy", prof=EU,
  rows=[("Longwy", "Centres & workshops", "Lorraine town whose faience works (from 1798) developed the enamels in the 1870s", "Longwy", 0)],
  ov={"Enamels from Longwy": "alias"})
S("E1-85", pat=[r"изразц|izrazts|stove tile"], node=r"izraztsy", excl=r"german|austria|swed|dutch", kw="Russian stove tiles", prof=EU,
  rows=[("Yaroslavl", "Centres & workshops", "17th-c. centre whose church facades carry polychrome izraztsy", "Yaroslavl", 0),
        ("Stepan Polubes", "Makers", "Belarusian-born tile master of the New Jerusalem Monastery, 17th c.", "Stepan Ivanov (Polubes)", 1)],
  ov={"Russian tiled stoves (izraztsy)": "alias"})
S("E1-86", pat=[r"skopin|скопин"], node=r"skopin", kw="Skopin pottery", prof=EU,
  rows=[("Skopin", "Centres & workshops", "town in Ryazan Oblast, centre of the fantastical glazed ware", "Skopin", 0)],
  ov={"Skopin pottery": "alias"})
S("E1-87", pat=[r"balkhar|балхар"], kw="Balkhar", prof=EU,
  rows=[("Balkhar", "Centres & workshops", "Lak village in Dagestan where women make the pottery", "Balkhar", 0)],
  ov={"Balkhar pottery": "alias"})
S("E1-88", pat=[r"opishn|опошн"], node=r"opishnia", kw="Opishnia", prof=EU,
  rows=[("Opishnia", "Centres & workshops", "Poltava Oblast pottery town, seat of the National Museum of Ukrainian Pottery", "Opishnia", 0)],
  ov={"Opishnia ceramics": "alias"})
S("E1-89", pat=[r"kosiv|kosov|косів|косов"], node=r"kosiv", kw="Kosiv ceramics", prof=EU,
  ich=("https://ich.unesco.org/en/RL/tradition-of-kosiv-painted-ceramics-01456", "UNESCO ICH: Tradition of Kosiv painted ceramics", "Representative List element (2019)"),
  rows=[("Oleksa Bakhmatiuk", "Makers", "Kosiv master of figurative painted ceramics, 1820–1882", "Oleksa Bakhmatiuk", 1)],
  ov={"Kosiv painted ceramics": "alias", "Kosiv": ("Kosiv", "Centres & workshops", "Hutsul town in Ivano-Frankivsk Oblast")})
S("E1-90", pat=[r"sokal|сокал"], kw="Sokal ceramics", prof=EU,
  rows=[("Sokal", "Centres & workshops", "town in Lviv Oblast, Ukraine", "Sokal", 0)], ov={"Sokal ceramics": "alias"})
S("E1-91", pat=[r"bubniv|бубнів|бубнов"], kw="Bubnivka", prof=EU, ov={"Bubnivka ceramics": "alias"})
S("E1-92", pat=[r"oleshn|олешн"], kw="Oleshnia", prof=EU, ov={"Oleshnia pottery": "alias"})
S("E1-93", pat=[r"horezu|hurez"], kw="Horezu", prof=EU,
  rows=[("Horezu", "Centres & workshops", "Oltenian town at the foot of the Carpathians; nearby Hurezi Monastery is a UNESCO site", "Horezu", 0),
        ("Horezu cockerel", "Sub-types", "the cockerel motif painted on Horezu plates", "Horezu ceramics", 0)],
  ov={"Horezu ceramics": "alias"})
S("E1-94", pat=[r"zlakus"], kw="Zlakusa", prof="folk",
  ich=("https://ich.unesco.org/en/RL/zlakusa-pottery-making-hand-wheel-pottery-making-in-the-village-of-zlakusa-01466", "UNESCO ICH: Zlakusa pottery making", "Representative List element (2020)"),
  rows=[("Zlakusa", "Centres & workshops", "village near Užice, western Serbia", "Zlakusa", 0)],
  ov={"Zlakusa pottery making": "alias"})
S("E1-95", pat=[r"impruneta"], kw="Impruneta terracotta", prof=EU,
  rows=[("Impruneta", "Centres & workshops", "town south of Florence whose kilns supplied Brunelleschi's dome tiles", "Impruneta", 0)],
  ov={"Impruneta terracotta": ("Impruneta citrus pot (conca)", "Sub-types", "large frost-proof garden pot for lemon trees · Possession: Impruneta citrus pot (C2)")})
S("E1-96", pat=[r"thrapsano"], kw="Thrapsano", prof=EU,
  rows=[("Thrapsano", "Centres & workshops", "village in Heraklion regional unit, Crete", "Thrapsano", 0)],
  ov={"Thrapsano pottery": ("Cretan pithos", "Sub-types", "large storage jar thrown by itinerant teams of Thrapsano potters · Possession: Cretan pithos (C2)")})
S("E1-97", pat=[(r"encaustic", r"tile")], kw="encaustic tile", prof=EU,
  rows=[("Chertsey tiles", "Sub-types", "inlaid tiles from Chertsey Abbey with Tristan and Richard I scenes, c. 1250; British Museum", "Chertsey Abbey", 0),
        ("Minton", "Centres & workshops", "Stoke firm that revived encaustic tiles from 1840 (Palace of Westminster floors)", "Minton", 0),
        ("Maw & Co", "Centres & workshops", "Shropshire maker of encaustic and decorative tiles, from 1850", "Maw & Co", 0),
        ("Herbert Minton", "Makers", "Stoke potter who patented the revived encaustic tile, 1793–1858", "Herbert Minton", 1)],
  ov={"Victorian encaustic tile": ("Victorian encaustic tile", "Sub-types", "machine-pressed inlaid floor tile of the Gothic Revival · Possession: Encaustic tile (C8)")})
S("E1-98", pat=[r"stove tile|ofenkachel|kachel|tiled stove|kakelugn|hafner"], excl=r"изразц|izrazts|russian", kw="stove tile", prof=EU,
  rows=[("Rörstrand", "Centres & workshops", "Stockholm faience factory, supplier of kakelugn tiles, from 1726", "Rörstrand", 0)],
  ov={"Kachelofen (German and Austrian tiled stove)": ("Kachelofen", "Sub-types", "German and Austrian tiled masonry stove · Possession: Masonry heater (G3)"),
      "Kakelugn": ("Kakelugn", "Sub-types", "Swedish tall tiled stove made efficient by Cronstedt and Wrede (1767), its faience tiles from Rörstrand and Marieberg · Possession: Masonry heater (G3)")})

ISL = "islam"
S("E2-1", pat=[(r"seljuk|seljuq|saljuq|silhouette|laqabi", r"frit|stonepaste|ceramic|earthenware|glaz")], excl=r"lustre|mina.?i|lajvard", kw="Seljuk ceramic",
  rows=[("Monochrome ware", "Sub-types", "fritware in a single turquoise, cobalt or white glaze, often carved or moulded", "Islamic pottery", 0),
        ("Silhouette ware", "Sub-types", "designs carved in thick black slip under clear turquoise glaze", "Islamic pottery", 0),
        ("Laqabi ware", "Sub-types", "carved fritware with coloured glazes kept apart by incised lines", "Islamic pottery", 0),
        ("Rayy", "Centres & workshops", "city south of Tehran, long credited with much Seljuq pottery", "Ray, Iran", 0),
        ("Kashan", "Centres & workshops", "the main Seljuq fritware centre", "Kashan", 0)])
S("E2-2", pat=[(r"kashan", r"lustre|luster")], kw="Kashan lustre",
  rows=[("Abu Tahir family", "Makers", "Kashan dynasty of lustre potters and tile makers, 12th–14th c.", "Abu Tahir", 1),
        ("Kashan", "Centres & workshops", "city in central Iran, the only lustre centre of Iran in this period", "Kashan", 0),
        ("Mihrab tiles", "Sub-types", "monumental lustre-tiled prayer niches such as those of Imamzada Yahya at Veramin", "Kashan lustreware", 0)],
  ov={"Abu Zayd, Persian, active late 12th–early 13th century": ("Abu Zayd, Persian, active late 12th–early 13th century", "Makers", "Kashan potter in lustre and mina'i, fl. 1186–1219"),
      "Ali ibn Muhammad ibn Abi Tahir": ("Ali ibn Muhammad ibn Abi Tahir", "Makers", "lustre potter of the Abu Tahir family, 13th c."),
      "Hassan b. Arabshah": ("Hassan b. Arabshah", "Makers", "Kashan lustre tile maker (attribution uncertain)"),
      "Abū Zayd ibn Muḥammad ibn Abī Zayd": ("Abū Zayd ibn Muḥammad ibn Abī Zayd", "Makers", "Kashan lustre and mina'i potter; the same artist as Abu Zayd above in another record")})
S("E2-3", pat=[(r"mina.?i|haft.?rang", r"frit|stonepaste|ceramic|earthenware|bowl|tile|beaker|ewer")], excl=r"parchment|paper|manuscript|qur|glass|enamel(?!led overglaze)", kw="mina'i",
  rows=[("Kashan", "Centres & workshops", "the main centre of mina'i ware, late 12th–early 13th c.", "Kashan", 0),
        ("Freer Beaker", "W", "mina'i beaker painted in strips with the Shahnama story of Bizhan and Manizha, early 13th c.; Freer Gallery, Washington", "Mina'i ware", 0)])
S("E2-4", pat=[r"lajvard"], kw="lajvardina",
  rows=[("Kashan", "Centres & workshops", "Ilkhanid centre of lajvardina vessels and tiles", "Kashan", 0),
        ("Takht-i Sulaiman", "Centres & workshops", "Ilkhanid summer palace whose lajvardina tiles were excavated in the 1960s–70s", "Takht-e Soleyman", 0)])
S("E2-5", pat=[r"raqq?a|ar-raqqah"], kw="Raqqa ware",
  rows=[("Raqqa", "Centres & workshops", "Euphrates city of Ayyubid fritware kilns, 12th–13th c.", "Raqqa", 0),
        ("Raqqa lustre", "Sub-types", "brown lustre on greenish glaze, Raqqa, late 12th–13th c.", "Islamic pottery", 0)])
S("E2-6", pat=[r"sultanabad"], kw="Sultanabad",
  rows=[("Sultanabad", "Centres & workshops", "the old name of Arak, central Iran, where the ware was first found", "Arak, Iran", 0)])
S("E2-7", pat=[r"iznik|i̇znik|nicaea"], excl=r"glass|velvet|silk|textile", kw="Iznik",
  rows=[("İznik", "Centres & workshops", "town south-east of Istanbul, the Ottoman fritware centre, late 15th–17th c.", "İznik", 0),
        ("Golden Horn ware", "Sub-types", "blue-and-white with thin spirals, 1530s, once thought made at the Golden Horn", "Iznik pottery", 0),
        ("Damascus ware (Iznik)", "Sub-types", "Iznik palette of sage green, manganese and blue, c. 1540–1555", "Iznik pottery", 0),
        ("Rhodian ware", "Sub-types", "bole-red Iznik of c. 1557–1600, once thought made on Rhodes", "Iznik pottery", 0),
        ("Rüstem Pasha Mosque", "W", "Istanbul mosque by Mimar Sinan, c. 1561–1563, lined with Iznik tiles", "Rüstem Pasha Mosque", 0),
        ("Dome of the Rock lamp", "W", "Iznik mosque lamp dated 1549, from the Dome of the Rock; British Museum, London", "Iznik pottery", 0)],
  ov={"Abraham of Kütahya": ("Abraham of Kütahya", "Makers", "potter named on an Armenian-inscribed ewer of 1510 that gives the name to early Iznik blue-and-white"),
      "Musli": ("Musli", "Makers", "signer of the Dome of the Rock lamp of 1549 (British Museum)")})
S("E2-8", pat=[(r"damascus|syria", r"tile|frit|stonepaste|earthenware")], excl=r"mamluk|made in: england|transfer|abbasid|raqq|ayyubid", kw="Damascus tiles",
  rows=[("Damascus", "Centres & workshops", "Syrian capital whose 16th–17th c. tile workshops decorated mosques and houses", "Damascus", 0),
        ("Süleymaniye Tekkiye (Damascus)", "W", "Ottoman complex by Mimar Sinan, 1554–1559, with Damascus tiles", "Tekkiye Mosque", 0)])
S("E2-9", pat=[r"kubach"], kw="Kubachi ware",
  rows=[("Kubachi", "Centres & workshops", "Dagestan village where much of the ware was collected, giving its name; made in Tabriz", "Kubachi", 0),
        ("Tabriz", "Centres & workshops", "north-west Iranian city considered the likely production centre", "Tabriz", 0)])
S("E2-10", pat=[(r"safavid|kirman|kerman|gombroon|meshed|mashhad", r"frit|stonepaste|ceramic|earthenware|glaz|porcelain")], excl=r"kubach|glass|metal|silk|copper", kw="Safavid ceramic",
  rows=[("Kirman ware", "Sub-types", "blue-and-white and polychrome fritware of Kerman, 17th c.", "Kerman", 0),
        ("Gombroon ware", "Sub-types", "thin white fritware exported via Bandar Abbas (Gombroon), 17th–18th c.", "Bandar Abbas", 0),
        ("Mashhad", "Centres & workshops", "Khorasan centre of blue-and-white fritware", "Mashhad", 0),
        ("Isfahan", "Centres & workshops", "Safavid capital whose buildings carry haft-rangi (cuerda seca) tiles", "Isfahan", 0)])
S("E2-11", pat=[r"k[uü]tahya"], node=r"Kutahya and Canakkale", excl=r"[cç]anakkale|chanak", kw="Kutahya",
  rows=[("Kütahya", "Centres & workshops", "western Anatolian town of mostly Armenian potters", "Kütahya", 0)],
  ov={"Mustafa Ali Effendi": ("Mustafa Ali Effendi", "Makers", "tile maker (Kütahya attribution uncertain)")})
S("E2-12", pat=[(r"qajar|kajar", r"frit|stonepaste|ceramic|earthenware|tile")], kw="Qajar tile",
  rows=[("Golestan Palace", "W", "Qajar royal palace in Tehran with painted tile revetments; UNESCO World Heritage Site", "Golestan Palace", 0),
        ("Tehran", "Centres & workshops", "Qajar capital and main tile centre", "Tehran", 0),
        ("Shiraz", "Centres & workshops", "centre of 'Qajar rose' tiles", "Shiraz", 0)],
  ov={"Isfahani, Ali Muhammad": ("Isfahani, Ali Muhammad", "Makers", "Qajar tile maker in Tehran and Isfahan, fl. 1870s–1888"),
      "Ali Akbar Shirazi": ("Ali Akbar Shirazi", "Makers", "Qajar maker named on a bowl (medium uncertain)"),
      "Nasr, Muhammad": ("Nasr, Muhammad", "Makers", "Qajar potter"),
      "Muhammad ibn Yusuf": ("Muhammad ibn Yusuf", "Makers", "Qajar maker named on a plate (medium uncertain)")})
S("E2-13", pat=[r"qallal", (r"tunis", r"tile")], kw="Qallaline tile",
  rows=[("Tunis", "Centres & workshops", "the Qallaline quarter of the medina housed the potters", "Medina of Tunis", 0)],
  ov={"The craftsman may have been the Tunisian, al-Hajj Mas’ud al-Sab’a": ("The craftsman may have been the Tunisian, al-Hajj Mas’ud al-Sab’a", "Makers", "al-Hajj Mas'ud al-Sab'a, Tunisian tile maker (tentative attribution)")})
S("E2-14", pat=[(r"jaipur", r"blue|pottery|ceram")], node=r"Blue Pottery of Jaipur", kw="Jaipur blue pottery", prof="folk",
  rows=[("Kripal Singh Shekhawat", "Makers", "artist who revived Jaipur blue pottery from the 1950s, 1922–2008", "Kripal Singh Shekhawat", 1),
        ("Jaipur", "Centres & workshops", "Rajasthan city, centre of the craft since the 19th c.", "Jaipur", 0)],
  ov={"Blue Pottery of Jaipur": "alias"})
S("E2-15", pat=[(r"egypt", r"faience|glazed composition")], kw="Egyptian faience", prof="antiq",
  rows=[("William (hippopotamus)", "W", "blue faience hippopotamus, Middle Kingdom, c. 1961–1878 BC; Metropolitan Museum, New York", "William (hippo)", 0),
        ("Step Pyramid tiles", "W", "blue faience wall tiles of Djoser's underground chambers, Saqqara, c. 2650 BC", "Pyramid of Djoser", 0),
        ("Amarna", "Centres & workshops", "Akhenaten's capital, whose faience workshops made inlays and rings", "Amarna", 0)],
  ov={"Scarabs": ("Scarabs", "Sub-types", "faience and steatite beetle amulets and seals, the commonest Egyptian faience objects"),
      "Amulets": ("Amulets", "Sub-types", "protective faience amulets of gods and symbols, especially Late Period"),
      "Ushabti": ("Ushabti", "Sub-types", "faience servant figurines placed in tombs, notably Third Intermediate Period")})
