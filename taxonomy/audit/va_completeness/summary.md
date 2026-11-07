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
| J Photography | 83 | 3,159 | 6,467 | 3,858 | 1% |
| L Art in Place | 114 | 0 | 0 | 0 | 100% |
| ? unknown type | 0 | 52,043 | 7,371 | 185,069 | 0% |
| **All** | 437,354 | 863,008 | 102,283 | 255,862 | **31%** |

Of the general-only objects, 18,256 sit under labels reviewed and kept general (`v2_review.csv`: the named leaf does not hold the whole label), 794 under unreviewed labels whose qualifier names a leaf, and 74,465 under qualified labels no leaf carries. V3 counts general objects resolved by their own titles (`v3_cells.csv`, `pipelines/r3/collections_resolve.py`).

## Flags by check

| Check | High | Medium | Low |
|---|---:|---:|---:|
| V2 | 0 | 13 | 60 |
| V3 | 18 | 40 | 39 |
| V4 | 0 | 0 | 223 |
| V5 | 0 | 0 | 1 |
| V6 | 0 | 0 | 508 |

V4: 385 named missing traditions in the mapping, 162 now carried by a leaf name, 223 open. V6: 114 rows in leftover per-object works lists.

## V8 Region × medium: leaves (museum records)

Each cell: leaves in the tree, then gathered museum records in thousands. A dash is an empty cell; **bold** marks a cell with evidence and no leaf. Full table in `region_medium.csv`.

| Region | A | B | C | D | E | F | G | H | I | J | K | L |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Western Europe | 81 | 8 (1k) | 14 (64k) | 26 (6k) | 24 (82k) | 6 (6k) | 25 (14k) | 60 (37k) | 28 (1k) | 6 (2k) | 56 | 19 |
| Central & Eastern Europe | 24 (2k) | 3 | 5 | 18 (2k) | 12 (1k) | 4 | 7 (2k) | 54 (8k) | 12 (2k) | – | 19 | 7 |
| Greco-Roman & Byzantine Mediterranean | 5 (7k) | – | 1 (1k) | 13 (4k) | 16 (4k) | 3 (8k) | 9 (4k) | 3 | – | – | 10 | 9 |
| Ancient Egypt & Nubia | – | – | 1 | 3 (1k) | 5 (4k) | 1 | 1 (2k) | 2 | – | – | 2 | 2 |
| Ancient Near East | – | – | 1 | 5 (5k) | 9 (1k) | 1 | 5 (1k) | 1 | – | – | 6 | 3 |
| Islamic world (MENA, Iran, Anatolia) | 6 (6k) | 2 (1k) | 9 (6k) | 9 (7k) | 25 (57k) | 7 (3k) | 12 (24k) | 29 (14k) | 11 (2k) | – | 22 | 9 |
| Central Asia & Silk Road | 1 (1k) | – | 1 (3k) | 2 (1k) | 1 | – | 3 (1k) | 9 (3k) | – | – | 1 | 6 |
| Himalaya | 8 (5k) | – | 3 (3k) | 5 (3k) | **–** | – | 2 (2k) | 3 (2k) | 2 | – | 4 | 2 |
| South Asia | 24 (19k) | 1 (2k) | 2 (1k) | 13 (3k) | 5 (2k) | – (1k) | 7 (10k) | 30 (12k) | 8 (2k) | – | 18 | 13 |
| Southeast Asia | 7 (12k) | 2 (3k) | 5 (3k) | 15 (9k) | 7 (3k) | **– (4k)** | 3 (53k) | 20 (54k) | 4 (23k) | 1 (6k) | 15 | 7 |
| China | 10 (19k) | 2 (2k) | 5 (11k) | 9 (10k) | 25 (44k) | 1 | 7 (10k) | 12 (2k) | 6 (3k) | – | 12 | 2 |
| Japan | 13 (23k) | 5 (39k) | 4 (35k) | 11 (11k) | 22 (29k) | 2 | 9 (43k) | 15 (19k) | 12 (11k) | 1 | 14 | 4 |
| Korea | 5 (5k) | – | 3 (2k) | 2 | 8 (3k) | – | 5 (2k) | 7 (1k) | 4 | – | 2 | 3 |
| Sub-Saharan Africa | 11 (1k) | – | 3 (1k) | 55 (4k) | 4 (9k) | 1 (1k) | 3 (17k) | 27 (16k) | 3 (9k) | 1 | 7 | 9 |
| North America (Indigenous) | 6 (4k) | 2 (1k) | – | 9 (7k) | 16 (23k) | **– (1k)** | 4 (10k) | 32 (23k) | 2 (7k) | – | 3 | 8 |
| North America (settler) | 25 | 2 (1k) | 1 | 7 | 2 (1k) | 1 | 2 (1k) | 6 (13k) | 2 | 5 | 14 | 2 |
| Mesoamerica & Caribbean | 7 (1k) | 1 | 2 | 14 (5k) | 26 (19k) | – | 4 (2k) | 13 (5k) | 1 (1k) | – | 5 | 5 |
| South America | 12 (2k) | 1 | – | 8 (1k) | 29 (15k) | – | 13 (7k) | 16 (13k) | 3 (4k) | – | 4 | 11 |
| Oceania (Pacific) | 3 (1k) | – | – | 13 (6k) | 3 (1k) | – | 2 (14k) | 8 (12k) | 6 (7k) | – | 7 | 4 |
| Australia (Aboriginal) | 3 | 1 | – | 4 | 1 | – | 1 (1k) | 2 | – | – | – | 5 |

Reviewed cells (`v8_review.csv`):

| Cell | Decision | Reason |
|---|---|---|
| B × South Asia | covered | B2-22 Indian Chromolithographs added; most 'Indian' print records are bazaar prints of that tradition |
| C × South Asia | false signal | the 568 'Indian' book-arts records are miniature paintings (A1); manuscripts are covered by C2-5 and A1-9 Jain Manuscript Painting |
| E × Himalaya | false signal | records typed as ceramics are skull cups and Tara figures; no attested Himalayan pottery tradition found (Nixi pottery not attested here) |
| F × Southeast Asia | false signal | the 3854 'Indonesian' glass records are frogs masks and figures typed as glass by their materials list |
| F × North America (Indigenous) | covered | the records are glass trade beads on beadwork: H9-11 Great Lakes and H9-16 Subarctic Floral Beadwork added |
| F × Ancient Near East | covered | F1-19 Late Bronze Age Glass added; Phoenician core-formed glass is in F1-4 |
| G × Ancient Egypt & Nubia | covered | G3-31 Ancient Egyptian Jewellery & Amulets (its region facet corrected) |
| G × Himalaya | covered | G2-14 Tibetan Arms and Armour added; Himalayan metal images are D5-9 and D5-11 |
| G × Oceania (Pacific) | partly covered | G3-33 Kula Valuables added; the rest are spears and clubs (wood) with no attested leaf beyond I1-15 Fijian Clubs; pounamu is D3-9 |
| H × Greco-Roman & Byzantine Mediterranean | covered | H3-61 Byzantine Silk added |
| H × Himalaya | covered | H3-62 Bhutanese Textiles added; Tibetan rugs H1-13 and Kashmir shawls H3-6 |
| I × North America (Indigenous) | covered | I1-31 Northwest Coast Woodcarving holds the NW Coast records; the rest are arrows drums and pipes (arms and instruments) |
| I × Oceania (Pacific) | partly covered | I1-15 Fijian Clubs; the Papua New Guinea wood figures are D5 sculpture (Sepik Carving etc.); headrests and kava bowls have no attested leaf yet |
| J × Southeast Asia | covered | J1-18 Photography in the Dutch East Indies added (36 labels remapped) |
| E × Oceania (Pacific) | covered | E1-147 Lapita Pottery and E1-148 Sepik Pottery added |

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
| low | Mezcala Stone Sculpture | named tradition with gathered objects and no leaf | families D; max institutions per key 1; labels: Mezcala | 153 |
| low | Fon Metal Sculpture | named tradition with gathered objects and no leaf | families G; max institutions per key 1; labels: Fon | 101 |
| low | Irish Cut Glass | named tradition with gathered objects and no leaf | families F; max institutions per key 2; labels: Irish | 89 |
| low | Gupta Sculpture | named tradition with gathered objects and no leaf | families D; max institutions per key 1; labels: Gupta period; Indian / Gupta period | 67 |
| low | Shipibo-Conibo Textiles | named tradition with gathered objects and no leaf | families EH; max institutions per key 1; labels: Conibo; Shipibo; Shipibo-Conibo | 64 |
| low | Dali Kingdom Buddhist sculpture | named tradition with gathered objects and no leaf | families DG; max institutions per key 7; labels: Dali Kingdom (Yunnan) | 49 |
| low | Barrancoid pottery | named tradition with gathered objects and no leaf | families E; max institutions per key 1; labels: possibly Barrancoid Tradition (archaeological culture) (attributed); probably Barrancoid Tradition ( | 49 |
| low | Casma pottery | named tradition with gathered objects and no leaf | families E; max institutions per key 1; labels: possibly Casma or Ychsma (Ichma) (archaeological culture) (attributed; probably Casma (archaeologica | 48 |
| low | Kichwa pottery | named tradition with gathered objects and no leaf | families E; max institutions per key 1; labels: probably Highland Kichua (attributed) | 47 |
| low | Mandan pottery | named tradition with gathered objects and no leaf | families E; max institutions per key 1; labels: Numakiki (Mandan); probably Plains Village Tradition: Numakiki (Mandan) (archaeological) (attributed | 47 |
| low | Tzeltal Maya pottery (Amatenango) | named tradition with gathered objects and no leaf | families E; max institutions per key 1; labels: Oxchuc Tzeltal Maya (Occucero); probably Tzeltal Maya (attributed) | 47 |
| low | Burmese Buddhist sculpture | named tradition with gathered objects and no leaf | families D; max institutions per key 3; labels: Burmese | 46 |
| low | Chupícuaro ceramics | named tradition with gathered objects and no leaf | families E; max institutions per key 2; labels: Chupicuaro; probably Chupícuaro (archaeological culture) (attributed) | 46 |
| low | Cupisnique pottery | named tradition with gathered objects and no leaf | families E; max institutions per key 2; labels: Cupisnique; probably Chavín or Cupisnique (archaeological culture) (attributed) | 46 |
| low | Zulu pottery (ukhamba) | named tradition with gathered objects and no leaf | families E; max institutions per key 7; labels: Zulu; Zulu ceramics (ukhamba) and wire baskets (imbenge) | 46 |
