import sys
from .config import Config, ModelClass
from .llm.factory import build_client
from .search.firecrawl import FirecrawlClient
from .search.tavily import TavilyClient
from .stages.context import ResearchContext
from .stages.positions import map_positions
from .stages.cases import find_cases
from .stages.verify import verify_outcome
from .stages.policy import survey_policy
from .stages.synthesize import synthesize
from .stages.redteam import red_team
from .store import RunResult


def _log(msg: str) -> None:
    print(f"[evaluate] {msg}", flush=True)


def build_context(cfg: Config, keys: dict[str, str]) -> ResearchContext:
    clients = {cls: build_client(spec, keys) for cls, spec in cfg.routing.items()}
    if keys.get("tavily"):
        search = TavilyClient(api_key=keys["tavily"])
        _log("search provider: Tavily (+ Jina scraping)")
    else:
        search = FirecrawlClient(api_key=keys.get("firecrawl", ""))
        _log("search provider: Firecrawl")
    return ResearchContext(search=search,
                           llm_for=lambda cls: clients[cls],
                           max_searches=cfg.max_searches)


def _outcomes_from_cases(cases) -> list[str]:
    return [f"{c.location}: {c.result}" for c in cases]


def run_evaluation(topic: str, cfg: Config, keys: dict[str, str]) -> RunResult:
    routing = cfg.routing
    _log(f"starting evaluation: {topic!r}")
    _log(f"model routing — light: {routing[ModelClass.LIGHT].model}, "
         f"medium: {routing[ModelClass.MEDIUM].model}, "
         f"heavy: {routing[ModelClass.HEAVY].model}")

    ctx = build_context(cfg, keys)

    _log("stage 1/6 — positions: steel-manning pro/against/in-between (medium)...")
    positions = map_positions(topic, ctx)
    _log(f"  done: {len(positions.pro)} pro, {len(positions.against)} against, "
         f"{len(positions.inbetween)} in-between")

    _log("stage 2/6 — cases: finding real-world instances (medium + search)...")
    cases = find_cases(topic, ctx)
    _log(f"  done: {len(cases)} cases found (searches used: {ctx.searches_used})")

    outcomes = _outcomes_from_cases(cases)
    _log(f"stage 3/6 — verify: causal verification for {len(outcomes)} outcome(s) "
         f"(medium, depth budget={cfg.depth_budget})...")
    threads = []
    for i, o in enumerate(outcomes, 1):
        _log(f"  verifying outcome {i}/{len(outcomes)}: {o[:60]}...")
        thread = verify_outcome(o, topic=topic, ctx=ctx, depth_budget=cfg.depth_budget)
        status = "cut short" if thread.cut_short else "resolved"
        _log(f"    {len(thread.nodes)} node(s), {status} (searches used: {ctx.searches_used})")
        threads.append(thread)

    _log("stage 4/6 — policy: surveying existing policy landscape (medium + search)...")
    policy = survey_policy(topic, ctx)
    _log(f"  done: {len(policy)} policy claims (searches used: {ctx.searches_used})")

    _log("stage 5/6 — synthesize: building conditional framework + verdict (heavy)...")
    synth = synthesize(topic, positions, cases, threads, policy, ctx)
    _log(f"  done: {len(synth.framework)} framework branch(es)")

    _log("stage 6/6 — red-team: adversarially attacking the verdict (heavy)...")
    final_verdict = red_team(topic, synth.verdict, ctx)
    _log(f"  done: confidence={final_verdict.confidence.value}")

    _log(f"evaluation complete — total searches used: {ctx.searches_used}")

    return RunResult(
        topic=topic, positions=positions, cases=cases, threads=threads, policy=policy,
        framework=synth.framework, verdict=final_verdict,
        searches_used=getattr(ctx, "searches_used", 0),
    )
