from pydantic import BaseModel
from ..config import ModelClass
from ..contracts import VerificationThread, SpeculationNode, Lean, Evidence, SourceTier
from ..tiering import normalize_evidence
from .context import ResearchContext, SearchBudgetExceeded


def _search_query(topic: str, hypothesis: str) -> str:
    """Build a clean search query from a causal hypothesis.

    Top-level hypotheses arrive as '<outcome>: left-leaning explanation'. The trailing
    '-leaning explanation' boilerplate is search noise, so strip it; the outcome that
    precedes the colon is the thing we actually want to find a cause for. Deeper
    (depth>=2) hypotheses are already concrete causal questions and pass through cleaned.
    """
    h = hypothesis
    for boiler in ("left-leaning explanation", "right-leaning explanation"):
        h = h.replace(boiler, "")
    core = h.strip(" :-") or hypothesis
    return f"{topic} cause explanation {core} data evidence".strip()


def _dedup_evidence(items: list[Evidence]) -> list[Evidence]:
    """Drop repeated URLs within a node (the model often re-cites the same source)."""
    seen: set[str] = set()
    out: list[Evidence] = []
    for e in items:
        if e.url in seen:
            continue
        seen.add(e.url)
        out.append(e)
    return out


class ProbeResult(BaseModel):
    status: str
    evidence: list[Evidence]
    next_hypotheses: list[str]


_SYS = (
    "You investigate WHY an outcome occurred, using only provided search material. "
    "Decide status: 'confirmed' (data supports the hypothesis), 'refuted' (data "
    "contradicts it), or 'unresolved'. Attach any supporting Evidence with tiers. "
    "If unresolved and a deeper cause is plausible, list next_hypotheses to chase. "
    "Never invent sources; absence of data => unresolved, not confirmed."
)


def _probe(hypothesis: str, topic: str, lean: Lean, depth: int,
           ctx: ResearchContext) -> tuple[SpeculationNode, list[str]]:
    try:
        hits = ctx.search(_search_query(topic, hypothesis), limit=6)
        parts = []
        for h in hits[:3]:
            parts.append(f"{h.title} {h.url}\n{ctx.scrape(h.url)[:3000]}")
        corpus = "\n\n".join(parts)
    except SearchBudgetExceeded:
        corpus = ""
    client, model = ctx.llm(ModelClass.MEDIUM)
    res = client.structured_call(ProbeResult, [
        {"role": "system", "content": _SYS},
        {"role": "user", "content": f"Outcome topic: {topic}\nHypothesis: {hypothesis}\n"
                                    f"Search material:\n{corpus or '(none available)'}"},
    ], model=model)
    evidence = _dedup_evidence(normalize_evidence(res.evidence))
    node = SpeculationNode(hypothesis=hypothesis, lean=lean, evidence=evidence,
                           status=res.status, depth=depth)
    children = res.next_hypotheses if res.status == "unresolved" else []
    return node, children


def verify_outcome(outcome: str, topic: str, ctx: ResearchContext,
                   depth_budget: int) -> VerificationThread:
    """Generate left/right reads of an outcome and recurse, governed by depth + budget."""
    nodes: list[SpeculationNode] = []
    cut_short = False
    cut_reason = None

    frontier = [(f"{outcome}: left-leaning explanation", Lean.LEFT, 1),
                (f"{outcome}: right-leaning explanation", Lean.RIGHT, 1)]

    while frontier:
        hypothesis, lean, depth = frontier.pop(0)
        if depth > depth_budget:
            cut_short = True
            cut_reason = "depth_cap"
            continue
        try:
            node, children = _probe(hypothesis, topic, lean, depth, ctx)
        except SearchBudgetExceeded:
            cut_short = True
            cut_reason = "budget_cap"
            break
        nodes.append(node)
        if children and depth + 1 > depth_budget:
            cut_short = True
            cut_reason = "depth_cap"
        for child in children:
            frontier.append((child, lean, depth + 1))

    return VerificationThread(outcome=outcome, nodes=nodes,
                              cut_short=cut_short, cut_short_reason=cut_reason)
