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
    assert ctx.searched
