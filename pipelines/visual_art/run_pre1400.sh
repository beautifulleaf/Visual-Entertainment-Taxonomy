#!/usr/bin/env bash
# Pre-1400 named-maker passes (antiquity, medieval Europe/Byzantium/Armenia, East
# Asia, Islamic world), scored with the model fitted on europe_1400-1900, at its
# 90%-recall cutoff (visual-art-plan.md §2.3). Pools first (one query per 50-year
# bucket for all occupations, BCE dates, floruit and work-period dating; later
# regions reuse the cache), then holdings (Met/AIC/Cleveland plus the cached East
# Asia sweep) and pageviews (reuses the cached monthly dump), then scoring.
# Usage: bash pipelines/visual_art/run_pre1400.sh [WORKERS]   (Wikidata queries in parallel, default 1)
set -euo pipefail
cd "$(dirname "$0")/../.."
WORKERS="${1:-1}"
REGIONS="antiquity_mediterranean europe_medieval_500-1400 east_asia_pre1400 islamic_pre1400"
for r in $REGIONS; do
  python3 -u pipelines/visual_art/build_pool.py --region "$r" --workers "$WORKERS"
done
python3 -u pipelines/visual_art/museum_holdings.py
python3 -u pipelines/visual_art/pageviews.py
for r in $REGIONS; do
  python3 -u pipelines/visual_art/depth_model.py apply --region "$r" --model europe_1400-1900
done
