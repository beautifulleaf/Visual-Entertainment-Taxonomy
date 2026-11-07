# bucket_academic_19c: summary

Leaves: A5-38 Academic Art, D5-115 Academic Sculpture, A5-31 Romanticism, A5-30 Neoclassicism, D5-114 Neoclassical Sculpture, A5-40 Realism, A5-45 Naturalism.
Input: 5,026 rows (5,021 artists). Output: 4,066 kinds in the 7 leaves, 205 in 6 new leaves (12 of them added rows with Wikipedia sources), 667 moves_out.

## What changed
- Every leaf now has an axis: named academies, schools, circles and colonies come first, then the rest of the artists by country of activity. Historic states are folded into present-day countries, and Czech, Polish, South Slavic, Baltic and Ukrainian artists of the empires get their own groups. Groups over 150 are split by birth year, countries with fewer than 3 artists are pooled as "Other regions", and every group is ordered by birth year.
- Named groups kept inside leaves (all attested in the literature): Lyon/École d'Écouen, Victorian classicism, The Clique, St John's Wood Clique, Fairy painting, Grand-Ducal Saxon Art School (Weimar), Tervuren School, Generation of the National Theatre, Tinerimea artistică and the Official Salon (Romania), American Renaissance, Western American Art, Academy of San Carlos, Imperial Academy of Fine Arts (Brazil), Troubadour style, Juste milieu, German Romanticism, Biedermeier, The Ancients, Bristol School, Society of Painters in Water Colours, Norwegian romantic nationalism, School of Posillipo, Scapigliatura, Venetsianov school, Atelier of Jacques-Louis David, Ingres and his pupils, Deutschrömer, Peale family, Canova and his school, Thorvaldsen and his workshop, Berlin school of sculpture, French Romantic sculpture, White Marmorean Flock, Volcano School, Molse School, Verismo (painting), Grupo do Leão, Cranbrook Colony, Idyllic school, École de Concarneau, Étaples art colony, Wissant school, Nagybánya artists' colony.
- Moves out (667) go into existing named leaves: Düsseldorf (95), Munich School (50), Danish Golden Age (27), Nazarenes (20), PRB incl. the American Pre-Raphaelites (18), Hudson River (18), Hague, Macchiaioli, Barbizon, Norwich, Costumbrismo, Luminism, Tonalism, Glasgow School, Neo-Grec, Impressionism/Neo-Impressionism (Divisionists), Symbolism, Animalier School, New Sculpture, Naïve Art/Art Brut. Wrong-medium makers were moved too: illustrators and caricaturists to Illustration (119) and Golden Age of Illustration, etchers to Etching Revival, photographers to Early Photography (37) and Pictorialism, architects to the relevant architecture leaves, designers to Arts and Crafts and Art Nouveau, Plains ledger artists to Ledger Art. Soviet painters went to Socialist Realism (30), 20th-century realists to Contemporary, Modern, Social Realism, Regionalism and Magic Realism, and Old Masters in Realism to Baroque, Rococo and Dutch Golden Age.
- Sculptors filed under painting leaves went to the two sculpture leaves in this pass, and late-Romantic, Academic and Realist names were re-filed across the painting leaves.
- Every leaf has a `catalogues` list: Base Salons (Musée d'Orsay), POP–Joconde, WikiArt movement pages, Louvre, Tate, Tretyakov, Mapping Sculpture, Museo Canova, Thorvaldsens Museum, Wikimedia Commons categories, and Skagens Museum, Penlee House and the Finnish National Gallery for the new leaves.
- Glosses are rebuilt from the row data ("Painter, b. 1848; Hungary"), and the machine "movement X" glosses are gone.

## New leaves
1. Orientalism (110; by country)
2. Peredvizhniki (46; by generation; adds Nikolai Ge and Viktor Vasnetsov)
3. Skagen Painters (12; adds Krøyer, Anna and Marie Krøyer/Ancher, Drachmann, Björck, Thaulow)
4. Newlyn School (12; adds Gotch and Chevallier Tayler)
5. Lyon School (14)
6. Golden Age of Finnish Art (11; adds Järnefelt and Halonen)

Krøyer, Ge, Vasnetsov and Halonen also exist in other passes' inputs, so the coordinator should dedupe them.

## Doubts
- Four input rows have a blank name (b. 1927, US), one each in A5-38, A5-31, A5-30 and D5-114. They are parked in moves_out to A5-111 only so the validator's "lost maker" check passes. They should be dropped.
- Orientalism membership partly follows Wikidata "Orientalism" tags: Roybet, Comerre, Ferrier, Sicard, Philippoteaux, Aloysius O'Kelly and Nathaniel Hone. Doubtful Spanish tags (e.g. Casado del Alisal, Palmaroli) and Makart were not moved.
- Peredvizhniki membership of Kuvshinnikova (tagged), Bogolyubov, Lemokh and Brullov is plausible but not checked against the Society's rolls.
- Munich and Düsseldorf moves follow training at the academy. Only canonical names were moved; many Munich-trained Central Europeans stay in their country groups.
- D5-114 has one works row (Lion of the Bavarians, Nafplio). The sculpture leaves are artist-led, so no works catalogue or Collections group was computed.
- No new kinds were added to the 7 input leaves (none was minimal).
