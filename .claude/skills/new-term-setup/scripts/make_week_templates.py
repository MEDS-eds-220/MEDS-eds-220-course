"""Create the weekly page templates (week 0-10 and finals week) for a new term.

Run it AFTER _variables.yml has the new term's dates. Templates call the date variables
({{< var weekN-tuesday >}} etc.), so they never contain hard-coded dates. Assignment
"available" and "due" callouts, the Thanksgiving week and the final project deadlines
are placed in the right week by reading the dates in _variables.yml.

Usage (from the repo root, with the eds220-env conda env active):
    python .claude/skills/new-term-setup/scripts/make_week_templates.py 2027 [--plan plan.yml] [--out DIR]

plan.yml (optional) holds the planned topics from the class calendar, added to each page
as an HTML comment:
    2: {tuesday: 'Updating dataframes', thursday: 'Building conda environment', friday: 'Handling string data'}

Refuses to overwrite existing files.
"""
import argparse
import datetime as dt
import pathlib
import sys

import yaml

MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July",
                                      "August", "September", "October", "November", "December"], 1)}
FINALS = 11
V = lambda k: "{{< var " + k + " >}}"

# Assignment pages linked from the "due" callouts. Assignment 4 has two versions.
ASSIGNMENT_PAGES = {1: "assignment1", 2: "assignment2", 3: "assignment3", 4: "assignment4-palisades-eaton-fires"}


def parse(value, year):
    _, rest = value.split(", ")
    month, day = rest.split()
    return dt.date(year, MONTHS[month], int(day))


def week_of(variables, key, mon0, year):
    return (parse(variables[key], year) - mon0).days // 7


def prep(key):
    return f"::: {{.callout-warning icon=false}}\n## Preparation for next class ({V(key)})\n\n1. \n:::\n"


def class_block(n, key):
    return f"## Class {n} ({V(key)})\n\n1. \n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("year", type=int)
    ap.add_argument("--plan")
    ap.add_argument("--out")
    args = ap.parse_args()

    root = pathlib.Path.cwd()
    variables = yaml.safe_load((root / "_variables.yml").read_text())
    plan = yaml.safe_load(pathlib.Path(args.plan).read_text()) if args.plan else {}
    out = pathlib.Path(args.out) if args.out else root / "week-by-week" / "weekly-descriptions"
    mon0 = parse(variables["week0-monday"], args.year)
    wk = lambda key: week_of(variables, key, mon0, args.year)

    release = {wk(f"hwk{n}-release"): n for n in range(1, 5)}
    due = {wk(f"hwk{n}-due"): n for n in range(1, 5)}
    final_week = wk("final-repo-due")

    # No class on days that fall on Thanksgiving (4th Thursday of November) or the day after
    nov1 = dt.date(args.year, 11, 1)
    tg = nov1 + dt.timedelta(days=(3 - nov1.weekday()) % 7, weeks=3)
    no_class = {tg, tg + dt.timedelta(days=1)}
    is_off = lambda key: parse(variables[key], args.year) in no_class

    pages = {}
    class_n = 1
    for w in range(11):
        p = plan.get(w, {}) or {}
        s = [f"# Week {w} : {V(f'week{w}-range')}\n"]
        if p:
            topics = " | ".join(f"{d.capitalize()} - {p[d]}" for d in ("tuesday", "thursday", "friday") if p.get(d))
            s.append(f"<!-- Planned (class calendar): {topics} -->\n")
        if w in due:
            n = due[w]
            s.append(f"::: {{.callout-important icon=false}}\n## Assignment {n} due this Saturday\n\n"
                     f"[Assignment {n}](/assignments/{ASSIGNMENT_PAGES[n]}.qmd) is due by 11:59 pm on {V(f'hwk{n}-due')}. "
                     f"Logistics questions will be answered until 5 pm on {V(f'hwk{n}-questions-deadline')}.\n:::\n")
        days = [d for d in ("tuesday", "thursday") if f"week{w}-{d}" in variables and not is_off(f"week{w}-{d}")]
        if w == 0:
            # Week 0: Thursday setup session, then the first class on Friday
            days = []
            s.append(f"## Setup session ({V('week0-thursday')})\n\n1. \n\n<br>\n")
            s.append(f"## Class 1 ({V('week0-friday')})\n\n1. \n")
            s.append(prep("week1-tuesday"))
            class_n = 2
        for d in days:
            s.append(class_block(class_n, f"week{w}-{d}"))
            nxt = f"week{w}-thursday" if d == "tuesday" and "thursday" in days else f"week{w + 1}-tuesday"
            if w < 10 or d == "tuesday":
                s.append(prep(nxt))
            if d == days[-1] and w in release:
                n = release[w]
                s.append(f"\n::: {{.callout-tip icon=false}}\n## Assignment {n} available this Friday\n\n"
                         f"Assignment {n} will be available by the end of {V(f'hwk{n}-release')} and will be due by "
                         f"11:59 pm on {V(f'hwk{n}-due')}.\n:::\n")
            s.append("\n<br>\n")
            class_n += 1
        fri = f"week{w}-friday"
        if w > 0 and fri in variables and not is_off(fri):
            s.append(f"\n## Discussion section ({V(fri)})\n\n::: {{.callout-warning icon=false}}\n"
                     "## Preparation for discussion section\n\n- \n:::\n\n<br>\n")
        off = [k for k in (f"week{w}-thursday", fri) if k in variables and is_off(k)]
        if off:
            s.append(f"\n## No class on {' and '.join(V(k) for k in off)}\n\nHappy Thanksgiving! 🦃\n\n<br>\n")
        if w == final_week:
            s.append(f"\n::: {{.callout-important icon=false}}\n## Final project deadlines\n\n"
                     f"- Task 1 (blog post) is due by 11:59 pm on {V('final-blog-post-due')}.\n"
                     f"- Task 2 (GitHub repo) is due by 11:59 pm on {V('final-repo-due')}.\n\n"
                     "See the [final project instructions](/assignments/final-project.qmd) for details.\n:::\n\n<br>\n")
        pages[f"week-{w}-{args.year}.qmd"] = "\n".join(s)

    pages[f"finals-week-{args.year}.qmd"] = (
        f"# Finals week : {V('finals-week-range')}\n\n"
        f"::: {{.callout-important icon=false}}\n## Final project resubmission\n\n"
        f"- Feedback for both final project tasks will be available by {V('final-feedback-date')}.\n"
        f"- The final resubmission for both tasks is due by {V('final-resubmission-time')} on "
        f"{V('final-resubmission-due')} (last day of the quarter).\n\n"
        "See the [final project instructions](/assignments/final-project.qmd) for details.\n:::\n\n<br>\n")

    existing = [n for n in pages if (out / n).exists()]
    if existing:
        sys.exit(f"Refusing to overwrite: {', '.join(existing)}")
    out.mkdir(parents=True, exist_ok=True)
    for name, text in pages.items():
        (out / name).write_text(text)
    print(f"Wrote {len(pages)} templates to {out}")
    print(f"Thanksgiving: {tg:%A, %B} {tg.day}. Homework released in weeks {sorted(release)}, "
          f"due in weeks {sorted(due)}; final project deadlines in week {final_week}.")


if __name__ == "__main__":
    main()
