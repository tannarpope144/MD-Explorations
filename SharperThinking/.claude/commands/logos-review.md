---
description: List entries with their status — no quiz, just overview
---

# /logos-review

You are giving the user a tabular overview of their Logos corpus.

**User input:** $ARGUMENTS

## Supported filters

- `--unactivated` — entries whose `activated:` is blank.
- `--tag <tag>` — entries whose `tags` array contains `<tag>` exactly.
- `--stale [days]` — activated entries not drilled in the last `days` days (default 30). "Not drilled" means no line in `log/attempts.jsonl` for that slug, or the most recent line is older than the threshold.
- `--struggling` — activated entries whose most recent log line has verdict `needs work`.

Filters can be combined (logical AND).

## What to show

1. **Scan `entries/`** and read frontmatter for every `.md` file.
2. **Apply filters.**
3. **Compute last-drilled info** for each entry from `log/attempts.jsonl` (if it exists).
4. **Render a table** in markdown:

| Name | Type | Tags | Activated | Last drilled | Last verdict |
|---|---|---|---|---|---|
| Second-Order Thinking | framework | decision-making, systems | 2026-05-28 | 2026-05-28 (college) | passed |
| Steelmanning | term | argumentation | — | — | — |

- For `Activated`: show the date, or `—` if blank.
- For `Last drilled`: show `YYYY-MM-DD (tier)`, or `—` if never.
- For `Last verdict`: show the verdict string, or `—` if never drilled.
- Sort by `Name` alphabetically unless a filter implies a more useful sort (e.g., `--stale` sorts oldest-first).

5. **Below the table**, give a one-line summary: "N entries total (M activated, K unactivated)."

## Hard rules

- Never modify entries or the log. This command is read-only.
- If `entries/` is empty, say so and suggest `/logos-capture`.
- If a frontmatter field is malformed, fail loudly with the file path. Do not silently skip.
