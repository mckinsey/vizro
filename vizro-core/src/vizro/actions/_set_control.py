from __future__ import annotations

import base64
import json
from typing import Literal, Protocol, cast, runtime_checkable

from dash import get_relative_path
from pydantic import Field, JsonValue

from vizro.actions._abstract_action import _AbstractAction
from vizro.managers import model_manager
from vizro.models._models_utils import _log_call
from vizro.models.types import ControlType, ModelID


# This defines what a model needs to implement for it to be capable of acting as the trigger of set_control.
@runtime_checkable
class _SupportsSetControl(Protocol):
    def _get_value_from_trigger(self, value: JsonValue, trigger: JsonValue) -> JsonValue: ...


def _encode_to_base64(value):
    json_bytes = json.dumps(value, separators=(",", ":")).encode("utf-8")
    b64_bytes = base64.urlsafe_b64encode(json_bytes)
    return f"b64_{b64_bytes.decode('utf-8').rstrip('=')}"


class set_control(_AbstractAction):
    """Sets the value of a control, which then updates its targets.

    Abstract: Usage documentation
        [Graph and table interactions](../user-guides/graph-table-actions.md)

    The following Vizro models can be a source of `set_control`:

    * [`AgGrid`][vizro.models.AgGrid]: triggers `set_control` when user clicks on a row in the table. `value` is string
    specifying which column in the clicked row is used to set `control`.
    * [`Graph`][vizro.models.Graph]: triggers `set_control` when user clicks on data in the graph. `value` is string
    that can be used in two ways to specify how to set `control`:

        * Column from which to take the value. This requires you to set `custom_data` in the graph's `figure` function.
        * String to [traverse a Box](https://github.com/cdgriffith/Box/wiki/Types-of-Boxes#box-dots) that contains the
        trigger data [`clickData["points"][0]`](https://dash.plotly.com/interactive-graphing). This is typically
        useful for a positional variable, for example `"x"`, and does not require setting `custom_data`.

    * [`Figure`][vizro.models.Figure]: triggers `set_control` when user clicks on the figure. `value` specifies a
    literal value to set `control` to.
    * [`Button`][vizro.models.Button]: triggers `set_control` when user clicks on the button. `value` specifies a
    literal value to set `control` to.
    * [`Card`][vizro.models.Card]: triggers `set_control` when user clicks on the card. `value` specifies a
    literal value to set `control` to.

    Args:
        control (ModelID): Control whose value is set. If this is on a different page from the trigger then it must have
            `show_in_url=True`. The control's selector must be categorical (e.g. Dropdown, RadioItems, Checklist).
        value (JsonValue): Value taken from trigger to set `control`. Format depends on the source model that triggers
            `set_control`.

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
    """

    type: Literal["set_control"] = "set_control"
    control: ModelID = Field(
        description="Filter or Parameter component id to be affected by the trigger."
        "If the control is on a different page to the trigger then it must have `show_in_url=True`."
    )
    value: JsonValue = Field(
        description="Value to take from trigger and send to the `target`. Format depends on the model "
        "that triggers `set_control`."
    )

    @_log_call
    def pre_build(self):
        from vizro.models._controls._controls_utils import _is_categorical_selector

        # Validate that action's parent model supports `set_control` action.
        if not isinstance(self._parent_model, _SupportsSetControl):
            raise ValueError(
                f"`set_control` action was added to the model with ID `{self._parent_model.id}`, "
                "but this action can only be used with models that support it (e.g. Graph, AgGrid, Figure etc). "
                "See all models that can source a `set_control` at "
                "https://vizro.readthedocs.io/en/stable/pages/API-reference/actions/#vizro.actions.set_control"
            )

        # Validate that action's control exists in the dashboard.
        control_model = cast(ControlType, model_manager[self.control]) if self.control in model_manager else None
        control_model_page = model_manager._get_model_page(control_model) if control_model else None
        if control_model is None or control_model_page is None:
            raise ValueError(
                f"Model with ID `{self.control}` used as a `control` in `set_control` action not found in the "
                f"dashboard. Please provide a valid control ID that exists in the dashboard."
            )

        # Validate that control model has a categorical selector.
        if not _is_categorical_selector(getattr(control_model, "selector", None)):
            raise TypeError(
                f"Model with ID `{self.control}` used as a `control` in `set_control` action must be a control model "
                f"(e.g. Filter, Parameter) that uses a categorical selector (e.g. Dropdown, Checklist or RadioItems)."
            )

        if control_model_page == model_manager._get_model_page(self):
            self._same_page = True
        else:
            # Validate that control on different page has `show_in_url=True`.
            if not control_model.show_in_url:
                raise ValueError(
                    f"Model with ID `{self.control}` used as a `control` in `set_control` action is on a different "
                    f"page from the trigger and so must have `show_in_url=True`."
                )
            self._same_page = False

    def function(self, _trigger):
        value = cast(_SupportsSetControl, self._parent_model)._get_value_from_trigger(self.value, _trigger)

        if self._same_page:
            # Returning a single element value works for both single and multi select selectors.
            return value

        page_path = model_manager._get_model_page(model_manager[self.control]).path
        url_query_params = f"?{self.control}={_encode_to_base64(value)}"
        return get_relative_path(page_path), url_query_params

    @property
    def outputs(self):  # type: ignore[override]
        if self._same_page:
            return self.control
        return ["vizro_url.pathname", "vizro_url.search"]
