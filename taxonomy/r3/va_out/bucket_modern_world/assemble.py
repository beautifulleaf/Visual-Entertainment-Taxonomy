import json, collections
S = json.load(open('stage.json'))
W = 'https://en.wikipedia.org/wiki/'
MERGE = {'Saudi Arabia':'Syria, Jordan and the Gulf','Bahrain':'Syria, Jordan and the Gulf','Syria':'Syria, Jordan and the Gulf','Jordan':'Syria, Jordan and the Gulf','Kuwait':'Syria, Jordan and the Gulf',
 'Benin':'Benin, Cameroon and Togo','Cameroon':'Benin, Cameroon and Togo','Togo':'Benin, Cameroon and Togo',
 'Tanzania':'Tanzania and Mozambique','Mozambique':'Tanzania and Mozambique',
 'Malaysia':'Malaysia and Singapore','Singapore':'Malaysia and Singapore',
 'Myanmar':'Myanmar, Thailand and Vietnam','Thailand':'Myanmar, Thailand and Vietnam','Vietnam':'Myanmar, Thailand and Vietnam',
 'Fiji':'Fiji and Papua New Guinea','Papua New Guinea':'Fiji and Papua New Guinea',
 'Ecuador':'Bolivia, Ecuador and Paraguay','Bolivia':'Bolivia, Ecuador and Paraguay','Paraguay':'Bolivia, Ecuador and Paraguay',
 'Guyana':'Guyana and Suriname','Suriname':'Guyana and Suriname',
 'United Kingdom':'Europe','Germany':'Europe','Ukraine':'Europe',"Generation of the '30s (Greece)":'Europe',
 'United States (birth year not recorded)':'United States (born 1880–1894)' }
ORDER = """Stieglitz circle (291 and An American Place)
Woodstock art colony
Taos and Santa Fe art colonies
Native American artists (San Ildefonso, Santa Fe Studio and after)
Chicago Black Renaissance
Spiral (arts alliance)
Boston Expressionism
United States (born 1860–1879)
United States (born 1880–1894)
United States (born 1895–1909)
United States (born 1910–1924)
United States (born 1925–1934)
United States (born 1935 and later)
Beaver Hall Group
Painters Eleven
Les Automatistes
Plasticiens
Regina Five
Woodlands School and Indian Group of Seven
Atlantic realism
Canada
Escuela Mexicana de Pintura
Oaxacan School (Mexico)
Mexico
Guatemala
El Salvador
Nicaragua
Costa Rica
Panama
Cuban Vanguardia
Los Once (Cuba)
Cuba
Dominican Republic
Puerto Rico
Jamaica
Guyana and Suriname
Venezuela
Colombia
Peru
Bolivia, Ecuador and Paraguay
Generación del 13 (Chile)
Grupo Montparnasse and Generation of '28 (Chile)
Chile
Grupo de París (Argentina)
Otra Figuración (Argentina)
Argentina
Planismo (Uruguay)
Uruguay
Grupo Rex and Nova Objetividade Brasileira
Brazil
Hi-Red Center and Japanese anti-art (1960s)
Japan
South Korea
Three Masters Crossing the Strait (渡海三家)
West Lake School (Hangzhou National Academy of Art)
New Jinling School (Jiangsu)
China
New Ink Painting movement (Hong Kong)
Ton Fan Group (Taiwan)
Fifth Moon Group (Taiwan)
Taiwan
Calcutta Group
Baroda School
Group 1890
Madras Art Movement (Cholamandal)
Neo-Tantra
India
Bangladesh (Dhaka Art Institute generation)
Lahore Art Circle and Pakistani modernists
Pakistan
'43 Group (Sri Lanka)
Mooi Indië (Indonesia)
Persagi (Indonesia)
Bandung School (Indonesia)
Indonesia
Thirteen Moderns (Philippines)
Philippines
École des Beaux-Arts de l'Indochine (Vietnam)
Myanmar, Thailand and Vietnam
Nanyang style (Singapore and Malaya)
Malaysia and Singapore
1914 Generation (Turkey)
D Group (Turkey)
Yeniler (Turkey)
Turkey
Iran
Baghdad Modern Art Group and Al-Ruwad (Iraq)
Iraq
Syria, Jordan and the Gulf
Lebanon
Palestine
Eretz-Israeli style (1920s Tel Aviv)
New Horizons (Israel)
Israel
Egypt
Khartoum School and Crystalists (Sudan)
Casablanca School (Morocco)
Morocco
École d'Alger
Algeria
École de Tunis
Tunisia
Zaria Art Society (Nigeria)
Oshogbo School (Nigeria)
Nigeria
Ghana
Benin, Cameroon and Togo
Ethiopia
Tanzania and Mozambique
Zimbabwe
South Africa
Angry Penguins
Antipodeans
Australia
The Group (Christchurch)
Māori modernism
New Zealand
Fiji and Papua New Guinea
Soviet Union
Europe""".split('\n')
res = []
for r in S['residual']:
    g = MERGE.get(r[1], r[1])
    res.append([r[0], g, r[2], r[3], 1, r[5]])
gi = {g: i for i, g in enumerate(ORDER)}
missing = sorted(set(r[1] for r in res) - set(gi))
assert not missing, missing
res.sort(key=lambda r: (gi[r[1]], r[5], r[0]))
kinds = [r[:5] for r in res]
cnt = collections.Counter(r[1] for r in kinds)
def ms(q): return f'https://www.metmuseum.org/art/collection/search?q={q}'
leaves = {'A5-110': {
  'axis': 'Non-Western-European artists only (this pass): by named school, group or colony where the literature names one, each placed beside its country; otherwise by country of activity. Regions ordered United States and Canada, Mexico and Central America, Caribbean, South America, East Asia, South Asia, Southeast Asia, West Asia, North Africa, sub-Saharan Africa, Oceania, Soviet Union; the United States is split by birth cohort; countries with one or two rows are merged with neighbours; within a group by birth year.',
  'catalogues': [
    ['https://www.getty.edu/research/tools/vocabularies/ulan/', 'Getty Union List of Artist Names (ULAN)', 'authority records for artists worldwide, with nationalities, roles and dates'],
    ['https://icaa.mfah.org/', 'ICAA Documents of Latin American and Latino Art (MFAH)', 'digital archive of primary sources on 20th-century Latin American and Latino artists and groups'],
    ['https://aaa.org.hk/en/collections', 'Asia Art Archive collections', 'archives and documentation of modern and contemporary art across Asia'],
    ['https://www.encyclopedia.mathaf.org.qa/', 'Mathaf Encyclopedia of Modern Art and the Arab World', 'biographies of modern artists of the Arab world'],
    ['https://americanart.si.edu/art', 'Smithsonian American Art Museum collection', 'about 45,000 works by American artists'],
  ],
  'kinds': kinds, 'alias_rows': []}}
def nl(key, sub, label, breadth, defn, src, cats, axis, korder):
    rows = S['NEW'][key]
    go = {g: i for i, g in enumerate(korder)}
    assert set(r[1] for r in rows) <= set(go), (key, set(r[1] for r in rows) - set(go))
    rows = sorted(rows, key=lambda r: (go[r[1]], r[5], r[0]))
    return {'key': key, 'sub': sub, 'label': label, 'breadth': breadth, 'defn': defn, 'aliases': '', 'see': 'A5-110 Modern Art',
            'src': [[src, 'Wikipedia']], 'catalogues': cats, 'axis': axis, 'kinds': [r[:5] for r in rows]}
NL = [
 nl('GUTAI','A5','Gutai group','narrow','Members of the Gutai Art Association (Gutai Bijutsu Kyōkai), founded by Jirō Yoshihara in Ashiya in 1954 and dissolved in 1972: e.g. Kazuo Shiraga, Saburō Murakami, Atsuko Tanaka, Sadamasa Motonaga.',
    W+'Gutai_group',
    [['https://www.tate.org.uk/search?q=gutai','Tate collection search: Gutai','works by Gutai members in the Tate collection'],
     ['https://www.moma.org/collection/?q=gutai','MoMA collection search: Gutai','Gutai works and documentation at MoMA'],
     ['https://ashiya-museum.jp/','Ashiya City Museum of Art & History','home collection and archive of the Gutai group']],
    'by date of joining: founding members (1954), Zero Society members who joined in 1955, other 1955 members, second generation; within a group by birth',
    ['Founding members (1954)','Zero Society members (joined 1955)','Members from 1955','Second generation (1960s)']),
 nl('G7','A5','Group of Seven (artists)','narrow','Members of the Group of Seven, the Toronto landscape painters who exhibited together from 1920 to 1931 (enlarged to ten members): e.g. Lawren Harris, A. Y. Jackson, Frederick Varley, A. J. Casson.',
    W+'Group_of_Seven_(artists)',
    [['https://mcmichael.com/','McMichael Canadian Art Collection','museum devoted to the Group of Seven and their contemporaries, Kleinburg'],
     ['https://www.gallery.ca/collection','National Gallery of Canada collection','the national collection, with large Group of Seven holdings'],
     ['https://ago.ca/collection','Art Gallery of Ontario collection','Toronto collection with major Group of Seven holdings']],
    'by membership: original members of 1920, then later members (1926–1932); within a group by birth',
    ['Original members (1920)','Later members']),
 nl('BRMOD','A5','Brazilian modernism','medium','Brazilian modernist artists from the 1917 Malfatti exhibition and the Semana de Arte Moderna (1922) to the 1940s, including the Antropofagia circle and the São Paulo and Rio groups (Grupo Santa Helena, Núcleo Bernardelli): e.g. Tarsila do Amaral, Di Cavalcanti, Candido Portinari.',
    W+'Brazilian_modernism',
    [['https://enciclopedia.itaucultural.org.br/','Enciclopédia Itaú Cultural','Portuguese-language encyclopedia of Brazilian artists, groups and works'],
     ['https://icaa.mfah.org/','ICAA Documents of Latin American and Latino Art (MFAH)','primary documents of Brazilian modernism'],
     ['https://pinacoteca.org.br/','Pinacoteca de São Paulo','collection of Brazilian art with core modernist holdings']],
    'by phase and circle: Semana de Arte Moderna and Grupo dos Cinco, second generation, then the São Paulo and Rio studio groups (Grupo Santa Helena, Núcleo Bernardelli); within a group by birth',
    ['Semana de Arte Moderna and Grupo dos Cinco','Second generation (1925–1945)','Grupo Santa Helena','Núcleo Bernardelli']),
 nl('PAG','A5',"Progressive Artists' Group",'narrow',"Members and close associates of the Progressive Artists' Group founded in Bombay in 1947 by F. N. Souza: e.g. S. H. Raza, M. F. Husain, K. H. Ara, Akbar Padamsee.",
    W+'Progressive_Artists%27_Group',
    [['https://www.knma.in/','Kiran Nadar Museum of Art','Delhi collection with major holdings of the Progressives'],
     ['https://aaa.org.hk/en/collections','Asia Art Archive collections','documentation of South Asian modernism'],
     ['https://www.tate.org.uk/search?q=progressive+artists+group','Tate collection search',"works and texts on the Progressive Artists' Group"]],
    'founding members (1947) first, then later members and associates; within a group by birth',
    ['Founding members (1947)','Later members and associates']),
 nl('RUPT','A5','Generación de la Ruptura','medium','Mexican artists of the 1950s–60s who broke with the Mexican School and muralism in favour of abstraction and new figuration: e.g. José Luis Cuevas, Manuel Felguérez, Lilia Carrillo, Vicente Rojo.',
    W+'Generaci%C3%B3n_de_la_Ruptura',
    [['https://icaa.mfah.org/','ICAA Documents of Latin American and Latino Art (MFAH)','primary documents including Cuevas\'s La cortina de nopal'],
     ['https://mam.inba.gob.mx/','Museo de Arte Moderno, Mexico City','collection of 20th-century Mexican art including the Ruptura']],
    'precursors first, then the Ruptura painters; within a group by birth',
    ['Precursors','Ruptura painters']),
 nl('TGP','B2','Taller de Gráfica Popular','narrow','Members of the Taller de Gráfica Popular, the Mexico City printmaking collective founded in 1937 by Leopoldo Méndez, Pablo O\'Higgins and Luis Arenal: e.g. Alfredo Zalce, Ángel Bracho, Mariana Yampolsky.',
    W+'Taller_de_Gr%C3%A1fica_Popular',
    [['https://www.artic.edu/collection?q=Taller+de+Gr%C3%A1fica+Popular','Art Institute of Chicago collection search','TGP prints at the Art Institute of Chicago'],
     [ms('Taller+de+Gr%C3%A1fica+Popular'),'Metropolitan Museum collection search','TGP prints at the Met'],
     ['https://icaa.mfah.org/','ICAA Documents of Latin American and Latino Art (MFAH)','TGP documents and manifestos']],
    'founders (1937) first, then members; within a group by birth (Pablo O\'Higgins is placed under Mexican Muralism)',
    ['Founders (1937)','Members']),
 nl('INDIG','A5','Indigenismo','medium','Andean indigenista painters and sculptors of c. 1920–1960 who made Indigenous people and landscape the subject of a national modern art: e.g. José Sabogal (Peru), Camilo Egas (Ecuador), Cecilio Guzmán de Rojas (Bolivia). (Mexican indigenist muralists sit under Mexican Muralism.)',
    W+'Indigenismo',
    [['https://mali.pe/','Museo de Arte de Lima (MALI)','Peruvian collection with the indigenista school'],
     ['https://icaa.mfah.org/','ICAA Documents of Latin American and Latino Art (MFAH)','primary documents of Andean indigenismo']],
    'by country: Peru (the Sabogal school), Ecuador, Bolivia; within a group by birth',
    ['Peru','Ecuador','Bolivia']),
 nl('CHIM','A5','Chicago Imagists','narrow','Chicago figurative artists shown at the Hyde Park Art Center 1966–1971 (Hairy Who, False Image, Nonplussed Some), with their teachers and the Monster Roster precursors: e.g. Jim Nutt, Gladys Nilsson, Roger Brown, Ed Paschke.',
    W+'Chicago_Imagists',
    [['https://www.artic.edu/collection?q=Hairy+Who','Art Institute of Chicago collection search','Hairy Who and Imagist works at the Art Institute'],
     ['https://smartmuseum.uchicago.edu/','Smart Museum of Art','University of Chicago collection with Chicago Imagist holdings']],
    'Monster Roster precursors (1950s), then the Hyde Park Art Center groups (Hairy Who; False Image and Nonplussed Some), then teachers and associates; within a group by birth',
    ['Monster Roster (precursors, 1950s)','Hairy Who (1966–1969)','False Image and Nonplussed Some','Teachers and associates']),
 nl('FEM','A5','Feminist art movement','medium','Artists of the feminist art movement of the late 1960s–1980s, centred in the United States (A.I.R. Gallery, Heresies, the Feminist Art Program): e.g. Judy Chicago, Nancy Spero, Harmony Hammond, Mary Beth Edelson.',
    W+'Feminist_art',
    [['https://www.brooklynmuseum.org/eascfa/feminist_art_base','Brooklyn Museum Feminist Art Base','online database of feminist artists (Elizabeth A. Sackler Center)'],
     ['https://www.airgallery.org/','A.I.R. Gallery','the first women artists\' cooperative gallery, New York (1972)']],
    'by circle: A.I.R. Gallery founders, Heresies Collective, the Feminist Art Program and West Coast, other United States artists, then outside the United States; within a group by birth',
    ['A.I.R. Gallery founders (1972)','Heresies Collective','Feminist Art Program and West Coast','Other United States artists','Outside the United States']),
 nl('AAA','A5','American Abstract Artists','narrow','Members of American Abstract Artists, the New York association founded in 1936 to promote abstract art: e.g. Burgoyne Diller, Gertrude Greene, George L. K. Morris, Alice Trumbull Mason.',
    W+'American_Abstract_Artists',
    [['https://americanabstractartists.org/','American Abstract Artists','the association\'s own site with member history'],
     ['https://www.aaa.si.edu/','Archives of American Art','papers of AAA members']],
    'founding members (1936–37) first, then the Park Avenue Cubists and later members; within a group by birth',
    ['Founding members (1936–37)','Park Avenue Cubists and later members']),
]
out = {'leaves': leaves, 'new_leaves': NL, 'moves_out': S['moves'], 'dropped': S['dropped']}
json.dump(out, open('result.json', 'w'), ensure_ascii=False, indent=1)
print(len(kinds), cnt.most_common(6), sum(len(n['kinds']) for n in NL))
