# bucket_contemporary: summary

Leaves: A5-111 Contemporary Art, D5-119 Contemporary Sculpture, M1-1 Installation Art, M1-2 Conceptual Art, M2-5 New Media Art, L2-51 Street Art.
Rebuild: `python3 enrich.py && python3 build.py` (assignments in mapping.py, axes/defns/catalogues in texts.json).

## Moves
- 234 makers moved out to 51 existing leaves. The main targets: Neo-Expressionism A5-98 (23: Mülheimer Freiheit, Moritzplatz, Austrian Neue Wilde, Transavanguardia, Gruppa, Figuration Libre/Combas, Fischl, Rothenberg), Contemporary Photography J1-13 (29), Illustration B1-5 (29: illustrators, cartoonists, comics artists with no comics leaf), Performance Art M1-8 (21), Video Art M2-4 (14), Contemporary Indigenous Australian Art A5-13 (11), Contemporary Design I3-20 (11), Land Art M1-6 (9), American Comics B1-3 (8), Manga B1-9 (5), architects to K6-19/25/26, plus Superflat, Stuckism, Mission School, Lowbrow, Pattern and Decoration, Photorealism, Hurufiyya, British Black Arts, Gond, Haitian, Inuit print/sculpture, Polish posters, Düsseldorf School (the Bechers), Arte Povera (Penone), Kinetic (Theo Jansen), Internet/Generative/AI art.
- 19 misfiled pre-modern or modern artists sent to their period leaves (e.g. Mahmud Muzahhib and Habiballah Savaji to Persian Miniature, Master of Palanquinos to Hispano-Flemish, Ben Enwonwu and Mahmoud Saïd to Modern Art).
- Moves between leaves in this pass: Art & Language, Moscow Conceptualists, Photoconceptualism, General Idea, NSK, New Art Practice, Gorgona now sit in M1-2. Light and Space, Mono-ha and Gutai sit in M1-1. E.A.T., teamLab, Studio Azzurro and Cory Arcangel sit in M2-5. Graffiti writers sit in L2-51.

## New leaves (5)
NEW YBA Young British Artists (33, A5) · NBS New British Sculpture (12, D5) · PIC Pictures Generation (10, A5) · REL Relational art (8, M1) · FBC Franco-Belgian comics (22, B1).

## Residue organisation
- Named groups come first: Neo-Geo, New Leipzig School, New Glasgow Boys, Nuova Scuola Romana, Nueva Figuración Madrileña/La Movida, Neomexicanismo, Stars, '85 New Wave, Scar Art, Cynical Realism, Beijing East Village, New Literati, Congolese popular painting, Ukrainian New Wave, New Academy (St Petersburg), Sámi, Lahore neo-miniature, Māori, First Nations, Native American, Chicano, Feminist art, Amazonian Indigenous artists.
- After the named groups, artists are grouped by country of activity. A country with more than 150 artists is split by birth generation (US, UK). Countries with fewer than 3 artists are pooled by region.
- Artists with no recorded country (about 580, mostly from biennial lists) are grouped by the biennial or list edition that recorded them, taken from data/interim/contemporary_list_artists.csv. Their glosses come from that file too.
- Added Sub-types rows: named tendencies (A5-111), street-art techniques (L2-51), installation and new-media sub-types. Every leaf has 3–5 catalogues links.
- Dropped: 2 Smithsonian culture-label rows (Cree, Potawatomi) and 3 generic mural route rows in L2-51.

## Doubts / for the coordinator
- 6 input rows have an empty name (US, b. 1927, one per leaf). They are junk. They are routed as moves_out to A5-110 only so that the validator passes; please delete them.
- 11 non-artist list entries (e.g. "date=20 October 2022}}", "No award", "E-FLUX JOURNAL") are kept in an "Unverified list entries" group. They can be deleted.
- Mikhail Shibanov → Neoclassicism, Charles Martin Powell → Romanticism and Wang Bing (Qing, left under China) are period guesses.
- Comics artists without a national comics leaf (Italian, British, Polish, Argentine) went to Illustration B1-5.
- Most famous movement members are not in this bucket, so YBA, Pictures Generation and the others hold only the members found here. Other passes may hold the rest.
