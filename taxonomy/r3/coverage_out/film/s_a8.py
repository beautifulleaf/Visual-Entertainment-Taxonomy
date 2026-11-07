W = "https://en.wikipedia.org/wiki/"
SS = ["Silent Epics (1913–1927)", "Hollywood & British Epics of the Studio and Widescreen Era (1932–1966)", "Italian Peplum (1954–1965)",
      "Art-House & Erotic Antiquity", "Revival Epics (2000–)"]
SSMAP = {"tt0161953": SS[0], "tt0003740": SS[0], "tt0016641": SS[0], "tt0038390": SS[1], "tt0049833": SS[1], "tt0043949": SS[1],
         "tt0044355": SS[1], "tt0052618": SS[1], "tt0054331": SS[1], "tt0056937": SS[1], "tt0047630": SS[2], "tt0055950": SS[3],
         "tt0076208": SS[3], "tt0075177": SS[3], "tt0080491": SS[3], "tt29703523": SS[3], "tt19861162": SS[3]}
JD = ["Prewar Jidaigeki (1925–1945)", "Postwar Golden Age (1950–1959)", "1960s Jidaigeki", "Late & Contemporary Jidaigeki (1970–)"]
RESEC = {
 "A8-2": {"axis": "era / national production tradition", "secs": SS,
          "fn": lambda tc, r, i: SSMAP.get(tc) or (SS[4] if int(r["year"]) >= 2000 else None)},
 "A8-5": {"axis": "era", "secs": JD,
          "fn": lambda tc, r, i: JD[0] if int(r["year"]) < 1946 else JD[1] if int(r["year"]) < 1960 else JD[2] if int(r["year"]) < 1970 else JD[3]},
}
NEW = [
 {"key": "NEW_A8_SAGEUK", "sub": "A8", "label": "Sageuk Film", "breadth": "national genre",
  "defn": "The Korean historical film (sageuk), set chiefly in the Goryeo and Joseon courts and countryside: palace intrigue, royal doubles, scholars, painters and kisaeng (<i>The King and the Clown</i>, <i>Masquerade</i>, <i>Untold Scandal</i>).",
  "aliases": "sageuk", "see": "A8-4 Royal Court Drama", "src": [[W + "Sageuk", "Wikipedia"]]},
]
ITEMS = """
# Sword and sandal
A8-2 | Silent Epics (1913–1927) | Quo Vadis? | 1913 | Enrico Guazzoni | tt0002445
A8-2 | Hollywood & British Epics of the Studio and Widescreen Era (1932–1966) | The Sign of the Cross | 1932 | Cecil B. DeMille | tt0023470
A8-2 | Hollywood & British Epics of the Studio and Widescreen Era (1932–1966) | Samson and Delilah | 1949 | Cecil B. DeMille | tt0041838
A8-2 | Hollywood & British Epics of the Studio and Widescreen Era (1932–1966) | David and Bathsheba | 1951 | Henry King | tt0043455
A8-2 | Hollywood & British Epics of the Studio and Widescreen Era (1932–1966) | The Robe | 1953 | Henry Koster | tt0046247
A8-2 | Hollywood & British Epics of the Studio and Widescreen Era (1932–1966) | Demetrius and the Gladiators | 1954 | Delmer Daves | tt0046899
A8-2 | Hollywood & British Epics of the Studio and Widescreen Era (1932–1966) | The Egyptian | 1954 | Michael Curtiz | tt0046949
A8-2 | Hollywood & British Epics of the Studio and Widescreen Era (1932–1966) | Land of the Pharaohs | 1955 | Howard Hawks | tt0048283
A8-2 | Hollywood & British Epics of the Studio and Widescreen Era (1932–1966) | Helen of Troy | 1956 | Robert Wise | tt0049301
A8-2 | Hollywood & British Epics of the Studio and Widescreen Era (1932–1966) | Solomon and Sheba | 1959 | King Vidor | tt0053290
A8-2 | Hollywood & British Epics of the Studio and Widescreen Era (1932–1966) | Esther and the King | 1960 | Raoul Walsh | tt0053800
A8-2 | Hollywood & British Epics of the Studio and Widescreen Era (1932–1966) | King of Kings | 1961 | Nicholas Ray | tt0055047
A8-2 | Hollywood & British Epics of the Studio and Widescreen Era (1932–1966) | Barabbas | 1961 | Richard Fleischer | tt0055774
A8-2 | Hollywood & British Epics of the Studio and Widescreen Era (1932–1966) | The 300 Spartans | 1962 | Rudolph Maté | tt0055719
A8-2 | Hollywood & British Epics of the Studio and Widescreen Era (1932–1966) | Sodom and Gomorrah | 1962 | Robert Aldrich | tt0056504
A8-2 | Hollywood & British Epics of the Studio and Widescreen Era (1932–1966) | The Fall of the Roman Empire | 1964 | Anthony Mann | tt0058085
A8-2 | Italian Peplum (1954–1965) | Hercules | 1958 | Pietro Francisci | tt0050381
A8-2 | Italian Peplum (1954–1965) | Hercules Unchained | 1959 | Pietro Francisci | tt0052782
A8-2 | Italian Peplum (1954–1965) | The Giant of Marathon | 1959 | Jacques Tourneur; Mario Bava | tt0052604
A8-2 | Italian Peplum (1954–1965) | The Last Days of Pompeii | 1959 | Mario Bonnard; Sergio Leone | tt0054422
A8-2 | Italian Peplum (1954–1965) | Hercules in the Haunted World | 1961 | Mario Bava | tt0054850
A8-2 | Italian Peplum (1954–1965) | The Colossus of Rhodes | 1961 | Sergio Leone | tt0054756
A8-2 | Italian Peplum (1954–1965) | Hercules and the Captive Women | 1961 | Vittorio Cottafavi | tt0054851
A8-2 | Italian Peplum (1954–1965) | Duel of the Titans | 1961 | Sergio Corbucci | tt0057460
A8-2 | Italian Peplum (1954–1965) | The Trojan Horse | 1961 | Giorgio Ferroni | tt0056042
A8-2 | Italian Peplum (1954–1965) | Hercules Against the Moon Men | 1964 | Giacomo Gentilomo | tt0058311
# Jidaigeki
A8-5 | Prewar Jidaigeki (1925–1945) | Orochi | 1925 | Buntarō Futagawa | tt0016185
A8-5 | Prewar Jidaigeki (1925–1945) | Sazen Tange and the Pot Worth a Million Ryo | 1935 | Sadao Yamanaka | tt0027076
A8-5 | Prewar Jidaigeki (1925–1945) | Humanity and Paper Balloons | 1937 | Sadao Yamanaka | tt0029314
A8-5 | Prewar Jidaigeki (1925–1945) | The 47 Ronin | 1941 | Kenji Mizoguchi | tt0033654
A8-5 | Postwar Golden Age (1950–1959) | Samurai Saga | 1959 | Hiroshi Inagaki | tt0052579
A8-5 | 1960s Jidaigeki | Shinsengumi: Assassins of Honor | 1969 | Tadashi Sawashima | tt0066372
A8-6 | Classic Ronin & Samurai Swordplay | Goyokin | 1969 | Hideo Gosha | tt0064387
# Sageuk
NEW_A8_SAGEUK | | Painted Fire | 2002 | Im Kwon-taek | tt0317234
NEW_A8_SAGEUK | | Untold Scandal | 2003 | E J-yong | tt0380689
NEW_A8_SAGEUK | | The King and the Clown | 2005 | Lee Joon-ik | tt0492835
NEW_A8_SAGEUK | | Hwang Jin Yi | 2007 | Chang Yoon-hyun | tt1059200
NEW_A8_SAGEUK | | War of the Arrows | 2011 | Kim Han-min | tt2025526
NEW_A8_SAGEUK | | Masquerade | 2012 | Choo Chang-min | tt2290840
NEW_A8_SAGEUK | | The Face Reader | 2013 | Han Jae-rim | tt3008014
NEW_A8_SAGEUK | | The Fatal Encounter | 2014 | Lee Jae-kyoo | tt3479208
NEW_A8_SAGEUK | | The Throne | 2015 | Lee Joon-ik | tt4010918
NEW_A8_SAGEUK | | The Fortress | 2017 | Hwang Dong-hyuk | tt7160176
NEW_A8_SAGEUK | | The King's Letters | 2019 | Cho Chul-hyun | tt10438454
NEW_A8_SAGEUK | | Forbidden Dream | 2019 | Hur Jin-ho | tt11498038
NEW_A8_SAGEUK | | The Book of Fish | 2021 | Lee Joon-ik | tt14371900
NEW_A8_SAGEUK | | The Night Owl | 2022 | An Tae-jin | tt23871504
A9-1 | Early Modern, Napoleonic & Colonial Wars | Hansan: Rising Dragon | 2022 | Kim Han-min | tt21109538
A9-1 | Early Modern, Napoleonic & Colonial Wars | Noryang: Deadly Sea | 2023 | Kim Han-min | tt22813112
"""
