---
name: fix-typos
description: Fix typos, grammar slips and small factual inconsistencies in one EDS 220 lesson (or other course page), re-render it, and report every change. Use when the user asks to fix typos in a specific lesson or page.
argument-hint: <lesson number, lesson name, or path to a .qmd file>
---

# Fix typos in a lesson

Proofread a single course page and fix mistakes without changing its teaching content or voice.

## 1. Find the file

- The argument can be a path, a lesson number ("lesson 5", "5") or part of a name ("groupby", "basic plotting").
- Resolve it against `book/chapters/` and the `book` sidebar in `_quarto.yml`. Lessons are either `book/chapters/lesson-N-name.qmd` or `book/chapters/lesson-N-name/lesson-N-name.qmd`.
- If the argument matches more than one file, or none, ask before continuing.
- Never edit archived schedules (`week-by-week/week-by-week-YYYY.qmd`).

## 2. Read the whole file

Read every line, including YAML, callouts, code comments, figure captions, and content inside `<!-- -->` comments. Finish reading before making any edits.

## 3. What to fix

**Always fix:**
- Misspellings (e.g. occured, intersted, parenthesis → parentheses when plural).
- British spellings: the course uses American spelling throughout, so change them (e.g. behaviour → behavior, colour → color, visualise → visualize, analyse → analyze). Leave code, function and parameter names, quoted titles and proper nouns as they are.
- Doubled or missing words ("the the", "That is the  we just used"). When a missing word must be guessed, pick the obvious one and flag it in the report.
- Grammar: subject-verb agreement, it's/its, your/you, missing articles, comma splices that make a sentence hard to read.
- Double spaces inside sentences.
- Misplaced Markdown or code formatting (e.g. `` `and value_counts()` `` → ``and `value_counts()` ``, an unclosed quote in inline code, a Python block labelled ``` R).
- Broken links with an empty target (`[text]()`), when the right target is obvious from the text.

**Also fix, but list separately in the report (they change what students read):**
- Prose that contradicts the code next to it: a wrong parameter name (`subset` vs `subplots`), a wrong variable (`pd.count` vs `df.count`), a comment whose number doesn't match the code (`head(3)` described as "first five rows", `>1996` above `>2020`).
- Off-by-one wording about positions vs indices ("the 8th column" for `iloc[:, 8]`).
- Terms that go against the lesson's own vocabulary (e.g. "location-based" when the lesson says "position-based"; calling a method an "operator").
- Titles of external resources that are misquoted.

**Match course conventions (from `conventions.qmd` and CLAUDE.md):**
- "data frame" in prose (not "dataframe"), except in code and in names like `pandas.DataFrame`.
- Learning objectives introduced by "By the end of this lesson, students will be able to:".
- Section headings in sentence case.

**Do not change:**
- Headings like `# 3 Basic plotting`: the number is intentional lesson numbering.
- The author's voice, informal tone, emoji, or sentence structure when it is already correct.
- Explanations, examples, exercises or code logic, beyond the inconsistencies above.
- Other files, even if the same typo appears there (mention it instead).

**Commented-out code cells:** Quarto executes ```{python} cells even inside `<!-- -->`, so fix anything in them that would stop the page from rendering (e.g. stray leading indentation). Fix plain typos there too.

## 4. Apply the edits

- Use exact, unique string replacements (Edit tool, or a short Python script that asserts each old string occurs exactly once). Don't use regex rewrites across the whole file.
- Don't reflow lines or reformat code.

## 5. Re-render

```bash
source "$(conda info --base)/etc/profile.d/conda.sh" && conda activate eds220-env
quarto render <path/to/file.qmd>
```

- If rendering fails, read the error. If a pre-existing problem in the file causes it, fix it only if it is small and obvious (and report it). Otherwise stop and tell the user.
- If the page reads local data (`data/` next to the lesson) and it's missing, don't render. Say so.
- Check `git status`. If the render deleted files under `docs/`, confirm the new HTML doesn't reference them (they should be stale orphans) and say so.
- Note output that changed for reasons other than your edits (e.g. random numbers from `np.random`).
- Do not commit. Don't touch unrelated modified files in the working tree.

## 6. Report

Group the changes:

1. **Spelling**: a compact list, `wrong → right` (British-to-American changes included).
2. **Grammar and wording**: short before → after pairs.
3. **Changes to what the lesson says, which you may want to check**: each change that affects meaning, code references or instructions, with a one-line reason.
4. **Left alone**: anything you noticed but didn't change, and why (unclear intent, issues in other files).

End with whether the page rendered cleanly and that nothing was committed.
