from common import *

BF_TO_RF = ['Kleophrades Painter', 'Oltos', 'Euxitheos', 'Brygos', 'Brygos Painter', 'Onesimos', 'Douris', 'Makron', 'Hieron', 'Epiktetos', 'Euergides Painter', 'Myson', 'Peithinos', 'Triptolemos Painter',
    'Berlin Painter', 'Skythes', 'Kachrylion', 'Syriskos Painter', 'Ambrosios Painter', 'Pasiades Painter', 'Elpinikos Painter', 'Thaliarchos Painter', 'Epeleios Painter', 'Goluchow Painter', 'Bowdoin-Eye Painter',
    'Dikaios Painter', 'Hermaios Painter', 'Chelis Painter', 'Hischylos Painter', 'Salting Painter', 'Gales Painter', 'Winchester Painter', 'Painter of London E 33', 'Painter of Louvre G 36', 'Paseas', 'Pheidippos', 'Hypsis']
RF_TO_BF = ['Exekias', 'Haimon Painter', 'Beldam Painter']

BF_GROUPS = [
    ('Protoattic and early Attic black-figure', ['Polyphemos Painter', 'Ram Jug Painter', 'Mesogeia Painter', 'Painter of Berlin A 34', 'Lion Painter', 'Bellerophon Painter', 'Piraeus Painter', 'Nessos Painter', 'Cerameicus Painter', 'Gorgon Painter']),
    ('Komast Group, Sophilos and Kleitias', ['KX Painter', 'KY Painter', 'Sophilos', 'Kleitias', 'Ergotimos']),
    ('Siana cups and Tyrrhenian amphorae', ['C Painter', 'Heidelberg Painter', 'Griffin-Bird Painter', 'Castellani Painter', 'Goltyr Painter', 'Camtar Painter', 'Tityos Painter', 'Painter of the Dresden Lekanis', 'Ptoon Painter', 'Polos Painter', 'Timenor']),
    ('Lydos and the mid-6th-century workshops', ['Nearchos', 'Lydos', 'Painter of Acropolis 606', 'Painter of London B 76']),
    ('Little-master cups', ['Tleson', 'Tleson Painter', 'Xenocles', 'Xenokles Painter', 'Hermogenes', 'Sakonides', 'Phrynos', 'Phrynos Painter', 'Glaukytes', 'Hischylos', 'Taleides Painter', 'Ergoteles', 'Eucheiros', 'Anakles', 'Sokles', 'Elbows Out']),
    ('Amasis Painter, Exekias and Group E', ['Amasis Painter', 'Exekias', 'Painter of the Vatican Mourner', 'Painter of Berlin 1686', 'Swing Painter', 'Princeton Painter', 'Affecter', 'Painter of Munich 1410']),
    ('Bilingual workshop of Andokides and Psiax', ['Andokides', 'Andokides painter', 'Lysippides Painter', 'Psiax', 'Menon']),
    ('Nikosthenes and Pamphaios workshop', ['Nikosthenes', 'Nikosthenes Painter', 'BMN Painter', 'Pamphaios']),
    ('Leagros Group and the Antimenes Painter (late 6th century)', ['Antimenes Painter', 'Euphiletos Painter', 'Acheloos Painter', 'Priam Painter', 'Rycroft Painter', 'Madrid Painter', 'Painter of Louvre F6', 'Daybreak Painter', 'Timagoras', 'Mastos Painter']),
    ('Late black-figure (5th century)', ['Eucharides Painter', 'Nikoxenos Painter', 'Edinburgh Painter', 'Sappho Painter', 'Diosphos Painter', 'Athena Painter', 'Theseus Painter', 'Haimon Painter', 'Marathon Painter', 'Beldam Painter', 'Pithos Painter', 'Gela Painter', 'Painter of the Nicosia Olpe', 'Michigan Painter']),
    ('Chalcidian black-figure', ['Inscription Painter']),
    ('Potters known from signatures', ['Charinus', 'Hypereides', 'Gryton', 'Paidikos', 'Gales', 'Hermaios', 'Pasiades', 'Sikelos', 'Chelis', 'Sosias', 'Python', 'Pythokles Painter']),
]
BF_MOVES = {'Chares': 'E1-26', 'Timonidas': 'E1-26', 'Cavalcade Painter': 'E1-26', 'Columbus Painter': 'E1-26', 'Shambling Bull Painter': 'E1-26', 'Painter of Palermo 489': 'E1-26', 'Panther Painter': 'E1-26',
            'Painter of Vatican 73': 'E1-26', 'Duel Painter': 'E1-26', 'Butades': 'E1-26', 'Painter of Toronto 919.5.110': 'E1-26', 'Honolulu Painter': 'E1-26', 'Bearded Sphinx Painter': 'E1-34',
            'Naucratis Painter': 'E1-29', 'Hunt Painter': 'E1-29', 'Rider Painter': 'E1-29', 'Arkesilas Painter': 'E1-29', 'Boreads painter': 'E1-29'}

RF_GROUPS = [
    ('Bilingual vase painting', []),
    ('Early red-figure cup painters (Oltos, Epiktetos)', ['Oltos', 'Epiktetos', 'Skythes', 'Paseas', 'Pheidippos', 'Euergides Painter', 'Kachrylion', 'Euxitheos', 'Peithinos', 'Chelis Painter', 'Hischylos Painter', 'Bowdoin-Eye Painter',
        'Ambrosios Painter', 'Elpinikos Painter', 'Thaliarchos Painter', 'Hermaios Painter', 'Epeleios Painter', 'Salting Painter', 'Gales Painter', 'Pasiades Painter', 'Goluchow Painter', 'Winchester Painter',
        'Painter of London E 33', 'Painter of Louvre G 36', 'Apollodoros']),
    ('Pioneer Group', ['Euphronios', 'Euthymides', 'Phintias', 'Smikros', 'Hypsis', 'Sosias Painter', 'Dikaios Painter']),
    ('Late Archaic masters (Kleophrades, Berlin, Brygos, Douris, Makron, Onesimos)', ['Kleophrades Painter', 'Berlin Painter', 'Myson', 'Onesimos', 'Brygos', 'Brygos Painter', 'Foundry Painter', 'Dokimasia Painter',
        'Antiphon Painter', 'Douris', 'Makron', 'Hieron', 'Triptolemos Painter', 'Syriskos Painter', 'Hegesiboulos Painter']),
    ('Mannerists', ['Pan Painter', 'Pig Painter', 'Nausicaa Painter']),
    ('Early Classical (Niobid, Pistoxenos, Penthesilea)', ['Niobid Painter', 'Altamura Painter', 'Pistoxenos Painter', 'Penthesilea Painter', 'Sotades', 'M Potter', 'Hermonax', 'Providence Painter', 'Tarquinia Painter', 'Mannheim Painter', 'Florence Painter', 'Carlsruhe Painter']),
    ('High Classical (Achilles, Polygnotos, Kleophon)', ['Achilles Painter', 'Phiale Painter', 'Reed Painter', 'Polygnotos', 'Kleophon Painter', 'Dinos Painter', 'Eretria Painter', 'Washing Painter', 'Shuvalov Painter', 'Codrus Painter', 'Polion', 'Aison']),
    ('Rich style and Kerch style (late 5th–4th century)', ['Meidias', 'Meidias Painter', 'Aristophanes', 'Nikias', 'Nikias Painter', 'Pronomos Painter', 'Meleager Painter', 'Jena Painter', 'Painter of the Wedding Procession', 'Marsyas Painter', 'Xenophantos']),
    ('Lucanian red-figure', ['Pisticci Painter', 'Amycus Painter', 'Choephoroi Painter']),
    ('Apulian red-figure', ['Painter of the Berlin Dancing Girl', 'Tarporley Painter', 'Sisyphus Painter', 'Lucera Painter', 'Ilioupersis Painter', 'Lycurgus Painter', 'Varrese Painter', 'Darius Painter', 'Underworld Painter',
        'Baltimore Painter', 'White Saccos Painter', 'Ganymede Painter', 'Armidale Painter']),
    ('Campanian red-figure', ['Kassandra Painter', 'Parrish Painter']),
    ('Paestan red-figure', ['Asteas', 'Python']),
    ('South Italian red-figure (other workshops)', ['Aphrodite Painter', 'Painter of the Boston Orest', 'Loebbecke Painter']),
    ('Other ancient craftspeople in the data', ['Sellia Epyre']),
]
RF_MOVES = {'Micali Painter': 'E1-34', 'Nazzano Painter': 'E1-34', 'Novius Plautius': 'G1-25', 'Sosus of Pergamon': 'L3-6', 'Dioscorides of Samos': 'L3-6', 'Chimaera Painter': 'E1-26'}

def merged(code, extra_from, names):
    l = dict(LEAVES[code])
    l['rows'] = [r for r in LEAVES[code]['rows'] if r[0] not in names[0]] + [r for r in LEAVES[extra_from]['rows'] if r[0] in names[1]]
    return l

def vgloss(r):
    e = ev(r); b = e.get('birth', '')
    g = ''
    if b.startswith('-'):
        g = 'active c. %s BC' % (int(b[1:]) - 0)
    if r[2] and not r[2].startswith('movement') and 'Archaic Greek sculpture' not in r[2] and not r[2].startswith('Q'):
        pass
    return g

def build(out):
    # Black-figure: drop RF painters (sent to E1-28), add BF painters found in E1-28
    pyth_bf = True
    bf = dict(LEAVES['E1-27'])
    bf['rows'] = [r for r in LEAVES['E1-27']['rows'] if r[0] not in BF_TO_RF or r[0] == 'Python'] + [r for r in LEAVES['E1-28']['rows'] if r[0] in RF_TO_BF]
    rf = dict(LEAVES['E1-28'])
    rf['rows'] = [r for r in LEAVES['E1-28']['rows'] if r[0] not in RF_TO_BF] + [r for r in LEAVES['E1-27']['rows'] if r[0] in BF_TO_RF and r[0] != 'Python']
    gl = {}
    for l in (bf, rf):
        for r in l['rows']:
            b = ev(r).get('birth', '')
            if b.startswith('-'):
                gl[r[0]] = 'active c. %s BC' % b[1:]
    gbf = dict(gl); gbf['Python'] = 'Attic potter of Douris\'s cups, c. 500–470 BC'
    k = []
    for r in LEAVES['E1-27']['rows']:
        if r[0] == 'Protoattic':
            k.append(['Protoattic', 'Sub-types', 'Athenian orientalising pottery of c. 700–630 BC, the forerunner of Attic black-figure', r[3], 0])
        if r[0] == 'Boeotian black-figure':
            k.append(['Boeotian black-figure', 'Sub-types', 'black-figure of Boeotia, including the Kabeiric ware of Thebes', r[3], 0])
    add(k, 'Sub-types', [('Corinthian vase painting', 'the first black-figure, Corinth c. 700–550 BC (own leaf)', wp('Corinthian vase painting')),
                         ('Laconian vase painting', 'Spartan black-figure, c. 620–500 BC (own leaf)', wp('Laconian vase painting')),
                         ('Chalcidian vase painting', 'black-figure of Chalcidian type, probably made at Rhegion, c. 560–510 BC', wp('Chalcidian vase painting')),
                         ('Caeretan hydria', 'hydriai made by East Greek immigrant painters at Caere, c. 530–510 BC', wp('Caeretan hydria')),
                         ('Panathenaic amphora', 'prize amphorae of the Panathenaic Games, kept in black-figure into the Hellenistic period', wp('Panathenaic amphora')),
                         ('Little-master cup', 'fine Attic cups with miniature friezes, c. 560–530 BC', wp('Little-master cup')),
                         ('Siana cup', 'early Attic black-figure cup type, c. 575–550 BC', wp('Siana cup')),
                         ('Tyrrhenian amphora', 'Attic black-figure ovoid amphorae made for Etruria, c. 565–550 BC', wp('Tyrrhenian amphorae')),
                         ('Six\'s technique', 'variant in which figures are painted over the black gloss in added colour', wp("Six's technique"))])
    add(k, 'Named vases', [('François Vase (Kleitias and Ergotimos, c. 570 BC)', 'Attic black-figure volute krater; Museo Archeologico Nazionale, Florence', wp('François Vase')),
                           ('Dionysus Cup (Exekias, c. 530 BC)', 'eye cup with Dionysus\'s ship; Staatliche Antikensammlungen, Munich', wp('Dionysus Cup')),
                           ('Eleusis Amphora (Polyphemos Painter, c. 670 BC)', 'Protoattic amphora with the blinding of Polyphemos; Archaeological Museum of Eleusis', wp('Eleusis Amphora'))])
    k += [x if x[1] != 'Country not recorded' else x[:1] + ['Other named black-figure hands'] + x[2:] for x in assign(bf, BF_GROUPS, BF_MOVES, glosses=gbf)]
    out['leaves']['E1-27'] = dict(
        axis='sub-types and fabrics first, then the named vases, then Attic painters and potters by workshop and phase as Beazley grouped them (Protoattic and early, Komast Group, Siana and Tyrrhenian, Lydos, Little Masters, Amasis and Exekias, Andokides–Psiax, Nikosthenes, Leagros Group, late black-figure), then potters known from signatures; Corinthian and Laconian painters moved to their own leaves, red-figure cup painters to Red-Figure Pottery',
        catalogues=[['https://www.beazley.ox.ac.uk/carc/pottery', 'Beazley Archive Pottery Database', 'over 120,000 Athenian figure-decorated vases, searchable by painter, shape and technique'],
                    ['https://www.cvaonline.org/cva/', 'Corpus Vasorum Antiquorum online', 'the CVA fascicules of Greek vases by museum'],
                    ['https://www.britishmuseum.org/collection/search?keyword=black-figured', 'British Museum collection: black-figured', 'the BM\'s black-figured vases'],
                    ['https://www.metmuseum.org/art/collection/search?q=black-figure', 'The Met collection: black-figure', 'black-figure vases at the Met']],
        kinds=k)
    k = []
    for r in LEAVES['E1-28']['rows']:
        if r[0] == 'bilingual vase painting':
            k.append(['Bilingual vase painting', 'Sub-types', 'Attic vases c. 530–500 BC with one side black-figure and the other red-figure', r[3], 0])
    add(k, 'Sub-types', [('White-ground technique', 'Attic outline drawing on a white slip, above all on funerary lekythoi, from c. 500 BC', wp('White-ground technique')),
                         ('Kerch style', 'late Attic red-figure of the 4th century BC with added colour, named after finds at Kerch', wp('Kerch style')),
                         ('Apulian vase painting', 'the largest South Italian red-figure fabric, c. 430–300 BC', wp('Apulian vase painting')),
                         ('Lucanian vase painting', 'the first South Italian red-figure fabric, from c. 440 BC', wp('Lucanian vase painting')),
                         ('Campanian vase painting', 'red-figure of Campania, c. 380–300 BC', wp('Campanian vase painting')),
                         ('Paestan vase painting', 'red-figure of Paestum, led by Asteas and Python', wp('Paestan vase painting'))])
    add(k, 'Named vases', [('Euphronios Krater (Euphronios, c. 515 BC)', 'calyx krater with the death of Sarpedon; Museo Nazionale Etrusco di Villa Giulia, Rome', wp('Euphronios krater')),
                           ('Vivenzio Hydria (Kleophrades Painter, c. 480 BC)', 'hydria with the sack of Troy; Museo Archeologico Nazionale, Naples', wp('Vivenzio Hydria')),
                           ('Berlin Foundry Cup (Foundry Painter, c. 490 BC)', 'kylix with a bronze foundry; Antikensammlung, Berlin', wp('Berlin Foundry Cup')),
                           ('Eurymedon vase (c. 460 BC)', 'oinochoe alluding to the battle of the Eurymedon; Museum für Kunst und Gewerbe, Hamburg', wp('Eurymedon vase')),
                           ('Niobid Krater (Niobid Painter, c. 460 BC)', 'calyx krater with Herakles and the Niobids; Louvre, Paris', wp('Niobid Krater')),
                           ('Pronomos Vase (Pronomos Painter, c. 400 BC)', 'volute krater with a satyr-play cast; Museo Archeologico Nazionale, Naples', wp('Pronomos Vase')),
                           ('Darius Vase (Darius Painter, c. 340 BC)', 'Apulian volute krater with the council of Darius; Museo Archeologico Nazionale, Naples', wp('Darius Vase'))])
    gl['Sellia Epyre'] = 'Roman gold-embroiderer known from an inscription; not a vase painter'
    gl['Python'] = 'Paestan red-figure painter, partner of Asteas, c. 360–330 BC'
    k += [x if x[1] != 'Country not recorded' else x[:1] + ['Other named red-figure hands'] + x[2:] for x in assign(rf, RF_GROUPS, RF_MOVES, glosses=gl)]
    out['leaves']['E1-28'] = dict(
        axis='sub-types and fabrics, then named vases, then Attic painters by Beazley\'s phases and groups (early cup painters, Pioneer Group, Late Archaic masters, Mannerists, Early Classical, High Classical, Rich and Kerch styles), then South Italian painters by fabric (Lucanian, Apulian, Campanian, Paestan); black-figure painters moved to Black-Figure Pottery, Etruscan painters to their leaf',
        catalogues=[['https://www.beazley.ox.ac.uk/carc/pottery', 'Beazley Archive Pottery Database', 'over 120,000 Athenian figure-decorated vases, searchable by painter, shape and technique'],
                    ['https://www.cvaonline.org/cva/', 'Corpus Vasorum Antiquorum online', 'the CVA fascicules of Greek vases by museum'],
                    ['https://www.britishmuseum.org/collection/search?keyword=red-figured', 'British Museum collection: red-figured', 'the BM\'s red-figured vases'],
                    ['https://www.metmuseum.org/art/collection/search?q=red-figure', 'The Met collection: red-figure', 'red-figure vases at the Met']],
        kinds=k)

DESC = {'Potters known from signatures': 'Attic potter known from signatures', 'Chalcidian black-figure': 'Chalcidian black-figure painter',
        'Lucanian red-figure': 'Lucanian red-figure painter', 'Apulian red-figure': 'Apulian red-figure painter', 'Campanian red-figure': 'Campanian red-figure painter',
        'Paestan red-figure': 'Paestan red-figure painter', 'South Italian red-figure (other workshops)': 'South Italian red-figure painter'}
_build = build
def build(out):
    _build(out)
    for code, tech in (('E1-27', 'black-figure'), ('E1-28', 'red-figure')):
        for x in out['leaves'][code]['kinds']:
            if x[4] != 1:
                continue
            if x[1] in ('Classical Athens', 'Other named black-figure hands', 'Other named red-figure hands'):
                x[1] = 'Other named Attic hands'
            if x[0] in ('Python', 'Sellia Epyre'):
                continue
            pot = x[0] in ('Ergotimos', 'Nikosthenes', 'Pamphaios', 'Andokides', 'Timagoras', 'Hieron', 'Brygos', 'Euxitheos', 'Kachrylion', 'Sotades', 'Meidias', 'Nikias', 'Xenophantos', 'M Potter', 'Tleson', 'Xenocles', 'Hermogenes', 'Glaukytes', 'Hischylos', 'Ergoteles', 'Eucheiros', 'Anakles', 'Sokles', 'Menon')
            d = DESC.get(x[1]) or ('Attic %s %s' % (tech, 'potter' if pot else 'painter'))
            x[2] = d + ('; ' + x[2] if x[2] and not x[2].startswith('active c.') else '')
