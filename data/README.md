# data/

Raw SAR products land here (gitignored — they're large, hundreds of MB to a few GB
per scene). Nothing here is committed.

## First scene (pinned, free)
Umbra open data, Bingham Copper Mine, UMBRA-05, 2024-01-12. Pull it with:

```bash
python src/fetch_umbra.py --task "Bingham Copper Mine" \
  --collect 2024-01-12-04-09-18_UMBRA-05 --products CPHD SICD METADATA
```

Files you'll get per collect:
- `*_CPHD.cphd`   — compensated phase history (best input for sub-aperture work)
- `*_SICD.nitf`   — single-look complex (amplitude + phase)
- `*_GEC.tif`     — geocoded quicklook (for orientation)
- `*_METADATA.json`

Bucket (public, CC-BY 4.0, no signup): `s3://umbra-open-data-catalog`
