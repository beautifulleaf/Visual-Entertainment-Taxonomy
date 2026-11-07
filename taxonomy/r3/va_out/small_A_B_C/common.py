"""Shared helpers for the small_A_B_C configs."""
import re
from urllib.parse import quote_plus


def met(q, what=None):
    return ("https://www.metmuseum.org/art/collection/search?q=" + quote_plus(q), "The Met collection search: " + q, what or f"all Met objects matching '{q}'")


def vam(q, what=None):
    return ("https://collections.vam.ac.uk/search/?q=" + quote_plus(q), "V&A Collections search: " + q, what or f"all V&A objects matching '{q}'")


def bm(q, what=None):
    return ("https://www.britishmuseum.org/collection/search?keyword=" + quote_plus(q), "British Museum collection search: " + q, what or f"all British Museum objects matching '{q}'")


def aic(q, what=None):
    return ("https://www.artic.edu/collection?q=" + quote_plus(q), "Art Institute of Chicago collection: " + q, what or f"all AIC works matching '{q}'")


def tate(q, what=None):
    return ("https://www.tate.org.uk/search?q=" + quote_plus(q), "Tate collection search: " + q, what or f"Tate works and texts matching '{q}'")


def moma(q, what=None):
    return ("https://www.moma.org/collection/?q=" + quote_plus(q), "MoMA collection search: " + q, what or f"MoMA works matching '{q}'")


def harvard(q, what=None):
    return ("https://harvardartmuseums.org/collections?q=" + quote_plus(q), "Harvard Art Museums: " + q, what or f"Harvard Art Museums objects matching '{q}'")


def si(q, what=None):
    return ("https://collections.si.edu/search/results.htm?q=" + quote_plus(q), "Smithsonian Collections Search: " + q, what or f"Smithsonian objects (incl. Freer|Sackler) matching '{q}'")


def eur(q, what=None):
    return ("https://www.europeana.eu/en/search?query=" + quote_plus(q), "Europeana: " + q, what or f"European museum and library records matching '{q}'")


def wp(title, what):
    return ("https://en.wikipedia.org/wiki/" + title.replace(" ", "_"), "Wikipedia: " + title.replace("_", " "), what)


def ukiyo(q):
    return ("https://ukiyo-e.org/search?q=" + quote_plus(q), "Ukiyo-e.org: " + q, f"Japanese prints matching '{q}' pooled from 20+ museum collections")


BODLEIAN = ("https://digital.bodleian.ox.ac.uk/", "Digital Bodleian", "digitised manuscripts of the Bodleian Libraries, Oxford")
GALLICA = ("https://gallica.bnf.fr/", "Gallica (BnF)", "digitised manuscripts and prints of the Bibliothèque nationale de France")
VHMML = ("https://www.vhmml.org/readingRoom/", "vHMML Reading Room", "Hill Museum & Manuscript Library digitised manuscripts (Ethiopia, Mali, Middle East, Armenia...)")
ECOD = ("https://www.e-codices.unifr.ch/en", "e-codices", "virtual manuscript library of Switzerland (St Gall, Einsiedeln...)")
HAR = ("https://www.himalayanart.org/", "Himalayan Art Resources", "over 60,000 images of Himalayan and Tibetan art, indexed by tradition and painting style")
IDP = ("https://idp.bl.uk/", "International Dunhuang Programme", "digitised manuscripts and paintings from Dunhuang and the Silk Road")
SHAHNAMA = ("https://shahnama.caret.cam.ac.uk/", "Shahnama Project (Cambridge)", "illustrated Shahnama manuscripts and their paintings, catalogued worldwide")
DIGIVAT = ("https://digi.vatlib.it/", "DigiVatLib", "digitised manuscripts of the Vatican Library")
PINAKES = ("https://pinakes.irht.cnrs.fr/", "Pinakes (IRHT)", "census of Greek manuscripts and their holding libraries")
MATENADARAN = ("https://www.matenadaran.am/", "Matenadaran", "the Mesrop Mashtots Institute of Ancient Manuscripts, Yerevan")
LEIDEN = ("https://digitalcollections.universiteitleiden.nl/", "Leiden University Digital Collections", "Indonesian, Malay and other Asian manuscripts of Leiden University Library")
COLBASE = ("https://colbase.nich.go.jp/", "ColBase", "integrated collections database of Japan's four national museums")
BUNKA = ("https://bunka.nii.ac.jp/", "Cultural Heritage Online (Japan)", "Japan's national database of designated cultural properties")
NGA_AU = ("https://searchthecollection.nga.gov.au/", "National Gallery of Australia collection", "searchable collection incl. the largest holding of Aboriginal and Torres Strait Islander art")
GOSKAT = ("https://goskatalog.ru/portal/", "Goskatalog", "State Catalogue of the Museum Fund of the Russian Federation")
EMUSEUM_KR = ("https://www.emuseum.go.kr/", "e-Museum (Korea)", "collections of Korea's national and public museums")
NPM = ("https://digitalarchive.npm.gov.tw/", "National Palace Museum Open Data", "digital archive of the National Palace Museum, Taipei")
MUS_INDIA = ("https://museumsofindia.gov.in/", "Museums of India", "national portal of Indian museum collections")
LAMBIEK = ("https://www.lambiek.net/", "Lambiek Comiclopedia", "biographical encyclopedia of over 14,000 comics artists")
GCD = ("https://www.comics.org/", "Grand Comics Database", "index of comics issues, stories and creators worldwide")
RKD = ("https://rkd.nl/", "RKD – Netherlands Institute for Art History", "artists and images database for Netherlandish and Flemish art")


def y(x):
    return x.get("_y")


def low(x, *keys):
    return " ".join((x.get(k) or "") for k in keys).lower()


def G(d):
    """{"Group": "name; name; ..."} -> {name: group}"""
    out = {}
    for g, names in d.items():
        for n in names.split(";"):
            n = n.strip()
            if n:
                out[n] = g
    return out
