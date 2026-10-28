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
  Mughal painting is owned by the Islamic-world job; Mughal objects that fall
      into these sweeps are kept but flagged (overlap = islamic_world).

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
                           attributed share, with tradition / period / date

Usage: python3 pipelines/regional/south_asia_africa_americas.py
           [--skip vam,cma,aic,rijks] [--fetch-only] [--delay 1.0] [--rijks-max 1500]
"""
import argparse
import collections
import csv
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
from build_traditions import fold, tidy  # noqa: E402

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
            "kathmandu", "kathmandu valley", "rajasthan", "mewar", "udaipur", "jaipur", "amber", "kota", "bundi",
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
        ],
        "Southeast Asia": [
            "southeast asia", "south east asia", "mainland southeast asia", "cambodia", "kampuchea", "angkor",
            "thailand", "siam", "ayutthaya", "sukhothai", "lopburi", "bangkok", "chiang mai", "lan na", "lanna",
            "laos", "luang prabang", "vietnam", "viet nam", "annam", "champa", "tonkin", "cochin china", "hue",
            "myanmar", "burma", "pagan", "bagan", "mandalay", "rangoon", "yangon", "ava", "arakan", "shan state",
            "kachin state", "pyu", "indonesia", "java", "central java", "east java", "eastern java", "west java",
            "bali", "lombok", "sumatra", "borneo", "kalimantan", "sulawesi", "celebes", "moluccas", "maluku",
            "flores", "sumba", "timor", "nias", "dutch east indies", "netherlands indies", "yogyakarta",
            "jogjakarta", "surakarta", "solo", "cirebon", "madura", "malaysia", "malaya", "malay peninsula",
            "penang", "malacca", "melaka", "sarawak", "sabah", "brunei", "singapore", "philippines", "luzon",
            "mindanao", "sulu", "dvaravati", "srivijaya", "majapahit", "khmer",
        ],
    },
    "africa": {
        "West Africa": [
            "west africa", "western africa", "nigeria", "benin city", "ile-ife", "ife", "igbo-ukwu", "nok",
            "yorubaland", "ghana", "gold coast", "asante", "ashanti", "kumasi", "cote d ivoire", "cote divoire",
            "ivory coast", "mali", "bandiagara", "djenne", "jenne", "timbuktu", "burkina faso", "upper volta",
            "senegal", "gambia", "guinea", "guinea-bissau", "sierra leone", "liberia", "togo", "republic of benin",
            "dahomey", "abomey", "niger", "cameroon", "cameroon grassfields", "grassfields", "bamum", "foumban",
            "mauritania", "korhogo", "lagos", "ibadan", "calabar", "oyo", "abeokuta", "ikere", "owo", "benin kingdom",
            "kingdom of benin", "sahel", "northern africa and the sahel", "western sudan",
        ],
        "Central Africa": [
            "central africa", "democratic republic of the congo", "democratic republic of congo", "congo",
            "zaire", "belgian congo", "republic of the congo", "congo brazzaville", "gabon", "angola", "cabinda",
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
            "magdala",
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
            "new guinea", "papua new guinea", "papua", "west papua", "irian jaya", "sepik", "sepik river",
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
EXCLUDE_PLACES = ["egypt", "morocco", "algeria", "tunisia", "libya", "iran", "persia", "iraq", "syria",
                  "turkey", "afghanistan", "china", "japan", "korea", "mongolia", "uzbekistan"]

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


def place_match(text):
    """First (longest) region place in the text -> (region, subregion, matched name) or None."""
    t = fold(text)
    if not t:
        return None
    best = None
    for rx, n, region, sub in _PLACE_RE:
        m = rx.search(t)
        if m and (best is None or m.start() < best[3]):
            best = (region, sub, n, m.start())
            if m.start() == 0:
                break
    return best[:3] if best else None


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
    """Yield records for params, bisecting the year range until each query is under the cap."""
    n = vam_count(dict(params, year_made_from=lo, year_made_to=hi), cache_dir)
    if n == 0:
        return
    if n <= VAM_MAX or hi - lo < 2:
        if n > VAM_MAX:
            print(f"  V&A {label} {lo}-{hi}: {n} records, capped at {VAM_MAX}", file=sys.stderr)
        yield from vam_pages(dict(params, year_made_from=lo, year_made_to=hi), cache_dir, f"{label}_{lo}_{hi}")
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
SKIP_VAM_COLLECTIONS = {"Department of Photography", "Theatre and Performance Collection", "Young V&A Collection",
                        "National Art Library", "Museum of Childhood"}


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
            {"department": dept, "skip": skip, "limit": limit, "fields": CMA_FIELDS})
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
    def notation(x):
        for n in x.get("notation") or []:
            if n.get("@language") == "en":
                return n.get("@value", "")
        return (x.get("notation") or [{}])[0].get("@value", "") if x.get("notation") else x.get("_label", "")

    def lin(objs, lang="300388277"):
        out = []
        for o in objs or []:
            langs = [l.get("id", "") for l in o.get("language") or []]
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
