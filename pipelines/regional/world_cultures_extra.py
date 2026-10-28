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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip", default="", help="comma-separated sources to skip: rijks,nmvw,bm")
    ap.add_argument("--only", default="", help="comma-separated sources to run (default: all)")
    ap.add_argument("--fetch-only", action="store_true", help="download / extract caches, build no tables")
    ap.add_argument("--limit", type=int, default=0, help="test: stop each stream after N records")
    args = ap.parse_args()
    run = [s for s in (args.only.split(",") if args.only else SOURCES) if s and s not in args.skip.split(",")]
    if "rijks" in run:
        extract_rijks(args.limit or None)


if __name__ == "__main__":
    main()
