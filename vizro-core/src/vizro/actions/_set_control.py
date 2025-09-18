from __future__ import annotations

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
    """Sets the value of a control based on data from the trigger.

    Args:
        control (ModelID): Filter or Parameter component id to be affected by the trigger. If the control is on a
            different page to the trigger then it must have `show_in_url=True`.
        value (str): TODO AM: ADD DESCRIPTION
    """

    type: Literal["set_control"] = "set_control"
    control: ModelID = Field(
        description="Filter or Parameter component id to be affected by the trigger."
        "If the control is on a different page to the trigger then it must have `show_in_url=True`."
    )
    value: str = Field(description="TODO AM: ADD DESCRIPTION")

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

        # Validate that control model has a categorical selector.
        if not isinstance(getattr(control_model, "selector", None), (vm.Dropdown, vm.Checklist, vm.RadioItems)):
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
