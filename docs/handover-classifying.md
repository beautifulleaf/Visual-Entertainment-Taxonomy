# Handover: gathering → classifying

Written 2026-10-28, when gathering closed. This is the inventory for the classifying session. Read it with [classifying-plan.md](classifying-plan.md) (method and conventions), [visual-art-plan.md](visual-art-plan.md) (Visual Art sources and decisions) and [sourcing-plan.md](sourcing-plan.md) §8 (Film & TV cutoffs). Row counts are data rows, excluding the header.

## 0. Getting the data into the new session

**`data/` is gitignored, so a fresh cloud session has no `data/interim/` and no `data/raw/`.** Every input below lives in `data/interim/`.

| What | Size | Needed for |
|---|---|---|
| `data/interim/` | 615 MB on disk, **90 MB as .tar.gz** (measured) | all classifying inputs |
| `data/raw/museums/MetObjects.csv` | 326 MB | only for re-running `coverage_audit.py`; classifying itself does not need it |
| `data/raw/` (everything) | 16 GB | regeneration only |

**Recommendation: transfer `data/interim/` as one archive. Do not regenerate it.** At 90 MB compressed it is far under the ~1.5 GB limit. The parent session should arrange the transfer, for example `tar czf interim.tgz -C data interim` here and `tar xzf interim.tgz -C data` there, or a release asset or private bucket. Add `MetObjects.csv` (about 60–70 MB gzipped) only if the classifying session needs to re-run the audit. After unpacking, check the row counts against the tables below.

**Regeneration from scratch is a last resort.** It needs the 16 GB of raw downloads (IMDb dumps, 5.9 GB of Wikimedia pageview dumps, 3.1 GB of museum dumps, 3.9 GB of regional harvests), API keys (`MDBLIST_API_KEY`; optional `EUROPEANA_API_KEY`), and live access to rate-limited services (Wikidata SPARQL, which was in a 1-request-a-minute outage on 2026-10-28; MDL at 1–1.5 s a request; MDBList). In order:

| Step | Commands (run from repo root) | Rough time with an empty cache |
|---|---|---|
| Film | `film/build_candidates.py` → `film/mdblist_enrich.py` → `film/canon_lists.py` → `film/letterboxd_sample.py` → `film/underrepresented_countries.py` | IMDb download + ~10 min MDBList; Wikidata by country: hours |
| TV | `tv/build_candidates.py` → `tv/mdblist_enrich.py` → `tv/route.py` → `tv/awards.py` | ~30 min plus Wikipedia/Wikidata |
| Anime | `anime/build_candidates.py` → `anime/popularity.py` | ~1 h (MAL ranking walk, AniList) |
| Asian drama | `asian_drama/build_candidates.py` → `asian_drama/mdl_fetch.py` → `asian_drama/topup_pools.py` → `asian_drama/match_awards.py` → `asian_drama/select.py` | MDL ~3 h for 5,000 pages, plus pools |
| Unscripted | `unscripted/build_formats.py` | Wikidata, < 1 h |
| Visual art, artists | `visual_art/build_pool.py --region europe_1400-1900`, `museum_holdings.py`, `pageviews.py`, `depth_model.py`; `bash visual_art/run_modern.sh`; `bash visual_art/run_pre1400.sh`; `build_modern_reference.py`, `fit_modern.py` | Wikidata pools: several hours; pageview dumps: hours |
| Contemporary | `contemporary_art/build_pool.py` → `canon_lists.py` → `resolve_list_artists.py` → `score.py` | hours (Wikidata/QLever) |
| Traditions | `unattributed/build_traditions.py --no-aat`; `regional/*.py` (smithsonian, himalaya_central_asia, islamic_world, south_asia_africa_americas, africa_oceania_targeted, east_asia, world_cultures_extra, europe_folk, gap_sweep, world_folk); `manuscripts/build_traditions.py`; `in_situ/build_traditions.py`; `architecture/build_styles.py` → `architecture/nonwestern_exemplars.py` | museum dumps and APIs: many hours (Goskatalog alone reads 6.1M records) |
| Audit | `visual_art/coverage_audit.py` | ~1 min |

All commands are `python3 pipelines/<path>`. Expect a day or more in total, with risk from services that block cloud IPs (IDP, Auckland Museum, the NPM dumps).

## 1. What is final and what is not

| Tab | Database | Status | Size |
|---|---|---|---|
| Visual Art | Europe 1400–1900 artists | **FINAL SELECTION** (`selected`) | 9,973 |
| | Modern 1860–1960 artists (9 regions) | **FINAL SELECTION** (`selected`) | 17,706 |
| | Pre-1400 artists (4 passes) | **FINAL SELECTION** (`final` in `scores_*_era.csv`) | 1,166 |
| | Contemporary artists | **FINAL SELECTION** (`selected = 1`) | 11,125 (incl. 790 with no QID: 685 list-only + 105 list-only after a wrong match) |
| | All artists, unioned by QID | union of the above | **30,761 QIDs + 790 list-only names** (overlaps: Europe∩modern 5,306, modern∩contemporary 2,516, Europe∩pre-1400 45) |
| | Tradition, school, style and folk nodes | **CANDIDATE POOLS** with inclusion rules (§2.3 of the plan), not yet cut | see §2.2 |
| | Architecture styles | candidate pool; cutoff rule decided (sitelinks ≥5 OR ≥3 heritage buildings OR any UNESCO) → 894 + 146 non-Western | §2.3 |
| Film & TV | Asian drama | **FINAL SELECTION** (`asian_drama_selected.csv`) | 5,268 |
| | Unscripted formats | **FINAL SELECTION** (`unscripted_formats.csv`, `kind = unscripted`) | 211 formats (+254 scripted remake families) |
| | Film | **RULES DECIDED, SELECTION NOT MATERIALISED** | ~19k expected |
| | Scripted TV | **RULES DECIDED, SELECTION NOT MATERIALISED** | ~7,100 expected |
| | Anime | **RULES DECIDED, SELECTION NOT MATERIALISED** | ~5,500 expected |

**First task for classifying:** write a small `select` step for film, scripted TV and anime that applies sourcing-plan §8 to the files listed in §3. The counts quoted there were measured ad hoc and no script writes them out. For the visual-art tradition pools, apply the §2.3 inclusion rule as part of seeding leaves.

## 2. Visual Art inputs

Join key everywhere: Wikidata QID. Region × era grid: 20 regions × antiquity (<500) / traditional (500–1859) / modern (1860–1959) / contemporary (≥1960).

### 2.1 Artists (kinds under artist-led leaves)

| File | Rows | Row is | Key columns | Selection |
|---|---|---|---|---|
| `visual_art/scores_europe_1400-1900.csv` | 41,453 | pool artist with model score | qid, label, birth, medium, cell, is_reference, art_occ_share, score, **selected** | 9,973 selected (90% reference recall + all reference artists; architecture excluded) |
| `visual_art/pool_europe_1400-1900.csv` | 41,473 | pool artist with Wikidata facts | qid, countries (QIDs), media, movements, genres, ulan_id, authority_ids | evidence for the above |
| `visual_art/scores_modern_<region>.csv` (9) | 59,957 | modern pool artist with score | as above + manual_include, **dropped_by_guard** | 17,706 selected (80% recall + Europe guard + manual includes) |
| `visual_art/pool_modern_<region>.csv` (9) | 59,957 | modern pool facts | countries, media, movements | evidence |
| `visual_art/scores_<pass>_era.csv` (4: antiquity_mediterranean, europe_medieval_500-1400, east_asia_pre1400, islamic_pre1400) | 1,495 | pre-1400 pool artist, era model | **final**, note, cell, medium | 1,166 final (460 / 443 / 247 / 16) |
| `contemporary_scores.csv` | 49,782 | contemporary candidate (pool, addition, list-only) | key, qid, region, medium, score, **selected**, routes, auto_include, guarantee_movements, source | 11,125 selected |
| `contemporary_pool.csv` (+ `_additions`, 985) | 48,269 | pool facts | countries, media, art_occ_share, museum/market IDs, awards, lists | evidence |
| `contemporary_list_artists.csv` | 3,184 | canon-list name and its resolution | name, lists, qid, status, country, region | evidence; list-only names carry country here |
| `contemporary_movements.csv` | 797 | post-1945 movement and its guarantee | movement, kept, guaranteed_members | movement leaves for contemporary |
| `modern_reference_candidate.csv` / `modern_reference_movements.csv` | 1,934 / 1,708 | modern reference member / movement | movement, region, rank_in_movement | movement leaves for modern |
| `depth_reference_matched.csv` | 910 | Europe 1400–1900 reference name → QID | movement, name, qid | movement leaves for 1400–1900 |
| `visual_art/holdings.csv`, `pageviews.csv` | 75,031 / 82,789 | per-QID evidence | met/aic/cma objects, timeline works; views | evidence |
| `regional/east_asia_artists.csv` | 10,349 | named maker in East Asian museums | artist_key, romanised name, country, periods, designated_total | **named makers, not a selection** (kinds under schools) |
| `regional/islamic_makers.csv` | 616 | named maker | maker, dynasties, school | makers under schools |
| `regional/*_makers.csv` (africa 19, americas_oceania 37, south_southeast_asia 385, africa_oceania_targeted 417, himalaya_central_asia 41) | 899 | named maker | maker, traditions, dates | makers under traditions |
| `manuscripts_illuminators.csv` | 911 | named illuminator | qid, tradition, region, floruit_est | makers under manuscript traditions |
| `architecture_architects.csv` | 2,688 | architect of exemplar buildings | qid, styles, buildings | hang under styles |

Caveats:
- Pre-1400: the calligrapher occupation pulled in poets and emperors (Li Bai, Du Fu, Huizong); some vase "Groups"/"Classes" are typed as notname (kept as workshop evidence in `pre1400_workshop_groups.csv`). Zhan Ziqian and Yi Nyeong are missing (no dates); Kaikei is ranked as a painter.
- Modern: Russian-Empire, imperial-state and secondary-citizenship placement fixes are applied. Countries in pools are QIDs, and émigrés can appear in two regions. 8 reference artists with no usable placement are in `seeds/visual-art/modern_manual_includes.csv`.
- Contemporary: modern architects (5,167 in the pool) are kept as gathered; decide in classifying whether they are artists or go under styles. Wikidata gives Kusama a 2026 death date. 104 list artists resolved to non-artists were kept as list-only names. One QID is in both the contemporary and pre-1400 selections (a wrong match).
- Architecture is not selected by the artist model (decided). Architects hang under styles.
- **Aboriginal Australian artists cannot be told apart from settler Australians by country**, so all Australian modern and contemporary artists sit in Oceania (Pacific) in the audit. Place them by tradition (gap sweep art centres) in classifying.

### 2.2 Tradition nodes (leaves for tradition-led cells)

All are candidate pools. Inclusion rule (§2.3): base-level culture/tradition with ≥50 objects OR any Met Timeline work, threshold scaled to collection size; sub-traditions as children.

| File | Rows | Row is | Key columns | Notes and noise |
|---|---|---|---|---|
| `unattributed_cultures.csv` | 5,493 | Met (+AIC counts) culture (4,329), culture×period (822), period (342) | key, label, parent, objects, timeline_works, begin/end_median, dominant_department | ≥50 objects or Timeline → 501 cultures. Islamic dynasties are inferred (stopgap); regional labels override. Attic red- vs black-figure not split |
| `unattributed_object_traditions.csv` | 8,895 | culture × classification / technique | culture, classification, technique, objects | object-tradition (ware) nodes: blue-and-white, celadon, lustreware |
| `regional/smithsonian_cultures.csv` | 5,708 | Smithsonian culture / period (NMAI 4,981) | unit, kind, culture, objects, begin_median | strongest source for the Indigenous Americas |
| `regional/africa_traditions.csv`, `americas_oceania_traditions.csv`, `south_southeast_asia_traditions.csv` | 1,449 / 1,794 / 4,558 | culture, culture×period×type rows | kind, culture, culture_group, period, objects, attributed_share, named_makers | V&A/Cleveland/AIC/Rijks. Manuscripts count once per folio; 12k undated V&A records not reachable |
| `regional/africa_oceania_targeted_traditions.csv` | 4,851 | same layout, Mia/Penn/Te Papa/Yale | region, culture, objects | ~40–50 genuinely new nodes; Yale capped at 5,300 |
| `regional/east_asia_traditions.csv` | 802 | country × period × object type | all_objects, attributed_share, top_kilns_workshops | painting artist-led, ceramics/sculpture/metalwork tradition-led; NPM categories as counts only; Korean labels partly untranslated |
| `regional/himalaya_central_asia_traditions.csv` | 1,012 | **71 final traditions** + tradition×period (296) + ×type (645) | tradition, period, medium, objects, attributed_share | 34% of HAR items have no period; IDP Berlin mirror only |
| `regional/islamic_dynasties.csv` / `islamic_schools.csv` | 53 / 94 (51 schools, 43 centres) | dynasty / school or production centre | objects, attributed_share, named_makers, conflict_inferred_as | school detection is regex-based; Persian schools thin; no cross-source dedup |
| `regional/world_extra_cultures.csv` | 871 | Rijksmuseum/Wereldmuseum culture key | kind, level (base/sub), region, objects, **is_new** (445 new), gained_institution | `kind = place` rows (163) are country buckets, not traditions |
| `regional/europe_folk_traditions.csv` | 2,369 | European folk/vernacular node | kind (wikidata, people_medium, culture_medium, pattern, technique), region, medium, total_objects, ich/heritage designation, is_new_node | Wikidata noise (trades, single artworks) left in; thin for Luxembourg, Iceland, Kosovo and the small Balkan states |
| `regional/world_folk_traditions.csv` | see §2.6 | non-European folk node | kind, region, country, people, medium, **status** (new / known / alias-of-existing-cell), total_objects_distinct | finished 2026-10-28 (§2.6); alias rows duplicate an existing cell |
| `regional/gap_sweep_traditions.csv` | 250 | seed node (150), Wikidata ICH (79), art centre (17) | area, label, region, medium, objects, attributed_share, top_named_makers, new_vs_known | "no evidence anywhere" nodes kept (enconchado, biombos, Igbo-Ukwu, Mapungubwe ...); top makers include European print sources for colonial nodes |
| `manuscripts_traditions.csv` | 200 | manuscript tradition (125 style, 57 unlinked Wikidata styles, 18 genres) | label, qid, region, n_manuscripts, n_illuminated, gap | 85% of 122,463 items placed; thin: Armenian schools, Pala, Odia, Goryeo sutras, Aztec, Bohemian Gothic. Rules in `manuscripts_rules.csv` |
| `in_situ_traditions.csv` | 680 | art-in-place node: 198 by rule, 221 fallback "kind – country", 260 unmapped Wikidata items | label, kind, region, n_sites, n_unesco, node_source | **the 260 unmapped Wikidata items are noise** (medical "mosaic trisomy", "photo mural"); Western Europe inflated by ~18,900 Swedish rock-art records |

### 2.3 Architecture (family "architecture", leaves = styles)

| File | Rows | Row is | Notes |
|---|---|---|---|
| `architecture_styles.csv` | 2,412 | Wikidata style item | Western-biased tags; 617 zero-sitelink "… architecture style" bulk items (judge, don't count); AAT links on 259 only |
| `architecture_exemplars.csv` | 14,245 | exemplar building (≤15 per style, tiered) | plus 5,992 UNESCO items with no style; the unstyled list includes cities and natural sites |
| `architecture_nonwestern_styles.csv` / `_exemplars.csv` / `_rules.csv` | 146 / 80,771 / 204 | proposed style / candidate building / rule | 20,283 assigned; 60k unassigned; Dravidian sub-periods thin (98 dated temples of ~16k); false matches (1903 Taj Mahal Palace hotel → Mughal; Sanchi → Nagara); 15 wrong existing P149 tags flagged. **Review the rules before anything goes into `seeds/`** |

### 2.4 Evidence (objects; not nodes)
`regional/*_objects.csv` (East Asia 205,989; Smithsonian 315,019; Rijks/Wereldmuseum 503,190; Islamic 21,086; Himalaya 11,997; south/southeast Asia 35,645; Africa/Oceania targeted 51,517; Africa 1,557; Americas/Oceania 3,732; gap sweep 13,579; Europe folk 31,742; world folk, §2.6), `manuscripts_items.csv` (122,463), `in_situ_exemplars.csv` (35,261). Use them for representative works (3–10 per node), holding institutions and prominence, never as items to place. `*_sources.csv` and `*_dropped.csv` are logs.

### 2.5 Seeds (in git)
`seeds/visual-art/`: depth references (`europe_1400-1900_depth_reference.txt`, `modern_1860-1960_depth_reference.txt`), manual includes and excludes (modern, pre-1400, contemporary), `depth_reference_overrides.csv`, and **`attribution_profile.csv`** (new, §5).

### 2.6 World folk pass (closed 2026-10-28)
WORLD_FOLK_PLACEHOLDER

## 3. Film & Television inputs

| File | Rows | Row is | Key columns | Status / rule |
|---|---|---|---|---|
| `film_candidates.csv` | 84,993 | IMDb film-like title ≥500 votes | tconst, title_type, year, genres, imdb_votes | candidate pool |
| `film_ratings.csv` | 83,332 | MDBList enrichment | letterboxd_votes, country (ISO-2), imdb/mdblist genres, tmdb_id | **15,150 have Letterboxd ≥10k (main bar)** |
| `film_candidates_extra.csv` | 26,471 | extra candidates for 146 under-covered countries | same + source, target_country, wikidata | regional top-up with Letterboxd floor 100 |
| `film_canon.csv` | 5,913 | (list, film) | list, tconst, match_method | 3,839 distinct films; canon route |
| `film_letterboxd_estimates.csv` | 11,500 | gap film, sample estimate | estimated_letterboxd_votes | 32 at ≥10k are included (doc says 34); *Man* (2012) needs a hand check; 28 high-IMDb gaps are for manual review |
| `film_country_reattribution.csv` | 1,699 | film whose Wikidata P495 differs from MDBList country | wikidata_countries | P495 wins for the regional rule; **review 108 South Africa reattributions** (*Chappie*, *Dredd*) |
| `tv_candidates.csv` / `tv_ratings.csv` | 43,676 | IMDb series ≥100 votes / MDBList enrichment | episodes, country, genres | pool |
| `tv_routed.csv` | 43,676 | series routed to a database | **database** (scripted_tv 32,520, unscripted 4,249, asian_drama 3,768, anime 3,139), **serial_tradition** (1,102) | scripted ≥2,500 IMDb votes = 6,342; +5% regional top-up (+502); +award winners (+296) |
| `tv_awards.csv` | 5,533 | award row | won, tconst, qid, match | ~460 winners without IMDb ID (Chinese/Taiwanese/older Korean) |
| `anime_candidates.csv` / `anime_popularity.csv` | 38,270 | anime-offline-database entry / MAL + AniList popularity | mal_members, type, year, genres, top_tags, country_of_origin | MAL ≥25k = 5,167; + pre-2000 top 20% per decade (+271); donghua MAL ≥10k (146) |
| `asian_drama_selected.csv` | 5,268 | **final drama** | mdl_id, country, year, watchers, reasons, awards | KR 1,614 · JP 1,465 · CN 1,135 · TH 545 · TW 230 · PH 148 · HK 127 · SG 4 |
| `asian_unscripted_mdl.csv` | 212 | MDL variety show | | goes to unscripted, not drama |
| `asian_drama_mdl.csv`, `_mdl_pools.csv`, `_candidates.csv`, `_awards.csv` | 5,000 / 3,967 / 4,589 / 1,364 | ranking / top-up pools / IMDb–Wikidata cross-reference / award rows | | evidence |
| `unscripted_formats.csv` | 465 | format family | kind (unscripted 211, scripted 254), cluster, n_versions, members | **211 unscripted formats final**; scripted remake families feed scripted TV; a few Japanese broadcast slots slip in |
| `unscripted_adaptations.csv` | 3,143 | national version | format_qid, country, tconst | kinds/evidence under formats |

**Gap still open (classifying-plan.md):** genre placement needs content features: TMDB keywords (check MDBList first), Wikidata genre/based-on/director links, and short plot summaries from the Wikipedia dumps. These are not gathered.
Licensing: audience counts (Letterboxd via MDBList, MAL, MDL, IMDb) stay internal; publish only derived categories and IDs.

## 4. Coverage audit (visual-art-plan.md §2.2)
`python3 pipelines/visual_art/coverage_audit.py` → `data/interim/coverage_grid.csv` (region × era: traditions, objects, artists, makers, attributed_share, sources), `coverage_media.csv` (region × medium: tradition nodes, objects, cultures, sources), `coverage_flags.csv`.

FLAGS_PLACEHOLDER

## 5. Attribution profile (decides the primary node type per cell)
`data/interim/attribution_profile.csv` (full) and `seeds/visual-art/attribution_profile.csv` (region, era, profile, attributed_share, n_traditions, n_artists, rule_basis). Eras: the four grid eras plus `traditional:500-1399` and `traditional:1400-1859`. **Use the split rows for the traditional era**, because the 1400 boundary separates medieval from post-1400 practice.

**Rule:** attributed share = objects with a named maker ÷ objects with attribution information, from the object-level files (Met, Smithsonian incl. SAAM, the regional sweeps, East Asia, Islamic, Himalaya, Rijks/Wereldmuseum, gap sweep), used when ≥200 objects. Share < 15% → tradition-led; share > 50% → artist-led. Otherwise (15–50%, or not measured) the node balance decides: traditions ≥ 3× named artists → tradition-led; named artists (selected + named makers) ≥ 3× traditions → artist-led; else mixed. Structural cells → n/a.

PROFILE_PLACEHOLDER
