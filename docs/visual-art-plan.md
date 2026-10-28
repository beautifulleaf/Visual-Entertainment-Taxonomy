# Visual art: deep dive (structure, sources, metrics)

Status: proposal (2026-10-27). Numbers marked *measured* come from live Wikidata SPARQL queries on that date.

## 1. Structure

The taxonomy is a **region × period grid**, with art traditions inside each cell:

```
Region (e.g. East Asia)
 └ Period (e.g. Song dynasty, 960–1279)
    └ Tradition / movement / school (e.g. Northern Song monumental landscape)
       └ Artist  or  Workshop / culture group (for unattributed work)
          └ Representative works (3–10, from open-access museum records)
```

- **Grid backbone:** the Met's *Heilbrunn Timeline of Art History* (a region-by-period chronology that is already worldwide) and Smarthistory's survey structure, mapped onto **Getty AAT** style and period terms so every node has a stable ID.
- **Named artists** only where the tradition records authorship. Elsewhere the leaf is a **culture or workshop node** (Attic red-figure, Benin court bronzes, Nok terracotta, Moche portrait vessels, Gandhara sculpture, Aboriginal rock art). Known names hang under these nodes (e.g. Exekias under Attic black-figure).
- **Contemporary is not one bucket.** After about 1960 the grid stays regional (Gutai, Dansaekhwa, Cynical Realism, the Dakar School, Neo-concretism, the Hurufiyya movement), and there is also a cross-regional layer of *global contemporary* movements and media (see §4).

## 2. Historical art (pre-1960): sources and metric

| Source | Role | Access / notes |
|---|---|---|
| Wikidata | artists, movements (P135), dates, citizenship, sitelinks, ID crosswalk | SPARQL / dumps, CC0 |
| Getty ULAN / AAT / TGN | artist authority; style, period and culture terms; places | LOD N-Triples only. XML and relational downloads retired; final static dump dated 2026-01-30 |
| Met (470k+ objects), AIC, Cleveland, NGA, Smithsonian (incl. the National Museum of Asian Art and the National Museum of African Art), Rijksmuseum | institutional presence; representative works; `culture` field for unattributed work | CC0 CSV/JSON/APIs |
| ColBase (Japan's national museums), National Palace Museum Taiwan open data | East Asian depth | open |
| Europeana | European regional museums | API |
| WikiArt (Wikidata P6002, 5,694 linked, *measured*) | cross-check only | no official bulk API |

**Metric:** Wikidata **sitelink count** (number of Wikipedia language editions), thresholded **per region × period cell** at a percentile, with a global floor; plus the number of open-access museums holding the artist's work.
*Measured:* painters with ≥5 sitelinks = 24,946, ≥15 = 4,119; sculptors ≥5 = 6,773; photographers ≥5 = 7,033.

### 2.1 Depth target: calibrated from the reference lists
The target depth is the owner-supplied list in `seeds/visual-art/europe_1400-1900_depth_reference.txt`: WikiArt-style movement lists, 910 names from Early Renaissance to Realism. `pipelines/visual_art/calibrate_depth.py` matches each name to Wikidata. 837 matched by exact label, with birth-year and art-occupation guards; 75 of those are ambiguous and flagged for hand review, and 73 are unmatched, mostly spelling variants without diacritics such as "Albrecht Durer" or "Diego Velazquez".

*Measured sitelink distribution of the reference artists (p10 / p25 / median):*
| Movement | n | p10 | p25 | median |
|---|---|---|---|---|
| Early Renaissance | 22 | 22 | 30 | 40.5 |
| High Renaissance | 28 | 18 | 28 | 45 |
| Mannerism | 36 | 14 | 24 | 36.5 |
| Northern Renaissance | 47 | 13 | 18 | 33 |
| Baroque | 99 | 8 | 13 | 23 |
| Dutch Golden Age | 53 | 14 | 18 | 27 |
| Rococo | 56 | 9 | 19 | 26 |
| Neoclassicism | 50 | 7 | 11 | 23 |
| Romanticism | 249 | 4 | 8 | 16 |
| Academic Art | 78 | 4 | 9 | 14 |
| Realism / Naturalism | 192 | 3 | 8 | 15 |
| **All** | 910 | **5** | **11** | **21** |

**Finding: a sitelink cutoff alone cannot reproduce this depth.** Painters born 1300–1900 worldwide: ≥5 sitelinks = 16,561 (18× the reference, still missing ~10% of it); ≥12 = 4,269 (missing ~25%). The reference is a *curated* top tier, roughly the most-exhibited and most-reproduced ~900 painters of 1400–1900 Europe, not everyone with some Wikipedia presence.

**Method: treat the reference as labelled training data.**
1. Candidate pool for the reference cells: **visual artists in every medium** active 1400–1900 in Europe and its colonies, with ≥3 sitelinks.
   **Decided 2026-10-28:** painters only was too narrow for a visual-art taxonomy. Occupations are grouped into media (`regions.MEDIA`): painting, sculpture, architecture, photography, printmaking, book arts, design and decorative arts, drawing and illustration, and unspecified visual art. Each artist gets a primary medium (the first matching group in that order) and keeps all their media for placement in the taxonomy (Michelangelo sits under painting, sculpture and architecture).
   Medium is the third cell axis: features are percentiles within medium × period. The reference list is painting movements, so the model is **fitted on the painting cells plus every reference artist** (Bernini, Canova and Piranesi count as positives), and then scores every medium with the same coefficients and cutoff. Famous sculptors and architects aren't on a painting list, so treating them as negatives would teach the model the wrong thing.
2. Features: sitelinks, pageviews, number of open-access museums holding work, number of Heilbrunn Timeline works, ULAN record, WikiArt ID, and Art UK / RKD / national-database IDs.
3. Fit a simple, interpretable model (logistic regression) predicting reference membership. Pick the score cutoff that recovers about 95% of the reference, which matches "if in doubt, include".
4. Apply the same model to every other region × period cell. Features are percentile-normalised within the cell, so thinner Wikipedia coverage elsewhere doesn't empty those cells.
   **Decided (2026-10-27): harvest candidates once, take the evidence per region × era.** Wikidata is global, so the candidate fetch is done once worldwide and cached. Each region's config (`pipelines/visual_art/regions.py`) then names its own evidence:
   - **who counts as an artist:** painters for Europe; ink painters, calligraphers and ukiyo-e print designers for East Asia; miniaturists, illuminators and calligraphers for the Islamic world;
   - **which collections are decisive:** the Met, AIC and Cleveland as an encyclopedic baseline everywhere, plus specialists such as ColBase, the National Palace Museum and the National Museum of Asian Art for East Asia, or the V&A and the British Library for South Asia;
   - **which authority files count:** RKD, Art UK, Joconde, the Prado and others for Europe.

   The model sees only abstract features built from these (`museum_objects`, `n_museums`, `n_regional_ids`, plus sitelinks, pageviews, Timeline works, ULAN and WikiArt). So the coefficients fitted on Europe carry over while the sources behind each feature change by region.
5. Validate per region with further reference lists added to `seeds/visual-art/` (e.g. Chinese painting by dynasty, Ukiyo-e, Mughal/Rajput, Persian miniature, Latin American colonial), each in the same "Movement: names" format.

**First fit (2026-10-28), Europe 1400–1900, all media** (`pipelines/visual_art/depth_model.py`; coefficients in `pipelines/visual_art/models/europe_1400-1900.json`):
- **Data:**
  - Pool: 41,413 artists by the pool rule: painting 24,426, architecture 8,218, sculpture 3,868, photography 2,103, printmaking 1,156, drawing 773, design 638, book arts 154.
  - Positives: 889 reference artists. 20 others on the list were active only after 1900 and are left out.
  - Pageviews: September 2026 dump. Holdings: Met 7,331 artists, AIC 2,761, Cleveland 1,945; Met Timeline 1,094.
- **Two corrections were needed:**
  - **`has_wikiart` is excluded.** The reference lists are WikiArt's movement lists, so the ID leaked the label: it took a +14.8 coefficient, and the model picked almost no sculptors or architects.
  - **Coefficients are constrained to be ≥ 0.** Unconstrained, sitelinks and pageviews took opposite signs.
- **Coefficients** (all features are within-cell percentiles): pageviews +5.40 · Met Timeline works +1.98 · regional authority IDs +1.35 · sitelinks +0.94 · number of museums +0.40 · ULAN +0.26 · museum objects 0.00.
- **Top non-reference picks:** Impressionists and Post-Impressionists (the reference stops at Realism), Rodin, Saint-Gaudens, Frank Lloyd Wright, William Morris, Lalique, Pugin, Stieglitz, Mucha.
- **Recall vs. size:**

| Reference recall | Selected | Painting | Sculpture | Architecture | Printmaking | Photography | Drawing | Design | Book arts |
|---|---|---|---|---|---|---|---|---|---|
| 70% | 4,296 | 2,689 | 409 | 774 | 94 | 208 | 56 | 53 | 9 |
| 80% | 6,876 | 4,182 | 664 | 1,267 | 177 | 340 | 117 | 95 | 26 |
| 85% | 9,412 | 5,687 | 885 | 1,770 | 269 | 456 | 166 | 133 | 33 |
| 90% | 12,971 | 7,723 | 1,195 | 2,518 | 364 | 662 | 247 | 197 | 44 |
| **95%** | **22,434** | 13,199 | 2,104 | 4,450 | 640 | 1,133 | 430 | 347 | 85 |

- **At the 95% target the cutoff is very low.** The bottom 5% of the reference list have almost no presence in any source (Mazzolini, Bidau, Papin score ≈ 0), so the cutoff (score 0.0049) takes about half the pool. Cross-validated, the same cutoff recovers 94.8% out of fold.
- **Open decision:** keep 95% (22k), or take 90% (13k) and add the stragglers explicitly as reference members. Architecture is large at any cutoff, because Wikidata documents 19th-century architects densely; a per-medium cap or a higher architecture cutoff may be wanted.

## 2A. Unattributed traditions: antiquity, decorative arts, architecture

A large part of world art has no recorded maker. *Measured* in the Met's open-access CSV (503,012 objects): **40% have no artist**, rising to 94–99% in the Greek and Roman, Egyptian, Islamic, Medieval and Ancient West Asian departments, 72% in Asian Art and 67% in European Sculpture and Decorative Arts. These traditions therefore need their **own node type and their own prominence signals**, not the artist pipeline.

### Node types
| Node | Examples | Children |
|---|---|---|
| **Culture / period style** | Attic red-figure, Benin court art, Nok, Moche, Gandhara, Mamluk, Nazca, Jōmon | object traditions, representative works, known names where they exist (Exekias) |
| **Object tradition / ware** (region × medium) | Iznik ware, Song celadon, Ming blue-and-white, Persian carpets by centre (Tabriz, Kashan), Mamluk enamelled glass, Limoges enamel, Chinese lacquer, Kente cloth | representative works |
| **Workshop / manufactory** | Sèvres, Meissen, Gobelins, Wedgwood, Tiffany Studios, Kakiemon kilns | designers where known, representative works |
| **Architectural style** | Gothic, Mughal, Khmer, Nara-period temple style, Pueblo, Brutalism | exemplar buildings and sites, named architects where attributed |
| **Monument / site** | Angkor Wat, Hagia Sophia, Great Zimbabwe, Chartres | — |

Medium is a third axis alongside region and period: painting and calligraphy, sculpture, ceramics, glass, metalwork and jewellery, textiles and carpets, furniture and woodwork, lacquer, manuscripts and the arts of the book, arms and armour, costume, musical instruments, architecture.

### Sources
| Source | Role |
|---|---|
| **Met Heilbrunn Timeline works** | *Measured:* 7,946 Timeline works, 3,210 of them unattributed, spanning **578 distinct cultures**. This is the curatorial equivalent of the WikiArt lists for unattributed art, so it serves as the depth benchmark. |
| Met / AIC / Cleveland / Smithsonian (incl. Cooper Hewitt and the National Museum of Asian Art) / Rijksmuseum / V&A open data | `culture`, `period`, `dynasty`, `classification` fields. *Measured (Met, unattributed only):* 5,954 distinct culture strings, of which 206 have ≥50 objects and 32 have ≥500; 137 periods with ≥50 objects. The culture strings need normalising to AAT terms. |
| **Getty AAT** | the styles/periods/cultures facet and the object-type hierarchy: stable IDs for every tradition and medium node |
| **Wikidata** | *Measured, items with ≥5 / ≥15 sitelinks:* architectural styles 401 / 171, art movements 445 / 211, art styles 160 / 85, archaeological cultures 580 / 185 |
| **UNESCO World Heritage List** (~1,200 sites) + Wikidata buildings by sitelinks | exemplar monuments for architecture and sites |
| ColBase, National Palace Museum, ICOM / national museum portals | East Asian ceramics, bronzes and lacquer, plus regional depth |

*Measured, first harvest (2026-10-28, `pipelines/unattributed/build_traditions.py`):*
- **Input:** 193,847 unattributed Met objects. Placeholder makers ("Unidentified artist", "Yoruba artist", the Benin brass-casting guild) count as unattributed; the Drawings and Prints, Photographs and Libraries departments are excluded.
- **Cultures:** 6,394 raw culture strings normalise to 4,329 culture keys at two levels (`greek` > `greek, attic`), plus 822 culture × period and 342 period rows. 228 cultures have ≥50 objects, 41 have ≥500, and 668 have Timeline works.
- **Object traditions:** 8,895 rows of culture × classification and culture × technique. Technique comes from the Medium field (blue-and-white, celadon, sancai, stonepaste, lustreware, maki-e, ...).
- **AIC:** adds counts for 295 cultures (by place of origin). Cleveland is skipped, because the fetched data has no culture field.
- **Caveats:**
  - The Met records no Period or Dynasty on Islamic Art objects, so the dynasty (Mamluk, Safavid, Timurid, Ottoman, ...) is inferred from culture plus date (`ISLAMIC_PERIODS`).
  - Attic red-figure vs black-figure cannot be split: the Met CSV never records it.
- **Pending:** the Getty AAT mapping. vocab.getty.edu returned 499/403 throughout, so re-run the script when it's back; the AAT columns are empty until then.

### Prominence metric (tradition nodes)
Each signal is a percentile within its region × period cell:
1. **Curatorial:** has Heilbrunn Timeline works, or a Smarthistory or Heilbrunn essay (auto-include).
2. **Institutional:** the number of objects across open-access museums, and the number of museums holding it.
3. **Attention:** Wikidata sitelinks of the tradition item, plus pageviews.
4. **Architecture only:** the number of UNESCO-listed and high-sitelink exemplar buildings.

Representative works per node: 3–10, preferring Timeline works and museum "highlights" (the Met's `Is Highlight` flag), then public-domain images.

## 3. Living and contemporary artists

This is the hardest part. No single source measures prominence the way IMDb or Letterboxd votes do for film, and every ranking is skewed toward Europe and the US. ArtReview's Power 100 for 2006–2012 was about 0.4% African; Artfacts and Kunstkompass are Euro-centric by design. So **contemporary prominence has to be built as a composite of independent signals.**

### 3.1 What Wikidata gives us (*measured*, living = born ≥1930 with no death date)
| Slice | Count |
|---|---|
| Living painters, sitelinks ≥3 / ≥10 / ≥20 | 7,579 / 874 / 270 |
| Living (≥5 sitelinks): sculptors 1,364 · photographers 2,741 · "visual artist" 1,028 · installation artists 624 · draftspersons 629 · graphic artists 420 | — |
| Living people with an **Artnet** ID | 10,300 |
| Living people with an **Artsy** ID | 7,966 |
| Living people with a **MoMA** ID | 6,030 |
| Humans with gallery representation ("represented by", P1875) | 11,262 |
| Humans with exhibition history (P608) | 535 (too sparse to use) |
| Artfacts ID properties P13700 / P8943 | 257 / 672 (sparse, so Artfacts has to be matched by name) |
| Living painters (≥3 sitelinks) with an Instagram handle | 582 (sparse) |

Wikidata is therefore a good **candidate pool and ID crosswalk**, but weak as a prominence measure for living artists, because sitelinks lag a career by 5–15 years.

### 3.2 Signals and sources

| Signal | Source | Access | What it captures |
|---|---|---|---|
| **Institutional ranking** | **Artfacts** (1M+ artists, 1M+ exhibitions, daily-updated network ranking) | €15/month "Discover" shows ranks; **API/bulk only via enterprise contact** (support@artfacts.net); free public top-100 list | exhibition record at weighted institutions; the best single art-world signal |
| **Annual canon lists** | **Kunstkompass** (Capital, top 100 living + "stars of tomorrow"; 2025 edition published Nov 2025), **ArtReview Power 100** (Dec 2025; people, not only artists), **Monopol Top 100** | public web pages, about 300 names a year; transcribe | consensus top tier |
| **Market** | **Artprice** *Contemporary Art Market Report*: Top 500 contemporary + Top 100 ultra-contemporary (born after 1980). The 2026 edition covers Jul 2025–Jun 2026 and was released Oct 2026 | free account, PDF | collector demand; catches market-led names (KAWS, Beeple, Anadol) |
| **Biennial / mega-exhibition participation** | **Universes in Universe** (consistent participant lists for Venice, documenta, São Paulo, Gwangju, Sharjah, Dak'Art, Havana, Istanbul and others; e.g. Venice 2026, 110 participants) + Biennial Foundation | public pages, structured lists | curatorial recognition; the **best non-Western signal**, because Sharjah, Dak'Art, Gwangju, Kochi-Muziris and the Asia Pacific Triennial are built around regional scenes |
| **Museum collections** | MoMA artists CSV (15,995 artists with QID + ULAN), Tate (about 3,500 artists), Met, AIC, Smithsonian (Hirshhorn, the Smithsonian American Art Museum, the National Museum of African Art) | CC0 GitHub/APIs | permanent institutional validation |
| **Gallery representation** | Wikidata P1875 + public **artist rosters** of about 25 blue-chip and regional-leader galleries (Gagosian, Zwirner, Hauser & Wirth, Pace, White Cube, Lisson, Perrotin, Ropac, Sprüth Magers, Marian Goodman, kurimanzutto, Goodman Gallery, Stevenson, Mendes Wood DM, ShanghART, Kukje, Tina Kim, Experimenter, Sfeir-Semler, and others) | small public HTML lists; 25 pages to transcribe | market entry point; regional leaders matter more than global mega-galleries for non-Western coverage |
| **Major prizes** | Golden Lion, Turner, Hugo Boss, Praemium Imperiale, Prix Marcel Duchamp, Hepworth, Future Generation, Prince Claus, Sovereign Asian Art Prize, FNB Art Prize, the Jameel Prize, and others | Wikidata P166 + Wikipedia winner lists | peer recognition |
| **Consumer attention** | **Wikipedia pageviews** across all language editions (Wikimedia monthly bulk dumps; the REST API rate-limits shared IPs), multilingual sitelinks, The Art Newspaper's annual **exhibition attendance** survey | free | what the public actually seeks out: Kusama, Banksy, teamLab, Hockney |

### 3.3 Regional depth sources (to fill gaps the global signals miss)
- **East Asia:** Artron (artron.net, the dominant Chinese artist and auction database), MMCA Korea collection, ColBase / MOT Tokyo, M+ (Hong Kong) collection.
- **South and Southeast Asia:** Asia Art Archive (AAA, plus AAA in India), Art World Database (Southeast Asia), Saffronart auction records, Kochi-Muziris Biennale lists.
- **Africa:** Contemporary And (C&), Dak'Art and Lagos/Bamako biennial lists, the Zeitz MOCAA and National Museum of African Art collections, Goodman and Stevenson rosters.
- **Latin America:** ICAA Documents Project (MFAH), Bienal de São Paulo archive, Arte al Día, kurimanzutto and Mendes Wood rosters.
- **Middle East / North Africa:** Barjeel Art Foundation, Mathaf, Sharjah Art Foundation, the Jameel Prize.
- **Indigenous contemporary:** national-gallery collections (Australia, Canada, NZ), the Sydney Biennale, and the Smithsonian National Museum of the American Indian.

Verify each of these for bulk access before building on it; several are browse-only.

### 3.4 Consumer-relevant categories that art-world rankings under-count
Each gets its own node so it is not filtered out by institution-centric metrics:
- **Street art and muralism** (Banksy, JR, Os Gêmeos, Shepard Fairey, Vhils)
- **Pop-market crossover** (KAWS, Murakami, Yoshitomo Nara, Daniel Arsham)
- **Immersive and digital** (teamLab, Refik Anadol, Studio Drift), and **NFT/crypto art** (Beeple, XCOPY)
- **Illustration and comics crossover** (Moebius lineage, Yoshitaka Amano, Kim Jung Gi)
- **Self-taught / outsider** (an Outsider Art Fair or Collection de l'Art Brut node)
- **Craft-based contemporary** (ceramics, textiles, glass)

The **consumer attention** and **market** signals carry these categories, which is why those two signals are in the composite.

### 3.5 Inclusion rule (proposal)
Normalise each signal to a percentile **within the artist's region** (by citizenship or base). Score = weighted sum, with proposed weights:

| Signal | Weight |
|---|---|
| Artfacts rank (or a proxy if no subscription) | 0.25 |
| Biennial / mega-exhibition count (main exhibitions, last 30 years) | 0.20 |
| Museum collections (number of major open-data museums holding work) | 0.15 |
| Consumer attention (pageviews across languages, plus sitelinks) | 0.20 |
| Market (Artprice Top 500/100, Artnet presence) | 0.10 |
| Prizes + gallery representation | 0.10 |

- **Auto-include:** any appearance on Kunstkompass, the Power 100 (artists only), the Artprice Top 500, Venice or documenta main exhibitions, or a top prize.
- **Include:** composite score ≥ the regional cutoff, chosen so each region lands at a set share of the total. That keeps Western dominance in check without fixed quotas.
- **Expected size:** roughly **5–10k living and contemporary artists**. This rests on about 7.6k living painters with ≥3 sitelinks plus the other media slices; it gets checked once the candidate pool is built.

### 3.6 Refresh cadence
- Annual: Kunstkompass, Power 100 and Artprice (Oct–Dec), and biennial lists as each opens.
- Monthly: pageviews.
- Quarterly: Artfacts, if subscribed.

## 4. Decisions
1. **Scale: maximise coverage** (decided 2026-10-27). Use the broad end of the range, about 10k+ living and contemporary artists, with cutoffs set low enough that every region × medium cell is represented. If in doubt, include.
2. **Contemporary = active after 1960** (the art-historical convention; it captures Gutai, Dansaekhwa, Pop and Conceptual art as contemporary-era nodes).
3. **Artfacts: deferred.** Start with the free signals; add Artfacts (€15/month, or a research/API request) if emerging artists turn out under-covered.
