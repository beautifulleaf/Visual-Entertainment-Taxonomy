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
4. **Gaps:** if MDBList lacks a Letterboxd figure for a candidate, fall back to the Letterboxd user samples (Apr 2026 / Dec 2025) as a relative signal, with a threshold calibrated on films that do have MDBList votes.

Canon/curation lists: Sight and Sound 2022, TSPDT 1000 and 21st-century 1000, the Criterion Collection, national film registries, top prizes at major festivals.

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
  - If a candidate is still missing after that, Douban/TMDB carry it rather than more aggressive fetching.
- *Measured (2026-10-28, `pipelines/asian_drama/`):* 4,589 candidates, made up of 3,768 series from the TV harvest and 821 more from Wikidata. Only 1,602 have an MDL ID on Wikidata (Wikidata's 5,371 MDL links are mostly films), so the fetcher resolves the rest through MDL search. MDL did serve normal pages to the fetcher from the cloud container.
- Secondary signals: **Douban rating counts** for C-dramas (a better domestic signal than MDL), TMDB vote_count filtered by origin_country (KR, CN, JP, TW, TH, PH), and Naver/Nielsen Korea peak ratings.
- Proposed: MDL watchers ≥ ~5–10k OR Douban ≥50k ratings (the threshold MDL list-makers use for 2022+ titles) OR a top domestic award (Baeksang, Golden Bird, and similar).

## 6. Unscripted TV (cluster-based)
- **Unit = format**, with national adaptations as children: Idol, Got Talent, The Voice, Big Brother, Survivor, MasterChef, Bake Off, Millionaire, Family Feud, Wheel of Fortune, Deal or No Deal, Dancing with the Stars / Strictly, The Masked Singer, Love Island, The Bachelor, Dragons' Den / Shark Tank, Drag Race, Top Model, Amazing Race, Ninja Warrior, Hell's Kitchen, Come Dine with Me, Supernanny, Wife Swap, The Traitors, Married at First Sight, and others.
- Formats sit under genre clusters: talent competition, cooking, dating, social-experiment and elimination, game show, makeover and lifestyle, docusoap and celebrity reality, survival and adventure, talk and late night.
- Sources: Wikidata "based on" (P144) and "instance of: television format", Wikipedia franchise articles (which list adaptations by country), and IMDb/TMDB for each local version. Trade trackers (K7 Media, The Wit) are paid and optional.
- *Measured (2026-10-28, `pipelines/unscripted/build_formats.py`):* Wikidata links a format's versions inconsistently (based on / media franchise / part of the series / derivative work), so each connected family of linked programmes is treated as one format.
  - Rule: ≥3 versions in ≥2 countries, with no country holding more than 80% of them unless the family spans 5+. That gives **209 unscripted formats with 3,127 versions**: game show 110, reality/docusoap 57, talent competition 24, cooking 8, dating 7, talk 3.
  - It also gives 254 scripted remake families (*Yo soy Betty, la fea*, *The Office*) for scripted TV, though a few Japanese broadcast slots still slip in through mis-tagged items.
  - Coverage against `seeds/unscripted/formats_checklist.txt`: 33 of 35. Wife Swap and Married at First Sight are missing and need hand-adding.
- **Non-format unscripted** (prestige docuseries, true crime, nature, stand-alone reality like *Keeping Up with the Kardashians*) is handled as individual titles under the scripted-TV thresholds.

## 7. Licensing note
Almost every audience-metric dataset (IMDb, Letterboxd samples, Douban, MAL dumps) is **non-commercial**. That is fine for an internal or personal taxonomy. If the taxonomy will ever be published commercially, ship only our own derived categories and IDs, never the raw counts.
