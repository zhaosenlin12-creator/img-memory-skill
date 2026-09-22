#!/usr/bin/env python3
"""Assemble a flipbook from metadata and treated photos into the bundled runtime.

Usage:
    python3 scripts/build_book.py \
        --runtime skills/create-photo-flipbook-ui/assets/html \
        --metadata captions.json \
        --photos assets/photos \
        --out book

The metadata JSON drives every page. Expected shape:

{
  "book": {
    "title": "...", "subtitle": "...", "period": "...",
    "intro": "line1\\nline2", "dedication": "..."
  },
  "chapters": [
    {"id": "ch1", "no": "第一章", "title": "...", "motto": "...", "lead": "line1\\nline2"}
  ],
  "cards": [
    {"id": 1, "chapter": "ch1", "date": "...", "place": "...", "age": "...",
     "text": "...", "raw": false}
  ],
  "closing": "line1\\nline2"
}

Photos are expected at <out>/assets/photos/t-<id:02d>.jpg unless --photos is
given, in which case files are copied from that directory. A card with
"raw": true is rendered with the CSS warm-filter fallback (for photos that
could not be AI-treated). The script patches flipbook.js once to expose
window.__bookFlip for the sound hooks in book-extra.js.
"""
import argparse
import io
import json
import os
import re
import shutil


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def patch_flipbook(src_text):
    if "window.__bookFlip" in src_text:
        return src_text
    return src_text.replace(
        "pageFlip.loadFromHTML(pages);",
        "pageFlip.loadFromHTML(pages);\nwindow.__bookFlip = pageFlip;",
    )


MOTIFS = {
    "ch1": (
        "heart",
        '<path d="M12 21s-7-4.6-9.6-9.2C.9 8.6 3.4 5 7 5c2 0 3.4 1 5 2.8C13.6 6 15 5 17 5c3.6 0 6.1 3.6 4.6 6.8C19 16.4 12 21 12 21z"/>',
    ),
    "ch2": (
        "moon",
        '<path d="M20.5 14.2A8.5 8.5 0 1 1 9.8 3.5a7 7 0 0 0 10.7 10.7z"/>',
    ),
    "ch3": (
        "star",
        '<path d="M12 2.5l2.8 6.4 6.9.6-5.3 4.5 1.6 6.8L12 17.2l-6 3.6 1.6-6.8L2.3 9.5l6.9-.6z"/>',
    ),
    "ch4": (
        "sun",
        '<circle cx="12" cy="12" r="4.4"/><path d="M12 1.8v2.6M12 19.6v2.6M1.8 12h2.6M19.6 12h2.6M4.6 4.6l1.8 1.8M17.6 17.6l1.8 1.8M19.4 4.6l-1.8 1.8M6.4 17.6l-1.8 1.8"/>',
    ),
}


def motif(ch_id):
    name, path = MOTIFS.get(ch_id, MOTIFS["ch3"])
    return (
        f'<div class="motif motif--{name}" aria-hidden="true">'
        f'<svg viewBox="0 0 24 24" width="26" height="26">{path}</svg></div>'
    )


def particles(n=10):
    return f'<div class="particles" aria-hidden="true">{"<i></i>" * n}</div>'


def twinkles(n=5):
    return f'<div class="twinkles" aria-hidden="true">{"<i></i>" * n}</div>'


def build(meta, out):
    book = meta["book"]
    chapters = {c["id"]: c for c in meta["chapters"]}
    cards = sorted(meta["cards"], key=lambda c: c["id"])
    pages = []

    def push(s):
        pages.append(s)

    push(
        f'''            <article class="book-page cover-page" data-density="hard" aria-label="Front cover">
              <img class="bg bg--kenburns" src="assets/pages/cover.jpg" alt="Cover art" />
              <div class="scrim scrim--cover"></div>
              {particles(10)}
              <div class="cover-content">
                <p class="kicker">A little journey</p>
                <h1>{esc(book["title"])}<br/>{esc(book.get("title2", ""))}</h1>
                <p class="subtitle">{esc(book.get("subtitle", ""))}</p>
                <p class="folio">{esc(book.get("period", ""))}</p>
              </div>
            </article>'''
    )

    intro_html = "<br/>".join(esc(l) for l in book.get("intro", "").split("\n") if l.strip())
    push(
        f'''            <article class="book-page text-page" aria-label="Title page">
              <div class="text-content">
                <p class="kicker">To our little one</p>
                <p class="body">{intro_html}</p>
                <p class="dedication">{esc(book.get("dedication", ""))}</p>
              </div>
              <p class="page-number">02</p>
            </article>'''
    )

    def divider(ch):
        en = {"ch1": "Chapter One", "ch2": "Chapter Two", "ch3": "Chapter Three", "ch4": "Chapter Four"}.get(
            ch["id"], ch["no"]
        )
        lead = "<br/>".join(esc(l) for l in ch.get("lead", "").split("\n") if l.strip())
        return f'''            <article class="book-page divider" aria-label="{esc(ch["no"])} {esc(ch["title"])}">
              <img class="bg bg--kenburns" src="assets/pages/{ch["id"]}.jpg" alt="Chapter art" />
              <div class="scrim scrim--divider"></div>
              {twinkles(5)}
              <div class="divider-content">
                <p class="kicker">{en}</p>
                <h2>{esc(ch["no"])} · {esc(ch["title"])}</h2>
                <p class="lead">{lead}</p>
                <p class="motto">{esc(ch.get("motto", ""))}</p>
              </div>
            </article>'''

    def photo_card(c):
        ch = chapters[c["chapter"]]
        leaf = len(pages) + 1
        raw_cls = " card--raw" if c.get("raw") else ""
        return f'''            <article class="book-page card{raw_cls} card--{ch["id"]}" aria-label="Photo {c["id"]:02d}">
              <img class="card-photo" src="assets/photos/t-{c["id"]:02d}.jpg" alt="Photo {c["id"]:02d}" />
              <div class="scrim"></div>
              {motif(ch["id"])}
              <div class="ambient" aria-hidden="true"></div>
              <div class="card-caption">
                <p class="kicker">{esc(ch["no"])} · {esc(ch["title"])}</p>
                <p class="card-text">{esc(c["text"])}</p>
                <p class="card-meta">{esc(c.get("date", ""))} · {esc(c.get("place", ""))}</p>
                <p class="card-age">{esc(c.get("age", ""))}</p>
              </div>
              <p class="page-number">{leaf:02d}</p>
            </article>'''

    for ch in meta["chapters"]:
        push(divider(ch))
        for c in [c for c in cards if c["chapter"] == ch["id"]]:
            push(photo_card(c))

    closing_html = "<br/>".join(esc(l) for l in meta.get("closing", "").split("\n") if l.strip())
    push(
        f'''            <article class="book-page closing-page" aria-label="Closing page">
              <img class="bg bg--kenburns" src="assets/pages/closing.jpg" alt="Closing art" />
              <div class="scrim scrim--divider"></div>
              {twinkles(4)}
              <div class="divider-content">
                <p class="kicker">Epilogue</p>
                <h2>{closing_html}</h2>
              </div>
            </article>'''
    )

    push(
        '''            <article class="book-page back-cover" data-density="hard" aria-label="Back cover">
              <img class="bg" src="assets/pages/back.jpg" alt="Back cover art" />
              <div class="scrim scrim--back"></div>
              <div class="particles particles--soft" aria-hidden="true"><i></i><i></i><i></i></div>
              <p class="back-folio">陪你长大 · A Little Journey</p>
            </article>'''
    )

    page_block = "\n".join(pages)
    index_html = f'''<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{esc(book["title"])} · {esc(book.get("subtitle", ""))}</title>
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
    <main class="room">
      <header class="book-header">
        <span>Baby memory book</span>
        <h1>{esc(book["title"])}</h1>
        <div class="header-right">
          <button id="music-toggle" type="button" aria-label="Background music" title="Background music">&#9835;</button>
          <span id="orientation">Open spread</span>
        </div>
      </header>

      <section class="stage" aria-label="Interactive photo book">
        <div class="book-rig">
          <div id="book" class="book" data-page-width="360" data-page-height="640">
{page_block}
          </div>
        </div>
      </section>

      <footer class="controls" aria-label="Book controls">
        <button id="previous" type="button" aria-label="Previous page">&larr;</button>
        <div class="status" aria-live="polite">
          <span id="page-status">Cover</span>
          <small>Drag / tap a corner / arrow keys · ♪ music</small>
        </div>
        <button id="next" type="button" aria-label="Next page">&rarr;</button>
      </footer>
    </main>

    <audio id="bgm" src="assets/audio/music.mp3" loop preload="auto"></audio>
    <audio id="sfx-flip" src="assets/audio/flip.mp3" preload="auto"></audio>

    <script src="vendor/page-flip.browser.js"></script>
    <script src="flipbook.js"></script>
    <script src="book-extra.js"></script>
  </body>
</html>
'''
    with io.open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
    return len(pages)


def main():
    ap = argparse.ArgumentParser(description="Assemble a flipbook from metadata into the runtime.")
    ap.add_argument("--runtime", required=True, help="Path to the skill's assets/html runtime")
    ap.add_argument("--metadata", required=True, help="Captions/metadata JSON file")
    ap.add_argument("--photos", help="Optional source directory of treated photos (copied to out/assets/photos)")
    ap.add_argument("--out", required=True, help="Output root for the built book")
    args = ap.parse_args()

    with io.open(args.metadata, encoding="utf-8") as f:
        meta = json.load(f)

    os.makedirs(os.path.join(args.out, "assets", "photos"), exist_ok=True)
    os.makedirs(os.path.join(args.out, "assets", "audio"), exist_ok=True)

    # copy treated photos when provided
    if args.photos:
        cards = sorted(meta["cards"], key=lambda c: c["id"])
        for c in cards:
            src = os.path.join(args.photos, f"t-{c['id']:02d}.jpg")
            if not os.path.isfile(src):
                alt = os.path.join(args.photos, f"{c['id']:02d}.jpg")
                if os.path.isfile(alt):
                    src = alt
                else:
                    raise SystemExit(f"Missing photo for card {c['id']}: {src}")
            dst = os.path.join(args.out, "assets", "photos", f"t-{c['id']:02d}.jpg")
            if os.path.abspath(src) != os.path.abspath(dst):
                shutil.copyfile(src, dst)

    # copy runtime (flipbook.js patched once, book-extra.js, styles, vendor)
    shutil.copyfile(
        os.path.join(args.runtime, "flipbook.js"),
        os.path.join(args.out, "flipbook.js"),
    )
    src_js = io.open(os.path.join(args.out, "flipbook.js"), encoding="utf-8").read()
    io.open(os.path.join(args.out, "flipbook.js"), "w", encoding="utf-8").write(patch_flipbook(src_js))
    shutil.copyfile(os.path.join(args.runtime, "book-extra.js"), os.path.join(args.out, "book-extra.js"))
    shutil.copyfile(os.path.join(args.runtime, "styles.css"), os.path.join(args.out, "styles.css"))
    os.makedirs(os.path.join(args.out, "vendor"), exist_ok=True)
    shutil.copyfile(
        os.path.join(args.runtime, "vendor", "page-flip.browser.js"),
        os.path.join(args.out, "vendor", "page-flip.browser.js"),
    )
    shutil.copyfile(
        os.path.join(args.runtime, "vendor", "PAGE-FLIP-LICENSE"),
        os.path.join(args.out, "vendor", "PAGE-FLIP-LICENSE"),
    )

    count = build(meta, args.out)
    print(f"Built {count} leaves at {args.out}")


if __name__ == "__main__":
    main()
