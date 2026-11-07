"""Parse cached TSPDT pages/spreadsheets into lists.csv + entries.csv (writes incrementally)."""
import csv, html, os, re, sys, collections
import openpyxl, xlrd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matcher import Matcher, uninvert

RAW = sys.argv[1]
OUT = sys.argv[2]
BASE = "https://theyshootpictures.com/"
M = Matcher()

EF = ["list_id", "rank", "title", "year", "director", "country", "tconst", "match",
      "genre", "colour", "mins", "tconst_source"]
ef = open(os.path.join(OUT, "entries.csv"), "w", newline="", encoding="utf-8")
ew = csv.DictWriter(ef, EF)
ew.writeheader()
LISTS = []


def raw(p):
    return open(os.path.join(RAW, p.replace("/", "_")), encoding="utf-8", errors="replace").read()


def clean(s):
    s = html.unescape(re.sub(r"<[^>]+>", "", str(s if s is not None else ""))).replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip()


def num(v):
    if v is None or v == "":
        return ""
    try:
        f = float(v)
        return str(int(f)) if f == int(f) else str(f)
    except Exception:
        return str(v).strip()


def director_fmt(d):
    d = clean(d)
    if "," in d and "/" not in d and "&" not in d and d.count(",") == 1:
        last, first = d.split(",", 1)
        return f"{first.strip()} {last.strip()}"
    return d


def tt_of(v):
    m = re.search(r"(tt\d{6,})", str(v or ""))
    return m.group(1) if m else ""


def add_list(list_id, title, kind, url, rows, notes=""):
    n = 0
    for r in rows:
        r = dict(r)
        r["list_id"] = list_id
        r["title"] = uninvert(re.sub(r"\s*\[\d{4}\]$", "", clean(r.get("title", ""))))
        r["year"] = clean(r.get("year", "")).replace(".0", "")
        tt = r.get("tconst", "")
        if tt:
            r["match"] = "exact"
            r["tconst_source"] = "source_imdb_link"
        else:
            tt, m = M.match(r["title"], r["year"])
            if m == "none" and r.get("alt"):
                for a in r["alt"]:
                    tt, m = M.match(a, r["year"])
                    if m != "none":
                        m = "fuzzy"
                        break
            r["tconst"], r["match"] = tt, m
            r["tconst_source"] = "title_year" if tt else ""
        r.pop("alt", None)
        ew.writerow({k: r.get(k, "") for k in EF})
        n += 1
    ef.flush()
    LISTS.append(dict(list_id=list_id, list_title=title, kind=kind, url=BASE + url if not url.startswith("http") else url,
                      n_entries=n, notes=notes))
    print(list_id, n, flush=True)


def html_table(page):
    t = raw(page)
    t = t[t.find("<tbody"):]
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S):
        c = [clean(x) for x in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(c) >= 7:
            yield c


def xls_rows(fname):
    s = xlrd.open_workbook(os.path.join(RAW, fname)).sheet_by_index(0)
    h = [num(x) for x in s.row_values(0)]
    for i in range(1, s.nrows):
        yield dict(zip(h, s.row_values(i)))


def key(title, year):
    return (clean(title).lower(), num(year)[:4])


# ---------- 1. starting lists + top-1000s (HTML tables enriched from the site's XLS) ----------
JOIN = collections.Counter()


def ranked_table(list_id, title, page, xls, rankcol, notes):
    extra = {}
    if xls:
        for r in xls_rows(xls):
            pos = num(r.get(rankcol, ""))
            k = pos if pos and pos != "0" else None
            d = dict(genre=clean(r.get("Genre", "")), colour=clean(r.get("Colour", r.get("Col", ""))),
                     country=clean(r.get("Country", "")), k=key(r.get("Title", ""), r.get("Year", "")))
            if k:
                extra[("p", k)] = d
            extra[key(r.get("Title", ""), r.get("Year", ""))] = d
    rows = []
    for c in html_table(page):
        pos, prev, t, d, y, country, mins = c[:7]
        e = extra.get(("p", pos))
        if not e or e["k"][0] != key(t, y)[0]:
            e = extra.get(key(t, y)) or {}
        JOIN[list_id] += bool(e)
        rows.append(dict(rank=pos, title=t, year=y, director=director_fmt(d),
                         country=e.get("country") or country, mins=mins,
                         genre=e.get("genre", ""), colour=e.get("colour", ""),
                         alt=[re.sub(r"\s*\[[^\]]*\]$", "", t)]))
    add_list(list_id, title, "canon", page, rows, notes)


ranked_table("tspdt_starting_list", "Greatest Films Starting List (all films ranked, 2026 edition)",
             "gf1000_startinglist_table2.php", "resources_StartingList.xls", "2026",
             "Full table (gf1000_startinglist_table.php links to _table2.php, one server-rendered page); genre/colour/full country joined from resources/StartingList.xls")
ranked_table("tspdt_21st_starting_list", "21st Century Starting List (all films ranked, 2026 edition)",
             "21stcentury_startinglist_table2.php", "resources_StartingList_21stCentury.xls", "2026",
             "Full table (21stcentury_startinglist_table.php links to _table2.php); genre/colour/full country from resources/StartingList_21stCentury.xls")
ranked_table("tspdt_1000", "The 1,000 Greatest Films (2026 edition)", "gf1000_all1000films_table.php",
             "resources_1000GreatestFilms.xls", "Pos", "genre/colour from resources/1000GreatestFilms.xls")
ranked_table("tspdt_21st_century_1000", "The 21st Century's 1,000 Most Acclaimed Films (2026 edition)",
             "21stcentury_allfilms_table.php", "resources_21stCenturyFilms.xls", "Pos",
             "genre/colour from resources/21stCenturyFilms.xls")


# ---------- 2. Ex-1000 pages: "TITLE (Director, Year) ranks... (current)" ----------
def ex_page(list_id, title, page, notes):
    t = raw(page)
    t = re.sub(r"<br\s*/?>", "\n", t)
    rows = []
    for line in clean_lines(t):
        m = re.match(r"^(.+?) \(([^()]*), (\d{4})(?:-\d+)?\)\s+((?:\d+ - )+\d+)\s*\((\d+)\)", line)
        if m:
            rows.append(dict(title=titlecase(m.group(1)), year=m.group(3), director=m.group(2),
                             notes=m.group(5)))
    add_list(list_id, title, "other", page, rows, notes)


def clean_lines(t):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</li>|</tr>|</div>", "\n", t)
    return [x for x in (clean(l) for l in html.unescape(re.sub(r"<[^>]+>", "", t)).split("\n")) if x]


SMALL = {"a", "an", "the", "of", "in", "and", "on", "at", "to", "for", "by", "or", "de", "la", "le", "du", "des", "et", "from", "with"}


def titlecase(s):
    words = s.lower().split(" ")
    out = []
    for i, w in enumerate(words):
        if i and w in SMALL:
            out.append(w)
        else:
            out.append(re.sub(r"^([^a-zà-ÿ]*)([a-zà-ÿ])", lambda m: m.group(1) + m.group(2).upper(), w))
    return " ".join(out)


ex_page("tspdt_gf_ex1000", "Ex-1,000 Greatest Films (former place-getters)", "gf1000_all1000films_ex1000.htm",
        "Unranked: films in earlier editions of the 1,000 GF but not the current one")
ex_page("tspdt_21st_ex1000", "21st Century Ex-1,000 (former place-getters)", "21stcentury_extop1000.htm",
        "Unranked: films in earlier 21st-century editions but not the current one")


# ---------- 3. Noir (xlsx has the 1,000 noir films + the 'more noir(ish)' films) ----------
wb = openpyxl.load_workbook(os.path.join(RAW, "resources_Noir-Films.xlsx"))
ws = wb.worksheets[0]
noir, more = [], []
for i, row in enumerate(ws.iter_rows()):
    if i == 0:
        continue
    v = [c.value for c in row]
    if not v[2]:
        continue
    link = row[10].hyperlink.target if row[10].hyperlink else ""
    alts = [clean(x) for x in (v[8], v[9]) if x]
    r = dict(title=v[2], year=num(v[3]), director=director_fmt(v[1]), mins=num(v[4]), colour=clean(v[5]),
             country=clean(v[6]), genre=clean(v[7]), tconst=tt_of(link), alt=[uninvert(a) for a in alts])
    (noir if v[0] == "Yes" else more).append(r)
add_list("tspdt_noir1000", "1,000 Noir Films", "genre", "noir1000.htm", noir,
         "Unranked; from resources/Noir-Films.xlsx (Noir1000=Yes); same films as noir1000a-z / by title/director/year/country pages")
add_list("tspdt_more_noir", "More Noir(ish) Films", "genre", "morenoir.htm", more,
         "Unranked; from resources/Noir-Films.xlsx (Noir1000 blank); page says 842 films")


# ---------- 4. TSPDT polls (xlsx) ----------
def xlsx_iter(fname, sheet=0):
    wb = openpyxl.load_workbook(os.path.join(RAW, fname), read_only=True)
    ws = wb.worksheets[sheet] if isinstance(sheet, int) else wb[sheet]
    it = ws.iter_rows(values_only=True)
    h = [str(x).strip() if x is not None else "" for x in next(it)]
    for r in it:
        yield dict(zip(h, r))


rows = []
for r in xlsx_iter("resources_2026_tspdt_poll_all_films.xlsx", 0):
    if not r.get("Title"):
        continue
    rows.append(dict(rank=num(r["Ranking"]), title=r["Title"], year=num(r["Year"]), director=director_fmt(r["Director"]),
                     country=clean(r["Country"]), genre=clean(r["Genre"]), colour=clean(r["Col"]), mins=num(r["Length"]),
                     tconst=tt_of(r.get("IMDbtt"))))
add_list("tspdt_poll_2026", "The 2026 TSPDT Poll (readers' favourite films, all films receiving votes)", "poll",
         "2026poll.htm", rows, "From resources/2026_tspdt_poll_all_films.xlsx sheet '2026 poll'; pages 2026poll_top250 / _998-251 show the top 998")
rows = []
for r in xlsx_iter("resources_TSPDT-2021-Poll---All-Films.xlsx", 0):
    if not r.get("Title"):
        continue
    rows.append(dict(rank=num(r["Rkg"]), title=r["Title"], year=num(r["Year"]), director=director_fmt(r["Director"]),
                     country=clean(r["Country"]), genre=clean(r["Genre"]).strip("-"), colour=clean(r["Colour"]).strip("-"),
                     mins=num(r["Length"])))
rows.sort(key=lambda r: int(r["rank"] or 99999))
add_list("tspdt_poll_2021", "2021 TSPDT Poll: 1,005 Film Favourites (all films receiving votes)", "poll", "2021poll.htm",
         rows, "From resources/TSPDT-2021-Poll---All-Films.xlsx; ranks tie")


# ---------- 5. Beyond the Sight & Sound Canon ----------
def bss(sheet, list_id, title, url, notes, fname="resources_BtheSSCanon_Master-List.xlsx"):
    rows = []
    for r in xlsx_iter(fname, sheet):
        if not r.get("Title"):
            continue
        eng = clean(r.get("English Title", ""))
        rows.append(dict(rank="", title=eng or r["Title"], year=num(r["Year"]), director=clean(r.get("Directors", "")),
                         country=clean(r.get("Country", "")), tconst=tt_of(r.get("URL IMDb") or r.get("URL")),
                         genre="", alt=[clean(r["Title"])]))
    add_list(list_id, title, "poll", url, rows, notes)


bss("A-List", "bss_a_list", "Beyond the Sight & Sound Canon: The A-List (1,030 films)", "beyondtheSScanon_A-List.htm",
    "Films with >=3 critics' votes and none in S&S 2022; from resources/BtheSSCanon_Master-List.xlsx")
bss("B-List", "bss_b_list", "Beyond the Sight & Sound Canon: B-List (2022 releases)", "beyondtheSScanon.htm",
    "From resources/BtheSSCanon_Master-List.xlsx sheet B-List")
bss("2+ Votes", "bss_2plus_votes", "Beyond the Sight & Sound Canon: films with 2 votes", "beyondtheSScanon.htm",
    "From resources/BtheSSCanon_Master-List.xlsx sheet '2+ Votes'")
bss("Orphans", "bss_orphans", "Beyond the Sight & Sound Canon: orphans (single-vote films)", "beyondtheSScanon.htm",
    "From resources/BtheSSCanon_Master-List.xlsx sheet Orphans")

# critics' ballots from the 16 HTML pages
CRIT_PAGES = ["A", "B", "C", "D", "E-F", "G", "H", "I-K", "L", "M", "N-O", "P-Q", "R", "S", "T-V", "W-Z"]
used = collections.Counter()
for letter in CRIT_PAGES:
    page = f"beyondtheSScanon_critics{letter}.htm"
    t = raw(page)
    start = t.find("were removed from ballots")
    t = t[start if start > 0 else 0:]
    names = [(m.start(), clean(m.group(1))) for m in re.finditer(
        r'class="fontStack[^"]*">\s*<div[^>]*><div[^>]*class=\'stacks_in text_stack\'>(.*?)</div>', t, re.S)]
    roles = {}
    for m in re.finditer(r"<span[^>]*font-weight:bold;[^>]*><em>(.*?)</em></span>", t, re.S):
        roles[m.start()] = clean(m.group(1))
    films = [(m.start(), clean(m.group(1)), m.group(2)) for m in re.finditer(
        r'<span[^>]*>([^<>]+\(\d{4}[^<>]*\))</span>(?:<span[^>]*>\s*</span>)?(?:<span[^>]*><u><a href="https?://www\.imdb\.com/title/(tt\d+)/?[^"]*")?', t)]
    for i, (pos, name) in enumerate(names):
        end = names[i + 1][0] if i + 1 < len(names) else len(t)
        role = next((v for k, v in sorted(roles.items()) if pos < k < end), "")
        rows = []
        for fp, txt, tt in films:
            if not (pos < fp < end):
                continue
            m = re.match(r"^(.*) \((\d{4})[^,]*,\s*(.*)\)$", txt)
            if not m:
                continue
            rows.append(dict(title=m.group(1), year=m.group(2), director=m.group(3), tconst=tt or ""))
        if not rows:
            continue
        slug = re.sub(r"[^a-z0-9]+", "_", html.unescape(name).lower()).strip("_")
        import unicodedata
        slug = unicodedata.normalize("NFKD", slug).encode("ascii", "ignore").decode() or "critic"
        used[slug] += 1
        if used[slug] > 1:
            slug += f"_{used[slug]}"
        add_list(f"bss_ballot_{slug}", f"Beyond the S&S Canon ballot: {name}", "critic", page, rows,
                 f"{role}; chronological, unranked")


# ---------- 6. TSPDT Recommendations ----------
t = raw("tspdtrecommendations.htm")
rows = []
for m in re.finditer(r'<span[^>]*>([^<>]+?\(([^()<>]*?), (\d{4})[^()<>]*?\))</span>', t):
    txt = clean(m.group(1))
    mm = re.match(r"^(.*) \((.*), (\d{4})(?:-\d+)?(?:, \d+m)?\)$", txt)
    if not mm:
        continue
    seg = t[m.end():m.end() + 1500]
    seg = seg[:seg.find("<br")] if "<br" in seg else seg
    rows.append(dict(title=titlecase(re.sub(r"\s*\[[^\]]*\]$", "", mm.group(1))), year=mm.group(3),
                     director=mm.group(2), tconst=tt_of(re.search(r'imdb\.com/title/(tt\d+)', seg).group(1)) if re.search(r'imdb\.com/title/(tt\d+)', seg) else ""))
add_list("tspdt_recommendations", "TSPDT's Film Recommendations", "other", "tspdtrecommendations.htm", rows,
         "Unranked, alphabetical; IMDb links on page")

# ---------- 7. pages with no film entries / views ----------
NOFILM = [
    ("tspdt_gf_top250_directors", "The 1,000 Greatest Films: Top 250 Directors", "director", "gf1000_top250directors.htm",
     "Ranks directors only (with counts of films); no film titles listed"),
    ("tspdt_21st_top100_directors", "21st Century: Top 100 Directors", "director", "21stcentury_top100directors.htm",
     "Ranks directors only; no film titles listed"),
    ("tspdt_noir_key_directors", "50 Key Noir Directors", "director", "50keynoirdirectors.htm", "50 directors; no film titles"),
    ("tspdt_director_filmographies", "Director pages: Selected Filmography (2,325 pages in sitemap.xml)", "director", "directors.htm",
     "Not fetched: filmographies load by script from a Google Sheet (direct sheet download was refused by the session's permission policy); static HTML holds no film list"),
    ("tspdt_gf1000_all_selections", "1,000 Greatest Films: all critics' selections (153,893 rows)", "critic", "resources/1000GFAllSelectionsCritics.xlsx",
     "Not expanded: per-critic citations restricted to films already in tspdt_1000"),
    ("tspdt_listed_by", "Listed By (Rosenbaum / Scorsese ballots)", "other", "listedby.htm", "Names ballots only; films flagged only on director pages"),
]
for lid, title, kind, url, note in NOFILM:
    LISTS.append(dict(list_id=lid, list_title=title, kind=kind, url=BASE + url, n_entries=0, notes=note))
VIEWS = {
    "tspdt_1000": ["gf1000.htm", "gf1000_alpha.htm", "gf1000_rank1-1000.htm", "gf1000_rank1000-1.htm", "gf1000_year.htm",
                   "gf1000_all1000films.htm", "gf1000_all1000films_rankinghistory.htm", "gf1000_all1000films_alternativetitles.htm"],
    "tspdt_21st_century_1000": ["21stcentury.htm", "21stcentury_films1000-251.htm", "21stcentury_t250_alpha.htm",
                                "21stcentury_t250_250-1.htm", "21stcentury_t250_rank1-250.htm", "21stcentury_t250_year.htm",
                                "21stcentury_rankinghistory.htm", "21stcentury_alternativetitles.htm"],
    "tspdt_starting_list": ["gf1000_startinglist_table.php"],
    "tspdt_21st_starting_list": ["21stcentury_startinglist_table.php"],
    "tspdt_noir1000": ["noir1000%s.htm" % c for c in "abcdefghijklmnopqrstuvwyz"] + ["noir1000title.htm", "noir1000director.htm",
                       "noir1000year.htm", "noir1000country.htm", "noir1000updates.htm"],
    "tspdt_poll_2026": ["2026poll_top250.htm", "2026poll_998-251.htm", "polls.htm"],
    "bss_a_list": ["beyondtheSScanon.htm"],
}
for lid, pages in VIEWS.items():
    for p in pages:
        LISTS.append(dict(list_id=f"view:{p.rsplit('.', 1)[0]}", list_title=f"view/alias of {lid}", kind="other",
                          url=BASE + p, n_entries=0, notes=f"Same films as {lid}; not duplicated in entries.csv"))

with open(os.path.join(OUT, "lists.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, ["list_id", "list_title", "kind", "url", "n_entries", "notes"])
    w.writeheader()
    w.writerows(LISTS)
ef.close()
print("xls joins", dict(JOIN))
