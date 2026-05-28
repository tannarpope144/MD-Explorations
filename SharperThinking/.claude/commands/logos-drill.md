---
description: Pick an activated entry (weighted toward least-recently drilled) and quiz the user
---

# /logos-drill

You are picking an entry for the user to drill, then handing off to the quiz flow.

**User input:** $ARGUMENTS

Expected format: `[tier] [--tag <tag>]` — both optional. Tier is `college`, `graduate`, or `doctorate`.

## Selection logic

1. **List all files in `entries/`** (exclude `.gitkeep`). For each, read the frontmatter.

2. **Filter to activated entries only.** An entry is activated iff its `activated:` field has a date value (not blank).

3. **Apply tag filter if provided.** If the user passed `--tag <tag>`, keep only entries whose `tags` array contains `<tag>` exactly.

4. **Handle empty result:**
   - If there are no entries on disk at all → tell the user: "No entries yet. Capture one with `/logos-capture`."
   - If there are entries but none activated → tell the user how many unactivated entries exist and suggest `/logos-review --unactivated`.
   - If a tag filter eliminated everything → tell the user no activated entries match that tag.

5. **Compute weights from `log/attempts.jsonl`** (if the file exists):
   - For each candidate slug, find the most recent log line where `entry == slug`. Note its date.
   - Entries that have NEVER appeared in the log are treated as maximally stale (highest weight).
   - Older drills → higher weight. Newer drills → lower weight.
   - A simple weighting that works: `weight = days_since_last_drill + 1`, with never-drilled entries assigned a weight equal to the max observed `days_since_last_drill + 100` (so they're strongly preferred but not the only choice).

6. **Pick one entry** via weighted random selection.

## Handoff

1. Tell the user which entry was picked and why ("haven't drilled this in 12 days" or "never drilled before"). One line.

2. Then **delegate to the quiz flow** by behaving exactly as if `/logos-quiz <picked-slug> <tier>` had been invoked. If no tier was provided, default to `graduate` (since activated entries are always at least at college level).

## Hard rules

- Never pick an unactivated entry.
- Never quiz on an entry that doesn't exist on disk.
- If `log/attempts.jsonl` is missing or empty, all activated entries are "never drilled" and get equal max weight.
