#!/bin/bash
# fetch_press_images.sh — download the 2026 "Second Sphinx" press-conference scan images published
# (with Biondi's permission) on archaeologicalrescue.org/secondsphinx/. Kept out of git under data/.
# Tries the original upload first (may retain EXIF), falls back to the 1024x767 resize.
# Per docs/PREREGISTRATION_PRESS_IMAGES_2026-09-27.md E.1.   Run from the repo root:
#   bash fetch_press_images.sh
OUT=data/secondsphinx_2026
mkdir -p "$OUT"
BASE=https://archaeologicalrescue.org/wp-content/uploads/2026/06
IDS="07 08 17 19 20 22 23 24 25 26 27 28 29 30 31 32 33 34 35 37 38 39 40 41 41-1 42 43 44 46 47 48 49 50 51 52 53 54 55 55-1 56 57 58 60 61 62 62-1 63 64 66 69 70 71 72 73 74 78-1 79 80"
for id in $IDS; do
  f="$OUT/$id.jpg"
  curl -sSfL -A "Mozilla/5.0" -o "$f" "$BASE/$id.jpg" 2>/dev/null \
    || curl -sSfL -A "Mozilla/5.0" -o "$f" "$BASE/$id-1024x767.jpg" 2>/dev/null \
    || { echo "$id  FAILED"; rm -f "$f"; continue; }
  echo "$id  $(file -b "$f" | cut -c1-60)"
done
echo "done -> $OUT ($(ls "$OUT" | wc -l | tr -d ' ') files)"
