"""Regional sweeps for South and Southeast Asia, Africa, and the Indigenous
Americas and Oceania (visual-art-plan.md §2, §2A, §2.1 point 4, §2.2).

These cells are largely tradition-led (§2.1 point 4): the primary nodes are
schools, cultures, dynasties and workshops (Mewar, Kangra/Pahari, Deccani,
Company painting; Gupta, Chola, Pala sculpture; Khmer, Champa, Majapahit;
Yoruba, Benin court, Kuba; Moche, Maya, Haida; Maori, Asmat, ...), and named
masters (Nainsukh, Manaku, Olowe of Ise, the "Master of Buli") hang under
them. This script harvests collections that record those labels and measures
the attribution profile (share of objects with a named maker) per tradition,
as the coverage audit (§2.2) asks.

Sources (every request is cached gzip-compressed under
data/raw/regional/<region-dir>/<source>/ and spaced ~1 s apart; re-runs read
the cache, so the harvest is resumable):

  V&A Collections API v2 (api.vam.ac.uk, no key)
      South & SE Asia: the whole "South & South East Asia Collection"
      (id_collection THES48598, ~45k records), split by year range so no query
      passes the API's 10,000-record cap, plus place-of-origin sweeps for
      South/SE Asian places in the other collections (Company painting sits in
      Prints, Drawings & Paintings). Africa, Americas, Oceania: place-of-origin
      sweeps. q_place_name is a fuzzy text match, so every record is re-checked
      against the region's place lexicon; in settler countries (Canada, USA,
      Australia, New Zealand, South Africa, Latin America after 1550) a record
      is kept only with an Indigenous culture term. The V&A `styles` field
      carries the school / dynasty label (Mewar, Kangra, Chola, Company, ...),
      often with a Getty AAT id. Pages are reduced to the fields used before
      they are cached. The Islamic-world job owns data/raw/regional/vam/.
  Cleveland Museum of Art open-access API, by department: Indian and Southeast
      Asian Art, African Art, Art of the Americas, Oceania, plus Textiles
      filtered by culture. `culture` is a hierarchy string ("Africa, Central
      Africa, Cameroon, Bangwa Kingdom"; "India, Rajasthan, Mewar, 18th
      century"); makers come from `creators`.
  Art Institute of Chicago dump on disk (data/raw/museums/aic/artic-api-data/
      json/artworks/*.json): place_of_origin, style_title and artist_display.
      AIC files cultures as agents ("Kuba", "Moche"), so an artist counts as a
      named maker only when it is not a culture term and not a placeholder.
  Rijksmuseum data services (data.rijksmuseum.nl, keyless Linked Art): the
      search API has no place filter, so a short list of keyword searches
      (Majapahit, Shiva, kris, Ceylon, Benin, Asmat, ...) is run and each hit
      is fetched and kept only if its production place is in a region.
      Capped at --rijks-max objects.
  British Museum: no bulk or LOD route. The SPARQL endpoint
      (collection.britishmuseum.org) has been offline since 2021 and the
      collection-search API sits behind a Cloudflare challenge; reported as
      unreachable, not harvested.
  Smithsonian (NMAA, NMAfA, NMAI) is harvested by pipelines/regional/smithsonian.py.
  Mughal painting is owned by the Islamic-world job; Mughal, Awadh and Deccani
      objects that fall into these sweeps are kept but flagged (overlap =
      islamic_world). Nepal, Tibet, Bhutan, Gandhara and NW Pakistan are flagged
      overlap = himalaya_central_asia (pipelines/regional/himalaya_central_asia.py).

Filters: photographs, objects made 1960 or later, objects whose named makers are
all Western (European/American artists depicting the region: comma-inverted V&A
names, "(English, ...)" nationalities, military titles, a short reviewed list),
records from settler countries without an Indigenous culture term, and V&A
records from out-of-scope collections (East Asia, Middle East, photography,
theatre, library) are dropped; counts per reason go to the _dropped file.

Outputs (data/interim/regional/), for region in south_southeast_asia, africa,
americas_oceania:
  <region>_objects.csv     one row per object: source, id, title, subregion,
                           country, tradition (culture/school), period/dynasty,
                           object type, labels as recorded, date text and
                           begin/end, makers (named only), attributed flag,
                           materials, institution, url
  <region>_traditions.csv  kind = culture | culture_period | culture_type |
                           culture_period_type | period: objects per source,
                           n_sources, attributed share, date range and mid-date
                           quantiles, top object types / raw labels / named
                           makers, overlap flag, example ids
  <region>_makers.csv      named makers with objects, sources, traditions,
                           periods, roles, date range, example ids
  south_asia_africa_americas_sources.csv  per region x source: objects,
                           attributed share, culture / period / date coverage,
                           overlap counts
  south_asia_africa_americas_dropped.csv  records dropped, per source and reason

Usage: python3 pipelines/regional/south_asia_africa_americas.py
           [--skip vam,cma,aic,rijks] [--fetch-only] [--delay 1.0] [--rijks-max 1500]
"""
import argparse
import collections
import csv
import functools
import glob
import gzip
import json
import os
import re
import statistics
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw", "regional")
OUT_DIR = os.path.join(ROOT, "data", "interim", "regional")
AIC_DIR = os.path.join(ROOT, "data", "raw", "museums", "aic", "artic-api-data", "json", "artworks")
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"

sys.path.insert(0, os.path.join(ROOT, "pipelines", "unattributed"))
from build_traditions import fold as _bt_fold, tidy  # noqa: E402


def fold(s):
    """build_traditions.fold, but Unicode dashes become hyphens first ("Lobi–style" -> "lobi-style")."""
    return _bt_fold(re.sub(r"[\u2010-\u2015\u2212]", "-", s or ""))

VAM_API = "https://api.vam.ac.uk/v2/objects/search"
VAM_OBJECT_URL = "https://collections.vam.ac.uk/item/{}/"
VAM_MAX = 10000
VAM_PAGE = 100
CMA_API = "https://openaccess-api.clevelandart.org/api/artworks/"
CMA_FIELDS = ("id,accession_number,title,culture,creators,type,technique,creation_date,"
              "creation_date_earliest,creation_date_latest,department,collection,url")
RIJKS_SEARCH = "https://data.rijksmuseum.nl/search/collection"

REGIONS = ("south_southeast_asia", "africa", "americas_oceania")
REGION_DIR = {"south_southeast_asia": "south_asia", "africa": "africa", "americas_oceania": "americas_oceania"}

# --------------------------------------------------------------------- fetching

_last = [0.0]
DELAY = [1.0]
NET = collections.Counter()


def _get(url, accept="application/json"):
    for attempt in range(5):
        wait = DELAY[0] - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                NET["ok"] += 1
                return r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code in (400, 404, 410, 422):
                NET[f"http_{e.code}"] += 1
                print(f"  {e.code} {url}", file=sys.stderr)
                return None
            print(f"  {e.code} {url} (retry {attempt + 1})", file=sys.stderr)
        except Exception as e:  # URLError, timeouts, resets, incomplete reads
            print(f"  {type(e).__name__}: {e} {url} (retry {attempt + 1})", file=sys.stderr)
        time.sleep(min(60, 5 * 2 ** attempt))
    NET["failed"] += 1
    return None


def cached_json(url, path, reduce=None, accept="application/json", ok=None):
    """GET url as JSON, reduce it, cache the result gzip-compressed at path(.json.gz).
    ok(data) -> False marks a transient bad answer (e.g. an empty page): it is
    retried and never cached."""
    if os.path.exists(path):
        try:
            with gzip.open(path, "rt", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError, EOFError):
            os.remove(path)
    for attempt in range(3):
        text = _get(url, accept)
        if text is None:
            return None
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            NET["bad_json"] += 1
            data = None
        if data is not None and reduce:
            data = reduce(data)
        if data is not None and (ok is None or ok(data)):
            break
        NET["retried_bad_answer"] += 1
        time.sleep(10 * (attempt + 1))
    else:
        return data
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path + ".part", "wt", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(path + ".part", path)
    return data


def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")[:120]


def to_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        try:
            return int(float(v))
        except (TypeError, ValueError):
            return None


# ------------------------------------------------------------------ lexicons
# Places -> (region, subregion, country). Matched as whole folded words/phrases
# against place text; first (longest) match wins.

PLACES = {
    "south_southeast_asia": {
        "South Asia": [
            "india", "indian subcontinent", "pakistan", "bangladesh", "sri lanka", "ceylon", "nepal", "bhutan",
            "kathmandu", "kathmandu valley", "rajasthan", "mewar", "udaipur", "jaipur", "kota", "bundi",
            "kishangarh", "bikaner", "jodhpur", "marwar", "nathdwara", "deogarh", "devgarh", "sawar", "uniara",
            "ajmer", "alwar", "malwa", "bundelkhand", "datia", "orchha", "punjab", "punjab hills", "pahari",
            "kangra", "guler", "basohli", "chamba", "mandi", "kulu", "kullu", "nurpur", "bilaspur", "jammu",
            "jasrota", "mankot", "garhwal", "tehri garhwal", "himachal pradesh", "kashmir", "srinagar", "ladakh",
            "deccan", "golconda", "golkonda", "bijapur", "ahmadnagar", "hyderabad", "aurangabad", "bidar",
            "mysore", "karnataka", "tamil nadu", "thanjavur", "tanjore", "madurai", "tiruchirappalli", "trichinopoly",
            "chennai", "madras", "kerala", "travancore", "andhra pradesh", "telangana", "orissa", "odisha", "puri",
            "bengal", "west bengal", "calcutta", "kolkata", "murshidabad", "patna", "bihar", "nalanda", "kurkihar",
            "uttar pradesh", "mathura", "sarnath", "lucknow", "awadh", "oudh", "faizabad", "benares", "varanasi",
            "agra", "delhi", "old delhi", "new delhi", "fatehpur sikri", "madhya pradesh", "gwalior", "khajuraho",
            "sanchi", "bharhut", "gujarat", "ahmedabad", "ahmadabad", "surat", "kutch", "kachchh", "cambay",
            "khambhat", "maharashtra", "bombay", "mumbai", "pune", "poona", "ajanta", "ellora", "goa", "assam",
            "manipur", "sindh", "sind", "lahore", "multan", "peshawar", "taxila", "gandhara", "swat",
            "north india", "south india", "central india", "western india", "eastern india", "southeast india",
            "northern india", "southern india", "himalayas", "himalaya", "western himalayas", "tibet", "western tibet",
            "central tibet", "eastern tibet", "lhasa", "sikkim", "dhaka", "dacca", "kandy", "jaffna", "anuradhapura",
            "polonnaruwa", "ahmednagar", "burhanpur", "rajput", "kotah", "bengal presidency", "amritsar",
            "voor-indie", "brits-indie", "coromandel", "coromandelkust", "bengalen", "malabar",
        ],
        "Southeast Asia": [
            "southeast asia", "south east asia", "mainland southeast asia", "cambodia", "kampuchea", "angkor",
            "thailand", "siam", "ayutthaya", "sukhothai", "lopburi", "bangkok", "chiang mai", "lan na", "lanna",
            "laos", "luang prabang", "vietnam", "viet nam", "annam", "champa", "tonkin", "cochin china", "hue",
            "myanmar", "burma", "pagan", "bagan", "mandalay", "rangoon", "yangon", "ava", "arakan", "shan state",
            "kachin state", "pyu", "indonesia", "java", "central java", "east java", "eastern java", "west java",
            "bali", "lombok", "sumatra", "borneo", "kalimantan", "sulawesi", "celebes", "moluccas", "maluku",
            "flores", "sumba", "timor", "nias", "dutch east indies", "netherlands indies", "yogyakarta",
            "jogjakarta", "surakarta", "solo", "cirebon", "madura", "cambodja", "birma", "indonesie",
            "nederlands-indie", "oost-java", "midden-java", "west-java", "candi", "tjandi", "atjeh", "celebes", "malaysia", "malaya", "malay peninsula",
            "penang", "malacca", "melaka", "sarawak", "sabah", "brunei", "singapore", "philippines", "luzon",
            "mindanao", "sulu", "dvaravati", "srivijaya", "majapahit", "khmer",
        ],
    },
    "africa": {
        "West Africa": [
            "west africa", "western africa", "nigeria", "benin city", "ile-ife", "ife", "igbo-ukwu", "nok",
            "yorubaland", "ghana", "gold coast", "asante", "ashanti", "kumasi", "cote d ivoire", "cote divoire",
            "ivory coast", "goudkust", "mali", "bandiagara", "djenne", "jenne", "timbuktu", "burkina faso", "upper volta",
            "senegal", "gambia", "guinea", "guinea-bissau", "sierra leone", "liberia", "togo", "republic of benin",
            "dahomey", "abomey", "niger", "cameroon", "cameroon grassfields", "grassfields", "bamum", "foumban",
            "mauritania", "korhogo", "lagos", "ibadan", "calabar", "oyo", "abeokuta", "ikere", "owo", "benin kingdom",
            "kingdom of benin", "sahel", "northern africa and the sahel", "western sudan",
        ],
        "Central Africa": [
            "central africa", "democratic republic of the congo", "democratic republic of congo", "congo",
            "zaire", "belgian congo", "belgisch-congo", "republic of the congo", "congo brazzaville", "gabon", "angola", "cabinda",
            "central african republic", "chad", "equatorial guinea", "fernando po", "bioko", "kasai", "kongo",
            "loango", "zambia", "northern rhodesia",
        ],
        "Eastern and Southern Africa": [
            "east africa", "eastern africa", "eastern and southern africa", "southern africa", "south africa",
            "kenya", "tanzania", "tanganyika", "zanzibar", "uganda", "rwanda", "burundi", "ethiopia", "abyssinia",
            "eritrea", "somalia", "somaliland", "djibouti", "sudan", "south sudan", "southern sudan", "nubia",
            "madagascar", "malawi", "mozambique", "zimbabwe", "rhodesia", "southern rhodesia", "botswana",
            "namibia", "lesotho", "swaziland", "eswatini", "natal", "zululand", "kwazulu-natal", "transvaal",
            "cape colony", "cape of good hope", "great zimbabwe", "gondar", "lalibela", "aksum", "axum", "maqdala",
            "magdala", "zuid-afrika", "abessinie",
        ],
        "Africa (unspecified)": ["africa", "sub-saharan africa", "african"],
    },
    "americas_oceania": {
        "North America": [
            "north america", "united states", "usa", "canada", "alaska", "arctic", "british columbia",
            "northwest coast", "pacific northwest", "southwest", "american southwest", "new mexico", "arizona",
            "plains", "great plains", "great lakes", "woodlands", "eastern woodlands", "california", "nunavut",
            "greenland", "labrador", "hudson bay", "pueblo of acoma", "acoma", "zuni", "hopi", "san ildefonso",
            "santa clara", "cochiti", "mississippi", "ohio", "oklahoma", "dakota", "montana", "wyoming", "nevada",
            "oregon", "washington state", "queen charlotte islands", "haida gwaii",
        ],
        "Mesoamerica": [
            "mesoamerica", "mexico", "west mexico", "western mexico", "guatemala", "belize", "honduras",
            "el salvador", "yucatan", "chiapas", "oaxaca", "veracruz", "veracruz state", "colima", "colima state",
            "jalisco", "nayarit", "nayarit state", "guerrero", "teotihuacan", "tenochtitlan", "puebla",
            "campeche", "tabasco", "palenque", "copan",
        ],
        "Central America and Caribbean": [
            "central america", "costa rica", "panama", "nicaragua", "caribbean", "antilles", "puerto rico",
            "hispaniola", "dominican republic", "haiti", "cuba", "jamaica", "bahamas", "greater nicoya", "cocle",
        ],
        "South America": [
            "south america", "andes", "andean", "peru", "peruvian north coast", "peruvian south coast",
            "southern peru", "northern peru", "central coast", "north coast", "south coast", "nazca valley",
            "nasca", "moche valley", "lambayeque", "cusco", "cuzco", "bolivia", "ecuador", "colombia", "chile",
            "argentina", "venezuela", "brazil", "amazon", "amazonia", "guyana", "british guiana", "suriname",
            "surinam", "french guiana", "paraguay", "uruguay", "tierra del fuego", "patagonia", "tiwanaku",
            "tiahuanaco", "lake titicaca",
        ],
        "Oceania": [
            "oceania", "pacific islands", "pacific", "south pacific", "melanesia", "polynesia", "micronesia",
            "new guinea", "papua new guinea", "papua", "nieuw-guinea", "papoea-nieuw-guinea", "west papua", "irian jaya", "sepik", "sepik river",
            "middle sepik", "lower sepik", "massim", "trobriand islands", "new ireland", "new britain",
            "admiralty islands", "solomon islands", "vanuatu", "new hebrides", "new caledonia", "fiji", "samoa",
            "tonga", "cook islands", "tahiti", "society islands", "marquesas", "marquesas islands", "hawaii",
            "hawaiian islands", "new zealand", "aotearoa", "rapa nui", "easter island", "austral islands",
            "caroline islands", "marshall islands", "kiribati", "gilbert islands", "nauru", "palau", "belau",
            "torres strait", "torres strait islands", "australia", "arnhem land", "northern territory",
            "western australia", "queensland", "asmat", "lake sentani", "gulf province", "huon gulf",
            "bismarck archipelago", "santa cruz islands", "tuvalu", "mangareva", "chuuk", "yap",
        ],
    },
}

# Regions owned by other jobs (Islamic world, ancient Mediterranean/Egypt, East Asia).
EXCLUDE_PLACES = ["north africa", "coptic", "egypt", "morocco", "algeria", "tunisia", "libya", "iran", "persia", "iraq", "syria",
                  "turkey", "afghanistan", "china", "japan", "korea", "mongolia", "uzbekistan",
                  "iranian", "persian", "qajar", "safavid", "timurid", "ottoman", "chinese", "japanese", "ming",
                  "qing", "longquan", "isfahan", "europe", "european", "england", "english", "london", "france",
                  "french", "netherlands", "dutch", "germany", "italy"]

# settler/colonial countries: keep only with an Indigenous culture term (or pre-1550 in Latin America)
SETTLER = {"united states", "usa", "canada", "australia", "new zealand", "south africa", "north america",
           "mexico", "peru", "brazil", "argentina", "chile", "colombia", "ecuador", "bolivia", "venezuela",
           "guatemala", "cuba", "jamaica", "haiti", "dominican republic", "puerto rico", "panama", "costa rica",
           "paraguay", "uruguay", "honduras", "el salvador", "nicaragua", "belize", "suriname", "surinam",
           "guyana", "british guiana", "french guiana", "hawaii", "hawaiian islands", "natal", "cape colony",
           "transvaal", "puebla", "mexico city", "caribbean", "south america", "central america", "mesoamerica",
           "plains", "southwest", "ohio", "mississippi", "california", "oklahoma", "arizona", "new mexico",
           "washington state", "oregon", "montana", "wyoming", "nevada", "dakota", "alaska", "british columbia",
           "greenland", "western australia", "queensland", "northern territory", "zimbabwe", "rhodesia",
           "southern rhodesia", "kenya", "namibia"}

_place_index = []
for region, subs in PLACES.items():
    for sub, names in subs.items():
        for n in names:
            _place_index.append((fold(n), region, sub))
_place_index.sort(key=lambda x: -len(x[0]))
_PLACE_RE = [(re.compile(r"(?<![a-z])" + re.escape(n).replace(r"\ ", r"[ ,-]+") + r"(?![a-z])"), n, r, s)
             for n, r, s in _place_index]
_EXCL_RE = re.compile(r"(?<![a-z])(" + "|".join(re.escape(x) for x in EXCLUDE_PLACES) + r")(?![a-z])")


@functools.lru_cache(maxsize=200000)
def place_match(text):
    """Region place named in the text -> (region, subregion, matched name) or None.
    With places from several regions ("Bali, Cameroon"), the region with most
    matches wins, then the one with the longest matched name."""
    t = fold(text)
    if not t:
        return None
    hits = []
    for rx, n, region, sub in _PLACE_RE:
        m = rx.search(t)
        if m:
            hits.append((region, sub, n, m.start()))
    if not hits:
        return None
    per_region = collections.Counter(h[0] for h in hits)
    hits.sort(key=lambda h: (-per_region[h[0]], -len(h[2]), h[3]))
    region = hits[0][0]
    # the most specific place of that region = the longest name; subregion from it,
    # but avoid the generic "Africa (unspecified)" when a country is named
    best = [h for h in hits if h[0] == region and not h[1].endswith("(unspecified)")] or hits
    return best[0][:3]


BROAD_PLACES = {"west africa", "western africa", "central africa", "east africa", "eastern africa", "southern africa",
                "eastern and southern africa", "sahel", "northern africa and the sahel", "north america",
                "south america", "central america", "mesoamerica", "southeast asia", "south east asia", "oceania",
                "pacific", "pacific islands", "south pacific", "himalayas", "himalaya", "caribbean", "andes"}


@functools.lru_cache(maxsize=200000)
def excluded_place(text):
    """True when an out-of-scope place (Egypt, Iran, China, ...) is named before any region place."""
    t = fold(text)
    m = _EXCL_RE.search(t)
    if not m:
        return False
    first_region = min((rx.search(t).start() for rx, n, _, sub in _PLACE_RE
                        if n not in BROAD_PLACES and not sub.endswith("(unspecified)") and rx.search(t)),
                       default=None)
    return first_region is None or m.start() < first_region


# --------------------------------------------------------------------- V&A

def _txt(x):
    return (x or {}).get("text", "") if isinstance(x, dict) else (x or "")


def vam_reduce_record(r):
    def names(key):
        out = []
        for m in r.get(key) or []:
            n = _txt(m.get("name")).strip()
            if n:
                out.append([n, _txt(m.get("association"))])
        return out
    return {
        "id": r.get("systemNumber", ""),
        "type": r.get("objectType") or "",
        "title": next((t.get("title", "") for t in r.get("titles") or [] if t.get("title")), "")
                 or r.get("_primaryTitle") or "",
        "styles": [[s.get("text", ""), s.get("id", "")] for s in r.get("styles") or [] if s.get("text")],
        "places": [[_txt(p.get("place")), _txt(p.get("association"))] for p in r.get("placesOfOrigin") or []
                   if _txt(p.get("place"))],
        "dates": [[_txt(d.get("date")), (d.get("date") or {}).get("earliest"), (d.get("date") or {}).get("latest")]
                  for d in (r.get("productionDates") or [])[:1]],
        "persons": names("artistMakerPerson"),
        "orgs": names("artistMakerOrganisations"),
        "peoples": names("artistMakerPeople"),
        "cats": [c.get("text", "") for c in r.get("categories") or [] if c.get("text")],
        "coll": _txt(r.get("collectionCode")),
        "mats": r.get("materialsAndTechniques") or "; ".join(
            _txt(x) for x in (r.get("materials") or []) + (r.get("techniques") or [])),
        "production": (r.get("production") or "")[:300],
        "brief": (r.get("briefDescription") or "")[:300],
    }


def vam_reduce(d):
    return {"info": {k: d.get("info", {}).get(k) for k in ("record_count", "pages", "page")},
            "records": [vam_reduce_record(r) for r in d.get("records") or []]}


def vam_count(params, cache_dir):
    url = VAM_API + "?" + urllib.parse.urlencode(dict(params, page_size=1))
    d = cached_json(url, os.path.join(cache_dir, "count_" + slug(urllib.parse.urlencode(params)) + ".json.gz"),
                    reduce=lambda d: {"info": d.get("info", {}), "records": []})
    return (d or {}).get("info", {}).get("record_count", 0)


def vam_pages(params, cache_dir, label):
    page = 1
    while True:
        p = dict(params, page_size=VAM_PAGE, page=page, data_profile="full")
        url = VAM_API + "?" + urllib.parse.urlencode(p)
        d = cached_json(url, os.path.join(cache_dir, slug(label), f"p{page:03d}.json.gz"), reduce=vam_reduce,
                        ok=lambda d: bool(d["records"]) or (d["info"].get("record_count") or 0) < page * VAM_PAGE)
        if not d or not d.get("records"):
            return
        yield from d["records"]
        info = d.get("info", {})
        if page >= (info.get("pages") or 0) or page * VAM_PAGE >= VAM_MAX:
            return
        page += 1


UNDATED_SKIPPED = collections.Counter()


def vam_sweep(params, cache_dir, label):
    """All records for params; queries over the cap are split by year range, which
    drops records without a parsed production date (counted in UNDATED_SKIPPED)."""
    total = vam_count(params, cache_dir)
    if total <= VAM_MAX:
        yield from vam_pages(params, cache_dir, label)
        return
    dated = vam_count(dict(params, year_made_from=-10000, year_made_to=3000), cache_dir)
    UNDATED_SKIPPED[label] = total - dated
    yield from vam_split(params, cache_dir, label)


def vam_split(params, cache_dir, label, lo=-10000, hi=3000):
    """Yield records for params, splitting the year range until each part can be read.

    The year filter matches every record whose date range *overlaps* the window,
    so many records spanning e.g. 1800-1900 fall in every narrow window and
    bisection alone cannot get under the cap. A window of up to twice the cap is
    therefore read twice, ordered by date ascending and descending."""
    p = dict(params, year_made_from=lo, year_made_to=hi)
    n = vam_count(p, cache_dir)
    if n == 0:
        return
    tag = f"{label}_{lo}_{hi}".replace("-", "m")
    if n <= VAM_MAX:
        yield from vam_pages(p, cache_dir, tag)
        return
    if n <= 2 * VAM_MAX or hi - lo < 2:
        if n > 2 * VAM_MAX:
            print(f"  V&A {label} {lo}-{hi}: {n} records, only {2 * VAM_MAX} reachable", file=sys.stderr)
        for order in ("asc", "desc"):
            yield from vam_pages(dict(p, order_by="date", order_sort=order), cache_dir, f"{tag}_{order}")
        return
    if lo < 0 < hi:
        mid = 0
    elif lo < 1000 < hi:
        mid = 1000
    elif lo < 1600 < hi:
        mid = 1600
    else:
        mid = (lo + hi) // 2
    yield from vam_split(params, cache_dir, label, lo, mid)
    yield from vam_split(params, cache_dir, label, mid + 1, hi)


VAM_SA_SECTION = "THES48598"   # South & South East Asia Collection
VAM_PLACE_SWEEPS = {
    "south_southeast_asia": ["India", "Pakistan", "Bangladesh", "Sri Lanka", "Ceylon", "Nepal", "Bhutan", "Tibet",
                             "Burma", "Myanmar", "Thailand", "Siam", "Cambodia", "Laos", "Vietnam", "Indonesia",
                             "Java", "Bali", "Sumatra", "Malaysia", "Philippines"],
    "africa": ["Africa", "West Africa", "Nigeria", "Benin", "Ghana", "Ivory Coast", "Mali", "Sierra Leone",
               "Cameroon", "Congo", "Zaire", "Angola", "Gabon", "Ethiopia", "Sudan", "Kenya", "Tanzania",
               "Zanzibar", "Uganda", "South Africa", "Zimbabwe", "Madagascar", "Mozambique", "Zambia",
               "Senegal", "Liberia", "Guinea", "Somalia", "Malawi", "Botswana", "Namibia", "Lesotho"],
    "americas_oceania": ["Canada", "Alaska", "Arctic", "North America", "Mexico", "Guatemala", "Peru", "Bolivia",
                         "Ecuador", "Colombia", "Costa Rica", "Panama", "Brazil", "Guyana", "Suriname", "Chile",
                         "Argentina", "Venezuela", "New Zealand", "Australia", "Papua New Guinea", "New Guinea",
                         "Fiji", "Samoa", "Tonga", "Hawaii", "Tahiti", "Solomon Islands", "Vanuatu",
                         "New Caledonia", "Marquesas", "Easter Island", "Cook Islands", "Polynesia",
                         "Melanesia", "Micronesia", "Pacific Islands", "Torres Strait", "Sepik"],
}
# collectionCode values: photography, theatre, Young V&A, the library, and the East Asian and
# Middle East sections (owned by the East Asia and Islamic-world jobs)
SKIP_VAM_COLLECTIONS = {"PH", "PHO", "T&P", "YVA", "MOC", "NAL", "EAS", "MES"}
# Prints, Drawings & Paintings: from a place sweep, kept only with a recorded school/culture
# label (Company, Kalighat, ...); otherwise mostly British artists' views of the region
VAM_LABEL_ONLY_COLLECTIONS = {"PDP"}
COMMERCIAL_ROLES = re.compile(r"(?i)manufactur|publish|retail|printer|designer|distribut|factory")


def harvest_vam(regions):
    recs = {}
    for region in regions:
        cache = os.path.join(RAW, REGION_DIR[region], "vam")
        n0 = len(recs)
        if region == "south_southeast_asia":
            for r in vam_sweep({"id_collection": VAM_SA_SECTION}, cache, "section_THES48598"):
                recs.setdefault(r["id"], (r, "section", region))
            print(f"  V&A South & SE Asia Collection: {len(recs) - n0} records", file=sys.stderr)
        for place in VAM_PLACE_SWEEPS[region]:
            n1 = len(recs)
            for r in vam_sweep({"q_place_name": place}, cache, "place_" + slug(place)):
                recs.setdefault(r["id"], (r, "place:" + place, region))
            print(f"  V&A place {place}: {len(recs) - n1} new records", file=sys.stderr)
    return list(recs.values())


# --------------------------------------------------------------- Cleveland

CMA_DEPTS = {
    "south_southeast_asia": ["Indian and Southeast Asian Art"],
    "africa": ["African Art"],
    "americas_oceania": ["Art of the Americas", "Oceania"],
}
CMA_FILTERED_DEPTS = ["Textiles"]   # kept only when the culture string falls in a region


def cma_reduce(d):
    keep = CMA_FIELDS.split(",")
    return {"info": {"total": d.get("info", {}).get("total", 0)},
            "data": [{k: r.get(k) for k in keep} for r in d.get("data") or []]}


def cma_department(dept, cache_dir):
    skip, limit = 0, 100
    while True:
        url = CMA_API + "?" + urllib.parse.urlencode(
            {"department": dept, "skip": skip, "limit": limit, "fields": CMA_FIELDS}, safe=",")
        d = cached_json(url, os.path.join(cache_dir, f"{slug(dept)}_{skip:05d}.json.gz"), reduce=cma_reduce,
                        ok=lambda d: bool(d["data"]) and d["info"]["total"] > 0)
        if not d or not d.get("data"):
            return
        yield from d["data"]
        skip += limit
        if skip >= d["info"].get("total", 0):
            return


def harvest_cma(regions):
    out = []
    for region in regions:
        cache = os.path.join(RAW, REGION_DIR[region], "cma")
        for dept in CMA_DEPTS[region]:
            n = 0
            for r in cma_department(dept, cache):
                out.append((r, "dept:" + dept, region))
                n += 1
            print(f"  CMA {dept}: {n} objects", file=sys.stderr)
    # Textiles: shared cache (one copy), region decided later from the culture string
    cache = os.path.join(RAW, "south_asia", "cma")
    for dept in CMA_FILTERED_DEPTS:
        n = 0
        for r in cma_department(dept, cache):
            out.append((r, "dept:" + dept, None))
            n += 1
        print(f"  CMA {dept}: {n} objects (filtered by culture)", file=sys.stderr)
    return out


# --------------------------------------------------------------------- AIC

AIC_SKIP_DEPTS = {"Photography and Media", "Ryerson and Burnham Libraries Special Collections", "AIC Archives"}
AIC_KEYS = ["id", "title", "artist_display", "artist_title", "artist_id", "place_of_origin", "style_title",
            "style_titles", "date_display", "date_start", "date_end", "classification_title",
            "artwork_type_title", "medium_display", "department_title", "term_titles", "is_public_domain"]


def harvest_aic():
    """Candidate AIC records (filtered for region later). Reads the dump on disk."""
    files = glob.glob(os.path.join(AIC_DIR, "*.json"))
    out = []
    for fn in files:
        try:
            with open(fn, encoding="utf-8") as f:
                d = json.load(f)
        except (OSError, ValueError):
            continue
        if d.get("department_title") in AIC_SKIP_DEPTS:
            continue
        out.append(({k: d.get(k) for k in AIC_KEYS}, "dump", None))
    print(f"  AIC dump: {len(files)} files, {len(out)} candidates", file=sys.stderr)
    return out


# ------------------------------------------------------------------ Rijksmuseum

RIJKS_QUERIES = [
    # South / Southeast Asia
    "Majapahit", "Boeddha", "Buddha", "Shiva", "Siva", "Vishnu", "Wisnu", "Ganesha", "Ganesa", "Hindoe",
    "Bodhisattva", "Durga", "Parvati", "kris", "wayang", "batik", "Bali", "Lombok", "Ceylon", "Sri Lanka",
    "Kandy", "Siam", "Cambodja", "Birma", "Coromandel", "Bengalen", "Golconda", "Mughal", "Mogol", "India",
    "Indonesia", "Sumatra", "Borobudur", "Prambanan",
    # Africa
    "Benin", "Yoruba", "Ashanti", "Goudkust", "Congo", "Kongo", "Afrikaans masker", "Elmina",
    # Americas / Oceania
    "Inca", "Inka", "Azteken", "Maya", "Peru", "Papoea", "Nieuw-Guinea", "Asmat", "Maori", "Hawaii", "Tahiti",
    "Suriname inheems", "Arowakken", "Karaiben",
]


def rijks_reduce(d):
    try:
        return _rijks_reduce(d)
    except (AttributeError, TypeError, KeyError, IndexError) as e:
        NET["rijks_unparsed"] += 1
        return {"id": d.get("id", "") if isinstance(d, dict) else "", "unparsed": str(e)[:100]}


def _rijks_reduce(d):
    def notation(x):
        if isinstance(x, str):
            return x
        if not isinstance(x, dict):
            return ""
        nots = x.get("notation") or []
        if isinstance(nots, (str, dict)):
            nots = [nots]
        for n in nots:
            if isinstance(n, dict) and n.get("@language") == "en":
                return n.get("@value", "")
        for n in nots:
            if isinstance(n, dict):
                return n.get("@value", "")
            if isinstance(n, str):
                return n
        for i in x.get("identified_by") or []:
            if isinstance(i, dict) and i.get("type") == "Name" and i.get("content"):
                return i["content"]
        return x.get("_label", "")

    def lin(objs, lang="300388277"):
        out = []
        for o in objs or []:
            if not isinstance(o, dict):
                continue
            langs = [l.get("id", "") if isinstance(l, dict) else str(l) for l in o.get("language") or []]
            if not langs or any(lang in l for l in langs):
                out.append(o.get("content", ""))
        return out
    prod = d.get("produced_by") or {}
    parts = prod.get("part") or [prod]
    makers, places, techs = [], [], []
    for p in parts:
        for a in p.get("carried_out_by") or []:
            makers.append(notation(a))
        for pl in p.get("took_place_at") or []:
            places.append(notation(pl))
        for t in p.get("technique") or []:
            techs.append(notation(t))
        for txt in lin(p.get("referred_to_by")):
            makers.append("~" + txt)
    ts = prod.get("timespan") or {}
    names = [i.get("content", "") for i in d.get("identified_by") or [] if i.get("type") == "Name"]
    objno = next((i.get("content", "") for i in d.get("identified_by") or []
                  if i.get("type") == "Identifier"), "")
    types = [notation(c) for c in d.get("classified_as") or [] if isinstance(c, dict)]
    mats = [notation(m) for m in d.get("made_of") or []]
    texts = lin(d.get("referred_to_by"))
    return {"id": d.get("id", ""), "objno": objno, "names": names[:3], "types": types, "makers": makers,
            "places": places, "techs": techs, "mats": mats,
            "begin": ts.get("begin_of_the_begin"), "end": ts.get("end_of_the_end"),
            "date_text": next((x.get("content", "") for x in (ts.get("identified_by") or [])), ""),
            "texts": [t[:200] for t in texts[:4]]}


def harvest_rijks(max_objects):
    cache = os.path.join(RAW, "south_asia", "rijks")  # one shared cache for the three regions
    per_query = collections.OrderedDict()
    for q in RIJKS_QUERIES:
        per_query[q] = []
        url = RIJKS_SEARCH + "?" + urllib.parse.urlencode({"description": q})
        page = 0
        while url and page < 20:
            d = cached_json(url, os.path.join(cache, "search", f"{slug(q)}_{page:02d}.json.gz"),
                            reduce=lambda d: {"items": [i["id"] for i in d.get("orderedItems") or []],
                                              "next": (d.get("next") or {}).get("id"),
                                              "total": (d.get("partOf") or {}).get("totalItems")},
                            accept="application/ld+json")
            if not d:
                break
            per_query[q].extend(d["items"])
            url = d.get("next")
            page += 1
    ids = {}   # round-robin over the queries, so the cap does not starve the later regions
    for k in range(max((len(v) for v in per_query.values()), default=0)):
        for q, lst in per_query.items():
            if k < len(lst):
                ids.setdefault(lst[k], q)
    print(f"  Rijks: {len(ids)} ids from {len(RIJKS_QUERIES)} keyword searches", file=sys.stderr)
    out = []
    for n, (oid, q) in enumerate(ids.items()):
        if n >= max_objects:
            print(f"  Rijks: capped at {max_objects} objects", file=sys.stderr)
            break
        rec = cached_json(oid, os.path.join(cache, "objects", slug(oid.rsplit("/", 1)[-1]) + ".json.gz"),
                          reduce=rijks_reduce, accept="application/ld+json")
        if rec:
            out.append((rec, "q:" + q, None))
        if n and n % 250 == 0:
            print(f"  Rijks: {n} objects read", file=sys.stderr)
    return out


# ------------------------------------------------------------ tradition lexicons
# (pattern on folded text, canonical label). Patterns are whole-word regexes;
# order matters (specific first). "Group: School" labels give a two-level key.

def _L(pairs):
    return [(re.compile(r"(?<![a-z])(?:" + p + r")(?![a-z])"), lab) for p, lab in pairs]


SSEA_CULTURES = _L([
    # Pahari painting (Punjab Hills)
    (r"kangra", "Pahari: Kangra"), (r"guler", "Pahari: Guler"), (r"basohli|basholi", "Pahari: Basohli"),
    (r"chamba", "Pahari: Chamba"), (r"mandi", "Pahari: Mandi"), (r"kulu|kullu", "Pahari: Kulu"),
    (r"nurpur", "Pahari: Nurpur"), (r"bilaspur|kahlur", "Pahari: Bilaspur"), (r"jasrota", "Pahari: Jasrota"),
    (r"mankot", "Pahari: Mankot"), (r"bahu", "Pahari: Bahu"), (r"jammu", "Pahari: Jammu"),
    (r"(tehri )?garhwal", "Pahari: Garhwal"), (r"sirmur", "Pahari: Sirmur"), (r"arki", "Pahari: Arki"),
    (r"pahari|punjab hills|hill (states|kingdoms)", "Pahari"),
    # Rajput painting (Rajasthan, Central India)
    (r"mewar|udaipur", "Rajput: Mewar"), (r"nathdwara", "Rajput: Nathdwara"), (r"deogarh|devgarh", "Rajput: Deogarh"),
    (r"bundi", "Rajput: Bundi"), (r"kota|kotah", "Rajput: Kota"), (r"kishangarh", "Rajput: Kishangarh"),
    (r"bikaner", "Rajput: Bikaner"), (r"jodhpur|marwar", "Rajput: Marwar (Jodhpur)"),
    (r"jaipur|amber (palace|fort|state)|amer", "Rajput: Jaipur (Amber)"), (r"alwar", "Rajput: Alwar"), (r"ajmer", "Rajput: Ajmer"),
    (r"sawar", "Rajput: Sawar"), (r"uniara", "Rajput: Uniara"), (r"raghogarh", "Rajput: Raghogarh"),
    (r"sirohi", "Rajput: Sirohi"), (r"karauli", "Rajput: Karauli"), (r"isarda", "Rajput: Isarda"),
    (r"datia|orchha|bundelkhand", "Rajput: Bundelkhand"), (r"malwa", "Rajput: Malwa"),
    (r"narsinghgarh|sitamau|ratlam|sailana", "Rajput: Malwa"),
    (r"rajput|rajasthani", "Rajput"),
    # Deccani
    (r"bijapur", "Deccani: Bijapur"), (r"golconda|golkonda", "Deccani: Golconda"),
    (r"ahmadnagar|ahmednagar", "Deccani: Ahmadnagar"), (r"hyderabad", "Deccani: Hyderabad"),
    (r"bidar|bidri", "Deccani: Bidar"), (r"aurangabad", "Deccani: Aurangabad"), (r"kurnool", "Deccani: Kurnool"),
    (r"deccani|deccan", "Deccani"),
    # Company painting and other colonial-era schools
    (r"kalighat", "Kalighat painting"),
    (r"company", "Company school"),
    (r"bengal school", "Bengal School"),
    # Mughal and successor courts (Mughal is owned by the Islamic-world job)
    (r"lucknow|awadh|oudh|faizabad", "Awadh (Lucknow)"), (r"farrukhabad", "Farrukhabad"),
    (r"murshidabad", "Murshidabad"),
    (r"mughal|mogul|moghul|shah jahan|jahangir|akbar|aurangzeb", "Mughal"),
    (r"sikh|lahore", "Sikh (Punjab)"),
    (r"sultanate", "Sultanate (pre-Mughal)"),
    (r"western indian|jain|jaina", "Western Indian (Jain)"),
    (r"mysore", "Mysore"), (r"tanjore|thanjavur", "Thanjavur (Tanjore)"),
    (r"mithila|madhubani", "Mithila (Madhubani)"), (r"pattachitra|patachitra", "Odisha: Pattachitra"),
    (r"kashmir|kashmiri", "Kashmiri"),
    (r"gandhara|gandharan", "Gandhara"), (r"mathura", "Mathura"),
    (r"indus valley|harappa|harappan|mohenjo", "Indus Valley"),
    (r"amaravati|nagarjunakonda", "Amaravati"), (r"ajanta", "Ajanta"), (r"sanchi", "Sanchi"), (r"bharhut", "Bharhut"), (r"chandraketugarh", "Chandraketugarh"),
    (r"newar|newari", "Nepalese (Newar)"), (r"nepal|nepalese|nepali|kathmandu", "Nepalese (Newar)"),
    (r"sino-tibetan", "Sino-Tibetan"), (r"tibet|tibetan", "Tibetan"), (r"bhutan|bhutanese", "Bhutanese"),
    (r"himalaya|himalayan", "Himalayan"),
    (r"kandyan|kandy", "Sri Lankan: Kandyan"), (r"sri lanka|sri lankan|sinhal|singhalese|ceylon", "Sri Lankan"),
    (r"gujarat|gujarati", "Gujarat"), (r"orissa|odisha|puri", "Odisha"),
    (r"bengal|bengali|bengalen|bangladesh", "Bengal"), (r"bihar|patna", "Bihar"),
    (r"tamil nadu|south india|south indian|southern india|kerala|karnataka|andhra|madurai", "South Indian"),
    (r"pakistan|sindh|sind|peshawar|taxila", "Pakistan (Indus / NW)"),
    # Southeast Asia
    (r"khmer|angkor|angkorian|cambodia|cambodian|cambodja", "Khmer"),
    (r"champa|cham", "Cham (Champa)"),
    (r"dvaravati", "Mon-Dvaravati"), (r"pyu", "Pyu"),
    (r"lan ?na", "Thai: Lan Na"), (r"sawankhalok|si satchanalai", "Thai: Sawankhalok ware"),
    (r"thai|thailand|siam|siamese", "Thai"),
    (r"lao|laos|laotian", "Lao"),
    (r"shan", "Burmese: Shan"), (r"arakan|arakanese|mrauk", "Burmese: Arakan"),
    (r"burma|burmese|birma|myanmar", "Burmese"),
    (r"dong ?son", "Dong Son"), (r"ban chiang", "Ban Chiang"),
    (r"vietnam|vietnamese|annam|annamese|tonkin", "Vietnamese"),
    (r"bali|balinese", "Balinese"), (r"lombok|sasak", "Lombok (Sasak)"),
    (r"batak", "Sumatran: Batak"), (r"minangkabau", "Sumatran: Minangkabau"), (r"aceh|acehnese", "Sumatran: Aceh"),
    (r"lampung", "Sumatran: Lampung"), (r"nias", "Nias"), (r"sumatra|sumatran|palembang", "Sumatran"),
    (r"dayak|iban|borneo|kalimantan|sarawak", "Dayak (Borneo)"),
    (r"toraja|sulawesi|celebes|bugis", "Sulawesi"), (r"sumba|sumbanese", "Sumba"), (r"flores", "Flores"),
    (r"timor", "Timor"), (r"moluccas|maluku|tanimbar", "Moluccas"),
    (r"candi|tjandi|java|javanese|majapahit|yogyakarta|jogjakarta|surakarta|cirebon|madura", "Javanese"),
    (r"indonesia|indonesian|indonesie|dutch east indies|nederlands-indie", "Indonesian"),
    (r"malay|malaya|malaysia|malaysian|penang|malacca|melaka|brunei", "Malay"),
    (r"philippines|philippine|filipino|ifugao|luzon|mindanao|moro|t.?boli", "Philippine"),
    (r"indian|india", "Indian"),
])

SSEA_PERIODS = _L([
    (r"indus valley|harappan|mohenjo", "Indus Valley"), (r"pre-?mauryan", "Pre-Mauryan"),
    (r"maurya|mauryan", "Maurya"), (r"shunga|sunga", "Shunga"), (r"satavahana|andhra period", "Satavahana"),
    (r"ikshvaku", "Ikshvaku"), (r"kushan|kushana|kusana", "Kushan"), (r"post-?gupta", "Post-Gupta"),
    (r"gupta", "Gupta"), (r"vakataka", "Vakataka"), (r"pallava", "Pallava"),
    (r"chalukya|chalukyan", "Chalukya"), (r"rashtrakuta", "Rashtrakuta"), (r"pala-?sena|pala|sena dynasty", "Pala"),
    (r"chola", "Chola"), (r"pandya", "Pandya"), (r"hoysala", "Hoysala"), (r"kakatiya", "Kakatiya"),
    (r"vijayanagara?", "Vijayanagara"), (r"nayaka?", "Nayaka"), (r"eastern ganga|ganga (dynasty|period)", "Eastern Ganga"),
    (r"chandella|chandela", "Chandella"), (r"pratihara", "Pratihara"), (r"paramara", "Paramara"),
    (r"solanki|chaulukya|vaghela", "Solanki"), (r"kalachuri", "Kalachuri"), (r"karkota", "Karkota"),
    (r"utpala", "Utpala"), (r"licchavi", "Licchavi"), (r"thakuri", "Thakuri"), (r"malla", "Malla"),
    (r"anuradhapura", "Anuradhapura"), (r"polonnaruwa", "Polonnaruwa"), (r"kandyan|kandy", "Kandyan"),
    (r"delhi sultanate|sultanate", "Sultanate"),
    (r"mughal|mogul|shah jahan|jahangir|akbar|aurangzeb", "Mughal"),
    (r"company", "Company (British colonial)"), (r"british raj|victorian", "British Raj"),
    (r"funan|phnom da", "Funan"), (r"pre-?angkor|pre-?angkorian|sambor prei kuk|prei kmeng|kompong preah", "Pre-Angkorian"),
    (r"angkor wat", "Angkorian: Angkor Wat style"), (r"bayon", "Angkorian: Bayon style"),
    (r"baphuon", "Angkorian: Baphuon style"), (r"koh ker", "Angkorian: Koh Ker style"),
    (r"banteay srei", "Angkorian: Banteay Srei style"), (r"jayavarman", "Angkorian"),
    (r"angkor|angkorian", "Angkorian"), (r"post-?angkor", "Post-Angkorian"),
    (r"dvaravati", "Dvaravati"), (r"srivijaya", "Srivijaya"), (r"u ?thong", "U Thong"),
    (r"lopburi", "Lopburi"), (r"sukhothai", "Sukhothai"), (r"ayutthaya|ayudhya", "Ayutthaya"),
    (r"chiang saen", "Chiang Saen"), (r"lan ?na", "Lan Na"), (r"rattanakosin|bangkok period", "Rattanakosin"),
    (r"pyu", "Pyu"), (r"pagan|bagan", "Pagan"), (r"ava period|inwa", "Ava"), (r"amarapura", "Amarapura"),
    (r"konbaung", "Konbaung"), (r"mandalay", "Konbaung: Mandalay"), (r"mrauk ?u", "Mrauk U"),
    (r"central javanese|sailendra|mataram", "Central Javanese"),
    (r"east javanese|eastern javanese|kediri|singhasari|singasari", "East Javanese"), (r"majapahit", "Majapahit"),
    (r"my son|dong duong|tra kieu|thap mam", "Champa"),
    (r"ly dynasty", "Ly dynasty"), (r"tran dynasty", "Tran dynasty"), (r"le dynasty", "Le dynasty"),
    (r"nguyen", "Nguyen dynasty"), (r"dong ?son", "Dong Son"), (r"ban chiang", "Ban Chiang"),
])

AFRICA_CULTURES = _L([
    (r"igbo-?ukwu", "Igbo-Ukwu"), (r"nok", "Nok"), (r"ile-?ife|ife", "Ife"), (r"owo", "Owo"),
    (r"djenne|jenne|inland niger delta", "Inland Niger Delta (Djenne)"), (r"sao", "Sao"),
    (r"sapi(-portuguese)?|afro-portuguese", "Sapi (Afro-Portuguese)"),
    (r"edo|benin kingdom|kingdom of benin|court of benin|benin city|bini", "Edo (Benin Kingdom)"),
    (r"yoruba|ijebu|egba|oyo", "Yoruba"), (r"igbo|ibo", "Igbo"), (r"ibibio|anang|annang", "Ibibio"),
    (r"ijo|ijaw|kalabari", "Ijo"), (r"idoma", "Idoma"), (r"igala", "Igala"), (r"ejagham|ekoi", "Ejagham"),
    (r"mumuye", "Mumuye"), (r"jukun", "Jukun"), (r"chamba", "Chamba"), (r"mambila", "Mambila"),
    (r"hausa", "Hausa"), (r"nupe", "Nupe"), (r"urhobo", "Urhobo"), (r"tiv", "Tiv"), (r"montol", "Montol"),
    (r"bamum|bamoun|foumban", "Cameroon Grassfields: Bamum"), (r"bamileke", "Cameroon Grassfields: Bamileke"),
    (r"bangwa", "Cameroon Grassfields: Bangwa"), (r"kom", "Cameroon Grassfields: Kom"),
    (r"grassfields?|grasslands|babanki|bali-nyonga|oku", "Cameroon Grassfields"),
    (r"asante|ashanti", "Akan: Asante"), (r"fante|fanti", "Akan: Fante"),
    (r"ewe", "Ewe"), (r"krobo", "Krobo"), (r"fon|dahomey|abomey", "Fon (Dahomey)"),
    (r"lagoons?( peoples)?|attie|ebrie|akye", "Lagoon peoples"),
    (r"baule|baoule", "Baule"), (r"senufo|senoufo|siena", "Senufo"), (r"guro|gouro", "Guro"),
    (r"dan|yacouba", "Dan"), (r"wee|guere|wobe", "We (Guere)"), (r"kran", "Kran"), (r"grebo", "Grebo"),
    (r"bete", "Bete"), (r"mende", "Mende"), (r"temne", "Temne"), (r"sherbro|bullom", "Sherbro"),
    (r"kissi", "Kissi"), (r"toma|loma", "Toma"), (r"kpelle", "Kpelle"), (r"bassa", "Bassa"),
    (r"baga", "Baga"), (r"nalu", "Nalu"), (r"bidjogo|bijago|bissagos", "Bidjogo"), (r"landuma", "Landuma"),
    (r"bamana|bambara", "Bamana"), (r"dogon", "Dogon"), (r"tellem", "Tellem"), (r"malinke|maninka", "Malinke"),
    (r"mande", "Mande"), (r"marka", "Marka"), (r"bozo", "Bozo"), (r"minianka", "Minianka"),
    (r"bwa|bobo-?ule", "Bwa"), (r"bobo", "Bobo"), (r"mossi", "Mossi"), (r"nuna", "Nuna"), (r"winiama", "Winiama"),
    (r"kurumba", "Kurumba"), (r"lobi", "Lobi"), (r"gurunsi|kassena|nankani", "Gurunsi"), (r"tusyan", "Tusyan"),
    (r"fulani|fulbe|peul", "Fulani"), (r"tuareg|tuaregs", "Tuareg"), (r"wolof", "Wolof"),
    (r"fang", "Fang"), (r"kota|bakota|mahongwe", "Kota"), (r"punu|lumbo", "Punu"), (r"tsogo", "Tsogo"),
    (r"vuvi", "Vuvi"), (r"kwele|bakwele", "Kwele"), (r"teke|bateke", "Teke"),
    (r"kongo|bakongo|yombe|vili|woyo|bwende|solongo", "Kongo"), (r"bembe|babembe", "Bembe"),
    (r"kuba|bakuba|bushoong|ngeende|bushong", "Kuba"), (r"luba|baluba", "Luba"), (r"songye|songe|basonge", "Songye"),
    (r"hemba", "Hemba"), (r"tabwa", "Tabwa"), (r"lega|rega|balega", "Lega"),
    (r"chokwe|tshokwe|cokwe", "Chokwe"), (r"lunda", "Lunda"), (r"pende|bapende", "Pende"), (r"yaka|bayaka", "Yaka"),
    (r"suku", "Suku"), (r"mbunda", "Mbunda"), (r"lulua|luluwa|bena lulua", "Lulua"), (r"salampasu", "Salampasu"),
    (r"lwalwa", "Lwalwa"), (r"mangbetu", "Mangbetu"), (r"zande|azande", "Zande"), (r"ngbaka", "Ngbaka"),
    (r"ngbandi", "Ngbandi"), (r"mbole", "Mbole"), (r"boa", "Boa"), (r"kusu", "Kusu"), (r"holo", "Holo"),
    (r"ovimbundu", "Ovimbundu"), (r"lozi|barotse", "Lozi"),
    (r"zulu", "Zulu"), (r"xhosa", "Xhosa"), (r"ndebele", "Ndebele"), (r"sotho|basotho", "Sotho"),
    (r"tsonga|shangaan", "Tsonga"), (r"venda", "Venda"), (r"swazi", "Swazi"), (r"nguni", "Nguni"),
    (r"shona", "Shona"), (r"makonde", "Makonde"), (r"makua", "Makua"), (r"yao", "Yao"), (r"chewa", "Chewa"),
    (r"nyamwezi", "Nyamwezi"), (r"sukuma", "Sukuma"), (r"zaramo|zalamo", "Zaramo"), (r"swahili", "Swahili"),
    (r"maasai|masai", "Maasai"), (r"samburu", "Samburu"), (r"turkana", "Turkana"), (r"pokot", "Pokot"),
    (r"kamba", "Kamba"), (r"kikuyu", "Kikuyu"), (r"giryama|mijikenda", "Mijikenda"),
    (r"ganda|baganda", "Ganda"), (r"tutsi|rwandan", "Rwanda"),
    (r"amhara|gondar|gondarine|tigray|tigrinya|ethiopian|ethiopia|abyssinian|abyssinia|maqdala|magdala",
     "Ethiopian"), (r"oromo|galla", "Oromo"), (r"somali", "Somali"),
    (r"dinka", "Dinka"), (r"nuer", "Nuer"), (r"shilluk", "Shilluk"), (r"nuba", "Nuba"),
    (r"meroitic|meroe|napatan|kerma|kushite|nubian|nubia", "Nubian (Kush)"),
    (r"malagasy|sakalava|mahafaly|merina|antanosy|madagascar", "Malagasy"),
    (r"berber|amazigh|kabyle", "Amazigh (Berber)"),
    # broad language/culture groups last, so the specific people wins ("Baule; ... akan")
    (r"akan", "Akan"),
])

AFRICA_PERIODS = _L([
    (r"nok", "Nok"), (r"igbo-?ukwu", "Igbo-Ukwu"), (r"ife classical|classical ife|pavement era", "Ife classical"),
    (r"early period", "Early period"), (r"middle period", "Middle period"), (r"late period", "Late period"),
    (r"gondarine|gondar", "Gondarine"), (r"aksumite|axumite", "Aksumite"), (r"solomonic", "Solomonic"),
    (r"meroitic", "Meroitic"), (r"napatan", "Napatan"), (r"kerma", "Kerma"),
    (r"djenne|inland niger delta", "Inland Niger Delta"), (r"sao", "Sao"), (r"neolithic", "Neolithic"),
    (r"iron age", "Iron Age"), (r"colonial", "Colonial"),
])

AMERICAS_CULTURES = _L([
    # Mesoamerica
    (r"olmec|olmeca", "Olmec"), (r"tlatilco", "Tlatilco"), (r"xochipala", "Xochipala"), (r"mezcala", "Mezcala"),
    (r"chupicuaro", "Chupicuaro"), (r"colima", "West Mexico: Colima"), (r"jalisco", "West Mexico: Jalisco"),
    (r"nayarit", "West Mexico: Nayarit"), (r"west(ern)? mexic(o|an)|shaft tomb", "West Mexico"),
    (r"teotihuacan", "Teotihuacan"), (r"zapotec", "Zapotec"), (r"mixtec|mixteca", "Mixtec"),
    (r"remojadas", "Classic Veracruz: Remojadas"), (r"veracruz|totonac|el tajin", "Classic Veracruz"),
    (r"huastec|huasteca", "Huastec"), (r"toltec", "Toltec"), (r"aztec|mexica", "Aztec (Mexica)"),
    (r"tarascan|purepecha", "Tarascan"), (r"maya|mayan|jaina", "Maya"), (r"guerrero", "Guerrero"),
    (r"huichol|wixarika", "Huichol"),
    # Central America and Caribbean
    (r"cocle|conte", "Panama: Cocle"), (r"veraguas", "Panama: Veraguas"), (r"chiriqui", "Gran Chiriqui"),
    (r"diquis", "Costa Rica: Diquis"), (r"nicoya", "Greater Nicoya"), (r"atlantic watershed|linea vieja", "Costa Rica: Atlantic Watershed"),
    (r"ulua", "Ulua"), (r"lenca", "Lenca"), (r"taino", "Taino"), (r"guna|kuna|cuna", "Guna"), (r"embera", "Embera"),
    # Andes and South America
    (r"cupisnique", "Cupisnique"), (r"chavin", "Chavin"), (r"paracas", "Paracas"), (r"nasca|nazca", "Nasca"),
    (r"vicus", "Vicus"), (r"moche|mochica", "Moche"), (r"recuay", "Recuay"), (r"lima culture|lima style", "Lima"),
    (r"tiwanaku-?wari|wari|huari", "Wari"), (r"tiwanaku|tiahuanaco", "Tiwanaku"),
    (r"lambayeque|sican", "Lambayeque (Sican)"), (r"chimu", "Chimu"), (r"chancay", "Chancay"),
    (r"chuquibamba", "Chuquibamba"), (r"ica|chincha|ica-chincha", "Ica-Chincha"), (r"inca|inka", "Inca"),
    (r"aymara", "Aymara"), (r"quechua", "Quechua"), (r"valdivia", "Valdivia"), (r"chorrera", "Chorrera"),
    (r"jama-?coaque", "Jama-Coaque"), (r"bahia", "Bahia"), (r"tolita|tumaco", "La Tolita-Tumaco"),
    (r"mantena|manteno", "Manteno"), (r"carchi|narino|capuli|piartal|tuza", "Carchi-Narino"),
    (r"quimbaya", "Quimbaya"), (r"calima", "Calima"), (r"tairona", "Tairona"), (r"muisca", "Muisca"),
    (r"zenu|sinu", "Zenu"), (r"tolima", "Tolima"), (r"san agustin", "San Agustin"),
    (r"marajoara|marajo", "Marajoara"), (r"santarem|tapajos", "Santarem (Tapajos)"),
    (r"shipibo|conibo", "Shipibo-Conibo"), (r"canelos quichua|canelos", "Canelos Quichua"),
    (r"shuar|jivaro|achuar", "Shuar"), (r"kayapo", "Kayapo"), (r"karaja", "Karaja"), (r"wayana", "Wayana"),
    (r"bororo", "Bororo"), (r"mapuche|araucanian", "Mapuche"), (r"yanomami", "Yanomami"), (r"tukano", "Tukano"),
    (r"wauja|waura", "Wauja"), (r"tikuna|ticuna", "Tikuna"), (r"munduruku", "Munduruku"),
    (r"arawak|arowak|lokono|carib|kalina|kari.?na", "Arawak / Carib (Guianas)"),
    # North America
    (r"haida", "Haida"), (r"tlingit", "Tlingit"), (r"tsimshian", "Tsimshian"),
    (r"kwakwaka.?wakw|kwakiutl", "Kwakwaka'wakw"), (r"nuu-?chah-?nulth|nootka", "Nuu-chah-nulth"),
    (r"heiltsuk|bella bella", "Heiltsuk"), (r"nuxalk|bella coola", "Nuxalk"), (r"makah", "Makah"),
    (r"coast salish|salish", "Coast Salish"), (r"northwest coast", "Northwest Coast"),
    (r"yup.?ik|yupik", "Yup'ik"), (r"inupiat|inupiaq", "Inupiat"), (r"inuit|eskimo", "Inuit"),
    (r"aleut|unangan", "Aleut (Unangan)"), (r"athabaskan|athapaskan|gwich.?in|dene", "Athabaskan"),
    (r"cree", "Cree"), (r"ojibwe?|ojibwa|chippewa|anishinaabe", "Ojibwe"), (r"odawa", "Odawa"),
    (r"potawatomi", "Potawatomi"), (r"menominee", "Menominee"), (r"ho-?chunk|winnebago", "Ho-Chunk"),
    (r"meskwaki|sauk", "Meskwaki / Sauk"), (r"huron|wendat", "Huron-Wendat"),
    (r"iroquois|haudenosaunee|mohawk|seneca|onondaga|oneida|cayuga|tuscarora", "Haudenosaunee (Iroquois)"),
    (r"mi.?kmaq|micmac", "Mi'kmaq"), (r"lenape|delaware", "Lenape (Delaware)"), (r"shawnee", "Shawnee"),
    (r"cherokee", "Cherokee"), (r"muscogee|creek (indian|nation|people)", "Muscogee (Creek)"), (r"seminole", "Seminole"),
    (r"choctaw", "Choctaw"), (r"chickasaw", "Chickasaw"), (r"caddo", "Caddo"),
    (r"lakota|sioux|dakota|nakota|yanktonai|yankton|hunkpapa|oglala|brule", "Lakota / Dakota (Sioux)"),
    (r"cheyenne", "Cheyenne"), (r"arapaho", "Arapaho"), (r"crow|apsaalooke", "Crow"),
    (r"blackfeet|blackfoot|siksika|kainai|piegan|piikani", "Blackfoot"), (r"assiniboine|nakoda", "Assiniboine"),
    (r"gros ventre|aaniiih", "Gros Ventre"), (r"mandan", "Mandan"), (r"hidatsa", "Hidatsa"),
    (r"arikara", "Arikara"), (r"pawnee", "Pawnee"), (r"osage", "Osage"), (r"omaha", "Omaha"), (r"ponca", "Ponca"),
    (r"kiowa", "Kiowa"), (r"comanche", "Comanche"), (r"nez perce", "Nez Perce"), (r"shoshone", "Shoshone"),
    (r"ute", "Ute"), (r"paiute", "Paiute"), (r"washoe", "Washoe"), (r"pomo", "Pomo"), (r"chumash", "Chumash"),
    (r"yurok|karuk|hupa", "Yurok / Karuk / Hupa"), (r"yokuts", "Yokuts"), (r"panamint", "Panamint"),
    (r"apache", "Apache"), (r"navajo|dine", "Navajo (Dine)"), (r"hopi", "Hopi"), (r"zuni", "Zuni"),
    (r"acoma", "Pueblo: Acoma"), (r"laguna", "Pueblo: Laguna"), (r"san ildefonso", "Pueblo: San Ildefonso"),
    (r"santa clara", "Pueblo: Santa Clara"), (r"cochiti", "Pueblo: Cochiti"), (r"santo domingo|kewa", "Pueblo: Santo Domingo"),
    (r"zia", "Pueblo: Zia"), (r"jemez", "Pueblo: Jemez"), (r"isleta", "Pueblo: Isleta"), (r"tesuque", "Pueblo: Tesuque"),
    (r"taos", "Pueblo: Taos"), (r"ancestral pueblo(an)?|anasazi|basketmaker", "Ancestral Pueblo"),
    (r"mimbres|mogollon", "Mimbres (Mogollon)"), (r"hohokam", "Hohokam"), (r"casas grandes|paquime", "Casas Grandes"),
    (r"pueblo", "Pueblo"), (r"tohono o.?odham|papago", "Tohono O'odham"), (r"pima|akimel", "Akimel O'odham"),
    (r"mississippian", "Mississippian"), (r"hopewell", "Hopewell"), (r"adena", "Adena"),
    (r"plains", "Plains"), (r"great lakes|woodlands", "Great Lakes / Woodlands"),
    (r"native american|american indian|first nations|indigenous", "Native North American"),
    # Oceania
    (r"maori|aotearoa", "Maori"), (r"hawaiian|hawaii", "Hawaiian"), (r"marquesan|marquesas", "Marquesan"),
    (r"rapa nui|easter island", "Rapa Nui"), (r"tahitian|tahiti|society islands", "Society Islands (Tahiti)"),
    (r"austral islands|raivavae|rurutu|tubuai", "Austral Islands"), (r"mangareva|gambier", "Mangareva"),
    (r"cook islands|rarotonga|mangaia|aitutaki", "Cook Islands"), (r"samoan|samoa", "Samoan"),
    (r"tongan|tonga", "Tongan"), (r"fijian|fiji", "Fijian"), (r"tuvalu|ellice", "Tuvalu"),
    (r"niue", "Niue"), (r"tokelau", "Tokelau"),
    (r"kiribati|gilbert islands|i-kiribati", "Kiribati"), (r"marshall islands", "Marshall Islands"),
    (r"chuuk|truk|mortlock", "Chuuk"), (r"yap|yapese", "Yap"), (r"palau|belau", "Palau"),
    (r"pohnpei|ponape|kosrae", "Pohnpei / Kosrae"), (r"caroline islands|carolinian", "Caroline Islands"),
    (r"nauru", "Nauru"), (r"micronesia|micronesian", "Micronesian"),
    (r"asmat", "Asmat"), (r"iatmul", "Sepik: Iatmul"), (r"abelam", "Sepik: Abelam"), (r"kwoma", "Sepik: Kwoma"),
    (r"sawos", "Sepik: Sawos"), (r"boiken", "Sepik: Boiken"), (r"chambri", "Sepik: Chambri"),
    (r"biwat|mundugumor|yuat", "Yuat River"), (r"ramu", "Lower Ramu"), (r"sepik", "Sepik"),
    (r"lake sentani|sentani", "Lake Sentani"), (r"geelvink|cenderawasih|biak", "Cenderawasih Bay"),
    (r"elema|kerewa|gope|papuan gulf|gulf province", "Papuan Gulf"), (r"marind", "Marind-anim"),
    (r"torres strait", "Torres Strait"), (r"massim|trobriand|kiriwina|woodlark", "Massim"),
    (r"new ireland|malagan|malanggan", "New Ireland"), (r"tolai|baining|sulka|new britain", "New Britain"),
    (r"admiralty islands|manus", "Admiralty Islands"), (r"bougainville|buka", "Bougainville"),
    (r"solomon islands|solomons|santa cruz", "Solomon Islands"),
    (r"vanuatu|new hebrides|malakula|malekula|ambrym|ni-vanuatu", "Vanuatu"),
    (r"new caledonia|kanak", "New Caledonia (Kanak)"), (r"huon gulf|tami|siassi", "Huon Gulf"),
    (r"highlands|mendi|enga|huli|wahgi", "New Guinea Highlands"),
    (r"aboriginal|aborigine|arnhem land|yolngu|tiwi|warlpiri|pitjantjatjara", "Aboriginal Australian"),
    (r"lapita", "Lapita"), (r"polynesia|polynesian", "Polynesian"), (r"melanesia|melanesian", "Melanesian"),
    (r"new guinea|papua|papuan", "New Guinea"),
    (r"pre-?columbian|precolumbian|prehispanic|pre-?hispanic", "Pre-Columbian (unspecified)"),
])

AMERICAS_PERIODS = _L([
    (r"early formative|early preclassic", "Early Formative"), (r"middle formative|middle preclassic", "Middle Formative"),
    (r"late formative|late preclassic|terminal preclassic|protoclassic", "Late Formative"),
    (r"formative|preclassic|pre-classic", "Formative"), (r"early classic", "Early Classic"),
    (r"late classic|terminal classic", "Late Classic"), (r"epiclassic", "Epiclassic"),
    (r"early postclassic", "Early Postclassic"), (r"late postclassic", "Late Postclassic"),
    (r"postclassic|post-classic", "Postclassic"), (r"classic period|classic", "Classic"),
    (r"initial period", "Initial Period"), (r"early horizon", "Early Horizon"),
    (r"early intermediate", "Early Intermediate Period"), (r"middle horizon", "Middle Horizon"),
    (r"late intermediate", "Late Intermediate Period"), (r"late horizon", "Late Horizon"),
    (r"archaic", "Archaic"), (r"early woodland", "Early Woodland"), (r"middle woodland", "Middle Woodland"),
    (r"late woodland", "Late Woodland"), (r"woodland period", "Woodland"),
    (r"mississippian period", "Mississippian"), (r"pueblo (i|ii|iii|iv|v)", "Pueblo period"),
    (r"basketmaker", "Basketmaker"), (r"reservation period|reservation era", "Reservation period"),
    (r"colonial", "Colonial"), (r"lapita", "Lapita"),
])

REGION_LEX = {
    "south_southeast_asia": (SSEA_CULTURES, SSEA_PERIODS),
    "africa": (AFRICA_CULTURES, AFRICA_PERIODS),
    "americas_oceania": (AMERICAS_CULTURES, AMERICAS_PERIODS),
}
OVERLAP = {"Mughal": "islamic_world", "Awadh (Lucknow)": "islamic_world", "Farrukhabad": "islamic_world",
           "Murshidabad": "islamic_world", "Deccani": "islamic_world (Deccani sultanates)",
           # Nepal, Tibet, Bhutan, Gandhara and NW Pakistan are also swept by
           # pipelines/regional/himalaya_central_asia.py
           "Nepalese (Newar)": "himalaya_central_asia", "Tibetan": "himalaya_central_asia",
           "Sino-Tibetan": "himalaya_central_asia", "Bhutanese": "himalaya_central_asia",
           "Himalayan": "himalaya_central_asia", "Gandhara": "himalaya_central_asia",
           "Pakistan (Indus / NW)": "himalaya_central_asia"}
# fallback cultures that only restate the place
GENERIC_CULTURES = {"Indian", "Indonesian", "Thai", "Burmese", "South Indian", "Bengal", "Bihar", "Gujarat",
                    "Odisha", "Pakistan (Indus / NW)", "Malay", "Philippine", "Vietnamese", "Lao", "Sri Lankan",
                    "Native North American", "Pre-Columbian (unspecified)", "Polynesian", "Melanesian",
                    "Micronesian", "New Guinea", "Himalayan", "Ethiopian"}


def match_ordered(lex, text):
    """First pattern (in list order) that matches; list order encodes specificity."""
    for rx, lab in lex:
        if rx.search(text):
            return lab
    return None


def century_label(begin, end):
    if begin is None and end is None:
        return ""
    b = begin if begin is not None else end
    e = end if end is not None else begin
    mid = (b + e) / 2
    if e - b > 300:
        # broad archaeological ranges: name the millennium when the range sits inside one
        mb, me = (b - 1) // 1000 if b > 0 else -((-b) // 1000) - 1, (e - 1) // 1000 if e > 0 else -((-e) // 1000) - 1
        if e - b <= 1000 and mb == me:
            k = mb + 1 if mb >= 0 else -mb
            return f"{k}{_suffix(k)} millennium {'CE' if mb >= 0 else 'BCE'}"
        return ""
    if mid < 0:
        c = int((-mid) // 100) + 1
        return f"{c}{_suffix(c)} century BCE"
    c = int(mid // 100) + 1
    return f"{c}{_suffix(c)} century"


def _suffix(n):
    return "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


# ------------------------------------------------------------------ object types

OBJECT_TYPES = [
    ("photograph", r"photograph|albumen|gelatin silver|daguerreotype|negative|lantern slide"),
    ("print", r"\bprint\b|woodblock print|lithograph|etching|engraving|aquatint|mezzotint"),
    ("manuscript and book", r"manuscript|folio|codex|book|album\b|page from|leaf from|scroll"),
    ("painting", r"painting|miniature|thangka|tangka|paubha|pata\b|pattachitra|gouache|watercolou?r|opaque|"
                 r"pigments? on|oil on|bark painting|portrait"),
    ("drawing", r"drawing|sketch|pounce|cartoon"),
    ("mask", r"\bmasks?\b|headcrest|helmet mask|face mask"),
    ("sculpture", r"sculpture|statue|statuette|figure|figurine|\bhead\b|torso|bust|relief|stele|stela|carving|"
                  r"idol|image of|deity|bodhisattva|buddha|shiva|vishnu|ganesha|nkisi|minkisi|reliquary figure|"
                  r"tiki|effigy|\bbronze\b|terracotta|lingam|linga"),
    ("textile", r"textile|\bsari\b|saree|shawl|cloth|fabric|embroider|kente|adire|adinkra|mola\b|batik|ikat|"
                r"patola|chintz|palampore|rumal|carpet|\brug\b|tapestry|weaving|woven|velvet|brocade|kalamkari|"
                r"\bbark cloth|barkcloth|tapa|quilt|blanket|hanging|sash|turban cloth|kanga|kanga|kain|songket|"
                r"sampot|skirt cloth|tunic|poncho|mantle|fragment of a"),
    ("costume and accessories", r"costume|garment|dress|robe|coat|jacket|tunic|skirt|trousers|shirt|choga|"
                                r"angarkha|headdress|head ?dress|\bhat\b|\bcap\b|turban|shoe|sandal|boot|"
                                r"moccasin|footwear|belt|apron|cape|cloak|fan\b|bag\b|pouch|purse"),
    ("jewellery and ornament", r"jewel|earring|ear ornament|ear spool|ear flare|bangle|necklace|anklet|"
                               r"bracelet|armlet|\bring\b|nose ring|pendant|\bbead|brooch|pectoral|"
                               r"ornament|amulet|comb|hairpin|lip plug|labret|gorget|torque|torc"),
    ("arms and armour", r"sword|dagger|\bkris\b|keris|knife|katar|shield|spear|lance|axe|\bbow\b|arrow|club|"
                        r"helmet|armou?r|gun|matchlock|musket|pistol|scabbard|sheath|quiver|mace|weapon|tulwar"),
    ("musical instrument", r"drum|harp|sitar|vina|veena|sarangi|lute|flute|horn\b|trumpet|gong|rattle|"
                           r"xylophone|balafon|sanza|mbira|lamellophone|bell\b|slit gong|instrument"),
    ("ceramics", r"ceramic|pottery|earthenware|stoneware|porcelain|\bjar\b|\bpot\b|vessel|bowl|dish|plate|"
                 r"vase|bottle|ewer|jug|cup|beaker|stirrup|effigy vessel|olla|terracotta vessel|tile"),
    ("metalwork", r"metalwork|\bbrass|copper|silver|gold|\biron\b|bronze vessel|tray|lamp|incense|huqqa|hookah|"
                  r"huqqa base|spittoon|ewer|basin|betel|lime box|casket|bidri|repousse|enamel"),
    ("furniture and woodwork", r"furniture|chair|stool|throne|bench|bed\b|headrest|neckrest|table|chest|"
                               r"cabinet|\bbox\b|door|panel|lintel|post\b|house post|bracket|screen|"
                               r"canoe|paddle|prow|bowl, wood|staff|scepter|sceptre|fly whisk|whisk"),
    ("basketry and fibre", r"basket|basketry|mat\b|matting|featherwork|feather"),
    ("ritual object", r"shrine|altar|reliquary|stupa|ritual|offering|votive|charm|power figure|divination|"
                      r"oracle|ancestor board|malagan|board"),
    ("architectural element", r"architectural|column|pillar|capital|frieze|bracket|jali|window|railing|"
                              r"temple|facade|lintel|plaque|brick"),
    ("coin and seal", r"\bcoin\b|\bseal\b|token|medal"),
    ("tool and implement", r"tool|implement|spoon|ladle|scoop|adze|hoe|loom|weight|spindle|mortar|pestle|"
                           r"container|gourd|calabash|whistle|pipe|game|toy|doll"),
]
OBJECT_TYPES = [(n, re.compile(p, re.I)) for n, p in OBJECT_TYPES]


def object_group(*texts):
    for t in texts:
        if not t:
            continue
        for n, rx in OBJECT_TYPES:
            if rx.search(t):
                return n
    return "other"


# ------------------------------------------------------------------ makers

PLACEHOLDER = re.compile(
    r"(?i)^(unknown|unidentified|anonymous|anoniem|not known|unrecorded|n/?a|none|various|others?|"
    r"artist unknown|maker unknown|unknown maker)\b|\b(unknown|unidentified)$|"
    r"^[\w'-]+ (embroiderer|weaver|potter|carver|maker|painter|smith|sculptor|craftsman|beadworker)s?$|\bartists?(\s*\(s\))?$|^artists? of\b|\b(guild|caste)\b|"
    r"\b(people|peoples|culture|style|school|tribe)$|^(workshop|atelier)$")
MAKER_CLEAN = re.compile(r"(?i)^(design(ed)? attributed to|attributed to|attrib\.?|probably by|possibly by|probably|possibly|perhaps|"
                         r"workshop of|studio of|circle of|follower of|school of|style of|after|designed by|"
                         r"made by|carved by|painted by|signed by|by)\s+")


def clean_maker(name):
    n = tidy(name)
    prev = None
    while prev != n:
        prev = n
        n = MAKER_CLEAN.sub("", n).strip()
    return n


def is_named(name, region):
    """A personal or notname maker, not a placeholder or a culture/people name."""
    n = clean_maker(name)
    if not n or len(n) < 2 or PLACEHOLDER.search(n):
        return False
    f = fold(n)
    if re.match(r"(?i)master of|master with|master\b", n):
        return True
    for reg in REGIONS:
        lex = REGION_LEX[reg][0]
        lab = match_ordered(lex, f)
        if lab:
            # the whole name is a culture/place term ("Kuba", "Iwo Yoruba", "Moche", "Mewar")
            rest = f
            for rx, _ in lex:
                rest = rx.sub(" ", rest)
            if len(re.sub(r"[^a-z]", "", rest)) <= 4:
                return False
    if place_match(n) and len(f.split()) <= 3 and not re.search(r"\d", n):
        pm = place_match(n)
        if pm and fold(pm[2]) == f:
            return False
    return True


def maker_kind(name):
    n = clean_maker(name)
    if re.match(r"(?i)master (of|with)\b", n):
        return "notname"
    if re.search(r"(?i)\b(workshop|atelier|studio|company|co\.|& co|manufactur|factory|firm|ltd|school)\b", name):
        return "workshop/organisation"
    return "person"


# ------------------------------------------------------------- source -> rows

def year(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return int(v)
    m = re.match(r"\s*(-?\d{1,5})", str(v))
    return int(m.group(1)) if m else None


FALLBACK_NAME = {
    "democratic republic of the congo": "DR Congo", "democratic republic of congo": "DR Congo", "zaire": "DR Congo",
    "belgian congo": "DR Congo", "congo": "Congo", "republic of the congo": "Republic of the Congo",
    "cote d ivoire": "Cote d'Ivoire", "cote divoire": "Cote d'Ivoire", "ivory coast": "Cote d'Ivoire",
    "central coast": "Peru, central coast", "north coast": "Peru, north coast", "south coast": "Peru, south coast",
    "peruvian north coast": "Peru, north coast", "peruvian south coast": "Peru, south coast",
    "southern peru": "Peru, south", "northern peru": "Peru, north", "nazca valley": "Peru, south coast",
    "moche valley": "Peru, north coast", "burma": "Myanmar", "siam": "Thailand", "ceylon": "Sri Lanka",
    "usa": "United States", "upper volta": "Burkina Faso", "dahomey": "Republic of Benin",
    "gold coast": "Ghana", "abyssinia": "Ethiopia", "new hebrides": "Vanuatu", "easter island": "Rapa Nui",
    "northern africa and the sahel": "Sahel", "eastern and southern africa": "Eastern and Southern Africa",
}
LATIN = {"Mesoamerica", "Central America and Caribbean", "South America"}
DROPPED = collections.Counter()


def indigenous_evidence(text):
    t = fold(text)
    return bool(match_ordered(AMERICAS_CULTURES, t) or match_ordered(AFRICA_CULTURES, t))


def needs_indigenous(pm):
    return pm and (fold(pm[2]) in SETTLER or pm[1] in LATIN)


def decide_region(source, prior, strong_prior, place_text, label_text, extra_text, begin, end, trusted=False):
    """Region and place match for a record, or None (with the reason counted in DROPPED)."""
    pm = place_match(place_text) or place_match(label_text)
    if pm is None and not strong_prior:
        DROPPED[(source, "no region place")] += 1
        return None
    if not strong_prior and excluded_place(place_text):
        DROPPED[(source, "out-of-scope place first")] += 1
        return None
    if strong_prior and (prior == "africa" or pm is None) and excluded_place(place_text + "; " + label_text):
        DROPPED[(source, "out-of-scope place first")] += 1
        return None
    if strong_prior:
        # department / section records stay in the department's region unless their
        # place belongs to another swept region (Cleveland files Island SE Asia under Oceania)
        region = pm[0] if pm else prior
    else:
        region = pm[0]
        if prior and region != prior:
            DROPPED[(source, "place outside sweep region")] += 1
            return None
    if region in ("americas_oceania", "africa") and needs_indigenous(pm) and not trusted:
        mid = None if begin is None or end is None else (begin + end) / 2
        early = pm[1] in LATIN and mid is not None and mid < 1550
        if not early and not indigenous_evidence(label_text + (" " + extra_text if source in ("vam", "rijks") else "")):
            DROPPED[(source, "settler-country record without Indigenous culture term")] += 1
            return None
    if begin is not None and begin >= 1960:
        DROPPED[(source, "made 1960 or later")] += 1
        return None
    return region, pm


def classify(row, label_text, place_text, extra_text, agent=None):
    lex_c, lex_p = REGION_LEX[row["region"]]
    lt, pt, et = fold(label_text), fold(place_text), fold(extra_text)
    culture = match_ordered(lex_c, lt)
    src = "label"
    if not culture:
        culture = match_ordered(lex_c, pt)
        src = "place"
    if not culture:
        culture = match_ordered(lex_c, et)
        src = "description"
    if not culture and agent:
        # the source's own culture name for the record (AIC culture agents such as
        # "Baatonu (Bariba)", "Salinar"; Cleveland "Lobi-style maker")
        culture = agent
        src = "label (source culture name)"
    if not culture:
        pm = row["_pm"]
        culture = f"Unspecified ({FALLBACK_NAME.get(pm[2], pm[2].title())})" if pm else "Unspecified"
        src = "fallback"
    elif culture in GENERIC_CULTURES:
        src += " (generic)"
    period = match_ordered(lex_p, fold(label_text + " " + row["date_text"]))
    psrc = "recorded" if period else ""
    if not period:
        period = match_ordered(lex_p, et)
        psrc = "description" if period else ""
    if not period:
        period = century_label(row["date_begin"], row["date_end"])
        psrc = "century" if period else ""
    row.update(culture=culture, culture_group=culture.split(":")[0].strip(), culture_source=src,
               period=period, period_source=psrc,
               overlap=OVERLAP.get(culture) or OVERLAP.get(culture.split(":")[0])
               or (OVERLAP.get(period, "") if culture in GENERIC_CULTURES or src == "fallback" else ""))


WESTERN = re.compile(r"\((English|British|American|French|Dutch|German|Scottish|Irish|Italian|Austrian|Swiss|"
                     r"Danish|Belgian|Swedish|Canadian|Australian|Spanish|Portuguese|Russian|Finnish|Norwegian)\b")


# military / honorific titles mark British colonial-era artists in these records
WESTERN_TITLES = re.compile(r"^(Captain|Capt\.?|Lt\.?|Lieutenant|Colonel|Col\.?|Major|General|Sir|Lady|Mrs\.?|Miss|"
                            r"Dr\.?|Rev\.?|Reverend)\s")
# frequent Western makers in the V&A South & SE Asia records, reviewed by hand (2026-10-28)
WESTERN_NAMES = re.compile(r"(?<![a-z])(griffiths|de fabeck|fabeck|lockwood kipling|kipling|elkington|blaikie keith|"
                           r"daniell|chinnery|canning|carpenter|locker|landseer|grindlay|orme|simpson)(?![a-z])")


def make_row(source, rid, region, pm, title, otype, oclass, labels, place_text, extra, date_text, begin, end,
             makers, materials, institution, collection, url, sweep, agent=None):
    begin = begin if begin is None or -12000 < begin < 2100 else None
    end = end if end is None or -12000 < end < 2100 else None
    if begin is not None and end is not None and begin > end:
        begin, end = end, begin
    named, western = [], []
    for n, role in makers:
        if is_named(n, region):
            western.append(bool(WESTERN.search(n) or WESTERN_TITLES.search(n) or WESTERN_NAMES.search(fold(n)))
                           or (source == "vam" and bool(re.match(r"^[A-Z][\w'-]+, [A-Z]", n))))
            nm = clean_maker(n.split(" (")[0]) if "(" in n else clean_maker(n)
            if nm and (nm, role) not in [(a, b) for a, b, _ in named]:
                named.append((nm, role, maker_kind(n)))
    row = {"source": source, "id": rid, "region": region, "subregion": pm[1] if pm else "",
           "place": pm[2].title() if pm else "", "_pm": pm, "title": tidy(title)[:200],
           "object_type": tidy(otype)[:80], "object_group": object_group(otype, oclass, title, materials),
           "labels": tidy(labels)[:300], "date_text": tidy(date_text)[:80], "date_begin": begin, "date_end": end,
           "makers": named, "attributed": bool(named),
           "western_makers": bool(western) and all(western), "materials": tidy(materials)[:200],
           "institution": institution, "collection": collection, "url": url, "sweep": sweep}
    if row["object_group"] == "photograph":
        DROPPED[(source, "photograph")] += 1
        return None
    if named and row["western_makers"]:
        # European / American artists depicting the region (Daniell, Poynter, Gauguin):
        # colonial-era Western art, not the region's own traditions
        DROPPED[(source, "made by a Western artist")] += 1
        return None
    classify(row, labels, place_text, extra, agent)
    if source == "vam" and sweep.startswith("place:"):
        if collection in VAM_LABEL_ONLY_COLLECTIONS and row["culture_source"] != "label":
            DROPPED[(source, "Prints, Drawings & Paintings record without a school/culture label")] += 1
            return None
        if region != "south_southeast_asia":
            if (row["object_group"] in ("print", "drawing", "painting", "manuscript and book")
                    and row["culture_source"] != "label"):
                DROPPED[(source, "two-dimensional work without a recorded Indigenous culture")] += 1
                return None
            if named and (row["culture_source"] == "fallback" or any(COMMERCIAL_ROLES.search(r) for _, r in makers)):
                DROPPED[(source, "named Western/commercial maker without an Indigenous culture")] += 1
                return None
    return row


def _add(out, row):
    if row is not None:
        out.append(row)


SOURCE_INST = {"vam": "Victoria and Albert Museum", "cma": "Cleveland Museum of Art",
               "aic": "Art Institute of Chicago", "rijks": "Rijksmuseum"}


EAST_ASIAN_STYLE = re.compile(r"(?i)\b(qing|ming|yuan|song|tang|kangxi|yongzheng|qianlong|jiaqing|daoguang|"
                              r"guangxu|edo|meiji|joseon|goryeo)\b")


def rows_vam(items):
    out = []
    for r, sweep, prior in items:
        typ = r["type"]
        if re.search(r"(?i)photograph|negative|lantern slide", typ) or r["coll"] in SKIP_VAM_COLLECTIONS:
            DROPPED[("vam", "photograph / out-of-scope collection")] += 1
            continue
        styles = "; ".join(s for s, _ in r["styles"])
        peoples = "; ".join(n for n, _ in r["peoples"])
        labels = "; ".join(x for x in (styles, peoples, r["production"]) if x)
        places = "; ".join(p for p, _ in r["places"])
        place_text = "; ".join(x for x in (places, r["production"], r["brief"]) if x)
        extra = " ".join([r["title"], typ, r["brief"], " ".join(r["cats"])])
        dt, b, e = (r["dates"][0] if r["dates"] else ["", None, None])
        b, e = year(b), year(e)
        if EAST_ASIAN_STYLE.search(styles):
            DROPPED[("vam", "East Asian period style (Qing, Ming, Edo, ...)")] += 1
            continue
        strong = sweep == "section"
        dec = decide_region("vam", prior, strong, place_text, labels, extra, b, e)
        if not dec:
            continue
        region, pm = dec
        makers = [(n, role) for n, role in r["persons"] + r["orgs"]]
        _add(out, make_row("vam", r["id"], region, pm, r["title"] or typ, typ, "", labels, place_text, extra,
                            dt, b, e, makers, r["mats"], SOURCE_INST["vam"], r["coll"],
                            VAM_OBJECT_URL.format(r["id"]), sweep))
    return out


def rows_cma(items):
    out = []
    for r, sweep, prior in items:
        cult = "; ".join(r.get("culture") or [])
        extra = " ".join(filter(None, [r.get("title") or "", r.get("type") or ""]))
        b, e = year(r.get("creation_date_earliest")), year(r.get("creation_date_latest"))
        trusted = prior is not None and not re.search(r"(?i)spanish|colonial|europe|american,", cult)
        dec = decide_region("cma", prior, prior is not None, cult, cult, extra, b, e, trusted=trusted)
        if not dec:
            continue
        region, pm = dec
        if pm is None:
            pm = place_match(cult)
            if pm and pm[0] != region:
                pm = None
        makers = []
        for c in r.get("creators") or []:
            desc = c.get("description") or ""
            makers.append((desc, c.get("role") or ""))
        m_style = re.search(r"(?i)([A-Z][\w'-]+)[-–]style maker", cult)
        _add(out, make_row("cma", r.get("accession_number") or str(r.get("id")), region, pm, r.get("title") or "",
                            r.get("type") or "", "", cult, cult, extra, r.get("creation_date") or "", b, e, makers,
                            r.get("technique") or "", SOURCE_INST["cma"], r.get("department") or "",
                            r.get("url") or "", sweep, agent=m_style.group(1) if m_style else None))
    return out


AIC_OUT_DEPTS = {"Applied Arts of Europe", "Painting and Sculpture of Europe", "Architecture and Design",
                 "Contemporary Art", "Modern Art", "Modern and Contemporary Art", "Arts of Greece, Rome, and Byzantium",
                 "Prints and Drawings"}


def agent_culture(name, named):
    """A culture-agent name usable as the culture label, or None."""
    n = tidy(re.sub(r"\(.*?\)", " ", name or ""))
    if named or not n or PLACEHOLDER.search(n) or len(n) > 40 or re.search(r"\d", n):
        return None
    pm = place_match(n)
    if pm and fold(pm[2]) == fold(n):
        return None
    if fold(n) in {"islamic", "archaic", "unknown", "african", "american", "indian", "asian"}:
        return None
    return n


def rows_aic(items):
    out = []
    for r, sweep, _ in items:
        dept = r.get("department_title") or ""
        if dept in AIC_OUT_DEPTS:
            continue
        disp = r.get("artist_display") or ""
        first = disp.split("\n")[0]
        artist = r.get("artist_title") or ""
        # AIC files cultures as agents ("Kuba", "Moche", "Grasslands"); personal makers
        # carry a "(Nationality, dates)" or "active ..." qualifier on the first line
        named = (bool(artist) and is_named(artist, None) and is_named(first, None)
                 and bool(re.search(r"\((?=[^)]*(\d{3}|active|born|died|century))", first)))
        styles = "; ".join(r.get("style_titles") or [])
        culture_lines = disp if not named else "\n".join(disp.split("\n")[1:])
        labels = "; ".join(x for x in (culture_lines.replace("\n", "; "), styles) if x)
        place_text = "; ".join(x for x in (r.get("place_of_origin") or "", disp.replace("\n", "; ")) if x)
        extra = " ".join(filter(None, [r.get("title") or "", r.get("classification_title") or "",
                                       r.get("artwork_type_title") or ""]))
        b, e = year(r.get("date_start")), year(r.get("date_end"))
        dec = decide_region("aic", None, False, place_text, labels, extra, b, e)
        if not dec:
            continue
        region, pm = dec
        makers = [(first if "(" in first else artist, "")] if named else []
        _add(out, make_row("aic", str(r["id"]), region, pm, r.get("title") or "",
                            r.get("artwork_type_title") or "", r.get("classification_title") or "", labels,
                            place_text, extra, r.get("date_display") or "", b, e, makers,
                            r.get("medium_display") or "", SOURCE_INST["aic"], dept,
                            f"https://www.artic.edu/artworks/{r['id']}", "dump", agent=agent_culture(artist, named)))
    return out


def rows_rijks(items):
    out = []
    for r, sweep, _ in items:
        types = "; ".join(t for t in r.get("types") or [] if t)
        if re.search(r"(?i)photograph|\bprint\b|foto", types):
            DROPPED[("rijks", "photograph / print")] += 1
            continue
        places = "; ".join(r.get("places") or [])
        prod_txt = "; ".join(m[1:] for m in r.get("makers") or [] if m.startswith("~"))
        labels = prod_txt
        extra = " ".join((r.get("names") or [])[:1] + [types] + (r.get("texts") or [])[:2])
        b, e = year(r.get("begin")), year(r.get("end"))
        dec = decide_region("rijks", None, False, places + "; " + prod_txt, labels, extra, b, e)
        if not dec:
            continue
        region, pm = dec
        makers = [(m, "") for m in r.get("makers") or [] if not m.startswith("~")]
        title = next((n for n in r.get("names") or [] if n), "")
        _add(out, make_row("rijks", r.get("objno") or r["id"], region, pm, title, types, "", labels,
                            places + "; " + prod_txt, extra, r.get("date_text") or "", b, e, makers,
                            "; ".join(r.get("mats") or []), SOURCE_INST["rijks"], "", r["id"], sweep))
    return out


# ------------------------------------------------------------------ outputs

SOURCES = ("vam", "cma", "aic", "rijks")


def _q(vals, p):
    return round(vals[min(len(vals) - 1, int(p * len(vals)))]) if vals else ""


def top(counter, n=5):
    return "; ".join(f"{k} ({v})" for k, v in counter.most_common(n) if k)


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def write_region(region, rows):
    rows.sort(key=lambda r: (r["culture"], r["period"], r["source"], r["date_begin"] or 0))
    ocols = ["source", "id", "title", "region", "subregion", "place", "culture", "culture_group", "culture_source",
             "period", "period_source", "object_group", "object_type", "labels_recorded", "date_text",
             "date_begin", "date_end", "makers", "attributed", "materials", "institution", "collection",
             "overlap", "sweep", "url"]
    write_csv(os.path.join(OUT_DIR, f"{region}_objects.csv"), ocols, [[
        r["source"], r["id"], r["title"], r["region"], r["subregion"], r["place"], r["culture"], r["culture_group"],
        r["culture_source"], r["period"], r["period_source"], r["object_group"], r["object_type"], r["labels"],
        r["date_text"], "" if r["date_begin"] is None else r["date_begin"],
        "" if r["date_end"] is None else r["date_end"],
        "; ".join(f"{n} ({role})" if role else n for n, role, _ in r["makers"]), int(r["attributed"]),
        r["materials"], r["institution"], r["collection"], r["overlap"], r["sweep"], r["url"]] for r in rows])

    # ---- traditions
    def blank():
        return {"src": collections.Counter(), "att": 0, "begins": [], "ends": [], "mids": [],
                "types": collections.Counter(), "raw": collections.Counter(), "makers": collections.Counter(),
                "subs": collections.Counter(), "periods": collections.Counter(), "cultures": collections.Counter(),
                "csrc": collections.Counter(), "ex": [], "overlap": ""}
    agg = collections.defaultdict(blank)
    for r in rows:
        keys = [("culture", r["culture"], "", ""),
                ("culture_type", r["culture"], "", r["object_group"])]
        if r["culture_group"] != r["culture"]:
            keys.append(("culture_group", r["culture_group"], "", ""))
        if r["period"]:
            keys += [("culture_period", r["culture"], r["period"], ""),
                     ("culture_period_type", r["culture"], r["period"], r["object_group"]),
                     ("period", "", r["period"], "")]
        for k in keys:
            a = agg[k]
            a["src"][r["source"]] += 1
            a["att"] += r["attributed"]
            if r["date_begin"] is not None:
                a["begins"].append(r["date_begin"])
            if r["date_end"] is not None:
                a["ends"].append(r["date_end"])
            if r["date_begin"] is not None and r["date_end"] is not None:
                a["mids"].append((r["date_begin"] + r["date_end"]) / 2)
            a["types"][r["object_group"]] += 1
            a["raw"][r["labels"][:70]] += 1
            for n, _, _ in r["makers"]:
                a["makers"][n] += 1
            a["subs"][r["subregion"]] += 1
            a["periods"][r["period"]] += 1
            a["cultures"][r["culture"]] += 1
            a["csrc"][r["culture_source"].split(" ")[0]] += 1
            a["overlap"] = a["overlap"] or r["overlap"]
            if len(a["ex"]) < 4:
                a["ex"].append(f"{r['source']}:{r['id']}")
    tcols = ["kind", "key", "culture", "culture_group", "period", "object_group", "objects"] + \
            [f"objects_{s}" for s in SOURCES] + \
            ["n_sources", "attributed", "attributed_share", "date_begin_min", "date_end_max", "mid_p10",
             "mid_median", "mid_p90", "top_object_groups", "top_periods", "top_cultures", "subregions",
             "culture_from", "named_makers", "raw_labels", "overlap", "example_ids"]
    trows = []
    order = {"culture_group": 0, "culture": 1, "culture_period": 2, "culture_type": 3, "culture_period_type": 4,
             "period": 5}
    for (kind, cult, per, typ), a in sorted(agg.items(), key=lambda kv: (order[kv[0][0]], -sum(kv[1]["src"].values()))):
        n = sum(a["src"].values())
        mids = sorted(a["mids"])
        key = " | ".join(fold(x) for x in (cult, per, typ) if x)
        trows.append([kind, key, cult, cult.split(":")[0].strip() if cult else "", per, typ, n] +
                     [a["src"][s] for s in SOURCES] +
                     [sum(1 for s in SOURCES if a["src"][s]), a["att"], round(a["att"] / n, 3),
                      min(a["begins"]) if a["begins"] else "", max(a["ends"]) if a["ends"] else "",
                      _q(mids, 0.1), round(statistics.median(mids)) if mids else "", _q(mids, 0.9),
                      top(a["types"]), top(a["periods"]) if kind in ("culture", "culture_group", "culture_type") else "",
                      top(a["cultures"]) if kind == "period" or kind == "culture_group" else "",
                      top(a["subs"], 3), top(a["csrc"], 4), top(a["makers"], 8), top(a["raw"], 3), a["overlap"],
                      " ".join(a["ex"])])
    write_csv(os.path.join(OUT_DIR, f"{region}_traditions.csv"), tcols, trows)

    # ---- makers
    mk = collections.defaultdict(lambda: {"names": collections.Counter(), "src": collections.Counter(),
                                          "cult": collections.Counter(), "per": collections.Counter(),
                                          "roles": collections.Counter(), "kind": collections.Counter(),
                                          "types": collections.Counter(), "begins": [], "ends": [], "ex": []})
    for r in rows:
        for n, role, kind in r["makers"]:
            k = fold(re.sub(r"\(.*?\)", " ", n)).replace(",", " ")
            k = " ".join(k.split())
            if not k:
                continue
            m = mk[k]
            m["names"][n] += 1
            m["src"][r["source"]] += 1
            m["cult"][r["culture"]] += 1
            m["per"][r["period"]] += 1
            m["types"][r["object_group"]] += 1
            if role:
                m["roles"][role.lower()] += 1
            m["kind"][kind] += 1
            if r["date_begin"] is not None:
                m["begins"].append(r["date_begin"])
            if r["date_end"] is not None:
                m["ends"].append(r["date_end"])
            if len(m["ex"]) < 4:
                m["ex"].append(f"{r['source']}:{r['id']}")
    mcols = ["maker", "name_variants", "maker_kind", "objects"] + [f"objects_{s}" for s in SOURCES] + \
            ["n_sources", "traditions", "periods", "object_groups", "roles", "date_begin_min", "date_end_max",
             "example_ids"]
    mrows = []
    for k, m in sorted(mk.items(), key=lambda kv: (-sum(kv[1]["src"].values()), kv[0])):
        mrows.append([m["names"].most_common(1)[0][0], top(m["names"], 4), m["kind"].most_common(1)[0][0],
                      sum(m["src"].values())] + [m["src"][s] for s in SOURCES] +
                     [sum(1 for s in SOURCES if m["src"][s]), top(m["cult"], 4), top(m["per"], 3),
                      top(m["types"], 3), top(m["roles"], 3), min(m["begins"]) if m["begins"] else "",
                      max(m["ends"]) if m["ends"] else "", " ".join(m["ex"])])
    write_csv(os.path.join(OUT_DIR, f"{region}_makers.csv"), mcols, mrows)
    return agg, mk


def build(raw):
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = []
    builders = {"vam": rows_vam, "cma": rows_cma, "aic": rows_aic, "rijks": rows_rijks}
    for src, items in raw.items():
        got = builders[src](items)
        print(f"  {src}: {len(items)} records read, {len(got)} kept", file=sys.stderr)
        rows += got
    # one object per (source, id): V&A records can arrive from several sweeps
    seen, uniq = set(), []
    for r in rows:
        if (r["source"], r["id"]) not in seen:
            seen.add((r["source"], r["id"]))
            uniq.append(r)
    summary = []
    for region in REGIONS:
        rr = [r for r in uniq if r["region"] == region]
        agg, mk = write_region(region, rr)
        for src in SOURCES + ("all",):
            sr = [r for r in rr if src == "all" or r["source"] == src]
            if not sr:
                continue
            n = len(sr)
            summary.append([region, src, n, sum(r["attributed"] for r in sr),
                            round(sum(r["attributed"] for r in sr) / n, 3),
                            round(sum(1 for r in sr if r["culture_source"] in ("label", "place")) / n, 3),
                            round(sum(1 for r in sr if not r["culture_source"].startswith("fallback")) / n, 3),
                            round(sum(1 for r in sr if r["period_source"] in ("recorded", "description")) / n, 3),
                            round(sum(1 for r in sr if r["date_begin"] is not None) / n, 3),
                            len({r["culture"] for r in sr}), len({r["period"] for r in sr if r["period"]}),
                            len({fold(n_) for r in sr for n_, _, _ in r["makers"]}),
                            sum(1 for r in sr if r["overlap"].startswith("islamic")),
                            sum(1 for r in sr if r["overlap"].startswith("himalaya"))])
        print(f"{region}: {len(rr)} objects, {len({r['culture'] for r in rr})} cultures, "
              f"{len(mk)} named makers, attributed {sum(r['attributed'] for r in rr)}", file=sys.stderr)
    write_csv(os.path.join(OUT_DIR, "south_asia_africa_americas_sources.csv"),
              ["region", "source", "objects", "attributed", "attributed_share", "culture_specific_share",
               "culture_any_share", "period_recorded_share", "dated_share", "cultures", "periods", "named_makers",
               "overlap_islamic_world", "overlap_himalaya_central_asia"], summary)
    write_csv(os.path.join(OUT_DIR, "south_asia_africa_americas_dropped.csv"), ["source", "reason", "records"],
              [[s, why, n] for (s, why), n in sorted(DROPPED.items())])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skip", default="", help="comma-separated sources to skip: vam,cma,aic,rijks")
    ap.add_argument("--fetch-only", action="store_true", help="harvest into the cache, write nothing")
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between requests (default 1.0)")
    ap.add_argument("--rijks-max", type=int, default=1500, help="max Rijksmuseum objects to fetch")
    args = ap.parse_args()
    DELAY[0] = args.delay
    skip = set(filter(None, args.skip.split(",")))
    raw = {}
    if "cma" not in skip:
        raw["cma"] = harvest_cma(REGIONS)
    if "vam" not in skip:
        raw["vam"] = harvest_vam(REGIONS)
    if "rijks" not in skip:
        raw["rijks"] = harvest_rijks(args.rijks_max)
    if "aic" not in skip and not args.fetch_only:
        raw["aic"] = harvest_aic()
    print(f"network: {dict(NET)}; V&A undated records skipped by year splits: {dict(UNDATED_SKIPPED)}",
          file=sys.stderr)
    if args.fetch_only:
        return
    build(raw)


if __name__ == "__main__":
    main()
