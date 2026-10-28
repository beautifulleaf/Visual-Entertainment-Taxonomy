"""Regional sweep: the Himalayas, Central Asia and the Silk Road
(visual-art-plan.md §2, §2A, §2.1 point 4, §2.1b, §2.2).

Himalayan and Central Asian art is largely tradition-led (§2.1 point 4): the
primary nodes are painting traditions, sculpture styles, period styles and
workshops (Menri, Khyenri, Karma Gadri, Beri, Guge, Densatil, the Tsang atelier,
Newar Licchavi / Malla work, Zanabazar's school, Dolonnor, the Yongle imperial
style; Gandhara, Kushan, Bactria, Sogdiana, Khotan, Kucha, Turfan/Uyghur,
Dunhuang, the Tangut), and named masters (Aniko, Situ Panchen, Choying Dorje,
Zanabazar, Khyentse Chenmo, Namkha Tashi) hang under them. This script collects
the evidence for those nodes as the sources record it, with periods, object
types and makers, and measures the attribution profile per tradition (§2.2).

Sources (every request is cached gzip-compressed under
data/raw/regional/himalaya_central_asia/<source>/, spaced --delay seconds apart
(default 1.0) and retried with back-off; re-runs read the cache, so the harvest
is resumable):

  Himalayan Art Resources (himalayanart.org), the field's reference database.
      robots.txt disallows only /utility/, large images, /my_gallery/ and two
      legacy URLs. HAR files style, tradition, school and artist as *thematic
      sets* ("Painting Tradition: Menri Main Page", "Painting Style: Khyenri",
      "Sculpture: Zanabazar Style", "Artist: Choying Dorje & Atelier",
      "Nepal: Early Malla Period Sculpture", "Region: Western Xia (Tangut)"),
      not as an item field. So instead of crawling all items, the set list from
      the search form (~6,900 sets) is filtered to the style / tradition /
      school / artist / regional-style sets (TRADITION_LEX and REGION_LEX on the
      set name; photo archives, bibliographies, contemporary and iconography-
      only sets are dropped). Each selected set's pages give its item numbers;
      each item page gives origin location, date range, lineage, material,
      collection and catalogue number. An item's tradition is the most specific
      tradition among the sets it belongs to; its makers come from Artist and
      atelier sets. Item pages are reduced to those fields before caching.
  V&A Collections API v2 (api.vam.ac.uk, no key): place-of-origin sweeps
      (Tibet, Nepal, Bhutan, Ladakh, Mongolia, Gandhara, Swat, Afghanistan,
      Pakistan, Central Asia, Xinjiang, Dunhuang, Kashmir, Samarkand, ...) and
      keyword sweeps (Tibetan, thangka, Newar, Gandhara, Kushan, Sogdian, ...).
      q_place_name is a fuzzy text match, so every record is re-checked against
      the place lexicon (REGION_LEX). Islamic-period Central Asia, Afghanistan
      and Pakistan (owned by the Islamic-world job) and later Kashmir (South
      Asia job) are dropped by date (keep_region). Records are reduced before
      caching. The V&A `styles` field is the recorded style (sparse here).
  Cleveland Museum of Art open-access API: departments Indian and Southeast
      Asian Art, Chinese Art and Textiles, filtered to Himalayan / Central Asian
      culture strings ("Nepal, Kathmandu Valley, Malla period", "Pakistan,
      Gandhara, Kushan Period", "Central Asia (Sogdiana) or Tibet").
  Art Institute of Chicago dump on disk (data/raw/museums/aic/artic-api-data/
      json/artworks/*.json): place_of_origin, style_title, artist_display.
  International Dunhuang Programme. The new site (idp.bl.uk) sits behind a
      Cloudflare challenge (403) and the Japanese / Russian mirrors are down;
      the Berlin mirror (idp.bbaw.de, legacy IDP database, robots.txt allows
      /database/) is used: its predefined search by object form (Gemälde =
      paintings, Artefakt = artefacts, Stoff = textiles) is run in a cookie
      session and the result lists are read (holding institution, pressmark,
      find site, language/script, materials). The lists carry no dates; the
      find site gives the oasis culture (Dunhuang, Khotan, Kucha, Turfan,
      Kharakhoto, Miran/Niya/Loulan, ...). Records with no find site
      (19th-century British prints and photographs) are dropped.
  Met cross-check: data/interim/unattributed_cultures.csv (built by
      pipelines/unattributed/build_traditions.py); top-level culture rows that
      fall in these regions are normalised with the same lexicon and their
      unattributed object counts are attached per tradition
      (met_unattributed_objects). Met objects are not re-harvested.
  Smithsonian (NMAA) is covered by pipelines/regional/smithsonian.py.

Overlap with other jobs: the South & Southeast Asia sweep also reads V&A /
Cleveland / AIC records from Nepal, Bhutan, Tibet and Gandhara; those rows are
marked overlap=south_asia here. Islamic-world material is excluded by date.

Normalising (TRADITION_LEX, PERIOD_LEX, REGION_LEX, PERIODS):
  tradition   the recorded style / school / culture label, matched against
              TRADITION_LEX (basis=recorded; for HAR: the thematic set);
              otherwise derived from region + date (basis=derived: Nepal by
              Licchavi / Transitional / Early & Late Malla / Shah, Gandhara as
              Gandharan, Tibet as Tibetan (<subregion>), ...).
  period      a recorded period / dynasty word (Licchavi, Malla, Kushan, Yuan,
              Ming, Qing, Western Xia, Tibetan rule, ...) or, failing that,
              derived from region + mid date (PERIODS).
  attributed  the object has a named maker: an artist or a named master's
              atelier/design (not "style of", not placeholders).

Outputs (data/interim/regional/):
  himalaya_central_asia_objects.csv     one row per object: source, id, title,
      region_group (Himalaya | Central Asia & Silk Road), region, country,
      place as recorded, tradition as recorded (labels / HAR sets), tradition,
      all traditions, basis, period (+basis), date text, begin/end, object type,
      medium, materials, makers ("name [role]"), attributed, lineage (HAR),
      institution / collection, language (IDP), overlap, url
  himalaya_central_asia_traditions.csv  kind = tradition | tradition_period |
      tradition_period_type: objects per source, n_sources, recorded share,
      attributed share, date range and mid-date quartiles, top object types,
      places, named makers, Met cross-check (tradition rows), example ids
  himalaya_central_asia_makers.csv      named makers / ateliers: objects per
      source, roles, traditions (the school they hang under), regions,
      periods, date range, example ids

Usage: python3 pipelines/regional/himalaya_central_asia.py
           [--skip har,vam,cma,aic,idp] [--har-max-items N] [--delay 1.0]
           [--fetch-only]
"""
import argparse
import collections
import csv
import gzip
import html
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
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw", "regional", "himalaya_central_asia")
OUT_DIR = os.path.join(ROOT, "data", "interim", "regional")
AIC_DIR = os.path.join(ROOT, "data", "raw", "museums", "aic", "artic-api-data", "json", "artworks")
MET_CULTURES = os.path.join(ROOT, "data", "interim", "unattributed_cultures.csv")
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"

HAR = "https://www.himalayanart.org"
VAM_API = "https://api.vam.ac.uk/v2/objects/search"
VAM_OBJECT_URL = "https://collections.vam.ac.uk/item/{}/"
VAM_MAX = 10000
VAM_PAGE = 100
CMA_API = "https://openaccess-api.clevelandart.org/api/artworks/"
CMA_FIELDS = ("id,accession_number,title,culture,creators,type,technique,creation_date,"
              "creation_date_earliest,creation_date_latest,department,url")
IDP = "http://idp.bbaw.de"
SOURCES = ("har", "vam", "cma", "aic", "idp")

# --------------------------------------------------------------------- fetching

_last = [0.0]
DELAY = [1.0]
NET = collections.Counter()


def _request(url, data=None, headers=None, opener=None):
    """GET (or POST multipart `data`) with spacing and back-off. Returns text or None."""
    for attempt in range(5):
        wait = DELAY[0] - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        h = {"User-Agent": UA, "Accept": "application/json, text/html;q=0.9"}
        h.update(headers or {})
        req = urllib.request.Request(url, data=data, headers=h)
        try:
            with (opener.open(req, timeout=180) if opener else urllib.request.urlopen(req, timeout=180)) as r:
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


def cached(url, path, parse, ok=None, **kw):
    """GET url, parse(text) -> data, cache data gzip-compressed at path. ok(data)
    False marks a transient bad answer: it is retried and never cached."""
    data = cache_read(path)
    if data is not None:
        return data
    for attempt in range(3):
        text = _request(url, **kw)
        if text is None:
            return None
        try:
            data = parse(text)
        except (ValueError, KeyError, TypeError) as e:
            NET["bad_answer"] += 1
            print(f"  unparseable answer from {url}: {e}", file=sys.stderr)
            data = None
        if data is not None and (ok is None or ok(data)):
            cache_write(path, data)
            return data
        NET["retried_bad_answer"] += 1
        time.sleep(10 * (attempt + 1))
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


def fold(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9,:()'&/ -]", " ", s).split())


def tidy(s):
    s = unicodedata.normalize("NFKC", html.unescape(s or "")).replace("’", "'")
    return " ".join(s.split()).strip(" ,;:-")


# ------------------------------------------------------------------ lexicons
# Regions: (regex on folded place / label text, region_group, region, country).
# First match wins, so the specific places come first.
HIM, CAS = "Himalaya", "Central Asia & Silk Road"
REGION_LEX = [
    (r"dunhuang|mogao|yulin cave|\banxi\b|guazhou", CAS, "Dunhuang", "China"),
    (r"khara.?khoto|kharakhoto|tangut|xi ?xia|western xia|ningxia|heishui", CAS, "Tangut realm (Western Xia)", "China"),
    (r"khotan|yotkan|rawak|dandan.?oilik|dandanuiliq|domoko|balawaste|khadalik|farhad.?beg|akterek|siyelik|"
     r"mazar.?tagh|hanguya|iledong|ulugh.?mazar|uzun.?tati|karayantak|kara.?yantak|melikawat|keriya|karadong|"
     r"endere|sampula|jigdalik|tamoghil|darabzandong|tugadong|khitai", CAS, "Khotan", "China (Xinjiang)"),
    (r"\bmiran\b|\bniya\b|loulan|lop.?nor|kroraina|shanshan|charchan|yingpan", CAS, "Shanshan (Miran, Niya, Loulan)",
     "China (Xinjiang)"),
    (r"kucha|kuqa|kizil|qizil|kumtura|subashi|duldur|tumshuk|simsim|kirish|shorchuk|karashahr|qarashahr|"
     r"mingoi|ming.?oi|khora\b", CAS, "Kucha & northern Tarim", "China (Xinjiang)"),
    (r"turfan|turpan|bezeklik|bazaklik|qoc?ho|kocho|chotscho|khocho|gaochang|astana|yarkhoto|jiaohe|murtuk|toyuk|"
     r"sangim|sengim|idikut|bulayik|kurutka|beiting|beshbalik", CAS, "Turfan (Uyghur Qocho)", "China (Xinjiang)"),
    (r"xinjiang|tarim|kashgar|yarkand|tashkurghan|east(ern)? turkestan|chinese turkestan|chinese central asia",
     CAS, "Xinjiang (other)", "China (Xinjiang)"),
    (r"sogd|samarkand|samarqand|panjikent|penjikent|pendzhikent|afrasiab|afrasiyab|varakhsha|ustrushana|bukhara|"
     r"uzbekistan|tajikistan", CAS, "Sogdiana & Transoxiana", "Uzbekistan / Tajikistan"),
    (r"bactria|balkh|termez|termiz|airtam|kara.?tepe|fayaz.?tepe|dalverzin|ai.?khanum|tillya|ajina.?tepe|"
     r"turkmenistan|merv|margiana|oxus|kushano", CAS, "Bactria & Margiana", "Afghanistan / Uzbekistan / Turkmenistan"),
    (r"gilgit|chilas|\byasin\b|darel|darkot|hunza|baltistan|skardu", CAS, "Gilgit & Upper Indus", "Pakistan"),
    (r"gandhar|\bswat\b|taxila|peshawar|mardan|takht.?i.?bahi|sahri.?bahlol|jamalgarhi|charsadda|buner|bajaur|"
     r"\bdir\b|hadda|jalalabad|bamiyan|bamian|begram|kapisa|shotorak|paitava|fondukistan|\bkabul\b",
     CAS, "Gandhara", "Pakistan / Afghanistan"),
    (r"afghanistan|afghan", CAS, "Afghanistan (other)", "Afghanistan"),
    (r"pakistan", CAS, "Pakistan (other)", "Pakistan"),
    (r"kashmir|srinagar", HIM, "Kashmir", "India / Pakistan"),
    (r"ladakh|alchi|\bleh\b|\bspiti\b|kinnaur|kunawar|zangskar|zanskar|lahaul|\btabo\b|hemis|western himalaya",
     HIM, "Ladakh & Western Himalaya", "India"),
    (r"guge|tsaparang|tholing|toling|ngari|purang|west(ern)? tibet", HIM, "Western Tibet", "China (Tibet)"),
    (r"kham\b|derge|dege\b|chamdo|riwoche|palpung|kandze|ganzi|east(ern)? tibet|amdo|rebkong|repkong|regong|"
     r"qinghai|kokonor|labrang|kumbum", HIM, "Eastern Tibet (Kham, Amdo)", "China (Tibet / Qinghai / Sichuan)"),
    (r"lhasa|shigatse|gyantse|shalu|\bngor\b|densatil|central tibet|southern tibet|\btsang\b|u.?tsang|yarlung|"
     r"tashi.?lhunpo|narthang|nartang|samye|reting|sakya monastery", HIM, "Central Tibet", "China (Tibet)"),
    (r"tibet|tibetan", HIM, "Tibet", "China (Tibet)"),
    (r"mustang|dolpo|humla|jumla|khasa|yatse", HIM, "Western Nepal (Mustang, Khasa)", "Nepal"),
    (r"nepal|kathmandu|patan|lalitpur|bhaktapur|newar|deopatan", HIM, "Nepal (Kathmandu Valley)", "Nepal"),
    (r"bhutan", HIM, "Bhutan", "Bhutan"),
    (r"sikkim", HIM, "Sikkim", "India"),
    (r"inner mongolia|dolonn?or", HIM, "Inner Mongolia", "China (Inner Mongolia)"),
    (r"mongol|buryat|kalmyk|khalkha|\burga\b|ulaanbaatar", HIM, "Mongolia & Buryatia", "Mongolia / Russia"),
    (r"dali kingdom|yunnan|naxi", HIM, "Yunnan (Dali, Naxi)", "China"),
    (r"central asia|silk road|turkestan|kyrgyz|kazakh|semirechye", CAS, "Central Asia (other)", "Central Asia"),
    (r"himalaya", HIM, "Himalaya (unspecified)", ""),
    (r"\bchina\b|chinese|beijing|sino.?tibetan|qianlong|yongle|xuande|kangxi|chengde|ching dynasty|wutai",
     HIM, "China (Himalayan-style)", "China"),
]
REGION_RE = [(re.compile(p), g, r, c) for p, g, r, c in REGION_LEX]

# Traditions / schools / styles: (regex on folded label text, label). Ordered
# from specific to general; the first match is the primary tradition.
TRADITION_LEX = [
    (r"new men-?ri|men-?ri \(new\)|menri.{0,12}\bnew\b|sarma menri|menri sarma", "Menri (New Menri)"),
    (r"tashi.?lhunpo (style|menri)|menri, tashi.?lhunpo|tashi.?lhunpo.{0,10}menri", "Menri (Tashi Lhunpo)"),
    (r"\bmen-?ri\b|menthang|mentang|sman.?ris", "Menri"),
    (r"khyen-?ri|khyentse chenmo|mkhyen.?ris", "Khyenri"),
    (r"palpung|situ panchen", "Karma Gadri (Palpung)"),
    (r"karma ?gar-?d?ri|karma gar-?ri|gardri|\bgadri\b|garlug|namkha tashi|sgar.?bris", "Karma Gadri"),
    (r"khazi lha?zo|khazi lazo", "Khazi Lhazo style"),
    (r"choying dorje", "Choying Dorje atelier (Tenth Karmapa)"),
    (r"trehor|namkha gyan|kandze valley", "Trehor / Kandze (Namkha Gyan)"),
    (r"sonam gyaltsen", "Sonam Gyaltsen atelier"),
    (r"tsang (province )?atelier", "Tsang atelier"),
    (r"densatil", "Densatil"),
    (r"gyantse", "Gyantse"),
    (r"\bngor\b", "Ngor style"),
    (r"\bbalri\b|\bberi\b|bal.?ris", "Beri (Balri)"),
    (r"kham-?ri|kham riwoche|chamdo regional", "Kham regional (Kham-ri)"),
    (r"dzamthang|aba region", "Jonang Dzamthang"),
    (r"lhatog|khampa ?gar|minimalis", "Lhatog / Khampagar"),
    (r"rebkong|repkong|regong", "Rebkong (Amdo)"),
    (r"guge|tsaparang|tholing", "Guge (Western Tibet)"),
    (r"monastic period", "Tibetan Monastic Period style"),
    (r"yongle|xuande|zhengtong", "Ming imperial (Yongle / Xuande)"),
    (r"qianlong", "Qing imperial (Qianlong)"),
    (r"kangxi", "Qing imperial (Kangxi)"),
    (r"chengde", "Chengde (Qing)"),
    (r"\baniko\b|\baraniko\b|\banige\b", "Aniko school (Yuan)"),
    (r"dolonn?or", "Dolonnor (Inner Mongolia)"),
    (r"zanabazar", "Zanabazar school"),
    (r"dali kingdom|dali style", "Dali Kingdom (Yunnan)"),
    (r"\bnaxi\b", "Naxi"),
    (r"tangut|xi ?xia|western xia|khara.?khoto|kharakhoto", "Tangut (Western Xia)"),
    (r"dunhuang|mogao|yulin", "Dunhuang"),
    (r"khotan", "Khotanese"),
    (r"kucha|kizil|qizil|kumtura|subashi|duldur|tumshuk|shorchuk", "Kucha / northern Tarim"),
    (r"bezeklik|bazaklik|qoc?ho|kocho|chotscho|khocho|uyghur|uighur|uigur|turfan", "Uyghur (Turfan, Qocho)"),
    (r"\bmiran\b|\bniya\b|loulan|kroraina|shanshan", "Shanshan (Miran, Niya, Loulan)"),
    (r"sogd|panjikent|penjikent|afrasiab|afrasiyab|varakhsha", "Sogdian"),
    (r"kushano.?sasanian", "Kushano-Sasanian"),
    (r"graeco.?bactrian|greco.?bactrian|indo.?greek", "Graeco-Bactrian / Indo-Greek"),
    (r"bactria.?margiana|\bbmac\b|oxus civili", "Bactria-Margiana (BMAC)"),
    (r"bactria", "Bactrian"),
    (r"hadda", "Hadda (Gandharan stucco)"),
    (r"bamiyan|bamian", "Bamiyan"),
    (r"\bswat\b", "Swat Valley"),
    (r"gandhar", "Gandharan"),
    (r"kushan|kusana|kushana", "Kushan"),
    (r"gilgit|chilas|palola|patola shahi", "Gilgit (Palola Shahi)"),
    (r"kashmir", "Kashmiri"),
    (r"licchavi|lichchhavi|lichavi", "Nepal: Licchavi"),
    (r"transitional period|thakuri", "Nepal: Transitional (Thakuri)"),
    (r"early mall?a", "Nepal: Early Malla"),
    (r"late mall?a", "Nepal: Late Malla"),
    (r"khasa|yatse", "Khasa Malla (western Nepal)"),
    (r"\bmall?a (period|dynasty)", "Nepal: Malla"),
    (r"\bshah (period|dynasty)", "Nepal: Shah"),
    (r"newar", "Newar"),
    (r"mustang", "Mustang"),
    (r"bhutan", "Bhutanese"),
    (r"sikkim", "Sikkimese"),
    (r"ladakh|alchi|\bspiti\b|kunawar|kinnaur|zangskar|zanskar|\btabo\b|hemis", "Western Himalayan (Ladakh, Spiti, Kinnaur)"),
    (r"buryat", "Buryat"),
    (r"inner mongolia", "Inner Mongolian"),
    (r"mongol", "Mongolian"),
    (r"sino.?tibetan|painting style: chinese|chinese style|sculpture: china$|region: china|tibeto.?chinese|"
     r"ching dynasty|ming period style",
     "Sino-Tibetan (China)"),
    (r"indian style|painting style: indian|\bpala\b", "Pala / Indian style (in Tibet)"),
    (r"tibetan empire|period of tibetan rule|tibetan rule", "Tibetan Empire period"),
    (r"west(ern)? tibet", "Western Tibetan"),
    (r"east(ern)? tibet|\bkham\b|derge|\bamdo\b", "Eastern Tibetan"),
    (r"central tibet", "Central Tibetan"),
]
TRADITION_RE = [(re.compile(p), t) for p, t in TRADITION_LEX]
TRADITION_RANK = {t: i for i, (_, t) in enumerate(TRADITION_LEX)}

# Recorded period / dynasty words -> period label
PERIOD_LEX = [
    (r"licchavi|lichchhavi", "Licchavi (c. 300-879)"),
    (r"transitional period|thakuri", "Transitional / Thakuri (879-1200)"),
    (r"early mall?a", "Early Malla (1200-1482)"),
    (r"late mall?a", "Late Malla (1482-1769)"),
    (r"\bmall?a\b", "Malla (1200-1769)"),
    (r"\bshah (period|dynasty)", "Shah (1769-2008)"),
    (r"kushano.?sasanian", "Kushano-Sasanian (c. 230-365)"),
    (r"kushan|kusana|kushana", "Kushan (c. 30-375)"),
    (r"graeco.?bactrian|greco.?bactrian|indo.?greek", "Graeco-Bactrian / Indo-Greek (c. 250-10 BCE)"),
    (r"hephthal|kidarite", "Kidarite / Hephthalite (c. 375-600)"),
    (r"turk shahi", "Turk Shahi (c. 600-870)"),
    (r"hindu shahi", "Hindu Shahi (c. 870-1026)"),
    (r"karkota", "Karkota (625-855)"),
    (r"utpala", "Utpala (855-1003)"),
    (r"lohara", "Lohara (1003-1339)"),
    (r"period of tibetan rule|tibetan empire|tibetan rule", "Tibetan Empire (c. 618-842)"),
    (r"western xia|xi ?xia|tangut", "Western Xia (1038-1227)"),
    (r"uyghur kingdom|uighur kingdom|qocho kingdom|kingdom of qocho", "Uyghur Qocho kingdom (c. 850-1250)"),
    (r"\bsui\b", "Sui (581-618)"),
    (r"\btang\b", "Tang (618-907)"),
    (r"five dynasties", "Five Dynasties (907-960)"),
    (r"\bliao\b", "Liao (907-1125)"),
    (r"\bsong\b", "Song (960-1279)"),
    (r"\byuan\b", "Yuan (1271-1368)"),
    (r"\bming\b|yongle|xuande|zhengtong|wanli", "Ming (1368-1644)"),
    (r"\bqing\b|qianlong|kangxi|yongzheng|jiaqing|daoguang", "Qing (1644-1912)"),
    (r"pala.?sena|\bpala (period|dynasty)", "Pala (c. 750-1200)"),
    (r"gupta", "Gupta (c. 320-550)"),
]
PERIOD_RE = [(re.compile(p), t) for p, t in PERIOD_LEX]

# Derived periods: region -> [(start, end, label)] on the object's mid date
CHINA = [(581, 618, "Sui (581-618)"), (618, 907, "Tang (618-907)"), (907, 960, "Five Dynasties (907-960)"),
         (960, 1271, "Song (960-1279)"), (1271, 1368, "Yuan (1271-1368)"), (1368, 1644, "Ming (1368-1644)"),
         (1644, 1912, "Qing (1644-1912)"), (1912, 2100, "Modern (1912-)")]
TIBET = [(600, 842, "Tibetan Empire (c. 618-842)"), (842, 1247, "Era of Fragmentation / Later Diffusion (842-1247)"),
         (1247, 1354, "Sakya-Yuan (1247-1354)"), (1354, 1435, "Phagmodrupa (1354-1435)"),
         (1435, 1565, "Rinpungpa (1435-1565)"), (1565, 1642, "Tsangpa (1565-1642)"),
         (1642, 1912, "Ganden Phodrang (1642-1912)"), (1912, 2100, "Modern (1912-)")]
GANDHARA = [(-330, -185, "Mauryan (c. 322-185 BCE)"), (-185, -10, "Indo-Greek (c. 185-10 BCE)"),
            (-10, 30, "Indo-Scythian / Indo-Parthian (c. 10 BCE-30 CE)"), (30, 375, "Kushan (c. 30-375)"),
            (375, 600, "Kidarite / Hephthalite (c. 375-600)"), (600, 870, "Turk Shahi (c. 600-870)"),
            (870, 1026, "Hindu Shahi (c. 870-1026)")]
PERIODS = {
    "Nepal (Kathmandu Valley)": [(300, 879, "Licchavi (c. 300-879)"), (879, 1200, "Transitional / Thakuri (879-1200)"),
                                 (1200, 1482, "Early Malla (1200-1482)"), (1482, 1769, "Late Malla (1482-1769)"),
                                 (1769, 2100, "Shah (1769-2008)")],
    "Western Nepal (Mustang, Khasa)": [(1100, 1400, "Khasa Malla (c. 1100-1400)"), (1400, 1769, "Late Malla (1482-1769)"),
                                        (1769, 2100, "Shah (1769-2008)")],
    "Tibet": TIBET, "Central Tibet": TIBET, "Western Tibet": [(600, 842, "Tibetan Empire (c. 618-842)"),
                                                            (842, 1630, "Guge-Purang kingdom (c. 950-1630)")] + TIBET[6:],
    "Eastern Tibet (Kham, Amdo)": TIBET,
    "Ladakh & Western Himalaya": [(950, 1460, "West Tibetan kingdoms (Maryul, Guge-Purang) (c. 950-1460)"),
                                  (1460, 1842, "Namgyal (1460-1842)"), (1842, 2100, "Dogra / modern (1842-)")],
    "Bhutan": [(0, 1616, "Pre-Zhabdrung (before 1616)"), (1616, 1907, "Zhabdrung / Desi era (1616-1907)"),
               (1907, 2100, "Wangchuck monarchy (1907-)")],
    "Sikkim": [(1642, 1975, "Namgyal Chogyals (1642-1975)")],
    "Mongolia & Buryatia": [(1206, 1368, "Mongol Empire / Yuan (1206-1368)"), (1368, 1635, "Northern Yuan (1368-1635)"),
                            (1635, 1911, "Qing era / Jebtsundamba Khutughtus (1635-1911)"),
                            (1911, 2100, "Bogd Khanate / modern (1911-)")],
    "Inner Mongolia": CHINA, "China (Himalayan-style)": CHINA, "Yunnan (Dali, Naxi)": [(937, 1253, "Dali Kingdom (937-1253)")] + CHINA[4:],
    "Kashmir": [(0, 625, "Early (before 625)"), (625, 855, "Karkota (625-855)"), (855, 1003, "Utpala (855-1003)"),
                (1003, 1339, "Lohara (1003-1339)")],
    "Gandhara": GANDHARA, "Pakistan (other)": GANDHARA, "Afghanistan (other)": GANDHARA,
    "Gilgit & Upper Indus": [(0, 600, "Early historic"), (600, 800, "Palola Shahi (c. 600-800)")],
    "Bactria & Margiana": [(-2400, -1500, "Bronze Age (BMAC, c. 2400-1500 BCE)"), (-550, -330, "Achaemenid (550-330 BCE)"),
                           (-330, -250, "Seleucid (330-250 BCE)"), (-250, -125, "Graeco-Bactrian (c. 250-125 BCE)"),
                           (-125, 30, "Yuezhi (c. 125 BCE-30 CE)"), (30, 230, "Kushan (c. 30-375)"),
                           (230, 365, "Kushano-Sasanian (c. 230-365)"), (365, 560, "Kidarite / Hephthalite (c. 375-600)"),
                           (560, 750, "Western Turk / Tokharistan (c. 560-750)")],
    "Sogdiana & Transoxiana": [(-550, -330, "Achaemenid (550-330 BCE)"), (-330, 400, "Early Sogdian (c. 330 BCE-400 CE)"),
                               (400, 750, "Sogdian city-states (c. 400-750)")],
    "Dunhuang": [(366, 581, "Sixteen Kingdoms / Northern dynasties (366-581)"), (581, 618, "Sui (581-618)"),
                 (618, 781, "Tang (618-907)"), (781, 848, "Tibetan Empire (c. 618-842)"),
                 (848, 1036, "Guiyijun (848-1036)"), (1036, 1227, "Western Xia (1038-1227)"),
                 (1227, 1368, "Yuan (1271-1368)")],
    "Tangut realm (Western Xia)": [(1038, 1227, "Western Xia (1038-1227)"), (1227, 1368, "Yuan (1271-1368)")],
    "Turfan (Uyghur Qocho)": [(0, 640, "Gaochang kingdom (to 640)"), (640, 792, "Tang (618-907)"),
                              (792, 850, "Tibetan Empire (c. 618-842)"), (850, 1250, "Uyghur Qocho kingdom (c. 850-1250)"),
                              (1250, 1400, "Mongol / Chagatai (1250-1400)")],
    "Kucha & northern Tarim": [(0, 658, "Kingdom of Kucha (to 658)"), (658, 790, "Tang (618-907)"),
                               (790, 1250, "Uyghur (c. 790-1250)")],
    "Khotan": [(0, 1006, "Kingdom of Khotan (to 1006)")],
    "Shanshan (Miran, Niya, Loulan)": [(0, 450, "Kroraina / Shanshan kingdom (to c. 450)"),
                                      (650, 850, "Tibetan Empire (c. 618-842)")],
    "Xinjiang (other)": [(0, 1250, "Tarim oasis kingdoms (to c. 1250)")],
}

# Derived traditions when no recorded label matched
REGION_DEFAULT_TRADITION = {
    "Tibet": "Tibetan", "Central Tibet": "Tibetan (Central)", "Western Tibet": "Tibetan (Western)",
    "Eastern Tibet (Kham, Amdo)": "Tibetan (Eastern)", "Ladakh & Western Himalaya": "Western Himalayan (Ladakh, Spiti, Kinnaur)",
    "Western Nepal (Mustang, Khasa)": "Mustang", "Bhutan": "Bhutanese", "Sikkim": "Sikkimese",
    "Mongolia & Buryatia": "Mongolian", "Inner Mongolia": "Inner Mongolian", "Yunnan (Dali, Naxi)": "Dali Kingdom (Yunnan)",
    "Kashmir": "Kashmiri", "Gandhara": "Gandharan", "Pakistan (other)": "Gandharan", "Afghanistan (other)": "Gandharan",
    "Gilgit & Upper Indus": "Gilgit (Palola Shahi)", "Bactria & Margiana": "Bactrian", "Sogdiana & Transoxiana": "Sogdian",
    "Dunhuang": "Dunhuang", "Tangut realm (Western Xia)": "Tangut (Western Xia)", "Turfan (Uyghur Qocho)": "Uyghur (Turfan, Qocho)",
    "Kucha & northern Tarim": "Kucha / northern Tarim", "Khotan": "Khotanese",
    "Shanshan (Miran, Niya, Loulan)": "Shanshan (Miran, Niya, Loulan)", "Xinjiang (other)": "Tarim Basin (other)",
    "Central Asia (other)": "Central Asian (other)", "Himalaya (unspecified)": "Himalayan (unspecified)",
    "China (Himalayan-style)": "Sino-Tibetan (China)",
}
NEPAL_TRADITION = {"Licchavi (c. 300-879)": "Nepal: Licchavi", "Transitional / Thakuri (879-1200)": "Nepal: Transitional (Thakuri)",
                   "Early Malla (1200-1482)": "Nepal: Early Malla", "Late Malla (1482-1769)": "Nepal: Late Malla",
                   "Shah (1769-2008)": "Nepal: Shah"}

ISLAMIC_RE = re.compile(r"islam|timurid|safavid|shaybanid|samanid|ghaznavid|ghurid|seljuk|seljuq|qajar|mughal|"
                        r"durrani|khanate|uzbek|manghit|ashtarkhanid|kara.?khanid|qarakhanid|abbasid|umayyad|"
                        r"mamluk|ottoman|ilkhanid|chagatai", re.I)


def match_region(text):
    t = fold(text)
    for rx, g, r, c in REGION_RE:
        if rx.search(t):
            return g, r, c
    return None


def match_traditions(text):
    t = fold(text)
    return [lab for rx, lab in TRADITION_RE if rx.search(t)]


def match_period(text):
    t = fold(text)
    for rx, lab in PERIOD_RE:
        if rx.search(t):
            return lab
    return ""


def mid_of(b, e):
    if b is None and e is None:
        return None
    if b is None:
        return e
    if e is None:
        return b
    return (b + e) / 2


def derive_period(region, mid):
    if mid is None:
        return ""
    for a, b, lab in PERIODS.get(region, []):
        if a <= mid < b:
            return lab
    if region in ("Tibet", "Central Tibet", "Eastern Tibet (Kham, Amdo)", "Western Tibet") and mid >= 1912:
        return "Modern (1912-)"
    return ""


def keep_region(region, mid, labels=""):
    """Scope rules at the edges of the region (the Islamic world, South Asia and
    the Indus civilisation belong to other jobs)."""
    if ISLAMIC_RE.search(labels or ""):
        return False
    if region in ("Afghanistan (other)", "Gandhara", "Bactria & Margiana", "Sogdiana & Transoxiana",
                  "Central Asia (other)", "Gilgit & Upper Indus"):
        # undated finds from Samarkand, Afghanistan, ... are mostly Islamic-period
        return mid is not None and mid < 1000
    if region == "Pakistan (other)":
        return mid is not None and -330 <= mid < 1000
    if region == "Kashmir":
        return mid is not None and mid < 1400
    if region == "Khotan":
        return mid is None or mid < 1100
    if region in ("Kucha & northern Tarim", "Turfan (Uyghur Qocho)", "Xinjiang (other)", "Shanshan (Miran, Niya, Loulan)"):
        return mid is None or mid < 1450
    return True


def classify(row, place_text, label_text, extra_traditions=()):
    """Fill region, tradition(s), period on row. Returns False if out of scope."""
    reg = match_region(place_text) or match_region(label_text)
    b, e = row.get("date_begin"), row.get("date_end")
    mid = mid_of(b, e)
    if not reg:
        return False
    g, r, c = reg
    if not keep_region(r, mid, label_text):
        return False
    if r == "China (Himalayan-style)" and row.get("source") != "har" and not re.search(
            r"tibet|sino|lama|mongol|himalaya|tangut|xixia|dunhuang", fold(place_text + " " + label_text)):
        return False
    row.update(region_group=g, region=r, country=c)
    trads = list(dict.fromkeys(list(extra_traditions) + match_traditions(label_text)))
    period = match_period(label_text)
    row["period_basis"] = "recorded" if period else ""
    if not period:
        period = derive_period(r, mid)
        row["period_basis"] = "derived" if period else ""
    row["period"] = period
    if trads:
        trads.sort(key=lambda t: TRADITION_RANK.get(t, 999))
        row["tradition_basis"] = "recorded"
    else:
        if r == "Nepal (Kathmandu Valley)":
            t = NEPAL_TRADITION.get(derive_period(r, mid), "Nepalese (undated)")
        else:
            t = REGION_DEFAULT_TRADITION.get(r, r)
        trads = [t]
        row["tradition_basis"] = "derived"
    row["tradition"] = trads[0]
    row["traditions_all"] = "; ".join(trads)
    return True


MEDIUM_RE = [
    ("painting", re.compile(r"thangka|tangka|paint|mural|pigment|on cotton|on silk|on cloth|banner|scroll|"
                            r"tempera|watercolou?r|gemalde|initiation card|tsakali|tsakli", re.I)),
    ("manuscript / book", re.compile(r"manuscript|folio|sutra|book|\bpage\b|leaf|pothi|codex|illuminat", re.I)),
    ("textile", re.compile(r"textile|appliqu|embroider|brocade|tapestry|kesi|silk fragment|carpet|rug|\bstoff\b|"
                           r"costume|robe|coat|apron|garment|hat\b|fabric|felt", re.I)),
    ("sculpture", re.compile(r"sculpt|figure|statue|statuette|relief|stele|head of|bust|torso|bronze|copper alloy|"
                             r"gilt|repouss|stucco|schist|terracotta|clay|stone|buddha|bodhisattva|deity|tsatsa", re.I)),
    ("ritual object", re.compile(r"ritual|vajra|ghanta|bell|phurba|kila|reliquary|stupa|chorten|prayer wheel|"
                                 r"amulet|gau\b|ga'u|offering|skull|kapala|mandala|altar|butter lamp", re.I)),
    ("jewellery", re.compile(r"jewel|necklace|earring|ring\b|bracelet|pendant|bead|ornament|brooch", re.I)),
    ("metalwork", re.compile(r"ewer|bowl|vessel|teapot|jug|box|plate|dish|cup|metal|silver|brass|iron", re.I)),
    ("arms & armour", re.compile(r"sword|knife|dagger|helmet|armou?r|saddle|shield|bow\b|quiver|spear", re.I)),
    ("ceramics", re.compile(r"ceramic|pottery|porcelain|earthenware|stoneware|\bpot\b|\bjar\b|vase", re.I)),
    ("woodwork / furniture", re.compile(r"wood|table|chest|cabinet|book.?cover|printing block|woodblock", re.I)),
    ("mask", re.compile(r"\bmask", re.I)),
]


def medium_of(*texts):
    for t in texts:
        for name, rx in MEDIUM_RE:
            if t and rx.search(t):
                return name
    return "other"


# ------------------------------------------------------------------ makers

PLACEHOLDER_MAKER = re.compile(
    r"^(unknown|unidentified|anonymous|not known|various|unrecorded|n/?a|none)\b", re.I)
MAKER_ALIASES = [
    (r"\b(aniko|araniko|anige|arniko)\b", "Aniko"),
    (r"khazi lha?zo|khazi lazo", "Khazi Lhazo"),
    (r"drugu cho.?e?gyal", "Drugu Choegyal"),
    (r"\bpei\b", "Pei Zhuangxin"),
    (r"namkha gyan", "Trehor Namkha Gyan"),
    (r"situ panchen", "Situ Panchen Chokyi Jungne"),
    (r"zanabazar", "Zanabazar"),
    (r"choying dorje", "Choying Dorje (Tenth Karmapa)"),
    (r"khyentse chenmo", "Khyentse Chenmo"),
]
MAKER_ALIAS_RE = [(re.compile(p, re.I), n) for p, n in MAKER_ALIASES]
ATTRIBUTED_ROLES = re.compile(r"^(artist|maker|painter|sculptor|designer|design|atelier|attributed|made|calligrapher|"
                              r"carver|caster|weaver|creator|workshop of|probably|possibly|$)", re.I)


def maker_name(n):
    n = tidy(n)
    for rx, canon in MAKER_ALIAS_RE:
        if rx.search(n):
            return canon
    return n


def maker_key(n):
    s = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"[^a-z ]", " ", s)
    return " ".join(s.split())


# --------------------------------------------------------- Himalayan Art Resources

HAR_EXCLUDE = re.compile(
    r"archive|\(miller\)|pritzker|uranchimeg|maki\b|bibliograph|glossary|essay|video|contemporary|confusion|"
    r"calendar|exhibition|wutaishan|dazu|burma|bodhgaya|gangetic|region, india|region: india|india, pala|"
    r"pala period \(|^sculpture: india$|jain|japan|resume|^contents|himalayan art \(all\)|duplicate|"
    r"photograph|^tibet(?!: densatil)|^bhutan:|monastery plan|winter palace|sacred sites|cityscape|"
    r"stupas$|architecture|prayer flag|^publication|^initiation cards|abstract:|later copies|copies\)|"
    r"^artist: (unknown|three paintings)", re.I)
HAR_CORE_PREFIX = re.compile(r"^(painting style|painting tradition|sculpture|artist|region|nepal|mongolia|"
                             r"art history)\b", re.I)


# labels that name a region or a lineage seat rather than a school: on subject
# sets ("Teacher: Ngor Khenchen", "Buddhist Deity: Jambhala (East Tibet)") they
# describe the subject, so they count only on style-like sets
REGIONISH = {"Bhutanese", "Mongolian", "Buryat", "Inner Mongolian", "Eastern Tibetan", "Western Tibetan",
             "Central Tibetan", "Ngor style", "Western Himalayan (Ladakh, Spiti, Kinnaur)", "Sikkimese", "Mustang",
             "Newar", "Kashmiri", "Dunhuang", "Sogdian", "Khotanese", "Gandharan", "Swat Valley", "Naxi"}
STYLE_LIKE = re.compile(r"^(painting set|sculpture set|collection of|collection:)|style|painting|sculpture|"
                        r"masterworks|atelier|workshop", re.I)


def har_select_sets(names):
    """{setID: name} -> {setID: (name, tradition or '', region or None)} for
    tradition / style / school / artist / regional-style sets."""
    out = {}
    for sid, name in names.items():
        if HAR_EXCLUDE.search(name):
            continue
        trads = match_traditions(name)
        reg = match_region(name)
        artist = bool(re.match(r"artist:", name, re.I))
        if trads and trads[0] in REGIONISH and not HAR_CORE_PREFIX.match(name) and not STYLE_LIKE.search(name):
            trads = []
        if trads or artist or (HAR_CORE_PREFIX.match(name) and reg):
            out[sid] = (name, trads[0] if trads else "", reg)
    return out


def har_set_maker(name):
    """Named maker carried by a set name: ("Situ Panchen Chokyi Jungne", "design")."""
    m = re.match(r"artist:\s*(.+)$", name, re.I)
    if m:
        n = m.group(1)
        role = "style of" if re.search(r"\bstyle\b", n, re.I) else (
            "atelier" if re.search(r"atelier", n, re.I) else "artist")
        n = re.sub(r"\(.*?\)|\[.*?\]", " ", n)
        n = re.split(r"\s+(?:&|and)\s+atelier|\s+atelier|\s+style\b|\s+-\s+|\s+(?:page|masterworks|works of art|works|"
                     r"painting sets|subjects list|biography)\b", n, flags=re.I)[0]
        n = n.strip(" ,:")
        return (maker_name(n), role) if n else None
    for rx, canon, role in ((r"situ panchen design", "Situ Panchen Chokyi Jungne", "design"),
                            (r"sonam gyaltsen (&|and) atelier", "Sonam Gyaltsen", "atelier"),
                            (r"choying dorje (&|and )?atelier|choying dorje atelier", "Choying Dorje (Tenth Karmapa)", "atelier"),
                            (r"namkha gyan.{0,6}atelier|trehor namkha gyan", "Trehor Namkha Gyan", "atelier"),
                            (r"zanabazar style (&|and) atelier", "Zanabazar", "atelier"),
                            (r"khazi lha?zo (&|and) atelier", "Khazi Lhazo", "atelier"),
                            (r"aniko\[\?\]", "Aniko", "attributed (uncertain)")):
        if re.search(rx, name, re.I):
            return canon, role
    return None


def har_set_medium(name):
    n = name.lower()
    if re.search(r"sculpt|bronze|metal|stone|wood|repouss|clay|tsatsa|ivory|densatil|dolonnor", n):
        return "sculpture"
    if re.search(r"textile|appliqu", n):
        return "textile"
    if re.search(r"paint|thangka|mural|scroll|tradition|manuscript|mandala", n):
        return "painting"
    return ""


def har_parse_set_list(text):
    m = list(re.finditer(r'<select name="setID"(.*?)</select>', text, re.S))
    if not m:
        raise ValueError("no set list on the search page")
    opts = re.findall(r'<option value="(\d+)"[^>]*>([^<\n]*)', m[0].group(1))
    return {sid: tidy(n) for sid, n in opts if sid != "0" and tidy(n)}


def har_parse_set_page(text):
    if "setPageSetID" not in text:
        raise ValueError("not a set page")
    items = []
    blk = re.search(r"ICODE,LABEL,FIGURECATEGORY[^\n]*\n(.*?)-->", text, re.S)
    if blk:
        for rec in csv.reader(blk.group(1).strip().splitlines()):
            if rec and rec[0].isdigit():
                items.append([rec[0], rec[2] if len(rec) > 2 else "", rec[4] if len(rec) > 4 else ""])
    pages = [int(p) for p in re.findall(r"setID=\d+&amp;page=(\d+)", text)] or [1]
    return {"items": items, "pages": max(pages)}


def har_parse_item(text):
    if "item-details" not in text and "page-title" not in text:
        raise ValueError("not an item page")
    f = {k: tidy(re.sub(r"<[^>]+>", " ", v)) for k, v in re.findall(r'<td id="([^"]+)">(.*?)</td>', text, re.S)}
    t = re.search(r'<h1 class="page-title">(.*?)</h1>', text, re.S)
    title = tidy(re.sub(r"<span id=\"page-type\">.*?</span>|<[^>]+>", " ", t.group(1))) if t else ""
    if re.match(r"item no\.? \d+$", title, re.I):
        title = ""
    sets = re.findall(r'href="/search/set\.cfm\?setID=(\d+)">([^<]*)</a>', text)
    return {"title": title, "fields": f, "sets": [[s, tidy(n)] for s, n in sets]}


ROLE_RANK = {"artist": 0, "atelier": 1, "design": 2, "attributed (uncertain)": 3, "style of": 4}


def harvest_har(max_items=0):
    base = os.path.join(RAW, "har")
    names = cached(HAR + "/search/", os.path.join(base, "set_list.json.gz"), har_parse_set_list)
    if not names:
        print("  HAR: set list unreachable", file=sys.stderr)
        return [], {"har_unreachable": 1}
    sel = har_select_sets(names)
    print(f"  HAR: {len(names)} thematic sets, {len(sel)} selected as tradition / style / school / artist sets",
          file=sys.stderr)
    members = collections.defaultdict(list)   # icode -> [setID]
    figure = {}
    for i, (sid, (name, trad, reg)) in enumerate(sorted(sel.items(), key=lambda x: int(x[0]))):
        page, npages = 1, 1
        while page <= npages:
            url = f"{HAR}/search/set.cfm?setID={sid}" + (f"&page={page}" if page > 1 else "")
            d = cached(url, os.path.join(base, "sets", f"{sid}_p{page:03d}.json.gz"), har_parse_set_page)
            if not d:
                break
            npages = d["pages"]
            for icode, fcat, fig in d["items"]:
                members[icode].append(sid)
                figure.setdefault(icode, (fcat, fig))
            page += 1
        if (i + 1) % 100 == 0:
            print(f"  HAR: {i + 1}/{len(sel)} sets read, {len(members)} items so far", file=sys.stderr)
    icodes = sorted(members, key=lambda x: (-len(members[x]), int(x)))
    print(f"  HAR: {len(icodes)} distinct items in the selected sets", file=sys.stderr)
    if max_items and len(icodes) > max_items:
        print(f"  HAR: item pages capped at {max_items} (items in most sets first)", file=sys.stderr)
        icodes = icodes[:max_items]
    rows, stats = [], collections.Counter()
    for k, icode in enumerate(icodes):
        d = cached(f"{HAR}/items/{icode}", os.path.join(base, "items", icode[-2:].zfill(2), f"{icode}.json.gz"),
                   har_parse_item)
        if (k + 1) % 500 == 0:
            print(f"  HAR: {k + 1}/{len(icodes)} item pages", file=sys.stderr)
        if not d:
            stats["item_unreachable"] += 1
            continue
        f = d["fields"]
        origin, dr = f.get("origin-location", ""), f.get("date-range", "")
        if not origin and not dr and not d["title"]:
            stats["detail_image_skipped"] += 1   # detail / secondary photographs of another item
            continue
        m = re.match(r"\s*(-?\d{1,4})\s*-\s*(-?\d{1,4})", dr)
        b, e = (int(m.group(1)), int(m.group(2))) if m else (to_int(dr), to_int(dr))
        set_names = [sel[s][0] for s in members[icode] if s in sel]
        trads = [sel[s][1] for s in members[icode] if s in sel and sel[s][1]]
        best = {}   # one role per maker: artist > atelier > design > attributed > style of
        for s in members[icode]:
            mk = har_set_maker(sel[s][0]) if s in sel else None
            if mk and (mk[0] not in best or ROLE_RANK.get(mk[1], 9) < ROLE_RANK.get(best[mk[0]], 9)):
                best[mk[0]] = mk[1]
        makers = list(best.items())
        fcat, fig = figure.get(icode, ("", ""))
        mats = f.get("material", "")
        med = medium_of(mats) if mats else ""
        if not med or med == "other":
            meds = [har_set_medium(n) for n in set_names]
            med = next((x for x in meds if x), "") or medium_of(d["title"], fcat) or "other"
        row = {
            "source": "har", "id": icode, "title": d["title"] or " - ".join(x for x in (fcat, fig) if x),
            "place_recorded": origin, "tradition_recorded": " | ".join(set_names),
            "date_text": dr, "date_begin": b, "date_end": e,
            "object_type": med, "medium": med, "materials": mats,
            "makers": makers, "lineage": f.get("lineages", ""),
            "institution": f.get("collection", ""), "language": "",
            "url": f"{HAR}/items/{icode}",
        }
        # the item's origin decides the region; the set names refine a bare
        # "Tibet" or stand in when the origin is outside the lexicon ("China")
        o_reg, s_reg = match_region(origin), match_region(" | ".join(set_names))
        if o_reg and not (o_reg[1] == "Tibet" and s_reg and "Tibet" in s_reg[1]):
            place = origin
        else:
            place = " | ".join(set_names) or origin
        if not classify(row, place, " | ".join(set_names), trads):
            stats["out_of_scope"] += 1
            continue
        rows.append(row)
    stats["objects"] = len(rows)
    print(f"  HAR: {len(rows)} objects ({dict(stats)})", file=sys.stderr)
    return rows, stats


# --------------------------------------------------------------------- V&A

VAM_PLACES = ["Tibet", "Lhasa", "Nepal", "Kathmandu", "Patan", "Bhaktapur", "Bhutan", "Ladakh", "Sikkim",
              "Mongolia", "Inner Mongolia", "Himalayas", "Gandhara", "Swat", "Taxila", "Peshawar", "Hadda",
              "Afghanistan", "Pakistan", "Central Asia", "Xinjiang", "Dunhuang", "Khotan", "Kashmir",
              "Samarkand", "Uzbekistan", "Tajikistan", "Turkmenistan"]
VAM_KEYWORDS = ["Tibetan", "thangka", "Newar", "Nepalese", "Bhutanese", "Mongolian", "Gandhara", "Gandharan",
                "Kushan", "Sogdian", "Bactrian", "Khotan", "Dunhuang", "Tangut", "Xixia", "Uighur", "Sino-Tibetan"]
DOCUMENTARY_TYPE = re.compile(r"photograph|negative|lantern slide|postcard|print\b|transparency|cast\b|model\b|"
                              r"sketch|drawing", re.I)


def vam_reduce(d):
    recs = []
    for r in d.get("records") or []:
        dates = r.get("productionDates") or []
        dd = dates[0].get("date", {}) if dates else {}
        recs.append({
            "id": r.get("systemNumber", ""),
            "type": r.get("objectType") or "",
            "title": next((t.get("title", "") for t in r.get("titles") or [] if t.get("title")), ""),
            "styles": [s.get("text", "") for s in r.get("styles") or [] if s.get("text")],
            "places": [[(p.get("place") or {}).get("text", ""), (p.get("association") or {}).get("text", "")]
                       for p in r.get("placesOfOrigin") or []],
            "date": [dd.get("text", ""), dd.get("earliest"), dd.get("latest")],
            "makers": [[(m.get("name") or {}).get("text", ""), (m.get("association") or {}).get("text", "")]
                       for m in (r.get("artistMakerPerson") or []) + (r.get("artistMakerOrganisations") or [])],
            "people": [(m.get("name") or {}).get("text", "") for m in r.get("artistMakerPeople") or []],
            "mats": r.get("materialsAndTechniques") or "",
            "coll": (r.get("collectionCode") or {}).get("text", ""),
            "production": (r.get("production") or "")[:400],
        })
    return {"info": d.get("info", {}), "records": recs}


def vam_query(label, params):
    page = 1
    while True:
        p = dict(params, page_size=VAM_PAGE, page=page, data_profile="full")
        url = VAM_API + "?" + urllib.parse.urlencode(p)
        d = cached(url, os.path.join(RAW, "vam", slug(label), f"p{page:03d}.json.gz"), lambda t: vam_reduce(json.loads(t)))
        if not d or not d.get("records"):
            break
        yield from d["records"]
        info = d.get("info", {})
        if page >= info.get("pages", 0) or page * VAM_PAGE >= VAM_MAX:
            break
        page += 1


def vam_year(s):
    m = re.match(r"(-?\d{1,4})", str(s or ""))
    return int(m.group(1)) if m else None


def vam_row(r):
    made = [p for p, a in r["places"] if p and a in ("made", "", "probably made", "possibly made", "found")]
    place = "; ".join(dict.fromkeys(made or [p for p, a in r["places"] if p and not re.match(
        r"(photographed|depicted|published|printed|retailed|collected|used)", a or "")]))
    makers = [(maker_name(n), role) for n, role in r["makers"] if n and not PLACEHOLDER_MAKER.match(n)]
    labels = "; ".join(r["styles"] + r["people"])
    return {
        "source": "vam", "id": r["id"], "title": r["title"] or r["type"],
        "place_recorded": place, "tradition_recorded": labels,
        "date_text": r["date"][0], "date_begin": vam_year(r["date"][1]), "date_end": vam_year(r["date"][2]),
        "object_type": r["type"], "medium": medium_of(r["type"], r["mats"]), "materials": r["mats"][:300],
        "makers": makers, "lineage": "", "institution": "Victoria and Albert Museum (" + r["coll"] + ")",
        "language": "", "url": VAM_OBJECT_URL.format(r["id"]),
        "_label_text": labels + " | " + r["production"],
    }


def harvest_vam():
    rows, stats = {}, collections.Counter()
    sweeps = [(p, {"q_place_name": p}) for p in VAM_PLACES] + [("kw_" + k, {"q": k}) for k in VAM_KEYWORDS]
    for label, params in sweeps:
        n = kept = 0
        for rec in vam_query(label, params):
            n += 1
            if not rec["id"] or rec["id"] in rows:
                continue
            row = vam_row(rec)
            if DOCUMENTARY_TYPE.search(row["object_type"]) and (row["date_begin"] or 0) >= 1750:
                stats["documentary_dropped"] += 1
                continue
            # place text decides; labels only help when no place is recorded
            ok = classify(row, row["place_recorded"] or row["_label_text"], row["_label_text"])
            if ok:
                rows[rec["id"]] = row
                kept += 1
        stats[label] = kept
        print(f"  V&A {label}: {n} records read, {kept} new kept", file=sys.stderr)
    return list(rows.values()), stats


# --------------------------------------------------------------- Cleveland

CMA_DEPTS = ["Indian and Southeast Asian Art", "Chinese Art", "Textiles"]


def harvest_cma():
    rows, stats = {}, collections.Counter()
    for dept in CMA_DEPTS:
        skip, n, kept = 0, 0, 0
        while True:
            url = CMA_API + "?" + urllib.parse.urlencode({"department": dept, "skip": skip, "limit": 1000,
                                                           "fields": CMA_FIELDS})
            d = cached(url, os.path.join(RAW, "cma", f"{slug(dept)}_{skip:05d}.json.gz"), json.loads,
                       ok=lambda x: "data" in x)
            if not d or not d.get("data"):
                break
            for r in d["data"]:
                n += 1
                cult = "; ".join(r.get("culture") or [])
                aid = r.get("accession_number") or str(r.get("id"))
                if not cult or aid in rows:
                    continue
                makers = []
                for c in r.get("creators") or []:
                    desc = c.get("description") or ""
                    nm = re.sub(r"^(attributed to|workshop of|circle of|follower of|school of)\s+", "", desc.split(" (")[0],
                                flags=re.I).strip()
                    if nm and not PLACEHOLDER_MAKER.match(nm):
                        role = c.get("role") or ""
                        if re.match(r"attributed to", desc, re.I):
                            role = "attributed"
                        elif re.match(r"(workshop|circle|follower|school) of", desc, re.I):
                            role = desc.split(" ")[0].lower() + " of"
                        makers.append((maker_name(nm), role or "artist"))
                row = {
                    "source": "cma", "id": aid, "title": r.get("title") or "",
                    "place_recorded": cult, "tradition_recorded": cult,
                    "date_text": r.get("creation_date") or "",
                    "date_begin": r.get("creation_date_earliest"), "date_end": r.get("creation_date_latest"),
                    "object_type": r.get("type") or "", "materials": (r.get("technique") or "")[:300],
                    "makers": makers, "lineage": "", "institution": "Cleveland Museum of Art (" + dept + ")",
                    "language": "", "url": r.get("url") or "",
                }
                row["medium"] = medium_of(row["object_type"], row["materials"], row["title"])
                if dept != "Indian and Southeast Asian Art" and not re.search(
                        r"tibet|mongol|xinjiang|dunhuang|central asia|sogd|khotan|kucha|turfan|tangut|xixia|"
                        r"nepal|bhutan|himalaya|gandhara|bactria|uyghur|uighur|afghanistan", cult, re.I):
                    continue
                if classify(row, cult, cult):
                    rows[aid] = row
                    kept += 1
            total = d.get("info", {}).get("total", 0)
            skip += 1000
            if skip >= total:
                break
        stats[dept] = kept
        print(f"  CMA {dept}: {n} records read, {kept} kept", file=sys.stderr)
    return list(rows.values()), stats


# --------------------------------------------------------------------- AIC

def harvest_aic():
    rows, stats = [], collections.Counter()
    if not os.path.isdir(AIC_DIR):
        print("  AIC: dump not on disk", file=sys.stderr)
        return rows, {"aic_missing": 1}
    for fn in os.listdir(AIC_DIR):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(AIC_DIR, fn), encoding="utf-8") as f:
                d = json.load(f)
        except (OSError, ValueError):
            continue
        place = d.get("place_of_origin") or ""
        style = d.get("style_title") or ""
        if not place or not match_region(place):
            continue
        artist = (d.get("artist_display") or "").split("\n")[0].strip()
        makers = []
        if artist and not match_region(artist) and not PLACEHOLDER_MAKER.match(artist) \
                and not re.match(r"(tibet|nepal|mongol|bhutan|china|india|pakistan|afghan|gandhara)", artist, re.I):
            makers.append((maker_name(re.split(r"\s*\(", artist)[0]), "artist"))
        row = {
            "source": "aic", "id": str(d.get("id")), "title": d.get("title") or "",
            "place_recorded": place, "tradition_recorded": "; ".join(x for x in [style] + (d.get("style_titles") or [])[1:] if x),
            "date_text": d.get("date_display") or "", "date_begin": d.get("date_start"), "date_end": d.get("date_end"),
            "object_type": d.get("artwork_type_title") or d.get("classification_title") or "",
            "materials": (d.get("medium_display") or "")[:300], "makers": makers, "lineage": "",
            "institution": "Art Institute of Chicago", "language": "",
            "url": f"https://www.artic.edu/artworks/{d.get('id')}",
        }
        row["medium"] = medium_of(d.get("classification_title") or "", row["materials"], row["title"])
        label = " | ".join(x for x in (style, d.get("date_display") or "", place) if x)
        if style.lower() in ("himalayan", "south asian", "east asian"):
            label = place
        if classify(row, place, label):
            rows.append(row)
    stats["objects"] = len(rows)
    print(f"  AIC: {len(rows)} objects", file=sys.stderr)
    return rows, stats


# ----------------------------------------------------- IDP (Berlin mirror)

IDP_FORMS = {"ITEM000059": "painting", "ITEM000060": "artefact", "ITEM000482": "textile"}
IDP_SITE_REGION = [  # IDP find-site spellings that REGION_LEX does not already cover
    (r"chotscho|qoco|bazaklik|sangim|kichikhassar|chongtim|kurutka", "Turfan (Uyghur Qocho)"),
    (r"mingoi|kizilyar|kumtura|kucha|tumshuk|duldulokur|machi|shorchuk|khora", "Kucha & northern Tarim"),
    (r"karakhoja", "Turfan (Uyghur Qocho)"),
    # Stein site marks given in place of a site name: Ch. = Qianfodong (Dunhuang),
    # T. = Dunhuang limes, M. = Miran, M.Tagh = Mazar Tagh, E. = Endere,
    # L.A-L.K = Loulan, Ka. = Karadong
    (r"^\(?ch [0-9ivxl]", "Dunhuang"), (r"^\(?t [ivxl]+\b", "Dunhuang"),
    (r"^\(?m tagh", "Khotan"), (r"^\(?(e (i|ii|iii|fort)\b)", "Khotan"), (r"^\(?ka [ivx]+", "Khotan"),
    (r"^\(?m [ivx]+\b", "Shanshan (Miran, Niya, Loulan)"), (r"^\(?l [a-k]\b", "Shanshan (Miran, Niya, Loulan)"),
]
DE_MATERIALS = [("Tusche", "ink"), ("Farbe", "colour"), ("Seide", "silk"), ("Papier", "paper"), ("Hanf", "hemp"),
                ("Baumwolle", "cotton"), ("Wolle", "wool"), ("Holz", "wood"), ("Leinen", "linen"), ("Ton", "clay"),
                ("Bronze", "bronze"), ("Kupfer", "copper"), ("Stuck", "stucco"), ("Leder", "leather"),
                ("Gold", "gold"), ("Silber", "silver"), ("Stein", "stone"), (" auf ", " on "), (" und ", " and ")]


def idp_parse_results(text):
    if "Suchergebnisse" not in text and "SUCHERGEBNISSE" not in text:
        raise ValueError("not a result page")
    total = re.search(r"Gefundene Objekte:\s*(\d+)", text)
    rows = []
    for blk in re.findall(r'<td class="resultdetails">(.*?)</td>', text, re.S):
        inst = re.search(r'institute\.a4d\?id=\d+"[^>]*>([^<]*)</a>', blk)
        pm = re.search(r'oo_scroll_h\.a4d\?[^"]*recnum=(\d+)[^"]*">([^<]*)</a>', blk)
        fields = dict((k.strip(), tidy(v)) for k, v in re.findall(r"<br>\s*([^:<]+):\s*([^<]*)", blk))
        rows.append({"institution": tidy(inst.group(1)) if inst else "", "recnum": pm.group(1) if pm else "",
                     "pressmark": tidy(pm.group(2)) if pm else "", "site": fields.get("Fundort", ""),
                     "language": fields.get("Sprache(n)/Schrifte(n)", ""), "materials": fields.get("Materialien", "")})
    return {"total": int(total.group(1)) if total else None, "rows": rows}


class IdpSession:
    """Cookie session on the legacy IDP database; a predefined search per object
    form gives a result uid whose pages are read 50 at a time."""

    def __init__(self):
        import http.cookiejar
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.uid = {}

    def search(self, form):
        if form in self.uid:
            return self.uid[form]
        if _request(IDP + "/database/database_search.a4d", opener=self.opener) is None:
            return None
        boundary = uuid.uuid4().hex
        parts = [("f_pdSearchArtefact", "on"), ("f_pdSearchArtefactList", form), ("f_pdSearchSubmit", "SUBMIT")]
        body = "".join(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n' for k, v in parts)
        body = (body + f"--{boundary}--\r\n").encode()
        text = _request(IDP + "/database/search_wait.a4d", data=body, opener=self.opener,
                        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        m = re.search(r"search_results\.a4d\?uid=(\d+)", text or "")
        self.uid[form] = m.group(1) if m else None
        return self.uid[form]


def harvest_idp():
    rows, stats = {}, collections.Counter()
    sess = None
    for form, kind in IDP_FORMS.items():
        bst, total, n = 1, None, 0
        while total is None or bst <= total:
            path = os.path.join(RAW, "idp", f"{form}_{bst:05d}.json.gz")
            d = cache_read(path)
            if d is None:
                sess = sess or IdpSession()
                uid = sess.search(form)
                if not uid:
                    print(f"  IDP {kind}: search failed", file=sys.stderr)
                    stats["idp_unreachable"] += 1
                    break
                url = f"{IDP}/database/search_results.a4d?uid={uid}" + (f";bst={bst}" if bst > 1 else "")
                text = _request(url, opener=sess.opener)
                try:
                    d = idp_parse_results(text or "")
                except ValueError:
                    d = None
                if not d or (not d["rows"] and (d.get("total") or 0) >= bst):
                    sess.uid.pop(form, None)   # session expired: search again once
                    uid = sess.search(form)
                    text = _request(f"{IDP}/database/search_results.a4d?uid={uid};bst={bst}", opener=sess.opener) if uid else None
                    try:
                        d = idp_parse_results(text or "")
                    except ValueError:
                        d = None
                if not d:
                    print(f"  IDP {kind}: page at {bst} unreadable", file=sys.stderr)
                    break
                cache_write(path, d)
            total = d.get("total") or 0
            for r in d["rows"]:
                n += 1
                site = r["site"]
                if not site or re.match(r"(unbekannt|not applicable)", site, re.I):
                    stats["no_find_site"] += 1
                    continue
                key = f"{r['institution']}|{r['pressmark']}"
                if key in rows:
                    continue
                mats = r["materials"]
                for de, en in DE_MATERIALS:
                    mats = mats.replace(de, en)
                site_txt = site.replace("_", " ")
                for rx, reg in IDP_SITE_REGION:
                    if re.search(rx, fold(site_txt)):
                        site_txt += " | " + {"Shanshan (Miran, Niya, Loulan)": "Miran"}.get(reg, reg.split(" (")[0].split(" &")[0])
                row = {
                    "source": "idp", "id": key, "title": f"{kind} {r['pressmark']}",
                    "place_recorded": site.replace("_", " "), "tradition_recorded": r["language"],
                    "date_text": "", "date_begin": None, "date_end": None,
                    "object_type": kind, "medium": "painting" if kind == "painting" else (
                        "textile" if kind == "textile" else medium_of(mats) if mats else "other"),
                    "materials": mats, "makers": [], "lineage": "", "institution": r["institution"],
                    "language": r["language"], "url": f"{IDP}/database/oo_loader.a4d?pm={urllib.parse.quote(r['pressmark'])}",
                }
                lang_label = {"Tangutisch": "tangut", "Uigurisch": "uyghur", "Sogdisch": "sogdian",
                              "Khotansakisch": "khotan"}.get(r["language"], "")
                if classify(row, site_txt, site_txt + (" | " + lang_label if lang_label else "")):
                    rows[key] = row
                else:
                    stats["site_out_of_scope"] += 1
            bst += 50
            if not d["rows"]:
                break
        stats[kind] = n
        print(f"  IDP {kind}: {n} result rows read", file=sys.stderr)
    print(f"  IDP: {len(rows)} objects kept ({dict(stats)})", file=sys.stderr)
    return list(rows.values()), stats


# ----------------------------------------------------------- Met cross-check

def met_crosscheck():
    """tradition -> unattributed Met objects (top-level culture rows only)."""
    out = collections.Counter()
    if not os.path.exists(MET_CULTURES):
        return out
    with open(MET_CULTURES, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["kind"] != "culture" or r["parent"]:
                continue
            row = {"date_begin": to_int(r["begin_median"]), "date_end": to_int(r["end_median"])}
            lab = r["label"] + " | " + r["top_periods"].split(" (")[0]
            if match_region(r["label"]) and classify(row, r["label"], lab):
                out[row["tradition"]] += to_int(r["objects"]) or 0
    return out


# ------------------------------------------------------------------- outputs

OBJ_FIELDS = ["source", "id", "title", "region_group", "region", "country", "place_recorded", "tradition_recorded",
              "tradition", "traditions_all", "tradition_basis", "period", "period_basis", "date_text", "date_begin",
              "date_end", "object_type", "medium", "materials", "makers", "attributed", "lineage", "institution",
              "language", "overlap", "url"]
SOUTH_ASIA_OVERLAP = {"Nepal (Kathmandu Valley)", "Western Nepal (Mustang, Khasa)", "Bhutan", "Tibet", "Central Tibet",
                      "Western Tibet", "Eastern Tibet (Kham, Amdo)", "Ladakh & Western Himalaya", "Sikkim", "Kashmir",
                      "Gandhara", "Pakistan (other)"}


def top(counter, n=6):
    return "; ".join(f"{k} ({v})" for k, v in counter.most_common(n) if k)


def is_attributed(makers):
    return any(ATTRIBUTED_ROLES.match(role or "") and not re.match(r"style of|follower|circle|school of", role or "", re.I)
               for _, role in makers)


def write_outputs(rows, met):
    os.makedirs(OUT_DIR, exist_ok=True)
    for r in rows:
        r["attributed"] = 1 if is_attributed(r["makers"]) else 0
        r["overlap"] = "south_asia" if r["source"] in ("vam", "cma", "aic") and r["region"] in SOUTH_ASIA_OVERLAP else ""
    path = os.path.join(OUT_DIR, "himalaya_central_asia_objects.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OBJ_FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in sorted(rows, key=lambda x: (x["region_group"], x["region"], x["tradition"], x["source"], x["id"])):
            out = dict(r)
            out["makers"] = "; ".join(f"{n} [{role}]" if role else n for n, role in r["makers"])
            w.writerow(out)
    print(f"wrote {path} ({len(rows)} rows)", file=sys.stderr)

    def new():
        return {"n": 0, "src": collections.Counter(), "rec": 0, "att": 0, "begins": [], "ends": [], "mids": [],
                "types": collections.Counter(), "places": collections.Counter(), "makers": collections.Counter(),
                "regions": collections.Counter(), "groups": collections.Counter(), "ex": []}
    aggs = collections.defaultdict(new)
    for r in rows:
        for kind, key in (("tradition", (r["tradition"], "", "")),
                          ("tradition_period", (r["tradition"], r["period"], "")),
                          ("tradition_period_type", (r["tradition"], r["period"], r["medium"]))):
            a = aggs[(kind,) + key]
            a["n"] += 1
            a["src"][r["source"]] += 1
            a["rec"] += r["tradition_basis"] == "recorded"
            a["att"] += r["attributed"]
            if r["date_begin"] is not None:
                a["begins"].append(r["date_begin"])
            if r["date_end"] is not None:
                a["ends"].append(r["date_end"])
            m = mid_of(r["date_begin"], r["date_end"])
            if m is not None:
                a["mids"].append(m)
            a["types"][r["object_type"] or r["medium"]] += 1
            a["places"][r["place_recorded"]] += 1
            a["regions"][r["region"]] += 1
            a["groups"][r["region_group"]] += 1
            for n, role in r["makers"]:
                a["makers"][n] += 1
            if len(a["ex"]) < 5:
                a["ex"].append(f"{r['source']}:{r['id']}")

    def q(v, p):
        if not v:
            return ""
        v = sorted(v)
        return round(v[min(len(v) - 1, int(p * len(v)))])

    path = os.path.join(OUT_DIR, "himalaya_central_asia_traditions.csv")
    fields = (["kind", "region_group", "region", "tradition", "period", "medium", "objects"] +
              [f"objects_{s}" for s in SOURCES] +
              ["n_sources", "recorded_share", "attributed_objects", "attributed_share", "date_begin_min", "mid_p25",
               "mid_median", "mid_p75", "date_end_max", "top_object_types", "top_places", "top_regions",
               "named_makers", "met_unattributed_objects", "example_ids"])
    order = {"tradition": 0, "tradition_period": 1, "tradition_period_type": 2}
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for key in sorted(aggs, key=lambda k: (order[k[0]], -aggs[k]["n"] if k[0] == "tradition" else 0, k[1:])):
            a = aggs[key]
            kind, trad, period, med = key
            w.writerow([kind, a["groups"].most_common(1)[0][0], a["regions"].most_common(1)[0][0], trad, period, med,
                        a["n"]] + [a["src"][s] for s in SOURCES] +
                       [len(a["src"]), round(a["rec"] / a["n"], 3), a["att"], round(a["att"] / a["n"], 3),
                        min(a["begins"]) if a["begins"] else "", q(a["mids"], .25), q(a["mids"], .5), q(a["mids"], .75),
                        max(a["ends"]) if a["ends"] else "", top(a["types"]), top(a["places"], 4), top(a["regions"], 4),
                        top(a["makers"], 8), met.get(trad, "") if kind == "tradition" else "", " ".join(a["ex"])])
    print(f"wrote {path} ({len(aggs)} rows)", file=sys.stderr)

    mk = {}
    for r in rows:
        for n, role in r["makers"]:
            k = maker_key(n)
            if not k:
                continue
            m = mk.setdefault(k, {"name": collections.Counter(), "n": 0, "src": collections.Counter(),
                                  "roles": collections.Counter(), "trads": collections.Counter(),
                                  "regions": collections.Counter(), "periods": collections.Counter(),
                                  "begins": [], "ends": [], "ex": []})
            m["name"][n] += 1
            m["n"] += 1
            m["src"][r["source"]] += 1
            m["roles"][role or "artist"] += 1
            for t in r["traditions_all"].split("; "):
                m["trads"][t] += 1
            m["regions"][r["region"]] += 1
            m["periods"][r["period"]] += 1
            if r["date_begin"] is not None:
                m["begins"].append(r["date_begin"])
            if r["date_end"] is not None:
                m["ends"].append(r["date_end"])
            if len(m["ex"]) < 5:
                m["ex"].append(f"{r['source']}:{r['id']}")
    path = os.path.join(OUT_DIR, "himalaya_central_asia_makers.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["maker", "maker_key", "objects"] + [f"objects_{s}" for s in SOURCES] +
                   ["roles", "school", "traditions", "regions", "periods", "date_begin_min", "date_end_max",
                    "example_ids"])
        for k, m in sorted(mk.items(), key=lambda x: -x[1]["n"]):
            w.writerow([m["name"].most_common(1)[0][0], k, m["n"]] + [m["src"][s] for s in SOURCES] +
                       [top(m["roles"]), m["trads"].most_common(1)[0][0], top(m["trads"]), top(m["regions"], 4),
                        top(m["periods"], 4), min(m["begins"]) if m["begins"] else "",
                        max(m["ends"]) if m["ends"] else "", " ".join(m["ex"])])
    print(f"wrote {path} ({len(mk)} makers)", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skip", default="", help="comma-separated sources to skip: har,vam,cma,aic,idp")
    ap.add_argument("--har-max-items", type=int, default=0, help="cap on HAR item pages (0 = all items in the selected sets)")
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between requests (default 1.0)")
    ap.add_argument("--fetch-only", action="store_true", help="fill the cache, write nothing")
    args = ap.parse_args()
    DELAY[0] = args.delay
    skip = {s.strip() for s in args.skip.split(",") if s.strip()}
    harvesters = {"har": lambda: harvest_har(args.har_max_items), "vam": harvest_vam, "cma": harvest_cma,
                  "aic": harvest_aic, "idp": harvest_idp}
    rows, summary = [], {}
    for name in SOURCES:
        if name in skip:
            continue
        print(f"== {name}", file=sys.stderr)
        got, stats = harvesters[name]()
        rows += got
        summary[name] = len(got)
    print(f"network: {dict(NET)}", file=sys.stderr)
    if args.fetch_only:
        return
    met = met_crosscheck()
    write_outputs(rows, met)
    n = len(rows)
    att = sum(r["attributed"] for r in rows)
    print(f"objects per source: {summary}; total {n}; attributed {att} ({att / max(n, 1):.1%})", file=sys.stderr)
    for g in (HIM, CAS):
        sub = [r for r in rows if r["region_group"] == g]
        a = sum(r["attributed"] for r in sub)
        print(f"  {g}: {len(sub)} objects, attributed {a} ({a / max(len(sub), 1):.1%}), "
              f"recorded tradition {sum(r['tradition_basis'] == 'recorded' for r in sub)}", file=sys.stderr)


if __name__ == "__main__":
    main()
