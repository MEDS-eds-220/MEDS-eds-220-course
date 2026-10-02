"""Archive the current term's weekly pages into one frozen week-by-week-YYYY.qmd file.

Every {{< var key >}} shortcode is replaced by its current value from _variables.yml,
so the archive keeps this term's dates and names after _variables.yml is updated.

Usage (from the repo root, with the eds220-env conda env active):
    python .claude/skills/new-term-setup/scripts/archive_weeks.py 2026 [--out PATH]

Without --out it writes week-by-week/week-by-week-YYYY.qmd and refuses to overwrite it.
"""
import argparse
import pathlib
import re
import sys

import yaml

VAR = re.compile(r"\{\{<\s*var\s+([\w-]+)\s*>\}\}")
HEADING = re.compile(r"^(#{1,6})(\s.*)$")
FENCE = re.compile(r"^\s*(```|~~~)")
CALLOUT = re.compile(r"^:{3,}\s*\{\s*\.callout")
WEEK_HEADING = re.compile(r"^#{1,6}\s+(Week \d+|Finals week)\s*:\s*(.*)$")
# Links and images with relative paths break when the text moves to week-by-week/
RELATIVE_LINK = re.compile(r"\]\((?!/|https?:|mailto:|#|\{\{)([^)]+)\)")


def week_files(folder, year):
    files = sorted(folder.glob(f"week-*-{year}.qmd"), key=lambda p: int(p.name.split("-")[1]))
    finals = folder / f"finals-week-{year}.qmd"
    return files + ([finals] if finals.exists() else [])


def resolve(text, variables, source):
    def sub(m):
        key = m.group(1)
        if key not in variables:
            sys.exit(f"{source}: unknown variable '{key}'")
        return str(variables[key])
    return VAR.sub(sub, text)


def demote(lines, target=3):
    """Shift headings outside code blocks so the shallowest one becomes level `target`.

    Callout titles (the first heading inside a ::: callout) are ignored when finding the
    shallowest level, since Quarto uses them as titles whatever their level.
    """
    in_code, levels, prev = False, [], ""
    for line in lines:
        if FENCE.match(line):
            in_code = not in_code
        elif not in_code and (m := HEADING.match(line)) and not CALLOUT.match(prev):
            levels.append(len(m.group(1)))
        if line.strip():
            prev = line
    if not levels:
        return lines
    shift = max(0, target - min(levels))
    out, in_code = [], False
    for line in lines:
        if FENCE.match(line):
            in_code = not in_code
        elif not in_code and (m := HEADING.match(line)):
            line = "#" * min(6, len(m.group(1)) + shift) + m.group(2)
        out.append(line)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("year")
    ap.add_argument("--out")
    args = ap.parse_args()

    root = pathlib.Path.cwd()
    variables = yaml.safe_load((root / "_variables.yml").read_text())
    files = week_files(root / "week-by-week" / "weekly-descriptions", args.year)
    if not files:
        sys.exit(f"No week-*-{args.year}.qmd files found")
    out = pathlib.Path(args.out) if args.out else root / "week-by-week" / f"week-by-week-{args.year}.qmd"
    if out.exists() and not args.out:
        sys.exit(f"{out} already exists. Archives are frozen, so it will not be overwritten.")

    parts = [
        "# Week by week\n",
        ':::{style="color:red;" .center-text}\n<p style="text-align: center;">\n'
        f"**THIS IS THE {args.year} WEEK BY WEEK- IT IS FOR INSTRUCTOR REFERENCE ONLY**\n</p>\n:::\n",
        "You will find the course announcements and daily activities here.\n",
    ]
    warnings = []
    for f in files:
        text = resolve(f.read_text(), variables, f.name)
        lines = text.splitlines()
        # The page's own "Week N : dates" heading becomes the archive section heading
        idx = next((i for i, l in enumerate(lines) if WEEK_HEADING.match(l)), None)
        if idx is None:
            sys.exit(f"{f.name}: no 'Week N : dates' heading found")
        name, dates = WEEK_HEADING.match(lines[idx]).groups()
        body = demote(lines[:idx] + lines[idx + 1:])
        body_text = "\n".join(body).strip()
        for m in RELATIVE_LINK.finditer(body_text):
            warnings.append(f"{f.name}: relative link or image '{m.group(1)}' may break in the archive")
        parts.append(
            f"## {name} : {dates}\n"
            '::::{.callout-note appearance="minimal" collapse="true" }\n'
            "## What happened\n\n"
            f"{body_text}\n\n"
            "::::\n\n<br>\n"
        )
    out.write_text("\n".join(parts))
    print(f"Wrote {out} from {len(files)} weekly pages: {', '.join(f.name for f in files)}")
    for w in warnings:
        print("WARNING:", w)


if __name__ == "__main__":
    main()
