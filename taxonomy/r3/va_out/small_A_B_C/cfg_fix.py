"""Post-load fixes: URL replacements for unverified Wikipedia titles and extra rows for thin leaves."""
from common import *

URL = {"Gond art": "Jangarh Singh Shyam", "Tigua art": "https://collections.si.edu/search/results.htm?q=Tigua", "Sarhua": "Sarhua District",
       "Mezen painting": "https://ru.wikipedia.org/wiki/Мезенская_роспись", "Literatura de cordel": "Cordel literature", "J. Borges": "José Francisco Borges",
       "Kammavaca": "https://www.britishmuseum.org/collection/search?keyword=kammavaca", "Japanese bookbinding": "Wasōbon", "Mata ni Pachedi": "Mata Ni Pachedi",
       "Vietnamese woodblock printing": "Kim Hoàng painting", "Oegyujanggak": "Uigwe", "Vycinanka": "https://www.europeana.eu/en/search?query=vycinanka",
       "Butterfly binding": "Bookbinding", "Northern Dvina painting": "Northern Dvina", "Gorodets painting": "Gorodets painting"}
CAT = {"A6-3": [wp("Jangarh Singh Shyam", "the founder of Pardhan Gond painting")], "A6-15": [wp("Sarhua District", "the district of the painted boards")],
       "A6-16": [si("Tigua")], "A6-24": [("https://ru.wikipedia.org/wiki/Мезенская_роспись", "Wikipedia (ru): Мезенская роспись", "the tradition and its centres"), GOSKAT],
       "A6-25": [GOSKAT], "B2-3": [wp("Kim Hoàng painting", "the tradition")], "B2-5": [wp("Cordel literature", "the chapbook tradition and its woodcuts")],
       "C2-8": [bm("kammavaca"), vam("kammavaca")], "C3-4": [wp("Wasōbon", "Japanese book forms"), wp("Japanese books", "history of the Japanese book")],
       "C4-5": [eur("vycinanka")], "A4-5": [wp("Mata Ni Pachedi", "the tradition"), vam("Mata ni pachedi")],
       "A5-77": [("https://www.galleriaborghese.beniculturali.it/", "Galleria Nazionale d'Arte Moderna network", "Roman 20th-century painting")] and [("https://lagallerianazionale.com/en/", "La Galleria Nazionale, Rome", "national collection of Italian modern art incl. the Scuola Romana")],
       "A6-13": [si("retablo"), met("retablo")], "A6-22": [("https://uk.wikipedia.org/wiki/Таврійський_розпис", "Wikipedia (uk): Таврійський розпис", "the tradition")],
       "A6-23": [GOSKAT, ("https://ru.wikipedia.org/wiki/Городецкая_роспись", "Wikipedia (ru): Городецкая роспись", "the tradition")]}
ADD = {
    "A5-7": [("Nanban art", "Sub-types", "Japanese namban lacquer, the model for shell inlay", "Nanban art")],
    "A5-8": [("Folding screen", "Sub-types", "the screen form adopted from Japan", "Folding screen")],
    "A6-3": [("Bharat Bhavan", "Centres & workshops", "Bhopal arts centre where Jangarh Singh Shyam began painting (1981)", "Bharat Bhavan")],
    "A6-7": [("Cycle rickshaw", "Sub-types", "the vehicle whose panels and hoods are painted", "Cycle rickshaw")],
    "A6-15": [("Ayacucho Region", "Centres & workshops", "Andean region of Sarhua and the retablo makers", "Ayacucho Region")],
    "A6-16": [("Cotopaxi Province", "Centres & workshops", "Ecuadorian province of the Tigua communities", "Cotopaxi Province")],
    "A6-17": [("Buenos Aires", "Centres & workshops", "city of the fileteadores, UNESCO 2015", "Buenos Aires")],
    "A6-19": [("Stencil", "Sub-types", "the cut theorems used to build up the image", "Stencil")],
    "A6-21": [("Dnipropetrovsk Oblast", "Centres & workshops", "region of Petrykivka village", "Dnipropetrovsk Oblast")],
    "A6-22": [("Tauric painting (uk)", "Sub-types", "Таврійський розпис, national intangible heritage of Ukraine", "https://uk.wikipedia.org/wiki/Таврійський_розпис")],
    "A6-23": [("Distaff", "Sub-types", "spinning distaff whose base board carried the paintings", "Distaff")],
    "A6-24": [("Mezen River", "Centres & workshops", "lower Mezen villages of the painters", "Mezen River")],
    "A6-27": [("Mytishchi", "Centres & workshops", "district near Moscow where Zhostovo lies", "Mytishchi")],
    "B2-2": [("Hanoi", "Centres & workshops", "old quarter of Hanoi", "Hanoi")],
    "C1-6": [("Hui people", "Sub-types", "Chinese-speaking Muslims whose calligraphy this is", "Hui people"), ("Arabic calligraphy", "Sub-types", "the wider Arabic tradition", "Arabic calligraphy")],
    "C1-7": [("Zanabazar", "Makers", "creator of the Soyombo script (1635–1723)", "Zanabazar")],
    "C2-11": [("Joseon court ceremonies", "Sub-types", "royal weddings, funerals and processions recorded in uigwe", "Joseon")],
    "C2-19": [("Merovingian script", "Sub-types", "the Merovingian minuscule hands", "Merovingian script")],
    "C4-2": [("Rangoli", "Sub-types", "related floor designs in coloured powder", "Rangoli")],
    "C4-4": [("Tissue paper", "Sub-types", "papel de china, the usual material", "Tissue paper"), ("Mexican folk art", "Sub-types", "the wider tradition of Mexican crafts", "Mexican handcrafts and folk art")],
    "C4-6": [("Paper flower", "Sub-types", "paper flower making worldwide", "Paper flower")],
    "A4-6": [("Nakashi painters", "Makers", "the Nakashi community of Cheriyal", "Cheriyal scroll painting")],
    "A4-2": [("Chitrakar", "Sub-types", "the painter caste name of the patuas", "Chitrakar")],
    "A4-1": [("Raghurajpur", "Centres & workshops", "heritage crafts village of the chitrakars", "Raghurajpur")],
}


def apply(CFG):
    for c, v in CFG.items():
        v["add"] = [tuple([a[0], a[1], a[2], URL.get(a[3], a[3])] + list(a[4:])) for a in v.get("add", [])]
        if c in CAT:
            v["cat"] = list(v.get("cat", [])) + CAT[c]
        if c in ADD:
            v["add"] = list(v["add"]) + ADD[c]
