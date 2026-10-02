# EDS 220 - Working with Environmental Datasets

Source for the course website of **EDS 220 - Working with Environmental Datasets**, part of the Master of Environmental Data Science (MEDS) program at the Bren School, UC Santa Barbara ([course listing](https://bren.ucsb.edu/courses/eds-220)).

**Course website:** <https://meds-eds-220.github.io/MEDS-eds-220-course/>

This hands-on course explores widely used environmental data formats and Python libraries for analyzing environmental data, working with open data repositories and cloud platforms to source and analyze real-world datasets. It also serves as an introduction to Python programming. The website holds the lecture notes, discussion sections, assignments, setup tutorials, syllabus and a week-by-week schedule.

## Repository layout

| Path | Contents |
|---|---|
| `index.qmd`, `syllabus.qmd` | Home page and syllabus |
| `book/` | Lecture notes (the "notes" section of the site) |
| `discussion-sections/` | Published discussion sections |
| `assignments/` | Homework assignments and final project |
| `setup/` | Setup tutorials for students (conda, VS Code, Jupyter kernel, GitHub PAT) |
| `slides/` | Revealjs slides |
| `week-by-week/` | Weekly pages for the current term and archives of past years |
| `_variables.yml` | Term dates, deadlines, teaching team info and external links |
| `_quarto.yml` | Site configuration: navbar, sidebar, theme, bibliography |
| `references/` | Shared bibliography (`references.bib`) and IEEE citation style |
| `shortcodes/` | Custom Quarto shortcodes (the course calendar) |
| `docs/` | Rendered website, served by GitHub Pages |
| `_freeze/` | Cached code-cell outputs |

## Building the site locally

You need [Quarto](https://quarto.org/docs/get-started/) and [conda](https://docs.conda.io/).

```bash
# Create and activate the Python environment used to run the code cells
conda env create -f eds220-env.yml
conda activate eds220-env

# Live preview while editing
quarto preview

# Render the full site into docs/
quarto render

# Render a single page
quarto render path/to/file.qmd
```

Code results are cached in `_freeze/` (`freeze: auto`), so a page's Python only re-runs when its source changes.

**Data:** `data/` folders are gitignored. Some lessons read data from local `data/` folders next to the lesson, so those pages can't be re-executed from a fresh clone without first downloading the data. Their cached outputs in `_freeze/` still let the rest of the site render.

## Publishing

The site is published with GitHub Pages from the `docs/` folder on `main`. After changing a page, render it and commit the source together with the updated `docs/` and `_freeze/` files.


## Contributing

📝 If you have suggestions on how to correct, improve, or expand these course materials, please email the course instructor at c_galazgarcia@ucsb.edu or [file a GitHub issue](https://github.com/MEDS-eds-220/MEDS-eds-220-course/issues).

To suggest a specific change, you can also open a pull request:

1. Fork this repository and create a new branch.
2. Edit the source `.qmd` file(s), following [`conventions.qmd`](conventions.qmd).
3. Render the pages you changed (`quarto render path/to/file.qmd`) and check that they look right.
4. Commit your changes following [`commits-guidelines.qmd`](commits-guidelines.qmd) and [open a pull request](https://github.com/MEDS-eds-220/MEDS-eds-220-course/pulls) describing what you changed and why.

🌟 If these materials have been useful to you, consider adding a star to this repository!

## Authors

These course materials were developed by [Carmen Galaz García](https://github.com/carmengg), with contributions from [Annie Adams](https://github.com/annieradams).

## License

Course materials are licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).
