from lib import *
L = Leaf("A14-1")
def region(c):
    c0 = (c or "").split("-")[0]
    if c0 in ("France", "FR", "Belgium"): return 1
    if c0 in ("Germany", "DE", "West Germany", "East Germany", "XG", "Austria"): return 2
    if c0 in ("USSR", "Russia", "Czechoslovakia", "CZ", "Hungary", "YU", "RS", "Poland", "AZ"): return 3
    if c0 in ("UK", "GB", "Spain", "ES", "Italy", "Greece", "Finland", "Portugal", "Norway"): return 4
    if c0 in ("Argentina", "Mexico", "BR", "Brazil", "PE", "Cuba"): return 5
    if c0 in ("Egypt", "LB", "CD", "South Africa", "CV", "Nigeria"): return 6
    return 7
overrides = {"Bride & Prejudice": 7, "Tangos: The Exile of Gardel": 5, "The Moon Over the Alley": 4, "Beloved": 1,
 "Silence… on tourne": 6, "One Night the Moon": 7, "Bran Nue Dae": 7, "Siméon": 1, "Under the Roofs of Paris": 1,
 "Yidl Mitn Fidl": 3, "Don Quixote": 2, "Three Penny Opera": 2, "Feuerwerk": 2, "Black Orpheus": 5}
for t in L.T:
    if t["sec"] == "6" or (t["sec"] == "" and t["year"] and yr(t) < 1960 and "Clair" in (t["who"] or "")) or t["title"] == "Traktoristy":
        L.A[t["id"]] = ["NEW1", overrides.get(t["title"], region(t["country"]))]
# René Clair's Hollywood/British films stay with his French work in NEW1
for t in L.T:
    if "René Clair" in (t["who"] or ""): L.A[t["id"]] = ["NEW1", 1]
L.put(["So Proudly We Hail!"], "self", 1)
L.put(["Idlewild", "1 Day"], "self", 5)
L.put(["In the Heights"], "self", 2)
m = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "7": 6}
L.rest(lambda t: ["self", m[t["sec"]]])
OUT["A14-1"] = {
 "defn": "An American-tradition musical film whose songs and dances arise inside the story and carry plot and character, written for the screen or adapted from the stage (Top Hat, Meet Me in St. Louis, West Side Story, La La Land). Integrated musicals of other national cinemas go to European & World Film Musical; numbers staged as performances to A14-4; an all-sung film to A14-5.",
 "axis": "by origin and audience: Hollywood studio originals, Broadway adaptations, family musicals, teen musicals, later screen originals, and the Astaire–Rogers cycle",
 "secs": ["Hollywood Studio Musicals", "Broadway Adaptations", "Family & Fantasy Musicals", "Teen & High-School Musicals", "Contemporary Screen Originals", "Astaire–Rogers RKO Musicals (1933–1939)"],
 "new_leaves": [
  {"key": "NEW1", "label": "European & World Film Musical", "breadth": "Integrated film musicals of national cinemas outside Hollywood",
   "defn": "A book musical — songs and dances carrying the story — made in a national film industry outside Hollywood: René Clair's French musicals, German Tonfilm comedies, the Soviet musical comedies of Aleksandrov and Pyryev, the Egyptian and Lebanese musical, the films of Demy and Honoré (Le Million, Volga-Volga, The Young Girls of Rochefort, Love Songs). Operettas go to Operetta Film; Hindi masala films, rumberas and comedia ranchera to their own leaves.",
   "aliases": "international film musical; non-Hollywood musical", "src": [["https://en.wikipedia.org/wiki/Musical_film", "Wikipedia"]],
   "axis": "by national tradition",
   "secs": ["French", "German & Austrian", "Soviet & Eastern European", "British, Iberian & Other European", "Latin American", "Arab & African", "Asian & Oceanian"]}],
 "assign": L.A, "moves": L.moves}
save()
