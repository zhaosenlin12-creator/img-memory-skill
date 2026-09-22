---
name: create-photo-flipbook-ui
description: Curate and sequence supplied photographs, finished pages, contact sheets, or existing book HTML into a responsive 3D page-turning photobook website using raw HTML, CSS, and vanilla JavaScript. Use for photo flipbooks, albums, zines, lookbooks, portfolios, sequencing raw photos, wrapping designed pages, or orchestrating a visual photo skill into a book. The advanced default path adds a story timeline with dates/places/ages, mixed visual direction (illustrated covers plus artistic photo cards), ambient motion, background music and page-flip sound, and PDF export, all data-driven from one metadata file. This style-neutral engine owns book editing and presentation while routing visual transformation to a curated list of separate photo skills.
---

# Create Photo Flipbook UI

Own the book, not the visual style. Curate, sequence, pace, pair, and present the work; route image transformation to a separate photo skill. Reuse the bundled runtime and do not force finished artwork through redesign.

## Intent gate

Use the finished-page fast path only when the user explicitly asks to assemble the supplied images as-is, preserve their order, perform no editing, or simply wrap them in a book UI. If the request is ambiguous, default to the editing path.

## Choose the path

### Finished-page fast path

Trigger this path only from an explicit no-edit or assemble-as-is request. It applies to raw photographs and designed pages alike.

- Preserve every supplied image and its artwork exactly.
- Make each image one complete HTML leaf; do not crop, caption, or redesign it.
- Derive the book ratio from the finished pages. Normalize the longer UI edge to at most `640`; never use raw pixel dimensions as UI dimensions.
- Use the exact common ratio when dimensions match. Otherwise use the dominant ratio with `contain`.
- Preserve a supplied front cover. Otherwise make a restrained cover whose surface color matches the empty back cover.
- Copy the runtime, insert the pages, set ratio and colors, validate, and stop.

### Default editing path (advanced)

Use this path whenever the user has not explicitly declined editing. For more than three images, generate and actually view a contact sheet before making editorial decisions; creating the file is not inspection.

For standalone photographs, edit selection, sequence, pairings, pacing, and spread roles. For already-designed pages, treat each page image as an indivisible artwork: edit selection, sequence, pacing, blank leaves, and covers, but do not alter its internal composition unless requested.

Follow this order:

1. Generate and view a source contact sheet.
2. Explore the collection before editing it. Identify its strongest subjects, recurring motifs, visual range, emotional register, technical limits, and possible forms. Open originals only to resolve focus, expression, crop, or near-duplicates.
3. **Draft the story timeline and metadata.** Before writing a single page, build the narrative spine: propose chapters (or one continuous arc), assign each selected photo a date, a place, and an age/stage line, and draft one warm caption per photo plus a lead sentence and motto per chapter. When dates or places are unknown, infer them from photo content (home, hospital, park, lake, field, village...) and mark them clearly as draft so the user can correct them. Keep all of this in one metadata JSON (see `scripts/build_book.py` for the schema) so the book is fully data-driven and every caption, date, place, and age is a single editable field.
4. Read [photo-skill-catalog.md](references/photo-skill-catalog.md). Use the user's named compatible photo skills when supplied; otherwise choose the smallest set of listed skills that fits the collection. One is usually sufficient, but choose more than one when their combination has a clear purpose and can form one coherent book. If none fits, keep the photographs visually unchanged rather than inventing a house style. Read [book-editing.md](references/book-editing.md) as baseline knowledge, not a fixed recipe, and [card-design-system.md](references/card-design-system.md) for the bundled default card grammar.
5. **Choose the visual direction.** The default mixed direction keeps real people recognizable: illustrated cover, chapter dividers, and closing (generated or supplied artwork) carry the stylized, storybook warmth, while content cards keep AI-treated photographs with the subject's face and features untouched. If the user names a photo skill or a specific style, let its grammar override the default; the mixed structure (illustrated bookends + photographic content) survives because it keeps faces true while still looking designed.
6. **Treat the photographs.** For the content cards, deliver one treated image per selected photo at the leaf ratio (9:16 by default) with a consistent treatment: warm, soft-light grading, film grain, gentle re-framing to center the subject, and no change to facial identity. Re-frame non-matching ratios by extending environment color, not by hard-cropping people. If a photo skill or safety gate rejects a specific image, keep the original photo and mark that card `"raw": true` so the runtime applies a CSS warm-filter fallback; disclose the fallback in your report. Curate only photographs that are both strong and suitable for that direction, then design the complete sequence and its changing rhythm before generating artwork. Do not preserve every image or filename order automatically.
7. Generate the outside-cover spread first: the left half is the back cover and the right half is the front cover. Then generate every interior double-page spread in reading order, or assemble single-leaf pages when the metadata-driven card path is chosen. Keep one spread ratio and consistent dimensions, protect the intended gutter, and treat each accepted spread as indivisible artwork.
8. **Add sound and motion.** Generate a warm, loop-friendly background track (30–60s) and a soft paper-flip sound, place them at `assets/audio/music.mp3` and `assets/audio/flip.mp3`, and keep the template's `<audio>` wiring and `book-extra.js` (music toggle + flip sound). Use the default ambient motion (ken-burns on illustrated pages, floating particles, twinkling stars, warm bokeh, chapter motifs) from the design system; adapt or reduce it when the book's register is quieter. If audio generation is unavailable, the book still works silently — report that.
9. **Assemble with the bundled scripts.** Run `scripts/build_book.py` against the metadata to emit `index.html` into the output root, copy the runtime, and patch `flipbook.js` to expose the engine for sound hooks. Run `scripts/make_preview.py` to inspect every leaf at a glance, and `scripts/make_print.py` to produce `print.html` for PDF export.
10. Build a contact sheet from the accepted full spreads in reading order. Review the final contact sheet / page preview using every relevant selected photo skill's quality gate and the book-level rhythm critique in [book-editing.md](references/book-editing.md). Regenerate only clear visual failures, revise only clear sequencing failures, then export final HTML and PDF when requested.

### Mixed or existing-book inputs

On the default editing path, preserve the internal artwork of polished pages while editing unresolved photographs and the book-level sequence. Modify supplied HTML in place when practical. Preserve filenames, captions, and existing controls unless requested otherwise; preserve ordering only on the fast path or when explicitly requested.

## Visual skill routing

- Keep this skill free of visual styles, artist references, palettes, texture systems, typography systems, and generation prompts. The bundled [card-design-system.md](references/card-design-system.md) is a default grammar owned by this skill; a user-named photo skill overrides its look.
- Choose one or more visual photo skills according to the collection. Prefer the smallest sufficient set; combine skills only when their visual languages are compatible and their different roles strengthen the sequence.
- Treat [photo-skill-catalog.md](references/photo-skill-catalog.md) as the default allowlist. A user may explicitly name another available photo skill; use it when its output can become a page or spread without violating the runtime contract.
- If a selected skill is unavailable, state that briefly and use the closest available catalog entry only when the substitution preserves the requested direction.
- Do not copy another skill's instructions into this skill. Extend the catalog with a routing entry instead.

## Style fidelity vs book coherence

Treat each selected photo skill as a visual grammar, not a rigid spread template.

- Preserve its signature invariants: source-photo treatment, material or process character, palette logic, typography behavior, collage or illustration language, and quality gate.
- Let the selected grammar shape editorial decisions too. A sparse style may demand a shorter edit and longer pauses; a layered or multi-photo style may support denser pairings and faster passages. Decide from the selected skill set rather than applying one universal sequencing formula.
- Vary book-level composition when the sequence needs it: image count and scale, density, negative space, contrast, crop or bleed, accent intensity, text presence, visual weight, and quiet versus peak spreads.
- Adapt a page- or poster-oriented skill to the book's spread ratio while keeping its recognizable grammar. Do not repeat one recipe across the whole book.
- Maintain continuity through a limited recurring palette, type system, material language, and motifs. Create rhythm through deliberate changes in space, scale, contrast, density, and emotional temperature.
- Prefer a coherent book over isolated showpiece spreads. When combining skills, unify them through shared palette, typography, materials, image treatment, or recurring motifs; assign each skill a consistent purpose rather than switching styles arbitrarily.

## Runtime

Copy `assets/html/` into the output root when a runtime is needed. Keep raw `.book-page` elements inside `#book`; do not introduce React, TypeScript, JSX, Vite, or a required page manifest.

Place `index.html` directly in the requested output root. Do not create a nested `site/` directory unless requested. Put unchanged photographs under `assets/photos/`, accepted full-spread artwork under `assets/spreads/`, split runtime leaves under `assets/pages/`, and generated audio under `assets/audio/`.

Make each transformed `.book-page` contain only its accepted artwork image. Do not reconstruct, decorate, caption, or repair another photo skill's artwork with HTML or CSS. For cards built by this skill's own default grammar (metadata-driven captions), the HTML caption block is the intended artwork and is editable data, not a repair.

Keep these invariants:

- Only the first and last leaves use `data-density="hard"`; interior leaves remain soft.
- Add a blank interior leaf when correct spread pairing requires it.
- On the editing path, keep the generated back cover as the final hard leaf. On the fast path, preserve a supplied back cover; only use an empty final leaf when no back cover exists, matching its surface color to the front cover.
- Lock controls while renderer state is not `read`.
- Preserve mouse, touch, buttons, keyboard, desktop-spread, and mobile single-page behavior.
- Constrain the book by viewport width and height.
- Do not add a visible center gap or book-level overlay. Use page-bound pseudo-elements above page content for spine shadows so photographs cannot cover them and the shadows move with turns.
- Keep the sound wiring intact: `#bgm` looped track, `#sfx-flip` page-flip sound, `#music-toggle` button, `book-extra.js` started after `flipbook.js`, and `window.__bookFlip` exposed by `flipbook.js`. All audio failures must fail silently.

## Scripts

Pass filenames in the exact display order; the scripts do not discover or sort files. Stable IDs come from the supplied labels.

```bash
# source photos or accepted spreads
python3 scripts/make_contact_sheet.py --output contact-sheet.jpg image-03.jpg image-01.jpg image-08.jpg

# assemble the book from metadata + treated photos + runtime
python3 scripts/build_book.py --runtime skills/create-photo-flipbook-ui/assets/html \
  --metadata captions.json --photos assets/photos --out book

# inspect every leaf as a preview grid, then export a per-leaf PDF
python3 scripts/make_preview.py --book book --out preview
python3 scripts/make_print.py --book book
chrome --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=book.pdf "file://$(pwd)/print.html"
```

Review the final contact sheet or preview using every relevant selected photo skill's quality gate and the book-editing critique, and verify the PDF page count equals the leaf count.

## Validation

- Verify referenced assets exist and copied sources remain unchanged.
- Run `node --test html-contract.test.mjs` after copying the runtime.
- Check page count, order, cover density, source references, selected ratio, and matching cover colors programmatically.
- On the editing path, verify the finished artwork order and inspect its page preview/contact sheet.
- Confirm the sound wiring is present (audio ids, toggle button, `book-extra.js`, `window.__bookFlip`) and that missing audio files fail silently.
- Do not use browser interaction to test animation. Do not claim animation was tested.
- Do not claim PDF delivery unless a PDF file was actually generated and validated.
- Report checks that passed and provide the start command.

From the directory containing `index.html`, serve the book with:

```bash
python3 -m http.server 4173
```
