"""Resolve canon-list artists the pool join missed (visual-art-plan.md §3.1b, §3.5).

build_pool.py joins data/interim/contemporary_lists.csv to the candidate pool by
normalised name, so a list artist outside the pool (too few sitelinks, born before
1920, no art occupation on Wikidata, a label spelt differently) gets no QID. The
loss is worst for non-Western biennials and prizes, the very artists the
auto-include rule (§3.5) must keep. This script looks those names up on Wikidata
without the pool filters and keeps every list artist, resolved or not.

Steps
1. Read data/interim/contemporary_lists_matched.csv (artist rows: is_artist != 0) and
   group the entries into distinct artists: by QID where the pool join found one,
   otherwise by token-sorted normalised name. Unmatched entries whose name equals a
   matched entry's name (birth year compatible) take that entry's QID.
2. Name variants per unmatched artist: the name as given; Artprice's "Given SURNAME" /
   "SURNAME Given" style turned into both orders in title case; comma-inverted names;
   diacritics stripped; hyphen variants (Pei-Ming / Pei-ming / Pei Ming / Peiming);
   Arabic article variants (Al X / Al-X / AlX); duos and collectives with & / and /
   et / und, plus each member of a duo as a separate lookup.
3. Lookup stages, each only for artists the previous stages left unresolved:
   A  exact label or alias, in any of LANGS, among humans and groups of humans or
      organisations (VALUES batches of language-tagged literals; labels and aliases
      are separate queries, which keeps the index lookups fast);
   B  label / alias prefix search among humans ("Yan Pei", "Nikau Hi"), matched
      locally on normalised keys: same tokens in any order, spaces and hyphens
      ignored ("Pei-Ming Yan" = "Yan Peiming"); transliteration keys (Al-/El-
      dropped, doubled letters, ou/u, y/i, kh/k, ph/f, q/k, w/v) and one-letter typos
      (names of 10+ letters) count as weak name matches;
   C  the wbsearchentities API (1 request/s; disabled for the run after repeated
      429/503 answers, which shared IPs get often), checked like B.
   Stage B needs QLever's fast prefix filter, so it is skipped with --endpoint wdqs.
4. Disambiguation per candidate (facts fetched for every candidate and cached):
   art      a visual-art occupation (build_pool.art_occupations()), or for a group an
            artist-collective / art-group type or an art field of work (P101);
   creative a film, music, writing, design, architecture or curating occupation;
   birth    birth (or inception) year within 1 year of the list's birth year;
            2-3 years off is neutral, more is a conflict;
   country  a citizenship / birth / residence / group country named in the list's
            country field (country names in six languages, capitals, million cities).
   Strong name matches (exact, normalised) are accepted with art, birth or country,
   or with creative when they are the only candidate; weak ones (transliteration,
   typo) need both art and birth. A birth conflict rejects a candidate unless art
   and country both agree; a near birth year (2-3 off) rejects one without art. The best-scoring candidate wins;
   if more than one was accepted the row is flagged ambiguous with the others listed.
5. Outputs
   data/interim/contemporary_list_artists.csv  one row per distinct list artist:
     name, norm_name, lists, n_lists, editions, n_entries, best_rank, country,
     birth_year, qid, label, status (pool / resolved_not_in_pool / unresolved),
     in_pool, method (pool_join / same_name / exact / prefix / wbsearch / members),
     evidence, ambiguous, alternatives, member_qids, region.
     Duos resolved only through their members keep qid blank and list member_qids;
     status then follows the members. Unresolved artists stay in as list-only
     candidates, carried by the list itself (auto-include rule).
   data/interim/contemporary_pool_additions.csv  resolved QIDs not in the pool (and
     duo members not in it), with the pool's core columns (sitelinks, wikipedias,
     birth / death / living, citizenship -> region via build_pool.region_of, seeded
     from data/raw/wikidata/pool/country_continents.json, media, art_occ_share,
     market / museum IDs, awards) plus occupations and the lists they come from.

Wikidata access: --endpoint qlever (default) sends SPARQL to QLever's Wikidata
mirror (qlever.dev), because WDQS was rate-limiting to 1 request/min during an outage
when this was written; --endpoint wdqs uses query.wikidata.org. Either way at most
--workers (1-2) queries run at once, starts are spaced >= 2 s apart, every result is
cached under data/raw/wikidata/contemporary_resolve/ (re-runs are free and
resumable), and network errors, 429 and 5xx are retried with backoff. A batch that
times out is split in halves and retried; a batch that keeps failing is skipped
(not cached), so a re-run picks it up.

Usage: python3 pipelines/contemporary_art/resolve_list_artists.py [--workers 2]
       [--endpoint qlever|wdqs] [--no-wbsearch]
"""
import argparse
import collections
import csv
from concurrent.futures import ThreadPoolExecutor
import hashlib
import http.client
import itertools
import json
import math
import os
import re
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "visual_art"))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "contemporary_art"))
import build_pool as bp  # noqa: E402
from wikidata import UA, year_of  # noqa: E402

INTERIM = os.path.join(ROOT, "data", "interim")
MATCHED_PATH = os.path.join(INTERIM, "contemporary_lists_matched.csv")
POOL_PATH = os.path.join(INTERIM, "contemporary_pool.csv")
OUT_PATH = os.path.join(INTERIM, "contemporary_list_artists.csv")
ADD_PATH = os.path.join(INTERIM, "contemporary_pool_additions.csv")
RAW = os.path.join(ROOT, "data", "raw", "wikidata", "contemporary_resolve")
POOL_COUNTRIES = os.path.join(bp.RAW, "countries.json")

ENDPOINTS = {"qlever": "https://qlever.dev/api/wikidata", "wdqs": "https://query.wikidata.org/sparql"}
PREFIXES = """PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX schema: <http://schema.org/>
"""
LANGS = ["mul", "en", "fr", "de", "es", "pt", "it", "nl", "tr", "id", "sv", "pl"]
LITERALS_PER_QUERY = 4000
PREFIX_BLOCKS_PER_QUERY = 40
FACTS_CHUNK = 150
MIN_INTERVAL = 2.0

HUMAN = "Q5"
GROUP_ROOTS = ["Q16334295", "Q43229"]          # group of humans, organization
ART_GROUP_ROOTS = ["Q1400264", "Q4502119"]     # artist collective, art group
ART_FIELDS = {"Q735", "Q36649", "Q186030", "Q2018526", "Q11633"}  # art, visual arts, contemporary art, arts, photography
CREATIVE_OCCS = {
    "Q639669", "Q36834", "Q177220", "Q753110", "Q488205",   # musician, composer, singer, songwriter, singer-songwriter
    "Q36180", "Q49757", "Q6625963", "Q482980", "Q11774202",  # writer, poet, novelist, author, essayist
    "Q42973", "Q5322166", "Q3501317", "Q1323191",           # architect, designer, fashion designer, costume designer
    "Q674426", "Q1792450", "Q4164507",                      # curator, art historian, art critic
    "Q3658608", "Q5716684", "Q2259451", "Q28389",           # choreographer, dancer, stage actor, screenwriter
    "Q2526255", "Q1414443", "Q3455803", "Q222344", "Q7042855",  # film director, filmmaker, director, cinematographer, film editor
    "Q183945",                                              # record producer
}
# A handful of country spellings the label lookup does not cover.
COUNTRY_ALIASES = {"swiss": "Q39", "korea": "Q884", "uk": "Q145", "usa": "Q30", "us": "Q30",
                   "uae": "Q878", "drc": "Q974", "england": "Q145", "scotland": "Q145", "wales": "Q145",
                   "holland": "Q55", "palestine": "Q219060", "taiwan": "Q865", "hong kong": "Q8646",
                   "ivory coast": "Q1008", "cote d ivoire": "Q1008", "russia": "Q159", "iran": "Q794",
                   "vietnam": "Q881", "syria": "Q858", "bosnia": "Q225", "macedonia": "Q221"}

_pace_lock = threading.Lock()
_last_start = [0.0]
_cache_lock = threading.Lock()


class QueryTimeout(Exception):
    """The endpoint gave up on the query; a smaller batch may succeed."""


# ---------------------------------------------------------------- SPARQL access

def _post(endpoint, query):
    url = ENDPOINTS[endpoint]
    body = urllib.parse.urlencode({"query": PREFIXES + query}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "User-Agent": UA, "Accept": "application/sparql-results+json",
        "Content-Type": "application/x-www-form-urlencoded"})
    with _pace_lock:
        wait = _last_start[0] + MIN_INTERVAL - time.time()
        if wait > 0:
            time.sleep(wait)
        _last_start[0] = time.time()
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode("utf-8"))


def run_sparql(endpoint, query, attempts=8):
    """SELECT query -> list of {var: value} (entity URIs shortened to QIDs, and
    language-tagged literals as (value, lang) only for ?l). Cached by query hash."""
    key = hashlib.sha1((endpoint + "\n" + query).encode()).hexdigest()
    path = os.path.join(RAW, "sparql", key[:2], key + ".json")
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    for attempt in range(attempts):
        try:
            data = _post(endpoint, query)
            break
        except urllib.error.HTTPError as e:
            text = e.read()[:2000].decode("utf-8", "replace")
            if "timed out" in text or "TimeoutException" in text:
                raise QueryTimeout(text[:200])
            wait = int(e.headers.get("Retry-After") or 0) or min(300, 15 * 2 ** attempt)
            print(f"    SPARQL HTTP {e.code}, retrying in {wait}s")
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException,
                json.JSONDecodeError, OSError) as e:
            wait = min(300, 15 * 2 ** attempt)
            print(f"    SPARQL {type(e).__name__}: {str(e)[:80]}, retrying in {wait}s")
            time.sleep(wait)
    else:
        raise RuntimeError("SPARQL query failed repeatedly")
    out = []
    for b in data["results"]["bindings"]:
        row = {}
        for k, v in b.items():
            val = v["value"]
            if v["type"] == "uri" and val.startswith("http://www.wikidata.org/entity/"):
                val = val.rsplit("/", 1)[1]
            elif v["type"] == "uri" and val.startswith("http://www.wikidata.org/prop/direct/"):
                val = val.rsplit("/", 1)[1]
            row[k] = val
            if v.get("xml:lang"):
                row[k + "_lang"] = v["xml:lang"]
        out.append(row)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".part", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    os.replace(path + ".part", path)
    return out


def run_batches(endpoint, items, make_query, size, workers, label):
    """Run make_query(chunk) over chunks of items (<= workers at once); a chunk that
    times out is split in halves. Returns (rows, n_failed_items)."""
    chunks = [items[i:i + size] for i in range(0, len(items), size)]
    rows, failed = [], [0]
    done = [0]

    def do(chunk):
        try:
            return run_sparql(endpoint, make_query(chunk))
        except QueryTimeout:
            if len(chunk) == 1:
                print(f"    {label}: single item timed out, skipped")
                failed[0] += 1
                return []
            mid = len(chunk) // 2
            return do(chunk[:mid]) + do(chunk[mid:])
        except RuntimeError as e:
            print(f"    {label}: batch of {len(chunk)} skipped ({e}); re-run to retry")
            failed[0] += len(chunk)
            return []

    with ThreadPoolExecutor(workers) as pool:
        for res in pool.map(do, chunks):
            rows.extend(res)
            done[0] += 1
            if done[0] % 10 == 0 or done[0] == len(chunks):
                print(f"  {label}: {done[0]}/{len(chunks)} queries")
    return rows, failed[0]


def lit(s, lang=None):
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"@{lang}' if lang else f'"{s}"'


# ---------------------------------------------------------------- names

def fold(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.replace("ø", "o").replace("Ø", "O").replace("ł", "l").replace("Ł", "L").replace("ß", "ss")


norm = bp.norm


def sort_key(name):
    return " ".join(sorted(norm(name).split()))


def is_caps(tok):
    letters = [c for c in tok if c.isalpha()]
    return len(letters) >= 2 and all(c.isupper() for c in letters)


def title_tok(tok):
    out = re.sub(r"[^\W\d_]+", lambda m: m.group()[:1].upper() + m.group()[1:].lower(), tok)
    return re.sub(r"\bMc([a-z])", lambda m: "Mc" + m.group(1).upper(), out)


def base_forms(name):
    """Orderings / casings of a name, most likely label first: Artprice's
    'Given SURNAME' in title case both ways, 'Surname, Given' inverted, ALL CAPS in
    title case, then the name as given."""
    s = " ".join(re.sub(r"\(.*?\)", " ", name).split()).strip(" ,;")
    starts = [s]
    if s.count(",") == 1 and not re.search(r"&| and | und | et ", s):
        a, b = [x.strip() for x in s.split(",")]
        if a and b:
            starts.insert(0, f"{b} {a}")
    forms = []
    for x in starts:
        toks = x.replace(",", " ").split()
        caps = [is_caps(t) for t in toks]
        if toks and any(caps) and not all(caps):
            sur = [title_tok(t) for t, c in zip(toks, caps) if c]
            given = [t for t, c in zip(toks, caps) if not c]
            forms += [" ".join(given + sur), " ".join(sur + given)]
        elif toks and all(caps):
            forms.append(" ".join(title_tok(t) for t in toks))
        elif x and x == x.lower():
            forms.append(" ".join(title_tok(t) for t in toks))
        forms.append(x)
    return list(dict.fromkeys(f for f in forms if f))


def spelling_variants(form):
    out = {form, fold(form)}
    for f in list(out):
        if "-" in f:
            out.add(f.replace("-", " "))
            out.add(f.replace("-", ""))
            out.add(re.sub(r"-(\w)", lambda m: "-" + m.group(1).lower(), f))
            out.add(re.sub(r"-(\w)", lambda m: m.group(1).lower(), f))
        m = re.search(r"\b([AaEe]l)[ -](\w)", f)
        if m:
            for sep in (" ", "-", ""):
                out.add(re.sub(r"\b([AaEe]l)[ -](\w)", lambda mm: mm.group(1) + sep + mm.group(2), f))
        if "&" in f:
            for w in ("and", "et", "und", "e", "y"):
                out.add(f.replace("&", w))
        if re.search(r"\band\b", f):
            out.add(re.sub(r"\band\b", "&", f))
    return [v for v in out if v.strip()]


def name_variants(name, limit=24):
    out = []
    for f in base_forms(name):
        mixed_caps = any(is_caps(t) for t in f.split()) and not all(is_caps(t) for t in f.split())
        for v in [f] if mixed_caps else sorted(spelling_variants(f), key=lambda x: (x != f, x)):
            if v not in out:
                out.append(v)
    return out[:limit]


DUO_SPLIT = re.compile(r"\s*(?:&|\+|/|,|\band\b|\bund\b|\bet\b)\s*")


def members(name):
    """Members of a duo / trio named 'A & B' (each with >= 2 tokens), else []."""
    if not DUO_SPLIT.search(name):
        return []
    parts = [p.strip() for p in DUO_SPLIT.split(name) if p.strip()]
    if len(parts) < 2 or any(len(p.split()) < 2 for p in parts):
        return []
    return parts


def compact_perms(name):
    toks = norm(name).split()
    if not toks:
        return set()
    if len(toks) > 4:
        return {"".join(toks), "".join(sorted(toks))}
    return {"".join(p) for p in itertools.permutations(toks)}


def translit(s):
    s = re.sub(r"^(al|el|ul|ad|ar|as|at|az)(?=[a-z]{3})", "", s)
    for a, b in (("kh", "k"), ("ph", "f"), ("q", "k"), ("w", "v"), ("ou", "u"), ("oo", "u"),
                 ("y", "i"), ("ee", "i"), ("dh", "d"), ("th", "t"), ("j", "dj")):
        s = s.replace(a, b)
    return re.sub(r"(.)\1+", r"\1", s)


def translit_keys(name):
    toks = [re.sub(r"^(al|el)$", "", t) for t in norm(name).split()]
    toks = [translit(t) for t in toks if t]
    if not toks or len(toks) > 4:
        return set()
    return {"".join(p) for p in itertools.permutations(toks)}


def lev1(a, b):
    """True if a and b differ by at most one edit."""
    if a == b:
        return True
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) > len(b):
        a, b = b, a
    i = 0
    while i < len(a) and a[i] == b[i]:
        i += 1
    return a[i + (len(a) == len(b)):] == b[i + 1:]


def name_match(query_name, label):
    """'exact-norm' / 'normalised' / 'translit' / 'typo' / None for a found label."""
    if norm(query_name) == norm(label):
        return "exact-norm"
    qa, la = set(), compact_perms(label)
    for f in base_forms(query_name):
        qa |= compact_perms(f)
    if qa & la:
        return "normalised"
    qt, lt = set(), translit_keys(label)
    for f in base_forms(query_name):
        qt |= translit_keys(f)
    if qt & lt:
        return "translit"
    nq, nl = norm(query_name).replace(" ", ""), norm(label).replace(" ", "")
    if len(nq) >= 10 and any(lev1(x, y) for x in qa for y in la):
        return "typo"
    return None


# ---------------------------------------------------------------- list artists

def birth_of(s):
    m = re.search(r"\b(1[89]\d\d|20[0-2]\d)\b", s or "")
    return int(m.group()) if m else None


def load_list_artists():
    """Distinct list artists: {key: record}; matched ones keyed 'Q...'."""
    rows = [r for r in csv.DictReader(open(MATCHED_PATH, encoding="utf-8")) if r.get("is_artist") != "0"]
    artists = {}
    name_qid = {}
    for r in rows:
        if r["qid"]:
            name_qid.setdefault(sort_key(r["name"]), {}).setdefault(r["qid"], set()).add(birth_of(r["birth_year"]))
    for r in rows:
        qid, method = r["qid"], "pool_join" if r["qid"] else ""
        if not qid:
            cands = name_qid.get(sort_key(r["name"]), {})
            by = birth_of(r["birth_year"])
            ok = [q for q, bs in cands.items()
                  if by is None or all(b is None or abs(b - by) <= 1 for b in bs)]
            if len(ok) == 1:
                qid, method = ok[0], "same_name"
        key = qid or "N:" + sort_key(r["name"])
        if key == "N:":
            continue
        a = artists.setdefault(key, {"entries": [], "qid": qid, "method": method})
        if method == "pool_join":
            a["method"] = "pool_join"
        a["entries"].append(r)
    for a in artists.values():
        es = a["entries"]
        names = collections.Counter(e["name"] for e in es)
        # Prefer a form that is not Artprice's SURNAME style.
        a["name"] = max(names, key=lambda n: (not any(is_caps(t) for t in n.split()), names[n]))
        a["names"] = list(names)
        births = collections.Counter(b for b in (birth_of(e["birth_year"]) for e in es) if b)
        a["birth"] = births.most_common(1)[0][0] if births else None
        a["country"] = "; ".join(dict.fromkeys(e["country"].strip() for e in es if e["country"].strip()))
    return artists


# ---------------------------------------------------------------- countries

def country_lookup(endpoint):
    """{normalised name: {country QIDs}} from country labels and aliases (six
    languages), capitals and million cities; plus {country QID: ISO code}."""
    langs = '"en", "de", "fr", "es", "pt", "it"'
    rows = []
    for pred in ("rdfs:label", "skos:altLabel"):
        rows += run_sparql(endpoint, f"""SELECT ?c ?n WHERE {{
          ?c wdt:P297 [] ; {pred} ?n . FILTER(LANG(?n) IN ({langs})) }}""")
    out = collections.defaultdict(set)
    for r in rows:
        k = norm(r["n"])
        if len(k) >= 4 or r["n"].isupper():
            out[k].add(r["c"])
    for qs in (run_sparql(endpoint, f"""SELECT ?c ?n WHERE {{
          ?c wdt:P297 [] ; wdt:P36 ?city . ?city rdfs:label ?n . FILTER(LANG(?n) IN ({langs})) }}"""),
               run_sparql(endpoint, f"""SELECT ?c ?n WHERE {{
          ?city wdt:P31 wd:Q1637706 ; wdt:P17 ?c . ?c wdt:P297 [] .
          ?city rdfs:label ?n . FILTER(LANG(?n) IN ({langs})) }}""")):
        for r in qs:
            k = norm(r["n"])
            if len(k) >= 4 and k not in out:
                out[k].add(r["c"])
    for k, q in COUNTRY_ALIASES.items():
        out[k].add(q)
    return out


def parse_countries(text, lookup):
    """Country QIDs named in a list's free-text country field."""
    toks = norm(text.replace("/", " ; ")).split()
    found, i = set(), 0
    while i < len(toks):
        for n in range(min(5, len(toks) - i), 0, -1):
            k = " ".join(toks[i:i + n])
            if k in lookup:
                found |= lookup[k]
                i += n
                break
        else:
            i += 1
    return found


# ---------------------------------------------------------------- Wikidata facts

FACT_PROPS = sorted(set(bp.FACT_PROPS) | {"P31", "P106", "P569", "P570", "P571", "P576", "P27", "P17",
                                          "P495", "P101", "P551"})


def fetch_facts(endpoint, qids, workers):
    """{qid: {"claims": {prop: [values]}, "label", "sitelinks", "titles": {wiki: title}}}, cached."""
    path = os.path.join(RAW, "facts.json")
    facts = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    todo = sorted(q for q in qids if q not in facts)
    if not todo:
        return facts
    props = " ".join("wdt:" + p for p in FACT_PROPS)

    def chunk_facts(chunk):
        values = " ".join("wd:" + q for q in chunk)
        rec = {q: {"claims": {}, "label": "", "label_lang": "", "sitelinks": 0, "titles": {}} for q in chunk}
        for r in run_sparql(endpoint, f"""SELECT ?p ?prop ?v WHERE {{
              VALUES ?p {{ {values} }} VALUES ?prop {{ {props} }} ?p ?prop ?v . }}"""):
            v = r["v"]
            if r["prop"] in ("P569", "P570", "P571", "P576"):
                v = year_of(v)
            rec[r["p"]]["claims"].setdefault(r["prop"], []).append(v)
        for prop, path_ in (("birth_country", "wdt:P19/wdt:P17"), ("residence_country", "wdt:P551/wdt:P17"),
                            ("hq_country", "wdt:P159/wdt:P17"), ("formation_country", "wdt:P740/wdt:P17")):
            for r in run_sparql(endpoint, f"SELECT ?p ?v WHERE {{ VALUES ?p {{ {values} }} ?p {path_} ?v . }}"):
                rec[r["p"]]["claims"].setdefault(prop, []).append(r["v"])
        for r in run_sparql(endpoint, f"SELECT ?p ?s WHERE {{ VALUES ?p {{ {values} }} ?p wikibase:sitelinks ?s . }}"):
            rec[r["p"]]["sitelinks"] = int(r["s"])
        for r in run_sparql(endpoint, f"""SELECT ?p ?l WHERE {{ VALUES ?p {{ {values} }}
              ?p rdfs:label ?l . FILTER(LANG(?l) IN ("en", "mul")) }}"""):
            if not rec[r["p"]]["label"] or r.get("l_lang") == "en":
                rec[r["p"]]["label"] = r["l"]
        for r in run_sparql(endpoint, f"""SELECT ?p ?site ?t WHERE {{ VALUES ?p {{ {values} }}
              ?a schema:about ?p ; schema:isPartOf ?site ; schema:name ?t . }}"""):
            if r["site"].endswith(".wikipedia.org/"):
                rec[r["p"]]["titles"][r["site"].split("//", 1)[1].split(".wikipedia.org", 1)[0]] = r["t"]
        return rec

    chunks = [todo[i:i + FACTS_CHUNK] for i in range(0, len(todo), FACTS_CHUNK)]
    with ThreadPoolExecutor(workers) as pool:
        futures = [pool.submit(chunk_facts, c) for c in chunks]
        for i, fut in enumerate(futures, 1):
            try:
                rec = fut.result()
            except (RuntimeError, QueryTimeout) as e:
                print(f"    facts chunk skipped ({str(e)[:80]}); re-run to retry")
                continue
            with _cache_lock:
                facts.update(rec)
                if i % 5 == 0 or i == len(chunks):
                    with open(path + ".part", "w", encoding="utf-8") as f:
                        json.dump(facts, f, ensure_ascii=False)
                    os.replace(path + ".part", path)
            if i % 5 == 0 or i == len(chunks):
                print(f"  facts: {min(i * FACTS_CHUNK, len(todo))}/{len(todo)}")
    return facts


def type_roots(endpoint, types):
    """{type QID: set of roots among GROUP_ROOTS + ART_GROUP_ROOTS it is a subclass of}."""
    path = os.path.join(RAW, "type_roots.json")
    known = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    todo = sorted(t for t in types if t not in known and re.fullmatch(r"Q\d+", t))
    roots = " ".join("wd:" + q for q in GROUP_ROOTS + ART_GROUP_ROOTS)
    for i in range(0, len(todo), 200):
        chunk = todo[i:i + 200]
        values = " ".join("wd:" + q for q in chunk)
        try:
            rows = run_sparql(endpoint, f"""SELECT ?t ?root WHERE {{ VALUES ?t {{ {values} }}
                  VALUES ?root {{ {roots} }} ?t wdt:P279* ?root . }}""")
        except (RuntimeError, QueryTimeout) as e:
            print(f"    type roots chunk skipped ({str(e)[:60]})")
            continue
        for t in chunk:
            known[t] = []
        for r in rows:
            known[r["t"]].append(r["root"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(known, f)
    return {t: set(v) for t, v in known.items()}


# ---------------------------------------------------------------- evidence

class Judge:
    def __init__(self, facts, troots, art_occs, country_lookup_):
        self.facts, self.troots, self.art, self.clook = facts, troots, art_occs, country_lookup_

    def kind(self, q):
        f = self.facts.get(q)
        if not f:
            return None
        types = set(f["claims"].get("P31", []))
        if HUMAN in types:
            return "human"
        roots = set().union(*(self.troots.get(t, set()) for t in types)) if types else set()
        if roots & set(ART_GROUP_ROOTS):
            return "art_group"
        if roots & set(GROUP_ROOTS):
            return "group"
        return None

    def evaluate(self, artist, q, match):
        """(accepted?, score, evidence list) for candidate q of artist."""
        f = self.facts[q]
        cl = f["claims"]
        kind = self.kind(q)
        ev = []
        occs = set(cl.get("P106", []))
        art = bool(occs & self.art) or kind == "art_group" or bool(set(cl.get("P101", [])) & ART_FIELDS)
        creative = not art and bool(occs & CREATIVE_OCCS)
        if art:
            ev.append("art")
        if creative:
            ev.append("creative")
        wb = [y for y in cl.get("P569", []) + (cl.get("P571", []) if kind != "human" else []) if y is not None]
        birth = near = conflict = False
        if artist["birth"] and wb:
            d = min(abs(y - artist["birth"]) for y in wb)
            if d <= 1:
                birth = True
                ev.append(f"birth {min(wb)}")
            elif d <= 3:
                near = True
                ev.append(f"birth near ({min(wb)} vs {artist['birth']})")
            else:
                conflict = True
                ev.append(f"birth conflict ({min(wb)} vs {artist['birth']})")
        cands = set()
        for k in ("P27", "birth_country", "residence_country", "P551", "P17", "P495", "hq_country", "formation_country"):
            cands |= set(cl.get(k, []))
        country = bool(artist["countries"] & cands)
        if country:
            ev.append("country " + "|".join(sorted(artist["countries"] & cands)))
        strong = match in ("exact", "exact-norm", "normalised")
        ev.insert(0, f"name {match}")
        if conflict and not (art and country):
            return False, 0, ev, False
        if near and not art:
            # A birth year 2-3 years off is only tolerated for a visual artist.
            return False, 0, ev, False
        ok = (art or birth or country or creative) if strong else (birth and art)
        only_creative = creative and not (birth or country)
        score = 3 * art + 3 * birth + 2 * country + creative + 0.5 * near + (1 if match == "exact" else 0.5 if strong else 0)
        return ok, score, ev, only_creative

    def choose(self, artist, cand_matches):
        """cand_matches: {qid: match type}. Returns (qid, evidence, alternatives, tie) or None.
        A candidate backed only by a creative (non-visual-art) occupation is accepted
        only when it is the sole candidate left."""
        accepted = []
        for q, m in cand_matches.items():
            if q not in self.facts or self.kind(q) is None:
                continue
            ok, score, ev, only_creative = self.evaluate(artist, q, m)
            if ok:
                accepted.append((score, math.log1p(self.facts[q].get("sitelinks", 0)), q, ev, only_creative))
        if len(accepted) > 1:
            accepted = [a for a in accepted if not a[4]]
        if not accepted:
            return None
        accepted.sort(key=lambda a: (a[0], a[1]), reverse=True)
        best = accepted[0]
        tie = len(accepted) > 1 and accepted[1][0] >= best[0]
        return best[2], best[3], [a[2] for a in accepted[1:]], tie


# ---------------------------------------------------------------- stages

def stage_exact(endpoint, targets, workers):
    """{target key: {qid: 'exact'}} from exact label / alias matches."""
    lit_to_keys = collections.defaultdict(set)
    for key, t in targets.items():
        for v in t["variants"]:
            lit_to_keys[v].add(key)
    names = sorted(lit_to_keys)
    per = max(1, LITERALS_PER_QUERY // len(LANGS))
    out = collections.defaultdict(dict)
    for pred in ("rdfs:label", "skos:altLabel"):
        def make(chunk, pred=pred):
            values = " ".join(lit(n, lang) for n in chunk for lang in LANGS)
            return f"SELECT DISTINCT ?l ?p WHERE {{ VALUES ?l {{ {values} }} ?p {pred} ?l . }}"
        rows, failed = run_batches(endpoint, names, make, per, workers, f"exact {pred}")
        for r in rows:
            if re.fullmatch(r"Q\d+", r["p"]):
                for key in lit_to_keys.get(r["l"], ()):
                    out[key][r["p"]] = "exact"
    return out


def prefixes_for(name):
    out = set()
    for f in base_forms(name):
        for g in {f, fold(f)}:
            toks = g.split()
            if len(toks) >= 2:
                n = 3 if len(re.sub(r"\W", "", toks[1][:3])) >= 3 else 4
                out.add(toks[0] + " " + toks[1][:n])
            elif len(toks) == 1 and len(toks[0]) >= 5:
                out.add(title_tok(toks[0]))
    return out


def stage_prefix(endpoint, targets, workers):
    """{target key: {qid: match type}} from label / alias prefix search among humans."""
    pre_to_keys = collections.defaultdict(set)
    for key, t in targets.items():
        for p in prefixes_for(t["name"]):
            pre_to_keys[p].add(key)
    pres = sorted(pre_to_keys)
    found = []
    for pred in ("rdfs:label", "skos:altLabel"):
        def make(chunk, pred=pred):
            blocks = " UNION ".join(f"{{ ?p {pred} ?l . FILTER(STRSTARTS(?l, {lit(x)})) }}" for x in chunk)
            return f"SELECT DISTINCT ?p ?l WHERE {{ {blocks} ?p wdt:P31 wd:Q5 . }}"
        rows, failed = run_batches(endpoint, pres, make, PREFIX_BLOCKS_PER_QUERY, workers, f"prefix {pred}")
        found.extend(rows)
    # Bucket the found labels under the searched prefixes they start with.
    by_pre = collections.defaultdict(set)
    for r in found:
        if re.fullmatch(r"Q\d+", r["p"]):
            for n in range(3, len(r["l"]) + 1):
                if r["l"][:n] in pre_to_keys:
                    by_pre[r["l"][:n]].add((r["p"], r["l"]))
    out = collections.defaultdict(dict)
    rank = {"exact-norm": 0, "normalised": 1, "translit": 2, "typo": 3}
    for p, keys in pre_to_keys.items():
        for q, l in by_pre.get(p, ()):
            for key in keys:
                m = name_match(targets[key]["name"], l)
                if not m:
                    for alt in targets[key]["names"][1:]:
                        m = name_match(alt, l)
                        if m:
                            break
                if m and (q not in out[key] or rank[m] < rank[out[key][q]]):
                    out[key][q] = m
    return out


class WbSearch:
    API = "https://www.wikidata.org/w/api.php"

    def __init__(self):
        self.path = os.path.join(RAW, "wbsearch.json")
        self.cache = json.load(open(self.path, encoding="utf-8")) if os.path.exists(self.path) else {}
        self.disabled = False
        self.fails = 0
        self.last = 0.0
        self.n_new = 0

    def save(self):
        with open(self.path + ".part", "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False)
        os.replace(self.path + ".part", self.path)

    def search(self, text):
        if text in self.cache:
            return self.cache[text]
        if self.disabled:
            return None
        params = urllib.parse.urlencode({"action": "wbsearchentities", "search": text, "language": "en",
                                         "type": "item", "limit": 10, "format": "json", "maxlag": 5})
        for attempt in range(3):
            wait = self.last + 1.0 - time.time()
            if wait > 0:
                time.sleep(wait)
            self.last = time.time()
            try:
                req = urllib.request.Request(f"{self.API}?{params}", headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = json.loads(r.read().decode("utf-8"))
                if "error" in data:
                    time.sleep(10)
                    continue
                res = [{"id": x["id"], "text": x.get("match", {}).get("text", x.get("label", ""))}
                       for x in data.get("search", [])]
                self.cache[text] = res
                self.fails = 0
                self.n_new += 1
                if self.n_new % 25 == 0:
                    self.save()
                return res
            except urllib.error.HTTPError as e:
                if e.code in (429, 503):
                    self.fails += 1
                    if self.fails >= 4:
                        print("    wbsearchentities keeps answering 429/503: stage C disabled for this run")
                        self.disabled = True
                        return None
                    time.sleep(int(e.headers.get("Retry-After") or 0) or 30 * (attempt + 1))
                else:
                    time.sleep(10)
            except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException,
                    json.JSONDecodeError, OSError):
                time.sleep(10 * (attempt + 1))
        return None


def stage_wbsearch(targets, ws):
    out = collections.defaultdict(dict)
    rank = {"exact-norm": 0, "normalised": 1, "translit": 2, "typo": 3}
    for i, (key, t) in enumerate(sorted(targets.items()), 1):
        for text in base_forms(t["name"])[:2]:
            res = ws.search(text)
            if res is None:
                continue
            for x in res:
                m = name_match(t["name"], x["text"])
                if m and (x["id"] not in out[key] or rank[m] < rank[out[key][x["id"]]]):
                    out[key][x["id"]] = m
        if ws.disabled:
            break
        if i % 100 == 0:
            print(f"  wbsearch: {i}/{len(targets)}")
    ws.save()
    return out


# ---------------------------------------------------------------- main

def pool_index():
    rows = {}
    with open(POOL_PATH, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[r["qid"]] = r
    return rows


def country_info(endpoint, countries):
    """build_pool.fetch_countries' format, seeded from the pool's and visual_art's caches."""
    path = os.path.join(RAW, "countries.json")
    known = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    pool_known = json.load(open(POOL_COUNTRIES, encoding="utf-8")) if os.path.exists(POOL_COUNTRIES) else {}
    shared = json.load(open(bp.SHARED_CONTINENTS, encoding="utf-8")) if os.path.exists(bp.SHARED_CONTINENTS) else {}
    for c in countries:
        if c not in known and c in pool_known:
            known[c] = dict(pool_known[c])
        rec = known.setdefault(c, {"continents": [], "iso": None})
        if not rec["continents"] and shared.get(c):
            rec["continents"] = list(shared[c])
    for prop_path in bp.CONTINENT_PATHS:
        todo = [c for c in countries if not known[c]["continents"] and not known[c].get(f"tried {prop_path}")]
        for i in range(0, len(todo), 100):
            values = " ".join("wd:" + q for q in todo[i:i + 100])
            for r in run_sparql(endpoint, f"SELECT ?c ?cont WHERE {{ VALUES ?c {{ {values} }} ?c {prop_path} ?cont . }}"):
                if r["cont"] not in known[r["c"]]["continents"]:
                    known[r["c"]]["continents"].append(r["cont"])
        for c in todo:
            known[c][f"tried {prop_path}"] = True
    todo = [c for c in countries if "iso_tried" not in known[c]]
    for i in range(0, len(todo), 200):
        values = " ".join("wd:" + q for q in todo[i:i + 200])
        for r in run_sparql(endpoint, f"SELECT ?c ?iso WHERE {{ VALUES ?c {{ {values} }} ?c wdt:P297 ?iso . }}"):
            known[r["c"]]["iso"] = r["iso"]
    for c in todo:
        known[c]["iso_tried"] = True
    with open(path, "w", encoding="utf-8") as f:
        json.dump(known, f)
    return known


def addition_row(q, f, cinfo, art, judge, list_names):
    cl = f["claims"]
    is_coll = judge.kind(q) in ("art_group", "group")
    births = [y for y in cl.get("P569" if not is_coll else "P571", []) if y is not None]
    deaths = [y for y in cl.get("P570" if not is_coll else "P576", []) if y is not None]
    birth, death = (min(births) if births else None), (min(deaths) if deaths else None)
    occs = set(cl.get("P106", []))
    media = [m for m, qs in bp.GROUPS.items() if occs & set(qs)]
    cits = [c for c in dict.fromkeys(cl.get("P27", []) or ([] if not is_coll else
            cl.get("P17", []) + cl.get("P495", []) + cl.get("hq_country", []) + cl.get("formation_country", [])))
            if re.fullmatch(r"Q\d+", c)]
    bcs = [c for c in dict.fromkeys(cl.get("birth_country", [])) if re.fullmatch(r"Q\d+", c)]
    countries_ = cits or bcs
    regions = list(dict.fromkeys(r for r in (bp.region_of(c, cinfo) for c in countries_) if r))
    primary = next((r for r in (bp.region_of(c, cinfo) for c in bcs) if r in regions), regions[0] if regions else "")
    conts = sorted({c for x in countries_ for c in bp.continent_of(x, cinfo)})
    primary_cont = next((c for x in countries_ if bp.region_of(x, cinfo) == primary
                         for c in bp.continent_of(x, cinfo)), "")
    row = {
        "qid": q, "label": f.get("label", ""), "birth": birth if birth is not None else "",
        "death": death if death is not None else "",
        "living": int(death is None and not is_coll and (birth is None or birth >= 1926)),
        "is_collective": int(is_coll), "pool_rules": "list_resolved",
        "countries": "|".join(countries_),
        "country_codes": "|".join(filter(None, ((cinfo.get(c) or {}).get("iso") or "" for c in countries_))),
        "region": primary, "regions": "|".join(regions), "continent": primary_cont, "continents": "|".join(conts),
        "medium": media[0] if media else bp.UNSPECIFIED, "media": "|".join(media),
        "art_occ_share": round(len(occs & art) / len(occs), 2) if occs else "",
        "sitelinks": f.get("sitelinks", 0), "wikipedias": len(f.get("titles", {})),
    }
    for pid, name in bp.ID_COLUMNS.items():
        row[f"{name}_id"] = (cl.get(pid) or [""])[0]
    row["n_museum_ids"] = sum(1 for pid in bp.MUSEUM_IDS if cl.get(pid))
    row["museum_ids"] = "|".join(bp.MUSEUM_IDS[pid] for pid in bp.MUSEUM_IDS if cl.get(pid))
    row["n_galleries"] = len(set(cl.get("P1875", [])))
    row["galleries"] = "|".join(sorted(set(cl.get("P1875", []))))
    row["n_awards"] = len(set(cl.get("P166", [])))
    row["awards"] = "|".join(sorted(set(cl.get("P166", []))))
    row["n_exhibitions"] = len(set(cl.get("P608", [])))
    row["instagram"] = int(bool(cl.get("P2003")))
    row["n_lists"] = len(list_names)
    row["lists"] = "|".join(sorted(list_names))
    row["occupations"] = "|".join(sorted(occs))
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    # Wikidata allows 5 concurrent queries per IP and another job uses 2.
    ap.add_argument("--workers", type=int, default=2, choices=range(1, 3))
    ap.add_argument("--endpoint", choices=sorted(ENDPOINTS), default="qlever")
    ap.add_argument("--no-wbsearch", action="store_true", help="skip stage C (wbsearchentities API)")
    args = ap.parse_args()
    os.makedirs(RAW, exist_ok=True)
    ep = args.endpoint

    artists = load_list_artists()
    pool = pool_index()
    print(f"{len(artists)} distinct list artists, {sum(1 for a in artists.values() if a['qid'])} with a QID")

    print("country names")
    clook = country_lookup(ep)
    for a in artists.values():
        a["countries"] = parse_countries(a["country"], clook)

    # Lookup targets: unresolved artists, plus duo members.
    targets = {}
    for key, a in artists.items():
        if a["qid"]:
            continue
        targets[key] = {"name": a["name"], "names": a["names"], "birth": a["birth"], "countries": a["countries"],
                        "variants": list(dict.fromkeys(v for n in a["names"] for v in name_variants(n)))}
        a["member_keys"] = []
        for m in members(a["name"]):
            mk = "M:" + sort_key(m)
            a["member_keys"].append(mk)
            targets.setdefault(mk, {"name": m, "names": [m], "birth": None, "countries": a["countries"],
                                    "variants": name_variants(m)})
    print(f"{len(targets)} lookup targets ({sum(1 for k in targets if k.startswith('M:'))} duo members)")

    art = bp.art_occupations()
    facts, troots = {}, {}
    results, methods = {}, {}

    def judge_stage(cands, method):
        nonlocal facts, troots
        qids = {q for c in cands.values() for q in c}
        facts = fetch_facts(ep, qids, args.workers)
        types = {t for q in qids if q in facts for t in facts[q]["claims"].get("P31", [])} - {HUMAN}
        troots = type_roots(ep, types)
        judge = Judge(facts, troots, art, clook)
        n = 0
        for key, c in cands.items():
            if key in results or not c:
                continue
            res = judge.choose(targets[key], c)
            if res:
                results[key], methods[key] = res, method
                n += 1
        print(f"  {method}: {n} resolved ({sum(1 for c in cands.values() if c)} targets had name hits)")
        return judge

    print("stage A: exact labels and aliases")
    judge = judge_stage(stage_exact(ep, targets, args.workers), "exact")
    left = {k: t for k, t in targets.items() if k not in results}
    if ep == "qlever":
        print(f"stage B: prefix search for {len(left)} targets")
        judge = judge_stage(stage_prefix(ep, left, args.workers), "prefix")
    else:
        print("stage B skipped (needs QLever's prefix filter)")
    left = {k: t for k, t in targets.items() if k not in results}
    if not args.no_wbsearch:
        print(f"stage C: wbsearchentities for {len(left)} targets")
        ws = WbSearch()
        judge = judge_stage(stage_wbsearch(left, ws), "wbsearch")

    # Fold results into the artists; merge artists that resolved to the same QID.
    merged = {}
    for key, a in artists.items():
        if not a["qid"] and key in results:
            q, ev, alts, tie = results[key]
            a.update(qid=q, method=methods[key], evidence="; ".join(ev), alternatives="|".join(alts),
                     ambiguous=int(bool(alts)), tie=int(tie))
        elif not a["qid"]:
            mq = [results[mk][0] for mk in a.get("member_keys", []) if mk in results]
            if mq and len(mq) == len(a["member_keys"]):
                a.update(member_qids="|".join(mq), method="members",
                         evidence=" / ".join("; ".join(results[mk][1]) for mk in a["member_keys"]))
        k = a["qid"] or key
        if k in merged:
            m = merged[k]
            m["entries"] += a["entries"]
            m["names"] = list(dict.fromkeys(m["names"] + a["names"]))
            if m["method"] != "pool_join" and a["method"] == "pool_join":
                m["method"] = "pool_join"
        else:
            merged[k] = a

    all_qids = {q for a in merged.values() for q in ([a["qid"]] if a["qid"] else []) + a.get("member_qids", "").split("|") if q}
    facts = fetch_facts(ep, all_qids, args.workers)
    add_qids = sorted(q for q in all_qids if q not in pool)
    countries = sorted({c for q in add_qids if q in facts for k in ("P27", "birth_country", "P17", "P495", "hq_country",
                        "formation_country") for c in facts[q]["claims"].get(k, []) if re.fullmatch(r"Q\d+", c)}
                       | {c for a in merged.values() for c in a["countries"]})
    cinfo = country_info(ep, countries)
    judge = Judge(facts, troots, art, clook)

    lists_by_q = collections.defaultdict(set)
    for a in merged.values():
        for q in ([a["qid"]] if a["qid"] else []) + [x for x in a.get("member_qids", "").split("|") if x]:
            lists_by_q[q] |= {e["list"] for e in a["entries"]}
    additions = [addition_row(q, facts[q], cinfo, art, judge, lists_by_q[q]) for q in add_qids if q in facts]
    add_by_q = {r["qid"]: r for r in additions}

    out = []
    for key, a in merged.items():
        es = a["entries"]
        q = a["qid"]
        mq = [x for x in a.get("member_qids", "").split("|") if x]
        if q:
            in_pool = q in pool
            status = "pool" if in_pool else "resolved_not_in_pool"
        elif mq:
            in_pool = all(x in pool for x in mq)
            status = "pool" if in_pool else "resolved_not_in_pool"
        else:
            in_pool, status = False, "unresolved"
        region = ""
        for x in [q] + mq if q else mq:
            region = (pool.get(x) or add_by_q.get(x) or {}).get("region", "") or region
            if region:
                break
        if not region and a["countries"]:
            region = next((r for r in (bp.region_of(c, cinfo) for c in sorted(a["countries"])) if r), "")
        ranks = [int(e["rank"]) for e in es if re.fullmatch(r"\d+", e["rank"] or "")]
        lists = sorted({e["list"] for e in es})
        out.append({
            "name": a["name"], "norm_name": norm(a["name"]), "lists": "|".join(lists), "n_lists": len(lists),
            "editions": "|".join(sorted({f"{e['list']}:{e['edition']}" for e in es})), "n_entries": len(es),
            "best_rank": min(ranks) if ranks else "", "country": a["country"],
            "birth_year": a["birth"] or "", "qid": q or "",
            "label": (facts.get(q) or {}).get("label", "") or (pool.get(q) or {}).get("label", "") if q else "",
            "status": status, "in_pool": int(in_pool), "method": a["method"] or "",
            "evidence": a.get("evidence", ""), "ambiguous": a.get("ambiguous", 0),
            "alternatives": a.get("alternatives", ""), "member_qids": "|".join(mq), "region": region,
            "_tie": a.get("tie", 0), "_entries": es,
        })
    out.sort(key=lambda r: (r["status"], r["name"].lower()))
    cols = [c for c in out[0] if not c.startswith("_")]
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)
    if additions:
        with open(ADD_PATH, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(additions[0]))
            w.writeheader()
            w.writerows(sorted(additions, key=lambda r: -r["sitelinks"]))

    # Summary.
    st = collections.Counter(r["status"] for r in out)
    newly = collections.Counter(r["method"] for r in out if r["method"] not in ("pool_join", ""))
    print(f"\n{len(out)} distinct list artists: " + ", ".join(f"{k} {v}" for k, v in st.most_common()))
    print("resolved by method: " + ", ".join(f"{k} {v}" for k, v in newly.most_common()))
    print(f"ambiguous: {sum(r['ambiguous'] for r in out)} (tied scores: {sum(r['_tie'] for r in out)})")
    print("\nper list (entries): before -> pool / resolved_not_in_pool / unresolved")
    per = collections.defaultdict(collections.Counter)
    for r in out:
        for e in r["_entries"]:
            c = per[e["list"]]
            c["n"] += 1
            c["before"] += bool(e["qid"])
            c[r["status"]] += 1
    for lst, c in sorted(per.items(), key=lambda x: -x[1]["n"]):
        print(f"  {lst:30s} {c['n']:5d}  matched before {c['before']:4d}  pool {c['pool']:4d}  "
              f"resolved_not_in_pool {c['resolved_not_in_pool']:4d}  unresolved {c['unresolved']:4d}")
    print("\nby region (distinct artists): pool / resolved_not_in_pool / unresolved")
    reg = collections.defaultdict(collections.Counter)
    for r in out:
        reg[r["region"] or "(unknown)"][r["status"]] += 1
    for k, c in sorted(reg.items(), key=lambda x: -sum(x[1].values())):
        print(f"  {k:30s} pool {c['pool']:4d}  resolved_not_in_pool {c['resolved_not_in_pool']:4d}  "
              f"unresolved {c['unresolved']:4d}")
    print(f"\nwrote {OUT_PATH}\nwrote {ADD_PATH} ({len(additions)} rows)")


if __name__ == "__main__":
    main()
