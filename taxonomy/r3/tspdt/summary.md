# TSPDT harvest (2026-11-07)

Whole site of They Shoot Pictures, Don't They (theyshootpictures.com), fetched once per page with curl (~1 s apart) and parsed locally; raw pages in `raw/` (64 MB, gitignored, re-fetchable with `scripts/`).

- sitemap.xml: 2,413 URLs (2,325 director pages, 88 others), plus 11 linked spreadsheets and the two Starting List tables.
- `lists.csv`: 346 rows; 288 lists with entries — 4 canon, 2 noir, 6 polls, 273 critics' ballots ("Beyond the Sight & Sound canon"), 3 others (two Ex-1000 lists, Recommendations); the rest rank directors only or are aliases.
- `entries.csv`: 93,974 rows, ~41,300 distinct films, 84.7% matched to IMDb (77,874 exact, 1,708 fuzzy, 14,392 none); extra columns genre, colour, mins, tconst_source (TSPDT's own IMDb link vs title+year match). 18,774 matched films are not in film_selected.csv.
- Starting Lists (one server-rendered table each; genre, colour and country from the site's XLS files):
  - `tspdt_starting_list`: 26,551 rows, 66.4% matched, 8,990 matched films not selected.
  - `tspdt_21st_starting_list`: 13,420 rows, 67.5% matched, 4,012 not selected.
  - Union: 39,971 rows (~31,400 films), 20,218 tconsts, **10,429 matched films not selected**; ~11,000 films unmatched (kept with director and country).
- Check: 1,942 of 1,945 tspdt_1000 / 21st-century-1000 ids agree with film_canon.csv; tspdt_1000 98.5% matched, 21st Century 1000 96.0%.
- Not fetched: director filmographies (loaded by script from a Google Sheet; download refused by the session's permission policy); 2 pages 404. The site has no separate genre, national or decade lists; genre is a column of the Starting Lists.
