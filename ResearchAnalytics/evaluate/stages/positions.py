from ..config import ModelClass
from ..contracts import Positions
from ..tiering import normalize_positions
from .context import ResearchContext

_SYS = (
    "You are a rigorous, politically-aware policy analyst. For the given idea, "
    "produce curated positions: pro, against, and in-between. STEEL-MAN each side — "
    "state the strongest honest version. Every Claim MUST include: data (>=1 source "
    "with a tier), insight (the so-what), and a bias_note naming who tends to make "
    "this argument and which way it leans. Do not invent sources."
)


def map_positions(topic: str, ctx: ResearchContext) -> Positions:
    client, model = ctx.llm(ModelClass.MEDIUM)
    messages = [
        {"role": "system", "content": _SYS},
        {"role": "user", "content": f"Idea to evaluate: {topic}"},
    ]
    return normalize_positions(client.structured_call(Positions, messages, model=model))
