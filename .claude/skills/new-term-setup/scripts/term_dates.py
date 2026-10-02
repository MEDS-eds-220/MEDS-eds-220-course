"""Print the CLASS DATES and DEADLINES blocks of _variables.yml for a new term.

Everything is computed from the Monday of week 0, with the course's standing rules:
- lectures on Tuesday and Thursday, discussion section on Friday;
- homework released every other Friday from week 1, due 11:59 pm on the following
  week's Saturday, logistics questions until 5 pm the day before the due date,
  resubmission on the Saturday one week after the due date;
- Thanksgiving (4th Thursday of November) cancels Thursday class and Friday section.

Final project dates and the entry/exit surveys are printed as SUGGESTIONS based on
the Fall 2026 pattern. Confirm them against the new calendar and syllabus.

Usage: python .claude/skills/new-term-setup/scripts/term_dates.py 2027-09-20
"""
import datetime as dt
import sys

SHORT = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec"]


def long(d):
    return f"{d:%A}, {d:%B} {d.day}"


def short(d):
    return f"{SHORT[d.month - 1]} {d.day}"


def week_range(mon, last_day=6):
    end = mon + dt.timedelta(days=last_day)
    if end.month == mon.month:
        return f"{short(mon)} - {end.day}"
    return f"{short(mon)} - {short(end)}"


def thanksgiving(year):
    nov1 = dt.date(year, 11, 1)
    first_thu = nov1 + dt.timedelta(days=(3 - nov1.weekday()) % 7)
    return first_thu + dt.timedelta(weeks=3)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    mon0 = dt.date.fromisoformat(sys.argv[1])
    if mon0.weekday() != 0:
        sys.exit(f"{mon0} is a {mon0:%A}, not a Monday")
    tg = thanksgiving(mon0.year)
    day = lambda w, d: mon0 + dt.timedelta(weeks=w, days=d)  # d: 0=Mon ... 5=Sat

    print("# ---------------------------------------")
    print("# CLASS DATES")
    print("# Lectures on Tuesday and Thursday, discussion section on Friday.\n")
    for w in range(11):
        print(f"# Week {w}")
        if w == 0:
            print(f"week0-monday: '{long(mon0)}'      # start of the term: the course calendar counts weeks from here")
        print(f"week{w}-range: '{week_range(day(w, 0))}'")
        for name, d in [("tuesday", 1), ("thursday", 3), ("friday", 4)]:
            if w == 0 and name == "tuesday":
                continue  # no class on Tuesday of week 0
            date = day(w, d)
            note = ""
            if w == 0 and name == "thursday":
                note = "   # setup session (no class on Tuesday)"
            if date in (tg, tg + dt.timedelta(days=1)):
                note = "   # no class - Thanksgiving"
            print(f"week{w}-{name}: '{long(date)}'{note}")
        print()
    print("# Finals week")
    print(f"finals-week-range: '{week_range(day(11, 0), last_day=4)}'\n")

    print("# ---------------------------------------")
    print("# DEADLINES")
    print("# Homework is released on Friday and due at 11:59 pm on the following week's Saturday.")
    print("# Logistics questions are answered until 5 pm on the day before the due date.\n")
    print(f"entry-survey-due: '{long(day(0, 3))}'   # SUGGESTION: Thursday of week 0\n")
    for n in range(1, 5):
        release = day(1 + 2 * (n - 1), 4)
        due = release + dt.timedelta(days=8)
        print(f"hwk{n}-release: '{long(release)}'")
        print(f"hwk{n}-questions-deadline: '{long(due - dt.timedelta(days=1))}'")
        print(f"hwk{n}-due: '{long(due)}'")
        print(f"hwk{n}-resubmission: '{long(due + dt.timedelta(days=7))}'\n")
    print("# SUGGESTIONS from the Fall 2026 pattern: check every one against the calendar and syllabus")
    print(f"final-project-instructions-available: '{long(day(9, 0))}'")
    print(f"final-blog-post-due: '{long(day(10, 2))}'")
    print(f"final-repo-due: '{long(day(10, 5))}'")
    print(f"final-feedback-date: '{long(day(11, 1))}'")
    print(f"final-resubmission-due: '{long(day(11, 4))}'")
    print("final-resubmission-time: '5 pm'")
    print(f"exit-survey-due: '{long(day(11, 4))}'")
    print(f"last-day-of-quarter: '{long(day(11, 4))}'")
    tg_week = (tg - mon0).days // 7
    print(f"\n# Thanksgiving is {long(tg)} (week {tg_week}).")


if __name__ == "__main__":
    main()
