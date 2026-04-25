# Quarto Project Architecture: Unified Book + Slides

## Goal

Restructure the heka22 repository into a single Quarto Book project that serves as the single host for lecture notes and presentation slides. The book is published to GitHub Pages via `docs/`. Slides are rendered as standalone RevealJS HTML files and embedded in lecture note chapters via iframes.

## Current State

- `lecture_notes/` — Quarto Book sub-project with its own `_quarto.yml`, outputs to `../docs`
- `presentations/` — standalone `.qmd` RevealJS files, no project config
- `_extensions/pjkreutzer/pjk_theme/` — custom theme at repo root; provides `pjk_theme-html` and `pjk_theme-revealjs` formats
- Problem: presentations can't find the extension because there's no root-level `_quarto.yml` establishing a project scope

## Design

### Directory Structure

```
heka22/
  _quarto.yml              # single book project config
  _extensions/pjkreutzer/  # theme (unchanged location)
  index.qmd                # book landing page (moved from lecture_notes/)
  references.qmd           # bibliography page (moved from lecture_notes/)
  references.bib           # (unchanged location)
  lectures/                # renamed from lecture_notes/
    lecture-1.qmd
    lecture-2.qmd
    lecture-3.qmd
    lecture-4.qmd
    lecture-5.qmd
    lecture-6.qmd
    lecture-7.qmd
    lecture-8.qmd
  slides/                  # renamed from presentations/
    introduction.qmd
    lecture-1.qmd
    lecture-2.qmd
    lecture-3.qmd
    lecture-4.qmd
    lecture-5.qmd
    lecture-6.qmd
    lecture-7.qmd
    lecture-8.qmd
  assets/                  # unchanged
  assignments/             # unchanged
  materials/               # unchanged
  old_course-materials/    # unchanged, ignored by Quarto
  docs/                    # rendered output
    index.html
    lectures/lecture-1.html
    ...
    slides/introduction.html
    slides/lecture-1.html
    ...
```

### `_quarto.yml`

```yaml
project:
  type: book
  output-dir: docs
  render:
    - "*.qmd"
    - "lectures/*.qmd"
    - "slides/*.qmd"

book:
  title: "Ecological Economics"
  subtitle: "HEKA22---VT26"
  author: Jonas Kreutzer
  date: last-modified
  date-format: long
  chapters:
    - index.qmd
    - part: "Lectures"
      chapters:
        - lectures/lecture-1.qmd
        - lectures/lecture-2.qmd
        - lectures/lecture-3.qmd
        - lectures/lecture-4.qmd
        - lectures/lecture-5.qmd
        - lectures/lecture-6.qmd
        - lectures/lecture-7.qmd
        - lectures/lecture-8.qmd
    - references.qmd

bibliography: references.bib

format:
  pjk_theme-html:
    toc: true
```

A `slides/_metadata.yml` provides directory-level defaults for all slide files:

```yaml
format:
  pjk_theme-revealjs:
    embed-resources: true
```

This means individual slide `.qmd` files no longer need to specify their format — the directory metadata handles it.

Key config decisions:

- **`project: render:`** — Explicitly lists which directories to render. This ensures slide `.qmd` files are rendered (not just copied). The `resources` directive only copies static files and would not render `.qmd` sources.
- **`slides/_metadata.yml`** — Sets the default format for the slides directory to `pjk_theme-revealjs`. Quarto merges directory-level metadata with project-level config, and the more specific directory metadata wins, so slides render as RevealJS even though the project default is HTML.
- **Book navigation** — Only files listed under `book: chapters:` appear in the book TOC. Rendered slide files land in `docs/slides/` but are not part of the book navigation.
- **Single render** — `quarto render` builds both the book and all slides in one pass.

### Slides Shortcode

A `slides` shortcode is added to the existing `_extensions/pjkreutzer/pjk_theme/` extension.

**File:** `_extensions/pjkreutzer/pjk_theme/_shortcodes/slides.html`

**Registration in `_extension.yml`:**

```yaml
contributes:
  shortcodes:
    - _shortcodes/slides.html
  formats:
    revealjs:
      ...
    html:
      ...
```

**Shortcode template** (Lua-based shortcode handler or simple HTML template accessing the first positional argument):

The shortcode takes one positional argument — the slide filename without extension — and wraps it in the existing `.responsive-container` / `.responsive-iframe` CSS classes from `html.scss`. The exact implementation (Lua filter vs HTML template) will be determined during implementation, but the generated output is:

**Usage in lecture notes:**

```markdown
## Slides

{{< slides lecture-1 >}}
```

**Generated HTML:**

```html
<div class="responsive-container">
  <iframe class="responsive-iframe" src="slides/lecture-1.html" allowfullscreen></iframe>
</div>
```

The relative path `slides/lecture-1.html` resolves correctly: from `docs/lectures/lecture-1.html` up to `docs/`, then into `docs/slides/lecture-1.html`. Note: the actual path resolution may need `../slides/lecture-1.html` since lecture pages render under `docs/lectures/`. This will be verified during implementation.

### Existing CSS (no changes needed)

From `_extensions/pjkreutzer/pjk_theme/html.scss`:

```scss
.responsive-container {
    position: relative;
    width: 100%;
    padding-bottom: 5%;
}

.responsive-iframe {
    position: relative;
    top: 0;
    left: 0;
    width: 100%;
    height: 500px;
}
```

### File Moves

| From | To |
|------|----|
| `lecture_notes/index.qmd` | `index.qmd` |
| `lecture_notes/references.qmd` | `references.qmd` |
| `lecture_notes/lecture-*.qmd` | `lectures/lecture-*.qmd` |
| `presentations/*.qmd` | `slides/*.qmd` |
| `lecture_notes/_quarto.yml` | deleted (replaced by root `_quarto.yml`) |
| `lecture_notes/.gitignore` | `.gitignore` (merge if needed) |
| (new) | `slides/_metadata.yml` (directory-level format defaults) |

### What Stays Unchanged

- `_extensions/pjkreutzer/pjk_theme/` — location unchanged, just adds shortcode
- `assets/`, `assignments/`, `materials/` — unchanged
- `old_course-materials/` — unchanged, ignored
- `references.bib` — already at root
- `.gitignore` at root — already exists

### Update Paths in Content

- Lecture notes: update slide links from `../presentations/lecture-X.html` to use `{{< slides lecture-X >}}` shortcode
- `index.qmd`: update schedule table slide links from `../presentations/` to `slides/`
- Slide `.qmd` files: check for any relative paths to `assets/` or other resources and adjust for new location (`slides/` → root is `../`)

## Out of Scope

- Deployment pipeline / GitHub Actions (manual `quarto render` + push to `docs/` for now)
- Changes to slide content
- Changes to lecture note content beyond path updates
- Changes to the RevealJS theme or HTML theme styling
