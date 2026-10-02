---
name: new-term-setup
description: Roll the EDS 220 website over to a new term. Archives the past term's week-by-week pages, updates _variables.yml (dates, deadlines, teaching team, rooms, links, weekly topics, calendar), creates the new weekly templates, finds term-specific content that variables don't cover, re-renders and reports. Use when the instructor asks to set up the site for a new year or term.
argument-hint: <new year, e.g. 2027>
---

# New term setup

Set up the course website for the new term: $ARGUMENTS

Most term-specific content lives in `_variables.yml` (see `CLAUDE.md`). This skill updates that file and everything around it. Work through the steps in order, and keep a running list of every change and every value you had to guess, for the final report.

## Ground rules

- **Don't guess dates, names or links.** Take them from the new class calendar and syllabus, or ask. When something has to be inferred, for example from last year's pattern, mark it `# CHECK` in `_variables.yml` and list it in the report.
- **Never edit an existing archive** (`week-by-week/week-by-week-YYYY.qmd`). Create the new one; don't touch the old ones.
- **Stay inside the repository.** Put scratch files (plans, previews) in the session scratchpad or in the gitignored `_planning/`.
- **Don't commit.** Leave that to the instructor.
- **Check for a running preview** (`ps aux | grep "[q]uarto.*preview"`) before rendering. If the instructor has one running, tell them that renders may collide with it. Never start a `quarto preview` yourself.
- The scripts need PyYAML: run them from the repo root after `source "$(conda info --base)/etc/profile.d/conda.sh" && conda activate eds220-env`.

## 1. Gather the inputs

Before changing anything, collect these (look in `_planning/` first, and ask for what's missing):

1. **The new term and year**, and the **Monday of week 0**.
2. **The new class calendar** (a CSV export in `_planning/`, named like `EDS 220 Class Calendar YYYY ...`). It has the weekly topics and the deadlines. **Check its dates against the year.** The 2026 file's column headers still had 2025 dates, so its weekdays were off by one. If the dates and weekdays don't match, line up each row by weekday and tell the instructor.
3. **The new syllabus** (a PDF in `_planning/`, or ask). It is the source of truth for dates when materials disagree (the instructor confirmed this in Fall 2026). Read the whole thing. Its hyperlink targets can be extracted from the raw PDF with a `/URI` regex over the decompressed streams. The Google Doc version usually can't be fetched.
4. **The teaching team**: names, pronouns, emails, websites, GitHub links, student hours, best way to contact. Also class and section times and rooms.
5. **New links** for anything recreated each term (see step 4).

Show the instructor a short summary of what you found and what's missing, and wait for answers before step 3.

## 2. Archive the past term

1. Check that the past term's weekly pages (`week-by-week/weekly-descriptions/*-YYYY.qmd`) are final. Ask if any look unfilled.
2. **Run the archive script before changing `_variables.yml`.** It replaces every `{{< var >}}` with its current value, so the archive keeps the past term's dates:
   ```bash
   python .claude/skills/new-term-setup/scripts/archive_weeks.py <past year>
   ```
   It writes `week-by-week/week-by-week-<past year>.qmd` in the same format as earlier archives: a collapsed "What happened" section per week. It refuses to overwrite an existing archive. Fix any relative links it warns about.
3. Add the archive to `week-by-week/previous-years.qmd`, following the existing lines.
4. In `_quarto.yml`, empty the "week by week" navbar menu down to "past years". Variables don't work in `_quarto.yml`, so this is a manual edit.
5. Ask before deleting the past term's weekly pages. They stay in git history, and their rendered `docs/` HTML should go with them.

## 3. Update `_variables.yml`

Go section by section and keep the file's structure and comments.

- **Class dates and deadlines.** Generate them from the Monday of week 0:
  ```bash
  python .claude/skills/new-term-setup/scripts/term_dates.py YYYY-MM-DD
  ```
  It prints the CLASS DATES and DEADLINES blocks using the course's standing rules: homework released every other Friday from week 1, due the next week's Saturday, resubmission one week later, and Thanksgiving off. Compare every value with the calendar and syllabus, and use the syllabus where they differ. The final project and survey dates it prints are only suggestions from the 2026 pattern.
- **General**: `term`, `course-listing` and `syllabus-google-doc` if it changed; class and section times and rooms.
- **Teaching team**: every `instructor-*` and `ta-*` key. `ta-name` is the TA's first name, used in sentences like "come see {TA} or {instructor}".
- **Weekly topics**: `week0-topic` to `finals-week-topic`, from the calendar.
- **Workshops**: the MEDS Career & Professional Development workshop links and live-session dates, from the syllabus.
- **`calendar-events`**: check that each event still applies, and add or remove events to match the syllabus. Events only point to date variables, so most years need no change here.

Write every date as `'Weekday, Month D'`. The course calendar checks each weekday against its date when rendering.

## 4. Links that change every term

Go through the URL variables and ask about each one that is usually recreated: `entry-survey`, `github-repos-spreadsheet`, `discussion-teams-spreadsheet`, `presentation-dates-spreadsheet`, `syllabus-google-doc`, and the workshop links. Rubrics, notes, slides and shared folders usually stay the same, but list them so the instructor can confirm. If a new link isn't available yet, keep the old one, add `# CHECK: last year's link` and list it in the report.

## 5. Create the weekly templates

1. Optionally write a plan file in the scratchpad from the calendar's topics (format in the script's docstring), so each page gets its planned topics as a comment.
2. Run:
   ```bash
   python .claude/skills/new-term-setup/scripts/make_week_templates.py <new year> --plan <plan.yml>
   ```
   It writes `week-N-YYYY.qmd` (weeks 0-10) and `finals-week-YYYY.qmd` to `week-by-week/weekly-descriptions/`. Class numbers run on from Class 1 on the Friday of week 0. The assignment, Thanksgiving and final project callouts land in the right weeks from the dates in `_variables.yml`, so run it after step 3.
3. Don't add the templates to the navbar. The instructor adds each week when it is ready.

## 6. Sweep for content that variables don't cover

Search the non-archive pages (exclude `docs/`, `_freeze/`, `_planning/` and `week-by-week/week-by-week-*.qmd`) for:

- the past year and term name, e.g. `2026`, `Fall 2026` (for example the note in `discussion-sections/discussion-sections-listing.qmd`);
- past teaching-team names (e.g. `grep -rn "Fatiq\|Annie"`);
- hard-coded dates (weekday and month names, `M/D` patterns) and Google links (`docs.google.com`, `drive.google.com`, `forms.gle`).

Turn anything term-specific into a variable. Report, but don't change, what variables can't reach: `_quarto.yml`, HTML comments, images such as `slides/images/fatiq.jpg` in the syllabus slides, and the homework repos.

## 7. Render and check

```bash
quarto render
```

- Every `WARNING (course-calendar)` line is a date whose weekday doesn't match. Fix each one in `_variables.yml`.
- Check that no shortcode is left unresolved: `grep -rl "{{&lt; var" docs/` should print nothing.
- Spot-check the new values in `docs/index.html` (calendar), `docs/syllabus.html` (homework and portfolio tables) and one assignment page.

## 8. Report

Group the report into:

1. **Archived**: the new archive file, the `previous-years.qmd` link, the navbar change, and any deleted pages.
2. **Updated in `_variables.yml`**: a short summary per section, not every key.
3. **Needs checking**: every `# CHECK` value and every disagreement between the calendar, the syllabus and last year's pattern, each with the value you used.
4. **Not covered by variables**: everything from step 6 left for the instructor.
5. **Render**: whether it was clean, and any warnings.

End with what is left to do by hand, and remind the instructor that nothing was committed.
