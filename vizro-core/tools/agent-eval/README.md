# Vizro docs agent eval suite

A small prototype harness for measuring how well AI coding agents build Vizro dashboards from a natural-language prompt using only the Vizro docs, and for surfacing where the docs need work.

## What this measures

For every prompt in [`prompts.yaml`](prompts.yaml), the harness asks a coding agent (Claude, GPT-5, Cursor, etc.) to produce a working Vizro app. Each run is scored against the [rubric](rubric.md).

The agent has access only to the published Vizro docs (and `llms.txt`) — no `vizro-mcp` server, no `vizro-e2e-flow` skill. Prompts that score poorly point at gaps or ambiguities in the docs that the docs team can address.

## Contents

- [`prompts.yaml`](prompts.yaml): 18 realistic dashboard-building prompts, organized by capability area.
- [`rubric.md`](rubric.md): scoring rubric — three criteria (validates, renders, intent) each 0-2, so 0-6 per run.
- [`run_eval.py`](run_eval.py): CLI runner. Iterates prompts × models, calls the configured agent, scores the result, writes `results/<timestamp>/`.
- [`agents.py`](agents.py): agent callables — `mock` (fixed valid dashboard, for smoke tests) and `anthropic-docs-only` (real Anthropic API call, optionally injecting `llms.txt`).

## Setup

The harness needs `vizro` importable (to construct and boot the produced dashboards), plus `pyyaml`, `requests`, and — if you want to use the Anthropic agent — `anthropic`.

The simplest path is to run inside the `vizro-core` hatch env, which already has `vizro`. Install the harness's own dependencies into that env once:

```bash
cd vizro-core
hatch run pip install -r tools/agent-eval/requirements.txt
```

For the `anthropic-docs-only` agent, also set:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# Optional: inject the current docs so the agent doesn't rely on training-data recall.
export VIZRO_EVAL_DOCS_FILE="$(pwd)/docs/llms.txt"
```

## How to run

Smoke test the pipeline with the mock agent (no API calls, no key required):

```bash
cd vizro-core
hatch run python tools/agent-eval/run_eval.py \
    --agent mock \
    --models mock-model \
    --prompts tools/agent-eval/prompts.yaml \
    --only P01 \
    --out tools/agent-eval/results
```

Then run for real against Anthropic:

```bash
cd vizro-core
hatch run python tools/agent-eval/run_eval.py \
    --agent anthropic-docs-only \
    --models claude-sonnet-4-5-20250929 \
    --prompts tools/agent-eval/prompts.yaml \
    --out tools/agent-eval/results
```

Useful flags:

- `--only P01 P07`: run just those prompt ids (fast local iteration).
- `--models` accepts multiple, and every model is run against every prompt.

The runner produces:

- `results/<timestamp>/raw/<model>-<prompt-id>.py` — the code the agent produced.
- `results/<timestamp>/scores.jsonl` — one JSON object per run with prompt id, model, scores, tags.
- `results/<timestamp>/summary.md` — per-model averages, pass rate, and a failure-tag frequency table.

## Interpreting results

Focus triage on prompts that repeatedly score 0 or 1 on **Config validates** or **Dashboard renders** — the failure tags in `scores.jsonl` (`wrong-import`, `wrong-argument`, `render-boot-crash`, `render-error-log`, …) point at the section of the docs that needs work.

## Extending the suite

- Add a new prompt: append a block to `prompts.yaml`. Prompt ids are stable; do not renumber.
- Add a new agent: define a function `(prompt, model) -> str` in `agents.py`, then either extend the `--agent` choices in `run_eval.py` or import `run_eval` and call `register_agent(your_fn)` from your own script.
- Change scoring: edit `rubric.md` and the `score_*` functions in `run_eval.py`. Keep old runs comparable by bumping `RUBRIC_VERSION`.

## What's not implemented yet

Criterion C (**intent matched**) is still a stub — every row currently gets an `intent-not-implemented` tag with score 0. Criteria A and B are fully implemented and grade every run. See the `score_intent` docstring in `run_eval.py` for the recommended next step.
