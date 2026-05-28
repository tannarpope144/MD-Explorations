# Logos System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Logos system — four Claude Code slash commands (`/logos-capture`, `/logos-quiz`, `/logos-drill`, `/logos-review`) that operate on a flat folder of markdown entries to support tiered self-quizzing on terms, frameworks, and distinctions.

**Architecture:** Pure markdown + slash-command prompts. No scripts, no databases. Entries live in `entries/` as `.md` files with YAML frontmatter. Quiz attempts are appended to `log/attempts.jsonl`. All orchestration — file scanning, frontmatter parsing, log writing, weighted random selection — is performed by Claude executing instructions in the command prompt files.

**Tech Stack:** Markdown, YAML frontmatter, JSONL, Claude Code slash commands.

---

## File Structure

| File | Responsibility |
|---|---|
| `entries/second-order-thinking.md` | Seed entry — proof the structure works end-to-end |
| `templates/entry-template.md` | Skeleton used by `/logos-capture` |
| `.claude/commands/logos-capture.md` | Capture prompt: gather, sharpen, draft, offer activation |
| `.claude/commands/logos-quiz.md` | Quiz prompt: tier rules, question generation, evaluation, logging, activation update |
| `.claude/commands/logos-drill.md` | Drill prompt: scan entries, weighted-least-recent pick, delegate to quiz |
| `.claude/commands/logos-review.md` | Review prompt: tabular listing with filters |
| `log/.gitkeep` | Keep `log/` directory in git before first quiz |
| `log/attempts.jsonl` | Append-only quiz history (created on first quiz) |
| `README.md` | One-page user guide |

Each command prompt is one focused file with one responsibility. The seed entry and template are reference material the prompts will mention by path.

---

## Task 1: Scaffold directories and gitignore

**Files:**
- Create: `entries/.gitkeep`
- Create: `templates/.gitkeep`
- Create: `.claude/commands/.gitkeep`
- Create: `log/.gitkeep`
- Modify: `.gitignore` (already exists with `.superpowers/`)

- [ ] **Step 1: Create empty directory placeholders**

```bash
cd "C:/Users/Tannar Pope/Desktop/MDExplorations/SharperThinking"
mkdir -p entries templates .claude/commands log
touch entries/.gitkeep templates/.gitkeep .claude/commands/.gitkeep log/.gitkeep
```

- [ ] **Step 2: Verify .gitignore already excludes .superpowers/**

Run: `cat .gitignore`
Expected output: `.superpowers/`

If missing, add it.

- [ ] **Step 3: Verify structure**

Run: `ls -la entries templates .claude/commands log`
Expected: each directory contains a `.gitkeep` file.

- [ ] **Step 4: Commit**

```bash
git add entries/.gitkeep templates/.gitkeep .claude/commands/.gitkeep log/.gitkeep
git commit -m "chore: scaffold logos directory structure"
```

---

## Task 2: Write the entry template

**Files:**
- Create: `templates/entry-template.md`

- [ ] **Step 1: Write the template**

Create `templates/entry-template.md` with this exact content:

```markdown
---
name: <Human-readable name>
type: <term | framework | distinction>
tags: []
related: []
source: ""
captured: <YYYY-MM-DD>
activated:
---

## Definition
<One or two sentences. Precise. In your own words.>

## When to use
- <Situation 1>
- <Situation 2>

## When NOT to use
- <Misuse 1>
- <Misuse 2>

## Examples
1. <Concrete example>
2. <Concrete example>

## Notes
<Optional personal annotations.>
```

**For type=distinction**, replace the body sections with:

```markdown
## Side A
<Name of one side and what it means.>

## Side B
<Name of the other side and what it means.>

## The distinction
<Why the contrast matters. What confusion does drawing this line prevent?>

## Examples
1. <Concrete example showing the contrast in action>

## Notes
<Optional personal annotations.>
```

**For type=framework**, the standard body works, but a `## Steps` or `## Structure` section may be added before `## Examples`.

- [ ] **Step 2: Verify the file**

Run: `cat templates/entry-template.md`
Expected: full template visible.

- [ ] **Step 3: Commit**

```bash
git add templates/entry-template.md
git commit -m "feat: add entry template for logos system"
```

---

## Task 3: Write the seed entry (second-order-thinking)

**Files:**
- Create: `entries/second-order-thinking.md`

- [ ] **Step 1: Write the seed entry**

Create `entries/second-order-thinking.md`:

```markdown
---
name: Second-Order Thinking
type: framework
tags: [decision-making, systems, consequences]
related: [first-order-thinking, unintended-consequences, chestertons-fence]
source: "Howard Marks, The Most Important Thing; popularized by Shane Parrish (Farnam Street)"
captured: 2026-05-28
activated: 2026-05-28
---

## Definition
Reasoning about the consequences of the consequences. First-order thinking
asks "what happens if I do X?"; second-order thinking asks "and then what?"
— following effects out at least one more step than the obvious answer.

## When to use
- Policy decisions where incentives may produce paradoxical results
- Investment choices where consensus already prices in the obvious outcome
- Negotiation, where your counterparty will react to your move
- Any time the "obvious" answer feels too easy

## When NOT to use
- Reversible, low-stakes decisions where deliberation costs more than mistakes
- When you lack the domain knowledge to reason credibly past the first step
  (speculation dressed as analysis is worse than admitting the obvious)
- When second-order thinking becomes a stalling tactic against acting on a clear answer

## Examples
1. Rent control: first-order says "rents are lower, tenants benefit." Second-order
   asks "and then what?" — landlords under-invest in maintenance, supply shrinks,
   the lowest-income renters get squeezed out.
2. Pay engineers per bug fixed: first-order incentivizes fixing. Second-order
   incentivizes shipping bugs to fix later.
3. In investing: if everyone agrees a stock will go up, the price already reflects
   that — the second-order question is "what does the consensus miss?"

## Notes
The classic failure mode is stopping at the second order when the relevant
dynamics live at the third or fourth. The discipline isn't "think one more step"
— it's "keep asking 'and then what?' until you stop getting new information."
```

- [ ] **Step 2: Verify**

Run: `cat entries/second-order-thinking.md`
Expected: file matches the content above.

- [ ] **Step 3: Commit**

```bash
git add entries/second-order-thinking.md
git commit -m "feat: add second-order-thinking seed entry"
```

---

## Task 4: Write /logos-capture prompt

**Files:**
- Create: `.claude/commands/logos-capture.md`

- [ ] **Step 1: Write the capture command prompt**

Create `.claude/commands/logos-capture.md`:

```markdown
---
description: Capture a new entry (term, framework, or distinction) from a rough note
---

# /logos-capture

You are helping the user capture a new entry in their Logos system. The user has provided rough notes or just a term name in the arguments below:

**User input:** $ARGUMENTS

## Your job

1. **Determine if this is a duplicate.** Compute a slug from the term name (lowercase, hyphens, ASCII only). Check if `entries/<slug>.md` already exists. If it does, show the existing entry and ask the user: edit, run a quiz on it, or cancel. Do not proceed with capture.

2. **Sharpen before drafting.** Read the user's rough input. If anything is vague, imprecise, or ambiguous, ask **1-3 targeted sharpening questions** — one at a time — to pin it down. Capture is itself a thinking exercise. Examples of good sharpening questions:
   - "You wrote X. Is that the same as Y, or is there a difference you want the entry to preserve?"
   - "Is this a term (a name for a thing), a framework (a way to think), or a distinction (a contrast between two ideas)?"
   - "Where did you encounter this? A specific source helps later when reviewing."

   Do not ask sharpening questions you can answer from context. Do not ask more than three.

3. **Draft the entry.** Use the template at `templates/entry-template.md` as the skeleton. Choose the appropriate variant based on `type`. Fill in:
   - `name` — human-readable
   - `type` — term, framework, or distinction
   - `tags` — 2-4 lowercase, hyphenated tags
   - `related` — slugs (filenames without `.md`) of related entries that already exist in `entries/` or that the user mentions. Do not invent slugs for entries that don't exist.
   - `source` — what the user gave you, as a free-text string
   - `captured` — today's date in YYYY-MM-DD
   - `activated` — **leave blank**

   Write the body in the user's own framing where possible, sharpened for precision.

4. **Save to `entries/<slug>.md`.** Confirm the file was created.

5. **Offer the activation quiz.** End your response with exactly:

   > Entry drafted at `entries/<slug>.md` (not yet activated).
   >
   > Want to run your activation quiz now? It's college tier — short, focused on recognition and definition. Run `/logos-quiz <slug>` to start, or come back to it later.

## Hard rules

- Never set `activated` during capture. Activation only happens via `/logos-quiz`.
- Never invent a source the user didn't mention.
- Never add `related` slugs to entries that don't exist on disk.
- If the user's input is just a term name with no context, ask sharpening questions before drafting — don't fabricate a definition.
```

- [ ] **Step 2: Verify the file is valid markdown**

Run: `cat .claude/commands/logos-capture.md`
Expected: full prompt visible, frontmatter intact.

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/logos-capture.md
git commit -m "feat: add /logos-capture command"
```

---

## Task 5: Write /logos-quiz prompt

**Files:**
- Create: `.claude/commands/logos-quiz.md`

- [ ] **Step 1: Write the quiz command prompt**

Create `.claude/commands/logos-quiz.md`:

````markdown
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
````

- [ ] **Step 2: Verify the file**

Run: `cat .claude/commands/logos-quiz.md`
Expected: full prompt with all sections, frontmatter intact.

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/logos-quiz.md
git commit -m "feat: add /logos-quiz command with anti-sycophancy guardrail"
```

---

## Task 6: Write /logos-drill prompt

**Files:**
- Create: `.claude/commands/logos-drill.md`

- [ ] **Step 1: Write the drill command prompt**

Create `.claude/commands/logos-drill.md`:

```markdown
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
```

- [ ] **Step 2: Verify the file**

Run: `cat .claude/commands/logos-drill.md`
Expected: full prompt visible.

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/logos-drill.md
git commit -m "feat: add /logos-drill command with weighted-least-recent selection"
```

---

## Task 7: Write /logos-review prompt

**Files:**
- Create: `.claude/commands/logos-review.md`

- [ ] **Step 1: Write the review command prompt**

Create `.claude/commands/logos-review.md`:

```markdown
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
```

- [ ] **Step 2: Verify the file**

Run: `cat .claude/commands/logos-review.md`
Expected: full prompt visible.

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/logos-review.md
git commit -m "feat: add /logos-review command with filters"
```

---

## Task 8: Write the README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write the README**

Create `README.md`:

````markdown
# Logos

A personal system for sharpening thinking and communication — captures precise terms, mental frameworks, and conceptual distinctions, then drills you on them at college, graduate, or doctorate tier.

Built on plain markdown + Claude Code slash commands. No scripts, no database.

## How it works

Every entry lives as a markdown file in `entries/` with frontmatter declaring its type (term / framework / distinction), tags, and activation status. Captured entries are **inert until you pass an activation quiz** — this prevents the failure mode where you accumulate cool-sounding notes you never actually internalize.

Four slash commands run the system:

| Command | What it does |
|---|---|
| `/logos-capture <rough note>` | Drafts a new entry from a fragment, asks sharpening questions, offers an activation quiz |
| `/logos-quiz <slug> [tier]` | Quizzes you on an entry. Tier defaults to college (if not activated) or graduate (if activated) |
| `/logos-drill [tier] [--tag x]` | Picks an activated entry weighted toward least-recently drilled, then quizzes you |
| `/logos-review [filters]` | Tabular overview. Filters: `--unactivated`, `--tag x`, `--stale [days]`, `--struggling` |

## The three tiers

- **College** — recognition and recall. Define the term, identify an example.
- **Graduate** — application and analysis. Apply it to a scenario; distinguish it from neighbors.
- **Doctorate** — evaluation and synthesis. Critique uses of it; resolve tensions; construct edge cases.

(Bloom's taxonomy maps internally — two Bloom levels per tier — so the quizzer can vary question types within a tier.)

## Entry types

- **term** — a precise word for a thing (e.g., *steelmanning*)
- **framework** — a way of thinking (e.g., *second-order thinking*)
- **distinction** — a paired contrast worth holding (e.g., *risk vs. uncertainty*)

All three share the same frontmatter shape; the body sections differ slightly. See `templates/entry-template.md`.

## The point

The quizzer is built to tell you precisely where you're weak. No "great job" — just `solid` / `partial` / `off`, with the specific gap named. The system is for improvement, not engagement.

## Files

```
entries/                # one .md per term/framework/distinction (flat)
templates/              # entry skeleton
.claude/commands/       # the four slash commands
log/attempts.jsonl      # append-only quiz history
docs/superpowers/       # design spec and implementation plan
```

## Adding to your corpus

```
/logos-capture steelmanning - heard on Lex w/ Weinstein, presenting the strongest version of an opposing argument
```

Claude will draft the entry, ask any sharpening questions, save it, and offer the activation quiz. Once activated, it's eligible for `/logos-drill`.
````

- [ ] **Step 2: Verify**

Run: `cat README.md`
Expected: full README visible.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add Logos README"
```

---

## Task 9: End-to-end smoke test

**Goal:** Manually verify the four commands work against the real corpus. No code, just exercising the system as a user would.

- [ ] **Step 1: Verify the seed entry is recognized**

In Claude Code, run:

```
/logos-review
```

Expected: a table containing one row for "Second-Order Thinking" with `Activated: 2026-05-28`, `Last drilled: —`, `Last verdict: —`. Summary line: "1 entry total (1 activated, 0 unactivated)."

- [ ] **Step 2: Test /logos-quiz on the seed entry at graduate tier**

Run:

```
/logos-quiz second-order-thinking graduate
```

Expected:
- Claude states the entry name and tier in one line.
- Claude asks 3-5 questions, one at a time, waiting for your answer between each.
- Each evaluation uses `solid` / `partial` / `off` — not "great job."
- A final verdict and a one-line "focus on this next time."
- A new line appears in `log/attempts.jsonl`.

Verify:

```bash
cat log/attempts.jsonl
```

Expected: one JSON line with today's date, entry `second-order-thinking`, tier `graduate`, a verdict, and a (possibly empty) `weak_spots` array.

- [ ] **Step 3: Test /logos-drill**

Run:

```
/logos-drill graduate
```

Expected: Claude picks second-order-thinking (the only activated entry), states why ("most recent drill was today" or similar), and delegates into the quiz flow.

- [ ] **Step 4: Test /logos-capture with a vague input**

Run:

```
/logos-capture chestertons fence - heard somewhere, dont remove a fence if you dont know why its there
```

Expected:
- Claude asks 1-3 sharpening questions before drafting (e.g., "Is this a term or a framework?", "Where did you hear it?").
- After answering, Claude drafts `entries/chestertons-fence.md` with `activated:` blank.
- Claude offers the activation quiz.

Verify the file exists:

```bash
cat entries/chestertons-fence.md
```

Expected: complete entry, `activated:` blank.

- [ ] **Step 5: Test activation flow**

Run:

```
/logos-quiz chestertons-fence
```

(No tier — should default to college since not yet activated.)

Take the quiz. If you pass:

```bash
grep '^activated:' entries/chestertons-fence.md
```

Expected: `activated: 2026-05-28` (today's date).

- [ ] **Step 6: Verify /logos-review --unactivated filter**

Run:

```
/logos-review --unactivated
```

Expected: if Chesterton's Fence was activated in step 5, the table is empty. If not, that entry is the only row.

- [ ] **Step 7: Commit smoke-test outputs**

The smoke test produces real entries and log lines. Commit them:

```bash
git add entries/ log/attempts.jsonl
git commit -m "test: end-to-end smoke test of logos system"
```

---

## Task 10: Final review

- [ ] **Step 1: Sanity check the full system**

Run:

```
/logos-review
```

You should see at least two entries (Second-Order Thinking + whatever you captured during the smoke test) with accurate "last drilled" data.

- [ ] **Step 2: Verify nothing is broken**

```bash
ls -la entries/ .claude/commands/ templates/ log/
git log --oneline | head -15
```

Expected:
- Files in each directory match the file structure table above.
- Git log shows ~10 commits for this feature.

- [ ] **Step 3: Stop and reflect**

Open one entry. Read it. Does it actually sharpen your understanding of the concept? If yes, the system works. If no, the entry needs revision — not the system.

---

## Self-Review (completed by author)

**1. Spec coverage:**
- Folder structure → Task 1 ✓
- Entry structure & template → Task 2 ✓
- Seed entry → Task 3 ✓
- /logos-capture (with sharpening, duplicate handling, activation offer) → Task 4 ✓
- /logos-quiz (tier rules, question rules, evaluation rubric, anti-sycophancy, logging, activation update, atomicity) → Task 5 ✓
- /logos-drill (filter to activated, weighted-least-recent, never-drilled treatment, empty-corpus behavior) → Task 6 ✓
- /logos-review (all four filters, malformed frontmatter loud-fail) → Task 7 ✓
- README → Task 8 ✓
- End-to-end verification → Tasks 9-10 ✓

**2. Placeholder scan:** No TBDs, no "add appropriate X," no "similar to Task N." Every prompt is fully written.

**3. Type consistency:** Slug format (lowercase, hyphenated, no `.md`) is consistent across capture, quiz, drill, and review. Frontmatter field names (`name`, `type`, `tags`, `related`, `source`, `captured`, `activated`) match across template, seed entry, and all four command prompts. Verdict values (`passed`, `partial`, `needs work`) match between the quiz prompt's verdict section and the review prompt's `--struggling` filter.
