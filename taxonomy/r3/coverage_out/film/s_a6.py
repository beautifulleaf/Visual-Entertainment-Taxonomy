SS = ["1980s Sword-and-Sorcery Boom (incl. Italian barbarian films)", "Later Sword and Sorcery (1990s–)"]
RESEC = {"A6-2": {"axis": "era (the field dates the screen genre from the 1982 Conan boom)", "secs": SS,
                  "fn": lambda tc, r, i: SS[0] if int(r["year"]) < 1990 else SS[1]}}
SECS = [("A6-12", "Soviet Skazka Films (Ptushko & Rou)")]
ITEMS = """
A6-2 | 1980s Sword-and-Sorcery Boom (incl. Italian barbarian films) | Ator: The Fighting Eagle | 1982 | Joe D'Amato | tt0085183
A6-2 | 1980s Sword-and-Sorcery Boom (incl. Italian barbarian films) | Gunan, King of the Barbarians | 1982 | Franco Prosperi | -
A6-2 | 1980s Sword-and-Sorcery Boom (incl. Italian barbarian films) | Yor: The Hunter from the Future | 1983 | Antonio Margheriti | tt0084935
A6-2 | 1980s Sword-and-Sorcery Boom (incl. Italian barbarian films) | Hundra | 1983 | Matt Cimber | tt0087436
A6-2 | 1980s Sword-and-Sorcery Boom (incl. Italian barbarian films) | The Barbarians | 1987 | Ruggero Deodato | tt0092615
A6-2 | Later Sword and Sorcery (1990s–) | Kull the Conqueror | 1997 | John Nicolella | tt0119484
# Soviet skazka
A6-12 | Soviet Skazka Films (Ptushko & Rou) | Vasilisa the Beautiful | 1939 | Aleksandr Rou | tt0167474
A6-12 | Soviet Skazka Films (Ptushko & Rou) | Kashchey the Deathless | 1944 | Aleksandr Rou | -
A6-12 | Soviet Skazka Films (Ptushko & Rou) | The Stone Flower | 1946 | Aleksandr Ptushko | tt0038666
A6-12 | Soviet Skazka Films (Ptushko & Rou) | Cinderella | 1947 | Nadezhda Kosheverova; Mikhail Shapiro | tt0168269
A6-12 | Soviet Skazka Films (Ptushko & Rou) | Sadko | 1953 | Aleksandr Ptushko | tt0046264
A6-12 | Soviet Skazka Films (Ptushko & Rou) | Ilya Muromets | 1956 | Aleksandr Ptushko | tt0049358
A6-12 | Soviet Skazka Films (Ptushko & Rou) | Sampo | 1959 | Aleksandr Ptushko | tt0053240
A6-12 | Soviet Skazka Films (Ptushko & Rou) | The Magic Weaver | 1960 | Aleksandr Rou | tt0054065
A6-12 | Soviet Skazka Films (Ptushko & Rou) | Kingdom of Crooked Mirrors | 1963 | Aleksandr Rou | tt0145033
A6-12 | Soviet Skazka Films (Ptushko & Rou) | Jack Frost (Morozko) | 1964 | Aleksandr Rou | tt0058374
A6-12 | Soviet Skazka Films (Ptushko & Rou) | The Tale of Tsar Saltan | 1966 | Aleksandr Ptushko | tt0174207
A6-12 | Soviet Skazka Films (Ptushko & Rou) | Fire, Water and Brass Pipes | 1968 | Aleksandr Rou | -
A6-12 | Soviet Skazka Films (Ptushko & Rou) | Barbara the Fair with the Silken Hair | 1969 | Aleksandr Rou | tt0191625
A6-12 | Soviet Skazka Films (Ptushko & Rou) | Ruslan and Ludmila | 1972 | Aleksandr Ptushko | tt0174174
A6-12 | Soviet Skazka Films (Ptushko & Rou) | The Golden Horns | 1972 | Aleksandr Rou | tt0069544
# Prehistoric
A6-24 | | One Million Years B.C. | 1966 | Don Chaffey | tt0060782
A6-24 | | When Dinosaurs Ruled the Earth | 1970 | Val Guest | tt0066561
A6-24 | | Creatures the World Forgot | 1971 | Don Chaffey | tt0066955
A6-24 | | Caveman | 1981 | Carl Gottlieb | tt0082146
A6-24 | | The Clan of the Cave Bear | 1986 | Michael Chapman | tt0090848
A6-24 | | Ao: The Last Hunter | 2010 | Jacques Malaterre | tt1526578
A6-24 | | Iceman | 2017 | Felix Randau | tt5907748
"""
NEW = [
 {"key": "NEW_A6_BERG", "sub": "A6", "label": "Bergfilm (Mountain Film)", "breadth": "national genre",
  "defn": "The German mountain film of the 1920s–30s (Arnold Fanck, Leni Riefenstahl, Luis Trenker): real Alpine climbing and skiing photographed on location, elemental storms and avalanches, romantic rivalry and heroic summits (<i>The Holy Mountain</i>, <i>The White Hell of Pitz Palu</i>, <i>The Blue Light</i>).",
  "aliases": "mountain film", "see": "A19-22 Mountaineering & Expedition Film", "src": [["https://en.wikipedia.org/wiki/Mountain_film", "Wikipedia"]]},
]
ITEMS += """
NEW_A6_BERG | | The Holy Mountain | 1926 | Arnold Fanck | tt0016953
NEW_A6_BERG | | The Great Leap | 1927 | Arnold Fanck | -
NEW_A6_BERG | | The White Hell of Pitz Palu | 1929 | Arnold Fanck; G. W. Pabst | tt0020570
NEW_A6_BERG | | Storm over Mont Blanc | 1930 | Arnold Fanck | -
NEW_A6_BERG | | The White Ecstasy | 1931 | Arnold Fanck | -
NEW_A6_BERG | | The Blue Light | 1932 | Leni Riefenstahl; Béla Balázs | tt0022694
NEW_A6_BERG | | The Rebel | 1932 | Luis Trenker; Curtis Bernhardt | -
NEW_A6_BERG | | S.O.S. Eisberg | 1933 | Arnold Fanck | -
"""
