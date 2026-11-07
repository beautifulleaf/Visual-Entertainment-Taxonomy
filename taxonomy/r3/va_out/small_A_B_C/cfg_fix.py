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

GLOSS = {
    "A5-12": {"Utopia (Anmatyerre / Alyawarr batik and painting)": "Utopia homelands NE of Alice Springs: batik (1977) then acrylic painting (Kngwarreye, Petyarre)",
              "Papunya Tula (Western Desert painting)": "Papunya, NT: the founding company of the movement (1972)",
              "Yuendumu / Lajamanu (Warlpiri: Warlukurlangu, Warnayaka)": "Warlpiri art centres of Yuendumu and Lajamanu",
              "APY / Ngaanyatjarra Lands art centres (Ernabella, Tjala, Spinifex, Tjanpi)": "Pitjantjatjara and Ngaanyatjarra art centres of SA and WA",
              "Balgo (Warlayirti Artists)": "Balgo (Wirrimanu), Kimberley edge, from 1987", "Haasts Bluff (Ikuntji Artists)": "Ikuntji art centre, Haasts Bluff, NT (1992)",
              "Jukurrpa Designs": "Alice Springs Aboriginal design studio", "Ernabella Arts": "Pukatja (Ernabella), SA, oldest Aboriginal art centre (1948)",
              "Tjala Arts": "Amata, APY Lands, SA", "Lajamanu (Warnayaka)": "Warnayaka Art Centre, Lajamanu, NT"},
    "A5-13": {"Tiwi ochre painting (Munupi, Jilamara)": "ochre painting of the Tiwi Islands (Munupi, Jilamara art centres)", "Warmun / East Kimberley (Gija) painting": "Gija ochre painting of Warmun (Turkey Creek), WA",
              "Fitzroy Crossing (Mangkaja Arts)": "Mangkaja Arts, Fitzroy Crossing, WA (1981)", "Mornington Island (Lardil, Kaiadilt) art": "Mornington Island Art, Gulf of Carpentaria, Qld",
              "Ngukurr (Roper River) painting": "Ngukurr Arts, Roper River, NT", "Waringarri Aboriginal Arts": "Kununurra art centre, East Kimberley (1985)"},
    "A6-18": {"x-ray style": "West Arnhem Land depiction of skeleton and organs", "Eastern Arnhem Land (Yolngu) bark painting (Yirrkala, Galiwin'ku)": "Yolŋu clan painting of Yirrkala and Galiwin'ku",
              "Western Arnhem Land bark painting (Kunwinjku, Oenpelli)": "Kunwinjku painting of Gunbalanya (Oenpelli) and Maningrida's west",
              "Groote Eylandt bark painting (Anindilyakwa)": "Anindilyakwa painting of Groote Eylandt", "Central Arnhem Land bark painting (Maningrida, Ramingining, Milingimbi)": "Maningrida, Ramingining and Milingimbi painting",
              "Buku-Larrnggay Mulka Centre (Yirrkala)": "Yolŋu art centre of Yirrkala (1976)", "Injalak Arts (Gunbalanya/Oenpelli)": "Kunwinjku art centre of Gunbalanya (1989)",
              "Maningrida Arts & Culture": "Maningrida art centre, Central Arnhem Land (1973)", "Ramingining and Milingimbi": "Central Arnhem Land communities (Bula'bula Arts, Milingimbi Art and Culture)"},
    "A6-31": {"Hector Hyppolite": "Vodou priest-painter (1894–1948), first master of the Centre d'Art", "Philomé Obin": "Cap-Haïtien painter (1892–1986)", "Préfète Duffaut": "Jacmel painter of imaginary cities (1923–2012)"},
    "B1-3": {"Newspaper comic strips": "daily and Sunday strips from the 1890s", "Underground comix": "self-published adult comics of the late 1960s–70s", "Superhero comics": "the genre launched by Superman (1938)",
             "Golden Age of Comic Books": "c. 1938–1956", "Winsor McCay": "Little Nemo (1867–1934)", "George Herriman": "Krazy Kat (1880–1944)", "Will Eisner": "The Spirit, A Contract with God (1917–2005)",
             "Robert Crumb": "underground cartoonist (b. 1943)", "Art Spiegelman": "Maus (b. 1948)"},
    "B2-4": {"Zhuxianzhen New Year prints (Kaifeng)": "Henan, oldest centre (Song origin)", "Taohuawu (Suzhou) prints": "Suzhou, Jiangsu, refined colour prints from the Ming",
             "Yangliuqing New Year prints (Tianjin)": "Tianjin, printed then hand-painted", "Weifang / Yangjiabu New Year prints": "Shandong", "Wuqiang New Year prints (Hebei)": "Hebei", "Mianzhu New Year prints (Sichuan)": "Sichuan"},
    "B2-9": {"Belle Époque poster": "colour lithograph posters, Paris 1870s–1914", "American poster of the 1890s": "literary and magazine posters", "Italian poster (Ricordi)": "posters printed by Ricordi, Milan",
             "Swiss poster": "object and typographic posters from the 1900s", "British poster": "railway and Underground posters", "Art Deco poster": "France 1920s–30s", "Psychedelic poster": "San Francisco concert posters, 1960s",
             "Jules Chéret": "father of the colour poster (1836–1932)", "Alphonse Mucha": "Gismonda (1894) (1860–1939)", "Leonetto Cappiello": "Le Thermogène (1909) (1875–1942)"},
    "B2-11": {"ROSTA windows": "stencilled news posters of the Russian Telegraph Agency, 1919–22", "Constructivist photomontage poster": "1920s–30s photomontage of Klutsis and Kulagina",
              "Dmitry Moor": "Have You Volunteered? (1920) (1883–1946)", "Viktor Deni": "Civil War caricaturist (1893–1946)", "Viktor Koretsky": "wartime and Cold War posters (1909–1998)", "Irakli Toidze": "The Motherland Calls! (1941) (1902–1985)"},
    "B2-12": {"Henryk Tomaszewski": "founder of the school (1914–2005)", "Jan Lenica": "poster artist and animator (1928–2001)", "Roman Cieślewicz": "poster and collage artist (1930–1996)",
              "Waldemar Świerzy": "poster artist (1931–2013)", "Franciszek Starowieyski": "poster artist (1930–2009)"},
    "C2-5": {"South Indian palm-leaf (Tamil, Malayalam, Telugu, Kannada)": "incised olas of South India", "Odia palm-leaf": "incised and illustrated palm leaves of Odisha", "Sinhalese palm-leaf": "Buddhist ola books of Sri Lanka",
             "Nepalese (Newar) manuscripts": "illuminated Buddhist palm-leaf books of the Kathmandu Valley", "Khmer manuscripts": "Cambodian palm-leaf books", "Southeast Asian palm-leaf (unlocalised)": "palm-leaf books of mainland Southeast Asia"},
    "A5-91": {"Christo and Jeanne-Claude": "wrapping artists (1935–2020; 1935–2009)"},
    "C1-4": {"Muhammad Husain Zarin Qalam": "Muhammad Husain Kashmiri 'Zarin Qalam', Akbar's nasta'liq master (d. 1611)"},
}


def apply_gloss(CFG):
    for c, d in GLOSS.items():
        CFG.setdefault(c, {}).setdefault("gloss", {}).update(d)
