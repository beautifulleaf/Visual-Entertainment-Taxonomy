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

Evidence is per region: `occupations` (who counts as an artist there),
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

# Encyclopedic open-access collections, a baseline for every region. Regions add
# their specialist collections on top (the decisive ones differ by region and era).
GLOBAL_COLLECTIONS = ["met", "aic", "cma"]
# Authority IDs meaningful everywhere; kept as named model features.
GLOBAL_IDS = {"P245": "ulan", "P6002": "wikiart"}

REGIONS = {
    "europe_1400-1900": {
        "label": "Europe and its colonies, painters active 1400-1900",
        "active": (1400, 1900),
        "occupations": [PAINTER],
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
    #     "occupations": [PAINTER, "Q3303330", "Q11569986"],  # + calligrapher, printmaker
    #     "continents": [],
    #     "countries": [...],  # China and its dynasties, Japan, Korea, ...
    #     "min_sitelinks": 3,
    #     "reference": None,  # built during the pass
    #     "collections": GLOBAL_COLLECTIONS + ["colbase", "npm_taiwan", "nmaa"],
    #     "authority_ids": [...],  # e.g. Tokyo National Research Institute for Cultural Properties, NDL
    # },
}

# Width (years) of the period buckets inside a region. Features are converted to
# percentiles within each region x period cell, so a model fitted where Wikipedia
# coverage is dense transfers to cells where it is thin.
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
