"""helpers for hand-written kinds and catalogues"""
from urllib.parse import quote_plus

def wurl(a): return "https://en.wikipedia.org/wiki/" + a.replace(" ", "_")
def surl(q): return "https://en.wikipedia.org/w/index.php?search=" + quote_plus(q)

def W(name, group, gloss, art=None, mk=0):
    return [name, group, gloss, "r3 " + wurl(art or name), mk]
def SR(name, group, gloss, q=None, mk=0):
    return [name, group, gloss, "r3 " + surl(q or name), mk]
def M(name, group, gloss, art=None):
    return W(name, group, gloss, art, 1)
def MS(name, group, gloss, q=None):
    return SR(name, group, gloss, q, 1)

# catalogues
def UN(i, label, what="UNESCO World Heritage List entry: description, maps and component sites"):
    return [f"https://whc.unesco.org/en/list/{i}", f"UNESCO World Heritage List: {label}", what]
def UNS(q, what):
    return [f"https://whc.unesco.org/en/list/?search={quote_plus(q)}", f"UNESCO World Heritage List search: {q}", what]
def WP(a, what, label=None):
    return [wurl(a), label or f"Wikipedia: {a}", what]
def COM(q, what="Wikimedia Commons media search: photographs of all recorded sites and works"):
    return [f"https://commons.wikimedia.org/w/index.php?search={quote_plus(q)}", f"Wikimedia Commons: {q}", what]
BRAD = ["https://www.bradshawfoundation.com/", "Bradshaw Foundation rock art archive", "online archive of world rock art, organised by region and site"]
TARA = ["https://africanrockart.org/", "Trust for African Rock Art (TARA)", "photographic archive of rock art across Africa"]
BMRA = ["https://www.britishmuseum.org/collection/search?keyword=rock%20art", "British Museum collection: rock art", "includes the African Rock Art Image Project (c. 25,000 photographs, TARA archive)"]
def BM(q, what): return [f"https://www.britishmuseum.org/collection/search?keyword={quote_plus(q)}", f"British Museum collection search: {q}", what]
def MET(q, what): return [f"https://www.metmuseum.org/art/collection/search?q={quote_plus(q)}", f"Metropolitan Museum collection search: {q}", what]
def VAM(q, what): return [f"https://collections.vam.ac.uk/search/?q={quote_plus(q)}", f"V&A collections search: {q}", what]
WGA = ["https://www.wga.hu/", "Web Gallery of Art", "searchable database of European painting and fresco cycles to 1900"]
PRINCETON = ["https://theindex.princeton.edu/", "Index of Medieval Art (Princeton)", "iconographic database of medieval works, including wall paintings and mosaics"]
ARCHNET = ["https://www.archnet.org/", "Archnet", "archive of Islamic architecture and its sites, with images and bibliography"]
IAH = ["https://islamicarchitecturalheritage.com/", "Islamic Architectural Heritage", "photographic archive of Islamic monuments by country"]
HIST_ENG = ["https://historicengland.org.uk/listing/the-list/", "National Heritage List for England", "statutory register of scheduled monuments and listed sites"]
CANMORE = ["https://canmore.org.uk/", "Canmore (Historic Environment Scotland)", "national record of Scotland's archaeological sites, incl. carved rocks"]
POP = ["https://pop.culture.gouv.fr/", "POP: plateforme ouverte du patrimoine (Mérimée/Palissy)", "French national register of protected monuments and their decoration"]
ICCD = ["https://catalogo.beniculturali.it/", "Catalogo generale dei Beni Culturali", "Italian national catalogue of cultural heritage"]
ASI = ["https://asi.nic.in/", "Archaeological Survey of India", "national monument lists by state"]
NRHP = ["https://www.nps.gov/subjects/nationalregister/index.htm", "US National Register of Historic Places", "national register, incl. listed rock-art and earthwork sites"]
HAR = ["https://www.himalayanart.org/", "Himalayan Art Resources", "database of Himalayan and Tibetan art, incl. mural programmes"]
HUNT = ["https://huntington.wmc.ohio-state.edu/", "Huntington Photographic Archive of Buddhist and Asian Art", "photographic survey of South and Central Asian monuments"]
IDP = ["https://idp.bl.uk/", "International Dunhuang Programme", "digitised Silk Road manuscripts, paintings and site records"]
BUNKA = ["https://bunka.nii.ac.jp/", "Cultural Heritage Online (Japan)", "Japanese national database of designated cultural properties"]
ICH = ["https://ich.unesco.org/en/lists", "UNESCO Intangible Cultural Heritage Lists", "inscribed practices with nomination files and films"]
WELL = ["https://wellcomecollection.org/search/works?query=tattoo", "Wellcome Collection: tattoo", "historical images and objects of tattooing worldwide"]
SAHA = ["https://www.sahapedia.org/", "Sahapedia", "open encyclopedia of Indian arts and cultural heritage"]
