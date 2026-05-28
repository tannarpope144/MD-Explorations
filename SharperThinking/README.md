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
