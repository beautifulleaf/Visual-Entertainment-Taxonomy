"""Build the television coverage-pass outputs (run: python3 build.py)."""
import csv, json, os
R = '/home/user/Visual-Entertainment-Taxonomy/'
OUT = os.path.dirname(os.path.abspath(__file__))
csv.field_size_limit(10**9)
placed = {r['id']: r for r in csv.DictReader(open(R+'taxonomy/r3/ft_title_index.tsv'), delimiter='\t')}
cand = {r['tconst']: r for r in csv.DictReader(open(R+'data/interim/tv_candidates.csv'))}
rat = {r['tconst']: r for r in csv.DictReader(open(R+'data/interim/tv_ratings.csv'))}

W = 'https://en.wikipedia.org/wiki/'
NEW = [
 dict(key='NEW_GOLDEN', sub='B1', label='Golden Age Anthology Drama',
      breadth='cycle (US, 1947–1961)',
      defn='A sponsor-titled American anthology drama of the first Golden Age of Television (c. 1947–1961): a new self-contained teleplay each week, broadcast live from New York or Hollywood (Kraft Television Theatre, Studio One, The Philco Television Playhouse, Playhouse 90) or, later in the decade, filmed in Hollywood (General Electric Theater, Schlitz Playhouse). Later anthologies stay in B1-29 Anthology Drama.',
      aliases='live anthology drama; Golden Age of Television', see='B1-29',
      src=[[W+'Golden_Age_of_Television', 'Wikipedia'], [W+'Anthology_series', 'Wikipedia']],
      axis='production mode', secs=['Live Anthologies', 'Filmed Anthologies']),
 dict(key='NEW_BIZ', sub='B14', label='Business Reality Television',
      breadth='genre',
      defn='Factual entertainment built around running or financing a business: entrepreneurs pitching to investors, experts rescuing failing restaurants, bars and hotels, bosses going undercover, and dealers trading, pawning and buying at auction (Dragons\' Den, Kitchen Nightmares, Bar Rescue, Undercover Boss, Pawn Stars).',
      aliases='business reality TV', see='B13-4; B14-2',
      src=[[W+'Reality_television#Business_improvement', 'Wikipedia (Reality television: Business improvement)'], ['taxonomy/r3/imdb_interests.tsv', 'IMDb interest: Business Reality TV']],
      axis='premise', secs=['Pitch & Investment Shows', 'Business Rescue & Turnaround Shows', 'Undercover Boss Shows', 'Pawn, Picking & Auction Shows']),
 dict(key='NEW_PROP', sub='B14', label='Property & Home Improvement Television',
      breadth='genre',
      defn='Lifestyle television about buying, selling, building and renovating homes: house-hunting and relocation shows, renovation and flipping shows, self-build and design series, and luxury real-estate docusoaps (Location, Location, Location, House Hunters, Grand Designs, Fixer Upper, Selling Sunset). One-off makeovers of a home as a gift stay in B14-4 Makeover Show.',
      aliases='property television; home improvement television; HGTV-style renovation shows', see='B14-4',
      src=[[W+'Reality_television#Renovation', 'Wikipedia (Reality television: Renovation)'], ['taxonomy/r3/imdb_interests.tsv', 'IMDb interest: Home Improvement']],
      axis='premise', secs=['House-Hunting & Relocation', 'Renovation, Flipping & DIY', 'Self-Build & Design', 'Real-Estate Agents & Luxury Listings']),
 dict(key='NEW_CRIME', sub='B14', label='Crime & Law-Enforcement Reality',
      breadth='genre',
      defn='Reality television that follows police, border, custody and prison officers, bounty hunters and investigators at work, filmed on ride-alongs, in custody suites and in stings (Cops, Live PD, Border Security, 24 Hours in Police Custody, Dog the Bounty Hunter). Documentary investigations of past cases go to B11-11 True Crime Docuseries.',
      aliases='crime reality TV; police reality; first-responder reality', see='B11-11; B14-9',
      src=[[W+'Reality_television#First_responder_reality_style', 'Wikipedia (Reality television: Professional activities / first responder reality)'], ['taxonomy/r3/imdb_interests.tsv', 'IMDb interest: Crime Reality TV']],
      axis='setting', secs=['Ride-Along & Patrol Reality', 'Border, Custody & Prison Reality', 'Investigation & Sting Reality', 'Bounty Hunting & Manhunts']),
 dict(key='NEW_NEWS', sub='B11', label='News & Current Affairs Programmes',
      breadth='genre',
      defn='Regularly scheduled journalism programmes: investigative newsmagazines and current-affairs strands, political interview and debate programmes, breakfast television, evening newscasts, cable news and opinion shows, and tabloid and entertainment news magazines (60 Minutes, Panorama, Meet the Press, Today, PBS NewsHour, Entertainment Tonight).',
      aliases='newsmagazine; current affairs; breakfast television', see='B11-10; B15-3',
      src=[[W+'Newsmagazine', 'Wikipedia'], [W+'Current_affairs_(news_format)', 'Wikipedia'], [W+'Breakfast_television', 'Wikipedia'], ['taxonomy/r3/imdb_interests.tsv', 'IMDb interest: News']],
      axis='programme form', secs=['Newsmagazines & Investigative Current Affairs', 'Political Interview & Debate Programmes', 'Breakfast & Morning Television', 'Evening Newscasts', 'Cable News & Opinion Shows', 'Tabloid & Entertainment News']),
 dict(key='NEW_SINETRON', sub='B12', label='Sinetron',
      breadth='national tradition (Indonesia)',
      defn='The Indonesian television serial (sinema elektronik): long-running daily or weekly family, romance, religious and comedy serials of the private networks RCTI, SCTV and Indosiar (Si Doel Anak Sekolahan, Para Pencari Tuhan, Ikatan Cinta).',
      aliases='sinema elektronik', see='B12-4',
      src=[[W+'Sinetron', 'Wikipedia']]),
]
NEW_SECTIONS = [('B9-17', 'Steampunk & Gaslamp Fantasy')]

RESECT = {
 'B1-1': dict(axis='era of the prestige-TV cycle', secs=['Third Golden Age: Cable Prestige (1999–2012)', 'Peak TV & Streaming Era (2013–)'],
              assign={'tt0248654':1,'tt0421030':1,'tt0804503':1,'tt2183404':2,'tt2699128':2,'tt4270492':2,'tt9612102':2}),
 'B15-1': dict(axis='era', secs=['Golden Age Variety (1948–1960)', 'Network Variety Hours (1961–1979)', 'Post-Network & International Variety (1980–)'],
              assign={'tt0040053':1,'tt0043224':1,'tt0048899':1,'tt0054522':2,'tt0056748':2,'tt0065294':2,'Q666799':3,'tt0090515':3,'tt12060448':3,'tt0103363':3,'tt0202741':3,'tt0461622':3,'tt8425308':3,'tt9663964':3}),
 'B14-8': dict(axis='subject taught', secs=['Cooking Shows', 'Art, Craft & Hobby Instruction', 'Know-How, Science & Collecting'],
              assign={'Q3052933':3,'tt0383795':2,'tt0313033':2,'tt0344651':1,'Q486844':3,'tt8772088':1,'tt8773080':2,'tt10359446':1}),
 'B14-7': dict(axis='premise', secs=['Motoring & Road-Trip Shows', 'Comic & Celebrity Travel Shows', 'Survival & Wilderness Shows'],
              assign={'tt1628033':1,'tt0389701':2,'tt1248967':1,'tt9620768':3,'tt3816666':3,'tt5020352':2,'tt5712554':1,'tt9170584':2,'tt27790101':2}),
 'B14-6': dict(axis='premise', secs=['Ghost-Hunting Investigations', 'Mediums & Psychics', 'Cryptid & Monster Hunts'],
              assign={'tt0426697':1,'tt0785036':1,'tt5435072':1,'tt10589968':3}),
}

MOVES = [  # id, to, sec, note
 *[(i,'NEW_GOLDEN',s,'Golden Age anthology, from B1-29') for i,s in [('tt0040021',1),('tt0040049',1),('tt0040051',1),('tt0042141',1),('tt0044266',1),('tt0044248',2),('tt0045449',1),('tt0046637',1),('tt0048893',1)]],
 ('Q2579158','NEW_BIZ',1,'Dragons\' Den format (incl. Shark Tank), from B13-4'),
 ('tt1442553','NEW_BIZ',3,'from B14-3'),
 ('Q1538095','NEW_BIZ',2,'Kitchen Nightmares format, from B14-4'),
 ('Q1548487','NEW_PROP',3,'from B14-4'),
 ('Q610525','NEW_PROP',1,'from B14-4'),
 ('Q797907','NEW_CRIME',1,'from B14-2'),
 ('tt0096563','NEW_CRIME',1,'from B14-2'),
 ('Q11888566','NEW_CRIME',1,'from B14-2'),
 ('tt0424627','NEW_CRIME',4,'from B14-2'),
 ('tt27612322','NEW_CRIME',4,'from B14-2'),
 ('tt12187604','B12-10','','Sri Lankan teledrama, from B1-5'),
 ('tt14544908','B12-10','','Sri Lankan teledrama, from B8-2'),
 ('tt0489974','B9-17','Steampunk & Gaslamp Fantasy','re-section within leaf'),
 ('tt8697870','B9-17','Steampunk & Gaslamp Fantasy','re-section within leaf'),
]

ADDS = {  # (to, sec): [ids]
 ('NEW_GOLDEN',1): 'tt0039123 tt0043204 tt0042123 tt0046587 tt0047756 tt0042074',
 ('NEW_GOLDEN',2): 'tt0045395 tt0043228 tt0041023 tt0044263 tt0051328 tt0047768 tt0045409 tt0046648',
 ('NEW_BIZ',1): 'tt3788022',
 ('NEW_BIZ',2): 'tt3080030 tt1863526 tt1771742 tt2242025 tt2129304 tt1183335 tt1272837 tt7768166',
 ('NEW_BIZ',4): 'tt1492088 tt1785123 tt1596786',
 ('NEW_PROP',1): 'tt0341864 tt0369117 tt0795129 tt0390700 tt0300839 tt3869500',
 ('NEW_PROP',2): 'tt0419336 tt1827882 tt4591390 tt2902088 tt0476041 tt0078701 tt0765621 tt2107314 tt6666966 tt6249614 tt0418372',
 ('NEW_PROP',3): 'tt3321546',
 ('NEW_PROP',4): 'tt9817298 tt0815063 tt2238348',
 ('B14-4',2): 'tt0216467 tt0278249 tt0189251 tt0213345 tt3002170',
 ('NEW_CRIME',1): 'tt6225166 tt20883058 tt0411021 tt1397259 tt3276004 tt0155394 tt1531068 tt4287464 tt1506191',
 ('NEW_CRIME',2): 'tt0439351 tt4116046 tt0446847 tt1128727 tt1707374',
 ('NEW_CRIME',3): 'tt3694654 tt2402569 tt20318388',
 ('B14-6',1): 'tt1319900 tt0362355 tt1122725 tt2012511 tt5512658 tt6181672 tt6155068 tt1690621 tt3967028 tt10813648 tt1526818 tt1873887 tt1472386',
 ('B14-6',2): 'tt2010806 tt5271054',
 ('B14-6',3): 'tt0941372 tt1948830 tt3019170',
 ('B11-12',''): 'tt1320080 tt1170243 tt4355188 tt2740518',
 ('B14-9',''): 'tt0081916 tt0123357 tt0282291 tt0235927 tt0346307 tt3953642 tt3854942 tt0445120 tt3226310 tt0346306 tt15306330 tt3960750 tt2361632',
 ('B15-5',''): 'tt1405257 tt1454441 tt0352110 tt1198300 tt0944181',
 ('B14-7',1): 'tt0163503',
 ('B14-7',3): 'tt0883772 tt0770659 tt1673441 tt4633666 tt5141658 tt1695353',
 ('B14-8',1): 'tt0163936 tt0169499 tt0273002 tt0783322 tt0285390 tt0337534 tt1724448 tt0294085 tt0966554 tt0298633 tt0364805 tt1057604 tt0282298 tt1842155 tt0758722',
 ('B14-8',2): 'tt0185087',
 ('B14-8',3): 'tt0260618',
 ('NEW_NEWS',1): 'tt0123338 tt0309123 tt0124932 tt0103396 tt0271894 tt0199257 tt0181269 tt0983197 tt0133302 tt2782710 tt1043090 tt0169446 tt0196301 tt0477545 tt0096680',
 ('NEW_NEWS',2): 'tt0149490 tt0267212 tt0163471 tt0386208 tt0481456 tt0045431 tt0088550',
 ('NEW_NEWS',3): 'tt0044298 tt0072506 tt2163227 tt0428169 tt3644198 tt1170244',
 ('NEW_NEWS',4): 'tt0231035 tt0247880 tt0246393 tt0229153',
 ('NEW_NEWS',5): 'tt0380086 tt1280627 tt1500570 tt6238614 tt0284767',
 ('NEW_NEWS',6): 'tt0166442 tt0096605 tt0190177 tt0081857 tt0167515 tt1095213',
 ('NEW_SINETRON',''): 'tt0331786 tt1998808 tt10995120 tt13984562',
 ('B12-10',''): 'tt10022848 tt10295228 tt8837006',
 ('B12-3',''): 'tt1612716 tt6340304 tt5676412 tt3275706 tt3518272 tt3904068 tt1585368 tt1527368 tt6607810 tt10367818',
 ('B12-1',1): 'tt0211866 tt0130410 tt1705090',
 ('B12-1',2): 'tt0217193 tt0224974 tt0320925',
 ('B12-1',3): 'tt0327759',
 ('B12-1',4): 'tt0191705',
 ('B12-8',''): 'tt2452062 tt5700398 tt0853973 tt0397214 tt7453862 tt0294139 tt5328326 tt30145246 tt8437668',
 ('B7-7',''): 'tt0088621 tt1830332',
 ('B10-2',''): 'tt0043244 tt0085060 tt0190169 tt0191731 tt0143080',
 ('B9-17','Steampunk & Gaslamp Fantasy'): 'tt0112045 tt0178161',
 ('B15-1',1): 'tt0042173 tt0042094 tt0040041 tt0040048 tt0044272 tt0051276 tt0043192 tt0044262',
 ('B15-1',2): 'tt0061296 tt0058797 tt0056767 tt0063908 tt0063930 tt0057755 tt0063902 tt0063919 tt0055660',
 ('B15-1',3): 'tt0250920 tt0316977',
}

def info(i):
    c = cand.get(i); r = rat.get(i, {})
    if c: return c['title'], c['start_year'], r.get('country', '')
    if r: return r['mdblist_title'], r['start_year'] or r['year'], r.get('country', '')
    raise SystemExit('no info for ' + i)

json.dump(NEW, open(os.path.join(OUT, 'new_leaves.json'), 'w'), ensure_ascii=False, indent=1)
with open(os.path.join(OUT, 'new_sections.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['leaf', 'label']); w.writerows(NEW_SECTIONS)
with open(os.path.join(OUT, 'moves.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['id', 'to', 'sec', 'note']); w.writerows(MOVES)
n = 0
with open(os.path.join(OUT, 'adds.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['id', 'title', 'year', 'who', 'kind', 'to', 'sec', 'note'])
    for (to, sec), ids in ADDS.items():
        for i in ids.split():
            t, y, c = info(i); w.writerow([i, t, y, c, 'tv', to, sec, '']); n += 1
# resections must cover every title of the leaf
for leaf, rs in RESECT.items():
    have = {k for k, r in placed.items() if r['leaf'] == leaf}
    assert have == set(rs['assign']), (leaf, have ^ set(rs['assign']))
json.dump(RESECT, open(os.path.join(OUT, 'resections.json'), 'w'), ensure_ascii=False, indent=1)
print('adds', n, 'moves', len(MOVES))
