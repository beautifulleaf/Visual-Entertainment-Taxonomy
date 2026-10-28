"""Targeted sweep that thickens Africa, Oceania and Indigenous Australia
(visual-art-plan.md §2A, §2.1 point 4, §2.1b, §2.2).

The earlier sweep (pipelines/regional/south_asia_africa_americas.py: V&A,
Cleveland, AIC, Rijksmuseum) left these cells thin: Africa 1,557 objects and
Oceania 104. This script harvests open collection data from institutions that
are strong in exactly these areas and writes the same object / tradition /
maker tables, so the coverage audit (§2.2) can combine them. The cells are
tradition-led: the primary node is the culture or workshop (Yoruba, Edo/Benin
court, Kuba, Asmat, Sepik, Maori, Yolngu bark painting, ...), and named
masters (Olowe of Ise, Bamgboye, Maku of Erin, ...) hang under it; the
attributed share per tradition is the attribution profile.

Sources (all keyless; every response is cached gzip-compressed under
data/raw/regional/africa_oceania_targeted/<source>/, so re-runs read the cache
and an interrupted harvest resumes where it stopped):

  mia       Minneapolis Institute of Art, public search API (search.artsmia.org,
            Elasticsearch-backed; the same records as the artsmia/collection
            GitHub dump, but current). Department "Arts of Global Africa" and
            every object with continent Africa or Oceania. Mia files cultures
            as artists ("Yoruba artist"), so those count as unattributed.
            Public domain data (CC0 metadata).
  penn      Penn Museum bulk CSV (collections.penn.museum, CC BY 4.0, ~150 MB,
            downloaded once): curatorial sections African and Oceanian. The
            www.penn.museum host answers 403 to this client; the collections
            host serves the file. Oceanian includes Island Southeast Asia
            (Philippines, Borneo, Sumatra), which is dropped here (owned by the
            south_southeast_asia sweep).
  tepapa    Museum of New Zealand Te Papa Tongarewa collections API
            (data.tepapa.govt.nz). Assigned keys need registration, but the API
            itself hands out short-lived guest tokens for keyless use (its
            documented guest key); metadata CC BY 4.0. Collections Pacific
            Cultures and Taonga Maori, objects only. `influencedBy` carries the
            culture / iwi and the Maori art periods (Te Puawaitanga, Te Huringa).
  auckland  Auckland War Memorial Museum (Tamaki Paenga Hira) Linked Open Data
            SPARQL endpoint (api.aucklandmuseum.com/sparql; API v2 dropped its
            key). The Elasticsearch search route sits behind a bot challenge;
            SPARQL is used instead, a few seconds apart, with long back-off when
            the challenge page appears. Departments (keepers)
            Pacific, World, Ethnology and Maori, plus every object whose cultural
            origin is Maori / Moriori / an iwi. The endpoint's firewall refuses
            ORDER BY / UNION / "||" in queries, so ids are listed per department
            and fields fetched with simple per-field queries over id batches.
  yale      Yale LUX (lux.collections.yale.edu, Linked Art, keyless):
            Yale University Art Gallery African Art and Indo-Pacific Art
            collections, and Yale Peabody Museum Anthropology records matching
            Africa / Oceania terms. Each record is fetched individually (~3 req/s).

Checked and skipped (reported in the run summary): Brooklyn Museum (API key;
the site answers with a Vercel security checkpoint), Musee du quai Branly
(no open-data API or bulk download; HTML catalogue only), National Gallery of
Australia (searchthecollection.nga.gov.au answers 403), Art Gallery of NSW
(robots.txt disallows Anthropic agents, and pages sit behind a JS client
challenge), Te Papa assigned keys (not needed: guest token), Smithsonian NMAfA
(pipelines/regional/smithsonian.py), the Met (pipelines/unattributed/).

Shared logic (place lexicon, culture lexicons, object groups, maker tests,
century labels) is imported from south_asia_africa_americas.py; this script
extends the Africa and Oceania culture lexicons (Herero, San, Mbuti, Wardaman,
Tiwi, Yolngu, Papunya Tula / Western Desert, Maori iwi, Moriori, ...) and the
period lexicon (Maori art periods).

Filters: objects made 1960 or later; photographs; Egypt, North Africa,
Coptic/Hebrew/Classical material (owned by other jobs); Island Southeast Asia
(south_southeast_asia sweep); the Americas (Smithsonian NMAI and the earlier
sweep); prehistoric lithics and debitage (flakes, cores, scrapers, sherds);
records from settler countries without Indigenous evidence (unless the
source's department is Indigenous by definition: Te Papa Taonga Maori /
Pacific Cultures, Auckland Pacific); objects whose named makers are all
Western. Counts per reason go to _dropped.csv.

Outputs (data/interim/regional/), same columns as africa_* / americas_oceania_*
(objects_<source> columns for this sweep's sources; Oceania rows carry
region = americas_oceania, subregion = Oceania, as in the earlier sweep):
  africa_oceania_targeted_objects.csv     one row per object
  africa_oceania_targeted_traditions.csv  culture_group | culture | culture_period |
                                          culture_type | culture_period_type | period
                                          per region: counts per source, n_sources,
                                          attributed share, dates, top makers
  africa_oceania_targeted_makers.csv      named makers
  africa_oceania_targeted_sources.csv     per region x source summary, plus the
                                          growth over the earlier sweep
  africa_oceania_targeted_dropped.csv     records dropped, per source and reason

Usage: python3 pipelines/regional/africa_oceania_targeted.py
           [--only mia,penn,tepapa,auckland,yale] [--skip ...] [--fetch-only]
           [--delay 0.34] [--yale-max N]
Run one --only --fetch-only process per source for parallel harvesting, then a
plain run (all from cache) to build the tables.
"""
import argparse
import collections
import concurrent.futures
import csv
import gzip
import json
import os
import re
import statistics
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw", "regional", "africa_oceania_targeted")
OUT_DIR = os.path.join(ROOT, "data", "interim", "regional")
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"
PREFIX = "africa_oceania_targeted"

sys.path.insert(0, os.path.join(ROOT, "pipelines", "regional"))
import south_asia_africa_americas as saa  # noqa: E402
from south_asia_africa_americas import (fold, tidy, place_match, excluded_place, match_ordered,  # noqa: E402
                                        century_label, object_group, is_named, clean_maker, maker_kind,
                                        slug, top, _q, write_csv)

SOURCES = ("mia", "penn", "tepapa", "auckland", "yale")
SOURCE_INST = {"mia": "Minneapolis Institute of Art", "penn": "Penn Museum",
               "tepapa": "Museum of New Zealand Te Papa Tongarewa",
               "auckland": "Auckland War Memorial Museum", "yale": "Yale University (LUX)"}
SKIPPED_SOURCES = [
    ("brooklyn", "Brooklyn Museum", "API needs a key; site answers with a Vercel security checkpoint (429)"),
    ("quai_branly", "Musee du quai Branly", "no open-data API or bulk download; HTML catalogue only"),
    ("nga", "National Gallery of Australia", "searchthecollection.nga.gov.au answers 403; no open data"),
    ("agnsw", "Art Gallery of New South Wales",
     "robots.txt disallows anthropic-ai/ClaudeBot; pages behind a JS client challenge; no open API"),
    ("penn_www", "Penn Museum (www.penn.museum)", "403 to this client; collections.penn.museum serves the CSV"),
]

# ------------------------------------------------------------------ fetching

_last = [0.0]
_lock = threading.Lock()
DELAY = [0.34]
NET = collections.Counter()


class Challenge(Exception):
    pass


def http(url, data=None, headers=None, timeout=180, attempts=6, accept="application/json"):
    """GET (or POST data) -> text, or None for a permanent failure. Retries
    network errors, 429/5xx and bot-challenge pages with growing back-off."""
    for attempt in range(attempts):
        with _lock:   # requests start at most every DELAY seconds, also across worker threads
            wait = DELAY[0] - (time.time() - _last[0])
            if wait > 0:
                time.sleep(wait)
            _last[0] = time.time()
        h = {"User-Agent": UA, "Accept": accept}
        h.update(headers or {})
        req = urllib.request.Request(url, data=data, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                text = r.read().decode("utf-8", errors="replace")
            if text.lstrip()[:200].lower().startswith("<!doctype html") and "Testing connection" in text[:2000]:
                raise Challenge()
            NET["ok"] += 1
            return text
        except Challenge:
            NET["challenge"] += 1
            pause = 120 * (attempt + 1)
            print(f"  bot challenge on {url[:90]} - pausing {pause}s", file=sys.stderr)
            time.sleep(pause)
            continue
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read(3000).decode("utf-8", "replace")
            except Exception:
                pass
            if "Testing connection" in body:
                NET["challenge"] += 1
                pause = 120 * (attempt + 1)
                print(f"  bot challenge ({e.code}) on {url[:90]} - pausing {pause}s", file=sys.stderr)
                time.sleep(pause)
                continue
            if e.code == 401:
                raise
            if e.code in (400, 403, 404, 410, 422):
                NET[f"http_{e.code}"] += 1
                print(f"  {e.code} {url[:120]}", file=sys.stderr)
                return None
            NET[f"http_{e.code}"] += 1
            ra = e.headers.get("Retry-After") if e.headers else None
            pause = int(ra) if ra and ra.isdigit() else 15 * (attempt + 1)
            print(f"  {e.code} {url[:100]} (retry {attempt + 1}, {pause}s)", file=sys.stderr)
            time.sleep(min(pause, 300))
            continue
        except Exception as e:  # URLError, timeouts, resets, incomplete reads
            NET["neterr"] += 1
            print(f"  {type(e).__name__}: {e} {url[:100]} (retry {attempt + 1})", file=sys.stderr)
            time.sleep(min(120, 5 * 2 ** attempt))
    NET["failed"] += 1
    return None


def cache_read(path):
    if os.path.exists(path):
        try:
            with gzip.open(path, "rt", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError, EOFError):
            os.remove(path)
    return None


def cache_write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path + ".part", "wt", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(path + ".part", path)


def cached(path, fetch, reduce=None):
    """Cached JSON: fetch() -> text; reduce(parsed) -> what is stored."""
    d = cache_read(path)
    if d is not None:
        return d
    text = fetch()
    if text is None:
        return None
    try:
        d = json.loads(text)
    except json.JSONDecodeError:
        NET["bad_json"] += 1
        return None
    if reduce:
        d = reduce(d)
    if d is not None:
        cache_write(path, d)
    return d


# ------------------------------------------------------------------ dates

_CENT = re.compile(r"(?i)(early|mid|late|first half of the|second half of the|1st half|2nd half)?[ -]*"
                   r"(\d{1,2})(?:st|nd|rd|th)(?:\s*(?:-|–|to|or)\s*(?:early|mid|late)?[ -]*(\d{1,2})(?:st|nd|rd|th))?"
                   r"\s*(?:century|c\.)\s*(bce|bc|b\.c\.)?")


def parse_date(text):
    """Free-text date -> (begin, end) years, or (None, None)."""
    t = (text or "").replace("–", "-").replace("—", "-")
    if not t.strip():
        return None, None
    bce = bool(re.search(r"(?i)\b(bce|b\.c\.?|bc)\b", t))
    m = _CENT.search(t)
    if m:
        q, c1, c2, mb = m.group(1), int(m.group(2)), m.group(3), m.group(4)
        c2 = int(c2) if c2 else c1
        if mb or (bce and not re.search(r"\d{3,4}", t)):
            return -c1 * 100, -(c2 - 1) * 100
        b, e = (c1 - 1) * 100, c2 * 100 - 1
        if q and not m.group(3):
            ql = q.lower()
            if ql.startswith("early") or "first" in ql or "1st" in ql:
                e = b + 40 if ql.startswith("early") else b + 50
            elif ql.startswith("late") or "second" in ql or "2nd" in ql:
                b = e - 40 if ql.startswith("late") else e - 50
            elif ql.startswith("mid"):
                b, e = b + 30, b + 70
        return b, e
    yrs = [int(y) for y in re.findall(r"(?<!\d)(\d{3,4})(?!\d)", t)]
    if not yrs:
        return None, None
    decade = re.search(r"(\d{3})0s", t)
    if bce:
        yrs = [-y for y in yrs]
    b, e = min(yrs), max(yrs)
    if decade and len(yrs) == 1:
        e = b + 9
    return b, e


def iso_year(s):
    if not s:
        return None
    m = re.match(r"\s*(-?)(\d{1,6})", str(s))
    if not m:
        return None
    y = int(m.group(2))
    return -y if m.group(1) else y


# ------------------------------------------------------------------ lexicons
# extensions to the shared lexicons (specific first; they are prepended)

EXTRA_AFRICA = saa._L([
    (r"bushongo|bushong|bakuba|bangongo|pianga|ngongo", "Kuba"), (r"baluba|kanioka|kaniok", "Luba"),
    (r"bayaka", "Yaka"), (r"mendi", "Mende"), (r"akamba", "Kamba"), (r"agni|anyi", "Akan: Anyi"),
    (r"asalampasu", "Salampasu"), (r"herero|himba", "Herero"),
    (r"bushm[ae]n|san|basarwa|ju.?hoansi|kung", "San"), (r"mbuti|pygmy|twa|aka|baka", "Central African foragers (Mbuti, Aka, Baka)"),
    (r"arbore", "Arbore"), (r"karamojong|karimojong|jie|dodoth", "Karamojong"),
    (r"nandi|kalenjin", "Kalenjin"), (r"mandingo|mandinka", "Malinke"), (r"beti|ewondo|bulu", "Beti"),
    (r"lwena|luvale|luena", "Luvale"), (r"wodaabe|bororo fulani", "Fulani"), (r"ambundu|mbundu", "Mbundu"),
    (r"shangana|shangana-tsonga", "Tsonga"), (r"bamileke", "Cameroon Grassfields: Bamileke"),
    (r"bena lulua", "Lulua"), (r"bwami", "Lega"), (r"kongo-?yombe|yombe", "Kongo"), (r"vili", "Kongo"),
    (r"mitsogo", "Tsogo"), (r"bakota", "Kota"), (r"ogoni", "Ogoni"), (r"kalabari", "Ijo"),
    (r"ibo", "Igbo"), (r"ijebu", "Yoruba"), (r"djenne|jenne", "Inland Niger Delta (Djenne)"),
    (r"turkana", "Turkana"), (r"gikuyu", "Kikuyu"), (r"luo", "Luo"), (r"bemba", "Bemba"), (r"tonga", "Tonga (Zambia)"),
    (r"ndengese|dengese", "Ndengese"), (r"kete", "Kete"), (r"wongo", "Wongo"), (r"tetela", "Tetela"),
    (r"sakalava|mahafaly|merina", "Malagasy"), (r"edo|bini|benin", "Edo (Benin Kingdom)"),
    (r"luguru", "Luguru"), (r"ishan|esan", "Esan"), (r"ngoni", "Ngoni"), (r"hehe", "Hehe"),
    (r"kirdi|mafa|matakam", "Mandara Mountains (Kirdi)"), (r"gurage", "Gurage"), (r"bijago", "Bidjogo"),
])
EXTRA_AFRICA_EXCL_FOR_OCEANIA = set()

EXTRA_OCEANIA = saa._L([
    # Indigenous Australia (schools / regions)
    (r"papunya( tula)?", "Aboriginal Australian: Papunya Tula (Western Desert)"),
    (r"pintupi|warlpiri|walpiri|luritja|anmatyerr|kintore|kiwirrkura|yuendumu|utopia|balgo|western desert|"
     r"pitjantjatjara|ngaanyatjarra|spinifex|martu", "Aboriginal Australian: Western Desert"),
    (r"arrernte|aranda|hermannsburg|namatjira", "Aboriginal Australian: Arrernte (Hermannsburg)"),
    (r"yolngu|yolnu|yolu|yirrkala|galiwinku|elcho island|milingimbi|ramingining|gapuwiyak|gupapuyngu|"
     r"rirratjingu|gumatj|djambarrpuyngu|maymuru|munggurrawuy|narritjin|mawalan|marika|yunupingu",
     "Aboriginal Australian: Yolngu (Northeast Arnhem Land)"),
    (r"kunwinjku|gunwinggu|gunwinjgu|oenpelli|gunbalanya|maningrida|kuninjku|western arnhem", "Aboriginal Australian: Western Arnhem Land"),
    (r"arnhem land", "Aboriginal Australian: Arnhem Land"),
    (r"tiwi|bathurst island|melville island|puruntatameri", "Aboriginal Australian: Tiwi"),
    (r"wardaman|wadaman", "Aboriginal Australian: Wardaman"),
    (r"kimberley|wandjina|warmun|turkey creek|worrorra|ngarinyin|wunambal", "Aboriginal Australian: Kimberley"),
    (r"torres strait( islander)?s?|mer island|mabuiag|badu|saibai|murray island", "Torres Strait"),
    (r"aborigin(al|e|es)|indigenous australian|first australians", "Aboriginal Australian"),
    # Maori iwi (Auckland / Te Papa) -> Maori: <iwi>; Moriori
    (r"moriori|rekohu|chatham islands", "Moriori"),
    (r"te arawa|ngati pikiao|ngati whakaue|tuhourangi|ngati tarawhai|ngati rangiwewehi", "Maori: Te Arawa"),
    (r"ngai tahu|kai tahu|ngaitahu", "Maori: Ngai Tahu"), (r"ngati porou", "Maori: Ngati Porou"),
    (r"tuhoe|ngai tuhoe", "Maori: Tuhoe"), (r"ngapuhi|nga puhi", "Maori: Ngapuhi"),
    (r"tainui|waikato|ngati maniapoto|ngati raukawa", "Maori: Tainui"),
    (r"ngati kahungunu|kahungunu", "Maori: Ngati Kahungunu"), (r"rongowhakaata", "Maori: Rongowhakaata"),
    (r"te ati awa|te atiawa|ngati toa|ngati tuwharetoa|tuwharetoa|whanganui|te aitanga a mahaki|ngati awa|"
     r"ngati ranginui|ngai te rangi|ngati whatua|ngati kuri|te rarawa|te aupouri|te whanau a apanui|"
     r"ngati tama|ngati mutunga|taranaki|ngati ruanui|ngaa rauru|nga rauru|ngati apa|rangitane|muaupoko|"
     r"ngati hine|ngati kuia|ngati rarua|ngati koata|waitaha|ngati mamoe", "Maori: other iwi"),
    # Pacific nationality / culture adjectives missing from the shared list
    (r"niuean", "Niue"), (r"tokelauan", "Tokelau"), (r"tuvaluan", "Tuvalu"), (r"rarotongan", "Cook Islands"),
    (r"solomon islander", "Solomon Islands"), (r"i-?kiribati|gilbertese", "Kiribati"),
    (r"lakalai|nakanai|tolai|baining|sulka|mengen", "New Britain"), (r"yonggom|muyu", "New Guinea: Yonggom"),
    (r"gimi|kukukuku|anga|asaro|chimbu|simbu|melpa|hagen|mount hagen", "New Guinea Highlands"),
    (r"madang|astrolabe bay|bilbil", "New Guinea: Madang"), (r"kerewa|gogodala", "Papuan Gulf"),
    (r"mekeo|motu|hula|aroma", "New Guinea: Central Province (Papuan coast)"),
    (r"humboldt bay|tobati|jayapura", "Lake Sentani"), (r"mimika|kamoro", "New Guinea: Kamoro"),
    (r"santa cruz islands|nendo|reef islands", "Solomon Islands"), (r"loyalty islands", "New Caledonia (Kanak)"),
    (r"wallis|futuna|uvea", "Wallis and Futuna"), (r"rotuma", "Rotuma"),
])
EXTRA_OCEANIA_PERIODS = saa._L([
    (r"te huringa iii|te huringa 3", "Te Huringa III (1950-)"),
    (r"te huringa ii|te huringa 2", "Te Huringa II (1900-1950)"),
    (r"te huringa i|te huringa 1|te huringa", "Te Huringa I (1800-1900)"),
    (r"te puawaitanga", "Te Puawaitanga (1500-1800)"), (r"te tipunga", "Te Tipunga (1200-1500)"),
    (r"nga kakano", "Nga Kakano (900-1200)"), (r"archaic", "Archaic"), (r"lapita", "Lapita"),
    (r"late colonial", "Late Colonial"),
])

_maori_idx = next(i for i, (_, lab) in enumerate(saa.AMERICAS_CULTURES) if lab == "Maori")
_precol_idx = next(i for i, (_, lab) in enumerate(saa.AMERICAS_CULTURES) if lab.startswith("Pre-Columbian"))
OCEANIA_ONLY = saa.AMERICAS_CULTURES[_maori_idx:_precol_idx]
AFRICA_LEX = EXTRA_AFRICA + saa.AFRICA_CULTURES
OCEANIA_LEX = EXTRA_OCEANIA + OCEANIA_ONLY
# make the shared maker test aware of the new culture names ("Herero", "Tiwi" are not makers)
saa.REGION_LEX["africa"] = (AFRICA_LEX, saa.AFRICA_PERIODS)
saa.REGION_LEX["americas_oceania"] = (OCEANIA_LEX + saa.AMERICAS_CULTURES, EXTRA_OCEANIA_PERIODS + saa.AMERICAS_PERIODS)
LEX = {"africa": (AFRICA_LEX, saa.AFRICA_PERIODS), "americas_oceania": (OCEANIA_LEX, EXTRA_OCEANIA_PERIODS)}
GENERIC = saa.GENERIC_CULTURES | {"Aboriginal Australian", "Central African foragers (Mbuti, Aka, Baka)"}


def match_lex(lex, text, minlen=0):
    """First lexicon entry that matches; with minlen, the matched text must be that long
    (descriptions: skip short ambiguous names such as 'Dan', 'Ewe', 'Fon', 'Aka')."""
    for rx, lab in lex:
        m = rx.search(text)
        if m and len(m.group(0)) >= minlen:
            return lab
    return None


def indigenous_evidence(text):
    t = fold(text)
    return bool(match_lex(AFRICA_LEX, t, 4) or match_lex(OCEANIA_LEX, t, 4))


EXCLUDE_CULTURE = re.compile(r"(?<![a-z])(coptic|hebrew|jewish|egypt|egyptian|ancient egyptian|roman|greek|"
                             r"hellenistic|punic|phoenician|carthag\w*|byzantine|ottoman|moorish|moroccan|"
                             r"algerian|tunisian|libyan|north africa|north african|islamic|arab|arabic)(?![a-z])")
LITHIC = re.compile(r"(?<![a-z])(debitage|flakes?|flake tool|cores?|scrapers?|bifaces?|hand ?axes?|handaxes?|"
                    r"choppers?|microliths?|burins?|cleavers?|lithics?|hammerstones?|sherds?|potsherds?|"
                    r"manuports?|chips?|spalls?|cobble tool|retouched|fragment of stone|stone tool)(?![a-z])")
PREHIST = re.compile(r"(?<![a-z])(acheulian|acheulean|mousterian|oldowan|paleolithic|palaeolithic|"
                     r"stone age|levallois|sangoan|lupemban|aterian|still bay|howiesons poort|wilton)(?![a-z])")
# object types that are not visual-art evidence: tools and archaeological implements (Te Papa's
# Taonga Maori holds ~8k adze blades, 4k fishhooks and 1k net sinkers from excavations), and
# non-object media (sound recordings, typography portfolios, ephemera). Carved / pounamu /
# ceremonial pieces and anything with a named maker are kept.
TOOLS = re.compile(r"^(sinkers?|sinkers \(fishing\)|drills?|drill points?|awls?|grindstones?|files|needles?|chisels?|"
                   r"remnants|remains|realia|lures?|fasteners?|abraders?|polishers?|hammers?|tools?|implements?|"
                   r"pestles?|net gauges?|whetstones?|blanks?|preforms?|adzes?|adze blades?|axes \(tools\)|axe heads?|"
                   r"projectile points?|points?|blades?|fishhooks?|fish ?hooks?|fishhook points?|hooks?|gouges?|"
                   r"artifacts|unidentified objects?|fragments?|cutters?|knives \(tools\)|obsidian|cores)$")
TOOL_KEEP = re.compile(r"(?i)pounamu|poutangata|ceremonial|hafted|carved|ornament|hei matau|nephrite|jade")
NONART = re.compile(r"(?<![a-z])(sound recordings?|compact discs?|phonograph records?|audio|video ?recordings?|"
                    r"motion pictures?|films?|dvds?|cassettes?|portfolios?|typefaces?|fonts?|ephemera|documents?|"
                    r"letters \(correspondence\)|certificates?|tickets?|programmes?|programs \(documents\)|posters?|"
                    r"postage stamps?|stamps?|banknotes?|coins?|medals?|badges?|installations \(visual works\)|"
                    r"t-shirts?|specimens?|samples?)(?![a-z])")
ISLAND_SEA = re.compile(r"(?<![a-z])(philippines|luzon|mindanao|visayas|sulu|borneo|sarawak|sabah|kalimantan|"
                        r"sumatra|java|bali|lombok|sulawesi|celebes|flores|sumba|timor|moluccas|maluku|nias|"
                        r"malaysia|malaya|indonesia|bagobo|ifugao|bontoc|kalinga|apayao|igorot|tagalog|moro|"
                        r"iban|dayak|kayan|kenyah|kantu|melanau|minangkabau|minangkebau|lampong|lampung|"
                        r"batak|toraja|javanese|balinese|malay|yakan|tausug|maranao|dou donggo|pipikoro)(?![a-z])")


# ------------------------------------------------------------------ source harvests
# Each harvest returns normalised records:
# {source,id,title,otype,oclass,labels,place,extra,date_text,begin,end,makers[(name,role)],
#  materials,collection,url,sweep,prior,strong,trusted}

def rec(**kw):
    base = {"title": "", "otype": "", "oclass": "", "labels": "", "place": "", "extra": "", "date_text": "",
            "begin": None, "end": None, "makers": [], "materials": "", "collection": "", "url": "", "sweep": "",
            "prior": None, "strong": False, "trusted": False}
    base.update(kw)
    return base


# ---- Mia
MIA_API = "https://search.artsmia.org/"
MIA_QUERIES = ['department:"Arts of Global Africa"', "continent:Africa", "continent:Oceania",
               'department:"Arts of Oceania"']
MIA_KEEP = ["id", "title", "medium", "classification", "object_name", "continent", "country", "nationality",
            "culture", "dated", "artist", "role", "department", "accession_number", "style", "description",
            "text", "creditline", "life_date"]


def harvest_mia():
    cache = os.path.join(RAW, "mia")
    out = {}
    for q in MIA_QUERIES:
        url = MIA_API + urllib.parse.quote(q) + "?size=5000"
        d = cached(os.path.join(cache, slug(q) + ".json.gz"), lambda: http(url),
                   reduce=lambda d: {"total": d["hits"]["total"],
                                     "hits": [{k: (h["_source"].get(k) or "") if k not in ("text", "description")
                                               else re.sub(r"<[^>]+>", " ", str(h["_source"].get(k) or ""))[:400]
                                               for k in MIA_KEEP} for h in d["hits"]["hits"]]})
        if not d:
            print(f"  Mia {q}: failed", file=sys.stderr)
            continue
        n0 = len(out)
        for h in d["hits"]:
            out.setdefault(h["id"], (h, q))
        print(f"  Mia {q}: {len(d['hits'])} hits ({len(out) - n0} new)", file=sys.stderr)
    recs = []
    for h, q in out.values():
        dept = h.get("department", "")
        cont = h.get("continent", "")
        prior = "africa" if cont == "Africa" or dept == "Arts of Global Africa" else \
            "americas_oceania" if cont == "Oceania" or dept == "Arts of Oceania" else None
        makers = []
        for part in re.split(r";\s*", h.get("artist") or ""):
            part = re.sub(r"^(Artist|Maker|Designer|Producer|Carver|Weaver|Sculptor)\s*:\s*", "", part.strip(), flags=re.I)
            part = re.sub(r"^or\s+", "", part)
            if part:
                makers.append((part, h.get("role") or ""))
        b, e = parse_date(h.get("dated"))
        recs.append(rec(source="mia", id=str(h["id"]), title=h.get("title", ""), otype=h.get("object_name", ""),
                        oclass=h.get("classification", ""),
                        labels="; ".join(x for x in (h.get("culture"), h.get("artist"), h.get("nationality"),
                                                     h.get("style")) if x),
                        place="; ".join(x for x in (h.get("country"), cont) if x),
                        extra=(h.get("description") or "") + " " + (h.get("text") or ""),
                        date_text=h.get("dated", ""), begin=b, end=e, makers=makers, materials=h.get("medium", ""),
                        collection=dept, url=f"https://collections.artsmia.org/art/{h['id']}", sweep="q:" + q,
                        prior=prior, strong=dept in ("Arts of Global Africa", "Arts of Oceania"),
                        trusted=dept in ("Arts of Global Africa", "Arts of Oceania")))
    print(f"  Mia: {len(recs)} records", file=sys.stderr)
    return recs


# ---- Penn
PENN_CSV = "https://collections.penn.museum/collections/assets/data/Penn_Museum_Collections_Data.csv"
PENN_SECTIONS = {"African": "africa", "Oceanian": "americas_oceania"}


def penn_download(path):
    if os.path.exists(path):
        return True
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for attempt in range(4):
        try:
            req = urllib.request.Request(PENN_CSV, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=600) as r, open(path + ".part", "wb") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
            os.replace(path + ".part", path)
            return True
        except Exception as e:
            print(f"  Penn download: {type(e).__name__}: {e} (retry {attempt + 1})", file=sys.stderr)
            time.sleep(30 * (attempt + 1))
    return False


def harvest_penn():
    path = os.path.join(RAW, "penn", "Penn_Museum_Collections_Data.csv")
    if not penn_download(path):
        print("  Penn: download failed", file=sys.stderr)
        return []
    csv.field_size_limit(1 << 30)
    recs = []
    with open(path, encoding="utf-8", errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            region = PENN_SECTIONS.get(row.get("curatorialSection") or "")
            if not region:
                continue
            b, e = saa.to_int(row.get("earlyDate")), saa.to_int(row.get("lateDate"))
            if b is None and e is None:
                b, e = parse_date(row.get("dateMade"))
            makers = [(m.strip(), "") for m in re.split(r",\s*", row.get("creator") or "") if m.strip()]
            recs.append(rec(source="penn", id=row["identifier"], title=row.get("title") or row.get("objectName") or "",
                            otype=row.get("objectName", ""), oclass=row.get("nativeName", ""),
                            labels="; ".join(x for x in (row.get("culture"), row.get("cultureArea"),
                                                         row.get("period")) if x),
                            place="; ".join(x for x in (row.get("placeName"), row.get("siteName")) if x),
                            extra=(row.get("description") or "")[:500], date_text=row.get("dateMade") or "",
                            begin=b, end=e, makers=makers,
                            materials="; ".join(x for x in (row.get("material"), row.get("technique")) if x),
                            collection=row.get("curatorialSection", ""), url=row.get("Record URL", ""),
                            sweep="section:" + row.get("curatorialSection", ""), prior=region, strong=True,
                            trusted=True))
    print(f"  Penn: {len(recs)} records in the African and Oceanian sections", file=sys.stderr)
    return recs


# ---- Te Papa
TEPAPA_API = "https://data.tepapa.govt.nz/collection/search"
TEPAPA_COLLECTIONS = ["PacificCultures", "TaongaMāori"]
TEPAPA_PAGE = 500
_tok = [None, 0.0]


def tepapa_token(force=False):
    if _tok[0] and not force and time.time() - _tok[1] < 600:
        return _tok[0]
    req = urllib.request.Request(TEPAPA_API, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=60)
    except urllib.error.HTTPError as e:
        try:
            _tok[0] = json.loads(e.read().decode("utf-8"))["guestToken"]
            _tok[1] = time.time()
        except (ValueError, KeyError):
            pass
    return _tok[0]


def tepapa_reduce(d):
    out = []
    for r in d.get("results") or []:
        prods = []
        for p in r.get("production") or []:
            c = p.get("contributor") or {}
            sp = p.get("spatial") or {}
            role = p.get("role")
            prods.append({"maker": c.get("title", "") if isinstance(c, dict) else "",
                          "role": role.get("title", "") if isinstance(role, dict) else (role or ""),
                          "place": sp.get("title", "") if isinstance(sp, dict) else "",
                          "nation": "; ".join(sp.get("nation") or []) if isinstance(sp, dict) else "",
                          "date": p.get("verbatimCreatedDate") or "",
                          "created": p.get("createdDate") or "",
                          "title": p.get("title", "")})
        out.append({"id": r.get("id"), "identifier": r.get("identifier", ""), "title": r.get("title", ""),
                    "collection": r.get("collection", ""), "prod": prods,
                    "types": [c.get("title", "") for c in r.get("isTypeOf") or [] if isinstance(c, dict)],
                    "infl": [c.get("title", "") for c in r.get("influencedBy") or [] if isinstance(c, dict)],
                    "mats": r.get("isMadeOfSummary") or "; ".join(c.get("title", "") for c in r.get("isMadeOf") or []
                                                                   if isinstance(c, dict)),
                    "tech": [c.get("title", "") for c in r.get("productionUsedTechnique") or [] if isinstance(c, dict)],
                    "credit": r.get("creditLine", "")})
    return {"count": ((d.get("_metadata") or {}).get("resultset") or {}).get("count"), "results": out}


def tepapa_page(coll, frm):
    body = json.dumps({"query": "*", "filters": [{"field": "collection", "keyword": coll},
                                                 {"field": "type", "keyword": "Object"}],
                       "size": TEPAPA_PAGE, "from": frm, "sort": [{"field": "id", "order": "asc"}]}).encode()

    def fetch():
        for _ in range(3):
            try:
                return http(TEPAPA_API, data=body, headers={"Authorization": "Bearer " + (tepapa_token() or ""),
                                                            "Content-Type": "application/json"})
            except urllib.error.HTTPError as e:
                if e.code == 401:
                    tepapa_token(force=True)
                    continue
                raise
        return None
    return cached(os.path.join(RAW, "tepapa", f"{slug(coll)}_{frm:06d}.json.gz"), fetch, reduce=tepapa_reduce)


def harvest_tepapa():
    recs = []
    for coll in TEPAPA_COLLECTIONS:
        frm, total, n = 0, None, 0
        while total is None or frm < total:
            d = tepapa_page(coll, frm)
            if not d:
                print(f"  Te Papa {coll} from {frm}: failed", file=sys.stderr)
                break
            total = d.get("count") or 0
            for r in d["results"]:
                n += 1
                makers = [(p["maker"], p["role"]) for p in r["prod"] if p["maker"]]
                dtext = "; ".join(p["date"] for p in r["prod"] if p["date"])
                b, e = parse_date(dtext)
                if b is None:
                    ys = [iso_year(p["created"]) for p in r["prod"] if p["created"]]
                    ys = [y for y in ys if y is not None]
                    if ys:
                        b, e = min(ys), max(ys)
                infl = [x.replace(" [attributed]", "") for x in r["infl"]]
                place = "; ".join(x for p in r["prod"] for x in (p["place"], p["nation"]) if x)
                if coll == "TaongaMāori":
                    place = (place + "; New Zealand") if place else "New Zealand"
                    if not any(re.search(r"(?i)m[aā]ori|moriori", x) for x in infl):
                        infl.append("Māori")
                recs.append(rec(source="tepapa", id=str(r["id"]), title=r["title"],
                                otype="; ".join(r["types"][:3]), oclass="; ".join(r["tech"][:3]),
                                labels="; ".join(infl), place=place, extra="", date_text=dtext[:80],
                                begin=b, end=e, makers=makers, materials=r["mats"], collection=coll,
                                url=f"https://collections.tepapa.govt.nz/object/{r['id']}", sweep="collection:" + coll,
                                prior="americas_oceania", strong=True, trusted=True))
            if not d["results"]:
                break
            frm += TEPAPA_PAGE
        print(f"  Te Papa {coll}: {n} of {total} objects", file=sys.stderr)
    return recs


# ---- Auckland
# The endpoint sits behind a web-application firewall that answers SQL-looking
# queries with a bot challenge: ORDER BY, UNION, "||" and GROUP_CONCAT separators
# are all refused, as are some PREFIX declarations (so names are expanded to full IRIs).
# So: plain id lists per department, then one simple query per field over batches of
# ids (VALUES), POSTed a few seconds apart.
AUCK_SPARQL = "https://api.aucklandmuseum.com/sparql"
AUCK_BATCH = 800
AUCK_DELAY = 3.0
AUCK_PREFIX = ("PREFIX ecrm: <http://erlangen-crm.org/current/> "
               "PREFIX am: <http://collections.aucklandmuseum.com/ontology/core/> "
               "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> "
               "PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX foaf: <http://xmlns.com/foaf/0.1/> ")
AUCK_KEEPERS = ["Pacific", "World", "Ethnology", "Māori"]
AUCK_OBJ = "http://api.aucklandmuseum.com/id/humanhistory/object/"
AUCK_FIELDS = {
    "base": ("SELECT ?s ?title ?acc ?keeper ?desc WHERE { %s OPTIONAL { ?s dc:title ?title } "
             "OPTIONAL { ?s am:accessionNumber ?acc } OPTIONAL { ?s ecrm:P50_has_current_keeper/rdf:value ?keeper } "
             "OPTIONAL { ?s dc:description ?desc } }"),
    "cult": "SELECT ?s ?cult WHERE { %s ?s am:culturalOrigin ?cult }",
    "cls": "SELECT ?s ?cls WHERE { %s ?s am:classification/rdf:value ?cls }",
    "place": ("SELECT ?s ?place ?parent WHERE { %s ?s ecrm:P108i_was_produced_by/ecrm:P7_took_place_at ?pn . "
              "?pn dc:title ?place . OPTIONAL { ?pn am:childOf/dc:title ?parent } }"),
    "time": ("SELECT ?s ?dnote ?begin ?end WHERE { %s ?s ecrm:P108i_was_produced_by/ecrm:P4_has_time_span ?ts . "
             "OPTIONAL { ?ts ecrm:P3_has_note ?dnote } OPTIONAL { ?ts ecrm:P82a_begin_of_the_begin ?begin } "
             "OPTIONAL { ?ts ecrm:P82b_end_of_the_end ?end } }"),
    "maker": ("SELECT ?s ?maker ?role WHERE { %s ?s ecrm:P108i_was_produced_by/am:productionPersonAssociation ?pa . "
              "?pa ecrm:P14_carried_out_by/foaf:name ?maker . OPTIONAL { ?pa am:primaryProductionRole ?role } }"),
}
MAORI_ORIGIN = re.compile(r"(?i)m[aā]ori|moriori|iwi hapu")


def auck_expand(q):
    """Prefixed names -> full IRIs, with no PREFIX block (the firewall challenges some PREFIX lines)."""
    ns = dict(re.findall(r"PREFIX (\w+): <([^>]+)>", AUCK_PREFIX))
    return re.sub(r"(?<![\w<\"])(%s):([A-Za-z_][\w.-]*\w)" % "|".join(ns),
                  lambda m: f"<{ns[m.group(1)]}{m.group(2)}>", q)


def auck_query(q, path):
    def fetch():
        saved = DELAY[0]
        DELAY[0] = max(DELAY[0], AUCK_DELAY)
        try:
            return http(AUCK_SPARQL, data=urllib.parse.urlencode({"query": auck_expand(q)}).encode(),
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                        accept="application/sparql-results+json", timeout=300)
        finally:
            DELAY[0] = saved
    return cached(path, fetch, reduce=lambda d: [{k: v.get("value", "") for k, v in b.items()}
                                                  for b in d["results"]["bindings"]])


def harvest_auckland():
    cache = os.path.join(RAW, "auckland")
    slice_of = collections.OrderedDict()
    for k in AUCK_KEEPERS:
        ids = auck_query('SELECT ?s WHERE { ?s ecrm:P50_has_current_keeper/rdf:value "%s" }' % k,
                         os.path.join(cache, f"ids_keeper_{slug(k)}.json.gz")) or []
        for b in ids:
            slice_of.setdefault(b["s"], "keeper:" + k)
        print(f"  Auckland keeper {k}: {len(ids)} objects", file=sys.stderr)
    origins = auck_query("SELECT ?s ?co WHERE { ?s am:culturalOrigin ?co }",
                         os.path.join(cache, "ids_cultural_origin.json.gz")) or []
    n = 0
    for b in origins:
        if MAORI_ORIGIN.search(b.get("co", "")) and b["s"] not in slice_of:
            slice_of[b["s"]] = "culture:Maori"
            n += 1
    print(f"  Auckland Maori/Moriori/iwi cultural origin outside those departments: {n}", file=sys.stderr)
    ids = [s for s in slice_of if s.startswith(AUCK_OBJ)]
    vals = collections.defaultdict(lambda: collections.defaultdict(list))
    for i in range(0, len(ids), AUCK_BATCH):
        batch = ids[i:i + AUCK_BATCH]
        v = "VALUES ?s { " + " ".join(f"<{s}>" for s in batch) + " }"
        for field, q in AUCK_FIELDS.items():
            res = auck_query(q % v, os.path.join(cache, "fields", f"{field}_{i:06d}_{len(batch)}.json.gz"))
            if res is None:
                print(f"  Auckland {field} batch {i}: failed", file=sys.stderr)
                continue
            for b in res:
                for k2, x in b.items():
                    if k2 != "s" and x and x not in vals[b["s"]][k2]:
                        vals[b["s"]][k2].append(x)
        if (i // AUCK_BATCH) % 10 == 0:
            print(f"  Auckland: {i + len(batch)}/{len(ids)} objects read", file=sys.stderr)
    recs = []
    for s in ids:
        o = vals.get(s, {})
        sl = slice_of[s]
        cults = [c for c in o.get("cult", []) if c.lower() != "unknown"]
        labels = "; ".join(c.replace("/", " / ") for c in cults)
        if any("Iwi Hapu" in c for c in cults) and not re.search(r"(?i)m[aā]ori", labels):
            labels += "; Māori"
        makers = []
        mk, roles = o.get("maker", []), o.get("role", [])
        for j, nm in enumerate(mk):
            if nm.strip() and nm.strip().lower() != "unknown":
                makers.append((nm.strip(), roles[j] if j < len(roles) and len(mk) == len(roles) else
                               (roles[0] if len(roles) == 1 else "")))
        dnote = "; ".join(x for x in o.get("dnote", []) if x.lower() != "unknown")
        bs = [iso_year(x) for x in o.get("begin", [])]
        es = [iso_year(x) for x in o.get("end", [])]
        bs, es = [x for x in bs if x is not None], [x for x in es if x is not None]
        b, e = (min(bs) if bs else None), (max(es) if es else None)
        if b is None and e is None:
            b, e = parse_date(dnote)
        places = [p.strip("[]") for p in o.get("place", []) + o.get("parent", [])]
        keeper = (o.get("keeper") or [""])[0]
        trusted = keeper in ("Pacific", "Māori") or sl == "culture:Maori"
        oid = s.rsplit("/", 1)[-1]
        recs.append(rec(source="auckland", id=oid, title=(o.get("title") or [""])[0],
                        otype=(o.get("cls") or [""])[0], oclass="", labels=labels, place="; ".join(places),
                        extra=" ".join(o.get("desc", []))[:500], date_text=dnote[:80], begin=b, end=e,
                        makers=makers, materials="", collection=keeper,
                        url=f"https://www.aucklandmuseum.com/collection/object/am_humanhistory-object-{oid}",
                        sweep=sl, prior="americas_oceania" if trusted else None, strong=trusted, trusted=trusted))
    print(f"  Auckland: {len(recs)} records", file=sys.stderr)
    return recs


# ---- Yale LUX
LUX = "https://lux.collections.yale.edu"
YUAG_AFRICA = LUX + "/data/set/68a04911-0631-4924-94f2-4d32838d6d2a"
PEABODY_ANTH = LUX + "/data/set/00db6d99-fc28-4e41-b5b1-aa619f75e59a"
OCEANIA_TERMS = ["Oceania", "Polynesia", "Melanesia", "Micronesia", "New Guinea", "Papua", "Australia",
                 "Aboriginal", "Maori", "New Zealand", "Hawaii", "Fiji", "Samoa", "Tonga", "Solomon Islands",
                 "Vanuatu", "New Hebrides", "New Caledonia", "Marquesas", "Tahiti", "Admiralty Islands",
                 "New Ireland", "New Britain", "Bismarck Archipelago", "Torres Strait", "Sepik", "Asmat",
                 "Caroline Islands", "Marshall Islands", "Kiribati", "Cook Islands", "Easter Island"]
LUX_QUERIES = {
    "yuag_african_art": ({"memberOf": {"id": YUAG_AFRICA}}, "africa", True),
    "yuag_indo_pacific": ({"memberOf": {"name": "Indo-Pacific"}}, None, False),
    "peabody_africa": ({"AND": [{"memberOf": {"id": PEABODY_ANTH}},
                                {"OR": [{"text": "Africa"}, {"text": "African"}]}]}, "africa", False),
    "peabody_oceania": ({"AND": [{"memberOf": {"id": PEABODY_ANTH}},
                                 {"OR": [{"text": t} for t in OCEANIA_TERMS]}]}, "americas_oceania", False),
}


def lux_ids(name, q):
    ids, page = [], 1
    while True:
        url = f"{LUX}/api/search/item?" + urllib.parse.urlencode({"q": json.dumps(q), "page": page, "pageLength": 100})
        d = cached(os.path.join(RAW, "yale", "search", f"{name}_{page:04d}.json.gz"), lambda: http(url),
                   reduce=lambda d: {"ids": [i["id"] for i in d.get("orderedItems") or []],
                                     "next": bool(d.get("next")),
                                     "total": (d.get("partOf") or [{}])[0].get("totalItems")
                                     if isinstance(d.get("partOf"), list) else None})
        if not d:
            break
        ids += d["ids"]
        if not d["next"] or not d["ids"]:
            break
        page += 1
    return ids


def _labels(objs):
    return [o.get("_label", "") for o in objs or [] if isinstance(o, dict) and o.get("_label")]


def lux_reduce(d):
    prod = d.get("produced_by") or {}
    parts = [prod] + [p for p in prod.get("part") or [] if isinstance(p, dict)]
    ts = prod.get("timespan") or {}
    makers, places, pnotes, influ = [], [], [], []
    for p in parts:
        role = "; ".join(_labels(p.get("classified_as")))
        for a in p.get("carried_out_by") or []:
            if isinstance(a, dict):
                makers.append([a.get("_label", ""), role, a.get("type", "")])
        places += _labels(p.get("took_place_at"))
        influ += _labels(p.get("influenced_by"))
        for r in p.get("referred_to_by") or []:
            if isinstance(r, dict) and r.get("content"):
                pnotes.append([", ".join(_labels(r.get("classified_as"))), r["content"][:300]])
    notes = []
    for r in d.get("referred_to_by") or []:
        if isinstance(r, dict) and r.get("content"):
            cl = ", ".join(_labels(r.get("classified_as")))
            if re.search(r"(?i)access statement|visitors|rights|credit|copyright|plan your visit", cl):
                continue
            notes.append([cl, r["content"][:400]])
    ids = []
    for i in d.get("identified_by") or []:
        if isinstance(i, dict) and i.get("type") == "Identifier":
            ids.append([", ".join(_labels(i.get("classified_as"))), i.get("content", "")])
    web = ""
    for s in d.get("subject_of") or []:
        for c in (s.get("digitally_carried_by") or []) if isinstance(s, dict) else []:
            for ap in c.get("access_point") or []:
                if "artgallery.yale.edu" in ap.get("id", "") or "peabody" in ap.get("id", ""):
                    web = web or ap["id"]
    enc = []
    for e in d.get("encountered_by") or []:
        if isinstance(e, dict):
            enc += _labels(e.get("took_place_at"))
    return {"id": d.get("id", ""), "label": d.get("_label", ""), "classes": _labels(d.get("classified_as")),
            "mats": _labels(d.get("made_of")), "members": _labels(d.get("member_of")),
            "owner": _labels(d.get("current_owner")),
            "date_text": next((i.get("content", "") for i in ts.get("identified_by") or [] if isinstance(i, dict)), ""),
            "begin": ts.get("begin_of_the_begin"), "end": ts.get("end_of_the_end"),
            "makers": makers, "places": places, "pnotes": pnotes, "influ": influ, "notes": notes[:12],
            "ids": ids, "web": web, "enc": enc}


def harvest_yale(max_items):
    plan = collections.OrderedDict()
    for name, (q, prior, trusted) in LUX_QUERIES.items():
        ids = lux_ids(name, q)
        print(f"  Yale LUX {name}: {len(ids)} ids", file=sys.stderr)
        for i in ids:
            plan.setdefault(i, (name, prior, trusted))
    items = list(plan.items())[:max_items or None]

    def item(oid):
        uuid = oid.rsplit("/", 1)[-1]
        return cached(os.path.join(RAW, "yale", "items", uuid[:2], uuid + ".json.gz"), lambda: http(oid),
                      reduce=lux_reduce)
    # LUX answers in ~0.3-1 s, so a few workers keep the rate near DELAY without exceeding it
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        got = []
        for n, r in enumerate(ex.map(item, [oid for oid, _ in items])):
            got.append(r)
            if n and n % 1000 == 0:
                print(f"  Yale LUX: {n}/{len(items)} items read", file=sys.stderr)
    recs = []
    for (oid, (name, prior, trusted)), r in zip(items, got):
        uuid = oid.rsplit("/", 1)[-1]
        if not r:
            continue
        culture = [c for cl, c in r["notes"] + r["pnotes"] if re.search(r"(?i)culture|people|ethnic", cl)]
        placen = [c for cl, c in r["pnotes"] + r["notes"] if re.search(r"(?i)place", cl)]
        creator = [c for cl, c in r["pnotes"] if re.search(r"(?i)creator", cl)]
        period = [c for cl, c in r["notes"] if re.search(r"(?i)^period", cl)]
        medium = [c for cl, c in r["notes"] if re.search(r"(?i)^medium", cl)]
        makers = []
        for nm, role, typ in r["makers"]:
            nm = re.sub(r"^[A-Za-z ]{2,30}:\s*", "", nm)       # "Artist: Maku of Erin (died 1915)"
            nm = re.sub(r"\s*\((?:[^()]*\d[^()]*|active[^()]*|died[^()]*|born[^()]*)\)\s*$", "", nm).strip()
            if typ == "Group" and not re.search(r"(?i)workshop|atelier|studio", nm):
                culture.append(nm)    # culture groups recorded as the producing group
                continue
            if nm:
                makers.append((nm, role))
        acc = next((c for cl, c in r["ids"] if "Accession" in cl), "") or next((c for _, c in r["ids"]), "")
        desc = " ".join(c for cl, c in r["notes"] if re.search(r"(?i)description|label|note|summary", cl)
                        and not re.search(r"(?i)culture|provenance|exhibition|bibliograph|citation", cl))
        b, e = iso_year(r["begin"]), iso_year(r["end"])
        if b is None and e is None:
            b, e = parse_date(r["date_text"])
        title = re.sub(r"\s*\[.*$", "", r["label"]) if name.startswith("peabody") else r["label"]
        recs.append(rec(source="yale", id=acc or uuid, title=title, otype="; ".join(r["classes"][:4]),
                        oclass="", labels="; ".join(culture + creator + period),
                        place="; ".join(placen + r["places"]),
                        extra=(r["label"] + " " + desc)[:500], date_text=r["date_text"], begin=b, end=e,
                        makers=makers, materials="; ".join(medium[:1] + r["mats"][:6]),
                        collection="; ".join(m for m in r["members"] if "Yale" in m)[:120],
                        url=r["web"] or oid.replace("/data/", "/view/"), sweep="lux:" + name,
                        prior=prior, strong=name == "yuag_african_art", trusted=trusted))
    print(f"  Yale LUX: {len(recs)} records", file=sys.stderr)
    return recs


# ------------------------------------------------------------------ rows

DROPPED = collections.Counter()
SETTLER_OCEANIA = {"australia", "new zealand", "aotearoa", "hawaii", "hawaiian islands", "western australia",
                   "queensland", "northern territory"}


def drop(source, why):
    DROPPED[(source, why)] += 1
    return None


def decide_region(r):
    src = r["source"]
    pt, lt, et = r["place"], r["labels"], r["extra"]
    allt = fold(" ".join((pt, lt, r["title"])))
    if EXCLUDE_CULTURE.search(fold(lt)) or (excluded_place(pt) if pt else False):
        return drop(src, "Egypt / North Africa / Mediterranean / Islamic (other jobs)")
    pm = place_match(pt) or place_match(lt)
    if pm is None and not r["strong"]:
        pm = place_match(r["title"]) or (place_match(et) if et else None)
    if (pm and pm[0] == "south_southeast_asia") or (r["prior"] != "africa" and ISLAND_SEA.search(allt)):
        return drop(src, "Island / mainland Southeast Asia (south_southeast_asia sweep)")
    if pm is None:
        if not r["strong"] or not r["prior"]:
            return drop(src, "no Africa / Oceania place or culture")
        region = r["prior"]
    else:
        region = pm[0]
        if region == "americas_oceania" and pm[1] != "Oceania":
            if r["prior"] == "americas_oceania" and r["strong"] and match_lex(OCEANIA_LEX, fold(lt), 4):
                pm = None    # a Pacific culture with a stray Americas place word
            else:
                return drop(src, "Americas (out of scope: NMAI / earlier sweep)")
        if r["prior"] and region != r["prior"] and not r["strong"]:
            return drop(src, "place outside the query's region")
        if r["prior"] and region != r["prior"] and r["strong"]:
            region = r["prior"] if not place_match(pt) else region
    if region not in ("africa", "americas_oceania"):
        return drop(src, "no Africa / Oceania place or culture")
    if not r["trusted"]:
        settler = pm and (fold(pm[2]) in saa.SETTLER or fold(pm[2]) in SETTLER_OCEANIA)
        if settler and not indigenous_evidence(lt + " " + r["title"] + " " + et):
            return drop(src, "settler-country record without Indigenous culture term")
    return region, pm


def classify(row, labels, place, extra):
    lex_c, lex_p = LEX[row["region"]]
    lt, pt, et = fold(labels), fold(place), fold(extra)
    culture, src = match_lex(lex_c, lt), "label"
    if not culture:
        culture, src = match_lex(lex_c, pt), "place"
    if not culture:
        culture, src = match_lex(lex_c, fold(row["title"]), 4), "title"
    if not culture:
        culture, src = match_lex(lex_c, et, 5), "description"
    if culture and culture.startswith("Maori: other iwi"):
        culture = "Maori: other iwi"
    if not culture:
        pm = row["_pm"]
        culture = f"Unspecified ({saa.FALLBACK_NAME.get(pm[2], pm[2].title())})" if pm else \
            ("Unspecified (Africa)" if row["region"] == "africa" else "Unspecified (Oceania)")
        src = "fallback"
    elif culture in GENERIC:
        src += " (generic)"
    period = match_lex(lex_p, fold(labels + " " + row["date_text"]))
    psrc = "recorded" if period else ""
    if not period:
        period = match_lex(lex_p, et, 5)
        psrc = "description" if period else ""
    if not period:
        period = century_label(row["date_begin"], row["date_end"])
        psrc = "century" if period else ""
    row.update(culture=culture, culture_group=culture.split(":")[0].strip(), culture_source=src,
               period=period, period_source=psrc, overlap="")


DIRECTIONS = re.compile(r"(?<![a-z])(northern|southern|eastern|western|central|north|south|east|west|coastal|"
                        r"upper|lower|island|islands|region|province|probably|possibly)(?![a-z])")
WESTERN_FIRM = re.compile(r"(?i)\b(inc\.?|ltd\.?|llc|corporation|new york|london|paris|and company|& co\.?|"
                          r"entertainment|records)\b")


def not_maker(name):
    """Place names, culture names and placeholders that sources put in the maker field
    ("Democratic Republic of the Congo", "Papua New Guinea, (Trobriand Islands)", "Luguru",
    "Fulani artist made for Tuareg", "France (uncertain)")."""
    f = fold(name)
    if not f or saa._EXCL_RE.search(f) or re.search(r"(?i)\(uncertain\)|^unknown|^various|^not recorded|^unidentified",
                                                    name):
        return True
    if re.search(r"(?i)\bartists?\b|\bpeoples?\b|\bculture\b|\btribe\b", name) and \
            match_lex(OCEANIA_LEX + AFRICA_LEX, f):
        return True
    core = fold(re.sub(r"\(.*?\)", " ", name))
    pm = place_match(core)
    if pm:
        rest = DIRECTIONS.sub(" ", core.replace(fold(pm[2]), " "))
        if not re.sub(r"[^a-z]", "", rest):
            return True
    return bool(match_lex(OCEANIA_LEX + AFRICA_LEX, f) and len(f.split()) <= 2 and not re.search(r"(?i) of ", name))


def make_row(r):
    src = r["source"]
    d = decide_region(r)
    if d is None:
        return None
    region, pm = d
    b, e = r["begin"], r["end"]
    b = b if b is None or -12000 < b < 2100 else None
    e = e if e is None or -12000 < e < 2100 else None
    if b is not None and e is not None and b > e:
        b, e = e, b
    if b is not None and b >= 1960:
        return drop(src, "made 1960 or later")
    ftitle = fold(" ".join((r["title"], r["otype"])))
    if LITHIC.search(fold(r["otype"] or r["title"])) or (PREHIST.search(fold(r["labels"] + " " + r["date_text"]))
                                                         and re.search(r"(?i)stone|flint|chert|quartz|obsidian",
                                                                       r["materials"] + " " + ftitle)):
        return drop(src, "prehistoric lithic / debitage / sherd")
    otype1 = fold(re.split(r";", r["otype"] or "")[0]).strip()
    if NONART.search(otype1):
        return drop(src, "non-object media (recordings, typography, ephemera, installations)")
    if TOOLS.match(otype1) and not TOOL_KEEP.search(r["title"] + " " + r["otype"] + " " + r["materials"]) \
            and not any(n and not not_maker(n) for n, _ in r["makers"]):
        return drop(src, "utilitarian tool / archaeological implement")
    named, western = [], []
    for n, role in r["makers"]:
        if not n or not_maker(n) or not is_named(n, region):
            continue
        western.append(bool(saa.WESTERN.search(n) or saa.WESTERN_TITLES.search(n) or WESTERN_FIRM.search(n)))
        nm = clean_maker(re.sub(r"(?i)^design invented by\s+|\s+from (the )?village of .*$|\s+\((died|born|active)[^)]*\)$",
                                "", n.strip()))
        if nm and (nm, role) not in [(a, b_) for a, b_, _ in named]:
            named.append((nm, role, maker_kind(n)))
    row = {"source": src, "id": r["id"], "region": region,
           "subregion": pm[1] if pm else ("Oceania" if region == "americas_oceania" else "Africa (unspecified)"),
           "place": pm[2].title() if pm else "", "_pm": pm, "title": tidy(r["title"])[:200],
           "object_type": tidy(r["otype"])[:80],
           "object_group": object_group(r["otype"], r["oclass"], r["title"], r["materials"]),
           "labels": tidy(r["labels"])[:300], "date_text": tidy(r["date_text"])[:80], "date_begin": b, "date_end": e,
           "makers": named, "attributed": bool(named), "materials": tidy(r["materials"])[:200],
           "institution": SOURCE_INST[src], "collection": r["collection"], "url": r["url"], "sweep": r["sweep"]}
    if row["object_group"] == "photograph":
        return drop(src, "photograph")
    if named and all(western):
        return drop(src, "made by a Western artist")
    if region == "americas_oceania" and row["subregion"] != "Oceania":
        row["subregion"] = "Oceania"
    classify(row, r["labels"], r["place"], r["extra"])
    return row


# ------------------------------------------------------------------ outputs

def write_tables(rows):
    rows.sort(key=lambda r: (r["region"], r["culture"], r["period"], r["source"], r["date_begin"] or 0))
    ocols = ["source", "id", "title", "region", "subregion", "place", "culture", "culture_group", "culture_source",
             "period", "period_source", "object_group", "object_type", "labels_recorded", "date_text",
             "date_begin", "date_end", "makers", "attributed", "materials", "institution", "collection",
             "overlap", "sweep", "url"]
    write_csv(os.path.join(OUT_DIR, f"{PREFIX}_objects.csv"), ocols, [[
        r["source"], r["id"], r["title"], r["region"], r["subregion"], r["place"], r["culture"], r["culture_group"],
        r["culture_source"], r["period"], r["period_source"], r["object_group"], r["object_type"], r["labels"],
        r["date_text"], "" if r["date_begin"] is None else r["date_begin"],
        "" if r["date_end"] is None else r["date_end"],
        "; ".join(f"{n} ({role})" if role else n for n, role, _ in r["makers"]), int(r["attributed"]),
        r["materials"], r["institution"], r["collection"], r["overlap"], r["sweep"], r["url"]] for r in rows])

    def blank():
        return {"src": collections.Counter(), "att": 0, "begins": [], "ends": [], "mids": [],
                "types": collections.Counter(), "raw": collections.Counter(), "makers": collections.Counter(),
                "subs": collections.Counter(), "periods": collections.Counter(), "cultures": collections.Counter(),
                "csrc": collections.Counter(), "ex": []}
    agg = collections.defaultdict(blank)
    for r in rows:
        reg = r["region"]
        keys = [("culture", reg, r["culture"], "", ""), ("culture_type", reg, r["culture"], "", r["object_group"])]
        if r["culture_group"] != r["culture"]:
            keys.append(("culture_group", reg, r["culture_group"], "", ""))
        if r["period"]:
            keys += [("culture_period", reg, r["culture"], r["period"], ""),
                     ("culture_period_type", reg, r["culture"], r["period"], r["object_group"]),
                     ("period", reg, "", r["period"], "")]
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
            if len(a["ex"]) < 4:
                a["ex"].append(f"{r['source']}:{r['id']}")
    tcols = ["kind", "region", "key", "culture", "culture_group", "period", "object_group", "objects"] + \
            [f"objects_{s}" for s in SOURCES] + \
            ["n_sources", "attributed", "attributed_share", "date_begin_min", "date_end_max", "mid_p10",
             "mid_median", "mid_p90", "top_object_groups", "top_periods", "top_cultures", "subregions",
             "culture_from", "named_makers", "raw_labels", "overlap", "example_ids"]
    order = {"culture_group": 0, "culture": 1, "culture_period": 2, "culture_type": 3, "culture_period_type": 4,
             "period": 5}
    trows = []
    for (kind, reg, cult, per, typ), a in sorted(agg.items(), key=lambda kv: (kv[0][1], order[kv[0][0]],
                                                                              -sum(kv[1]["src"].values()))):
        n = sum(a["src"].values())
        mids = sorted(a["mids"])
        key = " | ".join(fold(x) for x in (cult, per, typ) if x)
        trows.append([kind, reg, key, cult, cult.split(":")[0].strip() if cult else "", per, typ, n] +
                     [a["src"][s] for s in SOURCES] +
                     [sum(1 for s in SOURCES if a["src"][s]), a["att"], round(a["att"] / n, 3),
                      min(a["begins"]) if a["begins"] else "", max(a["ends"]) if a["ends"] else "",
                      _q(mids, 0.1), round(statistics.median(mids)) if mids else "", _q(mids, 0.9),
                      top(a["types"]), top(a["periods"]) if kind in ("culture", "culture_group", "culture_type") else "",
                      top(a["cultures"]) if kind in ("period", "culture_group") else "",
                      top(a["subs"], 3), top(a["csrc"], 4), top(a["makers"], 8), top(a["raw"], 3), "",
                      " ".join(a["ex"])])
    write_csv(os.path.join(OUT_DIR, f"{PREFIX}_traditions.csv"), tcols, trows)

    mk = collections.defaultdict(lambda: {"names": collections.Counter(), "src": collections.Counter(),
                                          "cult": collections.Counter(), "per": collections.Counter(),
                                          "roles": collections.Counter(), "kind": collections.Counter(),
                                          "types": collections.Counter(), "regions": collections.Counter(),
                                          "begins": [], "ends": [], "ex": []})
    for r in rows:
        for n, role, kind in r["makers"]:
            k = " ".join(fold(re.sub(r"\(.*?\)", " ", n)).replace(",", " ").split())
            if not k:
                continue
            m = mk[k]
            m["names"][n] += 1
            m["src"][r["source"]] += 1
            m["cult"][r["culture"]] += 1
            m["per"][r["period"]] += 1
            m["types"][r["object_group"]] += 1
            m["regions"][r["region"]] += 1
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
             "example_ids", "region"]
    mrows = []
    for k, m in sorted(mk.items(), key=lambda kv: (-sum(kv[1]["src"].values()), kv[0])):
        mrows.append([m["names"].most_common(1)[0][0], top(m["names"], 4), m["kind"].most_common(1)[0][0],
                      sum(m["src"].values())] + [m["src"][s] for s in SOURCES] +
                     [sum(1 for s in SOURCES if m["src"][s]), top(m["cult"], 4), top(m["per"], 3),
                      top(m["types"], 3), top(m["roles"], 3), min(m["begins"]) if m["begins"] else "",
                      max(m["ends"]) if m["ends"] else "", " ".join(m["ex"]), m["regions"].most_common(1)[0][0]])
    write_csv(os.path.join(OUT_DIR, f"{PREFIX}_makers.csv"), mcols, mrows)
    return mk


def baseline():
    """Objects / cultures / makers in the earlier sweep's Africa and Oceania tables."""
    out = {}
    for region, fn, keep in (("africa", "africa_objects.csv", lambda r: True),
                             ("americas_oceania", "americas_oceania_objects.csv",
                              lambda r: r["subregion"] == "Oceania")):
        path = os.path.join(OUT_DIR, fn)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8", newline="") as f:
            rows = [r for r in csv.DictReader(f) if keep(r)]
        out[region] = {"objects": len(rows), "cultures": {r["culture"] for r in rows},
                       "attributed": sum(int(r["attributed"] or 0) for r in rows)}
    return out


def build(recs):
    os.makedirs(OUT_DIR, exist_ok=True)
    rows, seen = [], set()
    for r in recs:
        if (r["source"], r["id"]) in seen:
            continue
        seen.add((r["source"], r["id"]))
        row = make_row(r)
        if row:
            rows.append(row)
    write_tables(rows)
    base = baseline()
    summary = []
    for region in ("africa", "americas_oceania"):
        rr = [r for r in rows if r["region"] == region]
        for src in SOURCES + ("all",):
            sr = [r for r in rr if src == "all" or r["source"] == src]
            if not sr:
                continue
            n = len(sr)
            summary.append([region, src, n, sum(r["attributed"] for r in sr),
                            round(sum(r["attributed"] for r in sr) / n, 3),
                            round(sum(1 for r in sr if r["culture_source"].split(" ")[0] in ("label", "place")
                                      and "generic" not in r["culture_source"]) / n, 3),
                            round(sum(1 for r in sr if not r["culture_source"].startswith("fallback")) / n, 3),
                            round(sum(1 for r in sr if r["period_source"] in ("recorded", "description")) / n, 3),
                            round(sum(1 for r in sr if r["date_begin"] is not None) / n, 3),
                            len({r["culture"] for r in sr}), len({r["period"] for r in sr if r["period"]}),
                            len({fold(m) for r in sr for m, _, _ in r["makers"]}), "", ""])
        b = base.get(region)
        if b:
            cults = {r["culture"] for r in rr}
            summary.append([region, "baseline_south_asia_africa_americas", b["objects"], b["attributed"],
                            round(b["attributed"] / b["objects"], 3) if b["objects"] else "", "", "", "", "",
                            len(b["cultures"]), "", "", "", ""])
            summary.append([region, "growth_vs_baseline", len(rr), "", "", "", "", "", "",
                            len(cults - b["cultures"]), "", "",
                            round((len(rr) + b["objects"]) / b["objects"], 2) if b["objects"] else "",
                            "; ".join(sorted(c for c in cults - b["cultures"] if not c.startswith("Unspecified"))[:60])])
        print(f"{region}: {len(rr)} objects, {len({r['culture'] for r in rr})} cultures, "
              f"attributed {sum(r['attributed'] for r in rr)}", file=sys.stderr)
    for key, inst, why in SKIPPED_SOURCES:
        summary.append(["", key, "", "", "", "", "", "", "", "", "", "", "", f"skipped: {inst}: {why}"])
    write_csv(os.path.join(OUT_DIR, f"{PREFIX}_sources.csv"),
              ["region", "source", "objects", "attributed", "attributed_share", "culture_specific_share",
               "culture_any_share", "period_recorded_share", "dated_share", "cultures", "periods", "named_makers",
               "growth_factor_with_baseline", "note"], summary)
    write_csv(os.path.join(OUT_DIR, f"{PREFIX}_dropped.csv"), ["source", "reason", "records"],
              [[s, why, n] for (s, why), n in sorted(DROPPED.items())])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--only", default="", help="comma-separated sources to run: " + ",".join(SOURCES))
    ap.add_argument("--skip", default="", help="comma-separated sources to skip")
    ap.add_argument("--fetch-only", action="store_true", help="harvest into the cache, write nothing")
    ap.add_argument("--delay", type=float, default=0.34,
                    help="seconds between API requests (default 0.34, ~3 req/s; Auckland SPARQL always waits "
                         f"{AUCK_DELAY:.0f}s)")
    ap.add_argument("--yale-max", type=int, default=0, help="cap on Yale LUX item fetches (0 = no cap)")
    args = ap.parse_args()
    DELAY[0] = args.delay
    only = set(filter(None, args.only.split(","))) or set(SOURCES)
    only -= set(filter(None, args.skip.split(",")))
    harvesters = {"mia": harvest_mia, "penn": harvest_penn, "tepapa": harvest_tepapa,
                  "auckland": harvest_auckland, "yale": lambda: harvest_yale(args.yale_max)}
    recs = []
    for s in SOURCES:
        if s in only:
            print(f"[{s}]", file=sys.stderr)
            recs += harvesters[s]()
    print(f"network: {dict(NET)}", file=sys.stderr)
    if args.fetch_only:
        return
    build(recs)


if __name__ == "__main__":
    main()
