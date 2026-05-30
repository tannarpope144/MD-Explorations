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
    assert "| Finland |" in md
    assert "[Src A](https://a.com)" in md
    assert "[T1]" in md or "T1" in md
    assert "## References" in md
    assert "unresolved" in md.lower()
    assert "## Verdict" in md
    assert "pilot selection bias" in md


def test_chat_is_c_layer_only_framework_plus_verdict():
    txt = render_chat(_result())
    assert "narrow UBI is defensible" in txt
    assert "if you prioritize poverty reduction" in txt
    assert "Finland" not in txt
