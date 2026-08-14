#!/bin/bash
# fetch_giza.sh — download every Umbra open-data acquisition over the Giza plateau.
#
# Task: sar-data/tasks/ad hoc/Pyramids of Giza/   (CC-BY 4.0, no credentials)
# Three passes, two satellites, Feb–Mar 2023. SICD is what the pipeline reads;
# CPHD is the raw phase history, kept for a more faithful sub-aperture study later.
#
# Safe to re-run: every transfer resumes from what is already on disk (-C -) and
# retries through dropped connections. Run detached so it survives logout:
#
#   nohup ./fetch_giza.sh > /tmp/giza_dl.log 2>&1 &
#
# Progress:  tail -f /tmp/giza_dl.log
# Check:     ./fetch_giza.sh --verify

set -u
BASE="https://umbra-open-data-catalog.s3.amazonaws.com/sar-data/tasks/ad%20hoc/Pyramids%20of%20Giza"
DEST="$(cd "$(dirname "$0")" && pwd)/data"
mkdir -p "$DEST"

# collect-uuid | folder | filename | local name | expected bytes
FILES=(
"7e7cd796-3842-4923-8b48-4c0950ece945|2023-02-07-07-58-27_UMBRA-05|2023-02-07-07-58-27_UMBRA-05_SICD.nitf|giza_2023-02-07_UMBRA-05_SICD.nitf|243597312"
"44da7805-2129-4105-add8-2403bf671f40|2023-02-08-07-54-55_UMBRA-04|2023-02-08-07-54-55_UMBRA-04_SICD.nitf|giza_2023-02-08_UMBRA-04_SICD.nitf|253968384"
"5aa49658-ecf9-4504-afee-281f43fb076e|2023-03-08-07-57-53_UMBRA-04|2023-03-08-07-57-53_UMBRA-04_SICD.nitf|giza_2023-03-08_UMBRA-04_SICD.nitf|1704000000"
"7e7cd796-3842-4923-8b48-4c0950ece945|2023-02-07-07-58-27_UMBRA-05|2023-02-07-07-58-27_UMBRA-05_CPHD.cphd|giza_2023-02-07_UMBRA-05_CPHD.cphd|440000000"
"44da7805-2129-4105-add8-2403bf671f40|2023-02-08-07-54-55_UMBRA-04|2023-02-08-07-54-55_UMBRA-04_CPHD.cphd|giza_2023-02-08_UMBRA-04_CPHD.cphd|520000000"
)

if [ "${1:-}" = "--verify" ]; then
  printf '%-46s %10s\n' FILE SIZE
  for row in "${FILES[@]}"; do
    IFS='|' read -r _ _ _ local _ <<< "$row"
    if [ -f "$DEST/$local" ]; then
      printf '%-46s %10s\n' "$local" "$(du -h "$DEST/$local" | cut -f1)"
    else
      printf '%-46s %10s\n' "$local" "MISSING"
    fi
  done
  exit 0
fi

echo "=== Giza download started $(date) ==="
n=0
for row in "${FILES[@]}"; do
  IFS='|' read -r uuid folder remote local expected <<< "$row"
  n=$((n+1))
  echo
  echo "[$n/${#FILES[@]}] $local  (expect ~$((expected/1000000)) MB)"
  curl -sS -C - --retry 100 --retry-delay 10 --retry-all-errors --connect-timeout 30 \
       -o "$DEST/$local" "$BASE/$uuid/$folder/$remote"
  rc=$?
  if [ -f "$DEST/$local" ]; then
    got=$(wc -c < "$DEST/$local" | tr -d ' ')
    echo "    curl exit $rc, $((got/1000000)) MB on disk"
  else
    echo "    curl exit $rc, NO FILE"
  fi
done

echo
echo "=== finished $(date) ==="
"$0" --verify
