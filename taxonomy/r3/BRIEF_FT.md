# R3 brief: Film & Television block pass

You are one of 19 parallel passes rebuilding the Film & Television tab of the owner's Visual Entertainment Taxonomy (a browsable reference work, published as a claude.ai artifact). Each pass owns one **block**: a set of new sub-families and every title currently placed in them. Repository root: `/home/user/Visual-Entertainment-Taxonomy`.

## Why
The owner's review: "we are not at the level of granularity or organization needed. 'Comedy film' currently contains over 600 entries from silent films to Zoolander ... you will need to exhibit abstract thinking here to perfect this, take a look at the Culinary Taxonomy for an example."

The Culinary Taxonomy's method, which you must follow:
- A **leaf** is defined abstractly by what the thing *is* (its structure / engine / mode), with a one-sentence membership test and examples, and it groups comparable items. Typical leaf: 20–80 items; large leaves are allowed only when they are then divided.
- A leaf over ~40 items is divided into **sections** along one stated **axis** ("by the comic engine: ..., ...; X last"). Sections are ordered by affinity (canonical form first, edge cases last), never alphabetically. Typically 3–10 sections, each with at least ~3 items. A last catch-all section is allowed only if small, and named specifically ("Other Workplace Comedies", not "Other").
  Culinary example — leaf *Leavened Oven Flatbreads* (94 items), axis "by where it bakes, pocket, oiled and thin crisp breads apart: tandoor wall, oven floor, stones or embers, pan", sections: Tandoor-Wall Breads · Puffed Pocket Breads · Oven-Floor Breads · Oiled & Dimpled Breads · Thin Sheet & Crisp Breads · Stone & Ember-Baked Breads · Pan-Baked Leavened Breads.
- Membership is decided by tests, not by names; exactly one home per title.

## The tab's new shape (decided)
Families: **A Film** (features and short films; the old Short Film family is now sub-family A21), **B Television** (series, the serial drama traditions, unscripted formats, live event and sports television). Web series (internet-native content) are out of scope: they go to the future Interactive Entertainment Taxonomy; subscription streaming series are television. **C Animation** (anime C1–C11 and non-Japanese animation C12–C14). The retired Asian Drama family is gone. All sub-families of the tab:
- A1 Movements & Schools
- A2 Crime
- A3 Thriller & Mystery
- A4 Horror
- A5 Science Fiction
- A6 Fantasy & Adventure
- A7 Action & Martial Arts
- A8 Historical & Period Film
- A9 War Film
- A10 Western
- A11 Biographical Film
- A12 Comedy
- A13 Romance
- A14 Musical & Dance Film
- A15 Erotic Film
- A16 Drama
- A17 Children's & Family Film
- A18 Popular Cinema Modes
- A19 Documentary
- A20 Experimental & Avant-Garde
- A21 Short Film
- B1 Drama Series
- B2 Korean Drama
- B3 Japanese Television Drama
- B4 Chinese-Language Drama
- B5 Boys' Love & Girls' Love Drama
- B6 Lakorn
- B7 Crime & Thriller Series
- B8 Comedy Series
- B9 Speculative Series
- B10 Children's Series
- B11 Documentary Series
- B12 Serial Drama Traditions
- B13 Competition Formats
- B14 Factual Entertainment Formats
- B15 Variety & Talk Formats
- B16 Live Event & Sports Television
- C1 Action & Battle Anime
- C2 Mecha & Science Fiction Anime
- C3 Fantasy & Isekai Anime
- C4 Magical Girl Anime
- C5 Romance Anime
- C6 Slice of Life & Iyashikei Anime
- C7 Sports & Game Anime
- C8 Drama, Mystery & Psychological Anime
- C9 Horror Anime
- C10 Comedy Anime
- C11 Children's & Family Anime
- C12 Animated Feature
- C13 Animated Series
- C14 Animated Short

## Rules for leaves
1. **Names are attested.** Every leaf label is the established term in film/TV history, criticism, the trade or fandom (Wikipedia article title, Wikidata genre item, encyclopedia or reputable criticism). Never coin a phrase. Give at least one source URL per leaf in `src` (normally `https://en.wikipedia.org/wiki/<Article>` — only articles you are confident exist). Native terms go in aliases or in parentheses (Jidaigeki, *wuxia*).
2. **Abstraction over catch-alls.** No leaf may be a residual like "Comedy Film" or "Drama Series". Find the comic/dramatic/thrill engine, premise, mode or named cycle that groups titles. Cycles, movements and national genres that the field names (giallo, poliziottesco, Ealing comedy, Nordic noir, makjang) are leaves; plain country, decade, studio, director, platform are **filters, never leaves** (exception in the animation block hint).
3. **Sizes.** Leaf hard maximum 200 titles, aim ≤ 120, median 30–80. Leaves over 40 must have sections (`secs`) and a leaf `axis`. A leaf under 5 titles is acceptable only for an attested movement, cycle or tradition with its own canon; otherwise merge it. Keep all existing small named cycles from the old tree (yakuza film, cine quinqui, bourekas, rumberas, partisan film ...) unless you merge them into a better attested leaf and say so in the summary.
4. **Order** leaves within a sub-family by affinity (canonical form first, neighbours together, hybrids and edge cases last). Number them `<SUB>-1, <SUB>-2, ...` in that order.
5. **Breadth**: broad / medium / narrow (how wide the concept is, not the count).
6. **Definition** (`defn`): a membership test stated as what the title *is*, plus 2–4 example titles from your list in parentheses, plus a boundary sentence where a neighbour is close ("a romantic comedy goes to A13"). Plain HTML allowed (<i>, no links).
7. `see`: short text naming neighbour leaves by new code ("A12-14 Parody & Spoof; A13 Romance"). You may cite codes inside your block, or any sub-family code above.
8. Sub-family `axis` must start with "Axis:" and state the single axis of the sub-family.

## Rules for placement
- Place **every** title in your input file exactly once, in one of your block's leaves, with a section number if the leaf has sections. Use your own knowledge of the film/series first; the evidence columns (genres, Wikidata genre, keywords, overview, the old leaf and the old note) help with titles you do not know.
- `see_also`: optional, one or two other leaf codes (new codes) for a strong secondary genre.
- `note`: keep the old note if still useful, or a short reason (≤ 12 words) for a non-obvious placement. Never write audience counts.
- `route`: ONLY for clear errors where the title does not belong in any of your sub-families at all (e.g. a romantic comedy sitting in Comedy, or an animated feature in a live-action block): put the target sub-family code (e.g. `A13`) in `route` and leave `leaf`/`sec` empty. Keep routes rare (well under 5% of rows). Do not route a title just because it is a hybrid; hybrids get see_also.

## Files
- Input: `taxonomy/r3/ft_in/<block>.csv` — columns id, title, year, who (director or country), old_leaf, old_leaf_label, old_see, note, movement_tag, kind, genres, wd_genre, keywords, overview, extra. Read it with Python (csv module); it is too big to read whole in one tool call. Also read `taxonomy/r3/ft_blocks.json` for your block's sub-families and hint.
- Output directory: `taxonomy/r3/ft_out/<block>/` with
  - `leaves.json`: {"subs": [{"code": "A12", "label": "Comedy", "axis": "Axis: ...", "leaves": [{"code": "A12-1", "label": "...", "breadth": "medium", "defn": "...", "aliases": "...", "see": "...", "src": [["https://en.wikipedia.org/wiki/...", "Wikipedia"]], "axis": "by ... (only if secs)", "secs": ["Section 1", "Section 2"]}]}]}
    Sub-family labels may be refined but keep the codes. Every listed sub-family of your block must appear.
  - `assign.csv`: header `id,leaf,sec,see_also,note,route`; one row per input id. `sec` is the 1-based index into the leaf's `secs` (blank if none).
  - `summary.md`: ≤ 40 lines — the leaf list with counts, merges of old cycles, any weakly attested labels, routes.
- Suggested method: (1) profile the input (counts per old leaf, sample titles); (2) draft the leaf + section scheme; (3) assign in chunks of ~200–300 titles with Python you write to files (you may write per-chunk CSVs into your output directory and concatenate them; delete scratch chunks at the end); (4) run `python3 pipelines/r3/ft_validate.py <block>` and fix every ERROR and as many WARNs as sensible; iterate until it exits 0.
- Write only inside `taxonomy/r3/ft_out/<block>/`. Do not edit other files, do not commit, do not touch git.
- **Blocks that add titles** (`"additions": true` in ft_blocks.json, e.g. tv_live_sports): also write `additions.csv` with header `id,title,year,who,leaf,sec,see_also,note` — one row per added title (who = country or broadcaster). Ids: an IMDb tconst or Wikidata QID you are confident of, else blank. Only real, notable programmes and broadcasts.
- Final reply: ≤ 15 lines: leaves count, size max/median, routed count, validator status, notable judgement calls.
