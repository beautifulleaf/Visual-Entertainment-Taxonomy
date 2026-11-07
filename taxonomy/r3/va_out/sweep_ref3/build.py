"""AAT reference sweep, part 3 (2026-11-07): leaves for the empty region x era cells found by ref_close.py.

Each is an archaeological culture with a published visual tradition, attested by an encyclopedia, museum, UNESCO or
excavation source found by web search on 2026-11-07. Not made leaves: the North American Paleo-Indian point types
(Clovis, Folsom, Plano ...; a lithic typology, no source treats them as a visual tradition) and Afanasievo (no art
source found); Maiemir goes to Animal Style as an early Scythian phase (aat_decisions.csv).
"""
import json, os
W = "https://en.wikipedia.org/wiki/"
def k(name, group, note, url): return [name, group, note, "r3 " + url, 0]
def leaf(key, sub, label, defn, src, kinds, aliases="", see=""):
    return dict(key=key, sub=sub, label=label, breadth="narrow", defn=defn, aliases=aliases, see=see, src=src,
                catalogues=[["https://www.britishmuseum.org/collection/search?keyword=" + label.split()[0], f"British Museum collection search: {label.split()[0]}", "objects in the British Museum"]],
                axis="phases and sites, then holding institutions", kinds=kinds)
L = [
 leaf("OKUNEV", "D5", "Okunev Stelae", "The monumental stone stelae and sculpture of the Okunev culture of the Minusinsk Basin, South Siberia (c. 2500–1800 BCE): saber-shaped slabs of sandstone and granite up to four metres or more carved with masked anthropomorphic faces, solar signs and beasts, with petroglyphs and small carved amulets.",
      [[W + "Okunev_culture", "Wikipedia"]], [k("Stele of Shira", "Sub-types", "Khakassia National Museum, Abakan", W + "Okunev_culture"), k("Okunev petroglyphs", "Sub-types", "", W + "Okunev_culture")],
      aliases="Okunevo culture", see="L1-2 Petroglyphs of the Mongolian Altai"),
 leaf("KARASUK", "G1", "Karasuk Bronzes", "Bronze knives, daggers and axes of the Karasuk culture of South Siberia and the Altai (c. 1500–800 BCE): curved single-edged knives with handles cast as animal heads, a realistic animal art that fed the later Scytho-Siberian Animal Style and reached Shang–Zhou China.",
      [[W + "Karasuk_culture", "Wikipedia"]], [k("Animal-headed knife", "Sub-types", "curved knife with animal pommel", W + "Karasuk_culture"), k("Tagar culture", "Schools & phases", "Iron Age successor in Khakassia", W + "Karasuk_culture")],
      see="G1-12 Animal Style"),
 leaf("PAZYRYK", "H6", "Pazyryk Felts and Carvings", "The art preserved in the frozen kurgans of the Pazyryk culture of the Altai (6th–3rd century BCE; Pazyryk, Bashadar, Tuekta, Ukok): appliqué and dyed felt hangings and saddle cloths with animal combat and investiture scenes, carved wooden griffins, elk and felines, leather cut-work, tattoos, and imported Persian and Chinese textiles including the Pazyryk carpet.",
      [["https://www.penn.museum/sites/expedition/the-textiles-from-pazyryk/", "Penn Museum, Expedition"], ["https://whc.unesco.org/fr/listesindicatives/6283", "UNESCO Tentative List: Treasures of the Pazyryk Culture"]],
      [k("Bashadar", "Schools & phases", "earlier kurgans with carved wooden animals", "https://www.penn.museum/sites/expedition/the-textiles-from-pazyryk/"), k("Felt appliqué hanging", "Sub-types", "", "https://www.penn.museum/sites/expedition/the-textiles-from-pazyryk/"), k("Pazyryk carpet", "Sub-types", "oldest surviving pile carpet, Hermitage", "https://www.penn.museum/sites/expedition/the-textiles-from-pazyryk/")],
      aliases="Pazyryk culture; Altai frozen tombs", see="G1-12 Animal Style"),
 leaf("DILMUN", "D3", "Dilmun Seals", "Round stamp seals of steatite of the Dilmun civilization of Bahrain, Failaka and the eastern Arabian coast (c. 2050–1650 BCE), carved with gazelles, bulls, human figures and symbols, drawing on the Indus seal tradition; with the ridged Barbar pottery and the royal burial mounds.",
      [["https://www.harappa.com/sites/default/files/pdf/Laursen-2016-Arabian_Archaeology_and_Epigraphy.pdf", "Laursen 2016, Arabian Archaeology and Epigraphy"], ["https://media.unesco.org/sites/default/files/webform/mow001/219.pdf", "UNESCO Memory of the World nomination"]],
      [k("Early Dilmun seal", "Sub-types", "round steatite stamp seal", "https://www.harappa.com/sites/default/files/pdf/Laursen-2016-Arabian_Archaeology_and_Epigraphy.pdf"), k("Barbar pottery", "Sub-types", "ridged red ware", "http://shell.cas.usf.edu/~rtykot/PR%20109%20Ashkanani%20&%20Tykot%202013.pdf")],
      see="D3-6 Minoan Seals"),
 leaf("JORWE", "E1", "Jorwe Ware", "Black-on-red painted pottery of the Chalcolithic Jorwe culture of Maharashtra (c. 1400–700 BCE; Inamgaon, Daimabad, Walki): fine wheel-thrown spouted jars and carinated bowls painted with geometric patterns and occasionally deer and human figures.",
      [["https://imp-art.org/articles/jorwe-culture/", "Impart"], ["https://indike.org/pramana/inp.artefact.site.inamgaon.1968-dhavalikar-black-painted-red-ware-jorwe-fabric", "Indian Archaeology: a Review, Inamgaon"]],
      [k("Inamgaon", "Schools & phases", "type settlement", "https://imp-art.org/articles/jorwe-culture/"), k("Malwa ware", "Schools & phases", "preceding painted ware", "https://imp-art.org/articles/jorwe-culture/")],
      see="E1-154 Harappan Pottery"),
 leaf("KURAARAX", "E1", "Kura–Araxes Pottery", "The handmade red-black burnished ware of the Kura–Araxes (Early Transcaucasian) culture of the South Caucasus and eastern Anatolia (c. 3500–2450 BCE), with incised and relief spirals and geometric motifs, decorated hearth stands, spread to the Levant as Khirbet Kerak ware.",
      [[W + "Kura–Araxes_culture", "Wikipedia"]], [k("Khirbet Kerak ware", "Sub-types", "Levantine variant", W + "Kura–Araxes_culture"), k("Red-black burnished ware", "Sub-types", "", W + "Kura–Araxes_culture")],
      aliases="Early Transcaucasian ware; Karaz pottery"),
 leaf("BELDIBI", "L1", "Beldibi Cave Art", "Coloured rock engravings and paintings of the Beldibi cave near Antalya (late Palaeolithic to proto-Neolithic, c. 10,000 BCE), the only known cave art in western Asia, with portable stones carved with naturalistic animals and geometric ornament.",
      [[W + "Belbaşı", "Wikipedia"]], [k("Belbaşı", "Schools & phases", "neighbouring cave of the same sequence", W + "Belbaşı")], see="L1-35 Levantine Rock Art"),
]
json.dump(dict(leaves={}, new_leaves=L, moves_out=[], dropped=[]), open(os.path.join(os.path.dirname(__file__), "result.json"), "w"), ensure_ascii=False, indent=1)
print(len(L), "new leaves")
