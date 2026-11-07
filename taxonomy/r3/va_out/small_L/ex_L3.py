from xh import *
E, X = {}, {}
D = ("dup",)
def drop(r): return ("drop", r)
LBL = drop("tradition bucket label from the gathered data; its sites are expanded in the catalogue")
AX = "Sub-types and techniques first, then the sites and works catalogue sectioned by region or school, then collections and named makers."
BODY = "Sub-types first (every gathered Wikidata item of the practice, then attested types), then centres and named practitioners."

# ---------------- L3 mosaic & tile ----------------
E["L3-1"] = dict(axis=AX, catalogues=[ARCHNET, IAH, UN(148, "Old City of Jerusalem and its Walls"), UN(20, "Ancient City of Damascus")],
    kinds=[W("Glass and gold wall mosaic", "Sub-types", "Byzantine-trained glass tesserae on gold ground, without figures: trees, vines, jewels and cities", "Umayyad Mosque")],
    knowledge_sites=[W("Hisham's Palace", "Umayyad Syria and Palestine", "Jericho; c. 740s; bath-hall floor mosaics incl. the Tree of Life with lions and gazelles"),
                     W("Al-Aqsa Mosque", "Umayyad Syria and Palestine", "Jerusalem; fragments of Umayyad and Fatimid wall mosaic")])

E["L3-2"] = dict(axis=AX, catalogues=[ARCHNET, IAH, WP("Zellij", "tradition article"), VAM("zellige", "zellige panels and tiles in the V&A")],
    kinds=[W("Hand-cut geometric zellige", "Sub-types", "glazed tiles cut into tesserae (furmah) and set face-down into star patterns", "Zellij"),
           SR("Alicatado", "Sub-types", "the Andalusi term for cut-tile mosaic dadoes (Alhambra, Seville Alcázar)", "Alicatado"),
           W("Fez", "Centres & workshops", "Morocco; the main zellige workshops (maâlem), with Meknes", "Fez, Morocco")],
    knowledge_sites=[W("Al-Attarine Madrasa", "Marinid and Saadian Morocco", "Fez; 1323-25; Marinid zellige dadoes"),
                     W("Saadian Tombs", "Marinid and Saadian Morocco", "Marrakesh; 1578-1603; zellige and carved stucco mausolea"),
                     W("Bahia Palace", "Marinid and Saadian Morocco", "Marrakesh; 1860s-1900; 19th-century zellige revival"),
                     W("Alcázar of Seville", "Nasrid al-Andalus", "Seville; Mudéjar palace of Peter I with alicatado dadoes, 1364")])

E["L3-3"] = dict(axis=AX, catalogues=[ARCHNET, IAH, VAM("cut-tile mosaic", "Persian and Central Asian tile panels in the V&A"), MET("tile mosaic Iran", "mihrabs and panels incl. the Isfahan mihrab of 1354")],
    kinds=[W("Moʿaraq (cut-tile mosaic)", "Sub-types", "monochrome glazed tiles cut and fitted into patterns, 14th-17th century", "Persian architecture"),
           W("Haft rangi (cuerda seca tiles)", "Sub-types", "seven-colour painted square tiles, the cheaper Safavid alternative", "Haft rangi")],
    knowledge_sites=[W("Blue Mosque, Tabriz", "Qara Qoyunlu and Aq Qoyunlu", "Tabriz; 1465; the finest Turkmen tile mosaic"),
                     W("Goharshad Mosque", "Timurid Khorasan", "Mashhad; 1418; tile mosaic iwans built for Goharshad"),
                     W("Bibi-Khanym Mosque", "Timurid Samarkand", "Samarkand; 1399-1404; Timur's congregational mosque")])

E["L3-4"] = dict(axis=AX, catalogues=[ARCHNET, IAH, WP("Wazir Khan Mosque", "the principal monument")],
    kinds=[W("Multan", "Centres & workshops", "Punjab; kashigari of Multan, tile-mosaic and blue-glazed revetment and vessels, 14th c. onward")],
    knowledge_sites=[W("Tomb of Shah Rukn-e-Alam", "Multan and the Punjab", "Multan; 1320s; brick mausoleum with glazed tile bands"),
                     W("Chauburji", "Lahore", "Lahore; 1646; gateway once covered in kashi kari tile mosaic"),
                     W("Picture Wall", "Lahore", "Lahore Fort; 1624-31; tile-mosaic and fresco wall of elephants, angels and polo", "Picture Wall, Lahore Fort"),
                     W("Shah Jahan Mosque", "Sindh", "Thatta; 1647-59; blue-and-white tilework")])
X[("L3-4", "Multani blue pottery and tiles")] = drop("replaced by the Multan centre row")

E["L3-5"] = dict(axis=AX, catalogues=[ARCHNET, IAH, COM("Aina-kari mirror mosaic")],
    kinds=[W("Ayeneh-kari", "Sub-types", "Persian cut-mirror mosaic of shrines and palaces, Safavid to present", "Ayeneh-kari"),
           W("Sheesh Mahal work", "Sub-types", "Mughal and Rajput convex-mirror inlay in stucco (shisha)", "Sheesh Mahal")],
    knowledge_sites=[W("Shah Cheragh", "Persian shrines and palaces", "Shiraz; shrine with total mirror-mosaic interior"),
                     W("Golestan Palace", "Persian shrines and palaces", "Tehran; Hall of Mirrors (Talar-e Aineh), Qajar; UNESCO World Heritage Site"),
                     SR("Sheesh Mahal (Lahore Fort)", "Mughal and Rajput palaces", "Lahore; 1631-32 mirror palace of Shah Jahan", "Sheesh Mahal Lahore Fort"),
                     W("Amber Fort", "Mughal and Rajput palaces", "Jaipur; Sheesh Mahal of the Jai Mandir; UNESCO (Hill Forts of Rajasthan)")])
X[("L3-5", "mosaic - Mughal Empire (undated)")] = LBL

E["L3-6"] = dict(axis=AX, catalogues=[WP("Pella", "site article"), COM("Pella mosaics"), WP("Mosaic", "survey article")],
    knowledge_sites=[W("Stag Hunt Mosaic", "Greek mosaic sites", "Pella; c. 300 BC; pebble mosaic signed by Gnosis; Pella Archaeological Museum"),
                     W("Pella", "Greek mosaic sites", "Macedonia; Macedonian capital with pebble mosaics of the late 4th c. BC"),
                     W("Olynthus", "Greek mosaic sites", "Chalkidiki; 5th-4th c. BC pebble floors, among the earliest"),
                     W("Delos", "Greek mosaic sites", "Cyclades; Hellenistic tessellated floors (House of Dionysus, House of the Dolphins); UNESCO")],
    kinds=[MS("Sosus of Pergamon", "Makers", "Hellenistic mosaicist of the 'unswept floor' and the doves, copied in Roman mosaics", "Sosus of Pergamon")])
X[("L3-6", "Pebble mosaic")] = ("Sub-types", "floors of natural river pebbles, Greek Classical to early Hellenistic (Olynthus, Pella)")

E["L3-7"] = dict(axis=AX, catalogues=[WP("Roman mosaic", "survey article"), ["https://www.bardomuseum.tn/", "Bardo National Museum", "the largest collection of Roman mosaics"], COM("Roman mosaics"), BM("Roman mosaic", "Roman mosaics in the British Museum")],
    kinds=[W("Opus tessellatum", "Sub-types", "floors of regular stone tesserae, the standard Roman technique", "Opus tessellatum"),
           W("Opus vermiculatum", "Sub-types", "minute tesserae for painterly emblemata", "Opus vermiculatum"),
           W("Opus sectile", "Sub-types", "cut-stone inlay of marble and glass panels", "Opus sectile"),
           W("Emblema", "Sub-types", "a finely worked central picture panel set into a floor", "Emblema (art)")])
for n in ("Roman mosaics of the East (Antioch, Zeugma)", "Roman North African mosaics", "Villa Romana del Casale and Roman Sicily mosaics", "mosaic - France (ancient)"): X[("L3-7", n)] = LBL

E["L3-8"] = dict(axis=AX, catalogues=[UN(788, "Early Christian Monuments of Ravenna"), UN(1487, "Arab-Norman Palermo and the Cathedral Churches of Cefalú and Monreale"), PRINCETON, COM("Byzantine mosaics")],
    kinds=[M("Jacopo Torriti", "Makers", "Roman mosaicist, apse of Santa Maria Maggiore, 1295"),
           M("Pietro Cavallini", "Makers", "Roman painter and mosaicist, Life of the Virgin, Santa Maria in Trastevere, 1291")])
for n in ("Middle Byzantine mosaics (Hagia Sophia, Hosios Loukas, Daphni, Nea Moni)", "Early Christian and medieval mosaics of Rome", "Ravenna Early Christian and Byzantine mosaics",
          "Norman Sicilian mosaics (Palermo, Monreale, Cefalù)", "Venetian Byzantine mosaics (San Marco, Torcello)", "Kyivan Rus' mosaics", "Levantine church floor mosaics (Madaba school)"): X[("L3-8", n)] = LBL

E["L3-9"] = dict(axis=AX, catalogues=[["https://www.museudoazulejo.gov.pt/", "Museu Nacional do Azulejo", "Lisbon national tile museum and collection"], WP("Azulejo", "tradition article"), VAM("azulejo", "Portuguese and Spanish tiles in the V&A")],
    kinds=[W("Museu Nacional do Azulejo", "Collections", "Lisbon; national tile museum in the Madre de Deus convent"),
           M("Gabriel del Barco", "Makers", "(1648/9-c. 1703) Spanish-born painter of the first great blue-and-white figurative panels in Portugal"),
           MS("Policarpo de Oliveira Bernardes", "Makers", "(1695-1778) master of the Grand Production of blue-and-white panels", "Policarpo de Oliveira Bernardes"),
           M("Rafael Bordalo Pinheiro", "Makers", "(1846-1905) caricaturist and ceramicist of the Caldas da Rainha factory"),
           M("Jorge Colaço", "Makers", "(1868-1942) panels of São Bento station, Porto, 1905-16"),
           M("Maria Keil", "Makers", "(1914-2012) designer of the Lisbon Metro tile panels")])
X[("L3-9", "Spanish azulejo and alicatado")] = LBL

E["L3-10"] = dict(axis=AX, catalogues=[UN(320, "Works of Antoni Gaudí"), UN(804, "Palau de la Música Catalana and Hospital de Sant Pau"), WP("Trencadís", "technique article")],
    kinds=[M("Antoni Gaudí", "Makers", "(1852-1926) Park Güell, Casa Batlló, Casa Milà"),
           M("Josep Maria Jujol", "Makers", "(1879-1949) the trencadís bench of Park Güell"),
           M("Lluís Domènech i Montaner", "Makers", "(1850-1923) Hospital de Sant Pau, Palau de la Música Catalana")],
    knowledge_sites=[W("Casa Batlló", "Modernista works in trencadís", "Barcelona; 1904-06; façade of glass and ceramic trencadís; UNESCO"),
                     W("Palau de la Música Catalana", "Modernista works in trencadís", "Barcelona; 1905-08; mosaic columns and façade; UNESCO")])

E["L3-11"] = dict(axis="Sub-types first, then named pavements (from knowledge; the gathered record holds none), then designers.",
    catalogues=[WP("Portuguese pavement", "tradition article"), COM("Calçada portuguesa")],
    kinds=[W("Mar Largo wave pattern", "Sub-types", "black-and-white wave design of the Rossio, 1849, copied at Copacabana", "Portuguese pavement"),
           W("Calceteiro", "Centres & workshops", "the paviour's craft, taught at Lisbon's Escola de Calceteiros", "Portuguese pavement"),
           M("Roberto Burle Marx", "Makers", "(1909-1994) designer of the Copacabana promenade pavement, 1970")],
    knowledge_sites=[W("Rossio", "Named pavements", "Lisbon; Pedro IV square, laid 1848-49, the founding calçada"),
                     W("Copacabana, Rio de Janeiro", "Named pavements", "Avenida Atlântica promenade, wave pavement redesigned by Burle Marx")])
X[("L3-11", "Portuguese pavement (calçada)")] = ("alias",)

E["L3-12"] = dict(axis=AX, catalogues=[COM("Soviet mosaics"), WP("Moscow Metro", "stations with mosaic programmes"), [surl("Soviet Mosaics in Ukraine"), "Wikipedia search: Soviet mosaics in Ukraine", "articles on the Ukrainian mosaic heritage"]],
    kinds=[M("Alexander Deineka", "Makers", "(1899-1969) ceiling mosaics of Mayakovskaya station, Moscow, 1938"),
           M("Pavel Korin", "Makers", "(1892-1967) mosaic ceilings of Komsomolskaya (Koltsevaya line), 1952"),
           M("Alla Horska", "Makers", "(1929-1970) Ukrainian dissident artist, Tree of Life mosaic, Mariupol"),
           M("Zurab Tsereteli", "Makers", "(1934-2025) Georgian mosaic panels and resort mosaics of the 1960s-70s")],
    knowledge_sites=[W("Mayakovskaya (Moscow Metro)", "Russian SFSR", "Moscow; 1938; 34 ceiling mosaics of 'A Day of Soviet Sky' by Deineka"),
                     W("Komsomolskaya (Koltsevaya line)", "Russian SFSR", "Moscow; 1952; Korin's mosaics of Russian military history")])

# ---------------- L4 geoglyphs ----------------
GAX = "Sub-types first, then the geoglyphs catalogue by field or figure type."
E["L4-1"] = dict(axis=GAX, catalogues=[WP("Steppe Geoglyphs", "tradition article"), COM("Turgai geoglyphs")],
    kinds=[W("Earthen-mound geometric figures", "Sub-types", "squares, crosses, rings and swastika-like figures of small mounds, Turgai trough", "Steppe Geoglyphs")],
    knowledge_sites=[W("Ushtogay Square", "Turgai (Kazakhstan)", "Kostanay region; 287 m square of 101 mounds, the best-known steppe geoglyph"),
                     SR("Zyuratkul geoglyph", "Southern Urals", "Chelyabinsk oblast; elk figure c. 275 m long, found 2011", "Zyuratkul geoglyph")])

E["L4-2"] = dict(axis="Sites catalogue from knowledge (the gathered record holds none): the five mountain characters lit on 16 August, in lighting order.",
    catalogues=[WP("Gozan no Okuribi", "festival article"), COM("Gozan no Okuribi")],
    knowledge_sites=[W("Daimonji (Nyoigatake)", "Five bonfire characters", "Higashiyama, Kyoto; the great 大 character, lit first", "Gozan no Okuribi"),
                     W("Myōhō (Matsugasaki)", "Five bonfire characters", "Matsugasaki, Kyoto; the characters 妙 and 法", "Gozan no Okuribi"),
                     W("Funagata (Funayama)", "Five bonfire characters", "Nishigamo, Kyoto; boat shape", "Gozan no Okuribi"),
                     W("Hidari Daimonji", "Five bonfire characters", "Ōkitayama, Kyoto; the left-hand 大", "Gozan no Okuribi"),
                     W("Torii-gata (Mandaragi)", "Five bonfire characters", "Saga Toriimoto, Kyoto; torii gate shape, lit last", "Gozan no Okuribi")])
X[("L4-2", "Gozan no Okuribi (Kyoto bonfire characters)")] = ("alias",)

E["L4-3"] = dict(axis=GAX, catalogues=[UN(700, "Lines and Geoglyphs of Nasca and Palpa"), WP("Nazca Lines", "site article with figure list"), COM("Nazca Lines")],
    kinds=[W("Biomorphs", "Sub-types", "animal and plant figures (monkey, hummingbird, spider) of the Nazca culture, c. 100 BC-AD 700", "Nazca Lines"),
           W("Lines and trapezoids", "Sub-types", "straight lines up to several km and cleared trapezoids", "Nazca Lines"),
           W("Paracas-period hillside figures", "Schools & phases", "earlier figures on hill slopes of Palpa, c. 400-200 BC", "Nazca Lines")])
X[("L4-3", "Palpa lines")] = drop("section label; the Palpa figures are listed in their section")

E["L4-4"] = dict(axis=GAX, catalogues=[WP("Atacama Giant", "the largest figure"), COM("Pintados geoglyphs")],
    kinds=[W("Hillside mosaic geoglyphs", "Sub-types", "figures built by clearing and piling dark stones on desert slopes along caravan routes, AD 600-1500", "Atacama Giant")])
X[("L4-4", "Chug-Chug")] = D

E["L4-5"] = dict(axis=GAX, catalogues=[WP("Acre geoglyphs", "site article"), COM("Acre geoglyphs")],
    kinds=[W("Ditched geometric enclosures", "Sub-types", "circles and squares of ditches up to 300 m across, c. 2000 BP; over 450 known", "Acre geoglyphs"),
           W("Amazonian earthworks", "Sub-types", "the wider class of pre-Columbian ditches and causeways revealed by deforestation", "Acre geoglyphs")])

E["L4-6"] = dict(axis=GAX, catalogues=[["https://www.nps.gov/efmo/", "Effigy Mounds National Monument (NPS)", "over 200 mounds incl. 31 effigies"], WP("Effigy mound", "type article"), NRHP],
    kinds=[W("Animal-effigy mounds", "Sub-types", "bear, bird and panther mounds of the Late Woodland Effigy Moundbuilders, c. 700-1100", "Effigy mound")],
    knowledge_sites=[W("Effigy Mounds National Monument", "Ancient effigy mounds", "Iowa; Marching Bears group and 30 other effigies"),
                     W("Man Mound", "Ancient effigy mounds", "Baraboo, Wisconsin; the only surviving human-shaped effigy mound"),
                     W("Rock Eagle Effigy Mound", "Ancient effigy mounds", "Putnam County, Georgia; quartz-cobble bird effigy, Middle Woodland"),
                     SR("Lizard Mound State Park", "Ancient effigy mounds", "Washington County, Wisconsin; 28 mounds incl. lizard effigies", "Lizard Mound County Park")])

E["L4-7"] = dict(axis=GAX, catalogues=[WP("Blythe Intaglios", "site article"), NRHP],
    kinds=[W("Mojave and Quechan intaglios", "Sub-types", "figures scraped through desert pavement; human figure read as Mastamho the creator", "Blythe Intaglios")],
    knowledge_sites=[W("Topock Maze", "Lower Colorado River intaglios", "Mohave County, Arizona; windrow maze linked to Mojave ritual")])

E["L4-8"] = dict(axis=GAX, catalogues=[HIST_ENG, WP("Hill figure", "type article with lists of hill figures"), COM("Chalk hill figures")],
    kinds=[W("Chalk-cut figures", "Sub-types", "turf removed to expose chalk, kept by periodic scouring", "Hill figure")])

# ---------------- L5 body art ----------------
def B(code, cats, kinds, ex=None):
    E[code] = dict(axis=BODY, catalogues=cats, kinds=kinds)
B("L5-1", [WELL, [surl("Deq tattoo"), "Wikipedia search: Deq", "article on the Kurdish tattoo practice"], COM("Deq tattoo")],
  [SR("Arab facial tattooing (washm)", "Sub-types", "chin, forehead and hand tattoos of rural Arab and Bedouin women", "washm tattoo"),
   SR("Amazigh tattooing", "Sub-types", "Berber facial and hand tattoos of North Africa, related designs", "Berber tattoo"),
   SR("Dakkak", "Centres & workshops", "Kurdish and Dom (Ghorbati) women practitioners who travelled between villages", "Deq tattoo")])
B("L5-2", [WELL, SAHA, COM("Godna tattoo")],
  [SR("Baiga godna", "Sub-types", "full-body godna of Baiga women, Madhya Pradesh", "Baiga tattoo"),
   SR("Gond godna", "Sub-types", "Gond tattoo practice, central India", "Godna")])
X[("L5-2", "Naga tattooing")] = ("Sub-types", "Northeast India: facial and body tattoos marking head-hunting and status, Konyak and others")
X[("L5-2", "Apatani tattooing")] = ("Sub-types", "Northeast India: blue facial lines and nose plugs of Apatani women, Ziro Valley")
B("L5-3", [WP("Mehndi", "practice article"), COM("Mehndi designs"), WELL],
  [SR("Rajasthani mehndi", "Sub-types", "dense fine-line bridal designs covering hands and feet", "Rajasthani mehndi"),
   SR("Arabic mehndi", "Sub-types", "bold, spaced floral trails of Gulf style", "Arabic mehndi"),
   SR("Moroccan henna", "Sub-types", "geometric Amazigh-derived henna designs", "Moroccan henna"),
   W("Sojat", "Centres & workshops", "Pali, Rajasthan; centre of henna cultivation (GI tag Sojat Mehndi)")])
B("L5-4", [WP("Sak yant", "practice article"), COM("Sak yant"), WELL],
  [SR("Hah Taew (five lines)", "Sub-types", "the five-row yantra of protective verses", "Sak yant Hah Taew"),
   SR("Gao Yord (nine spires)", "Sub-types", "nine-peaked yantra, the commonest design", "Sak yant Gao Yord"),
   W("Wat Bang Phra", "Centres & workshops", "Nakhon Chai Si, Nakhon Pathom; monastery of the annual Wai Khru tattoo festival")])
B("L5-5", [COM("Mentawai tattoo"), WELL],
  [SR("Titi", "Sub-types", "the Mentawai name for tattoo: lines and plant motifs applied by sipaniti tattooists", "Mentawai tattoo"),
   W("Siberut", "Centres & workshops", "largest Mentawai island, West Sumatra; main area of traditional titi"),
   W("Mentawai people", "Centres & workshops", "people of the Mentawai Islands who practise titi")])
B("L5-6", [WELL, COM("Batok tattoo")],
  [SR("Pintados (Visayan tattooing)", "Sub-types", "full-body tattoos recorded by the Spanish in the Visayas (Boxer Codex)", "Pintados Visayan tattoo"),
   SR("Iban tattooing", "Sub-types", "Iban kelingai of Borneo: bunga terung (aubergine flower) and throat tattoos", "Iban tattoo"),
   M("Whang-od", "Makers", "Kalinga mambabatok (b. c. 1917) of Buscalan, last traditional batok master", "Whang-od Oggay"),
   W("Kalinga (province)", "Centres & workshops", "Cordillera, Luzon; Buscalan village and the batok revival")])
B("L5-7", [WELL, COM("Irezumi"), BUNKA],
  [W("Horimono", "Sub-types", "full-body Edo-period designs drawn from ukiyo-e heroes (Suikoden)", "Irezumi"),
   M("Horiyoshi III", "Makers", "(b. 1946) Yokohama irezumi master")])
X[("L5-7", "Ainu tattooing")] = D
X[("L5-7", "Hajichi")] = D
B("L5-8", [WELL, BM("scarification", "objects and images of scarification in the British Museum")],
  [W("Nuba peoples", "Sub-types", "Nuba scarification of the Sudanese Nuba Mountains, body cicatrices marking life stages"),
   W("Tammari people", "Sub-types", "Betammaribe facial scarification of Benin and Togo")])
X[("L5-8", "Yoruba facial marks")] = D
B("L5-9", [WELL, COM("Inuit tattoo")],
  [SR("Skin-stitching", "Sub-types", "soot-covered sinew thread drawn under the skin with a needle", "Inuit tattooing"),
   SR("Skin-poking", "Sub-types", "pigment pricked into the skin with a pointed tool", "Inuit tattooing"),
   W("Nunavut", "Centres & workshops", "Canada; centre of the 21st-century kakiniit revival")])
B("L5-10", [["https://teara.govt.nz/en/ta-moko-traditional-tattoo", "Te Ara: Tā moko", "Encyclopedia of New Zealand entry with images"], COM("Tā moko"), WELL],
  [SR("Moko kauae", "Sub-types", "women's chin moko", "Moko kauae"),
   SR("Uhi", "Sub-types", "bone chisels that cut grooved moko (uhi matarau)", "Uhi tā moko"),
   W("Mokomokai", "Collections", "preserved tattooed heads, now repatriated from museum collections to Te Papa")])
B("L5-11", [WELL, COM("Samoan tatau")],
  [SR("Su'a Sulu'ape Paulo II", "Makers", "(1950-1999) Samoan tufuga ta tatau who spread the peʻa abroad", "Sulu'ape Paulo II", 1)])
X[("L5-11", "peʻa")] = D
X[("L5-11", "veiqia (Fiji)")] = D
X[("L5-11", "malu")] = D
B("L5-12", [WELL, COM("Sailor tattoo"), [surl("American traditional tattoo"), "Wikipedia search: American traditional tattoo", "style articles"]],
  [M("Sutherland Macdonald", "Makers", "(1860-1942) London tattooist, patented the electric machine in Britain"),
   M("George Burchett", "Makers", "(1872-1953) 'King of Tattooists', London"),
   M("Sailor Jerry", "Makers", "Norman Collins (1911-1973), Honolulu; codified American traditional"),
   M("Lyle Tuttle", "Makers", "(1931-2019) San Francisco tattooist"),
   M("Don Ed Hardy", "Makers", "(b. 1945) bridged American traditional and Japanese styles")])
X[("L5-12", "Prison tattooing")] = D
X[("L5-12", "American traditional")] = D

# ---------------- L6 floor & sand ----------------
E["L6-1"] = dict(axis="Sub-types first, then centres and peoples.", catalogues=[[surl("Sona sand drawing"), "Wikipedia search: Sona", "article on Chokwe sand drawings"], COM("Sona Chokwe")],
    kinds=[SR("Lusona", "Sub-types", "a single drawing: one continuous line looped around a grid of dots, illustrating a tale", "Sona sand drawing"),
           W("Chokwe people", "Centres & workshops", "Angola, DR Congo and Zambia; the akwa kuta sona storytellers"),
           W("Lunda Norte Province", "Centres & workshops", "north-east Angola; core area of sona with Moxico")])
X[("L6-1", "Lusona")] = D
E["L6-2"] = dict(axis="Sub-types first, then centres and collections, then named singers (hataałii).", catalogues=[["https://www.wheelwright.org/", "Wheelwright Museum of the American Indian", "Santa Fe; founded with Hosteen Klah's sandpainting reproductions"], WP("Sandpainting", "practice article")],
    kinds=[W("Dry painting for healing ceremonies", "Sub-types", "Holy People drawn in coloured sand, used and erased within the ceremony", "Sandpainting"),
           W("Nightway", "Sub-types", "nine-night Yeibichai ceremony with its own sandpainting set"),
           W("Wheelwright Museum of the American Indian", "Collections", "Santa Fe; sandpainting tapestries and reproductions"),
           M("Hosteen Klah", "Makers", "(1867-1937) Navajo hataałii and weaver of sandpainting tapestries")])
E["L6-3"] = dict(axis="Sub-types first, then centres of the carpet tradition.", catalogues=[ICH, COM("Corpus Christi flower carpets")],
    kinds=[W("Infiorata", "Sub-types", "Italian flower-petal carpets for Corpus Domini (Genzano, Spello, Noto)"),
           W("Spycimierz", "Centres & workshops", "Łódź voivodeship, Poland; 2 km flower carpet, UNESCO ICH 2021 with other Polish villages"),
           W("Genzano di Roma", "Centres & workshops", "Lazio; Infiorata on the Via Italo Belardi since 1778"),
           W("La Orotava", "Centres & workshops", "Tenerife; Corpus Christi carpets of flowers and volcanic sand")])
X[("L6-3", "Flower carpets tradition for Corpus Christi processions")] = ("alias",)
