# -*- coding: utf-8 -*-
"""Turn phone photos into fast, privacy-safe WebP files for the site.
Put photos in C:\\sheroot\\photos-inbox, named by where they go, then run:
    python _build/optimize_photos.py && python _build/build.py

Names:  hero.jpg            -> big photo in the Home hero (the practice / the people)
        team.jpg            -> About page team photo
        clinic-1.jpg ...    -> Home 'Inside the clinic' gallery (clinic-1, clinic-2, ...)
        service-<slug>.jpg  -> photo on that treatment page, e.g. service-neck-pain.jpg
Re-encoding strips hidden metadata (GPS location, device info) that phones add to photos."""
import os, glob
from PIL import Image, ImageOps
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE) + os.sep
SRC = ROOT + 'photos-inbox/'; OUT = ROOT + 'images/photos/'; os.makedirs(OUT, exist_ok=True)
MAX = {'hero': 1600}
n = 0
for p in sorted(glob.glob(SRC + '*')):
    base, ext = os.path.splitext(os.path.basename(p))
    if ext.lower() not in ('.jpg', '.jpeg', '.png', '.webp'):
        print('skipped (unsupported type, convert to JPG):', os.path.basename(p)); continue
    im = ImageOps.exif_transpose(Image.open(p)).convert('RGB')   # fixes phone rotation
    name = base.lower().replace(' ', '-')
    im.thumbnail((MAX.get(name, 1400),) * 2, Image.LANCZOS)
    im.save(OUT + name + '.webp', 'WEBP', quality=80, method=6)
    print(f'{name}.webp  {im.size[0]}x{im.size[1]}  {os.path.getsize(OUT + name + ".webp")//1024} KB'); n += 1
print(n, 'photo(s) ready')
