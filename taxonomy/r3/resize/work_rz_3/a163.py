from lib import *
L = Leaf("A16-3")
sisters = ["Zi mei hua","Badi Bahen","They Were Sisters","Our Sister Hedy","Koto","The Makioka Sisters","Oriana","The Color Purple",
 "The Whales of August","The Dressmaker","Sweetie","The Last Days of Chez Nous","Georgia","Marvin's Room","Eve's Bayou","Pauline & Paulette",
 "Ladies in Lavender","In Her Shoes","I've Loved You So Long","Back to Stay","Suzanne","Our Little Sister","Margot at the Wedding",
 "My Sister's Keeper","Cake","Dolly Kitty","Paradise is Burning","The Silent Twins","The Line","Girls on Wire","Cousins","El Mundo sigue",
 "Radiance","The Vertical Ray of the Sun","Hard Truths","Donkey Days","The Secret Rapture","Thick Skinned","To Live"]
brothers = ["East of Eden","Rocco and His Brothers","Family Diary","All Fall Down","Vash syn i brat","Upkar","The Birch Wood",
 "Three Brothers","Dominick and Eugene","Blood","Return Home","The Indian Runner","A River Runs Through It","Simple Men",
 "The Way We Laughed","Twin Falls Idaho","Erskinville Kings","Tully","Pau and His Brother","Life Marks","Agnes and His Brothers",
 "Three Dancing Slaves","The Letters","Sway","Dans Paris","Private Property","My Brother is an Only Child","Shotgun Stories",
 "Brothers","Tetro","I Wish","The Porcelain Horse","Seethamma","Kumbalangi Nights","Brother$","A Normal Family","Anemone",
 "My Father's Shadow","Perayaan Mati Rasa","The Quiet Son"]
for nm in sisters:
    for t in L.find(nm):
        if t["sec"] in ("1", ""): L.A[t["id"]] = ["NEW1", 1]
for nm in brothers:
    for t in L.find(nm):
        if t["sec"] == "1": L.A[t["id"]] = ["NEW1", 2]
foster = ["The Jack-Knife Man","Sono ato no hachi","Foster-mother","Ty ne sirota","Wechselbalg","Vojtech","The King of Masks","Lucky Star",
 "Foster Child","The Unloved","The Kid with a Bike","La Mif","The Quiet Girl","A Thousand and One"]
adopt = ["Adoption","Secrets & Lies","Kannathil Muthamittal","Holy Lola","Loggerheads","A Brand New Life","Beautiful Duckling",
 "In Safe Hands","True Mothers","Nowhere Special","Return to Seoul","The Odd Life of Timothy Green"]
L.put(foster, "NEW2", 1); L.put(adopt, "NEW2", 2)
L.put(["Umm el-Arusah", "A Wedding"], "self", 2)
L.put(["At Any Price"], "self", 3)
def d(t):
    s = t["sec"]
    if s == "1": return ["NEW1", 3]
    if s == "2": return ["self", 2]
    if s == "3": return ["self", 3]
    if s == "4": return ["self", 4]
    if s == "5": return ["NEW2", 3]
    return ["self", 1]
L.rest(d)
OUT["A16-3"] = {
 "defn": "A drama whose engine is the family as a group rather than one parent–child pair or one sibling bond: the household, the family gathered for a holiday or funeral, the inheritance, the home after a death (Still Walking, Rachel Getting Married, Summer Hours, Ordinary People). Siblings go to Sibling Drama; foster, adoptive and chosen families to Found Family Film; one parent and child to A16-4; a couple to A16-5.",
 "axis": "by the family occasion: the household, then the gathered family, the inheritance, and the bereaved home last",
 "secs": ["The Family Household", "Family Gatherings & Reunions", "Inheritance, Feuds & Family Fortunes", "Bereaved Families"],
 "new_leaves": [
  {"key": "NEW1", "label": "Sibling Drama", "breadth": "Dramas of sisters, brothers and brother–sister bonds",
   "defn": "A family drama centred on siblings — sisters, brothers, or a brother and sister — their rivalry, devotion or estrangement (Rocco and His Brothers, The Makioka Sisters, You Can Count on Me, Our Little Sister, Frère et soeur). A drama of the whole family goes to Family Drama.",
   "aliases": "sister film; brothers film", "src": [["https://en.wikipedia.org/wiki/Sibling_relationship", "Wikipedia"]],
   "axis": "by the sibling bond: sisters, brothers, then brother and sister and mixed sibling groups",
   "secs": ["Sisters", "Brothers", "Brothers & Sisters"]},
  {"key": "NEW2", "label": "Found Family Film", "breadth": "Dramas of foster, adoptive and chosen families",
   "defn": "A family drama whose family is made rather than born: the foster home and the orphan taken in, adoption and the search for birth origins, the chosen family of strangers (The Kid with a Bike, Secrets & Lies, Shoplifters, The Quiet Girl, Return to Seoul).",
   "aliases": "chosen family; foster family drama; adoption drama", "src": [["https://en.wikipedia.org/wiki/Found_family", "Wikipedia"]],
   "axis": "by how the family is made: fostering and orphans, adoption and birth origins, then chosen families",
   "secs": ["Foster Care & Orphans", "Adoption & Birth Origins", "Chosen Families"]}],
 "assign": L.A, "moves": L.moves}
save()
