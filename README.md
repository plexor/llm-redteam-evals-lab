# LLM Red Team Evals Lab 🧠⚔️

**Author:** Ruben Colón  
**Purpose:** Advanced LLM red teaming + evaluation harness with reproducible datasets, scoring taxonomy, and reporting.

This repo is designed to demonstrate real evaluator skill:
- prompt injection + jailbreak methodology
- multi-turn attack chains
- tool-injection testing
- hallucination/citation falsification detection
- instruction hierarchy conflict stress tests
- scoring + failure tagging
- automated reporting + model comparison

## Models to Test
Recommended baseline targets:
- GPT-4o (gold standard)
- Llama 3.1 70B (open-source baseline)
- DeepSeek R1 (reasoning stress test)
- Mixtral (helpful-slip hunting)

## Quick Start
```bash
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
python evals/run_eval.py --dataset datasets/prompts/jailbreak.jsonl --model gpt4o

# quick subset + CSV + summary artifacts
python evals/run_eval.py --dataset datasets/prompts/jailbreak.jsonl --model gpt4o --max-prompts 10 --format json+csv --summary

# reproducible artifact names
python evals/run_eval.py --dataset datasets/prompts/jailbreak.jsonl --model gpt4o --run-id baseline_week1
```

## Folder Structure
- `datasets/` prompt corpora in JSONL
- `evals/` evaluation runners + scoring utilities
- `tools/` prompt mutation + attack chain generation
- `reports/` casefiles + weekly reports
- `results/` raw outputs grouped by model

## Scoring
See `docs/scoring_rubric.md` and `docs/taxonomy.md`.

## Disclaimer
This repository is intended for defensive security research and evaluation work.
