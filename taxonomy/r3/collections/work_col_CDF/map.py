import csv, re, sys, collections
B = '/home/user/Visual-Entertainment-Taxonomy/taxonomy/r3/collections/'
rows = list(csv.DictReader(open(B + 'in_col_CDF.csv')))

def S(p, s, fl=re.I):
    return re.search(p, s, fl) is not None

# ---------- manuscripts file: explicit label regexes ----------
MAN = [
 (r'^Western European manuscripts, Gothic', 'C2-29'),
 (r'^Western European manuscripts', 'general:C'),
 (r'^Byzantine / Greek|^Byzantine,', 'A1-16'),
 (r'^Post-Byzantine', 'general:C'),
 (r'Hebrew: Second Temple', 'exclude:Dead Sea text scrolls'),
 (r'^Hebrew', 'C2-26'),
 (r'Islamic book arts: Arabic', 'C2-2'),
 (r'Islamic book arts: Persianate', 'A1-2'),
 (r'Islamic book arts: Ottoman', 'A1-3'),
 (r'Islamic book arts: Maghrebi', 'C1-2'),
 (r'^Dunhuang', 'C2-10'),
 (r'^Tibetan manuscripts', 'missing:Tibetan manuscript illumination'),
 (r'^Armenian', 'A1-20'),
 (r'^Romanesque', 'C2-24'),
 (r'Balinese lontar', 'C2-6'),
 (r'^Javanese manuscripts', 'C2-6'),
 (r'^French late Gothic|^Italian Renaissance|^German / Austrian late Gothic|^Iberian late Gothic', 'C2-25'),
 (r'^Chinese illustrated manuscripts', 'general:C'),
 (r'^Japanese manuscripts and Nara-ehon', 'A1-14'),
 (r'^Japanese emaki', 'A2-8'),
 (r'^Japanese illustrated sutras', 'C2-12'),
 (r'^Ethiopian', 'C2-14'),
 (r'^Gothic:|^International Gothic|^English late medieval', 'C2-29'),
 (r'^Ancient Egyptian papyri', 'C2-15'),
 (r'^Graeco-Roman Egyptian papyri', 'exclude:documentary papyri'),
 (r'^Mexican / New Spain|^Andean colonial', 'exclude:alphabetic text manuscripts'),
 (r'^Mesoamerican codices, colonial', 'A1-19'),
 (r'^Borgia', 'A1-17'), (r'^Mixtec codices', 'A1-18'), (r'^Maya codices', 'C2-16'),
 (r'^Coptic', 'missing:Coptic manuscript illumination'),
 (r'^Syriac', 'missing:Syriac manuscript illumination'),
 (r'^Old Rus', 'C2-27'),
 (r'^South Slavic', 'missing:South Slavic manuscript illumination'),
 (r'^Georgian', 'C1-8'),
 (r'^Aramaic', 'exclude:text scrolls'),
 (r'^Samaritan|^Mandaic|^Sogdian|^Bamum|^Croatian Glagolitic|^Central and Eastern European|^Hindi|^South Asian manuscripts|^Indonesian manuscripts|^Sanskrit', 'general:C'),
 (r'^Flemish', 'C2-30'),
 (r'^Islamic Nusantara', 'C2-4'),
 (r'^Bugis', 'missing:Lontara manuscripts (Bugis-Makassar)'),
 (r'^Korean', 'C2-11'),
 (r'^Mongolian', 'C1-7'),
 (r'^Insular', 'C2-18'), (r'^Ottonian', 'C2-21'), (r'^Carolingian', 'C2-20'),
 (r'^Anglo-Saxon', 'C2-22'), (r'^Late Antique', 'C2-17'), (r'^Merovingian', 'C2-19'),
 (r'^Burmese parabaik and kammavaca', 'C2-8'),
 (r'^Thai samut', 'C2-7'), (r'^Mozarabic', 'C2-23'),
 (r'^Rajput', 'A1-7'), (r'^Jain', 'A1-9'), (r'^Assamese', 'A1-11'),
 (r'^South Indian palm-leaf|^Nepalese \(Newar\) manuscripts|^Sinhal|palm-leaf', 'C2-5'),
]

PLAINS = r"Sioux|Lakota|Dakota|Tsitsistas|Cheyenne|Inunaina|Arapaho|Apsáalooke|Crow|Blackf|Niitsitapii|Pikuni|Kainai|Siksika|Kiowa|Niuam|Comanche|Assiniboine|Plains Cree|Prairie Cree|Shoshone|Bannock|\bUte\b|Osage|Ponca|Omaha|Pawnee|Mandan|Numakiki|Hidatsa|Minitari|Arikara|Sahnish|Gros Ventre|A'aninin|Kaw \(|\bOto\b|^Iowa|Sarcee|Tsuu T'ina|Plains Apache|Wichita|^Plains$|Plains \(attributed|Southern Plains|Northern Plains|Plains Ojibwa|Caddo$|Saulteaux|^Sicangu|Oglala|Hunkpapa|Minneconjou|Ihanktonwan|Wahpeton|Sisitonwan"
HAUD = r"Seneca|Mohawk|Tuscarora|Onondaga|Oneida|Cayuga|Iroquois"
GLAKES = r"Chippewa|Ojibwa|Anishinaabe|Potawatomi|Menominee|Ho-Chunk|Winnebago|Meskwaki|Sac and Fox|Odawa|Kickapoo|Shawnee|Miami|Delaware|Lenape|Wendat|Huron|Peoria|Mohegan|Niantic|Mi'kmaq|Penobscot|Passamaquoddy"
SUBARC = r"Cree|Innu|Naskapi|Mushuaunnuat|Dene|Gwich'in|Slavey|Deh Gah|Tahltan|Kaska|Chipewyan|Denésoliné|Tanana|Ktunaxa|Kootenai"
PLATEAU = r"Nez Perce|Niimíipuu|Umatilla|Yakama|Klikitat|Warm Springs|Salish \(Flathead\)|Nlaka'pamux"
ALASKA = r"Iñupiaq|Yup'ik|Yupik|Cup'ik|Cu'pig|Unangax|Aleut|Kuskwogmiut|Nunivagmiut"
CANINUIT = r"Inuit|Inuvialuit|Kalaallit|Tunumiit|Inughuit|Iglulingmiut|Netsilingmiut|Baffinland|Sallirmiut|Labrador"
NWC = r"Tlingit|Haida|Kwakwaka|Nuu-chah-nulth|Nuxalk|Tsimshian|Nisga'a|Makah|Quinault|Gwawa'enux"
TOOLS = r"hammer|maul|abrader|grinding|axe|adze|scraper|arrow|harpoon|sinker|net weight|knife|drill|chisel|pestle|mortar|crampon|whetstone|lamp|blade|hoe|flake|debitage|straightener|polishing|needle|toggle|wick|snow knife|whip|crochet|float plug|tightener|bola|sling stone|worked stone|unidentifiable|disc-shaped|cone-shaped|perforated|grooved|pitted|club head|spherical|work surface|foreshaft|pounder|beater|spear|bag handle|hair comb|comb|pointed object|biface|cache blade|boatstone|bannerstone|metate|stone$"

def smiths(lab, fam, sam):
    L = lab; s = sam.lower()
    if S(r'Non-Indian', L): return 'exclude:non-Native trade goods'
    if S(r'Multiple archaeological cultures', L): return 'exclude:mixed archaeological bucket'
    if S(r'Liangzhu|Longshan', L): return 'D3-3'
    if S(r'^Buddhists', L): return 'general:D'
    if S(r'^Chinese$', L): return 'general:' + fam
    if S(r'Middle Easterners|Europeans|Egyptians|Southeast Asians', L): return 'general:F'
    if S(r'Muslims', L): return 'general:' + fam
    if S(r'^Native Americans$|^North America$|^Native North American', L): return 'general:H' if fam in 'FC' else 'general:D'
    if S(r'Himalayan peoples', L): return 'general:C'
    # miniatures / models (family C)
    if fam == 'C':
        if S(r'basket', s):
            for p, c in [(r'Pomo', 'H8-12'), (r'Choctaw', 'H8-21'), (r"O'odham|Pima|Papago", 'H8-19'), (r'Passamaquoddy', 'H8-22'), (r'Hopi', 'H8-20')]:
                if S(p, L): return c
            return 'general:H'
        if S(r'vessel|bowl|plate|casket', s):
            for p, c in [(r'Acoma', 'E1-67'), (r'Hopi', 'E1-68'), (r'Santa Clara', 'E1-69'), (r'Zuni|A:shiwi', 'E1-66'), (r'Mimbres', 'E1-62'), (r'Cibola|Anasazi', 'E1-61'), (r'Chimú', 'E1-49')]:
                if S(p, L): return c
            return 'general:E'
        if S(r'moccasin|poncho|bag', s): return 'general:H'
        if S(r'Miniature Mask', sam): return 'D4-18'
        return 'exclude:ethnographic models/miniatures'
    if S(r'archaeolog', L):
        # archaeological cultures
        if fam == 'D' and not S(TOOLS, s) and S(r'figure|sculpture|mask|head|fetish|maskette|eccentric', s):
            for p, c in [(r'\bMaya', 'D5-63'), (r'Aztec', 'D5-64'), (r'Veracruz', 'D5-65'), (r'Olmec', 'D5-62'), (r'Chican|Chicoid', 'D6-5'), (r'Mixtec|Zapotec|Mesoamerica|Mexico|Puebla|Ostionoid|Teotihuac|Manteño|Mezcala', 'general:D'), (r'Hopi|Zuni|A:shiwi', 'D5-79')]:
                if S(p, L): return c
            return 'general:D'
        if S(r'pipe', s) and S(r'Woodland|Northeast|Southeast|Adena|Hopewell', L): return 'D6-7'
        if S(r'Maya', L) and S(r'eccentric', s): return 'D5-63'
        return 'exclude:archaeological tools'
    if fam == 'D':
        if S(r'Zuni|A:shiwi', L): return 'D5-79'
        if S(r'Cochiti', L): return 'D5-80'
        if S(r'Hopi', L) and S('mask', s): return 'D5-78'
        if S(r'Otomí', L): return 'A6-14'
        if S(r'Nuu-chah-nulth', L) and S('mask', s): return 'D4-24'
        if S(ALASKA, L):
            if S(r'mask', s): return 'D4-25'
            return 'D2-9'
        if S(r'Inuit \[', L) and not S(TOOLS, s): return 'D5-77'
        if S(r'^Inuit$', L): return 'D5-77'
        if S(r'Tuscarora', L): return 'general:D'
        if S(TOOLS + r'|war club|tomahawk|letter opener|pipe|equipment|bundle|headband|tobacco|bag|toy|model|figure|bison', s): return 'exclude:ethnographic tools'
        return 'general:D'
    if fam == 'F':
        if S(r'Zuni|A:shiwi', L): return 'G3-16'
        if S(r'Diné|Navajo', L): return 'G3-15'
        if S(r'Mapuche', L): return 'G3-14'
        if S(r'Pomo', L) and S('basket', s): return 'H8-12'
        if S(r'Modoc|Washoe|Mono|Kutzadika|Hupa|Karuk|Paiute', L) and S('basket', s): return 'H8-13'
        if S(r'Umatilla|Klikitat', L) and S('bag', s): return 'H8-16'
        if S(HAUD, L): return 'H9-7'
        if S(PLATEAU, L): return 'missing:Plateau beadwork'
        if S(r'Huron|Wendat', L) and S('moccasin', s): return 'H4-40'
        if S(PLAINS, L): return 'H9-6'
        if S(r'Taos', L): return 'H9-6'
        if S(GLAKES + r'|Great Lakes', L): return 'missing:Great Lakes floral beadwork'
        if S(SUBARC, L): return 'missing:Subarctic beadwork'
        if S(r'Wixarika|Huichol', L): return 'missing:Huichol beadwork'
        if S(r'Aymara|Quechua', L): return 'H2-7'
        if S(r"K'iche'", L): return 'general:H'
        return 'general:H'
    return None

def east(lab, fam, sam):
    m = re.match(r'(Japan|China|Korea) · ?(.*)', lab)
    if not m: return None
    c, p = m.group(1), m.group(2)
    s = sam
    if fam == 'C':
        if c == 'Japan':
            if S(r'Nara|8世紀|12世紀|12～13|16世紀', p) or S(r'kyō|sutra|Sutra|経', s): return 'C2-12'
            if S(r'^\d{4}$|^c\. 1|century|^n\.d\.|Reproduction|1615-1867|^1[78]', p) or S(r'^Ehon|gafu|gakyô|gakyo|Ehon', s): return 'missing:Ehon (Japanese woodblock-printed books)'
            return 'C1-10'
        if c == 'China': return 'C1-9'
        if c == 'Korea':
            if S(r'Goryeo', p): return 'C2-12'
            return 'C1-13'
    if fam == 'D':
        if c == 'Japan':
            if S(r'No Mask|Noh|Bugaku|^面$', s): return 'missing:Noh masks' if not S('Bugaku', s) else 'missing:Bugaku masks'
            if S(r'Edo|Momoyama|Muromachi|17～19|現代', p) and S(r'mask|Mask|面', s): return 'missing:Noh masks'
            if S(r'Nara', p) and S('Gigaku', s): return 'missing:Gigaku masks'
            if S(r'Heisei|16～17', p): return 'general:D'
            if p == '': return 'general:D'
            return 'D5-24'
        if c == 'China':
            if S(r'Shang|Zhou|Neolithic|Unknown|Warring', p): return 'D3-3' if not S('Cranes|Stele', s) else 'general:D'
            if S(r'Han', p): return 'D5-21' if S('Model', s) else 'general:D'
            return 'D5-22'
        if c == 'Korea':
            if S(r'Baekje', p) or S('Pedestal', s): return 'general:D'
            return 'D5-23'
    if fam == 'F':
        if c == 'China': return 'missing:Qing imperial glass (Peking glass)'
        if c == 'Korea' and S('Silla', p): return 'missing:Silla glass'
        return 'general:F'
    return None

ISL = [
 (r'Mamluk', {'F': 'F3-1', 'C': 'C2-2', 'D': 'general:D'}),
 (r'Abbasid', {'F': 'F2-1', 'C': 'C2-1'}),
 (r'Fatimid', {'F': 'general:F', 'D': 'general:D'}),
 (r'Nasrid', {'D': 'D1-2'}),
 (r'Qajar', {'F': 'missing:Persian blown glass (Shiraz)', 'C': 'A5-1'}),
 (r'Safavid|Timurid|Ilkhanid|^Iran', {'C': 'A1-2'}),
 (r'Seljuq', {'C': 'C2-2', 'D': 'general:D'}),
 (r'Ottoman · Ottoman Istanbul', {'C': 'B1-1'}),
 (r'Ottoman', {'C': 'C3-1', 'F': 'general:F'}),
 (r'Deccani|Hyderabad|Bijapur|Golconda', {'C': 'A1-5'}),
 (r'[Cc]ompany', {'C': 'A1-6'}),
 (r'Mughal|Lucknow|Murshidabad|Lahore|Agra', {'C': 'A1-4', 'F': 'missing:Mughal glass', 'D': 'general:D'}),
 (r'Kashmir', {'C': 'general:C'}),
 (r'^Spain', {'C': 'C1-2', 'D': 'general:D'}),
 (r'^Egypt', {'C': 'C3-1', 'F': 'general:F', 'D': 'general:D'}),
 (r'Umayyad|Hammadid|Islamic Spain', {'D': 'general:D'}),
 (r'ISLAM|Islam|Syria', {'F': 'general:F', 'D': 'general:D'}),
]

def islamic(lab, fam, sam):
    if lab == 'Qajar' and fam == 'C' and S('Mirror', sam): return 'I2-1'
    if lab == 'Murshidabad' and fam == 'D': return 'missing:Murshidabad ivory carving'
    for p, d in ISL:
        if S(p, lab, 0):
            return d.get(fam, 'general:' + fam)
    return None

def europe(lab, fam, sam):
    if lab.startswith('wd:'):
        return {'wd:Q1799758': 'I2-21', 'wd:Q1268796': 'I2-19', 'wd:Q1799759': 'I2-20'}.get(lab)
    if lab.startswith('pattern:'):
        return {'old_russian_manuscript_illumination': 'C2-27', 'chukchi_walrus_ivory_engraving_uelen': 'D2-14',
                'tobolsk_bone_carving': 'D2-15', 'kholmogory_bone_carving': 'missing:Kholmogory bone carving',
                'georgian_manuscript_illumination': 'exclude:postcard reproductions',
                'serbian_manuscript_illumination': 'exclude:bookplates, not manuscripts',
                'old_believer_pomor_vyg_book_painting': 'missing:Vyg (Pomor) Old Believer book painting'}.get(lab[8:])
    m = re.match(r'people:([a-z_]+):(\w+)', lab)
    if not m: return None
    pe, kind = m.groups()
    if kind == 'manuscript_illumination': return 'exclude:mis-typed ethnographic objects'
    if kind == 'glass': return 'exclude:everyday glassware, no tradition'
    if kind == 'lacquer_miniature': return 'general:I'
    if kind == 'bone_carving':
        if pe == 'chukchi': return 'D2-14'
        if pe == 'yakut_sakha': return 'D2-16'
        if pe == 'sami': return 'D2-13'
        if pe in ('khanty', 'mansi', 'nenets', 'evenk', 'koryak', 'nanai', 'buryat', 'georgian', 'dagestani_general', 'azerbaijani', 'ukrainian', 'adyghe_circassian_kabardian', 'lak'): return 'general:D'
        return 'exclude:everyday objects, no tradition'
    return None

if __name__ == '__main__':
    pass
