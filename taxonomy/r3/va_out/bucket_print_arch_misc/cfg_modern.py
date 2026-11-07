from common import *
from arch import works, architect_info, arch_gloss
from arch_cfg import substyles, UNESCO, cat
import re

# style labels (architects csv / exemplar tags) -> named group, in priority order
K622_STYLE = [
    ('Metabolism', ['Metabolism']),
    ('De Stijl', ['De Stijl', 'neoplasticism']),
    ('Amsterdam School', ['Amsterdam School']),
    ('New Hague School', ['New Hague School']),
    ('Purism', ['purism']),
    ('Neues Bauen and Nieuwe Zakelijkheid (New Objectivity)', ['Neues Bauen', 'New Objectivity', 'Nieuwe Zakelijkheid']),
    ('Functionalism', ['functionalism']),
    ('Italian Rationalism (Como group)', ['Rationalism of Lake Como', 'rationalism']),
    ('Noucentisme', ['Noucentisme']),
    ('Organic architecture', ['organic architecture', 'anthroposophic architecture']),
    ('Usonian architecture (Taliesin Fellowship)', ['Usonian architecture']),
    ('Brazilian modernism', ['Modernist architecture in Brazil']),
    ('Structuralism', ['structuralism']),
    ('Brussels style (Expo 58)', ['Brussels style', 'expo style']),
    ('Bienne modernism', ['Bienne modernism']),
    ('New Formalism', ['New Formalism']),
    ('Soviet Modernism', ['Soviet Modernist architecture', 'neoconstructivism']),
]
K622_GROUPS = [
    ('Metabolism', ['Kiyonori Kikutake', 'Masato Otaka', 'Arata Isozaki']),
    ('Organic architecture', ['Imre Makovecz', 'Douglas Cardinal', 'Reima Pietilä', 'Raili Pietilä', 'Jan Wils']),
    ('Neo-Liberty', ['Roberto Gabetti', 'Aimaro Isola', 'Gae Aulenti']),
    ('Grup R (Barcelona)', ['Josep Antoni Coderch', 'Antoni de Moragas i Gallissà', 'Josep Maria Martorell i Codina', 'Oriol Bohigas', 'Manuel Ribas i Piera']),
    ('Escuela de Madrid', ['Javier Carvajal Ferrer', 'Antonio Fernández Alba', 'Fernando Higueras', 'Antonio Lamela', 'Rafael Moneo']),
    ('Porto School', ['Fernando Távora', 'Álvaro Siza Vieira']),
    ('Ticino School', ['Mario Botta', 'Luigi Snozzi', 'Bruno Reichlin']),
    ('Italian Radical architecture (Superstudio, Archizoom, Gruppo Strum)', ['Adolfo Natalini', 'Cristiano Toraldo di Francia', 'Andrea Branzi', 'Paolo Deganello', 'Pietro Derossi', 'Giorgio Ceretti', 'Alessandro Mendini']),
    ('Visionary and experimental architecture (Archigram, Haus-Rucker-Co, GIAP)', ['Yona Friedman', 'Michael Webb', 'Cedric Price', 'Günter Zamp Kelp', 'Laurids Ortner', 'Raimund Abraham', 'Friedrich St. Florian', 'James Wines', 'Luc Deleu', 'Matti Suuronen']),
    ('Yugoslav modernism', ['Zlatko Ugljen', 'Ivan Štraus', 'Andrija Mutnjaković', 'Boris Magaš', 'Hrvoje Šarinić', 'Dinko Kovačić', 'Stanko Kristl', 'Milan Mihelič', 'Savin Sever', 'Mihajlo Mitrović', 'Uglješa Bogunović', 'Ivan Antić', 'Aleksandar Đokić', 'Marko Mušič', 'Svetlana Kana Radević', 'Boris Podrecca']),
    ('Soviet Modernism', ['Raine Karp', 'Yuriy Khimich', 'Andrey Bokov', 'Sabir Rakhimovich Adylov']),
    ('Critical regionalism and regional modernisms', ['Glenn Murcutt', 'Charles Correa', 'Raj Rewal', 'Muzharul Islam', 'Rogelio Salmona', 'Guillermo Bermúdez', 'Rifat Chadirji', 'Turgut Cansever', 'Leandro Locsin', 'Tadao Ando',
                                                    'Mick Pearce', 'Bruno Stagno', 'Kamran Diba', 'Hossein Amanat', 'Nayyar Ali Dada', 'Arif Hasan', 'Wu Liangyong', 'Ja\'afar Tuqan', 'Alex Ifeanyichukwu Ekwueme', 'Sverre Fehn', 'Juha Leiviskä']),
    ('Landscape architects and urban planners', ['Ian McHarg', 'Cornelia Oberlander', 'Shlomo Aronson', 'Jan Gehl', 'Peter Latz', 'Jaime Lerner', 'Liu Thai Ker', 'Klaus Humpert']),
]
K622_MOVES = {
    # high-tech
    'Norman Foster': 'K6-19', 'Richard Rogers': 'K6-19', 'Su Rogers': 'K6-19', 'Renzo Piano': 'K6-19', 'Michael Hopkins': 'K6-19', 'Patty Hopkins': 'K6-19',
    'Nicholas Grimshaw': 'K6-19', 'Jan Kaplický': 'K6-19', 'Frei Otto': 'K6-19',
    # deconstructivism
    'Wolf D. Prix': 'K6-25', 'Helmut Swiczinsky': 'K6-25', 'Thom Mayne': 'K6-25', 'Eric Owen Moss': 'K6-25', 'Günther Domenig': 'K6-25',
    # postmodern
    'Robert A. M. Stern': 'K6-24', 'Stanley Tigerman': 'K6-24', 'James Stirling': 'K6-24', 'Michael Wilford': 'K6-24', 'Helmut Jahn': 'K6-24',
    # new classical
    'Quinlan Terry': 'K6-20',
    # traditional sthapati
    'V. Ganapati Sthapati': 'K7-4',
    # designers
    'Eero Aarnio': 'I3-19', 'Yrjö Kukkapuro': 'I3-19', 'Pierre Paulin': 'I3-19', 'Marc Held': 'I3-19', 'Marc Berthier': 'I3-19', 'Poul Kjærholm': 'I3-19', 'Nanna Ditzel': 'I3-19',
    'Luigi Colani': 'I3-19', 'Hans Gugelot': 'I3-19', 'Dieter Rams': 'I3-19', 'Vladimir Kagan': 'I3-19', 'Sergio Rodrigues': 'I3-19', 'Bruno Mathsson': 'I3-19',
    'Livio Castiglioni': 'I3-19', 'Pier Giacomo Castiglioni': 'I3-19', 'Marco Zanuso': 'I3-19', 'Cini Boeri': 'I3-19', 'Anna Castelli Ferrieri': 'I3-19', 'Vico Magistretti': 'I3-19',
    'Gianfranco Frattini': 'I3-19', 'Sergio Asti': 'I3-19', 'Charles Eames': 'I3-19', 'Niko Kralj': 'I3-19', 'Giotto Stoppino': 'I3-19', 'Tobia Scarpa': 'I3-19', 'Afra Bianchin': 'I3-19',
    'Mario Bellini': 'I3-19', 'Paolo Lomazzi': 'I3-19', 'Donato D\'Urbino': 'I3-19', 'Cesare Casati': 'I3-19', 'Cesare Leonardi': 'I3-19', 'Giandomenico Belotti': 'I3-19',
    'Massimo Vignelli': 'I3-19', 'Lella Vignelli': 'I3-19', 'Bob Noorda': 'I3-19', 'Benno Wissing': 'I3-19', 'AG Fronzoni': 'I3-19', 'Davorin Savnik': 'I3-19', 'Andrée Putman': 'I3-20',
    'Miquel Milà i Sagnier': 'I3-19',
    # photographers / artists
    'Gabriele Basilico': 'J1-13', 'Guido Guidi': 'J1-13', 'Nico de Haas': 'J1-10', 'Vito Acconci': 'M1-8', 'Manfredo Massironi': 'D5-120', 'Nanda Vigo': 'A5-110',
}

K626_GROUPS = [
    ('Minimalism in architecture', ['John Pawson', 'Alberto Campo Baeza', 'David Chipperfield', 'Jacques Herzog', 'Pierre de Meuron', 'Annette Gigon', 'Max Dudler']),
    ('Blobitecture', ['Greg Lynn']),
    ('Parametricism and digital architecture', ['Alejandro Zaera-Polo', 'Farshid Moussavi', 'Hani Rashid', 'Lise Anne Couture', 'Preston Scott Cohen', 'Neri Oxman', 'Jürgen Mayer', 'Arturo Vittori', 'Vicente Guallart', 'Enric Ruiz Geli']),
    ('SuperDutch', ['Winy Maas', 'Ben van Berkel', 'Caroline Bos', 'Francine Houben', 'Erick van Egeraat', 'Ellen van Loon', 'Mels Crouwel', 'Winka Dubbeldam', 'Adriaan Geuze', 'Petra Blaisse', 'Xaveer De Geyter']),
    ('Russian paper architecture', ['Utkin Ilya Valentinovich', 'Yury Avvakumov']),
    ('Porto School', ['Eduardo Souto de Moura']),
    ('Critical regionalism', ['Diébédo Francis Kéré', 'Marina Tabassum', 'Simón Vélez', 'Anna Heringer', 'Anupama Kundoo', 'Bijoy Jain', 'Mariam Kamara', 'Kunlé Adeyemi', 'Vo Trong Nghia', 'Rasem Badran', 'Paul Pholeros',
                              'Giancarlo Mazzanti', 'Alejandro Alavena', 'Zhang Ke', 'Ken Yeang', 'Tatiana Bilbao', 'Frida Escobedo', 'Marwa Al-Sabouni', 'Joar Nango']),
    ('Catalan architecture since the 1980s', ['Enric Miralles', 'Carme Pinós', 'Benedetta Tagliabue', 'Carme Pigem', 'Josep Lluis Mateo']),
    ('Neo-Rationalism', ['Hans Kollhoff']),
    ('Landscape architects', ['Michel Desvigne']),
]
K626_MOVES = {
    'Julian Bicknell': 'K6-20', 'Robert Adam': 'K6-20', 'Marvano': 'B1-7',
    'Michael Elmgreen': 'A5-111', 'Tomás Saraceno': 'A5-111', 'Marjetica Potrč': 'A5-111', 'Mathieu Kleyebe Abonnenc': 'A5-111', 'Max Hooper Schneider': 'A5-111',
    'Bonnie Sherk': 'A5-111', 'Yadegar Asisi': 'A5-111', 'Ola Hassanain': 'A5-111',
    'Iwan Baan': 'J1-13', 'Bas Princen': 'J1-13', 'Walter Niedermayr': 'J1-13',
    'Maarten van Severen': 'I3-20', 'Bořek Šípek': 'I3-20', 'Ilkka Suppanen': 'I3-20', 'Antonio Citterio': 'I3-20', 'Paolo Piva': 'I3-20', 'Michele De Lucchi': 'I3-20', 'Matteo Thun': 'I3-20',
    'Stefano Giovannoni': 'I3-20', 'Piero Lissoni': 'I3-20', 'Massimo Iosa Ghini': 'I3-20', 'Patricia Urquiola': 'I3-20', 'Jonas Bohlin': 'I3-20', 'Mats Theselius': 'I3-20', 'Hannes Wettstein': 'I3-20',
    'Alfredo Häberli': 'I3-20', 'Ron Arad': 'I3-20', 'Satyendra Pakhale': 'I3-20', 'Bas van Beek': 'I3-20', 'Oki Sato': 'I3-20', 'Ted Noten': 'I3-20', 'India Mahdavi': 'I3-20', 'Martine Bedin': 'I3-20',
    'Antonio Pio Saracino': 'I3-20', 'Sunita Kohli': 'I3-20', 'Amina Agueznay': 'I3-20',
}
K626_STYLE = [('Blobitecture', ['Blobitecture']), ('Minimalism in architecture', ['minimalism in architecture', 'minimalist architecture', 'Minimalism']),
              ('Neomodern', ['neomodern']), ('Critical regionalism', ['critical regionalism'])]

def group_makers(leaf, groups, moves, style_groups, order_tail):
    gi = {}
    for i, (g, ns) in enumerate(groups):
        for n in ns:
            gi.setdefault(n, g)
    order = [g for g, _ in style_groups] + [g for g, _ in groups if g not in [x for x, _ in style_groups]]
    rows = []
    for r in leaf['rows']:
        if not is_maker(r):
            continue
        n = r[0]
        if not n.strip():
            MOVES.append([n, leaf['code'], 'A5-111']); continue
        if n in moves:
            MOVES.append([n, leaf['code'], moves[n]]); continue
        info = architect_info(r)
        g = gi.get(n)
        if not g and info:
            st = info['styles_label'].split('|')
            for name, labs in style_groups:
                if any(s in st for s in labs):
                    g = name; break
        if not g and r[1] in ('High-tech architecture', 'Amsterdam School', 'Rationalism', 'Organic architecture', 'Metabolism', 'Functionalism', 'Neues Bauen'):
            g = {'Rationalism': 'Italian Rationalism (Como group)', 'Neues Bauen': None}.get(r[1], r[1])
        e = ev(r)
        if not g:
            c = e.get('countries') or (info['citizenship'] if info else '')
            g = country(c.replace('|', ','))
        if info and r[1] == 'Architects':
            gl = arch_gloss(r, info)
        else:
            gl = mgloss(r)
            if info and not e.get('birth'):
                gl = arch_gloss(r, info)
        try:
            b = int(e.get('birth') or (info['birth'] if info else '') or 9999)
        except ValueError:
            b = 9999
        rows.append((g, b, [n, g, gl, r[3], 1]))
    cnt = collections.Counter(g for g, _, _ in rows)
    oi = {g: i for i, g in enumerate(order)}
    rows.sort(key=lambda x: (oi.get(x[0], 1000 - cnt[x[0]]), x[0], x[1]))
    return [k for _, _, k in rows]

DOCOMOMO = ['https://docomomo.com/', 'Docomomo International', 'registers of buildings, sites and neighbourhoods of the Modern Movement by national chapter']
def build(out):
    leaf = LEAVES['K6-22']
    kinds = substyles(leaf, {'Movements': 'Sub-styles and movements', 'Phases': 'Sub-styles and movements', 'Regional schools': 'Regional schools'}, [])
    kinds = [k for k in kinds if not is_maker(k)]
    secs = [('De Stijl buildings', ['de stijl']), ('Purist buildings', ['purism']), ('Functionalist buildings', ['functionalism']), ('Neues Bauen buildings', ['neues bauen']),
            ('New Objectivity buildings', ['new objectivity', 'nieuwe zakelijkheid']), ('New Hague School buildings', ['new hague school']), ('Noucentista buildings', ['noucentisme']),
            ('Italian Rationalist buildings', ['rationalism of lake como', 'rationalism']), ('Organic architecture buildings', ['organic architecture']), ('Usonian houses', ['usonian architecture']),
            ('Bienne modernism buildings', ['bienne modernism']), ('Brazilian modernist buildings', ['modernist architecture in brazil']), ('Brussels style (Expo 58) buildings', ['brussels style', 'expo style']),
            ('Structuralist buildings', ['structuralism']), ('New Formalist buildings', ['new formalism']), ('Soviet Modernist buildings', ['soviet modernist architecture', 'neoconstructivism']),
            ('Late Modernist buildings', ['late modernism'])]
    kinds += works(secs, ['modern architecture', 'modernism', 'american modernism'], 'Modernist', hi=None)
    kinds += group_makers(leaf, K622_GROUPS, K622_MOVES, K622_STYLE, [])
    out['leaves']['K6-22'] = dict(
        axis='Sub-styles and regional schools; works: every gathered exemplar building tagged modern or with one of the listed sub-styles that has a Wikipedia article or heritage/UNESCO listing, by sub-style then building type; architects by named movement, group or school (from their buildings\' styles and the literature), the rest by country; designers, photographers and artists moved to their own leaves',
        catalogues=[DOCOMOMO, [wp('List of modernist architects'), 'Wikipedia: List of modernist architects', 'modernist architects with their works'], cat('Modernist architecture by country', 'all Wikipedia articles on modernist buildings, by country'),
                    ['https://whc.unesco.org/en/list/?search=modern', 'UNESCO World Heritage List (search: modern)', 'inscribed modern-movement sites, e.g. Le Corbusier\'s works, Brasília, Tel Aviv White City']],
        kinds=kinds, alias_rows=list(leaf['alias_rows']))

    leaf = LEAVES['K6-26']
    kinds = substyles(leaf, {'Movements': 'Sub-styles and movements', 'Regional schools': 'Sub-styles and movements'}, ['critical regionalism', 'minimalism in architecture', 'neomodern', 'Blobitecture', 'parametricism', 'Complementary architecture', 'Cholet'])
    kinds = [k for k in kinds if not is_maker(k)]
    kinds += works([('Critical regionalist buildings', ['critical regionalism']), ('Minimalist buildings', ['minimalism in architecture']), ('Neomodern buildings', ['neomodern']),
                    ('Blobitecture buildings', ['blobitecture']), ('Parametricist buildings', ['parametricism'])], ['contemporary architecture'], 'Contemporary', hi=None)
    kinds += group_makers(leaf, K626_GROUPS, K626_MOVES, K626_STYLE, [])
    out['leaves']['K6-26'] = dict(
        axis='Sub-styles and movements; works: every gathered exemplar building tagged contemporary or with a listed sub-style that has a Wikipedia article or heritage listing, by sub-style then building type; architects by named movement or group, the rest by country; designers, photographers and artists moved to their own leaves',
        catalogues=[['https://www.archdaily.com/', 'ArchDaily', 'the largest online archive of contemporary built projects, searchable by architect, type and country'],
                    ['https://www.miesarch.com/', 'EU Mies van der Rohe Award archive', 'every nominated and shortlisted European building since 1988'],
                    ['https://www.pritzkerprize.com/laureates', 'Pritzker Architecture Prize laureates', 'all laureates with their principal works'],
                    ['https://www.akdn.org/architecture', 'Aga Khan Award for Architecture', 'all award-winning and shortlisted projects since 1980']],
        kinds=kinds, alias_rows=list(leaf['alias_rows']))
