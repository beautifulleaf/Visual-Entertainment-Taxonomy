A = {}
WP = "r3 https://en.wikipedia.org/wiki/"
A["A1-4"] = [
 ("Schools & phases", "Imperial Mughal atelier;Prince Salim's atelier (Allahabad);Lucknow (Awadh);Murshidabad"),
 ("Makers: Humayun and Akbar's atelier (c. 1550–1605)", "Mir Sayyid Ali;Abd al-Samad;Dasavanta;Basawan"),
]
G_AK = "Makers: Humayun and Akbar's atelier (c. 1550–1605)"
G_JA = "Makers: Jahangir's atelier (1605–1627)"
G_SJ = "Makers: Shah Jahan and Aurangzeb (1628–1707)"
G_LM = "Makers: Late Mughal (Delhi, 18th century)"
G_SA = "Makers: Prince Salim's atelier (Allahabad)"
G_AW = "Makers: Lucknow and Faizabad (Awadh)"
G_MU = "Makers: Murshidabad"


def mughal_group(name, gloss, g0):
    if g0 in ("Lucknow (Awadh)", "Awadh"): return G_AW
    if g0 == "Murshidabad": return G_MU
    if g0 == "Prince Salim's atelier (Allahabad)": return G_SA
    if g0 == "Late Mughal": return G_LM
    gl = gloss or ""
    if "Muhammad Shah" in gl or gl.lower().startswith("late mughal"): return G_LM
    if gl.startswith("Jahangir") or "Razmnama 1616" in gl or "Jahangir's atelier" in gl or "Jahangir/" in gl: return G_JA
    if gl.startswith("Shah Jahan") or "Shah Jahan's" in gl or "Aurangzeb" in gl: return G_SJ
    if "Akbar" in gl or "Tutinama" in gl or "Akbarnama" in gl or "Razmnama" in gl or "Chingiznama" in gl or "Shahnama" in gl: return G_AK
    return None

# hand assignment for rows whose gloss does not say the reign
MANUAL = {"Bhawani Kalan": G_AK, "Khem": G_AK, "Nandi": G_AK, "Mushfiq": G_AK, "Gujarati": G_AK, "Ghulam 'Ali": G_AK, "Nur Muhammad": G_JA, "Muhammad Ali": G_JA,
          "Abu'l Hasan": G_JA, "Bishandas": G_JA, "Mansur": G_JA, "Farrukh Beg": G_AK, "Farrokh": G_AK,
          "Sahifa Banu": G_JA, "Inayat": G_JA, "Nini": G_JA, "Shiv Das": G_SJ, "Muhammad Abed": G_SJ, "`Abid": G_SJ,
          "Ghulaman": G_SJ, "Masud": G_LM, "Madhu": G_LM, "Muhammad Panah": G_LM, "Attributed to Bhawani Das": G_LM,
          "'Ali al-Husaini": G_JA, "Aqa Reza": G_JA, "Chitarman": G_SJ, "Hunhar": G_SJ, "Abdullah": G_JA,
          "Payag": G_SA, "Muhammad Sharif": G_SA, "Lal Chand": G_JA, "Murar": G_JA, "Balchand": G_JA,
          "Govardhan": G_JA, "Daulat": G_JA, "Manohar": G_JA, "Hashim": G_SJ, "Bichitr": G_SJ, "Chitarman II": G_LM}

MUGHAL_WORKS = [
 ["Hamzanama (Akbar's atelier, c. 1562–1577)", "Manuscripts of Akbar's reign", "Giant cloth-painted romance of Amir Hamza, c. 1,400 paintings; leaves in the MAK Vienna, V&A London and elsewhere", WP + "Hamzanama", 0],
 ["Cleveland Tutinama (c. 1560)", "Manuscripts of Akbar's reign", "Early Akbar-period Tales of a Parrot; Cleveland Museum of Art", WP + "Tutinama", 0],
 ["Razmnama (Akbar's atelier, 1584–1586)", "Manuscripts of Akbar's reign", "Persian Mahabharata made for Akbar; imperial copy in the City Palace Museum, Jaipur", WP + "Razmnama", 0],
 ["Akbarnama (Akbar's atelier, c. 1590–1595)", "Manuscripts of Akbar's reign", "Illustrated official history of Akbar; V&A London (116 paintings) and Chester Beatty Library, Dublin", WP + "Akbarnama", 0],
 ["Baburnama (illustrated copies, c. 1589–1600)", "Manuscripts of Akbar's reign", "Memoirs of Babur in Persian translation; copies dispersed (British Library, V&A, National Museum New Delhi)", WP + "Baburnama", 0],
 ["Khamsa of Nizami (British Library, Or. 12208)", "Manuscripts of Akbar's reign", "Lahore, early 1590s, over forty miniatures; British Library, London, and Walters Art Museum, Baltimore", WP + "Khamsa_of_Nizami_(British_Library,_Or._12208)", 0],
 ["Gulshan Album (Muraqqa-e Gulshan, c. 1599–1609)", "Albums of Jahangir's reign", "Album begun by Prince Salim; Golestan Palace, Tehran, and Staatsbibliothek Berlin, leaves widely dispersed", WP + "Gulshan_Album", 0],
 ["St. Petersburg Muraqqa", "Albums of Jahangir's reign", "Album of Mughal and Persian paintings and calligraphy; Institute of Oriental Manuscripts, St Petersburg", WP + "St._Petersburg_Muraqqa", 0],
 ["Jahangir Preferring a Sufi Shaikh to Kings (Bichitr, c. 1615–1618)", "Albums of Jahangir's reign", "Allegorical album page from the St Petersburg album; Freer Gallery of Art, Washington", WP + "Jahangir_Preferring_a_Sufi_Shaikh_to_Kings", 0],
 ["Minto Album", "Albums of Shah Jahan's reign", "Jahangir- and Shah Jahan-period album pages; Chester Beatty Library, Dublin, and V&A London", WP + "Minto_Album", 0],
 ["Shah Jahan Album (Kevorkian Album, c. 1620–1820)", "Albums of Shah Jahan's reign", "Fifty album folios of portraits and natural history; Metropolitan Museum of Art (41) and Freer Gallery (9)", WP + "Shah_Jahan_Album", 0],
 ["Padshahnama (Windsor, c. 1630–1657)", "Manuscripts of Shah Jahan's reign", "Illustrated official chronicle of Shah Jahan; Royal Collection, Windsor Castle", WP + "Padshahnama", 0],
]
COLL = [
 ("Victoria and Albert Museum, London", 2909), ("Cleveland Museum of Art", 1224),
 ("National Museum of Asian Art (Freer and Sackler), Smithsonian, Washington", 90), ("Museum Volkenkunde, Leiden", 40),
 ("Art Institute of Chicago", 16), ("Aga Khan Museum, Toronto", 12),
]
EXTRA = {"A1-4": MUGHAL_WORKS + [[n, "Collections", f"{c} Mughal paintings and album pages in the gathered object records", "computed: data/interim/regional/*_objects.csv", 0] for n, c in COLL]}

import json, os
_inp = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "va_in", "bucket_named_movements.json")))["leaves"]
GROUP_OF = {}
for _l in _inp:
    if _l["code"] != "A1-4": continue
    for _r in _l["rows"]:
        if not _r[4] and _r[1] in ("", ): continue
        g = MANUAL.get(_r[0]) or (mughal_group(_r[0], _r[2], _r[1]) if _r[4] else None)
        if g: GROUP_OF[("A1-4", _r[0])] = g
