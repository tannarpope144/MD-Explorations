from pydantic import BaseModel
from ..config import ModelClass
from ..contracts import (Positions, Case, VerificationThread, Claim,
                         Verdict, ConditionalBranch)
from .context import ResearchContext


class Synthesis(BaseModel):
    framework: list[ConditionalBranch]
    verdict: Verdict


_SYS = (
    "You are a blunt, pragmatic analyst. Using ONLY the supplied positions, case "
    "ledger, verification threads, and policy survey, produce TWO layers, kept "
    "strictly separate:\n"
    "1) framework: value-neutral conditional branches ('it's a good idea IF you value "
    "X and accept tradeoff Y; a bad idea IF your priority is Z').\n"
    "2) verdict: a decisive bottom_line with reasoning, plus the single strongest "
    "counter-argument to your own call. Reference real cases ('tried in N, succeeded "
    "in M because...'). Be honest about uncertainty; do not let opinion contaminate "
    "the value-neutral framework."
)


def _serialize(pos, cases, threads, policy) -> str:
    return (f"POSITIONS:\n{pos.model_dump_json(indent=2)}\n\n"
            f"CASES:\n{[c.model_dump() for c in cases]}\n\n"
            f"THREADS:\n{[t.model_dump() for t in threads]}\n\n"
            f"POLICY:\n{[c.model_dump() for c in policy]}")


def synthesize(topic: str, positions: Positions, cases: list[Case],
               threads: list[VerificationThread], policy: list[Claim],
               ctx: ResearchContext) -> Synthesis:
    client, model = ctx.llm(ModelClass.HEAVY)
    return client.structured_call(Synthesis, [
        {"role": "system", "content": _SYS},
        {"role": "user", "content": f"Idea: {topic}\n\n" +
                                    _serialize(positions, cases, threads, policy)},
    ], model=model)
