"""A1 Manuscript & Album Painting."""
import re
from common import *

NOISE = re.compile(r"(Papyrus Berlin|^\s*$|Clermont|Hamburg|Portolan|Letter from|Moabit|lexicon|Tafsir|Misbah|Suwar al-aqalim|Al-Hisn|Kitab almulahhas|"
                   r"Maronite|MS\. Greaves|Al – Mustamlah|Maddat al-baqa|Book of Healing|Kitab al-Aqa)", re.I)
QURAN = re.compile(r"(Qur|Koran|Quran|Mushaf|Muṣḥaf|Codex (Parisino|Mashhad)|Sana'a manuscript|Birmingham Quran|Topkapi manuscript|Calligraph|Muraqqa|Karahisari)", re.I)


def o(x):
    return low(x, "origin", "origin_resolved", "culture")


def not_persian(x):
    s = o(x)
    return any(k in s for k in ("mughal", "deccan", "bijapur", "golconda", "malwa", "ottoman", "lahore", "agra", "delhi", "india", "rum", "konya", "zengid"))


def persian_school(x):
    s, yy, lab = o(x), y(x), x["label"]
    if QURAN.search(lab) or NOISE.search(lab) or not_persian(x) or re.search(r"Letter|Page of", lab):
        return None
    if any(k in s for k in ("syria", "egypt", "mamluk", "umayyad", "abbasid")) or (yy and yy < 1256):
        return None
    if "jalayir" in s:
        return "Jalayirid manuscripts (Baghdad, Tabriz)"
    if "ilkhan" in s or (yy and 1256 <= yy <= 1340 and "shiraz" not in s):
        return "Ilkhanid manuscripts (Tabriz, Baghdad, Maragha)"
    if "shiraz" in s and yy and yy < 1400:
        return "Injuid and Muzaffarid Shiraz manuscripts"
    if ("timurid" in s and (yy is None or yy <= 1510)) or (yy and 1395 <= yy <= 1506):
        if "shiraz" in s:
            return "Timurid Shiraz manuscripts"
        if any(k in s for k in ("aq qoyunlu", "lahijan", "turkman")) and "herat" not in s:
            return "Turkman manuscripts (Tabriz, Shiraz)"
        if "samarkand" in s:
            return "Timurid Samarkand manuscripts"
        return "Timurid Herat manuscripts"
    if yy and yy > 1506:
        if "tabriz" in s:
            return "Safavid Tabriz manuscripts"
        if "shiraz" in s:
            return "Safavid Shiraz manuscripts"
        if "herat" in s or "bukhara" in s:
            return "Safavid Herat and Shaybanid Bukhara manuscripts"
        if "qazvin" in s or (yy < 1598 and "isfahan" not in s and "mashhad" not in s):
            return "Safavid Qazvin and Mashhad manuscripts"
        if yy >= 1722:
            return "Afsharid, Zand and Qajar manuscripts"
        return "Safavid Isfahan manuscripts"
    return "Undated Persian manuscripts"


P_ORDER = ["Ilkhanid manuscripts (Tabriz, Baghdad, Maragha)", "Injuid and Muzaffarid Shiraz manuscripts", "Jalayirid manuscripts (Baghdad, Tabriz)",
           "Timurid Herat manuscripts", "Timurid Samarkand manuscripts", "Timurid Shiraz manuscripts", "Turkman manuscripts (Tabriz, Shiraz)", "Safavid Tabriz manuscripts",
           "Safavid Herat and Shaybanid Bukhara manuscripts", "Safavid Shiraz manuscripts", "Safavid Qazvin and Mashhad manuscripts", "Safavid Isfahan manuscripts",
           "Afsharid, Zand and Qajar manuscripts", "Undated Persian manuscripts"]

PERSIANATE = "Islamic book arts: Persianate (see islamic_world.py)"
ARABIC = "Islamic book arts: Arabic (see islamic_world.py)"
OTTOMAN = "Islamic book arts: Ottoman (see islamic_world.py)"
ISL = {PERSIANATE, ARABIC, OTTOMAN, "Islamic book arts: Maghrebi / Andalusi (see islamic_world.py)", "South Asian manuscripts (unlocalised)"}


def arab_phase(x):
    lab, s, yy = x["label"], o(x), y(x)
    if QURAN.search(lab) or NOISE.search(lab) or "iran" in s or "timurid" in s or "ottoman" in s or "afsharid" in s:
        return None
    if not (x["illuminated_class"] == "1" or re.search(r"Maqamat|Kalila|Wonders|Diryaq|Hadith Bayad|materia medica|Kawakib|Fixed Stars|Baytarah|Hiyal|Sufi", lab, re.I)):
        return None
    if "mamluk" in s or (yy and yy > 1260):
        return "Mamluk and later manuscripts (Cairo, Damascus, Syria)"
    if yy:
        return "Abbasid and Jaziran manuscripts (Baghdad, Mosul, to 1258)"
    return "Undated Arabic illustrated manuscripts"


ARAB_ORDER = ["Abbasid and Jaziran manuscripts (Baghdad, Mosul, to 1258)", "Mamluk and later manuscripts (Cairo, Damascus, Syria)", "Undated Arabic illustrated manuscripts"]


def ottoman_phase(x):
    lab, s, yy = x["label"], o(x), y(x)
    if x["tradition"] not in ISL or "ottoman" not in s and x["tradition"] != OTTOMAN:
        return None
    if QURAN.search(lab) or NOISE.search(lab) or "zengid" in s or "karaman" in s or x["illuminated_class"] != "1":
        return None
    if yy and yy < 1566:
        return "Manuscripts of Mehmed II to Süleyman (to 1566)"
    if yy and yy <= 1603:
        return "Manuscripts of Selim II and Murad III (1566–1603)"
    if yy:
        return "17th–18th-century manuscripts and albums"
    return "Undated Ottoman manuscripts"


DECCAN = re.compile(r"bijapur|vijayapura|golconda|hyderabad|ahmadnagar|deccan|bidar", re.I)


def deccan(x):
    s = o(x)
    if not DECCAN.search(s) or NOISE.search(x["label"]):
        return None
    if "bijapur" in s or "vijayapura" in s:
        return "Bijapur manuscripts and album paintings"
    if "golconda" in s or "hyderabad" in s:
        return "Golconda and Hyderabad paintings"
    return "Ahmadnagar and other Deccani paintings"


PAHARI = re.compile(r"nurpur|basohli|kangra|guler|chamba|mandi|garhwal|kulu|jammu|bilaspur|jasrota|mankot", re.I)
RAJ = re.compile(r"mewar|udaipur|bundi|kota|jaipur|amber|jodhpur|marwar|bikaner|kishangarh|malwa|mathura|deogarh|nathdwara", re.I)

BYZ_TRADS = {"Byzantine / Greek manuscripts (undated)", "Byzantine, Early (to 843)", "Byzantine, Middle (843-1204)",
             "Byzantine, Palaiologan (1204-1453)", "Byzantine (style recorded)", "Post-Byzantine Greek (1453+)"}
BYZ_ILL = {"Madrid Skylitzes", "Rossano Gospels", "Sinope Gospels", "Vienna Dioscurides", "Vienna Genesis", "Cotton Genesis", "Ambrosian Iliad",
           "Naples Dioscurides", "Joshua Roll", "Paris Psalter", "Menologion of Basil II", "Chludov Psalter", "The Homilies of James of Kokkinobaphos",
           "Homilies of St. Gregory of Nazianzus", "Theological treatises of John VI Kantakouzenos", "Trebizond Gospel", "Berlin Genesis",
           "Oracles of Leo the Wise", "Codex Beratinus", "Klontzas Marciana Manuscript", "Thesaurus Picturarum", "Uspenski Gospels"}


def byz(x):
    if x["tradition"] not in BYZ_TRADS:
        return None
    lab = x["label"]
    if not (x["illuminated_class"] == "1" or lab in BYZ_ILL or lab.startswith("Theological treatises of John VI")):
        return None
    yy, t = y(x), x["tradition"]
    if t.startswith("Post") or (yy and yy >= 1453):
        return "Post-Byzantine manuscripts (after 1453)"
    if "Early" in t or (yy and yy < 843):
        return "Early Byzantine manuscripts (to 843)"
    if "Palaiologan" in t or (yy and yy > 1204):
        return "Palaiologan manuscripts (1261–1453)"
    if "Middle" in t or yy:
        return "Middle Byzantine manuscripts (843–1204)"
    return "Byzantine illuminated manuscripts, undated"


BYZ_ORDER = ["Early Byzantine manuscripts (to 843)", "Middle Byzantine manuscripts (843–1204)", "Palaiologan manuscripts (1261–1453)",
             "Byzantine illuminated manuscripts, undated", "Post-Byzantine manuscripts (after 1453)"]

BORGIA = {"Codex Borgia", "Codex Cospi", "Codex Laud", "Codex Vaticanus B", "Codex Fejérváry-Mayer"}
MIXTEC = {"Codex Zouche-Nuttall", "Codex Vindobonensis Mexicanus I", "Codex Selden", "Codex Bodley", "Codex Colombino-Becker", "Codex Colombino", "Codex Waecker-Gotter", "Selden Roll"}
AZ_RIT = {"Codex Borbonicus", "Aubin Tonalamatl", "Codex Ríos", "Codex Telleriano-Remensis"}
AZ_HIST = {"Codex Azcatitlan", "Codex Boturini", "Aubin Codex", "Codex Mendoza", "Lienzo de Tlaxcala", "Historia de Tlaxcala", "Codex Cozcatzin",
           "Codex Escalada", "Codex Totomixtlahuaca", "Codex Ixtlilxóchitl", "Crónica Mexicayotl", "Anales de Tlatelolco", "Historia Tolteca-Chichimeca"}
AZ_ENC = {"Florentine Codex", "Codex Durán", "Libellus de Medicinalibus Indorum Herbis", "Relation of Michoacan"}


def aztec(x):
    lab = x["label"]
    if lab in AZ_RIT:
        return "Ritual and calendrical codices"
    if lab in AZ_HIST:
        return "Historical, migration and tribute codices"
    if lab in AZ_ENC:
        return "Colonial encyclopaedic and missionary codices"
    return None


ARM_TR = {"Armenian (later or unlocalised)": "Later and unlocalised Armenian manuscripts", "Armenian: Ani / early Armenian (to 1200)": "Early Armenian manuscripts (to 1200)",
          "Armenian: Vaspurakan school": "Vaspurakan school manuscripts", "Armenian: Cilician school": "Cilician school manuscripts",
          "Armenian: New Julfa / diaspora": "New Julfa and diaspora manuscripts"}
ARM_ORDER = ["Early Armenian manuscripts (to 1200)", "Cilician school manuscripts", "Vaspurakan school manuscripts", "New Julfa and diaspora manuscripts",
             "Later and unlocalised Armenian manuscripts"]

ETH = {"Ethiopian (Ge'ez)", "Ethiopian (Ge'ez), early (to 1500)", "Ethiopian (Ge'ez), Gondarine and later"}


def eth_paint(x):
    if x["tradition"] not in ETH or re.search(r"Papyrus|scroll", x["label"], re.I):
        return None
    if not (x["illuminated_class"] == "1" or "Gospel" in x["label"] or "Gospel" in x["genres"]):
        return None
    yy = y(x)
    if "early" in x["tradition"] or (yy and yy < 1500):
        return "Early Ethiopian manuscripts (Aksumite to 15th century)"
    return "Gondarine and later manuscripts (16th–18th century)"


def coll_trad(*trads, f=None):
    d = {"trad": list(trads)}
    if f:
        d["cfilter"] = f
    return d


CFG = {
    "A1-1": dict(
        axis="Schools by centre (Baghdad, Mosul, Mamluk Cairo and Damascus); works: every gathered illustrated Arabic manuscript with sitelinks ≥ 1 (Qur'ans, papyri and text-only items excluded), by phase; then collections and painter-scribes.",
        regroup={"Baghdad school": "Schools & phases"},
        gloss={"Baghdad school": "13th-century Abbasid book painting of Baghdad: the Maqamat of al-Hariri, Rasa'il Ikhwan al-Safa, Dioscorides"},
        add=[("Mamluk painting", "Schools & phases", "14th-century book painting of Cairo and Damascus: Maqamat, Kalila wa Dimna, furusiyya and automata treatises", "Mamluk Sultanate"),
             ("Maqamat al-Hariri", "Sub-types", "al-Hariri's picaresque tales, the most often illustrated Arabic text (c. 13 illustrated copies, 1220s–1330s)", "Maqamat al-Hariri"),
             ("Kalila wa Dimna", "Sub-types", "Arabic animal fables of Ibn al-Muqaffa, illustrated in Syria and Egypt from the 13th century", "Kalīla wa-Dimna"),
             ("Book of Antidotes of Pseudo-Galen (Kitab al-Diryaq)", "Sub-types", "illustrated pharmacological treatise, Jazira copies 1199 (BnF) and c. 1250 (Vienna)", "Kitab al-Diryaq"),
             ("Book of Knowledge of Ingenious Mechanical Devices (al-Jazari)", "Sub-types", "al-Jazari's 1206 treatise on automata, illustrated copies Syria and Egypt 13th–14th c.", "Book of Knowledge of Ingenious Mechanical Devices")],
        ms=dict(trad=[ARABIC], section=arab_phase, order=ARAB_ORDER),
        coll_ms=coll_trad(ARABIC, f=lambda x: not QURAN.search(x["label"])),
        cat=[met("Maqamat"), GALLICA, wp("Arabic miniature", "survey of Arab book painting with its principal illustrated manuscripts")],
    ),
    "A1-2": dict(
        axis="Schools by dynasty and centre (Ilkhanid Tabriz to Safavid Isfahan), canonical sequence; works: every gathered Persian illustrated manuscript or album folio with sitelinks ≥ 1 (Mughal, Deccani and Ottoman items go to those leaves; Qur'ans to Islamic Illumination), by school; then collections; painters grouped by school.",
        regroup={"Isfahan school": "Schools & phases", "Shiraz school (Safavid)": "Schools & phases", "Shiraz school (Timurid)": "Schools & phases",
                 "Herat school": "Schools & phases", "Tabriz school (Safavid)": "Schools & phases", "Qazvin school": "Schools & phases",
                 "Ilkhanid Tabriz": "Schools & phases", "Inju school (Shiraz)": "Schools & phases", "Bukhara school": "Schools & phases"},
        gloss={"Isfahan school": "Safavid capital school from c. 1598: single-page album painting of Riza-yi 'Abbasi and followers",
               "Shiraz school (Safavid)": "commercial Shiraz workshops, 16th century, producing many Shahnamas and Khamsas",
               "Shiraz school (Timurid)": "Timurid Shiraz under Iskandar Sultan and Ibrahim Sultan, early 15th century",
               "Herat school": "Timurid Herat under Baysunghur and Sultan Husayn Bayqara, c. 1420–1507; Bihzad",
               "Tabriz school (Safavid)": "early Safavid court workshop of Shah Isma'il and Tahmasp, 1501–48: Shahnama of Shah Tahmasp",
               "Qazvin school": "Safavid capital 1548–98: elongated figures, album pages; Shahnama of Isma'il II",
               "Ilkhanid Tabriz": "Mongol court centre, c. 1300–1336: Jami' al-Tawarikh, Great Mongol Shahnama",
               "Inju school (Shiraz)": "Injuid Shiraz, 1330s–1350s: small Shahnamas with red and gold grounds",
               "Bukhara school": "Shaybanid Bukhara, 16th century, continuing the Herat manner of Bihzad's pupils",
               "Muhammad Yusuf": "Safavid painter, Isfahan, fl. 1630–60", "Afzal Al-Husayni": "Isfahan painter, fl. 1640s",
               "Muʿin Musavvir": "Isfahan painter, pupil of Riza, fl. 1635–97", "Muhammad Qasim": "Isfahan painter and poet, d. 1659/60",
               "Muhammad Siya Qalam": "15th-century album painter of the Siyah Qalam demons and nomads; attribution debated",
               "Mirak": "Mirak Naqqash, Herat painter-illuminator, teacher of Bihzad", "Darvish Muhammad": "Aq Qoyunlu court painter, late 15th century",
               "Yahya ibn Mahmud al-Wasiti": "Baghdad painter-scribe of the 1237 Maqamat (Arab painting)", "Jamal al-Din Muhammad Isfahani": "Persian painter"},
        grp_map={"Isfahan school": "Isfahan school painters", "Herat school": "Herat school painters", "Tabriz school (Safavid)": "Tabriz school painters",
                 "Qazvin school": "Qazvin school painters", "Turkman school": "Turkman and Jalayirid painters", "Jalayirid school": "Turkman and Jalayirid painters",
                 "Ilkhanid Tabriz": "Turkman and Jalayirid painters"},
        add=[("Muzaffarid Shiraz", "Schools & phases", "Shiraz under the Muzaffarids, 1350s–1393, precursor of the Timurid style", "Muzaffarid dynasty"),
             ("Siyah Qalam", "Schools & phases", "'black pen' album drawings of demons and nomads, Turkman Tabriz c. 1450–1500 (Topkapı albums)", "Siyah Qalam"),
             ("Shahnameh of Shah Tahmasp (Sultan Muhammad and others, c. 1522–40)", "Safavid Tabriz manuscripts", "the 258-painting royal Shahnama, Tabriz; folios dispersed (Met, Aga Khan Museum...)", "Shahnameh of Shah Tahmasp"),
             ("Khamsa of Nizami (British Library, Or. 2265)", "Safavid Tabriz manuscripts", "Tabriz, 1539–43, for Shah Tahmasp; paintings by Sultan Muhammad, Aqa Mirak, Mir Sayyid Ali; British Library", "Khamsa of Nizami (British Library, Or. 2265)"),
             ("Haft Awrang of Ibrahim Mirza (Freer Jami)", "Safavid Qazvin and Mashhad manuscripts", "Mashhad, 1556–65, for Sultan Ibrahim Mirza; Freer Gallery of Art, Washington", "Freer Jami")],
        ms=dict(trad=[PERSIANATE], section=persian_school, order=P_ORDER),
        coll_ms=coll_trad(PERSIANATE, f=lambda x: not not_persian(x) and not QURAN.search(x["label"])),
        coll_obj=[("islamic_objects.csv", lambda x: x["book_arts"] == "1" and x["dynasty"].split(";")[0].strip() in ("Ilkhanid", "Timurid", "Safavid", "Injuid", "Aq Qoyunlu", "Jalayirid", "Timurid; Safavid"))],
        order=["Schools & phases"] + P_ORDER + ["Collections", "Turkman and Jalayirid painters", "Herat school painters", "Tabriz school painters", "Qazvin school painters", "Isfahan school painters", "Makers"],
        cat=[SHAHNAMA, met("Safavid"), si("Persian manuscript"), BODLEIAN, vam("Persian manuscript")],
    ),
    "A1-3": dict(
        axis="Workshop and phase (nakkaşhane of Mehmed II to the Tulip Period); works: every gathered Ottoman illustrated manuscript or album (illuminated flag, sitelinks ≥ 1; Qur'ans excluded), by reign; then collections and painters by date.",
        regroup={"Ottoman court atelier (nakkaşhane)": "Centres & workshops"},
        gloss={"Ottoman court atelier (nakkaşhane)": "the palace painting studio of Istanbul, 15th–18th century",
               "Mustafa": "nakkaşhane painter of the Surname-i Hümayun (1582)", "Feramruz?": "nakkaşhane painter of the Surname-i Hümayun (1582)",
               "Ali": "nakkaşhane painter of the Surname-i Hümayun (1582)", "Mehmet Haydar": "nakkaşhane painter of the Surname-i Hümayun (1582)",
               "Recep Abdullah": "nakkaşhane painter of the Surname-i Hümayun (1582)", "Al-fakir Süleyman": "painter of a portrait of Ahmed I",
               "Hüseyin al-Istanbuli": "painter of an Ottoman genealogy scroll", "Attributed to Vali Jan": "Vali Jan, Persian émigré saz-style painter, Istanbul late 16th c.",
               "Rupen Manas": "Armenian painter at the Ottoman court, 17th century", "Kapidagli, Konstantin": "Konstantin Kapıdağlı, court painter of Selim III's portraits, c. 1800",
               "Matrakçı Nasuh": "polymath and topographical painter, Beyan-ı Menazil (1537)", "Levni": "court painter of the Surname-i Vehbi (c. 1720), Tulip Period",
               "Nakkaş Osman": "head painter of Murad III's histories: Hünername, Surname-i Hümayun", "Anthim the Iberian": "Georgian-born printer and engraver active in Wallachia"},
        add=[("Şahname-i Selim Han", "Schools & phases", "illustrated dynastic history (1581), Topkapı Palace Library", "Şehname-i Selim Han"),
             ("Hünername", "Manuscripts of Selim II and Murad III (1566–1603)", "Lokman and Nakkaş Osman, 1584–88, Topkapı Palace Library", "Hünername"),
             ("Surname-i Hümayun", "Manuscripts of Selim II and Murad III (1566–1603)", "festival book of the 1582 circumcision feast, Nakkaş Osman's workshop; Topkapı", "Surname-i Hümayun"),
             ("Surname-i Vehbi", "17th–18th-century manuscripts and albums", "Levni's festival book of 1720, Topkapı Palace Library", "Surname-i Vehbi"),
             ("Beyan-ı Menazil", "Manuscripts of Mehmed II to Süleyman (to 1566)", "Matrakçı Nasuh's topographical account of the Iraq campaign, 1537; Istanbul University Library", "Matrakçı Nasuh"),
             ("Süleymanname", "Manuscripts of Mehmed II to Süleyman (to 1566)", "Arifi's history of Süleyman, 1558, Topkapı Palace Library", "Süleymanname")],
        ms=dict(trad=[OTTOMAN, PERSIANATE], section=ottoman_phase,
                order=["Manuscripts of Mehmed II to Süleyman (to 1566)", "Manuscripts of Selim II and Murad III (1566–1603)", "17th–18th-century manuscripts and albums", "Undated Ottoman manuscripts"]),
        coll_ms=coll_trad(OTTOMAN, f=lambda x: not QURAN.search(x["label"])),
        coll_obj=[("islamic_objects.csv", lambda x: x["book_arts"] == "1" and x["dynasty"].startswith("Ottoman"))],
        cat=[met("Ottoman manuscript"), si("Ottoman"), wp("Ottoman miniature", "survey with the principal illustrated Ottoman manuscripts")],
    ),
    "A1-5": dict(
        axis="Schools by sultanate (Ahmadnagar, Bijapur, Golconda, Hyderabad); works: every gathered Deccani manuscript or painting with sitelinks ≥ 1, by sultanate; then collections and painters.",
        regroup={"Golconda school": "Schools & phases", "Hyderabad school": "Schools & phases", "Bijapur school": "Schools & phases",
                 },
        to_alias=["Deccani: Golconda", "Bijapur"],
        persons=["Rahim Deccani"],
        gloss={"Golconda school": "Qutb Shahi court painting, Golconda, late 16th–17th century", "Hyderabad school": "Asaf Jahi painting of Hyderabad, 18th–19th century",
               "Bijapur school": "Adil Shahi court painting under Ibrahim Adil Shah II (r. 1580–1627)", "Ali Riza, the \"Bodleian Painter\"": "Bijapur painter, fl. 1605–30",
               "Shafi": "Bijapur painter of a marbled picture, c. 1650", "Rahim Deccani": "Deccani painter, 17th century"},
        add=[("Ahmadnagar school", "Schools & phases", "Nizam Shahi court painting: the Tarif-i Husain Shahi (c. 1565)", "Ahmadnagar Sultanate"),
             ("Tarif-i Husain Shahi", "Ahmadnagar and other Deccani paintings", "Ahmadnagar, c. 1565–69, earliest Deccani manuscript; Bharata Itihasa Samshodhaka Mandala, Pune", "Tarif-i Husain Shahi"),
             ("Nujum al-Ulum (Stars of the Sciences)", "Bijapur manuscripts and album paintings", "Bijapur, 1570; Chester Beatty Library, Dublin", "Nujum al-Ulum"),
             ("Farrukh Beg", "Makers", "Persian-born painter at Bijapur and the Mughal court, c. 1545–c. 1615", "Farrukh Beg")],
        ms=dict(trad=[], section=deccan, order=["Ahmadnagar and other Deccani paintings", "Bijapur manuscripts and album paintings", "Golconda and Hyderabad paintings"]),
        coll_obj=[("islamic_objects.csv", lambda x: x["school_workshop"].startswith("Deccani") and x["book_arts"] == "1"),
                  ("south_southeast_asia_objects.csv", lambda x: x["culture"].startswith("Deccani") and x["object_group"] == "painting")],
        cat=[met("Deccan"), vam("Deccani painting"), wp("Deccan painting", "survey with schools and principal works")],
    ),
    "A1-6": dict(
        axis="Centres of production (Murshidabad, Patna, Calcutta, Lucknow, Delhi, Tanjore, Trichinopoly, Punjab), then collections and painters.",
        to_alias=["Company school"],
        persons=["Shiva Lal", "Bahadur Lal II", "Brahmin Sadanand"],
        grp_map={"Delhi": "Makers", "Punjab": "Makers", "Patna": "Makers"},
        gloss={"Mazhar Ali Khan": "Delhi Company painter of monuments, fl. 1840–60", "Faiz Ali Khan": "Delhi Company painter, mid-19th century",
               "Khan, Ghulam Ali": "Ghulam Ali Khan, Delhi painter for William Fraser and the Skinner family, fl. 1817–52", "Jiwan Ram": "Delhi Company portraitist, fl. 1820s–40s",
               "Kehar Singh": "Lahore painter of trades and costumes, Sikh period", "Shiva Lal": "Patna Company painter, 19th century",
               "Bahadur Lal II": "Patna Company painter, late 19th century", "Brahmin Sadanand": "Company-period painter"},
        add=[("Patna school", "Centres & workshops", "Company painting of Patna and Arrah, c. 1770–1900, Sewak Ram to Shiva Lal", "Patna School"),
             ("Murshidabad", "Centres & workshops", "Bengal Nawabi court centre where Company painting began, c. 1760s–80s", "Murshidabad"),
             ("Tanjore Company painting", "Centres & workshops", "Thanjavur sets of castes, deities and festivals for British buyers, c. 1770–1830", "Thanjavur painting"),
             ("Fraser Album", "Sub-types", "Delhi paintings of 1815–19 for William and James Fraser by Ghulam Ali Khan's circle", "Fraser Album"),
             ("Impey Album", "Sub-types", "natural-history paintings for Lady Impey, Calcutta, 1774–82, by Shaikh Zain al-Din and others", "Impey Album"),
             ("Shaikh Zain al-Din", "Makers", "Patna-born painter of the Impey natural-history album, Calcutta, fl. 1770s–80s", "Shaikh Zain al-Din"),
             ("Sita Ram", "Makers", "painter for Lord Hastings' tour of 1814–15, Bengal", "Sita Ram (artist)"),
             ("Sewak Ram", "Makers", "early Patna Company painter, c. 1770–1830", "Sewak Ram")],
        coll_obj=[("islamic_objects.csv", lambda x: x["school_workshop"] == "Company school"),
                  ("south_southeast_asia_objects.csv", lambda x: x["culture"] == "Company school")],
        cat=[vam("Company painting"), bm("Company school"), wp("Company painting", "survey with centres and painters")],
    ),
    "A1-7": dict(
        axis="Court schools in canonical order (Mewar, Bundi, Kota, Kishangarh, Jaipur, Marwar, Bikaner, Malwa, then smaller thikanas); then named painters by school. No gathered named-manuscript catalogue exists for the tradition; Collections ranks museums by objects.",
        to_alias=["Rajput", "Rajput: Jaipur (Amber)", "Western India, Jhilai"],
        regroup={n: "Schools & phases" for n in ["Rajput: Mewar", "Rajput: Kota", "Rajput: Marwar (Jodhpur)", "Rajput: Malwa", "Rajput: Bikaner", "Rajput: Bundi",
                                                 "Kishangarh", "Nathdwara", "Bundelkhand", "Sirohi", "Raghogarh", "Deogarh", "Isarda", "Sawar", "Alwar"]},
        rename={"Rajput: Mewar": "Mewar school", "Rajput: Kota": "Kota school", "Rajput: Marwar (Jodhpur)": "Marwar (Jodhpur) school", "Rajput: Malwa": "Malwa school",
                "Rajput: Bikaner": "Bikaner school", "Rajput: Bundi": "Bundi school", "Kishangarh": "Kishangarh school", "Nathdwara": "Nathdwara school"},
        gloss={"Rajput: Mewar": "Udaipur court, from the Chawand Ragamala (1605) to 19th-century court scenes", "Rajput: Kota": "hunting scenes of the Kota court, 18th–19th century",
               "Rajput: Marwar (Jodhpur)": "Jodhpur court painting, peaking under Man Singh (r. 1803–43)", "Rajput: Malwa": "Central Indian school, 17th century: Rasikapriya and Ragamala sets",
               "Rajput: Bikaner": "Bikaner court painting with strong Mughal-trained ustads, 17th–18th century", "Rajput: Bundi": "Bundi court, lush landscapes and ragamalas, 17th–19th century",
               "Kishangarh": "Kishangarh court under Savant Singh, elongated Radha figures (Bani Thani)", "Nathdwara": "temple-town painting for the Shrinathji shrine, Pushtimarg",
               "Bundelkhand": "Datia and Orchha courts, Central India", "Sirohi": "Sirohi court, southern Rajasthan", "Raghogarh": "Raghogarh thikana, Central India",
               "Deogarh": "Mewar thikana of Deogarh, 18th–19th century (Chokha, Bagta)", "Isarda": "Isarda thikana near Jaipur", "Sawar": "Sawar thikana near Ajmer",
               "Alwar": "Alwar court, late 18th–19th century", "Chokha": "Mewar and Deogarh painter, fl. 1799–1826", "Nasiruddin": "painter of the Chawand Ragamala (1605), Mewar",
               "Mewar Stipple Master": "anonymous Mewar painter of stippled court scenes, c. 1690–1710", "Jiva": "Mewar court painter, 18th century",
               "Jugarsi": "Mewar court painter", "Ruknuddin": "Bikaner ustad, fl. 1650–97", "Ustad Murad": "Bikaner painter, 18th century", "Nathu": "Bikaner painter",
               "Sahib Ram": "Jaipur court portraitist, late 18th century", "Chhajju Lal": "Jaipur painter", "Amar Das Bhatti": "Marwar painter, 19th century",
               "Dana Bhatti": "Marwar painter, 19th century", "Ghasiram": "Ghasiram Hardev Sharma, Nathdwara painter (1869–1930)"},
        persons=["Chokha", "Nasiruddin", "Mewar Stipple Master", "Jiva", "Jugarsi", "Ruknuddin", "Ustad Murad", "Nathu", "Sahib Ram", "Chhajju Lal", "Amar Das Bhatti", "Dana Bhatti", "Ghasiram"],
        add=[("Jaipur (Amber) school", "Schools & phases", "Kachhwaha court of Amber and Jaipur, 17th–19th century", "Jaipur painting"),
             ("Bagta", "Makers", "Deogarh and Mewar painter, fl. 1761–1814", "Bagta"),
             ("Sahibdin", "Makers", "Mewar master of the Ramayana and Ragamala sets, fl. 1628–55", "Sahibdin")],
        coll_obj=[("south_southeast_asia_objects.csv", lambda x: x["culture"].startswith("Rajput") and x["object_group"] == "painting")],
        cat=[met("Rajput"), vam("Rajasthan painting"), MUS_INDIA, wp("Rajput painting", "survey of the court schools and their works")],
    ),
    "A1-8": dict(
        axis="Hill-court schools from the Basohli phase to the Guler–Kangra phase (Basohli, Nurpur, Mankot, Jasrota, Guler, Kangra, Chamba, Mandi, Kulu, Bilaspur, Garhwal, Jammu); works: every gathered Pahari manuscript with sitelinks ≥ 1; then collections and painters (family of Pandit Seu first).",
        to_alias=["Pahari", "Pahari painting"],
        regroup={n: "Schools & phases" for n in ["Pahari: Kangra", "Pahari: Guler", "Pahari: Garhwal", "Pahari: Kulu", "Pahari: Chamba", "Pahari: Mandi", "Pahari: Jammu",
                                                 "Pahari: Bilaspur", "Pahari: Nurpur", "Pahari: Basohli", "Mankot", "Jasrota", "Arki"]},
        rename={k: k.replace("Pahari: ", "") + " school" for k in ["Pahari: Kangra", "Pahari: Guler", "Pahari: Garhwal", "Pahari: Kulu", "Pahari: Chamba", "Pahari: Mandi",
                                                                   "Pahari: Jammu", "Pahari: Bilaspur", "Pahari: Nurpur", "Pahari: Basohli"]},
        gloss={"Pahari: Basohli": "bold early style, c. 1660–1730: Rasamanjari of Kripal", "Pahari: Guler": "family of Pandit Seu (Manaku, Nainsukh), Guler, c. 1740–80",
               "Pahari: Kangra": "lyrical later phase under Sansar Chand (r. 1775–1823): Gita Govinda, Bhagavata Purana", "Pahari: Garhwal": "Garhwal court, Mola Ram and the Guler-trained painters",
               "Pahari: Kulu": "Kulu court, 18th century: Shangri Ramayana", "Pahari: Chamba": "Chamba court, 18th–19th century", "Pahari: Mandi": "Mandi court, 17th–19th century",
               "Pahari: Jammu": "Jammu and Jasrota courts, Nainsukh's patron Balwant Singh", "Pahari: Bilaspur": "Bilaspur (Kahlur) court, 17th–18th century",
               "Pahari: Nurpur": "Nurpur court, Golu and Devidasa, late 17th–18th century", "Mankot": "Mankot court, early 18th century", "Jasrota": "Jasrota, Nainsukh's base under Balwant Singh",
               "Arki": "Arki (Baghal) court, 18th–19th century", "Nainsukh": "Guler painter for Balwant Singh of Jasrota (c. 1710–1778)", "Manaku": "Guler painter, elder son of Pandit Seu (c. 1700–1760)",
               "Fattu": "Guler-Kangra painter, son of Manaku", "Purkhu": "Kangra court painter of Sansar Chand, fl. 1780–1820", "Sanju": "Pahari painter",
               "Mola Ram": "Garhwal painter and poet (1743–1833)", "Mangat Ram": "Garhwal painter", "Mangnu": "Chamba painter", "Kripal of Nurpur": "painter of the Basohli Rasamanjari (1695)",
               "Master of the court of Mandi": "anonymous Mandi master, early 18th century"},
        persons=["Nainsukh", "Manaku", "Fattu", "Purkhu", "Sanju", "Mola Ram", "Mangat Ram", "Mangnu", "Kripal of Nurpur", "Master of the court of Mandi"],
        add=[("Pandit Seu", "Makers", "Guler painter (c. 1680–1740), father of Manaku and Nainsukh", "Pandit Seu"),
             ("Devidasa", "Makers", "Nurpur painter of the 1694 Basohli Rasamanjari", "Devidasa")],
        ms=dict(trad=[], filter=lambda x: bool(PAHARI.search(o(x))), section=lambda x: "Pahari illustrated sets and manuscripts"),
        coll_obj=[("south_southeast_asia_objects.csv", lambda x: x["culture"].startswith("Pahari") and x["object_group"] == "painting")],
        cat=[met("Pahari"), vam("Pahari painting"), MUS_INDIA, wp("Pahari painting", "survey of schools and their works")],
    ),
    "A1-9": dict(
        axis="Sub-types by text (Kalpasutra, Kalakacharya-katha), then every gathered Jain illustrated manuscript with sitelinks ≥ 1 by date, then collections.",
        to_alias=["Western Indian (Jain)"], regroup={"Kalpasutra and Jain illustrated texts": "Sub-types"},
        rename={"Kalpasutra and Jain illustrated texts": "Kalpasutra"},
        gloss={"Kalpasutra and Jain illustrated texts": "the life of the Jinas, most often illustrated Jain text, palm leaf then paper, 13th–16th c."},
        add=[("Kalakacharya-katha", "Sub-types", "story of the monk Kalaka, bound with Kalpasutras from the 14th century", "Kalakacharya"),
             ("Western Indian style", "Schools & phases", "angular figures with projecting further eye, Gujarat and Rajasthan, 12th–16th century", "Jain art"),
             ("Patan", "Centres & workshops", "Gujarat centre of Jain manuscript production and libraries (bhandars)", "Patan, Gujarat"),
             ("Jaisalmer", "Centres & workshops", "Jinabhadra Suri bhandar, one of the great Jain manuscript libraries", "Jaisalmer")],
        ms=dict(trad=[], filter=lambda x: (x["tradition"] == "Jain manuscripts (Western Indian style)" or "kalpa" in x["label"].lower()) and x["label"] != "Agama (Jainism)",
                section=lambda x: "Kalpasutra and other Jain manuscripts"),
        coll_obj=[("south_southeast_asia_objects.csv", lambda x: x["culture"] == "Western Indian (Jain)")],
        cat=[met("Kalpasutra"), vam("Jain manuscript"), wp("Jain art", "survey including the Western Indian manuscript style")],
    ),
    "A1-10": dict(
        axis="Sub-types (court portraiture, Janamsakhi illustration), then Lahore and hill painters active for Sikh patrons, by date; collections ranked by gathered Sikh (Punjab) objects. No named Sikh manuscript with sitelinks in the gathered data.",
        add=[("Janamsakhi", "Sub-types", "illustrated hagiographies of Guru Nanak, from the 18th century (B-40 Janamsakhi, 1733)", "Janamsakhi"),
             ("Sikh court portraiture", "Sub-types", "portraits of Maharaja Ranjit Singh and his court, Lahore, 1810s–40s", "Ranjit Singh"),
             ("Purkhu", "Makers", "Kangra painter who also worked for Sikh patrons", "Purkhu"),
             ("Kapur Singh", "Makers", "Amritsar painter of Punjabi trades and portraits, mid-19th century", "Kapur Singh (painter)"),
             ("August Schoefft", "Makers", "Hungarian painter at the Lahore court, 1841, The Court of Lahore", "August Schoefft"),
             ("Emily Eden", "Makers", "English artist who drew Ranjit Singh's court, 1838", "Emily Eden")],
        coll_obj=[("south_southeast_asia_objects.csv", lambda x: x["culture"] == "Sikh (Punjab)" and x["object_group"] == "painting")],
        cat=[vam("Sikh"), met("Sikh"), wp("Sikh art and culture", "survey including Sikh painting")],
    ),
    "A1-11": dict(
        axis="Styles (Sattriya, Ahom court Garhgaya, Darrang), then named manuscripts known from the literature (the gathered rows are noise), then painters; collections ranked by gathered Assam objects.",
        to_alias=["Assamese (Sanchipat) and Bengali manuscripts"],
        add=[("Sattriya style", "Schools & phases", "monastic (sattra) style of Vaishnava manuscripts, 16th–19th century", "Sattriya"),
             ("Garhgaya style", "Schools & phases", "Ahom court style of the capital Garhgaon, 18th century", "Ahom kingdom"),
             ("Sanchipat", "Sub-types", "folios of agarwood bark, the writing and painting surface", "Sanchipat"),
             ("Hastividyarnava", "Named manuscripts", "treatise on elephants painted by Dilbar and Dosai for Siva Singha, 1734; Directorate of Archives, Guwahati", "Hastividyarnava"),
             ("Chitra Bhagavata", "Named manuscripts", "illustrated Bhagavata Purana (Book X), 16th century, Barpeta Satra", "Chitra Bhagavata"),
             ("Dilbar and Dosai", "Makers", "Ahom court painters of the Hastividyarnava (1734)", "Hastividyarnava")],
        coll_obj=[("south_southeast_asia_objects.csv", lambda x: x["culture"] == "Unspecified (Assam)")],
        cat=[wp("Assamese painting", "survey of manuscript painting in Assam"), MUS_INDIA],
    ),
    "A1-12": dict(
        axis="Sub-types (white and black parabaik), then the Konbaung court workshops and named painters by date; collections ranked by gathered parabaik and court-painting objects.",
        regroup={"Burmese court painting": "Schools & phases", "Burmese parabaik manuscript painting": "Sub-types", "Konbaung court workshops (Mindon, Thibaw)": "Centres & workshops"},
        rename={"Burmese parabaik manuscript painting": "White parabaik"},
        gloss={"Burmese court painting": "painting of the Konbaung court at Amarapura and Mandalay, 18th–19th century",
               "Burmese parabaik manuscript painting": "white mulberry-paper folding books painted in watercolour with court and Jataka scenes",
               "Maung Tin Hla": "Mandalay painter of parabaik, late 19th century", "Yatanabon Maung Su": "Mandalay (Yatanabon) parabaik painter, late 19th century",
               "Konbaung court workshops (Mindon, Thibaw)": "royal painters' workshops of Mandalay under Mindon and Thibaw"},
        persons=["Maung Tin Hla", "Yatanabon Maung Su"],
        add=[("Black parabaik", "Sub-types", "blackened folding books written with steatite, used for records and drafts", "Parabaik"),
             ("Saya Chone", "Makers", "Konbaung court painter (1866–1917), bridge to modern Burmese painting", "Saya Chone")],
        coll_obj=[("gap_sweep_objects.csv", lambda x: x["node_label"] in ("Burmese parabaik manuscript painting", "Burmese court painting"))],
        cat=[bm("parabaik"), wp("Parabaik", "the Burmese folding-book form and its painting")],
    ),
    "A1-13": dict(
        axis="Sub-types by text (Phra Malai, Traiphum, treatises), then every gathered named Thai manuscript with sitelinks ≥ 1, then collections.",
        to_alias=["Thai manuscript painting (samut khoi, Phra Malai)"],
        add=[("Phra Malai manuscripts", "Sub-types", "funerary chanting books of the monk Phra Malai's visit to heaven and hell, 18th–19th century", "Phra Malai"),
             ("Traiphum manuscripts", "Sub-types", "illustrated Buddhist cosmologies (Three Worlds), Ayutthaya and Thonburi", "Traiphum Phra Ruang"),
             ("Samut khoi", "Sub-types", "folding books of khoi-bark paper, white or blackened", "Samut khoi")],
        ms=dict(trad=["Thai samut khoi and Lanna manuscripts"], section=lambda x: "Named Thai manuscripts"),
        coll_obj=[("gap_sweep_objects.csv", lambda x: x["node_label"].startswith("Thai manuscript painting"))],
        cat=[bm("Phra Malai"), wp("Samut khoi", "the Thai folding manuscript and its painting")],
    ),
    "A1-14": dict(
        axis="Sub-types (book and scroll formats, otogi-zōshi texts), then every gathered illustrated tale manuscript (monogatari copies) with sitelinks ≥ 1, then collections.",
        to_alias=["Japanese manuscripts and Nara-ehon"],
        add=[("Otogi-zōshi", "Sub-types", "Muromachi and Edo short tales, the main texts of Nara-ehon", "Otogizōshi"),
             ("Emaki format (Nara-emaki)", "Sub-types", "Nara-ehon tales painted as handscrolls", "Emakimono"),
             ("Bunshō sōshi", "Named works", "otogi-zōshi tale of a salt-maker's rise, often illustrated as Nara-ehon", "Bunshō sōshi"),
             ("Shuten-dōji", "Named works", "ogre-slaying tale, one of the most illustrated Nara-ehon subjects", "Shuten-dōji")],
        ms=dict(trad=["Japanese manuscripts and Nara-ehon"], filter=lambda x: bool(re.search(r"monogatari|Genji|ehon|zōshi", x["label"], re.I)),
                section=lambda x: "Illustrated and illuminated tale manuscripts"),
        coll_ms=coll_trad("Japanese manuscripts and Nara-ehon"),
        cat=[COLBASE, wp("Nara-ehon", "the illustrated-book genre and examples")],
    ),
    "A1-15": dict(
        axis="Phases (Aksumite and early Solomonic, Gondarine); works: every gathered Ethiopian painted manuscript (illuminated flag or Gospel book, sitelinks ≥ 1; scrolls go to Ethiopian Magic Scrolls), by phase; then collections.",
        to_alias=["Ethiopian illuminated manuscripts"],
        add=[("First Gondarine style", "Schools & phases", "court painting of Gondar, c. 1630–1730", "Gondarine period"),
             ("Second Gondarine style", "Schools & phases", "18th-century Gondar painting with richer colour and Western prints as models", "Gondarine period"),
             ("Garima Gospels", "Early Ethiopian manuscripts (Aksumite to 15th century)", "Aksumite Gospels, c. 390–660, the oldest illustrated Christian books; Abba Garima Monastery", "Garima Gospels"),
             ("Miracles of Mary (Te'amire Maryam)", "Sub-types", "Marian miracle books, the most richly illustrated Gondarine genre", "Ethiopian art"),
             ("Fere Seyon", "Makers", "15th-century painter at the court of Zara Yaqob, Marian icons and manuscripts", "Ethiopian art")],
        ms=dict(trad=list(ETH), section=eth_paint, order=["Early Ethiopian manuscripts (Aksumite to 15th century)", "Gondarine and later manuscripts (16th–18th century)"]),
        coll_ms=coll_trad(*ETH),
        coll_obj=[("gap_sweep_objects.csv", lambda x: x["node_label"] == "Ethiopian illuminated manuscripts")],
        cat=[VHMML, wp("Ethiopian art", "survey with manuscript painting"), met("Ethiopian manuscript")],
    ),
    "A1-16": dict(
        axis="Phases (Early, Macedonian Renaissance, Komnenian, Palaiologan, post-Byzantine); works: every gathered Byzantine manuscript with painted miniatures (illuminated flag or recorded miniature cycle; numbered New Testament witnesses excluded), sitelinks ≥ 1, by phase; then collections and illuminators.",
        to_alias=["Byzantine, Middle (843-1204)"], regroup={"Macedonian Renaissance": "Schools & phases"},
        gloss={"Macedonian Renaissance": "classicising revival of the 9th–10th century: Paris Psalter, Joshua Roll, Menologion of Basil II",
               "Kokkinobaphos Master": "illuminator of the Homilies of James of Kokkinobaphos, Constantinople, 12th century",
               "Pantoleon": "lead painter of the Menologion of Basil II, c. 1000"},
        persons=["Kokkinobaphos Master", "Pantoleon"],
        add=[("Komnenian style", "Schools & phases", "12th-century court style, Kokkinobaphos Master", "Komnenian restoration"),
             ("Palaiologan Renaissance", "Schools & phases", "late classicism of 1261–1453 in books and icons", "Palaiologan Renaissance"),
             ("Purple codices", "Sub-types", "Gospels on purple-dyed parchment in gold and silver: Rossano, Sinope, Petropolitanus", "Purple parchment"),
             ("Aristocratic psalters", "Sub-types", "full-page miniature psalters of the Paris Psalter type", "Paris Psalter"),
             ("Marginal psalters", "Sub-types", "psalters with marginal illustrations: Chludov, Theodore, Bristol Psalters", "Chludov Psalter")],
        ms=dict(trad=list(BYZ_TRADS), section=byz, order=BYZ_ORDER),
        coll_ms=coll_trad(*BYZ_TRADS, f=lambda x: x["illuminated_class"] == "1"),
        cat=[PINAKES, DIGIVAT, GALLICA, wp("Byzantine illuminated manuscripts", "survey and list of principal manuscripts")],
    ),
    "A1-17": dict(
        axis="Works: the five screenfold codices of the group as gathered (sitelinks ≥ 1; misattributed European items excluded), by date; then collections.",
        to_alias=["Borgia group codices"],
        add=[("Tonalamatl", "Sub-types", "260-day divinatory almanacs, the core content of the group", "Tonalpohualli")],
        ms=dict(trad=[], filter=lambda x: x["label"] in BORGIA, section=lambda x: "Borgia Group codices"),
        coll_ms=dict(trad=[], cfilter=lambda x: x["label"] in BORGIA),
        cat=[wp("Borgia Group", "the five codices of the group with holdings"), DIGIVAT, ("http://www.famsi.org/research/loubat/", "FAMSI: Loubat facsimiles", "facsimiles of the Borgia, Vaticanus B, Cospi and other codices")],
    ),
    "A1-18": dict(
        axis="Works: every gathered Mixtec screenfold codex with sitelinks ≥ 1 (misattributed Vienna and Bodleian European items excluded), pre-Hispanic first then colonial; then collections.",
        to_alias=["Mixtec codices"],
        add=[("Eight Deer Jaguar Claw", "Sub-types", "Mixtec ruler (1063–1115) whose life is the main subject of the codices", "Eight Deer Jaguar Claw")],
        ms=dict(trad=[], filter=lambda x: x["label"] in MIXTEC,
                section=lambda x: "Colonial Mixtec codices" if x["label"] in ("Selden Roll", "Codex Selden") else "Pre-Hispanic Mixtec codices",
                order=["Pre-Hispanic Mixtec codices", "Colonial Mixtec codices"]),
        coll_ms=dict(trad=[], cfilter=lambda x: x["label"] in MIXTEC),
        cat=[wp("Mixtec codices", "list of the surviving codices"), BODLEIAN],
    ),
    "A1-19": dict(
        axis="Works: every gathered Aztec / Nahua codex with sitelinks ≥ 1, by type (ritual and calendrical, historical and tribute, colonial encyclopaedic); then collections.",
        to_alias=["Mesoamerican codices, colonial", "Aztec / Nahua codices (pre-conquest)"],
        add=[("Tlacuilo", "Sub-types", "the Nahua painter-scribe who made the codices", "Tlacuilo")],
        ms=dict(trad=[], filter=lambda x: aztec(x) is not None, section=aztec,
                order=["Ritual and calendrical codices", "Historical, migration and tribute codices", "Colonial encyclopaedic and missionary codices"]),
        coll_ms=dict(trad=["Mesoamerican codices, colonial", "Aztec / Nahua codices (pre-conquest)", "Mexican / New Spain manuscripts (unlocalised)"]),
        cat=[wp("Aztec codices", "list of surviving Aztec codices with holdings"), ("https://www.loc.gov/collections/", "Library of Congress Digital Collections", "includes the Codex Quetzalecatzin and other Mexican pictorial manuscripts"), GALLICA],
    ),
    "A1-20": dict(
        axis="Schools by region (early Armenian, Cilician, Gladzor, Tatev, Vaspurakan, Crimean, New Julfa); works: every gathered Armenian manuscript with sitelinks ≥ 2 (the ≥ 1 rule gives 1,170, mostly Matenadaran stubs), by school; then collections and illuminators.",
        to_alias=["Armenian (later or unlocalised)", "Armenian manuscript illumination"],
        regroup={n: "Schools & phases" for n in ["Armenian: Ani / early Armenian (to 1200)", "Armenian: Vaspurakan school", "Armenian: New Julfa / diaspora", "Armenian: Cilician school",
                                                 "Armenian: Glajor (Gladzor) school", "Armenian: Syunik / Tatev school", "Armenian: Crimean school", "Lesser Armenian school of miniature painting"]},
        rename={"Armenian: Ani / early Armenian (to 1200)": "Early Armenian school (to 1200)", "Armenian: Vaspurakan school": "Vaspurakan school",
                "Armenian: New Julfa / diaspora": "New Julfa school", "Armenian: Cilician school": "Cilician school", "Armenian: Glajor (Gladzor) school": "Gladzor school",
                "Armenian: Syunik / Tatev school": "Tatev school", "Armenian: Crimean school": "Crimean school", "Lesser Armenian school of miniature painting": "Lesser Armenian school"},
        gloss={"Armenian: Ani / early Armenian (to 1200)": "Etchmiadzin and Mugni Gospels, 10th–11th century", "Armenian: Vaspurakan school": "Lake Van monasteries, 13th–17th century",
               "Armenian: New Julfa / diaspora": "Isfahan suburb workshops, 17th century", "Armenian: Cilician school": "Hromkla and Sis, 12th–14th century, Toros Roslin",
               "Armenian: Glajor (Gladzor) school": "Gladzor university, Vayots Dzor, c. 1280–1340, Momik and T'oros of Taron",
               "Armenian: Syunik / Tatev school": "Tatev monastery, 14th–15th century, Grigor Tatevatsi", "Armenian: Crimean school": "Caffa and Surkhat, 14th–15th century",
               "Lesser Armenian school of miniature painting": "Lesser Armenia (Sebastia region) painting", "Toros Roslin": "Cilician master, Hromkla, fl. 1256–68",
               "Sargis Pitsak": "Cilician painter, fl. 1307–55", "Momik": "Gladzor painter, sculptor and architect, d. 1333", "Mesrop of Khizan": "Khizan (Vaspurakan) painter, fl. 1605–51",
               "Vardan Baghishetsi": "Vaspurakan painter, 17th century", "Naghash Hovnatan": "painter and poet (1661–1722), founder of the Hovnatanian dynasty"},
        persons=["Toros Roslin", "Sargis Pitsak", "Momik", "Mesrop of Khizan", "Vardan Baghishetsi", "Naghash Hovnatan"],
        add=[("Etchmiadzin Gospels", "Early Armenian manuscripts (to 1200)", "989, with 6th-century ivory covers; Matenadaran, Yerevan", "Echmiadzin Gospels"),
             ("T'oros Taronatsi", "Makers", "Gladzor painter, fl. 1307–46", "T'oros Taronatsi"),
             ("Grigor Tatevatsi", "Makers", "Tatev theologian and painter (1346–1409)", "Grigor Tatevatsi")],
        ms=dict(trad=list(ARM_TR), minsl=2, section=lambda x: ARM_TR.get(x["tradition"]), order=ARM_ORDER),
        coll_ms=coll_trad(*ARM_TR),
        cat=[MATENADARAN, VHMML, wp("Armenian illuminated manuscripts", "survey of schools and principal manuscripts")],
    ),
}
