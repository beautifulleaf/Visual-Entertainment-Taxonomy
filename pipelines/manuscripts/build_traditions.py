"""Manuscript and book-arts traditions from Wikidata (visual-art-plan.md §2A, §2.2).

Illuminated and illustrated manuscripts mostly sit in libraries, not museums, so
the museum sweeps leave the book-arts traditions thin (Byzantine, Armenian,
Georgian, Ethiopian, Coptic, Syriac, Insular, Carolingian, Ottonian, Mozarabic,
Romanesque, Gothic, Books of Hours, Hebrew, Mesoamerican codices, palm-leaf and
paper manuscripts of South and Southeast Asia, Tibetan, emaki, Korean sutras).
This script gathers the evidence for those traditions from Wikidata, where
libraries (BnF, Bodleian, Matenadaran, Penn, Free Library, the Indonesian and
Southeast Asian digitisation programmes, ...) have imported their holdings.

Sources
  Wikidata (WDQS, one query at a time; QLever's mirror qlever.dev/api/wikidata
  as fallback, used for the rest of the run once WDQS fails a query).
  1. Manuscript classes: every subclass (P279*) of manuscript (Q87167), minus
     the calligraphic-work subtree (Q22669850: 82k Palace Museum calligraphy,
     not book arts) and document-like classes (EXCLUDE_CLASS_RE: maps, music,
     autographs, charters, letters, ...). Plus EXTRA_CLASSES, verified by label
     at run time: Gospel Book, psalter, Evangeliary, Haggadah, lectionary,
     bestiary, manuscript illumination (single leaves/miniatures), Kotenseki;
     their instances are kept only when dated before 1650 or held (P195).
  2. Per item: P31, P195 holding collection, P495 origin, P1071 place of
     creation, P2596 culture, P571 inception, P135 movement, P136 genre, P170
     creator, P407 language, P282 script, P361 part of, sitelinks, labels.
     Leaves inherit missing language / origin / date / style from a parent
     manuscript (P361) in the harvest.
  3. Referenced entities (places, languages, collections, styles, creators):
     labels, plus P17 and P131 of origin places so a city resolves to its
     country.
  4. Illumination schools and styles as items: style-type items (art style,
     movement, school, style of an area, ...) whose English label names
     illumination / miniature painting / manuscripts, plus the period styles in
     STYLE_SEEDS (verified by label at run time), plus style-type values of
     P135/P136/P2596 on harvested manuscripts.
  5. Named illuminators: humans with occupation illuminator (Q998628) with
     movement, citizenship, birth place, work location, dates and sitelinks.
  No library catalogue is harvested directly: e-codices, Digital Bodleian, BnF
  Gallica SRU and the British Library would each need per-record requests, and
  their holdings already reach Wikidata in part (BnF 75k, Bodleian 1.4k).

Grouping into tradition nodes
  data/interim/manuscripts_rules.csv is the reviewable rule table (written from
  DEFAULT_RULES on the first run or with --reset-rules; edits to it are read on
  later runs). Each row: tradition, kind, region, script/language, and regexes
  over the *labels* of the item's recorded style (P135/P136/P2596), classes,
  own label, languages + scripts, origin (P495/P1071/P2596 and their
  country/parent), holding collections, plus a year range. Every non-empty
  condition must match. kind=style rows are tried in order and the first match
  wins (so recorded-style rows come first, then specific school rules, then
  broad fallbacks); kind=genre rows (Books of Hours, Beatus, Haggadah, emaki,
  Kalpasutra, ...) tag every match, across styles. Undated items only match a
  dated rule when undated_ok=1. The basis column says which conditions fired.
  Islamic book arts are counted only (region "Islamic world", flagged as
  covered by pipelines/regional/islamic_world.py).

Outputs (data/interim/)
  manuscripts_items.csv        one row per manuscript item with its facts,
                               tradition, genres, region and basis
  manuscripts_traditions.csv   one row per tradition / genre node, plus
                               unlinked Wikidata illumination-style items:
                               label, qid, kind, region, script/language, era
                               (rule range and item p5-p95), n_manuscripts,
                               n_illuminated, n_sitelinked, n_recorded_style,
                               top holding libraries, named illuminators,
                               sample manuscripts, sources, gap flag
  manuscripts_illuminators.csv humans with occupation illuminator, with the
                               tradition they hang under (origin/style rules)
  manuscripts_regions.csv      coverage per world region with gap flags
  manuscripts_rules.csv        the rule table (see above)
  Raw SPARQL results are cached under data/raw/wikidata/manuscripts/, keyed
  by a hash of the query, so a re-run resumes.

Usage: python3 pipelines/manuscripts/build_traditions.py
           [--endpoint wdqs|qlever] [--reset-rules] [--offline]
"""
import argparse
import collections
import csv
import hashlib
import json
import os
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "visual_art"))
from wikidata import year_of  # noqa: E402

RAW = os.path.join(ROOT, "data", "raw", "wikidata", "manuscripts")
OUT_DIR = os.path.join(ROOT, "data", "interim")
RULES_CSV = os.path.join(OUT_DIR, "manuscripts_rules.csv")
ISLAMIC_DYN = os.path.join(OUT_DIR, "regional", "islamic_dynasties.csv")
ISLAMIC_SCH = os.path.join(OUT_DIR, "regional", "islamic_schools.csv")
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"

ENDPOINTS = {"wdqs": "https://query.wikidata.org/sparql", "qlever": "https://qlever.dev/api/wikidata"}
ENDPOINT = ["wdqs"]
OFFLINE = [False]
PREFIXES = """PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
"""

MANUSCRIPT = "Q87167"
CALLIGRAPHIC_WORK = "Q22669850"
ILLUMINATOR = "Q998628"
# Classes outside the manuscript tree (labels verified 2026-10-28 and again at run time).
EXTRA_CLASSES = {
    "Q690851": "Gospel Book", "Q956165": "psalter", "Q1754581": "Evangeliary", "Q623354": "Haggadah",
    "Q284465": "lectionary", "Q830560": "bestiary", "Q8362": "manuscript illumination",
    "Q107026784": "Kotenseki",
}
# Subclasses of manuscript that are documents, not book arts.
EXCLUDE_CLASS_RE = re.compile(
    r"calligraph|autograph|holograph|nachlass|letter|charter|cartulary|documentary|signal flag|"
    r"name added|tughra|siyah|bokuseki|kohitsu|komonjo|\bmap\b|music|sheet|traditionsbuch|"
    r"almanac|silloge|libro becerro|tumbo|genealogical roll|roll of arms", re.I)
# Classes that mark an item as decorated / illustrated (n_illuminated).
ILLUMINATED_CLASS_RE = re.compile(
    r"illuminat|book of hours|beatus|emaki|ornamental sutra|scroll painting|bible moralis|"
    r"exultet|muraqqa|ikkan|shinkan|biane|haggadah|gospel book|psalter|evangeliary|bestiary|"
    r"illustrated chronicle|liederhandschrift|mesoamerican codex|colonial codex|miniature", re.I)
# Period / school style items to link tradition nodes to (labels verified 2026-10-28).
STYLE_SEEDS = {
    "Q612118": "Insular art", "Q614082": "Carolingian art", "Q1066218": "Ottonian art",
    "Q1951304": "Mozarabic art", "Q46805": "Romanesque art", "Q46825": "Gothic art",
    "Q867769": "International Gothic", "Q211884": "Byzantine art", "Q577622": "Coptic art",
    "Q3450240": "Armenian art", "Q1028422": "Georgian art", "Q2688661": "Ethiopian art",
    "Q597365": "Yamato-e", "Q1190781": "emakimono", "Q2988788": "Rajput painting",
    "Q3631050": "Pahari painting", "Q15941800": "Ghent-Bruges school", "Q1400430": "Macedonian Renaissance",
    "Q2008210": "Visigothic art", "Q2864582": "Aztec art", "Q2353833": "art of illumination",
    "Q28455113": "book art",
}
STYLE_TYPES = {
    "Q1792644": "art style", "Q968159": "art movement", "Q2736610": "artistic school",
    "Q1292119": "style", "Q65266274": "art style of an area", "Q25679497": "art of an area",
    "Q3326867": "painting movement", "Q1792379": "art genre",
}
STYLE_LABEL_RE = (r"illuminat|miniature painting|manuscript|book art|book paint|codex|codices|"
                  r"emaki|scriptori|school of armenian")

REGIONS = ["Western Europe", "C&E Europe incl. Armenia/Georgia", "Byzantine", "Egypt/Coptic",
           "Near East/Syriac", "Islamic world", "Central Asia", "Himalaya", "South Asia", "SE Asia",
           "China", "Japan", "Korea", "Ethiopia/Sub-Saharan Africa", "Mesoamerica", "South America"]

# ------------------------------------------------------------------ rule table

# Label regexes reused below.
W_LANG = (r"^(latin|medieval latin|ecclesiastical latin|vulgar latin|french|old french|middle french|"
          r"anglo-norman|occitan|old occitan|italian|old italian|german|old high german|middle high german|"
          r"middle low german|english|old english|middle english|spanish|old spanish|castilian|catalan|"
          r"portuguese|galician|galician-portuguese|dutch|middle dutch|flemish|welsh|middle welsh|irish|"
          r"old irish|middle irish|scottish gaelic|breton|icelandic|old norse|danish|swedish|norwegian|"
          r"luxembourgish|picard|walloon|franco-proven.al|scots)$")
W_ORIGIN = (r"france|paris|francia|frank|normandy|burgund|champagne|italy|italian|lombard|tuscan|florence|"
            r"venice|bologna|milan|naples|sicily|rome\b|papal|england|english|britain|wales|scotland|ireland|"
            r"northumbria|mercia|wessex|germany|german|holy roman|bavaria|saxony|swabia|rhine|spain|castile|"
            r"le[oó]n|aragon|catalonia|navarre|asturias|portugal|flanders|belgium|netherlands|low countries|"
            r"brabant|hainaut|holland|switzerland|austria|luxembourg|denmark|sweden|norway|iceland")
SLAV_LANG = r"slavonic|old east slavic|russian|ruthenian|serbian|bulgarian|macedonian|croatian|glagolitic|cyrillic"
ISLAMIC_LANG = (r"^(arabic|classical arabic|persian|old persian|classical persian|ottoman turkish|urdu|chagatai|"
                r"pashto|kurdish|azerbaijani|dari|tajik|sindhi|kashmiri)$|arabic script|naskh|nasta.?l.?q|"
                r"kufic|muhaqqaq|thuluth|maghrebi|ta.?l.?q|riq.?a|diwani")

# (tradition, kind, region, script_language, style_re, class_re, label_re, lang_re, origin_re,
#  collection_re, year_min, year_max, undated_ok, note)
DEFAULT_RULES = [
    # ---- recorded style / culture (P135 / P136 / P2596) first
    ("Insular (Hiberno-Saxon)", "style", "Western Europe", "Latin, Old Irish, Old English", r"insular|hiberno", "", "", "", "", "", "", "", 1, "recorded style"),
    ("Carolingian", "style", "Western Europe", "Latin (Carolingian minuscule)", r"carolingian", "", "", "", "", "", "", "", 1, "recorded style"),
    ("Ottonian", "style", "Western Europe", "Latin", r"ottonian", "", "", "", "", "", "", "", 1, "recorded style"),
    ("Mozarabic / Visigothic", "style", "Western Europe", "Latin (Visigothic script)", r"mozarab|visigoth|early medieval spain", "", "", "", "", "", "", "", 1, "recorded style"),
    ("Mosan / Romanesque", "style", "Western Europe", "Latin", r"romanesque|mosan", "", "", "", "", "", "", "", 1, "recorded style"),
    ("Ghent-Bruges / Flemish illumination", "style", "Western Europe", "Latin, French, Dutch", r"ghent-bruges|flemish|netherlandish illumination", "", "", "", "", "", "", "", 1, "recorded style"),
    ("International Gothic", "style", "Western Europe", "Latin, French", r"international gothic", "", "", "", "", "", "", "", 1, "recorded style"),
    ("Byzantine, Middle (843-1204)", "style", "Byzantine", "Greek", r"macedonian renaissance|komnen", "", "", "", "", "", "", "", 1, "recorded style"),
    ("Byzantine (style recorded)", "style", "Byzantine", "Greek", r"byzantine", "", "", "", "", "", "", "", 1, "recorded style"),
    ("Coptic", "style", "Egypt/Coptic", "Coptic", r"coptic", "", "", "", "", "", "", "", 1, "recorded style"),
    ("Ancient Egyptian papyri", "style", "Egypt/Coptic", "Egyptian (hieroglyphic, hieratic, demotic)", r"ancient egypt|art of ancient egypt", "", "", "", "", "", "", "", 1, "recorded culture"),
    ("Gothic (style recorded)", "style", "Western Europe", "Latin, vernaculars", r"gothic", "", "", "", "", "", "", "", 1, "recorded style"),
    ("Renaissance illumination", "style", "Western Europe", "Latin, vernaculars", r"renaissance", "", "", "", "", "", "", "", 1, "recorded style"),
    ("Japanese emaki (Yamato-e)", "style", "Japan", "Japanese", r"yamato-e|tosa|inseiki", "", "", "", "", "", "", "", 1, "recorded style"),
    ("Aztec / Nahua codices (pre-conquest)", "style", "Mesoamerica", "Nahuatl pictography", r"aztec|mexica", "", "", "", "", "", "", 1520, 1, "recorded culture"),
    ("Mixtec codices", "style", "Mesoamerica", "Mixtec pictography", r"mixtec", "", "", "", "", "", "", "", 1, "recorded culture"),
    ("Maya codices", "style", "Mesoamerica", "Maya hieroglyphs", r"\bmaya", "", "", "", "", "", "", "", 1, "recorded culture"),
    ("Ethiopian (Ge'ez)", "style", "Ethiopia/Sub-Saharan Africa", "Ge'ez", r"amhara|ethiopia", "", "", "", "", "", "", "", 1, "recorded culture"),
    ("Islamic book arts: Persianate (see islamic_world.py)", "style", "Islamic world", "Persian", r"mughal|deccan|persian painting|timurid|safavid", "", "", "", "", "", "", "", 1, "recorded style; covered by islamic_world.py"),
    ("Balinese lontar", "style", "SE Asia", "Balinese, Kawi (Balinese script)", r"^bali", "", "", "", "", "", "", "", 1, "recorded culture"),
    # ---- class / genre-driven traditions
    ("Ancient Egyptian papyri", "style", "Egypt/Coptic", "Egyptian (hieroglyphic, hieratic, demotic)", "", "", "", r"egyptian|demotic|hieratic|hieroglyph", "", "", "", "", 1, ""),
    ("Japanese emaki (Yamato-e)", "style", "Japan", "Japanese", "", r"emaki|yōkai emaki|scroll painting", "", "", r"japan", "", "", "", 1, ""),
    ("Japanese emaki (Yamato-e)", "style", "Japan", "Japanese", "", r"emaki", "", "", "", "", "", "", 1, ""),
    ("Japanese illustrated sutras", "style", "Japan", "Classical Chinese / Japanese", "", r"ornamental sutra|ikkan-ky|shinkan", "", "", "", "", "", "", 1, ""),
    ("Japanese manuscripts and Nara-ehon", "style", "Japan", "Japanese", "", r"kotenseki|genji|aobyoshi|kawachi|kakemono|shigajiku", "", "", "", "", "", "", 1, ""),
    ("Mesoamerican codices, colonial", "style", "Mesoamerica", "Nahuatl, Spanish, pictography", "", r"colonial codex", "", "", "", "", "", "", 1, ""),
    ("Mesoamerican codices, colonial", "style", "Mesoamerica", "Nahuatl, Spanish, pictography", "", r"mesoamerican codex", "", "", "", "", 1521, "", 0, ""),
    ("Maya codices", "style", "Mesoamerica", "Maya hieroglyphs", "", "", r"dresden codex|madrid codex|paris codex|grolier|maya codex|codex tro|codex cortes", "", "", "", "", "", 1, ""),
    ("Mixtec codices", "style", "Mesoamerica", "Mixtec pictography", "", "", r"zouche|nuttall|bodley|selden|vindobonensis|colombino|becker|codex vienna|mixtec", "", "", "", "", "", 1, ""),
    ("Borgia group codices", "style", "Mesoamerica", "Central Mexican pictography", "", "", r"borgia|cospi|fej.rv.ry|laud|vaticanus b|codex vaticanus 3773", "", "", "", "", "", 1, ""),
    ("Mesoamerican codices, colonial", "style", "Mesoamerica", "Nahuatl, Spanish, pictography", "", "", r"c[oó]d(ex|ice)|lienzo|mapa de|tira de", r"nahuatl|mixtec|maya|zapotec|otom|purépecha|tarascan", "", "", 1521, "", 1, ""),
    ("Mesoamerican codices, colonial", "style", "Mesoamerica", "Nahuatl, Spanish, pictography", "", "", r"c[oó]d(ex|ice)|lienzo|mapa de|tira de", "", r"mexico|new spain|aztec|mixtec|oaxaca|guatemala|maya|tlaxcala|yucat", "", 1521, "", 1, ""),
    ("Aztec / Nahua codices (pre-conquest)", "style", "Mesoamerica", "Nahuatl pictography", "", r"mesoamerican codex", "", "", "", "", "", 1520, 1, ""),
    ("Andean colonial manuscripts", "style", "South America", "Spanish, Quechua, Aymara", "", "", "", r"quechua|aymara|puquina|mapudungun", "", "", "", "", 1, ""),
    ("Andean colonial manuscripts", "style", "South America", "Spanish, Quechua, Aymara", "", "", "", "", r"peru|bolivia|ecuador|viceroyalty of peru|new granada|colombia|chile|argentina|venezuela|r[ií]o de la plata|inca", "", "", "", 1, ""),
    ("Brazilian / Portuguese American manuscripts", "style", "South America", "Portuguese, Tupi", "", "", "", "", r"brazil", "", "", "", 1, ""),
    # ---- Hebrew
    ("Hebrew: Yemenite", "style", "Near East/Syriac", "Hebrew, Judeo-Arabic", "", "", "", r"hebrew|judeo-arabic|aramaic", r"yemen", "", "", "", 1, ""),
    ("Hebrew: Sephardi", "style", "Western Europe", "Hebrew, Judeo-Arabic, Ladino", "", "", "", r"hebrew|judeo-arabic|ladino|judeo-spanish", r"spain|castile|aragon|catalonia|navarre|portugal|le[oó]n|al-andalus|provence|majorca|morocco|maghreb|tunisia", "", "", "", 1, ""),
    ("Hebrew: Ashkenazi", "style", "Western Europe", "Hebrew, Yiddish", "", "", "", r"hebrew|yiddish|judeo-german", r"german|holy roman|rhine|austria|bohemia|czech|poland|lithuania|alsace|switzerland|hungary|ukraine", "", "", "", 1, ""),
    ("Hebrew: Ashkenazi", "style", "Western Europe", "Hebrew, Yiddish", "", "", "", r"yiddish", "", "", "", "", 1, ""),
    ("Hebrew: Italian", "style", "Western Europe", "Hebrew, Judeo-Italian", "", "", "", r"hebrew|judeo-italian", r"ital|venice|rome\b|florence|mantua|ferrara|padua|lombard|tuscan|sicily|naples", "", "", "", 1, ""),
    ("Hebrew: French / Provençal", "style", "Western Europe", "Hebrew", "", "", "", r"hebrew|judeo-french", r"france|provence|paris|champagne", "", "", "", 1, ""),
    ("Hebrew: Oriental (Mizrahi, Persian, Egyptian)", "style", "Near East/Syriac", "Hebrew, Judeo-Arabic, Judeo-Persian", "", "", "", r"hebrew|judeo-arabic|judeo-persian|aramaic", r"egypt|iraq|syria|iran|persia|palestin|israel|lebanon|turkey|ottoman|byzant|kurdist|bukhar|afghan|india|cairo", "", "", "", 1, ""),
    ("Hebrew: Second Temple scrolls (Dead Sea)", "style", "Near East/Syriac", "Hebrew, Aramaic", "", "", r"dead sea|qumran|^4q|^1q|^11q", "", "", "", "", "", 1, ""),
    ("Hebrew manuscripts (unlocalised)", "style", "Western Europe", "Hebrew, Judeo-Arabic", "", "", "", r"^(hebrew|biblical hebrew|medieval hebrew|mishnaic hebrew|judeo-arabic|judeo-persian|ladino|judeo-spanish|yiddish|hebrew alphabet)$", "", "", "", "", 1, "region provisional: most undated Hebrew manuscripts in Wikidata are European library holdings"),
    # ---- Armenian schools
    ("Armenian: Cilician school", "style", "C&E Europe incl. Armenia/Georgia", "Classical Armenian", "", "", "", "", r"cilicia|\bsis\b|hromkla|rumkale|adana|tarsus|mopsuestia|lesser armenia", "", "", "", 1, ""),
    ("Armenian: Glajor (Gladzor) school", "style", "C&E Europe incl. Armenia/Georgia", "Classical Armenian", r"gla[dj]zor|glajor", "", "", "", "", "", "", "", 1, "recorded style"),
    ("Armenian: Glajor (Gladzor) school", "style", "C&E Europe incl. Armenia/Georgia", "Classical Armenian", "", "", "", "", r"gla[dj]zor|glajor|vayots", "", "", "", 1, ""),
    ("Armenian: Syunik / Tatev school", "style", "C&E Europe incl. Armenia/Georgia", "Classical Armenian", r"tatev|syunik", "", "", "", r"", "", "", "", 1, "recorded style"),
    ("Armenian: Syunik / Tatev school", "style", "C&E Europe incl. Armenia/Georgia", "Classical Armenian", "", "", "", "", r"tatev|syunik|siunik", "", "", "", 1, ""),
    ("Armenian: Vaspurakan school", "style", "C&E Europe incl. Armenia/Georgia", "Classical Armenian", r"vaspurakan", "", "", "", "", "", "", "", 1, "recorded style"),
    ("Armenian: Vaspurakan school", "style", "C&E Europe incl. Armenia/Georgia", "Classical Armenian", "", "", "", "", r"vaspurakan|\bvan\b|aghtamar|akhtamar|khizan|hizan|bitlis|ostan", "", "", "", 1, ""),
    ("Armenian: Crimean school", "style", "C&E Europe incl. Armenia/Georgia", "Classical Armenian", r"crimean school", "", "", "", "", "", "", "", 1, "recorded style"),
    ("Armenian: Crimean school", "style", "C&E Europe incl. Armenia/Georgia", "Classical Armenian", "", "", "", r"armenian", r"crimea|kaffa|feodosi|surkhat|caffa", "", "", "", 1, ""),
    ("Armenian: New Julfa / diaspora", "style", "C&E Europe incl. Armenia/Georgia", "Classical Armenian", "", "", "", r"armenian", r"julfa|isfahan|iran|persia|constantinople|istanbul|lviv|lwów|lemberg|amsterdam|venice|poland|jerusalem", "", "", "", 1, ""),
    ("Armenian: Ani / early Armenian (to 1200)", "style", "C&E Europe incl. Armenia/Georgia", "Classical Armenian", r"ani school", "", "", "", "", "", "", "", 1, "recorded style"),
    ("Armenian: Ani / early Armenian (to 1200)", "style", "C&E Europe incl. Armenia/Georgia", "Classical Armenian", "", "", "", r"armenian", "", "", "", 1200, 0, ""),
    ("Armenian: Ani / early Armenian (to 1200)", "style", "C&E Europe incl. Armenia/Georgia", "Classical Armenian", "", "", "", "", r"^ani$|bagratid|echmiadzin|etchmiadzin", "", "", 1200, 1, ""),
    ("Armenian (later or unlocalised)", "style", "C&E Europe incl. Armenia/Georgia", "Classical Armenian", "", "", "", r"armenian", "", "", "", "", 1, ""),
    ("Armenian (later or unlocalised)", "style", "C&E Europe incl. Armenia/Georgia", "Classical Armenian", "", "", "", "", r"armenia", "", "", "", 1, ""),
    ("Armenian (later or unlocalised)", "style", "C&E Europe incl. Armenia/Georgia", "Classical Armenian", "", "", "", "", "", r"matenadaran", "", "", 1, "holding library only"),
    # ---- Georgian, Slavonic
    ("Georgian", "style", "C&E Europe incl. Armenia/Georgia", "Old Georgian (asomtavruli, nuskhuri, mkhedruli)", "", "", "", r"georgian|asomtavruli|nuskhuri|mkhedruli", "", "", "", "", 1, ""),
    ("Georgian", "style", "C&E Europe incl. Armenia/Georgia", "Old Georgian", "", r"mravaltavi", "", "", "", "", "", "", 1, ""),
    ("Georgian", "style", "C&E Europe incl. Armenia/Georgia", "Old Georgian", "", "", "", "", r"^georgia$|kingdom of georgia|kartli|kakheti|imereti|tao-klarjeti|iberia|svaneti|tbilisi|gelati|mtskheta", "", "", "", 1, ""),
    ("Georgian", "style", "C&E Europe incl. Armenia/Georgia", "Old Georgian", "", "", "", "", "", r"korneli kekelidze|national centre of manuscripts|georgian national", "", "", 1, "holding library only"),
    ("Croatian Glagolitic", "style", "C&E Europe incl. Armenia/Georgia", "Church Slavonic (Glagolitic)", "", "", "", r"glagolitic", "", "", "", "", 1, ""),
    ("South Slavic (Serbian, Bulgarian)", "style", "C&E Europe incl. Armenia/Georgia", "Church Slavonic (Cyrillic)", "", "", "", SLAV_LANG, r"serbia|bulgaria|macedonia|montenegro|bosnia|wallachia|moldavia|romania|athos|hilandar|zograf", "", "", "", 1, ""),
    ("South Slavic (Serbian, Bulgarian)", "style", "C&E Europe incl. Armenia/Georgia", "Church Slavonic (Cyrillic)", "", "", "", r"serbian|bulgarian|macedonian", "", "", "", "", 1, ""),
    ("Old Rus' and Muscovite", "style", "C&E Europe incl. Armenia/Georgia", "Church Slavonic, Old East Slavic", "", "", "", "", r"russia|rus'|rus\b|muscov|novgorod|moscow|kiev|kyiv|pskov|vladimir|rostov|tver|ukraine|belarus", "", "", "", 1, ""),
    ("Old Rus' and Muscovite", "style", "C&E Europe incl. Armenia/Georgia", "Church Slavonic, Old East Slavic", "", "", "", SLAV_LANG, "", "", "", "", 1, ""),
    ("Old Rus' and Muscovite", "style", "C&E Europe incl. Armenia/Georgia", "Church Slavonic", "", r"church slavonic|slavonic menaion", "", "", "", "", "", "", 1, ""),
    # ---- Ethiopia / Africa
    ("Ethiopian (Ge'ez), early (to 1500)", "style", "Ethiopia/Sub-Saharan Africa", "Ge'ez", "", "", "", r"ge.?ez|amharic|tigrinya|tigre|ethiopic", "", "", "", 1500, 0, ""),
    ("Ethiopian (Ge'ez), Gondarine and later", "style", "Ethiopia/Sub-Saharan Africa", "Ge'ez, Amharic", "", "", "", r"ge.?ez|amharic|tigrinya|tigre|ethiopic", "", "", 1501, "", 0, ""),
    ("Ethiopian (Ge'ez)", "style", "Ethiopia/Sub-Saharan Africa", "Ge'ez", "", "", "", r"ge.?ez|amharic|tigrinya|tigre|ethiopic", "", "", "", "", 1, ""),
    ("Ethiopian (Ge'ez)", "style", "Ethiopia/Sub-Saharan Africa", "Ge'ez", "", "", "", "", r"ethiopia|eritrea|abyssinia|aksum|axum|gondar|tigray|lalibela", "", "", "", 1, ""),
    ("Nubian (Old Nubian, Greek, Coptic)", "style", "Ethiopia/Sub-Saharan Africa", "Old Nubian", "", "", "", r"nubian", "", "", "", "", 1, ""),
    ("Nubian (Old Nubian, Greek, Coptic)", "style", "Ethiopia/Sub-Saharan Africa", "Old Nubian, Greek, Coptic", "", "", "", "", r"nubia|makuria|nobatia|alodia|qasr ibrim|sudan", "", "", 1500, 0, ""),
    ("Bamum and other African scripts", "style", "Ethiopia/Sub-Saharan Africa", "Bamum, Vai, Nsibidi", "", "", "", r"bamum|vai\b|nsibidi|mende|adlam|tifinagh|tamazight|berber", "", "", "", "", 1, ""),
    ("West African Ajami / Sahelian Islamic (see islamic_world.py)", "style", "Islamic world", "Arabic, Ajami (Hausa, Fula, Wolof)", "", "", "", r"hausa|fula|fulfulde|wolof|songhay|kanuri|mandinka|ajami", "", "", "", "", 1, "covered by islamic_world.py"),
    ("West African Ajami / Sahelian Islamic (see islamic_world.py)", "style", "Islamic world", "Arabic, Ajami", "", "", "", "", r"mali\b|timbuktu|niger\b|nigeria|senegal|mauritania|chad|sokoto|kano|guinea|ghana|cameroon", "", "", "", 1, "covered by islamic_world.py"),
    ("Swahili / East African Islamic (see islamic_world.py)", "style", "Islamic world", "Swahili, Arabic", "", "", "", r"swahili", "", "", "", "", 1, "covered by islamic_world.py"),
    # ---- Coptic, Syriac, Near East
    ("Coptic", "style", "Egypt/Coptic", "Coptic (Sahidic, Bohairic)", "", "", "", r"coptic|sahidic|bohairic|fayyumic|akhmimic", "", "", "", "", 1, ""),
    ("Graeco-Roman Egyptian papyri", "style", "Egypt/Coptic", "Greek, Latin (on papyrus)", "", r"papyrus", "", "", "", "", "", 700, 1, "mostly documentary; few illustrated"),
    ("Graeco-Roman Egyptian papyri", "style", "Egypt/Coptic", "Greek, Latin", "", "", "", r"greek|latin", r"egypt|oxyrhynch|fayum|thebes|alexandria", "", "", 700, 1, ""),
    ("Syriac", "style", "Near East/Syriac", "Syriac (Estrangela, Serto, East Syriac), Garshuni", "", "", "", r"syriac|estrangela|serto|garshuni|karshuni|neo-aramaic|christian palestinian aramaic|sureth|turoyo", "", "", "", "", 1, ""),
    ("Samaritan", "style", "Near East/Syriac", "Samaritan Hebrew / Aramaic", "", "", "", r"samaritan", "", "", "", "", 1, ""),
    ("Mandaic", "style", "Near East/Syriac", "Mandaic", "", "", "", r"mandaic", "", "", "", "", 1, ""),
    ("Christian Arabic / Melkite", "style", "Near East/Syriac", "Arabic (Christian)", "", "", r"gospel|psalter|lectionary|evangel|liturg|horologion|euchologion|synaxar|menaion|kontakion", r"^arabic$", "", "", "", "", 1, "label-based; Arabic Christian texts"),
    ("Sogdian, Old Uyghur and Turfan manuscripts", "style", "Central Asia", "Sogdian, Old Uyghur, Middle Persian, Tocharian", "", "", "", r"sogdian|uyghur|uighur|tocharian|khotanese|bactrian|manichae|middle persian|parthian|old turkic|tangut|kharosthi|gandhari|saka", "", "", "", "", 1, ""),
    ("Sogdian, Old Uyghur and Turfan manuscripts", "style", "Central Asia", "various", "", "", "", "", r"turfan|khocho|qocho|bezeklik|khotan|kucha|xinjiang|tarim|kroraina|khara-khoto|bamiyan|gilgit", "", "", "", 1, ""),
    ("Mongolian manuscripts", "style", "Central Asia", "Classical Mongolian, Oirat", "", "", "", r"mongol|oirat|buryat|kalmyk|todo|manchu", "", "", "", "", 1, ""),
    # ---- Himalaya
    ("Tibetan manuscripts and illustrated books", "style", "Himalaya", "Classical Tibetan", "", "", "", r"tibet", "", "", "", "", 1, ""),
    ("Tibetan manuscripts and illustrated books", "style", "Himalaya", "Classical Tibetan", "", "", "", "", r"tibet|lhasa|ladakh|bhutan|sikkim|mustang|guge|tsang", "", "", "", 1, ""),
    ("Nepalese (Newar) manuscripts", "style", "Himalaya", "Sanskrit, Newar (Ranjana, Bhujimol)", "", "", "", r"newar|nepal bhasa|ranjana|bhujimol|nepali|prachalit", "", "", "", "", 1, ""),
    ("Nepalese (Newar) manuscripts", "style", "Himalaya", "Sanskrit, Newar", "", "", "", "", r"nepal|kathmandu|patan|bhaktapur", "", "", "", 1, ""),
    # ---- South Asia
    ("Pala Buddhist palm-leaf", "style", "South Asia", "Sanskrit (Siddham, proto-Bengali)", "", "", r"prajnaparamita|prajñāpāramitā|pancaraksa|pañcarakṣā|karandavyuha|sadhanamala|astasahasrika", "", "", "", "", 1300, 1, ""),
    ("Pala Buddhist palm-leaf", "style", "South Asia", "Sanskrit", "", "", "", r"sanskrit|siddham|pali", r"bengal|bihar|nalanda|vikramashila|pala|bangladesh|magadha", "", 700, 1300, 0, ""),
    ("Jain manuscripts (Western Indian style)", "style", "South Asia", "Prakrit, Sanskrit, Old Gujarati", "", "", r"kalpa.?s[uū]tra|kalakacharya|k[aā]lak[aā]c[aā]rya|uttar[aā]dhyayana|jain|sangrahan|jina|mahavira|mahāvīra|parshvanatha|neminatha|shalibhadra|adinatha", "", "", "", "", "", 1, ""),
    ("Jain manuscripts (Western Indian style)", "style", "South Asia", "Prakrit, Sanskrit, Old Gujarati", "", "", "", r"prakrit|ardhamagadhi|maharashtri|apabhramsa|apabhraṃśa|old gujarati|jain", "", "", "", "", 1, ""),
    ("Odia palm-leaf", "style", "South Asia", "Odia", "", "", "", r"odia|oriya", "", "", "", "", 1, ""),
    ("Odia palm-leaf", "style", "South Asia", "Odia, Sanskrit", "", "", "", "", r"odisha|orissa|puri\b|cuttack|ganjam", "", "", "", 1, ""),
    ("Assamese (Sanchipat) and Bengali manuscripts", "style", "South Asia", "Assamese, Bengali", "", "", "", r"assamese|bengali|bangla|maithili|tirhuta", "", "", "", "", 1, ""),
    ("Kashmiri birch-bark and Sharada manuscripts", "style", "South Asia", "Sanskrit (Sharada)", "", r"birch bark", "", "", "", "", "", "", 1, ""),
    ("Kashmiri birch-bark and Sharada manuscripts", "style", "South Asia", "Sanskrit (Sharada)", "", "", "", r"sharada|śāradā|kashmiri", "", "", "", "", 1, ""),
    ("Sikh (Gurmukhi) manuscripts", "style", "South Asia", "Punjabi (Gurmukhi)", "", "", "", r"gurmukhi|punjabi|panjabi", "", "", "", "", 1, ""),
    ("South Indian palm-leaf (Tamil, Malayalam, Telugu, Kannada)", "style", "South Asia", "Tamil, Malayalam, Telugu, Kannada, Grantha", "", "", "", r"tamil|malayalam|telugu|kannada|grantha|tulu|nandinagari", "", "", "", "", 1, ""),
    ("Sinhalese palm-leaf", "style", "South Asia", "Sinhala, Pali", "", "", "", r"sinhala|sinhalese", "", "", "", "", 1, ""),
    ("Sinhalese palm-leaf", "style", "South Asia", "Sinhala, Pali", "", "", "", "", r"sri lanka|ceylon|kandy|anuradhapura", "", "", "", 1, ""),
    ("Rajput / Pahari illustrated manuscripts", "style", "South Asia", "Sanskrit, Hindi (Braj), Rajasthani", r"rajput|pahari|rajasthan|kangra|basohli|mewar", "", "", "", "", "", "", "", 1, "recorded style"),
    ("Rajput / Pahari illustrated manuscripts", "style", "South Asia", "Sanskrit, Hindi (Braj), Rajasthani", "", "", r"bhagavata|bh[aā]gavata|ramayana|r[aā]m[aā]yaṇa|gita govinda|g[iī]tagovinda|rasikapriya|ragamala|r[aā]gam[aā]l[aā]|devi mahatmya|devīmāhātmya|mahabharata|chaurapanchasika|laur chanda|rasamanjari|baramasa|harivamsa", "", "", "", "", "", 1, "label-based; Mughal Razmnama/Ramayana copies may fall here"),
    ("Hindi / Rajasthani / Marathi / Gujarati manuscripts", "style", "South Asia", "Hindi, Rajasthani, Marathi, Gujarati (Devanagari)", "", "", "", r"hindi|braj|awadhi|rajasthani|marwari|marathi|gujarati|modi|devanagari|nepali", "", "", "", "", 1, ""),
    ("Sanskrit manuscripts (unlocalised)", "style", "South Asia", "Sanskrit", "", "", "", r"sanskrit|vedic|pali", "", "", "", "", 1, "Pali may be Southeast Asian"),
    ("South Asian palm-leaf (unlocalised)", "style", "South Asia", "various", "", r"palm-leaf", "", "", r"india|bharat", "", "", "", 1, ""),
    # ---- Southeast Asia
    ("Islamic Nusantara manuscripts (Jawi, Pegon)", "style", "SE Asia", "Malay (Jawi), Javanese (Pegon), Acehnese", "", "", "", r"jawi|pegon|malay|acehnese|minangkabau|banjar", "", "", "", "", 1, "overlaps Islamic world"),
    ("Balinese lontar", "style", "SE Asia", "Balinese, Kawi (Balinese script)", "", r"geguritan|kakawin|kidung|pupuh|gedong kirtya", "", "", "", "", "", "", 1, ""),
    ("Balinese lontar", "style", "SE Asia", "Balinese, Kawi", "", "", "", r"balinese", "", "", "", "", 1, ""),
    ("Balinese lontar", "style", "SE Asia", "Balinese, Kawi", "", "", "", "", r"^bali|bali province|lombok|denpasar|singaraja|karangasem|gianyar|tabanan|klungkung|buleleng", "", "", "", 1, ""),
    ("Javanese manuscripts (Old Javanese / Kawi, Javanese)", "style", "SE Asia", "Javanese, Old Javanese (Kawi)", "", "", "", r"javanese|kawi|cacarakan|sundanese|madurese|sasak|old sundanese", "", "", "", "", 1, ""),
    ("Batak pustaha", "style", "SE Asia", "Batak", "", "", r"pustaha|pustaka", r"batak|toba|karo|mandailing|simalungun", "", "", "", "", 1, ""),
    ("Batak pustaha", "style", "SE Asia", "Batak", "", "", "", r"batak|toba|mandailing|simalungun", "", "", "", "", 1, ""),
    ("Bugis / Makassar (lontara)", "style", "SE Asia", "Buginese, Makassarese (Lontara)", "", "", "", r"bugi|buginese|makassar|lontara", "", "", "", "", 1, ""),
    ("Burmese parabaik and kammavaca", "style", "SE Asia", "Burmese, Pali", "", "", r"parabaik|kammav[aā]c[aā]|kammavacha|kammawa", "", "", "", "", "", 1, ""),
    ("Burmese parabaik and kammavaca", "style", "SE Asia", "Burmese, Pali, Shan, Mon", "", "", "", r"burmese|myanmar|shan|\bmon\b|karen", "", "", "", "", 1, ""),
    ("Burmese parabaik and kammavaca", "style", "SE Asia", "Burmese, Pali", "", "", "", "", r"myanmar|burma|mandalay|ava\b|pagan|amarapura|konbaung", "", "", "", 1, ""),
    ("Thai samut khoi and Lanna manuscripts", "style", "SE Asia", "Thai, Pali (Khom), Northern Thai (Tai Tham)", "", "", r"samut|phra malai|traiphum|tamra|folding book", "", r"thai|siam", "", "", "", 1, ""),
    ("Thai samut khoi and Lanna manuscripts", "style", "SE Asia", "Thai, Pali, Northern Thai", "", "", "", r"^thai$|northern thai|lanna|tai tham|khom|tai l[uü]|tai nua|khün|lao|isan", "", "", "", "", 1, ""),
    ("Thai samut khoi and Lanna manuscripts", "style", "SE Asia", "Thai, Pali", "", "", "", "", r"thailand|siam|ayutthaya|rattanakosin|lan na|chiang mai|laos|lan xang|luang prabang", "", "", "", 1, ""),
    ("Khmer manuscripts", "style", "SE Asia", "Khmer, Pali", "", "", "", r"khmer", "", "", "", "", 1, ""),
    ("Khmer manuscripts", "style", "SE Asia", "Khmer, Pali", "", "", "", "", r"cambodia|khmer", "", "", "", 1, ""),
    ("Vietnamese (Han-Nom) manuscripts", "style", "SE Asia", "Classical Chinese, Chu Nom", "", "", "", r"vietnam|ch[ữu] n[ôo]m|han-nom", "", "", "", "", 1, ""),
    ("Vietnamese (Han-Nom) manuscripts", "style", "SE Asia", "Classical Chinese, Chu Nom", "", "", "", "", r"vietnam|annam|tonkin|dai viet|đại việt|hue\b", "", "", "", 1, ""),
    ("Philippine (Baybayin) manuscripts", "style", "SE Asia", "Tagalog (Baybayin), Hanunoo", "", "", "", r"baybayin|tagalog|hanuno|buhid|tagbanwa|visayan|cebuano|ilocano", "", "", "", "", 1, ""),
    ("Indonesian manuscripts (unlocalised)", "style", "SE Asia", "various", "", "", "", "", r"indonesia|dutch east indies|java|sumatra|sulawesi|borneo|kalimantan|madura|lombok|aceh", "", "", "", 1, ""),
    ("Indonesian manuscripts (unlocalised)", "style", "SE Asia", "various", "", "", "", "", "", r"endangered and affected manuscripts in southeast asia|manuskrip nusantara|wanantara|kementerian agama|religious affairs|perpustakaan nasional", "", "", 1, "holding library only"),
    ("Southeast Asian palm-leaf (unlocalised)", "style", "SE Asia", "Pali and vernaculars", "", r"palm-leaf", "", r"pali", "", "", "", "", 1, ""),
    # ---- Korea, China, Japan
    ("Korean: Goryeo illuminated sutras", "style", "Korea", "Classical Chinese (Korean)", "", "", "", "", r"korea|goryeo|koryo|joseon|chos[oŏ]n|silla", "", 900, 1392, 0, ""),
    ("Korean: Joseon manuscripts and uigwe", "style", "Korea", "Classical Chinese, Korean (Hangul)", "", "", "", "", r"korea|joseon|chos[oŏ]n", "", 1392, "", 1, ""),
    ("Korean: Joseon manuscripts and uigwe", "style", "Korea", "Korean (Hangul)", "", "", "", r"korean|hangul|idu", "", "", "", "", 1, ""),
    ("Japanese illustrated sutras", "style", "Japan", "Classical Chinese / Japanese", "", "", r"sutra|ky[oō]\b|-ky[oō]|heike nōkyō|ingaky", "", r"japan|nara|kyoto|heian", "", "", 1600, 1, ""),
    ("Japanese manuscripts and Nara-ehon", "style", "Japan", "Japanese", "", "", "", r"japanese|kanbun|man.y.gana|hiragana|katakana", "", "", "", "", 1, ""),
    ("Japanese manuscripts and Nara-ehon", "style", "Japan", "Japanese", "", "", "", "", r"japan|kyoto|edo\b|nara\b|kamakura|heian", "", "", "", 1, ""),
    ("Dunhuang and early Chinese manuscripts (to 1000)", "style", "China", "Classical Chinese", "", "", "", r"chinese", "", "", "", 1000, 0, ""),
    ("Dunhuang and early Chinese manuscripts (to 1000)", "style", "China", "Classical Chinese, Tibetan, Sogdian", "", "", r"dunhuang|mogao|stein|pelliot", "", "", "", "", "", 1, ""),
    ("Chinese illustrated manuscripts and scrolls (1000+)", "style", "China", "Classical Chinese", "", "", "", r"chinese|nüshu|yi\b|naxi|dongba|zhuang", "", "", 1001, "", 1, ""),
    ("Chinese illustrated manuscripts and scrolls (1000+)", "style", "China", "Classical Chinese", "", "", "", "", r"china|qing|ming dynasty|song dynasty|yuan dynasty|tang dynasty", "", "", "", 1, ""),
    # ---- Byzantine
    ("Byzantine, Early (to 843)", "style", "Byzantine", "Greek (uncial)", "", "", "", r"greek", "", "", 330, 843, 0, ""),
    ("Byzantine, Middle (843-1204)", "style", "Byzantine", "Greek (minuscule)", "", "", "", r"greek", "", "", 844, 1204, 0, ""),
    ("Byzantine, Palaiologan (1204-1453)", "style", "Byzantine", "Greek", "", "", "", r"greek", "", "", 1205, 1453, 0, ""),
    ("Post-Byzantine Greek (1453+)", "style", "Byzantine", "Greek", "", "", "", r"greek", "", "", 1454, "", 0, ""),
    ("Byzantine / Greek manuscripts (undated)", "style", "Byzantine", "Greek", "", "", "", r"greek", "", "", "", "", 1, ""),
    ("Byzantine / Greek manuscripts (undated)", "style", "Byzantine", "Greek", "", "", "", "", r"byzantin|constantinople|athos|trebizond|nicaea|mistra|morea", "", "", "", 1, ""),
    # ---- Islamic world (counts only; covered by islamic_world.py)
    ("Islamic book arts: Persianate (see islamic_world.py)", "style", "Islamic world", "Persian, Chagatai, Urdu", "", "", "", r"^(persian|classical persian|dari|tajik|chagatai|urdu|pashto|kashmiri|sindhi)$|nasta.?l.?q|shikasta", "", "", "", "", 1, "covered by islamic_world.py"),
    ("Islamic book arts: Ottoman (see islamic_world.py)", "style", "Islamic world", "Ottoman Turkish, Arabic", "", "", "", r"ottoman turkish|turkish|azerbaijani|crimean tatar|tatar", "", "", "", "", 1, "covered by islamic_world.py"),
    ("Islamic book arts: Ottoman (see islamic_world.py)", "style", "Islamic world", "Ottoman Turkish, Arabic", "", "", "", ISLAMIC_LANG, r"ottoman|turkey|istanbul|constantinople|edirne|bursa", "", "", "", 1, "covered by islamic_world.py"),
    ("Islamic book arts: Maghrebi / Andalusi (see islamic_world.py)", "style", "Islamic world", "Arabic (Maghrebi script)", "", "", "", ISLAMIC_LANG, r"morocco|algeria|tunisia|libya|al-andalus|granada|spain|maghreb|fez|marrakesh|kairouan", "", "", "", 1, "covered by islamic_world.py"),
    ("Islamic book arts: Arabic (see islamic_world.py)", "style", "Islamic world", "Arabic", "", "", "", ISLAMIC_LANG, "", "", "", "", 1, "covered by islamic_world.py"),
    ("Islamic book arts: Arabic (see islamic_world.py)", "style", "Islamic world", "Arabic", "", r"hilya|muraqqa|quranic", "", "", "", "", "", "", 1, "covered by islamic_world.py"),
    ("Islamic book arts: Persianate (see islamic_world.py)", "style", "Islamic world", "Persian", "", "", "", "", r"^iran$|persia|safavid|timurid|qajar|ilkhan|mughal|herat|tabriz|shiraz|isfahan|bukhara|samarkand|afghanistan|golconda|bijapur|deccan", "", "", "", 1, "covered by islamic_world.py"),
    # ---- Western Europe by origin x date (rule table)
    ("Late Antique and Early Christian", "style", "Western Europe", "Latin (rustic capitals, uncial)", "", "", "", W_LANG, "", "", 300, 650, 0, ""),
    ("Insular (Hiberno-Saxon)", "style", "Western Europe", "Latin, Old Irish, Old English (Insular script)", "", "", "", "", r"ireland|irish|scotland|iona|northumbria|lindisfarne|jarrow|wearmouth|mercia|kent|canterbury|wales|england|britain|anglo-saxon", "", 550, 900, 0, ""),
    ("Insular (Hiberno-Saxon)", "style", "Western Europe", "Old Irish, Old English", "", "", "", r"^(old irish|old english|insular)", "", "", 550, 900, 0, ""),
    ("Merovingian", "style", "Western Europe", "Latin (Merovingian script)", "", "", "", "", r"france|francia|frank|neustria|austrasia|corbie|luxeuil|laon|belgium|merovingian", "", 600, 770, 0, ""),
    ("Carolingian", "style", "Western Europe", "Latin (Carolingian minuscule)", "", "", "", "", r"france|francia|frank|germany|german|holy roman|tours|reims|metz|aachen|corbie|saint-denis|st\.? gall|switzerland|lorsch|fulda|belgium|netherlands|luxembourg|austria|italy|lombard|bavaria|salzburg|regensburg|carolingian", "", 750, 900, 0, ""),
    ("Anglo-Saxon (Winchester school)", "style", "Western Europe", "Latin, Old English", "", "", "", "", r"england|english|britain|wessex|winchester|canterbury|anglo-saxon", "", 901, 1100, 0, ""),
    ("Ottonian", "style", "Western Europe", "Latin", "", "", "", "", r"germany|german|holy roman|reichenau|trier|cologne|köln|echternach|fulda|regensburg|bavaria|saxony|hildesheim|corvey|luxembourg|switzerland|austria|salzburg|mainz|lotharingia|lorraine", "", 901, 1060, 0, ""),
    ("Mozarabic / Visigothic", "style", "Western Europe", "Latin (Visigothic script)", "", "", "", "", r"spain|castile|le[oó]n|asturias|catalonia|navarre|aragon|galicia|portugal|al-andalus|visigoth|mozarab", "", 711, 1100, 0, ""),
    ("Romanesque", "style", "Western Europe", "Latin", "", "", "", "", W_ORIGIN, "", 1061, 1200, 0, ""),
    ("Romanesque", "style", "Western Europe", "Latin, vernaculars", "", "", "", W_LANG, "", "", 1061, 1200, 0, "language and date only"),
    ("Gothic: Parisian", "style", "Western Europe", "Latin, French", "", "", "", "", r"^paris$|île-de-france|ile-de-france", "", 1200, 1420, 0, ""),
    ("Gothic: French and Northern French", "style", "Western Europe", "Latin, French", "", "", "", "", r"france|normandy|picardy|champagne|burgund|artois|northern france|anjou|brittany|provence|avignon|lorraine", "", 1200, 1420, 0, ""),
    ("Gothic: English", "style", "Western Europe", "Latin, Anglo-Norman, Middle English", "", "", "", "", r"england|english|britain|east anglia|london|oxford|wales|scotland|ireland", "", 1200, 1420, 0, ""),
    ("Gothic: Bohemian", "style", "C&E Europe incl. Armenia/Georgia", "Latin, Czech, German", "", "", "", "", r"bohemia|prague|czech|moravia|silesia", "", 1300, 1450, 0, ""),
    ("Gothic: Central European (Poland, Hungary)", "style", "C&E Europe incl. Armenia/Georgia", "Latin", "", "", "", "", r"poland|kraków|cracow|hungary|slovakia|croatia|dalmatia|slovenia|lithuania|transylvania", "", 1200, 1500, 0, ""),
    ("Gothic: Italian (Bologna, Florence, Siena, Lombardy)", "style", "Western Europe", "Latin, Italian", "", "", "", "", r"ital|bologna|florence|siena|venice|lombard|milan|naples|tuscan|perugia|padua|genoa|rome\b|sicily|papal", "", 1200, 1420, 0, ""),
    ("Gothic: German and Austrian", "style", "Western Europe", "Latin, Middle High German", "", "", "", "", r"german|holy roman|austria|bavaria|swabia|saxony|rhine|switzerland|franconia|cologne|westphal|alsace", "", 1200, 1450, 0, ""),
    ("Gothic: Low Countries", "style", "Western Europe", "Latin, Middle Dutch, French", "", "", "", "", r"flanders|belgium|netherlands|low countries|brabant|hainaut|holland|utrecht|liège|bruges|ghent|tournai", "", 1200, 1420, 0, ""),
    ("Gothic: Iberian", "style", "Western Europe", "Latin, Castilian, Catalan, Portuguese", "", "", "", "", r"spain|castile|le[oó]n|aragon|catalonia|navarre|portugal|valencia|majorca|galicia", "", 1200, 1450, 0, ""),
    ("Flemish / Ghent-Bruges and Burgundian Netherlands", "style", "Western Europe", "Latin, French, Middle Dutch", "", "", "", "", r"flanders|belgium|netherlands|low countries|brabant|hainaut|holland|bruges|ghent|utrecht|burgundian netherlands|tournai|valenciennes", "", 1421, 1580, 0, ""),
    ("French late Gothic and Renaissance (Fouquet, Bourdichon)", "style", "Western Europe", "Latin, Middle French", "", "", "", "", r"france|paris|tours|rouen|normandy|burgund|anjou|bourges|loire|lyon|provence|avignon", "", 1421, 1600, 0, ""),
    ("Italian Renaissance illumination", "style", "Western Europe", "Latin, Italian", "", "", "", "", r"ital|florence|ferrara|milan|venice|naples|rome\b|lombard|bologna|mantua|urbino|siena|tuscan|papal", "", 1421, 1600, 0, ""),
    ("Hungarian Corvinian", "style", "C&E Europe incl. Armenia/Georgia", "Latin", "", "", r"corvin", "", "", "", "", "", 1, ""),
    ("German / Austrian late Gothic and Renaissance", "style", "Western Europe", "Latin, Early New High German", "", "", "", "", r"german|holy roman|austria|bavaria|swabia|saxony|rhine|switzerland|franconia|nuremberg|augsburg|bohemia|prague", "", 1451, 1600, 0, ""),
    ("English late medieval", "style", "Western Europe", "Latin, Middle English", "", "", "", "", r"england|english|britain|wales|scotland|ireland", "", 1421, 1600, 0, ""),
    ("Iberian late Gothic and Renaissance", "style", "Western Europe", "Latin, Castilian, Catalan, Portuguese", "", "", "", "", r"spain|castile|le[oó]n|aragon|catalonia|navarre|portugal|valencia|majorca", "", 1451, 1600, 0, ""),
    ("Central and Eastern European manuscripts (1500+)", "style", "C&E Europe incl. Armenia/Georgia", "Latin, vernaculars", "", "", "", "", r"poland|hungary|bohemia|czech|slovakia|croatia|lithuania|transylvania|romania", "", 1451, "", 1, ""),
    ("Western European manuscripts, early modern (1600+)", "style", "Western Europe", "Latin, vernaculars", "", "", "", "", W_ORIGIN, "", 1601, "", 0, "post-medieval; low priority"),
    ("Western European manuscripts, early medieval (unlocalised, to 1060)", "style", "Western Europe", "Latin", "", "", "", W_LANG, "", "", 651, 1060, 0, "language and date only"),
    ("Western European manuscripts, Gothic (unlocalised, 1201-1450)", "style", "Western Europe", "Latin, vernaculars", "", "", "", W_LANG, "", "", 1201, 1450, 0, "language and date only"),
    ("Western European manuscripts, late medieval/Renaissance (unlocalised, 1451-1600)", "style", "Western Europe", "Latin, vernaculars", "", "", "", W_LANG, "", "", 1451, 1600, 0, "language and date only"),
    ("Western European manuscripts, early modern (1600+)", "style", "Western Europe", "Latin, vernaculars", "", "", "", W_LANG, "", "", 1601, "", 0, "language and date only"),
    ("Western European manuscripts (undated)", "style", "Western Europe", "Latin, vernaculars", "", "", "", W_LANG, "", "", "", "", 1, "language only"),
    ("Western European manuscripts (undated)", "style", "Western Europe", "Latin, vernaculars", "", "", "", "", W_ORIGIN, "", "", "", 1, "origin only"),
    # ---- genres (multi-tag, cross-cutting)
    ("Books of Hours", "genre", "Western Europe", "Latin, French, Dutch", "", r"book of hours", "", "", "", "", "", "", 1, ""),
    ("Books of Hours", "genre", "Western Europe", "Latin, French, Dutch", r"book of hours", "", r"book of hours|hours of |heures|horae|stundenbuch|getijdenboek|libro de horas|libro d'ore|livre d'heures|getijden", "", "", "", "", "", 1, ""),
    ("Beatus manuscripts", "genre", "Western Europe", "Latin (Visigothic script)", "", r"beatus", "", "", "", "", "", "", 1, ""),
    ("Beatus manuscripts", "genre", "Western Europe", "Latin", "", "", r"beatus|commentary on the apocalypse|liebana", "", "", "", "", "", 1, ""),
    ("Gospel books", "genre", "", "", "", r"gospel book|evangeliary|tetraevangel", "", "", "", "", "", "", 1, ""),
    ("Gospel books", "genre", "", "", "", "", r"gospels|evangeliar|evangeliary|evangelistary|evangéliaire|tetraevangel|gospel book|четвероевангел|ավետարան", "", "", "", "", "", 1, ""),
    ("Psalters", "genre", "", "", "", r"psalter", r"psalter|psautier|psalterium", "", "", "", "", "", 1, ""),
    ("Apocalypses (non-Beatus)", "genre", "Western Europe", "Latin, Anglo-Norman", "", "", r"apocalypse|apocalypsis", "", "", "", "", "", 1, ""),
    ("Bibles moralisées and illustrated Bibles", "genre", "Western Europe", "Latin, French", "", r"bible moralis|biblical manuscript", r"bible", "", "", "", "", "", 1, ""),
    ("Bestiaries", "genre", "Western Europe", "Latin, Anglo-Norman", "", r"bestiary", r"bestiar", "", "", "", "", "", 1, ""),
    ("Haggadot", "genre", "", "Hebrew", "", r"haggadah", r"haggad", "", "", "", "", "", 1, ""),
    ("Mahzorim and Hebrew Bibles", "genre", "", "Hebrew", "", "", r"mahzor|ma[hḥ]zor|mishneh torah|hebrew bible|pentateuch", r"hebrew", "", "", "", "", 1, ""),
    ("Exultet rolls", "genre", "Western Europe", "Latin (Beneventan)", "", r"exultet", r"exultet", "", "", "", "", "", 1, ""),
    ("Chronicles and illustrated histories", "genre", "", "", "", r"illustrated chronicle", r"chronicle|chroniques|chronik|cronaca|crónica|skylitzes|grandes chroniques", "", "", "", "", "", 1, ""),
    ("Kalpasutra and Jain illustrated texts", "genre", "South Asia", "Prakrit", "", "", r"kalpa.?s[uū]tra|kalakacharya|k[aā]lak[aā]c[aā]rya", "", "", "", "", "", 1, ""),
    ("Prajnaparamita and Buddhist illustrated sutras", "genre", "", "Sanskrit, Pali, Classical Chinese, Tibetan", "", r"ornamental sutra|ikkan|kammava", r"prajn|prajñ|sutra|sūtra|ky[oō]\b|kammav|phra malai", "", "", "", "", "", 1, ""),
    ("Emakimono (narrative handscrolls)", "genre", "Japan", "Japanese", r"emaki|yamato-e", r"emaki", r"emaki|e-maki|monogatari emaki|engi emaki", "", "", "", "", "", 1, ""),
    ("Shahnameh and Persian illustrated epics (see islamic_world.py)", "genre", "Islamic world", "Persian", "", "", r"shahnam|shāhnāma|shahnama|khamsa|haft awrang|book of kings", "", "", "", "", "", 1, "covered by islamic_world.py"),
    ("Mesoamerican screenfold codices", "genre", "Mesoamerica", "pictography", "", r"mesoamerican codex|colonial codex", "", "", "", "", "", "", 1, ""),
    ("Palm-leaf manuscripts", "genre", "", "", "", r"palm-leaf|lontar|geguritan|kakawin|kidung", "", "", "", "", "", "", 1, ""),
    ("Scrolls and rolls", "genre", "", "", "", r"scroll|rotulus|roll\b|emaki", "", "", "", "", "", "", 1, ""),
]
RULE_FIELDS = ["tradition", "kind", "region", "script_language", "style_re", "class_re", "label_re", "lang_re",
               "origin_re", "collection_re", "year_min", "year_max", "undated_ok", "note"]
# Linking tradition nodes to Wikidata style items (label regexes over harvested style items).
TRADITION_STYLE_LINKS = {
    "Insular (Hiberno-Saxon)": r"^(art of insular illumination|insular art)$",
    "Carolingian": r"^(art of carolingian illumination|carolingian art)$",
    "Ottonian": r"^(art of ottonian illumination|ottonian art)$",
    "Merovingian": r"^art of merovingian illumination$",
    "Anglo-Saxon (Winchester school)": r"^art of anglo-saxon illumination$",
    "Mozarabic / Visigothic": r"^(art of illumination in early medieval spain|mozarabic art)$",
    "Romanesque": r"^art of +romanesque illumination$",
    "Mosan / Romanesque": r"^art of +romanesque illumination$",
    "Late Antique and Early Christian": r"^art of late antique illumination$",
    "Gothic (style recorded)": r"^art of gothic illumination$",
    "Gothic: French and Northern French": r"^art of gothic illumination$",
    "International Gothic": r"^international gothic$",
    "Renaissance illumination": r"^art of renaissance illumination$",
    "Italian Renaissance illumination": r"^art of renaissance illumination$",
    "Ghent-Bruges / Flemish illumination": r"^(ghent-bruges school|art of netherlandish illumination)$",
    "Flemish / Ghent-Bruges and Burgundian Netherlands": r"^(ghent-bruges school|art of netherlandish illumination)$",
    "Byzantine (style recorded)": r"^art of byzantine illumination$",
    "Byzantine, Middle (843-1204)": r"^macedonian renaissance$",
    "Byzantine, Early (to 843)": r"^art of byzantine illumination$",
    "Byzantine, Palaiologan (1204-1453)": r"^art of byzantine illumination$",
    "Coptic": r"^art of coptic illumination$",
    "Ethiopian (Ge'ez)": r"^art of ethiopian illumination$",
    "Ethiopian (Ge'ez), early (to 1500)": r"^art of ethiopian illumination$",
    "Ethiopian (Ge'ez), Gondarine and later": r"^art of ethiopian illumination$",
    "Hebrew manuscripts (unlocalised)": r"^art of jewish illumination$",
    "Armenian: Cilician school": r"^ci?cilian school of armenian miniature painting$",
    "Armenian: Glajor (Gladzor) school": r"^gladzor +school of armenian miniature painting$",
    "Armenian: Syunik / Tatev school": r"^tatev school of armenian miniature painting$",
    "Armenian: Vaspurakan school": r"^vaspurakan school of armenian miniature painting$",
    "Armenian: Crimean school": r"^crimean school of armenian miniature painting$",
    "Armenian: Ani / early Armenian (to 1200)": r"^ani school of armenian miniature painting$",
    "Armenian (later or unlocalised)": r"^art of armenian illumination$",
    "Japanese emaki (Yamato-e)": r"^(yamato-e|emakimono)$",
    "Emakimono (narrative handscrolls)": r"^emakimono$",
    "Rajput / Pahari illustrated manuscripts": r"^rajput painting$",
    "Islamic book arts: Arabic (see islamic_world.py)": r"^art of islamic illumination$",
    "Islamic book arts: Ottoman (see islamic_world.py)": r"^ottoman illumination$",
    "Georgian": r"^georgian art$",
    "Aztec / Nahua codices (pre-conquest)": r"^aztec art$",
}
# Traditions named in the brief: gap check (expected node, minimum items before it counts as covered).
EXPECTED = [
    "Byzantine", "Armenian: Cilician", "Armenian: Vaspurakan", "Armenian: Glajor", "Armenian: Syunik",
    "Georgian", "Ethiopian", "Coptic", "Syriac", "Insular", "Carolingian", "Ottonian", "Mozarabic",
    "Beatus", "Romanesque", "Gothic: Parisian", "Gothic: English", "Gothic: Bohemian", "Books of Hours",
    "Hebrew: Sephardi", "Hebrew: Ashkenazi", "Mixtec", "Aztec", "Maya", "Mesoamerican codices, colonial",
    "Jain", "Pala", "Odia", "Balinese", "Thai samut khoi", "Burmese parabaik", "Tibetan", "Emakimono",
    "Japanese illustrated sutras", "Chinese illustrated", "Dunhuang", "Korean", "Andean", "Nepalese",
    "Sogdian", "Mongolian",
]
GAP_MIN = 10


# ------------------------------------------------------------------- SPARQL

def run_query(query, retries=4):
    body = (PREFIXES + query)
    for ep in list(dict.fromkeys([ENDPOINT[0], "qlever"])):
        data = None
        for attempt in range(retries):
            req = urllib.request.Request(ENDPOINTS[ep], data=urllib.parse.urlencode({"query": body}).encode(), headers={
                "User-Agent": UA, "Accept": "application/sparql-results+json",
                "Content-Type": "application/x-www-form-urlencoded"})
            try:
                with urllib.request.urlopen(req, timeout=300) as r:
                    data = json.loads(r.read().decode("utf-8"), strict=False)
                break
            except urllib.error.HTTPError as e:
                msg = e.read()[:160]
                if e.code in (400,):
                    print(f"    {ep} HTTP 400: {msg!r}")
                    break
                if e.code == 403:
                    print(f"    {ep} HTTP 403, giving up on this endpoint")
                    break
                wait = int(e.headers.get("Retry-After") or 0) or min(120, 10 * 2 ** attempt)
                print(f"    {ep} HTTP {e.code}, retrying in {wait}s")
                time.sleep(wait)
            except Exception as e:  # timeouts, resets, truncated JSON
                print(f"    {ep} {type(e).__name__}: {str(e)[:100]}, retrying")
                time.sleep(min(120, 10 * 2 ** attempt))
        if data is not None:
            if ep != ENDPOINT[0]:
                print(f"    switching to {ep} for the rest of the run")
                ENDPOINT[0] = ep
            time.sleep(1)
            out = []
            for b in data["results"]["bindings"]:
                row = {}
                for k, v in b.items():
                    val = v["value"]
                    if v["type"] == "uri" and val.startswith("http://www.wikidata.org/entity/"):
                        val = val.rsplit("/", 1)[1]
                    row[k] = val
                out.append(row)
            return out
    raise RuntimeError("SPARQL query failed on every endpoint")


def cached(query, tag):
    os.makedirs(RAW, exist_ok=True)
    h = hashlib.sha1(query.encode()).hexdigest()[:16]
    path = os.path.join(RAW, f"{tag}_{h}.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    if OFFLINE[0]:
        raise RuntimeError(f"--offline and no cache for {tag}")
    print(f"  query {tag}")
    rows = run_query(query)
    with open(path + ".part", "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False)
    os.replace(path + ".part", path)
    return rows


def values(qids):
    return " ".join(f"wd:{q}" for q in qids)


def chunks(seq, n):
    seq = list(seq)
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


LABEL_LANGS = ["en", "mul", "fr", "de", "it", "es", "nl", "la", "pt", "ca", "pl", "cs", "ru", "hy", "ka",
               "id", "ban", "jv", "ja", "zh", "ko", "he", "ar", "fa", "el"]


def entity_meta(qids, tag):
    """{qid: {"label", "P17": [...], "P131": [...], "P31": [...]}} for referenced entities."""
    meta = {}
    langs = ", ".join(f'"{l}"' for l in LABEL_LANGS)
    for i, ch in enumerate(chunks(sorted(qids), 400)):
        rows = cached(f"SELECT ?e ?l WHERE {{ VALUES ?e {{ {values(ch)} }} ?e rdfs:label ?l . "
                      f"FILTER(LANG(?l) IN ({langs})) }}", f"{tag}_labels")
        best = {}
        for r in rows:
            # rank by language order; rows lack lang tag, so pick the first label seen per language query below
            best.setdefault(r["e"], []).append(r["l"])
        rows_en = cached(f"SELECT ?e ?l WHERE {{ VALUES ?e {{ {values(ch)} }} ?e rdfs:label ?l . "
                         f"FILTER(LANG(?l) = \"en\") }}", f"{tag}_labels_en")
        en = {r["e"]: r["l"] for r in rows_en}
        for q in ch:
            meta[q] = {"label": en.get(q) or (best.get(q) or [""])[0], "P17": [], "P131": [], "P31": []}
        for prop in ("P17", "P131", "P31"):
            for r in cached(f"SELECT ?e ?v WHERE {{ VALUES ?e {{ {values(ch)} }} ?e wdt:{prop} ?v }}", f"{tag}_{prop}"):
                meta[r["e"]][prop].append(r["v"])
    return meta


# ------------------------------------------------------------------ harvest

ITEM_PROPS = ["P31", "P195", "P495", "P1071", "P2596", "P571", "P135", "P136", "P170", "P407", "P282", "P361"]


def harvest_items():
    tree = cached(f"SELECT ?k WHERE {{ ?k wdt:P279* wd:{MANUSCRIPT} }}", "class_tree")
    cal = cached(f"SELECT ?k WHERE {{ ?k wdt:P279* wd:{CALLIGRAPHIC_WORK} }}", "class_tree_calligraphy")
    cal = {r["k"] for r in cal}
    tree = [r["k"] for r in tree if r["k"].startswith("Q") and r["k"] not in cal]
    counts = cached(f"SELECT ?k (COUNT(?i) AS ?n) WHERE {{ ?k wdt:P279* wd:{MANUSCRIPT} . ?i wdt:P31 ?k }} GROUP BY ?k",
                    "class_counts")
    counts = {r["k"]: int(r["n"]) for r in counts}
    cmeta = entity_meta(set(tree) | set(EXTRA_CLASSES), "classes")
    for q, lab in EXTRA_CLASSES.items():
        if cmeta[q]["label"].lower() != lab.lower():
            print(f"  WARNING extra class {q}: expected {lab!r}, Wikidata says {cmeta[q]['label']!r}")
    used = [k for k in tree if counts.get(k)]
    excluded = {k for k in used if EXCLUDE_CLASS_RE.search(cmeta[k]["label"] or "")}
    keep_classes = [k for k in used if k not in excluded]
    print(f"  manuscript classes: {len(tree)} in tree, {len(used)} with instances, {len(excluded)} excluded "
          f"({', '.join(sorted(cmeta[k]['label'] for k in excluded))}); calligraphy subtree {len(cal)} classes dropped")
    big = [k for k in keep_classes if counts.get(k, 0) > 20000]
    small = [k for k in keep_classes if k not in big]
    groups = [[k] for k in big] + [small] + [list(EXTRA_CLASSES)]
    items = collections.defaultdict(lambda: collections.defaultdict(set))
    sitelinks = {}
    for gi, grp in enumerate(groups):
        vals = values(grp)
        tag = f"g{gi}"
        for r in cached(f"SELECT ?i ?sl WHERE {{ VALUES ?k {{ {vals} }} ?i wdt:P31 ?k . ?i wikibase:sitelinks ?sl }}", f"{tag}_items"):
            sitelinks[r["i"]] = int(r["sl"])
        for prop in ITEM_PROPS:
            for r in cached(f"SELECT ?i ?v WHERE {{ VALUES ?k {{ {vals} }} ?i wdt:P31 ?k . ?i wdt:{prop} ?v }}", f"{tag}_{prop}"):
                items[r["i"]][prop].add(r["v"])
        for r in cached(f"SELECT ?i ?l WHERE {{ VALUES ?k {{ {vals} }} ?i wdt:P31 ?k . ?i rdfs:label ?l FILTER(LANG(?l) = \"en\") }}", f"{tag}_label_en"):
            items[r["i"]]["label_en"].add(r["l"])
        for lang in ("mul", "fr", "de", "it", "es", "nl", "id", "ja", "zh", "hy"):
            for r in cached(f"SELECT ?i ?l WHERE {{ VALUES ?k {{ {vals} }} ?i wdt:P31 ?k . ?i rdfs:label ?l FILTER(LANG(?l) = \"{lang}\") }}", f"{tag}_label_{lang}"):
                items[r["i"]]["label_other"].add((LABEL_LANGS.index(lang), r["l"]))
    # Extra classes outside the tree: keep only medieval / pre-modern or held items.
    extra_only = set()
    tree_set = set(keep_classes)
    for q, d in list(items.items()):
        if not (d["P31"] & tree_set) and not (d["P31"] & excluded):
            years = [year_of(v) for v in d["P571"]]
            years = [y for y in years if y is not None]
            if (years and min(years) < 1650) or (not years and d["P195"]):
                extra_only.add(q)
            else:
                del items[q]
    # Items whose only manuscript classes are excluded document types are dropped.
    dropped = 0
    for q, d in list(items.items()):
        ms = d["P31"] & (tree_set | set(EXTRA_CLASSES))
        if not ms:
            del items[q]
            dropped += 1
    print(f"  items: {len(items)} kept ({len(extra_only)} via extra classes), {dropped} document-type items dropped")
    return items, sitelinks, cmeta, excluded


def harvest_styles():
    types = values(STYLE_TYPES)
    rows = cached(f"SELECT ?s ?l ?t ?sl WHERE {{ VALUES ?t {{ {types} }} ?s wdt:P31 ?t . ?s rdfs:label ?l "
                  f"FILTER(LANG(?l) = \"en\") FILTER(REGEX(?l, \"{STYLE_LABEL_RE}\", \"i\")) ?s wikibase:sitelinks ?sl }}",
                  "styles_regex")
    styles = {}
    for r in rows:
        if re.search(r"gothic (rock|revival|horror|fiction|literature|novel|metal)|neo-gothic|raygun|new gothic|postmodern", r["l"], re.I):
            continue
        s = styles.setdefault(r["s"], {"label": r["l"], "types": set(), "sitelinks": int(r["sl"]), "source": "label regex"})
        s["types"].add(STYLE_TYPES[r["t"]])
    return styles


def harvest_illuminators():
    base = f"?h wdt:P106 wd:{ILLUMINATOR} ."
    people = {}
    for r in cached(f"SELECT ?h ?sl WHERE {{ {base} ?h wikibase:sitelinks ?sl }}", "illum_items"):
        people[r["h"]] = collections.defaultdict(set, {"sitelinks": int(r["sl"])})
    for prop in ("P135", "P27", "P19", "P937", "P569", "P570", "P1317", "P2031", "P106"):
        for r in cached(f"SELECT ?h ?v WHERE {{ {base} ?h wdt:{prop} ?v }}", f"illum_{prop}"):
            if r["h"] in people:
                people[r["h"]][prop].add(r["v"])
    for r in cached(f"SELECT ?h ?l WHERE {{ {base} ?h rdfs:label ?l FILTER(LANG(?l) = \"en\") }}", "illum_label_en"):
        if r["h"] in people:
            people[r["h"]]["label"] = r["l"]
    for lang in ("mul", "fr", "de", "it", "hy"):
        for r in cached(f"SELECT ?h ?l WHERE {{ {base} ?h rdfs:label ?l FILTER(LANG(?l) = \"{lang}\") }}", f"illum_label_{lang}"):
            if r["h"] in people and not people[r["h"]].get("label"):
                people[r["h"]]["label"] = r["l"]
    return people


# ------------------------------------------------------------------ rules

def load_rules(reset):
    if reset or not os.path.exists(RULES_CSV):
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(RULES_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["rule_id"] + RULE_FIELDS)
            for i, r in enumerate(DEFAULT_RULES, 1):
                w.writerow([i] + list(r))
        print(f"  wrote rule table {RULES_CSV} ({len(DEFAULT_RULES)} rules)")
    rules = []
    with open(RULES_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            r = dict(row)
            for k in ("style_re", "class_re", "label_re", "lang_re", "origin_re", "collection_re"):
                r[k + "_c"] = re.compile(r[k], re.I) if r[k] else None
            r["ymin"] = int(r["year_min"]) if r["year_min"] not in ("", None) else None
            r["ymax"] = int(r["year_max"]) if r["year_max"] not in ("", None) else None
            r["undated"] = str(r["undated_ok"]).strip() in ("1", "true", "True")
            rules.append(r)
    return rules


FIELD_OF = {"style_re": "styles", "class_re": "classes", "label_re": "labels", "lang_re": "langs",
            "origin_re": "origins", "collection_re": "collections"}


def rule_matches(r, f, year, ignore=()):
    fired = []
    for k, field in FIELD_OF.items():
        rx = r[k + "_c"]
        if rx is None:
            continue
        if k in ignore:
            return None
        if not any(rx.search(v) for v in f[field] if v):
            return None
        fired.append(field)
    if not fired and r["ymin"] is None and r["ymax"] is None:
        return None
    if r["ymin"] is not None or r["ymax"] is not None:
        if year is None:
            if not r["undated"]:
                return None
        else:
            if r["ymin"] is not None and year < r["ymin"]:
                return None
            if r["ymax"] is not None and year > r["ymax"]:
                return None
            fired.append("date")
    return fired


def assign(rules, f, year, ignore=()):
    style, basis, genres = None, "", []
    for r in rules:
        if r["kind"] == "genre":
            if rule_matches(r, f, year, ignore) is not None and r["tradition"] not in genres:
                genres.append(r["tradition"])
            continue
        if style is None:
            fired = rule_matches(r, f, year, ignore)
            if fired is not None:
                style = r
                basis = ("recorded style" if "styles" in fired else "rule") + f" #{r['rule_id']}: " + "+".join(fired)
    return style, basis, genres


# ------------------------------------------------------------------ main

def pct(vals, p):
    vals = sorted(vals)
    if not vals:
        return None
    return vals[min(len(vals) - 1, int(round(p / 100 * (len(vals) - 1))))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", choices=sorted(ENDPOINTS), default="wdqs")
    ap.add_argument("--reset-rules", action="store_true", help="rewrite manuscripts_rules.csv from DEFAULT_RULES")
    ap.add_argument("--offline", action="store_true", help="use cached SPARQL results only")
    args = ap.parse_args()
    ENDPOINT[0] = args.endpoint
    OFFLINE[0] = args.offline

    print("1. manuscript items")
    items, sitelinks, cmeta, excluded = harvest_items()
    print("2. illumination styles and illuminators")
    styles = harvest_styles()
    seed_meta = entity_meta(STYLE_SEEDS, "seeds")
    for q, lab in STYLE_SEEDS.items():
        got = seed_meta[q]["label"]
        if got.lower() != lab.lower():
            print(f"  WARNING style seed {q}: expected {lab!r}, Wikidata says {got!r}; skipped")
            continue
        styles.setdefault(q, {"label": got, "types": set(), "sitelinks": 0, "source": "seed"})
    people = harvest_illuminators()
    print(f"  {len(styles)} style items, {len(people)} illuminators")

    print("3. referenced entities")
    refs = set()
    for d in items.values():
        for p in ("P31", "P195", "P495", "P1071", "P2596", "P135", "P136", "P170", "P407", "P282"):
            refs |= {v for v in d[p] if v.startswith("Q")}
    for d in people.values():
        for p in ("P135", "P27", "P19", "P937"):
            refs |= {v for v in d[p] if v.startswith("Q")}
    refs |= set(styles)
    meta = entity_meta(refs, "refs")
    # Countries / parents of origin places, one more hop for labels.
    hop = set()
    for q, m in meta.items():
        hop |= set(m["P17"]) | set(m["P131"])
    hop -= set(meta)
    meta.update(entity_meta(hop, "refs_hop"))
    for q in styles:
        if q in meta and not styles[q].get("sitelinks"):
            pass
    sl_rows = cached(f"SELECT ?s ?sl WHERE {{ VALUES ?s {{ {values(styles)} }} ?s wikibase:sitelinks ?sl }}", "styles_sitelinks")
    for r in sl_rows:
        styles[r["s"]]["sitelinks"] = int(r["sl"])
    # Style-type values used on manuscripts count as style items too.
    style_type_set = set(STYLE_TYPES) | {"Q11514315", "Q465299", "Q11042"}
    for d in items.values():
        for p in ("P135", "P136", "P2596"):
            for v in d[p]:
                if v in meta and set(meta[v]["P31"]) & set(STYLE_TYPES) and v not in styles:
                    styles[v] = {"label": meta[v]["label"], "types": set(), "sitelinks": 0, "source": f"{p} on manuscripts"}

    def lab(q):
        return (meta.get(q) or {}).get("label") or q

    def origin_labels(qs):
        out = set()
        for q in qs:
            m = meta.get(q)
            if not m:
                continue
            out.add(m["label"])
            for p in m["P17"] + m["P131"]:
                out.add(lab(p))
        out.discard("undetermined geographic location")
        return out

    # Inherit missing facts from parent manuscripts (leaves and folios).
    for q, d in items.items():
        for parent in d["P361"]:
            pd = items.get(parent)
            if not pd:
                continue
            for p in ("P407", "P282", "P495", "P1071", "P2596", "P571", "P135", "P195"):
                if not d[p] and pd[p]:
                    d[p] = set(pd[p])
                    d["inherited"].add(p)

    rules = load_rules(args.reset_rules)
    print("4. assigning traditions")
    out_items = []
    for q, d in items.items():
        label = next(iter(sorted(d["label_en"])), "") or (sorted(d["label_other"])[0][1] if d["label_other"] else "")
        years = [y for y in (year_of(v) for v in d["P571"]) if y is not None]
        year = min(years) if years else None
        classes = [lab(c) for c in sorted(d["P31"])]
        f = {
            "styles": [lab(v) for v in d["P135"] | d["P136"] | d["P2596"]],
            "classes": classes,
            "labels": [label] + [l for _, l in sorted(d["label_other"])],
            "langs": [lab(v) for v in d["P407"] | d["P282"]],
            "origins": sorted(origin_labels(d["P495"] | d["P1071"] | d["P2596"])),
            "collections": [lab(v) for v in d["P195"]],
        }
        style, basis, genres = assign(rules, f, year)
        illum = any(ILLUMINATED_CLASS_RE.search(c) for c in classes)
        out_items.append({
            "qid": q, "label": label, "classes": "; ".join(classes), "illuminated_class": int(illum),
            "year": year if year is not None else "", "languages_scripts": "; ".join(f["langs"]),
            "origin": "; ".join(lab(v) for v in sorted(d["P495"] | d["P1071"])),
            "origin_resolved": "; ".join(f["origins"]), "culture": "; ".join(lab(v) for v in sorted(d["P2596"])),
            "styles_recorded": "; ".join(lab(v) for v in sorted(d["P135"] | d["P136"])),
            "creators": "; ".join(lab(v) for v in sorted(d["P170"])),
            "creator_qids": " ".join(sorted(d["P170"])),
            "collections": "; ".join(f["collections"]), "part_of": " ".join(sorted(d["P361"])),
            "inherited_from_parent": " ".join(sorted(d["inherited"])),
            "sitelinks": sitelinks.get(q, 0),
            "tradition": style["tradition"] if style else "", "region": style["region"] if style else "",
            "genres": "; ".join(genres), "basis": basis,
            "covered_elsewhere": "islamic_world.py" if style and "islamic_world" in (style["note"] or "") else "",
        })

    # Illuminators: origin/style rules only (no language, label or class evidence).
    out_people = []
    for q, d in people.items():
        y = None
        for p in ("P1317", "P2031"):
            ys = [year_of(v) for v in d[p]]
            ys = [v for v in ys if v is not None]
            if ys:
                y = min(ys)
                break
        if y is None:
            ys = [year_of(v) for v in d["P569"]]
            ys = [v for v in ys if v is not None]
            y = min(ys) + 30 if ys else None
        if y is None:
            ys = [year_of(v) for v in d["P570"]]
            ys = [v for v in ys if v is not None]
            y = min(ys) - 20 if ys else None
        f = {"styles": [lab(v) for v in d["P135"]], "classes": [], "labels": [], "langs": [],
             "origins": sorted(origin_labels(d["P27"] | d["P19"] | d["P937"])), "collections": []}
        style, basis, _ = assign(rules, f, y, ignore=("class_re", "label_re", "lang_re", "collection_re"))
        out_people.append({
            "qid": q, "label": d.get("label", ""), "floruit_est": y if y is not None else "",
            "movement": "; ".join(lab(v) for v in sorted(d["P135"])),
            "citizenship": "; ".join(lab(v) for v in sorted(d["P27"])),
            "birth_place": "; ".join(lab(v) for v in sorted(d["P19"])),
            "work_location": "; ".join(lab(v) for v in sorted(d["P937"])),
            "sitelinks": d.get("sitelinks", 0),
            "tradition": style["tradition"] if style else "", "region": style["region"] if style else "",
            "basis": basis,
        })

    # ---------------- traditions
    rule_info = collections.OrderedDict()
    for r in rules:
        ri = rule_info.setdefault(r["tradition"], {"kind": r["kind"], "region": r["region"], "script": r["script_language"],
                                                   "ymin": [], "ymax": [], "note": set()})
        if r["ymin"] is not None:
            ri["ymin"].append(r["ymin"])
        if r["ymax"] is not None:
            ri["ymax"].append(r["ymax"])
        if r["note"]:
            ri["note"].add(r["note"])
    by_trad = collections.defaultdict(list)
    for it in out_items:
        if it["tradition"]:
            by_trad[it["tradition"]].append(it)
        for g in filter(None, it["genres"].split("; ")):
            by_trad[g].append(it)
    illum_by_trad = collections.defaultdict(list)
    for p in out_people:
        if p["tradition"]:
            illum_by_trad[p["tradition"]].append(p)

    islamic_note = ""
    if os.path.exists(ISLAMIC_DYN):
        with open(ISLAMIC_DYN, encoding="utf-8") as fh:
            dyn = list(csv.DictReader(fh))
        ba = sum(int(r.get("book_arts_objects") or 0) for r in dyn)
        nsch = 0
        if os.path.exists(ISLAMIC_SCH):
            with open(ISLAMIC_SCH, encoding="utf-8") as fh:
                nsch = sum(1 for r in csv.DictReader(fh) if r["kind"] == "school")
        islamic_note = f"islamic_world.py: {ba} book-arts objects across {len(dyn)} dynasties, {nsch} schools"

    trad_rows = []
    for name, ri in rule_info.items():
        its = by_trad.get(name, [])
        years = [it["year"] for it in its if it["year"] != ""]
        cols = collections.Counter(c for it in its for c in filter(None, it["collections"].split("; ")))
        creators = collections.Counter(c for it in its for c in filter(None, it["creators"].split("; ")) if c != "anonymous")
        for p in sorted(illum_by_trad.get(name, []), key=lambda p: -p["sitelinks"]):
            if p["label"] and p["label"] not in creators:
                creators[p["label"]] = 0
        samples = sorted(its, key=lambda it: (-it["sitelinks"], -it["illuminated_class"]))[:8]
        link_rx = TRADITION_STYLE_LINKS.get(name)
        qid = ""
        if link_rx:
            hits = [s for s, v in styles.items() if re.search(link_rx, v["label"], re.I)]
            qid = " ".join(sorted(hits, key=lambda s: -styles[s]["sitelinks"]))
        rmin = min(ri["ymin"]) if ri["ymin"] else ""
        rmax = max(ri["ymax"]) if ri["ymax"] else ""
        note = "; ".join(sorted(ri["note"]))
        if "islamic_world" in note and islamic_note:
            note += f"; {islamic_note}"
        expected_hit = any(e.lower() in name.lower() for e in EXPECTED)
        trad_rows.append({
            "label": name, "qid": qid, "kind": ri["kind"], "region": ri["region"], "script_language": ri["script"],
            "era_rule": f"{rmin}-{rmax}" if (rmin != "" or rmax != "") else "",
            "era_items_p5_p95": f"{pct(years, 5)}-{pct(years, 95)}" if years else "",
            "n_manuscripts": len(its), "n_illuminated": sum(it["illuminated_class"] for it in its),
            "n_sitelinked": sum(1 for it in its if it["sitelinks"] > 0),
            "n_recorded_style": sum(1 for it in its if it["basis"].startswith("recorded")),
            "n_illuminators": len(illum_by_trad.get(name, [])),
            "top_holding_libraries": "; ".join(f"{c} ({n})" for c, n in cols.most_common(6)),
            "named_illuminators": "; ".join(f"{c} ({n})" if n else c for c, n in creators.most_common(10)),
            "sample_manuscripts": "; ".join(f"{it['label'] or '?'} ({it['qid']})" for it in samples),
            "sources": "Wikidata" + (f"; {islamic_note}" if "islamic_world" in note and islamic_note else ""),
            "covered_elsewhere": "islamic_world.py" if "islamic_world" in note else "",
            "gap": "GAP" if expected_hit and len(its) < GAP_MIN else "",
            "note": note,
        })
    linked = {q for r in trad_rows for q in r["qid"].split()}
    for q, s in sorted(styles.items(), key=lambda kv: -kv[1]["sitelinks"]):
        if q in linked:
            continue
        n = sum(1 for d in items.values() if q in (d["P135"] | d["P136"] | d["P2596"]))
        trad_rows.append({
            "label": s["label"], "qid": q, "kind": "wikidata style (unlinked)", "region": "", "script_language": "",
            "era_rule": "", "era_items_p5_p95": "", "n_manuscripts": n, "n_illuminated": "", "n_sitelinked": "",
            "n_recorded_style": n, "n_illuminators": "", "top_holding_libraries": "", "named_illuminators": "",
            "sample_manuscripts": "", "sources": f"Wikidata ({s['source']}; sitelinks {s['sitelinks']})",
            "covered_elsewhere": "", "gap": "", "note": ", ".join(sorted(s["types"])),
        })

    # ---------------- regions
    reg_rows = []
    for reg in REGIONS:
        its = [it for it in out_items if it["region"] == reg]
        trs = [r for r in trad_rows if r["region"] == reg and r["kind"] == "style"]
        gaps = [r["label"] for r in trs if r["gap"]]
        reg_rows.append({
            "region": reg, "n_traditions": len(trs), "n_traditions_with_items": sum(1 for r in trs if r["n_manuscripts"]),
            "n_manuscripts": len(its), "n_illuminated": sum(it["illuminated_class"] for it in its),
            "n_sitelinked": sum(1 for it in its if it["sitelinks"] > 0),
            "n_recorded_style": sum(1 for it in its if it["basis"].startswith("recorded")),
            "n_illuminators": sum(1 for p in out_people if p["region"] == reg),
            "top_traditions": "; ".join(f"{r['label']} ({r['n_manuscripts']})" for r in sorted(trs, key=lambda r: -r["n_manuscripts"])[:6]),
            "gaps": "; ".join(gaps),
            "flag": ("covered by islamic_world.py" if reg == "Islamic world" else
                     "EMPTY" if not its else "THIN" if len(its) < 50 or sum(1 for it in its if it["sitelinks"] > 0) < 10 else ""),
        })
    unassigned = [it for it in out_items if not it["tradition"]]

    os.makedirs(OUT_DIR, exist_ok=True)

    def write(name, rows):
        path = os.path.join(OUT_DIR, name)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"  wrote {path} ({len(rows)} rows)")

    out_items.sort(key=lambda it: (it["region"] or "~", it["tradition"] or "~", -it["sitelinks"]))
    write("manuscripts_items.csv", out_items)
    write("manuscripts_traditions.csv", trad_rows)
    write("manuscripts_illuminators.csv", sorted(out_people, key=lambda p: (p["region"] or "~", -p["sitelinks"])))
    write("manuscripts_regions.csv", reg_rows)

    print("\nSummary")
    print(f"  items {len(out_items)}; assigned {len(out_items) - len(unassigned)}; unassigned {len(unassigned)}; "
          f"illuminated-class {sum(it['illuminated_class'] for it in out_items)}; sitelinked {sum(1 for it in out_items if it['sitelinks'])}")
    print(f"  recorded style basis {sum(1 for it in out_items if it['basis'].startswith('recorded'))}; "
          f"illuminators {len(out_people)} ({sum(1 for p in out_people if p['tradition'])} placed)")
    print(f"  {'region':36} {'trad':>4} {'mss':>7} {'illum':>6} {'sitel':>6} {'illmrs':>6}  flag / gaps")
    for r in reg_rows:
        print(f"  {r['region']:36} {r['n_traditions_with_items']:>4} {r['n_manuscripts']:>7} {r['n_illuminated']:>6} "
              f"{r['n_sitelinked']:>6} {r['n_illuminators']:>6}  {r['flag']} {r['gaps']}")
    ua = collections.Counter(l for it in unassigned for l in (it["languages_scripts"].split("; ") if it["languages_scripts"] else ["(no language)"]))
    print("  unassigned by language:", "; ".join(f"{k} {v}" for k, v in ua.most_common(15)))


if __name__ == "__main__":
    main()
