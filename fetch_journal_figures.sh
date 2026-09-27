#!/bin/bash
# fetch_journal_figures.sh — download the JOURNAL version's figures 39-56 of Biondi & Malanga,
# Remote Sens. 2022, 14, 5231 (retracted 10 Aug 2026; CC-BY 4.0), from MDPI's public image server.
# Journal Figs 39-47, 49-52, 54-56 are the 16 "Tags association" pairs (= preprint Figs 34-40, 42-50);
# Fig 48 is the plain SLC image. Kept out of git under data/. Run from the repo root:
#   bash fetch_journal_figures.sh
set -e
OUT=data/biondi2022/journal
mkdir -p "$OUT"
BASE=https://pub.mdpi-res.com/remotesensing/remotesensing-14-05231/article_deploy/html/images
for n in $(seq 39 56); do
  f=remotesensing-14-05231-g0$n.png
  curl -sSL -A "Mozilla/5.0" -o "$OUT/$f" "$BASE/$f"
  echo "$f  $(file -b "$OUT/$f" | cut -c1-40)"
done
echo "done -> $OUT"
