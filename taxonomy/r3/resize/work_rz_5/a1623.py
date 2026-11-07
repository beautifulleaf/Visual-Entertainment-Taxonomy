from common import *
L = INP["A16-23"]; o = load(); A = {}
extra = {"tt0046002": ["self", 1], "tspdt:the-mistress-1962": ["self", 2], "tt0061055": ["self", 2], "tspdt:rags-tatters-2013": ["NEW1", 3]}
for t in L["titles"]:
    s = sec(t); i = t["id"]; y = yr(t)
    if i in extra: A[i] = extra[i]
    elif s == 1: A[i] = ["self", 1]
    elif s == 2: A[i] = ["NEW1", 1 if y < 1967 else (2 if y < 1980 else 3)]
    elif s == 3: A[i] = ["self", 2]
    else: A[i] = ["self", 3]
o["A16-23"] = {
 "defn": "A drama whose engine is political power — winning and abusing office, or living under it, or communities torn by political conflict (Mr. Smith Goes to Washington, The Candidate, Yol, Leviathan). Films of militant struggle and revolution go to Revolutionary Film; political thrillers to A3; war to A9.",
 "axis": "by the relation to power: holding and seeking office, life under repression, then communal conflict and extremism",
 "secs": ["Power & Office", "Life under Repression", "Conflict & Extremism"],
 "new_leaves": [{"key": "NEW1", "label": "Revolutionary Film", "breadth": "Dramas of militants, uprisings, strikes and revolutionary movements",
   "defn": "A drama whose subject is the making of revolution or militant struggle — the activist cell, the uprising, the strike, the liberation movement, often itself made as militant cinema (Wind from the East, Ice, Milestones, Finye, Good Morning, Night, Rang De Basanti). Films of life under a regime without organised resistance stay in Political Drama.",
   "aliases": "militant cinema; cinéma militant; revolutionary cinema", "src": WP("Third_Cinema"),
   "axis": "by era of the struggle: socialist-realist and early revolutionary films, the 1967–79 militant-cinema wave, then post-1980 activism and uprising",
   "secs": ["Socialist & Early Revolutionary Films (to 1966)", "Militant Cinema of 1967–1979", "Activism & Uprising since 1980"]}],
 "assign": A, "moves": []}
save(o)
import collections; print(collections.Counter(tuple(v) for v in A.values()))
