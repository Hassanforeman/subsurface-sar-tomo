#!/usr/bin/env python3
"""
fetch_umbra.py — list and download free Umbra open-data SAR scenes.

Public bucket: s3://umbra-open-data-catalog  (CC-BY 4.0, no credentials).
Runs on your Mac. Install deps first:  pip install boto3

Examples
--------
# List the captures (collects) available for a task/location:
python src/fetch_umbra.py --task "Bingham Copper Mine"

# Download specific products for one collect into ./data/:
python src/fetch_umbra.py --task "Bingham Copper Mine" \
    --collect 2024-01-12-04-09-18_UMBRA-05 --products CPHD SICD METADATA

# List all top-level task folders (locations + thematic collections):
python src/fetch_umbra.py --list-tasks
"""
import argparse, os, sys

BUCKET = "umbra-open-data-catalog"
ROOT = "sar-data/tasks/"

def _client():
    import boto3
    from botocore import UNSIGNED
    from botocore.config import Config
    return boto3.client("s3", region_name="us-west-2",
                        config=Config(signature_version=UNSIGNED))

def _list_prefixes(s3, prefix):
    out, token = [], None
    while True:
        kw = dict(Bucket=BUCKET, Prefix=prefix, Delimiter="/")
        if token: kw["ContinuationToken"] = token
        r = s3.list_objects_v2(**kw)
        out += [p["Prefix"] for p in r.get("CommonPrefixes", [])]
        if not r.get("IsTruncated"): break
        token = r["NextContinuationToken"]
    return out

def _list_keys(s3, prefix):
    out, token = [], None
    while True:
        kw = dict(Bucket=BUCKET, Prefix=prefix)
        if token: kw["ContinuationToken"] = token
        r = s3.list_objects_v2(**kw)
        out += [(o["Key"], o["Size"]) for o in r.get("Contents", [])]
        if not r.get("IsTruncated"): break
        token = r["NextContinuationToken"]
    return out

def main():
    ap = argparse.ArgumentParser(description="Fetch free Umbra open-data scenes.")
    ap.add_argument("--list-tasks", action="store_true", help="list all task folders")
    ap.add_argument("--task", help='task/location name, e.g. "Bingham Copper Mine"')
    ap.add_argument("--collect", help="specific collect folder; omit to list collects")
    ap.add_argument("--products", nargs="*", default=["CPHD", "SICD", "METADATA"],
                    help="substrings to match in filenames (e.g. CPHD SICD GEC METADATA)")
    ap.add_argument("--out", default="data", help="output dir (default ./data)")
    args = ap.parse_args()

    try:
        s3 = _client()
    except Exception as e:
        sys.exit("Need boto3:  pip install boto3   (%s)" % e)

    if args.list_tasks:
        for p in _list_prefixes(s3, ROOT):
            print(p.replace(ROOT, "").rstrip("/"))
        return

    if not args.task:
        sys.exit("Provide --task NAME (or --list-tasks).")

    base = f"{ROOT}{args.task}/"
    if not args.collect:
        # list collects (task -> capture uuid -> collect folder); show collect-level dirs
        print(f"Collects under '{args.task}':")
        seen = set()
        for key, _ in _list_keys(s3, base):
            parts = key[len(base):].split("/")
            if len(parts) >= 2:
                label = parts[1]            # the dated collect folder
                if label and label not in seen:
                    seen.add(label); print("  ", label)
        if not seen:
            print("  (none — check the exact task name with --list-tasks)")
        return

    # download matching products for the named collect
    os.makedirs(args.out, exist_ok=True)
    matches = [(k, sz) for k, sz in _list_keys(s3, base)
               if args.collect in k and any(p.upper() in k.upper() for p in args.products)]
    if not matches:
        sys.exit("No files matched. Try without --products to see everything, or re-check --collect.")
    for key, size in matches:
        dest = os.path.join(args.out, os.path.basename(key))
        print(f"↓ {os.path.basename(key)}  ({size/1e6:.1f} MB)")
        s3.download_file(BUCKET, key, dest)
    print(f"Done → {args.out}/")

if __name__ == "__main__":
    main()
