import json
from evaluate.contracts import (Positions, Verdict, ConditionalBranch, Confidence,
                                 Claim, Evidence, SourceTier)
from evaluate.store import RunResult, save_run


def _claim(s):
    return Claim(statement=s, data=[Evidence(claim_text="x", url="https://a.com",
                title="A", tier=SourceTier.T2)], insight="i", bias_note="b",
                confidence=Confidence.MEDIUM)


def test_save_run_writes_valid_json(tmp_path):
    rr = RunResult(
        topic="UBI",
        positions=Positions(pro=[_claim("p")], against=[], inbetween=[]),
        cases=[], threads=[], policy=[],
        framework=[ConditionalBranch(condition="c", judgment="j")],
        verdict=Verdict(bottom_line="b", reasoning="r", strongest_counter="s",
                        confidence=Confidence.LOW),
        searches_used=3,
    )
    p = tmp_path / "run.json"
    save_run(rr, p)
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["topic"] == "UBI"
    assert data["searches_used"] == 3
