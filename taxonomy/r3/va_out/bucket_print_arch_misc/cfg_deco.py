from common import *

DECO_ADD = [
    ('Émile-Jacques Ruhlmann', 'French ensemblier, master of Art Deco furniture, 1879–1933', 'Émile-Jacques Ruhlmann'),
    ('Jean Dunand', 'Swiss-French lacquer and metalwork artist, 1877–1942', 'Jean Dunand'),
    ('Eileen Gray', 'Irish furniture designer and architect, lacquer screens and E-1027, 1878–1976', 'Eileen Gray'),
    ('Edgar Brandt', 'French ironworker, 1880–1960', 'Edgar Brandt'),
    ('Jean Puiforcat', 'French silversmith, 1897–1945', 'Jean Puiforcat'),
    ('Pierre Chareau', 'French furniture designer and architect of the Maison de Verre, 1883–1950', 'Pierre Chareau'),
    ('Paul Iribe', 'French designer and illustrator, 1883–1935', 'Paul Iribe'),
    ('Süe et Mare', 'Compagnie des Arts Français, Paris decorating firm of Louis Süe and André Mare, 1919–1928', 'Süe et Mare'),
]
DECO_GROUPS = [
    ('Furniture, interiors and decorators', ['Maurice Dufrêne', 'André Groult', 'Jules Leleu', 'Betty Joel', 'Jean-Michel Frank', 'René Gabriel', 'Jean Royère', 'Syrie Maugham', 'Sibyl, Lady Colefax', 'Nancy Lancaster',
        'Ilonka Karasz', 'Pipsan Saarinen Swanson', 'Edward Wormley', 'Prince Sigvard Bernadotte']),
    ('Wiener Werkstätte (late phase)', ['Mathilde Flögl', 'Felice Rix-Ueno', 'Susi Singer-Schinnerl']),
    ('Jewellery and silver', ['Raymond Templier', 'Jean Schlumberger', 'Harald Nielsen', 'Wiwen Nilsson', 'Elisabeth Treskow', 'William Spratling', 'Héctor Aguilar', 'Sylvia Stave']),
    ('Glass and lighting', ['Paolo Venini', 'Flavio Poli', 'Archimede Seguso', 'Göran Hongell', 'Lisa Johansson-Pape', 'Gunnel Nyman', 'Max Ingrand', 'Stasys Ušinskas', 'Miksa Róth']),
    ('Ceramics and studio pottery', ['Clarice Cliff', 'Susie Cooper', 'Katherine Pleydell-Bouverie', 'Lucie Rie', 'Toini Muona', 'Friedl Holzer-Kjellberg', 'Gunnar Nylund', 'Hedwig Bollhagen', 'Trude Petri', 'Lea Halpern',
        'Maija Grotell', 'Laura Andreson', 'Otto Natzler', 'Gertrud Natzler']),
    ('Textiles, tapestry and fibre art', ['Hannah Ryggen', 'Barbro Nilsson', 'Dora Jung', 'Sigrun Berg', 'Synnøve Anker Aurdal', 'Astrid Sampe', 'Marianne Strengell', 'Dorothy Liebes', 'Mariska Karasz', 'Jacqueline Groag',
        'Vera Neumann', 'Lenore Tawney', 'Claire Zeisler', 'Wanda Telakowska', 'Eva Frieberger', 'Bessie M. Scott', 'Pola Stout']),
    ('Paris couture of the 1920s–30s', ['Madeleine Vionnet', 'Jean Patou', 'Lucien Lelong', 'Nina Ricci', 'Elsa Schiaparelli', 'Maggy Rouff', 'Jacques Heim', 'Marcel Rochas', 'Grès', 'Cristóbal Balenciaga', 'Christian Dior',
        'André Perugia', 'Roger Vivier', 'Charles Jourdan', 'Louis Réard']),
    ('London, Italian and American couture and ready-to-wear', ['Norman Hartnell', 'Victor Stiebel', 'Charles James', 'Edwin Hardy Amies', 'Salvatore Ferragamo', 'Aldo Gucci', 'Fernanda Gattinoni', 'Main Bocher',
        'Hattie Carnegie', 'Nettie Rosenstein', 'Valentina', 'Lilly Daché', 'Omar Kiam', 'Norman Norell', 'Vera Maxwell', 'Adele Simpson', 'Elizabeth Hawes', 'Claire McCardell', 'Pauline Trigère', 'Etienne Aigner', 'Zara Bate']),
    ('Hollywood and stage costume and set design', ['Travis Banton', 'Edith Head', 'Adrian', 'Helen Rose', 'Jean Louis', 'Boris Aronson', 'Rudi Feld', 'Aline Bernstein']),
    ('Graphic design, book design and illustration', ['Francis Meynell', 'Sander Stols', 'Willem Sandberg', 'Marcel Jacno', 'George Salter', 'Lester Beall', 'Will Burtin', 'Erik Nitsche', 'Henri Friedlaender', 'Merle Armitage',
        'Donia Nachshen', 'Carl Erickson', 'Russell Patterson', 'Otto Soglow', 'Virginia Lee Burton', 'George Barbier', 'Conrad Fehn']),
    ('Streamline Moderne and industrial design', ['Raymond Loewy', 'Harley Earl', 'Gilbert Rohde', 'Harold Van Doren', 'Henry Dreyfuss', 'Russel Wright', 'John Vassos', 'Egmont Hegel Arens', 'John Tjaarda', 'Dante Giacosa',
        'Corradino D\'Ascanio', 'Alec Issigonis', 'Walter Zapp', 'Hans Hilfiker', 'Piet Hein', 'Earl Tupper']),
    ('Inventors, manufacturers and patrons', ['Leo Gerstenzang', 'Earle Dickson', 'Forrest Mars', 'Estée Lauder', 'Larry Aldrich', 'Sidney Janis', 'Pauline de Rothschild']),
]
DECO_MOVES = {'Otti Berger': 'I3-17', 'Benita Koch-Otte': 'I3-17', 'Margaretha Reichardt': 'I3-17', 'Marli Ehrman': 'I3-17', 'Kitty van der Mijll Dekker': 'I3-17', 'Christian Dell': 'I3-17', 'Naum Slutzky': 'I3-17',
              'Theodor Bogler': 'I3-17', 'Erich Dieckmann': 'I3-17', 'Marguerite Wildenhain': 'I3-17', 'Frans Wildenhain': 'I3-17',
              'Lucy M. Lewis': 'E1-67', 'Raymond Savignac': 'B2-9', 'Hans Schleger': 'B2-9', 'Alex Diggelmann': 'B2-9', 'Dolly Rudeman': 'B2-9', 'Mikhail Cheremnykh': 'B2-11'}

NOUV_TO_DECO = ['Maurice Dufrêne', 'André Groult', 'Jules Leleu', 'Madeleine Vionnet', 'Jean Patou', 'Lucien Lelong', 'Nina Ricci', 'Charles Jourdan', 'Hattie Carnegie', 'Syrie Maugham', 'Sibyl, Lady Colefax',
                'George Barbier', 'Egmont Hegel Arens', 'Aline Bernstein']
NOUV_ADD_MAKERS = [
    ('Émile Gallé', 'Nancy glass and furniture maker, founder of the École de Nancy, 1846–1904', 'Émile Gallé', 'École de Nancy'),
    ('Louis Majorelle', 'Nancy furniture maker, 1859–1926', 'Louis Majorelle', 'École de Nancy'),
    ('Hector Guimard', 'Paris architect-designer of the Métro entrances, 1867–1942', 'Hector Guimard', 'Paris (Maison de l\'Art Nouveau)'),
    ('René Lalique', 'French jeweller and glassmaker, 1860–1945', 'René Lalique', 'Paris (Maison de l\'Art Nouveau)'),
    ('Alphonse Mucha', 'Czech poster artist and designer working in Paris, 1860–1939', 'Alphonse Mucha', 'Paris (Maison de l\'Art Nouveau)'),
    ('Eugène Grasset', 'Swiss-French decorative designer and poster artist, 1845–1917', 'Eugène Grasset', 'Paris (Maison de l\'Art Nouveau)'),
    ('Georges Fouquet', 'Paris jeweller, Mucha collaborator, 1862–1957', 'Georges Fouquet', 'Paris (Maison de l\'Art Nouveau)'),
    ('Henry van de Velde', 'Belgian designer and architect, 1863–1957', 'Henry van de Velde', 'Belgian Art Nouveau'),
    ('Philippe Wolfers', 'Belgian jeweller and silversmith, 1858–1929', 'Philippe Wolfers', 'Belgian Art Nouveau'),
    ('Louis Comfort Tiffany', 'American glass and decorative-arts designer, 1848–1933', 'Louis Comfort Tiffany', 'American Art Nouveau'),
    ('Koloman Moser', 'Viennese designer, co-founder of the Wiener Werkstätte, 1868–1918', 'Koloman Moser', 'Vienna Secession and Wiener Werkstätte'),
    ('Josef Hoffmann', 'Viennese architect-designer, co-founder of the Wiener Werkstätte, 1870–1956', 'Josef Hoffmann', 'Vienna Secession and Wiener Werkstätte'),
    ('Charles Rennie Mackintosh', 'Glasgow architect and designer, 1868–1928', 'Charles Rennie Mackintosh', 'Glasgow Style'),
    ('Margaret Macdonald Mackintosh', 'Glasgow designer, one of The Four, 1864–1933', 'Margaret Macdonald Mackintosh', 'Glasgow Style'),
    ('Archibald Knox', 'Manx designer of Liberty\'s Cymric and Tudric wares, 1864–1933', 'Archibald Knox', 'Liberty style (Britain)'),
    ('Hermann Obrist', 'Swiss-German embroidery designer of Munich Jugendstil, 1862–1927', 'Hermann Obrist', 'Jugendstil'),
    ('Carlo Bugatti', 'Milanese furniture designer, 1856–1940', 'Carlo Bugatti', 'Stile Liberty'),
]
NOUV_CENTRES = [
    ('École de Nancy', 'alliance of Nancy\'s Art Nouveau industries founded 1901 (Gallé, Daum, Majorelle)', 'École de Nancy'),
    ('Maison de l\'Art Nouveau', 'Siegfried Bing\'s Paris gallery (1895) that named the style', 'Maison de l\'Art Nouveau'),
    ('Wiener Werkstätte', 'Vienna production cooperative of designers and craftsmen, 1903–1932', 'Wiener Werkstätte'),
    ('Darmstadt Artists\' Colony', 'artists\' colony on the Mathildenhöhe founded 1899 by Ernst Ludwig of Hesse', 'Darmstadt Artists\' Colony'),
    ('Liberty & Co.', 'London store whose Cymric and Tudric wares gave Italy the name Stile Liberty', 'Liberty (department store)'),
    ('Tiffany Studios', 'New York glass and decorative-arts firm of Louis Comfort Tiffany, 1902–1932', 'Tiffany Studios'),
    ('Loetz', 'Bohemian art-glass works at Klášterský Mlýn', 'Loetz'),
    ('Rozenburg', 'Hague porcelain and earthenware factory famous for eggshell porcelain, 1883–1917', 'Rozenburg'),
    ('Zsolnay', 'Pécs porcelain and eosin-glaze manufactory', 'Zsolnay'),
]
NOUV_GROUPS = [
    ('Paris (Maison de l\'Art Nouveau)', ['Théodore Deck', 'Auguste Jean', 'Louis Aucoc', 'Henri Vever', 'Emile Lenoble', 'Louis Cartier', 'Pierre C. Cartier', 'Camille Tharaud', 'Jean Gaudin', 'Pierre Yantorny', 'Henriette Negrin', 'Blaise Cendrars']),
    ('École de Nancy', ['Victor Amalric Walter']),
    ('Vienna Secession and Wiener Werkstätte', ['Ditha Moser', 'Emilie Louise Flöge', 'Paul Jaray', 'Franz Josef Popp']),
    ('Jugendstil', ['Patriz Huber', 'Friedrich Adler', 'Paul Leni', 'Frederick Meyer']),
    ('Glasgow Style', ['Jessie Newbery']),
    ('Catalan modernisme', ['Gaspar Homar i Mezquida']),
    ('Stile Liberty', ['Maria Monaci Gallenga', 'Alfonso Bialetti']),
    ('Skønvirke and Nordic Art Nouveau', ['Frida Hansen', 'Patrick Nordström', 'Märta Måås-Fjetterström', 'Evald Nielsen', 'Karl Gustaf Hjalmar Armfeldt', 'Alma Pihl', 'Emma Jacobsson', 'Louise Adelborg', 'Kay Bojesen', 'Sven Gustaf Wingqvist']),
    ('British Arts and Crafts and Art Nouveau', ['Charlotte Rhead', 'Martin Travers', 'Christine Angus', 'Wilhelmina Geddes', 'Frank Pick', 'Fougasse', 'Thomas Andrews']),
    ('American art pottery and metalwork', ['Frederick Hurten Rhead', 'R. Guy Cowan', 'Arthur Eugene Baggs', 'Glen Lukens', 'Dorothea Warren O\'Hara', 'Marie Zimmermann', 'John Hays Hammond Jr.']),
    ('American poster and magazine illustration', ['Frederick Strothmann', 'J. Allen St. John', 'Charles Buckles Falls', 'Herbert Paus', 'Paul Stahr', 'Louis D. Fancher', 'Arthur William Brown', 'Hendrik Willem van Loon']),
    ('Colonial and Asian figures', ['Kartini', 'Pingali Venkayya', 'Maria Louisa Gardner']),
]
NOUV_MOVES = {'Ernest A. Batchelder': 'I3-14', 'Dard Hunter': 'I3-14', 'Robert (Mouseman) Thompson': 'I3-14', 'Maria Martinez': 'E1-69', 'Erik Magnussen': 'I3-20'}

def build(out):
    # Art Deco
    l = dict(LEAVES['I3-16']); l['rows'] = LEAVES['I3-16']['rows'] + [r for r in LEAVES['I3-15']['rows'] if r[0] in NOUV_TO_DECO]
    k = []
    add(k, 'Canonical Art Deco designers', [(n, g, wp(u)) for n, g, u in DECO_ADD], 1)
    k += assign(l, DECO_GROUPS, DECO_MOVES)
    out['leaves']['I3-16'] = dict(
        axis='canonical Paris ensembliers first, then by medium: furniture and interiors, Wiener Werkstätte, jewellery and silver, glass, ceramics, textiles, couture, costume, graphic design, Streamline industrial design; within each by birth. The gathered rows are designers born c. 1890–1910 who worked in the Art Deco decades; Bauhaus makers moved to the Bauhaus leaf',
        catalogues=[['https://collections.vam.ac.uk/search/?q=art%20deco', 'V&A collections: Art Deco', 'Art Deco objects in the Victoria and Albert Museum'],
                    ['https://www.metmuseum.org/art/collection/search?q=art%20deco', 'The Met collection: Art Deco', 'Art Deco furniture, metalwork and glass at the Met'],
                    ['https://collection.cooperhewitt.org/search/collection/?query=art%20deco', 'Cooper Hewitt collection: Art Deco', 'Art Deco design objects at the Smithsonian design museum'],
                    ['https://madparis.fr/', 'Musée des Arts Décoratifs, Paris', 'the Paris museum whose 1925 Exposition gave the style its name']],
        kinds=k)
    # Art Nouveau
    k = []
    for r in LEAVES['I3-15']['rows']:
        if r[0] == 'Catalan modernism':
            k.append(['Catalan modernisme', 'Sub-types', 'the Catalan form of Art Nouveau in architecture and the decorative arts, Barcelona c. 1888–1911', r[3], 0])
    add(k, 'Sub-types', [('Jugendstil', 'German and Scandinavian name and branch of the style, after the Munich magazine Jugend', wp('Jugendstil')),
                         ('Stile Liberty', 'Italian Art Nouveau, named after Liberty & Co. of London', wp('Stile Liberty')),
                         ('Vienna Secession', 'Austrian branch of the style, the Secession founded 1897', wp('Vienna Secession'))])
    for r in LEAVES['I3-15']['rows']:
        if r[0] == 'Daum':
            k.append(['Daum', 'Centres & workshops', 'Daum glassworks, Nancy: Art Nouveau cameo and pâte-de-verre glass from the 1890s', r[3], 0])
    add(k, 'Centres & workshops', [(n, g, wp(u)) for n, g, u in NOUV_CENTRES])
    groups = [(g, ns) for g, ns in NOUV_GROUPS]
    added = collections.defaultdict(list)
    for n, g, u, grp in NOUV_ADD_MAKERS:
        added[grp].append([n, grp, g, 'r3 ' + wp(u), 1])
    l = dict(LEAVES['I3-15']); l['rows'] = [r for r in LEAVES['I3-15']['rows'] if r[0] not in NOUV_TO_DECO]
    mk = assign(l, groups, NOUV_MOVES)
    order = [g for g, _ in NOUV_GROUPS]
    for g in added:
        if g not in order:
            order.insert(3, g)
    bygroup = collections.defaultdict(list)
    for x in mk:
        bygroup[x[1]].append(x)
    for g in order:
        k += added.get(g, []) + bygroup.pop(g, [])
    for g, xs in bygroup.items():
        k += xs
    out['leaves']['I3-15'] = dict(
        axis='sub-types (national names of the style), then centres and workshops, then makers by national school or circle (Paris, Nancy, Belgium, Vienna, Munich/Darmstadt, Glasgow, Liberty, Catalonia, Italy, the Nordic countries, America), canonical masters first in each; designers whose work is Art Deco moved to that leaf',
        catalogues=[['https://www.artnouveau.eu/', 'Réseau Art Nouveau Network', 'the Art Nouveau heritage of its member cities'],
                    ['https://www.musee-orsay.fr/en/collections', 'Musée d\'Orsay collections', 'the national collection of French Art Nouveau decorative arts'],
                    ['https://collections.vam.ac.uk/search/?q=art%20nouveau', 'V&A collections: Art Nouveau', 'Art Nouveau objects in the Victoria and Albert Museum'],
                    ['https://www.metmuseum.org/art/collection/search?q=art%20nouveau', 'The Met collection: Art Nouveau', 'Art Nouveau glass, jewellery and furniture at the Met'],
                    ['https://musee-ecole-de-nancy.nancy.fr/', 'Musée de l\'École de Nancy', 'the museum of the Nancy school (Gallé, Majorelle, Daum)']],
        kinds=k)
