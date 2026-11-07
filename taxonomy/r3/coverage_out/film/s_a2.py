NOIR = ["American Noir: Wartime Phase (1940–1945)", "American Noir: Post-War Phase (1946–1949)", "American Noir: Late Phase (1950–1962)",
        "British Noir", "French Noir & Poetic-Realist Precursors", "Italian & Other European Noir", "Japanese Noir (Nikkatsu & Studio Noir)", "Latin American Noir (Argentina & Mexico)"]

def noir(tc, r, i):
    c = i.get("country", ""); y = int(r["year"])
    if c == "US": return NOIR[0] if y <= 1945 else NOIR[1] if y <= 1949 else NOIR[2]
    return {"GB": NOIR[3], "FR": NOIR[4], "IT": NOIR[5], "NO": NOIR[5], "JP": NOIR[6], "AR": NOIR[7], "MX": NOIR[7]}.get(c)

YAK = ["Early & Post-War Yakuza Films", "Borderless Action & Ninkyō Eiga (1959–1972)", "Jitsuroku Eiga (1973–1980s)",
       "V-Cinema & the Auteur Yakuza Film (1989–)", "Yakuza Films Made Abroad"]
RESEC = {
 "A2-24": {"axis": "national tradition and (for Hollywood) Schrader's phases of classic noir", "secs": NOIR, "fn": noir},
 "A2-3": {"axis": "era / production cycle of the Japanese yakuza film", "secs": YAK, "map": {
    "tt0054709": YAK[0], "tt0061101": YAK[1], "tt0070246": YAK[2], "tt0073918": YAK[4], "tt0098967": YAK[3], "tt0108188": YAK[3],
    "tt0119250": YAK[3], "tt0221111": YAK[3], "tt0222851": YAK[3], "tt0361668": YAK[3], "tt1462667": YAK[3], "tt2011311": YAK[4],
    "tt10228168": YAK[3], "tt33029866": YAK[3]}},
}
ITEMS = """
# ---- Film noir: national noir additions
A2-24 | British Noir | Brighton Rock | 1948 | John Boulting | tt0039220
A2-24 | British Noir | They Made Me a Fugitive | 1947 | Alberto Cavalcanti | tt0039895
A2-24 | British Noir | It Always Rains on Sunday | 1947 | Robert Hamer | tt0040481
A2-24 | British Noir | The October Man | 1947 | Roy Ward Baker | tt0039676
A2-24 | British Noir | Dear Murderer | 1947 | Arthur Crabtree | tt0039306
A2-24 | British Noir | Daybreak | 1948 | Compton Bennett | tt0039304
A2-24 | British Noir | Noose | 1948 | Edmond T. Gréville | tt0040651
A2-24 | British Noir | Obsession | 1949 | Edward Dmytryk | tt0041460
A2-24 | British Noir | Pool of London | 1951 | Basil Dearden | tt0042851
A2-24 | British Noir | The Long Memory | 1953 | Robert Hamer | tt0044849
A2-24 | British Noir | Tiger in the Smoke | 1956 | Roy Ward Baker | tt0049854
A2-24 | British Noir | Nowhere to Go | 1958 | Seth Holt | tt0052013
A2-24 | British Noir | Hell Is a City | 1960 | Val Guest | tt0053900
A2-24 | French Noir & Poetic-Realist Precursors | Le Dernier tournant | 1939 | Pierre Chenal | tt0031222
A2-24 | French Noir & Poetic-Realist Precursors | Dédée d'Anvers | 1948 | Yves Allégret | tt0039344
A2-24 | French Noir & Poetic-Realist Precursors | Such a Pretty Little Beach | 1949 | Yves Allégret | tt0040917
A2-24 | French Noir & Poetic-Realist Precursors | Thérèse Raquin | 1953 | Marcel Carné | tt0046429
A2-24 | French Noir & Poetic-Realist Precursors | Razzia sur la chnouf | 1955 | Henri Decoin | tt0048543
A2-24 | French Noir & Poetic-Realist Precursors | Deadlier Than the Male | 1956 | Julien Duvivier | tt0051172
A2-24 | Italian & Other European Noir | Story of a Love Affair | 1950 | Michelangelo Antonioni | tt0042355
A2-24 | Latin American Noir (Argentina & Mexico) | Distinto amanecer | 1943 | Julio Bracho | tt0035807
A2-24 | Latin American Noir (Argentina & Mexico) | La Otra | 1946 | Roberto Gavaldón | tt0038813
A2-24 | Latin American Noir (Argentina & Mexico) | In the Palm of Your Hand | 1951 | Roberto Gavaldón | tt0042434
A2-24 | Latin American Noir (Argentina & Mexico) | Night Falls | 1952 | Roberto Gavaldón | tt0265417
A2-24 | American Noir: Wartime Phase (1940–1945) | The Glass Key | 1942 | Stuart Heisler | tt0034798
A2-24 | American Noir: Post-War Phase (1946–1949) | The Dark Corner | 1946 | Henry Hathaway | tt0038453
A2-24 | American Noir: Post-War Phase (1946–1949) | Dead Reckoning | 1947 | John Cromwell | tt0039305
A2-24 | American Noir: Post-War Phase (1946–1949) | Kiss of Death | 1947 | Henry Hathaway | tt0039536
A2-24 | American Noir: Post-War Phase (1946–1949) | Pitfall | 1948 | André de Toth | tt0040695
A2-24 | American Noir: Post-War Phase (1946–1949) | Too Late for Tears | 1949 | Byron Haskin | tt0041968
A2-24 | American Noir: Late Phase (1950–1962) | Armored Car Robbery | 1950 | Richard Fleischer | tt0042206
A2-24 | American Noir: Late Phase (1950–1962) | Caged | 1950 | John Cromwell | tt0042296
A2-24 | American Noir: Late Phase (1950–1962) | The Narrow Margin | 1952 | Richard Fleischer | tt0044954
A2-24 | American Noir: Late Phase (1950–1962) | Crime Wave | 1954 | André de Toth | tt0046878
A2-24 | American Noir: Late Phase (1950–1962) | The Big Knife | 1955 | Robert Aldrich | tt0047880
A2-24 | American Noir: Late Phase (1950–1962) | House of Bamboo | 1955 | Samuel Fuller | tt0048182
A2-24 | American Noir: Late Phase (1950–1962) | The Crimson Kimono | 1959 | Samuel Fuller | tt0052713
A2-24 | American Noir: Late Phase (1950–1962) | Underworld U.S.A. | 1961 | Samuel Fuller | tt0055571
# ---- Yakuza
A2-3 | Borderless Action & Ninkyō Eiga (1959–1972) | Theater of Life: Hishakaku | 1963 | Tadashi Sawashima | -
A2-3 | Borderless Action & Ninkyō Eiga (1959–1972) | Abashiri Prison | 1965 | Teruo Ishii | -
A2-3 | Borderless Action & Ninkyō Eiga (1959–1972) | Tattooed Life | 1965 | Seijun Suzuki | tt0059320
A2-3 | Borderless Action & Ninkyō Eiga (1959–1972) | Brutal Tales of Chivalry | 1965 | Kiyoshi Saeki | -
A2-3 | Borderless Action & Ninkyō Eiga (1959–1972) | Big Time Gambling Boss | 1968 | Kōsaku Yamashita | tt0199349
A2-3 | Borderless Action & Ninkyō Eiga (1959–1972) | Red Peony Gambler | 1968 | Kōsaku Yamashita | -
A2-3 | Borderless Action & Ninkyō Eiga (1959–1972) | Sympathy for the Underdog | 1971 | Kinji Fukasaku | tt0066806
A2-3 | Jitsuroku Eiga (1973–1980s) | Street Mobster | 1972 | Kinji Fukasaku | tt0068629
A2-3 | Jitsuroku Eiga (1973–1980s) | Hiroshima Death Match | 1973 | Kinji Fukasaku | tt0070245
A2-3 | Jitsuroku Eiga (1973–1980s) | Proxy War | 1973 | Kinji Fukasaku | tt0070244
A2-3 | Jitsuroku Eiga (1973–1980s) | Police Tactics | 1974 | Kinji Fukasaku | tt0071696
A2-3 | Jitsuroku Eiga (1973–1980s) | Final Episode | 1974 | Kinji Fukasaku | tt0226018
A2-3 | Jitsuroku Eiga (1973–1980s) | Graveyard of Honor | 1975 | Kinji Fukasaku | tt0073207
A2-3 | Jitsuroku Eiga (1973–1980s) | Cops vs. Thugs | 1975 | Kinji Fukasaku | tt0073234
A2-3 | Jitsuroku Eiga (1973–1980s) | Yakuza Graveyard | 1976 | Kinji Fukasaku | tt0075441
A2-3 | V-Cinema & the Auteur Yakuza Film (1989–) | Shinjuku Triad Society | 1995 | Takashi Miike | tt0258960
A2-3 | V-Cinema & the Auteur Yakuza Film (1989–) | Fudoh: The New Generation | 1996 | Takashi Miike | tt0123092
A2-3 | V-Cinema & the Auteur Yakuza Film (1989–) | Rainy Dog | 1997 | Takashi Miike | tt0142316
A2-3 | V-Cinema & the Auteur Yakuza Film (1989–) | Graveyard of Honor | 2002 | Takashi Miike | tt0316599
A2-3 | V-Cinema & the Auteur Yakuza Film (1989–) | The Blood of Wolves | 2018 | Kazuya Shiraishi | tt6622902
A2-3 | V-Cinema & the Auteur Yakuza Film (1989–) | Yakuza and the Family | 2020 | Michihito Fujii | tt13356884
# ---- Pinky violence
A2-10 | | Female Prisoner Scorpion: Beast Stable | 1973 | Shunya Itō | tt0226875
A2-10 | | Female Prisoner Scorpion: #701's Grudge Song | 1973 | Yasuharu Hasebe | tt0226873
A2-10 | | The Joy of Torture | 1968 | Teruo Ishii | tt0059816
A2-10 | | Inferno of Torture | 1969 | Teruo Ishii | tt0142920
A2-10 | | Orgies of Edo | 1969 | Teruo Ishii | tt0143010
A2-10 | | Stray Cat Rock: Delinquent Girl Boss | 1970 | Yasuharu Hasebe | tt0204504
A2-10 | | Stray Cat Rock: Sex Hunter | 1970 | Yasuharu Hasebe | tt0223783
A2-10 | | Girl Boss Guerrilla | 1972 | Norifumi Suzuki | tt0451930
A2-10 | | Sex & Fury | 1973 | Norifumi Suzuki | tt0070085
A2-10 | | Terrifying Girls' High School: Lynch Law Classroom | 1973 | Norifumi Suzuki | tt0451788
A2-10 | | Female Yakuza Tale: Inquisition and Torture | 1973 | Teruo Ishii | tt0142998
A2-10 | | Criminal Woman: Killing Melody | 1973 | Atsushi Mihori | tt0451984
A2-10 | | School of the Holy Beast | 1974 | Norifumi Suzuki | tt0224077
A2-10 | | Zero Woman: Red Handcuffs | 1974 | Yukio Noda | tt0283693
# ---- Poliziottesco
A2-4 | | Execution Squad | 1972 | Steno | tt0069109
A2-4 | | The Italian Connection | 1972 | Fernando Di Leo | tt0068902
A2-4 | | The Boss | 1973 | Fernando Di Leo | tt0069818
A2-4 | | High Crime | 1973 | Enzo G. Castellari | tt0070552
A2-4 | | Revolver | 1973 | Sergio Sollima | tt0073626
A2-4 | | Mean Frank and Crazy Tony | 1973 | Michele Lupo | tt0069979
A2-4 | | Almost Human | 1974 | Umberto Lenzi | tt0071840
A2-4 | | Street Law | 1974 | Enzo G. Castellari | tt0071330
A2-4 | | Shoot First, Die Later | 1974 | Fernando Di Leo | tt0072010
A2-4 | | Violent Rome | 1975 | Marino Girolami | tt0073633
A2-4 | | Syndicate Sadists | 1975 | Umberto Lenzi | tt0073051
A2-4 | | The Tough Ones | 1976 | Umberto Lenzi | tt0075152
A2-4 | | Violent Naples | 1976 | Umberto Lenzi | tt0074952
A2-4 | | The Big Racket | 1976 | Enzo G. Castellari | tt0074586
A2-4 | | Live Like a Cop, Die Like a Man | 1976 | Ruggero Deodato | tt0075375
A2-4 | | Colt 38 Special Squad | 1976 | Massimo Dallamano | tt0075115
# ---- Cine quinqui
A2-9 | | Street Warriors | 1977 | José Antonio de la Loma | tt0075060
A2-9 | | Perros callejeros II | 1979 | José Antonio de la Loma | -
A2-9 | | Navajeros | 1980 | Eloy de la Iglesia | tt0081218
A2-9 | | Los últimos golpes de El Torete | 1980 | José Antonio de la Loma | -
A2-9 | | Pals | 1982 | Eloy de la Iglesia | tt0080554
A2-9 | | El pico | 1983 | Eloy de la Iglesia | tt0086104
A2-9 | | El pico 2 | 1984 | Eloy de la Iglesia | tt0087913
A2-9 | | Yo, el Vaquilla | 1985 | José Antonio de la Loma | tt0090354
# ---- Mumbai noir
A2-2 | | Parinda | 1989 | Vidhu Vinod Chopra | tt0102636
A2-2 | | Agneepath | 1990 | Mukul S. Anand | tt0098999
A2-2 | | Vaastav: The Reality | 1999 | Mahesh Manjrekar | tt0220832
A2-2 | | Company | 2002 | Ram Gopal Varma | tt0296574
A2-2 | | Black Friday | 2004 | Anurag Kashyap | tt0400234
A2-2 | | Ab Tak Chhappan | 2004 | Shimit Amin | tt0402014
A2-2 | | D | 2005 | Vishram Sawant | tt0454435
A2-2 | | Sarkar | 2005 | Ram Gopal Varma | tt0432047
A2-2 | | Shootout at Lokhandwala | 2007 | Apoorva Lakhia | tt0811066
A2-2 | | Once Upon a Time in Mumbaai | 2010 | Milan Luthria | tt1395054
A2-2 | | Shootout at Wadala | 2013 | Sanjay Gupta | tt2301155
A2-2 | | Bombay Velvet | 2015 | Anurag Kashyap | tt2979920
A2-2 | | Daddy | 2017 | Ashim Ahluwalia | tt6926486
"""
