#!/bin/bash
# check_downloads.sh — status of the Bingham stacking SICD downloads.
# Run:  bash ~/Desktop/subsurface-sar-tomo/check_downloads.sh
cd ~/Desktop/subsurface-sar-tomo/data 2>/dev/null || { echo "data/ folder not found"; exit 1; }

PASSES=(
  2024-01-12-04-09-18_UMBRA-05   # already had this one
  2024-01-11-04-14-45_UMBRA-05
  2024-02-26-04-16-52_UMBRA-05
  2024-03-11-04-16-18_UMBRA-05
  2024-05-08-04-09-56_UMBRA-05
)

echo "Bingham stack downloads (each is ~800 MB when complete):"
done_count=0
for p in "${PASSES[@]}"; do
  f="${p}_SICD.nitf"
  if [ -f "$f" ]; then
    s1=$(wc -c < "$f" | tr -d ' ')
    sleep 5
    s2=$(wc -c < "$f" | tr -d ' ')
    mb=$(awk "BEGIN{printf \"%.0f\", $s2/1048576}")
    if [ "$s2" -gt "$s1" ]; then
      st="DOWNLOADING (growing)"
    elif [ "$s2" -ge 734003200 ]; then
      st="COMPLETE"; done_count=$((done_count+1))
    else
      st="partial/stalled? (re-run the fetch for this one)"
    fi
    printf "  %-32s %6s MB   %s\n" "$p" "$mb" "$st"
  else
    temp=$(ls "${f}".* 2>/dev/null | head -1)
    if [ -n "$temp" ]; then
      s1=$(wc -c < "$temp" | tr -d ' '); sleep 2; s2=$(wc -c < "$temp" | tr -d ' ')
      mb=$(awk "BEGIN{printf \"%.0f\", $s2/1048576}")
      if [ "$s2" -gt "$s1" ]; then st="DOWNLOADING (growing)"; else st="temp file stalled? re-run fetch"; fi
      printf "  %-32s %6s MB   %s\n" "$p" "$mb" "$st"
    else
      printf "  %-32s %6s      %s\n" "$p" "-" "MISSING (not started)"
    fi
  fi
done

echo "-------------------------------------------"
echo "$done_count of 5 complete."
if [ "$done_count" -eq 5 ]; then
  echo "All set — you can run the stack:"
  echo '  python3.13 src/stack.py --sicds \'
  echo '    data/2024-01-12-04-09-18_UMBRA-05_SICD.nitf \'
  echo '    data/2024-01-11-04-14-45_UMBRA-05_SICD.nitf \'
  echo '    data/2024-02-26-04-16-52_UMBRA-05_SICD.nitf \'
  echo '    data/2024-03-11-04-16-18_UMBRA-05_SICD.nitf \'
  echo '    data/2024-05-08-04-09-56_UMBRA-05_SICD.nitf --n-sub 128'
fi
