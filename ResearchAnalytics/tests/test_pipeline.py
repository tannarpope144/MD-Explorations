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
    assert result.verdict.bottom_line == "bl2"
    assert result.framework[0].condition == "c"
    assert result.searches_used == 7
