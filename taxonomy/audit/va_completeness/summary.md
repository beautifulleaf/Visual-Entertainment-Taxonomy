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

Of the general-only objects, 19,050 sit under labels whose qualifier already names a leaf (mapping misses, fixable without new leaves) and 74,828 under qualified labels no leaf carries.

## Flags by check

| Check | High | Medium | Low |
|---|---:|---:|---:|
| V2 | 1 | 20 | 61 |
| V3 | 19 | 40 | 39 |
| V4 | 5 | 28 | 263 |
| V5 | 0 | 0 | 1 |
| V6 | 0 | 47 | 429 |
| V7 | 0 | 26 | 34 |

V4: 384 named missing traditions in the mapping, 88 now carried by a leaf name, 296 open. V6: 84 rows in leftover per-object works lists.

### Qualified labels resolved only to general (top 15)

| Severity | Where | What | Evidence | Objects |
|---|---|---|---|---:|
| high | Greek, Attic [E] | mapping miss: label names a tradition that has a leaf | qualifier 'attic' matches E1-27, E1-28 | 15,461 |
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
| medium | China · Song [A] | mapping miss: label names a tradition that has a leaf | qualifier 'song' matches A2-2 | 895 |
| medium | China · Tang [E] | mapping miss: label names a tradition that has a leaf | qualifier 'tang' matches E1-20 | 503 |
| medium | Korea · Joseon [E] | mapping miss: label names a tradition that has a leaf | qualifier 'joseon' matches E4-15 | 403 |
| medium | Philippine weaving (pina, Yakan, Kalinga, Ifugao) [H] | mapping miss: label names a tradition that has a leaf | qualifier 'pina yakan kalinga ifugao' matches H3-14 | 344 |

### Culture × medium gaps (top 15)

| Severity | Where | What | Evidence | Objects |
|---|---|---|---|---:|
| high | indonesia × H | unverified coverage: many objects in this medium, (almost) none resolvable to a leaf from their source label (either a missing leaf or a label coarser than the leaves; decide from object titles and dates) | leaf 0% of 48,547 in scope; general 48,547, missing 0; leaves in other families: AG | 48,547 |
| high | indonesia × G | unverified coverage: many objects in this medium, (almost) none resolvable to a leaf from their source label (either a missing leaf or a label coarser than the leaves; decide from object titles and dates) | leaf 6% of 46,618 in scope; general 43,633, missing 0; leaves in other families: A | 46,618 |
| high | china × E | unverified coverage: many objects in this medium, (almost) none resolvable to a leaf from their source label (either a missing leaf or a label coarser than the leaves; decide from object titles and dates) | leaf 7% of 29,752 in scope; general 27,760, missing 0; leaves in other families: ABCDIJ | 29,752 |
| high | japan × A | unverified coverage: many objects in this medium, (almost) none resolvable to a leaf from their source label (either a missing leaf or a label coarser than the leaves; decide from object titles and dates) | leaf 4% of 21,535 in scope; general 20,730, missing 34; leaves in other families: BCDEGHIJ | 21,535 |
| high | indonesia × I | unverified coverage: many objects in this medium, (almost) none resolvable to a leaf from their source label (either a missing leaf or a label coarser than the leaves; decide from object titles and dates) | leaf 0% of 20,937 in scope; general 20,937, missing 0; leaves in other families: AG | 20,937 |
| high | japan × H | unverified coverage: many objects in this medium, (almost) none resolvable to a leaf from their source label (either a missing leaf or a label coarser than the leaves; decide from object titles and dates) | leaf 0% of 18,567 in scope; general 18,561, missing 0; leaves in other families: ABCDEGIJ | 18,567 |
| high | china × A | unverified coverage: many objects in this medium, (almost) none resolvable to a leaf from their source label (either a missing leaf or a label coarser than the leaves; decide from object titles and dates) | leaf 5% of 17,614 in scope; general 16,702, missing 14; leaves in other families: BCDEIJ | 17,614 |
| high | indonesia × A | unverified coverage: many objects in this medium, (almost) none resolvable to a leaf from their source label (either a missing leaf or a label coarser than the leaves; decide from object titles and dates) | leaf 1% of 10,589 in scope; general 10,491, missing 0; leaves in other families: G | 10,589 |
| high | france × H | unverified coverage: many objects in this medium, (almost) none resolvable to a leaf from their source label (either a missing leaf or a label coarser than the leaves; decide from object titles and dates) | leaf 2% of 9,886 in scope; general 9,663, missing 6; leaves in other families: E | 9,886 |
| high | egypt × G | unverified coverage: many objects in this medium, (almost) none resolvable to a leaf from their source label (either a missing leaf or a label coarser than the leaves; decide from object titles and dates) | leaf 0% of 9,445 in scope; general 365, missing 9,080; leaves in other families: CEFHI | 9,445 |
| high | italy × H | unverified coverage: many objects in this medium, (almost) none resolvable to a leaf from their source label (either a missing leaf or a label coarser than the leaves; decide from object titles and dates) | leaf 2% of 9,418 in scope; general 9,193, missing 0; leaves in other families: DEFG | 9,418 |
| high | china × G | unverified coverage: many objects in this medium, (almost) none resolvable to a leaf from their source label (either a missing leaf or a label coarser than the leaves; decide from object titles and dates) | leaf 0% of 9,021 in scope; general 8,478, missing 543; leaves in other families: ABCDEIJ | 9,021 |
| high | india × H | unverified coverage: many objects in this medium, (almost) none resolvable to a leaf from their source label (either a missing leaf or a label coarser than the leaves; decide from object titles and dates) | leaf 1% of 8,359 in scope; general 8,250, missing 0; leaves in other families: ADG | 8,359 |
| high | india × G | unverified coverage: many objects in this medium, (almost) none resolvable to a leaf from their source label (either a missing leaf or a label coarser than the leaves; decide from object titles and dates) | leaf 1% of 5,944 in scope; general 5,878, missing 0; leaves in other families: ADH | 5,944 |
| high | indonesia × D | unverified coverage: many objects in this medium, (almost) none resolvable to a leaf from their source label (either a missing leaf or a label coarser than the leaves; decide from object titles and dates) | leaf 0% of 5,909 in scope; general 5,575, missing 334; leaves in other families: AG | 5,909 |

### Open named traditions (top 15)

| Severity | Where | What | Evidence | Objects |
|---|---|---|---|---:|
| high | Ancient Egyptian Jewellery and Metalwork | named tradition with gathered objects and no leaf | families G; max institutions per key 2; labels: 26th; 30th Dynasty; Egyptian; Egyptian / 26th; Egyptian / 30th Dynasty; Egyptian / Late Dynastic; Eg | 20,847 |
| high | Seljuk Stucco | named tradition with gathered objects and no leaf | families ?; max institutions per key 2; labels: Iranian; Iranian / Seljuq; Seljuq | 6,651 |
| high | Cypriot Pottery | named tradition with gathered objects and no leaf | families E; max institutions per key 2; labels: Cypriot; Cypriot / Bronze Age; Cypriot / Cypro-Archaic; Cypriot / Cypro-Geometric; Cypriot / Early C | 3,828 |
| high | Cypriot Sculpture | named tradition with gathered objects and no leaf | families DE; max institutions per key 2; labels: Cypriot; Cypriot / Archaic; Cypriot / Classical; Cypriot / Cypro-Classical; Cypriot / Hellenistic; C | 1,690 |
| high | Ancient Greek Bronzes | named tradition with gathered objects and no leaf | families G; max institutions per key 2; labels: Greek; Greek / Classical; Greek / Geometric; Greek / Hellenistic; Greek, Cretan; Greek, Cretan / Arc | 1,275 |
| medium | Mamluk Pottery | named tradition with gathered objects and no leaf | families E; max institutions per key 1; labels: Egyptian / Mamluk; Mamluk; Syrian / Mamluk | 1,613 |
| medium | Predynastic Egyptian Pottery | named tradition with gathered objects and no leaf | families E; max institutions per key 1; labels: Egyptian / Naqada; Egyptian / Predynastic Period; Naqada; Predynastic Period | 1,258 |
| medium | Native American Studio Painting | named tradition with gathered objects and no leaf | families A; max institutions per key 1; labels: Absentee Shawnee; Absentee Shawnee [Shawnee, Oklahoma-Pottawatomie County]; Diné (Navajo); Eastern B | 1,252 |
| medium | Chican Ostionoid (Taíno) pottery | named tradition with gathered objects and no leaf | families E; max institutions per key 1; labels: possibly Chican Ostionoid (Chicoid) (archaeological culture) (attributed); probably Chican Ostionoid | 1,151 |
| medium | Ehon (Japanese woodblock-printed books) | named tradition with gathered objects and no leaf | families C; max institutions per key 1; labels: Japan · 1682; Japan · 1683; Japan · 1720; Japan · 1735; Japan · 1752; Japan · 1765; Japan · 1771; Ja | 1,066 |
| medium | Mughal Textiles | named tradition with gathered objects and no leaf | families E; max institutions per key 1; labels: Indian / Mughal; Mughal; Pakistani / Mughal | 1,046 |
| medium | Sasanian Stamp Seals | named tradition with gathered objects and no leaf | families D; max institutions per key 1; labels: Sasanian; Sasanian / Sasanian | 961 |
| medium | Roman Metalwork | named tradition with gathered objects and no leaf | families G; max institutions per key 1; labels: Mid-Imperial; Roman; Roman / Hellenistic; Roman / Mid-Imperial | 867 |
| medium | Lydian Pottery | named tradition with gathered objects and no leaf | families E; max institutions per key 1; labels: Lydian; Lydian / Archaic; Lydian / Geometric; Lydian, Sardis; Lydian, Sardis / Geometric | 646 |
| medium | Krobo glass beads | named tradition with gathered objects and no leaf | families F; max institutions per key 4; labels: Ghanaian | 618 |

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
