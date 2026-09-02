# CLAUDE.md — read this first

This repository is an independent reproduction-and-refutation of Biondi & Malanga's SAR Doppler
"micro-motion tomography" (the disputed Giza "underground city" method).

## Before doing anything

1. Read **`docs/STATE.md`** — the single source of truth for current status, plus the
   "settled — do not re-derive" and "actually open" ledgers. It exists specifically to stop
   sessions repeating finished work. Do not start new analysis until you've checked it.
2. Follow **`docs/DOCUMENTATION_RULES.md`** — how we record results and supersede old ones.
   In short: STATE.md is read first and updated last; never silently supersede (banner the old
   doc + move the ledger item); every number points to a script + a `runs/` JSON.
3. Technical reference is **`docs/TECHNICAL_BIBLE.md`** (keep it updated when durable facts change).

## Environment notes

- The Cowork sandbox mounts this repo but starts without `sarpy`/`scipy` → `pip install sarpy scipy`.
- The sandbox and cloud container are blocked from the Umbra/Capella S3 buckets — new scenes are
  fetched on Hassan's Mac, then the mounted pipeline runs on them.
- Hand Hassan one terminal command at a time. Honesty over hype; be the honest counterweight, not a cheerleader.
