"""AAT reference sweep (2026-11-07): homes for the Getty AAT terms that have gathered museum records but no leaf.

Source: taxonomy/audit/reference/aat_crosswalk.csv, the 278 'uncovered' terms with records. Each was decided by
reading its records (medium family, titles, dates) against the leaves of its region (dossier rebuilt by
pipelines/r3/ref_decide.py):
  entry     the people or style is written as a "Peoples & cultures" entry into the existing leaf its records
            and the literature place it in (taxonomy/r3/aat_decisions.csv -> va_peoples.csv, how=decided)
  new leaf  a named tradition with no leaf, attested by a museum, UNESCO or encyclopedia source found by web
            search on 2026-11-07 (below); the AAT peoples it covers are its "Peoples & cultures" entries
  facet     a nationality, period or generic designation (served by the region and period facets)
  recorded  the records are utilitarian or ethnographic objects with no named visual tradition in the
            literature found; left for the sources, not the tree
Held (named traditions not confirmed from this environment): Nupe pottery, Wichí chaguar weaving, Mosquitia
barkcloth, Warao basketry. Their peoples are 'recorded' until a source is found.
Writes result.json in the va_out pass format.
"""
import json, os
W = "https://en.wikipedia.org/wiki/"
MET = "https://www.metmuseum.org/art/collection/search?q="
BM = "https://www.britishmuseum.org/collection/search?keyword="


def met(q, what): return [MET + q.replace(" ", "+"), f"The Met collection search: {q}", what]
def bm(q, what): return [BM + q.replace(" ", "+"), f"British Museum collection search: {q}", what]
def p(name, note, url): return [name, "Peoples & cultures", note, "r3 " + url, 0]
def k(name, group, note, url): return [name, group, note, "r3 " + url, 0]


def leaf(key, sub, label, defn, src, peoples, kinds=(), aliases="", see="", axis="", cat=None, breadth="narrow"):
    return dict(key=key, sub=sub, label=label, breadth=breadth, defn=defn, aliases=aliases, see=see,
                src=src, catalogues=cat or [met(label.split(" (")[0], f"{label} in the Metropolitan Museum")],
                axis=axis or "types, then the peoples who make it, then holding institutions",
                kinds=list(kinds) + [p(n, note, src[0][0]) for n, note in peoples])


L = [
    leaf("BFMASK", "D4", "Masks of Burkina Faso",
         "The painted wooden masks of the Volta River peoples of Burkina Faso and southern Mali: the tall plank masks "
         "(nwantantay) and animal masks of the Bwa, the masks of the Bobo, Nuna, Winiama and other Gurunsi-speaking peoples, "
         "the Mossi karanga, and the Nafana bedu, covered with red, white and black geometric patterns and danced at "
         "funerals, initiations and agricultural festivals.",
         [[W + "Art_of_Burkina_Faso", "Wikipedia"], [W + "Bwa_people", "Wikipedia"]],
         [("Bobo", "AAT Bobo; Bobo-Fing masks (nyanga)"), ("Sambla", "AAT Sambla"), ("Kurumba", "AAT Kurumba; antelope headdresses"),
          ("Nuna", "AAT Nuna"), ("Winiama", "AAT Winiama"), ("Gurunsi", "AAT Gurunsi"), ("Nafana", "AAT Nafana; bedu masks")],
         [k("Plank mask (nwantantay)", "Sub-types", "Bwa plank mask surmounting a disk-shaped face", W + "Bwa_people"),
          k("Leaf mask", "Sub-types", "Bwa masks of leaves dedicated to Dwo", W + "Art_of_Burkina_Faso")],
         aliases="Voltaic masks; Bwa masks; Plank masks", see="D4-12 Dogon Masks"),
    leaf("GUROMASK", "D4", "Guro Masks",
         "The masks of the Guro (Kweni) of central Côte d'Ivoire: the sacred family of zamble, with its fused antelope and "
         "crocodile muzzle, his wife gu and his wild brother zauli, danced at funerals of lineage elders, and entertainment "
         "masks designed by individual performers; also heddle pulleys carved with heads.",
         [["https://www.artic.edu/articles/732/five-new-things-in-african-art", "Art Institute of Chicago"],
          ["https://africanarchive.org/en/staemme/guro", "African Art Archive"]],
         [("Guro", "AAT Guro (peripheral Mande)")],
         [k("Zamble", "Sub-types", "hybrid antelope-crocodile mask", "https://www.artic.edu/articles/732/five-new-things-in-african-art"),
          k("Gu", "Sub-types", "female face mask, wife of zamble", "https://africanarchive.org/en/staemme/guro")],
         see="D5-46 Baule Sculpture"),
    leaf("BAGA", "D4", "Baga Headdresses",
         "The carved headdresses of the Baga of coastal Guinea: the colossal d'mba (nimba) shoulder mask of the great mother, "
         "the a-Mantsho-ña-Tshol serpent headdress, and the banda, danced at planting and harvest festivals, marriages and "
         "funerals; suppressed in the 1950s and revived since the 1980s.",
         [["https://dma.org/art/collection/object/3069658", "Dallas Museum of Art"]],
         [("Baga", "AAT Baga (Simo)"), ("Landuma", "AAT Landuma (Simo)")],
         [k("D'mba (nimba)", "Sub-types", "great-mother shoulder headdress", "https://dma.org/art/collection/object/3069658"),
          k("a-Mantsho-ña-Tshol", "Sub-types", "serpent headdress, master of medicine", "https://dma.org/art/collection/object/3069658")],
         aliases="Nimba; D'mba"),
    leaf("BENUE", "D5", "Benue River Valley Sculpture",
         "The sculpture, masks and ceramic spirit vessels of the peoples of the Benue River valley in central Nigeria: "
         "Mumuye columnar figures and sukuru masks, Chamba buffalo masks, Jukun, Mambila, Tiv, Idoma and Igala figures and "
         "masks, Ga'anda and other Upper Benue spirit vessels, and the iron and bronze regalia of the region.",
         [["https://fowler.ucla.edu/exhibitions/central-nigeria-unmasked-arts-of-the-benue-river-valley/", "Fowler Museum, Central Nigeria Unmasked (2011)"]],
         [("Mumuye", "AAT Mumuye"), ("Chamba", "AAT Chamba (Nigerian)"), ("Jukun", "AAT Jukun"), ("Mambila", "AAT Mambila"),
          ("Tiv", "AAT Tiv"), ("Idoma", "AAT Idoma"), ("Igala", "AAT Igala"), ("Ga'anda", "AAT Ga'anda; spirit vessels"),
          ("Jen", "AAT Jen"), ("Tangale", "AAT Tangale"), ("Waja", "AAT Waja"), ("Wurkun", "AAT Wurkun"), ("Koro", "AAT Koro"),
          ("Gwari", "AAT Gwari")],
         aliases="Arts of the Benue River Valley; Central Nigerian sculpture", see="D5-30 Nok Terracottas"),
    leaf("EKPO", "D4", "Ekpo Masks",
         "The masks of the Ekpo men's society of the Ibibio and Anang of south-eastern Nigeria, worn at the festival after "
         "the yam harvest when the ancestors return: dark idiok ekpo masks of evil spirits and pale mfon ekpo masks of beauty, "
         "with Ibibio marionettes and ancestor figures.",
         [["https://sainsburycentre.ac.uk/art-and-objects/237-dance-mask-for-the-ekpo-society", "Sainsbury Centre"]],
         [("Ibibio", "AAT Ibibio (Cross River)")],
         [k("Idiok ekpo", "Sub-types", "dark mask of an evil spirit", "https://sainsburycentre.ac.uk/art-and-objects/237-dance-mask-for-the-ekpo-society"),
          k("Mfon ekpo", "Sub-types", "pale mask of idealised beauty", "https://sainsburycentre.ac.uk/art-and-objects/237-dance-mask-for-the-ekpo-society")],
         see="D4-17 Igbo Masks"),
    leaf("NDELTA", "D4", "Niger Delta Water-Spirit Masks",
         "The masquerade headdresses of the Niger Delta: horizontal Ijo and Kalabari crests of water spirits in the form of "
         "hippopotamus, sawfish, shark and crocodile, performed by the Ekine society, and the articulated-jaw masks of the Ogoni.",
         [["https://africa.si.edu/collection/object/nmafa_2006-2-1", "National Museum of African Art"],
          ["https://learn.ncartmuseum.org/artwork/sawfish-headdress", "North Carolina Museum of Art"]],
         [("Ijo", "AAT Ijo (Niger Delta)"), ("Ogoni", "AAT Ogoni (Cross River)")],
         aliases="Ijo water-spirit headdresses; Kalabari masks"),
    leaf("XRIVER", "D4", "Cross River Skin-Covered Headdresses",
         "The dance crests of the Ejagham, Boki and neighbouring peoples of the Cross River in Nigeria and Cameroon: heads carved "
         "in wood and covered with soaked antelope skin, often Janus-faced, with pegged teeth and coiffures, owned by age and "
         "entertainment associations and worn at funerals and initiations.",
         [[W + "African_art", "Wikipedia"]],
         [("Ejagham", "AAT Ejagham"), ("Keaka", "AAT Keaka (Ejagham)")],
         cat=[met("Ejagham", "Ejagham headdresses in the Metropolitan Museum")], aliases="Ekoi headdresses"),
    leaf("URHOBO", "D4", "Urhobo Masks and Sculpture",
         "The masks and figures of the Urhobo of the western Niger Delta: water-spirit masks danced at festivals for spirits "
         "who travel upriver, the maiden masks with bridal coiffures, and the large edjo shrine figures.",
         [["https://africa.si.edu/collection/selected-artwork/2122", "National Museum of African Art"]],
         [("Urhobo", "AAT Urhobo (Edo-speaking)")]),
    leaf("YAKA", "D4", "Yaka and Suku Masks",
         "The masks of the Kwango-Kwilu region of the Democratic Republic of the Congo: the polychrome Yaka masks with "
         "upturned noses and raffia ruffs, held by a handle and danced in pairs at the close of the n-khanda boys' initiation, "
         "the Suku hemba helmet masks, and the masks of the Holo, Huana and Mbun.",
         [["https://www.slam.org/collection/objects/1681/", "Saint Louis Art Museum"]],
         [("Yaka", "AAT Yaka (Kwango-Kwilu)"), ("Suku", "AAT Suku"), ("Holo", "AAT Holo"), ("Huana", "AAT Huana"), ("Mbun", "AAT Mbun (Lower Kasai)")],
         [k("Ndeemba", "Sub-types", "initiation mask of the n-khanda camp", "https://www.slam.org/collection/objects/1681/")],
         see="D4-22 Pende Masks"),
    leaf("MBOLE", "D5", "Mbole Ofika Figures",
         "The ofika figures of the Mbole of the Lomami River region, Democratic Republic of the Congo: slender, hunched figures "
         "of hanged men, painted ochre and white, shown at the close of initiation into the Lilwa association to teach its law.",
         [["https://www.clevelandart.org/print/art/2016.33", "Cleveland Museum of Art"]],
         [("Mbole", "AAT Mbole (Mongo)")], see="D5-51 Lega Sculpture"),
    leaf("KANAK", "D5", "Kanak Sculpture",
         "The carving of the Kanak of New Caledonia: flèches faîtières (roof finials) and door jambs of the great clan houses, "
         "ancestor figures, masks of feathers and hair, and ceremonial axes and clubs.",
         [[W + "Flèche_faîtière", "Wikipedia"]], [("Kanak", "AAT Kanak (New Caledonian)")],
         [k("Flèche faîtière", "Sub-types", "roof finial of the clan house", W + "Flèche_faîtière")], aliases="New Caledonian carving"),
    leaf("BUKA", "I1", "Buka Ceremonial Paddles",
         "The carved and painted ceremonial paddles and dance clubs of Buka and Bougainville in the northern Solomon Islands, "
         "decorated in red, black and white with the kokorra, a squatting human figure wearing the upe headdress of male initiates.",
         [["https://web.prm.ox.ac.uk/rpr/index.php/article-index/12-articles/294-degeneration-part-2.html", "Pitt Rivers Museum"]],
         [("Bougainville", "AAT Bougainville (Solomon Islands)")], aliases="Kokorra paddles", see="D5-87 Nguzu Nguzu"),
    leaf("STICK", "I1", "Marshall Islands Stick Charts",
         "The navigational charts of the Marshall Islands: frames of palm-frond midribs bound with coconut fibre, curved sticks "
         "for ocean swells and cowrie shells for islands (mattang, meddo and rebbelib), used to teach voyaging and since the "
         "20th century also made for sale.",
         [[W + "Marshall_Islands_stick_chart", "Wikipedia"]], [("Marshallese", "AAT Marshallese (Micronesian)")],
         [k("Mattang", "Sub-types", "teaching chart of swell patterns", W + "Marshall_Islands_stick_chart"),
          k("Rebbelib", "Sub-types", "chart of a whole island chain", W + "Marshall_Islands_stick_chart")]),
    leaf("RAI", "D3", "Rai Stones",
         "The stone discs of Yap, quarried from aragonite on Palau and carried by canoe and raft, ranging from a few centimetres "
         "to several metres across, displayed outside houses and community buildings and exchanged at marriages, funerals and other "
         "ceremonies.",
         [["https://repository.si.edu/items/1e60ad21-d0ce-4421-a5be-8a41248644e9", "Smithsonian (Gillilland 1975)"], [W + "Rai_stones", "Wikipedia"]],
         [("Yap", "AAT Yap (Caroline Islands)")], aliases="Yapese stone money"),
    leaf("PALAU", "I1", "Palauan Storyboards",
         "The carved and painted narrative wood panels of Palau, derived from the carved beams and gables of the bai (men's "
         "clubhouse) and since the 1930s made as portable boards, telling legends such as the breadfruit tree and the Yapese "
         "currency quarrying.",
         [["https://www.penn.museum/documents/publications/expedition/18-1/Smith.pdf", "Penn Museum, Expedition 18-1"]],
         [("Palauan", "AAT Palauan (Caroline Islands)")], aliases="Palau bai carving", see="K12-3 Maneaba"),
    leaf("AUSTRAL", "D5", "Austral Islands Carving",
         "The woodcarving of the Austral Islands of French Polynesia: the deity figure A'a of Rurutu, the ceremonial paddles "
         "and ladles of Raivavae and Tubuai carved with interlocking geometric motifs and small human figures, fly whisks and "
         "drums.",
         [["https://www.penn.museum/sites/journal/938", "Penn Museum Journal (1921)"], ["https://smarthistory.org/rurutu-figure-known-as-aa/", "Smarthistory / British Museum"]],
         [("Austral Islands", "AAT Austral Islands (Polynesian)")], see="D5-88 Marquesan Carving"),
    leaf("LENCA", "E1", "Lenca Pottery",
         "The pottery of the Lenca of western Honduras and eastern El Salvador, made by hand by women from pre-Columbian times "
         "to the present: orange and brick-coloured household ware, and since the 1980s the black-and-white painted pottery of "
         "the La Campa and Gracias cooperatives.",
         [[W + "Lenca", "Wikipedia"]], [("Lenca", "AAT Lenca (Native Central American)")], see="E1-102 Ulúa Polychrome"),
    leaf("KADIWEU", "E1", "Kadiwéu Ceramics",
         "The pottery of the Kadiwéu (Caduveo) of Mato Grosso do Sul, Brazil: vessels, plates and figures painted with the minute "
         "symmetric scroll designs the Kadiwéu also paint on faces and bodies, recorded by Guido Boggiani and Claude Lévi-Strauss.",
         [["https://pib.socioambiental.org/en/Povo:Kadiw%C3%A9u", "Instituto Socioambiental, Indigenous Peoples in Brazil"]],
         [("Caduveo", "AAT Caduveo (Chaco)")], aliases="Caduveo pottery"),
    leaf("KUSIWA", "L5", "Kusiwa",
         "The graphic art of the Wajãpi of Amapá, Brazil: geometric motifs of the jaguar, anaconda, butterfly and fish painted on "
         "bodies and objects with annatto and resins, inscribed on the UNESCO Representative List in 2008.",
         [["https://ich.unesco.org/en/RL/oral-and-graphic-expressions-of-the-wajapi-00049", "UNESCO ICH"]],
         [("Wajãpi", "AAT Wajãpi (Guaraní)")], aliases="Wajapi body painting"),
    leaf("SELKNAM", "L5", "Selk'nam Body Painting",
         "The body painting of the Selk'nam (Ona) of Tierra del Fuego in red, white and black, with designs for hunting, combat "
         "and peace, and the totemic designs and bark masks of the spirits of the Hain initiation ceremony, photographed by "
         "Martin Gusinde in 1919–1924.",
         [["https://precolombino.cl/wp/en/culturas-americanas/pueblos-originarios-de-chile/selk%C2%B4nam/nggallery/slideshow", "Museo Chileno de Arte Precolombino"]],
         [("Selk'nam", "AAT Selk'nam"), ("Ona", "AAT Ona")], aliases="Hain body painting"),
    leaf("QUILLANGO", "A4", "Quillango",
         "The painted guanaco-skin robes of the Tehuelche (Aónikenk) of Patagonia, sewn from many pelts, worn fur inward with "
         "the painted side out, decorated with red, black and yellow geometric designs.",
         [["https://www.mininterior.gob.ar/agn/pdf/Tehuelches.pdf", "Archivo General de la Nación, Argentina"]],
         [("Tehuelche", "AAT Tehuelche"), ("Patagón", "AAT Patagón")], aliases="Tehuelche painted robes", see="A4-18 Plains Hide Painting"),
    leaf("NASKAPI", "A4", "Naskapi Painted Coats",
         "The painted caribou-skin coats of the Innu (Naskapi) of Quebec and Labrador, cut on the model of European frock coats "
         "and painted with dream-given designs in mineral and plant pigments bound with fish roe, with a triangular back gusset "
         "for the mountain of the Caribou Master; worn for one hunting season.",
         [["https://www.heritage.nf.ca/articles/indigenous/innu-culture.php", "Heritage Newfoundland and Labrador"],
          ["https://prm.web.ox.ac.uk/files/topleasethespiritspdf", "Pitt Rivers Museum"]],
         [("Naskapi", "AAT Naskapi (Innu)")], aliases="Innu painted coats", see="A4-18 Plains Hide Painting"),
    leaf("HUASTEC", "D5", "Huastec Sculpture",
         "The stone sculpture of the Huastec of the Gulf Coast of Mexico (c. 900–1521): sandstone figures of deities and rulers, "
         "naturalistic bodies with tall conical or fan headdresses, carved fully in the round in the Postclassic, with shell "
         "ornaments and effigy vessels.",
         [[W + "Huastec_civilization", "Wikipedia"]], [("Huastec", "AAT Huastec (Native Central Mexican)")],
         see="D5-65 Classic Veracruz Sculpture"),
    leaf("MAROON", "I1", "Maroon Arts of Suriname",
         "The woodcarving, textiles and painting of the Saramaka, Ndyuka, Aluku and other Maroon peoples of Suriname and French "
         "Guiana: low-relief and openwork carved paddles, combs, stools and house fronts with tacks and inlays, appliqué and "
         "embroidered capes, and the painted carving of the eastern Maroons.",
         [["https://www.encyclopedia.com/history/encyclopedias-almanacs-transcripts-and-maps/maroon-arts", "Encyclopedia of African-American Culture and History"]],
         [("Maroon", "AAT Maroon")], aliases="Saramaka woodcarving; Tembe"),
    leaf("PYU", "K9", "Pyu Architecture",
         "The brick architecture of the Pyu city-states of the Irrawaddy dry zone (2nd century BCE – 9th century CE): the walled "
         "and moated cities of Halin, Beikthano and Sri Ksetra with palace citadels and the cylindrical memorial stupas of the "
         "earliest Buddhist urban culture in Southeast Asia; UNESCO World Heritage 2014.",
         [["https://whc.unesco.org/en/list/1444/", "UNESCO World Heritage Centre"]], [("Pyu", "AAT Pyu (Southeast Asian)")], see="K9-5 Burmese Architecture"),
    leaf("YAO", "A4", "Yao Ritual Paintings",
         "The Taoist ceremonial scroll paintings (mien fang) of the Yao (Iu Mien) of South China, northern Vietnam, Laos and "
         "Thailand: sets of about seventeen hanging scrolls of the Three Pure Ones, the Jade Emperor, marshals and other deities "
         "displayed in ordinations and rites.",
         [["https://www.pha-tad-ke.com/wp-content/uploads/2022/02/2012-E-Catalog-Yao-Mien.pdf", "Pha Tad Ke, Yao Mien Ceremonial Paintings"]],
         [("Yao", "AAT Yao (Chinese, Vietnamese minorities; Southeast Asian)")], aliases="Mien fang; Iu Mien paintings"),
    leaf("TANGUT", "A4", "Tangut Buddhist Painting",
         "The Buddhist painting of the Tangut Western Xia (1038–1227), known chiefly from the hoard of Khara-Khoto excavated by "
         "Kozlov in 1908–1909: thangkas and silk paintings of Amitabha, Chakrasamvara, Vajravarahi and other deities in "
         "Tibetan and Chinese styles, with clay sculpture and xylograph frontispieces.",
         [[W + "Khara-Khoto", "Wikipedia"], ["https://harvardartmuseums.org/article/inside-and-out-a-technical-investigation-of-clay-buddhist-objects-from-khara-khoto", "Harvard Art Museums"]],
         [("Tangut", "AAT Tangut (Himalayan)")], aliases="Western Xia painting; Xixia painting", see="A4-7 Thangka"),
    leaf("YEKUANA", "H8", "Ye'kuana Basketry",
         "The plaited baskets of the Ye'kuana (Makiritare) of the upper Orinoco in Venezuela and Brazil: storage baskets and trays "
         "woven in black and natural strips with meander and animal designs (waja), made by men.",
         [["https://collection-online.moa.ubc.ca/search/item?category%5Bculture%5D%5B0%5D=1846581&row=4&tab=more", "Museum of Anthropology at UBC"]],
         [("Makiritaré", "AAT Makiritaré (Native Amazonian)")], aliases="Makiritare basketry; Waja trays", see="H9-14 Amazonian Featherwork"),
]

# sub-types for the leaves whose only people is named in the label or definition (the crosswalk then counts the term
# as covered by the leaf and writes no Peoples & cultures entry, which left these cards empty)
EXTRA = {
    "Urhobo Masks and Sculpture": [k("Water-spirit mask", "Sub-types", "maiden mask with bridal coiffure for river spirits", "https://africa.si.edu/collection/selected-artwork/2122"), k("Edjo shrine figure", "Sub-types", "large figure of a spirit kept in a shrine", "https://africa.si.edu/collection/selected-artwork/2122")],
    "Mbole Ofika Figures": [k("Ofika (hanging figure)", "Sub-types", "figure of a hanged man shown at Lilwa initiation", "https://www.clevelandart.org/print/art/2016.33"), k("Lilwa association", "Schools & phases", "the men's association whose law the figures teach", "https://www.clevelandart.org/print/art/2016.33")],
    "Buka Ceremonial Paddles": [k("Kokorra paddle", "Sub-types", "ceremonial paddle with squatting figures", "https://web.prm.ox.ac.uk/rpr/index.php/article-index/12-articles/294-degeneration-part-2.html"), k("Dance club", "Sub-types", "carved and painted club used in dance", "https://web.prm.ox.ac.uk/rpr/index.php/article-index/12-articles/294-degeneration-part-2.html")],
    "Palauan Storyboards": [k("Storyboard", "Sub-types", "portable carved narrative board", "https://www.penn.museum/documents/publications/expedition/18-1/Smith.pdf"), k("Bai beam and gable carving", "Sub-types", "carved and painted beams of the men's house", "https://www.penn.museum/documents/publications/expedition/18-1/Smith.pdf")],
    "Austral Islands Carving": [k("A'a of Rurutu", "Sub-types", "hollow deity figure covered with thirty small figures", "https://smarthistory.org/rurutu-figure-known-as-aa/"), k("Ceremonial paddle", "Sub-types", "Raivavae and Tubuai paddles with geometric relief and figures on the pommel", "https://www.penn.museum/sites/journal/938"), k("Ceremonial ladle", "Sub-types", "carved ladles of Raivavae and Tubuai", "https://www.penn.museum/sites/journal/938"), k("Fly whisk (tahiri)", "Sub-types", "whisk with a carved handle", "https://smarthistory.org/rurutu-figure-known-as-aa/")],
    "Kadiwéu Ceramics": [k("Painted vessel", "Sub-types", "vases and plates painted with scroll designs", "https://pib.socioambiental.org/en/Povo:Kadiw%C3%A9u"), k("Face and body painting", "Sub-types", "genipap and charcoal designs drawn with a sliver of bamboo", "https://pib.socioambiental.org/en/Povo:Kadiw%C3%A9u")],
    "Kusiwa": [k("Body painting with annatto", "Sub-types", "red annatto and resin motifs on the body", "https://ich.unesco.org/en/RL/oral-and-graphic-expressions-of-the-wajapi-00049"), k("Painted objects", "Sub-types", "kusiwa motifs on objects", "https://ich.unesco.org/en/RL/oral-and-graphic-expressions-of-the-wajapi-00049")],
    "Naskapi Painted Coats": [k("Painted caribou-skin coat", "Sub-types", "frock-coat cut with a triangular back gusset", "https://www.heritage.nf.ca/articles/indigenous/innu-culture.php"), k("Painted hide", "Sub-types", "caribou hide painted with the same designs, shown to the rising sun", "https://prm.web.ox.ac.uk/files/topleasethespiritspdf")],
    "Maroon Arts of Suriname": [k("Saramaka woodcarving", "Schools & phases", "central Maroon carving with tacks, inlays and pyrogravure", "https://www.encyclopedia.com/history/encyclopedias-almanacs-transcripts-and-maps/maroon-arts"), k("Eastern Maroon painted carving", "Schools & phases", "Aluku and Ndyuka carving with commercial paints", "https://www.encyclopedia.com/history/encyclopedias-almanacs-transcripts-and-maps/maroon-arts"), k("Appliqué and embroidered cape", "Sub-types", "men's shoulder capes of imported cotton", "https://www.encyclopedia.com/history/encyclopedias-almanacs-transcripts-and-maps/maroon-arts")],
    "Ye'kuana Basketry": [k("Waja", "Sub-types", "round plaited tray with figurative designs", "https://collection-online.moa.ubc.ca/search/item?category%5Bculture%5D%5B0%5D=1846581&row=4&tab=more"), k("Storage basket", "Sub-types", "square-based basket with meander designs", "https://collection-online.moa.ubc.ca/search/item?category%5Bculture%5D%5B0%5D=1846581&row=4&tab=more")],
}
for x in L: x["kinds"] = EXTRA.get(x["label"], []) + x["kinds"]
json.dump(dict(leaves={}, new_leaves=L, moves_out=[], dropped=[]),
          open(os.path.join(os.path.dirname(__file__), "result.json"), "w"), ensure_ascii=False, indent=1)
print(len(L), "new leaves")
