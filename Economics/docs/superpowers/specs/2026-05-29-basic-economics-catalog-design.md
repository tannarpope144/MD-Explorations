# Basic Economics Catalog — Design

**Date:** 2026-05-29
**Status:** Approved
**Author:** Tannar Pope (with Claude)

## Purpose

A reference catalog of the economic principles in Thomas Sowell's *Basic Economics*,
each paired with how it actually played out in the real world. The catalog is built so
that an **agent can look up a single principle and pull only that file into context** —
no need to load the whole corpus.

## Goals

- **Exhaustive coverage** of the distinct ideas in *Basic Economics* (estimated 60–100+ principles).
- Each principle is a **standalone, small Markdown file** — minimal context cost per lookup.
- Each principle records **how it worked out in the real world**, drawing on Sowell's own
  examples plus broader documented cases.
- A **master index** lets an agent find the right principle without reading every file.

## Non-Goals

- Not a prose summary or book report of *Basic Economics*.
- Not a structured-data (YAML/JSON) dataset — Markdown was chosen for readability/greppability.
- Not original economic research or novel claims; this catalogs established ideas and well-documented outcomes.

## Structure

```
Economics/
├── README.md                 # what this is, how agents should use it
├── INDEX.md                  # master lookup table (the agent's entry point)
├── principles/
│   ├── P001-scarcity.md
│   ├── P002-prices-as-signals.md
│   ├── P003-rent-control.md
│   └── … one file per principle
└── docs/superpowers/specs/   # design docs
```

### Lookup flow for an agent

1. Read the small `INDEX.md`.
2. Find the matching principle row (by name, category, fallacy, or tag).
3. Open **only** that one `Pxxx-*.md` file.

This keeps per-lookup context minimal — the core reason for one-file-per-principle.

### IDs and filenames

- Stable IDs of the form `Pxxx` (zero-padded, e.g. `P003`).
- Filename = `ID-kebab-name.md` (e.g. `P003-rent-control.md`).
- IDs are stable so files can cross-link and agents can cite them.

### Categories

Mirror Sowell's seven parts. Used for filtering/tagging, **not** for foldering
(all principle files live flat in `principles/`):

1. Prices & Markets
2. Industry & Commerce
3. Work & Pay
4. Time & Risk
5. National Economy
6. International Economy
7. Special Issues

## INDEX.md format

A single Markdown table, one row per principle:

| ID | Principle | Category | Corrects fallacy | Tags |
|----|-----------|----------|------------------|------|
| P003 | Rent control | Prices & Markets | "caps make housing affordable" | housing, price-controls, shortages |

## Per-principle file template

Every `Pxxx-*.md` file uses these fixed headings so agents can rely on a consistent shape:

```markdown
# P003 — Rent Control

**Category:** Prices & Markets
**Tags:** housing, price-controls, shortages
**Source:** Basic Economics (Sowell), Ch. 3 — Price Controls

## Principle
Formal statement of the economic principle.

## In plain English
One or two sentences an agent can quote directly.

## The fallacy it corrects
The wrong intuition this counters (e.g., "price caps make housing more affordable").

## How it played out
- **Sowell's cases:** the examples from the book (NYC, San Francisco…) + outcome.
- **Broader cases:** other documented instances (other cities/eras) + outcome.

## Related principles
- P002 — Prices as signals
- P00x — Shortages vs. scarcity
```

## Content sourcing

- Principles and Sowell's examples are drawn from *Basic Economics* (Sowell).
- "Broader cases" add other documented real-world instances (other countries/eras).
- For specific real-world claims (dates, figures, named places), stick to well-established,
  widely-reported facts and phrase carefully. Do **not** invent precise statistics. When a
  figure is approximate or uncertain, say so rather than fabricate precision.

## Build process

"Exhaustive" is a large body of work. Build **category-by-category** with a review checkpoint:

1. Draft **Part I — Prices & Markets** fully (all its principle files + their INDEX rows).
2. **Review checkpoint:** user reviews quality and format on this real sample.
3. After approval, proceed through Parts II–VII, one category at a time.

This avoids producing 100 files in a format that would need rework.

> **Execution note:** the implementation plan is written for **handoff to Sonnet** —
> the drafting work (per-category batches) is intended to be carried out by Sonnet agents.

## Validation

A final check that:

- Every `INDEX.md` row has a matching `principles/Pxxx-*.md` file (and vice versa).
- Every principle file contains all required template sections.
- Every cross-referenced ID in "Related principles" exists.

Done as a review pass or a small script at the end of each category and at completion.

## Success criteria

- An agent can answer "what does Sowell say about X and how did it work out?" by reading
  `INDEX.md` plus one principle file.
- Coverage spans all seven parts of the book.
- Format is consistent across every file (validated).
