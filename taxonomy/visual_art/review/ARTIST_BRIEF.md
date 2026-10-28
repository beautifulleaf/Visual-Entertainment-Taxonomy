# Visual Art: artist-led leaves (movements, schools, period styles)

Context: read `taxonomy/visual_art/review/va_tree.txt` (families, sub-families, precedence P1–P13, modifiers). The tab has
31,551 selected artists (`taxonomy/visual_art/artists.csv`: qid, label, birth, medium, media, region, era, sources,
movements as `QID:label|...`). Artists are **kinds** under leaves. A leaf here is a **named movement, school or period
style in one medium** (Impressionism in painting; Baroque sculpture; ukiyo-e in printmaking; Pictorialism in photography;
Bauhaus in design; Brutalism in architecture → K6). Owner's rule P11: an artist goes to the movement or school their work is
attested in; with no attested movement, to the **period-style leaf of their medium** — never to a country (region and
period are filters, D2).

Inputs:
- `taxonomy/visual_art/movements.csv`: the 675 Wikidata movement values (P135) of the selected artists: qid, label, n
  artists, median birth, media, regions, whether a gathering reference list kept it (modern_ref / contemp_ref), examples.
- `taxonomy/visual_art/artists_no_movement_cells.csv`: the 25,950 artists with no movement, counted by medium × region ×
  birth band (50 years). These need period-style leaves.
- Gathering reference lists already used for selection: Europe 1400–1900 period styles (Early Renaissance, High
  Renaissance, Northern Renaissance, Mannerism, Baroque, Dutch Golden Age, Rococo, Neoclassicism, Romanticism, Academic
  Art, Realism); modern and contemporary kept movements (in movements.csv `reference`).

Produce (Python csv module, into `taxonomy/visual_art/review/`):
1. `artist_leaves.csv`: `tmp,sub,label,breadth,defn,aliases,see,attest,note` — every leaf for artist-led cells.
   - `sub` is an existing sub-family: painting A5 (easel and its modern lineages), A2 (East Asian ink painting schools),
     A1 (manuscript/album: e.g. Rajput, Pahari are tradition-led, leave them to regions), A3 icons; B1 drawing, B2
     printmaking; D5 figurative sculpture; J photography (no sub-families yet: propose `J1 Photography` and use it);
     M new media (propose `M1 Installation & Performance`, `M2 Video & Digital Art`); design and decorative arts → the
     material family if clear, else propose `I3` (furniture, design) or note it; architecture → K4–K6 styles (P8).
   - Movements: keep a movement as a leaf when it is an attested art movement, school or style with enough members
     (as a rule ≥5 selected artists, or a gathering reference movement); artist groups, associations, exhibition
     societies and colonies (Les XX, Berlin Secession, Grez colony) become **kinds** (groups) under the movement or
     period-style leaf they belong to, not leaves. Merge synonyms (Baroque / Baroque painting). One leaf per medium:
     Impressionism in painting; an Impressionist sculptor goes to the sculpture period leaf with the movement as a tag.
   - Period-style leaves cover every medium × era the no-movement table needs, with attested names: e.g. painting:
     Gothic Painting, Early Netherlandish Painting, Italian Renaissance Painting, Northern Renaissance, Mannerism, Baroque
     Painting, Dutch Golden Age Painting, Rococo, Neoclassicism, Romanticism, Academic Art, Realism, ... Modern Art (as
     the period style of 1860–1945 artists with no movement), Contemporary Art (≥1945). Sculpture, prints, drawing and
     photography get their own period styles (e.g. Baroque Sculpture, Renaissance Sculpture, Pictorialism, Straight
     Photography, Contemporary Photography). Ancient Greek vase painters → the vase-painting leaves (Attic black-figure,
     red-figure, ...) in E1 (pottery decoration). East Asian painters → their school or lineage (Zhe school, Wu school,
     Kanō school, Rinpa, Nanga/Bunjinga, Maruyama–Shijō, Shanghai School, Lingnan School, Nihonga, Yōga ...), with a
     literati or court painting leaf where no school is recorded.
   - Labels attested (Wikidata QID, `wiki:` English Wikipedia title, or URL in `attest`). No coined labels.
2. `movement_map.csv`: `qid,label,disposition,note` — for every row of movements.csv: `leaf:<tmp>` (the movement is that
   leaf), `kind:<tmp>/<group name>` (an artist group under that leaf), `tag` (a period, a broad label such as
   "contemporary art", "modernism", "abstract art", "Orientalism" — a subject or umbrella that cannot be a home), or
   `exclude:<reason>` (not an art movement).
3. `period_rules.csv`: `medium,region,birth_from,birth_to,leaf,note` — ordered rules (first match wins) that send an artist
   with no usable movement to a period-style leaf. `medium` uses the values in artists.csv (painting, sculpture,
   photography, drawing and illustration, printmaking, design and decorative arts, architecture, vase painting, book arts,
   installation, performance and conceptual, video, new media and digital, street art and muralism, visual art
   (unspecified), ''). `region` may be `*` or one of the regions in artists.csv. Cover every cell of
   artists_no_movement_cells.csv, including unknown birth (use era) and unknown medium (treat as painting).

Keep scratch files in `/tmp/claude-0/va_artists/`. Edit no other repository file. Reply with: leaves by sub-family (counts),
movement dispositions by type, number of rules, and up to 5 problems for the owner.
