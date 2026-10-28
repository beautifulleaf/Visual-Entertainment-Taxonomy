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
  Cleveland Museum of Art open access API, department "Islamic Art"
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
                         with object counts, sources, dynasties and dates; the
                         seed for a named-artist reference list for the region

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
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            print(f"  {e} {url} (retry {attempt + 1})", file=sys.stderr)
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
               "kashmir rajasthan ahmadabad burhanpur"),
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
    }


def vam_keep(row, sweep):
    """Section/category sweeps keep everything; place and keyword sweeps are filtered."""
    if sweep in ("section", "islam"):
        return True
    if row["dynasties"]:
        return True
    b, e = row["date_begin"], row["date_end"]
    mid = (b + e) / 2 if b is not None and e is not None else None
    bases = set(row["bases"])
    if bases & ISLAMIC_BASES and (mid is None or mid >= 622):
        return True
    if sweep in ("Mughal", "Deccan", "Deccani") and bases & {"indian", "pakistani"} and mid and 1206 <= mid <= 1858:
        return True
    if sweep in ("Nasrid", "Hispano-Moresque", "al-Andalus", "Mudejar") and "spanish" in bases and mid and 711 <= mid <= 1500:
        return True
    return False


def harvest_vam():
    rows = {}
    stats = collections.Counter()
    sweeps = [("section", {"id_collection": VAM_SECTION}, (("date", "asc"), ("date", "desc"))),
              ("islam", {"id_category": VAM_ISLAM_CAT}, ((None, None),))]
    sweeps += [(p, {"q_place_name": p, "year_made_from": 622, "year_made_to": 1950}, ((None, None),)) for p in VAM_PLACES]
    sweeps += [(k, {"q": k}, ((None, None),)) for k in VAM_KEYWORDS]
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
        url = (en.get("objectUrl") or "").replace("&pageD=N", "")
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
            "institution": f.get("Holding Museum", ""), "collection": en.get("countryName", ""),
            "url": url, "sweep": "dynasty pages",
        })
    print(f"  DIA: {len(rows)} unique objects, {n_detail} object pages read", file=sys.stderr)
    return rows, collections.Counter(dia=len(rows))


# --------------------------------------------------------------- Cleveland

def harvest_cma():
    rows = []
    skip, limit = 0, 100
    while True:
        url = CMA_API + "?" + urllib.parse.urlencode({"department": "Islamic Art", "skip": skip, "limit": limit})
        d = fetch_json(url, os.path.join(RAW, "cma", f"islamic_art_{skip:05d}.json"))
        if not d or not d.get("data"):
            break
        for r in d["data"]:
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
            rows.append({
                "source": "cma", "id": r.get("accession_number") or str(r.get("id")),
                "title": r.get("title") or "", "object_type": r.get("type") or "",
                "dynasty_recorded": cult, "dynasties": norm_dynasties(cult, bases),
                "culture_place": place, "bases": bases,
                "date_text": r.get("creation_date") or "",
                "date_begin": r.get("creation_date_earliest"), "date_end": r.get("creation_date_latest"),
                "makers": makers, "materials_technique": tech,
                "techniques": technique_keys(tech + " " + (r.get("title") or "")),
                "institution": "Cleveland Museum of Art", "collection": r.get("department") or "",
                "url": r.get("url") or "", "sweep": "Islamic Art",
            })
        total = d.get("info", {}).get("total", 0)
        skip += limit
        if skip >= total:
            break
    print(f"  CMA Islamic Art: {len(rows)} objects", file=sys.stderr)
    return rows, collections.Counter(cma=len(rows))


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


def write_outputs(rows):
    os.makedirs(OUT_DIR, exist_ok=True)
    for r in rows:
        check(r)
    rows.sort(key=lambda r: (r["source"], r["dynasties"][0] if r["dynasties"] else "~", r["date_begin"] or 0))
    cols = ["source", "id", "title", "object_type", "dynasty_recorded", "dynasty", "culture_place",
            "date_text", "date_begin", "date_end", "makers", "materials_technique", "techniques",
            "institution", "collection", "met_inferred_dynasty", "inference_check", "url"]
    with open(os.path.join(OUT_DIR, "islamic_objects.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow([r["source"], r["id"], r["title"], r["object_type"], r["dynasty_recorded"],
                        "; ".join(r["dynasties"]), r["culture_place"], r["date_text"],
                        "" if r["date_begin"] is None else r["date_begin"],
                        "" if r["date_end"] is None else r["date_end"],
                        "; ".join(f"{n} ({role})" if role else n for n, role in r["makers"]),
                        r["materials_technique"], "; ".join(r["techniques"]), r["institution"],
                        r["collection"], r["met_inferred"], r["check"], r["url"]])

    # ---- dynasties
    met = met_counts()
    agg = collections.defaultdict(lambda: {"src": collections.Counter(), "types": collections.Counter(),
                                           "tech": collections.Counter(), "places": collections.Counter(),
                                           "makers": collections.Counter(), "begins": [], "ends": [],
                                           "mids": [], "check": collections.Counter(),
                                           "conflicts": collections.Counter(), "raw": collections.Counter(),
                                           "examples": []})
    for r in rows:
        for d in r["dynasties"]:
            a = agg[d]
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
            if len(a["examples"]) < 4:
                a["examples"].append(f"{r['source']}:{r['id']}")
    dcols = ["key", "dynasty", "objects", "objects_vam", "objects_dia", "objects_cma", "date_begin_min",
             "date_end_max", "mid_p10", "mid_median", "mid_p90", "top_object_types", "top_techniques",
             "top_places", "named_makers", "checked", "agree", "conflict", "agree_share",
             "conflict_inferred_as", "met_inferred_objects", "raw_labels", "example_ids"]
    with open(os.path.join(OUT_DIR, "islamic_dynasties.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(dcols)
        for d, a in sorted(agg.items(), key=lambda kv: -sum(kv[1]["src"].values())):
            mids = sorted(a["mids"])

            def q(p):
                return round(mids[min(len(mids) - 1, int(p * len(mids)))]) if mids else ""
            key = fold(d)
            checked = a["check"]["agree"] + a["check"]["conflict"]
            w.writerow([key, d, sum(a["src"].values()), a["src"]["vam"], a["src"]["dia"], a["src"]["cma"],
                        min(a["begins"]) if a["begins"] else "", max(a["ends"]) if a["ends"] else "",
                        q(0.1), round(statistics.median(mids)) if mids else "", q(0.9),
                        top(a["types"]), top(a["tech"]), top(a["places"], 4), top(a["makers"], 8),
                        checked, a["check"]["agree"], a["check"]["conflict"],
                        round(a["check"]["agree"] / checked, 2) if checked else "",
                        top(a["conflicts"], 4), met.get(key, ""), top(a["raw"], 4), " ".join(a["examples"])])

    # ---- makers
    mk = collections.defaultdict(lambda: {"names": collections.Counter(), "src": collections.Counter(),
                                          "dyn": collections.Counter(), "roles": collections.Counter(),
                                          "begins": [], "ends": [], "ids": [], "titles": [], "places": collections.Counter()})
    for r in rows:
        for n, role in r["makers"]:
            k = maker_key(n)
            if not k:
                continue
            m = mk[k]
            m["names"][n] += 1
            m["src"][r["source"]] += 1
            for d in r["dynasties"]:
                m["dyn"][d] += 1
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
    mcols = ["maker", "name_variants", "objects", "objects_vam", "objects_dia", "objects_cma",
             "dynasty_objects", "dynasties", "roles", "places", "date_begin_min", "date_end_max",
             "example_ids", "example_titles"]
    with open(os.path.join(OUT_DIR, "islamic_makers.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(mcols)
        order = sorted(mk.items(), key=lambda kv: (-(sum(kv[1]["dyn"].values()) > 0), -sum(kv[1]["src"].values())))
        for k, m in order:
            w.writerow([m["names"].most_common(1)[0][0], top(m["names"], 5), sum(m["src"].values()),
                        m["src"]["vam"], m["src"]["dia"], m["src"]["cma"], sum(m["dyn"].values()),
                        top(m["dyn"], 4), top(m["roles"], 3), top(m["places"], 3),
                        min(m["begins"]) if m["begins"] else "", max(m["ends"]) if m["ends"] else "",
                        " ".join(m["ids"]), " | ".join(m["titles"])])
    return agg, mk


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

    agg, mk = write_outputs(rows)
    with_dyn = collections.Counter(r["source"] for r in rows if r["dynasties"])
    checks = collections.Counter((r["source"], r["check"]) for r in rows)
    print(f"objects: {dict(stats)}; with a recorded dynasty: {dict(with_dyn)}")
    print(f"inference check: {dict(sorted(checks.items()))}")
    print(f"dynasties: {len(agg)}; named makers: {len(mk)}")
    print(f"wrote {OUT_DIR}/islamic_objects.csv, islamic_dynasties.csv, islamic_makers.csv")


if __name__ == "__main__":
    main()
