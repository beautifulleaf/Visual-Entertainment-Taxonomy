"""Coverage audit: what gathering has produced per world region x era (visual-art-plan.md §2.2).

Reads every gathered output under data/interim/ and counts per region x era:
  traditions   distinct culture / dynasty / school / style / folk-tradition labels (folded, unioned across sources)
  objects      museum objects behind those labels (culture-level rows only, so not double-counted within a source)
  artists      selected artists (depth passes, modern, pre-1400 era selection, contemporary), unioned by QID
  makers       named makers recorded by the regional sweeps, manuscripts and architecture (not selected)
  attributed_share  share of objects with a named maker, from the object-level files (attribution profile)
  sources      distinct sources contributing

Regions come from the source's own region where it records one, else from keywords on the label
(KEYWORDS) or on the country (COUNTRY_KEYWORDS, for artists and modern states). Eras use the label's
median date: antiquity < 500, traditional 500-1859, modern 1860-1959, contemporary >= 1960. Internally
'traditional' is split at 1400 (early / late) so the attribution profile can separate medieval from
post-1400 cells. Both are approximations meant to find empty and thin cells, not to classify.

Outputs (data/interim/):
  coverage_grid.csv        region x era
  coverage_media.csv       region x medium (tradition nodes, objects, cultures, sources)
  coverage_flags.csv       every empty / thin / single-source cell of both grids, with a reason
  attribution_profile.csv  region x era (+ traditional split) profile: artist-led / tradition-led / mixed
and seeds/visual-art/attribution_profile.csv (compact copy for the classifier).
Usage:  python3 pipelines/visual_art/coverage_audit.py      (about 1 minute; reads ~1.2M object rows plus MetObjects.csv)
"""
import collections
import csv
import glob
import json
import os
import re
import statistics
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INTERIM = os.path.join(ROOT, "data", "interim")
RAW = os.path.join(ROOT, "data", "raw")
REG = os.path.join(INTERIM, "regional")
VA = os.path.join(INTERIM, "visual_art")
OUT = os.path.join(INTERIM, "coverage_grid.csv")
FLAGS_OUT = os.path.join(INTERIM, "coverage_flags.csv")
PROFILE_OUT = os.path.join(INTERIM, "attribution_profile.csv")
PROFILE_SEED = os.path.join(ROOT, "seeds", "visual-art", "attribution_profile.csv")

WE, CEE, GR = "Western Europe", "Central & Eastern Europe", "Greco-Roman & Byzantine Mediterranean"
EG, ANE, ISL = "Ancient Egypt & Nubia", "Ancient Near East", "Islamic world (MENA, Iran, Anatolia)"
CA, HIM, SA, SEA = "Central Asia & Silk Road", "Himalaya", "South Asia", "Southeast Asia"
CN, JP, KR = "China", "Japan", "Korea"
SSA, NAI, NAS = "Sub-Saharan Africa", "North America (Indigenous)", "North America (settler)"
MESO, SAM, OCE, AUS = "Mesoamerica & Caribbean", "South America", "Oceania (Pacific)", "Australia (Aboriginal)"
REGIONS = [WE, CEE, GR, EG, ANE, ISL, CA, HIM, SA, SEA, CN, JP, KR, SSA, NAI, NAS, MESO, SAM, OCE, AUS]
ERAS = ["antiquity", "traditional", "modern", "contemporary"]
FINE = ["antiquity", "early", "late", "modern", "contemporary"]   # early = 500-1399, late = 1400-1859
COARSE = {"antiquity": "antiquity", "early": "traditional", "late": "traditional",
          "modern": "modern", "contemporary": "contemporary"}

# Cells that do not exist by the grid's own definitions (historical regions, Islamic era starts 7th c.).
STRUCTURAL = {
    (EG, "modern"), (EG, "contemporary"), (ANE, "traditional"), (ANE, "modern"), (ANE, "contemporary"),
    (GR, "modern"), (GR, "contemporary"), (ISL, "antiquity"), (NAS, "antiquity"),
}
# Cells with large art-historical weight: thin below MAJOR_MIN nodes rather than THIN_MIN.
MAJOR = {
    (WE, "traditional"), (WE, "modern"), (WE, "contemporary"), (CEE, "traditional"), (CEE, "modern"),
    (GR, "antiquity"), (GR, "traditional"), (EG, "antiquity"), (ANE, "antiquity"), (ISL, "traditional"),
    (CA, "antiquity"), (CA, "traditional"), (HIM, "traditional"), (SA, "antiquity"), (SA, "traditional"),
    (SA, "modern"), (SA, "contemporary"), (SEA, "traditional"), (CN, "antiquity"), (CN, "traditional"),
    (CN, "modern"), (CN, "contemporary"), (JP, "traditional"), (JP, "modern"), (JP, "contemporary"),
    (KR, "traditional"), (KR, "contemporary"), (SSA, "traditional"), (SSA, "modern"), (SSA, "contemporary"),
    (NAI, "traditional"), (NAS, "modern"), (NAS, "contemporary"), (MESO, "antiquity"), (MESO, "traditional"),
    (SAM, "antiquity"), (SAM, "traditional"), (SAM, "modern"), (SAM, "contemporary"), (OCE, "traditional"),
    (AUS, "contemporary"),
}
THIN_MIN, MAJOR_MIN = 15, 100   # nodes = traditions + artists + makers
THIN_OBJECTS = 100              # tradition-led cell with fewer objects behind its traditions is thin evidence

# (regex on the folded label, region); first match wins. Every alternative is anchored at a word start,
# so short ethnonyms do not fire inside other words ("decorative" -> Tiv, "minimalism" -> Mali).
KEYWORDS = [
    (r"american indian|native american|first nations|plains indian|pacific northwest|northwest coast", NAI),
    (r"latin americ|ibero-?americ|hispanic americ|viceregal|novohispan|new spain|cusco|cuzco|quito|potosi|"
     r"alto peru|lima\b|bogota|santa fe de bogota|minas gerais|bahia|pernambuco", SAM),
    (r"west indi|casta painting|puebla|oaxaca|talavera poblana", MESO),
    (r"aborigin|arnhem|torres strait|yolngu|papunya|kimberley|tiwi|warlpiri|western desert|utopia|balgo|"
     r"warmun|wandjina|arrernte|pitjantjatjara|ernabella|yirrkala|maningrida|tjala|tjanpi", AUS),
    (r"egypt|coptic|nubia|meroit|kerma|napatan|ptolema|pharaon|ballana|kush", EG),
    (r"greek|attic\b|corinth|etrusc|roman\b|romans\b|roman,|roman empire|graeco|greco|hellenist|cypri|minoan|myce|"
     r"cycladic|byzant|boeotian|laconian|apulian|campanian|south italian|italic\b|villanovan|sardin|thracian|"
     r"macedon|crete|cretan|euboean|daunian|faliscan", GR),
    (r"sumer|akkad|babylon|assyria|mesopotam|elam|hittite|urart|phoenic|canaan|levant|achaemenid|parthian|"
     r"sasan|anatolia|luristan|neo-(?:assyr|babylon|hittite|elamite|sumer)|hurrian|mitanni|south arabian|"
     r"sabaean|nabat|palmyr|bactria|scythian|iran(ian)?, (ancient|bronze|iron)|proto-elamite|cappadoc|syro|"
     r"ugarit|carthag", ANE),
    (r"tibet|nepal|newar|bhutan|ladakh|himalaya|mongol|kashmir|zanabazar|menri|khyenri|gardri|sikkim|"
     r"buryat|mustang|guge|tangut|naxi", HIM),
    (r"sogd|khotan|kucha|turfan|uyghur|dunhuang|gandhar|kushan|silk road|khwarazm|central asia|kazakh|"
     r"uzbek|turkmen|kyrgyz|tajik|bukhar|samarkand|afghan|kizil|shanshan|miran\b|niya\b|loulan|swat\b|hadda", CA),
    (r"islam|ottoman|safavid|qajar|timurid|mamluk|fatimid|abbasid|umayyad|seljuq|seljuk|ilkhan|ayyubid|"
     r"nasrid|almohad|almoravid|persian|iran|turk|syria|egypt.*islam|morocc|tunis|alger|maghreb|moorish|"
     r"arab|iraq|yemen|hispano-moresque|mudejar|samanid|buyid|zangid|aghlabid|tulunid|jalayirid|injuid|"
     r"zirid|hammadid|taifa|kurd|berber|amazigh|bedouin|caucasian rug|shirvan|kazak\b|bergama|ushak", ISL),
    (r"china|chinese|han dynasty|tang\b|song dynasty|ming\b|qing\b|yuan dynasty|zhou\b|shang\b|liao\b|"
     r"jin dynasty|northern wei|six dynasties|taiwan|hong kong|jingdezhen|swatow|miao\b|dong\b|zhuang|"
     r"bai\b|yi\b|li\b|nianhua|paiwan|atayal", CN),
    (r"japan|edo\b(?!.*(benin|nigeria|peoples?))|meiji|heian|kamakura|muromachi|momoyama|jomon|yayoi|"
     r"kofun|nara period|asuka|ainu|ryukyu|okinawa|ukiyo|seto\b|satsuma|bizen|kutani|imari|mingei|otsu-e", JP),
    (r"korea|joseon|goryeo|silla|baekje|goguryeo|gaya\b|balhae", KR),
    (r"india|mughal|rajput|rajasthan|pahari|deccan|bengal|gujarat|tamil|kerala|chola|pala\b|gupta|sri lanka|"
     r"ceylon|pakistan|bangladesh|orissa|odisha|karnataka|andhra|mysore|maratha|sikh|punjab|company school|"
     r"kangra|mewar|bundi|kota\b|jaipur|basohli|mathura|vijayanagar|hoysala|maithil|madhubani|gond\b|"
     r"warli|kalighat|sinhal|kandy", SA),
    (r"thai|siam|burm|myanmar|cambod|khmer|angkor|lao\b|laos|vietnam|champa|cham\b|java|bali|sumatra|"
     r"indonesia|borneo|dayak|batak|toraja|sulawesi|malay|philippin|flores|sumba|timor|dong son|ban chiang|"
     r"pyu\b|mon\b|majapahit|tanimbar|mentawai|ngaju|peranakan|wayang|bencharong|tonkin|t'?boli|ifugao|"
     r"singapore|brunei", SEA),
    (r"maya\b|mayan|aztec|mexica|olmec|teotihuacan|zapotec|mixtec|toltec|huastec|veracruz|west mexico|colima|"
     r"jalisco|nayarit|mexic|guatemal|costa rica|panama|nicaragu|hondur|salvador|caribbean|taino|cuba|"
     r"haiti|jamaica|puerto ric|dominican|chiriqui|diquis|cocle|guanacaste|mesoameric|antill|curacao|aruba|"
     r"belize|trinidad|barbados|bahamas|martinique|guadeloupe", MESO),
    (r"inca|moche|nasca|nazca|chimu|wari\b|paracas|chavin|tiwanaku|tiahuanaco|recuay|lambayeque|sican|chancay|"
     r"peru|bolivia|ecuador|colombia|venezuel|brazil|argentin|chile|amazon|andean|quimbaya|tairona|muisca|"
     r"calima|tolima|valdivia|jama\b|manteno|guyana|surinam|paraguay|urugua|mapuche|shipibo|kayapo|wayana|"
     r"south americ", SAM),
    (r"maori|hawai|samoa|tonga|fiji|papua|new guinea|sepik|asmat|solomon|vanuatu|new caledon|kanak|"
     r"micronesia|polynes|melanesia|marquesa|tahiti|cook island|easter island|rapa nui|caroline|marshall island|"
     r"palau|chuuk|kiribati|tuvalu|admiralty|new ireland|new britain|massim|trobriand|torres|abelam|iatmul|"
     r"oceani|pacific|aotearoa|new zealand|austral islands|mangareva|niue|moriori|lapita|guam|chamorro", OCE),
    (r"yoruba|akan|asante|ashanti|baule|dogon|bamana|bambara|senufo|kuba\b|kongo|luba\b|chokwe|songye|fang\b|"
     r"punu|kota\b|igbo|benin|edo\b|ife\b|nok\b|bamileke|bamum|grassfields|cameroon|zulu|xhosa|ndebele|shona|"
     r"maasai|swahili|ethiopi|eritre|aksum|axum|fon\b|dahomey|mende|dan\b|we\b|guro\b|lobi\b|mossi|bobo\b|"
     r"bwa\b|hausa|fulani|tuareg|kenya|tanzania|uganda|congo|zaire|angola|zambia|zimbabwe|mozambique|"
     r"madagascar|malagasy|nigeria|ghana|mali\b|malian|burkina|senegal|guinea|sierra leone|liberia|"
     r"ivory coast|cote d'ivoire|gabon|sudan|somali|rwanda|burundi|malawi|botswana|namibia|south africa|"
     r"lesotho|eswatini|swazi|chad\b|niger\b|african|makonde|pende|yaka\b|lega\b|hemba|tabwa|mangbetu|azande|"
     r"teke\b|vili\b|yombe|bembe|kwele|ogoni|ijo\b|ibibio|ejagham|mumuye|jukun|chamba|tiv\b|nupe|igala|"
     r"idoma|bijago|baga\b|nalu\b|kissi|toma\b|loma\b|san\b|khoisan|kikuyu|kalenjin|karamojong|gurage|"
     r"katsina|sapi\b|tellem|mapungubwe|lydenburg|igbo-ukwu|esie|inland niger|djenne|jenne|kente|"
     r"tingatinga|cape verde|sao tome|comoros|mauritius|seychelles|djibouti|tigray|amhara", SSA),
    (r"navajo|dine\b|hopi|zuni|pueblo|apache|lakota|sioux|cheyenne|crow\b|blackfoot|cree\b|ojibwe|anishinaabe|"
     r"iroquois|haudenosaunee|mohawk|seneca|cherokee|creek\b|seminole|tlingit|haida|kwakwaka|kwakiutl|"
     r"tsimshian|nuu-chah|salish|inuit|inupiat|yupik|yup'ik|aleut|athabas|pomo\b|chumash|maidu|washoe|arapaho|"
     r"kiowa|comanche|osage|pawnee|mandan|hidatsa|arikara|shoshone|ute\b|paiute|nez perce|yakama|delaware|"
     r"lenape|wampanoag|micmac|mi'kmaq|penobscot|abenaki|huron|wendat|winnebago|ho-chunk|menominee|"
     r"potawatomi|plains\b|woodlands|great basin|subarctic|arctic|mississippian|hopewell|adena|"
     r"anasazi|ancestral pueblo|mimbres|hohokam|mogollon|indigenous north", NAI),
    (r"americ|united states|canad|new england|pennsylvan|new york|boston|philadelph|shaker", NAS),
    (r"russia|soviet|poland|polish|hungar|czech|bohemia|slovak|ukrain|belarus|lithuan|latvi|eston|romania|"
     r"moldov|moldav|bulgar|serbia|croat|sloven|bosnia|montenegr|macedonian|north macedonia|albania|kosovo|"
     r"georgia|armenia|azerbaij|finland|finnish|sami\b|karelia|transylvan|balkan|slav|cossack|tatar|bashkir|"
     r"komi\b|mari\b|yugoslav|udmurt|chuvash|mordv|siberia|yakut|sakha|evenk|nenets|khanty|chukchi|"
     r"dagestan|chechen|ossetia|circassia|abkhaz|old believer|novgorod|pskov|stroganov|palekh|khokhloma|gzhel", CEE),
    (r"french|france|british|english|scottish|irish|welsh|italian|italy|venet|floren|spanish|spain|portug|"
     r"german|austria|swiss|dutch|flemish|netherland|belgi|danish|denmark|swed|norw|iceland|europe|"
     r"medieval|gothic|romanesque|carolingian|ottonian|merovingian|anglo-saxon|celtic|viking|frankish|"
     r"visigoth|langobard|limoges|nuremberg|augsburg|meissen|sevres|delft|faience|majolica|maiolica|"
     r"insular|mozarab|sephard|ashkenaz|prussia|bavaria|saxon|holland|flanders|brabant|luxembourg|"
     r"scotland|england|wales|ireland|great britain|united kingdom|cisleithania|habsburg|holy roman|"
     r"hamburg|lubeck|holstein|weimar|wurttemberg|hanover|monaco|liechtenstein|andorra|san marino", WE),
]
KEYWORDS = [(re.compile(r"\b(?:" + p + ")"), r) for p, r in KEYWORDS]

# Modern states and their predecessors, read before KEYWORDS for artists' countries and folk countries
# (so Egypt the modern state is MENA, not Ancient Egypt; Greece and Italy are Western Europe, not Greco-Roman).
COUNTRY_KEYWORDS = [
    (r"australia", OCE),   # settler and modern artists; Aboriginal art is placed by tradition, not by country
    (r"new zealand|aotearoa", OCE),
    (r"egypt|israel|palestin|leban|jordan|kuwait|qatar|emirates|uae\b|saudi|oman\b|bahrain|libya|alger|"
     r"tunisi|morocc|iraq|syria|yemen|iran|persia|turk(?!men)|ottoman", ISL),
    (r"afghan", CA),
    (r"greece|greek|cyprus|cypriot|ital|sardinia|sicil|naples|two sicilies|papal|venice|venetian|genoa|"
     r"tuscan|malta|maltese|spain|spanish|portug", WE),
    (r"united states|usa\b|canada|confedera", NAS),
    (r"taiwan|hong kong|macau|manchukuo", CN),
]
COUNTRY_KEYWORDS = [(re.compile(r"\b(?:" + p + ")"), r) for p, r in COUNTRY_KEYWORDS]

# Met departments with a fixed region (others fall back to keywords).
MET_DEPT = {
    "Egyptian Art": EG,
    "Greek and Roman Art": GR,
    "Ancient West Asian Art": ANE,
    "Islamic Art": ISL,
    "The American Wing": NAS,
}


def fold(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s).strip()


def key_of(s):
    """Identity key for counting distinct labels/names: accents stripped and lower-cased like fold(),
    but CJK and other non-Latin letters kept (fold() would reduce 'o:長船長光' to 'o:')."""
    s = "".join(c for c in unicodedata.normalize("NFKD", s or "") if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s)).strip().lower()


def region_of(label, default=None):
    f = fold(label)
    if not f:
        return default
    for pat, reg in KEYWORDS:
        if pat.search(f):
            return reg
    return default


def country_region(label, default=None):
    f = fold(label)
    if not f:
        return default
    for pat, reg in COUNTRY_KEYWORDS:
        if pat.search(f):
            return reg
    return region_of(f, default)


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def fine_era(year):
    if year is None:
        return None
    if year < 500:
        return "antiquity"
    if year < 1400:
        return "early"
    if year < 1860:
        return "late"
    if year < 1960:
        return "modern"
    return "contemporary"


def era_of(year):
    f = fine_era(year)
    return COARSE[f] if f else None


def era_fix(reg, year, label=""):
    """Ancient-region keywords on later material: Egyptian and Near Eastern labels after 700 are the
    Islamic-era MENA region (Coptic, Nubian and Ethiopian Christian material stays), Greek after 1830 is
    Western Europe, and pre-500 'Islamic world' hits (Iran, Arabia) are the Ancient Near East."""
    if reg is None or year is None:
        return reg
    if reg == EG and year >= 700 and not re.search(r"copt|nubia|christian|ethiop|kerma|ballana", fold(label)):
        return ISL
    if reg == ANE and year >= 700:
        return ISL
    if reg == GR and year >= 1830:
        return WE
    if reg == ISL and year < 500:
        return ANE
    return reg


def mid(*vals):
    vs = [num(v) for v in vals if num(v) is not None]
    return sum(vs) / len(vs) if vs else None


def rows(path):
    if not os.path.exists(path):
        print("missing:", os.path.relpath(path, ROOT))
        return
    with open(path, encoding="utf-8") as f:
        yield from csv.DictReader(f)


def year_in(text):
    """Median year from strings like '1891-1987 (median 1963)', 'c. 1900', '1600..1950', '650-900'."""
    t = text or ""
    m = re.search(r"median (-?\d{1,4})", t)
    if m:
        return float(m.group(1))
    ys = [float(y) for y in re.findall(r"(?<![\d])-?\d{3,4}(?![\d])", t)]
    if not ys:
        return None
    return (min(ys) + max(ys)) / 2


# --- Country labels (Wikidata QIDs in the artist pools) ----------------------------------------------
def country_labels():
    lab = {}
    for f in glob.glob(os.path.join(RAW, "regional", "wikidata_*folk", "*countr*.json")):
        try:
            for d in json.load(open(f, encoding="utf-8")):
                if d.get("cl"):
                    lab.setdefault(d["c"], d["cl"])
        except (ValueError, KeyError, TypeError):
            continue
    for f in [os.path.join(RAW, "wikidata", "in_situ", "labels.json"),
              os.path.join(RAW, "wikidata", "architecture", "labels.json")]:
        if os.path.exists(f):
            for q, l in json.load(open(f, encoding="utf-8")).items():
                if isinstance(l, str):
                    lab.setdefault(q, l)
    return lab


COUNTRY_LABEL = {}


def qids(s):
    return [q.strip() for q in re.split(r"[;|,\s]+", s or "") if q.strip().startswith("Q")]


def place_artist(countries, allowed, default, antiquity=False):
    """Region from a list of country QIDs: the first one whose region is allowed, else the default."""
    found = []
    for q in qids(countries):
        lab = COUNTRY_LABEL.get(q)
        if not lab:
            continue
        reg = region_of(lab) if antiquity else country_region(lab)
        if reg:
            found.append(reg)
    for reg in found:
        if allowed is None or reg in allowed:
            return reg
    return default


# --- Grid -------------------------------------------------------------------------------------------
class Grid:
    def __init__(self):
        self.trad = collections.defaultdict(set)
        self.objects = collections.Counter()
        self.sources = collections.defaultdict(set)
        self.artists = collections.defaultdict(set)
        self.makers = collections.defaultdict(set)
        self.attr = collections.Counter()        # attributed objects
        self.attr_n = collections.Counter()      # objects with attribution information
        self.attr_src = collections.defaultdict(set)
        self.unplaced = collections.Counter()
        self.media_trad = collections.defaultdict(set)   # (region, medium) -> tradition labels

    def tradition(self, source, label, region, year, objects=0, medium=None):
        region = era_fix(region, year, label)
        fe = fine_era(year)
        if not region or not fe or not key_of(label):
            self.unplaced[source] += 1
            return
        self.trad[region, fe].add(key_of(label))
        self.objects[region, fe] += int(num(objects) or 0)
        self.sources[region, fe].add(source)
        if medium:
            self.media_trad[region, medium].add(key_of(label))

    def artist(self, source, key, region, year=None, fe=None):
        fe = fe or fine_era(year)
        if region and fe:
            self.artists[region, fe].add(key)
            self.sources[region, fe].add(source)
        else:
            self.unplaced[source] += 1

    def maker(self, source, key, region, year):
        region = era_fix(region, year)
        fe = fine_era(year)
        if region and fe:
            self.makers[region, fe].add(f"{source}:{key_of(key)}")
            self.sources[region, fe].add(source)
        else:
            self.unplaced[source] += 1

    def attribution(self, source, region, year, attributed, label=""):
        region = era_fix(region, year, label)
        fe = fine_era(year)
        if region and fe:
            self.attr_n[region, fe] += 1
            self.attr[region, fe] += 1 if attributed else 0
            self.attr_src[region, fe].add(source)

    # aggregate fine eras into a coarse era (or a list of fine eras)
    def cell(self, region, fines):
        k = [(region, f) for f in fines]
        return {
            "traditions": len(set().union(*(self.trad[x] for x in k))),
            "objects": sum(self.objects[x] for x in k),
            "artists": len(set().union(*(self.artists[x] for x in k))),
            "makers": len(set().union(*(self.makers[x] for x in k))),
            "attr": sum(self.attr[x] for x in k),
            "attr_n": sum(self.attr_n[x] for x in k),
            "sources": sorted(set().union(*(self.sources[x] for x in k))),
            "attr_sources": sorted(set().union(*(self.attr_src[x] for x in k))),
        }


FINES_OF = {e: [f for f in FINE if COARSE[f] == e] for e in ERAS}

# Medium names of node-level files (folk, gap sweep, Himalaya) -> media grid names.
NODE_MEDIUM = [
    (r"manuscript|illuminat|calligraph|book", "calligraphy & book arts"),
    (r"icon painting|painting|thangka|bark painting|scroll", "painting"),
    (r"popular print|prints?\b|paper-cut|woodblock|nianhua", "prints"),
    (r"costume|embroider|lace|textile|carpet|rug|weav|kilim|felt|batik|ikat|quilt|applique|barkcloth|tapa|"
     r"beadwork|dress|headdress", "textiles & costume"),
    (r"ceramic|pottery|porcelain|tile|faience|terracotta", "ceramics"),
    (r"glass", "glass"),
    (r"arms|armour|weapon|sword", "arms & armour"),
    (r"mask|puppet|ritual", "masks & ritual objects"),
    (r"lacquer|woodwork|furniture|woodcarving / woodwork|painting \(wood\)", "woodwork, furniture & lacquer"),
    (r"sculpt|carving|bone|stone|toys|figur", "sculpture & carving"),
    (r"metal|jewel|silver|gold|bronze|enamel", "jewellery & metalwork"),
    (r"basket|birch bark|fibre|fiber", "basketry & fibre"),
    (r"musical", "musical instruments"),
]
NODE_MEDIUM = [(re.compile(p), m) for p, m in NODE_MEDIUM]


def node_medium(text):
    f = fold(text)
    for pat, m in NODE_MEDIUM:
        if pat.search(f):
            return m
    return medium_of(text) if f else "other"


def build_grid():
    g = Grid()

    # Met (and AIC counts folded in) cultures from build_traditions.py
    for r in rows(os.path.join(INTERIM, "unattributed_cultures.csv")):
        if r["kind"] == "period":
            # Egyptian, Near Eastern and Asian material is recorded by period/dynasty, not culture
            # (New Kingdom, Ptolemaic, Edo): count the label, objects are already in the culture rows
            reg = region_of(r["label"]) or MET_DEPT.get(r["dominant_department"])
            if r["dominant_department"] in ("Egyptian Art", "Greek and Roman Art", "Ancient West Asian Art"):
                reg = MET_DEPT[r["dominant_department"]]
            g.tradition("met/aic", r["label"], reg, mid(r["begin_median"], r["end_median"]), 0)
        if r["kind"] != "culture":
            continue
        reg = MET_DEPT.get(r["dominant_department"]) or region_of(r["label"])
        if reg == EG and r["dominant_department"] == "Islamic Art":
            reg = ISL
        g.tradition("met/aic", r["label"], reg, mid(r["begin_median"], r["end_median"]), r["objects"])
    # Met object traditions (culture x classification) give media for tradition nodes
    for r in rows(os.path.join(INTERIM, "unattributed_object_traditions.csv")):
        reg = MET_DEPT.get(r["dominant_department"]) or region_of(r["culture"])
        if reg and int(num(r["objects"]) or 0) >= MIN_OBJECTS:
            g.media_trad[reg, medium_of(r["classification"], r["technique"])].add(fold(r["culture"]))

    # Regional sweeps that share the culture-row layout
    defaults = {
        "africa_traditions.csv": SSA,
        "americas_oceania_traditions.csv": None,
        "south_southeast_asia_traditions.csv": SA,
    }
    for name, default in defaults.items():
        src = name.split("_traditions")[0]
        for r in rows(os.path.join(REG, name)):
            label = r["culture"] or r["culture_group"]
            reg = region_of(label) or region_of(r["culture_group"]) or region_of(r["subregions"]) or default
            if r["kind"] == "culture":
                g.tradition(src, label, reg, num(r["mid_median"]), r["objects"])
            elif r["kind"] == "culture_type" and reg and int(num(r["objects"]) or 0) >= MIN_OBJECTS:
                g.media_trad[reg, medium_of(r["object_group"])].add(fold(label))
    for r in rows(os.path.join(REG, "africa_oceania_targeted_traditions.csv")):
        default = SSA if r["region"] == "africa" else OCE
        label = r["culture"] or r["culture_group"]
        reg = region_of(label) or region_of(r["culture_group"]) or default
        if r["kind"] == "culture":
            g.tradition("africa_oceania_targeted", label, reg, num(r["mid_median"]), r["objects"])
        elif r["kind"] == "culture_type" and int(num(r["objects"]) or 0) >= MIN_OBJECTS:
            g.media_trad[reg, medium_of(r["object_group"])].add(fold(label))

    # East Asia: country x period x object type
    ea = {"China": CN, "Japan": JP, "Korea": KR, "Taiwan": CN}
    for r in rows(os.path.join(REG, "east_asia_traditions.csv")):
        reg = ea.get(r["country"])
        label = f'{r["country"]} {r["period_en"]}'
        g.tradition("east_asia", label, reg, mid(r["period_begin"], r["period_end"]), r["all_objects"])
        if reg and int(num(r["all_objects"]) or 0) >= MIN_OBJECTS:
            g.media_trad[reg, medium_of(r["object_type"])].add(fold(label))
    period_mid = {}
    for r in rows(os.path.join(REG, "east_asia_traditions.csv")):
        period_mid.setdefault((r["country"], r["period_en"]), mid(r["period_begin"], r["period_end"]))
    for r in rows(os.path.join(REG, "east_asia_artists.csv")):
        y = num(r["birth_year"])
        y = y + 40 if y is not None else (num(r["death_year"]) - 10 if num(r["death_year"]) else None)
        if y is None:   # most makers carry only a period ("Edo", "Qing"): use its midpoint
            per = (r["periods"] or "").split(";")[0].strip()
            y = period_mid.get((r["country"], per)) or next(
                (v for (c, p), v in period_mid.items() if p == per), None)
        g.maker("east_asia", r["artist_key"], ea.get(r["country"]), y)

    # Himalaya / Central Asia (final: 71 traditions; tradition x period rows carry the dates)
    for r in rows(os.path.join(REG, "himalaya_central_asia_traditions.csv")):
        reg = HIM if r["region_group"] == "Himalaya" else CA
        if r["kind"] == "tradition_period":
            g.tradition("himalaya_central_asia", f'{r["tradition"]} {r["period"]}', reg,
                        num(r["mid_median"]), r["objects"])
        elif r["kind"] == "tradition":
            # undated periods: the tradition row itself, without objects (already in its period rows)
            g.tradition("himalaya_central_asia", r["tradition"], reg, num(r["mid_median"]), 0)
        elif r["kind"] == "tradition_period_type" and int(num(r["objects"]) or 0) >= MIN_OBJECTS:
            g.media_trad[reg, node_medium(r["medium"])].add(fold(r["tradition"]))

    # Islamic world: dynasties and schools
    for r in rows(os.path.join(REG, "islamic_dynasties.csv")):
        reg = SA if re.search(r"mughal|deccan|sultanate|bengal|gujarat", fold(r["dynasty"])) else ISL
        g.tradition("islamic", r["dynasty"], reg, num(r["mid_median"]), r["objects"])
    for r in rows(os.path.join(REG, "islamic_schools.csv")):
        reg = region_of(r["name"].replace("Company", "India"), ISL)
        if reg not in (SA, ISL, CA):
            reg = ISL
        if re.search(r"mughal|deccan|lucknow|murshidabad|salim|company|golconda|bijapur|hyderabad", fold(r["name"])):
            reg = SA
        g.tradition("islamic", r["name"], reg, num(r["mid_median"]), 0,
                    medium="calligraphy & book arts" if r["kind"] == "school" else None)
    for r in rows(os.path.join(REG, "islamic_makers.csv")):
        reg = SA if re.search(r"mughal|deccan", fold(r["dynasties"])) else ISL
        g.maker("islamic", r["maker"], reg, mid(r["date_begin_min"], r["date_end_max"]))

    # Smithsonian cultures (NMAI is Indigenous Americas; NMAA Asia)
    for r in rows(os.path.join(REG, "smithsonian_cultures.csv")):
        if r["kind"] != "culture" or r["unit"] in ("SAAM", "CHNDM", "HMSG"):
            continue
        default = {"NMAI": NAI, "NMAfA": SSA}.get(r["unit"])
        reg = region_of(r["culture"], default)
        if r["unit"] == "NMAI" and reg in (NAS, WE, None):
            reg = NAI
        g.tradition("smithsonian", r["culture"], reg, num(r["begin_median"]), r["objects"])

    # Rijksmuseum / Wereldmuseum cultures: new keys and known keys (base level carries the objects)
    wx = {"southeast_asia": SEA, "south_asia": SA, "africa": SSA, "africa_north": ISL, "west_asia_islamic": ISL,
          "oceania": OCE, "himalaya_central_asia": HIM, "east_asia": CN, "europe": WE, "americas": None}
    for r in rows(os.path.join(REG, "world_extra_cultures.csv")):
        if r["kind"] == "place":
            continue   # country buckets (Suriname, Indonesia, ...), not traditions; their objects count in the media grid
        reg = region_of(r["label"]) or country_region(r["countries"]) or wx.get(r["region"])
        if r["region"] == "americas" and reg in (None, WE, NAS) and not region_of(r["label"]):
            reg = country_region(r["countries"], SAM)
        g.tradition("rijks/wereldmuseum", r["label"], reg, num(r["mid_median"]),
                    r["objects"] if r["level"] == "base" else 0)

    # Regional makers
    for name, default in [("africa_makers.csv", SSA), ("south_southeast_asia_makers.csv", SA),
                          ("americas_oceania_makers.csv", None), ("africa_oceania_targeted_makers.csv", None),
                          ("himalaya_central_asia_makers.csv", HIM)]:
        for r in rows(os.path.join(REG, name)):
            label = " ".join(r.get(k, "") or "" for k in ("traditions", "tradition", "culture", "places", "regions"))
            g.maker("regional_makers", r["maker"], region_of(label, default),
                    mid(r.get("date_begin_min"), r.get("date_end_max")))

    # European folk and vernacular traditions. Undated or Wikidata-only nodes count as traditional;
    # nodes dated by their museum objects keep that date (folk objects are mostly 1850-1950).
    efr = {"Western Europe": WE, "Southern Europe": WE, "Nordic": WE, "British Isles": WE, "Central Europe": WE,
           "Eastern Europe": CEE, "Balkans": CEE, "Baltic": CEE, "Caucasus": CEE, "Caucasus (Russia)": CEE,
           "Russia: Siberia (Asian)": CEE, "Russia: Volga-Ural": CEE, "Russia: North": CEE,
           "Europe (pan-regional)": WE}
    EFOLK_REGION.clear()
    for r in rows(os.path.join(REG, "europe_folk_traditions.csv")):
        first = (r["region"] or "").split(";")[0].strip()
        reg = country_region(r["country"].split(";")[0]) if r["country"] else None
        if reg not in (WE, CEE):
            reg = efr.get(first) or region_of(r["label"]) or (WE if not r["country"] else None)
        if reg in (GR,):
            reg = WE
        y = year_in(r["period"]) if r["kind"] != "wikidata" else None
        if y is None or y < 500:
            y = 1700.0
        med = node_medium(r["medium"])
        EFOLK_REGION[r["node_key"]] = (reg, med)
        g.tradition("europe_folk", r["label"], reg, y, r["total_objects"], medium=med)

    # World folk (non-European), excluding alias rows (they duplicate an existing cell)
    wfr = {"East Asia": CN, "MENA / Central Asia": ISL, "Oceania": OCE, "Southeast Asia": SEA,
           "North America": NAI, "South Asia": SA, "Africa": SSA, "South America": SAM,
           "Mexico / Central America & Caribbean": MESO, "Asia (other)": CA}
    WFOLK_REGION.clear()
    for r in rows(os.path.join(REG, "world_folk_traditions.csv")):
        first = (r["region"] or "").split(";")[0].strip()
        reg = region_of(r["label"]) or region_of(r["people"]) or country_region((r["country"] or "").split(";")[0]) \
            or wfr.get(first)
        if reg in (WE, CEE, GR, EG, ANE) and wfr.get(first):
            reg = wfr[first]   # ancient/European keyword hits inside a non-European folk row
        y = mid(r.get("date_begin_min"), r.get("date_begin_max")) or year_in(r.get("period"))
        if y is None or y < 500:
            y = 1700.0
        med = node_medium(r["medium"])
        WFOLK_REGION[r["node_key"]] = (reg, med)
        if r["status"] == "alias-of-existing-cell":
            continue
        g.tradition("world_folk", r["label"], reg, y, r.get("total_objects_distinct") or 0, medium=med)

    # Gap sweep (colonial Latin America, SE Asia, East Asian folk, Aboriginal Australia, ancient Africa)
    gsr = {"Southeast Asia": SEA, "Australia (Aboriginal and Torres Strait Islander)": AUS,
           "Africa (ancient and early)": SSA, "Latin America (colonial)": SAM, "Latin America": SAM, "East Asia": CN}
    GAP_REGION.clear()
    for r in rows(os.path.join(REG, "gap_sweep_traditions.csv")):
        default = gsr.get(r["region"])
        reg = region_of(r["label"]) or region_of(r["qid_label"]) or default
        if default == AUS:
            reg = AUS
        elif default == SEA and reg not in (SEA,):
            reg = SEA
        elif default == CN and reg not in (CN, JP, KR):
            reg = CN
        elif default == SSA and reg not in (SSA, EG):
            reg = SSA
        elif default == SAM and reg not in (SAM, MESO):
            reg = SAM
        y = num(r["mid_median"]) or year_in(r["era_nominal"]) or 1750.0
        med = node_medium(r["medium"])
        GAP_REGION[r["key"]] = (reg, med)
        g.tradition("gap_sweep", r["label"], reg, y, r["objects"], medium=med)
        for name in (r["top_named_makers"] or "").split(";"):
            name = re.sub(r"\s*\(\d+\)$", "", name).strip()
            if name and not PLACEHOLDER.search(name):
                g.maker("gap_sweep", name, era_fix(reg, y), y)

    # Manuscript illumination traditions and illuminators
    mr = {"Western Europe": WE, "C&E Europe incl. Armenia/Georgia": CEE, "South Asia": SA, "SE Asia": SEA,
          "Mesoamerica": MESO, "Islamic world": ISL, "Byzantine": GR, "Ethiopia/Sub-Saharan Africa": SSA,
          "Japan": JP, "Egypt/Coptic": EG, "South America": SAM, "Central Asia": CA, "Himalaya": HIM,
          "Korea": KR, "China": CN}
    for r in rows(os.path.join(INTERIM, "manuscripts_traditions.csv")):
        y = year_in(r["era_items_p5_p95"]) or year_in(r["era_rule"])
        reg = mr.get(r["region"])
        if r["region"] == "Near East/Syriac":
            reg = ANE if (y or 1000) < 500 else ISL
        if not reg:
            reg = region_of(r["label"])
        if r["kind"] == "genre" and not y:
            continue   # cross-regional genre nodes (Books of Hours, ...) have no single cell
        g.tradition("manuscripts", r["label"], reg, y, r["n_manuscripts"], medium="calligraphy & book arts")
    for r in rows(os.path.join(INTERIM, "manuscripts_illuminators.csv")):
        reg = mr.get(r["region"]) or (ISL if r["region"] == "Near East/Syriac" else region_of(r["citizenship"]))
        g.maker("manuscripts", r["qid"] or r["label"], reg, num(r["floruit_est"]))

    # Art in place (rock art, murals, mosaics, geoglyphs, body art). Unmapped Wikidata items are noise.
    ir = {"Western Europe": WE, "C&E Europe": CEE, "South America": SAM, "Greco-Roman/Byzantine": GR,
          "South Asia": SA, "N. America Indigenous": NAI, "Near East": ANE, "Islamic world": ISL,
          "Mesoamerica": MESO, "SE Asia": SEA, "Oceania": OCE, "China": CN, "North America (settler/modern)": NAS,
          "Aboriginal Australia": AUS, "Central Asia": CA, "Japan": JP, "Sub-Saharan Africa": SSA, "Korea": KR,
          "Egypt & Nubia": EG, "Himalaya": HIM, "North Africa & Sahara": SSA, "Caribbean": MESO}
    INSITU_SITES.clear()
    for r in rows(os.path.join(INTERIM, "in_situ_traditions.csv")):
        if r["node_source"].startswith("wikidata item") or r["node_source"].startswith("unassigned"):
            continue
        reg = ir.get(r["region"]) or region_of(r["label"]) or country_region(re.sub(r"\(\d+\)", "", r["country"]))
        y = mid(r["year_min"], r["year_max"]) or year_in(r["era"])
        if y is None:
            # prehistoric rock art and geoglyphs are antiquity; undated murals/mosaics default to traditional
            y = 0.0 if r["kind"] in ("rock art", "geoglyph") else 1200.0
        g.tradition("in_situ", r["label"], reg, y, 0, medium="art in place")
        if reg:
            INSITU_SITES[reg] += int(num(r["n_sites"]) or 0)

    # Architecture: styles passing the §2.3 cutoff, plus the non-Western pass
    for r in rows(os.path.join(INTERIM, "architecture_styles.csv")):
        if not ((num(r["sitelinks"]) or 0) >= 5 or (num(r["n_heritage"]) or 0) >= 3 or (num(r["n_unesco"]) or 0) >= 1):
            continue
        top = (r["buildings_top_countries"] or "").split("|")[0]
        reg = region_of(r["label"]) or country_region(r["country_explicit_label"]) \
            or country_region(re.sub(r"\s*\(\d+\)", "", top))
        if not reg:
            reg = {"Europe": WE, "North America": NAS, "South America": SAM, "Africa": SSA,
                   "Oceania": OCE}.get(r["region"])
        y = mid(r["period_start"], r["period_end"]) or num(r["buildings_inception_median"]) \
            or (num(r["century"]) * 100 - 50 if num(r["century"]) else None)
        g.tradition("architecture", r["label"], reg, y, 0, medium="architecture")
        if reg:
            ARCH_BUILDINGS[reg] += int(num(r["n_buildings"]) or 0)
    fam = {"dravidian": SA, "nagara": SA, "vesara": SA, "indo_islamic": SA, "bengal": SA, "sri_lankan": SA,
           "early_buddhist": SA, "gandharan": CA, "central_asian": CA, "andean": SAM, "maya": MESO,
           "mesoamerican": MESO, "chinese": CN, "japanese": JP, "korean": KR, "persian": ISL, "arab_islamic": ISL,
           "maghreb": ISL, "ottoman": ISL, "ethiopian": SSA, "sahel": SSA, "javanese": SEA, "khmer": SEA,
           "thai": SEA, "burmese": SEA, "balinese": SEA, "cham": SEA, "tibetan": HIM, "oceania": OCE,
           "eastern_woodlands": NAI}
    ex_year = collections.defaultdict(list)
    ex_n = collections.Counter()
    for r in rows(os.path.join(INTERIM, "architecture_nonwestern_exemplars.csv")):
        if r["proposed_style"]:
            ex_n[r["proposed_style"]] += 1
            if num(r["inception"]) is not None:
                ex_year[r["proposed_style"]].append(num(r["inception"]))
    for r in rows(os.path.join(INTERIM, "architecture_nonwestern_styles.csv")):
        reg = fam.get(r["family"]) or region_of(r["proposed_style"]) or region_of(r["family"].replace("_", " "))
        ys = ex_year.get(r["proposed_style"])
        y = statistics.median(ys) if ys else 1200.0
        g.tradition("architecture_nonwestern", r["proposed_style"], reg, y, 0, medium="architecture")
        if reg:
            ARCH_BUILDINGS[reg] += ex_n[r["proposed_style"]]
    for r in rows(os.path.join(INTERIM, "architecture_architects.csv")):
        b = num(r["birth"])
        g.maker("architects", r["qid"], country_region(r["citizenship"].split("|")[0]), b + 40 if b else None)

    # --- Selected artists, unioned by QID per cell ---
    europe = {WE, CEE}
    # Europe 1400-1900 (selected): Europe and its colonies, so any region; era by birth + 40
    pool = {r["qid"]: r["countries"] for r in rows(os.path.join(VA, "pool_europe_1400-1900.csv"))}
    for r in rows(os.path.join(VA, "scores_europe_1400-1900.csv")):
        if r["selected"] in ("1", "True"):
            b = num(r["birth"])
            g.artist("depth_europe", r["qid"], place_artist(pool.get(r["qid"]), None, WE), b + 40 if b else None)
    # Modern 1860-1960 (selected, final 17,706): split into the grid's regions by country
    modern = {
        "europe": (europe, WE), "north_america": ({NAS, NAI}, NAS), "latin_america": ({MESO, SAM}, SAM),
        "east_asia": ({CN, JP, KR, HIM}, CN), "south_asia": ({SA, HIM}, SA), "southeast_asia": ({SEA}, SEA),
        "mena_central_asia": ({ISL, CA, CEE}, ISL), "subsaharan_africa": ({SSA}, SSA), "oceania": ({OCE, AUS}, OCE),
    }
    for path in sorted(glob.glob(os.path.join(VA, "scores_modern_*.csv"))):
        key = os.path.basename(path)[len("scores_modern_"):-4]
        allowed, default = modern[key]
        pool = {r["qid"]: r["countries"] for r in rows(os.path.join(VA, f"pool_modern_{key}.csv"))}
        for r in rows(path):
            if r["selected"] in ("1", "True"):
                g.artist("depth_modern", r["qid"], place_artist(pool.get(r["qid"]), allowed, default), fe="modern")
    # Pre-1400 era selection ('final')
    pre = {"antiquity_mediterranean": ({GR, EG, ANE}, GR, True), "europe_medieval_500-1400": ({WE, CEE, GR}, WE, True),
           "east_asia_pre1400": ({CN, JP, KR}, CN, False), "islamic_pre1400": ({ISL, CA, SA}, ISL, True)}
    for key, (allowed, default, anti) in pre.items():
        pool = {r["qid"]: r["countries"] for r in rows(os.path.join(VA, f"pool_{key}.csv"))}
        for r in rows(os.path.join(VA, f"scores_{key}_era.csv")):
            if r["final"] not in ("1", "True"):
                continue
            b = num(r["birth"])
            y = b + 40 if b is not None else year_in(r["cell"])
            if key == "islamic_pre1400" and (y is None or y < 650):
                y = 900.0
            g.artist("pre1400", r["qid"], place_artist(pool.get(r["qid"]), allowed, default, antiquity=anti), y)
    # Contemporary (selected, 11,125 incl. list-only)
    cpool = {}
    for name in ("contemporary_pool.csv", "contemporary_pool_additions.csv"):
        for r in rows(os.path.join(INTERIM, name)):
            cpool.setdefault(r["qid"], r["countries"])
    clist = {}
    for r in rows(os.path.join(INTERIM, "contemporary_list_artists.csv")):
        clist.setdefault("list:" + r["norm_name"], r["country"])
    contemp = {
        "Europe": (europe, WE), "North America": ({NAS, NAI}, NAS), "Latin America and Caribbean": ({MESO, SAM}, SAM),
        "East Asia": ({CN, JP, KR, HIM}, CN), "Middle East and North Africa": ({ISL, CA, CEE}, ISL),
        "Sub-Saharan Africa": ({SSA}, SSA), "Oceania": ({OCE, AUS}, OCE), "South Asia": ({SA, HIM}, SA),
        "Southeast Asia": ({SEA}, SEA), "Central Asia": ({CA, HIM}, CA),
        "Asia (other)": ({CN, JP, KR, SA, SEA, CA, HIM, ISL}, None), "Unknown": (None, None),
    }
    for r in rows(os.path.join(INTERIM, "contemporary_scores.csv")):
        if r["selected"] != "1":
            continue
        allowed, default = contemp.get(r["region"], (None, None))
        if r["qid"]:
            reg = place_artist(cpool.get(r["qid"]), allowed, default)
        else:
            reg = country_region(clist.get(r["key"], ""), default)
        g.artist("contemporary", r["qid"] or r["key"], reg, fe="contemporary")
    return g


EFOLK_REGION, WFOLK_REGION, GAP_REGION = {}, {}, {}
INSITU_SITES, ARCH_BUILDINGS = collections.Counter(), collections.Counter()


# --- Region x medium -------------------------------------------------------
# The same region can look covered on the strength of one medium (painting) while
# its textiles or ceramics are absent; this grid counts, per region x medium, the
# objects, the distinct culture labels (>= MIN_OBJECTS objects in that medium) and the
# tradition nodes whose own medium (or culture x object-type row) is that medium.
# The same object pass measures the attributed share per region x era.
MEDIA_OUT = os.path.join(INTERIM, "coverage_media.csv")
MIN_OBJECTS = 3
MEDIA = [
    ("photography", r"photograph|negative|daguerreotype|albumen|gelatin silver"),
    ("calligraphy & book arts", r"calligraph|manuscript|codex|codices|qur.?an|album|illuminat|book|folio|page\b|"
                                r"scroll|sutra|document|letter|rubbing|miniature"),
    ("prints", r"\bprint|woodblock|woodcut|etching|engraving|lithograph|ukiyo|poster|stencil"),
    ("drawing", r"drawing|sketch|cartoon|works on paper"),
    ("painting", r"painting|thangka|tangka|fresco|mural|icon\b|bark painting|hanging scroll|handscroll|screen|fan\b|fans"),
    ("textiles & costume", r"textile|carpet|rug\b|kilim|embroider|lace|woven|weav|silk|linen|cotton|wool|tapestr|"
                           r"costume|dress|garment|robe|shawl|sash|belt|hat\b|headdress|cap\b|shoe|moccasin|footwear|"
                           r"bag\b|bags|beadwork|quillwork|kimono|sari|cloth|cushion|cover\b|trouser|batik|ikat|kente|"
                           r"feather|fabric|sampler|quilt|accessor"),
    ("ceramics", r"ceramic|porcelain|pottery|stoneware|earthenware|terracotta|terra cotta|faience|majolica|maiolica|"
                 r"vase|vases|tile|bowl|dish|plate|jar|jug|ewer|cup\b|vessel|potsherd|clay|kiln|celadon|sherd"),
    ("glass", r"\bglass|enamel"),
    ("arms & armour", r"arms|armou?r|sword|dagger|helmet|firearm|shield|spear|weapon|blade|bow\b|arrow|archery|"
                      r"shafted|equestrian|tsuba|sword furniture"),
    ("masks & ritual objects", r"\bmask|ritual|reliquar|shrine|altar|fetish|power figure|ceremonial|regalia|"
                               r"staff|amulet|charm"),
    ("mosaics & architectural decoration", r"mosaic|architectural|ornament & architecture|capital\b|column|stucco|corbel|lintel"),
    ("sculpture & carving", r"sculpt|statue|figure|figurine|relief|carving|carved|bust\b|netsuke|ivor|jade|stone|"
                            r"effigy|idol|head\b|totem|stela|stele"),
    ("jewellery & metalwork", r"jewel|ornament|necklace|earring|bracelet|pendant|bead|ring\b|gorget|brooch|"
                              r"metal|bronze|gold|silver|copper|brass|iron|medal|plaquette|coin|seal\b|lamp"),
    ("woodwork, furniture & lacquer", r"wood|furniture|chair|stool|chest|cabinet|table|lacquer|inro|box\b|panel|"
                                      r"door|frame|headrest"),
    ("basketry & fibre", r"basket|fibre|fiber|mat\b|matting|raffia|bark\b|barkcloth|tapa"),
    ("musical instruments", r"musical|instrument|drum|aerophone|chordophone|idiophone|membranophone|flute|whistle|"
                            r"lute|harp"),
    ("tools & everyday", r"tool|implement|utensil|spoon|pipe|pestle|scraper|axe|celt\b|projectile|net\b|fishing"),
]
MEDIA = [(m, re.compile(p)) for m, p in MEDIA]
# 'architecture' and 'art in place' come from the node-level passes (styles, in-situ traditions);
# their objects are buildings and sites, not museum objects.
MEDIA_NAMES = [m for m, _ in MEDIA] + ["architecture", "art in place", "other"]
MEDIA_STRUCTURAL = {(EG, "photography"), (ANE, "photography"), (GR, "photography"),
                    (EG, "prints"), (ANE, "prints"), (GR, "prints"), (NAI, "prints")}

MET_DEPT_REGION = dict(MET_DEPT, **{
    "European Paintings": WE, "European Sculpture and Decorative Arts": WE,
    "Medieval Art": WE, "The Cloisters": WE, "Robert Lehman Collection": WE,
})

# Generic maker placeholders count as unattributed (same rule as pipelines/unattributed/build_traditions.py).
PLACEHOLDER = re.compile(r"(?i)^(unknown|unidentified|anonymous)\b|\bartists?(\s*\(s\))?$|^artists? of\b"
                         r"|\b(guild|caste)\b")


def met_attributed(name):
    first = (name or "").split("|")[0].strip()
    return bool(first) and not PLACEHOLDER.search(first)


def medium_of(*texts):
    f = fold(" | ".join(t for t in texts if t))
    for m, pat in MEDIA:
        if pat.search(f):
            return m
    return "other"


class MediaGrid:
    def __init__(self):
        self.objects = collections.Counter()
        self.cultures = collections.defaultdict(collections.Counter)
        self.sources = collections.defaultdict(set)

    def add(self, source, region, medium, culture, n=1):
        if not region:
            return
        k = (region, medium)
        self.objects[k] += n
        self.cultures[k][fold(culture) or "(unlabelled)"] += n
        self.sources[k].add(source)


def object_pass(g):
    csv.field_size_limit(1 << 30)
    m = MediaGrid()

    met = os.path.join(RAW, "museums", "MetObjects.csv")
    with open(met, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            dept = r["Department"]
            if dept in ("Modern and Contemporary Art", "Photographs", "The Libraries", "Drawings and Prints") and not r["Culture"]:
                # Artist-led departments: medium coverage there comes from the artist passes.
                continue
            label = r["Culture"] or r["Country"] or r["Artist Nationality"]
            reg = region_of(label) or MET_DEPT_REGION.get(dept)
            if reg == EG and dept == "Islamic Art":
                reg = ISL
            med = medium_of(r["Classification"], r["Object Name"], r["Medium"])
            m.add("met", reg, med, r["Culture"] or r["Country"])
            g.attribution("met", reg, mid(r["Object Begin Date"], r["Object End Date"]), met_attributed(r["Artist Display Name"]),
                          label)

    sweeps = {
        "africa_objects.csv": SSA, "americas_oceania_objects.csv": None,
        "south_southeast_asia_objects.csv": SA, "africa_oceania_targeted_objects.csv": None,
    }
    for name, default in sweeps.items():
        src = name.split("_objects")[0]
        for r in rows(os.path.join(REG, name)):
            label = r["culture"] or r["culture_group"] or r["place"]
            dflt = default
            if dflt is None:
                dflt = OCE if "oceania" in fold(r["subregion"] + r["region"]) and "americ" not in fold(r["subregion"]) \
                    else (SSA if "africa" in fold(r["region"]) else None)
            reg = region_of(label) or region_of(r["subregion"]) or dflt
            med = medium_of(r["object_group"], r["object_type"], r["materials"])
            m.add(src, reg, med, label)
            g.attribution(src, reg, mid(r["date_begin"], r["date_end"]), r["attributed"] == "1", label)

    ea = {"China": CN, "Japan": JP, "Korea": KR, "Taiwan": CN}
    for r in rows(os.path.join(REG, "east_asia_objects.csv")):
        ot = r["object_type"]
        if ot in ("archaeology", "documents and historical materials", "other"):
            ot = r["object_subtype"] or ot
        reg = ea.get(r["country"])
        m.add("east_asia", reg, medium_of(ot, r["title_en"]), r["period_en"])
        g.attribution("east_asia", reg, mid(r["date_begin"], r["date_end"]), r["attribution"] != "unattributed")

    for r in rows(os.path.join(REG, "himalaya_central_asia_objects.csv")):
        reg = HIM if r["region_group"] == "Himalaya" else CA
        m.add("himalaya_central_asia", reg, medium_of(r["medium"], r["object_type"]), r["tradition"])
        g.attribution("himalaya_central_asia", reg, mid(r["date_begin"], r["date_end"]), r["attributed"] == "1")

    for r in rows(os.path.join(REG, "islamic_objects.csv")):
        reg = SA if re.search(r"mughal|deccan", fold(r["dynasty"])) else ISL
        med = "calligraphy & book arts" if r["book_arts"] in ("1", "True", "yes") and "painting" not in fold(r["object_type"]) \
            else medium_of(r["object_type"], r["materials_technique"])
        m.add("islamic", reg, med, r["dynasty"] or r["culture_place"])
        g.attribution("islamic", reg, mid(r["date_begin"], r["date_end"]), r["attributed"] == "1")

    for r in rows(os.path.join(REG, "smithsonian_objects.csv")):
        if r["unit"] in ("HMSG", "CHNDM"):
            continue
        if r["unit"] == "SAAM":
            # American art: no culture field, but it measures attribution for the settler cells
            g.attribution("smithsonian", NAS, mid(r["begin_year"], r["end_year"]), (num(r["n_makers_named"]) or 0) > 0)
            continue
        default = {"NMAI": NAI, "NMAfA": SSA}.get(r["unit"])
        label = r["culture"] or r["countries"]
        reg = region_of(label, default)
        if r["unit"] == "NMAI" and reg in (NAS, WE, None):
            reg = NAI
        m.add("smithsonian", reg, medium_of(r["object_type_indexed"], r["object_type"], r["object_name"], r["medium"]), label)
        g.attribution("smithsonian", reg, mid(r["begin_year"], r["end_year"]), (num(r["n_makers_named"]) or 0) > 0)

    wx = {"southeast_asia": SEA, "south_asia": SA, "africa": SSA, "africa_north": ISL, "west_asia_islamic": ISL,
          "oceania": OCE, "himalaya_central_asia": HIM, "east_asia": CN, "europe": WE, "americas": SAM}
    for r in rows(os.path.join(REG, "world_extra_objects.csv")):
        reg = region_of(r["culture_label"]) or country_region(r["country"]) or wx.get(r["region"])
        src = "rijks/wereldmuseum"
        m.add(src, reg, medium_of(r["object_group"] if r["object_group"] != "other" else "", r["object_type"], r["materials"]),
              r["culture_label"] or r["country"])
        g.attribution(src, reg, mid(r["date_begin"], r["date_end"]), r["attributed"] == "1", r["culture_label"])

    for r in rows(os.path.join(REG, "gap_sweep_objects.csv")):
        reg, _ = GAP_REGION.get(r["node"], (None, None))
        m.add("gap_sweep", reg, medium_of(r["object_group"], r["title"]), r["node_label"])
        g.attribution("gap_sweep", reg, mid(r["date_begin"], r["date_end"]), r["attributed"] == "1")

    for name, regmap, src in [("europe_folk_objects.csv", EFOLK_REGION, "europe_folk"),
                              ("world_folk_objects.csv", WFOLK_REGION, "world_folk")]:
        for r in rows(os.path.join(REG, name)):
            reg, med = regmap.get(r["node_key"], (None, None))
            m.add(src, reg, med or node_medium(r["medium"]), r.get("node_label") or r["node_key"])

    for reg, n in INSITU_SITES.items():
        m.add("in_situ", reg, "art in place", "", n)
    for reg, n in ARCH_BUILDINGS.items():
        m.add("architecture", reg, "architecture", "", n)

    with open(MEDIA_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["region", "medium", "traditions", "objects", "cultures", "n_sources", "sources", "top_cultures"])
        for reg in REGIONS:
            for med in MEDIA_NAMES:
                k = (reg, med)
                cult = {c: n for c, n in m.cultures[k].items() if n >= MIN_OBJECTS and c != "(unlabelled)"}
                top = "; ".join(f"{c} ({n})" for c, n in sorted(cult.items(), key=lambda x: -x[1])[:8])
                w.writerow([reg, med, len(g.media_trad[k]), m.objects[k], len(cult), len(m.sources[k]),
                            "; ".join(sorted(m.sources[k])), top])
    print(f"wrote {MEDIA_OUT}")
    return m


# --- Attribution profile ----------------------------------------------------
MIN_ATTR_OBJECTS = 200   # below this, the attributed share is not used


def profile_of(share, n_trad, n_named):
    """Rule (visual-art-plan.md §2.1 step 4): the measured attributed share decides; the node balance
    decides when the share is in the middle band or not measured."""
    if share is not None and share < 0.15:
        return "tradition-led", f"attributed share {share:.0%} < 15%"
    if share is not None and share > 0.50:
        return "artist-led", f"attributed share {share:.0%} > 50%"
    lead = f"attributed share {share:.0%} in 15-50%; " if share is not None else "attributed share not measured; "
    if n_trad == 0 and n_named == 0:
        return "n/a", lead + "no nodes"
    if n_trad >= 3 * n_named:
        return "tradition-led", lead + f"traditions {n_trad} >= 3x named artists {n_named}"
    if n_named >= 3 * n_trad:
        return "artist-led", lead + f"named artists {n_named} >= 3x traditions {n_trad}"
    return "mixed", lead + f"traditions {n_trad} vs named artists {n_named} within 3x"


def write_outputs(g, m):
    grid_rows, flags, prof = [], [], []
    for reg in REGIONS:
        for era in ERAS:
            c = g.cell(reg, FINES_OF[era])
            share = c["attr"] / c["attr_n"] if c["attr_n"] >= MIN_ATTR_OBJECTS else None
            grid_rows.append([reg, era, c["traditions"], c["objects"], c["artists"], c["makers"],
                              f"{share:.3f}" if share is not None else "", c["attr_n"],
                              len(c["sources"]), "; ".join(c["sources"])])
            # flags
            nodes = c["traditions"] + c["artists"] + c["makers"]
            k = (reg, era)
            if k in STRUCTURAL:
                if nodes == 0:
                    flags.append(["era", reg, era, "n/a", "structural: cell outside the region's definition", nodes, 0, ""])
                continue
            need = MAJOR_MIN if k in MAJOR else THIN_MIN
            src = "; ".join(c["sources"])
            if nodes == 0:
                flags.append(["era", reg, era, "empty", "no traditions, artists or makers", 0, 0, ""])
                continue
            if nodes < need:
                flags.append(["era", reg, era, "thin",
                              f"{nodes} nodes (traditions {c['traditions']}, artists {c['artists']}, makers {c['makers']}) "
                              f"< {need}{' for a major cell' if k in MAJOR else ''}", nodes, len(c["sources"]), src])
            elif c["traditions"] and c["artists"] + c["makers"] < c["traditions"] and c["objects"] < THIN_OBJECTS \
                    and (share is None or share < 0.5):
                flags.append(["era", reg, era, "thin-evidence",
                              f"tradition-led cell with only {c['objects']} museum objects behind {c['traditions']} traditions",
                              nodes, len(c["sources"]), src])
            if len(c["sources"]) == 1:
                flags.append(["era", reg, era, "single-source",
                              f"all {nodes} nodes from {c['sources'][0]}" + (" (Met alone)" if c["sources"][0] == "met/aic" else ""),
                              nodes, 1, src])
    # profile: coarse eras, plus traditional split at 1400
    prof_eras = [("antiquity", ["antiquity"]), ("traditional", ["early", "late"]),
                 ("traditional:500-1399", ["early"]), ("traditional:1400-1859", ["late"]),
                 ("modern", ["modern"]), ("contemporary", ["contemporary"])]
    for reg in REGIONS:
        for era, fines in prof_eras:
            c = g.cell(reg, fines)
            share = c["attr"] / c["attr_n"] if c["attr_n"] >= MIN_ATTR_OBJECTS else None
            named = c["artists"] + c["makers"]
            coarse = era.split(":")[0]
            if (reg, coarse) in STRUCTURAL and c["traditions"] + named < THIN_MIN:
                p, basis = "n/a", "structural: cell outside the region's definition"
            else:
                p, basis = profile_of(share, c["traditions"], named)
            prof.append({"region": reg, "era": era, "profile": p,
                         "attributed_share": f"{share:.3f}" if share is not None else "",
                         "attributed_objects": c["attr"], "objects_with_attribution": c["attr_n"],
                         "attribution_sources": "; ".join(c["attr_sources"]),
                         "n_traditions": c["traditions"], "n_artists_selected": c["artists"], "n_makers": c["makers"],
                         "n_artists": named, "rule_basis": basis})

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["region", "era", "traditions", "objects", "artists", "makers", "attributed_share",
                    "objects_with_attribution", "n_sources", "sources"])
        w.writerows(grid_rows)
    print(f"wrote {OUT}")

    # media flags
    for reg in REGIONS:
        for med in MEDIA_NAMES:
            if med == "other":
                continue
            k = (reg, med)
            ob, tr, ns = m.objects[k], len(g.media_trad[k]), len(m.sources[k])
            src = "; ".join(sorted(m.sources[k]))
            if k in MEDIA_STRUCTURAL:
                continue
            if ob == 0 and tr == 0:
                flags.append(["medium", reg, med, "empty", "no objects and no tradition nodes in this medium", 0, 0, ""])
            elif tr < 3 and ob < 50:
                flags.append(["medium", reg, med, "thin", f"{tr} tradition nodes, {ob} objects", tr, ns, src])
            elif ns == 1 and tr < 3:
                flags.append(["medium", reg, med, "single-source", f"{ob} objects all from {src}, {tr} tradition nodes", tr, 1, src])
    with open(FLAGS_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["grid", "region", "cell", "flag", "reason", "nodes", "n_sources", "sources"])
        w.writerows(flags)
    print(f"wrote {FLAGS_OUT}: {collections.Counter((x[0], x[3]) for x in flags)}")

    cols = ["region", "era", "profile", "attributed_share", "attributed_objects", "objects_with_attribution",
            "attribution_sources", "n_traditions", "n_artists_selected", "n_makers", "n_artists", "rule_basis"]
    with open(PROFILE_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(prof)
    os.makedirs(os.path.dirname(PROFILE_SEED), exist_ok=True)
    with open(PROFILE_SEED, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["region", "era", "profile", "attributed_share", "n_traditions", "n_artists", "rule_basis"])
        for p in prof:
            w.writerow([p["region"], p["era"], p["profile"], p["attributed_share"], p["n_traditions"],
                        p["n_artists"], p["rule_basis"]])
    print(f"wrote {PROFILE_OUT} and {os.path.relpath(PROFILE_SEED, ROOT)}: "
          f"{collections.Counter(p['profile'] for p in prof if ':' not in p['era'])}")


def main():
    COUNTRY_LABEL.update(country_labels())
    g = build_grid()
    m = object_pass(g)
    write_outputs(g, m)
    print("unplaced rows per source:", dict(g.unplaced))


if __name__ == "__main__":
    main()
