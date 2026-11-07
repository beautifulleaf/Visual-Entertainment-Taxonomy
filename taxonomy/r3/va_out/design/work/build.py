import json, re, os, sys, unicodedata, collections
W=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(W,"..","..","..","..","..")
sys.path.insert(0,W)
inp=json.load(open(os.path.join(ROOT,"taxonomy/r3/va_in/design.json")))["leaves"]
LEAVES=[]
for m in ("leaves1","leaves2","leaves3","leaves4","leaves5"):
    LEAVES+=__import__(m).L
KEYS={l["key"]:l for l in LEAVES}
def norm(s):
    s=s.replace("ø","o").replace("Ø","O").replace("æ","ae")
    return unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode().lower().replace(" ","")
def wurl(t): return "https://en.wikipedia.org/wiki/"+t
def country(c):
    c=(c or "").split(",")[0].strip()
    c=re.sub(r"^(Kingdom of the |Kingdom of |Empire of )","",c)
    return {"Japan":"Japan","British Raj":"India","People's Republic of China":"China","England":"United Kingdom","Second Polish Republic":"Poland"}.get(c,c) or "Country unrecorded"
# assignment, in input order
lines=[l.rstrip("\n").split("|") for l in open(os.path.join(W,"assign.txt"),encoding="utf8")]
rows=[(lf["code"],r) for lf in inp for r in lf["rows"] if r[1]=="Artists"]
assert len(rows)==len(lines),(len(rows),len(lines))
for (c,r),l in zip(rows,lines): assert r[0]==l[0],(r[0],l[0])
GROUPFIX={
 "JAPGD":{"Ikkō Tanaka":"Nippon Design Center founders","Kazumasa Nagai":"Nippon Design Center founders","Ryuichi Yamashiro":"Nippon Design Center founders","*":"Later generation"},
 "JAPIND":{"Isamu Kenmochi":"Postwar pioneers","Sori Yanagi":"Postwar pioneers","Masahiro Mori":"Postwar pioneers","*":"Contemporary"},
 "DANISH":{"Poul Cadovius":"Industrial modernists","Aksel Bender Madsen":"Cabinetmakers' Guild generation","Grete Jalk":"Cabinetmakers' Guild generation"},
 "AMCM":{"Irving Harper":"Herman Miller circle","Robert Propst":"Herman Miller circle","Jens Risom":"Knoll circle","Julien Hébert":"Canada","*":"Other American designers"},
 "BRITISH":{"Kenneth Grange":"Industrial designers","Douglas Scott":"Industrial designers","Alex Moulton":"Industrial designers","Susan Williams-Ellis":"Industrial designers","*":"Festival of Britain generation"},
 "POP":{"Franco Teodoro":"Italy","Olivier Mourgue":"France","Roger Tallon":"France","Edgardo Giménez":"Argentina"},
 "MEMPHIS":{"*":"International contributors"},
 "CORPID":{"Alan Fletcher":"British identity designers","Henri Kay Henrion":"British identity designers","*":"American identity designers"},
 "DUTCHGD":{"Jurriaan Schrofer":"Total Design and Stedelijk modernists","*":"Later generation"},
 "NEWWAVE":{"Wolfgang Weingart":"Basel New Wave","Dan Friedman":"Basel New Wave","Edward Fella":"Cranbrook and Emigre","Neville Brody":"Britain","Jonathan Barnbrook":"Britain","Paul Elliman":"Britain","*":"North America"},
 "POMO":{"*":"France"},"BAUHAUS":{"*":"Bauhaus students"},
}
RES={"CER":"Studio ceramics","FIB":"Fibre art and weaving","JEW":"Art jewellery and metalwork","FAS":"Fashion design","COS":"Costume and stage design","CRF":"Craft furniture makers","OTH":"Other designers and artists"}
ROLE={"CER":"studio ceramist","FIB":"textile and fibre artist","JEW":"jeweller and metalsmith","FAS":"fashion designer","COS":"costume and stage designer","CRF":"furniture maker","OTH":"designer"}
OTHNOTE={"Margot Fonteyn":"British ballerina (1919–1991); in the design data via Wikidata, not a designer",
 "Chris Eubank":"British boxer (b. 1966); in the design data via Wikidata, not a designer",
 "Tony Esposito":"Canadian ice-hockey goaltender (1943–2021); in the design data via Wikidata",
 "Eka Kurniawan":"Indonesian novelist (b. 1975); in the design data via Wikidata",
 "Niels Due Jensen":"Danish engineer and Grundfos chairman (b. 1943)",
 "Enric Bernat":"Spanish confectioner (1923–2003); founder of Chupa Chups",
 "Denise René":"French gallerist (1913–2012); champion of Concrete and Op art",
 "Eugen Gomringer":"Bolivian-born Swiss concrete poet (1925–2025); secretary to Max Bill at Ulm",
 "Gerald Holtom":"British designer (1914–1985); nuclear-disarmament peace symbol (1958)",
 "Gilbert Baker":"American artist (1951–2017); rainbow flag (1978)",
 "Robert Kalina":"Austrian banknote designer (b. 1955); first-series euro banknotes",
 "Lidewij Edelkoort":"Dutch trend forecaster (b. 1950)",
 "Roman Haubenstock-Ramati":"Polish-Austrian composer (1919–1994); graphic scores",
 "Joop Geesink":"Dutch puppet-animation producer (1913–1984); Dollywood studio",
 "Jack Ryan":"American toy designer at Mattel (1926–1991); Barbie and Hot Wheels",
 "Hobart Alter":"American surfboard and catamaran maker (1933–2014); Hobie Cat",
 "James Harvey":"American painter and package designer (1929–1965); Brillo box",
 "Jon Bannenberg":"Australian yacht designer (1929–2002)",
 "Savitri Khanolkar":"Swiss-Indian artist (1913–1990); designed the Param Vir Chakra",
 "Edwin Schlossberg":"American exhibition designer (b. 1945); ESI Design",
 "Ben Kelly":"British interior designer (b. 1949); Haçienda nightclub, Manchester",
 "Patrick Reyntiens":"British stained-glass artist (1925–2021); Coventry Cathedral baptistery window",
 "Giorgia Lupi":"Italian information designer (b. 1981); Dear Data, Pentagram",
 "Bahia Shehab":"Lebanese-Egyptian designer (b. 1977); Arabic typography and street art",
 "Ferdinand Kriwet":"German visual-poetry artist (1942–2018)",
 "Mark Perry":"British punk writer (b. 1957); Sniffin' Glue fanzine",
 "Diana Phipps":"Austrian-British interior decorator (b. 1936)",
 "Sussanne Khan":"Indian interior designer (b. 1978)",
 "Mohamed Melehi":"Moroccan artist and graphic designer (1936–2020); Casablanca School",
 "David Tartakover":"Israeli graphic designer (b. 1944); political posters",
 "Izzika Gaon":"Israeli designer and curator (1938–2006); Israel Museum design department",
 "Mengü Ertel":"Turkish graphic designer (1931–2015)",
 "Idania del Río":"Cuban graphic designer (b. 1981); Clandestina, Havana",
 "Oscar Mariné":"Spanish graphic designer (b. 1951); Almodóvar film posters",
 "Renate Müller":"German toy designer (b. 1945); therapeutic jute toys, GDR",
 "Libuše Niklová":"Czech toy designer (1934–1981); inflatable rubber toys for Fatra",
 "J. S. G. Boggs":"American artist (1955–2017); hand-drawn banknotes",
 "Suzanne Lee":"British designer (b. 1970); BioCouture grown materials",
 "Pablo Reinoso":"Argentine-French artist-designer (b. 1955); Spaghetti benches",
 "Arno Coenen":"Dutch artist (b. 1972); Markthal Rotterdam ceiling mural",
 "Jens Eilstrup Rasmussen":"Danish computer scientist (b. 1966); co-creator of Google Maps",
 "Edward Windsor, Lord Downpatrick":"British fashion designer (b. 1988)",
 "Josua Reichert":"German typographic artist (1937–2020)",
 "Greta Schödl":"Austrian visual-poetry artist (b. 1929)",
 "Daria Dorosh":"Ukrainian-born American artist (b. 1943); A.I.R. Gallery co-founder",
 "Enzo Apicella":"Italian designer and cartoonist in London (1922–2018); Pizza Express interiors",
 "Kevin Beasley":"American artist (b. 1985); sculpture and sound",
 "Meriem Bennani":"Moroccan artist (b. 1988); video and installation",
 "Ademola Olugebefola":"American artist (b. 1941); Weusi Artist Collective",
}
def yr(r):
    e=r[5] if len(r)>5 else {}
    return e.get("birth","")
def gl_input(code,r,t):
    e=r[5] if len(r)>5 else {}
    if r[0] in OTHNOTE: return OTHNOTE[r[0]]
    c=country(e.get("countries","")); b=e.get("birth","")
    s=f"{c} {ROLE[t]}"+(f", b. {b}" if b else "")
    if e.get("movements"): s+=f"; {e['movements']}"
    return s
out={"leaves":{},"new_leaves":[],"moves_out":[],"dropped":[]}
resid={"I3-19":[],"I3-20":[]}; nin=collections.defaultdict(list)
for (code,r),l in zip(rows,lines):
    t=l[1]
    if t.startswith(">"): out["moves_out"].append([r[0],code,t[1:]]); continue
    if t in RES:
        g=RES[t]
        if t=="FAS":
            c=country((r[5] if len(r)>5 else {}).get("countries",""))
            g="Fashion design: "+(c if c in ("France","Italy","United States","United Kingdom","Japan") else "other countries")
        resid[code].append([r[0],g,gl_input(code,r,t),r[3],1,yr(r)]); continue
    key,_,grp=t.partition(":")
    assert key in KEYS,key
    fx=GROUPFIX.get(key,{})
    grp=fx.get(r[0]) or fx.get("*") or grp or "Designers"
    if key=="CONTEMP" and grp!="Critical and social design":
        grp=country((r[5] if len(r)>5 else {}).get("countries",""))
    nin[key].append([r[0],grp,l[2],r[3],1,yr(r)])
# possession row
poss=[r for lf in inp for r in lf["rows"] if r[1]!="Artists"]
assert len(poss)==1
def by(v):
    m=re.search(r"\((?:b\. )?(\d{4})",v[2]); return int(v[5] or (m.group(1) if m else 3000))
GO=["Furniture and products","Lighting","Glass","Graphic design"]
for l in LEAVES:
    k=l["key"]; kinds=[]
    for n,g,s in l.get("firms",[]):
        kinds.append([n,"Centres & workshops",g,s if s.startswith("possession") else "r3 "+wurl(s),0])
    for n,g,s in l["objs"]: kinds.append([n,"Designed objects",g,"r3 "+wurl(s),0])
    ins={norm(x[0]):x for x in nin[k]}
    des=[]; order=[]
    for n,g,gl,t in l["des"]:
        if g not in order: order.append(g)
        if norm(n) in ins:
            x=ins.pop(norm(n)); x[1]=g; x[2]=gl; des.append(x)
        else: des.append([n,g,gl,"r3 "+wurl(t or n.replace(" ","_")),0,""])
    for x in nin[k]:
        if norm(x[0]) in ins:
            des.append(x)
            if x[1] not in order: order.append(x[1])
    if k=="ITALIAN": order=[g for g in GO if g in order]+[g for g in order if g not in GO]
    if k=="CONTEMP":
        cc=collections.Counter(x[1] for x in des)
        for x in des:
            if cc[x[1]]<2: x[1]="other countries"
        cc=collections.Counter(x[1] for x in des); order=list(dict.fromkeys(x[1] for x in des))
        order=["Critical and social design"]+sorted([g for g in order if g!="Critical and social design"],key=lambda g:(g=="other countries",-cc[g]))
    multi=len(order)>1
    for g in order:
        for x in sorted([x for x in des if x[1]==g],key=by):
            kinds.append([x[0],("Designers: "+g) if multi else "Designers",x[2],x[3],1])
    nl=dict(key=k,sub=l["sub"],label=l["label"],breadth=l["breadth"],defn=l["defn"],aliases="",see="",src=l["src"],catalogues=l["cat"],
            axis=l["axis"].replace("designers:", "designers (born-year order within each group):",1),kinds=kinds)
    if k=="SCAND": nl["aliases"]="Swedish Modern; Nordic design; Design in Scandinavia"
    if k=="BAUHAUS": nl["see"]="I3-17"
    if k=="CONSTR": nl["see"]="B2-11"
    out["new_leaves"].append(nl)
# residual leaves
RO=["Craft furniture makers","Studio ceramics","Fibre art and weaving","Art jewellery and metalwork","Fashion design: France","Fashion design: Italy","Fashion design: United States","Fashion design: United Kingdom","Fashion design: Japan","Fashion design: other countries","Costume and stage design","Other designers and artists"]
CATS=[["https://www.vogue.com/fashion-shows","Vogue Runway","every runway collection of the fashion houses listed here"],
      ["https://www.metmuseum.org/art/collection/search?q=Costume%20Institute","Metropolitan Museum: Costume Institute","fashion holdings of the Met"],
      [VA:="https://collections.vam.ac.uk/search/?q=studio%20pottery","V&A collections: studio pottery","studio ceramics in the V&A"]]
for code,lab,defn in (("I3-19","Mid-Century","Designer-makers born c. 1910–1944 outside the design schools of N Design: craft furniture makers, studio ceramists, fibre artists, art jewellers, fashion and costume designers. Serial-production designers now sit in N Design leaves."),
                      ("I3-20","Contemporary","Designer-makers born from 1945 outside the design schools of N Design: craft furniture, studio ceramics, fibre art, art jewellery, fashion and costume design. Serial-production designers now sit in N Design leaves.")):
    ks=[]
    for g in RO:
        for x in sorted([x for x in resid[code] if x[1]==g],key=lambda x:x[5] or "9999"): ks.append(x[:5])
    out["leaves"][code]={"axis":"residual of designers placed in N Design: by craft field (furniture, ceramics, fibre, jewellery), then fashion by country, costume, others; born-year order",
        "defn":defn,"catalogues":CATS,"kinds":ks,"alias_rows":[]}
out["leaves"]["I3-19"]["alias_rows"]=[]
out["dropped"].append(["I3-19","Scandinavian Modern","restates the new leaf Scandinavian Modern; its Georg Jensen possession link kept there as 'Georg Jensen silver'"])
# drop added duplicates across leaves (keep first)
seen={}
for nl in out["new_leaves"]:
    keep=[]
    for x in nl["kinds"]:
        if x[4] and x[3].startswith("r3"):
            if x[0] in seen: continue
            seen[x[0]]=nl["key"]
        keep.append(x)
    nl["kinds"]=keep
json.dump(out,open(os.path.join(W,"..","result.json"),"w"),ensure_ascii=False,indent=1)
print({nl["key"]:len(nl["kinds"]) for nl in out["new_leaves"]}, {c:len(v["kinds"]) for c,v in out["leaves"].items()}, len(out["moves_out"]))
