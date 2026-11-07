from lib import *
L = Leaf("A19-9")
# moves
L.move("Fallen Champ", "Sports Documentary", "Mike Tyson biography, not a political cause")
L.move("Desert One", "Historical Documentary", "history of the 1980 Iran hostage rescue mission")
L.move("A Lion in the House", "Direct Cinema & Cinéma Vérité", "observational film of children with cancer; no political cause")
# --- NEW1 environmental
env = {
 1: ["Minamata","The Shiranui Sea","Flere Atomkraftvaerker","Dark Circle","The Falls","Alexei and the Spring","Plastic Planet",
     "Vapor Trail","Beijing Besieged","No Man's Zone","1700 kelvin","The End of the World Begins","After the Apocalypse","Wake: Subic",
     "Behemoth","Sonic Sea","The Secret Life of Landfill","Rejeito","The Flat Jungle"],
 2: ["And on the Eighth Day","An Inconvenient Truth","The 11th Hour","Home$","Chasing Ice","Before the Flood","Chasing Coral",
     "Anthropocene","The Human Scale","The Unforeseen","Un Pays en flammes","Go Further","If a Tree Falls"],
 3: ["September Wheat","The Animals Film","Earthlings","McLibel","Food, Inc.","The Cove","A Place at the Table","Cowspiracy",
     "That Sugar Film","What the Health","Dominion","The Game Changers","Seaspiracy"],
 4: ["Narmada","Mauna Kea","Q2P","Impenetrable","Raising Resistance","Virunga","Koneline","Angry Inuk","The Territory","La Rivière",
     "Lonely Oaks","The Battle for Laikipia","Yintah","Patrol","River of Grass"],
}
for s, names in env.items(): L.put(names, "NEW1", s)
# --- NEW2 militant cinema
mil = {
 1: ["Ogawa", "Noriaki Tsuchimoto", "Fumio Kamei", "Sato, Mitsuo"],
 2: ["José Massip","Leobardo Lopez","Patricio Guzmán","Vladimir Carvalho","Lumbreras","Sergio Rezende","Leon Hirszman","Mattei, Georges"],
 3: ["Godard, Jean-Luc","von Alemann","Le Masson","Thomas Harlan","Abouda","Karlin, Marc","Flütsch","Clayton, Susan","Jean-Pierre Thorn",
     "Cinema Action","Jürg Hassler","Peter Lennon","Peter Whitehead","Karel Vachek","Pere Portabella","Rui Simoes","Peter Watkins","Chris Marker","Milton Bryan"],
 4: ["Bird, Stewart","Howard Alk","William Greaves","Yolande DuLuart","Cinda Firestone","Warrington Hudlin","Peter Biskind","Emile de Antonio","Brown, Barry"],
 5: ["Merata Mita","Deepa Dhanraj","Hussein Torabi"],
}
for s, subs in mil.items():
    for t in L.T:
        if t["id"] in L.A or yr(t) > 1990: continue
        if any(x.lower() in (t["who"] or "").lower() for x in subs): L.A[t["id"]] = ["NEW2", s]
L.put(["Informe general"], "NEW2", 3)
L.put(["The Battle of Chile"], "NEW2", 2)
# --- NEW3 LGBTQ
lg = {
 1: ["Word Is Out","Gay USA","Before Stonewall","The Times of Harvey Milk","Improper Conduct","Forbidden Love","No Secret Anymore",
     "Man Made","Screaming Queens","Rebel Dykes","Trembling Before G-d","Pray Away"],
 2: ["Bright Eyes","Common Threads","We Were Here","United in Anger","How to Survive a Plague","Larry Kramer","Fig Trees"],
 3: ["Suddenly, Last Winter","Queer China","Call Me Kuchu","Indianara","Welcome to Chechyna","Framing Agnes","Kokomo City","The Stroll",
     "Beyond the Aggressives","Queendom"],
}
for s, names in lg.items(): L.put(names, "NEW3", s)
# --- self: split old sec 6
elect = ["Four More Years","Our Brand is Crisis","Street Fight","Anytown, USA","This Divided State","Hacer patria","Citizen Juling",
 "Videocracy","Democrats","Weiner","Get Me Roger Stone","The King","Brexitannia","Knock Down the House","The Edge of Democracy","Mayor",
 "President","Bobi Wine","Cocalero","La Cosa","The Champions","Apocalypse in the Tropics","Lost Course","Millhouse","The Big Durian"]
for nm in elect:
    for t in L.find(nm):
        if t["id"] not in L.A: L.A[t["id"]] = ["self", 5]
L.put(["El Silencio de otros"], "self", 3)
L.put(["Prison and Paradise"], "self", 1)
L.put(["The Big One"], "self", 1)
L.put(["Yoake no kuni"], "self", 6)
m = {"1": 1, "3": 2, "4": 3, "5": 4, "6": 6, "2": 1}
L.rest(lambda t: ["self", m.get(t["sec"], 6)])
OUT["A19-9"] = {
 "defn": "A documentary that takes a side on a public issue or follows a political movement, campaign or politician (Roger &amp; Me, Harlan County U.S.A., 13th, The Square). Environmental causes go to Environmental Documentary, films made inside 1957–1990 militant movements to Militant Cinema, LGBTQ liberation and rights to LGBTQ Documentary; exposés of hidden wrongdoing to A19-10.",
 "axis": "by the cause: first-person polemic, labour, civil and human rights, women's movements, elections and politicians, then protest and uprisings",
 "secs": ["Polemic & First-Person Advocacy", "Labour & Class", "Civil Rights, Race & Human Rights", "Women's Movements", "Elections, Parties & Politicians", "Protest, Uprisings & Revolutions"],
 "new_leaves": [
  {"key": "NEW1", "label": "Environmental Documentary", "breadth": "Documentaries of ecological causes: pollution, climate, food and animals, land defence",
   "defn": "A documentary that argues an ecological cause — industrial pollution and nuclear risk, climate change, the food system and animal welfare, or a community's defence of its land and water (Minamata, An Inconvenient Truth, Food, Inc., The Cove, Virunga). A nature film without an argument goes to Nature Documentary.",
   "aliases": "eco-documentary; environmental film", "src": [["https://en.wikipedia.org/wiki/Environmental_film", "Wikipedia"]],
   "axis": "by the cause: pollution and disaster, climate and the planet, food and animals, then land, water and indigenous defence",
   "secs": ["Pollution, Nuclear & Industrial Disaster", "Climate & the Planet", "Food, Health & Animals", "Land, Water & Indigenous Defence"]},
  {"key": "NEW2", "label": "Militant Cinema", "breadth": "Documentaries made inside a movement as its weapon, 1957–1990: collectives, Newsreel, Third Cinema",
   "defn": "A documentary made from inside a struggle by its participants or a film collective, as an instrument of the movement rather than a report on it, in the cycle from the late 1950s to 1990 (The Battle of Chile, Summer in Narita, Finally Got the News…, The Nightcleaners, Patu!). Later activist films stay in Political Documentary.",
   "aliases": "cinéma militant; Third Cinema; Newsreel; collective documentary", "src": [["https://en.wikipedia.org/wiki/Third_Cinema", "Wikipedia"]],
   "axis": "by national movement: Japanese collectives, Latin American Third Cinema, European militant collectives, North American Newsreel and Black radical cinema, then Asia, Africa and Oceania",
   "secs": ["Japanese Collective Documentary", "Latin American Third Cinema", "European Militant Collectives", "North American Newsreel & Black Radical Cinema", "Asia, Africa & Oceania"]},
  {"key": "NEW3", "label": "LGBTQ Documentary", "breadth": "Documentaries of gay, lesbian and trans liberation, AIDS activism and LGBTQ rights",
   "defn": "A documentary about LGBTQ people as a political community — gay liberation and its histories, AIDS activism, trans lives and the global fight for LGBTQ rights (Word Is Out, The Times of Harvey Milk, How to Survive a Plague, Kokomo City). A portrait of one queer artist goes to Biographical Documentary.",
   "aliases": "queer documentary; gay and lesbian documentary", "src": [["https://en.wikipedia.org/wiki/LGBTQ_cinema", "Wikipedia"]],
   "axis": "by the cause: liberation and queer histories, AIDS activism, then trans lives and LGBTQ rights worldwide",
   "secs": ["Gay Liberation & Queer Histories", "AIDS Activism", "Trans Lives & Global LGBTQ Rights"]}],
 "assign": L.A, "moves": L.moves}
save()
