# R3 brief: Film & Television coverage pass

The Film & Television tab has been rebuilt (866 leaves; index `taxonomy/r3/ft_leaf_index.tsv` with code, label, sub-family, title count, sections and definition; every placed title in `taxonomy/r3/ft_title_index.tsv`). The earlier passes could only re-sort titles that were already selected, so subgenres with no selected titles are missing or empty. The owner: "Pink film shouldn't be empty, for example *Antiporno* (2016) has over 60K ratings on Letterboxd" and "We want to make sure **all existing subgenres are represented**."

You own one part of the tab (see your prompt). Your job:
1. **Audit coverage.** For each sub-family you own, list the established subgenres, cycles, movements and national genre traditions that the field names — use Wikipedia's genre articles and lists (e.g. "List of film genres", each genre article's "Subgenres" section, "Lists of horror films by subgenre", "List of television genres", "List of anime genres"), Wikidata film-genre items, and the trade's/fandom's own terms. Compare with the existing leaves and their sections. A subgenre counts as represented when it is a leaf, or a named section of a leaf, with at least 5 titles (an attested cycle whose whole canon is smaller may have fewer, but never 0).
2. **Add what is missing.** For each missing or empty subgenre: either a new leaf (if it is a genre in its own right) or a new section of the closest existing leaf; then give it titles:
   - first, **move** already-placed titles that belong there (e.g. *Antiporno* (tt5973032) from A20-7 to Pink Film / Roman Porno);
   - then **add** titles from the gathered candidate pools, which carry real ids: `data/interim/film_candidates.csv` (IMDb ≥500 votes: tconst, title, year, genres, imdb_votes), `film_ratings.csv` (same tconsts with letterboxd_votes and country), `film_candidates_extra.csv`, `tv_candidates.csv`, `anime_candidates.csv` (mal_id, tags). Prefer the most-watched and canonical titles; aim for 5–25 titles per added subgenre, more for big genres that were simply absent.
   - only if a canonical title is not in any pool, add it from knowledge with an IMDb tconst or MAL id you are sure of (else leave id blank).
3. Fill every **empty leaf** in your part (e.g. A15-5 Pink Film: the pink film canon of Kōji Wakamatsu, Masao Adachi, Hisayasu Satō, Takahisa Zeze, the "Seven Lucky Gods" of pink, and Nikkatsu Roman Porno — Tatsumi Kumashiro, Noboru Tanaka, Masaru Konuma, Chūsei Sone — and the 2016 Roman Porno Reboot, which includes *Antiporno*).
Do not re-sort the rest of the tab; only move a title when it clearly belongs in a subgenre you are adding or filling.

Rules from the main brief still hold: attested names only (source URL per new leaf), one home per title, leaves defined by what the work is, country/decade/studio are filters (named national cycles are leaves), sections along a stated axis, web series out of scope (subscription streaming is television), explicit pornography is out of scope (it belongs to the Pleasure Taxonomies; pink film and Roman Porno are theatrical softcore genres with a critical canon and belong here).

## Output: `taxonomy/r3/coverage_out/<part>/`
- `new_leaves.json`: `[{"key": "NEW1", "sub": "A4", "label": "...", "breadth": "...", "defn": "...", "aliases": "", "see": "", "src": [["https://en.wikipedia.org/wiki/...", "Wikipedia"]], "axis": "(if secs)", "secs": [...]}]`
- `new_sections.csv`: `leaf,label` — a section appended to an existing leaf's `secs` (referenced as `<leaf>#<label>` below).
- `moves.csv`: `id,to,sec,note` — `to` is an existing leaf code or a NEW key; `sec` is a 1-based index into that leaf's sections, or a new section label, or blank.
- `adds.csv`: `id,title,year,who,kind,to,sec,note` — `kind` is film / tv / anime; `who` is director or country.
- `summary.md` (≤ 50 lines): the coverage audit (subgenres checked, which were missing, what you added), doubts.
Run `python3 pipelines/r3/coverage_validate.py <part>` until it exits 0. Keep scripts inside your output directory. Do not touch git or other files.
