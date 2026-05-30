# Idea Evaluation Engine

Provider-agnostic Python harness that evaluates an idea/policy and produces a rigorous,
blunt, pragmatic report. Every claim follows **Data → Insight → Acknowledged bias**;
sources are tiered (T1 primary → T4 opinion); real-world cases are normalized into a
ledger; causal "why" threads are verified recursively under a depth+budget governor.

## Setup

```bash
pip install -e ".[dev]"
cp .env.example .env   # fill in ANTHROPIC/OPENAI/DEEPSEEK/FIRECRAWL keys
```

## Run

```bash
python -m evaluate "Universal Basic Income" --out-dir ./reports --depth 4
```

Outputs: a formal Markdown file + a JSON run record in `--out-dir`, and a conversational
synthesis to stdout.

## Model routing

Stages declare a class (light/medium/heavy); `evaluate/config.py` maps each class to a
(provider, model). Edit `default_config()` to retune.

## Tests

```bash
pytest -v
```
