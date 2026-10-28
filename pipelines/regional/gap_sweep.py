"""Gap sweep over five thin areas found by the region x medium coverage audit
(data/interim/coverage_media.csv; visual-art-plan.md §2A, §2.1b, §2.2).

Gathering = tradition NODES + EVIDENCE (object counts, holding institutions,
representative works), not object completeness. This script defines a node
lexicon per area, measures each node against the museum data already on disk,
then Wikidata, then a few keyless open APIs, and reports which nodes are NEW
against everything gathered so far.

Areas (`AREA` column):
  colonial_latam   Colonial Latin American painting schools and allied arts:
                   Cusco, Quito, Lima, Potosi / Alto Peru, New Spain, casta
                   painting, enconchado, biombos, feather mosaic, retablos,
                   ex-votos, New Mexican santeros, Ayacucho, Brazilian Baroque,
                   New Granada, Guatemala, barniz de Pasto, maque, colonial silver.
  southeast_asia   Thai manuscript / temple painting and lacquer, Balinese
                   Kamasan / Ubud / Batuan painting, wayang kulit / golek /
                   klitik / beber, Thai and Khmer shadow theatre, Burmese
                   parabaik, kalaga, marionettes and lacquer, Vietnamese Dong Ho /
                   Hang Trong / Kim Hoang prints and son mai, Philippine traditions.
  east_asia_folk   Chinese New Year prints (nianhua) by centre, paper-cutting,
                   the four embroideries (Su, Xiang, Shu, Yue), minority arts
                   (Miao, Yi, Dong, Bai, Zhuang, Li, Yao, Naxi, Regong), Korean
                   minhwa, bojagi, hwagak, Hahoe masks, Japanese mingei, Otsu-e,
                   ema, Ainu, Ryukyuan bingata / bashofu / lacquer, folk textiles.
  aboriginal_aus   Bark painting by region (Western / Central / Eastern Arnhem
                   Land, Groote Eylandt, Tiwi), Western Desert (Papunya Tula,
                   Balgo, Utopia, Yuendumu, APY, Haasts Bluff), Hermannsburg,
                   Kimberley (Warmun, Wandjina, Mangkaja, riji), Aurukun,
                   rainforest shields, toas, Torres Strait masks; art centres.
  ancient_africa   Nok, Sokoto, Katsina, Igbo-Ukwu, Ife, Owo, Esie, Tsoede
                   bronzes, early Benin, Inland Niger Delta, Bankoni, Tellem,
                   Bura, Koma, Sao, Sapi, Aksum, Kerma, Napata / Meroe, Nubian
                   A/C-Group, Ballana, Christian Nubia, Great Zimbabwe,
                   Mapungubwe, Lydenburg, Swahili coast; Ethiopian icons,
                   manuscripts, healing scrolls, crosses.

Sources, in order of use:
  1. Cached museum data (no network): Met open-access CSV
     (data/raw/museums/MetObjects.csv), AIC dump (artic-api-data; a slim copy
     is cached to data/raw/regional/gap_sweep/aic_slim.jsonl.gz), Smithsonian
     Open Access (data/interim/regional/smithsonian_objects.csv, all units),
     Penn Museum CSV (all curatorial sections, incl. Egyptian = Nubia),
     Mia / Te Papa / Yale LUX caches (read through africa_oceania_targeted.py
     with its network function disabled), every cached V&A and Cleveland page
     under data/raw/regional/, Rijksmuseum LIDO slim extract
     (world_extra/rijks/records.jsonl.gz) and the East Asia sweep's object
     table (ColBase, Bunka-isan, NPM, Korean e-museum rows only).
  2. Wikidata (WDQS, one query at a time; QLever mirror as fallback):
     node QIDs by exact label, works linked to each node (P135 / P136 / P2596
     / P31 / P361 / P1269) with collection (P195) and creator (P170), artists
     linked by P135 / P463 / P1416 / P108; per-area discovery: colonial Latin
     American paintings (by holding collection country and by country of
     origin, 1521-1830), Aboriginal and Torres Strait Islander artists (P27
     Australia + P172 ethnic group) with their works' collections and art
     centres, archaeological cultures of Africa with P2596 objects, art
     movements / styles of Southeast and East Asia, UNESCO intangible-heritage
     crafts per area. Cached under data/raw/regional/gap_sweep/wikidata/.
  3. Open APIs (keyless, cached under data/raw/regional/gap_sweep/{vam,cma}/):
     V&A API v2 (q=<node term>, data_profile=full, <=3 pages, 1 req/s) and the
     Cleveland Museum of Art open-access API (q=<node term>, <=3 pages,
     ~2 req/s). Search hits pass through the same node matcher as the caches.
     The Met API is not queried: the open-access CSV already holds every Met
     record the API would return.

Checked and not used: Kluge-Ruhe Aboriginal Art Collection (UVA): kluge-ruhe.org
answers 403 even for robots.txt (stopped per project rule); National Gallery of
Australia (403) and Art Gallery of NSW (robots.txt disallows Anthropic agents):
not contacted, per the earlier sweep's findings; British Museum (robots.txt
disallows); Wereldmuseum / NMVW linked data (1.8 GB N-Triples on disk, objects
reach their keywords only through nested blank nodes; the world_cultures_extra
job owns that parse; reuse its output when it lands).

Matching: each node has an explicit-naming regex (basis "named") and/or an
inference rule (place x medium x date window, basis "inferred"; e.g. a painting
made in Cuzco 1550-1850 counts toward the Cusco School). Context / exclusion
regexes keep homonyms out (Hopi katsina vs Katsina terracottas, Kwoma bark
paintings vs Arnhem Land). Catch-all nodes ("fallback") count an object only
when no specific node of the same family matched. Photographs are dropped.

Node gain: every node is checked against the node-level names already in
data/interim/unattributed_cultures.csv, data/interim/regional/*_traditions.csv
and smithsonian_cultures.csv. new_vs_known = known (a node / culture label
matches), mentioned (only raw label strings match), or new.

Outputs (data/interim/regional/):
  gap_sweep_traditions.csv  one row per node (seed nodes, Wikidata-discovered
                            candidates, art centres): area, key, label, qid,
                            region, medium, era range, objects per source,
                            attributed share, holding institutions, sample works,
                            Wikidata evidence, new_vs_known
  gap_sweep_objects.csv     one row per object x node (museum objects and
                            Wikidata works), with match basis
  gap_sweep_sources.csv     per source: records read, matched, status

Usage: python3 pipelines/regional/gap_sweep.py [--skip-api] [--skip-wikidata]
           [--endpoint wdqs|qlever] [--sources met,aic,...] [--delay 1.0]
"""
import argparse
import collections
import csv
import glob
import gzip
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data")
RAWREG = os.path.join(DATA, "raw", "regional")
RAW = os.path.join(RAWREG, "gap_sweep")
INTERIM = os.path.join(DATA, "interim")
OUT_DIR = os.path.join(INTERIM, "regional")
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"

sys.path.insert(0, os.path.join(ROOT, "pipelines", "regional"))
import south_asia_africa_americas as saa  # noqa: E402
import africa_oceania_targeted as aot  # noqa: E402

csv.field_size_limit(1 << 30)


def log(*a):
    print(*a, file=sys.stderr, flush=True)


# ------------------------------------------------------------------ text

_TR = str.maketrans({"đ": "d", "Đ": "d", "ŋ": "ng", "Ŋ": "ng", "’": "'", "‘": "'", "ʻ": "'", "–": "-",
                     "—": "-", "ł": "l", "ø": "o", "æ": "ae", "ß": "ss"})


def fold(s):
    """casefold + strip accents (Latin only; CJK untouched)."""
    s = (s or "").translate(_TR).casefold()
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def rx(p):
    return re.compile(p) if p else None


# ------------------------------------------------------------------ node lexicon
# Patterns are written in folded form (lower case, no accents).

AU = (r"australia|aborigin|arnhem|northern territory|western australia|queensland|south australia|"
      r"new south wales|kimberley|torres strait|western desert|central desert|tiwi|yolngu|warlpiri|pintupi|"
      r"arrernte|pitjantjatjara|anmatyerr")
LATAM = (r"mexic|new spain|nueva espana|novohispan|peru|cuzco|cusco|lima\b|bolivia|potosi|alto peru|ecuador|quito|"
         r"colombia|new granada|nueva granada|bogota|guatemala|brazil|brasil|bahia|minas gerais|venezuela|"
         r"argentin|chile|paraguay|philippin|latin america|spanish colonial|viceroyalty|andean|new mexico|"
         r"puebla|oaxaca|cuba|puerto rico|dominican")
THAI = r"thai|siam|ayutthaya|rattanakosin|bangkok|lan ?na|chiang mai"
BURMA = r"burm|myanmar|mandalay|pagan\b|bagan|rangoon|yangon|shan state|konbaung|amarapura"
VIET = r"vietnam|viet nam|annam|tonkin|cochinchin|hanoi|hue\b|indochin"
BALI = r"\bbali|balinese|klungkung|gianyar|karangasem"
JAVA = r"\bjava|javanese|jawa|sunda|indonesia|surakarta|yogyakarta|cirebon|madura|lombok"
PHIL = r"philippin|filipin|luzon|mindanao|visayas|manila|ifugao|cordillera"
CHINA = r"china|chinese|qing|ming dynasty|\bmin guo|republic period|guizhou|yunnan|guangxi|hunan|sichuan|hainan"
KOREA = r"korea|joseon|choson|chosun|goryeo|조선|한국"
JAPAN = r"japan|edo period|meiji|日本|江戸|明治"
ETH = r"ethiop|abyssin|ge'?ez|amhar|gondar|tigray|tigrinya|lalibela|eritre"
NIGERIA = r"nigeria|yoruba|edo\b|benin city|kingdom of benin|niger river|lower niger"

NODES = []


def N(area, key, label, region, medium, era, pat=None, ctx=None, neg=None, inf=None, groups=None, med=None,
      date=None, fallback=False, family=None, kn=None, wd=(), api=(), parent="", qid=None, desc_ok=False):
    """area/key/label; region, nominal medium and era (begin, end);
    pat   explicit-naming regex on title / labels / place / type / medium (+ description if desc_ok)
    ctx   regex that must also match the record text (place / culture context)
    neg   regex that vetoes a match
    inf   (place regex, groups-or-None, (begin, end), medium regex-or-None): inference rule
    groups/med  object-group set or medium regex the object must satisfy (either one)
    date  (begin, end) window the object's date must overlap (undated objects pass)
    fallback/family  catch-all node counted only when no specific node of the family matched
    kn    regex for the known-node check (default: pat)
    wd    exact Wikidata labels ("label" = @en, or "label@xx")
    api   V&A / Cleveland search terms"""
    NODES.append(dict(area=area, key=key, label=label, region=region, medium=medium, era=era, pat=rx(pat),
                      ctx=rx(ctx), neg=rx(neg),
                      inf=(rx(inf[0]), set(inf[1]) if inf[1] else None, inf[2], rx(inf[3]) if len(inf) > 3 else None)
                      if inf else None,
                      groups=set(groups) if groups else None, med=rx(med), date=date, fallback=fallback,
                      family=family or key, kn=rx(kn or pat), wd=list(wd), api=list(api), parent=parent,
                      qid=qid, desc_ok=desc_ok))


PAINT = ("painting", "drawing")
SCULPT = ("sculpture",)
PS = ("painting", "drawing", "sculpture")

# ---- 1. Colonial Latin America
A = "colonial_latam"
R = "Latin America (colonial)"
N(A, "col_cusco", "Cusco School (Escuela cuzquena)", R, "painting", (1550, 1850),
  pat=r"cuzco school|cusco school|escuela cuzquen|escuela cusquen|cuzquen[oa]|cusquen[oa]|school of cuzco|school of cusco",
  inf=(r"cuzco|cusco", PAINT, (1550, 1850)), kn=r"cuzco school|cusco school|escuela cu[sz]quen|cu[sz]quen[oa]",
  family="col_peru", wd=["Cusco School", "Cuzco School", "Escuela cuzqueña@es", "Cusco school"], api=["Cuzco", "Cusco"])
N(A, "col_altoperu", "Potosi / Alto Peru (Collao) painting", R, "painting", (1550, 1850),
  pat=r"alto peru|upper peru|collao|escuela potosin|potosi school|school of potosi",
  inf=(r"bolivia|potosi|la paz|chuquisaca|sucre\b|oruro|charcas", PAINT, (1550, 1850)),
  kn=r"alto peru|upper peru|collao|potosi", family="col_peru",
  wd=["Potosí School", "Collao School", "Escuela potosina@es", "Escuela del Collao@es"], api=["Potosi", "Bolivia painting"])
N(A, "col_peru", "Viceroyalty of Peru painting (Lima and other centres)", R, "painting", (1550, 1850),
  pat=r"escuela limen|lima school|viceroyalty of peru|virreinato del peru",
  inf=(r"peru|lima\b|arequipa|ayacucho|huamanga|trujillo", PAINT, (1550, 1850)), fallback=True, family="col_peru",
  kn=r"viceroyalty of peru|lima school|peruvian colonial", wd=["Escuela limeña@es"], api=["Peru painting"])
N(A, "col_quito", "Quito School (Escuela quitena)", R, "painting; polychrome sculpture", (1550, 1850),
  pat=r"quito school|escuela quiten|quiten[oa]|school of quito|caspicara|legarda|miguel de santiago",
  inf=(r"quito|ecuador", PS, (1550, 1850)), kn=r"quito school|escuela quiten|quiten[oa]",
  wd=["Quito School", "Escuela quiteña@es", "Quito school"], api=["Quito"])
N(A, "col_nspain", "New Spain painting (Novohispanic)", R, "painting", (1521, 1821),
  pat=r"new spain|nueva espana|novohispan|viceroyalty of new spain",
  inf=(r"mexic|puebla|oaxaca|tlaxcala|guanajuato|michoacan|zacatecas", PAINT, (1521, 1821)),
  neg=r"new mexico|nuevo mexico", fallback=True, family="col_mex", kn=r"new spain|nueva espana|novohispan",
  wd=["New Spanish painting", "Novohispanic painting", "Pintura novohispana@es", "Colonial Mexican art"],
  api=["New Spain painting"])
N(A, "col_nspain_sculpt", "New Spain polychrome sculpture (estofado)", R, "sculpture", (1521, 1821),
  pat=r"estofad", inf=(r"mexic|new spain|nueva espana|puebla|oaxaca|guatemala", SCULPT, (1521, 1821)),
  neg=r"new mexico", fallback=True, family="col_mex", kn=r"estofad|novohispan sculpt",
  wd=["Estofado"], api=["estofado"])
N(A, "col_casta", "Casta painting (pintura de castas)", R, "painting", (1700, 1810),
  pat=r"pintura de castas|casta painting|casta series|cuadros? de castas|\bcastas\b|"
      r"\bde espanol y (de )?(india|negra|mestiza|mulata|morisca|castiza|albina)|\bde (mestizo|castizo|mulato|morisco|lobo|"
      r"chino|indio) y (de )?(espanola|india|mestiza|negra|mulata|loba)",
  kn=r"casta painting|pintura de castas", wd=["casta painting", "Pintura de castas@es"], api=["casta painting", "castas"])
N(A, "col_enconchado", "Enconchado (shell-inlay painting)", R, "painting", (1650, 1750), pat=r"enconchad",
  wd=["Enconchado", "enconchado@es"], api=["enconchado"])
N(A, "col_biombo", "Mexican biombos (folding screens)", R, "painting", (1600, 1800),
  pat=r"biombo|folding screen", ctx=r"mexic|new spain|nueva espana", groups=None,
  kn=r"biombo", wd=["Biombo", "biombo@es"], api=["biombo"])
N(A, "col_feather", "Mexican feather mosaic (arte plumario)", R, "featherwork", (1520, 1800),
  pat=r"feather (mosaic|painting|picture|work)|featherwork|arte plumario|plumaria|amanteca|mosaico de plumas",
  ctx=r"mexic|new spain|michoacan|aztec|nahua", date=(1500, 1850), kn=r"feather mosaic|arte plumario|amanteca",
  wd=["Feather mosaic", "Arte plumario@es", "feather work"], api=["feather mosaic"])
N(A, "col_retablo", "Retablo devotional painting (Mexico and Andes)", R, "painting (tin, panel)", (1750, 1950),
  pat=r"\bretablos?\b|lamina|painting on tin|oil on tin", ctx=r"mexic|guatemala|peru|bolivia|ecuador|colombia|latin america",
  neg=r"new mexico|nuevo mexico|ayacucho|huamanga|san marcos|cajon|spain|spanish(?!.colonial)",
  kn=r"retablo", wd=["Retablo (Latin American folk art)", "Retablo"], api=["retablo"])
N(A, "col_exvoto", "Ex-voto painting (Latin America)", R, "painting (tin)", (1700, 1950),
  pat=r"ex[- ]?votos?|exvoto|milagro painting|votive painting", ctx=LATAM, kn=r"ex-?voto",
  wd=["Ex-voto", "exvoto@es"], api=["ex-voto"])
N(A, "col_santero", "New Mexican santero tradition (retablos and bultos)", R, "painting; sculpture", (1750, 1950),
  pat=r"santero|\bbultos?\b|retablos?|\bsantos?\b|reredos", ctx=r"new mexico|nuevo mexico|santa fe|taos|rio grande|truchas|cordova",
  kn=r"santero|new mexican", wd=["Santero", "New Mexican santos", "Santos (art)"], api=["santero", "bulto"])
N(A, "col_ayacucho", "Ayacucho retablos and Huamanga alabaster (piedra de Huamanga)", R, "sculpture; folk boxes",
  (1700, 2000), pat=r"ayacucho|huamanga|san marcos box|cajon san marcos|piedra de huamanga|sanmarcos",
  kn=r"ayacucho|huamanga", wd=["Retablo ayacuchano@es", "Piedra de Huamanga@es", "Ayacucho retablo"], api=["Ayacucho", "Huamanga"])
N(A, "col_brazil", "Brazilian Baroque (Barroco mineiro, Bahia)", R, "sculpture; painting", (1650, 1830),
  pat=r"aleijadinho|ataide|barroco mineiro|mineiro baroque|brazilian baroque|ouro preto",
  inf=(r"brazil|brasil|bahia|minas gerais|pernambuco|rio de janeiro|salvador", PS + ("furniture and woodwork",), (1600, 1830)),
  kn=r"brazilian baroque|barroco mineiro|aleijadinho", wd=["Brazilian Baroque", "Barroco mineiro@pt", "Mineiro Baroque"],
  api=["Brazil baroque"])
N(A, "col_ngranada", "New Granada painting (Santafe de Bogota)", R, "painting", (1550, 1830),
  pat=r"nueva granada|new granada|santa ?fe de bogota|vasquez de arce|gregorio vasquez|figueroa workshop",
  inf=(r"colombia|bogota|popayan|tunja", PS, (1550, 1830)), kn=r"new granada|nueva granada",
  wd=["Colonial art of New Granada", "Arte colonial neogranadino@es"], api=["New Granada"])
N(A, "col_guatemala", "Guatemalan colonial sculpture and painting (Antigua)", R, "sculpture; painting", (1550, 1830),
  inf=(r"guatemala|antigua guatemala", PS, (1550, 1830)), pat=r"antigua guatemala|guatemalan colonial",
  kn=r"guatemalan colonial|antigua guatemala", wd=["Guatemalan colonial art"], api=["Guatemala colonial"])
N(A, "col_pasto", "Barniz de Pasto (mopa-mopa lacquer)", R, "lacquer", (1600, 1900),
  pat=r"barniz de pasto|mopa[- ]?mopa|pasto varnish|pasto lacquer|barniz", ctx=r"pasto|colombia|ecuador|quito|peru|andes|mopa",
  kn=r"barniz de pasto|mopa-?mopa", wd=["Barniz de Pasto", "Barniz de Pasto@es"], api=["barniz de Pasto", "mopa mopa"])
N(A, "col_maque", "Mexican lacquer (maque: Olinala, Patzcuaro, Periban)", R, "lacquer", (1550, 1900),
  pat=r"olinala|\bbateas?\b|patzcuaro|periban|uruapan|\bmaque\b|lacquer(ed)? (gourd|chest|tray)",
  ctx=r"mexic|new spain|michoacan|guerrero", inf=(r"mexic|new spain|michoacan", None, (1550, 1900), r"lacquer"),
  kn=r"\bmaque\b|olinala|mexican lacquer", wd=["Maque", "Olinalá lacquerware", "Laca mexicana@es"], api=["Olinala", "Mexican lacquer"])
N(A, "col_silver", "Viceroyalty of Peru silver (Potosi, Cusco, Lima)", R, "metalwork", (1550, 1850),
  inf=(r"peru|bolivia|potosi|cuzco|cusco|lima\b|alto peru", None, (1550, 1850), r"silver|plata"),
  pat=r"potosi silver|peruvian silver|andean silver", kn=r"peruvian silver|andean colonial silver",
  wd=["Silverwork of Potosí"], api=["Potosi silver"])
N(A, "col_talavera", "Talavera poblana (Puebla tin-glazed earthenware)", R, "ceramics", (1550, 1900),
  pat=r"talavera poblana|talavera de puebla|puebla (earthenware|maiolica|majolica|tin-glazed)",
  inf=(r"puebla", ("ceramics",), (1550, 1900)), kn=r"talavera poblana|puebla", wd=["Talavera pottery", "Talavera poblana@es"],
  api=["Talavera poblana"])
N(A, "col_andean_textile", "Colonial Andean tapestry weaving (tapices, uncu)", R, "textiles", (1550, 1830),
  inf=(r"peru|bolivia|andean|cuzco|cusco|potosi", ("textile", "costume and accessories"), (1550, 1830)),
  pat=r"colonial (andean|peruvian) (tapestry|textile)|andean colonial (tapestry|textile)", kn=r"colonial andean",
  wd=["Colonial Andean textiles"], api=["Andean tapestry colonial"])

# ---- 2. Southeast Asia
A = "southeast_asia"
R = "Southeast Asia"
N(A, "sea_thai_ms", "Thai manuscript painting (samut khoi, Phra Malai)", R, "manuscript painting", (1700, 1950),
  pat=r"samut ?(khoi|thai|khoy)|phra malai|phra ?malai|thai manuscript|traiphum|folding (book|manuscript)",
  ctx=THAI, kn=r"samut khoi|phra malai|thai manuscript", wd=["Samut khoi", "Samut thai", "Phra Malai"], api=["Phra Malai", "samut khoi"])
N(A, "sea_thai_painting", "Thai temple painting (phra bot banners, murals)", R, "painting", (1600, 1950),
  pat=r"phra bot|temple banner|banner painting|cloth painting|thai mural|thai painting",
  inf=(THAI, PAINT, (1500, 1950)), ctx=THAI, fallback=True, family="sea_thai_ms",
  kn=r"phra bot|thai (temple )?painting|thai mural", wd=["Thai art", "Thai mural painting", "Phra bot"], api=["Thai painting", "phra bot"])
N(A, "sea_thai_lacquer", "Thai gold-and-black lacquer (lai rot nam)", R, "lacquer", (1600, 1950),
  pat=r"lai ?rot ?nam|lai ?rod ?nam|lacquer", ctx=THAI, kn=r"lai rot nam|thai lacquer",
  wd=["Lai rot nam", "Thai lacquerware"], api=["lai rot nam", "Thai lacquer"])
N(A, "sea_bencharong", "Bencharong porcelain", R, "ceramics", (1700, 1900),
  pat=r"bencharong|benjarong|lai nam thong|ben?charong", kn=r"bencharong|benjarong", wd=["Bencharong", "Benjarong"],
  api=["Bencharong"])
N(A, "sea_kamasan", "Balinese Kamasan (wayang-style) painting", R, "painting", (1600, 1960),
  pat=r"kamasan|klungkung (painting|style)|langse|ider-?ider|wayang[- ]style|parba|palelintangan|calendar painting",
  ctx=BALI + r"|kamasan", kn=r"kamasan", wd=["Kamasan painting", "Kamasan"], api=["Kamasan"])
N(A, "sea_ubud", "Ubud / Pita Maha painting", R, "painting", (1930, 1970),
  pat=r"\bubud\b|pita maha|pengosekan|penestanan|young artists", ctx=BALI + r"|ubud|pita maha", kn=r"\bubud|pita maha",
  wd=["Pita Maha", "Ubud painting", "Young Artists (Bali)"], api=["Ubud", "Pita Maha"])
N(A, "sea_batuan", "Batuan painting", R, "painting", (1930, 2000), pat=r"batuan", ctx=BALI + r"|batuan", kn=r"batuan",
  wd=["Batuan painting", "Batuan style"], api=["Batuan"])
N(A, "sea_bali_painting", "Balinese painting (other)", R, "painting", (1700, 1970),
  inf=(BALI, PAINT, (1600, 1970)), fallback=True, family="sea_bali", kn=r"balinese painting", wd=["Balinese painting"],
  api=["Balinese painting"])
N(A, "sea_wayang_kulit", "Wayang kulit (shadow puppets, Java / Bali)", R, "puppets (hide)", (1500, 2000),
  pat=r"wayang kulit|wajang ko?ulit|wayang purwa|wajang poerwa|shadow (puppet|play|theatre|theater)|leather puppet|"
      r"hide puppet|wayang gedog|wayang madya|wayang sasak|wayang parwa|wayang ramayana",
  ctx=JAVA + r"|" + BALI + r"|malay|kelantan|wayang|wajang", neg=r"golek|klitik|krucil|beber|thai|siam|cambod|khmer|china|chinese|turk|karagoz",
  kn=r"wayang kulit|wajang", wd=["Wayang kulit", "Wayang"], api=["wayang kulit", "shadow puppet Java"])
N(A, "sea_wayang_golek", "Wayang golek (rod puppets, Sunda / Java)", R, "puppets (wood)", (1600, 2000),
  pat=r"wayang golek|wajang golek|wayang menak|wayang cepak|\bgolek\b|rod puppet", ctx=JAVA + r"|golek",
  kn=r"wayang golek|wajang golek", wd=["Wayang golek"], api=["wayang golek"])
N(A, "sea_wayang_klitik", "Wayang klitik / krucil (flat wooden puppets)", R, "puppets (wood)", (1600, 2000),
  pat=r"klitik|krucil|kroetjil|kruchil|wajang keroetjil", kn=r"klitik|krucil", wd=["Wayang klitik", "Wayang krucil"],
  api=["wayang klitik"])
N(A, "sea_wayang_beber", "Wayang beber (narrative scroll painting)", R, "painting (scroll)", (1600, 2000),
  pat=r"wayang beber|wajang beber", kn=r"wayang beber", wd=["Wayang beber"], api=["wayang beber"])
N(A, "sea_wayang_other", "Wayang (form unrecorded)", R, "puppets", (1500, 2000),
  pat=r"\bwayang\b|\bwajang\b", neg=r"topeng|wayang wong|wayang orang|batik", fallback=True, family="sea_wayang",
  kn=r"\bwayang\b", wd=[], api=["wayang"])
for _k in ("sea_wayang_kulit", "sea_wayang_golek", "sea_wayang_klitik", "sea_wayang_beber"):
    NODES[[n["key"] for n in NODES].index(_k)]["family"] = "sea_wayang"
N(A, "sea_topeng", "Topeng masks (Java / Bali masked dance)", R, "masks", (1600, 2000),
  pat=r"topeng|wayang topeng|wayang wong|barong|rangda|\bdance mask", ctx=JAVA + r"|" + BALI + r"|topeng",
  kn=r"topeng", wd=["Topeng", "Wayang topeng"], api=["topeng"])
N(A, "sea_thai_nang", "Thai shadow theatre (nang yai, nang talung)", R, "puppets (hide)", (1700, 2000),
  pat=r"nang ?yai|nang ?talung|nang ?ta?lung|shadow (puppet|play|theatre|figure)", ctx=THAI + r"|nang yai|nang talung",
  kn=r"nang yai|nang talung", wd=["Nang yai", "Nang talung"], api=["nang yai"])
N(A, "sea_sbek", "Khmer shadow theatre (sbek thom)", R, "puppets (hide)", (1700, 2000),
  pat=r"sbek|nang sbek|shadow (puppet|play|theatre|figure)", ctx=r"cambod|khmer|sbek", kn=r"sbek",
  wd=["Sbek thom", "Sbek Thom"], api=["sbek"])
N(A, "sea_burma_puppet", "Burmese marionettes (yoke thé)", R, "puppets", (1750, 2000),
  pat=r"yoke ?th[ea]|marionette|string puppet|\bpuppets?\b", ctx=BURMA, kn=r"yoke the|burmese marionette",
  wd=["Yoke thé", "Burmese marionette"], api=["Burmese marionette", "Burma puppet"])
N(A, "sea_parabaik", "Burmese parabaik manuscript painting", R, "manuscript painting", (1750, 1950),
  pat=r"parabaik|parabeik|para-?baik|folding (book|manuscript)|manuscript", ctx=BURMA + r"|parabaik",
  kn=r"parabaik|parabeik", wd=["Parabaik"], api=["parabaik"])
N(A, "sea_burma_painting", "Burmese court painting", R, "painting", (1750, 1950),
  inf=(BURMA, PAINT, (1700, 1960)), fallback=True, family="sea_parabaik", kn=r"burmese painting",
  wd=["Burmese painting"], api=["Burmese painting"])
N(A, "sea_kalaga", "Burmese kalaga (sequined tapestries)", R, "textiles", (1800, 2000),
  pat=r"kalaga|shwe ?chi ?doe|sequin(n)?ed (tapestry|hanging)", ctx=BURMA + r"|kalaga", kn=r"kalaga",
  wd=["Kalaga", "Shwe chi doe"], api=["kalaga"])
N(A, "sea_burma_lacquer", "Burmese lacquer (yun, Bagan)", R, "lacquer", (1700, 2000),
  pat=r"lacquer|\byun\b|thitsi|hsun ?ok|kun-?it|thayo|shwe-?zawa", ctx=BURMA, kn=r"burmese lacquer|\byun\b|shwe-?zawa",
  wd=["Burmese lacquerware", "Shwe-zawa", "Yun lacquerware"], api=["Burmese lacquer"])
N(A, "sea_burma_silver", "Burmese silverwork", R, "metalwork", (1800, 1950),
  inf=(BURMA, None, (1750, 1960), r"silver"), kn=r"burmese silver", wd=["Burmese silverware"], api=["Burmese silver"])
N(A, "sea_dongho", "Dong Ho woodblock prints", R, "prints", (1600, 2000), pat=r"dong ?ho\b|dongho",
  ctx=VIET + r"|dong ho|bac ninh", kn=r"dong ho", wd=["Đông Hồ painting", "Dong Ho painting", "Tranh Đông Hồ@vi"],
  api=["Dong Ho"])
N(A, "sea_hangtrong", "Hang Trong woodblock prints", R, "prints", (1700, 2000), pat=r"hang ?trong", kn=r"hang trong",
  wd=["Hàng Trống painting", "Tranh Hàng Trống@vi"], api=["Hang Trong"])
N(A, "sea_kimhoang", "Kim Hoang and Lang Sinh prints", R, "prints", (1700, 2000), pat=r"kim ?hoang|lang ?sinh",
  ctx=VIET + r"|kim hoang|lang sinh", kn=r"kim hoang|lang sinh",
  wd=["Kim Hoàng painting", "Làng Sình painting", "Tranh Kim Hoàng@vi", "Tranh làng Sình@vi"], api=["Kim Hoang"])
N(A, "sea_viet_print", "Vietnamese folk woodblock prints (other)", R, "prints", (1700, 2000),
  pat=r"woodblock|woodcut|new year (print|picture)|\bprint\b|tranh", ctx=VIET, groups=("print", "painting", "other"),
  fallback=True, family="sea_dongho", kn=r"vietnamese (folk )?(woodblock|print)", wd=["Vietnamese woodblock printing"],
  api=["Vietnamese woodblock"])
for _k in ("sea_hangtrong", "sea_kimhoang"):
    NODES[[n["key"] for n in NODES].index(_k)]["family"] = "sea_dongho"
N(A, "sea_sonmai", "Vietnamese lacquer painting (son mai)", R, "lacquer painting", (1925, 2000),
  pat=r"son ?mai|lacquer", ctx=VIET + r"|son mai", kn=r"son mai|vietnamese lacquer", wd=["Sơn mài", "Son mai"],
  api=["son mai"])
N(A, "sea_viet_painting", "Vietnamese painting (Nguyen court, silk, Indochina school)", R, "painting", (1800, 1960),
  inf=(VIET, PAINT, (1700, 1960)), fallback=True, family="sea_viet_painting", kn=r"vietnamese painting|indochina school",
  wd=["Vietnamese painting", "École des Beaux-Arts de l'Indochine"], api=["Vietnamese painting"])
N(A, "sea_ph_ivory", "Hispano-Philippine ivory santos", R, "sculpture (ivory)", (1590, 1900),
  inf=(PHIL, None, (1580, 1900), r"ivory"), pat=r"hispano-?philippine|indo-?portuguese.*philippin|filipino ivory|philippine ivory",
  kn=r"hispano-?philippine|philippine ivory", wd=["Hispano-Philippine ivory", "Philippine ivory"], api=["Philippine ivory"])
N(A, "sea_ph_santos", "Philippine wooden santos and colonial religious painting", R, "sculpture; painting", (1600, 1950),
  pat=r"\bsantos?\b|santo nino|virgin|saint|crucifix|retablo|religious", ctx=PHIL, neg=r"ivory|bulul|ifugao",
  groups=PS, kn=r"philippine santo|santo nino", wd=["Santo (Philippines)", "Santos of the Philippines"], api=["Philippine santo"])
N(A, "sea_ph_bulul", "Ifugao bulul (granary figures)", R, "sculpture", (1500, 2000), pat=r"bulul|bulol|bul-ul|\bhipag\b|punamhan",
  kn=r"bulul|bulol", wd=["Bulul"], api=["bulul"])
N(A, "sea_ph_okir", "Maranao okir and sarimanok", R, "woodcarving; metalwork", (1700, 2000),
  pat=r"\bokir|okkil|sarimanok|maranao|torogan|lanao", kn=r"okir|sarimanok|maranao", wd=["Okir", "Sarimanok"],
  api=["Maranao", "sarimanok"])
N(A, "sea_ph_tnalak", "T'boli t'nalak (abaca ikat)", R, "textiles", (1800, 2000), pat=r"t'?nalak|tinalak|t'?boli|tboli",
  kn=r"t'?nalak|t'?boli", wd=["T'nalak", "Tʼnalak"], api=["T'boli", "tnalak"])
N(A, "sea_ph_tipos", "Tipos del Pais and Letras y figuras (Philippine colonial painting)", R, "painting", (1820, 1900),
  pat=r"tipos del pais|letras y figuras|damian domingo|justiniano asuncion|jose honorato lozano|lozano album",
  kn=r"tipos del pais|letras y figuras", wd=["Tipos del País", "Letras y figuras"], api=["Tipos del Pais", "letras y figuras"])
N(A, "sea_ph_textile", "Philippine weaving (pina, Yakan, Kalinga, Ifugao)", R, "textiles", (1800, 2000),
  pat=r"pina (cloth|fib|fabric)|\bpina\b|yakan|kalinga|ifugao (textile|blanket|skirt)|inabel|abel iloko|habol|b'laan|bagobo",
  ctx=PHIL + r"|yakan|kalinga|bagobo|pina", groups=("textile", "costume and accessories", "other"),
  kn=r"\bpina\b|yakan|kalinga|bagobo|inabel", wd=["Piña", "Inabel", "Yakan weaving"], api=["pina cloth", "Yakan"])

# ---- 3. East Asian folk and minority arts
A = "east_asia_folk"
R = "East Asia"
N(A, "ea_nianhua", "Chinese New Year prints (nianhua)", R, "prints", (1600, 1950),
  pat=r"nianhua|nian hua|new year('?s)? (picture|print|painting)|年画|年畫|door gods?|門神|门神|kitchen god|zao ?jun|"
      r"zaojun|灶君|灶神|paper gods?|zhima|紙馬|纸马|god of wealth print",
  ctx=CHINA + r"|年画|年畫|門神|门神|灶|纸马|紙馬", neg=r"japan|ukiyo|vietnam|tobacco|kinney", fallback=True, family="ea_nianhua",
  kn=r"nianhua|new year print|年画|年畫", wd=["Nianhua", "Chinese New Year painting", "年画@zh"], api=["New Year print China", "nianhua", "door god"])
N(A, "ea_yangliuqing", "Yangliuqing New Year prints (Tianjin)", R, "prints", (1600, 1950),
  pat=r"yang ?liu ?qing|yang-liu-ch'?ing|楊柳青|杨柳青", family="ea_nianhua", kn=r"yangliuqing|楊柳青|杨柳青",
  wd=["Yangliuqing woodblock New Year paintings", "Yangliuqing", "杨柳青木版年画@zh"], api=["Yangliuqing"])
N(A, "ea_taohuawu", "Taohuawu (Suzhou) prints", R, "prints", (1600, 1900),
  pat=r"taohuawu|tao ?hua ?wu|桃花塢|桃花坞|\bgusu\b|姑蘇|姑苏|suzhou (print|woodblock|woodcut|single[- ]sheet)",
  family="ea_nianhua", kn=r"taohuawu|桃花塢|桃花坞|suzhou print", wd=["Taohuawu woodblock New Year pictures", "桃花坞木版年画@zh"],
  api=["Taohuawu", "Suzhou print"])
N(A, "ea_weifang", "Weifang / Yangjiabu New Year prints", R, "prints", (1600, 1950),
  pat=r"weifang|yangjiabu|yang ?jia ?bu|楊家埠|杨家埠|濰縣|潍县|wei ?xian", family="ea_nianhua", kn=r"weifang|yangjiabu|楊家埠|杨家埠",
  wd=["Yangjiabu woodblock New Year pictures", "杨家埠木版年画@zh", "Weifang kite"], api=["Yangjiabu", "Weifang"])
N(A, "ea_zhuxianzhen", "Zhuxianzhen New Year prints (Kaifeng)", R, "prints", (1500, 1950), pat=r"zhuxian|朱仙鎮|朱仙镇",
  family="ea_nianhua", kn=r"zhuxian", wd=["Zhuxianzhen woodblock New Year pictures", "朱仙镇木版年画@zh"], api=["Zhuxianzhen"])
N(A, "ea_mianzhu", "Mianzhu New Year prints (Sichuan)", R, "prints", (1600, 1950), pat=r"mianzhu|綿竹|绵竹",
  family="ea_nianhua", kn=r"mianzhu", wd=["Mianzhu New Year pictures", "绵竹年画@zh"], api=["Mianzhu"])
N(A, "ea_wuqiang", "Wuqiang New Year prints (Hebei)", R, "prints", (1600, 1950), pat=r"wuqiang|武強|武强", family="ea_nianhua",
  kn=r"wuqiang", wd=["Wuqiang New Year pictures", "武强年画@zh"], api=["Wuqiang"])
N(A, "ea_papercut", "Chinese paper-cutting (jianzhi)", R, "paper-cut", (1700, 2000),
  pat=r"paper[- ]?cut|cut[- ]paper|jianzhi|jian zhi|剪纸|剪紙|窗花|window flower|chuang ?hua",
  ctx=CHINA + r"|剪纸|剪紙|窗花", neg=r"silhouette|scherenschnitt|polish|wycinanki|japan|mexic|papel picado",
  kn=r"paper-?cut|jianzhi|剪纸|剪紙", wd=["Chinese paper cutting", "Paper cutting", "剪纸@zh"], api=["Chinese paper cut", "papercut China"])
N(A, "ea_suxiu", "Suzhou embroidery (Su xiu)", R, "embroidery", (1600, 2000),
  pat=r"su ?xiu|蘇繡|苏绣|suzhou embroider|gu embroider|顧繡|顾绣|gu family embroider", kn=r"su ?xiu|蘇繡|苏绣|suzhou embroider",
  wd=["Suzhou embroidery", "苏绣@zh"], api=["Suzhou embroidery"])
N(A, "ea_xiangxiu", "Hunan embroidery (Xiang xiu)", R, "embroidery", (1800, 2000),
  pat=r"xiang ?xiu|湘繡|湘绣|hunan embroider|changsha embroider", kn=r"xiang ?xiu|湘繡|湘绣|hunan embroider",
  wd=["Hunan embroidery", "湘绣@zh", "Xiang embroidery"], api=["Hunan embroidery"])
N(A, "ea_shuxiu", "Sichuan embroidery (Shu xiu)", R, "embroidery", (1800, 2000),
  pat=r"shu ?xiu|蜀繡|蜀绣|sichuan embroider|chengdu embroider|szechwan embroider", kn=r"shu ?xiu|蜀繡|蜀绣|sichuan embroider",
  wd=["Shu embroidery", "蜀绣@zh", "Sichuan embroidery"], api=["Sichuan embroidery"])
N(A, "ea_yuexiu", "Cantonese embroidery (Yue xiu / Guangxiu)", R, "embroidery", (1700, 2000),
  pat=r"yue ?xiu|guang ?xiu|粵繡|粤绣|廣繡|广绣|canton(ese)? (embroider|shawl)|guangdong embroider|chaozhou embroider|chao ?xiu|潮繡|潮绣",
  kn=r"yue ?xiu|guang ?xiu|粵繡|粤绣|cantonese embroider", wd=["Guangdong embroidery", "粤绣@zh", "Cantonese embroidery"],
  api=["Canton embroidery", "Cantonese shawl"])
N(A, "ea_miao_textile", "Miao (Hmong) textiles: embroidery, batik, pleated skirts", R, "textiles; costume", (1800, 2000),
  pat=r"\bmiao\b|\bhmong\b|\bmeo\b|\bmong (njua|leng|daw)|苗族|苗绣|苗繡", groups=("textile", "costume and accessories", "other"),
  neg=r"dong qichang|wen miao|miao ?fu|miaofeng|\bmiao (shan|ying)", kn=r"\bmiao\b|\bhmong\b|苗族",
  wd=["Miao embroidery", "Hmong textile art", "Miao people"], api=["Miao", "Hmong"])
N(A, "ea_miao_silver", "Miao silverwork", R, "metalwork; jewellery", (1800, 2000),
  pat=r"\bmiao\b|\bhmong\b|苗族|苗银|苗銀", groups=("jewellery and ornament", "metalwork"), med=r"silver",
  neg=r"dong qichang|wen miao", kn=r"miao silver|苗银|苗銀", wd=["Miao silver ornaments", "苗族银饰@zh"], api=["Miao silver"])
N(A, "ea_yi", "Yi (Nuosu) lacquerware and textiles", R, "lacquer; textiles", (1800, 2000),
  pat=r"nuosu|\byi (people|nationality|minority|lacquer|ethnic)|\blolo\b|liangshan|彝族", kn=r"nuosu|\byi people|彝族",
  wd=["Yi lacquerware", "Nuosu", "Yi people"], api=["Nuosu", "Yi lacquer"])
N(A, "ea_dong", "Dong (Kam) textiles", R, "textiles", (1800, 2000),
  pat=r"\bdong (people|minority|nationality|ethnic|embroider|textile|jacket|baby carrier|weav)|\bkam people|侗族|侗锦|侗錦",
  kn=r"\bdong people|侗族|kam people", wd=["Dong brocade", "Dong people", "侗锦@zh"], api=["Dong minority textile"])
N(A, "ea_bai", "Bai tie-dye (zharan, Dali)", R, "textiles (resist-dyed)", (1800, 2000),
  pat=r"zha ?ran|扎染|\bbai (people|minority|nationality|tie)|dali tie|tie-?dye", ctx=r"yunnan|dali|\bbai\b|扎染|白族",
  kn=r"zha ?ran|扎染|bai tie|白族", wd=["Bai tie-dye", "Bai tie-dyeing technique", "白族扎染技艺@zh"], api=["Bai tie-dye", "Yunnan tie-dye"])
N(A, "ea_zhuang", "Zhuang brocade (zhuangjin)", R, "textiles", (1800, 2000),
  pat=r"zhuang ?jin|zhuang (brocade|textile|people|minority)|壮锦|壯錦|壮族", kn=r"zhuang",
  wd=["Zhuang brocade", "壮锦@zh"], api=["Zhuang brocade"])
N(A, "ea_li", "Li textiles (Hainan)", R, "textiles", (1800, 2000),
  pat=r"\bli (people|minority|textile|ethnic|tribe|weav)|hainan (textile|weav|li\b)|黎锦|黎錦|黎族", kn=r"\bli people|黎锦|黎族|hainan",
  wd=["Li brocade", "Li textile techniques", "黎锦@zh"], api=["Hainan Li textile"])
N(A, "ea_yao", "Yao (Mien) embroidery and ritual paintings", R, "textiles; painting", (1800, 2000),
  pat=r"\byao (people|mien|ritual|embroider|minority|tribe|taoist|textile|costume)|\bmien\b|iu ?mien|瑶族|瑤族",
  kn=r"\byao (people|mien)|\bmien\b|瑶族|瑤族", wd=["Yao people", "Mien people", "Yao ritual painting"], api=["Yao Mien"])
N(A, "ea_naxi", "Naxi Dongba manuscripts and painting", R, "manuscripts; painting", (1600, 2000),
  pat=r"\bnaxi\b|\bnakhi\b|dongba|tomba|東巴|东巴|纳西|納西", kn=r"naxi|nakhi|dongba", wd=["Dongba", "Naxi script", "Dongba manuscript"],
  api=["Naxi", "Dongba"])
N(A, "ea_regong", "Regong (Rebkong) art", R, "painting (thangka); sculpture", (1500, 2000),
  pat=r"regong|rebkong|repkong|rebgong|热贡|熱貢|tongren (county|thangka)", kn=r"regong|rebkong|热贡|熱貢",
  wd=["Regong arts", "Regong art", "热贡艺术@zh"], api=["Regong", "Rebkong"])
N(A, "ea_minhwa", "Korean minhwa folk painting", R, "painting", (1700, 1950),
  pat=r"minhwa|min-hwa|민화|民畫|民画|chaek ?geori|ch'?aekk?ori|chaekgado|책거리|책가도|munja-?do|문자도|文字圖|"
      r"character (painting|ideograph)|hojak|호작도|까치호랑이|magpie and tiger|tiger and magpie|sipjangsaeng|십장생|"
      r"ten symbols of longevity|bookshelf|scholar'?s (accoutrements|objects) (screen|painting)|ch'?aekkado",
  ctx=KOREA + r"|민화|책거리|문자도|minhwa", kn=r"minhwa|민화|chaekgeori|munjado|책거리|문자도",
  wd=["Minhwa", "Chaekgeori", "Munjado", "민화@ko"], api=["minhwa", "Korean folk painting", "chaekgeori"])
N(A, "ea_bojagi", "Korean bojagi (wrapping cloths)", R, "textiles", (1700, 2000),
  pat=r"bojagi|pojagi|po-?jagi|보자기|褓|jogakbo|조각보|wrapping cloth", ctx=KOREA + r"|보자기|bojagi|pojagi|조각보",
  kn=r"bojagi|pojagi|보자기|조각보", wd=["Bojagi", "보자기@ko"], api=["bojagi", "pojagi", "Korean wrapping cloth"])
N(A, "ea_hwagak", "Korean hwagak (painted ox-horn)", R, "decorative arts (ox horn)", (1700, 1950),
  pat=r"hwagak|hwagag|hwa-?gak|화각|華角|ox[- ]?horn", ctx=KOREA + r"|화각|hwagak", kn=r"hwagak|화각|華角",
  wd=["Hwagak", "화각공예@ko"], api=["hwagak", "Korean ox horn"])
N(A, "ea_hahoe", "Korean folk masks (Hahoe tal)", R, "masks", (1100, 2000),
  pat=r"hahoe|하회|\btal\b|mask|탈", ctx=KOREA + r"|하회|hahoe", groups=("mask", "sculpture", "other"),
  kn=r"hahoe|하회", wd=["Hahoe mask", "Hahoetal", "하회탈@ko"], api=["Hahoe mask", "Korean mask"])
N(A, "ea_mingei", "Japanese mingei (folk-craft) movement", R, "ceramics; textiles; prints", (1920, 1990),
  pat=r"mingei|民芸|民藝|folk[- ]craft movement|hamada shoji|shoji hamada|kawai kanjiro|kanjiro kawai|serizawa|"
      r"munakata shiko|shiko munakata|yanagi soetsu|soetsu yanagi|tomimoto kenkichi|kenkichi tomimoto|"
      r"funaki|bernard leach|shimaoka tatsuzo|tatsuzo shimaoka|mashiko",
  kn=r"mingei|民芸|民藝", wd=["Mingei", "Mingei movement", "民藝運動@ja"], api=["mingei", "Hamada Shoji", "Mashiko"])
N(A, "ea_otsue", "Otsu-e (Otsu folk painting)", R, "painting", (1620, 1900),
  pat=r"\botsu[- ]?e\b|大津絵|大津繪|otsu (painting|picture)", kn=r"otsu-?e|大津絵", wd=["Ōtsu-e", "Otsu-e", "大津絵@ja"],
  api=["Otsu-e", "Otsu painting"])
N(A, "ea_ema", "Ema (votive plaques)", R, "painting (votive)", (1500, 1950),
  pat=r"絵馬|\bema\b.{0,40}(votive|plaque|tablet|shrine)|(votive|shrine) (plaque|tablet|painting).{0,40}\bema\b|\(ema\)|^ema\b|"
      r"votive (horse )?(plaque|tablet|picture)",
  ctx=JAPAN + r"|絵馬|shrine", neg=r"asmat|kinney|tobacco", kn=r"\bema\b|絵馬", wd=["Ema (Shinto)", "Ema", "絵馬@ja"],
  api=["ema votive", "votive plaque Japan"])
N(A, "ea_ainu", "Ainu textiles and carving (attush, ruunpe, ikupasuy)", R, "textiles; woodcarving", (1700, 2000),
  pat=r"\bainu\b|アイヌ|attu?sh?\b|attus|ruunpe|chikarkarpe|kaparamip|ikupasuy|ikubashui|ikupasui|イクパスイ|アットゥシ|"
      r"\bezo\b|蝦夷|hokkaido (textile|robe|carving)", neg=r"tainui|maori", kn=r"\bainu\b|アイヌ",
  wd=["Ainu art", "Ainu people", "Attus", "Ikupasuy"], api=["Ainu"])
N(A, "ea_bingata", "Ryukyuan bingata (stencil-dyed textiles)", R, "textiles (stencil-dyed)", (1600, 2000),
  pat=r"bingata|紅型|binngata", kn=r"bingata|紅型", wd=["Bingata", "紅型@ja"], api=["bingata"])
N(A, "ea_ryukyu_textile", "Ryukyuan weaving (bashofu, kasuri, Shuri)", R, "textiles", (1600, 2000),
  pat=r"basho[- ]?fu|芭蕉布|琉球絣|shuri|kumejima|miyako jofu|yaeyama|ryukyu kasuri", ctx=r"ryukyu|okinawa|琉球|沖縄|basho|芭蕉|shuri|kumejima|miyako|yaeyama",
  inf=(r"ryukyu|okinawa|琉球|沖縄", ("textile", "costume and accessories"), (1500, 2000)),
  neg=r"bingata|紅型", kn=r"bashofu|basho-fu|芭蕉布|ryukyu(an)? (textile|weav)", wd=["Bashōfu", "Bashofu", "芭蕉布@ja", "Ryukyu kasuri"],
  api=["bashofu", "Okinawa textile"])
N(A, "ea_ryukyu_lacquer", "Ryukyu lacquer", R, "lacquer", (1500, 1900),
  inf=(r"ryukyu|okinawa|琉球|沖縄", None, (1400, 1950), r"lacquer|漆|urushi|raden|chinkin"),
  pat=r"ryukyu(an)? lacquer|琉球漆器", kn=r"ryukyu(an)? lacquer|琉球漆器", wd=["Ryukyu lacquerware", "琉球漆器@ja"], api=["Ryukyu lacquer"])
N(A, "ea_japan_folk_textile", "Japanese folk textiles (tsutsugaki, sashiko, kogin, boro, sakiori)", R, "textiles", (1700, 1950),
  pat=r"tsutsugaki|筒描|sashiko|刺し子|刺子|kogin|こぎん|\bboro\b|sakiori|裂織|katazome|yogi\b|furoshiki|noren|hishizashi|"
      r"aizome|indigo[- ]dyed.*(futon|cover)", ctx=JAPAN + r"|tsutsugaki|sashiko|kogin|筒描|刺し子",
  kn=r"tsutsugaki|sashiko|kogin|\bboro\b|sakiori", wd=["Tsutsugaki", "Sashiko", "Kogin-zashi", "Boro (textile)", "Sakiori"],
  api=["tsutsugaki", "sashiko", "boro textile"])

# ---- 4. Aboriginal Australian and Torres Strait Islander art
A = "aboriginal_aus"
R = "Australia (Aboriginal and Torres Strait Islander)"
N(A, "au_bark_west", "Western Arnhem Land bark painting (Kunwinjku, Oenpelli)", R, "bark painting", (1880, 2020),
  pat=r"kunwinjku|gunwinggu|gunwinjgu|gunwinjku|oenpelli|gunbalanya|kunbarlang|croker island|goulburn island|minjilang|"
      r"x-?ray (style|painting)|mimih?\b|western arnhem", ctx=AU + r"|oenpelli|kunwinjku|gunwinggu", family="au_bark",
  kn=r"western arnhem|kunwinjku|gunwinggu|oenpelli", wd=["Kunwinjku art", "X-ray art", "Mimi spirits"], api=["Oenpelli", "Kunwinjku"])
N(A, "au_bark_central", "Central Arnhem Land bark painting (Maningrida, Ramingining, Milingimbi)", R, "bark painting",
  (1920, 2020), pat=r"maningrida|ramingining|milingimbi|burarra|rembarrnga|kuninjku|kune\b|djinang|ganalbingu|yan-?nhangu|"
      r"central arnhem|bula'?bula|ndjebbana|liverpool river", ctx=AU + r"|maningrida|ramingining|milingimbi", family="au_bark",
  kn=r"central arnhem|maningrida|ramingining|milingimbi", wd=["Maningrida Arts & Culture", "Bula'bula Arts", "Ramingining Artists"],
  api=["Maningrida", "Ramingining", "Milingimbi"])
N(A, "au_bark_east", "Eastern Arnhem Land (Yolngu) bark painting (Yirrkala, Galiwin'ku)", R, "bark painting", (1930, 2020),
  pat=r"yirrkala|yolngu|galiwin'?ku|elcho island|gapuwiyak|buku-?larrnggay|dhalwangu|gumatj|rirratjingu|madarrpa|manggalili|"
      r"djapu|marrakulu|wangurri|djambarrpuyngu|gupapuyngu|east(ern)? arnhem|north[- ]?east arnhem|larrakitj|yirritja|dhuwa",
  ctx=AU + r"|yirrkala|yolngu|galiwin", family="au_bark", kn=r"yolngu|yirrkala|eastern arnhem|east arnhem",
  wd=["Yolngu art", "Buku-Larrnggay Mulka Centre", "Yirrkala bark petitions", "Larrakitj"], api=["Yirrkala", "Yolngu"])
N(A, "au_groote", "Groote Eylandt bark painting (Anindilyakwa)", R, "bark painting", (1920, 2020),
  pat=r"groote|anindilyakwa|angurugu|umbakumba|bickerton island", family="au_bark", kn=r"groote|anindilyakwa",
  wd=["Anindilyakwa Arts"], api=["Groote Eylandt"])
N(A, "au_bark_other", "Arnhem Land bark painting (region unrecorded)", R, "bark painting", (1880, 2020),
  pat=r"bark painting|painting on bark|on (eucalyptus |stringybark )?bark|stringybark|bark-paintings", ctx=AU,
  neg=r"kwoma|sepik|papua|new guinea|maprik|abelam|yinibu|amazon|tapa|mexic|amate", fallback=True, family="au_bark",
  kn=r"bark painting|arnhem land", wd=["Bark painting", "Australian Aboriginal bark painting"], api=["bark painting"])
N(A, "au_tiwi", "Tiwi art (pukumani poles, ochre painting)", R, "sculpture; painting", (1900, 2020),
  pat=r"\btiwi\b|pukumani|tutini|bathurst island|melville island|jilamara|munupi|ngaruwanajirri|nguiu|wurrumiyanga|milikapiti|pirlangimpi",
  kn=r"\btiwi\b|pukumani", wd=["Tiwi art", "Pukumani pole", "Jilamara Arts and Crafts", "Munupi Arts"], api=["Tiwi", "pukumani"])
N(A, "au_papunya", "Papunya Tula (Western Desert painting)", R, "painting (acrylic)", (1971, 2020),
  pat=r"papunya|tula artists|walungurru|kintore|kiwirrkura|kiwirrkurra|pintupi", ctx=AU + r"|papunya", family="au_wd",
  kn=r"papunya", wd=["Papunya Tula", "Papunya Tula Artists", "Western Desert art movement"], api=["Papunya"])
N(A, "au_balgo", "Balgo (Warlayirti Artists)", R, "painting (acrylic)", (1980, 2020),
  pat=r"balgo|wirrimanu|warlayirti|kukatja", family="au_wd", kn=r"balgo|warlayirti", wd=["Warlayirti Artists", "Balgo"],
  api=["Balgo"])
N(A, "au_utopia", "Utopia (Anmatyerre / Alyawarr batik and painting)", R, "painting; batik", (1977, 2020),
  pat=r"\butopia\b|anmatyerr|alyawarr|alhalkere|kngwarreye|petyarre|kemarre", ctx=AU + r"|anmatyerr|alyawarr|kngwarreye",
  neg=r"thomas more|morris|utopian|socialist", family="au_wd", kn=r"\butopia\b|anmatyerr|alyawarr",
  wd=["Utopia (Northern Territory)", "Utopia Women's Batik Group"], api=["Utopia Aboriginal", "Anmatyerre"])
N(A, "au_yuendumu", "Yuendumu / Lajamanu (Warlpiri: Warlukurlangu, Warnayaka)", R, "painting (acrylic)", (1983, 2020),
  pat=r"yuendumu|warlukurlangu|warlpiri|walbiri|lajamanu|warnayaka|willowra|nyirripi", family="au_wd",
  kn=r"yuendumu|warlpiri|warlukurlangu", wd=["Warlukurlangu Artists", "Warlpiri art", "Yuendumu Doors"], api=["Yuendumu", "Warlpiri"])
N(A, "au_apy", "APY / Ngaanyatjarra Lands art centres (Ernabella, Tjala, Spinifex, Tjanpi)", R, "painting; batik; fibre",
  (1948, 2020), pat=r"ernabella|pukatja|tjala arts|\btjala\b|amata|pitjantjatjara|yankunytjatjara|anangu|spinifex arts|tjanpi|"
      r"ngaanyatjarra|warakurna|irrunytju|kaltjiti|indulkana|iwantja|mimili|tjungu|ninuku|papulankutja|blackstone|tjarlirli|"
      r"kayili|minyma|apy lands", ctx=AU + r"|pitjantjatjara|ernabella|anangu|ngaanyatjarra", family="au_wd",
  kn=r"ernabella|pitjantjatjara|apy|anangu|ngaanyatjarra|spinifex", wd=["Ernabella Arts", "Tjala Arts", "Spinifex Arts Project",
                                                                         "Tjanpi Desert Weavers", "APY Art Centre Collective"],
  api=["Ernabella", "Pitjantjatjara"])
N(A, "au_haasts", "Haasts Bluff (Ikuntji Artists)", R, "painting (acrylic)", (1992, 2020), pat=r"haasts bluff|ikuntji",
  family="au_wd", kn=r"haasts bluff|ikuntji", wd=["Ikuntji Artists", "Haasts Bluff"], api=["Haasts Bluff"])
N(A, "au_western_desert", "Western / Central Desert painting (other)", R, "painting (acrylic)", (1971, 2020),
  pat=r"western desert|central desert|luritja|dot painting|dreaming|tjukurrpa|jukurrpa|acrylic (on|polymer).{0,30}(canvas|linen|board)",
  ctx=AU, neg=r"arnhem|yolngu|tiwi|kimberley|warmun|hermannsburg|torres", fallback=True, family="au_wd",
  kn=r"western desert|central desert", wd=["Western Desert art", "Indigenous Australian art"], api=["Western Desert"])
N(A, "au_hermannsburg", "Hermannsburg watercolour school (Namatjira and followers)", R, "watercolour", (1934, 2020),
  pat=r"hermannsburg|ntaria|namatjira|pareroultja|raberaba|inkamala|ebatarinja|arrernte (watercolou?r|landscape)",
  groups=("painting", "drawing", "other", "print"), kn=r"hermannsburg|namatjira",
  wd=["Hermannsburg School", "Hermannsburg school", "Namatjira"], api=["Hermannsburg", "Namatjira"])
N(A, "au_hermannsburg_pottery", "Hermannsburg Potters", R, "ceramics", (1990, 2020),
  pat=r"hermannsburg|ntaria", groups=("ceramics",), kn=r"hermannsburg potter", wd=["Hermannsburg Potters"],
  api=["Hermannsburg Potters"])
N(A, "au_warmun", "Warmun / East Kimberley (Gija) painting", R, "painting (ochre)", (1975, 2020),
  pat=r"warmun|turkey creek|\bgija\b|\bkija\b|jirrawun|rover thomas|queenie mckenzie|paddy jaminji|freddie timms|"
      r"east kimberley|kununurra|waringarri|mirriwoong|miriwoong", kn=r"warmun|gija|kija|turkey creek|east kimberley",
  wd=["Warmun Art Centre", "Waringarri Aboriginal Arts", "Jirrawun Arts"], api=["Warmun", "Turkey Creek"])
N(A, "au_wandjina", "Wandjina art (Mowanjum: Worrorra, Ngarinyin, Wunambal)", R, "painting; rock art", (1950, 2020),
  pat=r"wandjina|wanjina|mowanjum|worrorra|worora|ngarinyin|ungarinyin|wunambal|kalumburu|gwion", kn=r"wandjina|wanjina|mowanjum",
  wd=["Wandjina", "Mowanjum Art and Culture Centre"], api=["Wandjina"])
N(A, "au_mangkaja", "Fitzroy Crossing (Mangkaja Arts)", R, "painting; fibre", (1980, 2020),
  pat=r"mangkaja|fitzroy crossing|wangkajunga|walmajarri|bunuba|gooniyandi|marnin studio", kn=r"mangkaja|fitzroy crossing",
  wd=["Mangkaja Arts"], api=["Mangkaja", "Fitzroy Crossing"])
N(A, "au_riji", "Kimberley pearl-shell ornaments (riji, jakuli)", R, "carved pearl shell", (1850, 2020),
  pat=r"\briji\b|jakuli|lonka ?lonka|pearl[- ]?shell (pendant|ornament|plaque)|engraved pearl", ctx=AU + r"|riji|broome|bardi",
  neg=r"torres|new guinea|papua|kina", kn=r"riji|jakuli|pearl shell", wd=["Riji (pearl shell)", "Riji"], api=["riji pearl shell"])
N(A, "au_aurukun", "Aurukun (Wik) sculpture", R, "sculpture", (1960, 2020), pat=r"aurukun|wik[- ]?mungkan|\bwik\b|wik-?ngathan",
  ctx=AU + r"|aurukun|wik", kn=r"aurukun|\bwik\b", wd=["Wik people", "Aurukun"], api=["Aurukun"])
N(A, "au_rainforest", "Queensland rainforest shields and bicornual baskets", R, "painted shields; fibre", (1850, 1950),
  pat=r"rainforest (shield|basket)|bicornual|cardwell|jirrbal|girramay|djabugay|yidinji|ngadjon|north queensland (shield|basket)|"
      r"murray upper|tully river", ctx=AU + r"|queensland|cardwell|bicornual", kn=r"rainforest shield|bicornual",
  wd=["Rainforest shield", "Bicornual basket"], api=["rainforest shield Queensland", "bicornual basket"])
N(A, "au_southeast", "Southeast Australian carved shields, clubs and possum-skin cloaks", R, "woodcarving; skin cloaks", (1800, 1950),
  pat=r"possum[- ]?skin|parrying shield|broad shield|tree carving|dendroglyph|kulinyu|wurundjeri|gunditjmara|wiradjuri|kamilaroi|"
      r"gamilaraay|yorta yorta|wathaurong|murray river|victoria(n)? aborig|new south wales aborig|lake condah|coranderrk",
  ctx=AU + r"|victoria|new south wales|murray", kn=r"possum-?skin|southeast australia|wiradjuri|kamilaroi|wurundjeri",
  wd=["Possum-skin cloak", "Parrying shield (Australia)"], api=["possum skin cloak", "Aboriginal shield Victoria"])
N(A, "au_toas", "Lake Eyre toas (direction markers)", R, "sculpture (small painted)", (1900, 1910),
  pat=r"\btoas?\b", ctx=r"lake eyre|killalpaninna|diyari|dieri|cooper creek|australia", kn=r"\btoas?\b",
  wd=["Toa (Lake Eyre)", "Toas"], api=["toas Lake Eyre"])
N(A, "au_mornington", "Mornington Island (Lardil, Kaiadilt) art", R, "painting; sculpture", (1960, 2020),
  pat=r"mornington island|lardil|kaiadilt|bentinck island|gununa", kn=r"mornington island|lardil|kaiadilt",
  wd=["Mornington Island Art", "Kaiadilt art"], api=["Mornington Island"])
N(A, "au_ngukurr", "Ngukurr (Roper River) painting", R, "painting (acrylic)", (1987, 2020), pat=r"ngukurr|roper river",
  kn=r"ngukurr", wd=["Ngukurr Arts Centre"], api=["Ngukurr"])
N(A, "au_ts_mask", "Torres Strait turtle-shell masks (krar, le-op)", R, "masks (turtle shell)", (1700, 1920),
  pat=r"\bkrar\b|le-?op|turtle[- ]?shell|tortoise[- ]?shell|\bmask", ctx=r"torres strait|mabuiag|mabuyag|saibai|badu|\bmoa\b|erub|"
      r"darnley|murray island|\bmer\b|nagir|yam island|tudu|dauan|boigu",
  groups=("mask", "sculpture", "other", "ritual object"), family="au_ts", kn=r"torres strait (mask|turtle)|krar|le-?op",
  wd=["Torres Strait Islander mask", "Krar (mask)", "Mawa mask"], api=["Torres Strait mask"])
N(A, "au_ts_other", "Torres Strait Islander art (dhari, drums, carving, printmaking)", R, "various", (1700, 2020),
  pat=r"torres strait|mabuiag|mabuyag|saibai|badu island|\bdhari\b|dari headdress|warup|erub|darnley island|murray island|"
      r"moa island|zenadth kes", fallback=True, family="au_ts", kn=r"torres strait",
  wd=["Torres Strait Islander art", "Dhari"], api=["Torres Strait"])

# ---- 5. Ancient Africa (+ Ethiopian traditional painting)
A = "ancient_africa"
R = "Africa (ancient and early)"
N(A, "af_nok", "Nok terracottas", R, "sculpture (terracotta)", (-900, 300), pat=r"\bnok\b",
  ctx=r"nigeria|terracotta|nok culture|nok artist|nok-style|nok style|jos plateau|kaduna|sculpt|figure|head",
  neg=r"hopi|kachina|rowlandson|ackermann", kn=r"\bnok\b", wd=["Nok culture", "Nok terracottas", "Nok art"], api=["Nok"])
N(A, "af_sokoto", "Sokoto terracottas", R, "sculpture (terracotta)", (-500, 300), pat=r"sokoto",
  ctx=r"terracotta|figure|head|sculpt|nigeria", groups=("sculpture", "other", "ceramics"), kn=r"sokoto",
  wd=["Sokoto culture", "Sokoto terracotta"], api=["Sokoto terracotta"])
N(A, "af_katsina", "Katsina terracottas", R, "sculpture (terracotta)", (-500, 300), pat=r"katsina",
  ctx=r"terracotta|nigeria|katsina ala|katsina culture", neg=r"hopi|kachina|pueblo|zuni|doll|tihu|cottonwood|arizona",
  groups=("sculpture", "other", "ceramics"), kn=r"katsina (terracotta|culture)|katsina ala",
  wd=["Katsina culture", "Katsina Ala"], api=["Katsina terracotta"])
N(A, "af_igboukwu", "Igbo-Ukwu bronzes", R, "metalwork (bronze)", (800, 1000), pat=r"igbo[- ]?ukwu|igbo ukwu",
  kn=r"igbo[- ]?ukwu", wd=["Igbo-Ukwu", "Igbo-Ukwu art"], api=["Igbo-Ukwu"])
N(A, "af_ife", "Ife (Ile-Ife) classical art", R, "sculpture (copper alloy, terracotta)", (1000, 1500),
  pat=r"\bife\b|ile[- ]ife|\bife (culture|style|head)", ctx=r"nigeria|yoruba|ife|terracotta|copper|bronze",
  neg=r"\blife\b|wife|knife", date=(800, 1700), kn=r"\bife\b|ile-ife", wd=["Ife art", "Ife bronze head", "Ife Empire", "Ife"],
  api=["Ife"])
N(A, "af_owo", "Owo art", R, "sculpture (terracotta, ivory)", (1300, 1900), pat=r"\bowo\b", ctx=r"nigeria|yoruba|owo",
  kn=r"\bowo\b", wd=["Owo"], api=["Owo Yoruba"])
N(A, "af_esie", "Esie soapstone figures", R, "sculpture (stone)", (1100, 1500), pat=r"\besie\b", kn=r"\besie\b",
  wd=["Esie soapstone sculpture", "Esie Museum"], api=["Esie"])
N(A, "af_tada", "Tsoede bronzes (Tada, Jebba) and Lower Niger Bronze Industry", R, "metalwork (bronze)", (1300, 1600),
  pat=r"tsoede|jebba|\btada\b|lower niger bronze|lower niger", kn=r"tsoede|lower niger|jebba",
  wd=["Tsoede bronzes", "Lower Niger Bronze Industry"], api=["Tsoede", "Lower Niger bronze"])
N(A, "af_benin_early", "Benin court art, early period (before 1700)", R, "metalwork (brass); ivory", (1300, 1700),
  pat=r"\bbenin\b|\bedo\b|benin city|court of benin|kingdom of benin", ctx=r"nigeria|edo|benin city|kingdom of benin|court|oba|plaque|benin",
  neg=r"republic of benin|dahomey|\bfon\b|abomey|porto-novo", date=(1200, 1700),
  kn=r"benin (early|16th|middle period)|early benin", wd=["Benin Bronzes", "Benin art"], api=["Benin plaque"])
N(A, "af_ind", "Inland Niger Delta (Djenne-jeno) terracottas", R, "sculpture (terracotta)", (300, 1700),
  pat=r"djenn?e|jenne|inland niger delta|niger delta \(djenne|jenne-?jeno|djenne-?jeno", neg=r"mosque",
  kn=r"inland niger delta|djenn?e|jenne", wd=["Djenné-Djenno", "Inland Niger Delta terracotta", "Djenné terracotta"], api=["Djenne"])
N(A, "af_bankoni", "Bankoni terracottas", R, "sculpture (terracotta)", (1100, 1600), pat=r"bankoni", kn=r"bankoni",
  wd=["Bankoni"], api=["Bankoni"])
N(A, "af_tellem", "Tellem (Bandiagara) sculpture and textiles", R, "sculpture; textiles", (1000, 1500), pat=r"tellem",
  kn=r"tellem", wd=["Tellem", "Tellem people"], api=["Tellem"])
N(A, "af_bura", "Bura (Asinda-Sikka) terracottas", R, "sculpture (terracotta)", (200, 1100), pat=r"\bbura\b|asinda[- ]?sikka",
  ctx=r"niger|terracotta|bura", neg=r"bura\b.*(nigeria|cameroon).*(people|textile)", kn=r"\bbura\b",
  wd=["Bura culture", "Bura (archaeological site)"], api=["Bura terracotta"])
N(A, "af_koma", "Koma (Komaland) terracottas", R, "sculpture (terracotta)", (1100, 1700), pat=r"\bkoma\b|komaland",
  ctx=r"ghana|terracotta|koma", kn=r"\bkoma\b|komaland", wd=["Koma Land", "Komaland terracottas"], api=["Koma terracotta"])
N(A, "af_sao", "Sao culture (Lake Chad)", R, "sculpture (terracotta, bronze)", (500, 1600), pat=r"\bsao\b",
  ctx=r"chad|cameroon|terracotta|bronze|kotoko|sao culture", neg=r"sao paulo|sao tome|\bsao\b \w+ (brazil|portugal)",
  kn=r"\bsao\b", wd=["Sao civilisation", "Sao civilization", "Sao people"], api=["Sao Chad"])
N(A, "af_sapi", "Sapi stone figures (nomoli, pomdo) and Sapi-Portuguese ivories", R, "sculpture (stone, ivory)", (1400, 1650),
  pat=r"\bsapi\b|nomoli|pomdo|afro-?portuguese|sapi-?portuguese|bullom|luso-?african", kn=r"sapi|nomoli|afro-?portuguese",
  wd=["Sapi", "Nomoli", "Afro-Portuguese ivories"], api=["nomoli", "Afro-Portuguese ivory"])
N(A, "af_aksum", "Aksumite art", R, "sculpture; coins; architecture", (-100, 960),
  pat=r"aksum|axum|aksumite|axumite|pre-?aksumite|d'?mt\b|yeha|matara|adulis", kn=r"aksum|axum",
  wd=["Kingdom of Aksum", "Aksumite art", "Aksumite architecture"], api=["Aksum", "Axum"])
N(A, "af_kerma", "Kerma culture (Nubia)", R, "ceramics; jewellery", (-2500, -1500), pat=r"\bkerma\b", kn=r"\bkerma\b",
  wd=["Kerma culture", "Kingdom of Kerma"], api=["Kerma"])
N(A, "af_kush", "Napatan and Meroitic Kush", R, "sculpture; ceramics; jewellery", (-800, 350),
  pat=r"napata|napatan|meroe|meroitic|kushite|\bkush\b|nubian.{0,20}(25th|twenty-fifth) dynasty|(25th|twenty-fifth) dynasty|"
      r"karanog|el-?kurru|nuri\b|jebel barkal|gebel barkal|faras.{0,20}meroitic", kn=r"napata|meroe|meroitic|kushite|\bkush\b",
  wd=["Kingdom of Kush", "Meroitic art", "Meroë", "Napata"], api=["Meroe", "Meroitic", "Kushite"])
N(A, "af_nubia_ac", "Nubian A-Group, C-Group and Pan-Grave cultures", R, "ceramics; figurines", (-3800, -1500),
  pat=r"\ba-?group\b|\bc-?group\b|pan-?grave", ctx=r"nubia|egypt|sudan|group|grave", kn=r"a-group|c-group|pan-grave",
  wd=["A-Group culture", "C-Group culture", "Pan-Grave culture"], api=["C-Group Nubia"])
N(A, "af_ballana", "Post-Meroitic Nubia (X-Group / Ballana)", R, "metalwork; ceramics", (350, 600),
  pat=r"ballana|qustul|x-?group|post-?meroitic|noba(dia)?\b", kn=r"ballana|x-group|post-meroitic",
  wd=["Ballana culture", "X-Group culture", "Noubadia"], api=["Ballana"])
N(A, "af_christian_nubia", "Christian Nubia (Faras wall painting, Makuria)", R, "wall painting; ceramics", (550, 1500),
  pat=r"faras|makuria|nobadia|alodia|christian nubia|old nubian|dongola|qasr ibrim", kn=r"faras|makuria|christian nubia",
  wd=["Faras Gallery", "Makuria", "Nubian Christian art"], api=["Faras", "Christian Nubia"])
N(A, "af_gzim", "Great Zimbabwe (soapstone birds) and Zimbabwe culture", R, "sculpture (soapstone); architecture", (1100, 1650),
  pat=r"great zimbabwe|zimbabwe birds?|soapstone birds?|zimbabwe culture|\bkhami\b|mutapa|monomotapa|torwa",
  kn=r"great zimbabwe|zimbabwe culture|zimbabwe bird", wd=["Great Zimbabwe", "Zimbabwe Bird", "Zimbabwe culture"],
  api=["Great Zimbabwe"])
N(A, "af_mapungubwe", "Mapungubwe (gold rhinoceros)", R, "goldwork", (1075, 1220), pat=r"mapungubwe|bambandyanalo|\bk2 (site|culture)",
  kn=r"mapungubwe", wd=["Kingdom of Mapungubwe", "Golden Rhinoceros of Mapungubwe", "Mapungubwe"], api=["Mapungubwe"])
N(A, "af_lydenburg", "Lydenburg heads", R, "sculpture (terracotta)", (450, 650), pat=r"lydenburg", kn=r"lydenburg",
  wd=["Lydenburg Heads"], api=["Lydenburg"])
N(A, "af_swahili", "Swahili coast (Kilwa, Lamu, Zanzibar) arts", R, "architecture; furniture; ceramics", (900, 1900),
  pat=r"swahili|kilwa|\blamu\b|\bpate\b|\bgedi\b|\bgede\b|songo mnara|\bmanda\b|shanga|zanzibar (door|chair|chest)|siwa horn|kiti cha enzi",
  ctx=r"kenya|tanzania|zanzibar|east africa|swahili|kilwa|lamu|mombasa|somali|comoro", kn=r"swahili|kilwa|lamu",
  wd=["Swahili architecture", "Swahili culture", "Kilwa Kisiwani", "Siwa (horn)"], api=["Swahili", "Lamu"])
N(A, "af_eth_icon", "Ethiopian icon and panel painting (Gondarine)", R, "painting (panel)", (1400, 1900),
  pat=r"icon|diptych|triptych|panel painting|gondar|gondarine|painting|madonna|virgin", ctx=ETH,
  groups=("painting", "ritual object", "other", "furniture and woodwork", "drawing"), neg=r"manuscript|scroll|cross",
  family="af_eth", kn=r"ethiopian (icon|painting)|gondarine", wd=["Ethiopian art", "Gondarine art", "Ethiopian icon"],
  api=["Ethiopian icon"])
N(A, "af_eth_ms", "Ethiopian illuminated manuscripts", R, "manuscript painting", (1300, 1900),
  pat=r"manuscript|gospel|psalter|miracles of mary|ta'?amra maryam|homiliary|leaf from|folio|codex|book of", ctx=ETH,
  neg=r"scroll", family="af_eth", kn=r"ethiopian manuscript|ethiopian illuminated",
  wd=["Ethiopian manuscripts", "Ethiopian illuminated manuscript", "Garima Gospels"], api=["Ethiopian manuscript"])
N(A, "af_eth_scroll", "Ethiopian healing (protective) scrolls", R, "painting on parchment", (1700, 1950),
  pat=r"(magic|healing|prayer|protective|amulet|talismanic) scroll|ketab|\bscroll\b|amulet", ctx=ETH, family="af_eth",
  kn=r"ethiopian (magic|healing|prayer) scroll", wd=["Ethiopian magic scroll", "Ethiopian healing scroll"], api=["Ethiopian scroll"])
N(A, "af_eth_cross", "Ethiopian processional and hand crosses", R, "metalwork; woodwork", (1200, 1950),
  pat=r"\bcross(es)?\b", ctx=ETH, family="af_eth", kn=r"ethiopian (processional |hand )?cross",
  wd=["Ethiopian cross", "Processional cross (Ethiopia)", "Lalibela cross"], api=["Ethiopian cross"])
N(A, "af_eth_other", "Ethiopian traditional arts (other)", R, "various", (1300, 1950), pat=r"ethiop|abyssin",
  fallback=True, family="af_eth", kn=r"ethiopian", wd=[], api=[])

NODE = {n["key"]: n for n in NODES}
AREAS = ["colonial_latam", "southeast_asia", "east_asia_folk", "aboriginal_aus", "ancient_africa"]

# a fast pre-filter: any node's pattern, inference place or context
_parts = []
for _n in NODES:
    if _n["pat"]:
        _parts.append(_n["pat"].pattern)
    if _n["inf"]:
        _parts.append(_n["inf"][0].pattern)
PREFILTER = re.compile("|".join(f"(?:{p})" for p in _parts))


# ------------------------------------------------------------------ records

def R_(source, inst, rid, title="", labels="", place="", otype="", medium="", desc="", date="", begin=None, end=None,
       makers=(), url="", flag=""):
    return {"source": source, "inst": inst, "id": str(rid), "title": title or "", "labels": labels or "",
            "place": place or "", "otype": otype or "", "medium": medium or "", "desc": desc or "",
            "date": date or "", "begin": begin, "end": end, "makers": [m for m in makers if m], "url": url or "",
            "flag": flag or ""}


def iyear(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def iter_met():
    path = os.path.join(DATA, "raw", "museums", "MetObjects.csv")
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r["Department"] in ("Photographs", "The Libraries"):
                continue
            flag = ";".join(x for x, k in (("highlight", "Is Highlight"), ("timeline", "Is Timeline Work"))
                            if r.get(k) == "True")
            yield R_("met", "The Metropolitan Museum of Art", r["Object ID"], r["Title"],
                     "; ".join(x for x in (r["Culture"], r["Period"], r["Dynasty"], r["Reign"], r["Artist Display Name"],
                                           r["Artist Nationality"], r["Portfolio"]) if x),
                     "; ".join(x for x in (r["Country"], r["Region"], r["Subregion"], r["State"], r["City"], r["Locale"],
                                           r["Excavation"]) if x),
                     "; ".join(x for x in (r["Object Name"], r["Classification"]) if x), r["Medium"],
                     r.get("Tags", ""), r["Object Date"], iyear(r["Object Begin Date"]), iyear(r["Object End Date"]),
                     [m for m in r["Artist Display Name"].split("|")],
                     r.get("Link Resource") or f"https://www.metmuseum.org/art/collection/search/{r['Object ID']}", flag)


def iter_aic():
    slim = os.path.join(RAW, "aic_slim.jsonl.gz")
    if not os.path.exists(slim):
        os.makedirs(RAW, exist_ok=True)
        files = glob.glob(os.path.join(saa.AIC_DIR, "*.json"))
        log(f"  AIC: building slim cache from {len(files)} dump files")
        with gzip.open(slim + ".part", "wt", encoding="utf-8") as out:
            for fn in files:
                try:
                    with open(fn, encoding="utf-8") as f:
                        d = json.load(f)
                except (OSError, ValueError):
                    continue
                if d.get("department_title") in saa.AIC_SKIP_DEPTS:
                    continue
                out.write(json.dumps({k: d.get(k) for k in saa.AIC_KEYS + ["is_boosted"]}, ensure_ascii=False) + "\n")
        os.replace(slim + ".part", slim)
    with gzip.open(slim, "rt", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            ad = d.get("artist_display") or ""
            yield R_("aic", "Art Institute of Chicago", d["id"], d.get("title"),
                     "; ".join([ad.replace("\n", "; ")] + list(d.get("style_titles") or [])),
                     d.get("place_of_origin"), "; ".join(x for x in (d.get("artwork_type_title"), d.get("classification_title"))
                                                         if x),
                     d.get("medium_display"), "; ".join(d.get("term_titles") or [])[:400], d.get("date_display"),
                     d.get("date_start"), d.get("date_end"), [d.get("artist_title") or ""],
                     f"https://www.artic.edu/artworks/{d['id']}", "highlight" if d.get("is_boosted") else "")


SI_UNITS = {"FSG": "Smithsonian National Museum of Asian Art", "NMAfA": "Smithsonian National Museum of African Art",
            "NMAI": "Smithsonian National Museum of the American Indian", "CHNDM": "Cooper Hewitt, Smithsonian Design Museum",
            "SAAM": "Smithsonian American Art Museum", "HMSG": "Hirshhorn Museum and Sculpture Garden",
            "NMAH": "Smithsonian National Museum of American History", "NMNHANTHRO": "Smithsonian NMNH Anthropology"}


def iter_smithsonian():
    path = os.path.join(OUT_DIR, "smithsonian_objects.csv")
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            yield R_("smithsonian", SI_UNITS.get(r["unit"], "Smithsonian " + r["unit"]), r["record_id"], r["title"],
                     "; ".join(x for x in (r["culture"], r["period"], r["school_style"], r["nmai_culture_area"],
                                           r["nmai_archeol_1"], r["makers"]) if x),
                     "; ".join(x for x in (r["place"], r["countries"]) if x),
                     "; ".join(x for x in (r["object_type"], r["object_name"]) if x),
                     "; ".join(x for x in (r["medium"], r["technique"]) if x), r["period_topics"], r["date"],
                     iyear(r["begin_year"]), iyear(r["end_year"]), r["makers"].split("; ") if r["makers"] else [],
                     r["record_link"])


def iter_penn():
    path = os.path.join(RAWREG, "africa_oceania_targeted", "penn", "Penn_Museum_Collections_Data.csv")
    with open(path, encoding="utf-8", errors="replace", newline="") as f:
        for r in csv.DictReader(f):
            b, e = saa.to_int(r.get("earlyDate")), saa.to_int(r.get("lateDate"))
            if b is None and e is None:
                b, e = aot.parse_date(r.get("dateMade"))
            yield R_("penn", "Penn Museum", r["identifier"], r.get("title") or r.get("objectName"),
                     "; ".join(x for x in (r.get("culture"), r.get("cultureArea"), r.get("period"), r.get("creator"),
                                           r.get("curatorialSection")) if x),
                     "; ".join(x for x in (r.get("placeName"), r.get("siteName"), r.get("locus")) if x),
                     "; ".join(x for x in (r.get("objectName"), r.get("nativeName")) if x),
                     "; ".join(x for x in (r.get("material"), r.get("technique")) if x),
                     (r.get("description") or "")[:400] + " " + (r.get("iconography") or ""), r.get("dateMade"), b, e,
                     re.split(r",\s*", r.get("creator") or ""), r.get("Record URL"))


def iter_aot():
    """Mia / Te Papa / Yale LUX caches through the targeted sweep's readers, network off."""
    aot.http = lambda *a, **k: None
    for src, fn in (("mia", aot.harvest_mia), ("tepapa", aot.harvest_tepapa), ("yale", lambda: aot.harvest_yale(None))):
        try:
            recs = fn()
        except Exception as ex:  # a missing cache directory
            log(f"  {src}: cache unreadable ({type(ex).__name__}: {ex})")
            continue
        for r in recs:
            yield R_(src, aot.SOURCE_INST[src], r["id"], r["title"], r["labels"], r["place"],
                     "; ".join(x for x in (r["otype"], r["oclass"]) if x), r["materials"], r["extra"][:400],
                     r["date_text"], r["begin"], r["end"], [m for m, _ in r["makers"]], r["url"])


def vam_record(rec, inst="Victoria and Albert Museum"):
    r = saa.vam_reduce_record(rec) if "systemNumber" in rec else rec
    d = (r.get("dates") or [[None, None, None]])[0]
    names = [p[0] for p in r.get("persons") or []] + [o[0] for o in r.get("orgs") or []]
    return R_("vam", inst, r.get("id"), r.get("title"),
              "; ".join([s[0] for s in r.get("styles") or []] + [p[0] for p in r.get("peoples") or []] + names),
              "; ".join(p[0] for p in r.get("places") or []),
              "; ".join([r.get("type") or ""] + list(r.get("cats") or [])), r.get("mats"),
              ((r.get("brief") or "") + " " + (r.get("production") or ""))[:500], d[0] if d else "",
              iyear((d[1] or "")[:5].rstrip("-")) if d and d[1] else None,
              iyear((d[2] or "")[:5].rstrip("-")) if d and d[2] else None, names,
              saa.VAM_OBJECT_URL.format(r.get("id")))


def _load_any(fn):
    try:
        if fn.endswith(".gz"):
            with gzip.open(fn, "rt", encoding="utf-8") as f:
                return json.load(f)
        with open(fn, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError, EOFError):
        return None


def iter_vam_cache():
    files = [f for f in glob.glob(os.path.join(RAWREG, "**", "*.json*"), recursive=True)
             if os.sep + "vam" + os.sep in f and os.path.basename(f).startswith("p") or
             (os.sep + "regional" + os.sep + "vam" + os.sep in f)]
    files += glob.glob(os.path.join(RAW, "vam", "*.json.gz"))
    seen = set()
    for fn in sorted(set(files)):
        if os.path.basename(fn).startswith("count_"):
            continue
        d = _load_any(fn)
        if not isinstance(d, dict):
            continue
        for rec in d.get("records") or []:
            sid = rec.get("systemNumber") or rec.get("id")
            if not sid or sid in seen:
                continue
            seen.add(sid)
            yield vam_record(rec)


def cma_record(r):
    cul = r.get("culture")
    if isinstance(cul, str):
        cul = [cul]
    creators = r.get("creators") or []
    if isinstance(creators, str):
        creators = re.findall(r"'description': '([^']*)'", creators)
    else:
        creators = [c.get("description", "") for c in creators if isinstance(c, dict)]
    makers = [re.sub(r"\s*\(.*$", "", c) for c in creators]
    return R_("cma", "Cleveland Museum of Art", r.get("id"), r.get("title"),
              "; ".join(list(cul or []) + creators), "; ".join(cul or []),
              "; ".join(str(x) for x in (r.get("type"), r.get("department")) if x), r.get("technique"),
              str(r.get("description") or r.get("did_you_know") or "")[:400], r.get("creation_date"),
              iyear(r.get("creation_date_earliest")), iyear(r.get("creation_date_latest")), makers,
              r.get("url") or f"https://clevelandart.org/art/{r.get('accession_number')}")


def iter_cma_cache():
    files = [f for f in glob.glob(os.path.join(RAWREG, "**", "*.json*"), recursive=True)
             if os.sep + "cma" + os.sep in f]
    seen = set()
    for fn in sorted(files):
        d = _load_any(fn)
        if not isinstance(d, dict):
            continue
        for r in d.get("data") or []:
            if not isinstance(r, dict) or r.get("id") in seen:
                continue
            seen.add(r.get("id"))
            yield cma_record(r)


def iter_rijks():
    path = os.path.join(RAWREG, "world_extra", "rijks", "records.jsonl.gz")
    if not os.path.exists(path):
        return
    try:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                makers = [m.split("|")[0] for m in d.get("makers") or []]
                yield R_("rijks", "Rijksmuseum", d.get("objno") or d.get("rid"), d.get("title"),
                         "; ".join((d.get("periods") or []) + makers), "; ".join(d.get("places") or []),
                         "; ".join((d.get("types") or []) + (d.get("classes") or [])),
                         "; ".join((d.get("mats") or []) + (d.get("techs") or [])), (d.get("desc") or "")[:400], "",
                         iyear(d.get("begin")), iyear(d.get("end")), makers, d.get("url"))
    except (EOFError, OSError) as ex:  # the extract may still be growing
        log(f"  rijks: stopped early ({type(ex).__name__})")


def iter_eastasia():
    path = os.path.join(OUT_DIR, "east_asia_objects.csv")
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["source"] not in ("colbase", "bunka", "npm", "emuseum"):
                continue
            yield R_(r["source"], r["holder"] or {"npm": "National Palace Museum"}.get(r["source"], r["source"]),
                     r["id"], r["title"] + (" / " + r["title_en"] if r["title_en"] else ""),
                     "; ".join(x for x in (r["period_original"], r["period_en"], r["artist_original"],
                                           r["artist_romanised"]) if x), r["country"],
                     "; ".join(x for x in (r["object_type"], r["object_subtype"]) if x), "", "", r["date"],
                     iyear(r["date_begin"]), iyear(r["date_end"]),
                     [r["artist_romanised"] or r["artist_original"]] if r["attribution"] != "unattributed" else [],
                     r["url"])


READERS = collections.OrderedDict([("met", iter_met), ("aic", iter_aic), ("smithsonian", iter_smithsonian),
                                   ("penn", iter_penn), ("aot", iter_aot), ("vam", iter_vam_cache),
                                   ("cma", iter_cma_cache), ("rijks", iter_rijks), ("eastasia", iter_eastasia)])


# ------------------------------------------------------------------ matching

NOT_NAMED = re.compile(r"(?i)\b(unknown|unidentified|anonymous|anonym|onbekend|school|painter|artist|artists|carver|potter|"
                       r"weaver|people|culture|style|manner of|circle of|follower of|tribe|workshop of|maker|group|"
                       r"village|clan|nation|community|women|men|centre|center|museum|collection|expedition|"
                       r"company|co\.|ltd|inc\b|corporation)\b")


def named_makers(makers):
    out = []
    for m in makers:
        m = (m or "").strip()
        if not m or NOT_NAMED.search(m):
            continue
        try:
            if not saa.is_named(m, "africa"):
                continue
        except Exception:
            pass
        out.append(saa.clean_maker(m))
    return out


def date_overlap(r, win):
    if not win:
        return True
    b, e = r["begin"], r["end"]
    if b is None and e is None:
        return True
    b = b if b is not None else e
    e = e if e is not None else b
    return not (e < win[0] or b > win[1])


def date_inside(r, win):
    b, e = r["begin"], r["end"]
    if b is None and e is None:
        return False
    b = b if b is not None else e
    e = e if e is not None else b
    mid = (b + e) / 2
    return win[0] <= mid <= win[1]


def match(r):
    core = fold(" | ".join((r["title"], r["labels"], r["place"], r["otype"], r["medium"])))
    desc = fold(r["desc"])
    full = core + " | " + desc
    if not PREFILTER.search(full):
        return [], None
    group = saa.object_group(r["otype"], r["title"], r["medium"])
    if group == "photograph" or re.search(r"photograph|postcard|albumen print|gelatin silver", fold(r["otype"])):
        return [], group
    loc = fold(r["place"] + " | " + r["labels"])
    hits = []
    for n in NODES:
        basis = None
        if n["pat"] and (n["pat"].search(core) or (n["desc_ok"] and n["pat"].search(desc))):
            basis = "named"
        elif n["inf"]:
            prx, groups, win, mrx = n["inf"]
            if prx.search(loc) and date_inside(r, win) and \
                    ((groups and group in groups) or (mrx and mrx.search(fold(r["medium"] + " " + r["otype"] + " " + r["title"])))):
                basis = "inferred"
        if not basis:
            continue
        if n["ctx"] and not n["ctx"].search(full):
            continue
        if n["neg"] and n["neg"].search(core):
            continue
        if (n["groups"] or n["med"]) and not ((n["groups"] and group in n["groups"]) or
                                               (n["med"] and n["med"].search(fold(r["medium"] + " " + r["title"])))):
            continue
        if n["date"] and not date_overlap(r, n["date"]):
            continue
        hits.append((n["key"], basis))
    if hits:
        specific = {NODE[k]["family"] for k, _ in hits if not NODE[k]["fallback"]}
        hits = [(k, b) for k, b in hits if not (NODE[k]["fallback"] and NODE[k]["family"] in specific)]
        # a named hit in a family beats inferred hits of the same family (Cusco named vs Peru inferred)
        named_fams = {NODE[k]["family"] for k, b in hits if b == "named"}
        hits = [(k, b) for k, b in hits if b == "named" or NODE[k]["family"] not in named_fams or NODE[k]["family"] == k]
    return hits, group


# ------------------------------------------------------------------ open APIs

_last = [0.0]


def http_json(url, delay):
    wait = delay - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                text = resp.read().decode("utf-8", "replace")
            if "<html" in text[:300].lower():
                raise aot.Challenge()
            return json.loads(text)
        except urllib.error.HTTPError as e:
            if e.code == 403:
                raise aot.Challenge()
            if e.code in (400, 404, 422):
                return None
            time.sleep(10 * (attempt + 1))
        except aot.Challenge:
            raise
        except Exception as ex:
            log(f"    {type(ex).__name__}: {url[:100]}")
            time.sleep(5 * (attempt + 1))
    return None


def cache_json(path, fetch):
    if os.path.exists(path):
        d = _load_any(path)
        if d is not None:
            return d
    d = fetch()
    if d is not None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with gzip.open(path + ".part", "wt", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)
        os.replace(path + ".part", path)
    return d


API_STATUS = collections.Counter()
API_HITS = collections.defaultdict(dict)   # term -> {source: total hits}


def api_terms():
    terms = collections.OrderedDict()
    for n in NODES:
        for t in n["api"]:
            terms.setdefault(t, []).append(n["key"])
    return terms


def harvest_vam_api(delay, pages=3):
    recs = []
    for term in api_terms():
        for page in range(1, pages + 1):
            path = os.path.join(RAW, "vam", f"{saa.slug(term)}_p{page}.json.gz")
            url = saa.VAM_API + "?" + urllib.parse.urlencode({"q": term, "page_size": 100, "page": page,
                                                               "data_profile": "full"})
            try:
                d = cache_json(path, lambda: (lambda x: saa.vam_reduce(x) if x else None)(http_json(url, delay)))
            except aot.Challenge:
                API_STATUS["vam_blocked"] += 1
                log("  V&A API: 403 / challenge - stopping V&A")
                return recs
            if not d:
                API_STATUS["vam_failed"] += 1
                break
            API_STATUS["vam_pages"] += 1
            if page == 1:
                API_HITS[term]["vam"] = d["info"].get("record_count") or 0
            for rec in d.get("records") or []:
                recs.append(vam_record(rec))
            if page >= (d["info"].get("pages") or 0):
                break
    return recs


CMA_SEARCH_FIELDS = saa.CMA_FIELDS + ",description,did_you_know"


def harvest_cma_api(delay, pages=3):
    recs = []
    for term in api_terms():
        for page in range(pages):
            path = os.path.join(RAW, "cma", f"{saa.slug(term)}_{page}.json.gz")
            url = saa.CMA_API + "?" + urllib.parse.urlencode({"q": term, "limit": 100, "skip": page * 100,
                                                              "fields": CMA_SEARCH_FIELDS}, safe=",")
            try:
                d = cache_json(path, lambda: (lambda x: {"info": {"total": (x.get("info") or {}).get("total", 0)},
                                                         "data": x.get("data") or []} if x else None)(http_json(url, delay)))
            except aot.Challenge:
                API_STATUS["cma_blocked"] += 1
                log("  Cleveland API: 403 / challenge - stopping Cleveland")
                return recs
            if not d:
                API_STATUS["cma_failed"] += 1
                break
            API_STATUS["cma_pages"] += 1
            if page == 0:
                API_HITS[term]["cma"] = d["info"].get("total") or 0
            for r in d["data"]:
                recs.append(cma_record(r))
            if (page + 1) * 100 >= (d["info"].get("total") or 0):
                break
    return recs


# ------------------------------------------------------------------ Wikidata

ENDPOINTS = {"wdqs": "https://query.wikidata.org/sparql", "qlever": "https://qlever.dev/api/wikidata"}
ENDPOINT = ["wdqs"]
PREFIXES = """PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""
WD_LOG = collections.Counter()


def _sparql_once(endpoint, query):
    body = urllib.parse.urlencode({"query": PREFIXES + query}).encode()
    req = urllib.request.Request(ENDPOINTS[endpoint], data=body, headers={
        "User-Agent": UA, "Accept": "application/sparql-results+json",
        "Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode("utf-8"))


def sparql(query, name):
    """One query at a time (this process never runs two); cached by name + query hash."""
    h = hashlib.sha1(query.encode()).hexdigest()[:10]
    path = os.path.join(RAW, "wikidata", f"{name}_{h}.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    order = [ENDPOINT[0]] + [e for e in ENDPOINTS if e != ENDPOINT[0]]
    data = None
    for ep in order:
        for attempt in range(3):
            try:
                data = _sparql_once(ep, query)
                WD_LOG[ep] += 1
                break
            except urllib.error.HTTPError as e:
                msg = e.read()[:200]
                WD_LOG[f"{ep}_http_{e.code}"] += 1
                log(f"    {ep} HTTP {e.code} on {name}: {msg!r}")
                if e.code in (400, 403):
                    break
                wait = int(e.headers.get("Retry-After") or 0) or 20 * (attempt + 1)
                time.sleep(min(wait, 120))
            except Exception as ex:
                WD_LOG[f"{ep}_err"] += 1
                log(f"    {ep} {type(ex).__name__} on {name}")
                time.sleep(15 * (attempt + 1))
        if data is not None:
            break
    if data is None:
        log(f"  SPARQL {name}: failed on every endpoint")
        return None
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
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    return out


def lit(s):
    lab, _, lang = s.rpartition("@") if re.search(r"@[a-z]{2,3}$", s) else (s, "", "en")
    return json.dumps(lab, ensure_ascii=False) + "@" + lang


BAD_CLASSES = re.compile(r"(?i)\b(human settlement|city|town|village|commune|municipality|river|mountain|family name|"
                         r"given name|surname|disambiguation|wikimedia|film|album|song|single|band|taxon|species|genus|"
                         r"railway station|airport|ship|asteroid|scholarly article|book|novel|television|football|"
                         r"sports|company|business|record label|video game|literary work|journal|magazine|human\b|"
                         r"locality|district|ward|neighborhood|suburb|street|road|school building|university|"
                         r"administrative|census|county|province|region of|parish|lake|island|hill|valley)")


def wd_resolve():
    labels = sorted({lit(l) for n in NODES for l in n["wd"]} |
                    {lit("Representative List of the Intangible Cultural Heritage of Humanity")})
    rows = []
    for i in range(0, len(labels), 60):
        chunk = " ".join(labels[i:i + 60])
        res = sparql(f"""SELECT ?l ?item ?sl ?desc ?cl WHERE {{
  VALUES ?l {{ {chunk} }}
  ?item rdfs:label|skos:altLabel ?l .
  ?item wikibase:sitelinks ?sl .
  OPTIONAL {{ ?item schema:description ?desc FILTER(LANG(?desc) = "en") }}
  OPTIONAL {{ ?item wdt:P31 ?c . ?c rdfs:label ?cl FILTER(LANG(?cl) = "en") }}
}}""", f"resolve_{i // 60:02d}")
        rows += res or []
    cand = collections.defaultdict(lambda: {"sl": 0, "desc": "", "cls": set(), "labels": set()})
    for r in rows:
        c = cand[r["item"]]
        c["sl"] = int(r.get("sl") or 0)
        c["desc"] = r.get("desc", "")
        if r.get("cl"):
            c["cls"].add(r["cl"])
        c["labels"].add(r["l"])
    by_label = collections.defaultdict(list)
    for q, c in cand.items():
        for l in c["labels"]:
            by_label[fold(l)].append(q)
    out = {}
    for n in NODES:
        if n["qid"]:
            out[n["key"]] = (n["qid"], "", 0, "")
            continue
        best = None
        for rank, l in enumerate(n["wd"]):
            lab = l.rpartition("@")[0] if re.search(r"@[a-z]{2,3}$", l) else l
            for q in by_label.get(fold(lab), []):
                c = cand[q]
                if c["cls"] and all(BAD_CLASSES.search(x) for x in c["cls"]):
                    continue
                if BAD_CLASSES.search(c["desc"]) and not re.search(r"(?i)art|style|culture|craft|paint|school|tradition|"
                                                                  r"textile|print|puppet|movement|technique|civili",
                                                                  c["desc"]):
                    continue
                key = (-rank, c["sl"])
                if best is None or key > best[0]:
                    best = (key, q, lab, c)
        if best:
            out[n["key"]] = (best[1], best[2], best[3]["sl"], best[3]["desc"])
    ich = [q for q, c in cand.items() if "Representative List of the Intangible Cultural Heritage of Humanity" in c["labels"]]
    return out, ich


def wd_node_evidence(qids):
    """works and artists linked to node QIDs."""
    vals = sorted(set(qids))
    works, artists = [], []
    for i in range(0, len(vals), 25):
        chunk = " ".join("wd:" + q for q in vals[i:i + 25])
        res = sparql(f"""SELECT ?node ?p ?w ?wl ?coll ?colll ?cr ?crl ?inc ?sl WHERE {{
  VALUES ?node {{ {chunk} }}
  VALUES ?p {{ wdt:P135 wdt:P136 wdt:P2596 wdt:P31 wdt:P361 wdt:P1269 wdt:P279 }}
  ?w ?p ?node .
  FILTER NOT EXISTS {{ ?w wdt:P31 wd:Q5 }}
  ?w wikibase:sitelinks ?sl .
  OPTIONAL {{ ?w rdfs:label ?wl FILTER(LANG(?wl) = "en") }}
  OPTIONAL {{ ?w wdt:P195 ?coll . OPTIONAL {{ ?coll rdfs:label ?colll FILTER(LANG(?colll) = "en") }} }}
  OPTIONAL {{ ?w wdt:P170 ?cr . OPTIONAL {{ ?cr rdfs:label ?crl FILTER(LANG(?crl) = "en") }} }}
  OPTIONAL {{ ?w wdt:P571 ?inc }}
}} LIMIT 60000""", f"works_{i // 25:02d}")
        works += res or []
        res = sparql(f"""SELECT ?node ?a ?al ?sl WHERE {{
  VALUES ?node {{ {chunk} }}
  VALUES ?p {{ wdt:P135 wdt:P463 wdt:P1416 wdt:P108 }}
  ?a ?p ?node ; wdt:P31 wd:Q5 ; wikibase:sitelinks ?sl .
  OPTIONAL {{ ?a rdfs:label ?al FILTER(LANG(?al) = "en") }}
}} LIMIT 20000""", f"artists_{i // 25:02d}")
        artists += res or []
    return works, artists


LATAM_Q = {"Q419": "Peru", "Q750": "Bolivia", "Q736": "Ecuador", "Q96": "Mexico", "Q739": "Colombia", "Q155": "Brazil",
           "Q774": "Guatemala", "Q717": "Venezuela", "Q414": "Argentina", "Q298": "Chile", "Q733": "Paraguay"}
SEA_Q = {"Q869": "Thailand", "Q252": "Indonesia", "Q836": "Myanmar", "Q881": "Vietnam", "Q928": "Philippines",
         "Q424": "Cambodia", "Q819": "Laos", "Q833": "Malaysia"}
EA_Q = {"Q148": "China", "Q17": "Japan", "Q884": "South Korea", "Q423": "North Korea", "Q865": "Taiwan"}
AU_Q = {"Q408": "Australia"}
COUNTRY_TO_NODE = {"Peru": "col_peru", "Bolivia": "col_altoperu", "Ecuador": "col_quito", "Mexico": "col_nspain",
                   "Colombia": "col_ngranada", "Brazil": "col_brazil", "Guatemala": "col_guatemala"}


def wd_discovery(ich_qids):
    D = {}
    vals = " ".join("wd:" + q for q in LATAM_Q)
    D["latam_held"] = sparql(f"""SELECT ?w ?wl ?c ?coll ?colll ?cr ?crl ?mv ?mvl ?inc ?sl WHERE {{
  VALUES ?c {{ {vals} }}
  ?w wdt:P31 wd:Q3305213 ; wdt:P195 ?coll ; wdt:P571 ?inc .
  ?coll wdt:P17 ?c .
  FILTER(YEAR(?inc) >= 1521 && YEAR(?inc) <= 1830)
  ?w wikibase:sitelinks ?sl .
  OPTIONAL {{ ?w rdfs:label ?wl FILTER(LANG(?wl) = "en") }}
  OPTIONAL {{ ?coll rdfs:label ?colll FILTER(LANG(?colll) = "en") }}
  OPTIONAL {{ ?w wdt:P170 ?cr . OPTIONAL {{ ?cr rdfs:label ?crl FILTER(LANG(?crl) = "en") }} }}
  OPTIONAL {{ ?w wdt:P135 ?mv . OPTIONAL {{ ?mv rdfs:label ?mvl FILTER(LANG(?mvl) = "en") }} }}
}} LIMIT 80000""", "latam_held")
    D["latam_origin"] = sparql(f"""SELECT ?w ?wl ?c ?coll ?colll ?cr ?crl ?mv ?mvl ?inc ?sl WHERE {{
  VALUES ?c {{ {vals} }}
  ?w wdt:P31 wd:Q3305213 ; wdt:P495 ?c ; wdt:P571 ?inc .
  FILTER(YEAR(?inc) >= 1521 && YEAR(?inc) <= 1830)
  ?w wikibase:sitelinks ?sl .
  OPTIONAL {{ ?w rdfs:label ?wl FILTER(LANG(?wl) = "en") }}
  OPTIONAL {{ ?w wdt:P195 ?coll . OPTIONAL {{ ?coll rdfs:label ?colll FILTER(LANG(?colll) = "en") }} }}
  OPTIONAL {{ ?w wdt:P170 ?cr . OPTIONAL {{ ?cr rdfs:label ?crl FILTER(LANG(?crl) = "en") }} }}
  OPTIONAL {{ ?w wdt:P135 ?mv . OPTIONAL {{ ?mv rdfs:label ?mvl FILTER(LANG(?mvl) = "en") }} }}
}} LIMIT 80000""", "latam_origin")
    D["au_artists"] = sparql("""SELECT ?a ?al ?ad ?eg ?egl ?egd ?sl ?b ?occl ?bpl ?org ?orgl ?mv ?mvl WHERE {
  ?a wdt:P27 wd:Q408 ; wdt:P172 ?eg ; wdt:P31 wd:Q5 ; wikibase:sitelinks ?sl .
  OPTIONAL { ?a rdfs:label ?al FILTER(LANG(?al) = "en") }
  OPTIONAL { ?a schema:description ?ad FILTER(LANG(?ad) = "en") }
  OPTIONAL { ?eg rdfs:label ?egl FILTER(LANG(?egl) = "en") }
  OPTIONAL { ?eg schema:description ?egd FILTER(LANG(?egd) = "en") }
  OPTIONAL { ?a wdt:P569 ?b }
  OPTIONAL { ?a wdt:P106 ?occ . ?occ rdfs:label ?occl FILTER(LANG(?occl) = "en") }
  OPTIONAL { ?a wdt:P19 ?bp . ?bp rdfs:label ?bpl FILTER(LANG(?bpl) = "en") }
  OPTIONAL { ?a wdt:P463|wdt:P1416|wdt:P108 ?org . OPTIONAL { ?org rdfs:label ?orgl FILTER(LANG(?orgl) = "en") } }
  OPTIONAL { ?a wdt:P135 ?mv . OPTIONAL { ?mv rdfs:label ?mvl FILTER(LANG(?mvl) = "en") } }
} LIMIT 100000""", "au_artists")
    D["africa_cultures"] = sparql("""SELECT ?cu ?cul ?cud ?sl (COUNT(DISTINCT ?w) AS ?works) WHERE {
  ?cu wdt:P31 wd:Q465299 ; wdt:P17 ?c ; wikibase:sitelinks ?sl .
  ?c wdt:P30 wd:Q15 .
  OPTIONAL { ?w wdt:P2596 ?cu }
  OPTIONAL { ?cu rdfs:label ?cul FILTER(LANG(?cul) = "en") }
  OPTIONAL { ?cu schema:description ?cud FILTER(LANG(?cud) = "en") }
} GROUP BY ?cu ?cul ?cud ?sl""", "africa_cultures")
    allc = dict(SEA_Q, **EA_Q)
    vals = " ".join("wd:" + q for q in allc)
    D["asia_styles"] = sparql(f"""SELECT ?x ?xl ?xd ?t ?c ?sl WHERE {{
  VALUES ?t {{ wd:Q968159 wd:Q1792644 wd:Q1792379 }}
  VALUES ?c {{ {vals} }}
  ?x wdt:P31 ?t ; wikibase:sitelinks ?sl .
  {{ ?x wdt:P17 ?c }} UNION {{ ?x wdt:P495 ?c }}
  OPTIONAL {{ ?x rdfs:label ?xl FILTER(LANG(?xl) = "en") }}
  OPTIONAL {{ ?x schema:description ?xd FILTER(LANG(?xd) = "en") }}
}}""", "asia_styles")
    if ich_qids:
        allc = dict(LATAM_Q, **SEA_Q, **EA_Q, **AU_Q)
        vals = " ".join("wd:" + q for q in allc)
        ichv = " ".join("wd:" + q for q in ich_qids)
        D["ich"] = sparql(f"""SELECT ?x ?xl ?xd ?c ?sl WHERE {{
  VALUES ?ich {{ {ichv} }}
  VALUES ?c {{ {vals} }}
  ?x wdt:P1435 ?ich ; wdt:P17 ?c ; wikibase:sitelinks ?sl .
  OPTIONAL {{ ?x rdfs:label ?xl FILTER(LANG(?xl) = "en") }}
  OPTIONAL {{ ?x schema:description ?xd FILTER(LANG(?xd) = "en") }}
}}""", "ich_asia_latam_au")
        D["ich_africa"] = sparql(f"""SELECT ?x ?xl ?xd ?c ?sl WHERE {{
  VALUES ?ich {{ {ichv} }}
  ?x wdt:P1435 ?ich ; wdt:P17 ?c ; wikibase:sitelinks ?sl .
  ?c wdt:P30 wd:Q15 .
  OPTIONAL {{ ?x rdfs:label ?xl FILTER(LANG(?xl) = "en") }}
  OPTIONAL {{ ?x schema:description ?xd FILTER(LANG(?xd) = "en") }}
}}""", "ich_africa")
    return D


def wd_artist_works(qids):
    vals = sorted(set(qids))
    out = []
    for i in range(0, len(vals), 200):
        chunk = " ".join("wd:" + q for q in vals[i:i + 200])
        out += sparql(f"""SELECT ?a ?w ?wl ?coll ?colll ?inc ?sl WHERE {{
  VALUES ?a {{ {chunk} }}
  ?w wdt:P170 ?a ; wikibase:sitelinks ?sl .
  OPTIONAL {{ ?w rdfs:label ?wl FILTER(LANG(?wl) = "en") }}
  OPTIONAL {{ ?w wdt:P195 ?coll . OPTIONAL {{ ?coll rdfs:label ?colll FILTER(LANG(?colll) = "en") }} }}
  OPTIONAL {{ ?w wdt:P571 ?inc }}
}} LIMIT 50000""", f"au_artist_works_{i // 200:02d}") or []
    return out


# ------------------------------------------------------------------ known-node check

def known_index():
    labelish, rawish = [], []
    files = [os.path.join(INTERIM, "unattributed_cultures.csv"), os.path.join(OUT_DIR, "smithsonian_cultures.csv")] + \
        sorted(f for f in glob.glob(os.path.join(OUT_DIR, "*_traditions.csv")) if "gap_sweep" not in f)
    LAB = {"key", "label", "culture", "culture_group", "period", "tradition", "top_kilns_workshops", "period_en",
           "top_cultures", "parent"}
    RAWC = {"raw_labels", "top_raw_strings", "raw_strings", "period_original_examples", "top_places", "examples",
            "top_classifications", "top_periods", "named_makers"}
    for fn in files:
        if not os.path.exists(fn):
            continue
        base = os.path.basename(fn)
        with open(fn, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                for c, v in r.items():
                    if not v or not c:
                        continue
                    if c in LAB:
                        for part in re.split(r";\s*", v):
                            labelish.append((fold(re.sub(r"\s*\(\d+\)$", "", part)), base, c))
                    elif c in RAWC:
                        rawish.append((fold(v), base, c))
    # de-duplicate
    labelish = list({(a, b, c) for a, b, c in labelish})
    rawish = list({(a, b, c) for a, b, c in rawish})
    return labelish, rawish


def known_status(rxk, labelish, rawish):
    if not rxk:
        return "new", ""
    for v, base, col in labelish:
        if rxk.search(v):
            return "known", f"{base}:{col}={v[:60]}"
    for v, base, col in rawish:
        m = rxk.search(v)
        if m:
            s = max(0, m.start() - 25)
            return "mentioned", f"{base}:{col}~{v[s:m.end() + 25]}"
    return "new", ""


# ------------------------------------------------------------------ assembly

def pct(vals, p):
    return round(vals[min(len(vals) - 1, int(p * len(vals)))]) if vals else ""


def write_csv(path, header, rows):
    with open(path + ".part", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    os.replace(path + ".part", path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-api", action="store_true")
    ap.add_argument("--skip-wikidata", action="store_true")
    ap.add_argument("--endpoint", choices=sorted(ENDPOINTS), default="wdqs")
    ap.add_argument("--sources", default=",".join(READERS))
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between V&A requests (Cleveland: half)")
    args = ap.parse_args()
    ENDPOINT[0] = args.endpoint
    os.makedirs(RAW, exist_ok=True)

    objs = {}                       # (source, id, node) -> row
    src_stats = collections.defaultdict(collections.Counter)
    recs_by_key = {}

    def take(r, origin):
        st = src_stats[origin]
        st["read"] += 1
        hits, group = match(r)
        if not hits:
            return
        st["matched"] += 1
        nm = named_makers(r["makers"])
        for k, basis in hits:
            key = (r["source"], r["id"], k)
            if key in objs:
                continue
            objs[key] = dict(r, node=k, basis=basis, group=group, named=nm)

    # 1. caches
    for name in [s for s in args.sources.split(",") if s in READERS]:
        t0 = time.time()
        n0 = len(objs)
        try:
            for r in READERS[name]():
                take(r, name)
        except FileNotFoundError as ex:
            log(f"  {name}: missing ({ex})")
            src_stats[name]["missing"] += 1
        log(f"{name}: {src_stats[name]['read']} read, {src_stats[name]['matched']} matched, "
            f"{len(objs) - n0} object-node rows ({time.time() - t0:.0f}s)")

    # 2. APIs
    if not args.skip_api:
        log("V&A API ...")
        for r in harvest_vam_api(args.delay):
            take(r, "vam_api")
        log(f"vam_api: {src_stats['vam_api']['read']} read, {src_stats['vam_api']['matched']} matched")
        log("Cleveland API ...")
        for r in harvest_cma_api(max(0.34, args.delay / 2)):
            take(r, "cma_api")
        log(f"cma_api: {src_stats['cma_api']['read']} read, {src_stats['cma_api']['matched']} matched")

    # 3. Wikidata
    qids, wd_works, wd_artists, disc, ich = {}, [], [], {}, []
    au_works = []
    if not args.skip_wikidata:
        log("Wikidata: resolving node labels ...")
        qids, ich = wd_resolve()
        log(f"  {len(qids)} of {len(NODES)} nodes resolved; ICH list items {ich}")
        wd_works, wd_artists = wd_node_evidence([q for q, *_ in qids.values()])
        log(f"  works linked to nodes: {len(wd_works)} rows; artists: {len(wd_artists)} rows")
        disc = wd_discovery(ich)
        for k, v in disc.items():
            log(f"  discovery {k}: {len(v or [])} rows")

    build(objs, src_stats, qids, wd_works, wd_artists, disc, args)


# ------------------------------------------------------------------ build tables

AU_GROUP_RX = re.compile(r"(?i)aborig|torres|indigenous austral|australian indigenous|first nations|yolngu|yolŋu|warlpiri|"
                         r"pintupi|arrernte|aranda|anmatyerr|alyawarr|pitjantjatjara|yankunytjatjara|ngaanyatjarra|tiwi|"
                         r"kunwinjku|gunwinggu|gija|kija|wiradjuri|kamilaroi|gamilaraay|noongar|nyungar|yorta|wurundjeri|"
                         r"kaurna|bundjalung|arabana|luritja|walmajarri|bardi|worrorra|ngarinyin|murri|koori|koorie|"
                         r"palawa|meriam|kaurareg|kalaw|wik\b|lardil|kaiadilt|anindilyakwa|burarra|gurindji|warumungu|"
                         r"people of (the )?(northern territory|western australia|queensland|south australia|new south wales|"
                         r"victoria|central australia|arnhem)")
CRAFT_RX = re.compile(r"(?i)paint|carv|weav|embroider|textile|print|puppet|lacquer|potter|ceramic|craft|paper|cut|dye|"
                      r"mask|sculpt|\bart\b|arts\b|batik|silver|wood|calligraph|kite|figurine|ikat|brocade|inlay|"
                      r"theatre|theater|shadow|making|technique|knowledge|skills of")


def build(objs, src_stats, qids, wd_works, wd_artists, disc, args):
    labelish, rawish = known_index()
    log(f"known index: {len(labelish)} node labels, {len(rawish)} raw strings")

    by_node = collections.defaultdict(list)
    for o in objs.values():
        by_node[o["node"]].append(o)

    # Wikidata evidence per node
    q2node = collections.defaultdict(list)
    for k, (q, *_r) in qids.items():
        q2node[q].append(k)
    wd_ev = collections.defaultdict(lambda: {"works": {}, "artists": {}})
    for r in wd_works:
        for k in q2node.get(r["node"], []):
            w = wd_ev[k]["works"].setdefault(r["w"], {"label": r.get("wl", ""), "colls": set(), "creators": set(),
                                                       "inc": r.get("inc", ""), "sl": int(r.get("sl") or 0),
                                                       "prop": r["p"].rsplit("/", 1)[-1]})
            if r.get("coll"):
                w["colls"].add(r.get("colll") or r["coll"])
            if r.get("cr"):
                w["creators"].add(r.get("crl") or r["cr"])
    for r in wd_artists:
        for k in q2node.get(r["node"], []):
            wd_ev[k]["artists"][r["a"]] = (r.get("al") or r["a"], int(r.get("sl") or 0))

    wd_objects = []
    # colonial paintings discovery -> nodes (movement QID, Cusco by label, else country)
    latam_rows = {}
    for name in ("latam_held", "latam_origin"):
        for r in disc.get(name) or []:
            latam_rows.setdefault(r["w"], r)
            x = latam_rows[r["w"]]
            x.setdefault("_colls", set())
            if r.get("coll"):
                x["_colls"].add(r.get("colll") or r["coll"])
            x.setdefault("_mv", set())
            if r.get("mv"):
                x["_mv"].add(r["mv"])
            x.setdefault("_cr", set())
            if r.get("cr"):
                x["_cr"].add(r.get("crl") or r["cr"])
    latam_by_node = collections.defaultdict(dict)
    for wq, x in latam_rows.items():
        node = None
        for mv in x["_mv"]:
            if q2node.get(mv):
                node = [k for k in q2node[mv] if k.startswith("col_")][:1]
                node = node[0] if node else None
        text = fold(" ".join([x.get("wl", "")] + list(x["_colls"]) + list(x["_cr"])))
        if not node and re.search(r"cuzco|cusco|cuzquen|cusquen", text):
            node = "col_cusco"
        if not node and re.search(r"potosi|collao", text):
            node = "col_altoperu"
        if not node and re.search(r"quito|quiten", text):
            node = "col_quito"
        if not node and re.search(r"casta", text):
            node = "col_casta"
        if not node:
            node = COUNTRY_TO_NODE.get(LATAM_Q.get(x["c"], ""))
        if node:
            latam_by_node[node][wq] = x

    # Aboriginal artists -> nodes
    au = {}
    for r in disc.get("au_artists") or []:
        a = au.setdefault(r["a"], {"label": r.get("al", r["a"]), "desc": r.get("ad", ""), "sl": int(r.get("sl") or 0),
                                   "eg": set(), "egd": set(), "occ": set(), "bp": set(), "orgs": {}, "mv": set(),
                                   "b": r.get("b", "")})
        a["eg"].add(r.get("egl", ""))
        a["egd"].add(r.get("egd", ""))
        if r.get("occl"):
            a["occ"].add(r["occl"])
        if r.get("bpl"):
            a["bp"].add(r["bpl"])
        if r.get("org"):
            a["orgs"][r["org"]] = r.get("orgl") or r["org"]
        if r.get("mvl"):
            a["mv"].add(r["mvl"])
    au_ind = {q: a for q, a in au.items()
              if AU_GROUP_RX.search(" ".join(a["eg"] | a["egd"])) and
              not re.search(r"(?i)\b(european|english|scottish|irish|greek|italian|chinese|lebanese|german|jewish|dutch|"
                            r"anglo|white|vietnamese|croatian|serbian|maltese)\b", " ".join(a["eg"]))}
    art_occ = re.compile(r"(?i)artist|painter|sculptor|printmaker|weaver|carver|potter|ceramic|textile|photograph|designer|"
                         r"illustrator|craft|basket")
    au_art = {q: a for q, a in au_ind.items() if art_occ.search(" ".join(a["occ"]) + " " + a["desc"])}
    au_works = wd_artist_works(list(au_art)) if au_art and not args.skip_wikidata else []
    works_by_artist = collections.defaultdict(list)
    for r in au_works:
        works_by_artist[r["a"]].append(r)
    au_nodes = [n for n in NODES if n["area"] == "aboriginal_aus"]
    au_by_node = collections.defaultdict(dict)
    centres = collections.defaultdict(lambda: {"label": "", "members": set()})
    for q, a in au_art.items():
        text = fold(" ".join([a["desc"]] + list(a["eg"]) + list(a["bp"]) + list(a["orgs"].values()) + list(a["mv"])))
        hit = [n["key"] for n in au_nodes if n["pat"] and not n["fallback"] and n["pat"].search(text)]
        if not hit and re.search(r"bark", text):
            hit = ["au_bark_other"]
        if not hit and re.search(r"desert|dot painting|acrylic", text):
            hit = ["au_western_desert"]
        for k in hit:
            au_by_node[k][q] = a
        for oq, ol in a["orgs"].items():
            if re.search(r"(?i)art|artist|centre|center|tula|mulka|weaver|corporation|cooperative|co-?op", ol):
                centres[oq]["label"] = ol
                centres[oq]["members"].add(a["label"])

    def node_row(n, olist, qinfo, ev, extra_works=None, extra_artists=None, kind="seed_node", note=""):
        srcs = collections.Counter()
        insts = collections.Counter()
        groups = collections.Counter()
        makers = collections.Counter()
        basis = collections.Counter()
        mids, begins, ends = [], [], []
        attributed = 0
        for o in olist:
            srcs[o["source"]] += 1
            insts[o["inst"]] += 1
            groups[o["group"]] += 1
            basis[o["basis"]] += 1
            if o["named"]:
                attributed += 1
                for m in o["named"][:2]:
                    makers[m] += 1
            b, e = o["begin"], o["end"]
            if b is not None or e is not None:
                b = b if b is not None else e
                e = e if e is not None else b
                if -10000 < b < 2100 and -10000 < e < 2100:
                    begins.append(b)
                    ends.append(e)
                    mids.append((b + e) / 2)
        mids.sort()
        wdw = ev["works"] if ev else {}
        works = dict(wdw)
        for wq, x in (extra_works or {}).items():
            works.setdefault(wq, {"label": x.get("wl", ""), "colls": x.get("_colls", set()), "creators": x.get("_cr", set()),
                                  "inc": x.get("inc", ""), "sl": int(x.get("sl") or 0), "prop": "discovery"})
        art_works = [w for w in works.values() if w["colls"] or w["creators"] or w["inc"]]
        wd_colls = collections.Counter(c for w in art_works for c in w["colls"])
        wd_attr = sum(1 for w in art_works if any(c and not re.search(r"(?i)anonymous|unknown", c) for c in w["creators"]))
        artists = dict(ev["artists"]) if ev else {}
        for q, a in (extra_artists or {}).items():
            artists.setdefault(q, (a["label"], a["sl"]))
        all_insts = collections.Counter(insts)
        for c, v in wd_colls.items():
            all_insts[c + " (wd)"] += v
        inst_names = {re.sub(r" \(wd\)$", "", i) for i in all_insts}
        # sample works: Met highlight / timeline first, then spread over institutions, then Wikidata by sitelinks
        samples, seen_inst = [], collections.Counter()
        for o in sorted(olist, key=lambda o: (not o["flag"], o["basis"] != "named", not o["url"], o["source"], o["id"])):
            if seen_inst[o["inst"]] >= 2:
                continue
            seen_inst[o["inst"]] += 1
            d = o["date"] or (f"{o['begin']}" if o["begin"] is not None else "")
            samples.append(f"{o['source']}:{o['id']} {o['title'][:60]}" + (f" ({d})" if d else "") +
                           (f" [{o['flag']}]" if o["flag"] else ""))
            if len(samples) >= 5:
                break
        for wq, w in sorted(art_works and [(q, w) for q, w in works.items() if w in art_works] or [],
                            key=lambda x: -x[1]["sl"])[:3]:
            samples.append(f"wd:{wq} {w['label'][:60]}" + (f" @ {sorted(w['colls'])[0][:40]}" if w["colls"] else ""))
        st, km = known_status(n.get("kn"), labelish, rawish)
        q = qinfo or ("", "", "", "")
        return [n["area"], kind, n["key"], n["label"], n.get("parent", ""), q[0], q[1], q[2], q[3][:80], n["region"],
                n["medium"], "; ".join(f"{g} ({v})" for g, v in groups.most_common(4)),
                f"{n['era'][0]}..{n['era'][1]}" if n.get("era") else "",
                min(begins) if begins else "", pct(mids, 0.1), pct(mids, 0.5), pct(mids, 0.9), max(ends) if ends else "",
                len(olist), basis["named"], basis["inferred"],
                "; ".join(f"{s} {v}" for s, v in srcs.most_common()), *[srcs.get(s, 0) for s in SRC_COLS],
                attributed, round(attributed / len(olist), 3) if olist else "",
                "; ".join(f"{m} ({v})" for m, v in makers.most_common(5)),
                len(inst_names), "; ".join(f"{i} ({v})" for i, v in all_insts.most_common(8)),
                " | ".join(samples), len(works), len(art_works), round(wd_attr / len(art_works), 3) if art_works else "",
                "; ".join(f"{c} ({v})" for c, v in wd_colls.most_common(5)), len(artists),
                "; ".join(a for a, _ in sorted(artists.values(), key=lambda x: -x[1])[:6]),
                "; ".join(f"{t}: {API_HITS[t].get('vam', '')}/{API_HITS[t].get('cma', '')}" for t in n.get("api", [])
                          if t in API_HITS),
                st, km, note]

    rows = []
    for n in NODES:
        rows.append(node_row(n, by_node.get(n["key"], []), qids.get(n["key"]), wd_ev.get(n["key"]),
                             extra_works=latam_by_node.get(n["key"]), extra_artists=au_by_node.get(n["key"])))
    seed_q = {q for q, *_ in qids.values()}

    def cand(area, key, label, region, medium, q, sl, desc, note, kind):
        pseudo = {"area": area, "key": key, "label": label, "region": region, "medium": medium, "era": None,
                  "kn": re.compile(re.escape(fold(label))) if label else None, "api": []}
        return node_row(pseudo, [], (q, label, sl, desc), None, kind=kind, note=note)

    # art centres (workshop nodes) from artists' memberships
    for oq, c in sorted(centres.items(), key=lambda x: -len(x[1]["members"])):
        if oq in seed_q:
            continue
        r = cand("aboriginal_aus", "wd_" + oq, c["label"], "Australia (Aboriginal and Torres Strait Islander)",
                 "art centre / workshop", oq, "", "", f"{len(c['members'])} member artists: " +
                 "; ".join(sorted(c["members"])[:6]), "art_centre")
        rows.append(r)
    # discovery candidates
    for r in disc.get("africa_cultures") or []:
        if r["cu"] in seed_q or (int(r.get("works") or 0) == 0 and int(r.get("sl") or 0) < 5):
            continue
        rows.append(cand("ancient_africa", "wd_" + r["cu"], r.get("cul", r["cu"]), "Africa (ancient and early)",
                         "archaeological culture", r["cu"], r.get("sl"), r.get("cud", ""),
                         f"{r.get('works')} Wikidata items with P2596", "wd_archaeological_culture"))
    areamap = {**{v: "southeast_asia" for v in SEA_Q.values()}, **{v: "east_asia_folk" for v in EA_Q.values()},
               **{v: "colonial_latam" for v in LATAM_Q.values()}, "Australia": "aboriginal_aus"}
    regmap = {"southeast_asia": "Southeast Asia", "east_asia_folk": "East Asia", "colonial_latam": "Latin America",
              "aboriginal_aus": "Australia (Aboriginal and Torres Strait Islander)", "ancient_africa": "Africa"}
    qc = {**SEA_Q, **EA_Q, **LATAM_Q, **AU_Q}
    seen = set()
    for r in disc.get("asia_styles") or []:
        if r["x"] in seed_q or r["x"] in seen:
            continue
        txt = r.get("xl", "") + " " + r.get("xd", "")
        if not re.search(r"(?i)folk|tradition|print|paint|textile|embroider|craft|puppet|lacquer|woodblock|"
                         r"school|ink|ethnic|minority|art", txt) or int(r.get("sl") or 0) < 2:
            continue
        seen.add(r["x"])
        area = areamap.get(qc.get(r["c"], ""), "")
        rows.append(cand(area, "wd_" + r["x"], r.get("xl", r["x"]), regmap.get(area, ""), "style / movement", r["x"],
                         r.get("sl"), r.get("xd", ""), "art movement / style / genre item (" + qc.get(r["c"], "") + ")",
                         "wd_style"))
    for name in ("ich", "ich_africa"):
        for r in disc.get(name) or []:
            if r["x"] in seed_q or r["x"] in seen:
                continue
            txt = r.get("xl", "") + " " + r.get("xd", "")
            if not CRAFT_RX.search(txt):
                continue
            if name == "ich_africa" and not re.search(r"(?i)ethiop|nubia|aksum|sudan|zimbabwe|nigeria", txt + qc.get(r["c"], "")):
                area = "ancient_africa"
            seen.add(r["x"])
            area = "ancient_africa" if name == "ich_africa" else areamap.get(qc.get(r["c"], ""), "")
            rows.append(cand(area, "wd_" + r["x"], r.get("xl", r["x"]), regmap.get(area, ""), "intangible heritage craft",
                             r["x"], r.get("sl"), r.get("xd", ""), "UNESCO ICH Representative List item", "wd_ich"))

    write_csv(os.path.join(OUT_DIR, "gap_sweep_traditions.csv"), TRAD_HEADER, rows)

    # objects table
    orows = []
    for o in sorted(objs.values(), key=lambda o: (NODE[o["node"]]["area"], o["node"], o["source"], o["id"])):
        orows.append([NODE[o["node"]]["area"], o["node"], NODE[o["node"]]["label"], o["basis"], o["source"], o["inst"],
                      o["id"], o["title"][:200], o["date"][:60], o["begin"] if o["begin"] is not None else "",
                      o["end"] if o["end"] is not None else "", o["group"], "; ".join(o["named"][:3]),
                      1 if o["named"] else 0, o["place"][:150], o["labels"][:200], o["flag"], o["url"]])
    for k, ev in wd_ev.items():
        for wq, w in ev["works"].items():
            if not (w["colls"] or w["creators"] or w["inc"]):
                continue
            orows.append([NODE[k]["area"], k, NODE[k]["label"], "wikidata:" + w["prop"], "wikidata",
                          "; ".join(sorted(w["colls"]))[:200], wq, w["label"][:200], w["inc"][:10], "", "", "",
                          "; ".join(sorted(w["creators"]))[:120],
                          1 if any(not re.search(r"(?i)anonymous|unknown", c) for c in w["creators"]) else 0,
                          "", "", f"sitelinks={w['sl']}", f"https://www.wikidata.org/wiki/{wq}"])
    for k, ws in latam_by_node.items():
        for wq, x in ws.items():
            if wq in wd_ev.get(k, {}).get("works", {}):
                continue
            crs = sorted(x["_cr"])
            orows.append([NODE[k]["area"], k, NODE[k]["label"], "wikidata:colonial_painting", "wikidata",
                          "; ".join(sorted(x["_colls"]))[:200], wq, x.get("wl", "")[:200], x.get("inc", "")[:10], "", "",
                          "painting", "; ".join(crs)[:120],
                          1 if any(c and not re.search(r"(?i)anonymous|unknown", c) for c in crs) else 0,
                          LATAM_Q.get(x["c"], ""), "", f"sitelinks={x.get('sl')}", f"https://www.wikidata.org/wiki/{wq}"])
    for k, arts in au_by_node.items():
        for aq, a in arts.items():
            for r in works_by_artist.get(aq, []):
                orows.append([NODE[k]["area"], k, NODE[k]["label"], "wikidata:artist_work", "wikidata",
                              r.get("colll") or r.get("coll", ""), r["w"], r.get("wl", "")[:200], r.get("inc", "")[:10],
                              "", "", "", a["label"], 1, "", "; ".join(sorted(a["eg"]))[:120], f"sitelinks={r.get('sl')}",
                              f"https://www.wikidata.org/wiki/{r['w']}"])
    write_csv(os.path.join(OUT_DIR, "gap_sweep_objects.csv"), OBJ_HEADER, orows)

    srows = []
    for s, st in src_stats.items():
        srows.append([s, st["read"], st["matched"], "cache" if not s.endswith("_api") else "api", ""])
    for k, v in API_STATUS.items():
        srows.append([k, v, "", "api", ""])
    for k, v in WD_LOG.items():
        srows.append(["wikidata_" + k, v, "", "sparql", ""])
    srows.append(["au_aboriginal_artists_wd", len(au_ind), len(au_art), "sparql",
                  f"artists with P27 Australia + Aboriginal/TSI P172; {len(au_art)} with art occupations; "
                  f"{len(au_works)} work rows; {len(centres)} organisations"])
    srows.append(["latam_colonial_paintings_wd", len(latam_rows), sum(len(v) for v in latam_by_node.values()), "sparql",
                  "paintings 1521-1830 held in or originating from Latin American countries"])
    for name, why in (("kluge_ruhe", "kluge-ruhe.org answers 403 (incl. robots.txt); stopped"),
                      ("nga", "National Gallery of Australia search answers 403 (earlier sweep); not contacted"),
                      ("agnsw", "robots.txt disallows Anthropic agents (earlier sweep); not contacted"),
                      ("met_api", "not needed: the open-access CSV holds every Met record"),
                      ("nmvw", "N-Triples on disk need a nested blank-node parse (world_cultures_extra job)"),
                      ("british_museum", "robots.txt disallows Anthropic agents")):
        srows.append([name, "", "", "blocked/skipped", why])
    write_csv(os.path.join(OUT_DIR, "gap_sweep_sources.csv"), ["source", "read", "matched", "kind", "note"], srows)

    # summary
    log("\n== node gain per area (seed nodes with evidence) ==")
    for area in AREAS:
        rr = [r for r in rows if r[0] == area and r[1] == "seed_node"]
        ev = [r for r in rr if r[TRAD_HEADER.index("objects")] or r[TRAD_HEADER.index("wd_works_with_evidence")]
              or r[TRAD_HEADER.index("wd_artists")]]
        c = collections.Counter(r[TRAD_HEADER.index("new_vs_known")] for r in ev)
        cc = collections.Counter(r[TRAD_HEADER.index("new_vs_known")] for r in rows if r[0] == area and r[1] != "seed_node")
        log(f"{area}: {len(rr)} seed nodes, {len(ev)} with evidence: " + ", ".join(f"{k} {v}" for k, v in c.most_common()) +
            f" | Wikidata candidates: " + ", ".join(f"{k} {v}" for k, v in cc.most_common()))
    log(f"objects table: {len(orows)} rows; traditions table: {len(rows)} rows")


SRC_COLS = ["met", "aic", "smithsonian", "penn", "mia", "tepapa", "yale", "vam", "cma", "rijks", "colbase", "bunka", "npm",
            "emuseum"]
TRAD_HEADER = ["area", "kind", "key", "label", "parent", "qid", "qid_label", "qid_sitelinks", "qid_description", "region",
               "medium", "media_observed", "era_nominal", "date_begin_min", "mid_p10", "mid_median", "mid_p90",
               "date_end_max", "objects", "objects_named_basis", "objects_inferred_basis", "objects_per_source",
               *["objects_" + s for s in SRC_COLS], "attributed", "attributed_share", "top_named_makers",
               "n_institutions", "holding_institutions", "sample_works", "wd_linked_items", "wd_works_with_evidence",
               "wd_attributed_share", "wd_collections", "wd_artists", "wd_top_artists", "api_hits_vam_cma",
               "new_vs_known", "known_match", "note"]
OBJ_HEADER = ["area", "node", "node_label", "basis", "source", "institution", "id", "title", "date_text", "date_begin",
              "date_end", "object_group", "named_makers", "attributed", "place", "labels", "flag", "url"]


if __name__ == "__main__":
    main()
