"""Candidate set for unattributed traditions (visual-art-plan.md §2A).

Most antiquities, decorative arts and non-Western objects have no recorded maker,
so they are grouped by culture, period and object tradition instead of artist.
This script takes every object without an artist and turns its free-text
Culture and Period strings into normalised tradition keys:

  Culture  "Greek, Attic" / "Attic" / "Greek (Attic)"   -> greek, attic
           "probably French", "French (?)"               -> french
           "Chimú or Chancay"                            -> chimu + chancay (split)
           "China" / "Chinese"                           -> chinese
           "Chinese, for European market"                -> chinese, export
           "Pakistan (ancient region of Gandhara)"       -> gandhara
           Keys have at most two levels (base, sub); a sub-level key also counts
           towards its base, so "greek" includes "greek, attic".
           Objects with no Culture fall back to the Country/Region field in the
           Egyptian, Islamic, Ancient West Asian and Asian departments
           (culture_source = country).
  Period   "Qing dynasty (1644–1911), Kangxi period (1662–1722)" -> qing dynasty
           "Edo (1615–1868) or Meiji period (1868–1912)"        -> edo + meiji
           "Late Archaic" -> archaic when "archaic" is itself a key.
           The Met CSV has no Period for Islamic Art, so its dynastic period
           (Mamluk, Safavid, Timurid, Ottoman, Mughal, ...) is inferred from the
           culture/country and the object's mid date (ISLAMIC_PERIODS).
  Technique (object traditions only) is read from Medium for a short list of
           named wares and techniques: red-figure, black-figure, celadon,
           blue-and-white, sancai, famille rose, cloisonné, lustreware, ...

Inputs (all on disk, CC0):
  data/raw/museums/MetObjects.csv                     the Met open-access CSV
  data/raw/museums/aic/artic-api-data/json/artworks   Art Institute of Chicago dump
      (unattributed = artist_id null; place_of_origin mapped to the same keys)
  Cleveland: data/raw/museums/cma_creators.jsonl holds creators only, with no
      culture field, so it is not used here.
  Getty AAT "Styles and Periods" facet (aat:300015646), fetched once from
      https://vocab.getty.edu/sparql and cached in data/raw/aat/. When the
      endpoint is unreachable the aat_* columns are left empty.

Outputs:
  data/interim/unattributed_cultures.csv            one row per
      kind=culture         normalised culture (base and sub level)
      kind=culture_period  culture x period ("egyptian | new kingdom")
      kind=period          period alone, with its dominant cultures
  data/interim/unattributed_object_traditions.csv   one row per
      kind=culture_class            culture x classification ("chinese / ceramics")
      kind=culture_period_class     culture x period x classification
      kind=culture_technique        culture x technique ("greek, attic / red-figure")
      kind=culture_period_technique culture x period x technique
  Columns: objects (all attributions, including "A or B"), objects_sole (single
  attribution), timeline_works, highlights, begin/end_median, dominant
  department, top classifications, example Met object IDs (Timeline works and
  highlights first), aic_objects (culture rows), aat_id / aat_label / aat_match.

Usage: python3 pipelines/unattributed/build_traditions.py [--no-aat] [--min-objects 3]
"""
import argparse
import collections
import csv
import glob
import json
import os
import re
import statistics
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

csv.field_size_limit(1 << 24)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw", "museums")
MET_CSV = os.path.join(RAW, "MetObjects.csv")
AIC_DIR = os.path.join(RAW, "aic", "artic-api-data", "json", "artworks")
AAT_DIR = os.path.join(ROOT, "data", "raw", "aat")
OUT_DIR = os.path.join(ROOT, "data", "interim")
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"
AAT_SPARQL = "https://vocab.getty.edu/sparql.json"
AAT_FACET = "300015646"  # Styles and Periods
AAT_PAGE = 2000

# Departments whose unattributed objects are not "traditions" in the §2A sense
# (anonymous prints, photographs, ephemera, library material).
SKIP_DEPTS = {"Drawings and Prints", "Photographs", "The Libraries"}
# Departments where an empty Culture may fall back to Country / Region.
FALLBACK_DEPTS = {"Egyptian Art", "Islamic Art", "Ancient West Asian Art", "Asian Art",
                  "The Michael C. Rockefeller Wing", "Arts of Africa, Oceania, and the Americas"}
DEPT_DEFAULT = {"Egyptian Art": "Egyptian", "Islamic Art": "Islamic"}

# ---------------------------------------------------------------- culture keys

# country / region nouns and variant adjectives -> one adjective form
DEMONYM = {
    "china": "Chinese", "japan": "Japanese", "korea": "Korean", "india": "Indian",
    "iran": "Iranian", "persian": "Iranian", "persia": "Iranian", "iraq": "Iraqi",
    "egypt": "Egyptian", "syria": "Syrian", "turkey": "Turkish", "anatolia": "Anatolian",
    "thailand": "Thai", "tibet": "Tibetan", "nepal": "Nepalese", "nepali": "Nepalese",
    "pakistan": "Pakistani", "afghanistan": "Afghan", "indonesia": "Indonesian",
    "vietnam": "Vietnamese", "cambodia": "Cambodian", "myanmar": "Burmese", "burma": "Burmese",
    "sri lanka": "Sri Lankan", "bangladesh": "Bangladeshi", "philippines": "Philippine",
    "malaysia": "Malaysian", "laos": "Lao", "bhutan": "Bhutanese", "mongolia": "Mongolian",
    "taiwan": "Taiwanese", "peru": "Peruvian", "mexico": "Mexican", "colombia": "Colombian",
    "costa rica": "Costa Rican", "bolivia": "Bolivian", "ecuador": "Ecuadoran",
    "guatemala": "Guatemalan", "panama": "Panamanian", "morocco": "Moroccan",
    "algeria": "Algerian", "tunisia": "Tunisian", "spain": "Spanish", "italy": "Italian",
    "france": "French", "germany": "German", "england": "British", "english": "British",
    "united kingdom": "British", "great britain": "British", "scotland": "Scottish",
    "ireland": "Irish", "wales": "Welsh", "netherlands": "Dutch", "holland": "Dutch",
    "belgium": "Belgian", "flanders": "Flemish", "austria": "Austrian",
    "switzerland": "Swiss", "russia": "Russian", "greece": "Greek", "cyprus": "Cypriot",
    "uzbekistan": "Uzbek", "present-day uzbekistan": "Uzbek", "mesopotamia": "Mesopotamian",
    "levant": "Levantine", "nubia": "Nubian", "sudan": "Sudanese",
    "saudi arabia": "Arabian", "arabia": "Arabian", "yemen": "Yemeni", "caucasus": "Caucasian",
    "armenia": "Armenian", "georgia": "Georgian", "portugal": "Portuguese",
    "bohemia": "Bohemian", "hungary": "Hungarian", "poland": "Polish", "sweden": "Swedish",
    "denmark": "Danish", "norway": "Norwegian", "europe": "European",
    "united states": "American", "usa": "American", "canada": "Canadian",
    "palestine": "Palestinian", "israel": "Israeli", "lebanon": "Lebanese",
    "jordan": "Jordanian", "upper egypt": "Egyptian", "lower egypt": "Egyptian",
    "egypt and sudan": "Egyptian", "egypt and syria": "Egyptian", "crete": "Minoan", "nigeria": "Nigerian", "ghana": "Ghanaian",
    "mali": "Malian", "ethiopia": "Ethiopian", "kenya": "Kenyan", "south africa": "South African",
    "papua new guinea": "Papua New Guinean", "new zealand": "New Zealand",
}

# whole-key aliases (lowercase key -> canonical key), applied after parsing
ALIAS = {
    "attic": "greek, attic", "laconian": "greek, laconian", "corinthian": "greek, corinthian",
    "boeotian": "greek, boeotian", "apulian": "greek, apulian", "campanian": "greek, campanian",
    "lucanian": "greek, lucanian", "euboean": "greek, euboean", "east greek": "greek, east greek",
    "greek, attica": "greek, attic", "javanese": "indonesian, java", "balinese": "indonesian, bali",
    "mexica": "aztec", "mexica, aztec": "aztec", "aztec, mexica": "aztec",
    "burmese, burma": "burmese", "minoan, crete": "minoan", "nazca": "nasca",
    "southern and northern cheyenne": "cheyenne", "northern cheyenne": "cheyenne",
    "southern cheyenne": "cheyenne", "thai, thailand": "thai", "tibetan, tibet": "tibetan",
    "maya, mayan": "maya", "mayan": "maya", "inka": "inca", "olmec-style": "olmec",
    "edo": "edo, benin kingdom", "benin": "edo, benin kingdom", "benin kingdom": "edo, benin kingdom",
    "chinese, china": "chinese", "sardis, lydian": "lydian, sardis", "japanese, japan": "japanese",
}
SUB_PROMOTE = {"gandhara"}  # "Pakistan (ancient region of Gandhara)" -> gandhara
DROP = {"", "unknown", "unknown fabric", "undetermined", "various", "n/a"}

UNCERTAIN = re.compile(r"\b(possibly|probably|likely|perhaps|presumably|or later|style of)\b|\(\?\)|\?",
                       re.I)
MARKET = re.compile(r",?\s*\(?\b(for (the )?[\w\s.-]*?market|[\w\s.-]*? market|for export)\b\)?", re.I)
COMPONENT = re.compile(r"(?i)\b(?:hilt|blade|mounts?|scabbard|barrel|lock|stock|fittings?|sheath|guard)"
                       r"(?: and \w+)?\s*[,:]\s*([^;]+)")
AFTER = re.compile(r",?\s*\bafter [\w\s.-]+ original\b", re.I)


def fold(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9, -]", " ", s).split())


def tidy(s):
    s = unicodedata.normalize("NFKC", s or "").replace("’", "'")
    return " ".join(s.split()).strip(" ,;:-")


def split_alternatives(s):
    """'Chimú or Chancay' -> 2; 'north or central coast' stays (lowercase right side)."""
    out = []
    for part in re.split(r"\s*/\s*", s):
        out.extend(re.split(r"\s+or\s+(?=[A-Z])", part))
    return [p for p in (tidy(x) for x in out) if p]


def culture_keys(raw):
    """Raw Culture string -> (list of (key, label) pairs, export flag)."""
    s = tidy(raw)
    if not s or fold(s) in DROP:
        return []
    s = tidy(UNCERTAIN.sub(" ", s))
    export = bool(MARKET.search(s))
    s = tidy(AFTER.sub(" ", MARKET.sub(" ", s)))
    parts = COMPONENT.findall(s)  # arms: "hilt, Indian; blade, European" -> Indian / European
    if parts:
        s = " / ".join(tidy(p) for p in parts)
    keys = []
    for alt in split_alternatives(s):
        parts = []
        outer = tidy(re.sub(r"\([^)]*\)", " ", alt))
        parens = [tidy(p) for p in re.findall(r"\(([^)]*)\)", alt)]
        parts = [tidy(p) for p in re.split(r"[,;]", outer) if tidy(p)]
        for p in parens:
            m = re.match(r"(?i)ancient region of (.+)", p)
            if m:
                parts.append(tidy(m.group(1)))
            elif p and len(parts) == 1:
                parts.append(tidy(p.split(",")[0]))
        parts = [re.sub(r"(?i)\s+(people|peoples|culture)$", "", re.sub(r"(?i)^present-day\s+", "", p))
                 for p in parts]
        parts = [p for p in parts if fold(p) not in DROP]
        if not parts:
            continue
        if len(parts) > 2:
            parts = [parts[0], parts[-1]]
        parts[0] = DEMONYM.get(fold(parts[0]), parts[0])
        if export:
            parts = [parts[0], "export"]
        if len(parts) == 2 and fold(parts[1]) in SUB_PROMOTE:
            parts = [parts[1]]
        if len(parts) == 2 and fold(parts[1]) == fold(parts[0]):
            parts = parts[:1]
        key = ", ".join(fold(p) for p in parts)
        label = ", ".join(p[:1].upper() + p[1:] for p in parts)
        if key in ALIAS:
            key = ALIAS[key]
            label = key.title()
        keys.append((key, label))
    return keys


def parent_key(key):
    return key.split(", ")[0] if ", " in key else None


# ----------------------------------------------------------------- period keys

DATES = re.compile(r"\([^)]*\d[^)]*\)|\b(ca\.|c\.)?\s*\d{2,4}\s*(bce|ce|bc|ad)?\b", re.I)
DIRECTION = re.compile(r"^(northern|southern|eastern|western)\s+(?=\w+ dynasty)", re.I)
KEEP_PERIOD_WORD = {"late", "early", "middle", "old", "new", "intermediate"}


def period_keys(raw):
    s = tidy(raw)
    if not s:
        return []
    s = UNCERTAIN.sub(" ", s)
    s = re.sub(r"(?i)\bmark and\b", " ", s)
    s = DATES.sub(" ", s)
    out = []
    for alt in re.split(r"\s*(?:/|–|—|\bor\b|\bto\b)\s*", s):
        alt = tidy(alt.split(",")[0])
        alt = DIRECTION.sub("", alt)
        alt = re.sub(r"\s+(?:[IVX]+[a-c]?|[0-9][a-c]?)$", "", alt)  # Iron Age II -> Iron Age
        k = fold(alt)
        if k.endswith(" period") and k[:-7] not in KEEP_PERIOD_WORD and len(k) > 7:
            k = k[:-7]
        if k in DROP or not re.search(r"[a-z]", k):
            continue
        out.append((k, tidy(alt)))
    return out


# The Met CSV carries no Period for Islamic Art, so the dynastic period is inferred
# from the culture key and the object's mid date (e.g. Egypt/Syria 1250-1517 -> Mamluk).
ISLAMIC_PERIODS = [
    ({"egyptian", "syrian", "palestinian", "lebanese"}, 1250, 1517, "Mamluk"),
    ({"egyptian", "syrian"}, 1171, 1250, "Ayyubid"),
    ({"egyptian", "syrian", "tunisian"}, 909, 1171, "Fatimid"),
    ({"egyptian"}, 1517, 1867, "Ottoman"),
    ({"syrian", "iraqi", "egyptian"}, 661, 750, "Umayyad"),
    ({"iraqi", "iranian", "syrian", "egyptian"}, 750, 909, "Abbasid"),
    ({"iranian", "iraqi"}, 1037, 1194, "Seljuq"),
    ({"turkish", "anatolian"}, 1081, 1308, "Seljuq"),
    ({"iranian", "iraqi"}, 1256, 1353, "Ilkhanid"),
    ({"iranian", "central asia", "uzbek", "afghan"}, 1370, 1507, "Timurid"),
    ({"iranian"}, 1501, 1722, "Safavid"),
    ({"iranian"}, 1789, 1925, "Qajar"),
    ({"turkish", "anatolian", "syrian", "iraqi"}, 1299, 1923, "Ottoman"),
    ({"indian", "pakistani"}, 1526, 1857, "Mughal"),
    ({"spanish"}, 756, 1031, "Umayyad (Spain)"),
    ({"spanish"}, 1232, 1492, "Nasrid"),
    ({"moroccan", "spanish", "algerian"}, 1040, 1269, "Almoravid and Almohad"),
]


def infer_islamic_period(culture_keys_, begin, end):
    if begin is None or end is None:
        return []
    mid = (begin + end) / 2
    bases = {k.split(", ")[0] for k in culture_keys_}
    for cultures, start, stop, name in ISLAMIC_PERIODS:
        if bases & cultures and start <= mid <= stop:
            return [(fold(name), name)]
    return []


# phases whose bare name is rarely used alone ("Final Jōmon" -> jomon)
PERIOD_GROUP = {"jomon", "yayoi", "woodland", "formative", "classic", "postclassic", "preclassic"}


def collapse_period_prefixes(counter):
    """'late archaic' -> 'archaic' when 'archaic' is itself a common key."""
    remap = {}
    for k in counter:
        m = re.match(r"(early|late|mid|final|middle|initial|terminal|incipient)\s+(.+)", k)
        if not m:
            continue
        rest = m.group(2)
        if rest in PERIOD_GROUP or (counter.get(rest, 0) >= 20 and rest not in KEEP_PERIOD_WORD
                                    and rest not in ("dynastic", "period", "kingdom")):
            remap[k] = rest
    return remap


# ------------------------------------------------------- classification/technique

def classification_key(cls, object_name):
    c = tidy((cls or "").split("|")[0])
    if not c:
        c = tidy((object_name or "").split(",")[0])
        if not c:
            return "unclassified"
    f = fold(c)
    if "sculpt" in f or f in ("terracottas", "stucco"):
        return "sculpture" if "sculpt" in f else f
    f = f.split("-")[0].strip()
    return {"gold and silver": "metalwork", "metal": "metalwork", "bronzes": "bronzes",
            "vases": "vases", "ivories and bone": "ivories"}.get(f, f) or "unclassified"


TECHNIQUES = [
    ("red-figure", r"red[- ]figure"), ("black-figure", r"black[- ]figure"),
    ("white-ground", r"white[- ]ground"), ("celadon", r"celadon"),
    ("blue-and-white", r"blue[- ]and[- ]white|underglaze (cobalt )?blue|cobalt blue under"),
    ("sancai", r"sancai|three[- ]colou?r"), ("famille rose", r"famille rose"),
    ("famille verte", r"famille verte"), ("cloisonne", r"cloisonn"), ("champleve", r"champlev"),
    ("lustreware", r"lust(er|re)"), ("stonepaste", r"stonepaste|fritware"),
    ("minai", r"mina'?i"), ("enameled glass", None), ("lacquer", r"lacquer"),
    ("maki-e", r"maki-?e"), ("tin-glazed", r"tin[- ]glaze|maiolica|majolica|delftware"), ("faience", r"faience"),
    ("sgraffito", r"sgraffit"), ("slipware", r"slip[- ](painted|decorated|trailed)|slipware"),
    ("hard-paste porcelain", r"hard[- ]paste"), ("soft-paste porcelain", r"soft[- ]paste"),
    ("salt-glazed stoneware", r"salt[- ]glaze"), ("niello", r"niello"),
    ("tapestry", r"tapestry"), ("ikat", r"\bikat\b"), ("batik", r"\bbatik\b"),
]
TECHNIQUES = [(n, re.compile(p, re.I) if p else None) for n, p in TECHNIQUES]


def techniques(medium):
    m = medium or ""
    out = [n for n, rx in TECHNIQUES if rx is not None and rx.search(m)]
    if re.search(r"(?i)\bglass\b", m) and re.search(r"(?i)enamel", m):
        out.append("enameled glass")
    return out


# ------------------------------------------------------------------ aggregation

def to_int(v):
    try:
        return int(str(v).strip())
    except ValueError:
        return None


class Agg:
    __slots__ = ("n", "sole", "direct", "tl", "hl", "begin", "end", "dept", "cls", "per", "cult",
                 "raw", "ex", "labels")

    def __init__(self):
        self.n = self.sole = self.direct = self.tl = self.hl = 0
        self.begin, self.end, self.ex = [], [], []
        self.dept, self.cls, self.per, self.cult, self.raw, self.labels = (
            collections.Counter() for _ in range(6))

    def add(self, o, sole, direct, label):
        self.n += 1
        self.sole += sole
        self.direct += direct
        self.tl += o["tl"]
        self.hl += o["hl"]
        if o["begin"] is not None:
            self.begin.append(o["begin"])
        if o["end"] is not None:
            self.end.append(o["end"])
        self.dept[o["dept"]] += 1
        self.cls[o["cls"]] += 1
        for p in o["periods"]:
            self.per[p] += 1
        for c in o["cultures"]:
            self.cult[c] += 1
        if o["raw"]:
            self.raw[o["raw"]] += 1
        self.labels[label] += 1
        if o["tl"] or o["hl"] or len(self.ex) < 5:
            self.ex.append((-o["tl"], -o["hl"], o["id"]))
            if len(self.ex) > 60:
                self.ex = sorted(self.ex)[:10]


def top(counter, n=3, labels=None):
    return "; ".join(f"{(labels or {}).get(k, k)} ({v})" for k, v in counter.most_common(n) if k)


# Generic maker placeholders count as unattributed: "Unidentified artist",
# "Yoruba artist", "Moche artist(s)", "Ìgùn Ẹ́rọ̀nwwọ̀n (brass-casting guild) artists",
# "Artists of Mariwai Village", "Unknown". Named masters ("Master of the Die") do not.
PLACEHOLDER = re.compile(r"(?i)^(unknown|unidentified|anonymous)\b|\bartists?(\s*\(s\))?$|^artists? of\b"
                         r"|\b(guild|caste)\b")


def unattributed(name):
    first = tidy((name or "").split("|")[0])
    return not first or bool(PLACEHOLDER.search(first))


def load_met(include_all):
    """Unattributed Met objects as dicts with culture / period / class keys."""
    objs, period_count, period_label = [], collections.Counter(), collections.defaultdict(collections.Counter)
    raw_cultures, skipped = set(), collections.Counter()
    with open(MET_CSV, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if not unattributed(r["Artist Display Name"]):
                continue
            dept = r["Department"]
            if dept in SKIP_DEPTS and not include_all:
                skipped["department"] += 1
                continue
            raw = tidy(r["Culture"])
            source = "culture"
            ck = culture_keys(raw)
            if raw:
                raw_cultures.add(raw)
            if not ck and dept in FALLBACK_DEPTS:
                place = tidy((r["Country"] or r["Region"] or "").split("|")[0])
                ck = culture_keys(place)
                if not ck and dept in DEPT_DEFAULT:
                    ck = culture_keys(DEPT_DEFAULT[dept])
                source = "country" if ck else source
            if not ck:
                skipped["no culture"] += 1
                continue
            pk = period_keys(r["Period"])
            if not pk and dept == "Islamic Art":
                pk = infer_islamic_period([k for k, _ in ck], to_int(r["Object Begin Date"]),
                                          to_int(r["Object End Date"]))
            for k, lab in pk:
                period_count[k] += 1
                period_label[k][lab] += 1
            objs.append({
                "id": r["Object ID"], "dept": dept, "raw": raw if source == "culture" else "",
                "source": source, "ck": ck, "pk": pk,
                "tl": int(r["Is Timeline Work"].strip().lower() == "true"),
                "hl": int(r["Is Highlight"].strip().lower() == "true"),
                "begin": to_int(r["Object Begin Date"]), "end": to_int(r["Object End Date"]),
                "cls": classification_key(r["Classification"], r["Object Name"]),
                "tech": techniques(r["Medium"]),
            })
    remap = collapse_period_prefixes(period_count)
    plabel = {}
    for k, c in period_label.items():
        plabel[k] = c.most_common(1)[0][0]
    for o in objs:
        o["periods"] = sorted({remap.get(k, k) for k, _ in o["pk"]})
    return objs, raw_cultures, plabel, remap, skipped


def aic_counts(sub_index):
    """AIC unattributed artworks per culture key (place_of_origin)."""
    counts, unmatched = collections.Counter(), collections.Counter()
    files = glob.glob(os.path.join(AIC_DIR, "*.json"))
    for fn in files:
        try:
            with open(fn, encoding="utf-8") as f:
                d = json.load(f)
        except (OSError, ValueError):
            continue
        if d.get("artist_id") is not None:
            continue
        place = tidy(d.get("place_of_origin") or "")
        if not place:
            continue
        keys = set()
        for k, _ in culture_keys(place):
            if k in sub_index:  # a city/region such as Staffordshire -> british, staffordshire
                k = sub_index[k]
            keys.add(k)
            if parent_key(k):
                keys.add(parent_key(k))
        if not keys:
            unmatched[place] += 1
        for k in keys:
            counts[k] += 1
    return counts, len(files)


# -------------------------------------------------------------------------- AAT

def sparql(query):
    url = AAT_SPARQL + "?" + urllib.parse.urlencode({"query": query})
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "application/sparql-results+json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


AAT_QUERY = """PREFIX gvp: <http://vocab.getty.edu/ontology#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xl: <http://www.w3.org/2008/05/skos-xl#>
PREFIX aat: <http://vocab.getty.edu/aat/>
SELECT ?s ?pref ?parent (GROUP_CONCAT(DISTINCT ?alt; separator="|") AS ?alts) WHERE {
  ?s a gvp:Concept ; skos:inScheme aat: ; gvp:broaderExtended aat:%s ;
     gvp:prefLabelGVP/xl:literalForm ?pref .
  OPTIONAL { ?s gvp:broaderPreferred/gvp:prefLabelGVP/xl:literalForm ?parent }
  OPTIONAL { ?s skos:altLabel ?alt . FILTER(lang(?alt) = "en" || lang(?alt) = "") }
} GROUP BY ?s ?pref ?parent ORDER BY ?s LIMIT %d OFFSET %d"""


def load_aat():
    """Styles and Periods terms: list of (id, pref, parent, [labels]). Cached per page."""
    os.makedirs(AAT_DIR, exist_ok=True)
    terms, offset = [], 0
    while True:
        path = os.path.join(AAT_DIR, f"styles_periods_{offset:06d}.json")
        if not os.path.exists(path):
            data, err = None, None
            for attempt in range(4):
                try:
                    data = sparql(AAT_QUERY % (AAT_FACET, AAT_PAGE, offset))
                    break
                except (urllib.error.URLError, OSError, ValueError) as e:
                    err = e
                    time.sleep(5 * (attempt + 1))
            if data is None:
                print(f"AAT endpoint unreachable ({err}); aat_* columns left empty")
                return None
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            time.sleep(1.5)
        with open(path, encoding="utf-8") as f:
            rows = json.load(f)["results"]["bindings"]
        for b in rows:
            labels = [b["pref"]["value"]] + [a for a in b.get("alts", {}).get("value", "").split("|") if a]
            terms.append((b["s"]["value"].rsplit("/", 1)[-1], b["pref"]["value"],
                          b.get("parent", {}).get("value", ""), labels))
        if len(rows) < AAT_PAGE:
            break
        offset += AAT_PAGE
    return terms


GENERIC = re.compile(r"\b(styles?|periods?|cultures?|dynasty|dynasties|or|and|the|of)\b")


def aat_head(label):
    """'Chinese (culture or style)' -> ('chinese', 'culture or style')."""
    qual = " ".join(re.findall(r"\(([^)]*)\)", label))
    head = fold(re.sub(r"\([^)]*\)", " ", label)).replace(",", " ")
    return " ".join(head.split()), fold(qual)


class AATIndex:
    def __init__(self, terms):
        self.by_head = collections.defaultdict(list)
        for tid, pref, parent, labels in terms:
            for lab in labels:
                head, qual = aat_head(lab)
                for h in {head, " ".join(GENERIC.sub(" ", head).split())}:
                    if h:
                        self.by_head[h].append((tid, pref, qual + " " + fold(parent)))

    def lookup(self, heads, context):
        ctx = set(context.split())
        for level, h in heads:
            h2 = " ".join(GENERIC.sub(" ", h).split())
            cands = self.by_head.get(h) or self.by_head.get(h2)
            if not cands:
                continue
            uniq = {c[0]: c for c in cands}
            scored = sorted(uniq.values(), key=lambda c: (-len(ctx & set(c[2].replace(",", " ").split())),
                                                         c[0]))
            best = scored[0]
            if len(uniq) > 1 and not ctx & set(best[2].split()):
                level += "_ambiguous"
            return best[0], best[1], level
        return "", "", ""


def culture_heads(key):
    base, _, sub = key.partition(", ")
    heads = [("exact", f"{sub} {base}" if sub else base)]
    if sub:
        heads += [("exact", f"{base} {sub}"), ("sub", sub), ("parent", base)]
    return heads, f"{base} {sub}"


# ------------------------------------------------------------------------- main

def median(xs):
    return int(statistics.median(xs)) if xs else ""


def write(path, rows, fields):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-aat", action="store_true", help="skip the Getty AAT mapping")
    ap.add_argument("--min-objects", type=int, default=3,
                    help="min objects for culture_period, period and object-tradition rows "
                         "(rows with a Timeline work are always kept)")
    ap.add_argument("--all-departments", action="store_true",
                    help="also use Drawings and Prints, Photographs and Libraries")
    args = ap.parse_args()

    objs, raw_cultures, plabel, premap, skipped = load_met(args.all_departments)
    print(f"Met: {len(objs)} unattributed objects with a culture "
          f"(skipped {dict(skipped)}); {len(raw_cultures)} distinct raw Culture strings")

    cult = collections.defaultdict(Agg)
    cper = collections.defaultdict(Agg)
    per = collections.defaultdict(Agg)
    ocls = collections.defaultdict(Agg)
    clabel = {}
    for o in objs:
        direct = {k for k, _ in o["ck"]}
        for k, lab in o["ck"]:
            clabel.setdefault(k, collections.Counter())[lab] += 1
        keys = set(direct) | {parent_key(k) for k in direct if parent_key(k)}
        o["cultures"] = sorted(direct)
        sole = int(len(direct) == 1)
        for k in keys:
            if k not in clabel:
                clabel[k] = collections.Counter({k.title(): 1})
            cult[k].add(o, sole, int(k in direct), o["source"])
            for p in o["periods"]:
                cper[(k, p)].add(o, sole, 1, "")
                ocls[("culture_period_class", k, p, o["cls"])].add(o, sole, 1, "")
                for t in o["tech"]:
                    ocls[("culture_period_technique", k, p, t)].add(o, sole, 1, "")
            ocls[("culture_class", k, "", o["cls"])].add(o, sole, 1, "")
            for t in o["tech"]:
                ocls[("culture_technique", k, "", t)].add(o, sole, 1, "")
        for p in o["periods"]:
            per[p].add(o, int(len(o["periods"]) == 1), 1, "")
    clab = {k: c.most_common(1)[0][0] for k, c in clabel.items()}
    for k, c in clabel.items():  # parent label from children if it never occurs alone
        if ", " in clab[k] and ", " not in k:
            clab[k] = clab[k].split(", ")[0]
    for k, v in premap.items():  # "Final Jōmon period" -> "Jōmon period"
        if v not in plabel:
            plabel[v] = plabel.get(k, v).split(" ", 1)[-1]

    # sub-level names (staffordshire, venice, java, ...) -> full key, for AIC places
    sub_index, seen = {}, collections.Counter()
    for k in cult:
        if ", " in k:
            seen[k.split(", ", 1)[1]] += 1
            sub_index[k.split(", ", 1)[1]] = k
    sub_index = {s: k for s, k in sub_index.items() if seen[s] == 1 and s not in cult and s != "export"}
    aic, aic_files = aic_counts(sub_index) if os.path.isdir(AIC_DIR) else (collections.Counter(), 0)
    print(f"AIC: {aic_files} artworks read; {sum(aic.values())} culture attributions")

    aat = None
    if not args.no_aat:
        terms = load_aat()
        if terms:
            aat = AATIndex(terms)
            print(f"AAT: {len(terms)} Styles and Periods terms")

    def stats(a):
        return {
            "objects": a.n, "objects_sole": a.sole, "timeline_works": a.tl, "highlights": a.hl,
            "begin_median": median(a.begin), "end_median": median(a.end),
            "dominant_department": a.dept.most_common(1)[0][0] if a.dept else "",
            "dominant_department_share": round(a.dept.most_common(1)[0][1] / a.n, 2) if a.n else "",
            "top_classifications": top(a.cls),
            "example_object_ids": " ".join(i for _, _, i in sorted(a.ex)[:5]),
        }

    def aat_cols(heads, ctx):
        if not aat:
            return {"aat_id": "", "aat_label": "", "aat_match": ""}
        tid, lab, level = aat.lookup(heads, ctx)
        return {"aat_id": tid, "aat_label": lab, "aat_match": level}

    rows = []
    for k, a in cult.items():
        heads, ctx = culture_heads(k)
        if a.begin and statistics.median(a.begin) < 500:
            ctx += " ancient"  # Egyptian (ancient) vs Egyptian (modern)
        rows.append({"kind": "culture", "key": k, "label": clab[k], "parent": parent_key(k) or "",
                     "culture": k, "period": "", "objects_direct": a.direct,
                     "culture_source": top(a.labels, 2), "raw_strings": len(a.raw),
                     "top_raw_strings": top(a.raw), **stats(a),
                     "top_periods": top(a.per, 3, plabel), "top_cultures": "",
                     "aic_objects": aic.get(k, 0), **aat_cols(heads, ctx)})
    for (k, p), a in cper.items():
        if a.n < args.min_objects and not a.tl:
            continue
        base = k.split(", ")[0]
        ph = [("exact", p), ("exact", f"{p} {base}")]
        rows.append({"kind": "culture_period", "key": f"{k} | {p}",
                     "label": f"{clab[k]} | {plabel.get(p, p)}", "parent": k, "culture": k,
                     "period": p, "objects_direct": a.n, "culture_source": "", "raw_strings": len(a.raw),
                     "top_raw_strings": top(a.raw), **stats(a), "top_periods": "",
                     "top_cultures": "", "aic_objects": "", **aat_cols(ph, k.replace(",", ""))})
    for p, a in per.items():
        if a.n < args.min_objects and not a.tl:
            continue
        ctx = " ".join(c.replace(",", "") for c, _ in a.cult.most_common(3))
        rows.append({"kind": "period", "key": p, "label": plabel.get(p, p), "parent": "",
                     "culture": "", "period": p, "objects_direct": a.n, "culture_source": "",
                     "raw_strings": "", "top_raw_strings": "", **stats(a), "top_periods": "",
                     "top_cultures": top(a.cult, 3, clab), "aic_objects": "",
                     **aat_cols([("exact", p)], ctx)})
    order = {"culture": 0, "culture_period": 1, "period": 2}
    rows.sort(key=lambda r: (order[r["kind"]], -r["objects"], r["key"]))
    fields = ["kind", "key", "label", "parent", "culture", "period", "objects", "objects_sole",
              "objects_direct", "timeline_works", "highlights", "begin_median", "end_median",
              "dominant_department", "dominant_department_share", "top_classifications",
              "top_periods", "top_cultures", "raw_strings", "top_raw_strings", "culture_source",
              "example_object_ids", "aic_objects", "aat_id", "aat_label", "aat_match"]
    out1 = os.path.join(OUT_DIR, "unattributed_cultures.csv")
    write(out1, rows, fields)

    trows = []
    for (kind, k, p, c), a in ocls.items():
        if a.n < args.min_objects and not a.tl:
            continue
        label = clab[k] + (f" | {plabel.get(p, p)}" if p else "") + f" / {c}"
        trows.append({"kind": kind, "key": f"{k}{' | ' + p if p else ''} / {c}", "label": label,
                      "culture": k, "period": p,
                      "classification" if "class" in kind else "technique": c, **stats(a)})
    korder = {"culture_class": 0, "culture_technique": 1, "culture_period_class": 2,
              "culture_period_technique": 3}
    trows.sort(key=lambda r: (korder[r["kind"]], -r["objects"], r["key"]))
    tfields = ["kind", "key", "label", "culture", "period", "classification", "technique",
               "objects", "objects_sole", "timeline_works", "highlights", "begin_median",
               "end_median", "dominant_department", "dominant_department_share",
               "top_classifications", "example_object_ids"]
    out2 = os.path.join(OUT_DIR, "unattributed_object_traditions.csv")
    write(out2, trows, tfields)

    # summary
    crow = [r for r in rows if r["kind"] == "culture"]
    print(f"\n{len(raw_cultures)} raw Culture strings -> {len(crow)} normalised cultures "
          f"({sum(1 for r in crow if not r['parent'])} base, {sum(1 for r in crow if r['parent'])} sub)")
    for t in (50, 500):
        print(f"  >= {t} objects: {sum(1 for r in crow if r['objects'] >= t)}")
    print(f"  with Timeline works: {sum(1 for r in crow if r['timeline_works'])}")
    if aat:
        for kind in ("culture", "culture_period", "period"):
            rs = [r for r in rows if r["kind"] == kind]
            big = [r for r in rs if r["objects"] >= 50]
            hit = lambda xs: sum(1 for r in xs if r["aat_match"] in ("exact", "sub"))
            print(f"  AAT {kind}: {hit(rs)}/{len(rs)} exact/sub; >=50 objects {hit(big)}/{len(big)}")
    print(f"wrote {out1} ({len(rows)} rows) and {out2} ({len(trows)} rows)")


if __name__ == "__main__":
    main()
