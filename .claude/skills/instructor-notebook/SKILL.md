---
name: instructor-notebook
description: Create or revise the instructor notebook for an EDS 220 lesson from the current lesson .qmd and the instructor's notes on scope. Builds it with a script in _planning/, runs it, and writes it to instructor-materials. Use when the instructor asks to make, update, or redo an instructor notebook for a lesson. (Student notebooks have their own skill.)
argument-hint: <lesson, e.g. lesson-14-xarray> [notes on what to include or skip]
---

# Instructor notebook

Lesson and notes: $ARGUMENTS

If no lesson was given, ask for one. The notes on scope are the instructor's decisions:
follow them exactly, and ask only if something in them is ambiguous.

## Where things live (all under ~/Documents/COURSES/EDS_220/)

- Lesson (source of truth): `MEDS-eds-220-course/book/chapters/<lesson>/<lesson>.qmd`
  (or `book/chapters/<lesson>.qmd` for single-file lessons)
- Instructor notebook (output): `instructor-materials/instructor-notebooks/<lesson>-INSTRUCTOR.ipynb`
- Student notebook (where students start): `student-notebooks/<lesson>-STUDENT(S).ipynb`
- Build scripts: `MEDS-eds-220-course/_planning/build-<lesson>-instructor-nb.py` (gitignored).
  Earlier ones (L10, L11, L13, L14, L18) are examples of the pattern.
- Assignments: `MEDS-eds-220-course/assignments/` and `_planning/hwk-repos/`

## Steps

1. **Read everything first:** the whole lesson .qmd, the existing instructor notebook
   (if any), and the student notebook (if any). Note which code cells the student
   notebook already has filled in and where it goes blank.
2. **Check the homework** when the notes mention it: grep the assignments for the
   functions/methods students will need, and make sure the notebook covers them.
3. **Write the build script** in `_planning/`, modeled on
   `build-lesson-14-instructor-nb.py`: cells built with nbformat, executed with nbclient,
   written straight to `instructor-materials/instructor-notebooks/`. Use the markers
   below even where an older script uses different ones.
4. **Content rules:**
   - Simplified text: short sentences and bullets, not the lesson's full prose. Keep the
     lesson's code, section order and headings (only the first letter capitalized).
   - Start with the title, a link to the lesson on the course site, and learning
     objectives cut down to the notebook's scope.
   - Drop anything the notes say is covered elsewhere (e.g. slides); leave an all-caps
     cue where to switch, e.g. `GO OVER THE NETCDF SLIDES FIRST`.
   - Topics the notes say to "only mention": a table or one sentence, no code.
   - Short all-caps cues for classroom flow: `STUDENTS START TYPING HERE`,
     `EMPTY NOTEBOOK FOR STUDENTS STARTS HERE`, `SHOW DIAGRAM ON SLIDES`.
   - Images: use the published URL
     (`https://meds-eds-220.github.io/MEDS-eds-220-course/book/images/<lesson-n>/...`),
     not `/book/...` paths, so they show up in Jupyter.
   - Long helper code (e.g. maps) → a talking point pointing to the course website.

## Markers

- **Code students already have** starts with the comment `# THIS IS PRE-FILLED FOR STUDENTS`.
  In a cell that mixes both, mark each part separately: `# THIS IS PRE-FILLED FOR STUDENTS`
  above the pre-filled part and `# STUDENTS TYPE THIS` above the rest.
  Unmarked code = students type it.
- **Talking points** (things the instructor says out loud, check-in answers, data quirks,
  links to homework) go in markdown between `---` rules with this header:

  ```
  ---

  THIS IS BLANK FOR STUDENTS

  <talking points>

  ---
  ```

  In the build script, use a `blank(text)` helper that returns this block.

## Run and report

5. **Run it** with `/opt/anaconda3/envs/test-eds220-env/bin/python`, from the course repo
   root, with a run folder in the scratchpad (create it first) or the lesson folder if it
   needs local `data/`. Pass the run folder as an argument. Confirm every code cell has
   outputs and no errors.
6. **Report:** what's in the notebook section by section, what was dropped or only
   mentioned, how it ran, any differences between the student notebook's pre-filled code
   and the instructor notebook (don't fix them here: that's the student notebook skill),
   and anything odd in the repos (e.g. unrelated uncommitted changes). Don't commit
   unless asked.

## Ground rules

- The lesson .qmd is the source of truth. Never edit it from this skill.
- Don't edit the student notebook from this skill.
- Don't render the course site.
- Leave unrelated changes in any repo alone, but mention them.
