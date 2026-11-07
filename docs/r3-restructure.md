# R3: restructuring release (owner review, 2026-11-06 / 07)

## Owner requests
1. Visual Art: N Design is empty; many leaves are minimal or unorganized.
2. Film & Television: remove the retired Asian Drama family (F) and re-letter; Short Film goes inside Film; Serial Drama and Unscripted Formats go under Television; Anime becomes **Animation**, taking western and other non-Japanese animated film and TV.
3. Granularity: "Comedy film" held 630 titles from silent films to Zoolander. Leaves must be abstract, attested and divided into sections along a stated axis, as in the Culinary Taxonomy.
4. (2026-11-07) Remove web series: internet content goes to the future Interactive Entertainment Taxonomy, organised by its format.
5. (2026-11-07) Add a Copy button on leaf cards, as in the Culinary page.

## Decisions
- **Families (FT):** A Film (A1–A20 genre sub-families + A21 Short Film), B Television (B1–B11 series, B12 Serial Drama Traditions, B13–B15 unscripted formats), C Animation (C1–C11 anime, C12 Animated Feature, C13 Animated Series, C14 Animated Short). Old F and the retired leaves A12-5 and E12-1 are dropped. Every old FT code maps to new codes in `taxonomy/r3/ft_migration.csv` (built at assembly).
- **Web series rule:** a series is internet content, not television, when it is native to the open internet (YouTube, web portals, social video, app micro-drama). Subscription streaming series (Netflix, Prime, iQIYI, Tencent, Indian OTT "web series") are television and stay. Applied as: old leaves G3-6 Web Show and C1-17 Vertical Short Drama; titles whose Wikidata genre is web series / web drama; Korean web dramas (Naver TV / YouTube short-episode format). Films are never removed by this rule. Result: 82 titles in `taxonomy/r3/web_series_removed.csv`; each keeps a finder row pointing to the Interactive Entertainment Taxonomy. Text edits: TV12 and TV13 lose their web-series clauses; "web series" leaves the Series-format filter; C1-14's definition says "streaming" instead of "web series".
- **Sections:** leaves over ~40 entries carry an `axis` and `secs` (FT) or section groups (VA), as in the Culinary page.

## Method
Block passes, one per group of sub-families (18 FT blocks, 15 VA passes), each following `taxonomy/r3/BRIEF_FT.md` or `BRIEF_VA.md` and checked by `pipelines/r3/ft_validate.py` / `va_validate.py`. Inputs: `pipelines/r3/ft_inputs.py`, `pipelines/r3/va_inputs.py`.

## Status
- 2026-11-07: first launch of all 33 passes stopped on the account's weekly usage limit before any output was written. Inputs, briefs, validators and the web-series rule are in place.
