# Proposed amendment to EP boundary rule B16 (for the Pleasure Taxonomies, v6.5)
Owner decision 2026-11-07: Model A stays, and B16's "no titles" clause is dropped so that the visual-media leaves can be mapped in full. The named entries are **makers**, not titles. This file is prepared in the VE repo and is applied in the Pleasure repo with its tools (`tools/media_ops.py`); this draft does not edit that repo.

## What changes
| Current B16 clause | Proposed |
|---|---|
| "…names a media title, character or platform only where that name is itself the attested term for a practice, and then only as an alias." | Named makers and platforms may be kinds or sub-kinds under the media practice leaves. Individual works are not entries. A work may be named only as an example inside a maker's gloss. |
| Kinds by line: one axis (era, medium or product); sub-kinds are channels or trade segments | Adds a second sub-kind axis, the **maker**. It sits beside the channel and segment sub-kinds of each era kind and never replaces them. Its group headings are the field's ecosystems, e.g. porno chic, gay theatrical era, gonzo, Japanese AV. |
| Seam sentence (D21) | Restated as ruling S3 under Model A: explicitness × the circuit at making; the art circuit wins on a mixed release; later fame does not move a work. |
| Unchanged | Media are not leaves. Using them is the practice. Explicitness is a graded note. The no-links rule stands: sources go in the attestation ledger and Appendix E, not the body. |

## Proposed text
> **B16 — Media are not leaves; using them is a practice; makers are named, works are not** (v6.2, D10, D18; v6.3, D20; v6.4, D21; v6.5, D22).
>
> The media are not entries: voice and sound, written text, image, live performance, the remote relay, and immersive or generated environments. The practices of consuming, making and exchanging media are leaves of II-K, each filed by what is done with the medium, and their names are aliases there. These practices are watching pornography, reading and writing erotica, listening to audio erotica, sexting and exchanging intimate images, phone and video sex, text role-play, connected toys used at a distance, virtual worlds and adult games, camming, AI companions, erotic photography and print, drawn and animated erotic media, and amateur and creator content.
>
> What a work depicts is the Context leaf it depicts, and imagining with no medium at all is Erotic Fantasising (II-B-14, D16). Explicitness is a graded note, not a leaf.
>
> Each media leaf is filed by ecosystem, with a Kinds by line naming one axis: usually the era, otherwise the medium or the product sold. Under each kind, two kinds of sub-kind may stand. The first is the channels or trade segments of that era, where a channel is itself what a buyer chooses. The second, since v6.5, is the **named makers** of that ecosystem. Makers are the directors, studios and labels of film and video; the photographers, publishers and magazines of print; the artists, studios, publishers and labels of drawn and animated media; and the platforms and notable creator collectives of the amateur, creator, cam, sexting, video-call, virtual-world, game and AI ecosystems. Makers are grouped under the field's own era and ecosystem headings and ordered by affinity.
>
> A maker is listed when the field's histories, halls of fame or trade press name it as part of the canon of its ecosystem. The long tail goes to the Finder. Individual works (films, scenes, magazines' issues, titles, characters) are not entries. A work may be named only as an example in a maker's gloss, at most two per maker.
>
> A named national tradition (pink film, commedia sexy) remains a sub-kind by the region rule, and a bare country label is the regional modifier. Whatever cuts across the kinds is a modifier (Appendix A), never a kind: release format, filming style, production standards, production mode, explicitness, audience, audio production.
>
> A kind needs fetched sources on two sites; a sub-kind, a maker included, needs one inside an attested kind (A1). Makers' sources are recorded in the attestation ledger. Outside Appendix E and that ledger the document contains no links.
>
> **Nothing is named that depicts anyone under eighteen, or that was made or shared without the consent of everyone depicted (B1, B2).** A maker or platform known chiefly for such material, or for illegal material, is not listed even when the field names it. Generated images of real people made without their consent are excluded.
>
> **The seam with Visual Entertainment** (Model A, VE ruling S3; D21, D22) decides on the work as made, by two questions: is it explicit, and was it made for the adult trade or for the art and mainstream circuit? Explicit work made for the adult trade is classified here, under its maker. Explicit work made for the art or mainstream circuit is Visual Entertainment's, placed by its genre. On a mixed circuit the art circuit wins, and later fame, acquisition or reissue does not move a work. Non-explicit erotic genres with their own canon are Visual Entertainment's. Adult-trade segments without one are here. The side that does not hold a category keeps a Finder row.
>
> Appendix E cites research sources by author and title, including a research programme's commercial name where that is how it is known, and community references (C-numbers) by name and web address.

## Consequences when applied
- New decision **D22** goes in STATUS.md and the change log (v6.5). An Appendix A note says that the maker axis is a sub-kind axis, not a modifier.
- The maker sub-kinds come from `ep_visual_porn_draft.json`. Each needs one fetched source to enter as a sub-kind, or two on different sites if promoted to a kind.
- New children II-K-9.1 and II-K-9.2 (II-K-9 has none) follow the append-only numbering. They change a leaf's structure, so they go to the owner first (CLAUDE.md).
- No owner-decided leaf or child is renamed or dropped.
