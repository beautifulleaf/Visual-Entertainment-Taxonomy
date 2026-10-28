"""East Asian regional sweep (visual-art-plan.md §2, §2A, §2.1 point 4, §2.2).

East Asia has two attribution profiles (§2.1 point 4): painting is largely
artist-led (literati painting, ukiyo-e, Rinpa, Joseon true-view and genre
painting), while ceramics, bronzes, lacquer, jade and Buddhist sculpture are
tradition-led. This script harvests collections that record East Asia's own
categories (dynasty or era, object type, national designation) so the
classifying stage gets evidence at the level each tradition records, and so the
attribution profile can be measured instead of assumed.

Sources (all keyless; every request cached under data/raw/regional/east_asia/,
spaced ~1 s apart; re-runs read the cache, so an interrupted run resumes):
  ColBase (colbase/opendata.tsv)
      The open-data TSV of Japan's national museums (Tokyo, Kyoto, Nara and
      Kyushu National Museums, Nabunken, Tobunken, the Imperial Collections):
      ~155k records with 時代世紀 (era/century), 分類 and 種別 (object type),
      作者 (maker, with role suffix 筆 / 作 / 模 ...) plus an English Artist
      field ("By Utagawa Hiroshige (1797–1858)") and 文化財指定 (国宝,
      重要文化財, 重要美術品). The file is read from disk; download it from the
      ColBase open-data page if it is missing.
  Japan's designated properties (bunka/)
      国指定文化財等データベース (kunishitei.bunka.go.jp), the Agency for Cultural
      Affairs database behind Japan Cultural Heritage Online (bunka.nii.ac.jp,
      now online.bunka.go.jp, whose 国宝・重要文化財 list links to it).
      Every 国宝 and 重要文化財 in the fine-arts-and-crafts register (美術工芸品),
      via its CSV export. The export fails above ~2,000 rows, so queries are
      split by art category x 国宝/重要文化財, and by era when still too large.
      Makers come from the 〈…筆／…〉 part of the official name.
  National Palace Museum, Taipei (npm/)
      The open-data portal (digitalarchive.npm.gov.tw/opendata): the whole
      catalogue listed by dynasty x category (~108k objects). Listings give
      only the title, so painting / calligraphy / fan makers are parsed from
      the title convention "dynasty + maker + title" (明沈周廬山高 軸), using a
      lexicon of known names (Cleveland, ColBase) and a frequency rule for the
      rest; "明人", "宋人" etc. mean anonymous. Detail pages are fetched for one
      object per parsed maker (--npm-details, most frequent first) to get the
      museum's own romanisation.
  Korea e-Museum (emuseum/)
      emuseum.go.kr, the National Museum of Korea's union catalogue. Its Open
      API needs a data.go.kr key, so the public search pages are used instead:
      (a) every Korean 국보 (National Treasure) and 보물 (Treasure) object, with
      its detail page (국적/시대, 분류, 재질, 국가지정유산); (b) the National Museum
      of Korea's painting and calligraphy (서화), listed per period facet, with
      makers parsed from titles ("김홍도 필 …", "전 정선 필 …"); (c) facet counts
      of the National Museum of Korea's whole collection by period x material,
      used only as all-objects context in the traditions table.
  Cleveland Museum of Art open-access API (cma/)
      Departments Chinese, Japanese and Korean Art: culture carries the dynasty
      ("China, Ming dynasty (1368–1644)"); creators carry original-script names
      and life dates.
  Art Institute of Chicago dump (data/raw/museums/aic/..., on disk, optional)
      Objects whose place of origin is China, Japan or Korea; period from the
      date text and style terms; original-script names from artist_display.

Normalisation:
  period    the recorded dynasty/era string is kept as is (period_original) and
            mapped to an English period (PERIODS), using the object's country to
            choose between homographs (南北朝, 三国, 新石器).
  type      every source's own classification is mapped to one medium axis
            (painting, prints, calligraphy, sculpture, ceramics, metalwork, jade,
            lacquer, textiles, ...; see TYPE_* tables). The source category is
            kept in object_subtype.
  maker     original script plus romanisation; attribution is one of named,
            attributed_to (伝 / 전 / "Attributed to"), copy (模本, excluded from the
            attribution share), workshop (kilns such as 景徳鎮窯) or unattributed.
            Makers are merged across sources on a variant-folded original-script
            key (黃/黄, 徵/徴, 圓山應擧/円山応挙), then on romanisation when life
            dates agree.

Outputs (data/interim/regional/):
  east_asia_objects.csv     one row per object (all sources)
  east_asia_artists.csv     one row per maker: original + romanised name, life
                            dates, country, periods, object counts per source,
                            designated-property counts (Japan 国宝 / 重要文化財 from
                            the national register, Korea 국보 / 보물 from e-Museum,
                            ColBase's own designations separately); the seed
                            for an East Asian reference list
  east_asia_traditions.csv  country x period x object type: unattributed and
                            workshop objects per source, all objects, the
                            attributed share, designated unattributed objects,
                            top kilns/workshops and examples

Usage: python3 pipelines/regional/east_asia.py [--skip bunka,npm,emuseum,cma,aic]
           [--npm-details 400] [--korea-details 2000] [--delay 1.0] [--offline]
"""
import argparse
import collections
import csv
import glob
import html
import http.client
import http.cookiejar
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

csv.field_size_limit(1 << 24)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw", "regional", "east_asia")
OUT_DIR = os.path.join(ROOT, "data", "interim", "regional")
AIC_DIR = os.path.join(ROOT, "data", "raw", "museums", "aic", "artic-api-data", "json", "artworks")
COLBASE_TSV = os.path.join(RAW, "colbase", "opendata.tsv")
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"
BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VisualEntertainmentTaxonomy/0.1"

EAST = {"Japan", "China", "Korea", "Taiwan"}
OFFLINE = [False]
UNREACHABLE = collections.Counter()

# --------------------------------------------------------------------- fetching


class Fetcher:
    """Rate-limited HTTP client with cookies and retries. Never caches by itself."""

    def __init__(self, delay, ua=UA, name=""):
        self.delay, self.ua, self.name, self.last = delay, ua, name, 0.0
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
        self.requests = 0
        self.failures = 0

    def request(self, url, data=None, headers=None, tries=4, timeout=120):
        if OFFLINE[0]:
            return None
        for attempt in range(tries):
            wait = self.delay - (time.time() - self.last)
            if wait > 0:
                time.sleep(wait)
            self.last = time.time()
            h = {"User-Agent": self.ua}
            h.update(headers or {})
            if isinstance(data, str):
                data = data.encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=h)
            self.requests += 1
            try:
                with self.opener.open(req, timeout=timeout) as r:
                    return r.read()
            except urllib.error.HTTPError as e:
                print(f"  [{self.name}] HTTP {e.code} {url[:140]} (try {attempt + 1})", file=sys.stderr)
                if e.code in (400, 401, 403, 404, 410):
                    break
            except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException,
                    OSError) as e:
                print(f"  [{self.name}] {type(e).__name__}: {e} {url[:140]} (try {attempt + 1})",
                      file=sys.stderr)
            time.sleep(min(60, 5 * (attempt + 1)))
        self.failures += 1
        UNREACHABLE[self.name] += 1
        return None


def cached(path, produce):
    """JSON cache: return the stored value, or produce() and store it unless None."""
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            os.remove(path)
    value = produce()
    if value is None:
        return None
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".part", "w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(path + ".part", path)
    return value


def strip_tags(s):
    s = re.sub(r"<br\s*/?>", " ", s or "")
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))).strip()


def safe(s):
    return re.sub(r"[^\w.-]+", "_", s).strip("_")[:80]


# ------------------------------------------------------------------- name keys

# Traditional / shinjitai / simplified variants seen in East Asian maker names.
# Applied to matching keys only; the recorded spelling is kept for display.
VARIANTS = dict(zip(
    "黃徵齊齋澤濱邊廣國圖畫學寶藝顏錢壽樂榮惠雙應舉擧圓澀濟讀嚴禪傳淸歷恆眞靑爲與吳賴嶋嶌邨僊晉祿禮鐵豐薰臺灣萬寫實盡單戰黑點燈鷗曉龜龍螢鄕德佛來兩參從縣變關陽陰會豔岡髙﨑",
    "黄徴斉斎沢浜辺広国図画学宝芸顔銭寿楽栄恵双応挙挙円渋済読厳禅伝清歴恒真青為与呉頼島島村仙晋禄礼鉄豊薫台湾万写実尽単戦黒点灯鴎暁亀竜蛍郷徳仏来両参従県変関陽陰会艶岡高崎"))
NAME_ALIASES_F = {}
SIMPLIFIED = dict(zip("黄徴赵孟頫沈周董其昌王恽寿平郑燮刘陈张杨吴钱龚邹罗蓝马冯", "黄徴趙孟頫沈周董其昌王惲壽平鄭燮劉陳張楊呉銭龔鄒羅藍馬馮"))


# Same person under a longer art name in one source and the short one elsewhere.
NAME_ALIASES = {"雪舟等楊": "雪舟", "安藤広重": "歌川広重", "一立斎広重": "歌川広重", "雪村周継": "雪村", "天章周文": "周文",
                "可翁仁賀": "可翁", "大巧如拙": "如拙", "池野大雅": "池大雅", "谷口蕪村": "与謝蕪村", "画狂老人卍": "葛飾北斎",
                "応挙": "円山応挙", "牧谿法常": "牧谿", "梁楷": "梁楷"}


def fold_cjk(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"[\s・･.,、，'\"「」『』（）()〈〉<>\[\]]", "", s)
    return "".join(VARIANTS.get(SIMPLIFIED.get(ch, ch), SIMPLIFIED.get(ch, ch)) for ch in s)


def fold_rom(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("ou", "o").replace("uu", "u").replace("oo", "o")  # Hokusai / Kōrin spellings
    return re.sub(r"[^a-z]", "", s)


NAME_ALIASES_F.update({fold_cjk(k): fold_cjk(v) for k, v in NAME_ALIASES.items()})
CJK = re.compile(r"[぀-ヿ㐀-鿿豈-﫿가-힯]")


def has_cjk(s):
    return bool(CJK.search(s or ""))


DATES = re.compile(r"(?:(?:possibly|active|act\.|fl\.|c\.|ca\.|born|died)\s*)?(\d{3,4})(?:/\d{1,2})?\??\s*[-–—~～]\s*"
                   r"(?:(?:possibly|c\.|ca\.)\s*)?(\d{2,4})(?:/\d{1,2})?")


def life_dates(text):
    """'(1797–1858)', '1831 - 89', 'Japanese, 1760–1849' -> (1797, 1858). Active dates are skipped."""
    if not text:
        return None
    m = DATES.search(text)
    if not m:
        return None
    if re.search(r"\b(active|act\.|fl\.)\s*" + m.group(1), text):
        return None
    b, d = m.group(1), m.group(2)
    if len(d) < len(b):
        d = b[: len(b) - len(d)] + d
    b, d = int(b), int(d)
    if not (0 < b < d <= b + 110):
        return None
    return b, d


# ------------------------------------------------------------------- periods

# (english, country, begin, end, aliases). Latin aliases match whole words in
# lower case; CJK / Hangul aliases match as substrings. Homographs are listed
# under each country and resolved by the object's country.
PERIODS = [
    # Japan
    ("Paleolithic (Japan)", "Japan", -38000, -14000, ["旧石器", "先土器"]),
    ("Jōmon", "Japan", -10000, -300, ["縄文", "jomon", "jōmon"]),
    ("Yayoi", "Japan", -300, 250, ["弥生", "yayoi"]),
    ("Kofun", "Japan", 250, 592, ["古墳", "kofun"]),
    ("Asuka", "Japan", 592, 710, ["飛鳥", "白鳳", "asuka", "hakuho"]),
    ("Nara", "Japan", 710, 794, ["奈良", "nara"]),
    ("Heian", "Japan", 794, 1185, ["平安", "藤原", "heian"]),
    ("Kamakura", "Japan", 1185, 1333, ["鎌倉", "kamakura"]),
    ("Nanbokuchō", "Japan", 1336, 1392, ["南北朝", "nanbokucho", "nambokucho", "nanbokuchō"]),
    ("Muromachi", "Japan", 1336, 1573, ["室町", "muromachi"]),
    ("Momoyama", "Japan", 1573, 1615, ["安土桃山", "桃山", "momoyama", "azuchi"]),
    ("Edo", "Japan", 1615, 1868, ["江戸", "edo", "에도"]),
    ("Meiji", "Japan", 1868, 1912, ["明治", "meiji"]),
    ("Taishō", "Japan", 1912, 1926, ["大正", "taisho", "taishō"]),
    ("Shōwa", "Japan", 1926, 1989, ["昭和", "showa", "shōwa"]),
    ("Heisei", "Japan", 1989, 2019, ["平成", "heisei"]),
    ("Muromachi", "Japan", 1336, 1573, ["무로마치"]),
    ("Momoyama", "Japan", 1573, 1615, ["모모야마"]),
    ("Meiji–Shōwa (modern)", "Japan", 1868, 1989, ["근대"]),
    ("Ryukyu Kingdom", "Japan", 1429, 1879, ["尚氏", "琉球王国", "ryukyu kingdom"]),
    # China
    ("Neolithic", "China", -7000, -1600, ["新石器", "neolithic", "신석기"]),
    ("Shang", "China", -1600, -1046, ["商", "殷", "shang", "상"]),
    ("Western Zhou", "China", -1046, -771, ["西周", "western zhou", "서주"]),
    ("Eastern Zhou", "China", -770, -256, ["東周", "东周", "eastern zhou", "동주"]),
    ("Spring and Autumn", "China", -770, -476, ["春秋", "spring and autumn", "춘추"]),
    ("Warring States", "China", -475, -221, ["戰國", "戦国", "战国", "warring states", "전국"]),
    ("Qin", "China", -221, -206, ["秦", "qin dynasty", "진"]),
    ("Western Han", "China", -206, 9, ["西漢", "前漢", "西汉", "western han", "전한"]),
    ("Xin", "China", 9, 23, ["新莽", "新時代", "wang mang"]),
    ("Eastern Han", "China", 25, 220, ["東漢", "後漢", "东汉", "eastern han", "후한"]),
    ("Han", "China", -206, 220, ["漢", "汉", "han dynasty", "한대"]),
    ("Three Kingdoms (China)", "China", 220, 280, ["三國", "三国", "three kingdoms", "삼국"]),
    ("Six Dynasties", "China", 220, 589, ["六朝", "魏晉南北朝", "魏晋南北朝", "南北朝", "東晉", "西晉", "東晋", "西晋",
                                          "晉", "晋", "北魏", "東魏", "西魏", "北齊", "北斉", "北周", "南朝", "北朝", "五胡十六国",
                                          "six dynasties", "northern wei", "northern qi", "jin dynasty (265",
                                          "eastern jin", "western jin", "northern and southern"]),
    ("Sui", "China", 581, 618, ["隋", "sui dynasty", "수"]),
    ("Tang", "China", 618, 907, ["唐", "tang dynasty", "당"]),
    ("Five Dynasties", "China", 907, 960, ["五代", "five dynasties", "오대"]),
    ("Liao", "China", 907, 1125, ["遼", "辽", "liao", "요"]),
    ("Northern Song", "China", 960, 1127, ["北宋", "northern song", "북송"]),
    ("Southern Song", "China", 1127, 1279, ["南宋", "southern song", "남송"]),
    ("Song", "China", 960, 1279, ["宋", "song dynasty", "송"]),
    ("Jin", "China", 1115, 1234, ["金", "jin dynasty (1115", "jurchen", "금"]),
    ("Xi Xia", "China", 1038, 1227, ["西夏", "xixia", "xi xia"]),
    ("Yuan", "China", 1271, 1368, ["元", "yuan", "원"]),
    ("Ming", "China", 1368, 1644, ["明", "ming", "명"]),
    ("Qing", "China", 1644, 1911, ["清", "qing", "청"]),
    ("Republic", "China", 1912, 1949, ["民國", "民国", "中華民国", "republic period", "republican"]),
    ("People's Republic", "China", 1949, 2100, ["中華人民共和国", "people's republic", "1945년이후"]),
    ("Modern (China)", "China", 1840, 1949, ["근대"]),
    # Korea
    ("Paleolithic (Korea)", "Korea", -40000, -8000, ["구석기", "旧石器"]),
    ("Neolithic (Korea)", "Korea", -8000, -1500, ["신석기", "新石器", "neolithic"]),
    ("Bronze Age (Korea)", "Korea", -1500, -300, ["청동기", "青銅器時代", "bronze age"]),
    ("Early Iron Age (Korea)", "Korea", -300, -100, ["초기철기", "初期鉄器", "early iron age"]),
    ("Proto-Three Kingdoms", "Korea", -100, 300, ["원삼국", "原三国", "proto-three kingdoms"]),
    ("Lelang", "Korea", -108, 313, ["낙랑", "楽浪", "樂浪", "lelang", "nangnang"]),
    ("Goguryeo", "Korea", -37, 668, ["고구려", "高句麗", "goguryeo", "koguryo"]),
    ("Baekje", "Korea", -18, 660, ["백제", "百済", "百濟", "baekje", "paekche"]),
    ("Silla", "Korea", -57, 668, ["신라", "新羅", "silla"]),
    ("Gaya", "Korea", 42, 562, ["가야", "伽耶", "加耶", "伽倻", "gaya", "kaya"]),
    ("Three Kingdoms (Korea)", "Korea", -57, 668, ["삼국", "三国", "三國", "three kingdoms"]),
    ("Unified Silla", "Korea", 668, 935, ["통일신라", "統一新羅", "unified silla"]),
    ("Balhae", "Korea", 698, 926, ["발해", "渤海", "balhae", "parhae"]),
    ("Late Silla–Early Goryeo", "Korea", 880, 960, ["라말여초"]),
    ("Goryeo", "Korea", 918, 1392, ["고려", "高麗", "goryeo", "koryo", "goryo"]),
    ("Late Goryeo–Early Joseon", "Korea", 1350, 1450, ["려말선초"]),
    ("Joseon", "Korea", 1392, 1897, ["조선", "朝鮮", "李朝", "李氏朝鮮", "joseon", "choson", "chosŏn"]),
    ("Korean Empire", "Korea", 1897, 1910, ["대한제국", "大韓帝国", "korean empire"]),
    ("Japanese colonial period", "Korea", 1910, 1945, ["일제강점", "japanese colonial"]),
    ("Post-1945 (Korea)", "Korea", 1945, 2100, ["광복이후", "2000년 이후"]),
]
_PALIAS = []
for _i, (_en, _c, _b, _e, _al) in enumerate(PERIODS):
    for _a in _al:
        if has_cjk(_a):
            _PALIAS.append((_a, None, _i))
        else:
            _PALIAS.append((_a, re.compile(r"(?<![a-z])" + re.escape(_a) + r"(?![a-z])"), _i))
_COUNTRIES_OF = collections.defaultdict(set)
for _a, _, _i in _PALIAS:
    _COUNTRIES_OF[_a].add(PERIODS[_i][1])
_UNIQUE = [all(len(_COUNTRIES_OF[a]) == 1 for a in p[4]) for p in PERIODS]
# Single CJK characters that are also common in Japanese era names / words
# (元禄, 明暦, 金銅); they only count when nothing longer matched.
WEAK = {"元", "明", "金", "清", "宋", "唐", "商", "秦", "漢", "隋", "晉", "晋", "殷", "汉", "수", "당", "송", "원", "명",
        "청", "요", "금", "진", "상"}


def period_of(text, country=None):
    """Return the PERIODS index for a recorded period string, or None."""
    if not text:
        return None
    low = text.lower()
    hits = []
    for alias, rx, i in _PALIAS:
        if rx is None:
            if alias in ("수", "당", "송", "원", "명", "청", "요", "금", "진", "상", "한대", "전국", "전한", "후한", "삼국"):
                # Hangul single-syllable dynasty names: only as a whole label
                if text.strip() != alias:
                    continue
                pos = 0
            else:
                pos = text.find(alias)
        else:
            m = rx.search(low)
            pos = m.start() if m else -1
        if pos >= 0:
            hits.append((alias in WEAK, pos, -len(alias), i))
    if not hits:
        return None
    if not country:
        # vote with aliases that belong to one country only (三国時代(新羅) -> Korea)
        votes = collections.Counter(PERIODS[h[3]][1] for h in hits if _UNIQUE[h[3]])
        if len(votes) == 1:
            country = next(iter(votes))
    if country:
        same = [h for h in hits if PERIODS[h[3]][1] == country]
        if same:
            hits = same
        elif country in EAST:
            return None
    hits.sort()
    return hits[0][3]


def period_label(i):
    return PERIODS[i][0] if i is not None else ""


# ------------------------------------------------------------------ attribution

PLACEHOLDER = re.compile(r"不詳|不明|未詳|作者不|筆者不|佚名|無款|unknown|anonymous|unidentified|미상|작자미상|"
                         r"^(?:宋|元|明|清|唐|五代|宋元)人$", re.I)
NON_PERSON = re.compile(r"アイヌ|研究所|博物館|写真館|美術館|学校|製作所|商店|会社|協会|本舗|^中国|^朝鮮|^日本|^韓国|"
                        r"^台湾|^琉球|^沖縄|人形師|^Ｇ．|ware\b|kiln|workshop|studio", re.I)
WORKSHOP = re.compile(r"(窯|焼|工房|御用|官窯|伊万里|瀬戸|有田|鍋島|唐津|萩|楽家|座)$|窯|ware\b|kiln|workshop", re.I)
JP_ROLES = [("撮影", "photographer"), ("下絵", "designer"), ("原画", "designer"), ("図案", "designer"),
            ("筆", "painter"), ("画", "painter"), ("書", "calligrapher"), ("作", "maker"), ("造", "maker"),
            ("製", "maker"), ("刻", "carver"), ("彫", "carver"), ("模", "copyist"), ("摸", "copyist"),
            ("写", "copyist"), ("著", "author"), ("編", "author"), ("撰", "author"), ("訳", "author"),
            ("校", "author"), ("賛", "inscriber"), ("銘", "maker")]
CREATOR_ROLES = {"painter", "calligrapher", "maker", "carver", "designer", "photographer", "artist", ""}


def split_jp_maker(token):
    """'伝狩野元信筆' -> ('狩野元信', 'painter', True)."""
    t = re.sub(r"[（(〈][^）)〉]*[）)〉]", "", token).strip(" 　　「」『』")
    attributed = False
    if t.startswith("伝") and len(t) > 2:
        t, attributed = t[1:], True
    role = ""
    for suf, r in JP_ROLES:
        if t.endswith(suf) and len(t) > len(suf):
            t, role = t[: -len(suf)], r
            break
    t = t.strip(" 　　")
    return t, role, attributed


def jp_makers(raw):
    """ColBase 作者 -> list of (name, role, attributed). Placeholders give []."""
    out = []
    if not raw:
        return out
    for tok in re.split(r"[、，,;；/／　]|・(?=[^ァ-ヶー])", raw):
        tok = tok.strip()
        if not tok:
            continue
        name, role, attr = split_jp_maker(tok)
        name = name.strip("[]【】［］「」 ")
        if len(name) < 2 or PLACEHOLDER.search(name) or NON_PERSON.search(name) or WORKSHOP.search(name):
            continue
        if re.fullmatch(r"[\x00-\x7f\uff01-\uff5e]+", name) and (len(name) < 6 or "&" in name or " " not in name):
            continue   # photographic studios and fragments ("Cie", "AD．BRAUN")
        out.append((name, role, attr))
    return out


BUNKA_NOT_NAME = re.compile(r"(紙本|絹本|墨書|朱書|金字|銀字|墨画|著色|淡彩|刊本|写本|版本|自筆|宸筆|親筆|直筆|真筆|御筆|"
                            r"肉筆|年|所在|旧|附|並|共|各|屏風|曲|幅|巻|帖|冊|躯|口|面|枚|基|点|通|紙背)")


def bunka_makers(name):
    """Makers from an official register name: 紙本金地著色洛中洛外図〈狩野永徳筆／六曲屏風〉."""
    out = []
    for inner in re.findall(r"〈([^〉]*)〉", name or ""):
        for part in re.split(r"[／/]", inner):
            for tok in re.split(r"[\s　、]+", part.strip()):
                if not tok:
                    continue
                n, role, attr = split_jp_maker(tok)
                if role not in ("painter", "calligrapher", "maker", "carver") or len(n) < 2 or len(n) > 10:
                    continue
                if BUNKA_NOT_NAME.search(n) or PLACEHOLDER.search(n):
                    continue
                out.append((n, role, attr))
    return out


EN_PREFIX = re.compile(r"^(?:by|attributed to|painted by|calligraphy by|copied by|copy by|written by|made by|"
                       r"inscribed by|design(?:ed)? by|carved by|signed)\s+", re.I)


def en_names(raw):
    """ColBase English Artist -> list of (romanised, (birth, death) or None, attributed)."""
    out = []
    if not raw:
        return out
    for part in re.split(r";|\s+and\s+|,\s*(?=(?:by|attributed|painted|calligraphy)\b)", raw):
        part = part.strip()
        if not part:
            continue
        attributed = bool(re.match(r"attributed to", part, re.I))
        p = EN_PREFIX.sub("", part)
        dates = life_dates(p)
        p = re.sub(r"\([^)]*\)", "", p).strip(" ,.")
        if not p or PLACEHOLDER.search(p) or len(p) < 3:
            continue
        out.append((p, dates, attributed))
    return out


# ------------------------------------------------------------- Korean helpers

_RR_I = ["g", "kk", "n", "d", "tt", "r", "m", "b", "pp", "s", "ss", "", "j", "jj", "ch", "k", "t", "p", "h"]
_RR_M = ["a", "ae", "ya", "yae", "eo", "e", "yeo", "ye", "o", "wa", "wae", "oe", "yo", "u", "wo", "we", "wi",
         "yu", "eu", "ui", "i"]
_RR_F = ["", "k", "k", "k", "n", "n", "n", "t", "l", "k", "m", "l", "l", "l", "p", "l", "m", "p", "p", "t", "t",
         "ng", "t", "t", "k", "t", "p", "t"]
KO_SURNAME = {"김": "Kim", "이": "Yi", "박": "Park", "최": "Choe", "정": "Jeong", "강": "Kang", "조": "Jo",
              "윤": "Yun", "장": "Jang", "임": "Im", "한": "Han", "신": "Sin", "오": "O", "서": "Seo", "권": "Kwon",
              "황": "Hwang", "안": "An", "송": "Song", "류": "Yu", "유": "Yu", "홍": "Hong", "전": "Jeon", "고": "Go",
              "문": "Mun", "손": "Son", "양": "Yang", "배": "Bae", "백": "Baek", "허": "Heo", "남": "Nam",
              "심": "Sim", "노": "No", "하": "Ha", "곽": "Gwak", "성": "Seong", "차": "Cha", "주": "Ju", "구": "Gu",
              "민": "Min", "변": "Byeon", "채": "Chae", "엄": "Eom", "원": "Won", "천": "Cheon", "방": "Bang",
              "공": "Gong", "현": "Hyeon", "함": "Ham", "염": "Yeom", "여": "Yeo", "추": "Chu", "도": "Do",
              "석": "Seok", "설": "Seol", "마": "Ma", "길": "Gil", "위": "Wi", "표": "Pyo", "명": "Myeong",
              "기": "Gi", "반": "Ban", "왕": "Wang", "옥": "Ok", "육": "Yuk", "인": "In", "맹": "Maeng",
              "탁": "Tak", "국": "Guk", "어": "Eo", "은": "Eun", "편": "Pyeon", "경": "Gyeong", "봉": "Bong",
              "남궁": "Namgung", "황보": "Hwangbo", "제갈": "Jegal", "선우": "Seonu", "독고": "Dokgo"}


def rr_syllable(ch):
    code = ord(ch) - 0xAC00
    if not 0 <= code < 11172:
        return ch
    i, m, f = code // 588, (code % 588) // 28, code % 28
    return _RR_I[i] + _RR_M[m] + _RR_F[f]


def romanise_korean_name(name):
    """김홍도 -> Kim Hong-do; 정선 -> Jeong Seon (Revised Romanization, syllable by syllable)."""
    if not name or not re.fullmatch(r"[가-힣]{2,5}", name):
        return ""
    sur = name[:2] if name[:2] in KO_SURNAME and len(name) >= 4 else name[:1]
    given = name[len(sur):]
    s = KO_SURNAME.get(sur) or "".join(rr_syllable(c) for c in sur).capitalize()
    g = "-".join(rr_syllable(c) for c in given)
    return f"{s} {g[:1].upper()}{g[1:]}" if g else s


KO_MAKER = [
    re.compile(r"(?:^|[\s(])(전\s*)?(?:[가-힣]{1,3}\s+)?([가-힣]{2,4})\s*(?:필|筆)(?=$|[\s,(])"),
    re.compile(r"(?:^|[\s(])(전\s*)?(?:[가-힣]{1,3}\s+)?([가-힣]{2,4})\s+(?:글씨|그림|작)(?=$|[\s,(])"),
    re.compile(r"(?:^|[\s(])(전\s*)?([가-힣]{2,4})(?:이|가)\s*(?:그린|쓴)"),
]
KO_NOT_NAME = re.compile(r"미상|작자|필자|화원|도화서|일괄|무명|기타|각종|여러")


def korean_maker(title):
    for rx in KO_MAKER:
        m = rx.search(title or "")
        if m:
            name = m.group(2)
            if KO_NOT_NAME.search(name):
                return None
            return name, bool(m.group(1))
    return None


# ----------------------------------------------------------------- object type

TYPES = ["painting", "prints", "calligraphy", "sculpture", "ceramics", "metalwork", "jade", "lacquer", "textiles",
         "enamel", "carving", "fans", "rubbings", "arms and armour", "decorative arts", "archaeology",
         "books and manuscripts", "documents and historical materials", "photography", "coins", "stationery",
         "ethnographic", "architecture", "glass", "other"]

COLBASE_TYPE = {"絵画": "painting", "東洋絵画": "painting", "黒田記念館収蔵品": "painting", "印仏": "prints",
                "書跡": "calligraphy", "東洋書跡": "calligraphy", "彫刻": "sculpture", "東洋彫刻": "sculpture",
                "陶磁": "ceramics", "東洋陶磁": "ceramics", "金工": "metalwork", "東洋金工": "metalwork",
                "刀剣": "arms and armour", "漆工": "lacquer", "東洋漆工": "lacquer", "染織": "textiles",
                "東洋染織": "textiles", "考古": "archaeology", "東洋考古": "archaeology",
                "和書": "books and manuscripts", "漢籍": "books and manuscripts",
                "歴史資料": "documents and historical materials", "歴史": "documents and historical materials",
                "文書": "documents and historical materials", "荷札": "documents and historical materials",
                "付札": "documents and historical materials", "伝票": "documents and historical materials",
                "題籤": "documents and historical materials", "考課": "documents and historical materials",
                "習書･落書": "documents and historical materials", "文書･習書･落書": "documents and historical materials",
                "文書･習書": "documents and historical materials",
                "習書･落書･木製品": "documents and historical materials",
                "写真資料": "photography", "民族資料": "ethnographic", "東洋民族": "ethnographic",
                "工芸": "decorative arts", "建築": "architecture", "建物": "architecture", "木製品": "decorative arts",
                "将棋の駒": "decorative arts"}
SUBTYPE_HINTS = [("浮世絵", "prints"), ("版画", "prints"), ("絵画", "painting"), ("彫刻", "sculpture"),
                 ("書跡", "calligraphy"), ("陶磁", "ceramics"), ("金工", "metalwork"), ("漆工", "lacquer"),
                 ("染織", "textiles"), ("刀剣", "arms and armour"), ("甲冑", "arms and armour")]
BUNKA_TYPE = {"絵画": "painting", "彫刻": "sculpture", "書跡・典籍": "calligraphy",
              "古文書": "documents and historical materials", "考古資料": "archaeology",
              "歴史資料": "documents and historical materials"}
CRAFT_HINTS = [(r"太刀|刀|剣|甲|鎧|胴丸|腹巻|槍|薙刀|鉾|弓|矢|兜|大鎧|拵", "arms and armour"),
               (r"蒔絵|螺鈿|漆|彫漆|堆朱|沈金", "lacquer"),
               (r"陶|磁|焼|茶碗|壺|瓶|水指|茶入|香炉|青花|釉", "ceramics"),
               (r"織|繍|袈裟|小袖|裂|帛|染|装束|打敷|幡|錦|綾|羅|唐衣|胴服|帷子", "textiles"),
               (r"鏡|金銅|銅|鉄|鐘|梵鐘|錫|銀|金具|鰐口|華鬘|舎利|釜|鍍金|透彫", "metalwork")]
NPM_TYPE = {"銅器": "metalwork", "陶瓷器": "ceramics", "玉器": "jade", "琺瑯器": "enamel", "雕刻": "carving",
            "漆器": "lacquer", "錢幣": "coins", "文具": "stationery", "雜項": "other", "織品": "textiles",
            "絲繡": "textiles", "繪畫": "painting", "法書": "calligraphy", "法帖": "rubbings", "拓片": "rubbings",
            "成扇": "fans", "其他": "other"}
NPM_CATS = list(NPM_TYPE)
KO_MATERIAL_TYPE = {"금속": "metalwork", "토제": "ceramics", "도자기": "ceramics", "돌": "sculpture",
                    "석": "sculpture", "유리/보석": "glass", "나무": "decorative arts", "지": "painting",
                    "사직": "textiles", "골각패": "decorative arts", "칠": "lacquer", "피모": "textiles",
                    "초본": "decorative arts", "옥석": "jade", "합성수지": "other", "기타": "other"}
EN_TYPE = [(r"woodblock|print|surimono|nishiki-e", "prints"), (r"calligraph", "calligraphy"),
           (r"hanging scroll|handscroll|album|painting|screen|fan painting|scroll", "painting"),
           (r"\bfan\b", "fans"), (r"sculpt|figure|buddha|bodhisattva|statue", "sculpture"),
           (r"porcelain|stoneware|earthenware|ceramic|celadon|vessel|pottery|tea bowl|jar|vase", "ceramics"),
           (r"\bjade\b|nephrite", "jade"), (r"lacquer", "lacquer"),
           (r"textile|silk|costume|kesi|embroider|kimono|robe|fabric|woven", "textiles"),
           (r"cloisonn|enamel", "enamel"), (r"sword|armor|armour|arms|helmet|tsuba|blade", "arms and armour"),
           (r"bronze|metal|silver|gold|iron|mirror|jewel", "metalwork"),
           (r"netsuke|inro|ivory|carving|wood|bamboo|horn", "carving"), (r"photograph", "photography"),
           (r"glass", "glass"), (r"book|manuscript|sutra", "books and manuscripts"),
           (r"rubbing", "rubbings"), (r"coin", "coins"), (r"drawing|sketch", "painting")]


def en_type(*texts):
    t = " ".join(x for x in texts if x).lower()
    for rx, ty in EN_TYPE:
        if re.search(rx, t):
            return ty
    return "other"


def craft_type(title):
    for rx, ty in CRAFT_HINTS:
        if re.search(rx, title or ""):
            return ty
    return "decorative arts"


# ----------------------------------------------------------------- designation

DESIGNATION_EN = {"国宝": "National Treasure (Japan)", "重要文化財": "Important Cultural Property (Japan)",
                  "重要美術品": "Important Art Object (Japan, 1933–50 register)",
                  "국보": "National Treasure (Korea)", "보물": "Treasure (Korea)",
                  "국가민속문화유산": "National Folklore Cultural Heritage (Korea)"}

# ----------------------------------------------------------------- record shape

OBJ_FIELDS = ["source", "id", "title", "title_en", "country", "period_original", "period_en", "object_type",
              "object_subtype", "artist_original", "artist_romanised", "artist_role", "attribution",
              "artist_key", "designation", "designation_en", "date", "date_begin", "date_end", "holder", "url"]


def obj(**kw):
    o = {k: "" for k in OBJ_FIELDS}
    o.update({k: ("" if v is None else v) for k, v in kw.items()})
    if o["period_en"] == "" and isinstance(kw.get("_period_idx"), int):
        o["period_en"] = period_label(kw["_period_idx"])
    o.pop("_period_idx", None)
    o["_makers"] = kw.get("_makers", [])
    return o


def set_dates_from_period(o, pidx):
    if pidx is not None and not o["date_begin"]:
        o["date_begin"], o["date_end"] = PERIODS[pidx][2], PERIODS[pidx][3]


# ========================================================================= ColBase

COLBASE_INST = {"tnm": "Tokyo National Museum", "kyohaku": "Kyoto National Museum",
                "narahaku": "Nara National Museum", "kyuhaku": "Kyushu National Museum",
                "nabunken": "Nara National Research Institute for Cultural Properties",
                "tobunken": "Tokyo National Research Institute for Cultural Properties",
                "shozokan": "Museum of the Imperial Collections"}
PLACE_COUNTRY = [(r"台湾|taiwan", "Taiwan"), (r"中国|景徳鎮|china|chaina|chinese|龍泉|磁州|建窯|宜興|徳化|福建|浙江|江西|"
                                              r"河南|河北|陝西|山西|山東|四川|広東|江蘇|雲南|甘粛|内蒙古|遼寧|吉林|新疆", "China"),
                 (r"朝鮮|韓国|高麗|korea|百済|新羅|伽耶|加耶|楽浪|慶州|扶余", "Korea"),
                 (r"日本|japan|伊万里|有田|瀬戸|京都|東京|大阪|奈良|江戸|九州|北海道|沖縄|琉球|アイヌ|ainu|okinawa|"
                  r"薩摩|美濃|備前|信楽|丹波|越前|常滑|萩|唐津|九谷|鍋島|肥前|尾張|加賀|[都道府県]$", "Japan")]


FOREIGN = re.compile(r"タイ|インド|ベトナム|オランダ|アメリカ|イギリス|フランス|ドイツ|イタリア|スペイン|ポルトガル|エジプト|"
                     r"イラン|ペルシ|ギリシ|ローマ|カンボジア|ミャンマー|インドネシア|ジャワ|クメール|アフガ|パキスタン|ガンダーラ|"
                     r"ネパール|チベット|モンゴル|西アジア|ヨーロッパ|ムガル|阮朝|ラーンナー")


def place_country(place):
    if not place:
        return ""
    for rx, c in PLACE_COUNTRY:
        if re.search(rx, place, re.I):
            return c
    return "other"


def colbase_date(row, I, pidx):
    def num(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return None
    b, e = num(row[I["時代範囲開始"]]), num(row[I["時代範囲終了"]])
    if b is not None and abs(b) <= 21 and (e is None or abs(e) <= 21):   # centuries
        b = (b - 1) * 100 if b > 0 else b * 100
        e = e * 100 - 1 if e and e > 0 else (e * 100 + 99 if e else None)
    if b is None and pidx is not None:
        b, e = PERIODS[pidx][2], PERIODS[pidx][3]
    return b, e


def load_colbase():
    if not os.path.exists(COLBASE_TSV):
        print(f"ColBase: {COLBASE_TSV} missing; download the open-data TSV from colbase.nich.go.jp", file=sys.stderr)
        UNREACHABLE["colbase (file missing)"] += 1
        return []
    out = []
    dropped = collections.Counter()
    with open(COLBASE_TSV, encoding="utf-8", newline="") as f:
        r = csv.reader(f, delimiter="\t")
        h = next(r)
        I = {}
        for i, k in enumerate(h):
            I.setdefault(k, i)
        for row in r:
            if len(row) < len(h):
                row += [""] * (len(h) - len(row))
            g = lambda k: row[I[k]].strip()  # noqa: E731
            cls, subtype = g("分類"), g("種別")
            place = g("制作地") or g("Country/Origin")
            period_txt = g("時代世紀")
            pc = place_country(place)
            if not pc and FOREIGN.search(period_txt):
                pc = "other"
            pidx = period_of(period_txt or g("Period/Century"), pc if pc in EAST else None)
            country = pc
            if not country:
                if pidx is not None:
                    country = PERIODS[pidx][1]
                elif not cls.startswith("東洋") and cls not in ("民族資料",):
                    country = "Japan"
            if country not in EAST:
                dropped[country or "(unknown)"] += 1
                continue
            if pidx is not None and PERIODS[pidx][1] != country:
                pidx = period_of(period_txt or g("Period/Century"), country)
            otype = COLBASE_TYPE.get(cls, "")
            if cls in ("絵画", "東洋絵画", "法隆寺宝物", "") or not otype:
                for hint, ty in SUBTYPE_HINTS:
                    if hint in subtype:
                        otype = ty
                        break
            otype = otype or ("painting" if "絵" in cls else "other")
            if otype == "painting" and "浮世絵" in subtype and "肉筆" not in g("品質形状"):
                otype = "prints"
            makers = jp_makers(g("作者"))
            ens = en_names(g("Artist"))
            mk = []
            for j, (n, role, attr) in enumerate(makers):
                rom, dates = "", None
                if len(ens) == len(makers):
                    rom, dates = ens[j][0], ens[j][1]
                    attr = attr or ens[j][2]
                mk.append({"name": n, "rom": rom, "dates": dates, "role": role, "attributed": attr})
            raw_maker = g("作者")
            attribution = maker_attribution(mk, raw_maker)
            des = g("文化財指定")
            des = des if des and des != "未指定" else ""
            b, e = colbase_date(row, I, pidx)
            inst = g("機関識別子")
            o = obj(source="colbase", id=f"{inst}:{g('機関管理番号') or g('JPS_ID')}", title=g("作品名"),
                    title_en=g("Title of work"), country=country, period_original=period_txt or g("Period/Century"),
                    _period_idx=pidx, object_type=otype, object_subtype=subtype or cls,
                    attribution=attribution, designation=des, designation_en=DESIGNATION_EN.get(des, des),
                    date=period_txt, date_begin=b, date_end=e, holder=COLBASE_INST.get(inst, inst),
                    url=g("URL"), _makers=mk)
            if attribution == "workshop":
                o["_workshop"] = re.sub(r"^中国・", "", raw_maker)
            out.append(o)
    print(f"ColBase: {len(out):,} East Asian objects; dropped {sum(dropped.values()):,} "
          f"(non-East-Asian or unknown place: {dict(dropped.most_common(6))})")
    return out


def maker_attribution(mk, raw):
    creators = [m for m in mk if m["role"] in CREATOR_ROLES]
    if creators:
        return "attributed_to" if all(m["attributed"] for m in creators) else "named"
    if any(m["role"] == "copyist" for m in mk):
        return "copy"
    if raw and WORKSHOP.search(raw):
        return "workshop"
    return "unattributed"


# ==================================================== Japan designated properties

KUN = "https://kunishitei.bunka.go.jp"
KUN_KINDS = ["絵画", "彫刻", "工芸品", "書跡・典籍", "古文書", "考古資料", "歴史資料"]
KUN_NATIONS = ["国宝", "重要文化財"]
KUN_ERAS = ["縄文", "弥生", "古墳", "飛鳥", "奈良", "平安", "鎌倉", "南北朝", "室町", "安土桃山", "江戸", "明治", "大正",
            "昭和", "平成", "五胡十六国", "隋", "唐", "五代十国", "北宋", "南宋", "元", "明", "清", "中国その他", "新羅", "高麗",
            "李氏朝鮮", "朝鮮その他", "欧米", "その他"]
KUN_MAX = 1900
KUN_COUNTRY = {"日本": "Japan", "中国": "China", "朝鮮": "Korea", "韓国": "Korea", "台湾": "Taiwan"}


class Kunishitei:
    def __init__(self, fetcher):
        self.f = fetcher
        self.token = None

    def _token(self, page):
        m = re.search(r'name="_csrfToken" autocomplete="off" value="([^"]+)"', page or "")
        return m.group(1) if m else None

    def start(self):
        page = self.f.request(KUN + "/bsys/index")
        self.token = self._token(page.decode("utf-8", "replace")) if page else None
        return self.token is not None

    def params(self, kind, nation, era=""):
        p = [("_method", "POST"), ("_csrfToken", self.token), ("screen_id", "index"), ("page_no", "1"),
             ("register_sub_id", "201"), ("entry_kind_201[]", kind), ("nation_div_201", nation)]
        if era:
            p.append(("era_201", era))
        return p

    def count(self, kind, nation, era=""):
        if not self.token and not self.start():
            return None
        body = urllib.parse.urlencode(self.params(kind, nation, era))
        page = self.f.request(KUN + "/bsys/searchlist", data=body,
                              headers={"Content-Type": "application/x-www-form-urlencoded",
                                       "Referer": KUN + "/bsys/index"})
        if page is None:
            return None
        t = page.decode("utf-8", "replace")
        self.token = self._token(t) or self.token
        m = re.search(r"([\d,]+)\s*件中", t)
        if m:
            return int(m.group(1).replace(",", ""))
        if "該当する" in t or "0件" in t:
            return 0
        return None

    def csv(self, kind, nation, era=""):
        body = urllib.parse.urlencode(self.params(kind, nation, era))
        data = self.f.request(KUN + "/utile/csv-list", data=body,
                              headers={"Content-Type": "application/x-www-form-urlencoded",
                                       "Referer": KUN + "/bsys/searchlist"})
        if data is None:
            return None
        text = data.decode("utf-8-sig", "replace")
        if not text.startswith('"台帳ID"'):
            print(f"  kunishitei CSV for {kind}/{nation}/{era} is not a CSV ({text[:60]!r})", file=sys.stderr)
            return None
        return text


def fetch_bunka(delay):
    d = os.path.join(RAW, "bunka")
    os.makedirs(d, exist_ok=True)
    k = Kunishitei(Fetcher(delay, BROWSER_UA, "kunishitei"))
    counts_path = os.path.join(d, "counts.json")
    counts = {}
    if os.path.exists(counts_path):
        with open(counts_path, encoding="utf-8") as f:
            counts = json.load(f)

    def get_count(key, *a):
        if key not in counts:
            n = k.count(*a)
            if n is None:
                return None
            counts[key] = n
            with open(counts_path, "w", encoding="utf-8") as f:
                json.dump(counts, f, ensure_ascii=False, indent=0)
        return counts[key]

    def get_csv(key, *a):
        path = os.path.join(d, safe(key) + ".csv")
        if os.path.exists(path):
            return path
        text = k.csv(*a)
        if text is None:
            return None
        with open(path + ".part", "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(path + ".part", path)
        return path

    files, missing = [], []
    for kind in KUN_KINDS:
        for nation in KUN_NATIONS:
            key = f"{kind}|{nation}"
            n = get_count(key, kind, nation)
            if n is None:
                missing.append(key)
                continue
            if n == 0:
                continue
            if n <= KUN_MAX:
                p = get_csv(key, kind, nation)
                (files if p else missing).append(p or key)
                continue
            got = 0
            for era in KUN_ERAS:
                ek = f"{key}|{era}"
                n2 = get_count(ek, kind, nation, era)
                if n2 is None:
                    missing.append(ek)
                    continue
                if n2 == 0:
                    continue
                got += n2
                p = get_csv(ek, kind, nation, era)
                (files if p else missing).append(p or ek)
            if got < n:
                print(f"  kunishitei {key}: {n} records, era split covers {got} (records without era are missed)",
                      file=sys.stderr)
    if missing:
        print(f"  kunishitei: {len(missing)} queries failed: {missing[:6]}", file=sys.stderr)
    return files


def load_bunka(files):
    out, seen = [], set()
    for path in files:
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                oid = row.get("管理対象ID", "")
                if not oid or oid in seen:
                    continue
                seen.add(oid)
                country = KUN_COUNTRY.get(row.get("国", ""), "other")
                if country not in EAST:
                    continue
                era = row.get("時代", "")
                pidx = period_of(era, country)
                if era == "中国その他" or era == "朝鮮その他":
                    pidx = None
                kind = row.get("種別2", "")
                name = row.get("名称", "")
                otype = BUNKA_TYPE.get(kind) or craft_type(name)
                mk = [{"name": n, "rom": "", "dates": None, "role": r, "attributed": a}
                      for n, r, a in bunka_makers(name)]
                des = row.get("種別1", "")
                date_kokuho, date_juyo = row.get("国宝指定年月日", ""), row.get("重文指定年月日", "")
                o = obj(source="bunka", id=f"201/{oid}", title=name, country=country, period_original=era,
                        _period_idx=pidx, object_type=otype, object_subtype=kind,
                        attribution=maker_attribution(mk, ""), designation=des,
                        designation_en=DESIGNATION_EN.get(des, des), date=era,
                        holder=row.get("所有者名", "") or row.get("保管施設の名称", ""),
                        url=f"{KUN}/heritage/detail/201/{oid}", _makers=mk)
                set_dates_from_period(o, pidx)
                o["_designated_on"] = date_kokuho or date_juyo
                out.append(o)
    print(f"Japan designated properties (kunishitei): {len(out):,} East Asian objects "
          f"({collections.Counter(o['designation'] for o in out)})")
    return out


# ============================================================ National Palace Museum

NPM = "https://digitalarchive.npm.gov.tw/opendata"
NPM_DYNASTIES = ["-7000~-2000~新石器時代", "-2600~-2000~新石器時代晚期", "-1600~-1046~商", "-1100~-800~西周",
                 "-800~-500~春秋", "-500~-300~戰國", "-221~-207~秦", "-206~8~西漢", "9~23~新莽", "25~220~東漢",
                 "220~589~魏晉南北朝", "581~618~隋", "618~907~唐", "907~960~五代", "907~1125~遼", "960~1279~宋",
                 "1115~1234~金", "1271~1368~元", "1368~1644~明", "1644~1911~清", "1911~9999~民國", "0~0~時代不詳"]
NPM_PAGE = 2000
NPM_ARTIST_CATS = {"繪畫", "法書", "成扇"}
NPM_PREFIXES = sorted(["六朝梁", "六朝", "五代南唐", "五代後蜀", "五代", "南唐", "北宋", "南宋", "東晉", "西晉", "晉", "唐", "宋",
                       "元", "明", "清", "金", "遼", "隋", "民國", "後梁", "北魏", "漢", "宋元", "元明", "明清"],
                      key=len, reverse=True)
NPM_NOT_NAME = set("圖卷冊軸畫帖集冊頁幅屏書法墨跡")
NPM_BAD_END = set("畫寫書臨仿摹倣墨繪行草楷題詩詞山水花鳥竹梅蘭石松雪秋春夏冬江溪雲林圖卷冊軸人物蓮荷集等御製法帖與及并合"
                  "觀遊圖景色居堂亭閣樓溪山峰谷泉")
EMPEROR = re.compile(r"^[一-鿿](宗|祖|帝)")


def npm_search(fetcher, cat, dyn, page):
    body = json.dumps({"RegisterType": cat or None, "IndexYear": None, "WestBeginYear": 0, "WestEndYear": 0,
                       "YearDisplay": dyn or None, "SearchContent": None, "RegisterTypeEng": None,
                       "PageInfo": {"PageIndex": page, "PageSize": NPM_PAGE, "PageCount": 0}})
    data = fetcher.request(NPM + "/Pub/Search", data=body, headers={"Content-Type": "application/json"},
                           timeout=240)
    if data is None:
        return None
    t = data.decode("utf-8", "replace")
    items = re.findall(r"Detail\('(\d+)',\s*'(\w+)'\)\"\s*class=\"card\">.*?card-title\">([^<]*)<", t, re.S)
    if not items:
        return None
    return [[i, dep, html.unescape(title).strip()] for i, dep, title in items]


def npm_counts(fetcher, dyn):
    data = fetcher.request(NPM + "/Pub/InitCategory",
                           data=urllib.parse.urlencode({"dynasty": dyn, "category": ""}),
                           headers={"Content-Type": "application/x-www-form-urlencoded"})
    if data is None:
        return None
    t = strip_tags(data.decode("utf-8", "replace"))
    out = {c: int(n) for c, n in re.findall(r"([一-鿿]+)\s*\((\d+)\)", t)}
    return out or None


def fetch_npm(delay):
    f = Fetcher(delay, BROWSER_UA, "npm")
    d = os.path.join(RAW, "npm")
    rows = {}
    expected = 0
    for di, dyn in enumerate(NPM_DYNASTIES):
        counts = cached(os.path.join(d, "counts", f"{di:02d}.json"), lambda: npm_counts(f, dyn))
        if counts is None:
            print(f"  NPM: no category counts for {dyn}", file=sys.stderr)
            continue
        for cat in NPM_CATS:
            n = counts.get(cat, 0)
            if not n:
                continue
            expected += n
            for page in range(1, (n - 1) // NPM_PAGE + 2):
                items = cached(os.path.join(d, "list", f"{di:02d}_{safe(cat)}_{page}.json"),
                               lambda: npm_search(f, cat, dyn, page))
                if items is None:
                    print(f"  NPM: listing failed {dyn} {cat} p{page}", file=sys.stderr)
                    continue
                for i, dep, title in items:
                    r = rows.setdefault(f"{dep}{i}", {"id": i, "dep": dep, "title": title, "cat": cat, "dyn": []})
                    label = dyn.split("~")[-1]
                    if label not in r["dyn"]:
                        r["dyn"].append(label)
    print(f"NPM: {len(rows):,} distinct objects listed ({expected:,} dynasty x category hits expected); "
          f"{f.requests} requests")
    return list(rows.values()), f


def npm_title_split(title):
    """'明沈周廬山高　軸' -> ('明', '沈周廬山高　軸')."""
    t = title.strip()
    for p in NPM_PREFIXES:
        if t.startswith(p):
            return p, t[len(p):]
    return "", t


def npm_parse_makers(rows, lexicon):
    """Attach 'maker' to painting / calligraphy / fan rows using lexicon + frequency."""
    rems = []
    cnt = collections.Counter()
    for r in rows:
        if r["cat"] not in NPM_ARTIST_CATS:
            continue
        pre, rem = npm_title_split(r["title"])
        rem = re.sub(r"^[（(][^）)]*[）)]", "", rem)
        rem = re.sub(r"^(原題|傳|伝)", lambda m: "" if m.group(1) == "原題" else m.group(0), rem)
        r["_pre"], r["_rem"] = pre, rem
        rems.append(r)
        f = fold_cjk(rem.lstrip("傳"))
        for L in (2, 3, 4):
            if len(f) >= L:
                cnt[f[:L]] += 1
    lex = {}
    for name in lexicon:
        fn = fold_cjk(name)
        if 2 <= len(fn) <= 4:
            lex[fn] = name
    for r in rems:
        rem = r["_rem"]
        attributed = rem.startswith("傳")
        rem = rem[1:] if attributed else rem
        f = fold_cjk(rem)
        r["maker"], r["attributed"] = "", attributed
        if not f or f[0] == "人" or f.startswith(("院本", "院畫", "院", "佚名", "無款", "人畫", "人書")) or \
                (len(f) > 1 and f[0] in "宋元明清唐" and f[1] == "人"):
            r["anonymous"] = True
            continue
        best = None
        for L in (4, 3, 2):
            if f[:L] in lex and len(f) > L:
                best = rem[:L]
                break
        if best is None:
            n_prev = 0
            for L in (2, 3, 4):
                c = f[:L]
                if len(c) < L or len(f) == L or any(ch in NPM_NOT_NAME for ch in c):
                    break
                n = cnt[c]
                if n < 2:
                    break
                if L == 2:
                    best, n_prev = rem[:2], n
                elif n >= 0.5 * n_prev and c[-1] not in NPM_BAD_END:
                    best, n_prev = rem[:L], n
                else:
                    break
        if best and EMPEROR.match(best) and r["_pre"]:
            best = r["_pre"][-1] + best      # 清高宗, 宋徽宗
        r["maker"] = best or ""
        r["anonymous"] = False


def npm_detail(fetcher, i, dep):
    data = fetcher.request(f"{NPM}/Pub/Detail/{i}?dep={dep}&mode=full")
    if data is None:
        return None
    t = data.decode("utf-8", "replace")
    fields = {}
    for k, v in re.findall(r"<td>\s*([^<]{1,12}?)\s*</td>\s*<td>(.*?)</td>", t, re.S):
        k = k.strip()
        if k and k not in fields:
            fields[k] = strip_tags(v)[:300]
    return fields


def npm_romanise(author, name):
    """'張僧繇,明人 Anonymous,Ming Dynasty,Zhang Sengyou,Liang dynasty' + '張僧繇' -> 'Zhang Sengyou'."""
    toks = [t.strip() for t in re.split(r",", author or "") if t.strip()]
    cjk = [re.sub(r"\s.*", "", t) for t in toks if has_cjk(t)]
    lat = [t for t in toks if not has_cjk(t) and not re.search(r"dynasty|period|anonymous|unknown|emperor of", t, re.I)
           and re.fullmatch(r"[A-Za-z' .\-āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü]+", t)]
    fn = fold_cjk(name)
    idx = next((j for j, c in enumerate(cjk) if fold_cjk(c) == fn), None)
    if idx is None:
        return ""
    names_cjk = [c for c in cjk if not c.endswith("人")]
    if len(lat) == 1 and len(names_cjk) == 1:
        return lat[0]
    if len(lat) == len(names_cjk) and fn in [fold_cjk(c) for c in names_cjk]:
        return lat[[fold_cjk(c) for c in names_cjk].index(fn)]
    return ""


def load_npm(rows, fetcher, lexicon, n_details):
    npm_parse_makers(rows, lexicon)
    # one detail page per maker, most frequent makers first
    by_maker = collections.defaultdict(list)
    for r in rows:
        if r.get("maker"):
            by_maker[fold_cjk(r["maker"])].append(r)
    rom = {}
    order = sorted(by_maker, key=lambda k: -len(by_maker[k]))
    fetched = 0
    for k in order[:n_details]:
        r = by_maker[k][0]
        det = cached(os.path.join(RAW, "npm", "detail", f"{r['dep']}{r['id']}.json"),
                     lambda: npm_detail(fetcher, r["id"], r["dep"]))
        fetched += 1
        if det:
            rr = npm_romanise(det.get("作者", ""), r["maker"])
            if rr:
                rom[k] = rr
    print(f"NPM: {len(by_maker):,} parsed makers; detail pages read for {fetched}, romanised {len(rom)}")
    out = []
    for r in rows:
        labels = r["dyn"]
        pre = r.get("_pre") or npm_title_split(r["title"])[0]
        cand = [period_of(lb, "China") for lb in labels]
        pidx = None
        if len(cand) == 1:
            pidx = cand[0]
        elif pre:
            p2 = period_of(pre, "China")
            pidx = p2 if p2 in cand else (cand[0] if cand else None)
        elif cand:
            pidx = cand[0]
        mk = []
        if r.get("maker"):
            mk = [{"name": r["maker"], "rom": rom.get(fold_cjk(r["maker"]), ""), "dates": None,
                   "role": "painter" if r["cat"] != "法書" else "calligrapher", "attributed": r.get("attributed")}]
        otype = NPM_TYPE[r["cat"]]
        if mk:
            attribution = "attributed_to" if r.get("attributed") else "named"
        elif r["cat"] in NPM_ARTIST_CATS and not r.get("anonymous"):
            attribution = "named_unparsed"
        else:
            attribution = "unattributed"
        o = obj(source="npm", id=f"{r['dep']}{r['id']}", title=r["title"], country="China",
                period_original="/".join(labels), _period_idx=pidx, object_type=otype, object_subtype=r["cat"],
                attribution=attribution, holder="National Palace Museum, Taipei",
                url=f"{NPM}/Pub/Detail/{r['id']}?dep={r['dep']}&mode=full", _makers=mk)
        set_dates_from_period(o, pidx)
        out.append(o)
    return out


# ================================================================== Korea e-Museum

EM = "https://www.emuseum.go.kr"
EM_KEYS = ("cateClass cateListFlag keyword pageNum rows reltRows sort highQualityYn isImgExistOp mckoglsvOp "
           "isIntrstMuseumOp filedOp detailFlag dq mcSeqNo author culturalHerNo publicType detailedDes thema "
           "storySeq categoryLv categoryCode ps01Lv1 ps01Lv2 ps01Lv3 ps06Lv1 ps06Lv2 ps08Lv1 ps08Lv2 ps09Lv1 "
           "ps09Lv2 ps09Lv3 ps09Lv4 ps12Lv1 ps15Lv1 gl05Lv1 gl05Lv2 mobileFacetIng location facet1Lv1 facet1Lv2 "
           "facet1Lv3 facet2Lv1 facet3Lv1 facet3Lv2 facet4Lv1 facet4Lv2 facet5Lv1 facet5Lv2 facet5Lv3 facet5Lv4 "
           "facet6Lv1 facet6Lv2 facet7Lv1Selected facet7Lv1 facet8Lv1 keywordHistory radioSearchCheck").split()
EM_ROWS = 36
EM_NMK = "PS01001001"
EM_DESIGNATIONS = [("PS12001", "국보"), ("PS12002", "보물")]
EM_SEOHWA = [("PS09009003001", "calligraphy", "글씨"), ("PS09009003002", "painting", "회화")]
EM_COUNTRY = {"PS06001": "Korea", "PS06002": "China", "PS06003": "Japan"}


class EMuseum:
    def __init__(self, fetcher):
        self.f = fetcher
        self.started = False

    def search(self, **params):
        if not self.started:
            self.f.request(EM + "/main")
            self.started = True
        d = {k: "" for k in EM_KEYS}
        d.update(params)
        data = self.f.request(EM + "/headerSearch?" + urllib.parse.urlencode(d))
        if data is None:
            return None
        return data.decode("utf-8", "replace")

    @staticmethod
    def total(page):
        m = re.search(r"검색 결과 : ([\d,]+)", page or "")
        return int(m.group(1).replace(",", "")) if m else None

    @staticmethod
    def facets(page):
        out = []
        for m in re.finditer(r"goFacet\('([^']+)','([^']+)'(?:,'[^']*')?\);\"\s*title=\"([^\"]+?) 조건[^>]*>"
                             r"\s*[^<(]*\(([\d,]+)\)", page or ""):
            out.append([m.group(1), m.group(2), m.group(3), int(m.group(4).replace(",", ""))])
        return out

    @staticmethod
    def items(page):
        out = []
        for block in (page or "").split('<div class="item">')[1:]:
            rid = re.search(r"fnMaker\('I','(PS\w+)'", block)
            title = re.search(r'class="title ellipsis">(.*?)</div>', block, re.S)
            lis = re.findall(r"<li>(.*?)</li>", block, re.S)
            if rid and title:
                out.append([rid.group(1), strip_tags(title.group(1)), strip_tags(lis[0]) if lis else "",
                            strip_tags(lis[1]) if len(lis) > 1 else ""])
        return out

    def listing(self, cache_key, max_pages=400, **params):
        """All items for a facet query: [[relicId, title, museum, accession], ...]."""
        d = os.path.join(RAW, "korea", "list")
        first = cached(os.path.join(d, f"{cache_key}_1.json"), lambda: self._page(1, **params))
        if first is None:
            return None, None
        total = first["total"] or 0
        items = list(first["items"])
        pages = min(max_pages, (total - 1) // EM_ROWS + 1) if total else 0
        for p in range(2, pages + 1):
            pg = cached(os.path.join(d, f"{cache_key}_{p}.json"), lambda: self._page(p, **params))
            if pg is None:
                print(f"  e-Museum: page {p} of {cache_key} failed", file=sys.stderr)
                continue
            items.extend(pg["items"])
        return items, first

    def _page(self, p, **params):
        page = self.search(rows=str(EM_ROWS), pageNum=str(p), **params)
        if page is None or self.total(page) is None:
            return None
        return {"total": self.total(page), "items": self.items(page), "facets": self.facets(page) if p == 1 else []}

    def detail(self, rid):
        data = self.f.request(f"{EM}/detail?relicId={rid}")
        if data is None:
            return None
        t = data.decode("utf-8", "replace")
        fields = {}
        for k, v in re.findall(r"<li>\s*<em>([^<]+)</em>\s*<span>(.*?)</span>\s*</li>", t, re.S):
            k = k.strip()
            if k not in fields:
                fields[k] = strip_tags(v)[:300]
        m = re.search(r"<title>(.*?)</title>", t, re.S)
        fields["_title"] = strip_tags(m.group(1)).replace(" - e뮤지엄 소장품검색", "") if m else ""
        return fields if len(fields) > 1 else None


def em_period(label, country):
    if not label or "미상" in label:
        return None
    return period_of(label, country)


def ko_type(classification, material, title):
    c = classification or ""
    if "서화" in c or "회화" in c or "글씨" in c:
        if "글씨" in c or "서예" in c or "서첩" in c or "어필" in c:
            return "calligraphy"
        if "판화" in c:
            return "prints"
        return "painting"
    if "불교" in c and ("불상" in c or "조각" in c):
        return "sculpture"
    if "무기" in c or "무구" in c:
        return "arms and armour"
    if "전적" in c or "문헌" in c or "기록" in c:
        return "books and manuscripts"
    if "불상" in c or "불상" in (title or "") or "조각" in c:
        return "sculpture"
    m = (material or "").split(" - ")[0].strip()
    if m in KO_MATERIAL_TYPE:
        t = KO_MATERIAL_TYPE[m]
        if t == "painting":
            return "books and manuscripts" if ("문서" in c or "책" in c) else "painting"
        return t
    return "other"


def fetch_korea(delay, n_details):
    em = EMuseum(Fetcher(delay, BROWSER_UA, "emuseum"))
    out = []
    # (a) designated properties, Korean (facet3Lv1 = 한국) national treasures and treasures, with details
    designated = []
    for code, label in EM_DESIGNATIONS:
        items, first = em.listing(f"des_{code}", facet2Lv1=code, facet3Lv1="PS06001")
        if items is None:
            print(f"  e-Museum: designated listing {label} failed", file=sys.stderr)
            continue
        print(f"  e-Museum {label}: {first['total']:,} listed, {len(items):,} read")
        designated += [(it, label) for it in items]
    seen = set()
    n_det = 0
    for it, label in designated:
        rid = it[0]
        if rid in seen:
            continue
        seen.add(rid)
        det = None
        if n_det < n_details:
            det = cached(os.path.join(RAW, "korea", "detail", f"{rid}.json"), lambda: em.detail(rid))
            n_det += 1
        det = det or {}
        cp = det.get("국적/시대", "")
        country_txt, _, period_txt = cp.partition(" - ")
        country = {"한국": "Korea", "중국": "China", "일본": "Japan"}.get(country_txt.strip(), "Korea")
        pidx = em_period(period_txt.strip(), country)
        title = it[1]
        maker = None
        for key in ("작가", "제작자", "작자"):
            if det.get(key):
                maker = (det[key].strip(), False)
                break
        maker = maker or korean_maker(title)
        mk = []
        if maker and not KO_NOT_NAME.search(maker[0]):
            mk = [{"name": maker[0], "rom": romanise_korean_name(maker[0]), "dates": None, "role": "artist",
                   "attributed": maker[1]}]
        otype = ko_type(det.get("분류", ""), det.get("재질", ""), title)
        o = obj(source="emuseum", id=rid, title=title, country=country, period_original=period_txt.strip(),
                _period_idx=pidx, object_type=otype, object_subtype=det.get("분류", ""),
                attribution=maker_attribution(mk, ""), designation=det.get("국가지정유산") or label,
                designation_en=DESIGNATION_EN.get(det.get("국가지정유산") or label, label),
                holder=it[2], url=f"{EM}/detail?relicId={rid}", _makers=mk)
        set_dates_from_period(o, pidx)
        out.append(o)
    print(f"  e-Museum designated: {len(out):,} objects ({n_det} detail pages)")
    # (b) National Museum of Korea painting and calligraphy, per period facet
    nmk_n = 0
    for code, otype, ko in EM_SEOHWA:
        _, first = em.listing(f"nmk_{code}_all", max_pages=1, facet1Lv2=EM_NMK, facet5Lv3=code)
        if first is None:
            print(f"  e-Museum: NMK {ko} facets failed", file=sys.stderr)
            continue
        periods = [f for f in first["facets"] if f[0] == "facet3Lv2"]
        covered = 0
        for _, pcode, plabel, n in periods:
            items, _ = em.listing(f"nmk_{code}_{pcode}", facet1Lv2=EM_NMK, facet5Lv3=code, facet3Lv2=pcode)
            if items is None:
                continue
            covered += len(items)
            country = EM_COUNTRY.get(pcode[:7], "other")
            pidx = em_period(plabel, country if country in EAST else None)
            for rid, title, museum, acc in items:
                if rid in seen:
                    continue
                seen.add(rid)
                maker = korean_maker(title)
                mk = []
                if maker:
                    mk = [{"name": maker[0], "rom": romanise_korean_name(maker[0]), "dates": None,
                           "role": "painter" if otype == "painting" else "calligrapher", "attributed": maker[1]}]
                o = obj(source="emuseum", id=rid, title=title, country=country, period_original=plabel,
                        _period_idx=pidx, object_type=otype, object_subtype=f"서화 - {ko}",
                        attribution=maker_attribution(mk, ""), holder=museum or "국립중앙박물관",
                        url=f"{EM}/detail?relicId={rid}", _makers=mk)
                set_dates_from_period(o, pidx)
                out.append(o)
                nmk_n += 1
        print(f"  e-Museum NMK {ko}: {first['total']:,} listed, {covered:,} read across {len(periods)} period facets")
    # (c) NMK whole collection: period x material facet counts (context for traditions)
    facet_counts = []
    _, first = em.listing("nmk_all", max_pages=1, facet1Lv2=EM_NMK)
    if first is not None:
        for _, pcode, plabel, n in [f for f in first["facets"] if f[0] == "facet3Lv2"]:
            country = EM_COUNTRY.get(pcode[:7], "other")
            if country not in EAST:
                continue
            _, pf = em.listing(f"nmk_all_{pcode}", max_pages=1, facet1Lv2=EM_NMK, facet3Lv2=pcode)
            if pf is None:
                continue
            for fk, mcode, mlabel, mn in pf["facets"]:
                if fk == "facet4Lv1":
                    facet_counts.append({"country": country, "period_original": plabel,
                                         "period_en": period_label(em_period(plabel, country)),
                                         "material": mlabel, "object_type": KO_MATERIAL_TYPE.get(mlabel, "other"),
                                         "objects": mn})
    print(f"e-Museum: {len(out):,} objects ({nmk_n:,} NMK painting/calligraphy); "
          f"{len(facet_counts)} NMK period x material facet cells; {em.f.requests} requests")
    return out, facet_counts


# ========================================================================= Cleveland

CMA_API = "https://openaccess-api.clevelandart.org/api/artworks/"
CMA_DEPTS = {"Chinese Art": "China", "Japanese Art": "Japan", "Korean Art": "Korea"}
CMA_NON_CREATOR = {"inscriber", "publisher", "author", "collector", "former owner", "printer", "editor",
                   "translator", "compiler", "commentator", "seal carver", "owner"}
CMA_FIELDS = ("id,accession_number,title,culture,creators,type,technique,creation_date,creation_date_earliest,"
              "creation_date_latest,department,url,collection")


def fetch_cma(delay):
    f = Fetcher(delay, UA, "cma")
    out = []
    for dept, country in CMA_DEPTS.items():
        skip = 0
        while True:
            def get():
                q = urllib.parse.urlencode({"department": dept, "limit": 1000, "skip": skip, "fields": CMA_FIELDS})
                data = f.request(CMA_API + "?" + q, timeout=240)
                if data is None:
                    return None
                d = json.loads(data)
                keep = []
                for o in d.get("data", []):
                    o["creators"] = [{k: c.get(k) for k in ("description", "role", "name_in_original_language",
                                                            "birth_year", "death_year", "qualifier")}
                                     for c in (o.get("creators") or [])]
                    keep.append(o)
                return {"total": d.get("info", {}).get("total", 0), "data": keep}
            page = cached(os.path.join(RAW, "cma", f"{safe(dept)}_{skip}.json"), get)
            if page is None:
                print(f"  CMA: {dept} skip={skip} failed", file=sys.stderr)
                break
            for o in page["data"]:
                out.append(cma_object(o, country))
            skip += 1000
            if skip >= page["total"] or not page["data"]:
                break
    print(f"Cleveland: {len(out):,} objects")
    return out


def cma_object(o, country):
    culture = "; ".join(o.get("culture") or [])
    pidx = period_of(culture, country)
    mk = []
    for c in o.get("creators") or []:
        desc = c.get("description") or ""
        rom = re.sub(r"\s*\(.*", "", desc).strip()
        orig = (c.get("name_in_original_language") or "").strip()
        if not rom or PLACEHOLDER.search(rom) or WORKSHOP.search(rom):
            continue
        attributed = bool(re.search(r"attributed|follower|circle|school|style", (c.get("qualifier") or "") +
                                    " " + (c.get("role") or ""), re.I))
        dates = None
        try:
            b, d = int(c.get("birth_year") or 0), int(c.get("death_year") or 0)
            if b and d:
                dates = (b, d)
        except ValueError:
            dates = life_dates(desc)
        role = (c.get("role") or "artist").lower()
        mk.append({"name": orig if has_cjk(orig) else "", "rom": rom, "dates": dates,
                   "role": role if role in CMA_NON_CREATOR else "artist", "attributed": attributed})
    raw = " ".join((c.get("description") or "") for c in o.get("creators") or [])
    attribution = maker_attribution(mk, raw)
    if attribution == "workshop":
        ob_workshop = re.sub(r"\s*\(.*", "", raw)[:40]
    else:
        ob_workshop = ""
    otype = en_type(o.get("type"), o.get("collection"), o.get("technique"))
    ob = obj(source="cma", id=str(o.get("id")), title=o.get("title", ""), country=country,
             period_original=culture, _period_idx=pidx, object_type=otype,
             object_subtype=o.get("type") or o.get("collection") or "", attribution=attribution,
             date=o.get("creation_date", ""), date_begin=o.get("creation_date_earliest"),
             date_end=o.get("creation_date_latest"), holder="Cleveland Museum of Art",
             url=o.get("url", ""), _makers=mk)
    ob["_workshop"] = ob_workshop
    return ob


# ============================================================================== AIC

AIC_COUNTRY = {"China": "China", "Japan": "Japan", "Korea": "Korea", "Taiwan": "Taiwan"}


def load_aic():
    if not os.path.isdir(AIC_DIR):
        print("AIC dump not on disk; skipped")
        return []
    out = []
    for path in glob.glob(os.path.join(AIC_DIR, "*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        country = AIC_COUNTRY.get((d.get("place_of_origin") or "").strip())
        if not country:
            continue
        text = " ".join([d.get("date_display") or ""] + (d.get("style_titles") or []))
        pidx = period_of(text, country)
        mk = []
        title_a = (d.get("artist_title") or "").strip()
        disp = d.get("artist_display") or ""
        if title_a and not PLACEHOLDER.search(title_a) and not NON_PERSON.search(title_a) \
                and not WORKSHOP.search(title_a):
            first = disp.split("\n")[0]
            orig = "".join(CJK.findall(first)) if has_cjk(first) else ""
            mk.append({"name": orig, "rom": title_a, "dates": life_dates(disp), "role": "artist",
                       "attributed": bool(re.search(r"attributed", disp, re.I))})
        attribution = maker_attribution(mk, disp)
        otype = en_type(d.get("classification_title"), d.get("artwork_type_title"), d.get("medium_display"))
        out.append(obj(source="aic", id=str(d.get("id")), title=d.get("title") or "", country=country,
                       period_original=d.get("date_display") or "", _period_idx=pidx, object_type=otype,
                       object_subtype=d.get("classification_title") or d.get("artwork_type_title") or "",
                       attribution=attribution, date=d.get("date_display") or "", date_begin=d.get("date_start"),
                       date_end=d.get("date_end"), holder="Art Institute of Chicago",
                       url=f"https://www.artic.edu/artworks/{d.get('id')}", _makers=mk))
    print(f"AIC: {len(out):,} objects from China / Japan / Korea")
    return out


# ======================================================================== artists

NON_ARTIST_TYPES = {"books and manuscripts", "documents and historical materials", "archaeology", "coins"}
SOURCES = ["colbase", "bunka", "npm", "emuseum", "cma", "aic"]


def build_artists(objects):
    """Assign artist_key to every maker mention and aggregate per maker."""
    rom2key = collections.defaultdict(collections.Counter)
    for o in objects:
        for m in o["_makers"]:
            if m["name"]:
                fk = fold_cjk(m["name"])
                m["key"] = "o:" + NAME_ALIASES_F.get(fk, fk)
                if m["rom"]:
                    rom2key[fold_rom(m["rom"])][m["key"]] += 1
    for o in objects:
        for m in o["_makers"]:
            if not m.get("key"):
                fr = fold_rom(m["rom"])
                if not fr:
                    continue
                m["key"] = rom2key[fr].most_common(1)[0][0] if fr in rom2key else "r:" + fr
    # per-key romanisation and dates
    roms = collections.defaultdict(collections.Counter)
    dates = collections.defaultdict(collections.Counter)
    for o in objects:
        for m in o["_makers"]:
            if m.get("key"):
                if m["rom"]:
                    roms[m["key"]][m["rom"]] += 1
                if m["dates"]:
                    dates[m["key"]][tuple(m["dates"])] += 1
    # merge original-script keys that share a romanisation and agree on dates (hanja vs hangul, variants)
    by_rom = collections.defaultdict(list)
    for k, c in roms.items():
        by_rom[fold_rom(c.most_common(1)[0][0])].append(k)
    alias = {}
    for fr, keys in by_rom.items():
        if len(keys) < 2 or len(fr) < 6:
            continue
        keys.sort(key=lambda k: -sum(roms[k].values()))
        head = keys[0]
        hd = dates[head].most_common(1)[0][0] if dates[head] else None
        for k in keys[1:]:
            kd = dates[k].most_common(1)[0][0] if dates[k] else None
            if hd and kd and abs(hd[0] - kd[0]) > 2:
                continue
            alias[k] = head
    agg = {}
    for o in objects:
        keys_here = []
        for m in o["_makers"]:
            k = m.get("key")
            if not k:
                continue
            k = alias.get(k, k)
            m["key"] = k
            if m["role"] not in CREATOR_ROLES and m["role"] != "artist":
                continue
            if k in keys_here:
                continue
            keys_here.append(k)
            a = agg.setdefault(k, {"orig": collections.Counter(), "rom": collections.Counter(),
                                   "dates": collections.Counter(), "country": collections.Counter(),
                                   "period": collections.Counter(), "type": collections.Counter(),
                                   "src": collections.Counter(), "attr_to": 0, "des": collections.Counter(),
                                   "examples": [], "visual": 0})
            if m["name"]:
                a["orig"][m["name"]] += 1
            if m["rom"]:
                a["rom"][m["rom"]] += 1
            if m["dates"]:
                a["dates"][tuple(m["dates"])] += 1
            a["country"][o["country"]] += 1
            if o["period_en"]:
                a["period"][o["period_en"]] += 1
            a["type"][o["object_type"]] += 1
            a["src"][o["source"]] += 1
            if m["attributed"]:
                a["attr_to"] += 1
            if o["object_type"] not in NON_ARTIST_TYPES:
                a["visual"] += 1
            if o["designation"]:
                a["des"][(o["source"], o["designation"])] += 1
            if len(a["examples"]) < 3 and (o["designation"] or len(a["examples"]) < 2):
                a["examples"].append(o["title"][:60])
        # write back the primary maker on the object row
        creators = [m for m in o["_makers"] if m.get("key") and (m["role"] in CREATOR_ROLES or m["role"] == "artist")]
        show = creators or o["_makers"]
        if show:
            o["artist_original"] = " / ".join(m["name"] for m in show if m["name"])
            o["artist_romanised"] = " / ".join(m["rom"] or "" for m in show if m["rom"])
            o["artist_role"] = " / ".join(m["role"] for m in show if m["role"])
            o["artist_key"] = " / ".join(m.get("key", "") for m in show if m.get("key"))
    # fill romanisations from the per-key table
    rom_best = {k: (a["rom"].most_common(1)[0][0] if a["rom"] else "") for k, a in agg.items()}
    for o in objects:
        if o["artist_key"] and not o["artist_romanised"]:
            o["artist_romanised"] = " / ".join(rom_best.get(k, "") for k in o["artist_key"].split(" / ")
                                               if rom_best.get(k))
    rows = []
    for k, a in agg.items():
        if a["visual"] == 0:
            continue
        d = a["dates"].most_common(1)[0][0] if a["dates"] else ("", "")
        des = a["des"]
        row = {
            "artist_key": k,
            "artist_original": a["orig"].most_common(1)[0][0] if a["orig"] else "",
            "artist_romanised": rom_best[k],
            "other_names": "; ".join(list(n for n, _ in a["orig"].most_common(4))[1:] +
                                     list(n for n, _ in a["rom"].most_common(3))[1:]),
            "birth_year": d[0], "death_year": d[1],
            "country": a["country"].most_common(1)[0][0],
            "periods": "; ".join(p for p, _ in a["period"].most_common(3)),
            "object_types": "; ".join(f"{t} {n}" for t, n in a["type"].most_common(3)),
            "objects_total": sum(a["src"].values()),
        }
        for s in SOURCES:
            row[f"objects_{s}"] = a["src"].get(s, 0)
        row["attributed_to_objects"] = a["attr_to"]
        row["n_sources"] = len(a["src"])
        row["jp_kokuho"] = des.get(("bunka", "国宝"), 0)
        row["jp_juyo_bunkazai"] = des.get(("bunka", "重要文化財"), 0)
        row["kr_gukbo"] = sum(n for (s, dn), n in des.items() if s == "emuseum" and dn == "국보")
        row["kr_bomul"] = sum(n for (s, dn), n in des.items() if s == "emuseum" and dn == "보물")
        row["designated_total"] = row["jp_kokuho"] + row["jp_juyo_bunkazai"] + row["kr_gukbo"] + row["kr_bomul"]
        row["colbase_kokuho"] = des.get(("colbase", "国宝"), 0)
        row["colbase_juyo_bunkazai"] = des.get(("colbase", "重要文化財"), 0)
        row["colbase_juyo_bijutsuhin"] = des.get(("colbase", "重要美術品"), 0)
        row["example_titles"] = " | ".join(a["examples"])
        rows.append(row)
    rows.sort(key=lambda r: (-r["designated_total"], -r["objects_total"]))
    return rows


# ====================================================================== traditions

def build_traditions(objects, facet_counts):
    cells = {}

    def cell(country, period, otype):
        return cells.setdefault((country, period or "(unknown)", otype), {
            "all": 0, "attr": 0, "una": 0, "copies": 0, "src": collections.Counter(), "des": 0,
            "workshops": collections.Counter(), "orig": collections.Counter(), "examples": [], "nmk_all": 0})
    for o in objects:
        c = cell(o["country"], o["period_en"], o["object_type"])
        if o["attribution"] == "copy":
            c["copies"] += 1
            continue
        c["all"] += 1
        if o["attribution"] in ("named", "attributed_to", "named_unparsed"):
            c["attr"] += 1
            continue
        c["una"] += 1
        c["src"][o["source"]] += 1
        if o["designation"]:
            c["des"] += 1
        if o["attribution"] == "workshop" and o.get("_workshop"):
            c["workshops"][o["_workshop"][:30]] += 1
        if o["period_original"]:
            c["orig"][o["period_original"][:40]] += 1
        if len(c["examples"]) < 3 and (o["designation"] or len(c["examples"]) < 2):
            c["examples"].append(f"{o['source']}:{o['title'][:50]}")
    for fc in facet_counts:
        cell(fc["country"], fc["period_en"] or fc["period_original"], fc["object_type"])["nmk_all"] += fc["objects"]
    rows = []
    for (country, period, otype), c in cells.items():
        pidx = next((i for i, p in enumerate(PERIODS) if p[0] == period and p[1] == country), None)
        row = {"country": country, "period_en": period,
               "period_begin": PERIODS[pidx][2] if pidx is not None else "",
               "period_end": PERIODS[pidx][3] if pidx is not None else "",
               "object_type": otype, "unattributed_objects": c["una"], "all_objects": c["all"],
               "attributed_share": round(c["attr"] / c["all"], 3) if c["all"] else "",
               "copies_excluded": c["copies"]}
        for s in SOURCES:
            row[f"unattributed_{s}"] = c["src"].get(s, 0)
        row["designated_unattributed"] = c["des"]
        row["nmk_all_objects_by_material"] = c["nmk_all"]
        row["top_kilns_workshops"] = "; ".join(f"{n} ({k})" for n, k in c["workshops"].most_common(3))
        row["period_original_examples"] = "; ".join(p for p, _ in c["orig"].most_common(3))
        row["examples"] = " | ".join(c["examples"])
        if row["unattributed_objects"] or row["nmk_all_objects_by_material"]:
            rows.append(row)
    order = {"China": 0, "Japan": 1, "Korea": 2, "Taiwan": 3}
    rows.sort(key=lambda r: (order.get(r["country"], 9), r["period_begin"] if r["period_begin"] != "" else 99999,
                             r["period_en"], -r["unattributed_objects"]))
    return rows


# ========================================================================== output

def write(path, rows, fields):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".part", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    os.replace(path + ".part", path)


def report(objects, artists, traditions):
    print("\n== objects per source")
    for s, n in collections.Counter(o["source"] for o in objects).most_common():
        des = sum(1 for o in objects if o["source"] == s and o["designation"])
        print(f"  {s:8s} {n:8,}   designated {des:,}")
    print("\n== attributed share by object type (named + attributed_to over all, copies excluded)")
    t = collections.defaultdict(lambda: [0, 0, 0])
    for o in objects:
        if o["attribution"] == "copy":
            t[o["object_type"]][2] += 1
            continue
        t[o["object_type"]][1] += 1
        if o["attribution"] in ("named", "attributed_to", "named_unparsed"):
            t[o["object_type"]][0] += 1
    for ty, (a, n, cp) in sorted(t.items(), key=lambda x: -x[1][1]):
        print(f"  {ty:36s} {n:7,}  attributed {a / n:5.1%}" + (f"  (+{cp:,} copies)" if cp else ""))
    print("\n== period coverage (objects; attributed share) by country")
    p = collections.defaultdict(lambda: [0, 0, collections.Counter()])
    for o in objects:
        if o["attribution"] == "copy":
            continue
        k = (o["country"], o["period_en"] or "(unknown)")
        p[k][0] += 1
        p[k][1] += o["attribution"] in ("named", "attributed_to", "named_unparsed")
        p[k][2][o["source"]] += 1
    beg = {(pp[1], pp[0]): pp[2] for pp in PERIODS}
    for k in sorted(p, key=lambda k: (k[0], beg.get(k, 99999))):
        n, a, src = p[k]
        print(f"  {k[0]:7s} {k[1]:28s} {n:7,}  {a / n:5.1%}  " +
              ", ".join(f"{s} {c:,}" for s, c in src.most_common()))
    print("\n== top 30 artists (designated, then objects)")
    for r in artists[:30]:
        print(f"  {r['artist_original'][:12]:12s} {r['artist_romanised'][:26]:26s} {r['birth_year']}-{r['death_year']} "
              f"{r['country']:6s} des {r['designated_total']:3d} (kokuho {r['jp_kokuho']}, juyo {r['jp_juyo_bunkazai']}, "
              f"kr {r['kr_gukbo']}/{r['kr_bomul']}) obj {r['objects_total']:5d} src {r['n_sources']}")
    print("\n== top 30 artists by objects")
    for r in sorted(artists, key=lambda r: -r["objects_total"])[:30]:
        print(f"  {r['artist_original'][:12]:12s} {r['artist_romanised'][:26]:26s} {r['country']:6s} "
              f"obj {r['objects_total']:5d} " + " ".join(f"{s}={r['objects_' + s]}" for s in SOURCES if r['objects_' + s])
              + f" des {r['designated_total']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip", default="", help="comma list of sources to skip: bunka,npm,emuseum,cma,aic")
    ap.add_argument("--npm-details", type=int, default=400, help="NPM detail pages (one per parsed maker)")
    ap.add_argument("--korea-details", type=int, default=2000, help="e-Museum detail pages for designated objects")
    ap.add_argument("--delay", type=float, default=1.0)
    ap.add_argument("--offline", action="store_true", help="use cached responses only")
    args = ap.parse_args()
    OFFLINE[0] = args.offline
    skip = set(filter(None, args.skip.split(",")))

    objects = load_colbase()
    cma = [] if "cma" in skip else fetch_cma(args.delay)
    aic = [] if "aic" in skip else load_aic()
    bunka = []
    if "bunka" not in skip:
        bunka = load_bunka(fetch_bunka(args.delay))
    korea, facet_counts = ([], []) if "emuseum" in skip else fetch_korea(args.delay, args.korea_details)
    npm = []
    if "npm" not in skip:
        rows, fetcher = fetch_npm(args.delay)
        lexicon = set()
        for o in cma + objects:
            if o["country"] == "China":
                for m in o["_makers"]:
                    if m["name"] and has_cjk(m["name"]):
                        lexicon.add(m["name"])
        npm = load_npm(rows, fetcher, lexicon, args.npm_details)
    objects = objects + bunka + npm + korea + cma + aic

    artists = build_artists(objects)
    traditions = build_traditions(objects, facet_counts)
    for o in objects:
        for k in ("date_begin", "date_end"):
            if o[k] in (None, ""):
                o[k] = ""
    write(os.path.join(OUT_DIR, "east_asia_objects.csv"), objects, OBJ_FIELDS)
    afields = ["artist_key", "artist_original", "artist_romanised", "other_names", "birth_year", "death_year",
               "country", "periods", "object_types", "objects_total"] + [f"objects_{s}" for s in SOURCES] + \
              ["attributed_to_objects", "n_sources", "designated_total", "jp_kokuho", "jp_juyo_bunkazai", "kr_gukbo",
               "kr_bomul", "colbase_kokuho", "colbase_juyo_bunkazai", "colbase_juyo_bijutsuhin", "example_titles"]
    write(os.path.join(OUT_DIR, "east_asia_artists.csv"), artists, afields)
    tfields = ["country", "period_en", "period_begin", "period_end", "object_type", "unattributed_objects",
               "all_objects", "attributed_share", "copies_excluded"] + [f"unattributed_{s}" for s in SOURCES] + \
              ["designated_unattributed", "nmk_all_objects_by_material", "top_kilns_workshops",
               "period_original_examples", "examples"]
    write(os.path.join(OUT_DIR, "east_asia_traditions.csv"), traditions, tfields)
    print(f"\nwrote {len(objects):,} objects, {len(artists):,} artists, {len(traditions):,} tradition cells "
          f"to {OUT_DIR}")
    if UNREACHABLE:
        print(f"failed requests by source: {dict(UNREACHABLE)}")
    report(objects, artists, traditions)


if __name__ == "__main__":
    main()
