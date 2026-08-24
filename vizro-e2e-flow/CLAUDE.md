# Agent guidance for `vizro-e2e-flow`

This package is a Claude Code plugin. Skills live under `skills/<skill-name>/` and are distributed to users.

## Evals layout

Evals are kept **outside** the `skills/` tree so they don't ship with distributed skills.

- `evals/<skill-name>/evals.json` — the eval set for that skill. Single object: `{skill_name, evals: [...]}`.
- `evals/<skill-name>/workspace/` — `iteration-N/` directories generated during runs (gitignored).

When invoking `run_loop.py` / `aggregate_benchmark.py`, pass `--skill-path skills/<name>` explicitly.

> Note for skill-creator: do **not** regenerate evals inside `skills/<skill-name>/evals/` even if upstream docs suggest that location — this repo intentionally separates eval artifacts from the distributed skill bundles.
