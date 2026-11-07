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
