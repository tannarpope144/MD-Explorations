from ..store import RunResult


def render_chat(result: RunResult) -> str:
    r = result
    fw = "\n".join(f"  • {b.condition} → {b.judgment}" for b in r.framework)
    return (
        f"Here's my read on {r.topic}.\n\n"
        f"The tradeoffs, value-neutral:\n{fw}\n\n"
        f"My blunt call: {r.verdict.bottom_line}\n"
        f"Why: {r.verdict.reasoning}\n"
        f"The strongest argument against my call: {r.verdict.strongest_counter}\n"
        f"(Confidence: {r.verdict.confidence.value}.)\n\n"
        f"Full record with the case ledger, citations, and verification chains "
        f"is in the formal file."
    )
