# sweep_completeness: open named traditions from the completeness audit (V4)

Why these were open: the Met/AIC culture counts (`collections/in_col_met.csv`) were mapped to `missing:<tradition>` in the label mapping, but `missing_traditions.csv` was built from the per-object file only, so the R3 vetting pass (`va_out/missing_traditions`) never saw them. `collections_build.py` now carries those Met counts into `missing_institutions.json` (largest single label, because the Met's culture labels overlap).

Rule for every open tradition with >= 50 objects: a new leaf iff (1) an English Wikipedia article attests the name (web search, 2026-11-07), (2) >= 200 objects after de-duplicating overlapping labels, (3) the records show the medium, (4) no existing leaf covers it.

## New leaves (11)
E1 Ancient Cypriot Pottery; D5 Ancient Cypriot Sculpture; D1 Seljuk Stucco; E1 Predynastic Egyptian Pottery; E1 Paracas Pottery; G1 Byzantine Silver; G1 Etruscan Bronzes; G1 Roman Metalwork; G3 Ancient Egyptian Jewellery & Amulets; A1 Pala Painting (C2-5's Pala kind already said "pictures may later go to A1"); D5 Classical Javanese Sculpture.

## Held: attestation not confirmed from this environment (owner)
Mamluk Pottery (1,613 objects), Mughal Textiles (1,046; the Met key also holds codices and jewellery, medium unclear), Ancient Greek Bronzes (1,275), Sasanian Stamp Seals (961), Lydian Pottery (646; only the *Lydion* vase-shape stub found), Turkmen Jewellery (449), Vicús Metalwork (216), Kwoma Bark Painting (224).

## Below the object threshold (< 200 after de-duplication)
Bactria-Margiana Metalwork (193), Laconian Lead Figurines (186), Italic Bronzes, Mezcala Stone Sculpture, Tibetan Arms and Armour, Fon Metal Sculpture, Irish Cut Glass, Seville Pottery, Batak Sculpture, Dayak Sculpture, Gupta Sculpture (D5-2 Art of Mathura covers the Gupta phase), Shipibo-Conibo Textiles, Thessalian Neolithic Pottery, Shunga Art, Harappan Pottery, Chantilly Lace, Lyon Silk and smaller.

## Doubts
- Counts are Met culture counts; the Met's medium typing is coarse. Seljuk Stucco's labels also hold Seljuq ceramics and jewellery; Ancient Egyptian Jewellery's include jar labels and inlays. The holding-institution counts therefore overstate these leaves.
- Every source is an article or the section of one that treats the tradition; sub-type rows cite the same articles where the sub-type has none of its own.
