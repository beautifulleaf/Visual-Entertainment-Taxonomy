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
