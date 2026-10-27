# Sourcing plan: metrics and harvest sources

Status: proposal (2026-10-27). Numbers marked *measured* were computed on that date; everything else is a recommendation to be confirmed.

## 0. Cross-cutting decisions

- **Wikidata QID is the universal join key.** Wikidata already carries cross-IDs for every source below:
  IMDb (P345), TMDB movie/TV (P4947/P4983), Letterboxd (P6127, ~273k films linked, *measured*),
  MyAnimeList (P4086), AniList (P8729), MyDramaList (P3868), Douban film/drama (P4529/P6443),
  ULAN (P245), WikiArt (P6002), Artfacts (P13700), Art UK (P1367).
- **Prominence thresholds are relative to the region and period, not global.** One global cutoff reproduces the Anglophone/Western bias of whatever platform measures it. Each region and period bucket gets its own percentile cutoff, with a global floor.
- **The inclusion rule is a union of signals (an OR).** A title or artist enters if *any* qualifying signal passes: audience count, canon list, institutional presence, or multilingual Wikipedia presence. That keeps cult and niche work without a long tail.

## 1. Traditional visual art (ancient to contemporary, worldwide)

### Unit of organization
- **Named artists** where the tradition records authorship (most post-1300 Western, Chinese/Japanese/Korean literati and court painting, Persian/Mughal miniature, modern and contemporary everywhere).
- **Cultures, workshops and object traditions** where it does not (Attic red-figure, Benin bronzes, Nok, Gandhara, Moche, Maya ceramics, Aboriginal rock art). Getty AAT and museum `culture` fields provide these nodes. Named artists hang under them where they are known (e.g. Exekias under Attic black-figure).
- Hierarchy: Region, then Period, then Movement/School/Tradition, then Artist or Workshop, then representative works.

### Spine (open, bulk-downloadable)
| Source | Use | Access |
|---|---|---|
| Wikidata | artists, movements (P135), dates, citizenship, sitelinks | SPARQL / dumps, CC0 |
| Getty ULAN | artist authority (~300k), roles, nationality | LOD N-Triples (XML/relational retired; final static dump 2026-01-30) |
| Getty AAT | styles, periods, cultures, object types (the taxonomy backbone) | LOD N-Triples |
| Met, AIC, Cleveland, NGA, MoMA, Smithsonian (incl. National Museum of Asian Art and the National Museum of African Art) | institutional presence, representative works, culture tags | CC0 CSV/JSON/APIs |
| ColBase (Japan national museums), National Palace Museum Taiwan open data, Europeana | East Asian and European depth | open APIs/downloads |
| WikiArt (via Wikidata P6002) | cross-check and style labels only, **not the spine** | no official bulk API |

### Prominence metric (artists)
Composite score, thresholded per region and period:
1. **Wikidata sitelink count**, i.e. the number of Wikipedia language editions. This is the best single global signal because zh/ja/ar/fa/hi wikis carry their own canons. *Measured:* painters with ≥5 sitelinks = 24,946, ≥15 = 4,119; sculptors ≥5 = 6,773; photographers ≥5 = 7,033. WikiArt has roughly 3–4k artists.
2. **Museum presence**: the number of distinct open-access collections holding the artist's work.
3. **Contemporary only**: Artfacts ranking (Wikidata P13700), plus participation in major biennials and documenta. Market data (Artprice) is optional and paid.

### Do not build on
- Artsy public API: officially being retired and may disappear without notice.

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
- Limits: free = 1,000 requests/day; €3/month supporter = 100,000/day; every tier is also capped at 1,000 reads per 5 minutes. A full pass over ~60k candidates is ~300 batch calls, under an hour even on the free tier.
- MDBList refreshes Letterboxd numbers itself; use its `updates` endpoint for incremental sync.
- Caveat: MDBList obtains this from Letterboxd. We consume a public third-party API rather than scraping, but the counts remain Letterboxd's data, so keep them internal (see §7).

### Pipeline
1. **Candidate set:** IMDb `movie` with numVotes ≥ 1,000 (49,392, *measured*), unioned with TMDB films with vote_count ≥ ~50 and with every film on the canon lists below. The union catches titles that are under-voted on IMDb but logged on Letterboxd (arthouse, non-English, shorts).
2. **Enrich via MDBList batch:** get `letterboxd.votes` per film.
3. **Include if** `letterboxd.votes ≥ 10,000` **OR** a canon/curation hit **OR** the regional-percentile rule (top-N by Letterboxd votes per country and decade, so that Nigerian, Indonesian or Iranian cinema is not cut).
4. **Gaps:** if MDBList lacks a Letterboxd figure for a candidate, fall back to the Letterboxd user samples (Apr 2026 / Dec 2025) as a relative signal, with a threshold calibrated on films that do have MDBList votes.

Canon/curation lists: Sight and Sound 2022, TSPDT 1000 and 21st-century 1000, the Criterion Collection, national film registries, top prizes at major festivals.

*Measured IMDb counts (movies):* ≥1k votes = 49,392 · ≥2.5k = 29,175 · ≥5k = 19,221 · ≥10k = 12,657.
*Measured Letterboxd 10M-sample (films logged by ≥N of 6,519 users):* ≥20 = 41,960 · ≥50 = 23,586 · ≥100 = 15,129.
**Expected final size: about 20–30k films**, an estimate to be replaced by the real figure after the first MDBList pass.

Other routes checked and rejected as primary: Google rich snippets via a SERP API (works, but costs per query and is less structured); third-party aggregator pages such as WeTrakr, which show the same Letterboxd count on HTML pages only.

Metadata comes from the TMDB API plus the daily ID exports, with Kaggle `alanvourch/tmdb-movies-daily-updates` (TMDB+IMDb, daily) as a bulk shortcut.

## 3. Scripted TV (non-anime, non-Asian-drama)
- Spine: IMDb `tvSeries` + `tvMiniSeries`, with TMDB TV for metadata, networks and origin country.
- *Measured IMDb counts:* series ≥2.5k votes = 6,172, ≥5k = 3,909; miniseries ≥2.5k = 1,469.
- Proposed: **IMDb ≥2.5k votes OR the regional-percentile rule OR a major award (Emmy, BAFTA, International Emmy, Peabody)**, giving about 7–9k titles. Trakt watcher counts (free API) are a secondary signal.
- Gap to decide: telenovelas, Turkish dizi and Indian serials are under-voted on IMDb. Either give them their own sub-databases like anime, or rely on the regional rule.

## 4. Anime (own database)
- Spine: **anime-offline-database**, the weekly-updated JSON that cross-references MAL, AniList, AniDB, Kitsu and others. The original manami-project repo was archived 2026-07-04 (final release 2026-27) and continues as `cedya77/anime-offline-database` (~38k entries, week 36 2026).
- Metric: **MAL members** via the Jikan API, cross-checked with AniList popularity (free GraphQL API, no key).
- Proposed: MAL members ≥ ~25–50k, separately per format (TV, film, OVA/ONA), plus a per-decade percentile for pre-2000 titles.
- Include donghua (Chinese animation) here, using AniList plus Bilibili/Douban signals.

## 5. Asian live-action dramas (own database)
- Metric: **MyDramaList "Watchers"**. There is no official public API, only unofficial scrapers and reverse-engineered app wrappers, and no public dataset was found. Use Wikidata P3868 for the ID join and fetch watcher counts politely in small batches (a ToS risk to accept or avoid).
- Secondary signals: **Douban rating counts** for C-dramas (a better domestic signal than MDL), TMDB vote_count filtered by origin_country (KR, CN, JP, TW, TH, PH), and Naver/Nielsen Korea peak ratings.
- Proposed: MDL watchers ≥ ~5–10k OR Douban ≥50k ratings (the threshold MDL list-makers use for 2022+ titles) OR a top domestic award (Baeksang, Golden Bird, and similar).

## 6. Unscripted TV (cluster-based)
- **Unit = format**, with national adaptations as children: Idol, Got Talent, The Voice, Big Brother, Survivor, MasterChef, Bake Off, Millionaire, Family Feud, Wheel of Fortune, Deal or No Deal, Dancing with the Stars / Strictly, The Masked Singer, Love Island, The Bachelor, Dragons' Den / Shark Tank, Drag Race, Top Model, Amazing Race, Ninja Warrior, Hell's Kitchen, Come Dine with Me, Supernanny, Wife Swap, The Traitors, Married at First Sight, and others.
- Formats sit under genre clusters: talent competition, cooking, dating, social-experiment and elimination, game show, makeover and lifestyle, docusoap and celebrity reality, survival and adventure, talk and late night.
- Sources: Wikidata "based on" (P144) and "instance of: television format", Wikipedia franchise articles (which list adaptations by country), and IMDb/TMDB for each local version. Trade trackers (K7 Media, The Wit) are paid and optional.
- **Non-format unscripted** (prestige docuseries, true crime, nature, stand-alone reality like *Keeping Up with the Kardashians*) is handled as individual titles under the scripted-TV thresholds.

## 7. Licensing note
Almost every audience-metric dataset (IMDb, Letterboxd samples, Douban, MAL dumps) is **non-commercial**. That is fine for an internal or personal taxonomy. If the taxonomy will ever be published commercially, ship only our own derived categories and IDs, never the raw counts.
