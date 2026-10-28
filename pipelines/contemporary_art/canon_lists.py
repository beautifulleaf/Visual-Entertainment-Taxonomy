"""Non-Wikidata canon and signal lists for contemporary artists (visual-art-plan.md §3.2, §3.5).

Gathers the "auto-include" lists and the related signal lists for artists active
after 1960, one row per (list, edition, entry):

  kunstkompass       Capital Kunstkompass top 10 per year, 2001 onwards. The full top 100
                     is behind Capital's paywall and capital.de refuses automated clients,
                     so the transcriptions on German Wikipedia ("Kunstkompass") are used.
  artreview_power100 ArtReview Power 100. artreview.com is a Gatsby site; every entry has
                     a page-data JSON giving its place per edition plus the previous and
                     next entries, so each edition is read by walking that chain from a
                     seed entry. Non-artists (curators, collectors, gallerists, ...) are
                     kept but flagged is_artist=0, from ArtReview's own category (Artist,
                     Artists and Artist Collective count as artists).
  artprice_top500    Artprice Contemporary Art Market Report: Top 500 contemporary artists
  artprice_ultra100  (born after 1945) by auction turnover, and the Top 100
                     ultra-contemporary artists when the edition has one (2026 only has a
                     Top 10 of ultra-contemporary auction debuts). Parsed from the
                     free PDFs on imgpublic.artprice.com (needs `pypdf`).
  venice_biennale    Main (international) exhibition of the Venice Biennale, from the
                     official artist lists on labiennale.org (robots.txt asks for 60 s
                     between requests, so the first run of this source is slow).
  documenta          documenta 14 and documenta fifteen participants (English Wikipedia).
  <biennial>         Other biennials from their participant announcements, mostly on e-flux
                     (see EFLUX below): Sharjah 14-17, Istanbul 18, Gwangju 15-16,
                     Kochi-Muziris 6, São Paulo 35 (bienal.org.br) and 36, Dak'Art 15
                     (africanscolumn.com transcription). The Asia Pacific Triennial is missing:
                     qagoma.qld.gov.au answers 403 and e-flux only names a handful of APT11 artists.
  prize_jameel       Jameel Prize winners and shortlists, editions 2-5 (V&A article pages;
                     editions 1, 6 and 7 have no parseable V&A page).
  prize_<name>       Prize winners (and shortlists where the page has them) from English
                     Wikipedia: Turner, Hugo Boss, Praemium Imperiale (painting and
                     sculpture only), Marcel Duchamp, Venice Golden/Silver Lions, Future
                     Generation Art Prize, Prince Claus Award (all laureates; is_artist is a
                     keyword guess from Wikipedia's one-line description).

Not used, and why:
  universes.art (Universes in Universe) and artprice.com: their robots.txt opts out of
  Anthropic's agents (anthropic-ai / Claude-Web / ClaudeBot). This script is run by an AI
  agent, so fetch() honours those rules as well as the ones for its own user agent.
  capital.de: answers every non-browser client with 403, and the full Kunstkompass top 100
  is not published anywhere else in the open (press coverage gives the top 10-13 only).

Robustness: fetch() retries timeouts, connection errors and 429/5xx with exponential backoff;
each source runs independently (a failing one keeps its rows from the previous output), and
the output is checkpointed after every source. Re-runs are cheap: every cached page is reused.

Every page is fetched once, one request at a time (>= 1.5 s apart per host, or the
host's robots.txt Crawl-delay), with an identifying User-Agent, after checking
robots.txt, and cached under data/raw/contemporary/<host>/.

Output: data/interim/contemporary_lists.csv with columns
  list, edition, rank, name, country, birth_year, is_artist, role, note, source_url
`name` is the name as given by the source (Artprice's "First LAST" kept as printed);
`role` is winner / nominee / laureate / participant / ranked; `is_artist` is 1, 0 or
blank (unknown). Matching to Wikidata is a later step.

Usage: python3 pipelines/contemporary_art/canon_lists.py [--only kunstkompass artprice ...]
       [--power100-editions 2019 2020 ... 2025]
"""
import argparse
import collections
import csv
import hashlib
import html
import json
import logging
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw", "contemporary")
OUT_PATH = os.path.join(ROOT, "data", "interim", "contemporary_lists.csv")
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"
# robots.txt groups that also apply to us: this pipeline is run by an AI agent.
AGENT_TOKENS = ("ClaudeBot", "Claude-Web", "anthropic-ai", "Claude-User")
MIN_DELAY = 1.5
FIELDS = ["list", "edition", "rank", "name", "country", "birth_year", "is_artist", "role", "note", "source_url"]

# ---------------------------------------------------------------- fetching

_robots, _last = {}, {}


class Blocked(Exception):
    pass


def cache_path(url):
    p = urllib.parse.urlsplit(url)
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", (p.path + ("?" + p.query if p.query else "")).strip("/"))[:120]
    return os.path.join(RAW, p.netloc, f"{name or 'index'}.{hashlib.sha1(url.encode()).hexdigest()[:10]}")


def _robots_for(scheme, host):
    if host not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            req = urllib.request.Request(f"{scheme}://{host}/robots.txt", headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                rp.parse(r.read().decode("utf-8", "replace").splitlines())
        except urllib.error.HTTPError as e:
            rp.allow_all = e.code in (404, 410)
            rp.disallow_all = not rp.allow_all
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            # robots.txt unreachable: do not cache the failure, so a later call can retry
            raise urllib.error.URLError(f"robots.txt of {host} unreachable: {e}")
        _robots[host] = rp
        _last[host] = time.time()
    return _robots[host]


def fetch(url, binary=False):
    """GET url politely (robots.txt, per-host delay, retries on 429/503), cached under RAW."""
    path = cache_path(url)
    if not os.path.exists(path):
        p = urllib.parse.urlsplit(url)
        rp = _robots_for(p.scheme, p.netloc)
        for agent in (UA,) + AGENT_TOKENS:
            if not rp.can_fetch(agent, url):
                raise Blocked(f"robots.txt of {p.netloc} disallows {agent} for {url}")
        delay = max(MIN_DELAY, float(rp.crawl_delay(UA) or 0))
        attempts = 5
        for attempt in range(attempts):
            wait = _last.get(p.netloc, 0) + delay - time.time()
            if wait > 0:
                time.sleep(wait)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=120) as r:
                    body = r.read()
                break
            except urllib.error.HTTPError as e:
                # transient server-side errors: back off and retry; anything else (404, 403) is final
                if e.code in (429, 500, 502, 503, 504) and attempt < attempts - 1:
                    ra = e.headers.get("Retry-After") or ""
                    time.sleep(int(ra) if ra.isdigit() else min(300, 10 * 2 ** attempt))
                    continue
                raise
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
                # DNS hiccups, resets, timeouts, truncated reads: exponential backoff
                if attempt < attempts - 1:
                    print(f"  fetch {url}: {e}; retrying", file=sys.stderr)
                    time.sleep(min(300, 5 * 2 ** attempt))
                    continue
                raise
            finally:
                _last[p.netloc] = time.time()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path + ".part", "wb") as f:
            f.write(body)
        os.replace(path + ".part", path)
    with open(path, "rb") as f:
        data = f.read()
    return data if binary else data.decode("utf-8", "replace")


def wiki_raw(title, lang="en"):
    # /w/index.php and /w/api.php are disallowed in robots.txt; /wiki/<title>?action=raw is not.
    return fetch(f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(title)}?action=raw")


# ---------------------------------------------------------------- text helpers

def row(lst, edition, name, rank="", country="", birth="", is_artist="", role="", note="", src=""):
    return {"list": lst, "edition": edition, "rank": rank, "name": clean(name), "country": clean(country),
            "birth_year": birth or "", "is_artist": is_artist, "role": role, "note": clean(note), "source_url": src}


def clean(s):
    s = html.unescape(str(s or "")).replace("\xa0", " ")
    return " ".join(s.split()).strip(" ,;:*")


def strip_html(s):
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h\d)>", "\n", s)
    return html.unescape(re.sub(r"<[^>]+>", " ", s))


def strip_wiki(s):
    """Plain text of a wikitext fragment (links -> labels, refs/templates/markup removed)."""
    s = re.sub(r"(?s)<ref[^>/]*/>|<ref[^>]*>.*?</ref>|<!--.*?-->", "", s)
    s = re.sub(r"\{\{(?:sortname|PersonZelle|SortKey)\|([^|}]*)\|([^|}]*)[^}]*\}\}", r"\1 \2", s, flags=re.I)
    s = re.sub(r"\{\{(?:nowrap|small)\|([^}]*)\}\}", r"\1", s, flags=re.I)
    for _ in range(3):
        s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = re.sub(r"\[\[(?:File|Datei|Image):[^\]]*\]\]", "", s)
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\[https?://\S+ ([^\]]*)\]", r"\1", s)
    s = re.sub(r"'{2,}", "", s)
    return clean(re.sub(r"<[^>]+>", " ", s))


def wiki_people(fragment):
    """Names in a wikitext cell: link labels, sortname templates, or <br>/comma-separated text."""
    frag = re.sub(r"(?s)<ref[^>/]*/>|<ref[^>]*>.*?</ref>|<!--.*?-->", "", fragment)
    names = []
    for part in re.split(r"<br\s*/?>|\n", frag, flags=re.I):
        part = part.strip()
        if not part:
            continue
        links = re.findall(r"\{\{(?:sortname|PersonZelle)\|([^|}]*)\|([^|}]*)", part, flags=re.I)
        found = [f"{a} {b}" for a, b in links]
        found += [m.split("|")[-1] for m in re.findall(r"\[\[([^\]]+)\]\]", part)
                  if not re.match(r"(?i)(file|datei|image):", m)]
        if found:
            names += found
        else:
            names += [p for p in (strip_wiki(x) for x in part.split(",")) if p]
    return [clean(n) for n in names if clean(n) and clean(n) not in ("—", "-", "–")]


def split_cells(line, sep):
    """Split a wikitable line on `sep` outside [[...]] and {{...}}."""
    out, depth, buf, i = [], 0, "", 0
    while i < len(line):
        two = line[i:i + 2]
        if two in ("[[", "{{"):
            depth += 1
            buf += two
            i += 2
            continue
        if two in ("]]", "}}"):
            depth = max(0, depth - 1)
            buf += two
            i += 2
            continue
        if depth == 0 and line.startswith(sep, i):
            out.append(buf)
            buf = ""
            i += len(sep)
            continue
        buf += line[i]
        i += 1
    out.append(buf)
    return out


def wikitables(text):
    """[[row cells...], ...] per wikitable; header rows dropped, cell attributes removed."""
    tables = []
    for m in re.finditer(r"(?ms)^\{\|.*?^\|\}", text):
        rows, cur = [], None
        for line in m.group(0).split("\n")[1:]:
            if line.startswith("|-") or line.startswith("|}"):
                if cur:
                    rows.append(cur)
                cur = []
                continue
            if line.startswith("!") or line.startswith("|+"):
                cur = None
                continue
            if cur is None:
                continue
            if line.startswith("|"):
                for cell in split_cells(line[1:], "||"):
                    parts = split_cells(cell, "|")
                    if len(parts) > 1 and re.search(r"=|^\s*$", parts[0]) and "[[" not in parts[0]:
                        cell = "|".join(parts[1:])
                    cur.append(cell.strip())
            elif cur:
                cur[-1] += "\n" + line
        if cur:
            rows.append(cur)
        tables.append([r for r in rows if r])
    return tables


def year_in(s):
    m = re.search(r"\b(19[5-9]\d|20[0-3]\d)\b", strip_wiki(s))
    return m.group(1) if m else ""


# ---------------------------------------------------------------- 1. Kunstkompass

def kunstkompass():
    url = "https://de.wikipedia.org/wiki/Kunstkompass?action=raw"
    text = wiki_raw("Kunstkompass", "de")
    rows = []
    for m in re.finditer(r"(?ms)^=== Kunstkompass ([^=]+?) ===\n(.*?)(?=^==)", text):
        years = re.findall(r"\d{4}", m.group(1))
        edition = years[0] if len(years) == 1 else f"{years[0]}-{years[-1]}"
        body = m.group(2)
        for table in wikitables(body):
            for cells in table:
                if len(cells) < 2 or not re.fullmatch(r"\d+", strip_wiki(cells[0])):
                    continue
                names = wiki_people(cells[1])
                country = strip_wiki(cells[3]) if len(cells) >= 5 else (strip_wiki(cells[2]) if len(cells) == 4 else "")
                for n in names:
                    rows.append(row("kunstkompass", edition, n, rank=strip_wiki(cells[0]), country=country,
                                    is_artist=1, role="ranked", src=url))
        # "Auf den weiteren Plätzen folgten 6. [[Anselm Kiefer]], 7. ..."
        for rk, name in re.findall(r"\b(\d{1,3})\. \[\[([^\]]+)\]\]", body):
            rows.append(row("kunstkompass", edition, name.split("|")[-1], rank=rk, is_artist=1, role="ranked", src=url))
    return rows


# ---------------------------------------------------------------- 2. ArtReview Power 100

ARTREVIEW_SEED = "/artist/ibrahim-mahama/"


def artreview_power100(editions):
    """Walk each edition's prev/next chain of artist pages (Gatsby page-data JSON)."""
    editions = {str(e) for e in editions}
    seen, queue = set(), collections.deque([ARTREVIEW_SEED])
    entries = {}  # (edition, place) -> (title, category, path)
    while queue:
        path = queue.popleft()
        if path in seen:
            continue
        seen.add(path)
        url = f"https://artreview.com/page-data{path}page-data.json"
        try:
            data = json.loads(fetch(url))
        except (urllib.error.HTTPError, ValueError) as e:
            print(f"  artreview: {path}: {e}", file=sys.stderr)
            continue
        a = data["result"]["data"].get("wordpressWpArtist") or {}
        cat = (a.get("artist_category") or {}).get("name", "")
        for e in (a.get("acf") or {}).get("artist_power_100") or []:
            ed = (e.get("edition") or {}).get("name")
            if ed not in editions:
                continue
            entries[(ed, e.get("place"))] = (a.get("title", ""), cat, path)
            for nb in (e.get("prev"), e.get("next")):
                if nb and nb.get("path") and nb["path"] not in seen:
                    queue.append(nb["path"])
        if len(seen) % 50 == 0:
            print(f"  artreview: {len(seen)} pages, {len(entries)} entries", flush=True)
    rows = []
    for (ed, place), (title, cat, path) in sorted(entries.items(), key=lambda kv: (kv[0][0], kv[0][1] or 0)):
        rows.append(row("artreview_power100", ed, title, rank=place or "",
                        is_artist=1 if cat.startswith("Artist") else 0, role="ranked", note=cat,
                        src=f"https://artreview.com{path}"))
    return rows


# ---------------------------------------------------------------- 3. Artprice

ARTPRICE_PDF = "https://imgpublic.artprice.com/pdf/the-contemporary-art-market-report-{year}.pdf"
ARTPRICE_ROW = re.compile(
    r"(?<![\d,$.])(\d{1,3}) ([^\d\s$()](?:(?!Turnover|artprice|Rank |record)[^$()])+?) \(([^)]*)\)\s*([^$\d]*?)\s*\$\s?[\d,]+")


def artprice(years):
    try:
        import pypdf
    except ImportError:
        print("  artprice: pypdf not installed (pip install pypdf); skipped", file=sys.stderr)
        return []
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    rows = []
    for year in years:
        url = ARTPRICE_PDF.format(year=year)
        try:
            fetch(url, binary=True)
        except (urllib.error.HTTPError, Blocked) as e:
            print(f"  artprice {year}: {e}", file=sys.stderr)
            continue
        reader = pypdf.PdfReader(cache_path(url))
        tables, cur, expect = [], [], 1
        for page in reader.pages:
            text = page.extract_text() or ""
            if not re.search(r"Artist[^\n]{0,40}Turnover", text):  # ranking-table pages only
                continue
            for m in ARTPRICE_ROW.finditer(re.sub(r"\s*\n\s*", " ", text)):
                rk = int(m.group(1))
                if rk == 1 and cur:
                    tables.append(cur)
                    cur = []
                if rk != (cur[-1][0] + 1 if cur else 1):
                    continue
                cur.append((rk, m.group(2), m.group(3), m.group(4)))
        if cur:
            tables.append(cur)
        for t in tables:
            # 2026 has no ultra-contemporary Top 100, only a Top 10 of auction debuts (artists under 40)
            lst = ("artprice_top500" if len(t) >= 400 else "artprice_ultra100" if len(t) >= 90
                   else f"artprice_ultra_debuts_top{len(t)}")
            for rk, name, dates, country in t:
                b = re.search(r"(\d{4})", dates)
                rows.append(row(lst, year, name, rank=rk, country=country, birth=b.group(1) if b else "",
                                is_artist=1, role="ranked", note=f"({dates})", src=url))
        print(f"  artprice {year}: tables of {[len(t) for t in tables]}")
    return rows


# ---------------------------------------------------------------- 4. Biennials

VENICE_LISTS = {  # edition -> static list page ("N. SURNAME, First" + "b. YEAR Country, ...")
    "2015": "https://www.labiennale.org/en/art/2015/biennale-arte-2015-artisti",
    "2017": "https://www.labiennale.org/en/art/2017/artists",
}
VENICE_VIEWS = {  # edition -> paginated participant views (title + "YEAR, Country")
    "2019": ["https://www.labiennale.org/en/art/2019/artists"],
    "2022": ["https://www.labiennale.org/en/art/2022/milk-dreams"],
    "2024": ["https://www.labiennale.org/en/art/2024/nucleo-contemporaneo",
             "https://www.labiennale.org/en/art/2024/portraits",
             "https://www.labiennale.org/en/art/2024/abstractions",
             "https://www.labiennale.org/en/art/2024/italians-everywhere"],
}
VENICE_NEWS = {  # edition -> news page listing "Name, born YEAR, Place. Lives in ..."
    "2026": "https://www.labiennale.org/en/news/biennale-arte-2026-invited-artists",
}


def _bio(text):
    """(birth_year, country) from 'b. 1971 Palestine, lives ...' / '1985, Jordan' / 'born 1983, Manila, Philippines'."""
    m = re.search(r"(?:b\.|born|founded)?\s*(\d{4})(?:\s*[-–]\s*(?:d\.\s*)?\d{4})?,?\s*([^,.;\n]*)", text)
    if not m:
        return "", ""
    return m.group(1), m.group(2).strip()


def venice():
    rows = []
    for ed, url in VENICE_LISTS.items():
        text = strip_html(fetch(url))
        for m in re.finditer(r"(?m)^\s*(\d{1,3})\.\s+(.+?)\s*(?:>>>)?\s*\n\s*(.*)", text):
            raw = clean(m.group(2))
            surname, _, first = raw.partition(", ")
            name = f"{first} {surname.title() if surname.isupper() else surname}" if first else raw
            b, c = _bio(m.group(3))
            rows.append(row("venice_biennale", ed, name, rank="", country=c, birth=b, is_artist=1,
                            role="participant", note=f"listed as {raw}", src=url))
    for ed, sections in VENICE_VIEWS.items():
        for base in sections:
            page, last = 0, 0
            while page <= last:
                url = base if page == 0 else f"{base}?page={page}"
                try:
                    h = fetch(url)
                except urllib.error.HTTPError as e:
                    print(f"  venice {url}: {e}", file=sys.stderr)
                    break
                pages = [int(p) for p in re.findall(r"[?&]page=(\d+)", h)]
                last = max([last] + pages)
                for m in re.finditer(r'(?s)class="lb-item-title">(.*?)</div>\s*(?:<div class="lb-excerpt">(.*?)</div>)?', h):
                    b, c = _bio(strip_html(m.group(2) or ""))
                    rows.append(row("venice_biennale", ed, strip_html(m.group(1)), country=c, birth=b,
                                    is_artist=1, role="participant", note=base.rsplit("/", 1)[-1], src=url))
                page += 1
    for ed, url in VENICE_NEWS.items():
        text = strip_html(fetch(url))
        for m in re.finditer(r"(?m)^\s*([^\n,]{2,80}?)\s*,\s*(?:born|b\.|founded|established)\s+(\d{4})([^\n]*)", text):
            place = [p.strip() for p in m.group(3).split(".")[0].split(",") if p.strip()]
            rows.append(row("venice_biennale", ed, m.group(1), birth=m.group(2),
                            country=place[-1] if place else "", is_artist=1, role="participant", src=url))
    return dedupe(rows)


def documenta():
    rows = []
    for title, ed in (("Documenta_14", "documenta 14 (2017)"), ("Documenta_fifteen", "documenta fifteen (2022)")):
        url = f"https://en.wikipedia.org/wiki/{title}?action=raw"
        text = wiki_raw(title)
        for sec in re.finditer(r"(?ms)^==\s*(Participants|Deceased[^=]*)\s*==\n(.*?)(?=^==[^=])", text):
            deceased = sec.group(1).startswith("Deceased")
            for line in re.findall(r"(?m)^\*\s*(.+)$", sec.group(2)):
                line = re.sub(r"^'''[^']*'''\s*", "", line)
                line = re.sub(r"(?s)<ref[^>/]*/>|<ref[^>]*>.*?</ref>", "", line)
                for item in split_cells(line, ","):
                    dates = re.search(r"\(([^)]*\d{4}[^)]*)\)", item)
                    b = re.search(r"(\d{4})", dates.group(1)) if dates else None
                    links = [m.split("|")[-1] for m in re.findall(r"\[\[([^\]]+)\]\]", item)]
                    for n in links or [strip_wiki(re.sub(r"\([^)]*\)", "", item))]:
                        if clean(n):
                            rows.append(row("documenta", ed, n, birth=b.group(1) if b else "",
                                            role="participant", note="deceased" if deceased else "", src=url))
    return dedupe(rows)


# e-flux participant announcements: (list, edition, url, mode, start marker, end marker).
# mode "sep": the list is text separated by commas, semicolons or line breaks (bold runs,
# e.g. curator headings, are dropped); mode "bold": each participant is a <strong> run.
EFLUX = [
    ("sharjah_biennial", "SB14 (2019)", "https://www.e-flux.com/announcements/210307/sharjah-biennial-14leaving-the-echo-chamber",
     "bold", "The complete selection of participating artists", "Media contact"),
    ("sharjah_biennial", "SB15 (2023)", "https://www.e-flux.com/announcements/459583/sharjah-biennial-15-participating-artists",
     "sep", "participating artists</strong>", "</p>"),
    ("sharjah_biennial", "SB17 (2027)", "https://www.e-flux.com/announcements/6787370/sharjah-biennial-17-framework-and-participants",
     "sep", "List of participants", "About the curators"),
    ("istanbul_biennial", "18th (2025-2027), first leg", "https://www.e-flux.com/announcements/6784139/18th-istanbul-biennialthe-three-legged-cat",
     "bold", "Participating artists in the first leg of the biennial<br></strong>", "list of participants in the public program"),
    ("kochi_muziris_biennale", "6th (2025)", "https://www.e-flux.com/announcements/6784510/participating-artists",
     "sep", "Participating artists of the Sixth Edition of Kochi-Muziris Biennale", "</p>"),
    ("gwangju_biennale", "15th (2024)", "https://www.e-flux.com/announcements/595141/artist-list-for-15th-edition",
     "sep", "Participating artists:</strong>", "</p>"),
    ("gwangju_biennale", "16th (2026)", "https://www.e-flux.com/announcements/6787431/16th-gwangju-biennaleyou-must-change-your-life",
     "sep", "Participating artists", "</p>"),
    ("sharjah_biennial", "SB16 (2025)", "https://www.e-flux.com/announcements/627545/sharjah-biennial-16-to-carry",
     "sep", "List of participants </strong>", "*Participants presenting"),
    ("sao_paulo_bienal", "36th (2025)", "https://www.e-flux.com/announcements/672979/36th-bienal-de-sao-paulonot-all-travellers-walk-roads-of-humanity-as-practice",
     "sep", "The participating artists for the 36th Bienal de São Paulo are:", "Another five participants"),
    # not e-flux: the Fundação Bienal's own full-cast announcement, one name per line
    ("sao_paulo_bienal", "35th (2023)", "https://bienal.org.br/?p=66713",
     "lines", "<b>Full List</b>", "The names followed by *"),
    # Dak'Art 15 (2024) international exhibition, from AfricansColumn's transcription of the
    # official announcement (biennaledakar.org has no static artist list); one <li> per artist
    ("dakart", "15th (2024)", "https://africanscolumn.com/dakart-2024-unveils-theme-artist-lineup-and-curators-for-15th-african-contemporary-art-biennale/",
     "li", "The full list of participating artists includes", "</ol>"),
]


def eflux_body(h):
    i = h.find('class="article__body"')
    if i < 0:
        return ""
    ends = [k for k in (h.find('class="announcement__logo', i), h.find('class="article__bottom-buttons', i)) if k > 0]
    return h[i:min(ends) if ends else i + 200000]


def split_outside_parens(text, seps=",;"):
    out, depth, buf = [], 0, ""
    for ch in text:
        depth += ch == "("
        depth -= ch == ")" and depth > 0
        if ch in seps and depth == 0:
            out.append(buf)
            buf = ""
        else:
            buf += ch
    return out + [buf]


def eflux_names(body, mode, start, end):
    if start:
        k = body.find(start)
        body = body[k + len(start):] if k >= 0 else ""
    if end and end in body:
        body = body[:body.index(end)]
    if mode == "li":
        items = [strip_html(x) for x in re.findall(r"(?s)<li[^>]*>(.*?)</li>", body)]
    elif mode == "lines":  # one participant per line; collaborations kept whole
        items = strip_html(body).split("\n")
    elif mode == "bold":
        body = re.sub(r"</(strong|b)>(?:\s|&nbsp;)*<\1>", " ", body)
        runs = [strip_html(r) for r in re.findall(r"(?s)<(?:strong|b)>(.*?)</(?:strong|b)>", body)]
        items = [x for r in runs if not re.search(r"(?i)curated by|:", r) for x in split_outside_parens(r)]
    else:
        body = re.sub(r"(?s)<strong>.*?</strong>", "\n", body)
        items = [x for line in strip_html(body).split("\n") for x in split_outside_parens(line)]
    out = []
    for x in items:
        x = clean(re.sub(r"^\s*and\s+", "", clean(x))).rstrip(".* ")
        if 1 < len(x) <= 90 and not x.startswith("<") and len(x.split()) <= 12 and not re.search(r"(?i)\b(born|lives|the biennial)\b", x):
            out.append(x)
    return out


def eflux():
    rows = []
    for lst, ed, url, mode, start, end in EFLUX:
        try:
            h = fetch(url)
            body = eflux_body(h) if "e-flux.com" in url else h
        except (urllib.error.URLError, Blocked) as e:
            print(f"  e-flux {lst} {ed}: {e}", file=sys.stderr)
            continue
        for n in eflux_names(body, mode, start, end):
            rows.append(row(lst, ed, n, role="participant", src=url))
    return dedupe(rows)


# ---------------------------------------------------------------- 5. Prizes (Wikipedia)

def prize_turner():
    title = "List_of_Turner_Prize_winners_and_nominees"
    url, rows = f"https://en.wikipedia.org/wiki/{title}?action=raw", []
    for table in wikitables(wiki_raw(title)):
        for c in table:
            if len(c) < 4 or not year_in(c[0]):
                continue
            y = year_in(c[0])
            if "cancel" in c[1].lower():
                for n in wiki_people(re.sub(r"(?i)'''bursaries''':?", "", c[2])):
                    rows.append(row("prize_turner", y, n, is_artist=1, role="bursary", src=url))
                continue
            for n in wiki_people(c[1]):
                rows.append(row("prize_turner", y, n, is_artist=1, role="winner", src=url))
            for n in wiki_people(c[3]):
                rows.append(row("prize_turner", y, n, is_artist=1, role="nominee", src=url))
    return rows


def prize_hugo_boss():
    title = "Hugo_Boss_Prize"
    url, rows = f"https://en.wikipedia.org/wiki/{title}?action=raw", []
    text = wiki_raw(title)
    for m in re.finditer(r"(?ms)^'''(\d{4})'''\s*\n(.*?)(?=^'''\d{4}'''|^==)", text):
        y, body = m.groups()
        lines = body.strip().split("\n")
        first = lines[0] if lines else ""
        winners = [x.split("|")[-1] for x in re.findall(r"\[\[([^\]]+)\]\]", first)][:2]
        for n in winners[:1] if "and" not in strip_wiki(first).split(" won")[0] else winners:
            rows.append(row("prize_hugo_boss", y, n, is_artist=1, role="winner", src=url))
        for line in lines[1:]:
            if line.startswith("*"):
                country = re.search(r"\(([^)]*)\)\s*$", strip_wiki(line))
                for n in wiki_people(re.sub(r"\([^)]*\)\s*$", "", line.lstrip("* "))):
                    rows.append(row("prize_hugo_boss", y, n, country=country.group(1) if country else "",
                                    is_artist=1, role="nominee", src=url))
    return dedupe(rows)


def prize_praemium():
    title = "Praemium_Imperiale"
    url, rows = f"https://en.wikipedia.org/wiki/{title}?action=raw", []
    for table in wikitables(wiki_raw(title)):
        for c in table:
            if len(c) >= 3 and year_in(c[0]):
                for col, field in ((1, "painting"), (2, "sculpture")):
                    for n in wiki_people(c[col]):
                        if n.lower() not in ("and",):
                            rows.append(row("prize_praemium_imperiale", year_in(c[0]), re.sub(r"^and ", "", n),
                                            is_artist=1, role="laureate", note=field, src=url))
    return rows


def prize_duchamp():
    title = "Marcel_Duchamp_Prize"
    url, rows = f"https://en.wikipedia.org/wiki/{title}?action=raw", []
    for table in wikitables(wiki_raw(title)):
        for c in table:
            if len(c) >= 2 and year_in(c[0]):
                for n in wiki_people(c[1]):
                    rows.append(row("prize_marcel_duchamp", year_in(c[0]), n, is_artist=1, role="winner", src=url))
                for n in wiki_people(c[2]) if len(c) > 2 else []:
                    rows.append(row("prize_marcel_duchamp", year_in(c[0]), n, is_artist=1, role="nominee", src=url))
    return rows


def prize_venice_lions():
    title = "List_of_Venice_Biennale_exhibitions"
    url, rows = f"https://en.wikipedia.org/wiki/{title}?action=raw", []
    for table in wikitables(wiki_raw(title)):
        for c in table:
            if len(c) < 5:
                continue
            y = year_in(c[1])
            for award, names in re.findall(r"(?m)^\*\s*([^:\n]+):\s*(.+)$", c[4]):
                a = award.lower()
                if "pavilion" in a or "participation" in a or "national" in a:
                    names = re.sub(r"\[\[[^\]]*(?:pavilion|Pavilion)[^\]]*\]\]", "", names)
                    names = names.split(" with ", 1)[1] if " with " in names else ""
                role = ("golden_lion_best_artist" if "golden" in a and "artist" in a else
                        "golden_lion_lifetime" if "lifetime" in a else
                        "golden_lion_national" if "golden" in a and "national" in a else
                        "silver_lion" if "silver" in a else "other")
                for n in wiki_people(names.replace(" and ", ", ")):
                    if not re.search(r"(?i)pavilion|''", n):
                        rows.append(row("prize_venice_lions", y, n, is_artist=1, role=role, note=strip_wiki(award),
                                        src=url))
    return [r for r in rows if r["edition"] and int(r["edition"]) >= 1960]


def prize_future_generation():
    title = "Future_Generation_Art_Prize"
    url, rows = f"https://en.wikipedia.org/wiki/{title}?action=raw", []
    for y, body in re.findall(r"(?m)^\*\s*(\d{4}):\s*(.+)$", wiki_raw(title)):
        body = re.sub(r"(?s)<ref[^>]*>.*?</ref>|<ref[^>]*/>", "", body)
        parts = re.split(r"([A-Z][A-Za-z']*(?: [A-Za-z']+)*? (?:Prize|Award)):", body)
        for label, names in zip(parts[1::2], parts[2::2]):
            names = names.strip().rstrip(".")
            role = "winner" if label.startswith("Main") else "special_prize" if "Special" in label else "other"
            for n in wiki_people(names.replace(" and ", ", ")):
                rows.append(row("prize_future_generation", y, n, is_artist=1, role=role, note=label, src=url))
    return rows


ARTIST_WORDS = re.compile(r"(?i)\b(artist|painter|sculpt|photograph|visual|installation|video art|printmak|"
                          r"illustrat|cartoon|ceramic|textile|calligraph|performance art)")


def prize_prince_claus():
    title = "Prince_Claus_Fund"
    url, rows = f"https://en.wikipedia.org/wiki/{title}?action=raw", []
    text = wiki_raw(title)
    for m in re.finditer(r"(?ms)^==\s*The (\d{4}) Prince Claus Awards\s*==\n(.*?)(?=^==[^=])", text):
        y, body = m.groups()
        lau = re.search(r"(?ms)^===\s*Laureates\s*===.*?\n(.*?)(?=^===|\Z)", body)
        for line in re.findall(r"(?m)^\*\s*(.+)$", lau.group(1) if lau else ""):
            plain = strip_wiki(line)
            name = re.split(r"\s*\(", plain, 1)[0]
            first_link = re.match(r"\s*(?:The\s+)?\[\[([^\]]+)\]\]", line)
            if first_link:
                name = first_link.group(1).split("|")[-1]
            parens = [p for p in re.findall(r"\(([^)]*)\)", plain) if "Principal Award" not in p]
            country, _, field = (parens[0] if parens else "").partition(", ")
            desc = "; ".join(x for x in (field, plain.rsplit(")", 1)[1].strip(" ,.") if ")" in plain else "") if x)
            rows.append(row("prize_prince_claus", y, name, country=country,
                            is_artist=1 if ARTIST_WORDS.search(desc) else 0,
                            role="principal_award" if "Principal Award" in plain else "laureate",
                            note=desc, src=url))
    return rows


JAMEEL_PAGES = {  # V&A article per edition (English Wikipedia has no Jameel Prize article)
    "2009": "jameel-prize-2009", "2011": "jameel-prize-2011", "2013": "jameel-prize-3",
    "2016": "jameel-prize-4", "2018": "jameel-prize-5",
}


def prize_jameel():
    rows = []
    for ed, slug in JAMEEL_PAGES.items():
        url = f"https://www.vam.ac.uk/articles/{slug}"
        try:
            text = strip_html(fetch(url))
        except (urllib.error.HTTPError, Blocked) as e:
            print(f"  jameel {ed}: {e}", file=sys.stderr)
            continue
        for w in re.findall(r"([^\n]+?) – WINNERS? OF THE JAMEEL PRIZE", text):
            rows.append(row("prize_jameel", ed, w.strip().title() if w.strip().isupper() else w, is_artist=1,
                            role="winner", note="name upper-cased at source", src=url))
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        k = next((i for i, l in enumerate(lines) if "SHORTLIST" in l.upper() and len(l) < 80), None)
        if k is None:
            continue
        # each shortlisted name is a heading followed by a paragraph that starts with the name
        for i in range(k + 1, len(lines) - 1):
            if len(lines[i].split()) <= 7 and lines[i + 1].startswith(lines[i]) and lines[i] != lines[i + 1]:
                rows.append(row("prize_jameel", ed, lines[i], is_artist=1, role="shortlisted", src=url))
    return dedupe(rows)


PRIZES = [prize_jameel, prize_turner, prize_hugo_boss, prize_praemium, prize_duchamp, prize_venice_lions,
          prize_future_generation, prize_prince_claus]


# ---------------------------------------------------------------- main

def dedupe(rows):
    seen, out = set(), []
    for r in rows:
        k = (r["list"], r["edition"], r["name"].lower(), r["role"])
        if r["name"] and k not in seen:
            seen.add(k)
            out.append(r)
    return out


SOURCES = ["kunstkompass", "artreview", "artprice", "venice", "documenta", "eflux", "prizes"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+", choices=SOURCES, help="run only these sources (rows of the "
                    "other sources, and of any source that fails, are kept from the existing output file)")
    ap.add_argument("--power100-editions", nargs="+", default=[str(y) for y in range(2019, 2026)])
    ap.add_argument("--artprice-years", nargs="+", default=["2023", "2024", "2025", "2026"])
    args = ap.parse_args()
    run = args.only or SOURCES
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    kept = []
    if os.path.exists(OUT_PATH):
        with open(OUT_PATH, encoding="utf-8") as f:
            kept = list(csv.DictReader(f))
    groups = {
        "kunstkompass": lambda: kunstkompass(),
        "artreview": lambda: artreview_power100(args.power100_editions),
        "artprice": lambda: artprice(args.artprice_years),
        "venice": venice,
        "documenta": documenta,
        "eflux": eflux,
        "prizes": lambda: [r for p in PRIZES for r in p()],
    }
    prefixes = {"kunstkompass": ("kunstkompass",), "artreview": ("artreview",), "artprice": ("artprice",),
                "venice": ("venice_biennale",), "documenta": ("documenta",),
                "eflux": tuple({e[0] for e in EFLUX}), "prizes": ("prize_",)}
    def write(rows):
        with open(OUT_PATH + ".part", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
        os.replace(OUT_PATH + ".part", OUT_PATH)

    rows, failed = [], []
    for src in run:
        print(f"{src} ...", flush=True)
        try:
            got = groups[src]()
        except Exception as e:  # one broken source must not lose the others; its old rows are kept
            print(f"  {src} failed: {type(e).__name__}: {e}", file=sys.stderr)
            failed.append(src)
            continue
        rows += got
        kept = [r for r in kept if not r["list"].startswith(prefixes[src])]
        print(f"  {len(got)} rows")
        write(kept + rows)  # checkpoint after every source
    rows = kept + rows
    write(rows)
    if failed:
        print(f"failed sources (re-run with --only {' '.join(failed)}): {failed}", file=sys.stderr)

    counts = collections.defaultdict(lambda: [0, set()])
    for r in rows:
        c = counts[r["list"]]
        c[0] += 1
        c[1].add(r["edition"])
    print(f"\n{'list':28} {'rows':>6}  editions")
    for lst in sorted(counts):
        n, eds = counts[lst]
        print(f"{lst:28} {n:6}  {', '.join(sorted(eds))}")
    artists = {norm(r["name"]) for r in rows if r["is_artist"] != "0" and r["is_artist"] != 0}
    print(f"\n{len(rows)} rows; {len({norm(r['name']) for r in rows})} distinct names; "
          f"{len(artists)} distinct names not flagged as non-artists")
    print(f"wrote {OUT_PATH}")


def norm(name):
    import unicodedata
    s = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s).split())


if __name__ == "__main__":
    main()
