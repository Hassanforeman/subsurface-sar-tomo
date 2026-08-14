#!/usr/bin/env bash
# find_gran_sasso.sh — is there free X-band spotlight coverage over Gran Sasso / LNGS?
#
# WHY: HarmonicSAR published a tomographic "reconstruction" of Laboratori Nazionali del
# Gran Sasso (LNGS) at 1.4 km depth. LNGS is three excavated halls, each roughly
# 100 x 20 x 18 m, under ~1400 m of rock, with a layout published by INFN. That makes it
# the best ground-truth target for a deep-void claim that exists anywhere.
#
# This script finds out whether we can run our own pipeline over the same place.
#
# Needs: aws cli. No credentials required - these buckets are public.
#   sudo apt install awscli     (or)     brew install awscli
#
# Run:  bash find_gran_sasso.sh

set -u
OUT="gran_sasso_search"
mkdir -p "$OUT"

# LNGS underground labs sit near 42.4275 N, 13.5147 E.
# Box below covers the whole Gran Sasso massif with margin.
LAT_MIN=42.30; LAT_MAX=42.60
LON_MIN=13.30; LON_MAX=13.75

echo "==============================================================="
echo " STEP 1  Umbra - list every open-data task name"
echo "==============================================================="
aws s3 ls --no-sign-request "s3://umbra-open-data-catalog/sar-data/tasks/" \
  > "$OUT/umbra_tasks.txt" 2>&1
n=$(grep -c PRE "$OUT/umbra_tasks.txt" 2>/dev/null || echo 0)
echo "  $n tasks found -> $OUT/umbra_tasks.txt"
echo
echo "  Names containing anything Italian or mountain-related:"
grep -iE "italy|italia|gran ?sasso|aquila|abruzzo|apennin|teramo|assergi|campo imperatore|volcano|mountain|tunnel|mine" \
  "$OUT/umbra_tasks.txt" | sed 's/^/    /' || echo "    (none by name - this proves nothing, see step 2)"

echo
echo "==============================================================="
echo " STEP 2  Umbra - search by COORDINATES, not by name"
echo "==============================================================="
echo "  Task names are arbitrary, so this reads every scene's STAC metadata"
echo "  and keeps anything inside the Gran Sasso box."
echo "  This downloads only small JSON files, but there are a lot of them."
echo "  Expect 10-30 minutes. Leave it running."
echo

aws s3 ls --no-sign-request --recursive "s3://umbra-open-data-catalog/sar-data/tasks/" \
  | grep -iE "\.json$" | awk '{print $4}' > "$OUT/umbra_json_keys.txt" 2>/dev/null
echo "  $(wc -l < "$OUT/umbra_json_keys.txt") metadata files to check"

: > "$OUT/umbra_hits.txt"
i=0
while read -r key; do
  i=$((i+1))
  [ $((i % 250)) -eq 0 ] && echo "    ...$i checked, $(wc -l < "$OUT/umbra_hits.txt") hits so far"
  body=$(aws s3 cp --no-sign-request "s3://umbra-open-data-catalog/$key" - 2>/dev/null | head -c 200000)
  [ -z "$body" ] && continue
  python3 - "$key" "$LAT_MIN" "$LAT_MAX" "$LON_MIN" "$LON_MAX" <<'PYEOF' >> "$OUT/umbra_hits.txt" 2>/dev/null
import sys, json, re
key, la1, la2, lo1, lo2 = sys.argv[1], *map(float, sys.argv[2:6])
raw = sys.stdin.read()
try:
    d = json.loads(raw)
except Exception:
    sys.exit()
def coords(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("bbox",) and isinstance(v, list) and len(v) >= 4:
                yield (v[1], v[0]); yield (v[3], v[2])
            if k.lower() in ("lat", "latitude") and isinstance(v, (int, float)):
                yield (v, None)
            yield from coords(v)
    elif isinstance(o, list):
        for v in o:
            if (isinstance(v, list) and len(v) == 2
                    and all(isinstance(x, (int, float)) for x in v)):
                yield (v[1], v[0])
            yield from coords(v)
for la, lo in coords(d):
    if lo is None:
        continue
    if la1 <= la <= la2 and lo1 <= lo <= lo2:
        print(f"{key}\t{la:.4f}\t{lo:.4f}")
        break
PYEOF
done < "$OUT/umbra_json_keys.txt"

echo
echo "  UMBRA HITS: $(wc -l < "$OUT/umbra_hits.txt")"
sort -u "$OUT/umbra_hits.txt" | sed 's/^/    /'

echo
echo "==============================================================="
echo " STEP 3  Capella - same coordinate search"
echo "==============================================================="
aws s3 ls --no-sign-request "s3://capella-open-data/data/" > "$OUT/capella_top.txt" 2>&1
head -20 "$OUT/capella_top.txt" | sed 's/^/    /'
echo "    (full listing in $OUT/capella_top.txt)"

echo
echo "==============================================================="
echo " WHAT TO DO WITH THE RESULT"
echo "==============================================================="
cat <<'NOTE'
  If there are hits:
    Send me $OUT/umbra_hits.txt. We pre-register predictions FIRST, push them,
    and only then process. Same protocol as Giza.

  If there are none:
    That is itself worth saying publicly, and politely: the site cannot be
    independently checked with free data, so the reconstruction cannot be
    reproduced by anyone. Which raises the obvious question of which sensor
    and which scene HarmonicSAR used.

  Either way, ASK HIM for the scene ID. It costs him nothing to give and it is
  the single thing that makes the claim checkable.
NOTE
