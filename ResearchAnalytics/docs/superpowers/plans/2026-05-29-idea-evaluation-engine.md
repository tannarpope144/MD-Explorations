# Idea Evaluation Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a provider-agnostic Python harness that takes a single idea/policy prompt and autonomously produces a rigorous, blunt, pragmatic evaluation (formal Markdown file + conversational synthesis), enforcing Data→Insight→Bias, tiered sourcing, a normalized case ledger, and governed recursive causal verification.

**Architecture:** A deterministic Python orchestrator (`pipeline.py`) drives agentic stages. All model output passes through a per-provider `structured_call` adapter with Pydantic validate-and-retry, so rigor contracts are enforced in code. Stages declare a model *class* (light/medium/heavy) mapped to concrete models in config. Web research goes through a swappable `SearchClient` (Firecrawl default). Two artifacts are rendered: a full Markdown record and a conversational C-layer.

**Tech Stack:** Python 3.11+, Pydantic v2, official `anthropic` + `openai` SDKs, `httpx`, `pytest`, `pytest-mock`. CLI via `python -m evaluate "<topic>"`.

---

## File Structure

```
evaluate/
├── __init__.py
├── __main__.py            # CLI entry
├── config.py              # model-class routing, budgets, env keys
├── contracts.py           # Pydantic schemas (Evidence, Claim, Case, Verdict, ...)
├── store.py               # persist a run to JSON
├── pipeline.py            # orchestrator: stage sequence + governor
├── llm/
│   ├── __init__.py
│   ├── base.py            # LLMClient ABC + structured_call + validate-retry
│   ├── anthropic.py       # forced tool-use structured output
│   ├── openai.py          # strict JSON-schema response_format
│   ├── deepseek.py        # OpenAI-compatible (base_url swap)
│   └── factory.py         # class(light/medium/heavy) -> client+model
├── search/
│   ├── __init__.py
│   ├── base.py            # SearchClient ABC (search + scrape)
│   └── firecrawl.py       # default impl
├── stages/
│   ├── __init__.py
│   ├── positions.py       # steel-man pro/against/in-between -> Claim[]
│   ├── cases.py           # real-world instances -> Case[]
│   ├── verify.py          # governed recursive causal verification
│   ├── policy.py          # existing-policy survey -> Claim[]
│   ├── synthesize.py      # conditional framework + blunt verdict
│   └── redteam.py         # adversarial attack on verdict
└── render/
    ├── __init__.py
    ├── formal.py          # full Markdown record
    └── chat.py            # C-layer conversational synthesis
tests/                     # mirrors package layout
pyproject.toml
.env.example
```

**Build order rationale:** contracts first (everything depends on them) → LLM adapter (the keystone) → search → individual stages (each independently testable with mocked LLM/search) → governor logic in verify → pipeline wiring → render → CLI. Each task leaves the tree green.

---

## Task 0: Project scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `evaluate/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "evaluate"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.6",
    "anthropic>=0.39",
    "openai>=1.40",
    "httpx>=0.27",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-mock>=3.12"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create `.env.example`**

```
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
DEEPSEEK_API_KEY=
FIRECRAWL_API_KEY=
```

- [ ] **Step 3: Create empty `evaluate/__init__.py` and `tests/__init__.py`**

```python
# evaluate/__init__.py
```
```python
# tests/__init__.py
```

- [ ] **Step 4: Install and verify**

Run: `pip install -e ".[dev]"`
Expected: installs without error.

Run: `python -c "import evaluate; print('ok')"`
Expected: prints `ok`

- [ ] **Step 5: Commit**

```bash
git init
git add pyproject.toml .env.example evaluate/__init__.py tests/__init__.py
git commit -m "chore: project scaffold"
```

---

## Task 1: Core contracts (Pydantic schemas)

**Files:**
- Create: `evaluate/contracts.py`
- Test: `tests/test_contracts.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_contracts.py
import pytest
from pydantic import ValidationError
from evaluate.contracts import Evidence, Claim, Case, SourceTier, Confidence

def test_evidence_requires_url_and_tier():
    e = Evidence(claim_text="x", url="https://a.com", title="A", tier=SourceTier.T2)
    assert e.tier == SourceTier.T2

def test_claim_rejects_missing_data():
    with pytest.raises(ValidationError):
        Claim(statement="UBI helps", data=[], insight="i", bias_note="b",
              confidence=Confidence.LOW)

def test_claim_requires_bias_note():
    e = Evidence(claim_text="x", url="https://a.com", title="A", tier=SourceTier.T1)
    with pytest.raises(ValidationError):
        Claim(statement="s", data=[e], insight="i", bias_note="",
              confidence=Confidence.HIGH)

def test_case_normalized_fields():
    c = Case(location="Finland", start_date="2017", end_date="2018", scale="2000 people",
             funding_model="govt", target_population="unemployed",
             outcome_metric="employment rate", result="no sig change",
             tier=SourceTier.T1, source_urls=["https://k.fi"])
    assert c.location == "Finland"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_contracts.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'evaluate.contracts'`

- [ ] **Step 3: Write `evaluate/contracts.py`**

```python
from enum import IntEnum, Enum
from pydantic import BaseModel, Field, field_validator

class SourceTier(IntEnum):
    T1 = 1  # primary data / official statistics
    T2 = 2  # peer-reviewed
    T3 = 3  # reputable secondary
    T4 = 4  # advocacy / opinion

class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SPECULATIVE = "speculative"

class Lean(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    NEUTRAL = "neutral"

class Evidence(BaseModel):
    claim_text: str            # what this source supports, in our words
    url: str
    title: str
    tier: SourceTier

class Claim(BaseModel):
    statement: str
    data: list[Evidence] = Field(min_length=1)   # >=1 required by contract
    insight: str
    bias_note: str
    confidence: Confidence

    @field_validator("bias_note", "insight", "statement")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be blank")
        return v

class Case(BaseModel):
    location: str
    start_date: str
    end_date: str
    scale: str
    funding_model: str
    target_population: str
    outcome_metric: str
    result: str
    tier: SourceTier
    source_urls: list[str] = Field(min_length=1)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_contracts.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add evaluate/contracts.py tests/test_contracts.py
git commit -m "feat: core Pydantic contracts (Evidence, Claim, Case)"
```

---

## Task 2: Synthesis & verification contracts

**Files:**
- Modify: `evaluate/contracts.py` (append)
- Test: `tests/test_contracts_synthesis.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_contracts_synthesis.py
import pytest
from pydantic import ValidationError
from evaluate.contracts import (
    SpeculationNode, VerificationThread, ConditionalBranch, Verdict,
    SourceTier, Confidence, Lean, Evidence,
)

def test_speculation_node_has_lean():
    n = SpeculationNode(hypothesis="capital flight", lean=Lean.RIGHT,
                        evidence=[], status="unresolved", depth=1)
    assert n.lean == Lean.RIGHT

def test_thread_requires_outcome():
    t = VerificationThread(outcome="GDP dropped", nodes=[])
    assert t.outcome == "GDP dropped"

def test_verdict_requires_strongest_counter():
    with pytest.raises(ValidationError):
        Verdict(bottom_line="bad idea", reasoning="r", strongest_counter="",
                confidence=Confidence.MEDIUM)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_contracts_synthesis.py -v`
Expected: FAIL with `ImportError` for the new names.

- [ ] **Step 3: Append to `evaluate/contracts.py`**

```python
class SpeculationNode(BaseModel):
    hypothesis: str
    lean: Lean
    evidence: list[Evidence]                 # may be empty while unresolved
    status: str                              # "confirmed" | "refuted" | "unresolved"
    depth: int

class VerificationThread(BaseModel):
    outcome: str                             # the observed outcome being explained
    nodes: list[SpeculationNode]
    cut_short: bool = False                  # True if a governor cap stopped it
    cut_short_reason: str | None = None      # "depth_cap" | "budget_cap" | None

class ConditionalBranch(BaseModel):
    condition: str                           # "if you value X and accept tradeoff Y"
    judgment: str                            # "it's defensible" / "it's a bad idea"

class Verdict(BaseModel):
    bottom_line: str
    reasoning: str
    strongest_counter: str                   # the red-team's best attack (required)
    confidence: Confidence

    @field_validator("bottom_line", "reasoning", "strongest_counter")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be blank")
        return v

class Positions(BaseModel):
    pro: list[Claim]
    against: list[Claim]
    inbetween: list[Claim]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_contracts_synthesis.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add evaluate/contracts.py tests/test_contracts_synthesis.py
git commit -m "feat: synthesis & verification contracts"
```

---

## Task 3: LLMClient base + validate-and-retry (the keystone)

**Files:**
- Create: `evaluate/llm/__init__.py`
- Create: `evaluate/llm/base.py`
- Test: `tests/llm/test_base.py`
- Create: `tests/llm/__init__.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/llm/test_base.py
import pytest
from pydantic import BaseModel
from evaluate.llm.base import LLMClient, StructuredCallError

class Toy(BaseModel):
    answer: str

class FakeClient(LLMClient):
    """Returns queued raw strings; lets us test validate-and-retry."""
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []
    def _raw_structured(self, schema, messages, model, **kw):
        self.calls.append(messages)
        return self._responses.pop(0)

def test_returns_validated_instance():
    c = FakeClient(['{"answer": "ok"}'])
    out = c.structured_call(Toy, [{"role": "user", "content": "hi"}], model="m")
    assert isinstance(out, Toy) and out.answer == "ok"

def test_retries_then_succeeds():
    c = FakeClient(['{"bad": 1}', '{"answer": "fixed"}'])
    out = c.structured_call(Toy, [{"role": "user", "content": "hi"}], model="m",
                            max_retries=2)
    assert out.answer == "fixed"
    assert len(c.calls) == 2
    # retry message must include the validation error feedback
    assert "answer" in str(c.calls[1])

def test_raises_after_exhausting_retries():
    c = FakeClient(['{"bad": 1}', '{"bad": 2}'])
    with pytest.raises(StructuredCallError):
        c.structured_call(Toy, [{"role": "user", "content": "hi"}], model="m",
                          max_retries=2)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/llm/test_base.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'evaluate.llm'`

- [ ] **Step 3: Create `evaluate/llm/__init__.py` and `tests/llm/__init__.py` (empty), then write `evaluate/llm/base.py`**

```python
# evaluate/llm/__init__.py  (empty)
```

```python
# evaluate/llm/base.py
from abc import ABC, abstractmethod
import json
from pydantic import BaseModel, ValidationError

class StructuredCallError(RuntimeError):
    pass

class LLMClient(ABC):
    @abstractmethod
    def _raw_structured(self, schema: type[BaseModel], messages: list[dict],
                        model: str, **kwargs) -> str:
        """Provider-specific call. Returns the raw JSON string the model produced."""
        ...

    def structured_call(self, schema: type[BaseModel], messages: list[dict],
                        model: str, max_retries: int = 3, **kwargs) -> BaseModel:
        convo = list(messages)
        last_err = None
        for _ in range(max_retries):
            raw = self._raw_structured(schema, convo, model, **kwargs)
            try:
                return schema.model_validate_json(raw)
            except ValidationError as e:
                last_err = e
                convo = convo + [
                    {"role": "assistant", "content": raw},
                    {"role": "user", "content":
                        f"Your previous response failed schema validation:\n{e}\n"
                        f"Return ONLY valid JSON matching the schema."},
                ]
        raise StructuredCallError(f"schema validation failed after "
                                  f"{max_retries} attempts: {last_err}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/llm/test_base.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add evaluate/llm/__init__.py tests/llm/__init__.py evaluate/llm/base.py tests/llm/test_base.py
git commit -m "feat: LLMClient base with validate-and-retry (keystone)"
```

---

## Task 4: Provider adapters (OpenAI, DeepSeek, Anthropic)

**Files:**
- Create: `evaluate/llm/openai.py`
- Create: `evaluate/llm/deepseek.py`
- Create: `evaluate/llm/anthropic.py`
- Test: `tests/llm/test_adapters.py`

- [ ] **Step 1: Write the failing tests (SDKs mocked)**

```python
# tests/llm/test_adapters.py
from pydantic import BaseModel
from evaluate.llm.openai import OpenAIClient
from evaluate.llm.anthropic import AnthropicClient

class Toy(BaseModel):
    answer: str

def test_openai_extracts_json_content(mocker):
    fake_msg = mocker.Mock()
    fake_msg.content = '{"answer": "hi"}'
    fake_resp = mocker.Mock()
    fake_resp.choices = [mocker.Mock(message=fake_msg)]
    sdk = mocker.Mock()
    sdk.chat.completions.create.return_value = fake_resp
    c = OpenAIClient(client=sdk)
    out = c.structured_call(Toy, [{"role": "user", "content": "q"}], model="gpt-x")
    assert out.answer == "hi"
    # strict json schema response_format was passed
    kw = sdk.chat.completions.create.call_args.kwargs
    assert kw["response_format"]["type"] == "json_schema"

def test_anthropic_extracts_tool_input(mocker):
    block = mocker.Mock()
    block.type = "tool_use"
    block.input = {"answer": "hi"}
    fake_resp = mocker.Mock()
    fake_resp.content = [block]
    sdk = mocker.Mock()
    sdk.messages.create.return_value = fake_resp
    c = AnthropicClient(client=sdk)
    out = c.structured_call(Toy, [{"role": "user", "content": "q"}], model="claude-x")
    assert out.answer == "hi"
    kw = sdk.messages.create.call_args.kwargs
    assert kw["tool_choice"]["type"] == "tool"   # forced tool use
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/llm/test_adapters.py -v`
Expected: FAIL with import errors for the adapter classes.

- [ ] **Step 3: Write the three adapters**

```python
# evaluate/llm/openai.py
import json
from pydantic import BaseModel
from .base import LLMClient

class OpenAIClient(LLMClient):
    def __init__(self, client=None, api_key=None, base_url=None):
        if client is None:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url=base_url)
        self._c = client

    def _raw_structured(self, schema: type[BaseModel], messages, model, **kw) -> str:
        resp = self._c.chat.completions.create(
            model=model,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {"name": schema.__name__, "strict": True,
                                "schema": schema.model_json_schema()},
            },
        )
        return resp.choices[0].message.content
```

```python
# evaluate/llm/deepseek.py
from .openai import OpenAIClient

class DeepSeekClient(OpenAIClient):
    """DeepSeek is OpenAI-API-compatible; just point at its base_url."""
    def __init__(self, api_key=None, base_url="https://api.deepseek.com", client=None):
        super().__init__(client=client, api_key=api_key, base_url=base_url)
```

```python
# evaluate/llm/anthropic.py
from pydantic import BaseModel
from .base import LLMClient

class AnthropicClient(LLMClient):
    def __init__(self, client=None, api_key=None):
        if client is None:
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
        self._c = client

    def _raw_structured(self, schema: type[BaseModel], messages, model,
                        max_tokens=4096, **kw) -> str:
        import json
        tool = {
            "name": "emit",
            "description": f"Emit a {schema.__name__} object.",
            "input_schema": schema.model_json_schema(),
        }
        resp = self._c.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages,
            tools=[tool],
            tool_choice={"type": "tool", "name": "emit"},
        )
        for block in resp.content:
            if getattr(block, "type", None) == "tool_use":
                return json.dumps(block.input)
        raise RuntimeError("no tool_use block in Anthropic response")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/llm/test_adapters.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add evaluate/llm/openai.py evaluate/llm/deepseek.py evaluate/llm/anthropic.py tests/llm/test_adapters.py
git commit -m "feat: OpenAI/DeepSeek/Anthropic structured-output adapters"
```

---

## Task 5: Config + model-class factory

**Files:**
- Create: `evaluate/config.py`
- Create: `evaluate/llm/factory.py`
- Test: `tests/test_factory.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_factory.py
from evaluate.config import Config, ModelClass, ModelSpec
from evaluate.llm.factory import build_client
from evaluate.llm.openai import OpenAIClient
from evaluate.llm.anthropic import AnthropicClient

def test_config_maps_classes():
    cfg = Config(
        routing={
            ModelClass.LIGHT:  ModelSpec(provider="deepseek", model="deepseek-chat"),
            ModelClass.MEDIUM: ModelSpec(provider="openai",   model="gpt-4o-mini"),
            ModelClass.HEAVY:  ModelSpec(provider="anthropic",model="claude-x"),
        },
        depth_budget=4, max_searches=50,
    )
    assert cfg.routing[ModelClass.HEAVY].provider == "anthropic"

def test_build_client_returns_right_type():
    spec = ModelSpec(provider="anthropic", model="claude-x")
    client, model = build_client(spec, keys={"anthropic": "k"})
    assert isinstance(client, AnthropicClient) and model == "claude-x"
    spec2 = ModelSpec(provider="openai", model="gpt-x")
    client2, _ = build_client(spec2, keys={"openai": "k"})
    assert isinstance(client2, OpenAIClient)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_factory.py -v`
Expected: FAIL with import errors.

- [ ] **Step 3: Write `evaluate/config.py` and `evaluate/llm/factory.py`**

```python
# evaluate/config.py
import os
from enum import Enum
from pydantic import BaseModel

class ModelClass(str, Enum):
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"

class ModelSpec(BaseModel):
    provider: str   # "openai" | "deepseek" | "anthropic"
    model: str

class Config(BaseModel):
    routing: dict[ModelClass, ModelSpec]
    depth_budget: int = 4
    max_searches: int = 50

def load_keys() -> dict[str, str]:
    return {
        "openai": os.environ.get("OPENAI_API_KEY", ""),
        "deepseek": os.environ.get("DEEPSEEK_API_KEY", ""),
        "anthropic": os.environ.get("ANTHROPIC_API_KEY", ""),
        "firecrawl": os.environ.get("FIRECRAWL_API_KEY", ""),
    }
```

```python
# evaluate/llm/factory.py
from ..config import ModelSpec
from .openai import OpenAIClient
from .deepseek import DeepSeekClient
from .anthropic import AnthropicClient

def build_client(spec: ModelSpec, keys: dict[str, str]):
    p = spec.provider
    if p == "openai":
        return OpenAIClient(api_key=keys["openai"]), spec.model
    if p == "deepseek":
        return DeepSeekClient(api_key=keys["deepseek"]), spec.model
    if p == "anthropic":
        return AnthropicClient(api_key=keys["anthropic"]), spec.model
    raise ValueError(f"unknown provider: {p}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_factory.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add evaluate/config.py evaluate/llm/factory.py tests/test_factory.py
git commit -m "feat: config + light/medium/heavy model-class factory"
```

---

## Task 6: SearchClient base + Firecrawl impl

**Files:**
- Create: `evaluate/search/__init__.py`
- Create: `evaluate/search/base.py`
- Create: `evaluate/search/firecrawl.py`
- Create: `tests/search/__init__.py`
- Test: `tests/search/test_firecrawl.py`

- [ ] **Step 1: Write the failing tests (httpx mocked)**

```python
# tests/search/test_firecrawl.py
from evaluate.search.base import SearchResult
from evaluate.search.firecrawl import FirecrawlClient

def test_search_parses_results(mocker):
    http = mocker.Mock()
    resp = mocker.Mock()
    resp.json.return_value = {"data": [
        {"url": "https://a.com", "title": "A", "description": "d"},
    ]}
    resp.raise_for_status = mocker.Mock()
    http.post.return_value = resp
    c = FirecrawlClient(api_key="k", http=http)
    out = c.search("ubi finland", limit=5)
    assert out[0].url == "https://a.com" and isinstance(out[0], SearchResult)

def test_scrape_returns_markdown(mocker):
    http = mocker.Mock()
    resp = mocker.Mock()
    resp.json.return_value = {"data": {"markdown": "# hello"}}
    resp.raise_for_status = mocker.Mock()
    http.post.return_value = resp
    c = FirecrawlClient(api_key="k", http=http)
    md = c.scrape("https://a.com")
    assert md == "# hello"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/search/test_firecrawl.py -v`
Expected: FAIL with import errors.

- [ ] **Step 3: Write base + Firecrawl (create empty `__init__.py` files first)**

```python
# evaluate/search/__init__.py  (empty)
# tests/search/__init__.py     (empty)
```

```python
# evaluate/search/base.py
from abc import ABC, abstractmethod
from pydantic import BaseModel

class SearchResult(BaseModel):
    url: str
    title: str
    snippet: str = ""

class SearchClient(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 10) -> list[SearchResult]: ...
    @abstractmethod
    def scrape(self, url: str) -> str: ...
```

```python
# evaluate/search/firecrawl.py
import httpx
from .base import SearchClient, SearchResult

class FirecrawlClient(SearchClient):
    BASE = "https://api.firecrawl.dev/v1"

    def __init__(self, api_key: str, http=None):
        self._key = api_key
        self._http = http or httpx.Client(timeout=60)

    def _headers(self):
        return {"Authorization": f"Bearer {self._key}"}

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        r = self._http.post(f"{self.BASE}/search",
                            headers=self._headers(),
                            json={"query": query, "limit": limit})
        r.raise_for_status()
        return [SearchResult(url=d["url"], title=d.get("title", ""),
                             snippet=d.get("description", ""))
                for d in r.json().get("data", [])]

    def scrape(self, url: str) -> str:
        r = self._http.post(f"{self.BASE}/scrape",
                            headers=self._headers(),
                            json={"url": url, "formats": ["markdown"]})
        r.raise_for_status()
        return r.json().get("data", {}).get("markdown", "")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/search/test_firecrawl.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add evaluate/search/ tests/search/
git commit -m "feat: SearchClient base + Firecrawl implementation"
```

---

## Task 7: ResearchContext helper (shared stage dependency + search budget)

**Files:**
- Create: `evaluate/stages/__init__.py`
- Create: `evaluate/stages/context.py`
- Create: `tests/stages/__init__.py`
- Test: `tests/stages/test_context.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/stages/test_context.py
import pytest
from evaluate.stages.context import ResearchContext, SearchBudgetExceeded

class FakeSearch:
    def __init__(self): self.n = 0
    def search(self, q, limit=10): self.n += 1; return []
    def scrape(self, url): return "md"

def test_search_increments_and_enforces_budget():
    ctx = ResearchContext(search=FakeSearch(), llm_for=lambda c: (None, "m"),
                          max_searches=2)
    ctx.search("a"); ctx.search("b")
    with pytest.raises(SearchBudgetExceeded):
        ctx.search("c")

def test_searches_used_tracked():
    ctx = ResearchContext(search=FakeSearch(), llm_for=lambda c: (None, "m"),
                          max_searches=5)
    ctx.search("a")
    assert ctx.searches_used == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/stages/test_context.py -v`
Expected: FAIL with import errors.

- [ ] **Step 3: Write context (create empty `__init__.py` files first)**

```python
# evaluate/stages/__init__.py  (empty)
# tests/stages/__init__.py     (empty)
```

```python
# evaluate/stages/context.py
from collections.abc import Callable
from ..config import ModelClass
from ..search.base import SearchClient, SearchResult

class SearchBudgetExceeded(RuntimeError):
    pass

class ResearchContext:
    """Shared dependency passed to every stage: budgeted search + class-routed LLM."""
    def __init__(self, search: SearchClient,
                 llm_for: Callable[[ModelClass], tuple],
                 max_searches: int):
        self._search = search
        self._llm_for = llm_for
        self.max_searches = max_searches
        self.searches_used = 0

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        if self.searches_used >= self.max_searches:
            raise SearchBudgetExceeded(f"budget {self.max_searches} reached")
        self.searches_used += 1
        return self._search.search(query, limit)

    def scrape(self, url: str) -> str:
        return self._search.scrape(url)

    def llm(self, cls: ModelClass):
        """Returns (client, model) for the requested class."""
        return self._llm_for(cls)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/stages/test_context.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add evaluate/stages/__init__.py tests/stages/__init__.py evaluate/stages/context.py tests/stages/test_context.py
git commit -m "feat: ResearchContext with budgeted search + class-routed LLM"
```

---

## Task 8: Positions stage (steel-man pro/against/in-between)

**Files:**
- Create: `evaluate/stages/positions.py`
- Test: `tests/stages/test_positions.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/stages/test_positions.py
from evaluate.contracts import Positions, Claim, Evidence, SourceTier, Confidence
from evaluate.config import ModelClass
from evaluate.stages.positions import map_positions

def _claim(s):
    return Claim(statement=s, data=[Evidence(claim_text="x", url="https://a.com",
                title="A", tier=SourceTier.T2)], insight="i", bias_note="b",
                confidence=Confidence.MEDIUM)

class FakeLLM:
    def structured_call(self, schema, messages, model, **kw):
        return Positions(pro=[_claim("p")], against=[_claim("a")],
                         inbetween=[_claim("m")])

class FakeCtx:
    def __init__(self): self.requested = None
    def llm(self, cls): self.requested = cls; return (FakeLLM(), "model-x")

def test_map_positions_uses_medium_class_and_returns_positions():
    ctx = FakeCtx()
    out = map_positions("UBI", ctx)
    assert isinstance(out, Positions)
    assert out.pro[0].statement == "p"
    assert ctx.requested == ModelClass.MEDIUM
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/stages/test_positions.py -v`
Expected: FAIL with `ImportError` for `map_positions`.

- [ ] **Step 3: Write `evaluate/stages/positions.py`**

```python
# evaluate/stages/positions.py
from ..config import ModelClass
from ..contracts import Positions
from .context import ResearchContext

_SYS = (
    "You are a rigorous, politically-aware policy analyst. For the given idea, "
    "produce curated positions: pro, against, and in-between. STEEL-MAN each side — "
    "state the strongest honest version. Every Claim MUST include: data (>=1 source "
    "with a tier), insight (the so-what), and a bias_note naming who tends to make "
    "this argument and which way it leans. Do not invent sources."
)

def map_positions(topic: str, ctx: ResearchContext) -> Positions:
    client, model = ctx.llm(ModelClass.MEDIUM)
    messages = [
        {"role": "system", "content": _SYS},
        {"role": "user", "content": f"Idea to evaluate: {topic}"},
    ]
    return client.structured_call(Positions, messages, model=model)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/stages/test_positions.py -v`
Expected: 1 passed

- [ ] **Step 5: Commit**

```bash
git add evaluate/stages/positions.py tests/stages/test_positions.py
git commit -m "feat: positions stage (steel-manned pro/against/in-between)"
```

---

## Task 9: Cases stage (real-world instances → normalized ledger)

**Files:**
- Create: `evaluate/stages/cases.py`
- Test: `tests/stages/test_cases.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/stages/test_cases.py
from evaluate.contracts import Case, SourceTier
from evaluate.config import ModelClass
from evaluate.stages.cases import find_cases, CaseList

class FakeLLM:
    def structured_call(self, schema, messages, model, **kw):
        return CaseList(cases=[Case(
            location="Finland", start_date="2017", end_date="2018",
            scale="2000", funding_model="govt", target_population="unemployed",
            outcome_metric="employment", result="no sig change",
            tier=SourceTier.T1, source_urls=["https://k.fi"])])

class FakeCtx:
    def __init__(self): self.requested=None; self.searched=[]
    def llm(self, cls): self.requested=cls; return (FakeLLM(), "m")
    def search(self, q, limit=10): self.searched.append(q); return []
    def scrape(self, url): return "md"

def test_find_cases_returns_normalized_cases_via_medium():
    ctx = FakeCtx()
    out = find_cases("UBI", ctx)
    assert out[0].location == "Finland"
    assert ctx.requested == ModelClass.MEDIUM
    assert ctx.searched  # it performed at least one search
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/stages/test_cases.py -v`
Expected: FAIL with import errors.

- [ ] **Step 3: Write `evaluate/stages/cases.py`**

```python
# evaluate/stages/cases.py
from pydantic import BaseModel
from ..config import ModelClass
from ..contracts import Case
from .context import ResearchContext

class CaseList(BaseModel):
    cases: list[Case]

_SYS = (
    "Extract real-world instances where the idea was actually tried. For EACH instance "
    "fill the SAME normalized fields (location, dates, scale, funding_model, "
    "target_population, outcome_metric, result, tier, source_urls). Use only the "
    "provided search material; do not invent instances or sources. If a field is "
    "unknown, say 'unknown' — never fabricate."
)

def find_cases(topic: str, ctx: ResearchContext) -> list[Case]:
    hits = ctx.search(f"{topic} pilot OR experiment OR trial real-world outcomes", limit=10)
    corpus = []
    for h in hits[:5]:
        corpus.append(f"## {h.title}\n{h.url}\n{ctx.scrape(h.url)[:4000]}")
    client, model = ctx.llm(ModelClass.MEDIUM)
    messages = [
        {"role": "system", "content": _SYS},
        {"role": "user", "content": f"Idea: {topic}\n\nSearch material:\n" +
                                    "\n\n".join(corpus)},
    ]
    return client.structured_call(CaseList, messages, model=model).cases
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/stages/test_cases.py -v`
Expected: 1 passed

- [ ] **Step 5: Commit**

```bash
git add evaluate/stages/cases.py tests/stages/test_cases.py
git commit -m "feat: cases stage (normalized real-world ledger)"
```

---

## Task 10: Verify stage — governed recursive causal verification

**Files:**
- Create: `evaluate/stages/verify.py`
- Test: `tests/stages/test_verify.py`

- [ ] **Step 1: Write the failing tests (governor is the focus)**

```python
# tests/stages/test_verify.py
from evaluate.contracts import VerificationThread, SpeculationNode, Lean, Evidence, SourceTier
from evaluate.config import ModelClass
from evaluate.stages.verify import verify_outcome, ProbeResult

class ScriptedLLM:
    """Always returns an unresolved node with two child hypotheses -> forces recursion."""
    def structured_call(self, schema, messages, model, **kw):
        return ProbeResult(
            status="unresolved",
            evidence=[],
            next_hypotheses=["deeper cause A", "deeper cause B"],
        )

class FakeCtx:
    def llm(self, cls): return (ScriptedLLM(), "m")
    def search(self, q, limit=10): return []
    def scrape(self, url): return "md"

def test_depth_cap_stops_recursion_and_labels_cut_short():
    ctx = FakeCtx()
    thread = verify_outcome("GDP dropped", topic="UBI", ctx=ctx, depth_budget=2)
    assert isinstance(thread, VerificationThread)
    assert thread.cut_short is True
    assert thread.cut_short_reason == "depth_cap"
    # max node depth never exceeds the budget
    assert max(n.depth for n in thread.nodes) <= 2

def test_generates_left_and_right_reads_at_first_layer():
    ctx = FakeCtx()
    thread = verify_outcome("GDP dropped", topic="UBI", ctx=ctx, depth_budget=1)
    leans = {n.lean for n in thread.nodes if n.depth == 1}
    assert Lean.LEFT in leans and Lean.RIGHT in leans
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/stages/test_verify.py -v`
Expected: FAIL with import errors.

- [ ] **Step 3: Write `evaluate/stages/verify.py`**

```python
# evaluate/stages/verify.py
from pydantic import BaseModel
from ..config import ModelClass
from ..contracts import VerificationThread, SpeculationNode, Lean, Evidence, SourceTier
from .context import ResearchContext, SearchBudgetExceeded

class ProbeResult(BaseModel):
    status: str                      # "confirmed" | "refuted" | "unresolved"
    evidence: list[Evidence]
    next_hypotheses: list[str]       # deeper causes to chase if unresolved

_SYS = (
    "You investigate WHY an outcome occurred, using only provided search material. "
    "Decide status: 'confirmed' (data supports the hypothesis), 'refuted' (data "
    "contradicts it), or 'unresolved'. Attach any supporting Evidence with tiers. "
    "If unresolved and a deeper cause is plausible, list next_hypotheses to chase. "
    "Never invent sources; absence of data => unresolved, not confirmed."
)

def _probe(hypothesis: str, topic: str, lean: Lean, depth: int,
           ctx: ResearchContext) -> tuple[SpeculationNode, list[str]]:
    try:
        hits = ctx.search(f"{topic} {hypothesis} data evidence", limit=6)
        corpus = "\n\n".join(f"{h.title} {h.url}\n{ctx.scrape(h.url)[:3000]}"
                             for h in hits[:3])
    except SearchBudgetExceeded:
        corpus = ""
    client, model = ctx.llm(ModelClass.MEDIUM)
    res = client.structured_call(ProbeResult, [
        {"role": "system", "content": _SYS},
        {"role": "user", "content": f"Outcome topic: {topic}\nHypothesis: {hypothesis}\n"
                                    f"Search material:\n{corpus or '(none available)'}"},
    ], model=model)
    node = SpeculationNode(hypothesis=hypothesis, lean=lean, evidence=res.evidence,
                           status=res.status, depth=depth)
    children = res.next_hypotheses if res.status == "unresolved" else []
    return node, children

def verify_outcome(outcome: str, topic: str, ctx: ResearchContext,
                   depth_budget: int) -> VerificationThread:
    """Generate left/right reads of an outcome and recurse, governed by depth + budget."""
    nodes: list[SpeculationNode] = []
    cut_short = False
    cut_reason = None

    # Seed layer: a left-leaning read and a right-leaning read.
    frontier = [(f"{outcome}: left-leaning explanation", Lean.LEFT, 1),
                (f"{outcome}: right-leaning explanation", Lean.RIGHT, 1)]

    while frontier:
        hypothesis, lean, depth = frontier.pop(0)
        if depth > depth_budget:
            cut_short = True
            cut_reason = "depth_cap"
            continue
        try:
            node, children = _probe(hypothesis, topic, lean, depth, ctx)
        except SearchBudgetExceeded:
            cut_short = True
            cut_reason = "budget_cap"
            break
        nodes.append(node)
        if children and depth + 1 > depth_budget:
            cut_short = True
            cut_reason = "depth_cap"
        for child in children:
            frontier.append((child, lean, depth + 1))

    return VerificationThread(outcome=outcome, nodes=nodes,
                              cut_short=cut_short, cut_short_reason=cut_reason)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/stages/test_verify.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add evaluate/stages/verify.py tests/stages/test_verify.py
git commit -m "feat: governed recursive causal verification (depth+budget governor)"
```

---

## Task 11: Policy stage (existing-policy survey)

**Files:**
- Create: `evaluate/stages/policy.py`
- Test: `tests/stages/test_policy.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/stages/test_policy.py
from evaluate.contracts import Claim, Evidence, SourceTier, Confidence
from evaluate.config import ModelClass
from evaluate.stages.policy import survey_policy, PolicyClaims

def _claim(s):
    return Claim(statement=s, data=[Evidence(claim_text="x", url="https://g.gov",
                title="G", tier=SourceTier.T1)], insight="i", bias_note="b",
                confidence=Confidence.HIGH)

class FakeLLM:
    def structured_call(self, schema, messages, model, **kw):
        return PolicyClaims(claims=[_claim("existing law X")])

class FakeCtx:
    def __init__(self): self.requested=None
    def llm(self, cls): self.requested=cls; return (FakeLLM(), "m")
    def search(self, q, limit=10): return []
    def scrape(self, url): return "md"

def test_survey_policy_returns_claims_via_medium():
    ctx = FakeCtx()
    out = survey_policy("UBI", ctx)
    assert out[0].statement == "existing law X"
    assert ctx.requested == ModelClass.MEDIUM
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/stages/test_policy.py -v`
Expected: FAIL with import errors.

- [ ] **Step 3: Write `evaluate/stages/policy.py`**

```python
# evaluate/stages/policy.py
from pydantic import BaseModel
from ..config import ModelClass
from ..contracts import Claim
from .context import ResearchContext

class PolicyClaims(BaseModel):
    claims: list[Claim]

_SYS = (
    "Survey the EXISTING policy landscape around the idea: current laws, active "
    "proposals, regulatory posture, and jurisdictional differences. Each Claim needs "
    "data (tiered sources), insight, and a bias_note. Prefer primary/government "
    "sources (T1). Do not invent policy that does not exist."
)

def survey_policy(topic: str, ctx: ResearchContext) -> list[Claim]:
    hits = ctx.search(f"{topic} policy law legislation proposal government", limit=8)
    corpus = "\n\n".join(f"{h.title} {h.url}\n{ctx.scrape(h.url)[:3500]}"
                         for h in hits[:4])
    client, model = ctx.llm(ModelClass.MEDIUM)
    return client.structured_call(PolicyClaims, [
        {"role": "system", "content": _SYS},
        {"role": "user", "content": f"Idea: {topic}\n\nSearch material:\n{corpus}"},
    ], model=model).claims
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/stages/test_policy.py -v`
Expected: 1 passed

- [ ] **Step 5: Commit**

```bash
git add evaluate/stages/policy.py tests/stages/test_policy.py
git commit -m "feat: policy-landscape survey stage"
```

---

## Task 12: Synthesize stage (conditional framework + blunt verdict)

**Files:**
- Create: `evaluate/stages/synthesize.py`
- Test: `tests/stages/test_synthesize.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/stages/test_synthesize.py
from evaluate.contracts import (Positions, Case, VerificationThread, Claim, Evidence,
                                 SourceTier, Confidence, Verdict, ConditionalBranch)
from evaluate.config import ModelClass
from evaluate.stages.synthesize import synthesize, Synthesis

def _claim(s):
    return Claim(statement=s, data=[Evidence(claim_text="x", url="https://a.com",
                title="A", tier=SourceTier.T2)], insight="i", bias_note="b",
                confidence=Confidence.MEDIUM)

class FakeLLM:
    def structured_call(self, schema, messages, model, **kw):
        return Synthesis(
            framework=[ConditionalBranch(condition="if you value X", judgment="defensible")],
            verdict=Verdict(bottom_line="narrow version is defensible", reasoning="r",
                            strongest_counter="fiscal cost", confidence=Confidence.MEDIUM))

class FakeCtx:
    def __init__(self): self.requested=None
    def llm(self, cls): self.requested=cls; return (FakeLLM(), "m")

def test_synthesize_uses_heavy_and_returns_framework_and_verdict():
    ctx = FakeCtx()
    pos = Positions(pro=[_claim("p")], against=[_claim("a")], inbetween=[])
    out = synthesize("UBI", pos, cases=[], threads=[], policy=[_claim("law")], ctx=ctx)
    assert isinstance(out, Synthesis)
    assert out.verdict.strongest_counter == "fiscal cost"
    assert out.framework[0].condition == "if you value X"
    assert ctx.requested == ModelClass.HEAVY
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/stages/test_synthesize.py -v`
Expected: FAIL with import errors.

- [ ] **Step 3: Write `evaluate/stages/synthesize.py`**

```python
# evaluate/stages/synthesize.py
from pydantic import BaseModel
from ..config import ModelClass
from ..contracts import (Positions, Case, VerificationThread, Claim,
                         Verdict, ConditionalBranch)
from .context import ResearchContext

class Synthesis(BaseModel):
    framework: list[ConditionalBranch]   # value-neutral tradeoffs
    verdict: Verdict                     # the blunt bottom line

_SYS = (
    "You are a blunt, pragmatic analyst. Using ONLY the supplied positions, case "
    "ledger, verification threads, and policy survey, produce TWO layers, kept "
    "strictly separate:\n"
    "1) framework: value-neutral conditional branches ('it's a good idea IF you value "
    "X and accept tradeoff Y; a bad idea IF your priority is Z').\n"
    "2) verdict: a decisive bottom_line with reasoning, plus the single strongest "
    "counter-argument to your own call. Reference real cases ('tried in N, succeeded "
    "in M because...'). Be honest about uncertainty; do not let opinion contaminate "
    "the value-neutral framework."
)

def _serialize(pos, cases, threads, policy) -> str:
    return (f"POSITIONS:\n{pos.model_dump_json(indent=2)}\n\n"
            f"CASES:\n{[c.model_dump() for c in cases]}\n\n"
            f"THREADS:\n{[t.model_dump() for t in threads]}\n\n"
            f"POLICY:\n{[c.model_dump() for c in policy]}")

def synthesize(topic: str, positions: Positions, cases: list[Case],
               threads: list[VerificationThread], policy: list[Claim],
               ctx: ResearchContext) -> Synthesis:
    client, model = ctx.llm(ModelClass.HEAVY)
    return client.structured_call(Synthesis, [
        {"role": "system", "content": _SYS},
        {"role": "user", "content": f"Idea: {topic}\n\n" +
                                    _serialize(positions, cases, threads, policy)},
    ], model=model)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/stages/test_synthesize.py -v`
Expected: 1 passed

- [ ] **Step 5: Commit**

```bash
git add evaluate/stages/synthesize.py tests/stages/test_synthesize.py
git commit -m "feat: synthesis stage (conditional framework + blunt verdict)"
```

---

## Task 13: Red-team stage (adversarial attack on the verdict)

**Files:**
- Create: `evaluate/stages/redteam.py`
- Test: `tests/stages/test_redteam.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/stages/test_redteam.py
from evaluate.contracts import Verdict, Confidence
from evaluate.config import ModelClass
from evaluate.stages.redteam import red_team

class FakeLLM:
    def structured_call(self, schema, messages, model, **kw):
        # returns a revised verdict with a sharpened counter
        return Verdict(bottom_line="revised: defensible only at small scale",
                       reasoning="after attack", strongest_counter="selection bias in pilots",
                       confidence=Confidence.LOW)

class FakeCtx:
    def __init__(self): self.requested=None
    def llm(self, cls): self.requested=cls; return (FakeLLM(), "m")

def test_red_team_returns_revised_verdict_via_heavy():
    ctx = FakeCtx()
    original = Verdict(bottom_line="defensible", reasoning="r",
                       strongest_counter="cost", confidence=Confidence.MEDIUM)
    out = red_team("UBI", original, ctx)
    assert out.strongest_counter == "selection bias in pilots"
    assert ctx.requested == ModelClass.HEAVY
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/stages/test_redteam.py -v`
Expected: FAIL with import errors.

- [ ] **Step 3: Write `evaluate/stages/redteam.py`**

```python
# evaluate/stages/redteam.py
from ..config import ModelClass
from ..contracts import Verdict
from .context import ResearchContext

_SYS = (
    "You are an adversarial red-team. Attack the given verdict as hard as you honestly "
    "can: find its weakest assumption, the strongest counter-evidence, and any smuggled "
    "bias. Then return a REVISED Verdict — either defended (unchanged bottom_line with a "
    "sharper strongest_counter and possibly lower confidence) or corrected if the attack "
    "succeeds. The strongest_counter field must hold the best surviving objection."
)

def red_team(topic: str, verdict: Verdict, ctx: ResearchContext) -> Verdict:
    client, model = ctx.llm(ModelClass.HEAVY)
    return client.structured_call(Verdict, [
        {"role": "system", "content": _SYS},
        {"role": "user", "content": f"Idea: {topic}\n\nVerdict to attack:\n"
                                    f"{verdict.model_dump_json(indent=2)}"},
    ], model=model)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/stages/test_redteam.py -v`
Expected: 1 passed

- [ ] **Step 5: Commit**

```bash
git add evaluate/stages/redteam.py tests/stages/test_redteam.py
git commit -m "feat: adversarial red-team stage"
```

---

## Task 14: RunResult model + JSON store

**Files:**
- Create: `evaluate/store.py`
- Test: `tests/test_store.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_store.py
import json
from evaluate.contracts import (Positions, Verdict, ConditionalBranch, Confidence,
                                 Claim, Evidence, SourceTier)
from evaluate.store import RunResult, save_run

def _claim(s):
    return Claim(statement=s, data=[Evidence(claim_text="x", url="https://a.com",
                title="A", tier=SourceTier.T2)], insight="i", bias_note="b",
                confidence=Confidence.MEDIUM)

def test_save_run_writes_valid_json(tmp_path):
    rr = RunResult(
        topic="UBI",
        positions=Positions(pro=[_claim("p")], against=[], inbetween=[]),
        cases=[], threads=[], policy=[],
        framework=[ConditionalBranch(condition="c", judgment="j")],
        verdict=Verdict(bottom_line="b", reasoning="r", strongest_counter="s",
                        confidence=Confidence.LOW),
        searches_used=3,
    )
    p = tmp_path / "run.json"
    save_run(rr, p)
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["topic"] == "UBI"
    assert data["searches_used"] == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_store.py -v`
Expected: FAIL with import errors.

- [ ] **Step 3: Write `evaluate/store.py`**

```python
# evaluate/store.py
from pathlib import Path
from pydantic import BaseModel
from .contracts import (Positions, Case, VerificationThread, Claim,
                        ConditionalBranch, Verdict)

class RunResult(BaseModel):
    topic: str
    positions: Positions
    cases: list[Case]
    threads: list[VerificationThread]
    policy: list[Claim]
    framework: list[ConditionalBranch]
    verdict: Verdict
    searches_used: int

def save_run(result: RunResult, path: Path) -> None:
    Path(path).write_text(result.model_dump_json(indent=2), encoding="utf-8")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_store.py -v`
Expected: 1 passed

- [ ] **Step 5: Commit**

```bash
git add evaluate/store.py tests/test_store.py
git commit -m "feat: RunResult model + JSON store"
```

---

## Task 15: Render — formal Markdown + chat C-layer

**Files:**
- Create: `evaluate/render/__init__.py`
- Create: `evaluate/render/formal.py`
- Create: `evaluate/render/chat.py`
- Create: `tests/render/__init__.py`
- Test: `tests/render/test_render.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/render/test_render.py
from evaluate.contracts import (Positions, Case, VerificationThread, SpeculationNode,
    Lean, Claim, Evidence, SourceTier, Confidence, ConditionalBranch, Verdict)
from evaluate.store import RunResult
from evaluate.render.formal import render_formal
from evaluate.render.chat import render_chat

def _claim(s, tier=SourceTier.T2):
    return Claim(statement=s, data=[Evidence(claim_text="x", url="https://a.com",
                title="Src A", tier=tier)], insight="because Y", bias_note="left-cited",
                confidence=Confidence.MEDIUM)

def _result():
    return RunResult(
        topic="UBI",
        positions=Positions(pro=[_claim("helps poverty")], against=[_claim("costs too much")],
                            inbetween=[]),
        cases=[Case(location="Finland", start_date="2017", end_date="2018", scale="2000",
                    funding_model="govt", target_population="unemployed",
                    outcome_metric="employment", result="no sig change",
                    tier=SourceTier.T1, source_urls=["https://k.fi"])],
        threads=[VerificationThread(outcome="GDP dipped",
                 nodes=[SpeculationNode(hypothesis="capital flight", lean=Lean.RIGHT,
                        evidence=[], status="unresolved", depth=1)],
                 cut_short=True, cut_short_reason="depth_cap")],
        policy=[_claim("no federal UBI law", SourceTier.T1)],
        framework=[ConditionalBranch(condition="if you prioritize poverty reduction",
                                     judgment="defensible at small scale")],
        verdict=Verdict(bottom_line="narrow UBI is defensible; universal is not",
                        reasoning="cost scaling", strongest_counter="pilot selection bias",
                        confidence=Confidence.MEDIUM),
        searches_used=12)

def test_formal_includes_sections_links_tiers_and_cutshort_label():
    md = render_formal(_result())
    assert "# UBI" in md or "# Evaluation: UBI" in md
    assert "## Case Ledger" in md
    assert "| Finland |" in md                       # ledger table row
    assert "[Src A](https://a.com)" in md            # inline citation link
    assert "[T1]" in md or "T1" in md                # tier annotated
    assert "## References" in md
    assert "unresolved" in md.lower()                # cut-short thread labeled
    assert "## Verdict" in md
    assert "pilot selection bias" in md              # red-teamed counter present

def test_chat_is_c_layer_only_framework_plus_verdict():
    txt = render_chat(_result())
    assert "narrow UBI is defensible" in txt         # bottom line
    assert "if you prioritize poverty reduction" in txt   # framework
    # C-layer points to the file rather than dumping the ledger
    assert "Finland" not in txt
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/render/test_render.py -v`
Expected: FAIL with import errors.

- [ ] **Step 3: Write render modules (create empty `__init__.py` files first)**

```python
# evaluate/render/__init__.py   (empty)
# tests/render/__init__.py      (empty)
```

```python
# evaluate/render/formal.py
from ..store import RunResult
from ..contracts import Claim, Case

def _cite(c: Claim) -> str:
    links = " ".join(f"[{e.title}]({e.url}) [T{int(e.tier)}]" for e in c.data)
    return (f"- **{c.statement}** ({c.confidence.value})\n"
            f"  - _Data:_ {links}\n"
            f"  - _Insight:_ {c.insight}\n"
            f"  - _Bias/lean:_ {c.bias_note}")

def _claims_block(title: str, claims: list[Claim]) -> str:
    if not claims:
        return f"### {title}\n_(none found)_\n"
    return f"### {title}\n" + "\n".join(_cite(c) for c in claims) + "\n"

def _ledger_table(cases: list[Case]) -> str:
    if not cases:
        return "_(no real-world instances found)_\n"
    header = ("| Location | Dates | Scale | Funding | Population | Metric | Result | Tier |\n"
              "|---|---|---|---|---|---|---|---|\n")
    rows = "".join(
        f"| {c.location} | {c.start_date}–{c.end_date} | {c.scale} | {c.funding_model} "
        f"| {c.target_population} | {c.outcome_metric} | {c.result} | T{int(c.tier)} |\n"
        for c in cases)
    return header + rows

def _threads_block(threads) -> str:
    out = []
    for t in threads:
        out.append(f"### Outcome: {t.outcome}")
        for n in t.nodes:
            ev = ", ".join(f"[{e.title}]({e.url}) [T{int(e.tier)}]" for e in n.evidence) \
                 or "_no supporting data_"
            out.append(f"- ({n.lean.value}, depth {n.depth}) **{n.hypothesis}** — "
                       f"status: {n.status}; evidence: {ev}")
        if t.cut_short:
            out.append(f"> ⚠️ **Unresolved — would need deeper investigation** "
                       f"(stopped: {t.cut_short_reason}).")
    return "\n".join(out) + "\n"

def _references(result: RunResult) -> str:
    seen = {}
    for grp in (result.positions.pro, result.positions.against,
                result.positions.inbetween, result.policy):
        for c in grp:
            for e in c.data:
                seen[e.url] = (e.title, int(e.tier))
    for c in result.cases:
        for u in c.source_urls:
            seen.setdefault(u, ("(case source)", int(c.tier)))
    lines = [f"- [{t}]({u}) — T{tier}" for u, (t, tier) in seen.items()]
    return "## References\n" + ("\n".join(lines) if lines else "_(none)_") + "\n"

def render_formal(result: RunResult) -> str:
    r = result
    parts = [
        f"# Evaluation: {r.topic}\n",
        "## Positions\n",
        _claims_block("Pro", r.positions.pro),
        _claims_block("Against", r.positions.against),
        _claims_block("In-between", r.positions.inbetween),
        "## Case Ledger\n", _ledger_table(r.cases),
        "## Causal Verification\n", _threads_block(r.threads),
        "## Existing Policy\n", _claims_block("Policy landscape", r.policy),
        "## Tradeoff Framework\n",
        "\n".join(f"- **{b.condition}** → {b.judgment}" for b in r.framework) + "\n",
        "## Verdict\n",
        f"**Bottom line:** {r.verdict.bottom_line}\n\n"
        f"**Reasoning:** {r.verdict.reasoning}\n\n"
        f"**Strongest counter (red-team):** {r.verdict.strongest_counter}\n\n"
        f"**Confidence:** {r.verdict.confidence.value}\n",
        f"\n_Sources consulted via {r.searches_used} searches._\n",
        _references(r),
    ]
    return "\n".join(parts)
```

```python
# evaluate/render/chat.py
from ..store import RunResult

def render_chat(result: RunResult) -> str:
    r = result
    fw = "\n".join(f"  • {b.condition} → {b.judgment}" for b in r.framework)
    return (
        f"Here's my read on {r.topic}.\n\n"
        f"The tradeoffs, value-neutral:\n{fw}\n\n"
        f"My blunt call: {r.verdict.bottom_line}\n"
        f"Why: {r.verdict.reasoning}\n"
        f"The strongest argument against my call: {r.verdict.strongest_counter}\n"
        f"(Confidence: {r.verdict.confidence.value}.)\n\n"
        f"Full record with the case ledger, citations, and verification chains "
        f"is in the formal file."
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/render/test_render.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add evaluate/render/ tests/render/
git commit -m "feat: formal Markdown + chat C-layer renderers"
```

---

## Task 16: Pipeline orchestrator

**Files:**
- Create: `evaluate/pipeline.py`
- Test: `tests/test_pipeline.py`

- [ ] **Step 1: Write the failing test (all stages mocked via monkeypatch)**

```python
# tests/test_pipeline.py
from evaluate.contracts import (Positions, Case, VerificationThread, SpeculationNode,
    Lean, Claim, Evidence, SourceTier, Confidence, ConditionalBranch, Verdict)
from evaluate.config import Config, ModelClass, ModelSpec
from evaluate.store import RunResult
from evaluate import pipeline as P

def _claim(s):
    return Claim(statement=s, data=[Evidence(claim_text="x", url="https://a.com",
                title="A", tier=SourceTier.T2)], insight="i", bias_note="b",
                confidence=Confidence.MEDIUM)

def test_pipeline_runs_all_stages_and_returns_runresult(monkeypatch):
    monkeypatch.setattr(P, "map_positions",
        lambda topic, ctx: Positions(pro=[_claim("p")], against=[_claim("a")], inbetween=[]))
    monkeypatch.setattr(P, "find_cases",
        lambda topic, ctx: [Case(location="Finland", start_date="2017", end_date="2018",
            scale="2000", funding_model="govt", target_population="unemployed",
            outcome_metric="employment", result="no sig change", tier=SourceTier.T1,
            source_urls=["https://k.fi"])])
    monkeypatch.setattr(P, "verify_outcome",
        lambda outcome, topic, ctx, depth_budget: VerificationThread(outcome=outcome,
            nodes=[SpeculationNode(hypothesis="h", lean=Lean.LEFT, evidence=[],
                   status="unresolved", depth=1)], cut_short=False))
    monkeypatch.setattr(P, "survey_policy", lambda topic, ctx: [_claim("law")])
    from evaluate.stages.synthesize import Synthesis
    monkeypatch.setattr(P, "synthesize",
        lambda topic, positions, cases, threads, policy, ctx: Synthesis(
            framework=[ConditionalBranch(condition="c", judgment="j")],
            verdict=Verdict(bottom_line="bl", reasoning="r", strongest_counter="sc",
                            confidence=Confidence.MEDIUM)))
    monkeypatch.setattr(P, "red_team",
        lambda topic, verdict, ctx: Verdict(bottom_line="bl2", reasoning="r2",
            strongest_counter="sc2", confidence=Confidence.LOW))

    # stub the context builder so no real clients/keys are needed
    class StubCtx:
        searches_used = 7
    monkeypatch.setattr(P, "build_context", lambda cfg, keys: StubCtx())

    cfg = Config(routing={
        ModelClass.LIGHT: ModelSpec(provider="deepseek", model="d"),
        ModelClass.MEDIUM: ModelSpec(provider="openai", model="o"),
        ModelClass.HEAVY: ModelSpec(provider="anthropic", model="c"),
    }, depth_budget=3)

    result = P.run_evaluation("UBI", cfg, keys={})
    assert isinstance(result, RunResult)
    assert result.verdict.bottom_line == "bl2"        # red-teamed verdict wins
    assert result.framework[0].condition == "c"
    assert result.searches_used == 7
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_pipeline.py -v`
Expected: FAIL with `AttributeError`/import errors.

- [ ] **Step 3: Write `evaluate/pipeline.py`**

```python
# evaluate/pipeline.py
from .config import Config, ModelClass
from .llm.factory import build_client
from .search.firecrawl import FirecrawlClient
from .stages.context import ResearchContext
from .stages.positions import map_positions
from .stages.cases import find_cases
from .stages.verify import verify_outcome
from .stages.policy import survey_policy
from .stages.synthesize import synthesize
from .stages.redteam import red_team
from .store import RunResult

def build_context(cfg: Config, keys: dict[str, str]) -> ResearchContext:
    clients = {cls: build_client(spec, keys) for cls, spec in cfg.routing.items()}
    search = FirecrawlClient(api_key=keys.get("firecrawl", ""))
    return ResearchContext(search=search,
                           llm_for=lambda cls: clients[cls],
                           max_searches=cfg.max_searches)

def _outcomes_from_cases(cases) -> list[str]:
    # Each case's measured result is an outcome worth explaining.
    return [f"{c.location}: {c.result}" for c in cases]

def run_evaluation(topic: str, cfg: Config, keys: dict[str, str]) -> RunResult:
    ctx = build_context(cfg, keys)

    positions = map_positions(topic, ctx)
    cases = find_cases(topic, ctx)

    threads = [verify_outcome(o, topic=topic, ctx=ctx, depth_budget=cfg.depth_budget)
               for o in _outcomes_from_cases(cases)]

    policy = survey_policy(topic, ctx)

    synth = synthesize(topic, positions, cases, threads, policy, ctx)
    final_verdict = red_team(topic, synth.verdict, ctx)

    return RunResult(
        topic=topic, positions=positions, cases=cases, threads=threads, policy=policy,
        framework=synth.framework, verdict=final_verdict,
        searches_used=getattr(ctx, "searches_used", 0),
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_pipeline.py -v`
Expected: 1 passed

- [ ] **Step 5: Commit**

```bash
git add evaluate/pipeline.py tests/test_pipeline.py
git commit -m "feat: pipeline orchestrator wiring all stages"
```

---

## Task 17: CLI entry point + default config

**Files:**
- Create: `evaluate/__main__.py`
- Modify: `evaluate/config.py` (add `default_config`)
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_cli.py
from pathlib import Path
from evaluate.config import default_config, ModelClass
from evaluate.__main__ import main
from evaluate.store import RunResult
from evaluate.contracts import (Positions, Verdict, ConditionalBranch, Confidence)
from evaluate import __main__ as M

def test_default_config_has_three_classes():
    cfg = default_config()
    assert set(cfg.routing.keys()) == {ModelClass.LIGHT, ModelClass.MEDIUM, ModelClass.HEAVY}

def test_main_writes_formal_file_and_prints_chat(monkeypatch, tmp_path, capsys):
    rr = RunResult(topic="UBI",
        positions=Positions(pro=[], against=[], inbetween=[]),
        cases=[], threads=[], policy=[],
        framework=[ConditionalBranch(condition="c", judgment="j")],
        verdict=Verdict(bottom_line="my call", reasoning="r", strongest_counter="s",
                        confidence=Confidence.LOW), searches_used=0)
    monkeypatch.setattr(M, "run_evaluation", lambda topic, cfg, keys: rr)
    monkeypatch.setattr(M, "load_keys", lambda: {})
    out_dir = tmp_path
    code = main(["UBI", "--out-dir", str(out_dir)])
    assert code == 0
    files = list(out_dir.glob("*.md"))
    assert len(files) == 1 and "UBI" in files[0].read_text(encoding="utf-8")
    captured = capsys.readouterr()
    assert "my call" in captured.out                  # chat C-layer printed
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_cli.py -v`
Expected: FAIL with import errors.

- [ ] **Step 3: Add `default_config` to `evaluate/config.py`**

```python
# append to evaluate/config.py
def default_config() -> "Config":
    return Config(routing={
        ModelClass.LIGHT:  ModelSpec(provider="deepseek",  model="deepseek-chat"),
        ModelClass.MEDIUM: ModelSpec(provider="openai",    model="gpt-4o-mini"),
        ModelClass.HEAVY:  ModelSpec(provider="anthropic", model="claude-3-5-sonnet-latest"),
    })
```

- [ ] **Step 4: Write `evaluate/__main__.py`**

```python
# evaluate/__main__.py
import argparse
import re
import sys
from pathlib import Path
from .config import default_config, load_keys
from .pipeline import run_evaluation
from .store import save_run
from .render.formal import render_formal
from .render.chat import render_chat

def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="evaluate",
                                 description="Idea Evaluation Engine")
    ap.add_argument("topic", help="the idea/policy to evaluate")
    ap.add_argument("--out-dir", default=".", help="where to write the formal file")
    ap.add_argument("--depth", type=int, default=None, help="causal recursion depth budget")
    ap.add_argument("--max-searches", type=int, default=None)
    args = ap.parse_args(argv)

    cfg = default_config()
    if args.depth is not None:
        cfg.depth_budget = args.depth
    if args.max_searches is not None:
        cfg.max_searches = args.max_searches

    keys = load_keys()
    result = run_evaluation(args.topic, cfg, keys)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    formal_path = out_dir / f"{_slug(args.topic)}-evaluation.md"
    formal_path.write_text(render_formal(result), encoding="utf-8")
    save_run(result, out_dir / f"{_slug(args.topic)}-run.json")

    print(render_chat(result))
    print(f"\n[formal file: {formal_path}]")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_cli.py -v`
Expected: 2 passed

- [ ] **Step 6: Run the full suite**

Run: `pytest -v`
Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add evaluate/__main__.py evaluate/config.py tests/test_cli.py
git commit -m "feat: CLI entry point + default light/medium/heavy config"
```

---

## Task 18: README + live smoke run (manual, key-gated)

**Files:**
- Create: `README.md`
- Test: manual

- [ ] **Step 1: Write `README.md`**

````markdown
# Idea Evaluation Engine

Provider-agnostic Python harness that evaluates an idea/policy and produces a rigorous,
blunt, pragmatic report. Every claim follows **Data → Insight → Acknowledged bias**;
sources are tiered (T1 primary → T4 opinion); real-world cases are normalized into a
ledger; causal "why" threads are verified recursively under a depth+budget governor.

## Setup
```bash
pip install -e ".[dev]"
cp .env.example .env   # fill in ANTHROPIC/OPENAI/DEEPSEEK/FIRECRAWL keys
```

## Run
```bash
python -m evaluate "Universal Basic Income" --out-dir ./reports --depth 4
```
Outputs: a formal Markdown file + a JSON run record in `--out-dir`, and a conversational
synthesis to stdout.

## Model routing
Stages declare a class (light/medium/heavy); `evaluate/config.py` maps each class to a
(provider, model). Edit `default_config()` to retune.

## Tests
```bash
pytest -v
```
````

- [ ] **Step 2: Commit the README**

```bash
git add README.md
git commit -m "docs: README with setup, run, routing"
```

- [ ] **Step 3: Live smoke run (manual — requires real API keys)**

Run (with `.env` populated):
`python -m evaluate "Universal Basic Income" --out-dir ./reports --depth 2 --max-searches 12`

Expected:
- A `reports/universal-basic-income-evaluation.md` is produced with Positions, a Case
  Ledger table, Causal Verification (any cut-short thread labeled "unresolved"),
  Existing Policy, Tradeoff Framework, Verdict (with a red-teamed strongest counter),
  and a References list with tier annotations.
- A conversational synthesis (framework + blunt call) printed to stdout.

Verify the honesty guarantees by inspection:
- No claim lacks a source link + tier.
- Any thread stopped by a cap shows the "unresolved — would need deeper investigation" note.

- [ ] **Step 4: Commit any fixes found during smoke run**

```bash
git add -A
git commit -m "fix: issues found during live smoke run"
```

---

## Self-Review Notes (coverage against spec)

- **§3.1 Claim contract** → Task 1 (`Claim` requires ≥1 `Evidence`, non-blank `bias_note`).
- **§3.2 Tiered sourcing** → Task 1 (`SourceTier`), surfaced in render Task 15 (inline + References).
- **§3.3 Case ledger (struct internally, prose externally)** → Task 1 (`Case`), Task 9 (fill), Task 15 (`_ledger_table`).
- **§3.4 Governed recursion (depth + confidence + budget, labeled cut-short)** → Task 7 (search budget), Task 10 (depth cap + confidence-stop via `status`, `cut_short` labeling), Task 16 (depth_budget wired from config).
- **§4.1 LLM adapter + validate-retry** → Task 3 (keystone), Task 4 (three providers).
- **§4.2 Search layer (Firecrawl, swappable)** → Task 6.
- **§4.3 light/medium/heavy routing** → Task 5 (factory), Task 17 (default_config); stages request classes in Tasks 8–13.
- **§5 Pipeline / parallel-able fan-out** → Task 16 (sequential wiring; per-outcome threads are independent and can be parallelized later without interface change).
- **§6 Two artifacts** → Task 15 (formal + chat), Task 17 (CLI writes file + prints chat).
- **§7 Error handling / honesty** → Task 3 (retry then hard-fail), Task 7 (`SearchBudgetExceeded`), Task 10 (no-data ⇒ unresolved, labeled).
- **§8 Testing** → every task is TDD; Task 16 end-to-end; Task 18 live smoke.
- **§9 Stack** → Task 0.

**Type-consistency check:** `structured_call(schema, messages, model, ...)`, `ctx.llm(cls) -> (client, model)`, `ctx.search/scrape`, `verify_outcome(outcome, topic, ctx, depth_budget)`, `Synthesis(framework, verdict)`, `RunResult(...)` — names match across Tasks 3–17. No undefined references.

**Known deferrals (per spec §5/§10, not gaps):** parallel fan-out is wired sequentially (interfaces allow drop-in `concurrent.futures` later); cross-session memory is out of scope for v1.
