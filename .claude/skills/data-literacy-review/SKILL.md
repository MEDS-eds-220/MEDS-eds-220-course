---
name: data-literacy-review
description: Review one EDS 220 lesson, discussion section, or assignment for the data itself rather than the code, so students think critically about the data instead of wrangling along. Raises data pitfalls and provenance issues students should discuss, suggests where to add check-ins and pre-class prep on the data and metadata, turns hidden judgment calls into student decisions, flags code that silently changes the data, and proposes a learning objective and an assessment question. Use when the instructor asks to review a page's data, add data literacy, provenance, pitfalls or "know your data" content, or plan pre-class data prep.
argument-hint: <path to a lesson, discussion section or assignment .qmd>
---

# Data literacy review

Review this file: $ARGUMENTS

If no path was given, ask which page to review. The aim of this review is to move the course from "how to wrangle this data in Python" towards "how to understand, question and trust this data". Python stays the vehicle, and the data becomes the subject.

**The goal is critical thinking, not more information.** The instructor wants students to stop wrangling along and start judging the data themselves. So prefer suggestions where students do the thinking over ones where the page tells them the answer:

- **Discovery over disclosure.** Let students run into a problem (a spike from a fill value, points falling in the ocean, a join that loses rows) before the page explains it. A callout that explains the pitfall upfront is the weakest option. Use it only when discovering it would take too long.
- **Decisions over instructions.** Wherever the page makes a judgment call without saying so, students should make the call and justify it.
- **Open questions.** Good questions have more than one defensible answer and can't be answered by rerunning the code. "What is the CRS?" is a lookup. "Is this CRS a good choice for measuring distances here, and why?" is thinking.

Rate every suggestion by the level of thinking it asks for:
1. **Notice:** spot that something is off.
2. **Explain:** say why it happens, using the metadata.
3. **Decide:** choose how to handle it and justify the choice.
4. **Critique:** judge a claim, plot or analysis, including the lesson's own.

Each page should have at least one **Decide** or **Critique** moment. Notice-only check-ins don't count as critical thinking on their own.

This is a different job from `lesson-audit`, which checks the code and content for correctness. Don't repeat code-currency findings here. If you notice an actual error, mention it in one line and point to `lesson-audit`.

## Ground rules

- **Read-only by default.** Report and don't edit until the instructor asks. When asked to add suggestions to the page, change only the approved items and list every change afterwards. If the instructor wants inserted items marked for review, use the CHECK HERE format: `---` / `**CHECK HERE** (data review item N: short description)` / `---`, with a blank line before and after every `---`.
- **Never create, modify or delete files outside this repository.** Planning notes go in `_planning/` (gitignored). Run code only as snippets through stdin, never as saved scripts.
- **Don't render.** Leave `quarto render` to the instructor.
- Read the **whole file** before reporting, including `<!-- -->` comments and the "About the data" section.
- **Student-facing text** you draft must not mention EDS 217. Refer to other lessons as "L#: topic" (for example "L7: time series"), never as a bare "L7".
- **Hidden answers** in drafted check-ins go in plain ```` ```python ```` fences inside `<!-- -->`, never in `{python}` cells, because commented `{python}` cells still execute. Note that Quarto publishes HTML comments, so students can see them with "view source".

## Step 1: Profile each dataset

For every dataset the page uses (including ones loaded in linked notebooks or homework repos in `_planning/hwk-repos/`):

1. **Find the source.** Follow the links in "About the data" and the `@citation` in `references/references.bib`. When web access is available, open the repository landing page and the metadata (EML on EDI/KNB, the XML or "about" page, the STAC collection and item properties). If you can't reach it, say so.
2. **Answer the data-biography questions** as far as the metadata allows:
   - Who made it, and why (monitoring, regulation, research, a compilation)?
   - How was it collected or produced (instrument, survey, model, classification, reports from the public)?
   - What is one observation (one row, one feature, one pixel)?
   - When and where does it cover, and at what resolution or scale?
   - What are the units, codes and missing-data conventions?
   - Is it a measurement, an estimate, a model output or an index?
   - Which version is it? Was it simplified, derived or pre-processed for the course, and what was lost?
   - What license applies, and how should it be cited?
3. **Inspect the data when you can.** Local copies may exist in gitignored `data/` folders next to the lesson, in `_planning/data/`, or at a URL in the page. Use `/opt/anaconda3/bin/python3` (pandas 2.2, numpy 2.x; geopandas, xarray and rioxarray may need the `eds220-env` conda environment). Look for:
   - shape, dtypes, ranges, and suspicious round or extreme values (likely fill values);
   - NaN counts, and whether "missing" rows are absent or coded;
   - category codes and their frequencies;
   - for spatial data, the CRS, bounds, nodata value, dtype, scale/offset attributes and resolution;
   - row counts before and after the page's joins, clips and filters.

## Step 2: Check against the pitfall catalog

Go through [pitfalls.md](pitfalls.md) for the data types the page uses, and through its "Across all types" section. Report only pitfalls that **actually apply to this data**, with evidence. Don't list generic warnings. A pitfall that applies but is minor can be left out. If you find a pitfall that isn't in the catalog, report it and offer to add it.

## Step 3: Check the course map

If `_planning/data-literacy-map.md` exists, read it. It records which pitfall each page **introduces** and which it **reinforces**. Use it to:
- avoid introducing a pitfall a second time as if it were new (refer back to where students first met it instead);
- prefer pitfalls the course hasn't covered yet;
- notice when this page could reinforce one introduced earlier.

If the map doesn't exist, say so and offer to start it with this page's entries.

## Step 4: Plan critical-thinking moments, check-ins and prep

First, look for places where the page currently does the thinking for students:

- **Pre-empted pitfalls.** The page handles a problem before students can see it (for example `na_values=` set at load, the CRS stated before anyone looks, data already filtered or cleaned for them). Suggest letting students meet the problem first, then fix it.
- **Hidden judgment calls.** The page makes a choice without saying it is a choice: dropping NaN, the join type, a threshold, a resampling frequency, a classification, a projection, which dataset or source to use, a color scale. Suggest turning the most important one into a student decision. Students should state the alternatives, pick one, and give a reason. Where possible, have them compare the results of two choices.
- **Unexamined conclusions.** The page ends with a plot or result and moves on. Suggest asking what the result can and can't support.

Then suggest where students should stop and look at the data. Use the course's existing check-in format:

```markdown
:::{.callout-tip }
## Check-in

...
:::
```

For data background that isn't an exercise, propose a "Know your data" callout. Use `:::{.callout-note}` with a `## Know your data` heading unless the instructor has picked a different style (check the map and earlier pages for one already in use).

Choose from these formats, and fit them to the point in the page where they help most:

- **Pre-class metadata hunt** (5–10 min, before class). Three or four questions answerable from the metadata page: who, how, what one row is, what the missing-data code is. Link to the landing page, not straight to the file.
- **Predict, then run.** Before a load, plot, join or clip, students write down what they expect (row count, range, how the map should look), then compare.
- **Sanity check right after loading.** `head`, `dtypes`, `describe`, NaN counts, unique values; for spatial data also the CRS, bounds, nodata and a quick plot. Ask "what here looks wrong or surprising?"
- **Row count before and after.** At every join, clip, `dropna` or filter.
- **Pause before interpreting.** Before students read meaning into a plot or map: "What could make this pattern appear even if nothing real changed?"
- **Compare sources.** When two sources describe the same thing (two fire perimeters, two boundary sets), have students compare them.
- **Your call.** Students choose how to handle an issue (missing values, a join, a threshold), justify it in a markdown cell, then compare their result with a classmate who chose differently.
- **Spot the flaw.** Show a plausible but flawed plot, claim or code result made from the lesson's own data (an average of fill values, a trend that is really better detection, a map in the wrong CRS). Students find what's wrong and explain how they'd know.
- **What would you need to know?** Before an analysis, students list what they would need to learn about the data to trust the answer, then check what the metadata actually tells them.
- **Write the caveat.** At the end, students write two or three sentences on what their result can and can't support and why. Their audience is someone who will act on the result. This supports the course description's goal of communicating the strengths and weaknesses of data products.

For each suggestion, give the location (a line link), the format, its thinking level (Notice, Explain, Decide or Critique), the time it takes, and a draft of the text. Don't put the answer in the student-facing text. Put the expected answer, or the range of reasonable answers, in a hidden comment for the instructor. Keep the cohort in mind: mostly Python beginners, so check-ins should be short and answerable, and pre-class prep should total 15 minutes or less.

## Step 5: Additional checks

1. **Silent changes.** List the operations in the page's code that change the data without an error: `dropna`, `how='inner'` (the `merge` default), `sjoin` and `clip` dropping features, `astype` truncating, `resample`/`groupby` dropping NaN, reprojection, raster resampling (especially on categorical rasters), and `pd.read_csv` guessing dtypes or turning codes into numbers. For each, suggest the one-line check that would show what happened.
2. **Provenance and citation.** Check that the page cites each dataset with `@key`, links to the original repository and metadata, gives an access date or version where it matters, and says plainly when the course uses a simplified or derived copy. Suggest any new `references.bib` entries in IEEE style.
3. **Data that is too clean to teach with.** If the page uses data where no real pitfall can arise (Palmer penguins, synthetic arrays, data simplified for the course), say so. Suggest one specific real-data alternative or a raw-data variant only if it fits the lesson's goals. Note the cost of switching. This is optional advice, not a correction.
4. **Learning objective.** Draft one data-literacy objective to add to the page's list under "By the end of this lesson, students will be able to:" (for example "identify fill values in a dataset's metadata and exclude them before analysis").
5. **Assessment link.** Draft one homework or reflection question that checks the main pitfall. Check the assignments in `assignments/` and `_planning/hwk-repos/` first so you don't duplicate one that exists (HW1 already covers Datasheets for Datasets).

## Report format

Reply in chat (no HTML file unless asked), in this order:

1. **Data at a glance.** For each dataset, one short data-biography paragraph (the Step 1 answers, gaps marked "not in metadata"). Then one or two sentences on how well the page currently helps students understand this data, and where it does the thinking for them.
2. **Pitfalls to discuss.** The three to five that matter most for this page, most important first. For each: what it is, the evidence from the data or metadata, where it shows up in the page (line link), and a draft discussion question for students. Mark each **introduce** or **reinforce** (see the course map).
3. **Critical-thinking moments.** The pre-empted pitfalls, hidden judgment calls and unexamined conclusions from Step 4, each turned into a student activity with location, thinking level, time and draft text. Put the strongest **Decide** or **Critique** moment first.
4. **Check-ins and pre-class prep.** The remaining placements from Step 4, each with location, format, thinking level, time and draft text.
5. **Silent changes.** From Step 5.1.
6. **Provenance and citation.** From Step 5.2. Leave out if complete.
7. **Objective and assessment.** The draft objective and question from Steps 5.4 and 5.5. The objective and the question should be at the **Decide** or **Critique** level.
8. **Data choice.** From Step 5.3, only if it applies.

Close the report with a one-line **thinking balance** for the page as it would be after the suggestions: how many moments it has at each level. Flag the page if it would still be mostly Notice.

Tag every claim about the data with how you know it:
- **Tested**: you ran code on the data;
- **Metadata**: you read it in the source's metadata or documentation (link it);
- **In file**: you read it in the page;
- **Not verified**: from general knowledge only, so the instructor should check.

Number the items in sections 2–8 with one continuous sequence, so the instructor can ask for changes by number. Reference locations as clickable markdown links relative to the repo root. Leave out empty sections.

End by offering to:
- insert the approved items into the page;
- update `_planning/data-literacy-map.md` with this page's introduced and reinforced pitfalls;
- add any new pitfalls to [pitfalls.md](pitfalls.md).

Don't do any of these until asked.
