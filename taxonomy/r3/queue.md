# R3 pass queue (concurrency cap 20)
FT: all 19 blocks done (validators clean); full FT trial assembly clean: 866 leaves, 36,547 titles.
VA running: design, bucket_modern_west, bucket_modern_world, bucket_contemporary, bucket_academic_19c, bucket_modsculpture_photo, bucket_named_movements, bucket_print_arch_misc, small_A_B_C, small_D_F, small_E, small_G_I_J_M, small_H, small_K, small_L.
Waiting: none.
To do at assembly:
- verify every leaf src URL and View-all catalogue URL (several passes could not reach Wikipedia);
- remap old FT codes left in notes and see-also;
- check pass-made labels flagged as weakly attested and list them in the report;
- review: Korean/Chinese weekend family serials in B1 Family Drama (may belong in B2/B4); "Desperation Crime Drama" section; Romantic Comedy-Drama leaf.
- Wikipedia API rate-limited this connection (2026-11-07): rerun `pipelines/r3/check_wiki.py` after the passes finish.
- Coverage step (owner: "make sure all existing subgenres are represented"): waits for the TSPDT harvest (taxonomy/r3/tspdt/), then 3 passes (film / television / animation) per taxonomy/r3/BRIEF_COVERAGE.md, using taxonomy/r3/imdb_interests.tsv (IMDb's 243 genre interests), AllMovie genre pages, Wikipedia genre lists and TSPDT lists.
- Done VA: bucket_contemporary (5 new leaves, 234 moved), bucket_modsculpture_photo (4 new photography leaves, 307 moved).
- Follow-up after design + small_H: move fashion designers left in country groups (Westwood, McQueen, Yamamoto, Lagerfeld ...) to the couture/fashion leaves; Scandinavian designers (Wirkkala, Sarpaneva) to N Design leaves.
