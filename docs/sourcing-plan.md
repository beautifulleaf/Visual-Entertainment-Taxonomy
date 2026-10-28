# Sourcing plan: metrics and harvest sources

Status: proposal (2026-10-27). Numbers marked *measured* were computed on that date; everything else is a recommendation to be confirmed.

## 0. Cross-cutting decisions

- **Wikidata QID is the universal join key.** Wikidata already carries cross-IDs for every source below:
  IMDb (P345), TMDB movie/TV (P4947/P4983), Letterboxd (P6127, ~273k films linked, *measured*),
  MyAnimeList (P4086), AniList (P8729), MyDramaList (P3868), Douban film/drama (P4529/P6443),
  ULAN (P245), WikiArt (P6002), Artfacts (P13700, sparse: 257), Art UK (P1367), Artsy (P2042), Artnet (P3782), MoMA (P2174).
- **Prominence thresholds are relative to the region and period, not global.** One global cutoff reproduces the Anglophone/Western bias of whatever platform measures it. Each region and period bucket gets its own percentile cutoff, with a global floor.
- **The inclusion rule is a union of signals (an OR).** A title or artist enters if *any* qualifying signal passes: audience count, canon list, institutional presence, or multilingual Wikipedia presence. That keeps cult and niche work without a long tail.

## 1. Traditional visual art (ancient to contemporary, worldwide)

See **[visual-art-plan.md](visual-art-plan.md)** for the full deep dive. Summary:
- Region × period grid (Met Heilbrunn Timeline + Getty AAT), with culture or workshop nodes for unattributed work.
- Historical metric: Wikidata sitelinks plus museum presence, thresholded per region and period.
- Living and contemporary: a composite of Artfacts rank, biennial participation, museum collections, consumer attention (pageviews), market (Artprice) and prizes/galleries, normalised within each region.
- Do not build on the Artsy public API (being retired).

## 2. Film

### Target metric: Letterboxd ≥10k ratings. Can we get it?
- **Official API:** application-only, and it explicitly excludes data analysis and recommendation projects. The API *does* expose per-film `ratings`/`watches`/`fans`/`lists` counts, but access is not realistic.
- **Site scraping:** blocked by Cloudflare challenges from datacenter IPs (*measured*), and against the ToS. Commercial Apify actors exist that return `ratingsCount` through residential proxies. This is a legal and ToS risk.
- **Public datasets: none carries per-film total rating counts.** The best available are *user samples*:
  | Dataset | Size | Date | Notes |
  |---|---|---|---|
  | Kaggle `tliocastro/letterboxd-sample-apr-2026` | 20.2M interactions + diary + follows | crawl Apr 2026 | includes IMDb `tconst` mapping; CC BY-NC |
  | HF `titouann/letterboxd-10m-movies-ratings-2025` | 10.46M ratings, 6,519 users, 281k films | Dec 2025 | CC BY-NC-SA |
  | Kaggle `freeth/letterboxd-film-ratings` | 18M ratings, 11k users | Oct 2023 | older |
  | HF `pkchwy` / `PratikDhonde/letterboxd-all-movie-data` | 847k films, avg rating + top reviews | 2025 | no counts; useful for slug and metadata |
  | Kaggle `gsimonx37/letterboxd` | 950k+ films, metadata | — | no counts |

### Solution: MDBList API (recommended primary source for Letterboxd rating counts)
MDBList (mdblist.com) aggregates ratings from IMDb, TMDB, Trakt, Letterboxd, RT, Metacritic and MAL. Each entry in its `ratings` array includes **`votes`**. For Letterboxd, `votes` is the **number of ratings**, e.g. `{"source":"letterboxd","value":3.5,"score":70,"votes":354165}`. That is exactly the "10k+ ratings" metric.
- Free API key; **batch "Media Info" endpoint takes up to 200 IMDb/TMDB IDs per request**; lists can be sorted by `lettervotes`.
- Limits: free = 1,000 requests/day; €3/month supporter = 100,000/day; every tier is also capped at 1,000 reads per 5 minutes. A full pass over the 85k candidates is 425 batch calls, about 10 minutes (*measured*). Our key's limit is 25,000 requests a day.
- MDBList refreshes Letterboxd numbers itself; use its `updates` endpoint for incremental sync.
- Caveat: MDBList obtains this from Letterboxd. We consume a public third-party API rather than scraping, but the counts remain Letterboxd's data, so keep them internal (see §7).

### Pipeline
1. **Candidate set:** IMDb film-like titles with numVotes ≥ 500 (84,993, *measured*; `pipelines/film/build_candidates.py`), unioned with TMDB films with vote_count ≥ ~50 and with every film on the canon lists below. The union catches titles that are under-voted on IMDb but logged on Letterboxd (arthouse, non-English, shorts).
2. **Enrich via MDBList batch:** get `letterboxd.votes` per film.
3. **Include if** `letterboxd.votes ≥ 10,000` **OR** a canon/curation hit **OR** the regional-percentile rule (top-N by Letterboxd votes per country and decade, so that Nigerian, Indonesian or Iranian cinema is not cut).
4. **Gaps (decided 2026-10-28).** On the 73,493 films with both counts, log IMDb votes and log Letterboxd ratings correlate at 0.85. The share reaching ≥10k Letterboxd by IMDb votes: 500–1k 0.9% · 1k–2k 2.7% · 2k–5k 9.6% · 5k–10k 31% · 10k–20k 59% · 20k–50k 89% · 50k+ 99.5%. Of the 11,500 candidates with no Letterboxd figure, about 11,250 have under 5k IMDb votes and are near-certainly below 10k.
   **High IMDb votes plus no Letterboxd figure is itself a red flag.** The 33 gap films at ≥20k IMDb votes are mostly DVD featurettes (*Attack of the Clones: Deleted Scenes*, *HBO First Look*), fan films, audiobook videos, streamer clips, and Indian titles with brigaded IMDb votes; the sample puts *Dam999* at ~240 Letterboxd ratings and *Checkmate* at ~125. So they are **not** auto-included.
   The deciding signal is the Letterboxd user sample (`pipelines/film/letterboxd_sample.py`): HF `titouann/letterboxd-10m-movies-ratings-2025`, 10.46M ratings from 6,519 users, joined by Letterboxd slug.
   - Calibration: log10(LB) = 2.098 + 0.956·log10(sample users), R² 0.79, so 10k Letterboxd ≈ 98 sample users. As a cutoff it gets about 84% of calls right in both directions; the estimate is good to about ×2 and under-estimates blockbusters.
   - Coverage: 6,422 of the 11,500 gaps get an estimate.
   - **Included: the 34 with an estimate ≥10k.** These are mostly cult shorts and videos MDBList never returned (*Save Ralph*, the Grindhouse fake trailers, Ari Aster's *Beau*, *Sallie Gardner at a Gallop*). *Man* (2012), matched on the generic slug `man`, needs a hand check.
   - **Manual review:** the 28 gaps with ≥20k IMDb votes and no estimate.
   - Canon films among the gaps enter through canon anyway.
   - Indian films are thin in the sample (*Kaiva* has no raters), so Indian titles rely on the regional rule.

Canon/curation lists: Sight and Sound 2022, TSPDT 1000 and 21st-century 1000, the Criterion Collection, national film registries, top prizes at major festivals.
*Measured (2026-10-28, `pipelines/film/canon_lists.py`):* **3,839 distinct films** are on at least one canon list. **About 1,500 of them are not already in through Letterboxd ≥10k**: about 1,100 are candidates under 10k ratings, and about 400 are not film candidates at all (mostly shorts and titles under 500 IMDb votes).

| List | Source | Entries | Matched |
|---|---|---|---|
| Sight and Sound 2022 critics (full 264) / directors (104) | JSON in the BFI pages | 368 | 99% |
| TSPDT 1000 / 21st-century 1000 | theyshootpictures.com | 2,000 | 99.6% |
| Criterion (+ Eclipse) | Wikipedia list (criterion.com returns 403) | 2,183 | 96% |
| Palme d'Or, Golden Lion, Golden Bear | Wikipedia | 261 | 99% |
| Oscar Best Picture / International Feature | Wikipedia | 176 | 99% |
| US National Film Registry | Wikipedia | 925 | 96% |

Matching runs locally against the IMDb datasets (title, alternative titles, year ±1–2), with director confirmation where the source names one. Hand fixes go in `seeds/film/canon_overrides.csv`. The ~150 unmatched rows are mostly non-features (box-set extras, registry home movies), plus a few real misses where IMDb's year differs by 2+ (*Aguirre*, *Partie de campagne*, *Out 1*).

*Measured IMDb counts (movies):* ≥1k votes = 49,392 · ≥2.5k = 29,175 · ≥5k = 19,221 · ≥10k = 12,657.
*Measured Letterboxd 10M-sample (films logged by ≥N of 6,519 users):* ≥20 = 41,960 · ≥50 = 23,586 · ≥100 = 15,129.
*Measured, first MDBList pass (2026-10-27):* candidates = IMDb films (movie, tvMovie, short, video, tvSpecial; adult titles excluded) with ≥500 votes = **84,993**. MDBList returned 83,332 of them, and **73,493 have a Letterboxd rating count**. The other 11,500 have none: 1,661 were not returned at all, and 9,839 came back with a null Letterboxd figure. Those are mostly low-vote titles (median 745 IMDb votes), over-represented among TV movies, videos and Indian films. India is 17% of the null-figure titles against 8% of all candidates, because IMDb votes there outrun Letterboxd use; the largest is *Kaiva* (2023), with 69,668 IMDb votes. These are what step 4's fallback is for. *Measured, why the figure is null:* 9,503 of the 9,839 have a Letterboxd URL in MDBList but no count. On a 400-film sample checked against Wikidata's Letterboxd IDs (P6127), MDBList's slug was right for 269 of 279, so for most of them MDBList simply never stored a count; they are low-traffic films (median 720 IMDb votes, against 1,908 for films with a count). The other ~4% are **alternative-title misses**: MDBList built the slug from the English title where Letterboxd uses the original title, or the reverse (*Les Enfants terribles* → `the-strange-ones-1950`, *Hum Bhi Akele Tum Bhi Akele* → `i-am-alone-so-are-you`). For the fallback, join on Wikidata P6127 or TMDB ID rather than on MDBList's slug. Only about 10% of the 1,661 films MDBList did not return at all have a Letterboxd ID on Wikidata, so most of them are probably not on Letterboxd.

| Letterboxd ratings | All film types | Feature films (`movie`) only |
|---|---|---|
| ≥1k | 47,884 | 42,077 |
| ≥5k | 22,225 | 20,382 |
| ≥10k | **15,150** | **14,120** |
| ≥25k | 8,931 | 8,487 |
| ≥100k | 3,782 | 3,694 |

**Final size: about 15k films clear the 10k-ratings bar** (14.1k features, plus about 1k shorts, TV movies, videos and specials). The canon/curation and regional-percentile rules add to that, so the total should land around 17–20k (an estimate until those lists are joined). That is below the earlier 20–30k estimate, because the 10k bar on Letterboxd is stricter than it looked from the IMDb counts. Each film record also keeps IMDb genres, MDBList genres (mostly TMDB's), country, language and runtime, which feed the genre → cluster organisation and the per-country/decade rule.
Spot checks (Letterboxd ratings): *Parasite* 5.96M, *The Dark Knight* 4.96M, *Good Will Hunting* 3.69M, *The Shawshank Redemption* 3.20M, *Princess Mononoke* 1.87M, *Come and See* 515k, *Seven Samurai* 480k, *Ran* 296k, *Balto* 81k, *The Wild Bunch* 81k, *The Wages of Fear* 75k.
Note: MDBList reports the Letterboxd average on a 0–10 scale (twice the site's 5-star value).

Other routes checked and rejected as primary: Google rich snippets via a SERP API (works, but costs per query and is less structured); third-party aggregator pages such as WeTrakr, which show the same Letterboxd count on HTML pages only.

Metadata comes from the TMDB API plus the daily ID exports, with Kaggle `alanvourch/tmdb-movies-daily-updates` (TMDB+IMDb, daily) as a bulk shortcut.

## 3. Scripted TV (non-anime, non-Asian-drama)
- Spine: IMDb `tvSeries` + `tvMiniSeries`, with TMDB TV for metadata, networks and origin country.
- *Measured (2026-10-28, `pipelines/tv/`):* 43,676 IMDb series with ≥100 votes, with episode counts; MDBList returned 38,857, 38,585 of them with an origin country. `route.py` splits them into four databases:

  | Database | Series | IMDb ≥2.5k | IMDb ≥500 |
  |---|---|---|---|
  | Scripted TV | 32,520 | 6,342 | 14,512 |
  | Anime | 3,139 | 583 | 1,626 |
  | Asian drama | 3,768 | 462 | 1,641 |
  | Unscripted | 4,249 | 254 | 1,186 |

  The serial-tradition flag marks 1,102 scripted series: TR 293, IN 260, BR 170, MX 155, CO 54, AR 53 and others. The minimum is ≥30 episodes for dizi (long episodes, short seasons) and ≥100 elsewhere.
- *Measured IMDb counts:* series ≥2.5k votes = 6,172, ≥5k = 3,909; miniseries ≥2.5k = 1,469.
- Proposed: **IMDb ≥2.5k votes OR the regional-percentile rule OR a major award (Emmy, BAFTA, International Emmy, Peabody)**, giving about 7–9k titles. Trakt watcher counts (free API) are a secondary signal.
- *Measured, award signal (2026-10-28, `pipelines/tv/awards.py`):* 5,533 award rows. The sources are Wikidata P166/P1411 plus Wikipedia winner lists for Emmy, International Emmy, BAFTA, Peabody, Golden Globe, TVyNovelas, Indian Telly, Golden Butterfly, Baeksang, Golden Eagle, Flying Apsaras, Magnolia, Golden Bell and the Asian Television Awards.
  - Series: **1,641 winners** (3,354 including nominees). 1,177 winners have an IMDb ID.
  - **The award rule adds about 650 winning series not already at ≥2.5k IMDb votes:** 400 are in the TV harvest below the bar (296 scripted, 76 Asian drama, 27 unscripted), and 256 are not in the harvest at all.
  - About 460 winners have no IMDb ID, mostly Chinese, Taiwanese and older Korean titles from the Golden Eagle, Golden Bell, Magnolia and Flying Apsaras awards. **Follow-up:** match them to the MDL ranking, by MDL native title.
- **Decided (2026-10-27): telenovelas, Turkish dizi and Indian serials stay in the scripted-TV database, without sub-databases of their own.** Anime and Asian dramas got their own databases because each has its own audience platform and metric (MAL, MDL). These traditions don't, since their audiences barely use IMDb or any rating site, so a separate database would have no spine metric. Instead:
  - They form a **"long-running serial" format node** (telenovela, dizi, Indian daily soap, also the Filipino teleserye and the Arabic Ramadan series) under scripted TV, so the later genre → cluster organisation can group them.
  - **Inclusion uses the regional-percentile rule** (top-N per origin country × decade, by IMDb votes and by TMDB vote_count), plus signals that track their actual reach: **Wikipedia sitelinks** (export reach; top dizi air in 100+ countries and gain many language editions), the **International Emmy** telenovela and non-English drama categories, and the national awards (Premios TVyNovelas, Indian Telly Awards, Altın Kelebek).
  - National ratings (Kantar IBOPE Brazil and Mexico, BARC India, Turkey's TİAK) are optional, if any are found to be published as open data.
  - Revisit if the regional rule leaves these cells visibly thin.

## 4. Anime (own database)
- Spine: **anime-offline-database**, the weekly-updated JSON that cross-references MAL, AniList, AniDB, Kitsu and others. The original manami-project repo was archived 2026-07-04 (final release 2026-27) and continues as `cedya77/anime-offline-database` (~38k entries, week 36 2026).
- Metric: **MAL members** via the Jikan API, cross-checked with AniList popularity (free GraphQL API, no key).
- **Decided (2026-10-28): MAL members ≥ 25,000.** Plus a per-decade top-up for pre-2000 titles and a per-country one for donghua, because MAL's audience skews recent (*Tetsuwan Atom*, 1963, has 15k members).
  - *Measured:* 38,270 candidates (`pipelines/anime/`). MAL counts come from MAL's public popularity ranking, walked down to 1,000 members: 15,644 titles.
  - MAL members ≥5k = 9,767 · ≥10k = 7,465 · **≥25k = 5,167** · ≥50k = 3,711 · ≥100k = 2,468.
  - At ≥25k by format: TV 3,194, film 684, OVA 531, special 460, ONA 297. By decade: 1960s 1 · 1970s 17 · 1980s 66 · 1990s 204 · 2000s 994 · 2010s 2,352 · 2020s 1,500. Donghua: 73 of 736.
  - AniList popularity is kept as a cross-check and for tags, genres and country of origin (22,598 titles found). AniList's audience is smaller and younger: only 2,649 titles reach 25k there.
  - Jikan (the unofficial MAL API) was unreachable from the cloud container. The official MAL API needs a client ID, so it can replace the ranking walk if one is registered.
- Include donghua (Chinese animation) here, using AniList plus Bilibili/Douban signals.

## 5. Asian live-action dramas (own database)
- Metric: **MyDramaList "Watchers"**. There is no official public API, only unofficial scrapers and reverse-engineered app wrappers, and no public dataset was found. Use Wikidata P3868 for the ID join.
- **Decided (2026-10-27): fetch MDL watcher counts politely.** The ToS risk is accepted. MDL's robots.txt allows general crawling (`User-agent: * / Allow: /`) and reserves only AI training (`Content-Signal: ai-train=no`). Rules for the fetcher:
  - One request at a time, 1.5 seconds apart by default (raised from 3–5 s on 2026-10-28 to finish a full pass in about 3 hours; the fetcher enforces a hard floor of 1 s), with an identifying User-Agent. Back off on any 429/403 or Cloudflare challenge, and never work around one (no rotating proxies, no headless-browser evasion).
  - Fetch only the title pages of candidates (IDs from Wikidata P3868 plus MDL search for the rest). Store only the ID, watchers, rating, rating count and episode count. Cache every page, so each title is fetched once per refresh. Refresh at most quarterly.
  - The counts stay internal, like every other audience metric (§7), and are never used to train models, per MDL's content signal.
  - If a title is still missing after that, TMDB carries it rather than more aggressive fetching.
- **Decided (2026-10-28): candidates come from MDL's own popularity ranking**, as anime does from MAL. That ranking is the top 5,000 dramas, 250 pages in MDL's watcher-based order, with each title page fetched for exact watchers (`pipelines/asian_drama/mdl_fetch.py`). The watchers cutoff is set from the measured distribution. The IMDb/Wikidata set below becomes a cross-reference for IMDb and Wikidata IDs.
- *Measured (2026-10-28, `pipelines/asian_drama/build_candidates.py`, now cross-reference only):* 4,589 candidates, made up of 3,768 series from the TV harvest and 821 more from Wikidata. Only 1,602 have an MDL ID on Wikidata (Wikidata's 5,371 MDL links are mostly films), so the fetcher resolves the rest through MDL search. MDL did serve normal pages to the fetcher from the cloud container.
- **Decided (2026-10-28): no Douban harvest.** MDL's ranking already covers Chinese dramas: 323 of the first 1,640 ranked are Chinese, behind 904 Korean and ahead of 228 Thai, 104 Japanese and 38 Taiwanese. If the cutoff leaves Chinese (or Thai, Taiwanese, Filipino) dramas thin relative to their domestic weight, a per-country top-up from MDL's own ranking fixes it, as donghua does for anime. Douban stays an optional later cross-check.
- Other secondary signals (optional): TMDB vote_count by origin_country, Naver/Nielsen Korea peak ratings.
- Proposed: MDL watchers ≥ ~5–10k (to be set from the measured distribution) OR a per-country MDL top-up OR a top domestic award (Baeksang, Golden Bird, and similar).

## 6. Unscripted TV (cluster-based)
- **Unit = format**, with national adaptations as children: Idol, Got Talent, The Voice, Big Brother, Survivor, MasterChef, Bake Off, Millionaire, Family Feud, Wheel of Fortune, Deal or No Deal, Dancing with the Stars / Strictly, The Masked Singer, Love Island, The Bachelor, Dragons' Den / Shark Tank, Drag Race, Top Model, Amazing Race, Ninja Warrior, Hell's Kitchen, Come Dine with Me, Supernanny, Wife Swap, The Traitors, Married at First Sight, and others.
- Formats sit under genre clusters: talent competition, cooking, dating, social-experiment and elimination, game show, makeover and lifestyle, docusoap and celebrity reality, survival and adventure, talk and late night.
- Sources: Wikidata "based on" (P144) and "instance of: television format", Wikipedia franchise articles (which list adaptations by country), and IMDb/TMDB for each local version. Trade trackers (K7 Media, The Wit) are paid and optional.
- *Measured (2026-10-28, `pipelines/unscripted/build_formats.py`):* Wikidata links a format's versions inconsistently (based on / media franchise / part of the series / derivative work), so each connected family of linked programmes is treated as one format.
  - Rule: ≥3 versions in ≥2 countries, with no country holding more than 80% of them unless the family spans 5+. That gives **209 unscripted formats with 3,127 versions**: game show 110, reality/docusoap 57, talent competition 24, cooking 8, dating 7, talk 3.
  - It also gives 254 scripted remake families (*Yo soy Betty, la fea*, *The Office*) for scripted TV, though a few Japanese broadcast slots still slip in through mis-tagged items.
  - Coverage against `seeds/unscripted/formats_checklist.txt`: 35 of 35, with Wife Swap and Married at First Sight added by hand in `seeds/unscripted/format_additions.csv` (Wikidata does not link their national versions).
- **Non-format unscripted** (prestige docuseries, true crime, nature, stand-alone reality like *Keeping Up with the Kardashians*) is handled as individual titles under the scripted-TV thresholds.

## 8. Inclusion cutoffs (decided 2026-10-28)
All rules below are an OR: a title qualifies through any one of them. "Regional top-up" means top X% per country × decade, with a minimum count per cell and a vote floor, so small industries are represented without re-adding big markets.

| Database | Main bar | Top-ups and other routes | Measured size |
|---|---|---|---|
| Film | Letterboxd ≥10k ratings | canon lists (§2); gap rule (§2 step 4); regional top-up **5%** per country × decade (min 3 per cell; Letterboxd floor 1k, or **100** in under-covered countries; +1,587 with the extra candidates) | ~18–19k |
| Scripted TV | IMDb ≥2,500 votes (6,342) | regional top-up **5%** per country × decade (≥200 votes, min 3; +502); **award winners** (+296 scripted; nominations are a signal only) | ~7,100 |
| Anime | MAL members ≥25,000 (5,167) | pre-2000: top **20%** per decade, min 5 (+271); donghua: MAL ≥**10,000** (146 instead of 73) | ~5,500 |
| Asian drama | MDL watchers ≥**5,000** (3,364 dramas) | per-country top-up: top **15%** per country × decade, min 5 (Japanese, Filipino and Hong Kong dramas are under-counted on MDL); award winners; MDL's variety shows go to unscripted | ~3,500+ |
| *(measured)* Asian drama selection | `pipelines/asian_drama/select.py`: **3,530 dramas** (KR 1,517 · CN 976 · TH 545 · JP 356 · TW 110 · PH 15 · HK 7 · SG 4); 3,412 via ≥5k watchers, 112 award-only (e.g. *Sandglass* 1995, *Journey to the West* 1986). 195 winning award rows matched to MDL (`match_awards.py`, via native and AKA titles); 460 unmatched, half never searched (request cap). 212 MDL variety shows go to unscripted. **The per-country top-up added only 5 titles:** the top-5,000 ranking holds just 7 HK and 30 PH dramas, and Japan is under-counted (*Naoki Hanzawa* 8,897 watchers). A per-country popularity pool from MDL's country-filtered listings is being fetched | |
| Unscripted | all cross-border formats (≥3 versions in ≥2 countries; 211) | non-format shows use the scripted-TV rules | 211 formats |

**Gathering gap found while setting these: African film.** The IMDb ≥500-vote candidate floor leaves Nigeria with 19 candidates, Ghana 3, Kenya 1 and Ethiopia 2 (against Iran 527, Egypt 446). Countries with under 200 candidates therefore get a lower floor (IMDb ≥100) plus Wikidata/TMDB films by country, before the regional top-up applies.
*Measured (2026-10-28, `pipelines/film/underrepresented_countries.py`):* **26,471 extra candidates** (Wikidata films by country, plus IMDb 100–499 votes, enriched via MDBList; `data/interim/film_candidates_extra.csv`). Examples: Nigeria 19 → 319, South Africa 99 → 535, Ghana 3 → 39, Senegal 6 → 39, Kenya 1 → 28, Sri Lanka 14 → 242, Cambodia 3 → 58, Myanmar 2 → 41.
**Decided:** these films typically have 200–500 Letterboxd ratings, so in the **146 countries with under 200 original candidates** the regional top-up's Letterboxd floor is **100** instead of 1,000. That adds **490 films** (*Difret*, *Teza*, *Keteke*, *Nawi*, *Contras' City*, *Sira*, *The Figurine*, *Isoken*, ...). With the extra candidates the top-up now selects 1,587 films in total.

## 7. Licensing note
Almost every audience-metric dataset (IMDb, Letterboxd samples, Douban, MAL dumps) is **non-commercial**. That is fine for an internal or personal taxonomy. If the taxonomy will ever be published commercially, ship only our own derived categories and IDs, never the raw counts.
