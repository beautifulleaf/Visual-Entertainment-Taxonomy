# Per-leaf building-catalogue configuration for pass small_K.
# Each section: (section label, [sources], optional filter). Source "W:<style_label>" (architecture_exemplars.csv)
# or "N:<proposed_style>" (architecture_nonwestern_exemplars.csv). Sections are listed in affinity order.

def yr(r):
    import re
    m = re.match(r"-?\d+", r.get("inception") or "")
    return int(m.group()) if m else None

def before(y):
    return lambda r: (yr(r) is not None and yr(r) < y)
def from_(y):
    return lambda r: (yr(r) is None or yr(r) >= y)
def country(*cs):
    return lambda r: any(c in (r.get("country_label") or r.get("country") or "") for c in cs)

S = {}
def L(code, *secs, black=(), split=None):
    S[code] = dict(secs=list(secs), black=list(black), split=split)

# ---------------- K1 Islamic ----------------
L("K1-1", ("Umayyad mosques, palaces and desert castles", ["W:Umayyad architecture", "W:Umayyad art", "W:Rashidun architecture"]),
          ("Early Islamic buildings before 750", ["N:Early Islamic (Umayyad / Abbasid / Tulunid)"], before(750)))
L("K1-2", ("Abbasid buildings (Iraq, Iran, Egypt)", ["W:Abbasid architecture", "N:Early Islamic (Umayyad / Abbasid / Tulunid)"], from_(750)),
          ("Aghlabid and Idrisid Maghreb (to 909)", ["W:Aghlabid architecture", "N:Early Islamic Maghreb (Aghlabid / Idrisid / Zirid)"], lambda r: yr(r) is None or yr(r) < 909))
L("K1-3", ("Fatimid buildings", ["W:Fatimid architecture", "N:Fatimid"]))
L("K1-4", ("Caliphal Córdoba (Umayyads of al-Andalus)", ["W:art of the Umayyads of Cordoba"]),
          ("Taifa buildings", ["W:Taifa art"]),
          ("Zirid and Hammadid Maghreb (909 onwards)", ["N:Early Islamic Maghreb (Aghlabid / Idrisid / Zirid)"], lambda r: yr(r) is not None and yr(r) >= 909),
          ("Almoravid and Almohad buildings", ["W:art of Almoravides and Almohades", "W:Almohad architecture", "W:Almoravid art", "N:Almoravid / Almohad"]),
          ("Nasrid Granada", ["W:Nasrid architecture"]),
          ("Marinid, Zayyanid and Hafsid buildings", ["W:Marinid architecture", "N:Marinid / Zayyanid / Hafsid"]),
          ("Saadian buildings", ["N:Saadian"]),
          ("Alaouite buildings", ["N:Alaouite"]),
          ("Moorish buildings, phase unassigned", ["W:Moorish architecture", "W:Art of Al-Andalus", "W:Moorish style", "W:Moroccan architecture"]),
          black=["Mazagan"])
L("K1-5", ("Mudéjar of Aragon (UNESCO group)", ["W:Mudéjar architecture of Aragon"]),
          ("Mudéjar buildings of Castile, Andalusia and elsewhere", ["W:Mudéjar architecture", "W:Mudéjar style"]))
L("K1-6", ("Great Seljuk buildings (Iran, Central Asia)", ["W:Seljuk architecture", "W:Razi style", "N:Persian — Seljuk / Khwarazmian"]),
          ("Khwarazmian buildings", ["W:Khwarazmian architecture"]),
          ("Pre-Seljuk Persianate buildings (Samanid, Buyid, Ghaznavid, Ziyarid)", ["N:Persian — early Islamic (Samanid / Buyid / Ghaznavid)", "W:Samanid architecture", "W:Ghaznavid architecture", "W:Buyid architecture", "W:Ziyarid architecture", "W:Saffarid architecture", "W:Tahirid architecture", "W:Ghaznavid art"]),
          ("Nakhchivan school", ["W:Architectural school of Nakhchivan"]),
          ("Arran school", ["W:Arran architectural school"]),
          ("Shirvan–Absheron school", ["W:Shirvan-Absheron architectural school", "N:Azerbaijani (Shirvan–Absheron)"]), split=None)
L("K1-7", ("Anatolian Seljuk and beylik buildings", ["W:Anatolian Seljuk architecture", "N:Anatolian Seljuk / Beylik"]))
L("K1-8", ("Ayyubid buildings (precursor)", ["W:Ayyubid architecture", "N:Ayyubid"]),
          ("Bahri Mamluk buildings (1250–1382)", ["W:Mamluk architecture", "N:Mamluk"], before(1382)),
          ("Burji Mamluk buildings (1382–1517)", ["W:Mamluk architecture", "N:Mamluk"], from_(1382)))
L("K1-9", ("Ilkhanid buildings", ["W:Ilkhanid architecture", "N:Persian — Ilkhanid / Muzaffarid"]),
          ("Azari style buildings", ["W:Azari style"]),
          ("Jalayirid Iraq", ["N:Iraqi Islamic (Ilkhanid / Jalayirid)"]))
L("K1-10", ("Timurid buildings", ["W:Timurid architecture", "W:Timurid art", "N:Timurid"]),
           ("Shaybanid and khanate buildings (post-Timurid Central Asia)", ["N:Central Asian — Shaybanid / khanates (Bukhara, Khiva, Kokand)"]), split=["country"])
L("K1-11", ("Safavid buildings", ["W:Safavid architecture", "N:Persian — Safavid"]),
           ("Isfahani style buildings", ["W:Isfahani style"]))
L("K1-12", ("Ottoman buildings in Anatolia and the Balkans", ["W:Ottoman architecture", "N:Ottoman"]),
           ("Ottoman Baroque buildings", ["W:Ottoman Baroque"]),
           ("Ottoman buildings of the Arab provinces", ["N:Ottoman (Arab provinces)", "W:Ottoman architecture in Egypt"]),
           split=["century", "class"])
L("K1-13", ("Afsharid buildings", ["W:Afsharid architecture"]),
           ("Zand buildings", ["W:Zand architecture"]),
           ("Qajar buildings", ["W:Qajar architecture", "N:Persian — Qajar"]))
L("K1-14", ("Delhi Sultanate buildings", ["N:Indo-Islamic (Delhi Sultanate)", "W:Tughlaq architecture style"]),
           ("Gujarat Sultanate buildings", ["N:Gujarat Sultanate"]),
           ("Bengal Sultanate buildings", ["N:Bengal Sultanate", "W:Bengal Sultanate architecture style"]),
           ("Deccan Sultanate buildings", ["N:Deccan Sultanates (Bahmani / Qutb Shahi / Adil Shahi)", "W:Qutb Shahi architecture", "W:Deccani architecture style"]),
           ("Indo-Islamic buildings, sultanate unassigned", ["W:Indo-Islamic architecture"]))
L("K1-15", ("Mughal buildings", ["W:Mughal architecture", "N:Mughal"]), split="country")
L("K1-16", ("Sudano-Sahelian mosques and buildings", ["W:Sudano-Sahelian architecture", "N:Sudano-Sahelian"]),
           ("Inland Niger Delta towns", ["N:Sudano-Sahelian (urban sites)"]))
L("K1-17", ("Swahili coast buildings and towns", ["W:Swahili architecture", "N:Swahili coast (coral stone)"]))
L("K1-18", ("Chinese Islamic mosques and tombs", ["N:Chinese Islamic"]), split="region")
L("K1-19", ("Javanese and Malay tajug-roofed mosques", ["W:Mosque architecture in Indonesia", "N:Javanese / Malay mosque (tajug)"]), split="country")

# ---------------- K2 revivals ----------------
L("K2-1", ("Moorish Revival buildings", ["W:Moorish Revival architecture", "W:moresque"]), ("Heliopolis style (Egypt)", ["W:Heliopolis style"]))
L("K2-2", ("Neo-Mudéjar buildings", ["W:neo-Mudéjar"]))
L("K2-3", ("Neo-Mamluk buildings", ["W:Neo-Mamluk architecture"]))
L("K2-4", ("First National Architectural Movement buildings", ["W:First national architectural movement"]))
L("K2-5", ("Indo-Saracenic buildings", ["W:Indo-Saracenic architecture"]))
L("K2-7", ("Tudor Revival buildings", ["W:Tudor Revival architecture", "W:Elizabethan Revival"]), ("Jacobethan buildings", ["W:Jacobethan"]), ("English Cottage style houses", ["W:English Cottage architecture"]))
L("K2-8", ("Rundbogenstil buildings", ["W:Rundbogenstil"]), ("Romanesque Revival buildings (Europe)", ["W:Romanesque Revival architecture", "W:Romanesque Revival Architecture in the United Kingdom", "W:Neo-Norman style", "W:Norman Revival architecture", "W:Bristol Byzantine"]),
          ("Romanesque Revival in the United States", ["W:Romanesque Revival architecture in the United States"]), ("Richardsonian Romanesque buildings", ["W:Richardsonian Romanesque"]))
L("K2-9", ("Neo-Byzantine buildings", ["W:Byzantine Revival architecture"]), ("Neo-Byzantine in the Russian Empire", ["W:Neo-Byzantine architecture in the Russian Empire"]), ("Serbo-Byzantine Revival buildings", ["W:Serbo-Byzantine style (modern architecture)"]))
L("K2-11", ("Italianate buildings", ["W:Italianate architecture"]))
L("K2-12", ("Second Empire buildings in France", ["W:Second Empire style", "W:Second Empire architecture in Europe"], country("France")),
           ("Haussmannian buildings (Paris)", ["W:Haussmannian architecture"]),
           ("Second Empire buildings elsewhere in Europe", ["W:Second Empire style", "W:Second Empire architecture in Europe"], lambda r: "France" not in r["country_label"] and r["continent"] != "North America"),
           ("Second Empire in the United States and Canada", ["W:Second Empire architecture in the United States and Canada", "W:Second Empire style"], lambda r: r["continent"] == "North America"))
L("K2-13", ("Neo-Baroque buildings", ["W:baroque revival", "W:neobarroc"]), ("Edwardian Baroque buildings", ["W:Edwardian architecture"]), ("Rococo Revival buildings", ["W:Rococo Revival architecture", "W:Rococo Revival"]))
L("K2-14", ("Greek Revival buildings", ["W:Greek Revival architecture"]), ("Antebellum (American South)", ["W:Antebellum architecture"]), ("Néo-Grec buildings", ["W:Neo-Grec"]), ("Neo-Pompeian buildings", ["W:neo-pompeian style"]))
L("K2-15", ("Egyptian Revival buildings", ["W:Egyptian Revival architecture", "W:Egyptian Revival"]))
L("K2-16", ("Beaux-Arts buildings", ["W:Beaux-Arts", "W:Belgian Beaux-Arts architecture"]), ("American Renaissance buildings", ["W:American Renaissance"]), ("City Beautiful movement", ["W:City Beautiful movement"]))
L("K2-18", ("Victorian buildings (Britain and Empire)", ["W:Victorian architecture"]), ("Stick style", ["W:Stick style"]), ("Folk Victorian", ["W:Folk Victorian"]), ("Late Victorian Plain (Canada)", ["W:Late Victorian Plain"]),
           ("Victorian Free Classical (Australia)", ["W:Victorian Free Classical"]), ("Victorian Filigree (Australia)", ["W:Victorian Filigree architecture"]), ("Gingerbread houses (Haiti)", ["W:Gingerbread house"]))
L("K2-19", ("Queen Anne Revival in Britain", ["W:Queen Anne Revival architecture", "W:Queen Anne style"], lambda r: r["continent"] != "North America"),
           ("Queen Anne style in the United States and Canada", ["W:Queen Anne style architecture in the United States", "W:Queen Anne style", "W:Free Classic Queen Anne style"], lambda r: r["continent"] == "North America"),
           ("Eastlake buildings", ["W:Eastlake Movement", "W:Eastlake üslubu"]))
L("K2-20", ("Shingle style buildings", ["W:Shingle style architecture"]))
L("K2-21", ("Colonial Revival buildings", ["W:Colonial Revival architecture"]), ("Georgian Revival buildings", ["W:Georgian Revival architecture"]), ("Dutch Colonial Revival houses", ["W:Dutch Colonial Revival architecture"]))
L("K2-22", ("Spanish Colonial Revival buildings", ["W:Spanish Colonial Revival architecture"]), ("Mediterranean Revival buildings", ["W:Mediterranean Revival architecture"]), ("Spanish Eclectic buildings", ["W:Spanish Eclectic architecture"]))
L("K2-23", ("Mission Revival buildings", ["W:Mission Revival architecture"]))
L("K2-24", ("Pueblo Revival buildings", ["W:Pueblo Revival Style architecture"]), ("Territorial style", ["W:Territorial architecture"]), ("Territorial Revival", ["W:Territorial Revival architecture"]), ("Pueblo Deco", ["W:Pueblo Deco architecture"]))
L("K2-25", ("Mayan Revival buildings", ["W:Mayan Revival architecture"]))
L("K2-26", ("Neo-Manueline buildings", ["W:Neo-Manueline"]))
L("K2-27", ("Russian Revival buildings", ["W:Russian Revival architecture"]), ("Russian-Byzantine (Thon) style", ["W:Russian-Byzantine architecture"]), ("Brick style (kirpichny stil)", ["W:brick style"]))
L("K2-28", ("Neoclassical Revival buildings", ["W:Russian Neoclassical Revival"]), ("Retrospectivist buildings", ["W:Retrospectivist architecture"]))
L("K2-29", ("Romanian Revival buildings", ["W:Romanian Revival architecture", "W:Neo-Moldavian architecture"]))
L("K2-30", ("National Romantic buildings (Nordic countries)", ["W:national Romantic style", "W:romantic nationalism"]), ("Dragestil (Norway)", ["W:dragestil"]), ("Northern Modern (Russia)", ["W:Northern modern"]),
           ("Polish manor style and national style", ["W:styl dworkowy", "W:national style"]))
L("K2-31", ("Zakopane Style buildings", ["W:Zakopane Style architecture"]))
L("K2-32", ("Swiss chalet style buildings", ["W:Swiss chalet style"]))
L("K2-33", ("Federation buildings", ["W:Federation architecture"]))
L("K2-34", ("National Park Service rustic", ["W:National Park Service rustic"]), ("WPA Rustic", ["W:WPA Rustic"]), ("Forest Service rustic", ["W:Forest Service rustic"]), ("Adirondack Great Camps", ["W:Adirondack Architecture"]), ("Rustic buildings, other", ["W:rustic architecture"]))

# ---------------- K3 ancient ----------------
L("K3-1", ("Ancient Egyptian temples, tombs and pyramids", ["W:ancient Egyptian architecture", "W:Late Egyptian"]))
L("K3-2", ("Elamite buildings", ["W:Elamite architecture"]))
L("K3-3", ("Median buildings (precursor)", ["W:Median architecture"]), ("Achaemenid buildings", ["W:Achaemenid architecture"]))
L("K3-4", ("Parthian buildings", ["W:Parthian architecture"]))
L("K3-5", ("Sasanian buildings", ["W:Sasanian architecture"]))
L("K3-6", ("Minoan palaces and sites", ["W:Minoan civilization"]))
L("K3-7", ("Mycenaean citadels and tombs", ["W:Cyclopean masonry"], country("Greece")))
L("K3-8", ("Archaic and Classical Greek buildings", ["W:ancient Greek architecture", "W:Doric order", "W:Ionic order", "W:Corinthian order", "W:peripteral", "W:amphiprostyle", "W:tetrastyle"]),
          ("Hellenistic buildings", ["W:Hellenistic architecture", "W:Hellenistic period", "W:Seleucid architecture"]))
L("K3-9", ("Etruscan buildings and tombs", ["W:Etruscan architecture"]))
L("K3-10", ("Roman buildings", ["W:ancient Roman architecture", "W:Tuscan order", "W:Composite order", "W:tetrapylon", "W:Romano-British culture"]))
L("K3-11")

# ---------------- K4 medieval ----------------
L("K4-1", ("Early Christian basilicas, baptisteries and catacombs", ["W:Early Christian architecture", "W:early Christian art"]))
L("K4-2", ("Byzantine churches and buildings", ["W:Byzantine architecture", "W:Byzantine art", "W:Macedonian Renaissance", "W:Renaixement Comnè"]), ("Cross-in-square churches", ["W:cross-in-square"]))
L("K4-3", ("Raška school", ["W:Rascian architecture"]), ("Serbo-Byzantine churches", ["W:Serbo-Byzantine architecture"]), ("Morava school", ["W:Morava architectural school"]))
L("K4-4", ("Kievan Rus' churches", ["W:Architecture of Kievan Rus'"]), ("Vladimir-Suzdal school", ["W:Vladimir-Suzdal school (art)", "W:Russian Romanesque"]),
          ("Polotsk school", ["W:Architectural school of Polock"]), ("Hrodna school", ["W:architectural school of Hrodna"]), ("Pskov school", ["W:Pskov architectural style"]))
L("K4-5", ("Armenian churches and monasteries", ["W:Armenian architecture", "W:Armenian church architecture"]))
L("K4-6", ("Georgian churches and monasteries", ["W:architecture of Georgia"]))
L("K4-7", ("Visigothic buildings", ["W:Visigothic architecture", "W:Visigothic art"]), ("Merovingian buildings", ["W:Merovingian art", "W:Merovingian architecture"]), ("Lombard buildings", ["W:Lombard architecture"]),
          ("Asturian buildings", ["W:Asturian architecture", "W:pre-Romanesque art"], country("Spain")), ("Mozarabic and Repoblación buildings", ["W:Mozarabic architecture", "W:Mozarabic art", "W:Repoblación art and architecture"]),
          ("Anglo-Saxon buildings", ["W:Anglo-Saxon architecture", "W:Anglo-Saxon art"]), ("Pre-Romanesque buildings, region unassigned", ["W:Pre-Romanesque architecture", "W:pre-Romanesque art"]))
L("K4-8", ("Carolingian buildings", ["W:Carolingian architecture", "W:Carolingian Renaissance"]))
L("K4-9", ("Ottonian buildings", ["W:Ottonian architecture", "W:Ottonian art"]))
L("K4-10", ("First Romanesque (Lombard band)", ["W:First Romanesque"]), ("Catalan Romanesque", ["W:Romanesque art in Catalonia"]), ("Spanish Romanesque", ["W:Romanesque architecture in Spain", "W:Romanesque art in Segovia Province", "W:Romanesque art in Galicia", "W:Romanesque art in Aragon"]),
           ("French Romanesque", ["W:French Romanesque architecture", "W:Romanesque art in Auvergne"]), ("Provençal Romanesque", ["W:Romanesque art of Provence"]), ("Norman and Anglo-Norman Romanesque", ["W:Norman architecture"]),
           ("Italian Romanesque", ["W:romanesque architecture in Italy"]), ("Pisan Romanesque", ["W:romanesque arte in Pisa"]), ("Florentine Romanesque (Proto-Renaissance)", ["W:Proto-Renaissance", "W:romanesque architecture in Florence"]),
           ("Apulian Romanesque", ["W:Romanesque art in Apulia"]), ("Sardinian Romanesque", ["W:Romanesque architecture in Sardinia"]), ("Mosan Romanesque", ["W:Mosan art"]),
           ("Polish Romanesque", ["W:Romanesque architecture in Poland"]), ("Portuguese Romanesque", ["W:Portuguese Romanesque architecture"]), ("Brick Romanesque", ["W:Brick Romanesque Architecture", "W:Brick Romanesque Style"]),
           ("Cistercian abbeys", ["W:Cistercian architecture"]), ("Romanesque buildings, region unassigned", ["W:Romanesque architecture", "W:Romanesque art"]),
           black=["Arm reliquary"])
L("K4-11", ("Arab-Norman buildings of Palermo, Cefalù and Monreale", ["W:Norman-Arab-Byzantine culture", "W:Norman architecture of Sicily"]))
L("K4-12", ("Moldavian churches and monasteries", ["W:architecture of Moldova"]))

# ---------------- K5 early modern ----------------
L("K5-1", ("Tudor buildings", ["W:Tudor architecture"]), ("Elizabethan buildings", ["W:Elizabethan architecture"]))
L("K5-2", ("Plateresque buildings", ["W:Plateresque", "W:Estilo Cisneros"]))
L("K5-3", ("Manueline buildings", ["W:Manueline"]))
L("K5-4", ("Herrerian buildings", ["W:Herrerian"]), ("Neo-Herrerian buildings", ["W:arquitectura neoherreriana"]))
L("K5-5", ("Churrigueresque buildings", ["W:Churrigueresque"]))
L("K5-6", ("Régence buildings", ["W:Regence style"]), ("French Rococo (Louis XV) buildings", ["W:Louis Quinze"]), ("Rococo buildings in Central Europe", ["W:Rococo architecture", "W:Rococo"]),
          ("Frederician Rococo", ["W:Frederician Rococo"]), ("Chinoiserie pavilions", ["W:chinoiserie"]))
L("K5-7", ("Uzorochye churches and palaces", ["W:Uzorochye"]), ("Yaroslavl school", ["W:Yaroslavl school", "W:architecture of Yaroslavl"]), ("Tented-roof churches", ["W:tented-roof church"]))
L("K5-8", ("Brâncovenesc churches, monasteries and palaces", ["W:Brâncovenesc art", "W:Brâncovenesc style"]))
L("K5-9", ("Palladian and Neo-Palladian buildings", ["W:Palladian architecture"]), ("Jeffersonian buildings", ["W:Jeffersonian architecture"]))
L("K5-10", ("Georgian buildings", ["W:Georgian architecture"]), ("Adam style", ["W:Adam style"]), ("Regency buildings", ["W:Regency architecture"]))
L("K5-11", ("Empire style buildings", ["W:Empire style"]), ("Russian Empire style", ["W:Russian Empire style"]))
L("K5-12", ("Federal style buildings", ["W:Federal architecture"]))
L("K5-13", ("Pombaline buildings (Lisbon)", ["W:Pombaline style"]))
L("K5-14", ("Bulgarian Revival churches, houses and schools", ["W:The Architecture of the Bulgarian Revival", "W:Bulgarian National Revival"]), ("Zheravna and Teteven houses", ["W:Жеравненска къща", "W:Тетевенска къща"]))
L("K5-15", ("First Period (New England)", ["W:First Period"]), ("Saltbox houses", ["W:saltbox"]), ("Cape Cod houses", ["W:Cape Cod"]), ("Tidewater houses", ["W:Tidewater architecture"]), ("American colonial buildings, other", ["W:American colonial architecture"]))
L("K5-16", ("Spanish colonial buildings", ["W:Spanish Colonial architecture", "W:Spanish Colonial style"]), ("New Spanish Baroque", ["W:New Spanish Baroque", "W:baroque architecture in New Spain"]), ("Hispanic Baroque", ["W:Hispanic baroque"]),
           ("Earthquake Baroque (Philippines)", ["W:Earthquake Baroque"]), ("Monterey Colonial (California)", ["W:Monterey Colonial architecture"]))
L("K5-17", ("Andean Baroque churches", ["W:Andean Baroque"]))
L("K5-18", ("Portuguese colonial buildings", ["W:Portuguese colonial architecture"]), ("Brazilian colonial and Baroque", ["W:colonial architecture of Brazil", "W:Brazilian baroque", "W:barroco mineiro"]))
L("K5-19", ("French colonial buildings", ["W:French Colonial"]), ("Creole architecture (Louisiana and Gulf Coast)", ["W:Creole architecture in the United States"]), ("Creole case (Antilles)", ["W:Creole case"]))
L("K5-20", ("New Netherland (Dutch colonial America)", ["W:Dutch Colonial architecture in New Netherlands"]), ("Dutch colonial buildings in Asia, Africa and the Caribbean", ["W:Dutch colonial architecture"]), ("Indies Empire and New Indies styles", ["W:Indies Empire style", "W:New Indies style"]))
L("K5-21", ("Cape Dutch homesteads and buildings", ["W:Cape Dutch architecture"]))

# ---------------- K6 modern ----------------
L("K6-1", ("Arts and Crafts houses and buildings", ["W:Arts and Crafts movement"]), ("Cottage style (Low Countries)", ["W:cottage style", "W:cottage"]), ("English mansion style (Netherlands)", ["W:English mansion style in the Netherlands"]),
          ("American Craftsman", ["W:American Craftsman"]), ("California and airplane bungalows", ["W:California bungalow", "W:Airplane Bungalow"]))
L("K6-2", ("Chicago School buildings", ["W:Chicago School"]))
L("K6-3", ("Prairie School buildings", ["W:Prairie School architecture", "W:Prairie architecture style"]))
L("K6-4", ("Czech Cubist buildings", ["W:cubism"]), ("Rondocubist buildings", ["W:Rondocubism"]))
L("K6-5", ("Expressionist buildings (Germany and elsewhere)", ["W:expressionist architecture", "W:Expressionism", "W:organický expresionismus"]), ("Brick Expressionism", ["W:Brick Expressionism", "W:Backsteinexpressionismus in Hannover"]),
          ("Amsterdam School", ["W:Amsterdam School"]), ("Dudok style", ["W:Dudok-trant"]), ("Dom Bellot style", ["W:dombellotisme"]))
L("K6-6", ("Futurist buildings and projects", ["W:futurist architecture", "W:Futurism"]), ("Googie", ["W:Googie"]), ("Neo-futurist buildings", ["W:neo-futurism"]))
L("K6-7", ("Art Deco buildings", ["W:Art Deco architecture", "W:Art Deco", "W:Art Deco architecture in Reims", "W:Art Deco Revival"]), ("Valencian Art Deco", ["W:Art Deco in the Land of Valencia"]),
          ("Streamline Moderne buildings", ["W:Streamline Moderne architecture", "W:Streamline Moderne", "W:Moderne architecture"]), ("PWA Moderne buildings", ["W:PWA Moderne"]))
L("K6-8", ("Bauhaus buildings", ["W:Bauhaus", "W:Bauhaus modernism"]))
L("K6-9", ("International Style buildings", ["W:International Style"]), ("International Style in Israel (White City)", ["W:International style in Israel"]))
L("K6-10", ("Constructivist buildings", ["W:constructivist architecture", "W:Constructivism", "W:avant-garde architecture of the Soviet Union"]), ("Postconstructivist buildings", ["W:Postconstructivism"]))
L("K6-11", ("Reform architecture buildings", ["W:Reform Architecture"]), ("Um 1800", ["W:Um 1800"]), ("Heimatschutz architecture", ["W:Heimatschutz architecture"]), ("Heimatstil", ["W:Heimatstil"]), ("Gruppenbau", ["W:Gruppenbau"]))
L("K6-12", ("Traditionalist School buildings", ["W:Traditionalist School"]), ("Delft School", ["W:Delftse School"]), ("Bossche School", ["W:Bossche School"]))
L("K6-13", ("Nordic Classicism buildings", ["W:Nordic Classicism"]))
L("K6-14", ("Stripped Classicism buildings", ["W:Stripped Classicism"]))
L("K6-16", ("Novecento buildings", ["W:Novecento Italiano"]), ("Fascist-period buildings", ["W:architecture of the Fascist period", "W:fascist architecture in Italy", "W:Stile Littorio"]), ("Monumentalist buildings", ["W:monumentalism in architecture"]))
L("K6-17", ("Nazi buildings", ["W:Nazi architecture"]))
L("K6-18", ("Mid-century modern buildings", ["W:mid-century modern"]), ("Miami Modern (MiMo)", ["W:Miami Modern architecture"]), ("Sarasota School", ["W:Sarasota School of Architecture"]), ("Northwest Regional style", ["W:Northwest Regional style"]))
L("K6-19", ("High-tech buildings", ["W:high-tech architecture"]))
L("K6-20", ("New Classical buildings", ["W:New Classical architecture", "W:Neoclassicalism", "W:Neo-Historism"]))
L("K6-23", ("Brutalist buildings", ["W:brutalist architecture"]), ("Czechoslovak New Brutalism", ["W:nový brutalismus"]))
L("K6-24", ("Postmodern buildings", ["W:postmodern architecture", "W:Postmodernism", "W:Italian postmodern architecture", "W:postmodern architecture in Russia"]), ("New Urbanism", ["W:New Urbanism"]))
L("K6-25", ("Deconstructivist buildings", ["W:deconstructivism"]))

# ---------------- K7 South Asia ----------------
L("K7-1", ("Nagara temples of central and north India", ["N:Nagara — central / north India"]), ("Chandela temples (Khajuraho)", ["N:Nagara — Chandela (Khajuraho)"]),
          ("Bhumija and Hemadpanti temples (Deccan)", ["N:Nagara — Bhumija / Hemadpanti (Deccan)"]), ("Himalayan Nagara temples", ["N:Nagara — Himalayan (Himachal / Uttarakhand)"]),
          ("Kashmiri temples (Karkota and Utpala)", ["N:Kashmiri (Karkota / Utpala)"]), ("Assamese (Ahom) temples", ["N:Assamese / Ahom temple"]),
          black=["Sanchi", "Dhamek", "Chaukhandi"], split=["region"])
L("K7-2", ("Kalinga (Odishan) temples", ["W:Kalinga architecture", "W:Rekha deul", "N:Nagara — Kalinga (Odisha)"]), ("Deul temples outside Odisha", ["W:Deul"]), split=None)
L("K7-3", ("Maru-Gurjara temples", ["W:Māru-Gurjara architecture", "N:Nagara — Maru-Gurjara"]), split="region")
L("K7-4", ("Pallava temples", ["N:Dravidian — Pallava"]), ("Chola temples", ["N:Dravidian — Chola"]), ("Vijayanagara temples", ["N:Dravidian — Vijayanagara"]), ("Kakatiya temples", ["N:Kakatiya", "W:Kakatiya architecture"]),
          ("Later Dravidian temples (after 1736)", ["N:Dravidian — modern (after 1736)"]), ("Dravidian temples of Tamil Nadu and the south, period unassigned", ["W:Dravidian architecture", "W:Tamil architecture", "N:Dravidian (undated)"]),
          ("Andhra Dravidian temples", ["N:Andhra Dravidian (other / undated)"]), ("Karnataka Dravidian temples", ["N:Karnataka Dravidian (other / undated)"]), ("Sri Lankan kovils", ["N:Sri Lankan Dravidian (kovil)"]), split=None)
L("K7-5", ("Badami Chalukya temples", ["N:Badami Chalukya", "W:Badami Chalukya architecture"]), ("Western Chalukya (Kalyani) temples", ["N:Western Chalukya (Kalyani)"]), ("Hoysala temples", ["N:Hoysala", "W:Hoysala architecture"]))
L("K7-6", ("Kerala temples", ["N:Kerala temple architecture", "W:architecture of Kerala"]), split=["place"])
L("K7-7", ("At-chala temples", ["W:At-chala"]), ("Char-chala temples", ["W:Char-chala"]), ("Do-chala temples", ["W:Do-chala"]), ("Jor-bangla temples", ["W:Jor-bangla"]),
          ("Ek-ratna temples", ["W:Ek-ratna"]), ("Pancharatna temples", ["W:Pancharatna"]), ("Navaratna temples", ["W:Navaratna"]), ("Higher ratna temples (13, 17, 25 pinnacles)", ["W:Trayodash-ratna", "W:Saptadash-ratna", "W:Panchabimsati-ratna"]),
          ("Dalan temples", ["W:dalan"]), ("Bengal temples, type unassigned", ["N:Bengal temple (chala / ratna, terracotta)", "W:Baro-chala"]))
L("K7-8", ("Early Buddhist stupas, viharas and chaityas (Maurya to Pala)", ["N:Early Buddhist (Maurya – Gupta – Pala)", "W:Buddhist architecture"]), ("Gandharan Buddhist sites", ["N:Gandharan Buddhist", "W:Greco-Buddhist art"]),
          black=["Buddhas of Bamiyan"])
L("K7-9", ("Rock-cut caves and temples", ["N:Indian rock-cut (caves)", "W:rock-cut architecture in India"]))
L("K7-10", ("Anuradhapura period", ["N:Sinhalese — Anuradhapura"]), ("Polonnaruwa period", ["N:Sinhalese — Polonnaruwa"]), ("Kandyan period", ["N:Sinhalese — Kandyan"]), ("Sinhalese Buddhist sites, period unassigned", ["N:Sinhalese Buddhist (other)"]), split=["region", "class"])
L("K7-11", ("Newar temples, stupas and palaces (Kathmandu valley)", ["N:Newar (Kathmandu valley)", "W:Newa architecture"]), split=None)
L("K7-12", ("Tibetan Buddhist monasteries and temples", ["N:Tibetan Buddhist", "W:Tibetan Buddhist architecture"]), black=["Vikram"], split="region")
L("K7-13", ("Bhutanese dzongs", ["N:Bhutanese dzong", "W:dzong"]))
L("K7-14", ("Rajput forts and palaces", ["N:Rajput (forts and palaces)", "W:Rajasthani architecture style"]), ("Maratha hill and sea forts (Deccan)", ["N:Deccan hill and sea forts (Maratha era)"]), split=["class"])
L("K7-15", ("Stepwells", ["N:Stepwell (western India)"]), split="region")
L("K7-16", ("Gurdwaras and Sikh buildings", ["W:Sikh architecture"]))
L("K7-17", ("Harappan cities and sites", ["N:Harappan (Indus)"]))
for c in ("K7-18", "K7-19", "K7-20"): L(c)

# ---------------- K8 East Asia ----------------
L("K8-1", ("Pre-Tang buildings (to 617)", ["N:Chinese — pre-Tang (to 617)"]), ("Tang buildings (618–907)", ["N:Chinese — Tang (618–907)"]), ("Liao, Song and Jin buildings (907–1279)", ["N:Chinese — Liao / Song / Jin (907–1279)"]),
          ("Yuan buildings (1279–1368)", ["N:Chinese — Yuan (1279–1368)"]), ("Ming buildings (1368–1644)", ["N:Chinese — Ming (1368–1644)"]), ("Qing buildings (1644–1912)", ["N:Chinese — Qing (1644–1912)"]),
          ("Imperial palaces and paifang", ["W:Chinese Palaces", "W:paifang", "W:Imperial Chinese Architecture Style"]), ("Chinese buildings, period unassigned", ["W:Chinese architecture"]),
          ("Chinese temples, period unassigned", ["N:Chinese temple (undated)"]), split="class")
L("K8-2", ("Siheyuan", ["W:siheyuan"]), ("Sanheyuan (Taiwan)", ["W:sanheyuan"]))
L("K8-3"); L("K8-6"); L("K8-9")
L("K8-4", ("Tulou and walled villages", ["I:tulou cluster", "I:tulou"]))
L("K8-5", ("Hui-style villages, houses and halls", ["W:Hui-style architecture"]))
L("K8-7", ("Taiwanese (Minnan) temples", ["N:Taiwanese (Minnan) temple"]), split=["region", "class"])
L("K8-8", ("Sichuanese buildings", ["W:Sichuanese architecture", "W:vernacular residential architecture of Western Sichuan"]))
L("K8-10", ("Shinmei-zukuri shrines", ["W:Shinmei-zukuri"]), ("Taisha-zukuri shrines", ["W:Taisha-zukuri"]), ("Sumiyoshi-zukuri shrines", ["W:Sumiyoshi-zukuri"]), ("Nagare-zukuri shrines", ["W:nagare-zukuri"]),
           ("Kasuga-zukuri shrines", ["W:Kasuga-zukuri"]), ("Hachiman-zukuri shrines", ["W:Hachiman-zukuri"]), ("Hiyoshi-zukuri shrines", ["W:Hiyoshi-zukuri"]), ("Ishi-no-ma-zukuri (gongen-zukuri) shrines", ["W:Ishi-no-ma-zukuri"]),
           ("Sengen-zukuri shrines", ["W:Sengen-zukuri"]), ("Other honden styles (Ōtori, Kashii, Kibitsu, Gion, Owari, Oki, Nakayama)", ["W:Ōtori-zukuri", "W:Kashii-zukuri", "W:Kibitsu-zukuri", "W:Gion-zukuri", "W:Owari-zukuri", "W:Oki-zukuri", "W:Nakayama-zukuri", "W:yatsumune-zukuri"]),
           ("Shinto shrines, honden style unassigned", ["N:Shinto shrine"]), split="jregion")
L("K8-11", ("Asuka and Nara temples (538–794)", ["N:Japanese Buddhist — Asuka / Nara (538–794)", "W:Shitennō-ji style"]), ("Heian temples (794–1185)", ["N:Japanese Buddhist — Heian (794–1185)"]),
           ("Kamakura temples: Daibutsuyō and Zenshūyō", ["N:Japanese Buddhist — Kamakura (Daibutsuyō / Zenshūyō)", "W:Daibutsuyō"]), ("Wayō and Setchūyō halls", ["W:Wayō", "W:Setchūyō"]),
           ("Muromachi and Momoyama temples", ["N:Japanese Buddhist — Muromachi / Momoyama"]), ("Edo temples", ["N:Japanese Buddhist — Edo"]),
           ("Kakezukuri, sayadō, azekura and gates", ["W:kakezukuri", "W:さやと", "W:azekura-zukuri", "W:rōmon"]), ("Japanese Buddhist temples, period unassigned", ["N:Japanese Buddhist (undated)", "W:Japanese Buddhist architecture"]), split="jregion")
L("K8-12", ("Shinden-zukuri palaces and halls", ["W:Shinden-zukuri"]))
L("K8-13", ("Shuden-zukuri halls", ["W:shuden-zukuri"]), ("Shoin-zukuri halls and residences", ["W:shoin-zukuri"]))
L("K8-14", ("Sukiya-zukuri villas and residences", ["W:sukiya-zukuri"]), ("Chashitsu (tea houses)", ["W:chashitsu", "W:sōan"]), ("Modern Japanese-style (kindai wafū) buildings", ["W:modern Japanese-style architecture"]))
L("K8-15", ("Nōka farmhouses", ["W:minka", "W:Kudozukuri", "W:Tamugimata multilayered house"]), ("Gasshō-zukuri houses", ["W:gasshō-zukuri"]), ("Magariya (L-shaped farmhouses)", ["W:magariya"]),
           ("Machiya (townhouses)", ["W:machiya"]), ("Kominka (preserved old houses)", ["I:kominka"]), ("Dozō (kura storehouses)", ["W:dozō"]), ("Buke yashiki and nagayamon", ["W:buke yashiki", "W:nagayamon"]))
L("K8-16", ("Japanese castles", ["N:Japanese castle", "W:Japanese castle architecture", "W:southern Kyushu type castle"]), split="jregion")
L("K8-17", ("Keyhole-shaped kofun (zenpō-kōen-fun)", ["W:zenpō-kōen-fun", "W:Makimuku-type keyhole-shaped kofun"]), ("Zenpō-kōhō-fun", ["W:Zenpō-kōhō-fun"]), ("Scallop-shaped kofun", ["W:scallop-shaped kofun"]),
           ("Round kofun", ["W:round-topped burial mound"]), ("Square and rectangular kofun", ["W:square kofun", "W:Rectangular Kofun", "W:Sōhō-chūen Kofun"]), ("Octagonal kofun", ["W:octagonal kofun"]),
           ("Kofun, shape unassigned", ["N:Kofun (mounded tombs)"]), split="jregion")
L("K8-18", ("Ryukyuan gusuku, palaces and tombs", ["W:Ryukyuan architecture", "W:hahubaka"]))
L("K8-19", ("Giyōfū buildings", ["W:Giyōfū architecture"]), ("Japanese-Western eclectic buildings", ["W:Japanese-Western Eclectic Architecture"]))
L("K8-20", ("Three Kingdoms and Unified Silla temples", ["N:Korean Buddhist — Three Kingdoms / Unified Silla"]), ("Goryeo temples", ["N:Korean Buddhist — Goryeo"]), ("Joseon buildings", ["N:Korean — Joseon"]),
           ("Korean buildings, other", ["W:Korean architecture"]), ("Korean Buddhist temples, period unassigned", ["N:Korean Buddhist (undated)"]), split=["region"])
L("K8-21")

# ---------------- K9 Southeast Asia ----------------
L("K9-1", ("Pre-Angkorian temples", ["N:Pre-Angkorian Khmer"]), ("Angkorian temples", ["N:Khmer (Angkorian)", "W:Khmer architecture"]), ("Provincial Angkorian temples (Thailand, Laos)", ["N:Khmer (Angkorian, provincial)"]),
          ("Post-Angkorian Buddhist buildings", ["N:Cambodian Buddhist (post-Angkor)"]), split=["region", "country"])
L("K9-2", ("Central Javanese candi (Mataram)", ["N:Javanese candi — Central Java (Mataram)"]), ("East Javanese candi (Kediri, Singhasari, Majapahit)", ["N:Javanese candi — East Java (Kediri / Singhasari / Majapahit)"]),
          ("Sumatran candi (Srivijaya and Melayu)", ["N:Sumatran candi (Srivijaya / Melayu)"]), ("Javanese candi, period unassigned", ["N:Javanese candi (other)"]), black=["Sri Mariamman"])
L("K9-3", ("Balinese pura (temples)", ["N:Balinese (pura)"]), ("Balinese buildings, other", ["W:Balinese architecture"]), split=None)
L("K9-4")
L("K9-5", ("Pagan temples and stupas", ["N:Burmese — Pagan"]), ("Mrauk U (Arakan)", ["N:Arakanese (Mrauk U)"]), ("Post-Pagan Burmese pagodas and monasteries", ["N:Burmese Buddhist (post-Pagan)"]), split=["region"])
L("K9-6", ("Sukhothai", ["N:Thai — Sukhothai"]), ("Lanna", ["N:Thai — Lanna"]), ("Ayutthaya", ["N:Thai — Ayutthaya"]), ("Rattanakosin", ["N:Thai — Rattanakosin"]), ("Thai buildings, period unassigned", ["W:Thai architecture", "W:architecture of Thailand"]), split=["region"])
L("K9-7", ("Lao temples and stupas", ["N:Lao (Lan Xang / Luang Prabang)"]))
L("K9-8", ("Cham temple towers", ["N:Cham"]))
L("K9-9", ("Vietnamese Buddhist pagodas", ["N:Vietnamese Buddhist (Lý – Nguyễn)"]), ("Vietnamese buildings, other", ["W:Vietnamese architecture", "W:Trùng thiềm điệp ốc"]))
L("K9-10"); L("K9-11")
L("K9-12", ("Bahay na bato houses", ["W:bahay na bato"]))
L("K9-13", ("Sino-Portuguese buildings", ["W:Sino-Portuguese architecture"]))
L("K9-14", ("Malay houses and palaces", ["W:Malay architecture", "W:architecture of Malaysia"]))

# ---------------- K10 Africa ----------------
L("K10-1", ("Aksumite sites", ["N:Aksumite"]))
L("K10-2", ("Rock-hewn churches", ["N:Ethiopian rock-hewn churches"]), black=["Abu Simbel", "Ruins of Aksum"])
L("K10-3", ("Gondarine castles and churches", ["N:Gondarine (Ethiopia)"]))
L("K10-4", ("Kushite pyramids, temples and towns", ["N:Kushite (Napatan / Meroitic)"]), split=["class"])
L("K10-5", ("Zimbabwe culture dry-stone sites", ["N:Zimbabwe culture (dry-stone)"]), black=["Tsodilo", "Makapansgat", "Kubu"])
L("K10-6", ("Maghrebi ksour and kasbahs", ["N:Maghrebi earthen (ksar / kasbah)", "I:ksar", "I:kasbah"]), ("Saharan stone ksour (Mauritania)", ["N:Saharan stone (Mauritania ksour)"]), black=["Nouakchott"], split="country")
L("K10-7")

# ---------------- K11 Americas ----------------
L("K11-1", ("Southern lowland Maya (Petén, Usumacinta, Belize)", ["N:Maya — southern lowlands (Petén / Usumacinta / Belize)"]), ("Maya highlands and southeast (Guatemala, Copán)", ["N:Maya — highlands and southeast (Guatemala highlands, Copán)"]),
           ("Río Bec", ["N:Maya — Río Bec"]), ("Chenes", ["N:Maya — Chenes"]), ("Puuc", ["N:Maya — Puuc"]), ("Northern lowland Maya", ["N:Maya — northern lowlands"]), ("Maya sites, region unassigned", ["N:Maya (unlocated)", "W:Maya architecture"]), split=["country", "region"])
L("K11-2", ("Olmec sites", ["N:Olmec"]), ("Teotihuacan", ["N:Teotihuacan"]), ("Zapotec and Mixtec sites (Oaxaca)", ["N:Zapotec / Mixtec (Oaxaca)"]), ("Classic Veracruz and Totonac sites", ["N:Classic Veracruz / Totonac"]),
           ("Toltec sites", ["N:Toltec"]), ("Mesoamerican sites of central and western Mexico, culture unassigned", ["N:Mesoamerican (central / western Mexico, unassigned)", "W:Mesoamerican architecture"]), black=["Guilá Naquitz", "Gheo-Shih"], split=["region"])
L("K11-3", ("Aztec sites", ["N:Aztec"]))
L("K11-4", ("Inca sites", ["N:Inca", "W:Inca architecture"]), split=["region","country"])
L("K11-5", ("Caral / Norte Chico", ["N:Caral / Norte Chico"]), ("Chavín", ["N:Chavín"]), ("Moche", ["N:Moche"]), ("Wari", ["N:Wari"]), ("Chimú", ["N:Chimú"]), ("Chachapoya", ["N:Chachapoya"]),
           ("Regional cultures (Recuay, Lima, Sicán ...)", ["N:Andean regional (Recuay, Lima, Sicán, ...)"]), ("Andean sites, culture unassigned (incl. Tiwanaku)", ["N:Andean (culture unassigned)"]), black=["Toro Muerto", "שלום", "Stela", "Portal of the Falcons", "Obelisk", "Lanzón"], split=["region","country"])
L("K11-6", ("Ancestral Puebloan great houses, cliff dwellings and pueblos", ["N:Ancestral Puebloan", "W:Pueblo architecture"]), split="region")
L("K11-7", ("Mound Builder earthworks", ["N:Mississippian / mound builders"]))

# ---------------- K12 Oceania & vernacular ----------------
L("K12-5", ("Marae", ["I:marae"]), ("Rapa Nui ahu", ["N:Rapa Nui (ahu / moai)"]), ("Tongan langi and trilithon", ["N:Tongan megalithic (langi / trilithon)"]))
L("K12-6", ("Saudeleur megalithic sites", ["N:Nan Madol (Saudeleur megalithic)"]), black=["Leluh"])
L("K12-7", ("Churches of Chiloé", ["W:Chilotan architecture"]))
L("K12-8", ("British vernacular buildings", ["W:Cotswold architecture"], country("United Kingdom")))
L("K12-9", ("Fachwerk houses in Germany", ["W:timber-framed house", "W:Fachwerkarchitektur", "W:half-timbering", "W:timber framing"], country("Germany")))
L("K12-11", ("Vainakh towers", ["W:Ingush architecture"]))
L("K12-14", ("I-houses", ["W:I-house"]), ("Gablefront houses", ["W:gablefront house"]), ("Shotgun houses", ["W:shotgun house"]), ("Dogtrot, single-pen and hall-and-parlor houses", ["W:dogtrot house", "W:Single pen and double pen architecture", "W:hall and parlor house"]),
            ("New Mexico vernacular", ["W:New Mexico vernacular"]), ("Round barns", ["W:round barn"]))
L("K12-17", ("French vernacular buildings", ["W:Briarde architecture"]))
L("K12-18", ("Cycladic buildings", ["W:Cycladic architecture", "W:κυκλαδική αρχιτεκτονική"]))
L("K12-12", ("Hórreos", ["I:hórreo"], country("Spain")))
L("K12-13", ("Trulli", ["I:trullo"], country("Italy")))
for c in ("K12-1", "K12-2", "K12-3", "K12-4", "K12-10", "K12-15", "K12-16", "K12-19", "K12-20"): L(c)
L("K13-1", ("Persian gardens", ["I:Persian garden"]))
L("K13-3", ("Chinese gardens", ["I:Chinese garden"]))
L("K13-4", ("Japanese gardens", ["I:Japanese garden", "I:Japanese strolling garden", "I:daimyō garden", "I:dry landscape garden"]))
L("K13-6", ("French formal gardens", ["I:French formal garden"]))
L("K13-7", ("English landscape gardens", ["I:English garden"]))
for c in ("K13-2", "K13-5", "K14-1", "K14-2", "K14-3", "K14-4"): L(c)
