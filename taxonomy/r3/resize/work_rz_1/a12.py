from common import *
import collections
R=rows('A21-12')
ARTS1=[21,25,31,42,44,49,56,58,89,92,103,118,119,122,123,125,133,137,147,153,155,158,171,180,181,190,196,249,253]
ETH=[5,6,7,9,10,18,20,23,32,33,36,41,48,53,55,57,85,112,124,127,135,146,192,707,731]
POL1=[1,2,75,80,107,183,184,198,217,228,258]
DESETA=[35,37,38,47]
E2ARTS=[528,513,524,452,466,469,485,468,465,541,489,577,579,584,626,649,563,510,482,583,680,667,604,500]
E2POL=[581,612,685,641,617,467,479,483,507,562,540,569,592,658,520,545,495]
CITY=[369,370,372,373,374,375,376,377,378,380,383,387,388,390,392,396,398,403,408,414,424,441,371]
WRIT=[49,92,147,155,181,190,196,153]
FILM=[513,524,89,118,122,123,158,171,180,253,482,510,563,577,579,584,626,649,583,680,667]
MUSIC_PEOPLE=[56,119,133]
DANCE=[708,711,724,730,736,735,737]
def cls(r):
    n,s=r['n'],r['sec']
    if n in ETH: return 'NEW5'
    if n in ARTS1 or n in E2ARTS or s=='5': return 'NEW4'
    if n in POL1 or n in E2POL or s=='2': return 'NEW1'
    if n in DESETA or s=='3': return 'NEW2'
    if s=='4' or n==3: return 'NEW3'
    return 'self'
def sec(r,k):
    n,s,y=r['n'],r['sec'],r['y']
    if k=='self':
        if s=='6': return 6
        return 1 if y<=1959 else 2 if y<=1979 else 3 if y<=1999 else 4 if y<=2014 else 5
    if k=='NEW1': return 1 if y<=1959 else 2 if y<=1969 else 3 if y<=1979 else 4 if y<=2009 else 5
    if k=='NEW2':
        if n in CITY: return 1
        return 2 if y<=1969 else 3 if y<=1999 else 4
    if k=='NEW3': return 1 if y<=1979 else 2 if y<=1999 else 3 if y<=2014 else 4 if y<=2019 else 5
    if k=='NEW4':
        if n in DANCE: return 5
        if s=='5' or n in MUSIC_PEOPLE: return 4
        if n in FILM: return 3
        if n in WRIT: return 2
        return 1
    if k=='NEW5': return 1 if y<=1949 else 2 if y<=1979 else 3
src=lambda u:[[u,'Wikipedia']]
out={'label':'Documentary Short',
 'defn':'A nonfiction short of the sound era observing people, work and social life at first hand — portraits, social observation and sport — not made as sponsored, scientific, political, poetic, essay, arts or ethnographic film (Le Sang des bêtes, Les Raquetteurs, Talking Heads, Period. End of Sentence.).',
 'axis':'by era for portrait and social shorts, then sport',
 'secs':['Portrait & Social Shorts to 1959','Portrait & Social Shorts 1960–1979','Portrait & Social Shorts 1980–1999','Portrait & Social Shorts 2000–2014','Portrait & Social Shorts since 2015','Sport Shorts'],
 'new_leaves':[
  {'key':'NEW1','label':'Political Documentary Short','breadth':'Short militant, activist and social-issue documentaries.',
   'defn':'A documentary short made to argue, mobilise or bear witness on a political or social cause — militant and revolutionary newsreels, anticolonial and activist films, war and social-issue reportage (Misère au Borinage, Afrique 50, Now, Hanoi Tuesday 13th, The White Helmets).',
   'aliases':'militant film; activist documentary short; social-issue documentary short','src':src('https://en.wikipedia.org/wiki/Political_cinema'),
   'axis':'by era: interwar and postwar militant film, the 1960s revolutionary and Third Cinema shorts, the 1970s collectives, then later activism','secs':['Militant Shorts to 1959','Revolutionary & Third Cinema Shorts 1960–1969','Activist & Collective Shorts 1970–1979','Activist & Issue Shorts 1980–2009','Activist & Issue Shorts since 2010']},
  {'key':'NEW2','label':'Poetic Documentary Short','breadth':'Short documentaries organised by rhythm, image and mood rather than argument: city symphonies and lyrical studies of place and labour.',
   'defn':'A documentary short shaped by visual rhythm, montage and mood instead of exposition — city symphonies, lyrical studies of landscape, seasons and work (Manhatta, Rain, À propos de Nice, Islands of Fire, Beginning).',
   'aliases':'city symphony short; lyrical documentary','src':src('https://en.wikipedia.org/wiki/Poetic_documentary'),
   'axis':'city symphonies first, then poetic documentary by era','secs':['City Symphonies & Street Films','Poetic Documentary to 1969','Poetic Documentary 1970–1999','Poetic Documentary since 2000']},
  {'key':'NEW3','label':'Essay Film Short','breadth':'Short first-person and reflective nonfiction films that think through images, memory and history.',
   'defn':'A nonfiction short that reflects in a personal, argumentative voice, working through memory, history and images themselves (Night and Fog, The House Is Black, Reassemblage, Isle of Flowers, History and Memory).',
   'aliases':'short essay film; video essay; film essay','src':src('https://en.wikipedia.org/wiki/Essay_film'),
   'axis':'by era','secs':['Essay Shorts to 1979','Essay Shorts 1980–1999','Essay Shorts 2000–2014','Essay Shorts 2015–2019','Essay Shorts since 2020']},
  {'key':'NEW4','label':'Arts Documentary Short','breadth':'Short documentaries about artists, writers, filmmakers, musicians and dancers and their work.',
   'defn':'A documentary short whose subject is an art, an artist or a performance — painting and sculpture, writers, cinema and filmmakers, music and dance (Henri Matisse, Guernica, Jazz Dance, Werner Herzog Eats His Shoe, Kazuo Ohno).',
   'aliases':'art documentary short; music documentary short; dance documentary','src':src('https://en.wikipedia.org/wiki/Art_film_(documentary)'),
   'axis':'by art form','secs':['Art & Artists','Writers & Poets','Cinema & Filmmakers','Music & Musicians','Dance & Performance']},
  {'key':'NEW5','label':'Ethnographic Short','breadth':'Short fieldwork and ethnographic documentaries of ritual, craft and community life.',
   'defn':'A documentary short recording the ritual, craft or daily life of a community as ethnographic fieldwork (Trance and Dance in Bali, Les Maîtres fous, The Ax Fight, Gestes du repas).',
   'aliases':'ethnographic documentary short; visual anthropology short','src':src('https://en.wikipedia.org/wiki/Ethnographic_film'),
   'axis':'by era of fieldwork','secs':['Early Fieldwork Films (to 1949)','Ethnographic Shorts 1950–1979','Ethnographic Shorts since 1980']}],
 'assign':{},'moves':[]}
for r in R:
    k=cls(r); out['assign'][r['id']]=[k,sec(r,k)]
c=collections.Counter(v[0] for v in out['assign'].values()); print(c)
print(collections.Counter(tuple(v) for v in out['assign'].values()))
json.dump(out,open('o_A21-12.json','w'),ensure_ascii=False,indent=1)
