# Structure audit

Computed from the published data: FT 962 leaves (545 sectioned), VA 1774 leaves. Flags in `flags.csv`.

| Check | Finding | High | Medium | Low |
|---|---|---:|---:|---:|
| S1 | declared section with no titles | 0 | 0 | 1 |
| S1 | one-title section | 0 | 0 | 3 |
| S1 | over 40 titles and no sections | 0 | 60 | 0 |
| S1 | sections without a stated axis | 0 | 2 | 0 |
| S1 | titles outside every section of a sectioned leaf | 0 | 72 | 131 |
| S10 | country section with mixed countries | 0 | 0 | 111 |
| S10 | filmmaker section whose titles are mostly by others | 0 | 0 | 4 |
| S2 | era sections out of chronological order | 0 | 9 | 0 |
| S2 | era sections overlap | 0 | 7 | 0 |
| S2 | titles outside their era section's dates | 0 | 9 | 12 |
| S3 | section not in year order | 0 | 0 | 1 |
| S4 | one sub-type name in two leaves | 0 | 0 | 22 |
| S4 | one title in two leaves | 0 | 6 | 0 |
| S5 | section label is also a leaf elsewhere | 0 | 16 | 0 |
| S5 | two leaves with one label in one family | 0 | 19 | 0 |
| S6 | uneven sub-family: one or few leaves hold most entries | 0 | 0 | 16 |
| S7 | defn names a code that does not exist | 0 | 2 | 0 |
| S7 | see gives a code with another leaf's label | 0 | 14 | 0 |
| S7 | see names a code that does not exist | 0 | 5 | 0 |

S2: 147 titles fall outside the dates of their era section.

## S9 Axis kinds per sub-family (sectioned leaves)

| Tab | Sub-family | era | country/region | auteur/school | form/theme |
|---|---|---:|---:|---:|---:|
| FT | A1 Movements & Schools | 1 | 1 | 0 | 1 |
| FT | A2 Crime | 4 | 2 | 0 | 7 |
| FT | A3 Thriller & Mystery | 4 | 1 | 0 | 11 |
| FT | A4 Horror | 7 | 1 | 1 | 17 |
| FT | A5 Science Fiction | 1 | 0 | 0 | 9 |
| FT | A6 Fantasy & Adventure | 1 | 0 | 1 | 7 |
| FT | A7 Action & Martial Arts | 3 | 0 | 0 | 3 |
| FT | A8 Historical & Period Film | 6 | 0 | 0 | 4 |
| FT | A9 War Film | 3 | 0 | 0 | 4 |
| FT | A10 Western | 1 | 1 | 0 | 2 |
| FT | A11 Biographical Film | 1 | 2 | 0 | 7 |
| FT | A12 Comedy | 4 | 2 | 2 | 22 |
| FT | A13 Romance | 4 | 1 | 1 | 17 |
| FT | A14 Musical & Dance Film | 1 | 1 | 0 | 5 |
| FT | A15 Erotic Film | 3 | 1 | 0 | 1 |
| FT | A16 Drama | 15 | 3 | 3 | 18 |
| FT | A17 Children's & Family Film | 0 | 0 | 1 | 8 |
| FT | A18 Popular Cinema Modes | 3 | 0 | 0 | 1 |
| FT | A19 Documentary | 8 | 3 | 3 | 16 |
| FT | A20 Experimental & Avant-Garde | 2 | 1 | 0 | 0 |
| FT | A21 Short Film | 10 | 0 | 2 | 4 |
| FT | B1 Drama Series | 5 | 1 | 2 | 14 |
| FT | B2 Korean Drama | 1 | 1 | 1 | 5 |
| FT | B3 Japanese Television Drama | 1 | 0 | 2 | 6 |
| FT | B4 Chinese-Language Drama | 1 | 1 | 1 | 9 |
| FT | B5 Boys' Love & Girls' Love Drama | 3 | 0 | 3 | 3 |
| FT | B7 Crime & Thriller Series | 3 | 1 | 1 | 21 |
| FT | B8 Comedy Series | 5 | 0 | 1 | 10 |
| FT | B9 Speculative Series | 0 | 0 | 0 | 25 |
| FT | B10 Children's Series | 0 | 0 | 2 | 1 |
| FT | B11 Documentary Series | 0 | 2 | 0 | 6 |
| FT | B12 Serial Drama Traditions | 0 | 0 | 1 | 3 |
| FT | B13 Competition Formats | 0 | 1 | 0 | 2 |
| FT | B14 Factual Entertainment Formats | 0 | 0 | 1 | 8 |
| FT | B15 Variety & Talk Formats | 1 | 0 | 0 | 3 |
| FT | B16 Live Event & Sports Television | 1 | 1 | 0 | 2 |
| FT | C1 Action & Battle Anime | 2 | 0 | 2 | 9 |
| FT | C2 Mecha & Science Fiction Anime | 1 | 0 | 0 | 5 |
| FT | C3 Fantasy & Isekai Anime | 1 | 0 | 0 | 8 |
| FT | C4 Magical Girl Anime | 0 | 0 | 0 | 1 |
| FT | C5 Romance Anime | 1 | 0 | 5 | 4 |
| FT | C6 Slice of Life & Iyashikei Anime | 0 | 1 | 0 | 5 |
| FT | C7 Sports & Game Anime | 0 | 0 | 0 | 4 |
| FT | C8 Drama, Mystery & Psychological Anime | 4 | 0 | 1 | 3 |
| FT | C9 Horror Anime | 0 | 0 | 1 | 0 |
| FT | C10 Comedy Anime | 0 | 1 | 2 | 7 |
| FT | C11 Children's & Family Anime | 1 | 0 | 0 | 2 |
| FT | C12 Animated Feature | 3 | 2 | 2 | 6 |
| FT | C13 Animated Series | 3 | 1 | 1 | 6 |
| FT | C14 Animated Short | 4 | 1 | 2 | 1 |
| VA | A1 Manuscript & Album Painting | 11 | 2 | 2 | 7 |
| VA | A2 East Asian Ink & Colour Painting | 11 | 0 | 2 | 2 |
| VA | A3 Icon Painting | 4 | 0 | 1 | 1 |
| VA | A4 Cloth & Scroll Painting | 8 | 1 | 0 | 9 |
| VA | A5 Easel Painting | 47 | 55 | 4 | 39 |
| VA | A6 Folk & Popular Painting | 22 | 5 | 0 | 4 |
| VA | B1 Drawing | 7 | 1 | 2 | 0 |
| VA | B2 Printmaking | 10 | 3 | 0 | 8 |
| VA | C1 Calligraphy | 9 | 0 | 1 | 3 |
| VA | C2 Illuminated Manuscripts & Illumination | 13 | 7 | 1 | 12 |
| VA | C3 Bookbinding | 3 | 0 | 0 | 1 |
| VA | C4 Paper Arts | 2 | 3 | 0 | 8 |
| VA | D1 Architectural Carving & Stucco | 0 | 0 | 0 | 4 |
| VA | D2 Ivory & Bone Carving | 3 | 0 | 0 | 15 |
| VA | D3 Hardstone, Rock Crystal & Jade Carving | 3 | 0 | 0 | 9 |
| VA | D4 Masks & Puppets | 0 | 1 | 0 | 32 |
| VA | D5 Figurative Sculpture | 28 | 7 | 3 | 99 |
| VA | D6 Ritual Objects & Regalia | 0 | 0 | 0 | 13 |
| VA | E1 Earthenware | 136 | 0 | 0 | 3 |
| VA | E2 Fritware (Stonepaste) | 15 | 0 | 0 | 0 |
| VA | E3 Stoneware | 34 | 0 | 0 | 0 |
| VA | E4 Porcelain | 26 | 0 | 0 | 0 |
| VA | F1 Blown & Moulded Glass | 0 | 0 | 2 | 16 |
| VA | F2 Cut & Carved Glass | 1 | 0 | 0 | 3 |
| VA | F3 Enamelled & Gilded Glass | 0 | 0 | 0 | 1 |
| VA | F4 Lustre-Painted Glass | 0 | 0 | 0 | 1 |
| VA | F5 Stained Glass | 1 | 0 | 0 | 2 |
| VA | G1 Metalwork | 14 | 0 | 0 | 57 |
| VA | G2 Arms & Armour | 3 | 0 | 0 | 10 |
| VA | G3 Jewellery | 5 | 0 | 0 | 26 |
| VA | H1 Pile Carpets & Rugs | 5 | 0 | 0 | 9 |
| VA | H2 Flatweaves | 5 | 0 | 0 | 20 |
| VA | H3 Woven Silks & Figured Textiles | 7 | 0 | 0 | 45 |
| VA | H4 Embroidery & Needlework | 13 | 0 | 1 | 85 |
| VA | H5 Dyed & Printed Textiles | 10 | 0 | 0 | 29 |
| VA | H6 Felt | 0 | 0 | 0 | 1 |
| VA | H7 Dress & Costume | 2 | 2 | 0 | 17 |
| VA | H8 Basketry, Barkcloth & Fibre Arts | 6 | 0 | 0 | 33 |
| VA | H9 Beadwork, Quillwork & Featherwork | 3 | 0 | 0 | 11 |
| VA | H10 Leatherwork | 1 | 0 | 0 | 2 |
| VA | I1 Carved & Inlaid Woodwork | 0 | 0 | 0 | 32 |
| VA | I2 Lacquer | 3 | 1 | 0 | 18 |
| VA | I3 Furniture & Decorative Arts Styles | 4 | 12 | 0 | 8 |
| VA | I4 Musical Instruments | 1 | 0 | 0 | 22 |
| VA | J1 Photographic Schools & Movements | 5 | 9 | 0 | 3 |
| VA | K1 Islamic Architecture | 19 | 0 | 0 | 0 |
| VA | K2 Historicist & National Revivals | 1 | 33 | 0 | 0 |
| VA | K3 Ancient Mediterranean & Near Eastern Architecture | 10 | 0 | 0 | 1 |
| VA | K4 Medieval European Architecture | 13 | 0 | 0 | 0 |
| VA | K5 Early Modern European & Colonial Architecture | 4 | 20 | 0 | 0 |
| VA | K6 Modern & Contemporary Architecture | 3 | 23 | 0 | 0 |
| VA | K7 South Asian Architecture | 2 | 15 | 0 | 2 |
| VA | K8 East Asian Architecture | 18 | 0 | 0 | 3 |
| VA | K9 Southeast Asian Architecture | 11 | 0 | 0 | 3 |
| VA | K10 African Architecture | 0 | 6 | 0 | 1 |
| VA | K11 Indigenous American Architecture | 0 | 7 | 0 | 0 |
| VA | K12 Vernacular & Oceanic Architecture | 0 | 10 | 0 | 10 |
| VA | K13 Gardens & Designed Landscapes | 0 | 7 | 0 | 0 |
| VA | K14 Plant & Floral Arts | 0 | 0 | 0 | 4 |
| VA | L1 Rock Art | 38 | 3 | 0 | 1 |
| VA | L2 Wall Painting | 37 | 1 | 0 | 13 |
| VA | L3 Mosaic & Tile Revetment | 0 | 11 | 0 | 1 |
| VA | L4 Geoglyphs | 0 | 7 | 0 | 1 |
| VA | L5 Body Art | 0 | 0 | 0 | 12 |
| VA | L6 Floor & Sand Painting | 0 | 0 | 0 | 3 |
| VA | M1 Installation, Conceptual & Performance Art | 1 | 5 | 0 | 3 |
| VA | M2 Video & New Media Art | 1 | 2 | 0 | 2 |
| VA | N1 Furniture & Lighting Design | 12 | 0 | 0 | 0 |
| VA | N2 Product & Industrial Design | 9 | 0 | 0 | 0 |
| VA | N3 Graphic Design | 13 | 0 | 0 | 0 |

## S6 Most uneven sub-families

| Tab | Sub-family | Leaves | Entries | Gini | Largest leaf |
|---|---|---:|---:|---:|---:|
| VA | A5 Easel Painting | 145 | 19,245 | 0.83 | 31% |
| VA | D5 Figurative Sculpture | 138 | 4,267 | 0.81 | 38% |
| VA | H7 Dress & Costume | 23 | 291 | 0.70 | 60% |
| VA | K8 East Asian Architecture | 21 | 528 | 0.68 | 29% |
| VA | K5 Early Modern European & Colonial Architecture | 24 | 1,285 | 0.68 | 33% |
| VA | I3 Furniture & Decorative Arts Styles | 24 | 958 | 0.67 | 22% |
| VA | B1 Drawing | 10 | 1,395 | 0.67 | 56% |
| VA | J1 Photographic Schools & Movements | 17 | 3,104 | 0.66 | 29% |
| VA | L2 Wall Painting | 51 | 779 | 0.66 | 22% |
| VA | K4 Medieval European Architecture | 13 | 684 | 0.65 | 46% |
| VA | B2 Printmaking | 21 | 920 | 0.65 | 27% |
| VA | L1 Rock Art | 42 | 584 | 0.62 | 19% |
| VA | K9 Southeast Asian Architecture | 14 | 197 | 0.60 | 36% |
| VA | H8 Basketry, Barkcloth & Fibre Arts | 49 | 192 | 0.58 | 14% |
| VA | M1 Installation, Conceptual & Performance Art | 9 | 524 | 0.58 | 51% |

## Era sections: examples

| Tab | Where | What | Evidence |
|---|---|---|---|
| FT | A12-4 Screwball Comedy | era sections out of chronological order | 1933–1945 before 1930–1939 |
| FT | A15-5 Pink Film | era sections overlap | 1962–1971 and 1971–1988 |
| FT | A15-5 Pink Film | era sections overlap | 1971–1988 and 1985–2000 |
| FT | A15-5 Pink Film | titles outside their era section's dates | Pink Shitennō (Four Heavenly Kings, 1985–2000): Kandagawa Wars (1983); Abnormal Family (1984); Tokyo X Erotica (2001) |
| FT | A16-19 Social Realism | era sections out of chronological order | 1980–9999 before -9999–1989 |
| FT | A16-41 Heimatfilm | era sections overlap | 1947–1969 and 1968–1979 |
| FT | A3-4 Krimi | era sections overlap | 1959–1972 and 1960–1964 |
| FT | A5-6 Kaiju | era sections overlap | 1984–1999 and 1999–2004 |
| FT | A6-2 Sword and Sorcery | titles outside their era section's dates | Later Sword and Sorcery (1990s–): The Hexer (2001); The Scorpion King (2002); Solomon Kane (2009); Conan the Barbarian (2011) (+4) |
| FT | A8-2 Sword-and-Sandal Film | era sections overlap | 1932–1966 and 1954–1965 |
| FT | B8-1 Family Sitcom | era sections out of chronological order | 2010–2019 before -9999–1999 |
| FT | B8-1 Family Sitcom | titles outside their era section's dates | US streaming era (2010s–): The Big Show Show (2020–2020); Country Comfort (2021–2021); Dad Stop Embarrassing Me! (2021–2021); The Upshaws (2021–2026) (+5) |
| FT | B8-1 Family Sitcom | titles outside their era section's dates | Other national family sitcoms (2000s–): High Kick Season 3 (2011); Seksenler (2012–2022); Bhabiji Ghar Par Hain (2015–2026); Wagle Ki Duniya (2021–) |
| FT | B8-3 Workplace Comedy | era sections out of chronological order | 2010–2019 before 1960–1979 |
| FT | B8-3 Workplace Comedy | era sections out of chronological order | 2010–9999 before -9999–1999 |

## One title in two leaves (FT)

| Tab | Where | What | Evidence |
|---|---|---|---|
| FT | Carlos (2010–2010) | one title in two leaves | A11-13, B7-21 |
| FT | Cartesius (1974–) | one title in two leaves | A11-6, B1-27 |
| FT | Festival (2010) | one title in two leaves | A12-40, A19-32 |
| FT | When the Levees Broke: A Requiem in Four Acts (2006–2007) | one title in two leaves | A19-10, B11-3 |
| FT | World on a Wire (1973–1973) | one title in two leaves | A1-15, B9-6 |
| FT | —- ———- (1967) | one title in two leaves | A20-2, A21-19 |

## Rank conflicts

| Tab | Where | What | Evidence |
|---|---|---|---|
| FT | A2-22 Social Problem Film | section label is also a leaf elsewhere | section 'Juvenile Delinquency Film' = leaf A16-15 |
| FT | A2-25 Neo-Noir | section label is also a leaf elsewhere | section 'Country Noir' = leaf B7-5 |
| FT | A21-15 Avant-Garde Short | section label is also a leaf elsewhere | section 'Surrealist Film' = leaf A20-1 |
| FT | A3-10 Revenge Thriller | section label is also a leaf elsewhere | section 'Vigilante Film' = leaf A7-3 |
| FT | B4-21 TVB Drama | section label is also a leaf elsewhere | section 'Costume Drama' = leaf A8-9, B1-20 |
| FT | B8-15 Political Satire | section label is also a leaf elsewhere | section 'Social Satire' = leaf A12-15 |
| FT | B9-11 Comic Science Fiction & Comic Fantasy | section label is also a leaf elsewhere | section 'Comic Fantasy' = leaf C3-7 |
| FT | B9-6 Artificial Intelligence in Fiction | section label is also a leaf elsewhere | section 'Cyberpunk' = leaf A5-11 |
| FT | C1-13 Superhero Anime | section label is also a leaf elsewhere | section 'Superhero Parody & Deconstruction' = leaf A6-17 |
| FT | C1-15 Gun Action Anime | section label is also a leaf elsewhere | section 'Girls with Guns' = leaf A7-7 |
| FT | C12-19 Adult Animation | section label is also a leaf elsewhere | section 'Adult Animated Comedy' = leaf C13-2 |
| FT | C13-2 Adult Animated Comedy | section label is also a leaf elsewhere | section 'Surreal & Absurdist Comedy' = leaf A12-19, B8-12 |
| FT | C13-3 Adult Animated Action & Drama | section label is also a leaf elsewhere | section 'Anthology Series' = leaf B9-10 |
| FT | C3-1 Isekai (Transported to Another World) | section label is also a leaf elsewhere | section 'Portal Fantasy' = leaf A6-4 |
| FT | C5-4 Romantic Comedy | section label is also a leaf elsewhere | section 'Workplace Romantic Comedy' = leaf A13-19 |

## Broken references

| Tab | Where | What | Evidence |
|---|---|---|---|
| FT | A13-12 Romantic Comedy of Manners | defn names a code that does not exist | A13-10 |
| FT | B15-1 Variety Show | see names a code that does not exist | B15-6 Television Special |
| VA | C2-6 Lontar | see gives a code with another leaf's label | D4-7 'Palm-Leaf Manuscripts' but D4-7 is 'Sbek Thom' |
| VA | D3-10 Pietra Dura | see gives a code with another leaf's label | E4-25 'Mosaic & Tile Revetment' but E4-25 is 'Soft-Paste Porcelain' |
| VA | D5-137 Ancient Cypriot Sculpture | see gives a code with another leaf's label | E1 'Ancient Cypriot Pottery' but E1 is 'Earthenware' |
| VA | D5-71 Santos | see gives a code with another leaf's label | D5-68 'Philippine Santos' but D5-68 is 'Valdivia Figurines' |
| VA | E1-65 Casas Grandes Pottery | see gives a code with another leaf's label | H8-20 'Mata Ortiz Pottery' but H8-20 is 'Hopi Basketry' |
| VA | E1-81 Talavera de la Reina Pottery | see names a code that does not exist | L44 Talavera Poblana |
| VA | F5-3 Tiffany Glass | see gives a code with another leaf's label | I3-11 'Art Nouveau' but I3-11 is 'Empire Style' |
| VA | H2-13 Chimayó Weaving | see names a code that does not exist | L72 Saltillo Serape |
| VA | H4-44 Bucks Point Lace | see gives a code with another leaf's label | D2-11 'Brussels Lace' but D2-11 is 'Gothic Ivories' |
| VA | H4-44 Bucks Point Lace | see gives a code with another leaf's label | D2-12 'Mechlin Lace' but D2-12 is 'Scrimshaw' |
| VA | H4-44 Bucks Point Lace | see gives a code with another leaf's label | D5-92 'Honiton Lace' but D5-92 is 'Wildfowl Decoys' |
| VA | H4-46 Amish Quilts | see gives a code with another leaf's label | G3-20 'Star Quilts' but G3-20 is 'Fabergé' |
| VA | H5-12 Indonesian Ikat | see gives a code with another leaf's label | H5-10 'Patola' but H5-10 is 'Indonesian Batik' |
