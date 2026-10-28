"""Candidate exemplars for non-Western architectural styles without P149 (visual-art-plan.md §2.1b, §2.2).

Wikidata's architectural-style tags (P149) are dense for European styles and
nearly empty elsewhere (Khmer 3 buildings, Maya 6, Inca 2, Hoysala 1; no usable
Nagara or Asuka/Nara temple style). This pass ignores P149 when choosing and
assigns a *proposed* style to each building from explicit rules instead:

1. Building class x country. For each verified class QID (Hindu temple, stupa,
   wat, candi, mosque, madrasa, archaeological site, Shinto shrine, ...; see
   CLASSES, each checked against its English label before any fetch) and each
   country in its scope, list the instances (P31/P279*) that have >= --min-sitelinks
   sitelinks, a heritage designation (P1435), a UNESCO id (P757) or an
   inception (P571).
2. UNESCO components. World Heritage sites (P757) in countries outside Europe,
   plus every item that is part of (P361, one or two levels) such a site.
3. Details for every candidate: classes matched, countries, admin ancestors
   (P131+, used as "region"), inception (P571, else P580), heritage (P1435),
   part of (P361), culture (P2596), founder (P112/P88), coordinates and any P149.
4. Rules (RULES below, first match wins): country + class + region/coordinates
   + date range (+ culture) -> proposed style. Each row records the rule id; the
   rule table is printed for review and written to
   data/interim/architecture_nonwestern_rules.csv (proposed seeds input; this
   script never writes into seeds/).
5. P149 check: existing style tags are grouped into families by label (FAMILY_RE);
   a row is flagged when its existing tags name a regional family that the
   proposed style's family does not accept (e.g. Angkor Wat: Dravidian vs Khmer).

Caveat: P571 on temples is often the founding date, not the date of the
standing fabric (Japanese temples founded in the Asuka period and rebuilt in
Edo, Meenakshi dated 1200). Dated rules inherit that bias.

Every SPARQL result is cached under data/raw/wikidata/architecture/ (keyed by a
hash of the query; shared with build_styles.py), at most --workers (2)
concurrent queries; a failed query is reported and skipped, so re-running
resumes from the cache.

Outputs:
  data/interim/architecture_nonwestern_exemplars.csv
  data/interim/architecture_nonwestern_styles.csv
  data/interim/architecture_nonwestern_rules.csv

Usage: python3 pipelines/architecture/nonwestern_exemplars.py [--workers 2] [--min-sitelinks 1]
"""
import argparse
import collections
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "visual_art"))
from wikidata import sparql, year_of  # noqa: E402

RAW = os.path.join(ROOT, "data", "raw", "wikidata", "architecture")
POOL_RAW = os.path.join(ROOT, "data", "raw", "wikidata", "pool")
OUT_DIR = os.path.join(ROOT, "data", "interim")
STYLES_CSV = os.path.join(OUT_DIR, "architecture_styles.csv")
CHUNK = 200
WORKERS = 2
FAILED = []

# ---------------------------------------------------------------- verified QIDs
# Class key -> (QID, English label it must carry). Verified 2026-10-28 by label
# lookup (the QID with the most instances among items carrying that label).
CLASSES = {
    "hindu_temple": ("Q842402", "Hindu temple"),
    "jain_temple": ("Q2613100", "Jain temple"),
    "buddhist_temple": ("Q5393308", "Buddhist temple"),
    "stupa": ("Q180987", "stupa"),
    "pagoda": ("Q199451", "pagoda"),
    "chinese_pagoda": ("Q5100853", "Chinese pagoda"),
    "wat": ("Q427287", "wat"),
    "candi": ("Q2736554", "Candi"),
    "khmer_temple": ("Q13016741", "Khmer temple"),
    "cave_temple": ("Q21550442", "cave temple"),
    "rock_cut": ("Q11587139", "rock-cut architecture"),
    "tibetan_monastery": ("Q54074585", "Tibetan Buddhist monastery"),
    "korean_temple": ("Q1566035", "Korean Buddhist temple"),
    "chinese_temple": ("Q2680845", "Chinese temple"),
    "taoist_temple": ("Q1151612", "Taoist temple"),
    "shinto_shrine": ("Q845945", "Shinto shrine"),
    "japanese_castle": ("Q92026", "Japanese castle"),
    "kofun": ("Q1141225", "kofun"),
    "mosque": ("Q32815", "mosque"),
    "madrasa": ("Q132834", "madrasa"),
    "caravanserai": ("Q186347", "caravanserai"),
    "mausoleum": ("Q162875", "mausoleum"),
    "tomb": ("Q381885", "tomb"),
    "imamzadeh": ("Q136868", "imamzadeh"),
    "dargah": ("Q2639699", "dargah"),
    "palace": ("Q16560", "palace"),
    "fort": ("Q1785071", "fort"),
    "fortress": ("Q57831", "fortress"),
    "castle": ("Q23413", "castle"),
    "ksar": ("Q89691", "ksar"),
    "stepwell": ("Q1473950", "stepwell"),
    "meso_pyramid": ("Q2270185", "Mesoamerican pyramid"),
    "pyramid": ("Q12516", "pyramid"),
    "archaeological_site": ("Q839954", "archaeological site"),
    "ruins": ("Q109607", "ruins"),
    "ancient_city": ("Q15661340", "ancient city"),
    "cliff_dwelling": ("Q899959", "cliff dwelling"),
    "pueblo": ("Q251749", "pueblo"),
    "rock_cut_church": ("Q1404292", "rock-cut church"),
    "monolithic_church": ("Q1931855", "monolithic church"),
    "church": ("Q16970", "church building"),
    "monastery": ("Q44613", "monastery"),
    "dzong": ("Q386952", "dzong"),
    "temple": ("Q44539", "temple"),  # generic: class matching only, never listed
}

COUNTRIES = {
    "Q668": "India", "Q843": "Pakistan", "Q902": "Bangladesh", "Q837": "Nepal", "Q854": "Sri Lanka",
    "Q917": "Bhutan", "Q836": "Myanmar", "Q869": "Thailand", "Q424": "Cambodia", "Q819": "Laos",
    "Q881": "Vietnam", "Q252": "Indonesia", "Q833": "Malaysia", "Q148": "People's Republic of China",
    "Q17": "Japan", "Q884": "South Korea", "Q423": "North Korea", "Q865": "Taiwan", "Q711": "Mongolia",
    "Q794": "Iran", "Q796": "Iraq", "Q858": "Syria", "Q79": "Egypt", "Q43": "Turkey", "Q265": "Uzbekistan",
    "Q889": "Afghanistan", "Q874": "Turkmenistan", "Q863": "Tajikistan", "Q232": "Kazakhstan",
    "Q227": "Azerbaijan", "Q1028": "Morocco", "Q948": "Tunisia", "Q262": "Algeria", "Q1016": "Libya",
    "Q805": "Yemen", "Q842": "Oman", "Q912": "Mali", "Q1032": "Niger", "Q965": "Burkina Faso",
    "Q1041": "Senegal", "Q1025": "Mauritania", "Q1006": "Guinea", "Q1008": "Ivory Coast", "Q117": "Ghana",
    "Q1033": "Nigeria", "Q657": "Chad", "Q962": "Benin", "Q114": "Kenya", "Q924": "Tanzania",
    "Q115": "Ethiopia", "Q986": "Eritrea", "Q1049": "Sudan", "Q954": "Zimbabwe", "Q1029": "Mozambique",
    "Q258": "South Africa", "Q963": "Botswana", "Q96": "Mexico", "Q774": "Guatemala", "Q242": "Belize",
    "Q783": "Honduras", "Q792": "El Salvador", "Q419": "Peru", "Q750": "Bolivia", "Q736": "Ecuador",
    "Q298": "Chile", "Q739": "Colombia", "Q414": "Argentina", "Q30": "United States",
    "Q702": "Federated States of Micronesia", "Q678": "Tonga",
}
C = {v: k for k, v in COUNTRIES.items()}


def cs(*names):
    return {C[n] for n in names}


S_ASIA = cs("India", "Pakistan", "Bangladesh", "Nepal", "Sri Lanka", "Bhutan")
SE_ASIA = cs("Myanmar", "Thailand", "Cambodia", "Laos", "Vietnam", "Indonesia", "Malaysia")
E_ASIA = cs("People's Republic of China", "Japan", "South Korea", "North Korea", "Taiwan")
ISLAMIC = cs("Iran", "Iraq", "Syria", "Egypt", "Turkey", "Uzbekistan", "Afghanistan", "Turkmenistan", "Tajikistan",
             "Kazakhstan", "Azerbaijan", "Morocco", "Tunisia", "Algeria", "Libya", "Yemen", "Oman")
SAHEL = cs("Mali", "Niger", "Burkina Faso", "Senegal", "Mauritania", "Guinea", "Ivory Coast", "Ghana", "Nigeria", "Chad")
SWAHILI = cs("Kenya", "Tanzania")
ETH = cs("Ethiopia", "Eritrea")
MESO = cs("Mexico", "Guatemala", "Belize", "Honduras", "El Salvador")
ANDES = cs("Peru", "Bolivia", "Ecuador", "Chile", "Colombia", "Argentina")
S_AFR = cs("Zimbabwe", "Mozambique", "South Africa", "Botswana")
OCEANIA = cs("Federated States of Micronesia", "Tonga")

# Which countries each class is listed in (step 1).
SCOPE = {
    "hindu_temple": S_ASIA | SE_ASIA,
    "jain_temple": cs("India"),
    "buddhist_temple": S_ASIA | SE_ASIA | E_ASIA | cs("Mongolia"),
    "stupa": S_ASIA | SE_ASIA | E_ASIA | cs("Afghanistan"),
    "pagoda": S_ASIA | SE_ASIA | E_ASIA,
    "chinese_pagoda": cs("People's Republic of China", "Taiwan"),
    "wat": cs("Thailand", "Cambodia", "Laos", "Myanmar"),
    "candi": cs("Indonesia"),
    "khmer_temple": cs("Cambodia", "Thailand", "Laos", "Vietnam"),
    "cave_temple": cs("India", "Sri Lanka", "People's Republic of China"),
    "rock_cut": cs("India", "Sri Lanka", "People's Republic of China"),
    "tibetan_monastery": cs("People's Republic of China", "India", "Nepal", "Bhutan", "Mongolia"),
    "korean_temple": cs("South Korea", "North Korea"),
    "chinese_temple": cs("People's Republic of China", "Taiwan"),
    "taoist_temple": cs("People's Republic of China", "Taiwan"),
    "shinto_shrine": cs("Japan"),
    "japanese_castle": cs("Japan"),
    "kofun": cs("Japan"),
    "mosque": ISLAMIC | S_ASIA | SAHEL | SWAHILI | ETH | cs("People's Republic of China", "Indonesia", "Malaysia"),
    "madrasa": ISLAMIC | S_ASIA | SAHEL,
    "caravanserai": ISLAMIC | S_ASIA,
    "mausoleum": ISLAMIC | S_ASIA | SWAHILI,
    "tomb": ISLAMIC | S_ASIA | SWAHILI,
    "imamzadeh": cs("Iran", "Iraq"),
    "dargah": S_ASIA,
    "palace": S_ASIA | ISLAMIC | SE_ASIA | E_ASIA | ETH | cs("Benin", "Nigeria"),
    "fort": S_ASIA | ISLAMIC,
    "fortress": S_ASIA | ISLAMIC,
    "castle": ETH,
    "ksar": cs("Morocco", "Algeria", "Tunisia", "Mauritania"),
    "stepwell": cs("India", "Pakistan"),
    "meso_pyramid": MESO,
    "pyramid": MESO | cs("Sudan", "Peru"),
    "archaeological_site": MESO | ANDES | S_AFR | ETH | SWAHILI | OCEANIA | cs(
        "Cambodia", "Thailand", "Laos", "Vietnam", "Myanmar", "Indonesia", "Sri Lanka", "India", "Pakistan",
        "Afghanistan", "Sudan", "Mali", "United States"),
    "ruins": MESO | ANDES | S_AFR | ETH | SWAHILI | OCEANIA | cs(
        "Cambodia", "Thailand", "Laos", "Vietnam", "Myanmar", "Indonesia", "Sri Lanka", "India", "Sudan", "Mali"),
    "ancient_city": MESO | ANDES | S_AFR | ETH | SWAHILI | cs("Cambodia", "Myanmar", "Sri Lanka", "Sudan", "Mali"),
    "cliff_dwelling": cs("United States", "Mexico"),
    "pueblo": cs("United States"),
    "rock_cut_church": ETH,
    "monolithic_church": ETH,
    "church": ETH,
    "monastery": ETH,
    "dzong": cs("Bhutan"),
}

# ---------------------------------------------------------------- rule table
TEMPLE = {"hindu_temple", "buddhist_temple", "jain_temple", "temple", "khmer_temple", "wat", "candi", "stupa",
          "pagoda", "cave_temple", "rock_cut", "pyramid"}
SITE = {"archaeological_site", "ruins", "ancient_city"}
MESO_SITE = SITE | {"meso_pyramid", "pyramid", "temple"}
ISL = {"mosque", "madrasa", "caravanserai", "mausoleum", "tomb", "imamzadeh", "dargah", "palace", "fort", "fortress"}
EA_BUDDHIST = {"buddhist_temple", "pagoda", "chinese_pagoda", "stupa", "korean_temple"}
NORTH_INDIA = r"uttar pradesh|madhya pradesh|bihar|jharkhand|haryana|delhi|punjab|chhattisgarh"

MAYA_COUNTRY = cs("Guatemala", "Belize")
MAYA_MX = r"yucat|campeche|quintana roo|chiapas|tabasco"


def R(rid, style, family, **cond):
    """One rule: all given conditions must hold (see match())."""
    return dict(id=rid, style=style, family=family, **cond)


# Conditions: classes (any), countries (any), place (regex over admin ancestors
# + part-of labels), name (regex over the item's label), years (lo, hi inclusive, needs a date), undated (needs no
# date), culture (regex over P2596 labels), founder (regex over P112/P88),
# bbox (lat_lo, lat_hi, lon_lo, lon_hi), maya (in the Maya area: culture Maya,
# Guatemala/Belize, the Mexican Maya states, or western Honduras/El Salvador),
# notable (heritage, UNESCO or >= 3 sitelinks), before (regex over existing style
# labels in architecture_styles.csv, for the before/after count).
RULES = [
    # --- explicit culture (P2596) first
    R("C01", "Inca", "andean", culture=r"\binca", before=r"^inca"),
    R("C02", "Aztec", "mesoamerican", culture=r"aztec|mexica", before=r"aztec"),
    R("C03", "Zapotec / Mixtec (Oaxaca)", "mesoamerican", culture=r"zapotec|mixtec"),
    R("C04", "Teotihuacan", "mesoamerican", culture=r"teotihuac"),
    R("C05", "Toltec", "mesoamerican", culture=r"toltec"),
    R("C06", "Olmec", "mesoamerican", culture=r"olmec"),
    R("C07", "Classic Veracruz / Totonac", "mesoamerican", culture=r"totonac|veracruz|huastec"),
    R("C08", "Moche", "andean", culture=r"moche|mochica"),
    R("C09", "Chimú", "andean", culture=r"chim[uú]"),
    R("C10", "Wari", "andean", culture=r"\bwari|huari"),
    R("C11", "Chavín", "andean", culture=r"chav[ií]n"),
    R("C12", "Nazca / Paracas", "andean", culture=r"nazca|nasca|paracas"),
    R("C13", "Tiwanaku", "andean", culture=r"tiwanaku|tiahuanaco"),
    R("C14", "Chachapoya", "andean", culture=r"chachapoya"),
    R("C15", "Caral / Norte Chico", "andean", culture=r"caral|norte chico"),
    R("C16", "Andean regional (Recuay, Lima, Sicán, ...)", "andean", culture=r"recuay|lima culture|sic[aá]n|lambayeque|yarowilca|cajamarca"),
    R("C17", "Ancestral Puebloan", "puebloan", culture=r"puebloan|anasazi", before=r"^pueblo architecture"),
    R("C18", "Mississippian / mound builders", "eastern_woodlands", culture=r"mississippian|hopewell|adena|poverty point"),
    R("C19", "Harappan (Indus)", "harappan", culture=r"indus|harappa"),
    R("C20", "Cham", "cham", culture=r"champa|\bcham\b"),
    R("C21", "Aksumite", "ethiopian", culture=r"aksum|axum"),
    R("C22", "Kushite (Napatan / Meroitic)", "kushite", culture=r"kush|mero[eë]|napata"),
    R("C23", "Zimbabwe culture (dry-stone)", "zimbabwe", culture=r"zimbabwe|mapungubwe|torwa|rozvi"),

    # --- Maya (area + coordinates for sub-region)
    R("M01", "Maya — Puuc", "maya", maya=True, classes=MESO_SITE, bbox=(19.95, 20.6, -90.2, -89.3), before=r"puuc|maya arch"),
    R("M02", "Maya — Chenes", "maya", maya=True, classes=MESO_SITE, bbox=(19.2, 19.95, -90.15, -89.3), before=r"chenes"),
    R("M03", "Maya — Río Bec", "maya", maya=True, classes=MESO_SITE, bbox=(17.9, 18.85, -89.7, -88.9), before=r"r[ií]o bec"),
    R("M04", "Maya — northern lowlands", "maya", maya=True, classes=MESO_SITE, bbox=(19.0, 22.0, -91.5, -86.5)),
    R("M05", "Maya — southern lowlands (Petén / Usumacinta / Belize)", "maya", maya=True, classes=MESO_SITE, bbox=(15.5, 19.0, -94.5, -87.5)),
    R("M06", "Maya — highlands and southeast (Guatemala highlands, Copán)", "maya", maya=True, classes=MESO_SITE, bbox=(13.0, 15.5, -92.5, -87.5)),
    R("M07", "Maya (unlocated)", "maya", maya=True, classes=MESO_SITE, culture=r"maya"),
    R("M08", "Maya (unlocated)", "maya", maya=True, classes=MESO_SITE, countries=MAYA_COUNTRY),

    # --- other Mesoamerica
    R("X01", "Teotihuacan", "mesoamerican", countries=cs("Mexico"), classes=MESO_SITE, place=r"teotihuac"),
    R("X01b", "Teotihuacan", "mesoamerican", countries=cs("Mexico"), classes=MESO_SITE, name=r"teotihuac|pyramid of the (sun|moon)|feathered serpent|ciudadela"),
    R("X02", "Aztec", "mesoamerican", countries=cs("Mexico"), classes=MESO_SITE, years=(1300, 1521),
      place=r"mexico city|state of mexico|méxico|hidalgo|tlaxcala|puebla|morelos"),
    R("X03", "Zapotec / Mixtec (Oaxaca)", "mesoamerican", countries=cs("Mexico"), classes=MESO_SITE, place=r"oaxaca"),
    R("X04", "Classic Veracruz / Totonac", "mesoamerican", countries=cs("Mexico"), classes=MESO_SITE, place=r"veracruz"),
    R("X05", "Mesoamerican (central / western Mexico, unassigned)", "mesoamerican", countries=cs("Mexico"), classes=MESO_SITE, notable=True),

    # --- Andes
    R("A01", "Inca", "andean", countries=ANDES, classes=SITE | {"pyramid", "fortress", "palace", "temple"}, years=(1400, 1572), before=r"^inca"),
    R("A02", "Inca", "andean", countries=ANDES, place=r"inca road|qhapaq|saqsaywaman|sacsayhuam|sacred valley|machu picchu|ollantaytambo|cusco|cuzco", classes=SITE | {"fortress", "palace", "temple"}, undated=True),
    R("A03", "Andean (culture unassigned)", "andean", countries=cs("Peru", "Bolivia", "Ecuador"), classes=SITE | {"pyramid"}, notable=True),

    # --- North America, Africa, Oceania
    R("N01", "Ancestral Puebloan", "puebloan", countries=cs("United States", "Mexico"), classes={"cliff_dwelling", "pueblo"} | SITE,
      place=r"arizona|new mexico|colorado|utah|chihuahua"),
    R("F01", "Ethiopian rock-hewn churches", "ethiopian", classes={"rock_cut_church", "monolithic_church"}),
    R("F02", "Ethiopian rock-hewn churches", "ethiopian", countries=ETH, classes={"church", "monastery", "rock_cut"} | SITE,
      place=r"lalibela|tigray|gheralta|wukro|lasta|north wollo"),
    R("F03", "Gondarine (Ethiopia)", "ethiopian", countries=ETH, classes={"castle", "palace", "fortress", "church"} | SITE, place=r"gondar|fasil"),
    R("F04", "Aksumite", "ethiopian", countries=ETH, classes=SITE | {"church", "tomb"}, place=r"aksum|axum|yeha"),
    R("F05", "Ethiopian church (other)", "ethiopian", countries=ETH, classes={"church", "monastery"}, years=(300, 1900)),
    R("F10", "Zimbabwe culture (dry-stone)", "zimbabwe", countries=cs("Zimbabwe", "Mozambique", "Botswana"), classes=SITE),
    R("F11", "Zimbabwe culture (dry-stone)", "zimbabwe", countries=cs("South Africa"), classes=SITE, place=r"limpopo|mapungubwe|vhembe"),
    R("F20", "Sudano-Sahelian", "sahel", countries=cs("Mali", "Niger", "Burkina Faso", "Guinea", "Ivory Coast", "Ghana", "Chad"),
      classes={"mosque", "madrasa", "tomb", "mausoleum", "palace"}, years=(1200, 1960), before=r"sudano|sahel"),
    R("F21", "Sudano-Sahelian", "sahel", countries=cs("Mali", "Niger", "Burkina Faso", "Guinea", "Ivory Coast", "Ghana", "Chad"),
      classes={"mosque", "madrasa", "tomb", "mausoleum", "palace"}, undated=True, notable=True),
    R("F22", "Sudano-Sahelian", "sahel", countries=cs("Nigeria", "Senegal"), classes={"mosque"}, years=(1200, 1930)),
    R("F23", "Sudano-Sahelian", "sahel", countries=cs("Nigeria"), classes={"mosque", "palace"}, place=r"kano|katsina|zaria|sokoto|zazzau|bauchi|kaduna"),
    R("F24", "Saharan stone (Mauritania ksour)", "saharan", countries=cs("Mauritania"), classes={"mosque", "ksar"} | SITE),
    R("F25", "Sudano-Sahelian (urban sites)", "sahel", countries=cs("Mali"), classes=SITE),
    R("F30", "Swahili coast (coral stone)", "swahili", countries=SWAHILI, classes={"mosque", "tomb", "mausoleum", "palace", "fort"} | SITE,
      place=r"kilwa|lamu|mombasa|kilifi|zanzibar|unguja|pemba|tanga|lindi|mtwara|malindi|gedi|songo|kwale|bagamoyo|pwani|coast",
      before=r"swahili"),
    R("F40", "Kushite (Napatan / Meroitic)", "kushite", countries=cs("Sudan"), classes={"pyramid"} | SITE),
    R("F50", "Benin / Dahomey court architecture", "west_african_court", countries=cs("Benin", "Nigeria"), classes={"palace"}, notable=True),
    R("O01", "Nan Madol (Saudeleur megalithic)", "oceania", countries=cs("Federated States of Micronesia"), classes=SITE, place=r"pohnpei|kosrae|nan madol|leluh"),
    R("O02", "Rapa Nui (ahu / moai)", "oceania", countries=cs("Chile"), place=r"easter island|isla de pascua|rapa nui"),
    R("O03", "Tongan megalithic (langi / trilithon)", "oceania", countries=cs("Tonga"), classes=SITE),

    # --- Khmer and mainland Southeast Asia
    R("K01", "Pre-Angkorian Khmer", "khmer", countries=cs("Cambodia", "Laos", "Thailand", "Vietnam"), classes=TEMPLE | SITE, years=(550, 801),
      place=r"cambodia|kampong thom|sambor|takeo|champasak|kampong|siem reap|preah vihear|kratie|svay rieng"),
    R("K02", "Khmer (Angkorian)", "khmer", countries=cs("Cambodia"), classes=TEMPLE | SITE, years=(802, 1431), before=r"khmer"),
    R("K03", "Khmer (Angkorian)", "khmer", classes={"khmer_temple"}),
    R("K04", "Khmer (Angkorian, provincial)", "khmer", countries=cs("Thailand", "Laos"), classes=TEMPLE | SITE, years=(850, 1300),
      place=r"buri ?ram|nakhon ratchasima|surin|si ?sa ?ket|ubon|lop ?buri|sa kaeo|prachin|champasak|phimai|phanom rung"),
    R("K05", "Khmer (Angkorian)", "khmer", countries=cs("Cambodia"), classes=TEMPLE | SITE, undated=True,
      place=r"angkor|siem reap|preah vihear|oddar meanchey|banteay meanchey|koh ker|kampong thom|battambang"),
    R("K06", "Khmer (Angkorian, provincial)", "khmer", countries=cs("Thailand", "Laos"), classes={"hindu_temple", "archaeological_site", "ruins"}, undated=True,
      place=r"buri ?ram|nakhon ratchasima|surin|si ?sa ?ket|phimai|phanom rung|champasak|vat phou|wat phu"),
    R("K07", "Cambodian Buddhist (post-Angkor)", "khmer", countries=cs("Cambodia"), classes={"wat", "buddhist_temple", "stupa", "pagoda"}, years=(1432, 1950)),
    R("T01", "Thai — Sukhothai", "thai", countries=cs("Thailand"), classes=TEMPLE | SITE, years=(1238, 1438), place=r"sukhothai|satchanalai|kamphaeng phet"),
    R("T02", "Thai — Sukhothai", "thai", countries=cs("Thailand"), classes=TEMPLE | SITE, undated=True, notable=True, place=r"sukhothai|satchanalai|kamphaeng phet"),
    R("T03", "Thai — Lanna", "thai", countries=cs("Thailand"), classes=TEMPLE, years=(1260, 1900),
      place=r"chiang mai|chiang rai|lamphun|lampang|phayao|\bnan\b|nan province|phrae|mae hong son"),
    R("T04", "Thai — Lanna", "thai", countries=cs("Thailand"), classes=TEMPLE, undated=True, notable=True,
      place=r"chiang mai|chiang rai|lamphun|lampang|phayao|nan province|phrae|mae hong son"),
    R("T05", "Thai — Ayutthaya", "thai", countries=cs("Thailand"), classes=TEMPLE | SITE | {"palace"}, years=(1351, 1767)),
    R("T06", "Thai — Ayutthaya", "thai", countries=cs("Thailand"), classes=TEMPLE | SITE | {"palace"}, undated=True, notable=True, place=r"ayutthaya"),
    R("T07", "Thai — Rattanakosin", "thai", countries=cs("Thailand"), classes=TEMPLE | {"palace"}, years=(1782, 1932)),
    R("L01", "Lao (Lan Xang / Luang Prabang)", "lao", countries=cs("Laos"), classes={"wat", "buddhist_temple", "stupa"}, before=r"\blao"),
    R("V01", "Cham", "cham", countries=cs("Vietnam"), classes={"hindu_temple", "temple", "archaeological_site", "ruins", "khmer_temple"},
      place=r"qu[aả]ng nam|b[iì]nh [đd][iị]nh|ninh thu[aậ]n|kh[aá]nh h[oò]a|ph[uú] y[eê]n|b[iì]nh thu[aậ]n|m[yỹ] s[oơ]n|qu[aả]ng ng[aã]i|da nang|đà nẵng"),
    R("V02", "Vietnamese Buddhist (Lý – Nguyễn)", "vietnamese", countries=cs("Vietnam"), classes={"buddhist_temple", "pagoda", "stupa"}, notable=True),
    R("B01", "Burmese — Pagan", "burmese", countries=cs("Myanmar"), classes=TEMPLE | SITE, years=(849, 1297), before=r"pagan|bagan"),
    R("B02", "Burmese — Pagan", "burmese", countries=cs("Myanmar"), classes=TEMPLE | SITE, undated=True, place=r"bagan|pagan|nyaung-?u"),
    R("B03", "Arakanese (Mrauk U)", "burmese", countries=cs("Myanmar"), classes=TEMPLE | SITE, place=r"mrauk"),
    R("B04", "Burmese Buddhist (post-Pagan)", "burmese", countries=cs("Myanmar"), classes={"buddhist_temple", "pagoda", "stupa", "wat"}),

    # --- Island Southeast Asia
    R("J06", "Balinese (pura)", "balinese", countries=cs("Indonesia"), classes={"hindu_temple", "temple", "candi"}, place=r"\bbali"),
    R("J01", "Javanese candi — Central Java (Mataram)", "javanese", countries=cs("Indonesia"), classes=TEMPLE | SITE, years=(650, 1000),
      place=r"central java|yogyakarta|magelang|klaten|sleman|dieng|semarang|wonosobo|banjarnegara|temanggung", before=r"candi|indonesia|java"),
    R("J02", "Javanese candi — Central Java (Mataram)", "javanese", countries=cs("Indonesia"), classes=TEMPLE, undated=True,
      place=r"central java|yogyakarta|magelang|klaten|sleman|dieng|semarang|wonosobo|banjarnegara|temanggung"),
    R("J03", "Javanese candi — East Java (Kediri / Singhasari / Majapahit)", "javanese", countries=cs("Indonesia"), classes=TEMPLE | SITE,
      years=(929, 1527), place=r"east java|malang|blitar|mojokerto|trowulan|kediri|pasuruan|probolinggo|jombang|tulungagung"),
    R("J04", "Javanese candi — East Java (Kediri / Singhasari / Majapahit)", "javanese", countries=cs("Indonesia"), classes=TEMPLE, undated=True,
      place=r"east java|malang|blitar|mojokerto|trowulan|kediri|pasuruan|probolinggo|jombang|tulungagung"),
    R("J05", "Sumatran candi (Srivijaya / Melayu)", "javanese", countries=cs("Indonesia"), classes={"candi", "stupa", "buddhist_temple", "hindu_temple"},
      place=r"sumatra|jambi|riau|muara|padang lawas|lampung|bengkulu"),
    R("J07", "Javanese candi (other)", "javanese", countries=cs("Indonesia"), classes={"candi"}),
    R("J08", "Javanese / Malay mosque (tajug)", "javanese", countries=cs("Indonesia", "Malaysia"), classes={"mosque"}, years=(1400, 1850),
      before=r"mosque architecture in indonesia"),

    # --- South Asia: Sri Lanka, Nepal, Bhutan, Gandhara
    R("S01", "Sinhalese — Anuradhapura", "sri_lankan", countries=cs("Sri Lanka"), classes=TEMPLE | SITE | {"palace"}, place=r"anuradhapura|mihintale|mihintalaya"),
    R("S02", "Sinhalese — Polonnaruwa", "sri_lankan", countries=cs("Sri Lanka"), classes=TEMPLE | SITE | {"palace"}, place=r"polonnaruwa"),
    R("S03", "Sinhalese — Kandyan", "sri_lankan", countries=cs("Sri Lanka"), classes=TEMPLE | {"palace"}, place=r"kandy"),
    R("S04", "Sinhalese Buddhist (other)", "sri_lankan", countries=cs("Sri Lanka"), classes={"buddhist_temple", "stupa", "cave_temple", "rock_cut"} | SITE, notable=True),
    R("S05", "Sri Lankan Dravidian (kovil)", "dravidian", countries=cs("Sri Lanka"), classes={"hindu_temple"}, notable=True),
    R("S10", "Newar (Kathmandu valley)", "newar", countries=cs("Nepal"), classes={"hindu_temple", "buddhist_temple", "pagoda", "stupa", "palace", "temple"},
      years=(-500, 1850), before=r"newa"),
    R("S10b", "Newar (Kathmandu valley)", "newar", countries=cs("Nepal"), classes={"hindu_temple", "buddhist_temple", "pagoda", "stupa", "palace", "temple"},
      undated=True),
    R("S11", "Bhutanese dzong", "tibetan", countries=cs("Bhutan"), classes={"dzong", "fortress", "fort", "buddhist_temple", "tibetan_monastery"}),
    R("S12", "Tibetan Buddhist", "tibetan", classes={"tibetan_monastery"}, before=r"tibet"),
    R("S12b", "Tibetan Buddhist", "tibetan", countries=cs("People's Republic of China"), classes=EA_BUDDHIST | {"palace", "chinese_temple", "temple"},
      place=r"tibet|xizang|lhasa|shigatse|nyingchi|shannan|chamdo|ngari"),
    R("S13", "Gandharan Buddhist", "gandharan", countries=cs("Pakistan", "Afghanistan"), classes={"stupa", "buddhist_temple", "archaeological_site", "ruins"},
      place=r"taxila|khyber|peshawar|swat|mardan|takht|gandhara|punjab|nangarhar|bamyan|kabul|kapisa|logar|balkh", before=r"gandhar"),

    # --- India: Dravidian (Tamil Nadu, Puducherry)
    R("D01", "Dravidian — Pallava", "dravidian", countries=cs("India"), classes=TEMPLE, place=r"mahabalipuram|mamallapuram", years=(550, 900)),
    R("D02", "Dravidian — Pallava", "dravidian", countries=cs("India"), classes=TEMPLE, place=r"mahabalipuram|mamallapuram", undated=True),
    R("D03", "Dravidian — Chola", "dravidian", countries=cs("India"), classes=TEMPLE, place=r"great living chola"),
    R("D04", "Dravidian — Chola", "dravidian", countries=cs("India"), classes=TEMPLE, founder=r"chola|rajaraja|rajendra|parantaka|kulottunga|aditya i"),
    R("D05", "Dravidian — Pallava", "dravidian", countries=cs("India"), classes=TEMPLE, founder=r"pallava|narasimhavarman|mahendravarman|rajasimha"),
    R("D10", "Dravidian — Pallava", "dravidian", countries=cs("India"), classes=TEMPLE, place=r"tamil nadu|puducherry|pondicherry", years=(550, 849), before=r"pallava"),
    R("D11", "Dravidian — Chola", "dravidian", countries=cs("India"), classes=TEMPLE, place=r"tamil nadu|puducherry|pondicherry", years=(850, 1250), before=r"chola"),
    R("D12", "Dravidian — Pandya", "dravidian", countries=cs("India"), classes=TEMPLE, place=r"tamil nadu|puducherry|pondicherry", years=(1251, 1350), before=r"pandya"),
    R("D13", "Dravidian — Vijayanagara", "dravidian", countries=cs("India"), classes=TEMPLE | {"palace"}, place=r"tamil nadu|puducherry|pondicherry", years=(1351, 1565), before=r"vijayanagar"),
    R("D14", "Dravidian — Nayak", "dravidian", countries=cs("India"), classes=TEMPLE | {"palace"}, place=r"tamil nadu|puducherry|pondicherry", years=(1566, 1736), before=r"nayak"),
    R("D15", "Dravidian — modern (after 1736)", "dravidian", countries=cs("India"), classes=TEMPLE, place=r"tamil nadu|puducherry|pondicherry", years=(1737, 2100)),
    R("D16", "Dravidian (undated)", "dravidian", countries=cs("India"), classes=TEMPLE, place=r"tamil nadu|puducherry|pondicherry", undated=True, notable=True, before=r"dravid"),
    # Karnataka
    R("D20", "Badami Chalukya", "vesara", countries=cs("India"), classes=TEMPLE, place=r"pattadakal|aihole|badami|bagalkot|mahakuta", years=(500, 800), before=r"badami chalukya"),
    R("D21", "Badami Chalukya", "vesara", countries=cs("India"), classes=TEMPLE, place=r"pattadakal|aihole|badami|mahakuta", undated=True),
    R("D22", "Dravidian — Vijayanagara", "dravidian", countries=cs("India"), classes=TEMPLE | {"palace", "fort", "ruins", "archaeological_site"}, place=r"hampi|vijayanagara"),
    R("D23", "Dravidian — Vijayanagara", "dravidian", countries=cs("India"), classes=TEMPLE, place=r"karnataka|andhra pradesh", years=(1336, 1565)),
    R("D24", "Hoysala", "vesara", countries=cs("India"), classes=TEMPLE, place=r"hassan|mandya|mysore|mysuru|chikmagalur|chikkamagaluru|tumkur|tumakuru|chamarajanagar|kolar|bangalore|bengaluru|shimoga|shivamogga|belur|halebidu|somanathapura",
      years=(1100, 1343), before=r"hoysala"),
    R("D25", "Hoysala", "vesara", countries=cs("India"), classes=TEMPLE, place=r"hassan|mandya|mysore|mysuru|chikmagalur|chikkamagaluru|tumkur|tumakuru|belur|halebidu|somanathapura",
      undated=True, notable=True),
    R("D26", "Western Chalukya (Kalyani)", "vesara", countries=cs("India"), classes=TEMPLE, place=r"karnataka|telangana|maharashtra", years=(973, 1200), before=r"western chalukya|chalukya"),
    R("D27", "Western Chalukya (Kalyani)", "vesara", countries=cs("India"), classes=TEMPLE, undated=True, notable=True,
      place=r"dharwad|gadag|haveri|koppal|davanagere|bellary|ballari|raichur|bidar|kalaburagi|gulbarga|vijayapura|bijapur|lakkundi|itagi|lakshmeshwar"),
    R("D28", "Karnataka Dravidian (other / undated)", "dravidian", countries=cs("India"), classes=TEMPLE, place=r"karnataka", notable=True),
    # Kerala, Andhra, Telangana
    R("D30", "Kerala temple architecture", "dravidian", countries=cs("India"), classes=TEMPLE | {"palace"}, place=r"kerala", before=r"kerala"),
    R("D31", "Kakatiya", "dravidian", countries=cs("India"), classes=TEMPLE | {"fort"}, place=r"telangana|warangal|andhra pradesh", years=(1083, 1323), before=r"kakatiya"),
    R("D32", "Andhra Dravidian (other / undated)", "dravidian", countries=cs("India"), classes=TEMPLE, place=r"telangana|andhra pradesh", notable=True),

    # --- India: Nagara and other north/east schools
    R("G01", "Nagara — Chandela (Khajuraho)", "nagara", countries=cs("India"), classes=TEMPLE, place=r"khajuraho|chhatarpur", before=r"chandela|khajuraho"),
    R("G02", "Nagara — Kalinga (Odisha)", "nagara", countries=cs("India"), classes=TEMPLE, place=r"odisha|orissa", years=(600, 1600), before=r"kalinga|odia|orissan"),
    R("G03", "Nagara — Kalinga (Odisha)", "nagara", countries=cs("India"), classes=TEMPLE, place=r"odisha|orissa", undated=True, notable=True),
    R("G04", "Nagara — Maru-Gurjara", "nagara", countries=cs("India"), classes={"jain_temple"}, place=r"gujarat|rajasthan|mount abu"),
    R("G05", "Nagara — Maru-Gurjara", "nagara", countries=cs("India"), classes=TEMPLE, place=r"gujarat|rajasthan", years=(950, 1350), before=r"m[aā]ru-gurjara"),
    R("G06", "Nagara — Maru-Gurjara", "nagara", countries=cs("India"), classes=TEMPLE, place=r"gujarat|rajasthan", undated=True, notable=True),
    R("G08", "Nagara — Bhumija / Hemadpanti (Deccan)", "nagara", countries=cs("India"), classes=TEMPLE, place=r"maharashtra", years=(1000, 1350)),
    R("G09", "Indian rock-cut (caves)", "rock_cut_india", countries=cs("India"), classes={"cave_temple", "rock_cut"}),
    R("G09b", "Indian rock-cut (caves)", "rock_cut_india", countries=cs("India"), classes={"buddhist_temple", "hindu_temple", "jain_temple"},
      place=r"ajanta|ellora|elephanta|karla|bhaja|kanheri|bagh caves|udayagiri"),
    R("G10", "Nagara — Bhumija / Hemadpanti (Deccan)", "nagara", countries=cs("India"), classes=TEMPLE, place=r"maharashtra", undated=True, notable=True),
    R("G11", "Kashmiri (Karkota / Utpala)", "nagara", countries=cs("India"), classes=TEMPLE | SITE, place=r"kashmir|martand|avantipur", years=(500, 1300)),
    R("G12", "Kashmiri (Karkota / Utpala)", "nagara", countries=cs("India"), classes=TEMPLE | SITE, place=r"kashmir|martand|avantipur", undated=True, notable=True),
    R("G13", "Nagara — Himalayan (Himachal / Uttarakhand)", "nagara", countries=cs("India"), classes=TEMPLE, place=r"himachal|uttarakhand", notable=True),
    R("G14", "Bengal temple (chala / ratna, terracotta)", "bengal", countries=cs("India", "Bangladesh"), classes=TEMPLE, place=r"west bengal|bengal|bangladesh|bishnupur|bankura|kalna|dhaka|rajshahi|khulna",
      years=(1500, 1900), before=r"bengal|chala|ratna|navaratna|pancharatna"),
    R("G15", "Bengal temple (chala / ratna, terracotta)", "bengal", countries=cs("India", "Bangladesh"), classes=TEMPLE, undated=True, notable=True,
      place=r"west bengal|bengal|bangladesh|bishnupur|bankura|kalna|dhaka|rajshahi|khulna"),
    R("G16", "Assamese / Ahom temple", "nagara", countries=cs("India"), classes=TEMPLE, place=r"assam", notable=True),
    R("G17", "Nagara — central / north India", "nagara", countries=cs("India"), classes=TEMPLE, place=NORTH_INDIA, years=(400, 1300), before=r"nagara"),
    R("G18", "Nagara — central / north India", "nagara", countries=cs("India"), classes=TEMPLE, place=NORTH_INDIA, undated=True, notable=True),
    R("G19", "Early Buddhist (Maurya – Gupta – Pala)", "early_buddhist", countries=cs("India", "Bangladesh"), classes={"stupa", "buddhist_temple"}, years=(-300, 1200)),
    R("G20", "Early Buddhist (Maurya – Gupta – Pala)", "early_buddhist", countries=cs("India", "Bangladesh"), classes={"stupa", "buddhist_temple"} | SITE, undated=True,
      place=r"sanchi|bodh gaya|nalanda|sarnath|amaravati|bharhut|vikramashila|paharpur|somapura|vaishali|kushinagar|nagarjuna"),

    # --- South Asia: Indo-Islamic, Mughal, Rajput
    R("I01", "Mughal", "mughal", countries=cs("India", "Pakistan", "Bangladesh"), classes=ISL | {"stepwell"},
      place=r"fatehpur sikri|red fort|agra fort|humayun|taj mahal|lahore fort|shalimar"),
    R("I02", "Rajput (forts and palaces)", "rajput", countries=cs("India"), classes={"fort", "fortress", "palace"}, place=r"rajasthan|hill forts of rajasthan", before=r"rajput"),
    R("I03", "Deccan Sultanates (Bahmani / Qutb Shahi / Adil Shahi)", "indo_islamic", countries=cs("India"), classes=ISL,
      place=r"karnataka|telangana|maharashtra|andhra pradesh|hyderabad|bijapur|bidar|golconda|gulbarga|kalaburagi", years=(1347, 1687), before=r"deccan"),
    R("I04", "Gujarat Sultanate", "indo_islamic", countries=cs("India"), classes=ISL | {"stepwell"}, place=r"gujarat", years=(1407, 1573)),
    R("I05", "Bengal Sultanate", "indo_islamic", countries=cs("India", "Bangladesh"), classes=ISL, place=r"bengal|bangladesh|dhaka|rajshahi|khulna|chittagong|sylhet|bagerhat|gaur|pandua|malda",
      years=(1352, 1576), before=r"bengal sultanate"),
    R("I06", "Indo-Islamic (Delhi Sultanate)", "indo_islamic", countries=cs("India", "Pakistan", "Bangladesh"), classes=ISL, years=(1192, 1525), before=r"indo-islamic|sultanate"),
    R("I07", "Mughal", "mughal", countries=cs("India", "Pakistan", "Bangladesh"), classes=ISL - {"fort", "fortress", "palace"}, years=(1526, 1857), before=r"^mughal architecture"),
    R("I07b", "Mughal", "mughal", countries=cs("India", "Pakistan", "Bangladesh"), classes={"fort", "fortress", "palace"}, years=(1526, 1857),
      place=r"agra|delhi|lahore|fatehpur|allahabad|prayagraj|attock|ajmer|aurangabad|dhaka|srinagar"),
    R("I08", "Mughal", "mughal", countries=cs("India", "Pakistan", "Bangladesh"), classes=ISL, undated=True, notable=True,
      place=r"\bagra\b|lahore"),
    R("I08b", "Mughal", "mughal", countries=cs("India", "Pakistan", "Bangladesh"), classes=ISL, name=r"taj mahal|humayun|akbar|jahangir|itimad|shalimar"),
    R("I09", "Deccan hill and sea forts (Maratha era)", "maratha", countries=cs("India"), classes={"fort", "fortress"}, place=r"maharashtra", notable=True),
    R("G07", "Stepwell (western India)", "nagara", countries=cs("India", "Pakistan"), classes={"stepwell"}),


    # --- Iran, Central Asia, Anatolia, Arab world, Maghreb (dated only)
    R("P01", "Persian — early Islamic (Samanid / Buyid / Ghaznavid)", "persian", countries=cs("Iran", "Afghanistan", "Uzbekistan", "Turkmenistan", "Tajikistan"), classes=ISL, years=(800, 1036)),
    R("P02", "Persian — Seljuk / Khwarazmian", "persian", countries=cs("Iran", "Afghanistan", "Uzbekistan", "Turkmenistan", "Tajikistan", "Azerbaijan"), classes=ISL, years=(1037, 1255), before=r"^seljuk architecture"),
    R("P03", "Persian — Ilkhanid / Muzaffarid", "persian", countries=cs("Iran", "Iraq", "Azerbaijan"), classes=ISL, years=(1256, 1369), before=r"ilkhanid"),
    R("P04", "Timurid", "persian", countries=cs("Iran", "Afghanistan", "Uzbekistan", "Turkmenistan", "Tajikistan", "Kazakhstan"), classes=ISL, years=(1370, 1507), before=r"^timurid"),
    R("P05", "Persian — Safavid", "persian", countries=cs("Iran", "Azerbaijan"), classes=ISL, years=(1501, 1736), before=r"safavid"),
    R("P06", "Central Asian — Shaybanid / khanates (Bukhara, Khiva, Kokand)", "central_asian", countries=cs("Uzbekistan", "Turkmenistan", "Tajikistan", "Kazakhstan", "Afghanistan"), classes=ISL, years=(1500, 1920)),
    R("P07", "Persian — Qajar", "persian", countries=cs("Iran"), classes=ISL, years=(1789, 1925), before=r"qajar"),
    R("P08", "Azerbaijani (Shirvan–Absheron)", "persian", countries=cs("Azerbaijan"), classes=ISL, years=(1256, 1900)),
    R("U01", "Anatolian Seljuk / Beylik", "ottoman", countries=cs("Turkey"), classes=ISL, years=(1075, 1350), before=r"anatolian seljuk"),
    R("U02", "Ottoman", "ottoman", countries=cs("Turkey"), classes=ISL, years=(1351, 1922), before=r"^ottoman architecture$"),
    R("E01", "Early Islamic (Umayyad / Abbasid / Tulunid)", "arab_islamic", countries=cs("Egypt", "Syria", "Iraq"), classes=ISL, years=(640, 968)),
    R("E02", "Fatimid", "arab_islamic", countries=cs("Egypt", "Syria", "Tunisia"), classes=ISL, years=(969, 1170), before=r"fatimid"),
    R("E03", "Ayyubid", "arab_islamic", countries=cs("Egypt", "Syria", "Iraq"), classes=ISL, years=(1171, 1249)),
    R("E04", "Mamluk", "arab_islamic", countries=cs("Egypt", "Syria"), classes=ISL, years=(1250, 1517), before=r"^mamluk"),
    R("E05", "Ottoman (Arab provinces)", "ottoman", countries=cs("Egypt", "Syria", "Iraq", "Libya", "Tunisia", "Algeria", "Yemen"), classes=ISL, years=(1518, 1882)),
    R("E06", "Iraqi Islamic (Ilkhanid / Jalayirid)", "arab_islamic", countries=cs("Iraq"), classes=ISL, years=(1256, 1517)),
    R("E07", "Yemeni / Omani Islamic", "arab_islamic", countries=cs("Yemen", "Oman"), classes=ISL, years=(600, 1900)),
    R("W01", "Almoravid / Almohad", "maghreb", countries=cs("Morocco", "Algeria", "Tunisia"), classes=ISL, years=(1040, 1269), before=r"almohad|almoravid"),
    R("W02", "Marinid / Zayyanid / Hafsid", "maghreb", countries=cs("Morocco", "Algeria", "Tunisia"), classes=ISL, years=(1229, 1550), before=r"marinid"),
    R("W03", "Saadian", "maghreb", countries=cs("Morocco"), classes=ISL, years=(1510, 1659)),
    R("W04", "Alaouite", "maghreb", countries=cs("Morocco"), classes=ISL, years=(1660, 1912)),
    R("W05", "Maghrebi earthen (ksar / kasbah)", "maghreb", countries=cs("Morocco", "Algeria", "Tunisia"), classes={"ksar"}),
    R("W06", "Early Islamic Maghreb (Aghlabid / Idrisid / Zirid)", "maghreb", countries=cs("Tunisia", "Algeria", "Morocco", "Libya"), classes=ISL, years=(670, 1039)),
    R("H01", "Chinese Islamic", "chinese", countries=cs("People's Republic of China"), classes={"mosque"}, before=r"chinese islamic"),
    R("H02", "Swahili coast (coral stone)", "swahili", countries=SWAHILI, classes={"mosque", "tomb", "mausoleum"}, years=(900, 1900)),
    R("H03", "Ethiopian Islamic (Harar)", "ethiopian", countries=ETH, classes={"mosque", "tomb", "mausoleum"}, place=r"harar|harari"),

    # --- East Asia (dates are often founding dates, see module docstring)
    R("Y01", "Kofun (mounded tombs)", "japanese", countries=cs("Japan"), classes={"kofun"}),
    R("Y02", "Japanese Buddhist — Asuka / Nara (538–794)", "japanese", countries=cs("Japan"), classes=EA_BUDDHIST, years=(538, 794), before=r"asuka|japanese buddhist"),
    R("Y03", "Japanese Buddhist — Heian (794–1185)", "japanese", countries=cs("Japan"), classes=EA_BUDDHIST, years=(795, 1185)),
    R("Y04", "Japanese Buddhist — Kamakura (Daibutsuyō / Zenshūyō)", "japanese", countries=cs("Japan"), classes=EA_BUDDHIST, years=(1186, 1333)),
    R("Y05", "Japanese Buddhist — Muromachi / Momoyama", "japanese", countries=cs("Japan"), classes=EA_BUDDHIST, years=(1334, 1602)),
    R("Y06", "Japanese Buddhist — Edo", "japanese", countries=cs("Japan"), classes=EA_BUDDHIST, years=(1603, 1867)),
    R("Y07", "Japanese Buddhist (undated)", "japanese", countries=cs("Japan"), classes=EA_BUDDHIST, undated=True, notable=True),
    R("Y08", "Shinto shrine", "japanese", countries=cs("Japan"), classes={"shinto_shrine"}, years=(-100, 1867), before=r"zukuri|shinto"),
    R("Y09", "Shinto shrine", "japanese", countries=cs("Japan"), classes={"shinto_shrine"}, undated=True, notable=True),
    R("Y10", "Japanese castle", "japanese", countries=cs("Japan"), classes={"japanese_castle"}, before=r"japanese castle"),
    R("Z01", "Korean Buddhist — Three Kingdoms / Unified Silla", "korean", countries=cs("South Korea", "North Korea"), classes=EA_BUDDHIST, years=(372, 935)),
    R("Z02", "Korean Buddhist — Goryeo", "korean", countries=cs("South Korea", "North Korea"), classes=EA_BUDDHIST, years=(936, 1392)),
    R("Z03", "Korean — Joseon", "korean", countries=cs("South Korea", "North Korea"), classes=EA_BUDDHIST | {"palace"}, years=(1393, 1897)),
    R("Z04", "Korean Buddhist (undated)", "korean", countries=cs("South Korea", "North Korea"), classes=EA_BUDDHIST, undated=True, notable=True, before=r"korean"),
    R("Q01", "Chinese — pre-Tang (to 617)", "chinese", countries=cs("People's Republic of China"), classes=EA_BUDDHIST | {"chinese_temple", "taoist_temple", "cave_temple", "rock_cut"}, years=(-300, 617)),
    R("Q02", "Chinese — Tang (618–907)", "chinese", countries=cs("People's Republic of China"), classes=EA_BUDDHIST | {"chinese_temple", "taoist_temple", "cave_temple", "rock_cut"}, years=(618, 907)),
    R("Q03", "Chinese — Liao / Song / Jin (907–1279)", "chinese", countries=cs("People's Republic of China"), classes=EA_BUDDHIST | {"chinese_temple", "taoist_temple", "cave_temple", "rock_cut"}, years=(908, 1279)),
    R("Q04", "Chinese — Yuan (1279–1368)", "chinese", countries=cs("People's Republic of China"), classes=EA_BUDDHIST | {"chinese_temple", "taoist_temple"}, years=(1280, 1368)),
    R("Q05", "Chinese — Ming (1368–1644)", "chinese", countries=cs("People's Republic of China"), classes=EA_BUDDHIST | {"chinese_temple", "taoist_temple", "palace"}, years=(1369, 1644)),
    R("Q06", "Chinese — Qing (1644–1912)", "chinese", countries=cs("People's Republic of China"), classes=EA_BUDDHIST | {"chinese_temple", "taoist_temple", "palace"}, years=(1645, 1912)),
    R("Q07", "Chinese temple (undated)", "chinese", countries=cs("People's Republic of China"), classes=EA_BUDDHIST | {"chinese_temple", "taoist_temple"}, undated=True, notable=True, before=r"^chinese architecture$"),
    R("Q08", "Taiwanese (Minnan) temple", "chinese", countries=cs("Taiwan"), classes=EA_BUDDHIST | {"chinese_temple", "taoist_temple"}, notable=True),
]

# Existing P149 labels -> regional families (for wrong-tag flags). Labels that match
# none (Islamic architecture, Buddhist architecture, rock-cut architecture, ...) are
# treated as generic and never flagged.
FAMILY_RE = [
    ("khmer", r"khmer|angkor"),
    ("dravidian", r"dravid|tamil|chola|pallava|pandya|nayak|vijayanagar|kerala|kakatiya"),
    ("vesara", r"hoysala|chalukya|vesara"),
    ("nagara", r"nagara|kalinga|odia|orissa|m[aā]ru|gurjara|solanki|chandela|bhumija|hemadpanti"),
    ("bengal", r"bengal|\bchala|ratna\b|navaratna|pancharatna|at-chala|dalan"),
    ("mughal", r"mughal"),
    ("indo_islamic", r"indo-islamic|sultanate|deccan"),
    ("rajput", r"rajput"),
    ("persian", r"\biran|persian|safavid|timurid|qajar|ilkhanid|seljuk|isfahan|khorasan|razi|azeri"),
    ("central_asian", r"timurid|samanid|bukhar|khwarazm|karakhanid|shaybanid"),
    ("ottoman", r"ottoman|seljuk|turkish"),
    ("arab_islamic", r"mamluk|fatimid|ayyubid|umayyad|abbasid|tulunid"),
    ("maghreb", r"moorish|maghreb|almohad|almoravid|marinid|saadian|andalus|morocc|hafsid|aghlabid"),
    ("sahel", r"sudano|sahel"),
    ("swahili", r"swahili"),
    ("maya", r"\bmaya|puuc|chenes|r[ií]o bec"),
    ("mesoamerican", r"aztec|mexica|zapotec|mixtec|teotihuac|toltec|olmec|mesoamerica|talud"),
    ("andean", r"\binca|andean|moche|chim[uú]|wari|tiwanaku|chav[ií]n"),
    ("japanese", r"japan|shinto|zukuri|wayō|zenshūyō|daibutsuyō|asuka|heian|kamakura|shoin|sukiya"),
    ("chinese", r"\bchin(a|ese)\b"),
    ("korean", r"korea|joseon|goryeo|silla"),
    ("thai", r"\bthai|siam|ayutthaya|sukhothai|lanna|rattanakosin"),
    ("burmese", r"burm|myanmar|\bpagan\b|bagan"),
    ("lao", r"\blao"),
    ("cham", r"\bcham\b"),
    ("vietnamese", r"vietnam"),
    ("javanese", r"\bjava|candi|indonesia|majapahit|malay"),
    ("balinese", r"\bbali"),
    ("sri_lankan", r"sri lanka|sinhal|anuradhapura|polonnaruwa|kandyan"),
    ("newar", r"\bnewa|nepal"),
    ("tibetan", r"tibet|dzong"),
    ("ethiopian", r"ethiop|aksum|axum|lalibela|gondar"),
    ("zimbabwe", r"zimbabwe"),
    ("puebloan", r"pueblo"),
    ("european", r"gothic|baroque|renaissance|neoclassic|romanesque|colonial|victorian|art deco|modernis|indo-saracenic|revival|byzantine|rococo|palladian|art nouveau"),
]
# Proposed family -> other families it accepts without a flag.
COMPAT = {
    "mughal": {"indo_islamic"}, "indo_islamic": {"mughal"},
    "vesara": {"dravidian"}, "dravidian": {"vesara"},
    "persian": {"central_asian", "ottoman", "arab_islamic"}, "central_asian": {"persian"},
    "ottoman": {"persian", "arab_islamic", "maghreb"}, "arab_islamic": {"ottoman", "persian", "maghreb"},
    "maghreb": {"ottoman", "arab_islamic"}, "saharan": {"maghreb", "sahel"}, "maratha": {"mughal", "rajput"},
    "maya": {"mesoamerican"}, "mesoamerican": {"maya"},
    "nagara": {"bengal", "rajput"}, "bengal": {"nagara", "indo_islamic"}, "rajput": {"mughal", "nagara", "indo_islamic"},
    "javanese": {"balinese"}, "balinese": {"javanese"},
    "khmer": set(), "thai": {"khmer", "burmese", "lao"}, "lao": {"thai"}, "burmese": {"thai"},
    "early_buddhist": {"nagara"}, "rock_cut_india": {"nagara", "dravidian", "vesara", "early_buddhist"},
    "gandharan": set(), "tibetan": {"chinese", "newar"}, "newar": {"tibetan"},
    "sahel": set(), "swahili": {"arab_islamic"}, "andean": set(), "japanese": {"chinese"}, "korean": {"chinese"},
    "chinese": {"tibetan"},
}


# ---------------------------------------------------------------- SPARQL plumbing

def q(query):
    """Cached SPARQL (one JSON file per distinct query text, same cache as build_styles.py).

    Returns None (and records the failure) when the query keeps failing, so the
    run continues; a re-run retries only the missing queries."""
    h = hashlib.sha1(query.encode()).hexdigest()[:16]
    path = os.path.join(RAW, f"q_{h}.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    try:
        rows = sparql(query)
    except Exception as e:  # noqa: BLE001 - any failure: report and carry on
        print(f"    query failed ({type(e).__name__}: {e}); will retry on re-run")
        FAILED.append(query[:120])
        return None
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False)
    os.replace(tmp, path)
    return rows


def run_all(queries, label):
    """Run queries with at most WORKERS concurrent; failed ones yield []."""
    out = []
    with ThreadPoolExecutor(WORKERS) as pool:
        for i, rows in enumerate(pool.map(q, queries), 1):
            out.append(rows or [])
            if i % 25 == 0 or i == len(queries):
                print(f"  {label}: {i}/{len(queries)}", flush=True)
    return out


def chunks(items, n=CHUNK):
    return [items[i:i + n] for i in range(0, len(items), n)]


def values(qids):
    return " ".join("wd:" + x for x in qids)


def is_qid(x):
    return bool(x) and re.fullmatch(r"Q\d+", x) is not None


# ---------------------------------------------------------------- steps

def verify(force):
    """Check every class and country QID against its expected English label."""
    expected = {qid: lab for qid, lab in CLASSES.values()}
    expected.update(COUNTRIES)
    got = {}
    for rows in run_all([f"""SELECT ?x ?l WHERE {{ VALUES ?x {{ {values(c)} }}
              ?x rdfs:label ?l FILTER(LANG(?l) = "en") }}""" for c in chunks(sorted(expected))], "verify labels"):
        got.update({r["x"]: r["l"] for r in rows})
    bad = [(x, lab, got.get(x)) for x, lab in expected.items() if (got.get(x) or "").lower() != lab.lower()]
    for x, lab, g in bad:
        print(f"  LABEL MISMATCH {x}: expected {lab!r}, Wikidata has {g!r}")
    if bad and not force:
        sys.exit("QID verification failed (pass --force to continue)")
    print(f"verified {len(expected) - len(bad)}/{len(expected)} class and country QIDs by label")


def list_candidates(min_sl):
    """Step 1: class x country listings -> {qid: sitelinks}, {qid: set(class keys listed under)}."""
    jobs = [(k, c) for k in sorted(SCOPE) for c in sorted(SCOPE[k])]
    queries = [f"""SELECT ?b ?sl WHERE {{ ?b wdt:P31/wdt:P279* wd:{CLASSES[k][0]} ; wdt:P17 wd:{c} ; wikibase:sitelinks ?sl .
              FILTER(?sl >= {min_sl} || EXISTS {{ ?b wdt:P1435 [] }} || EXISTS {{ ?b wdt:P757 [] }} || EXISTS {{ ?b wdt:P571 [] }}) }}"""
               for k, c in jobs]
    sl, per_job = {}, collections.Counter()
    for (k, c), rows in zip(jobs, run_all(queries, "class x country listings")):
        for r in rows:
            sl[r["b"]] = int(r["sl"])
            per_job[(k, c)] += 1
    print(f"  {len(sl)} listed items from {len(jobs)} class x country pairs")
    return sl, per_job


def unesco_items():
    """Step 2: WHS (P757) outside Europe and their components -> {qid: site qid or ''}."""
    sites = q("""SELECT ?s ?c WHERE { ?s wdt:P757 ?id . OPTIONAL { ?s wdt:P17 ?c } }""") or []
    countries = sorted({r["c"] for r in sites if is_qid(r.get("c"))})
    conts = country_continents(countries)
    keep = {"Q48", "Q15", "Q49", "Q18", "Q55643", "Q538", "Q3960"}
    excluded = {"Q159"}  # Russia: listed in Asia but its WHS are European or natural
    site_c = collections.defaultdict(set)
    for r in sites:
        if is_qid(r.get("c")):
            site_c[r["s"]].add(r["c"])
    whs = sorted(s for s, cc in site_c.items() if any(set(conts.get(c, [])) & keep for c in cc) and not cc & excluded)
    comp = {}
    for rows in run_all([f"""SELECT ?b ?s WHERE {{ VALUES ?s {{ {values(c)} }}
              {{ ?b wdt:P361 ?s }} UNION {{ ?b wdt:P361/wdt:P361 ?s }} }}""" for c in chunks(whs)], "UNESCO components"):
        for r in rows:
            comp.setdefault(r["b"], r["s"])
    for s in whs:
        comp[s] = ""
    print(f"  {len(whs)} World Heritage items outside Europe, {len(comp) - len(whs)} components")
    return comp, set(whs)


def country_continents(countries):
    """Continent(s) per country QID; shares data/raw/wikidata/pool/country_continents.json."""
    path = os.path.join(POOL_RAW, "country_continents.json")
    os.makedirs(POOL_RAW, exist_ok=True)
    known = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    for prop_path in ["wdt:P30", "wdt:P17/wdt:P30", "wdt:P1366/wdt:P30", "wdt:P36/wdt:P17/wdt:P30"]:
        todo = [c for c in countries if not known.get(c)]
        if not todo:
            break
        for c in todo:
            known.setdefault(c, [])
        for rows in run_all([f"SELECT ?c ?cont WHERE {{ VALUES ?c {{ {values(ch)} }} ?c {prop_path} ?cont . }}"
                             for ch in chunks(todo, 100)], f"continents {prop_path}"):
            for r in rows:
                if r["cont"] not in known[r["c"]]:
                    known[r["c"]].append(r["cont"])
    tmp = path + ".tmp"
    json.dump(known, open(tmp, "w", encoding="utf-8"))
    os.replace(tmp, path)
    return known


DETAIL_PROPS = ["P17", "P571", "P580", "P1435", "P757", "P361", "P149", "P2596", "P112", "P88", "P625"]


def details(qids):
    """Step 3: claims, sitelinks, matched classes and admin ancestors for every candidate."""
    claims = {x: collections.defaultdict(list) for x in qids}
    pv = " ".join("wdt:" + p for p in DETAIL_PROPS)
    for rows in run_all([f"""SELECT ?s ?prop ?v WHERE {{ VALUES ?s {{ {values(c)} }}
              VALUES ?prop {{ {pv} }} ?s ?prop ?v . }}""" for c in chunks(qids)], "candidate claims"):
        for r in rows:
            p = r["prop"].rsplit("/", 1)[-1]
            if r["v"] not in claims[r["s"]][p]:
                claims[r["s"]][p].append(r["v"])
    sl = {}
    for rows in run_all([f"SELECT ?s ?sl WHERE {{ VALUES ?s {{ {values(c)} }} ?s wikibase:sitelinks ?sl }}"
                         for c in chunks(qids)], "candidate sitelinks"):
        sl.update({r["s"]: int(r["sl"]) for r in rows})
    cls_by_qid = {qid: k for k, (qid, _) in CLASSES.items()}
    cvals = values(sorted(cls_by_qid))
    classes = collections.defaultdict(set)
    for rows in run_all([f"""SELECT DISTINCT ?s ?c WHERE {{ VALUES ?s {{ {values(c)} }} VALUES ?c {{ {cvals} }}
              ?s wdt:P31/wdt:P279* ?c . }}""" for c in chunks(qids)], "candidate classes"):
        for r in rows:
            classes[r["s"]].add(cls_by_qid[r["c"]])
    admin = collections.defaultdict(list)
    top = {}
    for rows in run_all([f"""SELECT DISTINCT ?s ?a ?al ?top WHERE {{ VALUES ?s {{ {values(c)} }} ?s wdt:P131+ ?a .
              OPTIONAL {{ ?a rdfs:label ?al FILTER(LANG(?al) = "en") }}
              BIND(EXISTS {{ ?a wdt:P131 ?cty . ?s wdt:P17 ?cty }} AS ?top) }}""" for c in chunks(qids)], "admin ancestors"):
        for r in rows:
            lab = r.get("al") or r["a"]
            if lab not in admin[r["s"]]:
                admin[r["s"]].append(lab)
            if r.get("top") in ("true", "1"):
                top.setdefault(r["s"], lab)
    return claims, sl, classes, admin, top


def fetch_labels(qids):
    """English (else any) labels; shares data/raw/wikidata/architecture/labels.json with build_styles.py."""
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


# ---------------------------------------------------------------- rules

def in_maya_area(c):
    if re.search(r"\bmaya", c["culture"]):
        return True
    if c["countries"] & MAYA_COUNTRY:
        return True
    if C["Mexico"] in c["countries"] and re.search(MAYA_MX, c["place"]):
        return True
    if c["countries"] & cs("Honduras", "El Salvador") and c["lon"] is not None and c["lon"] < -88.6:
        return True
    return False


CHURCH_NAME = r"cathedral|church|basilica|chapel|parroquia|iglesia|catedral|convent|capilla|templo de san|santuario"


def match(rule, c):
    # Churches (and converted churches) only ever match the Ethiopian rules: the
    # generic "temple" class otherwise pulls colonial churches into local styles.
    if rule["family"] != "ethiopian" and ("church" in c["classes"] or re.search(CHURCH_NAME, c["label"].lower())):
        return False
    if "name" in rule and not re.search(rule["name"], c["label"].lower()):
        return False
    if "culture" in rule and not re.search(rule["culture"], c["culture"]):
        return False
    if "classes" in rule and not (rule["classes"] & c["classes"]):
        return False
    if "countries" in rule and not (rule["countries"] & c["countries"]):
        return False
    if "place" in rule and not re.search(rule["place"], c["place"]):
        return False
    if "founder" in rule and not re.search(rule["founder"], c["founder"]):
        return False
    if "years" in rule:
        lo, hi = rule["years"]
        if c["year"] is None or not lo <= c["year"] <= hi:
            return False
    if rule.get("undated") and c["year"] is not None:
        return False
    if "bbox" in rule:
        la0, la1, lo0, lo1 = rule["bbox"]
        if c["lat"] is None or not (la0 <= c["lat"] <= la1 and lo0 <= c["lon"] <= lo1):
            return False
    if rule.get("maya") and not in_maya_area(c):
        return False
    if rule.get("notable") and not (c["heritage_any"] or c["sitelinks"] >= 3):
        return False
    return True


def describe(rule):
    names = {v: k for k, v in C.items()}
    parts = []
    if "culture" in rule:
        parts.append(f"culture~/{rule['culture']}/")
    if rule.get("maya"):
        parts.append("Maya area")
    if "countries" in rule:
        cc = sorted(names[x] for x in rule["countries"])
        parts.append("country∈{" + (",".join(cc) if len(cc) <= 6 else ",".join(cc[:6]) + f",+{len(cc) - 6}") + "}")
    if "classes" in rule:
        parts.append("class∈{" + ",".join(sorted(rule["classes"])) + "}")
    if "place" in rule:
        parts.append(f"place~/{rule['place'][:60]}/")
    if "name" in rule:
        parts.append(f"label~/{rule['name']}/")
    if "founder" in rule:
        parts.append(f"founder~/{rule['founder']}/")
    if "years" in rule:
        parts.append(f"{rule['years'][0]}–{rule['years'][1]}")
    if rule.get("undated"):
        parts.append("undated")
    if "bbox" in rule:
        parts.append("lat/lon in " + str(rule["bbox"]))
    if rule.get("notable"):
        parts.append("notable (heritage/UNESCO or >=3 sitelinks)")
    return " & ".join(parts)


def families_of(label):
    low = label.lower()
    return {fam for fam, pat in FAMILY_RE if re.search(pat, low)}


# ---------------------------------------------------------------- main

def main():
    global WORKERS
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--workers", type=int, default=2, choices=range(1, 3), help="concurrent SPARQL queries (max 2)")
    ap.add_argument("--min-sitelinks", type=int, default=1,
                    help="list instances with at least this many sitelinks (heritage, UNESCO or dated items always)")
    ap.add_argument("--force", action="store_true", help="continue despite QID label mismatches")
    args = ap.parse_args()
    WORKERS = args.workers
    os.makedirs(RAW, exist_ok=True)

    verify(args.force)
    listed_sl, per_job = list_candidates(args.min_sitelinks)
    comp, whs = unesco_items()
    qids = sorted(set(listed_sl) | set(comp))
    print(f"{len(qids)} candidates; fetching details")
    claims, sl, classes, admin, top = details(qids)

    want = set(qids) | set(COUNTRIES) | whs
    for cl in claims.values():
        for p in ("P17", "P1435", "P361", "P149", "P2596", "P112", "P88"):
            want.update(cl.get(p, []))
    labels = fetch_labels(want)

    def lab(x):
        return labels.get(x, "") or x

    # ---- candidate records
    cands = []
    for x in qids:
        cl = claims[x]
        yrs = sorted(y for y in (year_of(v) for v in cl.get("P571", [])) if y is not None)
        src = "P571"
        if not yrs:
            yrs = sorted(y for y in (year_of(v) for v in cl.get("P580", [])) if y is not None)
            src = "P580"
        m = re.match(r"Point\(([-\d.eE]+) ([-\d.eE]+)\)", (cl.get("P625") or [""])[0])
        parts = [p for p in cl.get("P361", []) if is_qid(p)]
        unesco_part = comp.get(x) or next((p for p in parts if p in whs), "")
        is_whs = x in whs or bool(cl.get("P757")) or "Q9259" in cl.get("P1435", [])
        her = [h for h in cl.get("P1435", []) if is_qid(h)]
        place_labels = admin.get(x, []) + [lab(p) for p in parts] + ([lab(unesco_part)] if unesco_part else [])
        ctys = {c for c in cl.get("P17", []) if is_qid(c)}
        cands.append({
            "qid": x, "label": lab(x), "classes": classes.get(x, set()), "countries": ctys,
            "year": yrs[0] if yrs else None, "year_src": src if yrs else "",
            "lat": float(m.group(2)) if m else None, "lon": float(m.group(1)) if m else None,
            "place": " | ".join(place_labels).lower(),
            "culture": " | ".join(lab(v) for v in cl.get("P2596", []) if is_qid(v)).lower(),
            "founder": " | ".join(lab(v) for v in cl.get("P112", []) + cl.get("P88", []) if is_qid(v)).lower(),
            "sitelinks": sl.get(x, listed_sl.get(x, 0)),
            "heritage": her, "is_whs": is_whs, "unesco_part": unesco_part,
            "heritage_any": bool(her or is_whs or unesco_part),
            "parts": parts, "p149": [s for s in cl.get("P149", []) if is_qid(s)],
            "region": top.get(x, ""), "admin": admin.get(x, []),
        })

    # ---- apply rules
    for c in cands:
        c["rule"] = next((r for r in RULES if match(r, c)), None)

    # ---- existing P149 check
    flags = []
    for c in cands:
        c["flag"] = ""
        r = c["rule"]
        if not r or not c["p149"]:
            continue
        existing = {s: families_of(lab(s)) for s in c["p149"]}
        fams = set().union(*existing.values())
        if not fams:
            continue
        ok = {r["family"]} | COMPAT.get(r["family"], set())
        if c["year"] is not None and c["year"] >= 1800:
            # 19th/20th-century buildings mix local and European revival styles legitimately.
            existing = {s: f - {"european"} for s, f in existing.items()}
        # Flag every existing tag that names only families the proposed style does not
        # accept, even when another tag agrees (Angkor Wat: Khmer + Dravidian).
        bad = [f"{lab(s)} ({'/'.join(sorted(f))})" for s, f in existing.items() if f and not f & ok]
        if not bad:
            continue
        c["flag"] = f"P149 {'; '.join(bad)} vs proposed {r['style']} ({r['family']})"
        flags.append(c)

    # ---- write rules (proposed seeds input, for review)
    rule_rows = [{"rule": r["id"], "proposed_style": r["style"], "family": r["family"], "conditions": describe(r),
                  "n_candidates": sum(1 for c in cands if c["rule"] is r)} for r in RULES]
    write_csv(os.path.join(OUT_DIR, "architecture_nonwestern_rules.csv"), rule_rows)

    # ---- exemplars CSV
    def tier(c):
        return 0 if c["is_whs"] else 1 if c["unesco_part"] else 2 if c["heritage"] else 3

    rows = []
    for c in sorted(cands, key=lambda c: ((c["rule"] or {}).get("style", "~"), tier(c), -c["sitelinks"], c["qid"])):
        r = c["rule"]
        rows.append({
            "qid": c["qid"], "label": c["label"], "class": "|".join(sorted(c["classes"])),
            "country": "|".join(lab(x) for x in sorted(c["countries"])), "region": c["region"],
            "inception": "" if c["year"] is None else c["year"],
            "heritage": "|".join(["World Heritage Site"] * c["is_whs"] + [lab(h) for h in c["heritage"] if h != "Q9259"]),
            "sitelinks": c["sitelinks"],
            "proposed_style": r["style"] if r else "", "rule": f"{r['id']}: {describe(r)}" if r else "",
            "existing_p149": "|".join(lab(s) for s in c["p149"]),
            "p149_flag": c["flag"], "tier": ["unesco_site", "part_of_unesco", "heritage", "none"][tier(c)],
            "unesco_site": lab(c["unesco_part"]) if c["unesco_part"] else "",
            "family": r["family"] if r else "", "inception_source": c["year_src"],
            "admin": "|".join(c["admin"]), "part_of": "|".join(lab(p) for p in c["parts"]),
            "culture": c["culture"], "lat": "" if c["lat"] is None else c["lat"], "lon": "" if c["lon"] is None else c["lon"],
        })
    write_csv(os.path.join(OUT_DIR, "architecture_nonwestern_exemplars.csv"), rows)

    # ---- styles CSV (with before = existing P149 styles matching the rule's `before` regex)
    existing_styles = list(csv.DictReader(open(STYLES_CSV, encoding="utf-8"))) if os.path.exists(STYLES_CSV) else []
    by_style = collections.defaultdict(list)
    for c in cands:
        if c["rule"]:
            by_style[c["rule"]["style"]].append(c)
    before_re = {}
    for r in RULES:
        if "before" in r:
            before_re.setdefault(r["style"], r["before"])
    srows = []
    for style, cs_ in by_style.items():
        ranked = sorted(cs_, key=lambda c: (tier(c), -c["sitelinks"], c["qid"]))
        matches = [s for s in existing_styles if style in before_re and re.search(before_re[style], s["label"].lower())]
        matches.sort(key=lambda s: -int(s["n_buildings"]))
        srows.append({
            "proposed_style": style, "family": cs_[0]["rule"]["family"],
            "n_candidates": len(cs_), "n_heritage": sum(1 for c in cs_ if c["heritage_any"]),
            "n_unesco": sum(1 for c in cs_ if c["is_whs"] or c["unesco_part"]),
            "n_dated": sum(1 for c in cs_ if c["year"] is not None),
            "n_p149_flags": sum(1 for c in cs_ if c["flag"]),
            "rules": "|".join(sorted({c["rule"]["id"] for c in cs_})),
            "before_p149_buildings": sum(int(s["n_buildings"]) for s in matches),
            "before_p149_styles": "|".join(f"{s['label']} ({s['n_buildings']})" for s in matches if int(s["n_buildings"]))[:300],
            "top10": " | ".join(f"{c['label']} ({c['qid']})" for c in ranked[:10]),
        })
    srows.sort(key=lambda s: (s["family"], -s["n_candidates"]))
    write_csv(os.path.join(OUT_DIR, "architecture_nonwestern_styles.csv"), srows)

    # ---- review printout
    print("\n=== rule table (proposed seeds-style mapping; review before copying into seeds/) ===")
    for r in rule_rows:
        print(f"{r['rule']:4} {r['n_candidates']:6}  {r['proposed_style']:<58} <- {r['conditions']}")
    print("\n=== proposed styles ===")
    for s in srows:
        print(f"{s['proposed_style']:<60} cand {s['n_candidates']:6}  heritage {s['n_heritage']:5}  unesco {s['n_unesco']:4}  "
              f"before {s['before_p149_buildings']:5}\n    top: {s['top10'][:220]}")
    print(f"\n=== P149 flags ({len(flags)}) ===")
    for c in sorted(flags, key=lambda c: -c["sitelinks"])[:60]:
        print(f"  {c['qid']:<11} {c['label'][:40]:<40} sl {c['sitelinks']:3}  {c['flag']}")
    n_un = sum(1 for c in cands if not c["rule"])
    print(f"\n{len(cands)} candidates, {len(cands) - n_un} with a proposed style, {n_un} unassigned; {len(flags)} P149 flags")
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
