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
