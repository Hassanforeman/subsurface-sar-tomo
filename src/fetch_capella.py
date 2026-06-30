#!/usr/bin/env python3
"""
fetch_capella.py — download a free Capella open-data SAR scene (cross-sensor check).

Public bucket: s3://capella-open-data  (CC-BY 4.0, no credentials).
Companion to fetch_umbra.py. Capella organises by DATE, not by task/location, and the
capture id embeds the date (…_HH_YYYYMMDDhhmmss_…), so you only need the capture id.

Runs on your Mac. Install deps first:  pip install boto3

Examples
--------
# Download the curated "Cairo" spotlight SICD (central Cairo, 2024-11-23) into ./data/:
python src/fetch_capella.py --capture CAPELLA_C13_SP_SICD_HH_20241123062737_20241123062813

# Any other open capture id works the same way:
python src/fetch_capella.py --capture CAPELLA_C13_SP_CPHD_HH_20241123085831_20241123085910
"""
import argparse, os, re, sys

BUCKET = "capella-open-data"


def _client():
    import boto3
    from botocore import UNSIGNED
    from botocore.config import Config
    # Capella open data lives in us-west-2; UNSIGNED = no credentials needed.
    return boto3.client("s3", region_name="us-west-2",
                        config=Config(signature_version=UNSIGNED))


def _date_from_capture(capture):
    """Pull YYYY/MM/DD from the 14-digit timestamp inside the capture id."""
    m = re.search(r"(\d{8})\d{6}", capture)
    if not m:
        sys.exit("Could not find a YYYYMMDD timestamp in --capture; check the id.")
    d = m.group(1)
    return d[0:4], d[4:6], d[6:8]


def main():
    ap = argparse.ArgumentParser(description="Fetch a free Capella open-data scene.")
    ap.add_argument("--capture", required=True,
                    help="capture id, e.g. CAPELLA_C13_SP_SICD_HH_20241123062737_20241123062813")
    ap.add_argument("--ext", default="ntf",
                    help="file extension for the product (default ntf for SICD/SLC; use cphd for CPHD)")
    ap.add_argument("--out", default="data", help="output dir (default ./data)")
    args = ap.parse_args()

    try:
        s3 = _client()
    except Exception as e:
        sys.exit("Need boto3:  pip install boto3   (%s)" % e)

    yyyy, mm, dd = _date_from_capture(args.capture)
    key = f"data/{yyyy}/{mm}/{dd}/{args.capture}/{args.capture}.{args.ext}"
    os.makedirs(args.out, exist_ok=True)
    dest = os.path.join(args.out, f"{args.capture}.{args.ext}")

    # size (for a sanity check) then download
    try:
        size = s3.head_object(Bucket=BUCKET, Key=key)["ContentLength"]
    except Exception as e:
        sys.exit(f"Could not find s3://{BUCKET}/{key}\n  ({e})\n"
                 "Re-check the capture id / --ext (SICD & SLC are .ntf, CPHD is .cphd).")
    print(f"↓ {os.path.basename(key)}  ({size/1e9:.2f} GB)  -> {dest}")
    s3.download_file(BUCKET, key, dest)
    print(f"Done → {dest}")


if __name__ == "__main__":
    main()
