---
name: write-readme
description: Write or update a README.md for an EDS 220 repository (the course website or another course repo such as an assignment template, the in-class or discussion-sections repo, or shared notebooks). Use when the user asks to create, rewrite or add a section to a README.
argument-hint: <optional: path to the repo, or what the README is for>
---

# Write a README

Write a README for someone who lands on the repository on GitHub: a student, a future TA, or an instructor at another school who wants to reuse the materials. It should tell them what the repo is, how to use it, how to contribute and who made it.

## 1. Gather facts before writing

Read before writing anything. Don't guess any fact you can look up.

- **Existing README:** read it first. If it has real content, keep the user's wording and structure and only add or fix what was asked. Overwrite it only if it is a placeholder (e.g. just the repo name).
- **What the repo is:** for the course website, take the course description from `_course-description.qmd` and paraphrase it lightly. For other repos, read the files in it and the course pages that link to it (`grep -rn "<repo-name>" --include='*.qmd' --exclude-dir=docs .`).
- **Exact names:** copy repository, folder, environment and file names exactly as the course pages spell them (e.g. `eds220-in-class`, `eds220-discussion-sections`, `eds220-env`). If the pages disagree, use the spelling on the setup page and point out the mismatch to the user.
- **Links:** the course website URL, course listing and teaching-team GitHub profiles are in `_variables.yml`. Get the remote URL with `git remote -v`.
- **People:** `_variables.yml` (current team), the archived `week-by-week/week-by-week-YYYY.qmd` files (past team members, read only) and `git log --format='%an %ae' | sort -u`. If you can't find someone's GitHub profile, ask. Don't build a URL from their name.
- **License:** the website footer in `_quarto.yml` (course materials are CC BY-NC 4.0), or a `LICENSE` file in the repo.

## 2. Structure

Use the sections that apply, in this order. Skip any that would be empty.

1. **Title**: `# EDS 220 - Working with Environmental Datasets`, or the repo's purpose for other repos (e.g. `# EDS 220 in-class notebooks`).
2. **Summary**: one or two sentences on what the repo is and how it fits the course, followed by a link to the course website.
3. **Repository layout**: a table (`| Path | Contents |`) or a file tree in a plain ``` code fence. In trees, use `├──`, `└──` and `│`, give every folder a trailing `/` and leave no lines that are only whitespace.
4. **Setup / usage**: the commands someone needs, in a `bash` block with a short comment on each step. For the website: conda env, `quarto preview`, `quarto render`, and the note that local `data/` folders are gitignored. For student repos: how to clone it and which environment or kernel to use, linking to the right `setup/` page on the course website rather than repeating it.
5. **Publishing**: website repo only. GitHub Pages serves `docs/` from `main`, so commit `docs/` and `_freeze/` with the source change.
6. **Contributing**: reuse the "Contribute" text from `index.qmd` (email the instructor or file an issue, and the 🌟 star note), with the repo's own issues link. For repos that accept outside changes, add short numbered pull request steps: fork and branch, edit, check, commit following `commits-guidelines.qmd`, open a PR.
7. **Authors**: "These course materials were developed by [Name](GitHub profile), with contributions from [Name](GitHub profile)." Confirm the list with the user if anyone besides the instructor is involved.
8. **License**: one line with a link.

## 3. Style

- Follow `conventions.qmd`: headings in sentence case, American spelling.
- Write for an outside reader. Leave out internal maintenance rules (how `_variables.yml` works, never editing the archives, navbar edits). Those live in `CLAUDE.md` and `conventions.qmd`. Link to them instead.
- Don't put anything in the README that changes each term: dates, the term name, current TA names, student hours, room numbers or Google Docs links. Shortcodes like `{{< var >}}` don't work in a README.
- Keep it short. A reader should get the gist in a minute.
- Use relative links for files in the repo (`[conventions](conventions.qmd)`) and full URLs for everything else.
- Never mention EDS 217 in the README.

## 4. Check

- Every relative link points to a file that exists, and every command matches the repo (env file name, render settings).
- For the website repo, confirm `README.md` won't be rendered as a site page: `_quarto.yml`'s `render:` list should only include `*.qmd` and `*.ipynb`.
- Don't commit.

## 5. Report

Start with one line naming the audience as you understood it. Then list:

- the sections you wrote or changed,
- facts you looked up and where you found them (e.g. a GitHub profile found in the git log),
- anything you weren't sure about or that the user may want to change, and inconsistencies you found in other files but didn't fix.
