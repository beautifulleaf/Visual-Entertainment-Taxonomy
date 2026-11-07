from lib import *
L = Leaf("A16-4")
sons = ["The Goose Woman","Pilgrimage","Le Mioche","None But the Lonely Heart","The Rocking Horse Winner","My Son John","Shyamchi Aai",
 "Sons and Lovers","A Raisin in the Sun","Binding Sentiments","Mama vyshla zamuzh","The Long Farewell","Furtivos","Entire Days Among the Trees",
 "Luna","Mater amatisima","Raggedy Man","Maicol","The Miracle","The Day the Sun Turned Cold","My Own","Eat Your Soup","The May Lady",
 "Comedy of Innocence","One Life Stand","Respiro","Dear Frankie","The Heart is Deceitful","Tokyo Tower","Flight of the Red Balloon",
 "Ramchand Pakistani","I Killed My Mother","The String","I'm Glad My Mother","Tender Son","Sebbe","Mama$","We Need to Talk About Kevin",
 "Roadie","Ilo Ilo","10.000 noches","Bad Hair","Mommy","Room","The Book of Henry","Life and Nothing More","Ben Is Back","Ramen Shop",
 "A Family Tour","Our Mothers","Mother$","Amparo","God's Creatures","When Morning Comes","The Damned Don't Cry","Big World",
 "Heaven is Beneath","Who Do I Belong To","Saba","On Your Lap","Out of Love"]
mothers_old = ["Szerelem","Les Fleurs sauvages","Dear Nanny","Mother","The Way Home","Baboussia","La Madre","Gatos Viejos",
 "She Doesn't Want to Sleep Alone","A Few Hours of Spring","Rosie","Last Laugh","Mamang","Stepne","How to Make Millions","When Fall Is Coming"]
sec = {t["id"]: t["sec"] for t in L.T}
for nm in sons:
    for t in L.find(nm):
        if t["sec"] == "3": L.A[t["id"]] = ["NEW1", 2]
for nm in mothers_old:
    for t in L.find(nm):
        if t["sec"] == "4": L.A[t["id"]] = ["NEW1", 3]
L.put(["The Apartment with Two Women", "Grbavica"], "NEW1", 1)
def d(t):
    s = t["sec"]
    if s == "2": return ["self", 2]
    if s == "3": return ["NEW1", 1]
    if s == "4": return ["self", 3]
    return ["self", 1]
L.rest(d)
OUT["A16-4"] = {
 "label": "Father–Child Drama",
 "defn": "A drama centred on a father and his child — the father–son or father–daughter bond strained, broken or repaired, into the father's old age (The Return, Aftersun, Fences, On Golden Pond, Like Father, Like Son). A mother and child goes to Mother–Child Drama; a drama of the whole family to A16-3; Japanese shomingeki to A16-1.",
 "axis": "by the child and the stage of life: fathers and sons, fathers and daughters, then ageing fathers (and parents) with their adult children",
 "secs": ["Fathers & Sons", "Fathers & Daughters", "Ageing Fathers & Adult Children"],
 "new_leaves": [
  {"key": "NEW1", "label": "Mother–Child Drama", "breadth": "Dramas of a mother and her daughter or son",
   "defn": "A drama centred on a mother and her child — the mother–daughter or mother–son bond, from childhood to the mother's old age (Autumn Sonata, Terms of Endearment, Mommy, I Killed My Mother, Room). A father and child goes to Father–Child Drama; a drama of the whole family to A16-3.",
   "aliases": "mother–daughter film; mother–son drama", "src": [["https://en.wikipedia.org/wiki/Motherhood", "Wikipedia"]],
   "axis": "by the child and the stage of life: mothers and daughters, mothers and sons, then ageing mothers (and grandmothers) with their adult children",
   "secs": ["Mothers & Daughters", "Mothers & Sons", "Ageing Mothers & Adult Children"]}],
 "assign": L.A, "moves": L.moves}
save()
