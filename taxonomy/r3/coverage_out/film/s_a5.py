W = "https://en.wikipedia.org/wiki/"
K = ["Shōwa Era (1954–1975)", "Heisei Era (1984–1999)", "Millennium Era (1999–2004)", "Reiwa Era (2016–)",
     "Hollywood Giant Monsters & the MonsterVerse", "Kaiju beyond Japan and Hollywood"]

def kaiju(tc, r, i):
    c = i.get("country"); y = int(r["year"])
    if c == "JP":
        if tc in ("tt0188640", "tt0255198", "tt0279112", "tt0314111", "tt0366526", "tt0399102"): return K[2]
        return K[0] if y <= 1975 else K[1] if y <= 1999 else K[3] if y >= 2016 else K[2]
    if c == "US": return K[4]
    return K[5]

TOK = ["Toho, Daiei & Toei Special-Effects Films", "Henshin Heroes (Ultra, Rider, Sentai & Power Rangers)"]
RESEC = {
 "A5-6": {"axis": "era of the Japanese kaiju eiga (Shōwa / Heisei / Millennium / Reiwa) and tradition outside Japan", "secs": K, "fn": kaiju},
 "A5-7": {"axis": "production tradition", "secs": TOK, "fn": lambda tc, r, i: TOK[1]},
}
NEW = [
 {"key": "NEW_A5_AFRO", "sub": "A5", "label": "Afrofuturist Film", "breadth": "movement",
  "defn": "Science fiction of the Afrofuturist movement (the term is Mark Dery's, 1993): Black diasporic and African speculative futures, cosmic myth and technoculture (<i>Space Is the Place</i>, <i>The Brother from Another Planet</i>, <i>Neptune Frost</i>).",
  "aliases": "Afrofuturism", "see": "A1-21 L.A. Rebellion", "src": [[W + "Afrofuturism", "Wikipedia"]]},
]
ITEMS = """
# ---- Kaiju
A5-6 | Shōwa Era (1954–1975) | Varan the Unbelievable | 1962 | Ishirō Honda | tt0056648
A5-6 | Shōwa Era (1954–1975) | Dogora | 1964 | Ishirō Honda | tt0058698
A5-6 | Shōwa Era (1954–1975) | Frankenstein vs. Baragon | 1965 | Ishirō Honda | tt0059205
A5-6 | Shōwa Era (1954–1975) | The War of the Gargantuas | 1966 | Ishirō Honda | tt0060440
A5-6 | Shōwa Era (1954–1975) | Gamera vs. Barugon | 1966 | Shigeo Tanaka | tt0060446
A5-6 | Shōwa Era (1954–1975) | Gamera vs. Gyaos | 1967 | Noriaki Yuasa | tt0061695
A5-6 | Shōwa Era (1954–1975) | Gappa the Triphibian Monster | 1967 | Haruyasu Noguchi | tt0061550
A5-6 | Shōwa Era (1954–1975) | Gamera vs. Viras | 1968 | Noriaki Yuasa | tt0063000
A5-6 | Shōwa Era (1954–1975) | Gamera vs. Guiron | 1969 | Noriaki Yuasa | tt0064360
A5-6 | Shōwa Era (1954–1975) | Gamera vs. Jiger | 1970 | Noriaki Yuasa | tt0065755
A5-6 | Shōwa Era (1954–1975) | Space Amoeba | 1970 | Ishirō Honda | tt0065776
A5-6 | Shōwa Era (1954–1975) | Gamera vs. Zigra | 1971 | Noriaki Yuasa | tt0067123
A5-6 | Heisei Era (1984–1999) | Rebirth of Mothra | 1996 | Okihiro Yoneda | tt0117089
A5-6 | Heisei Era (1984–1999) | Gamera 3: Revenge of Iris | 1999 | Shūsuke Kaneko | tt0184503
A5-6 | Millennium Era (1999–2004) | Gamera the Brave | 2006 | Ryuta Tasaki | tt0467923
# ---- Tokusatsu
A5-7 | Toho, Daiei & Toei Special-Effects Films | The Mysterians | 1957 | Ishirō Honda | tt0050251
A5-7 | Toho, Daiei & Toei Special-Effects Films | The H-Man | 1958 | Ishirō Honda | tt0051413
A5-7 | Toho, Daiei & Toei Special-Effects Films | Battle in Outer Space | 1959 | Ishirō Honda | tt0053388
A5-7 | Toho, Daiei & Toei Special-Effects Films | The Human Vapor | 1960 | Ishirō Honda | tt0053853
A5-7 | Toho, Daiei & Toei Special-Effects Films | Gorath | 1962 | Ishirō Honda | tt0056709
A5-7 | Toho, Daiei & Toei Special-Effects Films | Atragon | 1963 | Ishirō Honda | tt0057215
A5-7 | Toho, Daiei & Toei Special-Effects Films | Daimajin | 1966 | Kimiyoshi Yasuda | tt0062851
A5-7 | Toho, Daiei & Toei Special-Effects Films | Return of Daimajin | 1966 | Kenji Misumi | tt0062853
A5-7 | Toho, Daiei & Toei Special-Effects Films | Wrath of Daimajin | 1966 | Kazuo Mori | tt0062852
A5-7 | Toho, Daiei & Toei Special-Effects Films | Magic Serpent | 1966 | Tetsuya Yamauchi | tt0060579
A5-7 | Henshin Heroes (Ultra, Rider, Sentai & Power Rangers) | Prince of Space | 1959 | Eijirō Wakabayashi | tt0053464
A5-7 | Henshin Heroes (Ultra, Rider, Sentai & Power Rangers) | Zebraman | 2004 | Takashi Miike | tt0388556
# ---- Afrofuturism
NEW_A5_AFRO | | Space Is the Place | 1974 | John Coney | tt0072195
NEW_A5_AFRO | | The Brother from Another Planet | 1984 | John Sayles | tt0087004
NEW_A5_AFRO | | Welcome II the Terrordome | 1995 | Ngozi Onwurah | tt0111681
NEW_A5_AFRO | | The Last Angel of History | 1996 | John Akomfrah | -
NEW_A5_AFRO | | Pumzi | 2009 | Wanuri Kahiu | tt1508328
NEW_A5_AFRO | | Crumbs | 2015 | Miguel Llansó | tt4362764
NEW_A5_AFRO | | Neptune Frost | 2021 | Saul Williams; Anisia Uzeyman | tt11873472
"""
