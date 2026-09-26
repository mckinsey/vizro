# Vizro pre-stable deprecations plan (v0.1.60 → v0.1.61)

## Context

Ahead of the breaking **Vizro 1.0.0** release we want to ship a **non-breaking `0.1.61`** that:
enables all the new syntax, emits `FutureWarning`s for everything we intend to remove in 1.0.0, and documents
how to migrate. The golden rule (from the team's own process): **never emit a deprecation warning the user
can't already fix** — for each item the 1.0.0 behaviour must already be reachable in 0.1.61, so a user who
switches to the new syntax gets no warning.

Targets come from the deprecation tracking issue. **In scope for 0.1.61:**
Cascader `full_path` default flip, RangeSlider→Slider merge, `set_control`→`set_controls`, a Python-3.10
deprecation heads-up, and re-pointing all existing "0.2.0" messaging to "1.0.0".
**Explicitly out of scope:** AgGrid/Table (1.0.0 only), `consistent_colors` default flip ("don't do anything now"),
and the *actual* Python-3.10 drop + `flask_caching>=2.5` (deferred to 1.0.0).

Decisions locked with the user:
- **`set_controls`**: add a NEW action `set_controls(controls: list[ModelID], value=...)` where `controls` accepts a
  **list of ids only**. **Keep `set_control`** but decorate it `@deprecated` pointing to `set_controls`. (Not per-control values.)
- **Python 3.10 / `flask_caching`**: **defer both** the drop and the `flask_caching>=2.5` bump to 1.0.0, but in 0.1.61
  **emit a runtime deprecation warning when running on 3.10**. (Precedent check: the prior 3.9/3.8 drops used **no**
  runtime warning — only a changelog `Removed` entry — so this warning is a small new pattern. Flagged for sign-off.)
- **Versioning**: **re-point every existing "Vizro 0.2.0" reference to "Vizro 1.0.0"** and use 1.0.0 in all new messages.
- **Scope**: **vizro-core only.** vizro-mcp / vizro-e2e-flow / vizro-ai are follow-ups (listed at the end).

---

## Deprecation mechanics (templates already in the codebase — reuse verbatim)

| Shape | Template to copy | Mechanism |
|---|---|---|
| Rename/deprecate a **model or action class** | `src/vizro/models/_grid.py` (`Layout`), `src/vizro/actions/_filter_interaction.py` | `@deprecated("… will not exist in Vizro 1.0.0 (<link>). Use …", category=FutureWarning)` from `typing_extensions`; fires on instantiation |
| Deprecate a **field/argument** | `make_deprecated_field_warning` in `src/vizro/models/_models_utils.py`; used on `Action.inputs` in `_action/_action.py` | `BeforeValidator` factory → `FutureWarning`; add `❗Deprecated:` note in the field `description` (do NOT use pydantic `deprecated=`) |
| Deprecate a **usage pattern / detect explicit-vs-default** | `make_actions_chain` in `_models_utils.py`; `set_variant_defaults` in `actions/_notifications.py` | `@model_validator(mode="after")` + `warnings.warn(..., FutureWarning, stacklevel=…)`; detect via `"field" not in self.model_fields_set`; mutate via `self.__dict__["field"] = …` (bypasses `frozen`/`validate_assignment`) |
| Legacy config discriminator | `_get_layout_discriminator`/`_get_action_discriminator` in `types.py` | callable `Discriminator` + `Tag` — **not needed** for our items (all keep explicit `type` literals) |
| **Boolean mode switch (`range`)** | `date_picker.py` + `validate_date_time_range_picker` in `_form_utils.py` | `range: bool` field + `value` union type + cross-field validator + branching `__call__` |
| **Legacy tests** | `tests/unit/vizro/models/test_legacy_layout.py`, `tests/unit/vizro/actions/test_legacy_*.py` | copy old-API tests into a `test_legacy_*.py` (no `parametrize`), module-level `pytestmark = pytest.mark.filterwarnings("ignore:<msg>:FutureWarning")`; add `pytest.warns(FutureWarning, match=…)` tests. Global `filterwarnings=["error"]` (pyproject) turns every stray warning into a failure |
| **Changelog** | `hatch run changelog:add` → scriv fragment; uncomment `### Deprecated` (and `### Added`) | categories: `Highlights ✨, Removed, Added, Changed, Deprecated, Fixed, Security` |

**Message conventions:** short, imperative fix, name **Vizro 1.0.0**, link
`https://vizro.readthedocs.io/en/stable/pages/API-reference/deprecations/#<anchor>`; get `stacklevel` right so the
console points at the user's line. Every warning gets a matching section in
`docs/pages/API-reference/deprecations.md`.

**Generated files — regenerate, don't hand-edit:** `schemas/*.json` (`hatch run schema`),
`docs/pages/components_compendium/*` (`tools/generate_compendium.py`), `docs/pages/for-llms.md` + `docs/llms.txt`
(docs build), `cheatsheet.html`, `CHANGELOG.md` (scriv collect at release).

---

## Branch strategy

Integration branch **`deprecation/vizro-pre-stable`** off `main`. Each item below is its **own feature branch → PR
into the integration branch**. When all are merged, one final PR `deprecation/vizro-pre-stable → main` ships the
non-breaking **0.1.61**. Order is by user impact (most common first), which is also the intended
`deprecations.md` ordering.

0. `deprecation/repoint-1.0.0` — re-point 0.2.0→1.0.0 (prerequisite; merge first).
1. `deprecation/range-slider` — RangeSlider → Slider(range=True).
2. `deprecation/set-controls` — set_control → set_controls.
3. `deprecation/cascader-full-path` — full_path default-change warning.
4. `deprecation/python-310` — Python 3.10 deprecation warning.

---

## Item 0 — Re-point "0.2.0" → "1.0.0"  (branch `deprecation/repoint-1.0.0`)

Twelve references across 6 files. Straight find/replace of the version token in deprecation text (keep code/logic):
- `src/vizro/models/types.py` (layout & action missing-`type` warnings)
- `src/vizro/models/_grid.py` (`Layout` `@deprecated`)
- `src/vizro/models/_models_utils.py` (`make_deprecated_field_warning`, `make_actions_chain`)
- `src/vizro/models/_action/_action.py` (`inputs` field + static-arg warning)
- `src/vizro/actions/_filter_interaction.py` (`@deprecated`)
- `docs/pages/API-reference/deprecations.md` (intro front-matter + body; retitle toward 1.0.0)

Update the matching `match=` strings in existing legacy tests (`test_legacy_layout.py`, `test_legacy_export_data.py`,
`test_legacy_filter_interaction.py`, `test_page.py`, `test_container.py`) since they assert on the message text.
Changelog: `### Changed` (or none — it's message-only). Run `hatch run test-unit` to confirm all `match=`/`pytestmark`
strings still line up.

---

## Item 1 — Merge RangeSlider into Slider  (branch `deprecation/range-slider`)

**v1 behaviour:** `Slider` has `range: bool`; `Slider(range=True)` == today's `RangeSlider`. `RangeSlider` removed.
**0.1.61:** add `range` to `Slider`; make `RangeSlider` a deprecated alias. Template = `DatePicker.range`.

**`src/vizro/models/_components/form/slider.py`**
- Add `range: bool = False` (`Field(..., validate_default=True)`; default **False**, unlike DatePicker's True).
- Widen `value` to `float | list[float] | None` (mirror DatePicker's `list[date] | date | None`; keep the
  `min_length/max_length == 2` check for the list case).
- Add `@model_validator(mode="after")` `validate_slider_range` mirroring `validate_date_time_range_picker` in
  `_form_utils.py` ("set range=True if providing a list", "set range=False if providing a single value"). Prefer a
  model-validator over a field `AfterValidator` to avoid the value-before-range field-ordering constraint.
- Branch on `self.range` in `__call__` / `_build_dynamic_placeholder`: `dcc.RangeSlider` vs `dcc.Slider`, value
  fallback `[min, max]` vs `min`, and `_inner_component_properties`.

**`src/vizro/models/_components/form/range_slider.py`** → becomes the deprecated alias:
```python
@deprecated("`RangeSlider` is deprecated and will not exist in Vizro 1.0.0 (<link>). Use `Slider(range=True)`.",
            category=FutureWarning)
class RangeSlider(Slider):
    type: Literal["range_slider"] = "range_slider"  # keep so YAML `type: range_slider` still routes here
    range: bool = True                              # force range mode
```
`RangeSlider(Slider)` means `isinstance(range_slider, Slider)` is True (simplifies checks); a plain `Slider(range=True)`
is **not** a `RangeSlider` instance (so the deprecation only fires on explicit `RangeSlider(...)`).

**Avoid spurious internal warnings (critical):** auto-selected numerical filters currently instantiate `RangeSlider`.
Migrate every internal instantiation to `Slider(range=True)`:
- `src/vizro/models/_controls/filter.py`: `DEFAULT_SELECTORS["numerical"]` → a callable yielding `Slider(range=True)`
  (e.g. `functools.partial(Slider, range=True)` — verify `DEFAULT_SELECTORS` is only *instantiated*, not used in
  isinstance/subclass checks). Change the `_filter_between` branch from `isinstance(sel, RangeSlider)` to
  `isinstance(sel, Slider) and sel.range`.
- `SELECTORS["numerical"]`, `_is_numerical_or_date_selector`, `Form.pre_build` isinstance tuples: `Slider` now covers
  the `RangeSlider` subclass, so keep or simplify — just ensure no code *constructs* `RangeSlider`.
- `_controls_utils.get_selector_default_value` and `_set_control._shape_value_for_control` already use
  `getattr(selector, "range", …)` — no change needed.

**Keep working / update:** `SelectorType` union (leave `RangeSlider` in — plain string discriminator + its `type`
literal keeps YAML back-compat), `models/__init__.py` + `_components/form/__init__.py` exports/`__all__`,
`themes/_mantine_theme.py` keys.

**Tests/examples/docs:** copy `tests/unit/.../form/test_range_slider.py` → `test_legacy_range_slider.py`
(`pytestmark` ignore + a `pytest.warns` test); migrate `test_filter.py` and all e2e to `Slider(range=True)`; migrate
`examples/dev/app.py`, `examples/dev/yaml_version/dashboard.yaml` (`type: slider` + `range: true`), `themes/`,
`mantine/`; migrate docs (`custom-components.md` builds a custom RangeSlider — 26 refs; `filters.md`, `selectors.md`,
`controls.md`, `data.md`, `explore-components.md`). Add `deprecations.md` section + `### Deprecated` changelog fragment.
Regenerate schema.

---

## Item 2 — set_control → set_controls  (branch `deprecation/set-controls`)

**v1 behaviour:** `set_controls(controls: list[ModelID], value=...)`; `set_control` removed.
**0.1.61:** add `set_controls`; keep `set_control` as a deprecated alias. Template = `filter_interaction` (`@deprecated`)
+ `_on_page_load(update_targets)` (subclass reuse).

**`src/vizro/actions/_set_control.py`** — make `set_controls` the canonical `_AbstractAction` (move the existing
pre_build / `function` / `outputs` / `_shape_value_for_control` / `notifications` logic onto it, keyed off
`self.controls` via the existing `_control_ids` property):
```python
class set_controls(_AbstractAction):
    type: Literal["set_controls"] = "set_controls"
    controls: list[ModelID] = Field(default=[], description="…")   # list of ids only; non-empty enforced in pre_build
    value: JsonValue = Field(default=None, description="…")        # unchanged semantics (shared value/directive)

@deprecated("`set_control` is deprecated and will not exist in Vizro 1.0.0 (<link>). Use `set_controls`.",
            category=FutureWarning)
class set_control(set_controls):
    type: Literal["set_control"] = "set_control"
    control: ModelID | list[ModelID] = Field(description="…")      # back-compat: single id or list
    # @model_validator(after): self.__dict__["controls"] = [control] if str else list(control)
```
Implementation notes: `controls` needs a default (`[]`) so the `set_control` subclass constructs via `control=`;
keep the existing "reject empty" check in `pre_build` so an actual empty `set_controls(controls=[])` errors. (If the
subclass field-mapping proves fiddly, factor a shared private base instead — either is fine.)

**Wire-up:** add `Annotated["set_controls", Tag("set_controls")]` to `ActionType` in `types.py`; export `set_controls`
in `src/vizro/actions/__init__.py` (`__all__`), keep `set_control` exported.

**Avoid spurious internal warnings (critical):** `_controls_utils.build_default_control_selector_actions` creates
`set_control(control=targeted_controls)` for every default-synced Filter/Parameter — migrate it to
`set_controls(controls=targeted_controls)`, else every such control warns.

**Re-point filter_interaction:** its `@deprecated` message and the `deprecations.md` `#filter-interaction` section
currently say "use `set_control`" — change to `set_controls` (since `set_control` is now itself deprecated).

**Tests/examples/docs:** copy `tests/unit/vizro/actions/test_set_control.py` → `test_legacy_set_control.py`
(`pytestmark` + `pytest.warns`); migrate the whole `set_control` reference set — the e2e `set_control_*` dashboard
pages, `test_dom_elements`, `test_http_requests`, `tests_utils/.../constants.py`; migrate `examples/dev/app.py` +
`dev/yaml_version/dashboard.yaml` (`type: set_controls`); migrate docs — **`graph-table-actions.md` (~90 refs)** is the
big one, plus `controls.md`, `card.md`, `actions.md`, `filters.md`, `parameters.md`, `selectors.md`. Update the
`set_control` docstring examples to `set_controls`. Add `deprecations.md` section + `### Added` (set_controls) and
`### Deprecated` (set_control) changelog fragments. Regenerate schema + compendium.

---

## Item 3 — Cascader `full_path` default False → True  (branch `deprecation/cascader-full-path`)

**v1 behaviour:** `full_path` defaults to `True`. **0.1.61:** keep `default=False`, warn only when the user hasn't set
it (behaviour unchanged this release). Template = `set_variant_defaults` (`model_fields_set` detection).

**`src/vizro/models/_components/form/cascader.py`** — add a `@model_validator(mode="after")`:
```python
if "full_path" not in self.model_fields_set:
    warnings.warn(
        "The default of `Cascader.full_path` will change from False to True in Vizro 1.0.0 (<link>). "
        "Set `full_path=False` to keep current behaviour.",
        category=FutureWarning, stacklevel=…)
# Do NOT change behaviour in 0.1.61 — full_path stays False. (frozen=True, so a flip would need self.__dict__.)
```
Add an `❗Deprecated:` note to the `full_path` field `description` (keep `frozen=True`; adjust the "immutable once set"
wording only if needed).

**Avoid spurious internal warnings:** check whether hierarchical Filter auto-selection ever constructs a `Cascader`
without `full_path` (`DEFAULT_SELECTORS`/`SELECTORS["hierarchical"]`, `filter.py`); if so, set `full_path` explicitly
at that construction site to keep it quiet and lock current behaviour.

**Tests/docs:** add a `pytest.warns(FutureWarning)` test for the unset case; in existing cascader tests/fixtures
either set `full_path` explicitly or add a module `pytestmark` ignore so the suite stays green. Update
`selectors.md`/`filters.md`. Add `deprecations.md` section + `### Deprecated` changelog fragment.
(Downstream note for 1.0.0: `set_control` rejects `full_path=True` cascaders — flipping the default interacts with
targetability; a 1.0.0 concern, not this release.)

---

## Item 4 — Python 3.10 deprecation warning  (branch `deprecation/python-310`)

**v1 behaviour (deferred):** drop 3.10, bump `flask_caching>=2.5` (both pins in `vizro-core` + `vizro-experimental`
`pyproject.toml`), add 3.15 — following the `b7bd0218c` checklist (pyproject `requires-python`+classifiers, `hatch.toml`
matrix/default/lower-bounds/`all.pyX` env, all `.github/workflows/*` matrices + `PYTHON_VERSION`, `.readthedocs.yaml`,
`README`). **None of this happens in 0.1.61.**

**0.1.61:** emit a runtime `FutureWarning` once when `sys.version_info < (3, 11)`:
"Python 3.10 support will be removed in Vizro 1.0.0 (<link>). Upgrade to Python 3.11+." Location: `src/vizro/__init__.py`
(import-time, simplest/most visible) or `Vizro.__init__`/`build` (more controlled) — recommend package import with a
correct `stacklevel`. Add `deprecations.md` section + `### Deprecated` changelog fragment. No config/CI changes.

> **Sign-off flag:** this runtime version warning has **no precedent** (3.9/3.8 drops warned only via changelog). It's
> cheap and user-friendly, but if you'd rather match precedent we can drop the warning and announce via changelog +
> deprecations.md only. Also note 0.1.61 CI still runs 3.10, so we won't accidentally break it.

---

## deprecations.md & the 1.0.0 migration guide

Add one section per new item (mirror the `FutureWarning` text, expand with before/after), ordered by impact:
RangeSlider, set_control, Cascader `full_path`, Python 3.10 — after the existing Layout/actions/filter_interaction
sections (which get the 0.2.0→1.0.0 re-point). For 1.0.0: rename `deprecations.md` → `migration.md`, keep all entries,
append the changes we *couldn't* pre-warn (AgGrid/Table, `consistent_colors`, the actual 3.10 drop), and re-order by
theme/likelihood. (1.0.0 work — documented here, not done now.)

## Out of scope / deferred to 1.0.0
AgGrid↔Table rename; `consistent_colors` default flip; the real Python-3.10 drop + `flask_caching>=2.5` + Python 3.15;
and all *removals* (RangeSlider, set_control, Layout, Action `inputs`/static-args/built-in-in-Action, filter_interaction,
`full_path` default flip).

## Follow-ups (other packages — not this effort)
- **vizro-mcp**: `server.py` `deprecated_models` map (add `set_control`/`RangeSlider`; re-point filter_interaction→set_controls);
  `_utils/prompts.py` hardcoded selector list (drop RangeSlider) — note it already auto-excludes `__deprecated__` actions.
- **vizro-e2e-flow**: skills/evals naming RangeSlider/set_control.
- **vizro-ai**: references, if any.

---

## Verification (per branch + integration)
1. `hatch run lint` and `hatch run test-unit` (green; `filterwarnings=["error"]` means any stray `FutureWarning` fails).
2. New `pytest.warns(FutureWarning, match=…)` tests fire for old syntax; `test_legacy_*.py` suites pass with `pytestmark`.
3. **No spurious warnings from internal paths** — run `hatch run example scratch_dev` and `hatch run example dev`
   with a numerical Filter (auto RangeSlider), a hierarchical Cascader Filter, and default-synced controls; confirm the
   console is warning-free with new syntax, and each *old* syntax (`vm.RangeSlider`, `va.set_control`, unset `full_path`,
   Python 3.10) emits exactly one warning pointing at the user's line.
4. `hatch run schema` (new `set_controls` type + `Slider.range`); regenerate compendium/for-llms; `hatch run changelog:add` per item.
5. YAML back-compat: `type: range_slider` and `type: set_control` still validate (with warning); `type: slider`+`range: true`
   and `type: set_controls` validate clean.
