from __future__ import annotations

import logging
from functools import cached_property
from typing import Literal, Protocol, cast, runtime_checkable

from dash import get_relative_path, no_update, set_props
from pydantic import Field, JsonValue

from vizro.actions._abstract_action import _AbstractAction
from vizro.managers import model_manager
from vizro.models._models_utils import _log_call
from vizro.models.types import ControlType, ModelID, _normalize_action_notifications

logger = logging.getLogger(__name__)

# A complete range value has exactly two entries: [start, end].
_RANGE_VALUE_LEN = 2


# This defines what a model needs to implement for it to be capable of acting as the trigger of set_control.
@runtime_checkable
class _SupportsSetControl(Protocol):
    def _get_value_from_trigger(self, value: JsonValue, trigger: JsonValue) -> JsonValue: ...


class set_control(_AbstractAction):
    """Sets the value of one or more controls, which then update their targets.

    Abstract: Usage documentation
        [Graph and table interactions](../user-guides/graph-table-actions.md)

    `control` accepts a single control id or a list of control ids. Pass a list to set several controls from a single
    trigger (for example, one graph click that cross-filters multiple filters, or one selector that syncs several
    controls). The same `value` is sent to every targeted control and is reshaped to each control's own selector.

    The following Vizro models can be a source of `set_control`:

    * [`AgGrid`][vizro.models.AgGrid]: triggers `set_control` when `cellClicked` or `selectedRows` changes (for example
    after a cell click or when the row selection changes). `value` can be:

        * `"cell"`, `"column"`, or `"row"` to use the clicked cell's value, column id, or row id respectively.
        * Any other string to treat as a column name, taking values from the selected row(s).
    * [`Graph`][vizro.models.Graph]: triggers `set_control` when the user clicks on data in the graph. `value` is a
    string that can be used in two ways to specify how to set `control`:

        * Column from which to take the value. This requires you to set `custom_data` in the graph's `figure` function.
        * String to [traverse a Box](https://github.com/cdgriffith/Box/wiki/Types-of-Boxes#box-dots) that contains the
        trigger data [`clickData["points"][0]`](https://dash.plotly.com/interactive-graphing). This is typically
        useful for a positional variable, for example `"x"`, and does not require setting `custom_data`.

    * [`Figure`][vizro.models.Figure]: triggers `set_control` when the user clicks on the figure. `value` specifies a
    literal value to set `control` to.
    * [`Button`][vizro.models.Button]: triggers `set_control` when the user clicks on the button. `value` specifies a
    literal value to set `control` to.
    * [`Card`][vizro.models.Card]: triggers `set_control` when the user clicks on the card. `value` specifies a
    literal value to set `control` to.

    Example: `AgGrid` as trigger
        ```python
        import vizro.actions as va

        vm.AgGrid(
            figure=dash_ag_grid(iris),
            actions=va.set_control(control="target_control", value="species"),
        )
        ```

    Example: `Graph` as trigger with `custom_data`
        ```python
        import vizro.actions as va

        vm.Graph(
            figure=px.scatter(iris, x="sepal_width", y="sepal_length", custom_data="species"),
            actions=va.set_control(control="target_control", value="species"),
        )
        ```

    Example: `Graph` as trigger without `custom_data`
        ```python
        import vizro.actions as va

        vm.Graph(
            figure=px.box(iris, x="species", y="sepal_length"),
            actions=va.set_control(control="target_control", value="x"),
        )
        ```

    Example: `Figure` as trigger
        ```python
        import vizro.actions as va
        from vizro.figures import kpi_card

        vm.Figure(
            figure=kpi_card(tips, value_column="tip", title="Click KPI to set control to A"),
            actions=va.set_control(control="target_control", value="A"),
        )
        ```

    Example: `Button` as trigger
        ```python
        import vizro.actions as va

        vm.Button(
            text="Click to set control to A",
            actions=va.set_control(control="target_control", value="A"),
        )
        ```

    Example: `Card` as trigger
        ```python
        import vizro.actions as va

        vm.Card(
            title="Click Card to set control to A",
            actions=va.set_control(control="target_control", value="A"),
        )
        ```

    Example: target multiple controls at once
        ```python
        import vizro.actions as va

        vm.Graph(
            figure=px.scatter(iris, x="sepal_width", y="sepal_length", custom_data="species"),
            actions=va.set_control(control=["target_control_1", "target_control_2"], value="species"),
        )
        ```
    """

    type: Literal["set_control"] = "set_control"
    control: ModelID | list[ModelID] = Field(
        description="Filter or Parameter component id(s) to be affected by the trigger. Provide a single id to set "
        "one control, or a list of ids to set several controls at once. Each control can be on the same page as the "
        "trigger or on a different page: a different-page control is kept in sync through the internal "
        "`vizro_controls_store`, and its new value is applied when that page is opened."
    )

    # TODO AM-PP: How about making it optional with default=None.
    value: JsonValue = Field(
        description="Value to take from trigger and send to the `target`. Format depends on the model "
        "that triggers `set_control`."
    )

    @property
    def _control_ids(self) -> list[ModelID]:
        """Normalize `control` (a single id or a list) to a de-duplicated, order-preserving list of control ids.

        Duplicates are collapsed because two Dash `Output`s pointing at the same component within a single callback
        is an error, not merely redundant.
        """
        control_ids = [self.control] if isinstance(self.control, str) else list(self.control)
        return list(dict.fromkeys(control_ids))

    @_log_call
    def pre_build(self):
        # Validate that action's parent model supports `set_control` action.
        if not isinstance(self._parent_model, _SupportsSetControl):
            raise ValueError(
                f"`set_control` action was added to the model with ID `{self._parent_model.id}`, "
                "but this action can only be used with models that support it "
                "(for example, Graph, AgGrid, Figure, and so on). "
                "See all models that can source a `set_control` at "
                "https://vizro.readthedocs.io/en/stable/pages/API-reference/actions/#vizro.actions.set_control"
            )

        # An empty `control` (e.g. `control=[]`) has nothing to set: it would produce zero callback outputs and fail at
        # runtime, so reject it clearly at build time.
        if not self._control_ids:
            raise ValueError(
                f"`set_control` action on model `{self._parent_model.id}` has an empty `control`. "
                "Provide at least one Filter or Parameter id to set."
            )

        from vizro.models._controls._controls_utils import SELECTORS, _is_hierarchical_selector

        # Validate every targeted control and classify it by page (order-preserving), so the callback can update
        # same-page controls directly through its outputs and sync cross-page controls through `vizro_controls_store`.
        action_page = model_manager._get_model_page(self)
        self._same_page_controls: list[ModelID] = []
        self._cross_page_controls: list[ModelID] = []
        cross_page_pages = []  # pages of the cross-page controls, used to resolve the drill-through navigation target

        for control_id in self._control_ids:
            # Validate that the control exists in the dashboard.
            control_model = cast(ControlType, model_manager[control_id]) if control_id in model_manager else None
            control_model_page = model_manager._get_model_page(control_model) if control_model else None
            if control_model is None or control_model_page is None:
                raise ValueError(
                    f"Model with ID `{control_id}` used as a `control` in `set_control` action not found in the "
                    f"dashboard. Please provide a valid control ID that exists in the dashboard."
                )

            # Validate that target control model is Filter or Parameter.
            if not hasattr(control_model, "selector"):
                raise TypeError(
                    f"Model with ID `{control_id}` used as a `control` in `set_control` action must be a control "
                    f"model (for example, Filter, Parameter)."
                )

            # A path-mode Cascader (full_path=True) identifies a selection by its full root-to-leaf path. A trigger
            # (Graph/AgGrid) only supplies a single column value, which cannot reconstruct a path, so `set_control`
            # is disabled for it. Leaf mode (full_path=False) works like a flat selector and is supported.
            selector = getattr(control_model, "selector", None)
            if _is_hierarchical_selector(selector) and getattr(selector, "full_path", False):
                raise ValueError(
                    f"`set_control` cannot target control `{control_id}` because its Cascader selector uses "
                    f"full_path=True. A trigger supplies a single leaf value that cannot be resolved to a full "
                    f"root-to-leaf path. Use a Cascader with full_path=False (leaf mode) to enable `set_control`."
                )

            if control_model_page == action_page:
                self._same_page_controls.append(control_id)
            else:
                self._cross_page_controls.append(control_id)
                cross_page_pages.append(control_model_page)

        # Distinguish two cross-page use cases by what triggers the action:
        #   - triggered by a control's own selector (Dropdown, Checklist, ...) -> "syncing controls": stay on the
        #     current page, the value is applied to the target when its page is next opened;
        #   - triggered by a figure/action component (Graph, AgGrid, Figure, Button, Card, ...) -> "drill-through":
        #     navigate to the target control's page so the user is taken to the drilled-into detail.
        # Only relevant when a target is on a different page (see `function`).
        selector_types = tuple(selector for selectors in SELECTORS.values() for selector in selectors)
        self._is_drill_through = not isinstance(self._parent_model, selector_types)

        # Resolve the drill-through navigation target once (a control's page is fixed at build time). Drill-through
        # navigates only when the destination is unambiguous: every cross-page target lives on a single page. When they
        # span several pages there is no single "detail view" to open (and only one `vizro_url`), so we never navigate
        # (path stays None). `get_relative_path` is deferred to `function` as it needs the running app's routing config.
        distinct_pages = {page.id: page for page in cross_page_pages}
        self._drill_through_path = next(iter(distinct_pages.values())).path if len(distinct_pages) == 1 else None

    def function(self, _trigger, _controls_store):
        value = cast(_SupportsSetControl, self._parent_model)._get_value_from_trigger(self.value, _trigger)

        # Returning no_update will leave the control(s) unchanged and their actions will not be triggered.
        # Don't raise PreventUpdate exception as it stops other actions in the chain from running.
        # Reuse the framework helper so the no_update shape always matches `outputs` (scalar for one output, else one
        # entry per output) - a single source of truth for the 1-element-list -> scalar collapse rule.
        if value is no_update:
            return self._no_update_outputs(self._transformed_outputs)

        # Same-page targets: their selectors are mounted, so update them directly through the callback outputs. Each
        # value is reshaped for its own selector; a target that cannot accept the value contributes no_update so the
        # other targets are still updated.
        results = [
            self._shape_value_for_control(control_id, value, _controls_store) for control_id in self._same_page_controls
        ]

        # Different-page targets: their selectors are not mounted, so they cannot be callback outputs. Persist each new
        # value into `vizro_controls_store` (via set_props, as the store is only a State here); the target page's sync
        # callback applies this `currentValue` to the selector when that page is opened.
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
                # Drill-through navigates to the pre-resolved target page (see pre_build); it is None when the targets
                # span several pages, in which case we stay put and each page applies its value from the store on open.
                # A control-to-control sync never navigates.
                if self._is_drill_through and self._drill_through_path is not None:
                    navigated = get_relative_path(self._drill_through_path)

            # `vizro_url.pathname` is the last output whenever there are cross-page targets (see `outputs`).
            results.append(navigated)

        # A single output must return a scalar; multiple outputs must return a positionally-aligned list.
        return results[0] if len(results) == 1 else results

    def _shape_value_for_control(self, control_id, value, controls_store):
        """Shape the trigger-derived `value` for one target control, or return `no_update` to skip just that control.

        The raw value is derived once from the trigger; this resets it to the control's original value when the
        trigger yields None, then reshapes it to the target selector (multi vs range vs single-value). Returns
        `no_update` when the value cannot be applied to this control (an incomplete range, or a multi-item list into
        a single-value selector), leaving that control unchanged without affecting the others.
        """
        from vizro.models import AgGrid, Checklist, Graph, RangeSlider

        selector = cast(ControlType, model_manager[control_id]).selector

        # If value is None then reset control to original value. Fall back to the selector's build-time value if the
        # store entry is missing/incomplete - a persisted (storage_type="session") store can be stale after a control
        # was added or renamed, so we must not assume the key exists.
        if value is None:
            control_store = controls_store.get(control_id, {})
            value = control_store.get("originalValue", selector.value)

        is_multi = getattr(selector, "multi", isinstance(selector, Checklist))
        is_range = getattr(selector, "range", isinstance(selector, RangeSlider))

        # A leaf-mode Cascader (the only kind that reaches here — path mode is rejected at pre_build) reshapes
        # like a flat categorical selector: a multi-select value is a list of leaves, a single-select a scalar.
        if is_multi:
            return value if isinstance(value, list) else [value]
        if is_range:
            # AgGrid/Graph emit the picked values in selection (click) order, so a multi-value trigger can arrive
            # with its ends out of order; reorder into [min, max] to form a valid range. A range *selector*
            # (RangeSlider/DatePicker/DateTimePicker/TimePicker) instead emits an authoritative positional
            # [start, end] that must be preserved as-is: its ends are not always lexically ordered (e.g. a
            # DateTimePicker with a timed start and a date-only, whole-day end), so reordering would misplace them.
            reorder_range = isinstance(self._parent_model, (AgGrid, Graph))
            normalized = self._normalize_range_value(value, reorder=reorder_range)
            # An incomplete/empty range must not be synced (see `_normalize_range_value`); skip just this control.
            return no_update if normalized is None else normalized
        if isinstance(value, list):
            # Target is single-value selector but value is list.
            if len(value) == 1:
                return value[0]
            logger.debug(
                "set_control %s received list with %d items but targets a single-value %s %s; skipping this control",
                self.id,
                len(value),
                type(selector).__name__,
                control_id,
            )
            return no_update
        return value

    def _write_cross_page_store_entry(self, control_id, value, controls_store):
        """Persist a cross-page target's new value into `vizro_controls_store`.

        If the control's entry is missing (a persisted storage_type="session" store can be stale after a control was
        added/renamed), rebuild the full entry - mirroring Dashboard._make_page_layout - rather than writing only
        `currentValue`. A complete entry keeps cross-page syncing working (the sync callback needs `crossPageTarget`,
        `selectorId`, etc.) instead of merely avoiding a KeyError. `crossPageTarget` is True here by construction:
        this control is the target of a cross-page set_control.
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
        # `vizro_controls_store` via set_props instead, so they contribute only the shared `vizro_url.pathname` output
        # (used to navigate on drill-through; `no_update` for a control-to-control sync so the page does not change).
        if self._cross_page_controls:
            return [*self._same_page_controls, "vizro_url.pathname"]
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
            # A scalar empty value (None or "") is an incomplete/cleared selection, exactly like the list cases
            # below: don't sync it (min/max would raise on None, and "" would seed a meaningless ["", ""] range).
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
        # set_control has only a subtle visual cue (the control value changing), so show the success notification.
        # cached_property is used as the notification models are built once per action instead of being re-minted
        # (with fresh model_manager entries) on every callback run.
        return _normalize_action_notifications({"success": "Controls updated.", "error": "Setting controls failed."})
