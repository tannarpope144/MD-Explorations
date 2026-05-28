# Logos — A System for Sharpening Thinking and Communication

**Date:** 2026-05-28
**Status:** Design approved, ready for implementation planning

## Purpose

A personal system for absorbing precise terms, mental frameworks, and conceptual distinctions encountered in podcasts, books, and conversations — and actually internalizing them through tiered self-quizzing. The goal is sharper day-to-day thinking and communication, not building a personal wiki.

The system is named **Logos** (λόγος — reason, discourse, the principle of rational thought). All slash commands use the `logos-` prefix.

## Core Decisions

| Decision | Choice |
|---|---|
| Source of truth | Markdown files with YAML frontmatter |
| Interface | Claude Code slash commands |
| Entry types | Terms, frameworks, distinctions |
| Folder layout | Flat (`entries/`) with frontmatter tags |
| Quiz generation | AI-generated on demand, not pre-written |
| Difficulty tiers | College / Graduate / Doctorate (Bloom-mapped internally) |
| Capture rule | Entries are inert until passing an activation quiz |
| Selection logic | Manual default; weighted-least-recent for random drill |
| Out of scope (v1) | Spaced repetition, quotes, people, web UI, gamification |

## Folder Structure

```
SharperThinking/
├── entries/                    # flat folder, all entry types
│   ├── steelmanning.md
│   ├── second-order-thinking.md
│   ├── risk-vs-uncertainty.md
│   └── ...
├── .claude/
│   ├── commands/
│   │   ├── logos-capture.md
│   │   ├── logos-quiz.md
│   │   ├── logos-drill.md
│   │   └── logos-review.md
│   └── settings.json
├── templates/
│   └── entry-template.md
├── log/
│   └── attempts.jsonl          # append-only quiz history
├── docs/
│   └── superpowers/specs/
├── README.md
└── .gitignore                  # ignores .superpowers/
```

**Rationale:**
- Flat `entries/` keeps the system Obsidian-friendly and grep-friendly. Categorization lives in frontmatter `tags`.
- `log/attempts.jsonl` is append-only and schemaless enough to evolve without migrations. Sufficient for future spaced-repetition without locking us in.
- `.superpowers/` is git-ignored (visual companion session data).

## Entry Structure

Every entry — term, framework, or distinction — uses the same shape. The `type` field disambiguates.

```markdown
---
name: Steelmanning
type: term                       # term | framework | distinction
tags: [argumentation, epistemics]
related: [strawman, charitable-interpretation, principle-of-charity]
source: "Lex Fridman ep #234 w/ Eric Weinstein"
captured: 2026-05-28
activated:                       # date passed first quiz; blank = not yet active
---

## Definition
Presenting the strongest possible version of an opposing argument before
critiquing it — stronger than the version the opponent actually made.

## When to use
- Public debate where intellectual honesty matters
- Internal reasoning when you suspect motivated reasoning in yourself
- Before dismissing a position you find distasteful

## When NOT to use
- When time is short and the position is clearly bad-faith
- Performatively, to signal virtue without engaging
- When the original argument is already strong (you're being patronizing)

## Examples
1. Before arguing against a policy, restating it in terms its supporters would endorse.
2. In a code review: rebuilding the author's reasoning before suggesting changes.

## Notes
(Your own annotations. Optional.)
```

**Variations by type:**

- **Distinction:** `name` is the pair ("Risk vs. Uncertainty"). Body uses `## Side A` / `## Side B` / `## The distinction` instead of the standard sections.
- **Framework:** Same shape; body tends to include a `## Steps` or `## Structure` section.

**Field rationale:**
- `activated:` is a date, not a boolean — preserves *when* you internalized it.
- `related:` uses slugs (filename without `.md`), enabling future graph operations without parsing prose.
- `source:` is a free-text string — enough provenance without a citation schema.

## Difficulty Tiers (Bloom-mapped)

Three tiers exposed to the user, internally informed by Bloom's revised taxonomy so the quizzer can vary question types within a tier.

| Tier | Bloom levels | Example question types |
|---|---|---|
| **College** | Remember + Understand | Define X. Identify the example. Explain in your own words. |
| **Graduate** | Apply + Analyze | Apply X to this scenario. Distinguish X from Y. Diagnose this argument. |
| **Doctorate** | Evaluate + Create | Critique this use of X. Construct a case where X fails. Resolve the tension between X and Y. |

The activation quiz is **always college tier** — a low bar proving recognition. Mastery at higher tiers comes through repeated drilling.

## Slash Commands

### `/logos-capture <rough note or term name>`

Fast capture from a podcast/article/conversation. Result: a draft entry, ready for activation quiz.

**Flow:**
1. Invoked with whatever the user has — a term, a quote, a fragment.
2. Claude asks 1-3 targeted *sharpening* questions to fill gaps (type? source detail? what struck you?). The prompt explicitly instructs Claude to push back on vague phrasing — capture itself is a thinking exercise, not data entry.
3. Claude writes a draft `.md` file to `entries/<slug>.md` from the template.
4. `activated:` is left blank.
5. Claude immediately offers: *"Want to run your activation quiz now? (college tier)"*

**Duplicate handling:** If the slug already exists, the command shows the existing entry and asks: edit / quiz / cancel.

### `/logos-quiz <entry-slug> [tier]`

Drill a specific entry at a chosen tier.

**Flow:**
1. Loads the entry's markdown.
2. Loads the tier definition (College / Graduate / Doctorate, with Bloom mapping internal to the prompt).
3. Generates 3-5 fresh questions appropriate to the tier — mixed formats (recall, application, critique, scenario).
4. Asks one at a time. User answers in chat.
5. After each answer: brief evaluation + the model answer + a follow-up if useful.
6. End of session: a verdict (passed / partial / needs work) and one sentence of what to focus on next.
7. Appends a single line to `log/attempts.jsonl`.
8. If this is the **activation quiz** (no `activated:` date yet) and the user passes college tier → frontmatter is updated with today's date.

**Tier defaults if omitted:** college if not yet activated, graduate otherwise.

**Atomicity:** A session that is interrupted before completion writes nothing to the log. Sessions are all-or-nothing.

### `/logos-drill [tier] [tag-filter]`

"Sharpen me on something — you pick."

**Flow:**
1. Scans `entries/` frontmatter; filters to activated entries only.
2. Picks one entry, weighted toward least-recently drilled (from `log/attempts.jsonl`), respecting optional tag filter. Entries that have never been drilled are treated as maximally stale and get the highest weight.
3. Delegates to `/logos-quiz <picked-slug> <tier>`.

**Empty-corpus behavior:** If no activated entries exist, reports the count of unactivated entries and points to `/logos-review --unactivated`.

**Why weighted-least-recent:** Simplest selection that prevents drilling the same three favorites. Same log file supports a future upgrade to true spaced repetition without migration.

### `/logos-review [filter]`

Browse and reflect — no quiz here.

**Flow:**
1. Lists entries in a table: name, type, tags, activated?, last drilled, last result.
2. Optional filters:
   - `--unactivated` — drafts awaiting activation
   - `--tag <x>` — restrict to a tag
   - `--stale [days]` — not drilled in the last `days` days (default 30)
   - `--struggling` — last verdict was "needs work"
3. Each row links to the file.

## The Quiz Prompt (the heart of the system)

The single most important component. Lives in `.claude/commands/logos-quiz.md` and contains:

**1. Tier definitions** with Bloom mapping (see table above).

**2. Question-generation rules:**
- Generate 3-5 questions per session.
- Mix formats within a tier — never three "define X" in a row.
- Pull from the entry's own examples *and* invent fresh scenarios. Don't regurgitate the markdown.
- For distinctions: at least one question must force *application* of the contrast, not recitation.
- Vary shape: open-ended, multiple-choice, "what's wrong with this?", scenario diagnosis.

**3. Evaluation rubric** — per question:
- **Solid** — accurate and complete.
- **Partial** — got the gist, missed nuance (with what was missed).
- **Off** — wrong or confused (with the correct picture).

**4. Session verdict:**
- **Passed** — all solid, or one partial.
- **Partial** — multiple partials or one off.
- **Needs work** — multiple offs or fundamental misunderstanding.

**5. Log line** appended to `log/attempts.jsonl`:
```json
{"date":"2026-05-28","entry":"steelmanning","tier":"graduate","verdict":"partial","weak_spots":["distinguishing from charitable interpretation"]}
```

**6. Anti-sycophancy guardrail.** The prompt explicitly instructs:

> Do not soften feedback. A partial answer is not "great" — it is partial. Naming weakness precisely is the value you provide. The user wants to actually improve, not feel good.

This is the most important sentence in the system. Without it, the AI defaults to encouraging tone and the user stops improving.

## Capture & Activation Rules

**An entry is inert until activated.**

```
/logos-capture          →  writes entries/<slug>.md with activated: (blank)
       │
       └─→ offers immediate activation quiz (college tier)
              │
              ├─ pass         → frontmatter updated with activated: <date>
              ├─ partial/fail → entry stays inactive; user can retry anytime
              └─ skip         → entry stays inactive
```

**Consequences of inactivity:**
- Invisible to `/logos-drill` — won't be picked for random drilling.
- Shows up in `/logos-review --unactivated` as a TODO list.

**Activation is a one-way door.** Once activated, an entry stays activated. Later "needs work" verdicts surface via `--struggling` filter but do not revoke activation.

## Edge Cases

| Case | Behavior |
|---|---|
| Duplicate capture | Show existing entry; offer edit / quiz / cancel |
| Empty corpus on `/logos-drill` | Report count of unactivated; point to `/logos-review --unactivated` |
| Malformed frontmatter | Fail loudly with file path; no silent skipping |
| Tier omitted in `/logos-quiz` | College if not activated, graduate if activated |
| Quiz interrupted mid-session | No log line written — sessions are atomic |
| `related:` slug points to non-existent entry | `/logos-review` flags it; quizzer ignores it |

## Explicitly Out of Scope (v1)

- True spaced-repetition algorithm — weighted-least-recent suffices until the corpus is large.
- Entry types beyond term/framework/distinction (no quotes, no people).
- Pre-written quiz questions per entry — AI generates fresh each time.
- Web UI or Obsidian plugin — markdown + Claude Code only.
- Multi-user / sync — single-user; git is the sync layer if desired.
- Audio/video capture from podcasts — capture by hand or paste a transcript snippet.
- Numeric grades, streaks, gamification — the system is for improvement, not engagement.

## Success Criteria

The system is working if:

1. After a podcast, the user can capture a new term in under 2 minutes and activate it within 5.
2. The user can name 10+ activated terms after 4 weeks of use and use them correctly in conversation.
3. `/logos-drill` reliably surfaces something the user hasn't seen in a while.
4. The quizzer's feedback is precise enough that the user can identify a specific weakness after a session — not just a vibe.
5. The user doesn't accumulate a graveyard of unactivated entries (`/logos-review --unactivated` stays short).

## Future Considerations (NOT v1)

- Spaced-repetition algorithm operating on the existing `attempts.jsonl`.
- A `/logos-link` command to surface related-but-unconnected entries based on tag overlap.
- A `/logos-essay` command that picks 2-3 activated entries and asks the user to write a short integration piece using all of them.
- Periodic "audit" reviews flagging entries that have never been drilled at graduate or doctorate tier.

These are deliberately deferred. v1 ships with the four commands above.
