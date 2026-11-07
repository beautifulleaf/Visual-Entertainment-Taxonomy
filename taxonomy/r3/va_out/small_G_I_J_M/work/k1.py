# knowledge for G1 (metalwork), G2 (arms), G3 (jewellery)
# add rows: (name, group, gloss, url-or-wiki-article, is_maker)
from kutil import met, vam, bm, si, ch, wpl, U
K = {}
SUB, SCH, CEN, MAK = 'Sub-types', 'Schools & phases', 'Centres & workshops', 'Makers'
ISL = ['https://islamicart.museumwnf.org/', 'Discover Islamic Art (Museum With No Frontiers)', 'virtual museum of Islamic art objects from over 100 collections']

K['G1-1'] = dict(cats=[met('Khurasan brass'), vam('Khurasan brass'), ISL],
  add=[('Herat', CEN, 'chief centre of 12th–13th-c. inlaid brass in Khurasan (Afghanistan)', 'Herat', 0),
       ('Bobrinsky Bucket (Muhammad ibn ʿAbd al-Wahid and Masʿud ibn Ahmad, 1163)', 'Named inlaid vessels', 'cast and silver- and copper-inlaid brass bucket, Herat, 1163; State Hermitage Museum, St Petersburg', 'Bobrinsky_Bucket', 0),
       ('Wade Cup (Khurasan, c. 1200)', 'Named inlaid vessels', 'silver- and copper-inlaid brass cup with figural and animated-script bands; Cleveland Museum of Art', 'Wade_Cup', 0),
       ('Vaso Vescovali (Khurasan, c. 1200)', 'Named inlaid vessels', 'silver-inlaid high-tin bronze lidded bowl with planets and zodiac; British Museum, London', 'Vaso_Vescovali', 0),
       ('Muhammad ibn ʿAbd al-Wahid', MAK, 'caster of the Bobrinsky Bucket, Herat, 1163', 'Bobrinsky_Bucket', 1),
       ('Masʿud ibn Ahmad al-Naqqash', MAK, 'inlayer (naqqash) of the Bobrinsky Bucket, Herat, 1163', 'Bobrinsky_Bucket', 1)])
K['G1-2'] = dict(cats=[met('Mosul inlaid brass'), bm('Mosul'), ISL],
  add=[('Mosul', CEN, 'Zangid city on the Tigris whose 13th-c. inlay workshops gave the nisba al-Mawsili', 'Mosul', 0),
       ('Blacas Ewer (Shujaʿ ibn Manaʿ al-Mawsili, 1232)', 'Named inlaid vessels', 'brass ewer inlaid with silver and copper, Mosul, 1232; British Museum, London', 'Blacas_ewer', 0)])
K['G1-3'] = dict(cats=[met('Mamluk brass'), vam('Mamluk brass'), ISL],
  add=[('Cairo', CEN, 'Mamluk capital, main centre of inlaid brass for sultans and amirs', 'Cairo', 0),
       ('Damascus', CEN, 'second Mamluk centre of inlaid brass and of later export wares', 'Damascus', 0),
       ('Baptistère de Saint Louis (Muhammad ibn al-Zayn, c. 1320–40)', 'Named inlaid vessels', 'hammered brass basin inlaid with silver, gold and niello, Egypt or Syria; Musée du Louvre, Paris', 'Baptistère_de_Saint_Louis', 0),
       ('Muhammad ibn al-Zayn', MAK, 'Mamluk inlayer who signed the Baptistère de Saint Louis six times, early 14th c.', 'Baptistère_de_Saint_Louis', 1)])
K['G1-4'] = dict(cats=[met('Veneto-Saracenic'), vam('Veneto-Saracenic'), bm('Veneto-Saracenic')],
  add=[('Venice', CEN, 'trade hub long held to be the place of manufacture, hence the 19th-c. name', 'Venice', 0),
       ('Western Iran (Tabriz)', CEN, 'now credited with much of the group, with Mamluk Cairo and Damascus', 'Islamic_metalwork', 0)])
K['G1-5'] = dict(cats=[met('tombak'), vam('tombak'), ['https://www.topkapisarayi.gov.tr/en', 'Topkapı Palace Museum', 'the Ottoman court collections, Istanbul']],
  add=[('Istanbul court workshops (ehl-i hiref)', CEN, 'palace craft corporations of the Ottoman sultans, Istanbul, 16th–19th c.', 'Ottoman_art', 0),
       ('Tombak ewers and basins', SUB, 'gilt-copper ewer-and-basin (ibrik and leğen) sets for hand-washing', 'Tombac', 0),
       ('Mosque finials (alem) and lamps', SUB, 'gilt-copper crescents and fittings for domes, minarets and tombs', 'Tombac', 0)])
K['G1-6'] = dict(cats=[met('bidri'), vam('bidri'), bm('bidri')],
  add=[('Teh-nishan', SUB, 'deep-cut bidri inlay of silver wire and sheet set flush into the zinc alloy', 'Bidriware', 0),
       ('Zar-nishan', SUB, 'low-relief bidri inlay raised slightly above the ground', 'Bidriware', 0),
       ('Zarbuland', SUB, 'bidri inlay raised in high relief above the blackened ground', 'Bidriware', 0),
       ('Aftabi', SUB, 'bidri in which a cut-out silver sheet is overlaid on the ground', 'Bidriware', 0),
       ('Lucknow', CEN, 'Awadh centre of bidri from the 18th c., with dense floral grounds', 'Lucknow', 0),
       ('Purnia', CEN, 'Bihar centre of bidri huqqa bases, 18th–19th c.', 'Purnia', 0)])
K['G1-7'] = dict(cats=[met('koftgari'), vam('koftgari'), ['https://collections.royalarmouries.org/', 'Royal Armouries collections online', 'Leeds collection with Indian damascened arms']],
  add=[('Teh-nishan (true damascening)', SUB, 'gold or silver hammered into channels cut in the steel', 'Koftgari', 0),
       ('Koftgari (false damascening)', SUB, 'gold wire hammered onto a cross-hatched steel surface', 'Koftgari', 0),
       ('Sialkot', CEN, 'Punjab centre of koftgari arms and boxes', 'Sialkot', 0),
       ('Gujrat (Punjab)', CEN, 'Punjab centre of 19th-c. koftgari, with Sialkot', 'Gujrat,_Pakistan', 0),
       ('Jaipur', CEN, 'Rajasthan centre of koftgari arms and objects', 'Jaipur', 0),
       ('Alwar', CEN, 'Rajput court centre of damascened arms', 'Alwar', 0)])
K['G1-8'] = dict(cats=[['https://www.mhs.ox.ac.uk/epact/', 'Epact: Scientific Instruments of Medieval and Renaissance Europe', 'catalogue including Islamic astrolabes in European collections'], ['https://www.hsm.ox.ac.uk/collections-online', 'History of Science Museum, Oxford: collections online', 'the largest astrolabe collection (Lewis Evans)'], met('astrolabe')],
  add=[('Planispheric astrolabe', SUB, 'the standard engraved brass astrolabe with plates for latitudes', 'Astrolabe', 0),
       ('Celestial globe', SUB, 'cast or raised brass star globe engraved with constellations', 'Celestial_globe', 0),
       ('Qibla indicator (qiblanuma)', SUB, 'instrument for finding the direction of Mecca', 'Qibla', 0),
       ('Lahore astrolabe makers (family of Allahdad)', CEN, 'four generations of Lahore makers, 16th–17th c.', 'Astrolabe', 0),
       ('Maragha observatory', CEN, 'Ilkhanid observatory (1259) where al-Tabari made his globe', 'Maragheh_observatory', 0),
       ('Ahmad ibn Abi Bakr ibn al-Sarraj', MAK, 'Aleppo maker of the universal astrolabe of 1328–29 (Benaki Museum)', 'Astrolabe', 1),
       ('Muhammad Salih Tahtawi', MAK, 'Thatta (Sindh) maker of a seamless celestial globe, 1659–60', 'Celestial_globe', 1)])
K['G1-9'] = dict(cats=[vam('turquoise inlay Iran'), met('Iran turquoise')],
  add=[('Isfahan', CEN, 'main centre of firoozeh koobi copper and brass objects', 'Isfahan', 0),
       ('Mashhad', CEN, 'Khorasan centre of turquoise-chip work near the Nishapur mines', 'Mashhad', 0),
       ('Nishapur turquoise', SUB, 'the Khorasan turquoise used for the chips', 'Turquoise', 0)])
K['G1-10'] = dict(cats=[met('Safavid brass'), vam('Iran brass'), ISL],
  add=[('Inju inlaid brass', SCH, 'silver- and gold-inlaid brass of Shiraz under the Inju, 14th c.', 'Injuids', 0),
       ('Timurid brass', SCH, 'Herat inlaid brass jugs and candlesticks, 15th c.', 'Timurid_Empire', 0),
       ('Safavid tinned brass and copper', SCH, 'engraved tinned vessels with Persian verse bands, 16th–17th c.', 'Safavid_art', 0),
       ('Qajar cut steel', SCH, 'pierced and chiselled steel standards, plaques and helmets, 19th c.', 'Qajar_art', 0)])
K['G1-11'] = dict(cats=[['https://www.hermitagemuseum.org/wps/portal/hermitage/explore/collections/', 'State Hermitage Museum collections', 'holds most Sogdian silver from the Urals finds'], bm('Sogdian'), met('Sogdian')],
  add=[('Samarkand', CEN, 'Sogdian capital (Afrasiyab), 6th–8th c.', 'Samarkand', 0),
       ('Panjikent', CEN, 'Sogdian city of wall paintings and metalwork, 5th–8th c.', 'Panjakent', 0),
       ('Bukhara', CEN, 'Sogdian city-state on the Zeravshan', 'Bukhara', 0)])
K['G1-12'] = dict(cats=[['https://www.hermitagemuseum.org/wps/portal/hermitage/explore/collections/', 'State Hermitage Museum collections', 'Scythian gold and the Siberian Collection of Peter the Great'], met('Scythian'), bm('Scythian')],
  add=[('Scythian art', SCH, 'gold and bronze animal art of the Pontic steppe, 7th–3rd c. BC', 'Scythian_art', 0),
       ('Saka', SCH, 'eastern Scythian peoples of Central Asia (Issyk kurgan Golden Man)', 'Saka', 0),
       ('Pazyryk culture', SCH, 'Altai burials of felt, wood and gold in the animal style, 6th–3rd c. BC', 'Pazyryk_culture', 0),
       ('Ordos culture', SCH, 'animal-style bronzes of the northern Chinese frontier', 'Ordos_culture', 0),
       ('Siberian Collection of Peter the Great', 'Named treasures', 'gold belt plaques and torques collected 1715–26; State Hermitage Museum, St Petersburg', 'Scythian_art', 0),
       ('Tovsta Mohyla pectoral (4th c. BC)', 'Named treasures', 'Scythian gold pectoral from a kurgan near Pokrov; Museum of Historical Treasures of Ukraine, Kyiv', 'Scythian_art', 0)])
K['G1-13'] = dict(cats=[['https://baotanglichsu.vn/en', 'National Museum of Vietnamese History', 'the main collection of Đông Sơn drums, Hanoi'], met('Dong Son'), bm('Dong Son drum')],
  add=[('Heger type I', SUB, 'the classic Đông Sơn kettle-drum type in Franz Heger’s 1902 classification', 'Dong_Son_drum', 0),
       ('Ngọc Lũ drum', 'Named drums', 'bronze drum with star tympanum and feathered dancers; National Museum of Vietnamese History, Hanoi', 'Dong_Son_drum', 0),
       ('Hoàng Hạ drum', 'Named drums', 'Đông Sơn drum found in Hà Nam, 1937; National Museum of Vietnamese History, Hanoi', 'Dong_Son_drum', 0),
       ('Cổ Loa drum', 'Named drums', 'drum excavated at the Cổ Loa citadel, 1982; Hanoi', 'Cổ_Loa_Citadel', 0)])
K['G1-14'] = dict(cats=[vam('Burmese silver'), met('Burmese silver'), bm('Burma silver')],
  add=[('Rangoon (Yangon)', CEN, 'colonial-era export silversmithing centre, late 19th c.', 'Yangon', 0),
       ('Mandalay', CEN, 'royal capital of the Konbaung court silversmiths', 'Mandalay', 0),
       ('Thayetmyo', CEN, 'Upper Burma centre of repoussé silver', 'Thayetmyo', 0),
       ('Shan States silver', SCH, 'repoussé silver of the Shan principalities', 'Shan_State', 0)])
K['G1-15'] = dict(cats=[['https://digitalarchive.npm.gov.tw/', 'National Palace Museum Open Data, Taipei', 'Shang and Zhou bronze vessels of the Qing imperial collection'], met('Chinese bronze ritual vessel'), bm('ritual vessel China bronze')],
  add=[('Ding (cauldron)', SUB, 'tripod or four-legged cooking cauldron, the emblem of rank', 'Ding_(vessel)', 0),
       ('Gui (food vessel)', SUB, 'two-handled bowl for grain offerings', 'Gui_(vessel)', 0),
       ('Jue and gu (wine vessels)', SUB, 'tripod pouring cup and trumpet-shaped beaker, Shang', 'Jue_(vessel)', 0),
       ('Zun and you (wine vessels)', SUB, 'wine jars, often animal-shaped', 'Zun_(vessel)', 0),
       ('Bianzhong (bell chimes)', SUB, 'tuned sets of bronze bells', 'Bianzhong', 0),
       ('Erligang culture', SCH, 'early Bronze Age culture of Zhengzhou, 16th–14th c. BC', 'Erligang_culture', 0),
       ('Anyang (late Shang)', SCH, 'royal bronze workshops of Yinxu, 13th–11th c. BC', 'Yinxu', 0),
       ('Western Zhou bronzes', SCH, 'inscribed bronzes of the Zhou kings, 11th c.–771 BC', 'Western_Zhou', 0),
       ('Houmuwu ding (late Shang)', 'Named bronzes', 'largest Shang bronze, 832 kg, from Anyang; National Museum of China, Beijing', 'Houmuwu_ding', 0),
       ('Maogong ding (Western Zhou)', 'Named bronzes', 'cauldron with the longest bronze inscription (497 characters); National Palace Museum, Taipei', 'Mao_Gong_ding', 0),
       ('Bells of Marquis Yi of Zeng (433 BC)', 'Named bronzes', 'set of 65 bronze bells from the tomb at Suizhou; Hubei Provincial Museum, Wuhan', 'Marquis_Yi_of_Zeng', 0)])
K['G1-16'] = dict(cats=[met('Ordos'), bm('Ordos'), si('Ordos')],
  add=[('Belt plaques', SUB, 'openwork cast plaques of animals in combat', 'Ordos_culture', 0),
       ('Daggers and knives', SUB, 'cast bronze knives with animal-headed pommels', 'Ordos_culture', 0),
       ('Xiongnu', SCH, 'the steppe confederation whose art continues the Ordos tradition', 'Xiongnu', 0)])
K['G1-17'] = dict(cats=[['https://www.emuseum.go.kr/', 'e-Museum (National Museums of Korea)', 'collections of Korea’s national museums'], ['https://ich.unesco.org/en/lists', 'UNESCO Intangible Cultural Heritage Lists', 'element lists']],
  add=[('Bangjja yugi', SUB, 'forged high-tin bronze tableware, hammered from cast ingots', 'Anseong', 0),
       ('Jumul yugi', SUB, 'cast bronze tableware poured in moulds', 'Anseong', 0),
       ('Anseong', CEN, 'Gyeonggi town famed for cast yugi (Anseong matchum)', 'Anseong', 0),
       ('Napcheong', CEN, 'North Pyongan centre of forged bangjja yugi', 'Anseong', 0)])
K['G1-18'] = dict(cats=[['https://www.emuseum.go.kr/', 'e-Museum (National Museums of Korea)', 'collections of Korea’s national museums'], met('Goryeo silver inlaid')],
  add=[('Silver-inlaid bronze kundika', SUB, 'Goryeo ritual ewers inlaid with silver wire', 'Kundika', 0),
       ('Silver-inlaid incense burners', SUB, 'Goryeo bronze censers with inlaid Sanskrit and floral designs', 'Korean_art', 0),
       ('Kundika with silver-inlaid willow and waterfowl design (Goryeo, 12th c.)', 'Named inlaid works', 'National Treasure of Korea; National Museum of Korea, Seoul', 'Kundika', 0)])
K['G1-19'] = dict(cats=[bm('Ethiopian cross'), met('Ethiopian cross'), ['https://www.si.edu/search/collection-images?edan_q=Ethiopian%20cross', 'Smithsonian collections search', 'Ethiopian crosses']],
  add=[('Processional cross (meskel)', SUB, 'large cast or wood cross carried on a staff in liturgy', 'Processional_cross', 0),
       ('Hand cross', SUB, 'priest’s blessing cross with a handle', 'Ethiopian_Orthodox_Tewahedo_Church', 0),
       ('Neck cross (mäsqäl)', SUB, 'small pendant cross worn by the baptised', 'Ethiopian_Orthodox_Tewahedo_Church', 0),
       ('Lalibela', CEN, 'centre of cast-brass processional crosses, 12th–13th c.', 'Lalibela', 0),
       ('Gondar', CEN, '17th–18th-c. royal centre of silver crosses', 'Gondar', 0)])
K['G1-20'] = dict(cats=[bm('Akan gold weight'), met('Akan goldweight'), ['https://www.penn.museum/collections/', 'Penn Museum collections', 'large holdings of Asante goldweights']],
  add=[('Geometric goldweights', SUB, 'abstract weights of the early period (c. 1400–1700)', 'Akan_goldweights', 0),
       ('Figurative goldweights', SUB, 'proverb weights of people, animals and objects (c. 1700–1900)', 'Akan_goldweights', 0),
       ('Akan_goldweights', SUB, 'cast brass vessels for gold dust and shrine use', 'Akan_goldweights', 0),
       ('Forowa', SUB, 'sheet-brass boxes for shea butter', 'Akan_goldweights', 0),
       ('Gold-dust boxes and spoons (sanaa)', SUB, 'equipment of the goldweighing kit', 'Akan_goldweights', 0)])
K['G1-21'] = dict(cats=[['https://en.wikipedia.org/wiki/Igbo-Ukwu', 'Igbo-Ukwu (Wikipedia)', 'the three excavated sites and their finds'], bm('Igbo-Ukwu')],
  add=[('Igbo Isaiah', CEN, 'storehouse site excavated by Thurstan Shaw, 1959–60', 'Igbo-Ukwu', 0),
       ('Igbo Richard', CEN, 'burial chamber of a titled man with regalia', 'Igbo-Ukwu', 0),
       ('Igbo Jonah', CEN, 'disposal pit with bronzes and pottery', 'Igbo-Ukwu', 0),
       ('Roped pot on a stand', 'Named bronzes', 'leaded-bronze vessel with cast rope cage, 9th–10th c.; National Museum, Lagos', 'Igbo-Ukwu', 0)])
K['G1-22'] = dict(cats=[met('Luristan'), bm('Luristan'), ['https://collectie.wereldculturen.nl/', 'Wereldmuseum collection (NMVW)', 'Dutch world-culture museums']],
  add=[('Master-of-animals standard finials', SUB, 'openwork finials of a hero grasping beasts', 'Luristan_bronze', 0),
       ('Horse-bits with figural cheekpieces', SUB, 'bits with cast animal and demon cheekpieces', 'Luristan_bronze', 0),
       ('Votive pins and whetstone handles', SUB, 'disc-headed pins and animal-headed sockets', 'Luristan_bronze', 0),
       ('Surkh Dum-i Luri', CEN, 'temple site with thousands of votive pins, excavated 1938', 'Luristan_bronze', 0)])
K['G1-23'] = dict(cats=[bm('Oxus Treasure'), met('Achaemenid'), ['https://www.livius.org/', 'Livius.org', 'Achaemenid sources and objects']],
  add=[('Rhyton', SUB, 'horn-shaped drinking vessel ending in an animal forepart', 'Rhyton', 0),
       ('Phiale', SUB, 'fluted gold or silver libation bowl', 'Phiale', 0),
       ('Oxus Treasure (5th–4th c. BC)', 'Named treasures', '180 gold and silver pieces found on the Oxus, 1877–80; British Museum, London', 'Oxus_Treasure', 0),
       ('Apadana foundation tablets', 'Named treasures', 'gold and silver tablets of Darius I from Persepolis; National Museum of Iran, Tehran', 'Apadana', 0)])
K['G1-24'] = dict(cats=[met('Sasanian silver'), bm('Sasanian'), ['https://www.hermitagemuseum.org/wps/portal/hermitage/explore/collections/', 'State Hermitage Museum collections', 'the largest group of Sasanian silver']],
  add=[('Royal hunting plates', SUB, 'silver-gilt plates of the king hunting on horseback', 'Sasanian_art', 0),
       ('Ewers with dancing figures', SUB, 'silver-gilt ewers with Dionysiac dancers', 'Sasanian_art', 0),
       ('Cup of Chosroes', 'Named works', 'gold, rock-crystal and garnet cup, 6th–7th c.; Cabinet des Médailles, BnF, Paris', 'Sasanian_art', 0)])
K['G1-25'] = dict(cats=[met('Etruscan mirror'), bm('Etruscan mirror'), ['https://www.museoetru.it/', 'Museo Nazionale Etrusco di Villa Giulia', 'the Ficoroni Cista and Praenestine finds']],
  add=[('Ficoroni Cista (Novios Plautios, 4th c. BC)', 'Named works', 'engraved bronze cista from Praeneste with the Argonauts; Villa Giulia, Rome', 'Ficoroni_Cista', 0),
       ('Novios Plautios', MAK, 'bronzeworker who signed the Ficoroni Cista in Rome', 'Ficoroni_Cista', 1),
       ('Vulci', CEN, 'Etruscan city with major bronze workshops', 'Vulci', 0)])
K['G1-26'] = dict(cats=[met('Moche gold'), ['https://www.banrepcultural.org/museo-del-oro', 'Museo del Oro (Banco de la República)', 'pre-Hispanic goldwork, Bogotá'], si('Moche gold')],
  add=[('Depletion gilding', SUB, 'Moche technique of enriching gold at the surface of alloys', 'Moche_culture', 0),
       ('Royal Tombs of Sipán', CEN, 'Huaca Rajada burials of the Lord of Sipán, excavated 1987', 'Lord_of_Sipán', 0),
       ('Huacas del Sol y de la Luna', CEN, 'Moche capital on the Moche river', 'Huaca_del_Sol', 0)])
K['G1-27'] = dict(cats=[met('Sican'), si('Sican gold'), ['https://www.banrepcultural.org/museo-del-oro', 'Museo del Oro (Banco de la República)', 'pre-Hispanic goldwork, Bogotá']],
  add=[('Tumi', SUB, 'crescent-bladed ceremonial knife with a figure of Naylamp', 'Tumi', 0),
       ('Sicán funerary masks', SUB, 'hammered gold masks with winged eyes from elite tombs', 'Sican_culture', 0),
       ('Batán Grande', CEN, 'Sicán ceremonial centre and tomb site, Lambayeque', 'Sican_culture', 0)])
K['G1-28'] = dict(cats=[met('Chimu silver'), si('Chimu'), bm('Chimu')],
  add=[('Chan Chan', CEN, 'Chimú capital whose craftsmen were moved to Cusco after 1470', 'Chan_Chan', 0),
       ('Beakers (keros)', SUB, 'hammered silver and gold beakers with repoussé faces', 'Chimú_culture', 0),
       ('Ear spools', SUB, 'large gold ear ornaments of the Chimú elite', 'Chimú_culture', 0)])
K['G1-29'] = dict(cats=[met('Inca silver'), si('Inka silver'), bm('Inca')],
  add=[('Capacocha offerings', SUB, 'gold and silver figurines buried with child sacrifices on Andean peaks', 'Capacocha', 0),
       ('Silver llama figurines', SUB, 'cast and sheet llamas offered in highland shrines', 'Inca_Empire', 0),
       ('Tupu', SUB, 'shawl pins worn by Inca women', 'Inca_Empire', 0),
       ('Coricancha', CEN, 'Cusco sun temple once sheathed in gold, with a gold garden', 'Coricancha', 0)])
K['G1-30'] = dict(cats=[['https://www.banrepcultural.org/museo-del-oro', 'Museo del Oro (Banco de la República)', 'the largest Muisca collection, Bogotá'], met('Muisca'), si('Muisca')],
  add=[('Tunjo', SUB, 'flat votive figure cast by lost wax', 'Tunjo', 0),
       ('Muisca raft', 'Named works', 'gold raft of the zipa’s investiture, found 1969 at Pasca; Museo del Oro, Bogotá', 'Muisca_raft', 0),
       ('Lake Guatavita', CEN, 'sacred lake of offerings at the origin of El Dorado', 'Lake_Guatavita', 0)])
K['G1-31'] = dict(cats=[met('Peru silver colonial'), vam('Peruvian silver'), bm('Potosi silver')],
  add=[('Potosí', CEN, 'silver-mining city of Upper Peru and centre of church plate', 'Potosí', 0),
       ('Cusco', CEN, 'viceregal centre of church and domestic silver', 'Cusco', 0),
       ('Lima', CEN, 'viceregal capital and its silversmiths’ guild', 'Lima', 0),
       ('Sahumador', SUB, 'silver incense burner, often bird- or animal-shaped', 'Potosí', 0),
       ('Mate cups and bombillas', SUB, 'silver mate gourds and straws of the Andes and Río de la Plata', 'Mate_(drink)', 0)])
K['G1-32'] = dict(cats=[bm('La Tène'), met('Celtic La Tene'), ['https://www.mnh.si/', 'Corpus links via national museums', 'see museum holdings']],
  add=[('Early Style', SCH, 'first La Tène style of the 5th c. BC with Etruscan palmettes', 'La_Tène_culture', 0),
       ('Waldalgesheim style', SCH, 'continuous tendril style of the 4th c. BC', 'Waldalgesheim_chariot_burial', 0),
       ('Plastic style', SCH, 'three-dimensional cast ornament, 3rd c. BC', 'La_Tène_culture', 0),
       ('Sword style', SCH, 'engraved scabbard ornament of Hungary and Switzerland, 3rd c. BC', 'La_Tène_culture', 0),
       ('Basse-Yutz Flagons', 'Named works', 'pair of bronze flagons with coral inlay, Lorraine, c. 400 BC; British Museum, London', 'Basse-Yutz_Flagons', 0),
       ('Battersea Shield', 'Named works', 'bronze shield facing with red glass, found in the Thames, 350–50 BC; British Museum, London', 'Battersea_Shield', 0),
       ('Gundestrup cauldron', 'Named works', 'silver cauldron with gods and animals, 1st c. BC; National Museum of Denmark, Copenhagen', 'Gundestrup_cauldron', 0),
       ('Snettisham Hoard', 'Named works', 'gold torcs including the Great Torc, 1st c. BC; British Museum, London', 'Snettisham_Hoard', 0),
       ('Desborough Mirror', 'Named works', 'bronze mirror with mirror-style engraving, 50 BC–AD 50; British Museum, London', 'Desborough_Mirror', 0)])
K['G1-32']['cats'] = [bm('La Tène'), met('Celtic La Tene'), ['https://www.britishmuseum.org/collection/search?keyword=Iron%20Age%20Celtic', 'British Museum collection search', 'Iron Age Celtic metalwork']]
K['G1-33'] = dict(cats=[met('Merovingian'), bm('Migration period'), ['https://www.britishmuseum.org/collection/search?keyword=Frankish', 'British Museum collection search', 'Frankish metalwork']],
  add=[('Bow brooch', SUB, 'cast silver-gilt brooch of the Germanic dress', 'Bow_brooch', 0),
       ('Bracteate', SUB, 'thin gold disc pendant stamped with animal style', 'Bracteate', 0),
       ('Pietroasele Treasure', 'Named treasures', 'Gothic gold and garnet treasure, 4th–5th c.; National History Museum of Romania, Bucharest', 'Pietroasele_Treasure', 0),
       ('Treasure of Guarrazar', 'Named treasures', 'Visigothic votive crowns, 7th c.; Museo Arqueológico Nacional, Madrid, and Musée de Cluny', 'Treasure_of_Guarrazar', 0),
       ('Tomb of Childeric I', 'Named treasures', 'Frankish king’s grave goods found at Tournai, 1653; Cabinet des Médailles, Paris', 'Childeric_I', 0),
       ('Domagnano Treasure', 'Named treasures', 'Ostrogothic garnet jewellery, c. 500; Germanisches Nationalmuseum and British Museum', 'Domagnano_Treasure', 0)])
K['G1-34'] = dict(cats=[bm('Anglo-Saxon'), ['https://www.portableantiquities.org.uk/', 'Portable Antiquities Scheme database', 'recorded finds from England and Wales'], ['https://www.staffordshirehoard.org.uk/', 'Staffordshire Hoard', 'the hoard and its catalogue']],
  add=[('Trewhiddle style', SCH, 'niello-inlaid silver animal style of the 9th c.', 'Trewhiddle_style', 0),
       ('Sutton Hoo ship burial', 'Named treasures', 'royal grave of c. 625 with the great gold buckle; British Museum, London', 'Sutton_Hoo', 0),
       ('Staffordshire Hoard', 'Named treasures', 'over 3,500 gold and garnet war fittings, 7th c.; Birmingham Museum and Potteries Museum', 'Staffordshire_Hoard', 0),
       ('Kingston Brooch', 'Named treasures', 'gold and garnet composite disc brooch, 7th c.; World Museum, Liverpool', 'Kingston_Brooch', 0),
       ('Fuller Brooch', 'Named treasures', 'silver and niello disc brooch with the Five Senses, 9th c.; British Museum, London', 'Fuller_Brooch', 0),
       ('Alfred Jewel', 'Named treasures', 'gold, enamel and rock-crystal aestel head, 871–899; Ashmolean Museum, Oxford', 'Alfred_Jewel', 0)])
K['G1-35'] = dict(cats=[['https://samlinger.khm.uio.no/', 'Museum of Cultural History, Oslo: collections', 'Viking finds including the Oseberg ship'], bm('Viking'), ['https://www.unimus.no/portal/', 'Unimus (Norwegian university museums)', 'Norwegian archaeological objects']],
  add=[('Oseberg ship burial', 'Named finds', 'ship burial of 834 with carved wagon and sledges; Museum of Cultural History, Oslo', 'Oseberg_ship', 0),
       ('Jelling stones', 'Named finds', 'runestones of Gorm and Harald Bluetooth, 10th c.; UNESCO site, Jelling', 'Jelling_stones', 0),
       ('Cuerdale Hoard', 'Named finds', 'silver hoard of c. 905 from Lancashire; British Museum, London', 'Cuerdale_Hoard', 0),
       ('Vale of York Hoard', 'Named finds', 'silver hoard with a gilt cup, c. 927; British Museum and Yorkshire Museum', 'Vale_of_York_Hoard', 0),
       ('Urnes Stave Church', 'Named finds', 'church with 11th-c. carved portal of the Urnes style; UNESCO site', 'Urnes_Stave_Church', 0)])
K['G1-36'] = dict(cats=[met('Bilston enamel'), vam('South Staffordshire enamel'), ch('enamel Bilston')],
  add=[('Snuffboxes and patch boxes', SUB, 'the commonest painted-enamel wares', 'Snuff_box', 0),
       ('Étuis and bonbonnières', SUB, 'enamelled cases and sweet boxes', 'Étui', 0),
       ('Stephen Theodore Janssen', MAK, 'proprietor of the York House enamel works at Battersea, 1753–56', 'Stephen_Theodore_Janssen', 1),
       ('Simon-François Ravenet', MAK, 'French engraver of transfer-print plates for Battersea, 1750s', 'Simon_François_Ravenet', 1)])
K['G1-37'] = dict(cats=[met('ormolu'), ['https://wallacelive.wallacecollection.org/', 'Wallace Collection online', 'French 18th-c. gilt bronze and mounted porcelain'], ['https://www.rct.uk/collection/search', 'Royal Collection Trust collection search', 'French and English ormolu']],
  add=[('Furniture mounts', SUB, 'chased gilt-bronze mounts for commodes and desks', 'Ormolu', 0),
       ('Mantel clocks (pendules)', SUB, 'clock cases of gilt bronze, often figural', 'Ormolu', 0),
       ('Candelabra and girandoles', SUB, 'gilt-bronze lighting', 'Ormolu', 0),
       ('Soho Manufactory', CEN, 'Matthew Boulton’s Birmingham works, England’s leading ormolu maker from 1768', 'Soho_Manufactory', 0),
       ('Jacques Caffieri', MAK, 'Louis XV fondeur-ciseleur, 1678–1755', 'Jacques_Caffieri', 1),
       ('Pierre Gouthière', MAK, 'Paris chaser and gilder, inventor of matt gilding, 1732–1813', 'Pierre_Gouthière', 1),
       ('Pierre-Philippe Thomire', MAK, 'leading Empire bronzier, 1751–1843', 'Pierre-Philippe_Thomire', 1)])
K['G1-38'] = dict(cats=[['https://goskatalog.ru/portal/', 'Goskatalog (State Catalogue of the Museum Fund of Russia)', 'Russian museum objects incl. Kubachi metalwork'], met('Kubachi'), vam('Kubachi')],
  add=[('Niello silver', SUB, 'engraved silver filled with black niello', 'Kubachi,_Republic_of_Dagestan', 0),
       ('Engraved copper cauldrons', SUB, 'large engraved copper vessels of the Kubachi masters', 'Kubachi,_Republic_of_Dagestan', 0),
       ('Kubachi', CEN, 'Dargin mountain village of metalworkers in Dagestan', 'Kubachi,_Republic_of_Dagestan', 0)])
K['G1-39'] = dict(cats=[['https://goskatalog.ru/portal/', 'Goskatalog (State Catalogue of the Museum Fund of Russia)', 'Kasli castings in Russian museums']],
  add=[('Kasli', CEN, 'iron works in Chelyabinsk Oblast founded 1747, art casting from the 1810s', 'Kasli', 0),
       ('Kasli cast-iron pavilion (1900)', 'Named works', 'openwork pavilion shown at the Paris Exposition 1900; Yekaterinburg Museum of Fine Arts', 'Kasli', 0),
       ('Yevgeny Lanceray', MAK, 'sculptor whose horse and genre models were cast at Kasli', 'Kasli', 1),
       ('Peter Clodt von Jürgensburg', MAK, 'sculptor whose horse models were reproduced at Kasli', 'Peter_Clodt_von_Jürgensburg', 1)])
K['G1-40'] = dict(cats=[['https://goskatalog.ru/portal/', 'Goskatalog (State Catalogue of the Museum Fund of Russia)', 'Rostov finift in Russian museums']],
  add=[('Rostov the Great', CEN, 'centre of finift from the late 18th c.; Rostov Finift factory (1931)', 'Rostov', 0),
       ('Usolye enamel', SCH, 'painted enamel of Solvychegodsk, late 17th c., before Rostov', 'Solvychegodsk', 0)])
K['G1-41'] = dict(cats=[['https://goskatalog.ru/portal/', 'Goskatalog (State Catalogue of the Museum Fund of Russia)', 'Hutsul objects in Russian museums'], ['https://ich.unesco.org/en/lists', 'UNESCO Intangible Cultural Heritage Lists', 'element lists']],
  add=[('Toporets (Hutsul axe-staff)', SUB, 'brass-inlaid walking axe carried by Hutsul men', 'Hutsuls', 0),
       ('Cast brass crosses and jewellery', SUB, 'open-cast pendant crosses and clasps', 'Hutsuls', 0),
       ('Kosiv', CEN, 'Hutsul craft town in Ivano-Frankivsk Oblast', 'Kosiv', 0)])
K['G1-42'] = dict(cats=[['https://ich.unesco.org/en/lists', 'UNESCO Intangible Cultural Heritage Lists', 'Drotárstvo, wire craft and art (2023)']],
  add=[('Wire-mended pottery', SUB, 'the tinkers’ original craft of binding cracked earthenware', 'Tinker', 0),
       ('Wire objects and sculpture', SUB, 'household wares and later art objects in wire', 'Tinker', 0),
       ('Budatín Castle (Považie Museum), Žilina', CEN, 'home of the permanent exposition of Slovak tinkering', 'Budatín_Castle', 0)])
K['G1-43'] = dict(cats=[met('Limoges enamel'), vam('Limoges enamel'), ['https://wallacelive.wallacecollection.org/', 'Wallace Collection online', 'Limoges painted enamels']],
  add=[('Nardon Pénicaud', MAK, 'founder of Limoges painted enamel, c. 1470–1542', 'Limoges_enamel', 1),
       ('Jean de Court', MAK, 'Limoges painter-enameller, fl. 1555–85', 'Limoges_enamel', 1),
       ('Suzanne de Court', MAK, 'Limoges woman enameller, fl. c. 1600', 'Limoges_enamel', 1),
       ('Becket Casket (c. 1180)', 'Champlevé reliquaries', 'Limoges champlevé reliquary of Thomas Becket; Victoria and Albert Museum, London', 'Becket_Casket', 0)])
K['G1-44'] = dict(cats=[met('Augsburg silver'), vam('Augsburg silver'), ch('Augsburg')],
  add=[('Kunstschrank (art cabinet)', SUB, 'ebony cabinets with silver mounts assembled by Augsburg agents', 'Philipp_Hainhofer', 0),
       ('Philipp Hainhofer', CEN, 'Augsburg agent who organised art cabinets for princes, 1578–1647', 'Philipp_Hainhofer', 0),
       ('Biller family', MAK, 'Augsburg dynasty of silversmiths, late 17th–18th c.', 'Augsburg', 1),
       ('Matthäus Wallbaum', MAK, 'Augsburg silversmith of mounted cabinets and altars, 1554–1632', 'Augsburg', 1)])
K['G1-45'] = dict(cats=[vam('English silver'), met('English silver'), ['https://www.goldsmiths.co.uk/', 'The Goldsmiths’ Company', 'hallmarking records and collection']],
  add=[('Britannia standard', SCH, 'higher silver standard compulsory 1697–1720', 'Britannia_silver', 0),
       ('Worshipful Company of Goldsmiths', CEN, 'London assay office and guild since 1327', 'Worshipful_Company_of_Goldsmiths', 0),
       ('Birmingham Assay Office', CEN, 'assay office founded 1773 for Boulton’s trade', 'Birmingham_Assay_Office', 0),
       ('Nicholas Sprimont', MAK, 'Huguenot silversmith in London, later of Chelsea porcelain, 1716–71', 'Nicholas_Sprimont', 1),
       ('Paul Storr', MAK, 'Regency silversmith to Rundell, Bridge and Rundell, 1770–1844', 'Paul_Storr', 1)])
K['G1-46'] = dict(cats=[met('Byzantine enamel'), bm('Byzantine enamel'), ['https://www.basilicasanmarco.it/', 'Basilica di San Marco', 'the Pala d’Oro and Treasury']],
  add=[('Limburg Staurotheke', 'Named works', 'cross reliquary of 968–985 in cloisonné enamel; Limburg Cathedral Treasury', 'Limburg_Staurotheke', 0),
       ('Fieschi Morgan Staurotheke', 'Named works', 'enamelled cross reliquary, c. 800; Metropolitan Museum of Art, New York', 'Fieschi_Morgan_Staurotheke', 0),
       ('Holy Crown of Hungary', 'Named works', 'crown with Byzantine enamel plaques of 1074–77; Hungarian Parliament, Budapest', 'Holy_Crown_of_Hungary', 0),
       ('Khakhuli triptych', 'Named works', 'Georgian icon with over 100 Byzantine and Georgian enamels; Georgian National Museum, Tbilisi', 'Khakhuli_triptych', 0)])
K['G1-47'] = dict(cats=[['https://digitalarchive.npm.gov.tw/', 'National Palace Museum Open Data, Taipei', 'Ming and Qing imperial cloisonné'], met('Chinese cloisonné'), vam('cloisonné China')],
  add=[('Xuande-mark cloisonné', SCH, 'earliest reign-marked pieces, 1426–35', 'Cloisonné', 0),
       ('Jingtai cloisonné', SCH, 'the reign (1450–57) that gave cloisonné its name jingtailan', 'Jingtai_Emperor', 0),
       ('Qianlong imperial cloisonné', SCH, 'height of the court enamel workshops, 1736–95', 'Qianlong_Emperor', 0)])
K['G1-48'] = dict(cats=[met('Japanese cloisonné'), vam('Japanese cloisonné'), ['https://www.khalilicollections.org/', 'Khalili Collections', 'Japanese art of the Meiji period']],
  add=[('Kaji Tsunekichi', MAK, 'Owari reviver of cloisonné in the 1830s, 1803–83', 'Cloisonné', 1),
       ('Hayashi Kodenji', MAK, 'Nagoya cloisonné master of the Meiji era', 'Cloisonné', 1),
       ('Ando Cloisonné Company', CEN, 'Nagoya firm founded 1880 by Ando Jubei', 'Cloisonné', 0),
       ('Kyoto school (yūsen)', SCH, 'wired cloisonné with painterly detail (Namikawa Yasuyuki)', 'Namikawa_Yasuyuki', 0),
       ('Tokyo school (musen)', SCH, 'wireless cloisonné of Namikawa Sōsuke', 'Namikawa_Sōsuke', 0)])
K['G1-49'] = dict(cats=[met('Mosan'), vam('Mosan'), bm('Mosan')],
  add=[('Rainer of Huy', MAK, 'bronze-caster of the Liège baptismal font, 1107–18', 'Rainer_of_Huy', 1),
       ('Stavelot Triptych (c. 1156–58)', 'Named works', 'reliquary of the True Cross with Mosan enamels; Morgan Library and Museum, New York', 'Stavelot_Triptych', 0),
       ('Verdun Altar (Nicholas of Verdun, 1181)', 'Named works', '51 enamelled plaques of typology; Klosterneuburg Monastery', 'Verdun_Altar', 0),
       ('Shrine of the Three Kings (c. 1180–1225)', 'Named works', 'triple-sarcophagus reliquary begun by Nicholas of Verdun; Cologne Cathedral', 'Shrine_of_the_Three_Kings', 0),
       ('Baptismal font of St Bartholomew, Liège', 'Named works', 'brass font on twelve oxen by Rainer of Huy; St Bartholomew’s Church, Liège', 'Rainer_of_Huy', 0)])
CL = [['https://www.watch-museum.ch/', 'Musée international d’horlogerie, La Chaux-de-Fonds', 'watch and clock collection of the Jura'], ['https://www.bmimages.com/', 'British Museum images', '']]
K['G1-50'] = dict(cats=[['https://www.mih.ch/', 'Musée international d’horlogerie, La Chaux-de-Fonds', 'the reference collection of Swiss watchmaking'], ['https://www.patek.com/en/company/patek-philippe-museum', 'Patek Philippe Museum, Geneva', 'Geneva watches from the 16th c.'], ['https://ich.unesco.org/en/lists', 'UNESCO Intangible Cultural Heritage Lists', 'craftsmanship of mechanical watchmaking and art mechanics (2020)']],
  add=[('La Chaux-de-Fonds / Le Locle', CEN, 'watchmaking towns planned around the industry; UNESCO World Heritage 2009', 'La_Chaux-de-Fonds', 0),
       ('Vallée de Joux', CEN, 'Jura valley of complication makers (Le Brassus, Le Sentier)', 'Vallée_de_Joux', 0),
       ('Jaquet-Droz automata (1768–74)', 'Named works', 'The Writer, The Draughtsman and The Musician; Musée d’art et d’histoire, Neuchâtel', 'Jaquet-Droz_automata', 0),
       ('Pierre Jaquet-Droz', MAK, 'La Chaux-de-Fonds watchmaker and automaton maker, 1721–90', 'Pierre_Jaquet-Droz', 1),
       ('Ferdinand Berthoud', MAK, 'Neuchâtel-born marine chronometer maker, 1727–1807', 'Ferdinand_Berthoud', 1),
       ('Abraham-Louis Breguet', MAK, 'Neuchâtel-born watchmaker in Paris, inventor of the tourbillon, 1747–1823', 'Abraham-Louis_Breguet', 1),
       ('Vacheron Constantin', CEN, 'Geneva manufacture founded 1755', 'Vacheron_Constantin', 0),
       ('Patek Philippe', CEN, 'Geneva manufacture founded 1839', 'Patek_Philippe', 0),
       ('Audemars Piguet', CEN, 'Le Brassus manufacture founded 1875', 'Audemars_Piguet', 0)])
K['G1-51'] = dict(cats=[['https://www.deutsches-uhrenmuseum.de/', 'Deutsches Uhrenmuseum, Furtwangen', 'the Black Forest clock collection']],
  add=[('Cuckoo clock', SUB, 'carved-case clock with a calling cuckoo, from the mid-18th c.', 'Cuckoo_clock', 0),
       ('Shield clock (Schilduhr)', SUB, 'clock with painted wooden shield dial', 'Cuckoo_clock', 0),
       ('Furtwangen', CEN, 'clockmaking town, seat of the Deutsches Uhrenmuseum and clockmaking school (1850)', 'Furtwangen_im_Schwarzwald', 0),
       ('Triberg', CEN, 'Black Forest clockmaking and cuckoo-clock town', 'Triberg_im_Schwarzwald', 0),
       ('Junghans', CEN, 'Schramberg clock factory founded 1861', 'Junghans', 0)])
K['G1-52'] = dict(cats=[bm('clock London'), ['https://www.rmg.co.uk/collections', 'Royal Museums Greenwich collections', 'clocks and Harrison’s marine timekeepers'], vam('longcase clock')],
  add=[('Longcase clock', SUB, 'pendulum clock in a tall case, from c. 1660', 'Longcase_clock', 0),
       ('Bracket clock', SUB, 'spring-driven table clock', 'Bracket_clock', 0),
       ('Lantern clock', SUB, 'weight-driven brass wall clock of the 17th c.', 'Lantern_clock', 0),
       ('Worshipful Company of Clockmakers', CEN, 'London guild chartered 1631', 'Worshipful_Company_of_Clockmakers', 0),
       ('Ahasuerus Fromanteel', MAK, 'introduced the pendulum clock to England, 1658', 'Ahasuerus_Fromanteel', 1),
       ('Edward East', MAK, 'royal clockmaker to Charles I and II, 1602–97', 'Edward_East', 1),
       ('Joseph Knibb', MAK, 'Oxford and London clockmaker, 1640–1711', 'Joseph_Knibb', 1),
       ('Thomas Tompion', MAK, 'father of English clockmaking, 1639–1713', 'Thomas_Tompion', 1),
       ('Daniel Quare', MAK, 'London clock and barometer maker, 1649–1724', 'Daniel_Quare', 1),
       ('George Graham', MAK, 'Tompion’s successor, inventor of the deadbeat escapement, 1673–1751', 'George_Graham_(clockmaker)', 1)])
K['G1-53'] = dict(cats=[['https://www.uhrenmuseum-glashuette.com/', 'Deutsches Uhrenmuseum Glashütte', 'the museum of Glashütte watchmaking']],
  add=[('Ferdinand Adolph Lange', MAK, 'founder of Glashütte watchmaking, 1815–75', 'Ferdinand_Adolph_Lange', 1),
       ('Moritz Grossmann', MAK, 'Glashütte watchmaker and school founder, 1826–85', 'Glashütte', 1),
       ('Glashütte Original', CEN, 'successor of the GUB state works', 'Glashütte_Original', 0),
       ('Nomos Glashütte', CEN, 'Glashütte maker founded 1990', 'Nomos_Glashütte', 0)])
K['G1-54'] = dict(cats=[met('Morbier clock'), ['https://www.pop.culture.gouv.fr/', 'POP: la plateforme ouverte du patrimoine', 'French heritage objects incl. Comtoise clocks']],
  add=[('Morbier', CEN, 'Jura village where Comtoise clocks began c. 1680 (Mayet brothers)', 'Morbier', 0),
       ('Morez', CEN, 'Jura town of clockmaking and spectacles', 'Morez', 0),
       ('Lyre pendulum', SUB, 'embossed brass pendulum of the later Comtoise clock', 'Longcase_clock', 0)])
K['G1-55'] = dict(cats=[['https://digitaltmuseum.se/', 'DigitaltMuseum (Sweden)', 'Swedish museum objects incl. Mora clocks']],
  add=[('Mora', CEN, 'Dalarna parish whose villages made the clocks', 'Mora,_Sweden', 0),
       ('Östnor', CEN, 'village in Mora parish, main clockmaking village', 'Mora_clock', 0)])
K['G1-56'] = dict(cats=[['https://www.seiko-design.com/', 'Seiko Museum Ginza', 'wadokei collection'], met('Japanese clock'), bm('Japanese clock')],
  add=[('Pillar clock (shaku-dokei)', SUB, 'hanging clock with a vertical hour scale', 'Japanese_clock', 0),
       ('Bracket clock (yagura-dokei)', SUB, 'weight-driven clock on a pyramidal stand', 'Japanese_clock', 0),
       ('Pillow clock (makura-dokei)', SUB, 'spring-driven table clock', 'Japanese_clock', 0),
       ('Myriad year clock (Tanaka Hisashige, 1851)', 'Named works', 'six-faced clock; National Museum of Nature and Science, Tokyo', 'Myriad_year_clock', 0),
       ('Tanaka Hisashige', MAK, 'inventor and clockmaker, founder of Toshiba’s forerunner, 1799–1881', 'Tanaka_Hisashige', 1)])
K['G1-57'] = dict(cats=[['https://www.wienmuseum.at/', 'Wien Museum', 'includes the Uhrenmuseum Wien']],
  add=[('Laterndluhr', SUB, 'lantern-shaped Biedermeier regulator', 'Regulator_clock', 0),
       ('Dachluhr', SUB, 'regulator with roof-shaped pediment', 'Regulator_clock', 0),
       ('Gustav Becker', CEN, 'Silesian factory (1847) that mass-produced Vienna regulators', 'Gustav_Becker', 0),
       ('Uhrenmuseum Wien', CEN, 'Vienna clock museum with regulator collection', 'Vienna', 0)])
K['G1-58'] = dict(cats=[['https://www.nawcc.org/', 'National Watch and Clock Museum (NAWCC)', 'American clocks'], met('Connecticut shelf clock'), si('shelf clock')],
  add=[('Pillar-and-scroll shelf clock', SUB, 'Eli Terry’s patented shelf clock, c. 1816', 'Eli_Terry', 0),
       ('OG (ogee) clock', SUB, 'cheap brass-movement clock in an ogee-moulded case, 1840s on', 'Chauncey_Jerome', 0),
       ('Seth Thomas', MAK, 'Connecticut clockmaker, 1785–1859', 'Seth_Thomas_(clockmaker)', 1),
       ('Chauncey Jerome', MAK, 'maker of the brass-movement OG clock, 1793–1868', 'Chauncey_Jerome', 1),
       ('Silas Hoadley', MAK, 'Terry’s partner, 1786–1870', 'Eli_Terry', 1),
       ('Ansonia Clock Company', CEN, 'Connecticut and Brooklyn clock factory, 1851', 'Ansonia_Clock_Company', 0),
       ('Waterbury Clock Company', CEN, 'Connecticut maker, 1857', 'Waterbury_Clock_Company', 0)])
K['G1-59'] = dict(cats=[met('Morocco brass'), vam('Morocco brass'), bm('Morocco brass')],
  add=[('Fez', CEN, 'medina of brass and copper workshops (Seffarine square)', 'Fez,_Morocco', 0),
       ('Marrakesh', CEN, 'souk of lantern makers', 'Marrakesh', 0),
       ('Meknes', CEN, 'centre of damascened iron (dmasquinerie)', 'Meknes', 0),
       ('Tea trays and teapots', SUB, 'engraved brass trays (siniya) and teapots', 'Fez,_Morocco', 0)])
K['G1-60'] = dict(cats=[['https://kougeihin.jp/en/', 'Japan Traditional Crafts (kougeihin.jp)', 'designated traditional crafts incl. Nambu ironware']],
  add=[('Tetsubin', SUB, 'cast-iron kettle, the emblem of Nanbu ironware', 'Tetsubin', 0),
       ('Fūrin', SUB, 'cast-iron wind chime', 'Fūrin', 0),
       ('Morioka', CEN, 'castle town of the Nanbu domain and its kettle casters', 'Morioka', 0),
       ('Mizusawa (Ōshū)', CEN, 'second Nanbu ironware centre', 'Ōshū,_Iwate', 0)])
K['G1-61'] = dict(cats=[['https://www.klingenmuseum.de/', 'Deutsches Klingenmuseum, Solingen', 'blade and cutlery collection']],
  add=[('Etched sword blades', SUB, 'export blades of the 16th–18th c.', 'Solingen', 0),
       ('Zwilling J. A. Henckels', CEN, 'Solingen knife maker founded 1731', 'Zwilling_J._A._Henckels', 0),
       ('Wüsthof', CEN, 'Solingen knife maker founded 1814', 'Wüsthof', 0),
       ('Böker', CEN, 'Solingen knife maker (Heinr. Böker & Co.), 1869', 'Böker', 0)])
K['G1-62'] = dict(cats=[['https://www.pop.culture.gouv.fr/', 'POP: la plateforme ouverte du patrimoine', 'French heritage objects']],
  add=[('Sabatier', CEN, 'family of Thiers cutlers and kitchen-knife marks', 'Sabatier', 0),
       ('Laguiole', CEN, 'Aubrac village where the Laguiole knife was born, 1829', 'Laguiole', 0)])
K['G1-63'] = dict(cats=[['https://kougeihin.jp/en/', 'Japan Traditional Crafts (kougeihin.jp)', 'designated forged-blade crafts']],
  add=[('Yanagiba', SUB, 'long single-bevel slicing knife for sashimi', 'Japanese_kitchen_knife', 0),
       ('Deba', SUB, 'heavy single-bevel fish knife', 'Japanese_kitchen_knife', 0),
       ('Gyuto', SUB, 'double-bevel chef’s knife of Western form', 'Japanese_kitchen_knife', 0),
       ('Higonokami', SUB, 'folding friction knife of Miki', 'Higonokami', 0)])
K['G1-64'] = dict(cats=[['https://www.sheffieldmuseums.org.uk/', 'Sheffield Museums', 'the Hawley Collection of tools and cutlery']],
  add=[('Company of Cutlers in Hallamshire', CEN, 'Sheffield cutlers’ guild founded 1624', 'Company_of_Cutlers_in_Hallamshire', 0),
       ('Joseph Rodgers & Sons', CEN, 'leading 19th-c. Sheffield cutlers', 'Sheffield', 0),
       ('Benjamin Huntsman', MAK, 'inventor of crucible steel, 1704–76', 'Benjamin_Huntsman', 1),
       ('Harry Brearley', MAK, 'inventor of stainless steel in Sheffield, 1913', 'Harry_Brearley', 1)])
K['G1-65'] = dict(cats=[['https://www.mhs.ox.ac.uk/epact/', 'Epact: Scientific Instruments of Medieval and Renaissance Europe', 'catalogue of instruments before 1600'], ['https://www.hsm.ox.ac.uk/collections-online', 'History of Science Museum, Oxford', 'collections online'], ['https://catalogo.museogalileo.it/', 'Museo Galileo catalogue', 'Florence collection of scientific instruments']],
  add=[('Gualterus Arsenius', MAK, 'Louvain astrolabe maker, fl. 1554–79', 'Gualterus_Arsenius', 1),
       ('Georg Hartmann', MAK, 'Nuremberg instrument maker, 1489–1564', 'Georg_Hartmann', 1),
       ('Erasmus Habermel', MAK, 'Prague instrument maker to Rudolf II, d. 1606', 'Erasmus_Habermel', 1),
       ('John Dollond', MAK, 'London optician, achromatic lens patent 1758', 'John_Dollond', 1),
       ('Jesse Ramsden', MAK, 'London instrument maker, dividing engine, 1735–1800', 'Jesse_Ramsden', 1),
       ('Edward Nairne', MAK, 'London maker of electrical and optical instruments, 1726–1806', 'Edward_Nairne', 1)])
K['G1-66'] = dict(cats=[['https://en.wikipedia.org/wiki/Nachiarkoil_lamp', 'Nachiarkoil lamp (Wikipedia)', 'the GI-registered craft']],
  add=[('Kuthuvilakku', SUB, 'tall standing oil lamp with multiple wicks', 'Kuthuvilakku', 0),
       ('Annapakshi lamp', SUB, 'lamp crowned by a swan', 'Nachiarkoil_lamp', 0),
       ('Nachiarkoil_lamp', CEN, 'village near Kumbakonam, Tamil Nadu', 'Nachiarkoil_lamp', 0)])
K['G1-67'] = dict(cats=[['https://nationalcowboymuseum.org/', 'National Cowboy & Western Heritage Museum', 'Western silver and saddlery']],
  add=[('Trophy buckles', SUB, 'engraved silver rodeo prize buckles', 'Belt_buckle', 0),
       ('Spurs and bits', SUB, 'silver-overlaid horse gear', 'Spur', 0),
       ('Edward H. Bohlin', MAK, 'Hollywood saddle and silver maker, 1895–1980', 'Edward_H._Bohlin', 1),
       ('Montana Silversmiths', CEN, 'Columbus, Montana, maker of rodeo buckles, 1973', 'Belt_buckle', 0)])
ARM = [['https://collections.royalarmouries.org/', 'Royal Armouries collections online', 'the UK national collection of arms and armour'], ['https://wallacelive.wallacecollection.org/', 'Wallace Collection online', 'European and Oriental arms and armour']]
K['G2-1'] = dict(cats=[met('Islamic arms armor'), ARM[0], ARM[1]],
  add=[('Shamshir', SUB, 'curved Persian sabre', 'Shamshir', 0), ('Kilij', SUB, 'Ottoman sabre with a flared tip', 'Kilij', 0),
       ('Yatagan', SUB, 'Ottoman forward-curved short sword', 'Yatagan', 0), ('Talwar', SUB, 'Indian sabre with disc pommel', 'Talwar', 0),
       ('Khanjar', SUB, 'double-curved dagger', 'Khanjar', 0), ('Wootz steel', SUB, 'crucible steel with watered pattern used for blades', 'Wootz_steel', 0),
       ('Isfahan', CEN, 'Safavid centre of sword-making (Asadullah)', 'Isfahan', 0), ('Damascus', CEN, 'Syrian centre giving its name to watered blades', 'Damascus_steel', 0)])
K['G2-2'] = dict(cats=[['https://collectie.wereldculturen.nl/', 'Wereldmuseum collection (NMVW)', 'thousands of krisses from Indonesia'], met('kris'), ['https://ich.unesco.org/en/lists', 'UNESCO Intangible Cultural Heritage Lists', 'Indonesian Kris (2008)']],
  add=[('Pamor', SUB, 'pattern-welded layered blade of iron and meteoric nickel', 'Kris', 0),
       ('Surakarta', CEN, 'Javanese court centre of kris smiths (empu)', 'Surakarta', 0),
       ('Yogyakarta', CEN, 'Javanese court centre of kris smiths', 'Yogyakarta', 0),
       ('Aeng Tong-Tong (Sumenep, Madura)', CEN, 'village of kris smiths on Madura', 'Sumenep_Regency', 0)])
K['G2-3'] = dict(cats=[['https://colbase.nich.go.jp/', 'ColBase (National Institutes for Cultural Heritage, Japan)', 'Tokyo, Kyoto, Nara and Kyushu national museum objects'], ['https://bunka.nii.ac.jp/', 'Cultural Heritage Online (bunka.nii.ac.jp)', 'Japan’s designated cultural properties'], met('Japanese sword')],
  add=[('Sanjō Munechika', MAK, 'Kyoto smith of the Heian period, Yamashiro tradition', 'Sanjō_Munechika', 1),
       ('Masamune', MAK, 'Sagami smith of the Sōshū tradition, c. 1264–1343', 'Masamune', 1),
       ('Muramasa', MAK, 'Ise smith of the Muromachi period', 'Muramasa', 1),
       ('Nagasone Kotetsu', MAK, 'Edo shintō smith, 1597–1678', 'Nagasone_Kotetsu', 1),
       ('Minamoto no Kiyomaro', MAK, 'late-Edo shinshintō smith, 1813–55', 'Japanese_sword', 1),
       ('Dōjigiri Yasutsuna', 'Tenka-Goken (five great swords)', 'tachi by Yasutsuna, Heian; National Treasure; Tokyo National Museum', 'Tenka-Goken', 0),
       ('Mikazuki Munechika', 'Tenka-Goken (five great swords)', 'tachi by Sanjō Munechika, Heian; National Treasure; Tokyo National Museum', 'Tenka-Goken', 0),
       ('Ōdenta Mitsuyo', 'Tenka-Goken (five great swords)', 'tachi by Miike Mitsuyo, Heian; National Treasure; Maeda Ikutokukai', 'Tenka-Goken', 0),
       ('Onimaru Kunitsuna', 'Tenka-Goken (five great swords)', 'tachi by Awataguchi Kunitsuna, Kamakura; Imperial Household collection', 'Tenka-Goken', 0),
       ('Juzumaru Tsunetsugu', 'Tenka-Goken (five great swords)', 'tachi by Aoe Tsunetsugu, Kamakura; Important Cultural Property; Hontsu-ji, Amagasaki', 'Tenka-Goken', 0)])
K['G2-4'] = dict(cats=[['https://colbase.nich.go.jp/', 'ColBase (National Institutes for Cultural Heritage, Japan)', 'sword fittings in the national museums'], met('tsuba'), bm('tsuba')],
  add=[('Tsuba', SUB, 'sword guard', 'Tsuba', 0), ('Menuki', SUB, 'hilt ornaments under the binding', 'Menuki', 0),
       ('Tsuba', SUB, 'handle of the utility knife carried in the scabbard', 'Tsuba', 0),
       ('Gotō school', SCH, 'shogunal fittings makers founded by Gotō Yūjō (1440–1512)', 'Tsuba', 0),
       ('Umetada school', SCH, 'Kyoto school of fittings and blades, Momoyama period', 'Tsuba', 0),
       ('Nara school', SCH, 'Edo machibori school of carved fittings', 'Tsuba', 0),
       ('Yokoya school', SCH, 'Edo school of katakiri-bori engraving (Yokoya Sōmin)', 'Tsuba', 0),
       ('Kanō Natsuo', MAK, 'Meiji metal artist and maker of fittings, 1828–98', 'Kanō_Natsuo', 1)])
K['G2-5'] = dict(cats=[met('Milan armor'), ARM[0], ARM[1]],
  add=[('Missaglia family', MAK, 'Milanese armourers (Tommaso and Antonio Missaglia), 15th c.', 'Filippo_Negroli', 1),
       ('Filippo Negroli', MAK, 'Milanese armourer of embossed parade armour, c. 1510–79', 'Filippo_Negroli', 1),
       ('Pompeo della Cesa', MAK, 'Milanese armourer of etched armour, fl. 1572–93', 'Filippo_Negroli', 1),
       ('Burgonet of Guidobaldo II (Filippo Negroli, 1543)', 'Named armours', 'embossed steel helmet with sea monster; Metropolitan Museum of Art, New York', 'Filippo_Negroli', 0)])
K['G2-6'] = dict(cats=[['https://www.finna.fi/', 'Finna (Finnish museums, libraries and archives)', 'puukko knives in Finnish museums']],
  add=[('Kauhava', CEN, 'Ostrobothnian town of puukko smiths', 'Kauhava', 0),
       ('Fiskars', CEN, 'ironworks village and knife maker since 1649', 'Fiskars', 0),
       ('Marttiini', CEN, 'Rovaniemi knife maker founded 1928', 'Marttiini', 0),
       ('Leuku', SUB, 'large Sámi knife related to the puukko', 'Puukko', 0)])
K['G2-7'] = dict(cats=[['https://www.dpm.org.cn/', 'Palace Museum, Beijing', 'imperial arms']],
  add=[('Jian', SUB, 'straight double-edged sword', 'Jian', 0), ('Dao', SUB, 'single-edged sabre', 'Dao_(sword)', 0),
       ('Ou Yezi', MAK, 'legendary swordsmith of the Spring and Autumn period credited with founding Longquan sword-making', 'Longquan', 1),
       ('Longquan', CEN, 'Zhejiang city of swords and celadon', 'Longquan', 0)])
K['G2-8'] = dict(cats=[['https://collections.royalarmouries.org/', 'Royal Armouries collections online', 'kukris and Gurkha arms'], met('kukri')],
  add=[('Sirupate', SUB, 'slender kukri with a leaf-shaped blade', 'Kukri', 0), ('Chainpure', SUB, 'kukri type named after Chainpur', 'Kukri', 0),
       ('Bhojpur', CEN, 'eastern Nepal centre of kukri smiths', 'Bhojpur_District,_Nepal', 0), ('Kami (smith caste)', CEN, 'Nepali smiths who forge kukris', 'Kami_(caste)', 0)])
K['G2-9'] = dict(cats=[['https://kougeihin.jp/en/', 'Japan Traditional Crafts (kougeihin.jp)', 'Miyakonojō bows']],
  add=[('Daikyū', SUB, 'the full-length (over 2 m) bow of kyūdō', 'Yumi', 0), ('Miyakonojō', CEN, 'Miyazaki city that makes most Japanese bows', 'Miyakonojō', 0),
       ('Shibata Kanjūrō', MAK, 'hereditary line of imperial bowyers in Kyoto', 'Kanjuro_Shibata_XX', 1)])
K['G2-10'] = dict(cats=[['https://www.emuseum.go.kr/', 'e-Museum (National Museums of Korea)', 'Korean bows and archery equipment']],
  add=[('Gungsi', SUB, 'the designated bow-making craft (gungsi, also arrow-making yesi)', 'Gakgung', 0),
       ('Yecheon', CEN, 'Gyeongbuk centre of traditional bow-making', 'Yecheon_County', 0)])
K['G2-11'] = dict(cats=[met('Gothic armor'), ARM[0], ['https://www.khm.at/en/visit/collections/imperial-armoury', 'Kunsthistorisches Museum: Imperial Armoury', 'Hofjagd- und Rüstkammer, Vienna']],
  add=[('Maximilian armour', SUB, 'fluted armour of the early 16th c.', 'Maximilian_armour', 0),
       ('Augsburg', CEN, 'armourers’ city of the Helmschmid family', 'Augsburg', 0), ('Innsbruck', CEN, 'imperial court armoury of Maximilian I', 'Innsbruck', 0),
       ('Nuremberg', CEN, 'guild centre of munition and fine armour', 'Nuremberg', 0), ('Landshut', CEN, 'Bavarian armour centre (Wolfgang Grosschedel)', 'Landshut', 0),
       ('Lorenz Helmschmid', MAK, 'Augsburg armourer to Maximilian I, c. 1445–1516', 'Lorenz_Helmschmid', 1),
       ('Kolman Helmschmid', MAK, 'Augsburg armourer, 1471–1532', 'Kolman_Helmschmid', 1),
       ('Konrad Seusenhofer', MAK, 'Innsbruck court armourer, d. 1517', 'Konrad_Seusenhofer', 1)])
K['G2-12'] = dict(cats=[['https://colbase.nich.go.jp/', 'ColBase (National Institutes for Cultural Heritage, Japan)', 'armour in the national museums'], ['https://bunka.nii.ac.jp/', 'Cultural Heritage Online (bunka.nii.ac.jp)', 'designated armours'], met('Japanese armor')],
  add=[('Ō-yoroi', SUB, 'great box-shaped armour of mounted archers, Heian–Kamakura', 'Ō-yoroi', 0), ('Dō-maru', SUB, 'wrap-around armour fastened at the side', 'Dō-maru', 0),
       ('Japanese_armour', SUB, 'armour opening at the back', 'Japanese_armour', 0), ('Tōsei gusoku', SUB, 'plate armour of the Sengoku and Edo periods', 'Japanese_armour', 0),
       ('Myōchin school', SCH, 'armourers’ school of iron helmets and masks', 'Japanese_armour', 0), ('Saotome school', SCH, 'Edo-period helmet makers', 'Japanese_armour', 0)])
K['G3-1'] = dict(cats=[met('Fatimid gold'), vam('Fatimid'), ['https://www.davidmus.dk/en', 'The David Collection, Copenhagen', 'Islamic jewellery']],
  add=[('Filigree crescent earrings', SUB, 'hollow gold crescents of filigree and granulation', 'Fatimid_art', 0), ('Cairo', CEN, 'Fatimid capital (969–1171)', 'Cairo', 0)])
K['G3-2'] = dict(cats=[vam('Mughal jewellery'), ['https://www.khalilicollections.org/', 'Khalili Collections', 'Mughal and Indian jewels'], ['https://www.al-sabah-collection.com/', 'The al-Sabah Collection, Kuwait', 'jewelled arts of India']],
  add=[('Kundan', SUB, 'gem-setting in pure gold foil', 'Kundan', 0), ('Meenakari', SUB, 'enamelling of the backs of jewels', 'Meenakari', 0),
       ('Jadau', SUB, 'gem-set gold jewellery', 'Kundan', 0), ('Sarpech', SUB, 'turban ornament', 'Sarpech', 0),
       ('Wine cup of Shah Jahan (1657)', 'Named jewels and jewelled objects', 'white nephrite jade cup; Victoria and Albert Museum, London', 'Wine_cup_of_Shah_Jahan', 0),
       ('Mughal Emerald (1695)', 'Named jewels and jewelled objects', 'carved emerald of 217.80 carats; Museum of Islamic Art, Doha', 'Mughal_Emerald', 0)])
K['G3-3'] = dict(cats=[met('Yemen silver jewelry'), bm('Bedouin jewellery'), vam('Oman silver')],
  add=[('Sanaʿa', CEN, 'Yemeni centre of Jewish silversmiths until 1949', 'Sanaa', 0), ('Nizwa', CEN, 'Omani silver market town', 'Nizwa', 0),
       ('Hirz (amulet case)', SUB, 'silver Qur’an case worn as amulet', 'Amulet', 0)])
K['G3-4'] = dict(cats=[met('Berber jewelry'), bm('Berber jewellery'), ['https://www.jardinmajorelle.com/en/pierre-berge-museum-of-berber-arts/', 'Pierre Bergé Museum of Berber Arts, Marrakesh', 'Amazigh jewellery collection']],
  add=[('Tizerzai (fibulae)', SUB, 'pairs of triangular silver fibulae joined by chains', 'Fibula_(brooch)', 0), ('Agadez cross', SUB, 'Tuareg pendant cross', 'Tuareg_people', 0),
       ('Beni Yenni (Kabylia)', CEN, 'Kabyle village of enamelled silver', 'Beni_Yenni', 0), ('Tiznit', CEN, 'Souss silver town', 'Tiznit', 0), ('Agadez', CEN, 'Tuareg smiths’ town in Niger', 'Agadez', 0)])
K['G3-5'] = dict(cats=[met('Javanese gold'), ['https://www.museumnasional.or.id/', 'Museum Nasional Indonesia', 'the Wonoboyo hoard and Old Javanese gold'], ['https://collectie.wereldculturen.nl/', 'Wereldmuseum collection (NMVW)', 'Javanese gold in Dutch museums']],
  add=[('Wonoboyo hoard', 'Named treasures', 'gold and silver hoard of the 9th c. found near Prambanan, 1990; Museum Nasional Indonesia, Jakarta', 'Wonoboyo_hoard', 0),
       ('Upavita (sacred-thread clasp)', SUB, 'gold clasp of the Brahmanical sacred thread', 'Upanayana', 0)])
K['G3-6'] = dict(cats=[met('Miao silver'), bm('Miao silver')],
  add=[('Horn headdress', SUB, 'silver buffalo-horn crown worn at festivals', 'Miao_people', 0), ('Neck rings', SUB, 'stacked forged silver torques', 'Miao_people', 0),
       ('Shidong (Taijiang)', CEN, 'Guizhou town of Miao silversmiths and the Sisters’ Meal festival', 'Taijiang_County', 0), ('Kaili', CEN, 'capital of Qiandongnan, centre of Miao silver', 'Kaili,_Guizhou', 0)])
GOLD = ['https://www.banrepcultural.org/museo-del-oro', 'Museo del Oro (Banco de la República)', 'over 34,000 pre-Hispanic gold objects, Bogotá']
K['G3-8'] = dict(cats=[GOLD, met('Tairona'), si('Tairona')],
  add=[('Bat-man pendants', SUB, 'cast figures of a man with bat attributes', 'Tairona', 0), ('Eagle pendants', SUB, 'cast spread-winged birds', 'Tairona', 0),
       ('Ciudad Perdida', CEN, 'Tairona city of the Sierra Nevada, c. 800', 'Ciudad_Perdida', 0)])
K['G3-9'] = dict(cats=[GOLD, ['https://www.culturaydeporte.gob.es/museodeamerica/', 'Museo de América, Madrid', 'the Quimbaya Treasure'], met('Quimbaya')],
  add=[('Quimbaya Treasure', 'Named treasures', '122 gold objects found at La Soledad, 1890; Museo de América, Madrid', 'Quimbaya_Treasure', 0),
       ('Poporo Quimbaya', 'Named treasures', 'gold lime container, 300 AD; Museo del Oro, Bogotá', 'Poporo_Quimbaya', 0)])
K['G3-10'] = dict(cats=[GOLD, met('Calima')], add=[('Calima diadems', SUB, 'hammered gold crowns with dangling plaques', 'Calima_culture', 0)])
K['G3-11'] = dict(cats=[GOLD, met('Tolima')], add=[('Anthropozoomorphic pendants', SUB, 'flat cast figures with splayed limbs and anchor tails', 'Museo_del_Oro', 0)])
K['G3-12'] = dict(cats=[['https://www.penn.museum/collections/', 'Penn Museum collections', 'the Sitio Conte gold'], met('Cocle gold'), si('Panama gold')],
  add=[('Sitio Conte', CEN, 'Coclé cemetery excavated by Harvard and Penn, 1930–40', 'Sitio_Conte', 0), ('El Caño', CEN, 'Coclé cemetery with gold-rich burials', 'Sitio_Conte', 0)])
K['G3-13'] = dict(cats=[['https://www.inah.gob.mx/', 'INAH (Instituto Nacional de Antropología e Historia)', 'Mexican archaeological collections'], met('Mixtec gold'), bm('Mixtec_culture')],
  add=[('Monte Albán Tomb 7 treasure', 'Named treasures', 'Mixtec gold, jade and turquoise reburied at Monte Albán, found 1932; Museo de las Culturas de Oaxaca', 'Monte_Albán', 0),
       ('Labrets and lip plugs', SUB, 'cast gold lip ornaments', 'Mixtec_culture', 0)])
K['G3-14'] = dict(cats=[si('Mapuche silver'), ['https://www.precolombino.cl/', 'Museo Chileno de Arte Precolombino', 'Mapuche silver collection']],
  add=[('Trapelacucha', SUB, 'pectoral of chains and plaques', 'Mapuche', 0), ('Trarilonco', SUB, 'silver headband', 'Mapuche', 0),
       ('Tupu', SUB, 'large disc-headed shawl pin', 'Mapuche', 0), ('Rütrafe', CEN, 'Mapuche silversmiths', 'Mapuche', 0)])
K['G3-15'] = dict(cats=[si('Navajo silver'), ['https://heard.org/', 'Heard Museum, Phoenix', 'Native American jewellery'], ['https://www.wheelwright.org/', 'Wheelwright Museum of the American Indian', 'Southwestern silver collection']],
  add=[('Concho belt', SUB, 'belt of stamped silver discs', 'Concho', 0), ('Squash blossom necklace', SUB, 'beaded necklace with blossoms and a naja', 'Squash_blossom_necklace', 0),
       ('Ketoh (bow guard)', SUB, 'silver-mounted leather wrist guard', 'Bow_guard', 0),
       ('Atsidi Sani', MAK, 'first known Navajo silversmith, c. 1830–1918', 'Atsidi_Sani', 1)])
K['G3-16'] = dict(cats=[si('Zuni jewelry'), ['https://heard.org/', 'Heard Museum, Phoenix', 'Native American jewellery']],
  add=[('Needlepoint', SUB, 'tiny pointed turquoise stones set in rows', 'Zuni_people', 0), ('Petit point', SUB, 'small teardrop stones in clusters', 'Zuni_people', 0),
       ('Channel inlay', SUB, 'stones set in silver channels', 'Zuni_people', 0), ('Mosaic inlay', SUB, 'shell, jet and turquoise set as mosaic figures', 'Zuni_people', 0)])
K['G3-17'] = dict(cats=[si('heishi'), ['https://heard.org/', 'Heard Museum, Phoenix', 'Native American jewellery']],
  add=[('Shell heishi', SUB, 'disc beads of spiny oyster, olivella and clam shell', 'Kewa_Pueblo,_New_Mexico', 0), ('Turquoise heishi', SUB, 'disc beads of turquoise', 'Kewa_Pueblo,_New_Mexico', 0)])
K['G3-18'] = dict(cats=[si('trade silver'), ['https://www.royalontariomuseum.ca/', 'Royal Ontario Museum', 'fur-trade silver']],
  add=[('Gorgets', SUB, 'crescent breast ornaments', 'Trade_silver', 0), ('Brooches', SUB, 'ring and disc brooches sewn on clothing', 'Trade_silver', 0),
       ('Armbands', SUB, 'silver arm bands given as diplomatic gifts', 'Trade_silver', 0), ('Montreal silversmiths', CEN, 'makers for the North West Company trade', 'Trade_silver', 0)])
K['G3-19'] = dict(cats=[['https://collections.museumsvictoria.com.au/', 'Museums Victoria Collections', 'Aboriginal pearl-shell ornaments'], bm('pearl shell Kimberley')],
  add=[('Bardi and Dampier Peninsula carvers', CEN, 'pearl-shell engravers of the West Kimberley coast', 'Bardi_people', 0)])
K['G3-20'] = dict(cats=[['https://www.fabergemuseum.ru/en', 'Fabergé Museum, St Petersburg', 'the Link of Times collection of Imperial eggs'], ['https://www.rct.uk/collection/search', 'Royal Collection Trust collection search', 'the British royal Fabergé collection'], ['https://en.wikipedia.org/wiki/Fabergé_egg', 'Fabergé egg (Wikipedia)', 'list of all Imperial and other Fabergé eggs and their locations']],
  add=[('August Holmström', MAK, 'Fabergé head jeweller, 1829–1903', 'August_Holmström', 1),
       ('Hen egg (1885)', 'Imperial Easter eggs', 'first Imperial egg, for Maria Feodorovna; Fabergé Museum, St Petersburg', 'Hen_(Fabergé_egg)', 0),
       ('Renaissance egg (1894)', 'Imperial Easter eggs', 'agate egg, last given by Alexander III; Fabergé Museum, St Petersburg', 'Renaissance_(Fabergé_egg)', 0),
       ('Coronation egg (1897)', 'Imperial Easter eggs', 'guilloché egg with coronation-coach surprise; Fabergé Museum, St Petersburg', 'Coronation_(Fabergé_egg)', 0),
       ('Lilies of the Valley egg (1898)', 'Imperial Easter eggs', 'pink enamel Art Nouveau egg; Fabergé Museum, St Petersburg', 'Lilies_of_the_Valley_(Fabergé_egg)', 0),
       ('Moscow Kremlin egg (1906)', 'Imperial Easter eggs', 'largest Imperial egg, with a model of the Dormition Cathedral; Kremlin Armoury, Moscow', 'Moscow_Kremlin_(Fabergé_egg)', 0),
       ('Winter egg (1913)', 'Imperial Easter eggs', 'rock-crystal egg with frost engraving; private collection', 'Winter_(Fabergé_egg)', 0)])
K['G3-21'] = dict(cats=[vam('hair jewellery'), met('hairwork')],
  add=[('Vamhus', CEN, 'Dalarna village whose women travelled Europe making hair jewellery', 'Vamhus', 0), ('Hair pictures', SUB, 'memorial pictures worked from hair', 'Mourning_jewelry', 0)])
K['G3-22'] = dict(cats=[vam('temple jewellery'), ['https://en.wikipedia.org/wiki/Temple_Jewellery_of_Nagercoil', 'Temple Jewellery of Nagercoil (Wikipedia)', 'the GI-registered craft']],
  add=[('Nagercoil', CEN, 'Kanyakumari town, main centre of temple jewellery', 'Nagercoil', 0), ('Temple_Jewellery_of_Nagercoil', SUB, 'bell-shaped earring', 'Temple_Jewellery_of_Nagercoil', 0), ('Vanki', SUB, 'V-shaped armlet', 'Temple_Jewellery_of_Nagercoil', 0)])
K['G3-23'] = dict(cats=[vam('thewa')],
  add=[('Pratapgarh', CEN, 'Rajasthan town, home of thewa', 'Pratapgarh,_Rajasthan', 0), ('Raj Soni family', MAK, 'hereditary Pratapgarh thewa makers since the 18th c.', 'Thewa', 1)])
K['G3-24'] = dict(cats=[vam('Cuttack filigree')], add=[('Cuttack', CEN, 'Odisha city of silver filigree', 'Cuttack', 0), ('Durga Puja mekhas', SUB, 'filigree backdrops for Durga Puja images', 'Tarakasi', 0)])
K['G3-25'] = dict(cats=[si('Hopi silver'), ['https://musnaz.org/', 'Museum of Northern Arizona', 'Hopi overlay and silver']],
  add=[('Hopi Silvercraft Cooperative Guild', CEN, 'guild founded 1949 at Second Mesa for GI-trained smiths', 'Hopi', 0),
       ('Paul Saufkie', MAK, 'Hopi silversmith who taught overlay to the Guild, 1898–1993', 'Hopi', 1),
       ('Charles Loloma', MAK, 'Hopi jeweller of inlaid gold and stones, 1921–91', 'Charles_Loloma', 1)])
K['G3-26'] = dict(cats=[si('Taxco silver'), met('Spratling')],
  add=[('William Spratling', MAK, 'American designer who revived Taxco silver from 1931, 1900–67', 'William_Spratling', 1),
       ('Los Castillo', CEN, 'Taxco workshop of the Castillo brothers (1939)', 'William_Spratling', 0),
       ('Antonio Pineda', MAK, 'Taxco modernist silversmith, 1919–2009', 'William_Spratling', 1)])
K['G3-27'] = dict(cats=[['https://colbase.nich.go.jp/', 'ColBase (National Institutes for Cultural Heritage, Japan)', 'hair ornaments in the national museums'], met('kanzashi'), vam('kanzashi')],
  add=[('Tsumami kanzashi', SUB, 'ornaments of folded silk squares', 'Kanzashi', 0), ('Kushi', SUB, 'ornamental comb', 'Kanzashi', 0), ('Kōgai', SUB, 'bar-shaped hair stick', 'Kanzashi', 0)])

# glosses and placements for existing evidence/met rows: name -> (group, gloss[, newname])
OV = {
 'G1-6': {'Deccani: Bidar': (CEN, 'Deccan city that gives bidri its name, from the 14th–15th c.', 'Bidar'), 'Loodoo Lall': (MAK, 'named bidri maker of Bidar')},
 'G1-9': {'Varshosazi': ('DROP', 'a different Iranian craft (nickel-silver work), not turquoise inlay')},
 'G1-12': {'Sarmatian': (SCH, 'animal style of the Sarmatian steppe peoples, 3rd c. BC–4th c. AD'), 'Xiongnu': (SCH, 'animal style of the Xiongnu confederation, 3rd c. BC–1st c. AD')},
 'G1-14': {'Maung Yin Maung': (MAK, 'named Burmese silversmith in museum records')},
 'G1-16': {'Ordos region': (CEN, 'Ordos plateau in the bend of the Yellow River, Inner Mongolia', 'Ordos')},
 'G1-20': {'Kwaku Benpoh': ('MOVE', None)},
 'G1-25': {'Praenestine': (SUB, 'engraved bronze cistae (toilet caskets) of Praeneste, 4th–3rd c. BC', 'Praenestine cistae'), 'Faliscan': (CEN, 'Faliscan centres north of Rome sharing the Etruscan mirror tradition')},
 'G1-31': {'Gaucho silverwork (plateria criolla)': (SUB, 'silver mate gear, belts and horse gear of the Río de la Plata, 18th–20th c.')},
 'G1-33': {'Frankish': (SCH, 'Merovingian Frankish garnet cloisonné and brooches, 5th–8th c.'), 'Langobardic': (SCH, 'Lombard metalwork of Italy, 568–774', 'Lombard'),
           'Visigothic': (SCH, 'Visigothic eagle fibulae and votive crowns of Spain, 5th–8th c.'), 'East Germanic': (SCH, 'Gothic and Gepid polychrome jewellery of the Danube and Black Sea'),
           'Ostrogothic and nomadic (East Germanic or nomadic)': (SCH, 'Ostrogothic jewellery of Italy and its nomadic sources, c. 500', 'Ostrogothic'),
           'East Germanic or nomadic': ('DROP', 'duplicate culture label of East Germanic'), 'East German, Byzantine': ('DROP', 'duplicate culture label of East Germanic'),
           'Langobardic, Roman': ('DROP', 'duplicate culture label of Lombard'), 'Western European, Langobardic': ('DROP', 'duplicate culture label of Lombard')},
 'G1-35': {'Oseberg style': (SCH, 'gripping-beast style of the early 9th c. (Style E), after the Oseberg burial'), 'Borre style': (SCH, 'ring-chain and gripping-beast style, c. 850–950'),
           'Jelling style': (SCH, 'ribbon-bodied S-shaped animals, c. 900–975'), 'Mammen style': (SCH, 'foliate-tailed animals of the Mammen axe, c. 950–1000'),
           'Ringerike style': (SCH, 'tendril and lion style, c. 990–1050'), 'Urnes style': (SCH, 'final slender interlaced animal style, c. 1050–1150')},
 'G1-36': {'British, Bilston': ('DROP', 'duplicate of Bilston'), 'British, Birmingham': (CEN, 'Birmingham toy-trade enamellers', 'Birmingham'),
           'Wednesbury': (CEN, 'South Staffordshire enamelling town'), 'Battersea': (CEN, 'York House enamel works, Battersea, 1753–56'),
           'Bilston': (CEN, 'South Staffordshire town, main centre of painted enamel boxes')},
 'G1-37': {'Chinese with French mounts': ('DROP', 'duplicate of Mounted porcelain'), 'British, London mounts and Chinese porcelain': ('DROP', 'duplicate of Mounted porcelain'),
           'Mounted porcelain': (SUB, 'Chinese and Japanese porcelain set in French and English gilt-bronze mounts')},
 'G1-38': {'Caucasian, Northern Dagestan': (SUB, 'silver-mounted Kubachi daggers (kinjal) and arms', 'Kubachi daggers (kinjal)')},
 'G1-40': {'Rostov finift': ('DROP', 'duplicate of the leaf itself')},
 'G1-43': {'Champlevé (Œuvre de Limoges)': (SUB, 'gilt copper with enamel in cut fields, c. 1150–1350, reliquaries and croziers'),
           'Painted enamel and grisaille': (SUB, 'enamel painted on copper, from c. 1470; grisaille from c. 1530'),
           'Léonard Limosin': (MAK, 'Limoges enameller and court painter to François I, c. 1505–75'), 'Pierre Reymond': (MAK, 'Limoges grisaille enameller, c. 1513–84'),
           'Martial Courteys': (MAK, 'Limoges enameller of the Courteys family, fl. 1580s'), 'Pierre Courteys': (MAK, 'Limoges enameller, c. 1520–86'),
           'Nicholas of Verdun': ('MOVEIN', 'G1-49')},
 'G1-44': {'Johann Andreas Thelot': (MAK, 'Augsburg goldsmith and chaser, 1655–1734'), 'Johann Martin Satzger I': (MAK, 'Augsburg goldsmith, 18th c.'), 'Johann Erhard Heuglin II': (MAK, 'Augsburg goldsmith, 1687–1757')},
 'G1-45': {'Huguenot silver': (SCH, 'silver of French Protestant refugee goldsmiths in London, c. 1685–1760'),
           'Paul de Lamerie': (MAK, 'Huguenot silversmith in London, 1688–1751'), 'Simon Pantin I': (MAK, 'Huguenot silversmith in London, d. 1728'),
           'Pierre Harache': (MAK, 'Huguenot silversmith, first refugee admitted to the Goldsmiths, 1682'), 'David Willaume': (MAK, 'Huguenot silversmith in London, 1658–1741'),
           'Pierre Platel': (MAK, 'Huguenot silversmith, master of de Lamerie, d. 1719'), 'Henry Chawner': (MAK, 'London silversmith, 1764–1851'),
           'Joseph Angell II': (MAK, 'London silversmith, 19th c.'), 'Robert Hennell I': (MAK, 'London silversmith, 1741–1811'), 'Thomas Heming': (MAK, 'royal goldsmith to George III, 1722–1801'),
           'Old Sheffield Plate': (SUB, None)},
 'G1-46': {"Pala d'Oro": ('Named works', 'gold altarpiece with Byzantine enamels, 10th–14th c.; St Mark’s Basilica, Venice'),
           'Senkschmelz': (SUB, 'sunk enamel: figures in a recess on a plain gold ground'), 'Vollschmelz': (SUB, 'full enamel covering the whole plaque')},
 'G1-47': {'Qing imperial enamel workshops': (CEN, 'enamel workshops of the Imperial Household Department (Zaobanchu), Forbidden City'), 'Beijing Enamel Factory': (CEN, 'Beijing state cloisonné factory, 1950s–present')},
 'G1-48': {'Owari cloisonné (Shippō village)': (CEN, 'Shippō village near Nagoya, home of Kaji Tsunekichi’s revival'),
           'Musen (wireless) cloisonné': (SUB, 'cloisonné with wires removed after firing, Tokyo (Namikawa Sōsuke)'),
           'Namikawa Yasuyuki': (MAK, 'Kyoto cloisonné master, 1845–1927'), 'Namikawa Sōsuke': (MAK, 'Tokyo musen cloisonné master, 1847–1910')},
 'G1-63': {'Sakai uchihamono': (CEN, None)},
 'G2-2': {'Javanese': (SUB, 'kris of the Javanese courts (Surakarta, Yogyakarta)', 'Javanese kris'), 'Balinese': (SUB, 'Balinese kris with figural hilts', 'Balinese kris'),
          'Madurese': (SUB, 'kris of Madura', 'Madurese kris'), 'Bugis (South Sulawesi)': (SUB, 'Bugis and Makassar kris of South Sulawesi', 'Bugis kris'),
          'Sumbawa': (SUB, 'kris of Sumbawa with gold-sheathed hilts', 'Sumbawa kris'), 'Sumatran': (SUB, 'Sumatran kris (Minangkabau, Aceh, Palembang)', 'Sumatran kris'),
          'Malay Peninsula': (SUB, 'Malay kris of the Peninsula (Johor, Kelantan, Patani)', 'Malay kris'), 'Moro kalis': (SUB, 'long kalis of the Moro of Mindanao and Sulu')},
 'G2-3': {x: (SCH, None) for x in ['Yamato tradition', 'Yamashiro tradition', 'Bizen tradition', 'Sōshū tradition', 'Mino tradition']},
 'G2-4': {'Mokume-gane': (SUB, 'layered mixed-metal laminate devised for sword fittings, 17th c.'), 'Higo school': (SCH, 'iron-guard schools of Kumamoto (Hayashi, Kasuga, Nishigaki)')},
 'G3-4': {'Khit er rouh': (SUB, 'Moroccan headdress chain of silver plaques'), 'Kabyle jewelery': (SUB, 'cloisonné-enamelled silver of Kabylia (Beni Yenni)', 'Kabyle enamelled silver'),
          'Tuareg': (SUB, 'cast and engraved Tuareg silver: crosses, rings and amulets', 'Tuareg silver')},
 'G3-5': {'Central Javanese': (SCH, 'gold of the Central Javanese period, 8th–10th c.'), 'East Javanese': (SCH, 'gold of the East Javanese period, 10th–15th c. (Kediri, Majapahit)')},
 'G3-8': {'La Aguja style': (SCH, 'Tairona goldwork style named in museum records'), 'Bellavista style': (SCH, 'Tairona goldwork style named in museum records')},
 'G3-9': {'possibly Quimbaya (archaeological culture) (attributed)': ('DROP', 'ceramics label row, not goldwork'), 'Early Quimbaya': (SCH, 'Early Quimbaya (Classic) goldwork, c. 500 BC–AD 600'), 'Late Quimbaya': (SCH, 'Late Quimbaya goldwork, AD 600–1600')},
 'G3-10': {'Calima, Yotoco': (SCH, 'Yotoco period, c. 200 BC–AD 1300, the height of Calima goldwork', 'Yotoco'), 'Calima, Ilama': (SCH, 'Ilama period, c. 1500 BC–AD 100', 'Ilama'), 'Malagana': (SCH, 'Malagana culture of the Cauca valley, c. 200 BC–AD 200')},
 'G3-12': {'Chiriqui': (SCH, 'Chiriquí style of western Panama', 'Chiriquí'), 'Cocle': ('ALIAS', None), 'Panama: Veraguas': (SCH, 'Veraguas style of central Panama', 'Veraguas'),
           'Coclé, Macaracas': (SCH, 'Macaracas phase of Gran Coclé, c. 700–900', 'Macaracas style'), 'Diquís': (SCH, 'Diquís style of southern Costa Rica'),
           'Coclé, Parita': (SCH, 'Parita phase of Gran Coclé, c. 1100–1520', 'Parita style'), 'Initial style (Chiriquí)': (SCH, 'Initial Group of early Isthmian gold, c. 300–700')},
 'G3-13': {'Ñudzavui': ('ALIAS', None)},
 'G3-15': {'Kenneth Begay': (MAK, 'Navajo modernist silversmith, 1913–77')},
 'G3-17': {'Santo Domingo (Kewa)': (CEN, 'Kewa Pueblo, New Mexico, the main heishi centre')},
 'G3-18': {'German silver': (SUB, 'nickel-silver ornaments of the Prairies and Great Lakes, later 19th c.')},
 'G3-20': {'Imperial Easter eggs': (SUB, 'the 50 eggs made for Alexander III and Nicholas II, 1885–1916'), 'Fabergé egg': ('DROP', 'duplicate of Imperial Easter eggs')},
 'G3-21': {'Mourning jewellery': (SUB, None)},
}
