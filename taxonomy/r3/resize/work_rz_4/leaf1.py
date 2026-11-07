from common import *
C="A16-8"
def s1(t):
    y=yr(t); return ("self", 1 if y<1980 else 2 if y<2000 else 3)
old = T(C,"The End of the Road","The Immortal Story","Szindbád","Conversation Piece","Madame Rosa","Chastnaya zhizn","Infinity","Three Colors: Red","Nelly & Monsieur Arnaud","Inquietude","Paraguayan Hammock","O'Horten","Autumn","Gran Torino","Cloud 9","That Evening Sun","Poetry","Tey","Bwakaw","Bright Days Ahead","Sweet Bean","Mr. Holmes","Youth","Aquarius","Lucky","The Heiresses","Diane","The Man Who Killed Hitler","The Life Ahead","This Is Not a Burial","Cosas imposibles","Utama","Sunday")
review = T(C,"Parthenope","The Life of Chuck")+["tt0020814"]
ov = {}
for i in old: ov[i]=("NEW1",3)
for i in review: ov[i]=("NEW1",1)
ov.update(W_(C,"self",4,"The Razor's Edge"))
ov.update(W_(C,"self",3,"On War"))
A = build(C, {"1":s1,"2":("self",4),"3":("self",5),"4":("NEW1",1),"5":("NEW1",2)}, ov)
o = {"label":"Existentialist Film",
 "defn":"An art-film character study whose engine is a crisis of meaning in the present tense — alienation, ennui, or a self disguised or doubled (La Dolce Vita, The Silence, Lost in Translation, The Passenger, The Double Life of Véronique). A life weighed up at its middle or end goes to the Midlife Crisis Film; a clinical inner state to A16-7; a quiet everyday portrait to A16-9.",
 "axis":"by the shape of the crisis: alienation first, divided by era (the postwar modernist wave to 1979, its late-modernist continuation in the 1980s–90s, the contemporary festival film), then the ennui of the affluent, and double lives and masks last",
 "secs":["Modernist Alienation (to 1979)","Late-Modernist Alienation (1980–1999)","Contemporary Alienation (2000– )","Ennui of the Affluent","Double Lives & Masks"],
 "new_leaves":[{"key":"NEW1","label":"Midlife Crisis Film","breadth":"existential dramas of a life weighed up — at its middle, in old age, or reviewed whole from rise to fall",
   "defn":"A drama whose crisis of meaning comes from taking stock of a life already lived: the midlife crisis, the reckoning of old age, or a whole life reviewed in its rise and fall (Dodsworth, Save the Tiger, Husbands, Citizen Kane, Death of a Salesman, Youth, Gran Torino). Test: the film's engine is the review of a life's course rather than a present-tense alienation (A16-8) or a clinical breakdown (A16-7).",
   "aliases":"midlife-crisis drama; late-life drama; life-review film","src":[["https://en.wikipedia.org/wiki/Midlife_crisis","Wikipedia"]],
   "axis":"by where the life is weighed up: the whole life reviewed in its rise and fall first, then the crisis at midlife, and old age and last reckonings last",
   "secs":["Rise-and-Fall Lives","Midlife Crisis","Old Age & Last Reckonings"]}],
 "assign":A,"moves":[]}
save(C,o); report(C,A)
