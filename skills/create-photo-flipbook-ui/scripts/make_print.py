#!/usr/bin/env python3
"""Build print.html from a built book for exact PDF export.

Usage:
    python3 scripts/make_print.py --book book

Writes <book>/print.html stacking every leaf at 360x640 with
`@page{size:360px 640px;margin:0}` and exact color printing, so a headless
browser can export a per-leaf PDF:

    chrome --headless=new --disable-gpu --no-pdf-header-footer \
      --print-to-pdf=book.pdf "file://$(pwd)/print.html"
"""
import argparse
import io
import os
import re

CELLS_CSS = """
html,body{margin:0;padding:0;background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
.cell{width:360px;height:640px;position:relative;overflow:hidden;page-break-after:always;break-after:page;}
.cell:last-child{page-break-after:auto;break-after:auto;}
.cell .book-page{width:100%;height:100%;}
.cell .book-page::after,.cell .book-page::before{display:none;}
.cell .page-number{position:absolute;}
@page{size:360px 640px;margin:0;}
"""


def main():
    ap = argparse.ArgumentParser(description="Build print.html for PDF export.")
    ap.add_argument("--book", required=True, help="Built book directory containing index.html and styles.css")
    args = ap.parse_args()

    with io.open(os.path.join(args.book, "index.html"), encoding="utf-8") as f:
        html = f.read()
    arts = re.findall(r"<article.*?</article>", html, re.S)
    if not arts:
        raise SystemExit("No .book-page articles found in index.html")
    cells = "\n".join(f'<div class="cell">{a}</div>' for a in arts)
    preview = (
        '<!doctype html><html><head><meta charset="utf-8"><title>Print</title>'
        '<link rel="stylesheet" href="styles.css"><style>' + CELLS_CSS + "</style></head><body>"
        + cells + "</body></html>"
    )
    out = os.path.join(args.book, "print.html")
    with io.open(out, "w", encoding="utf-8") as f:
        f.write(preview)
    print(f"Wrote {out} with {len(arts)} leaves")


if __name__ == "__main__":
    main()
