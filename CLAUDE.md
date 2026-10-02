# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Course website for EDS 220 (Working with Environmental Datasets, UCSB MEDS). It is a Quarto website with Python content, published through GitHub Pages from the committed `docs/` folder.

## Commands

```bash
quarto preview                      # live-reload local preview of the whole site
quarto render                       # render the full site into docs/
quarto render path/to/file.qmd      # render one page (updates its docs/ output and _freeze/)
conda env create -f eds220-env.yml  # Python env used to execute code cells (eds220-env)
```

There are no tests or linters. To check a change, render the affected page.

## Architecture / build behavior

- `_quarto.yml` controls everything: the navbar, the `book` sidebar (lesson order and sections), the theme and the bibliography. A new lesson, assignment or top-level page must be added to it by hand to show up in navigation. Discussion sections are the exception: `discussion-sections/discussion-sections-listing.qmd` is a Quarto listing that picks them up automatically from their YAML (`week`, `title`, `image`).
- `execute: freeze: auto`: code-cell results are cached in `_freeze/` and re-run only when a source file changes. Commit `_freeze/` and `docs/` with the source change, since the published site is served straight from `docs/`. Re-rendering a page runs its Python, so the conda env and any data it needs must be present.
- Data: `**/data/` is gitignored. Lessons either load data from URLs or read local `data/` folders that sit next to the lesson (for example `book/chapters/lesson-3-pandas-subsetting/data/`). Those local folders are not in the repo, so a fresh clone cannot re-execute those pages. Lessons that have their own data or images live in their own subfolder (`book/chapters/lesson-N-name/lesson-N-name.qmd`). Single-file lessons sit directly in `book/chapters/`.
- Content areas: `book/` (lecture notes, the "notes" navbar item), `discussion-sections/` (published weekly sections), `discussion-sections-upcoming/` (draft notebooks and data prep for future sections), `assignments/`, `setup/` (student setup tutorials), `slides/` (revealjs, styled with `meds-slides-styles.scss`), and `week-by-week/` (see below).
- Week by week: the current term has one page per week in `week-by-week/weekly-descriptions/` (`week-N-YYYY.qmd` for weeks 0-10, plus `finals-week-YYYY.qmd`). Templates for upcoming weeks are created ahead of time with their dates filled in. Each week appears on the site only once it is added by hand to the "week by week" navbar menu in `_quarto.yml`. Past years are archived as single files, `week-by-week/week-by-week-YYYY.qmd`, linked from `previous-years.qmd`. Never edit the archives.
- Central variables: `_variables.yml` holds everything that changes each term or repeats across pages: the term name, teaching-team names, emails and student hours, class dates for every week, assignment and final project deadlines, and URLs to externally hosted documents (Google Docs, Sheets, Slides, Drive folders and forms). Pages call them with `{{< var key >}}`, e.g. `[rubric]({{< var hwk1-rubric >}})` or `due by **11:59 pm on {{< var hwk1-due >}}**`. Never hard-code a date, a teaching-team name or a Google URL in a page; add a variable instead. Shortcodes do not work in `_quarto.yml` or inside HTML comments. After changing `_variables.yml`, re-render the full site so every page picks up the new values.
- Citations: every source (packages, datasets, articles, websites) is cited with `@key` against the single shared `references/references.bib`, in IEEE style (`references/ieee-with-url.csl`).

## Content conventions (from `conventions.qmd`)

- File names are all lowercase with words separated by `-`.
- In section headings, capitalize only the first letter. Example headings follow the form `Example: what this is about {.unlisted}`.
- Lessons use `toc-title: In this lesson` in their YAML and state their learning objectives as "By the end of this lesson, students will be able to:".
- Discussion section YAML:
  ```yaml
  ---
  title: Topic of discussion section
  subtitle: Week n - Discussion section
  week: n
  image: images/ds-weekn.png
  sidebar: false
  ---
  ```
  Body order: a brief intro ending with "In this discussion section, you will:" and a list; Setup and General directions, each in a `:::{.callout-tip appearance="minimal"}` block; "About the data" in a `:::{.callout-note appearance="minimal"}` block; then numbered exercises.

## Commits

Follow `commits-guidelines.qmd`: use the imperative mood, capitalize the summary line and keep it to about 50 characters, and avoid vague messages such as "Fixes" or "Updates".
