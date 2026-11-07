FIX={"Archizoom":"Archizoom_Associati","AEG":"AEG_(German_company)","David_Carson":"David_Carson_(graphic_designer)","Fritz_Hansen":"Fritz_Hansen_(company)","Josef_Frank":"Josef_Frank_(architect)","Ron_Arad":"Ron_Arad_(industrial_designer)","Tom_Dixon":"Tom_Dixon_(industrial_designer)","William_Golden":"William_Golden_(graphic_designer)","Colin_Forbes":"Colin_Forbes_(graphic_designer)","Alessi_(company)":"Alessi_(Italian_company)","Arco_lamp":"Achille_Castiglioni","Ball_Clock":"George_Nelson_(designer)","Bauhausb%C3%BCcher":"L%C3%A1szl%C3%B3_Moholy-Nagy",
"Braun_SK_4":"Dieter_Rams","British_Rail_corporate_identity":"Design_Research_Unit","Butterfly_stool":"Sori_Yanagi","Chair_No._14":"Thonet",
"David_Rowland_(designer)":"David_Rowland_(industrial_designer)","Droog_(design_firm)":"Droog_(company)","Fiat_500_(1957)":"Fiat_500",
"Flos_(company)":"Flos","Gispen_(company)":"Willem_Hendrik_Gispen","J._%26_J._Kohn":"Jacob_%26_Josef_Kohn","Lockheed_Lounge":"Marc_Newson",
"Nippon_Design_Center":"Yusaku_Kamekura","Poltronova":"Archizoom","Purkersdorf_Sanatorium":"Sanatorium_Purkersdorf","Series_7_chair":"Arne_Jacobsen",
"Ulm_stool":"Max_Bill","Wishbone_Chair":"Wishbone_chair","Womb_chair":"Eero_Saarinen","Total_Design":"Wim_Crouwel","Gruppo_Strum":"Gufram",
"Peter_Keler":"Bauhaus","Tejo_Remy":"Droog_(company)","Jurgen_Bey":"Droog_(company)","Bertjan_Pot":"Moooi","Fulvio_Bianconi":"Venini",
"Ingeborg_Lundin":"Orrefors","Dietrich_Lubs":"Braun_(company)","Gionatan_De_Pas":None,"Jack_Pritchard":"Isokon","Olof_B%C3%A4ckstr%C3%B6m":"Fiskars","Olof_Bäckström":"Fiskars",
"Alessandro_Guerriero":"Studio_Alchimia","Ben_Bos":"Wim_Crouwel","Carl_Jakob_Jucker":"Wilhelm_Wagenfeld","Cristiano_Toraldo_di_Francia":"Superstudio",
"Erwin_Braun":"Braun_(company)","Inge_Aicher-Scholl":"Ulm_School_of_Design","Walter_Zeischegg":"Ulm_School_of_Design","Maria_Likarz":"Wiener_Werkst%C3%A4tte",
"Masanori_Umeda":"Memphis_Group","Massimo_Morozzi":"Archizoom","Paolo_Deganello":"Archizoom","Paul_Davis_(illustrator)":"Push_Pin_Studios",
"R._D._E._Oxenaar":"Ootje_Oxenaar","Ralph_Eckerstrom":"Unimark_International","Rody_Graumans":"Droog_(company)","Siegfried_Odermatt":"Rosmarie_Tissi",
"Gert_Dumbar":"Studio_Dumbar","Friso_Kramer":None,"Giancarlo_Piretti":None,"Herbert_Krenchel":None,"Erik_Magnussen_(designer)":None,
"OXO_(kitchen_utensil_brand)":None,"Peter_Murdoch_(designer)":None,"Paolo_Rizzatto":None,"Ryuichi_Yamashiro":None}
ALT={"Blow chair (De Pas, D'Urbino, Lomazzi and Scolari, 1967)":"https://www.moma.org/collection/?q=Blow%20chair",
"Gionatan De Pas":"https://www.moma.org/collection/?q=De%20Pas","Revolt chair (Friso Kramer, 1953)":"https://www.stedelijk.nl/en/collection",
"Plia folding chair (Giancarlo Piretti, 1967)":"https://www.moma.org/collection/?q=Plia",
"Krenit bowl (Herbert Krenchel, 1953)":"https://www.moma.org/collection/?q=Krenit",
"EM vacuum jug (Erik Magnussen, 1977)":"https://www.moma.org/collection/?q=Erik%20Magnussen",
"OXO Good Grips peeler (Smart Design, 1990)":"https://www.moma.org/collection/?q=OXO%20Good%20Grips",
"Spotty chair (Peter Murdoch, 1963)":"https://collections.vam.ac.uk/search/?q=Peter%20Murdoch",
"Joe chair (De Pas, D'Urbino and Lomazzi, 1970)":"https://www.moma.org/collection/?q=De%20Pas"}
DROP={"Kōichi Satō","Riki Watanabe","Gustav Siegel","Marcel Kammerer","Ugo La Pietra","Sigurd Persson","Anthon Beeke","Peter Murdoch","Magis",
"Costanza lamp (Paolo Rizzatto, 1986)","Forest (Ryuichi Yamashiro, 1955)"}
SRC={"JAPIND":[["https://en.wikipedia.org/wiki/Sori_Yanagi","Wikipedia"],["https://en.wikipedia.org/wiki/Kenji_Ekuan","Wikipedia"]],
"JAPGD":[["https://en.wikipedia.org/wiki/Yusaku_Kamekura","Wikipedia"],["https://en.wikipedia.org/wiki/Ikko_Tanaka","Wikipedia"]],
"NEWTYPO":[["https://en.wikipedia.org/wiki/Jan_Tschichold","Wikipedia"]],
"RADICAL":[["https://en.wikipedia.org/wiki/Archizoom","Wikipedia"],["https://en.wikipedia.org/wiki/Superstudio","Wikipedia"],["https://en.wikipedia.org/wiki/Studio_Alchimia","Wikipedia"]],
"DUTCHGD":[["https://en.wikipedia.org/wiki/Wim_Crouwel","Wikipedia"]],
"DROOG":[["https://en.wikipedia.org/wiki/Droog_(company)","Wikipedia"]]}
def apply(out):
    for nl in out["new_leaves"]:
        if nl["key"] in SRC: nl["src"]=SRC[nl["key"]]
        for x in nl["src"]:
            t=x[0].split("/wiki/")[1]
            if t in FIX and FIX[t]: x[0]="https://en.wikipedia.org/wiki/"+FIX[t]
        ks=[]
        for k in nl["kinds"]:
            if k[0] in DROP: continue
            if k[0] in ALT: k[3]="r3 "+ALT[k[0]]
            elif k[3].startswith("r3 https://en.wikipedia.org/wiki/"):
                t=k[3].split("/wiki/")[1]
                if t in FIX:
                    assert FIX[t], k
                    k[3]="r3 https://en.wikipedia.org/wiki/"+FIX[t]
            ks.append(k)
        nl["kinds"]=ks
