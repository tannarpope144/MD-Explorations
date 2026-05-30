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
