---
name: session-review
description: Review the current conversation and recommend what to save in memory, which skills to update, and whether a new skill is worth creating. Read-only; reports a brief assessment and makes no changes. Use when the user asks whether anything from the session should be remembered, added to a skill, or turned into a skill.
argument-hint: <optional focus, e.g. "only skills" or "discussion section 2">
---

# Session review

Look back over this conversation and recommend what is worth keeping. Focus: $ARGUMENTS

## Ground rules

- **Read-only.** Don't write, edit or delete memory files or skills. Report only, and wait for the user to choose items.
- Read before recommending. Check `MEMORY.md` and the memory files it links to, and the skills in `.claude/skills/` (read the `SKILL.md` of any skill you propose to change). That way you update existing entries instead of proposing duplicates.

## What to look for

**Memory** (one fact per file; see the memory instructions in the system prompt):
- corrections or preferences the user stated ("don't do X", "I prefer Y"), with the reason;
- decisions the user settled, so later sessions don't re-suggest them (for example, a lesson keeps a method the audit questioned);
- non-obvious facts about the course, the build or the workflow that cost time to discover;
- existing memories that this session showed to be wrong, incomplete or out of date.

Don't propose saving:
- what the repo already records (code, `CLAUDE.md`, `conventions.qmd`, git history);
- details that only mattered for this conversation;
- anything from the entrance survey or other private planning files.

**Skill updates:**
- a check a skill missed that found a real problem this session;
- report-format changes the user asked for or kept asking for;
- steps the user had to correct, or steps that were done differently from what the skill says.

**New skills.** Propose one only when the task:
- is likely to recur (for example, every discussion section or every term), and
- has steps or conventions that aren't obvious from the repo.

A one-off task, or one already covered by adding a few lines to an existing skill, doesn't need a new skill. Say so.

## Report format

Reply briefly in chat, in three groups: **Memory**, **Skill updates**, **New skills**. Leave out an empty group, or say "nothing" in one line.

- Number the items with one continuous sequence across groups, so the user can pick by number.
- For each item: what to save or change, where (the memory file to create or update, or the skill and section), and one line on why it matters.
- Mark whether it creates something new or updates something that exists.
- End with your recommendation of which items to do, and ask which ones the user wants.
