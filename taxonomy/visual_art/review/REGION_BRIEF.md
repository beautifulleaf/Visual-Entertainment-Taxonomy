# Visual Art region brief: design the leaves, place every row

You are building one regional slice of the Visual Art tab of a reference taxonomy (a browsable reference work in the style
of a museum's or encyclopedia's classification). Read `taxonomy/visual_art/review/va_tree.txt` first: the tab key, the 13
families (A Painting … M New Media) with membership tests, keys and sub-families (each with an axis), the leaves already
built in the pilot (Islamic world), the precedence sentences P1–P13 and the modifiers.

Your input: `taxonomy/visual_art/regions/<slice>_pool.csv`. Each row is a candidate gathered from museum and Wikidata
sources: pool_id, source, label, type, region, era, objects, medium, evidence, disposition. Rows whose `disposition` is
already filled (`exclude:below inclusion rule (§2.3)`) are done — skip them. Every row with an empty disposition must get
exactly one.

## The rules of the house (owner's rulings)
- Levels: Tab → Family → Sub-family → Leaf → Kind (→ Variant). A **leaf** is a named tradition, school, ware, workshop
  tradition or style **in one medium** (Benin brass casting, Kuba raffia textiles, Song celadon, Jōmon pottery, Pahari
  painting, Asante kente). A culture alone is never a leaf: its leaves are its traditions per medium (P12).
- **Kinds** under a leaf are its sub-types, centres, phases, sub-schools, workshops and named makers (D7: seeded from the
  object records — use the evidence columns: top cultures, sub-groups, kilns/workshops, named makers).
- **Dynasties, periods, places, centres, countries and cultures are filters, never nodes** (D2, P6, P7). A row that is a
  period label (Edo, Ming, Late Period, "Japan Edo") or a place/country bucket is `tag:period` or `tag:place` unless the
  field names a distinct school or ware after it (Arita ware, Kano school), in which case it is a leaf or kind.
- Ornament and motifs are tags (D6). Painting sub-families are by format (D5). Each named folk or ware tradition is its own
  leaf (D7).
- **Labels are scholarly and attested**: the established term in English (museum, encyclopedia or art-historical usage),
  native terms as aliases. Never coin a label. Every leaf needs an attestation: a Wikidata QID you are confident of, or an
  English Wikipedia article title, or a museum/encyclopedia URL. If you cannot attest a label, do not make the leaf: make
  the row a kind of a broader attested leaf, or an alias, or exclude it.
- Ordering by affinity (canonical first, edge cases last) — list your leaves in that order within each sub-family.
- Exactly one home per row.

## Dispositions (one per row with an empty disposition)
- `leaf:<L#>` — the row is the tradition the leaf stands for (it attests the leaf). `<L#>` is your temporary leaf id
  (L1, L2, …) or an existing pilot leaf code (e.g. `E2-7`).
- `kind:<L#>/<group>` — a kind under that leaf; `<group>` optional (e.g. `kind:L4/Asante`).
- `alias:<L#>` — another name of a leaf or kind already placed (no second node).
- `tag:period` / `tag:place` — a filter label (D2).
- `route:<family or slice>` — belongs to another family or slice (e.g. `route:VA-K` architecture, `route:islamic`,
  `route:south_asia`, `route:artist-led` for modern/contemporary named artists).
- `exclude:<reason>` — noise (trades, single artworks, non-art, archaeological tools, coins as currency, natural history),
  an umbrella term, or a duplicate.

## Outputs (write with Python's csv module into `taxonomy/visual_art/review/`)
1. `<slice>_leaves.csv`: `tmp,sub,label,breadth,defn,aliases,see,attest,note`
   - tmp: L1, L2 …; sub: an existing sub-family code (e.g. D5, H8, E1, K10, L1); breadth: broad / medium / narrow;
   - defn: one sentence stating what the tradition is, with 2–4 representative works or types in <i>…</i> where natural;
   - aliases: `;`-separated attested variants and native terms; see: related leaf labels or codes;
   - attest: `Q123` or `wiki:English Wikipedia title` or a URL.
2. `<slice>_disp.csv`: `pool_id,disposition,note` — one row per pool row you placed (the rows with empty disposition).
3. `<slice>_kinds.csv`: `tmp,kind,group,basis` — extra kinds seeded from the evidence (sub-groups, centres, kilns,
   workshops, named makers) that are not pool rows themselves. Keep it to kinds the evidence names; no invention.

Keep any scratch files in your own folder `/tmp/claude-0/va_<slice>/`. Do not edit any other repository file.
Reply with: leaves proposed (count per family), dispositions by type, and up to 5 problems for the owner (labels you could
not attest, seams between leaves, gaps in the families).

## Notes from the first slice (South Asia)
- Pictures in illustrated manuscripts are painting (P1): make an A1 leaf for a manuscript-painting tradition (e.g. Pala
  manuscript painting) rather than filing it under C2.
- Floor and ground designs (rangoli, kolam, sand painting) go to L6.
- Other slices may already have made a leaf you need: check `taxonomy/visual_art/review/*_leaves.csv` from finished
  slices and reuse their label (write it as a `route:<slice>` disposition with the label in the note) rather than making a
  duplicate leaf for the same tradition.
