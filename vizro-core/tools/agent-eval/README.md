# Vizro docs agent eval suite

A small prototype harness for measuring how well AI coding agents build Vizro dashboards from a natural-language prompt using only the Vizro docs, and for surfacing where the docs need work.

## What this measures

For every prompt in [`prompts.yaml`](prompts.yaml), the harness asks a coding agent (Claude, GPT-5, Cursor, etc.) to produce a working Vizro app. Each run is scored against the [rubric](rubric.md).

The agent has access only to the published Vizro docs (and `llms.txt`) — no `vizro-mcp` server, no `vizro-e2e-flow` skill. Prompts that score poorly point at gaps or ambiguities in the docs that the docs team can address.

## Contents

- [`prompts.yaml`](prompts.yaml): 18 realistic dashboard-building prompts, organised by capability area.
- [`rubric.md`](rubric.md): scoring rubric — three criteria (validates, renders, intent) each 0-2, so 0-6 per run.
- [`run_eval.py`](run_eval.py): runner skeleton. Iterates prompts × models, calls the configured agent, scores the result, writes `results/<timestamp>/results.json`.

## How to run

The runner requires you to plug in an agent-invocation function. Out of the box, `run_eval.py` will raise until you provide one.

```bash
python vizro-core/tools/agent-eval/run_eval.py \
    --models claude-opus-4 gpt-5 \
    --prompts vizro-core/tools/agent-eval/prompts.yaml \
    --out vizro-core/tools/agent-eval/results
```

The runner produces:

- `results/<timestamp>/raw/<model>-<prompt-id>.py` — the code the agent produced.
- `results/<timestamp>/scores.jsonl` — one JSON object per run with prompt id, model, scores, notes.
- `results/<timestamp>/summary.md` — human-readable aggregate: pass rates per model, most-failed prompts.

## Interpreting results

Focus triage on prompts that repeatedly score 0 or 1 on **Config validates** or **Intent matched** — the failure tags in `scores.jsonl` (`wrong-import`, `wrong-argument`, `hallucinated-api`, etc.) point at the section of the docs that needs work.

## Extending the suite

- Add a new prompt: append a block to `prompts.yaml`. Prompt ids are stable; do not renumber.
- Change scoring: edit `rubric.md` and the `score_run` function in `run_eval.py`. Keep old runs comparable by bumping `RUBRIC_VERSION`.
