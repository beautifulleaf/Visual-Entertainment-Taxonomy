from common import *

# ---------------- B1-5 Illustration ----------------
B15_GROUPS = [
    ('Georgian and Regency caricature', ['Henry Bunbury', 'Isaac Robert Cruikshank', 'James Akin', 'Nikolay Alexandrovich Stepanov']),
    ('Victorian magazine illustration (Punch, Illustrated London News)', ['Ebenezer Landells', 'William Makepeace Thackeray', 'John Leech', 'James William Edmund Doyle', 'Charles H. Bennett', 'George du Maurier',
        'Tom Hood', 'W. S. Gilbert', 'Mary Ellen Edwards', 'Francis Carruthers Gould', 'Melton Prior', 'Georg Bötticher', 'Henri Meyer', 'Paul Hadol', 'Angelo Agostini']),
    ('American wood-engraving era illustration (Harper\'s, Leslie\'s)', ['Alexander Anderson', 'David Hunter Strother', 'Henry Louis Stephens', 'Frank Bellew', 'Sol Eytinge Jr.', 'True Williams',
        'Palmer Cox', 'Frank Hamilton Taylor', 'Rufus Fairchild Zogbaum']),
    ('Natural-history and scientific illustration', ['François Levaillant', 'Mary-Anne Paulzzze Lavoisier', 'John Frederick Miller', 'Prideaux John Selby', 'William Swainson', 'Augusta Innes Withers',
        'John Obadiah Westwood', 'Philip Henry Gosse', 'Henry Bradbury', 'Robert Gillmor', 'Abel Rodríguez']),
    ('Topographical, travel and expedition draughtsmen', ['William Gell', 'John Preston Neale', 'Louis Maurice Adolphe Linant de Bellefonds', 'Graham Gore', 'Felix Philipp Kanitz', 'Horatio Gordon Robley', 'Max Eyth', 'Alfred Wainwright']),
    ('Historical, military and reconstruction illustration', ['Paul Girardet', 'Björn Landström', 'Liliane Funcken', 'Angus McBride', 'Peter Connolly', 'Victor Ambrus']),
    ('Editorial and political cartoonists', ['David Langdon', 'Herblock', 'Bill Mauldin', 'Antonio Arias Bernal', 'Edmund Valtman', 'Philipp Rupprecht', 'Horst von Möllendorff', 'Friedel Stern', 'Zeev', 'Kariel Gardosh',
        'Turhan Selçuk', 'R. K. Laxman', 'Mangesh Tendulkar', 'Parviz Shapour', 'Zbigniew Lengren', 'Jacques Faizant', 'Piem', 'Siné', 'Marie Marcks', 'Giorgio Forattini', 'Ranan Lurie', 'Predrag Koraksić Corax',
        'Nicholas Garland', 'Heinz Valk', 'Forges', 'Gerhard Haderer', 'Plantu', 'Ali Farzat', 'Andrey Bilzho', 'Michel Kichka', 'Jonathan Shapiro', 'Pierre Kroll', 'Ali Dilem', 'Luz', 'Ramón Esono', 'Doaa el-Adl', 'Tony Rafty', 'Michael Atchison', 'Finn Graff', 'Jacques-Armand Cardon', 'Aurel']),
    ('Gag and magazine cartoonists (The New Yorker, Punch, Esquire)', ['Enrique Herreros', 'Félix Kassowitz', 'Osbert Lancaster', 'E. Simms Campbell', 'Mischa Richter', 'Syd Hoff', 'Chaval', 'Ronald Searle', 'Paul Flora',
        'Jean Bosc', 'Gerard Hoffnung', 'Henrik Tikkanen', 'Ton Smits', 'Carlos Garaycochea', 'Gahan Wilson', 'Guillermo Mordillo', 'Peter van Straaten', 'Jaap Vegter', 'Erich Sokol', 'Charles Barsotti', 'Ed Koren',
        'Willie Rushton', 'Balázs Balázs-Piri', 'Claude Serre', 'Hans Georg Rauch', 'Ray Lowry', 'Roz Chast', 'Jacky Fleming', 'Gébé', 'Jean-Marc Reiser', 'Roy Doty', 'Franz Eggenschwiler']),
    ('Children\'s book illustration: Britain and Ireland', ['Favell Lee Mortimer', 'Helen Binyon', 'Diana Ross', 'Pauline Baynes', 'Judith Kerr', 'Val Biro', 'Eric Hill', 'Jean Adamson', 'Peter Firmin', 'Susan Shaw',
        'Quentin Blake', 'Raymond Briggs', 'Anthony Colbert', 'Antony Maitland', 'Gerald Rose', 'Roger Hargreaves', 'John Burningham', 'Allan Ahlberg', 'Helen Oxenbury', 'Michael Foreman', 'Tony Ross', 'John Vernon Lord',
        'Mairi Hedderwick', 'Jan Pieńkowski', 'Anthony Browne', 'Graeme Base', 'Chris Riddell', 'Lucy Cousins', 'Kitty Crowther']),
    ('Children\'s book illustration: North America', ['Roger Duvoisin', 'Virginia Frances Sterrett', 'Ruth Krauss', 'Wesley Dennis', 'Glen Rounds', 'Aurelius Battaglia', 'Elizabeth Orton Jones', 'Evaline Ness', 'Joseph Low',
        'Garth Williams', 'Winifred Milius Lubell', 'Tasha Tudor', 'Marc Simont', 'Ezra Jack Keats', 'Richard Scarry', 'Edward Gorey', 'Vera Williams', 'Norman Bridwell', 'Eric Carle', 'Simms Taback', 'Tom Feelings',
        'Tomie dePaola', 'Anita Lobel', 'Jerry Pinkney']),
    ('Children\'s book illustration: continental Europe and beyond', ['Heinrich Hoffmann', 'Marie Olfers', 'Ernest Nister', 'Tony Schumacher', 'Sulamith Wülfing', 'Wiktoria Goryńska', 'Pierre Probst', 'Ingrid Vang Nyman',
        'Svend Otto S.', 'Zbigniew Rychlicki', 'Leonid Vladimirski', 'Felicitas Kuhn', 'Mance Post', 'Fritzi Harmsen van Beek', 'Gabrielle Vincent', 'Sybil Wettasinghe', 'Marcel Marlier', 'Victor Chizhikov', 'Valery Traugot',
        'Alona Frankel', 'Philippe Fix', 'Josse Goffin', 'Lena Anderson', 'Roser Capdevila', 'Nicole Claveloux', 'Ulf Löfgren', 'Per Åhlin', 'Bengt Böckman', 'Wolf Erlbruch', 'Hervé Tullet', 'Iwona Chmielewska',
        'Blexbolex', 'Rébecca Dautremer', 'Jakob Martin Strid', 'Terry Denton', 'Galinka Ehrenfest', 'Hans Ticha', 'Gerhard Kettner', 'Erkki Tanttu', 'Folke Dahlberg', 'Bertil Almqvist', 'Marion Fayolle']),
    ('Book illustration and decoration', ['Fritz Kredel', 'Eric Fraser', 'Erich Mönch', 'Robert Lips', 'Elisabeth Schumacher', 'Robert Trossin', 'Christoph Meckel', 'Nanne Meyer', 'John Alan Maxwell', 'Gray Foy', 'Agus Djaya', 'Kasing Lung']),
    ('American magazine and advertising illustration', ['Robert Fawcett', 'Oronzo Vito Gasparo', 'Al Parker', 'Austin Briggs', 'Coby Whitmore', 'Stephen Longstreet', 'Ione Robinson', 'Bob Peak', 'Roger Hane', 'Peter Fingesten']),
    ('Fashion illustration', ['Joe Eula', 'Kenneth Paul Block', 'Tom Keogh', 'Alvin Colt']),
    ('Fantasy, science-fiction and pulp illustration', ['Hannes Bok', 'Virgil Finlay', 'Ed Emshwiller', 'Basil Gogos', 'Darrell K. Sweet', 'John Schoenherr', 'Didier Graffet', 'Kim Jung Gi']),
    ('Graphic designers and typographers', ['Franz Xaver Reimspiess', 'Berthold Wolpe', 'Otte Wallish', 'Herbert W. Kapitzki', 'Aloísio Sergio Magalhães', 'Elaine Lustig Cohen', 'Jost Hochuli', 'Rosmarie Tissi', 'Hansje van Halem', 'Siegfried Woldhek']),
    ('Animation artists and puppet-film makers', ['Karel Zeman', 'Marc Davis', 'Norman Hetherington', 'Dušan Vukotić', 'Zoltán Huszárik', 'Nedeljko Dragić', 'Paul Driessen', 'Picha', 'Ronnie del Carmen']),
    ('British comics', ['Don Lawrence', 'Carlos Ezquerra', 'Dave Gibbons', 'John Bolton', 'Kate Charlesworth', 'Posy Simmonds', 'Eddie Campbell', 'Tula Lotay']),
    ('Italian comics (fumetti)', ['Nicola Salerno', 'Walter Molino', 'Lina Buffolente', 'Romano Scarpa', 'Sergio Toppi', 'Guido Crepax', 'Magnus', 'Igort', 'Paolo Bacilieri', 'Sara Pichelli', 'Zerocalcare']),
    ('Spanish comics (historieta and the Bruguera school)', ['Francisco Ibáñez Talavera', 'Ana Miralles', 'Juanjo Guarnido', 'Paco Roca', 'José Luis Munuera']),
    ('Argentine historieta and humour', ['José Luis Salinas', 'Alberto Breccia', 'Quino', 'Copi', 'Sergio Aragonés']),
    ('Dutch comics', ['Frans Piët', 'Hans G. Kresse', 'Carol Voges', 'Jan van Haasteren', 'Martin Lodewijk', 'Aimée de Jongh']),
    ('Asian comics and cartooning (manhua, Indian comics)', ['Narayan Debnath', 'Tsai Chih-chung', 'Hamid Nada']),
    ('Graphic novels and alternative comics', ['Seth Tobocman', 'Igor Kordej', 'Zoran Janjetov', 'Anke Feuchtenberger', 'Jason', 'Rutu Modan', 'Reinhard Kleist', 'Asaf Hanuka', 'Barbara Yelin', 'Liv Strömquist',
        'Zeina Abirached', 'Lilli Carré', 'Anna Haifisch', 'Nino Bulling', 'Zainab Fasiki', 'Andreas']),
    ('Writers, scholars and amateurs who drew', ['Johann Friedrich Anthing', 'Joséphine de Beauharnais', 'Countess Róża Potocka', 'Edward Ellerker Williams', 'Napoleon III', 'Edward FitzGerald', 'Napoleon II',
        'Eugène Pottier', 'Gunnar Wennerberg', 'Princess Clémentine, Princess of Koháry', 'Adrien Dubouché', 'Henry Howe', 'Henry Ford', 'Paul Heyse', 'Ernest d\'Hervilly', 'Carl Snoilsky', 'Infanta Antónia of Portugal',
        'Mary Eliza Haweis', 'Michel Manzi', 'Sibylle Riquetti de Mirabeau', 'Georges Zipélius', 'Jacques Prévert', 'Max Morise', 'Maurice Gilliams', 'Pascal Pia', 'Eugène Ionesco', 'Pere Calders', 'Sarah Churchill',
        'Cioma Schönhaus', 'Hans Bradtke', 'Édouard Jaguer', 'Hédi Fried', 'Pierre Mercure', 'Stig Claesson', 'Bernard Heidsieck', 'Simon Vinkenoog', 'Guy Debord', 'Willem de Ridder', 'Paul Jamin', 'Hannes Hegen']),
]
B15_MOVES = {
    # American comics
    'Floyd Gottfredson': 'B1-3', 'C. C. Beck': 'B1-3', 'Noel Sickles': 'B1-3', 'Joe Simon': 'B1-3', 'Dick Sprang': 'B1-3', 'George Tuska': 'B1-3', 'Dik Browne': 'B1-3', 'Ken Bald': 'B1-3', 'John Severin': 'B1-3',
    'Stan Drake': 'B1-3', 'Jerry Robinson': 'B1-3', 'Mike Sekowsky': 'B1-3', 'Dick Ayers': 'B1-3', 'Carmine Infantino': 'B1-3', 'Johnny Craig': 'B1-3', 'Murphy Anderson': 'B1-3', 'Russ Heath': 'B1-3',
    'Eric Stanton': 'B1-3', 'Alex Toth': 'B1-3', 'Frank Springer': 'B1-3', 'George Woodbridge': 'B1-3', 'Don Martin': 'B1-3', 'Angelo Torres': 'B1-3', 'Gray Morrow': 'B1-3', 'Larry Lieber': 'B1-3',
    'Sal Buscema': 'B1-3', 'Melinda Gebbie': 'B1-3', 'Gilbert Shelton': 'B1-3', 'Dave Cockrum': 'B1-3', 'Don Rosa': 'B1-3', 'Dave Sim': 'B1-3', 'Alfredo Alcala': 'B1-3', 'Pablo Marcos': 'B1-3',
    # Marcinelle school (Journal de Spirou)
    'Mitacq': 'B1-8', 'Marc Wasterlain': 'B1-8', 'Bédu': 'B1-8', 'Fabrice Tarrin': 'B1-8',
    # manga
    'Nagano': 'B1-9', 'Mamiya Oki': 'B1-9', 'Yukine Honami': 'B1-9', 'Yuki Kodama': 'B1-9',
    # posters
    'Herbert Leupin': 'B2-9', 'Boris Grinsson': 'B2-9', 'John van Hamersveld': 'B2-9',
    # printmaking / painting / contemporary art
    'Annie Pootoogook': 'B2-6', 'Krishen Khanna': 'A5-110', 'Ernesto Deira': 'A5-110', 'Antun Motika': 'A5-110', 'Pedro de Oraá': 'A5-110', 'Gauri Bhanja': 'A5-109', 'Ida Bagus Pegug': 'A5-2',
    'Susan Te Kahurangi King': 'A5-80', 'Grazia Varisco': 'D5-120', 'Katalin Ladik': 'M1-8', 'Karen Finley': 'M1-8', 'Kembra Pfahler': 'M1-8', 'Felix Partz': 'M1-2', 'Mary Bauermeister': 'M1-3', 'Robert Whitman': 'M1-8',
    'Terry Jennings': 'M1-3',
}
B15_CONTEMP = ['Rinus Van de Velde', 'Joëlle Tuerlinckx', 'Sophie Podolski', 'José Damasceno', 'Gloria Ortiz-Hernández', 'Eva Koťátková', 'Adolfo Nadal Walcot', 'Ala Younis', 'Toyin Ojih Odutola', 'Fernando Bryce',
    'Gilda Mantilla', 'Ding Yi', 'Jacky Tsai', 'Ciprian Mureşan', 'Petra Štefanková', 'Kagiso Patrick Mautloa', 'Araya Rasdjarmrearnsook', 'Nidhal Chamekh', 'Emre Hüner', 'Anya Gallaccio', 'Paul Noble', 'Adam Dant',
    'Olivia Plender', 'Rory Pilgrim', 'Sam Cox', 'Claire Barclay', 'Elspeth Lamb', 'Deanna Petherbridge', 'Marcel Odenbach', 'Thomas Kilpper', 'Thomas Locher', 'Marc Brandenburg', 'Julia Mangold', 'Michael Riedel',
    'Bjorn Dahlem', 'Bettina von Arnim', 'Richard Haas', 'Donald Evans', 'Heide Fasnacht', 'Jim Isermann', 'Russell Crotty', 'Eve Aschheim', 'Anne Chu', 'Martin Kersels', 'Mark Dion', 'Bruce Jensen', 'Tam Van Tran',
    'Ann Craven', 'Edgar Arceneaux', 'Banks Violette', 'Amy Cutler', 'Trisha Donnelly', 'Sam Lewitt', 'Sadie Barnette', 'Jacolby Satterwhite', 'Guadalupe Maravilla', 'Ernesto Caivano', 'Ester Partegàs',
    'Elena del Rivero', 'Victor Hugo', 'Fred Martin', 'Sam Middleton', 'Jack Roth', 'Gabi Klasmer', 'Aya Ben Ron', 'Nahid Hagigat', 'Anna Park', 'Gerardo Pita']
for n in B15_CONTEMP:
    B15_MOVES[n] = 'A5-111'
B15_TO_B215 = ['Jiang Feng', 'Birgit Skiöld', 'Jörg Schmeisser', 'Rolf Münzner', 'Heinz Kiwitz', 'Clément Moreau']

# Franco-Belgian comics: new leaf
FB_GROUPS = [
    ('Journal de Tintin and Spirou generation (1946–1970s)', ['Dino Attanasio', 'Édouard Aidans', 'René Follet', 'Paul Gillon', 'Georges Pichard', 'Monique Watteau', 'Derib', 'Hermann Huppen', 'René Hausman', 'Renaud']),
    ('Pilote generation (1959–1970s)', ['René Goscinny', 'Gotlib', 'Jean-Claude Mézières', 'André Chéret', 'Robert Lassalvy', 'Florence Cestac']),
    ('Adult bande dessinée of the 1970s–80s (Métal hurlant, Fluide glacial, À suivre)', ['Caza', 'Alex Varenne', 'Jacques Tardi', 'Hervé Barulea', 'Daniel Hulet', 'Philippe Liégeois', 'Jean-Claude Denis', 'François Boucq', 'Serge Ernst', 'Coyote']),
    ('Realist album series (1980s–2000s)', ['André Juillard', 'Christian Rossi', 'Jean-Pierre Gibrat', 'Alain Dodier', 'Patrice Pellerin', 'Philippe Berthet', 'Bernard Hislaire', 'Philippe Francq', 'Jean-Louis Mourier',
        'Isabelle Dethan', 'Tiburce Oger', 'Mazan', 'Jean-David Morvan', 'Ralph Meyer', 'Béatrice Tillier', 'Fabien Vehlmann', 'Jean-Yves Ferri', 'Zep']),
    ('Nouvelle bande dessinée (L\'Association and after)', ['David Beauchard', 'Émile Bravo', 'Nicolas de Crécy', 'Blutch', 'Dominique Goblet', 'Emmanuel Larcenet', 'Christophe Blain', 'Judith Vanistendael', 'Riad Sattouf',
        'Catherine Meurisse', 'Pénélope Bagieu', 'Jul\' Maroh', 'Brecht Evens', 'Émilie Gleason']),
]

# ---------------- B1-6 Golden Age of Illustration ----------------
B16_GROUPS = [
    ('Victorian and Edwardian book illustration (Britain)', ['Laurence Housman', 'Helen Stratton', 'Harold Robert Millar', 'Charles Robinson', 'William Heath Robinson', 'Alfred Garth Jones', 'Edmund Hort New', 'Harold Nelson',
        'Mabel Dearmer', 'Frank C. Papé', 'Edward Detmold', 'W. T. Horton', 'Reginald Knowles', 'Noel Rooke', 'Edith Holden', 'Mary Emily Eaton', 'Walter Paget', 'Phyllis Gardner', 'Clare Leighton']),
    ('British children\'s illustration and comic annuals', ['Helen Bannerman', 'Mary Tourtel', 'Mabel Lucie Attwell', 'George E. Studdy', 'Alfred Bestall', 'Kathleen Hale', 'Helen Jacobs', 'Basil Temple Blackwood', 'Oliver Herford']),
    ('Punch, press caricature and British comic art', ['Harry Furniss', 'Julius Mendes Price', 'Victor Gillam', 'Edward Tennyson Reed', 'Phil May', 'George Morrow', 'Frank Reynolds', 'William Haselden', 'Donald McGill',
        'H. M. Bateman', 'Power O\'Malley', 'David Low', 'Norman Pett', 'John Gilroy', 'John Hargrave', 'Oliver Onions', 'Frederick Gordon Crosby']),
    ('Special artists and war illustrators', ['Frederic Villiers', 'Paul Martin']),
    ('American book and magazine illustration (Brandywine era)', ['William Hamilton Gibson', 'William Allen Rogers', 'William Ladd Taylor', 'Isaac Walton Taber', 'Frederick Richardson', 'Charles M. Relyea', 'Peter Newell',
        'Maud Humphrey', 'Edwin George Lutz', 'Florence Scovel Shinn', 'Charlotte Harding', 'Frederic Dorr Steele', 'Charles Livingston Bull', 'Franklin Booth', 'John Wolcott Adams', 'Sarah Stilwell Weber',
        'Harry Everett Townsend', 'Joseph Clement Coll', 'Maginel Wright Enright', 'Edward Mason Eggleston', 'Edwin Megargee', 'Frank Godwin', 'Katherine Sturges Dodge', 'Edmund Franklin Ward', 'James Charles Castle', 'Milo Winter', 'H. G. Peter']),
    ('American children\'s books and the Oz illustrators', ['William Wallace Denslow', 'John R. Neill', 'Gelett Burgess', 'Fanny Cory', 'Grace Drayton', 'Harrison Cady', 'Tony Sarg', 'Dorothy P. Lathrop', 'Robert Lawson',
        'Helen Sewell', 'Kate Seredy', 'Kurt Wiese']),
    ('American political cartoonists (Puck, Judge, The Masses)', ['Frederick Burr Opper', 'T. S. Sullivant', 'E. W. Kemble', 'Louis Dalrymple', 'Homer Davenport', 'Udo Keppler', 'Art Young', 'Robert Minor',
        'William Charles McNulty', 'Lydia Gibson', 'Henry Mayer']),
    ('Early American comic strips', ['George Timothy Tobin', 'Tad Dorgan', 'Gene Carr']),
    ('Jazz Age magazine artists (Vanity Fair, The New Yorker, Life)', ['Otho Cushing', 'Alfred Frueh', 'Rea Irvin', 'John Held, Jr.', 'Gluyas Williams', 'Ralph Barton', 'James Thurber', 'Garrett Price', 'Mary Petty']),
    ('French illustration and press drawing (Le Rire, L\'Assiette au beurre)', ['Arthur Sapeck', 'Jean Baptiste Guth', 'Caran d\'Ache', 'Benjamin Rabier', 'Maurice Radiguet', 'André Rouveyre', 'Chéri Hérouard', 'Gus Bofa',
        'Henri-Paul Deyveaux-Gassier', 'André Warnot', 'André Galland', 'Jacques Touchet', 'Jean Sennep', 'Georges Méliès']),
    ('French children\'s books and early bande dessinée', ['Louis Forton', 'Étienne Le Rallic', 'Alain Saint-Ogan', 'Jean de Brunhoff']),
    ('German and Austrian illustration (Simplicissimus, Jugend)', ['Hans Schließmann', 'Hugo Gerard Ströhl', 'Gertrud Caspari', 'Sibylle von Olfers', 'Else Wenz-Vie͏̈tor', 'Erich Schilling', 'Alastair', 'Ludwig Sütterlin', 'Bruno Grimschitz']),
    ('Italian illustration (Corriere dei Piccoli)', ['Luigi Bertelli', 'Rata Langa', 'Giuseppe Scalarini', 'Gennaro Favai', 'Antonio Rubino']),
    ('Scandinavian illustration', ['Cornelia Cederberg', 'Oskar Andersson', 'Ragnvald Blix', 'Signe Hammarsten-Jansson', 'Vera Nilsson', 'Johan Bull', 'Rudolf Petersson', 'Hans Norsbo', 'Karl August Hindrey']),
    ('Russian illustration and Futurist books', ['Aleksey Remizov', 'Клемм Катерина Пилипівна', 'Velimir Khlebnikov', 'Aleksei Kruchenykh', 'Nikolay Radlov']),
    ('Australian illustration', ['May Gibbs', 'Dorothy Wall', 'Stan Cross']),
    ('Spanish, Portuguese and Latin American illustration', ['Juan Picasso González', 'Joaquín Xaudaró', 'Manuel Tovar Siles', 'Henrique Alvim Corrêa', 'Stuart Carvalhais', 'Conrado Walter Massaguer', 'Ricardo Rendón', 'Emilio Freixas']),
    ('Writers, designers and amateurs who drew', ['Max Elskamp', 'Paul Scheerbart', 'Jac P. Thijsse', 'Max Jakob Friedländer', 'Ernest Louis, Grand Duke of Hesse and by Rhine', 'Princess Henriette of Belgium', 'Heinrich Mann',
        'Miklós Bánffy', 'Cor van Gogh', 'Jan Feith', 'Eusebi Güell i López', 'Georges Bataille', 'Maria Pawlikowska-Jasnorzewska', 'Emma Hauck', 'Christoph Bernoulli', 'Hans Stocker', 'Henryk Minkiewicz', 'Karel Fleischmann', 'Robert Edmond Jones']),
]
B16_MOVES = {'Emma Hauck': 'A5-80'}
B16_ADD = [
    ('Walter Crane', 'English illustrator of toy books and Arts and Crafts book design, 1845–1915', 'Walter Crane'),
    ('Randolph Caldecott', 'English picture-book illustrator, 1846–1886; namesake of the Caldecott Medal', 'Randolph Caldecott'),
    ('Kate Greenaway', 'English children\'s illustrator, 1846–1901; namesake of the Greenaway Medal', 'Kate Greenaway'),
    ('Aubrey Beardsley', 'English black-and-white illustrator of Salome and The Yellow Book, 1872–1898', 'Aubrey Beardsley'),
    ('Arthur Rackham', 'English illustrator of Peter Pan and the Ring, 1867–1939', 'Arthur Rackham'),
    ('Edmund Dulac', 'French-British illustrator of the Arabian Nights and Andersen, 1882–1953', 'Edmund Dulac'),
    ('Kay Nielsen', 'Danish illustrator of East of the Sun and West of the Moon, 1886–1957', 'Kay Nielsen'),
    ('Harry Clarke', 'Irish stained-glass artist and illustrator of Poe and Andersen, 1889–1931', 'Harry Clarke'),
    ('Howard Pyle', 'American illustrator and teacher, founder of the Brandywine School, 1853–1911', 'Howard Pyle'),
    ('N. C. Wyeth', 'American illustrator of Treasure Island, Pyle\'s pupil, 1882–1945', 'N._C._Wyeth'),
    ('Jessie Willcox Smith', 'American illustrator of children\'s books, Pyle\'s pupil, 1863–1935', 'Jessie Willcox Smith'),
    ('Maxfield Parrish', 'American illustrator and painter, 1870–1966', 'Maxfield Parrish'),
    ('Charles Dana Gibson', 'American illustrator, creator of the Gibson Girl, 1867–1944', 'Charles Dana Gibson'),
    ('J. C. Leyendecker', 'American magazine-cover and advertising illustrator, 1874–1951', 'J._C._Leyendecker'),
    ('Ivan Bilibin', 'Russian illustrator of folk tales, World of Art circle, 1876–1942', 'Ivan Bilibin'),
    ('Elsa Beskow', 'Swedish picture-book author and illustrator, 1874–1953', 'Elsa Beskow'),
    ('John Bauer', 'Swedish illustrator of Among Gnomes and Trolls, 1882–1918', 'John Bauer (illustrator)'),
]

# ---------------- B2-14 Etching Revival ----------------
B214_GROUPS = [
    ('Painter-etchers', ['Francis Seymour Haden', 'Rodolphe Bresdin', 'Amédée de Noé', 'Charles-Michel Geoffroy', 'Mary Nimmo Moran', 'Henry Wolf', 'Edmond Andre Rocher', 'Auguste Brouet', 'Malo-Renault', 'F. L. Griggs',
        'Achille Ouvré', 'Helen Hyde', 'Elizabeth Campbell Fisher Clay', 'Emma Zorn', 'Thomas Sturge Moore', 'Nelly Bodenheim', 'Bert Nienhuis', 'Edmund Edel', 'Aleksei Aleksandrovich Radakov', 'Manuel Manilla']),
    ('Printers, publishers and dealers (Société des Aquafortistes)', ['Auguste Delâtre', 'Alfred Cadart', 'Joseph Lemercier', 'Auguste Clot', 'Edmond Ramus', 'Adolph Friedländer', 'Pierre Gusman']),
    ('Critics, collectors and cataloguers', ['Charles Blanc', 'Philippe Burty', 'Henry Havard', 'Loÿs Delteil', 'Gustav Pauli', 'Louis Alexander Fagan', 'Victor de Stuers', 'Llewellynn Jewitt', 'Horace de Viel-Castel']),
    ('Reproductive line and mezzotint engravers', ['Fyodor Iordan', 'James Tibbits Willmore', 'Samuel Cousins', 'John Cousen', 'William Holl', 'Charles George Lewis', 'Eugen Eduard Schäffer', 'Carl Johan Billmark', 'Achille-Louis Martinet',
        'Gaetano Dura', 'Tommaso Aloysio Juvara', 'Eduard Mandel', 'John Henry Le Keux', 'Alphonse François', 'Auguste III Blanchard', 'François-Eugène-Augustin Bridoux', 'Johann Leonhard Raab', 'Doris Raab',
        'Louis Jacoby', 'Thomas Oldham Barlow', 'Saro Cucinotta', 'Charles Henry Jeens', 'Achille Jacquet', 'Charles Albert Waltner', 'Giuseppe Barberis', 'August Weger', 'Wilhelm Hecht', 'Edwin Davis French', 'Gustav Kruell', 'John Chester Buttre', 'John Sartain', 'Patrick H. Reason', 'Charles Edward Barber']),
    ('Wood engravers of the illustrated press', ['Charles Swain', 'Joseph Swain', 'Henry Linton', 'Mason Jackson', 'William Luson Thomas', 'Frank Leslie', 'François Pannemaker', 'Auguste Danse', 'Alexandre Manceau',
        'Jean-Baptiste Danguin', 'Gustave Janet', 'Charles Barbant', 'Tony Beltrand', 'Charles Baude', 'Émile Jean Sulpis', 'Hugo Kaeseberg', 'Abraham Jacobus Wendel', 'Andrew Varick Stout Anthony', 'Firmin Gillot', 'Henri Boutet', 'George Samuel Measom']),
    ('Lithographers and chromolithograph publishers (Currier & Ives, Prang)', ['George Baxter', 'Nathaniel Currier', 'James Merritt Ives', 'John Henry Bufford', 'Louis Prang', 'Julius Bien', 'Alfred Guesdon',
        'Pierre Gustave Staal', 'Émile Théodore Therond', 'Alfred Taiée', 'Wilhelm Heuer', 'Wilhelm Tempel', 'Eusebi Planas i Franquesa', 'Alfred Concanen', 'Edward Tracy Turnerelli', 'Charles Clérice', 'Frank Mason Robinson']),
    ('Botanical and scientific illustrators', ['Walter Hood Fitch', 'Louis van Houtte', 'Marie Firmin Bocourt', 'Margaret Flockton', 'Anna Botsford Comstock', 'Caroline Amelia Powell', 'William Griggs', 'George Allen', 'Niels Christian Kierkegaard']),
    ('Writers, designers and amateurs', ['Joseph Bouchardy', 'Aglaüs Bouvenne', 'Gabrielle-Marie Niel', 'Marc-Louis Solon', 'Gustave Le Rouge', 'Henry Bataille', 'Alfred Jarry', 'Paul Renner', 'Mary Louise McLaughlin', 'Walter Montieth Aikman', 'Charles Francis Hall', 'John Henry Walker', 'F. H. Townsend', 'Auguste Roedel']),
]
B214_MOVES = {}
B214_ADD = [
    ('Charles Meryon', 'French etcher of the Eaux-fortes sur Paris, 1821–1868', 'Charles Meryon'),
    ('Félix Bracquemond', 'French etcher and founder member of the Société des Aquafortistes, 1833–1914', 'Félix Bracquemond'),
    ('Charles-François Daubigny', 'French Barbizon painter and etcher, 1817–1878', 'Charles-François Daubigny'),
    ('Alphonse Legros', 'French-born etcher, Slade professor in London, 1837–1911', 'Alphonse Legros'),
    ('Félix Buhot', 'French etcher of Paris and London scenes, 1847–1898', 'Félix Buhot'),
    ('James McNeill Whistler', 'American etcher of the Thames Set and Venice Sets, 1834–1903', 'James McNeill Whistler'),
    ('Frank Short', 'English etcher and mezzotinter, 1857–1945', 'Frank Short'),
    ('Muirhead Bone', 'Scottish etcher and drypoint artist, 1876–1953', 'Muirhead Bone'),
    ('D. Y. Cameron', 'Scottish etcher of architecture and landscape, 1865–1945', 'David Young Cameron'),
    ('James McBey', 'Scottish etcher, 1883–1959', 'James McBey'),
    ('Joseph Pennell', 'American etcher and lithographer, 1857–1926', 'Joseph Pennell'),
    ('Anders Zorn', 'Swedish painter-etcher, 1860–1920', 'Anders Zorn'),
]

# ---------------- B2-15 Modern Printmaking ----------------
B215_GROUPS = [
    ('Expressionist and social woodcut', ['Heinz Kiwitz', 'Clément Moreau', 'Hanna Nagel', 'Fritz Eichenberg', 'Karl Bickel', 'Vjačeslav Vasʹkovsʹkyj', 'Sofiya Nalepinska-Boychuk']),
    ('British wood-engraving revival', ['Gwen Raverat', 'Phyllis Barron', 'Joan Hassall', 'Reynolds Stone', 'Monica Poole', 'Eileen Soper', 'George Worsley Adamson', 'Malcolm Osborne']),
    ('Grosvenor School and colour linocut', ['Ethel Spowers', 'Jessie Traill']),
    ('American printmakers (etching and lithography)', ['Martin Lewis', 'Roi Partridge', 'John R. Sinnock', 'Clarence William Anderson', 'Thomas Handforth', 'Lynton Richards Kistler', 'Ian Hugo', 'Ruth Chaney', 'Irving Amen',
        'Irene Aronson', 'Sante Graziani', 'Warrington Colescott', 'Charles Cajori', 'Robert Mallary', 'Peter Milton', 'Ce Roser', 'Barry Moser', 'Tadeusz Lapinski', 'Ansei Uchima', 'Glen Alps']),
    ('Print workshops and master printers (Mourlot, Crommelynck, Tamarind)', ['Fernand Mourlot', 'Aldo Crommelynck', 'Garo Antreasian', 'Irwin Hollander', 'Donald Saff', 'Claire Van Vliet', 'Julien Levy', 'Pierre Restany']),
    ('French book illustration and engraving (livre d\'artiste)', ['André Édouard Marty', 'Maximilien Vox', 'Jean Bruller', 'Marc Saint-Saëns', 'Valentin le Campion', 'Cécile Reims', 'Yves Beaujard', 'Philippe Mohlitz', 'Jean Widmer']),
    ('Chinese Modern Woodcut Movement', ['Jiang Feng']),
    ('Bengal and Indian printmaking', ['Mukul Dey', 'Chittaprosad Bhattacharya']),
    ('Rorke\'s Drift and African printmaking', ['Azaria Mbatha', 'John Muafangejo']),
    ('Latin American printmaking', ['Oswaldo Goeldi', 'Renina Katz', 'Florencia de Amesti', 'Julio Plaza', 'Francisco Copello']),
    ('Central and Eastern European graphic art', ['Jan Marcin Szancer', 'Kazimierz Mann', 'Szymon Kobyliński', 'Andrzej Heidrich', 'Czesław Słania', 'Ádám Würtz', 'Alena Kučerová']),
    ('Nordic printmaking and illustration', ['Harald Damsleth', 'Thorbjørn Egner', 'Palle Nielsen', 'Dagny Hald', 'Outi Heiskanen', 'Lars Fredrikson', 'Rie Cramer']),
    ('Italian xylography', ['Luigi Servolini', 'Nedo Mion Ferrario']),
    ('Postwar print artists', ['Birgit Skiöld', 'Jörg Schmeisser', 'Rolf Münzner', 'Shiou-Ping Liao', 'Barry Cleavin', 'Mariam A. Aleem', 'Anastasios Alevizos', 'Noel Sheridan', 'Vera Frenkel', 'Shirley Hughes']),
    ('Writers, performers and designers', ['Jackson Mac Low', 'Hannah Weiner', 'Betty Dodson', 'Terry Riley', 'Ed Bereal', 'Peter Opsvik', 'Mary Lee Bendolph']),
]
B215_MOVES = {'Pitseolak Ashoona': 'B2-6', 'Jessie Oonark': 'B2-6', 'Mary Lee Bendolph': 'H4-93', 'Peter Opsvik': 'I3-19', 'Terry Riley': 'M1-3', 'Betty Dodson': 'A5-111', 'Ed Bereal': 'A5-111', 'Vera Frenkel': 'A5-111', 'Noel Sheridan': 'A5-111'}
B215_ADD = [
    ('Käthe Kollwitz', 'German printmaker of the War and Peasants\' War cycles, 1867–1945', 'Käthe Kollwitz'),
    ('Ernst Ludwig Kirchner', 'German Expressionist (Die Brücke) woodcut artist, 1880–1938', 'Ernst Ludwig Kirchner'),
    ('Frans Masereel', 'Belgian woodcut novelist (Passionate Journey), 1889–1972', 'Frans Masereel'),
    ('Lynd Ward', 'American wood-engraved novels (Gods\' Man), 1905–1985', 'Lynd Ward'),
    ('M. C. Escher', 'Dutch graphic artist of tessellations and impossible spaces, 1898–1972', 'M._C._Escher'),
    ('Claude Flight', 'English linocut artist, teacher at the Grosvenor School, 1881–1955', 'Claude Flight'),
    ('Sybil Andrews', 'English-Canadian Grosvenor School linocut artist, 1898–1992', 'Sybil Andrews'),
    ('Stanley William Hayter', 'English engraver, founder of Atelier 17, 1901–1988', 'Stanley William Hayter'),
    ('Lu Xun', 'Chinese writer who launched the Modern Woodcut Movement in 1931, 1881–1936', 'Lu Xun'),
    ('Leopoldo Méndez', 'Mexican printmaker of the Taller de Gráfica Popular, 1902–1969', 'Leopoldo Méndez'),
    ('June Wayne', 'American lithographer, founder of the Tamarind Lithography Workshop, 1918–2011', 'June Wayne'),
]


def leaf_without(code, names):
    l = dict(LEAVES[code]); l['rows'] = [r for r in LEAVES[code]['rows'] if r[0] not in names]; return l

def rows_named(code, names):
    l = dict(LEAVES[code]); l['rows'] = [r for r in LEAVES[code]['rows'] if r[0] in names]; return l

def build(out):
    fbnames = set(n for _, ns in FB_GROUPS for n in ns)
    # B1-5
    l = leaf_without('B1-5', fbnames | set(B15_TO_B215))
    kinds = assign(l, B15_GROUPS, B15_MOVES)
    out['leaves']['B1-5'] = dict(
        axis='by sub-type of illustration (caricature, magazine, scientific, topographical, children\'s books, cartoons, fantasy, graphic design), then national comics traditions not covered by their own leaves; within each group by birth; comics artists of the Franco-Belgian, American, Marcinelle and manga traditions, poster artists and gallery artists moved to their own leaves',
        catalogues=[['https://www.loc.gov/pictures/collection/cai/', 'Library of Congress: Cabinet of American Illustration', 'original drawings by American illustrators, c. 1880–1940'],
                    ['https://www.cartoons.ac.uk/', 'British Cartoon Archive (University of Kent)', 'over 200,000 British cartoons and caricatures, searchable by artist'],
                    ['https://www.britishmuseum.org/collection/search?keyword=caricature', 'British Museum collection: caricature', 'the BM\'s satirical prints and drawings (Gillray, Rowlandson, Cruikshank)'],
                    ['https://www.illustrationhistory.org/', 'Norman Rockwell Museum: Illustration History', 'biographies and works of illustrators across periods and genres']],
        kinds=kinds)
    # Franco-Belgian comics new leaf
    fl = rows_named('B1-5', fbnames)
    fk = assign(fl, FB_GROUPS, {}, glosses={})
    out['new_leaves'].append(dict(key='NEW1', sub='B1', label='Franco-Belgian Comics', breadth='broad',
        defn='The album-format bande dessinée of France, Belgium and Switzerland from the 1930s on, built around the weeklies Tintin, Spirou and Pilote and later the adult magazines and independent presses: <i>Hergé\'s Tintin</i>, <i>Goscinny and Uderzo\'s Astérix</i>, <i>Tardi\'s Adèle Blanc-Sec</i>, <i>Blain\'s Isaac le pirate</i>. Ligne Claire and the Marcinelle School are its two named schools with their own leaves.',
        aliases='bande dessinée; BD; Franco-Belgian comics', see='B1-7; B1-8',
        src=[[wp('Franco-Belgian comics'), 'Wikipedia']],
        catalogues=[['https://www.bedetheque.com/', 'Bedetheque', 'near-complete database of every Franco-Belgian album, series and author'],
                    ['https://www.citebd.org/', 'Cité internationale de la bande dessinée et de l\'image (Angoulême)', 'museum and collection of original BD art and albums'],
                    ['https://www.comicscenter.net/', 'Belgian Comic Strip Center (Brussels)', 'the national museum of Belgian comics and its archive']],
        axis='by magazine generation: Tintin and Spirou weeklies, Pilote, the adult magazines of the 1970s–80s, realist album series, then the nouvelle bande dessinée; within each by birth',
        kinds=fk))
    # B1-6
    k = assign(LEAVES['B1-6'], B16_GROUPS, B16_MOVES)
    add(k, 'Canonical Golden Age illustrators', [(n, g, wp(u)) for n, g, u in B16_ADD], 1)
    can = [x for x in k if x[1] == 'Canonical Golden Age illustrators']
    k = can + [x for x in k if x[1] != 'Canonical Golden Age illustrators']
    out['leaves']['B1-6'] = dict(
        axis='canonical masters first, then by national school and venue (British book illustration, Punch, American Brandywine-era magazines, political cartoon weeklies, early comic strips, French and German satirical press, Scandinavian, Russian); within each by birth',
        catalogues=[['https://www.loc.gov/pictures/collection/cai/', 'Library of Congress: Cabinet of American Illustration', 'original drawings by American Golden Age illustrators'],
                    ['https://www.delart.org/collections/', 'Delaware Art Museum collection', 'the largest holding of Howard Pyle and Brandywine School illustration'],
                    ['https://collections.vam.ac.uk/search/?q=illustration', 'V&A collections: illustration', 'British book illustration drawings and prints'],
                    ['https://www.illustrationhistory.org/', 'Norman Rockwell Museum: Illustration History', 'illustrators of the Golden Age with their works']],
        kinds=k)
    # B2-14
    k = assign(LEAVES['B2-14'], B214_GROUPS, B214_MOVES)
    add(k, 'Painter-etchers of the revival', [(n, g, wp(u)) for n, g, u in B214_ADD], 1)
    can = [x for x in k if x[1] == 'Painter-etchers of the revival']
    k = can + [x for x in k if x[1] != 'Painter-etchers of the revival']
    out['leaves']['B2-14'] = dict(
        axis='the revival\'s painter-etchers first, then the trade around them (printers and publishers, critics and cataloguers), then the reproductive engravers, wood engravers and lithographers of the same decades whom the gathered data placed here; within each by birth',
        defn='The re-emergence of etching as an original art c. 1850–1930 in France, Britain and the United States, launched by Cadart\'s Société des Aquafortistes (1862) and Haden\'s Royal Society of Painter-Etchers (1880): <i>Whistler\'s Thames Set</i>, <i>Méryon\'s Eaux-fortes sur Paris</i>, <i>Seymour Haden\'s landscapes</i>.',
        catalogues=[['https://www.britishmuseum.org/collection/search?keyword=etching%20revival', 'British Museum collection: etching revival', 'the BM\'s holdings of revival etchings'],
                    ['https://www.metmuseum.org/art/collection/search?q=etching%20revival', 'The Met collection: etching revival', 'Met prints of the revival (Whistler, Haden, Méryon)'],
                    ['https://www.whistleretchings.org/', 'Whistler Etchings Project (Glasgow)', 'catalogue raisonné of all of Whistler\'s etchings'],
                    ['https://re-society.org/', 'Royal Society of Painter-Printmakers', 'the society Haden founded in 1880 and its history']],
        kinds=k)
    # B2-15
    extra = [r for r in LEAVES['B1-5']['rows'] if r[0] in B15_TO_B215]
    l = dict(LEAVES['B2-15']); l['rows'] = LEAVES['B2-15']['rows'] + extra
    k = assign(l, B215_GROUPS, B215_MOVES)
    add(k, 'Canonical modern printmakers', [(n, g, wp(u)) for n, g, u in B215_ADD], 1)
    can = [x for x in k if x[1] == 'Canonical modern printmakers']
    k = can + [x for x in k if x[1] != 'Canonical modern printmakers']
    out['leaves']['B2-15'] = dict(
        axis='canonical masters first, then by movement and technique (Expressionist and social woodcut, British wood-engraving revival, Grosvenor School linocut, American printmakers, master printers and workshops, livre d\'artiste), then regional movements; within each by birth',
        catalogues=[['https://www.moma.org/collection/?q=print', 'MoMA collection', 'MoMA\'s department of drawings and prints, searchable by artist and technique'],
                    ['https://www.britishmuseum.org/collection/search?keyword=woodcut&dateFrom=1900', 'British Museum collection: 20th-century woodcuts', 'modern prints in the BM'],
                    ['https://www.tamarind.unm.edu/', 'Tamarind Institute', 'the lithography workshop and its archive of editions'],
                    ['https://www.nga.gov/collection-search-result.html?artobj_classification=print', 'National Gallery of Art: prints', 'the NGA\'s print collection, searchable by artist']],
        kinds=k)
