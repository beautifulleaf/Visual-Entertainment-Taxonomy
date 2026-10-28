"""World-cultures sweep: extra non-Western and unattributed traditions
(visual-art-plan.md §2A, §2.1b).

Gathering scope is NODES (cultures, traditions, production centres, workshops)
plus EVIDENCE (object counts, holding institutions, representative works), not
object completeness. This script reads two large Dutch open datasets that are
strong in exactly the traditions the earlier sweeps left thin (Indonesia,
Suriname and the Caribbean, Japan export wares, Oceania, Africa, costume,
textiles, carving, metalwork) and measures how many culture keys they add
over everything already gathered.

Sources (each can be disabled with --skip):

  rijks  Rijksmuseum historical LIDO dump (2020-01, CC0, ~411 MB zip holding a
         12.5 GB XML file; GitHub release of Rijksmuseum/rijksmuseum.github.io,
         linked from data.rijksmuseum.nl/docs/data-dumps/historical-dumps).
         The current multi-domain dump (2024-11) has no object archive, only
         images, places, concepts, library records, so the LIDO dump is the
         bulk route; the Search API / OAI-PMH were not needed.
         LIDO has no culture field: the culture key is derived from the
         production place (eventPlace of the creation event), mapped to a
         country / region through PLACE_COUNTRY and the Rijksmuseum SKOS
         thesaurus (201911, broader relations for ~460 places). Kept: objects
         made outside Europe, plus European textiles, costume, lace and folk
         objects that record a production place. Prints, photographs, drawings
         by European makers, coins and medals are dropped.
         The zip is streamed (never extracted); the slim per-record extract is
         cached as data/raw/regional/world_extra/rijks/records.jsonl.gz.
  nmvw   Wereldmuseum / Nationaal Museum van Wereldculturen (Tropenmuseum,
         Museum Volkenkunde, Afrika Museum, Wereldmuseum Rotterdam), dataset
         nmvw/collection-archives on the Colonial Collections TriplyDB
         (data.colonialcollections.nl, CC0, Linked Art / CIDOC-CRM, updated
         2026-10-24): full N-Triples download, 1.8 GB gzip, 120M statements in
         16 graphs (objects, geography-objects, makers, material-objects,
         thesaurus, ...). The dataset has no SPARQL service and per-graph
         downloads are not exposed, so the whole file is downloaded once to
         data/raw/regional/world_extra/nmvw/ and streamed. The NMVW thesaurus
         (nmvw/thesaurus, mapped to AAT / GeoNames) gives labels for the
         culture and place concepts.
  bm     British Museum Collection Online: NOT HARVESTED. robots.txt (checked
         2026-10-28) disallows anthropic-ai, ClaudeBot and Claude-Web for the
         whole site, sets Content-Signal ai-train=no, and disallows /search
         for every agent. Per project rule the source stops there; with --only
         bm the script re-reads robots.txt and reports, but never downloads
         collection data.

Culture keys reuse pipelines/unattributed/build_traditions.py (culture_keys,
fold, tidy, DEMONYM, ALIAS), so they line up with the Met / AIC keys.

Node-gain measurement: every key found here is compared with the keys already
gathered: data/interim/unattributed_cultures.csv (Met / AIC) and the culture /
tradition columns of data/interim/regional/*.csv (Smithsonian, East Asia,
South & Southeast Asia, Africa, Americas & Oceania, Africa/Oceania targeted,
Islamic, Himalaya & Central Asia). A key counts as known when the key, its
leaf ("akan, asante" -> "asante") or its alias matches any name in those
files. For known keys the earlier holding institutions are collected too, so
the output says when a node gained a new holding institution.

Outputs (data/interim/regional/):
  world_extra_objects.csv   slim evidence rows: source, id, title, culture
                            key(s) and label, culture_from (field the key came
                            from), place, country, region, object type /
                            group, period, dates, maker, attributed, materials,
                            institution, url
  world_extra_cultures.csv  one row per culture key (base and sub level):
                            label, region, object groups, period range, counts
                            per source, holding institutions, known/new flag,
                            institutions already holding it, new institution
                            flag, sample URLs
Raw caches: data/raw/regional/world_extra/<source>/.

Usage: python3 pipelines/regional/world_cultures_extra.py [--skip rijks,nmvw,bm]
           [--only ...] [--fetch-only] [--limit N]
Long runs log progress to stderr; the Rijks and NMVW stream passes are cached,
so a re-run only rebuilds the tables.
"""
import argparse
import collections
import csv
import glob
import gzip
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile

csv.field_size_limit(1 << 24)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw", "regional", "world_extra")
INTERIM = os.path.join(ROOT, "data", "interim")
OUT_DIR = os.path.join(INTERIM, "regional")
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"

sys.path.insert(0, os.path.join(ROOT, "pipelines", "unattributed"))
from build_traditions import culture_keys, fold, tidy, DEMONYM, ALIAS  # noqa: E402

SOURCES = ("rijks", "nmvw", "bm")
SOURCE_INST = {"rijks": "Rijksmuseum", "nmvw": "Wereldmuseum (NMVW)", "bm": "British Museum"}

RIJKS_RELEASE = "https://github.com/Rijksmuseum/rijksmuseum.github.io/releases/download/1.0.0/"
RIJKS_LIDO = "202001-rma-lido-collection.zip"
RIJKS_SKOS = "201911-rma-skos-thesaurus.zip"
NMVW_DUMP = "https://data.colonialcollections.nl/nmvw/collection-archives/download.nt.gz"
NMVW_THES = "https://data.colonialcollections.nl/nmvw/thesaurus/download.nt.gz"
BM_ROBOTS = "https://www.britishmuseum.org/robots.txt"


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, file=sys.stderr, flush=True)


def download(url, path):
    """Download once (resumable via .part + HTTP Range)."""
    if os.path.exists(path):
        return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    part = path + ".part"
    for attempt in range(6):
        have = os.path.getsize(part) if os.path.exists(part) else 0
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        if have:
            req.add_header("Range", f"bytes={have}-")
        try:
            with urllib.request.urlopen(req, timeout=120) as r, open(part, "ab" if have else "wb") as f:
                if have and r.status != 206:
                    f.truncate(0)
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b)
            os.replace(part, path)
            log(f"downloaded {url} -> {path} ({os.path.getsize(path) >> 20} MB)")
            return path
        except (urllib.error.URLError, OSError) as e:
            log(f"download error {url}: {e}; retry {attempt + 1}")
            time.sleep(10 * (attempt + 1))
    raise SystemExit(f"could not download {url}")


def write_csv(path, rows, cols):
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    os.replace(tmp, path)
    log(f"wrote {path} ({len(rows)} rows)")


# ================================================================== Rijksmuseum

LIDO = "{http://www.lido-schema.org}"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
CREATION = ("expression_creation", "production", "work_conception", "creation")


def _terms(el, tag="term"):
    """{lang: first text} for the direct <lido:term>/<appellationValue> children."""
    out = {}
    if el is None:
        return out
    for t in el.findall(LIDO + tag):
        if t.text and t.text.strip():
            out.setdefault(t.get(XML_LANG, ""), t.text.strip())
    return out


def _en(d):
    return d.get("en") or d.get("") or d.get("nl") or next(iter(d.values()), "")


def rijks_record(rec):
    g = rec.find
    out = {"rid": (g(LIDO + "lidoRecID").text or "").rsplit("/", 1)[-1] if g(LIDO + "lidoRecID") is not None else "",
           "url": (g(LIDO + "objectPublishedID").text or "") if g(LIDO + "objectPublishedID") is not None else ""}
    dm = g(LIDO + "descriptiveMetadata")
    if dm is None:
        return out
    out["types"] = [_en(_terms(w)) for w in dm.iter(LIDO + "objectWorkType")]
    out["types_nl"] = [_terms(w).get("nl", "") for w in dm.iter(LIDO + "objectWorkType")]
    out["classes"] = [_en(_terms(c)) for c in dm.iter(LIDO + "classification")]
    titles = [_terms(ts, "appellationValue") for ts in dm.iter(LIDO + "titleSet")]
    out["title"] = next((t["en"] for t in titles if t.get("en")), "") or next((_en(t) for t in titles if t), "")
    wid = dm.find(".//" + LIDO + "workID")
    out["objno"] = wid.text.strip() if wid is not None and wid.text else ""
    desc = [v.text for v in dm.iter(LIDO + "descriptiveNoteValue")
            if v.text and v.getparent().tag == LIDO + "objectDescriptionSet"]
    out["desc"] = (desc[0] if desc else "")[:300]
    places, pids, periods, makers, mats, techs, begins, ends = [], [], [], [], [], [], [], []
    for ev in dm.iter(LIDO + "event"):
        et = ev.find(LIDO + "eventType")
        cid = et.find(LIDO + "conceptID") if et is not None else None
        etype = (cid.text or "").rsplit("/", 1)[-1] if cid is not None else ""
        if etype not in CREATION:
            continue
        for pl in ev.iter(LIDO + "place"):
            nps = pl.find(LIDO + "namePlaceSet")
            nm = _en(_terms(nps, "appellationValue")) if nps is not None else ""
            pid = pl.find(LIDO + "placeID")
            if nm:
                places.append(nm)
                pids.append((pid.text or "").rsplit(".", 1)[-1] if pid is not None else "")
        for pn in ev.findall(LIDO + "periodName"):
            t = _en(_terms(pn))
            if t:
                periods.append(t)
        for d in ev.iter(LIDO + "date"):
            e, l = d.find(LIDO + "earliestDate"), d.find(LIDO + "latestDate")
            if e is not None and e.text:
                begins.append(e.text.strip())
            if l is not None and l.text:
                ends.append(l.text.strip())
        for air in ev.iter(LIDO + "actorInRole"):
            a = air.find(LIDO + "actor")
            nm = ""
            if a is not None:
                ns = a.find(LIDO + "nameActorSet")
                nm = _en(_terms(ns, "appellationValue")) if ns is not None else ""
            role = _en(_terms(air.find(LIDO + "roleActor")))
            attr = _en(_terms(air.find(LIDO + "attributionQualifierActor")))
            if nm:
                makers.append("|".join((nm, role, attr)))
        for tm in ev.iter(LIDO + "termMaterialsTech"):
            t = _en(_terms(tm))
            if not t:
                continue
            (techs if tm.get(LIDO + "type", "").endswith("technique") else mats).append(t)
    out.update(places=places, pids=pids, periods=periods, makers=makers, mats=mats[:6], techs=techs[:6],
               begin=min(begins, default=""), end=max(ends, default=""))
    return out


def extract_rijks(limit=None):
    """Stream the LIDO zip once and cache a slim record per object."""
    cache = os.path.join(RAW, "rijks", "records.jsonl.gz")
    if os.path.exists(cache) and not limit:
        return cache
    from lxml import etree
    zpath = download(RIJKS_RELEASE + RIJKS_LIDO, os.path.join(RAW, "rijks", RIJKS_LIDO))
    download(RIJKS_RELEASE + RIJKS_SKOS, os.path.join(RAW, "rijks", RIJKS_SKOS))
    out = cache + (".sample" if limit else "") + ".part"
    n = 0
    t0 = time.time()
    with zipfile.ZipFile(zpath) as z, gzip.open(out, "wt", encoding="utf-8") as f:
        name = z.namelist()[0]
        with z.open(name) as stream:
            for _, el in etree.iterparse(stream, events=("end",), tag=LIDO + "lido", huge_tree=True):
                try:
                    r = rijks_record(el)
                except (AttributeError, TypeError, ValueError) as e:
                    r = {"error": str(e)[:100]}
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                el.clear()
                while el.getprevious() is not None:
                    del el.getparent()[0]
                n += 1
                if n % 50000 == 0:
                    log(f"rijks: {n} records ({time.time() - t0:.0f}s)")
                if limit and n >= limit:
                    break
    final = cache + (".sample" if limit else "")
    os.replace(out, final)
    log(f"rijks: {n} records extracted -> {final}")
    return final


# ------------------------------------------------------------ place lexicon
# country label (as build_traditions' DEMONYM / culture_keys understand it) -> region
COUNTRY_REGION = {
    "China": "east_asia", "Japan": "east_asia", "Korea": "east_asia", "Taiwan": "east_asia",
    "Tibet": "himalaya_central_asia", "Nepal": "himalaya_central_asia", "Central Asia": "himalaya_central_asia",
    "Mongolia": "east_asia",
    "India": "south_asia", "Sri Lanka": "south_asia", "Pakistan": "south_asia", "Bangladesh": "south_asia",
    "Afghanistan": "west_asia_islamic",
    "Indonesia": "southeast_asia", "Thailand": "southeast_asia", "Cambodia": "southeast_asia",
    "Vietnam": "southeast_asia", "Laos": "southeast_asia", "Burma": "southeast_asia", "Malaysia": "southeast_asia",
    "Philippines": "southeast_asia", "Singapore": "southeast_asia", "Timor-Leste": "southeast_asia",
    "Iran": "west_asia_islamic", "Turkey": "west_asia_islamic", "Syria": "west_asia_islamic",
    "Iraq": "west_asia_islamic", "Egypt": "africa_north", "Arabia": "west_asia_islamic",
    "Caucasus": "west_asia_islamic", "Armenia": "west_asia_islamic", "Kurdistan": "west_asia_islamic",
    "Palestine": "west_asia_islamic", "Lebanon": "west_asia_islamic", "Yemen": "west_asia_islamic",
    "Morocco": "africa_north", "Algeria": "africa_north", "Tunisia": "africa_north", "Libya": "africa_north",
    "South Africa": "africa", "Kenya": "africa", "Congo": "africa", "Benin": "africa", "Ghana": "africa",
    "Nigeria": "africa", "Mali": "africa", "Mozambique": "africa", "Ethiopia": "africa", "Africa": "africa",
    "Suriname": "americas", "Caribbean": "americas", "Curacao": "americas", "Brazil": "americas",
    "Mexico": "americas", "Peru": "americas", "Paraguay": "americas", "Argentina": "americas",
    "Guatemala": "americas", "Colombia": "americas", "Venezuela": "americas", "Guyana": "americas",
    "United States": "americas_settler", "Canada": "americas_settler",
    "Papua New Guinea": "oceania", "New Guinea": "oceania", "New Zealand": "oceania", "Australia": "oceania",
    "Fiji": "oceania", "Oceania": "oceania",
}
# Rijksmuseum production place (folded) -> country label; Dutch and English spellings
_PC = {
    "China": "china kanton canton jingdezhen dehua shantou swatow zuid-china jiangsu yangzhou taizhou changzhou "
             "huai'an shanghai yantai henan shanxi kansu ordos-gebied juluxian ningh-sia peking beijing "
             "nanking nanjing fujian guangdong zhejiang shandong yixing longquan cizhou",
    "Japan": "japan arita seto satsuma kyoto tokyo edo mino kutani hirado karatsu shigaraki bizen takatori hagi "
             "iga tamba nagoya fukui nagasaki deshima agano nakamura yokohama osaka kakiemon imari nikko",
    "Korea": "korea",
    "Indonesia": "indonesia indonesie dutch east indies, the nederlands oost-indie indonesian archipelago indie "
                 "java west-java oost-java midden-java batavia jakarta jogjakarta yogyakarta surabaya malang "
                 "buitenzorg bogor semarang salatiga tegal rembang grissee madura trawulan majapahit lombok bali "
                 "sumatra noord-sumatra zuid-sumatra oost-sumatra atjeh aceh padang brastagi medan bangka muntok "
                 "borneo kalimantan celebes sulawesi noord-celebes south celebes molukken zuid-molukken "
                 "noord-molukken centraal-molukken ambon aru-eilanden timor flores savoe soemba sumba tlogosari "
                 "anyar candi sewu candi merak candi plaosan lampong jatiroto belawan bindjai langkat weltevreden "
                 "tandjong priok palembang makassar ternate banda",
    "India": "india voor-indie deccan golkonda golconda coromandelkust kashmir surat gujarat jaipur rajasthan "
             "kangra bikaner bundi mewar kotah kota mandi orissa centraal-india noord-india zuid-india "
             "noordwest-india noordoost-india tamil nadu bengalen bengal murshidabad shorapur sirohi jammu pahari "
             "chamba guler bilaspur udaipur mankot lucknow kishangar kishangarh jodhpur mathura vizagapatnam "
             "karnataka kerala delhi agra ahmedabad benares masulipatnam pulicat negapatnam",
    "Pakistan": "gandhara sindh lahore",
    "Sri Lanka": "sri lanka ceylon colombo kandy galle ja-ela hulftsdorp jaffna",
    "Iran": "iran persia perzie kashan nishapur hamadan midden-perzie ferahan kirman noordwest-perzie "
            "zuid-perzie shiraz isfahan gorgan sari amol garrus senneh serabend sultanabad karadagh west-perzie "
            "zuidwest-perzie oost-perzie noord-perzie gamron khurasan",
    "Afghanistan": "afghanistan herat",
    "Turkey": "turkije turkey klein-azie istanboel istanbul constantinopel iznik kula ghiordes ladik bergama "
              "konya kirsehir broussa ushak usak mudjur melas yuruk kemerihisar sivrihisar centraal-klein-azie "
              "oost-klein-azie zuidoost klein-azie kutahya",
    "Caucasus": "kaukasus shirvan kazak karabakh kuba dagestan talish khila kabistan gendje oost-kaukasus",
    "Armenia": "talin armenie",
    "Kurdistan": "koerdistan",
    "Central Asia": "centraal-azie turkestan oost-turkestan zuid-turkestan samarqand samarkand beshir turkmenie "
                    "beludshistan bukhara",
    "Syria": "syrie raqqa damascus",
    "Egypt": "egypte cairo caiiro gizeh luxor",
    "Arabia": "arabie",
    "Palestine": "palestina jeruzalem",
    "Thailand": "thailand siam sawankhalok ban chiang ayuthia khmer dvaravati",
    "Cambodia": "cambodja",
    "Vietnam": "vietnam tonkin noord-vietnam annam",
    "Laos": "laos",
    "Burma": "birma burma",
    "Malaysia": "malaysia sarawak malakka",
    "Singapore": "singapore",
    "Tibet": "tibet kham centraal-tibet",
    "Nepal": "nepal",
    "Bangladesh": "bangladesh",
    "Morocco": "marokko",
    "Algeria": "algerije biskra",
    "Tunisia": "tunesie tunis",
    "South Africa": "zuid-afrika kaapprovincie kaapstad cape of good hope mpumalanga pretoria",
    "Kenya": "kenia",
    "Congo": "congo",
    "Benin": "benin",
    "Ghana": "elmina goudkust ghana",
    "Mozambique": "mozambique",
    "Mali": "mali",
    "Africa": "afrika",
    "Suriname": "suriname paramaribo",
    "Curacao": "curacao",
    "Caribbean": "nederlandse antillen saba sint eustatius bonaire aruba sint maarten west-indie",
    "Brazil": "brasil brazilie",
    "Mexico": "mexico",
    "Peru": "zuid-peru peru lima",
    "Paraguay": "paraguay",
    "Argentina": "buenos aires",
    "Venezuela": "venezuela",
    "United States": "haida",
    "New Guinea": "nieuw-guinea",
    "New Zealand": "new zealand",
    "Fiji": "fiji",
}
PLACE_COUNTRY = {}
# multi-word names are listed with their words joined by single spaces; resolve greedily below
_MULTI = {"dutch east indies, the", "nederlands oost-indie", "indonesian archipelago", "west-java", "candi sewu",
          "candi merak", "candi plaosan", "south celebes", "aru-eilanden", "bindjai langkat", "tandjong priok",
          "sri lanka", "tamil nadu", "cape of good hope", "nederlandse antillen", "sint eustatius", "sint maarten",
          "buenos aires", "new zealand", "ban chiang", "zuidoost klein-azie", "klein-azie"}
# Dutch exonyms -> English, for sub-level labels
PLACE_EN = {"istanboel": "Istanbul", "constantinopel": "Istanbul", "kanton": "Canton", "golkonda": "Golconda",
            "coromandelkust": "Coromandel Coast", "bengalen": "Bengal", "jogjakarta": "Yogyakarta",
            "batavia": "Jakarta", "atjeh": "Aceh", "soemba": "Sumba", "savoe": "Savu", "celebes": "Sulawesi",
            "molukken": "Maluku", "aru-eilanden": "Aru Islands", "cambodja": "Cambodia", "birma": "Burma",
            "broussa": "Bursa", "ushak": "Usak", "kaapstad": "Cape Town", "kaapprovincie": "Cape Province",
            "samarqand": "Samarkand", "caiiro": "Cairo", "gizeh": "Giza", "edo": "Edo (Tokyo)",
            "kishangar": "Kishangarh", "kotah": "Kota", "ayuthia": "Ayutthaya", "noord-celebes": "North Sulawesi",
            "south celebes": "South Sulawesi", "west-java": "West Java", "oost-java": "East Java",
            "midden-java": "Central Java", "noord-sumatra": "North Sumatra", "zuid-sumatra": "South Sumatra",
            "oost-sumatra": "East Sumatra", "zuid-molukken": "South Maluku", "noord-molukken": "North Maluku",
            "centraal-molukken": "Central Maluku", "oost-turkestan": "East Turkestan"}
for _c, _names in _PC.items():
    s = " " + _names + " "
    for m in sorted(_MULTI, key=len, reverse=True):
        if " " + m + " " in s:
            PLACE_COUNTRY[m] = _c
            s = s.replace(" " + m + " ", " ")
    for w in s.split():
        PLACE_COUNTRY.setdefault(w, _c)
# names that are the country itself (no sub-level key)
COUNTRY_SELF = {"china", "japan", "korea", "indonesia", "indonesie", "dutch east indies, the", "nederlands oost-indie",
                "indonesian archipelago", "indie", "india", "voor-indie", "sri lanka", "ceylon", "iran", "persia",
                "perzie", "afghanistan", "turkije", "turkey", "kaukasus", "koerdistan", "centraal-azie", "syrie",
                "egypte", "arabie", "palestina", "thailand", "siam", "cambodja", "vietnam", "laos", "birma", "burma",
                "malaysia", "singapore", "klein-azie", "turkestan", "zuidoost klein-azie", "tibet", "nepal", "bangladesh", "marokko", "algerije", "tunesie",
                "zuid-afrika", "kenia", "congo", "benin", "mozambique", "mali", "afrika", "suriname", "curacao",
                "nederlandse antillen", "west-indie", "brasil", "brazilie", "mexico", "paraguay", "venezuela",
                "nieuw-guinea", "new zealand", "fiji", "armenie", "ghana"}
# compass / generic regional prefixes give no sub-level key
GENERIC_SUB = re.compile(r"^(noord|zuid|oost|west|midden|centraal|noordwest|noordoost|zuidwest|zuidoost)-(?!java|sumatra|celebes|molukken|turkestan)"
                         r"|^(south|north|east|west|central) ")
# European textile, lace and folk-costume centres kept from Europe (country label for the key)
EURO_CENTRES = {
    "brussels": "Belgium", "mechelen": "Belgium", "binche": "Belgium", "ieper": "Belgium", "geraardsbergen": "Belgium",
    "kortrijk": "Belgium", "lierre": "Belgium", "lier": "Belgium", "turnhout": "Belgium", "oudenaarde": "Belgium",
    "burano": "Italy", "venice": "Italy", "pellestrina": "Italy", "abruzzi": "Italy", "genua": "Italy",
    "alencon": "France", "argentan": "France", "bayeux": "France", "calais": "France", "chantilly": "France",
    "valenciennes": "France", "le puy": "France", "le puy-en-velay": "France", "lyon": "France", "caen": "France",
    "honiton": "England", "buckingham": "England", "nottingham": "England", "norwich": "England",
    "paisley": "Scotland", "limerick": "Ireland", "carrickmacross": "Ireland",
    "sankt gallen": "Switzerland", "plauen": "Germany", "krefeld": "Germany", "tonderen": "Denmark",
    "vadstena": "Sweden", "dalarna": "Sweden",
    "haarlem": "Netherlands", "hindeloopen": "Netherlands", "marken": "Netherlands", "volendam": "Netherlands",
    "zaanstreek": "Netherlands", "friesland": "Netherlands", "schiermonnikoog": "Netherlands",
    "walcheren": "Netherlands", "zeeland": "Netherlands", "scheveningen": "Netherlands", "west-friesland": "Netherlands",
    "staphorst": "Netherlands", "spakenburg": "Netherlands", "urk": "Netherlands", "axel": "Netherlands",
}
EUROPE_WORDS = re.compile(r"europ|netherlands|nederland|holland|france|frankrijk|germany|duitsland|italy|italie|"
                          r"england|engeland|britain|belgium|belgie|spain|spanje|portugal|switzerland|zwitserland|"
                          r"austria|oostenrijk|vlaanderen|bohemen|ierland|scandinav|denemarken|zweden|russia")

TEXTILE_RE = re.compile(r"lace|kant\b|kantwerk|kleding|clothing|costume|kostuum|textile|weefsel|damast|damask|"
                        r"japon|muts|kraag|borduur|embroider|needle|merklap|sampler|servet|tafellaken|sjaal|"
                        r"schort|hemd|kous|tapijt|rug\b|carpet|tapestry|wandtapijt|quilt|deken|streekdracht|"
                        r"klederdracht|streeksieraad|oorijzer|folk|volkskunst|batik|ikat|sarong|kain|pha\b")
RIJKS_DROP_CLASSES = {"prints", "foto's", "Frederik Muller Historieplaten", "fotografisch geïllustreerde boeken",
                      "ex librissen", "Van Gelder", "volksprenten", "ornamentprenten", "boeken", "topografie",
                      "Atlas Ottens", "Oranjeportretten", "Indische albums", "costume and fashion prints",
                      "foto-opdrachten", "affiches", "Document Nederland", "opticaprenten", "documenten en objecten",
                      "documenten", "autografen", "archief Bonger", "Engelse spotprenten",
                      "munten, penningen en draagtekens"}
RIJKS_DROP_TYPES = re.compile(r"photo|foto|stereograph|carte-de-visite|ex libris|album|bladzijde|kaart\b|map\b|"
                              r"medal|penning|jeton|coin|munt|book\b|boek|letter|document|poster|affiche|postzegel|"
                              r"titel|omslag|magazine|negatie|glasdia|reproductie|prentbriefkaart|enquete|"
                              r"nieuwjaarswens|kalenderblad|plattegrond|text sheet")
# prints, drawings and paintings are kept only where the painting / print tradition is native
NATIVE_PICTORIAL = {"China", "Japan", "Korea", "India", "Pakistan", "Iran", "Turkey", "Tibet", "Nepal",
                    "Indonesia", "Thailand", "Burma", "Sri Lanka", "Central Asia", "Afghanistan", "Syria", "Egypt"}
# named makers of pictorial works elsewhere are mostly European visitors (sketchbooks of
# Istanbul, Luxor, Batavia); in East Asia they are the native print and painting masters
NAMED_PICTORIAL_OK = {"China", "Japan", "Korea"}
PICTORIAL_RE = re.compile(r"print|prent|drawing|tekening|painting|schilderij|aquarel|surimono|miniatu|kalligrafie|"
                          r"album|schetsboek")
ANON = re.compile(r"^(anonymous|anoniem|unknown|onbekend)", re.I)

OBJECT_GROUPS = [
    ("textile", r"textile|weefsel|damast|damask|batik|ikat|sarong|kain|tapestry|tapijt|rug\b|carpet|quilt|"
                r"servet|tafellaken|deken|cloth|doek|kleed|lap\b|sjaal|shawl|kant\b|lace|borduur|embroider"),
    ("costume and accessories", r"kleding|clothing|costume|kostuum|japon|muts|kraag|hemd|kous|schort|jas\b|"
                                r"rok\b|hat\b|hoed|headdress|hoofddeksel|sandaal|schoen|shoe|belt|gordel|fan\b|waaier|"
                                r"streekdracht|klederdracht|kimono|obi\b"),
    ("jewellery and ornament", r"jewel|sieraad|ring\b|brooch|broche|necklace|halsketting|armband|bracelet|"
                               r"oorijzer|earring|oorbel|pendant|hanger|kralen|bead"),
    ("arms and armour", r"kris|keris|sword|zwaard|dagger|dolk|klewang|spear|speer|lans|shield|schild|armour|"
                        r"harnas|gun|geweer|pistol|pistool|bow\b|boog|arrow|pijl|helmet|helm|wapen|weapon"),
    ("mask", r"mask|masker"),
    ("musical instrument", r"musical instrument|muziekinstrument|drum|trom|gong|gamelan|fluit|flute|rebab|"
                           r"angklung|wind instrument|string instrument"),
    ("ceramics", r"ceram|keramiek|porcelain|porselein|pot\b|vase|vaas|bowl|kom\b|dish|schotel|plate|bord\b|jar\b|"
                 r"kan\b|cup\b|kop\b|teapot|theepot|tile|tegel|earthenware|aardewerk|stoneware|steengoed|bottle|"
                 r"fles|scherf|sherd|kendi|celadon|kraak|tureen|dekselpot"),
    ("metalwork", r"bronze|brons|brass|messing|silver|zilver|gold\b|goud|copper|koper|iron\b|ijzer|metal|"
                  r"tin\b|candlestick|kandelaar|bell\b|bel\b|lamp"),
    ("lacquer", r"lacquer|lak\b|lakwerk|maki-e|inro|netsuke"),
    ("sculpture and carving", r"sculpt|beeld|figure|figuur|statue|carving|snijwerk|relief|ivory|ivoor|wood|hout|"
                              r"stone|steen|ancestor|voorouder|amulet"),
    ("furniture and woodwork", r"furniture|meubel|chair|stoel|table|tafel|cabinet|kast|chest|kist|box\b|doos|"
                               r"screen|scherm|bed\b"),
    ("basketry", r"basket|mand\b|vlechtwerk|matting|mat\b"),
    ("painting", r"painting|schilderij|thangka|tangka|scroll|rol\b|miniatu|wayang beber"),
    ("print", r"print|prent|surimono|woodcut|houtsnede"),
    ("drawing", r"drawing|tekening|aquarel|sketch|schets"),
    ("puppetry and theatre", r"wayang|puppet|pop\b|marionet|theatre|theater"),
    ("glass", r"glass|glas\b"),
    ("model", r"model\b|miniatuur"),
    ("tool and implement", r"tool|gereedschap|implement|spoon|lepel|knife|mes\b|comb|kam\b|pipe|pijp|"
                           r"container|bag\b|tas\b|paddle|peddel|boat|boot|prauw"),
]
OBJECT_GROUPS = [(g, re.compile(r"(?<![a-z])(?:" + p + ")")) for g, p in OBJECT_GROUPS]


def object_group(*texts):
    t = " ".join(x for x in texts if x).lower()
    for g, rx in OBJECT_GROUPS:
        if rx.search(t):
            return g
    return "other"


def rijks_place_country(place):
    f = fold(place)
    if f in PLACE_COUNTRY:
        return PLACE_COUNTRY[f], f not in COUNTRY_SELF
    return None, False


def rijks_rows(stats):
    path = extract_rijks()
    rows = []
    for line in gzip.open(path, "rt", encoding="utf-8"):
        r = json.loads(line)
        stats["rijks_records"] += 1
        places = r.get("places") or []
        if not places:
            stats["rijks_drop:no production place"] += 1
            continue
        classes = set(r.get("classes") or [])
        types = [t for t in (r.get("types") or []) if t]
        ttxt = " ".join(types).lower()
        country, sub_place = None, None
        for p in places:
            c, is_sub = rijks_place_country(p)
            if c:
                country = country or c
                if is_sub and not GENERIC_SUB.search(fold(p)) and sub_place is None and c == country:
                    sub_place = p
        euro_centre = None
        if not country:
            for p in places:
                if fold(p) in EURO_CENTRES:
                    euro_centre = p
                    break
        pictorial = bool(PICTORIAL_RE.search(ttxt)) or bool(classes & {"prints", "drawings", "paintings"})
        if classes & RIJKS_DROP_CLASSES - {"prints"} or RIJKS_DROP_TYPES.search(ttxt):
            if not (country in NATIVE_PICTORIAL and pictorial and not classes & {"foto's"}
                    and not re.search(r"photo|foto|book|boek|magazine|kaart|album", ttxt)):
                stats["rijks_drop:photo / print / document / coin"] += 1
                continue
        if "prints" in classes and not (country in NATIVE_PICTORIAL):
            stats["rijks_drop:photo / print / document / coin"] += 1
            continue
        makers = [m.split("|") for m in r.get("makers") or []]
        named = [m[0] for m in makers if m and m[0] and not ANON.search(m[0])]
        if country:
            if COUNTRY_REGION.get(country) == "americas_settler":
                stats["rijks_drop:settler country without Indigenous evidence"] += 1
                continue
            if pictorial and named and country not in NAMED_PICTORIAL_OK:
                stats["rijks_drop:pictorial work by named (Western) maker"] += 1
                continue
            sub = PLACE_EN.get(fold(sub_place), sub_place) if sub_place else None
            label_raw = f"{country}, {sub}" if sub else country
            culture_from = "production place"
        elif euro_centre and TEXTILE_RE.search(ttxt + " " + " ".join(classes).lower()):
            country = EURO_CENTRES[fold(euro_centre)]
            label_raw = f"{country}, {euro_centre}"
            culture_from = "production place (European textile / costume centre)"
        else:
            stats["rijks_drop:Europe / unresolved place"] += 1
            continue
        keys = culture_keys(label_raw)
        if not keys:
            stats["rijks_drop:no culture key"] += 1
            continue
        region = COUNTRY_REGION.get(country, "europe")
        rows.append({
            "source": "rijks", "id": r.get("objno") or r.get("rid"), "title": (r.get("title") or "")[:200],
            "culture_keys": "; ".join(k for k, _ in keys), "culture_label": "; ".join(l for _, l in keys),
            "culture_kind": "; ".join(("european_textile_centre" if euro_centre and not sub_place else
                                       "production_centre") if ", " in k else "place" for k, _ in keys),
            "culture_from": culture_from, "place": "; ".join(dict.fromkeys(places)), "country": country,
            "region": region, "object_type": "; ".join(dict.fromkeys(types))[:120],
            "object_group": object_group(ttxt, " ".join(classes), r.get("title") or "", " ".join(r.get("mats") or [])),
            "period": "; ".join(dict.fromkeys(r.get("periods") or [])), "date_begin": _year(r.get("begin")),
            "date_end": _year(r.get("end")), "maker": "; ".join(dict.fromkeys(named))[:200],
            "attributed": int(bool(named)), "materials": "; ".join(r.get("mats") or [])[:150],
            "institution": SOURCE_INST["rijks"],
            "url": (r.get("url") or "").replace("http://hdl.handle.net", "https://hdl.handle.net"),
        })
    stats["rijks_kept"] = len(rows)
    return rows


def _year(s):
    m = re.match(r"\s*(-?\d{1,4})", str(s or ""))
    return int(m.group(1)) if m else ""


# ========================================================================= NMVW

HDL = "<https://hdl.handle.net/20.500.11840/"
CRM = "http://www.cidoc-crm.org/cidoc-crm/"
NMVW_KEEP = ["E22_Human-Made_Object>", "purl.org/dc/terms/title>", "P108i_was_produced_by>",
             "P7_took_place_at>", "P4_has_time-span>", "P82a_begin_of_the_begin>", "P82b_end_of_the_end>",
             "P14_carried_out_by>", "P65_shows_visual_item>", "P138_represents>", "P2_has_type>",
             "P45_consists_of>", "skos/core#prefLabel>", "skos/core#altLabel>", "skos/core#broader>",
             "skos/core#inScheme>", "skos/core#exactMatch>", "20.500.11840/pi", "P1_is_identified_by>",
             "P190_has_symbolic_content>"]
INV = re.compile(r'^"([A-Z]{2,4}-[^"]{1,40})"')
LIT = re.compile(r'"((?:[^"\\]|\\.)*)"(?:@([A-Za-z-]+)|\^\^<[^>]*>)?\s*\.\s*$')
SCHEMES = {"conceptscheme1": "geo", "conceptscheme2": "objtype", "conceptscheme3": "culture",
           "conceptscheme4": "function", "conceptscheme5": "material"}


def _lit(s):
    m = LIT.search(s)
    if not m:
        return None, None
    v = m.group(1)
    if "\\" in v:
        try:
            v = json.loads('"' + v.replace("\\'", "'") + '"')
        except ValueError:
            v = v.replace('\\"', '"').replace("\\n", " ")
    return v, (m.group(2) or "")


def _id(iri):
    """Short id: object digits / termmasterN / piN / genid hex."""
    iri = iri.strip("<>")
    return iri.rsplit("/", 1)[-1]


def _lines(path):
    """zcat | grep -F prefilter (fast); falls back to Python filtering."""
    import shutil
    import subprocess
    if shutil.which("zcat") and shutil.which("grep"):
        args = ["grep", "-F"] + [x for p in NMVW_KEEP for x in ("-e", p)]
        z = subprocess.Popen(["zcat", path], stdout=subprocess.PIPE)
        g = subprocess.Popen(args, stdin=z.stdout, stdout=subprocess.PIPE, env=dict(os.environ, LC_ALL="C"))
        z.stdout.close()
        for b in g.stdout:
            yield b.decode("utf-8", "replace")
        g.wait()
        z.wait()
    else:
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
            for line in f:
                if any(p in line for p in NMVW_KEEP):
                    yield line


def extract_nmvw(limit=None):
    """One pass over the dump: per-object slim records + thesaurus, cached."""
    cache = os.path.join(RAW, "nmvw", "objects.jsonl.gz")
    thes_cache = os.path.join(RAW, "nmvw", "thesaurus.json.gz")
    if os.path.exists(cache) and os.path.exists(thes_cache) and not limit:
        return cache, thes_cache
    dump = download(NMVW_DUMP, os.path.join(RAW, "nmvw", "collection-archives.nt.gz"))
    objs, title, prod, place, tspan, begin, end, maker = set(), {}, {}, {}, {}, {}, {}, {}
    vis, rep, otype, mat = {}, {}, {}, {}
    pref, alt, broader, scheme, aat, pilabel = {}, {}, {}, {}, {}, {}
    ident, inv = {}, {}
    n = 0
    t0 = time.time()
    for line in _lines(dump):
        n += 1
        if n % 5_000_000 == 0:
            log(f"nmvw: {n:,} filtered lines ({time.time() - t0:.0f}s), {len(objs):,} objects")
        if limit and n > limit:
            break
        try:
            s, p, rest = line.split(" ", 2)
        except ValueError:
            continue
        p = p.strip("<>")
        sid = _id(s)
        is_obj = s.startswith(HDL) and sid.isdigit()
        if p.endswith("#type"):
            if is_obj and "E22_Human-Made_Object" in rest:
                objs.add(sid)
            continue
        o = rest.rsplit(" ", 1)[0].strip()
        if p == "http://purl.org/dc/terms/title" and is_obj:
            title[sid] = _lit(rest)[0]
        elif p == CRM + "P108i_was_produced_by" and is_obj:
            prod.setdefault(sid, []).append(_id(o))
        elif p == CRM + "P7_took_place_at":
            place.setdefault(sid, []).append(_id(o))
        elif p == CRM + "P4_has_time-span":
            tspan[sid] = _id(o)
        elif p == CRM + "P82a_begin_of_the_begin":
            begin[sid] = (_lit(rest)[0] or "")[:5]
        elif p == CRM + "P82b_end_of_the_end":
            end[sid] = (_lit(rest)[0] or "")[:5]
        elif p == CRM + "P14_carried_out_by":
            maker.setdefault(sid, []).append(_id(o))
        elif p == CRM + "P65_shows_visual_item" and is_obj:
            vis.setdefault(sid, []).append(_id(o))
        elif p == CRM + "P138_represents":
            rep.setdefault(sid, []).append(_id(o))
        elif p == CRM + "P2_has_type" and is_obj and "termmaster" in o:
            otype.setdefault(sid, []).append(_id(o))
        elif p == CRM + "P45_consists_of" and is_obj:
            mat.setdefault(sid, []).append(_id(o))
        elif p.startswith("http://www.w3.org/2004/02/skos/core#") and "termmaster" in s:
            k = p.rsplit("#", 1)[1]
            if k == "prefLabel":
                v, lang = _lit(rest)
                pref.setdefault(sid, {})[lang] = v
            elif k == "altLabel":
                v, lang = _lit(rest)
                if lang == "en":
                    alt.setdefault(sid, v)
            elif k == "broader":
                broader.setdefault(sid, _id(o))
            elif k == "inScheme":
                scheme[sid] = SCHEMES.get(_id(o), _id(o))
            elif k == "exactMatch" and "aat" in o:
                aat.setdefault(sid, _id(o))
        elif p == CRM + "P1_is_identified_by" and is_obj:
            ident.setdefault(sid, []).append(_id(o))
        elif p == CRM + "P190_has_symbolic_content":
            m = INV.match(rest.strip())
            if m:
                inv[sid] = m.group(1)
        elif p == "http://www.w3.org/2000/01/rdf-schema#label" and sid.startswith("pi"):
            pilabel[sid] = _lit(rest)[0]
    log(f"nmvw: {n:,} lines; {len(objs):,} objects, {len(prod):,} with production, "
        f"{len(vis):,} with visual items, {len(pref):,} thesaurus terms, {len(pilabel):,} makers")
    thes = {t: {"pref": pref.get(t, {}).get("") or next(iter(pref.get(t, {}).values()), ""),
                "en": pref.get(t, {}).get("en") or alt.get(t, ""), "broader": broader.get(t, ""),
                "scheme": scheme.get(t, ""), "aat": aat.get(t, "")}
            for t in set(pref) | set(broader) | set(scheme)}
    sfx = ".sample" if limit else ""
    with gzip.open(thes_cache + sfx + ".part", "wt", encoding="utf-8") as f:
        json.dump(thes, f, ensure_ascii=False)
    os.replace(thes_cache + sfx + ".part", thes_cache + sfx)
    with gzip.open(cache + sfx + ".part", "wt", encoding="utf-8") as f:
        for oid in sorted(objs | set(title) | set(prod), key=lambda x: int(x)):
            places, makers, b, e = [], [], [], []
            for pr in prod.get(oid, []):
                places += place.get(pr, [])
                makers += [pilabel.get(m, m) for m in maker.get(pr, [])]
                ts = tspan.get(pr)
                if ts:
                    b.append(begin.get(ts, ""))
                    e.append(end.get(ts, ""))
            terms = [t for v in vis.get(oid, []) for t in rep.get(v, [])]
            invs = [inv[g] for g in ident.get(oid, []) if g in inv]
            rec = {"id": oid, "inv": invs[0] if invs else "", "title": title.get(oid, ""), "places": places, "terms": terms,
                   "types": otype.get(oid, []), "mats": mat.get(oid, [])[:6], "makers": makers[:5],
                   "begin": min((x for x in b if x), default=""), "end": max((x for x in e if x), default="")}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    os.replace(cache + sfx + ".part", cache + sfx)
    log(f"nmvw: cached {cache + sfx}")
    return cache + sfx, thes_cache + sfx


NMVW_INST = {"TM": "Tropenmuseum", "RV": "Museum Volkenkunde", "WM": "Wereldmuseum Rotterdam",
             "AM": "Afrika Museum"}
NMVW_DROP_TYPES = re.compile(r"photo|slide|negative|lantern|stereo|collodion|albumen|gelatin|film\b|cyanotype|"
                             r"fonds|archiv|document|letter|book|manuscript page|periodical|newspaper|"
                             r"coin|money|banknote|paper money|human specimen|specimen|postcard|"
                             r"street scenes|landscapes \(representations\)|portraits")
NMVW_DROP_CHAINS = re.compile(r"visual works by subject type|information artifacts|document genres|"
                              r"exchange media|money")
PHOTO_TITLE = re.compile(r"portret|foto|lichtbeeld|gezicht op|opname|repr\b|serie\b|\bzicht|groep|"
                         r"landschap|straat|\bvan (de|het|een)\b|\d{4}")
RELIGION = re.compile(r"religon|religion")
PERIOD_STYLE = re.compile(r"\bperiods?\b|\bstyles?\b|periodes")
BROAD = re.compile(r"cultures\b|-culturen|culturen\b|\bregion|regional|peoples\b|speaking|widespread|groups\b|"
                   r"^(african|european|asian|oceanic|melanesian|polynesian|micronesian|american|native american|"
                   r"cultural provenance.*)$")
DIRECTIONAL = re.compile(r"^(north|south|east|west|central|southern|northern|eastern|western|highland|lowland|"
                         r"coastal|insular|mainland|upper|lower|middle)\b|^(indonesian|asian|african|american|"
                         r"oceanic|melanesian|european)$")
PAREN_IGNORE = {"people", "peoples", "culture", "style", "ethnic group", "volk"}
COUNTRY_NAMES = set(fold(x) for x in (
    "Afghanistan Algeria Angola Argentina Armenia Australia Bangladesh Benin Bhutan Bolivia Botswana Brazil "
    "Burkina_Faso Burundi Cambodia Cameroon Canada Chad Chile China Colombia Comoros Congo Cuba Curacao Egypt "
    "Ecuador Eritrea Ethiopia Fiji Gabon Gambia Ghana Greenland Guatemala Guinea Guinea-Bissau Guyana Haiti "
    "Honduras India Indonesia Iran Iraq Israel Ivory_Coast Jamaica Japan Jordan Kenya Kiribati Korea Kuwait Laos "
    "Lebanon Lesotho Liberia Libya Madagascar Malawi Malaysia Mali Mauritania Mexico Mongolia Morocco "
    "Mozambique Myanmar Namibia Nepal New_Zealand Nicaragua Niger Nigeria Oman Pakistan Panama Papua_New_Guinea "
    "Paraguay Peru Philippines Qatar Rwanda Samoa Saudi_Arabia Senegal Sierra_Leone Singapore Solomon_Islands "
    "Somalia South_Africa Sri_Lanka Sudan Suriname Swaziland Syria Taiwan Tanzania Thailand Timor-Leste Togo "
    "Tonga Tunisia Turkey Uganda United_States_of_America Uzbekistan Vanuatu Venezuela Vietnam Yemen Zambia "
    "Zimbabwe Democratic_Republic_of_the_Congo Republic_of_the_Congo Central_African_Republic Côte_d'Ivoire "
    "Equatorial_Guinea Djibouti Turkmenistan Tajikistan Kyrgyzstan Kazakhstan Azerbaijan Georgia Tibet "
    "Netherlands Belgium France Germany Italy Spain Portugal United_Kingdom Greece Russia Poland Austria "
    "Switzerland Sweden Norway Denmark Hungary Romania Bulgaria Albania Serbia Croatia Bosnia_and_Herzegovina "
    "Solomon_Islands_(nation) New_Caledonia French_Polynesia Micronesia Marshall_Islands Palau Aruba Bonaire "
    "Sint_Maarten Trinidad_and_Tobago Dominican_Republic Puerto_Rico El_Salvador Belize Costa_Rica Uruguay "
    "Western_Sahara Cape_Verde Sao_Tome_and_Principe Brunei East_Timor Burma").split())
COUNTRY_NAMES = {fold(x.replace("_", " ")) for x in COUNTRY_NAMES}
COUNTRY_NAMES |= {fold(x.replace("_", " ")) for x in (
    "Burkina_Faso Ivory_Coast New_Zealand Papua_New_Guinea Saudi_Arabia Sierra_Leone Solomon_Islands South_Africa "
    "Sri_Lanka United_States_of_America Democratic_Republic_of_the_Congo Republic_of_the_Congo "
    "Central_African_Republic Côte_d'Ivoire Equatorial_Guinea Bosnia_and_Herzegovina Solomon_Islands_(nation) "
    "New_Caledonia French_Polynesia Marshall_Islands Sint_Maarten Trinidad_and_Tobago Dominican_Republic "
    "Puerto_Rico El_Salvador Costa_Rica Western_Sahara Cape_Verde Sao_Tome_and_Principe East_Timor "
    "United_Kingdom").split()}


def geo_region(chain):
    """chain: labels root-first ('Geographical Provenance', 'Asia', 'East Asia', 'Japan', ...)."""
    t = " > ".join(chain[1:3]).lower()
    if not t:
        return ""
    if t.startswith("asia"):
        t3 = " > ".join(chain[2:4]).lower()
        if "east asia" in t and "southeast" not in t:
            return "east_asia"
        if re.search(r"(?<!east )south asia", t3):
            return "south_asia"
        if "southeast" in t3 or "zuidoost" in t3:
            return "southeast_asia"
        if "southwest asia" in t3:
            return "west_asia_islamic"
        if "central asia" in t3:
            return "himalaya_central_asia"
        return "west_asia_islamic"
    if t.startswith("africa"):
        return "africa_north" if "north africa" in t else "africa"
    if t.startswith("america"):
        return "americas"
    if t.startswith("oceania"):
        return "oceania"
    if t.startswith("eurasia"):
        return "europe" if "europe" in t else "himalaya_central_asia"
    return ""


def nmvw_rows(stats):
    cache, thes_cache = extract_nmvw()
    th = json.load(gzip.open(thes_cache, "rt", encoding="utf-8"))

    def lab(t):
        x = th.get(t) or {}
        return x.get("en") or x.get("pref") or ""

    chains = {}

    def chain(t):
        if t not in chains:
            out, seen = [], set()
            while t in th and t not in seen:
                seen.add(t)
                out.append(t)
                t = th[t]["broader"]
            chains[out[0] if out else t] = out[::-1]   # root first
            return out[::-1]
        return chains[t]

    def kind(t):
        c = chain(t)
        labels = " > ".join(lab(x) for x in c).lower()
        if RELIGION.search(labels):
            return "religion"
        if PERIOD_STYLE.search(" > ".join(lab(x) for x in c[1:]).lower()) and PERIOD_STYLE.search(
                (lab(t) + " " + lab(th.get(t, {}).get("broader", ""))).lower()):
            return "period_style"
        if BROAD.search(fold(lab(t))) or len(c) <= 3:
            return "regional_group"
        return "culture"

    def ckey(t):
        """culture term -> (key, label), with its parent culture as base when the parent is a culture."""
        label = lab(t)
        m = re.match(r"^(.*?)\s*\(([^)]*)\)\s*$", label)
        if m:
            outer, par = tidy(m.group(1)), tidy(m.group(2))
            label_raw = outer if fold(par) in PAREN_IGNORE else f"{par}, {outer}"
        else:
            label_raw = label
        keys = culture_keys(label_raw)
        if not keys:
            return None
        k, l = keys[0]
        if ", " not in k:
            par = th.get(t, {}).get("broader", "")
            pl = fold(re.sub(r"\s*\([^)]*\)", "", lab(par))) if par else ""
            if (par and kind(par) == "culture" and not DIRECTIONAL.search(pl) and " " not in pl
                    and not re.search(r"(an|ese|ish|ic|i)$", pl) and pl not in COUNTRY_NAMES):
                pk = culture_keys(re.sub(r"\s*\([^)]*\)", "", lab(par)))
                if pk and ", " not in pk[0][0] and pk[0][0] != k:
                    return f"{pk[0][0]}, {k}", f"{pk[0][1]}, {l}"
        return k, l

    rows = []
    for line in gzip.open(cache, "rt", encoding="utf-8"):
        r = json.loads(line)
        stats["nmvw_records"] += 1
        tlabels = [lab(t) for t in r.get("types") or []]
        tchains = " | ".join(" > ".join(lab(x) for x in chain(t)) for t in (r.get("types") or [])[:2]).lower()
        ttxt = " ".join(tlabels).lower()
        if (NMVW_DROP_TYPES.search(ttxt) or NMVW_DROP_CHAINS.search(tchains)) and not re.search(
                r"textile|cloth|costume|sculpt|statue|mask|painting|print\b|prints \(visual|drawing|gouache", ttxt):
            stats["nmvw_drop:photograph / archive / coin / specimen"] += 1
            continue
        if not tlabels:
            title = (r.get("title") or "").lower()
            if (PHOTO_TITLE.search(title) or len(title.split()) > 3) and object_group(title) == "other":
                stats["nmvw_drop:untyped record with photograph-like title"] += 1
                continue
        terms = r.get("terms") or []
        cterms = [t for t in dict.fromkeys(terms + (r.get("places") or [])) if th.get(t, {}).get("scheme") == "culture"]
        gterms = [t for t in (r.get("places") or []) + terms if th.get(t, {}).get("scheme") == "geo"]
        gchain = [lab(x) for x in chain(gterms[0])] if gterms else []
        country = next((l for l in gchain if fold(l) in COUNTRY_NAMES), "")
        region = geo_region(gchain)
        keys, labels, kinds, paths, aats = [], [], [], [], []
        for t in cterms:
            kd = kind(t)
            if kd == "religion":
                continue
            kl = ckey(t)
            if not kl:
                continue
            keys.append(kl[0])
            labels.append(kl[1])
            kinds.append(kd)
            paths.append(" > ".join(lab(x) for x in chain(t)[1:]))
            aats.append(th.get(t, {}).get("aat", ""))
            if not region:
                cc = " > ".join(lab(x) for x in chain(t)).lower()
                region = next((rg for w_, rg in (("east asian", "east_asia"), ("insular southeast", "southeast_asia"),
                                                 ("mainland southeast", "southeast_asia"), ("south asian", "south_asia"),
                                                 ("north-african", "africa_north"), ("african", "africa"),
                                                 ("oceanic", "oceania"), ("americas", "americas"),
                                                 ("west asian", "west_asia_islamic"), ("islamic", "west_asia_islamic"),
                                                 ("european", "europe")) if w_ in cc), "")
        culture_from = "recorded culture"
        if not keys:
            if not country:
                stats["nmvw_drop:no culture and no country"] += 1
                continue
            kl = culture_keys(re.sub(r"\s*\([^)]*\)", "", country))
            if not kl:
                stats["nmvw_drop:no culture key"] += 1
                continue
            keys, labels, kinds, paths, aats = [kl[0][0]], [kl[0][1]], ["place"], [" > ".join(gchain[1:])], [""]
            culture_from = "production place (country)"
        inv = r.get("inv") or ""
        inst = NMVW_INST.get(inv.split("-")[0], SOURCE_INST["nmvw"])
        makers = [m for m in r.get("makers") or [] if m and not ANON.search(m) and not m.startswith("pi")]
        rows.append({
            "source": "nmvw", "id": inv or r["id"], "title": (r.get("title") or "")[:200],
            "culture_keys": "; ".join(keys), "culture_label": "; ".join(labels), "culture_kind": "; ".join(kinds),
            "culture_path": " | ".join(paths)[:300], "aat": "; ".join(a for a in aats if a),
            "culture_from": culture_from, "place": "; ".join(dict.fromkeys(lab(t) for t in gterms[:3])),
            "country": country, "region": region, "object_type": "; ".join(tlabels)[:120],
            "object_group": object_group(ttxt, tchains, r.get("title") or ""),
            "period": "", "date_begin": _year(r.get("begin")), "date_end": _year(r.get("end")),
            "maker": "; ".join(dict.fromkeys(makers))[:200], "attributed": int(bool(makers)),
            "materials": "; ".join(lab(m) for m in r.get("mats") or [])[:150], "institution": inst,
            "url": f"https://hdl.handle.net/20.500.11840/{r['id']}",
        })
    stats["nmvw_kept"] = len(rows)
    stats["nmvw_kept_recorded_culture"] = sum(1 for x in rows if x["culture_from"] == "recorded culture")
    return rows


# ============================================================ known culture keys

MET = "Metropolitan Museum of Art"
AIC = "Art Institute of Chicago"
GENERIC_NAMES = {"unspecified", "other", "unknown", "various", "africa", "oceania", "asia", "americas",
                 "europe", "european", "south asia", "southeast asia", "east asia", "west africa"}


def name_variants(raw):
    """Folded names a raw culture string answers to: whole string, each key
    from culture_keys, its base and leaf, and both sides of 'Group: Sub'."""
    out = set()
    s = tidy(raw)
    if not s:
        return out
    pieces = [s] + [tidy(p) for p in re.split(r"\s*[:;/]\s*|\s+-\s+", s) if tidy(p)]
    for p in pieces:
        f = fold(p)
        if f:
            out.add(f)
        for k, _ in culture_keys(p):
            out.add(k)
            for part in k.split(", "):
                out.add(part)
    return {x for x in out if x and len(x) > 2}


def known_index():
    """{folded name: set(institutions)} over everything gathered before this sweep."""
    idx = collections.defaultdict(set)
    files = {}

    def add(raw, inst):
        for n in name_variants(raw):
            idx[n].add(inst)

    p = os.path.join(INTERIM, "unattributed_cultures.csv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p, encoding="utf-8")):
            if r["kind"] != "culture":
                continue
            for n in {r["key"], *r["key"].split(", ")}:
                idx[n].add(MET)
                if (r.get("aic_objects") or "0") not in ("", "0"):
                    idx[n].add(AIC)
            add(r["label"], MET)
        files["unattributed_cultures.csv"] = True
    # regional object tables: (file, culture columns, institution column or constant)
    specs = [
        ("africa_objects.csv", ("culture", "culture_group"), "institution"),
        ("africa_oceania_targeted_objects.csv", ("culture", "culture_group"), "institution"),
        ("americas_oceania_objects.csv", ("culture", "culture_group"), "institution"),
        ("south_southeast_asia_objects.csv", ("culture", "culture_group"), "institution"),
        ("himalaya_central_asia_objects.csv", ("tradition", "traditions_all", "region"), "institution"),
        ("islamic_objects.csv", ("dynasty", "school_workshop", "production_centre"), "institution"),
        ("smithsonian_objects.csv", ("culture", "culture_indexed", "nmai_culture_subarea"), "unit"),
        ("east_asia_objects.csv", ("period_en",), "holder"),
    ]
    unit_names = {"NMAI": "Smithsonian NMAI", "CHNDM": "Cooper Hewitt", "SAAM": "Smithsonian SAAM",
                  "NMAA": "Smithsonian NMAA", "HMSG": "Hirshhorn", "NMAfA": "Smithsonian NMAfA"}
    for fn, cols, icol in specs:
        p = os.path.join(OUT_DIR, fn)
        if not os.path.exists(p):
            log(f"known: {fn} missing, skipped")
            continue
        seen = {}
        for r in csv.DictReader(open(p, encoding="utf-8")):
            inst = r.get(icol, "") or fn
            inst = unit_names.get(inst, inst)
            for c in cols:
                v = r.get(c, "")
                if not v:
                    continue
                for part in v.split(";") if c == "traditions_all" else [v]:
                    k = (part, inst)
                    if k not in seen:
                        seen[k] = True
                        add(part, inst)
        files[fn] = len(seen)
    # tradition tables (kilns, schools, dynasties) add names but no institution
    for fn, cols in (("east_asia_traditions.csv", ("top_kilns_workshops",)),
                     ("islamic_dynasties.csv", ("dynasty",)), ("islamic_schools.csv", ("name",)),
                     ("smithsonian_cultures.csv", ("culture", "period"))):
        p = os.path.join(OUT_DIR, fn)
        if not os.path.exists(p):
            continue
        for r in csv.DictReader(open(p, encoding="utf-8")):
            for c in cols:
                for part in re.split(r";\s*", r.get(c, "") or ""):
                    part = re.sub(r"\s*\(\d+\)$", "", part)
                    for n in name_variants(part):
                        idx.setdefault(n, set())
    for g in GENERIC_NAMES:
        idx.setdefault(g, set())
    log(f"known index: {len(idx)} names from {len(files)} files")
    return idx


# ======================================================================== merge

OBJ_COLS = ["source", "id", "title", "culture_keys", "culture_label", "culture_kind", "culture_from", "culture_path",
            "aat", "place", "country", "region", "object_type", "object_group", "period", "date_begin", "date_end",
            "maker", "attributed", "materials", "institution", "url"]
CULT_COLS = ["key", "label", "level", "parent", "kind", "region", "countries", "object_groups", "date_begin_min",
             "date_end_max", "mid_median", "top_periods", "objects", "objects_rijks", "objects_nmvw", "attributed_share",
             "top_makers", "institutions", "n_institutions", "culture_from", "is_new", "match_basis", "matched_name",
             "known_institutions", "new_institutions", "gained_institution", "culture_path", "aat", "sample_urls"]
INST_PARENT = {"Tropenmuseum": "Wereldmuseum (NMVW)", "Museum Volkenkunde": "Wereldmuseum (NMVW)",
               "Wereldmuseum Rotterdam": "Wereldmuseum (NMVW)", "Afrika Museum": "Wereldmuseum (NMVW)"}
COUNTED_KINDS = ("culture", "period_style", "production_centre", "european_textile_centre")


def match_known(key, label, idx):
    """-> (basis, matched name, institutions) or (None, '', set())."""
    leaf = key.split(", ")[-1]
    lab_leaf = fold(label.split(", ")[-1]) if label else ""
    for basis, name in (("key", key), ("leaf", leaf), ("label", lab_leaf), ("label", fold(label))):
        if name and len(name) > 2 and name in idx:
            return basis, name, idx[name]
    # adjective -> place noun ("central javanese" -> "central java", "sumatran" -> "sumatra")
    for suf, rep in (("nese", ""), ("an", "a"), ("ese", ""), ("ian", "ia"), ("i", "")):
        if len(leaf) > 5 and leaf.endswith(suf):
            name = leaf[: -len(suf)] + rep
            for cand in (name, "indonesian, " + name):
                if cand in idx:
                    return "adjective", cand, idx[cand]
    return None, "", set()


def _top(counter, n=5):
    return "; ".join(f"{k} ({v})" for k, v in counter.most_common(n) if k)


def build_cultures(rows, idx):
    agg = collections.defaultdict(lambda: {"rows": 0, "src": collections.Counter(), "label": collections.Counter(),
                                           "kind": collections.Counter(), "region": collections.Counter(),
                                           "country": collections.Counter(), "group": collections.Counter(),
                                           "period": collections.Counter(), "inst": collections.Counter(),
                                           "from": collections.Counter(), "makers": collections.Counter(),
                                           "attr": 0, "b": [], "e": [], "mid": [], "urls": [], "path": "", "aat": ""})
    for r in rows:
        keys = r["culture_keys"].split("; ")
        labels = r["culture_label"].split("; ")
        kinds = (r.get("culture_kind") or "").split("; ")
        paths = (r.get("culture_path") or "").split(" | ")
        aats = (r.get("aat") or "").split("; ")
        seen = set()
        for i, k in enumerate(keys):
            lab = labels[i] if i < len(labels) else k
            kd = kinds[i] if i < len(kinds) else ""
            targets = [(k, lab, kd)]
            if ", " in k:
                targets.append((k.split(", ")[0], lab.split(", ")[0], kd if kd in ("culture", "period_style")
                                else "place"))
            for kk, ll, dd in targets:
                if kk in seen:
                    continue
                seen.add(kk)
                a = agg[kk]
                a["rows"] += 1
                a["src"][r["source"]] += 1
                a["label"][ll] += 1
                a["kind"][dd] += 1
                a["region"][r["region"]] += 1
                a["country"][r["country"]] += 1
                a["group"][r["object_group"]] += 1
                for p in (r.get("period") or "").split("; "):
                    a["period"][p] += 1
                a["inst"][r["institution"]] += 1
                a["from"][r["culture_from"]] += 1
                a["attr"] += int(r["attributed"] or 0)
                for m in (r.get("maker") or "").split("; "):
                    a["makers"][m] += 1
                b, e = r["date_begin"], r["date_end"]
                if b != "":
                    a["b"].append(b)
                if e != "":
                    a["e"].append(e)
                if b != "" and e != "" and e - b < 1000:
                    a["mid"].append((b + e) / 2)
                if len(a["urls"]) < 3 and r["url"]:
                    a["urls"].append(r["url"])
                if kk == k and i < len(paths) and paths[i] and not a["path"]:
                    a["path"] = paths[i]
                if kk == k and i < len(aats) and aats[i] and not a["aat"]:
                    a["aat"] = aats[i]
    out = []
    for k, a in agg.items():
        label = a["label"].most_common(1)[0][0]
        basis, name, kinst = match_known(k, label, idx)
        new_inst = sorted(set(i for i in a["inst"] if INST_PARENT.get(i, i) not in kinst and i not in kinst))
        mids = sorted(a["mid"])
        out.append({
            "key": k, "label": label, "level": "sub" if ", " in k else "base",
            "parent": k.split(", ")[0] if ", " in k else "",
            "kind": a["kind"].most_common(1)[0][0], "region": a["region"].most_common(1)[0][0],
            "countries": _top(a["country"], 3), "object_groups": _top(a["group"], 6),
            "date_begin_min": min(a["b"], default=""), "date_end_max": max(a["e"], default=""),
            "mid_median": int(mids[len(mids) // 2]) if mids else "", "top_periods": _top(a["period"], 4),
            "objects": a["rows"], "objects_rijks": a["src"]["rijks"], "objects_nmvw": a["src"]["nmvw"],
            "attributed_share": round(a["attr"] / a["rows"], 3), "top_makers": _top(a["makers"], 4),
            "institutions": _top(a["inst"], 6), "n_institutions": len(a["inst"]),
            "culture_from": _top(a["from"], 2), "is_new": int(basis is None), "match_basis": basis or "",
            "matched_name": name, "known_institutions": "; ".join(sorted(kinst))[:300],
            "new_institutions": "; ".join(new_inst) if basis else "",
            "gained_institution": int(bool(basis) and bool(new_inst)),
            "culture_path": a["path"], "aat": a["aat"], "sample_urls": " ".join(a["urls"]),
        })
    out.sort(key=lambda x: (-x["is_new"], -x["objects"]))
    return out


def gain_curve(rows, idx, source, steps=10):
    """Distinct new counted-kind keys after each tenth of the source's rows."""
    sel = [r for r in rows if r["source"] == source]
    if not sel:
        return []
    new, curve = set(), []
    cache = {}
    for n, r in enumerate(sel, 1):
        for k, kd in zip(r["culture_keys"].split("; "), (r.get("culture_kind") or "").split("; ")):
            if kd in COUNTED_KINDS:
                if k not in cache:
                    cache[k] = match_known(k, "", idx)[0] is None
                if cache[k]:
                    new.add(k)
        if n % max(1, len(sel) // steps) == 0 or n == len(sel):
            curve.append((n, len(new)))
    return curve


def bm_check():
    """British Museum: read robots.txt only; never harvest the collection."""
    try:
        req = urllib.request.Request(BM_ROBOTS, headers={"User-Agent": UA})
        txt = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as e:
        return f"robots.txt unreachable ({e}); not harvested"
    blocked = [ua for ua in ("anthropic-ai", "ClaudeBot", "Claude-Web")
               if re.search(r"User-agent:\s*" + re.escape(ua) + r"\s*\n\s*Disallow:\s*/\s*\n", txt, re.I)]
    sig = re.search(r"Content-Signal:\s*([^\n]+)", txt)
    return (f"robots.txt disallows {', '.join(blocked) or 'no Anthropic agent'} site-wide"
            f"{'; Content-Signal ' + sig.group(1).strip() if sig else ''}; /search disallowed for all agents; "
            "collection not harvested (project rule: stop when blocked)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip", default="", help="comma-separated sources to skip: rijks,nmvw,bm")
    ap.add_argument("--only", default="", help="comma-separated sources to run (default: all)")
    ap.add_argument("--fetch-only", action="store_true", help="download / extract caches, build no tables")
    ap.add_argument("--limit", type=int, default=0, help="test: stop each stream after N records")
    args = ap.parse_args()
    run = [s for s in (args.only.split(",") if args.only else SOURCES) if s and s not in args.skip.split(",")]
    if "bm" in run:
        log("bm: " + bm_check())
    if args.fetch_only:
        if "rijks" in run:
            extract_rijks(args.limit or None)
        if "nmvw" in run:
            extract_nmvw(args.limit or None)
        return
    stats = collections.Counter()
    rows = []
    if "rijks" in run:
        rows += rijks_rows(stats)
    if "nmvw" in run:
        rows += nmvw_rows(stats)
    for k, v in sorted(stats.items()):
        log(f"  {k}: {v:,}")
    idx = known_index()
    cultures = build_cultures(rows, idx)
    os.makedirs(OUT_DIR, exist_ok=True)
    write_csv(os.path.join(OUT_DIR, "world_extra_objects.csv"), rows, OBJ_COLS)
    write_csv(os.path.join(OUT_DIR, "world_extra_cultures.csv"), cultures, CULT_COLS)
    # summary: node gain
    for src in ("rijks", "nmvw"):
        curve = gain_curve(rows, idx, src)
        if curve:
            log(f"{src}: new counted keys by rows read: " + ", ".join(f"{n:,}->{k}" for n, k in curve))
    by = collections.Counter()
    for c in cultures:
        for thr in (1, 3, 10, 50):
            if c["objects"] >= thr:
                by[(c["kind"], c["is_new"], thr)] += 1
    for kd in sorted({c["kind"] for c in cultures}):
        log(f"  kind={kd:24s} " + "  ".join(f">={t}: new {by[(kd, 1, t)]} / known {by[(kd, 0, t)]}"
                                          for t in (1, 3, 10, 50)))
    log(f"  known keys that gained a holding institution: {sum(c['gained_institution'] for c in cultures)}")


if __name__ == "__main__":
    main()
