from __future__ import annotations
import pandas as pd

import base64
import json
from typing import Literal, Protocol, cast, runtime_checkable

from dash import get_relative_path
from pydantic import Field, JsonValue

import vizro.models as vm
from vizro.actions._abstract_action import _AbstractAction
from vizro.managers import model_manager
from vizro.models._models_utils import _log_call
from vizro.models.types import ControlType, ModelID


# This defines what a model needs to implement for it to be capable of acting as the trigger of set_control.
@runtime_checkable
class _SupportsSetControl(Protocol):
    def _get_value_from_trigger(self, value: str, trigger: JsonValue) -> JsonValue: ...


def _encode_to_base64(value):
    json_bytes = json.dumps(value, separators=(",", ":")).encode("utf-8")
    b64_bytes = base64.urlsafe_b64encode(json_bytes)
    return f"b64_{b64_bytes.decode('utf-8').rstrip('=')}"


class set_control(_AbstractAction):
    """Sets the value of a control, which then updates its targets.

    Abstract: Usage documentation
        [Graph and table interactions](../user-guides/graph-table-actions.md)

    The following Vizro models can be a source of `set_control`:

    * [`AgGrid`][vizro.models.AgGrid]: triggers `set_control` when user clicks on a row in the table. `value` specifies
    which column in the clicked row is used to set `control`.
    * [`Graph`][vizro.models.Graph]: triggers `set_control` when user clicks on data in the graph. `value` can be used
    in two ways to specify how to set `control`:

        * Column from which to take the value. This requires you to set `custom_data` in the graph's `figure` function.
        * String to [traverse a Box](https://github.com/cdgriffith/Box/wiki/Types-of-Boxes#box-dots) that contains the
        trigger data [`clickData["points"][0]`](https://dash.plotly.com/interactive-graphing), for example `"x"`.

    Args:
        control (ModelID): Control whose value is set. If this is on a different page from the trigger then it must have
            `show_in_url=True`. The control's selector must be categorical (e.g. Dropdown, RadioItems, Checklist).
        value (str): Value taken from trigger to set `control`. Format depends on the source model that triggers
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
    """

    type: Literal["set_control"] = "set_control"
    control: ModelID = Field(
        description="Filter or Parameter component id to be affected by the trigger."
        "If the control is on a different page to the trigger then it must have `show_in_url=True`."
    )
    value: str = Field(
        description="Value to take from trigger and send to the `target`. Format depends on the model "
        "that triggers `set_control`."
    )

    @_log_call
    def pre_build(self):
        # Validate that action's parent model supports `set_control` action.
        if not isinstance(self._parent_model, _SupportsSetControl):
            raise ValueError(
                f"`set_control` action was added to the model with ID `{self._parent_model.id}`, but this action "
                f"can only be used with models that support it (e.g. Graph, AgGrid)."
            )

        # Validate that action's control exists in the dashboard.
        control_model = cast(ControlType, model_manager[self.control]) if self.control in model_manager else None
        control_model_page = model_manager._get_model_page(control_model) if control_model else None
        if control_model is None or control_model_page is None:
            raise ValueError(
                f"Model with ID `{self.control}` used as a `control` in `set_control` action not found in the "
                f"dashboard. Please provide a valid control ID that exists in the dashboard."
            )

        if not hasattr(control_model, "selector"):
            raise TypeError(
                f"Model with ID `{self.control}` used as a `control` in `set_control` action must be a control model "
                f"(e.g. Filter, Parameter)."
            )

        # Determine whether the control selector is single, multi or range.
        if (
            isinstance(control_model.selector, (vm.RadioItems, vm.Slider, vm.Switch))
            or (isinstance(control_model.selector, vm.Dropdown) and not control_model.selector.multi)
            or (isinstance(control_model.selector, vm.DatePicker) and not control_model.selector.range)
        ):
            self._control_selector_type = "single"
        elif (
            isinstance(control_model.selector, vm.Checklist)
            or (isinstance(control_model.selector, vm.Dropdown) and control_model.selector.multi)
        ):
            self._control_selector_type = "multi"
        elif (
            isinstance(control_model.selector, vm.RangeSlider)
            or (isinstance(control_model.selector, vm.DatePicker) and control_model.selector.range)
        ):
            self._control_selector_type = "range"
        else:
            # TODO PP NOW: Should we cover this case too (for custom selectors IDK)?
            raise Exception("RAISE FOR NOW; THEN HANDLE IT PROPERLY")
            self._control_selector_type = "unknown"

        # Validate that action's trigger property is compatible with the target control selector type.
        if self._control_selector_type == "single" and self._first_in_chain_input_trigger_property == "select":
            raise TypeError(
                f"Model with ID `{self.control}` used as a `control` in `set_control` action has a single select "
                f"selector type (e.g. RadioItems, Slider, Switch, or Dropdown with `multi=False`) "
                f"and so cannot be set by a trigger with `actions_trigger='select'`. "
                f"Use another control type or use `actions_trigger='click'` instead."
            )

        if self._control_selector_type == "range" and self._first_in_chain_input_trigger_property == "click":
            # TODO PP NOW: Raise a warning maybe.
            pass

        if self._control_selector_type == "multi" and self._first_in_chain_input_trigger_property == "click":
            # TODO PP NOW: Raise a warning maybe.
            pass

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

        # Adjust value according to the control selector type (single, multi, range).
        value = self._adjust_result_by_control_type(value)

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

    def _adjust_result_by_control_type(self, value):
        # TODO PP NOW: Validation/adjustment scheme:
        #  single = RadioItems, Dropdown(multi=False), Slider, DatePicker(range=False), Switch
        #  multi = Checklist, Dropdown(multi=True)
        #  range = RangeSlider, DatePicker(range=True)
        #  1. click + single control -> OK -> value
        #  2. select + single control -> ERROR
        #  3. click + multi control -> OK(warn) -> value if isinstance(value, list) else [value]  # try with get_options here as well
        #  4. select + multi control -> OK -> Filter._get_options(value)  # to get unique values
        #  5. click + range control -> OK - questionable, buy I'm ok with that.
        #    It would mean that default actions-trigger can deal with any target. And, there's other triggers that work "better".
        #  6. select + range control -> OK -> Filter._get_min_max(value)  # to get min/max only

        if self._control_selector_type == "single":
            return value
        elif self._control_selector_type == "multi":
            return vm.Filter._get_options(pd.DataFrame(), current_value=value)
        elif self._control_selector_type == "range":
            return vm.Filter._get_min_max(pd.DataFrame(), current_value=value)
        else:
            # TODO PP NOW: Should we cover this case too (for custom selectors IDK)?
            raise Exception("RAISE FOR NOW; THEN HANDLE IT PROPERLY")
            return value
