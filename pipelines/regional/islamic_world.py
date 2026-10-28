"""Islamic-world regional sweep (visual-art-plan.md §2A, decision of 2026-10-28).

The Met CSV records no Period or Dynasty on Islamic Art objects, so
pipelines/unattributed/build_traditions.py infers the dynasty from culture plus
date (ISLAMIC_PERIODS). This script harvests collections that *record* the
dynasty or period, so their labels can override that inference:

  V&A Collections API v2 (api.vam.ac.uk, no key)
      Dynasty = the record's `styles` (Safavid, Qajar, Seljuk, Il-Khanid, ...).
      Sweeps: the whole Middle East Section (id_collection THES48607), the
      "Islam" category (THES48932), places of origin in the Islamic world from
      622 onwards, and keyword sweeps for Mughal, Deccani and Nasrid/al-Andalus
      work. Records from the place and keyword sweeps are kept only when they
      carry an Islamic dynasty style or were made in the Islamic world (Spain
      before 1500, South Asia 1206-1858 for the keyword sweeps). The API stops
      at 10,000 records per query, so the Middle East Section is read twice,
      ordered by date ascending and descending.
  Discover Islamic Art (Museum With No Frontiers, islamicart.museumwnf.org)
      Objects from ~100 partner museums, filed by dynasty through the JSON API
      behind its "Islamic Dynasties" pages (/dynasties-api/dynasties/<id>/objects).
      Each object page (database_item.php) adds holding museum, materials and
      technique, provenance and any named artist. The site has no robots.txt.
  Cleveland Museum of Art open access API, department "Islamic Art" in full,
      plus keyword sweeps for dynasty names (Islamic textiles sit in Textiles,
      Mughal and Deccani painting in Indian and Southeast Asian Art; keyword hits
      are kept only when the culture string names an Islamic dynasty).
      Dynasty is part of the `culture` string ("Iran, Seljuq period of Iran
      (1037-1194)"); makers come from `creators`.
  Harvard Art Museums API: used only when HARVARD_API_KEY is set (not
      implemented beyond the check; the sweep reports that it skipped it).

Every request is cached under data/raw/regional/<source>/ and spaced ~1 s
apart. Re-runs read the cache.

Recorded dynasty strings are normalised to a short list of names (Umayyad,
Abbasid, Fatimid, Seljuq, Ayyubid, Mamluk, Ilkhanid, Timurid, Safavid, Qajar,
Ottoman, Mughal, Nasrid, ...), keyed with the same fold() as the Met period
keys, so they line up with kind=period rows in data/interim/unattributed_cultures.csv.
Each object is also run through the Met-style inference (build_traditions'
ISLAMIC_PERIODS on its place of origin and mid date) and marked agree /
conflict / no_inference against its recorded dynasty.

Outputs (data/interim/regional/):
  islamic_objects.csv    one row per object: source, id, title, object type,
                         dynasty as recorded and normalised, culture/place, date
                         text + begin/end, makers, materials/technique, holding
                         institution, Met-style inferred dynasty and the check
  islamic_dynasties.csv  one row per normalised dynasty: objects per source,
                         date range, top object types / techniques / places,
                         named makers, agreement with the Met-style inference,
                         and the Met's own inferred count (met_inferred_objects)
  islamic_makers.csv     named makers (calligraphers, painters, potters, ...)
                         with object counts, sources, dynasties, dates and the
                         school they hang under (visual-art-plan.md §2.1 point 4);
                         the seed for a named-artist reference list for the region
  islamic_schools.csv    kind=school: schools / workshops (Timurid Herat, Safavid
                         Tabriz, Imperial Mughal atelier, Ottoman nakkashane,
                         Deccani, Company school, ...) as recorded, or for book
                         arts from the recorded painting centre (see
                         assign_school); kind=centre: production centres for all
                         objects. Both with attributed share and named masters.

Attributed share = objects with at least one named maker / all objects (the
attribution profile of §2.1 point 4 and the §2.2 coverage audit), per dynasty,
per school and for book arts separately.

Usage: python3 pipelines/regional/islamic_world.py [--skip vam,dia,cma]
           [--no-dia-details] [--delay 1.0]
"""
import argparse
import collections
import csv
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

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw", "regional")
OUT_DIR = os.path.join(ROOT, "data", "interim", "regional")
MET_CULTURES = os.path.join(ROOT, "data", "interim", "unattributed_cultures.csv")
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"

sys.path.insert(0, os.path.join(ROOT, "pipelines", "unattributed"))
from build_traditions import ISLAMIC_PERIODS, fold  # noqa: E402

VAM_API = "https://api.vam.ac.uk/v2/objects/search"
VAM_OBJECT_URL = "https://collections.vam.ac.uk/item/{}/"
VAM_MAX = 10000          # the API refuses page * page_size beyond this
VAM_PAGE = 100
DIA_API = "https://islamicart.museumwnf.org/dynasties-api"
DIA_SITE = "https://islamicart.museumwnf.org/"
CMA_API = "https://openaccess-api.clevelandart.org/api/artworks/"

# --------------------------------------------------------------------- fetching

_last = [0.0]
DELAY = [1.0]


def fetch(url, path):
    """GET url, caching the body at path. Returns text, or None on a hard error."""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for attempt in range(4):
        wait = DELAY[0] - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json, text/html"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
            text = raw.decode("utf-8", errors="replace")
            with open(path + ".part", "w", encoding="utf-8") as f:
                f.write(text)
            os.replace(path + ".part", path)
            return text
        except urllib.error.HTTPError as e:
            if e.code in (400, 404, 422):
                print(f"  {e.code} {url}", file=sys.stderr)
                return None
            print(f"  {e.code} {url} (retry {attempt + 1})", file=sys.stderr)
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            print(f"  {e} {url} (retry {attempt + 1})", file=sys.stderr)
        except ValueError as e:   # malformed URL: no point retrying
            print(f"  {e}", file=sys.stderr)
            return None
        except Exception as e:    # IncompleteRead, RemoteDisconnected, ...
            print(f"  {type(e).__name__}: {e} {url} (retry {attempt + 1})", file=sys.stderr)
        time.sleep(5 * (attempt + 1))
    return None


def fetch_json(url, path):
    text = fetch(url, path)
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        os.remove(path)
        return None


def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")[:120]


# ---------------------------------------------------------- dynasty normalising

# (regex on the folded string, normalised name). Order matters: specific first.
DYNASTY_PATTERNS = [
    (r"umayyads? (of|in) (al-andalus|spain|cordoba)|spanish umayyad|caliphate of cordoba|cordoban caliph", "Umayyad (Spain)"),
    (r"almoravid|almohad", "Almoravid and Almohad"),
    (r"nasrid", "Nasrid"),
    (r"\btaifa", "Taifa"),
    (r"mudejar", "Mudejar"),
    (r"marinid|wattasid", "Marinid"),
    (r"saadi", "Saadian"),
    (r"\balawi(te|d)s?\b", "Alawite (Morocco)"),
    (r"hafsid", "Hafsid"),
    (r"\bzirid", "Zirid"),
    (r"hammadid", "Hammadid"),
    (r"aghlabid", "Aghlabid"),
    (r"idrisid", "Idrisid"),
    (r"rustamid", "Rustamid"),
    (r"siculo.?norman|norman sicily", "Siculo-Norman"),
    (r"crusader", "Crusader"),
    (r"tulunid", "Tulunid"),
    (r"ikhshidid", "Ikhshidid"),
    (r"fatimid", "Fatimid"),
    (r"ayyubid", "Ayyubid"),
    (r"mamluk|mameluke|mamluke", "Mamluk"),
    (r"zangid|zengid", "Zangid"),
    (r"artuqid|artukid", "Artuqid"),
    (r"marwanid", "Marwanid"),
    (r"umayyad|omayyad", "Umayyad"),
    (r"abbasid|abbaside", "Abbasid"),
    (r"samanid", "Samanid"),
    (r"ghaznavid|ghaznevid", "Ghaznavid"),
    (r"ghurid", "Ghurid"),
    (r"buyid|buwayhid", "Buyid"),
    (r"khwarazm", "Khwarazmshah"),
    (r"sel[cjg]uk|seljuq|saljuq|seldjuk|seljouk", "Seljuq"),
    (r"il-?khanid|ilkhan", "Ilkhanid"),
    (r"jalayirid", "Jalayirid"),
    (r"muzaffarid", "Muzaffarid"),
    (r"inju(id)?\b", "Injuid"),
    (r"golden horde", "Golden Horde"),
    (r"timurid", "Timurid"),
    (r"aq ?qoyunlu|ak ?koyunlu|aqqoyunlu", "Aq Qoyunlu"),
    (r"qara ?qoyunlu|kara ?koyunlu", "Qara Qoyunlu"),
    (r"turkman|turkoman", "Turkman"),
    (r"shaybanid|shaibanid", "Shaybanid"),
    (r"safavid|safawid|safavi\b", "Safavid"),
    (r"afsharid|afshar\b", "Afsharid"),
    (r"\bzand\b", "Zand"),
    (r"qajar|kajar", "Qajar"),
    (r"pahlavi", "Pahlavi"),
    (r"qaramanid|karamanid", "Qaramanid"),
    (r"aydin|aydinid", "Aydinid"),
    (r"menteshe|mentese", "Menteshe"),
    (r"mengujekid|mengucek", "Mengujekid"),
    (r"ottoman|osmanli", "Ottoman"),
    (r"muhammad ali|mohammed ali|alawiyya", "Muhammad Ali dynasty"),
    (r"delhi sultanate|tughluq|khalji|lodi\b", "Delhi Sultanate"),
    (r"deccan|bijapur|golconda|adil shahi|qutb shahi|nizam shahi|ahmadnagar|bahmani", "Deccani sultanates"),
    (r"asaf jahi|nizams? of hyderabad", "Asaf Jahi"),
    (r"mughal|mogul|moghul", "Mughal"),
    (r"oudh|awadh|nawabs? of lucknow", "Awadh"),
    (r"mysore", "Mysore"),
    (r"busaid", "Al Busaid"),
    (r"early islamic", "Early Islamic"),
    (r"sasanian|sassanian|sasanid|sassanid", "Sasanian"),
    (r"\bqing\b", "Qing"),
]
DYNASTY_RE = [(re.compile(p), n) for p, n in DYNASTY_PATTERNS]


def norm_dynasties(text, place_bases=()):
    """All normalised dynasty names found in a recorded string (in order)."""
    t2 = fold(text) if text else ""
    t = t2.replace("-", " ")
    out = []
    for rx, name in DYNASTY_RE:
        if rx.search(t2) or rx.search(t):
            if name == "Umayyad" and ("Umayyad (Spain)" in out or "spanish" in place_bases):
                name = "Umayyad (Spain)"
            if name not in out:
                out.append(name)
    if "Umayyad (Spain)" in out and "Umayyad" in out:
        out.remove("Umayyad")
    return out


# ------------------------------------------------------------- place -> Met key

PLACE_BASE = [
    ("iranian", "iran persia persian isfahan esfahan kashan tabriz shiraz tehran teheran kirman kerman yazd "
                "mashhad meshed nishapur neyshabur nishapour rayy rey ray khorasan khurasan gurgan gorgan "
                "sultanabad qum qom hamadan fars mazandaran soltaniyeh sultaniyya qazvin kurdistan "
                "azerbaijan caucasus caucasian"),
    ("iraqi", "iraq baghdad mosul basra samarra karbala kufa"),
    ("syrian", "syria damascus aleppo raqqa hama"),
    ("egyptian", "egypt cairo fustat alexandria"),
    ("turkish", "turkey turkiye anatolia istanbul constantinople iznik bursa konya kutahya hereke ushak usak "
                "edirne diyarbakir"),
    ("central asia", "central asia uzbekistan samarkand samarqand bukhara khiva turkmenistan tajikistan merv "
                     "transoxiana kyrgyzstan kazakhstan"),
    ("afghan", "afghanistan herat ghazni kabul balkh"),
    ("indian", "india delhi agra fatehpur deccan golconda bijapur hyderabad lucknow mysore gujarat bengal "
               "kashmir rajasthan ahmadabad burhanpur murshidabad ahmadnagar avadh oudh mughal"),
    ("pakistani", "pakistan lahore sindh multan"),
    ("spanish", "spain andalus granada malaga cordoba seville valencia manises murcia almeria"),
    ("moroccan", "morocco fez fes marrakesh marrakech rabat meknes"),
    ("algerian", "algeria algiers tlemcen"),
    ("tunisian", "tunisia tunis kairouan qayrawan mahdia"),
    ("palestinian", "palestine jerusalem"),
    ("lebanese", "lebanon tripoli beirut"),
    ("arabian", "arabia saudi yemen oman mecca medina hijaz"),
    ("libyan", "libya"),
]
_PLACE_TOKENS = [(base, set(words.split())) for base, words in PLACE_BASE]


def place_bases(text):
    t = fold(text).replace(",", " ").replace("-", " ")
    toks = set(t.split())
    out = []
    if "central asia" in t:
        out.append("central asia")
    for base, words in _PLACE_TOKENS:
        if toks & words and base not in out:
            out.append(base)
    return out


ISLAMIC_BASES = {"iranian", "iraqi", "syrian", "egyptian", "turkish", "central asia", "afghan",
                 "moroccan", "algerian", "tunisian", "palestinian", "lebanese", "arabian", "libyan"}


def met_infer(bases, begin, end):
    """build_traditions.infer_islamic_period on place bases instead of Met cultures."""
    if begin is None or end is None:
        return None
    mid = (begin + end) / 2
    b = set(bases)
    for cultures, start, stop, name in ISLAMIC_PERIODS:
        if b & cultures and start <= mid <= stop:
            return name
    return None


# ------------------------------------------------------------ technique tokens

TECHNIQUES = [
    ("lustre", r"lustre|luster"),
    ("mina'i / overglaze", r"mina.?i|overglaze|enamel(l)?ed glaze"),
    ("underglaze", r"underglaze|under.glaze"),
    ("blue-and-white", r"blue.and.white"),
    ("cuerda seca", r"cuerda seca"),
    ("lajvardina", r"lajvardina"),
    ("slip-painted", r"slip"),
    ("sgraffito", r"sgraffiato|sgraffito|incised under"),
    ("stonepaste / fritware", r"stonepaste|fritware|frit\b|quartz.?paste"),
    ("earthenware", r"earthenware"),
    ("enamelled glass", r"glass.*enamel|enamel.*glass"),
    ("gilded", r"gild|gilt"),
    ("inlaid metal", r"inlai?d with (silver|gold|copper)|silver inlay|gold inlay|damascen|koftgari|bidri"),
    ("enamel", r"enamel"),
    ("engraved", r"engrav|chased"),
    ("cast", r"\bcast\b"),
    ("repousse", r"repouss"),
    ("carved", r"carv"),
    ("mother-of-pearl / inlay", r"mother.of.pearl|marquetry|khatam|inlay"),
    ("lacquer", r"lacquer"),
    ("knotted pile", r"knotted|pile\b|carpet"),
    ("tapestry / kilim", r"tapestry|kilim|slit.weave"),
    ("lampas / compound weave", r"lampas|samite|compound weave|taqueté|brocad|velvet"),
    ("tiraz", r"tiraz"),
    ("embroidered", r"embroider"),
    ("printed / block-printed", r"block.print|resist.dye|printed cotton|painted cotton|kalamkari"),
    ("ink and opaque watercolour", r"opaque watercolou?r|gouache|ink.*colou?r|colou?r.*ink|pigment"),
    ("calligraphy", r"calligraph|nasta.?liq|naskh|kufic|thuluth"),
    ("illumination", r"illuminat"),
    ("ink on paper", r"ink on paper"),
    ("parchment", r"parchment|vellum"),
    ("rock crystal", r"rock crystal"),
    ("ivory", r"ivory"),
    ("stucco", r"stucco"),
    ("jade", r"\bjade\b|nephrite"),
    ("oil painting", r"oil on|oil paint"),
    ("photography", r"albumen|photograph|gelatin silver"),
    ("lithograph", r"lithograph"),
]
TECH_RE = [(n, re.compile(p, re.I)) for n, p in TECHNIQUES]


def technique_keys(text):
    if not text:
        return []
    return [n for n, rx in TECH_RE if rx.search(text)]


# object type from a free-text name (Discover Islamic Art has no type field)
TYPE_WORDS = [
    ("Qur'an", r"qur.?an|koran"), ("manuscript", r"manuscript|codex"), ("album page", r"album"),
    ("folio", r"folio|page from|leaf"), ("calligraphy", r"calligraph"), ("painting", r"painting|miniature|portrait"),
    ("tile", r"\btiles?\b|tile panel"), ("bowl", r"\bbowl"), ("dish", r"\bdish"), ("plate", r"\bplate\b"),
    ("jar", r"\bjar\b|albarello"), ("ewer", r"\bewer"), ("jug", r"\bjug"), ("bottle", r"bottle"),
    ("vase", r"\bvase"), ("cup", r"\bcup\b|beaker|goblet"), ("basin", r"basin"), ("tray", r"\btray"),
    ("candlestick", r"candlestick|candle.?holder"), ("lamp", r"\blamp"), ("incense burner", r"incense"),
    ("box", r"\bbox|casket|pyxis|chest"), ("pen box", r"pen.?box|qalamdan"), ("mirror", r"mirror"),
    ("astrolabe", r"astrolabe"), ("coin", r"\bcoin|dinar|dirham"), ("textile", r"textile|fabric|silk|tiraz"),
    ("carpet", r"carpet|rug\b|kilim"), ("garment", r"robe|kaftan|caftan|coat|tunic|shirt|cap\b|turban"),
    ("tombstone", r"tombstone|stele|stela|epitaph|funerary"), ("inscription", r"inscription"),
    ("capital", r"\bcapital"), ("column", r"column"), ("panel", r"\bpanel"), ("door", r"\bdoor"),
    ("minbar", r"minbar"), ("mihrab", r"mihrab"), ("window", r"window|grille|screen"),
    ("sword", r"sword|sabre|scimitar|blade"), ("dagger", r"dagger|knife"), ("helmet", r"helmet"),
    ("armour", r"armou?r|shield|mail\b"), ("jewellery", r"jewel|ring\b|earring|necklace|bracelet|pendant"),
    ("fragment", r"fragment"), ("mosque lamp", r"mosque lamp"),
]
TYPE_RE = [(n, re.compile(p, re.I)) for n, p in TYPE_WORDS]


def type_from_name(name):
    for n, rx in TYPE_RE:
        if rx.search(name or ""):
            return n
    return ""


# ------------------------------------------------------------------ makers

PLACEHOLDER_MAKER = re.compile(
    r"^(unknown|unidentified|anonymous|not known|various|unrecorded|n/?a|none)\b", re.I)


def maker_key(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"\b(attributed to|attrib\.?|probably|possibly|workshop of|school of|style of|follower of|circle of)\b", " ", s)
    s = re.sub(r"[`'’ʿʾ‘\-\.]", "", s)
    s = re.sub(r"[^a-z ,]", " ", s)
    if "," in s:   # "Isfahani, Ali Muhammad" -> "ali muhammad isfahani"
        a, _, b = s.partition(",")
        s = f"{b} {a}"
    s = " ".join(s.split())
    for a, b in (("riza", "reza"), ("rizayi", "reza"), ("rezayi", "reza"), ("mohammad", "muhammad"),
                 ("mohammed", "muhammad"), ("muhammed", "muhammad"), ("mehmed", "muhammad"),
                 ("bihzad", "behzad"), ("bihzād", "behzad"), ("abbassi", "abbasi"), ("husain", "husayn"),
                 ("hussein", "husayn"), ("hosein", "husayn"), ("hossein", "husayn"), ("mir ", "mir ")):
        s = re.sub(rf"\b{a}\b", b, s)
    s = re.sub(r"\byi\b", "", s)
    return " ".join(s.split())


# --------------------------------------------------------------------- V&A

VAM_PLACES = ["Iran", "Persia", "Turkey", "Egypt", "Syria", "Iraq", "Uzbekistan", "Afghanistan", "Azerbaijan",
              "Central Asia", "Turkmenistan", "Morocco", "Tunisia", "Algeria", "Palestine", "Jerusalem",
              "Lebanon", "Yemen", "Arabia"]
# South Asian (1206-1858) and Iberian (711-1500) places, filtered again in vam_keep
VAM_PLACES_SOUTH_ASIA = ["Mughal Empire", "Deccan", "Bijapur", "Golconda", "Hyderabad", "Ahmadnagar", "Lucknow",
                         "Murshidabad", "Lahore", "Agra", "Delhi", "Kashmir"]
VAM_PLACES_SPAIN = ["Granada", "Malaga", "Valencia", "Manises", "Cordoba", "Spain"]
# Persian, Central Asian and Ottoman book-painting and production centres (622-1950)
VAM_PLACES_CENTRES = ["Herat", "Tabriz", "Shiraz", "Isfahan", "Qazvin", "Mashhad", "Bukhara", "Samarkand",
                      "Baghdad", "Istanbul", "Kashan"]
VAM_KEYWORDS = ["Mughal", "Deccan", "Deccani", "Nasrid", "Hispano-Moresque", "al-Andalus", "Mudejar",
                "Mamluk", "Ottoman", "Safavid", "Timurid", "Fatimid", "Seljuk", "Qajar", "Iznik"]
VAM_SECTION = "THES48607"      # Middle East Section
VAM_ISLAM_CAT = "THES48932"    # category "Islam"


def vam_query(label, params, orders=((None, None),)):
    """Page through a V&A search, possibly in several orders. Yields records."""
    for order_by, order_sort in orders:
        page = 1
        while True:
            p = dict(params, page_size=VAM_PAGE, page=page, data_profile="full")
            if order_by:
                p.update(order_by=order_by, order_sort=order_sort)
            url = VAM_API + "?" + urllib.parse.urlencode(p)
            tag = f"{label}_{order_by or 'default'}_{order_sort or ''}_p{page:03d}"
            d = fetch_json(url, os.path.join(RAW, "vam", slug(label), slug(tag) + ".json"))
            if not d or not d.get("records"):
                break
            yield from d["records"]
            info = d.get("info", {})
            if page >= info.get("pages", 0) or page * VAM_PAGE >= VAM_MAX:
                if info.get("record_count", 0) > VAM_MAX and order_by is None:
                    print(f"  V&A {label}: {info.get('record_count')} records, capped at {VAM_MAX}", file=sys.stderr)
                break
            page += 1


def vam_year(s):
    m = re.match(r"(-?\d{1,4})", s or "")
    return int(m.group(1)) if m else None


def vam_row(r):
    styles = [s.get("text", "") for s in r.get("styles") or [] if s.get("text")]
    places = r.get("placesOfOrigin") or []
    made = [p["place"]["text"] for p in places if p.get("place", {}).get("text")
            and (p.get("association", {}).get("text", "") in ("made", "", "probably made", "possibly made"))]
    place_txt = "; ".join(dict.fromkeys(made or [p["place"]["text"] for p in places if p.get("place", {}).get("text")]))
    dates = r.get("productionDates") or []
    dtext, begin, end = "", None, None
    if dates:
        d = dates[0].get("date", {})
        dtext, begin, end = d.get("text", ""), vam_year(d.get("earliest")), vam_year(d.get("latest"))
    makers = []
    for m in (r.get("artistMakerPerson") or []) + (r.get("artistMakerOrganisations") or []):
        n = (m.get("name") or {}).get("text", "").strip()
        if n and not PLACEHOLDER_MAKER.match(n):
            role = (m.get("association") or {}).get("text", "")
            makers.append((n, role))
    titles = [t.get("title", "") for t in r.get("titles") or [] if t.get("title")]
    mats = r.get("materialsAndTechniques") or "; ".join(
        [x.get("text", "") for x in (r.get("materials") or []) + (r.get("techniques") or [])])
    tech_list = [x.get("text", "") for x in (r.get("techniques") or []) + (r.get("materials") or [])]
    bases = place_bases(place_txt)
    return {
        "source": "vam", "id": r.get("systemNumber", ""),
        "title": titles[0] if titles else (r.get("objectType") or ""),
        "object_type": r.get("objectType") or "",
        "dynasty_recorded": "; ".join(styles),
        "dynasties": norm_dynasties("; ".join(styles), bases),
        "culture_place": place_txt, "bases": bases,
        "date_text": dtext, "date_begin": begin, "date_end": end,
        "makers": makers, "materials_technique": mats,
        "techniques": technique_keys(mats + " " + " ".join(tech_list)),
        "institution": "Victoria and Albert Museum",
        "collection": (r.get("collectionCode") or {}).get("text", ""),
        "url": VAM_OBJECT_URL.format(r.get("systemNumber", "")),
        "school_text": " | ".join(styles + [(r.get("production") or "")[:600]]),
        "centre_text": place_txt,
    }


# normalised labels that are not Islamic dynasties (kept as recorded, but they do
# not by themselves admit an object to the Islamic-world set)
NON_ISLAMIC_LABELS = {"Sasanian", "Qing", "Crusader", "Siculo-Norman"}
PRE_ISLAMIC_STYLE = re.compile(r"late antique|coptic|roman|ancient|byzantine|kingdom|dynastic|ptolemaic|"
                               r"sasanian|sassanian|parthian|seleucid|hellenistic|pharaonic|\btang\b|\bsong\b|\bliao\b", re.I)


DOCUMENTARY_TYPE = re.compile(r"sketchbook|photograph|negative|print|drawing|watercolou?r|lantern slide|postcard|"
                              r"cast|model|architectural|design|book\b|map\b", re.I)


def islamic_dynasties(row):
    return [d for d in row["dynasties"] if d not in NON_ISLAMIC_LABELS]


def vam_keep(row, sweep):
    """Section/category sweeps keep everything made from 622 on (the Middle East
    Section also holds Coptic, Late Antique and Pharaonic material, which is
    dropped); place and keyword sweeps are filtered."""
    b, e = row["date_begin"], row["date_end"]
    mid = (b + e) / 2 if b is not None and e is not None else None
    if islamic_dynasties(row):
        return True
    # 19th/20th-century documentation of the region (James William Wild's Cairo
    # sketchbooks, photographs, prints) is about Islamic art, not of it
    if DOCUMENTARY_TYPE.search(row["object_type"] or "") and mid is not None and mid >= 1780:
        return False
    if sweep in ("section", "islam"):
        if PRE_ISLAMIC_STYLE.search(row["dynasty_recorded"] or ""):
            return False
        return mid is None or mid >= 622
    bases = set(row["bases"])
    if PRE_ISLAMIC_STYLE.search(row["dynasty_recorded"] or ""):
        return False
    if bases & ISLAMIC_BASES and (mid is None or mid >= 622):
        return True
    south_asia = ("Mughal", "Deccan", "Deccani") + tuple(VAM_PLACES_SOUTH_ASIA)
    if sweep in south_asia and bases & {"indian", "pakistani"} and mid and 1206 <= mid <= 1858:
        return True
    spain = ("Nasrid", "Hispano-Moresque", "al-Andalus", "Mudejar") + tuple(VAM_PLACES_SPAIN)
    if sweep in spain and "spanish" in bases and mid and 711 <= mid <= 1500:
        return True
    return False


def harvest_vam():
    rows = {}
    stats = collections.Counter()
    sweeps = [("section", {"id_collection": VAM_SECTION}, (("date", "asc"), ("date", "desc"))),
              ("islam", {"id_category": VAM_ISLAM_CAT}, ((None, None),))]
    sweeps += [(p, {"q_place_name": p, "year_made_from": 622, "year_made_to": 1950}, ((None, None),)) for p in VAM_PLACES]
    for places, y0, y1 in ((VAM_PLACES_SOUTH_ASIA, 1206, 1858), (VAM_PLACES_SPAIN, 711, 1500),
                           (VAM_PLACES_CENTRES, 622, 1950)):
        sweeps += [(p, {"q_place_name": p, "year_made_from": y0, "year_made_to": y1}, ((None, None),))
                   for p in places]
    # "Mughal" matches ~17,400 records, over the 10,000 cap: read it in both date orders
    sweeps += [(k, {"q": k}, (("date", "asc"), ("date", "desc")) if k == "Mughal" else ((None, None),))
               for k in VAM_KEYWORDS]
    for sweep, params, orders in sweeps:
        n = kept = 0
        for rec in vam_query(sweep, params, orders):
            n += 1
            sid = rec.get("systemNumber")
            if not sid or sid in rows:
                continue
            row = vam_row(rec)
            if vam_keep(row, sweep):
                row["sweep"] = sweep
                rows[sid] = row
                kept += 1
        stats[sweep] = kept
        print(f"  V&A {sweep}: {n} records read, {kept} new kept", file=sys.stderr)
    return list(rows.values()), stats


# ------------------------------------------------------- Discover Islamic Art

DIA_LABELS = ("Name of Object", "Location", "Holding Museum", "Date of Object", "Museum Inventory Number",
              "Material(s) / Technique(s)", "Dimensions", "Period / Dynasty", "Provenance", "Artist",
              "Artist(s)", "Calligrapher", "Calligrapher(s)", "Architect", "Master", "Maker", "Patron",
              "Patron(s)", "Description", "Workshop", "Painter", "Craftsman", "Signed")


def dia_item_fields(page):
    s = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", "", page)
    s = re.sub(r"(?i)<br\s*/?>", " ", s)
    t = html.unescape(re.sub(r"<[^>]+>", "\n", s))
    lines = [ln.strip() for ln in t.split("\n") if ln.strip()]
    fields = {}
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.endswith(":") and len(ln) < 60:
            label = ln[:-1].strip()
            vals = []
            j = i + 1
            while j < len(lines) and not (lines[j].endswith(":") and len(lines[j]) < 60):
                vals.append(lines[j])
                j += 1
                if label != "Description" and len(vals) >= 3:
                    break
            if label not in fields:
                fields[label] = " ".join(vals) if label != "Description" else " ".join(vals)[:400]
            i = j
        else:
            i += 1
    return fields


def dia_key(url):
    m = re.search(r"id=([^&]+)", url)
    parts = m.group(1).split(";") if m else []
    return ";".join(parts[:5]) if parts else url


def harvest_dia(details=True):
    dyns = fetch_json(DIA_API + "/dynasties", os.path.join(RAW, "dia", "dynasties.json")) or []
    objs = {}
    for d in dyns:
        did = d["dynastyId"]
        dname = next((n["name"] for n in d["dynastyName"] if n["langId"] == "en"), str(did))
        page, total = 1, 0
        while True:
            data = fetch_json(f"{DIA_API}/dynasties/{did}/objects?page={page}",
                              os.path.join(RAW, "dia", "dynasty_objects", f"d{did:03d}_p{page:03d}.json"))
            if not data:
                break
            for o in data.get("data", []):
                en = next((x for x in o.get("details", []) if x.get("langId") == "en"), None)
                if not en:
                    en = (o.get("details") or [{}])[0]
                key = dia_key(en.get("objectUrl", "")) or str(o.get("objectId"))
                ent = objs.setdefault(key, {"en": en, "dynasty_lists": [], "objectId": o.get("objectId")})
                if dname not in ent["dynasty_lists"]:
                    ent["dynasty_lists"].append(dname)
            meta = data.get("meta", {})
            total = meta.get("total", total)
            if page >= meta.get("last_page", 1):
                break
            page += 1
        print(f"  DIA {dname}: {total} objects", file=sys.stderr)
    rows = []
    n_detail = 0
    for key, ent in objs.items():
        en = ent["en"]
        f = {}
        url = urllib.parse.urljoin(DIA_SITE, (en.get("objectUrl") or "").replace("&pageD=N", ""))
        if details and url:
            page = fetch(url, os.path.join(RAW, "dia", "items", slug(key) + ".html"))
            if page:
                f = dia_item_fields(page)
                n_detail += 1
        recorded = f.get("Period / Dynasty") or en.get("dynasty") or "; ".join(ent["dynasty_lists"])
        place = "; ".join(x for x in (f.get("Provenance", ""), en.get("countryName", "")) if x)
        bases = place_bases(f.get("Provenance", "")) or place_bases(en.get("countryName", ""))
        dyn = norm_dynasties(recorded, bases) or norm_dynasties("; ".join(ent["dynasty_lists"]), bases)
        makers = []
        for lab, val in f.items():
            if re.match(r"(Artist|Calligrapher|Architect|Master|Maker|Painter|Craftsman|Workshop)", lab) and val:
                for n in re.split(r";| and (?=[A-Z])", val):
                    n = n.strip(" .,")
                    if n and not PLACEHOLDER_MAKER.match(n) and len(n) < 120:
                        makers.append((n, re.sub(r"\(s\)$", "", lab.lower())))

        def yr(x):
            try:
                return int(x)
            except (TypeError, ValueError):
                return None
        name = (f.get("Name of Object") or en.get("name") or "").strip(" .")
        mats = f.get("Material(s) / Technique(s)", "")
        rows.append({
            "source": "dia", "id": key, "title": name,
            "object_type": type_from_name(name), "dynasty_recorded": recorded, "dynasties": dyn,
            "culture_place": place, "bases": bases,
            "date_text": f.get("Date of Object") or en.get("dateDescription", ""),
            "date_begin": yr(en.get("startDate")), "date_end": yr(en.get("endDate")),
            "makers": makers, "materials_technique": mats,
            "techniques": technique_keys(mats + " " + name),
            "institution": re.split(r" About ", f.get("Holding Museum", ""))[0].strip(),
            "collection": en.get("countryName", ""),
            "url": url, "sweep": "dynasty pages",
            "school_text": " | ".join(v for k, v in f.items() if re.match(r"(Workshop|Provenance|How provenance)", k)),
            "centre_text": f.get("Provenance", ""),
        })
    print(f"  DIA: {len(rows)} unique objects, {n_detail} object pages read", file=sys.stderr)
    return rows, collections.Counter(dia=len(rows))


# --------------------------------------------------------------- Cleveland

CMA_KEYWORDS = ["Umayyad", "Abbasid", "Fatimid", "Seljuq", "Ayyubid", "Mamluk", "Ilkhanid", "Timurid",
                "Safavid", "Qajar", "Ottoman", "Mughal", "Nasrid", "Deccan", "Samanid", "Buyid", "Ghaznavid",
                "Zand", "Turkman", "Shaybanid", "Jalayirid", "Almohad", "Hispano-Moresque"]


def cma_pages(label, params):
    skip, limit = 0, 100
    while True:
        url = CMA_API + "?" + urllib.parse.urlencode(dict(params, skip=skip, limit=limit))
        name = "islamic_art" if label == "Islamic Art" else "q_" + slug(label)
        d = fetch_json(url, os.path.join(RAW, "cma", f"{name}_{skip:05d}.json"))
        if not d or not d.get("data"):
            break
        yield from d["data"]
        total = d.get("info", {}).get("total", 0)
        skip += limit
        if skip >= total:
            break


def cma_row(r, sweep):
    cult = "; ".join(r.get("culture") or [])
    place = "; ".join(c.split(",")[0].strip() for c in (r.get("culture") or []))
    bases = place_bases(place)
    makers = []
    for c in r.get("creators") or []:
        desc = c.get("description") or ""
        n = desc.split(" (")[0].strip()
        if n and not PLACEHOLDER_MAKER.match(n):
            makers.append((n, c.get("role") or ""))
    tech = r.get("technique") or ""
    return {
        "source": "cma", "id": r.get("accession_number") or str(r.get("id")),
        "title": r.get("title") or "", "object_type": r.get("type") or "",
        "dynasty_recorded": cult, "dynasties": norm_dynasties(cult, bases),
        "culture_place": cult, "bases": bases,
        "date_text": r.get("creation_date") or "",
        "date_begin": r.get("creation_date_earliest"), "date_end": r.get("creation_date_latest"),
        "makers": makers, "materials_technique": tech,
        "techniques": technique_keys(tech + " " + (r.get("title") or "")),
        "institution": "Cleveland Museum of Art", "collection": r.get("department") or "",
        "url": r.get("url") or "", "sweep": sweep,
        "school_text": cult,
        "centre_text": cult,
    }


def harvest_cma():
    """Department "Islamic Art" in full, plus keyword sweeps for dynasty names
    (Islamic textiles sit in Textiles, Mughal and Deccani painting in Indian and
    Southeast Asian Art). Keyword hits are kept only when the culture string
    itself names an Islamic dynasty."""
    rows = {}
    sweeps = [("Islamic Art", {"department": "Islamic Art"})] + [(k, {"q": k}) for k in CMA_KEYWORDS]
    for sweep, params in sweeps:
        n = kept = 0
        for r in cma_pages(sweep, params):
            n += 1
            row = cma_row(r, sweep)
            if row["id"] in rows:
                continue
            if sweep == "Islamic Art" or islamic_dynasties(row):
                rows[row["id"]] = row
                kept += 1
        print(f"  CMA {sweep}: {n} records read, {kept} new kept", file=sys.stderr)
    print(f"  CMA: {len(rows)} objects", file=sys.stderr)
    return list(rows.values()), collections.Counter(cma=len(rows))


# --------------------------------------------------------- schools / workshops
#
# Islamic book painting is tradition-led (visual-art-plan.md §2.1 point 4): the
# primary nodes are schools and workshops, with named masters under them. A
# school is taken from what the record says, in this order:
#   recorded  an explicit court / workshop / school phrase in the dynasty or
#             style field, the culture string (Cleveland: "India, Mughal, court
#             of Akbar"), V&A production notes or a Discover Islamic Art
#             Workshop / provenance field;
#   place     for book arts only (paintings, manuscripts, album pages,
#             calligraphy, drawings), the recorded place of production when it
#             is one of the painting centres below, named "<dynasty> <city>"
#             (Timurid Herat, Safavid Tabriz, ...); when the record has no
#             dynasty the Met-style inferred one is used ("place, dynasty
#             inferred").
# Production centres (Iznik, Kashan, Herat, ...) are also kept for every object.

BOOK_ARTS_RE = re.compile(r"painting|miniature|manuscript|album|folio|calligraph|qur.?an|koran|drawing|"
                          r"illuminat|\bpage\b|\bbook\b|muraqqa|qit.?a\b|portrait|\bleaf\b|shahnam|khamsa", re.I)

CENTRES = [  # (regex on folded place text, centre name, painting school family)
    (r"\bherat\b", "Herat"), (r"\btabriz\b", "Tabriz"), (r"\bshiraz\b", "Shiraz"),
    (r"\b(isfahan|esfahan|ispahan)\b", "Isfahan"), (r"\bqazvin\b|\bkazvin\b", "Qazvin"),
    (r"\b(mashhad|meshed|mashad)\b", "Mashhad"), (r"\b(bukhara|bokhara)\b", "Bukhara"),
    (r"\b(samarkand|samarqand)\b", "Samarkand"), (r"\bbaghdad\b", "Baghdad"), (r"\bmosul\b", "Mosul"),
    (r"\b(istanbul|constantinople)\b", "Istanbul"), (r"\b(tehran|teheran)\b", "Tehran"),
    (r"\bcairo\b|\bfustat\b", "Cairo"), (r"\bdamascus\b", "Damascus"), (r"\baleppo\b", "Aleppo"),
    (r"\blahore\b", "Lahore"), (r"\bagra\b", "Agra"), (r"fatehpur", "Fatehpur Sikri"), (r"\bdelhi\b", "Delhi"),
    (r"\b(lucknow|awadh|avadh|oudh|faizabad)\b", "Lucknow (Awadh)"), (r"murshidabad", "Murshidabad"),
    (r"\bpatna\b", "Patna"), (r"\bkashmir\b", "Kashmir"), (r"\bbijapur\b", "Bijapur"),
    (r"\bgolconda\b", "Golconda"), (r"\bahmadnagar\b", "Ahmadnagar"), (r"\bhyderabad\b", "Hyderabad"),
    (r"\bkashan\b", "Kashan"), (r"\b(iznik|nicaea)\b", "Iznik"), (r"\b(kutahya|kütahya)\b", "Kutahya"),
    (r"\b(nishapur|neyshabur|nishapour)\b", "Nishapur"), (r"\b(rayy|rey|ray)\b", "Rayy"),
    (r"\b(raqqa)\b", "Raqqa"), (r"\bsamarra\b", "Samarra"), (r"\bkirman\b|\bkerman\b", "Kirman"),
    (r"\byazd\b", "Yazd"), (r"\bbursa\b", "Bursa"), (r"\bhereke\b", "Hereke"), (r"\b(ushak|usak)\b", "Ushak"),
    (r"\bgranada\b", "Granada"), (r"\bmalaga\b", "Malaga"), (r"\b(valencia|manises|paterna)\b", "Valencia"),
    (r"\bcordoba\b|madinat al.?zahra", "Cordoba"), (r"\bfez\b|\bfes\b", "Fez"),
    (r"\b(kairouan|qayrawan)\b", "Kairouan"), (r"\bsultanabad\b", "Sultanabad"),
]
CENTRE_RE = [(re.compile(p), n) for p, n in CENTRES]
DECCAN_CITIES = {"Bijapur", "Golconda", "Ahmadnagar", "Hyderabad"}
MUGHAL_REIGNS = ["Babur", "Humayun", "Akbar", "Jahangir", "Shah Jahan", "Aurangzeb", "Bahadur Shah",
                 "Muhammad Shah", "Shah Alam"]
SAFAVID_REIGNS = ["Shah Ismail", "Shah Tahmasp", "Shah Abbas", "Shah Safi", "Shah Sulayman", "Shah Sultan Husayn"]

EXPLICIT_SCHOOLS = [  # (regex on folded text, school); first match wins
    (r"company (school|style|painting|painter)|(^|[|;] ?)company( ?[|;]|$)", "Company school"),
    (r"mughal court|imperial (mughal )?(workshop|atelier|studio|library|kitabkhana)|"
     r"mughal (imperial|royal) (workshop|atelier|studio)|court of (babur|humayun|akbar|jahangir|shah jahan|aurangzeb)",
     "Imperial Mughal atelier"),
    (r"nakkash|nakkas|ehl.?i hiref|ottoman (court|palace|imperial) (workshop|studio|atelier)|"
     r"(court|palace) (workshop|studio|atelier) (in|of) istanbul", "Ottoman court studio (nakkashane)"),
    (r"kitab.?khana|(royal|court) (library|workshop|atelier|studio) of (shah|the safavid)|"
     r"court of shah (isma'?il|tahmasp|abbas)|safavid (court|royal) (workshop|atelier|studio)", "Safavid court atelier"),
    (r"timurid (court|royal) (workshop|atelier|studio)|court of (baysunghur|husayn bayqara|sultan husayn)|"
     r"baysunghur.{0,20}(workshop|atelier|library)", "Timurid court atelier"),
    (r"jalayirid (court|royal)|court of (sultan )?ahmad jalayir", "Jalayirid court atelier"),
    (r"bazaar (painting|style|painter)", "Bazaar painting"),
    (r"kalighat", "Kalighat"),
]
EXPLICIT_RE = [(re.compile(p), n) for p, n in EXPLICIT_SCHOOLS]


def tfold(s):
    """Lower-case ASCII, keeping the punctuation fold() drops (| ; ' and -)."""
    s = re.sub(r"[’‘ʿʾ`]", "'", s or "")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return " ".join(s.split())


NOT_BOOK_ARTS_RE = re.compile(r"wall|fresco|mural|\btiles?\b|textile|fabric|ceramic|bowl|dish|jar|vase|panel|"
                              r"lacquer|pen.?box|qalamdan|box\b|casket|binding|cover|glass|case\b|stand\b|chest", re.I)


def is_book_arts(row):
    t = f"{row['object_type']} | {row['title']}"
    if NOT_BOOK_ARTS_RE.search(row["object_type"] or ""):
        return False
    return bool(BOOK_ARTS_RE.search(t))


def centres(text):
    t = fold(text or "")
    return [n for rx, n in CENTRE_RE if rx.search(t)]


def assign_school(row):
    """Sets row['school'], row['school_basis'], row['centre'], row['reign'], row['book_arts']."""
    text = tfold(" | ".join([row.get("school_text", ""), row["dynasty_recorded"]]))
    dyns = islamic_dynasties(row)
    dyn = dyns[0] if dyns else ""
    cen = centres(row.get("centre_text", ""))
    row["centre"] = cen[0] if cen else ""
    row["book_arts"] = is_book_arts(row)
    reigns = [r for r in MUGHAL_REIGNS + SAFAVID_REIGNS
              if re.search(r"\b" + r.lower() + r"\b", text.replace("isma'il", "ismail"))]
    row["reign"] = reigns[0] if reigns else ""
    school, basis = "", ""
    for rx, name in EXPLICIT_RE:
        if rx.search(text):
            school, basis = name, "recorded"
            break
    if school == "Safavid court atelier" and row["centre"] in ("Tabriz", "Qazvin", "Isfahan", "Mashhad"):
        school = f"Safavid {row['centre']}"
    if school == "Timurid court atelier" and row["centre"] in ("Herat", "Shiraz", "Samarkand"):
        school = f"Timurid {row['centre']}"
    # Mughal reign styles on V&A records ("Mughal" + "Akbar") = the imperial atelier
    if not school and dyn == "Mughal" and row["book_arts"] and row["reign"] in MUGHAL_REIGNS[:6]:
        school, basis = "Imperial Mughal atelier", "recorded"
    if not school and row["book_arts"]:
        c = row["centre"]
        if c in DECCAN_CITIES or (not c and dyn == "Deccani sultanates"):
            school, basis = f"Deccani ({c})" if c else "Deccani", "place" if c else "recorded"
        elif c in ("Lucknow (Awadh)", "Murshidabad", "Patna", "Kashmir"):
            school, basis = c, "place"
        elif c and dyn:
            school, basis = f"{dyn} {c}", "place"
        elif c and row.get("met_inferred"):
            # no recorded dynasty: name the centre with the Met-style dynasty for its date
            school, basis = f"{row['met_inferred']} {c}", "place, dynasty inferred"
    row["school"], row["school_basis"] = school, basis


# ------------------------------------------------------------------ outputs

def met_counts():
    out = {}
    if not os.path.exists(MET_CULTURES):
        return out
    with open(MET_CULTURES, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["kind"] == "period":
                out[r["key"]] = int(r["objects"] or 0)
    return out


def top(counter, n=6):
    return "; ".join(f"{k} ({v})" for k, v in counter.most_common(n) if k)


def check(row):
    """Compare the recorded dynasty with the Met-style inference."""
    inferred = met_infer(row["bases"], row["date_begin"], row["date_end"])
    row["met_inferred"] = inferred or ""
    if not row["dynasties"]:
        row["check"] = "no_recorded_dynasty"
    elif not inferred:
        row["check"] = "no_inference"
    elif inferred in row["dynasties"] or (inferred == "Umayyad (Spain)" and "Umayyad" in row["dynasties"]):
        row["check"] = "agree"
    else:
        row["check"] = "conflict"


# named masters whose school is known when the records give no centre or court
MASTER_SCHOOLS = [
    (r"\bbehzad\b", "Timurid Herat"), (r"sultan ali mashhadi", "Timurid Herat"), (r"mir ali (haravi|heravi)", "Timurid Herat"),
    (r"(reza|riza) abbasi|aqa (reza|riza)\b", "Safavid Isfahan"), (r"muin musavvir", "Safavid Isfahan"),
    (r"muhammad zaman", "Safavid Isfahan"), (r"shaykh abbasi", "Safavid Isfahan"), (r"afzal al.?husayni", "Safavid Isfahan"),
    (r"sultan muhammad\b", "Safavid Tabriz"), (r"aqa mirak", "Safavid Tabriz"), (r"mir musavvir", "Safavid Tabriz"),
    (r"mirza ali\b", "Safavid Tabriz"), (r"dust muhammad", "Safavid Tabriz"), (r"muhammadi\b", "Safavid Qazvin"),
    (r"siyavush", "Safavid Qazvin"), (r"sadiqi beg", "Safavid Qazvin"),
    (r"mir sayyid ali|abd al.?samad|abdus samad|basawan|daswanth|\bmiskin\b|kesu das|manohar|abul hasan|"
     r"\bmansur\b|bichitr|govardhan|bishandas|\bpayag\b|balchand|\bhashim\b|\bnanha\b|farrukh beg|dharm das|"
     r"\btulsi\b|\bsanwala\b|\bbhawani\b|jagannath|\bmadhu\b|\bmahesh\b|khem karan|\bla ?l\b|\bmukund\b|"
     r"\bmanohar\b|\bdaulat\b|\bhunhar\b|\bchitarman\b|\bmurad\b", "Imperial Mughal atelier"),
    (r"\blevni\b|nakkas osman|nakkash osman|matrakci", "Ottoman court studio (nakkashane)"),
]
MASTER_RE = [(re.compile(p), n) for p, n in MASTER_SCHOOLS]
COMPARABLE = [name for _, _, _, name in ISLAMIC_PERIODS]


def write_outputs(rows):
    os.makedirs(OUT_DIR, exist_ok=True)
    for r in rows:
        check(r)
        assign_school(r)
    rows.sort(key=lambda r: (r["source"], r["dynasties"][0] if r["dynasties"] else "~", r["date_begin"] or 0))
    cols = ["source", "id", "title", "object_type", "dynasty_recorded", "dynasty", "culture_place",
            "date_text", "date_begin", "date_end", "makers", "attributed", "materials_technique", "techniques",
            "book_arts", "school_workshop", "school_basis", "production_centre", "reign",
            "institution", "collection", "met_inferred_dynasty", "inference_check", "sweep", "url"]
    with open(os.path.join(OUT_DIR, "islamic_objects.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow([r["source"], r["id"], r["title"], r["object_type"], r["dynasty_recorded"],
                        "; ".join(r["dynasties"]), r["culture_place"], r["date_text"],
                        "" if r["date_begin"] is None else r["date_begin"],
                        "" if r["date_end"] is None else r["date_end"],
                        "; ".join(f"{n} ({role})" if role else n for n, role in r["makers"]),
                        int(bool(r["makers"])), r["materials_technique"], "; ".join(r["techniques"]),
                        int(r["book_arts"]), r["school"], r["school_basis"], r["centre"], r["reign"],
                        r["institution"], r["collection"], r["met_inferred"], r["check"], r.get("sweep", ""), r["url"]])

    def new_agg():
        return {"src": collections.Counter(), "types": collections.Counter(), "tech": collections.Counter(),
                "places": collections.Counter(), "makers": collections.Counter(), "begins": [], "ends": [],
                "mids": [], "check": collections.Counter(), "conflicts": collections.Counter(),
                "raw": collections.Counter(), "examples": [], "schools": collections.Counter(),
                "centres": collections.Counter(), "dyn": collections.Counter(), "reigns": collections.Counter(),
                "basis": collections.Counter(), "n": 0, "attr": 0, "book": 0, "book_attr": 0}

    def add(a, r):
        a["n"] += 1
        a["attr"] += bool(r["makers"])
        a["book"] += r["book_arts"]
        a["book_attr"] += r["book_arts"] and bool(r["makers"])
        a["src"][r["source"]] += 1
        a["types"][(r["object_type"] or "").lower()] += 1
        for t in r["techniques"]:
            a["tech"][t] += 1
        for b in r["bases"][:1]:
            a["places"][b] += 1
        for n, _ in r["makers"]:
            a["makers"][n] += 1
        if r["date_begin"] is not None:
            a["begins"].append(r["date_begin"])
        if r["date_end"] is not None:
            a["ends"].append(r["date_end"])
        if r["date_begin"] is not None and r["date_end"] is not None:
            a["mids"].append((r["date_begin"] + r["date_end"]) / 2)
        a["check"][r["check"]] += 1
        if r["check"] == "conflict":
            a["conflicts"][r["met_inferred"]] += 1
        a["raw"][r["dynasty_recorded"][:80]] += 1
        a["schools"][r["school"]] += 1
        a["centres"][r["centre"]] += 1
        a["reigns"][r["reign"]] += 1
        a["basis"][r["school_basis"]] += 1
        for d in r["dynasties"]:
            a["dyn"][d] += 1
        if len(a["examples"]) < 4:
            a["examples"].append(f"{r['source']}:{r['id']}")

    def q(mids, p):
        return round(mids[min(len(mids) - 1, int(p * len(mids)))]) if mids else ""

    def share(x, n):
        return round(x / n, 3) if n else ""

    # ---- dynasties
    met = met_counts()
    agg = collections.defaultdict(new_agg)
    for r in rows:
        for d in r["dynasties"]:
            add(agg[d], r)
    reg_total = sum(agg[d]["n"] for d in COMPARABLE if d in agg)
    met_total = sum(met.get(fold(d), 0) for d in COMPARABLE)
    dcols = ["key", "dynasty", "objects", "objects_vam", "objects_dia", "objects_cma", "date_begin_min",
             "date_end_max", "mid_p10", "mid_median", "mid_p90", "top_object_types", "top_techniques",
             "top_places", "top_production_centres", "top_schools", "named_makers",
             "attributed_objects", "attributed_share", "book_arts_objects", "book_arts_attributed_share",
             "checked", "agree", "conflict", "agree_share", "conflict_inferred_as",
             "met_inferred_objects", "share_regional", "share_met", "raw_labels", "example_ids"]
    with open(os.path.join(OUT_DIR, "islamic_dynasties.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(dcols)
        for d, a in sorted(agg.items(), key=lambda kv: -kv[1]["n"]):
            mids = sorted(a["mids"])
            key = fold(d)
            checked = a["check"]["agree"] + a["check"]["conflict"]
            comparable = d in COMPARABLE
            w.writerow([key, d, a["n"], a["src"]["vam"], a["src"]["dia"], a["src"]["cma"],
                        min(a["begins"]) if a["begins"] else "", max(a["ends"]) if a["ends"] else "",
                        q(mids, 0.1), round(statistics.median(mids)) if mids else "", q(mids, 0.9),
                        top(a["types"]), top(a["tech"]), top(a["places"], 4), top(a["centres"], 5),
                        top(a["schools"], 5), top(a["makers"], 8),
                        a["attr"], share(a["attr"], a["n"]), a["book"], share(a["book_attr"], a["book"]),
                        checked, a["check"]["agree"], a["check"]["conflict"], share(a["check"]["agree"], checked),
                        top(a["conflicts"], 4), met.get(key, ""),
                        share(a["n"], reg_total) if comparable else "",
                        share(met.get(key, 0), met_total) if comparable else "",
                        top(a["raw"], 4), " ".join(a["examples"])])

    # ---- makers
    mk = collections.defaultdict(lambda: {"names": collections.Counter(), "src": collections.Counter(),
                                          "dyn": collections.Counter(), "roles": collections.Counter(),
                                          "schools": collections.Counter(), "book": 0,
                                          "begins": [], "ends": [], "ids": [], "titles": [], "places": collections.Counter()})
    for r in rows:
        for n, role in r["makers"]:
            k = maker_key(n)
            if not k:
                continue
            m = mk[k]
            m["names"][n] += 1
            m["src"][r["source"]] += 1
            m["book"] += r["book_arts"]
            for d in r["dynasties"]:
                m["dyn"][d] += 1
            if r["school"]:
                m["schools"][r["school"]] += 1
            if role:
                m["roles"][role.lower()] += 1
            for b in r["bases"][:1]:
                m["places"][b] += 1
            if r["date_begin"] is not None:
                m["begins"].append(r["date_begin"])
            if r["date_end"] is not None:
                m["ends"].append(r["date_end"])
            if len(m["ids"]) < 5:
                m["ids"].append(f"{r['source']}:{r['id']}")
                m["titles"].append(r["title"][:60])
    mcols = ["maker", "name_variants", "objects", "objects_vam", "objects_dia", "objects_cma", "book_arts_objects",
             "dynasty_objects", "dynasties", "school", "school_basis", "schools", "roles", "places",
             "date_begin_min", "date_end_max", "example_ids", "example_titles"]
    with open(os.path.join(OUT_DIR, "islamic_makers.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(mcols)
        order = sorted(mk.items(), key=lambda kv: (-(sum(kv[1]["dyn"].values()) > 0), -sum(kv[1]["src"].values())))
        for k, m in order:
            school, basis = "", ""
            if m["schools"]:
                school, basis = m["schools"].most_common(1)[0][0], "objects"
            else:
                hit = next((n for rx, n in MASTER_RE if rx.search(k)), "")
                if hit:
                    school, basis = hit, "known master"
            m["school"] = school
            w.writerow([m["names"].most_common(1)[0][0], top(m["names"], 5), sum(m["src"].values()),
                        m["src"]["vam"], m["src"]["dia"], m["src"]["cma"], m["book"], sum(m["dyn"].values()),
                        top(m["dyn"], 4), school, basis, top(m["schools"], 3), top(m["roles"], 3), top(m["places"], 3),
                        min(m["begins"]) if m["begins"] else "", max(m["ends"]) if m["ends"] else "",
                        " ".join(m["ids"]), " | ".join(m["titles"])])

    # ---- schools / workshops and production centres
    sch = collections.defaultdict(new_agg)
    cen = collections.defaultdict(new_agg)
    for r in rows:
        if r["school"]:
            add(sch[r["school"]], r)
        if r["centre"]:
            add(cen[r["centre"]], r)
    masters = collections.defaultdict(collections.Counter)
    for k, m in mk.items():
        if m.get("school"):
            masters[m["school"]][m["names"].most_common(1)[0][0]] = sum(m["src"].values())
    scols = ["kind", "name", "objects", "objects_vam", "objects_dia", "objects_cma", "basis",
             "dynasties", "date_begin_min", "date_end_max", "mid_median", "book_arts_objects",
             "attributed_objects", "attributed_share", "book_arts_attributed_share", "named_masters",
             "top_object_types", "top_techniques", "reigns", "example_ids"]
    with open(os.path.join(OUT_DIR, "islamic_schools.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(scols)
        for kind, table in (("school", sch), ("centre", cen)):
            for name, a in sorted(table.items(), key=lambda kv: -kv[1]["n"]):
                mids = sorted(a["mids"])
                named = masters.get(name, collections.Counter()) if kind == "school" else a["makers"]
                w.writerow([kind, name, a["n"], a["src"]["vam"], a["src"]["dia"], a["src"]["cma"],
                            top(a["basis"], 2) if kind == "school" else "place",
                            top(a["dyn"], 4), min(a["begins"]) if a["begins"] else "",
                            max(a["ends"]) if a["ends"] else "", round(statistics.median(mids)) if mids else "",
                            a["book"], a["attr"], share(a["attr"], a["n"]), share(a["book_attr"], a["book"]),
                            top(named, 10), top(a["types"]), top(a["tech"]), top(a["reigns"], 4),
                            " ".join(a["examples"])])
    return agg, mk, sch


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skip", default="", help="comma-separated sources to skip: vam,dia,cma")
    ap.add_argument("--no-dia-details", action="store_true", help="do not read Discover Islamic Art object pages")
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between requests (default 1.0)")
    args = ap.parse_args()
    DELAY[0] = args.delay
    skip = set(filter(None, args.skip.split(",")))

    rows, stats = [], collections.Counter()
    if "vam" not in skip:
        r, s = harvest_vam()
        rows += r
        stats["vam"] = len(r)
    if "dia" not in skip:
        r, s = harvest_dia(details=not args.no_dia_details)
        rows += r
        stats["dia"] = len(r)
    if "cma" not in skip:
        r, s = harvest_cma()
        rows += r
        stats["cma"] = len(r)
    if os.environ.get("HARVARD_API_KEY"):
        print("  HARVARD_API_KEY is set, but the Harvard harvest is not implemented yet; skipped", file=sys.stderr)
    else:
        print("  HARVARD_API_KEY not set; Harvard Art Museums skipped", file=sys.stderr)

    agg, mk, sch = write_outputs(rows)
    with_dyn = collections.Counter(r["source"] for r in rows if r["dynasties"])
    checks = collections.Counter((r["source"], r["check"]) for r in rows)
    print(f"objects: {dict(stats)}; with a recorded dynasty: {dict(with_dyn)}")
    print(f"inference check: {dict(sorted(checks.items()))}")
    attributed = collections.Counter(r["source"] for r in rows if r["makers"])
    with_school = collections.Counter(r["source"] for r in rows if r["school"])
    print(f"attributed (named maker): {dict(attributed)}; with a school/workshop: {dict(with_school)}")
    print(f"dynasties: {len(agg)}; schools/workshops: {len(sch)}; named makers: {len(mk)}")
    print(f"wrote {OUT_DIR}/islamic_objects.csv, islamic_dynasties.csv, islamic_makers.csv, islamic_schools.csv")


if __name__ == "__main__":
    main()
