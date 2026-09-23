from __future__ import annotations

import logging
from functools import cached_property
from typing import Literal, Protocol, cast, runtime_checkable

from dash import get_relative_path, no_update, set_props
from pydantic import Field, JsonValue, model_validator
from typing_extensions import deprecated

from vizro.actions._abstract_action import _AbstractAction
from vizro.managers import model_manager
from vizro.models._models_utils import _log_call
from vizro.models.types import ControlType, ModelID, _normalize_action_notifications

logger = logging.getLogger(__name__)

# A complete range value has exactly two entries: [start, end].
_RANGE_VALUE_LEN = 2


# What a model must implement to be a set_controls trigger.
@runtime_checkable
class _SupportsSetControl(Protocol):
    def _get_value_from_trigger(self, value: JsonValue, trigger: JsonValue) -> JsonValue: ...


class set_controls(_AbstractAction):
    """Sets the value of one or more controls, which then update their targets.

    Abstract: Usage documentation
        [Graph and table interactions](../user-guides/graph-table-actions.md)

    `controls` is a list of control ids. Pass several ids to set several controls from a single trigger (for example,
    one graph click that cross-filters multiple filters, or one selector that syncs several controls). The same `value`
    is sent to every targeted control and is reshaped to each control's own selector.

    The following Vizro models can be a source of `set_controls`:

    * [`AgGrid`][vizro.models.AgGrid]: triggers `set_controls` when `cellClicked` or `selectedRows` changes (for example
    after a cell click or when the row selection changes). `value` can be:

        * `"cell"`, `"column"`, or `"row"` to use the clicked cell's value, column id, or row id respectively.
        * Any other string to treat as a column name, taking values from the selected row(s).
    * [`Graph`][vizro.models.Graph]: triggers `set_controls` when the user clicks on data in the graph. `value` is a
    string that can be used in two ways to specify how to set `controls`:

        * Column from which to take the value. This requires you to set `custom_data` in the graph's `figure` function.
        * String to [traverse a Box](https://github.com/cdgriffith/Box/wiki/Types-of-Boxes#box-dots) that contains the
        trigger data [`clickData["points"][0]`](https://dash.plotly.com/interactive-graphing). This is typically
        useful for a positional variable, for example `"x"`, and does not require setting `custom_data`.

    * [`Figure`][vizro.models.Figure]: triggers `set_controls` when the user clicks on the figure. `value` specifies a
    literal value to set `controls` to.
    * [`Button`][vizro.models.Button]: triggers `set_controls` when the user clicks on the button. `value` specifies a
    literal value to set `controls` to.
    * [`Card`][vizro.models.Card]: triggers `set_controls` when the user clicks on the card. `value` specifies a
    literal value to set `controls` to.

    `value` is required for `Graph` and `AgGrid` (it is the directive for what to extract from the click). For
    `Figure`, `Card`, and `Button` it is the literal to set, and `value=None` resets the target control(s) to their
    default value. `value` may be omitted only when a control's own selector syncs to another control (via that
    control's `targets`): the sync uses the selector's live value and ignores `value`.

    Example: `AgGrid` as trigger
        ```python
        import vizro.actions as va

        vm.AgGrid(
            figure=dash_ag_grid(iris),
            actions=va.set_controls(controls=["target_control"], value="species"),
        )
        ```

    Example: `Graph` as trigger with `custom_data`
        ```python
        import vizro.actions as va

        vm.Graph(
            figure=px.scatter(iris, x="sepal_width", y="sepal_length", custom_data="species"),
            actions=va.set_controls(controls=["target_control"], value="species"),
        )
        ```

    Example: `Graph` as trigger without `custom_data`
        ```python
        import vizro.actions as va

        vm.Graph(
            figure=px.box(iris, x="species", y="sepal_length"),
            actions=va.set_controls(controls=["target_control"], value="x"),
        )
        ```

    Example: `Figure` as trigger
        ```python
        import vizro.actions as va
        from vizro.figures import kpi_card

        vm.Figure(
            figure=kpi_card(tips, value_column="tip", title="Click KPI to set control to A"),
            actions=va.set_controls(controls=["target_control"], value="A"),
        )
        ```

    Example: `Button` as trigger
        ```python
        import vizro.actions as va

        vm.Button(
            text="Click to set control to A",
            actions=va.set_controls(controls=["target_control"], value="A"),
        )
        ```

    Example: `Card` as trigger
        ```python
        import vizro.actions as va

        vm.Card(
            title="Click Card to set control to A",
            actions=va.set_controls(controls=["target_control"], value="A"),
        )
        ```

    Example: target multiple controls at once
        ```python
        import vizro.actions as va

        vm.Graph(
            figure=px.scatter(iris, x="sepal_width", y="sepal_length", custom_data="species"),
            actions=va.set_controls(controls=["target_control_1", "target_control_2"], value="species"),
        )
        ```

    Example: a control selector as trigger (no `value` needed)
        A control's own selector can be the source. Here a bare `RadioItems` (whitelisted as a page component with
        `add_type`) syncs its selected value to two filters. `value` is omitted: a selector sync sends the selector's
        own live value, so there is nothing to specify.
        ```python
        import vizro.models as vm
        import vizro.actions as va

        vm.Page.add_type("components", vm.RadioItems)  # allow a bare selector as a page component

        vm.RadioItems(
            options=["setosa", "versicolor", "virginica"],
            actions=va.set_controls(controls=["species_filter_1", "species_filter_2"]),
        )
        ```
    """

    type: Literal["set_controls"] = "set_controls"
    controls: list[ModelID] = Field(
        default=[],
        description="Filter or Parameter component ids to be affected by the trigger. Provide a list of ids to set "
        "several controls at once. Each control can be on the same page as the trigger or on a different page: a "
        "different-page control is kept in sync through the internal `vizro_controls_store`, and its new value is "
        "applied when that page is opened.",
    )

    value: JsonValue = Field(
        default=None,
        description="Value to take from the trigger and send to the target control(s). Its format depends on the "
        "triggering model (see the list above): for `Graph`/`AgGrid` it is an extraction directive (a column name or "
        "lookup) and is required; for `Figure`/`Card`/`Button` it is the literal value to set, and `value=None` "
        "resets the target control(s) to their default value. It may be omitted (defaults to `None`) only when a "
        "control's own selector syncs to another control, where `value` is ignored and the selector's live value is "
        "used instead.",
    )

    @property
    def _control_ids(self) -> list[ModelID]:
        """Return `controls` as a de-duplicated, order-preserving list of ids.

        Duplicates are collapsed because two Dash `Output`s on the same component in one callback is an error.
        """
        return list(dict.fromkeys(self.controls))

    @_log_call
    def pre_build(self):
        # Parent model must be able to source set_controls.
        if not isinstance(self._parent_model, _SupportsSetControl):
            raise ValueError(
                f"`set_controls` action was added to the model with ID `{self._parent_model.id}`, "
                "but this action can only be used with models that support it "
                "(for example, Graph, AgGrid, Figure, and so on). "
                "See all models that can source a `set_controls` at "
                "https://vizro.readthedocs.io/en/stable/pages/API-reference/actions/#vizro.actions.set_controls"
            )

        # An empty `controls` (e.g. []) produces zero callback outputs and fails at runtime; reject it at build time.
        if not self._control_ids:
            raise ValueError(
                f"`set_controls` action on model `{self._parent_model.id}` has an empty `controls`. "
                "Provide at least one Filter or Parameter id to set."
            )

        from vizro.models import AgGrid, Graph
        from vizro.models._controls._controls_utils import SELECTORS, _is_hierarchical_selector

        # Validate each target and split by page (order-preserving): same-page controls are updated via the callback
        # outputs, cross-page controls through `vizro_controls_store`.
        action_page = model_manager._get_model_page(self)
        self._same_page_controls: list[ModelID] = []
        self._cross_page_controls: list[ModelID] = []
        cross_page_pages = []  # pages of the cross-page controls, used to resolve the drill-through navigation target

        for control_id in self._control_ids:
            # Control must exist in the dashboard.
            control_model = cast(ControlType, model_manager[control_id]) if control_id in model_manager else None
            control_model_page = model_manager._get_model_page(control_model) if control_model else None
            if control_model is None or control_model_page is None:
                raise ValueError(
                    f"Model with ID `{control_id}` used as a `control` in `set_controls` action not found in the "
                    f"dashboard. Please provide a valid control ID that exists in the dashboard."
                )

            # Target must be a control model (Filter/Parameter).
            if not hasattr(control_model, "selector"):
                raise TypeError(
                    f"Model with ID `{control_id}` used as a `control` in `set_controls` action must be a control "
                    f"model (for example, Filter, Parameter)."
                )

            # A path-mode Cascader (full_path=True) identifies a selection by its full root-to-leaf path. A trigger
            # (Graph/AgGrid) only supplies a single column value, which cannot reconstruct a path, so `set_controls`
            # is disabled for it. Leaf mode (full_path=False) works like a flat selector and is supported.
            selector = getattr(control_model, "selector", None)
            if _is_hierarchical_selector(selector) and getattr(selector, "full_path", False):
                raise ValueError(
                    f"`set_controls` cannot target control `{control_id}` because its Cascader selector uses "
                    f"full_path=True. A trigger supplies a single leaf value that cannot be resolved to a full "
                    f"root-to-leaf path. Use a Cascader with full_path=False (leaf mode) to enable `set_controls`."
                )

            if control_model_page == action_page:
                self._same_page_controls.append(control_id)
            else:
                self._cross_page_controls.append(control_id)
                cross_page_pages.append(control_model_page)

        # The trigger decides cross-page behavior (see `function`): a control's own selector (Dropdown, Checklist, ...)
        # just "syncs" - stay put, apply on the target's next open; a figure/component (Graph, AgGrid, Button, ...)
        # "drills through" - navigate to the target's page.
        selector_types = tuple(selector for selectors in SELECTORS.values() for selector in selectors)
        self._is_drill_through = not isinstance(self._parent_model, selector_types)

        # `value` is an extraction directive for Graph/AgGrid (a column name or lookup used to pull the value out of
        # the click), so it is required for them: a missing value would only surface as a confusing "couldn't find
        # value None" at click time. Catch it here with a message tailored to the trigger. It is intentionally
        # optional elsewhere: Figure/Card/Button treat `value=None` as "reset the target(s) to their default", and a
        # selector-driven sync ignores `value` entirely (the selector's own live value is used).
        if self.value is None and isinstance(self._parent_model, (Graph, AgGrid)):
            value_hint = (
                'a column name present in the figure\'s `custom_data`, or a positional lookup such as "x" or "y"'
                if isinstance(self._parent_model, Graph)
                else '"cell", "column", "row", or a column name'
            )
            raise ValueError(
                f"`set_controls` triggered by `{type(self._parent_model).__name__}` model "
                f"`{self._parent_model.id}` requires a `value`: {value_hint}. See "
                "https://vizro.readthedocs.io/en/stable/pages/API-reference/actions/#vizro.actions.set_controls"
            )

        # Resolve the navigation target once (a control's page is fixed at build time). A drill-through navigates only
        # when every target is on one single *other* page:
        #   - no same-page target: staying to update a current-page control contradicts leaving, and that live selector
        #     update would race the navigation (two uncoordinated URL writes);
        #   - one cross-page destination: several pages give no single "detail view" to open (there is one `vizro_url`).
        # Otherwise path stays None: same-page targets are set live, cross-page ones applied from the store on open.
        # `get_relative_path` is deferred to `function` as it needs the running app's routing config.
        distinct_pages = {page.id: page for page in cross_page_pages}
        navigates = not self._same_page_controls and len(distinct_pages) == 1
        self._drill_through_path = next(iter(distinct_pages.values())).path if navigates else None

    def function(self, _trigger, _controls_store):
        value = cast(_SupportsSetControl, self._parent_model)._get_value_from_trigger(self.value, _trigger)

        # no_update leaves the control(s) unchanged and skips their actions. Don't raise PreventUpdate - it would stop
        # the rest of the chain. The helper shapes no_update to match `outputs` (scalar for one output, else a list).
        if value is no_update:
            return self._no_update_outputs(self._transformed_outputs)

        # Same-page targets: selectors are mounted, so update them directly via the callback outputs. Each value is
        # reshaped per selector; one that can't accept it contributes no_update so the others still update.
        results = [
            self._shape_value_for_control(control_id, value, _controls_store) for control_id in self._same_page_controls
        ]

        # Cross-page targets: selectors aren't mounted, so they can't be callback outputs. Persist each value into
        # `vizro_controls_store` via set_props (it's only a State here); the target page's sync callback applies this
        # `currentValue` when that page opens.
        navigated = no_update
        if self._cross_page_controls:
            wrote_any = False
            for control_id in self._cross_page_controls:
                shaped_value = self._shape_value_for_control(control_id, value, _controls_store)
                if shaped_value is no_update:
                    continue
                self._write_cross_page_store_entry(control_id, shaped_value, _controls_store)
                wrote_any = True

            if wrote_any:
                set_props("vizro_controls_store", {"data": _controls_store})
                # Navigate to the pre-resolved target page (see pre_build); it is None (stay put) when there is a
                # same-page target or the cross-page targets span several pages. A control-to-control sync never
                # navigates.
                if self._is_drill_through and self._drill_through_path is not None:
                    navigated = get_relative_path(self._drill_through_path)

            # `vizro_url.href` is the last output whenever there are cross-page targets (see `outputs`).
            results.append(navigated)

        # A single output must return a scalar; multiple outputs must return a positionally-aligned list.
        return results[0] if len(results) == 1 else results

    def _shape_value_for_control(self, control_id, value, controls_store):
        """Shape the trigger-derived `value` for one target control, or return `no_update` to skip just that control.

        The raw value is derived once from the trigger; a figure/component drill-through's None is the reset sentinel
        (restore the control's original value), while a selector sync propagates its live value (so a cleared source
        clears the target). It then reshapes the value to the target selector (multi vs range vs single-value).
        Returns `no_update` when the value cannot be applied to this control (an incomplete range, or a multi-item
        list into a single-value selector), leaving that control unchanged without affecting the others.
        """
        from vizro.models import AgGrid, Checklist, Graph, RangeSlider

        selector = cast(ControlType, model_manager[control_id]).selector

        # A drill-through's None is the reset sentinel: restore the control's original value (falling back to the
        # selector's build-time value if a session-persisted store entry is stale/missing after a control was
        # added/renamed). A selector sync instead propagates the source's live value, so a cleared source (None)
        # clears the target rather than resetting it, keeping the two controls mirrored.
        if value is None and self._is_drill_through:
            control_store = controls_store.get(control_id, {})
            value = control_store.get("originalValue", selector.value)

        is_multi = getattr(selector, "multi", isinstance(selector, Checklist))
        is_range = getattr(selector, "range", isinstance(selector, RangeSlider))

        # A leaf-mode Cascader (the only kind that reaches here — path mode is rejected at pre_build) reshapes
        # like a flat categorical selector: a multi-select value is a list of leaves, a single-select a scalar.
        if is_multi:
            # A cleared source (None, from a selector sync) clears a multi-select target rather than seeding [None].
            if value is None:
                return []
            return value if isinstance(value, list) else [value]
        if is_range:
            # AgGrid/Graph emit values in selection (click) order, so a multi-value trigger can arrive out of order;
            # reorder into [min, max]. A range selector emits an authoritative positional [start, end], kept as-is (its
            # ends aren't always ordered). See `_normalize_range_value`.
            reorder_range = isinstance(self._parent_model, (AgGrid, Graph))
            normalized = self._normalize_range_value(value, reorder=reorder_range)
            # An incomplete/empty range must not be synced (see `_normalize_range_value`); skip just this control.
            return no_update if normalized is None else normalized
        if isinstance(value, list):
            # Target is single-value selector but value is list.
            if len(value) == 1:
                return value[0]
            logger.debug(
                "set_controls %s received list with %d items but targets a single-value %s %s; skipping this control",
                self.id,
                len(value),
                type(selector).__name__,
                control_id,
            )
            return no_update
        return value

    def _write_cross_page_store_entry(self, control_id, value, controls_store):
        """Persist a cross-page target's new value into `vizro_controls_store`.

        If the entry is missing (a session-persisted store can be stale after a control was added/renamed), rebuild the
        full entry - mirroring Dashboard._make_page_layout - so cross-page sync keeps working (the sync callback needs
        `crossPageTarget`, `selectorId`, etc.), not merely avoid a KeyError. `crossPageTarget` is True by construction:
        this control is the target of a cross-page set_controls.
        """
        if control_id not in controls_store:
            control_model = cast(ControlType, model_manager[control_id])
            controls_store[control_id] = {
                "originalValue": control_model.selector.value,
                "pageId": model_manager._get_model_page(control_model).id,
                "selectorId": control_model.selector.id,
                "showInURL": control_model.show_in_url,
                "crossPageTarget": True,
            }
        controls_store[control_id]["currentValue"] = value

    @property
    def outputs(self):  # type: ignore[override]
        # Same-page targets are real callback outputs (their selectors are mounted). Cross-page targets are written to
        # `vizro_controls_store` via set_props instead, so they contribute only the shared `vizro_url.href` output
        # (used to navigate on drill-through; `no_update` for a control-to-control sync so the page does not change).
        # We navigate via `href` (the full target) rather than `pathname`: when the source page has a `show_in_url`
        # control, `page.js` rewrites the query string with `history.replaceState`, which desyncs `vizro_url` from the
        # browser URL. A `pathname`-only `callback-nav` then reconciles against that stale state and fails to navigate
        # (it re-asserts the current path); a full `href` navigates unambiguously regardless of the desync.
        if self._cross_page_controls:
            return [*self._same_page_controls, "vizro_url.href"]
        # All targets on the same page: a single target returns a bare id (one Output); several return a list.
        return self._same_page_controls[0] if len(self._same_page_controls) == 1 else self._same_page_controls

    @staticmethod
    def _normalize_range_value(value, *, reorder):
        """Shape a trigger value into a range control's [start, end], or None if it must not be synced.

        Returns None (meaning "do not sync") for an empty or incomplete selection. An incomplete range arrives
        mid-edit as e.g. [date, None] from a DatePicker after its first click, or ["10:00", ""] from a Time/DateTime
        picker before the second value is set. Such values must not be synced: min/max would raise on None (a 500
        error) and, for "", would drop the single set value into the wrong slot (["10:00", ""] -> ["", "10:00"], so
        the start lands in the end). The sync then happens once the second value is selected, exactly as the source.

        ``reorder`` controls the two-element case. A selection-order source (an AgGrid row selection or a Graph
        point selection) can emit the two ends in the order they were clicked, so ``reorder=True`` sorts them into
        [min, max] to avoid an inverted [start > end] range that filters to nothing. A range selector emits an
        authoritative positional [start, end] (``reorder=False``) that is kept as-is, because its ends are not
        always lexically ordered (e.g. a DateTimePicker whose start carries a time but whose end is a date-only,
        whole-day value), so sorting would misplace them. More than two entries can only come from a multi-selection
        source, which has no positional start/end, so it always collapses to the spanning [min, max].
        """
        if not isinstance(value, list):
            # A scalar empty value (None or "") is an incomplete/cleared selection: don't sync it (min/max would raise
            # on None, and "" would seed a meaningless ["", ""] range).
            if value is None or value == "":
                return None
            return [value, value]
        if len(value) == 0 or any(item is None or item == "" for item in value):
            return None
        if len(value) == 1:
            return [value[0], value[0]]
        if reorder or len(value) > _RANGE_VALUE_LEN:
            return [min(value), max(value)]
        return value

    @cached_property
    def notifications(self):  # type: ignore[override]
        # set_controls's only visual cue is the control value changing, so surface a success notification.
        # cached_property builds the notification models once per action instead of re-minting them (with fresh
        # model_manager entries) on every callback run.
        return _normalize_action_notifications({"success": "Controls updated.", "error": "Setting controls failed."})


@deprecated(
    "`set_control` is deprecated and will not exist in Vizro 1.0.0 "
    "(https://vizro.readthedocs.io/en/stable/pages/API-reference/deprecations/#set_control-action). "
    "Use `set_controls` with `controls` as a list of ids instead.",
    category=FutureWarning,
)
class set_control(set_controls):
    """Deprecated. Use [`set_controls`][vizro.actions.set_controls] with `controls` as a list of ids instead."""

    type: Literal["set_control"] = "set_control"  # type: ignore[assignment]
    control: ModelID | list[ModelID] = Field(
        description="Filter or Parameter component id(s) to be affected by the trigger. Provide a single id or a list "
        "of ids. Deprecated: use `set_controls` with `controls` instead."
    )

    @model_validator(mode="after")
    def _map_control_to_controls(self):
        # Map the legacy `control` (single id or list) onto the canonical `controls` list. Written via __dict__ to
        # bypass validate_assignment; `control` is already validated so the ids are valid ModelIDs.
        self.__dict__["controls"] = [self.control] if isinstance(self.control, str) else list(self.control)
        return self
