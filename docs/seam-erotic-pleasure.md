# Seam: Visual Entertainment ↔ Erotic Pleasure (decision record, 2026-10-28)

Owner request: examine the finished Visual Entertainment (VE) taxonomy (https://claude.ai/artifact/3i6kmC3zQdvQ5PL5ckrFQb, version 1793214456-723e) and decide which art forms belong there and which belong in EP. **Applied 2026-10-28** (owner: "make the changes to both taxonomies"), as ruling **S1** here and decision **D21** in the Pleasure Taxonomies. The rows for written, audio and game erotica are decided again with the Literature, Audio and Games taxonomies. Script: `pipelines/classify/seam_ep.py`.

## What each taxonomy classifies

- **VE** classifies works by what the work is: medium, form, genre, cycle, movement, tradition. It keeps a catalogue of makers and titles, read for the pleasure of looking and watching.
- **EP II-K** classifies the erotic practice of using media to be aroused, by ecosystem (D20). It names no titles (B16).

Overlap today:
- VE FT-A12 Erotic Film: Pink Film, Roman Porno, Erotic Drama, Sexploitation, Pornographic Film.
- VE FT-A3-4 Erotic Thriller, FT-A10-7 Teen & Sex Comedy, FT-C1-14 Erotic Drama Series.
- VE FT-E10-2 Ecchi and FT-E12-1 Hentai (77 titles).
- VE VA-B1 comics and manga (B1-3 American Comics includes underground comix; B1-9 Manga).

VE has nothing on shunga, pin-up, glamour, men's magazines or French postcards, and nothing on the amateur or creator trades.

## The rule (one test, applied in order)

1. **Explicit works made to arouse are EP.** This covers hardcore pornography and explicit anime, comics and art. Exception: an explicit work made and received as art cinema is placed by its genre in VE, with an EP pointer. This is VE's own rule AN8 applied to all of VE, not just anime.
2. **Non-explicit erotic works that film or art history names as a genre, cycle, movement or tradition, with its own makers and canon, are VE.** EP's leaf for the practice points to the VE codes and does not repeat them.
3. **Segments of the adult trade with no such canon are EP.** These are categories defined by how they are made and sold to arouse: channel, magazine tier, photo trade, creator economy, amateur exchange.
4. **The side that does not hold a category keeps one Finder row to its home.** Nothing is lost and nothing is duplicated (North Star 2, 5).

## Decisions by category

| Category | VE now | EP now | Home | The other side keeps |
|---|---|---|---|---|
| Studio pornography by era and channel | FT-A12-5 Pornographic Film (Golden Age features, 1 title) | II-K-1 (theatrical / home video / internet) | **EP** (rule 1) | VE: Finder row "pornographic film" → EP II-K-1; A12-5 retired |
| Amateur, creator and subscription content | — | II-K-13, II-K-14 | **EP** | VE: Finder rows |
| Erotic drama, erotic thriller, sexploitation, Euro-erotica / Emmanuelle softcore, pink film, Roman Porno, pinky violence, national sex comedies, teen sex comedy, erotic drama series | FT-A12-1…4, A2-6, A3-4, A10-7, C1-14 | II-K-15 sub-kinds | **VE** (rule 2) | EP: II-K-15 stays the practice of watching erotic film and TV for arousal; its genre sub-kinds become Finder rows to the VE codes |
| Late-night cable softcore, erotic anthology series, direct-to-video softcore | partly C1-14; channel is a VE filter | II-K-15 sub-kinds | **EP** (rule 3: trade channels, no canon) | VE: platform tag |
| Hentai (explicit anime) | FT-E12-1 (77 titles) | II-K-12 *Hentai anime & OVA* | **EP** (rule 1) | VE: E12 retired, Finder row → EP; the adult flag stays a VE filter |
| Ecchi (fan-service anime, non-explicit) | FT-E10-2 | ecchi as an explicitness tag | **VE** (rule 2) | EP: Finder "ecchi" → VE FT-E10-2 |
| Erotic manga, ladies' comics (redikomi), adult doujinshi, Rule 34 fan art, adult comics, Tijuana bibles, Western cartoon pornography, 3D/CG erotic animation | B1-9 Manga, B1-3 American Comics as general media | II-K-12 | **EP** (rules 1 and 3) | VE: B1-9 and B1-3 keep the media and see-also to EP |
| Underground comix | B1-3 kind | II-K-12 sub-kind | **VE** (a comics movement with a canon) | EP: Finder row → VE VA-B1-3 |
| Shunga | — (gap: not under B2-17 Ukiyo-e) | II-K-11 *Pre-photographic erotic art* | **VE** (rule 2: an ukiyo-e tradition with named masters) | EP: Finder row "shunga" → VE B2-17; VE should add shunga as a kind of B2-17 |
| Art nudes, erotic art looked at as art | painting, drawing and photography schools | II-K-11 aliases | **VE** | EP: Finder rows |
| French postcards, pin-ups and calendars, men's magazines, tabloid topless features, physique and beefcake magazines, glamour photography, thirst traps | — (J1-5 is fashion photography only) | II-K-11 kinds | **EP** (rule 3: the erotic photo trade) | VE: Finder rows; painted pin-up art may also be noted under VA-B1-5 Illustration |
| Adult animated features and series (Fritz the Cat) | FT-A15-4, C6-2 | — | **VE** | EP: none needed |
| Erotic ASMR, audio erotica | — | II-K-3 | **EP** | Decide with the Audio taxonomy (same test) |
| Written erotica, explicit fan fiction, erotic romance | — | II-K-2 | **EP** for the practice | Decide with the Literature taxonomy: a literary canon (classic erotica) may go there under rule 2 |
| Adult games, eroge | — | II-K-8.2 | **EP** for explicit (rule 1) | Decide with the Games taxonomy: games with sexual content go there |

## Effect on EP when applied

- II-K-15 keeps its leaf as the practice. Its genre sub-kinds become Finder rows to VE: sexploitation, national sex comedies, Euro-erotica and art-house, pink film, erotic thrillers. Its channel sub-kinds stay: late-night cable softcore, erotic anthology series, direct-to-video.
- II-K-11 loses *Pre-photographic erotic art* (shunga goes to VE) and the "art nudes" alias, and keeps the photo trade.
- II-K-12 loses *Underground comix*.
- **Owner decision needed when applying (CLAUDE.md):** II-K-11, II-K-12 and II-K-15 were confirmed with the owner (D20). Retiring their kinds is delegated work, but any change to a leaf itself goes to the owner first.

## Effect on VE when applied

- FT-A12-5 Pornographic Film and FT-E12-1 Hentai retire to Finder rows → EP. Their title lists leave VE, because EP names no titles.
- VE's own precedence rule AN8 is extended to all of VE.
- Shunga is added as a kind of VA-B2-17 Ukiyo-e.

## Published

- Visual Entertainment Taxonomy: https://claude.ai/artifact/3i6kmC3zQdvQ5PL5ckrFQb, version 3 (1793215548-90b3), 2026-10-28. `artifact/full/` in this repo holds the page and all 22 data files as published.
- Pleasure Taxonomies: https://claude.ai/artifact/N7rBgCKAyKhaBiAbqJS6Z5, version 21 (1793215515-6fe1), EP v6.4.
