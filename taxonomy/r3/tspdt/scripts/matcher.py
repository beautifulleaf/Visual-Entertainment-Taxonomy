"""Title/year -> tconst matcher over the repo's interim film tables."""
import csv, re, unicodedata

ROOT = "/home/user/Visual-Entertainment-Taxonomy/data/interim/"
ARTS = r"the|a|an|le|la|les|l'|il|lo|i|gli|der|die|das|el|los|las|un|une|o|os|as|de|het|een|den|det|ett|en|ein|eine"
INV = re.compile(r"^(.*), (The|A|An|Le|La|Les|L'|Il|Lo|I|Gli|Der|Die|Das|El|Los|Las|Un|Une|O|Os|As|De|Het|Een|Den|Det|Ett|En|Ein|Eine)$")


def uninvert(t):
    t = t.strip()
    m = INV.match(t)
    if m:
        return m.group(2) + ("" if m.group(2).endswith("'") else " ") + m.group(1)
    # "Title, The (Alt)" style
    m = re.match(r"^(.*), (The|A|An|Le|La|Les|L'|Il|El|Der|Die|Das) (\(.*\))$", t)
    if m:
        return f"{m.group(2)} {m.group(1)} {m.group(3)}"
    return t


SPELL = {"colour": "color", "colours": "colors", "neighbour": "neighbor", "neighbours": "neighbors",
         "blvd": "boulevard", "honour": "honor", "favour": "favor", "behaviour": "behavior",
         "theatre": "theater", "centre": "center", "labour": "labor", "harbour": "harbor",
         "armour": "armor", "splendour": "splendor", "splendours": "splendors", "humour": "humor",
         "rumour": "rumor", "valour": "valor", "vapour": "vapor", "glamour": "glamor", "odour": "odor",
         "ii": "2", "iii": "3", "iv": "4", "vi": "6", "two": "2", "one": "1", "three": "3",
         "mr": "mister", "dr": "doctor", "st": "saint", "vs": "versus", "grey": "gray"}


def norm(t):
    t = unicodedata.normalize("NFKD", t or "")
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    t = t.replace("&", " and ").replace("æ", "ae").replace("ø", "o").replace("ß", "ss").replace("œ", "oe")
    t = re.sub(rf"^({ARTS})\s+", "", t) if not t.startswith("l'") else t[2:]
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    t = re.sub(rf"^({ARTS.replace(chr(39), '')})\s+", "", t)
    t = " ".join(SPELL.get(w, w) for w in t.split())
    return t


def variants(title):
    title = re.sub(r"\s*\[[^\]]*\]\s*$", "", title.strip())
    t = uninvert(title)
    out = [t, title]
    m = re.match(r"^(.*?)\s*\((.+)\)$", t)  # "Title (Alt title)" or "(aka ...)"
    if m:
        out += [m.group(1), re.sub(r"^(aka|a\.k\.a\.)\s+", "", m.group(2), flags=re.I)]
    for s in list(out):
        if ":" in s:
            out.append(s.split(":")[0])
        if " / " in s:
            out += s.split(" / ")
    seen, res = set(), []
    for s in out:
        n = norm(uninvert(s.strip()))
        if n and n not in seen:
            seen.add(n); res.append(n)
    return res


def _int(x):
    try:
        return int(float(x))
    except Exception:
        return 0


TYPE_OK = {"movie", "tvMovie", "video", "short", "tvSpecial", "tvMiniSeries", "tvShort", "tvSeries", "tvEpisode", ""}


class Matcher:
    def __init__(self):
        self.tiers = [{}, {}]  # tier0: candidates+extra; tier1: ratings
        def add(tier, title, year, tconst, votes, prefix=False):
            y = _int(year)
            n = norm(title)
            if prefix:
                n = "\x00" + n
            if not n or not y or not tconst:
                return
            self.tiers[tier].setdefault((n, y), {})
            d = self.tiers[tier][(n, y)]
            d[tconst] = max(d.get(tconst, 0), votes)
            if ":" in title and not prefix:
                add(tier, title.split(":")[0], year, tconst, votes, prefix=True)
        for r in csv.DictReader(open(ROOT + "film_candidates.csv", encoding="utf-8")):
            v = _int(r["imdb_votes"])
            add(0, r["title"], r["year"], r["tconst"], v)
            add(0, r["original_title"], r["year"], r["tconst"], v)
        for r in csv.DictReader(open(ROOT + "film_candidates_extra.csv", encoding="utf-8")):
            add(0, r["mdblist_title"], r["year"], r["tconst"], _int(r["imdb_votes"]))
        for r in csv.DictReader(open(ROOT + "film_ratings.csv", encoding="utf-8")):
            add(1, r["mdblist_title"], r["year"], r["tconst"], _int(r["imdb_votes"]))
        self.cache = {}

    def match(self, title, year):
        m = re.match(r"\s*(\d{4})", str(year or ""))
        y = int(m.group(1)) if m else 0
        if not y or not title:
            return "", "none"
        key = (title, y)
        if key in self.cache:
            return self.cache[key]
        vs = variants(title)
        res = ("", "none")
        for tier in (0, 1):
            idx = self.tiers[tier]
            # exact: primary normalised form, same year
            found = None
            for i, n in enumerate(vs):
                for dy in (0, 1, -1):
                    d = idx.get((n, y + dy))
                    if d:
                        found = (max(d, key=d.get), "exact" if (i == 0 and dy == 0) else "fuzzy")
                        break
                if found:
                    break
            if not found:  # source title equals the part before a colon in the IMDb title
                for n in vs:
                    for dy in (0, 1, -1):
                        d = idx.get(("\x00" + n, y + dy))
                        if d:
                            found = (max(d, key=d.get), "fuzzy")
                            break
                    if found:
                        break
            if found:
                res = found
                break
        self.cache[key] = res
        return res
