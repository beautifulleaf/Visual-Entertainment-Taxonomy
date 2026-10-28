"""Major-award signal for series: winners and nominees of the big TV awards.

sourcing-plan.md §3 and §5 admit a series on "a major award" as well as on
audience counts. This collects, for each award category below, the series that
won it (won = 1) or were nominated (won = 0):

  Primetime Emmy        Drama / Comedy / Limited or Anthology Series
  International Emmy    Drama Series, Comedy, Telenovela, Non-English US Primetime
  BAFTA TV              Drama Series, Scripted Comedy (+ Comedy Programme), Mini-Series, International
  Peabody               all winners that are series
  Golden Globe          TV Series Drama, Musical or Comedy, Limited/Anthology Series
  Premios TVyNovelas    Best Telenovela
  Indian Telly Awards   Best Drama Series
  Golden Butterfly      Best Series, Best Comedy Series (Altın Kelebek, from trwiki)
  Baeksang Arts Awards  Best Drama, Grand Prize (Television)
  Golden Eagle (China)  Best Television Series
  Flying Apsaras        drama-series prizes (Feitian, from zhwiki ceremony pages)
  Magnolia              Best Television Series
  Golden Bell (Taiwan)  Best Television Series
  Asian Television Awards  Best Drama Series

Sources, in order:
  1. Wikidata: award received (P166) / nominated for (P1411) whose value is the
     category item (or a subclass of it), stated on the series itself or on a
     person with "for work" (P1686) pointing at the series. Point in time (P585)
     gives the year. Wikidata turns out to be thin for every award (e.g. 11 of
     ~40 Emmy drama winners carry the statement), so:
  2. Wikipedia list pages (wikitext via action=raw, cached under
     data/raw/tv_awards/, fetched ~1 s apart). Linked titles are resolved to
     QIDs through Wikidata sitelinks (season pages to their series); unlinked
     or unresolved titles are matched to data/interim/tv_routed.csv by
     normalised title + start year.
Then QIDs get IMDb ids (P345) and country (P495) from Wikidata. Peabody rows
are kept only when they resolve to a series (Peabody also honours radio,
news and films); for the other awards a row is dropped only if it resolves to
a non-series item that is not in tv_routed.

Output: data/interim/tv_awards.csv
  award, category, year, won, title, qid, tconst, country, source, match
  source = wikidata | wikipedia | both; match = qid | title | none
  (how the row got its tconst/identity).

Usage: python3 pipelines/tv/awards.py [--offline]
  --offline  use only cached Wikipedia pages (Wikidata is still queried)
"""
import argparse
import collections
import csv
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "visual_art"))
from wikidata import sparql, year_of  # noqa: E402

RAW = os.path.join(ROOT, "data", "raw", "tv_awards")
ROUTED = os.path.join(ROOT, "data", "interim", "tv_routed.csv")
OUT = os.path.join(ROOT, "data", "interim", "tv_awards.csv")
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"
PROGRAMME_CLASSES = "wd:Q5398426 wd:Q15416 wd:Q1259759 wd:Q526877"  # TV series, TV programme, miniseries, web series
SEASON_CLASS = "Q3464665"  # television series season
VOTES_RULE = 2500

# (award, category, Wikidata category QIDs, Wikipedia pages, fallback country)
# A page is (lang, title, parser); parsers: table, winners (winners-only table),
# peabody, bullets, ata, feitian.
AWARDS = [
    ("Primetime Emmy", "Outstanding Drama Series", ["Q989438"],
     [("en", "Primetime Emmy Award for Outstanding Drama Series", "table")], ""),
    ("Primetime Emmy", "Outstanding Comedy Series", ["Q2110156"],
     [("en", "Primetime Emmy Award for Outstanding Comedy Series", "table")], ""),
    ("Primetime Emmy", "Outstanding Limited or Anthology Series", ["Q20714679", "Q13423511"],
     [("en", "Primetime Emmy Award for Outstanding Limited or Anthology Series", "table")], ""),
    ("International Emmy", "Drama Series", ["Q16146879", "Q18466341"],
     [("en", "International Emmy Award for Best Drama Series", "table")], ""),
    ("International Emmy", "Comedy", ["Q10354949"],
     [("en", "International Emmy Award for Best Comedy Series", "table")], ""),
    ("International Emmy", "Telenovela", ["Q10354950"],
     [("en", "International Emmy Award for Best Telenovela", "table")], ""),
    ("International Emmy", "Non-English Language U.S. Primetime Program", ["Q18466357"],
     [("en", "International Emmy Award for Best Non-English Language U.S. Primetime Program", "table")], "US"),
    ("BAFTA TV", "Drama Series", ["Q2925698"],
     [("en", "British Academy Television Award for Best Drama Series", "table")], "GB"),
    ("BAFTA TV", "Scripted Comedy", ["Q4969377", "Q2925696"],
     [("en", "British Academy Television Award for Best Scripted Comedy", "table"),
      ("en", "British Academy Television Award for Best Comedy (Programme or Series)", "table")], "GB"),
    ("BAFTA TV", "Mini-Series", ["Q96373984"],
     [("en", "British Academy Television Award for Best Mini-Series", "table")], "GB"),
    ("BAFTA TV", "International", ["Q16985329"],
     [("en", "British Academy Television Award for Best International Programme", "table")], ""),
    ("Peabody", "Peabody Award", ["Q838121"],
     [("en", f"List of Peabody Award winners ({d}–{d + 9})", "peabody") for d in range(1940, 2030, 10)], ""),
    ("Golden Globe", "Television Series – Drama", ["Q1255198"],
     [("en", "Golden Globe Award for Best Television Series – Drama", "table")], ""),
    ("Golden Globe", "Television Series – Musical or Comedy", ["Q596294"],
     [("en", "Golden Globe Award for Best Television Series – Musical or Comedy", "table")], ""),
    ("Golden Globe", "Limited or Anthology Series or Television Film", ["Q265435"],
     [("en", "Golden Globe Award for Best Limited or Anthology Series or Television Film", "table")], ""),
    ("Premios TVyNovelas", "Best Telenovela", ["Q4376954", "Q56291477"],
     [("en", "TVyNovelas Award for Best Telenovela of the Year", "table")], "MX"),
    ("Indian Telly Awards", "Best Drama Series", ["Q16965258"],
     [("en", "Indian Telly Award for Best Drama Series", "winners")], "IN"),
    ("Golden Butterfly", "Best Series", ["Q118956281"],
     [("tr", "En İyi Dizi Altın Kelebek Ödülü", "table")], "TR"),
    ("Golden Butterfly", "Best Comedy Series", ["Q118956282"],
     [("tr", "En İyi Komedi Dizisi Altın Kelebek Ödülü", "table")], "TR"),
    ("Baeksang Arts Awards", "Best Drama", ["Q65121872"],
     [("en", "Baeksang Arts Award for Best Drama", "table")], "KR"),
    ("Baeksang Arts Awards", "Grand Prize – Television", ["Q65121870"],
     [("en", "Baeksang Arts Award Grand Prize – Television", "table")], "KR"),
    ("Golden Eagle (China)", "Best Television Series", ["Q5579357", "Q10873960"],
     [("en", "Golden Eagle Award for Best Television Series (China)", "table")], "CN"),
    ("Flying Apsaras", "Outstanding Television Series", ["Q724606"],
     [("zh", "<search>", "feitian")], "CN"),
    ("Magnolia", "Best Television Series", ["Q6731859"],
     [("en", "Magnolia Award for Best Television Series", "table")], ""),
    ("Golden Bell", "Best Television Series", ["Q4896818"],
     [("en", "Golden Bell Award for Best Television Series", "bullets")], "TW"),
    ("Asian Television Awards", "Best Drama Series", [],
     [("en", "Asian Television Awards", "ata")], ""),
]
WIN_MARKERS = ("faeb86", "b0c4de", "eedd82", "ffd700", "background:gold", "double dagger", "‡")
YEAR_RE = re.compile(r"(?<!\d)(19[3-9]\d|20[0-3]\d)(?!\d|s)")


# ---------------------------------------------------------------- fetching

_last_fetch = [0.0]


def http_get(url, retries=8):
    for attempt in range(retries):
        wait = 1.0 - (time.time() - _last_fetch[0])
        if wait > 0:
            time.sleep(wait)
        _last_fetch[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503, 504):
                pause = int(e.headers.get("Retry-After") or 0) or min(120, 5 * 2 ** attempt)
                print(f"    HTTP {e.code} for {url[:80]}..., retrying in {pause}s")
                time.sleep(pause)
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"    {e}, retrying")
            time.sleep(min(120, 5 * 2 ** attempt))
    raise RuntimeError(f"fetch failed repeatedly: {url}")


def wikitext(lang, title, offline=False):
    """Raw wikitext of a page, cached; '' if the page does not exist."""
    os.makedirs(RAW, exist_ok=True)
    path = os.path.join(RAW, f"{lang}_{title.replace(' ', '_').replace('/', '_')}.wiki")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    if offline:
        return ""
    url = f"https://{lang}.wikipedia.org/w/index.php?" + urllib.parse.urlencode({"title": title, "action": "raw"})
    body = http_get(url)
    text = body.decode("utf-8") if body else ""
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return text


def resolve_redirects(lang, titles):
    """{title: target} for titles that are redirects (MediaWiki API, 50 per call)."""
    out = {}
    titles = sorted(titles)
    for i in range(0, len(titles), 50):
        url = f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
            "action": "query", "titles": "|".join(titles[i:i + 50]), "redirects": 1, "format": "json"})
        data = json.loads(http_get(url) or b"{}")
        q = data.get("query", {})
        norm = {n["from"]: n["to"] for n in q.get("normalized", [])}
        red = {r["from"]: r["to"] for r in q.get("redirects", [])}
        for t in titles[i:i + 50]:
            n = norm.get(t, t)
            if n in red:
                out[t] = red[n]
            elif n != t:
                out[t] = n
    return out


# ---------------------------------------------------------------- wikitext parsing

def clean(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"<ref[^>]*/>", "", text)
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.S)
    return text


def strip_templates(s):
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    return s


def plain(s):
    """Wikitext -> plain text (links to labels, markup dropped)."""
    s = strip_templates(s)
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\[https?://\S+\s*([^\]]*)\]", r"\1", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("'''", "").replace("''", "")
    return re.sub(r"\s+", " ", s).strip(" ,;:-–\"")


LINK_RE = re.compile(r"\[\[([^\]|#]*)(?:#[^\]|]*)?(?:\|([^\]]*))?\]\]")


def entry_from(fragment):
    """(title, link target or '') from the wikitext of one title."""
    fragment = strip_templates(fragment)
    m = LINK_RE.search(fragment)
    if m and m.group(1).strip() and not re.match(r"(?i)(file|image|category):", m.group(1)):
        target = m.group(1).strip()
        label = plain(m.group(2) or target)
        # Only take the link if it is the title itself, not a link inside a longer title.
        rest = plain(LINK_RE.sub("", fragment))
        if len(rest) <= 3 or len(rest) < len(label):
            return label, target
    return plain(fragment), ""


def italic_title(cell):
    """First italic segment of a cell -> (title, target), or None."""
    s = strip_templates(cell).replace("'''", "")
    m = re.search(r"''(.+?)''", s)
    if not m:
        return None
    title, target = entry_from(m.group(1))
    return (title, target) if title else None


def split_cell(raw):
    """'attrs | content' -> (attrs, content), ignoring pipes inside [[ ]] and {{ }}."""
    depth = 0
    for i, ch in enumerate(raw):
        two = raw[i:i + 2]
        if two in ("[[", "{{"):
            depth += 1
        elif two in ("]]", "}}"):
            depth -= 1
        elif ch == "|" and depth == 0 and raw[i:i + 2] != "||":
            return raw[:i], raw[i + 1:]
    return "", raw


def split_row_cells(lines):
    cells = []
    for line in lines:
        if line and line[0] in "|!" and not line.startswith(("|-", "|}", "|+", "{|")):
            sep = "!!" if line[0] == "!" else "||"
            for part in line[1:].split(sep):
                cells.append(list(split_cell(part)) + [line[0]])
        elif cells:
            cells[-1][1] += "\n" + line
    return cells


def tables(text):
    """Yield (heading_year, list_of_rows) per wikitable; a row is (row_attrs, cells)."""
    heading_year = None
    rows, cur, in_table, row_attrs = None, [], 0, ""
    for line in text.split("\n"):
        st = line.strip()
        if not in_table and re.match(r"^=+[^=].*=+$", st):
            m = YEAR_RE.search(st)
            heading_year = int(m.group(1)) if m else heading_year
            continue
        if st.startswith("{|"):
            in_table += 1
            if in_table == 1:
                rows, cur, row_attrs = [], [], ""
            continue
        if not in_table:
            continue
        if st.startswith("|}"):
            in_table -= 1
            if in_table == 0:
                rows.append((row_attrs, split_row_cells(cur)))
                yield heading_year, rows
            continue
        if in_table > 1:
            continue
        if st.startswith("|-"):
            rows.append((row_attrs, split_row_cells(cur)))
            cur, row_attrs = [], st
        else:
            cur.append(st)


def parse_table(text, winners_only=False, title_cell="first"):
    out = []
    for heading_year, rows in tables(clean(text)):
        year = heading_year
        for row_attrs, cells in rows:
            if not cells:
                continue
            found, title_idx = None, None
            order = range(len(cells) - 1, -1, -1) if title_cell == "last" else range(len(cells))
            for i in order:
                if cells[i][2] == "!" and title_cell != "last":
                    continue
                found = italic_title(cells[i][1])
                if found:
                    title_idx = i
                    break
            before = cells if title_idx is None else cells[:title_idx] if title_cell == "first" else []
            for attrs, content, _ in before:
                m = YEAR_RE.search(plain(content))
                if m:
                    year = int(m.group(1))
                    break
            if not found:
                continue
            blob = (row_attrs + " " + " ".join(a + " " + c for a, c, _ in cells)).lower()
            won = 1 if winners_only or any(k in blob for k in WIN_MARKERS) else 0
            out.append((year, won, found[0], found[1]))
    return out


def parse_bullets(text):
    """'* YEAR: ''Winner''' / '** ''Nominee''' lists (Golden Bell)."""
    out, year = [], None
    for line in clean(text).split("\n"):
        m = re.match(r"^(\*+)\s*(.*)$", line.strip())
        if not m:
            continue
        level, body = len(m.group(1)), m.group(2)
        if level == 1:
            y = YEAR_RE.search(plain(body.split(":")[0]))
            if not y:
                continue
            year = int(y.group(1))
        found = italic_title(body)
        if found and year:
            out.append((year, 1 if level == 1 else 0, found[0], found[1]))
    return out


def parse_ata(text):
    """Asian Television Awards: 'Best Drama Series' entries in the per-year Winners sections."""
    text = clean(text)
    start, end = text.find("==Winners=="), text.find("==Acting award winners==")
    out, year = [], None
    lines = text[start:end].split("\n")
    i = 0
    while i < len(lines):
        st = lines[i].strip()
        hm = re.match(r"^=+\s*(\d{4})\s*=+$", st)
        if hm:
            year = int(hm.group(1))
        m = re.match(r"^[|*]\s*Best Drama Series\s*(?::|\|\||$)(.*)$", st)
        if m and year:
            if st.startswith("*"):   # list format: winners only
                q = re.search(r'"(.+?)"', m.group(1))
                if q:
                    out.append((year, 1) + entry_from(q.group(1)))
            else:
                block = [m.group(1)]
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith(("|-", "|}")):
                    block.append(lines[j].strip())
                    j += 1
                cells = []
                for b in block:
                    if b.startswith("|") or not cells:
                        cells.extend(x for x in b.lstrip("|").split("||"))
                    else:
                        cells[-1] += "\n" + b
                cells = [c for c in cells if c.strip()]
                for ci, cell in enumerate(cells):
                    for frag in re.findall(r"'''(.+?)'''", strip_templates(cell)):
                        title, target = entry_from(frag.replace("''", ""))
                        title = re.sub(r"\s*\((Episode|Season)[^)]*\)|\s+Season \d+.*$", "", title)
                        if title:
                            out.append((year, 1 if ci == 0 else 0, title, target))
                i = j
        i += 1
    return out


def parse_feitian(text):
    """One zhwiki Flying Apsaras ceremony page: works in drama-series sections."""
    text = clean(text)
    m = re.search(r"date\s*=\s*.*?((?:19|20)\d\d)年", text) or re.search(r"((?:19|20)\d\d)年", text)
    year = int(m.group(1)) if m else None
    out, keep, nominee_col = [], False, None
    for block in re.split(r"\n(?==+[^=])", text):
        head = block.split("\n", 1)[0]
        if head.startswith("="):
            h = plain(head.strip("= "))
            keep = bool(re.search(r"电视剧|连续剧|长篇|中篇|大奖", h)) and not re.search(
                r"单本|儿童|戏曲|译制|单项|演员|导演|编剧|个人|短剧|美术|音乐|摄像|特别", h)
        if not keep:
            continue
        nominee_col = None
        col = hcount = 0
        for line in block.split("\n"):
            st = line.strip()
            if st.startswith("{|"):
                hcount = 0
                continue
            if st.startswith("!"):
                for part in st.lstrip("!").split("!!"):
                    if "提名" in part and nominee_col is None:
                        nominee_col = hcount
                    hcount += 1
                continue
            if st.startswith("|-"):
                col = 0
                continue
            if st.startswith("|") and not st.startswith(("|}", "|+")):
                col += 1
                st = split_cell(st[1:])[1]
            nominated = "提名" in st or (nominee_col is not None and col - 1 >= nominee_col)
            for w in re.findall(r"《(.+?)》", st):
                title, target = entry_from(w)
                if title:
                    out.append((year, 0 if nominated else 1, title, target))
    return out


def feitian_pages():
    rows = sparql("""SELECT ?title WHERE {
      SERVICE wikibase:mwapi { bd:serviceParam wikibase:endpoint "zh.wikipedia.org"; wikibase:api "Generator";
        mwapi:generator "search"; mwapi:gsrsearch "intitle:飞天奖"; mwapi:gsrlimit "max".
        ?title wikibase:apiOutput mwapi:title. } }""")
    return sorted({r["title"] for r in rows if re.match(r"^第\d+届(中国)?电视剧飞天奖$", r["title"])})


# ---------------------------------------------------------------- Wikidata

def chunks(xs, n):
    xs = list(xs)
    for i in range(0, len(xs), n):
        yield xs[i:i + n]


def wikidata_awards():
    """Rows (award, category, year, won, qid) from P166/P1411 statements."""
    by_qid = {}
    for award, category, qids, _, _ in AWARDS:
        for q in qids:
            by_qid[q] = (award, category)
    q = """SELECT ?root ?item ?kind ?work ?t WHERE {
      VALUES ?root { %s }
      ?cat wdt:P279* ?root .
      { ?item p:P166 ?st . ?st ps:P166 ?cat . BIND("won" AS ?kind) }
      UNION { ?item p:P1411 ?st . ?st ps:P1411 ?cat . BIND("nom" AS ?kind) }
      OPTIONAL { ?st pq:P1686 ?work }
      OPTIONAL { ?st pq:P585 ?t }
    }""" % " ".join("wd:" + x for x in by_qid)
    out = []
    for r in sparql(q):
        award, category = by_qid[r["root"]]
        out.append((award, category, year_of(r.get("t")), 1 if r["kind"] == "won" else 0, r.get("work") or r["item"]))
    return out


def sitelink_qids(lang, titles):
    out = {}
    for batch in chunks(sorted(titles), 200):
        values = " ".join('"%s"@%s' % (t.replace("\\", "\\\\").replace('"', '\\"'), lang) for t in batch)
        for r in sparql("""SELECT ?name ?item WHERE { VALUES ?name { %s }
            ?a schema:about ?item; schema:isPartOf <https://%s.wikipedia.org/>; schema:name ?name . }""" % (values, lang)):
            out[r["name"]] = r["item"]
    return out


def item_details(qids):
    """{qid: {label, tconst, country, series(bool), season_of, start}}."""
    out = {}
    for batch in chunks(sorted(qids), 300):
        q = """SELECT ?item ?label ?imdb ?cc ?isSeries ?seasonOf ?start WHERE {
          VALUES ?item { %s }
          OPTIONAL { ?item rdfs:label ?label FILTER(LANG(?label) = "en") }
          OPTIONAL { ?item wdt:P345 ?imdb FILTER(STRSTARTS(?imdb, "tt")) }
          OPTIONAL { ?item wdt:P495/wdt:P297 ?cc }
          OPTIONAL { ?item wdt:P580|wdt:P577 ?start }
          OPTIONAL { VALUES ?cls { %s } ?item wdt:P31/wdt:P279* ?cls . BIND(true AS ?isSeries) }
          OPTIONAL { ?item wdt:P31 wd:%s ; wdt:P179|wdt:P361 ?seasonOf }
        }""" % (" ".join("wd:" + x for x in batch), PROGRAMME_CLASSES, SEASON_CLASS)
        for r in sparql(q):
            d = out.setdefault(r["item"], {"label": "", "tconst": "", "country": "", "series": False,
                                           "season_of": "", "start": None})
            d["label"] = d["label"] or r.get("label", "")
            d["tconst"] = d["tconst"] or r.get("imdb", "")
            d["country"] = d["country"] or r.get("cc", "")
            d["series"] = d["series"] or bool(r.get("isSeries"))
            d["season_of"] = d["season_of"] or r.get("seasonOf", "")
            y = year_of(r.get("start"))
            if y and (d["start"] is None or y < d["start"]):
                d["start"] = y
    return out


# ---------------------------------------------------------------- title matching

def norm(title):
    t = unicodedata.normalize("NFKD", title or "").encode("ascii", "ignore").decode().lower()
    t = re.sub(r"\(.*?\)", " ", t)
    t = t.replace("&", " and ")
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    t = re.sub(r"^(the|a|an) ", "", t)
    return t


def load_routed():
    rows = {}
    by_title = collections.defaultdict(list)
    with open(ROUTED, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            r["votes"] = int(float(r["imdb_votes"] or 0))
            r["start"] = int(r["start_year"]) if (r.get("start_year") or "").isdigit() else None
            rows[r["tconst"]] = r
            by_title[norm(r["mdblist_title"])].append(r)
    return rows, by_title


def title_match(by_title, title, year, country):
    cands = by_title.get(norm(title), [])
    if year:
        cands = [c for c in cands if c["start"] and year - 15 <= c["start"] <= year + 1]
    if not cands:
        return None
    if country:
        same = [c for c in cands if c["country"] == country]
        cands = same or cands
    return max(cands, key=lambda c: c["votes"])


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--offline", action="store_true", help="only use cached Wikipedia pages")
    args = ap.parse_args()

    routed, by_title = load_routed()
    print(f"tv_routed: {len(routed)} series")

    # 1. Wikipedia lists
    wiki_rows = []   # (award, category, year, won, title, lang, target, fallback_country)
    for award, category, _, pages, fallback in AWARDS:
        for lang, title, parser in pages:
            titles = feitian_pages() if parser == "feitian" else [title]
            got = []
            for t in titles:
                text = wikitext(lang, t, args.offline)
                if not text:
                    print(f"  missing page {lang}:{t}")
                    continue
                if parser in ("table", "winners"):
                    got += parse_table(text, winners_only=parser == "winners")
                elif parser == "peabody":
                    got += [(y, 1, a, b) for y, _, a, b in parse_table(text, title_cell="last")]
                elif parser == "bullets":
                    got += parse_bullets(text)
                elif parser == "ata":
                    got += parse_ata(text)
                elif parser == "feitian":
                    got += parse_feitian(text)
            wiki_rows += [(award, category, y, w, ti, lang, tg, fallback) for y, w, ti, tg in got]
            print(f"  {award} / {category} [{lang}:{title}]: {len(got)} entries, "
                  f"{sum(1 for g in got if g[1])} won")

    # 2. Link targets -> QIDs (sitelinks, then redirects)
    targets = collections.defaultdict(set)
    for r in wiki_rows:
        if r[6]:
            t = r[6].replace("_", " ").strip()
            targets[r[5]].add(t[:1].upper() + t[1:])
    link_qid = {}
    for lang, ts in targets.items():
        found = sitelink_qids(lang, ts)
        missing = ts - set(found)
        if missing and not args.offline:
            red = resolve_redirects(lang, missing)
            found2 = sitelink_qids(lang, set(red.values()))
            for src, dst in red.items():
                if dst in found2:
                    found[src] = found2[dst]
        for t, q in found.items():
            link_qid[(lang, t)] = q
        print(f"  {lang}: {len(found)}/{len(ts)} linked titles resolved to QIDs")

    # 3. Wikidata award statements
    wd_rows = wikidata_awards()
    print(f"  Wikidata: {len(wd_rows)} award statements")

    # 4. Item details (plus season -> series)
    qids = {q for q in link_qid.values()} | {r[4] for r in wd_rows}
    details = item_details(qids)
    seasons = {d["season_of"] for d in details.values() if d["season_of"] and not d["series"]}
    details.update(item_details(seasons - set(details)))

    def series_qid(q):
        d = details.get(q)
        if d and d["season_of"] and not d["series"]:
            return d["season_of"]
        return q

    # 5. Assemble
    records = []
    for award, category, year, won, title, lang, target, fallback in wiki_rows:
        t = target.replace("_", " ").strip()
        q = link_qid.get((lang, t[:1].upper() + t[1:])) if t else None
        records.append({"award": award, "category": category, "year": year, "won": won, "title": title,
                        "qid": series_qid(q) if q else "", "source": "wikipedia", "fallback": fallback})
    wiki_keys = collections.defaultdict(int)
    for r in records:
        if r["qid"]:
            k = (r["award"], r["category"], r["qid"])
            wiki_keys[k] = max(wiki_keys[k], r["won"])
    wd_added = 0
    for award, category, year, won, q in wd_rows:
        q = series_qid(q)
        k = (award, category, q)
        if k in wiki_keys and wiki_keys[k] >= won:
            for r in records:
                if (r["award"], r["category"], r["qid"]) == k and r["source"] == "wikipedia":
                    r["source"] = "both"
            continue
        fallback = next(a[4] for a in AWARDS if a[0] == award and a[1] == category)
        records.append({"award": award, "category": category, "year": year, "won": won, "title": "",
                        "qid": q, "source": "wikidata", "fallback": fallback})
        wd_added += 1
    print(f"  Wikidata rows not already in the Wikipedia lists: {wd_added}")

    out, dropped = {}, collections.Counter()
    for r in records:
        d = details.get(r["qid"]) if r["qid"] else None
        title = r["title"] or (d["label"] if d else "") or r["qid"]
        tconst = d["tconst"] if d else ""
        country = d["country"] if d else ""
        match = "qid" if tconst else "none"
        if not tconst:
            m = title_match(by_title, title, r["year"], country or r["fallback"])
            if not m and d and d["label"] and d["label"] != title:
                m = title_match(by_title, d["label"], r["year"], country or r["fallback"])
            if m:
                tconst, match = m["tconst"], "title"
                country = country or m["country"]
        if not country and tconst in routed:
            country = routed[tconst]["country"]
        country = country or r["fallback"]
        if r["qid"] and d is None and not tconst:
            pass   # unresolved QID details (should not happen); keep
        is_series = bool(d and d["series"]) or tconst in routed
        if r["award"] == "Peabody" and not is_series:
            dropped[r["award"]] += 1
            continue
        if d is not None and not d["series"] and tconst not in routed:
            dropped[r["award"]] += 1
            continue
        if r["source"] == "wikidata" and not d:
            dropped[r["award"]] += 1
            continue
        key = (r["award"], r["category"], r["year"], r["qid"] or tconst or norm(title), r["won"])
        if key in out:
            if r["source"] != out[key]["source"]:
                out[key]["source"] = "both"
            continue
        out[key] = {"award": r["award"], "category": r["category"], "year": r["year"] or "", "won": r["won"],
                    "title": title, "qid": r["qid"], "tconst": tconst, "country": country,
                    "source": r["source"], "match": match}
    # A nominee row is redundant when the same series won that category the same year.
    rows = [v for k, v in out.items() if not (k[4] == 0 and (k[0], k[1], k[2], k[3], 1) in out)]
    rows.sort(key=lambda x: (x["award"], x["category"], x["year"] or 0, -x["won"], x["title"]))
    print(f"  dropped non-series rows: {dict(dropped)}")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    cols = ["award", "category", "year", "won", "title", "qid", "tconst", "country", "source", "match"]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {os.path.relpath(OUT, ROOT)}")

    # ---- report
    print(f"\n{'award / category':62} {'won':>5} {'nom':>5} {'qid':>5} {'title':>5} {'none':>5} {'wd':>4}")
    for award, category, *_ in AWARDS:
        sub = [r for r in rows if r["award"] == award and r["category"] == category]
        c = collections.Counter(r["match"] for r in sub)
        print(f"{award + ' / ' + category:62.62} {sum(r['won'] for r in sub):5} "
              f"{sum(1 - r['won'] for r in sub):5} {c['qid']:5} {c['title']:5} {c['none']:5} "
              f"{sum(1 for r in sub if r['source'] != 'wikipedia'):4}")

    def series_key(r):
        return r["tconst"] or r["qid"] or "t:" + norm(r["title"])
    for label, subset in (("won", [r for r in rows if r["won"]]), ("won or nominated", rows)):
        keys = {series_key(r) for r in subset}
        tcs = {r["tconst"] for r in subset if r["tconst"]}
        in_routed = {t for t in tcs if t in routed}
        below = {t for t in in_routed if routed[t]["votes"] < VOTES_RULE}
        print(f"\nSeries that {label}: {len(keys)} distinct; {len(tcs)} with a tconst "
              f"({len(in_routed)} in tv_routed); not already >= {VOTES_RULE} IMDb votes: "
              f"{len(below)} in tv_routed below the line + {len(tcs - in_routed)} not in tv_routed")
        by_db = collections.Counter(routed[t]["database"] for t in below)
        print(f"  below the line by database: {dict(by_db)}")


if __name__ == "__main__":
    main()
