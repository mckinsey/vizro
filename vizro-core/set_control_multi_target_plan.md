# Plan: `set_control` targets multiple controls

## Context

`set_control` (`src/vizro/actions/_set_control.py`) can currently set exactly **one** control:
its field is `control: ModelID`. The "syncing controls" feature builds its default action chain in
`build_default_control_selector_actions` (`src/vizro/models/_controls/_controls_utils.py:148`) by fanning out
**one `set_control` per synced control**:

```python
selector.actions = [
    *[set_control(control=control_id, value=None) for control_id in targeted_controls],
    update_targets(...),
]
```

This is wasteful: N synced controls ⇒ N separate actions/callbacks ⇒ N "Control updated." notifications.
Letting `set_control.control` accept **a list of control ids** lets one action drive all synced controls at once
(one callback, one notification), and gives users an ergonomic way to drive several controls from a single trigger
(e.g. one Graph click cross-filtering multiple filters).

**Feasibility (confirmed):** the callback framework (`src/vizro/models/_action/_action.py`) already supports
"N outputs ↔ N positionally-aligned return values" and auto-shapes `no_update` per output on error
(`_transformed_outputs` collapses a 1-element output list to a single `Output`; `_action_callback_function`
matches list length). **No framework change is needed** — the work is contained to `_set_control.py` plus the
one internal generator, tests, docs, schema, and changelog.

## Decisions (from user)

1. **Scope = multi-target only.** This PR only makes `set_control.control` accept `ModelID | list[ModelID]`.
   The `set_control → set_controls` rename and `@deprecated` alias are **deferred to a follow-up PR** (outlined at
   the end so it isn't lost).
2. **Drill-through across multiple pages = navigate to the first target.** When a *drill-through* `set_control`
   (triggered by a Graph/AgGrid/Figure/Button/Card, not a control's own selector) targets controls that live on
   more than one page, deterministically navigate to the page of the **first cross-page control** (in `control`
   order); every other cross-page target is still synced via `vizro_controls_store`. Selector-triggered syncing
   across many pages is unaffected (it never navigates).

## Core change — `src/vizro/actions/_set_control.py`

### Field

```python
control: ModelID | list[ModelID] = Field(description="Filter or Parameter component id(s) ...")
```

Keep the field value **as the user supplied it** (str stays str, list stays list) so single-target configs and
existing `action.control` reads are unchanged. Add one private normaliser used everywhere internally:

```python
@property
def _control_ids(self) -> list[ModelID]:
    return [self.control] if isinstance(self.control, str) else self.control
```

### `pre_build` — validate every control, classify per page

Loop the existing single-control validation over `self._control_ids` (existence, has `selector`, and the
hierarchical `full_path=True` rejection — all already written, just run per id). Then replace the scalar
`self._same_page` with per-page classification, preserving `control` order:

- `self._same_page_controls: list[ModelID]` — controls on the trigger's page.
- `self._cross_page_controls: list[ModelID]` — controls on a different page.
- `self._is_drill_through: bool` — unchanged (depends only on the parent/trigger model type, via the existing
  `SELECTORS` check).

**Deduplicate** `self._control_ids` at validation time (preserve first-seen order). Two outputs to the same
component in one callback is a hard Dash error, so duplicates must be collapsed. `extract_control_targets`
(`_controls_utils.py:96`) already dedupes on the syncing path; mirror that here for user-authored lists.

### `function` — compute value once, shape per control

The raw value is derived **once** from the trigger (`_get_value_from_trigger` is target-independent — confirmed
across all `_SupportsSetControl` implementers). Factor the current per-selector shaping (lines 196–232: the
`value is None` reset, `is_multi`/`is_range`, single-value list-collapse, `_normalize_range_value`) into a helper:

```python
def _shape_value_for_control(self, control_id, raw_value, controls_store) -> Any | no_update
```

returning the reshaped value or `no_update` for that specific control (e.g. incomplete range, or a multi-item
list into a single-value selector). Then:

```python
value = self._parent_model._get_value_from_trigger(self.value, _trigger)
if value is no_update:
    return self._no_update_result()          # shaped to match `outputs` (scalar or [no_update]*N)

results = [self._shape_value_for_control(cid, value, _controls_store) for cid in self._same_page_controls]

navigated = no_update
if self._cross_page_controls:
    wrote_any = False
    for cid in self._cross_page_controls:
        shaped = self._shape_value_for_control(cid, value, _controls_store)
        if shaped is no_update:
            continue
        self._write_cross_page_store_entry(cid, shaped, _controls_store)   # existing lines 247–256, per id
        wrote_any = True
    if wrote_any:
        set_props("vizro_controls_store", {"data": _controls_store})
        if self._is_drill_through:
            first = self._cross_page_controls[0]
            navigated = get_relative_path(model_manager._get_model_page(model_manager[first]).path)
    results.append(navigated)

return results[0] if len(results) == 1 else results
```

`_no_update_result()` returns `no_update` when there is exactly one output, else `[no_update] * n` where
`n = len(same_page) + (1 if cross_page else 0)`.

### `outputs`

```python
@property
def outputs(self):
    same_page = self._same_page_controls
    if self._cross_page_controls:
        return [*same_page, "vizro_url.pathname"]
    return same_page[0] if len(same_page) == 1 else same_page
```

This preserves **byte-for-byte** the current single-target behavior:
- single same-page control → bare id string (framework unwraps to one `Output`, `function` returns a scalar);
- single cross-page control → `["vizro_url.pathname"]` (unwrapped to one `Output`).

Multi-target adds: all-same-page → `[id, id, …]`; mixed → `[id, …, "vizro_url.pathname"]`. Order in `outputs`
and in `function`'s returned list is the same `control` order, so positions line up.

### `notifications`

Leave the messages as-is (one callback ⇒ one notification regardless of target count — that's the win).
Optional nicety: `"Control(s) updated."` — noted, not required.

## Internal generator — `src/vizro/models/_controls/_controls_utils.py`

Collapse the fan-out in `build_default_control_selector_actions` (line 148) to a single multi-target action:

```python
selector.actions = [
    *([set_control(control=targeted_controls, value=None)] if targeted_controls else []),
    update_targets(id=update_targets_action_id, targets=targeted_figures),
]
```

`targeted_controls` is already deduped/ordered by `extract_control_targets`. Passing the list uniformly (even for
one target) is fine — a 1-element same-page list yields a single `Output` exactly as today.

## Tests

- **`tests/unit/vizro/actions/test_set_control.py`** (primary):
  - `TestSetControlInstantiation`: add list-valued `control`.
  - `TestSetControlPreBuild`: per-element validation (mix of valid/invalid ids raises the existing errors);
    populate/assert `_same_page_controls` / `_cross_page_controls`; dedupe of repeated ids. Update the existing
    `_same_page is True/False` assertions to the new list attributes.
  - `TestSetControlFunction`: same-page multi (returns aligned list), mixed same+cross (returns
    `[values…, path_or_no_update]`, `set_props` called once), cross-page **drill-through across two pages**
    navigates to the **first** control's page (reuse the existing `get_relative_path`/`set_props` mocking
    pattern), per-control `no_update` (one incomplete range among several).
  - `TestSetControlOutputs`: existing single-target assertions stay green; add all-same-page list,
    mixed-with-`vizro_url.pathname`, cross-page-only shapes.
- **`tests/unit/vizro/models/_controls/test_filter.py`** (`test_target_control_sync_actions`, ~L1842): the sync
  chain is now **one** `set_control` with `control == ["target_filter"]` (was `"target_filter"`).
- **`tests/unit/vizro/models/_controls/test_parameter.py`** (`test_target_multiple_controls_sync_actions`, ~L331):
  update from "one action per target" to a single `set_control(control=[...])`.
- Reuse fixtures already in `test_set_control.py` (`managers_two_pages_for_set_control`) — it already defines two
  pages with same-page and cross-page controls, ideal for multi-target cases.

## Docs

- **`src/vizro/actions/_set_control.py` docstring** (the API reference, rendered by mkdocstrings): document that
  `control` accepts a single id **or a list of ids**, and add a short "target multiple controls" example.
- **`docs/pages/user-guides/controls.md`**: simplify the bare-selector sync example (currently
  `actions=[set_control(control="species_filter_1", value=None), set_control(control="species_filter_2", value=None)]`
  at ~L159–162) to a single `set_control(control=["species_filter_1", "species_filter_2"], value=None)`.
- **`docs/pages/user-guides/graph-table-actions.md`**: in the multiple-cross-filter section (~L719–840) show the
  list form as the recommended way to drive several controls from one trigger.
- **`docs/pages/for-llms.md`**: update the `va.set_control()` cheatsheet row to mention list support.

## Schema / changelog / CI gates

- **Schema**: run `hatch run schema` to regenerate `schemas/0.1.61.dev0.json` (the `control` field becomes an
  `anyOf` of string / array of strings) and commit it. Verify with `hatch run schema-check` (CI gate).
- **Changelog**: `hatch run changelog:add`, then fill the **Changed** (or Added) section, e.g. *"`set_control` can
  now target multiple controls at once by passing a list of ids to `control`; the syncing-controls feature now
  emits a single `set_control` for all synced controls."* End with the PR link.
- **Lint**: `hatch run lint`.

## Caveats

1. **Duplicate ids must be deduped** in `pre_build` — two `Output`s to one component in a single callback is a
   hard Dash error, not just a warning.
2. **Drill-through to multiple pages** can only navigate once; per decision (2) it goes to the first cross-page
   target. Documented behavior, not an error.
3. **Order matters**: `outputs` and the `function` return list must iterate `control` in the same order — both use
   `self._same_page_controls` then the single trailing `vizro_url.pathname`.
4. **Notification behavior changes slightly (improvement)**: N synced controls used to emit N "Control updated."
   toasts; now one. Worth a line in the changelog.
5. **No rename this PR** ⇒ `ag_grid.py:195` (`isinstance(a, set_control)`) and `_dashboard.py` (`_get_models(set_control)`)
   need **no** change now (they still reference the same class). They only matter for the follow-up.
6. **`vizro-mcp`** (separate package) has `deprecated_models = {"filter_interaction": "set_control", ...}` in
   `server.py` — untouched by this PR; relevant only to the follow-up rename.

## Verification (end-to-end)

1. `hatch run test-unit tests/unit/vizro/actions/test_set_control.py tests/unit/vizro/models/_controls/test_filter.py tests/unit/vizro/models/_controls/test_parameter.py`
2. `hatch run lint` and `hatch run schema-check`.
3. Manual: build a small app (or adapt `examples/scratch_dev/app.py`, which already drives two controls from one
   selector) with (a) a Graph whose `set_control(control=[f1, f2], value="species")` cross-filters two same-page
   filters on click, and (b) a Filter with `targets=[other_filter, cross_page_filter]` to exercise the collapsed
   sync chain. Run `hatch run example scratch_dev`; confirm both same-page controls update from one click, only one
   success notification appears, and the cross-page value applies on page open.
4. (Optional) the e2e drill/cross-filter suites (`hatch run test-e2e-vizro-dom-elements`) — extend a
   `tests/e2e/.../pages/set_control_*.py` dashboard with a multi-target case if we want browser coverage.

## Follow-up PR (deferred — planned, not in this PR): rename `set_control` → `set_controls`

Mirrors the `Layout → Grid` precedent (`src/vizro/models/_grid.py:249`) and `filter_interaction`
(`src/vizro/actions/_filter_interaction.py:15`):

1. Rename the class to `set_controls` (`type: Literal["set_controls"]`, field `controls`); keep `set_control` as a
   `@deprecated(..., category=FutureWarning)` alias (`type` stays `"set_control"`). Because the field name changes
   (`control` → `controls`), prefer a **shared private base** that normalizes both to one internal list, rather
   than a plain subclass. Link the warning to a new `deprecations.md` anchor.
2. Register `set_controls` in the `ActionType` union (`src/vizro/models/types.py:760`), keeping `set_control`.
3. Export `set_controls` in `src/vizro/actions/__init__.py` and import it in `src/vizro/models/__init__.py`
   (feeds `model_rebuild()`).
4. Point internal constructors at `set_controls` (`_controls_utils.py`), and update the `isinstance` heuristic
   (`ag_grid.py:195`) and `_get_models` queries (`_dashboard.py`) to the non-deprecated class — **required** so
   Vizro's own default actions don't emit the deprecation warning.
5. Switch `examples/` and e2e dashboards from `set_control` to `set_controls`; add module-level
   `filterwarnings("ignore:...set_control...:FutureWarning")` where the deprecated path is exercised.
6. Add `docs/pages/API-reference/deprecations.md` section; update `filter_interaction`'s "After" example and the
   `_filter_interaction.py` message (both currently point at `set_control`); update `vizro-mcp` `deprecated_models`.
7. Add `tests/unit/vizro/actions/test_legacy_set_control.py` (`pytest.warns(FutureWarning, ...)` per the
   `test_legacy_layout.py` / `test_legacy_filter_interaction.py` template); regenerate schema (deprecated alias
   stays with `"deprecated": true`).
