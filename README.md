# Create Photo Flipbook UI

A style-neutral Codex skill that turns raw photo collections or finished pages into curated, page-turning photo books using raw HTML, CSS, and vanilla JavaScript.

The skill inspects the collection, chooses compatible visual photo skills, curates the strongest images, designs the sequence and rhythm, and assembles the accepted artwork into a responsive 3D flipbook. The **advanced default path** additionally turns the collection into a story: a timeline with dates, places, and ages; narrative captions and chapter leads; illustrated bookends around photographic content cards; ambient motion; background music and page-flip sound; and a per-leaf PDF export — all driven by one editable metadata file.

![Death Valley photo book open to a generated spread](docs/images/death-valley-flipbook.jpg)

## How it works

### 1. Inspect the raw photographs

For larger collections, the agent first creates and actually views an ordered contact sheet. This makes subject repetition, technical problems, visual motifs, and changes in scale or atmosphere legible before any images are selected.

![Contact sheet of 16 raw Death Valley photographs](docs/images/death-valley-raw-contact-sheet.jpg)

### 2. Choose the visual direction and edit the book

The flipbook engine does not own a house style. It chooses one or more compatible photo skills, reads their full instructions, and lets their visual behavior shape curation, pairing, pacing, and sequence. The default mixed direction keeps people recognizable: illustrated cover, chapter dividers, and closing carry the storybook warmth, while content cards keep AI-treated photographs with faces and features untouched.

The agent then:

- keeps quality above coverage;
- selects photographs that fit the visual direction;
- plans an opener, transitions, pauses, peaks, echoes, and ending when appropriate;
- varies density, scale, contrast, negative space, and emotional temperature;
- preserves one coherent material and visual language across the book.

In this Death Valley example, the agent selected 11 of 16 photographs and used the Gathered Scenes visual grammar.

### 3. Draft the story timeline and metadata

Before generating artwork, the agent builds the narrative spine in one metadata JSON: chapters (or a single arc), a date, a place, and an age/stage line for every photo, plus one warm caption per photo and a lead and motto per chapter. When dates or places are unknown, they are inferred from the photo content (home, hospital, park, lake, field, village…) and clearly marked as drafts for the user to correct.

### 4. Generate and review complete spreads

The outside cover is generated first as one spread — back cover on the left, front cover on the right — followed by every interior spread in reading order. A second contact sheet lets the agent judge the complete book at once and regenerate only clear failures.

![Contact sheet of seven generated Death Valley spreads](docs/images/death-valley-spread-contact-sheet.jpg)

This edit produced seven full spreads: one outside cover and six interiors. Their compositions change from spread to spread while paper, color, typography, and photographic treatment remain coherent.

### 5. Assemble, add sound and motion, and export

The bundled scripts assemble the metadata, treated photos, runtime, and audio into the book: `build_book.py` emits the HTML and patches the runtime for sound hooks, `make_preview.py` builds a visual review grid, and `make_print.py` produces `print.html` for an exact per-leaf PDF. The default runtime adds responsive sizing, page turns, touch, mouse, buttons, and keyboard controls, page-bound spine shadows, ambient motion (ken-burns, particles, twinkling stars, warm bokeh, chapter motifs), a background-music toggle, and a page-flip sound — without rebuilding the artwork in HTML.

## Use it in Codex

Attach a folder of photographs and ask:

```text
Use $create-photo-flipbook-ui to curate these photographs into a coherent photo book.
Choose the visual direction, use only the strongest images, and build the final HTML flipbook.
```

Ask for the advanced story treatment:

```text
Use $create-photo-flipbook-ui to make a memory book from these photos:
add a story timeline with dates, places, and ages, background music and page-flip
sound, gentle animations, and export both the HTML flipbook and a PDF.
```

If the inputs are already finished pages and should not be edited, say so explicitly:

```text
Use $create-photo-flipbook-ui to assemble these finished pages as-is.
Do not edit, crop, reorder, or redesign them.
```

## Install from GitHub

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo HaichaoLihc/create-photo-flipbook-ui \
  --path skills/create-photo-flipbook-ui \
  --ref main
```

After a tagged release, replace `main` with a version such as `v0.2.0`.

## Repository layout

- `skills/create-photo-flipbook-ui/`: installable Codex skill and reusable HTML runtime
  - `assets/html/`: flipbook runtime (template, styles, flipbook.js, book-extra.js, vendored page-flip library, contract test)
  - `references/`: book-editing method, photo-skill catalog, and the default card design system (tokens, motifs, motion, sound, PDF)
  - `scripts/`: contact sheet, metadata-driven book builder, preview grid, and print/PDF builder
- `examples/vanilla-html-book/`: dependency-free HTML reference implementation
- `examples/metadata.sample.json`: documented metadata schema for the advanced path
- `docs/images/`: README workflow and result examples
- `evals/cases/`: blinded forward-eval inputs
- `evals/rubrics/`: grader-only scoring rubrics
- `evals/run_eval.py`: isolated Codex eval runner
- `tests/`: repository-level structural checks

The installed skill excludes examples, evals, and repository documentation so Codex only loads the resources needed for the task. The example uses a null Sites project ID so it cannot accidentally target production deployment.

## Validate

```bash
python3 tests/validate_repo.py
node --test examples/vanilla-html-book/test.mjs
node --test skills/create-photo-flipbook-ui/assets/html/html-contract.test.mjs
```

Build the sample book end to end (replace `<treated-photos>` with a directory of
treated photos named `t-01.jpg`, `t-02.jpg`, …):

```bash
python3 skills/create-photo-flipbook-ui/scripts/build_book.py \
  --runtime skills/create-photo-flipbook-ui/assets/html \
  --metadata examples/metadata.sample.json \
  --photos <treated-photos> --out book
```

Preview or run a forward eval:

```bash
python3 evals/run_eval.py hawaii-v1 --dry-run
python3 evals/run_eval.py hawaii-v1
```

See `evals/README.md` for the isolation and grading workflow.

## License

MIT — see [LICENSE](LICENSE).
