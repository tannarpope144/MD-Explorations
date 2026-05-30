from evaluate.contracts import Verdict, Confidence
from evaluate.config import ModelClass
from evaluate.stages.redteam import red_team


class FakeLLM:
    def structured_call(self, schema, messages, model, **kw):
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
