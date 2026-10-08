---
name: mark-reviewed
description: Mark one EDS 220 document as done in the review tracker (_planning/review-tracker.md and .html) after its typo fixes and/or audit have been incorporated, and refresh its notes on remaining updates. Use when the instructor says a lesson, discussion section, assignment or page has finished fix-typos and/or lesson-audit.
argument-hint: <document (e.g. "L6: time series", "DS2", path)> [typos | audit | both (default)]
---

# Mark a document as reviewed

Update the review tracker for one document once the instructor has incorporated the `/fix-typos` changes, the relevant `/lesson-audit` findings, or both.

The tracker is `_planning/review-tracker.md` (the source) and `_planning/review-tracker.html` (generated from it, what the instructor reads). `_planning/` is gitignored, so never commit these files.

## 1. Find the row

- The argument can be a site lesson name or number ("L6: time series", "time series"), a discussion section ("DS2", "water crisis"), an assignment, a setup page or a path.
- Lesson numbers follow the **site titles**, not the file names (e.g. `lesson-7-time-series.qmd` is "L6: time series"). Each row lists the file name in parentheses, so match on either.
- If the argument matches no row or more than one, ask before continuing. If the document is missing from the tracker, add a row in the right table, in sidebar order.
- Always refer to lessons as "L#: topic" when talking to the instructor, never bare "L#".

## 2. Decide which columns to mark

- Default is **both** "Typos" and "Audit". If the instructor names only one ("typos done", "audit done"), mark only that one.
- Set the column(s) to ✅. Never change a ✅ back to ⬜ unless asked.
- ✅ means the changes were incorporated, not just that the skill was run. Don't check this against the git history: the instructor's word is enough.

## 3. Refresh the notes

The notes column lists only **what is still open** for that document. Read the document (the whole `.qmd`) and:

- Remove notes for items that are now fixed. Check each listed item against the file (e.g. a TODO that's gone, a link that's updated, a deprecated call that's replaced).
- Keep items that are still present, and update their line numbers if they moved.
- Add any remaining `TODO` markers (including inside `<!-- -->`), `**CHECK HERE**` review markers, and anything the instructor said is deferred.
- Keep notes about future changes, marked in bold, e.g. **pandas 3:** …. Check `_planning/code-currency-audit.html` section 3 for pandas 3 / numpy 2 / geopandas 1 items that apply to this document, and add any that are missing.
- If nothing is left, leave the notes cell empty.
- Keep notes short: one or two sentences per item, with line numbers where they help.

Also update the "Last updated" date near the top to today's date.

## 4. Regenerate the HTML

Run from the repo root:

```bash
quarto pandoc _planning/review-tracker.md -s --embed-resources \
  --css .claude/skills/mark-reviewed/tracker.css \
  --metadata pagetitle="Fall 2026 review tracker" \
  -o _planning/review-tracker.html
```

Use `pagetitle` (not `title`) so the heading isn't duplicated. Check that the command ran without errors and that the HTML contains the updated row.

## 5. Report

In a few lines, tell the instructor:
- which columns were marked for which document,
- which notes were removed as fixed, and which remain or were added,
- the link to [_planning/review-tracker.html](_planning/review-tracker.html).
