"""Coverage audit: what gathering has produced per world region x era (visual-art-plan.md §2.2).

Reads the gathered outputs under data/interim/ (Met/AIC cultures, the regional
sweeps, the artist depth passes, contemporary selection) and counts per region x era:
  traditions   distinct culture / dynasty / school labels (folded, unioned across sources)
  objects      objects behind those labels (culture-level rows only, so not double-counted)
  sources      distinct sources contributing
  artists      selected or named artists (depth passes, contemporary, regional makers)

Regions come from the source's own region where it records one, else from keywords
on the culture label. Eras use the label's median date: antiquity < 500, traditional
500-1859, modern 1860-1959, contemporary >= 1960. Both are approximations meant to
find empty and thin cells, not to classify.

Output: data/interim/coverage_grid.csv
Usage:  python3 pipelines/visual_art/coverage_audit.py
"""
import collections
import csv
import glob
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INTERIM = os.path.join(ROOT, "data", "interim")
REG = os.path.join(INTERIM, "regional")
OUT = os.path.join(INTERIM, "coverage_grid.csv")

REGIONS = [
    "Western Europe", "Central & Eastern Europe", "Greco-Roman & Byzantine Mediterranean",
    "Ancient Egypt & Nubia", "Ancient Near East", "Islamic world (MENA, Iran, Anatolia)",
    "Central Asia & Silk Road", "Himalaya", "South Asia", "Southeast Asia", "China", "Japan", "Korea",
    "Sub-Saharan Africa", "North America (Indigenous)", "North America (settler)",
    "Mesoamerica & Caribbean", "South America", "Oceania (Pacific)", "Australia (Aboriginal)",
]
ERAS = ["antiquity", "traditional", "modern", "contemporary"]

# (regex on the folded label, region); first match wins.
KEYWORDS = [
    (r"aborigin|arnhem|torres strait|yolngu|papunya|kimberley|tiwi|warlpiri", "Australia (Aboriginal)"),
    (r"egypt|coptic|nubia|meroit|kerma|napatan|ptolema|pharaon", "Ancient Egypt & Nubia"),
    (r"greek|attic|corinth|etrusc|roman|hellenist|cypri|minoan|myce|cycladic|byzant|boeotian|laconian|"
     r"apulian|campanian|south italian|italic|villanovan|sardin|thracian|macedon|crete|cretan", "Greco-Roman & Byzantine Mediterranean"),
    (r"sumer|akkad|babylon|assyria|mesopotam|elam|hittite|urart|phoenic|canaan|levant|achaemenid|parthian|"
     r"sasan|anatolia|luristan|neo-|hurrian|mitanni|south arabian|sabaean|nabat|palmyr|bactria|scythian|"
     r"iran(ian)?, (ancient|bronze|iron)|proto-elamite|cappadoc|syro|ugarit", "Ancient Near East"),
    (r"tibet|nepal|newar|bhutan|ladakh|himalaya|mongol|kashmir|zanabazar|menri|khyenri|gardri", "Himalaya"),
    (r"sogd|khotan|kucha|turfan|uyghur|dunhuang|gandhar|kushan|silk road|khwarazm|central asia|kazakh|"
     r"uzbek|turkmen|kyrgyz|tajik|bukhar|samarkand", "Central Asia & Silk Road"),
    (r"islam|ottoman|safavid|qajar|timurid|mamluk|fatimid|abbasid|umayyad|seljuq|seljuk|ilkhan|ayyubid|"
     r"nasrid|almohad|almoravid|persian|iran|turk|syria|egypt.*islam|morocc|tunis|alger|maghreb|moorish|"
     r"arab|iraq|yemen|hispano-moresque|mudejar|samanid|buyid|zangid|aghlabid|tulunid|jalayirid|injuid", "Islamic world (MENA, Iran, Anatolia)"),
    (r"china|chinese|han dynasty|tang|song dynasty|ming|qing|yuan dynasty|zhou|shang|liao|jin dynasty|"
     r"northern wei|six dynasties|taiwan|hong kong|jingdezhen", "China"),
    (r"japan|edo|meiji|heian|kamakura|muromachi|momoyama|jomon|yayoi|kofun|nara period|asuka|ainu|ryukyu|"
     r"okinawa|ukiyo", "Japan"),
    (r"korea|joseon|goryeo|silla|baekje|goguryeo|gaya", "Korea"),
    (r"india|mughal|rajput|rajasthan|pahari|deccan|bengal|gujarat|tamil|kerala|chola|pala\b|gupta|sri lanka|"
     r"ceylon|pakistan|bangladesh|orissa|odisha|karnataka|andhra|mysore|maratha|sikh|punjab|company school|"
     r"kangra|mewar|bundi|kota|jaipur|basohli|mathura|vijayanagar|hoysala", "South Asia"),
    (r"thai|siam|burm|myanmar|cambod|khmer|angkor|lao|vietnam|champa|cham\b|java|bali|sumatra|indonesia|"
     r"borneo|dayak|batak|toraja|sulawesi|malay|philippin|flores|sumba|timor|dong son|ban chiang|pyu|mon\b", "Southeast Asia"),
    (r"maya|aztec|mexica|olmec|teotihuacan|zapotec|mixtec|toltec|huastec|veracruz|west mexico|colima|"
     r"jalisco|nayarit|mexic|guatemal|costa rica|panama|nicaragu|hondur|salvador|caribbean|taino|cuba|"
     r"haiti|jamaica|puerto ric|dominican|chiriqui|diquis|cocle|guanacaste|mesoameric", "Mesoamerica & Caribbean"),
    (r"inca|moche|nasca|nazca|chimu|wari|paracas|chavin|tiwanaku|tiahuanaco|recuay|lambayeque|sican|chancay|"
     r"peru|bolivia|ecuador|colombia|venezuel|brazil|argentin|chile|amazon|andean|quimbaya|tairona|muisca|"
     r"calima|tolima|valdivia|jama|manteno|guyana|surinam|paraguay|urugua|mapuche|shipibo|kayapo|wayana", "South America"),
    (r"maori|hawai|samoa|tonga|fiji|papua|new guinea|sepik|asmat|solomon|vanuatu|new caledon|kanak|"
     r"micronesia|polynes|melanesia|marquesa|tahiti|cook island|easter island|rapa nui|caroline|marshall|"
     r"palau|chuuk|kiribati|tuvalu|admiralty|new ireland|new britain|massim|trobriand|torres|abelam|iatmul|"
     r"oceani|pacific|aotearoa|new zealand|austral islands|mangareva|niue", "Oceania (Pacific)"),
    (r"yoruba|akan|asante|ashanti|baule|dogon|bamana|bambara|senufo|kuba|kongo|luba|chokwe|songye|fang|"
     r"punu|kota|igbo|benin|edo\b|ife|nok|bamileke|bamum|grassfields|cameroon|zulu|xhosa|ndebele|shona|"
     r"maasai|swahili|ethiopi|ashanti|fon\b|dahomey|mende|dan\b|we\b|guro|lobi|mossi|bobo|bwa|hausa|fulani|"
     r"tuareg|kenya|tanzania|uganda|congo|zaire|angola|zambia|zimbabwe|mozambique|madagascar|malagasy|"
     r"nigeria|ghana|mali|burkina|senegal|guinea|sierra leone|liberia|ivory coast|cote d'ivoire|gabon|"
     r"sudan|somali|rwanda|burundi|malawi|botswana|namibia|south africa|lesotho|eswatini|swazi|chad|niger\b|"
     r"african|makonde|pende|yaka|lega|hemba|tabwa|mangbetu|azande|teke|vili|yombe|bembe|kwele|ogoni|"
     r"ijo|ibibio|ejagham|mumuye|jukun|chamba|tiv|nupe|igala|idoma|bijago|baga|nalu|kissi|toma|loma", "Sub-Saharan Africa"),
    (r"navajo|dine|hopi|zuni|pueblo|apache|lakota|sioux|cheyenne|crow|blackfoot|cree|ojibwe|anishinaabe|"
     r"iroquois|haudenosaunee|mohawk|seneca|cherokee|creek|seminole|tlingit|haida|kwakwaka|kwakiutl|"
     r"tsimshian|nuu-chah|salish|inuit|inupiat|yupik|aleut|athabas|pomo|chumash|maidu|washoe|arapaho|kiowa|"
     r"comanche|osage|pawnee|mandan|hidatsa|arikara|shoshone|ute|paiute|nez perce|yakama|delaware|lenape|"
     r"wampanoag|micmac|mi'kmaq|penobscot|abenaki|huron|wendat|winnebago|ho-chunk|menominee|potawatomi|"
     r"plains|woodlands|great basin|northwest coast|subarctic|arctic|mississippian|hopewell|adena|"
     r"anasazi|ancestral pueblo|mimbres|hohokam|mogollon|native american|first nations|american indian", "North America (Indigenous)"),
    (r"americ|united states|canad|new england|pennsylvan|new york|boston|philadelph|shaker", "North America (settler)"),
    (r"russia|poland|polish|hungar|czech|bohemia|slovak|ukrain|belarus|lithuan|latvi|eston|romania|"
     r"moldav|bulgar|serbia|croat|sloven|bosnia|montenegr|macedonian|albania|georgia|armenia|azerbaij|"
     r"finland|finnish|sami|karelia|transylvan|balkan|slav|cossack|tatar|bashkir|komi|mari\b", "Central & Eastern Europe"),
    (r"french|france|british|english|scottish|irish|welsh|italian|italy|venet|floren|spanish|spain|portug|"
     r"german|austria|swiss|dutch|flemish|netherland|belgi|danish|denmark|swed|norw|iceland|europe|"
     r"medieval|gothic|romanesque|carolingian|ottonian|merovingian|anglo-saxon|celtic|viking|frankish|"
     r"visigoth|langobard|limoges|nuremberg|augsburg|meissen|sevres|delft|faience|majolica|maiolica", "Western Europe"),
]
KEYWORDS = [(re.compile(p), r) for p, r in KEYWORDS]

# Met departments with a fixed region (others fall back to keywords).
MET_DEPT = {
    "Egyptian Art": "Ancient Egypt & Nubia",
    "Greek and Roman Art": "Greco-Roman & Byzantine Mediterranean",
    "Ancient West Asian Art": "Ancient Near East",
    "Islamic Art": "Islamic world (MENA, Iran, Anatolia)",
    "The American Wing": "North America (settler)",
}


def fold(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s).strip()


def region_of(label, default=None):
    f = fold(label)
    for pat, reg in KEYWORDS:
        if pat.search(f):
            return reg
    return default


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def era_of(year):
    if year is None:
        return None
    if year < 500:
        return "antiquity"
    if year < 1860:
        return "traditional"
    if year < 1960:
        return "modern"
    return "contemporary"


def mid(*vals):
    vs = [num(v) for v in vals if num(v) is not None]
    return sum(vs) / len(vs) if vs else None


def rows(path):
    with open(path, encoding="utf-8") as f:
        yield from csv.DictReader(f)


class Grid:
    def __init__(self):
        self.trad = collections.defaultdict(set)
        self.objects = collections.Counter()
        self.sources = collections.defaultdict(set)
        self.artists = collections.Counter()
        self.unplaced = collections.Counter()

    def tradition(self, source, label, region, year, objects):
        era = era_of(year)
        if not region or not era:
            self.unplaced[source] += 1
            return
        self.trad[region, era].add(fold(label))
        self.objects[region, era] += int(num(objects) or 0)
        self.sources[region, era].add(source)

    def artist(self, source, region, era, n=1):
        if region and era:
            self.artists[region, era] += n
            self.sources[region, era].add(source)


def main():
    g = Grid()

    # Met (and AIC counts folded in) cultures from build_traditions.py
    for r in rows(os.path.join(INTERIM, "unattributed_cultures.csv")):
        if r["kind"] != "culture":
            continue
        reg = MET_DEPT.get(r["dominant_department"]) or region_of(r["label"])
        if reg == "Ancient Egypt & Nubia" and r["dominant_department"] == "Islamic Art":
            reg = "Islamic world (MENA, Iran, Anatolia)"
        g.tradition("met/aic", r["label"], reg, mid(r["begin_median"], r["end_median"]), r["objects"])

    # Regional sweeps that share the culture-row layout
    defaults = {
        "africa_traditions.csv": "Sub-Saharan Africa",
        "americas_oceania_traditions.csv": None,
        "south_southeast_asia_traditions.csv": "South Asia",
    }
    for name, default in defaults.items():
        for r in rows(os.path.join(REG, name)):
            if r["kind"] != "culture":
                continue
            label = r["culture"] or r["culture_group"]
            reg = region_of(label) or region_of(r["culture_group"]) or default
            g.tradition(name.split("_traditions")[0], label, reg, num(r["mid_median"]), r["objects"])
    for r in rows(os.path.join(REG, "africa_oceania_targeted_traditions.csv")):
        if r["kind"] != "culture":
            continue
        default = "Sub-Saharan Africa" if r["region"] == "africa" else "Oceania (Pacific)"
        label = r["culture"] or r["culture_group"]
        reg = region_of(label) or region_of(r["culture_group"]) or default
        g.tradition("africa_oceania_targeted", label, reg, num(r["mid_median"]), r["objects"])

    # East Asia: country x period x object type
    ea = {"China": "China", "Japan": "Japan", "Korea": "Korea", "Taiwan": "China"}
    for r in rows(os.path.join(REG, "east_asia_traditions.csv")):
        reg = ea.get(r["country"])
        g.tradition("east_asia", f'{r["country"]} {r["period_en"]}', reg,
                    mid(r["period_begin"], r["period_end"]), r["all_objects"])
    for r in rows(os.path.join(REG, "east_asia_artists.csv")):
        y = num(r["birth_year"])
        y = y + 40 if y is not None else (num(r["death_year"]) - 10 if num(r["death_year"]) else None)
        g.artist("east_asia", ea.get(r["country"]), era_of(y))

    # Himalaya / Central Asia
    for r in rows(os.path.join(REG, "himalaya_central_asia_traditions.csv")):
        if r["kind"] not in ("tradition", "tradition_period"):
            continue
        reg = "Himalaya" if r["region_group"] == "Himalaya" else "Central Asia & Silk Road"
        g.tradition("himalaya_central_asia", f'{r["tradition"]} {r["period"]}', reg, num(r["mid_median"]), r["objects"])

    # Islamic world: dynasties and schools
    isl = "Islamic world (MENA, Iran, Anatolia)"
    for r in rows(os.path.join(REG, "islamic_dynasties.csv")):
        reg = "South Asia" if re.search(r"mughal|deccan|sultanate|bengal|gujarat", fold(r["dynasty"])) else isl
        g.tradition("islamic", r["dynasty"], reg, num(r["mid_median"]), r["objects"])
    for r in rows(os.path.join(REG, "islamic_schools.csv")):
        reg = region_of(r["name"].replace("Company", "India"), isl)
        if re.search(r"mughal|deccan|lucknow|murshidabad|salim|company|golconda|bijapur|hyderabad", fold(r["name"])):
            reg = "South Asia"
        g.tradition("islamic", r["name"], reg, num(r["mid_median"]), 0)
    for r in rows(os.path.join(REG, "islamic_makers.csv")):
        reg = "South Asia" if re.search(r"mughal|deccan", fold(r["dynasties"])) else isl
        g.artist("islamic", reg, era_of(mid(r["date_begin_min"], r["date_end_max"])))

    # Smithsonian cultures (NMAI is Indigenous Americas; NMAA Asia)
    for r in rows(os.path.join(REG, "smithsonian_cultures.csv")):
        if r["kind"] != "culture" or r["unit"] in ("SAAM", "CHNDM", "HMSG"):
            continue
        default = {"NMAI": "North America (Indigenous)", "NMAfA": "Sub-Saharan Africa"}.get(r["unit"])
        reg = region_of(r["culture"], default)
        if r["unit"] == "NMAI" and reg in ("North America (settler)", "Western Europe", None):
            reg = "North America (Indigenous)"
        g.tradition("smithsonian", r["culture"], reg, num(r["begin_median"]), r["objects"])

    # Regional makers
    for name, default in [("africa_makers.csv", "Sub-Saharan Africa"), ("south_southeast_asia_makers.csv", "South Asia"),
                          ("americas_oceania_makers.csv", None), ("africa_oceania_targeted_makers.csv", None),
                          ("himalaya_central_asia_makers.csv", "Himalaya")]:
        path = os.path.join(REG, name)
        if not os.path.exists(path):
            continue
        for r in rows(path):
            label = " ".join(r.get(k, "") for k in ("traditions", "tradition", "culture", "places"))
            g.artist("regional_makers", region_of(label, default), era_of(mid(r.get("date_begin_min"), r.get("date_end_max"))))

    # Artist depth passes: Europe 1400-1900 and modern regions (selected only)
    for r in rows(os.path.join(INTERIM, "visual_art", "scores_europe_1400-1900.csv")):
        if r["selected"] in ("1", "True"):
            b = num(r["birth"])
            g.artist("depth_europe", "Western Europe", era_of(b + 40 if b else None))
    modern = {
        "europe": "Western Europe", "north_america": "North America (settler)", "latin_america": "South America",
        "east_asia": "China", "south_asia": "South Asia", "southeast_asia": "Southeast Asia",
        "mena_central_asia": "Islamic world (MENA, Iran, Anatolia)", "subsaharan_africa": "Sub-Saharan Africa",
        "oceania": "Oceania (Pacific)",
    }
    for path in glob.glob(os.path.join(INTERIM, "visual_art", "scores_modern_*.csv")):
        reg = modern[os.path.basename(path)[len("scores_modern_"):-4]]
        for r in rows(path):
            if r["selected"] in ("1", "True"):
                g.artist("depth_modern", reg, "modern")
    contemp = {
        "Europe": "Western Europe", "North America": "North America (settler)",
        "Latin America and Caribbean": "South America", "East Asia": "China",
        "Middle East and North Africa": "Islamic world (MENA, Iran, Anatolia)", "Sub-Saharan Africa": "Sub-Saharan Africa",
        "Oceania": "Oceania (Pacific)", "South Asia": "South Asia", "Southeast Asia": "Southeast Asia",
        "Central Asia": "Central Asia & Silk Road",
    }
    for r in rows(os.path.join(INTERIM, "contemporary_scores.csv")):
        if r["selected"] == "1":
            g.artist("contemporary", contemp.get(r["region"]), "contemporary")

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["region", "era", "traditions", "objects", "artists", "n_sources", "sources"])
        for reg in REGIONS:
            for era in ERAS:
                k = (reg, era)
                w.writerow([reg, era, len(g.trad[k]), g.objects[k], g.artists[k], len(g.sources[k]),
                            "; ".join(sorted(g.sources[k]))])
    print(f"wrote {OUT}")
    print("unplaced rows per source:", dict(g.unplaced))
    media_grid()


# --- Region x medium -------------------------------------------------------
# The same region can look covered on the strength of one medium (painting) while
# its textiles or ceramics are absent; this grid counts, per region x medium, the
# objects and the distinct culture labels (>= MIN_OBJECTS objects in that medium).
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
MEDIA_NAMES = [m for m, _ in MEDIA] + ["other"]

MET_DEPT_REGION = dict(MET_DEPT, **{
    "European Paintings": "Western Europe", "European Sculpture and Decorative Arts": "Western Europe",
    "Medieval Art": "Western Europe", "The Cloisters": "Western Europe", "Robert Lehman Collection": "Western Europe",
})


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

    def add(self, source, region, medium, culture):
        if not region:
            return
        k = (region, medium)
        self.objects[k] += 1
        self.cultures[k][fold(culture) or "(unlabelled)"] += 1
        self.sources[k].add(source)


def media_grid():
    csv.field_size_limit(1 << 30)
    m = MediaGrid()

    met = os.path.join(ROOT, "data", "raw", "museums", "MetObjects.csv")
    with open(met, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            dept = r["Department"]
            if dept in ("Modern and Contemporary Art", "Photographs", "The Libraries", "Drawings and Prints") and not r["Culture"]:
                # Artist-led departments: medium coverage there comes from the artist passes.
                continue
            label = r["Culture"] or r["Country"] or r["Artist Nationality"]
            reg = region_of(label) or MET_DEPT_REGION.get(dept)
            if reg == "Ancient Egypt & Nubia" and dept == "Islamic Art":
                reg = "Islamic world (MENA, Iran, Anatolia)"
            med = medium_of(r["Classification"], r["Object Name"], r["Medium"])
            m.add("met", reg, med, r["Culture"] or r["Country"])

    sweeps = {
        "africa_objects.csv": "Sub-Saharan Africa", "americas_oceania_objects.csv": None,
        "south_southeast_asia_objects.csv": "South Asia", "africa_oceania_targeted_objects.csv": None,
    }
    for name, default in sweeps.items():
        for r in rows(os.path.join(REG, name)):
            label = r["culture"] or r["culture_group"] or r["place"]
            dflt = default
            if dflt is None:
                dflt = "Oceania (Pacific)" if "oceania" in fold(r["subregion"] + r["region"]) and "americ" not in fold(r["subregion"]) \
                    else ("Sub-Saharan Africa" if "africa" in fold(r["region"]) else None)
            reg = region_of(label) or region_of(r["subregion"]) or dflt
            med = medium_of(r["object_group"], r["object_type"], r["materials"])
            m.add(name.split("_objects")[0], reg, med, label)

    ea = {"China": "China", "Japan": "Japan", "Korea": "Korea", "Taiwan": "China"}
    for r in rows(os.path.join(REG, "east_asia_objects.csv")):
        ot = r["object_type"]
        if ot in ("archaeology", "documents and historical materials", "other"):
            ot = r["object_subtype"] or ot
        m.add("east_asia", ea.get(r["country"]), medium_of(ot, r["title_en"]), r["period_en"])

    for r in rows(os.path.join(REG, "himalaya_central_asia_objects.csv")):
        reg = "Himalaya" if r["region_group"] == "Himalaya" else "Central Asia & Silk Road"
        m.add("himalaya_central_asia", reg, medium_of(r["medium"], r["object_type"]), r["tradition"])

    for r in rows(os.path.join(REG, "islamic_objects.csv")):
        reg = "South Asia" if re.search(r"mughal|deccan", fold(r["dynasty"])) else "Islamic world (MENA, Iran, Anatolia)"
        med = "calligraphy & book arts" if r["book_arts"] in ("1", "True", "yes") and "painting" not in fold(r["object_type"]) \
            else medium_of(r["object_type"], r["materials_technique"])
        m.add("islamic", reg, med, r["dynasty"] or r["culture_place"])

    for r in rows(os.path.join(REG, "smithsonian_objects.csv")):
        if r["unit"] in ("SAAM", "HMSG", "CHNDM"):
            continue
        default = {"NMAI": "North America (Indigenous)", "NMAfA": "Sub-Saharan Africa"}.get(r["unit"])
        label = r["culture"] or r["countries"]
        reg = region_of(label, default)
        if r["unit"] == "NMAI" and reg in ("North America (settler)", "Western Europe", None):
            reg = "North America (Indigenous)"
        m.add("smithsonian", reg, medium_of(r["object_type_indexed"], r["object_type"], r["object_name"], r["medium"]), label)

    with open(MEDIA_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["region", "medium", "objects", "cultures", "n_sources", "sources", "top_cultures"])
        for reg in REGIONS:
            for med in MEDIA_NAMES:
                k = (reg, med)
                cult = {c: n for c, n in m.cultures[k].items() if n >= MIN_OBJECTS and c != "(unlabelled)"}
                top = "; ".join(f"{c} ({n})" for c, n in sorted(cult.items(), key=lambda x: -x[1])[:8])
                w.writerow([reg, med, m.objects[k], len(cult), len(m.sources[k]), "; ".join(sorted(m.sources[k])), top])
    print(f"wrote {MEDIA_OUT}")


if __name__ == "__main__":
    main()
