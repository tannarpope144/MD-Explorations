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
