# Vizro docs agent eval suite

A small harness for measuring how well AI coding agents build Vizro dashboards from a natural-language prompt, and for attributing failures to docs, skill, or MCP.

## What this measures

For every prompt in [`prompts.yaml`](prompts.yaml), the harness asks a coding agent (Claude, GPT-5, Cursor, etc.) to produce a working Vizro app. Each run is scored against the [rubric](rubric.md).

The suite runs three modes so that failures can be attributed:

| Mode                 | Agent has access to                                                   | If a prompt fails here it's a problem with...           |
| -------------------- | --------------------------------------------------------------------- | ------------------------------------------------------- |
| **docs-only**        | The published Vizro docs and `llms.txt` only.                         | The docs (this is the mode we want to improve).         |
| **skill**            | Docs + the `vizro-e2e-flow` skill (curated guides for common tasks).  | Skill coverage (the skill is missing the pattern).      |
| **mcp**              | Docs + the `vizro-mcp` server (tool calls for scaffolding, schema).   | The MCP surface (missing tool, unclear tool contract).  |

Prompts that fail in **docs-only** but succeed in **skill** or **mcp** indicate opportunities to enrich the docs with the same guidance.

## Contents

- [`prompts.yaml`](prompts.yaml): 18 realistic dashboard-building prompts, organised by capability area.
- [`rubric.md`](rubric.md): scoring rubric — three criteria (validates, renders, intent) each 0-2, so 0-6 per run.
- [`run_eval.py`](run_eval.py): runner skeleton. Iterates prompts × modes × models, calls the configured agent, scores the result, writes `results/<timestamp>/results.json`.

## How to run

The runner requires you to plug in an agent-invocation function per mode. Out of the box, `run_eval.py` will emit `NotImplementedError` for each mode until you provide callables.

```bash
python vizro-core/tools/agent-eval/run_eval.py \
    --models claude-opus-4 gpt-5 \
    --modes docs-only skill mcp \
    --prompts vizro-core/tools/agent-eval/prompts.yaml \
    --out vizro-core/tools/agent-eval/results
```

The runner produces:

- `results/<timestamp>/raw/<model>-<mode>-<prompt-id>.py` — the code the agent produced.
- `results/<timestamp>/scores.jsonl` — one JSON object per run with prompt id, model, mode, scores, notes.
- `results/<timestamp>/summary.md` — human-readable aggregate: pass rates per mode, most-failed prompts, deltas.

## Interpreting results

After a run, focus triage on prompts where **docs-only** underperforms **skill** or **mcp** by two or more points on the same criterion. Those are the biggest opportunities to add missing docs.

## Extending the suite

- Add a new prompt: append a block to `prompts.yaml`. Prompt ids are stable; do not renumber.
- Add a new mode: implement `agent_run_<mode>(prompt, model)` in `run_eval.py` and register it in the `MODES` dict.
- Change scoring: edit `rubric.md` and the `score_run` function in `run_eval.py`. Keep old runs comparable by bumping `RUBRIC_VERSION`.
