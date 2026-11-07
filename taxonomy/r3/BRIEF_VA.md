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

## Rules
1. **Never lose a maker.** Every input row with is_maker=1 (or group Artists/Architects/Makers) must come out exactly once: in a leaf's `kinds` (yours or a new leaf), or in `moves_out` to an existing leaf outside your pass. Non-maker rows may be kept, merged, turned into `alias_rows` (an alternative name of the leaf itself, e.g. a museum culture label that just restates the leaf), or dropped with a reason (noise only: duplicates, a row that is not a kind of this leaf).
2. **Minimal leaves:** every leaf left with ≤ 4 kinds should get 3–10 well-attested new kinds (sub-types, centres, named makers, representative works with museum) where the tradition has them. Empty leaves need this most. If you truly cannot attest anything, leave it and say so in the summary.
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
