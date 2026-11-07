# R3 pass `design`: summary

## What changed
- Built family **N Design** with 34 new leaves (12 under N1, 9 under N2, 13 under N3). Each leaf has a defn, src, `catalogues` (View all: MoMA, V&A, Cooper Hewitt collection searches, Designmuseum Danmark, Bauhaus-Archiv, HfG-Archiv Ulm, MAK Vienna, eMuseum.ch, Poster House, Isotype revisited, award databases such as Compasso d'Oro, G Mark, iF and Red Dot) and an axis that states its inclusion rule.
- Section order in every N leaf: Centres & workshops (firms) · Designed objects · Designers (split into named circles or phases, with country as the fallback).
  - Designed objects are named "Object (Designer, year)", with maker and holding collection in the gloss. The rule is objects held by MoMA, or by the leaf's named national collection, listed by date. About 355 objects in all.
- **N1 Furniture & Lighting:** Thonet Bentwood Furniture, De Stijl Design, Bauhaus Design, Union des Artistes Modernes, American Mid-Century Modern Design, Danish Modern, Italian Modern Design, British Modern Design, Pop Design, Radical Design, Memphis Group, Dutch Design (Goed Wonen, Droog, after Droog).
- **N2 Product & Industrial:** Wiener Werkstätte, Deutscher Werkbund, Streamline Moderne, Ulm School and Braun Functionalism, Scandinavian Modern (by country: Finland, Sweden, Denmark, Norway), Japanese Industrial Design, Automobile Design, Postmodern Design, Contemporary Industrial Design.
- **N3 Graphic:** Art Deco Poster, Constructivist Graphic Design, New Typography, Isotype, Swiss Style, New York School, Corporate Identity Design, Push Pin Studios, Psychedelic Poster Art, Album Cover Design, Japanese Graphic Design, Dutch Graphic Design, New Wave Typography.
- **I3-19 / I3-20:** 239 of the 692 designers moved into N leaves as Designers, with a new gloss each. 48 went by `moves_out` to existing leaves:
  - illustration and comics: B1-5, B1-3, B1-7, B1-8, B1-9
  - Studio Glass F1-10 (9) and Polish School of Posters B2-12
  - Mingei I3-18 (Shimaoka, MacKenzie, Kinjō), Kakiemon, Hopi and Pueblo pottery, Taxco silver, Drapo Vodou
  - art leaves: Pop, Funk, Surrealism, Black Arts, New Media
  - Contemporary Art (4 artists) and Modern Art A5-110 (1 nameless row)
- The remainder stays in I3-19 (244) and I3-20 (161) as residual designer-makers who fit no N leaf. They are grouped by field: craft furniture, studio ceramics, fibre art, art jewellery, fashion by country, costume and stage, others. Defns were rewritten to match, Vogue Runway, Met Costume Institute and V&A studio pottery were added as catalogues, and every row has a gloss.
- The I3-19 possession row "Scandinavian Modern" is now the kind "Georg Jensen silver" in the Scandinavian Modern leaf (Possession A3 link kept). The duplicate row is in `dropped`.
- 2 nameless input rows (b. 1927, US) were moved out to keep the maker count: the Funk-art one to A5-92, the other to A5-110.

## Doubts and suggestions for the coordinator
- **Overlaps:** Bauhaus Design overlaps I3-17 Bauhaus (1 row); consider merging I3-17 into it. Constructivist Graphic Design overlaps B2-11 Soviet Poster. I did not create Plakatstil or Polish School of Posters, because B2-10 and B2-12 already exist.
- **Fashion:** about 120 fashion designers stay in I3-19/I3-20. A Fashion Design leaf (for example under H7 Dress & Costume) would be their natural home. That is outside N, so I did not create it.
- **Wikipedia links:** I checked every added Wikipedia URL against the API.
  - Missing articles were replaced by the designer's, firm's or group's article. A few objects instead cite a MoMA, V&A or Stedelijk collection search: Plia, Krenit, the EM jug, the OXO peeler, Spotty, the Joe chair and the Revolt chair.
  - Dropped for lack of a confirmable page: Riki Watanabe, Gustav Siegel, Marcel Kammerer, Ugo La Pietra, Sigurd Persson, Anthon Beeke, Peter Murdoch, Magis, the Costanza lamp, Yamashiro's Forest.
- **Holdings:** for some Designed objects, the holding named in the gloss comes from my own knowledge (MoMA in most cases) and was not checked object by object. Check these: Thonet rocking chair, Café Museum chair, the WW Gitterwerk basket at the Met, and the AUTO list beyond MoMA's cars.
- **Non-designers kept:** some kept rows are not designers at all; Wikidata lists them under design. They are in "Other designers and artists" with honest glosses: Margot Fonteyn, Chris Eubank, Tony Esposito, Eka Kurniawan.
- **Uncertain placements:**
  - Placed but uncertain: Masuteru Aoba (Japanese Graphic Design) and Franco Teodoro (Pop Design, as co-designer of the Sacco).
  - Left as "Other" because I could not identify them: Johan van Loon, Bo Kristiansen, Randi Fisher, Salvador Terán, Jan Sylwester Drost, Klaar van der Lippe, Virgilio Forchiassin and a few others.
