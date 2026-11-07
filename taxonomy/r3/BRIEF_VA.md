# R3 brief: Visual Art pass

You are one of several parallel passes improving the Visual Art tab of the owner's Visual Entertainment Taxonomy (a browsable reference work published as a claude.ai artifact). Repository root: `/home/user/Visual-Entertainment-Taxonomy`.

## The owner's review
"Visual Art: Design is empty right now, and many of the leaves are minimal or unorganized." Visual Art "will try to stick to named traditions as found in museums (albeit needing a lot more organization and named entries)". The model for organization is the owner's Culinary Taxonomy: inside a leaf, entries are grouped into **sections** along one stated **axis**, ordered by affinity (canonical first, edge cases last), never alphabetically; every entry is a real, named thing with a one-line gloss.

## How the tab works (do not change)
- Tab → Family (by medium: Painting, Drawings & Prints, Book Arts, Sculpture, Ceramics, Glass, Metalwork, Textiles, Woodwork/Lacquer/Furniture, Photography, Architecture, Art in Place, New Media, Design) → Sub-family → **Leaf** (a named tradition, school, movement, ware, style) → **Kind** (sub-type, centre or workshop, named maker, artist, architect, representative work, site).
- Region and period are filters, never leaves. Named schools and movements that are national (Hague School, Bengal School) are legitimate leaves and sections.
- Leaf codes and labels stay as they are (you may improve a leaf's `defn`). New leaves get codes later from the coordinator.
- Names are attested: every leaf and every kind you add must be a real, established name you are confident of (art-historical literature, museum records, Wikipedia/Wikidata, Grove). **Never invent** makers, works or centres. When unsure, add nothing.

## A kind row
`[name, group, gloss, source, is_maker]`
- `name`: the kind's name (proper name of the sub-type, centre, workshop, maker, work or site; for a work: "Title (Maker, date)").
- `group`: the section the row sits in (see below).
- `gloss`: one short line — what it is, where/when, and for a work its holding museum. Plain text, ≤ 140 chars. Clean up machine glosses: drop "Gathered rows ...", raw counts like "glass 60", internal codes like "now T112 (period, painting)", "excluded rows ...". **Keep** any Possession back-link ("owned as X (Possession B3)") as a short trailing "· Possession: X (B3)", and keep the URL that was in a Possession gloss in the `source` field.
- `source`: keep the existing source tag for existing rows (e.g. `artists`, `met/aic`, `possession https://...`). For rows you add: `r3 <url>` with one URL you are confident exists (normally `https://en.wikipedia.org/wiki/<Article>` or a museum collection page).
- `is_maker`: 1 for a person or named maker (artist, architect, designer, potter...), else 0.

## Sections (groups)
- Each leaf gets an `axis` line stating how its groups are ordered, e.g. "by sub-school: Barbizon, Hague, ...; independents last" or "sub-types first, then centres, makers and representative works".
- Object-led and tradition-led leaves: use this vocabulary, in this order where present: **Sub-types · Schools & phases · Centres & workshops · Makers · Representative works · Sites · Building types** (Architecture: Sub-styles · Building types · Representative buildings · Architects). Do not invent other generic group names; specific attested names (a named workshop group, a dynasty-period phase name) are fine as groups.
- Artist-led leaves (movements, schools): group artists by **named sub-school, circle, group, colony, phase or generation** that the literature uses (e.g. Impressionism → "Batignolles group and founders", "American Impressionism", "Australian Impressionism (Heidelberg School)"...). Where no named grouping exists, the fallback group is the **country of activity** (just the country name, e.g. "Hungary"), and the axis says so. A group should usually hold 3–150 rows; split bigger ones.
- Order groups by affinity (founders/core first, followers, then national branches, then outliers).

## Viewing: every leaf must show the reader what to go and look at (owner, 2026-11-07)
"The weaknesses in visual art right now are especially prominent in non-named-artist-centric traditions like (non-modern) architecture, miniatures, etc. Someone reading this currently has no idea how to actually view them all."
So, for **every tradition-led leaf** (any leaf whose kinds are not mainly named artists: pre-modern architecture, manuscript and album painting, ceramics, textiles, metalwork, sculpture traditions, art in place, folk arts ...), whatever its size:
- **Representative works** group: 3–12 named, viewable works — buildings and sites ("Chartres Cathedral (Chartres, 1194–1220)"), manuscripts and albums ("Shahnama of Shah Tahmasp (Tabriz, c. 1525–35) — dispersed; Aga Khan Museum, Met"), objects ("Ardabil Carpet (1539–40) — V&A, London"). Gloss: place and date, holding museum or site, UNESCO status where it has one. Source: the object's museum page or the building's Wikipedia/Wikidata page. Prefer canonical works a reader can actually see or look up.
- **Where to see** group (is_maker 0): 2–6 holding collections or sites where the tradition is best seen ("Topkapı Palace Museum Library, Istanbul — Ottoman court manuscripts"; "Kyoto: Tō-ji, Daitoku-ji — Zen temple architecture").
- Put these two groups after the sub-types/centres groups and before makers in the order (the section vocabulary above extends to: Sub-types · Schools & phases · Centres & workshops · Representative works · Where to see · Makers ...).
- Use the gathered evidence, not only memory (read with Python, filter by the leaf's culture/style/tradition label; never cat whole files):
  - `data/interim/architecture_exemplars.csv` (style_label, label, country_label, inception, unesco_id, sitelinks, qid) and `architecture_nonwestern_exemplars.csv` (proposed_style, label, country, inception, unesco_site, qid) — buildings per style; prefer high sitelinks and UNESCO.
  - `data/interim/manuscripts_items.csv` (tradition, label, year, collections, sitelinks, qid) — named manuscripts per tradition.
  - `data/interim/in_situ_exemplars.csv` (tradition, site, place, date, unesco, qid) — sites for rock art, wall painting, mosaics.
  - `data/interim/regional/*_objects.csv` (title, culture/dynasty/period, institution, url) — museum objects with object-page URLs: Islamic, East Asia, South/Southeast Asia, Himalaya, Africa, Americas/Oceania, Smithsonian, folk, gap sweep. Pick titled objects (not "Fragment" or "Bowl" alone) from major institutions.
  - Source tag for rows from these files: `r3 <url>` (museum object page, or `https://www.wikidata.org/wiki/<qid>`).
- Artist-led leaves (movements) get one **Representative works** group of 3–8 canonical works with museum, placed before the artist groups.

## Rules
1. **Never lose a maker.** Every input row with is_maker=1 (or group Artists/Architects/Makers) must come out exactly once: in a leaf's `kinds` (yours or a new leaf), or in `moves_out` to an existing leaf outside your pass. Non-maker rows may be kept, merged, turned into `alias_rows` (an alternative name of the leaf itself, e.g. a museum culture label that just restates the leaf), or dropped with a reason (noise only: duplicates, a row that is not a kind of this leaf).
2. **Viewing** (above) applies to every tradition-led leaf. **Minimal leaves:** every leaf left with ≤ 4 kinds should get 3–10 well-attested new kinds (sub-types, centres, named makers, representative works with museum) where the tradition has them. Empty leaves need this most. If you truly cannot attest anything, leave it and say so in the summary.
3. **Catch-all buckets** (Modern Art, Contemporary Art, Academic Art, Modern Sculpture, Contemporary/Documentary/Straight Photography and the like): move each artist you can confidently identify into the named movement or school leaf they belong to (existing leaves: `taxonomy/r3/va_leaf_index.tsv`; use `moves_out` with the target code), or into a **new leaf** for an attested movement/school/group/colony with at least ~8 members in the data (e.g. Fauvism, Nabis, Hudson River School, Peredvizhniki, Nagybánya artists' colony, Mexican muralism — check the index first, many exist). The residual bucket keeps the rest, grouped as above. Use the evidence attached to artist rows (birth, countries, medium, Wikidata movements) plus your knowledge. Do not move an artist on a guess.
4. Keep leaf scope: a row that clearly belongs to another existing leaf may be moved with `moves_out`.

## Files
- Input: `taxonomy/r3/va_in/<pass>.json` → {"leaves": [{code, family, sub, sub_label, label, defn, aliases, see, n, alias_rows, rows}]}. Rows for artists carry a 6th element {birth, countries, medium, movements}; drop it in your output. Big files: read with Python, never cat whole.
- Leaf index: `taxonomy/r3/va_leaf_index.tsv` (all 1,599 leaves).
- Output: `taxonomy/r3/va_out/<pass>/result.json`:
```
{"leaves": {"<code>": {"axis": "...", "defn": "(optional improved definition)", "kinds": [[name, group, gloss, source, is_maker], ...], "alias_rows": ["..."]}},
 "new_leaves": [{"key": "NEW1", "sub": "A5", "label": "...", "breadth": "broad|medium|narrow", "defn": "membership test + examples", "aliases": "", "see": "", "src": [["https://en.wikipedia.org/wiki/...", "Wikipedia"]], "axis": "...", "kinds": [...]}],
 "moves_out": [["<name exactly as input>", "<from code>", "<to existing code>"]],
 "dropped": [["<from code>", "<name>", "<reason>"]]}
```
  Every input leaf must appear under "leaves" (even if unchanged). Rows within a group should be in a sensible order (by date for makers/works, canonical first for sub-types).
  Plus `taxonomy/r3/va_out/<pass>/summary.md` (≤ 40 lines): what you changed, new leaves, leaves you could not enrich, doubtful items.
- Run `python3 pipelines/r3/va_validate.py <pass>` and fix every ERROR; it must exit 0. Work in chunks with Python scripts you write inside your output directory (delete scratch files at the end). Write only in `taxonomy/r3/va_out/<pass>/`. Do not touch git or other files.
- Final reply: ≤ 15 lines: counts (kinds added, moved, new leaves), validator status, doubts.
