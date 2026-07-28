# Vizro docs agent eval rubric

Every run is scored on three criteria (or short-circuited as a **giveup** outcome — see below). Each criterion is worth **0**, **1**, or **2** for a maximum of **6 per run**. Scores are independent — a run can score 2 on validation even if intent match is 0.

**Rubric version:** 1

## The giveup outcome

Prompts are phrased as user goals, not Vizro implementations. The system prompt tells the agent to attempt each goal in Vizro using only the docs, and — critically — to emit a `##VIZRO_EVAL_GIVEUP##` marker followed by a written reason if it honestly cannot achieve the goal from the docs alone. A giveup is:

- **not scored on the three criteria** (all three read as 0);
- **tagged** `agent-gave-up`;
- **captured verbatim** in the summary's "Prompts where the agent gave up" section.

Giveups are the highest-value docs-team signal: the model is naming the section of the docs that failed to unblock it. Silent failures (agent invents an API and produces broken code) are worse than honest giveups — the system prompt discourages the former in favor of the latter.

## Criterion A — Config validates

Does the agent's output produce a valid `vm.Dashboard` object?

Test by executing the produced code in a subprocess and checking that a module-level `vm.Dashboard` instance is present without raising a `pydantic.ValidationError`, `TypeError`, `AttributeError`, `KeyError`, or `ValueError`.

| Score | Meaning                                                                                                                                         |
| ----- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| 0     | Module fails to import (syntax error, unknown import, wrong package name), no `vm.Dashboard` was constructed, or construction raises.           |
| 1     | Dashboard constructs but a Vizro- or pydantic-originated `DeprecationWarning` is emitted.                                                       |
| 2     | Clean construction with no errors and no Vizro-emitted warnings.                                                                                |

## Criterion B — Dashboard renders

Does calling `Vizro().build(dashboard).run(...)` start the app without error?

Run it in a subprocess with `debug=False`, poll `http://127.0.0.1:<port>/` until it responds (up to 15 s), then inspect the server log for ERROR-level records.

| Score | Meaning                                                                                                                            |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------- |
| 0     | Process crashes on startup, doesn't respond within 15 s, or `/` returns non-200.                                                   |
| 1     | Process starts and `/` returns 200, but the server log emits an ERROR-level record during startup or the first request.            |
| 2     | Process starts, `/` returns 200, and no ERROR records are emitted.                                                                 |

## Criterion C — Intent matched

Does the produced dashboard achieve the *user-visible outcome* the prompt asks for?

Each prompt lists outcome-style bullets under `intent:` in `prompts.yaml` (e.g. "user can restrict the view to a date range"). These describe what the finished dashboard should let a user do, not which Vizro model the agent must use — a `vm.DatePicker` and a `vm.Filter` with a range selector both satisfy the same intent. Prefer static inspection of `dashboard.model_dump()` for structural bullets; use an LLM-judge for the fuzzier ones once wired.

| Score | Meaning                                                                                                                            |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------- |
| 0     | Fewer than half of the intent bullets are satisfied, or the dashboard demonstrates a different feature.                            |
| 1     | Most intent bullets are satisfied but at least one is missing (wrong data column, missing action wiring, off-target selector, …).  |
| 2     | Every intent bullet is satisfied.                                                                                                  |

## Aggregation

For each model, report:

- **Per-criterion average** across all prompts (three floats between 0 and 2).
- **Overall pass rate** = fraction of prompts scoring **≥ 5 / 6** on the sum.
- **Giveup rate** = fraction of prompts where the agent emitted the giveup marker.

Giveups are excluded from the per-criterion averages' *numerator* but included in the *denominator*: a high giveup rate lowers the average score, which is intentional — giveups are still docs failures, just honest ones.

## Failure triage tags

Attached to a run when a criterion scores below 2 (or when the agent gives up). These make the summary skimmable and route work to the right area of the docs.

| Tag                          | When to apply                                                                                                     |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `agent-gave-up`              | Agent emitted the `##VIZRO_EVAL_GIVEUP##` marker. See `notes` for the reason.                                     |
| `wrong-import`               | Agent imported a non-existent module or forgot an import.                                                         |
| `wrong-model`                | Agent used the wrong `vm.*` model for the requested outcome.                                                      |
| `wrong-argument`             | Agent passed an unknown argument name, or a valid argument with a wrong-shape value.                              |
| `missing-decorator`          | Custom function used without `@capture(...)`.                                                                     |
| `wrong-capture-mode`         | `@capture("graph")` used for an action, etc.                                                                      |
| `missing-add-type`           | Custom component used without `Model.add_type(...)`.                                                              |
| `data-not-registered`        | YAML/JSON referenced a data source that was not added to `data_manager`.                                          |
| `stale-api`                  | Agent used an API that changed (deprecated model name, removed action, …).                                        |
| `hallucinated-api`           | Agent used a symbol that never existed in Vizro.                                                                  |
| `intent-drift`               | Dashboard runs but demonstrates a different feature than the prompt asked for.                                    |
