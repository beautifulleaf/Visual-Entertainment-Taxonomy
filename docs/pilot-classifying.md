# Classifying pilot (2026-10-28)

Published for review: https://claude.ai/artifact/Rsg7xw1qAKBDnF3RKG49Yt (page source `artifact/pilot.html`, data `artifact/pilot-data.json`).

Slices: Visual Art · Islamic world (tradition-led) and Film & Television · Japanese cinema. The page's "Pilot report" tab holds the census, the audits (blind test VA 39/50 and film 29/40 before fixes; 75 coverage probes), the rulings needed (Q1–Q8) and the scaling plan.

## Files
- `pipelines/classify/tree_visual_art.py`, `tree_film.py`: families (membership tests, keys), sub-families (axes), pilot leaves, precedence sentences, modifiers, attestation.
- `pipelines/classify/pilot_islamic.py` → `taxonomy/pilot/islamic_pool.csv` (rule dispositions for 1,357 candidate rows).
- `taxonomy/pilot/review/`: maker and film review files, blind-test and probe files.
- `seeds/classify/*_overrides.csv`: hand corrections after review.
- `pipelines/classify/build_pilot.py` → `taxonomy/pilot/islamic_placements.csv`, `japan_placements.csv`, `census.json`, `artifact/pilot-data.json`.
- `pipelines/classify/content_features.py`: TMDB keywords and overviews via MDBList (`append_to_response: keyword`) for all selected films and series → `data/interim/{film,tv}_content.csv`.
- `pipelines/classify/wikidata_titles.py`: Wikidata genre/director/movement facts by IMDb ID.
- `pipelines/classify/attest.py`: Wikidata label/alias resolution for node names (SPARQL; the search API is rate-limited from cloud IPs).

## Rulings awaited
Q1 movement vs genre first (film) · Q2 dynasties and places as filters · Q3 Asian Drama as a family · Q4 anime sub-families by genre, format as filter · Q5 painting sub-families by format · Q6 ornament as a tag · Q7 leaf granularity for folk/ware traditions · Q8 country rule for co-productions.

## Gathering gap found
Imamura's *Black Rain* (1989, 7,233 Letterboxd ratings) is not selected: the Japan 1980s 5% top-up missed it.
