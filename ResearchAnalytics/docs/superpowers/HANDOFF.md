# Handoff: Idea Evaluation Engine

**To:** A fresh Claude (Sonnet) session that will implement this project.
**From:** The design/planning session (2026-05-29).
**Working dir:** `C:\Users\Tannar Pope\Desktop\MDExplorations\ResearchAnalytics`

---

## 1. What you're building (in one paragraph)

A **provider-agnostic Python harness** that takes a single idea/policy prompt (e.g.
`"Universal Basic Income"`) and autonomously produces a rigorous, blunt, pragmatic
evaluation. It maps steel-manned positions (pro/against/in-between), finds real-world
cases where the idea was tried (normalized into a comparison ledger), recursively
verifies *why* outcomes happened (generating a left-leaning and a right-leaning
explanation, then chasing each with data), surveys existing policy, and synthesizes a
value-neutral tradeoff framework **plus** a decisive bottom-line verdict that an
adversarial red-team has already attacked. It emits two artifacts: a full **formal
Markdown file** (the dissertation, with tiered citations) and a conversational **chat
synthesis** (the bottom line + tradeoffs, printed to stdout).

The guiding philosophy (from researching `nousresearch/hermes-agent`): **the harness is
the effort multiplier.** Deterministic Python owns the loop, the budgets, and the rigor
contracts; the LLM does only the reasoning. Rigor is enforced in *code*, not prompt
discipline — a malformed claim literally cannot enter the pipeline.

## 2. The non-negotiable rigor contracts (the soul of the project)

These are WHY the project exists. Do not water them down for convenience.

1. **Data → Insight → Acknowledged bias/lean.** Every analytical `Claim` must carry
   ≥1 piece of evidence, an insight (the so-what), and a bias_note (who makes this
   argument / which way it leans). Enforced by Pydantic — a claim missing any of these
   fails validation and is sent back to the model to retry.
2. **Tiered sourcing.** Every source is tagged T1 (primary data) → T2 (peer-reviewed) →
   T3 (reputable secondary) → T4 (advocacy/opinion). The report must distinguish
   well-established from contested from one-sided framing.
3. **Normalized case ledger.** Every real-world instance fills the SAME fields so
   comparison is apples-to-apples, not narrative. "Tried in 4 places, succeeded in 1"
   must be grounded in differing ledger cells, not a vibe.
4. **Governed recursive causal verification.** When an outcome has no obvious cause,
   generate a LEFT-leaning read AND a RIGHT-leaning read, then verify each with data,
   recursively. Stop a thread when EITHER fires: (a) **depth budget** (default 4,
   configurable) or (b) **confidence/resolution** (confirmed / refuted / data-doesn't-
   exist), with a global **search budget** as backstop. **Any thread cut short by a cap
   MUST be labeled "unresolved — would need deeper investigation."** Silent dropping is
   itself a bias and is forbidden.
5. **Two-layer verdict, kept separate.** A value-neutral conditional framework ("good
   idea IF you value X and accept tradeoff Y") AND a blunt bottom line — with the
   strongest counter-argument to that bottom line surfaced by a red-team pass.

## 3. Architecture decisions already made (do not relitigate)

- **Standalone Python, NOT inside Claude Code.** Must run multi-provider
  (Anthropic + OpenAI + DeepSeek), so it owns its own loop.
- **Provider layer = direct SDKs + thin adapter** (Approach A, à la hermes-agent), NOT
  LiteLLM. ~150 lines per adapter buys native structured-output + Anthropic prompt
  caching. DeepSeek is OpenAI-API-compatible (subclass the OpenAI client, swap base_url).
- **Structured output keystone:** one `structured_call(schema, messages, model, ...)`
  method per provider + a **validate-and-retry wrapper** (parse → Pydantic validate → on
  failure resend the validation errors → retry N times → else hard-fail). OpenAI/DeepSeek
  use strict JSON-schema `response_format`; Anthropic uses forced tool-use whose tool
  input schema IS the Pydantic schema. **This is the single most important component.**
- **Model routing by class, not by name:** stages declare `light` / `medium` / `heavy`;
  `config.py` maps each class → (provider, model). No provider preferences are fixed —
  the model names in `default_config()` (`deepseek-chat`, `gpt-4o-mini`,
  `claude-3-5-sonnet-latest`) are ILLUSTRATIVE defaults the user will retune.
- **Search = Firecrawl** (`/search` + `/scrape`→markdown) behind a swappable
  `SearchClient` interface, mirroring the LLM layer.
- **Output = Markdown** with inline citation links annotated by tier (`[Src](url) [T2]`)
  + a References section.

## 4. Where everything lives

- **Spec (the why/what):** `docs/superpowers/specs/2026-05-29-idea-evaluation-engine-design.md`
- **Plan (the how, 18 TDD tasks):** `docs/superpowers/plans/2026-05-29-idea-evaluation-engine.md`
- **This handoff:** `docs/superpowers/HANDOFF.md`
- Read the spec first for intent, then execute the plan task-by-task.

## 5. How to execute

**REQUIRED:** Use the `superpowers:executing-plans` skill (you're an inline session, not
dispatching subagents). Follow the plan's tasks **strictly in order** — they build in
dependency order and each leaves the test suite green. Each task is TDD:
write failing test → run it (confirm it fails) → minimal implementation → run it (confirm
it passes) → commit. **Do not skip the "run the test and watch it fail" step** — it's how
you catch a test that passes for the wrong reason.

The plan contains complete code for every step. If reality diverges from the plan (an SDK
signature changed, a test won't fail as predicted), STOP and surface it rather than
improvising silently — the user wants confusion surfaced, not hidden (see their CLAUDE.md).

### Build order at a glance
0. Scaffold → 1–2. Contracts → **3. LLM base + validate-retry (keystone)** →
4. Provider adapters → 5. Config + class factory → 6. Firecrawl search →
7. ResearchContext (budgeted search + routed LLM) → 8–13. Stages (positions, cases,
**governed verify**, policy, synthesize, red-team) → 14. JSON store → 15. Render
(formal + chat) → 16. Pipeline → 17. CLI → 18. README + live smoke run.

## 6. Keys & the live run

- **Tasks 0–17 need NO API keys** — every test mocks the SDKs and Firecrawl via
  `pytest-mock` / `monkeypatch`. You can build and verify the entire system offline.
- **Task 18 is a live smoke run** that DOES need real keys in `.env` (copy from
  `.env.example`: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`,
  `FIRECRAWL_API_KEY`). If the user hasn't provided keys when you reach Task 18, complete
  everything else, run the full mocked suite green, then PAUSE and ask the user to
  populate `.env` before the live run. Do not fabricate a "successful" live run.

## 7. Environment notes

- Windows 11, PowerShell default shell. Bash is also available via the Bash tool.
- This dir is **not yet a git repo** — Task 0 step 5 runs `git init`. After that, commit
  after every task as the plan specifies (frequent commits).
- Per the user's global CLAUDE.md: surgical changes, simplicity first, surface
  assumptions/confusion, don't over-engineer. The plan already reflects this (e.g.,
  parallel fan-out is deliberately deferred — see below).

## 8. Deliberate deferrals (these are NOT gaps — don't "fix" them)

- **Parallel fan-out is wired sequentially in v1.** Per-outcome verification threads are
  independent and can later drop into `concurrent.futures` with no interface change.
  Don't add concurrency now (YAGNI).
- **No cross-session memory.** This is a single-job tool, not the long-running
  hermes-style research partner. Out of scope for v1.

## 9. Definition of done

- `pytest -v` is fully green (Tasks 1–17).
- `python -m evaluate "Universal Basic Income" --out-dir ./reports` produces a formal
  `.md` (with Positions, a Case Ledger table, Causal Verification with any cut-short
  thread labeled "unresolved", Existing Policy, Tradeoff Framework, a red-teamed Verdict,
  and a tier-annotated References list) + a JSON run record, and prints the chat synthesis.
- Spot-check the honesty guarantees by eye: no claim lacks a source link + tier; every
  capped thread carries the "unresolved — would need deeper investigation" note.

---

**First action for the receiving session:** read the spec, then read the plan, then
invoke `superpowers:executing-plans` and begin at Task 0.
