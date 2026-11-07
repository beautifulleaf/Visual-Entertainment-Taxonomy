import csv, re, sys, os
D = os.path.dirname(os.path.abspath(__file__))
O = os.path.dirname(D)
rows = list(csv.DictReader(open(os.path.join(O, "in_col_H.csv"))))
G = "general:H"

# ---- regex rules on lowercased label: (pattern, map, note) first match wins
R = [
 # non-native / noise
 (r"non-indian", "exclude:non-Native row (mis-regioned)", ""),
 (r"^unspecified$", "exclude:no attribution", ""),
 # Andean archaeological textiles
 (r"chancay or chim", G, "Chancay or Chimú, ambiguous"),
 (r"chancay", "H3-29", ""),
 (r"proto-nasca", "exclude:archaeological beads", ""),
 (r"paracas", "H4-32", ""),
 (r"nasca|nazca", "missing:Nasca Textiles", ""),
 (r"inka \(inca\) \(attributed\)", "G1-29", "tupu shawl pins"),
 (r"\binka\b|^inca$", "H2-4", ""),
 (r"wari|huari", "H2-5", ""),
 (r"chim[uú].*archaeolog.*", "missing:Chimú Textiles", ""),
 (r"^chimu$", "missing:Chimú Textiles", ""),
 (r"ica-chincha", "missing:Ica-Chincha Textiles", ""),
 (r"moche", "missing:Moche Textiles", ""),
 (r"sic[aá]n", "missing:Sicán Textiles", ""),
 (r"pachacamac|central andes|arica", G, "Andean archaeological, no style"),
 (r"san pedro de atacama|humahuaca", "exclude:archaeological weaving tools", ""),
 (r"tiwanaku|ychsma", "exclude:archaeological ornaments", ""),
 (r"muisca", "G1-30", "gold shawl pins"),
 (r"quimbaya", "G3-9", "gold beads"),
 (r"probably mixteca", "G3-13", "Mixtec gold beads"),
 # other archaeological: exclude
 (r"archaeolog|archaic|woodland tradition|thule tradition", "exclude:archaeological beads/fragments", ""),
 (r"^northern mesoamerica", "exclude:archaeological tools", ""),
]

def tribe(l):
    """Native American / Indigenous labels -> map"""
    T = [
     (r"chilkat", "H2-11"),
     (r"eastern shoshone|northern shoshone|^shoshone$|bannock", "H9-6"),
     (r"kwakwaka'wakw|kwakiutl", "missing:Northwest Coast Button Blankets"),
     (r"button blanket", "missing:Button Blankets"),
     (r"tlingit|haida", "H8-14"),
     (r"\bpomo\b", "H8-12"),
     (r"hupa|karuk|yurok|yokuts|kumeyaay|diegue|klamath|modoc|shasta|washoe|maidu|cahuilla|chemehuevi|mono paiute|kutzadika|achomawi|wiyot|tolowa|tübatulabal|luise|payómkawichum|mission$|northern california|unspecified \(california\)|paiute|koso|shoshone|bannock|cochimi|paipai|mojave|quechan|cocopa", "H8-13"),
     (r"apache|dilzhe|yavapai", "H8-18"),
     (r"o'odham|pima|piipaash|maricopa|nevome", "H8-19"),
     (r"hopi", "H8-20"),
     (r"cherokee|choctaw|chitimacha|koasati|coushatta|alibamu|chickasaw|muscogee|creek|houma|atakapa", "H8-21"),
     (r"passamaquoddy|penobscot|mi'kmaq|micmac|maliseet|abenaki|wawenock", "H8-22"),
     (r"klikitat|klickitat|nlaka'pamux|interior salish|stl'atl'imx|lillooet|tsilhqot|plateau", "H8-17"),
     (r"nez perce|niimíipuu|yakama|wasco|wishram|umatilla|warm springs|kalispel", "H8-16"),
     (r"unanga|aleut", "H8-15"),
     (r"wendat|huron|wyandot", "H4-40"),
     (r"seminole|miccosukee", "H4-38"),
     (r"mohawk|seneca|onondaga|oneida|cayuga|tuscarora|iroquois", "H9-7"),
     (r"osage|menominee|ho-chunk|winnebago|meskwaki|\bfox\b|potawatomi|sac and fox|\bsauk\b|kickapoo|\boto\b|^iowa|kaw \(|quapaw|miami|shawnee", "H4-39"),
     (r"sioux|lakota|dakota|apsáalooke|crow|kiowa|cheyenne|tsitsistas|arapaho|inunaina|blackf|piegan|kainai|siksika|niitsitapii|assiniboine|plains cree|arikara|sahnish|comanche|niuam|\bute\b|mandan|numakiki|hidatsa|minitari|gros ventre|a'aninin|ponca|omaha|pawnee|chaticks|tsuu t'ina|sarcee|plains ojibwa|plains apache|wichita|caddo|plains|metis|cree metis|salish \(flathead\)|ktunaxa|kootenai", "H9-6"),
     (r"odawa|ottawa|anishinaabe|ojibw|chippewa|saulteaux|mississauga|great lakes", "H9-5"),
     (r"diné|navajo", "H2-10"),
     (r"chimayo", "H2-13"),
     (r"saltillo", "H2-9"),
     (r"inuit|iñupiaq|inupiaq|yup'ik|yupik|cup'ik|cu'pig|inughuit|kalaallit|tunumiit|inuvialuit|sugpiaq|alutiiq|greenland", "missing:Inuit Skin Clothing"),
     (r"nisga'a|gitxsan|tsimshian|gitxaała|heiltsuk|haisla|nuxalk|wuikinuxv|northwest coast|dakelh|carrier", G),
     (r"makah|nuu-chah-nulth|nootka|tla-o-qui-aht", "missing:Nuu-chah-nulth and Makah Basketry"),
     (r"salish|cowichan|quinault|quileute|puyallup|duwamish|twana|squaxon|suquamish|skokomish|tsartlip|tsawout|saanich|snuneymuxw|lummi|chehalis|s'klallam|cowlitz|stó:lo|songhees|esquimalt|shishalh|siletz", "missing:Coast Salish Basketry"),
     (r"pequot|mohegan|narragansett|niantic|wampanoag|schaghticoke|paugussett|tunxis|mahican|stockbridge|montauk|shinnecock|matinecock|canarsee|munsee|lenape|delaware|nanticoke|rappahannock|mattaponi|pamunkey|chickahominy|peoria", "missing:Northeastern Splint Basketry"),
     (r"maya|k'iche'|kaqchikel|tz'utuhil|tzotzil|tzeltal|q'eqchi|mam\b|pocomam|pokomchi|chamula|chenalhó|lakandon|huixteco|ixil", "H3-28"),
     (r"quechua|aymara|kichua|quichua|saraguro|colla|ch'uta", "H2-7"),
     (r"guna|kuna", "H4-33"),
     (r"wixarika|huichol", "missing:Huichol Textiles and Beadwork"),
     (r"mapuche|huilliche|picunche", "missing:Mapuche Textiles"),
     (r"wayuu", "H8-40"),
     (r"zuni|a:shiwi|pueblo|kewa|laguna|jemez|isleta|acoma|taos|cochiti|san ildefonso|santa clara|k'apovi|ohkay|zia|san felipe|tewa", G),
    ]
    for p, m in T:
        if re.search(p, l): return m
    return None

def people(l):
    m = re.match(r"people:([a-z_]+?)(_birch_bark)?:(\w+)", l)
    if not m: return None
    p, bb, kind = m.group(1), m.group(2), m.group(3)
    if bb:
        forest = {"komi","udmurt","mari","mordvin_erzya_moksha","chuvash","tatar","bashkir","karelian","khanty","mansi","nenets","evenk","nanai","yakut_sakha","altai","tuvan","veps","khakas","buryat","koryak","chukchi","sami"}
        if p in forest: return ("H8-31", "")
        return ("exclude:keyword noise", "sample unrelated")
    E = {"chuvash":"H4-69","mari":"H4-70","karelian":"H4-71","ukrainian":"H4-66","belarusian":"H4-68",
         "tatar":"missing:Tatar Embroidery","bashkir":"missing:Bashkir Embroidery","udmurt":"missing:Udmurt Embroidery",
         "mordvin_erzya_moksha":"missing:Mordvin Embroidery","komi":G,"crimean_tatar":"missing:Crimean Tatar Embroidery",
         "hutsul":"H4-66","dagestani_general":"missing:Dagestani Gold Embroidery","dargin":G,"avar":G,
         "nenets":G,"khanty":G,"mansi":G,"evenk":G,"nanai":"missing:Nanai Fish-Skin Appliqué","koryak":G,"chukchi":G,
         "yakut_sakha":G,"altai":G,"buryat":G,"tuvan":G,"kalmyk":G,"khakas":G,"veps":G,"sami":"H7-4",
         "armenian":"H4-80","azerbaijani":G,"georgian":G,"adyghe_circassian_kabardian":"missing:Circassian Gold Embroidery",
         "lithuanian":G,"latvian":G,"estonian":G,"moldovan":G,"basque":G,"roma":G,"lezgin":G,"cossack":G,
         "boyko_lemko_rusyn":G,"karachay_balkar":G,"ossetian":G,"chechen":G,"kumyk":G,"ingrian_izhorian":G,"seto":G,"gagauz":G}
    C = {"mordvin_erzya_moksha":"H7-11","sami":"H7-4","basque":G}
    K = {"azerbaijani":"H1-4","dagestani_general":"H1-4","avar":"H1-4","lezgin":"H1-4","armenian":"H1-4","kumyk":"H1-4","lak":"H1-4",
         "moldovan":"H2-23","ukrainian":"missing:Ukrainian Kilim","georgian":"H1-4","ossetian":"H1-4",
         "adyghe_circassian_kabardian":"H6-1","karachay_balkar":"H6-1"}
    if kind == "embroidery": return (E.get(p, G), "")
    if kind == "costume": return (C.get(p, G), "noisy sample" if p not in C else "")
    if kind == "carpets": return (K.get(p, G), "")
    if kind == "lace": return (G, "")
    return (G, "")

PAT = {
 "pattern:azerbaijani_carpets_caucasian_rugs": ("H1-4",""),
 "pattern:honiton_lace": ("H4-59",""),
 "pattern:krestets_stitch": ("H4-72",""),
 "pattern:orenburg_shawl": ("H4-83",""),
 "pattern:birch_bark_work_tuohityo": ("H8-31",""),
 "pattern:skopin_pottery": ("exclude:keyword noise","pottery key, textile objects"),
 "pattern:shemogodsk_birch_bark_carving": ("H8-32",""),
 "pattern:blueprint_resist_dye_printing": ("H5-32",""),
 "pattern:pavlovo_posad_shawl": ("H5-34",""),
 "pattern:rushnyk": ("H4-67",""),
 "pattern:slutsk_sashes": ("missing:Slutsk Sashes",""),
 "pattern:tabasaran_carpets": ("H1-4","Dagestani pile carpets"),
 "pattern:kirov_vyatka_lace": ("missing:Vyatka Lace",""),
 "pattern:mikhailov_lace": ("missing:Mikhailov Lace",""),
 "pattern:tatar_leather_mosaic_ichigi": ("H4-82",""),
 "pattern:krolevets_weaving": ("missing:Krolevets Rushnyk Weaving",""),
 "pattern:balkhar_pottery": ("exclude:keyword noise","pottery key"),
 "pattern:lezgin_and_dagestani_carpets": ("H1-4",""),
 "pattern:yakut_bone_carving": ("exclude:keyword noise","bone-carving key"),
 "pattern:tobolsk_bone_carving": ("exclude:keyword noise","bone-carving key"),
 "pattern:santons_de_provence": ("exclude:keyword noise","figurine key"),
 "pattern:kasli_iron_casting": ("exclude:keyword noise","cast-iron key"),
 "pattern:rostov_enamel_finift": ("exclude:keyword noise","enamel key"),
 "pattern:chukchi_walrus_ivory_engraving_uelen": ("exclude:keyword noise","ivory key"),
 "pattern:kubachi_metalwork": ("exclude:keyword noise","metalwork key"),
 "wd:Q64407093": (G,"bobbin lace, generic technique"),
 "wd:Q2143601": ("H4-53",""), "wd:Q13513054": ("H4-66",""),
 "wd:Q774174": ("exclude:keyword noise","Palekh key, textile objects"),
 "wd:Q2051949": ("H4-57",""), "wd:Q2718962": ("missing:Chantilly Lace",""),
 "wd:Q4845699": ("H4-56",""), "wd:Q4913954": ("missing:Binche Lace",""),
 "wd:Q11872271": ("missing:Valenciennes Lace",""), "wd:Q4123721": ("H4-84","sample is china"),
 "wd:Q3855181": ("H4-54",""), "wd:Q5046174": ("H4-63",""), "wd:Q3023334": ("H4-60",""),
 "wd:Q7862370": ("missing:Tønder Lace",""), "wd:Q4174767": ("H4-85",""), "wd:Q97280262": ("H4-73",""),
}

CULT = {
 "culture:greek:embroidery":"H4-48","culture:greek_crete:embroidery":"H4-48","culture:greek_ionian_islands:embroidery":"H4-48",
 "culture:swedish:costume":"H7-6","culture:norwegian:costume":"H7-5","culture:norwegian_hardanger:lace":"H4-49",
 "culture:croatian:costume":"H7-9","culture:albanian:embroidery":"H7-8","culture:cypriot:lace":"H4-55",
 "culture:danish_tnder:lace":"missing:Tønder Lace","culture:swedish_vadstena:lace":"missing:Vadstena Lace",
 "culture:polish_kobylka:costume":"missing:Kontusz Sashes","culture:caucasian:carpets":"H1-4",
 "people:breton:costume":"missing:Breton Costume","culture:polish:embroidery":"exclude:keyword noise",
 "culture:swedish:embroidery":"exclude:keyword noise",
}

def base(r):
    l=r["label"]; ll=l.lower()
    if l in PAT: return PAT[l]
    if l in CULT: return (CULT[l],"")
    if l.startswith("culture:"): return (G,"")
    p=people(ll)
    if p: return p
    for pat,m,n in R:
        if re.search(pat,ll): return (m,n)
    if r["file"] in ("smithsonian",):
        t=tribe(ll)
        if t: return (t,"")
        return None
    return None
if __name__=="__main__":
    for i,r in enumerate(rows):
        b=base(r)
        if b is None: print(i,r["file"][:4],r["label"],"|",r["sample_title"][:30],"|",r["seed"])
