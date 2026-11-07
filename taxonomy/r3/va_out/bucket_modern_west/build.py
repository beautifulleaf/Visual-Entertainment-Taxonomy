import json, collections as C
from assign import amap, rows

W = lambda t: "https://en.wikipedia.org/wiki/" + t

# ---------- country normalisation for the residue ----------
NORM = {
 "Kingdom of Italy": "Italy", "United Kingdom of Great Britain and Ireland": "United Kingdom", "Kingdom of England": "United Kingdom",
 "British Empire": "United Kingdom", "Jersey": "United Kingdom", "Irish Republic": "Ireland",
 "German Reich": "Germany", "German Empire": "Germany", "Kingdom of Prussia": "Germany", "Kingdom of Bavaria": "Germany",
 "Kingdom of Württemberg": "Germany", "Kingdom of Saxony": "Germany", "Saxony": "Germany", "Weimar Republic": "Germany",
 "Hamburg": "Germany", "Bremen": "Germany", "Duchy of Brunswick": "Germany", "Duchy of Saxe-Coburg and Gotha": "Germany",
 "Grand Duchy of Hesse": "Germany", "Kingdom of the Netherlands": "Netherlands", "Kingdom of Denmark": "Denmark",
 "Soviet Union": "Russia", "Russian Empire": "Russia", "Russian Republic": "Russia", "Russian Socialist Federative Soviet Republic": "Russia",
 "Second Polish Republic": "Poland", "Congress Poland": "Poland", "General Government": "Poland", "Kingdom of Galicia and Lodomeria": "Poland",
 "Czech Republic": "Czechoslovakia", "First Czechoslovak Republic": "Czechoslovakia", "Czechoslovak Socialist Republic": "Czechoslovakia",
 "Austria–Hungary": "Czechoslovakia", "Austrian Empire": "Austria", "Cisleithania": "Austria",
 "Kingdom of Serbs": "Slovenia", "Kingdom of Yugoslavia": "Serbia", "Socialist Federal Republic of Yugoslavia": "Croatia",
 "Federal People's Republic of Yugoslavia": "Slovenia", "Yugoslavia": "Serbia", "Ottoman Empire": "Turkey",
 "Ukrainian State": "Ukraine", "Ukrainian People's Republic": "Ukraine", "Ukrainian Soviet Socialist Republic": "Ukraine",
 "Mandatory Palestine": "Israel", "Kingdom of France": "Ecuador", "Grand Duchy of Finland": "Finland", "Kingdom of Portugal": "Portugal",
 "Kingdom of Romania": "Romania", "Principality of Albania": "Albania", "British Raj": "India", "Dutch East Indies": "Indonesia",
 "French protectorate of Tunisia": "Tunisia", "Bonaire": "Caribbean Netherlands", "": "Country unrecorded",
}
OVR = {}
def ov(country, names):
    for n in names.split(";"): OVR[n.strip()] = country
ov("Austria", "Josefine Swoboda; Fritz Hegenbart; Eugenie Breithut-Munk; Michel Fingesten; Albert Reuss; Joseph Tomanek; Lea von Littrow; Rudolf Steiner; Ernst Klimt; Alois Hans Schram; Otto Barth")
ov("Slovakia", "Jozef Murgaš"); ov("Italy", "Umberto Veruda; Gregorio Sciltian")
ov("Czechoslovakia", "Jan Vilímek; Luděk Marold; Alfred Justitz"); ov("Romania", "Octavian Smigelschi"); ov("Hungary", "Géza Vastagh")
ov("Germany", "Leopold Schmutzler")
ov("Croatia", "Oton Iveković; Nasta Rojc; Ljubo Babić; Marta Ehrlich; Stanislav Rapotec; Zlatko Prica; Anka Krizmanić; Albert Kinert; Miljenko Stančić")
ov("Serbia", "Kosta Miličević; Aleksandar Deroko; Sava Šumanović; Nikolay Krasnov; Elena Andreevna Kiceliova; Stojan Ćelić; Radomir Damnjanović Damnjan; Mladen Srbinović; Lazar Vujaklija; Ranko Radović")
ov("Slovenia", "Rudolf Maister; Janez Bernik; Kiar Mesko")
ov("Bulgaria", "Anton Mitov"); ov("Armenia", "Arshak Fetvadjian; Charles Garabed Atamian; Vardges Sureniants; Karen Smbatyan; Marcos Grigorian")
ov("Greece", "Nicolai Himona"); ov("United Kingdom", "William Walcot; Boris Anrep"); ov("Australia", "Danila Vassilieff")
ov("France", "Théodore Strawinsky")
ov("Czechoslovakia", "Otakar Kubín"); ov("Switzerland", "Edouard Vallet; Marguerite Burnat-Provins"); ov("Canada", "J. E. H. MacDonald; Arthur Lismer"); ov("Tunisia", "Moses Levy")
ov("Croatia", "Krsto Hegedušić; Marijan Detoni; Ivan Tabaković; Dimitrije Bašičević"); ov("Serbia", "Đorđe Andrejević-Kun")
ov("Ukraine", "Nikolai Samokysh; Бокій Микола Миколайович; Орлов Іван Іванович; Іванов Іван Іванович; Іорданський Борис В'ячеславович")
ov("Poland", "Stanisław Kaczor-Batowski"); ov("Belarus", "Hieorhij Niski; Pavyel Maslyenikaw"); ov("Uzbekistan", "Igor Savitsky")

ORDER = ["France", "Belgium", "Netherlands", "Luxembourg", "United Kingdom", "Ireland", "Germany", "East Germany", "Austria", "Switzerland",
 "Liechtenstein", "Italy", "Slovenia", "Spain", "Portugal", "Denmark", "Faroe Islands", "Iceland", "Norway", "Sweden", "Finland",
 "Czechoslovakia", "Slovakia", "Hungary", "Poland", "Estonia", "Latvia", "Lithuania", "Russia", "Ukraine", "Belarus", "Armenia", "Georgia",
 "Azerbaijan", "Uzbekistan", "Moldova", "Romania", "Croatia", "Bosnia and Herzegovina", "Serbia", "Montenegro", "North Macedonia",
 "Albania", "Bulgaria", "Greece", "Cyprus", "Malta", "Turkey", "Israel", "Kuwait", "Tunisia", "South Africa", "Namibia", "Mozambique", "India",
 "Indonesia", "United States", "Canada", "Mexico", "Cuba", "Panama", "Caribbean Netherlands", "Suriname", "Venezuela", "Colombia", "Ecuador",
 "Peru", "Chile", "Argentina", "Brazil", "Australia", "New Zealand", "Country unrecorded"]
RANK = {c: i for i, c in enumerate(ORDER)}

def country(r):
    if r[0] in OVR: return OVR[r[0]]
    c = r[5]["countries"].split(",")[0].strip()
    return NORM.get(c, c)

ROLE = {}
def role(word, names):
    for n in names.split(";"): ROLE[n.strip()] = word
role("sculptor", "Barbara Hepworth; Arturo Martini; Clara Westhoff; Othmar Schimkowitz; Teresa Feoderovna Ries; Béni Ferenczy; Xawery Dunikowski; Manolo Hugué; Jorge Oteiza; Eduardo Chillida; Nestor Basterretxea; René Quillivic; Jacob Epstein")
role("architect", "Marcel Kammerer; Joseph Maria Olbrich; Józef Czajkowski")
role("designer", "Dagobert Peche; Carl Otto Czeschka; Eduard Josef Wimmer-Wisgrill; Jutta Sika; Bertold Löffler; Karl Diebitsch; Richard Klein; Koloman Moser")
role("ceramicist", "Gudrun Baudisch-Wittke; Josep Llorens i Artigas")
role("mosaicist and designer", "Leopold Forstner"); role("graphic artist", "Moriz Jung; Rudolf Kalvach; Ricard Opisso; Karel Teige")
role("tapestry artist", "Noémi Ferenczy"); role("photographer", "Brassaï")
role("artist", "Heinz Mack; Günther Uecker; Oskar Holweck; Armando; Henk Peeters; Jan Schoonhoven; Herman de Vries; Jan Henderikse; Jef Verheyen; Walter Leblanc; Dadamaino; Enrico Castellani; Agostino Bonalumi; Paolo Scheggi; Turi Simeti; Bernard Aubertin; Ilya Kabakov; Dmitri Prigov; Igor Makarevich; Francisco Infante-Arana; Vitaly Komar; Ivan Chuikov; Daniel Buren; Niele Toroni; Olivier Mosset; Michel Parmentier; Tadeusz Kantor")
MED = {"painting": "painter", "sculpture": "sculptor", "design and decorative arts": "designer"}

def gloss(r):
    e = r[5]; w = ROLE.get(r[0]) or MED.get(e["medium"], "artist")
    cs = [c.strip() for c in e["countries"].split(",") if c.strip()][:3]
    g = w[0].upper() + w[1:]
    if e["birth"]: g += f", born {e['birth']}"
    if cs: g += "; " + ", ".join(cs)
    old = (r[2] or "").strip()
    return g[:140]

def birth(r):
    try: return int(r[5]["birth"])
    except Exception: return 9999

# ---------- new leaves ----------
NEW = {
 "Orientalism": dict(breadth="broad", src="Orientalism",
   defn="Western painters of the Near East and North Africa, c. 1860–1940, whose work centres on scenes of the Maghreb, Egypt, the Levant and Ottoman lands: Dinet, Majorelle, the pensionnaires of the Villa Abd-el-Tif in Algiers, British and Spanish travelling painters. Earlier academic Orientalists (Gérôme, Fromentin) belong here too.",
   axis="by national school and institution: French Orientalists of the Third Republic, Villa Abd-el-Tif and the École d'Alger, then British, German, Austrian and Swiss, Spanish, Dutch and Belgian Orientalists; by birth within each",
   groups=["French Orientalists of the Third Republic", "Villa Abd-el-Tif and the École d'Alger", "British Orientalists", "German, Austrian and Swiss Orientalists", "Spanish Orientalists", "Dutch and Belgian Orientalists"],
   cats=[[W("List_of_Orientalist_artists"), "List of Orientalist artists (Wikipedia)", "alphabetical list of Orientalist painters with links to their articles"],
         ["https://www.wikiart.org/en/artists-by-art-movement/orientalism", "WikiArt: Orientalism", "artists and images catalogued under the Orientalism movement"],
         ["https://www.metmuseum.org/art/collection/search?q=Orientalism", "The Met collection search: Orientalism", "objects in the Metropolitan Museum tagged or described as Orientalist"]]),
 "Mir iskusstva": dict(breadth="medium", src="Mir_iskusstva",
   defn="The St Petersburg World of Art society and magazine (1898–1904, revived 1910–1924) around Benois, Bakst and Diaghilev: retrospective, graphic and theatrical art. Members only: Somov, Lanceray, Golovin, Ostroumova-Lebedeva, Bilibin, Kustodiev, Roerich, Dobuzhinsky.",
   axis="by generation of membership: founders and first generation (1898–1904), then the second generation of the revived society (from 1910); by birth within each",
   groups=["Founders and first generation", "Second generation (from 1910)"],
   cats=[["https://www.rusmuseum.ru/", "State Russian Museum", "largest holding of World of Art paintings and graphics, with online collection"],
         ["https://artsandculture.google.com/search?q=Mir%20iskusstva", "Google Arts & Culture: Mir iskusstva", "digitised works from partner museums tagged World of Art"],
         ["https://www.metmuseum.org/art/collection/search?q=Bakst", "The Met collection search: Bakst", "costume and stage designs by Bakst and the World of Art circle"]]),
 "St Ives School": dict(breadth="narrow", src="St_Ives_School",
   defn="Artists working in and around St Ives, Cornwall: the Victorian–Edwardian marine and landscape colony (Olsson, Talmage), and the modernists who gathered there from 1939 around Ben Nicholson and Barbara Hepworth (Lanyon, Heron, Hilton, Frost, Wynter, Barns-Graham).",
   axis="by phase: the early St Ives art colony, then the St Ives modernists from 1939; by birth within each",
   groups=["Early St Ives art colony", "St Ives modernists (1939 onward)"],
   cats=[["https://www.tate.org.uk/art/art-terms/s/st-ives-school", "Tate: St Ives School", "Tate's term page with its collection works by the St Ives artists (Tate St Ives)"],
         ["https://www.tate.org.uk/search?q=St+Ives+School", "Tate collection search: St Ives School", "all Tate records matching St Ives School"],
         ["https://artuk.org/discover/artists", "Art UK artists", "every oil painting in UK public collections, searchable by artist"]]),
 "Camden Town Group": dict(breadth="narrow", src="Camden_Town_Group",
   defn="The London group of Post-Impressionist painters formed in 1911 around Walter Sickert at 19 Fitzroy Street (Gore, Gilman, Ginner, Bevan, Drummond, Manson, Lightfoot, Innes), with the women of the Fitzroy Street Group who were barred from membership (Sands, Gosse, Lessore).",
   axis="members of the Camden Town Group (1911–1913) first, then the Fitzroy Street Group and associates; by birth within each",
   groups=["Camden Town Group members", "Fitzroy Street Group and associates"],
   cats=[["https://www.tate.org.uk/art/research-publications/camden-town-group", "Tate: The Camden Town Group in Context", "Tate research publication cataloguing the group's works, with essays"],
         ["https://www.tate.org.uk/art/art-terms/c/camden-town-group", "Tate: Camden Town Group", "term page linking Tate collection works by the group"]]),
 "ZERO": dict(breadth="medium", src="Zero_(art)",
   defn="The ZERO movement of light, motion and monochrome (1957–1966): the Düsseldorf ZERO group (Mack, Piene, Uecker), the Dutch Nul group, the Milan Azimut/h circle (Castellani, Manzoni) and Belgian and French associates.",
   axis="by group: ZERO group, Düsseldorf; Nul group, Netherlands; Azimut/h and the Italian ZERO circle; Belgian ZERO circle; international associates; by birth within each",
   groups=["ZERO group, Düsseldorf", "Nul group, Netherlands", "Azimut/h and the Italian ZERO circle", "Belgian ZERO circle", "International ZERO associates"],
   cats=[["https://www.zerofoundation.de/en/", "ZERO foundation, Düsseldorf", "archive of the ZERO movement with artist and exhibition records"],
         ["https://www.tate.org.uk/art/art-terms/z/zero", "Tate: ZERO", "term page with Tate collection works by ZERO artists"],
         ["https://www.centrepompidou.fr/en/recherche/oeuvres?terms=ZERO", "Centre Pompidou collection search: ZERO", "works in the Musée national d'art moderne matching ZERO"]]),
 "Leipzig School": dict(breadth="narrow", src="Leipzig_School_(painting)",
   defn="The figurative painting school of the Leipzig Academy of Visual Arts in the German Democratic Republic: the founding generation (Heisig, Tübke, Mattheuer, Sitte) and their students (Rink, Stelzmann, Zander). Not the post-1990 New Leipzig School.",
   axis="founding generation first, then the second generation of Leipzig Academy students; by birth within each",
   groups=["Founders: the 'big four' generation", "Second generation"],
   cats=[["https://www.bildatlas-ddr-kunst.de/", "Bildatlas: Kunst in der DDR", "database of some 20,000 GDR artworks in German public collections"],
         ["https://www.mdbk.de/en/collection/", "Museum der bildenden Künste Leipzig: collection", "the main public holding of Leipzig School painting"]]),
 "Nazi art": dict(breadth="narrow", src="Nazi_art",
   defn="Officially sanctioned art of the Third Reich (1933–1945): painters shown and bought at the Great German Art Exhibitions in Munich (Ziegler, Wissel, Peiner, Eichhorst, Saliger), and designers of party imagery. Membership test: work defined by the regime's cultural policy.",
   axis="painters of the Great German Art Exhibitions first, then designers and functionaries; by birth within each",
   groups=["Painters of the Great German Art Exhibitions", "Designers and functionaries"],
   cats=[["https://www.gdk-research.de/", "GDK Research", "photographic record of every work shown at the Great German Art Exhibitions, Munich 1937–1944"]]),
 "Vienna Secession": dict(breadth="medium", src="Vienna_Secession",
   defn="The Union of Austrian Artists founded in 1897 by Klimt, Moser, Moll, Olbrich and Hoffmann, its exhibitions in the Secession building, and the Wiener Werkstätte workshops (1903–1932) that grew from it.",
   axis="founding members (1897) first, then later members, then the Wiener Werkstätte and Kunstschau designers; by birth within each",
   groups=["Founding members (1897)", "Later members", "Members from outside Vienna", "Wiener Werkstätte and the Kunstschau"],
   cats=[["https://www.leopoldmuseum.org/en/collection", "Leopold Museum collection", "the largest Viennese holding of Secession and Wiener Werkstätte art"],
         ["https://sammlung.mak.at/en", "MAK collection online", "Museum of Applied Arts, Vienna: Wiener Werkstätte archive and objects"],
         ["https://collections.vam.ac.uk/search/?q=Wiener%20Werkstatte", "V&A search: Wiener Werkstätte", "Wiener Werkstätte objects in the Victoria and Albert Museum"],
         ["https://www.tate.org.uk/art/art-terms/s/secession", "Tate: Secession", "term page on the Vienna, Munich and Berlin secessions"]]),
 "Novecento Italiano": dict(breadth="narrow", src="Novecento_Italiano",
   defn="The Milan movement of a modern classical 'return to order' founded in 1922 by Margherita Sarfatti with seven painters (Bucci, Dudreville, Funi, Malerba, Marussig, Oppi, Sironi) and widened in the national exhibitions of 1926 and 1929 (Tosi, Carena, Campigli, Martini).",
   axis="the seven founding painters (1922) first, then exhibitors of the 1926 and 1929 shows, then the Italiens de Paris; by birth within each",
   groups=["The 'Seven painters of the Novecento' (1922)", "Exhibitors of the Novecento Italiano (1926–1929)", "Italiens de Paris"],
   cats=[["https://www.mart.tn.it/en/collezioni", "Mart, Rovereto: collections", "Museum of Modern and Contemporary Art of Trento and Rovereto, a main Novecento holding"],
         ["https://artsandculture.google.com/search?q=Novecento%20Italiano", "Google Arts & Culture: Novecento Italiano", "digitised works from Italian partner museums"]]),
 "Modernisme": dict(breadth="medium", src="Modernisme",
   defn="Catalan modernism in painting, c. 1888–1911: Rusiñol and Casas's Sitges festivals, the Els Quatre Gats tavern circle and the Colla del Safrà, and the decorative painters of Barcelona. Architecture of the movement sits under Art Nouveau Architecture.",
   axis="founders (Sitges festes modernistes) first, then the Colla del Safrà and Els Quatre Gats circle, then later Modernista painters; by birth within each",
   groups=["Founders: the Sitges festes modernistes", "Colla del Safrà and Els Quatre Gats circle", "Later Modernista painters"],
   cats=[["https://www.museunacional.cat/en/collection", "Museu Nacional d'Art de Catalunya: collection", "the main public holding of Catalan Modernista painting"],
         ["https://www.wikiart.org/en/artists-by-art-movement/modernismo", "WikiArt: Modernismo", "artists catalogued under Catalan Modernisme"]]),
 "Noucentisme": dict(breadth="narrow", src="Noucentisme",
   defn="The Catalan cultural movement of a Mediterranean classicism (c. 1906–1923) named by Eugeni d'Ors, reacting against Modernisme: Sunyer, Torres-García, Togores, Galí, Obiols, the sculptors Clarà and Manolo Hugué.",
   axis="painters first, then sculptors and designers; by birth within each",
   groups=["Noucentista painters", "Noucentista sculptors and designers"],
   cats=[["https://www.museunacional.cat/en/collection", "Museu Nacional d'Art de Catalunya: collection", "Noucentista painting and sculpture in the national collection of Catalonia"],
         ["https://artsandculture.google.com/search?q=Noucentisme", "Google Arts & Culture: Noucentisme", "digitised Noucentista works from partner museums"]]),
 "Soviet nonconformist art": dict(breadth="medium", src="Soviet_nonconformist_art",
   defn="Unofficial art made in the Soviet Union outside Socialist Realism, c. 1953–1986: the Lianozovo group, Moscow Conceptualism, Sots Art, the Dvizhenie kinetic group and independent Moscow and Leningrad artists.",
   axis="by circle: Lianozovo group, Moscow Conceptualism, Sots Art, Dvizhenie group, then other Moscow and Leningrad unofficial artists; by birth within each",
   groups=["Lianozovo group", "Moscow Conceptualism", "Sots Art", "Dvizhenie group", "Moscow and Leningrad unofficial artists"],
   cats=[["https://www.zimmerli.rutgers.edu/", "Zimmerli Art Museum (Norton and Nancy Dodge Collection)", "the largest collection of Soviet nonconformist art, some 20,000 works"],
         ["https://www.wikiart.org/en/artists-by-art-movement/sots-art", "WikiArt: Sots Art", "artists catalogued under Sots Art"]]),
 "Nagybánya artists' colony": dict(breadth="narrow", src="Nagybánya_artists'_colony",
   defn="The plein-air painters' colony founded in 1896 at Nagybánya (Baia Mare) by Hollósy, Ferenczy, Réti, Thorma and Iványi-Grünwald, the cradle of Hungarian modern painting, including the 'Neos' who became The Eight.",
   axis="founders first, then later Nagybánya painters, then the Neos who became The Eight (Nyolcak); by birth within each",
   groups=["Founders", "Later Nagybánya painters", "The Neos, later The Eight (Nyolcak)"],
   cats=[["https://www.mng.hu/en/", "Hungarian National Gallery", "the main collection of Nagybánya painting (Hungarian National Gallery, Budapest)"],
         ["https://artsandculture.google.com/search?q=Nagyb%C3%A1nya", "Google Arts & Culture: Nagybánya", "digitised Nagybánya works from partner museums"]]),
 "Young Poland": dict(breadth="medium", src="Young_Poland",
   defn="Polish modernism c. 1890–1918, centred on Kraków: Symbolist and Art Nouveau painters of the Society of Polish Artists 'Sztuka' (Malczewski, Wyspiański, Mehoffer, Stanisławski, Boznańska) and its sculptors and designers.",
   axis="members of the Society of Polish Artists 'Sztuka' first, then sculptors and designers; by birth within each",
   groups=["Society of Polish Artists 'Sztuka'", "Sculptors and designers"],
   cats=[["https://zbiory.mnk.pl/en", "National Museum in Kraków: digital collections", "the main holding of Young Poland painting"],
         ["https://www.mnw.art.pl/en/collections/", "National Museum in Warsaw: collections", "Polish painting 1890–1918 in the national collection"]]),
 "Kraków Group": dict(breadth="narrow", src="Kraków_Group",
   defn="The Kraków avant-garde association founded in 1932 and re-founded in 1957 around Tadeusz Kantor, Maria Jarema and Jonasz Stern: abstraction, Informel and theatre.",
   axis="members of the Kraków Group; by birth",
   groups=["Kraków Group"],
   cats=[["https://cricoteka.pl/en/", "Cricoteka", "Centre for the Documentation of the Art of Tadeusz Kantor, Kraków"],
         ["https://zbiory.mnk.pl/en", "National Museum in Kraków: digital collections", "post-war Kraków Group works in the national collection"]]),
}

# ---------- assemble ----------
moves, newk, resid = [], C.defaultdict(list), C.defaultdict(list)
regions = C.defaultdict(C.Counter)
for r in rows:
    n = r[0]
    if len(r) < 6:  # the Yanktonai Dakota culture row
        resid["United States"].append(["Oscar Howe", "United States", "Yanktonai Dakota modernist painter (1915–1983); 59 watercolours in the Smithsonian records", r[3], 1, 1915]); continue
    t = amap.get(n)
    if t and not t.startswith(("N:", "G:")):
        moves.append([n, "A5-110", t]); continue
    if t and t.startswith("N:"):
        lab, grp = t[2:].split("|")
        newk[lab].append([n, grp, gloss(r), "artists", 1, birth(r)]); continue
    if t: grp = t[2:]
    elif r[1] not in ("Artists", "Noucentisme", "Prague Secession", "White Rabbits", "Group of Seven", "École d'Alger"): grp = r[1]
    else: grp = country(r)
    regions[grp][country(r)] += 1
    resid[grp].append([n, grp, gloss(r), r[3], 1, birth(r)])

# split oversized country groups by generation
BINS = [(0, 1869, "born before 1870"), (1870, 1879, "born 1870–1879"), (1880, 1899, "born 1880–1899"), (1900, 1919, "born 1900–1919"), (1920, 1929, "born 1920–1929"), (1930, 9999, "born 1930 and later")]
final = {}
for g, lst in resid.items():
    if len(lst) > 150 and g in RANK:
        for lo, hi, lab in BINS:
            sub = [x[:] for x in lst if lo <= x[5] <= hi]
            for x in sub: x[1] = f"{g}, {lab}"
            if sub: final[f"{g}, {lab}"] = (RANK[g], 1, lo, sub)
    else:
        home = g if g in RANK else (regions[g].most_common(1)[0][0] if regions[g] else "Country unrecorded")
        final[g] = (RANK.get(home, 999), 1 if g in RANK else 0, sorted(x[5] for x in lst)[len(lst)//2], lst)
kinds = []
for g, (rk, isc, lo, lst) in sorted(final.items(), key=lambda kv: kv[1][:3]):
    kinds += [x[:5] for x in sorted(lst, key=lambda x: (x[5], x[0]))]

named = sorted({g for g, v in final.items() if v[1] == 0})
countries_used = [g for g in ORDER if g in resid]
out = {"leaves": {"A5-110": {
  "axis": "residual Western and Central European modern painters (born c. 1860–1944) not placed in a movement leaf; grouped by country of activity in a fixed west-to-east order (France, Low Countries, Britain and Ireland, German-speaking lands, Italy, Iberia, Nordic countries, Central and Eastern Europe, Balkans, then the Americas and elsewhere); within each country, named local schools, groups and colonies come first in order of their members' median birth (e.g. Bande noire, Seiz Breur, Worpswede, Gruppe 33, De Ploeg, Corrente, Halmstad Group), then the country group itself, split by generation of birth where it exceeds 150 artists; by birth within each group",
  "defn": "Painters born c. 1860–1944 active in Europe (and a few in the Americas) whose work is modern but who belong to no movement with its own leaf here; artists of a named movement (Fauvism, Cubism, Expressionism, Surrealism, Vienna Secession, Novecento Italiano, St Ives School ...) are listed in that leaf instead. Small named groups without a leaf of their own are kept as sections.",
  "catalogues": [["https://www.getty.edu/research/tools/vocabularies/ulan/", "Getty Union List of Artist Names (ULAN)", "authority records for some 300,000 artists with nationality, dates and roles"],
                 ["https://research.rkd.nl/en/", "RKD Research", "Netherlands Institute for Art History database of artists and artworks, strong on Dutch and Flemish artists"],
                 ["https://artuk.org/discover/artists", "Art UK: artists", "every oil painting in UK public collections, browsable by artist"],
                 ["https://www.europeana.eu/en/search?query=modern%20painting", "Europeana search", "digitised works from European museums and archives"]],
  "kinds": kinds, "alias_rows": []}},
 "new_leaves": [], "moves_out": moves, "dropped": []}
for i, (lab, d) in enumerate(NEW.items(), 1):
    lst = newk.get(lab, [])
    order = {g: j for j, g in enumerate(d["groups"])}
    ks = [x[:5] for x in sorted(lst, key=lambda x: (order.get(x[1], 99), x[5], x[0]))]
    out["new_leaves"].append({"key": f"NEW{i}", "sub": "A5", "label": lab, "breadth": d["breadth"], "defn": d["defn"], "aliases": "",
        "see": "A5-110 Modern Art", "src": [[W(d["src"]), "Wikipedia"]], "catalogues": d["cats"], "axis": d["axis"], "kinds": ks})
missing = set(newk) - set(NEW)
assert not missing, missing
json.dump(out, open("result.json", "w"), ensure_ascii=False, indent=1)
gs = C.Counter(k[1] for k in kinds)
print(len(kinds), "residual kinds;", len(moves), "moves;", sum(len(v) for v in newk.values()), "in new leaves")
print(sorted(gs.items(), key=lambda x: -x[1])[:25])
print([g for g, n in gs.items() if n > 150])
