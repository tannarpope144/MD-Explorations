from pydantic import BaseModel
from ..config import ModelClass
from ..contracts import Claim
from ..tiering import normalize_claim
from .context import ResearchContext


class PolicyClaims(BaseModel):
    claims: list[Claim]


_SYS = (
    "Survey the EXISTING policy landscape around the idea: current laws, active "
    "proposals, regulatory posture, and jurisdictional differences. Each Claim needs "
    "data (tiered sources), insight, and a bias_note. Prefer primary/government "
    "sources (T1). Do not invent policy that does not exist."
)


def survey_policy(topic: str, ctx: ResearchContext) -> list[Claim]:
    hits = ctx.search(f"{topic} policy law legislation proposal government", limit=8)
    corpus = "\n\n".join(f"{h.title} {h.url}\n{ctx.scrape(h.url)[:3500]}"
                         for h in hits[:4])
    client, model = ctx.llm(ModelClass.MEDIUM)
    claims = client.structured_call(PolicyClaims, [
        {"role": "system", "content": _SYS},
        {"role": "user", "content": f"Idea: {topic}\n\nSearch material:\n{corpus}"},
    ], model=model).claims
    return [normalize_claim(c) for c in claims]
