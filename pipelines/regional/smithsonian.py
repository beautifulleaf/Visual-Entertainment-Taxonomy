"""Smithsonian Open Access object records for the regional sweeps (visual-art-plan.md §2, §2A).

The regional sweeps (decided 2026-10-28) bring in collections that record each
region's own dynasty / period / culture labels, which override the labels the
Met-derived pipeline infers. This script harvests those labels, as recorded,
from the Smithsonian art units.

Source: the Smithsonian Open Access bulk metadata in the public AWS open-data
bucket "smithsonian-open-access" (CC0, no key needed):
  https://smithsonian-open-access.s3-us-west-2.amazonaws.com/metadata/edan/<unit>/
      index.txt            list of the data files (missing for some units; the
                           bucket listing is used then)
      00.txt ... ff.txt    one EDAN JSON record per line (plain text, not bz2)
Layout as inspected 2026-10-28. The bucket carries only the open-access
(CC0-image) subset of each unit, not the full catalogue: the National Museum of
Asian Art has ~4.7k records, African Art ~0.1k, Hirshhorn ~0.5k.

Units harvested (bucket prefix -> museum):
  fsg, nmaa  National Museum of Asian Art (Freer|Sackler). "nmaa" duplicates
             "fsg" record for record; both are read and deduplicated by record ID,
             and both are reported as unit NMAA.
  nmafa      National Museum of African Art
  nmai       National Museum of the American Indian
  chndm      Cooper Hewitt, Smithsonian Design Museum
  saam       Smithsonian American Art Museum (archival "ead_component" records skipped)
  hmsg       Hirshhorn Museum and Sculpture Garden
Only "edanmdm" (object) records are kept.

Fields are kept as recorded. Period/dynasty labels come from the freetext date
entries other than "Date" (Freer: label "Period" -> "Ming dynasty", "Safavid
period"), the Freer notes "School/Tradition" and "Court", Hirshhorn's "School",
the "Style" entry, period-like topics ("Heian period (794 - 1185)"), and the
parenthetical period in NMAI dates ("3,000 BC-AD 900 (Late Archaic to Late
Woodland period)"). Culture comes from the freetext "Culture" entry, NMAI's
"Culture/People" name entry and nmaiculture_* hierarchy, the indexed culture
terms, and placeholder makers ("Akan artist" -> Akan) as a last resort.

Raw files are cached gzip-compressed in data/raw/smithsonian/<unit>/ (about a
tenth of their size); --no-cache streams without keeping them.

Outputs (data/interim/regional/):
  smithsonian_objects.csv   one row per object: unit, record id, title, object
      type/name, culture (+source), NMAI culture hierarchy, place, countries,
      period/dynasty fields, school/style, period topics, date text, begin/end
      year, makers ("role: name" with life dates), maker identifiers,
      medium/materials, technique, CC0 metadata, has image, CC0 image, link.
  smithsonian_units.csv     per unit: objects and how many have culture, period,
      parsed date, maker, maker identifiers, image, CC0 image.
  smithsonian_cultures.csv  per unit x culture x period (kind = culture,
      culture_period, period): objects, begin min / median / end max, top
      object types, top media, example record IDs.
  smithsonian_makers.csv    per maker (normalised name + life dates): objects in
      total and per unit, roles, placeholder flag, identifiers, cultures seen.

Usage: python3 pipelines/regional/smithsonian.py [--units fsg,nmaa,...] [--no-cache]
                                                 [--workers 8]
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
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw", "smithsonian")
OUT_DIR = os.path.join(ROOT, "data", "interim", "regional")
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"
BUCKET = "https://smithsonian-open-access.s3-us-west-2.amazonaws.com"

# bucket prefix -> reported unit
UNITS = {"fsg": "NMAA", "nmaa": "NMAA", "nmafa": "NMAfA", "nmai": "NMAI",
         "chndm": "CHNDM", "saam": "SAAM", "hmsg": "HMSG"}

# name roles that are provenance, collecting or subject, not making
NON_MAKER_ROLE = re.compile(
    r"owner|seller|collector|donor|expedition|excavator|agent|iacb|presenter|funding|"
    r"honoree|lender|auction|subject|sitter|dedicatee|client|patron|student at|^for$|"
    r"culture/people|retailer|commissioner|previous|exchang|formerly attributed|custodian",
    re.I)
PLACEHOLDER = re.compile(
    r"^(unidentified|unknown|anonymous|not recorded)\b|^([A-Z][\w'-]+(?: [A-Z][\w'-]+)?) "
    r"(artist|artists|maker|makers|workshop|potter|weaver|carver|smith)s?$")
QUALIFIER = re.compile(
    r"^(traditionally attributed to|attributed to|formerly attributed to|possibly by|"
    r"probably by|workshop of|studio of|circle of|follower of|school of|style of|"
    r"manner of|after|copy after|possibly|probably|signed|inscribed by|by)\s+", re.I)
PERIOD_WORD = re.compile(
    r"\b(dynasty|period|era|reign|kingdom|empire|sultanate|caliphate|shogunate|"
    r"republic of china|three kingdoms|warring states|horizon)\b", re.I)
ID_PATTERNS = [
    ("ulan", re.compile(r"(?:vocab\.getty\.edu/(?:page/)?ulan/|ulan[:/ ]?)(5\d{8})", re.I)),
    ("wikidata", re.compile(r"wikidata\.org/(?:wiki|entity)/(Q\d+)", re.I)),
    ("viaf", re.compile(r"viaf\.org/viaf/(\d+)", re.I)),
    ("lcnaf", re.compile(r"id\.loc\.gov/authorities/names/(n[a-z]?\d+)", re.I)),
]


# ------------------------------------------------------------------ download

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def unit_files(prefix):
    try:
        urls = fetch(f"{BUCKET}/metadata/edan/{prefix}/index.txt").decode().split()
        if urls:
            return urls
    except urllib.error.HTTPError:
        pass
    keys, token = [], None
    while True:
        q = f"{BUCKET}/?list-type=2&prefix=metadata/edan/{prefix}/"
        if token:
            q += "&continuation-token=" + urllib.parse.quote(token)
        x = fetch(q).decode()
        keys += re.findall(r"<Key>([^<]+\.txt)</Key>", x)
        m = re.search(r"<NextContinuationToken>([^<]+)<", x)
        if not m:
            break
        token = m.group(1)
    return [f"{BUCKET}/{k}" for k in keys if not k.endswith("index.txt")]


def load_file(prefix, url, cache):
    path = os.path.join(RAW, prefix, os.path.basename(url) + ".gz")
    if cache and os.path.exists(path):
        with gzip.open(path, "rb") as f:
            data = f.read()
    else:
        for attempt in range(4):
            try:
                data = fetch(url)
                break
            except Exception:
                if attempt == 3:
                    raise
        if cache:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with gzip.open(path + ".part", "wb", compresslevel=6) as f:
                f.write(data)
            os.replace(path + ".part", path)
    return data.decode("utf-8").splitlines()


# ------------------------------------------------------------------ parsing

def ft(c, field, label=None):
    """freetext entries of a field, optionally only those with a given label."""
    out = []
    for e in c.get("freetext", {}).get(field, []) or []:
        if label is None or (e.get("label") or "").lower() == label.lower():
            v = (e.get("content") or "").strip()
            if v:
                out.append(v)
    return out


def uniq(seq):
    seen, out = set(), []
    for s in seq:
        s = re.sub(r"\s+", " ", s).strip()
        if s and s.lower() not in seen:
            seen.add(s.lower())
            out.append(s)
    return out


CENTURY = re.compile(
    r"(?:(early|mid|middle|late|first half of(?: the)?|second half of(?: the)?|"
    r"first quarter of(?: the)?|last quarter of(?: the)?)[\s-]+)?(\d{1,2})(?:st|nd|rd|th)"
    r"(?=[\s-]*(?:or\s+\d{1,2}(?:st|nd|rd|th)[\s-]*)?(?:-\s*(?:early |mid |late )?"
    r"\d{1,2}(?:st|nd|rd|th)\s*)?centur)", re.I)
MILLENNIUM = re.compile(r"(\d)(?:st|nd|rd|th)[\s-]*millenni", re.I)
YEAR = re.compile(r"(?<!\d)(?<!\d\.)(\d{1,5})(s?)(?!\d)")
BC = re.compile(r"^\s*(?:B\.?C\.?E?\.?|BCE)\b", re.I)
AD = re.compile(r"\b(?:A\.?D\.?|C\.?E\.?)\s*$", re.I)


def parse_years(text):
    """(begin, end) years from a free-text date; BCE as negative. None if unparseable."""
    if not text:
        return None, None
    t = text.replace("–", "-").replace("—", "-").replace("−", "-")
    t = re.sub(r"(\d),(\d{3})", r"\1\2", t)
    bce_all = bool(re.search(r"\bB\.?C\.?E?\b|\bBCE\b", t, re.I)) and not re.search(
        r"\bA\.?D\.?\b|\bC\.?E\.?\b(?<!BCE)", t)
    spans = []
    for m in CENTURY.finditer(t):
        n, mod = int(m.group(2)), (m.group(1) or "").lower()
        bc = bool(re.search(r"\bB\.?C", t[m.end():m.end() + 25], re.I)) or bce_all
        if bc:
            a, b = -(n * 100), -(n * 100 - 99)
        else:
            a, b = (n - 1) * 100, (n - 1) * 100 + 99
        if mod.startswith("early") or mod.startswith("first quarter"):
            b = a + 33
        elif mod.startswith("mid"):
            a, b = a + 33, a + 66
        elif mod.startswith("late") or mod.startswith("last quarter"):
            a = a + 66
        elif mod.startswith("first half"):
            b = a + 49
        elif mod.startswith("second half"):
            a = a + 50
        spans.append((a, b))
    for m in MILLENNIUM.finditer(t):
        n = int(m.group(1))
        bc = bool(re.search(r"\bB\.?C", t[m.end():m.end() + 25], re.I))
        spans.append((-(n * 1000), -(n * 1000 - 999)) if bc else ((n - 1) * 1000, n * 1000 - 1))
    stripped = CENTURY.sub(" ", MILLENNIUM.sub(" ", t))
    stripped = re.sub(r"\d{1,2}(?:st|nd|rd|th)\b", " ", stripped)
    years = []
    prev = None
    for m in YEAR.finditer(stripped):
        v = int(m.group(1))
        after = stripped[m.end():m.end() + 8]
        before = stripped[max(0, m.start() - 6):m.start()]
        bc = bool(BC.match(after)) or bce_all
        if v == 0 or (v > 2100 and not bc):
            continue
        ad = bool(AD.search(before)) or bool(re.match(r"^\s*(?:A\.?D|C\.?E)\b", after))
        if v < 100 and not (bc or ad or m.group(2)):
            # "1615-68": abbreviated end year
            if prev is not None and prev > 999 and stripped[m.start() - 1:m.start()] == "-":
                v = (prev // 100) * 100 + v
            else:
                continue
        if bc:
            years.append(-v)
            # "500-300 BCE": the start of a range shares the era of its end
            if years and len(years) >= 2 and years[-2] > 0 and not ad and \
                    "-" in stripped[stripped.rfind(str(abs(years[-2])), 0, m.start()):m.start()]:
                if abs(years[-2]) > v:
                    years[-2] = -years[-2]
        else:
            years.append(v)
            if m.group(2):  # 1880s
                years.append(v + (99 if v % 100 == 0 and v % 1000 else 9))
        prev = v
    for y in years:
        spans.append((y, y))
    if not spans:
        return None, None
    return min(a for a, _ in spans), max(b for _, b in spans)


def indexed_years(dates):
    ys = []
    for d in dates or []:
        m = re.match(r"^(\d{1,4})s$", str(d).strip())
        if m:
            v = int(m.group(1))
            ys += [v, v + (99 if v % 100 == 0 else 9)]
        m = re.match(r"^(\d{1,4})s? BCE$", str(d).strip())
        if m:
            v = -int(m.group(1))
            ys += [v - 99, v]
    return (min(ys), max(ys)) if ys else (None, None)


LIFE = [
    re.compile(r"\b(?:b\.|born)[^0-9]{0,60}?(\d{3,4})\s*[-/]?.{0,60}?(?:d\.|died)[^0-9]{0,60}?(\d{3,4})", re.I),
    re.compile(r"(?<!\d)(\d{3,4})(?:/\d{1,2})?\??\s*[-–]\s*(?:ca\.\s*|c\.\s*)?(\d{3,4})(?!\d)"),
]


def parse_maker(raw):
    """name, birth, death, nationality/descriptor from a Smithsonian name string."""
    s = re.sub(r"\s+", " ", raw).strip()
    s2 = QUALIFIER.sub("", s)
    s2 = QUALIFIER.sub("", s2)
    birth = death = None
    for rx in LIFE:
        m = rx.search(s2)
        if m:
            birth, death = int(m.group(1)), int(m.group(2))
            if death < birth:
                birth = death = None
                continue
            break
    if birth is None:
        m = re.search(r"\b(?:b\.|born)\s*(?:ca\.\s*)?(\d{3,4})", s2, re.I)
        if m:
            birth = int(m.group(1))
        m = re.search(r"\b(?:d\.|died)\s*(?:ca\.\s*)?(\d{3,4})", s2, re.I)
        if m:
            death = int(m.group(1))
    name = re.split(r"\s+\(|,\s", s2, maxsplit=1)[0].strip(" ,;")
    rest = s2[len(name):].strip(" ,")
    desc = ""
    m = re.match(r"^\(([^)]*)\)", rest)
    if m and not re.search(r"\d", m.group(1)) and "," not in m.group(1):
        rest = rest[m.end():].strip(" ,")  # NMAI aliases in parentheses
    parts = [p.strip() for p in re.split(r",", rest.strip("()")) if p.strip()]
    if parts and not re.search(r"\d|\bborn\b|\bb\.|active", parts[0]):
        desc = parts[0]
    return name, birth, death, desc


def norm_name(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s).split())


def find_ids(text):
    out = []
    for kind, rx in ID_PATTERNS:
        for m in rx.finditer(text):
            v = f"{kind}:{m.group(1)}"
            if v not in out:
                out.append(v)
    return out


def parse_record(d, unit):
    c = d.get("content", {})
    dnr = c.get("descriptiveNonRepeating", {})
    ix = c.get("indexedStructured", {}) or {}
    rec = {"unit": unit, "record_id": dnr.get("record_ID", ""),
           "title": (dnr.get("title") or {}).get("content") or d.get("title", "")}
    rec["accession"] = "; ".join(uniq(ft(c, "identifier", "Accession Number") + ft(c, "identifier", "Object number")
                                      + ft(c, "identifier", "Catalog Number")))
    rec["object_type"] = "; ".join(uniq(ft(c, "objectType", "Type") + ft(c, "objectType", "Object Type")))
    rec["object_name"] = "; ".join(uniq(ft(c, "objectType", "Object Name") + ft(c, "physicalDescription", "Object Name")
                                        + ft(c, "title", "Object Name") + ft(c, "objectType", "Indigenous Term")))
    rec["object_type_indexed"] = "; ".join(uniq(ix.get("object_type", []) or []))

    # makers
    makers, ids_all, placeholders = [], [], []
    for e in c.get("freetext", {}).get("name", []) or []:
        role, val = (e.get("label") or "").strip(), (e.get("content") or "").strip()
        if not val or NON_MAKER_ROLE.search(role):
            continue
        name, birth, death, desc = parse_maker(val)
        ph = bool(PLACEHOLDER.search(name))
        if ph:
            m = PLACEHOLDER.search(name)
            if m.group(2):
                placeholders.append(m.group(2))
        makers.append({"role": role, "raw": val, "name": name, "birth": birth, "death": death,
                       "desc": desc, "placeholder": ph, "ids": find_ids(json.dumps(e))})
    # identifiers anywhere in the record (names in indexedStructured may carry them)
    rec_ids = find_ids(json.dumps(c.get("indexedStructured", {})) + json.dumps(c.get("freetext", {}).get("name", [])))
    for m in makers:
        ids_all += m["ids"]
    rec["makers"] = " | ".join(
        f"{m['role']}: {m['name']}" + (f" ({m['birth'] or ''}-{m['death'] or ''})" if m["birth"] or m["death"] else "")
        for m in makers)
    rec["makers_raw"] = " | ".join(f"{m['role']}: {m['raw']}" for m in makers)
    rec["maker_ids"] = "; ".join(uniq(ids_all + rec_ids))
    rec["n_makers_named"] = sum(1 for m in makers if not m["placeholder"])

    # culture
    cult_ft = uniq(ft(c, "culture", "Culture") + [v for e in (c.get("freetext", {}).get("name", []) or [])
                                                   if (e.get("label") or "").lower() == "culture/people"
                                                   for v in [(e.get("content") or "").strip()]])
    cult_ix = uniq(ix.get("culture", []) or [])
    rec["culture"], rec["culture_source"] = "", ""
    if cult_ft:
        rec["culture"], rec["culture_source"] = "; ".join(cult_ft), "recorded"
    elif placeholders:
        rec["culture"], rec["culture_source"] = "; ".join(uniq(placeholders)), "maker"
    elif cult_ix:
        generic = {"indians of north america", "native americans", "indians of south america",
                   "indians of central america", "indians of mexico", "indians of the west indies"}
        spec = [x for x in cult_ix if x.lower() not in generic]
        if spec:
            rec["culture"], rec["culture_source"] = spec[0], "indexed"
    rec["culture_indexed"] = "; ".join(cult_ix)
    for k in ("continent", "culture_area", "culture_subarea", "archeol_1", "archeol_2", "archeol_3"):
        rec[f"nmai_{k}"] = "; ".join(uniq(ix.get(f"nmaiculture_{k}", []) or []))

    # place
    rec["place"] = " | ".join(f"{e.get('label')}: {e.get('content')}" for e in c.get("freetext", {}).get("place", []) or []
                              if e.get("content"))
    countries = []
    for g in ix.get("geoLocation", []) or []:
        if isinstance(g, dict):
            v = (g.get("L2") or {}).get("content")
            if v:
                countries.append(v)
    rec["countries"] = "; ".join(uniq(countries))

    # period / dynasty / era as recorded
    period, date_text = [], []
    for e in c.get("freetext", {}).get("date", []) or []:
        lab, val = (e.get("label") or "").strip(), (e.get("content") or "").strip()
        if not val:
            continue
        if lab.lower() in ("date", "date created", "date made", "dates"):
            date_text.append(val)
            m = re.search(r"\(([^()]*\b(?:period|phase|horizon|culture|tradition|dynasty)\b[^()]*)\)", val, re.I)
            if m:
                period.append(m.group(1))
        else:
            period.append(val)
    date_text += ft(c, "unitdate")
    rec["period"] = "; ".join(uniq(period))
    school = ft(c, "notes", "School/Tradition") + ft(c, "notes", "Court") + ft(c, "setName", "School") \
        + ft(c, "physicalDescription", "Style")
    rec["school_style"] = "; ".join(uniq(school))
    topics = ft(c, "topic") + list(ix.get("topic", []) or [])
    rec["period_topics"] = "; ".join(uniq(t for t in topics if PERIOD_WORD.search(t)))
    rec["date"] = "; ".join(uniq(date_text))
    b, e_ = parse_years(" ; ".join(date_text))
    rec["date_source"] = "text" if b is not None else ""
    if b is None:
        b, e_ = indexed_years(ix.get("date"))
        rec["date_source"] = "indexed" if b is not None else ""
    rec["begin_year"], rec["end_year"] = ("" if b is None else b), ("" if e_ is None else e_)

    rec["medium"] = "; ".join(uniq(ft(c, "physicalDescription", "Medium") + ft(c, "physicalDescription", "Media/Materials")))
    rec["technique"] = "; ".join(uniq(ft(c, "physicalDescription", "Techniques")))
    rec["metadata_cc0"] = int((dnr.get("metadata_usage") or {}).get("access") == "CC0")
    media = (dnr.get("online_media") or {}).get("media", []) or []
    imgs = [m for m in media if m.get("type") == "Images"]
    rec["has_image"] = int(bool(imgs))
    rec["image_cc0"] = int(any((m.get("usage") or {}).get("access") == "CC0" for m in imgs))
    rec["record_link"] = dnr.get("record_link", "") or dnr.get("guid", "")
    return rec, makers


# ------------------------------------------------------------------ aggregation

def top(counter, n=5):
    return "; ".join(f"{k} ({v})" for k, v in counter.most_common(n) if k)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default=",".join(UNITS), help="bucket prefixes, comma-separated")
    ap.add_argument("--no-cache", action="store_true", help="stream without keeping raw files")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)

    objects, seen = [], set()
    maker_agg = {}
    for prefix in args.units.split(","):
        unit = UNITS.get(prefix, prefix.upper())
        urls = unit_files(prefix)
        n_rec = n_skip = 0
        with concurrent.futures.ThreadPoolExecutor(args.workers) as ex:
            futs = [ex.submit(load_file, prefix, u, not args.no_cache) for u in urls]
            for fut in concurrent.futures.as_completed(futs):
                for line in fut.result():
                    if not line.strip():
                        continue
                    d = json.loads(line)
                    if d.get("type") != "edanmdm":
                        n_skip += 1
                        continue
                    rec, makers = parse_record(d, unit)
                    if rec["record_id"] in seen:
                        continue
                    seen.add(rec["record_id"])
                    n_rec += 1
                    objects.append(rec)
                    for m in makers:
                        key = (norm_name(m["name"]), m["birth"], m["death"])
                        if not key[0]:
                            continue
                        a = maker_agg.setdefault(key, {
                            "name": m["name"], "birth": m["birth"], "death": m["death"],
                            "desc": collections.Counter(), "roles": collections.Counter(),
                            "units": collections.Counter(), "ids": set(),
                            "cultures": collections.Counter(), "placeholder": m["placeholder"],
                            "raw": m["raw"], "records": set()})
                        if rec["record_id"] in a["records"]:
                            continue
                        a["records"].add(rec["record_id"])
                        a["units"][unit] += 1
                        a["roles"][m["role"]] += 1
                        a["desc"][m["desc"]] += 1
                        a["ids"].update(m["ids"])
                        if rec["culture"]:
                            a["cultures"][rec["culture"]] += 1
        print(f"{prefix}: {len(urls)} files, {n_rec} new object records, {n_skip} non-object skipped")

    cols = ["unit", "record_id", "accession", "title", "object_type", "object_name", "object_type_indexed",
            "culture", "culture_source", "culture_indexed", "nmai_continent", "nmai_culture_area",
            "nmai_culture_subarea", "nmai_archeol_1", "nmai_archeol_2", "nmai_archeol_3", "place", "countries",
            "period", "school_style", "period_topics", "date", "begin_year", "end_year", "date_source",
            "makers", "makers_raw", "n_makers_named", "maker_ids", "medium", "technique",
            "metadata_cc0", "has_image", "image_cc0", "record_link"]
    objects.sort(key=lambda r: (r["unit"], r["record_id"]))
    with open(os.path.join(OUT_DIR, "smithsonian_objects.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(objects)

    # per-unit summary
    units = collections.OrderedDict()
    for r in objects:
        u = units.setdefault(r["unit"], collections.Counter())
        u["objects"] += 1
        u["with_culture_recorded"] += r["culture_source"] == "recorded"
        u["with_culture_any"] += bool(r["culture"])
        u["with_period"] += bool(r["period"])
        u["with_period_or_school"] += bool(r["period"] or r["school_style"])
        u["with_period_any"] += bool(r["period"] or r["school_style"] or r["period_topics"])
        u["with_date_parsed"] += r["begin_year"] != ""
        u["with_named_maker"] += r["n_makers_named"] > 0
        u["with_maker_ids"] += bool(r["maker_ids"])
        u["has_image"] += r["has_image"]
        u["image_cc0"] += r["image_cc0"]
        u["metadata_cc0"] += r["metadata_cc0"]
    ucols = ["objects", "with_culture_recorded", "with_culture_any", "with_period", "with_period_or_school",
             "with_period_any", "with_date_parsed", "with_named_maker", "with_maker_ids", "has_image",
             "image_cc0", "metadata_cc0"]
    with open(os.path.join(OUT_DIR, "smithsonian_units.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["unit"] + ucols)
        for u, c in units.items():
            w.writerow([u] + [c[k] for k in ucols])
            print(u, " ".join(f"{k}={c[k]}" for k in ucols))

    # cultures x periods
    cells = {}
    for r in objects:
        period = r["period"] or r["school_style"] or r["period_topics"].split("; ")[0]
        culture = r["culture"]
        for kind, cu, pe in (("culture", culture, ""), ("culture_period", culture, period), ("period", "", period)):
            if (kind == "culture" and not cu) or (kind == "culture_period" and not (cu and pe)) or \
                    (kind == "period" and not pe):
                continue
            a = cells.setdefault((r["unit"], kind, cu, pe), {"n": 0, "b": [], "e": [], "types": collections.Counter(),
                                                             "media": collections.Counter(), "ex": [],
                                                             "src": collections.Counter()})
            a["n"] += 1
            if r["begin_year"] != "":
                a["b"].append(r["begin_year"])
                a["e"].append(r["end_year"])
            a["types"][r["object_type"] or r["object_name"]] += 1
            a["media"][r["medium"][:60]] += 1
            a["src"][r["culture_source"]] += 1
            if len(a["ex"]) < 5:
                a["ex"].append(r["record_id"])
    with open(os.path.join(OUT_DIR, "smithsonian_cultures.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["unit", "kind", "culture", "period", "objects", "begin_min", "begin_median", "end_max",
                    "culture_source", "top_object_types", "top_media", "example_record_ids"])
        for (u, kind, cu, pe), a in sorted(cells.items(), key=lambda kv: (kv[0][0], kv[0][1], -kv[1]["n"])):
            w.writerow([u, kind, cu, pe, a["n"], min(a["b"]) if a["b"] else "",
                        int(statistics.median(a["b"])) if a["b"] else "", max(a["e"]) if a["e"] else "",
                        top(a["src"], 3), top(a["types"]), top(a["media"], 3), "; ".join(a["ex"])])

    # makers
    unit_names = list(units)
    with open(os.path.join(OUT_DIR, "smithsonian_makers.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "birth", "death", "descriptor", "objects"] + [f"objects_{u}" for u in unit_names]
                   + ["roles", "placeholder", "identifiers", "top_cultures", "example_raw"])
        for a in sorted(maker_agg.values(), key=lambda a: -len(a["records"])):
            w.writerow([a["name"], a["birth"] or "", a["death"] or "", top(a["desc"], 1).rsplit(" (", 1)[0],
                        len(a["records"])] + [a["units"][u] for u in unit_names]
                       + [top(a["roles"], 4), int(a["placeholder"]), "; ".join(sorted(a["ids"])),
                          top(a["cultures"], 3), a["raw"]])
    print(f"objects {len(objects)}, culture/period cells {len(cells)}, makers {len(maker_agg)} "
          f"({sum(1 for a in maker_agg.values() if a['ids'])} with identifiers)")


if __name__ == "__main__":
    main()
