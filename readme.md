# Course: heka22 - Ecological Economics

This course was given in VT26 at Department of Geography, Lund University at the Bachelor level.

Author: Jonas Kreutzer

## Repo Structure

- `lectures/` -- Lecture note chapters (Quarto book)
- `slides/` -- RevealJS presentation sources
- `_extensions/` -- Shared Quarto theme extension (`pjk_theme`)
- `assets/` -- Images and other static files
- `assignments/` -- Course assignments
- `docs/` -- Rendered output (GitHub Pages)

## Building the Site

The project uses [Quarto profiles](https://quarto.org/docs/projects/profiles.html) to render the book and slides separately, since book projects only render chapter files.

```bash
./build.sh
```

This runs two render passes:

1. `quarto render --profile book` -- Renders the lecture notes as a Quarto book to `docs/`
2. `quarto render --profile slides` -- Renders all slide decks as standalone RevealJS HTML to `docs/slides/`

To preview the book locally:

```bash
quarto preview --profile book
```

## Configuration

| File | Purpose |
|------|---------|
| `_quarto.yml` | Shared base config (bibliography) |
| `_quarto-book.yml` | Book profile (chapters, HTML format) |
| `_quarto-slides.yml` | Slides profile (RevealJS format) |

## Embedding Slides

Slides are embedded in lecture notes using a custom shortcode:

```markdown
{{< slides lecture-1 >}}
```

This renders an iframe pointing to the corresponding slide deck in `docs/slides/`.