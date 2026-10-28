"""Pilot slice 1 (Visual Art): the Islamic world.

Builds the candidate pool from every gathered source that touches the slice and
gives each row exactly one disposition:

  leaf:<code>    the row is the tradition a leaf stands for (it attests the leaf)
  kind:<code>    a kind under that leaf (sub-school, centre, sub-type, maker)
  alias:<code>   another name of an existing leaf or kind (no second node)
  tag:period     a dynasty, reign or period: a filter, never a node (P6)
  tag:place      a place, centre, country or culture label: a filter (P7)
  route:<where>  belongs to another family or slice; placed when that is built
  exclude:<why>  noise, non-art, fails the inclusion rule, or duplicate

Rules come first; seeds/classify/islamic_overrides.csv (pool_id, disposition,
note) wins over any rule. Writes taxonomy/pilot/islamic_pool.csv.
"""
import csv
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
import tree_visual_art as T  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
D = os.path.join(ROOT, "data", "interim")
OUT = os.path.join(ROOT, "taxonomy", "pilot")
OVR = os.path.join(ROOT, "seeds", "classify", "islamic_overrides.csv")

LEAF = {l[0]: l for ls in T.LEAVES.values() for l in ls}


def rd(path):
    return list(csv.DictReader(open(os.path.join(D, path), encoding="utf-8")))


def num(x):
    try:
        return float(x or 0)
    except ValueError:
        return 0.0


# ---- tradition labels → disposition (curated from the pool's own labels) ----
TRAD = {
    # painting
    "Imperial Mughal atelier": "kind:A1-4", "Prince Salim's atelier (Allahabad)": "kind:A1-4",
    "Company school": "leaf:A1-6", "Deccani": "leaf:A1-5", "Deccani (Golconda)": "kind:A1-5",
    "Deccani (Hyderabad)": "kind:A1-5", "Deccani (Bijapur)": "kind:A1-5", "Lucknow (Awadh)": "kind:A1-4",
    "Murshidabad": "kind:A1-4", "Mughal Murshidabad": "alias:A1-4/Murshidabad", "Mughal Delhi": "tag:place",
    "Mughal Lahore": "tag:place", "Mughal Agra": "tag:place", "Mughal Herat": "exclude:artefact of regex detection (Timurid calligraphers on Mughal album pages); makers placed individually",
    "Kashmir": "tag:place", "Qajar Tehran": "tag:place", "Safavid Isfahan": "kind:A1-2", "Safavid Tabriz": "kind:A1-2",
    "Safavid Qazvin": "kind:A1-2", "Safavid Shiraz": "kind:A1-2", "Safavid Herat": "alias:A1-2/Herat school",
    "Safavid Bukhara": "alias:A1-2/Bukhara school", "Timurid Herat": "kind:A1-2", "Timurid Shiraz": "kind:A1-2",
    "Timurid Tabriz": "alias:A1-2/Turkman school", "Timurid Isfahan": "tag:place", "Injuid Shiraz": "kind:A1-2",
    "Ilkhanid Tabriz": "kind:A1-2", "Ilkhanid Baghdad": "alias:A1-2/Jalayirid school", "Ilkhanid Shiraz": "alias:A1-2/Injuid Shiraz",
    "Abbasid Baghdad": "kind:A1-1", "Ottoman court studio (nakkashane)": "kind:A1-3", "Ottoman Istanbul": "tag:place",
    "Mamluk Cairo": "tag:place", "Mamluk Damascus": "tag:place", "Ottoman Iznik": "alias:E2-7",
    "Deccani sultanates Delhi": "exclude:contradictory place × dynasty combination from regex detection",
    "Ilkhanid Kashan": "tag:place", "Samanid Nishapur": "alias:E1-4", "Zangid Mosul": "alias:G1-2",
    "Fatimid Kairouan": "tag:place", "Zirid Kairouan": "tag:place", "Abbasid Kairouan": "tag:place",
    "Abbasid Isfahan": "tag:place", "Aghlabid Kairouan": "tag:place", "Ayyubid Cairo": "tag:place",
    "Idrisid Fez": "tag:place", "Mudejar Valencia": "alias:E1-8", "Qajar Isfahan": "tag:place", "Qajar Shiraz": "tag:place",
    "Umayyad (Spain) Valencia": "tag:place",
    # manuscripts
    "Islamic book arts: Persianate (see islamic_world.py)": "kind:C2-2", "Islamic book arts: Ottoman (see islamic_world.py)": "kind:C2-2",
    "Islamic book arts: Arabic (see islamic_world.py)": "kind:C2-2", "Islamic book arts: Maghrebi / Andalusi (see islamic_world.py)": "kind:C2-2",
    "West African Ajami / Sahelian Islamic (see islamic_world.py)": "leaf:C2-3", "Swahili / East African Islamic (see islamic_world.py)": "kind:C2-2",
    "Islamic Nusantara manuscripts (Jawi, Pegon)": "leaf:C2-4", "Shahnameh and Persian illustrated epics (see islamic_world.py)": "alias:A1-2",
    "Mughal painting": "alias:A1-4", "calligraphy": "exclude:umbrella term (Islamic calligraphy is family C1, not a node)",
    "Islamic art": "exclude:umbrella term for the whole slice", "Mughal art": "exclude:umbrella term (tradition per medium)",
    # in situ
    "Islamic wall painting (other)": "exclude:fallback bucket of the rule table",
    "Safavid and Qajar palace wall painting (Isfahan)": "leaf:L2-2", "Umayyad palace painting (Qusayr 'Amra)": "leaf:L2-1",
    "Umayyad mosaics (Dome of the Rock, Great Mosque of Damascus)": "leaf:L3-1", "Maghrebi and Andalusi zellige": "leaf:L3-2",
    "Persian and Timurid architectural tilework": "leaf:L3-3", "Mughal and Punjabi tile mosaic (kashi kari)": "leaf:L3-4",
    "Ottoman Iznik tile revetments": "alias:E2-7", "Deq (Kurdish and Arab facial tattooing)": "leaf:L5-1",
    "Modern land art (Islamic world)": "route:VA-M (contemporary land art, artist-led)",
    # world folk (curated + Wikidata rows)
    "Moroccan pottery (Fez, Safi, Tamegroute)": "leaf:E1-10", "Bedouin silver jewellery (Yemen, Oman, Arabia)": "leaf:G3-3",
    "Kutahya and Canakkale pottery": "alias:E2-11", "Persian tribal kilims (gelim) and gabbeh": "kind:H2-1",
    "Amazigh (Berber) silver jewellery and enamel": "leaf:G3-4", "Palestinian embroidery (tatreez)": "leaf:H4-3",
    "Turkish oya (needle lace edging)": "leaf:H4-6", "Karagoz shadow puppets": "leaf:D4-1", "Suzani": "leaf:H4-1",
    "Anatolian kilim": "kind:H2-1", "Central Asian ikat (abrbandi)": "leaf:H5-1", "Turkmen tribal rugs and trappings": "leaf:H1-5",
    "Amazigh (Berber) rugs and weaving": "leaf:H1-9", "Kabyle pottery": "leaf:E1-11", "Ebru (Turkish paper marbling)": "leaf:C4-1",
    "Khatam (Persian micro-marquetry)": "leaf:I1-2", "Khayamiya (Egyptian tentmaker appliqué)": "leaf:H4-7",
    "Persian qalamkar (Isfahan printed cotton)": "leaf:H5-2", "Zellige": "alias:L3-2", "Al Sadu (Bedouin weaving)": "leaf:H2-3",
    "Baluch rugs": "leaf:H1-6", "Termeh": "leaf:H3-5", "Egyptian Harrania tapestry (Wissa Wassef)": "route:modern (Ramses Wissa Wassef Art Centre, 1952; modern artist-led cell)",
    "Kyrgyz and Kazakh felt (shyrdak, ala-kiyiz, tus kiiz)": "leaf:H6-1", "Sejnane pottery": "leaf:E1-12", "Pateh (Kerman embroidery)": "leaf:H4-4",
    "Uzbek ceramics (Rishtan, Gijduvan)": "leaf:E1-13", "Khamak embroidery (Kandahar)": "kind:H4-8",
    "Afghan war rugs": "kind:H1-7", "Persian carpet": "alias:H1-1", "kilim": "alias:H2-1", "İznik pottery": "alias:E2-7",
    "Anatolian rug": "alias:H1-2", "Turkmen rug": "alias:H1-5", "Afghan rug": "leaf:H1-7", "tatreez": "alias:H4-3",
    "Berber (Amazigh) carpet": "alias:H1-9", "soumak": "leaf:H2-2", "Mina'i ware": "leaf:E2-3", "Baluch rug": "alias:H1-6",
    "Herat school": "kind:A1-2", "Bukhara school": "kind:A1-2", "Esfahan school": "alias:A1-2/Safavid Isfahan",
    "Behzad's style of miniature art": "alias:A1-2/Herat school", "Seljuk pottery": "leaf:E2-1", "Kubachi ware": "leaf:E2-9",
    "Lājvard ware": "leaf:E2-4", "Raqqa ware": "leaf:E2-5", "Qashani": "alias:L3-3", "Iranian pottery": "exclude:umbrella term",
    "Ottoman pottery": "exclude:umbrella term", "ceramic arts in Uzbekistan": "alias:E1-13", "Moroccan rugs": "alias:H1-9",
    "Mamluk carpet": "leaf:H1-3", "Para-Mamluk carpet": "kind:H1-3", "Mosul School of Metalwork": "leaf:G1-2",
    "Siculo-Arabic ivory casket": "leaf:D2-2", "Firoozeh Koobi": "leaf:G1-9", "Berber jewellery": "alias:G3-4",
    "Kabyle jewelery": "kind:G3-4", "Khit er rouh": "kind:G3-4", "Olive wood carving in Palestine": "leaf:I1-4",
    "Palestinian costume": "leaf:H7-1", "Palestinian thobe": "alias:H7-1", "fashion in the Ottoman Empire": "leaf:H7-2",
    "The art of embroidery in Palestine, practices, skills, knowledge and rituals": "alias:H4-3",
    "traditional Syrian glassblowing": "leaf:F1-2", "aina-kari": "leaf:L3-5", "Traditional Ahlat stonework": "kind:K1-7",
    "Persian embroidery": "exclude:umbrella term", "Rasht embroidery": "leaf:H4-5", "Sistan embroidery": "kind:H4-8",
    "Sistan cream embroidery": "kind:H4-8", "Baloch needlework": "leaf:H4-8", "Turkmen embroidery": "kind:H1-5",
    "Turkmen-style needlework art": "kind:H1-5", "ala kiyiz": "alias:H6-1", "elechek": "route:costume (headdress; Possession Taxonomy)",
    "mergoum": "kind:H2-1", "Bijar kilim": "kind:H2-1", "Shahsevan kilim": "kind:H2-1", "Shushtar Bakhtiari kilim": "kind:H2-1",
    "court carpet": "kind:H1-1", "hunting carpet": "kind:H1-1", "animal carpet": "kind:H1-1", "Safavid carpet": "kind:H1-1",
    "Four Seasons carpet": "kind:H1-1", "Salting carpet": "kind:H1-1", "Polonais carpet": "kind:H1-1", "pictorial carpet": "kind:H1-8",
    "Indo-Isfahan carpet": "leaf:H1-8", "Anatolian animal carpet": "kind:H1-2", "Holbein carpet": "kind:H1-2", "Lotto carpet": "kind:H1-2",
    "Ghiordes carpet": "kind:H1-2", "Konya carpet": "kind:H1-2", "Hereke carpet": "kind:H1-2", "Kumkapi carpet": "kind:H1-2",
    "Smyrna carpet": "kind:H1-2", "Yürük rug": "kind:H1-2", "Yahyali rug": "kind:H1-2", "Demirci carpet": "kind:H1-2",
    "Yagcibedir rug": "kind:H1-2", "Kaymagli carpet": "kind:H1-2", "Karaja carpet": "kind:H1-1", "Yomut carpet": "kind:H1-5",
    "Salor rug": "kind:H1-5", "Ersari carpet": "kind:H1-5", "Göklen rug": "kind:H1-5", "Beshir carpet": "kind:H1-5",
    "Traditional Turkmen carpet making art in Turkmenistan": "alias:H1-5", "Chobi rug": "kind:H1-7",
    "Demirchilar": "kind:H1-4", "Garachop carpet": "kind:H1-4", "Garayazi carpet": "kind:H1-4", "Barda carpet": "kind:H1-4",
    "Lechek-Turunj carpet": "kind:H1-1", "Babar carpet": "kind:H1-9", "Arabian carpet": "exclude:umbrella label, no tradition",
    "Uzbek carpet": "exclude:fails inclusion (no objects, 0 tradition evidence); review with Central Asia slice",
    "Uzbek julkyr": "exclude:fails inclusion; review with Central Asia slice", "Uzbek napramach": "exclude:fails inclusion; review with Central Asia slice",
    "re-entrant rug": "kind:H1-2", "Axminster carpet": "route:Western Europe (English carpet manufactory)",
    "Bessarabian rugs and carpets": "route:Central & Eastern Europe folk", "pile warp substitution": "exclude:weaving technique, not a tradition",
    "Zeugdruckerei": "exclude:German term for cloth printing (generic technique)", "Mazman weaving loom": "exclude:a loom, not a tradition",
    "Varshosazi": "kind:G1-9", "Öñir": "exclude:fails inclusion; bare Wikidata item", "Naycha": "exclude:fails inclusion; bare Wikidata item",
    "Pardoz": "exclude:fails inclusion; bare Wikidata item", "Kapu (basket)": "route:basketry (folk craft family decision pending)",
    "Egyptian revival decorative arts": "route:Western Europe (European Egyptian Revival)", "Kazakh art": "exclude:umbrella term",
    "Kazakh decorative art": "exclude:umbrella term", "Kurdish art": "exclude:umbrella term", "Algerian embroidery": "kind:H4-2",
    "Button embroidery": "exclude:fails inclusion; bare Wikidata item", "Armak weaving": "kind:H2-1", "Bedouin weaving": "alias:H2-3",
    "chadorshabfi": "kind:H2-1", "Sermeh embroidery": "kind:H4-4", "Chakan": "kind:H4-1", "Elpek cloth": "exclude:fails inclusion; bare Wikidata item",
    "Al Talli": "exclude:fails inclusion (braid trimming); review", "kurar": "exclude:fails inclusion; bare Wikidata item",
    "metal engraving": "exclude:technique, not a tradition", "coba bowl": "route:Ancient Near East (Late Chalcolithic, pre-Islamic)",
    "orange-burnished": "route:Ancient Near East (pre-Islamic ware)", "Egyptian paste": "route:Ancient Egypt (faience body)",
    "Dawsari incense": "exclude:not visual art", "Al-Qatt Al-Asiri Al Saudi": "leaf:L2-3",
    "ʻArḍat janūbīyah": "exclude:performance (dance), not visual art", "التراث الشعبي والأهازيج الشعبية في السعودية": "exclude:not visual art",
    "الحيوما": "exclude:not visual art", "الرايح": "exclude:not visual art",
}
GARMENT = {"abaya", "arkhalig", "justacorps", "gandoura", "Moroccan kaftan", "Kazakh national clothes", "Afghan clothing",
           "chedda of Tlemcen", "ak-kalpak", "Saudi national dress", "Mdemma", "Traditional Libyan clothing", "حولي ليبي",
           "wazra", "Ghutra", "Shemagh", "Diglah", "Farwah", "Daq Alhab"}
RUG_CENTRE = re.compile(r"\b(rug|carpet)\b", re.I)
PERSIAN_RUG = {"Shiraz", "Tabriz", "Heriz", "Kashan", "Varamin", "Nain", "Qom", "Isfahan", "Bakhtiari", "Kerman", "Bijar", "Ardabil",
               "Abadeh", "Seraband", "Saruq", "Mashhad", "Zanjan", "Kashmar", "Karadagh", "Hamadan", "Meshkin", "Sanandaj", "Yazd",
               "Arak", "Jozan", "Shahsevan", "Lorestan", "Ahar", "Herat", "Bakshaish", "Qaen", "Qazvin", "Nishapur", "Qashqai",
               "Mamasani", "Moud", "Shahrekord", "Mushkabad", "Semnan", "Enjilas", "Viss", "Afshar", "Khorasan", "Gorevan", "Yalameh",
               "Khoi", "Azarshahr", "Sardroud", "Mahabad", "Bukan", "Sarab", "Joshaghan", "Feraghan", "Borujerd", "mir", "Shiraki",
               "sofra", "Dorukhsh"}

ARCH = {
    "Islamic architecture": "exclude:umbrella (sub-family K1 itself)", "architecture of Iran": "exclude:architecture of a country (place tag)",
    "Ottoman architecture": "leaf:K1-12", "Mughal architecture": "leaf:K1-15", "Moorish architecture": "leaf:K1-4",
    "Moorish Revival architecture": "leaf:K2-1", "Mughal gardens": "kind:K1-15", "Norman-Arab-Byzantine culture": "route:Arab-Norman (Sicily) — Medieval Europe style family",
    "Mozarabic art": "route:Medieval Europe (Christian art under Muslim rule)", "Mamluk architecture": "leaf:K1-8",
    "Indo-Islamic architecture": "leaf:K1-14", "Timurid art": "alias:K1-10", "Abbasid architecture": "leaf:K1-2",
    "Seljuk architecture": "leaf:K1-6", "architecture of Turkey": "exclude:architecture of a country (place tag)",
    "Timurid architecture": "leaf:K1-10", "Umayyad architecture": "leaf:K1-1", "Art of Al-Andalus": "alias:K1-4",
    "Fatimid architecture": "leaf:K1-3", "Safavid architecture": "leaf:K1-11", "Ottoman Baroque": "kind:K1-12",
    "Umayyad art": "alias:K1-1", "Nasrid art": "kind:K1-4", "Turku romanticism": "exclude:false match (Finnish)",
    "Chinese Islamic architecture": "leaf:K1-18", "Anatolian Seljuk architecture": "leaf:K1-7", "early Ottoman architecture": "kind:K1-12",
    "Neo-Mamluk architecture": "leaf:K2-3", "Arabic architecture": "exclude:umbrella", "art of the Umayyads of Cordoba": "kind:K1-4",
    "Moorish Revival architecture in Bosnia and Herzegovina": "kind:K2-1", "classical Ottoman architecture": "kind:K1-12",
    "Mozarabic architecture": "route:Medieval Europe", "Mozarabic art in Catalonia": "route:Medieval Europe",
    "Ottoman architecture in Egypt": "kind:K1-12", "Andalusian regionalist architecture": "route:Historicist revivals (Spanish regionalism)",
    "Ilkhanid architecture": "leaf:K1-9", "Indo-Persianate architecture": "alias:K1-15", "Andalusian architectural style": "alias:K1-4",
    "Fatimid architectural style": "alias:K1-3", "Moorish Revival architecture in Hungary": "kind:K2-1",
    "Ottoman architecture in the 19th–20th centuries": "kind:K1-12", "Islamic architecture of North Macedonia": "exclude:architecture of a country (place tag)",
    "Nasrid architecture": "alias:K1-4/Nasrid art", "Qajar architecture": "leaf:K1-13", "Andalusian costumbrismo": "exclude:false match (painting genre)",
    "early Anatolian Turkish architecture": "alias:K1-7", "Turkish vernacular architecture": "route:vernacular architecture (built at scale)",
    "Religious Islamic architecture": "exclude:zero-sitelink bulk item", "Ottoman Rococo": "alias:K1-12/Ottoman Baroque",
    "Moorish style": "alias:K1-4",
}
ARCH_NW = {
    "Mamluk": "alias:K1-8", "Yemeni / Omani Islamic": "exclude:proposed region bucket; review rules before seeding (handover §2.3)",
    "Ayyubid": "kind:K1-8", "Fatimid": "alias:K1-3", "Early Islamic (Umayyad / Abbasid / Tulunid)": "alias:K1-2",
    "Iraqi Islamic (Ilkhanid / Jalayirid)": "alias:K1-9", "Chinese Islamic": "alias:K1-18", "Ethiopian Islamic (Harar)": "kind:K1-16",
    "Indo-Islamic (Delhi Sultanate)": "kind:K1-14", "Gujarat Sultanate": "kind:K1-14", "Deccan Sultanates (Bahmani / Qutb Shahi / Adil Shahi)": "kind:K1-14",
    "Bengal Sultanate": "kind:K1-14", "Early Islamic Maghreb (Aghlabid / Idrisid / Zirid)": "kind:K1-4", "Mughal": "alias:K1-15",
    "Ottoman": "alias:K1-12", "Ottoman (Arab provinces)": "alias:K1-12/Ottoman architecture in Egypt", "Anatolian Seljuk / Beylik": "alias:K1-7",
    "Azerbaijani (Shirvan–Absheron)": "kind:K1-6", "Persian — Safavid": "alias:K1-11", "Persian — Ilkhanid / Muzaffarid": "alias:K1-9",
    "Timurid": "alias:K1-10", "Persian — Seljuk / Khwarazmian": "alias:K1-6", "Persian — Qajar": "alias:K1-13",
    "Persian — early Islamic (Samanid / Buyid / Ghaznavid)": "kind:K1-6",
}
ARCH_ZERO_STYLE = re.compile(r" architecture style$")


def maker_rule(m):
    """First-pass home for a named maker from the Islamic sweep."""
    name = m["maker"]
    roles = m["roles"].lower()
    titles = m["example_titles"].lower()
    school = m["school"]
    if re.search(r"^(others|possibly|attributed|signed|tara \d|banavari \d)", name, re.I) or name.lower() in {"others"}:
        return "exclude:not a maker name (attribution phrase or catalogue placeholder)"
    if "photographer" in roles:
        return "route:VA-J Photography (photographer of monuments; artist-led family)"
    if "workshop / movement" in roles and not school:
        return "review"
    sch = {"Imperial Mughal atelier": "kind:A1-4", "Prince Salim's atelier (Allahabad)": "kind:A1-4", "Lucknow (Awadh)": "kind:A1-4",
           "Mughal Murshidabad": "kind:A1-4", "Mughal Agra": "kind:A1-4", "Company school": "kind:A1-6", "Deccani": "kind:A1-5",
           "Deccani (Bijapur)": "kind:A1-5", "Deccani (Hyderabad)": "kind:A1-5", "Safavid Isfahan": "kind:A1-2", "Safavid Tabriz": "kind:A1-2",
           "Safavid Qazvin": "kind:A1-2", "Safavid Herat": "kind:A1-2", "Abbasid Baghdad": "kind:A1-1",
           "Ottoman court studio (nakkashane)": "kind:A1-3"}
    if "calligraph" in roles:
        return "review"
    if school in sch and re.search(r"paint|drawing|folio|page|album|portrait|akbar|prince|shah|khan|emperor|hunt|illustrat", titles):
        return sch[school]
    return "review"


def build():
    rows = []

    def add(src, sid, label, typ, ev, disp, note=""):
        rows.append({"pool_id": f"{src}:{sid}", "source": src, "label": label, "type": typ, "evidence": ev,
                     "disposition": disp, "note": note})

    for r in rd("regional/islamic_dynasties.csv"):
        add("islamic_dynasties", r["key"], r["dynasty"], "dynasty", f"{r['objects']} objects", "tag:period",
            "dynasty → period filter (P6)")
    for r in rd("regional/islamic_schools.csv"):
        if r["kind"] == "centre":
            add("islamic_schools", "centre:" + r["name"], r["name"], "centre", f"{r['objects']} objects", "tag:place",
                "production centre → place tag (P7); named wares and schools carry the centre's name where the field does")
        else:
            add("islamic_schools", "school:" + r["name"], r["name"], "school", f"{r['objects']} objects; {r['basis']}",
                TRAD.get(r["name"], "review"))
    for r in rd("regional/world_folk_traditions.csv"):
        if "MENA" not in r["region"] and "Central Asia" not in r["region"]:
            continue
        lab = r["label"]
        ev = f"{r['total_objects_distinct']} objects; {r['wd_sitelinks'] or 0} sitelinks; {r['kind']}"
        if lab in TRAD:
            disp = TRAD[lab]
        elif lab in GARMENT:
            disp = "exclude:garment type, not an art tradition (P10; Possession Taxonomy)"
        elif RUG_CENTRE.search(lab) and lab.split()[0] in PERSIAN_RUG:
            disp = "kind:H1-1"
        elif lab.split()[0] in PERSIAN_RUG and "kilim" not in lab.lower():
            disp = "kind:H1-1"
        elif lab.startswith("Afshar"):
            disp = "kind:H1-1"
        else:
            disp = "review"
        add("world_folk", r["node_key"], lab, "folk/" + r["kind"], ev, disp)
    for r in rd("manuscripts_traditions.csv"):
        lab = r["label"]
        if lab in TRAD:
            add("manuscripts", lab, lab, "manuscript tradition", f"{r['n_manuscripts']} manuscripts", TRAD[lab])
    for r in rd("in_situ_traditions.csv"):
        lab = r["label"]
        if lab in TRAD:
            add("in_situ", lab, lab, "art in place", f"{r['n_sites']} sites", TRAD[lab])
        elif r["region"] == "Islamic world" and "fallback" in r["node_source"]:
            add("in_situ", lab, lab, "art in place", f"{r['n_sites']} sites", "exclude:fallback 'kind – country' bucket (modern murals/mosaics; artist-led)")
    isl_arch = re.compile(r"islam|ottoman|mughal|moorish|mamluk|timurid|abbasid|seljuk|umayyad|andalus|fatimid|safavid|nasrid|ilkhanid|qajar|mozarab|mudéjar|norman-arab|turku|turkish|costumbrismo|iran|deccan|sultanate|indo-|persian", re.I)
    for r in rd("architecture_styles.csv"):
        lab = r["label"]
        if not isl_arch.search(lab):
            continue
        if lab in ARCH:
            disp = ARCH[lab]
        elif ARCH_ZERO_STYLE.search(lab) and r["sitelinks"] == "0":
            disp = "exclude:zero-sitelink bulk '… architecture style' item (handover §2.3: judge, don't count)"
        else:
            disp = "review"
        add("architecture_styles", r["qid"], lab, "architectural style", f"{r['sitelinks']} sitelinks; {r['n_buildings']} buildings", disp)
    for r in rd("architecture_nonwestern_styles.csv"):
        lab = r["proposed_style"]
        if lab in ARCH_NW:
            add("architecture_nonwestern", lab, lab, "proposed style", f"{r['n_candidates']} candidate buildings", ARCH_NW[lab])
    for r in rd("unattributed_cultures.csv"):
        if "Islamic" not in r.get("dominant_department", ""):
            continue
        if num(r["objects"]) < 50 and num(r["timeline_works"]) == 0:
            continue
        typ = "dynasty" if r["kind"] == "period" or r["label"].split(", ")[-1] in {"Seljuq", "Abbasid", "Mamluk", "Mughal", "Ottoman", "Fatimid", "Qajar", "Safavid", "Umayyad", "Ilkhanid", "Ayyubid", "Nasrid", "Timurid"} else "culture"
        add("met_cultures", r["key"], r["label"], typ, f"{r['objects']} objects; {r['timeline_works']} Timeline works",
            "tag:period" if typ == "dynasty" else "tag:place", "Met culture/period field → filter (P6, P7)")
    # makers
    for r in rd("regional/islamic_makers.csv"):
        add("islamic_makers", r["maker"], r["maker"], "maker",
            f"{r['objects']} objects; {r['dynasties'][:40]}; school {r['school'] or '–'}; roles {r['roles'][:40]}",
            maker_rule(r))
    for r in rd("manuscripts_illuminators.csv"):
        if "Islamic" in r["tradition"] or r["label"] in {"Levni"}:
            add("illuminators", r["qid"], r["label"], "maker", f"{r['sitelinks']} sitelinks; fl. {r['floruit_est']}", "review")
    for r in rd("visual_art/scores_islamic_pre1400_era.csv"):
        if r.get("final") in ("1", "True", "true"):
            add("pre1400_islamic", r["qid"], r["label"], "maker", f"{r['medium']}; {r['sitelinks']} sitelinks; {r.get('note','')}", "review")
    sel = {r["qid"]: r for r in rd("visual_art/scores_europe_1400-1900.csv") if r["selected"] in ("1", "True")}
    for q in ["Q3561135", "Q4115413", "Q4665830", "Q6419363"]:
        if q in sel:
            add("europe_1400-1900", q, sel[q]["label"], "maker", f"{sel[q]['medium']}; selected artist", "review")
    arch_styles = {"Q527449": "K1-12", "Q542261": "K1-15", "Q2864747": "K1-10", "Q16836366": "K1-3", "Q7448523": "K1-6",
                   "Q127632740": "K1-7", "Q4314692": "K1-6", "Q6095546": "K2-4", "Q111255949": "K2-3"}
    for r in rd("architecture_architects.csv"):
        homes = [arch_styles[s] for s in r["styles"].split("|") if s in arch_styles]
        if not homes:
            continue
        add("architects", r["qid"], r["label"], "architect", f"{r['sitelinks']} sitelinks; {r['buildings_label'][:60]}", "kind:" + homes[0])

    # overrides
    ovr = {}
    if os.path.exists(OVR):
        for o in csv.DictReader(open(OVR, encoding="utf-8")):
            ovr[o["pool_id"]] = o
    for r in rows:
        if r["pool_id"] in ovr:
            r["disposition"] = ovr[r["pool_id"]]["disposition"]
            if ovr[r["pool_id"]].get("note"):
                r["note"] = ovr[r["pool_id"]]["note"]
            r["by"] = "review"
        else:
            r["by"] = "rule"
    return rows


def main():
    rows = build()
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "islamic_pool.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["pool_id", "source", "label", "type", "evidence", "disposition", "note", "by"])
        w.writeheader()
        w.writerows(rows)
    c = Counter(r["disposition"].split(":")[0] for r in rows)
    print(len(rows), dict(c))
    bad = [r for r in rows if r["disposition"].split(":")[0] in ("kind", "leaf", "alias") and r["disposition"].split(":")[1].split("/")[0] not in LEAF]
    for r in bad:
        print("UNKNOWN CODE", r["pool_id"], r["disposition"])


if __name__ == "__main__":
    main()
