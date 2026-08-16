#!/usr/bin/env bash
# find_gran_sasso.sh  (v2 — v1 was broken; see BUG below)
#
# Searches the Umbra open-data catalogue by COORDINATE for scenes over the Gran
# Sasso massif (Laboratori Nazionali del Gran Sasso, INFN).
#
# BUG IN v1, FIXED HERE
# ---------------------
# v1 parsed `aws s3 ls --recursive` output with `awk '{print $4}'`, which stops at
# the first space. Most Umbra task names contain spaces ("ad hoc/Pyramids of
# Giza/"), so nearly every key was truncated to "sar-data/tasks/ad" and every
# subsequent download failed silently into /dev/null. The run reported 0 hits
# because it was reading nothing, not because there was nothing there.
#
# v1 was also pathologically slow: one `aws s3 cp` per file, 8,375 times,
# sequentially. v2 pulls every JSON in one parallel `aws s3 sync` and searches
# locally. Minutes instead of hours.
#
# Run:  bash find_gran_sasso.sh
set -u
OUT="$HOME/gran_sasso_search"; mkdir -p "$OUT/json"
BUCKET="umbra-open-data-catalog"

# LNGS underground halls sit near 42.4275 N, 13.5147 E.
LAT_MIN=42.30; LAT_MAX=42.60; LON_MIN=13.30; LON_MAX=13.75

echo "== STEP 1: full key listing (space-safe) =="
aws s3api list-objects-v2 --no-sign-request --bucket "$BUCKET" \
    --prefix "sar-data/tasks/" --output text --query 'Contents[].Key' \
  | tr '\t' '\n' | sed '/^$/d' > "$OUT/all_keys.txt"
echo "   $(wc -l < "$OUT/all_keys.txt") objects"
echo "   $(grep -ci '\.json$' "$OUT/all_keys.txt") JSON metadata files"
echo
echo "   sub-tasks under 'ad hoc' (where the Giza scene was filed):"
grep -i 'ad hoc/' "$OUT/all_keys.txt" | sed 's|.*ad hoc/||' | cut -d/ -f1 \
  | sort -u | sed 's/^/      /'

echo
echo "== STEP 2: bulk-download every JSON in parallel (minutes, not hours) =="
aws s3 sync --no-sign-request --only-show-errors \
    "s3://$BUCKET/sar-data/tasks/" "$OUT/json" \
    --exclude "*" --include "*.json"
echo "   $(find "$OUT/json" -name '*.json' | wc -l) files on disk"

echo
echo "== STEP 3: coordinate search =="
python3 - "$OUT" "$LAT_MIN" "$LAT_MAX" "$LON_MIN" "$LON_MAX" <<'PYEOF'
import sys, os, json
root, la1, la2, lo1, lo2 = sys.argv[1], *map(float, sys.argv[2:6])
def coords(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "bbox" and isinstance(v, list) and len(v) >= 4:
                yield (v[1], v[0]); yield (v[3], v[2])
            yield from coords(v)
    elif isinstance(o, list):
        for v in o:
            if (isinstance(v, list) and len(v) == 2
                    and all(isinstance(x, (int, float)) for x in v)):
                yield (v[1], v[0])
            yield from coords(v)
hits, n = [], 0
for dirpath, _, files in os.walk(os.path.join(root, "json")):
    for f in files:
        if not f.endswith(".json"): continue
        n += 1
        p = os.path.join(dirpath, f)
        try:
            d = json.load(open(p))
        except Exception:
            continue
        for la, lo in coords(d):
            if la1 <= la <= la2 and lo1 <= lo <= lo2:
                hits.append(f"{os.path.relpath(p, root)}\t{la:.4f}\t{lo:.4f}")
                break
open(os.path.join(root, "HITS.txt"), "w").write("\n".join(hits) + ("\n" if hits else ""))
print(f"   searched {n} files")
print(f"   {len(hits)} scenes inside the Gran Sasso box")
for h in hits[:40]: print("      " + h)
PYEOF

echo
echo "Result saved to $OUT/HITS.txt"
echo "If it is empty, no free Umbra scene covers Gran Sasso — which is itself the"
echo "finding: the published LNGS reconstruction cannot be independently checked."
