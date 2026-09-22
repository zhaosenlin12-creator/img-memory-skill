#!/usr/bin/env python3
"""Build a static preview page of every leaf for visual review.

Usage:
    python3 scripts/make_preview.py --book book [--out preview.html] [--per <n>]

Writes one HTML file per chunk of at most --per leaves (default 18), rendering
each leaf at 210x373px in a grid. Screenshot the files with a headless browser
to review the whole book at a glance:

    chrome --headless=new --disable-gpu --window-size=1850,1500 \\
      --screenshot=preview.png "file://$(pwd)/preview-1.html"
"""
import argparse
import io
import os
import re

GRID_CSS = """
body{margin:0;background:#cfc7b6;padding:20px;display:flex;flex-wrap:wrap;gap:14px;justify-content:center;}
.cell{width:210px;height:373px;position:relative;flex:0 0 auto;box-shadow:0 6px 18px rgba(0,0,0,.25);border-radius:6px;overflow:hidden;background:#f5efe3;}
.cell .book-page{width:100%;height:100%;}
.cell .book-page::after,.cell .book-page::before{display:none;}
.cell .page-number{position:absolute;}
"""


def main():
    ap = argparse.ArgumentParser(description="Build static preview grids of a built book.")
    ap.add_argument("--book", required=True, help="Built book directory containing index.html and styles.css")
    ap.add_argument("--out", default="preview.html", help="Output stem for preview HTML files (default: preview.html)")
    ap.add_argument("--per", type=int, default=18, help="Leaves per preview file")
    args = ap.parse_args()

    with io.open(os.path.join(args.book, "index.html"), encoding="utf-8") as f:
        html = f.read()
    arts = re.findall(r"<article.*?</article>", html, re.S)
    if not arts:
        raise SystemExit("No .book-page articles found in index.html")

    base, ext = os.path.splitext(args.out)
    chunks = [arts[i : i + args.per] for i in range(0, len(arts), args.per)]
    for i, chunk in enumerate(chunks, 1):
        cells = "\n".join(f'<div class="cell">{a}</div>' for a in chunk)
        page = (
            '<!doctype html><html><head><meta charset="utf-8"><title>Preview</title>'
            '<link rel="stylesheet" href="styles.css"><style>' + GRID_CSS + "</style></head><body>"
            + cells + "</body></html>"
        )
        out = f"{base}-{i}{ext}" if len(chunks) > 1 else args.out
        if not os.path.isabs(out):
            out = os.path.join(args.book, out)
        with io.open(out, "w", encoding="utf-8") as f:
            f.write(page)
        print(f"Wrote {out} ({len(chunk)} leaves)")


if __name__ == "__main__":
    main()
