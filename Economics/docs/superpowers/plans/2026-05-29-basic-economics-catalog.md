# Basic Economics Catalog Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Handoff note:** This plan is intended for execution by **Sonnet** agents. The author (Opus) wrote the plan; drafting of the catalog files is delegated per-category to Sonnet.

**Goal:** Build an exhaustive, one-file-per-principle Markdown catalog of the economic principles in Thomas Sowell's *Basic Economics*, each paired with how it played out in the real world, with a master `INDEX.md` for low-context agent lookup.

**Architecture:** Flat `principles/` directory of `Pxxx-kebab-name.md` files, each following a fixed template. A single `INDEX.md` table is the agent's entry point; agents read the index, then open exactly one principle file. Categories mirror Sowell's seven book parts and are used as tags/filters, not folders.

**Tech Stack:** Markdown only. Optional Node or PowerShell for the final validation pass. No build system, no runtime dependencies.

**Spec:** `docs/superpowers/specs/2026-05-29-basic-economics-catalog-design.md`

---

## Conventions (read before any task)

**ID assignment:** IDs are `Pxxx`, zero-padded to 3 digits, assigned sequentially in catalog order. Reserve ID blocks per category so categories can be drafted independently without collisions:

| Category | ID range |
|----------|----------|
| Part I — Prices & Markets | P001–P049 |
| Part II — Industry & Commerce | P050–P089 |
| Part III — Work & Pay | P090–P129 |
| Part IV — Time & Risk | P130–P159 |
| Part V — National Economy | P160–P199 |
| Part VI — International Economy | P200–P229 |
| Part VII — Special Issues | P230–P259 |

Assign IDs densely from the bottom of each range (P001, P002, …). Unused IDs in a range are fine — do not renumber to close gaps.

**Filename:** `principles/<ID>-<kebab-name>.md`, e.g. `principles/P003-rent-control.md`.

**Required file template (every principle file must match exactly):**

```markdown
# <ID> — <Principle Name>

**Category:** <one of the 7 categories>
**Tags:** <comma-separated lowercase tags>
**Source:** Basic Economics (Sowell), Ch. <n> — <chapter topic>

## Principle
<Formal statement of the economic principle.>

## In plain English
<One or two sentences an agent can quote directly.>

## The fallacy it corrects
<The wrong intuition this counters.>

## How it played out
- **Sowell's cases:** <examples from the book + outcome.>
- **Broader cases:** <other documented real-world instances + outcome.>

## Related principles
- <ID> — <name>
- <ID> — <name>
```

**INDEX.md row format:** `| <ID> | <Principle> | <Category> | <"fallacy in quotes"> | <tag, tag, tag> |`

**Sourcing rules (apply to every file):**
- Principles and "Sowell's cases" come from *Basic Economics*.
- "Broader cases" are other documented real-world instances (other countries/eras).
- For specific claims (dates, figures, named places) use only well-established, widely-reported facts. **Do not invent precise statistics.** If a figure is approximate, say "roughly"/"around" or describe direction of effect rather than fabricate precision.

**No-git note:** This folder is not a git repository. "Commit" steps below are written as **checkpoint** steps (no `git` command). If the user later runs `git init`, convert checkpoints to commits.

---

## Task 1: Scaffold the catalog

**Files:**
- Create: `README.md`
- Create: `INDEX.md`
- Create: `principles/.gitkeep` (placeholder so the empty dir exists)

- [ ] **Step 1: Create `principles/` directory with a placeholder**

Create `principles/.gitkeep` (empty file).

- [ ] **Step 2: Write `README.md`**

```markdown
# Basic Economics Catalog

A reference catalog of the economic principles in Thomas Sowell's *Basic Economics*,
each paired with how it played out in the real world.

## For agents — how to use this

1. Open `INDEX.md` (small — safe to load fully).
2. Find the principle by name, category, fallacy, or tag.
3. Open **only** the matching `principles/Pxxx-*.md` file. Do not load the whole folder.

## Structure

- `INDEX.md` — master lookup table.
- `principles/Pxxx-*.md` — one file per principle, fixed template.

## Categories (Sowell's seven parts)

1. Prices & Markets
2. Industry & Commerce
3. Work & Pay
4. Time & Risk
5. National Economy
6. International Economy
7. Special Issues

## Sourcing

Principles and primary examples are from *Basic Economics* (Sowell). "Broader cases"
add other documented real-world instances. Specific figures are kept to well-established
facts; approximate numbers are flagged as such.
```

- [ ] **Step 3: Write `INDEX.md` header (empty table, ready for rows)**

```markdown
# Basic Economics Catalog — Index

One row per principle. Open the matching `principles/<ID>-*.md` file for detail.

| ID | Principle | Category | Corrects fallacy | Tags |
|----|-----------|----------|------------------|------|
```

- [ ] **Step 4: Verify scaffold**

Run: `ls principles ; cat INDEX.md`
Expected: `principles/` exists; `INDEX.md` shows the header and empty table.

- [ ] **Step 5: Checkpoint**

Confirm `README.md`, `INDEX.md`, and `principles/` exist. Proceed to Task 2.

---

## Task 2: Part I — Prices & Markets (gold-standard sample) [REVIEW CHECKPOINT]

This is the **sample category**. After it is drafted, STOP for user review of quality and format before continuing. ID range **P001–P049**.

**Files:**
- Create: one `principles/Pxxx-*.md` per principle below.
- Modify: `INDEX.md` (add one row per principle).

**Candidate principles (create a file for each; add any additional distinct idea you find in Part I — the goal is exhaustive):**

1. Scarcity and trade-offs (the definition of economics)
2. Prices as signals / conveyors of information
3. Prices as incentives
4. Prices as a rationing mechanism
5. Price ceilings cause shortages
6. Rent control (housing shortage, deterioration, reduced construction, misallocation)
7. Price floors cause surpluses (e.g., agricultural price supports)
8. Scarcity vs. shortage (distinct concepts)
9. Black markets arise from price controls
10. Quality deterioration under price controls
11. Non-price allocation (lines, favoritism, discrimination) when prices are suppressed
12. There are no "needs," only trade-offs at the margin (incremental substitution)
13. Profit and loss as guidance signals
14. Competition disciplines prices
15. Hoarding / shortages dynamics under controls
16. Knowledge coordination — prices mobilize dispersed knowledge (Hayekian point as Sowell frames it)

- [ ] **Step 1: Write the gold-standard file `principles/P006-rent-control.md`**

Use this exact content as the quality bar for all other files:

```markdown
# P006 — Rent Control

**Category:** Prices & Markets
**Tags:** housing, price-controls, shortages, unintended-consequences
**Source:** Basic Economics (Sowell), Ch. 3 — Price Controls

## Principle
A government-imposed ceiling on rents, set below the market-clearing price, increases
the quantity of housing demanded while reducing the quantity supplied, producing a
persistent housing shortage and a series of secondary effects: reduced new construction,
deterioration of existing units, and allocation of scarce housing by non-price means.

## In plain English
Capping rents below market doesn't create more housing — it creates less, and the
housing that remains gets harder to find and worse maintained.

## The fallacy it corrects
"Rent control makes housing more affordable." It lowers the listed price but raises the
real cost of obtaining housing (search time, key money, lost availability) and shrinks supply.

## How it played out
- **Sowell's cases:** New York City's long-running rent control coincided with housing
  shortages, aging un-maintained buildings, and landlords abandoning unprofitable units.
  San Francisco rent control is associated with reduced rental supply as units convert
  to other uses. Sowell contrasts controlled and uncontrolled markets to show shortages
  appear where prices are capped.
- **Broader cases:** Post–WWII rent controls in numerous cities produced similar
  shortages; economists across the spectrum widely regard binding rent ceilings as a
  cause of reduced housing supply. Stockholm's regulated rents are a frequently cited
  example of long waiting lists for apartments.

## Related principles
- P005 — Price ceilings cause shortages
- P002 — Prices as signals
- P011 — Non-price allocation
```

- [ ] **Step 2: Draft the remaining Part I files**

For each remaining candidate (and any additional distinct Part I idea), create
`principles/Pxxx-*.md` following the template and matching the gold-standard's depth.
Assign IDs sequentially in P001–P049. Fill every section — no placeholders.

- [ ] **Step 3: Add INDEX rows for every Part I file**

Append one row per file to the table in `INDEX.md`, in ID order.

- [ ] **Step 4: Validate Part I**

Run these checks:
- Run: `ls principles` — every Part I ID has a file.
- Run: `grep -L "## How it played out" principles/*.md` — expected: no output (every file has the section).
- Run: `grep -c "^| P0" INDEX.md` — count matches the number of Part I files created.
- Spot-check 3 files: all six headings present, "How it played out" has both Sowell's and Broader cases, Related principles point to IDs that exist.

Expected: all checks pass.

- [ ] **Step 5: REVIEW CHECKPOINT — stop for user review**

Present the Part I files and INDEX rows to the user. Do NOT start Task 3 until the user
approves the quality and format. Apply any requested format changes to Part I first; those
changes become the standard for all later categories.

---

## Task 3: Part II — Industry & Commerce

ID range **P050–P089**. Follow the same steps as Task 2 (create files → add INDEX rows → validate), using the format approved in the Task 2 checkpoint.

**Candidate principles (exhaustive — add any distinct idea you find):**
1. The role of profit (incentive to satisfy consumers)
2. Losses are as important as profits (they force efficiency / reallocation)
3. Profit rate vs. total profit (rate of return matters)
4. Rise and fall of businesses / creative destruction
5. Specialization and division of labor
6. Economies of scale (and diseconomies of scale)
7. Big business is not the same as monopoly
8. Monopoly raises prices and restricts output
9. Cartels are inherently unstable
10. Predatory pricing — theory vs. evidence
11. The entrepreneur and the middleman add value
12. Brand names and reputation as information that lowers consumer risk
13. Regulation and its unintended consequences (regulatory capture, raised barriers)
14. Cost incidence — who actually bears a cost/tax
15. Inventory and just-in-time as cost management
16. How profit allocates capital across the economy

- [ ] **Step 1: Draft Part II files** (template + approved format; IDs P050–P089)
- [ ] **Step 2: Add INDEX rows** for every Part II file
- [ ] **Step 3: Validate** (same checks as Task 2 Step 4, scoped to Part II IDs)
- [ ] **Step 4: Checkpoint** — report counts, proceed to Task 4

---

## Task 4: Part III — Work & Pay

ID range **P090–P129**. Same steps as Task 3.

**Candidate principles (exhaustive):**
1. Wages reflect productivity, not employer generosity or worker need
2. Minimum wage laws reduce employment for the least-skilled (notably young and minority workers)
3. Labor demand is a derived demand
4. Employers substitute capital for labor when labor is made more expensive
5. Job-security mandates reduce hiring
6. Unions: gains to members can come at the expense of non-members and the unemployed
7. Discrimination is costly to the discriminator in competitive markets
8. Discrimination is cheaper/easier under regulation, monopoly, or government
9. Pay and working conditions are trade-offs (compensating differentials)
10. Income brackets are not fixed groups — income mobility over a lifetime
11. "The rich" and "the poor" are often the same people at different ages
12. Household vs. individual income statistics mislead
13. Pay differences reflect skill, risk, and productivity
14. Exploitation myths
15. Child labor and economic development
16. Unemployment types (frictional, structural)

- [ ] **Step 1: Draft Part III files** (IDs P090–P129)
- [ ] **Step 2: Add INDEX rows**
- [ ] **Step 3: Validate** (Part III scope)
- [ ] **Step 4: Checkpoint** — proceed to Task 5

---

## Task 5: Part IV — Time & Risk

ID range **P130–P159**. Same steps.

**Candidate principles (exhaustive):**
1. Present value and time preference (discounting the future)
2. Investment as deferred consumption
3. Interest as the price of time / credit
4. Speculation transfers and reduces risk; speculators tend to stabilize prices
5. Insurance as risk pooling
6. Moral hazard and adverse selection
7. Profit as payment for bearing risk
8. Present value caps natural-resource extraction (rebuts "running out" alarms; "known reserves" are economic, not physical, limits)
9. Inventory as managing time and risk
10. Why future costs/benefits are discounted in decisions

- [ ] **Step 1: Draft Part IV files** (IDs P130–P159)
- [ ] **Step 2: Add INDEX rows**
- [ ] **Step 3: Validate** (Part IV scope)
- [ ] **Step 4: Checkpoint** — proceed to Task 6

---

## Task 6: Part V — The National Economy

ID range **P160–P199**. Same steps.

**Candidate principles (exhaustive):**
1. National output (GDP) and its measurement limits
2. Functions of money
3. Inflation as too much money chasing too few goods; inflation as a hidden tax
4. Banking and credit creation
5. The proper functions of government (rule of law, property rights, contracts, defense)
6. Property rights enable prosperity
7. Externalities and public goods
8. The national debt — what it is and is not
9. Fiscal vs. monetary policy
10. The fallacy of composition (true for one ≠ true for all)
11. The broken-window fallacy (destruction is not net gain)
12. Velocity of money
13. Deflation and its effects
14. The hidden price of "free" government services

- [ ] **Step 1: Draft Part V files** (IDs P160–P199)
- [ ] **Step 2: Add INDEX rows**
- [ ] **Step 3: Validate** (Part V scope)
- [ ] **Step 4: Checkpoint** — proceed to Task 7

---

## Task 7: Part VI — The International Economy

ID range **P200–P229**. Same steps.

**Candidate principles (exhaustive):**
1. Comparative advantage and the gains from trade
2. Free trade vs. protectionism
3. Tariffs and quotas raise consumer costs and "save" jobs at high cost per job
4. Balance-of-trade / trade-deficit myths
5. Exchange rates and what they do
6. International transfers of wealth (foreign aid, investment) — effects
7. Imperialism did not generally enrich the colonizers (myth correction)
8. Outsourcing and jobs
9. The "infant industry" argument and its problems
10. "Dumping" arguments
11. Multinational corporations' role

- [ ] **Step 1: Draft Part VI files** (IDs P200–P229)
- [ ] **Step 2: Add INDEX rows**
- [ ] **Step 3: Validate** (Part VI scope)
- [ ] **Step 4: Checkpoint** — proceed to Task 8

---

## Task 8: Part VII — Special Economic Issues

ID range **P230–P259**. Same steps.

**Candidate principles (exhaustive):**
1. The seen and the unseen (opportunity cost; Bastiat as Sowell uses it)
2. Zero-sum thinking is usually wrong (trade is mutually beneficial)
3. The fallacy of "unmet needs" (everything competes for scarce resources)
4. Third-party decision-making vs. decisions by those who bear the consequences
5. Post hoc fallacy in economic reasoning
6. Myths about markets (e.g., "trickle-down" is a straw man)
7. "Non-economic" values still involve trade-offs
8. The role and limits of economists
9. "Social justice" claims and economic trade-offs

- [ ] **Step 1: Draft Part VII files** (IDs P230–P259)
- [ ] **Step 2: Add INDEX rows**
- [ ] **Step 3: Validate** (Part VII scope)
- [ ] **Step 4: Checkpoint** — proceed to Task 9

---

## Task 9: Final catalog-wide validation

**Files:**
- Create: `scripts/validate-catalog.mjs` (optional helper) OR perform checks manually.
- Modify: any file that fails a check.

- [ ] **Step 1: Index ↔ files consistency**

Run: `grep -o "^| P[0-9]\{3\}" INDEX.md` and compare to `ls principles/P*.md`.
Expected: every INDEX ID has a file, and every file has an INDEX row. Fix any mismatch.

- [ ] **Step 2: Template completeness**

Run: `grep -L "## Principle" principles/P*.md` then repeat for each required heading
(`## In plain English`, `## The fallacy it corrects`, `## How it played out`, `## Related principles`).
Expected: no output for any heading (every file has every section). Fix any file that prints.

- [ ] **Step 3: Cross-reference integrity**

For every `Pxxx` referenced under "Related principles", confirm a file with that ID exists.
Run: extract referenced IDs and diff against `ls principles`. Fix dangling references.

- [ ] **Step 4: No-placeholder scan**

Run: `grep -rniE "TODO|TBD|FIXME|fill in|placeholder" principles INDEX.md README.md`
Expected: no output. Fix anything found.

- [ ] **Step 5: Report and checkpoint**

Report total principle count, count per category, and confirmation that Steps 1–4 pass.
Catalog complete.

---

## Self-Review (completed by plan author)

**Spec coverage:**
- Exhaustive coverage → Tasks 2–8 cover all seven parts with exhaustive candidate lists + "add any distinct idea" instruction. ✓
- One-file-per-principle, low-context lookup → Task 1 scaffold + flat `principles/`. ✓
- Real-world outcomes (Sowell + broader) → "How it played out" template section + sourcing rules; gold-standard file demonstrates both. ✓
- Master index → Task 1 creates it; every category task appends rows; Task 9 validates. ✓
- Fixed template / consistent format → template in Conventions; gold-standard sample; validation in Task 9. ✓
- Category-by-category build with review checkpoint after first category → Task 2 ends with REVIEW CHECKPOINT. ✓
- Sourcing discipline (no fabricated stats) → Sourcing rules in Conventions, repeated intent. ✓
- Validation → Task 9. ✓
- Sonnet handoff → header handoff note. ✓

**Placeholder scan:** Plan contains no TBD/TODO in instructions; the one gold-standard file is fully written. ✓

**Consistency:** ID ranges in Conventions match each task's stated range; filename/template/INDEX-row formats are identical everywhere; validation greps reference the exact heading strings used in the template. ✓
