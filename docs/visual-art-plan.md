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
4. **Decided (2026-10-28): each region × period cell has an attribution profile, and it decides the main node type.** The profile is measured as the share of attributed objects in the museum data (Met, regional sweeps), not assumed.
   - **Tradition-led cells:** Persian and Islamic book painting, Mughal and Rajput painting, Byzantine icons, medieval Europe, most of Africa, Oceania and the pre-Columbian Americas.
     - The primary nodes are schools, styles and workshops (Timurid Herat, Safavid Tabriz, the Mughal atelier, Mewar, Kangra/Pahari, Deccani, ...), selected with the tradition metric (§2A), not the artist model.
     - Named masters (Behzad, Reza Abbasi, Basawan, Nainsukh) hang under their school and come in with it.
     - Landmark works can be nodes in their own right where they define a tradition (the *Shahnameh* of Shah Tahmasp, the *Hamzanama*, the *Book of Kells*).
   - **Artist-led cells:** Europe from about 1400, Chinese literati painting, ukiyo-e and Rinpa, colonial and modern Latin America. The artist model applies here, with schools and movements as the grouping above the artists.
   - **Mixed cells** use both.
   So the step below, applying the artist model to other cells, applies only to artist-led and mixed cells:
   Apply the same model to every other region × period cell. Features are percentile-normalised within the cell, so thinner Wikipedia coverage elsewhere doesn't empty those cells.
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
- **Decided (2026-10-28): cutoff at 90% reference recall, with the whole reference list included regardless of score, and architecture excluded from model selection (see below).** That selects **10,543 artists** for Europe 1400–1900: painting 7,806 · sculpture 1,196 · photography 662 · printmaking 367 · drawing 247 · design 197 · book arts 44 · unspecified 23 · architecture 1 (its reference entry). The 95% option was rejected: its extra ~9,400 artists are mostly the Wikipedia long tail (3–8 language editions, ~50–140 page views a month), and this region calibrates every other, so it would inflate them all. The rule is `depth_model.select()`; the default `--recall` is 0.90.
- *Earlier options considered:* keep 95% (22k), or take 90% (13k) and add the stragglers explicitly as reference members. Architecture is large at any cutoff, because Wikidata documents 19th-century architects densely; a per-medium cap or a higher architecture cutoff may be wanted.
- **Decided (2026-10-28): architecture is organised by *style*, not by architect.** Premodern architecture is mostly not architect-based, and Wikidata's architect coverage is skewed to 19th-century municipal practice. So:
  - the node is the **architectural style** (Romanesque, Gothic, Mughal, Khmer, Nara-period temple, Brutalism, ...) in its region × period cell, with Getty AAT style terms as IDs. Inclusion uses the tradition-node metric (§2A: curatorial presence, sitelinks, pageviews, number of heritage-listed exemplars);
  - **buildings are the style's representative works**: 3–10 per style, chosen by architectural style (P149) and ranked by heritage designation (UNESCO P757, P1435) and sitelinks;
  - **named architects hang under the style**, attached via the buildings they designed (P84);
  - the depth model does not select architects on its own; its architecture rows are kept only as a cross-check.
  - The style and exemplar-building harvest is queued behind the current Wikidata jobs.

### 2.1b Regional sweeps: results so far
- **Smithsonian Open Access** (`pipelines/regional/smithsonian.py`, 2026-10-28): 315,019 CC0 records across seven units.
  - **American Indian (NMAI): 237,752 objects**, 91% with a recorded culture and a culture-area hierarchy (Southwest, Woodlands, Plains, Mesoamerica, Andes, Arctic). This is the strongest source for the Indigenous Americas.
  - **The public bucket holds only part of the other collections:** Asian Art 4,720 records (79% with period or dynasty: Edo 780, Ming 359, Han 187, Goryeo 156, ...), African Art only 113, Hirshhorn 449. These regions need other sources (or api.si.edu with a key).
  - Cooper Hewitt (58,202), SAAM (13,783) and Hirshhorn record no culture or period, only makers.
  - No maker carries an outside ID (ULAN/Wikidata), so maker matching is a separate step.

- **Islamic world** (`pipelines/regional/islamic_world.py`, 2026-10-28): 21,086 objects (V&A 16,939, Discover Islamic Art 2,283 across 60 dynasty lists, Cleveland 1,864; Harvard skipped, no API key). Outputs `islamic_{objects,dynasties,schools,makers}.csv`.
  - **53 dynasties** with objects, including ones the Met inference cannot produce: Samanid, Buyid, Tulunid, Zirid, Hammadid, Taifa, Mudejar, Injuid, Jalayirid, Turkman.
  - **Recorded vs Met-inferred dynasty:** 7,049 agree and 1,077 conflict. The conflicts show where `ISLAMIC_PERIODS` is wrong: Deccani sultanates filed as Mughal (724), fuzzy Fatimid/Ayyubid/Mamluk boundaries, an Iranian gap from 1194 to 1256 (late Seljuq, Khwarazmian), and missing western dynasties (Mudejar, Taifa, Hammadid). Recorded labels override the inference.
  - **51 schools/workshops** (3,008 objects), e.g. Imperial Mughal atelier 926, Deccani Golconda 579, Company school 414, Prince Salim's atelier 364, Lucknow 108, Qajar Tehran 52, plus Safavid Tabriz/Qazvin/Isfahan/Shiraz and Timurid Herat/Shiraz. Persian schools are thin because the V&A rarely records a dynasty on Persian painting. 616 named makers hang under schools.
  - **Attributed share:** 4.7% of all objects; 11.5% of book arts (Safavid 31%, Ottoman 33%, Qajar 55%, Deccani 0.6%). So this region is **tradition-led**, with schools as the primary nodes and makers under them.
  - Limits: no cross-source de-duplication; school detection is regex-based (evidence for classifying, not a final node list).

- **Architecture styles** (`pipelines/architecture/build_styles.py`, 2026-10-28): 2,412 style items (669 with ≥5 sitelinks); 1,071 have tagged buildings (P149, 186,597 buildings); 14,245 exemplar rows (up to 15 per style, ranked UNESCO > part of UNESCO site > other heritage > sitelinks, plus 5,992 UNESCO items with no style); 2,688 architects of exemplars. Getty AAT links on only 259 styles (missing even for Gothic, Romanesque, Byzantine, Mughal, Ottoman), so a direct AAT match is needed once Getty is back.
  - **The style tags are Western-biased:** Gothic has 9,025 tagged buildings and Romanesque 9,126, against Khmer 3, Maya 6, Inca 2 and Hoysala 1. Nagara and Nara-period temple styles have no usable style item at all; Angkor, Chichen Itza, Machu Picchu, Hōryū-ji and Great Zimbabwe arrive only through the UNESCO list. Some tags are wrong: Angkor Wat is also tagged Dravidian, and the Taj Mahal "architecture of Iran".
  - A recent bulk import added 617 zero-sitelink "… architecture style" items, mostly Indian regional styles. They are kept for classification to judge and excluded from counts.
  - **Non-Western second pass done** (`pipelines/architecture/nonwestern_exemplars.py`). It uses 204 explicit rules on building class × country/admin region × date, plus UNESCO components outside Europe (rule table in `data/interim/architecture_nonwestern_rules.csv`, reviewed in classifying before anything goes into `seeds/`). 80,771 candidates, 20,283 assigned to 146 styles. Coverage, tagged buildings before → candidates now:

    | Style | Before | Now |
    |---|---|---|
    | Khmer (Angkorian) | 3 | 116 |
    | Maya (by sub-region, e.g. Puuc, Chenes, Río Bec) | 6 | 317 |
    | Inca | 2 | 121 |
    | Hoysala | 1 | 43 |
    | Nagara (Kalinga, Maru-Gurjara, Chandela, ...) | ~0 | 713 |
    | Asuka/Nara Buddhist temples | 5 | 297 |
    | Zimbabwe culture | 0 | 22 |
    | Ethiopian rock-hewn | 0 | 34 |
    | Javanese candi | ~6 | 136 |
    | Pagan | 0 | 25 |

    Also Thai, Lao, Cham, Newar, Swahili, Kushite, Mesoamerican and Andean cultures, Indo-Islamic, Mughal and Persian.
    - **Wrong existing tags flagged:** 15, e.g. Angkor Wat → Khmer (not Dravidian), Taj Mahal → Mughal.
    - **Known weaknesses:**
      - Only 98 of about 16k Indian temples carry a date, so the Dravidian dynasty sub-periods are thin.
      - P571 is sometimes a founding date, not the date of the standing building.
      - Some false matches: the 1903 Taj Mahal Palace hotel → Mughal; Sanchi → Nagara.
      - 60k candidates (minor temples, shrines, monasteries) are unassigned.
  - **Open item:** the unstyled list includes cities and natural sites (filter by instance-of).

### 2.4 Modern era pass (decided 2026-10-28)
**Periodisation:** *modern* runs from Impressionism (1860s–70s) to about 1960, and *contemporary* from the 1960s on (§3; contemporary pool = born ≥1920).
- **Calibration (decided 2026-10-28):** the Europe 1400–1900 reference is an *example of the depth wanted*, not a calibrator every era must be measured against. Each era is calibrated on its own reference: modern on a reference built from data (`build_modern_reference.py`: Wikidata movement membership, plus Wikipedia movement articles for non-Western movements that Wikidata leaves empty, ranked by Tate, MoMA (`Artists.json`; holdings yes/no only, since `Artworks.json` is not available), Wikidata collections and the regional sweeps), at 90% recall. Measured against that reference, the Europe model recovers only 63–80%. Pre-1400 passes get an era-own reference where Wikidata makes one cheap.
- **Placement fix:** Wikidata gives the Russian Empire's continents as North America (Alaska) and "Eurasia" (Q5401), which made North America its home continent and dropped every Russian-Empire artist (Shishkin, Roerich, Vereshchagin, Čiurlionis) from modern Europe. "Eurasia" is now read as Europe + Asia.
- **The gap it closes:** the Europe 1400–1900 pass only takes artists active by 1900 (born by about 1880), so artists born 1881–1919 were in neither pool. Picasso, Duchamp, Magritte, O'Keeffe, Kahlo, Rivera, Rothko, Pollock and Henry Moore were all missing.
- **The pass:** artists active **1860–1960**, all media, split into **nine world regions**, each ranked within its own medium × period cells so that every modernism is measured against its peers, not against Paris and New York.
  - The regions: Europe · North America · Latin America · East Asia · South Asia · Southeast Asia · Middle East, North Africa and Central Asia · Sub-Saharan Africa · Oceania (`regions.MODERN_REGIONS`; `exclude_countries` carves Mexico and the Caribbean out of North America, and North Africa out of Africa).
  - Examples of what this is meant to catch: Mexican muralism, the Bengal School and Indian modernism, *yōga*/*Nihonga*, Chinese modern ink painting, the Nsukka/Zaria schools.
- **Scoring:** until a modern reference exists, each region is scored with the model fitted on Europe 1400–1900.
- **Decided (2026-10-28): the modern reference list is built from data, not by hand.** It must avoid circularity, so it uses only signals the model does not use as features:
  - **movements as the skeleton:** Wikidata art movements active 1860–1960 and their members (P135/P463), including non-Western modernisms;
  - **within each movement, members ranked by works held at MoMA and Tate:** both CC0 collection datasets, and not model features. Regional collections stand in for movements those two museums under-cover;
  - **the reference is the top members of each movement**, scaled to movement size, mirroring the WikiArt-style lists.

  The Europe model's recall on this list is measured, and the model is refit if needed (`build_modern_reference.py`). The candidate list is reviewed before it goes into `seeds/visual-art/`.
- **Overlaps:** artists active 1860–1900 are also in the Europe 1400–1900 pass, and those born 1920–1940 are also in the contemporary pool. Selections are unioned by QID.
- **Runner:** `pipelines/visual_art/run_modern.sh`.
- **First run (2026-10-28):** 15,320 selected across the nine regions, before deduplication. The missing names are now in: Picasso, Magritte, Henry Moore, Duchamp, Kahlo, Rivera, Pollock, Rothko, O'Keeffe, Xu Beihong, Sadequain, M. F. Husain, Affandi, Siqueiros. Two fixes followed:
  - **Region assignment.** Wikidata lists imperial and transcontinental states on every continent they reached: France in South America and Oceania, the German Empire in Africa and Oceania, the Ottoman Empire in Africa. That put Gorky and Gibran into Sub-Saharan Africa and Max Ernst into Latin America. Modern regions now give each country a single home continent (`regions.HOME_CONTINENT_ORDER`). Explicit country lists still win.
  - **Incidental artists.** Writers, politicians and filmmakers with one art occupation, such as W. E. B. Du Bois, scored highly in thin regions. Every pool now carries `art_occ_share`, and selection multiplies the score by min(1, share/0.5) for non-reference artists, as for contemporary art. Tagore and other significant painter-writers can still pass on attention. The Europe 1400–1900 selection is re-run with the same factor; its coefficients are unchanged.
  - **Placement by birth and death country.** Secondary and honorary citizenships (Max Ernst: Cuba; Heinrich Kühn: Australia; Leni Riefenstahl: Sudan) put famous Europeans at the top of other regions' rankings. Modern regions now place an artist by where they were born or died (both count, so émigrés such as Gorky appear in both regions) and fall back to citizenship only when neither is known. Historical Egyptian states are added to North Africa. Birth or death place must also be matched by a citizenship from that region (when any citizenship is recorded). Without that check, colonial-era Europeans born or dying in colonies (Tolkien, Thackeray, Robert Capa, Jan Toorop, Yves Saint Laurent) took the top slots in the colonies' regions.
  - **Result after the fixes:** 12,840 distinct modern artists: Europe 9,701 · North America 2,038 · Latin America 459 · East Asia 362 · MENA/Central Asia 243 · Oceania 224 · South Asia 98 · Sub-Saharan Africa 73 · Southeast Asia 47. Sub-Saharan Africa is led by Seydou Keïta, Malick Sidibé, Irma Stern, Malangatana, Ernest Cole and Ousmane Sow. The smallest regions (Africa, South and Southeast Asia) are also covered by the tradition sweeps and the coverage audit.
  - After the first two fixes the Europe 1400–1900 selection is **9,973** (was 10,543), and the modern regions total about 14k before deduplication. Sub-Saharan Africa now leads with Irma Stern, Malangatana, Ousmane Sow and Seydou Keïta.

### 2.4b Pre-1400 named artists (measured 2026-10-28, `run_pre1400.sh`)
- **Passes:** `antiquity_mediterranean` (−800 to 500), `europe_medieval_500-1400` (incl. Byzantium, Armenia, Georgia), `east_asia_pre1400` (−200 to 1400) and `islamic_pre1400` (600–1400). Placement uses any of citizenship, birth or death country (`place_any`), because citizenships here are historical states. New medium: vase painting (vase painters and potters, including conventional names such as the Berlin Painter, typed as notname on Wikidata).
- **Pools:** 529 / 565 / 361 / 38. The Islamic pass is thin, and the Islamic regional sweep remains the main source there.
- **Europe model at its cutoff:** 394 selected (147 / 146 / 98 / 7). In: Giotto, Duccio, Cimabue, Simone Martini, the Pisani, Exekias, Euphronios, the Berlin and Amasis Painters, Phidias, Polykleitos, Praxiteles, Gu Kaizhi, Wu Daozi, Guo Xi, Unkei, al-Wasiti, Yaqut. Missing: Zhan Ziqian and Yi Nyeong (no dates on Wikidata), Kaikei (ranked as a painter), Villard de Honnecourt (architecture excluded).
- **Era-own reference** (153 members of pre-1400 schools and styles via P135): the Europe model recovers only 42%. An era model fitted on it barely discriminates (P135 tags workshop members as readily as masters) and would take about 80% of each pool (1,186).
- **Known noise:** the calligrapher occupation pulls in poets and emperors (Li Bai, Du Fu, Huizong); some vase "Groups" and "Classes" are typed as notname; primary medium takes painting before sculpture.

### 2.5 Getty vocabularies: dropped from this project (decided 2026-10-28)
Getty AAT/ULAN IDs are **not required**:
- Wikidata QIDs are the join key everywhere.
- ULAN already comes through Wikidata (P245) and is a model feature.
- The node hierarchy is built by clustering in the classifying stage. The AAT would at most be one input to it, and it is thin on many non-Western traditions.
- vocab.getty.edu refuses requests from cloud IPs.

The AAT columns in the tradition and architecture outputs stay empty. If the taxonomy is ever published or has to interoperate with museum systems, backfill them then: the matching code exists (`build_traditions.py` without `--no-aat`), run from a machine Getty does not block.

- **South/Southeast Asia, Africa, Americas/Oceania sweep** (`pipelines/regional/south_asia_africa_americas.py`; sources V&A, Cleveland, AIC and Rijksmuseum; British Museum unreachable):
  - **South and Southeast Asia: 35,645 objects (2.8% attributed).**
    - 58 recorded dynasties, e.g. Mughal 3,208, Company 2,583, Konbaung 299, Kushan 188, Pala 88, Angkorian 80+, Chola 46, Gupta 39, Pagan, Majapahit, Kandyan.
    - Painting schools down to court level: Rajput 1,456 (Jaipur, Mewar, Kota, Bundi, Kishangarh...), Pahari 564 (Kangra, Guler, Chamba...), Deccani, Kalighat.
    - Named masters under their schools: Nainsukh, Manaku, Basawan, La'l, Govardhan, Mola Ram, Chokha.
  - **Africa: 1,557 objects** (Asante, Yoruba, Ethiopian, Kuba, Zulu...; masters such as Olowe of Ise).
  - **Americas/Oceania: 3,732 objects** (Nasca, Moche, Maya, Chimu, Inca, Wari...; Pueblo potters 51% attributed). **Oceania has only 104.**
  - Africa and Oceania stay thin in these sources. The Met (about 12k objects in its Africa/Oceania/Americas cultures) and the Smithsonian NMAI remain the main sources there, and a targeted Africa and Oceania sweep is running.
  - Caveats: manuscripts count once per folio; 12k undated V&A records are not reachable through its API.

- **East Asia sweep** (`pipelines/regional/east_asia.py`): **205,989 objects, 10,350 artists, 804 tradition cells**. Sources:
  - ColBase 143k;
  - Japan's national designated-property register: 959 国宝 and 10,247 重要文化財;
  - National Palace Museum: 18k paintings, calligraphy works and fans item by item, plus 144k catalogue counts by dynasty × category;
  - e-Museum Korea: all 국보 and 보물, plus the National Museum of Korea's paintings;
  - Cleveland; AIC.

  Findings:
  - **Top artists by designated properties:** Kim Hong-do, Sesshū, Buson, Kōrin, Tōhaku, Ōkyo, Taiga; Japanese swordsmiths also rank high. **By objects:** Hiroshige, Hokusai, Utamaro, Dong Qichang, Wang Hui, Wen Zhengming, Shen Zhou.
  - **Attribution profile confirmed:** painting is artist-led (attributed share China 86%, Japan 56%, Korea 31%). Ceramics, sculpture and metalwork are tradition-led (1–7%; Japanese named potters are the exception).
  - **Thin cells for the audit:** Goguryeo, Balhae, Gaya and Korean Neolithic; Xin, Qin and Xi Xia.
  - **Unreachable:** NPM bulk dumps (connection reset; the other categories enter as counts only) and the Korea API (needs a data.go.kr key).

- **Africa/Oceania targeted sweep** (`pipelines/regional/africa_oceania_targeted.py`; Mia, Penn Museum bulk CSV, Te Papa, Yale LUX capped at the 5,300 cached items):
  - **Africa: 19,105 objects, 210 cultures** (was 1,557). **Oceania: 32,412 objects, 82 cultures** (was 104).
  - Of the 230 culture keys, 166 were already known from the Met, the Smithsonian or the earlier sweep. About 40–50 are genuinely new nodes: Aboriginal Australian schools (Arnhem Land, Western Desert, Kimberley, Tiwi, Arrernte), Māori iwi and Moriori, East African groups (Kikuyu, Kalenjin, Karamojong, Gurage), and Micronesia.
  - Unreachable: Auckland Museum (bot challenges, so stopped per the rules), Brooklyn (needs a key), quai Branly, NGA Australia, AGNSW (robots.txt blocks Claude).

**Decided (2026-10-28): gathering scope is nodes plus evidence, not object completeness.** The taxonomy lists traditions and artists, each with the collections and databases that hold their work and a few representative works. It does not list every object. Object-level harvesting only serves to:
1. discover nodes (traditions, schools, named makers) not yet captured;
2. measure prominence (object counts, number of holding institutions);
3. point to where the work lives.

**A source is complete once it stops adding nodes.** After that, aggregates are enough. Applied here: the Yale harvest was stopped at 5,300 of 23,030 items, since its holdings overlap known cultures.

### 2.2 Gathering exit criterion: coverage audit (decided 2026-10-28)
Node creation happens in the classifying stage. Gathering must hand it **evidence for every region at the level that region records**, so that no non-Western tradition drops out because it lacks artist names.
- **Grid:** before gathering closes, build a region × period audit grid. Per cell, it counts:
  - named artists (pool and selected);
  - tradition, school and style records (cultures, dynasties, schools from the Met/AIC harvest and the regional sweeps);
  - objects;
  - distinct sources;
  - the share of attributed objects (the attribution profile).
- **Flags:** cells that are empty, thin relative to their art-historical weight, or resting on a single source (especially the Met alone) are flagged.
- **Fix:** each flagged cell gets a targeted sweep before the handover to classifying.
- **Media inside a cell:** the grid is also split by medium (painting, sculpture, textiles and costume, ceramics, metalwork, woodwork, book arts, ...), so that a region is not counted as covered on the strength of its painting alone. This applies to Europe too: folk and vernacular traditions outside the Renaissance–Baroque–Rococo and academic line (embroidery and lace, folk painting such as rosemaling and lubok, regional icon schools, folk ceramics, woodcarving, costume) are tradition nodes in their own right and get their own sweep (`pipelines/regional/europe_folk.py`: Wikidata including UNESCO intangible-heritage crafts, Goskatalog, Finna, and the cached Met/AIC/V&A/Cleveland data).

### 2.3 Inclusion cutoffs (decided 2026-10-28)
- **Historical artists, artist-led cells:** the depth-model score at 90% reference recall, plus every reference artist (§2.1). Other regions reuse the fitted cutoff (`depth_model.py apply`).
- **Traditions, tradition-led cells:** a base-level culture or tradition with ≥50 objects OR any Met Heilbrunn Timeline work. Sub-traditions are kept as children. This gives 501 from the Met/AIC harvest. Each regional sweep uses the same rule, with the object threshold scaled to its collection size.
- **Architectural styles:** sitelinks ≥5 OR ≥3 heritage-listed buildings OR any UNESCO building. That gives 894, plus the styles from the non-Western pass. Sitelinks alone would leave Africa with 23 styles and South America with 10.
- **Contemporary artists:**
  - **Auto-include:** everyone on the 21 lists (1,530 pool artists, plus resolved and list-only artists).
  - **Everyone else:** a composite score ranked within the artist's region, with each region's cutoff set so the total is about 10–12k. Signals: pageviews, sitelinks, Artnet/Artsy/MoMA IDs, museum IDs and awards; Artfacts' planned weight moves to the museum and market IDs. `art_occ_share` down-weights celebrities.

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
  - The Met records no Period or Dynasty on Islamic Art objects, so the dynasty (Mamluk, Safavid, Timurid, Ottoman, ...) is inferred from culture plus date (`ISLAMIC_PERIODS`). **This is a stopgap (decided 2026-10-28).** The regional sweeps replace it with collections that record each region's own categories, and their labels override the Met-derived inference where they disagree. For the Islamic world: Smithsonian Open Access (incl. the National Museum of Asian Art), the V&A API, Harvard Art Museums, Discover Islamic Art (Museum With No Frontiers) and Cleveland's full artwork records. The same pattern applies to every region (ColBase and the National Palace Museum for East Asia, the V&A and the British Library for South Asia, ...).
  - Attic red-figure vs black-figure cannot be split: the Met CSV never records it.
- The Getty AAT mapping is not done; see §2.5 (Getty dropped from this project).

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

### 3.1b Candidate pool (measured 2026-10-28, `pipelines/contemporary_art/build_pool.py`)
- **Rule:** a person enters by either route:
  - *occupation rule:* any visual-art occupation, born ≥1920, sitelinks ≥3;
  - *market rule:* an Artnet, Artsy or MoMA ID plus an art occupation (sitelinks ≥1). The occupation requirement keeps out the subjects and celebrities those databases also index; film occupations are excluded.
  - Collectives are included when typed as artist collectives.
- **Pool: 48,269 artists**, 28,779 living. 38,161 come in by the occupation rule, 18,786 by the market rule (9,838 market-only).
  - By region: Europe 26,941 · North America 10,000 · Latin America 2,745 · East Asia 2,183 · MENA 2,096 · Sub-Saharan Africa 1,172 · Oceania 1,038 · South Asia 853 · Southeast Asia 406 · Central Asia 61 · unknown 697.
  - By primary medium: painting 18,899 · photography 7,523 · architecture 5,167 · sculpture 4,556 · design 3,623 · drawing 3,578 · installation, performance and conceptual 1,020 · new media 541 · street art 476.
- **Signals:**
  - Artnet 13,024, Artsy 8,048, MoMA 5,945 (18,875 have at least one); ULAN 14,919; museum IDs 10,912; awards (P166) 13,674.
  - Too thin to use: gallery representation (P1875, 1,867) and exhibition history (P608, 70).
- **Canon lists** (`pipelines/contemporary_art/canon_lists.py`): 6,304 entries and 3,582 distinct names across 21 lists:
  - Kunstkompass 2001–2025 (only the top 10 is public);
  - ArtReview Power 100 2019–2025 (artists flagged);
  - Artprice Top 500 2023–2026 and ultra-contemporary Top 100;
  - biennials from organisers' announcements: Venice 2015–2026, documenta 14/15, Sharjah 14–17, São Paulo 35–36, Gwangju 15–16, Kochi-Muziris, Istanbul 18, Dak'Art 15. Universes in Universe's robots.txt disallows Claude's crawlers, so it was not used;
  - prizes: Turner, Hugo Boss, Praemium Imperiale, Duchamp, Venice Lions, Future Generation, Prince Claus, Jameel.
  - Not available: the Kunstkompass top 100, and the Asia Pacific Triennial (403).
  - **1,530 pool artists are on at least one list.**
  - **The unmatched rate is highest for non-Western lists** (Dak'Art 53/58, Istanbul 35/47, Kochi 46/66, Jameel 29/47, Sharjah 300/483), which is Wikidata's bias showing through. Unmatched list artists are resolved without pool filters, and any still unresolved stay in as **list-only candidates** carried by the list (auto-include rule) (`resolve_list_artists.py`).
- **Caveats for scoring:**
  - `art_occ_share` (art occupations ÷ all occupations) is needed: celebrities who also paint or design (Bowie, George W. Bush) are in the pool on occupation.
  - Wikidata currently gives Yayoi Kusama a 2026 death date. Check it before relying on `living`.
  - **Modern architects (5,167 in the pool) stay in as gathered.** Whether they are treated as artists or placed under architectural styles is decided in the classifying/clustering stage (decided 2026-10-28).
### 3.1c Selection (measured 2026-10-28, `pipelines/contemporary_art/score.py`)
- **11,000 artists:** 3,232 auto-included from the 21 lists, plus 7,768 picked by score within each region.
- **Score:** within-region mid-rank percentiles of museum IDs and ULAN (0.30), market IDs (Artnet, Artsy, Artprice, MutualArt; 0.20), lists (0.20), pageviews (0.10), sitelinks (0.10) and awards (0.10), times a celebrity factor min(1, art_occ_share/0.5). Bowie, Bush and Dylan drop out; Yoko Ono stays via her Golden Lion.
- **Cutoff:** one selection fraction for every region (0.199), counting each region's auto-includes against its share, with every non-Western region guaranteed at least its top 25%.
- **Selected by region:**

  | Region | Selected |
  |---|---|
  | Europe | 5,401 |
  | North America | 2,007 |
  | Latin America | 721 |
  | East Asia | 574 |
  | MENA | 541 |
  | Sub-Saharan Africa | 307 |
  | South Asia | 220 |
  | Oceania | 212 |
  | Southeast Asia | 111 |
  | Central Asia | 16 |

  Plus about 810 list-only names, most of them with no region yet.
- **List resolution** (`resolve_list_artists.py`): 1,003 previously unmatched list artists were resolved, roughly doubling each non-Western region's matched list artists. 685 stay list-only (Wikidata has no item for most of them). Wikidata's public query service was in an outage that rate-limited to 1 request a minute, so lookups ran on the QLever Wikidata mirror (`--endpoint`). List artists born before 1920 (e.g. Venice 2024's historical section: Kahlo, Lam) are left to the modern pass. Selection re-run: 11,000 (3,075 auto-includes + 7,925 regional picks).
- **Fixes:**
  - 104 list artists resolved to Wikidata people with no art occupation (a poet, a researcher, Franz Boas) are kept as list-only names, not under the wrong QID.
  - Consumer categories that the metrics under-count (§3.4) get hand-curated includes in `seeds/visual-art/contemporary_manual_includes.csv`, starting with Beeple; add others as review finds them.

### 3.1d Fixes to the selection (decided 2026-10-28, in progress)
- **Movement guarantee:** every post-1945 art movement with at least 3 pool members keeps its top members by holdings (max(3, 15% of members), capped at 15), so movements whose members are individually modest (Mono-ha, Dansaekhwa, Neo-Concretism, Political Pop, Black Arts Movement, Superflat, ...) are not reduced to one or two names.
- **Attention route:** the top 2% of each region by pageviews are included when they are primarily artists (art_occ_share ≥ 0.5). This catches cult and popular artists that museum signals under-count (lowbrow, fantasy illustration, street art).
- **Market-record check:** an Artnet/Artsy/Artprice/MutualArt record counts only with at least one independent signal (museum, ULAN/Tate/MoMA, list, award, 5+ sitelinks or above-median regional pageviews), against vanity and minor-auction listings.
- **Modern cutoff:** chosen after reviewing samples of the marginal artists at 80%, 85% and 90% reference recall, so the modern pass does not drift into "everyone who painted".
- **Pre-1400 (decided):** the era-model selection (about 1,190 of 1,500) is taken, cleaned of literati with no art holdings, vase "Groups" and "Classes" (kept as workshop evidence), and with sculpture ranked before painting.

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
