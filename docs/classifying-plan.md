# Classifying plan: from gathered candidates to the published taxonomy

Decided 2026-10-28 with the owner. This is the brief for the classifying session(s); gathering (docs/sourcing-plan.md, docs/visual-art-plan.md) hands over candidates plus evidence.

## Owner decisions
1. **Purpose: a reference work, browsable.** Same family as the owner's Culinary, Possession and Pleasure taxonomies (published as claude.ai artifacts). Completeness and correctness of placement matter more than recommendation.
2. **Two tabs:** **Visual Art** and **Film & Television** (the latter includes anime, Asian drama and unscripted formats). Classification sorts each tab's candidates into nodes, as in the owner's other taxonomies.
3. **Review after publication.** The classifying session publishes the artifact; the owner reviews it and refines from there (rulings recorded as D-numbers, as in the Pleasure taxonomy).
4. **Naming: scholarly and attested,** so labels are searchable and free of invented phrasing. A label is the established term in the field (art-historical, film-historical, the trade's own term); every alias must be attested; coined terms never appear. Native terms are kept as aliases or in parentheses (Ukiyo-e, *wuxia*, Nihonga).
5. **Seam with the Erotic Pleasure taxonomy (ruling S1, 2026-10-28).** Explicit works made to arouse are classified in the Pleasure Taxonomies, not here; an explicit work made and received as art or mainstream cinema is placed by its genre. Non-explicit erotic genres and cycles with their own canon stay here; adult-trade segments with no canon are the Pleasure Taxonomies'. Retired: FT-A12-5 Pornographic Film (Caligula → A7-6) and FT-E12-1 Hentai (77 titles excluded); added: Shunga as a kind of VA-B2-17 Ukiyo-e. Record: docs/seam-erotic-pleasure.md; script: pipelines/classify/seam_ep.py.

## Conventions carried over from the owner's taxonomies
- **Page:** sticky top bar (title, tabs, search), left index with counts, main column, dark mode. A "How to place" guide tab with the placement keys.
- **Levels:** Tab → Family → Sub-family → Leaf → Kind (→ Variant). Nothing deeper.
  - Family: code, label, an italic **membership test** stated as what the thing *is*, optional key, notes.
  - Sub-family: code, label, an **axis** line ("Axis: ...").
  - Leaf: card with code, label, breadth (broad/medium/narrow), definition with examples, aliases, see also, kind count.
  - Kind: name, native name, gloss, region and period chips, synonyms, examples (representative works), source URLs/IDs.
- **Exactly one home per item,** decided by tests, not by names. A placement key where the first *yes* wins, plus precedence sentences for known seams.
- **Modifiers are not leaves:** region, period, country, studio/workshop location, venue and platform are tags and filters (a Region filter as in the Culinary page), never tree divisions. Named movements, schools and genres that happen to be national (Italian neorealism, Bengal School) are legitimate leaves because they are defined by what the work *is*.
- **Codes** stable and append-only between restructuring releases; retired codes are marked and never reused; a migration table when restructuring.
- **Ordering by affinity,** canonical form first, edge cases last; never alphabetical.
- **Attestation:** every node and alias traceable to a source (Wikidata QID, museum record, list, Wikipedia article). Gathered evidence columns carry this.
- **Audits before publication:** blind placement test (held-out items placed by a rater who sees only the keys), boundary/seam audit, coverage probes (blind, regional, naive phrasing), census.

## Tab 1: Visual Art
- **Families by medium/form** (what the work is): painting; sculpture; prints and drawings; book arts and calligraphy; ceramics; textiles and dress; metalwork and jewellery; woodwork, lacquer and furniture; glass; photography; architecture (by style; buildings as exemplars); art in place (rock art, wall painting, mosaics, geoglyphs, body art); new media, installation and performance.
- **Leaves:** traditions, schools, movements, workshops and styles (Attic red-figure; Kei school; Rajput painting, Pahari; Impressionism; Dansaekhwa; Benin court art; Khokhloma). Tradition-led cells (most of the non-Western and premodern world) have the tradition as the leaf and named makers as kinds under it; artist-led cells have artists as kinds under their movement or school.
- **Kinds:** artists (with primary medium; other media as see-also), sub-schools, ateliers, named workshops, sites (art in place), styles (architecture).
- **Region and period** are filters (the gathering grid: 20 world regions × antiquity / traditional / modern / contemporary), not families.
- **Inputs (data/interim):** artist selections (europe_1400-1900, modern_*, pre-1400 era, contemporary), tradition outputs (unattributed_cultures, regional/*traditions*, *_cultures, islamic_dynasties/schools, himalaya, europe_folk, world_folk, gap_sweep, world_extra), architecture styles (+ non-Western), manuscripts, in-situ, coverage grids.

## Tab 2: Film & Television
- **Families by form:** feature film; short film; television series (scripted); serial drama traditions (telenovela, dizi, daily soap: the long-running serial format node); anime (by format: TV series, film, OVA); Asian drama; unscripted formats (format families: talent competition, cooking, dating, social experiment, game show, makeover, docusoap, survival, talk).
- **Leaves:** genres, sub-genres, cycles and movements (film noir, giallo, Hong Kong heroic bloodshed, Italian neorealism, slow cinema, *jidaigeki*, *wuxia*, Korean revenge thriller, *iyashikei*, mecha), each with a membership test.
- **Kinds:** titles (one home each; see-also for secondary genres). Country, decade, studio, director are tags.
- **Inputs:** film (canon, Letterboxd estimates, regional top-up), TV routed, anime popularity, Asian drama selection, unscripted formats; genres from IMDb, TMDB (via MDBList), MAL genres/themes/demographics, MDL tags.
- **Content features needed for genre placement** (a gathering gap): TMDB keywords (check MDBList first), Wikidata genre/based-on/director links, short plot summaries from the Wikipedia bulk dumps (not the rate-limited API).

## Method
1. **Pilot first:** one Visual Art slice (the Islamic world: tradition-led, schools and dynasties) and one Film slice (Japanese cinema: genre clustering). Judge the keys and leaf granularity before scaling.
2. **Seed** leaves from attested labels (Wikidata movements/genres, museum culture/period/dynasty fields, MAL genres, regional sweep traditions, rule tables).
3. **Discover** what labels miss by clustering on content and shared people (directors, studios, writers, workshop members), then name each cluster only with an attested term.
4. **Place** every selected item with the placement key; record the key path.
5. **Audit** (blind placement, seams, coverage probes, census), then **publish**, then owner review.
