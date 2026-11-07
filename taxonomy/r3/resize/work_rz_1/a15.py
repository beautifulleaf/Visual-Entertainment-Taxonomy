from common import *
import collections
R=rows('A21-15')
def has(w,*names): return any(n.lower() in w.lower() for n in names)
LAND_DIR=['Hutton','Lapore','Gehr','Patiño','Szlam','Barley','Ben Rivers','Lertxundi','Bonnetta','Kooij','Drummond','Wittmann','Mazzolo','Rodríguez Dávila','Julie Murray','McIntyre','Simon Liu','Maya Connors','Fanderl','Emily Richardson','Fenz','Stauffacher','Shirley Clarke','Anthony Stern','Rudy Burckhardt','Helena Wittmann','Jeanne Liotta','Toby Tatum','Greg Marshall','Nour Ouayda','Azul Aizenberg','Laura Sanz','Daniela Zahlner','Meinhard Rauchensteiner','Olivier Perriquet','Mare Šuljak','David Osthoff','Jen Martin','Flo Mavy','Allison Janae Hamilton','Racquel Rowe','Shambhavi Kaul','Charles Yi Yong Lim','Renate Sami','Yang Fudong','Delgado','Los Ingrávidos','Alejandro Alonso','Leighton Pierce','Naomi Uman','Tsai Ming-liang','Mark Lapore','Sky Hopinka','Ephraim Asili','Beatriz Santiago','Dane Komljen','Abinadi Meza','Ayo Tsalithaba','Paola Buontempo','Carmen Rojas','Maite Abella','Demelza','Yto Barrada','Terence Davies','Ester Ivakič','Lucila Mariani','Daniel Nehm','Burak Cevik','Hogan Seidel','Ernie Gehr']
LAND_TITLE=['Sausalito','Bridges-Go-Round','The Wonder Ring','Castro Street','San Francisco','Valentin de las Sierras','Aimless Walk','Walking from Munich','Unconscious London Strata','Warrah','L\'Eau de la Seine','A Journey to Avebury','Dancers, Buildings','Desert','Star Garden','The Domain of the Moment','Aerial','Place of Work','Where I Am is Here','Ruskin','Wild Night in El Reno','Notes of an Early Fall','Customs and Immigration','Aguaespejo','Fire in Castilla','Acarino','Variaciones sobre una Granada','Boulder Blues','The Mammals of Victoria','Black Ice','Kindering','Mutable Fire','Herbst','Night Without Distance','The Sower of Stars','Wolves from Above','Vertical Air','Gletscher','Ein Jahr','American Colour','Kalendar','The Futurist','Coyote','Winds of Chanduy','Things','Tartarughe']
LYR_KEEP=['Dorsky','Hiler','Beavers','Aurand','Schüpbach','Mekas','Gibbons','Hammer','Gunvor Nelson','Chick Strand','Brakhage','Weerasethakul','Makino','Saito','Dinçel','Menken','Tait','Robertson','Friedrich','Schneemann','Markopoulos','Baillie','Hirsch','Caldini','Sonbert','Herwitz','Lowder','Hurtado','Rousseau','Grandrieux','Sogo','Ben Russell','Philip S. Solomon']
STRUCT_LAND=['Fog Line','Wind Vane','River Yar','Canadian Pacific','Les Tournesols','Voiliers','A Year Along the Abandoned Road','Market Street','Sound of a Million Insects','Ten Mornings','Ash 01','Two Moons','At the Horizon','Eventide','Atlantic35','Horizōn','2\'45"']
EXPANDED=[]
def cls(r):
    s,w,t,y=r['sec'],r['who'],r['title'],r['y']
    if s=='':
        if has(w,'Deren','Anger'): return 'self'
        if has(w,'Frampton'): return 'NEW3'
        if has(w,'Potter'): return 'NEW4'
        return 'NEW1'
    if s=='1': return 'self'
    if s=='2':
        if 'Aimless Walk' in t: return 'NEW2'
        return 'self'
    if s=='3':
        if t in ('Little Stabs at Happiness','Scotch Tape','Christmas on Earth'): return 'self'
        if any(x in t for x in LAND_TITLE): return 'NEW2'
        if has(w,*LYR_KEEP): return 'NEW1'
        if has(w,*LAND_DIR): return 'NEW2'
        if y>=2000: return 'NEW2'
        return 'NEW1'
    if s=='4':
        if any(t.startswith(x) for x in STRUCT_LAND): return 'NEW2'
        return 'NEW3'
    if s=='5': return 'NEW4'
    if s=='6': return 'NEW5'
A={}
for r in R: A[r['n']]=cls(r)
print(collections.Counter(A.values()))
import sys
if len(sys.argv)>1:
  for r in R:
    if A[r['n']]==sys.argv[1]: print(r['n'],r['sec'],r['y'],r['title'],'|',r['who'])

def cls2(r):
    s,w,t,y=r['sec'],r['who'],r['title'],r['y']
    k=cls(r)
    if s=='3' and w.strip() in ('','US'): k='NEW1'
    if t in ('The Anthem','A Letter to Uncle Boonmee'): k='NEW5'
    if s=='3' and 'Makino' in w: k='NEW3'
    if t=="L'Arrière-saison": k='NEW2'
    if 'Potter' in w: k='self'
    return k
BRAK=lambda r: 'Brakhage' in r['who'] or (r['sec'] in ('','3') and r['who'].strip() in ('','US'))
CITY=['Sausalito','Aimless Walk','Walking from Munich','Bridges-Go-Round','Castro Street','San Francisco','New York Portrait','L\'Eau de la Seine','Dancers, Buildings','Essex Street','Waterfront Follies','Carroll Gardens','Kolkata','Happy Valley','Site Watch','Customs and Immigration','The Futurist','Market Street','Canadian Pacific','Number One','A Depression in the Bay','Fluid Frontiers','East']
AUS=['Kubelka','Kren','Marc Adrian','Ernst Schmidt','Bauer']
BRIT=['le Grice','Gidal','Raban','Welsby','Crosswaite','Eatherley','Lis Rhodes','David Hall','John Smith','Greenaway','Sherwin','Tony Hill','Hein','Kirchhofer','Martedi','Bargellini','Lowder','Karel Doing','Akerman','Dwoskin','Iványi','Skallerud','Urlus','Schwaba','Kohlberger','Viktoria Schmid','Canapa']
def sec(r,k):
    s,w,t,y=r['sec'],r['who'],r['title'],r['y']
    if k=='self':
        if s=='1': return 1
        if y<=1939: return 2
        if y<=1959: return 3
        if y<=1979: return 4
        return 5
    if k=='NEW1':
        if BRAK(r): return 2
        if y<=1959: return 1
        if y<=1979: return 3
        if y<=1999: return 4
        return 5
    if k=='NEW2':
        if any(t.startswith(x) for x in CITY): return 1
        if s=='4': return 2
        if y<=1999: return 3
        if y<=2015: return 4
        return 5
    if k=='NEW3':
        if 'Owen Land' in w or 'Titz' in w: return 5
        if 'Warhol' in w or t.startswith('Two: Creeley'): return 2
        if any(x in w for x in AUS) and y<1985: return 1
        if y>=1985: return 6
        if any(x in w for x in BRIT): return 4
        return 3
    if k=='NEW4':
        if y<=1959: return 1
        if y<=1979: return 2
        if y<=1999: return 3
        if y<=2014: return 4
        return 5
    if k=='NEW5':
        if y<=1979: return 1
        if y<=1999: return 2
        if y<=2012: return 3
        return 4
out={'label':'Avant-Garde Short',
 'defn':'A short of the first and postwar avant-garde built on dream, ritual, rhythm or the plastic image rather than story: Dada and cinéma pur, surrealist, trance and psychodrama, mythopoeic and underground films (Ballet Mécanique, Un Chien andalou, Meshes of the Afternoon, Scorpio Rising). Lyrical, landscape, structural, found-footage and video works have their own leaves.',
 'axis':'by avant-garde movement in historical order: Dada and cinéma pur, surrealism, the trance film, the mythopoeic and underground film, then later dream shorts',
 'secs':['Dada & Cinéma Pur','Surrealist Film','Trance Film & Psychodrama','Mythopoeic & Underground Film','Later Surrealist & Dream Shorts'],
 'new_leaves':[
  {'key':'NEW1','label':'Lyrical Film','breadth':'Personal, first-person avant-garde shorts in the Brakhage line: the camera as the maker\'s eye, body and memory.',
   'defn':'An avant-garde short in which the camera renders the filmmaker\'s own seeing, body, household or devotion, with handheld, rhythmic or painted imagery and no story (Anticipation of the Night, Window Water Baby Moving, Fuses, Notebook, Pneuma). A film observing a place goes to Landscape Film.',
   'aliases':'film-poem; personal film; first-person film','src':[['https://en.wikipedia.org/wiki/Experimental_film','Wikipedia']],
   'axis':'by era, with Stan Brakhage\'s large body of work as its own section','secs':['Early Lyric & Film-Poems (to 1959)','The Films of Stan Brakhage','Lyrical Film 1960–1979','Lyrical Film 1980–1999','Lyrical Film since 2000']},
  {'key':'NEW2','label':'Landscape Film','breadth':'Avant-garde shorts devoted to place: cities, land, water, weather and light observed through the camera.',
   'defn':'An avant-garde short whose subject is a place — a city, a stretch of land or water, the weather or light over time — observed rather than narrated (Fog Line, New York Portrait, Study of a River, Altiplano, Night Without Distance).',
   'aliases':'landscape cinema; experimental landscape film','src':[['https://www.jstor.org/stable/10.13110/discourse.42.1-2.0173','Discourse (JSTOR)']],
   'axis':'by kind of place and method: city films, structural and durational landscapes, then land, water and light by era','secs':['City Films & Street Portraits','Structural & Durational Landscapes','Land, Water & Light to 1999','Land, Water & Light 2000–2015','Land, Water & Light since 2016']},
  {'key':'NEW3','label':'Structural Film','breadth':'Avant-garde shorts whose shape is set by a predetermined system or by the film material itself.',
   'defn':'An avant-garde short whose form is a predetermined structure or an exposure of the film material and apparatus — fixed frame, flicker, loop printing, rephotography, metric montage (Arnulf Rainer, The Flicker, Serene Velocity, Zorns Lemma, Berlin Horse).',
   'aliases':'structural-materialist film; metric film; flicker film','src':[['https://en.wikipedia.org/wiki/Structural_film','Wikipedia']],
   'axis':'by school: Austrian formal film, Warhol, American structural film, British and European structural-materialist film, Owen Land\'s parodies, then contemporary analog work','secs':['Austrian Formal Film','Warhol Screen Tests & Durational Films','American Structural Film','British & European Structural-Materialist Film','Owen Land & Structural Parody','Contemporary Structural & Analog Film (1985–)']},
  {'key':'NEW4','label':'Found-Footage Film','breadth':'Avant-garde shorts made by re-editing, reprinting or manipulating footage shot by others.',
   'defn':'An avant-garde short assembled from appropriated footage — newsreels, Hollywood films, home movies, archives — re-edited, optically reprinted or physically altered (Rose Hobart, A Movie, Free Fall, Passage à l\'acte, Outer Space).',
   'aliases':'collage film; appropriation film; compilation (avant-garde)','src':[['https://en.wikipedia.org/wiki/Found_footage_(appropriation)','Wikipedia']],
   'axis':'by era','secs':['Cornell & Early Collage (to 1959)','Collage Film 1960–1979','Found Footage 1980–1999','Found Footage 2000–2014','Found Footage since 2015']},
  {'key':'NEW5','label':'Video Art & Expanded Cinema','breadth':'Artists\' video, gallery moving-image works and expanded-cinema pieces.',
   'defn':'A short moving-image artwork made on video or for the gallery, or an expanded-cinema piece that works with projection, performance or installation (Vertical Roll, Global Groove, Line Describing a Cone, Semiotics of the Kitchen, How Not to Be Seen).',
   'aliases':'artists\' video; artists\' moving image; gallery film','src':[['https://en.wikipedia.org/wiki/Video_art','Wikipedia']],
   'axis':'by era','secs':['Early Video & Expanded Cinema (to 1979)','Video Art of the 1980s–90s','Gallery Moving Image 2000–2012','Contemporary Moving-Image Art (2013–)']}],
 'assign':{}, 'moves':[]}
for r in R:
    k=cls2(r); out['assign'][r['id']]=[k,sec(r,k)]
import collections
print(collections.Counter(tuple(v) for v in out['assign'].values()))
json.dump(out,open('o_A21-15.json','w'),ensure_ascii=False,indent=1)
