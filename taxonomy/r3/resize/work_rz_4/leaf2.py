from common import *
C="A16-22"
ov = {}
ov.update(W_(C,"NEW2",1,"Die Goldene Pest"))
ov.update(W_(C,"self",3,"Paulina"))
ov.update(W_(C,"self",3,"Test Pattern"))
A = build(C, {"1":("NEW1",1),"2":("NEW1",2),"3":("NEW1",3),"4":("self",1),"5":("self",2),"6":("self",3),"7":("self",4),"8":lambda t:("NEW2",1 if yr(t)<1960 else 2 if yr(t)<2000 else 3)}, ov)
o = {"label":"Social Problem Film",
 "defn":"A drama built to expose one named social ill of prejudice, violence or patriarchy — racism and caste, youth violence and its institutions, sexual violence and reproductive rights, the oppression of women (Gentleman's Agreement, Within Our Gates, Never Rarely Sometimes Always, Moolaadé). Addiction goes to the Addiction Drama; prostitution and trafficking to the Prostitution Film; diffuse working-class hardship to A16-19; the courtroom to A16-25.",
 "axis":"by the social ill: race and caste first, then youth violence and reform schools, sexual violence and reproductive rights, and the oppression of women last",
 "secs":["Race & Caste","Youth Violence & Reform Schools","Sexual Violence & Reproductive Rights","Patriarchy & Women's Rights"],
 "new_leaves":[
  {"key":"NEW1","label":"Addiction Drama","breadth":"social-problem dramas of drink, drugs and gambling",
   "defn":"A drama whose engine is one person's or one milieu's addiction — to alcohol, drugs or gambling — followed through craving, collapse and (sometimes) recovery (The Lost Weekend, Days of Wine and Roses, The Man with the Golden Arm, Requiem for a Dream, The Gambler). Test: the addiction itself is the subject, not a backdrop to crime (A2) or a psychological portrait (A16-7).",
   "aliases":"drug film; alcoholism film; addiction film","src":[["https://en.wikipedia.org/wiki/Drug_film","Wikipedia"]],
   "axis":"by the substance: drink first, then drugs, and gambling last",
   "secs":["Alcoholism","Drug Addiction","Gambling"]},
  {"key":"NEW2","label":"Prostitution Film","breadth":"dramas of sex work, the fallen woman and trafficking",
   "defn":"A drama whose subject is prostitution as a social condition — the fallen woman of the silent and studio eras, the brothel and the red-light district, the street, and modern trafficking (Diary of a Lost Girl, Street of Shame, Nights of Cabiria, Mamma Roma, Lilya 4-Ever, Much Loved). Test: selling sex is the protagonist's situation and the film's subject; an erotic treatment goes to A15.",
   "aliases":"fallen-woman film; sex-work drama; trafficking drama","src":[["https://en.wikipedia.org/wiki/Fallen_woman","Wikipedia"]],
   "axis":"by era, as the field divides it: the fallen-woman film of the silent and early sound eras, the postwar brothel and red-light film, then the modern sex-work and trafficking drama",
   "secs":["Fallen Women (to 1959)","Brothels & Red-Light Districts (1960–1999)","Sex Work & Trafficking (2000– )"]}],
 "assign":A,"moves":[]}
save(C,o); report(C,A)
