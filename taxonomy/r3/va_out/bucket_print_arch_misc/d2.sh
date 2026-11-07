python3 dump.py $1 | awk -F'\t' '$3=="1"' | cut -f1,3-6 | sort -t$'\t' -k4,4 -k3,3 | awk -F'\t' '{printf "%s|%s|%s|%s; ", $1,$3,substr($4,1,14),substr($5,1,30)} END{print ""}'
