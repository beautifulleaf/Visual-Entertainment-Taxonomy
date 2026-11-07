"""AAT reference sweep, part 5 (2026-11-07): leaves for open AAT clusters with a dedicated source, and the stone-tool
leaf the owner admitted to scope ("Yes to stone"). Sources found by web search on 2026-11-07.
"""
import json, os
W = "https://en.wikipedia.org/wiki/"
def k(name, group, note, url): return [name, group, note, "r3 " + url, 0]
def leaf(key, sub, label, defn, src, kinds, aliases="", see="", cat=None):
    return dict(key=key, sub=sub, label=label, breadth="narrow", defn=defn, aliases=aliases, see=see, src=src,
                catalogues=cat or [], axis="types and phases, then holding institutions", kinds=kinds)
AS = "https://www.archaeologysouthwest.org/2021/02/08/whats-the-point-all-about-clovis-points"
CC = "https://crowcanyon.org/EducationProducts/peoples_mesa_verde/paleoindian_artifacts.php"
L = [
 leaf("FLUTED", "D3", "Paleo-Indian Fluted Points", "The flaked stone projectile points of the Paleo-Indian period of North America (c. 13,000–8,000 BCE): Clovis, Folsom, Gainey, Cumberland and other fluted points, then the parallel-flaked lanceolate points of the Plano complexes (Agate Basin, Hell Gap, Cody, Scottsbluff), knapped from chosen jasper, chert, chalcedony and obsidian with a care for symmetry, colour and the full-length flute beyond any need of use.",
      [[W + "Folsom_tradition", "Wikipedia"], [AS, "Archaeology Southwest"], [CC, "Crow Canyon Archaeological Center"]],
      [k("Clovis point", "Sub-types", "large fluted point, c. 11,500–10,800 BCE", AS), k("Folsom point", "Sub-types", "flute almost to the tip", W + "Folsom_tradition"),
       k("Plano (parallel-flaked)", "Schools & phases", "unfluted lanceolate points of the late Paleo-Indian Plains", CC)],
      aliases="Clovis points; Folsom points; Fluted points; Paleoindian projectile points", see="D3-3 Chinese Jade",
      cat=[["https://www.britishmuseum.org/collection/search?keyword=Clovis", "British Museum collection search: Clovis", "Clovis points in the British Museum"]]),
 leaf("NYAU", "D4", "Nyau Masks", "The masks and costumes of the Nyau society of the Chewa of Malawi, Zambia and Mozambique, danced in the Gule Wamkulu ('great dance') at initiations, funerals and commemorations: carved and painted wooden face masks of spirits, animals and caricatured figures, and large basketry and straw structures; inscribed by UNESCO in 2005.",
      [["https://ich.unesco.org/en/RL/gule-wamkulu-00142", "UNESCO ICH"], ["https://www.emkp.org/documenting-the-endangered-mask-making-craft-of-the-gule-wamkulu-cultural-dance-among-the-nyau-secret-societies-of-malawi", "British Museum, Endangered Material Knowledge Programme"]],
      [k("Gule Wamkulu", "Schools & phases", "the masquerade", "https://ich.unesco.org/en/RL/gule-wamkulu-00142"), k("Kungoni Centre of Culture and Art, Malawi", "Holding institutions", "mask collection and museum", "https://www.emkp.org/documenting-the-endangered-mask-making-craft-of-the-gule-wamkulu-cultural-dance-among-the-nyau-secret-societies-of-malawi"), k("Kasiyamaliro", "Sub-types", "basketry animal structure", "https://www.emkp.org/documenting-the-endangered-mask-making-craft-of-the-gule-wamkulu-cultural-dance-among-the-nyau-secret-societies-of-malawi")],
      aliases="Gule Wamkulu masks; Chewa masks", see="D4-15 Chokwe Masks",
      cat=[["https://www.britishmuseum.org/collection/search?keyword=Nyau", "British Museum collection search: Nyau", "Nyau masks in the British Museum"],
           ["https://www.metmuseum.org/art/collection/search?q=Chewa", "The Met collection search: Chewa", "Chewa objects in the Metropolitan Museum"]]),
 leaf("VIGANGO", "D5", "Vigango", "Carved wooden memorial posts (singular kigango) of the Mijikenda of coastal Kenya, two to three metres tall, erected for deceased members of the Gohu society by the Giriama, Kauma, Jibana, Chonyi, Kambe and Ribe; incarnations of ancestors that may not be removed, many since returned from foreign museums.",
      [["https://www.culturalsurvival.org/publications/cultural-survival-quarterly/cultural-property-global-commodities-case-mijikenda", "Cultural Survival Quarterly (Udvardy, Giles, Mitsanze)"]],
      [k("National Museums of Kenya", "Holding institutions", "returned vigango", "https://www.culturalsurvival.org/publications/cultural-survival-quarterly/cultural-property-global-commodities-case-mijikenda"), k("Smithsonian National Museum of African Art", "Holding institutions", "", "https://www.culturalsurvival.org/publications/cultural-survival-quarterly/cultural-property-global-commodities-case-mijikenda"), k("Koma", "Sub-types", "short uncarved memorial pegs", "https://www.culturalsurvival.org/publications/cultural-survival-quarterly/cultural-property-global-commodities-case-mijikenda"), k("Gohu society", "Schools & phases", "", "https://www.culturalsurvival.org/publications/cultural-survival-quarterly/cultural-property-global-commodities-case-mijikenda")],
      aliases="Kigango; Mijikenda memorial posts",
      cat=[["https://www.metmuseum.org/art/collection/search?q=Mijikenda", "The Met collection search: Mijikenda", "Mijikenda objects in the Metropolitan Museum"],
           ["https://africa.si.edu/collection/search?edan_q=Mijikenda", "National Museum of African Art: Mijikenda", "vigango and Mijikenda objects at the Smithsonian"]]),
]
json.dump(dict(leaves={}, new_leaves=L, moves_out=[], dropped=[]), open(os.path.join(os.path.dirname(__file__), "result.json"), "w"), ensure_ascii=False, indent=1)
print(len(L), "new leaves")
