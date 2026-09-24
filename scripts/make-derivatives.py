#!/usr/bin/env python3
"""Make the stream's image derivatives from a source export.

For each source image this writes a WebP fallback and a set of AVIF sizes,
the same layout the feed images already use:

    assets/feed/<name>.webp                   fallback, at most 1250px wide
    assets/feed/responsive/<name>-480.avif    and 850 and 1250, never wider
                                              than the source

A source narrower than 1250px also gets an AVIF at its own width, so a
750px phone capture yields 480 and 750. AVIF uses quality 75 with 4:4:4
chroma, the settings the case-study derivatives were made with, and alpha
is kept. The originals are never changed.

    python3 scripts/make-derivatives.py qa/screenflow/trugreen-09.png
    python3 scripts/make-derivatives.py a.png b.png --name lawn-assessment-recommendation
    python3 scripts/make-derivatives.py source.png --out assets/feed --force

It prints the fallback's path, width, and height, ready for the item's
"media" in content/stream.json, then run node scripts/build-stream.mjs.

Needs Pillow with AVIF support (Pillow 11.3 or later), which this Mac has.
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, features

ROOT = Path(__file__).resolve().parents[1]
AVIF_WIDTHS = (480, 850, 1250)
FALLBACK_WIDTH = 1250


def resized(image, width):
    """The image scaled to `width`, keeping its aspect ratio."""
    if width >= image.width:
        return image
    height = round(image.height * width / image.width)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def prepare(image):
    """RGB, or RGBA when the source has transparency, so alpha survives."""
    has_alpha = image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info)
    return image.convert('RGBA' if has_alpha else 'RGB')


def write(path, image, force, **options):
    if path.exists() and not force:
        print(f'  kept     {path.relative_to(ROOT)} (exists; --force replaces it)')
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, **options)
    print(f'  wrote    {path.relative_to(ROOT)}  {image.width} × {image.height}')


def main():
    parser = argparse.ArgumentParser(description='Make WebP and AVIF derivatives for the stream.')
    parser.add_argument('sources', nargs='+', type=Path, help='source images, such as full-size PNG exports')
    parser.add_argument('--out', type=Path, default=Path('assets/feed'), help='folder for the fallback (default: assets/feed)')
    parser.add_argument('--name', help='output name, when there is one source; defaults to the source file name')
    parser.add_argument('--force', action='store_true', help='replace files that already exist')
    args = parser.parse_args()

    if not features.check('avif'):
        sys.exit('This Pillow cannot write AVIF. Pillow 11.3 or later includes it.')
    if args.name and len(args.sources) > 1:
        sys.exit('--name only works with one source.')

    out = (ROOT / args.out).resolve()
    for source in args.sources:
        name = args.name or source.stem
        with Image.open(source) as opened:
            image = prepare(opened)
        print(f'{source}  {image.width} × {image.height}')

        fallback = resized(image, FALLBACK_WIDTH)
        write(out / f'{name}.webp', fallback, args.force, format='WEBP', quality=80, method=6)

        widths = [w for w in AVIF_WIDTHS if w < image.width]
        if image.width <= FALLBACK_WIDTH:
            widths.append(image.width)
        for width in widths:
            write(out / 'responsive' / f'{name}-{width}.avif', resized(image, width), args.force,
                  format='AVIF', quality=75, subsampling='4:4:4')

        print(f'  media    "src": "{(out / f"{name}.webp").relative_to(ROOT)}", '
              f'"width": {fallback.width}, "height": {fallback.height}')


if __name__ == '__main__':
    main()
