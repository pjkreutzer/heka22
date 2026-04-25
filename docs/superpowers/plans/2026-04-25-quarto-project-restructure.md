# Quarto Project Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the heka22 repo into a single root-level Quarto Book project with slides rendered as standalone RevealJS and embedded in lecture notes via iframes.

**Architecture:** Single `_quarto.yml` at root defines a book project. Lecture notes are chapters under `lectures/`. Slides live under `slides/` with a `_metadata.yml` setting their format to RevealJS. A custom Lua shortcode embeds slides as iframes. Everything renders with one `quarto render` command and outputs to `docs/`.

**Tech Stack:** Quarto (book project), RevealJS, Lua (shortcode), pjk_theme extension

**Spec:** `docs/superpowers/specs/2026-04-25-quarto-project-architecture-design.md`

---

### Task 1: Move lecture notes files to new locations

Move files out of `lecture_notes/` to the root and `lectures/` directory.

**Files:**
- Move: `lecture_notes/index.qmd` -> `index.qmd`
- Move: `lecture_notes/references.qmd` -> `references.qmd`
- Move: `lecture_notes/lecture-1.qmd` through `lecture-8.qmd` -> `lectures/`
- Delete: `lecture_notes/_quarto.yml`
- Merge: `lecture_notes/.gitignore` into root `.gitignore`

- [ ] **Step 1: Create the `lectures/` directory**

```bash
mkdir -p lectures
```

- [ ] **Step 2: Move lecture chapter files**

```bash
mv lecture_notes/lecture-1.qmd lectures/
mv lecture_notes/lecture-2.qmd lectures/
mv lecture_notes/lecture-3.qmd lectures/
mv lecture_notes/lecture-4.qmd lectures/
mv lecture_notes/lecture-5.qmd lectures/
mv lecture_notes/lecture-6.qmd lectures/
mv lecture_notes/lecture-7.qmd lectures/
mv lecture_notes/lecture-8.qmd lectures/
```

- [ ] **Step 3: Move `index.qmd` and `references.qmd` to root**

```bash
mv lecture_notes/index.qmd index.qmd
mv lecture_notes/references.qmd references.qmd
```

- [ ] **Step 4: Merge `.gitignore` and remove `lecture_notes/`**

The root `.gitignore` already contains `/.quarto/` and `**/*.quarto_ipynb` (the only entries in `lecture_notes/.gitignore`). No merge needed — just remove the file and the now-empty directory.

```bash
rm lecture_notes/.gitignore
rm lecture_notes/_quarto.yml
rmdir lecture_notes
```

If `lecture_notes/` has hidden files like `.DS_Store`, remove those first:

```bash
rm -f lecture_notes/.DS_Store
rmdir lecture_notes
```

- [ ] **Step 5: Commit**

```bash
git add -A lectures/ index.qmd references.qmd
git rm -r lecture_notes/
git commit -m "Move lecture notes: lecture_notes/ -> lectures/, index/references to root"
```

---

### Task 2: Move presentations to `slides/`

**Files:**
- Move: `presentations/*.qmd` -> `slides/`
- Delete: `presentations/` directory

- [ ] **Step 1: Create `slides/` and move files**

```bash
mkdir -p slides
mv presentations/introduction.qmd slides/
mv presentations/lecture-1.qmd slides/
mv presentations/lecture-2.qmd slides/
mv presentations/lecture-3.qmd slides/
mv presentations/lecture-4.qmd slides/
mv presentations/lecture-5.qmd slides/
mv presentations/lecture-6.qmd slides/
mv presentations/lecture-7.qmd slides/
mv presentations/lecture-8.qmd slides/
```

- [ ] **Step 2: Remove old directory**

```bash
rm -f presentations/.DS_Store
rm -f presentations/lecture-1.html
rmdir presentations
```

Note: `presentations/lecture-1.html` is a rendered artifact listed in git status; remove it if present.

- [ ] **Step 3: Commit**

```bash
git add -A slides/
git rm -r presentations/
git commit -m "Move presentations/ -> slides/"
```

---

### Task 3: Create root `_quarto.yml` and `slides/_metadata.yml`

**Files:**
- Create: `_quarto.yml`
- Create: `slides/_metadata.yml`

- [ ] **Step 1: Create root `_quarto.yml`**

Write this file at the project root:

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

- [ ] **Step 2: Create `slides/_metadata.yml`**

This sets the default format for all `.qmd` files in the `slides/` directory:

```yaml
format:
  pjk_theme-revealjs:
    embed-resources: true
```

- [ ] **Step 3: Remove per-file `format:` blocks from slide files**

Since `slides/_metadata.yml` now provides the format, remove the `format:` block from each slide's YAML header. Each slide currently has:

```yaml
format:
    pjk_theme-revealjs:
        embed-resources: true
```

After removal, for example `slides/introduction.qmd` becomes:

```yaml
---
title: Introduction to Ecological Economics
subtitle: HEKA22
author: Jonas Kreutzer
date: 2026-04-29
---
```

And `slides/lecture-1.qmd` becomes:

```yaml
---
title: Introduction to Ecological Economics
subtitle: HEKA22
author: Jonas Kreutzer
date: 2026-04-29
---
```

Repeat for all 9 slide files (`introduction.qmd`, `lecture-1.qmd` through `lecture-8.qmd`).

- [ ] **Step 4: Commit**

```bash
git add _quarto.yml slides/_metadata.yml slides/*.qmd
git commit -m "Add root _quarto.yml and slides/_metadata.yml for unified project"
```

---

### Task 4: Update `.gitignore` for new structure

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Update `.gitignore`**

The current `.gitignore` has `presentations/*.html` which no longer applies. Update it for the new structure.

Current relevant line:
```
presentations/*.html
```

Replace with:
```
slides/*.html
```

- [ ] **Step 2: Commit**

```bash
git add .gitignore
git commit -m "Update .gitignore for slides/ directory"
```

---

### Task 5: Fix asset paths in slide files

**Files:**
- Modify: `slides/introduction.qmd`

- [ ] **Step 1: Update asset path in `slides/introduction.qmd`**

The file currently references:
```markdown
![](../assets/the_economy_stupid.png)
```

Since `slides/` is one level down from root (same depth as the old `presentations/`), this path is still correct (`../assets/` resolves to the root `assets/`). No change needed.

Verify no other slides reference assets:

```bash
grep -r "../assets\|../materials\|../assignments" slides/
```

Expected: only the one hit in `introduction.qmd`, which is already correct.

- [ ] **Step 2: Commit (skip if no changes)**

No commit needed if no paths changed.

---

### Task 6: Create the `slides` shortcode

**Files:**
- Create: `_extensions/pjkreutzer/pjk_theme/_shortcodes/slides.lua`
- Modify: `_extensions/pjkreutzer/pjk_theme/_extension.yml`

- [ ] **Step 1: Create the shortcode Lua file**

Create the directory and file `_extensions/pjkreutzer/pjk_theme/_shortcodes/slides.lua`:

```lua
-- Shortcode to embed a RevealJS slide deck as an iframe.
-- Usage: {{< slides lecture-1 >}}
-- Renders: an iframe pointing to slides/<name>.html wrapped in responsive CSS classes.

return {
  ["slides"] = function(args)
    local name = pandoc.utils.stringify(args[1])
    local html = '<div class="responsive-container">\n'
      .. '  <iframe class="responsive-iframe" src="../slides/'
      .. name
      .. '.html" allowfullscreen></iframe>\n'
      .. '</div>'
    return pandoc.RawInline("html", html)
  end
}
```

Note: the path uses `../slides/` because lecture pages render to `docs/lectures/lecture-X.html`, so they need to go up one directory to reach `docs/slides/`.

- [ ] **Step 2: Register the shortcode in `_extension.yml`**

Current `_extension.yml`:

```yaml
title: pjk_theme
author: Philipp Jonas Kreutzer
version: 2.0.0
quarto-required: ">=1.3.0"
contributes:
  formats:
    revealjs:
      brand: _brand.yml
      theme: [defaults.scss, revealjs.scss]
      center: true
    html:
      brand: _brand.yml
      theme: [litera, defaults.scss, html.scss]
```

Add the `shortcodes` key under `contributes`:

```yaml
title: pjk_theme
author: Philipp Jonas Kreutzer
version: 2.0.0
quarto-required: ">=1.3.0"
contributes:
  shortcodes:
    - _shortcodes/slides.lua
  formats:
    revealjs:
      brand: _brand.yml
      theme: [defaults.scss, revealjs.scss]
      center: true
    html:
      brand: _brand.yml
      theme: [litera, defaults.scss, html.scss]
```

- [ ] **Step 3: Commit**

```bash
git add _extensions/pjkreutzer/pjk_theme/_shortcodes/slides.lua
git add _extensions/pjkreutzer/pjk_theme/_extension.yml
git commit -m "Add slides shortcode to pjk_theme extension"
```

---

### Task 7: Update lecture notes to use the shortcode

**Files:**
- Modify: `lectures/lecture-1.qmd` through `lectures/lecture-8.qmd`

- [ ] **Step 1: Replace slide links with shortcode in all lecture files**

Each lecture file currently has a section like:

```markdown
## Slides

The slides for this lecture are available [here](../presentations/lecture-X.html).
```

Replace with:

```markdown
## Slides

{{< slides lecture-X >}}
```

Files to update (with the correct slide name for each):

| File | Shortcode |
|------|-----------|
| `lectures/lecture-1.qmd` | `{{< slides lecture-1 >}}` |
| `lectures/lecture-2.qmd` | `{{< slides lecture-1 >}}` (note: current file points to lecture-1.html — verify if this is intentional or a typo; if typo, use `lecture-2`) |
| `lectures/lecture-3.qmd` | `{{< slides lecture-3 >}}` |
| `lectures/lecture-4.qmd` | `{{< slides lecture-4 >}}` |
| `lectures/lecture-5.qmd` | `{{< slides lecture-5 >}}` |
| `lectures/lecture-6.qmd` | `{{< slides lecture-6 >}}` |
| `lectures/lecture-7.qmd` | `{{< slides lecture-7 >}}` |
| `lectures/lecture-8.qmd` | `{{< slides lecture-8 >}}` |

Note: `lectures/lecture-2.qmd` currently links to `../presentations/lecture-1.html` — this looks like a typo. Ask the user to confirm.

- [ ] **Step 2: Commit**

```bash
git add lectures/*.qmd
git commit -m "Replace slide links with {{< slides >}} shortcode in lecture notes"
```

---

### Task 8: Update `index.qmd` slide links

**Files:**
- Modify: `index.qmd`

- [ ] **Step 1: Update schedule table links**

The schedule table in `index.qmd` currently links to slides with relative paths like:

```markdown
| 1 | Introduction to Ecological Economics | [Slides](../presentations/lecture-1.html) |
```

Since `index.qmd` now renders at the root (`docs/index.html`), update paths to point to `slides/`:

```markdown
| 1 | Introduction to Ecological Economics | [Slides](slides/lecture-1.html) |
|2| Principles of Ecological Economics|[Slides](slides/lecture-2.html)|
|3| History of Economics and Ecology|[Slides](slides/lecture-3.html)|
|4| Raw Materrials and Metabolism|[Slides](slides/lecture-4.html)|
||Redovisning grupparbete||
|5| Doughnut Economics|[Slides](slides/lecture-5.html)|
|6| Barefoot Economics|[Slides](slides/lecture-6.html)|
|7| Eco Feminist Economics|[Slides](slides/lecture-7.html)|
|8| Degrowth|[Slides](slides/lecture-8.html)|
```

- [ ] **Step 2: Commit**

```bash
git add index.qmd
git commit -m "Update slide links in index.qmd for new directory structure"
```

---

### Task 9: Verify the build

- [ ] **Step 1: Clean old output**

```bash
rm -rf docs
rm -rf .quarto
```

- [ ] **Step 2: Render the project**

```bash
quarto render
```

Expected: Quarto renders the book and all slides. Output goes to `docs/`.

- [ ] **Step 3: Verify output structure**

```bash
ls docs/index.html
ls docs/lectures/lecture-1.html
ls docs/slides/lecture-1.html
ls docs/slides/introduction.html
```

All four files should exist.

- [ ] **Step 4: Preview and check iframe embedding**

```bash
quarto preview
```

Navigate to a lecture page (e.g., lecture-1) and verify:
- The slide deck loads in the iframe
- The iframe is styled with the responsive container
- Slides can be navigated within the iframe

If the iframe path is wrong (e.g., slides don't load), the fix is in the shortcode's `src` attribute — adjust the relative path prefix (`../slides/` vs `slides/`).

- [ ] **Step 5: Verify standalone slide rendering**

Open `docs/slides/lecture-1.html` directly in a browser. Confirm it renders as a full standalone RevealJS presentation.

- [ ] **Step 6: Commit rendered output if everything works**

```bash
git add docs/
git commit -m "Render unified book + slides site"
```
