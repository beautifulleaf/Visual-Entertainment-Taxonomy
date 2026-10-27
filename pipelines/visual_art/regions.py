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
itself is listed in `countries`. `reference` is optional: regions without one
are scored with a model fitted elsewhere, and their own reference lists get
added to seeds/visual-art/ as the per-region passes build them.
"""

EUROPE, NORTH_AMERICA, SOUTH_AMERICA = "Q46", "Q49", "Q18"
OCEANIA, INSULAR_OCEANIA, AUSTRALIA = "Q55643", "Q538", "Q3960"
ASIA, AFRICA = "Q48", "Q15"

PAINTER = "Q1028181"

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
    },
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
