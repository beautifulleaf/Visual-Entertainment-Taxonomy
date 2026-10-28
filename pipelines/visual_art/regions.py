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
NORTH_AFRICA = ["Q79", "Q1016", "Q948", "Q262", "Q1028"]
WEST_CENTRAL_ASIA = [
    "Q43", "Q794", "Q796", "Q822", "Q858", "Q851", "Q12560", "Q801", "Q810", "Q817", "Q842",
    "Q846", "Q878", "Q398", "Q805", "Q219060",                       # Middle East
    "Q265", "Q874", "Q813", "Q863",                                  # Central Asia
]

# Modern era (Impressionism to ~1960; contemporary starts in the 1960s), split by
# world region so that each modernism is ranked against its own peers, not
# against Paris and New York. No reference lists yet: each region is scored with
# the model fitted on europe_1400-1900 (`depth_model.py apply`).
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
        "min_sitelinks": 3,
        "reference": None,
        "collections": GLOBAL_COLLECTIONS,
        "authority_ids": REGIONS["europe_1400-1900"]["authority_ids"],
    }

# Width (years) of the period buckets inside a region. Features are converted to
# percentiles within each region x period x medium cell, so a model fitted where
# Wikipedia coverage is dense transfers to cells (and media) where it is thin.
PERIOD_BUCKET = 50


def active_span(birth, death, floruit=None):
    """Approximate working years: from age 20 to death (or age 70 if no death date)."""
    if birth is not None:
        start = birth + 20
        end = death if death is not None else birth + 70
    elif death is not None:
        start, end = death - 40, death
    elif floruit is not None:
        start, end = floruit - 10, floruit + 10
    else:
        return None
    return start, max(start, end)


def period_of(span):
    """Period bucket keyed on the midpoint of the active span, e.g. 1600 for 1600-1649."""
    mid = (span[0] + span[1]) // 2
    return mid - mid % PERIOD_BUCKET
