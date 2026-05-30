from evaluate.contracts import Evidence, Claim, Case, SourceTier, Confidence
from evaluate.tiering import (tier_for, normalize_evidence, normalize_claim,
                              normalize_case)


def test_known_domain_overrides_model_tier():
    # Model wrongly tagged Wikipedia T1; the domain rule corrects it to T3.
    assert tier_for("https://en.wikipedia.org/wiki/UBI", SourceTier.T1) == SourceTier.T3
    # Guardian must resolve to a single tier regardless of the model's guess.
    assert tier_for("https://www.theguardian.com/x", SourceTier.T1) == SourceTier.T3
    assert tier_for("https://www.theguardian.com/x", SourceTier.T2) == SourceTier.T3


def test_gov_is_t1():
    assert tier_for("https://www.congress.gov/crs-product/IF10865", SourceTier.T4) == SourceTier.T1
    assert tier_for("https://www.london.gov.uk/report.pdf", SourceTier.T3) == SourceTier.T1


def test_unknown_domain_keeps_model_tier():
    assert tier_for("https://some-unknown-blog.example/x", SourceTier.T2) == SourceTier.T2


def test_normalize_evidence_mutates_in_place():
    ev = [Evidence(claim_text="x", url="https://en.wikipedia.org/p", title="W",
                   tier=SourceTier.T1)]
    normalize_evidence(ev)
    assert ev[0].tier == SourceTier.T3


def test_normalize_claim():
    c = Claim(statement="s",
              data=[Evidence(claim_text="x", url="https://www.cato.org/p", title="C",
                             tier=SourceTier.T2)],
              insight="i", bias_note="b", confidence=Confidence.LOW)
    normalize_claim(c)
    assert c.data[0].tier == SourceTier.T4  # cato is advocacy


def test_normalize_case_takes_strongest_known_tier():
    # One unknown source + one .gov source -> case tier corrected to T1 (strongest).
    c = Case(location="X", start_date="2020", end_date="2021", scale="s",
             funding_model="f", target_population="t", outcome_metric="m",
             result="r", tier=SourceTier.T3,
             source_urls=["https://unknown.example/a", "https://data.gov/b"])
    normalize_case(c)
    assert c.tier == SourceTier.T1


def test_normalize_case_keeps_model_tier_when_all_unknown():
    c = Case(location="X", start_date="2020", end_date="2021", scale="s",
             funding_model="f", target_population="t", outcome_metric="m",
             result="r", tier=SourceTier.T2,
             source_urls=["https://unknown.example/a"])
    normalize_case(c)
    assert c.tier == SourceTier.T2
