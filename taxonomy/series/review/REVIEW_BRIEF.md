# Series placement review brief (anime, scripted TV and Asian drama, unscripted)

You place each title in one leaf of the Film & Television tab. Read the leaf file for your batch first:
- `anime_NN.csv` → `taxonomy/series/review/anime_leaves.txt` (family E, key, leaves, AN1–AN4)
- `tv_NN.csv` and `drama_NN.csv` → `taxonomy/series/review/tv_leaves.txt` (families C and D, keys, leaves, TV1–TV5)
- `unscripted_NN.csv` → `taxonomy/series/review/unscripted_leaves.txt` (family G)

Columns. Anime: id (MAL), title, english, type (format), year, episodes, country, is_adult, studio, genres (AniList/MAL),
top_tags, tags, film_tconst. TV: id (tconst, or mdl:<MyDramaList id> for Asian dramas), title, native_title, type, years,
episodes, country, language, network, serial_flag (1 = flagged as a serial-tradition country/format at gathering; evidence
only), imdb_genres, tmdb_genres, wd_genre, keywords (TMDB), overview, source. Unscripted: id (Wikidata), title, cluster,
n_versions, n_countries, first_year, source (format or asian_variety).

Method, per row:
1. Run the family key (first yes wins), then pick the most specific fitting leaf. Use the evidence and your own knowledge of the
   title. Precedence sentences decide seams. General leaves only when nothing narrower fits.
2. Anime: keep a franchise together (AN2) — rows are sorted so seasons sit next to each other. Demographic is a tag (AN3).
3. TV: a long-running serial in a named tradition is D (TV2); an Asian drama in a named C2 tradition stays in C2 whatever its
   genre (TV3); other Asian dramas go by genre (C1, C3, C5 ...). Many Asian dramas have little evidence: use the title, native
   title, country and year with your knowledge; if you do not know the show, place it from what the evidence shows and mark
   confidence low.
4. Not a fit for this family at all (an anime in the TV list → `route:FT-E`; a film → `route:FT-A`; an unscripted show in the
   TV list is placed directly in a G leaf (tv_leaves.txt now lists family G; TV13); a scripted show in the unscripted list → `route:FT-C`; a duplicate or non-title →
   `exclude:<reason>`).
5. `see_also`: at most two other leaf codes, `;`-separated, or empty.

Output: write `<batch>_out.csv` next to the input (e.g. `taxonomy/series/review/anime_03_out.csv`) with exactly these columns,
one row per input row, same order: `id,title,leaf,see_also,key_step,confidence,note`
- confidence: high / med / low; note ≤15 words, only when useful. Use Python's csv module; check the row count matches.
Reply with: rows written, leaf counts (top 10), and up to 5 seams or leaf gaps you noticed.

Temporary files: other reviewers run at the same time. Keep any helper or scratch file in your own folder named after your batch, e.g. /tmp/claude-0/review_films_07/ — never a shared or generic file name.
