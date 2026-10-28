"""European folk and vernacular visual traditions sweep (visual-art-plan.md §2A, §2.2).

Gathering scope is NODES (traditions) plus EVIDENCE (object counts, holding
institutions, representative works), not object completeness. This sweep makes
sure European traditions outside the Renaissance-Baroque-Rococo/academic
paradigm exist as candidate tradition nodes: embroidery, lace and weaving
traditions, folk and decorative painting, lacquer miniatures, folk ceramics and
tin-glazed wares, woodcarving, toys, paper-cuts, decorated eggs, costume,
regional icon-painting schools, and the arts of the peoples of Russia, the
Caucasus, the Baltic and the Balkans. Sources, in priority order:

  1. Wikidata (node backbone; WDQS via pipelines/visual_art/wikidata.py)
      Items that are instances or subclasses of craft / visual-tradition
      classes (ROOTS: folk art, craft, traditional craft, handicraft,
      decorative art, textile art, embroidery, lacemaking, bobbin lace,
      traditional costume, pottery style, tin-glazed pottery, painting
      technique, decorative painting, style of painting, icon painting, wood
      carving, egg decorating, Russian folk art, Russian lacquer art, toys,
      rug style, weaving/knitting technique, paperwork; and, only with a
      folk/craft signal in label, description or class, art movement, art
      style, art genre, artistic school, artistic technique). Every root QID
      was checked by its English label before use (2026-10-28). Broad roots
      (art style, art genre, pottery ware) are read one level deep (direct
      instances and subclasses only), the rest as whole subclass trees.
      Plus every item carrying an intangible-cultural-heritage status (P3259:
      UNESCO Representative / Urgent Safeguarding / Good Practices lists and
      the national inventories Wikidata records: France, Austria, Germany,
      Finland, Sweden, Ukraine, Armenia, Serbia, Flanders, Netherlands, Ireland,
      Portugal, Slovenia, Spain, Czechia, Poland, ...) or an HCA Red List of
      Endangered Crafts ID (P6599), kept when it has a craft/visual signal.
      Kept when located in Europe (P17/P495, or via P131/P276/P2341/P1071, or
      a European demonym or people in its label or class labels). Recorded:
      qid, label, description, country, people, sitelinks, enwiki title,
      classes, ICH status, heritage designations (P1435), inception, and
      linked works (items with P135/P136/P2079/P31 = node) with their
      collections (P195).
  2. Goskatalog (Russian State Museum Fund catalogue, CC0 repackaging by
      infoculture/goscatalogru, gzipped JSONL via GitHub LFS media URLs):
      data_4 (applied art), data_7 (ethnography), data_13 (applied art,
      everyday life and ethnography) in full, and data_1 (painting) for icons
      only. Streamed line by line; text = name + description + production
      place + technologies + main words + authors. Matched against the
      TRADITIONS patterns (craft centres, techniques, icon schools) and the
      PEOPLES ethnonyms; aggregated per tradition and per people x medium,
      with holding museums. Aggregates are cached (keyed by file sizes and a
      hash of the patterns) so re-runs skip the ~10 minute stream.
  3. Finna API (api.finna.fi, no key, <=1 req/s; robots allows generic
      agents, Content-Signal "search=yes, ai-train=no, use=reference"):
      physical objects (format 0/PhysicalObject/) per tradition / people query
      (Finnish, Swedish and Sami terms). Records count, top holding
      organisations, top topics and places, three sample records.
  4. Cached museum data, no new requests:
      the Met CSV (data/raw/museums/MetObjects.csv), the AIC dump, the V&A
      cache under data/raw/regional/vam (Spain/Valencia/Manises sweeps only)
      and the Cleveland cache under data/raw/regional/cma. European objects
      are kept when they match a TRADITIONS pattern, name a people, or carry a
      folk signal (peasant, folk, provincial, regional dress, ...); objects of
      East/North/Balkan/Baltic/Caucasus cultures are also kept in the folk
      media (textiles, costume, ceramics, wood, toys, ...) without a folk word.
      Aggregated per tradition and per culture x medium.
  5. Europeana Search API: used only when EUROPEANA_API_KEY is set (count +
      top data providers per tradition label); skipped otherwise.

Every HTTP request is cached under data/raw/regional/<source>/ (wikidata_europe_folk,
finna, goskatalog, europeana) and spaced politely; re-runs read the cache.
UA "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)".

Outputs (data/interim/regional/):
  europe_folk_traditions.csv  one row per candidate tradition node.
      kind = wikidata (a Wikidata item), pattern (a named tradition from the
      TRADITIONS list, linked to its Wikidata item when one matches by label),
      people_medium (an ethnonym x medium cell, e.g. "Tatar / embroidery"),
      culture_medium (a museum culture x medium cell, e.g. "Hungarian / costume").
      Columns: label, qid, country, people, region, medium, period, sources,
      object counts per source, top holding institutions, ICH designation,
      heritage designations, sitelinks, sample object URLs, and the comparison
      with build_traditions.py's Met/AIC culture keys (known_in_met_aic:
      exact / place / base_only / no). base_only and no count as NEW nodes.
  europe_folk_objects.csv  slim evidence rows (at most 40 per node and source).
  europe_folk_goskatalog_residual.csv  most frequent unmatched production
      places and technologies in Goskatalog (to judge whether the source still
      adds nodes).

Usage: python3 pipelines/regional/europe_folk.py [--skip wikidata,goskatalog,finna,museums]
           [--delay 1.0] [--no-icons]
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
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

csv.field_size_limit(1 << 24)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw", "regional")
MUSEUMS = os.path.join(ROOT, "data", "raw", "museums")
OUT_DIR = os.path.join(ROOT, "data", "interim", "regional")
MET_CULTURES = os.path.join(ROOT, "data", "interim", "unattributed_cultures.csv")
MET_TRADITIONS = os.path.join(ROOT, "data", "interim", "unattributed_object_traditions.csv")
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"

sys.path.insert(0, os.path.join(ROOT, "pipelines", "unattributed"))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "visual_art"))
from build_traditions import culture_keys, fold  # noqa: E402
import wikidata  # noqa: E402

WD_DIR = os.path.join(RAW, "wikidata_europe_folk")
GOSK_DIR = os.path.join(RAW, "goskatalog")
FINNA_DIR = os.path.join(RAW, "finna")
EUROPEANA_DIR = os.path.join(RAW, "europeana")
GOSK_URL = "https://media.githubusercontent.com/media/infoculture/goscatalogru/main/data/data_{}.jsonl.gz"
GOSK_FILES = {4: "applied art", 7: "ethnography", 13: "applied art, everyday life and ethnography"}
GOSK_ICON_FILE = 1   # painting: icons only
# graphics and rare books/documents: only manuscripts, illuminated books and lubok prints are read
GOSK_BOOK_FILES = {2: "graphics", 9: "documents, rare books", 14: "rare books"}
GOSK_OBJECT_URL = "https://goskatalog.ru/portal/#/collections?id={}"
FINNA_API = "https://api.finna.fi/v1/search"
FINNA_RECORD_URL = "https://finna.fi/Record/{}"
EUROPEANA_API = "https://api.europeana.eu/record/v2/search.json"
MAX_EVIDENCE = 40   # evidence rows per node and source in the objects CSV

# ------------------------------------------------------------------ fetching

_last = [0.0]
DELAY = [1.0]


def fetch(url, path, headers=None):
    """GET url, caching the body at path. Returns text, or None on a hard error.
    Raises PermissionError on 403/429 bot challenges so the caller can stop the source."""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for attempt in range(4):
        wait = DELAY[0] - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json",
                                                   **(headers or {})})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                text = r.read().decode("utf-8", errors="replace")
            with open(path + ".part", "w", encoding="utf-8") as f:
                f.write(text)
            os.replace(path + ".part", path)
            return text
        except urllib.error.HTTPError as e:
            if e.code in (400, 404, 422):
                print(f"  {e.code} {url}", file=sys.stderr)
                return None
            if e.code == 403:
                raise PermissionError(f"403 from {url}")
            print(f"  {e.code} {url} (retry {attempt + 1})", file=sys.stderr)
        except Exception as e:  # URLError, timeouts, IncompleteRead, ...
            print(f"  {type(e).__name__}: {e} {url} (retry {attempt + 1})", file=sys.stderr)
        time.sleep(5 * (attempt + 1))
    return None


def fetch_json(url, path, headers=None):
    text = fetch(url, path, headers)
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        os.remove(path)
        return None


def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "_", fold(s))[:100].strip("_") or hashlib.md5(s.encode()).hexdigest()[:12]


def sparql_cached(query, tag):
    """wikidata.sparql() with the result cached under WD_DIR by a hash of the query."""
    h = hashlib.sha1(query.encode()).hexdigest()[:16]
    path = os.path.join(WD_DIR, f"{tag}_{h}.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    try:
        rows = wikidata.sparql(query, retries=5)
    except RuntimeError:
        print("    WDQS failed repeatedly; trying the QLever mirror")
        rows = qlever(query)
    os.makedirs(WD_DIR, exist_ok=True)
    with open(path + ".part", "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False)
    os.replace(path + ".part", path)
    return rows


QLEVER = "https://qlever.dev/api/wikidata"
QLEVER_PREFIXES = """PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX schema: <http://schema.org/>
"""


def qlever(query):
    """Same result shape as wikidata.sparql(), from the (slower) QLever Wikidata mirror."""
    body = urllib.parse.urlencode({"query": QLEVER_PREFIXES + query}).encode()
    req = urllib.request.Request(QLEVER, data=body, headers={"User-Agent": UA,
                                                             "Accept": "application/sparql-results+json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        data = json.load(r)
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


# ------------------------------------------------------------ geography, peoples

# country label (as Wikidata gives it, incl. common historical states) -> (modern country, region)
REGION_OF = {}
for _region, _names in {
    "Nordic": ["Norway", "Sweden", "Denmark", "Finland", "Iceland", "Faroe Islands", "Åland"],
    "British Isles": ["United Kingdom", "Ireland", "England", "Scotland", "Wales", "Northern Ireland",
                      "Isle of Man", "Jersey", "Guernsey", "Kingdom of Great Britain", "Kingdom of England",
                      "Kingdom of Scotland", "United Kingdom of Great Britain and Ireland"],
    "Western Europe": ["France", "Belgium", "Netherlands", "Luxembourg", "Monaco", "Kingdom of France",
                       "Kingdom of the Netherlands", "Dutch Republic", "Duchy of Brabant", "County of Flanders",
                       "Southern Netherlands", "Burgundian Netherlands", "Habsburg Netherlands"],
    "Central Europe": ["Germany", "Austria", "Switzerland", "Liechtenstein", "Poland", "Czech Republic", "Czechia",
                       "Slovakia", "Hungary", "Slovenia", "Holy Roman Empire", "Austria-Hungary",
                       "Kingdom of Hungary", "Kingdom of Bohemia", "Electorate of Saxony", "Kingdom of Bavaria",
                       "Kingdom of Prussia", "Czechoslovakia", "German Empire", "Polish–Lithuanian Commonwealth",
                       "Austrian Empire", "Habsburg monarchy", "Archduchy of Austria", "Kingdom of Saxony",
                       "Weimar Republic", "Second Polish Republic", "Kingdom of Württemberg", "Margraviate of Moravia",
                       "Old Swiss Confederacy", "East Germany", "West Germany", "Cisleithania"],
    "Southern Europe": ["Spain", "Portugal", "Italy", "Malta", "San Marino", "Vatican City", "Andorra", "Greece",
                        "Cyprus", "Kingdom of Portugal", "Kingdom of Italy", "Republic of Venice", "Kingdom of Naples",
                        "Kingdom of the Two Sicilies", "Kingdom of Sicily", "Crown of Aragon", "Kingdom of Spain",
                        "Crown of Castile", "Kingdom of Sardinia", "Papal States", "Grand Duchy of Tuscany",
                        "Republic of Genoa", "Kingdom of Greece", "Byzantine Empire", "Gibraltar"],
    "Balkans": ["Croatia", "Serbia", "Bosnia and Herzegovina", "Montenegro", "North Macedonia", "Albania",
                "Bulgaria", "Romania", "Moldova", "Kosovo", "Yugoslavia", "Kingdom of Yugoslavia",
                "Socialist Federal Republic of Yugoslavia", "Kingdom of Romania", "Principality of Moldavia",
                "Wallachia", "Kingdom of Serbia", "Tsardom of Bulgaria", "Kingdom of Bulgaria",
                "Socialist Republic of Romania", "People's Republic of Bulgaria"],
    "Baltic": ["Estonia", "Latvia", "Lithuania", "Grand Duchy of Lithuania"],
    "Eastern Europe": ["Ukraine", "Belarus", "Russia", "Russian Empire", "Soviet Union", "Tsardom of Russia",
                       "Russian Soviet Federative Socialist Republic", "Ukrainian Soviet Socialist Republic",
                       "Byelorussian Soviet Socialist Republic", "Grand Duchy of Moscow", "Novgorod Republic",
                       "Kievan Rus'", "Cossack Hetmanate", "Pskov Republic", "Grand Duchy of Finland",
                       "Russian Socialist Federative Soviet Republic"],
    "Caucasus": ["Georgia", "Armenia", "Azerbaijan", "Kingdom of Georgia", "Armenian Soviet Socialist Republic",
                 "Georgian Soviet Socialist Republic", "Azerbaijan Soviet Socialist Republic", "Abkhazia",
                 "South Ossetia", "Artsakh"],
}.items():
    for _n in _names:
        REGION_OF[_n] = _region
EXCLUDED_COUNTRIES = {"Turkey", "Ottoman Empire", "Kazakhstan", "Seljuk Empire", "Sultanate of Rum"}

# European demonyms (folded) -> country; used for labels/class labels and museum cultures.
DEMONYMS = {
    "norwegian": "Norway", "swedish": "Sweden", "danish": "Denmark", "finnish": "Finland", "icelandic": "Iceland",
    "faroese": "Faroe Islands", "british": "United Kingdom", "english": "United Kingdom",
    "scottish": "United Kingdom", "welsh": "United Kingdom", "irish": "Ireland", "manx": "United Kingdom",
    "cornish": "United Kingdom", "french": "France", "breton": "France", "alsatian": "France",
    "provencal": "France", "belgian": "Belgium", "flemish": "Belgium", "walloon": "Belgium", "dutch": "Netherlands",
    "frisian": "Netherlands", "german": "Germany", "bavarian": "Germany", "sorbian": "Germany",
    "austrian": "Austria", "tyrolean": "Austria", "tyrolese": "Austria", "swiss": "Switzerland", "polish": "Poland",
    "kashubian": "Poland", "czech": "Czechia", "bohemian": "Czechia", "moravian": "Czechia", "slovak": "Slovakia",
    "hungarian": "Hungary", "magyar": "Hungary", "slovenian": "Slovenia", "slovene": "Slovenia",
    "spanish": "Spain", "catalan": "Spain", "basque": "Spain", "galician": "Spain", "andalusian": "Spain",
    "portuguese": "Portugal", "italian": "Italy", "sicilian": "Italy", "sardinian": "Italy", "neapolitan": "Italy",
    "venetian": "Italy", "maltese": "Malta", "greek": "Greece", "cretan": "Greece", "cypriot": "Cyprus",
    "croatian": "Croatia", "dalmatian": "Croatia", "serbian": "Serbia", "bosnian": "Bosnia and Herzegovina",
    "montenegrin": "Montenegro", "macedonian": "North Macedonia", "albanian": "Albania", "bulgarian": "Bulgaria",
    "romanian": "Romania", "transylvanian": "Romania", "moldovan": "Moldova", "moldavian": "Moldova",
    "estonian": "Estonia", "latvian": "Latvia", "lithuanian": "Lithuania", "ukrainian": "Ukraine",
    "belarusian": "Belarus", "byelorussian": "Belarus", "russian": "Russia", "georgian": "Georgia",
    "armenian": "Armenia", "azerbaijani": "Azerbaijan", "azeri": "Azerbaijan", "caucasian": "Caucasus",
    "slavic": "", "scandinavian": "", "nordic": "", "european": "",
}

# Peoples: (English name, country, region, regex over lowercased multilingual text).
# The regexes match Russian stems, English and Finnish/Swedish forms.
PEOPLES = [
    ("Sami", "Norway; Sweden; Finland; Russia", "Nordic", r"\bsaam|\bsami\b|\bsámi|samisk|\bsame\b|\blapp(ish|s)?\b|lappalai|саам|лопар"),
    ("Karelian", "Russia; Finland", "Russia: North", r"karjalai|karelian|karelsk|карел"),
    ("Veps", "Russia", "Russia: North", r"\bveps|vepsä|вепс"),
    ("Ingrian / Izhorian", "Russia", "Russia: North", r"inkeri|ingrian|ижор|izhor"),
    ("Komi", "Russia", "Russia: North", r"\bkomi\b|zyrian|permyak|\bкоми\b|коми-|зырян|пермяц"),
    ("Nenets", "Russia", "Russia: North", r"nenets|nenetsi|samoyed|ненец|ненецк|самоед"),
    ("Tatar", "Russia", "Russia: Volga-Ural", r"(?<!crimean )\btatar|(?<!крымско)татар"),
    ("Crimean Tatar", "Ukraine", "Eastern Europe", r"crimean tatar|krimintatar|крымскотатар|крымских татар"),
    ("Bashkir", "Russia", "Russia: Volga-Ural", r"bashkir|baškir|башкир"),
    ("Chuvash", "Russia", "Russia: Volga-Ural", r"chuvash|tšuvass|чуваш"),
    ("Mari", "Russia", "Russia: Volga-Ural", r"\bmari\b|marilai|cheremis|tšeremissi|марийск|мари\b|черемис"),
    ("Udmurt", "Russia", "Russia: Volga-Ural", r"udmurt|votyak|votjakki|удмурт|вотяц|вотяк"),
    ("Mordvin (Erzya, Moksha)", "Russia", "Russia: Volga-Ural", r"mordv|erzya|ersä|moksha|mokša|мордов|мордв|эрзя|эрзян|мокша|мокшан"),
    ("Kalmyk", "Russia", "Russia: Volga-Ural", r"kalmyk|kalmuck|калмык|калмыц"),
    ("Khanty", "Russia", "Russia: Siberia (Asian)", r"khanty|hanti|ostyak|ханты|хантый|остяк"),
    ("Mansi", "Russia", "Russia: Siberia (Asian)", r"\bmansi|vogul|манси|мансий|вогул"),
    ("Adyghe / Circassian / Kabardian", "Russia", "Caucasus (Russia)", r"circassian|adyg|kabard|cherkess|черкес|адыг|кабардин"),
    ("Ossetian", "Russia; Georgia", "Caucasus (Russia)", r"osset|осетин"),
    ("Chechen", "Russia", "Caucasus (Russia)", r"chechen|чечен"),
    ("Ingush", "Russia", "Caucasus (Russia)", r"ingush|ингуш"),
    ("Avar", "Russia", "Caucasus (Russia)", r"\bavar\b|\bavars\b|аварск|аварц"),
    ("Dargin", "Russia", "Caucasus (Russia)", r"dargin|даргин"),
    ("Lezgin", "Russia; Azerbaijan", "Caucasus (Russia)", r"lezgi|лезгин"),
    ("Kumyk", "Russia", "Caucasus (Russia)", r"kumyk|кумык"),
    ("Lak", "Russia", "Caucasus (Russia)", r"\blak\b|\blaks\b|лакск|лакц"),
    ("Nogai", "Russia", "Caucasus (Russia)", r"nogai|nogay|ногай"),
    ("Karachay-Balkar", "Russia", "Caucasus (Russia)", r"karachay|balkar|карачаев|балкар"),
    ("Dagestani (general)", "Russia", "Caucasus (Russia)", r"dagestan|daghestan|дагестан"),
    ("Georgian", "Georgia", "Caucasus", r"georgian|grusin|грузин"),
    ("Armenian", "Armenia", "Caucasus", r"armenian|armenia\b|armenisch|армян"),
    ("Azerbaijani", "Azerbaijan", "Caucasus", r"azerbaijan|azeri|азербайджан"),
    ("Cossack", "Russia; Ukraine", "Eastern Europe", r"cossack|kasakka|казач|казак"),
    ("Ukrainian", "Ukraine", "Eastern Europe", r"ukrain|украин|малоросс"),
    ("Hutsul", "Ukraine; Romania", "Eastern Europe", r"hutsul|huzul|guzul|гуцул|гуцуль"),
    ("Boyko / Lemko / Rusyn", "Ukraine; Poland; Slovakia", "Eastern Europe", r"boyko|bojko|lemko|łemk|rusyn|ruthenian|бойк|лемк|русин"),
    ("Belarusian", "Belarus", "Eastern Europe", r"belarus|byelorus|белорус"),
    ("Lithuanian", "Lithuania", "Baltic", r"lithuan|liettua|литов"),
    ("Latvian", "Latvia", "Baltic", r"latvian|lettish|latvia\b|latvialai|латыш|латвий"),
    ("Estonian", "Estonia", "Baltic", r"estonian|eesti|virolai|эстон"),
    ("Seto", "Estonia; Russia", "Baltic", r"\bseto\b|\bsetu\b|setomaa|сето\b|сету\b|полуверц"),
    ("Moldovan", "Moldova", "Balkans", r"moldov|moldav|молдав|молдован"),
    ("Gagauz", "Moldova", "Balkans", r"gagauz|гагауз"),
    ("Roma", "", "Europe (pan-regional)", r"\bgypsy|\bgipsy|\broma\b|\bromani\b|цыган"),
    ("Aromanian", "Greece; Albania; North Macedonia", "Balkans", r"aromanian|vlach|арумын|влах"),
    ("Sorbian", "Germany", "Central Europe", r"sorbian|\bsorb\b|wendish|лужиц"),
    ("Kashubian", "Poland", "Central Europe", r"kashub|kaszub|кашуб"),
    ("Goral (Podhale)", "Poland; Slovakia", "Central Europe", r"goral|górал|górals|górali|podhal|гурал"),
    ("Basque", "Spain; France", "Southern Europe", r"\bbasque|euskal|баск"),
    ("Breton", "France", "Western Europe", r"\bbreton|bretagne|brittany"),
    ("Frisian", "Netherlands; Germany", "Western Europe", r"frisian|friesland|fries\b"),
    ("Yakut (Sakha)", "Russia", "Russia: Siberia (Asian)", r"yakut|якут"),
    ("Buryat", "Russia", "Russia: Siberia (Asian)", r"buryat|бурят"),
    ("Evenk", "Russia", "Russia: Siberia (Asian)", r"evenk|tungus|эвенк|тунгус"),
    ("Chukchi", "Russia", "Russia: Siberia (Asian)", r"chukchi|чукч|чукот"),
    ("Nanai", "Russia", "Russia: Siberia (Asian)", r"nanai|нанай|гольд"),
    ("Tuvan", "Russia", "Russia: Siberia (Asian)", r"tuvan|тувин"),
    ("Altai", "Russia", "Russia: Siberia (Asian)", r"altai|алтайц|алтайск"),
    ("Khakas", "Russia", "Russia: Siberia (Asian)", r"khakas|хакас"),
    ("Koryak", "Russia", "Russia: Siberia (Asian)", r"koryak|коряк"),
]
PEOPLE_INFO = {p[0]: p for p in PEOPLES}

# Named traditions: (label, country, medium, regex over lowercased text, Finna query or "").
# Labels follow the usual English Wikipedia name so they can be linked to a
# Wikidata item by label. Regexes are multilingual (en / ru / native forms).
TRADITIONS = [
    # --- Russia: painting, lacquer, ceramics, toys, carving, metal, textiles
    ("Khokhloma", "Russia", "painting (wood)", r"khokhlom|chochlom|хохлом", ""),
    ("Gzhel ceramics", "Russia", "ceramics", r"gzhel|гжел", ""),
    ("Zhostovo painting", "Russia", "painting (metal trays)", r"zhostovo|жостов", ""),
    ("Palekh miniature", "Russia", "lacquer miniature", r"palekh|палех", ""),
    ("Fedoskino miniature", "Russia", "lacquer miniature", r"fedoskino|федоскин", ""),
    ("Mstyora miniature", "Russia", "lacquer miniature", r"mstyora|mstera|мстер|мстёр", ""),
    ("Kholuy miniature", "Russia", "lacquer miniature", r"kholui|kholuy|холуй|холуйск", ""),
    ("Gorodets painting", "Russia", "painting (wood)", r"gorodets|городецк\w* роспис|городецк\w* (донц|прялк)", ""),
    ("Mezen painting", "Russia", "painting (wood)", r"mezen painting|мезенск\w* (роспис|прялк)", ""),
    ("Northern Dvina painting", "Russia", "painting (wood)", r"severodvinsk|северодвинск\w* роспис|пермогорск|ракульск|борецк\w* (роспис|прялк)|пучужск|puchuga", ""),
    ("Pinega painting", "Russia", "painting (wood)", r"пинежск\w* (роспис|прялк)", ""),
    ("Polkhovsky Maidan painting", "Russia", "painting (wood)", r"polkhov|полхов", ""),
    ("Ural-Siberian painting", "Russia", "painting (wood)", r"урало-сибирск\w* роспис", ""),
    ("Nizhny Tagil tray painting", "Russia", "painting (metal trays)", r"тагильск\w* (поднос|роспис)", ""),
    ("Lubok", "Russia", "popular prints", r"\blubok|лубок|лубочн", ""),
    ("Matryoshka doll", "Russia", "toys", r"matryoshka|matrioshka|матрешк|матрёшк", ""),
    ("Dymkovo toy", "Russia", "toys", r"dymkovo|дымковск", ""),
    ("Filimonovo toy", "Russia", "toys", r"filimonovo|филимоновск", ""),
    ("Kargopol toy", "Russia", "toys", r"каргопольск\w* игрушк|kargopol toy", ""),
    ("Abashevo toy", "Russia", "toys", r"абашевск\w* игрушк", ""),
    ("Sergiev Posad toy", "Russia", "toys", r"(сергиево-?посадск|загорск)\w* игрушк", ""),
    ("Bogorodskoye carving", "Russia", "woodcarving", r"bogorodsk|богородск\w* (резьб|игрушк|резн)", ""),
    ("Abramtsevo-Kudrino carving", "Russia", "woodcarving", r"абрамцев|кудринск\w* резьб|abramtsevo", ""),
    ("Shemogodsk birch-bark carving", "Russia", "birch bark", r"shemogod|шемогодск", ""),
    ("Kholmogory bone carving", "Russia", "bone carving", r"kholmogor|холмогорск\w* (резьб|кост)", ""),
    ("Tobolsk bone carving", "Russia", "bone carving", r"тобольск\w* (резьб|кост)", ""),
    ("Veliky Ustyug niello", "Russia", "metalwork", r"ustyug niello|устюжск\w* черн|великоустюжск\w* черн", ""),
    ("Rostov enamel (finift)", "Russia", "enamel", r"finift|финифт", ""),
    ("Krasnoye-on-Volga filigree", "Russia", "metalwork", r"красносельск\w* (филигран|ювелир|скан)|казаковск\w* филигран", ""),
    ("Kasli iron casting", "Russia", "metalwork", r"\bkasli|каслинск", ""),
    ("Zlatoust engraving", "Russia", "metalwork", r"zlatoust|златоустовск\w* гравюр", ""),
    ("Vologda lace", "Russia", "lace", r"vologda lace|вологодск\w* кружев", ""),
    ("Yelets lace", "Russia", "lace", r"yelets lace|елецк\w* кружев", ""),
    ("Mikhailov lace", "Russia", "lace", r"михайловск\w* кружев", ""),
    ("Kirov (Vyatka) lace", "Russia", "lace", r"(вятск|кировск)\w* кружев", ""),
    ("Torzhok gold embroidery", "Russia", "embroidery", r"torzhok|торжокск\w* (золот|шить|вышив)", ""),
    ("Krestets stitch", "Russia", "embroidery", r"krestets|крестецк\w* строчк", ""),
    ("Mstyora embroidery (Vladimir stitch)", "Russia", "embroidery", r"мстерск\w* (вышив|белая гладь)|владимирск\w* шов", ""),
    ("Pavlovo Posad shawl", "Russia", "textile (printed)", r"pavlovo.?posad|павлово-?посадск", ""),
    ("Orenburg shawl", "Russia", "textile (knitted)", r"orenburg (shawl|down)|оренбургск\w* (пухов|плат|шал)", ""),
    ("Skopin pottery", "Russia", "ceramics", r"скопинск|skopin", ""),
    ("Russian tiled stoves (izraztsy)", "Russia", "ceramics", r"изразц|изразец|izrazets", ""),
    ("Kubachi metalwork", "Russia", "metalwork", r"kubachi|кубачин", ""),
    ("Balkhar pottery", "Russia", "ceramics", r"balkhar|балхар", ""),
    ("Untsukul wood inlay", "Russia", "woodwork", r"untsukul|унцукул", ""),
    ("Gotsatl metalwork", "Russia", "metalwork", r"гоцатл", ""),
    ("Tabasaran carpets", "Russia", "carpets", r"tabasaran|табасаран", ""),
    ("Tatar leather mosaic (ichigi)", "Russia", "leather", r"ичиг|кожан\w* мозаик|чиteк", ""),
    ("Yakut bone carving", "Russia", "bone carving", r"якутск\w* (резьб|кост)", ""),
    ("Chukchi walrus-ivory engraving (Uelen)", "Russia", "bone carving", r"уэлен|uelen", ""),
    # --- Russian icon-painting schools and centres
    ("Novgorod school (icon painting)", "Russia", "icon painting", r"novgorod school|новгородск\w* (школ|письм|иконопис)", ""),
    ("Pskov school (icon painting)", "Russia", "icon painting", r"pskov school|псковск\w* (школ|письм|иконопис)", ""),
    ("Moscow school (icon painting)", "Russia", "icon painting", r"moscow school of icon|московск\w* (школ|письм)\w*\W+(икон|xv|xvi)|московск\w* иконопис", ""),
    ("Stroganov school", "Russia", "icon painting", r"stroganov school|строгановск\w* (школ|письм|мастер)", ""),
    ("Yaroslavl school (icon painting)", "Russia", "icon painting", r"ярославск\w* (школ|письм|иконопис)", ""),
    ("Tver school (icon painting)", "Russia", "icon painting", r"тверск\w* (школ|письм)", ""),
    ("Rostov-Suzdal school (icon painting)", "Russia", "icon painting", r"(суздальск|ростовск|владимиро-суздальск)\w* (школ|письм)", ""),
    ("Vologda / Northern icon painting (severnye pis'ma)", "Russia", "icon painting", r"северн\w* письм|вологодск\w* (школ|письм|иконопис)|каргопольск\w* (письм|икон)", ""),
    ("Nevyansk icon", "Russia", "icon painting", r"nevyansk|невьянск", ""),
    ("Vetka icon", "Belarus", "icon painting", r"ветковск|vetka icon", ""),
    ("Old Believer icons and cast icons", "Russia", "icon painting", r"old believer|старообрядч|поморск\w* (лить|икон|медн|письм)|медное лить\w*", ""),
    ("Palekh icon painting", "Russia", "icon painting", r"палехск\w* (письм|икон)", ""),
    ("Mstyora icon painting", "Russia", "icon painting", r"мстерск\w* (письм|икон)", ""),
    ("Kholuy icon painting", "Russia", "icon painting", r"холуйск\w* (письм|икон)", ""),
    ("Ural icon painting", "Russia", "icon painting", r"уральск\w* (письм|школ)", ""),
    # --- Balkan and Caucasian icon schools (scope addition 2026-10-28)
    ("Tryavna Iconographic School", "Bulgaria", "icon painting", r"tryavna|трявн|тревненск", ""),
    ("Bansko art school", "Bulgaria", "icon painting", r"bansko|банско|банск\w* (школ|иконопис)", ""),
    ("Samokov Art School", "Bulgaria", "icon painting", r"samokov|самоковск", ""),
    ("Strandzha Iconographic School", "Bulgaria", "icon painting", r"strandzha|странджа", ""),
    ("Bulgarian icon painting", "Bulgaria", "icon painting", r"bulgarian icon|болгарск\w* икон", ""),
    ("Serbian icon painting", "Serbia", "icon painting", r"serbian icon|сербск\w* икон|srpsk\w* ikon", ""),
    ("Heptanese school", "Greece", "icon painting", r"heptanese|ionian school|eptanes", ""),
    ("Georgian icon painting and chased icons", "Georgia", "icon painting", r"georgian icon|грузинск\w* икон|georgian (repouss|chased)", ""),
    ("Belarusian icons", "Belarus", "icon painting", r"belarusian icon|белорусск\w* икон", ""),
    ("Ukrainian icon painting", "Ukraine", "icon painting", r"ukrainian icon|українськ\w* ікон|украинск\w* икон", ""),
    # --- manuscript illumination traditions (Caucasus, Slavic Orthodox)
    ("Armenian manuscript illumination", "Armenia", "manuscript illumination",
     r"armenian (illuminat|manuscript|gospel|miniatur)|армянск\w* (рукопис|миниатюр|евангел)|toros roslin|t'oros roslin", ""),
    ("Cilician school of Armenian illumination", "Armenia", "manuscript illumination", r"cilicia|киликийск|hromkla|ромкл", ""),
    ("Vaspurakan school of Armenian illumination", "Armenia", "manuscript illumination", r"vaspurakan|васпуракан", ""),
    ("Glajor (Gladzor) school of illumination", "Armenia", "manuscript illumination", r"glajor|gladzor|гладзор|глаjор", ""),
    ("Syunik school of illumination (Tatev)", "Armenia", "manuscript illumination", r"syunik|siunik|сюник|tatev\b|татев", ""),
    ("Georgian manuscript illumination", "Georgia", "manuscript illumination",
     r"georgian (illuminat|manuscript|gospel)|грузинск\w* (рукопис|миниатюр|евангел)", ""),
    ("Old Russian manuscript illumination", "Russia", "manuscript illumination",
     r"лицев\w* (рукопис|летопис|апокалипс|синодик|житие|псалтыр|евангел)|древнерусск\w* (рукопис|миниатюр|книжн)|"
     r"old russian (manuscript|illumin)|миниатюр\w* рукопис|рукописн\w* (книг|миниатюр|евангел|псалтыр|синодик)", ""),
    ("Old Believer (Pomor, Vyg) book painting", "Russia", "manuscript illumination",
     r"выговск|поморск\w* (рукопис|книжн|письм\w* книг)|старообрядческ\w* рукопис", ""),
    ("Serbian manuscript illumination", "Serbia", "manuscript illumination",
     r"serbian (manuscript|gospel|illumin)|сербск\w* (рукопис|евангел)|miroslav gospel|мирослав", ""),
    ("Bulgarian manuscript illumination", "Bulgaria", "manuscript illumination",
     r"bulgarian (manuscript|gospel|illumin)|болгарск\w* (рукопис|евангел)|ivan alexander|ивана александра", ""),
    # --- Ukraine, Belarus
    ("Petrykivka painting", "Ukraine", "painting (decorative)", r"petrykivk|petrikovk|петриківськ|петриковск", ""),
    ("Pysanka", "Ukraine; Poland", "decorated eggs", r"pysank|pisank|писанк", "pääsiäismuna"),
    ("Ukrainian embroidery (vyshyvanka)", "Ukraine", "embroidery", r"vyshyv|вишиванк|вишивк|вышиванк", ""),
    ("Rushnyk", "Ukraine; Belarus; Russia", "textile (embroidered towels)", r"rushnyk|рушник|рушнік", ""),
    ("Reshetylivka embroidery", "Ukraine", "embroidery", r"reshetyliv|решетилів|решетиловск", ""),
    ("Krolevets weaving", "Ukraine", "weaving", r"krolevets|кролевецк", ""),
    ("Kosiv ceramics", "Ukraine", "ceramics", r"\bkosiv|косівськ|косовск\w* керам", ""),
    ("Opishnia ceramics", "Ukraine", "ceramics", r"opishn|опішн|опошн", ""),
    ("Ukrainian kilim (lizhnyk)", "Ukraine", "carpets", r"lizhnyk|ліжник|лижник", ""),
    ("Slutsk sashes", "Belarus", "weaving", r"slutsk sash|слуцк\w* пояс|słuck", ""),
    ("Vytsinanka / Wycinanki (paper-cuts)", "Belarus; Poland", "paper-cut", r"vytsinank|wycinank|выцинанк|выцінанк", ""),
    # --- Poland, Czechia, Slovakia, Hungary
    ("Łowicz folk art", "Poland", "textile / paper-cut", r"łowick|lowicz|łowicz", ""),
    ("Kurpie folk art", "Poland", "textile / paper-cut", r"kurpi", ""),
    ("Zalipie painting", "Poland", "painting (walls)", r"zalipi", ""),
    ("Zakopane style", "Poland", "woodcarving / architecture", r"zakopan", ""),
    ("Kashubian embroidery", "Poland", "embroidery", r"kashubian embroid|haft kaszub", ""),
    ("Bolesławiec pottery", "Poland", "ceramics", r"bolesław|boleslaw|bunzlau", ""),
    ("Koniaków lace", "Poland", "lace", r"koniak[oó]w", ""),
    ("Kraków nativity scenes (szopki)", "Poland", "folk sculpture", r"szopk|krak[oó]w (nativity|cr[eè]che)", ""),
    ("Matyó embroidery", "Hungary", "embroidery", r"maty[oó]", ""),
    ("Kalotaszeg embroidery", "Hungary; Romania", "embroidery", r"kalotaszeg|izvorul cri", ""),
    ("Kalocsa embroidery", "Hungary", "embroidery", r"kalocsa", ""),
    ("Halas lace", "Hungary", "lace", r"halas lace|halasi csipke|kiskunhalas", ""),
    ("Hungarian szűr (embroidered felt coat)", "Hungary", "costume", r"sz[űu]r\b|szűr", ""),
    ("Busó masks (Mohács)", "Hungary", "masks", r"bus[oó]j[aá]r|\bbus[oó]\b|mohács mask", ""),
    ("Habán ware", "Slovakia; Czechia; Hungary", "ceramics", r"hab[aá]n|anabaptist (ware|faience|pottery)|габан", ""),
    ("Modra majolica", "Slovakia", "ceramics", r"modransk|modra (majolica|maiolica|faience)", ""),
    ("Čičmany decoration", "Slovakia", "painting (walls)", r"čičman|cicmany", ""),
    ("Slovácko embroidery", "Czechia", "embroidery", r"slov[aá]ck|moravian embroid", ""),
    ("Blueprint (resist-dye printing)", "Czechia; Slovakia; Hungary; Austria; Germany", "textile (printed)",
     r"modrotisk|blaudruck|kékfest|kekfest|indigo resist|blue.?print(ed)? (linen|cloth|textile)|набойк", ""),
    ("Hungarian painted furniture", "Hungary", "painting (wood)", r"hungarian painted (chest|furniture)|festett bútor", ""),
    # --- German-speaking lands
    ("Reverse glass painting (Hinterglasmalerei)", "Germany; Austria; Czechia; Slovakia; Romania", "painting (glass)",
     r"hinterglas|reverse.?(painted )?glass|reverse painting on glass|painted on (the )?reverse|maľba na skle|malba na skle|icoan\w* pe sticl|lasimaalau", ""),
    ("Bauernmalerei (peasant painting)", "Germany; Austria; Switzerland", "painting (wood)", r"bauernmalerei|bauernmöbel|bauernschrank|peasant painting", ""),
    ("Erzgebirge wooden toys and nutcrackers", "Germany", "toys", r"erzgebirg|nutcracker|nussknacker|seiffen", ""),
    ("Oberammergau woodcarving", "Germany", "woodcarving", r"oberammergau", ""),
    ("Black Forest woodcarving", "Germany", "woodcarving", r"black forest (carv|clock)|schwarzwälder|schwarzwald", ""),
    ("Brienz woodcarving", "Switzerland", "woodcarving", r"brienz", ""),
    ("Appenzell folk art (Senntumsmalerei, embroidery)", "Switzerland", "painting / embroidery", r"appenzell|senntum", ""),
    ("Scherenschnitte (paper-cutting)", "Germany; Switzerland", "paper-cut", r"scherenschnitt|papercut|paper.cut", ""),
    ("Sorbian Easter eggs", "Germany", "decorated eggs", r"sorbian (easter )?egg|sorbische ostereier", ""),
    ("Tracht (traditional costume)", "Germany; Austria; Switzerland", "costume", r"\btracht|dirndl|lederhose", ""),
    ("Rhenish stoneware", "Germany", "ceramics", r"westerwald|raeren|siegburg|frechen|bartmann|bellarmine|rhenish stoneware|steinzeug", ""),
    ("Gmunden ceramics", "Austria", "ceramics", r"gmundn", ""),
    # --- Nordic
    ("Rosemaling", "Norway", "painting (wood)", r"rosemål|rosemal|rose.?paint", "rosemaling"),
    ("Hardanger embroidery", "Norway", "embroidery", r"hardanger(søm| embroid| work)|hardangersöm|hardangerkirjont", "hardanger"),
    ("Bunad", "Norway", "costume", r"\bbunad", "bunad"),
    ("Norwegian acanthus carving", "Norway", "woodcarving", r"akantus|acanthus carv", "akantus"),
    ("Selbu knitting", "Norway", "textile (knitted)", r"\bselbu", "selbu"),
    ("Norwegian åklæ (tapestry coverlets)", "Norway", "weaving", r"åklæ|aaklae|aakle", "åklæ"),
    ("Dala painting (Dalmålning)", "Sweden", "painting (wood/wall)", r"dalmålning|dalmalning|dala paint|dalarna (paint|wall)", "dalmålning"),
    ("Kurbits", "Sweden", "painting (wood/wall)", r"kurbits", "kurbits"),
    ("Dala horse", "Sweden", "toys / woodcarving", r"dala ?horse|dalahäst|dalahast", "dalahäst"),
    ("Halland painting (Hallandsbonader)", "Sweden", "painting (textile)", r"hallandsbonad|hallandsmålning", "bonad"),
    ("Swedish folk costume (folkdräkt)", "Sweden", "costume", r"folkdräkt|sockendräkt", "folkdräkt"),
    ("Hedebo embroidery", "Denmark", "embroidery", r"hedebo", "hedebo"),
    ("Tønder lace", "Denmark", "lace", r"tønder|tonder lace", "tønder"),
    ("Ryijy (rya rug)", "Finland; Sweden", "weaving", r"ryijy|\brya\b|ryor\b|rya rug", "ryijy"),
    ("Raanu (Finnish flat-weave)", "Finland", "weaving", r"\braanu", "raanu"),
    ("Täkänä (double weave)", "Finland", "weaving", r"täkänä|takana double", "täkänä"),
    ("Himmeli (straw mobile)", "Finland", "straw work", r"himmeli", "himmeli"),
    ("Rauma bobbin lace", "Finland", "lace", r"rauman pitsi|rauma lace|nypläy|knyppl", "nypläys"),
    ("Kuksa (carved birch cup)", "Finland; Sweden; Norway", "woodcarving", r"\bkuksa|\bguksi|\bkåsa", "kuksa"),
    ("Puukko knife craft", "Finland", "metalwork", r"puukko", "puukko"),
    ("Finnish folk costume (kansanpuku)", "Finland", "costume", r"kansanpuku|kansallispuku", "kansanpuku"),
    ("Karelian embroidery", "Finland; Russia", "embroidery", r"(karjalai\w*|karelian) (kirjon|embroid)|karjalainen kirjonta|карельск\w* вышив", "karjalainen kirjonta"),
    ("Sámi duodji", "Norway; Sweden; Finland; Russia", "handicraft", r"duodji|duodje|saamelai\w* käsity|sami handicraft|саамск\w* (вышив|издел)", "duodji"),
    ("Birch-bark work (tuohityö)", "Finland; Russia", "birch bark", r"tuohi|birch.?bark|берест", "tuohityö"),
    ("Icelandic lopapeysa", "Iceland", "textile (knitted)", r"lopapeysa", ""),
    # --- British Isles
    ("Fair Isle knitting", "United Kingdom", "textile (knitted)", r"fair isle", ""),
    ("Shetland lace", "United Kingdom", "lace", r"shetland (lace|shawl)", ""),
    ("Aran sweater", "Ireland", "textile (knitted)", r"\baran (sweater|jumper|knit)|báinín", ""),
    ("Honiton lace", "United Kingdom", "lace", r"honiton", ""),
    ("Ayrshire whitework", "United Kingdom", "embroidery", r"ayrshire (white|work|embroid)", ""),
    ("Carrickmacross lace", "Ireland", "lace", r"carrickmacross", ""),
    ("Limerick lace", "Ireland", "lace", r"limerick lace", ""),
    ("Irish crochet lace", "Ireland", "lace", r"irish crochet", ""),
    ("Welsh lovespoon", "United Kingdom", "woodcarving", r"love ?spoon", ""),
    ("Welsh and North Country quilts", "United Kingdom", "textile (quilting)", r"welsh quilt|durham quilt|north country quilt", ""),
    ("Tartan", "United Kingdom", "weaving", r"tartan", ""),
    ("Harris Tweed", "United Kingdom", "weaving", r"harris tweed", ""),
    ("Staffordshire figures", "United Kingdom", "ceramics", r"staffordshire (figure|flatback|dog)", ""),
    ("Celtic Revival", "Ireland; United Kingdom", "decorative arts", r"celtic revival", ""),
    ("Narrowboat painting (roses and castles)", "United Kingdom", "painting (decorative)", r"narrowboat|roses and castles|measham", ""),
    # --- Low Countries, France
    ("Delftware", "Netherlands", "ceramics", r"delft", ""),
    ("Hindeloopen painting", "Netherlands", "painting (wood)", r"hindeloop", ""),
    ("Bruges lace", "Belgium", "lace", r"bruges lace|brugse kant", ""),
    ("Brussels lace", "Belgium", "lace", r"brussels (bobbin |needle )?lace|point de bruxelles|point d.angleterre", ""),
    ("Mechlin lace", "Belgium", "lace", r"mechlin|malines lace", ""),
    ("Binche lace", "Belgium", "lace", r"binche", ""),
    ("Valenciennes lace", "France", "lace", r"valenciennes", ""),
    ("Alençon lace", "France", "lace", r"alen[cç]on", ""),
    ("Chantilly lace", "France", "lace", r"chantilly lace|chantilly bobbin", ""),
    ("Le Puy lace", "France", "lace", r"le puy|puy lace", ""),
    ("Quimper faience", "France", "ceramics", r"quimper|henriot", ""),
    ("Breton (Bigouden) embroidery", "France", "embroidery", r"bigouden|breton embroid|broderie bretonne", ""),
    ("Provençal boutis and indiennes", "France", "textile (quilting / printed)", r"\bboutis|provençal (quilt|print)|indiennes de", ""),
    ("Images d'Épinal (popular prints)", "France", "popular prints", r"[ée]pinal|imagerie populaire", ""),
    ("Santons de Provence", "France", "folk sculpture", r"santon", ""),
    # --- Iberia, Italy, Malta
    ("Talavera de la Reina pottery", "Spain", "ceramics", r"talavera", ""),
    ("Azulejo", "Portugal; Spain", "ceramics (tiles)", r"azulejo", ""),
    ("Lagartera embroidery", "Spain", "embroidery", r"lagartera", ""),
    ("Manises lustreware", "Spain", "ceramics", r"manises", ""),
    ("Alcora faience", "Spain", "ceramics", r"alcora", ""),
    ("Barcelos pottery and rooster", "Portugal", "ceramics", r"barcelos", ""),
    ("Arraiolos rugs", "Portugal", "carpets", r"arraiolos", ""),
    ("Viana do Castelo filigree and embroidery", "Portugal", "metalwork / embroidery", r"viana do castelo|minho (embroid|filigree)|filigrana portug", ""),
    ("Caltagirone ceramics", "Italy", "ceramics", r"caltagirone", ""),
    ("Deruta maiolica", "Italy", "ceramics", r"deruta", ""),
    ("Burano lace", "Italy", "lace", r"burano", ""),
    ("Sicilian cart painting", "Italy", "painting (wood)", r"sicilian cart|carretto sicilian|carretti", ""),
    ("Neapolitan presepe", "Italy", "folk sculpture", r"presepe|presepio|neapolitan (cr[eè]che|nativity)", ""),
    ("Sardinian weaving", "Italy", "weaving", r"sardinian (rug|carpet|textile|weav)|tessuto sardo", ""),
    ("Maltese lace", "Malta", "lace", r"maltese lace|malta lace", ""),
    # --- Balkans, Greece, Cyprus
    ("Romanian glass icons", "Romania", "icon painting (glass)", r"icoan\w* pe sticl|glass icon|icon on glass|nicula", ""),
    ("Horezu ceramics", "Romania", "ceramics", r"horez", ""),
    ("Romanian blouse (ie)", "Romania; Moldova", "costume", r"romanian blouse|ie cu alti|altiț|altit[aă]", ""),
    ("Romanian and Moldovan carpets (scoarțe)", "Romania; Moldova", "carpets", r"scoar[tț]|moldovan carpet|romanian carpet|bessarabian (rug|carpet|kilim)", ""),
    ("Maramureș woodcarving", "Romania", "woodcarving", r"maramure", ""),
    ("Bucovina painted eggs", "Romania", "decorated eggs", r"ou[aă] (încondeiate|incondeiate)|romanian (easter )?egg|bucovin\w* egg", ""),
    ("Chiprovtsi carpets", "Bulgaria", "carpets", r"chiprovt|чипровск", ""),
    ("Troyan ceramics", "Bulgaria", "ceramics", r"troyan (ceram|pottery)|троянск\w* керам", ""),
    ("Pirot kilim", "Serbia", "carpets", r"\bpirot", ""),
    ("Zlakusa pottery", "Serbia", "ceramics", r"zlakus", ""),
    ("Pag lace", "Croatia", "lace", r"pag lace|paška čipka", ""),
    ("Lepoglava lace", "Croatia", "lace", r"lepoglav", ""),
    ("Hvar agave lace", "Croatia", "lace", r"agave lace|hvar lace", ""),
    ("Licitar (gingerbread hearts)", "Croatia", "decorated objects", r"licitar", ""),
    ("Idrija lace", "Slovenia", "lace", r"idrij", ""),
    ("Slovenian beehive panels", "Slovenia", "painting (wood)", r"panjsk\w* končnic|beehive (panel|front)", ""),
    ("Konjic woodcarving", "Bosnia and Herzegovina", "woodcarving", r"konjic", ""),
    ("Cretan School", "Greece", "icon painting", r"cretan school|cretan icon|критск\w* школ", ""),
    ("Athonite icon painting", "Greece", "icon painting", r"athonite|mount athos|афонск", ""),
    ("Post-Byzantine icon painting", "Greece; Balkans", "icon painting", r"post-byzantine|поствизантийск", ""),
    ("Greek island embroidery", "Greece", "embroidery", r"(skyros|dodecanese|epirus|cretan|ionian|naxos|rhodes|janina|ioannina|cycladic) embroid|greek island embroid", ""),
    ("Lefkara lace", "Cyprus", "lace", r"lefkara|lefkaritika", ""),
    # --- Baltic
    ("Lithuanian cross-crafting", "Lithuania", "woodcarving", r"kryždirbyst|cross.?crafting|крестоделие|lithuanian (wayside )?cross", ""),
    ("Lithuanian sashes (juostos)", "Lithuania", "weaving", r"juost", ""),
    ("Vilnius Easter palms (verbos)", "Lithuania", "straw work", r"\bverb(os|a)\b|vilnius palm", ""),
    ("Lithuanian folk sculpture (dievdirbiai)", "Lithuania", "woodcarving", r"dievdirb|rūpintojėl|rupintojel", ""),
    ("Muhu embroidery", "Estonia", "embroidery", r"\bmuhu", "muhu"),
    ("Kihnu textiles", "Estonia", "weaving / costume", r"\bkihnu", "kihnu"),
    ("Haapsalu shawl", "Estonia", "lace (knitted)", r"haapsalu", "haapsalu"),
    ("Latvian mittens and Lielvārde belt", "Latvia", "textile (knitted / woven)", r"lielvārd|lielvard|latvian mitten|cimdi", ""),
    # --- Caucasus
    ("Georgian cloisonné enamel (minankari)", "Georgia", "enamel", r"minankari|georgian (cloisonn|enamel)|грузинск\w* (эмал|перегородч)", ""),
    ("Khachkar", "Armenia", "stone carving", r"khachkar|хачкар", ""),
    ("Armenian needle lace", "Armenia", "lace", r"armenian (needle )?lace|армянск\w* кружев", ""),
    ("Armenian carpets", "Armenia", "carpets", r"armenian (carpet|rug)|армянск\w* ков", ""),
    ("Azerbaijani carpets (Caucasian rugs)", "Azerbaijan", "carpets",
     r"azerbaijan\w* (carpet|rug)|caucasian (carpet|rug)|(shirvan|karabagh|karabakh|kuba|quba|kazak|gendje|ganja|shirvan|talish|moghan|seichur|chichi|derbend|lesghi) (rug|carpet)|азербайджанск\w* ков|кавказск\w* ков", ""),
    ("Kelaghayi (silk headscarf)", "Azerbaijan", "textile (printed)", r"kelaghay|kelağay|келагаи", ""),
    ("Lezgin and Dagestani carpets", "Russia", "carpets", r"(лезгинск|дагестанск)\w* ков|dagestan\w* (rug|carpet)", ""),
    # --- pan-regional object traditions
    ("Bobbin lace", "", "lace", r"bobbin lace|коклюшечн|nypläy", ""),
]


# --------------------------------------------------------------- classifiers

MEDIUM_WORDS = [  # (medium, regex) on lowercased multilingual text; first match wins
    ("manuscript illumination", r"рукопис|манускрипт|manuscript|illuminat|gospel book|евангели\w* (рукоп|лицев)|"
                                r"лицев\w* (псалтыр|апокалипс|летопис|синодик)"),
    ("icon painting", r"\bикон|\bicon\b|\bicons\b|ikoni|ikon\b"),
    ("decorated eggs", r"\begg\b|eggs\b|яйц|писанк|pysank|pisank|pääsiäismun"),
    ("lace", r"кружев|\blace|pitsi|spets|dentelle|csipke|koronk|nypl|knyppl|čipk|kant\b"),
    ("embroidery", r"вышив|вышит|вишив|embroider|kirjon|kirjail|brodé|broder|stickerei|hímz|haft|vezen|izšiv"),
    ("toys", r"игрушк|кукл|\btoy|\bdoll|leikkikalu|nukke|matryosh|матрешк|матрёшк|свистульк|whistle"),
    ("lacquer miniature", r"лаков|папье-маше|lacquer|papier"),
    ("carpets", r"ковер|ковёр|ковр|палас|\brug\b|rugs\b|carpet|kilim|килим|ryijy|\brya\b|tapis"),
    ("costume", r"костюм|сарафан|рубах|понев|понёв|кокошник|головн\w* убор|одежд|обув|фартук|передник|кафтан|шуб|"
                r"costume|\bdress|blouse|shirt|apron|bodice|headdress|\bcap\b|bonnet|vest|jacket|\bcoat|skirt|"
                r"\bpuku|asu\b|dräkt|bunad|tracht|kaftan|shawl|платок|шаль|пояс|\bsash|belt\b|stocking|mitten|glove|"
                r"\bhat\b|footwear|boot|sock|рукавиц|варежк|чулк|lapaset|kintaat|sukat"),
    ("textiles", r"ткан|ткач|полотенц|рушник|скатерт|подзор|набойк|textile|weav|tapestr|towel|coverlet|blanket|"
                 r"cushion|pillow|cloth|linen|tekstiil|kangas|kudo|täkänä|raanu|sampler|quilt|textil"),
    ("ceramics", r"керамик|гончар|глиня|фаянс|майолик|изразц|фарфор|ceramic|pottery|earthenware|stoneware|faience|"
                 r"maiolica|majolica|\btile|\bjug\b|keramiik|saviast|porcelain|terracotta|terra cotta"),
    ("painting (folk/decorative)", r"роспис|расписн|painted|paint|maalattu|maalaus|målning|lubok|лубок"),
    ("metalwork", r"серебр|филигран|черн\w* по|финифт|эмал|лить|металл|медн|латун|silver|filigree|niello|enamel|"
                  r"\bmetal|brass|copper|pewter|hopea|jewel|ювелир|украшени|brooch|fibula|сюльгам|buckle"),
    ("arms", r"оружи|кинжал|шашк|ружь|сабл|weapon|dagger|sword|kindjal|kinjal|qama|shashka|powder flask|пороховниц"),
    ("bone carving", r"\bкост|моржов|bone\b|ivory|walrus|\bhorn\b|\bluu\b"),
    ("birch bark / basketry", r"берест|плетен|плетён|birch|bark|basket|tuohi|\bkori\b|näver|корзин|лапт"),
    ("glass", r"стекл|glass|\blasi"),
    ("leather", r"кожан|кожа\b|leather|nahka"),
    ("paper-cut / prints", r"вырезк|вытинанк|выцинанк|wycinank|scherenschnitt|paper.?cut|гравюр|print\b|prints\b"),
    ("woodcarving / woodwork", r"резьб|резн|дерев|прялк|ковш|солониц|wood|carv|\bpuu|veistos|\bträ|\btre\b|chest\b|"
                               r"furniture|spinning|distaff|kuksa|ladle|spoon|ложк|донц|сундук|мебел"),
    ("musical instruments", r"instrument|музыкальн|гусл|балалайк|kantele|fiddle|violin|lute"),
]
MEDIUM_RE = [(m, re.compile(p)) for m, p in MEDIUM_WORDS]


def medium_of(*texts):
    t = " ".join(x for x in texts if x).lower()
    for m, rx in MEDIUM_RE:
        if rx.search(t):
            return m
    return "other"


FOLK_SIGNAL = re.compile(
    r"folk|peasant|vernacular|rural|provincial|traditional|regional (dress|costume)|national (dress|costume)|"
    r"народн|крестьян|этнограф|kansan|kansallis|bonde|bauern|paysan|populaire|popular (print|art)|"
    r"handicraft|craft|ethnic|tribal|lubok|лубок|icon|икон", re.I)

TRAD_COMPILED = [(i, re.compile(t[3])) for i, t in enumerate(TRADITIONS)]
TRAD_BIG = re.compile("|".join(f"(?P<t{i}>{t[3]})" for i, t in enumerate(TRADITIONS)))
PEOPLE_BIG = re.compile("|".join(f"(?P<p{i}>{p[3]})" for i, p in enumerate(PEOPLES)))


def match_traditions(text):
    """All TRADITIONS indexes whose regex hits text (lowercased)."""
    if not TRAD_BIG.search(text):
        return []
    return [i for i, rx in TRAD_COMPILED if rx.search(text)]


def match_peoples(text):
    out = []
    for m in PEOPLE_BIG.finditer(text):
        name = PEOPLES[int(m.lastgroup[1:])][0]
        if name not in out:
            out.append(name)
    return out


def pattern_hash():
    blob = json.dumps([TRADITIONS, PEOPLES, MEDIUM_WORDS], ensure_ascii=False)
    return hashlib.sha1(blob.encode()).hexdigest()[:12]


# -------------------------------------------------------------- 1. Wikidata

# (qid, English label it was verified against, mode, needs a folk/craft signal)
# mode "tree": instances or subclasses anywhere below the root;
# mode "direct": direct instances, and subclasses at any depth (P279+) -- for
# huge roots whose instance trees are dominated by individual objects;
# mode "subclasses": subclasses only (pottery ware: its instances are single pots).
ROOTS = [
    ("Q1153484", "folk art", "tree", False),
    ("Q2207288", "craft", "tree", False),
    ("Q37736399", "traditional craft", "tree", False),
    ("Q877729", "handicraft", "tree", False),
    ("Q631931", "decorative art", "tree", False),
    ("Q10988986", "textile art", "tree", False),
    ("Q20091976", "textile art of an area", "tree", False),
    ("Q65418829", "textile art by ethnic group", "tree", False),
    ("Q120400477", "art by ethnic group", "tree", False),
    ("Q18281", "embroidery", "tree", False),
    ("Q43065851", "lacemaking", "tree", False),
    ("Q1412495", "bobbin lace", "tree", False),
    ("Q3172759", "traditional costume", "tree", False),
    ("Q24017852", "pottery style", "tree", False),
    ("Q17379525", "pottery ware", "subclasses", False),
    ("Q7807719", "tin-glazed pottery", "tree", False),
    ("Q55654686", "ceramic tile", "direct", False),
    ("Q1231896", "painting technique", "tree", True),
    ("Q16714933", "decorative painting", "tree", False),
    ("Q17399019", "style of painting", "tree", True),
    ("Q96398197", "painted glass", "tree", False),
    ("Q1962682", "icon painting", "tree", False),
    ("Q337907", "wood carving", "tree", False),
    ("Q605069", "egg decorating", "tree", False),
    ("Q116859347", "easter egg", "tree", False),
    ("Q4502129", "Russian folk art", "tree", False),
    ("Q1747411", "Russian lacquer art", "tree", False),
    ("Q16693034", "Russian toys", "tree", False),
    ("Q141711638", "clay toy", "tree", False),
    ("Q56147411", "rug style", "tree", False),
    ("Q54915266", "flatweave", "tree", False),
    ("Q2862826", "weaving technique", "tree", False),
    ("Q52368907", "knitting technique", "tree", False),
    ("Q10593571", "stranded colorwork", "tree", False),
    ("Q4822350", "whitework", "tree", False),
    ("Q25469086", "paperwork", "tree", True),
    ("Q2736610", "artistic school", "tree", True),
    ("Q968159", "art movement", "tree", True),
    ("Q1792644", "art style", "direct", True),
    ("Q1792379", "art genre", "direct", True),
    ("Q11177771", "artistic technique", "tree", True),
]
# P3259 values / P6599: intangible heritage and endangered crafts (all values are read)
ICH_SIGNAL = re.compile(
    r"craft|handicraft|embroider|lace|pottery|ceramic|porcelain|faience|carv|paint|weav|textile|costume|dress|"
    r"egg|toy|lacquer|rug|carpet|kilim|tile|azulejo|ware\b|enamel|filigree|woodwork|paper|basket|glass|"
    r"icon|knit|felt|printing|blueprint|indigo|dye|jewel|silver|metal|art\b|arts\b|decorat|ornament|"
    r"wicker|straw|leather|mask|doll|figur|sculpt|stone|cross|ceramics|clay|shawl|sash|belt|blouse|"
    r"народн|промысел|роспис|вышив|кружев|резьб", re.I)
NOT_TRADITION = re.compile(
    r"^(human|business|company|enterprise|factory|ceramics manufactory|manufacturer|museum|organi[sz]ation|"
    r"village|town|city|municipality|human settlement|commune|building|church|painting|sculpture|artwork|"
    r"work of art|film|book|album|single|ship|street|family name|given name|Wikimedia disambiguation page|"
    r"art exhibition|festival|award|periodical|literary work|written work|educational institution|"
    r"university|archaeological site|monument|icon|statue|retail chain|brand|trademark|website|"
    r"musical group|television series|video game|scholarly article|encyclopedia article|ethnic group|"
    r"administrative territorial entity|architectural structure|house|chapel|cathedral|monastery|"
    r"public holiday|holiday|dance|folk dance|musical instrument|type of musical instrument|food|dish|"
    r"recipe|beverage|tradition of a festival|religious festival|fiesta|carnival|procession|sport|"
    r"type of sport|game|ritual|rite|oral tradition|song|genre of music|music genre|language|"
    r"historical period|class of anatomical entity|taxon|architectural style|horse breed|dog breed)$", re.I)
MOVEMENT_FINE_ART = re.compile(r"avant.?garde|modernis|futuris|cubis|expressionis|surrealis|impressionis|"
                               r"abstract|realism|baroque|rococo|renaissance|mannerism|neoclassic|romanticism|"
                               r"academic|contemporary art|pop art|conceptual|minimalis|group of (painters|artists)",
                               re.I)
FOLK_WD = re.compile(
    r"folk|peasant|vernacular|traditional|craft|handicraft|ethnic|народн|embroider|lace|pottery|ceramic|"
    r"faience|maiolica|majolica|carv|weav|textile|costume|icon|egg|toy|lacquer|rug|carpet|kilim|tile|"
    r"\bware\b|enamel|filigree|woodwork|paper.?cut|basket|straw|decorative painting|naive|naïve|lubok|"
    r"popular print|miniature", re.I)


def europe_countries():
    rows = sparql_cached("""SELECT DISTINCT ?c ?cl WHERE {
      VALUES ?cont { wd:Q46 wd:Q48 } ?c wdt:P30 ?cont .
      VALUES ?t { wd:Q6256 wd:Q3624078 wd:Q3024240 wd:Q7275 wd:Q3336843 wd:Q1763527 wd:Q15634554 }
      ?c wdt:P31 ?t . ?c rdfs:label ?cl FILTER(lang(?cl)='en') }""", "countries")
    out = {}
    for r in rows:
        lab = r["cl"]
        if lab in EXCLUDED_COUNTRIES:
            continue
        if lab in REGION_OF:
            out[r["c"]] = lab
    return out


def root_members(qid, mode):
    if mode == "tree":
        q = f"SELECT DISTINCT ?i WHERE {{ ?i (wdt:P31|wdt:P279)/wdt:P279* wd:{qid} }}"
    elif mode == "subclasses":
        q = f"SELECT DISTINCT ?i WHERE {{ ?i wdt:P279+ wd:{qid} }}"
    else:
        q = f"SELECT DISTINCT ?i WHERE {{ {{ ?i wdt:P31 wd:{qid} }} UNION {{ ?i wdt:P279+ wd:{qid} }} }}"
    return [r["i"] for r in sparql_cached(q, f"root_{qid}") if r["i"].startswith("Q")]


def batched(qids, n):
    qids = sorted(qids, key=lambda q: int(q[1:]))
    for k in range(0, len(qids), n):
        yield qids[k:k + n]


def wd_details(qids, europe_q=None):
    """Labels, descriptions, sitelinks, countries, classes, ICH/heritage per item.
    With europe_q, items whose P17/P495 names only non-European countries are dropped
    after the first (country) query, so the other queries run on fewer items."""
    info = collections.defaultdict(lambda: collections.defaultdict(set))
    for chunk in batched(qids, 400):
        vals = " ".join(f"wd:{q}" for q in chunk)
        for r in sparql_cached("SELECT ?i ?p ?c WHERE { VALUES ?i { %s } VALUES ?p { wdt:P17 wdt:P495 } ?i ?p ?c }"
                               % vals, "det_cty"):
            info[r["i"]]["country_q"].add(r["c"])
    if europe_q is not None:
        qids = [q for q in qids if not info[q]["country_q"] or info[q]["country_q"] & europe_q]
    queries = {
        "lab": """SELECT ?i ?sl ?l ?lru ?lany ?d ?en WHERE { VALUES ?i { %s } ?i wikibase:sitelinks ?sl .
            OPTIONAL { ?i rdfs:label ?l FILTER(lang(?l)='en') } OPTIONAL { ?i rdfs:label ?lru FILTER(lang(?lru)='ru') }
            OPTIONAL { ?i rdfs:label ?lany FILTER(lang(?lany) IN ('mul','de','fr','uk','pl','hu','sv','fi','nb','es','it','cs','ro','ka','hy')) }
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
    for tag, tmpl in queries.items():
        for chunk in batched(qids, 250):
            vals = " ".join(f"wd:{q}" for q in chunk)
            for r in sparql_cached(tmpl % vals, f"det_{tag}"):
                d = info[r["i"]]
                if tag == "lab":
                    d["sitelinks"].add(int(r["sl"]))
                    for k in ("l", "lru", "lany", "d"):
                        if r.get(k):
                            d[k].add(r[k])
                    if r.get("en"):
                        d["enwiki"].add(r["en"])
                elif tag == "cty":
                    d["country_q"].add(r["c"])
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
    return info


def wd_linked_works(qids):
    """Works pointing at a node (movement, genre, fabrication method, instance of) and their collections."""
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


ICON_CLASS = "Q132137"          # icon (verified label 2026-10-28)
MANUSCRIPT_CLASS = "Q87167"     # manuscript
MS_LANGS = {  # language QID (verified labels) -> tradition label, None = decided by country
    "Q8785": "Armenian manuscript illumination", "Q181074": "Armenian manuscript illumination",
    "Q8108": "Georgian manuscript illumination", "Q34834": "Georgian manuscript illumination",
    "Q33251": None, "Q35499": None, "Q12292710": "Old Russian manuscript illumination",
    "Q9299": "Serbian manuscript illumination", "Q7918": "Bulgarian manuscript illumination",
    "Q12294897": "Bulgarian manuscript illumination",
}
ARMENIAN_SCHOOLS = [(r"cilici|sis\b|hromkla|skevra|drazark", "Cilician school of Armenian illumination"),
                    (r"vaspurakan|\bvan\b|aght?amar|khizan", "Vaspurakan school of Armenian illumination"),
                    (r"glajor|gladzor", "Glajor (Gladzor) school of illumination"),
                    (r"syunik|siunik|tatev", "Syunik school of illumination (Tatev)")]


def wd_icons_manuscripts():
    """Icon schools (P135 of icons) and Armenian/Georgian/Slavonic manuscripts with collections.
    Returns (extra candidate QIDs, {tradition label: evidence})."""
    schools = sparql_cached(f"""SELECT ?m (COUNT(DISTINCT ?w) AS ?n) WHERE {{ ?w wdt:P31 wd:{ICON_CLASS} ; wdt:P135 ?m }}
        GROUP BY ?m""", "icon_movements")
    extra = {r["m"] for r in schools if r["m"].startswith("Q")}
    vals = " ".join(f"wd:{q}" for q in MS_LANGS)
    rows = sparql_cached(f"""SELECT ?w ?wl ?lang ?c ?cl ?coll ?locl ?movl ?t ?sl WHERE {{
        VALUES ?lang {{ {vals} }} ?w wdt:P407 ?lang . ?w wdt:P31/wdt:P279* wd:{MANUSCRIPT_CLASS} .
        ?w wikibase:sitelinks ?sl .
        OPTIONAL {{ ?w rdfs:label ?wl FILTER(lang(?wl)='en') }}
        OPTIONAL {{ ?w wdt:P495|wdt:P17 ?c . ?c rdfs:label ?cl FILTER(lang(?cl)='en') }}
        OPTIONAL {{ ?w wdt:P195 ?cc . ?cc rdfs:label ?coll FILTER(lang(?coll)='en') }}
        OPTIONAL {{ ?w wdt:P1071 ?loc . ?loc rdfs:label ?locl FILTER(lang(?locl)='en') }}
        OPTIONAL {{ ?w wdt:P135 ?mv . ?mv rdfs:label ?movl FILTER(lang(?movl)='en') }}
        OPTIONAL {{ ?w wdt:P571 ?t }} }}""", "manuscripts")
    per_item = collections.defaultdict(lambda: collections.defaultdict(set))
    for r in rows:
        d = per_item[r["w"]]
        for k in ("wl", "lang", "cl", "coll", "locl", "movl", "t", "sl"):
            if r.get(k):
                d[k].add(r[k])
    ev = collections.defaultdict(lambda: {"n": 0, "colls": collections.Counter(), "years": [], "samples": []})
    for w, d in per_item.items():
        text = " ".join(sorted(d["wl"] | d["locl"] | d["movl"])).lower()
        countries = " ".join(d["cl"])
        labs = set()
        for lang in d["lang"]:
            lab = MS_LANGS.get(lang)
            if lab is None:
                lab = ("Serbian manuscript illumination" if "Serbia" in countries else
                       "Bulgarian manuscript illumination" if "Bulgaria" in countries else
                       "Old Russian manuscript illumination")
            labs.add(lab)
        if "Armenian manuscript illumination" in labs:
            for rx, lab in ARMENIAN_SCHOOLS:
                if re.search(rx, text):
                    labs.add(lab)
        year = min((wikidata.year_of(t) for t in d["t"] if wikidata.year_of(t) is not None), default=None)
        for lab in labs:
            e = ev[lab]
            e["n"] += 1
            e["colls"].update(d["coll"])
            if year is not None:
                e["years"].append(year)
            if len(e["samples"]) < 5:
                e["samples"].append(f"https://www.wikidata.org/wiki/{w}")
    print(f"  icon movements on Wikidata: {len(extra)}; manuscripts by language: {len(per_item)} "
          f"-> {', '.join(f'{k} {v[chr(110)]}' for k, v in ev.items())}")
    return extra, dict(ev)


def harvest_wikidata():
    countries = europe_countries()
    print(f"Wikidata: {len(countries)} European/Caucasian country items")
    via = collections.defaultdict(set)
    needs_signal = set()
    for qid, label, mode, signal in ROOTS:
        members = root_members(qid, mode)
        print(f"  root {qid} {label}: {len(members)} members")
        for m in members:
            via[m].add(label)
            if signal:
                needs_signal.add(m)
    icon_movements, ms_evidence = wd_icons_manuscripts()
    for m in icon_movements:
        via[m].add("icon movement")
    ich = sparql_cached("SELECT DISTINCT ?i WHERE { ?i wdt:P3259 ?v }", "ich_all")
    hca = sparql_cached("SELECT DISTINCT ?i WHERE { ?i wdt:P6599 ?v }", "hca_all")
    for r in ich:
        via[r["i"]].add("ICH status")
    for r in hca:
        via[r["i"]].add("HCA Red List")
    print(f"  ICH-status items {len(ich)}, HCA red-list items {len(hca)}; candidates {len(via)}")
    info = wd_details([q for q in via if q.startswith("Q")], set(countries))
    demonym_re = re.compile(r"\b(" + "|".join(re.escape(k) for k in DEMONYMS if DEMONYMS[k]) + r")\b")
    kept = {}
    drops = collections.Counter()
    for q, roots in via.items():
        d = info.get(q)
        if not d:
            drops["no details"] += 1
            continue
        label = next(iter(sorted(d["l"])), "") or next(iter(sorted(d["lany"])), "") or next(iter(sorted(d["lru"])), "")
        desc = next(iter(sorted(d["d"])), "")
        p31, p279 = d["p31"], d["p279"]
        classes = " | ".join(sorted(p31 | p279))
        text = f"{label} | {desc} | {classes}"
        # location
        cset = {countries[c] for c in d["country_q"] if c in countries}
        if not cset and not (d["country_q"] - set(countries)):
            cset = {countries[c] for c in d["loc_country_q"] if c in countries}
        peoples = match_peoples(f"{label} {desc} {' '.join(d['ethnic'])}".lower())
        if not cset:
            hits = {DEMONYMS[m] for m in demonym_re.findall(fold(f"{label} {desc} {' '.join(p279)}"))}
            hits.discard("")
            cset = {h for h in hits if h in REGION_OF or h == "Caucasus"}
        if not cset and peoples:
            cset = {c.strip() for p in peoples for c in PEOPLE_INFO[p][1].split(";") if c.strip()}
        if not cset:
            drops["not European"] += 1
            continue
        if d["country_q"] and not (d["country_q"] & set(countries)) and not d["loc_country_q"] & set(countries):
            drops["not European"] += 1
            continue
        # what kind of thing
        if p31 and all(NOT_TRADITION.match(c) for c in p31) and not p279:
            drops["not a tradition (P31 class)"] += 1
            continue
        only_ich = roots <= {"ICH status", "HCA Red List"}
        if only_ich and not ICH_SIGNAL.search(text):
            drops["ICH, not craft/visual"] += 1
            continue
        if q in needs_signal and not (roots - {r[1] for r in ROOTS if r[3]}) and not d["ich"]:
            if not FOLK_WD.search(text) or (MOVEMENT_FINE_ART.search(text) and not re.search(r"folk|icon|народн", text, re.I)):
                drops["broad root without folk signal"] += 1
                continue
        years = sorted(d["year"])
        kept[q] = {
            "qid": q, "label": label, "label_ru": next(iter(sorted(d["lru"])), ""), "description": desc,
            "aliases": sorted(d["alias"]), "countries": sorted(cset), "peoples": peoples,
            "sitelinks": max(d["sitelinks"] or {0}), "enwiki": next(iter(sorted(d["enwiki"])), ""),
            "classes": classes, "roots": sorted(roots), "ich": sorted(d["ich"]), "heritage": sorted(d["heritage"]),
            "year": years[0] if years else None,
            "medium": medium_of(label, desc, classes),
        }
    print(f"  kept {len(kept)} European candidate nodes; dropped {dict(drops)}")
    works, colls = wd_linked_works(list(kept))
    for q, k in kept.items():
        k["wd_works"] = works.get(q, 0)
        k["wd_collections"] = colls.get(q, collections.Counter())
    print(f"  {sum(1 for q in kept if works.get(q))} nodes have linked works ({sum(works.values())} works)")
    return kept, ms_evidence


def link_patterns_to_wikidata(kept):
    """Look up TRADITIONS labels (and their short forms) as Wikidata en labels/aliases."""
    names = {}
    for i, t in enumerate(TRADITIONS):
        lab = t[0]
        for v in {lab, re.sub(r"\s*\(.*?\)", "", lab).strip()}:
            names.setdefault(v, set()).add(i)
    by_label = collections.defaultdict(list)
    for q, k in kept.items():
        for v in [k["label"]] + k["aliases"]:
            by_label[fold(v)].append(q)
    link = {}
    missing = []
    for v, idx in names.items():
        qs = by_label.get(fold(v))
        if qs:
            best = max(qs, key=lambda q: kept[q]["sitelinks"])
            for i in idx:
                link.setdefault(i, best)
        else:
            missing.append(v)
    # labels not among the kept nodes: ask WDQS, keep the best item that is not a place/person
    for chunk in [missing[k:k + 80] for k in range(0, len(missing), 80)]:
        vals = " ".join('"%s"@en' % v.replace('"', '') for v in chunk)
        q = """SELECT ?l ?i ?sl (GROUP_CONCAT(DISTINCT ?cl; separator='|') AS ?cls) WHERE { VALUES ?l { %s }
            { ?i rdfs:label ?l } UNION { ?i skos:altLabel ?l } ?i wikibase:sitelinks ?sl .
            OPTIONAL { ?i wdt:P31|wdt:P279 ?c . ?c rdfs:label ?cl FILTER(lang(?cl)='en') } } GROUP BY ?l ?i ?sl""" % vals
        for r in sorted(sparql_cached(q, "patlabel"), key=lambda r: -int(r["sl"])):
            cls = [c for c in r.get("cls", "").split("|") if c]
            if cls and all(NOT_TRADITION.match(c) for c in cls):
                continue
            if re.search(r"village|settlement|town|city|human|river|municipal|commune|island|archipelago|"
                         r"railway|ship|station|family name|disambiguation|county|district|region", r.get("cls", ""), re.I):
                continue
            for i in names[r["l"]]:
                link.setdefault(i, r["i"])
    return link


# ------------------------------------------------------------- 2. Goskatalog

def gosk_download(n):
    path = os.path.join(GOSK_DIR, f"data_{n}.jsonl.gz")
    if os.path.exists(path):
        return path
    os.makedirs(GOSK_DIR, exist_ok=True)
    url = GOSK_URL.format(n)
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        size = int(r.headers.get("Content-Length") or 0)
    print(f"  downloading {url} ({size / 1e6:.0f} MB)")
    if size > 2_000_000_000:
        raise RuntimeError(f"data_{n} is {size / 1e9:.1f} GB, over the 2 GB per-file budget")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=600) as r, open(path + ".part", "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)
    os.replace(path + ".part", path)
    return path


ICON_RE = re.compile(r"^\s*(икона|складень|деисус|створ|киот)|\bикона\b")
BOOK_RE = re.compile(r"рукопис|лицев|миниатюр|евангел|псалтыр|апостол\b|минея|синодик|часослов|служебник|"
                     r"требник|октоих|триод|житие|летопис|канонник|ирмолог|обиходник|крюков|лубок|лубочн|"
                     r"народн\w* картин")


def _s(v):
    """Goskatalog fields are mostly strings but some records carry lists or dicts."""
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        return " ".join(_s(x) for x in v.values())
    if isinstance(v, (list, tuple)):
        return " ".join(_s(x) for x in v)
    return str(v)


def gosk_year(d):
    s = d.get("startDate") or ""
    m = re.match(r"(-?\d{4})", s)
    return int(m.group(1)) if m else None


def harvest_goskatalog(icons=True, progress=None):
    """Stream the Goskatalog files; return aggregates (cached by pattern hash and file sizes)."""
    files = [(n, gosk_download(n)) for n in GOSK_FILES]
    if icons:
        files.append((GOSK_ICON_FILE, gosk_download(GOSK_ICON_FILE)))
        files += [(n, gosk_download(n)) for n in GOSK_BOOK_FILES]
    key = pattern_hash() + "_" + "_".join(f"{n}-{os.path.getsize(p)}" for n, p in files)
    cache = os.path.join(GOSK_DIR, f"aggregate_{key}.json")
    if os.path.exists(cache):
        with open(cache, encoding="utf-8") as f:
            print("Goskatalog: aggregates read from cache")
            return json.load(f)
    agg = {"trad": {}, "people": {}, "records": 0, "matched": 0, "files": {},
           "residual_place": collections.Counter(), "residual_tech": collections.Counter(), "evidence": []}

    def bucket(table, key_):
        b = table.get(key_)
        if b is None:
            b = table[key_] = {"n": 0, "museums": collections.Counter(), "years": [], "samples": [],
                               "media": collections.Counter(), "places": collections.Counter()}
        return b

    t0 = time.time()
    for n, path in files:
        seen = matched = 0
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                seen += 1
                name = _s(d.get("name"))
                if n == GOSK_ICON_FILE and not ICON_RE.search(name.lower()):
                    continue
                desc = _s(d.get("description"))
                if n in GOSK_BOOK_FILES and not BOOK_RE.search((name + " " + desc[:500]).lower()):
                    continue
                place = _s(d.get("productionPlace"))
                tech = [_s(t) for t in (d.get("technologies") or []) if t] if isinstance(d.get("technologies"), list) \
                    else [_s(d.get("technologies"))] if d.get("technologies") else []
                words = _s(d.get("mainWords"))
                authors = _s(d.get("authors"))
                text = " ".join([name, desc[:1500], place, " ".join(tech), words, authors]).lower()
                trads = match_traditions(text)
                peoples = match_peoples(" ".join([name, desc[:1500], place]).lower())
                if n == GOSK_ICON_FILE:
                    med = "icon painting"
                elif n in GOSK_BOOK_FILES:
                    med = "popular prints" if re.search(r"лубок|лубочн|картин", name.lower()) else "manuscript illumination"
                else:
                    med = medium_of(name, " ".join(tech), desc[:300])
                museum = _s((d.get("museum") or {}).get("name")) if isinstance(d.get("museum"), dict) else ""
                year = gosk_year(d)
                if not trads and not peoples:
                    if n == GOSK_ICON_FILE or n in GOSK_BOOK_FILES:
                        # unmatched icons / manuscripts still count towards a generic Russian cell
                        b = bucket(agg["people"], f"Russian (no school recorded) / {med}")
                        b["n"] += 1
                        b["museums"][museum] += 1
                        if year is not None and len(b["years"]) < 5000:
                            b["years"].append(year)
                        if len(b["samples"]) < MAX_EVIDENCE:
                            b["samples"].append([d.get("id"), name[:150], museum[:120], place[:80], year, med])
                    else:
                        if place:
                            agg["residual_place"][place.strip()[:80]] += 1
                        for t in tech:
                            agg["residual_tech"][t.strip().lower()[:60]] += 1
                    continue
                matched += 1
                keys = [("trad", str(i)) for i in trads] + [("people", f"{p} / {med}") for p in peoples]
                for table, k in keys:
                    b = bucket(agg[table], k)
                    b["n"] += 1
                    b["museums"][museum] += 1
                    b["media"][med] += 1
                    if place:
                        b["places"][place.strip()[:60]] += 1
                    if year is not None and len(b["years"]) < 5000:
                        b["years"].append(year)
                    if len(b["samples"]) < MAX_EVIDENCE:
                        b["samples"].append([d.get("id"), name[:150], museum[:120], place[:80], year, med])
                if progress and (seen % 200000 == 0):
                    pass
                if seen % 250000 == 0:
                    msg = f"  goskatalog data_{n}: {seen} records, {matched} matched, {time.time() - t0:.0f}s"
                    print(msg, flush=True)
        agg["files"][str(n)] = {"records": seen, "matched": matched}
        agg["records"] += seen
        agg["matched"] += matched
        print(f"  goskatalog data_{n} ({GOSK_FILES.get(n) or GOSK_BOOK_FILES.get(n) or 'painting: icons'}): "
              f"{seen} records, {matched} matched")
    for table in ("trad", "people"):
        for b in agg[table].values():
            b["museums"] = b["museums"].most_common(15)
            b["media"] = b["media"].most_common(6)
            b["places"] = b["places"].most_common(6)
    agg["residual_place"] = agg["residual_place"].most_common(400)
    agg["residual_tech"] = agg["residual_tech"].most_common(400)
    with open(cache + ".part", "w", encoding="utf-8") as f:
        json.dump(agg, f, ensure_ascii=False)
    os.replace(cache + ".part", cache)
    return agg


# ------------------------------------------------------------------ 3. Finna

FINNA_PEOPLE_QUERIES = {
    "Sami": "saamelainen", "Karelian": "karjalainen", "Veps": "vepsäläinen", "Ingrian / Izhorian": "inkeriläinen",
    "Komi": "komi", "Mari": "mari", "Udmurt": "udmurtti", "Mordvin (Erzya, Moksha)": "mordva",
    "Khanty": "hanti", "Mansi": "mansi", "Nenets": "nenetsi", "Estonian": "virolainen", "Seto": "setu",
    "Tatar": "tataari", "Chuvash": "tšuvassi", "Hungarian": "unkarilainen", "Russian": "venäläinen",
}
FINNA_TECHNIQUE_QUERIES = {  # discovery queries: Finnish folk techniques not in TRADITIONS
    "kansanomainen": "folk (general)", "kirjonta": "embroidery", "pitsi": "lace", "kudonta": "weaving",
    "kansanpuku": "costume", "puukaiverrus": "woodcarving", "rukinlapa": "woodcarving (distaffs)",
    "kansanmaalaus": "folk painting", "ristipisto": "cross stitch", "virkkaus": "crochet",
    "lapaset": "knitted mittens", "nauhapirta": "band weaving", "huopa": "felt", "pärekori": "basketry",
    "olkityö": "straw work", "tuohikontti": "birch bark", "luukaiverrus": "bone carving",
}


def finna_query(lookfor):
    params = [("lookfor", lookfor), ("filter[]", 'format:"0/PhysicalObject/"'), ("limit", "3"),
              ("facet[]", "building"), ("facet[]", "topic_facet"), ("facet[]", "geographic_facet"),
              ("field[]", "id"), ("field[]", "title"), ("field[]", "buildings"), ("field[]", "year")]
    url = FINNA_API + "?" + urllib.parse.urlencode(params)
    return fetch_json(url, os.path.join(FINNA_DIR, slug(lookfor) + ".json"))


def finna_summary(d):
    if not d:
        return None
    facets = d.get("facets") or {}
    top_b = collections.Counter()
    for x in facets.get("building", []):
        top_b[x.get("translated") or x["value"]] += x["count"]
    return {
        "n": d.get("resultCount", 0),
        "buildings": top_b.most_common(8),
        "topics": [(x["value"], x["count"]) for x in facets.get("topic_facet", [])[:8]],
        "places": [(x["value"], x["count"]) for x in facets.get("geographic_facet", [])[:6]],
        "samples": [(r.get("id"), r.get("title"), r.get("year")) for r in d.get("records", [])],
    }


def harvest_finna():
    out = {"trad": {}, "people": {}, "technique": {}}
    try:
        for i, t in enumerate(TRADITIONS):
            if t[4]:
                out["trad"][str(i)] = finna_summary(finna_query(t[4]))
        for p, q in FINNA_PEOPLE_QUERIES.items():
            out["people"][p] = finna_summary(finna_query(q))
        for q, lab in FINNA_TECHNIQUE_QUERIES.items():
            out["technique"][q] = finna_summary(finna_query(q))
    except PermissionError as e:
        print(f"Finna blocked ({e}); stopping this source", file=sys.stderr)
        out["blocked"] = str(e)
    n = sum(1 for tab in ("trad", "people", "technique") for v in out[tab].values() if v)
    print(f"Finna: {n} queries answered")
    return out


# --------------------------------------------------------- 4. cached museums

WEST = {"french", "italian", "british", "english", "german", "dutch", "flemish", "spanish", "portuguese",
        "austrian", "swiss", "belgian", "irish", "scottish", "welsh", "european", "venetian", "neapolitan",
        "sicilian", "maltese", "luxembourg"}
EAST_NORTH = {"norwegian", "swedish", "danish", "finnish", "icelandic", "faroese", "polish", "czech", "bohemian",
              "moravian", "slovak", "hungarian", "hungarian-slovak", "slovenian", "croatian", "serbian", "bosnian",
              "montenegrin", "macedonian", "albanian", "bulgarian", "romanian", "moldovan", "greek", "cypriot",
              "estonian", "latvian", "lithuanian", "ukrainian", "belarusian", "russian", "georgian", "armenian",
              "azerbaijani", "azerbaijan", "caucasian", "transylvanian", "dalmatian", "sami", "lapp", "tatar",
              "cossack", "kashubian", "sorbian", "breton", "basque", "alsatian", "tyrolean", "bavarian",
              "silesian", "scandinavian", "slavic", "balkan", "yugoslav", "karelian"}
FOLK_MEDIA = {"embroidery", "lace", "textiles", "costume", "ceramics", "toys", "painting (folk/decorative)",
              "woodcarving / woodwork", "decorated eggs", "birch bark / basketry", "carpets", "bone carving",
              "paper-cut / prints", "icon painting", "leather", "arms", "metalwork"}
CULTURE_COUNTRY = dict(DEMONYMS, **{"hungarian-slovak": "Hungary", "azerbaijan": "Azerbaijan",
                                    "transylvanian": "Romania", "dalmatian": "Croatia", "silesian": "Poland",
                                    "lapp": "Norway", "sami": "Norway", "tatar": "Russia", "cossack": "Russia",
                                    "karelian": "Russia", "yugoslav": "Serbia", "balkan": "", "luxembourg": "Luxembourg"})
ANCIENT_DEPTS = {"Greek and Roman Art", "Egyptian Art", "Ancient Near Eastern Art", "Ancient West Asian Art",
                 "Drawings and Prints", "Photographs", "The Libraries", "Medieval Art", "The Cloisters",
                 "Robert Lehman Collection", "European Paintings", "Modern and Contemporary Art", "Asian Art",
                 "Arts of Africa, Oceania, and the Americas", "The American Wing", "Islamic Art"}


def museum_object(source, oid, url, title, culture, place, cls, objname, medium_text, dept, begin, institution,
                  agg, evidence):
    """Classify one museum object; update aggregates. Returns True when kept."""
    cult_raw = culture or place or ""
    keys = culture_keys(cult_raw) if cult_raw else []
    bases = {k.split(", ")[0] for k, _ in keys}
    text = " ".join(x for x in (title, culture, place, cls, objname, medium_text) if x).lower()
    trads = match_traditions(text)
    peoples = match_peoples(" ".join(x for x in (title, culture, place) if x).lower())
    euro = [b for b in bases if b in EAST_NORTH or b in WEST or b in CULTURE_COUNTRY]
    if not euro and not peoples and not trads:
        return False
    if not euro and not peoples:
        # tradition match outside a European culture string (e.g. "Delft" on a Chinese export piece):
        # keep only when no non-European culture is named
        if bases:
            return False
    med = medium_of(objname, cls, title, medium_text)
    folk = bool(FOLK_SIGNAL.search(text))
    east = any(b in EAST_NORTH for b in euro) or bool(peoples)
    if not trads and not (folk or (east and med in FOLK_MEDIA)):
        return False
    cells = [("trad", str(i)) for i in trads]
    for p in peoples:
        cells.append(("people", f"{p} / {med}"))
    if not peoples:
        for k, lab in keys:
            b = k.split(", ")[0]
            if b in euro and (folk or b in EAST_NORTH):
                cells.append(("culture", f"{lab} / {med}"))
    for table, k in cells:
        b = agg[table].setdefault(k, {"n": 0, "folk": 0, "inst": collections.Counter(), "years": [],
                                      "samples": [], "src": collections.Counter()})
        b["n"] += 1
        b["folk"] += folk
        b["inst"][institution] += 1
        b["src"][source] += 1
        if begin is not None:
            b["years"].append(begin)
        if len(b["samples"]) < 5:
            b["samples"].append(url)
        if len(evidence[(source, table, k)]) < MAX_EVIDENCE:
            evidence[(source, table, k)].append(
                {"source": source, "object_id": oid, "url": url, "title": (title or "")[:150],
                 "culture": (culture or place or "")[:80], "medium": med, "date": begin,
                 "institution": institution})
    return True


def to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def harvest_museums():
    agg = {"trad": {}, "people": {}, "culture": {}}
    evidence = collections.defaultdict(list)
    counts = collections.Counter()
    met = os.path.join(MUSEUMS, "MetObjects.csv")
    if os.path.exists(met):
        with open(met, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                dept = r.get("Department", "")
                if dept in ANCIENT_DEPTS:
                    continue
                oid = r.get("Object ID")
                url = r.get("Link Resource") or f"https://www.metmuseum.org/art/collection/search/{oid}"
                kept = museum_object("met", oid, url, r.get("Title"), r.get("Culture"),
                                     r.get("Country") or r.get("Region") or "", r.get("Classification"),
                                     r.get("Object Name"), r.get("Medium"), dept, to_int(r.get("Object Begin Date")),
                                     "The Metropolitan Museum of Art", agg, evidence)
                counts["met"] += kept
    aic_dir = os.path.join(MUSEUMS, "aic", "artic-api-data", "json", "artworks")
    if os.path.isdir(aic_dir):
        for fn in glob.glob(os.path.join(aic_dir, "*.json")):
            try:
                with open(fn, encoding="utf-8") as f:
                    d = json.load(f)
            except (OSError, ValueError):
                continue
            dept = d.get("department_title") or ""
            if re.search(r"prints and drawings|photograph|modern|contemporary|ancient|asian|africa|americas|"
                         r"painting and sculpture of europe", dept, re.I):
                continue
            kept = museum_object("aic", d.get("id"), f"https://www.artic.edu/artworks/{d.get('id')}",
                                 d.get("title"), "", d.get("place_of_origin"), d.get("classification_title"),
                                 d.get("artwork_type_title"), d.get("medium_display"), dept, d.get("date_start"),
                                 "Art Institute of Chicago", agg, evidence)
            counts["aic"] += kept
    for fn in glob.glob(os.path.join(RAW, "vam", "**", "*.json"), recursive=True):
        try:
            with open(fn, encoding="utf-8") as f:
                d = json.load(f)
        except (OSError, ValueError):
            continue
        for r in d.get("records", []):
            sid = r.get("systemNumber")
            if (("vam", sid)) in evidence:
                continue
            place = r.get("_primaryPlace") or ""
            title = r.get("_primaryTitle") or r.get("objectType") or ""
            date = (r.get("_primaryDate") or "")
            m = re.search(r"\d{3,4}", date)
            mt = r.get("materialsAndTechniques") or ""
            kept = museum_object("vam", sid, f"https://collections.vam.ac.uk/item/{sid}/", title, "", place, "",
                                 r.get("objectType"), mt, "", int(m.group()) if m else None,
                                 "Victoria and Albert Museum", agg, evidence)
            counts["vam"] += kept
    seen_cma = set()
    for fn in glob.glob(os.path.join(RAW, "cma", "*.json")):
        try:
            with open(fn, encoding="utf-8") as f:
                d = json.load(f)
        except (OSError, ValueError):
            continue
        for r in d.get("data", []):
            if r.get("id") in seen_cma:
                continue
            seen_cma.add(r.get("id"))
            cult = "; ".join(r.get("culture") or [])
            kept = museum_object("cma", r.get("id"), r.get("url") or "", r.get("title"), cult, "",
                                 r.get("type"), r.get("type"), r.get("technique"), r.get("department"),
                                 r.get("creation_date_earliest"), "Cleveland Museum of Art", agg, evidence)
            counts["cma"] += kept
    print(f"Museums (cached): kept objects {dict(counts)}; traditions {len(agg['trad'])}, "
          f"peoples x medium {len(agg['people'])}, cultures x medium {len(agg['culture'])}")
    return agg, evidence, counts


# --------------------------------------------------------- 5. Europeana (optional)

def harvest_europeana(labels):
    key = os.environ.get("EUROPEANA_API_KEY")
    if not key:
        print("Europeana: skipped (EUROPEANA_API_KEY not set)")
        return {}
    out = {}
    for lab in labels:
        params = {"wskey": key, "query": f'"{lab}"', "rows": "3", "profile": "minimal facets",
                  "facet": "DATA_PROVIDER", "qf": "TYPE:IMAGE"}
        url = EUROPEANA_API + "?" + urllib.parse.urlencode(params)
        cache_url = EUROPEANA_API + "?" + urllib.parse.urlencode({k: v for k, v in params.items() if k != "wskey"})
        path = os.path.join(EUROPEANA_DIR, hashlib.sha1(cache_url.encode()).hexdigest()[:16] + ".json")
        try:
            d = fetch_json(url, path)
        except PermissionError as e:
            print(f"Europeana blocked ({e})", file=sys.stderr)
            break
        if not d:
            continue
        prov = []
        for fc in d.get("facets", []):
            if fc.get("name") == "DATA_PROVIDER":
                prov = [(x["label"], x["count"]) for x in fc.get("fields", [])[:8]]
        out[lab] = {"n": d.get("totalResults", 0), "providers": prov,
                    "samples": [x.get("guid") for x in d.get("items", [])]}
    print(f"Europeana: {len(out)} labels queried")
    return out


# ------------------------------------------------------------ known in Met/AIC

GENERIC_TOKENS = set("""embroidery lace painting pottery ware ceramics ceramic style school icon icons folk art arts
craft crafts carving woodcarving miniature toy toys tradition traditional of the and de la le du del di da
technique work works rug rugs carpet carpets textile textiles weaving decorative russian costume figures
eggs egg shawl sashes knitting stitch printing on glass painted majolica maiolica faience scenes making
paper cuts""".split())


def load_known():
    """Met/AIC culture keys (build_traditions output) and their place tokens."""
    keys, sub_tokens, base = set(), collections.defaultdict(set), set()
    for path in (MET_CULTURES, MET_TRADITIONS):
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                k = r.get("key", "")
                keys.add(k)
                for part in re.split(r"[,/|]", k):
                    part = part.strip()
                    if part:
                        for tok in part.split():
                            if len(tok) >= 4:
                                sub_tokens[tok].add(k)
                if r.get("kind") == "culture" and ", " not in k:
                    base.add(k)
    return keys, sub_tokens, base


def known_status(label, known):
    keys, sub_tokens, base = known
    f = fold(label)
    if f in keys or f.replace(" / ", " / ") in keys:
        return "exact", f
    toks = [t for t in re.findall(r"[a-z]+", f) if t not in GENERIC_TOKENS and len(t) >= 4]
    for t in toks:
        if t in base or t.rstrip("s") in base:
            continue
        for cand in (t, t[:-1], t.rstrip("ware"), t[:5]):
            if len(cand) >= 4 and cand in sub_tokens:
                hits = sorted(sub_tokens[cand], key=len)
                # place-level hit only when the token is a sub-key (e.g. "dutch, delft"), not a base culture
                sub_hits = [h for h in hits if ", " in h and cand in h.split(", ", 1)[1]]
                if sub_hits:
                    return "place", sub_hits[0]
    for t in re.findall(r"[a-z-]+", f):
        if t in base:
            return "base_only", t
    return "no", ""


# ------------------------------------------------------------------ outputs

def period_of(years):
    ys = sorted(y for y in years if y is not None and -3000 < y < 2100)
    if not ys:
        return ""
    if len(ys) < 3:
        return f"c. {ys[0]}"
    q = statistics.quantiles(ys, n=10)
    return f"{int(q[0])}-{int(q[-1])} (median {int(statistics.median(ys))})"


def region_of_countries(cs):
    regs = []
    for c in cs:
        r = REGION_OF.get(c) or ("Caucasus" if c == "Caucasus" else "")
        if r and r not in regs:
            regs.append(r)
    return "; ".join(regs)


def write(path, rows, fields):
    with open(path + ".part", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    os.replace(path + ".part", path)


def topfmt(pairs, n=5):
    return "; ".join(f"{k} ({v})" for k, v in list(pairs)[:n] if k)


def build_outputs(wd, link, gosk, finna, museums, europeana, ms_ev=None):
    known = load_known()
    nodes = {}

    def node(key, **kw):
        n = nodes.get(key)
        if n is None:
            n = nodes[key] = {"node_key": key, "kind": kw.get("kind", ""), "label": "", "qid": "", "label_ru": "",
                              "country": "", "people": "", "region": "", "medium": "", "years": [],
                              "sources": set(), "institutions": collections.Counter(), "samples": [],
                              "wd_sitelinks": "", "wd_enwiki": "", "wd_classes": "", "wd_description": "",
                              "ich_designation": "", "heritage_designation": "", "wd_linked_works": 0,
                              "wikidata_objects": 0, "goskatalog_objects": 0, "finna_objects": 0, "met_objects": 0, "aic_objects": 0,
                              "vam_objects": 0, "cma_objects": 0, "europeana_objects": 0, "folk_share": "",
                              "top_places": "", "notes": ""}
        for k, v in kw.items():
            if v not in (None, "") and not n.get(k):
                n[k] = v
        return n

    # Wikidata nodes; pattern nodes linked to a QID share that node
    q_to_key = {}
    for q, k in wd.items():
        key = f"wd:{q}"
        q_to_key[q] = key
        n = node(key, kind="wikidata", label=k["label"], qid=q, label_ru=k["label_ru"],
                 country="; ".join(k["countries"]), people="; ".join(k["peoples"]),
                 region=region_of_countries(k["countries"]), medium=k["medium"])
        n["sources"].add("wikidata")
        n.update(wd_sitelinks=k["sitelinks"], wd_enwiki=k["enwiki"], wd_classes=k["classes"][:300],
                 wd_description=k["description"][:200], ich_designation="; ".join(k["ich"]),
                 heritage_designation="; ".join(k["heritage"]), wd_linked_works=k["wd_works"])
        if k["year"] is not None:
            n["years"].append(k["year"])
        n["institutions"].update(k["wd_collections"])
        if k["enwiki"]:
            n["samples"].append(k["enwiki"])
    for i, t in enumerate(TRADITIONS):
        q = link.get(i)
        key = q_to_key.get(q) or f"pattern:{slug(t[0])}"
        n = node(key, kind="pattern", label=t[0], qid=q or "", country=t[1], medium=t[2],
                 region=region_of_countries([c.strip() for c in t[1].split(";")]))
        n["pattern_label"] = t[0]
        if key.startswith("wd:"):
            n["medium"] = t[2]   # the curated medium beats the class-derived one
            n["notes"] = (n["notes"] + "; " if n["notes"] else "") + f"pattern '{t[0]}'"
        n.setdefault("_trad", []).append(i)

    def trad_node(i):
        q = link.get(i)
        return nodes[q_to_key.get(q) or f"pattern:{slug(TRADITIONS[i][0])}"]

    def people_node(cell):
        people, med = cell.split(" / ", 1)
        p = PEOPLE_INFO.get(people)
        return node(f"people:{slug(people)}:{slug(med)}", kind="people_medium", label=f"{people} / {med}",
                    people=people, country=p[1] if p else "", region=p[2] if p else "", medium=med)

    # Wikidata manuscripts (Armenian, Georgian, Slavonic) -> manuscript-illumination patterns
    lab_index = {t[0]: i for i, t in enumerate(TRADITIONS)}
    for lab, e in (ms_ev or {}).items():
        n = trad_node(lab_index[lab])
        n["wikidata_objects"] += e["n"]
        n["sources"].add("wikidata")
        n["institutions"].update(e["colls"])
        n["years"].extend(e["years"])
        n["samples"].extend(e["samples"][:3])
    # Goskatalog
    if gosk:
        for table in ("trad", "people"):
            for k, b in gosk[table].items():
                n = trad_node(int(k)) if table == "trad" else people_node(k)
                n["goskatalog_objects"] += b["n"]
                n["sources"].add("goskatalog")
                n["institutions"].update(dict(b["museums"]))
                n["years"].extend(b["years"])
                n["samples"].extend(GOSK_OBJECT_URL.format(s[0]) for s in b["samples"][:3])
                if b["places"] and not n["top_places"]:
                    n["top_places"] = topfmt(b["places"], 4)
    # Finna
    if finna:
        for i, s in finna.get("trad", {}).items():
            if s and s["n"]:
                n = trad_node(int(i))
                n["finna_objects"] += s["n"]
                n["sources"].add("finna")
                n["institutions"].update(dict(s["buildings"]))
                n["samples"].extend(FINNA_RECORD_URL.format(x[0]) for x in s["samples"][:2])
        for p, s in finna.get("people", {}).items():
            if s and s["n"]:
                n = node(f"people:{slug(p)}:finna", kind="people_medium", label=f"{p} / objects (Finna)", people=p,
                         country=PEOPLE_INFO[p][1] if p in PEOPLE_INFO else "",
                         region=PEOPLE_INFO[p][2] if p in PEOPLE_INFO else "Central Europe", medium="mixed")
                n["finna_objects"] += s["n"]
                n["sources"].add("finna")
                n["institutions"].update(dict(s["buildings"]))
                n["top_places"] = topfmt(s["topics"], 6)
                n["samples"].extend(FINNA_RECORD_URL.format(x[0]) for x in s["samples"][:2])
        for q, s in finna.get("technique", {}).items():
            if s and s["n"]:
                lab = FINNA_TECHNIQUE_QUERIES[q]
                n = node(f"finna:{slug(q)}", kind="technique", label=f"Finnish {lab} ({q})", country="Finland",
                         region="Nordic", medium=lab)
                n["finna_objects"] += s["n"]
                n["sources"].add("finna")
                n["institutions"].update(dict(s["buildings"]))
                n["top_places"] = topfmt(s["topics"], 6)
                n["samples"].extend(FINNA_RECORD_URL.format(x[0]) for x in s["samples"][:2])
    # Museums
    mus_agg, evidence, _ = museums if museums else ({"trad": {}, "people": {}, "culture": {}}, {}, None)
    for table in ("trad", "people", "culture"):
        for k, b in mus_agg[table].items():
            if table == "trad":
                n = trad_node(int(k))
            elif table == "people":
                n = people_node(k)
            else:
                cult, med = k.split(" / ", 1)
                base = fold(cult.split(",")[0])
                ctry = CULTURE_COUNTRY.get(base, "")
                n = node(f"culture:{slug(cult)}:{slug(med)}", kind="culture_medium", label=k, country=ctry,
                         region=region_of_countries([ctry]), medium=med)
            for src, c in b["src"].items():
                n[f"{src}_objects"] += c
                n["sources"].add(src)
            n["institutions"].update(b["inst"])
            n["years"].extend(b["years"])
            n["samples"].extend(b["samples"][:3])
            n["_folk"] = n.get("_folk", 0) + b["folk"]
            n["_mus"] = n.get("_mus", 0) + b["n"]
    for lab, s in (europeana or {}).items():
        for n in nodes.values():
            if n.get("pattern_label") == lab:
                n["europeana_objects"] = s["n"]
                n["sources"].add("europeana")
                n["institutions"].update(dict(s["providers"]))

    rows = []
    count_cols = ["wikidata_objects", "goskatalog_objects", "finna_objects", "met_objects", "aic_objects", "vam_objects",
                  "cma_objects", "europeana_objects"]
    for n in nodes.values():
        total = sum(n[c] for c in count_cols)
        if n["kind"] == "pattern" and not total and not n["qid"]:
            continue   # a named tradition no source evidenced
        if n["kind"] in ("people_medium", "culture_medium") and total < 3:
            continue   # noise floor for cells
        status, match = known_status(n.get("pattern_label") or n["label"], known)
        if n["kind"] == "culture_medium":
            status, match = ("base_only", fold(n["label"].split(" / ")[0])) if status == "no" else (status, match)
        row = dict(n)
        row.update(
            sources="; ".join(sorted(n["sources"])), total_objects=total, period=period_of(n["years"]),
            top_institutions=topfmt(n["institutions"].most_common(6), 6),
            n_institutions=len(n["institutions"]),
            sample_object_urls=" ".join(dict.fromkeys(n["samples"]))[:900],
            folk_share=f"{n['_folk'] / n['_mus']:.2f}" if n.get("_mus") else "",
            known_in_met_aic=status, met_aic_match=match,
            is_new_node="yes" if status in ("no", "base_only") else "no")
        rows.append(row)
    kind_order = {"wikidata": 0, "pattern": 1, "people_medium": 2, "culture_medium": 3, "technique": 4}
    rows.sort(key=lambda r: (kind_order.get(r["kind"], 9), -(int(r["wd_sitelinks"] or 0)), -r["total_objects"]))
    fields = ["node_key", "kind", "label", "qid", "label_ru", "country", "people", "region", "medium", "period",
              "sources", "total_objects"] + count_cols + [
              "wd_linked_works", "n_institutions", "top_institutions", "ich_designation", "heritage_designation",
              "wd_sitelinks", "wd_enwiki", "wd_description", "wd_classes", "folk_share", "top_places",
              "sample_object_urls", "known_in_met_aic", "met_aic_match", "is_new_node", "notes"]
    os.makedirs(OUT_DIR, exist_ok=True)
    write(os.path.join(OUT_DIR, "europe_folk_traditions.csv"), rows, fields)

    # slim evidence rows
    ev = []
    key_of = {}
    for n in nodes.values():
        for i in n.get("_trad", []):
            key_of[("trad", str(i))] = n["node_key"]
    if gosk:
        for table in ("trad", "people"):
            for k, b in gosk[table].items():
                nk = key_of.get((table, k)) if table == "trad" else people_node(k)["node_key"]
                for s in b["samples"]:
                    ev.append({"source": "goskatalog", "node_key": nk, "object_id": s[0],
                               "url": GOSK_OBJECT_URL.format(s[0]), "title": s[1], "institution": s[2],
                               "culture": s[3], "date": s[4], "medium": s[5]})
    for (src, table, k), items in (evidence or {}).items():
        if table == "trad":
            nk = key_of.get(("trad", k))
        elif table == "people":
            nk = people_node(k)["node_key"]
        else:
            cult, med = k.split(" / ", 1)
            nk = f"culture:{slug(cult)}:{slug(med)}"
        for it in items:
            ev.append(dict(it, node_key=nk))
    if finna:
        for i, s in finna.get("trad", {}).items():
            if s:
                for x in s["samples"]:
                    ev.append({"source": "finna", "node_key": key_of.get(("trad", i)), "object_id": x[0],
                               "url": FINNA_RECORD_URL.format(x[0]), "title": x[1], "date": x[2]})
    write(os.path.join(OUT_DIR, "europe_folk_objects.csv"), ev,
          ["source", "node_key", "object_id", "url", "title", "culture", "medium", "date", "institution"])
    if gosk:
        res = [{"kind": "production_place", "value": k, "objects": v} for k, v in gosk["residual_place"]] + \
              [{"kind": "technology", "value": k, "objects": v} for k, v in gosk["residual_tech"]]
        write(os.path.join(OUT_DIR, "europe_folk_goskatalog_residual.csv"), res, ["kind", "value", "objects"])
    return rows, ev


def report(rows, ev):
    by_kind = collections.Counter(r["kind"] for r in rows)
    new = collections.Counter(r["kind"] for r in rows if r["is_new_node"] == "yes")
    print(f"\nWrote {len(rows)} candidate nodes ({dict(by_kind)}), {len(ev)} evidence rows")
    print(f"NEW vs Met/AIC culture keys (known_in_met_aic in no/base_only): {sum(new.values())} ({dict(new)})")
    print("known status:", dict(collections.Counter(r["known_in_met_aic"] for r in rows)))
    named = [r for r in rows if r["kind"] in ("wikidata", "pattern")]
    cov = collections.Counter()
    for r in named:
        for c in {c.strip() for c in r["country"].split(";") if c.strip()}:
            cov[c] += 1
    print("Named tradition nodes per country:", ", ".join(f"{c} {v}" for c, v in cov.most_common()))
    modern = ["Norway", "Sweden", "Denmark", "Finland", "Iceland", "United Kingdom", "Ireland", "France", "Belgium",
              "Netherlands", "Luxembourg", "Germany", "Austria", "Switzerland", "Poland", "Czech Republic",
              "Slovakia", "Hungary", "Slovenia", "Spain", "Portugal", "Italy", "Malta", "Greece", "Cyprus",
              "Croatia", "Serbia", "Bosnia and Herzegovina", "Montenegro", "North Macedonia", "Albania",
              "Bulgaria", "Romania", "Moldova", "Kosovo", "Estonia", "Latvia", "Lithuania", "Ukraine", "Belarus",
              "Russia", "Georgia", "Armenia", "Azerbaijan"]
    thin = [f"{c} ({cov.get(c, 0) + cov.get('Czechia', 0) if c == 'Czech Republic' else cov.get(c, 0)})"
            for c in modern if (cov.get(c, 0) + (cov.get("Czechia", 0) if c == "Czech Republic" else 0)) <= 1]
    print("Countries with 0-1 named tradition nodes:", ", ".join(thin) or "none")
    pcov = collections.Counter()
    for r in rows:
        if r["people"]:
            for p in r["people"].split("; "):
                pcov[p] += 1
    thin_p = [p[0] for p in PEOPLES if pcov.get(p[0], 0) <= 1]
    print("Peoples with 0-1 nodes:", ", ".join(thin_p) or "none")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skip", default="", help="comma list of wikidata,goskatalog,finna,museums")
    ap.add_argument("--delay", type=float, default=1.0)
    ap.add_argument("--no-icons", action="store_true", help="skip the Goskatalog painting file (icons)")
    args = ap.parse_args()
    DELAY[0] = max(1.0, args.delay)
    skip = set(filter(None, args.skip.split(",")))
    wd, ms_ev = harvest_wikidata() if "wikidata" not in skip else ({}, {})
    link = link_patterns_to_wikidata(wd) if "wikidata" not in skip else {}
    print(f"Patterns linked to Wikidata: {len(link)} of {len(TRADITIONS)}")
    gosk = harvest_goskatalog(icons=not args.no_icons) if "goskatalog" not in skip else None
    finna = harvest_finna() if "finna" not in skip else None
    museums = harvest_museums() if "museums" not in skip else None
    europeana = harvest_europeana([t[0] for t in TRADITIONS])
    rows, ev = build_outputs(wd, link, gosk, finna, museums, europeana, ms_ev)
    report(rows, ev)


if __name__ == "__main__":
    main()
