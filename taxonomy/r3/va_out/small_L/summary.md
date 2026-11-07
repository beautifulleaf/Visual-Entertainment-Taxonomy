# small_L: Art in Place, 127 smaller leaves (rock art, wall painting, mosaic and tile, geoglyphs, body art, floor and sand painting)

Built by `build.py` (engine), `spec.py` (which in_situ traditions feed each leaf, noise exclusions, section axis), and `ex_L1.py`/`ex_L2.py`/`ex_L3.py` (hand-written kinds, catalogues and handling of each input row). Run from the repo root: `python3 taxonomy/r3/va_out/small_L/build.py`.
## What changed
- 3,010 kinds in all (303 input rows): 2,424 are rule-based site/work rows from `data/interim/in_situ_exemplars.csv` (source: the Wikidata item), and about 510 are attested sub-types, phases, centres, sites from knowledge and makers (source: Wikipedia; a Wikipedia search URL where I was unsure of the exact article title).
- Sites rule, the same for every leaf: every gathered site of the tradition with a Wikipedia/Wikimedia article (sitelinks >= 1) or a UNESCO or national heritage listing. Where a leaf had more than ~300 qualifying rows, the rule was tightened one step at a time and the axis says so:
  - Rock Carvings in Tanum (L1-38): the Swedish Fornsök and Norwegian register records (c. 20,000 numbered entries such as "Tanum 72:4") inflate Western Europe. Tightened to "article or UNESCO", which leaves 245 sites. Tanum comes first, then Sweden, Norway, Denmark and the Finnish rock paintings.
  - Gobustan (L1-14): the ~1,050 numbered Azerbaijani register entries were left to the register. Cup and Ring Marks (L1-37): ~390 unnamed scheduled-monument entries were left out, keeping 36 named sites.
  - Levantine Rock Art (L1-35): ~650 UNESCO component shelters with no article of their own were left to the UNESCO list; the 124 shelters with an article are kept.
  - Pompeian Wall Painting (L2-32): ~560 single-sitelink fresco records were left out (sitelinks >= 2 or UNESCO).
- Sections follow each field's own axis:
  - Rock art: region of the tradition (Levantine and Schematic by autonomous community; Franco-Cantabrian by Vézère, Pyrenees, Rhône, Cantabria, Asturias...).
  - Sasanian reliefs: by dynasty.
  - Byzantine wall painting: by school (Komnenian Macedonia, Serbian, Kyivan Rus', Yaroslavl...).
  - Italian fresco: Trecento, Early, High and Late Renaissance.
  - Ceilings: by country, with the German lands split at 1730 (Baroque/Rococo).
  - Roman mosaics: by province. Mexican and Chilean muralism: by phase. Hill figures: by figure type. Nazca: biomorphs, geometric figures, Palpa, Paracas.
- Every leaf has 1-6 `catalogues` (379 in all): UNESCO WHL entries by id, the Bradshaw Foundation, TARA and the British Museum African rock art project, SHFA, Fornsök, Kulturminnesøk, Kyppi, Historic England, Canmore, POP, ICCD, NRHP, Theban Mapping Project, OsirisNet, IDP, Digital Dunhuang, Himalayan Art Resources, Archnet, MNAC, the Princeton Index, the Web Gallery of Art, CAIN murals, Wellcome, plus Wikipedia and Commons.
- Collections groups were computed where the gathered rows name a holding museum (Bardo, Naples, Palazzo Massimo...), with a few attested ones added (Warsaw Faras Gallery, British Museum Nebamun, Yale for Dura-Europos).
- Makers: all 59 input makers are kept. 53 ancient Greek painters (L2-31) are now grouped by school (Archaic, 5th century, Sicyonian, Theban-Attic, Ionian/Hellenistic, women painters in Pliny). Six Roman painters (Famulus, Fabius Pictor, Pacuvius...) moved inside the pass to Pompeian Wall Painting (L2-32). About 110 attested painters were added:
  - the muralists by generation, for Mexican muralism;
  - Roman Baroque, Bolognese quadraturisti and Central European painters, for ceilings;
  - Trecento to Mannerist painters, for Italian fresco;
  - Panselinos, Astrapas and Eutychios, Theophanes, Rublev, Dionisius, for Byzantine wall painting;
  - azulejo painters, Gaudí and Jujol, and tattooists such as Sailor Jerry, Horiyoshi III and Whang-od.
- 122 input rows were dropped with reasons: in_situ bucket labels whose sites are now expanded, and evidence rows that duplicate a catalogue site. Rows that restate the leaf became `alias_rows`.
- Noise excluded from source buckets, each stated in the axis: Dazu Buddhist cliff sculpture (L1-6), Korean rock-cut Buddhas (L1-7), Nikolay Polissky land art in Steppe Geoglyphs (L4-1), modern Moldovan and Turkish murals in Byzantine wall painting, Faras paintings re-routed to L2-35, and the colonial Northmead carvings and Gosford "glyphs" (L1-29).
- No new leaves and no moves out.
## Leaves still thin (<= 4 kinds; 31)
Attested additions were made, but little more could be confidently named for:
- Samchyky Painting (L2-48: 1 kind)
- Saura, Sohrai-Khovar, Imigongo, Murals of Revolutionary Nicaragua (3 each)
- Quinkan, Acre Geoglyphs, Blythe Intaglios, Sona (3 each)
- several body-art leaves (Deq, Mentawai, Kakiniit, Tā Moko, African Scarification)

The gathered data held no sites at all for Al-Qatt, the Indian folk wall paintings, Rangoli, Litema, Ndebele, Scottish ceilings, Northern Irish murals, Portuguese pavement, Gozan no Okuribi and the L6 leaves. Their sites come from knowledge, as the axes say.
## Doubts
- Galician petroglyphs (Atlantic art) arrive in the data under Iberian Schematic Art (L1-36), and the Finnish rock paintings under Tanum (L1-38). Both are kept as separate sections, labelled for what they are.
- Wall-painting site rows often carry the building's inception date, not the painting's date (for example Verdun Cathedral, c. 990). The glosses add the first named work where one exists.
- Sources for less certain titles are Wikipedia search URLs (for example Pema Fatya, Master of Pedret, Kumtura Caves). These are safe links, but not article links.
