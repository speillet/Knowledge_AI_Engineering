#!/usr/bin/env python3
"""Render editable SVG diagrams to 2x PNGs for offline flashcards.

Optional authoring dependency only (exports use the committed PNGs):
    python3 -m pip install playwright
    python3 -m playwright install chromium
    python3 scripts/build_diagrams.py
"""

import xml.etree.ElementTree as ET

from playwright.sync_api import sync_playwright

from lint_flashcards import ROOT


def main() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(device_scale_factor=2)
        for source in sorted((ROOT / "assets/diagrams").glob("*.svg")):
            svg = ET.fromstring(source.read_text(encoding="utf-8"))
            width, height = int(svg.attrib["width"]), int(svg.attrib["height"])
            page.set_viewport_size({"width": width, "height": height})
            page.goto(source.as_uri())
            page.locator("svg").screenshot(path=str(source.with_suffix(".png")))
            print(f"Rendered {source.stem}: {width * 2} x {height * 2} pixels")
        browser.close()


if __name__ == "__main__":
    main()
