from pathlib import Path
from evaluate.config import default_config, ModelClass
from evaluate.__main__ import main
from evaluate.store import RunResult
from evaluate.contracts import (Positions, Verdict, ConditionalBranch, Confidence)
from evaluate import __main__ as M


def test_default_config_has_three_classes():
    cfg = default_config()
    assert set(cfg.routing.keys()) == {ModelClass.LIGHT, ModelClass.MEDIUM, ModelClass.HEAVY}


def test_main_writes_formal_file_and_prints_chat(monkeypatch, tmp_path, capsys):
    rr = RunResult(topic="UBI",
        positions=Positions(pro=[], against=[], inbetween=[]),
        cases=[], threads=[], policy=[],
        framework=[ConditionalBranch(condition="c", judgment="j")],
        verdict=Verdict(bottom_line="my call", reasoning="r", strongest_counter="s",
                        confidence=Confidence.LOW), searches_used=0)
    monkeypatch.setattr(M, "run_evaluation", lambda topic, cfg, keys: rr)
    monkeypatch.setattr(M, "load_keys", lambda: {})
    out_dir = tmp_path
    code = main(["UBI", "--out-dir", str(out_dir)])
    assert code == 0
    formal = out_dir / "ubi" / "evaluation.md"
    assert formal.exists() and "UBI" in formal.read_text(encoding="utf-8")
    captured = capsys.readouterr()
    assert "my call" in captured.out
