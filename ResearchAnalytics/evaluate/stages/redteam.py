from ..config import ModelClass
from ..contracts import Verdict
from .context import ResearchContext

_SYS = (
    "You are an adversarial red-team. Attack the given verdict as hard as you honestly "
    "can: find its weakest assumption, the strongest counter-evidence, and any smuggled "
    "bias. Then return a REVISED Verdict — either defended (unchanged bottom_line with a "
    "sharper strongest_counter and possibly lower confidence) or corrected if the attack "
    "succeeds. The strongest_counter field must hold the best surviving objection."
)


def red_team(topic: str, verdict: Verdict, ctx: ResearchContext) -> Verdict:
    client, model = ctx.llm(ModelClass.HEAVY)
    return client.structured_call(Verdict, [
        {"role": "system", "content": _SYS},
        {"role": "user", "content": f"Idea: {topic}\n\nVerdict to attack:\n"
                                    f"{verdict.model_dump_json(indent=2)}"},
    ], model=model)
