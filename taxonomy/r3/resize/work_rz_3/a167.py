from lib import *
L = Leaf("A16-7")
guilt = ["The Whispering Chorus","Broken Lullaby","The Guilt of Janet Ames","Rumors","Kokoro","Just Before Nightfall","The Youth Killer",
 "The Eel","The Woodsman","Manslaughter/Drabet","The Free Will","Stephanie Daley","Dry Season","The Kite Runner","Boy A","Seven Pounds",
 "Margaret","Michael","What Richard Did","The Hunt","Magallanes","Jindabyne","Levity","Every Thing Will Be Fine","Downriver","Maelstrom",
 "Daagi","The Unforgiven","Innocence","The United States of Leland","Betty","One Night","Student","The Wild Pear Tree","Blind Spot",
 "The Third Page","Fate/Yazgi","After the Curfew","Wicked Games"]
L.put(guilt, "self", 2)
L.put(["Straight to the Heart"], "self", 3)
L.put(["The Three Faces of Eve"], "NEW2", 1)
L.put(["Madre"], "NEW1", 3)
def era4(t, cuts):
    y = yr(t)
    for i, c in enumerate(cuts):
        if y < c: return i + 1
    return len(cuts) + 1
def d(t):
    s = t["sec"]
    if s == "1": return ["NEW1", era4(t, [2000, 2010, 2020])]
    if s == "2": return ["NEW2", era4(t, [1970, 2000, 2015])]
    if s == "3": return ["self", 1]
    return ["self", 3]
L.rest(d)
OUT["A16-7"] = {
 "label": "Psychological Drama",
 "defn": "A drama whose engine is one person's inner state of trauma, guilt or obsession, rendered from inside (Peppermint Candy, Affliction, Death in Venice, The Master). A drama of mourning goes to Grief Drama, one of madness and mental illness to Mental Illness Drama; where suspense drives it, see A3; where the crisis is existential rather than psychological, A16-8.",
 "axis": "by the inner condition: trauma and abuse first, then guilt and atonement, and obsession last",
 "secs": ["Trauma & Abuse", "Guilt & Atonement", "Obsession & Desire"],
 "new_leaves": [
  {"key": "NEW1", "label": "Grief Drama", "breadth": "Dramas of mourning: the bereaved spouse, parent or friend living through a death",
   "defn": "A drama whose subject is grief itself — a widow, widower, parent or friend living through loss, often in the long aftermath of a death (Three Colors: Blue, Maborosi, Manchester by the Sea, Drive My Car). A family collectively bereaved goes to Family Drama; a grief that becomes breakdown, to Mental Illness Drama.",
   "aliases": "bereavement drama; mourning film", "src": [["https://en.wikipedia.org/wiki/Grief", "Wikipedia"]],
   "axis": "by era", "secs": ["Before 2000", "2000–2009", "2010–2019", "2020 onward"]},
  {"key": "NEW2", "label": "Mental Illness Drama", "breadth": "Dramas of madness, breakdown, psychosis and the asylum",
   "defn": "A drama of a mind coming apart — schizophrenia, psychosis, depression, dissociation, breakdown — or of life in the asylum and clinic (Through a Glass Darkly, The Cobweb, Clean, Shaven, Spider, Take Shelter). A psychological thriller goes to A3; a grief drama to Grief Drama.",
   "aliases": "madness film; asylum drama; mental illness in film", "src": [["https://en.wikipedia.org/wiki/Mental_illness_in_film", "Wikipedia"]],
   "axis": "by era: the studio-era psychiatric drama, the anti-psychiatry and modernist decades, then the contemporary independent character study",
   "secs": ["Before 1970", "1970–1999", "2000–2014", "2015 onward"]}],
 "assign": L.A, "moves": L.moves}
save()
