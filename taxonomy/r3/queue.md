# R3 pass queue (concurrency cap 20)
FT: all 19 blocks done (validators clean); full FT trial assembly clean: 866 leaves, 36,547 titles.
VA running: design, bucket_modern_west, bucket_modern_world, bucket_contemporary, bucket_academic_19c, bucket_modsculpture_photo, bucket_named_movements, bucket_print_arch_misc, small_A_B_C, small_D_F, small_E, small_G_I_J_M, small_H, small_K, small_L.
Waiting: none.
To do at assembly:
- verify every leaf src URL and View-all catalogue URL (several passes could not reach Wikipedia);
- remap old FT codes left in notes and see-also;
- check pass-made labels flagged as weakly attested and list them in the report;
- review: Korean/Chinese weekend family serials in B1 Family Drama (may belong in B2/B4); "Desperation Crime Drama" section; Romantic Comedy-Drama leaf.
- Link check (owner: the per-link API check was inefficient): Wikipedia links checked offline against the one-file title dump (pipelines/r3/check_wiki.py); "View all" links checked once per URL template (domain + path pattern), one-offs individually.
- Coverage step (owner: "make sure all existing subgenres are represented"): waits for the TSPDT harvest (taxonomy/r3/tspdt/), then 3 passes (film / television / animation) per taxonomy/r3/BRIEF_COVERAGE.md, using taxonomy/r3/imdb_interests.tsv (IMDb's 243 genre interests), AllMovie genre pages, Wikipedia genre lists and TSPDT lists.
- Done VA: bucket_contemporary (5 new leaves, 234 moved), bucket_modsculpture_photo (4 new photography leaves, 307 moved).
- Follow-up after design + small_H: move fashion designers left in country groups (Westwood, McQueen, Yamamoto, Lagerfeld ...) to the couture/fashion leaves; Scandinavian designers (Wirkkala, Sarpaneva) to N Design leaves.
- Done VA: bucket_modern_world (10 new leaves, 405 moved).
- Merge fixes at assembly: duplicate artists "M'hamed Issiakhem" = "Mohammed Issiakhem (1928-1985)"; "Kamala Ibrahim Ishag" = "Kamala Ibrahim Ishaq" (Crystalist); new leaves with the same label across passes merge by label (Gutai, Feminist art); check Margaret Mellis and Joseph Uhl (Western European, left in a "Europe" group).
- Verify all `catalogues` URLs (passes picked many from memory).
- TSPDT Starting List (owner): harvest it fully (tspdt_starting_list, and the 21st Century Starting List tspdt_21st_starting_list), then place every Starting List film not already selected — a placement step after coverage (likely several passes by sub-family, depending on how many films are new).
- Done VA: bucket_named_movements (27 leaves sectioned by named schools; 20 moved out; Mughal works and Collections).
- Review after assembly: non-artists left in "outliers" groups (Maria Cunitz in Baroque, Carême in Old Master Print, Tarō Okamoto in Nihonga); suspect birth years (Richard Wilson b. 1953 in Rococo, François Dumont b. 1751 in Baroque Sculpture).
- Done VA: bucket_print_arch_misc (2,230 rows added, 304 moved, new Franco-Belgian Comics leaf — merge by label with the one from bucket_contemporary).
- Assembly fixes: rename "Maqsud Kashani, whose signature ..." → "Maqsud Kashani"; Josef Hoffmann and Henry van de Velde appear in both I3-15 and K6-21 (keep one home: I3-15 for Hoffmann? decide; van de Velde K6-21 as architect with I3-15 see-also).
- Starting List placement (owner: rules first, passes for the rest): ~10,400 matched + ~11,000 id-less films.
- Done VA: bucket_modern_west (15 new leaves, 1,242 moved; 4,072 residue grouped by ~110 named groups then country), bucket_academic_19c (6 new leaves, 667 moved).
- Assembly: merge same-label new leaves (Orientalism ×2, Franco-Belgian comics ×2, possibly Gutai, Feminist art, Mir iskusstva, Vienna Secession, Young Poland, Nagybánya); dedupe makers placed in two leaves (Krøyer, Nikolai Ge, Vasnetsov, Halonen ...): keep the named-school leaf over a residual bucket.
- Check judgement calls: Saliger and Padua in Nazi art; Epstein in Modern Sculpture (not Vorticism); Buren in BMPT section.
- Done VA: small_L (Art in Place: 3,010 kinds, 2,424 rule-based sites; 31 leaves still ≤ 4 kinds, ~20 leaves from knowledge only; some sources are Wikipedia search URLs — replace in the link check).
- Done: small_K (Architecture: 13,766 kinds), FT coverage television (6 new leaves, 238 adds; News leaf dropped at assembly — news out of scope). Owner's call noted: sitcom eras (British sitcom eras, US network-era sitcoms) not sectioned, since that would re-sort the comedy leaves.
- Done: FT coverage animation (4 new leaves incl. Soviet Animation and Animated Documentary; Golden Age cartoons by studio; ~414 canonical adds).
- Assembly fixes: Ne Zha (2019) and Ne Zha 2 placed twice (MAL id and IMDb id) — keep one; Harem has leaves in both C5-5 and C10-9 — merge into one; move Tower (2016) and The Missing Picture (2013) from A19 to the new Animated Documentary leaf; Princess Iron Fan (1941) added without id.
- Done VA: design (N Design: 34 leaves — 12 furniture & lighting, 9 product & industrial, 13 graphic; ~355 designed objects; 239 designers moved into N).
- Assembly decisions: merge I3-17 Bauhaus (1 row) into the new Bauhaus Design leaf; ~120 fashion designers left in I3-19/I3-20 → a Fashion Design leaf under H7 Dress & Costume (check what small_H built; with the fashion designers from the photo pass); B2-11 Soviet Poster vs Constructivist Graphic Design: keep both, see-also.
- Done VA: small_G_I_J_M (3,863 kinds from 872; 1,888 works-catalogue rows, 428 Collections rows, 483 View-all links; 53 leaves still ≤ 4 kinds; Pierre Gole in I1-23 and I3-8 — one home).
- Owner: yes to sitcom eras — pass re-sections B8 (and B10-4) by attested sitcom eras (coverage_out/sitcom_eras/resections.json); assembly applies re-sectioning after all moves and adds.
- Done: sitcom eras (B8-1 Family, B8-5 Hangout, B8-9 Character Comedy re-sectioned by attested US/UK eras; 315 titles). Broad City web original (tt1948541) out by override.
- Owner: yes to Workplace Comedy (B8-3) by era — pass running (adds to coverage_out/sitcom_eras/resections.json).
- Done VA: small_E (Ceramics: 4,112 kinds; 2,939 rule-based works; Bubnivka and Oleshnia still empty).
- Done: Workplace Comedy B8-3 by era (12 sections, 197 titles; script kept as coverage_out/sitcom_eras/build_b83.py). Family Sitcom 1970 titles moved to the relevancy-era section (era starts 1970, as in B8-3).
- Done VA: small_A_B_C (4,274 kinds; 741 manuscripts by rule; 623 Collections rows). Assembly: Malwa manuscripts unplaced; Registrum Gregorii master and Florentius one home.
- Done VA: small_H (Textiles: 4,728 kinds, 3,283 works by rule, 500 Collections rows; 126 leaves ≤ 4 kinds). Gap: no couture/runway leaf — at assembly add H7 'Haute Couture & Fashion Design' (houses + the ~120 fashion designers left in I3-19/I3-20 and those left by the photo pass), catalogues: Vogue Runway, Met Costume Institute, Kyoto Costume Institute, Europeana Fashion.
- Done: FT coverage film (27 new leaves, 20 re-sectioned, 911 adds; Pink Film 0 → 63). Assembly: merge duplicate leaves Screwball (A12-4 / A13-10), Spy Comedy (A3-22 / A12-50), Lost World (A5-14 / A6-21); Harem (C5-5 / C10-9).
- Resize rz_2 done (6 leaves split: Film Noir → American/International/British; Social Realism → +Labour Film, Rural Drama; Biographical Doc → +Portrait, Subculture; Essay Film → +Political Essay, Landscape Film; Relationship Drama → +Marriage Drama, Late-Life & May–December; Drama Short → +Art-House Short). Weakly attested labels to review: Rural Drama, Portrait Documentary, International Film Noir, Late-Life & May–December Romance.
- Resize rz_5 done (10 leaves split: +Film about Filmmaking, Revolutionary Film, Ethnofiction, Filmmaker Portrait Doc, Film History Doc, Spy-Action Film, Murder Comedy (weak label), Neo-Slasher, Doppelgänger Film, Social Thriller, Comedy Team Film, Love Triangle Film; A13-4 renamed Adultery Film).
