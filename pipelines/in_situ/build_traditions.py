"""In-situ visual traditions: rock art, wall painting, mosaics, geoglyphs, body art (visual-art-plan.md §2A, §2.1b, §2.2).

Every source gathered so far is a museum, so art that exists *in place* (painted
caves, rock shelters, church fresco cycles, mosaics on walls and floors, hill
figures, tattooing) is missing from the grid. This pass gathers candidate
tradition nodes and exemplar sites for it from Wikidata, following the pattern
of pipelines/architecture/nonwestern_exemplars.py:

1. Verify every class / helper QID against its English label (CLASSES, EXCLUDE,
   HELPERS); stop on a mismatch unless --force.
2. Harvest candidates:
   - instances (P31/P279*) of each class root (rock art, cave with prehistoric
     art, mural, fresco-as-artwork, ancient Roman mural painting, mosaic, zellij,
     azulejo, geoglyph, hill figure, land art), plus items made with the fresco
     technique (P2079) or with genre P136 = mural / rock art / land art;
     instances of EXCLUDE classes are dropped (photo mosaics, rock-cut
     architecture, medical tattoos, ...);
   - UNESCO World Heritage items (P1435 = Q9259 or P757) whose English label or
     description names rock art, painting, frescoes, murals, mosaics or
     geoglyphs;
   - SEEDS: named sites (Ajanta, Ravenna, Bonampak, ...) resolved by exact
     English label at run time (most sitelinks wins; unresolved labels are
     printed, never guessed).
3. Tradition items already in Wikidata: subclasses (P279+) of the class roots
   (Saharan rock art, Kerala mural painting, Byzantine mosaics, irezumi, ...),
   art styles / art movements / styles of painting whose label or description
   names an in-situ medium (Barrier Canyon Style, Pompeian Styles, ...), and
   body-art items (instances/subclasses of tattoo, body art, body painting,
   scarification, mehndi, tattoo style). Body art is Wikidata items only.
4. Details per candidate: P17, P571/P580/P1319, P1435, P757, P361, P276, P131
   (3 levels), P135/P136/P149, P2596, P2348, P31, P625, sitelinks, en label and
   description. Artworks (murals, frescoes, mosaics, ceiling paintings, tile
   panels) roll up to their location (P276) as the *site*; works whose location
   is a museum are kept but flagged in_museum and not counted as sites.
5. Rules (RULES below, first match wins): kind x country (ISO 3166 alpha-2 via
   P297) x text regex (label, description, admin places, part-of, location,
   culture, period, style, class labels) x date range x bbox -> tradition and
   world region. A rule may name a Wikidata tradition item by English label
   (`wd`), resolved and verified at run time. Unmatched sites fall back to
   "<kind> - <country> (<era bucket>)", with the world region from the
   country, date and kind (default_region). The rule table is written to
   data/interim/in_situ_rules.csv for review (classifying decides; nothing
   goes into seeds/ from here).

SPARQL results are cached under data/raw/wikidata/in_situ/ (one JSON per query
text). Queries run strictly one at a time (WDQS is shared); a failed query is
reported and skipped, so re-running resumes from the cache.

Outputs:
  data/interim/in_situ_traditions.csv   label, qid, kind, region, country, era range,
                                        n_sites, n_unesco, top exemplars, sources
  data/interim/in_situ_exemplars.csv    one row per site (or body-art item)
  data/interim/in_situ_rules.csv        the rule table with match counts
  data/interim/in_situ_coverage.csv     world region x kind counts

Usage: python3 pipelines/in_situ/build_traditions.py [--force] [--per-tradition 10]
"""
import argparse
import collections
import csv
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "visual_art"))
from wikidata import sparql, year_of  # noqa: E402

RAW = os.path.join(ROOT, "data", "raw", "wikidata", "in_situ")
OUT_DIR = os.path.join(ROOT, "data", "interim")
CHUNK = 200
FAILED = []

ROCK, MURAL, MOSAIC, GEO, BODY = "rock art", "mural", "mosaic", "geoglyph", "body art"
KINDS = [ROCK, MURAL, MOSAIC, GEO, BODY]

# ---------------------------------------------------------------- verified QIDs
# key -> (QID, English label it must carry, kind). Verified 2026-10-28 by exact
# label lookup (highest-sitelink item with that label) and re-checked every run.
CLASSES = {
    "rock_art": ("Q1211146", "rock art", ROCK),
    "petroglyph": ("Q42195", "petroglyph", ROCK),
    "cave_painting": ("Q214334", "cave painting", ROCK),
    "rock_painting": ("Q1269827", "rock painting", ROCK),
    "prehistoric_cave": ("Q11269813", "cave with prehistoric art", ROCK),
    "rock_relief": ("Q22022298", "rock relief", ROCK),
    "mural": ("Q219423", "mural", MURAL),
    "fresco_work": ("Q22669139", "fresco", MURAL),
    "roman_mural": ("Q2164653", "ancient Roman mural painting", MURAL),
    "ceiling_painting": ("Q1181933", "ceiling painting", MURAL),
    "mosaic": ("Q133067", "mosaic", MOSAIC),
    "zellij": ("Q189046", "zellij", MOSAIC),
    "azulejo": ("Q3179385", "azulejo", MOSAIC),
    "ceramic_panel": ("Q97072190", "religious ceramic panel", MOSAIC),
    "geoglyph": ("Q45791", "geoglyph", GEO),
    "hill_figure": ("Q2918952", "hill figure", GEO),
    "land_art": ("Q326478", "land art", GEO),
    # body art: traditions only (no sites are harvested from these)
    "tattoo": ("Q43006", "tattoo", BODY),
    "body_art": ("Q678649", "body art", BODY),
    "body_painting": ("Q620505", "body painting", BODY),
    "scarification": ("Q570784", "scarification", BODY),
    "mehndi": ("Q769843", "mehndi", BODY),
    "tattoo_style": ("Q20819322", "tattoo style", BODY),
}
SITE_CLASSES = [k for k, v in CLASSES.items() if v[2] != BODY]
# classes whose instances are portable or wall-bound *works*: they roll up to P276
WORK_CLASSES = {"mural", "fresco_work", "roman_mural", "ceiling_painting", "mosaic", "azulejo", "ceramic_panel"}
FRESCO_TECHNIQUE = ("Q134194", "fresco painting")  # P2079 fabrication method

# Subclasses whose instances are not in-situ visual art (or are architecture,
# covered by pipelines/architecture/). Instances of these are dropped.
EXCLUDE = {
    "Q115461282": "orthophotomosaic", "Q124362135": "satellite image mosaic", "Q1279431": "photographic mosaic",
    "Q136705358": "Rubik's Cube mosaic", "Q6839695": "micromosaic", "Q11587139": "rock-cut architecture",
    "Q388774": "rock-cut architecture in India", "Q7354874": "rock temple", "Q12060132": "hillside letter",
    "Q268052": "permanent make-up", "Q7698992": "temporary tattoo", "Q18460402": "electronic tattoo",
    "Q7876104": "UV tattoo", "Q20065040": "nipple tattoo", "Q5533240": "genital tattooing",
    "Q1739189": "corneal tattooing", "Q7570372": "scleral tattooing", "Q6806607": "medical tattoo",
    "Q109969674": "medical tattooing", "Q109969664": "endoscopic tattooing", "Q109969671": "surgical tattooing",
    "Q75174533": "aesthetic annular keratopigmentation", "Q140434560": "Tacet Mark",
}
HELPERS = {
    "Q9259": "World Heritage Site", "Q43113623": "part of UNESCO World Heritage Site", "Q33506": "museum",
    "Q1792644": "art style", "Q968159": "art movement", "Q17399019": "style of painting",
    "Q5": "human", "Q4167836": "Wikimedia category", "Q4167410": "Wikimedia disambiguation page",
    FRESCO_TECHNIQUE[0]: FRESCO_TECHNIQUE[1],
}
STYLE_TYPES = ["Q1792644", "Q968159", "Q17399019", "Q20819322"]

KIND_RE = {
    ROCK: r"rock art|rock-art|petroglyph|pictograph|rock painting|rock drawing|rock carving|rock engraving|cave painting|"
          r"cave art|painted cave|parietal|rock shelter painting|hand stencil|cup.and.ring",
    MURAL: r"\bmural|fresco|wall painting|wall-painting|painted church|ceiling painting|tomb painting|painted tomb|"
           r"church painting|temple painting|muralism",
    MOSAIC: r"mosaic|zellige|zellij|azulejo|tilework|tile work|\btiles?\b.*(mosque|madrasa|revetment)|trencad",
    GEO: r"geoglyph|hill figure|chalk figure|nazca lines|intaglio|land art|earthwork art",
    BODY: r"tattoo|tatau|tā moko|ta moko|scarification|cicatri|body painting|body art|mehndi|henna|irezumi",
}
WHS_RE = (r"rock art|rock-art|petroglyph|pictograph|rock painting|rock drawing|rock carving|rock engraving|cave art|"
          r"painted cave|paleolithic|palaeolithic art|prehistoric art|fresco|\bmural|wall painting|painted church|"
          r"painted monaster|\bpainted\b|mosaic|geoglyph|nazca|hill figure")

# ---------------------------------------------------------------- seeds
# Named exemplar sites and body-art items from the brief. Resolved by exact
# English label (highest sitelinks); kind is used only when no class matches.
SEEDS = {
    ROCK: ["Lascaux", "Cave of Altamira", "Chauvet Cave", "Cosquer Cave", "Font-de-Gaume cave", "Cave of Niaux",
           "Rock Art of the Mediterranean Basin on the Iberian Peninsula",
           "Siega Verde", "Prehistoric Rock Art Sites in the Côa Valley",
           "Tassili n'Ajjer", "Tadrart Acacus", "Laas Gaal", "Bhimbetka rock shelters", "Cueva de las Manos",
           "Serra da Capivara National Park", "Kakadu National Park", "Ubirr", "Murujuga", "Tsodilo", "Twyfelfontein",
           "Maloti-Drakensberg Park", "Matobo National Park", "Kondoa Rock Art Sites", "Chongoni Rock Art Area",
           "Tamgaly", "Gobustan State Reserve", "rock drawings in Valcamonica", "Rock Carvings in Tanum",
           "Rock carvings at Alta", "Rock Paintings of Hua Mountain", "Bangudae Petroglyphs",
           "Horseshoe Canyon", "Gwion Gwion rock art", "Coso Rock Art District", "Writing-on-Stone Provincial Park",
           "Petroglyph National Monument", "Newspaper Rock State Historic Monument",
           "Rock Paintings of Sierra de San Francisco", "Leang Tedongnge", "Chiribiquete National Park",
           "Toro Muerto", "Cave of Swimmers", "Ennedi Plateau", "Dhambalin", "Sego Canyon", "Painted Rock",
           "Kimberley", "Nourlangie Rock", "Ku-ring-gai Chase National Park", "Quinkan rock art", "Naqsh-e Rostam",
           "Behistun inscription", "Jubbah", "Rock Art in the Hail Region of Saudi Arabia", "Wadi Rum",
           "Leang Bulu' Sipong 4", "Seminole Canyon State Park and Historic Site", "Pedra Furada"],
    MURAL: ["Ajanta Caves", "Sigiriya", "Mogao Caves", "Kizil Caves", "Bezeklik Thousand Buddha Caves", "Bonampak",
            "Teotihuacan", "Cacaxtla", "San Bartolo", "Pompeii", "Villa of the Mysteries", "Herculaneum",
            "Etruscan Necropolises of Cerveteri and Tarquinia", "Tomb of the Leopards", "Tomb of Nefertari",
            "Valley of the Kings", "Akrotiri", "Thracian Tomb of Kazanlak", "Studenica Monastery", "Sopoćani",
            "Visoki Dečani", "Gračanica monastery", "Boyana Church", "Church of St. Panteleimon",
            "Gelati Monastery", "Ferapontov Monastery", "Voroneț Monastery", "churches of Moldavia",
            "Painted Churches in the Troödos Region", "Chora Church", "Göreme National Park and the Rock Sites of Cappadocia",
            "Scrovegni Chapel", "Sistine Chapel", "Sant Climent de Taüll", "Abbey Church of Saint-Savin-sur-Gartempe",
            "Alchi Monastery", "Tabo Monastery, Himachal Pradesh", "Ananda Temple", "Wat Phra Kaew", "Bagan", "Qasr Amra",
            "Chehel Sotun", "Mattancherry Palace", "Padmanabhapuram Palace", "Takamatsuzuka Tomb", "Kitora Tomb",
            "Goguryeo tombs", "Faras", "Panjakent", "Afrasiyab", "Hospicio Cabañas",
            "Andahuaylillas", "Huaca de la Luna", "Yongle Temple", "Fahai Temple",
            "Ellora Caves", "Dambulla cave temple", "Lepakshi", "Prahadisvarar Temple", "Shalu Monastery",
            "Palace of Fine Arts", "Mirogoj Cemetery", "Rila Monastery", "Kremikovtsi Monastery", "Saviour Church on Nereditsa",
            "Wat Pho", "Shwedagon Pagoda", "Lalibela", "Church of Debra Berhan Selassie", "Tomb of the Diver",
            "Tomb of Philip ΙΙ", "Sveshtari", "Ostrog monastery", "Mileševa", "Hosios Loukas",
            "Mystras", "Monastery of Saint John the Theologian"],
    MOSAIC: ["Basilica of San Vitale", "Mausoleum of Galla Placidia", "Early Christian Monuments of Ravenna",
             "Basilica of Sant'Apollinare Nuovo", "Hagia Sophia", "Dome of the Rock", "Umayyad Mosque",
             "Saint Sophia Cathedral", "Saint Michael's Golden-Domed Monastery", "Cappella Palatina",
             "Monreale Cathedral", "Cefalù Cathedral", "St Mark's Basilica", "Daphni Monastery", "Nea Moni of Chios",
             "Villa Romana del Casale", "Zeugma", "Madaba Map", "Khirbat al-Mafjar", "Shah Mosque", "Sheikh Lotfollah Mosque",
             "Registan", "Wazir Khan Mosque", "Rüstem Pasha Mosque", "Alhambra", "Bou Inania Madrasa", "Ben Youssef Madrasa",
             "Park Güell", "Santa Maria Maggiore", "Torcello Cathedral", "Basilica of Our Lady of the Assumption, St. Hermagoras and St. Fortunatus", "Volubilis",
             "Bardo National Museum", "Church of the Multiplication of the Loaves and Fish", "Gelati Monastery",
             "Chora Church", "Mosque-Cathedral of Cordoba", "Shah-i-Zinda", "Gur-e Amir", "Blue Mosque, Tabriz",
             "Tile mosaic of Lahore Fort"],
    GEO: ["Nazca Lines", "Uffington White Horse", "Cerne Abbas Giant", "Long Man of Wilmington", "Atacama Giant",
          "Cerro Pintados", "Blythe Intaglios", "Serpent Mound", "Steppe Geoglyph", "Spiral Jetty", "Palpa Lines",
          "Westbury White Horse", "Marree Man", "Paracas Candelabra", "Lines and Geoglyphs of Nasca and Palpa"],
    BODY: ["tā moko", "irezumi", "mehndi", "scarification", "Malu", "pe'a", "batok", "Deq", "kakiniit", "hajichi",
           "veiqia", "body painting", "tattooing in Ainu and Jōmon culture", "Yantra tattooing", "Iban tattoo", "Marquesan tattoo",
           "Hawaii tattoo", "kakau", "moko kauae", "Berber tattoo", "henna", "uli", "Kalinga tattoo",
           "Mentawai tattoo", "Chin tattoo", "godna", "Nuba scarification", "sailor tattoos", "Olympic tattoo",
           "Prison tattooing", "American traditional tattoo", "tattooing in China", "tattooing in India",
           "tattooing in Myanmar", "tattoos in Palau", "rajah", "tebori", "Litema"],
}

# ---------------------------------------------------------------- world regions
REGIONS = [
    "Western Europe", "C&E Europe", "Greco-Roman/Byzantine", "Egypt & Nubia", "Near East", "Islamic world",
    "Central Asia", "Himalaya", "South Asia", "SE Asia", "China", "Japan", "Korea", "Sub-Saharan Africa",
    "N. America Indigenous", "Mesoamerica", "South America", "Oceania", "Aboriginal Australia",
]
# Extra buckets (not in the brief's list): kept separate rather than forced into a wrong region.
EXTRA_REGIONS = ["North Africa & Sahara", "Caribbean", "North America (settler/modern)"]

ISO_REGION = {}
for _r, _codes in {
    "Western Europe": "FR ES PT IT DE GB IE NL BE LU CH AT DK SE NO FI IS MT MC AD SM VA LI FO",
    "C&E Europe": "PL CZ SK HU RO BG RS HR SI BA ME MK AL XK UA BY RU MD LT LV EE GE AM",
    "Greco-Roman/Byzantine": "GR CY",
    "Egypt & Nubia": "EG SD SS",
    "Near East": "IL PS JO LB SY IQ IR SA YE OM AE QA BH KW AZ TR",
    "Central Asia": "KZ KG UZ TJ TM AF MN",
    "Himalaya": "NP BT",
    "South Asia": "IN PK BD LK MV",
    "SE Asia": "TH MM KH LA VN MY SG ID PH BN TL",
    "China": "CN TW HK MO",
    "Japan": "JP",
    "Korea": "KR KP",
    "North Africa & Sahara": "MA DZ TN LY MR EH",
    "Mesoamerica": "MX GT BZ HN SV NI CR PA",
    "Caribbean": "CU DO HT JM PR BS TT BB LC VC GD AG DM KN VG VI GP MQ AW CW BQ KY TC",
    "South America": "BR AR CL PE BO EC CO VE GY SR GF UY PY",
    "Oceania": "NZ PG FJ WS TO VU SB NC PF FM MH PW KI TV NR CK NU GU MP AS WF",
    "Aboriginal Australia": "AU",
    "N. America Indigenous": "US CA GL",
}.items():
    for _c in _codes.split():
        ISO_REGION[_c] = _r
ISLAMIC_ISO = set("MA DZ TN LY MR EG SD SA YE OM AE QA BH KW IQ IR SY JO LB PS IL TR AF UZ TM TJ AZ KZ KG".split())
NEAR_EAST_LATE_ANTIQUE = set("SY JO LB IL PS TR".split())


def default_region(iso, year, kind, lon=None):
    """World region for a site from its country, date and kind (used when no rule sets one)."""
    r = ISO_REGION.get(iso)
    if r is None:
        return r
    if iso == "RU" and lon is not None and lon > 60:
        r = "Central Asia"
    if kind == BODY:
        return r
    if iso in ISLAMIC_ISO and year is not None and year >= 650 and iso not in ("IL",) and kind != ROCK:
        return "Islamic world"
    if iso in ("EG", "SD") and (year is None or year < 640):
        return "Egypt & Nubia"
    if year is not None and year < 650 and kind in (MURAL, MOSAIC):
        if iso == "IT" or iso in NEAR_EAST_LATE_ANTIQUE and year >= -330 or iso in ("TN", "LY", "DZ", "MA") and year >= -146:
            return "Greco-Roman/Byzantine"
    if iso == "TR" and year is not None and 330 <= year < 1453:
        return "Greco-Roman/Byzantine"
    if r == "Aboriginal Australia" and kind in (MURAL, MOSAIC) and (year is None or year >= 1788):
        return "Oceania"
    if r == "N. America Indigenous" and kind in (MURAL, MOSAIC) and (year is None or year >= 1600):
        return "North America (settler/modern)"
    return r


def era_bucket(y):
    if y is None:
        return "undated"
    if y < -3000:
        return "prehistoric"
    if y < 500:
        return "ancient"
    if y < 1500:
        return "medieval"
    if y < 1850:
        return "early modern"
    return "modern"


# ---------------------------------------------------------------- rule table
def R(rid, tradition, kinds, region, era="", **cond):
    """One rule. kinds: a kind or tuple of kinds; region None = default_region().
    Conditions (all must hold): iso (set of ISO2), text (regex over the combined
    text), notext (regex that must NOT match), years (lo, hi; needs a date),
    before (year < x, or undated when undated_ok), bbox (lat_lo, lat_hi, lon_lo, lon_hi),
    wd (English label of an existing Wikidata tradition item, resolved at run time)."""
    if isinstance(kinds, str):
        kinds = (kinds,)
    return dict(id=rid, tradition=tradition, kinds=set(kinds), region=region, era=era, **cond)


def S(codes):
    return set(codes.split())


PALAEO = r"palaeolithic|paleolithic|magdalen|aurignac|solutre|gravett|lascaux|altamira|chauvet|cosquer|font-de-gaume|" \
         r"niaux|pech merle|pech-merle|rouffignac|tito bustillo|el castillo|ekain|santimamiñe|covalanas|la pasiega|" \
         r"candamo|combarelles|cussac|gargas|cave with prehistoric art|isturitz|les trois|cap blanc|la garma|hornos de la pe"
AUS_NT_TOP = (-15.5, -10.5, 129.0, 137.5)
AUS_KIMBERLEY = (-19.5, -13.0, 121.0, 129.0)

RULES = [
    # ======================= ROCK ART =======================
    # --- Europe
    R("RA01", "Franco-Cantabrian Palaeolithic cave art", ROCK, "Western Europe", "c. 40,000-11,000 BP",
      iso=S("FR ES"), text=PALAEO, notext=r"levant|mediterranean basin"),
    R("RA02", "Côa / Siega Verde open-air Palaeolithic rock art", ROCK, "Western Europe", "c. 25,000-10,000 BP",
      iso=S("PT ES"), text=r"\bc[oô]a\b|siega verde|mazouco|escoural|faia"),
    R("RA03", "Levantine rock art (Mediterranean Basin of Iberia)", ROCK, "Western Europe", "c. 8000-3500 BCE",
      iso=S("ES"), text=r"levant|mediterranean basin|valltorta|cogul|minateda|abrigo|abric|shelter",
      wd="Rock Art of the Mediterranean Basin on the Iberian Peninsula"),
    R("RA04", "Iberian Schematic rock art", ROCK, "Western Europe", "c. 5000-1000 BCE",
      iso=S("ES PT"), text=r"schemat|esquem|petroglyph|petroglifo|insculturas|galicia|pontevedra|ourense|campo lameiro"),
    R("RA05", "Tanum / Bohuslän Bronze Age rock carvings", ROCK, "Western Europe", "c. 1700-500 BCE",
      iso=S("SE"), text=r"tanum|bohusl|vitlycke|fossum|aspeberget|litsleby"),
    R("RA06", "Alta rock art (Finnmark)", ROCK, "Western Europe", "c. 5000-0 BCE", iso=S("NO"), text=r"\balta\b|finnmark|hjemmeluft"),
    R("RA07", "Scandinavian rock carvings (hällristningar / helleristninger)", ROCK, "Western Europe", "Neolithic-Iron Age",
      iso=S("SE NO DK FI")),
    R("RA08", "Valcamonica and Alpine rock art", ROCK, "Western Europe", "c. 8000 BCE-1000 CE",
      iso=S("IT FR CH AT"), text=r"camonica|valcamonica|valtellina|bego|merveilles|grosio|naquane|capo di ponte"),
    R("RA09", "Atlantic rock art (cup-and-ring marks)", ROCK, "Western Europe", "Neolithic-Bronze Age",
      iso=S("GB IE"), wd="cup and ring mark"),
    R("RA10", "Onega and White Sea petroglyphs (Karelia)", ROCK, "C&E Europe", "c. 4000-2000 BCE",
      iso=S("RU"), text=r"onega|white sea|karelia|zalavruga|besov|vyg|belomorsk"),
    R("RA11", "Ural rock paintings (pisanitsy)", ROCK, "C&E Europe", "Neolithic-Iron Age", iso=S("RU"),
      text=r"ural|pisanits|kapova|shulgan|ignatievka|sverdlovsk|chelyabinsk|perm|bashkort", wd="Ural pictograms"),
    R("RA12", "Kapova / Shulgan-Tash Palaeolithic cave art", ROCK, "C&E Europe", "c. 36,000-14,000 BP",
      iso=S("RU"), text=r"kapova|shulgan"),
    # --- Asia
    R("RA20", "Gobustan petroglyphs", ROCK, "Near East", "c. 12,000 BP onward", iso=S("AZ"), text=r"gobust|qobust"),
    R("RA21", "Arabian rock art (Ha'il, Shuwaymis, Bir Hima, Wadi Rum)", ROCK, "Near East", "Neolithic-pre-Islamic",
      iso=S("SA JO YE OM AE QA KW BH")),
    R("RA22", "Sasanian and Achaemenid rock reliefs", ROCK, "Near East", "6th c. BCE-7th c. CE", iso=S("IR IQ"),
      text=r"relief|naqsh|behistun|bisotun|taq-e bostan|taq-i bustan|firuzabad|bishapur|rostam|rustam", wd="Sasanian rock relief",
      relief=True),
    R("RA23", "Near Eastern and Anatolian rock art", ROCK, "Near East", "Neolithic-Iron Age", iso=S("IR IQ IL PS SY LB TR AM GE")),
    R("RA24", "Tamgaly / Semirechye petroglyphs", ROCK, "Central Asia", "Bronze Age-medieval", iso=S("KZ KG"),
      text=r"tamgal|eshkiolmes|saimaly|cholpon|almaty|semirech|zhetysu|jetisu|bayan-zhurek|issyk"),
    R("RA25", "Mongolian Altai petroglyphs", ROCK, "Central Asia", "c. 11,000 BP onward", iso=S("MN"),
      wd="Petroglyphic Complexes of the Mongolian Altai"),
    R("RA26", "Siberian and Altai rock art (Tomsk, Shishkino, Sikachi-Alyan, Kalbak-Tash)", ROCK, "Central Asia",
      "Neolithic-Iron Age", iso=S("RU"), bbox=(40, 80, 60, 180)),
    R("RA27", "Central Asian petroglyphs (Sarmishsay, Zarautsoy, Saimaly-Tash)", ROCK, "Central Asia",
      "Bronze Age-medieval", iso=S("KZ KG UZ TJ TM AF")),
    R("RA28", "Ladakh, Karakoram and Upper Indus petroglyphs", ROCK, "Himalaya", "Bronze Age-medieval",
      iso=S("IN PK CN NP BT"), text=r"ladakh|zanskar|kargil|leh\b|gilgit|chilas|karakoram|hunza|baltistan|upper indus|"
                                    r"himachal|spiti|tibet|xizang|ngari|mustang"),
    R("RA29", "Bhimbetka and Central Indian rock shelters", ROCK, "South Asia", "Mesolithic-historical", iso=S("IN"),
      text=r"bhimbetka|madhya pradesh|raisen|chambal|pachmarhi|bhopal|adamgarh|jaora|mirzapur|kaimur|vindhya|chhattisgarh|"
           r"uttar pradesh|kathotia|satkunda"),
    R("RA30", "South Indian rock art and petroglyphs (Edakkal, Kupgal, Hampi)", ROCK, "South Asia", "Neolithic-Iron Age",
      iso=S("IN"), text=r"kerala|karnataka|tamil nadu|andhra|telangana|edakkal|kupgal|hampi|bellary|ballari|sanganakallu|"
                        r"kudumiyan|kerala|odisha|goa|konkan|ratnagiri|maharashtra"),
    R("RA31", "Indian rock art (other)", ROCK, "South Asia", "Mesolithic-historical", iso=S("IN")),
    R("RA32", "Sri Lankan and Pakistani rock art", ROCK, "South Asia", "", iso=S("LK PK BD")),
    R("RA33", "Zuojiang Huashan rock paintings", ROCK, "China", "c. 5th c. BCE-2nd c. CE", iso=S("CN"),
      text=r"huashan|hua mountain|zuojiang|ningming|guangxi", wd="Rock Paintings of Hua Mountain"),
    R("RA34", "Helan, Yinshan and northern Chinese petroglyphs", ROCK, "China", "Neolithic-medieval", iso=S("CN"),
      text=r"helan|yinshan|ningxia|inner mongolia|nei mongol|xinjiang|altay|gansu|qinghai|heilongjiang"),
    R("RA35", "Southern Chinese rock art (Cangyuan, Lianyungang, Jiangjunya)", ROCK, "China", "", iso=S("CN TW HK MO")),
    R("RA36", "Korean petroglyphs (Bangudae, Cheonjeon-ri)", ROCK, "Korea", "Neolithic-Bronze Age", iso=S("KR KP")),
    R("RA37", "Japanese rock carvings (Fugoppe, Temiya)", ROCK, "Japan", "Jōmon-Kofun", iso=S("JP")),
    R("RA38", "Maros-Pangkep (Sulawesi) cave art", ROCK, "SE Asia", "c. 51,000 BP onward", iso=S("ID"),
      text=r"sulawesi|maros|pangkep|leang|muna"),
    R("RA39", "Borneo cave art (Sangkulirang-Mangkalihat)", ROCK, "SE Asia", "c. 40,000 BP onward", iso=S("ID MY BN"),
      text=r"borneo|kalimantan|sangkulirang|mangkalihat|sabah|sarawak|niah"),
    R("RA40", "Mainland and island SE Asian rock art", ROCK, "SE Asia", "", iso=S("TH MM KH LA VN MY PH ID TL SG")),
    # --- Africa
    R("RA50", "Saharan rock art (Tassili, Acacus, Messak, Ennedi, Aïr)", ROCK, "North Africa & Sahara",
      "c. 12,000 BP-historical", iso=S("DZ LY NE TD ML MR MA EH TN"), wd="Saharan rock art"),
    R("RA51", "Gilf Kebir and Uweinat (Eastern Sahara) rock art", ROCK, "North Africa & Sahara", "Holocene",
      iso=S("EG SD LY"), text=r"gilf|uweinat|swimmers|beasts|wadi sura|foggini|jebel"),
    R("RA52", "Egyptian and Nubian rock art (Eastern Desert, Wadi Hammamat, Nile cataracts)", ROCK, "Egypt & Nubia",
      "Predynastic-pharaonic", iso=S("EG SD SS")),
    R("RA53", "Horn of Africa rock art (Laas Geel, Dhambalin)", ROCK, "Sub-Saharan Africa", "c. 5000-1000 BCE",
      iso=S("SO ET ER DJ")),
    R("RA54", "San (Bushman) rock art", ROCK, "Sub-Saharan Africa", "c. 27,000 BP-19th c.",
      iso=S("ZA LS BW NA ZW SZ"), wd="Rock art of the Bushmen"),
    R("RA55", "Central and East African rock art (Kondoa, Chongoni, Nyero)", ROCK, "Sub-Saharan Africa", "",
      iso=S("TZ MW UG KE ZM MZ AO CD RW BI CF CG GA CM")),
    R("RA56", "West African rock art", ROCK, "Sub-Saharan Africa", "", iso=S("NG GH BF CI GN SN SL LR TG BJ GM GW")),
    R("RA57", "Madagascar and Indian Ocean rock art", ROCK, "Sub-Saharan Africa", "", iso=S("MG MU KM SC")),
    # --- Australia (bbox/text before the catch-all)
    R("RA60", "Kimberley rock art (Gwion Gwion / Bradshaw, Wanjina)", ROCK, "Aboriginal Australia", "c. 17,000 BP onward",
      iso=S("AU"), text=r"kimberley|gwion|bradshaw|wandjina|wanjina|mitchell plateau|drysdale|king edward",
      wd="Gwion Gwion rock art"),
    R("RA61", "Kimberley rock art (Gwion Gwion / Bradshaw, Wanjina)", ROCK, "Aboriginal Australia", "c. 17,000 BP onward",
      iso=S("AU"), bbox=AUS_KIMBERLEY),
    R("RA62", "Arnhem Land and Kakadu rock art", ROCK, "Aboriginal Australia", "c. 28,000 BP-20th c.", iso=S("AU"),
      text=r"arnhem|kakadu|ubirr|nourlangie|burrungkuy|injalak|nawarla|gabarnmung|kunwinjku|kunbarlanja|oenpelli"),
    R("RA63", "Arnhem Land and Kakadu rock art", ROCK, "Aboriginal Australia", "c. 28,000 BP-20th c.", iso=S("AU"),
      bbox=AUS_NT_TOP),
    R("RA64", "Murujuga (Burrup) petroglyphs", ROCK, "Aboriginal Australia", "c. 40,000 BP onward", iso=S("AU"),
      text=r"murujuga|burrup|dampier|pilbara"),
    R("RA65", "Sydney Basin rock engravings", ROCK, "Aboriginal Australia", "Holocene", iso=S("AU"),
      text=r"sydney|ku-ring-gai|hawkesbury|central coast|blue mountains|brisbane water|wollemi|royal national park|"
           r"new south wales|nsw|gosford|hornsby|warringah|northern beaches|sutherland"),
    R("RA66", "Quinkan / Laura (Cape York) rock art", ROCK, "Aboriginal Australia", "", iso=S("AU"),
      text=r"laura|quinkan|cape york|queensland|carnarvon"),
    R("RA67", "Victorian and Grampians (Gariwerd) rock art", ROCK, "Aboriginal Australia", "", iso=S("AU"),
      text=r"grampians|gariwerd|victoria"),
    R("RA68", "Flinders Ranges and South Australian rock art", ROCK, "Aboriginal Australia", "", iso=S("AU"),
      text=r"flinders|south australia|koonalda|panaramitee|olary|yourambulla"),
    R("RA69", "Tasmanian rock art", ROCK, "Aboriginal Australia", "", iso=S("AU"), text=r"tasmania|preminghana"),
    R("RA70", "Central Australian rock art (Uluru, Ewaninga)", ROCK, "Aboriginal Australia", "", iso=S("AU"),
      text=r"uluru|kata tjuta|northern territory|ewaninga|n'dhala|alice springs|macdonnell"),
    R("RA71", "Aboriginal rock art (other)", ROCK, "Aboriginal Australia", "", iso=S("AU"), wd="Aboriginal rock painting"),
    # --- Oceania
    R("RA75", "Rapa Nui petroglyphs", ROCK, "Oceania", "", iso=S("CL"), text=r"rapa nui|easter island|orongo|isla de pascua"),
    R("RA76", "Hawaiian petroglyphs (ki'i pōhaku)", ROCK, "Oceania", "", iso=S("US"), text=r"hawai|puako|pu'u loa|puu loa|maui|kauai|oahu"),
    R("RA77", "Māori rock art", ROCK, "Oceania", "", iso=S("NZ")),
    R("RA78", "Melanesian and Pacific rock art", ROCK, "Oceania", "", iso=S("PG FJ VU SB NC PF WS TO FM PW GU MP")),
    # --- North America
    R("RA80", "Barrier Canyon Style", ROCK, "N. America Indigenous", "c. 4000-1500 BCE (disputed)", iso=S("US"),
      text=r"barrier canyon|horseshoe canyon|great gallery|sego|buckhorn wash", wd="Barrier Canyon Style"),
    R("RA81", "Chumash rock painting", ROCK, "N. America Indigenous", "c. 1000-1800 CE", iso=S("US"),
      text=r"chumash|santa barbara|painted cave|carrizo|painted rock|san luis obispo|ventura", wd="Rock art of the Chumash people"),
    R("RA82", "Coso Range rock art", ROCK, "N. America Indigenous", "", iso=S("US"), text=r"\bcoso\b|china lake|little petroglyph"),
    R("RA83", "Great Basin rock art", ROCK, "N. America Indigenous", "", iso=S("US"),
      text=r"nevada|great basin|owens|oregon|idaho|grimes point|mono county|inyo|lagomarsino"),
    R("RA84", "Lower Pecos rock art", ROCK, "N. America Indigenous", "c. 2500 BCE onward", iso=S("US"),
      text=r"pecos|white shaman|seminole canyon|val verde|panther cave|texas"),
    R("RA85", "Colorado Plateau and Southwest rock art (Ancestral Puebloan, Fremont, Hohokam)", ROCK,
      "N. America Indigenous", "", iso=S("US"),
      text=r"utah|colorado|arizona|new mexico|four corners|newspaper rock|petroglyph national|nine mile|pueblo|anasazi|"
           r"hohokam|fremont|mogollon|three rivers|chaco|canyon de chelly|mesa verde|albuquerque"),
    R("RA86", "California rock art (other)", ROCK, "N. America Indigenous", "", iso=S("US"), text=r"californ"),
    R("RA87", "Plains and Rocky Mountain rock art (Writing-on-Stone)", ROCK, "N. America Indigenous", "",
      iso=S("US CA"), text=r"alberta|writing-on-stone|saskatchewan|montana|wyoming|dakota|nebraska|kansas|manitoba|oklahoma"),
    R("RA88", "Pacific Northwest rock art", ROCK, "N. America Indigenous", "", iso=S("US CA"),
      text=r"washington|british columbia|alaska|columbia river|yukon"),
    R("RA89", "Canadian Shield and Eastern Woodlands rock art", ROCK, "N. America Indigenous", "", iso=S("US CA")),
    R("RA90", "Great Murals of Baja California", ROCK, "N. America Indigenous", "c. 1100 BCE-1300 CE", iso=S("MX"),
      text=r"baja|sierra de san francisco|mulegé|mulege|sierra de guadalupe|cochim"),
    R("RA91", "Mesoamerican and Mexican rock art", ROCK, "Mesoamerica", "", iso=S("MX GT BZ HN SV NI CR PA")),
    # --- South America & Caribbean
    R("RA95", "Serra da Capivara and Brazilian Nordeste rock art", ROCK, "South America", "c. 12,000 BP onward",
      iso=S("BR"), text=r"capivara|piau|nordeste|serid|pernambuco|bahia|rio grande do norte|para[ií]ba|catimbau|pedra furada"),
    R("RA96", "Amazonian and Orinoco petroglyphs (Chiribiquete, Monte Alegre)", ROCK, "South America", "",
      iso=S("BR CO VE GY SR GF"), text=r"amazon|par[aá]\b|roraima|chiribiquete|guaviare|orinoco|monte alegre|amazonas|caquet"),
    R("RA97", "Patagonian rock art (Cueva de las Manos, Río Pinturas)", ROCK, "South America", "c. 9300 BP onward",
      iso=S("AR CL"), text=r"manos|santa cruz|patagoni|pinturas|ays[eé]n|magallanes|chubut|neuqu|r[ií]o negro"),
    R("RA98", "Andean rock art (Toro Muerto, Chile's Norte Grande)", ROCK, "South America", "",
      iso=S("PE BO EC CL AR CO")),
    R("RA99", "Brazilian and southern South American rock art (other)", ROCK, "South America", "", iso=S("BR UY PY VE GY SR")),
    R("RA100", "Caribbean (Taíno) petroglyphs", ROCK, "Caribbean", "c. 600-1500 CE",
      iso=S("PR DO CU JM HT VG VI LC VC GD AG DM KN BS TT GP MQ AW CW BB")),

    # ======================= GEOGLYPHS =======================
    R("GL01", "Nazca and Palpa lines", GEO, "South America", "c. 500 BCE-500 CE", iso=S("PE"),
      text=r"nazca|nasca|palpa|paracas", wd="Nazca Lines"),
    R("GL02", "Atacama geoglyphs (Tarapacá, Pintados)", GEO, "South America", "c. 600-1500 CE", iso=S("CL"),
      text=r"atacama|tarapac|pintados|chug|unita|giant|lluta|azapa|tiliviche"),
    R("GL03", "Andean geoglyphs (other)", GEO, "South America", "", iso=S("PE BO CL AR")),
    R("GL04", "Amazonian (Acre) geoglyphs", GEO, "South America", "c. 0-1300 CE", iso=S("BR BO")),
    R("GL05", "English chalk hill figures", GEO, "Western Europe", "Bronze Age-19th c.", iso=S("GB IE"),
      text=r"uffington|cerne|long man|white horse|chalk|hill figure|giant|kilburn|westbury|wilmington", wd="hill figure"),
    R("GL06", "Steppe geoglyphs (Turgai)", GEO, "Central Asia", "Neolithic-Iron Age", iso=S("KZ RU"), wd="Steppe Geoglyph"),
    R("GL07", "Arabian desert kites and mustatils", GEO, "Near East", "Neolithic", iso=S("JO SA SY IL AE OM YE")),
    R("GL08", "North American intaglios and effigy figures (Blythe)", GEO, "N. America Indigenous", "", iso=S("US CA"),
      before=1800, undated_ok=True),
    R("GL09", "Gozan no Okuribi (Kyoto bonfire characters)", GEO, "Japan", "Edo period onward", iso=S("JP"),
      wd="Gozan no Okuribi"),
    R("GL10", "Modern land art", GEO, None, "1960s onward", years=(1950, 2100), wd="land art"),
    R("GL11", "Modern land art", GEO, None, "1960s onward", text=r"land art|earthwork|spiral jetty|lightning field"),

    # ======================= MOSAICS (before murals: works can be both) =======================
    R("MO01", "Ravenna Early Christian and Byzantine mosaics", MOSAIC, "Greco-Roman/Byzantine", "5th-6th c.",
      iso=S("IT"), text=r"ravenna|classe|galla placidia|san vitale|apollinare"),
    R("MO02", "Norman Sicilian mosaics (Palermo, Monreale, Cefalù)", MOSAIC, "Greco-Roman/Byzantine", "12th c.",
      iso=S("IT"), text=r"palermo|monreale|cefal|martorana|cappella palatina|sicil", years=(1000, 1300),
      undated_ok=True, wd="Byzantine mosaics of Sicily"),
    R("MO03", "Venetian Byzantine mosaics (San Marco, Torcello)", MOSAIC, "Greco-Roman/Byzantine", "11th-13th c.",
      iso=S("IT"), text=r"venezia|venice|san marco|st mark|torcello|murano"),
    R("MO04", "Cosmatesque pavements", MOSAIC, "Western Europe", "12th-13th c.", text=r"cosmat"),
    R("MO05", "Early Christian and medieval mosaics of Rome", MOSAIC, "Greco-Roman/Byzantine", "4th-13th c.",
      iso=S("IT"), text=r"\brom[ea]\b|vatican|lateran|santa maria maggiore|santa prassede|santa pudenziana|"
                        r"santi cosma|san clemente|santa costanza", years=(300, 1350), undated_ok=True),
    R("MO06", "Villa Romana del Casale and Roman Sicily mosaics", MOSAIC, "Greco-Roman/Byzantine", "4th c.",
      iso=S("IT"), text=r"armerina|casale|tellaro"),
    R("MO07", "Kyivan Rus' mosaics", MOSAIC, "C&E Europe", "11th-12th c.", iso=S("UA RU"),
      text=r"kyiv|kiev|sophia|mykhail|mikhail", years=(900, 1300), undated_ok=True),
    R("MO08", "Umayyad mosaics (Dome of the Rock, Great Mosque of Damascus)", MOSAIC, "Islamic world", "c. 690-750",
      text=r"dome of the rock|umayyad|damascus|mafjar|hisham|qasr|qusayr|cordoba|córdoba", iso=S("SY IL PS JO LB ES")),
    R("MO09", "Middle Byzantine mosaics (Hagia Sophia, Hosios Loukas, Daphni, Nea Moni)", MOSAIC, "Greco-Roman/Byzantine",
      "9th-12th c.", text=r"hagia sophia|ayasofya|hosios loukas|daphni|dafni|nea moni|chora|kariye|thessalon|"
                         r"pammakaristos|fethiye|vatopedi|athos", iso=S("TR GR CY")),
    R("MO10", "Byzantine mosaics (other)", MOSAIC, "Greco-Roman/Byzantine", "4th-15th c.",
      iso=S("TR GR CY IT IL PS JO SY LB EG GE AL MK BG RS"), years=(330, 1460), wd="Byzantine mosaics"),
    R("MO11", "Levantine church floor mosaics (Madaba school)", MOSAIC, "Greco-Roman/Byzantine", "4th-8th c.",
      iso=S("JO IL PS SY LB"), text=r"madaba|nebo|church|basilica|monaster|synagogue|umm ar|beth alpha|tabgha|sepphoris"),
    R("MO12", "Roman mosaics of the East (Antioch, Zeugma)", MOSAIC, "Greco-Roman/Byzantine", "2nd c. BCE-6th c. CE",
      iso=S("TR SY LB JO IL PS CY"), before=650, undated_ok=True),
    R("MO13", "Roman North African mosaics", MOSAIC, "Greco-Roman/Byzantine", "2nd-6th c.", iso=S("TN DZ LY MA"),
      before=700, undated_ok=True, notext=r"zellij|zellige|madrasa|mosque|medersa|palace"),
    R("MO14", "Hellenistic and Greek pebble mosaics", MOSAIC, "Greco-Roman/Byzantine", "5th-1st c. BCE",
      iso=S("GR MK AL"), before=0, wd="Hellenistic mosaic"),
    R("MO15", "Roman mosaics", MOSAIC, "Greco-Roman/Byzantine", "1st c. BCE-5th c. CE",
      text=r"roman|villa|domus|thermae|baths|pompei|herculan|ostia|aquileia", before=600, undated_ok=True, wd="Roman mosaic"),
    R("MO16", "Roman mosaics", MOSAIC, "Greco-Roman/Byzantine", "1st c. BCE-5th c. CE", years=(-200, 600), wd="Roman mosaic"),
    R("MO17", "Maghrebi and Andalusi zellige", MOSAIC, "Islamic world", "10th c. onward",
      iso=S("MA DZ TN ES LY"), text=r"zellij|zellige|madrasa|medersa|mosque|alhambra|bou inania|attarine|ben youssef|"
                                  r"palace|tile|alicatado|mezquita", wd="zellij"),
    R("MO18", "Persian and Timurid architectural tilework", MOSAIC, "Islamic world", "12th-19th c.",
      iso=S("IR UZ AF TM AZ TJ"), text=r"tile|kashi|mosque|madrasa|registan|shah-i-zinda|gur-e|mausoleum|shrine|"
                                    r"lotfollah|imam|caravanserai|haft rang|mu'arraq|moarraq"),
    R("MO19", "Ottoman Iznik tile revetments", MOSAIC, "Islamic world", "16th-17th c.", iso=S("TR"),
      text=r"tile|iznik|mosque|türbe|turbe|pasha|topkap|kiosk|köşk"),
    R("MO20", "Mughal and Punjabi tile mosaic (kashi kari)", MOSAIC, "Islamic world", "16th-18th c.", iso=S("PK IN"),
      text=r"tile|kashi|wazir khan|lahore|mosque|pietra dura|picture wall"),
    R("MO21", "Portuguese azulejo panels", MOSAIC, "Western Europe", "16th c. onward", iso=S("PT BR"), wd="azulejo"),
    R("MO22", "Spanish azulejo and alicatado", MOSAIC, "Western Europe", "", iso=S("ES"), text=r"azulejo|alicatado|tile|seville|sevilla"),
    R("MO23", "Catalan trencadís (modernisme)", MOSAIC, "Western Europe", "c. 1880-1930", iso=S("ES"),
      text=r"trencad|gaud[ií]|güell|guell|jujol|modernis", wd="trencadís"),
    R("MO24", "Soviet monumental mosaics", (MOSAIC, MURAL), "C&E Europe", "1920s-1991",
      iso=S("RU UA BY KZ UZ KG TJ TM AZ AM GE MD LT LV EE"), years=(1920, 1995), wd="Soviet mosaics"),
    R("MO25", "Portuguese pavement (calçada)", MOSAIC, "Western Europe", "19th c. onward", text=r"calçada|calcada|portuguese pavement",
      wd="Portuguese pavement"),
    R("MO26", "Medieval Western church mosaics", MOSAIC, "Western Europe", "", years=(600, 1500),
      iso=S("FR ES PT IT DE GB IE NL BE LU CH AT DK SE NO FI VA")),

    # ======================= MURALS / WALL PAINTING =======================
    # --- South Asia
    R("MU01", "Ajanta cave murals", MURAL, "South Asia", "2nd c. BCE-5th c. CE", iso=S("IN"), text=r"ajanta"),
    R("MU02", "Early Indian cave-temple murals (Bagh, Ellora, Badami, Sittanavasal)", MURAL, "South Asia", "5th-9th c.",
      iso=S("IN"), text=r"bagh caves|ellora|badami|sittanavasal|armamalai|bagh cave"),
    R("MU03", "Sigiriya frescoes", MURAL, "South Asia", "5th c.", iso=S("LK"), text=r"sigiriya"),
    R("MU04", "Kandyan-era temple frescoes (Dambulla, Degaldoruwa)", MURAL, "South Asia", "17th-19th c.", iso=S("LK"),
      wd="Kandyan Era Frescoes"),
    R("MU05", "Kerala mural painting", MURAL, "South Asia", "9th-19th c.", iso=S("IN"),
      text=r"kerala|mattancherry|padmanabhapuram|thrissur|ettumanoor|vadakkunnathan|travancore|kochi|cochin",
      wd="Kerala mural painting"),
    R("MU06", "Vijayanagara and Nayaka temple murals (Lepakshi, Hampi, Thanjavur)", MURAL, "South Asia", "11th-18th c.",
      iso=S("IN"), text=r"lepakshi|hampi|virupaksha|thanjavur|tanjore|brihadisvara|brihadeeswara|chidambaram|tamil nadu|"
                        r"karnataka|andhra|kanchipuram"),
    R("MU07", "Rajasthani haveli and palace murals (Shekhawati)", MURAL, "South Asia", "18th-20th c.", iso=S("IN"),
      text=r"shekhawati|haveli|rajasthan|jaipur|udaipur|bundi|jodhpur|bikaner|nawalgarh|mandawa"),
    R("MU08", "Western Himalayan Buddhist murals (Alchi, Tabo, Guge)", MURAL, "Himalaya", "10th-16th c.",
      iso=S("IN CN"), text=r"ladakh|alchi|tabo|spiti|lahaul|kinnaur|guge|tholing|tsaparang|zanskar|lamayuru|hemis|leh\b"),
    R("MU09", "Tibetan Buddhist wall painting", MURAL, "Himalaya", "7th c. onward", iso=S("CN IN NP BT MN"),
      text=r"tibet|xizang|lhasa|shalu|gyantse|samye|jokhang|potala|sakya|sikkim|arunachal|tawang|mustang|lo manthang|"
           r"bhutan|gompa|monaster|lamaser|dzong", wd="Tibetan Buddhist wall paintings"),
    R("MU10", "Nepalese and Bhutanese wall painting", MURAL, "Himalaya", "", iso=S("NP BT"), wd="Phallus paintings in Bhutan"),
    R("MU11", "Indian wall painting (other)", MURAL, "South Asia", "", iso=S("IN PK BD LK"), before=1900, undated_ok=True),
    # --- Central Asia & China & Korea & Japan
    R("MU15", "Kucha (Kizil) and Turfan (Bezeklik) cave murals", MURAL, "Central Asia", "3rd-13th c.", iso=S("CN"),
      text=r"kizil|kucha|kuqa|bezeklik|turfan|turpan|xinjiang|kumtura|kizilgaha|simsim|toyok|miran|khotan"),
    R("MU16", "Sogdian and Bactrian wall painting (Panjakent, Afrasiyab, Bamiyan)", MURAL, "Central Asia", "1st-9th c.",
      iso=S("UZ TJ AF TM KZ KG"), text=r"panjakent|penjikent|pendzhikent|afrasiyab|afrosiyob|samarkand|varakhsha|bamiyan|"
                                     r"balalyk|toprak|kalai|dilberjin|fayaz|kara tepe|sogd|bactri|ustrushana"),
    R("MU17", "Dunhuang (Mogao and Yulin) cave murals", MURAL, "China", "4th-14th c.", iso=S("CN"),
      text=r"dunhuang|mogao|yulin|western thousand buddha|anxi|guazhou"),
    R("MU18", "Chinese tomb murals", MURAL, "China", "Han-Ming", iso=S("CN"),
      text=r"tomb|mausoleum|qianling|zhanghuai|yide|yongtai|xianbei|mural tomb"),
    R("MU19", "Chinese Buddhist and Daoist temple murals (Yongle Palace, Fahai)", MURAL, "China", "Tang-Qing", iso=S("CN"),
      text=r"temple|yongle|fahai|monastery|palace|pilu|kaihua|yanshan|shanxi|hall"),
    R("MU20", "Chinese wall painting (other)", MURAL, "China", "", iso=S("CN TW HK MO"), before=1912, undated_ok=True),
    R("MU21", "Goguryeo tomb murals", MURAL, "Korea", "4th-7th c.", iso=S("KP KR CN"),
      text=r"goguryeo|koguryo|anak|gangseo|kangso|jian|ji'an|tomb of the dancers|muyongchong|anak tomb"),
    R("MU22", "Korean tomb and temple wall painting", MURAL, "Korea", "", iso=S("KR KP"), before=1910, undated_ok=True),
    R("MU23", "Japanese tomb and temple wall painting (Takamatsuzuka, Kitora, Hōryū-ji)", MURAL, "Japan", "7th-8th c.",
      iso=S("JP"), text=r"takamatsuzuka|kitora|h[oō]ry[uū]-?ji|kofun|decorated tomb|sohshoku|sōshoku|ozuka|chibusan|mezurashizuka"),
    R("MU24", "Japanese screen and wall painting (shōhekiga, fusuma-e)", MURAL, "Japan", "Muromachi-Edo", iso=S("JP"),
      text=r"fusuma|sh[oō]hekiga|shoheki|byōbu|byobu|nijō|nijo|daitoku|nanzen|kano|shoin", wd="shōhekiga"),
    R("MU25", "Japanese wall painting (other)", MURAL, "Japan", "", iso=S("JP"), before=1868, undated_ok=True),
    # --- SE Asia
    R("MU30", "Bagan temple murals", MURAL, "SE Asia", "11th-13th c.", iso=S("MM"), text=r"bagan|pagan|ananda|nyaung-u|minnanthu|myinkaba"),
    R("MU31", "Burmese temple murals (Konbaung, Ava, Sagaing)", MURAL, "SE Asia", "17th-19th c.", iso=S("MM")),
    R("MU32", "Thai temple murals", MURAL, "SE Asia", "Ayutthaya-Rattanakosin", iso=S("TH"), before=1950, undated_ok=True,
      wd="Thai temple art and architecture"),
    R("MU33", "Lao and Cambodian temple murals", MURAL, "SE Asia", "", iso=S("LA KH"), before=1950, undated_ok=True),
    R("MU34", "Indonesian and Vietnamese wall painting", MURAL, "SE Asia", "", iso=S("ID VN MY PH"), before=1900),
    # --- Egypt & Nubia, Aegean, Etruria, Rome
    R("MU40", "Egyptian tomb and temple painting", MURAL, "Egypt & Nubia", "c. 3100 BCE-4th c. CE", iso=S("EG"),
      before=400, undated_ok=True, notext=r"coptic|monaster|church|christian|mosque|cairo"),
    R("MU41", "Coptic monastic wall painting (Bawit, Red Monastery)", MURAL, "Egypt & Nubia", "4th-13th c.", iso=S("EG"),
      text=r"coptic|monaster|church|christian|anba|bawit|saqqara|red monastery|white monastery|deir"),
    R("MU42", "Nubian Christian wall painting (Faras)", MURAL, "Egypt & Nubia", "8th-14th c.", iso=S("SD SS EG"),
      text=r"faras|nubia|dongola|pachoras|abdallah|sonqi|banganarti"),
    R("MU43", "Aegean Bronze Age wall painting (Thera, Knossos)", MURAL, "Greco-Roman/Byzantine", "c. 1700-1200 BCE",
      iso=S("GR"), text=r"thera|akrotiri|santorini|knossos|minoan|crete|mycen|pylos|tiryns|amnisos|agia triada",
      before=-1000, undated_ok=True, wd="Wall Paintings of Thera"),
    R("MU44", "Macedonian and Thracian tomb painting (Vergina, Kazanlak, Sveshtari)", MURAL, "Greco-Roman/Byzantine",
      "4th-3rd c. BCE", iso=S("GR BG MK TR"), text=r"vergina|aigai|macedonian tomb|lefkadia|kazanlak|sveshtari|thracian|"
                                                 r"aleksandrovo|ostrusha|tomb of philip|persephone|agios athanasios"),
    R("MU45", "Paestum and Lucanian tomb painting", MURAL, "Greco-Roman/Byzantine", "5th-4th c. BCE", iso=S("IT"),
      text=r"paestum|diver|lucan|tomba del tuffatore"),
    R("MU46", "Etruscan tomb painting", MURAL, "Greco-Roman/Byzantine", "7th-2nd c. BCE", iso=S("IT"),
      text=r"etrusc|tarquinia|cerveteri|chiusi|vulci|orvieto|tomba d|tomb of the|necropol", before=0, undated_ok=True),
    R("MU47", "Roman wall painting (Pompeian Styles I-IV)", MURAL, "Greco-Roman/Byzantine", "2nd c. BCE-1st c. CE",
      text=r"pompei|herculan|stabia|oplont|boscoreale|boscotrecase|vesuvi|villa of the mysteries|villa dei misteri|"
           r"house of the|casa del|casa di|pompeian|farnesina|livia|domus aurea|augustus", before=200, undated_ok=True,
      wd="Pompeian Styles"),
    R("MU48", "Roman and late-antique wall painting (catacombs, provincial)", MURAL, "Greco-Roman/Byzantine",
      "1st-6th c.", before=650, wd="Roman wall painting",
      iso=S("IT VA FR ES PT DE GB AT CH HU HR SI RS BG RO GR TR CY IL PS JO SY LB TN LY DZ MA EG MK AL BA ME NL BE")),
    # --- Byzantine & Orthodox fresco
    R("MU50", "Cappadocian rock-cut church painting", MURAL, "Greco-Roman/Byzantine", "6th-13th c.", iso=S("TR"),
      text=r"cappadoc|g[oö]reme|ihlara|soğanlı|soganli|tokal|karanl|elmal|nevşehir|nevsehir|aksaray|ürgüp|urgup"),
    R("MU51", "Troödos painted churches (Cyprus)", MURAL, "Greco-Roman/Byzantine", "11th-16th c.", iso=S("CY"),
      wd="Painted Churches in the Troödos Region"),
    R("MU52", "Mount Athos and Late Byzantine Macedonian school (Panselinos)", MURAL, "Greco-Roman/Byzantine",
      "13th-16th c.", iso=S("GR"), text=r"athos|protaton|vatopedi|hilandar|chilandar|lavra|thessalon|panselinos|kastoria|veria|"
                                       r"meteora|mistra|mystras|peribleptos|pantanassa"),
    R("MU53", "Byzantine church painting (Greece, Anatolia)", MURAL, "Greco-Roman/Byzantine", "6th-15th c.",
      iso=S("GR TR"), before=1460, undated_ok=True),
    R("MU54", "Post-Byzantine Greek church painting (Cretan school)", MURAL, "Greco-Roman/Byzantine", "15th-19th c.",
      iso=S("GR CY"), years=(1453, 1900)),
    R("MU55", "Serbian medieval fresco (Raška, Morava schools)", MURAL, "C&E Europe", "12th-15th c.",
      iso=S("RS XK ME BA"), text=r"studenica|sopo[cć]ani|mile[sš]eva|gra[cč]anica|de[cč]ani|pe[cć]|bogorodica ljevi[sš]ka|"
                                  r"ravanica|kalenić|kalenic|manasija|resava|ljubostinja|monaster|church|žiča|zica|arilje|mora[cč]a"),
    R("MU56", "Macedonian (Ohrid) medieval fresco (Nerezi, Kurbinovo, St Sophia Ohrid)", MURAL, "C&E Europe",
      "11th-14th c.", iso=S("MK AL"), text=r"ohrid|nerezi|kurbinovo|prespa|prilep|markov|church|monaster|sv\.|st\."),
    R("MU57", "Bulgarian medieval fresco (Boyana, Ivanovo)", MURAL, "C&E Europe", "10th-17th c.", iso=S("BG"),
      text=r"boyana|ivanovo|rila|bachkovo|zemen|kremikovtsi|church|monaster|tarnovo|veliko|nessebar|nesebar",
      notext=r"thracian|kazanlak|sveshtari"),
    R("MU58", "Painted monasteries of Bukovina (northern Moldavia)", MURAL, "C&E Europe", "15th-16th c.", iso=S("RO"),
      text=r"vorone|moldovi|sucevi|humor|arbore|probota|p[aă]tr[aă]u[tţț]i|suceava|bucovina|bukovina|dragomirna|putna|"
           r"baia|r[aă]d[aă]u", wd="churches of Moldavia"),
    R("MU59", "Romanian church painting (Wallachia, Transylvania, Maramureș)", MURAL, "C&E Europe", "14th-19th c.",
      iso=S("RO MD"), before=1900, undated_ok=True),
    R("MU60", "Georgian medieval wall painting (Gelati, Ubisi, Svaneti)", MURAL, "C&E Europe", "9th-18th c.",
      iso=S("GE"), before=1900, undated_ok=True),
    R("MU61", "Armenian church wall painting", MURAL, "C&E Europe", "7th-18th c.", iso=S("AM"), before=1900, undated_ok=True),
    R("MU62", "Kyivan Rus' fresco (St Sophia, Kyiv)", MURAL, "C&E Europe", "11th-12th c.", iso=S("UA"),
      text=r"kyiv|kiev|sophia|chernihiv|vydubychi|kyrylivska|cyril", years=(900, 1300), undated_ok=True),
    R("MU63", "Russian medieval church fresco (Novgorod, Vladimir, Theophanes, Rublev, Dionisius)", MURAL, "C&E Europe",
      "12th-16th c.", iso=S("RU"), years=(1000, 1600), undated_ok=False),
    R("MU64", "Russian medieval church fresco (Novgorod, Vladimir, Theophanes, Rublev, Dionisius)", MURAL, "C&E Europe",
      "12th-16th c.", iso=S("RU"), text=r"novgorod|nereditsa|pskov|vladimir|staraya ladoga|ferapont|dionisi|rublev|theophanes|"
                                       r"feofan|volotovo|kovalevo|mirozh|bogolyubovo|dmitrievsky|kirillo"),
    R("MU65", "Yaroslavl and Muscovite church painting (17th c.)", MURAL, "C&E Europe", "17th c.", iso=S("RU"),
      years=(1600, 1800)),
    R("MU66", "Ukrainian, Belarusian and Polish-Lithuanian church painting", MURAL, "C&E Europe", "", iso=S("UA BY LT PL"),
      before=1850, undated_ok=False),
    # --- Islamic world
    R("MU70", "Umayyad palace painting (Qusayr 'Amra)", MURAL, "Islamic world", "8th c.", iso=S("JO SY IL PS"),
      text=r"amra|qusayr|qasr al-hayr|mafjar|umayyad|desert castle"),
    R("MU71", "Safavid and Qajar palace wall painting (Isfahan)", MURAL, "Islamic world", "16th-19th c.", iso=S("IR"),
      text=r"chehel|ali qapu|isfahan|esfahan|hasht behesht|qajar|safavid|golestan|tehran|kashan|shiraz"),
    R("MU72", "Islamic wall painting (other)", MURAL, "Islamic world", "", iso=ISLAMIC_ISO - S("IL"), years=(650, 1900)),
    # --- Western Europe
    R("MU80", "Catalan Romanesque wall painting (Taüll, Boí)", MURAL, "Western Europe", "11th-13th c.", iso=S("ES AD"),
      text=r"ta[uü]ll|bo[ií]|catalan|catalonia|catalunya|pyrene|lleida|girona|barcelona|andorra|pedret|esterri|"
           r"vall de bo|urgell", years=(900, 1300), undated_ok=True),
    R("MU81", "Romanesque wall painting", MURAL, "Western Europe", "10th-13th c.",
      iso=S("FR ES PT IT DE GB IE NL BE LU CH AT DK SE NO FI CZ PL SI HR SK HU"), years=(900, 1250)),
    R("MU82", "Gothic wall painting", MURAL, "Western Europe", "13th-15th c.",
      iso=S("FR ES PT DE GB IE NL BE LU CH AT DK SE NO FI CZ PL SI HR SK HU EE LV"), years=(1250, 1520), wd="Gothic mural"),
    R("MU83", "Istrian and Slovene Gothic frescoes (Beram, Hrastovlje)", MURAL, "C&E Europe", "14th-16th c.",
      iso=S("HR SI"), text=r"istri|beram|hrastovlje|pazin|buzet", wd="Gothic frescoes in Istria"),
    R("MU84", "Nordic church wall painting (kalkmålningar, Albertus Pictor)", MURAL, "Western Europe", "12th-16th c.",
      iso=S("SE DK FI NO"), before=1700, undated_ok=True),
    R("MU85", "Italian Trecento and Renaissance fresco (Giotto, Masaccio, Michelangelo)", MURAL, "Western Europe",
      "c. 1290-1600", iso=S("IT VA SM"), years=(1250, 1600)),
    R("MU86", "Italian medieval wall painting", MURAL, "Western Europe", "6th-13th c.", iso=S("IT VA SM"), years=(600, 1250)),
    R("MU87", "Baroque and Rococo ceiling and quadratura painting", MURAL, "Western Europe", "17th-18th c.",
      iso=S("IT VA FR ES PT DE AT CH BE NL GB CZ PL SK HU SI HR"), years=(1600, 1800)),
    R("MU88", "Lüftlmalerei (Alpine façade painting)", MURAL, "Western Europe", "18th-19th c.", iso=S("DE AT CH IT"),
      text=r"l[uü]ftl|oberammergau|mittenwald|façade|fassade|facade", wd="Lüftlmalerei"),
    R("MU89", "Scottish Renaissance painted ceilings", MURAL, "Western Europe", "16th-17th c.", iso=S("GB"),
      text=r"scotland|scottish|fife|edinburgh|aberdeen|crathes|culross|kinneil|stirling", years=(1500, 1700),
      undated_ok=True, wd="Scottish Renaissance painted ceilings"),
    R("MU90", "Western European wall and ceiling painting (other, pre-1850)", MURAL, "Western Europe", "",
      iso=S("FR ES PT IT DE GB IE NL BE LU CH AT DK SE NO FI IS MT VA"), years=(600, 1850)),
    R("MU91", "Central European wall and ceiling painting (pre-1850)", MURAL, "C&E Europe", "",
      iso=S("CZ PL SK HU SI HR LT LV EE"), years=(600, 1850)),
    # --- Americas
    R("MU95", "Murals of Bonampak", MURAL, "Mesoamerica", "c. 790 CE", iso=S("MX"), text=r"bonampak", wd="Murals of Bonampak"),
    R("MU96", "Teotihuacan mural painting (Tepantitla, Tetitla)", MURAL, "Mesoamerica", "c. 200-650 CE", iso=S("MX"),
      text=r"teotihuac|tepantitla|tetitla|atetelco|tlalocan"),
    R("MU97", "Cacaxtla and Epiclassic mural painting", MURAL, "Mesoamerica", "c. 650-900 CE", iso=S("MX"),
      text=r"cacaxtla|xochitecatl|tlaxcala"),
    R("MU98", "Maya mural painting (San Bartolo, Calakmul)", MURAL, "Mesoamerica", "c. 100 BCE-1500 CE",
      iso=S("MX GT BZ HN"), text=r"maya|san bartolo|calakmul|chilonch|tulum|chich[eé]n|uxmal|tikal|xultun|copan|yucat|campeche|chiapas|"
                                r"quintana|pet[eé]n|ek' balam|ek balam|mulchic", before=1550, undated_ok=True),
    R("MU99", "Mesoamerican mural painting (other)", MURAL, "Mesoamerica", "", iso=S("MX GT BZ HN SV"), before=1521),
    R("MU100", "Novohispanic convent murals (Actopan, Ixmiquilpan)", MURAL, "Mesoamerica", "16th-18th c.", iso=S("MX GT"),
      years=(1521, 1821)),
    R("MU101", "Novohispanic convent murals (Actopan, Ixmiquilpan)", MURAL, "Mesoamerica", "16th-18th c.", iso=S("MX"),
      text=r"ex-convento|exconvento|convento|convent|actopan|ixmiquilpan|epazoyucan|malinalco|huejotzingo|cuauhtinch"),
    R("MU102", "Mexican muralism", MURAL, "Mesoamerica", "1920s-1970s (modern)", iso=S("MX"),
      text=r"rivera|orozco|siqueiros|tamayo|o'gorman|muralism|muralismo|charlot|chávez morado|chavez morado|"
           r"palacio nacional|bellas artes|hospicio|san ildefonso|chapingo", wd="Mexican muralism"),
    R("MU103", "Mexican muralism", MURAL, "Mesoamerica", "1920s-1970s (modern)", iso=S("MX"), years=(1920, 1980),
      wd="Mexican muralism"),
    R("MU104", "Andean pre-Columbian mural painting (Moche, Lambayeque)", MURAL, "South America", "c. 100-1500 CE",
      iso=S("PE BO EC"), before=1532, undated_ok=False),
    R("MU105", "Andean pre-Columbian mural painting (Moche, Lambayeque)", MURAL, "South America", "c. 100-1500 CE",
      iso=S("PE"), text=r"huaca|moche|sipán|sipan|chan chan|pañamarca|panamarca|lambayeque|el brujo|cao viejo|ventarr"),
    R("MU106", "Andean colonial church murals (Andahuaylillas)", MURAL, "South America", "16th-18th c.",
      iso=S("PE BO EC CO"), years=(1532, 1830)),
    R("MU107", "Chilean muralism", MURAL, "South America", "1940s onward (modern)", iso=S("CL"), years=(1940, 2100),
      wd="Chilean muralism"),
    R("MU108", "Murals of Revolutionary Nicaragua", MURAL, "Mesoamerica", "1979-1990 (modern)", iso=S("NI"),
      years=(1975, 2000), wd="Murals of Revolutionary Nicaragua"),
    R("MU109", "Murals in Northern Ireland", MURAL, "Western Europe", "1970s onward (modern)", iso=S("GB IE"),
      text=r"belfast|derry|londonderry|northern ireland|falls road|shankill|bogside", wd="Murals in Northern Ireland"),
    # --- Africa
    R("MU115", "Ethiopian church wall painting (Gondarine, Lake Tana)", MURAL, "Sub-Saharan Africa", "12th-19th c.",
      iso=S("ET ER"), wd="Ethiopian art"),
    R("MU116", "Litema and Sotho / Ndebele house painting", MURAL, "Sub-Saharan Africa", "19th c. onward",
      iso=S("LS ZA"), text=r"litema|ndebele|sotho|basotho", wd="Litema"),
    R("MU117", "Swahili and East African wall painting", MURAL, "Sub-Saharan Africa", "", iso=S("KE TZ"), before=1900),

    # ======================= BODY ART (Wikidata items only) =======================
    R("BA01", "Tā moko (Māori)", BODY, "Oceania", "", text=r"moko|m[aā]ori", wd="tā moko"),
    R("BA02", "Polynesian tatau (Samoa, Tahiti, Marquesas, Hawai'i, Tonga, Fiji)", BODY, "Oceania", "",
      text=r"samoa|malu\b|pe['‘ʻ]a|tatau|marquesa|tahiti|polynesia|hawai|kakau|tonga|veiqia|fiji|uli\b|cook islands"),
    R("BA03", "Micronesian and Melanesian tattooing (Palau, PNG)", BODY, "Oceania", "",
      text=r"palau|micronesia|melanesia|papua|new guinea|solomon|vanuatu|carolin"),
    R("BA04", "Irezumi and Japanese tattooing (incl. hajichi, Ainu)", BODY, "Japan", "Jōmon onward",
      text=r"irezumi|tebori|japan|hajichi|ainu|okinawa|ryukyu|j[oō]mon", wd="irezumi"),
    R("BA05", "Mehndi (henna body art)", BODY, "South Asia", "", text=r"mehndi|mehendi|henna|mylanchi", wd="mehndi"),
    R("BA06", "Amazigh (Berber) tattooing", BODY, "North Africa & Sahara", "", text=r"berber|amazigh|kabyl|tuareg|siyala|chaoui"),
    R("BA07", "Deq (Kurdish and Arab facial tattooing)", BODY, "Near East", "", text=r"\bdeq\b|kurd|bedouin|arab", wd="Deq"),
    R("BA08", "African scarification traditions", BODY, "Sub-Saharan Africa", "",
      text=r"scarif|cicatri|nuba|\btiv\b|yoruba|dinka|nuer|ijaw|karo|surma|mursi|bétamarribé|betammaribe|tabwa|africa"),
    R("BA09", "Philippine and Bornean tattooing (batok, Iban)", BODY, "SE Asia", "",
      text=r"batok|batek|philippin|kalinga|visaya|pintados|iban|borneo|dayak|sarawak"),
    R("BA10", "Mainland and Indonesian SE Asian tattooing (sak yant, Mentawai, Chin)", BODY, "SE Asia", "",
      text=r"sak yant|yantra|thai|mentawai|indonesia|myanmar|burm|chin\b|shan|lao|rajah|khmer|cambodia"),
    R("BA11", "Inuit tattooing (kakiniit)", BODY, "N. America Indigenous", "", text=r"kakiniit|inuit|inupiat|yupik|tavlugun|arctic",
      wd="kakiniit"),
    R("BA12", "Indigenous North and South American body art", BODY, "N. America Indigenous", "",
      text=r"native american|first nations|haida|amazon|kayap|huni|genipa|jagua|american indigenous"),
    R("BA13", "Indian tattooing (godna, Naga, Apatani)", BODY, "South Asia", "", text=r"india|godna|apatani|konyak|naga|baiga|kutch"),
    R("BA14", "Chinese tattooing traditions (Dulong, Li)", BODY, "China", "", text=r"china|chinese|dulong|derung|\bli people|hainan|taiwan|atayal"),
    R("BA15", "Korean tattooing", BODY, "Korea", "", text=r"korea"),
    R("BA16", "Aboriginal Australian body painting", BODY, "Aboriginal Australia", "", text=r"aborigin|australia|yolngu|tiwi"),
    R("BA17", "Western sailor, prison and modern tattooing", BODY, "Western Europe", "18th c. onward (modern)",
      text=r"sailor|prison|olympic|american traditional|old school|neo-traditional|western|tribal|criminal|biker|military"),
    R("BA18", "Body painting traditions (general)", BODY, None, "", text=r"body paint|face ?paint"),
]


# ---------------------------------------------------------------- SPARQL plumbing
def q(query):
    """Cached SPARQL, one query at a time; returns None (recorded) on repeated failure."""
    h = hashlib.sha1(query.encode()).hexdigest()[:16]
    path = os.path.join(RAW, f"q_{h}.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    try:
        rows = sparql(query)
    except Exception as e:  # noqa: BLE001 - report and carry on
        print(f"    query failed ({type(e).__name__}: {e}); will retry on re-run")
        FAILED.append(query[:120])
        return None
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False)
    os.replace(tmp, path)
    return rows


def run_all(queries, label):
    out = []
    for i, query in enumerate(queries, 1):
        out.append(q(query) or [])
        if i % 25 == 0 or i == len(queries):
            print(f"  {label}: {i}/{len(queries)}", flush=True)
    return out


def chunks(items, n=CHUNK):
    items = list(items)
    return [items[i:i + n] for i in range(0, len(items), n)]


def values(qids):
    return " ".join("wd:" + x for x in qids)


def is_qid(x):
    return bool(x) and re.fullmatch(r"Q\d+", x) is not None


def lit(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"@en'


# ---------------------------------------------------------------- steps
def verify(force):
    expected = {qid: lab for qid, lab, _ in CLASSES.values()}
    expected.update(EXCLUDE)
    expected.update(HELPERS)
    got = {}
    for rows in run_all([f"""SELECT ?x ?l WHERE {{ VALUES ?x {{ {values(c)} }}
              ?x rdfs:label ?l FILTER(LANG(?l) = "en") }}""" for c in chunks(sorted(expected))], "verify labels"):
        got.update({r["x"]: r["l"] for r in rows})
    bad = [(x, lab, got.get(x)) for x, lab in expected.items() if (got.get(x) or "").lower() != lab.lower()]
    for x, lab, g in bad:
        print(f"  LABEL MISMATCH {x}: expected {lab!r}, Wikidata has {g!r}")
    if bad and not force:
        sys.exit("QID verification failed (pass --force to continue)")
    print(f"verified {len(expected) - len(bad)}/{len(expected)} class / helper QIDs by label")


def resolve_labels(labels, what):
    """Exact English label -> QID with the most sitelinks (skipping humans, categories, disambiguation pages)."""
    out = {}
    for ch in chunks(sorted(set(labels)), 60):
        rows = q(f"""SELECT ?l ?x ?sl WHERE {{ VALUES ?l {{ {' '.join(lit(s) for s in ch)} }} ?x rdfs:label ?l ;
                  wikibase:sitelinks ?sl . FILTER NOT EXISTS {{ ?x wdt:P31 wd:Q5 }}
                  FILTER NOT EXISTS {{ ?x wdt:P31 wd:Q4167836 }} FILTER NOT EXISTS {{ ?x wdt:P31 wd:Q4167410 }} }}""") or []
        best = {}
        for r in rows:
            lab, sl = r["l"], int(r["sl"])
            if lab not in best or sl > best[lab][1]:
                best[lab] = (r["x"], sl)
        out.update({k: v[0] for k, v in best.items()})
    missing = sorted(set(labels) - set(out))
    print(f"  {what}: resolved {len(out)}/{len(set(labels))} labels" + (f"; unresolved: {', '.join(missing)}" if missing else ""))
    return out


def excluded_items():
    """Instances (P31/P279*) of EXCLUDE classes."""
    ex = set()
    for rows in run_all([f"SELECT DISTINCT ?x WHERE {{ ?x wdt:P31/wdt:P279* wd:{c} }}" for c in sorted(EXCLUDE)],
                        "excluded classes"):
        ex.update(r["x"] for r in rows)
    return ex


def harvest():
    """Step 2: candidate sites -> {qid: set(class keys)}."""
    found = collections.defaultdict(set)
    keys = SITE_CLASSES
    for k, rows in zip(keys, run_all([f"SELECT DISTINCT ?x WHERE {{ ?x wdt:P31/wdt:P279* wd:{CLASSES[k][0]} }}"
                                      for k in keys], "class listings")):
        for r in rows:
            found[r["x"]].add(k)
    extra = [
        ("fresco_work", f"SELECT DISTINCT ?x WHERE {{ ?x wdt:P2079 wd:{FRESCO_TECHNIQUE[0]} }}"),
        ("mural", f"SELECT DISTINCT ?x WHERE {{ ?x wdt:P136 wd:{CLASSES['mural'][0]} }}"),
        ("rock_art", f"SELECT DISTINCT ?x WHERE {{ ?x wdt:P136 wd:{CLASSES['rock_art'][0]} }}"),
        ("land_art", f"SELECT DISTINCT ?x WHERE {{ ?x wdt:P136|wdt:P135 wd:{CLASSES['land_art'][0]} }}"),
        ("mosaic", f"SELECT DISTINCT ?x WHERE {{ ?x wdt:P136|wdt:P186 wd:{CLASSES['mosaic'][0]} }}"),
    ]
    for (k, _), rows in zip(extra, run_all([e[1] for e in extra], "technique / genre listings")):
        for r in rows:
            found[r["x"]].add(k)
    print(f"  {len(found)} items in site classes")
    return found


def unesco():
    """All World Heritage items with en label / description -> {qid: (label, desc)}."""
    rows = q("""SELECT ?s ?l ?d WHERE { { ?s wdt:P1435 wd:Q9259 } UNION { ?s wdt:P757 [] }
              OPTIONAL { ?s rdfs:label ?l FILTER(LANG(?l) = "en") } OPTIONAL { ?s schema:description ?d FILTER(LANG(?d) = "en") } }""") or []
    whs = {}
    for r in rows:
        whs[r["s"]] = (r.get("l", ""), r.get("d", ""))
    print(f"  {len(whs)} World Heritage items")
    return whs


def tradition_items():
    """Step 3: Wikidata items that are themselves in-situ traditions -> {qid: set(kinds)}."""
    trad = collections.defaultdict(set)
    roots = [k for k in CLASSES if k not in ("mosaic",)] + ["mosaic"]
    for k, rows in zip(roots, run_all([f"SELECT DISTINCT ?x WHERE {{ ?x wdt:P279+ wd:{CLASSES[k][0]} }}" for k in roots],
                                      "subclasses of class roots")):
        for r in rows:
            trad[r["x"]].add(CLASSES[k][2])
    for k in ("tattoo", "body_art", "body_painting", "scarification", "mehndi", "tattoo_style"):
        for r in q(f"SELECT DISTINCT ?x WHERE {{ ?x wdt:P31 wd:{CLASSES[k][0]} }}") or []:
            trad[r["x"]].add(BODY)
    # style-like items named after an in-situ medium (label or description), checked locally
    styles = {}
    for t in STYLE_TYPES:
        for r in q(f"""SELECT ?x ?l ?d WHERE {{ ?x wdt:P31 wd:{t} . OPTIONAL {{ ?x rdfs:label ?l FILTER(LANG(?l) = "en") }}
                   OPTIONAL {{ ?x schema:description ?d FILTER(LANG(?d) = "en") }} }}""") or []:
            styles[r["x"]] = (r.get("l", "") + " | " + r.get("d", "")).lower()
    n0 = len(trad)
    for x, text in styles.items():
        for kind, rx in KIND_RE.items():
            if re.search(rx, text):
                trad[x].add(kind)
    # keyword discovery through the Wikidata search API (via WDQS mwapi): classes only
    for term in ["tattooing", "tattoo tradition", "scarification", "body painting", "rock art", "rock paintings",
                 "petroglyphs", "cave paintings", "murals", "frescoes", "wall paintings", "mosaics", "geoglyphs",
                 "tilework", "painted churches", "haswbstatement:P279=Q43006", "haswbstatement:P279=Q1211146",
                 "haswbstatement:P279=Q219423", "haswbstatement:P279=Q133067"]:
        rows = q(f"""SELECT DISTINCT ?x ?l ?d WHERE {{ SERVICE wikibase:mwapi {{ bd:serviceParam wikibase:api "Search";
                  wikibase:endpoint "www.wikidata.org"; mwapi:srsearch "{term}"; mwapi:srlimit "max" .
                  ?x wikibase:apiOutputItem mwapi:title }}
                  {{ ?x wdt:P279 [] }} UNION {{ VALUES ?t {{ {values(STYLE_TYPES)} }} ?x wdt:P31 ?t }}
                  OPTIONAL {{ ?x rdfs:label ?l FILTER(LANG(?l) = "en") }} OPTIONAL {{ ?x schema:description ?d FILTER(LANG(?d) = "en") }} }}""") or []
        for r in rows:
            text = (r.get("l", "") + " | " + r.get("d", "")).lower()
            for kind, rx in KIND_RE.items():
                if re.search(rx, text):
                    trad[r["x"]].add(kind)
    print(f"  {len(trad)} Wikidata tradition items ({len(trad) - n0} from styles / search)")
    return trad


DETAIL_PROPS = ["P17", "P571", "P580", "P1319", "P1435", "P757", "P361", "P276", "P131", "P135", "P136", "P149",
                "P2596", "P2348", "P31", "P279", "P625", "P2079", "P495"]


def details(qids):
    claims = {x: collections.defaultdict(list) for x in qids}
    pv = " ".join("wdt:" + p for p in DETAIL_PROPS)
    for rows in run_all([f"""SELECT ?s ?prop ?v WHERE {{ VALUES ?s {{ {values(c)} }}
              VALUES ?prop {{ {pv} }} ?s ?prop ?v . }}""" for c in chunks(qids)], "claims"):
        for r in rows:
            p = r["prop"].rsplit("/", 1)[-1]
            if r["v"] not in claims[r["s"]][p]:
                claims[r["s"]][p].append(r["v"])
    meta = {}
    for rows in run_all([f"""SELECT ?s ?sl ?l ?d WHERE {{ VALUES ?s {{ {values(c)} }} ?s wikibase:sitelinks ?sl .
              OPTIONAL {{ ?s rdfs:label ?l FILTER(LANG(?l) = "en") }} OPTIONAL {{ ?s schema:description ?d FILTER(LANG(?d) = "en") }} }}"""
                         for c in chunks(qids)], "sitelinks / labels"):
        for r in rows:
            meta[r["s"]] = (int(r["sl"]), r.get("l", ""), r.get("d", ""))
    return claims, meta


def admin_chain(qids):
    """Labels of P131, P131/P131, P131/P131/P131 (fixed paths: cheap)."""
    out = collections.defaultdict(list)
    for rows in run_all([f"""SELECT ?s ?a1 ?a2 ?a3 WHERE {{ VALUES ?s {{ {values(c)} }} ?s wdt:P131 ?a1 .
              OPTIONAL {{ ?a1 wdt:P131 ?a2 . OPTIONAL {{ ?a2 wdt:P131 ?a3 }} }} }}""" for c in chunks(qids)], "admin chain"):
        for r in rows:
            for k in ("a1", "a2", "a3"):
                v = r.get(k)
                if is_qid(v) and v not in out[r["s"]]:
                    out[r["s"]].append(v)
    return out


def fetch_labels(qids):
    path = os.path.join(RAW, "labels.json")
    labels = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    todo = sorted({x for x in qids if is_qid(x)} - set(labels))
    for rows in run_all([f"""SELECT ?x (SAMPLE(?en) AS ?l) (SAMPLE(?any) AS ?a) WHERE {{ VALUES ?x {{ {values(c)} }}
              OPTIONAL {{ ?x rdfs:label ?en FILTER(LANG(?en) = "en") }} OPTIONAL {{ ?x rdfs:label ?any }} }} GROUP BY ?x"""
                         for c in chunks(todo, 400)], "labels"):
        for r in rows:
            labels[r["x"]] = r.get("l") or r.get("a") or ""
    tmp = path + ".tmp"
    json.dump(labels, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
    os.replace(tmp, path)
    return labels


def iso_codes(countries):
    out = {}
    for rows in run_all([f"SELECT ?c ?iso WHERE {{ VALUES ?c {{ {values(ch)} }} ?c wdt:P297 ?iso }}"
                         for ch in chunks(sorted(countries))], "ISO codes"):
        for r in rows:
            out.setdefault(r["c"], r["iso"])
    # constituent countries / historical states without P297: take the ISO code of their own P17
    todo = sorted(set(countries) - set(out))
    for rows in run_all([f"SELECT ?c ?iso WHERE {{ VALUES ?c {{ {values(ch)} }} ?c wdt:P17 ?k . ?k wdt:P297 ?iso }}"
                         for ch in chunks(todo)], "ISO codes via P17"):
        for r in rows:
            out.setdefault(r["c"], r["iso"])
    return out


def extra_claims(qids):
    """Collection (P195), population (P1082) and ISO code (P297): is a work museum-held, is a location a place?"""
    out = collections.defaultdict(set)
    for rows in run_all([f"""SELECT DISTINCT ?s ?p WHERE {{ VALUES ?s {{ {values(c)} }} VALUES ?p {{ wdt:P195 wdt:P1082 wdt:P297 }}
              ?s ?p [] . }}""" for c in chunks(qids)], "extra claims"):
        for r in rows:
            out[r["s"]].add(r["p"].rsplit("/", 1)[-1])
    return out


def museums(locs):
    out = set()
    for rows in run_all([f"""SELECT DISTINCT ?x WHERE {{ VALUES ?x {{ {values(c)} }} ?x wdt:P31/wdt:P279* wd:Q33506 }}"""
                         for c in chunks(sorted(locs))], "museum locations"):
        out.update(r["x"] for r in rows)
    return out


# ---------------------------------------------------------------- rules
def match(rule, c):
    if not (rule["kinds"] & c["kinds"]):
        return False
    if c.get("relief") and ROCK in rule["kinds"] and not rule.get("relief"):
        return False  # rock-cut relief sculpture only matches rules that ask for it
    if "iso" in rule and not (rule["iso"] & c["isos"]):
        return False
    if "text" in rule and not re.search(rule["text"], c["text"]):
        return False
    if "notext" in rule and re.search(rule["notext"], c["text"]):
        return False
    y = c["year"]
    if "years" in rule:
        if y is None:
            if not rule.get("undated_ok"):
                return False
        elif not rule["years"][0] <= y < rule["years"][1]:
            return False
    if "before" in rule:
        if y is None:
            if not rule.get("undated_ok"):
                return False
        elif y >= rule["before"]:
            return False
    if "bbox" in rule:
        if c["lat"] is None:
            return False
        a, b, lo, hi = rule["bbox"]
        if not (a <= c["lat"] <= b and lo <= c["lon"] <= hi):
            return False
    return True


def describe(rule):
    parts = ["kind=" + "/".join(sorted(rule["kinds"]))]
    if "iso" in rule:
        parts.append("country=" + " ".join(sorted(rule["iso"])))
    if "text" in rule:
        parts.append(f"text~/{rule['text'][:120]}/")
    if "notext" in rule:
        parts.append(f"not~/{rule['notext']}/")
    if "years" in rule:
        parts.append(f"years {rule['years'][0]}..{rule['years'][1]}" + (" or undated" if rule.get("undated_ok") else ""))
    if "before" in rule:
        parts.append(f"before {rule['before']}" + (" or undated" if rule.get("undated_ok") else ""))
    if "bbox" in rule:
        parts.append(f"bbox {rule['bbox']}")
    return "; ".join(parts)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--force", action="store_true", help="continue despite QID label mismatches")
    ap.add_argument("--per-tradition", type=int, default=10, help="exemplars listed per tradition in traditions.csv")
    args = ap.parse_args()
    os.makedirs(RAW, exist_ok=True)

    print("1. verify QIDs")
    verify(args.force)

    print("2. harvest candidates")
    found = harvest()
    excl = excluded_items()
    for x in list(found):
        if x in excl:
            del found[x]
    whs = unesco()
    whs_hit = {x for x, (l, d) in whs.items() if re.search(WHS_RE, (l + " | " + d).lower())}
    print(f"  {len(whs_hit)} World Heritage items match the in-situ keywords")
    seed_q = {}
    for kind, labs in SEEDS.items():
        for lab, x in resolve_labels(labs, f"seeds ({kind})").items():
            seed_q[x] = (kind, lab)

    print("3. Wikidata tradition items")
    trad = tradition_items()
    roots = {v[0] for v in CLASSES.values()}
    for x in list(trad):
        if x in EXCLUDE or x in excl or x in roots:  # class roots are media, not traditions
            del trad[x]
    rule_wd_labels = sorted({r["wd"] for r in RULES if r.get("wd")})
    rule_wd = resolve_labels(rule_wd_labels, "rule tradition items")

    print("4. details")
    body_seeds = {x for x, (k, _) in seed_q.items() if k == BODY}
    site_q = set(found) | whs_hit | {x for x in seed_q if x not in body_seeds}
    site_q -= set(trad)  # tradition (class-like) items are nodes, not sites
    all_q = sorted(site_q | set(trad) | body_seeds | set(rule_wd.values()))
    print(f"  {len(site_q)} candidate sites/works, {len(trad) + len(body_seeds)} tradition/body-art items")
    claims, meta = details(all_q)
    admin = admin_chain(sorted(site_q))

    locs = {v for x in site_q for v in claims[x].get("P276", []) if is_qid(v)}
    museum_locs = museums(locs)
    loc_claims, loc_meta = details(sorted(locs - set(all_q)))
    claims.update(loc_claims)
    meta.update(loc_meta)
    extra = extra_claims(sorted(site_q | locs))
    humans = {x for x in site_q if "Q5" in claims[x].get("P31", [])}
    site_q -= humans
    print(f"  dropped {len(humans)} humans (artists tagged with a land-art / mural movement)")

    want = set(all_q) | locs | set(whs_hit)
    for x in list(claims):
        for p in ("P17", "P1435", "P361", "P276", "P135", "P136", "P149", "P2596", "P2348", "P31", "P279"):
            want.update(claims[x].get(p, []))
    for v in admin.values():
        want.update(v)
    labels = fetch_labels(want)
    countries = {c for x in claims for c in claims[x].get("P17", []) if is_qid(c)}
    iso = iso_codes(countries)
    no_iso = collections.Counter(c for x in site_q for c in claims[x].get("P17", []) if is_qid(c) and c not in iso)

    def lab(x):
        return labels.get(x, "") or (meta.get(x, (0, "", ""))[1]) or x

    # ---- candidate records
    cls_by_qid = {v[0]: k for k, v in CLASSES.items()}
    whs_set = set(whs)

    def years_of(cl):
        for p in ("P571", "P580", "P1319"):
            ys = sorted(y for y in (year_of(v) for v in cl.get(p, [])) if y is not None)
            if ys:
                return ys[0], p
        return None, ""

    def kinds_of(x):
        ks = {CLASSES[k][2] for k in found.get(x, set())}
        cl = claims.get(x, {})
        for v in cl.get("P31", []) + cl.get("P279", []):
            if v in cls_by_qid:
                ks.add(CLASSES[cls_by_qid[v]][2])
        if not ks:
            text = (meta.get(x, (0, "", ""))[1] + " | " + meta.get(x, (0, "", ""))[2]).lower()
            ks = {k for k, rx in KIND_RE.items() if k != BODY and re.search(rx, text)}
        if not ks and x in seed_q:
            ks = {seed_q[x][0]}
        return ks

    cands = []
    for x in sorted(site_q):
        cl = claims[x]
        sl, l_en, desc = meta.get(x, (0, "", ""))
        kinds = kinds_of(x) - {BODY}
        if GEO in kinds:
            kinds.discard(ROCK)  # Wikidata files geoglyphs and hill figures under rock art
        if not kinds:
            continue  # WHS keyword hit whose wording turned out not to be about in-situ art
        y, ysrc = years_of(cl)
        m = re.match(r"Point\(([-\d.eE]+) ([-\d.eE]+)\)", (cl.get("P625") or [""])[0])
        is_work = bool(found.get(x, set()) & WORK_CLASSES) or "fresco_work" in found.get(x, set())
        loc = next((v for v in cl.get("P276", []) if is_qid(v)), "")
        in_museum = bool(loc and loc in museum_locs) or (is_work and not loc and "P195" in extra.get(x, set()))
        # a location that is a populated place or country is not a site: keep the work itself then
        loc_is_place = bool(loc) and bool(extra.get(loc, set()) & {"P1082", "P297"})
        site = loc if is_work and loc and not in_museum and not loc_is_place else x
        parts = [p for p in cl.get("P361", []) if is_qid(p)]
        site_cl = claims.get(site, cl)
        site_parts = parts + [p for p in site_cl.get("P361", []) if is_qid(p) and p not in parts]
        unesco_part = next((p for p in site_parts if p in whs_set), "")
        her = set(cl.get("P1435", [])) | (set(site_cl.get("P1435", [])) if site != x else set())
        is_whs = site in whs_set or x in whs_set or "Q9259" in her
        part_whs = bool(unesco_part) or "Q43113623" in her
        loc_cl = claims.get(loc, {}) if loc else {}
        ctys = [c for c in cl.get("P17", []) if is_qid(c)] or [c for c in site_cl.get("P17", []) if is_qid(c)] or \
            [c for c in loc_cl.get("P17", []) if is_qid(c)] or [c for c in cl.get("P495", []) if is_qid(c)]
        isos = {iso[c] for c in ctys if c in iso}
        if y is None and site != x:
            y, ysrc = years_of(site_cl)
            ysrc = ysrc and "site " + ysrc
        place = [lab(a) for a in admin.get(x, [])]
        textbits = [l_en, desc, lab(site) if site != x else ""] + place + [lab(p) for p in site_parts] + \
                   [lab(v) for p in ("P2596", "P2348", "P135", "P136", "P149", "P31", "P279") for v in cl.get(p, []) if is_qid(v)]
        lat = float(m.group(2)) if m else None
        lon = float(m.group(1)) if m else None
        cands.append({
            "qid": x, "label": l_en or lab(x), "desc": desc, "kinds": kinds, "isos": isos,
            "countries": "|".join(lab(c) for c in ctys), "year": y, "year_src": ysrc, "lat": lat, "lon": lon,
            "text": " | ".join(t for t in textbits if t).lower(), "sitelinks": sl, "site": site, "is_work": is_work,
            "in_museum": in_museum, "is_whs": is_whs, "part_whs": part_whs, "unesco_site": unesco_part,
            "heritage": sorted(h for h in her if is_qid(h) and h not in ("Q9259", "Q43113623")),
            "wd_links": {v for p in ("P135", "P136", "P149", "P31", "P279", "P361") for v in cl.get(p, []) if v in trad},
            "place": "|".join(place),
            "relief": found.get(x, set()) == {"rock_relief"} or (
                "Q22022298" in cl.get("P31", []) and not found.get(x, set()) - {"rock_relief", "rock_art"}),
        })
    print(f"  {len(cands)} candidate records")

    # ---- body-art items as candidates (traditions themselves; not sites)
    body = []
    for x in sorted({t for t, ks in trad.items() if BODY in ks} | body_seeds):
        sl, l_en, desc = meta.get(x, (0, "", ""))
        cl = claims.get(x, {})
        txt = " | ".join([l_en, desc] + [lab(v) for p in ("P17", "P2596", "P31", "P279", "P495") for v in cl.get(p, [])
                                         if is_qid(v)]).lower()
        if re.search(r"medical|surgical|cornea|scleral|make-up|makeup|fictional|electronic|uv tattoo|temporary|air show|"
                     r"airshow|military|germination|seed|\bdye\b|wikimedia|film|album|song|festival", (l_en + " | " + desc).lower()):
            continue
        body.append({"qid": x, "label": l_en or lab(x), "desc": desc, "kinds": {BODY}, "isos": {iso[c] for c in cl.get("P17", []) if c in iso},
                     "countries": "|".join(lab(c) for c in cl.get("P17", []) if is_qid(c)), "year": None, "year_src": "",
                     "lat": None, "lon": None, "text": txt, "sitelinks": sl, "site": x, "is_work": False, "in_museum": False,
                     "is_whs": False, "part_whs": False, "unesco_site": "", "heritage": [], "wd_links": set(), "place": ""})

    # ---- apply rules
    def primary_kind(c):
        return next(k for k in KINDS if k in c["kinds"])

    for c in cands + body:
        c["rule"] = next((r for r in RULES if match(r, c)), None)
        r = c["rule"]
        iso0 = sorted(c["isos"])[0] if c["isos"] else ""
        c["kind"] = next((k for k in KINDS if k in (r["kinds"] & c["kinds"])), None) if r else primary_kind(c)
        if r:
            c["tradition"] = r["tradition"]
            c["region"] = r["region"] or default_region(iso0, c["year"], c["kind"], c["lon"]) or "unknown"
            if not r["region"]:
                c["tradition"] += f" ({c['region']})"
        else:
            cname = c["countries"].split("|")[0] if c["countries"] else "no country"
            kname = "rock relief" if c.get("relief") else c["kind"]
            c["tradition"] = f"{kname} - {cname} ({era_bucket(c['year'])})" if c["kind"] != BODY else f"{c['label']} (body art)"
            c["region"] = default_region(iso0, c["year"], c["kind"], c["lon"]) or "unknown"

    # ---- site-level exemplars (works roll up to their location)
    def tier(c):
        return 0 if c["is_whs"] else 1 if c["part_whs"] else 2 if c["heritage"] else 3

    sites = {}
    for c in cands:
        key = (c["site"], c["tradition"])
        s = sites.get(key)
        site_sl = meta.get(c["site"], (c["sitelinks"],))[0]
        if s is None:
            s = sites[key] = {"site_qid": c["site"], "site": lab(c["site"]) if c["site"] != c["qid"] else c["label"],
                              "tradition": c["tradition"], "kind": c["kind"], "region": c["region"],
                              "country": c["countries"], "years": [], "is_whs": False, "part_whs": False, "heritage": set(),
                              "unesco_site": c["unesco_site"], "sitelinks": site_sl, "n_works": 0, "works": [],
                              "in_museum": c["in_museum"], "rule": c["rule"]["id"] if c["rule"] else "fallback",
                              "place": c["place"], "kinds": set(), "desc": c["desc"] if c["site"] == c["qid"] else ""}
        s["kinds"] |= c["kinds"]
        if c["year"] is not None:
            s["years"].append(c["year"])
        s["is_whs"] |= c["is_whs"]
        s["part_whs"] |= c["part_whs"]
        s["heritage"] |= set(c["heritage"])
        s["unesco_site"] = s["unesco_site"] or c["unesco_site"]
        if c["is_work"]:
            s["n_works"] += 1
            if len(s["works"]) < 5:
                s["works"].append(f"{c['label']} ({c['qid']})")
    srows = list(sites.values())
    for s in srows:
        s["tier"] = 0 if s["is_whs"] else 1 if s["part_whs"] else 2 if s["heritage"] else 3
    srows.sort(key=lambda s: (s["tradition"], s["in_museum"], s["tier"], -s["sitelinks"], s["site_qid"]))

    # ---- tradition items: link to rule nodes or stand alone
    rule_by_trad = {}
    for r in RULES:
        rule_by_trad.setdefault(r["tradition"], r)
    trad_qid = {}
    for r in RULES:
        if r.get("wd") and r["wd"] in rule_wd:
            trad_qid.setdefault(r["tradition"], rule_wd[r["wd"]])
    for c in cands + body:  # rules without a fixed region name one node per region
        if c["rule"]:
            rule_by_trad.setdefault(c["tradition"], c["rule"])
            if c["rule"].get("wd") in rule_wd:
                trad_qid.setdefault(c["tradition"], rule_wd[c["rule"]["wd"]])
    linked_items = collections.defaultdict(set)  # tradition label -> Wikidata items linked via its sites
    wd_sites = collections.defaultdict(set)      # wikidata tradition item -> sites linking to it
    for c in cands:
        for t in c["wd_links"]:
            wd_sites[t].add(c["site"])
            linked_items[c["tradition"]].add(t)
    body_by_qid = {b["qid"]: b for b in body}

    # ---- traditions CSV
    by_trad = collections.defaultdict(list)
    for s in srows:
        by_trad[s["tradition"]].append(s)
    trows = []
    for t, ss in by_trad.items():
        in_place = [s for s in ss if not s["in_museum"]]
        ys = sorted(y for s in in_place for y in s["years"])
        r = rule_by_trad.get(t)
        regions = collections.Counter(s["region"] for s in ss)
        ctys = collections.Counter(c for s in ss for c in s["country"].split("|") if c)
        top = [s for s in ss if not s["in_museum"]][:args.per_tradition]
        q_ = trad_qid.get(t, "")
        trows.append({
            "label": t, "qid": q_, "qid_label": lab(q_) if q_ else "", "kind": ss[0]["kind"],
            "region": regions.most_common(1)[0][0], "country": "|".join(f"{c} ({n})" for c, n in ctys.most_common(5)),
            "era": r["era"] if r else "", "year_min": ys[0] if ys else "", "year_max": ys[-1] if ys else "",
            "n_sites": len(in_place), "n_unesco": sum(1 for s in in_place if s["is_whs"] or s["part_whs"]),
            "n_heritage": sum(1 for s in in_place if s["tier"] <= 2), "n_works": sum(s["n_works"] for s in ss),
            "n_museum_works": sum(s["n_works"] for s in ss if s["in_museum"]),
            "sum_sitelinks": sum(s["sitelinks"] for s in in_place),
            "top_exemplars": " | ".join(f"{s['site']} ({s['site_qid']})" for s in top),
            "wikidata_items_linked": "|".join(f"{lab(x)} ({x})" for x in sorted(linked_items.get(t, set()))[:8]),
            "node_source": "rule" if r else "fallback (kind x country x era)",
            "rules": "|".join(sorted({s["rule"] for s in ss})),
            "sources": "Wikidata classes/P2079/P136" + ("; UNESCO WHS" if any(s["is_whs"] or s["part_whs"] for s in ss) else "")
                       + ("; seed labels" if any(s["site_qid"] in seed_q for s in ss) else ""),
        })
    # body-art traditions (Wikidata items only): grouped by rule, each item listed
    by_btrad = collections.defaultdict(list)
    for b in body:
        by_btrad[b["tradition"]].append(b)
    for t, bs in by_btrad.items():
        bs.sort(key=lambda b: -b["sitelinks"])
        r = rule_by_trad.get(t)
        q_ = trad_qid.get(t, "") or (bs[0]["qid"] if not r else "")
        trows.append({
            "label": t, "qid": q_, "qid_label": lab(q_) if q_ else "", "kind": BODY, "region": bs[0]["region"],
            "country": "|".join(sorted({c for b in bs for c in b["countries"].split("|") if c}))[:200],
            "era": r["era"] if r else "", "year_min": "", "year_max": "", "n_sites": 0, "n_unesco": 0, "n_heritage": 0,
            "n_works": 0, "n_museum_works": 0, "sum_sitelinks": sum(b["sitelinks"] for b in bs),
            "top_exemplars": " | ".join(f"{b['label']} ({b['qid']}, sl {b['sitelinks']})" for b in bs[:args.per_tradition]),
            "wikidata_items_linked": "|".join(f"{b['label']} ({b['qid']})" for b in bs[:8]),
            "node_source": "rule" if r else "wikidata item", "rules": r["id"] if r else "",
            "sources": "Wikidata items (tattoo / body art / scarification / mehndi classes, seed labels)",
        })
    # Wikidata in-situ tradition items not already the qid of a node: listed for classifying
    used = {t["qid"] for t in trows if t["qid"]} | set(body_by_qid)
    for x, ks in sorted(trad.items()):
        if x in used or BODY in ks and not (ks - {BODY}):
            continue
        sl, l_en, desc = meta.get(x, (0, "", ""))
        if re.search(r"photograph|satellite|orthophoto|rubik|wikimedia", (l_en + desc).lower()):
            continue
        linked = sorted(wd_sites.get(x, set()))
        kind = next(k for k in KINDS if k in ks)
        cl = claims.get(x, {})
        ctys = [lab(c) for c in cl.get("P17", []) + cl.get("P495", []) if is_qid(c)]
        trows.append({
            "label": l_en or lab(x), "qid": x, "qid_label": l_en or lab(x), "kind": kind,
            "region": "", "country": "|".join(ctys), "era": "", "year_min": "", "year_max": "",
            "n_sites": len(linked), "n_unesco": 0, "n_heritage": 0, "n_works": 0, "n_museum_works": 0, "sum_sitelinks": sl,
            "top_exemplars": " | ".join(f"{lab(s)} ({s})" for s in linked[:args.per_tradition]),
            "wikidata_items_linked": desc[:150], "node_source": "wikidata item (unmapped)", "rules": "",
            "sources": "Wikidata subclass / style item",
        })
    order = {k: i for i, k in enumerate(KINDS)}
    trows.sort(key=lambda t: (order[t["kind"]], t["node_source"].startswith("wikidata"), t["region"], -t["n_sites"], t["label"]))
    write_csv(os.path.join(OUT_DIR, "in_situ_traditions.csv"), trows)

    # ---- exemplars CSV
    erows = []
    for s in srows:
        ys = sorted(s["years"])
        erows.append({
            "site": s["site"], "qid": s["site_qid"], "tradition": s["tradition"], "kind": s["kind"],
            "region": s["region"], "country": s["country"], "date": ys[0] if ys else "",
            "unesco": "World Heritage Site" if s["is_whs"] else ("part of " + (lab(s["unesco_site"]) if s["unesco_site"] else "WHS"))
            if s["part_whs"] else "",
            "heritage": "|".join(lab(h) for h in sorted(s["heritage"]))[:200], "sitelinks": s["sitelinks"],
            "tier": ["unesco_site", "part_of_unesco", "heritage", "none"][s["tier"]],
            "in_museum": int(s["in_museum"]), "n_works": s["n_works"], "works": " | ".join(s["works"]),
            "rule": s["rule"], "seed": int(s["site_qid"] in seed_q), "place": s["place"][:150], "description": s["desc"][:150],
        })
    for b in sorted(body, key=lambda b: (b["tradition"], -b["sitelinks"])):
        erows.append({"site": b["label"], "qid": b["qid"], "tradition": b["tradition"], "kind": BODY, "region": b["region"],
                      "country": b["countries"], "date": "", "unesco": "", "heritage": "", "sitelinks": b["sitelinks"],
                      "tier": "none", "in_museum": 0, "n_works": 0, "works": "", "rule": b["rule"]["id"] if b["rule"] else "fallback",
                      "seed": int(b["qid"] in seed_q), "place": "", "description": b["desc"][:150]})
    write_csv(os.path.join(OUT_DIR, "in_situ_exemplars.csv"), erows)

    # ---- rules CSV
    n_rule = collections.Counter(s["rule"] for s in srows)
    n_rule.update(b["rule"]["id"] for b in body if b["rule"])
    rule_rows = [{"rule": r["id"], "tradition": r["tradition"], "kind": "/".join(sorted(r["kinds"])),
                  "region": r["region"] or "(from country)", "era": r["era"], "conditions": describe(r),
                  "wikidata_item": f"{r['wd']} ({rule_wd.get(r['wd'], 'unresolved')})" if r.get("wd") else "",
                  "n_matched": n_rule.get(r["id"], 0)} for r in RULES]
    write_csv(os.path.join(OUT_DIR, "in_situ_rules.csv"), rule_rows)

    # ---- coverage per world region x kind
    cov = collections.defaultdict(lambda: collections.Counter())
    for t in trows:
        if t["node_source"].startswith("wikidata item (unmapped)"):
            continue
        cov[t["region"]][t["kind"] + " nodes"] += 1
        cov[t["region"]][t["kind"] + " sites"] += t["n_sites"]
        cov[t["region"]]["unesco"] += t["n_unesco"]
        if t["node_source"] == "rule" or t["kind"] == BODY:
            cov[t["region"]]["named nodes"] += 1
    crow = []
    for reg in REGIONS + EXTRA_REGIONS + sorted(set(cov) - set(REGIONS) - set(EXTRA_REGIONS)):
        c = cov.get(reg, collections.Counter())
        row = {"region": reg, "extra_bucket": int(reg not in REGIONS), "named_nodes": c["named nodes"], "unesco": c["unesco"]}
        for k in KINDS:
            row[f"{k}_nodes"] = c[k + " nodes"]
            row[f"{k}_sites"] = c[k + " sites"]
        row["flag"] = "EMPTY" if not any(c[k + " nodes"] for k in KINDS) else \
            "missing: " + ", ".join(k for k in KINDS if not c[k + " nodes"])
        crow.append(row)
    write_csv(os.path.join(OUT_DIR, "in_situ_coverage.csv"), crow)

    # ---- printout
    print("\n=== coverage per world region (named nodes / sites per kind) ===")
    for row in crow:
        print(f"{row['region']:<32} named {row['named_nodes']:3}  unesco {row['unesco']:4}  " +
              "  ".join(f"{k.split()[0]} {row[k + '_nodes']}/{row[k + '_sites']}" for k in KINDS) + f"   {row['flag']}")
    print("\n=== rules with no match ===")
    print(", ".join(f"{r['rule']} {r['tradition'][:40]}" for r in rule_rows if not r["n_matched"]))
    nk = collections.Counter(s["kind"] for s in srows if not s["in_museum"])
    print(f"\n{len(cands)} candidate records -> {sum(nk.values())} in-situ sites ({dict(nk)}), "
          f"{sum(1 for s in srows if s['in_museum'])} museum-held work groups; {len(body)} body-art items; "
          f"{len(trows)} tradition rows ({sum(1 for t in trows if t['node_source'] == 'rule')} rule nodes)")
    if no_iso:
        print("countries without an ISO code (sites fall back to region 'unknown'): " +
              ", ".join(f"{lab(c)} ({n})" for c, n in no_iso.most_common(15)))
    if FAILED:
        print(f"WARNING: {len(FAILED)} queries failed; re-run to fill them in (results so far are cached)")


def write_csv(path, rows):
    if not rows:
        print(f"  nothing to write for {path}")
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"  wrote {path} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
