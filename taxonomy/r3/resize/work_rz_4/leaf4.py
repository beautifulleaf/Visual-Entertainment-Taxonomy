from common import *
C="A16-6"
SA={"India","IN","Sri Lanka","Uzbekistan","Pakistan"}
def wf(t):
    y=yr(t); c=cc(t); r=region(t)
    if y and y<1930: return ("NEW1",1)
    if c in ("JP","Japan"): return ("NEW1",4)
    if r=="east" or c in SA: return ("NEW1",5)
    if y>=1970: return ("NEW1",7)
    if r=="na": return ("NEW1",2)
    if r=="latam": return ("NEW1",6)
    return ("NEW1",3)
ov={}
def put(k,*ts):
    for i in T(C,*ts): ov[i]=k
# unassigned
for ts,k in [
 (["Wife, Be Like a Rose","Five Men in the Circus","The Girl in the Rumour","Magokoro","Spring Awakens","Lightning","Older Brother, Younger Sister","Sound of the Mountain","Iwashigumo","The Approach of Autumn","Letter of Introduction","Kings Row","Treno popolare","All I Desire","There's Always Tomorrow","Peyton Place"],("self",2)),
 (["Mother","Final Accord","The Abandoned","Nobody's Children"],("self",1)),
 (["Has Anybody Seen My Gal?","Meet Me at the Fair","No Room for the Groom","Take Me to Town","Weekend with Father","Sign of the Pagan","Taza, Son of Cochise","Captain Lightfoot","Battle Hymn","A Scandal in Paris","Sleep, My Love","Shockproof","A Time to Love and a Time to Die"],("self",4)),
]: put(k,*ts)
for ts in [["The Actress and the Poet","Three Sisters with Maiden Hearts","Tsuruhachi Tsurujirô","The Song Lantern","Meshi","Wife","Late Chrysanthemums","Flowing","Sudden Rain","Anzukko","Drifting","Yearning","Scattered Clouds"],
           ["Assunta Spina","The Diary of a Lost Woman","Looping the Loop","To New Shores","La Habanera","La Fumeria d'oppio","The Ship of Condemned Women","My Love","Summer Storm","Interlude"]]:
    for i in T(C,*ts): ov[i]=wf([t for t in IN[C]["titles"] if t["id"]==i][0])
# sec4/3 sanity: Grand Hotel is ensemble -> family? keep illness? move to woman's film
A = build(C, {"1":("self",1),"2":wf,"3":("self",2),"4":("self",3)}, ov)
o = {"label":"Melodrama",
 "defn":"A drama in the melodramatic mode — heightened emotion, sacrifice and fate carried by music and mise-en-scène — whose sacrifice is made for a child or a family, or to illness (Stella Dallas, Imitation of Life, Written on the Wind, Dark Victory, All About My Mother). The melodrama of the fallen, desiring or self-sacrificing woman in love goes to the Woman's Film; realist family dramas to A16-3 to A16-5.",
 "axis":"by the sacrifice at the core: maternal sacrifice first, then the family melodrama, the illness tearjerker, and Sirk's non-melodrama studio pictures last",
 "secs":["Maternal Melodrama","Family Melodrama","Illness Tearjerkers","Sirk's Comedies, Westerns & War Pictures"],
 "new_leaves":[{"key":"NEW1","label":"Woman's Film","breadth":"melodramas of the fallen, desiring or self-sacrificing woman, across national studio traditions",
   "defn":"A melodrama centred on a woman's desire, fall or sacrifice in love, marriage or work, made for and around a female star or a woman's point of view (The Cheat, Pandora's Box, Back Street, All That Heaven Allows, When a Woman Ascends the Stairs, Far from Heaven). Test: the heroine's own passion or fall is the engine; sacrifice for a child or a family stays in A16-6.",
   "aliases":"woman's picture; women's film; fallen-woman melodrama; josei eiga","src":[["https://en.wikipedia.org/wiki/Woman%27s_film","Wikipedia"]],
   "axis":"by era and national studio tradition: the silent vamp and fallen woman first, then the Hollywood woman's film, the European, Japanese, Chinese-Korean-Indian and Latin American traditions, and the modern revisionist woman's film last",
   "secs":["Silent Vamps & Fallen Women (to 1929)","Hollywood Woman's Film","European Woman's Film","Japanese Women's Films","Chinese, Korean & Indian Women's Melodrama","Latin American Melodrama","Modern & Revisionist Woman's Film (1970– )"]}],
 "assign":A,"moves":[]}
save(C,o); report(C,A)
