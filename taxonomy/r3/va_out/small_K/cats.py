"""External 'View all' catalogues, axis lines and definitions for pass small_K."""
import csv, json, os, re, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "../../../..")
from config import S

A = list(csv.DictReader(open(os.path.join(ROOT, "data/interim/architecture_exemplars.csv"))))
STYLEQ = {}
for r in A:
    if r["style_label"]: STYLEQ.setdefault(r["style_label"], r["style_qid"])
for r in csv.DictReader(open(os.path.join(ROOT, "data/interim/architecture_styles.csv"))):
    STYLEQ.setdefault(r["label"], r["qid"])
BAD = set()
p = os.path.join(HERE, "checklists.out")  # optional: list of missing Wikipedia titles
if os.path.exists(p):
    for line in open(p):
        if line.startswith("MISSING"): BAD = set(eval(line[len("MISSING "):]))

def wp(title, what):
    return None if title in BAD else ["https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"), safe="(),'_-"), f"Wikipedia: {title}", what]
def unesco(q, what=None):
    return ["https://whc.unesco.org/en/list/?search=" + urllib.parse.quote(q), "UNESCO World Heritage List", what or f"World Heritage properties matching '{q}'"]
def wdq(qids, name):
    qids = [q for q in dict.fromkeys(qids) if q]
    if not qids: return None
    q = ("SELECT ?building ?buildingLabel ?countryLabel ?inception WHERE { VALUES ?style { " + " ".join("wd:" + x for x in qids) +
         " } ?building wdt:P149 ?style . OPTIONAL { ?building wdt:P17 ?country } OPTIONAL { ?building wdt:P571 ?inception } "
         "SERVICE wikibase:label { bd:serviceParam wikibase:language \"en,mul\". } } ORDER BY ?inception")
    return ["https://query.wikidata.org/#" + urllib.parse.quote(q), "Wikidata query: every building tagged with the style",
            f"live list of all Wikidata items with architectural style (P149) = {name}, with country and date"]

ARCHNET = ["https://www.archnet.org/", "Archnet", "MIT–Aga Khan open library of Islamic architecture: sites, drawings and photographs"]
IAH = ["https://www.islamicarchitecturalheritage.com/", "Islamic Architectural Heritage", "photo archive of Islamic monuments arranged by country and dynasty"]
DIA = ["https://islamicart.museumwnf.org/", "Discover Islamic Art (Museum With No Frontiers)", "virtual museum of Islamic monuments and objects, by dynasty and country"]
NRHP = ["https://www.nps.gov/subjects/nationalregister/index.htm", "US National Register of Historic Places", "official register of over 97,000 listed US buildings, sites and districts"]
SAH = ["https://sah-archipedia.org/", "SAH Archipedia", "Society of Architectural Historians' illustrated encyclopedia of US buildings"]
HE = ["https://historicengland.org.uk/listing/the-list/", "National Heritage List for England", "every listed building, scheduled monument and registered park in England"]
POP = ["https://pop.culture.gouv.fr/", "POP (Mérimée)", "French national heritage platform: every protected monument (monuments historiques)"]
ARCHINFORM = ["https://www.archinform.net/", "archINFORM", "international database of modern architecture, searchable by architect, place and keyword"]
DOCOMOMO = ["https://www.docomomo.com/", "Docomomo International", "documentation and register of Modern Movement buildings and sites"]
PLEIADES = ["https://pleiades.stoa.org/", "Pleiades", "gazetteer of ancient places and sites of the Mediterranean and Near East"]
CRSBI = ["https://www.crsbi.ac.uk/", "Corpus of Romanesque Sculpture in Britain and Ireland", "every Romanesque church site in Britain and Ireland, with photographs"]
ASI = ["https://asi.nic.in/", "Archaeological Survey of India", "centrally protected monuments of India, listed by circle"]
JPCH = ["https://bunka.nii.ac.jp/", "Cultural Heritage Online (Bunka Isan Online)", "Japan's national portal of designated cultural properties"]
JPDB = ["https://kunishitei.bunka.go.jp/", "Database of National Cultural Properties (Agency for Cultural Affairs)", "every nationally designated building, site and garden in Japan"]
KR = ["https://www.heritage.go.kr/", "Korea Heritage Service", "national register of designated heritage of Korea"]
RIJKS = ["https://monumentenregister.cultureelerfgoed.nl/", "Rijksmonumentenregister", "Dutch national register of listed monuments"]
PARKS = ["https://www.parksandgardens.org/", "Parks & Gardens UK", "database of over 10,000 historic parks and gardens in the UK"]
WHL = ["https://whc.unesco.org/en/list/", "UNESCO World Heritage List", "all inscribed World Heritage properties"]

ISL = [ARCHNET, IAH, DIA]
IND = [ASI, wp("Monuments of National Importance", "India's centrally protected monuments, with state-by-state lists")]
JAP = [JPDB, JPCH]
CHN = []
USA = [NRHP, SAH]

EXTRA = {
 "K1-1": [unesco("Umayyad")], "K1-2": [unesco("Samarra")], "K1-3": [wp("Islamic Cairo", "the historic Islamic city of Cairo, with its Fatimid and Mamluk monuments · UNESCO"), wp("List of mosques in Cairo", "every historic mosque of Cairo by period")],
 "K1-4": [unesco("Alhambra", "Alhambra, Generalife and Albayzín, Granada"), unesco("Medina")], "K1-5": [unesco("Mudejar", "Mudéjar Architecture of Aragon")],
 "K1-6": [unesco("Seljuk")], "K1-7": [unesco("Seljuk")], "K1-8": [wp("Islamic Cairo", "the historic Islamic city of Cairo, with its Mamluk monuments · UNESCO"), wp("List of mosques in Cairo", "every historic mosque of Cairo by period")],
 "K1-9": [unesco("Soltaniyeh")], "K1-10": [unesco("Samarkand"), unesco("Bukhara")], "K1-11": [unesco("Isfahan")],
 "K1-12": [wp("List of mosques in Istanbul", "the mosques of Istanbul, Ottoman and later"), unesco("Ottoman")],
 "K1-13": [unesco("Golestan")], "K1-14": IND + [unesco("Qutb")], "K1-15": IND + [unesco("Mughal")],
 "K1-16": [unesco("Djenné"), unesco("Timbuktu")], "K1-17": [unesco("Kilwa"), unesco("Lamu")],
 "K1-18": CHN + [wp("List of mosques in China", "mosques of China by province")], "K1-19": [wp("List of mosques in Indonesia", "mosques of Indonesia")],
 "K2-1": [], "K2-5": IND, "K2-15": [], "K2-16": USA + [POP], "K2-18": [HE], "K2-19": USA + [HE], "K2-20": USA, "K2-21": USA, "K2-22": USA, "K2-23": USA,
 "K2-24": USA, "K2-25": USA, "K2-33": [], "K2-34": USA, "K2-7": [HE] + USA, "K2-8": USA + [HE], "K2-11": [HE] + USA, "K2-12": [POP] + USA, "K2-13": [HE], "K2-14": USA + [HE],
 "K2-30": [], "K2-2": [wp("Bien de Interés Cultural", "Spain's national heritage register")], "K2-26": [],
 "K3-1": [PLEIADES, wp("List of Egyptian pyramids", "every known Egyptian pyramid"), unesco("Thebes")], "K3-2": [PLEIADES, unesco("Babylon")], "K3-3": [PLEIADES, unesco("Persepolis")],
 "K3-4": [PLEIADES, unesco("Hatra")], "K3-5": [PLEIADES, unesco("Sasanian")], "K3-6": [PLEIADES, unesco("Minoan")], "K3-7": [PLEIADES, unesco("Mycenae")],
 "K3-8": [PLEIADES, wp("List of ancient Greek temples", "every known ancient Greek temple, by region")], "K3-9": [PLEIADES, unesco("Etruscan")],
 "K3-10": [PLEIADES, wp("List of Roman amphitheatres", "every known Roman amphitheatre"), unesco("Roman")], "K3-11": [PLEIADES, unesco("Petra"), unesco("Hegra")],
 "K4-1": [unesco("Ravenna")], "K4-2": [unesco("Byzantine")], "K4-3": [unesco("Medieval Monuments in Kosovo")], "K4-4": [unesco("Novgorod"), unesco("Vladimir")],
 "K4-5": [unesco("Armenia")], "K4-6": [unesco("Mtskheta")], "K4-7": [unesco("Asturias"), CRSBI], "K4-8": [unesco("Carolingian")], "K4-9": [unesco("Hildesheim")],
 "K4-10": [CRSBI, POP, unesco("Romanesque")], "K4-11": [unesco("Arab-Norman")], "K4-12": [wp("Churches of Moldavia", "the eight UNESCO painted churches of northern Moldavia"), unesco("Moldavia")],
 "K5-1": [HE], "K5-2": [wp("Bien de Interés Cultural", "Spain's national heritage register")], "K5-3": [unesco("Jerónimos")], "K5-4": [unesco("Escurial")],
 "K5-5": [], "K5-6": [unesco("Würzburg"), unesco("Sanssouci")], "K5-7": [unesco("Yaroslavl")], "K5-8": [unesco("Horezu")], "K5-9": [unesco("Vicenza", "City of Vicenza and the Palladian Villas of the Veneto"), HE],
 "K5-10": [HE], "K5-11": [POP], "K5-12": USA, "K5-13": [], "K5-15": USA, "K5-16": [unesco("Mexico City"), wp("List of Spanish missions in California", "the 21 Spanish missions of Alta California")],
 "K5-17": [unesco("Potosí")], "K5-18": [unesco("Ouro Preto"), unesco("Salvador de Bahia")], "K5-19": USA, "K5-20": [RIJKS], "K5-21": [],
 "K6-1": [HE] + USA, "K6-2": USA, "K6-3": USA + [wp("List of Frank Lloyd Wright works", "every built and unbuilt work of Frank Lloyd Wright")], "K6-4": [ARCHINFORM],
 "K6-5": [ARCHINFORM], "K6-6": [ARCHINFORM], "K6-7": [wp("List of Art Deco architecture", "Art Deco buildings worldwide, by country"), ARCHINFORM],
 "K6-8": [wp("Bauhaus and its Sites in Weimar, Dessau and Bernau", "the UNESCO Bauhaus sites"), DOCOMOMO, ARCHINFORM], "K6-9": [DOCOMOMO, ARCHINFORM, wp("White City, Tel Aviv", "Tel Aviv's 4,000 International Style buildings · UNESCO")],
 "K6-10": [DOCOMOMO, ARCHINFORM], "K6-11": [ARCHINFORM], "K6-12": [RIJKS, ARCHINFORM], "K6-13": [ARCHINFORM], "K6-14": USA + [ARCHINFORM], "K6-16": [ARCHINFORM], "K6-17": [ARCHINFORM],
 "K6-18": [DOCOMOMO] + USA, "K6-19": [ARCHINFORM], "K6-20": [ARCHINFORM], "K6-23": [wp("List of brutalist structures", "Brutalist buildings worldwide, by country"), DOCOMOMO, ARCHINFORM], "K6-24": [ARCHINFORM], "K6-25": [ARCHINFORM],
 "K7-1": IND + [unesco("Khajuraho")], "K7-2": IND + [unesco("Konark")], "K7-3": IND + [unesco("Champaner")], "K7-4": IND + [unesco("Chola")], "K7-5": IND + [unesco("Hoysala")],
 "K7-6": IND + [wp("List of Hindu temples in Kerala", "Hindu temples of Kerala by district")], "K7-7": IND, "K7-8": IND + [unesco("Buddhist")], "K7-9": IND + [unesco("Caves")], "K7-10": [unesco("Sri Lanka")], "K7-11": [unesco("Kathmandu")],
 "K7-12": [wp("List of Tibetan monasteries", "Tibetan Buddhist monasteries by region"), unesco("Lhasa")], "K7-13": [unesco("Bhutan")], "K7-14": IND + [wp("Hill Forts of Rajasthan", "the six UNESCO hill forts of Rajasthan"), unesco("Maratha")],
 "K7-15": IND + [unesco("Rani-ki-Vav")], "K7-16": [wp("List of gurdwaras", "gurdwaras worldwide, by country")], "K7-17": [unesco("Mohenjo"), unesco("Dholavira")],
 "K7-18": [], "K7-19": [], "K7-20": [],
 "K8-1": CHN + [unesco("China")], "K8-2": CHN, "K8-3": CHN, "K8-4": CHN + [unesco("Tulou")], "K8-5": CHN + [unesco("Xidi")], "K8-6": CHN + [unesco("Kaiping")], "K8-7": [], "K8-8": CHN, "K8-9": CHN,
 "K8-10": JAP + [wp("List of National Treasures of Japan (shrines)", "every shrine building designated a National Treasure"), wp("List of Shinto shrines in Japan", "Shinto shrines by prefecture")],
 "K8-11": JAP + [wp("List of National Treasures of Japan (temples)", "every temple building designated a National Treasure")],
 "K8-12": JAP, "K8-13": JAP + [wp("List of National Treasures of Japan (residences)", "residences designated National Treasures")], "K8-14": JAP, "K8-15": JAP, "K8-16": JAP + [wp("List of castles in Japan", "every Japanese castle by prefecture"), wp("100 Fine Castles of Japan", "the Japan Castle Foundation's list of 100 fine castles")],
 "K8-17": JAP + [unesco("Mozu-Furuichi")], "K8-18": JAP + [unesco("Ryukyu")], "K8-19": JAP, "K8-20": [KR, wp("National Treasure (South Korea)", "South Korea's National Treasures, with the full numbered list")], "K8-21": [KR, unesco("Historic Villages of Korea")],
 "K9-1": [unesco("Angkor")], "K9-2": [unesco("Borobudur"), unesco("Prambanan")], "K9-3": [unesco("Bali")], "K9-4": [], "K9-5": [unesco("Bagan")], "K9-6": [unesco("Ayutthaya"), unesco("Sukhothai")],
 "K9-7": [unesco("Luang Prabang")], "K9-8": [unesco("My Son")], "K9-9": [unesco("Hue")], "K9-10": [], "K9-11": [], "K9-12": [unesco("Vigan")], "K9-13": [unesco("Melaka")], "K9-14": [],
 "K10-1": [unesco("Aksum")], "K10-2": [unesco("Lalibela")], "K10-3": [unesco("Fasil Ghebbi")], "K10-4": [unesco("Meroe"), unesco("Gebel Barkal")], "K10-5": [unesco("Zimbabwe")],
 "K10-6": [unesco("Ksar"), unesco("Ksour")], "K10-7": [unesco("Sukur")],
 "K11-1": [wp("List of Maya sites", "every recorded Maya archaeological site"), unesco("Maya")], "K11-2": [wp("List of Mesoamerican pyramids", "Mesoamerican pyramids by site"), unesco("Pre-Hispanic")],
 "K11-3": [wp("List of Mesoamerican pyramids", "Mesoamerican pyramids by site"), unesco("Mexico City")], "K11-4": [unesco("Qhapaq"), unesco("Machu Picchu")], "K11-5": [unesco("Peru")],
 "K11-6": USA + [unesco("Chaco"), unesco("Mesa Verde")], "K11-7": USA + [wp("List of Mississippian sites", "Mississippian mound sites by state"), unesco("Hopewell")],
 "K12-1": [], "K12-5": [unesco("Taputapuātea"), unesco("Rapa Nui")], "K12-6": [unesco("Nan Madol")], "K12-7": [wp("Churches of Chiloé", "the 16 UNESCO wooden churches of Chiloé"), unesco("Chiloé")],
 "K12-8": [HE], "K12-9": [], "K12-11": [], "K12-12": [wp("Bien de Interés Cultural", "Spain's national heritage register")], "K12-13": [unesco("Trulli"), unesco("Matera")], "K12-14": USA,
 "K12-15": [unesco("Røros"), unesco("Petäjävesi")], "K12-17": [POP], "K12-18": [], "K12-20": [],
 "K13-1": [unesco("The Persian Garden", "the nine gardens of the UNESCO 'Persian Garden' property"), ARCHNET], "K13-2": [ARCHNET, unesco("Shalamar")],
 "K13-3": [wp("Classical Gardens of Suzhou", "the nine UNESCO scholar gardens of Suzhou"), unesco("Classical Gardens of Suzhou")],
 "K13-4": JAP + [wp("Place of Scenic Beauty", "Japan's designated gardens and landscapes, with lists by prefecture"), wp("Special Place of Scenic Beauty", "the gardens and landscapes of the highest designation")], "K13-5": [unesco("Medici Villas and Gardens"), PARKS],
 "K13-6": [POP], "K13-7": [PARKS, HE],
 "K14-1": [["https://www.bonsai-nbf.org/", "National Bonsai Foundation", "collection of the National Bonsai & Penjing Museum, US National Arboretum"]],
 "K14-2": [["https://www.bonsai-nbf.org/", "National Bonsai Foundation", "includes the Chinese penjing pavilion of the US National Arboretum"]],
 "K14-3": [], "K14-4": [["https://www.ikebanahq.org/", "Ikebana International", "worldwide federation of ikebana schools and chapters"], ["https://www.ikenobo.jp/english/", "Ikenobō", "the oldest ikebana school, Kyoto"]],
}

def style_qids(code):
    q = []
    for sec in S.get(code, {}).get("secs", []):
        for s in sec[1]:
            if s.startswith("W:"): q.append(STYLEQ.get(s[2:]))
    return [x for x in q if x]

def catalogues(code, leaf):
    cats = []
    w = wdq(style_qids(code), leaf["label"])
    fam = code.split("-")[0]
    base = {"K1": ISL, "K7": [], "K8": [], "K3": [], "K13": []}.get(fam, [])
    for c in [w] + EXTRA.get(code, []) + base:
        if c and c[0] not in [x[0] for x in cats]: cats.append(c)
    if not cats or len(cats) < 2:
        cats.append(unesco(leaf["label"].replace(" Architecture", "")))
    if len(cats) < 2 and WHL[0] not in [x[0] for x in cats]: cats.append(WHL)
    return cats[:5]

AXW = {"K1": "dynasty and phase", "K2": "sub-style and region", "K3": "phase", "K4": "regional school or phase", "K5": "sub-style and region",
       "K6": "sub-style or school", "K7": "dynasty, sub-style or region", "K8": "period, sub-style or region", "K9": "kingdom or period", "K10": "site type",
       "K11": "culture and region", "K12": "type", "K13": "garden type", "K14": "type"}

def AXIS_NOTE(code, leaf, cat, kinds):
    groups = list(dict.fromkeys(k[1] for k in kinds))
    secs = [g for g in groups if g not in ("Sub-styles", "Sub-types", "Centres & workshops", "Architects", "Makers", "Collections", "Schools")]
    lead = "Sub-styles, sub-types and centres first; then " if any(g in groups for g in ("Sub-styles", "Sub-types", "Centres & workshops")) else ""
    fam = code.split("-")[0]
    if cat.get("total"):
        t = cat.get("t") or 1
        noun = "garden" if fam == "K13" else "building or site"
        rule = (f"every gathered {noun} of the tradition with a Wikipedia article or a UNESCO/national heritage listing" if t == 1 else
                f"every gathered {noun} of the tradition with at least {t} Wikipedia articles or a UNESCO listing (rule tightened from 'any article or heritage listing', which gives over 400)")
        if cat.get("wd"): rule += ", gathered from the architecture CSVs plus a Wikidata sweep of instances or parts of the type"
        rule += " (proper-named, in Latin, Greek or Cyrillic script)"
        short = [re.sub(r":.*$", "", g) for g in secs]
        short = list(dict.fromkeys(short))
        s = f"{lead}works: {rule}, in sections by {AXW.get(fam, 'sub-style')} ({'; '.join(short[:8])}{' ...' if len(short) > 8 else ''}), each in date order"
        if any(":" in g for g in secs): s += "; large sections split by region or type"
        know = [g for g in secs if not any(g == x[0] for x in cat["sections"])]
        if know: s += "; named examples absent from the gathered data added from Wikipedia"
    elif secs:
        s = f"{lead}works: the gathered data has no buildings of this tradition, so every major named example with a Wikipedia article is listed from knowledge ({'; '.join(secs)})"
    else:
        s = f"{lead.rstrip('; then ').strip() or 'Sub-types and centres'}; the gathered data has no named works of this tradition"
    if "Architects" in groups: s += "; Architects last, by birth"
    if "Makers" in groups: s += "; Makers last"
    return s[:600]

DEFN = {}
