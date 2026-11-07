W = "https://en.wikipedia.org/wiki/"
SC = ["Classic Hollywood Screwball (1933–1945)", "European Screwball of the 1930s", "Late Studio-Era Screwball (1946–1960s)", "Neo-Screwball (1970–)"]

def sc(tc, r, i):
    y = int(r["year"]); c = i.get("country")
    if c not in ("US", "GB", ""): return SC[1]
    return SC[0] if y <= 1945 else SC[2] if y < 1970 else SC[3]

RESEC = {"A12-4": {"axis": "studio-era phase (the field dates the cycle 1934 to the early 1940s)", "secs": SC, "fn": sc}}
NEW = [
 {"key": "NEW_A12_SEXY", "sub": "A12", "label": "Commedia sexy all'italiana", "breadth": "national cycle",
  "defn": "The Italian erotic comedy cycle of c. 1970–1985: schoolteachers, nurses, policewomen and maids (Edwige Fenech, Gloria Guida, Lino Banfi, Alvaro Vitali) in bawdy, voyeuristic farces descended from the commedia all'italiana and the decamerotici (<i>Malizia</i>, <i>L'insegnante</i>).",
  "aliases": "Italian sex comedy", "see": "A12-10 Commedia all'italiana; A12-40 Sex Comedy", "src": [[W + "Commedia_sexy_all%27italiana", "Wikipedia"]]},
 {"key": "NEW_A12_CARRYON", "sub": "A12", "label": "Carry On Film", "breadth": "national cycle",
  "defn": "The British Carry On series (Peter Rogers and Gerald Thomas, 1958–1978, revived 1992): seaside-postcard innuendo, a stock company (Sid James, Kenneth Williams, Hattie Jacques, Barbara Windsor) and genre and institution parodies (<i>Carry On Nurse</i>, <i>Carry On Up the Khyber</i>).",
  "aliases": "Carry On series", "see": "A12-7 Farce; A12-9 Ealing Comedy", "src": [[W + "Carry_On_(franchise)", "Wikipedia"]]},
 {"key": "NEW_A12_CHANCHADA", "sub": "A12", "label": "Chanchada", "breadth": "national cycle",
  "defn": "The Brazilian popular musical comedy of the 1930s–1950s, above all Atlântida's carnival films with Oscarito and Grande Otelo: samba numbers, burlesque and parodies of Hollywood (<i>Carnaval Atlântida</i>, <i>Nem Sansão Nem Dalila</i>). Its erotic successor is A15-6 Pornochanchada.",
  "aliases": "", "see": "A15-6 Pornochanchada", "src": [[W + "Chanchada", "Wikipedia"]]},
]
ITEMS = """
# screwball
A12-4 | Classic Hollywood Screwball (1933–1945) | Hands Across the Table | 1935 | Mitchell Leisen | tt0026452
A12-4 | Classic Hollywood Screwball (1933–1945) | Theodora Goes Wild | 1936 | Richard Boleslawski | tt0028355
A12-4 | Classic Hollywood Screwball (1933–1945) | Libeled Lady | 1936 | Jack Conway | tt0027884
A12-4 | Classic Hollywood Screwball (1933–1945) | Nothing Sacred | 1937 | William A. Wellman | tt0029322
A12-4 | Classic Hollywood Screwball (1933–1945) | Easy Living | 1937 | Mitchell Leisen | tt0028816
A12-4 | Classic Hollywood Screwball (1933–1945) | Topper | 1937 | Norman Z. McLeod | tt0029682
A12-4 | Classic Hollywood Screwball (1933–1945) | Bluebeard's Eighth Wife | 1938 | Ernst Lubitsch | tt0029929
A12-4 | Classic Hollywood Screwball (1933–1945) | Merrily We Live | 1938 | Norman Z. McLeod | tt0030442
A12-4 | Classic Hollywood Screwball (1933–1945) | Christmas in July | 1940 | Preston Sturges | tt0032338
A12-4 | Classic Hollywood Screwball (1933–1945) | Love Crazy | 1941 | Jack Conway | tt0033852
A12-4 | Classic Hollywood Screwball (1933–1945) | The Major and the Minor | 1942 | Billy Wilder | tt0035019
A12-4 | Classic Hollywood Screwball (1933–1945) | The More the Merrier | 1943 | George Stevens | tt0036172
# Ealing
A12-9 | | Hue and Cry | 1947 | Charles Crichton | tt0039478
A12-9 | | Passport to Pimlico | 1949 | Henry Cornelius | tt0041737
A12-9 | | Whisky Galore! | 1949 | Alexander Mackendrick | tt0042040
A12-9 | | The Titfield Thunderbolt | 1953 | Charles Crichton | tt0046436
A12-9 | | The Maggie | 1954 | Alexander Mackendrick | tt0047085
# Comedia a portuguesa
A12-11 | | A Song of Lisbon | 1933 | José Cottinelli Telmo | tt0023871
A12-11 | | The Tyrant Father | 1941 | António Lopes Ribeiro | tt0033994
A12-11 | | O Costa do Castelo | 1943 | Arthur Duarte | tt0035759
A12-11 | | A Menina da Rádio | 1944 | Arthur Duarte | -
# Bourekas
A12-12 | | Fortuna | 1966 | Menahem Golan | tt0060423
A12-12 | | Katz and Carasso | 1971 | Menahem Golan | -
A12-12 | | Salomonico | 1972 | Alfred Steinhardt | tt0121714
A12-12 | | Kazablan | 1973 | Menahem Golan | tt0071715
A12-12 | | Charlie and a Half | 1974 | Boaz Davidson | tt0133689
# Mo lei tau
A12-13 | | All for the Winner | 1990 | Jeffrey Lau; Corey Yuen | tt0104147
A12-13 | | Fight Back to School | 1991 | Gordon Chan | tt0103045
A12-13 | | Justice, My Foot! | 1992 | Johnnie To | tt0105385
A12-13 | | Royal Tramp | 1992 | Wong Jing | tt0104770
A12-13 | | King of Beggars | 1992 | Gordon Chan | tt0100963
A12-13 | | Flirting Scholar | 1993 | Lee Lik-chi | tt0108289
A12-13 | | Love on Delivery | 1994 | Lee Lik-chi | tt0110852
A12-13 | | A Chinese Odyssey Part One: Pandora's Box | 1995 | Jeffrey Lau | tt0112778
A12-13 | | Forbidden City Cop | 1996 | Stephen Chow; Vincent Kok | tt0116014
A12-13 | | King of Comedy | 1999 | Stephen Chow; Lee Lik-chi | tt0188766
# commedia sexy
NEW_A12_SEXY | | Malicious | 1973 | Salvatore Samperi | tt0070358
NEW_A12_SEXY | | Giovannona Long-Thigh | 1973 | Sergio Martino | tt0070111
NEW_A12_SEXY | | How Funny Can Sex Be? | 1973 | Dino Risi | tt0070669
NEW_A12_SEXY | | Venial Sin | 1974 | Salvatore Samperi | tt0066015
NEW_A12_SEXY | | La poliziotta | 1974 | Steno | -
NEW_A12_SEXY | | The Teasers | 1975 | Michele Massimo Tarantini | tt0073290
NEW_A12_SEXY | | The School Teacher | 1975 | Nando Cicero | tt0073170
NEW_A12_SEXY | | The Sensuous Nurse | 1975 | Nello Rossati | tt0074682
NEW_A12_SEXY | | La dottoressa del distretto militare | 1976 | Nando Cicero | -
NEW_A12_SEXY | | Classe mista | 1976 | Mariano Laurenti | -
NEW_A12_SEXY | | Pierino contro tutti | 1981 | Marino Girolami | tt0082904
# Carry On
NEW_A12_CARRYON | | Carry on Sergeant | 1958 | Gerald Thomas | tt0051453
NEW_A12_CARRYON | | Carry on Nurse | 1959 | Gerald Thomas | tt0051452
NEW_A12_CARRYON | | Carry on Teacher | 1959 | Gerald Thomas | tt0052676
NEW_A12_CARRYON | | Carry on Regardless | 1961 | Gerald Thomas | tt0054727
NEW_A12_CARRYON | | Carry on Cleo | 1964 | Gerald Thomas | tt0057918
NEW_A12_CARRYON | | Carry on Spying | 1964 | Gerald Thomas | tt0057920
NEW_A12_CARRYON | | Carry on Jack | 1964 | Gerald Thomas | tt0057919
NEW_A12_CARRYON | | Carry on Cowboy | 1965 | Gerald Thomas | tt0059014
NEW_A12_CARRYON | | Carry on Screaming! | 1966 | Gerald Thomas | tt0060214
NEW_A12_CARRYON | | Carry on Doctor | 1967 | Gerald Thomas | tt0061450
NEW_A12_CARRYON | | Carry on Follow That Camel | 1967 | Gerald Thomas | tt0061680
NEW_A12_CARRYON | | Carry on Up the Khyber | 1968 | Gerald Thomas | tt0062782
NEW_A12_CARRYON | | Carry on Camping | 1969 | Gerald Thomas | tt0064133
NEW_A12_CARRYON | | Carry on Again Doctor | 1969 | Gerald Thomas | tt0064132
NEW_A12_CARRYON | | Carry on Up the Jungle | 1970 | Gerald Thomas | tt0065525
NEW_A12_CARRYON | | Carry on Loving | 1970 | Gerald Thomas | tt0065524
NEW_A12_CARRYON | | Carry on Henry VIII | 1971 | Gerald Thomas | tt0066894
NEW_A12_CARRYON | | Carry on at Your Convenience | 1971 | Gerald Thomas | tt0066895
NEW_A12_CARRYON | | Carry on Matron | 1972 | Gerald Thomas | tt0068339
NEW_A12_CARRYON | | Carry on Abroad | 1972 | Gerald Thomas | tt0069847
NEW_A12_CARRYON | | Carry on Dick | 1974 | Gerald Thomas | tt0071281
NEW_A12_CARRYON | | Carry on Columbus | 1992 | Gerald Thomas | tt0103927
# Chanchada
NEW_A12_CHANCHADA | | Alô Alô Carnaval | 1936 | Adhemar Gonzaga | -
NEW_A12_CHANCHADA | | Este Mundo é um Pandeiro | 1947 | Watson Macedo | -
NEW_A12_CHANCHADA | | Aviso aos Navegantes | 1950 | Watson Macedo | -
NEW_A12_CHANCHADA | | Carnaval Atlântida | 1952 | José Carlos Burle | -
NEW_A12_CHANCHADA | | Nem Sansão Nem Dalila | 1954 | Carlos Manga | -
NEW_A12_CHANCHADA | | Matar ou Correr | 1954 | Carlos Manga | -
NEW_A12_CHANCHADA | | O Homem do Sputnik | 1959 | Carlos Manga | -
"""
