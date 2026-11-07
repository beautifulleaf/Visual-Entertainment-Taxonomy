from common import *
C="A16-9"
ORD=["east","west","eastEu","na","latam","other"]
fix={i:"eastEu" for i in T(C,"An Unwritten Letter","Promeny pritelkyne evy","Easy Fault")}
def rg(t): return fix.get(t["id"], region(t))
A = build(C, {"":lambda t:("self",ORD.index(rg(t))+1),"1":lambda t:("self",ORD.index(rg(t))+1),"2":lambda t:("NEW1",ORD.index(rg(t))+1)}, {})
SECS=["East Asia","Western Europe","Eastern Europe, the Caucasus & Central Asia","North America","Latin America","Middle East, Africa, South & Southeast Asia, Oceania"]
o = {"label":"Slice of Life",
 "defn":"A drama with no plot engine beyond a settled daily life observed — routines, rituals, small encounters and the passing days of people at home in their place (Paterson, Perfect Days, Café Lumière, The Scent of Green Papaya). A life adrift goes to the Drifter Film; a crisis of meaning to A16-8; a journey to A16-36.",
 "axis":"by national and regional tradition, as festival everyday cinema is grouped: East Asia first (the Japanese, Korean, Chinese and Taiwanese quotidian film), then Western Europe, Eastern Europe and Central Asia, North America, Latin America, and the rest of the world last",
 "secs":SECS,
 "new_leaves":[{"key":"NEW1","label":"Drifter Film","breadth":"dramas of loners and drifters without settled place or purpose",
   "defn":"A drama of observed days whose protagonist is adrift — a loner, wanderer or young person between jobs, homes and attachments, followed without a plot engine (Wanda, Wendy and Lucy, Naked, Millennium Mambo, Morvern Callar, Old Joy). Test: the life is unsettled and the drift is the subject; a journey with a destination goes to A16-36, a settled daily routine stays in A16-9.",
   "aliases":"drifter drama; loner film","src":[["https://en.wikipedia.org/wiki/Drifter_(person)","Wikipedia"]],
   "axis":"by national and regional tradition: East Asia first, then Western Europe, Eastern Europe and Central Asia, North America, Latin America, and the rest of the world last",
   "secs":SECS}],
 "assign":A,"moves":[]}
save(C,o); report(C,A)
