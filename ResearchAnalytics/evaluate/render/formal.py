from ..store import RunResult
from ..contracts import Claim, Case


def _cite(c: Claim) -> str:
    links = " ".join(f"[{e.title}]({e.url}) [T{int(e.tier)}]" for e in c.data)
    return (f"- **{c.statement}** ({c.confidence.value})\n"
            f"  - _Data:_ {links}\n"
            f"  - _Insight:_ {c.insight}\n"
            f"  - _Bias/lean:_ {c.bias_note}")


def _claims_block(title: str, claims: list[Claim]) -> str:
    if not claims:
        return f"### {title}\n_(none found)_\n"
    return f"### {title}\n" + "\n".join(_cite(c) for c in claims) + "\n"


def _ledger_table(cases: list[Case]) -> str:
    if not cases:
        return "_(no real-world instances found)_\n"
    header = ("| Location | Dates | Scale | Funding | Population | Metric | Result | Tier |\n"
              "|---|---|---|---|---|---|---|---|\n")
    rows = "".join(
        f"| {c.location} | {c.start_date}–{c.end_date} | {c.scale} | {c.funding_model} "
        f"| {c.target_population} | {c.outcome_metric} | {c.result} | T{int(c.tier)} |\n"
        for c in cases)
    return header + rows


def _threads_block(threads) -> str:
    out = []
    for t in threads:
        out.append(f"### Outcome: {t.outcome}")
        for n in t.nodes:
            ev = ", ".join(f"[{e.title}]({e.url}) [T{int(e.tier)}]" for e in n.evidence) \
                 or "_no supporting data_"
            out.append(f"- ({n.lean.value}, depth {n.depth}) **{n.hypothesis}** — "
                       f"status: {n.status}; evidence: {ev}")
        if t.cut_short:
            out.append(f"> ⚠️ **Unresolved — would need deeper investigation** "
                       f"(stopped: {t.cut_short_reason}).")
    return "\n".join(out) + "\n"


def _references(result: RunResult) -> str:
    seen = {}
    for grp in (result.positions.pro, result.positions.against,
                result.positions.inbetween, result.policy):
        for c in grp:
            for e in c.data:
                seen[e.url] = (e.title, int(e.tier))
    for c in result.cases:
        for u in c.source_urls:
            seen.setdefault(u, ("(case source)", int(c.tier)))
    lines = [f"- [{t}]({u}) — T{tier}" for u, (t, tier) in seen.items()]
    return "## References\n" + ("\n".join(lines) if lines else "_(none)_") + "\n"


def render_formal(result: RunResult) -> str:
    r = result
    parts = [
        f"# Evaluation: {r.topic}\n",
        "## Positions\n",
        _claims_block("Pro", r.positions.pro),
        _claims_block("Against", r.positions.against),
        _claims_block("In-between", r.positions.inbetween),
        "## Case Ledger\n", _ledger_table(r.cases),
        "## Causal Verification\n", _threads_block(r.threads),
        "## Existing Policy\n", _claims_block("Policy landscape", r.policy),
        "## Tradeoff Framework\n",
        "\n".join(f"- **{b.condition}** → {b.judgment}" for b in r.framework) + "\n",
        "## Verdict\n",
        f"**Bottom line:** {r.verdict.bottom_line}\n\n"
        f"**Reasoning:** {r.verdict.reasoning}\n\n"
        f"**Strongest counter (red-team):** {r.verdict.strongest_counter}\n\n"
        f"**Confidence:** {r.verdict.confidence.value}\n",
        f"\n_Sources consulted via {r.searches_used} searches._\n",
        _references(r),
    ]
    return "\n".join(parts)
