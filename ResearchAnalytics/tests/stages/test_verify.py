from evaluate.contracts import VerificationThread, SpeculationNode, Lean, Evidence, SourceTier
from evaluate.config import ModelClass
from evaluate.stages.verify import (verify_outcome, ProbeResult,
                                     _search_query, _dedup_evidence)


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
    assert max(n.depth for n in thread.nodes) <= 2


def test_generates_left_and_right_reads_at_first_layer():
    ctx = FakeCtx()
    thread = verify_outcome("GDP dropped", topic="UBI", ctx=ctx, depth_budget=1)
    leans = {n.lean for n in thread.nodes if n.depth == 1}
    assert Lean.LEFT in leans and Lean.RIGHT in leans


def test_search_query_strips_lean_boilerplate_keeps_outcome():
    q = _search_query("UBI", "GDP dropped: left-leaning explanation")
    assert "left-leaning explanation" not in q  # boilerplate suffix stripped
    assert "GDP dropped" in q                    # the outcome we seek a cause for stays
    assert "UBI" in q


def test_dedup_evidence_drops_repeated_urls():
    e1 = Evidence(claim_text="a", url="https://x.com/1", title="A", tier=SourceTier.T2)
    e2 = Evidence(claim_text="b", url="https://x.com/1", title="A2", tier=SourceTier.T2)
    e3 = Evidence(claim_text="c", url="https://x.com/2", title="B", tier=SourceTier.T2)
    out = _dedup_evidence([e1, e2, e3])
    assert [e.url for e in out] == ["https://x.com/1", "https://x.com/2"]
