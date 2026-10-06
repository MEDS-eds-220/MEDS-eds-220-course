---
name: lesson-audit
description: Audit one EDS 220 lesson, discussion section, or assignment for incorrect or outdated content. Reports corrections (errors, bugs, broken code) separately from newer best practices and teaching gaps. Use when the instructor asks whether a lesson is outdated, incorrect, or needs updating.
argument-hint: <path to a lesson .qmd, e.g. book/chapters/lesson-4-plotting-pandas.qmd>
---

# Lesson audit

Audit this file: $ARGUMENTS

If no path was given, ask which lesson to audit. If the file links to or depends on other material (a homework question, an in-class notebook, a dataset), check those parts too, but keep the report focused on this file.

## Ground rules

- **Read-only by default.** Report findings and don't edit anything until the instructor asks. When asked to fix something, change only what was approved and list every change afterwards, including small typo or wording fixes.
- **Never create, modify or delete files outside this repository.** Run code only as snippets through stdin, not as saved scripts.
- **Don't render.** `quarto render` rewrites `docs/` and `_freeze/`. Leave rendering to the instructor.
- Read the **whole file**, not excerpts, before reporting.

## Context the audit needs

**The course.** EDS 220 (UCSB MEDS) is a Quarto site. Lessons are in `book/chapters/`, discussion sections in `discussion-sections/`, and assignments in `assignments/`. The homework notebooks live in the GitHub repos `MEDS-eds-220/eds220-hwk1`, `-hwk2` and `-hwk3`, which may already be cloned in `_planning/hwk-repos/`. The instructor's live-coding notebooks are in `MEDS-eds-220/in-class-notebooks`.

**The students.** Most are Python beginners. Many first coded in the summer EDS 217 bootcamp, and they often mix up R and Python syntax. EDS 217 (2026) covered the following, so treat it as review, not new material:
- pandas basics, boolean masks, `.isin`, `groupby().agg`, `merge`, `concat`, `pivot_table`, `to_datetime` with `.dt`, and `.str` methods;
- the pyplot state-machine interface and seaborn;
- functions with docstrings;
- its own pattern names: "filter pattern", "top-N pattern", "split-apply-combine".

EDS 217 did **not** cover `.iloc`, method chaining (it explicitly avoided it), `lambda`, `fig, ax`, `resample`/`rolling`, or anything geospatial. Its editor was Positron. The entrance survey (in `_planning/`, gitignored, never quote it) shows the students most want to write code from scratch.

**The environment.** Read `eds220-env.yml` each time. As of Fall 2026 it pinned a 2023 stack (numpy 1.24, which keeps pandas on 2.x; geopandas 0.14; python 3.11). For every finding, say whether it affects students **now** or only **after the environment is updated**.

**Earlier findings.** If `_planning/code-currency-audit.html` exists, read it first. It is a full-course audit from September 2026. Reuse its findings for this file, but check that each one is still present (line numbers shift, and some items are fixed). Don't report items that are already fixed.

**The instructor's style choices.** Don't flag these:
- bare `#### Example` headings;
- the order of topics;
- the choice of dataset, unless it's a data-quality or availability problem.

## What to check

1. **Correctness.** Look for:
   - statements that are false, including domain terms (for example, species richness vs abundance, CRS and projection claims, units);
   - code that errors or silently gives wrong results;
   - explanations of output that the code doesn't actually produce;
   - broken links or data URLs;
   - inconsistencies with other lessons;
   - solutions or answers hidden inside `<!-- -->` comments. Quarto copies HTML comments into the published page, so students can read them with "view source". Suggest moving them to a solutions notebook in `_planning/` (for example `_planning/dsN-test.ipynb`).
2. **Currency of methods.** Look for deprecated or removed APIs and changed defaults. Known changes to look for (verify them, don't assume):
   - **pandas 3:** Copy-on-Write is the default, so chained assignment never updates and `SettingWithCopyWarning` is gone; text columns get the `str` dtype, not `object`; datetimes default to microseconds; frequency aliases changed (`'ME'`, `'YE'`, `'h'`); `stack()` keeps NaN.
   - **numpy 2:** scalars print as `np.int64(...)`; removed aliases such as `np.NaN`; stricter dtype promotion (`np.select` with string choices and `default=np.nan` raises).
   - **geopandas 1.x:** pyogrio is the default I/O engine; `unary_union` is replaced by `union_all()`; `sjoin(op=)` is replaced by `predicate=`.
   - **xarray:** `.drop()` is replaced by `drop_vars`/`drop_sel`; `to_array` is replaced by `to_dataarray`.
   - **matplotlib 3.9+:** removed `cm.get_cmap`.
   - **pystac-client:** current method names.
3. **Newer, widely accepted practices.** Only include a practice that the library's own documentation recommends, or that is clearly standard in current data science work. Don't include personal preferences or trends. Examples: `pathlib`, `np.random.default_rng`, `.loc` assignment, GeoParquet, lazy loading with `chunks=`, `.explore()`. Say why it matters for beginners, and roughly what it would cost to adopt.
4. **Term-specific values that should come from `_variables.yml`.** Dates, deadlines, teaching-team names, rooms and links to Google Docs, Sheets, Slides, Drive folders or forms must never be hard-coded in a page (see `CLAUDE.md`). Look for:
   - hard-coded dates (weekday and month names, `M/D` patterns), even inside callouts and tables;
   - teaching-team names, including past TAs (for example "come see Annie or Carmen");
   - `docs.google.com`, `drive.google.com` and `forms.gle` links outside HTML comments;
   - the past term or year (for example "Fall 2025").

   For each one, name the variable to use (from `_variables.yml`) or propose a new one. Wrong values, such as an old date, a past TA or a weekday that doesn't match its date, go under **Corrections**. Values that are correct but hard-coded go under **Minor**. Also check that each `{{< var >}}` key used in the file exists in `_variables.yml`.
5. **Teaching gaps for this cohort.** Look for:
   - missing explanations of the errors beginners actually hit (for example, `and`/`or` on a Series);
   - places that clash with what EDS 217 taught;
   - homework questions that depend on something the lesson doesn't teach.

## How to verify

- **Test library-behaviour claims when you can.** `/opt/anaconda3/bin/python3` has pandas 2.2 and numpy 2.x. You can simulate pandas 3 with `pd.set_option('future.infer_string', True)` and `pd.set_option('mode.copy_on_write', True)`. Lesson data may exist locally in gitignored `data/` folders.
- **Check the current official documentation or release notes** (pandas "What's new", numpy release notes, the geopandas, xarray and rioxarray changelogs, matplotlib API changes) whenever web access is available. Cite the page. If you can't check, say that the finding is based on your knowledge up to a stated date.
- **Tag every finding** with how it was checked:
  - **Tested**: you ran code;
  - **In file**: you read the line;
  - **Docs**: you checked the current documentation;
  - **Not verified**: from knowledge only, so the instructor should check before acting.

## Report format

Reply in chat (no HTML file unless asked), in this order:

1. **Verdict.** Two or three sentences: is the lesson current and correct overall, and what matters most.
2. **Corrections.** Things that are wrong or broken: false statements, bugs, code that fails or gives wrong results, dead links. For each: what, where, why, fix, tag, and **Now** or **After env update**.
3. **Outdated methods and newer practices.** Keep this separate from corrections. For each: the old way, the current way, a source, whether adopting it is urgent or optional, and the tag.
4. **Worth adding for this cohort.** At most three items, each tied to a concrete student error or homework question.
5. **Minor.** Typos, inconsistent wording, redundant sentences. Keep it short.

**Re-audits.** When this file was already audited earlier in the conversation, add one line after the verdict listing what has been fixed since the last audit. Don't re-flag suggestions the instructor has decided against. If such an item is still worth a mention, list it once under a "still open, skip if decided" note.

Number the items in sections 2–5 with one continuous sequence (for example, if Corrections ends at 3, Outdated methods starts at 4), so the instructor can ask for fixes by number. Don't number the section headings, and don't restart the count in each section.

Reference locations as clickable markdown links relative to the repo root, for example `[line 42](book/chapters/lesson-3-pandas-subsetting/lesson-3-pandas-subsetting.qmd#L42)`. Leave out empty sections. End by offering to make specific fixes, and don't make them until asked.
