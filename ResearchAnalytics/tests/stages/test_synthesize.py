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
