# Seam: Visual Entertainment ↔ Possession (decision record, 2026-11-01)

Owner request: "Take and integrate everything the Possessions Taxonomy repo deferred to VE taxonomy." Applied 2026-11-01 as ruling **S2** here. Script: `pipelines/classify/seam_possession.py`. Row-by-row record: `taxonomy/seams/possession_handover.csv` (one row per handed-over item, with its decision and reason); new leaves: `taxonomy/seams/possession_new_leaves.csv`. Source: [beautifulleaf/Possession-Taxonomy](https://github.com/beautifulleaf/Possession-Taxonomy) `main` at `6991e3c` (2026-11-01), live page https://claude.ai/artifact/C1cQq1ygVd7bWfw7Duem6n.

## The rule (the owner's rubric, Possession BRIEF.md, 2026-10-31)

Ask of any tradition, in order:
1. **Can you buy it as a thing?** The product (a Persian rug, Murano glass, Harris Tweed cloth, a bonsai tree), its makers, sellers and protected names stay in **Possession**.
2. **Is it a way of making or decorating something to be looked at** (technique, style, school, motif, art form, artist lineage)? The tradition is **VE**. The Possession product links to it, and VE links back.
3. **Is it a way of using, consuming, wearing or keeping things?** It stays in **Possession** (or the Pleasure taxonomy for practices).

Related owner rulings in the Possession BRIEF that send things here: *Object, not content* (artists, works and movements of the art category belong to VE, 2026-10-31); *architectural styles are part of visual art* (property, 2026-10-31); *clothing traditions are artistic traditions* and *craft traditions in every category* (2026-10-31); *garden and flower design is deferred to VE* (2026-11-01); *museum design collections belong to VE* (2026-10-31; no rows handed over, see Open questions).

## What was handed over

| File in the Possession repo | Rows |
|---|---|
| `framework/handover/VE_craft_traditions.json` | 553 |
| `rebuild/work/V4_F2/ve_names.json` | 194 |
| `rebuild/work/V4_F2/ve_register.json` | 122 |
| `framework/handover/VE_A1_clothing_traditions.json` | 92 |
| `rebuild/reader/A1.json` | 85 |
| `rebuild/work/TRADITIONS_RETIRED/to_ve.json` | 13 |
| **Total** | **1059** |

The 85 named-cloth rows are the `ve` link-outs of the clothing category (A1); 44 of them repeat a cloth under several garments and take the first one's decision. Not handed to VE: brand deferrals (`verify/work/BRANDLAYER/DEFER_*.json`) go to the Interactive Entertainment and Literary taxonomies (game, book, music and magazine publishers); `IE_traditional_games.json` goes to Interactive Entertainment.

## Decisions

Every row was placed with the family key and precedence P1–P16 by eight placement passes (one per medium), then checked by the coordinator.

| Action | Meaning | Rows |
|---|---|---|
| `exists` | already here under the same or another name: the Possession name becomes an alias row ("Also gathered as") and a finder row | 395 |
| `kind` | a new kind of an existing (or new) leaf, with a one-line gloss, the Possession product and the source | 127 |
| `new_leaf` | a new leaf (the row is its first evidence row) | 180 |
| `finder` | a finder row routed to a leaf: works, named cloths, technique and material names | 270 |
| `decline` | not visual art under any family test: a product or a way of use, which stays in Possession by rubric questions 1 and 3 | 87 |

| Possession row | exists | kind | new_leaf | finder | decline |
|---|---|---|---|---|---|
| craft tradition | 217 | 87 | 141 | 40 | 68 |
| clothing tradition | 34 | 10 | 35 | 2 | 11 |
| garden & flower tradition | 0 | 2 | 4 | 5 | 2 |
| artist | 99 | 23 | 0 | 0 | 0 |
| work | 0 | 0 | 0 | 190 | 4 |
| named cloth | 45 | 5 | 0 | 33 | 2 |

### New leaves (178)
Codes are appended after the last code of each sub-family (append-only). Each rests on the item's own source page; two rest on seller or craft blogs and are marked in the scale-up note (Turkish Mosaic Lamp, Egyptian Hand-Blown Glass).

- **C Book Arts & Calligraphy**: C4-7 Oil-Paper Umbrella; C4-8 Fan Making; C4-9 Chōchin; C3-4 East Asian Bookbinding; C1-13 Korean Calligraphy; C4-10 Scherenschnitte; C4-11 Kirie; C4-12 Wycinanki; C4-13 Hanji.
- **D Sculpture & Carving**: D5-124 Garden Gnomes; D2-17 Torre del Greco Shell and Coral Carving; D3-11 Inkstone Carving; D5-125 Volterra Alabaster Carving; D3-12 Idar-Oberstein Agate Cutting; D5-126 Taxidermy; D5-127 Meerschaum Carving; D5-128 Thanjavur Dolls; D5-129 Erzgebirge Folk Art; D5-130 Dala Horse; D4-28 Punch and Judy; D4-29 Czech Marionettes; D2-18 Romanesque Ivories; D5-131 Brienz Woodcarving; D5-132 Val Gardena Woodcarving; D6-12 Butsudan.
- **E Ceramics**: E3-33 Banko Ware; E4-27 Hasami Ware; E3-34 Mino Ware; E1-95 Impruneta Terracotta; E1-96 Thrapsano Pottery; E1-97 Encaustic Tiles; E1-98 Kachelofen.
- **F Glass**: F1-11 Turkish Mosaic Lamp; F1-12 Swedish Art Glass; F1-13 Lauscha Glass; F1-14 Edo Glass; F2-3 Edo Kiriko; F1-15 Roman Micromosaic; F1-16 Egyptian Hand-Blown Glass.
- **G Metalwork, Arms & Jewellery**: G3-22 Temple Jewellery; G3-23 Thewa; G3-24 Tarakasi; G3-25 Hopi Silverwork; G3-26 Taxco Silver; G1-50 Jura Watchmaking; G1-51 Black Forest Clockmaking; G1-52 London Clockmaking; G1-53 Glashütte Watchmaking; G1-54 Comtoise Clockmaking; G1-55 Mora Clockmaking; G1-56 Wadokei; G1-57 Vienna Regulator Clockmaking; G1-58 Connecticut Clockmaking; G1-59 Moroccan Metalwork; G1-60 Nanbu Tekki; G1-61 Solingen Cutlery; G1-62 Thiers Cutlery; G1-63 Uchihamono; G1-64 Sheffield Cutlery; G2-7 Longquan Swords; G2-8 Khukuri; G2-9 Yumi; G2-10 Gakgung; G2-11 German Gothic Armour; G2-12 Japanese Armour; G1-65 European Scientific Instruments; G1-66 Nachiarkoil Lamps; G1-67 Western Silversmithing; G3-27 Kanzashi.
- **H Textiles, Carpets & Dress**: H4-94 Aran Knitting; H4-95 Gansey Knitting; H4-96 Fair Isle Knitting; H4-97 Lopapeysa; H4-98 Norwegian Knitting; H4-99 Cowichan Knitting; H7-13 Basotho Blanket; H4-100 Sukajan; H7-14 Savile Row Tailoring; H7-15 Neapolitan Tailoring; H3-41 Chanderi; H3-42 Maheshwari; H3-43 Mangalagiri; H3-44 Tangaliya; H3-45 Kasavu; H3-46 Kota Doria; H3-47 Nishijin-ori; H7-16 Qipao; H3-48 Acheik; H5-37 Khmer Silk Weaving; H4-101 Nyonya Kebaya; H7-17 Moroccan Caftan; H7-18 Tlemcen Wedding Costume; H4-102 Majboud Embroidery; H4-103 Hausa Embroidery; H3-49 Shemma; H7-19 Highland Dress; H3-50 Oaxacan Textiles; H7-20 Pollera; H5-38 Shweshwe; H5-39 Indian Ikat; H3-51 Tartan; H3-52 Tweed; H3-53 Faso Dan Fani; H8-40 Wayuu Weaving; H8-41 Kiondo; H1-12 Chinese Carpet; H1-13 Tibetan Rug; H1-14 Savonnerie Carpet; H3-54 Welsh Tapestry; H3-55 Trade Blankets; H3-56 Peshtemal; H3-57 Irish Linen; H3-58 Basque Linen; H5-40 Rajasthani Block Printing; H5-41 Indiennes; H4-104 Crewelwork; H4-105 Stumpwork; H4-106 Berlin Wool Work; H10-1 Jutti; H8-42 Skep; H10-2 Western Leatherwork; H10-3 Moroccan Leatherwork; H8-43 Nantucket Lightship Baskets.
- **I Woodwork, Lacquer & Furniture**: I3-21 Bezalel School; I3-22 Shaker Furniture; I3-23 Chinese Classical Furniture; I1-24 Essaouira Thuya Marquetry; I1-25 Kashmir Walnut Wood Carving; I1-26 Jepara Wood Carving; I3-24 Tansu; I3-25 Bandaji; I1-27 Magewappa; I1-28 Tendō Shōgi Koma; I4-2 Spanish Guitar; I4-3 Djembe; I4-4 Mbira; I4-5 Violin Making; I4-6 Tanpura; I4-7 Saraswati Veena; I4-8 Celtic Harp; I4-9 Cimbalom; I4-10 Santur; I4-11 Appalachian Dulcimer; I4-12 Kantele; I4-13 Koto; I4-14 Guzheng; I4-15 Erhu; I4-16 Taus and Dilruba; I4-17 Sarangi; I4-18 Hardanger Fiddle; I4-19 Nyckelharpa; I4-20 Accordion; I4-21 Bagpipes; I4-22 Gagaku Instruments; I4-23 Mechanical Musical Instruments; I1-29 Vardo; I1-30 Danish Freehand Pipes.
- **K Architecture**: K12-8 British Vernacular Architecture; K12-9 German Vernacular Architecture; K12-10 Kulla; K12-11 Vainakh Tower Architecture; K12-12 Spanish Vernacular Architecture; K12-13 Italian Vernacular Architecture; K12-14 American Vernacular Architecture; K9-14 Malay Traditional House; K7-18 Haveli; K12-15 Nordic Log Architecture; K7-19 Kashmiri Houseboat; K12-16 Swiss Farmhouse Architecture; K12-17 French Vernacular Architecture; K12-18 Cycladic Architecture; K12-19 Chattel House; K7-20 Assam-type House; K12-20 Queenslander; K14-1 Bonsai; K14-2 Penjing; K14-3 Hòn Non Bộ; K14-4 Ikebana.

### Coordinator overrides
- **Taxidermy** (Victorian cased and anthropomorphic taxidermy; Indian trophy studios): the placement pass declined both, but the owner names taxidermy among the artistic traditions sent here. New leaf D5-126 Taxidermy, with Indian trophy taxidermy as a kind.
- **Sheridan-style leather carving**: proposed as its own H4 leaf and also named inside the new H7-21 Western Leatherwork leaf; one home, so it is a kind of H7-21.
- **Ikebana** was proposed by two passes; one leaf (now K14-4).
- Two broken see-also codes found on the way are fixed: H4-46 and H4-92 now point to H4-93 Quilts of Gee's Bend (were T158 and H4-91).

### Back-links (precedence S2)
A leaf whose tradition makes products that Possession files names them at the end of its *See also* line ("Possession taxonomy: Persian rug (B2 Soft Furnishings)."); kinds carry the product in their gloss. `tree_visual_art.py` adds these from the hand-off CSV, so a full rebuild keeps them; the finder rows for works and Possession names are re-added by running the seam script after a rebuild, as with S1.

### Declined: kept out of VE
These rows are products or ways of use (rubric questions 1 and 3), or garment types (P10), so VE gives them no node; Possession already files the objects. Nothing is deleted: each row keeps its reason in the CSV, and any of them can still be taken into VE.

| Possession row | Category | Reason |
|---|---|---|
| Espadrille making | A2 | footwear: a garment type, not an art tradition (P10); the plaited esparto sole is a product craft that stays in Possession |
| Swedish clog making | A2 | P10: a footwear/garment type, not an art tradition; the product and its makers stay in Possession (plain work clog, wooden sole, leather upper; no named decorative tradition) |
| Mexican huarache making | A2 | P10: a footwear/garment type, not an art tradition; the product and its makers stay in Possession (braided-strap sandal) |
| Japanese geta and zōri making | A2 | P10: a footwear/garment type, not an art tradition; the product and its makers stay in Possession (geta and zori are footwear types) |
| Kolhapuri chappal craft | A2 | P10: a footwear/garment type, not an art tradition; the product and its makers stay in Possession (GI-protected sandal type; braiding and punching are techniques, a tag) |
| Peshawari chappal (kheri) craft | A2 | P10: a footwear/garment type, not an art tradition; the product and its makers stay in Possession (moulded sandal type) |
| Dutch klompen making | A2 | P10: a footwear/garment type, not an art tradition; the product and its makers stay in Possession (whole-wood clog; painted examples are folk decoration with no VE leaf to hold them) |
| Russian valenki felting | A2 | felt boots: a garment type, not an art tradition (P10); plain utilitarian felting with no decorative tradition the field names |
| Inuit and Yup'ik skin boots | A2 | P10: a footwear/garment type, not an art tradition; the product and its makers stay in Possession (mukluk/kamik footwear type; tech records no decoration) |
| Balkan opanci making | A2 | P10: a footwear/garment type, not an art tradition; the product and its makers stay in Possession (peasant shoe type of Balkan folk dress; spans several costume traditions) |
| Galway Claddagh making | A3 | owner 2026-11-01: object-named leaves become finder rows; no Irish goldsmithing leaf to route the Claddagh ring to; the ring is Possession's (A3) |
| Randoseru | A4 | rubric 1: a school-bag product; no decorative tradition |
| Paris trunk-making (malletier) | A4 | rubric 1: travel-trunk products and their houses (malletiers, brands) stay in Possession; no VE decorative tradition |
| Soviet watchmaking | A5 | owner 2026-11-01: object-named leaves become finder rows; Soviet industrial watchmaking has no decorative school; the clock traditions are now G1 school leaves |
| Walsall saddlery | B10 | Walsall is a manufacturing centre of plain English saddlery and bridlework; centres are evidence (P7), no decorative tradition |
| Tree beekeeping culture | B10 | rubric 3: a way of keeping bees (UNESCO practice); carving the hive is utilitarian, not made to be looked at |
| Australian stock saddlery | B10 | functional stock saddle derived from the English park saddle; no decorative tradition |
| Majlis | B1 | a reception room and its social use (rubric 3); its painted decoration is already VE L2-3 Al-Qatt Al-Asiri, link there |
| Charpai rope-bed weaving | B1 | utilitarian rope bed; the bias weave is a technique and the bed an object type (tags); no decorative tradition attested |
| Imabari towel | B2 | an industrial terry-towel district and certified brand: a product and its makers (rubric 1), no made-to-be-looked-at tradition |
| Villedieu-les-Poêles copperwork | B5 | Utilitarian copper cookware; no decorated or made-to-be-looked-at tradition is studied; pans and maker (Mauviel) stay in Possession. |
| Kyoto natural whetstones (tennen toishi) | B5 | Natural whetstones are quarried stone tools; nothing is made or decorated to be looked at. |
| Molcajete stone carving | B5 | Molcajete making produces a basalt grinding tool; no made-to-be-looked-at tradition under D (carving for its own sake) or any other VE test; stays a Possession product craft |
| Takayama chasen | B5 | functional bamboo tea whisk; no made-to-be-looked-at tradition (the tea practice is a way of using things, rubric 3) |
| Tula samovars | B5 | owner 2026-11-01: object-named leaves become finder rows; no Russian brass or metal-vessel leaf to route Tula samovars to; the samovar is Possession's (B5) |
| Edo kibashi | B5 | plain hand-planed chopsticks; no decorative tradition |
| Japanese natural whetstones | C1 | Natural whetstones are quarried stone tools; nothing is made or decorated to be looked at (same as P0162). |
| Swedish axe forging | C1 | Utilitarian forged axes; no decorated tradition studied; makers (Gränsfors, Hults, Wetterlings) stay in Possession. |
| Opinel and Savoie knives | C1 | A single brand's plain folding knife (Opinel); maker and product stay in Possession; no attested Savoie decorative tradition. |
| Japanese carpentry tools (daiku dōgu) | C1 | rubric 1/3: hand tools are products; Japanese joinery is a technique tag on the K8 Japanese architecture leaves |
| Austrian scythe-smithing | C2 | Utilitarian agricultural blades (scythes); heritage of a trade, not a decorated or made-to-be-looked-at tradition. |
| British regional billhook patterns | C2 | Regional patterns of utilitarian edge tools (billhooks); no decorated tradition. |
| Celluloid pen making | C5 | Industrial turning of celluloid pen bodies; a manufactured writing instrument, no VE family test fits; stays in Possession |
| Étival papermaking (Clairefontaine) | C5 | A paper mill and stationery brand (Clairefontaine); industrial papermaking with no made-to-be-looked-at tradition; maker stays in Possession |
| Chinese zhusuan | C5 | Abacus calculation is a mental and practical technique, not visual art; no VE family test fits |
| Banshu soroban | C5 | Abacus making is instrument making for calculation, not decorated or made to be looked at |
| Scandinavian linseed oil paint | C8 | a paint product and building-maintenance practice; the technique is a tag and VE holds no Scandinavian vernacular building leaf to carry it |
| Go equipment making | E1 | game equipment (boards, stones, bowls); no decorative tradition |
| Xiangqi set making | E1 | game equipment (engraved discs); no decorative tradition |
| Mahjong tile making | E1 | game equipment; carved bone-and-bamboo export sets are a collectors' product, no recognised art tradition |
| Austrian tarock card making | E1 | owner 2026-11-01: object-named leaves become finder rows; no leaf for European playing-card printing; the pack is Possession's (E1) |
| Kendama | E1 | skill toy of turned wood; no decorative tradition |
| Beigoma | E1 | cast-metal battle tops; no decorative tradition |
| Hurley making | E2 | sporting equipment; no made-to-be-looked-at tradition |
| English willow bat-making | E2 | sporting equipment; no made-to-be-looked-at tradition |
| Split-cane rod making | E2 | fishing tackle; precision craft, not made to be looked at |
| Swiss wooden sledge making | E2 | sporting sledges; no decorative tradition |
| London hand-made pointe shoe making | E2 | dance footwear (P10); purely functional |
| Miyakonojō bokken making | E2 | wooden training swords; not studied as decorated arms (G2) |
| Turkish hand-hammered cymbal making | E3 | Cymbals are studied for sound, not as decorated objects (I4 test); makers stay in Possession. |
| Chinese cymbal making | E3 | Cymbals are studied for sound, not as decorated objects (I4 test). |
| Afro-Cuban drums | E3 | staved, plain-shelled drums studied as music, not as decorated objects (I4 test) |
| Afro-Peruvian cajón | E3 | plain box drum studied as music, not as decorated objects (I4 test) |
| Hindustani tabla | E3 | studied through playing gharanas, not as decorated objects (I4 test) |
| Irish bodhrán | E3 | frame drum studied as music, not as decorated objects (I4 test) |
| Himalayan singing bowls | E3 | modern trade item of bell metal; no attested decorative tradition (G1 or I4) |
| Kodo (way of fragrance) | F4 | Kōdō is the appreciation of incense by smell, a way of using things; nothing made to be looked at |
| Birch-bark canoe building | G1 | boatbuilding studied as craft and naval architecture, not as decorated objects |
| Greenland kayak | G1 | boatbuilding studied as craft and naval architecture, not as decorated objects |
| Aleut baidarka | G1 | boatbuilding studied as craft and naval architecture, not as decorated objects |
| Bodrum gulet building | G1 | boatbuilding studied as craft and naval architecture, not as decorated objects |
| Colin Archer double-enders | G1 | boatbuilding studied as craft and naval architecture, not as decorated objects |
| Wheelwrighting | G1 | functional wheel-building trade; no decorative tradition |
| Coachbuilding (horse-drawn) | G1 | carriage-building trade; decorated state coaches fall under I3 period styles by their designers, the trade itself is not a tradition to look at |
| Dacha | G2 | a dacha is a use and building type (second home), not a style or made-to-be-looked-at tradition; dachas are built in any idiom (rubric 3) |
| Russian stove | G3 | the brick Russian stove is a heating and cooking appliance (mechanism), not made to be looked at; tiled stoves as decorated objects are already E1-85 Izraztsy |
| Japanese tsuge comb-making | H1 | plain boxwood comb; no decorative tradition (carved lacquer kushi would be a separate tradition) |
| Saint-Claude briar pipes | J10 | Saint-Claude is a manufacturing centre of briar pipes; centres are evidence (P7) |
| Marinière (French naval striped knitwear) | A1 | Garment type (striped sailor jersey fixed by naval regulation) made on industrial knitting mills; P10: garment types belong to Possession, no knitting tradition to place. |
| Wakayama loopwheel (tsuriami) knitting | A1 | Industrial machine process (loop-wheel jersey for sweatshirts), no decorative or made-to-be-looked-at tradition; the cloth and its makers stay in Possession. |
| Japanese selvedge denim (Kojima / Sanbi) | A1 | Industrial denim production on shuttle looms and reproduction jeans: a manufacturing method and product, not a visual-art tradition; stays in Possession. |
| Bisht | A1 | P10 garment type (men's cloak, like abaya and ghutra) belongs to Possession; no VE dress or embroidery leaf to hold it. Doubt: Hasawi bisht skills UNESCO 2025. |
| Burnous | A1 | P10 garment type (hooded wool cloak of the Maghreb) belongs to Possession; no decorative tradition named. |
| Rubberised mackintosh cloth | A1 | Rubberised cotton coat making is a manufacturing technique with no made-to-be-looked-at tradition; product and maker stay in Possession. |
| Béarnais beret making | A1 | Felted beret making is a manufacturing craft for a garment type (P10); no decorative tradition; stays in Possession. |
| Hebron keffiyeh weaving | A1 | P10: the keffiyeh (shemagh) is a garment type kept in Possession; mechanised factory weaving, no separate tradition to place. |
| Lovikka mitten knitting | A1 | P10 garment type: a plain thick mitten made to one maker's pattern, no decorative tradition; stays in Possession. Doubt: could join a Swedish knitting leaf if one is made. |
| Poncho salteño weaving | A1 | P10: the poncho salteño is a garment type and emblem (plain red panels with black bands), with no decorative weaving tradition named; stays in Possession. |
| Bleu de travail (French workwear) | A1 | Industrial work clothing (cut-and-sewn drill and moleskin), a garment type with no decorative tradition (P10); stays in Possession. |
| Marimo culture of Lake Akan | C3 | marimo are a naturally occurring alga protected as a natural monument; the Ainu festival is a custom; no made-to-be-looked-at tradition |
| Dutch bulb growing | C3 | commercial bulb agriculture (the product stays in Possession); no design canon. Doubt: the Keukenhof show garden could be a finder to K13-7 |
| BILD poster (IKEA) | F2 | Retail brand and seller of mass-produced prints (Possession); no made-to-be-looked-at tradition of its own. |
| Posters and prints (Desenio) | F2 | Retail brand and seller of mass-produced prints (Possession); no made-to-be-looked-at tradition of its own. |
| Art prints and framed prints (King & McGaw) | F2 | Retail brand and seller of mass-produced prints (Possession); no made-to-be-looked-at tradition of its own. |
| Art prints, canvas prints and framed posters (Society6) | F2 | Retail brand and seller of mass-produced prints (Possession); no made-to-be-looked-at tradition of its own. |
| Khadi | A1 | Plain hand-spun, hand-woven cloth whose significance is economic and political (Gandhi), with no decorative tradition; stays in Possession. Doubt. |
| Khadi | A1 | Plain hand-spun, hand-woven cloth whose significance is economic and political (Gandhi), with no decorative tradition; stays in Possession. Doubt. |

## Owner follow-up (2026-11-01)

Asked about the open questions of the first pass, the owner answered:
1. **Plant and floral arts: yes.** New sub-family **K14 Plant & Floral Arts** (axis: tradition) in the Architecture family beside K13 Gardens: K14-1 Bonsai (with saikei and kokedama), K14-2 Penjing, K14-3 Hòn Non Bộ, K14-4 Ikebana. Family key step 1 and the K key name it.
2. **Leatherwork: yes.** New sub-family **H10 Leatherwork** (axis: tradition): H10-1 Jutti, H10-2 Western Leatherwork (with Sheridan-style carving), H10-3 Moroccan Leatherwork. H4-82 Tatar Leather Mosaic, sewn as a textile, stays in H4 (the H10 axis says so); bindings stay C3, shadow puppets D4.
3. **Leaves named after an object become finder rows: "Sure".** Kiseru → G2-4 Japanese Sword Mountings, Staunton chessmen → I3-13 Victorian Decorative Arts, Windsor chair → I3-3 Chippendale Furniture (Georgian furniture), Hanafuda → B2-17 Ukiyo-e. Tula samovars, the Claddagh ring and the Industrie und Glück tarock have no tradition leaf to route to and are declined. *Clocks and Watches* and *Cutlery* held named regional schools, and the owner sends clock and watchmaking here, so instead of a finder row each gave way to its schools as leaves: G1-50 Jura Watchmaking (UNESCO 2020), G1-51 Black Forest, G1-52 London, G1-53 Glashütte, G1-54 Comtoise, G1-55 Mora, G1-56 Wadokei, G1-57 Vienna Regulator, G1-58 Connecticut clockmaking; G1-61 Solingen, G1-62 Thiers (with the Laguiole knife) and G1-64 Sheffield Cutlery. Soviet watchmaking, an industry with no decorative school, is declined.
4. **"What do you mean back to VE? This is VE."** Correct: the declined rows are not moved anywhere. They are the rows VE turned away as products or ways of use; they stay listed below so that any of them can still be taken in.
5. **Design section: yes, structure only, no gathering now.** New family **N Design** (membership test: an object or graphic designed for serial production and held as a landmark of its field by a design collection or a major design award, placed by the design movement or school that canonised it; the designed object is the kind). Sub-families N1 Furniture & Lighting Design, N2 Product & Industrial Design, N3 Graphic Design, each with axis *design movement or school* and no leaves yet. Family key step 3 sends designs for serial production to N; precedence **P17** separates N from I3 (period styles of furniture and the decorative arts keep their designers while N is gathered), B2 (posters made as prints), C1-12 (typefaces) and the studio crafts. Sources for the later gathering: MoMA (Architecture and Design), the V&A, Cooper Hewitt, the Design Museum (London), the Vitra Design Museum, Die Neue Sammlung, the ADI Design Museum (Compasso d'Oro) and Red Dot Best of the Best; a design enters on a fetched page showing it held or awarded (the rule the Possession taxonomy set for design landmarks).

The page's lede now counts the families instead of saying 13.

## Still open
1. **Region-named vernacular leaves.** K12-8/9/12/13/14/15/17 group house types under a country (British, German, Spanish ... Vernacular Architecture), where VE elsewhere makes single house types leaves.
2. **Comics publishers** went with the Literary hand-off, although VE holds comics (VA-B1-3, B1-9); they are publishers, not artists, so nothing moves unless the owner says so.
3. **Fixes the passes noticed, not made**: the Lalique glass kind sits under I3-12 Biedermeier; Seto Ware (E3-15) holds Mino-kiln kinds now that Mino Ware has its own leaf; C4-1 Ebru covers only Ottoman and Iranian marbling; H1-11 Ryijy is Finnish only, though Swedish and Norwegian rya point to it.

## Published

- Visual Entertainment Taxonomy: https://claude.ai/artifact/3i6kmC3zQdvQ5PL5ckrFQb, version 4 (1793569636-302f), 2026-11-01, with S2 and the owner follow-up. `artifact/full/` in this repo holds the page and all 23 data files as published (`m-va-N.json` is new).
