import pytest
from pydantic import ValidationError
from evaluate.contracts import Evidence, Claim, Case, SourceTier, Confidence

def test_evidence_requires_url_and_tier():
    e = Evidence(claim_text="x", url="https://a.com", title="A", tier=SourceTier.T2)
    assert e.tier == SourceTier.T2

def test_claim_rejects_missing_data():
    with pytest.raises(ValidationError):
        Claim(statement="UBI helps", data=[], insight="i", bias_note="b",
              confidence=Confidence.LOW)

def test_claim_requires_bias_note():
    e = Evidence(claim_text="x", url="https://a.com", title="A", tier=SourceTier.T1)
    with pytest.raises(ValidationError):
        Claim(statement="s", data=[e], insight="i", bias_note="",
              confidence=Confidence.HIGH)

def test_case_normalized_fields():
    c = Case(location="Finland", start_date="2017", end_date="2018", scale="2000 people",
             funding_model="govt", target_population="unemployed",
             outcome_metric="employment rate", result="no sig change",
             tier=SourceTier.T1, source_urls=["https://k.fi"])
    assert c.location == "Finland"
