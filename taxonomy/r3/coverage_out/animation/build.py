"""Build coverage outputs for part `animation` (family C). Run: python3 build.py"""
import csv, json, os, collections
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(D, "..", "..", "..", "..")
csv.field_size_limit(10**9)
placed = {r["id"]: r for r in csv.DictReader(open(f"{R}/taxonomy/r3/ft_title_index.tsv"), delimiter="\t")}
AC = {r["mal_id"]: r for r in csv.DictReader(open(f"{R}/data/interim/anime_candidates.csv")) if r["mal_id"]}
FR = {r["tconst"]: r for r in csv.DictReader(open(f"{R}/data/interim/film_ratings.csv"))}
FC = {r["tconst"]: r for r in csv.DictReader(open(f"{R}/data/interim/film_candidates.csv"))}
TS = {}
for r in csv.DictReader(open(f"{R}/taxonomy/r3/tspdt/entries.csv")):
    if r["tconst"] and r["tconst"] not in TS: TS[r["tconst"]] = r

W = "https://en.wikipedia.org/wiki/"
NEW = [
 dict(key="NEW1", sub="C12", label="Animated Documentary", breadth="genre",
      defn="A non-fiction film told wholly or chiefly through animation: reconstructed memory, testimony or reportage drawn, painted or modelled instead of filmed (<i>Waltz with Bashir</i>, <i>Flee</i>, <i>Ryan</i>, <i>The Sinking of the Lusitania</i>). Live-action documentaries with animated inserts stay in A19.",
      aliases="animadoc; animated non-fiction", see="A19", src=[[W+"Animated_documentary", "Wikipedia"]]),
 dict(key="NEW2", sub="C7", label="Spokon (Sports-Guts Anime)", breadth="cycle",
      defn="The Shōwa-era <i>supōtsu konjō</i> ('sports guts') cycle launched by Ikki Kajiwara's <i>Kyojin no Hoshi</i>: a sports series of brutal training, self-sacrifice and fighting spirit, chiefly 1968–1980s (<i>Kyojin no Hoshi</i>, <i>Attack No.1</i>, <i>Ashita no Joe</i>, <i>Ace wo Nerae!</i>, <i>Tiger Mask</i>). Later sports anime go to their sport (C7).",
      aliases="supokon; sports konjō", see="C7-1; C7-6", src=[["https://www.wikidata.org/wiki/Q2281511", "Wikidata"], ["https://it.wikipedia.org/wiki/Spokon", "Wikipedia (it)"], [W+"Sports_anime_and_manga", "Wikipedia"]]),
 dict(key="NEW3", sub="C10", label="Gender-Bender Anime", breadth="genre",
      defn="A comedy or romance whose engine is a character's change or concealment of sex: magical sex change and body transformation, or crossdressing (josō) passing (<i>Ranma ½</i>, <i>Stop!! Hibari-kun!</i>, <i>Kämpfer</i>, <i>Princess Princess</i>, <i>Oniichan wa Oshimai!</i>). Serious drama of gender identity goes to C8-7; body-swap romance to C5.",
      aliases="seitenkan; josō; MAL 'Crossdressing', 'Magical Sex Shift'", see="C10-8; C8-7", axis="device", secs=["Sex-Change & Transformation Comedies", "Crossdressing (Josō) Comedies"],
      src=[[W+"Gender_bender", "Wikipedia"], ["https://myanimelist.net/anime/genre/81/Magical_Sex_Shift", "MyAnimeList"], ["https://myanimelist.net/anime/genre/44/Crossdressing", "MyAnimeList"]]),
 dict(key="NEW4", sub="C14", label="Soviet Animation", breadth="national tradition",
      defn="The state-studio animation of the USSR, above all Soyuzmultfilm (Moscow) with Kievnauchfilm, Uzbekfilm and Ekran: fairy-tale features and shorts, satirical and modernist art shorts and the children's classics of its 'Golden Collection' (<i>The Snow Queen</i>, <i>Film, Film, Film</i>, <i>Winnie-the-Pooh</i>, <i>Hedgehog in the Fog</i>, <i>Three from Prostokvashino</i>). Soviet TV serials go to C13-14; Estonian and post-Soviet auteur shorts to C14-5.",
      aliases="Soyuzmultfilm; multfilm", see="C13-14; C14-5", axis="era",
      secs=["Socialist-Realist Fairy Tales (1936–1960)", "The Aesthetic Switch (1961–1968)", "Golden Collection Classics (1969–1991)"],
      src=[[W+"History_of_Russian_animation", "Wikipedia"], [W+"Soyuzmultfilm", "Wikipedia"]]),
]
NEW_SECTIONS = [("C12-2", "Fleischer Studios Features (1939–1941)"), ("C12-18", "Italian Auteur Animation"),
                ("C12-18", "East Asian Independent Animation"), ("C14-6", "Japanese Puppet Animation (Kawamoto Kihachirō)")]

# moves: id, to, sec, note
MOVES = [
 ("tt1185616","NEW1","","animated documentary, was in CG family film"), ("tt8430054","NEW1","",""),
 ("tt11242654","NEW1","","animated music documentary"), ("tt31064841","NEW1","","Lego-animated documentary"),
 ("tt0009620","NEW1","","first animated documentary (McCay)"),
 ("1550","NEW2","",""), ("311","NEW2","",""), ("3009","NEW2","",""), ("19973","NEW2","",""), ("2402","NEW2","",""), ("2921","NEW2","",""),
] + [(i,"NEW3",1,"magical sex change") for i in ["210","418","792","1007","1010","1008","1011","59145","60564","63801","6205","10076","24705","51678","36902"]] \
  + [(i,"NEW3",2,"crossdressing") for i in ["3332","907","10110","1569","22835","5030","9712"]] \
  + [("tt0073099","NEW4",3,"Norstein"), ("tt0079986","NEW4",3,"Norstein"), ("tt0241399","NEW4",3,"Kovalyov, Pilot studio 1990")] \
  + [("1497","C8-10",1,"Tezuka/Mushi Pro experimental"), ("3038","C8-10",1,"Animerama"), ("2755","C8-10",1,"Animerama"), ("601","C8-10",3,"art anime, was ghost story")]

A = []  # (id, kind, to, sec, note)
def F(to, sec, *ids, note=""):
    for i in ids: A.append((i, "film", to, sec, note))
def AN(to, sec, *ids, note=""):
    for i in ids: A.append((i, "anime", to, sec, note))
# NEW1 animated documentary
F("NEW1", "", "tt2967856","tt0905979","tt1817287","tt0414469","tt1996223","tt1621766","tt5236900","tt3946020")
# NEW2 spokon
AN("NEW2", "", "5834","15875","9916","2316","3825","2920","2922","313","314","312","5832","3870","9163")
# NEW3
AN("NEW3", 2, "9988")
# NEW4 Soviet
F("NEW4", 1, "tt0050604","tt2487736","tt5437470","tt0949326","tt0145799","tt2266785","tt0218798","tt0050987","tt0211470","tt0152066")
F("NEW4", 2, "tt2474800","tt0238938","tt0219119","tt0188580","tt3335068","tt1332537","tt0213309","tt0393932","tt0756316","tt0212943","tt0480465","tt0218563","tt3454556")
F("NEW4", 3, "tt0211729","tt0211730","tt0208558","tt0211281","tt0251333","tt0146970","tt0201520","tt0487562","tt3336054","tt0218931","tt0218696",
  "tt0209074","tt0165844","tt1230144","tt0066813","tt0437300","tt0071608","tt0218493","tt0928068","tt0217590","tt0188895","tt0201920","tt1074974",
  "tt0239096","tt0212969","tt1179072","tt0820136","tt0189160","tt1315584","tt1318414","tt0803764","tt0210804","tt0189195","tt0218534","tt0211653",
  "tt0216434","tt0155858","tt1352408","tt1288381","tt0219233","tt0142851","tt0882997","tt0487132","tt5517442","tt0982856","tt1259770","tt0098259",
  "tt0259499","tt0122227","tt0097118","tt0210974","tt2443150")
# C14-1 Golden Age (resectioned below): 1 silent, 2 Disney, 3 Fleischer, 4 Warner, 5 MGM, 6 UPA, 7 late/independent
F("C14-1", 1, "tt0000003","tt0000015","tt0131024","tt0002260","tt0141008","tt0012123","tt0017871")
F("C14-1", 2, "tt0019278","tt0020053","tt0026094","tt0027100","tt0028726","tt0029943","tt0032071","tt0033460","tt0035794","tt0038174","tt0046442")
F("C14-1", 3, "tt0141869","tt0021664","tt0023227","tt0025071","tt0029415","tt0031025","tt0034247","tt0033888")
F("C14-1", 4, "tt0031202","tt0034305","tt0034368","tt0034675","tt0034845","tt0035743","tt0035754","tt0036441","tt0036896","tt0037659","tt0037753",
  "tt0038317","tt0038373","tt0038586","tt0038588","tt0038671","tt0038576","tt0038880","tt0041349","tt0041462","tt0041598","tt0042418","tt0042928",
  "tt0043405","tt0043953","tt0044404","tt0044609","tt0045062","tt0045585","tt0045709","tt0046771","tt0048544","tt0050194","tt0051078","tt0053815")
F("C14-1", 5, "tt0031790","tt0032033","tt0034524","tt0035832","tt0036295","tt0036535","tt0036547","tt0037090","tt0037251","tt0038087","tt0038143",
  "tt0038702","tt0038786","tt0039251","tt0039535","tt0040218","tt0040611","tt0041146","tt0041593","tt0041858","tt0042032","tt0044095","tt0046393",
  "tt0046778","tt0046930","tt0047981","tt0048292")
F("C14-1", 6, "tt0043980","tt0153448")
F("C14-1", 4, "tt0053909"); F("C14-1", 7, "tt0053080")
# C14-4 abstract
F("C14-4", "", "tt0012620","tt0014407","tt0015384","tt0019498","tt0026226","tt0026580","tt0028156","tt0029686","tt0029350","tt0043296","tt0056060",
  "tt0380493","tt0067813","tt2363502")
# C14-5 auteur shorts: 1 NFB 2 Zagreb&Central 3 Soviet/Russian/Estonian 4 American indep 5 Western European 6 LatAm/Afr/Asian
F("C14-5", 1, "tt0075273","tt0079126","tt0206312","tt0088805","tt0094847","tt0200282","tt0933357","tt0063417","tt0055594","tt0134127","tt0075047",
  "tt0071636","tt0415853","tt0082209")
F("C14-5", 2, "tt0257098","tt0084764","tt0367944","tt0058246","tt0051544","tt0848381","tt0057450","tt0052585","tt0081040","tt0073715","tt0475949",
  "tt1814743","tt0440846","tt9347268","tt0114269","tt0054186","tt3044174","tt11386280")
F("C14-5", 3, "tt0219977","tt0452324","tt0452346","tt0207639","tt0475730","tt0222743","tt3965660")
F("C14-5", 4, "tt0440972","tt1282053","tt12837488","tt0141455","tt0352875","tt0305934")
F("C14-5", 5, "tt0096880","tt0091152","tt0088725","tt0108494","tt0106446","tt0102392","tt1720261","tt0498121","tt11884670","tt0321750","tt14293560",
  "tt0099696","tt0073068","tt0145834","tt0286736","tt0024721","tt0057361","tt0127710")
F("C14-5", 6, "tt0133191","tt1331015","tt0355439","tt1330999")
# C14-6 stop-motion shorts
F("C14-6", 1, "tt0013014","tt0145955","tt0047103","tt0025477")
F("C14-6", 2, "tt0065101","tt0068844","tt0169912","tt0099386")
F("C14-6", 4, "tt0092020","tt0095968","tt0266643","tt2372335","tt6531506","tt10499942","tt7925798","tt0211319","tt0125812")
AN("C14-6", "Japanese Puppet Animation (Kawamoto Kihachirō)", "6680","7171")
# C12 features
F("C12-2", "Fleischer Studios Features (1939–1941)", "tt0031397","tt0033727")
F("C12-2", 1, "tt0057093","tt0076416","tt0076593","tt0086489","tt0078915","tt0083701")
F("C12-2", 2, "tt0107875"); F("C12-2", 3, "tt0114108","tt0108395"); F("C12-2", 4, "tt0107745","tt0103783")
F("C12-6", "", "tt0386741")
F("C12-7", 2, "tt0131636","tt0082892","tt0091889","tt0122735"); F("C12-7", 5, "tt0259534","tt0488836")
F("C12-8", "", "tt0064806","tt0034091","tt0041890")
F("C12-9", 2, "tt0350194"); F("C12-9", 4, "tt0080461"); F("C12-9", 5, "tt1543920")
F("C12-11", 5, "tt0387658","tt0093066")
F("C12-14", 1, "tt6035092","tt0262264")
F("C12-14", 2, "tt4644382","tt9288776","tt11177804","tt19757204","tt13269670","tt27922374","tt16345484","tt30836045","tt6451304")
F("C12-16", 1, "tt0021309","tt0227528","tt0240034"); F("C12-16", 5, "tt0061931")
F("C12-16", 6, "tt0108069","tt1352765","tt10695672","tt0208298")
AN("C12-16", "", "7510")
F("C12-17", "", "tt1374985","tt5584796")
F("C12-18", 1, "tt1891769","tt5894778","tt0087376","tt0262333","tt9320184","tt6342440","tt6785292","tt9719864","tt1856057","tt1355638","tt2077908")
F("C12-18", 2, "tt5674658")
F("C12-18", 3, "tt0176694","tt0121431","tt0847478","tt8387918","tt6435164","tt0268282","tt0333215","tt1395059")
F("C12-18", 4, "tt1407052","tt7336470","tt1947964")
F("C12-18", 5, "tt1172203","tt0105654","tt0365296","tt1013607","tt2361846","tt2253947","tt5538568","tt0843358","tt4181270","tt0220450")
F("C12-18", "Italian Auteur Animation", "tt0074121","tt0144681","tt2990836")
F("C12-18", "East Asian Independent Animation", "tt2086830","tt3091272","tt2164058","tt0419954","tt0312941","tt7543904")
F("C14-7", 2, "tt0391404","tt0084701","tt0086590","tt0135636","tt0083951")
F("C2-16", "", "tt0328832"); F("C6-5", 1, "tt0368667")
# anime: C8-10 art anime, C11-5 early, C1-8, OVA-boom extras
AN("C8-10", 1, "1982","1984","2047","1989","3472")
AN("C8-10", 2, "2211","2550","3475","1370","16149")
AN("C8-10", 3, "2033")
AN("C11-5", 2, "30176","3990","28245"); AN("C11-5", 3, "7528","4481","7610","3905")
AN("C1-8", 1, "1343")
AN("C2-6", 1, "2060","2061","2062"); AN("C2-1", 1, "1832","498"); AN("C2-2", 4, "3061")

# extra add without id (canonical, not in pools)
NOID = [("", "Princess Iron Fan", "1941", "Wan Laiming; Wan Guchan", "film", "C12-14", 1, "first Chinese animated feature; no sure tconst")]

RESECT = {
 "C14-1": {"axis": "studio of the Golden Age of American animation", "secs": ["Silent-Era Pioneers (1892–1927)", "Walt Disney Studio & Silly Symphonies", "Fleischer Studios", "Warner Bros. (Looney Tunes & Merrie Melodies)", "MGM Cartoon Studio (Avery, Hanna & Barbera)", "UPA & Postwar Modernism", "Independent & Late Theatrical Shorts"],
   "assign": {"tt0000682":1,"tt0001737":1,"tt0004008":1,"tt0019422":2,"tt0136320":3,"tt0020414":2,"tt0022899":2,"tt0024578":3,"tt0024660":2,"tt0028119":3,
              "tt0029161":2,"tt0029339":2,"tt0030604":4,"tt0190806":2,"tt0051850":2,"tt0042871":4,"tt0043581":6,"tt0044868":5,"tt0045261":2,"tt0045708":4,
              "tt0046408":6,"tt0048449":4,"tt0051189":4,"tt0272170":7,"tt0063437":7,"tt0085936":2}},
 "C8-10": {"axis": "school & era", "secs": ["Mushi Production Experiments & Animerama (1962–1973)", "Independent & Festival Shorts", "Auteur Features & Series"],
   "assign": {"3220":1,"1497":1,"3038":1,"2755":1,"31259":2,"1072":2,"2832":2,"3326":2,"5365":2,"10448":2,"44059":2,"885":3,"2210":3,"875":3,"6774":3,"601":3}},
 "C11-5": {"axis": "era", "secs": ["Meiji–Taishō Pioneers (1907–1926)", "Early Shōwa & Wartime Animation (1927–1945)", "Postwar to Early Tōei Dōga (1946–1963)"],
   "assign": {**{i:1 for i in ["33187","17387","18457","23189","6654","7485","7494"]},
              **{i:2 for i in ["5632","5873","5875","4391","5631","5826","6769","4390","4393","4398","5813","5868","5661","6823","6838","6857","2765"]},
              **{i:3 for i in ["5662","12603","11447","6993","6994"]}}},
 "C12-14": {"axis": "era", "secs": ["Shanghai Animation Film Studio Classics (1941–1999)", "Contemporary Chinese Animation (2015–)"],
   "assign": {"tt0059855":1,"tt0354770":1,"tt1920885":2,"tt10627720":2,"tt10734928":2,"tt15000314":2,"tt25434854":2,"tt34956443":2}},
 "C1-8": {"axis": "era", "secs": ["OVA-Boom Seinen Action (1985–1995)", "Television & Streaming-Era Seinen Action (2000–)"],
   "assign": {**{i:1 for i in ["1341","1107","1342","1468","6016"]}}},
}

def main():
    # C1-8 rest -> sec 2
    for r in placed.values():
        if r["leaf"] == "C1-8" and r["id"] not in RESECT["C1-8"]["assign"]: RESECT["C1-8"]["assign"][r["id"]] = 2
    for lf, rs in RESECT.items():
        have = {r["id"] for r in placed.values() if r["leaf"] == lf} - {m[0] for m in MOVES}
        miss = have - set(rs["assign"]); assert not miss, (lf, miss)
    for m in MOVES:
        if m[1] in RESECT: RESECT[m[1]]["assign"][m[0]] = m[2]
    for a in A:
        if a[2] in RESECT: RESECT[a[2]]["assign"][a[0]] = a[3]
    seen = collections.Counter([m[0] for m in MOVES] + [a[0] for a in A])
    assert not [k for k, v in seen.items() if v > 1], [k for k, v in seen.items() if v > 1]
    rows = []
    for i, kind, to, sec, note in A:
        assert i not in placed, (i, placed.get(i))
        if kind == "anime":
            r = AC[i]; rows.append([i, r["title"], r["year"], "JP", "anime", to, sec, note])
        else:
            t = TS.get(i); f = FR.get(i, {}); c = FC.get(i, {})
            title = c.get("title") or f.get("mdblist_title") or (t or {}).get("title")
            year = c.get("year") or f.get("year") or (t or {}).get("year")
            who = ((t or {}).get("director") or f.get("country") or "").replace(",", ";")
            assert title and year, i
            rows.append([i, title, year, who, "film", to, sec, note])
    for r in NOID: rows.append(list(r))
    with open(f"{D}/adds.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["id","title","year","who","kind","to","sec","note"]); w.writerows(rows)
    with open(f"{D}/moves.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["id","to","sec","note"]); w.writerows(MOVES)
    with open(f"{D}/new_sections.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["leaf","label"]); w.writerows(NEW_SECTIONS)
    json.dump(NEW, open(f"{D}/new_leaves.json", "w"), ensure_ascii=False, indent=1)
    json.dump(RESECT, open(f"{D}/resections.json", "w"), ensure_ascii=False, indent=1)
    print(len(rows), "adds,", len(MOVES), "moves")
main()
