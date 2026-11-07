from lib import *
L = Leaf("A20-7")
# --- NEW2 artists' film & installation
artists = ["Ono, Yoko","Baldessari","Bill Viola","McCarthy","Mike Kelley","Matthew Barney","Douglas Gordon","Ahtila","Stan Douglas",
 "Bartana","Gonzalez-Foerster","Ange Leccia","Yang Fudong","Kirschner","Burns, A.K.","Ashery","van der Werve","Emily Wardill",
 "Liz Magic Laser","Senatore","Keren Cytter","Rosa Barba","Phil Collins","De Landa","Omer Fast","Rachel Maclean","Akomfrah",
 "Rosefeldt","Sondra Perry","Beloufa","Tacita Dean","Dellsperger","Wael Shawky","Shu Lea Cheang","Khaled Hafez","Kvium",
 "Mirza, Karen","Kuntzel","Škarnulytė","Ana Torfs","Ariane Michel","Mark (Canada) Lewis","Jesse Jones","Beatriz Santiago",
 "Neuman, Arjana","Tamar Guimarães","Deniz Eroglu","Futoshi Miyagi","Klonaris","Martos, Deneb","Niemczyk","Wallis, Clea",
 "Malashchuk","Forbes-Hamilton","Bamboat","Kasses","Aragno","Bani Khoshnoudi","Gregg Bordowitz","Daniel Barnett"]
def art_sec(t):
    if "[INSTALLATION]" in t["title"] or "[EXHIBITION]" in t["title"]: return 1
    return 2 if yr(t) < 2010 else 3
for t in L.T:
    if "[INSTALLATION]" in t["title"] or "[EXHIBITION]" in t["title"] or any(s.lower() in (t["who"] or "").lower() for s in artists):
        L.A[t["id"]] = ["NEW2", art_sec(t)]
# --- NEW1 counter-cinema, sections by national tradition
cc = {
 1: ["Marguerite Duras","Hanoun","Straub","Raynal","Pollet","Raúl Ruiz","Hugo Santiago","Eduardo de Gregorio","Alain Fleischer",
     "Carasco","Catherine Binet","Jean-Luc Godard"],
 2: ["Carmelo Bene","Edoardo Bruno","Taviani","Bellocchio","Portabella","Paulino Viota","João César Monteiro","Manoel de Oliveira",
     "Stavros Tornes","Kostas Sfikas","Angelidi"],
 3: ["Vlado Kristl","Werner Schroeter","Syberberg","Ottinger","Akerman, Chantal/Maxi","Karmakar","Gábor Bódy","Jancsó","Petr Skála",
     "Klopfenstein","Erik Løchen"],
 4: ["Yvonne Rainer","Mulvey","Sally Potter","Ronay, Esther","Mark Rappaport","Leslie Thornton","Ken McMullen","Stephen Dwoskin"],
 5: ["Glauber Rocha","García Espinosa"],
}
for s, subs in cc.items():
    for t in L.T:
        if t["id"] in L.A: continue
        if any(x.lower() in (t["who"] or "").lower() for x in subs): L.A[t["id"]] = ["NEW1", s]
# Kidlat Tahimik's Third Cinema fable sits with counter-cinema's non-Western wing
L.put(["Perfumed Nightmare"], "NEW1", 5)
L.put(["Love and Anger"], "NEW1", 2)
L.put(["Centro Histórico"], "self", 4)
def d(t):
    y = yr(t)
    if y < 1960: return ["self", 1]
    if y < 1990: return ["self", 2]
    if y < 2005: return ["self", 3]
    if y < 2015: return ["self", 4]
    if y < 2020: return ["self", 5]
    return ["self", 6]
L.rest(d)
OUT["A20-7"] = {
 "label": "Art Film",
 "defn": "A narrative feature whose avant-garde form (tableau, recitation, fragmentation, dream logic, anti-illusion) is its defining element (A Page of Madness, Limit, The Color of Pomegranates, Russian Ark, Holy Motors). The political-modernist 'counter-cinema' of Duras, Straub–Huillet, Godard and Rainer goes to Counter-Cinema; films made by gallery artists or for installation to Artists' Film & Video Installation; duration-based art films to A1-39 Slow Cinema.",
 "axis": "by era: the silent and interwar avant-garde feature, the poetic cinema of the 1960s–80s, then the later art-house avant-garde by period",
 "secs": ["Silent & Interwar Avant-Garde Features (to 1959)", "Poetic & Visionary Cinema (1960–1989)", "1990–2004", "2005–2014", "2015–2019", "2020 onward"],
 "new_leaves": [
  {"key": "NEW1", "label": "Counter-Cinema", "breadth": "Political-modernist narrative features of the 1960s–80s that dismantle illusion: text, recitation, distanciation",
   "defn": "A narrative feature in the political-modernist tradition Peter Wollen named 'counter-cinema': estrangement over identification, text and recitation over drama, the soundtrack split from the image, the narrative opened to theory (India Song, From the Clouds to the Resistance, Riddles of the Sphinx, Film About a Woman Who..., Salomé). Its core is 1968–1990, with its auteurs' later work; dream and tableau art films without that programme stay in Art Film.",
   "aliases": "political modernism; cinéma de la modernité; Brechtian cinema", "src": [["https://en.wikipedia.org/wiki/Peter_Wollen", "Wikipedia"]],
   "axis": "by national tradition: France and Belgium; Italy, Iberia and Greece; the German-speaking and Central European wing; the Anglo-American feminist wing; the Third Cinema wing",
   "secs": ["French & Belgian", "Italian, Iberian & Greek", "German & Central European", "British & North American", "Latin American & Asian"]},
  {"key": "NEW2", "label": "Artists' Film & Video Installation", "breadth": "Narrative and quasi-narrative works by gallery artists, and moving-image installations",
   "defn": "A moving-image work made by a visual artist from the gallery world, shown as a feature, a cycle or a multi-screen installation (Cremaster 3, Rape, Manifesto, Inconsolable Memories, Primitive). Underground and experimental filmmakers outside the art world stay in Art Film or their own leaves.",
   "aliases": "artists' cinema; gallery film; moving-image installation", "src": [["https://en.wikipedia.org/wiki/Video_installation", "Wikipedia"]],
   "axis": "by form and period: installations and exhibitions, then artists' features before and after 2010",
   "secs": ["Installations & Exhibitions", "Artists' Features to 2009", "Artists' Features 2010 onward"]}],
 "assign": L.A, "moves": L.moves}
save()
