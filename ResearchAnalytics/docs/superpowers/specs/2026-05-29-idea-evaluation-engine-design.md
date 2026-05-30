# Idea Evaluation Engine — Design

**Date:** 2026-05-29
**Status:** Approved design, pending implementation plan

## 1. Purpose

A provider-agnostic Python harness that takes a single idea or policy prompt (e.g.,
`"Universal Basic Income"`) and autonomously produces a rigorous, blunt, pragmatic
evaluation. It is inspired by the *hermes-agent* lesson that the **harness is the
effort multiplier**: a deterministic program fans out parallel agentic work, enforces
non-negotiable rigor contracts in code, routes stages to different models, and persists
the result.

The engine answers, for any idea:
- What are the curated positions (pro / against / in-between), steel-manned?
- Where has it been tried in the real world, and with what measurable outcomes?
- What does existing policy around it look like?
- Is an attempt at implementation a good idea — and how might it actually work?

Every analytical point obeys one contract: **Data → Insight → Acknowledged bias/lean.**

## 2. Non-Goals

- Not a Claude-Code-only tool. Must run standalone against multiple providers.
- Not a chat assistant or long-running multi-session research partner (single-job, deep).
- Not a general agent framework — it does *one* pipeline well.
- Does not invent data. Unverifiable threads are **labeled**, never silently dropped.

## 3. Core Principles (the rigor contracts)

These are enforced in **code**, not prompt discipline. A model cannot talk its way out
of them.

### 3.1 The Claim Contract
Every analytical point is a structured object:
```
Claim {
  statement: str
  data: Evidence[]          # >= 1 required; a claim with no data is rejected
  insight: str              # the interpretation/so-what
  bias_note: str            # acknowledged lean: who cites this, which direction it tilts
  confidence: enum(high|medium|low|speculative)
}
```
A claim missing `data` or `bias_note` fails validation and is sent back to the model.

### 3.2 Tiered Sourcing
Every `Evidence` carries a provenance tier:
```
Tier 1: primary data / official statistics
Tier 2: peer-reviewed research
Tier 3: reputable secondary (established journalism, gov reports)
Tier 4: advocacy / opinion / op-ed
```
The synthesis is **required** to distinguish well-established (T1–T2) from contested from
one-sided framing (T4). Tier is a field on every cited source and surfaces in the report.

### 3.3 The Case Ledger (structured internally, prose externally)
Every real-world instance is normalized into the **same fields** so comparison is
apples-to-apples, not narrative:
```
Case {
  location, start_date, end_date, scale (population/$), funding_model,
  target_population, outcome_metric, result, source_tier, sources[]
}
```
Cross-case divergence analysis ("succeeded in 1 of 4") must cite specific ledger cells.
The final report renders the ledger as readable prose + a summary table.

### 3.4 Recursive Causal Verification (governed)
When an outcome has no obvious cause, the engine generates **two competing
explanations — one left-leaning read, one right-leaning read** — then goes back out and
tries to verify each with data, recursively.

Example chain: `GDP dropped → maybe capital flight → research → 15% of businesses
relocated in 12mo [T1 cited] → but concurrent tax change? → research again…`

**Governor (stops a thread when EITHER fires):**
- **Depth budget** — max N layers deep (default 4, configurable via CLI/config). Stops
  runaway threads.
- **Confidence/resolution** — stop when the speculation is confirmed, refuted, or the
  data to settle it is determined not to exist. Stops fruitless threads.
- **Global research budget** — overall backstop (max searches / token spend).

Any thread cut short by a cap is explicitly labeled **"unresolved — would need deeper
investigation."** Silent dropping is itself a bias and is forbidden.

## 4. Architecture

```
evaluate/
├── __main__.py            # CLI: python -m evaluate "Universal Basic Income"
├── config.py              # model routing, budgets, API keys (env), defaults
├── pipeline.py            # the deterministic orchestrator (owns the loop + governor)
├── contracts.py           # Pydantic schemas: Claim, Evidence, Case, Verdict, etc.
├── llm/
│   ├── base.py            # LLMClient interface + structured_call() + validate-retry
│   ├── anthropic.py       # forced tool-use for structured output; prompt caching
│   ├── openai.py          # strict JSON-schema response_format
│   └── deepseek.py        # OpenAI-compatible (base_url swap)
├── search/
│   ├── base.py            # SearchClient interface (search + scrape)
│   └── firecrawl.py       # default impl: /search + /scrape -> clean markdown
├── stages/
│   ├── positions.py       # map & steel-man pro/against/in-between
│   ├── cases.py           # find real-world instances -> Case ledger
│   ├── verify.py          # recursive causal verification (governed)
│   ├── policy.py          # survey existing policy landscape
│   ├── synthesize.py      # conditional framework + blunt verdict
│   └── redteam.py         # adversarial attack on the verdict before finalizing
├── render/
│   ├── formal.py          # full scholarly artifact (the file)
│   └── chat.py            # the C-layer conversational synthesis (stdout)
└── store.py               # persist run: ledger, claims, chains, citations (JSON)
```

### 4.1 LLM Adapter Layer (Approach A: direct SDKs, thin adapter)
A small `LLMClient` interface implemented per provider. Core method:
```
structured_call(schema: type[BaseModel], messages, model, ...) -> BaseModel
```
- **OpenAI / DeepSeek:** strict JSON-schema `response_format`.
- **Anthropic:** forced tool-use whose tool input schema == the Pydantic schema; native
  prompt caching on the large synthesis context.
- **Validate-and-retry wrapper:** parse → Pydantic validate → on failure resend the
  validation errors and retry up to N times. The single most important piece of machinery.

### 4.2 Search Layer
`SearchClient` interface (mirrors the LLM layer for swappability). Default = **Firecrawl**
(`/search` for discovery, `/scrape` for clean markdown extraction).

### 4.3 Model Routing (light / medium / heavy classes)
First-class, declarative in `config.py`. Stages do **not** name models — they declare the
**class** of model they need:
```
light   # extraction, source-tier tagging, dedup, normalization
medium  # case-finding, policy survey, per-thread verification probes
heavy   # synthesis (framework + verdict), red-team
```
Config maps each class → (provider, model). Swapping which concrete model backs a class
is a one-line config change with no stage edits. No provider preferences are fixed in v1;
class→model mapping is left to runtime config.

## 5. Data Flow (the pipeline)

```
prompt "Universal Basic Income"
  │
  ▼ [positions]  steel-man pro / against / in-between  -> Claim[]  (Data→Insight→Bias)
  │
  ▼ [cases]      find real-world instances -> Case ledger (normalized fields)
  │
  ▼ [verify]     for each non-obvious outcome:
  │                 generate left-read + right-read -> recurse with governor
  │                 -> verified chains OR labeled-unresolved threads
  │
  ▼ [policy]     survey existing policy landscape -> Claim[]
  │
  ▼ [synthesize] conditional framework (value-neutral tradeoffs)
  │                 + blunt bottom-line verdict
  │
  ▼ [redteam]    adversarially attack the verdict; surface strongest counter;
  │                 verdict revised or defended explicitly
  │
  ▼ [render]     formal.md  (full record: claims, ledger, chains, citations+tiers,
  │                          framework, verdict, red-team)
  │              chat        (C-layer only: tradeoffs + blunt call, prose, points to file)
  └─ [store]     persist everything as JSON for audit/reuse
```

Parallel fan-out: position-mapping, case-finding, and per-thread verification probes are
dispatched as **parallel structured calls** (isolated so they don't pollute a shared
context — the hermes-agent subagent lesson), then merged deterministically by the pipeline.

## 6. Outputs (two artifacts, two altitudes)

- **Formal file** (`<topic>-evaluation-<date>.md`, **Markdown**): the dissertation. Every
  claim with Data→Insight→Bias, the case ledger + summary table, the recursive verification
  chains (including labeled-unresolved threads), the conditional framework, the blunt
  verdict, and the red-team. **Citations are inline Markdown links to source URLs, each
  annotated with its source tier** (e.g., `[source](url) [T2]`). A "References" section at
  the end lists every source with title, URL, and tier. The durable scholarly artifact.
- **Chat** (stdout): just the **C-layer** — the readable conversational synthesis. The
  tradeoff framework *and* the blunt bottom line, in prose, pointing to the file for receipts.

## 7. Error Handling & Honesty Guarantees

- **Schema violations** → validate-and-retry; hard-fail the run after N retries rather
  than emit an unvalidated claim.
- **Search failures / dead sources** → retry with backoff; if a claim's only support dies,
  the claim is downgraded in confidence and flagged, not silently kept.
- **Budget exhaustion** → governor stops gracefully; all cut-short threads labeled.
- **Provider errors** → adapter-level retry; optional fallback provider (config).
- **No-data outcome** → labeled `speculative`; never upgraded to fact.

## 8. Testing Strategy

- **Contracts:** unit tests that malformed claims/cases/evidence are rejected by Pydantic;
  validate-and-retry recovers from a deliberately bad model response (mocked).
- **Governor:** tests that depth cap, confidence-stop, and budget backstop each fire, and
  that cut-short threads are labeled.
- **Adapters:** mocked-SDK tests that each provider's `structured_call` returns a valid
  schema instance; one live smoke test per provider (opt-in, key-gated).
- **Pipeline:** an end-to-end run on a small fixed topic with mocked search/LLM, asserting
  the two artifacts are produced and every claim satisfies the contract.
- **Render:** snapshot tests of formal.md structure and the chat C-layer.

## 9. Stack

Python 3.11+, **Pydantic** (contracts/schemas), official `anthropic` + `openai` SDKs,
`httpx` (raw calls / Firecrawl), a small CLI. Config via env + `config.py`.

## 10. Future / Upgrade Path

- Add providers by implementing `LLMClient`; add search backends via `SearchClient`.
- Could later grow a persistent cross-session memory layer (hermes-agent style) if the
  single-job model ever needs to become a long-running research partner — explicitly out
  of scope for v1.
- Headless/scheduled runs are trivial once the CLI exists.
