import argparse
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")
from .config import default_config, load_keys
from .pipeline import run_evaluation
from .store import save_run
from .render.formal import render_formal
from .render.chat import render_chat


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="evaluate",
                                 description="Idea Evaluation Engine")
    ap.add_argument("topic", help="the idea/policy to evaluate")
    ap.add_argument("--out-dir", default=".", help="where to write the formal file")
    ap.add_argument("--depth", type=int, default=None, help="causal recursion depth budget")
    ap.add_argument("--max-searches", type=int, default=None)
    args = ap.parse_args(argv)

    cfg = default_config()
    if args.depth is not None:
        cfg.depth_budget = args.depth
    if args.max_searches is not None:
        cfg.max_searches = args.max_searches

    keys = load_keys()
    present = [k for k, v in keys.items() if v]
    missing = [k for k, v in keys.items() if not v]
    if present:
        print(f"[evaluate] keys loaded: {', '.join(present)}", flush=True)
    if missing:
        print(f"[evaluate] keys missing: {', '.join(missing)}", flush=True)
    result = run_evaluation(args.topic, cfg, keys)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(args.topic)
    run_dir = out_dir / slug
    run_dir.mkdir(parents=True, exist_ok=True)

    formal_path = run_dir / "evaluation.md"
    formal_path.write_text(render_formal(result), encoding="utf-8")
    chat_path = run_dir / "summary.md"
    chat_path.write_text(render_chat(result), encoding="utf-8")
    save_run(result, run_dir / "run.json")

    print(render_chat(result))
    print(f"\n[formal file: {formal_path}]")
    print(f"[summary file: {chat_path}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
