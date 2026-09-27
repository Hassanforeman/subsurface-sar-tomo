#!/usr/bin/env python3
"""
press_image_audit.py — mechanical part of the descriptive audit in
docs/PREREGISTRATION_PRESS_IMAGES_2026-09-27.md (checklist item 7 + inventory).

For every image in data/secondsphinx_2026/: size, SHA-256, JPEG quality hints, and all EXIF / XMP
text (Software, Make, Model, CreatorTool, DateTime). Writes runs/press_image_audit.json and a
numbered contact sheet runs/press_contact_*.png (sheets stay out of git: they are copies of the images).

  python3 src/press_image_audit.py
"""
import hashlib, json, os, re
from PIL import Image, ExifTags

DIR = "data/secondsphinx_2026"
KEYS = ("Software", "Make", "Model", "DateTime", "DateTimeOriginal", "Artist", "ImageDescription",
        "HostComputer")


def exif_of(im):
    out = {}
    try:
        ex = im.getexif()
        for k, v in ex.items():
            name = ExifTags.TAGS.get(k, str(k))
            if name in KEYS:
                out[name] = str(v)
    except Exception as e:  # noqa
        out["_error"] = str(e)
    return out


def xmp_of(raw):
    m = re.search(rb"<x:xmpmeta.*?</x:xmpmeta>", raw, re.S)
    if not m:
        return {}
    x = m.group(0).decode("latin1", "replace")
    hits = {}
    for tag in ("CreatorTool", "Software", "softwareAgent", "History"):
        v = re.findall(rf'{tag}="([^"]+)"', x) + re.findall(rf"<[^>]*{tag}>([^<]+)<", x)
        if v:
            hits[tag] = sorted(set(v))[:5]
    return hits


def main():
    files = sorted(f for f in os.listdir(DIR) if f.lower().endswith((".jpg", ".jpeg", ".png")))
    rows = []
    for f in files:
        p = os.path.join(DIR, f)
        raw = open(p, "rb").read()
        im = Image.open(p)
        rows.append(dict(file=f, size=list(im.size), mode=im.mode, bytes=len(raw),
                         sha256=hashlib.sha256(raw).hexdigest(),
                         resized_copy=("-1024x" in f) or im.size == (1024, 767),
                         exif=exif_of(im), xmp=xmp_of(raw),
                         icc=bool(im.info.get("icc_profile"))))
        print(f"{f:<10} {im.size[0]}x{im.size[1]}  exif={rows[-1]['exif'] or '-'}  xmp={rows[-1]['xmp'] or '-'}")
    os.makedirs("runs", exist_ok=True)
    json.dump(dict(source="archaeologicalrescue.org/secondsphinx/ (fetch_press_images.sh)",
                   prereg="docs/PREREGISTRATION_PRESS_IMAGES_2026-09-27.md", n=len(rows), images=rows),
              open("runs/press_image_audit.json", "w"), indent=1)
    # contact sheets, 12 per sheet, 3 columns, labelled by file id
    from PIL import ImageDraw
    per = 12
    for s in range(0, len(files), per):
        chunk = files[s:s + per]
        sheet = Image.new("RGB", (3 * 520, 4 * 410), "white")
        d = ImageDraw.Draw(sheet)
        for i, f in enumerate(chunk):
            t = Image.open(os.path.join(DIR, f)).convert("RGB")
            t.thumbnail((510, 385))
            x, y = (i % 3) * 520, (i // 3) * 410
            sheet.paste(t, (x, y + 20))
            d.text((x + 4, y + 4), f, fill=(200, 0, 0))
        sheet.save(f"runs/press_contact_{s // per + 1}.png")
    print(f"{len(rows)} images -> runs/press_image_audit.json; contact sheets runs/press_contact_*.png")


if __name__ == "__main__":
    main()
