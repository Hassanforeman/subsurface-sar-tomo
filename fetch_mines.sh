#!/usr/bin/env bash
# fetch_mines.sh — download the four Umbra open-data mine sites not yet in the paper.
#
# Predictions for these scenes are pre-registered in
#   docs/PREREGISTRATION_MINES_AND_GRANSASSO.md  (Part A)
# and were committed BEFORE any of this data was downloaded. Do not process
# anything until that file is pushed.
#
# Silver Peak is the negative control: a lithium BRINE operation, evaporation
# ponds, no underground void. Diavik is the positive-truth case: documented
# underground workings. If the method worked, those two should not look alike.
#
# Run:  bash fetch_mines.sh
set -u
DEST="data"; mkdir -p "$DEST"
BUCKET="s3://umbra-open-data-catalog/sar-data/tasks"

TASKS=(
  "Diavik Diamond Mine, Canada"
  "Kalgoorlie Super Pit, Australia"
  "Greenbushes Mine, Australia"
  "Silver Peak Mine, Nevada, United States"
  "Thacker Pass Lithium Mine, Nevada, United States"
)

for t in "${TASKS[@]}"; do
  echo
  echo "=============================================================="
  echo " $t"
  echo "=============================================================="
  aws s3 ls --no-sign-request "$BUCKET/$t/" 2>&1 | sed 's/^/    /'
done

echo
echo "=============================================================="
echo " Downloading the first SICD from each task"
echo "=============================================================="
for t in "${TASKS[@]}"; do
  key=$(aws s3 ls --no-sign-request --recursive "$BUCKET/$t/" 2>/dev/null \
        | grep -i "SICD.nitf$" | head -1 | awk '{$1="";$2="";$3="";print substr($0,4)}')
  if [ -z "$key" ]; then echo "  no SICD found for: $t"; continue; fi
  short=$(echo "$t" | tr ' ,' '__' | cut -c1-24)
  out="$DEST/${short}_SICD.nitf"
  if [ -f "$out" ]; then echo "  already have $out"; continue; fi
  echo "  $t"
  echo "    -> $out"
  aws s3 cp --no-sign-request "s3://umbra-open-data-catalog/$key" "$out"
done

echo
echo "Downloaded:"; ls -lh "$DEST"/*.nitf 2>/dev/null | awk '{print "  ",$5,$9}'
echo
echo "NEXT — only after the pre-registration is pushed:"
echo "  for f in $DEST/*_SICD.nitf; do"
echo "    python3 src/followup_experiments.py --sicd \"\$f\" --experiment nsub"
echo "  done"
