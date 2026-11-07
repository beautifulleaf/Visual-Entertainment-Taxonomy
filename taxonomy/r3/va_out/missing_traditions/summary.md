# missing_traditions: vetting of 108 collection labels (>= 50 objects)

- Outcome: 104 labels -> 91 new leaves (each with `collections_from`); 4 labels -> existing leaves (`merges.csv`). All 108 are covered exactly once (`check.py`).
- Merges: Māori pounamu carving -> D3-9 Hei-tiki (alias); Plateau beadwork -> H9-6 Plains Beadwork (section); Caddo pottery -> E1-70 Mississippian Pottery (section); Brazilian Colonial Painting -> D5-70 Brazilian Baroque (section; that leaf sits in sculpture, so the coordinator may prefer a new A5 leaf).
- Grouped labels: Flatstyle (Pueblo Painting + Native American Studio Painting + Kiowa Six; named school groups: San Ildefonso, Hopi, Kiowa Six, Studio, Bacone); Ostionoid Pottery (5 Ostionoid labels); Mixteca-Puebla Polychrome (+ Puebla-Tlaxcala); Yuman Pottery (Kumeyaay, Mojave, Quechan, + Maricopa < 50); Linen Damask (Haarlem + Kortrijk); Huichol Art (3 Huichol labels + yarn painting < 50); Wounaan and Emberá Basketry (2 labels).
- Families: E1 ceramics 46, D sculpture/masks 9, H textiles 22, G metal 6, I wood/lacquer 3, A 3, B/C 4, F glass 3.
- 352 kinds (sub-types, phases, centres/sites, 43 named makers); no object lists; collections attach from the index. Every Wikipedia URL was checked against the local enwiki title dump (data/enwiki-all-titles-in-ns0.gz); some kinds cite the culture article or a museum page when the sub-type has no article of its own.
- Catalogues: Smithsonian search (NMAI home of most labels), plus national hubs: Museo del Oro, Museos del Banco Central (Costa Rica), Museo Larco, Mediateca INAH, Museo Chileno de Arte Precolombino, Te Papa, ColBase, e-Museum Korea, Canadian Museum of History, BnF, Wereldculturen, Rijksmuseum, and a museum search.
- Thin leaves (1–3 kinds, few attested sub-types): Akawaio, Chachi, Ngäbe, Kali'na, Pamunkey, Susquehannock, Selin, Tierroid, Jama-Coaque, Nasca Textiles, Bahía, Karajá, Nuchu, Cherokee. Most of their value is in the holding institutions.

## Doubts / label noise (check before attaching collections)
- Kiowa Six (239) are Kiowa moccasins; Native American Studio Painting (1252) are mostly Navajo paint containers etc.; Pueblo Painting is mostly Hopi "Painting" records. They are attached to Flatstyle, but the object counts overstate it.
- Seri basketry objects are family E (pipe fragments); Great Basin and Wounaan basketry were also typed E; Haarlem/Kortrijk damask typed E (really H).
- Chinese bronze mirrors label includes Ming coins; Silla goldwork label includes Korean bells (covered by the leaf); Tibetan manuscript illumination is mostly BnF Dunhuang Tibetan items.
- Less firmly attested names: Selin Pottery (Selin period, NE Honduras), Tierroid Pottery (Tierra de los Indios style), Shiraz Glass (museum usage, no Wikipedia article), Kiribati Armour (museum sources only), Krobo Beads (from a "Ghanaian" glass-bead label).
- Scripts: build.py (writes result.json and merges.csv), check.py (coverage and URL check), titles.py, scan.py.
