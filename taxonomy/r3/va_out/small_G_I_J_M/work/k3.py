# knowledge for J1 photography, M1/M2 new media; AG = artist groupings {code: [(group, [names])]}
from kutil import met, vam, bm, si, moma, tate, wpl, U
K, AG = {}, {}
SUB, SCH, MAK = 'Sub-types', 'Schools & phases', 'Makers'
GETTY = lambda q: ['https://www.getty.edu/art/collection/search?q=' + q, 'Getty Museum collection search: ' + q, 'photographs in the J. Paul Getty Museum']

K['J1-1'] = dict(cats=[moma('modernist photography'), GETTY('modernist'), ['https://www.icp.org/', 'International Center of Photography', 'collection and archive']],
  axis='artist-led: photographers by named group (Group f/64, Neue Sachlichkeit), then by country',
  add=[('Paul Strand', 'Group f/64 and American straight modernism', 'American modernist photographer, 1890–1976', 'Paul_Strand', 1),
       ('Edward Weston', 'Group f/64 and American straight modernism', 'American photographer, co-founder of Group f/64, 1886–1958', 'Edward_Weston', 1),
       ('Imogen Cunningham', 'Group f/64 and American straight modernism', 'American photographer, Group f/64, 1883–1976', 'Imogen_Cunningham', 1),
       ('Albert Renger-Patzsch', 'Neue Sachlichkeit photography', 'German photographer of Die Welt ist schön (1928), 1897–1966', 'Albert_Renger-Patzsch', 1),
       ('Karl Blossfeldt', 'Neue Sachlichkeit photography', 'German photographer of plant forms, 1865–1932', 'Karl_Blossfeldt', 1),
       ('August Sander', 'Neue Sachlichkeit photography', 'German portrait photographer, People of the 20th Century, 1876–1964', 'August_Sander', 1),
       ('Group f/64', SCH, 'San Francisco group of sharp-focus photographers, 1932–35', 'Group_f/64', 0)])
AG['J1-2'] = [('Provoke (Japan)', ['Daidō Moriyama', 'Takuma Nakahira']),
  ('New York School of photography (1930s–1950s)', ['Helen Levitt', 'Lisette Model', 'Louis Faurer', 'Sid Grossman', 'Leon Levinstein', 'Rebecca Lepkoff', 'Saul Leiter', 'William Klein', 'Robert Frank', 'Vivian Maier']),
  ('Social landscape (1960s–1970s America)', ['Garry Winogrand', 'Lee Friedlander', 'Tod Papageorge', 'Joel Meyerowitz', 'Mark Cohen', 'Elliott Erwitt', 'Jill Freedman']),
  ('Later street photography (Magnum and after)', ['Alex Webb', 'Bruce Gilden', 'Jeff Mermelstein']),
  ('Netherlands', ['Ed van der Elsken']), ('United Kingdom', ['Tony Ray-Jones']), ('Chile', ['Sergio Larraín']), ('India', ['Raghubir Singh'])]
K['J1-2'] = dict(cats=[moma('street photography'), ['https://www.magnumphotos.com/', 'Magnum Photos', 'agency archive of its photographers'], GETTY('street')],
  axis='artist-led: photographers by named group or school (Provoke, New York School, social landscape), then by country',
  add=[('Henri Cartier-Bresson', 'Later street photography (Magnum and after)', 'French photographer, The Decisive Moment (1952), 1908–2004', 'Henri_Cartier-Bresson', 1)])
AG['J1-3'] = [('Weimar picture press (1920s–1930s)', ['Erich Salomon', 'Felix H. Man', 'Alfred Eisenstaedt', 'Martin Munkácsi']),
  ('Magnum Photos founders and members', ['Robert Capa', 'David Seymour', 'George Rodger', 'Werner Bischof', 'Inge Morath', 'Burt Glinn', 'Marc Riboud', 'Ian Berry', 'Philip Jones Griffiths', 'Gilles Peress', 'Thomas Hoepker']),
  ('Life magazine photographers', ['Margaret Bourke-White', 'W. Eugene Smith', 'Carl Mydans', 'David Douglas Duncan', 'Larry Burrows']),
  ('Spanish Civil War and Second World War', ['Gerda Taro', 'Joe Rosenthal']),
  ('Soviet photojournalists', ['Arkady Shaikhet', 'Max Alpert', 'Georgy Zelma', 'Yevgeny Khaldei']),
  ('Vietnam War photographers', ['Horst Faas', 'Henri Huet', 'Tim Page', 'Eddie Adams', 'Nick Ut', 'Malcolm Browne', 'Catherine Leroy', 'Gilles Caron', 'Ronald L. Haeberle', 'Don McCullin']),
  ('Press and spot news', ['Weegee', 'Peter Leibing']),
  ('Contemporary conflict photographers', ['James Nachtwey', 'Kevin Carter', 'Tim Hetherington'])]
K['J1-3'] = dict(cats=[['https://www.magnumphotos.com/', 'Magnum Photos', 'agency archive'], ['https://www.worldpressphoto.org/', 'World Press Photo', 'archive of contest winners since 1955'], ['https://www.icp.org/', 'International Center of Photography', 'collection and archive']],
  axis='artist-led: photojournalists by agency, magazine or war (Weimar press, Magnum, Life, Soviet, Vietnam), then later generations',
  add=[('Raising the Flag on Iwo Jima (Joe Rosenthal, 1945)', 'Named photographs', 'Associated Press photograph, 23 February 1945', 'Raising_the_Flag_on_Iwo_Jima', 0),
       ('The Falling Soldier (Robert Capa, 1936)', 'Named photographs', 'Spanish Civil War photograph published in Vu', 'The_Falling_Soldier', 0),
       ('Raising a Flag over the Reichstag (Yevgeny Khaldei, 1945)', 'Named photographs', 'photograph of 2 May 1945, Berlin', 'Raising_a_Flag_over_the_Reichstag', 0),
       ('The Terror of War (Nick Ut, 1972)', 'Named photographs', 'Associated Press photograph of Phan Thị Kim Phúc', 'The_Terror_of_War', 0)])
AG['J1-4'] = [('Paris Surrealist circle', ['Man Ray', 'Jacques-André Boiffard', 'Maurice Tabard', 'Dora Maar', 'Lee Miller', 'Claude Cahun']),
  ('Belgian Surrealism', ['Paul Nougé', 'Max Servais']), ('Czech Surrealism', ['Emila Medková']), ('Japan', ['Toshiko Okanoue']),
  ('Mexico', ['Manuel Álvarez Bravo', 'Kati Horna']), ('Argentina', ['Grete Stern']), ('United States', ['Clarence John Laughlin', 'Frederick Sommer'])]
K['J1-4'] = dict(cats=[moma('surrealist photography'), ['https://www.centrepompidou.fr/en/recherche/oeuvres?terms=surr%C3%A9alisme', 'Centre Pompidou collection search', 'Surrealist photographs'], GETTY('surrealist')],
  axis='artist-led: photographers by Surrealist circle (Paris, Belgian, Czech), then by country')
AG['J1-5'] = [('Pioneers (1910s–1930s)', ['Adolph de Meyer', 'George Hoyningen-Huene', 'Horst P. Horst', 'Cecil Beaton', 'Martin Munkácsi', 'Toni Frissell']),
  ('Post-war Vogue and Harper’s Bazaar (1940s–1960s)', ['Irving Penn', 'Richard Avedon', 'Louise Dahl-Wolfe', 'Lillian Bassman', 'Erwin Blumenfeld', 'Frances McLaughlin-Gill', 'Norman Parkinson', 'Melvin Sokolsky', 'Hiro', 'Bert Stern', 'Willy Maywald', 'Regina Relang', 'Jeanloup Sieff', 'Frank Horvat', 'Gian Paolo Barbieri']),
  ('The Black Trinity (Swinging London)', ['David Bailey', 'Brian Duffy', 'Terence Donovan']),
  ('1970s provocation', ['Helmut Newton', 'Guy Bourdin', 'Deborah Turbeville', 'Chris von Wangenheim', 'Sarah Moon', 'Francesco Scavullo', 'Hans Feurer', 'Arthur Elgort']),
  ('Supermodel era (1980s–1990s)', ['Patrick Demarchelier', 'Peter Lindbergh', 'Steven Meisel', 'Herb Ritts', 'Bruce Weber', 'Albert Watson', 'Ellen von Unwerth', 'Paolo Roversi']),
  ('Late 1990s and 2000s', ['Corinne Day', 'Nick Knight', 'Craig McDean', 'Mario Testino', 'Inez van Lamsweerde'])]
K['J1-5'] = dict(cats=[['https://www.vogue.com/fashion-shows', 'Vogue Runway', 'archive of fashion shows'], vam('fashion photograph'), ['https://www.condenast.com/', 'Condé Nast', 'publisher archive of Vogue']],
  axis='artist-led: photographers by phase and named group (pioneers, post-war magazines, the Black Trinity, 1970s, supermodel era, later)')
K['J1-5']['cats'] = [vam('fashion photograph'), moma('fashion photography'), GETTY('fashion')]
AG['J1-6'] = [('Teachers', ['Bernd Becher', 'Hilla Becher']), ('First Becher class (from 1976)', ['Tata Ronkholz', 'Candida Höfer', 'Axel Hütte', 'Thomas Struth', 'Andreas Gursky', 'Thomas Ruff']), ('Later students', ['Laurenz Berges', 'Simone Nieweg', 'Elger Esser'])]
K['J1-6'] = dict(cats=[moma('Becher'), tate('Becher'), ['https://www.photographie-sk-kultur.de/', 'Die Photographische Sammlung / SK Stiftung Kultur, Cologne', 'Bernd and Hilla Becher archive']],
  axis='artist-led: the teachers, then the Becher students by class generation',
  add=[('Water Towers (Bernd and Hilla Becher)', 'Named series', 'typological grids of water towers, 1960s–1980s', 'Bernd_and_Hilla_Becher', 0)])
AG['J1-10'] = [('Bauhaus and German New Vision', []), ('Soviet New Vision', []), ('Paris New Vision', []), ('Zen’ei shashin (Japan)', ['Kansuke Yamamoto']), ('Fotoform (Germany)', ['Otto Steinert'])]
K['J1-10'] = dict(cats=[moma('New Vision photography'), GETTY('New Vision'), ['https://www.bauhaus.de/en/', 'Bauhaus-Archiv', 'Moholy-Nagy and Bauhaus photography']],
  axis='artist-led: photographers by circle (Bauhaus, Soviet, Paris), then later heirs (Zen’ei shashin, Fotoform) and by country',
  add=[('László Moholy-Nagy', 'Bauhaus and German New Vision', 'Hungarian Bauhaus master, author of Malerei Fotografie Film (1925), 1895–1946', 'László_Moholy-Nagy', 1),
       ('Umbo', 'Bauhaus and German New Vision', 'German photographer, 1902–80', 'Umbo', 1), ('Aleksandr Rodchenko', 'Soviet New Vision', 'Soviet Constructivist photographer, 1891–1956', 'Alexander_Rodchenko', 1),
       ('Germaine Krull', 'Paris New Vision', 'German-born photographer of Métal (1928), 1897–1985', 'Germaine_Krull', 1), ('Florence Henri', 'Paris New Vision', 'American-born photographer in Paris, 1893–1982', 'Florence_Henri', 1),
       ('Film und Foto (Stuttgart, 1929)', SCH, 'Werkbund exhibition that defined the New Vision', 'Film_und_Foto', 0)])
AG['J1-11'] = []
K['J1-11'] = dict(cats=[['https://www.mediatheque-patrimoine.culture.gouv.fr/', 'Médiathèque du patrimoine et de la photographie', 'French state photography archives (incl. Ronis, Boubat)'], moma('Doisneau')],
  axis='artist-led: photographers by country of activity (France first)',
  add=[('Robert Doisneau', 'France', 'French humanist photographer, 1912–94', 'Robert_Doisneau', 1), ('Izis', 'France', 'Lithuanian-born French photographer, 1911–80', 'Izis_Bidermanas', 1),
       ('Sabine Weiss', 'France', 'Swiss-born French photographer, 1924–2021', 'Sabine_Weiss', 1), ('Janine Niépce', 'France', 'French photographer, 1921–2007', 'Janine_Niépce', 1),
       ('Le Baiser de l’hôtel de ville (Doisneau, 1950)', 'Named photographs', 'photograph made for Life; Atelier Robert Doisneau', 'Le_Baiser_de_l%27hôtel_de_ville', 0)])
AG['M1-3'] = [('George Maciunas and New York Fluxus', ['George Maciunas', 'George Brecht', 'Robert Watts', 'Alison Knowles', 'Geoffrey Hendricks', 'Ay-O', 'Joe Jones', 'Henry Flynt', 'Ben Patterson', 'Emmett Williams', 'Philip Corner', 'La Monte Young', 'Al Hansen', 'Allan Kaprow', 'John Cage']),
  ('Japanese Fluxus', ['Yoko Ono', 'Shigeko Kubota', 'Mieko Shiomi', 'Takako Saito', 'Yoshi Wada', 'Genpei Akasegawa']),
  ('German Fluxus', ['Joseph Beuys', 'Wolf Vostell', 'Tomas Schmit']),
  ('European Fluxus', ['Daniel Spoerri', 'Dieter Roth', 'Eric Andersen', 'Milan Knížák', 'Giuseppe Chiari', 'Öyvind Fahlström', 'Jean Dupuy', 'Jacques Halbert', 'John Armleder']),
  ('Zaj (Spain)', ['Esther Ferrer']), ('Latin America', ['Catalina Parra', 'Lotty Rosenfeld', 'Jaime Davidovich']), ('Later associates', ['Maria Eichhorn'])]
K['M1-3'] = dict(cats=[moma('Fluxus'), ['https://www.fondazionebonotto.org/', 'Fondazione Bonotto', 'Fluxus collection and archive'], tate('Fluxus')],
  axis='artist-led: by Fluxus circle (Maciunas’s New York group, Japanese, German, European), then Zaj, Latin America and later associates',
  add=[('Fluxkit', 'Named works', 'Maciunas’s boxed anthology of Fluxus multiples, 1964–65', 'Fluxus', 0), ('Cut Piece (Yoko Ono, 1964)', 'Named works', 'performance first given in Kyoto, 1964', 'Cut_Piece', 0)])
AG['M1-4'] = [('New York Correspondence School', ['Ray Johnson']), ('United States', ['Dick Higgins']), ('Hungary', ['Endre Tót', 'Géza Perneczky']), ('East Germany', ['Ruth Wolf-Rehfeldt', 'Robert Rehfeldt']), ('Poland', ['Jan Świdziński', 'Ewa Partum']),
  ('France', ['Ben Vautier', 'Robert Filliou', 'Henri Chopin', 'Fred Forest', 'Hervé Fischer', 'Julien Blaine']), ('Italy', ['Maurizio Nannucci']), ('West Germany', ['Dieter Hacker', 'Bernhard Blume', 'Martin Kippenberger']),
  ('Austria', ['Gerhard Rühm']), ('United Kingdom', ['John Furnival']), ('Spain', ['Menchu Lamas', 'Francesc Abad']), ('Nordic countries', ['Lenke Rothman', 'Lars Vilks', 'J.O. Mallander']), ('Japan', ['Shôzô Shimamoto']),
  ('Latin America', ['Edgardo Antonio Vigo', 'Paulo Bruscky', 'Marie Orensanz', 'Ulises Carrión', 'Guillermo Deisler'])]
K['M1-4'] = dict(cats=[moma('mail art'), ['https://www.getty.edu/research/collections/', 'Getty Research Institute collections', 'mail-art archives'], ['https://en.wikipedia.org/wiki/Mail_art', 'Mail art (Wikipedia)', 'overview and networks']],
  axis='artist-led: founder (New York Correspondence School), then networks by country of activity',
  add=[('Ray Johnson', 'New York Correspondence School', 'American artist, founder of the New York Correspondence School, 1927–95', 'Ray_Johnson', 1), ('Artistamps', SUB, 'artists’ postage stamps', 'Artistamp', 0)])
AG['M1-5'] = [('Celant’s Arte Povera group (1967–72)', ['Giovanni Anselmo', 'Alighiero Boetti', 'Luciano Fabro', 'Yannis Kounellis', 'Mario Merz', 'Marisa Merz', 'Giulio Paolini', 'Pino Pascali', 'Michelangelo Pistoletto', 'Emilio Prini', 'Gilberto Zorio']),
  ('Precursors', ['Piero Manzoni']), ('International associates', ['Ger van Elk', 'Irina Zatulovskaya'])]
K['M1-5'] = dict(cats=[['https://www.castellodirivoli.org/', 'Castello di Rivoli Museo d’Arte Contemporanea', 'major Arte Povera holdings'], tate('Arte Povera'), moma('Arte Povera')],
  axis='artist-led: Germano Celant’s core group, then precursors and international associates',
  add=[('Pier Paolo Calzolari', 'Celant’s Arte Povera group (1967–72)', 'Italian Arte Povera artist, b. 1943', 'Pier_Paolo_Calzolari', 1),
       ('Venus of the Rags (Pistoletto, 1967)', 'Named works', 'concrete Venus facing a heap of rags; Tate and other versions', 'Venus_of_the_Rags', 0)])
AG['M1-6'] = [('American land art (earthworks)', ['Nancy Holt', 'Robert Smithson', 'Michael Heizer', 'Walter De Maria', 'Robert Morris', 'Dennis Oppenheim', 'Agnes Denes']), ('Christo and Jeanne-Claude', ['Christo']), ('British land art', []),
  ('Environmental art', ['Alan Sonfist', 'Eve Andree Laramee', 'Andy Goldsworthy', 'Nils-Udo'])]
K['M1-6'] = dict(cats=[['https://www.diaart.org/', 'Dia Art Foundation', 'Spiral Jetty, The Lightning Field and other earthworks'], ['https://holtsmithsonfoundation.org/', 'Holt/Smithson Foundation', 'works of Smithson and Holt'], tate('land art')],
  axis='artist-led: American earthworks, Christo, environmental art; then works: every gathered land-art site with Wikipedia sitelinks ≥ 2, by date',
  add=[('Nancy Holt', 'American land art (earthworks)', 'American land artist, Sun Tunnels (1976), 1938–2014', 'Nancy_Holt', 1), ('Richard Long', 'British land art', 'British land artist, A Line Made by Walking (1967), b. 1945', 'Richard_Long_(artist)', 1),
       ('Hamish Fulton', 'British land art', 'British walking artist, b. 1946', 'Hamish_Fulton', 1)])
AG['M1-7'] = [('Core Actionists', ['Günter Brus', 'Otto Muehl', 'Hermann Nitsch', 'Rudolf Schwarzkogler']), ('Associated', ['Valie Export'])]
K['M1-7'] = dict(cats=[['https://www.mumok.at/en', 'mumok – Museum moderner Kunst Stiftung Ludwig Wien', 'major Viennese Actionism collection'], ['https://www.nitsch-foundation.com/', 'Nitsch Foundation', 'Hermann Nitsch archive'], tate('Viennese Actionism')],
  axis='artist-led: the four core Actionists, then associates',
  add=[('Orgien Mysterien Theater (Nitsch)', 'Named works', 'Nitsch’s cycle of ritual actions from 1957', 'Hermann_Nitsch', 0)])
AG['M1-8'] = [('Body art', ['Gina Pane']), ('Long-durational performance', ['Marina Abramović']), ('United Kingdom', ['Stuart Brisley'])]
K['M1-8'] = dict(cats=[tate('performance art'), moma('performance'), ['https://www.li-ma.nl/', 'LIMA, Amsterdam', 'media and performance art archive']],
  axis='artist-led: by named tendency (body art, long-durational performance), then by country',
  add=[('Chris Burden', 'Body art', 'American performance artist, Shoot (1971), 1946–2015', 'Chris_Burden', 1), ('Vito Acconci', 'Body art', 'American performance artist, 1940–2017', 'Vito_Acconci', 1),
       ('Carolee Schneemann', 'Body art', 'American artist, Interior Scroll (1975), 1939–2019', 'Carolee_Schneemann', 1), ('Ulay', 'Long-durational performance', 'German artist, Abramović’s partner 1976–88, 1943–2020', 'Ulay', 1),
       ('Tehching Hsieh', 'Long-durational performance', 'Taiwanese-American artist of one-year performances, b. 1950', 'Tehching_Hsieh', 1),
       ('Rhythm 0 (Abramović, 1974)', 'Named works', 'six-hour performance, Studio Morra, Naples', 'Rhythm_0', 0),
       ('I Like America and America Likes Me (Beuys, 1974)', 'Named works', 'action with a coyote, René Block Gallery, New York', 'I_Like_America_and_America_Likes_Me', 0)])
AG['M2-1'] = [('Computer art pioneers (1960s–1970s)', ['Frieder Nake', 'Georg Nees', 'A. Michael Noll', 'Vera Molnár', 'Manfred Mohr', 'Charles Csuri', 'Lillian Schwartz', 'Desmond Paul Henry', 'Jean-Pierre Hébert', 'Colette Bangert', 'Zdeněk Sýkora', 'Peter Struycken']),
  ('Contemporary generative art', ['Casey Reas', 'Hicham Berrada'])]
K['M2-1'] = dict(cats=[['https://www.digitalartarchive.at/', 'Archive of Digital Art (ADA)', 'database of digital and computer art'], vam('computer art'), ['https://zkm.de/en/collection', 'ZKM Center for Art and Media, Karlsruhe', 'media art collection']],
  axis='artist-led: computer-art pioneers, then contemporary generative artists',
  add=[('Processing', SUB, 'programming language for visual art by Casey Reas and Ben Fry, 2001', 'Processing', 0), ('Cybernetic Serendipity (London, 1968)', SCH, 'ICA exhibition of computer and cybernetic art', 'Cybernetic_Serendipity', 0)])
AG['M2-2'] = [('net.art (1990s)', ['Alexei Shulgin', 'Vuk Ćosić', 'Joan Heemskerk', 'Dirk Paesmans', 'Natalie Bookchin', 'Wolfgang Staehle', 'Shu Lea Cheang']),
  ('Post-internet generation', ['Petra Cortright', 'Jon Rafman', 'Amalia Ulman', 'Constant Dullaart', 'Aram Bartholl', 'Rafaël Rozendaal', 'Evan Roth'])]
K['M2-2'] = dict(cats=[['https://artbase.rhizome.org/', 'Rhizome ArtBase', 'archive of over 2,000 works of net art'], ['https://anthology.rhizome.org/', 'Net Art Anthology (Rhizome)', '100 works of net art history'], ['https://www.digitalartarchive.at/', 'Archive of Digital Art (ADA)', 'digital art database']],
  axis='artist-led: net.art pioneers, then the post-internet generation',
  add=[('Olia Lialina', 'net.art (1990s)', 'Russian net artist, My Boyfriend Came Back from the War (1996), b. 1971', 'Olia_Lialina', 1), ('Heath Bunting', 'net.art (1990s)', 'British net artist, b. 1966', 'Heath_Bunting', 1)])
AG['M2-3'] = [('Pioneers', ['Harold Cohen']), ('Machine-learning artists', ['Mario Klingemann', 'Refik Anadol', 'Anna Ridler'])]
K['M2-3'] = dict(cats=[['https://www.digitalartarchive.at/', 'Archive of Digital Art (ADA)', 'digital art database'], moma('Refik Anadol')],
  axis='artist-led: pioneers, then machine-learning artists',
  add=[('Obvious', 'Machine-learning artists', 'Paris collective, Edmond de Belamy (2018)', 'Obvious_(art_collective)', 1), ('Edmond de Belamy (Obvious, 2018)', 'Named works', 'GAN portrait sold at Christie’s, October 2018', 'Edmond_de_Belamy', 0)])
AG['M2-4'] = []
K['M2-4'] = dict(cats=[['https://www.eai.org/', 'Electronic Arts Intermix', 'distributor and archive of over 4,000 video works'], ['https://www.vdb.org/', 'Video Data Bank', 'video art archive, Chicago'], ['https://www.li-ma.nl/', 'LIMA, Amsterdam', 'media art archive']],
  axis='artist-led: video artists by country of activity',
  add=[('Nam June Paik', 'United States', 'Korean-American founder of video art, 1932–2006', 'Nam_June_Paik', 1), ('Bill Viola', 'United States', 'American video artist, 1951–2024', 'Bill_Viola', 1),
       ('Joan Jonas', 'United States', 'American video and performance artist, b. 1936', 'Joan_Jonas', 1), ('Peter Campus', 'United States', 'American video artist, b. 1937', 'Peter_Campus', 1),
       ('TV Buddha (Nam June Paik, 1974)', 'Named works', 'closed-circuit video sculpture; Stedelijk Museum, Amsterdam', 'TV_Buddha', 0)])
AG['I3-17'] = [('Associated', ['Edith Heath'])]
AG['I3-18'] = [('Founding circle', ['Shōji Hamada', 'Kawai Kanjirō', 'Kenkichi Tomimoto']), ('Mingei potters and craftsmen', ['Hajime Katō', 'Fujio Koyama', 'Toyozō Arakawa', 'Kaneshige Tōyō', 'Atsuya Hamada', 'Tappo Narui', 'Fujio Narui', 'Gen Murata', 'Saburō Kimura', 'Hokudo Mimura', 'Sachi Fujii', 'Kiichirō Kenmoku', 'Kōichi Kenmoku', 'Kazumasa Murasawa', 'Toshio Gunji', 'Takashi Kōno', 'Hiroshi Ohchi', 'Onisaburo Deguchi'])]
OV = {
 'J1-2': {'Provoke': ('Schools & phases', 'Japanese photography magazine and group of 1968–69 (are, bure, boke)')},
 'J1-3': {'Magnum Photos': ('Schools & phases', 'cooperative agency founded 1947 by Capa, Cartier-Bresson, Rodger and Seymour'), 'War photography': ('Sub-types', 'photography of armed conflict')},
 'J1-6': {'Bernd and Hilla Becher': ('DROP', 'duplicate of the separate Bernd Becher and Hilla Becher rows')},
 'M2-1': {'Computer art': ('Schools & phases', 'plotter and computer graphics art of the 1960s–1970s'), 'Frieder Nake, Georg Nees and A. Michael Noll': ('DROP', 'duplicate of the three individual rows'), 'Vera Molnár': ('Computer art pioneers (1960s–1970s)', 'Hungarian-French computer-art pioneer, 1924–2023')},
 'M2-2': {'Post-internet': ('Schools & phases', 'art after the internet, from c. 2008'), 'JODI': ('net.art (1990s)', 'Joan Heemskerk and Dirk Paesmans, net art duo from 1994'), 'Crypto art (NFT art)': ('Sub-types', 'art traded as non-fungible tokens, from 2017')},
 'M2-3': {'AARON': ('Sub-types', 'Harold Cohen’s drawing program, from 1973')},
 'M1-6': {x: ('DROP', 'regional bin row, replaced by the works list') for x in ['Modern land art (China)', 'Modern land art (Egypt & Nubia)', 'Modern land art (Mesoamerica)', 'Modern land art (N. America Indigenous)', 'Modern land art (Aboriginal Australia)', 'Modern land art (Oceania)', 'Modern land art (Western Europe)', 'Modern land art (C&E Europe)']},
}
