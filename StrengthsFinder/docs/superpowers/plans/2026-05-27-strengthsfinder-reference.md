# CliftonStrengths Reference Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a research-backed reference of all 34 CliftonStrengths themes (one markdown file per theme, grouped by domain, plus an index README) that an LLM agent can load to tailor responses, and humans can read directly.

**Architecture:** A `themes/` tree with four domain subfolders, each holding theme files that share an identical structure (YAML frontmatter + 7 prose sections). A top-level `README.md` indexes all themes and explains how an agent should use the reference. Content is original wording verified against Gallup and reputable sources; no verbatim copying of copyrighted descriptions.

**Tech Stack:** Markdown, YAML frontmatter. Research via WebSearch/WebFetch.

---

## File Structure

```
StrengthsFinder/
├── README.md                              # index + agent-usage guide
└── themes/
    ├── executing/
    │   ├── achiever.md
    │   ├── arranger.md
    │   ├── belief.md
    │   ├── consistency.md
    │   ├── deliberative.md
    │   ├── discipline.md
    │   ├── focus.md
    │   ├── responsibility.md
    │   └── restorative.md
    ├── influencing/
    │   ├── activator.md
    │   ├── command.md
    │   ├── communication.md
    │   ├── competition.md
    │   ├── maximizer.md
    │   ├── self-assurance.md
    │   ├── significance.md
    │   └── woo.md
    ├── relationship-building/
    │   ├── adaptability.md
    │   ├── connectedness.md
    │   ├── developer.md
    │   ├── empathy.md
    │   ├── harmony.md
    │   ├── includer.md
    │   ├── individualization.md
    │   ├── positivity.md
    │   └── relator.md
    └── strategic-thinking/
        ├── analytical.md
        ├── context.md
        ├── futuristic.md
        ├── ideation.md
        ├── input.md
        ├── intellection.md
        ├── learner.md
        └── strategic.md
```

Each theme file responsibility: fully describe ONE theme with agent-tailoring guidance. `README.md` responsibility: navigation + usage instructions only (no theme content duplicated).

---

## Canonical Theme File Template

Every theme file MUST follow this exact structure. `Achiever` shown as a worked example; all other files mirror it with theme-appropriate content.

````markdown
---
name: Achiever
domain: Executing
keywords: [drive, stamina, productivity, completion, work-ethic]
one_liner: Driven by a constant need to accomplish; finds deep satisfaction in being busy and productive.
---

# Achiever

## Overview

People strong in Achiever have a relentless inner drive to get things done.
Every day starts at zero, and they need to reach a tangible level of
accomplishment before they feel the day was worthwhile. This drive is steady and
self-renewing rather than tied to any single goal. *(Original wording faithful
to Gallup's theme definition.)*

## What They Value / What Drives Them

- Visible progress and completed tasks.
- A full, productive day; momentum and stamina.
- Being counted on to carry a heavy workload.

## How to Communicate With Them

- Acknowledge what they've already accomplished before adding more.
- Be concise and action-oriented; give them next steps, not just discussion.
- Frame requests as concrete, completable tasks with clear finish lines.

## Motivating Language vs. Demotivating Language

| Motivating | Demotivating |
|---|---|
| "Here's a clear list you can knock out today." | "Let's table this and revisit eventually." |
| "You've already shipped a lot — here's the next milestone." | "There's no real deadline, take your time." |
| "I know I can count on you to finish this." | "Don't worry about getting it all done." |

## Blind Spots / Shadow Side

- May overwork or struggle to rest, equating busyness with worth.
- Can undervalue reflection, relationships, or celebration in favor of the next task.
- Risk of burnout and impatience with slower-moving people or processes.

## Example Phrasings an Agent Could Use

- "Let's break this into a checklist so you can see it shrink."
- "You closed out three big things this week — want to line up the next?"
- "Here's the fastest path to done."

## Sources

- Gallup, CliftonStrengths "Achiever" theme (official theme definition).
- [Additional reputable source consulted during research.]
````

Rules for content:
- Original wording only. No verbatim Gallup sentences. Short attributed quotes are allowed in Sources/Overview if cited and genuinely additive.
- Official theme name and domain assignment used exactly.
- Keep each section tight; the file should be skimmable.

---

## Task 1: Scaffold directories and the worked example

**Files:**
- Create: `themes/executing/achiever.md`
- (Directories are created implicitly by writing files.)

- [ ] **Step 1: Write `themes/executing/achiever.md`** using the Canonical Theme File Template above, verbatim as the worked example (it is already researched).

- [ ] **Step 2: Verify structure**

Run: `Get-Content themes/executing/achiever.md | Select-String '^(##|---|name:|domain:)'`
Expected: frontmatter keys + all 7 section headings present.

- [ ] **Step 3: Commit**

```bash
git add themes/executing/achiever.md
git commit -m "Add Achiever theme as canonical example"
```

---

## Task 2: Executing domain (remaining 8 themes)

**Files:**
- Create: `themes/executing/arranger.md`, `belief.md`, `consistency.md`, `deliberative.md`, `discipline.md`, `focus.md`, `responsibility.md`, `restorative.md`

- [ ] **Step 1: Research** each of the 8 themes via WebSearch/WebFetch against Gallup and reputable sources. For each, note: core definition, what drives them, communication tips, blind spots.

- [ ] **Step 2: Write** all 8 files using the Canonical Theme File Template. `domain: Executing` for every file. Original wording.

- [ ] **Step 3: Verify** every file has frontmatter (`name`, `domain`, `keywords`, `one_liner`) and all 7 section headings.

Run: `Get-ChildItem themes/executing/*.md | ForEach-Object { $h=(Get-Content $_ | Select-String '^## ').Count; "$($_.Name): $h sections" }`
Expected: each file reports 7 sections.

- [ ] **Step 4: Commit**

```bash
git add themes/executing
git commit -m "Add remaining Executing domain themes"
```

---

## Task 3: Influencing domain (8 themes)

**Files:**
- Create: `themes/influencing/activator.md`, `command.md`, `communication.md`, `competition.md`, `maximizer.md`, `self-assurance.md`, `significance.md`, `woo.md`

- [ ] **Step 1: Research** the 8 Influencing themes (Gallup + reputable sources).

- [ ] **Step 2: Write** all 8 files using the template. `domain: Influencing`. Original wording.

- [ ] **Step 3: Verify** structure.

Run: `Get-ChildItem themes/influencing/*.md | ForEach-Object { $h=(Get-Content $_ | Select-String '^## ').Count; "$($_.Name): $h sections" }`
Expected: each file reports 7 sections.

- [ ] **Step 4: Commit**

```bash
git add themes/influencing
git commit -m "Add Influencing domain themes"
```

---

## Task 4: Relationship Building domain (9 themes)

**Files:**
- Create: `themes/relationship-building/adaptability.md`, `connectedness.md`, `developer.md`, `empathy.md`, `harmony.md`, `includer.md`, `individualization.md`, `positivity.md`, `relator.md`

- [ ] **Step 1: Research** the 9 Relationship Building themes (Gallup + reputable sources).

- [ ] **Step 2: Write** all 9 files using the template. `domain: Relationship Building`. Original wording.

- [ ] **Step 3: Verify** structure.

Run: `Get-ChildItem themes/relationship-building/*.md | ForEach-Object { $h=(Get-Content $_ | Select-String '^## ').Count; "$($_.Name): $h sections" }`
Expected: each file reports 7 sections.

- [ ] **Step 4: Commit**

```bash
git add themes/relationship-building
git commit -m "Add Relationship Building domain themes"
```

---

## Task 5: Strategic Thinking domain (8 themes)

**Files:**
- Create: `themes/strategic-thinking/analytical.md`, `context.md`, `futuristic.md`, `ideation.md`, `input.md`, `intellection.md`, `learner.md`, `strategic.md`

- [ ] **Step 1: Research** the 8 Strategic Thinking themes (Gallup + reputable sources).

- [ ] **Step 2: Write** all 8 files using the template. `domain: Strategic Thinking`. Original wording.

- [ ] **Step 3: Verify** structure.

Run: `Get-ChildItem themes/strategic-thinking/*.md | ForEach-Object { $h=(Get-Content $_ | Select-String '^## ').Count; "$($_.Name): $h sections" }`
Expected: each file reports 7 sections.

- [ ] **Step 4: Commit**

```bash
git add themes/strategic-thinking
git commit -m "Add Strategic Thinking domain themes"
```

---

## Task 6: README index + agent-usage guide

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write `README.md`** containing:
  - A short intro describing the reference and its copyright stance (original wording, faithful to Gallup).
  - A **"How agents should use this reference"** section with concrete instructions, e.g.:
    1. Identify the user's known themes.
    2. Load only those theme files.
    3. Apply each theme's "How to Communicate" and "Motivating Language" guidance.
    4. Avoid demotivating-language patterns.
    5. When a user has multiple themes, blend the guidance rather than overweighting one.
  - A table of all 34 themes grouped by domain: `| Theme | Domain | One-liner | File |`, with relative links to each file.

- [ ] **Step 2: Verify** all 34 links resolve.

Run: `Select-String -Path README.md -Pattern '\]\((themes/[^)]+)\)' | ForEach-Object { $_.Matches.Groups[1].Value } | ForEach-Object { if (Test-Path $_) { "OK $_" } else { "MISSING $_" } }`
Expected: 34 lines, all "OK".

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "Add README index and agent-usage guide"
```

---

## Task 7: Final consistency pass

**Files:**
- Modify: any theme file with detected inconsistencies.

- [ ] **Step 1: Confirm 34 theme files exist.**

Run: `(Get-ChildItem -Recurse themes/*.md).Count`
Expected: 34

- [ ] **Step 2: Confirm every file has required frontmatter keys.**

Run: `Get-ChildItem -Recurse themes/*.md | Where-Object { -not ((Get-Content $_ -Raw) -match 'name:' -and (Get-Content $_ -Raw) -match 'domain:' -and (Get-Content $_ -Raw) -match 'keywords:' -and (Get-Content $_ -Raw) -match 'one_liner:') } | Select-Object Name`
Expected: no output (all files have the keys).

- [ ] **Step 3: Spot-check** 3 random files for verbatim-copy risk; reword anything too close to source text.

- [ ] **Step 4: Commit** any fixes.

```bash
git add -A
git commit -m "Final consistency pass on StrengthsFinder reference"
```

---

## Self-Review Notes

- **Spec coverage:** all 34 themes (Tasks 1-5), per-theme 7-section + frontmatter structure (template + every write step), README index + agent-usage guide (Task 6), copyright constraint (template rules + Task 7 step 3). Covered.
- **Out-of-scope items** (personalized reports, theme-pairing analysis, scoring) are intentionally excluded.
- **Consistency:** `domain` values are fixed per task and match the spec's exact domain names.
