"""Region x period definitions for the artist-depth model (visual-art-plan.md §2.1).

Each region is one pass of the pipeline:
  build_pool.py --region R   -> data/interim/visual_art/pool_R.csv
  pageviews.py               -> pageview totals for every pooled artist
  museum_holdings.py         -> Met / AIC / Cleveland holdings per artist
  depth_model.py fit   --region R   (needs a reference list)
  depth_model.py apply --region R   (uses a model fitted on another region)

A region is matched on an artist's countries of citizenship (P27), falling back
to the country of the place of birth (P19) and then of death (P20). A country is
in the region if its continent (P30) is listed in `continents` or the country
itself is listed in `countries`.

Evidence is per region: `media` (which occupation groups count as artists there),
`collections` (which museum holdings count) and `authority_ids` (which regional
databases count). The model only sees abstract features built from them
(museum_objects, n_museums, n_regional_ids, ...), each turned into a percentile
within its region x period cell, so one fitted model transfers across regions
while the sources behind each feature change. `reference` is optional: regions without one
are scored with a model fitted elsewhere, and their own reference lists get
added to seeds/visual-art/ as the per-region passes build them.
"""

EUROPE, NORTH_AMERICA, SOUTH_AMERICA = "Q46", "Q49", "Q18"
OCEANIA, INSULAR_OCEANIA, AUSTRALIA = "Q55643", "Q538", "Q3960"
ASIA, AFRICA = "Q48", "Q15"
EURASIA = "Q5401"  # recorded on some states instead of Europe + Asia

PAINTER = "Q1028181"

# Visual-art occupations grouped by medium (the third axis of the grid, beside
# region and period). Order matters: an artist's primary medium is the first
# group that matches any of their occupations; all matching media are kept too.
MEDIA = {
    "painting": [PAINTER],
    "sculpture": ["Q1281618", "Q1708232"],                     # sculptor, medalist
    "architecture": ["Q42973", "Q2815948"],                    # architect, landscape architect
    "photography": ["Q33231"],                                 # photographer
    "printmaking": ["Q11569986", "Q329439", "Q10862983", "Q16947657"],  # printmaker, engraver, etcher, lithographer
    "book arts": ["Q998628", "Q47494964", "Q3303330"],         # illuminator, miniaturist, calligrapher
    "design and decorative arts": [
        "Q5322166",   # designer
        "Q211423",    # goldsmith
        "Q2216340",   # silversmith
        "Q336221",    # jeweler
        "Q7541856",   # ceramicist
        "Q3400050",   # potter
        "Q2865798",   # glass artist
        "Q2205972",   # stained-glass artist
        "Q559597",    # cabinetmaker
        "Q11455387",  # furniture designer
        "Q10694573",  # textile artist
        "Q21117684",  # tapestry weaver
        "Q282718",    # mosaicist
        "Q56673616",  # decorative artist
        "Q2133309",   # interior designer
        "Q3501317",   # fashion designer
    ],
    "drawing and illustration": ["Q15296811", "Q644687", "Q3658608", "Q1925963"],  # draftsperson, illustrator, caricaturist, graphic artist
    "visual art (unspecified)": ["Q3391743"],                  # visual artist
}
ALL_MEDIA = list(MEDIA)

# Ancient vase painting is its own medium in the pre-1400 passes (not in ALL_MEDIA,
# so the 1400+ passes are unchanged). QIDs verified by label: vase painter,
# pottery painter, ceramic painter, Attic vase-painter, red-figure, black-figure and
# white-ground vase painters, plus the ancient Greek and Attic potter occupations
# (generic "potter" stays in design and decorative arts).
MEDIA["vase painting"] = [
    "Q15301511", "Q59938940", "Q56312678", "Q21282419", "Q15303045", "Q15303031", "Q41000669",
    "Q21505859", "Q31092701",
]
# Pre-1400 media, in primary-medium order: vase painting first (a painter-potter like
# Exekias is a vase painter), then sculpture before painting, so sculptors who also
# carry "painter" (Phidias, Giovanni Pisano, Kaikei) are ranked in sculpture cells.
PRE1400_MEDIA = ["vase painting", "sculpture", "painting"] + [m for m in ALL_MEDIA if m not in ("painting", "sculpture")]
# Occupations that only matter before 1400, added to a medium for the pre-1400 passes
# (regions' "extra_occupations"; existing MEDIA groups and their caches stay as they are).
PRE1400_EXTRA_OCCUPATIONS = {
    "painting": ["Q4199058", "Q22669155"],           # iconographer (icon painter), fresco painter
    "sculpture": ["Q2928765", "Q2926103", "Q3109381"],  # busshi (Buddhist sculptor), brazier (bronze caster), gem engraver
    "visual art (unspecified)": ["Q483501"],         # artist: many medieval masters carry only this
}


def media_occupations(cfg):
    """{medium: occupation QIDs} for a region: MEDIA plus the region's extra occupations."""
    extra = cfg.get("extra_occupations", {})
    return {m: MEDIA[m] + extra.get(m, []) for m in cfg["media"]}

# Encyclopedic open-access collections, a baseline for every region. Regions add
# their specialist collections on top (the decisive ones differ by region and era).
GLOBAL_COLLECTIONS = ["met", "aic", "cma"]
# Authority IDs meaningful everywhere; kept as named model features.
GLOBAL_IDS = {"P245": "ulan", "P6002": "wikiart"}

REGIONS = {
    "europe_1400-1900": {
        "label": "Europe and its colonies, visual artists active 1400-1900",
        "active": (1400, 1900),
        "media": ALL_MEDIA,
        # The reference list is painting movements, so the model is fitted on the
        # painting cells (plus reference artists from any medium) and applied to
        # every medium with within-cell percentiles.
        "train_media": ["painting"],
        # Architecture is organised by style, with buildings as exemplars and
        # architects attached through them; the model does not select architects.
        "model_excluded_media": ["architecture"],
        "continents": [EUROPE, NORTH_AMERICA, SOUTH_AMERICA, OCEANIA, INSULAR_OCEANIA, AUSTRALIA],
        # Colonial states outside those continents.
        "countries": [
            "Q188161",  # Dutch East Indies
            "Q129286",  # British Raj
        ],
        "min_sitelinks": 3,
        "reference": "seeds/visual-art/europe_1400-1900_depth_reference.txt",
        # Holdings sources (museum_holdings.py) summed into museum_objects / n_museums.
        "collections": GLOBAL_COLLECTIONS,
        # Regional authority and museum IDs on Wikidata, counted into n_regional_ids.
        "authority_ids": [
            "P650",   # RKDartists
            "P1367",  # Art UK artist
            "P2843",  # Benezit
            "P4432",  # AKL / Artists of the World
            "P781",   # SIKART
            "P7711",  # Joconde author
            "P5321",  # Museo del Prado
            "P2538",  # Nationalmuseum Sweden
            "P2268",  # Musee d'Orsay
            "P2741",  # Tate
            "P1816",  # National Portrait Gallery (London)
            "P4808",  # Royal Academy
            "P8705",  # Louvre Department of Prints and Drawings
            "P2252",  # National Gallery of Art
            "P1795",  # Smithsonian American Art Museum
            "P2174",  # MoMA
        ],
    },
    # Template for the next passes. Each region brings its own evidence: who counts
    # as an artist there, which collections are decisive, which authority files
    # cover it. Uncomment once its holdings sources exist in museum_holdings.py.
    # "east_asia_pre1900": {
    #     "label": "China, Japan, Korea: painters, calligraphers, print designers, before 1900",
    #     "active": (600, 1900),
    #     "media": ALL_MEDIA,  # plus region-specific occupations (ink painter, ukiyo-e artist, ...) added to MEDIA
    #     "train_media": ["painting"],
    #     "continents": [],
    #     "countries": [...],  # China and its dynasties, Japan, Korea, ...
    #     "min_sitelinks": 3,
    #     "reference": None,  # built during the pass
    #     "collections": GLOBAL_COLLECTIONS + ["colbase", "npm_taiwan", "nmaa"],
    #     "authority_ids": [...],  # e.g. Tokyo National Research Institute for Cultural Properties, NDL
    # },
}

# A multi-continent country's home continent is the first of these it lists
# (used by regions with "home_continent": True).
HOME_CONTINENT_ORDER = [EUROPE, NORTH_AMERICA, SOUTH_AMERICA, AFRICA, OCEANIA, INSULAR_OCEANIA, AUSTRALIA, ASIA]

# Country groups for regions that cut across continents (QIDs verified by label).
LATIN_AMERICA_NORTH = [
    "Q96", "Q774", "Q242", "Q783", "Q792", "Q811", "Q800", "Q804",  # Mexico, Central America
    "Q241", "Q786", "Q790", "Q1183", "Q766",                        # Caribbean
]
EAST_ASIA = ["Q148", "Q17", "Q884", "Q423", "Q865", "Q711", "Q8646", "Q18097", "Q188712", "Q8733", "Q13426199"]
SOUTH_ASIA = ["Q668", "Q843", "Q902", "Q854", "Q837", "Q129286", "Q889"]
SOUTHEAST_ASIA = ["Q252", "Q928", "Q869", "Q881", "Q833", "Q334", "Q836", "Q424", "Q188161"]
NORTH_AFRICA = ["Q79", "Q1016", "Q948", "Q262", "Q1028",
                "Q124943", "Q3087763", "Q170468"]  # + Kingdom of Egypt, Republic of Egypt, United Arab Republic
WEST_CENTRAL_ASIA = [
    "Q43", "Q794", "Q796", "Q822", "Q858", "Q851", "Q12560", "Q801", "Q810", "Q817", "Q842",
    "Q846", "Q878", "Q398", "Q805", "Q219060",                       # Middle East
    "Q265", "Q874", "Q813", "Q863",                                  # Central Asia
]

# Modern era (Impressionism to ~1960; contemporary starts in the 1960s), split by
# world region so that each modernism is ranked against its own peers, not
# against Paris and New York. Calibrated on its own reference (decided 2026-10-28;
# the Europe 1400-1900 model was only an example of the depth wanted): one model
# fitted on all nine regions, models/modern_1860-1960.json (fit_modern.py).
MODERN_REGIONS = {
    "europe": {"continents": [EUROPE], "exclude_countries": WEST_CENTRAL_ASIA},
    "north_america": {"continents": [NORTH_AMERICA], "exclude_countries": LATIN_AMERICA_NORTH},
    "latin_america": {"continents": [SOUTH_AMERICA], "countries": LATIN_AMERICA_NORTH},
    "east_asia": {"countries": EAST_ASIA},
    "south_asia": {"countries": SOUTH_ASIA},
    "southeast_asia": {"countries": SOUTHEAST_ASIA},
    "mena_central_asia": {"countries": NORTH_AFRICA + WEST_CENTRAL_ASIA},
    "subsaharan_africa": {"continents": [AFRICA], "exclude_countries": NORTH_AFRICA},
    "oceania": {"continents": [OCEANIA, INSULAR_OCEANIA, AUSTRALIA]},
}
for _name, _geo in MODERN_REGIONS.items():
    REGIONS[f"modern_{_name}"] = {
        "label": f"Modern art (active 1860-1960), {_name.replace('_', ' ')}",
        "active": (1860, 1960),
        "media": ALL_MEDIA,
        "train_media": ["painting"],
        "model_excluded_media": ["architecture"],
        "continents": _geo.get("continents", []),
        "countries": _geo.get("countries", []),
        "exclude_countries": _geo.get("exclude_countries", []),
        "home_continent": True,
        "place_by_birth_death": True,
        "min_sitelinks": 3,
        # Modern reference built from data (build_modern_reference.py: movements from
        # Wikidata, ranked by Tate / MoMA / collection holdings, none of them model
        # features). Its artists below the pool rule still join the pool as positives.
        "reference": "seeds/visual-art/modern_1860-1960_depth_reference.txt",
        "reference_qids": "data/interim/modern_reference_candidate.csv",
        "reference_region": _name,
        # Artists always selected although under the cutoff or unplaceable (no country
        # on Wikidata); rows for modern_<region>, read by build_pool.py.
        "manual_includes": "seeds/visual-art/modern_manual_includes.csv",
        # Decided 2026-10-28 (Europe only): at the 80%-recall cutoff, a non-reference
        # artist held by none of the collections and under 100 monthly page views is
        # dropped (depth_model.select); Europe's dense Wikipedia long tail fills the
        # margin otherwise. Other regions: no guard.
        **({"selection_guard": {"min_museums": 1, "max_pageviews": 100}} if _name == "europe" else {}),
        "collections": GLOBAL_COLLECTIONS,
        "authority_ids": REGIONS["europe_1400-1900"]["authority_ids"],
    }

# Pre-1400 passes. The 1400+ passes start at 1400, so named makers before then
# (Giotto, Exekias, Phidias, Gu Kaizhi, Unkei, Ibn al-Bawwab) were in no pool. Each
# region is scored with the model fitted on europe_1400-1900 (`depth_model.py apply`).
# Citizenships are historical states (Tang dynasty, Delian League, Cilicia) and
# birth places resolve to modern countries, so "place_any" lets any of citizenship,
# birth or death country place an artist; the state lists below were curated from
# the citizenships found in the pre-1400 candidate pool (QIDs verified by label).
PRE1400_COMMON = {
    "media": PRE1400_MEDIA,
    "extra_occupations": PRE1400_EXTRA_OCCUPATIONS,
    "train_media": ["painting"],
    "model_excluded_media": ["architecture"],
    "home_continent": True,
    "place_any": True,
    "min_sitelinks": 3,
    "reference": None,
    "fetch_bucket": 50,   # one query per 50-year bucket for all occupations, BCE dates, floruit/work period
    "collections": GLOBAL_COLLECTIONS,
    "authority_ids": REGIONS["europe_1400-1900"]["authority_ids"],
}
ANTIQUE_MEDITERRANEAN_STATES = [
    "Q11772", "Q844930", "Q193235", "Q5690", "Q368628", "Q83958", "Q184313",  # Ancient Greece, Classical Athens, Delian League, Sparta, Sicyon, Macedonia, Magna Graecia
    "Q1747689", "Q2277", "Q1072140", "Q42834",                               # Ancient Rome, Roman Empire, Roman Republic, Western Roman Empire
    "Q2320005", "Q93180", "Q2022162",                                        # Ptolemaic Kingdom, Seleucid Empire, Kingdom of Pergamon
    "Q79", "Q11768", "Q43", "Q229", "Q858", "Q822", "Q801", "Q1016", "Q948",  # Egypt, Ancient Egypt, Turkey, Cyprus, Syria, Lebanon, Israel, Libya, Tunisia
]
MEDIEVAL_EUROPE_EXTRA = [
    "Q12544", "Q178913", "Q43", "Q229", "Q213638",                # Byzantine Empire, Empire of Trebizond, Turkey, Cyprus, Kingdom of Cyprus
    "Q399", "Q208404", "Q2622868", "Q335088",                     # Armenia, Kingdom of Armenia, Bagratid Armenia, Armenian Kingdom of Cilicia
    "Q230", "Q154667", "Q154816",                                 # Georgia, Kingdom of Georgia, Kingdom of the Iberians
    "Q55502",                                                     # Kingdom of Jerusalem
]
CHINA_JAPAN_KOREA_STATES = [
    "Q29520", "Q7209", "Q1147037", "Q1069829", "Q320930", "Q274488", "Q7352", "Q5066", "Q1145470", "Q306928",
    # China, Han, Eastern Han, Later Han, Cao Wei, Eastern Wu, Jin (x2), Western Jin, Eastern Jin
    "Q49697", "Q62456", "Q1069868", "Q62454", "Q875305", "Q1143164", "Q551067", "Q1143524", "Q7405", "Q9683",
    # Liu Song, Southern Qi, Liang, Chen, Northern Wei, Western Wei, Northern Zhou, Northern Qi, Sui, Tang
    "Q783489", "Q1143126", "Q1154540", "Q1154556", "Q1323195", "Q1326742", "Q11180184",
    # Later Liang, Later Tang, Later Jin, Later Zhou, Yang Wu, Southern Tang, Qi (Huang Chao)
    "Q1188046", "Q1149230", "Q1471995", "Q2314907", "Q1574107", "Q1730130", "Q4505481", "Q546282", "Q736936",
    # Yan, Western Yan, Former Qin, Later Zhao, Han Zhao, Later Qin, Liu Qi, Xia, Lu
    "Q7462", "Q319460", "Q1147043", "Q4958", "Q7427", "Q26472", "Q7313", "Q9903",
    # Song, Northern Song, Southern Song, Liao, Western Xia, Dali, Yuan, Ming
    "Q28370", "Q28428", "Q28456", "Q715257", "Q28084", "Q28322", "Q28208", "Q28179",
    # Goguryeo, Baekje, Silla, Later Silla, Gaya, Balhae, Goryeo, Joseon
    "Q736839",  # Kamakura shogunate
]
ISLAMIC_STATES = [
    "Q12490507", "Q8575586", "Q12536", "Q160307", "Q180114", "Q63135869", "Q282428", "Q847420", "Q11696332",
    # Rashidun, Umayyad, Abbasid, Fatimid, Ayyubid (x2), Mamluk (x2), Medieval Egypt
    "Q123559", "Q1337854", "Q171740", "Q75613", "Q199688", "Q238445",
    # al-Andalus, Emirate and Caliphate of Cordoba, Almoravid, Almohad, Emirate of Granada
    "Q12150341", "Q273874", "Q249578", "Q3708094", "Q975405", "Q63134381", "Q178084", "Q866716", "Q484195",
    # Samanid, Buyid, Ghaznavid, Seljuk, Sultanate of Rum, Khwarazmian, Ilkhanate, Jalayirid, Timurid
    "Q6563843", "Q709175", "Q428400", "Q189545", "Q1133431", "Q837187", "Q828665", "Q555994", "Q229411",
    # Nizari state, Tabaristan, Eldiguzids, Zengid, Artuqids, Hamdanid, Ikhshidid, Aq Qoyunlu, Delhi Sultanate
]
REGIONS["antiquity_mediterranean"] = {
    **PRE1400_COMMON,
    "label": "Greek, Etruscan, Hellenistic and Roman named makers, active 800 BCE-500 CE",
    "active": (-800, 500),
    "continents": [EUROPE],
    "countries": ANTIQUE_MEDITERRANEAN_STATES,
    # Many vase painters carry no citizenship or birth place, only a culture or a
    # language; build_pool falls back to work location, then to these.
    "fallback_cultures": [
        "Q11772", "Q17161", "Q184313",   # cultures: Ancient Greece, Etruscans, Magna Graecia
        "Q35497", "Q35726", "Q397",      # languages: Ancient Greek, Etruscan, Latin
    ],
}
REGIONS["europe_medieval_500-1400"] = {
    **PRE1400_COMMON,
    "label": "Medieval Europe, Byzantium, Armenia and Georgia, active 500-1400",
    "active": (500, 1400),
    "continents": [EUROPE],
    "countries": MEDIEVAL_EUROPE_EXTRA,
}
REGIONS["east_asia_pre1400"] = {
    **PRE1400_COMMON,
    # Starts at 200 BCE rather than 300 CE so that Han and Three Kingdoms calligraphers
    # and painters (Cai Yong, Zhang Zhi, Cao Buxing) are in some pass.
    "label": "China, Japan and Korea, active 200 BCE-1400",
    "active": (-200, 1400),
    "continents": [],
    "countries": EAST_ASIA + CHINA_JAPAN_KOREA_STATES,
    # The East Asia sweep (data/interim/regional/east_asia_artists.csv: ColBase, NPM,
    # e-Museum, designated properties) is matched to QIDs in museum_holdings.py.
    "collections": GLOBAL_COLLECTIONS + ["eastasia"],
}
REGIONS["islamic_pre1400"] = {
    **PRE1400_COMMON,
    "label": "Islamic world (calligraphers, illuminators, painters), active 600-1400",
    "active": (600, 1400),
    "continents": [],
    # Turkey is left out of the modern countries so that Byzantine artists born in
    # Constantinople stay out; Anatolian Seljuk artists come in through their states.
    "countries": [c for c in NORTH_AFRICA + WEST_CENTRAL_ASIA if c != "Q43"] + ISLAMIC_STATES,
}

# Width (years) of the period buckets inside a region. Features are converted to
# percentiles within each region x period x medium cell, so a model fitted where
# Wikipedia coverage is dense transfers to cells (and media) where it is thin.
PERIOD_BUCKET = 50


def active_span(birth, death, floruit=None, work_start=None, work_end=None):
    """Approximate working years: from age 20 to death (or age 70 if no death date).

    Without a birth date: 40 years up to death; else the work period (P2031/P2032);
    else 10 years either side of floruit (P1317)."""
    if birth is not None:
        start = birth + 20
        end = death if death is not None else birth + 70
    elif death is not None:
        start, end = death - 40, death
    elif work_start is not None or work_end is not None:
        start = work_start if work_start is not None else work_end - 20
        end = work_end if work_end is not None else work_start + 20
    elif floruit is not None:
        start, end = floruit - 10, floruit + 10
    else:
        return None
    return start, max(start, end)


def period_of(span):
    """Period bucket keyed on the midpoint of the active span, e.g. 1600 for 1600-1649."""
    mid = (span[0] + span[1]) // 2
    return mid - mid % PERIOD_BUCKET
