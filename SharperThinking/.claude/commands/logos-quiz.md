---
description: Quiz the user on a specific entry at a chosen tier (college/graduate/doctorate)
---

# /logos-quiz

You are running a quiz session for the user's Logos system.

**User input:** $ARGUMENTS

Expected format: `<entry-slug> [tier]` where tier is `college`, `graduate`, or `doctorate`.

## Setup

1. **Parse arguments.** Extract `<entry-slug>` and optional `<tier>`.

2. **Load the entry.** Read `entries/<slug>.md`. If the file doesn't exist, report the error and stop.

3. **Determine the tier.** If the user provided one, use it. If not:
   - If `activated:` in the frontmatter is blank → tier = `college` (this is an activation quiz)
   - Otherwise → tier = `graduate`

4. **Identify whether this is an activation quiz.** It is an activation quiz iff `activated:` is blank AND tier is `college`.

## Tier definitions (internal — do not show the table to the user)

| Tier | Bloom levels | Question types |
|---|---|---|
| college | Remember + Understand | Define X. Identify the example. Explain in your own words. |
| graduate | Apply + Analyze | Apply X to this scenario. Distinguish X from Y. Diagnose this argument. |
| doctorate | Evaluate + Create | Critique this use of X. Construct a case where X fails. Resolve the tension between X and Y. |

## Question generation rules

- Generate **3-5 questions**, total.
- **Mix formats within the tier.** Never ask three "define X" questions in a row.
- Pull from the entry's own examples *and* invent fresh scenarios. Do not just regurgitate the markdown.
- For type=distinction entries: at least one question must force *application* of the contrast, not recitation.
- Vary question shape across the session: open-ended, multiple-choice, "what's wrong with this?", scenario diagnosis.

## Conducting the session

1. Briefly tell the user what they're being quizzed on and at what tier. One line.
2. Ask **one question at a time.** Wait for the user's answer. Do not show the next question until they respond.
3. After each answer, give a brief evaluation using exactly this rubric:
   - **Solid** — accurate and complete.
   - **Partial** — got the gist, missed nuance. Name what was missed in one sentence.
   - **Off** — wrong or confused. Give the correct picture in 1-2 sentences.
4. Optionally ask a follow-up if the user's answer was instructive but incomplete. No more than one follow-up per question.
5. Move to the next question.

## Anti-sycophancy guardrail

Do not soften feedback. A partial answer is not "great" — it is partial. Naming weakness precisely is the value you provide. The user wants to actually improve, not feel good. Avoid: "good attempt," "you're on the right track," "almost," "nice try." Use: "solid," "partial — you missed X," "off — the correct picture is Y."

## Session verdict

After the final question, give a verdict:

- **Passed** — all solid, or one partial out of N.
- **Partial** — multiple partials, or one off.
- **Needs work** — multiple offs, or fundamental misunderstanding.

Then one sentence of what to focus on next time. No encouragement padding.

## Logging

Append exactly one JSON object on its own line to `log/attempts.jsonl`:

```json
{"date":"YYYY-MM-DD","entry":"<slug>","tier":"<tier>","verdict":"passed|partial|needs work","weak_spots":["..."]}
```

`weak_spots` is an array of short strings (or empty for "passed"). Use today's date.

If `log/attempts.jsonl` does not exist, create it with this as the first line.

**Atomicity:** If the user interrupts the session before the final verdict, write nothing to the log.

## Activation update

If this was an activation quiz AND the verdict is `passed`:
- Update the entry's frontmatter: set `activated:` to today's date in YYYY-MM-DD.
- Confirm to the user: "Entry activated — it's now eligible for `/logos-drill`."

If activation quiz with verdict `partial` or `needs work`:
- Do NOT update `activated:`.
- Tell the user: "Activation not granted yet — try again when you're ready."
