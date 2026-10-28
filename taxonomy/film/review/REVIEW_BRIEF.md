# Film placement review brief (for batch reviewers)

You place each film in one leaf of the Film & Television tab, families A Feature Film and B Short Film.

Read first: `taxonomy/film/review/ft_leaves.txt` (tab key, family keys, every leaf with its definition, precedence sentences F1–F20).

Input: `taxonomy/film/review/films_NN.csv`, one row per film: tconst, title, year, type (IMDb title type), runtime (minutes),
countries (Wikidata P495 first), language, director, wd_genre (Wikidata genres), wd_movement, imdb_genres, tmdb_genres,
linked_from (movement or cycle Wikipedia articles that link to this film's article), based_on, keywords (TMDB), overview,
proposal (a rule's guess — often too general; never trust it blindly), rule_reason.

Method, per film:
1. Run the tab key (anime → `route:FT-E`; a TV series or miniseries wrongly in the film list → `route:FT-C`; under 40 minutes → a B leaf) then the family key, first yes wins.
2. Use the evidence and your own knowledge of the film. The key wins over a leaf's examples (F10).
3. Named cycles beat movements and general genres (F1, F2). A1 movement leaves hold attested members only (named in the movement's Wikipedia article or reference histories; `linked_from` is evidence, not proof — an article also links influences and later films). If a film is an attested member but a cycle claims it, put the cycle as `leaf` and the movement code in `movement`.
4. Choose the most specific fitting leaf; general leaves (A2-4, A3-9, A6-1, A10-1, A14-5 ...) only when nothing narrower fits.
5. `see_also`: at most two other leaf codes the film plausibly touches (secondary genre), `;`-separated, or empty.
6. If the row is not a film at all (a music video, a TV episode, a video game, a duplicate), `leaf` = `exclude:<reason>`.

Output: write `taxonomy/film/review/films_NN_out.csv` with exactly these columns, one row per input row, same order:
`tconst,title,leaf,see_also,key_step,movement,confidence,note`
- leaf: a leaf code (e.g. `A4-8`), `route:FT-E`, `route:FT-C`, or `exclude:<reason>`
- key_step: the key step that decided it (e.g. `3`, `6`, `12`, `B 1`)
- movement: A1 code(s) for an attested movement member, `;`-separated, else empty
- confidence: high / med / low
- note: ≤15 words, only when useful (why a cycle, a seam, a doubt). Use csv quoting.
Write the file with Python's csv module. Check that the row count equals the input's before finishing.
Reply with: rows written, count of changes from the proposal, and up to 5 seams or leaf gaps you noticed (films that fit no leaf well).

Temporary files: other reviewers run at the same time. Keep any helper or scratch file in your own folder named after your batch, e.g. /tmp/claude-0/review_films_07/ — never a shared or generic file name.
