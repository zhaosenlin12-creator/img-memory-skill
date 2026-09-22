# Card Design System (Default Editing Path)

The bundled runtime ships one coherent, premium card design system for the
**default editing path**. Treat it as the engine's default visual grammar: adapt
its tokens to the collection, do not treat it as a rigid template, and never let
it override a user-named visual photo skill when one is supplied.

This file documents the system's invariants, tokens, and wiring so an agent can
adapt it coherently (ratio, palette, typography, animation, sound) without
breaking the runtime contract.

## 1. Page geometry

- Single-leaf ratio: **9:16 portrait** (`data-page-width="360" data-page-height="640"`).
  Chosen because phone-captured collections are dominated by tall photos; a
  9:16 leaf needs almost no crop for 9:16 sources.
- A full spread shows two 9:16 leaves side by side; mobile falls back to single
  pages automatically via the runtime.
- All generated photos should be delivered at the leaf ratio. When a source is a
  different ratio, re-frame with an AI edit (extend environment colors top/bottom
  to 9:16) instead of hard-cropping people.
- Never exceed 640 on either UI dimension (`html-contract.test.mjs` enforces it).

## 2. Palette tokens

```css
--paper: #f5efe3;   /* cream page surface */
--ink:   #3a3128;   /* warm near-black text */
--accent:#c0714c;   /* terracotta accent */
--cream: #faf5ea;   /* text on photos */
```

Warm cream + terracotta + soft neutral is the default family. When adapting to a
different collection, change these four tokens plus the scrim opacities, and
keep every other declaration token-driven.

## 3. Typography

- Display / titles: **Kai (楷体) serif stack** for warmth:
  `"Kaiti SC","STKaiti","KaiTi","Noto Serif SC",serif`.
- Body captions on photos: same Kai stack, `21px`, line-height `1.62`.
- Kickers, folios, meta, page numbers: `Arial` small caps with
  `letter-spacing: 0.2em` and `text-transform: uppercase`.

## 4. Page layouts

- **Photo card** (`.card`): full-bleed photo
  (`object-fit: cover; object-position: 50% 34%`), bottom gradient scrim, and a
  bottom caption block: kicker (chapter), story text, meta line
  (`date · place`), age line. Add `card--raw` when a photo could not be
  AI-treated: a CSS warm filter (`sepia(0.18) saturate(1.1) brightness(1.05)`)
  keeps it visually coherent.
- **Illustrated cover** (`.cover-page`): full-bleed illustration, stronger
  bottom scrim, kicker + big Kai title + subtitle + period.
- **Chapter divider** (`.divider`): full-bleed illustration, kicker (English
  chapter), chapter number + title, a one-to-two line narrative `lead`, and a
  small `motto`.
- **Text page** (`.text-page`): cream surface, centered dedication text with an
  accent-colored signature line.
- **Back cover** (`.back-cover`): quiet illustration, single folio line.

## 5. Chapter motifs

Each photo card carries a small chapter motif (top-left, stroked SVG, white at
~55% opacity) that gives the book a recurring visual language:

| chapter idea | class        | motif |
|---|---|---|
| Expectation  | `motif--heart` | heart |
| Arrival      | `motif--moon`  | moon  |
| Growing      | `motif--star`  | star  |
| Exploring    | `motif--sun`   | sun   |

Invent motifs for other narratives; keep them single glyphs, stroked, and quiet.

## 6. Ambient motion

All motion is CSS-only, cheap, and disabled or neutralized in print:

- `@keyframes floatUp` — warm petal/spark particles rising on covers
  (`.particles i`, positioned per-child with duration/delay).
- `@keyframes twinkle` — small stars pulsing on dividers and the closing page
  (`.twinkles i`).
- `@keyframes kenburns` — slow breathing zoom on illustrated backgrounds
  (`.bg--kenburns`, 26s alternate, `transform-origin: 50% 32%`).
- `.ambient` — radial warm bokeh glows blended with `mix-blend-mode: screen`
  over photo cards.

Use these as defaults. Reduce or remove them for a quieter, formal, or
reduced-motion audience; `@media (prefers-reduced-motion: reduce)` already
neutralizes scrolling; extend it if you strip the keyframes.

## 7. Sound wiring

The template ships two `<audio>` elements and a toggle button:

- `#bgm` → `assets/audio/music.mp3` (looped background track).
- `#sfx-flip` → `assets/audio/flip.mp3` (short page-flip sound).
- `#music-toggle` → header button that toggles the track.

`book-extra.js`:

- exposes the flip engine as `window.__bookFlip` (set by `flipbook.js`);
- plays `sfx-flip` on every `flip` event, throttled to ~140ms;
- tries to autoplay `bgm`, then starts it on the first
  pointer/key/touch interaction (browsers block unmuted autoplay);
- never throws when audio files are missing (the agent generates them at build
  time; if generation is unavailable, the book still works silently).

When building a book, generate a warm, loop-friendly background track
(30–60s) and a soft 0.5–1.5s paper-flip sound with the available audio
generation tool, place them as `music.mp3` / `flip.mp3` under `assets/audio/`,
and prefer compressed formats (MP3/OGG) over WAV to keep the book light.

## 8. Print & PDF

`print.html` (built by `scripts/make_print.py`) stacks every leaf at
360×640px with `@page{size:360px 640px;margin:0}` and exact color printing.
The print stylesheet hides the header, controls, music button, motifs, bokeh,
particles, and twinkles, and disables ken-burns, so exported PDF pages match
the on-screen artwork without UI or animation artifacts.

Export with a headless browser:

```bash
chrome --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=book.pdf "file://$(pwd)/print.html"
```

Verify the PDF page count equals the leaf count and spot-check a rendered page.

## 9. Adaptation checklist

When the collection demands a different look, change in this order: palette
tokens → typography stack → motif set → animation intensity → sound character.
Keep the structural contracts (leaf ratio ≤ 640, hard covers, interior soft,
page-ratio consistency, gutter safety) untouched.
