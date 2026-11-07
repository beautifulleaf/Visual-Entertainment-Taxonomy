#!/bin/bash
# usage: fetch.sh page...  (cached, 1.1s apart)
D=/tmp/claude-0/-home-user-Visual-Entertainment-Taxonomy/7a24fa89-91fb-57af-a0cc-3429547c895c/scratchpad/raw
for p in "$@"; do
  f="$D/$(echo "$p" | tr '/?=&' '____')"
  [ -s "$f" ] && continue
  code=$(curl -sS -L -A "Mozilla/5.0 (research; VisualEntertainmentTaxonomy)" -o "$f" -w "%{http_code}" "https://theyshootpictures.com/$p")
  [ "$code" != 200 ] && { echo "FAIL $code $p"; echo "$p $code" >> "$D/../failed.txt"; rm -f "$f"; }
  sleep 1.1
done
