# small_H: Textiles, Carpets & Dress (318 smaller leaves)

## What changed
- **All 318 leaves** have been cleaned and sectioned, and each has an axis line. Groups used: Sub-types · Schools & phases · Centres & workshops · Named works · object-type works sections (Carpets and rugs, Garments and dress, Hangings and covers, Bags, baskets and containers, Fragments and samples, Other objects; tapestry and lace leaves use one "<Leaf> pieces" section) · Collections · Makers.
- **Machine rows removed.** "Gathered rows" restatements became alias_rows. Smithsonian culture rows became named sub-types or centres. Glosses were rewritten. Possession links are kept as "· Possession: X (A1)", with the URL in source.
- **643 knowledge kinds added** (sub-types, named weaves and patterns, centres, workshops and houses, makers, named works). Each new URL was checked on Wikipedia (HTTP 200). Unconfirmed rows fell back to the leaf's verified article or were dropped (58 dropped).
- **Works catalogue computed from regional/*_objects.csv** (per-leaf regex in spec.tsv plus post-filters in build.py).
  - Rule: named works with a Wikipedia or museum page, then every gathered object with a specific title and a museum page, up to 30 per leaf, earliest-dated first, by object type.
  - Totals: 3,283 object works and 15 named works.
- **Collections:** 500 rows in 207 leaves. Institutions are ranked by gathered object count: all with 10 or more, else the top 8.
- **Catalogues on all 318 leaves:** searches of the Met, V&A, British Museum, Cooper Hewitt, Cleveland, AIC, Smithsonian and Europeana. Also, where relevant: Europeana Fashion (dress), the Textile Museum (carpets), the Quilt Index (quilts) and the KCI Digital Archives (Japanese dress and dyeing).
- No moves out and no new leaves (no bucket leaf in this pass). 8 noise rows dropped.

## Leaves still at 4 kinds or fewer (126)
- **Village ICH elements with nothing attestable beyond the place:** Obukhovychi, Hlyniany, Serpanok, Stapar, Sjenica, Reshetylivka, Turiisk, Iza, Shchitky, Heinämaa, Kruunupyy, Pärekori, Bastabinne, Sigulda, Vidzeme, Bezdan, Raanu, Täkänä.
- **Others where no URL-confirmed named kinds were found:** Zhuang brocade, Xiang and Shu embroidery, Tekat, Telepuk, Daluang, Chaesang, Wanchojang, Kosovo-style, Zmijanje, Syrian-Armenian, Glória do Ribatejo, Quill embroidery, Divina Pastora lace, Sujani, Ralli, Khamak, Chakan, the Indian handloom saris, Faso Dan Fani, Basque linen and the knitting leaves.

## Doubts
- **Wikipedia check:** many expected titles returned 404 (Syon Cope, Dragon carpet, Marby rug, The History of the King, Simonetti carpet), so those were left out. Some leaves fall back to broader articles (Inca Empire, Ottoman art, Tapestry, Quilt).
- **Object matching is regex-based.** Borderline objects remain: some Dutch descriptive Tropenmuseum titles, and Goskatalog "people:X:embroidery" buckets for the Volga leaves. The "Ryukyuan weaving" bucket feeds both Shuri and Bashōfu.
- **Very large Smithsonian sets** (Plains beadwork, California basketry) dominate Collections counts.
- Some data-given rows were kept unverified: Kaymagli carpet, Armak weaving, U Paw Hnyun, the Bamana bogolan makers.
