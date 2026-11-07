# bucket_modern_world — A5-110 Modern Art, artists outside Western Europe

Input: 2,399 maker rows (all is_maker 1). Output: every maker placed once.
- 405 moved out (`moves_out`) to existing leaves, 133 into 10 new leaves, 1,861 kept in A5-110.
- Kept rows have a gloss built from the evidence (birth year; countries). Machine glosses removed.

## Moves to existing leaves (largest)
Illustration B1-5 (34), Concrete Art A5-87 (23: Brazilian Ruptura/Neo-Concrete, Argentine AACI/Madí, Cuban Diez Pintores Concretos), Modern Architecture K6-22 (20 architects; plus Brutalist K6-23 x2, Postmodern K6-24 x1), American Comics B1-3 (19), Mexican Muralism L2-40 (19), Sōsaku-hanga B2-19 (16), Golden Age of Illustration B1-6 (15), Modern Printmaking B2-15 (14), Naïve Art A5-79 (13), Art Brut A5-80 (13), Impressionism A5-47 (13, American/Australian/Brazilian), Surrealism A5-66 (12, incl. Japanese and Egyptian Art and Liberty surrealists), Yōga A5-108 (12), Regionalism A5-71 (11, incl. California Scene), Kinetic Art D5-120 (11), Social Realism A5-73 (10), Conceptual Art M1-2 (9), Nihonga A2-13 (8), Harlem Renaissance A5-75 (8), Black Arts Movement A5-100 (8), Hurufiyya A5-106 (8, incl. Saqqakhaneh painters), Magic Realism A5-69 (7), Haitian Painting A6-31 (6), Bengal School A5-109 (6), Precisionism A5-70 (6), Photorealism A5-96 (6), Abstract Expressionism A5-81 (6); smaller moves to Manga, Video Art, calligraphy leaves (C1-3, C1-9, C1-10), Mingei, Tonalism, Color Field, Op Art, Minimalism/Postminimalism, Land Art, Performance, Lingnan, Persian Miniature, Sơn Mài, Balinese, Madhubani, Warli, Tingatinga, Inuit Printmaking, Shin-hanga, Type Design, etc.

## New leaves (Wikipedia titles)
Gutai group (10), Group of Seven (artists) (8), Brazilian modernism (17), Progressive Artists' Group (9), Generación de la Ruptura (14), Taller de Gráfica Popular (12, sub B2), Indigenismo (9, Andean), Chicago Imagists (15, incl. Monster Roster precursors), Feminist art movement (23; src is the "Feminist art" article), American Abstract Artists (16). Each has sectioned groups, an axis and catalogue links. Other passes may create Gutai / Feminist art too: merge by label.

## Residual A5-110 (my rows)
Grouped by named school/group/colony where attested (Stieglitz circle, Woodstock, Taos and Santa Fe, Spiral, Chicago Black Renaissance, Beaver Hall Group, Painters Eleven, Automatistes, Escuela Mexicana, Oaxacan School, Cuban Vanguardia, Generación del 13, Grupo Montparnasse, Planismo, Grupo de París, Grupo Rex, West Lake School, Three Masters Crossing the Strait, Ton Fan, Fifth Moon, New Ink, Calcutta Group, Baroda School, Madras Art Movement, '43 Group, Persagi, Bandung School, Thirteen Moderns, École des Beaux-Arts de l'Indochine, Nanyang style, D Group, 1914 Generation, Baghdad Modern Art Group/Al-Ruwad, New Horizons, Casablanca School, École de Tunis, École d'Alger, Khartoum School, Zaria Art Society, Oshogbo, Angry Penguins, Antipodeans, The Group (Christchurch), Māori modernism...), otherwise by country. The United States is split into birth cohorts so no group is over 150 rows. Countries with only 1–2 rows are merged with neighbours (e.g. "Benin, Cameroon and Togo").

## Doubts and notes for the coordinator
- One input row has an empty name (b. 1927, United States). It cannot be identified, so to satisfy the maker count it sits in `moves_out` to A5-111 and is also listed in `dropped`. Please delete it.
- Same person twice in the input: "M'hamed Issiakhem" / "Mohammed Issiakhem (1928-1985)" and "Kamala Ibrahim Ishag" / "Kamala Ibrahim Ishaq". Both copies are kept so no maker is lost; merge them.
- Western Europeans mis-routed to this pass: Margaret Mellis, Joseph Uhl ("Europe" group); Bernard Leach moved to Mingei.
- Moves to other catch-alls (B1-5 Illustration, B2-15 Modern Printmaking, K6-22 Modern Architecture) are by medium, not by movement.
- Less certain group placements: Ram Kumar and Mohan Samant as Progressive "associates"; Kadhim Hayder and Mahmoud Sabri under Al-Ruwad; Russell Clark with The Group; Kamala Ishaq under Khartoum School (she was a Crystalist).
- No Collections group was added (all leaves here are artist-led). Catalogue links are museum and archive sites (ICAA, Asia Art Archive, Mathaf, Getty ULAN, plus searches at the Met, AIC, Tate and MoMA).
