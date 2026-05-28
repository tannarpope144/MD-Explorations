# CliftonStrengths Reference for Humans & LLM Agents — Design

**Date:** 2026-05-27
**Status:** Approved

## Purpose

A research-backed reference covering all 34 CliftonStrengths (StrengthsFinder)
themes, structured so an LLM agent can tailor its responses to a user's known
strengths, and so humans can read it directly. Descriptions are original wording
that faithfully captures the official Gallup meaning (verified via web research),
not verbatim copies of Gallup's copyrighted text. Official theme names and the
4-domain classification are used as-is, since those are factual.

## Audience & Use Case

- **Primary:** an LLM agent loads the theme files for a user's known strengths
  and uses the guidance to craft responses matched to how that person thinks,
  communicates, and is motivated.
- **Secondary:** humans (coaches, staff) read the same files as a plain reference.

## Architecture / File Layout

```
StrengthsFinder/
├── README.md                     # Index + "How agents should use this"
├── themes/
│   ├── executing/                # 9 themes
│   ├── influencing/              # 8 themes
│   ├── relationship-building/    # 9 themes
│   └── strategic-thinking/       # 8 themes
│         └── achiever.md  ... etc. (34 files total)
```

- One file per theme (34 files), grouped into domain subfolders.
- `README.md` is the entry point: a table of all 34 themes
  (name → domain → one-line summary → file link), plus a short
  **"How to use this reference to tailor responses"** guide for agents.

### The 34 Themes by Domain

- **Executing (9):** Achiever, Arranger, Belief, Consistency, Deliberative,
  Discipline, Focus, Responsibility, Restorative
- **Influencing (8):** Activator, Command, Communication, Competition,
  Maximizer, Self-Assurance, Significance, Woo
- **Relationship Building (9):** Adaptability, Connectedness, Developer,
  Empathy, Harmony, Includer, Individualization, Positivity, Relator
- **Strategic Thinking (8):** Analytical, Context, Futuristic, Ideation,
  Input, Intellection, Learner, Strategic

## Per-Theme File Structure

Each theme file has YAML frontmatter plus rich prose.

```yaml
---
name: Achiever
domain: Executing
keywords: [drive, stamina, productivity, completion]
one_liner: Has a constant need for achievement; driven to accomplish.
---
```

Then these sections:

1. **Overview** — what the theme is (original wording).
2. **What they value / what drives them.**
3. **How to communicate with them** — core agent-tailoring guidance.
4. **Motivating language vs. demotivating language** — concrete contrasts.
5. **Blind spots / shadow side.**
6. **Example phrasings an agent could use** — ready-to-adapt snippets.
7. **Sources** — citations from the web research.

## Process

1. Web-research each theme against Gallup and reputable sources, batched by
   domain.
2. Write each theme file with frontmatter + the 7 sections, in original wording.
3. Build `README.md` index and the agent-usage guide.

## Constraints

- No verbatim reproduction of Gallup's copyrighted theme descriptions or report
  text. Original wording only; short attributed quotes with citation are
  acceptable where they genuinely add value.
- Official theme names and 4-domain classification used as-is (factual).

## Out of Scope (YAGNI)

- Personalized reports for specific individuals.
- Theme-pairing / "strengths dynamics" analysis between multiple themes.
- Any scoring or assessment functionality.
