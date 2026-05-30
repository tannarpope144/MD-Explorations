from pathlib import Path
from pydantic import BaseModel
from .contracts import (Positions, Case, VerificationThread, Claim,
                        ConditionalBranch, Verdict)


class RunResult(BaseModel):
    topic: str
    positions: Positions
    cases: list[Case]
    threads: list[VerificationThread]
    policy: list[Claim]
    framework: list[ConditionalBranch]
    verdict: Verdict
    searches_used: int


def save_run(result: RunResult, path: Path) -> None:
    Path(path).write_text(result.model_dump_json(indent=2), encoding="utf-8")
