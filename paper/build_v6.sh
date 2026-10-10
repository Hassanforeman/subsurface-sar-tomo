#!/usr/bin/env bash
# Build the v6.x preprint PDF from paper/PAPER_v6_DRAFT_2026-09-27.md (pandoc + xelatex, DejaVu fonts).
# Usage (from repo root): bash paper/build_v6.sh [out.pdf]   default -> paper/Giza_SAR_Doppler_Reproduction_v6.2.pdf
# Long repository paths get LaTeX break points (build-time only; the markdown source is unchanged).
set -euo pipefail
cd "$(dirname "$0")"
OUT=${1:-Giza_SAR_Doppler_Reproduction_v6.2.pdf}
TMP=$(mktemp -d)
python3 - "$TMP/paper.md" <<'PY'
import re, sys
s = open("PAPER_v6_DRAFT_2026-09-27.md", encoding="utf-8").read()
def brk(m):
    return re.sub(r'([_/\-.])', r'\1\\allowbreak{}', m.group(0))
# repository paths and long identifiers outside code spans / links
s = re.sub(r'(?<!\]\()(?<![`/\w])(?:runs|docs|src|paper)/[\w./*\-…]+', brk, s)
s = re.sub(r'(?<!\]\()(?<![`/\w{])[\w]*(?:UMBRA|CAPELLA)[\w.\-]*', brk, s)
s = re.sub(r'(?<![`/\w{])[A-Za-z][\w.]*_[\w.]{8,}', lambda m: m.group(0) if 'allowbreak' in m.group(0) else re.sub(r'([_.])', r'\1\\allowbreak{}', m.group(0)), s)
open(sys.argv[1], "w", encoding="utf-8").write(s)
PY
pandoc "$TMP/paper.md" -f markdown+raw_tex -o "$OUT" \
  --pdf-engine=xelatex --resource-path=.:..:../docs/figures \
  -V mainfont="DejaVu Serif" -V monofont="DejaVu Sans Mono" -V fontsize=10pt \
  -V geometry:margin=2.2cm -V colorlinks=true -V linkcolor=blue -V urlcolor=blue \
  -V header-includes='\usepackage{etoolbox}\AtBeginEnvironment{longtable}{\footnotesize}\AtBeginEnvironment{quote}{\small}\setlength{\emergencystretch}{3em}\usepackage{xurl}' \
  --shift-heading-level-by=-1
rm -rf "$TMP"
echo "-> $OUT"
