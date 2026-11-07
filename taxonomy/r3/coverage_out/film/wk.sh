#!/bin/bash
# usage: wk.sh "Page_title"  -> saves wiki/<title>.txt, prints headings
t="$1"; f="wiki/${t//\//_}.txt"
[ -s "$f" ] || curl -s "https://en.wikipedia.org/w/index.php?title=${t// /_}&action=raw&redirect=yes" -o "$f"
grep -E "^=+" "$f"
