# Vizro docs agent eval rubric

Every run of every prompt is scored on three criteria. Each is worth **0**, **1**, or **2** for a maximum of **6 per run**. Scores are independent — a run can score 2 on validation even if intent match is 0.

**Rubric version:** 1

## Criterion A — Config validates

Does the agent's output produce a valid `vm.Dashboard` object?

Test it by executing the produced code and checking that `vm.Dashboard(...)` returns without raising a `pydantic.ValidationError`, `TypeError`, `AttributeError`, `KeyError`, or `ValueError`.

| Score | Meaning                                                                                                                                         |
| ----- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| 0     | Module fails to import (syntax error, unknown import, wrong package name), or `vm.Dashboard(...)` raises a validation error.                    |
| 1     | Dashboard constructs but one or more secondary Pydantic warnings are emitted (deprecation warning, incorrect type but coerced, etc.).           |
| 2     | Clean construction with no errors and no Vizro-emitted warnings.                                                                                |

## Criterion B — Dashboard renders

Does calling `Vizro().build(dashboard).run(...)` start the app without error?

Run it in a subprocess with `debug=False`, waiting for the "Running on http://" line for up to 15 seconds, then hit `/` with `requests.get` and check the response is HTTP 200.

| Score | Meaning                                                                                                                            |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------- |
| 0     | Process crashes on startup, hangs past 15 seconds, or `/` returns non-200.                                                         |
| 1     | Process starts and `/` returns 200, but the server log emits an ERROR-level record during startup or the first request.            |
| 2     | Process starts, `/` returns 200, and no ERROR records are emitted.                                                                 |

## Criterion C — Intent matched

Does the produced dashboard satisfy the prompt's stated intent?

Each prompt lists explicit intent bullets under `intent:` in `prompts.yaml`. Compare the agent's code against those bullets. Prefer static inspection of the constructed `vm.Dashboard` object (via `.model_dump()`) over textual matching so equivalent phrasings pass.

| Score | Meaning                                                                                                                            |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------- |
| 0     | Fewer than half of the intent bullets are satisfied, or the dashboard demonstrates a different feature.                            |
| 1     | Most intent bullets are satisfied but at least one is missing or off (wrong argument name, wrong selector, missing action, ...).   |
| 2     | Every intent bullet is satisfied.                                                                                                  |

## Aggregation

For a `(model, mode)` pair, report:

- **Per-criterion average** across all prompts (three floats between 0 and 2).
- **Overall pass rate** = fraction of prompts scoring **≥ 5 / 6** on the sum.
- **Docs-attribution rate** = fraction of prompts where `docs-only` scored ≥ 2 points below `skill` or `mcp` on any criterion. These are the prompts the docs should learn to answer.

## Failure triage tags

When recording a run, add one of these tags per criterion if it scored below 2. These make the aggregate summary skimmable and actionable.

| Tag                          | When to apply                                                                                                     |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `wrong-import`               | Agent imported a non-existent module or forgot an import.                                                         |
| `wrong-model`                | Agent used the wrong `vm.*` model for the requested feature.                                                      |
| `wrong-argument`             | Agent passed an unknown argument name, or a valid argument with a wrong-shape value.                              |
| `missing-decorator`          | Custom function used without `@capture(...)`.                                                                     |
| `wrong-capture-mode`         | `@capture("graph")` used for an action, etc.                                                                      |
| `missing-add-type`           | Custom component used without `Model.add_type(...)`.                                                              |
| `data-not-registered`        | YAML/JSON referenced a data source that was not added to `data_manager`.                                          |
| `stale-api`                  | Agent used an API that changed (deprecated model name, removed action, ...).                                      |
| `hallucinated-api`           | Agent used a symbol that never existed in Vizro.                                                                  |
| `intent-drift`               | Dashboard runs but demonstrates a different feature.                                                              |
