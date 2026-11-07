"""Build result.json + merges.csv for the missing_traditions pass (run from repo root)."""
import json, csv, os, urllib.parse as up
OUT = os.path.dirname(os.path.abspath(__file__))

def W(t): return "https://en.wikipedia.org/wiki/" + t
def r(name, group, gloss, t, maker=0):
    url = t if t.startswith("http") else W(t)
    return [name, group, gloss, "r3 " + url, maker]
q = up.quote_plus
def SI(term, what): return ["https://collections.si.edu/search/results.htm?q=" + q(term), f"Smithsonian collections search: {term}", what]
def MET(term, what): return ["https://www.metmuseum.org/art/collection/search?q=" + q(term), f"The Met collection: {term}", what]
def CMA(term, what): return ["https://www.clevelandart.org/art/collection/search?search=" + q(term), f"Cleveland Museum of Art: {term}", what]
def VAM(term, what): return ["https://collections.vam.ac.uk/search/?q=" + q(term), f"V&A collections: {term}", what]
def BM(term, what): return ["https://www.britishmuseum.org/collection/search?keyword=" + q(term), f"British Museum collection: {term}", what]
def RIJ(term, what): return ["https://www.rijksmuseum.nl/en/collection/search?query=" + q(term), f"Rijksmuseum collection: {term}", what]
def COLBASE(term, what): return ["https://colbase.nich.go.jp/collection_items?locale=en&keyword=" + q(term), f"ColBase (Japan's national museums): {term}", what]
def PENN(term, what): return ["https://www.penn.museum/collections/search.php?term=" + q(term), f"Penn Museum collections: {term}", what]
ORO = ["https://www.banrepcultural.org/museo-del-oro", "Museo del Oro, Bogotá", "Colombia's national collection of pre-Hispanic goldwork and pottery"]
TEPAPA = ["https://collections.tepapa.govt.nz/", "Te Papa Collections Online", "New Zealand's national museum collection, including taonga Māori"]
EMUSEUM = ["https://www.emuseum.go.kr/", "e-Museum (Korea's national museums)", "integrated collection database of Korea's national and public museums"]
WERELD = ["https://collectie.wereldculturen.nl/", "Wereldculturen collection (NMVW)", "Museum Volkenkunde, Tropenmuseum, Afrika Museum and Wereldmuseum Rotterdam"]
QB = ["https://www.quaibranly.fr/en/collections/", "Musée du quai Branly collections", "French national collection of the arts of Africa, Oceania and the Americas"]
BCCR = ["https://www.museosdelbancocentral.org/", "Museos del Banco Central de Costa Rica", "Costa Rica's national collections of pre-Columbian gold and ceramics"]
LARCO = ["https://www.museolarco.org/", "Museo Larco, Lima", "major Peruvian collection of ancient Andean ceramics, online catalogue"]
INAH = ["https://mediateca.inah.gob.mx/", "Mediateca INAH", "Mexico's national archaeological and ethnographic collections online"]
PRECOL = ["https://precolombino.cl/", "Museo Chileno de Arte Precolombino", "Chile's museum of pre-Columbian art and its collection"]
CMH = ["https://www.historymuseum.ca/collections/", "Canadian Museum of History collections", "Canada's national collection of Indigenous material culture"]
BNF = ["https://archivesetmanuscrits.bnf.fr/", "BnF Archives et manuscrits", "catalogue of the manuscript departments of the Bibliothèque nationale de France"]
FLMNH = "https://www.floridamuseum.ufl.edu/latinarch/catalog/intermediate-area-artifacts/"

LEAVES = []
def L(key, sub, label, breadth, defn, aliases, see, src, cats, axis, kinds, cf):
    LEAVES.append({"key": key, "sub": sub, "label": label, "breadth": breadth, "defn": defn, "aliases": aliases,
                   "see": see, "src": [[W(s) if not s.startswith("http") else s, "Wikipedia" if not s.startswith("http") else "museum"] for s in src],
                   "catalogues": cats, "axis": axis, "kinds": kinds, "collections_from": cf})

ST, SP, CW, MK = "Sub-types", "Schools & phases", "Centres & workshops", "Makers"
AX_OBJ = "sub-types first, then phases, then centres and sites; holding institutions attach from the collections index"

# ---------------- A Painting ----------------
L("FLATSTYLE", "A5", "Flatstyle", "medium",
  "Twentieth-century Native American easel painting in opaque watercolour with flat, outlined colour and little shading or perspective, showing dances, ceremonies and daily life: the San Ildefonso watercolourists (1910s), Hopi painters, the Kiowa Six (Southern Plains style), Dorothy Dunn's Studio at the Santa Fe Indian School (1932–62) and the Bacone school.",
  "Flat style; Traditional Indian painting; Studio style; Pueblo painting; Kiowa style; Southern Plains style",
  "Ledger Art; Plains Hide Painting", ["Flatstyle", "Studio_style", "Kiowa_Six"],
  [SI("Kiowa painting", "Native American paintings in the Smithsonian (NMAI) and American Art Museum"),
   ["https://americanart.si.edu/search?query=" + q("Native American painting"), "Smithsonian American Art Museum search", "Native American easel paintings in SAAM"],
   ["https://philbrook.org/", "Philbrook Museum of Art", "Tulsa museum founded on the Native American painting annuals; major Flatstyle holdings"]],
  "artist-led: by named school in order of emergence — San Ildefonso school, Hopi painters, Kiowa Six, Studio style, Bacone school; artists by birth within each",
  [r("Julian Martinez", "San Ildefonso school", "San Ildefonso Pueblo painter and potter (1879–1943); early watercolours of dances", "Julian_Martinez", 1),
   r("Jose Encarnacion Peña", "San Ildefonso school", "San Ildefonso painter (1902–1979), one of the first Pueblo watercolourists", "Jose_Encarnacion_Peña", 1),
   r("Awa Tsireh", "San Ildefonso school", "Alfonso Roybal (1898–1955), San Ildefonso watercolourist of ceremonial dances", "Awa_Tsireh", 1),
   r("Tonita Peña", "San Ildefonso school", "San Ildefonso/Cochiti painter (1893–1949), first Pueblo woman painter of note", "Tonita_Peña", 1),
   r("Velino Shije Herrera", "San Ildefonso school", "Zia Pueblo painter (1902–1973) of the Santa Fe 'self-taught' generation", "Velino_Shije_Herrera", 1),
   r("Fred Kabotie", "Hopi painters", "Hopi painter (1900–1986) of katsina dances; Painted Desert Inn murals", "Fred_Kabotie", 1),
   r("Otis Polelonema", "Hopi painters", "Hopi painter (1902–1981), contemporary of Kabotie at the Santa Fe Indian School", "Otis_Polelonema", 1),
   r("Waldo Mootzka", "Hopi painters", "Hopi painter (1903–1940) of katsina and Snake Dance scenes", "Waldo_Mootzka", 1),
   r("Stephen Mopope", "Kiowa Six", "Kiowa painter and muralist (1898–1974), founder of the Kiowa (Southern Plains) style", "Stephen_Mopope", 1),
   r("Jack Hokeah", "Kiowa Six", "Kiowa painter and dancer (1900–1969)", "Jack_Hokeah", 1),
   r("Monroe Tsatoke", "Kiowa Six", "Kiowa painter (1904–1937) of Peyote and dance subjects", "Monroe_Tsatoke", 1),
   r("Spencer Asah", "Kiowa Six", "Kiowa painter (1905–1954); Anadarko murals with Mopope", "Spencer_Asah", 1),
   r("James Auchiah", "Kiowa Six", "Kiowa painter (1906–1974); Department of the Interior murals", "James_Auchiah", 1),
   r("Lois Smoky Kaulaity", "Kiowa Six", "Kiowa painter and beadworker (1907–1981), the group's only woman", "Lois_Smoky_Kaulaity", 1),
   r("Geronima Cruz Montoya", "Studio style", "Ohkay Owingeh painter (1915–2015), Dunn's successor at the Studio, Santa Fe", "Geronima_Cruz_Montoya", 1),
   r("Pablita Velarde", "Studio style", "Santa Clara Pueblo painter (1918–2006), Studio student; earth-pigment paintings", "Pablita_Velarde", 1),
   r("Pop Chalee", "Studio style", "Taos Pueblo painter (1906–1993) of 'enchanted forest' scenes; Studio student", "Pop_Chalee", 1),
   r("Harrison Begay", "Studio style", "Diné (Navajo) painter (1914/17–2012), Studio student", "Harrison_Begay", 1),
   r("Gerald Nailor", "Studio style", "Diné painter (1917–1952); Navajo Nation Council Chamber murals", "Gerald_Nailor", 1),
   r("Quincy Tahoma", "Studio style", "Diné painter (1920–1956), Studio student", "Quincy_Tahoma", 1),
   r("Allan Houser", "Studio style", "Chiricahua Apache painter and sculptor (1914–1994), Studio student", "Allan_Houser", 1),
   r("Joe Herrera", "Studio style", "Cochiti painter (1923–2001), Studio student who moved to abstraction", "Joe_Herrera", 1),
   r("Oscar Howe", "Studio style", "Yanktonai Dakota painter (1915–1983), Studio student, later broke with the style", "Oscar_Howe", 1),
   r("Acee Blue Eagle", "Bacone school", "Muscogee/Pawnee painter (1907–1959), first head of Bacone College's art department", "Acee_Blue_Eagle", 1),
   r("Woody Crumbo", "Bacone school", "Potawatomi painter (1912–1989), Bacone art director 1938–41", "Woody_Crumbo", 1),
   r("Solomon McCombs", "Bacone school", "Muscogee painter (1913–1980) of the Bacone style", "Solomon_McCombs", 1),
   r("Fred Beaver", "Bacone school", "Muscogee/Seminole painter (1911–1980) of the Bacone style", "Fred_Beaver", 1),
   r("Jerome Tiger", "Bacone school", "Muscogee/Seminole painter (1941–1967), late Bacone style", "Jerome_Tiger", 1)],
  ["Pueblo Painting", "Native American Studio Painting", "Kiowa Six"])

L("NEPMS", "A1", "Nepalese Manuscript Painting", "medium",
  "Paintings on the palm-leaf folios and wooden covers of Buddhist and Hindu manuscripts made by Newar artists of the Kathmandu Valley from the 11th century, in the Pala-derived style that fed Tibetan painting: illustrated Prajnaparamita and Pancharaksha manuscripts, painted book covers.",
  "Newar manuscript painting; Nepali illuminated manuscripts", "Paubha; Palm-Leaf Manuscripts; Pala Art",
  ["Nepalese_painting", "Newar_art"],
  [CMA("Nepal manuscript cover", "Nepalese manuscript covers and folios at Cleveland"),
   VAM("Nepal manuscript", "Nepalese manuscripts and covers at the V&A"),
   ["https://www.himalayanart.org/", "Himalayan Art Resources", "image database of Himalayan and Newar art"]],
  "sub-types (manuscript texts) first, then phases by dynasty",
  [r("Prajnaparamita manuscripts", ST, "illustrated Perfection of Wisdom sutras, the chief illuminated text of Newar workshops", "Prajnaparamita"),
   r("Pancharaksha manuscripts", ST, "texts of the five protective goddesses with their painted images", "Pancharaksha"),
   r("Gandavyuha manuscripts", ST, "illustrated Gandavyuha Sutra folios", "Gandavyuha_Sutra"),
   r("Painted manuscript covers", ST, "wooden covers (book boards) painted with deities and narratives", "Book_covers"),
   r("Thakuri period", SP, "11th–12th-century transitional period of the earliest dated Nepalese illuminated manuscripts", "Thakuri_dynasty"),
   r("Malla period", SP, "Newar manuscript painting under the Malla kings, 13th–18th century", "Malla_(Nepal)")],
  ["Nepalese Manuscript Painting"])

L("GORYEOBP", "A2", "Goryeo Buddhist Painting", "narrow",
  "Buddhist hanging scrolls painted in mineral colours and gold on silk in Goryeo Korea, chiefly 13th–14th century, often coloured from both sides of the silk, most now in Japanese temples: Water-Moon Avalokiteshvara, Amitabha triads, Ksitigarbha, arhats.",
  "Goryeo bulhwa", "Korean Buddhist Sculpture; Sutra Copying", ["Goryeo_Buddhist_paintings"],
  [EMUSEUM, COLBASE("高麗仏画", "Goryeo Buddhist paintings in Japan's national museums"),
   MET("Goryeo Buddhist painting", "Goryeo paintings at the Met")],
  "sub-types by iconography, then named painters",
  [r("Water-Moon Avalokiteshvara", ST, "Suwol Gwaneum, the bodhisattva seated on a rock by water; the type most associated with Goryeo", "Goryeo_Buddhist_paintings"),
   r("Amitabha", ST, "Amitabha Buddha alone or in triads, welcoming souls to the Pure Land", "Amitabha"),
   r("Ksitigarbha", ST, "Jijang bodhisattva with monk's staff, often with the Ten Kings", "Goryeo_Buddhist_paintings"),
   r("Hyeheo", MK, "Goryeo monk-painter (14th c.) of the Water-Moon Avalokiteshvara at Sensō-ji, Tokyo", "Goryeo_Buddhist_paintings", 1)],
  ["Goryeo Buddhist Painting"])

# ---------------- B / C ----------------
L("EHON", "B2", "Ehon", "medium",
  "Japanese woodblock-printed picture books of the Edo and Meiji periods, from illustrated tales to colour-printed kyōka anthologies, painting manuals and sketchbooks: Moronobu's picture books, Utamaro's Picture Book of Selected Insects (1788), the Hokusai Manga.",
  "e-hon; Japanese illustrated books; ehon picture books", "Ukiyo-e; Nara-ehon", ["Ehon", "Kusazōshi"],
  [["https://www.artic.edu/collection?q=ehon", "Art Institute of Chicago: ehon", "the AIC holds over a thousand Japanese printed books"],
   ["https://www.britishmuseum.org/collection/search?keyword=ehon", "British Museum: ehon", "Japanese illustrated books in the BM"],
   ["https://ukiyo-e.org/", "Ukiyo-e.org", "search engine of Japanese woodblock prints across museums"]],
  "sub-types (book formats) first, then makers by date",
  [r("Kusazōshi", ST, "popular illustrated fiction in small-format booklets", "Kusazōshi"),
   r("Kibyōshi", ST, "'yellow-cover' satirical picture books, 1775–1806", "Kibyōshi"),
   r("Hokusai Manga", ST, "Hokusai's sketchbook-manual in 15 volumes (1814–1878), the best-known gafu (painting manual)", "Hokusai_Manga"),
   r("Hishikawa Moronobu", MK, "Edo designer (1618–1694) who made the illustrated book a popular art", "Hishikawa_Moronobu", 1),
   r("Nishikawa Sukenobu", MK, "Kyoto designer (1671–1750) of picture books of women", "Nishikawa_Sukenobu", 1),
   r("Kitao Shigemasa", MK, "Edo designer (1739–1820) of colour picture books", "Kitao_Shigemasa", 1),
   r("Tsutaya Jūzaburō", MK, "Edo publisher (1750–1797) of Utamaro's ehon", "Tsutaya_Jūzaburō", 1),
   r("Kitagawa Utamaro", MK, "designer (c. 1753–1806) of the insect, shell and bird ehon of the 1780s–90s", "Kitagawa_Utamaro", 1),
   r("Katsushika Hokusai", MK, "designer (1760–1849) of the Manga and One Hundred Views of Mount Fuji", "Katsushika_Hokusai", 1),
   r("Kawanabe Kyōsai", MK, "Meiji painter-designer (1831–1889) of illustrated books", "Kawanabe_Kyōsai", 1)],
  ["Ehon (Japanese woodblock-printed books)"])

L("TIBMS", "C2", "Tibetan Manuscript Illumination", "medium",
  "Illuminated and illustrated Tibetan books in the long pothi format, from the Dunhuang finds (8th–10th c.) to the gold-and-silver on indigo-paper Kangyur and Tengyur sets of monasteries, with painted miniatures of deities and carved and painted book covers.",
  "Tibetan illuminated manuscripts; pecha", "Thangka; Dunhuang Manuscripts", ["Pecha", "Kangyur"],
  [BNF, ["https://www.himalayanart.org/", "Himalayan Art Resources", "image database of Tibetan art including manuscript folios and covers"],
   VAM("Tibetan manuscript", "Tibetan manuscripts and book covers at the V&A")],
  "sub-types (canonical sets and book parts) first, then centres",
  [r("Kangyur", ST, "the translated words of the Buddha, copied in illuminated multi-volume sets", "Kangyur"),
   r("Tengyur", ST, "the translated treatises, the second half of the canon", "Tengyur"),
   r("Pecha", ST, "loose-leaf oblong book format wrapped between wooden covers", "Pecha"),
   r("Dunhuang Tibetan manuscripts", ST, "Tibetan texts from the Library Cave, Dunhuang (Pelliot and Stein collections)", "Dunhuang_manuscripts"),
   r("Tholing Monastery", CW, "Guge royal monastery, western Tibet, a centre of early illumination", "Tholing_Monastery"),
   r("Tabo Monastery", CW, "Spiti monastery with 11th-century manuscripts", "Tabo_Monastery"),
   r("Gyantse", CW, "15th-century centre of painting and book production in Tsang", "Gyantse")],
  ["Tibetan manuscript illumination"])

L("COPTMS", "C2", "Coptic Manuscript Illumination", "narrow",
  "Illuminated and decorated manuscripts in Coptic (Sahidic and Bohairic) of the Egyptian church, from the 4th century onward: interlace frontispieces, ornamented initials and full-page saints, from the White Monastery, the Hamuli (Fayum) library and the Wadi Natrun monasteries.",
  "Coptic illuminated manuscripts", "Coptic Textiles; Ethiopian Manuscripts", ["Coptic_art", "Coptic_language"],
  [BNF, ["https://www.themorgan.org/", "Morgan Library & Museum", "holds the Hamuli Coptic manuscripts (9th–10th c.)"],
   BM("Coptic manuscript", "Coptic manuscripts and papyri in the British Museum")],
  "centres (monastic libraries) by date; then named manuscripts' collections",
  [r("White Monastery", CW, "Shenoute's monastery at Sohag, whose library yielded many Sahidic codices", "White_Monastery"),
   r("Hamuli manuscripts", CW, "library of the Monastery of St Michael, Fayum, 9th–10th c.; Morgan Library", "Hamuli"),
   r("Monastery of Saint Macarius the Great", CW, "Wadi Natrun monastery, source of Bohairic manuscripts", "Monastery_of_Saint_Macarius_the_Great"),
   r("Glazier Codex", CW, "4th–5th-century Coptic Acts with a crux ansata frontispiece; Morgan Library", "Glazier_Codex")],
  ["Coptic manuscript illumination"])

L("SYRMS", "C2", "Syriac Manuscript Illumination", "narrow",
  "Illuminated manuscripts of the Syriac churches of Mesopotamia and Syria from the 6th century: canon tables and full-page miniatures, as in the Rabbula Gospels (586), the Syriac Bible of Paris and the Jacobite lectionaries of Tur Abdin and Mosul (12th–13th c.).",
  "Syriac illuminated manuscripts", "Late Antique Illumination; Armenian Manuscript Illumination", ["Rabbula_Gospels", "Syriac_Christianity"],
  [BNF, ["https://hmml.org/", "Hill Museum & Manuscript Library", "vHMML: digitised Syriac manuscripts of the Middle East"],
   ["https://www.bl.uk/", "British Library", "the largest Syriac manuscript collection in Europe"]],
  "named manuscripts' traditions and centres by date",
  [r("Rabbula Gospels", ST, "illuminated Syriac Gospel book of 586, Biblioteca Laurenziana, Florence", "Rabbula_Gospels"),
   r("Syriac Bible of Paris", ST, "6th–7th-century illustrated Peshitta Old Testament, BnF syr. 341", "Syriac_Bible_of_Paris"),
   r("Tur Abdin", CW, "monastic region of south-east Anatolia producing illuminated lectionaries", "Tur_Abdin"),
   r("Mar Mattai Monastery", CW, "monastery near Mosul, a centre of 12th–13th-century Syriac illumination", "Mar_Mattai_Monastery")],
  ["Syriac manuscript illumination"])

# ---------------- D Sculpture ----------------
L("NOHMASK", "D4", "Noh Masks", "medium",
  "Carved and painted hinoki masks (omote) of Noh and Kyōgen theatre, from the 14th century, in fixed types for old men, women, demons and gods, made by hereditary carver lines and held by Noh schools and temples: ko-omote, hannya, okina, shikami.",
  "nōmen; omote; Noh mask", "Gigaku Masks; Bugaku Masks", ["Noh_mask", "Noh"],
  [COLBASE("能面", "Noh masks in the Tokyo, Kyoto, Nara and Kyushu national museums"),
   ["https://emuseum.nich.go.jp/", "e-Museum (National Treasures and Important Cultural Properties)", "Japan's designated masks from the national museums"],
   CMA("Noh mask", "Noh masks at Cleveland")],
  "sub-types by role category (god, man, woman, madwoman, demon), canonical first",
  [r("Okina", ST, "the old-man god mask with separate jaw, for the ritual Okina play", "Okina_(Noh)"),
   r("Ko-omote", ST, "young-woman mask, the type of the Konparu and Kita schools", "Noh_mask"),
   r("Zō-onna", ST, "dignified woman's mask created by Zōami", "Noh_mask"),
   r("Uba", ST, "old-woman mask", "Noh_mask"),
   r("Wakaotoko", ST, "young-man mask", "Noh_mask"),
   r("Akobujō", ST, "old-man mask with a wrinkled face", "Noh_mask"),
   r("Shikami", ST, "grimacing demon mask", "Noh_mask"),
   r("Hannya", ST, "horned female demon of jealousy", "Hannya")],
  ["Noh masks"])

L("GIGAKU", "D4", "Gigaku Masks", "narrow",
  "Large wooden and dry-lacquer masks covering the whole head, worn in gigaku processional dance-drama introduced from the continent in 612, carved mostly in the 7th–8th centuries and preserved at Hōryū-ji, Tōdai-ji and the Shōsōin: Karura, Kuron, Gokō, Suikoō.",
  "gigakumen", "Noh Masks; Bugaku Masks", ["Gigaku"],
  [COLBASE("伎楽面", "gigaku masks of the Hōryū-ji treasures (Tokyo National Museum) and other national museums"),
   ["https://shosoin.kunaicho.go.jp/en-US/", "Shōsōin Treasures", "the Imperial Household Agency's database of the Shōsōin, including gigaku masks"]],
  "sub-types (characters) first, then the temple treasuries that hold them",
  [r("Karura", ST, "Garuda bird-headed mask", "Karura"),
   r("Kuron", ST, "Kunlun mask of a dark-skinned lustful character", "Kuron"),
   r("Hōryū-ji", CW, "temple whose 7th-century gigaku masks are in the Gallery of Hōryū-ji Treasures, Tokyo", "Hōryū-ji"),
   r("Tōdai-ji", CW, "temple holding masks used at its 752 eye-opening ceremony", "Tōdai-ji"),
   r("Shōsōin", CW, "imperial repository at Nara holding 8th-century gigaku masks", "Shōsōin")],
  ["Gigaku masks"])

L("BUGAKU", "D4", "Bugaku Masks", "narrow",
  "Wooden masks, often with movable eyes or jaws, worn in bugaku court dances of gagaku from the Heian period, preserved at shrines and temples: Ranryō-ō, Nasori, Saisōrō, Ama and Ni-no-mai.",
  "bugakumen", "Gigaku Masks; Noh Masks", ["Bugaku", "Gagaku"],
  [COLBASE("舞楽面", "bugaku masks in Japan's national museums")],
  "sub-types (dance characters) first, then the shrines that hold sets",
  [r("Ranryō-ō", ST, "dragon-crowned mask of the Prince of Lanling dance", "Bugaku"),
   r("Nasori", ST, "mask of the dragon dance paired with Ranryō-ō", "Bugaku"),
   r("Saisōrō", ST, "old-man mask of a slow dance", "Bugaku"),
   r("Itsukushima Shrine", CW, "shrine with a long-preserved bugaku tradition and mask set", "Itsukushima_Shrine"),
   r("Kasuga-taisha", CW, "Nara shrine holding Heian–Kamakura bugaku masks", "Kasuga-taisha")],
  ["Bugaku masks"])

L("MEXMASK", "D4", "Mexican Masks", "medium",
  "Carved and painted wood, papier-mâché and leather masks worn in Mexican dances and carnivals that blend Indigenous and Spanish ritual: Danza de los Viejitos of Michoacán, Parachicos of Chiapa de Corzo, Chinelos of Morelos, Yaqui pascola masks, Moors and Christians dances.",
  "Mexican dance masks; máscaras mexicanas", "Cartonería; Alebrije", ["Mexican_mask-folk_art"],
  [SI("Mexican mask", "Mexican masks in the Smithsonian (NMAI)"), WERELD, INAH],
  "sub-types by dance, then regions",
  [r("Danza de los Viejitos", ST, "'dance of the little old men' of Michoacán, with smiling old-man masks", "Danza_de_los_Viejitos"),
   r("Parachicos", ST, "lacquered wooden masks of the January fiesta of Chiapa de Corzo, Chiapas", "Parachicos"),
   r("Chinelos", ST, "bearded masks of the carnival dancers of Morelos", "Chinelos"),
   r("Pascola", ST, "small carved masks of Yaqui and Mayo pascola dancers, Sonora", "Pascola"),
   r("Moors and Christians", ST, "dance-drama with masks of Spaniards and Moors", "Moors_and_Christians"),
   r("Guerrero", CW, "state with the richest tradition of carved dance masks", "Guerrero"),
   r("Michoacán", CW, "Purépecha state of the Viejitos and Corpus masks", "Michoacán")],
  ["Mexican Dance Masks"])

L("KARAJA", "D5", "Karajá Dolls (Ritxoko)", "narrow",
  "Fired and painted clay figurines made by Karajá women on Bananal Island and the Araguaia River, Brazil, representing people, animals and ritual scenes, registered as Brazilian cultural heritage by IPHAN in 2012.",
  "ritxoko; bonecas Karajá", "Caruaru Clay Figures", ["Karajá_people", "Bananal_Island"],
  [SI("Karaja", "Karajá figures in the Smithsonian (NMAI)"), MET("Karaja", "Karajá figures at the Met")],
  "sub-types first, then centres",
  [r("Ritxoko", ST, "the Karajá name for the figures, made by women and given to girls", "Karajá_people"),
   r("Bananal Island", CW, "river island on the Araguaia, home of the Karajá villages that make the dolls", "Bananal_Island")],
  ["Karajá ceramic dolls"])

L("BAHIA", "D5", "Bahía Figurines", "narrow",
  "Mould-made and hand-modelled ceramic figures of the Bahía culture of coastal Manabí, Ecuador (c. 500 BCE–500 CE): large hollow figures with elaborate headdresses and ear-spools, seated 'Buddha-like' figures and small solid figurines.",
  "Bahía ceramic figures", "Valdivia Figurines; Jama-Coaque Ceramics", ["Bahía_culture"],
  [SI("Bahía culture", "Bahía figures in the Smithsonian (NMAI)"), MET("Bahia Ecuador", "Bahía figures at the Met")],
  "sub-types first, then sites",
  [r("Hollow figures", ST, "large hollow seated and standing figures with headdresses", "Bahía_culture"),
   r("Bahía de Caráquez", CW, "type site of the culture on the Manabí coast", "Bahía_de_Caráquez")],
  ["Bahía ceramic figures"])

L("KUSHSCULP", "D5", "Kushite Sculpture", "medium",
  "Statuary, relief and figurines of the Nubian kingdom of Kush in its Napatan (c. 750–300 BCE) and Meroitic (c. 300 BCE–350 CE) phases, Egyptianising royal statues of the 25th Dynasty and Meroitic ba-statues and temple reliefs: Taharqa sphinx, Jebel Barkal statues, Meroë reliefs.",
  "Napatan sculpture; Meroitic sculpture; Nubian sculpture", "Ancient Egyptian Sculpture; Meroitic Pottery; Nubian Pyramids",
  ["Kingdom_of_Kush", "Napata", "Meroë"],
  [PENN("Meroitic", "Penn Museum's Karanog and Buhen excavation finds"),
   ["https://collections.mfa.org/search/objects/*/Kushite", "MFA Boston collections: Kushite", "the Harvard–MFA excavations of Kerma, Napata and Meroë"],
   BM("Kushite", "Kushite sculpture in the British Museum")],
  "phases first, then centres (royal sites)",
  [r("Twenty-fifth Dynasty", SP, "Kushite pharaohs ruling Egypt (c. 744–656 BCE), patrons of revived classical sculpture", "Twenty-fifth_Dynasty_of_Egypt"),
   r("Meroitic period", SP, "the later kingdom centred on Meroë, with ba-statues and local styles", "Meroitic"),
   r("Jebel Barkal", CW, "sacred mountain and temple complex at Napata, findspot of royal statues", "Jebel_Barkal"),
   r("El-Kurru", CW, "early royal cemetery of Napata", "El-Kurru"),
   r("Nuri", CW, "royal pyramid cemetery begun by Taharqa", "Nuri"),
   r("Meroë", CW, "capital and pyramid field of the Meroitic kingdom", "Meroë")],
  ["Kushite (Napatan-Meroitic) sculpture"])

L("NUCHU", "D6", "Nuchu", "narrow",
  "Small carved wooden human figures (nuchukana) of the Guna of Panama's Guna Yala, made by master carvers and kept in households to cure illness and guard against spirits; many show foreigners in hats and coats.",
  "nuchukana; Kuna curing figures", "Mola", ["Guna_people", "https://maxwellmuseum.unm.edu/maxwell-at-home/objects/object-monday-guna-nuchu"],
  [SI("Guna nuchu", "Guna objects in the Smithsonian (NMAI)"), ["https://maxwellmuseum.unm.edu/", "Maxwell Museum of Anthropology", "Mari Lyn Salvador Guna collection"]],
  "sub-types first",
  [r("Nuchukana", ST, "curing and guardian figures (plural of nuchu), carved of balsa and other spirit-bearing woods", "https://maxwellmuseum.unm.edu/maxwell-at-home/objects/object-monday-guna-nuchu"),
   r("Guna Yala", CW, "Caribbean comarca of the Guna, where the figures are carved", "Guna_people")],
  ["Guna nuchu figures"])

# ---------------- E Ceramics ----------------
def pot(key, label, defn, aliases, see, src, cats, kinds, cf, sub="E1", breadth="narrow", axis=AX_OBJ):
    L(key, sub, label, breadth, defn, aliases, see, src, cats, axis, kinds, cf)

pot("ATLWS", "Atlantic Watershed Pottery",
    "Pre-Columbian pottery of the Central Highlands and Caribbean (Atlantic Watershed) region of Costa Rica, c. 500 BCE–1550 CE: tripod vessels with modelled animal feet, appliqué effigy jars and painted wares buried in stone-cist cemeteries around Guayabo and Las Mercedes.",
    "Central Highlands–Atlantic Watershed pottery; Costa Rican Atlantic Watershed", "Nicoya Polychrome; Diquís Pottery",
    ["Atlantic_Watershed", "Isthmo-Colombian_area"],
    [BCCR, SI("Atlantic Watershed", "the Smithsonian (NMAI) Costa Rica collections"), MET("Atlantic Watershed", "Atlantic Watershed objects at the Met")],
    [r("Irazú Yellow Line", ST, "Period VI (c. 1000–1550) tripod wares with thick yellow painted lines", FLMNH),
     r("Guayabo", CW, "Guayabo National Monument, the largest excavated Atlantic Watershed settlement", "Guayabo_National_Monument"),
     r("Las Mercedes", CW, "mound site near Guácimo, source of early stone and ceramic finds", "Las_Mercedes")],
    ["Atlantic Watershed pottery"])

pot("DIQUIS", "Diquís Pottery",
    "Pottery of the Diquís sub-region of the Gran Chiriquí in south-western Costa Rica (c. 300–1550 CE), contemporary with the stone spheres: tripod bowls, painted and incised jars and effigy vessels.",
    "Diquís ceramics", "Chiriquí Pottery; Isthmian Goldwork", ["Diquís"],
    [BCCR, SI("Diquís", "Diquís pottery in the Smithsonian (NMAI)")],
    [r("Finca 6", CW, "Diquís Delta site with stone spheres (UNESCO 2014)", "Finca_6"),
     r("Stone spheres of Costa Rica", CW, "the sphere sites of the Diquís Delta that define the culture", "Stone_spheres_of_Costa_Rica")],
    ["Diquís pottery"])

pot("CHIRIQUI", "Chiriquí Pottery",
    "The pottery of the Gran Chiriquí region of western Panama and south-eastern Costa Rica (c. 300–1500 CE), in named wares: thin buff Biscuit ware (Armadillo ware), Alligator ware painted with stylised crocodiles, and negative-painted lost-colour ware.",
    "Gran Chiriquí pottery; Chiriqui ware", "Isthmian Goldwork; Gran Coclé Pottery; Diquís Pottery", ["Chiriquí_Province", "Barriles"],
    [SI("Chiriqui", "Chiriquí pottery in the Smithsonian (NMAI)"), MET("Chiriqui", "Chiriquí objects at the Met")],
    [r("Biscuit ware", ST, "thin unslipped buff ware (Tarrago Biscuit, 'Armadillo ware') with modelled animal feet", FLMNH),
     r("Alligator ware", ST, "painted ware with stylised crocodile motifs", FLMNH),
     r("Barriles", CW, "early Chiriquí ceremonial site in the Chiriquí highlands", "Barriles"),
     r("Bugaba", CW, "district of the Chiriquí highlands with extensive cemeteries", "Bugaba")],
    ["Chiriquí pottery"])

pot("ULUA", "Ulúa Polychrome",
    "Painted pottery of the Ulúa valley and Lake Yojoa region of north-western Honduras, c. 600–1000 CE, with Maya-derived figural and glyph-like decoration on cylinders and tripod bowls.",
    "Ulúa-Yojoa polychrome; Ulúa pottery", "Maya Ceramics", ["Ulúa_River", "Travesía"],
    [SI("Ulua", "Ulúa pottery in the Smithsonian (NMAI)"), ["https://peabody.harvard.edu/", "Peabody Museum, Harvard", "early excavated Ulúa valley collections"]],
    [r("Las Vegas Polychrome", ST, "related polychrome of the Lake Yojoa area", FLMNH),
     r("Travesía", CW, "Late Classic centre in the lower Ulúa valley", "Travesía"),
     r("Los Naranjos", CW, "site on Lake Yojoa", "Los_Naranjos")],
    ["Ulúa polychrome pottery"])

pot("SELIN", "Selin Pottery",
    "Pottery of the Selin period (c. 300–1000 CE) of north-eastern Honduras, defined from excavations near Trujillo: incised and appliqué bowls, effigy rattles and supports.",
    "Selin Tradition", "Ulúa Polychrome", ["Pre-Columbian_Honduras"],
    [SI("Selin", "Selin pottery in the Smithsonian (NMAI)")],
    [r("North-east Honduras", CW, "the Caribbean coast around Trujillo where the period was defined", "History_of_Honduras")],
    ["Selin pottery"])

pot("USULUTAN", "Usulután Ware",
    "Resist-decorated pottery of south-eastern Mesoamerica, c. 500 BCE–250 CE, with wavy parallel lines left light on an orange slip, centred on El Salvador and traded into the Maya region.",
    "Usulután resist ware", "Maya Ceramics", ["Usulután", "Chalchuapa"],
    [SI("Usulutan", "Usulután ware in the Smithsonian (NMAI)")],
    [r("Chalchuapa", CW, "Late Preclassic centre in El Salvador with abundant Usulután ware", "Chalchuapa"),
     r("Usulután", CW, "the Salvadoran department after which the ware is named", "Usulután")],
    ["Usulután ware"])

pot("ZAPOTEC", "Zapotec Ceramics",
    "Pottery of the Zapotec civilization of the Valley of Oaxaca (c. 500 BCE–1500 CE), above all grey-ware effigy urns of deities such as Cocijo set in tombs, and the phases of Monte Albán.",
    "Zapotec urns; Zapotec pottery", "Mixtec Codices; Barro Negro Pottery", ["Zapotec_civilization", "Monte_Albán"],
    [SI("Zapotec", "Zapotec ceramics in the Smithsonian (NMAI)"), INAH, MET("Zapotec", "Zapotec urns at the Met")],
    [r("Effigy urns", ST, "funerary urns with seated deity or ancestor figures", "Zapotec_civilization"),
     r("Cocijo", ST, "rain-god image, the most frequent urn deity", "Cocijo"),
     r("Monte Albán", CW, "Zapotec capital whose phases (I–V) date the pottery", "Monte_Albán"),
     r("Lambityeco", CW, "Late Classic Zapotec site with modelled tomb figures", "Lambityeco")],
    ["Zapotec ceramics"])

pot("MIXPUE", "Mixteca-Puebla Polychrome",
    "Late Postclassic (c. 1200–1520) painted pottery of Puebla, Tlaxcala and the Mixteca in the Mixteca-Puebla style shared with the Borgia Group codices: Cholula polychrome lacquer-like wares and Puebla-Tlaxcala codex-style vessels.",
    "Cholula polychrome; Puebla-Tlaxcala polychrome; codex-style pottery", "Borgia Group; Aztec Pottery", ["Cholula_(Mesoamerican_site)", "Mixtec"],
    [SI("Mixteca-Puebla", "Mixteca-Puebla ceramics in the Smithsonian (NMAI)"), INAH],
    [r("Cholula polychrome", ST, "glossy painted ware of Cholula traded across Mesoamerica", "Cholula_(Mesoamerican_site)"),
     r("Puebla-Tlaxcala polychrome", ST, "codex-style vessels of the Puebla-Tlaxcala valley", "Tlaxcala_(Nahua_state)"),
     r("Cholula", CW, "Puebla city and pilgrimage centre, chief producer", "Cholula_(Mesoamerican_site)"),
     r("Tlaxcala", CW, "Nahua state east of the Valley of Mexico", "Tlaxcala_(Nahua_state)")],
    ["Mixteca-Puebla polychrome pottery", "Puebla-Tlaxcala polychrome pottery"])

pot("AZTECPOT", "Aztec Pottery",
    "Pottery of the Basin of Mexico in the Aztec period (c. 1150–1520): Aztec Black-on-Orange in phases I–IV, red wares, Texcoco fabric-marked salt vessels, censers and figurines, from Tenochtitlan and the Templo Mayor offerings.",
    "Aztec ceramics; Mexica pottery", "Aztec Sculpture; Mixteca-Puebla Polychrome", ["Aztec_pottery"],
    [INAH, SI("Aztec", "Aztec pottery in the Smithsonian (NMAI)"), ["https://www.templomayor.inah.gob.mx/", "Museo del Templo Mayor", "offerings from the Templo Mayor of Tenochtitlan"]],
    [r("Aztec Black-on-Orange", ST, "the diagnostic Basin of Mexico ware, seriated in phases I–IV", "Aztec_pottery"),
     r("Tenochtitlan", CW, "Mexica capital", "Tenochtitlan"),
     r("Templo Mayor", CW, "main temple whose offerings preserve ritual ceramics", "Templo_Mayor"),
     r("Texcoco", CW, "Acolhua capital", "Texcoco")],
    ["Aztec pottery"])

pot("PUREPECHA", "Purépecha Pottery",
    "Pottery of the Tarascan (Purépecha) state of Michoacán, c. 1350–1530: spouted and stirrup-handled jars, painted and negative-decorated vessels and figures from Tzintzuntzan and Ihuatzio, and later Purépecha village pottery.",
    "Tarascan pottery", "Mexican Lacquerware", ["Tarascan_state", "Purépecha"],
    [SI("Purepecha", "Purépecha (Tarascan) pottery in the Smithsonian (NMAI)"), INAH],
    [r("Tzintzuntzan", CW, "Tarascan capital on Lake Pátzcuaro", "Tzintzuntzan"),
     r("Ihuatzio", CW, "Tarascan ceremonial centre", "Ihuatzio")],
    ["Purépecha pottery"])

pot("TUMACO", "Tumaco-La Tolita Ceramics",
    "Mould-made and modelled ceramic figures, masks, vessels and plaques of the Tumaco-La Tolita culture of the Pacific coast of Colombia and Ecuador (c. 600 BCE–350 CE): seated figures, erotic and deity figurines, feline masks.",
    "Tolita pottery; Tumaco figurines", "Tumaco-La Tolita Goldwork; Jama-Coaque Ceramics", ["Tumaco-La_Tolita_culture", "La_Tolita"],
    [ORO, SI("Tumaco La Tolita", "Tumaco-La Tolita objects in the Smithsonian (NMAI)")],
    [r("Mould-made figurines", ST, "figures pressed in moulds, the culture's most numerous art", "Tumaco-La_Tolita_culture"),
     r("La Tolita", CW, "island ceremonial centre in Esmeraldas, Ecuador", "La_Tolita"),
     r("Tumaco", CW, "Colombian Pacific port region of the culture's sites", "Tumaco")],
    ["Tumaco-La Tolita ceramics"])

pot("JAMA", "Jama-Coaque Ceramics",
    "Hollow and mould-made ceramic figures, pipes and stamps of the Jama-Coaque culture of northern Manabí, Ecuador (c. 350 BCE–1530 CE), showing costumed shamans, warriors and dignitaries.",
    "Jama-Coaque figures", "Bahía Figurines; Tumaco-La Tolita Ceramics", ["Jama_Canton", "Manabí_Province"],
    [SI("Jama-Coaque", "Jama-Coaque objects in the Smithsonian (NMAI)"), MET("Jama-Coaque", "Jama-Coaque figures at the Met")],
    [r("Jama valley", CW, "valley of northern Manabí where the culture is named", "Jama_Canton")],
    ["Jama-Coaque ceramics"])

pot("MANTENO", "Manteño-Huancavilca Pottery",
    "Burnished black and grey pottery of the Manteño-Huancavilca culture of coastal Ecuador (c. 800–1532 CE): figural whistles and jars, ceramic figures and spindle whorls, alongside the stone U-shaped seats.",
    "Manteño pottery", "Bahía Figurines", ["Manteño-Huancavilca_culture"],
    [SI("Manteño", "Manteño-Huancavilca objects in the Smithsonian (NMAI)")],
    [r("Manta", CW, "port at the centre of the Manteño area", "Manta,_Ecuador"),
     r("Agua Blanca", CW, "Manteño town site in Machalilla National Park", "Agua_Blanca")],
    ["Manteño-Huancavilca pottery"])

pot("CARCHI", "Carchi-Nariño Pottery",
    "Pottery of the highland Carchi (Ecuador) and Nariño (Colombia) region, c. 700–1500 CE, in the Capulí, Piartal and Tuza complexes: negative-painted footed bowls, coqueros figures chewing coca, ocarinas.",
    "Nariño pottery; Carchi pottery; Capulí pottery", "Barniz de Pasto", ["Nariño_culture", "Capulí_culture"],
    [ORO, SI("Carchi", "Carchi-Nariño pottery in the Smithsonian (NMAI)")],
    [r("Capulí", SP, "complex of negative-painted bowls and seated coquero figures", "Capulí_culture"),
     r("Piartal", SP, "later complex with painted geometric and animal designs", "Nariño_culture"),
     r("Tuza", SP, "latest complex, red-on-cream painting", "Nariño_culture")],
    ["Carchi (Nariño) pottery"])

pot("QUIMBAYA", "Quimbaya Pottery",
    "Pottery of the Quimbaya region of the middle Cauca valley, Colombia (c. 500 BCE–1600 CE): seated 'cacique' figures, negative-painted and incised vessels and urns of Early and Late Quimbaya.",
    "Quimbaya ceramics", "Quimbaya Goldwork", ["Quimbaya_culture"],
    [ORO, SI("Quimbaya", "Quimbaya objects in the Smithsonian (NMAI)")],
    [r("Early Quimbaya", SP, "Classic period of the gold Treasure of the Quimbayas", "Quimbaya_culture"),
     r("Late Quimbaya", SP, "later period of slab figures and urns", "Quimbaya_culture")],
    ["Quimbaya pottery"])

pot("TAIRONA", "Tairona Pottery",
    "Black and red pottery of the Tairona of the Sierra Nevada de Santa Marta, Colombia (c. 200–1600 CE): footed and effigy vessels, ocarinas and figures from stone-terraced towns such as Ciudad Perdida.",
    "Tayrona pottery", "Tairona Goldwork", ["Tairona"],
    [ORO, SI("Tairona", "Tairona objects in the Smithsonian (NMAI)")],
    [r("Ciudad Perdida", CW, "Teyuna, the largest Tairona town (c. 800 CE)", "Ciudad_Perdida")],
    ["Tairona pottery"])

pot("INCAPOT", "Inca Pottery",
    "Imperial Inca pottery (c. 1400–1532) in the Cusco polychrome style spread through the empire: aryballos (urpu) storage jars, plates with bird handles and pedestal pots, alongside local Inca-provincial wares.",
    "Inka pottery; Cusco polychrome", "Inca Textiles; Inca Metalwork; Inca Architecture", ["Aryballos", "Inca_Empire"],
    [LARCO, SI("Inka", "Inca pottery in the Smithsonian (NMAI)")],
    [r("Aryballos", ST, "narrow-necked storage jar with nubbin and strap handles", "Aryballos"),
     r("Cusco", CW, "imperial capital and origin of the style", "Cusco")],
    ["Inca pottery"])

pot("WARIPOT", "Wari Pottery",
    "Polychrome pottery of the Wari state of the central Andes (c. 600–1000 CE): oversized offering urns with staff-god faces smashed in ritual at Conchopata, face-neck jars and kero cups in the Chakipampa, Robles Moqo and Viñaque styles.",
    "Huari pottery", "Wari Textiles; Tiwanaku Pottery", ["Wari_culture", "Conchopata"],
    [LARCO, SI("Wari", "Wari pottery in the Smithsonian (NMAI)")],
    [r("Conchopata", CW, "Ayacucho site of the smashed oversized urns", "Conchopata"),
     r("Wari", CW, "capital near Ayacucho", "Wari_(archaeological_site)"),
     r("Pikillaqta", CW, "Wari administrative centre near Cusco", "Pikillaqta")],
    ["Wari pottery"])

pot("TIWANAKU", "Tiwanaku Pottery",
    "Polychrome pottery of Tiwanaku in the Lake Titicaca basin (c. 500–1000 CE): flaring kero beakers, puma-headed incense burners and tazones painted with condor and feline heads.",
    "Tiahuanaco pottery", "Wari Pottery", ["Tiwanaku"],
    [SI("Tiwanaku", "Tiwanaku pottery in the Smithsonian (NMAI)"), LARCO],
    [r("Kero", ST, "flaring drinking beaker, Tiwanaku's signature form", "Kero"),
     r("Tiwanaku", CW, "the capital near Lake Titicaca", "Tiwanaku")],
    ["Tiwanaku pottery"])

pot("SICAN", "Sicán Pottery",
    "Burnished blackware of the Middle Sicán (Lambayeque) culture of Peru's north coast (c. 900–1100 CE): single-spout and stirrup bottles with the Sicán Lord face, whistling vessels and paddle-stamped wares.",
    "Lambayeque pottery", "Sicán Metalwork; Chimú Blackware", ["Lambayeque_culture"],
    [LARCO, SI("Sican", "Sicán pottery in the Smithsonian (NMAI)")],
    [r("Batán Grande", CW, "Sicán capital and cemetery in the Lambayeque valley", "Batán_Grande"),
     r("Túcume", CW, "later Lambayeque pyramid centre", "Túcume")],
    ["Sicán (Lambayeque) pottery"])

pot("CHANCAY", "Chancay Pottery",
    "Black-on-white matte pottery of the Chancay culture of Peru's central coast (c. 1000–1470 CE): large ovoid jars with painted faces and cuchimilco standing figures with raised arms.",
    "Chancay black-on-white", "Chancay Textiles", ["Chancay_culture"],
    [LARCO, SI("Chancay", "Chancay pottery in the Smithsonian (NMAI)")],
    [r("Cuchimilco", ST, "hollow standing figure with raised arms, placed in tombs", "Cuchimilco")],
    ["Chancay pottery"])

pot("ICACHINCHA", "Ica-Chincha Pottery",
    "Late Intermediate pottery of the Ica and Chincha valleys of Peru's south coast (c. 1000–1476 CE), with textile-like geometric painting in black, white and red on globular jars and bowls.",
    "Ica pottery; Chincha pottery", "Nazca Pottery", ["Chincha_culture", "Ica,_Peru"],
    [SI("Ica-Chincha", "Ica-Chincha pottery in the Smithsonian (NMAI)"), LARCO],
    [r("Chincha", CW, "valley of the Chincha kingdom of traders", "Chincha_culture"),
     r("Ica", CW, "valley of the Ica style", "Ica,_Peru")],
    ["Ica-Chincha pottery"])

pot("HUMAHUACA", "Humahuaca Pottery",
    "Late pottery of the Quebrada de Humahuaca in north-western Argentina (c. 900–1535 CE), black-on-red bowls and jars and later Humahuaca-Inca vessels from pucará hill-forts such as Tilcara.",
    "Humahuaca-Inca pottery", "Inca Pottery", ["Quebrada_de_Humahuaca"],
    [SI("Humahuaca", "Humahuaca pottery in the Smithsonian (NMAI)"), PRECOL],
    [r("Pucará de Tilcara", CW, "fortified settlement of the Quebrada", "Pucará_de_Tilcara"),
     r("Quebrada de Humahuaca", CW, "valley in Jujuy, UNESCO World Heritage", "Quebrada_de_Humahuaca")],
    ["Humahuaca pottery"])

pot("SPATACAMA", "San Pedro de Atacama Pottery",
    "Polished black and red pottery of the San Pedro de Atacama oases in northern Chile (c. 500 BCE–1450 CE), with grey-black polished bowls and ladles, found with snuff trays and Tiwanaku imports.",
    "San Pedro polished blackware", "Tiwanaku Pottery", ["San_Pedro_de_Atacama", "Atacameño"],
    [PRECOL, SI("San Pedro de Atacama", "San Pedro de Atacama pottery in the Smithsonian (NMAI)")],
    [r("San Pedro de Atacama", CW, "oasis town and cemeteries of the tradition", "San_Pedro_de_Atacama")],
    ["San Pedro de Atacama pottery"])

pot("MAPUCHEPOT", "Mapuche Pottery",
    "Pottery of the Mapuche of south-central Chile and Argentina: metawe jars, ketru metawe duck-shaped jars and red-and-white painted vessels of the Vergel and Valdivia styles, still made by women potters.",
    "metawe", "Mapuche Silverwork; Mapuche Textiles; Quinchamalí Pottery", ["Mapuche"],
    [PRECOL, SI("Mapuche", "Mapuche objects in the Smithsonian (NMAI)")],
    [r("Metawe", ST, "the jar, the basic Mapuche pottery form", "Mapuche"),
     r("Ketru metawe", ST, "jar in the form of a duck", "Mapuche")],
    ["Mapuche pottery"])

pot("CHACHI", "Chachi Pottery",
    "Pottery of the Chachi (Cayapas) of Esmeraldas, Ecuador, made by women for cooking and ritual drinking.",
    "Cayapas pottery", "", ["Chachi_people"],
    [SI("Chachi", "Chachi objects in the Smithsonian (NMAI)")],
    [r("Esmeraldas", CW, "Ecuadorian province of the Chachi rivers", "Esmeraldas")],
    ["Chachi pottery"])

pot("NGABE", "Ngäbe Pottery",
    "Pottery of the Ngäbe (Guaymí) of western Panama, bowls and pipe bowls of the Ngäbe-Buglé region.",
    "Guaymí pottery", "Chiriquí Pottery", ["Ngäbe"],
    [SI("Ngabe", "Ngäbe objects in the Smithsonian (NMAI)")],
    [r("Ngäbe-Buglé Comarca", CW, "Indigenous territory of the Ngäbe", "Ngäbe-Buglé_Comarca")],
    ["Ngäbe pottery"])

pot("KALINA", "Kali'na Pottery",
    "Pottery of the Kali'na (Carib, Galibi) of coastal Suriname, Guyana and French Guiana: red and black painted jars, double jars and griddles made by women along the Marowijne.",
    "Carib pottery; Galibi pottery", "Akawaio Pottery", ["Kali'na"],
    [SI("Carib Suriname", "Kali'na objects in the Smithsonian (NMAI)"), WERELD],
    [r("Marowijne River", CW, "border river of Suriname and French Guiana with Kali'na villages", "Marowijne_River")],
    ["Kali'na (Carib) pottery"])

pot("AKAWAIO", "Akawaio Pottery",
    "Pottery of the Akawaio (Kapon) of the upper Mazaruni, Guyana, including pipe bowls and cooking pots.",
    "Acawai pottery", "Kali'na Pottery", ["Akawaio_people"],
    [SI("Akawaio", "Akawaio objects in the Smithsonian (NMAI)")],
    [r("Akawaio", CW, "Cariban people of the Guiana Highlands", "Akawaio_people")],
    ["Akawaio pottery"])

pot("VALENCIOID", "Valencioid Pottery",
    "Unpainted, richly modelled pottery and figurines of the Valencioid series around Lake Valencia, north-central Venezuela (c. 900–1500 CE): coffee-bean-eyed female figurines and anthropomorphic jars.",
    "Valencia phase pottery; Valencia figurines", "Tierroid Pottery", ["Lake_Valencia", FLMNH],
    [SI("Valencioid", "Valencioid objects in the Smithsonian (NMAI)")],
    [r("Valencia phase figurines", ST, "female figurines with broad heads, the 'Valencia phase trait'", FLMNH),
     r("Lake Valencia", CW, "the lake basin defining the series", "Lake_Valencia")],
    ["Valencioid pottery"])

pot("TIERROID", "Tierroid Pottery",
    "Figurines and vessels of the Tierroid series (Tierra de los Indios style) of western Venezuela, white-on-red painted figures classified by head form.",
    "Tierra de los Indios style", "Valencioid Pottery", [FLMNH],
    [SI("Tierroid", "Tierroid objects in the Smithsonian (NMAI)")],
    [r("Tierra de los Indios style", ST, "figurine style of five groups defined by head and body form", FLMNH)],
    ["Tierroid pottery"])

pot("SALADOID", "Saladoid Pottery",
    "White-on-red painted and zoned-incised pottery of the Saladoid series, made by the first farming potters to move from the Orinoco into the Antilles (c. 500 BCE–600 CE): bell-shaped bowls, effigy adornos and griddles.",
    "Saladoid ceramics; Cedrosan Saladoid", "Ostionoid Pottery; Troumassoid Pottery", ["Saladoid"],
    [SI("Saladoid", "Saladoid objects in the Smithsonian (NMAI)")],
    [r("Cedrosan Saladoid", ST, "white-on-red painted subseries of the Lesser Antilles and Puerto Rico", "Saladoid"),
     r("Huecan Saladoid", ST, "zoned-incised subseries of La Hueca, Vieques", "Saladoid"),
     r("Saladero", CW, "type site on the lower Orinoco, Venezuela", "Saladero")],
    ["Saladoid pottery"])

pot("OSTIONOID", "Ostionoid Pottery",
    "Pottery of the Ostionoid series of the Greater Antilles (c. 600–1500 CE), developing from the Saladoid and ending in the Chican wares of the Taíno: red-slipped Ostionan, Elenan, Meillacan and Chican (Chicoid) subseries with modelled-incised adornos.",
    "Taíno pottery; Chicoid pottery", "Saladoid Pottery; Taíno Zemís", ["Taíno", "Saladoid"],
    [SI("Ostionoid", "Ostionoid objects in the Smithsonian (NMAI)")],
    [r("Ostionan Ostionoid", ST, "earliest red-slipped subseries, Puerto Rico and Hispaniola", "Taíno"),
     r("Elenan Ostionoid", ST, "subseries of eastern Puerto Rico and the Virgin Islands", "Taíno"),
     r("Meillacan Ostionoid", ST, "appliqué and incised subseries of Hispaniola, Jamaica and Cuba", "Taíno"),
     r("Chican Ostionoid", ST, "the Taíno subseries with modelled-incised effigy adornos", "Taíno"),
     r("Tibes", CW, "ceremonial centre near Ponce, Puerto Rico", "Tibes_Indigenous_Ceremonial_Center"),
     r("Caguana", CW, "Taíno ball-court site, Utuado, Puerto Rico", "Caguana_Ceremonial_Ball_Courts_Site")],
    ["Ostionoid pottery", "Chican Ostionoid (Taíno) pottery", "Elenan Ostionoid pottery", "Meillacan Ostionoid pottery", "Ostionan Ostionoid pottery"])

pot("TROUMASSOID", "Troumassoid Pottery",
    "Post-Saladoid pottery of the Lesser Antilles (c. 600–1500 CE), red-slipped dishes, legged griddles and painted Calivigny ware, in the Troumassan, Mamoran and Suazan subseries.",
    "Suazoid pottery; Troumassoid series", "Saladoid Pottery", ["https://www.universiteitleiden.nl/en/research/research-projects/archaeology/guadeloupe"],
    [SI("Troumassoid", "Troumassoid objects in the Smithsonian (NMAI)")],
    [r("Troumassan Troumassoid", ST, "earlier subseries of the Windward Islands", "https://www.universiteitleiden.nl/en/research/research-projects/archaeology/guadeloupe"),
     r("Mamoran Troumassoid", ST, "subseries of the northern Lesser Antilles", "https://www.universiteitleiden.nl/en/research/research-projects/archaeology/guadeloupe"),
     r("Suazan Troumassoid", ST, "late subseries (Suazoid), with finger-indented rims and Calivigny painted ware", "https://www.universiteitleiden.nl/en/research/research-projects/archaeology/guadeloupe")],
    ["Troumassoid pottery"])

pot("MOGOLLON", "Mogollon Pottery",
    "Pottery of the Mogollon culture of south-western New Mexico, eastern Arizona and Chihuahua (c. 200–1450 CE): brown wares, red-on-brown and the Mimbres black-on-white of its Mimbres branch.",
    "Mogollon brown ware", "Mimbres Pottery; Casas Grandes Pottery", ["Mogollon_culture"],
    [SI("Mogollon", "Mogollon pottery in the Smithsonian (NMAI)"), ["https://www.mimbres.org/", "Mimbres Foundation", "Mimbres and Mogollon pottery research"]],
    [r("Mimbres black-on-white", ST, "figural bowls of the Mimbres branch (see Mimbres Pottery)", "Mimbres_pottery"),
     r("Grasshopper Pueblo", CW, "late Mogollon pueblo in east-central Arizona", "Grasshopper_Pueblo"),
     r("Mimbres valley", CW, "valley of the classic Mimbres sites", "Mimbres")],
    ["Mogollon pottery"])

pot("YUMAN", "Yuman Pottery",
    "Paddle-and-anvil pottery of the Yuman-speaking peoples of the lower Colorado River and southern California, descended from the Patayan: Kumeyaay ollas, Mojave and Quechan painted jars and effigy figures, Maricopa red-and-black polished ware.",
    "Patayan pottery; Colorado River pottery", "Ancestral Puebloan Pottery", ["Patayan", "Kumeyaay"],
    [SI("Mojave pottery", "Yuman pottery in the Smithsonian (NMAI)")],
    [r("Patayan", SP, "archaeological ancestors of the Yuman peoples (c. 700–1550)", "Patayan"),
     r("Kumeyaay", CW, "Diegueño of San Diego county and Baja California; ollas", "Kumeyaay"),
     r("Mojave", CW, "potters of painted jars and doll-like effigy figures", "Mohave_people"),
     r("Quechan", CW, "Yuma potters of the Colorado–Gila confluence", "Quechan_people"),
     r("Maricopa", CW, "polished red-and-black ware of the Gila River", "Maricopa_people")],
    ["Kumeyaay pottery", "Mojave pottery", "Quechan pottery", "Maricopa pottery"])

pot("CHEROKEEPOT", "Cherokee Pottery",
    "Stamped and incised pottery of the Cherokee of the southern Appalachians and its revival among the Eastern Band on the Qualla Boundary, North Carolina: pipe bowls, bowls and black-burnished wares.",
    "Eastern Band Cherokee pottery", "Catawba Pottery; Rivercane Basketry", ["Eastern_Band_of_Cherokee_Indians"],
    [SI("Cherokee pottery", "Cherokee pottery in the Smithsonian (NMAI)")],
    [r("Qualla Boundary", CW, "Eastern Band land in western North Carolina, centre of the revival", "Qualla_Boundary")],
    ["Cherokee pottery"])

pot("IROQUOIAN", "Iroquoian Pottery",
    "Collared and incised pottery and effigy clay pipes of the Iroquoian peoples of New York and Ontario (c. 900–1650), above all Seneca and Niagara Iroquoian pipes with human and animal heads.",
    "Haudenosaunee pottery; Iroquois pottery", "Ceremonial Pipes; Haudenosaunee Raised Beadwork", ["Iroquoian_peoples", "Seneca_people"],
    [SI("Seneca pipe", "Iroquoian pottery and pipes in the Smithsonian (NMAI)")],
    [r("Effigy pipes", ST, "clay pipes with modelled human or animal heads", "Iroquoian_peoples"),
     r("Seneca", CW, "western Haudenosaunee nation whose village sites yielded many pipes", "Seneca_people")],
    ["Iroquoian pottery"])

pot("SUSQ", "Susquehannock Pottery",
    "Collared incised pottery and clay pipes of the Susquehannock of the lower Susquehanna valley (c. 1550–1675).",
    "Susquehannock ware", "Iroquoian Pottery", ["Susquehannock"],
    [SI("Susquehannock", "Susquehannock objects in the Smithsonian (NMAI)")],
    [r("Lower Susquehanna valley", CW, "Lancaster County, Pennsylvania, homeland of the Susquehannock", "Susquehannock")],
    ["Susquehannock pottery"])

pot("PAMUNKEY", "Pamunkey Pottery",
    "Pottery of the Pamunkey of tidewater Virginia, an unbroken tradition of shell-tempered ware revived in the 1930s with glazed wares from the reservation pottery school.",
    "", "Catawba Pottery", ["Pamunkey"],
    [SI("Pamunkey", "Pamunkey objects in the Smithsonian (NMAI)")],
    [r("Pamunkey Indian Reservation", CW, "reservation on the Pamunkey River, King William County, Virginia", "Pamunkey_Indian_Reservation")],
    ["Pamunkey pottery"])

pot("DEPTFORD", "Deptford Pottery",
    "Check-stamped and simple-stamped pottery of the Deptford culture of the south-eastern Atlantic and Gulf coasts (c. 800 BCE–700 CE), preceding Swift Creek.",
    "Deptford check-stamped", "Swift Creek Pottery; Weeden Island Pottery", ["Deptford_culture"],
    [SI("Deptford", "Deptford pottery in the Smithsonian (NMAI)")],
    [r("Check-stamped ware", ST, "pottery impressed with a grid-carved paddle, the culture's marker", "Deptford_culture")],
    ["Deptford pottery"])

pot("STJOHNS", "St. Johns Pottery",
    "Chalky, sponge-spicule-tempered pottery of the St. Johns culture of north-eastern Florida (c. 500 BCE–1565 CE), plain, incised and later check-stamped.",
    "St. Johns chalky ware", "Mississippian Pottery; Weeden Island Pottery", ["St._Johns_culture"],
    [SI("St. Johns", "St. Johns pottery in the Smithsonian (NMAI)")],
    [r("St. Johns Check Stamped", ST, "late (St. Johns II) stamped variety", "St._Johns_culture"),
     r("Mount Royal", CW, "St. Johns II mound site on the St. Johns River", "Mount_Royal_(Florida)")],
    ["St. Johns pottery"])

pot("NUBIANCHR", "Christian Nubian Pottery",
    "Wheel-made painted pottery of the Christian kingdoms of Nubia (c. 550–1500), decorated with birds, crosses and vegetal designs in the manner of manuscripts, from the workshops of Faras and Old Dongola.",
    "Makurian pottery; Faras pottery", "Meroitic Pottery; Ethiopian Manuscripts", ["Christian_Nubia", "Makuria"],
    [PENN("Christian Nubia", "Penn Museum's Faras and Nubian finds"), BM("Christian Nubian", "Christian Nubian pottery in the British Museum")],
    [r("Faras", CW, "Nobadian capital and potteries", "Faras"),
     r("Old Dongola", CW, "Makurian capital", "Old_Dongola"),
     r("Qasr Ibrim", CW, "fortress-town with long pottery sequence", "Qasr_Ibrim")],
    ["Christian Nubian pottery"])

pot("MULTAN", "Multan Blue Pottery",
    "Blue-and-turquoise painted, glazed earthenware and tiles (kashi) of Multan in Punjab, used on its Sufi shrines and still made by kashigar families: dishes, vases and tile panels.",
    "kashigari; Multani pottery", "Blue Pottery of Jaipur; Kashi Kari", ["Multan", "Tomb_of_Shah_Rukn-e-Alam"],
    [VAM("Multan", "Multan pottery and tiles at the V&A")],
    [r("Tomb of Shah Rukn-e-Alam", CW, "14th-century Multan shrine with glazed tilework", "Tomb_of_Shah_Rukn-e-Alam"),
     r("Multan", CW, "Punjab city of the kashigar potters", "Multan")],
    ["Multani blue pottery"])

# ---------------- F Glass ----------------
L("PEKING", "F2", "Peking Glass", "narrow",
  "Glass of the Qing imperial glassworks founded in Beijing in 1696 and of its later imitators, carved like hardstone: monochrome and overlay (cameo) vases, faceted bottles, snuff bottles, golden age under Qianlong.",
  "Qing imperial glass; Beijing glass", "Chinese Snuff Bottles; Chinese Jade", ["Peking_glass"],
  [CMA("Qing glass", "Qing glass at Cleveland"), VAM("Peking glass", "Peking glass at the V&A"),
   ["https://www.dpm.org.cn/", "Palace Museum, Beijing", "the imperial collection of Qing glass"]],
  "sub-types first, then phases by reign and centres",
  [r("Overlay glass", ST, "layers of coloured glass carved in cameo relief", "Peking_glass"),
   r("Glass snuff bottles", ST, "the most numerous product of the workshops", "Snuff_bottle"),
   r("Kangxi period", SP, "foundation of the palace glassworks in 1696", "Kangxi_Emperor"),
   r("Qianlong period", SP, "golden age of the imperial glass (1735–96)", "Qianlong_Emperor"),
   r("Boshan", CW, "Shandong glassmaking town that supplied raw glass", "Boshan_District")],
  ["Qing imperial glass (Peking glass)"])

L("SHIRAZ", "F1", "Shiraz Glass", "narrow",
  "Free-blown glass of 18th–19th-century Iran, associated with Shiraz, in clear blue, green and amethyst: rosewater sprinklers with long twisted necks, decanters and ewers.",
  "Persian blown glass; Qajar glass", "Syrian Glassblowing; Beykoz Glass", ["Qajar_art", "Shiraz"],
  [VAM("Persian glass", "Qajar blown glass at the V&A"), WERELD],
  "sub-types first, then centres",
  [r("Rosewater sprinklers", ST, "gulabpash with long, often twisted necks", "Rosewater_sprinkler"),
   r("Shiraz", CW, "Fars city with which the glass is associated", "Shiraz")],
  ["Persian blown glass (Shiraz)"])

L("KROBO", "F1", "Krobo Beads", "narrow",
  "Powder-glass beads made by Krobo craftsmen of south-eastern Ghana from ground recycled glass fused in clay moulds: monochrome, painted 'writing' beads and fused-fragment beads, worn at Dipo puberty rites.",
  "Krobo powder-glass beads; Ghanaian glass beads", "Art of Glass Beads", ["Powder_glass_beads", "Krobo_people"],
  [WERELD, BM("Krobo bead", "Krobo beads in the British Museum")],
  "sub-types first, then centres",
  [r("Writing beads", ST, "'mue ne angma', powder-glass beads with painted designs", "Powder_glass_beads"),
   r("Fused-fragment beads", ST, "translucent beads from fused bottle-glass fragments", "Powder_glass_beads"),
   r("Odumase", CW, "Krobo town, centre of the bead industry", "Odumase")],
  ["Krobo glass beads"])

# ---------------- G Metalwork ----------------
L("CNMIRROR", "G1", "Chinese Bronze Mirrors", "medium",
  "Cast bronze mirrors of China, polished on one face and decorated on the back around a central knob, from the Warring States to the Ming: Warring States 'shan' mirrors, Han TLV mirrors, Tang lobed and sea-beast-and-grape mirrors, Song Huzhou mirrors.",
  "Chinese mirrors; jing", "Chinese Ritual Bronzes; Etruscan Mirrors", ["Chinese_bronze_mirror", "TLV_mirror"],
  [COLBASE("銅鏡", "bronze mirrors in Japan's national museums"), CMA("Chinese mirror", "Chinese mirrors at Cleveland"),
   MET("Chinese bronze mirror", "Chinese mirrors at the Met")],
  "sub-types by period, earliest first, then centres",
  [r("Warring States mirrors", ST, "thin mirrors with interlace and 'shan'-character grounds", "Warring_States_period"),
   r("TLV mirrors", ST, "Han mirrors with cosmological T, L and V motifs", "TLV_mirror"),
   r("Magic mirrors", ST, "mirrors that project their back design in reflected light", "Chinese_magic_mirror"),
   r("Tang mirrors", ST, "lobed, sea-beast-and-grape and inlaid mirrors of the Tang", "Tang_dynasty_art"),
   r("Huzhou", CW, "Zhejiang city of plain Song mirrors with maker's stamps", "Huzhou")],
  ["Chinese bronze mirrors"])

L("SILLAGOLD", "G3", "Silla Goldwork", "narrow",
  "Gold and gilt-bronze regalia from the 5th–6th-century royal mound tombs of Silla at Gyeongju — tree-and-antler crowns hung with jade gogok, earrings, girdles and vessels — and the bronze temple bells of Unified Silla.",
  "Silla gold crowns; Silla metalwork", "Korean Buddhist Sculpture", ["Crowns_of_Silla"],
  [EMUSEUM, ["https://gyeongju.museum.go.kr/", "Gyeongju National Museum", "the Silla tomb finds and the Bell of King Seongdeok"]],
  "sub-types first, then the tombs (centres) that yielded them",
  [r("Crowns of Silla", ST, "gold crowns with tree and antler uprights, spangles and jade", "Crowns_of_Silla"),
   r("Silla bronze bells", ST, "Unified Silla temple bells, culminating in the Bell of King Seongdeok (771)", "Bell_of_King_Seongdeok"),
   r("Geumgwanchong", CW, "'Gold Crown Tomb', Gyeongju, excavated 1921", "Geumgwanchong"),
   r("Cheonmachong", CW, "'Heavenly Horse Tomb', Gyeongju, excavated 1973", "Cheonmachong"),
   r("Gyeongju", CW, "Silla capital and its tumuli park", "Gyeongju")],
  ["Silla goldwork"])

L("TUMACOGOLD", "G3", "Tumaco-La Tolita Goldwork", "narrow",
  "Gold, tumbaga and sintered gold-platinum ornaments of the Tumaco-La Tolita culture (c. 600 BCE–350 CE), the earliest platinum working in the world: nose rings, masks, mirrors and miniature figures.",
  "La Tolita gold; Tumaco goldwork", "Tumaco-La Tolita Ceramics; Calima Goldwork", ["Tumaco-La_Tolita_culture", "Platinum"],
  [ORO, SI("La Tolita gold", "Tumaco-La Tolita goldwork in the Smithsonian (NMAI)")],
  "sub-types first, then centres",
  [r("Gold-platinum sintering", ST, "alloys of platinum and gold made by sintering grains", "Platinum"),
   r("La Tolita", CW, "island site in Esmeraldas, Ecuador", "La_Tolita")],
  ["Tumaco-La Tolita goldwork"])

L("ZENU", "G3", "Zenú Goldwork", "narrow",
  "Cast-filigree gold and tumbaga of the Zenú (Sinú) of the Caribbean lowlands of Colombia (c. 200 BCE–1000 CE): semicircular filigree ear ornaments, staff finials with birds and animals, pectorals.",
  "Sinú goldwork", "Tairona Goldwork; Quimbaya Goldwork", ["Zenú"],
  [ORO, SI("Zenu", "Zenú goldwork in the Smithsonian (NMAI)")],
  "sub-types first, then centres",
  [r("False-filigree ear ornaments", ST, "lost-wax cast openwork ear ornaments imitating filigree", "Zenú"),
   r("Sinú River", CW, "river valley of the Zenú hydraulic landscape", "Sinú_River")],
  ["Zenú goldwork"])

L("KIRIBATIARM", "G2", "Kiribati Armour", "narrow",
  "Body armour of the I-Kiribati (Gilbert Islands) knotted and woven from coconut-fibre sennit, sometimes with human-hair patterns — cuirasses, jerkins, leggings, porcupine-fish helmets — worn with shark-tooth weapons in formal duels.",
  "Gilbertese armour; te otanga; coconut-fibre armour", "Fijian Clubs",
  ["https://web.prm.ox.ac.uk/weapons/index.php/tour-by-region/oceania/oceania/arms-and-armour-oceania-222/index.html", "https://www.fg-art.org/en/artwork-of-the-month-archives/the-art-of-armour-in-kiribati"],
  [TEPAPA, WERELD, BM("Kiribati armour", "Kiribati armour in the British Museum")],
  "sub-types first",
  [r("Te otanga", ST, "the full suit of coconut-fibre armour", "https://www.aucklandmuseum.com/discover/stories/blog/2021/moving-the-needle"),
   r("Te barantauti", ST, "helmet of dried porcupine-fish skin", "https://www.rct.uk/collection/stories/grand-vestibule-the-british-monarchy-and-the-world/porcupine-fish-helmet-te-barantauti"),
   r("Shark-tooth weapons", ST, "wooden swords and spears edged with shark teeth", "https://web.prm.ox.ac.uk/weapons/index.php/tour-by-region/oceania/oceania/arms-and-armour-oceania-222/index.html")],
  ["Kiribati coconut-fibre armour"])

# ---------------- H Textiles ----------------
L("LINDAMASK", "H3", "Linen Damask", "medium",
  "Figured linen table linen woven on draw-looms in the Southern Netherlands and Holland from the 16th century, with hunting scenes, biblical stories, maps and coats of arms: Kortrijk (Courtrai) damask, Haarlem damask.",
  "Flemish damask; Courtrai damask; Haarlem damask", "Irish Linen; Bezdan Damask", ["Damask", "Kortrijk"],
  [RIJ("damast", "Kortrijk and Haarlem damask in the Rijksmuseum"), VAM("linen damask", "linen damask at the V&A")],
  "centres in order of rise (Kortrijk, then Haarlem), then makers",
  [r("Kortrijk", CW, "Flemish centre of linen damask weaving, 16th–17th c.", "Kortrijk"),
   r("Haarlem", CW, "Dutch centre after Flemish weavers emigrated, 17th c.", "Haarlem"),
   r("Passchier Lammertijn", MK, "Kortrijk-born damask weaver active in Haarlem (c. 1600)", "https://www.rijksmuseum.nl/en/collection/search?query=Passchier+Lammertijn", 1)],
  ["Haarlem linen damask", "Kortrijk linen damask"])

L("MAPUCHETEX", "H2", "Mapuche Textiles", "medium",
  "Warp-faced weaving of the Mapuche women of Chile and Argentina on the vertical loom, a pre-Hispanic tradition and major trade good: ponchos (makuñ) with stepped crosses, sashes, blankets and saddle cloths.",
  "Mapuche weaving", "Mapuche Silverwork; Mapuche Pottery", ["Mapuche_textiles"],
  [PRECOL, SI("Mapuche", "Mapuche textiles in the Smithsonian (NMAI)")],
  "sub-types first",
  [r("Poncho", ST, "makuñ, the chief's poncho with ikat or stepped designs", "Poncho"),
   r("Huilliche weaving", ST, "southern Mapuche (Huilliche) ponchos and blankets", "Mapuche_textiles")],
  ["Mapuche Textiles"])

L("CHIMUTEX", "H2", "Chimú Textiles", "narrow",
  "Textiles of the Chimú kingdom of Peru's north coast (c. 900–1470 CE): cotton and camelid tapestry, brocade and painted cloth, feathered tunics and ponchos from Chan Chan and coastal cemeteries.",
  "Chimu textiles", "Chimú Blackware; Chimú Metalwork; Chancay Textiles", ["Chimú_culture"],
  [LARCO, SI("Chimu textile", "Chimú textiles in the Smithsonian (NMAI)")],
  "sub-types, then centres",
  [r("Feathered tunics", ST, "tunics and panels covered with tropical feathers", "Chimú_culture"),
   r("Chan Chan", CW, "Chimú capital", "Chan_Chan")],
  ["Chimú Textiles"])

L("NASCATEX", "H2", "Nasca Textiles", "narrow",
  "Textiles of the Nasca culture of Peru's south coast (c. 100 BCE–700 CE), successors of Paracas: tapestry and embroidered mantles and tunics, three-dimensional needle-knitted borders, feathered ornaments.",
  "Nazca textiles", "Paracas Textiles; Nazca Pottery", ["Nazca_culture"],
  [LARCO, SI("Nasca", "Nasca textiles in the Smithsonian (NMAI)")],
  "centres",
  [r("Cahuachi", CW, "Nasca ceremonial centre", "Cahuachi")],
  ["Nasca Textiles"])

L("KUTCH", "H4", "Kutch Embroidery", "medium",
  "Embroidery of the pastoral and farming communities of Kutch, Gujarat, worked in silk and cotton with inset mirrors (abhla), each community with its own stitches and motifs: Rabari, Ahir, Banni, Mutwa, Jat and Sodha styles; GI-registered.",
  "Kutchi embroidery; Kachchhi bharat", "Rogan Art; Ajrakh; Ralli Quilt", ["Kutch_embroidery"],
  [VAM("Kutch embroidery", "Kutch embroidery at the V&A"), CMA("Kutch", "Kutch textiles at Cleveland")],
  "sub-types (community styles) first, then centres",
  [r("Rabari", ST, "chain-stitch and mirror embroidery of the Rabari herders", "Rabari"),
   r("Ahir", ST, "Ahir style with circles and mirrors", "Ahir"),
   r("Banni", ST, "embroidery of the Banni grassland communities", "Banni"),
   r("Mutwa", ST, "fine Mutwa embroidery of northern Banni", "Mutwa"),
   r("Jat", ST, "cross-stitch embroidery of the Jat herders", "Jat_people"),
   r("Abhla bharat", ST, "mirror work, common to all styles", "Abhla_bharat"),
   r("Bhuj", CW, "chief town of Kutch and its craft market", "Bhuj")],
  ["Kutch Embroidery"])

L("VALLACE", "H4", "Valenciennes Lace", "medium",
  "Straight bobbin lace made in one piece with ground and pattern worked together, originating at Valenciennes in the 17th century and later made in Flanders: Ypres, Bruges and Ghent 'Valenciennes' with round or diamond mesh.",
  "Val lace; Valenciennes", "Mechlin Lace; Brussels Lace; Alençon Lace", ["Valenciennes_lace"],
  [RIJ("Valenciennes kant", "Valenciennes lace in the Rijksmuseum"), MET("Valenciennes lace", "Valenciennes lace at the Met"),
   ["https://www.artic.edu/collection?q=Valenciennes%20lace", "Art Institute of Chicago: Valenciennes lace", "lace in the AIC textile collection"]],
  "centres in order of production",
  [r("Valenciennes", CW, "town in Hainaut, origin of the lace", "Valenciennes"),
   r("Lille", CW, "nearby French centre", "Lille"),
   r("Bailleul", CW, "French Flanders lace town", "Bailleul"),
   r("Ypres", CW, "chief Belgian centre of 19th-century Valenciennes", "Ypres"),
   r("Bruges", CW, "Flemish lace centre", "Bruges"),
   r("Ghent", CW, "Flemish lace centre", "Ghent")],
  ["Valenciennes Lace"])

L("SAMPLERS", "H4", "Needlework Samplers", "medium",
  "Embroidered samplers worked by girls to record stitches, alphabets, verses and pictures, from 16th-century band samplers to the schoolgirl samplers of Britain and America: band, spot, alphabet, map and memorial samplers, and the school samplers of Westtown and Mary Balch's Providence school.",
  "samplers; schoolgirl samplers; American samplers", "Berlin Wool Work; Crewelwork", ["Sampler_(needlework)"],
  [["https://www.cooperhewitt.org/search/collection?query=sampler", "Cooper Hewitt collection: samplers", "a large sampler collection at the Smithsonian Design Museum"],
   MET("sampler", "samplers at the Met"), VAM("sampler", "samplers at the V&A")],
  "sub-types first, then schools (centres)",
  [r("Band samplers", ST, "long narrow early samplers of stitch bands", "Sampler_(needlework)"),
   r("Alphabet samplers", ST, "letters and numerals for marking linen", "Sampler_(needlework)"),
   r("Map samplers", ST, "embroidered maps, popular c. 1770–1840", "Sampler_(needlework)"),
   r("Memorial samplers", ST, "mourning pictures with tombs and willows, early 19th c.", "Sampler_(needlework)"),
   r("Westtown School", CW, "Quaker boarding school, Pennsylvania, known for its samplers and globes", "Westtown_School"),
   r("Balch School", CW, "Mary Balch's school for girls, Providence, Rhode Island", "Balch_School")],
  ["American Needlework Samplers"])

L("BUTTONBL", "H4", "Button Blankets", "narrow",
  "Ceremonial robes of the Northwest Coast peoples made from trade wool blankets with red appliqué borders and crest figures outlined in mother-of-pearl buttons, worn at potlatches.",
  "button robes", "Chilkat Weaving; Northwest Coast Woodcarving", ["Button_blanket"],
  [SI("button blanket", "button blankets in the Smithsonian (NMAI)"), CMH],
  "centres by people",
  [r("Kwakwaka'wakw", CW, "button blankets of the Kwakwaka'wakw of Vancouver Island", "Kwakwaka'wakw"),
   r("Tlingit", CW, "Tlingit crest robes", "Tlingit"),
   r("Haida", CW, "Haida crest robes", "Haida_people")],
  ["Northwest Coast Button Blankets"])

L("KLEDER", "H7", "Klederdracht", "medium",
  "The regional folk costumes of the Netherlands, worn daily in fishing and Protestant farming communities into the 20th century and some still today, each with its caps, bodices and jewellery: Volendam, Marken, Staphorst, Spakenburg, Urk, Zeeland, Hindeloopen, Zaanstreek.",
  "Dutch folk costume; Dutch traditional dress", "Tracht; Bunad", ["Volendam", "Staphorst"],
  [RIJ("klederdracht", "Dutch regional costume in the Rijksmuseum"),
   ["https://www.openluchtmuseum.nl/", "Nederlands Openluchtmuseum", "the Dutch Open Air Museum's national costume collection"]],
  "centres (regions) from best-known living costumes to historical ones",
  [r("Volendam", CW, "fishing-village costume with the pointed lace cap", "Volendam"),
   r("Marken", CW, "former island costume with striped bodice", "Marken"),
   r("Staphorst", CW, "Overijssel costume still worn daily", "Staphorst"),
   r("Spakenburg", CW, "costume with the starched 'kraplap' shoulder piece", "Spakenburg"),
   r("Urk", CW, "former island fishing costume", "Urk"),
   r("Scheveningen", CW, "fishing-village costume of The Hague", "Scheveningen"),
   r("Zeeland", CW, "province of several costumes and gold ear-irons", "Zeeland"),
   r("Hindeloopen", CW, "Frisian town of painted furniture and chintz costume", "Hindeloopen"),
   r("Zaanstreek", CW, "18th-century costume of the Zaan region", "Zaanstreek")],
  ["Dutch Klederdracht"])

L("INUITCL", "H7", "Inuit Clothing", "medium",
  "Tailored skin clothing of the Inuit and Yup'ik of the Arctic, sewn from caribou, seal and bird skins with sinew: parkas and the women's amauti, trousers, mukluks and kamiit, gut-skin rain parkas and snow goggles.",
  "Inuit skin clothing; Eskimo clothing", "Inuit Sculpture; Yup'ik Masks", ["Inuit_clothing"],
  [SI("Inuit parka", "Inuit clothing in the Smithsonian (NMAI and NMNH)"), CMH],
  "sub-types first, then peoples (centres)",
  [r("Parka", ST, "hooded outer garment of caribou or sealskin", "Parka"),
   r("Amauti", ST, "women's parka with a pouch for carrying a child", "Amauti"),
   r("Anorak", ST, "pullover hooded jacket", "Anorak"),
   r("Mukluk", ST, "soft boot of sealskin or caribou", "Mukluk"),
   r("Snow goggles", ST, "slit goggles of wood, bone or ivory", "Snow_goggles"),
   r("Copper Inuit", CW, "central Arctic group of Coronation Gulf", "Copper_Inuit"),
   r("Iñupiat", CW, "northern Alaskan Inuit", "Iñupiat"),
   r("Yup'ik", CW, "south-western Alaskan Yup'ik", "Yup'ik")],
  ["Inuit Skin Clothing"])

def bas(key, label, defn, aliases, see, src, cats, kinds, cf, breadth="narrow", axis="sub-types first, then peoples and centres, then named makers"):
    L(key, "H8", label, breadth, defn, aliases, see, src, cats, axis, kinds, cf)

bas("CSBASK", "Coast Salish Basketry",
    "Coiled cedar-root baskets imbricated with bear grass and cherry bark, and twined baskets, of the Coast Salish and neighbouring peoples of Washington State and British Columbia: Cowichan, Quinault and Quileute baskets, lidded trunks and berry baskets.",
    "Salish basketry", "Plateau Imbricated Basketry; Coast Salish Weaving", ["Coast_Salish"],
    [SI("Salish basket", "Coast Salish baskets in the Smithsonian (NMAI)"), CMH],
    [r("Cowichan", CW, "Cowichan Tribes of Vancouver Island", "Cowichan_Tribes"),
     r("Quinault", CW, "Washington coast weavers of twined baskets", "Quinault"),
     r("Quileute", CW, "Olympic Peninsula basket makers", "Quileute")],
    ["Coast Salish Basketry"])

bas("NCNMAKAH", "Nuu-chah-nulth and Makah Basketry",
    "Fine wrapped-twined baskets of the Nuu-chah-nulth of Vancouver Island and the Makah of Cape Flattery, in bear grass and cedar bark with whaling scenes, from the conical whaler's hat to lidded 'trinket' baskets for the tourist trade.",
    "Makah basketry; Nootka basketry", "Spruce-Root Basketry", ["Makah", "Nuu-chah-nulth"],
    [SI("Makah basket", "Makah and Nuu-chah-nulth baskets in the Smithsonian (NMAI)"), ["https://makah.com/makah-tribal-info/museum/", "Makah Museum", "Neah Bay museum of the Ozette finds"]],
    [r("Makah", CW, "Neah Bay, Washington", "Makah"),
     r("Nuu-chah-nulth", CW, "west coast of Vancouver Island", "Nuu-chah-nulth"),
     r("Ozette", CW, "buried Makah village with preserved basketry (c. 1700)", "Ozette_Indian_Village_Archeological_Site")],
    ["Nuu-chah-nulth and Makah Basketry"])

bas("NESPLINT", "Northeastern Splint Basketry",
    "Plaited wood-splint baskets of black ash and oak made by the Indigenous peoples of the north-east and mid-Atlantic, painted or stamped with designs: Mohegan painted baskets, Lenape (Delaware), Pequot and Rappahannock baskets.",
    "woodsplint basketry; ash splint baskets", "Wabanaki Basketry", ["Mohegan", "Black_ash"],
    [SI("splint basket", "splint baskets in the Smithsonian (NMAI)")],
    [r("Mohegan", CW, "Connecticut makers of painted splint baskets", "Mohegan"),
     r("Pequot", CW, "Connecticut basket makers", "Pequot"),
     r("Lenape", CW, "Delaware basket makers, later in Oklahoma", "Lenape"),
     r("Rappahannock", CW, "Virginia basket makers", "Rappahannock_people")],
    ["Northeastern Splint Basketry"])

bas("GBBASK", "Great Basin Basketry",
    "Coiled and twined willow baskets of the Washoe, Paiute, Shoshone and Chemehuevi of the Great Basin, from water jars pitched with pine resin to the fine degikup baskets of Washoe weavers.",
    "Washoe basketry; Paiute basketry", "California Indian Basketry; Pomo Basketry", ["Great_Basin_tribes"],
    [SI("Paiute basket", "Great Basin baskets in the Smithsonian (NMAI)")],
    [r("Washoe", CW, "Lake Tahoe weavers of degikup baskets", "Washoe_people"),
     r("Northern Paiute", CW, "Pyramid Lake and Nevada weavers", "Northern_Paiute"),
     r("Chemehuevi", CW, "southern Paiute weavers of fine coiled baskets", "Chemehuevi"),
     r("Louisa Keyser", MK, "Washoe weaver Dat So La Lee (c. 1829–1925)", "Louisa_Keyser", 1)],
    ["Great Basin basketry"])

bas("SERIBASK", "Seri Basketry",
    "Coiled baskets of the Comcaac (Seri) of Sonora, made of torote stems, from the giant ceremonial saptim baskets to the bowls made for sale since the 1960s.",
    "Comcaac basketry; Seri coritas", "Pima Basketry", ["Seri_people"],
    [SI("Seri", "Seri objects in the Smithsonian (NMAI)")],
    [r("Comcaac", CW, "Seri communities of Punta Chueca and El Desemboque", "Seri_people")],
    ["Seri basketry"])

bas("WOUNAAN", "Wounaan and Emberá Basketry",
    "Tightly coiled palm-fibre baskets of the Wounaan and Emberá of Panama's Darién and Colombia's Chocó, made of chunga and nahuala palm dyed with plants, in animal and geometric designs.",
    "Wounaan baskets; Emberá baskets; werregue", "Mola", ["Wounaan", "Emberá"],
    [SI("Wounaan", "Wounaan and Emberá baskets in the Smithsonian (NMAI)")],
    [r("Wounaan", CW, "weavers of the Darién and Chocó", "Wounaan"),
     r("Emberá", CW, "weavers of the Darién and Chocó", "Emberá"),
     r("Darién Province", CW, "Panamanian province of the weaving communities", "Darién_Province")],
    ["Wounaan basketry", "Wounaan and Emberá Basketry"])

def bead(key, label, defn, aliases, see, src, cats, kinds, cf, breadth="narrow", axis="sub-types first, then peoples (centres)"):
    L(key, "H9", label, breadth, defn, aliases, see, src, cats, axis, kinds, cf)

bead("GLBEAD", "Great Lakes Floral Beadwork",
     "Glass-bead embroidery and loom beadwork of the Anishinaabe, Ho-Chunk, Meskwaki, Potawatomi and other Great Lakes peoples, from the 19th century, in curvilinear floral designs: bandolier bags, sashes, moccasins and hair ties.",
     "Woodlands floral beadwork; Ojibwe beadwork", "Ribbonwork; Plains Beadwork", ["Native_American_beadwork", "Bandolier_bag"],
     [SI("Ojibwe beadwork", "Great Lakes beadwork in the Smithsonian (NMAI)"), CMH],
     [r("Bandolier bag", ST, "gashkibidaagan, large shoulder bag, a showpiece of Great Lakes beadwork", "Bandolier_bag"),
      r("Ojibwe", CW, "Anishinaabe beadworkers of the upper Great Lakes", "Ojibwe"),
      r("Ho-Chunk", CW, "Winnebago beadworkers of Wisconsin", "Ho-Chunk"),
      r("Meskwaki", CW, "Fox beadworkers, Iowa", "Meskwaki"),
      r("Potawatomi", CW, "Great Lakes beadworkers", "Potawatomi")],
     ["Great Lakes floral beadwork"])

bead("SUBARCBEAD", "Subarctic Beadwork",
     "Floral glass-bead embroidery on hide and velvet of the Dene, Innu, Cree, Métis and other peoples of the Canadian and Alaskan Subarctic: moccasins, tunics, mitts, baby belts and gun cases.",
     "Métis beadwork; Dene beadwork", "Moosehair Embroidery; Porcupine Quillwork", ["Métis", "Subarctic_peoples"],
     [CMH, SI("Dene beadwork", "Subarctic beadwork in the Smithsonian (NMAI)")],
     [r("Métis", CW, "the 'flower beadwork people' of the Red River and north-west", "Métis"),
      r("Dene", CW, "Athabaskan beadworkers of the Northwest Territories", "Dene"),
      r("Gwich'in", CW, "Alaskan and Yukon Athabaskans", "Gwich'in"),
      r("Tahltan", CW, "northern British Columbia", "Tahltan"),
      r("Innu", CW, "Labrador and Quebec", "Innu")],
     ["Subarctic beadwork"])

bead("XHOSABEAD", "Xhosa Beadwork",
     "Glass-bead ornaments of the Xhosa of South Africa's Eastern Cape, in white, blue and red, signalling age and status: collars (ingqosha), aprons, headbands and beaded tobacco pouches.",
     "isiXhosa beadwork", "Zulu Beadwork; Shweshwe", ["Xhosa_people"],
     [["https://lux.collections.yale.edu/", "LUX: Yale Collections Discovery", "Yale's collections including Xhosa beadwork"], CMA("Xhosa", "Xhosa beadwork at Cleveland")],
     [r("Ingqosha", ST, "beaded collar", "Xhosa_people"),
      r("Eastern Cape", CW, "home of the Xhosa", "Xhosa_people")],
     ["Xhosa Beadwork"])

bead("AMAZFEATH", "Amazonian Featherwork",
     "Feather ornaments of the Indigenous peoples of the Amazon and Brazilian interior, tied and glued on cords and frames: head rings and diadems, ear ornaments, armbands and dance capes of the Karajá, Bororo, Kayapó and Munduruku.",
     "plumária; Amazonian feather art", "Mexican Featherwork; Hawaiian Featherwork", ["Featherwork"],
     [SI("feather headdress Brazil", "Amazonian featherwork in the Smithsonian (NMAI)"), WERELD, QB],
     [r("Karajá", CW, "Araguaia River featherworkers", "Karajá_people"),
      r("Bororo", CW, "Mato Grosso featherworkers", "Bororo"),
      r("Kayapó", CW, "Xingu featherworkers", "Kayapo"),
      r("Munduruku", CW, "Tapajós featherworkers", "Munduruku")],
     ["Amazonian Featherwork"])

L("HUICHOL", "H9", "Huichol Art", "medium",
  "The ritual and commercial arts of the Wixárika (Huichol) of the Sierra Madre Occidental: beaded gourd bowls and figures pressed into beeswax, yarn paintings (nierika), woven and embroidered sashes and bags, and ceramic offering bowls.",
  "Wixárika art; nierika; Huichol beadwork; Huichol yarn painting", "Mexican Featherwork", ["Huichol_art"],
  [SI("Huichol", "Huichol objects in the Smithsonian (NMAI)"), INAH, WERELD],
  "sub-types (media) first, then makers",
  [r("Beadwork", ST, "glass beads pressed into beeswax on gourds, masks and figures", "Huichol_art"),
   r("Yarn painting", ST, "nierika: yarn pressed into wax on boards", "Huichol_art"),
   r("Textiles", ST, "embroidered sashes, bags and men's costume", "Huichol_art"),
   r("José Benítez Sánchez", MK, "Huichol yarn painter (1938–2009)", "José_Benítez_Sánchez", 1)],
  ["Huichol Textiles and Beadwork", "Huichol beadwork", "Huichol ceramics", "Huichol Yarn Painting"])

# ---------------- I Woodwork / Lacquer ----------------
L("NWCWOOD", "I1", "Northwest Coast Woodcarving", "broad",
  "Carved and painted wood of the Northwest Coast peoples in formline design other than masks, poles and bentwood boxes: feast dishes, rattles, house posts and screens, canoes and paddles, chiefs' seats, combs and spoons.",
  "Northwest Coast art; formline carving", "Northwest Coast Masks; Totem Poles; Bentwood Boxes", ["Northwest_Coast_art", "Formline_art"],
  [SI("Kwakwaka'wakw", "Northwest Coast objects in the Smithsonian (NMAI)"), CMH,
   ["https://www.si.edu/", "Smithsonian Institution", "NMNH and NMAI hold the largest 19th-century Northwest Coast collections"]],
  "sub-types first, then makers by birth",
  [r("Feast dishes", ST, "large carved dishes for potlatch feasts", "Feast_dish"),
   r("Formline", ST, "the design system of ovoids and U-forms underlying the carving", "Formline_art"),
   r("Charles Edenshaw", MK, "Haida carver (c. 1839–1920)", "Charles_Edenshaw", 1),
   r("Willie Seaweed", MK, "Kwakwaka'wakw carver (1873–1967)", "Willie_Seaweed", 1),
   r("Mungo Martin", MK, "Kwakwaka'wakw carver (1879–1962)", "Mungo_Martin", 1),
   r("Ellen Neel", MK, "Kwakwaka'wakw carver (1916–1966)", "Ellen_Neel", 1),
   r("Henry Hunt", MK, "Kwakwaka'wakw carver (1923–1985)", "Henry_Hunt", 1),
   r("Doug Cranmer", MK, "'Namgis carver (1927–2006)", "Doug_Cranmer", 1),
   r("Bill Reid", MK, "Haida sculptor (1920–1998)", "Bill_Reid", 1),
   r("Tony Hunt", MK, "Kwakwaka'wakw carver (1942–2017)", "Tony_Hunt", 1),
   r("Robert Davidson", MK, "Haida carver (b. 1946)", "Robert_Davidson_(artist)", 1)],
  ["Northwest Coast woodcarving"])

L("KUBAWOOD", "I1", "Kuba Woodcarving", "narrow",
  "Carved wooden objects of the Kuba kingdom (Bushoong and related peoples) of the DR Congo, covered in interlace patterns: palm-wine cups with heads, tukula camwood boxes, drums, panels and figures.",
  "Kuba carving", "Ndop; Kuba Masks; Kuba Raffia Textiles", ["Kuba_art", "Kuba_Kingdom"],
  [PENN("Kuba", "Penn Museum's Kuba collection"), ["https://www.africamuseum.be/en", "Royal Museum for Central Africa", "Tervuren, the largest Kuba collection"]],
  "sub-types first, then centres",
  [r("Ndop", ST, "royal portrait figures (see Ndop)", "Ndop_(Kuba)"),
   r("Bushoong", CW, "ruling people of the Kuba kingdom at Nsheng", "Bushoong")],
  ["Kuba wood carving"])

L("CNLACQ", "I2", "Chinese Lacquerware", "broad",
  "Lacquer of China from the Neolithic to the Qing on wood, cloth and leather cores: painted Chu and Han lacquer, mother-of-pearl inlay, qiangjin incised gold, carved cinnabar lacquer and Coromandel screens.",
  "Chinese lacquer; qiqi", "Carved Lacquer; Japanese Lacquerware; Ryukyuan Lacquerware", ["Chinese_lacquerware"],
  [COLBASE("漆器 中国", "Chinese lacquer in Japan's national museums"), CMA("Chinese lacquer", "Chinese lacquer at Cleveland"),
   VAM("Chinese lacquer", "Chinese lacquer at the V&A")],
  "sub-types by technique, earliest first, then centres",
  [r("Painted lacquer", ST, "red-and-black painted lacquer of the Warring States and Han", "Chinese_lacquerware"),
   r("Carved lacquer", ST, "cinnabar and tixi lacquer carved in relief (see Carved Lacquer)", "Chinese_lacquerware"),
   r("Coromandel lacquer", ST, "incised and coloured screens of the Qing exported to Europe", "Coromandel_lacquer"),
   r("Mawangdui", CW, "Han tombs near Changsha with painted lacquer", "Mawangdui")],
  ["Chinese lacquerware"])

SPRINGER = "https://link.springer.com/article/10.1007/s10963-017-9102-y"
EXTRA = {
 "TAIRONA": [r("Sierra Nevada de Santa Marta", CW, "mountain massif of the Tairona towns, Colombia", "Sierra_Nevada_de_Santa_Marta")],
 "CHANCAY": [r("Chancay black-on-white", ST, "matte white-slipped ware painted in black, the culture's hallmark", "Chancay_culture"),
             r("Chancay valley", CW, "central-coast valley north of Lima", "Chancay")],
 "KUBAWOOD": [r("Tukula boxes", ST, "lidded boxes for red camwood (tukula) powder", "Kuba_art"),
              r("Palm-wine cups", ST, "carved cups, some with human heads, for palm wine", "Kuba_art")],
 "SERIBASK": [r("Saptim", ST, "giant ceremonial basket", "Seri_people"),
              r("Punta Chueca", CW, "Seri village on the Gulf of California", "Punta_Chueca"),
              r("El Desemboque", CW, "Seri village, Sonora", "El_Desemboque")],
 "DEPTFORD": [r("Simple-stamped ware", ST, "pottery impressed with a paddle of parallel grooves", "Deptford_culture"),
              r("Crystal River", CW, "Gulf-coast mound centre begun in the Deptford period", "Crystal_River_Archaeological_State_Park")],
 "STJOHNS": [r("St. Johns Plain", ST, "the plain chalky ware of all periods", "St._Johns_culture")],
 "SHIRAZ": [r("Decanters and ewers", ST, "blown table glass with applied handles", "Qajar_art"),
            r("Qajar period", SP, "19th-century floruit of the glass", "Qajar_art")],
 "MULTAN": [r("Kashi tile panels", ST, "painted glazed tiles for shrines and mosques", "Multan")],
 "MAPUCHETEX": [r("Vertical loom weaving", ST, "witral loom weaving of ponchos and blankets", "Mapuche_textiles")],
 "TIWANAKU": [r("Puma incense burners", ST, "incensarios with modelled puma heads", "Tiwanaku")],
 "SICAN": [r("Sicán Lord bottles", ST, "bottles with the face of the Sicán deity", "Lambayeque_culture")],
 "PUREPECHA": [r("Spouted jars", ST, "teapot-like spouted and stirrup-handled vessels", "Tarascan_state")],
 "HUMAHUACA": [r("Humahuaca-Inca style", SP, "local wares made under Inca rule (c. 1430–1535)", "Quebrada_de_Humahuaca")],
 "VALENCIOID": [r("El Topo style", ST, "late coastal style of the Valencioid series", SPRINGER)],
 "XHOSABEAD": [r("Beaded tobacco pouches", ST, "pouches carried by men and women", "Xhosa_people")],
 "ZENU": [r("Staff finials", ST, "cast finials with birds and animals for staffs of office", "Zenú")],
 "TUMACOGOLD": [r("Nose ornaments", ST, "hammered and cast nose rings and plaques", "Tumaco-La_Tolita_culture")],
 "IROQUOIAN": [r("Collared jars", ST, "jars with incised collars and castellations", "Iroquoian_peoples")],
 "USULUTAN": [r("Resist decoration", ST, "wavy multiple lines left light under a darker slip", "Usulután")],
}
for l in LEAVES:
    for k in EXTRA.get(l["key"], []):
        l["kinds"].append(k)
    RANK = {ST: 0, SP: 1, CW: 2, MK: 4}
    l["kinds"].sort(key=lambda x: RANK.get(x[1], 3))

json.dump({"leaves": {}, "new_leaves": LEAVES, "moves_out": [], "dropped": []},
          open(os.path.join(OUT, "result.json"), "w"), ensure_ascii=False, indent=1)

MERGES = [
  ["Māori pounamu carving", "D3-9", "alias", "Hei-tiki is defined as all pounamu ornaments and mere; aliases already include 'pounamu carving'"],
  ["Plateau beadwork", "H9-6", "section", "Plains Beadwork covers the Great Plains and Plateau; Nez Perce/Yakama as a Plateau section"],
  ["Caddo pottery", "E1-70", "section", "Mississippian Pottery definition includes Caddo engraved bottles; Caddoan Mississippian"],
  ["Brazilian Colonial Painting", "D5-70", "section", "Brazilian Baroque covers colonial church decoration incl. Ataíde ceilings; painting section (family A)"],
]
with open(os.path.join(OUT, "merges.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["tradition", "leaf_code", "as", "note"]); w.writerows(MERGES)
print(len(LEAVES), "new leaves,", sum(len(l["kinds"]) for l in LEAVES), "kinds,", len(MERGES), "merges")
