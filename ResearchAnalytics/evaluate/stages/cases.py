from pydantic import BaseModel
from ..config import ModelClass
from ..contracts import Case
from ..tiering import normalize_case
from .context import ResearchContext


class CaseList(BaseModel):
    cases: list[Case]


_SYS = (
    "Extract real-world instances where the idea was actually tried. For EACH instance "
    "fill the SAME normalized fields (location, dates, scale, funding_model, "
    "target_population, outcome_metric, result, tier, source_urls). Use only the "
    "provided search material; do not invent instances or sources. If a field is "
    "unknown, say 'unknown' — never fabricate."
)


def find_cases(topic: str, ctx: ResearchContext) -> list[Case]:
    hits = ctx.search(f"{topic} pilot OR experiment OR trial real-world outcomes", limit=10)
    corpus = []
    for h in hits[:5]:
        try:
            content = ctx.scrape(h.url)[:4000]
        except Exception:
            content = ""
        corpus.append(f"## {h.title}\n{h.url}\n{content}")
    client, model = ctx.llm(ModelClass.MEDIUM)
    messages = [
        {"role": "system", "content": _SYS},
        {"role": "user", "content": f"Idea: {topic}\n\nSearch material:\n" +
                                    "\n\n".join(corpus)},
    ]
    cases = client.structured_call(CaseList, messages, model=model).cases
    return [normalize_case(c) for c in cases]
