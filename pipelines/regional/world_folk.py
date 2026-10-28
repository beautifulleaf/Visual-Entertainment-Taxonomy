"""Non-European folk and vernacular visual traditions sweep (visual-art-plan.md §2A, §2.2).

Companion to europe_folk.py, with the same gathering scope: NODES (named
traditions) plus EVIDENCE (object counts, holding institutions, representative
works). The regional museum sweeps already hold cultures x media (e.g. "Navajo /
textiles"), but traditions named by TECHNIQUE or PLACE (Kalamkari, bogolan,
alebrijes, tivaevae, ...) do not exist there as nodes. This sweep adds them.

Sources:
  1. Wikidata, worldwide outside Europe. The same root classes and filters as
     europe_folk.py (folk art, craft, textile art, embroidery, pottery style,
     painting technique, decorative painting, rug style, ... plus every item with
     an intangible-heritage status (P3259) or an HCA Red List ID (P6599)),
     reusing europe_folk's cached root-member lists and item details
     (data/raw/regional/wikidata_europe_folk) and fetching details only for
     items whose country (P17/P495) lies wholly outside Europe. Kept when the
     item's country is non-European (a country item with a P30 continent other
     than Europe and not one of europe_folk's European/Caucasian countries;
     Turkey and Kazakhstan are included here), or, without a country, when its
     location (P131/P276/P2341/P1071) or a non-European demonym / people in its
     label, description or class labels places it outside Europe. Items already
     in europe_folk_traditions.csv are skipped. New queries are cached under
     data/raw/regional/wikidata_world_folk/; one query at a time, QLever mirror
     as fallback.
  2. A curated list (TRADITIONS below, ~280 entries) of named non-European folk
     and vernacular traditions: label, aliases (with native terms), country,
     people, region, medium, and a matching rule. A rule has a strong regex
     (distinctive names: "kalamkari", "bogolan", "tivaevae") that matches on its
     own, and optionally a weak regex (generic words: "batik", "bead", "kilim",
     "pottery") that only counts when a context regex (place / people:
     "java|indonesia", "zulu", "navajo|dine") also matches the object text.
     Linked to Wikidata items by label/alias (kept nodes first, then a label
     lookup).
  3. Evidence from cached museum data only (no new requests): the Met CSV, the
     AIC dump, and the regional object tables in data/interim/regional/
     (africa, africa_oceania_targeted, americas_oceania, south_southeast_asia,
     east_asia, himalaya_central_asia, islamic, smithsonian, world_extra,
     gap_sweep). The text matched is title + object name/type + medium/materials
     /technique + culture + place/country + tags, ASCII-folded and lowercased.
     Per node and source: object count, holding institutions, dates, samples.
     Sources overlap (gap_sweep and world_extra re-hold some Met / AIC /
     Rijksmuseum rows), so total_objects_distinct de-duplicates by URL.

Node gain: every node is compared with the nodes gathered so far
(data/interim/unattributed_cultures.csv, data/interim/regional/*traditions*.csv,
*_cultures.csv, *_schools.csv, europe_folk_traditions.csv, gap_sweep_traditions.csv):
  known                       the tradition's name (label without parenthesis,
                              or an alias) appears as a phrase in an existing
                              node label / key;
  alias-of-existing-cell      not named anywhere, but the entry is in essence a
                              people x medium cell (field `cell`, e.g. Navajo
                              weaving = "navajo" x textiles) and that culture
                              exists as a culture node / cell;
  new                         neither.

Outputs (data/interim/regional/):
  world_folk_traditions.csv  one row per node (kind wikidata / curated; a curated
      entry linked to a kept Wikidata item shares its row).
  world_folk_objects.csv     slim evidence rows (<= 40 per node per source).

Usage: python3 pipelines/regional/world_folk.py [--skip wikidata,museums] [--delay 1.0]
"""
import argparse
import collections
import csv
import glob
import hashlib
import json
import os
import re
import sys
import time
import unicodedata

csv.field_size_limit(1 << 24)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import europe_folk as ef  # noqa: E402  (reused: roots, filters, matcher, helpers)
from europe_folk import (ROOTS, NOT_TRADITION, ICH_SIGNAL, VISUAL_SIGNAL, GENERIC_ROOTS, OBJECT_P31,  # noqa: E402
                         TRADITION_P31, NON_VISUAL_CLASS, ARTWORK_P31, BIG_MOVEMENTS, MOVEMENT_FINE_ART,
                         FOLK_WD, GramMatcher, medium_of, period_of, write, topfmt, slug, fold, batched, qlever,
                         wikidata)

ROOT = ef.ROOT
RAW = ef.RAW
MUSEUMS = ef.MUSEUMS
OUT_DIR = ef.OUT_DIR
INTERIM = os.path.join(ROOT, "data", "interim")
WD_DIR = os.path.join(RAW, "wikidata_world_folk")
EU_WD_DIR = ef.WD_DIR
MAX_EVIDENCE = 40

# ------------------------------------------------------------------ Wikidata cache

def sparql_cached(query, tag):
    """Cached SPARQL: reads europe_folk's cache (same file naming) or this sweep's, else WDQS -> QLever."""
    h = hashlib.sha1(query.encode()).hexdigest()[:16]
    for d in (WD_DIR, EU_WD_DIR):
        path = os.path.join(d, f"{tag}_{h}.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    path = os.path.join(WD_DIR, f"{tag}_{h}.json")
    try:
        rows = wikidata.sparql(query, retries=5)
    except RuntimeError:
        print("    WDQS failed repeatedly; trying the QLever mirror", flush=True)
        rows = qlever(query)
    os.makedirs(WD_DIR, exist_ok=True)
    with open(path + ".part", "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False)
    os.replace(path + ".part", path)
    time.sleep(1.0)
    return rows


# ------------------------------------------------------------------ geography

REGIONS = ["South Asia", "East Asia", "Southeast Asia", "MENA / Central Asia", "Africa",
           "Mexico / Central America & Caribbean", "South America", "North America", "Oceania"]
REGION_BY_LABEL = {}
for _reg, _names in {
    "South Asia": ["India", "Pakistan", "Bangladesh", "Sri Lanka", "Nepal", "Bhutan", "Maldives", "British Raj",
                   "Mughal Empire", "Dominion of India", "Dominion of Pakistan", "Kingdom of Nepal", "Ceylon",
                   "British Ceylon", "Kingdom of Kandy", "Maratha Empire", "Vijayanagara Empire", "Sikh Empire",
                   "Company rule in India", "Bengal Sultanate", "Princely state", "Portuguese India"],
    "East Asia": ["China", "People's Republic of China", "Republic of China", "Taiwan", "Japan", "South Korea",
                  "North Korea", "Korea", "Mongolia", "Hong Kong", "Macau", "Qing dynasty", "Ming dynasty", "Joseon",
                  "Korean Empire", "Empire of Japan", "Tokugawa shogunate", "Ryukyu Kingdom", "Song dynasty",
                  "Tang dynasty", "Yuan dynasty", "Mongol Empire", "Goryeo", "Republic of China (1912–1949)",
                  "Mongolian People's Republic", "Manchukuo", "Korea under Japanese rule", "Taiwan under Japanese rule"],
    "Southeast Asia": ["Indonesia", "Malaysia", "Philippines", "Thailand", "Vietnam", "Cambodia", "Laos", "Myanmar",
                       "Singapore", "Brunei", "Timor-Leste", "East Timor", "Dutch East Indies", "French Indochina",
                       "Siam", "Kingdom of Ayutthaya", "Rattanakosin Kingdom", "Burma", "Majapahit",
                       "Spanish East Indies", "Captaincy General of the Philippines", "British Burma",
                       "Konbaung dynasty", "Khmer Empire", "Mataram Sultanate", "Malaya", "Federation of Malaya",
                       "Straits Settlements", "Đại Việt", "Nguyễn dynasty", "South Vietnam", "North Vietnam"],
    "MENA / Central Asia": ["Turkey", "Iran", "Iraq", "Syria", "Lebanon", "Israel", "Palestine", "State of Palestine",
                            "Jordan", "Saudi Arabia", "Yemen", "Oman", "United Arab Emirates", "Qatar", "Bahrain",
                            "Kuwait", "Egypt", "Libya", "Tunisia", "Algeria", "Morocco", "Western Sahara",
                            "Sahrawi Arab Democratic Republic", "Kazakhstan", "Uzbekistan", "Turkmenistan",
                            "Kyrgyzstan", "Tajikistan", "Afghanistan", "Ottoman Empire", "Safavid Iran",
                            "Qajar Iran", "Pahlavi Iran", "Persia", "Kingdom of Egypt", "Mandatory Palestine",
                            "Emirate of Bukhara", "Khanate of Khiva", "Khanate of Kokand", "Seljuk Empire",
                            "Sultanate of Rum", "Kingdom of Iraq", "Mutawakkilite Kingdom of Yemen",
                            "Uzbek Soviet Socialist Republic", "Kazakh Soviet Socialist Republic",
                            "Kirghiz Soviet Socialist Republic", "Turkmen Soviet Socialist Republic",
                            "Tajik Soviet Socialist Republic", "Mamluk Sultanate", "Ayyubid dynasty",
                            "Fatimid Caliphate", "Abbasid Caliphate", "Umayyad Caliphate", "Timurid Empire"],
    "Mexico / Central America & Caribbean": [
        "Mexico", "Guatemala", "Belize", "Honduras", "El Salvador", "Nicaragua", "Costa Rica", "Panama", "Cuba",
        "Haiti", "Dominican Republic", "Jamaica", "Puerto Rico", "Trinidad and Tobago", "The Bahamas", "Bahamas",
        "Barbados", "Grenada", "Saint Lucia", "Dominica", "Antigua and Barbuda", "Saint Vincent and the Grenadines",
        "Saint Kitts and Nevis", "New Spain", "Guadeloupe", "Martinique", "Curaçao", "Aruba",
        "Captaincy General of Guatemala", "Federal Republic of Central America", "Second Mexican Empire"],
    "North America": ["United States", "United States of America", "Canada", "Greenland", "Confederate States of America",
                      "Thirteen Colonies", "Province of Canada", "Kingdom of Hawaii", "Hawaiian Kingdom"],
}.items():
    for _n in _names:
        REGION_BY_LABEL[_n] = _reg
REGION_BY_LABEL["Kingdom of Hawaii"] = REGION_BY_LABEL["Hawaiian Kingdom"] = "Oceania"
CONTINENT_REGION = {"Q15": "Africa", "Q18": "South America", "Q49": "North America", "Q55643": "Oceania",
                    "Q538": "Oceania", "Q3960": "Oceania", "Q48": "Asia (other)", "Q51": "Antarctica"}
NON_EU_CONTINENTS = set(CONTINENT_REGION)

# Non-European demonyms / peoples (folded) -> region; used only for items without a country.
WORLD_DEMONYMS = {}
for _reg, _words in {
    "South Asia": "indian bengali bangladeshi pakistani sri lankan sinhalese tamil nepali nepalese newar gujarati "
                  "rajasthani punjabi kashmiri odia oriya bihari maithili marathi telugu kannada malayali sindhi "
                  "warli gond santal bhil toda naga mughal",
    "East Asia": "chinese japanese korean mongolian taiwanese okinawan ryukyuan ainu manchu miao hmong tujia "
                 "uyghur zhuang",
    "Southeast Asia": "indonesian javanese balinese sundanese malay malaysian filipino philippine thai siamese "
                      "vietnamese cambodian khmer lao laotian burmese myanmar dayak iban batak toraja sumbanese "
                      "timorese",
    "MENA / Central Asia": "turkish ottoman anatolian persian iranian arab arabic egyptian moroccan berber amazigh "
                           "tunisian algerian palestinian syrian lebanese iraqi kurdish yemeni omani bedouin "
                           "uzbek kazakh kyrgyz turkmen tajik afghan pashtun",
    "Africa": "african nigerian yoruba igbo hausa ghanaian asante ashanti akan ewe malian bambara dogon senegalese "
              "wolof congolese zulu xhosa ndebele sotho maasai masai kenyan tanzanian ethiopian ugandan "
              "malagasy cameroonian beninese tuareg fulani swahili",
    "Mexico / Central America & Caribbean": "mexican guatemalan maya mayan panamanian kuna guna haitian cuban "
                                            "puerto rican oaxacan zapotec mixtec huichol otomi nahua aztec",
    "South America": "peruvian bolivian chilean argentine argentinian brazilian colombian ecuadorian venezuelan "
                     "paraguayan uruguayan andean quechua aymara mapuche shipibo wayuu inca",
    "North America": "american canadian native american navajo hopi pueblo zuni cherokee lakota sioux inuit "
                     "eskimo haida tlingit iroquois ojibwe apache cheyenne seminole metis",
    "Oceania": "australian aboriginal maori polynesian melanesian micronesian hawaiian samoan tongan fijian "
               "tahitian papuan torres strait solomon vanuatu",
}.items():
    for _w in _words.split():
        WORLD_DEMONYMS[_w] = _reg
WORLD_DEMONYMS.update({"sri lankan": "South Asia", "native american": "North America", "torres strait": "Oceania",
                       "puerto rican": "Mexico / Central America & Caribbean"})
for _w in ("sri", "lankan", "rican", "puerto", "native", "strait", "torres"):
    WORLD_DEMONYMS.pop(_w, None)
DEMONYM_RE = re.compile(r"\b(" + "|".join(sorted((re.escape(k) for k in WORLD_DEMONYMS), key=len, reverse=True)) + r")\b")


# ------------------------------------------------------------------ curated traditions
# (label, aliases, country, people, region, medium, strong regex, weak regex, context regex, cell)
# Regexes run on ASCII-folded lowercased text (build_traditions.fold: diacritics and
# punctuation other than ", -" removed, so "Diné" -> "dine", "t'nalak" -> "t nalak").
# strong: matches alone. weak: counts only when ctx also matches. cell: the culture
# token when the entry is in essence a people x medium cell (for the alias check).
SA, EA, SEA, MENA, AF = "South Asia", "East Asia", "Southeast Asia", "MENA / Central Asia", "Africa"
MCA, SAM, NAM, OC = "Mexico / Central America & Caribbean", "South America", "North America", "Oceania"
T = [
    # ---------------------------------------------------------------- South Asia
    ("Madhubani painting", "Mithila painting", "India; Nepal", "Maithil", SA, "painting",
     r"madhubani|mithila", "", "", ""),
    ("Warli painting", "", "India", "Warli", SA, "painting", r"\bwarli\b", "", "", ""),
    ("Gond painting", "Pardhan Gond art", "India", "Gond", SA, "painting",
     r"\bgond (art|paint)|pardhan gond|jangarh", r"\bgond\b", r"paint|canvas|print|acrylic|ink", "gond"),
    ("Kalighat painting", "Kalighat pat", "India", "", SA, "painting", r"kalighat|kalighaat", "", "", ""),
    ("Patua scroll painting (Bengal pat)", "patachitra of Bengal; jadu patua; Santal scroll", "India; Bangladesh", "Patua",
     SA, "painting (scroll)", r"jadu ?patua|santal scroll|bengal(i)? (scroll|pat\b)|patua (scroll|painting|art)", r"\bpatuas?\b|scroll|\bpat\b", r"bengal|midnapore|medinipur|birbhum|santal|naya village", ""),
    ("Tanjore painting", "Thanjavur painting", "India", "", SA, "painting",
     r"tanjore (paint|picture|style)|thanjavur (paint|style)", r"tanjore|thanjavur", r"gesso|gilt|gold leaf|inlaid (stones|glass)|glass beads|reverse glass", ""),
    ("Mysore painting", "", "India", "", SA, "painting", r"mysore (paint|style|school)", "", "", ""),
    ("Kalamkari", "qalamkari; Machilipatnam kalamkari; Srikalahasti kalamkari", "India", "", SA, "textile (painted / printed)",
     r"kalamkari|qalamkari", r"kalamkar", r"india|andhra|machilipatnam|masulipatam|srikalahasti|coromandel|golconda", ""),
    ("Pattachitra", "Patachitra; Odisha pata; Raghurajpur", "India", "", SA, "painting",
     r"pattachitra|patachitra|patta ?chitra|pata ?chitra|raghurajpur|(orissa|odisha)n? (pata|patta|scroll|painting)", "", "", ""),
    ("Phad painting", "par; Pabuji ki phad", "India", "", SA, "painting (scroll)", r"\bphad\b|pabuji|devnarayan", "", "", ""),
    ("Pichwai", "pichhwai; pichhavai", "India", "", SA, "painting (temple hanging)",
     r"pichwai|pichhwai|pichhavai|picchvai|pichvai|pichhvai|pichavai", "", "", ""),
    ("Kantha", "nakshi kantha", "Bangladesh; India", "Bengali", SA, "embroidery", r"\bkantha", "", "", ""),
    ("Phulkari", "bagh", "India; Pakistan", "Punjabi", SA, "embroidery", r"phulkari|\bbagh (phulkari|shawl|embroid)", "", "", ""),
    ("Bandhani", "bandhej; bandhana", "India; Pakistan", "", SA, "textile (tie-dye)",
     r"bandhani|bandhej|bandhana|bandhni|bandani|chunadi|chundri", r"tie.?dye|tied and dyed|tie and dye", r"gujarat|rajasthan|kutch|kachchh|jaipur|jamnagar", ""),
    ("Leheriya", "lahariya", "India", "", SA, "textile (tie-dye)", r"leheriya|lahariya|laharia", "", "", ""),
    ("Ajrakh", "ajrak", "India; Pakistan", "Sindhi", SA, "textile (block-printed)", r"ajrakh?\b", "", "", ""),
    ("Patola", "patolu; Patan patola", "India", "", SA, "textile (double ikat)", r"patola|patolu", "", "", ""),
    ("Bidriware", "bidri", "India", "", SA, "metalwork (inlay)", r"\bbidri|bidriware", r"\bbidar\b", r"metal|inlay|hookah|huqqa|box|ewer|basin|zinc|silver", ""),
    ("Dhokra", "dokra; Bastar bronze", "India", "", SA, "metal casting", r"\bdhokra|\bdokra|\bdhokar\b|\bdhokhra|bastar (bronze|brass|metal|cast)", "", "", ""),
    ("Channapatna toys", "", "India", "", SA, "toys (lacquered wood)", r"channapatna", "", "", ""),
    ("Kondapalli toys", "", "India", "", SA, "toys (wood)", r"kondapalli", "", "", ""),
    ("Etikoppaka toys", "", "India", "", SA, "toys (lacquered wood)", r"etikoppaka", "", "", ""),
    ("Nirmal painting and toys", "", "India", "", SA, "painting / toys", r"\bnirmal (paint|toy|lacquer|craft)", "", "", ""),
    ("Blue Pottery of Jaipur", "Jaipur blue pottery", "India", "", SA, "ceramics",
     r"jaipur blue|blue pottery of jaipur", r"blue pottery|blue glazed|blue and white (pottery|ware|tile|jar|vase)", r"jaipur|rajasthan", ""),
    ("Sanjhi", "sanjhi paper stencil", "India", "", SA, "paper-cut", r"\bsanjhi|\bsanji (stencil|paper)", "", "", ""),
    ("Rogan art", "roghan", "India", "", SA, "textile (painted)", r"\brogan (art|paint)|\broghan", r"\brogan\b", r"kutch|nirona|\bindia\b", ""),
    ("Cheriyal scroll painting", "", "India", "", SA, "painting (scroll)", r"cheriyal|cherial", "", "", ""),
    ("Kavad", "kaavad", "India", "", SA, "painted wooden shrine", r"\bkaa?vad\b|\bkawad\b", "", "", ""),
    ("Chikankari", "chikan work", "India", "", SA, "embroidery", r"chikankari|chikan (work|embroid)", "", "", ""),
    ("Kashmir shawl", "kani shawl; sozni; pashmina; amlikar", "India; Pakistan", "Kashmiri", SA, "textile (shawl)",
     r"kani shawl|sozni|amlikar|kashmir(i)? shawl|shawl,? kashmir", r"shawl|pashmina|shatoosh", r"kashmir|srinagar", ""),
    ("Kutch embroidery (Rabari, Ahir, Banni)", "Kachchh embroidery; Rabari embroidery", "India", "Rabari; Ahir; Jat", SA, "embroidery",
     r"rabari|banni embroid|ahir embroid|kutch(i)? embroid|kachchh(i)? embroid",
     r"embroid|borduur|mirror|bodice|choli|kanjari|torans?\b|quilt", r"\bkutch\b|kachchh|saurashtra|kathiawar|sindh", "rabari"),
    ("Toda embroidery (pukhoor)", "puthukuli", "India", "Toda", SA, "embroidery", r"puthukuli|pukhoor",
     r"embroid|shawl|cloak", r"\btoda\b", "toda"),
    ("Banjara (Lambani) embroidery", "Lambadi", "India", "Banjara", SA, "embroidery", r"banjara|lambani|lambadi", "", "", "banjara"),
    ("Sujani", "sujni", "India", "", SA, "embroidery (quilting)", r"sujani|sujni", "", "", ""),
    ("Paithani", "", "India", "", SA, "textile (woven sari)", r"paithani", "", "", ""),
    ("Banarasi brocade (kinkhab)", "kincob; Benares brocade", "India", "", SA, "textile (brocade)",
     r"kinkhab|kincob|banarasi", r"banaras|benares|varanasi", r"brocade|\bsari\b|kinkhab|zari|gold thread|metal.?wrapped", ""),
    ("Kanchipuram silk", "Kanjeevaram", "India", "", SA, "textile (woven sari)", r"kanjeevaram|kanjivaram|conjeeveram",
     r"kanchipuram", r"silk|sari|textile", ""),
    ("Jamdani", "Dhaka muslin", "Bangladesh; India", "", SA, "textile (woven)", r"jamdani|dacca muslin|dhaka muslin", "", "", ""),
    ("Mata ni pachedi", "", "India", "", SA, "textile (painted)", r"mata ?ni ?pachedi|pachedi", "", "", ""),
    ("Sohrai and Khovar painting", "", "India", "", SA, "painting (mural)", r"sohrai|khovar", "", "", ""),
    ("Saura painting (idital)", "ittal", "India", "Saora", SA, "painting (mural)", r"\bsaura (paint|art|ital)|idital|\bittal", "", "", ""),
    ("Pithora painting", "", "India", "Rathwa; Bhil", SA, "painting (mural)", r"pithora", "", "", ""),
    ("Bhil painting", "", "India", "Bhil", SA, "painting", r"\bbhil (art|paint)", r"paint|canvas|acrylic", r"\bbhil\b", "bhil"),
    ("Molela terracotta plaques", "", "India", "", SA, "ceramics (terracotta)", r"molela", "", "", ""),
    ("Bankura horse", "", "India", "", SA, "ceramics (terracotta)", r"bankura horse|panchmura", r"horse|terracotta|animal figure", r"bankura", ""),
    ("Shadow puppetry of South India (tholu bommalata, togalu gombeyata)", "leather puppets", "India", "", SA, "puppets",
     r"tholu|tolu bommal|togalu|tholpavakoothu|tholpava", r"shadow puppet|leather puppet|puppet",
     r"andhra|karnataka|kerala|telugu|tamil|south indian|\bindia\b", ""),
    ("Kerala mural painting", "", "India", "", SA, "painting (mural)", r"kerala mural", "", "", ""),
    ("Kalamezhuthu and kolam floor drawing", "rangoli; kolam", "India", "", SA, "floor painting", r"kalamezhuthu|rangoli|\bkolam\b(?![ -]mask)", "", "", ""),
    ("Truck art (Pakistan)", "jingle truck", "Pakistan", "", SA, "painting (vehicle)", r"truck art|jingle truck", "", "", ""),
    ("Multani blue pottery and tiles", "kashi kari", "Pakistan", "", SA, "ceramics", r"kashi ?kari",
     r"pottery|tile|ceramic|glaze|earthenware|vase|bowl", r"\bmultan|\bhala\b|sindh", ""),
    ("Ralli quilts", "rilli; rilly", "Pakistan; India", "Sindhi", SA, "textile (quilting)", r"ralli quilt|rilli quilt", r"\bralli|\brilli|\brilly", r"quilt|sindh|pakistan|kutch|\bindia\b", ""),
    ("Ambalangoda masks", "kolam masks; sanni masks; raksha masks", "Sri Lanka", "Sinhalese", SA, "masks",
     r"ambalangoda|sanni (yakuma|mask)|raksha mask|kolam[ -]mask", r"\bmasks?\b|masker", r"sri lanka|ceylon|sinhal", "sinhalese"),
    ("Dumbara weaving", "", "Sri Lanka", "", SA, "weaving", r"\bdumbara", "", "", ""),
    ("Mithila-Janakpur ceramics and painting (Nepal)", "Janakpur art", "Nepal", "Maithil", SA, "painting / ceramics", r"janakpur", "", "", ""),
    # ---------------------------------------------------------------- East Asia
    ("Chinese New Year prints (nianhua)", "nianhua; Yangliuqing; Taohuawu; Yangjiabu; Zhuxianzhen; Wuqiang; Mianzhu",
     "China", "Han", EA, "popular prints",
     r"nianhua|nian hua|yangliuqing|taohuawu|yangjiabu|zhuxianzhen|wuqiang|mianzhu|(chinese )?new year (print|picture)", "", "", ""),
    ("Chinese paper-cutting (jianzhi)", "jianzhi", "China", "Han", EA, "paper-cut", r"jianzhi|jian zhi",
     r"paper.?cut|cut paper|papercut", r"\bchin(a|ese)\b|shaanxi|hebei|yuxian", ""),
    ("Chinese shadow puppets (piyingxi)", "piyingxi", "China", "", EA, "puppets", r"piying",
     r"shadow (puppet|figure|play|theat)", r"\bchin(a|ese)\b|shaanxi|beijing|luanzhou|sichuan|hebei", ""),
    ("Chinese clay figurines (Huishan, Clay Figure Zhang)", "Niren Zhang", "China", "", EA, "ceramics (figurines)",
     r"\bhuishan|niren ?zhang|clay figure zhang", "", "", ""),
    ("Suzhou embroidery (Su xiu)", "su xiu", "China", "", EA, "embroidery", r"\bsu ?xiu\b|suzhou embroid", "", "", ""),
    ("Hunan embroidery (Xiang xiu)", "xiang xiu", "China", "", EA, "embroidery", r"xiang ?xiu|hunan embroid", "", "", ""),
    ("Sichuan embroidery (Shu xiu)", "shu xiu", "China", "", EA, "embroidery", r"\bshu ?xiu|sichuan embroid", "", "", ""),
    ("Cantonese embroidery (Yue xiu / Guangxiu)", "guangxiu; yue xiu", "China", "", EA, "embroidery",
     r"guang ?xiu|yue ?xiu|canton(ese)? embroid", "", "", ""),
    ("Miao embroidery and textiles", "Hmong of China", "China", "Miao", EA, "embroidery / textiles",
     r"miao embroid", r"embroid|textile|skirt|jacket|baby carrier|collar|batik|apron|sleeve|costume|cloth|brocade",
     r"\bmiao\b", "miao"),
    ("Miao silverwork", "", "China", "Miao", EA, "metalwork (silver)", r"miao silver",
     r"silver|necklace|headdress|torque|neck ?ring|jewel", r"\bmiao\b", "miao"),
    ("Bai tie-dye (zharan)", "zharan; Dali tie-dye", "China", "Bai", EA, "textile (tie-dye)", r"zharan|bai tie.?dye",
     r"tie.?dye|tie and dye", r"\bbai\b|\bdali\b|yunnan", "bai"),
    ("Dong (Kam) textiles", "", "China", "Dong", EA, "textiles", r"dong (brocade|textile|minority)",
     r"textile|brocade|baby carrier|jacket|embroid", r"\bkam\b people|\bdong (people|minority|nationality)", "dong"),
    ("Zhuang brocade (zhuangjin)", "zhuangjin", "China", "Zhuang", EA, "textile (brocade)", r"zhuangjin|zhuang brocade",
     r"brocade|textile|baby carrier", r"\bzhuang\b", "zhuang"),
    ("Li textiles (Hainan)", "Li brocade", "China", "Li", EA, "textiles", r"\bli brocade|hainan (li|brocade|textile)", "", "", "li"),
    ("Yi (Nuosu) lacquerware", "Nuosu lacquer", "China", "Yi", EA, "lacquer", r"nuosu",
     r"lacquer|textile|cape|embroid", r"\byi (people|minority|nationality)|liangshan", "yi"),
    ("Naxi Dongba painting", "Dongba", "China", "Naxi", EA, "painting / manuscripts", r"dongba", r"paint|manuscript|scroll", r"naxi|nakhi", "naxi"),
    ("Korean minhwa (folk painting)", "minhwa; chaekgeori; munjado", "South Korea; North Korea", "Korean", EA, "painting",
     r"minhwa|chaekgeori|chaekkori|munjado|korean folk paint", "", "", ""),
    ("Korean bojagi", "pojagi; jogakbo", "South Korea", "Korean", EA, "textile (patchwork)", r"bojagi|pojagi|jogakbo|chogakpo", "", "", ""),
    ("Korean najeon (mother-of-pearl lacquer)", "najeonchilgi", "South Korea", "Korean", EA, "lacquer (inlay)",
     r"najeon|najon", r"mother.of.pearl|lacquer", r"korea|joseon|goryeo|choson|koryo", ""),
    ("Korean hwagak (painted ox horn)", "", "South Korea", "Korean", EA, "painted horn", r"hwagak", "", "", ""),
    ("Hahoe masks (Korean talchum masks)", "hahoetal", "South Korea", "Korean", EA, "masks", r"hahoe|talchum", r"\btal\b|\bmasks?\b|masker",
     r"korea", "korean"),
    ("Korean onggi", "", "South Korea", "Korean", EA, "ceramics", r"\bonggi\b", "", "", ""),
    ("Japanese mingei", "folk craft movement", "Japan", "", EA, "crafts (movement)", r"mingei",
     r"folk.?craft", r"japan", ""),
    ("Otsu-e", "Otsu painting", "Japan", "", EA, "painting", r"otsu-?e\b|otsu (e|painting)\b|otsu-e", "", "", ""),
    ("Kokeshi", "", "Japan", "", EA, "toys (wooden dolls)", r"kokeshi", "", "", ""),
    ("Japanese folk toys (kyodo gangu, hariko, Fushimi dolls)", "kyodo gangu; inu-hariko; Fushimi ningyo",
     "Japan", "", EA, "toys", r"kyodo gangu|kyodo-gangu|hariko|fushimi (doll|ningyo)|daruma|tsutsumi (doll|ningyo)|"
     r"sagara (doll|ningyo)|hakata (doll|ningyo)", "", "", ""),
    ("Ema (votive plaques)", "", "Japan", "", EA, "painting (votive)", r"\bema\b(?=.*(votive|plaque|shrine|horse|tablet))|\bema-",
     "", "", ""),
    ("Bingata", "Ryukyuan stencil dyeing", "Japan", "Ryukyuan", EA, "textile (stencil-dyed)", r"bingata", "", "", ""),
    ("Bashofu (Ryukyuan banana-fibre cloth)", "basho-fu", "Japan", "Ryukyuan", EA, "textile", r"basho ?-?fu", "", "", ""),
    ("Kasuri (Japanese ikat)", "kasuri", "Japan", "", EA, "textile (ikat)", r"kasuri|e-gasuri|egasuri", "", "", ""),
    ("Tsutsugaki", "", "Japan", "", EA, "textile (paste-resist)", r"tsutsugaki", "", "", ""),
    ("Sashiko, kogin and boro", "kogin-zashi; boro", "Japan", "", EA, "textile (stitched)", r"sashiko|kogin|hishizashi",
     r"\bboro\b", r"japan|aomori|textile|indigo|cotton", ""),
    ("Katagami (paper stencils)", "", "Japan", "", EA, "stencil", r"katagami|ise-katagami|ise katagami", "", "", ""),
    ("Ainu textiles and carving", "attus; ruunpe; ikupasuy; chikarkarpe", "Japan", "Ainu", EA, "textiles / woodcarving",
     r"attush?|ruunpe|ikupasuy|ikupasui|chikarkarpe|kaparamip|\bainu\b", "", "", "ainu"),
    ("Mongolian felt, leather and appliqué crafts", "", "Mongolia", "Mongol", EA, "felt / leather",
     r"mongol(ian)? (felt|applique|saddle|boot)", r"\bfelt\b|\bdeel\b|saddle|\bboots?\b",
     r"mongol", "mongolian"),
    ("Taiwanese Indigenous carving and weaving (Paiwan, Atayal, Rukai, Tao)", "", "Taiwan", "Paiwan; Atayal; Rukai; Tao",
     EA, "woodcarving / weaving", r"paiwan|atayal|\brukai|bunun|\byami\b|saisiyat|truku|taroko",
     "", "", "paiwan"),
    # ---------------------------------------------------------------- Southeast Asia
    ("Javanese batik (Indonesian batik)", "batik tulis; batik cap; batik pesisir", "Indonesia", "Javanese", SEA, "textile (wax-resist)",
     r"batik tulis|batik cap|batik pesisir|batik belanda|batik (pekalongan|lasem|cirebon|solo|yogya|jogja|madura)",
     r"batik", r"indonesia|\bjava|javanese|jogja|yogya|surakarta|\bsolo\b|pekalongan|cirebon|lasem|madura|sumatra|jambi|"
     r"\bbali|east indies|nederlands-indie|indies|sunda|garut|indramayu", ""),
    ("Malaysian batik", "", "Malaysia", "Malay", SEA, "textile (wax-resist)", r"batik malaysia", r"batik",
     r"malay|kelantan|terengganu|penang", ""),
    ("Indonesian ikat (tenun ikat)", "tenun; hinggi; kain kebat", "Indonesia", "", SEA, "textile (ikat)",
     r"tenun ikat|hinggi|hi(n)?gi kombu|kain kebat|lau pahudu|tais\b",
     r"\bikat|tenun|kain kebat|ikatten|geikat",
     r"sumba|flores|\btimor|savu|sawu|toraja|lembata|tanimbar|roti\b|\brote\b|alor|sikka|ende|lio\b|"
     r"indonesia|kalimantan|borneo|dayak|sulawesi|lesser sunda", ""),
    ("Iban pua kumbu", "pua", "Malaysia; Indonesia", "Iban", SEA, "textile (ikat)", r"pua kumbu|pua kombu",
     r"\bpua\b|ikat|textile|blanket", r"\biban\b|sarawak", "iban"),
    ("Songket", "kain songket", "Indonesia; Malaysia; Brunei", "Malay; Minangkabau", SEA, "textile (brocade)",
     r"songket|sungkit|kain songket", "", "", ""),
    ("Ulos (Batak textiles)", "ulos ragidup", "Indonesia", "Batak", SEA, "textile", r"\bulos\b", "", "", "batak"),
    ("Lampung ship cloths (tapis, tampan, palepai)", "tapis", "Indonesia", "Lampung", SEA, "textile",
     r"palepai|ship cloth|scheepjesdoek", r"\btapis\b|\btampan\b", r"lampung|sumatra", ""),
    ("Geringsing (Tenganan double ikat)", "gringsing", "Indonesia", "Balinese", SEA, "textile (double ikat)",
     r"g(e)?ringsing", "", "", ""),
    ("Wayang (shadow and rod puppets)", "wayang kulit; wayang golek; wayang klitik", "Indonesia; Malaysia", "Javanese; Balinese",
     SEA, "puppets", r"wayang", "", "", ""),
    ("Kamasan painting", "wayang style painting", "Indonesia", "Balinese", SEA, "painting", r"kamasan", "", "", ""),
    ("Balinese woodcarving and painting (Ubud, Batuan, Mas)", "Pita Maha", "Indonesia", "Balinese", SEA, "painting / woodcarving",
     r"pita maha|batuan|\bubud\b", r"painting|carving|snijwerk|schildering", r"balinese|klungkung|gianyar|bali, indonesia|indonesia.*\bbali\b|\bbali\b.*indonesia", "balinese"),
    ("Toraja carving (tau tau, pa'ssura)", "tau-tau", "Indonesia", "Toraja", SEA, "woodcarving", r"tau ?-?tau|passura",
     r"carv|figure|panel|snijwerk", r"toraja", "toraja"),
    ("Batak carving and magic books (pustaha)", "pustaha; tunggal panaluan", "Indonesia", "Batak", SEA, "woodcarving / books",
     r"pustaha|tunggal panaluan|sigale gale", r"carv|staff|figure|book|container|horn", r"\bbatak", "batak"),
    ("Dayak carving and beadwork", "hampatong", "Indonesia; Malaysia", "Dayak; Kenyah; Kayan", SEA, "woodcarving / beadwork",
     r"hampatong|hudoq|kelirieng", r"carv|bead|baby carrier|shield|hat|mask|figure|sword|mandau",
     r"dayak|kenyah|kayan|ngaju|kalimantan|borneo|sarawak", "dayak"),
    ("Dong Ho woodblock prints", "tranh Dong Ho", "Vietnam", "", SEA, "popular prints", r"\bdong ho (print|woodblock|painting|picture|village)|tranh dong ho", r"\bdong ho\b", r"vietnam|woodblock|print|folk", ""),
    ("Hang Trong woodblock prints", "", "Vietnam", "", SEA, "popular prints", r"hang trong", "", "", ""),
    ("Vietnamese lacquer painting (son mai)", "son mai", "Vietnam", "", SEA, "lacquer painting", r"\bson mai\b", "", "", ""),
    ("Bat Trang ceramics", "", "Vietnam", "", SEA, "ceramics", r"bat trang", "", "", ""),
    ("T'nalak (T'boli abaca ikat)", "tinalak", "Philippines", "T'boli", SEA, "textile (ikat)", r"\bt ?nalak|\btinalak|\bt ?boli\b",
     "", "", "tboli"),
    ("Philippine pina and other weaving (Yakan, Kalinga, Ifugao, inabel)", "pina cloth; inabel; Yakan weaving",
     "Philippines", "", SEA, "textile", r"\bpina (cloth|fiber|fibre|textile|handkerchief|embroid)|\bnipis\b|inabel|\byakan\b|"
     r"abel iloko", r"textile|weav|blanket|skirt|loincloth|ikat",
     r"kalinga|ifugao|bontoc|tinguian|itneg|bagobo|mandaya|b laan|blaan|maranao|tausug|philippin", ""),
    ("Ifugao bulul (granary figures)", "bulol", "Philippines", "Ifugao", SEA, "woodcarving", r"bulul|bulol", "", "", "ifugao"),
    ("Maranao okir and sarimanok", "okkil", "Philippines", "Maranao", SEA, "woodcarving / metalwork", r"\bokir\b|okkil|sarimanok",
     "", "", "maranao"),
    ("Burmese lacquer (yun)", "yun lacquerware", "Myanmar", "Burmese", SEA, "lacquer", r"\byun\b ?lacquer|thayo",
     r"lacquer", r"burm|myanmar|bagan|\bpagan\b|mandalay|shan state", "burmese"),
    ("Burmese kalaga (sequined tapestries)", "shwe chi doe", "Myanmar", "Burmese", SEA, "textile (embroidered)", r"kalaga|shwe ?chi",
     "", "", ""),
    ("Bencharong porcelain", "benjarong", "Thailand", "Thai", SEA, "ceramics", r"bencharong|benjarong|lai nam thong", "", "", ""),
    ("Cambodian ikat (hol)", "sampot hol", "Cambodia", "Khmer", SEA, "textile (ikat)", r"sampot hol|hol (lboeuk|kben|pidan)|pidan",
     r"ikat|\bhol\b|sampot", r"cambod|khmer|kampuchea", "khmer"),
    ("Lao weaving (sinh, pha biang)", "pha sin; Tai Lue; Tai Dam", "Laos", "Lao; Tai", SEA, "textile",
     r"pha biang|pha sin|\bsinh\b|tai lue|tai dam|tai daeng|black tai|tai lu\b",
     r"textile|weav|skirt|shawl|blanket|shaman cloth|ikat", r"\blao\b|\blaos\b|laotian|sam neua|houaphan", "lao"),
    ("Hmong paj ntaub and story cloths", "paj ntaub; story cloth", "Laos; Vietnam; Thailand; United States", "Hmong", SEA,
     "textile (appliqué / embroidery)", r"paj ntaub|pa ndau|story ?cloth",
     r"embroid|textile|applique|batik|baby carrier|collar|skirt|jacket|costume", r"\bhmong", "hmong"),
    ("Thai shadow puppets (nang yai, nang talung)", "", "Thailand", "Thai", SEA, "puppets", r"nang (yai|talung)", "", "", ""),
    # ---------------------------------------------------------------- MENA / Central Asia
    ("Anatolian kilim", "kelim; cicim; zili; Turkish flatweave", "Turkey", "Turkish; Yoruk; Kurdish", MENA, "carpets (flatweave)",
     r"cicim|\bzili\b|anatolian kilim", r"kilim|kelim|flat.?weave|sumak|soumak|slit.?tapestry",
     r"\bturk(ey|ish)?\b|anatol|konya|cappadoc|yoruk|yuruk|aydin|kars|sivas|malatya|obruk|aksaray|ottoman", ""),
    ("Persian tribal kilims (gelim) and gabbeh", "gelim; gabbeh", "Iran", "Qashqai; Luri; Bakhtiari; Shahsavan", MENA,
     "carpets (flatweave / pile)", r"gabbeh|gabeh|\bgelim|shahsavan|mafrash",
     r"kilim|kelim|flat.?weave|sumak|soumak|saddle ?bag|bag face|mafrash|tribal (rug|carpet|bag)",
     r"persia|iran|qashqa|kashkai|qashqai|bakhtiar|\bluri|\blori\b|khamseh|afshar|senneh|bijar|kurd", "qashqai"),
    ("Turkmen tribal rugs and trappings", "Tekke; Yomut; Ersari; Salor; Saryk; Chodor; engsi; chuval; asmalyk",
     "Turkmenistan; Afghanistan; Iran", "Turkmen", MENA, "carpets",
     r"\byomut|\byomud|\bersari|\bsaryk|\bengsi|asmalyk|turkmen (rug|carpet)",
     r"rug|carpet|tapijt|bag|trapping|tent band|tekke|salor|chodor|chuval|torba", r"turkmen|turkoman|turcoman", "turkmen"),
    ("Baluch rugs", "Baloch rugs", "Iran; Afghanistan; Pakistan", "Baluch", MENA, "carpets", r"balu?ch (rug|carpet|bag|prayer)",
     r"rug|carpet|tapijt|bag|weav|textile|embroid", r"\bbaluch(i|is)?\b|\bbaloch(i)?\b|\bbeluch|\bbelouch", "baluch"),
    ("Suzani", "susani", "Uzbekistan; Tajikistan", "Uzbek; Tajik", MENA, "embroidery", r"\bsuzani|\bsusani|\bsuzane\b|\bpalak\b|bolinpush",
     "", "", ""),
    ("Central Asian ikat (abrbandi)", "abr; adras; atlas", "Uzbekistan", "Uzbek; Tajik", MENA, "textile (ikat)",
     r"abrbandi|\badras\b|\batlas\b(?=.*silk)", r"\bikat|chapan|khalat",
     r"uzbek|bukhara|samarkand|fergana|ferghana|tashkent|central asia|turkestan|khiva|tajik|kokand|margilan", ""),
    ("Kyrgyz and Kazakh felt (shyrdak, ala-kiyiz, tus kiiz)", "shyrdak; ala-kiyiz; tus kiiz", "Kyrgyzstan; Kazakhstan",
     "Kyrgyz; Kazakh", MENA, "felt / embroidery", r"shyrdak|shirdak|ala ?-?kiyiz|ala ?-?kiiz|tus ?-?kiiz|tush ?-?kiyiz|tuskiiz",
     r"felt|embroid|hanging|yurt|tent band", r"kyrgyz|kirghiz|kazakh", "kyrgyz"),
    ("Uzbek ceramics (Rishtan, Gijduvan)", "Rishton", "Uzbekistan", "Uzbek", MENA, "ceramics", r"rishtan|rishton|gijduvan|gizhduvan",
     "", "", ""),
    ("Zellige", "zellij; zillij", "Morocco", "", MENA, "ceramics (tile mosaic)", r"\bzellige|\bzellij|\bzillij|\bzelij\b", "", "", ""),
    ("Amazigh (Berber) rugs and weaving", "Beni Ourain; Azilal; boucherouite; handira; hanbel", "Morocco; Algeria; Tunisia",
     "Amazigh", MENA, "carpets / weaving", r"beni ou?rain|beni mguild|azilal|boucherouite|handira|hanbel|zemmour|glaoua|"
     r"ait (ouaouzguite|bou|ouaou)", r"\brugs?\b(?! van)|carpet|tapijt|kilim|blanket|textile|weav|shawl|cloak|haik",
     r"berber|amazigh|imazighen|middle atlas|high atlas|kabyl|chaoui|chaouia|siroua|aurès|aures", "berber"),
    ("Amazigh (Berber) silver jewellery and enamel", "tabzimt; tizerzai; Kabyle enamel", "Morocco; Algeria", "Amazigh", MENA,
     "jewellery", r"tabzimt|tizerzai|tizerzay|beni yenni|tiznit",
     r"jewel|fibula|brooch|necklace|silver|enamel|bracelet|anklet|pendant|headdress|earring",
     r"berber|amazigh|kabyl|chaoui|anti-atlas", "berber"),
    ("Kabyle pottery", "", "Algeria", "Kabyle", MENA, "ceramics", r"kabyle pottery",
     r"pot|jar|vessel|ceramic|earthenware|lamp|bowl|dish", r"kabyl", "kabyle"),
    ("Sejnane pottery", "", "Tunisia", "", MENA, "ceramics", r"sejnane", "", "", ""),
    ("Moroccan pottery (Fez, Safi, Tamegroute)", "Fez blue pottery", "Morocco", "", MENA, "ceramics",
     r"tamegroute|tamgrout|(fez|fes|safi|meknes|sale) (pottery|ware|ceramic|bowl|dish|plate|jar|vase|tile|faience)",
     r"pottery|ceramic|earthenware|faience|aardewerk", r"morocc|\bfez\b|\bfes\b|\bsafi\b|meknes", ""),
    ("Palestinian embroidery (tatreez)", "tatriz", "Palestine; Jordan; Israel", "Palestinian", MENA, "embroidery",
     r"tatreez|tatriz|ramallah dress|bethlehem (dress|embroid|couching)",
     r"embroid|dress|thob|thawb|jillayeh|headdress|cushion|textile|chest panel|qabbeh", r"palestin|bethlehem|ramallah|hebron|gaza|jaffa", "palestinian"),
    ("Al Sadu (Bedouin weaving)", "sadu", "Kuwait; Saudi Arabia; UAE; Qatar", "Bedouin", MENA, "weaving",
     r"\bal ?sadu\b|\bsadu (weav|textile|house)", r"weav|textile|tent|rug|saddle bag|camel", r"bedouin|bedu\b", "bedouin"),
    ("Bedouin silver jewellery (Yemen, Oman, Arabia)", "", "Yemen; Oman; Saudi Arabia", "Bedouin", MENA, "jewellery",
     r"bedouin (silver|jewel)", r"silver|jewel|necklace|bracelet|amulet|hirz|khanjar|jambiya|anklet",
     r"bedouin|yemen|\boman\b|hadhram|najd", "bedouin"),
    ("Khamak embroidery (Kandahar)", "khamak; kandahari embroidery", "Afghanistan", "Pashtun", MENA, "embroidery",
     r"khamak|kandahar(i)? embroid", "", "", ""),
    ("Afghan war rugs", "", "Afghanistan", "", MENA, "carpets", r"war rug", "", "", ""),
    ("Khayamiya (Egyptian tentmaker appliqué)", "khayamia; tentmakers of Cairo", "Egypt", "", MENA, "textile (appliqué)",
     r"khayamiya|khayamia|khiyamiya|tentmaker", r"tent (applique|panel|hanging)", r"egypt|cairo", ""),
    ("Egyptian Harrania tapestry (Wissa Wassef)", "Ramses Wissa Wassef", "Egypt", "", MENA, "tapestry", r"harrania|wissa wassef",
     "", "", ""),
    ("Persian qalamkar (Isfahan printed cotton)", "ghalamkar", "Iran", "", MENA, "textile (block-printed)", r"qalamkar\b|ghalamkar",
     r"kalamkar\b", r"iran|persia|isfahan|esfahan", ""),
    ("Termeh", "", "Iran", "", MENA, "textile (woven)", r"termeh", "", "", ""),
    ("Khatam (Persian micro-marquetry)", "khatamkari", "Iran", "", MENA, "woodwork (inlay)", r"khatam(kari)?\b", "", "", ""),
    ("Pateh (Kerman embroidery)", "", "Iran", "", MENA, "embroidery", r"pate-?duzi|patehdouzi|pateh (embroid|douzi|duzi)", r"\bpateh\b", r"kerman|iran|persia", ""),
    ("Turkish oya (needle lace edging)", "igne oyasi", "Turkey", "Turkish", MENA, "lace", r"igne oyasi|oyasi|oya (lace|edging|needle)",
     r"needle ?lace|edging|\blace|\boya\b", r"\bturk(ey|ish|ic)?\b|anatol|ottoman", ""),
    ("Ebru (Turkish paper marbling)", "", "Turkey", "Turkish", MENA, "paper marbling", r"\bebru\b",
     r"marbl(ed|ing) paper|paper marbl", r"\bturk(ey|ish)?\b|ottoman|istanbul", ""),
    ("Karagoz shadow puppets", "Karagiozis", "Turkey; Greece", "", MENA, "puppets", r"karagoz|karagiozis|hacivat", "", "", ""),
    ("Kutahya and Canakkale pottery", "", "Turkey", "", MENA, "ceramics", r"kutahya|canakkale|chanak ?kale", "", "", ""),
    ("Tuareg silver and leatherwork", "Agadez cross; tanaghilt", "Niger; Mali; Algeria; Libya", "Tuareg", AF, "jewellery / leather",
     r"agadez cross|tanaghilt|tenarere|takoba",
     r"silver|jewel|cross|pendant|leather|bag|cushion|saddle|sword|amulet|tent post|bracelet|knife", r"tuareg|touareg|tamashek|tamasheq|agadez", "tuareg"),
    # ---------------------------------------------------------------- Africa
    ("Kente", "nwentoma; Ewe kente", "Ghana; Togo", "Asante; Ewe", AF, "textile (strip-woven)", r"\bkente|nwentoma", "", "", ""),
    ("Adinkra cloth", "", "Ghana", "Asante", AF, "textile (stamped)", r"adinkra", "", "", ""),
    ("Bogolan (mud cloth)", "bogolanfini; mud cloth", "Mali", "Bamana", AF, "textile (mud-dyed)", r"bogolan|mud ?-?cloth|mudcloth",
     "", "", ""),
    ("Adire", "adire eleko; adire oniko", "Nigeria", "Yoruba", AF, "textile (indigo resist)", r"\badire", "", "", ""),
    ("Aso oke", "aso-oke; sanyan; alaari; etu", "Nigeria", "Yoruba", AF, "textile (strip-woven)", r"aso ?-?oke|asooke", "", "", ""),
    ("Akwete cloth", "", "Nigeria", "Igbo", AF, "textile (woven)", r"akwete", "", "", ""),
    ("Hausa embroidered robes (babban riga)", "babban riga", "Nigeria; Niger", "Hausa; Nupe", AF, "embroidery (costume)",
     r"babban ?riga|agbada", r"robe|gown|embroid|riga\b|tunic", r"hausa|nupe|zaria|sokoto", "hausa"),
    ("Kuba raffia cloth (Kasai velvet)", "Kasai velvet; Shoowa; ncak; mapel", "DR Congo", "Kuba", AF, "textile (raffia)",
     r"kasai velvet|shoowa|bushoong|\bncak\b|mapel",
     r"raffia|textile|cloth|skirt|velvet|cut.?pile|embroid|panel|overskirt|wrapper", r"\bkuba\b", "kuba"),
    ("Ndebele beadwork", "ijogolo; mapoto; linaga", "South Africa; Zimbabwe", "Ndebele", AF, "beadwork",
     r"ijogolo|mapoto|\blinaga|isiphephetu", r"bead|apron|blanket|doll|neck ?ring|cape|leggings", r"ndebele", "ndebele"),
    ("Ndebele house painting", "Ndebele mural; Esther Mahlangu", "South Africa", "Ndebele", AF, "painting (mural)",
     r"ndebele (house|mural|wall|paint)|mahlangu", "", "", "ndebele"),
    ("Zulu beadwork", "isigolwane; ucu; love letters", "South Africa", "Zulu", AF, "beadwork",
     r"isigolwane|incwadi|zulu love letter", r"bead|necklace|apron|love letter|collar|belt|headband|ucu\b|isigege|cape",
     r"zulu|kwazulu|natal|nguni|msinga|nongoma", "zulu"),
    ("Zulu ceramics (ukhamba) and wire baskets (imbenge)", "ukhamba; izinkamba; telephone wire baskets", "South Africa", "Zulu",
     AF, "ceramics / basketry", r"ukhamba|izinkamba|imbenge|telephone wire",
     r"pot|jar|vessel|beer|basket|ceramic", r"zulu|kwazulu|nesta nala|magwaza", "zulu"),
    ("Xhosa beadwork", "", "South Africa", "Xhosa", AF, "beadwork", r"xhosa bead",
     r"bead|necklace|collar|apron|pipe bag|bag", r"xhosa|mfengu|thembu|mpondo|pondo", "xhosa"),
    ("Maasai beadwork", "Samburu beadwork", "Kenya; Tanzania", "Maasai; Samburu", AF, "beadwork", r"maasai bead|masai bead",
     r"bead|collar|necklace|earring|ornament|headdress|bracelet|neck ?ring|anklet|belt",
     r"maasai|masai|samburu|turkana|pokot|rendille", "maasai"),
    ("Tingatinga painting", "tinga tinga", "Tanzania", "", AF, "painting", r"tinga ?-?tinga", "", "", ""),
    ("Makonde carving (shetani, ujamaa)", "shetani; ujamaa", "Tanzania; Mozambique", "Makonde", AF, "woodcarving",
     r"shetani|ujamaa", r"carv|sculpture|figure|mask|ebony|wood", r"makonde|mawia", "makonde"),
    ("Shona stone sculpture", "Tengenenge", "Zimbabwe", "Shona", AF, "stone sculpture", r"shona (stone|sculpt)|tengenenge",
     r"stone|serpentine|springstone|verdite|opal stone", r"\bshona\b|zimbabwe", "shona"),
    ("Kamba (Akamba) carving", "", "Kenya", "Kamba", AF, "woodcarving", r"akamba",
     r"carv|figure|sculpture", r"akamba|wakamba|kamba peoples|kamba, kenya|kenya.*\bkamba\b|\bkamba\b.*kenya", "kamba"),
    ("Litema (Sotho mural)", "ditema", "Lesotho; South Africa", "Sotho", AF, "painting (mural)", r"litema|ditema", "", "", "sotho"),
    ("Asafo flags", "frankaa", "Ghana", "Fante", AF, "textile (appliqué)", r"asafo (flag|company|banner)|frankaa", r"\basafo\b", r"ghana|fante|fanti|akan|flag|banner", ""),
    ("Fon appliqué (Abomey hangings)", "Abomey appliqué", "Benin", "Fon", AF, "textile (appliqué)", r"abomey (applique|hanging|tapestr|cloth)",
     r"applique|tapestr|banner|wall hanging", r"\bfon (people|peoples)\b|dahomey|abomey|\bfon\b.*\bbenin\b(?! kingdom)", "fon"),
    ("Ghanaian fantasy coffins (abebuu adekai)", "figurative coffins", "Ghana", "Ga", AF, "sculpture",
     r"fantasy coffin|figurative coffin|abebuu|kane kwei|paa joe", "", "", ""),
    ("Senegalese reverse-glass painting (souwer)", "suwer; sous-verre", "Senegal", "Wolof", AF, "painting (glass)",
     r"souwer|suwer|souwere|sous ?-?verre", r"reverse (glass|painting)|painting on glass|glass painting", r"senegal|dakar|wolof", ""),
    ("Shweshwe", "isishweshwe", "South Africa", "", AF, "textile (printed)", r"shweshwe|isishweshwe", "", "", ""),
    ("Kanga and kitenge", "khanga; leso; chitenge", "Kenya; Tanzania", "Swahili", AF, "textile (printed)",
     r"\bkhanga|kitenge|chitenge|\bleso\b", r"\bkanga\b", r"swahili|kenya|tanzania|zanzibar|dar es salaam|mombasa|east africa", ""),
    ("Ugandan barkcloth (olubugo)", "lubugo; Buganda barkcloth", "Uganda", "Ganda", AF, "barkcloth", r"olubugo|lubugo",
     r"bark ?-?cloth", r"uganda|buganda|ganda\b", "ganda"),
    ("Akan goldweights (abrammuo)", "abrammuo; mrammuo", "Ghana; Côte d'Ivoire", "Akan", AF, "metal casting",
     r"abrammuo|mrammuo|gold ?-?weight", "", "", "akan"),
    ("Yoruba beadwork (ade crowns)", "ade", "Nigeria", "Yoruba", AF, "beadwork", r"beaded crown|\bade\b(?=.*crown)",
     r"bead", r"yoruba|ekiti|efon-alaye|oyo\b", "yoruba"),
    ("Fulani wedding blankets (khasa, arkilla)", "kaasa; arkilla kerka", "Mali; Niger", "Fulani", AF, "textile (woven)",
     r"arkilla|\bkaasa\b", r"\bkhasa\b|\bkerka\b|blanket|wedding", r"fulani|fulbe|peul|\bfula\b", "fulani"),
    ("Korhogo cloth (Senufo painted cloth)", "Senufo mud cloth", "Côte d'Ivoire", "Senufo", AF, "textile (painted)",
     r"korhogo (cloth|textile|painted)", r"painted cloth|mud cloth|painted textile", r"korhogo|senufo|senoufo", "senufo"),
    ("Ndop (Cameroon Grassfields resist-dyed cloth)", "", "Cameroon", "Bamileke; Bamum", AF, "textile (resist-dyed)",
     r"\bndop\b", "", "", ""),
    ("Dida raffia textiles", "", "Côte d'Ivoire", "Dida", AF, "textile (tie-dyed raffia)", r"\bdida\b(?=.*(raffia|textile|skirt|tie))",
     "", "", "dida"),
    ("Kiondo and Botswana (Okavango) baskets", "kyondo; Hambukushu baskets", "Kenya; Botswana", "Kikuyu; Hambukushu", AF,
     "basketry", r"kiondo|kyondo|hambukushu|mbukushu|wayeyi|bayei", r"basket", r"botswana|okavango|ngamiland", ""),
    ("Rwandan agaseke and imigongo", "agaseke; imigongo; peace basket", "Rwanda", "", AF, "basketry / painting",
     r"agaseke|imigongo|peace basket", r"basket", r"rwanda|tutsi", ""),
    ("Mangbetu pottery and figurative arts", "", "DR Congo", "Mangbetu", AF, "ceramics", r"mangbetu pot|mangbetu jar",
     r"pot|jar|vessel|ceramic|terracotta", r"mangbetu", "mangbetu"),
    # ---------------------------------------------------------------- Mexico / Central America & Caribbean
    ("Alebrijes and Oaxacan wood carving", "alebrije; Arrazola; San Martin Tilcajete; tonas y nahuales", "Mexico",
     "Zapotec", MCA, "woodcarving / papier-mache", r"alebrije|arrazola|tilcajete|tonas y nahuales|copal (carv|wood|figure)", "", "", ""),
    ("Mexican cartoneria (Judas figures)", "cartoneria; Judas", "Mexico", "", MCA, "papier-mache",
     r"cartoneria|carton(e|a) mexican", r"papier.?mache|paper mache|carton\b|judas figure|catrina",
     r"(?<!new )mexic|linares|celaya", ""),
    ("Papel picado", "papel cortado; papel de china", "Mexico", "", MCA, "paper-cut", r"papel picado|papel cortado", "", "", ""),
    ("Talavera poblana", "Puebla maiolica", "Mexico", "", MCA, "ceramics (tin-glazed)",
     r"talavera poblana|puebla (tin|majolica|maiolica|faience|earthenware|style)|talavera de puebla|loza poblana",
     r"talavera|tin-?glazed|majolica|maiolica|faience", r"puebla|(?<!new )mexic|new spain|nueva espana", ""),
    ("Amate bark-paper painting", "amatl; papel amate", "Mexico", "Nahua; Otomi", MCA, "painting (bark paper)", r"\bamate\b|\bamatl\b",
     r"bark ?paper", r"(?<!new )mexic|guerrero|otomi|nahua|san pablito|hidalgo|puebla", ""),
    ("Huichol yarn and bead art (nierika)", "nierika; Wixarika art", "Mexico", "Huichol (Wixarika)", MCA, "yarn painting / beadwork",
     r"nierika|yarn painting", r"yarn|bead|kralen|votive bowl|gourd bowl|jicara|beaded", r"huichol|wixarika|wixaritari", "huichol"),
    ("Otomi tenango embroidery", "tenango de Doria", "Mexico", "Otomi", MCA, "embroidery", r"tenango de doria|otomi embroid|tenango (embroid|textile|bordado)",
     r"embroid|borduur", r"otomi|hnahnu|tenango de doria", "otomi"),
    ("Maya huipil and backstrap weaving", "huipil; hipil; guipil; corte; tzute", "Guatemala; Mexico", "Maya", MCA, "textile",
     r"huipil|hipil|guipil|tzute|perraje",
     r"blouse|corte\b|tocoyal|headcloth|head cloth|cofradia|tzut",
     r"guatemal|chiapas|yucatan|quiche|k iche|kiche|cakchiquel|kaqchikel|tzotzil|tzeltal|mam\b|chichicastenango|"
     r"san antonio aguas|solola|todos santos|nebaj|ixil|comalapa|san juan sacatepequez|totonicapan|\bmaya", "maya"),
    ("Mola", "molas; Guna mola", "Panama; Colombia", "Guna (Kuna)", MCA, "textile (reverse appliqué)", r"\bmola\b(?=.*(kuna|cuna|guna|panama|san blas))|\bmolas\b",
     r"\bmola\b|reverse applique|blouse panel", r"kuna|cuna|guna|panama|san blas", "kuna"),
    ("Mexican lacquer (maque: Olinala, Patzcuaro, Chiapa de Corzo)", "maque; laca", "Mexico", "", MCA, "lacquer",
     r"\bmaque\b|olinala|laca de|chiapa de corzo lacquer", r"lacquer|\blaca\b|lak\b|gelakt|batea|jicara", r"olinala|patzcuaro|uruapan|periban|chiapa de corzo|michoacan|guerrero|(?<!new )mexic", ""),
    ("Arbol de la vida (Metepec tree of life)", "tree of life ceramics", "Mexico", "", MCA, "ceramics", r"arbol de la vida",
     r"tree of life", r"metepec|izucar|(?<!new )mexic", ""),
    ("Barro negro (Oaxaca black pottery)", "San Bartolo Coyotepec", "Mexico", "Zapotec", MCA, "ceramics",
     r"barro negro|coyotepec|dona rosa", r"black pottery|blackware|black ware", r"oaxaca|(?<!new )mexic", ""),
    ("Mata Ortiz pottery", "Juan Quezada", "Mexico", "", MCA, "ceramics", r"mata ortiz|juan quezada", "", "", ""),
    ("Tonala and Tlaquepaque pottery", "petatillo; bruñido", "Mexico", "", MCA, "ceramics", r"petatillo|tlaquepaque",
     r"pottery|ceramic|jar|bowl|plate|earthenware|burnished|vessel|bottle|figure", r"tonala\b", ""),
    ("Mexican tinwork (hojalata)", "hojalata", "Mexico", "", MCA, "metalwork (tin)", r"hojalata",
     r"tin ?work|tinware|\btin (mirror|frame|ornament|nicho|sculpture|lantern)", r"(?<!new )mexic|oaxaca|san miguel", ""),
    ("Mexican dance masks", "mascaras", "Mexico; Guatemala", "", MCA, "masks", r"mascara de danza|danza de los",
     r"\bmasks?\b|mascara|masker", r"(?<!new )mexic|guerrero|michoacan|oaxaca|puebla|tlaxcala|chiapas|guatemal|sonora|yaqui|mayo\b", "mexican"),
    ("Saltillo serape", "sarape", "Mexico", "", MCA, "textile (woven)", r"saltillo", r"serape|sarape", r"(?<!new )mexic|saltillo", ""),
    ("Rebozo", "", "Mexico", "", MCA, "textile (shawl)", r"rebozo", "", "", ""),
    ("Mexican retablos and ex-votos", "laminas; exvotos", "Mexico", "", MCA, "painting (devotional)",
     r"ex-?voto|exvoto|retablo", "", r"", ""),
    ("New Mexican santos (retablos and bultos)", "santero; bulto", "United States (New Mexico)", "Hispano", NAM, "painting / sculpture (devotional)",
     r"santero|\bbultos?\b", r"\bsantos?\b(?! domingo)|retablo|\bsaints?\b|reredos", r"new mexico|nuevo mexico|santa fe|taos|truchas|cordova", ""),
    ("Puerto Rican santos de palo", "santos de palo", "Puerto Rico", "", MCA, "woodcarving (devotional)", r"santos? de palo",
     r"\bsantos?\b|\bsaints?\b|heilige", r"puerto rico", ""),
    ("Haitian vodou flags (drapo)", "drapo vodou; sequin flags", "Haiti", "", MCA, "textile (sequinned)", r"drapo|vodou flag|voodoo flag|sequin(ned)? (flag|banner)",
     r"sequin", r"haiti|vodou|vodun|voodoo", ""),
    ("Haitian metal art (Croix-des-Bouquets)", "fer decoupe", "Haiti", "", MCA, "metalwork", r"croix.des.bouquets|fer decoupe",
     r"steel drum|oil drum|metal (cut|sculpture)|cut metal", r"haiti", ""),
    ("Salvadoran La Palma painting", "Fernando Llort", "El Salvador", "", MCA, "painting", r"llort|la palma (art|paint|style)", "", "", ""),
    # ---------------------------------------------------------------- South America
    ("Arpilleras", "arpillera", "Chile; Peru", "", SAM, "textile (appliqué)", r"arpillera", "", "", ""),
    ("Taquile textiles", "", "Peru", "Quechua", SAM, "textile (woven / knitted)", r"taquile (textile|weav|knit)",
     r"textile|weav|knit|sash|belt|chumpi|chullo|\bcap\b|hat\b|bag|chuspa|poncho|shawl", r"taquile", ""),
    ("Quinchamali pottery", "", "Chile", "", SAM, "ceramics", r"quinchamali", "", "", ""),
    ("Retablos ayacuchanos", "caja de San Marcos; Huamanga", "Peru", "", SAM, "devotional box / sculpture",
     r"caja de san marcos|san marcos box|retablo ayacuchano|ayacucho retablo|jimenez (retablo|family)",
     r"retablo|piedra de huamanga|alabaster|huamanga stone", r"ayacucho|huamanga|peru", ""),
    ("Shipibo kene designs", "kene", "Peru", "Shipibo-Conibo", SAM, "textile / ceramics", r"\bkene\b|shipibo (design|pattern)",
     r"textile|ceramic|pottery|skirt|tunic|cushma|painted|aardewerk|vessel|jar|embroid", r"shipibo|conibo", "shipibo"),
    ("Wayuu mochila and weaving", "susu; Wayuu bag", "Colombia; Venezuela", "Wayuu", SAM, "textile (crochet / woven)",
     r"wayuu|guajiro", r"mochila|bag|hammock|chinchorro|susu\b|textile|weav", r"guajira", "wayuu"),
    ("Mapuche silverwork and weaving", "trapelacucha; trarilonco; makun", "Chile; Argentina", "Mapuche", SAM, "jewellery / textile",
     r"trapelacucha|trarilonco|trarilonko|chaway|makun|trarihue|tupu\b(?=.*mapuche)",
     r"silver|jewel|pectoral|pin|textile|poncho|blanket|belt|weav|head ?band|stirrup", r"mapuche|araucan", "mapuche"),
    ("Peruvian carved gourds (mates burilados)", "mate burilado", "Peru", "", SAM, "carved gourds", r"mates? burilados?|burilado",
     r"gourd", r"peru|huancayo|cochas|andean|ayacucho|huanta|quechua", ""),
    ("Chulucanas pottery", "", "Peru", "", SAM, "ceramics", r"chulucanas (pottery|ceramic)",
     r"pottery|ceramic|vessel|jar|vase|aardewerk", r"chulucanas", ""),
    ("Pucara bulls (toritos de Pucara)", "torito", "Peru", "", SAM, "ceramics", r"toritos?\b", r"bull|stier|\btoro\b|ceramic|pottery|aardewerk", r"pucara", ""),
    ("Sarhua painted boards (tablas de Sarhua)", "", "Peru", "", SAM, "painting", r"sarhua", "", "", ""),
    ("Andean aguayo and lliclla weaving", "awayu; aguayo; lliclla; manta", "Bolivia; Peru", "Aymara; Quechua", SAM, "textile (woven)",
     r"aguayo|awayu|awayo|lliclla|llijlla|ahuayo|unku\b|chuspa|ch uspa|axsu\b|aksu\b",
     r"carrying cloth|manta\b|mantle|shawl|omslagdoek",
     r"aymara|quechua|bolivi|andean|cuzco|cusco|potosi|chuquisaca|titicaca|charazani|chinchero|pitumarca", "aymara"),
    ("Jalq'a and Tarabuco weaving", "Jalq'a; Tarabuco; Potolo", "Bolivia", "Jalq'a; Yampara", SAM, "textile (woven)",
     r"jalq ?a\b|jalqa|tarabuco|potolo|yampara", "", "", ""),
    ("Otavalo weaving", "", "Ecuador", "Kichwa Otavalo", SAM, "textile (woven)", r"otavalo (weav|textile|poncho|tapestr)",
     r"weav|textile|poncho|sash|belt|blanket|tapestr|faja|shawl", r"otavalo", ""),
    ("Toquilla straw hat (Panama hat)", "paja toquilla; Montecristi", "Ecuador", "", SAM, "straw weaving",
     r"toquilla|panama hat", r"montecristi", r"\bhat\b|straw|hoed", ""),
    ("Tigua painting", "", "Ecuador", "Kichwa", SAM, "painting", r"\btigua\b", "", "", ""),
    ("Barniz de Pasto (mopa-mopa)", "mopa-mopa", "Colombia", "", SAM, "lacquer", r"barniz de pasto|mopa ?-?mopa|barniz", "", "", ""),
    ("Literatura de cordel woodcuts", "xilogravura; cordel", "Brazil", "", SAM, "popular prints", r"cordel|xilogravura", "", "", ""),
    ("Caruaru clay figures (Mestre Vitalino)", "figureiros; Alto do Moura", "Brazil", "", SAM, "ceramics (figurines)",
     r"vitalino|alto do moura", r"ceramic|clay|pottery|figure|figurine|aardewerk|beeld", r"caruaru", ""),
    ("Renda de bilro (Brazilian bobbin lace)", "", "Brazil", "", SAM, "lace", r"renda de bilro|\bbilro", "", "", ""),
    ("Karaja dolls (ritxoko)", "ritxoko; litjoko", "Brazil", "Karaja", SAM, "ceramics (figurines)", r"ritxoko|litjoko",
     r"doll|figure|figurine|ceramic|clay", r"karaja|caraja|iny\b", "karaja"),
    ("Amazonian feather art (plumaria)", "arte plumaria", "Brazil; Peru; Ecuador", "Kayapo; Bororo; Munduruku; Ka'apor", SAM,
     "featherwork", r"plumaria|arte plumaria",
     r"feather", r"kayapo|karaja|bororo|munduruku|tapirape|urubu|kaapor|ka apor|rikbaktsa|wayana|tukano|shuar|jivaro|achuar|"
     r"amazon|xingu|mato grosso|aguaruna|awajun|kamayura|waiwai|wai-wai|kaxinawa", "amazonian"),
    ("Paraguayan nanduti lace", "nanduti; ao po'i", "Paraguay", "", SAM, "lace", r"nanduti|ao po ?i|aopoi", "", "", ""),
    ("Gaucho silverwork (plateria criolla)", "plateria criolla", "Argentina; Uruguay; Brazil", "Gaucho", SAM, "metalwork (silver)",
     r"plateria criolla|gaucho silver|pampas silver", r"silver|spur|stirrup|mate\b|bombilla|knife|facon|belt|rastra",
     r"gaucho|argentin|uruguay|rio de la plata|pampas|rio grande do sul", "gaucho"),
    ("Rari horsehair weaving", "crin de Rari", "Chile", "", SAM, "fibre (horsehair)", r"\brari\b|crin de rari",
     "", "", ""),
    # ---------------------------------------------------------------- North America
    ("Pueblo pottery", "Acoma pottery; Zuni pottery; Hopi pottery; Santa Clara pottery; San Ildefonso pottery; Cochiti pottery", "United States", "Pueblo peoples", NAM,
     "ceramics", r"san ildefonso|maria martinez|nampeyo|storyteller (figure|doll)|sikyatki|santa clara (pueblo|pottery|blackware)",
     r"pottery|\bjar\b|olla|bowl|ceramic|vessel|canteen|seed pot|storyteller|figurine|pitcher|dough bowl|blackware|polychrome",
     r"pueblo|acoma|\bzuni|\bhopi|santa clara|san ildefonso|cochiti|\bzia\b|laguna|santo domingo|kewa|tesuque|jemez|isleta|"
     r"\btewa|nampeyo|picuris|taos|san juan pueblo|ohkay owingeh|tigua|keres|hano\b", "pueblo"),
    ("Navajo weaving", "Diné weaving; chief blanket; Two Grey Hills; Ganado; Teec Nos Pos", "United States", "Navajo (Diné)", NAM,
     "textile (woven)", r"two gr[ae]y hills|teec nos pos|ganado red|wide ruins|chief ?s blanket|germantown|eye ?dazzler|yei rug",
     r"weav|textile|\brugs?\b|blanket|serape|sarape|\bmanta\b|tapestr|tapijt|deken",
     r"navajo|navaho|\bdine\b", "navajo"),
    ("Navajo and Pueblo silversmithing", "squash blossom; concho belt", "United States", "Navajo; Zuni; Hopi", NAM,
     "jewellery (silver / turquoise)", r"squash blossom|concho belt|concha belt|ketoh",
     r"silver|jewel|concho|bracelet|bridle|necklace|\brings?\b|bow guard|turquoise|zilver",
     r"navajo|navaho|\bdine\b|\bzuni|\bhopi|santo domingo|kewa", "navajo"),
    ("Zuni fetishes and inlay jewellery", "Zuni needlepoint", "United States", "Zuni", NAM, "carving / jewellery",
     r"zuni (fetish|inlay|needlepoint|petit point)", r"fetish|inlay|needlepoint|petit point|jewel|carv", r"\bzuni", "zuni"),
    ("Hopi katsina dolls (tihu)", "kachina dolls; tihu", "United States", "Hopi", NAM, "woodcarving (figures)", r"kachina|\btihu\b",
     r"\bkatsina\b", r"hopi|zuni|pueblo|doll|\bpop\b", "hopi"),
    ("Seminole patchwork", "Miccosukee patchwork", "United States", "Seminole; Miccosukee", NAM, "textile (patchwork)",
     r"seminole patchwork", r"patchwork|textile|skirt|jacket|shirt|cape|doll|big shirt", r"seminole|miccosukee", "seminole"),
    ("Ledger art", "ledger drawing; ledger book", "United States", "Cheyenne; Kiowa; Lakota; Arapaho", NAM, "drawing",
     r"ledger (drawing|art|book|page|sheet)|fort marion|ledger", "", "", ""),
    ("Plains beadwork and quillwork", "porcupine quillwork", "United States; Canada", "Lakota; Cheyenne; Crow; Blackfoot", NAM,
     "beadwork / quillwork", r"quill ?work|porcupine quill",
     r"\bbead|beaded|quill|kralen",
     r"lakota|sioux|dakota|nakota|cheyenne|\bcrow\b|apsaalooke|blackfeet|blackfoot|arapaho|kiowa|comanche|plains|assiniboine|"
     r"nez perce|shoshone|\bute\b|osage|omaha|pawnee|mandan|hidatsa|gros ventre|cree", "plains"),
    ("Great Lakes beadwork and ribbonwork", "bandolier bag; gashkibidaagan; floral beadwork", "United States; Canada",
     "Ojibwe; Potawatomi; Menominee; Ho-Chunk; Meskwaki", NAM, "beadwork / ribbonwork",
     r"bandolier bag|gashkibidaagan|ribbon ?work",
     r"\bbead|beaded|ribbon|kralen",
     r"ojibw|anishinaabe|chippewa|potawatomi|menominee|winnebago|ho-?chunk|great lakes|ottawa|odawa|meskwaki|sauk|fox\b|"
     r"miami|delaware|lenape|kickapoo|shawnee", "ojibwe"),
    ("Haudenosaunee raised beadwork", "Iroquois whimsies", "United States; Canada", "Haudenosaunee", NAM, "beadwork",
     r"whimsy|whimsies|raised beadwork", r"\bbead|beaded|kralen", r"iroquois|haudenosaunee|mohawk|seneca|tuscarora|"
     r"onondaga|oneida|cayuga|kahnawake|akwesasne", "iroquois"),
    ("Metis floral beadwork and octopus bags", "octopus bag; fire bag", "Canada", "Metis", NAM, "beadwork / embroidery",
     r"octopus bag|fire bag", r"bead|embroid|floral|bag|moccasin|jacket|sash", r"\bmetis\b|michif", "metis"),
    ("Chilkat and Ravenstail weaving", "naaxein", "United States; Canada", "Tlingit; Haida; Tsimshian", NAM, "textile (twined)",
     r"chilkat (blanket|robe|tunic|weav|dancing|apron|leggings)|naaxein|ravenstail", "", "", "tlingit"),
    ("Northwest Coast carving (totem poles, masks, bentwood boxes)", "formline", "Canada; United States",
     "Haida; Tlingit; Kwakwaka'wakw; Tsimshian; Nuu-chah-nulth", NAM, "woodcarving",
     r"totem pole|bentwood box|formline|transformation mask",
     r"totem|\bmasks?\b|masker|carv|snijwerk|rattle|frontlet|bentwood|panel|figure|\bpole\b",
     r"tlingit|haida|kwakwaka|kwakiutl|tsimshian|nuu-?chah|nootka|nuxalk|bella coola|heiltsuk|bella bella|makah|"
     r"coast salish|northwest coast|north west coast", "northwest coast"),
    ("Haida argillite carving", "", "Canada", "Haida", NAM, "stone carving", r"haida argillite", r"argillite", r"haida|skidegate|queen charlotte", "haida"),
    ("Native American basketry (California, Southwest, Plateau, Wabanaki)", "Pomo baskets; Apache baskets; Washoe degikup",
     "United States; Canada", "Pomo; Apache; Washoe; Tohono O'odham; Wabanaki", NAM, "basketry",
     r"degikup|pomo basket|apache (burden|olla) basket",
     r"basket|olla basket|burden basket|tray\b|winnowing|hat\b",
     r"pomo|apache|washoe|chemehuevi|yokuts|tohono|o odham|pima|papago|hupa|karuk|yurok|panamint|\bmono\b|miwok|maidu|"
     r"aleut|attu|chitimacha|passamaquoddy|penobscot|wabanaki|mi kmaq|micmac|maliseet|klickitat|yakama|cowlitz|"
     r"nuu-?chah|tlingit|haida|cherokee|choctaw|coushatta|havasupai|hualapai|paiute|shoshone|cahuilla|chumash|luiseno|"
     r"wasco|nez perce|tulare|kumeyaay|diegueno", "native american"),
    ("Inuit prints (Kinngait / Cape Dorset, Baker Lake)", "Kinngait; Cape Dorset; Qamani'tuaq", "Canada", "Inuit", NAM,
     "printmaking", r"(kinngait|cape dorset|west baffin) (print|studio|annual|graphic)|west baffin eskimo",
     r"print|stonecut|stencil|lithograph|etching|engraving|drawing|prent",
     r"inuit|eskimo|kinngait|cape dorset|baker lake|qamani ?tuaq|pangnirtung|ulukhaktok|puvirnituq|povungnituk|nunavut|nunavik", "inuit"),
    ("Inuit stone and ivory carving", "", "Canada; United States; Greenland", "Inuit; Yup'ik; Inupiat", NAM, "stone / ivory carving",
     r"inuit (sculpt|carv)|eskimo (carv|ivory)",
     r"sculpture|soapstone|serpentine|carving|carved figure|figurine|beeld",
     r"inuit|eskimo|inupiat|inupiaq|nunavut|nunavik|cape dorset|kinngait|igloolik|repulse bay|naujaat|greenland|kalaallit", "inuit"),
    ("Yup'ik masks", "Yupik masks", "United States", "Yup'ik", NAM, "masks", r"yup ?ik mask|yupik mask|cup ik mask",
     r"mask", r"yup ?ik|yupik|cup ik|kuskokwim|nunivak|yukon delta", "yupik"),
    ("American quilts", "album quilts; crazy quilts; Baltimore album", "United States", "", NAM, "textile (quilting)",
     r"baltimore album|album quilt|crazy quilt",
     r"quilt", r"american|united states|new england|pennsylvania|ohio|kentucky|virginia|new york|maryland|indiana|"
     r"massachusetts|connecticut|tennessee|carolina|illinois|new jersey|vermont|maine", "american"),
    ("Amish quilts", "Mennonite quilts", "United States", "Amish", NAM, "textile (quilting)", r"amish quilt",
     r"quilt", r"amish|mennonite|lancaster county", "amish"),
    ("African American quilts (Gee's Bend)", "Gee's Bend; Harriet Powers", "United States", "African American", NAM,
     "textile (quilting)", r"gee ?s bend|boykin|harriet powers", r"quilt", r"african american|african-american|black american|"
     r"enslaved|alabama", "african american"),
    ("Hawaiian quilts (kapa apana)", "kapa apana", "United States (Hawaii)", "Native Hawaiian", OC, "textile (quilting)",
     r"kapa ?apana|kapa kuiki", r"quilt", r"hawai", "hawaiian"),
    ("Pennsylvania German fraktur", "Taufschein; Vorschrift", "United States", "Pennsylvania German", NAM, "drawing / illumination",
     r"taufschein|vorschrift|geburts.?und.?taufschein", r"fraktur", r"pennsylvania|american|ohio|virginia|maryland|ephrata|"
     r"bucks county|berks|lancaster", "pennsylvania german"),
    ("Pennsylvania German decorated redware and painted chests", "sgraffito redware; dower chest", "United States",
     "Pennsylvania German", NAM, "ceramics / furniture", r"pennsylvania (german|dutch) (dower|chest|redware|sgraffito)",
     r"sgraffito|redware|slip.?decorated|dower chest|painted chest|blanket chest", r"pennsylvania (german|dutch)|berks county|lancaster county|bucks county|montgomery county|lehigh", "pennsylvania german"),
    ("Shaker crafts (oval boxes, furniture)", "", "United States", "Shaker", NAM, "furniture / woodwork",
     r"shaker (oval|box|chair|furniture|basket|rocker|rocking|cabinet|community|desk|stand|table|cloak|bonnet|sister)", "", "", "shaker"),
    ("American weathervanes and whirligigs", "", "United States", "", NAM, "metalwork / folk sculpture",
     r"weather ?vane|whirligig", "", "", ""),
    ("American decoys", "", "United States; Canada", "", NAM, "woodcarving", r"(duck|goose|shorebird|bird|canvasback|merganser|plover|curlew|swan|heron|mallard|teal) decoy",
     r"\bdecoy", r"american|united states|canad", ""),
    ("Scrimshaw", "", "United States", "", NAM, "engraved bone / ivory", r"scrimshaw", "", "", ""),
    ("American folk portraiture (limners)", "limner; itinerant portrait", "United States", "", NAM, "painting",
     r"\blimner|itinerant (painter|portrait)|folk portrait", "", "", ""),
    ("Theorem painting", "velvet painting", "United States", "", NAM, "painting", r"theorem (painting|picture)", "", "", ""),
    ("American needlework samplers", "", "United States", "", NAM, "embroidery", r"american sampler",
     r"sampler|needlework picture|mourning picture", r"american|united states|massachusetts|new england|pennsylvania|"
     r"connecticut|rhode island|new york|philadelphia|new jersey|maryland|virginia|new hampshire|boston|salem", "american"),
    ("Gullah sweetgrass baskets", "sweetgrass baskets", "United States", "Gullah Geechee", NAM, "basketry",
     r"gullah|mount pleasant basket", r"sweet ?grass", r"south carolina|charleston|gullah|geechee|african american", ""),
    ("Hooked rugs (incl. Grenfell mats)", "Grenfell mats", "United States; Canada", "", NAM, "textile (hooked)",
     r"hooked rug|rug hooking|grenfell (mat|hooked)|hooked mat", "", "", ""),
    ("Edgefield stoneware and face jugs", "Dave the Potter", "United States", "African American", NAM, "ceramics",
     r"edgefield|face jug|david drake|dave the potter", "", "", ""),
    ("Tramp art", "", "United States", "", NAM, "woodwork", r"tramp art", "", "", ""),
    # ---------------------------------------------------------------- Oceania
    ("Tongan ngatu (tapa)", "ngatu", "Tonga", "Tongan", OC, "barkcloth", r"ngatu",
     r"tapa|bark ?-?cloth|kupesi|boombast", r"tonga", "tongan"),
    ("Samoan siapo (tapa)", "siapo", "Samoa", "Samoan", OC, "barkcloth", r"siapo", r"tapa|bark ?-?cloth|boombast", r"samoa", "samoan"),
    ("Fijian masi (tapa)", "masi kesa", "Fiji", "Fijian", OC, "barkcloth", r"masi kesa|gatu vakaviti",
     r"tapa|bark ?-?cloth|boombast|\bmasi\b", r"fiji|lau islands|vatulele", "fijian"),
    ("Hawaiian kapa", "kapa moe", "United States (Hawaii)", "Native Hawaiian", OC, "barkcloth", r"\bkapa\b(?! ?apana| kuiki)",
     r"tapa|bark ?-?cloth", r"hawai", "hawaiian"),
    ("Omie and Maisin barkcloth (Papua New Guinea)", "nioge; tapa", "Papua New Guinea", "Omie; Maisin", OC, "barkcloth",
     r"\bomie\b|maisin|nioge", r"tapa|bark ?-?cloth|boombast", r"oro province|collingwood bay|northern province", ""),
    ("Polynesian tapa (other: Niue, Tahiti, Marquesas, Wallis-Futuna, Rapa Nui)", "ahu; hiapo", "French Polynesia; Niue; Wallis and Futuna",
     "", OC, "barkcloth", r"hiapo", r"tapa|bark ?-?cloth",
     r"niue|tahiti|marquesa|futuna|wallis|uvea|austral island|rapa nui|easter island|cook island|society island|polynes", ""),
    ("Tivaevae (Cook Islands quilts)", "tivaivai; tifaifai", "Cook Islands; French Polynesia", "Cook Islands Maori", OC,
     "textile (appliqué quilting)", r"tivaevae|tivaivai|tifaifai", "", "", ""),
    ("Lalava (Pacific lashing)", "magimagi; sennit lashing", "Tonga; Fiji; Samoa", "", OC, "fibre (lashing)", r"lalava|magimagi",
     r"(decorative|patterned|ornamental) (sennit|lashing)|sennit lashing|lashing pattern", r"tonga|fiji|samoa|polynes", ""),
    ("Bilum (PNG string bags)", "bilum; string bag", "Papua New Guinea", "", OC, "fibre (looped bags)", r"\bbilum",
     r"string bag|net ?bag|looped bag|netted bag", r"papua|new guinea|\bpng\b|sepik|highlands|wahgi|enga\b|huli", ""),
    ("Maori weaving (raranga, whatu: kakahu, korowai, kete, whariki)", "raranga; whatu; kakahu; korowai; kaitaka; piupiu",
     "New Zealand", "Maori", OC, "textile (weaving)", r"raranga|kakahu|korowai|kaitaka|kahu kiwi|kahu huruhuru|kahu kuri|piupiu|"
     r"whariki|\bwhatu\b|harakeke", r"\bkete\b|cloak|weav|flax|\bmat\b|basket|bag|garment", r"maori|aotearoa|new zealand", "maori"),
    ("Taniko", "", "New Zealand", "Maori", OC, "textile (twined borders)", r"taniko", "", "", "maori"),
    ("Maori whakairo (carving)", "whakairo; tekoteko; poupou; wakahuia; tauihu", "New Zealand", "Maori", OC, "woodcarving",
     r"whakairo|tekoteko|poupou|wakahuia|waka huia|tauihu|taurapa|koruru|tiki wananga",
     r"carv|snijwerk|figure|panel|treasure box|lintel|\bpare\b", r"maori|aotearoa|new zealand", "maori"),
    ("Maori pounamu (greenstone) and hei-tiki", "hei-tiki; pounamu; mere pounamu", "New Zealand", "Maori", OC, "stone carving",
     r"pounamu|hei ?-?tiki|mere pounamu|heitiki", r"greenstone|nephrite|jade", r"maori|new zealand", "maori"),
    ("Kowhaiwhai and tukutuku (meeting-house painting and panels)", "kowhaiwhai; tukutuku", "New Zealand", "Maori", OC,
     "painting / lattice panels", r"kowhaiwhai|tukutuku", "", "", "maori"),
    ("Aboriginal fibre art (Tjanpi, ghost nets, dilly bags, pandanus weaving)", "Tjanpi; ghost net art; dilly bag",
     "Australia", "Aboriginal Australians", OC, "fibre", r"tjanpi|ghost ?net|dilly bag|bathi\b|mindi\b|jilli bag|\bbatji",
     r"fibre|fiber|basket|\bmand|\bbag\b|\bmat\b|weav|string|pandanus|twined|coiled|feather string|gevlochten",
     r"aborigin|arnhem|yolngu|maningrida|ramingining|elcho|galiwin|yirrkala|milingimbi|tiwi|kimberley|"
     r"western desert|warlpiri|pitjantjatjara|ngaanyatjarra|anindilyakwa", "aboriginal"),
    ("Torres Strait Islander art (dhari, masks, printmaking)", "dhari; Zenadth Kes", "Australia", "Torres Strait Islanders", OC,
     "masks / carving / prints", r"torres strait|zenadth|mabuiag|saibai|darnley island|murray island|dari headdress", "", "", "torres strait"),
    ("Asmat carving", "bisj poles; Asmat shields", "Indonesia (Papua)", "Asmat", OC, "woodcarving", r"\basmat\b|\bbisj\b|mbis\b",
     "", "", "asmat"),
    ("Sepik carving and painting (Iatmul, Abelam, Kwoma)", "", "Papua New Guinea", "Iatmul; Abelam; Kwoma", OC, "woodcarving / painting",
     r"iatmul|abelam|kwoma|chambri|\byimar|sawos|karawari|kambot|\bsepik", "", "", "sepik"),
    ("Massim carving (Trobriand, kula)", "Trobriand carving; kula canoe prow", "Papua New Guinea", "Massim", OC, "woodcarving",
     r"trobriand|kiriwina|massim|kula (canoe|prow|ring)|tabuya|lagim", "", "", "massim"),
    ("Solomon Islands shell inlay (nguzunguzu)", "nguzunguzu", "Solomon Islands", "", OC, "woodcarving (inlay)",
     r"nguzunguzu|toto isu|musumusu", r"inlay|inlaid|ingelegd|figurehead|canoe prow", r"solomon|new georgia|roviana|marovo", ""),
    ("Vanuatu slit drums and grade figures (tamtam)", "atingting kon", "Vanuatu", "ni-Vanuatu", OC, "woodcarving",
     r"tamtam|atingting|tam-tam", r"slit.?(gong|drum)|grade (figure|society)|rambaramp",
     r"vanuatu|ambrym|malakula|malekula|new hebrides|pentecost", ""),
    ("Kiribati coconut-fibre armour", "", "Kiribati", "I-Kiribati", OC, "fibre (armour)", r"",
     r"armou?r|cuirass|helmet|corselet|corslet|shark.?tooth|sword", r"kiribati|gilbert island", "kiribati"),
    ("Marshall Islands stick charts", "rebbelib; mattang; meddo", "Marshall Islands", "Marshallese", OC, "navigation charts",
     r"stick chart|rebbelib|mattang|meddo\b", "", "", ""),
    ("Hawaiian featherwork (ahu ula, mahiole, kahili)", "ahu ula; mahiole; kahili", "United States (Hawaii)", "Native Hawaiian",
     OC, "featherwork", r"ahu ?ula|mahiole|kahili|lei hulu", r"feather (cloak|cape|helmet|lei|standard|image)", r"hawai", "hawaiian"),
    ("Pacific fine mats (ie toga, kiekie)", "ie toga; kiekie; fala", "Samoa; Tonga; Tuvalu", "", OC, "fibre (plaited)",
     r"ie ?toga|ie sae|ta ovala", r"fine mat|pandanus mat",
     r"samoa|tonga|tuvalu|kiribati|marshall|micronesia|fiji|wallis|futuna|tokelau", ""),
]
# expand to named fields
FIELDS = ("label", "aliases", "country", "people", "region", "medium", "rx", "weak", "ctx", "cell")
TRADITIONS = [dict(zip(FIELDS, t)) for t in T]
assert all(len(t) == len(FIELDS) for t in T), [t[0] for t in T if len(t) != len(FIELDS)]
for _t in TRADITIONS:
    assert _t["rx"] or (_t["weak"] and _t["ctx"]), _t["label"]
    assert not _t["weak"] or _t["ctx"], _t["label"]

STRONG_IDX = [i for i, t in enumerate(TRADITIONS) if t["rx"]]
WEAK_IDX = [i for i, t in enumerate(TRADITIONS) if t["weak"]]
STRONG_M = GramMatcher([TRADITIONS[i]["rx"] for i in STRONG_IDX])
WEAK_M = GramMatcher([TRADITIONS[i]["weak"] for i in WEAK_IDX])
CTX_RX = {i: re.compile(TRADITIONS[i]["ctx"]) for i in WEAK_IDX}
# strong-rule exceptions: a strong rule must not fire inside these European / unrelated uses
STRONG_GUARD = {
    "Mexican retablos and ex-votos": re.compile(r"(?<!new )mexic|new spain|nueva espana|guanajuato|jalisco|zacatecas|san luis potosi|"
                                                r"puebla|oaxaca|michoacan|queretaro|lamina"),
    "Pucara bulls (toritos de Pucara)": re.compile(r"peru|puno|pucara|andean|cusco|cuzco"),
    "Barniz de Pasto (mopa-mopa)": re.compile(r"pasto|colombia|new granada|mopa|ecuador|quito"),
    "American decoys": re.compile(r"duck|goose|bird|fish|shorebird|plover|curlew|carv|wood|merganser|swan"),
    "Literatura de cordel woodcuts": re.compile(r"brazil|nordeste|pernambuco|ceara|paraiba|bahia|xilogravura"),
    "Ledger art": re.compile(r"cheyenne|kiowa|lakota|sioux|arapaho|crow|plains|native american|fort marion|drawing|"
                             r"indigenous|comanche|kiowa"),
    "Chinese New Year prints (nianhua)": re.compile(r"\bchin(a|ese)\b|nianhua|tianjin|suzhou|kaifeng|shandong|hebei|sichuan|"
                                                    r"yangliuqing|taohuawu|yangjiabu|zhuxianzhen|wuqiang|mianzhu"),
    "Gullah sweetgrass baskets": re.compile(r"basket|gullah|carolina|georgia"),
    "Ndop (Cameroon Grassfields resist-dyed cloth)": re.compile(r"cameroon|bamileke|bamum|bamoun|grassfields|cloth|textile"),
    "Kanga and kitenge": re.compile(r"cloth|textile|wrap|print|kenya|tanzania|zanzibar|swahili|zambia|africa"),
    "Rari horsehair weaving": re.compile(r"chile|horsehair|crin"),
    "Kalamezhuthu and kolam floor drawing": re.compile(r"india|kerala|tamil|kolam|rangoli|kalamezhuthu"),
    "Taiwanese Indigenous carving and weaving (Paiwan, Atayal, Rukai, Tao)": re.compile(r"taiwan|formosa|paiwan|atayal|rukai"),
    "Toquilla straw hat (Panama hat)": re.compile(r"hat|straw|toquilla|ecuador|montecristi"),
    "Wayang (shadow and rod puppets)": re.compile(r"puppet|wayang|java|bali|indonesia|malay|figure|leather|wood"),
    "Pueblo pottery": re.compile(r"pueblo|ildefonso|nampeyo|martinez|sikyatki|santa clara|storyteller|hopi|zuni|tewa|acoma"),
    "Phad painting": re.compile(r"paint|scroll|rajasthan|india|pabuji|devnarayan"),
    "Kantha": re.compile(r"bengal|bangla|india|quilt|embroid|textile|cloth"),
    "Kente": re.compile(r"ghana|asante|ashanti|ewe|akan|togo|cloth|textile|weav|strip|kente"),
    "Kokeshi": re.compile(r"japan|doll|wood|tohoku|kokeshi"),
    "Japanese folk toys (kyodo gangu, hariko, Fushimi dolls)": re.compile(r"japan|doll|toy|ningyo|papier|hariko|fushimi"),
    "Fijian masi (tapa)": re.compile(r"fiji|tapa|bark|masi"),
    "Mola": re.compile(r"kuna|cuna|guna|panama|san blas|textile|blouse|applique|cloth"),
    "Rebozo": re.compile(r"mexic|shawl|textile|ikat|silk|cotton"),
}
for _lab in STRONG_GUARD:
    assert any(t["label"] == _lab for t in TRADITIONS), _lab


# archaeological objects are not evidence for a living folk tradition
NEGATIVE = re.compile(r"archaeolog|projectile point|bifacial|hammerstone|potsherd|\bsherds?\b|pre-?columbian|"
                      r"precolumbian|pre-?hispanic|prehistoric|ancestral pueblo|\bolmec|teotihuacan|toltec|\bmoche\b|"
                      r"nazca|nasca|chimu|paracas|\bwari\b|\bhuari\b|chancay|vicus|recuay|cupisnique|\bmochica|"
                      r"hohokam|mogollon|mimbres|anasazi|mississippian|hopewell|adena")


def match_text(text):
    """Indexes of TRADITIONS matched by folded text."""
    if NEGATIVE.search(text):
        return set()
    hits = set()
    for j in STRONG_M.all(text):
        i = STRONG_IDX[j]
        g = STRONG_GUARD.get(TRADITIONS[i]["label"])
        if g is None or g.search(text):
            hits.add(i)
    for j in WEAK_M.all(text):
        i = WEAK_IDX[j]
        if i not in hits and CTX_RX[i].search(text):
            hits.add(i)
    return hits


# ------------------------------------------------------------------ 1. Wikidata

# collection items typed only by their medium (e.g. SAAM "decorative artwork (ceramic) by ...")
INDIVIDUAL_P31 = {"decorative art", "ceramic art", "fiber art", "glass", "jewelry", "furniture", "toy", "plaque", "table",
                  "box", "sculpture", "work of art", "set of physical objects", "art collection", "carving", "vase",
                  "bowl", "textile", "quilt", "basket", "mask", "doll", "painting", "print", "photograph", "drawing",
                  "scale model", "model", "costume", "garment", "rug", "carpet"}
INDIVIDUAL_DESC = re.compile(r"^(decorative artwork|jewelry by|artwork by|scale model|object highlighted|textile by|"
                             r"ceramic by|print by|sculpture by|painting by|quilt by)|\(smithsonian|\bcollection of the\b|"
                             r"by unknown artist|\(\d{4}\.\d+\)|jewelry brand|\bbrand\b|\bcompany\b|"
                             r"pancake|\bfood\b|\bdish\b|\bsnack|cuisine|\bcake\b|highlighted in|metropolitan museum|national gallery|"
                             r"woodcut by|etching by|engraving by|anonymous painting|\bwriters\b|\bivories\b", re.I)
INDIVIDUAL_LABEL = re.compile(r"^(portion|fragment|part|pair|set) of\b|^clay toy in the form|^untitled", re.I)
FINE_ART_MOVEMENT = re.compile(r"modernis|avant.?garde|contemporary art|abstract|expressionis|surrealis|realism|"
                               r"\bschool of (fine )?art|academy", re.I)
ARCHAEO = re.compile(r"archaeolog|neolithic|j[oō]mon|haniwa|terra sigillata|style group|bronze age|iron age|"
                     r"paleolithic|palaeolithic|mesolithic|chalcolithic|pre-?columbian|prehistoric|\byayoi\b|\bkofun\b|"
                     r"\bancient\b|1st millennium bce|bce\b|distribution area|ceramic trad|\bancestral\b|pre-?latte|"
                     r"latte period|latte plainware|lapita|phoenic|carthag|amphora|amforas|\baztec|\binca\b|olmec|moche|nazca|"
                     r"teotihuacan|toltec|maya (painting|art)\b|medieval", re.I)


REGION_KEYWORDS = [
    (re.compile(r"mamluk|ottoman|safavid|qajar|persia|abbasid|umayyad|fatimid|ayyubid|seljuk|timurid|bukhara|khiva|"
                r"kokand|egypt|ilkhan|ghaznavid|samanid|zand|caliphate|sultanate of (rum|oman)"), "MENA / Central Asia"),
    (re.compile(r"korea|goryeo|joseon|silla|baekje|japan|ryukyu|chin(a|ese)|\bhan dynasty|\btang\b|\bsong dynasty|"
                r"\bming\b|\bqing\b|\byuan\b|\bzhou\b|\bchu\b|\bwei\b|\bjin\b|\bliao\b|mongol|manchu"), "East Asia"),
    (re.compile(r"malacca|johor|aceh|mataram|majapahit|srivijaya|siam|burm|khmer|champa|viet|ayutthaya|sukhothai|"
                r"lan na|brunei|sulu|bali\b|java"), "Southeast Asia"),
    (re.compile(r"mughal|maratha|bengal|delhi|deccan|sikh|rajput|vijayanagara|chola|ceylon|kandy|india|nepal|mysore|"
                r"hyderabad|gupta|\bpala\b|kushan"), "South Asia"),
]


def region_from_label(lab):
    f = fold(lab)
    for rx, reg in REGION_KEYWORDS:
        if rx.search(f):
            return reg
    return None


def world_countries():
    """{country qid: (label, region)} for country-like items with a non-European continent,
    excluding europe_folk's European / Caucasian countries."""
    rows = sparql_cached("""SELECT DISTINCT ?c ?cl ?cont WHERE {
      ?c wdt:P30 ?cont .
      VALUES ?t { wd:Q6256 wd:Q3624078 wd:Q3024240 wd:Q7275 wd:Q3336843 wd:Q1763527 wd:Q15634554
                  wd:Q417175 wd:Q161243 wd:Q46395 wd:Q50068795 wd:Q164950 wd:Q48349 }
      ?c wdt:P31 ?t . ?c rdfs:label ?cl FILTER(lang(?cl)='en') }""", "world_countries")
    europe = set(ef.europe_countries())
    conts = collections.defaultdict(set)
    labels = {}
    for r in rows:
        conts[r["c"]].add(r["cont"])
        labels[r["c"]] = r["cl"]
    out = {}
    for c, cs in conts.items():
        lab = labels[c]
        if c in europe or lab in ef.REGION_OF:
            continue
        if not cs & NON_EU_CONTINENTS:
            continue
        reg = REGION_BY_LABEL.get(lab)
        if not reg:
            for k in ("Q15", "Q18", "Q55643", "Q538", "Q3960", "Q49", "Q48"):
                if k in cs:
                    reg = CONTINENT_REGION[k]
                    break
        if reg in (None, "Asia (other)", "Africa") and lab not in REGION_BY_LABEL:
            reg = region_from_label(lab) or reg
        out[c] = (lab, reg or "unknown")
    return out


def load_europe_details():
    """europe_folk's cached detail rows -> (info, covered qids)."""
    info = collections.defaultdict(lambda: collections.defaultdict(set))
    covered = set()
    for fn in glob.glob(os.path.join(EU_WD_DIR, "det_cty_*.json")):
        for r in json.load(open(fn, encoding="utf-8")):
            info[r["i"]]["country_q"].add(r["c"])
    for tag in ("lab", "loc", "eth", "cls", "her", "inc", "alias"):
        for fn in glob.glob(os.path.join(EU_WD_DIR, f"det_{tag}_*.json")):
            for r in json.load(open(fn, encoding="utf-8")):
                absorb(info[r["i"]], tag, r)
                if tag == "lab":
                    covered.add(r["i"])
    return info, covered


def absorb(d, tag, r):
    if tag == "lab":
        d["sitelinks"].add(int(r["sl"]))
        for k in ("l", "lru", "lany", "d"):
            if r.get(k):
                d[k].add(r[k])
        if r.get("en"):
            d["enwiki"].add(r["en"])
    elif tag == "loc":
        d["loc_country_q"].add(r["c"])
    elif tag == "eth":
        d["ethnic"].add(r["el"])
    elif tag == "cls":
        d["p31" if r["p"].endswith("P31") else "p279"].add(r["cl"])
    elif tag == "her":
        d["ich" if r["p"].endswith("P3259") else "heritage"].add(r["hl"])
    elif tag == "inc":
        y = wikidata.year_of(r["t"])
        if y is not None:
            d["year"].add(y)
    elif tag == "alias":
        d["alias"].add(r["a"])


DETAIL_QUERIES = {
    "lab": """SELECT ?i ?sl ?l ?lru ?lany ?d ?en WHERE { VALUES ?i { %s } ?i wikibase:sitelinks ?sl .
        OPTIONAL { ?i rdfs:label ?l FILTER(lang(?l)='en') } OPTIONAL { ?i rdfs:label ?lru FILTER(lang(?lru)='ru') }
        OPTIONAL { ?i rdfs:label ?lany FILTER(lang(?lany) IN ('mul','es','fr','pt','id','ja','zh','ko','hi','ar','tr','fa','de')) }
        OPTIONAL { ?i schema:description ?d FILTER(lang(?d)='en') }
        OPTIONAL { ?en schema:about ?i ; schema:isPartOf <https://en.wikipedia.org/> } }""",
    "loc": """SELECT ?i ?c WHERE { VALUES ?i { %s } ?i (wdt:P131|wdt:P276|wdt:P2341|wdt:P1071) ?x . ?x wdt:P17 ?c }""",
    "eth": """SELECT ?i ?el WHERE { VALUES ?i { %s } ?i (wdt:P172|wdt:P2341) ?e . ?e rdfs:label ?el FILTER(lang(?el)='en') }""",
    "cls": """SELECT ?i ?p ?cl WHERE { VALUES ?i { %s } VALUES ?p { wdt:P31 wdt:P279 } ?i ?p ?c .
        ?c rdfs:label ?cl FILTER(lang(?cl)='en') }""",
    "her": """SELECT ?i ?p ?hl WHERE { VALUES ?i { %s } VALUES ?p { wdt:P3259 wdt:P1435 } ?i ?p ?h .
        ?h rdfs:label ?hl FILTER(lang(?hl)='en') }""",
    "inc": """SELECT ?i ?t WHERE { VALUES ?i { %s } ?i (wdt:P571|wdt:P580) ?t }""",
    "alias": """SELECT ?i ?a WHERE { VALUES ?i { %s } ?i skos:altLabel ?a FILTER(lang(?a)='en') }""",
}


def fetch_details(qids, info, tags=None):
    qids = sorted(qids, key=lambda q: int(q[1:]))
    tags = tags or list(DETAIL_QUERIES)
    total = (len(qids) + 249) // 250 * len(tags)
    done = 0
    for tag in tags:
        for chunk in batched(qids, 250):
            vals = " ".join(f"wd:{q}" for q in chunk)
            for r in sparql_cached(DETAIL_QUERIES[tag] % vals, f"det_{tag}"):
                absorb(info[r["i"]], tag, r)
            done += 1
            if done % 20 == 0:
                print(f"    details {done}/{total}", flush=True)


def europe_folk_qids():
    path = os.path.join(OUT_DIR, "europe_folk_traditions.csv")
    out = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("qid"):
                    out.add(r["qid"])
    return out


def harvest_wikidata():
    countries = world_countries()
    print(f"Wikidata: {len(countries)} non-European country items "
          f"({dict(collections.Counter(r for _, r in countries.values()))})", flush=True)
    europe_q = set(ef.europe_countries())
    via = collections.defaultdict(set)
    needs_signal = set()
    for qid, label, mode, signal in ROOTS:
        members = ef_root_members(qid, mode)
        for m in members:
            via[m].add(label)
            if signal:
                needs_signal.add(m)
    for r in sparql_cached("SELECT DISTINCT ?i WHERE { ?i wdt:P3259 ?v }", "ich_all"):
        via[r["i"]].add("ICH status")
    for r in sparql_cached("SELECT DISTINCT ?i WHERE { ?i wdt:P6599 ?v }", "hca_all"):
        via[r["i"]].add("HCA Red List")
    print(f"  candidates from roots + ICH + HCA: {len(via)}", flush=True)
    info, covered = load_europe_details()
    todo = [q for q in via if q.startswith("Q") and q not in covered and info[q]["country_q"]
            and not info[q]["country_q"] & europe_q]
    print(f"  details cached by europe_folk: {len(covered)}; to fetch (non-European country): {len(todo)}", flush=True)
    fetch_details(todo, info)
    # country items outside both lists (historical states without P30 etc.): label them
    unknown = {c for q in via for c in info[q]["country_q"] | info[q]["loc_country_q"]
               if c not in countries and c not in europe_q}
    extra_lab = {}
    for chunk in batched(sorted(unknown), 300):
        vals = " ".join(f"wd:{q}" for q in chunk)
        for r in sparql_cached("""SELECT ?c ?cl (GROUP_CONCAT(DISTINCT ?k; separator='|') AS ?ks) WHERE { VALUES ?c { %s }
                OPTIONAL { ?c rdfs:label ?cl FILTER(lang(?cl)='en') } OPTIONAL { ?c wdt:P30 ?k } } GROUP BY ?c ?cl""" % vals,
                               "country_extra"):
            ks = set(filter(None, r.get("ks", "").split("|")))
            lab = r.get("cl", "")
            reg = REGION_BY_LABEL.get(lab)
            if not reg and ks & NON_EU_CONTINENTS and "Q46" not in ks:
                reg = next(CONTINENT_REGION[k] for k in ("Q15", "Q18", "Q55643", "Q538", "Q3960", "Q49", "Q48") if k in ks)
                if reg in ("Asia (other)", "Africa"):
                    reg = region_from_label(lab) or reg
            elif not reg and not ks and region_from_label(lab):
                reg = region_from_label(lab)
            if reg:
                extra_lab[r["c"]] = (lab, reg)
    allc = dict(countries)
    allc.update(extra_lab)
    eu_done = europe_folk_qids()
    kept, drops = {}, collections.Counter()
    for q, roots in via.items():
        d = info.get(q)
        if not d or not d["sitelinks"]:
            drops["no details"] += 1
            continue
        if q in eu_done:
            drops["already in europe_folk"] += 1
            continue
        label = next(iter(sorted(d["l"])), "") or next(iter(sorted(d["lany"])), "")
        desc = next(iter(sorted(d["d"])), "")
        p31, p279 = d["p31"], d["p279"]
        classes = " | ".join(sorted(p31 | p279))
        text = f"{label} | {desc} | {classes}"
        cq = d["country_q"]
        if cq & europe_q:
            drops["European country"] += 1
            continue
        cset = {allc[c] for c in cq if c in allc}
        if not cset and not cq:
            cset = {allc[c] for c in d["loc_country_q"] if c in allc}
            if d["loc_country_q"] & europe_q:
                drops["European country"] += 1
                continue
        if not cset and not cq:
            hits = {WORLD_DEMONYMS[m] for m in DEMONYM_RE.findall(fold(f"{label} {desc} {' '.join(p279)} "
                                                                         f"{' '.join(d['ethnic'])}"))}
            cset = {("", h) for h in hits}
        if not cset:
            drops["not located outside Europe"] += 1
            continue
        if p31 and all(NOT_TRADITION.match(c) for c in p31) and not p279:
            drops["not a tradition (P31 class)"] += 1
            continue
        only_ich = roots <= {"ICH status", "HCA Red List"}
        if only_ich and not ICH_SIGNAL.search(text):
            drops["ICH, not craft/visual"] += 1
            continue
        if roots <= GENERIC_ROOTS and not VISUAL_SIGNAL.search(text):
            drops["generic craft root, no visual medium"] += 1
            continue
        if BIG_MOVEMENTS.match(label):
            drops["major style/movement"] += 1
            continue
        if any(NON_VISUAL_CLASS.search(c) for c in p31 | p279) and not FOLK_WD.search(label + " " + desc):
            drops["non-visual or ancient class"] += 1
            continue
        if re.search(r"music|dance|song|archaeolog|greek vase|food|dish|cuisine|beverage|pastry|dessert|bread|"
                     r"holiday|celebration|sport|game|fictional|character|deity|saint|martial art|theatre|theater",
                     classes, re.I):
            drops["non-visual or ancient class"] += 1
            continue
        if not p279 and p31 and all(ARTWORK_P31.search(c) for c in p31):
            drops["individual artwork (P31 medium class)"] += 1
            continue
        if not p279 and any(OBJECT_P31.search(c) for c in p31) and not any(TRADITION_P31.search(c) for c in p31):
            drops["individual object/place (P31)"] += 1
            continue
        if q in needs_signal and not (roots - {r[1] for r in ROOTS if r[3]}) and not d["ich"]:
            if not FOLK_WD.search(text) or (MOVEMENT_FINE_ART.search(text) and not re.search(r"folk|icon", text, re.I)):
                drops["broad root without folk signal"] += 1
                continue
        if not label:
            drops["no label"] += 1
            continue
        if p31 == {"motif (visual arts)"} and not p279:
            drops["motif (modifier, not a node)"] += 1
            continue
        if FINE_ART_MOVEMENT.search(label) and not re.search(r"folk|craft|naive|naïve|popular", f"{label} {desc}", re.I):
            drops["fine-art movement"] += 1
            continue
        if INDIVIDUAL_LABEL.search(label) or (not p279 and (INDIVIDUAL_DESC.search(desc) or (p31 and p31 <= INDIVIDUAL_P31))):
            drops["individual object (collection item)"] += 1
            continue
        if ARCHAEO.search(f"{label} | {desc} | {classes}"):
            drops["archaeological / ancient"] += 1
            continue
        if re.search(r"\bfood\b|\bjam\b|\bspread\b|condiment|music|melod|repertoire|dwelling|\byurt\b|calligraph",
                     f"{label} | {desc} | {classes}", re.I):
            drops["non-visual (food, music, dwelling) or calligraphy"] += 1
            continue
        if re.search(r"architectur|building", f"{label} {desc}", re.I) and not VISUAL_SIGNAL.search(label):
            drops["architecture"] += 1
            continue
        years = sorted(d["year"])
        kept[q] = {
            "qid": q, "label": label, "description": desc, "aliases": sorted(d["alias"]),
            "countries": sorted({c for c, _ in cset if c}), "regions": sorted({r for _, r in cset}),
            "peoples": sorted(d["ethnic"]), "sitelinks": max(d["sitelinks"] or {0}),
            "enwiki": next(iter(sorted(d["enwiki"])), ""), "classes": classes, "roots": sorted(roots),
            "ich": sorted(d["ich"]), "heritage": sorted(d["heritage"]), "year": years[0] if years else None,
            "medium": medium_of(label, desc, classes),
        }
    print(f"  kept {len(kept)} non-European candidate nodes; dropped {dict(drops)}", flush=True)
    works, colls = linked_works(list(kept))
    for q, k in kept.items():
        k["wd_works"] = works.get(q, 0)
        k["wd_collections"] = colls.get(q, collections.Counter())
    print(f"  {sum(1 for q in kept if works.get(q))} nodes have linked works ({sum(works.values())} works)", flush=True)
    return kept, info


def ef_root_members(qid, mode):
    if mode == "tree":
        q = f"SELECT DISTINCT ?i WHERE {{ ?i (wdt:P31|wdt:P279)/wdt:P279* wd:{qid} }}"
    elif mode == "subclasses":
        q = f"SELECT DISTINCT ?i WHERE {{ ?i wdt:P279+ wd:{qid} }}"
    else:
        q = f"SELECT DISTINCT ?i WHERE {{ {{ ?i wdt:P31 wd:{qid} }} UNION {{ ?i wdt:P279+ wd:{qid} }} }}"
    return [r["i"] for r in sparql_cached(q, f"root_{qid}") if r["i"].startswith("Q")]


def linked_works(qids):
    works, colls = collections.Counter(), collections.defaultdict(collections.Counter)
    tmpl = """SELECT ?n (COUNT(DISTINCT ?w) AS ?nw) WHERE { VALUES ?n { %s }
        ?w (wdt:P135|wdt:P136|wdt:P2079) ?n . } GROUP BY ?n"""
    tmpl_c = """SELECT ?n ?cl (COUNT(DISTINCT ?w) AS ?nw) WHERE { VALUES ?n { %s }
        ?w (wdt:P135|wdt:P136|wdt:P2079|wdt:P31) ?n . ?w wdt:P195 ?c . ?c rdfs:label ?cl FILTER(lang(?cl)='en') }
        GROUP BY ?n ?cl"""
    for chunk in batched(qids, 150):
        vals = " ".join(f"wd:{q}" for q in chunk)
        for r in sparql_cached(tmpl % vals, "works"):
            works[r["n"]] += int(r["nw"])
        for r in sparql_cached(tmpl_c % vals, "works_coll"):
            colls[r["n"]][r["cl"]] += int(r["nw"])
    return works, colls


def short_label(lab):
    return re.sub(r"\s*\(.*?\)", "", lab).strip()


def link_curated(kept, info):
    """Curated entry index -> QID, by label / alias against kept nodes, then a WDQS label lookup."""
    names = collections.defaultdict(set)
    for i, t in enumerate(TRADITIONS):
        for v in [t["label"], short_label(t["label"])] + [a.strip() for a in t["aliases"].split(";") if a.strip()]:
            if len(v) >= 4:
                names[v].add(i)
    by_label = collections.defaultdict(list)
    for q, k in kept.items():
        for v in [k["label"]] + k["aliases"]:
            by_label[fold(v)].append(q)
    link = {}
    # first pass: the label itself (not aliases) against kept nodes, then aliases
    for primary in (True, False):
        for v, idx in names.items():
            for i in idx:
                t = TRADITIONS[i]
                is_primary = v in (t["label"], short_label(t["label"]))
                if is_primary != primary or i in link:
                    continue
                qs = by_label.get(fold(v))
                if qs:
                    link[i] = max(qs, key=lambda q: kept[q]["sitelinks"])
    missing = {v for v, idx in names.items() if any(i not in link for i in idx)}
    variants = {}
    for v in missing:
        for x in {v, v.lower(), v[:1].lower() + v[1:]}:
            variants.setdefault(x, v)
    vlist = sorted(variants)
    cand = collections.defaultdict(list)
    for chunk in [vlist[k:k + 120] for k in range(0, len(vlist), 120)]:
        vals = " ".join('"%s"@en' % v.replace('"', '').replace("\\", "") for v in chunk)
        q = """SELECT ?l ?i ?sl (GROUP_CONCAT(DISTINCT ?cl; separator='|') AS ?cls) WHERE { VALUES ?l { %s }
            { ?i rdfs:label ?l } UNION { ?i skos:altLabel ?l } ?i wikibase:sitelinks ?sl .
            OPTIONAL { ?i wdt:P31|wdt:P279 ?c . ?c rdfs:label ?cl FILTER(lang(?cl)='en') } } GROUP BY ?l ?i ?sl""" % vals
        for r in sparql_cached(q, "patlabel"):
            cls = [c for c in r.get("cls", "").split("|") if c]
            if LINK_BAD.search(r.get("cls", "")):
                continue
            if cls and all(NOT_TRADITION.match(c) for c in cls):
                continue
            if re.search(r"village|settlement|town|city|human|river|municipal|commune|island|archipelago|railway|ship|"
                         r"station|family name|given name|disambiguation|county|district|region|province|ethnic group|"
                         r"people|language|taxon|species|genus|film|album|song|band|company|business|organization|"
                         r"film|television|video game|mountain|lake|state of|country|deity|fictional",
                         r.get("cls", ""), re.I):
                continue
            for i in names[variants[r["l"]]]:
                is_primary = variants[r["l"]] in (TRADITIONS[i]["label"], short_label(TRADITIONS[i]["label"]))
                cand[i].append((is_primary, int(r["sl"]), r["i"]))
    # sitelinks / ICH / description / classes for candidate items not among the kept nodes
    need = sorted({c[2] for cs in cand.values() for c in cs if c[2] not in kept and not info.get(c[2], {}).get("sitelinks")})
    if need:
        fetch_details(need, info, tags=["lab", "her", "cls"])
    rejected = []
    for i, cs in cand.items():
        if i in link:
            continue
        for is_primary, sl, q in sorted(cs, reverse=True):
            d = info.get(q) or {}
            desc = " ".join(d.get("d", ()))
            cls = " | ".join(sorted(set(d.get("p31", ())) | set(d.get("p279", ()))))
            blob = f"{desc} | {cls}"
            if LINK_BAD.search(blob):
                continue
            if not (is_primary and not desc and not cls) and not LINK_VISUAL.search(blob):
                continue
            link[i] = q
            break
        else:
            rejected.append(TRADITIONS[i]["label"])
    for i in [i for i in link if TRADITIONS[i]["label"] in LINK_BLOCK]:
        del link[i]
    print(f"  label matches rejected as non-visual / places / homonyms: {len(rejected)}", flush=True)
    return link


LINK_BAD = re.compile(r"comune|locality|municipal|neighbo|hamlet|unincorporated|census|mahalle|epistle|bible|\bbook\b|"
                      r"\bmaps?\b|cartograph|\bdish\b|food|dumpling|pasta|edible|dairy|\bdance|unit of|measurement|"
                      r"fictional|instrument|chordophone|beggar|profession|kitchen|utensil|festival|holiday|religio|"
                      r"communit|\bpeople\b|tribe|ethnic group|parroquia|settlement|village|\btown\b|\bcity\b|"
                      r"district|administrative|division|\bhuman\b|collective|calligrapher|illustrator|occupation|"
                      r"\bplant\b|species|taxon|cultivar|surname|given name|sweet potato|fries|deity|\bgod\b|architectural support|"
                      r"\bcolumn\b|door|hardware", re.I)
LINK_VISUAL = re.compile(r"art\b|arts\b|craft|textile|cloth|fabric|garment|costume|dress|weav|embroider|paint|carv|pottery|"
                         r"ceramic|ware\b|doll|toy|mask|puppet|print|jewel|silver|metal|lacquer|dye|batik|ikat|basket|"
                         r"quilt|rug|carpet|kilim|felt|tile|sculpt|figur|technique|ornament|decorat|motif|style|"
                         r"headdress|bag|mat\b|tapa|bark|feather|bead|paper|stencil|appliqu|mural|scroll|weight|"
                         r"coffin|shawl|sari|wrap|skirt|cap\b|hat\b|cross|pendant", re.I)
# curated labels whose Wikidata namesake is a different thing (checked by hand)
LINK_BLOCK = {"Ndop (Cameroon Grassfields resist-dyed cloth)", "American folk portraiture (limners)",
              "Pacific fine mats (ie toga, kiekie)", "Aso oke"}


# ------------------------------------------------------------------ 3. cached museum data

def to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def ftext(*parts):
    return fold(" | ".join(p for p in parts if p))


MET_SKIP_DEPTS = {"Greek and Roman Art", "Egyptian Art", "Ancient Near Eastern Art", "Ancient West Asian Art",
                  "The Cloisters", "Medieval Art", "Robert Lehman Collection", "European Paintings",
                  "European Sculpture and Decorative Arts", "Arms and Armor"}
# regional tables: (file stem, source name); text columns are those present among TEXT_COLS
REGIONAL = [("africa", "africa"), ("africa_oceania_targeted", "africa_oceania_targeted"),
            ("americas_oceania", "americas_oceania"), ("south_southeast_asia", "south_southeast_asia"),
            ("east_asia", "east_asia"), ("himalaya_central_asia", "himalaya_central_asia"), ("islamic", "islamic"),
            ("smithsonian", "smithsonian"), ("world_extra", "world_extra"), ("gap_sweep", "gap_sweep")]
TEXT_COLS = ["title", "title_en", "object_type", "object_subtype", "object_name", "object_type_indexed", "culture",
             "culture_indexed", "culture_label", "culture_group", "culture_keys", "culture_place", "place", "place_recorded",
             "country", "countries", "subregion", "region", "labels_recorded", "labels", "materials",
             "materials_technique", "techniques", "medium", "technique", "school_style", "nmai_culture_area",
             "nmai_culture_subarea", "tradition_recorded", "makers", "dynasty", "period"]
SMITHSONIAN_UNITS = {"NMAI": "Smithsonian National Museum of the American Indian",
                     "NMAfA": "Smithsonian National Museum of African Art",
                     "NMAA": "Smithsonian National Museum of Asian Art", "CHNDM": "Cooper Hewitt, Smithsonian Design Museum",
                     "SAAM": "Smithsonian American Art Museum", "HMSG": "Hirshhorn Museum and Sculpture Garden",
                     "NMAH": "Smithsonian National Museum of American History",
                     "NMNHAnthro": "Smithsonian NMNH Anthropology", "NMNH": "Smithsonian NMNH"}


class Evidence:
    def __init__(self):
        self.agg = {}
        self.rows = collections.defaultdict(list)
        self.read = collections.Counter()
        self.matched = collections.Counter()

    def add(self, i, source, oid, url, title, culture, date, inst, medium=""):
        b = self.agg.get(i)
        if b is None:
            b = self.agg[i] = {"src": collections.Counter(), "inst": collections.Counter(), "years": [], "urls": set(),
                               "samples": []}
        b["src"][source] += 1
        if inst:
            b["inst"][inst] += 1
        if date is not None and -3000 < date < 2100:
            b["years"].append(date)
        if url:
            b["urls"].add(url)
        if len(b["samples"]) < 6 and url:
            b["samples"].append(url)
        lst = self.rows[(i, source)]
        if len(lst) < MAX_EVIDENCE:
            lst.append({"source": source, "object_id": oid, "url": url, "title": (title or "")[:150],
                        "culture": (culture or "")[:80], "medium": (medium or "")[:80], "date": date,
                        "institution": inst})


def harvest_museums():
    ev = Evidence()
    t0 = time.time()
    met = os.path.join(MUSEUMS, "MetObjects.csv")
    if os.path.exists(met):
        with open(met, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if r.get("Department", "") in MET_SKIP_DEPTS:
                    continue
                ev.read["met"] += 1
                cult = r.get("Culture") or ""
                place = " ".join(filter(None, (r.get("Country"), r.get("Region"), r.get("Subregion"), r.get("State"),
                                               r.get("City"), r.get("Locale"))))
                text = ftext(r.get("Title"), r.get("Object Name"), cult, r.get("Period"), place, r.get("Classification"),
                             r.get("Medium"), r.get("Tags"), r.get("Artist Display Bio"), r.get("Artist Nationality"))
                hits = match_text(text)
                if hits:
                    ev.matched["met"] += 1
                    oid = r.get("Object ID")
                    url = r.get("Link Resource") or f"https://www.metmuseum.org/art/collection/search/{oid}"
                    for i in hits:
                        ev.add(i, "met", oid, url, r.get("Title"), cult or place, to_int(r.get("Object Begin Date")),
                               "The Metropolitan Museum of Art", r.get("Medium"))
        print(f"  met: {ev.read['met']} read, {ev.matched['met']} matched ({time.time() - t0:.0f}s)", flush=True)
    aic_dir = os.path.join(MUSEUMS, "aic", "artic-api-data", "json", "artworks")
    if os.path.isdir(aic_dir):
        for fn in glob.glob(os.path.join(aic_dir, "*.json")):
            try:
                with open(fn, encoding="utf-8") as f:
                    d = json.load(f)
            except (OSError, ValueError):
                continue
            ev.read["aic"] += 1
            dept = d.get("department_title") or ""
            if re.search(r"painting and sculpture of europe|ancient", dept, re.I):
                continue
            text = ftext(d.get("title"), d.get("place_of_origin"), d.get("artist_display"), d.get("artwork_type_title"),
                         d.get("medium_display"), " ".join(d.get("term_titles") or []),
                         " ".join(d.get("style_titles") or []), d.get("classification_title"))
            hits = match_text(text)
            if hits:
                ev.matched["aic"] += 1
                for i in hits:
                    ev.add(i, "aic", d.get("id"), f"https://www.artic.edu/artworks/{d.get('id')}", d.get("title"),
                           d.get("place_of_origin"), to_int(d.get("date_start")), "Art Institute of Chicago",
                           d.get("medium_display"))
        print(f"  aic: {ev.read['aic']} read, {ev.matched['aic']} matched ({time.time() - t0:.0f}s)", flush=True)
    for stem, source in REGIONAL:
        path = os.path.join(OUT_DIR, f"{stem}_objects.csv")
        if not os.path.exists(path):
            print(f"  {source}: missing {path}", flush=True)
            continue
        with open(path, encoding="utf-8", newline="") as f:
            rd = csv.DictReader(f)
            cols = [c for c in TEXT_COLS if c in rd.fieldnames]
            for r in rd:
                ev.read[source] += 1
                text = ftext(*(r.get(c) for c in cols))
                hits = match_text(text)
                if not hits:
                    continue
                ev.matched[source] += 1
                inst = r.get("institution") or r.get("holder") or ""
                if source == "smithsonian":
                    inst = SMITHSONIAN_UNITS.get(r.get("unit", ""), "Smithsonian " + r.get("unit", ""))
                url = r.get("url") or r.get("record_link") or ""
                oid = r.get("id") or r.get("record_id") or ""
                date = to_int(r.get("date_begin") or r.get("begin_year"))
                cult = r.get("culture") or r.get("culture_label") or r.get("place") or r.get("country") or ""
                med = r.get("materials") or r.get("medium") or r.get("object_type") or ""
                for i in hits:
                    ev.add(i, source, oid, url, r.get("title") or r.get("title_en"), cult, date, inst, med)
        print(f"  {source}: {ev.read[source]} read, {ev.matched[source]} matched ({time.time() - t0:.0f}s)", flush=True)
    return ev


# ------------------------------------------------------------------ 4. node gain

KNOWN_FILES = (["unattributed_cultures.csv"] +
               [os.path.join("regional", os.path.basename(p)) for p in
                sorted(glob.glob(os.path.join(OUT_DIR, "*traditions*.csv")) +
                       glob.glob(os.path.join(OUT_DIR, "*_cultures.csv")) +
                       glob.glob(os.path.join(OUT_DIR, "*_schools.csv")))
                if not os.path.basename(p).startswith("world_folk")])
NAME_COLS = ["label", "key", "tradition", "name", "qid_label", "node_label", "top_kilns_workshops"]
CULTURE_COLS = ["culture", "key", "culture_group", "top_cultures", "raw_labels", "label", "parent"]


def load_known():
    """Folded name strings and culture strings of all nodes gathered so far, with their file."""
    names, cultures = [], []
    for rel in KNOWN_FILES:
        path = os.path.join(INTERIM, rel)
        if not os.path.exists(path):
            continue
        tag = os.path.basename(rel).replace(".csv", "")
        with open(path, encoding="utf-8", newline="") as f:
            rd = csv.DictReader(f)
            ncols = [c for c in NAME_COLS if c in rd.fieldnames]
            ccols = [c for c in CULTURE_COLS if c in rd.fieldnames]
            for r in rd:
                for c in ncols:
                    v = r.get(c) or ""
                    if v:
                        names.append((fold(v), tag, v[:80]))
                for c in ccols:
                    for part in re.split(r"[;|/]|\(\d+\)", r.get(c) or ""):
                        p = fold(part)
                        if len(p) >= 3:
                            cultures.append((p, tag, part.strip()[:60]))
    return names, cultures


class KnownIndex:
    def __init__(self, known):
        names, cultures = known
        self.names = names
        self.name_blob = "\n".join(n for n, _, _ in names)
        self.cult_blob = "\n".join(c for c, _, _ in cultures)
        self.cultures = cultures
        self.name_starts = self._starts(names)
        self.cult_starts = self._starts(cultures)

    @staticmethod
    def _starts(rows):
        out, pos = [], 0
        for n, _, _ in rows:
            out.append(pos)
            pos += len(n) + 1
        return out

    def _find(self, phrase, blob, rows, starts):
        import bisect
        rx = re.compile(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])")
        hits = []
        for m in rx.finditer(blob):
            k = bisect.bisect_right(starts, m.start()) - 1
            hits.append(rows[k])
            if len(hits) >= 50:
                break
        return hits

    def name_hit(self, phrase):
        return self._find(phrase, self.name_blob, self.names, self.name_starts)

    def culture_hit(self, phrase):
        return self._find(phrase, self.cult_blob, self.cultures, self.cult_starts)


GENERIC_NAME = re.compile(r"^(painting|pottery|ceramics|weaving|embroidery|textiles?|lace|carving|beadwork|masks?|"
                          r"tapa|batik|ikat|kilim|quilts?|baskets?|basketry|toys?|santos|retablos?|sarape|serape|"
                          r"weaving|feather ?work|pua|ade|kete|par|abr|atlas|tais|bagh|manta|torito|tapis|bulto|"
                          r"masi|kapa|epa|amo|fala|ema|daruma|boro|kene|sadu|oya|ebru)$")


def known_status(names, cell, idx):
    """-> (status, match). names: label / short label / aliases."""
    for n in names:
        f = fold(n)
        if len(f) < 4 or GENERIC_NAME.match(f):
            continue
        hits = [h for h in idx.name_hit(f) if not h[1].startswith("world_folk")]
        if hits:
            named = [h for h in hits if h[0] != f]   # the phrase inside a longer node name
            bare = [h for h in hits if h[0] == f]    # a node whose whole name is the phrase
            if cell and not named:
                # a bare culture key equal to a sub-people alias (e.g. "shoowa"): the cell exists, not the name
                return "alias-of-existing-cell", f"{f} ({bare[0][1]})"
            h = (named or bare)[0]
            return "known", f"{h[1]}: {h[2]}"
    if cell:
        hits = idx.culture_hit(fold(cell))
        if hits:
            files = collections.Counter(h[1] for h in hits)
            return "alias-of-existing-cell", f"{cell} x medium ({', '.join(f for f, _ in files.most_common(3))})"
    return "new", ""


# ------------------------------------------------------------------ outputs

SOURCES = ["met", "aic"] + [s for _, s in REGIONAL]


def build_outputs(wd, link, info, ev):
    idx = KnownIndex(load_known())
    nodes = {}
    q_to_key = {}

    def new_node(key, **kw):
        n = {"node_key": key, "kind": "", "label": "", "aliases": "", "qid": "", "country": "", "people": "", "region": "",
             "medium": "", "ich_designation": "", "heritage_designation": "", "wd_sitelinks": "", "wd_enwiki": "",
             "wd_description": "", "wd_classes": "", "wd_linked_works": 0, "match_rule": "", "_trad": [],
             "institutions": collections.Counter(), "years": [], "urls": set(), "samples": [],
             "src": collections.Counter(), "notes": ""}
        n.update(kw)
        nodes[key] = n
        return n

    for q, k in (wd or {}).items():
        key = f"wd:{q}"
        q_to_key[q] = key
        n = new_node(key, kind="wikidata", label=k["label"], aliases="; ".join(k["aliases"][:8]), qid=q,
                     country="; ".join(k["countries"]), people="; ".join(k["peoples"]), region="; ".join(k["regions"]),
                     medium=k["medium"], ich_designation="; ".join(k["ich"]), heritage_designation="; ".join(k["heritage"]),
                     wd_sitelinks=k["sitelinks"], wd_enwiki=k["enwiki"], wd_description=k["description"][:200],
                     wd_classes=k["classes"][:300], wd_linked_works=k["wd_works"])
        n["institutions"].update(k["wd_collections"])
        if k["year"] is not None:
            n["years"].append(k["year"])
    claimed = set()
    for i, t in enumerate(TRADITIONS):
        q = link.get(i, "")
        if q in claimed:   # a second curated entry linked to the same item keeps its own node
            link[i] = q = ""
            t_note = f"Wikidata label match shared with another entry"
        else:
            t_note = ""
        if q:
            claimed.add(q)
        key = q_to_key.get(q) or f"curated:{slug(t['label'])}"
        if key in nodes:
            n = nodes[key]
            if n["kind"] == "wikidata":
                n["notes"] = (n["notes"] + "; " if n["notes"] else "") + f"curated '{t['label']}'"
                n["kind"] = "wikidata+curated"
                n["label"] = t["label"]   # curated (English usage) label beats the Wikidata label
                n["aliases"] = "; ".join(filter(None, [t["aliases"], n["aliases"]]))
                n["medium"], n["region"] = t["medium"], t["region"]
                n["country"], n["people"] = t["country"], t["people"] or n["people"]
        else:
            d = info.get(q) if q else None
            n = new_node(key, kind="curated", label=t["label"], aliases=t["aliases"], qid=q, country=t["country"],
                         people=t["people"], region=t["region"], medium=t["medium"])
            if d:
                n.update(ich_designation="; ".join(sorted(d.get("ich", ()))),
                         heritage_designation="; ".join(sorted(d.get("heritage", ()))),
                         wd_sitelinks=max(d.get("sitelinks") or {0}), wd_enwiki=next(iter(sorted(d.get("enwiki", ()))), ""),
                         wd_description=next(iter(sorted(d.get("d", ()))), "")[:200],
                         wd_classes=" | ".join(sorted(d.get("p31", set()) | d.get("p279", set())))[:300])
        n["_trad"].append(i)
        if t_note:
            n["notes"] = t_note
        rule = f"rx /{t['rx']}/" if t["rx"] else ""
        if t["weak"]:
            rule += f"{'; ' if rule else ''}weak /{t['weak']}/ + ctx /{t['ctx']}/"
        n["match_rule"] = (n["match_rule"] + " || " if n["match_rule"] else "") + rule
        n["_cell"] = t["cell"]
    if ev:
        for i, b in ev.agg.items():
            q = link.get(i, "")
            n = nodes[q_to_key.get(q) or f"curated:{slug(TRADITIONS[i]['label'])}"]
            n["src"].update(b["src"])
            n["institutions"].update(b["inst"])
            n["years"].extend(b["years"])
            n["urls"] |= b["urls"]
            n["samples"].extend(b["samples"])
    rows = []
    for n in nodes.values():
        names = [n["label"], short_label(n["label"])] + [a.strip() for a in n["aliases"].split(";") if a.strip()]
        status, match = known_status(names, n.get("_cell", ""), idx)
        ys = sorted(n["years"])
        row = dict(n)
        row.update(
            total_objects_distinct=len(n["urls"]), total_object_matches=sum(n["src"].values()),
            n_sources=len(n["src"]), **{f"objects_{s}": n["src"].get(s, 0) for s in SOURCES},
            date_begin_min=ys[0] if ys else "", date_begin_max=ys[-1] if ys else "", period=period_of(ys),
            n_institutions=len(n["institutions"]), top_institutions=topfmt(n["institutions"].most_common(8), 8),
            sample_object_urls=" ".join(list(dict.fromkeys(n["samples"]))[:6]),
            status=status, known_match=match if status == "known" else "",
            alias_of=match if status == "alias-of-existing-cell" else "", cell=n.get("_cell", ""))
        rows.append(row)
    order = {r: k for k, r in enumerate(REGIONS)}
    rows.sort(key=lambda r: (order.get(r["region"].split("; ")[0], 99), r["kind"] == "wikidata",
                             -r["total_objects_distinct"], -(int(r["wd_sitelinks"] or 0))))
    fields = (["node_key", "kind", "label", "aliases", "qid", "country", "people", "region", "medium", "ich_designation",
               "heritage_designation", "wd_sitelinks", "status", "known_match", "alias_of", "cell",
               "total_objects_distinct", "total_object_matches", "n_sources"] + [f"objects_{s}" for s in SOURCES] +
              ["wd_linked_works", "n_institutions", "top_institutions", "date_begin_min", "date_begin_max", "period",
               "sample_object_urls", "wd_enwiki", "wd_description", "wd_classes", "match_rule", "notes"])
    os.makedirs(OUT_DIR, exist_ok=True)
    write(os.path.join(OUT_DIR, "world_folk_traditions.csv"), rows, fields)
    evrows = []
    if ev:
        for (i, source), items in ev.rows.items():
            q = link.get(i, "")
            nk = q_to_key.get(q) or f"curated:{slug(TRADITIONS[i]['label'])}"
            for it in items:
                evrows.append(dict(it, node_key=nk, node_label=TRADITIONS[i]["label"]))
    write(os.path.join(OUT_DIR, "world_folk_objects.csv"), evrows,
          ["node_key", "node_label", "source", "object_id", "url", "title", "culture", "medium", "date", "institution"])
    return rows, evrows


TEST_LIST = ["Pattachitra", "Kalamkari", "Phad painting", "Pichwai", "Bidriware", "Dhokra", "Sanjhi",
             "Bogolan (mud cloth)", "Adire", "Aso oke", "Zulu beadwork", "Maasai beadwork", "Tingatinga painting",
             "Alebrijes and Oaxacan wood carving", "Papel picado", "Maya huipil and backstrap weaving", "Arpilleras",
             "Taquile textiles", "Quinchamali pottery", "Palestinian embroidery (tatreez)", "Khamak embroidery (Kandahar)",
             "Tivaevae (Cook Islands quilts)", "Lalava (Pacific lashing)", "Bilum (PNG string bags)", "Tongan ngatu (tapa)",
             "Pueblo pottery", "Navajo weaving", "Ledger art", "Songket"]


def report(rows, evrows, ev):
    print(f"\nWrote {len(rows)} nodes ({dict(collections.Counter(r['kind'] for r in rows))}), {len(evrows)} evidence rows")
    if ev:
        print("museum rows read:", dict(ev.read))
        print("museum rows matched:", dict(ev.matched))
    print("\nPer region: nodes / with objects / new / alias-of-existing-cell / known")
    per = collections.defaultdict(collections.Counter)
    for r in rows:
        reg = r["region"].split("; ")[0] or "unknown"
        c = per[reg]
        c["nodes"] += 1
        c["curated"] += r["kind"] != "wikidata"
        c["with_objects"] += r["total_objects_distinct"] > 0
        c[r["status"]] += 1
    for reg in REGIONS + sorted(set(per) - set(REGIONS)):
        c = per.get(reg)
        if c:
            print(f"  {reg:40s} {c['nodes']:4d} (curated {c['curated']}) objs {c['with_objects']:4d} new {c['new']:4d} "
                  f"alias {c['alias-of-existing-cell']:3d} known {c['known']:3d}")
    by_label = {r["label"]: r for r in rows}
    print("\nTest list:")
    for lab in TEST_LIST:
        r = by_label.get(lab)
        if not r:
            print(f"  {lab}: NOT A NODE")
            continue
        print(f"  {lab}: qid {r['qid'] or '-'}; objects {r['total_objects_distinct']} "
              f"(met {r['objects_met']}, aic {r['objects_aic']}, other {r['total_object_matches'] - r['objects_met'] - r['objects_aic']}); "
              f"{r['status']} {r['known_match'] or r['alias_of']}")
    zero = [r["label"] for r in rows if r["kind"] != "wikidata" and not r["total_objects_distinct"]]
    print(f"\nCurated nodes without museum evidence ({len(zero)}): {'; '.join(zero)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skip", default="", help="comma list of wikidata,museums")
    ap.add_argument("--delay", type=float, default=1.0)
    args = ap.parse_args()
    ef.DELAY[0] = max(1.0, args.delay)
    skip = set(filter(None, args.skip.split(",")))
    print(f"Curated traditions: {len(TRADITIONS)}", flush=True)
    if "wikidata" in skip:
        wd, info, link = {}, {}, {}
    else:
        wd, info = harvest_wikidata()
        link = link_curated(wd, info)
        print(f"Curated entries linked to Wikidata: {len(link)} of {len(TRADITIONS)} "
              f"({sum(1 for q in link.values() if q in wd)} to kept nodes)", flush=True)
    ev = harvest_museums() if "museums" not in skip else None
    rows, evrows = build_outputs(wd, link, info, ev)
    report(rows, evrows, ev)


if __name__ == "__main__":
    main()
