#!/usr/bin/env bash
# Modern-era pass (active 1860-1960), region by region (visual-art-plan.md §2.4).
# Pools first (the first region fetches the new birth decades; the rest reuse the
# cache), then holdings and pageviews for every pooled artist, then each region is
# scored with the model fitted on europe_1400-1900.
# Usage: bash pipelines/visual_art/run_modern.sh [WORKERS]   (Wikidata queries in parallel, default 1)
set -euo pipefail
cd "$(dirname "$0")/../.."
WORKERS="${1:-1}"
REGIONS="modern_europe modern_north_america modern_latin_america modern_east_asia modern_south_asia modern_southeast_asia modern_mena_central_asia modern_subsaharan_africa modern_oceania"
for r in $REGIONS; do
  python3 -u pipelines/visual_art/build_pool.py --region "$r" --workers "$WORKERS"
done
python3 -u pipelines/visual_art/museum_holdings.py
python3 -u pipelines/visual_art/pageviews.py
for r in $REGIONS; do
  python3 -u pipelines/visual_art/depth_model.py apply --region "$r" --model europe_1400-1900
done
