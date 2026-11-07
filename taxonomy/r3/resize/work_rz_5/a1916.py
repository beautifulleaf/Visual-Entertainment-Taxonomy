from common import *
L = INP["A19-16"]; o = load(); A = {}
ids = lambda s: set(s.split())
troubled = ids("""tt0083702 tt0102015 tt0107233 tt0308514 tt0332422 tt0424089 tt1433528 tt1935156 tt3966544 tt6893836 tt4857058 tt9357838
tspdt:i-am-cuba-the-siberian-mammoth-2005 tspdt:operation-filmmaker-2007 tspdt:waiting-for-fidel-1974 tt0390336 tspdt:demon-lover-diary-1980""")
retro = ids("""tt0385073 tt0251821 tt0416716 tt1080585 tt1510985 tt3088036 tt3551954 tspdt:notfilm-2015 tt5725908 tt10090796 tt5123896 tt12004838 tt12078990
tt16116174 tt10825052 tt30852316 tt31402962 tt32743685 tt34621966 tt39307872 tspdt:le-cinquieme-plan-de-la-jetee-2024 tspdt:following-nazarin-2015 tt0106696
tspdt:calamity-jane-delphine-seyrig-a-story-2020 tspdt:where-is-this-street-or-with-no-before-o-2022 tt32408421""")
rehearse = ids("""tt0116913 tt0977648 tspdt:chekhov-for-children-2010 tspdt:theater-of-war-2008 tt0795459 tt3282712 tspdt:dress-rehearsal-for-utopia-2012
tspdt:die-generalprobe-1980 tspdt:moscou-2009""")
actors = ids("""tt0059000 tspdt:la-solitude-du-chanteur-de-fond-1974 tspdt:gedachtnis-ein-film-fur-curt-bois-und-be-1982 tt0085905 tt0113159 tspdt:excavating-taylor-mead-2005
tt2372776 tspdt:andre-gregory-before-and-after-dinner-2013 tt4621016 tt4145178 tspdt:helmut-berger-actor-2015 tt4572820 tt9351746 tspdt:conrad-veidt-my-life-2019
tspdt:no-ordinary-man-2020 tt8801666 tspdt:boulevard-a-hollywood-story-2021 tt28254460 tt20274588 tt15823728 tspdt:bulle-ogier-portrait-dune-etoile-cachee--2024
tspdt:kim-novak-s-vertigo-2025 tspdt:disappearance-of-miss-scott-the-tv-2025 tt2645000 tspdt:io-sono-valentina-nappi-2018 tspdt:exhibition-1975 tt2327430 tt0200849
tspdt:the-american-dreamer-1971 tspdt:muppet-guys-talking-2017 tspdt:othelo-o-grande-2023 tspdt:pharos-of-chaos-1983 tspdt:prisoner-of-paradise-2002""")
crew = ids("""tspdt:citizen-langlois-1994 tt0420952 tt1151833 tspdt:celluloid-man-2012 tt2382298 tt6851066 tt4154086 tt29491918 tspdt:erase-and-forget-2017""")
genre = ids("""tt0072272 tt0111408 tt0996966 tt1479963 tt1144539 tt2395970 tt2125501 tt9442842 tt13938338 tt9567548 tspdt:east-side-story-1997 tspdt:the-taking-2021
tspdt:videoheaven-2025 tt0321353""")
rep = ids("""tt0112651 tspdt:a-bit-of-scarlet-1996 tspdt:women-under-the-influence-tv-1986 tspdt:sisters-in-cinema-2003 tt8637504 tt10410506 tt21438352
tspdt:midnight-ramble-tv-1994 tspdt:red-hollywood-1996""")
craft = ids("""tt5652594 tspdt:personal-journey-with-martin-scorsese-th-1995 tt0173772 tt3748512 tt0105764 tt0428441 tt2014338 tt4207112 tt1045642 tt2085910
tspdt:the-first-movie-2009 tt2917506 tspdt:a-sudden-glimpse-to-deeper-things-2024 tspdt:film-and-reality-1942 tspdt:homem-e-o-cinema-um-1977
tspdt:cinema-documentaire-fragments-d-une-hist-2014 tspdt:pelicula-de-gente-que-mira-peliculas-una-2012 tspdt:herbaria-2022 tspdt:the-last-days-of-humanity-2022
tspdt:66-kinos-2016 tspdt:a-filmless-festival-2015 tt0405496 tspdt:scala-2023 tspdt:the-neon-people-2025""")
for t in L["titles"]:
    i = t["id"]; s = sec(t)
    if i in actors: A[i] = ["NEW1", 2]
    elif s == 1:
        A[i] = ["self", 2 if i in troubled else 3 if i in retro else 4 if i in rehearse else 1]
    elif s == 2: A[i] = ["NEW1", 3 if i in crew else 1]
    else: A[i] = ["NEW2", 2 if i in genre else 3 if i in rep else 4 if i in craft else 1]
o["A19-16"] = {
 "label": "Making-of Documentary",
 "defn": "A documentary about the making of a particular film, series or stage production: the shoot, the rehearsal, the troubled or abandoned project, or the production looked back on (Hearts of Darkness, Burden of Dreams, Lost in La Mancha, Jodorowsky's Dune). Portraits of filmmakers and actors go to Filmmaker Portrait Documentary; histories of cinema to Film History Documentary.",
 "axis": "by the production's fate and the film's stance: the on-set record, the troubled or unmade production, the retrospective making-of, then the rehearsal film",
 "secs": ["On-Set Records & Shoot Diaries", "Troubled, Abandoned & Unmade Productions", "Retrospective Making-of & Production Histories", "Rehearsal & Stage-Production Films"],
 "new_leaves": [
  {"key": "NEW1", "label": "Filmmaker Portrait Documentary", "breadth": "Documentary portraits of directors, actors and other film people",
   "defn": "A documentary portrait of a person of the cinema — a director, actor, star or craftsperson — built on interviews, archive and the subject's films (Directed by John Ford, Cinéastes de notre temps, Marlene, My Best Fiend, Life Itself, De Palma). The making of one production goes to Making-of Documentary.",
   "aliases": "film-director portrait; actor documentary; Cinéastes de notre temps", "src": WP("Cin%C3%A9astes_de_notre_temps"),
   "axis": "by the sitter: directors first, then actors and stars, then crew, critics, programmers and archivists",
   "secs": ["Director Portraits", "Actor & Star Portraits", "Crew, Critics & Archivists"]},
  {"key": "NEW2", "label": "Film History Documentary", "breadth": "Documentaries on the history, genres, crafts and criticism of cinema",
   "defn": "A documentary that tells the history of cinema or a part of it — a national cinema, studio or era, a genre or cult, the screen image of a group, or a craft or way of watching (The Celluloid Closet, Visions of Light, A Personal Journey with Martin Scorsese Through American Movies, Not Quite Hollywood).",
   "aliases": "documentary on film history; cinema history documentary", "src": WP("Film_history"),
   "axis": "by the history told: national, studio and industry histories, genre and cult histories, representation on screen, then craft, criticism and cinephilia",
   "secs": ["National, Studio & Industry Histories", "Genre, Cult & Exploitation Histories", "Representation & Identity on Screen", "Craft, Criticism & Cinephilia"]}],
 "assign": A, "moves": []}
save(o)
import collections, re
print(sorted(collections.Counter(tuple(v) for v in A.values()).items()))
allids = set(t["id"] for t in L["titles"])
for tok in re.findall(r"(?:tt\d+|tspdt:[\w\-]+)", open(__file__).read()):
    if tok not in allids: print("BAD", tok)
