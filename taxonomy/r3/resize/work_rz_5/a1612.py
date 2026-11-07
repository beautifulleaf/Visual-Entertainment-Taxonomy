from common import *
L = INP["A16-12"]; o = load()
stage = set("""tspdt:this-ancient-law-1923 tspdt:kean-1924 tt0024353 tspdt:zaza-1938 tspdt:felice-nanteuil-1945 tt0042192 tt0044837 tspdt:comicos-1954 tt0046874
tspdt:two-stage-sisters-1964 tt0064897 tt0079672 tspdt:le-theatre-des-matieres-1977 tt0085461 tt0087193 tt0086889 tt0089902 tspdt:o-bobo-1987 tspdt:woman-demon-human-1987
tt0097635 tt0133343 tt0111590 tt0112427 tt0150216 tt0283422 tspdt:playing-in-the-company-of-men-2003 tt0368658 tt0383028 tt1314269 tt1175506 tt1690389 tt2379418
tt2406252 tt2276069 tt2452254 tt5820812 tt6101602 tspdt:first-night-nerves-2018 tspdt:un-soupcon-d-amour-2020 tspdt:isabella-2020 tt21342370 tt26671415
tt29578220 tt35231039 tspdt:pin-de-fartie-2025 tt0202055 tspdt:w-s-tragedy-1984 tspdt:ranganayaki-1981 tspdt:fauna-2020 tspdt:in-camera-2023 tt0116845
tspdt:the-firebird-1952 tt0045471""".split())
painters = set("""tspdt:la-femme-nue-1926 tt0035078 tspdt:donne-mois-tes-yeux-1943 tt0041386 tspdt:raft-of-the-medusa-th-1980 tspdt:every-picture-tells-a-story-1984
tspdt:life-classes-1987 tt0092637 tt0095649 tspdt:zena-s-krajolikom-1989 tt0101428 tspdt:frozen-1996 tt0290210 tt0422295 tspdt:crime-delicado-2005""".split())
A = {}
for t in L["titles"]:
    s = sec(t); i = t["id"]
    if s == 1:
        y = yr(t); A[i] = ["NEW1", 1 if y < 1980 else (2 if y < 2010 else 3)]
    elif s == 2: A[i] = ["self", 1 if i in stage else 2]
    elif s == 3: A[i] = ["self", 3]
    else: A[i] = ["self", 5 if i in painters else 4]
o["A16-12"] = {
 "label": "Artist Film (Künstlerroman)",
 "defn": "A drama of a fictional performer, musician, writer or painter whose art or career is the engine — the artist at work and in crisis (All About Eve, Opening Night, Tár, La belle noiseuse). Films about making films go to Film about Filmmaking; real artists' lives to A11; musicals to A14.",
 "axis": "by the art: stage, then screen and show-business performers, musicians, writers, and painters and visual artists last",
 "secs": ["Stage & Theatre", "Screen Stars, Dancers & Show Business", "Musicians", "Writers & Poets", "Painters, Sculptors & Visual Artists"],
 "new_leaves": [{"key": "NEW1", "label": "Film about Filmmaking", "breadth": "Fiction films set in the film world: a director, crew or production in crisis",
   "defn": "A fiction film whose subject is the making of films — a director's creative crisis, a troubled shoot, the studio or the film world, often self-reflexive (8½, The Bad and the Beautiful, Passion, The State of Things, Day for Night, Pain and Glory, The Fabelmans). Stage and screen performers' careers stay in Artist Film; documentaries on film production go to Making-of Documentary.",
   "aliases": "film within a film; metafilm; films about filmmaking; Hollywood-on-Hollywood film", "src": WP("Film_within_a_film"),
   "axis": "by era: classical and modernist films about filmmaking, the late-modern and festival-auteur decades, then the 2010s onward",
   "secs": ["Classical & Modernist Films about Filmmaking (to 1979)", "Late-Modern & Auteur Self-Portraits (1980–2009)", "Contemporary Films about Filmmaking (2010–)"]}],
 "assign": A, "moves": []}
save(o)
import collections; print(collections.Counter(tuple(v) for v in A.values()))
