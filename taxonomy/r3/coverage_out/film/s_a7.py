W = "https://en.wikipedia.org/wiki/"
WX = ["New-School Wuxia (1966–1984: King Hu, Chang Cheh, Chu Yuan)", "Hong Kong New Wave Wuxia (1985–1999)", "Wuxia Blockbusters (2000–)"]
NJ = ["Japanese Ninja Films", "Hong Kong Ninja Films", "Cannon & Western Ninja Boom (1981–)"]
NJMAP = {"tt0087805": NJ[2], "tt0088708": NJ[2], "tt1186367": NJ[2], "tt15358226": NJ[2], "tt8404256": NJ[2]}
RESEC = {
 "A7-12": {"axis": "era / school of the wuxia film", "secs": WX,
           "fn": lambda tc, r, i: WX[0] if int(r["year"]) < 1985 else WX[1] if int(r["year"]) < 2000 else WX[2]},
 "A7-14": {"axis": "national tradition / production cycle", "secs": NJ, "map": NJMAP},
}
SECS = [("A7-11", "Bruceploitation")]
NEW = [
 {"key": "NEW_A7_LUCHA", "sub": "A7", "label": "Lucha Film", "breadth": "national cycle",
  "defn": "The Mexican luchador film (1952–1980s): masked professional wrestlers — El Santo, Blue Demon, Mil Máscaras, the Wrestling Women — fighting vampires, mummies, mad scientists and Martians in action-horror-science-fiction serials (<i>Santo vs. the Vampire Women</i>).",
  "aliases": "luchador film; cine de luchadores", "see": "A4 Horror", "src": [[W + "Lucha_film", "Wikipedia"]]},
]
ITEMS = """
# Wuxia
A7-12 | New-School Wuxia (1966–1984: King Hu, Chang Cheh, Chu Yuan) | Golden Swallow | 1968 | Chang Cheh | tt0063105
A7-12 | New-School Wuxia (1966–1984: King Hu, Chang Cheh, Chu Yuan) | Intimate Confessions of a Chinese Courtesan | 1972 | Chu Yuan | tt0068744
A7-12 | New-School Wuxia (1966–1984: King Hu, Chang Cheh, Chu Yuan) | Killer Clans | 1976 | Chu Yuan | tt0074745
A7-12 | New-School Wuxia (1966–1984: King Hu, Chang Cheh, Chu Yuan) | The Magic Blade | 1976 | Chu Yuan | tt0075329
A7-12 | New-School Wuxia (1966–1984: King Hu, Chang Cheh, Chu Yuan) | Clans of Intrigue | 1977 | Chu Yuan | tt0075833
A7-12 | New-School Wuxia (1966–1984: King Hu, Chang Cheh, Chu Yuan) | Duel to the Death | 1983 | Ching Siu-tung | tt0084924
A7-12 | New-School Wuxia (1966–1984: King Hu, Chang Cheh, Chu Yuan) | Zu: Warriors from the Magic Mountain | 1983 | Tsui Hark | tt0086308
A7-12 | Hong Kong New Wave Wuxia (1985–1999) | Swordsman | 1990 | King Hu; Tsui Hark | tt0100973
A7-12 | Hong Kong New Wave Wuxia (1985–1999) | Swordsman II | 1992 | Ching Siu-tung | tt0103295
A7-12 | Hong Kong New Wave Wuxia (1985–1999) | New Dragon Gate Inn | 1992 | Raymond Lee | tt0105859
A7-12 | Hong Kong New Wave Wuxia (1985–1999) | Swordsman III: The East Is Red | 1993 | Ching Siu-tung | tt0105655
A7-12 | Hong Kong New Wave Wuxia (1985–1999) | The Bride with White Hair | 1993 | Ronny Yu | tt0106342
A7-12 | Hong Kong New Wave Wuxia (1985–1999) | Butterfly and Sword | 1993 | Michael Mak | tt0108614
A7-12 | Wuxia Blockbusters (2000–) | Reign of Assassins | 2010 | Su Chao-pin; John Woo | tt1460743
# Ninja
A7-14 | Japanese Ninja Films | Ninja, a Band of Assassins | 1962 | Satsuo Yamamoto | tt0164882
A7-14 | Japanese Ninja Films | Shinobi No Mono 2: Vengeance | 1963 | Satsuo Yamamoto | tt0200310
A7-14 | Japanese Ninja Films | Shogun's Ninja | 1980 | Norifumi Suzuki | tt0084674
A7-14 | Japanese Ninja Films | Owls' Castle | 1999 | Masahiro Shinoda | tt0275362
A7-14 | Japanese Ninja Films | Shinobi: Heart Under Blade | 2005 | Ten Shimoyama | tt0475723
A7-14 | Japanese Ninja Films | Kamui Gaiden | 2009 | Yōichi Sai | tt1156479
A7-14 | Hong Kong Ninja Films | Five Elements Ninjas | 1982 | Chang Cheh | tt0084921
A7-14 | Cannon & Western Ninja Boom (1981–) | Enter the Ninja | 1981 | Menahem Golan | tt0082332
A7-14 | Cannon & Western Ninja Boom (1981–) | Revenge of the Ninja | 1983 | Sam Firstenberg | tt0086192
A7-14 | Cannon & Western Ninja Boom (1981–) | Ninja | 2009 | Isaac Florentine | tt1182921
# Bruceploitation
A7-11 | Bruceploitation | Bruce Lee: The Man, the Myth | 1976 | Ng See-yuen | tt0077850
A7-11 | Bruceploitation | Exit the Dragon, Enter the Tiger | 1976 | Lee Tso-nam | tt0074506
A7-11 | Bruceploitation | Enter the Game of Death | 1978 | Joseph Velasco | tt0062936
A7-11 | Bruceploitation | The Clones of Bruce Lee | 1980 | Joseph Kong | tt0075859
A7-11 | Bruceploitation | Game of Death II | 1981 | Ng See-yuen | tt0076709
# Lucha film
NEW_A7_LUCHA | | Santo vs. Evil Brain | 1961 | Joselito Rodríguez | tt0052159
NEW_A7_LUCHA | | Santo vs. the Vampire Women | 1962 | Alfonso Corona Blake | tt0055408
NEW_A7_LUCHA | | Santo in the Wax Museum | 1963 | Alfonso Corona Blake | -
NEW_A7_LUCHA | | The Wrestling Women vs. the Aztec Mummy | 1964 | René Cardona | -
NEW_A7_LUCHA | | The Bat Woman | 1968 | René Cardona | tt0235608
NEW_A7_LUCHA | | Night of the Bloody Apes | 1969 | René Cardona | tt0063090
NEW_A7_LUCHA | | Santo in the Treasure of Dracula | 1969 | René Cardona | tt0208504
NEW_A7_LUCHA | | Santo and Blue Demon vs. the Monsters | 1970 | Gilberto Martínez Solares | tt0064932
NEW_A7_LUCHA | | Santo and Blue Demon vs. Dracula and the Wolf Man | 1973 | Miguel M. Delgado | tt0067708
"""
