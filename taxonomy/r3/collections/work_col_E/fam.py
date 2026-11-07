import csv,sys,collections,re,gzip,json
O='/home/user/Visual-Entertainment-Taxonomy/taxonomy/r3/collections/'
P=[('X',r'projectile|bifacial|scraper|hammerstone|abrader|point fragment|\bbiface|\bflake|\bcelt\b|\bdrill\b|\bknife\b|axe\b|\bbijl'),
('H',r'textile|cloth|doek|weefsel|sari\b|shawl|kimono|furisode|kesa\b|fukusa|sarong|batik|carpet|tapijt|\brug\b|\blap\b|kant\b|kloskant|servet|kleed|muslin|tunic|embroider|borduur|裂|織|襴|緞|錦|apron|\bmat\b|basket|mand|tapa|bark ?cloth|siapo|masi\b|ceintuur|robe|\bjas\b|hemd|broek|skirt|poncho|sash|belt|costume|furoshiki|haori|lungi|fabric|weave|chintz|stof\b|muts|hat\b|garment|jacket|dress|jurk|scarf|banner|hanging|cover\b|shoe|slof|bag\b|\btas\b|loincloth|wrapper|silk|zijde|katoen|cotton|wol\b|wool|lace|naaldkant|strook|sjerp|omslagdoek|hoofddoek|ikat|kain'),
('E',r'\bpot\b|potje|\bjar\b|bowl|vase|vaas|dish|plate|sherd|scherf|vessel|aardewerk|porcel|porsel|terracotta|terra cotta|\btile|tegel|\bkom\b|kommetje|kruik|schaal|\bbord\b|tea ?bowl|theekom|\bcup\b|\bkop\b|kopje|ewer|bottle|fles|pitcher|celadon|磁|焼|釉|碗|鉢|壺|瓶|canteen|ladle|dipper|whistl|ocarina|incens|griddle|spindle whorl|\blamp|teapot|theepot|saucer|schotel|jug|urn\b|olla|pottery|ware\b|stoneware|faience|majolica|maiolica|tankard|platter|tureen|figurine|effigy|seed pot|potsherd|pitcher|mug\b|beaker|amphora|krater|kylix|lekythos|oinochoe|hydria|sake|caddy|water dropper|incense|censer|flowerpot|basin|filter|tomb jar|土人形|stirrup|spout|deksel|lid\b'),
('G',r'silver|zilver|bronze|brons|\bgold|goud|necklace|sieraad|armband|bracelet|\bring\b|earring|oorbel|sword|zwaard|dagger|copper|koper|brass|metal|iron|ijzer|blik|tin\b|coin|munt|jewel|pendant|hanger|bead|kraal|kralen|響銅'),
('I',r'\bwood|hout|lacquer|lak\b|蒔絵|drum|trom|instrument|flute|fluit|furniture|chair|stoel|comb\b|kam\b|spoon|lepel|paddle|throw|werphout|speerwerper|bow\b|boog|calabash|kalebas|gourd|coconut|kokos'),
('D',r'beeld|statue|\bmask|masker|carving|netsuke|doll|\bpop\b|speelpop|sculpt|\bhead\b|\bhoofd\b|bust\b|buddha|boeddha|figure|figuur|amulet|fetish'),
('C',r'paper|papier|book|boek|manuscript|album|sutra|drawing|tekening|design on paper|print\b|prent'),
('J',r'photo|foto|negative|negatief'),
]
P=[(f,re.compile(p,re.I)) for f,p in P]
def cls(t):
    for f,p in P:
        if p.search(t): return f
    return '?'
keys={(r['file'],r['label']) for r in csv.DictReader(open(O+'in_col_E.csv'))}
c=collections.defaultdict(collections.Counter)
tt=collections.defaultdict(collections.Counter)
for r in csv.DictReader(gzip.open(O+'objects_norm.csv.gz','rt')):
    k=(r['file'],r['label'])
    if k in keys and r['family']=='E':
        t=re.sub(r'\s*\(Image withheld.*','',r['title'])
        c[k][cls(t)]+=1
        tt[k][t[:26].lower()]+=1
rs=list(csv.DictReader(open(O+'in_col_E.csv')))
out={}
with open(O+'work_col_E/dump3.txt','w') as f:
  for i,r in enumerate(rs):
    k=(r['file'],r['label']); n=sum(c[k].values()) or 1
    fam=' '.join(f'{a}{round(100*b/n)}' for a,b in c[k].most_common(4))
    out[i]=dict(c[k])
    tops=';'.join(f'{t}({m})' for t,m in tt[k].most_common(3))
    f.write(f"{i}|{r['file'][:5]}|{r['label']}|{r['objects']}|{fam}|{tops}|{r['seed']}\n")
json.dump(out,open(O+'work_col_E/fam.json','w'))
