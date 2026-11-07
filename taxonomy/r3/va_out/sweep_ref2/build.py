"""AAT reference sweep, part 2 (2026-11-07): new leaves for the named styles, schools, movements and wares of Getty
AAT that had no leaf, no gathered records, and no existing leaf to take them as an entry.

Source: taxonomy/audit/reference/notes_sort.csv (pipelines/r3/ref_notes.py sorts the uncovered AAT terms by their
Getty scope notes; the 'art' terms were decided cluster by cluster in taxonomy/r3/aat_decisions.csv). Each leaf below
is attested by an encyclopedia, museum or Wikipedia source found by web search on 2026-11-07.
Held (attestation not confirmed from this environment; the terms stay 'recorded'): Estridentismo, Palissy ware,
Scarlet Ware, Sialk pottery, Syro-Phoenician ivories, Arte Nucleare, Neo-Tantric art, Universal Constructivism.
"""
import json, os
W = "https://en.wikipedia.org/wiki/"
MET = "https://www.metmuseum.org/art/collection/search?q="


def met(q): return [[MET + q.replace(" ", "+"), f"The Met collection search: {q}", f"objects matching '{q}' in the Metropolitan Museum"]]
def k(name, group, note, url): return [name, group, note, "r3 " + url, 0]


def leaf(key, sub, label, defn, src, kinds, aliases="", see="", cat=None, axis="phases and centres, then artists and holding institutions"):
    return dict(key=key, sub=sub, label=label, breadth="narrow", defn=defn, aliases=aliases, see=see, src=src,
                catalogues=cat or met(label), axis=axis, kinds=kinds)


L = [
 leaf("SPATIALISM", "A5", "Spatialism", "Movement founded by Lucio Fontana in Milan in 1947 (anticipated by the Manifiesto blanco, Buenos Aires 1946) that sought to fuse colour, sound, space, movement and time, projecting art into real space with neon, television and the slashed and punctured canvas (Buchi, Tagli).",
      [[W + "Spatialism", "Wikipedia"]], [k("Lucio Fontana", "Makers", "founder; Concetto spaziale, Buchi and Tagli", W + "Lucio_Fontana"), k("Roberto Crippa", "Makers", "Spirals", W + "Spatialism")],
      aliases="Spazialismo; Spatialist", see="A5-83 Lyrical Abstraction"),
 leaf("DAUALSET", "A5", "Dau al Set", "The first post-war avant-garde group in Spain, founded in Barcelona in 1948 by Joan Brossa with Antoni Tàpies, Modest Cuixart, Joan Ponç and others, drawing on Surrealism and Dada and publishing the review Dau al Set until 1956.",
      [[W + "Dau_al_Set", "Wikipedia"]], [k("Antoni Tàpies", "Makers", "later matter painting", W + "Dau_al_Set"), k("Modest Cuixart", "Makers", "", W + "Dau_al_Set"), k("Joan Ponç", "Makers", "", W + "Dau_al_Set")],
      see="A5-66 Surrealism"),
 leaf("SUPPORTS", "A5", "Supports/Surfaces", "French group of 1966–1972 from Montpellier, Nîmes and Nice that deconstructed painting into its support (stretcher) and surface (canvas): unstretched canvases, stretchers without canvas and repeated imprinted forms, with a Marxist and structuralist theory.",
      [[W + "Supports/Surfaces", "Wikipedia"], ["https://www.nationalmusee.lu/en/exhibitions/supportssurfaces-viallat-saytour", "Nationalmusée Luxembourg"]],
      [k("Claude Viallat", "Makers", "repeated bean-shaped imprint", "https://www.nationalmusee.lu/en/exhibitions/supportssurfaces-viallat-saytour"), k("Daniel Dezeuze", "Makers", "stretchers without canvas", W + "Supports/Surfaces"), k("Patrick Saytour", "Makers", "", W + "Supports/Surfaces")]),
 leaf("SYNCHROMISM", "A5", "Synchromism", "American colour abstraction founded in Paris in 1912–1913 by Morgan Russell and Stanton Macdonald-Wright, orchestrating colour on the analogy of music (synchromies); the first American avant-garde movement to receive international attention.",
      [[W + "Synchromism", "Wikipedia"], ["https://www.britannica.com/art/Synchromism", "Britannica"]],
      [k("Morgan Russell", "Makers", "Synchromy in Green, 1913", "https://www.britannica.com/art/Synchromism"), k("Stanton Macdonald-Wright", "Makers", "", W + "Stanton_Macdonald-Wright")], see="A5-144 American Abstract Artists"),
 leaf("AMSCENE", "A5", "American Scene Painting", "Naturalistic painting of everyday American life of the 1920s–1940s, rooted in the Ashcan School and encouraged by the federal art projects of the Depression, comprising the Regionalists (Benton, Wood, Curry) and the Social Realists.",
      [["https://www.britannica.com/topic/American-Scene-painting", "Britannica"]], [k("Regionalism", "Schools & phases", "Benton, Wood and Curry", "https://www.britannica.com/topic/American-Scene-painting")],
      see="A5-73 Social Realism"),
 leaf("NABIS", "A5", "Nabis", "Group of young Paris painters (1888–c. 1900) formed around Paul Sérusier's Talisman, painted under Gauguin's guidance at Pont-Aven: Bonnard, Vuillard, Denis, Ranson, Vallotton; flat colour, decorative pattern and intimate interiors, with screens, posters and theatre design.",
      [[W + "Nabis_(art)", "Wikipedia"]], [k("Paul Sérusier", "Makers", "Le Talisman, 1888", W + "Nabis_(art)"), k("Pierre Bonnard", "Makers", "", W + "Nabis_(art)"), k("Édouard Vuillard", "Makers", "interiors", W + "Nabis_(art)"), k("Maurice Denis", "Makers", "theorist", W + "Nabis_(art)")],
      aliases="Les Nabis", see="A5-49 Post-Impressionism"),
 leaf("FANTREAL", "A5", "Vienna School of Fantastic Realism", "Group of Viennese painters formed after 1946 at the Akademie under Albert Paris Gütersloh — Ernst Fuchs, Rudolf Hausner, Arik Brauer, Wolfgang Hutter, Anton Lehmden — who painted dreamlike visions with the precision of the old masters.",
      [[W + "Vienna_School_of_Fantastic_Realism", "Wikipedia"], ["https://www.tate.org.uk/art/art-terms/f/fantastic-realism", "Tate"]],
      [k("Ernst Fuchs", "Makers", "", "https://www.tate.org.uk/art/art-terms/f/fantastic-realism"), k("Rudolf Hausner", "Makers", "", "https://www.tate.org.uk/art/art-terms/f/fantastic-realism"), k("Arik Brauer", "Makers", "", "https://www.tate.org.uk/art/art-terms/f/fantastic-realism")],
      aliases="Fantastic Realism; Phantastischer Realismus", see="A5-66 Surrealism"),
 leaf("BADPAINT", "A5", "Bad Painting", "Figurative painting that deliberately rejects good draftsmanship and taste, named by Marcia Tucker's 1978 exhibition at the New Museum, New York: deformed figures, high and low sources mixed, fantastic and irreverent content.",
      [[W + "Bad_Painting", "Wikipedia"], ["https://archive.newmuseum.org/exhibitions/5", "New Museum Digital Archive"]],
      [k("Joan Brown", "Makers", "", "https://archive.newmuseum.org/exhibitions/5"), k("Neil Jenney", "Makers", "", "https://archive.newmuseum.org/exhibitions/5"), k("William Wegman", "Makers", "", "https://archive.newmuseum.org/exhibitions/5")],
      aliases="\"Bad\" Painting", see="A5-98 Neo-Expressionism"),
 leaf("NANYANG", "A5", "Nanyang Style", "Modern painting of migrant Chinese artists in Singapore and Malaya from the 1930s to the 1960s, joining the Chinese ink tradition and the School of Paris with Southeast Asian subjects; associated with the Nanyang Academy of Fine Arts (Liu Kang, Chen Chong Swee, Cheong Soo Pieng, Chen Wen Hsi).",
      [[W + "Nanyang_Style", "Wikipedia"]], [k("Cheong Soo Pieng", "Makers", "", W + "Nanyang_Style"), k("Liu Kang", "Makers", "", W + "Nanyang_Style"), k("Chen Wen Hsi", "Makers", "", W + "Nanyang_Style")],
      aliases="Nanyang school; Nanyang art"),
 leaf("KINFORMEL", "A5", "Korean Informel", "Gestural, non-geometric abstraction in Korea from the mid-1950s to the mid-1960s, the first radical post-war movement there, linked to Art Informel and Abstract Expressionism and staged against the government-sponsored National Art Exhibition (gukjeon).",
      [["https://www.rem.routledge.com/articles/art-informel-in-korea", "Routledge Encyclopedia of Modernism"]], [k("Park Seo-bo", "Makers", "", "https://www.rem.routledge.com/articles/art-informel-in-korea")],
      aliases="Art Informel in Korea", see="A5-81 Abstract Expressionism"),
 leaf("MINJUNG", "A5", "Minjung Art", "\"People's art\" of South Korea in the 1980s, a politically engaged figurative art of the democratisation movement: paintings, woodcuts, banners (geolgae) and murals made by collectives and shown in open schools and protests.",
      [[W + "Minjung_art", "Wikipedia"]], [k("Oh Yoon", "Makers", "woodcuts", W + "Minjung_art"), k("Geolgae banner painting", "Sub-types", "large banners for rallies", W + "Minjung_art")],
      aliases="Minjung misul; People's art"),
 leaf("WOODLANDS", "A5", "Woodlands Style", "Painting of Anishinaabe and other First Nations artists founded by Norval Morrisseau in the 1960s: heavy black formlines, X-ray views and flat bright colour for legends and spiritual beings; practised by Carl Ray, Daphne Odjig, Jackson Beardy and the 'Indian Group of Seven'.",
      [[W + "Woodlands_style", "Wikipedia"]], [k("Norval Morrisseau", "Makers", "founder", W + "Norval_Morrisseau"), k("Carl Ray", "Makers", "", W + "Woodlands_style"), k("Jackson Beardy", "Makers", "", W + "Woodlands_style")],
      aliases="Woodlands school; Legend painting; Medicine painting; Anishnabe painting"),
 leaf("JAPONISME", "A5", "Japonisme", "The influence of Japanese art, especially ukiyo-e prints, on Western painting, prints and decorative arts after the opening of Japan in the 1850s: flat colour, cropped compositions and asymmetry in Manet, Whistler, Degas, Van Gogh and the Nabis, and the Anglo-Japanese style in design.",
      [["https://www.metmuseum.org/essays/japonisme", "The Met, Heilbrunn Timeline of Art History"]],
      [k("Anglo-Japanese style", "Sub-types", "British furniture and design (Godwin, Dresser)", "https://www.metmuseum.org/essays/japonisme"), k("Japonaiserie", "Sub-types", "Japanese motifs in Western decorative arts", "https://www.metmuseum.org/essays/japonisme")],
      see="B2-17 Ukiyo-e"),
 leaf("SITUATIONIST", "M1", "Situationist International", "Avant-garde of artists and theorists (1957–1972) grown out of Lettrism, led by Guy Debord, practising détournement, the dérive and psychogeography; its art included Asger Jorn's modified paintings and Pinot-Gallizio's industrial painting.",
      [[W + "Situationist", "Wikipedia"]], [k("Détournement", "Sub-types", "re-working of existing works", W + "Situationist"), k("Asger Jorn", "Makers", "modifications", W + "Situationist")],
      aliases="Situationism", see="M1-3 Fluxus"),
 leaf("TROPICALIA", "M1", "Tropicália", "Brazilian movement of the late 1960s joining installation, painting, performance, film, theatre and music, named after Hélio Oiticica's 1967 installation and allied with the musicians Caetano Veloso and Gilberto Gil.",
      [[W + "Tropicália", "Wikipedia"]], [k("Hélio Oiticica", "Makers", "Tropicália (1967), Parangolés", W + "Tropicália"), k("Lygia Clark", "Makers", "", W + "Tropicália")],
      aliases="Tropicalismo", see="A5-138 Brazilian modernism"),
 leaf("AUTODESTRUCT", "M1", "Auto-destructive Art", "Art in which destruction is part of the making, launched by Gustav Metzger in London in 1959 (acid on nylon paintings) and pursued in Jean Tinguely's self-destroying machines and the 1966 Destruction in Art Symposium.",
      [[W + "Auto-destructive_art", "Wikipedia"], ["https://www.tate.org.uk/art/art-terms/a/auto-destructive-art", "Tate"]],
      [k("Gustav Metzger", "Makers", "founder", W + "Gustav_Metzger"), k("Jean Tinguely", "Makers", "Hommage à New York, 1960", "https://www.tate.org.uk/art/art-terms/a/auto-destructive-art"), k("Destruction in Art Symposium", "Schools & phases", "London 1966, New York 1968", "https://www.tate.org.uk/art/art-terms/a/auto-destructive-art")]),
 leaf("LIGHTSPACE", "M1", "Light and Space", "Southern California movement of the 1960s–1970s making perception its subject with light, transparent resins, glass and built environments: James Turrell, Robert Irwin, Larry Bell, Doug Wheeler, Helen Pashgian, De Wain Valentine.",
      [[W + "Light_and_Space", "Wikipedia"]], [k("James Turrell", "Makers", "", W + "Light_and_Space"), k("Robert Irwin", "Makers", "", W + "Light_and_Space"), k("Larry Bell", "Makers", "", W + "Light_and_Space")],
      see="D5-121 Minimalism"),
 leaf("AFROFUT", "M2", "Afrofuturism", "Art, music and literature of the African diaspora that join science fiction, technology and Afrocentric myth to reimagine the past and future of Black people, in painting, collage, installation, film and video from the 1960s to the present.",
      [[W + "Afrofuturism", "Wikipedia"]], [k("Sun Ra", "Makers", "", W + "Afrofuturism"), k("Wangechi Mutu", "Makers", "", W + "Afrofuturism")]),
 leaf("BIOART", "M2", "Bioart", "Art practice working with live tissues, bacteria, living organisms and life processes, often in laboratories with scientists: transgenic works, tissue culture and genetic art.",
      [[W + "BioArt", "Wikipedia"]], [k("Transgenic art", "Sub-types", "", W + "BioArt"), k("Tissue culture art", "Sub-types", "", W + "BioArt")], aliases="Bio art"),
 leaf("GRAFFITI", "L2", "Graffiti Art", "Spray-painted lettering and images on walls and trains, from the New York subway writers of the 1970s to global street art: tags, throw-ups, pieces and the interlocking letters of wildstyle.",
      [[W + "Wildstyle", "Wikipedia"]], [k("Wildstyle", "Sub-types", "the most complex interlocking letter style", W + "Wildstyle"), k("Piece (masterpiece)", "Sub-types", "large multicolour work", W + "Wildstyle"), k("Throw-up", "Sub-types", "", W + "Wildstyle")],
      aliases="Aerosol art; Writing", see="L2-40 Mexican Muralism"),
 leaf("METABOLISM", "K6", "Metabolism", "Post-war Japanese architectural movement launched at the 1960 World Design Conference in Tokyo (Kikutake, Kurokawa, Maki, Otaka, with Tange), proposing megastructures with replaceable capsules on the model of organic growth: Nakagin Capsule Tower (1972).",
      [[W + "Metabolism_(architecture)", "Wikipedia"]], [k("Nakagin Capsule Tower", "Sub-types", "Kurokawa, 1972", W + "Metabolism_(architecture)"), k("Kisho Kurokawa", "Makers", "", W + "Metabolism_(architecture)"), k("Kiyonori Kikutake", "Makers", "", W + "Metabolism_(architecture)")],
      aliases="Metabolist movement", see="K6-23 Brutalist Architecture"),
 leaf("BRICKGOTHIC", "K4", "Brick Gothic", "Gothic architecture in brick of the north European plain and the Baltic (13th–16th centuries), where building stone was scarce: hall churches, town halls and castles of the Hanseatic towns and the Teutonic Order, with glazed and moulded brick ornament (St Mary's, Lübeck; Malbork).",
      [[W + "Brick_Gothic", "Wikipedia"]], [k("St Mary's Church, Lübeck", "Sub-types", "the model Hanseatic basilica", W + "Brick_Gothic"), k("Teutonic Order castles", "Sub-types", "Malbork", W + "Brick_Gothic")],
      aliases="Backsteingotik", see="K4-13 Gothic Architecture"),
 leaf("CELTREV", "I3", "Celtic Revival", "Decorative and fine arts of the 19th- and early-20th-century revival of Celtic culture in Ireland, Scotland and the Isle of Man: interlace and knotwork from the Book of Kells and early metalwork in jewellery, silver, pewter (Archibald Knox for Liberty), book illustration and painting (John Duncan).",
      [[W + "Celtic_Revival", "Wikipedia"]], [k("Archibald Knox", "Makers", "Liberty Cymric silver and Tudric pewter", W + "Celtic_Revival"), k("John Duncan", "Makers", "painter", W + "Celtic_Revival")],
      aliases="Celtic Twilight; Gaelic revival art", see="I3-14 Arts and Crafts Movement"),
 leaf("PLUMBATE", "E1", "Plumbate Ware", "Mesoamerican trade ware of the Soconusco (Pacific coast of Guatemala and Chiapas) with a lustrous grey glaze-like slip fired from iron-rich clay: San Juan Plumbate of the Late Classic and the widely traded Tohil Plumbate (c. 900–1200), often effigy vessels.",
      [["https://es.wikipedia.org/wiki/Cer%C3%A1mica_plumbate", "Wikipedia (es)"], ["https://es.wikipedia.org/wiki/Cer%C3%A1mica_Tohil_Plomiza", "Wikipedia (es)"]],
      [k("Tohil Plumbate", "Sub-types", "Early Postclassic effigy vessels", "https://es.wikipedia.org/wiki/Cer%C3%A1mica_Tohil_Plomiza"), k("San Juan Plumbate", "Sub-types", "Late Classic", "https://es.wikipedia.org/wiki/Cer%C3%A1mica_plumbate")],
      see="E1-43 Maya Ceramics"),
 leaf("SUE", "E3", "Sue Ware", "Blue-grey high-fired stoneware of Japan (5th–12th centuries), introduced from the Gaya region of Korea and made in tunnel kilns: jars, recumbent bottles and pedestal bowls with natural ash glaze, used in tombs and rites; produced at the Suemura and later the Sanage kilns.",
      [[W + "Sue_pottery", "Wikipedia"]], [k("Sanage kilns", "Schools & phases", "Nagoya area; ash-glazed successor wares", W + "Sue_pottery"), k("Yokobe (recumbent bottle)", "Sub-types", "", W + "Sue_pottery")],
      aliases="Sueki; Sue pottery", see="E1-19 Yayoi Pottery"),
 leaf("HASSUNA", "E1", "Hassuna Pottery", "Neolithic pottery of northern Mesopotamia (c. 6000–5500 BCE) named after Tell Hassuna: coarse Archaic Hassuna ware and the incised and red-painted Standard Hassuna ware, followed by imported Samarra painted ware.",
      [["http://www.britannica.com/place/Hassuna", "Britannica"]], [k("Archaic Hassuna", "Schools & phases", "", "http://www.britannica.com/place/Hassuna"), k("Standard Hassuna", "Schools & phases", "incised and painted", "http://www.britannica.com/place/Hassuna")],
      see="E1-149 Samarra Ware"),
 leaf("KHABUR", "E1", "Khabur Ware", "Wheel-made painted pottery of northern Mesopotamia and the Khabur basin (c. 1900–1500 BCE), with monochrome geometric bands in red, brown or black on jars, beakers and bowls; named by Max Mallowan at Chagar Bazar.",
      [["http://leilan.yale.edu/resources/habur-ware-ceramics", "Tell Leilan Project, Yale"]], [k("Chagar Bazar", "Schools & phases", "type site", "http://leilan.yale.edu/resources/habur-ware-ceramics")],
      aliases="Habur ware", see="E1-151 Ubaid Pottery"),
 leaf("NUZI", "E1", "Nuzi Ware", "Fine painted ware of the Mitanni kingdom (15th–early 13th century BCE), first identified at Nuzi: tall goblets with white designs of birds, plants and spirals on a dark band.",
      [[W + "Nuzi_ware", "Wikipedia"]], [k("Nuzi goblet", "Sub-types", "white-on-dark painted goblet", W + "Nuzi_ware")], see=""),
 leaf("PROVOKE", "J1", "Provoke", "Japanese photography of the magazine Provoke (1968–1969, Takuma Nakahira, Daidō Moriyama, Yutaka Takanashi) and its circle: grainy, blurred, out-of-focus images (are-bure-boke) against objective photojournalism.",
      [[W + "Provoke_(magazine)", "Wikipedia"], ["https://archive.artic.edu/ryerson/provoke/4", "Art Institute of Chicago"]],
      [k("Are-bure-boke", "Sub-types", "rough, blurry, out of focus", W + "Provoke_(magazine)"), k("Daidō Moriyama", "Makers", "", W + "Provoke_(magazine)"), k("Takuma Nakahira", "Makers", "", "https://archive.artic.edu/ryerson/provoke/4")]),
 leaf("SUBJPHOTO", "J1", "Subjective Photography", "Post-war experimental art photography named by Otto Steinert's exhibitions Subjektive Fotografie (Saarbrücken 1951–1958): photographs made from the photographer's inner visual impulse rather than as documents, with high contrast, abstraction and photograms.",
      [["https://www.nasjonalmuseet.no/utstillinger-og-arrangementer/nasjonalmuseet/utstillinger/2021/samlingsutstillingen/endringer-i-samlingspresentasjonen/rom-81", "Nasjonalmuseet, Oslo"]],
      [k("Otto Steinert", "Makers", "founder", "https://www.nasjonalmuseet.no/utstillinger-og-arrangementer/nasjonalmuseet/utstillinger/2021/samlingsutstillingen/endringer-i-samlingspresentasjonen/rom-81"), k("fotoform", "Schools & phases", "group of 1949", "https://www.nasjonalmuseet.no/utstillinger-og-arrangementer/nasjonalmuseet/utstillinger/2021/samlingsutstillingen/endringer-i-samlingspresentasjonen/rom-81")],
      aliases="Subjektive Fotografie"),
]
json.dump(dict(leaves={}, new_leaves=L, moves_out=[], dropped=[]), open(os.path.join(os.path.dirname(__file__), "result.json"), "w"), ensure_ascii=False, indent=1)
print(len(L), "new leaves")
