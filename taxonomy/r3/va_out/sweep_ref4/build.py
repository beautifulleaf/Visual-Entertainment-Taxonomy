"""AAT reference sweep, part 4 (2026-11-07): leaves for traditions revealed by the Smithsonian Open Access lookup
(pipelines/r3/ref_si_fetch.py) of the AAT peoples with no gathered records. Attested by Britannica and a museum
exhibition found by web search. Held: Konso waga memorial figures (not confirmed from this environment).
"""
import json, os
BRIT = "https://www.britannica.com/art/African-art/Other-visual-arts"
def k(name, group, note, url): return [name, group, note, "r3 " + url, 0]
L = [
 dict(key="GRASSFIELDS", sub="D5", label="Cameroon Grassfields Sculpture", breadth="medium",
      defn="The court art of the some two hundred kingdoms and chiefdoms of the Cameroon Grassfields (Bamileke, Bamum, Bangwa, Kom, Bafut, Nso, Mankon, Tikar): lefem commemorative figures of rulers, beaded thrones and stools with leopards, carved palace pillars and house posts, buffalo and elephant masquerade helmet crests, brass pipes and drinking horns.",
      aliases="Cameroon Grasslands art; Bamileke sculpture; Bamum art", see="H5-29 Ndop Cloth",
      src=[[BRIT, "Britannica: African art"], ["https://artgallery.qcc.cuny.edu/exhibits/powerful-arts-of-cameroon", "QCC Art Gallery, Powerful Arts of Cameroon"]],
      catalogues=[["https://www.metmuseum.org/art/collection/search?q=Grassfields", "The Met collection search: Grassfields", "Grassfields objects in the Metropolitan Museum"]],
      axis="kingdoms (Bamum, Bamileke, Kom, Bangwa ...), then object types and holding institutions",
      kinds=[k("Lefem commemorative figure", "Sub-types", "portrait of a ruler", "https://artgallery.qcc.cuny.edu/exhibits/powerful-arts-of-cameroon"),
             k("Beaded throne", "Sub-types", "seat of office with leopard support", "https://artgallery.qcc.cuny.edu/exhibits/powerful-arts-of-cameroon"),
             k("Palace pillar and house post", "Sub-types", "", "https://artgallery.qcc.cuny.edu/exhibits/powerful-arts-of-cameroon"),
             k("Bamum", "Schools & phases", "royal brass and beadwork of Foumban", "https://artgallery.qcc.cuny.edu/exhibits/powerful-arts-of-cameroon")]),
 dict(key="STRIPWEAVE", sub="H3", label="West African Strip Weaving", breadth="medium",
      defn="Cloth woven on the narrow double-heddle loom of West Africa in long strips, typically about ten centimetres wide, sewn edge to edge into wrappers, blankets, tunics and gowns: the wool and cotton blankets of Fulani weavers of the inner Niger delta (khasa, arkilla kerka), the smocks of northern Ghana, and the robes and wrappers of the Tukulor, Limba, Serer and other peoples.",
      aliases="Narrow-strip weaving; Strip-woven cloth", see="H3-23 Kente Cloth",
      src=[[BRIT, "Britannica: African art (textiles)"]],
      catalogues=[["https://www.metmuseum.org/art/collection/search?q=strip-woven", "The Met collection search: strip-woven", "strip-woven cloth in the Metropolitan Museum"]],
      axis="peoples and centres, then garment types and holding institutions",
      kinds=[k("Fulani wool blanket (khasa, arkilla)", "Sub-types", "", BRIT), k("Smock (fugu)", "Sub-types", "northern Ghana", BRIT), k("Double-heddle loom", "Sub-types", "the narrow loom itself", BRIT)]),
]
json.dump(dict(leaves={}, new_leaves=L, moves_out=[], dropped=[]), open(os.path.join(os.path.dirname(__file__), "result.json"), "w"), ensure_ascii=False, indent=1)
print(len(L), "new leaves")
