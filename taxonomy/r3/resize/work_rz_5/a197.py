from common import *
L = INP["A19-7"]; o = load(); A = {}
ids = lambda s: set(s.split())
ethno = ids("""tspdt:el-ultimo-malon-1917 tt0017743 tspdt:the-silent-enemy-1930 tt0021881 tspdt:que-viva-mexico-1932 tspdt:farrebique-1946 tt0040550 tt0052923
tspdt:la-pyramide-humaine-1961 tspdt:the-punishment-1962 tspdt:jaguar-1967 tspdt:the-mongols-1973 tspdt:fad-jal-1979 tspdt:la-nouba-des-femmes-du-mont-chenoua-1979
tspdt:turumba-1981 tspdt:two-laws-1981 tspdt:mi-tia-nora-1983 tspdt:magino-village-a-tale-1987 tspdt:liberte-egalite-fraternite-et-puis-apres-1990 tt0107376
tspdt:bontoc-eulogy-1995 tspdt:untouched-by-the-west-2002 tt0922605 tspdt:manoro-2006 tt1092031 tt1502396 tspdt:arraianos-2012 tspdt:to-the-wolf-2013
tspdt:episode-of-the-sea-2014 tspdt:la-mort-du-dieu-serpent-2014 tspdt:rio-corgo-2015 tt5072370 tt2338774 tt6977442 tt8423962 tt6157294 tt10265444
tt7601098 tt27502245 tspdt:canuto-s-transformation-2023 tt37660542 tt30768181 tt37538646 tspdt:monikondee-2025 tt31433781 tspdt:balikbayan-1-memories-of-overdevelopment-2015
tt8106566 tspdt:you-are-all-captains-2010 tt2855026 tspdt:rite-of-spring-1963 tspdt:the-moulin-2015 tspdt:silence-2012""")
reenact = ids("""tspdt:the-eternal-frame-1975 tspdt:the-battle-of-orgreave-2001 tt1623008 tt5278592 tt7520286 tt14300912 tt27502426 tt2177511 tspdt:theatre-of-war-2018
tt29102354 tspdt:charlie-victor-romeo-2013 tt5117222 tspdt:elgar-tv-1962 tspdt:isadora-duncan-the-biggest-dancer-in-the-1966 tspdt:song-of-summer-tv-1968
tspdt:dance-of-the-seven-veils-tv-1970 tspdt:far-from-poland-1984 tt3317522 tt34383611 tspdt:nos-defaites-2019 tt0210389 tspdt:actress-2014 tspdt:self-made-2010
tspdt:stephen-2023 tt14035242 tspdt:giron-1972 tspdt:mutzenbacher-2022 tspdt:blue-island-2022 tspdt:second-time-around-2018 tspdt:de-facto-2023 tspdt:here-for-life-2019
tt1646963 tspdt:the-tuba-thieves-2023 tspdt:people-power-bombshell-the-diary-of-viet-2016 tt7636966 tspdt:the-annotated-field-guide-of-ulysses-s-g-2020 tt2113090""")
mock = ids("""tt0080813 tspdt:dadetown-1996 tspdt:dark-side-of-the-moon-tv-2002 tspdt:un-tigre-de-papel-2008 tspdt:le-challat-de-tunis-2013 tt5518022
tspdt:nathan-for-you-finding-frances-tv-2017 tt0256639 tt1546653 tspdt:georg-1964 tspdt:brandy-in-the-wilderness-1971 tspdt:what-the-bleep-do-we-know-2004
tspdt:naked-as-nature-intended-1961 tspdt:the-naked-bunyip-1970 tspdt:language-of-love-1969 tspdt:la-mafia-non-e-piu-quella-di-una-volta-2019 tspdt:about-a-hero-2024
tspdt:welcome-interplanetary-and-sidereal-spac-2024 tspdt:dva-kapitana-ii-1993 tspdt:tito-po-drugi-put-medju-srbima-1993""")
meta = ids("""tt0354575 tspdt:salam-cinema-1995 tt0073471 tt0079204 tt0436811 tt0066922 tt0062043 tspdt:the-filmmaker-s-house-2020 tspdt:la-ultima-pelicula-2013 tt2352488
tt1165293 tspdt:homem-comum-2015 tspdt:a-dramatic-film-2019 tspdt:notas-para-una-pelicula-2022 tspdt:filmstunde-23-2024 tspdt:still-film-2023 tspdt:common-carrier-2017
tspdt:ulysses-2024 tspdt:nikita-lavretski-2019 tspdt:a-man-and-a-camera-2021 tt4160256 tt4944506 tt4692242 tspdt:bye-bye-africa-1999 tt0209950 tspdt:life-in-denmark-1972
tspdt:stagefright-1981 tt0104953 tspdt:unmade-beds-1997 tspdt:anna-1975 tt0076857 tspdt:mr-zhang-believes-2015 tspdt:kamikaze-hearts-1986 tspdt:description-of-an-island-1979
tspdt:me-and-my-brother-1969 tt0071219 tspdt:the-beloved-2007 tspdt:i-had-nowhere-to-go-2016 tt2389092 tspdt:never-eat-alone-2016 tspdt:the-dreamed-ones-2016
tspdt:popular-tradicion-de-esta-tierra-2024 tspdt:krabi-2562-2019 tspdt:it-s-all-true-unfinished-film-1943 tt9675320 tspdt:the-good-woman-of-bangkok-1991
tspdt:salam-cinema-1995 tt1439573 tspdt:king-murray-1969 tspdt:o-megalos-erotikos-1973""")
for t in L["titles"]:
    i = t["id"]; y = yr(t)
    if i in ethno: A[i] = ["NEW1", 1 if y < 1960 else (2 if y < 2000 else 3)]
    elif i in reenact: A[i] = ["self", 2]
    elif i in mock: A[i] = ["self", 3]
    elif i in meta: A[i] = ["self", 5]
    elif y < 1980: A[i] = ["self", 1]
    else: A[i] = ["self", 4]
o["A19-7"] = {
 "defn": "A film that blends documentary and fiction: staged or re-enacted scenes with real people, real people performing scripted or semi-scripted fictions, or fiction shot as documentary (Fires Were Started, Caesar Must Die, Four Daughters, The Arbor). Includes mockumentary features. Docufictions in which a community enacts its own culture go to Ethnofiction.",
 "axis": "by how fact and fiction are joined: the staged story documentary, re-enactment, the fake documentary, hybrid fiction with non-actors, then the self-reflexive docufiction",
 "secs": ["Story Documentary & Staged Actuality", "Re-enactment & Restaging", "Mockumentary & Fake Documentary", "Hybrid Fiction with Non-Actors", "Self-Reflexive & Essayistic Docufiction"],
 "new_leaves": [{"key": "NEW1", "label": "Ethnofiction", "breadth": "Docufiction in which a community plays itself within its own culture",
   "defn": "A docufiction in which members of a people or community — often indigenous, rural, nomadic or colonised — act out stories in their own setting, language and customs, so that the fiction serves as ethnography (Chang, Louisiana Story, Jaguar, Farrebique, Alamar, The Dead and the Others). Staged films about urban or institutional subjects stay in Docufiction; non-staged fieldwork goes to Ethnographic Film.",
   "aliases": "ethnographic fiction; ethno-fiction", "src": WP("Ethnofiction"),
   "axis": "by era: the silent and classical staged-ethnography film, Rouch and the ethnofiction of 1960–1999, then contemporary ethnofiction",
   "secs": ["Silent & Classical Staged Ethnography (to 1959)", "Rouch & After (1960–1999)", "Contemporary Ethnofiction (2000–)"]}],
 "assign": A, "moves": []}
save(o)
import collections; print(collections.Counter(tuple(v) for v in A.values()), len(A), len(L["titles"]))
