# VA completeness audit

Reference: the gathered museum records as mapped by the collections cross-reference (object counts are per source label × medium key), the coverage probes, and the published tree. No new searching. Flags in `flags.csv`.

## V1 Mass balance: where gathered objects resolve

| Family | Leaf | General only | Named, no leaf | Excluded | Leaf share of in-scope |
|---|---:|---:|---:|---:|---:|
| A Painting | 25,217 | 70,765 | 5,953 | 3,289 | 25% |
| B Drawings & Prints | 22,433 | 27,100 | 123 | 2,214 | 45% |
| C Book Arts & Calligraphy | 83,910 | 59,484 | 3,997 | 2,694 | 57% |
| D Sculpture & Carving | 42,250 | 29,322 | 4,746 | 22,085 | 55% |
| E Ceramics | 164,316 | 271,096 | 28,763 | 8,754 | 35% |
| F Glass | 22,560 | 18,585 | 4,403 | 4,895 | 50% |
| G Metalwork, Arms & Jewellery | 28,108 | 174,029 | 30,577 | 10,414 | 12% |
| H Textiles, Carpets & Dress | 40,870 | 85,654 | 6,906 | 5,235 | 31% |
| I Woodwork, Lacquer & Furniture | 7,493 | 71,771 | 2,977 | 7,355 | 9% |
| J Photography | 83 | 9,626 | 0 | 3,858 | 1% |
| L Art in Place | 114 | 0 | 0 | 0 | 100% |
| ? unknown type | 0 | 52,043 | 7,371 | 185,069 | 0% |
| **All** | 437,354 | 869,475 | 95,816 | 255,862 | **31%** |

Of the general-only objects, 18,256 sit under labels reviewed and kept general (`v2_review.csv`: the named leaf does not hold the whole label), 794 under unreviewed labels whose qualifier names a leaf, and 74,828 under qualified labels no leaf carries. V3 counts general objects resolved by their own titles (`v3_cells.csv`, `pipelines/r3/collections_resolve.py`).

## Flags by check

| Check | High | Medium | Low |
|---|---:|---:|---:|
| V2 | 0 | 13 | 61 |
| V3 | 18 | 40 | 39 |
| V4 | 0 | 2 | 242 |
| V5 | 0 | 0 | 1 |
| V6 | 0 | 47 | 415 |
| V7 | 0 | 26 | 34 |

V4: 384 named missing traditions in the mapping, 140 now carried by a leaf name, 244 open. V6: 84 rows in leftover per-object works lists.

### Qualified labels resolved only to general (top 15)

| Severity | Where | What | Evidence | Objects |
|---|---|---|---|---:|
| medium | China · Qing [A] | label names a period/school/ware but resolves only to general; no leaf carries it | qualifier 'qing'; top: National Palace Museum, Taipei (6061); Tokyo National Museum (358); Kyoto National Museum  | 7,287 |
| medium | Japan · Kofun [G] | label names a period/school/ware but resolves only to general; no leaf carries it | qualifier 'kofun'; top: Tokyo National Museum (6150); Kyoto National Museum (322); Kyushu National Museum (139); N | 6,896 |
| medium | Japan · Edo [A] | label names a period/school/ware but resolves only to general; no leaf carries it | qualifier 'edo'; top: Tokyo National Museum (4262); Kyoto National Museum (535); Cleveland Museum of Art (362);  | 5,891 |
| medium | Japan · Edo [H] | label names a period/school/ware but resolves only to general; no leaf carries it | qualifier 'edo'; top: Tokyo National Museum (2779); Kyoto National Museum (868); Art Institute of Chicago (415); | 4,558 |
| medium | Western European manuscripts, late medieval/Renaissance (unlocalised, 1451-1600) [C] | label names a period/school/ware but resolves only to general; no leaf carries it | qualifier 'medieval renaissance'; top: Bibliothèque nationale de France (2159); Harvard University (524); University of Pennsylva | 3,490 |
| medium | China · Ming [A] | label names a period/school/ware but resolves only to general; no leaf carries it | qualifier 'ming'; top: National Palace Museum, Taipei (2858); Tokyo National Museum (209); Cleveland Museum of Ar | 3,417 |
| medium | Korea · Joseon [A] | label names a period/school/ware but resolves only to general; no leaf carries it | qualifier 'joseon'; top: 국립중앙박물관 (2895); Tokyo National Museum (90); Cleveland Museum of Art (54); 제주추사관 (25) | 3,142 |
| medium | Japan · Edo [B] | label names a period/school/ware but resolves only to general; no leaf carries it | qualifier 'edo'; top: Tokyo National Museum (2677); Kyushu National Museum (165); Kyoto National Museum (52); 独立 | 3,103 |
| medium | China · Qing [E] | label names a period/school/ware but resolves only to general; no leaf carries it | qualifier 'qing'; top: Art Institute of Chicago (1765); Tokyo National Museum (741); Cleveland Museum of Art (292 | 2,940 |
| medium | Japan · Edo [G] | label names a period/school/ware but resolves only to general; no leaf carries it | qualifier 'edo'; top: Tokyo National Museum (1416); Cleveland Museum of Art (571); Kyoto National Museum (374);  | 2,534 |
| medium | Philippine weaving (pina, Yakan, Kalinga, Ifugao) [H] | label names a leaf: remap if that leaf holds the whole key | qualifier 'pina yakan kalinga ifugao' matches H3-14 | 344 |
| medium | Wixarika (Huichol) [H] | label names a leaf: remap if that leaf holds the whole key | qualifier 'huichol' matches H9-15 | 247 |
| medium | Guna (Kuna) [H] | label names a leaf: remap if that leaf holds the whole key | qualifier 'kuna' matches H4-33 | 203 |
| low | Japan · Meiji [A] | label names a period/school/ware but resolves only to general; no leaf carries it | qualifier 'meiji'; top: Tokyo National Museum (1216); Kyoto National Museum (267); Cleveland Museum of Art (64); A | 1,584 |
| low | Japan · Edo [I] | label names a period/school/ware but resolves only to general; no leaf carries it | qualifier 'edo'; top: Tokyo National Museum (1117); Kyoto National Museum (200); Kyushu National Museum (86); Cl | 1,501 |

### Culture × medium gaps (top 15)

| Severity | Where | What | Evidence | Objects |
|---|---|---|---|---:|
| high | indonesia × H | coverage not verifiable from the records: the label names only a culture and the titles name no tradition (see residual title words in v3_cells.csv); a coarse label, not a missing leaf, unless those words name one | leaf 2% of 48,547 in scope (incl. 793 resolved by title); general 48,547, missing 0; leaves in other families: AG | 48,547 |
| high | china × E | coverage not verifiable from the records: the label names only a culture and the titles name no tradition (see residual title words in v3_cells.csv); a coarse label, not a missing leaf, unless those words name one | leaf 7% of 29,752 in scope (incl. 131 resolved by title); general 27,760, missing 0; leaves in other families: ABCDIJ | 29,752 |
| high | japan × A | coverage not verifiable from the records: the label names only a culture and the titles name no tradition (see residual title words in v3_cells.csv); a coarse label, not a missing leaf, unless those words name one | leaf 4% of 21,535 in scope (incl. 68 resolved by title); general 20,730, missing 34; leaves in other families: BCDEGHIJ | 21,535 |
| high | indonesia × I | coverage not verifiable from the records: the label names only a culture and the titles name no tradition (see residual title words in v3_cells.csv); a coarse label, not a missing leaf, unless those words name one | leaf 0% of 20,937 in scope (incl. 103 resolved by title); general 20,937, missing 0; leaves in other families: AG | 20,937 |
| high | japan × H | coverage not verifiable from the records: the label names only a culture and the titles name no tradition (see residual title words in v3_cells.csv); a coarse label, not a missing leaf, unless those words name one | leaf 6% of 18,567 in scope (incl. 1,119 resolved by title); general 18,561, missing 0; leaves in other families: ABCDEGIJ | 18,567 |
| high | china × A | coverage not verifiable from the records: the label names only a culture and the titles name no tradition (see residual title words in v3_cells.csv); a coarse label, not a missing leaf, unless those words name one | leaf 5% of 17,614 in scope (incl. 8 resolved by title); general 16,702, missing 14; leaves in other families: BCDEIJ | 17,614 |
| high | indonesia × A | coverage not verifiable from the records: the label names only a culture and the titles name no tradition (see residual title words in v3_cells.csv); a coarse label, not a missing leaf, unless those words name one | leaf 6% of 10,589 in scope (incl. 571 resolved by title); general 10,491, missing 0; leaves in other families: G | 10,589 |
| high | france × H | coverage not verifiable from the records: the label names only a culture and the titles name no tradition (see residual title words in v3_cells.csv); a coarse label, not a missing leaf, unless those words name one | leaf 2% of 9,886 in scope (incl. 0 resolved by title); general 9,663, missing 6; leaves in other families: E | 9,886 |
| high | egypt × G | coverage not verifiable from the records: the label names only a culture and the titles name no tradition (see residual title words in v3_cells.csv); a coarse label, not a missing leaf, unless those words name one | leaf 0% of 9,445 in scope (incl. 0 resolved by title); general 365, missing 9,080; leaves in other families: CEFHI | 9,445 |
| high | italy × H | coverage not verifiable from the records: the label names only a culture and the titles name no tradition (see residual title words in v3_cells.csv); a coarse label, not a missing leaf, unless those words name one | leaf 2% of 9,418 in scope (incl. 0 resolved by title); general 9,193, missing 0; leaves in other families: DEFG | 9,418 |
| high | china × G | coverage not verifiable from the records: the label names only a culture and the titles name no tradition (see residual title words in v3_cells.csv); a coarse label, not a missing leaf, unless those words name one | leaf 1% of 9,021 in scope (incl. 84 resolved by title); general 8,478, missing 543; leaves in other families: ABCDEIJ | 9,021 |
| high | india × H | coverage not verifiable from the records: the label names only a culture and the titles name no tradition (see residual title words in v3_cells.csv); a coarse label, not a missing leaf, unless those words name one | leaf 2% of 8,359 in scope (incl. 47 resolved by title); general 8,250, missing 0; leaves in other families: ADG | 8,359 |
| high | india × G | coverage not verifiable from the records: the label names only a culture and the titles name no tradition (see residual title words in v3_cells.csv); a coarse label, not a missing leaf, unless those words name one | leaf 1% of 5,944 in scope (incl. 9 resolved by title); general 5,878, missing 0; leaves in other families: ADH | 5,944 |
| high | indonesia × D | coverage not verifiable from the records: the label names only a culture and the titles name no tradition (see residual title words in v3_cells.csv); a coarse label, not a missing leaf, unless those words name one | leaf 5% of 5,909 in scope (incl. 304 resolved by title); general 5,575, missing 334; leaves in other families: AG | 5,909 |
| high | iran × E | coverage not verifiable from the records: the label names only a culture and the titles name no tradition (see residual title words in v3_cells.csv); a coarse label, not a missing leaf, unless those words name one | leaf 4% of 5,610 in scope (incl. 6 resolved by title); general 5,395, missing 0; leaves in other families: ACGHI | 5,610 |

### Open named traditions (top 15)

| Severity | Where | What | Evidence | Objects |
|---|---|---|---|---:|
| medium | Bactria-Margiana Metalwork | named tradition with gathered objects and no leaf | families G; max institutions per key 1; labels: Bactria-Margiana Archaeological Complex; Bactria-Margiana Archaeological Complex / Bronze Age | 386 |
| medium | Laconian Lead Figurines | named tradition with gathered objects and no leaf | families ?; max institutions per key 1; labels: Greek, Laconian; Greek, Laconian / Archaic | 277 |
| low | Italic Bronzes | named tradition with gathered objects and no leaf | families G; max institutions per key 1; labels: Italic; Italic / Archaic; Italic / Classical; Italic / Geometric; Italic / Hellenistic | 197 |
| low | Mezcala Stone Sculpture | named tradition with gathered objects and no leaf | families D; max institutions per key 1; labels: Mezcala | 153 |
| low | Tibetan Arms and Armour | named tradition with gathered objects and no leaf | families ?; max institutions per key 2; labels: Tibetan | 107 |
| low | Fon Metal Sculpture | named tradition with gathered objects and no leaf | families G; max institutions per key 1; labels: Fon | 101 |
| low | Irish Cut Glass | named tradition with gathered objects and no leaf | families F; max institutions per key 2; labels: Irish | 89 |
| low | Seville Pottery | named tradition with gathered objects and no leaf | families E; max institutions per key 2; labels: Spanish, Seville | 86 |
| low | Batak Sculpture | named tradition with gathered objects and no leaf | families DI; max institutions per key 1; labels: Toba Batak | 80 |
| low | Dayak Sculpture | named tradition with gathered objects and no leaf | families D; max institutions per key 1; labels: Indonesian, Kalimantan; Kayan; Kenyah; Ngadju; Ot Danum | 80 |
| low | Gupta Sculpture | named tradition with gathered objects and no leaf | families D; max institutions per key 1; labels: Gupta period; Indian / Gupta period | 67 |
| low | Shipibo-Conibo Textiles | named tradition with gathered objects and no leaf | families EH; max institutions per key 1; labels: Conibo; Shipibo; Shipibo-Conibo | 64 |
| low | Thessalian Neolithic Pottery | named tradition with gathered objects and no leaf | families E; max institutions per key 1; labels: Neolithic, Thessaly; Neolithic, Thessaly / Neolithic | 64 |
| low | Shunga Art | named tradition with gathered objects and no leaf | families ?D; max institutions per key 1; labels: Indian / Shunga period; Shunga period | 62 |
| low | Harappan Pottery | named tradition with gathered objects and no leaf | families E; max institutions per key 1; labels: Early Harappan; Indus; Indus / Early Harappan | 57 |

### Leaf completeness (high and medium, top 15)

| Severity | Where | What | Evidence | Objects |
|---|---|---|---|---:|
| medium | D5-52 Ndop | leaf has no rows: the card shows only the definition and View-all links | n = 0 |  |
| medium | E1-15 Cham Pottery | leaf has no rows: the card shows only the definition and View-all links | n = 0 |  |
| medium | E1-16 Kasongan Pottery | leaf has no rows: the card shows only the definition and View-all links | n = 0 |  |
| medium | E1-59 Awajún Pottery | leaf has no rows: the card shows only the definition and View-all links | n = 0 |  |
| medium | E1-78 Saint-Porchaire Ware | leaf has no rows: the card shows only the definition and View-all links | n = 0 |  |
| medium | E1-91 Bubnivka Ceramics | leaf has no rows: the card shows only the definition and View-all links | n = 0 |  |
| medium | E1-92 Oleshnia Pottery | leaf has no rows: the card shows only the definition and View-all links | n = 0 |  |
| medium | E2-13 Qallaline Tiles | no attesting source |  |  |
| medium | E4-11 Kraak Ware | leaf has no rows: the card shows only the definition and View-all links | n = 0 |  |
| medium | H2-16 Raanu | leaf has no rows: the card shows only the definition and View-all links | n = 0 |  |
| medium | H3-17 Zhuang Brocade | leaf has no rows: the card shows only the definition and View-all links | n = 0 |  |
| medium | H3-19 Shuri Weaving | leaf has no rows: the card shows only the definition and View-all links | n = 0 |  |
| medium | H3-22 Hansan Mosi | leaf has no rows: the card shows only the definition and View-all links | n = 0 |  |
| medium | H3-26 Ivorian Loincloth Weaving | leaf has no rows: the card shows only the definition and View-all links | n = 0 |  |
| medium | H3-32 Täkänä | leaf has no rows: the card shows only the definition and View-all links | n = 0 |  |
