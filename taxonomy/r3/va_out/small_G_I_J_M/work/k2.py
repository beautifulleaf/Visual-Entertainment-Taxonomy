# knowledge for I1 woodwork, I2 lacquer, I3 furniture styles, I4 instruments
from kutil import met, vam, bm, si, ch, moma, wpl, U
K = {}
SUB, SCH, CEN, MAK = 'Sub-types', 'Schools & phases', 'Centres & workshops', 'Makers'
ISL = ['https://islamicart.museumwnf.org/', 'Discover Islamic Art (Museum With No Frontiers)', 'virtual museum of Islamic art objects from over 100 collections']
GOS = ['https://goskatalog.ru/portal/', 'Goskatalog (State Catalogue of the Museum Fund of Russia)', 'objects in Russian state museums']
ICH = ['https://ich.unesco.org/en/lists', 'UNESCO Intangible Cultural Heritage Lists', 'inscribed elements']
KOG = ['https://kougeihin.jp/en/', 'Japan Traditional Crafts (kougeihin.jp)', 'the designated traditional crafts of Japan']
COLB = ['https://colbase.nich.go.jp/', 'ColBase (National Institutes for Cultural Heritage, Japan)', 'objects in Japan’s four national museums']
EMK = ['https://www.emuseum.go.kr/', 'e-Museum (National Museums of Korea)', 'collections of Korea’s national museums']
MIMO = ['https://mimo-international.com/MIMO/', 'MIMO – Musical Instrument Museums Online', 'over 60,000 instruments in European and world collections']
MIMED = ['https://collections.ed.ac.uk/mimed', 'University of Edinburgh Musical Instrument collection (MIMEd)', 'historic instruments in Edinburgh']
HORN = ['https://www.horniman.ac.uk/collections/', 'Horniman Museum collections', 'over 9,000 musical instruments']

K['I1-1'] = dict(cats=[ISL, vam('mashrabiya'), ['https://www.archnet.org/', 'Archnet', 'Islamic architecture and its sites']],
  add=[('Shanashil', SUB, 'projecting latticed bay windows of Baghdad and Basra', 'Shanashil', 0), ('Rawshan', SUB, 'wooden window-bays of the Hijaz (Jeddah)', 'Mashrabiya', 0),
       ('Bayt al-Suhaymi', 'Named buildings', 'Ottoman-era house in Cairo with surviving mashrabiyas, 1648–1796', 'Bayt_al-Suhaymi', 0), ('Cairo', CEN, 'the classic centre of turned-spindle mashrabiya', 'Cairo', 0)])
K['I1-2'] = dict(cats=[vam('khatam'), met('khatam'), ISL],
  add=[('Shiraz', CEN, 'centre of khatam-kari', 'Shiraz', 0), ('Isfahan', CEN, 'centre of khatam workshops', 'Isfahan', 0), ('Khatam doors and panels', SUB, 'architectural khatam of shrines and palaces', 'Khatam', 0)])
K['I1-3'] = dict(cats=[vam('Ottoman mother-of-pearl'), ['https://www.topkapisarayi.gov.tr/en', 'Topkapı Palace Museum', 'Ottoman court furniture and thrones'], ISL],
  add=[('Throne of Sultan Ahmed I (Sedefkâr Mehmed Ağa, c. 1610)', 'Named works', 'walnut throne inlaid with mother-of-pearl and tortoiseshell; Topkapı Palace Museum, Istanbul', 'Sedefkâr_Mehmed_Ağa', 0),
       ('Sedefkâr Mehmed Ağa', MAK, 'Ottoman inlayer and architect of the Blue Mosque, c. 1540–1617', 'Sedefkâr_Mehmed_Ağa', 1)])
K['I1-4'] = dict(cats=[bm('olive wood Bethlehem'), vam('Bethlehem')],
  add=[('Bethlehem', CEN, 'town of olive-wood and mother-of-pearl workshops for pilgrims', 'Bethlehem', 0), ('Models of the Church of the Holy Sepulchre', SUB, 'olive-wood and mother-of-pearl models made for pilgrims, 17th–19th c.', 'Church_of_the_Holy_Sepulchre', 0),
       ('Nativity sets', SUB, 'carved crèche figures, the staple of the modern trade', 'Bethlehem', 0)])
K['I1-5'] = dict(cats=[vam('Islamic woodwork'), met('carved wood Islamic'), ISL],
  add=[('Minbar of Nur al-Din (Aleppo, 1168)', 'Minbars', 'minbar made in Aleppo for al-Aqsa Mosque, Jerusalem; burnt 1969', 'Minbar_of_Saladin', 0),
       ('Minbar of the Kutubiyya Mosque (Córdoba, 1137)', 'Minbars', 'marquetry minbar made in Córdoba for Marrakesh; Badi Palace, Marrakesh', 'Kutubiyya_Mosque', 0),
       ('Minbar of the Great Mosque of Kairouan (9th c.)', 'Minbars', 'oldest minbar in place, teak carved panels; Great Mosque of Kairouan', 'Great_Mosque_of_Kairouan', 0)])
K['I1-6'] = dict(cats=[met('Damascus Room'), ['https://www.smb.museum/en/museums-institutions/museum-fuer-islamische-kunst/home/', 'Museum für Islamische Kunst, Berlin', 'holds the Aleppo Room']],
  add=[('Aleppo Room (1600–03)', 'Named rooms', 'painted panelling of a Christian merchant’s house in Aleppo; Museum für Islamische Kunst, Berlin', 'Aleppo_Room', 0),
       ('Damascus Room (1707)', 'Named rooms', 'painted reception room of a Damascus house; Metropolitan Museum of Art, New York', 'Damascus_Room', 0)])
K['I1-7'] = dict(cats=[vam('Kondapalli')], add=[('Kondapalli', CEN, 'village near Vijayawada, Andhra Pradesh', 'Kondapalli', 0), ('Dasavatara sets', SUB, 'sets of the ten avatars of Vishnu', 'Kondapalli_Toys', 0), ('Ambari elephant', SUB, 'elephant with howdah', 'Kondapalli_Toys', 0)])
K['I1-8'] = dict(cats=[['https://collectie.wereldculturen.nl/', 'Wereldmuseum collection (NMVW)', 'Nirmal playing cards and toys'], vam('Nirmal')],
  add=[('Nirmal', CEN, 'town in Telangana of the Naqqash painters', 'Nirmal', 0), ('Ganjifa playing cards', SUB, 'painted Dasavatara ganjifa cards', 'Ganjifa', 0), ('Naqqash families', CEN, 'hereditary painter families of Nirmal', 'Nirmal', 0)])
K['I1-9'] = dict(cats=[vam('Malay wood'), bm('Malay woodcarving')], add=[('Kelantan', CEN, 'east-coast state of woodcarvers', 'Kelantan', 0), ('Terengganu', CEN, 'east-coast state of carvers and boatbuilders', 'Terengganu', 0), ('Awan larat', SUB, 'continuous scrolling cloud-vine motif', 'Kelantan', 0)])
K['I1-10'] = dict(cats=[KOG], add=[('Hakone', CEN, 'mountain resort of yosegi workshops', 'Hakone,_Kanagawa', 0), ('Himitsu-bako', SUB, 'secret puzzle box', 'Japanese_puzzle_box', 0)])
K['I1-11'] = dict(cats=[['https://ainu-upopoy.jp/en/', 'Upopoy National Ainu Museum', 'Ainu collections'], bm('Ainu')],
  add=[('Ikupasuy', SUB, 'carved prayer stick for libations', 'Ikupasuy', 0), ('Makiri', SUB, 'knife with carved hilt and sheath', 'Ainu_people', 0), ('Nibutani', CEN, 'Biratori village of the Nibutani-bori carvers', 'Biratori,_Hokkaido', 0)])
K['I1-12'] = dict(cats=[EMK], add=[('Hwagak boxes', SUB, 'women’s boxes and sewing kits faced with painted horn', 'Korean_art', 0)])
K['I1-13'] = dict(cats=[['https://collections.si.edu/search/results.htm?q=mate+burilado', 'Smithsonian collections search: mate burilado', 'Peruvian carved gourds']],
  add=[('Cochas Chico', CEN, 'Junín village of gourd carvers', 'Huancayo', 0), ('Cochas Grande', CEN, 'Junín village of gourd carvers', 'Huancayo', 0), ('Huanta', CEN, 'Ayacucho centre of narrative gourds', 'Huanta', 0)])
K['I1-14'] = dict(cats=[si('bentwood box'), ['https://moa.ubc.ca/', 'Museum of Anthropology at UBC', 'Northwest Coast collections'], bm('bentwood box')],
  add=[('Bentwood box', SUB, 'box made from a single kerfed cedar plank', 'Bentwood_box', 0),
       ('Charles Edenshaw', MAK, 'Haida carver and painter, c. 1839–1920', 'Charles_Edenshaw', 1), ('Willie Seaweed', MAK, 'Kwakwaka’wakw carver, c. 1873–1967', 'Willie_Seaweed', 1),
       ('Mungo Martin', MAK, 'Kwakwaka’wakw carver, 1879–1962', 'Mungo_Martin', 1), ('Bill Reid', MAK, 'Haida artist, 1920–98', 'Bill_Reid', 1)])
K['I1-15'] = dict(cats=[['https://collections.tepapa.govt.nz/', 'Te Papa collections online', 'Fijian clubs'], bm('Fiji club'), ['https://www.penn.museum/collections/', 'Penn Museum collections', 'Oceanian arms']],
  add=[('Totokia', SUB, 'beaked pineapple-headed club', 'War_club', 0), ('I ula (throwing club)', SUB, 'short club thrown in battle', 'War_club', 0), ('Culacula', SUB, 'paddle-shaped club', 'War_club', 0)])
K['I1-16'] = dict(cats=[met('tramp art')], add=[('Tramp art boxes', SUB, 'notch-carved layered cigar-box boxes', 'Tramp_art', 0), ('Tramp art frames', SUB, 'crown-of-thorns and layered picture frames', 'Tramp_art', 0)])
K['I1-17'] = dict(cats=[GOS], add=[('Abramtsevo carpentry workshop (1876)', CEN, 'workshop founded by Elizaveta Mamontova at the Abramtsevo estate', 'Abramtsevo_Colony', 0),
       ('Elena Polenova', MAK, 'designer of the Abramtsevo carpentry workshop, 1850–98', 'Elena_Polenova', 1)])
K['I1-18'] = dict(cats=[GOS], add=[('Untsukul', CEN, 'Avar village in Dagestan', 'Dagestan', 0), ('Walking sticks and boxes', SUB, 'silver-inlaid cornel-wood canes and caskets', 'Dagestan', 0)])
K['I1-19'] = dict(cats=[GOS], add=[('Yavoriv', CEN, 'Kosiv-area village of the Shkriblyak carvers', 'Hutsuls', 0), ('Shkriblyak family', MAK, 'Hutsul carvers from Yuriy Shkriblyak (1822–84)', 'Hutsuls', 1), ('Kosiv', CEN, 'Hutsul craft town', 'Kosiv', 0)])
K['I1-20'] = dict(cats=[ICH])
K['I1-21'] = dict(cats=[ICH], add=[('Konjic', CEN, 'town on the Neretva, Bosnia and Herzegovina', 'Konjic', 0)])
K['I1-22'] = dict(cats=[['https://www.finna.fi/', 'Finna (Finnish museums)', 'kuksa cups in Finnish museums']], add=[('Guksi', SUB, 'Sámi cup of birch burl', 'Kuksa', 0), ('Kåsa', SUB, 'Swedish carved cup', 'Kuksa', 0)])
K['I1-23'] = dict(cats=[['https://wallacelive.wallacecollection.org/', 'Wallace Collection online', 'the largest collection of Boulle furniture'], met('Boulle'), ['https://collections.louvre.fr/en/', 'Louvre collections', 'Boulle furniture']],
  add=[('Première-partie', SUB, 'tortoiseshell ground with brass pattern', 'André-Charles_Boulle', 0), ('Contre-partie', SUB, 'brass ground with tortoiseshell pattern', 'André-Charles_Boulle', 0),
       ('Étienne Levasseur', MAK, 'revived Boulle work in the 1760s, 1721–98', 'André-Charles_Boulle', 1), ('George Bullock', MAK, 'English Regency maker of buhl furniture, 1777–1818', 'André-Charles_Boulle', 1)])
K['I1-24'] = dict(cats=[vam('thuya')], add=[('Essaouira', CEN, 'Atlantic port whose woodworkers’ souk makes thuya marquetry', 'Essaouira', 0)])
K['I1-25'] = dict(cats=[vam('Kashmir walnut')], add=[('Srinagar', CEN, 'centre of walnut carving', 'Srinagar', 0), ('Khatamband', SUB, 'geometric wooden ceilings of Kashmir', 'Khatamband', 0)])
K['I1-26'] = dict(cats=[vam('Jepara')], add=[('Mantingan Mosque panels (16th c.)', 'Named works', 'carved stone and wood panels at the Mantingan Mosque, Jepara', 'Mantingan_Mosque', 0), ('Kartini', CEN, 'Jepara-born reformer who promoted its carvers, 1879–1904', 'Kartini', 0)])
K['I1-27'] = dict(cats=[KOG], add=[('Ōdate', CEN, 'Akita city of magewappa', 'Ōdate', 0)])
K['I1-28'] = dict(cats=[KOG], add=[('Tendō', CEN, 'Yamagata city producing most shogi pieces', 'Tendō,_Yamagata', 0), ('Kakikoma', SUB, 'pieces with written characters', 'Shogi', 0), ('Moriagekoma', SUB, 'pieces with raised-lacquer characters', 'Shogi', 0)])
K['I1-29'] = dict(cats=[['https://www.vam.ac.uk/', 'V&A', ''], ['https://www.gypsy-caravan.co.uk/', 'Romany wagons archive', '']])
K['I1-29'] = dict(cats=[vam('Romany wagon'), ['https://www.reading.ac.uk/merl', 'Museum of English Rural Life', 'holds Romani wagons']],
  add=[('Reading wagon', SUB, 'straight-sided wagon with large rear wheels, after Dunton of Reading', 'Vardo_(Romani_wagon)', 0), ('Ledge wagon', SUB, 'wagon with ledges over the wheels', 'Vardo_(Romani_wagon)', 0),
       ('Bow-top wagon', SUB, 'canvas-covered barrel-top wagon', 'Vardo_(Romani_wagon)', 0), ('Burton wagon', SUB, 'showman’s wagon with small wheels under the body', 'Vardo_(Romani_wagon)', 0),
       ('Dunton & Sons, Reading', CEN, 'Berkshire wagon builders of the Reading type', 'Vardo_(Romani_wagon)', 0)])
K['I1-30'] = dict(cats=[['https://pipedia.org/', 'Pipedia', 'encyclopedia of pipe makers and brands']],
  add=[('Sixten Ivarsson', MAK, 'Copenhagen pipe maker, father of the freehand, 1909–2001', 'https://pipedia.org/wiki/Jess_Chonowitsch', 1),
       ('Jess Chonowitsch', MAK, 'Danish freehand pipe maker, pupil of Ivarsson, b. 1946', 'https://pipedia.org/wiki/Jess_Chonowitsch', 1),
       ('Lars Ivarsson', MAK, 'Danish pipe maker, son of Sixten, b. 1944', 'https://pipedia.org/wiki/Jess_Chonowitsch', 1)])
K['I2-1'] = dict(cats=[vam('Persian lacquer'), ['https://www.khalilicollections.org/', 'Khalili Collections', 'the largest group of Persian lacquer'], ISL],
  add=[('Qalamdan (pen box)', SUB, 'painted papier-mâché pen box', 'Qalamdan', 0), ('Mirror cases and bookbindings', SUB, 'painted lacquer covers and cases', 'Qalamdan', 0),
       ('Safavid lacquer', SCH, 'Isfahan bindings and pen boxes, 16th–17th c.', 'Safavid_art', 0), ('Zand lacquer', SCH, 'Shiraz court lacquer of the 18th c.', 'Zand_dynasty', 0), ('Qajar lacquer', SCH, 'Tehran and Isfahan lacquer of the 19th c.', 'Qajar_art', 0),
       ('Najaf ʿAli', MAK, 'Qajar lacquer painter and founder of a family atelier, fl. 1815–70s', 'Qajar_art', 1)])
K['I2-2'] = dict(cats=[vam('Kashmir papier-mâché')], add=[('Srinagar', CEN, 'centre of Kashmiri papier-mâché', 'Srinagar', 0), ('Pen boxes (qalamdan)', SUB, 'the original kar-e-kalamdani product', 'Qalamdan', 0)])
K['I2-3'] = dict(cats=[vam('Ottoman lacquer'), ISL], add=[('Edirne', CEN, 'Thracian city that gave its name to the style', 'Edirne', 0), ('Writing boxes and bookbindings', SUB, 'the chief Edirnekâri objects', 'Ottoman_art', 0)])
K['I2-4'] = dict(cats=[vam('Channapatna')], add=[('Channapatna', CEN, 'Karnataka town of lac-turned toys', 'Channapatna', 0), ('Wright tree (Wrightia tinctoria) wood', SUB, 'the traditional ivory-wood of the toys', 'Channapatna_toys', 0)])
K['I2-5'] = dict(cats=[vam('Etikoppaka')], add=[('Etikoppaka', CEN, 'village on the Varaha river, Andhra Pradesh', 'Etikoppaka', 0)])
K['I2-6'] = dict(cats=[vam('Burmese lacquer'), bm('Burmese lacquer'), met('Burmese lacquer')],
  add=[('Yun', SUB, 'engraved, coloured-in lacquer of Bagan', 'Burmese_lacquerware', 0), ('Shwei-zawa', SUB, 'gold-leaf lacquer', 'Burmese_lacquerware', 0), ('Hmansi-shwei-cha', SUB, 'relief lacquer set with glass mosaic', 'Burmese_lacquerware', 0),
       ('Kyaukka', CEN, 'Monywa village of plain black utilitarian lacquer', 'Burmese_lacquerware', 0)])
K['I2-7'] = dict(cats=[['https://www.nationalmuseumbangkok.com/', 'Bangkok National Museum', 'Thai lacquer cabinets'], bm('Thai lacquer')],
  add=[('Manuscript cabinets (tu phra tham)', SUB, 'gold-and-black lacquer cabinets for scriptures', 'Thai_art', 0), ('Lacquer Pavilion, Suan Pakkad Palace', 'Named works', 'Ayutthaya-period pavilion with gold-and-black panels; Suan Pakkad Palace, Bangkok', 'Suan_Pakkad_Palace', 0)])
K['I2-8'] = dict(cats=[['https://digitalarchive.npm.gov.tw/', 'National Palace Museum Open Data, Taipei', 'imperial carved lacquer'], met('carved lacquer'), vam('carved lacquer')],
  add=[('Tihong (cinnabar lacquer)', SUB, 'red carved lacquer', 'Carved_lacquer', 0), ('Tixi (guri)', SUB, 'layered lacquer carved in pommel scrolls', 'Carved_lacquer', 0),
       ('Guoyuanchang (Orchard Workshop)', CEN, 'Yongle imperial lacquer workshop, Beijing', 'Carved_lacquer', 0), ('Yongle carved lacquer', SCH, 'thick cinnabar lacquer of 1403–24', 'Carved_lacquer', 0),
       ('Zhang Cheng', MAK, 'Yuan carved-lacquer master of Xitang, Jiaxing', 'Carved_lacquer', 1), ('Yang Mao', MAK, 'Yuan carved-lacquer master of Xitang, Jiaxing', 'Carved_lacquer', 1)])
K['I2-9'] = dict(cats=[COLB, ['https://bunka.nii.ac.jp/', 'Cultural Heritage Online (bunka.nii.ac.jp)', 'designated maki-e works'], met('maki-e')],
  add=[('Hiramaki-e', SUB, 'flat sprinkled-picture lacquer', 'Maki-e', 0), ('Takamaki-e', SUB, 'raised maki-e', 'Maki-e', 0), ('Togidashi maki-e', SUB, 'polished-out maki-e flush with the ground', 'Maki-e', 0),
       ('Kōdaiji maki-e', SCH, 'Momoyama hiramaki-e of the Kōdai-ji mausoleum', 'Kōdai-ji', 0), ('Kōami school', SCH, 'hereditary shogunal lacquerers from Kōami Michinaga (1410–78)', 'Maki-e', 0),
       ("Hon'ami Kōetsu", MAK, 'Rinpa founder and designer of writing boxes, 1558–1637', "Hon'ami_Kōetsu", 1), ('Ogata Kōrin', MAK, 'Rinpa painter and lacquer designer, 1658–1716', 'Ogata_Kōrin', 1),
       ('Shibata Zeshin', MAK, 'Edo–Meiji lacquerer and painter, 1807–91', 'Shibata_Zeshin', 1),
       ('Funabashi writing box (Hon’ami Kōetsu)', 'Named works', 'maki-e and lead writing box, 17th c.; National Treasure; Tokyo National Museum', "Hon'ami_Kōetsu", 0),
       ('Yatsuhashi writing box (Ogata Kōrin)', 'Named works', 'maki-e writing box with irises, 18th c.; National Treasure; Tokyo National Museum', 'Ogata_Kōrin', 0)])
K['I2-10'] = dict(cats=[COLB, KOG, met('Japanese lacquer')],
  add=[('Negoro ware', CEN, 'red-over-black lacquer of Negoro-ji, Wakayama', 'Negoro_ware', 0), ('Kiso lacquerware', CEN, 'Nagano centre of lacquer', 'Kiso_Valley', 0), ('Yamanaka lacquerware', CEN, 'Ishikawa turned-wood lacquer', 'Kaga,_Ishikawa', 0)])
K['I2-11'] = dict(cats=[['https://www.city.urasoe.lg.jp/', 'Urasoe Art Museum', 'Ryukyuan lacquer collection'], COLB],
  add=[('Tsuikin', SUB, 'applied lacquer relief', 'Ryukyu_Kingdom', 0), ('Chinkin', SUB, 'gold-leaf in incised lines', 'Ryukyu_Kingdom', 0), ('Raden', SUB, 'mother-of-pearl inlay', 'Raden', 0), ('Shuri', CEN, 'royal capital and its lacquer office (Kaizuri bugyōsho)', 'Shuri_Castle', 0)])
K['I2-12'] = dict(cats=[EMK, met('Korean mother-of-pearl lacquer'), bm('Korean lacquer mother-of-pearl')],
  add=[('Goryeo najeon sutra boxes', SUB, 'boxes with chrysanthemum inlay, of which fewer than ten survive', 'Tongyeong', 0), ('Tongyeong', CEN, 'south-coast centre of najeon', 'Tongyeong', 0)])
K['I2-13'] = dict(cats=[met('Yi lacquer')], add=[('Xide County', CEN, 'Liangshan county of Yi lacquer (national ICH)', 'Liangshan_Yi_Autonomous_Prefecture', 0)])
K['I2-14'] = dict(cats=[met('kintsugi')], add=[('Kintsugi', SUB, 'repair with gold-dusted lacquer', 'Kintsugi', 0), ('Yobitsugi', SUB, 'repair with shards from another piece', 'Kintsugi', 0)])
K['I2-15'] = dict(cats=[met('Mexican lacquer'), ['https://www.mexicolore.co.uk/', 'Mexicolore', '']])
K['I2-15'] = dict(cats=[met('Mexican lacquer'), si('maque Mexico')], add=[('Uruapan', CEN, 'Michoacán centre of incised and inlaid maque', 'Uruapan', 0)])
K['I2-16'] = dict(cats=[ICH], add=[('Pasto', CEN, 'capital of Nariño, Colombia', 'Pasto,_Colombia', 0), ('Mopa-mopa resin', SUB, 'resin of Elaeagia pastoensis chewed and stretched into sheets', 'Pasto,_Colombia', 0)])
K['I2-17'] = dict(cats=[GOS], add=[('Semyonov', CEN, 'town of the Khokhloma Painting factory', 'Semyonov,_Nizhny_Novgorod_Oblast', 0), ('Khokhloma', CEN, 'trading village that gave its name to the craft', 'Khokhloma', 0)])
K['I2-18'] = dict(cats=[GOS], add=[('Palekh', CEN, 'Ivanovo village of icon painters, lacquer miniature from 1923', 'Palekh', 0), ('Ivan Golikov', MAK, 'founder of Palekh lacquer miniature, 1887–1937', 'Palekh_miniature', 1)])
K['I2-19'] = dict(cats=[GOS], add=[('Fedoskino', CEN, 'village near Moscow', 'Fedoskino_miniature', 0), ('Lukutin factory', CEN, 'Fedoskino papier-mâché works of the Lukutin family, 1818–1904', 'Fedoskino_miniature', 0)])
K['I2-20'] = dict(cats=[GOS], add=[('Mstyora', CEN, 'Vladimir Oblast settlement', 'Mstyora', 0)])
K['I2-21'] = dict(cats=[GOS], add=[('Kholuy', CEN, 'Ivanovo village', 'Kholuy_miniature', 0)])
K['I3-1'] = dict(cats=[EMK], add=[('Naju soban', SUB, 'Naju style with straight legs', 'Soban', 0), ('Haeju soban', SUB, 'Haeju style with pierced panel legs', 'Soban', 0), ('Tongyeong soban', SUB, 'Tongyeong style with mother-of-pearl', 'Soban', 0)])
K['I3-2'] = dict(cats=[met('Queen Anne furniture'), vam('Queen Anne furniture'), ['https://www.winterthur.org/', 'Winterthur Museum', 'American furniture']],
  add=[('Cabriole leg', SUB, 'S-curved leg ending in pad or claw-and-ball foot', 'Cabriole_leg', 0), ('High chest (highboy)', SUB, 'tall chest on a stand', 'Highboy', 0),
       ('Newport', CEN, 'Rhode Island furniture centre (Townsend-Goddard)', 'Newport,_Rhode_Island', 0), ('Philadelphia', CEN, 'colonial furniture centre', 'Philadelphia', 0), ('Boston', CEN, 'colonial furniture centre', 'Boston', 0)])
K['I3-3'] = dict(cats=[met('Chippendale'), vam('Chippendale'), ['https://www.winterthur.org/', 'Winterthur Museum', 'American Chippendale furniture']],
  add=[('Philadelphia Chippendale', SCH, 'carved high-style furniture of Philadelphia, 1760s–70s', 'Thomas_Affleck', 0), ('Newport block-front', SCH, 'block-and-shell furniture of Newport', 'Newport,_Rhode_Island', 0),
       ('Thomas Affleck', MAK, 'Philadelphia cabinetmaker, 1740–95', 'Thomas_Affleck', 1), ('John Goddard', MAK, 'Newport cabinetmaker, 1723–85', 'John_Goddard_(cabinetmaker)', 1), ('John Townsend', MAK, 'Newport cabinetmaker, 1733–1809', 'John_Townsend_(cabinetmaker)', 1)])
K['I3-4'] = dict(cats=[met('Hepplewhite'), vam('Hepplewhite')], add=[('Shield-back chair', SUB, 'chair with a shield-shaped back', 'Hepplewhite', 0), ('John and Thomas Seymour', MAK, 'Boston Federal cabinetmakers', 'Hepplewhite', 1)])
K['I3-5'] = dict(cats=[met('Sheraton'), vam('Sheraton')], add=[('Duncan Phyfe', MAK, 'New York cabinetmaker, 1770–1854', 'Duncan_Phyfe', 1), ('Federal style', SCH, 'American furniture of 1780–1830', 'Federal_architecture', 0)])
K['I3-6'] = dict(cats=[met('International Gothic'), bm('Royal Gold Cup')],
  add=[('Goldenes Rössl (1404)', 'Named works', 'gold and enamel devotional group; Altötting Treasury', 'Goldenes_Rössl', 0), ('Apocalypse Tapestry (1377–82)', 'Named works', 'woven by Nicolas Bataille’s workshop; Château d’Angers', 'Apocalypse_Tapestry', 0),
       ('Royal Gold Cup (c. 1370–80)', 'Named works', 'gold and basse-taille enamel cup; British Museum, London', 'Royal_Gold_Cup', 0), ('Holy Thorn Reliquary (c. 1390s)', 'Named works', 'gold reliquary of Jean de Berry; British Museum, London', 'Holy_Thorn_Reliquary', 0)])
K['I3-7'] = dict(cats=[met('Mannerist goldsmith'), ['https://www.khm.at/en/visit/collections/kunstkammer-vienna', 'Kunsthistorisches Museum: Kunstkammer Vienna', 'Mannerist goldsmiths’ work']],
  add=[('Benvenuto Cellini', MAK, 'Florentine goldsmith and sculptor, 1500–71', 'Benvenuto_Cellini', 1), ('Wenzel Jamnitzer', MAK, 'Nuremberg goldsmith, 1507/08–85', 'Wenzel_Jamnitzer', 1),
       ('Saliera (Cellini, 1540–43)', 'Named works', 'gold salt cellar for François I; Kunsthistorisches Museum, Vienna', 'Cellini_Salt_Cellar', 0)])
K['I3-8'] = dict(cats=[['https://collections.louvre.fr/en/', 'Louvre collections', 'Louis XIV decorative arts'], ['https://collections.chateauversailles.fr/', 'Château de Versailles collections', 'furniture and objects']],
  add=[('Gobelins Manufactory', CEN, 'royal furniture and tapestry works under Le Brun, from 1662', 'Gobelins_Manufactory', 0), ('Charles Le Brun', MAK, 'director of the Gobelins and royal designer, 1619–90', 'Charles_Le_Brun', 1),
       ('Jean Berain the Elder', MAK, 'designer of the Chambre du Roi, 1640–1711', 'Jean_Berain_the_Elder', 1)])
K['I3-9'] = dict(cats=[['https://wallacelive.wallacecollection.org/', 'Wallace Collection online', 'French Rococo furniture'], met('Louis XV')],
  add=[('Vincennes-Sèvres', CEN, 'royal porcelain manufactory, 1740/1756', 'Manufacture_nationale_de_Sèvres', 0), ('Juste-Aurèle Meissonnier', MAK, 'Rococo ornamentalist and goldsmith, 1695–1750', 'Juste-Aurèle_Meissonnier', 1),
       ('Charles Cressent', MAK, 'ébéniste and bronzier of the Régence, 1685–1768', 'Charles_Cressent', 1)])
K['I3-10'] = dict(cats=[['https://wallacelive.wallacecollection.org/', 'Wallace Collection online', 'Louis XVI furniture and Sèvres'], met('Riesener')])
K['I3-11'] = dict(cats=[['https://www.mobiliernational.culture.gouv.fr/', 'Mobilier national', 'French state furniture collection'], met('Empire style')],
  add=[('Château de Malmaison', 'Named interiors', 'Josephine’s château remodelled by Percier and Fontaine from 1800', 'Château_de_Malmaison', 0),
       ('Charles Percier', MAK, 'Napoleonic architect-designer, 1764–1838', 'Charles_Percier', 1), ('Pierre-François-Léonard Fontaine', MAK, 'Percier’s partner, 1762–1853', 'Pierre-François-Léonard_Fontaine', 1),
       ('François-Honoré-Georges Jacob-Desmalter', MAK, 'Empire cabinetmaker, 1770–1841', 'François-Honoré-Georges_Jacob-Desmalter', 1)])
K['I3-12'] = dict(cats=[['https://www.mak.at/en', 'MAK – Museum of Applied Arts, Vienna', 'Biedermeier furniture'], ['https://www.hofmobiliendepot.at/', 'Hofmobiliendepot (Möbel Museum Wien)', 'Viennese furniture']],
  add=[('Josef Danhauser', MAK, 'Viennese furniture manufacturer, 1780–1829', 'Biedermeier', 1)])
K['I3-13'] = dict(cats=[vam('Victorian'), met('Victorian')], add=[('Augustus Pugin', MAK, 'Gothic Revival designer, 1812–52', 'Augustus_Pugin', 1), ('Minton', CEN, 'Stoke-on-Trent pottery, majolica from 1849', 'Mintons', 0)])
K['I3-14'] = dict(cats=[vam('Arts and Crafts'), met('Arts and Crafts'), ['https://www.wmgallery.org.uk/', 'William Morris Gallery', 'Morris & Co. collections']],
  add=[('William Morris', MAK, 'designer and founder of Morris & Co., 1834–96', 'William_Morris', 1), ('C. R. Ashbee', MAK, 'Guild of Handicraft founder, 1863–1942', 'Charles_Robert_Ashbee', 1), ('Ernest Gimson', MAK, 'Cotswold furniture designer, 1864–1919', 'Ernest_Gimson', 1)])
K['I3-17'] = dict(cats=[['https://www.bauhaus.de/en/', 'Bauhaus-Archiv / Museum für Gestaltung, Berlin', 'the largest Bauhaus collection'], ['https://harvardartmuseums.org/collections?q=bauhaus', 'Harvard Art Museums: Bauhaus', 'Busch-Reisinger Bauhaus collection'], moma('Bauhaus')],
  add=[('Walter Gropius', MAK, 'founder and director, 1883–1969', 'Walter_Gropius', 1), ('Marcel Breuer', MAK, 'furniture workshop master, 1902–81', 'Marcel_Breuer', 1), ('Marianne Brandt', MAK, 'metal workshop designer, 1893–1983', 'Marianne_Brandt', 1),
       ('Wilhelm Wagenfeld', MAK, 'metal workshop designer, 1900–90', 'Wilhelm_Wagenfeld', 1), ('Gunta Stölzl', MAK, 'weaving workshop master, 1897–1983', 'Gunta_Stölzl', 1), ('Anni Albers', MAK, 'weaver, 1899–1994', 'Anni_Albers', 1),
       ('Wassily Chair (Breuer, 1925)', 'Named works', 'tubular-steel club chair; MoMA and Bauhaus-Archiv', 'Wassily_Chair', 0), ('Wagenfeld lamp (1924)', 'Named works', 'glass and metal table lamp', 'Wagenfeld_lamp', 0)])
K['I3-18'] = dict(cats=[['https://mingeikan.or.jp/english/', 'Japan Folk Crafts Museum (Nihon Mingeikan)', 'Yanagi’s collection, Tokyo'], vam('Hamada Shoji')],
  add=[('Yanagi Sōetsu', MAK, 'founder of the Mingei movement, 1889–1961', 'Yanagi_Sōetsu', 1), ('Bernard Leach', MAK, 'English potter of the movement, 1887–1979', 'Bernard_Leach', 1),
       ('Munakata Shikō', MAK, 'woodblock printmaker of the movement, 1903–75', 'Shikō_Munakata', 1), ('Serizawa Keisuke', MAK, 'stencil dyer, 1895–1984', 'Keisuke_Serizawa', 1)])
K['I3-21'] = dict(cats=[['https://www.imj.org.il/en/collections', 'Israel Museum collections', 'Bezalel objects']],
  add=[('Boris Schatz', MAK, 'founder of the Bezalel School, 1867–1932', 'Boris_Schatz', 1), ('Ephraim Moses Lilien', MAK, 'Art Nouveau artist and Bezalel teacher, 1874–1925', 'Ephraim_Moses_Lilien', 1), ('Ze’ev Raban', MAK, 'Bezalel designer, 1890–1970', 'Ze%27ev_Raban', 1)])
K['I3-22'] = dict(cats=[['https://www.shakermuseum.us/', 'Shaker Museum (Mount Lebanon)', 'Shaker furniture collection'], met('Shaker')],
  add=[('Shaker oval box', SUB, 'swallowtail-jointed bentwood box', 'Shaker_furniture', 0), ('Mount Lebanon Shaker Village', CEN, 'leading Shaker community and chair factory, New York', 'Mount_Lebanon_Shaker_Society', 0),
       ('Hancock Shaker Village', CEN, 'Massachusetts Shaker community', 'Hancock_Shaker_Village', 0), ('Canterbury Shaker Village', CEN, 'New Hampshire Shaker community', 'Canterbury_Shaker_Village', 0)])
K['I3-23'] = dict(cats=[['https://www.dpm.org.cn/', 'Palace Museum, Beijing', 'Ming and Qing furniture'], met('huanghuali')],
  add=[('Huanghuali', SUB, 'fragrant rosewood of Ming furniture', 'Dalbergia_odorifera', 0), ('Zitan', SUB, 'dense purple sandalwood of Qing court furniture', 'Pterocarpus_santalinus', 0), ('Suzhou', CEN, 'Jiangnan centre of Ming furniture', 'Suzhou', 0)])
K['I3-24'] = dict(cats=[KOG], add=[('Isho-dansu', SUB, 'clothing chest', 'Tansu', 0), ('Kaidan-dansu', SUB, 'step chest', 'Tansu', 0), ('Funa-dansu', SUB, 'ship’s chest', 'Tansu', 0), ('Iwayado tansu', CEN, 'Iwate designated craft centre', 'Tansu', 0), ('Sendai tansu', CEN, 'Miyagi designated craft centre', 'Tansu', 0)])
K['I3-25'] = dict(cats=[EMK], add=[('Ganghwa bandaji', SUB, 'Gyeonggi type with large cut-metal plates', 'https://koreanantiquefurniture.com/gyeonggi-do-bandaji-경기도-반닫이', 0), ('Kaesong bandaji', SUB, 'Kaesong type', 'https://koreanantiquefurniture.com/gyeonggi-do-bandaji-경기도-반닫이', 0), ('Namhansanseong bandaji', SUB, 'Gwangju type', 'https://koreanantiquefurniture.com/gyeonggi-do-bandaji-경기도-반닫이', 0)])
K['I4-1'] = dict(cats=[['https://collections.tepapa.govt.nz/', 'Te Papa collections online', 'Vanuatu slit gongs'], bm('Vanuatu slit gong'), met('slit gong Vanuatu')],
  add=[('Ambrym', CEN, 'island of the upright atingting kon', 'Ambrym', 0), ('Malakula', CEN, 'island of slit gongs and grade rituals', 'Malakula', 0)])
K['I4-2'] = dict(cats=[MIMO, met('Spanish guitar')], add=[('Antonio de Torres Jurado', MAK, 'Almería luthier, creator of the modern classical guitar, 1817–92', 'Antonio_de_Torres_Jurado', 1),
       ('Manuel Ramírez', MAK, 'Madrid luthier, 1864–1916', 'Classical_guitar', 1), ('Santos Hernández', MAK, 'Madrid luthier, 1874–1943', 'Classical_guitar', 1), ('Ramírez guitars', CEN, 'Madrid workshop founded by José Ramírez I, 1882', 'Classical_guitar', 0)])
K['I4-3'] = dict(cats=[MIMO, met('djembe')], add=[('Dunun', SUB, 'cylindrical bass drums played with the djembe', 'Dunun', 0), ('Numu (smiths)', CEN, 'Mande smith caste who carve the drums', 'Djembe', 0)])
K['I4-4'] = dict(cats=[MIMO, bm('mbira')], add=[('Mbira dzavadzimu', SUB, '22–28-key mbira of the ancestors', 'Mbira_dzavadzimu', 0), ('Nyunga nyunga', SUB, '15-key mbira of eastern Zimbabwe', 'Mbira', 0), ('Matepe', SUB, 'large mbira of the Korekore', 'Mbira', 0)])
K['I4-5'] = dict(cats=[['https://www.tarisio.com/cozio-archive/', 'Tarisio Cozio Archive', 'database of over 20,000 fine stringed instruments'], ['https://www.museodelviolino.org/en/', 'Museo del Violino, Cremona', 'Cremonese instruments'], MIMO],
  add=[('Andrea Amati', MAK, 'founder of the Cremonese school, c. 1505–77', 'Andrea_Amati', 1), ('Nicolò Amati', MAK, 'Cremona maker and teacher, 1596–1684', 'Nicolò_Amati', 1), ('Antonio Stradivari', MAK, 'Cremona luthier, 1644–1737', 'Antonio_Stradivari', 1),
       ('Giuseppe Guarneri del Gesù', MAK, 'Cremona luthier, 1698–1744', 'Guarneri', 1), ('Jacob Stainer', MAK, 'Tyrolean luthier of Absam, c. 1618–83', 'Jacob_Stainer', 1), ('Matthias Klotz', MAK, 'founder of Mittenwald violin making, 1653–1743', 'Matthias_Klotz', 1),
       ('Jean-Baptiste Vuillaume', MAK, 'Mirecourt-born Paris luthier, 1798–1875', 'Jean-Baptiste_Vuillaume', 1),
       ('Messiah Stradivarius (1716)', 'Named instruments', 'unplayed Stradivari violin; Ashmolean Museum, Oxford', 'Messiah_Stradivarius', 0), ('Il Cannone (Guarneri del Gesù, 1743)', 'Named instruments', 'Paganini’s violin; Palazzo Tursi, Genoa', 'Il_Cannone_Guarnerius', 0)])
K['I4-6'] = dict(cats=[MIMO, vam('tanpura')], add=[('Miraj', CEN, 'Maharashtra town of sitar and tanpura makers', 'Miraj', 0), ('Tanjore tambura', SUB, 'south Indian tambura with jackwood body', 'Tanpura', 0)])
K['I4-7'] = dict(cats=[MIMO, vam('veena')], add=[('Thanjavur', CEN, 'town of veena makers (GI 2013)', 'Thanjavur', 0), ('Ekantha veena', SUB, 'veena carved from a single block', 'Saraswati_veena', 0)])
K['I4-8'] = dict(cats=[['https://www.nms.ac.uk/search-our-collections/', 'National Museums Scotland collections', 'the Queen Mary and Lamont harps'], MIMO],
  add=[('Trinity College harp', 'Named instruments', 'willow wire-strung harp, 14th–15th c.; Trinity College Dublin', 'Trinity_College_harp', 0), ('Queen Mary Harp', 'Named instruments', 'clàrsach of c. 1400–1500; National Museum of Scotland, Edinburgh', 'Queen_Mary_Harp', 0),
       ('Lamont Harp', 'Named instruments', 'clàrsach of c. 1500; National Museum of Scotland, Edinburgh', 'Lamont_Harp', 0), ('John Egan', MAK, 'Dublin harp maker of the Portable Irish Harp, fl. 1797–1841', 'Celtic_harp', 1)])
K['I4-9'] = dict(cats=[MIMO], add=[('Venczel József Schunda', MAK, 'Budapest maker of the concert cimbalom, 1845–1923', 'Cimbalom', 1), ('Concert cimbalom', SUB, 'pedalled chromatic cimbalom of 1874', 'Cimbalom', 0), ('Țambal', SUB, 'Romanian and Moldovan cimbalom', 'Cimbalom', 0)])
K['I4-10'] = dict(cats=[MIMO, vam('santur')], add=[('Santoor', SUB, 'Indian (Kashmiri) adaptation of the santur', 'Santoor', 0), ('Iraqi santur', SUB, 'santur of the Iraqi maqam ensemble (chalghi)', 'Santur', 0)])
K['I4-11'] = dict(cats=[si('Appalachian dulcimer')], add=[('Homer Ledford', MAK, 'Kentucky dulcimer maker, 1927–2006', 'Homer_Ledford', 1), ('Hourglass dulcimer', SUB, 'the commonest body shape', 'Appalachian_dulcimer', 0)])
K['I4-12'] = dict(cats=[['https://www.finna.fi/', 'Finna (Finnish museums)', 'kanteles in Finnish museums'], MIMO], add=[('Five-string kantele', SUB, 'the archaic carved kantele', 'Kantele', 0), ('Concert kantele', SUB, '36–40-string kantele with levers', 'Kantele', 0)])
K['I4-13'] = dict(cats=[COLB, MIMO, met('koto')], add=[('Gakusō', SUB, 'court koto of gagaku', 'Koto_(instrument)', 0), ('Zokusō', SUB, 'popular koto of the Edo period', 'Koto_(instrument)', 0)])
K['I4-14'] = dict(cats=[MIMO, met('zheng')], add=[('Shandong school', SCH, 'northern school', 'Guzheng', 0), ('Henan school', SCH, 'northern school', 'Guzheng', 0), ('Chaozhou school', SCH, 'southern school', 'Guzheng', 0), ('Hakka school', SCH, 'southern school', 'Guzheng', 0), ('Zhejiang school', SCH, 'Wulin school', 'Guzheng', 0)])
K['I4-15'] = dict(cats=[MIMO, met('erhu')], add=[('Gaohu', SUB, 'high-pitched huqin', 'Gaohu', 0), ('Zhonghu', SUB, 'alto huqin', 'Zhonghu', 0), ('Banhu', SUB, 'coconut-shell huqin of opera', 'Banhu', 0)])
K['I4-16'] = dict(cats=[MIMO, vam('dilruba')], add=[('Taus', SUB, 'peacock-bodied bowed lute', 'Taus_(instrument)', 0), ('Dilruba', SUB, 'smaller bowed lute without the peacock', 'Dilruba', 0), ('Esraj', SUB, 'Bengali relative of the dilruba', 'Esraj', 0)])
K['I4-17'] = dict(cats=[MIMO, vam('sarangi')], add=[('Sindhi sarangi', SUB, 'folk sarangi of Sindh and Rajasthan', 'Sarangi', 0), ('Nepali sarangi', SUB, 'four-string folk fiddle of the Gandharva', 'Sarangi_(Nepali)', 0)])
K['I4-18'] = dict(cats=[['https://digitaltmuseum.no/', 'DigitaltMuseum (Norway)', 'Hardanger fiddles in Norwegian museums']], add=[('Jaastad fiddle (1651)', 'Named instruments', 'oldest known Hardanger fiddle; University Museum of Bergen', 'Hardanger_fiddle', 0), ('Helland family', MAK, 'Bø (Telemark) dynasty of fiddle makers, 18th–20th c.', 'Hardanger_fiddle', 1)])
K['I4-19'] = dict(cats=[['https://digitaltmuseum.se/', 'DigitaltMuseum (Sweden)', 'nyckelharpas in Swedish museums']], add=[('Moraharpa', SUB, 'nyckelharpa dated 1526 from Mora', 'Nyckelharpa', 0), ('Kontrabasharpa', SUB, 'older drone nyckelharpa', 'Nyckelharpa', 0), ('August Bohlin', MAK, 'designer of the chromatic nyckelharpa, 1929', 'Nyckelharpa', 1)])
K['I4-20'] = dict(cats=[['https://www.museodellafisarmonica.it/en', 'Museo Internazionale della Fisarmonica, Castelfidardo', 'accordion museum'], MIMO],
  add=[('Paolo Soprani', MAK, 'founder of Castelfidardo accordion making, 1844–1918', 'Paolo_Soprani', 1), ('Hohner', CEN, 'Trossingen harmonica and accordion maker, 1857', 'Hohner', 0), ('Heinrich Band', MAK, 'inventor of the bandoneon, 1821–60', 'Heinrich_Band', 1), ('Concertina', SUB, 'hexagonal button free-reed instrument', 'Concertina', 0)])
K['I4-21'] = dict(cats=[MIMO, MIMED], add=[('Northumbrian smallpipes', SUB, 'bellows-blown pipes of north-east England', 'Northumbrian_smallpipes', 0), ('Scottish smallpipes', SUB, 'bellows smallpipes of Scotland', 'Scottish_smallpipes', 0)])
K['I4-22'] = dict(cats=[COLB, ['https://shosoin.kunaicho.go.jp/en-US/', 'Shōsōin Treasures (Imperial Household Agency)', 'the 8th-c. imperial repository']],
  add=[('Hichiriki', SUB, 'double-reed bamboo oboe', 'Hichiriki', 0), ('Ryūteki', SUB, 'dragon flute', 'Ryūteki', 0), ('Shō', SUB, 'mouth organ of 17 pipes', 'Shō_(instrument)', 0), ('Gakubiwa', SUB, 'court lute', 'Biwa', 0),
       ('Five-stringed biwa of the Shōsōin (8th c.)', 'Named instruments', 'red-sandalwood lute inlaid with mother-of-pearl; Shōsōin, Nara', 'Shōsōin', 0)])
K['I4-23'] = dict(cats=[['https://www.musee-boite-a-musique.ch/', 'CIMA – Musée de la boîte à musique, Sainte-Croix', ''], MIMO])
K['I4-23'] = dict(cats=[MIMO, ['https://www.museumspeelklok.nl/', 'Museum Speelklok, Utrecht', 'self-playing instruments and street organs']],
  add=[('Sainte-Croix', CEN, 'Vaud town of music-box makers', 'Music_box', 0), ('Antoine Favre', MAK, 'Geneva watchmaker who invented the music box, 1796', 'Music_box', 1), ('Reuge', CEN, 'Sainte-Croix music-box maker, 1865', 'Reuge', 0), ('Polyphon', CEN, 'Leipzig maker of disc music boxes', 'Music_box', 0)])

OV = {
 'I1-1': {'El Farouk, Omar': ('Makers', 'contemporary Cairo mashrabiya designer'), 'Hassan, Abua Zaid': ('Makers', 'contemporary Cairo mashrabiya maker')},
 'I1-3': {'Damascene mother-of-pearl inlay': ('Centres & workshops', None)},
 'I1-17': {'Vasily Vornoskov': ('Makers', 'Kudrino carver, founder of the style at Abramtsevo, 1876–1940')},
 'I1-23': {'André-Charles Boulle': ('Makers', 'ébéniste du roi, perfecter of tortoiseshell-and-brass marquetry, 1642–1732'), 'Pierre Gole': ('Makers', 'Dutch-born ébéniste to Louis XIV, c. 1620–84'), 'Alexandre-Jean Oppenordt': ('Makers', 'Dutch-born ébéniste in Paris, 1639–1715')},
 'I2-6': {'Hsaya Maung Htun': ('Makers', 'named Burmese lacquer master in museum records'), 'Maung Paw Sein': ('Makers', 'named Burmese lacquer maker in museum records'), 'Hsaya Khant': ('Makers', 'named Burmese lacquer master in museum records'),
          'Konbaung court workshops (Mindon, Thibaw)': ('Centres & workshops', 'royal lacquer workshops of Mandalay, 1850s–1885'), 'Bagan': ('Centres & workshops', 'centre of yun lacquer'), 'Pegu (Lower Burma)': ('Centres & workshops', 'Lower Burmese lacquer of the 16th-c. Pegu kingdom')},
 'I2-8': {'Qianlong imperial carved lacquer': ('Schools & phases', 'court carved lacquer of 1736–95')},
 'I2-10': {'Tsugaru-nuri': ('Centres & workshops', 'speckled multilayer lacquer of Hirosaki, Aomori'), 'Wajima-nuri': ('Centres & workshops', 'Ishikawa lacquer with diatomaceous-earth ground'), 'Kamakura-bori': ('Sub-types', 'carved wood under red lacquer, Kamakura'),
           'Aizu lacquerware': ('Centres & workshops', 'Fukushima lacquer centre'), 'Kishū lacquerware': ('Centres & workshops', 'Wakayama lacquer centre'), 'Raden': ('Sub-types', 'mother-of-pearl inlay'), 'Ikkan-bari': ('Sub-types', 'lacquer over paper moulded on a form'),
           'Wakasa-nuri': ('Centres & workshops', None)},
 'I2-12': {'lacquering': ('Sub-types', 'lacquering craft (chiljang), the designated counterpart of najeonjang', 'Chiljang')},
 'I2-15': {'Olinalá': ('Centres & workshops', 'Guerrero town of rayado lacquered boxes and gourds'), 'Pátzcuaro': ('Centres & workshops', 'Michoacán centre of painted and gilded maque'),
           'Chiapa de Corzo': ('Centres & workshops', 'Chiapas centre of painted lacquer gourds'), 'Peribán': ('Centres & workshops', 'Michoacán centre of maque')},
 'I3-3': {"The Gentleman and Cabinet-Maker's Director": ('Sub-types', 'Chippendale’s pattern book of 1754, 1755 and 1762'), 'Thomas Chippendale': ('Makers', 'London cabinetmaker, 1718–79')},
 'I3-4': {'George Hepplewhite': ('Makers', 'London cabinetmaker, d. 1786; Guide published 1788')},
 'I3-5': {'Thomas Sheraton': ('Makers', 'English furniture designer, 1751–1806')},
 'I3-10': {'Gustavian style': ('Sub-types', None)},
 'I3-12': {'Lalique glass': ('MOVEOUT', 'F1-9')},
 'I3-22': {'Shaker tape seating': ('Sub-types', None)},
 'I4-1': {'tree-fern grade figures': ('Sub-types', 'tree-fern figures of the graded society, Ambrym and Malakula')},
 'I4-5': {'Mittenwald violin making': ('Centres & workshops', None), 'Mirecourt lutherie': ('Centres & workshops', None), 'Vogtland (Musikwinkel) instrument making': ('Centres & workshops', None), 'Cremonese violin making': ('Centres & workshops', None)},
 'I4-8': {'Welsh triple harp': ('Sub-types', None)},
 'I4-20': {'Bandoneon (Carlsfeld)': ('Centres & workshops', None)},
 'I4-21': {'Great Highland bagpipe': ('Sub-types', None)},
 'I4-23': {'Dutch street organ': ('Sub-types', None)},
}

K['I1-10']['add'].append(('Zuku and muku', SUB, 'shaved yosegi veneer (zuku) and solid-block work (muku)', 'Japanese_puzzle_box', 0))
K['I1-20']['add'] = [('Chernihiv', CEN, 'regional capital of the oblast whose carving tradition is listed in Ukraine’s national ICH inventory', 'Chernihiv', 0)]
K['I1-21']['add'] += [('Carved furniture and interiors', SUB, 'chairs, tables and panelling with dense floral relief', 'Konjic', 0), ('Zanat', CEN, 'Konjic woodcarving workshop and design firm', 'Konjic', 0)]
K['I1-24']['add'].append(('Thuya burl', SUB, 'burl of Tetraclinis articulata, the medium of the craft', 'Tetraclinis', 0))
K['I1-25']['add'].append(('Pinjrakari', SUB, 'Kashmiri wooden lattice work for windows and screens', 'Kashmir_walnut_wood_carving', 0))
K['I1-27']['add'] += [('Wappa bento boxes', SUB, 'round and oval bentwood lunch boxes', 'Magewappa', 0), ('Ohitsu', SUB, 'bentwood rice container', 'Magewappa', 0)]
K['I2-5']['add'].append(('Ankudu wood', SUB, 'soft Wrightia tinctoria wood turned for the toys', 'Etikoppaka', 0))
K['I3-4']['add'].append(("The Cabinet-Maker and Upholsterer's Guide (1788)", SUB, 'Hepplewhite’s posthumous pattern book', 'Hepplewhite', 0))
K['I3-5']['add'].append(("The Cabinet-Maker and Upholsterer's Drawing-Book (1791–94)", SUB, 'Sheraton’s pattern book', 'Thomas_Sheraton', 0))
