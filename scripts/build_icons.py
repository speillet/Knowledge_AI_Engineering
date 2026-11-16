#!/usr/bin/env python3
"""Render the tab and home-screen icons of the website from website/assets/icons/favicon.svg.

The ICO and PNG files live in website/static/, where they replace the Blowfish defaults of the
same names. Run `make icons` after changing the SVG, then commit the files. Unlike the other
scripts, this one needs cairosvg and Pillow: python3 -m pip install cairosvg pillow
"""

import io
import re

import cairosvg
from PIL import Image

from lint_flashcards import ROOT

SVG = ROOT / "website/assets/icons/favicon.svg"
STATIC = ROOT / "website/static"
BACKGROUND = "#7c3aed"
# Home-screen icons are cropped by the system: Android keeps a circle of 40 % of the size.
TOUCH_SCALE = 0.76
MASKABLE_SCALE = 0.72


def render(svg: str, size: int) -> Image.Image:
    """The SVG as an RGBA image of size x size pixels."""
    png = cairosvg.svg2png(bytestring=svg.encode("utf-8"), output_width=size, output_height=size)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def full_bleed(svg: str, scale: float) -> str:
    """The icon drawing on a square background, scaled around the centre."""
    defs = re.search(r"<defs>.*?</defs>", svg, re.S)
    drawing = svg.split(f'fill="{BACKGROUND}"/>', 1)[1].rsplit("</svg>", 1)[0]
    offset = 24 * (1 - scale)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">'
        + (defs[0] if defs else "")
        + f'<rect width="48" height="48" fill="{BACKGROUND}"/>'
        + f'<g transform="translate({offset:.2f} {offset:.2f}) scale({scale})">{drawing}</g></svg>'
    )


def main() -> None:
    svg = SVG.read_text(encoding="utf-8")
    for size in (16, 32):
        render(svg, size).save(STATIC / f"favicon-{size}x{size}.png", optimize=True)
    render(svg, 48).save(STATIC / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    render(full_bleed(svg, TOUCH_SCALE), 180).convert("RGB").save(STATIC / "apple-touch-icon.png", optimize=True)
    for size in (192, 512):
        icon = render(full_bleed(svg, MASKABLE_SCALE), size).convert("RGB")
        icon.save(STATIC / f"android-chrome-{size}x{size}.png", optimize=True)
    print(f"Rendered the icons of {SVG.relative_to(ROOT)} into {STATIC.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
