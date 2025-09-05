from __future__ import annotations

import base64
import json
from typing import Literal, Protocol, Union, cast, runtime_checkable

from dash import get_relative_path
from pydantic import Field, JsonValue

import vizro.models as vm
from vizro._vizro_utils import experimental
from vizro.actions._abstract_action import _AbstractAction
from vizro.managers import model_manager
from vizro.models._models_utils import _log_call
from vizro.models.types import ControlType, ModelID

# TODO AM+PP: decide whether to make it control or controls plural. For now I just wrote it as singular but there's
#  inconsistency with filename and type.
"""
I'm not sure what the right syntax would be for targeting multiple controls?

Copied from https://github.com/McK-Internal/vizro-internal/issues/1939:
It should be possible to target multiple controls in one click
(think e.g. clicking on a 2D heatmap, see Max example in mckinsey/vizro#1301).
So we need some way to do e.g. target="country_filter", lookup="country" as well as
target="continent_filter", lookup="continent". This could be multiple set_control calls
or better a single set_controls. In this case what would API be? How do you assign the
right values to the right targets? Maybe a dictionary like {"country_filter": "country",
"continent_filter": "continent"}?

Then in the (more common) case of targeting a single control, what would it look like? target = {"target_id":
"species"}? Then there would be no need for separate lookup argument which is maybe nicer overall? Not sure which of
these I prefer:
1. target="filter" lookup="x"
2. targets={"filter": "x"}
3. targets=["continet_filter", "country_filter"] lookups=["x", "y"]
4. something else?

Option 3 is effectively unzipped version of 2. I think I prefer 2 to 3 but can predict problems with it if we want to
add more argument in future (e.g. replace vs. append mode). Could have targets be a pydantic model itself if that helps
but want to keep simple cases simple. How would it work with a default lookup value also?

Overall I tend to preferring option 1 for now but then I have no idea how to extend it to multiple controls in
future. Maybe we should ask chatGPT if it has any ideas here... Possibly overall it's easier for a user to just chain
multiple set_control actions together, just it's not so performant. Then ideally we'd need to come up with some way of
doing parallel actions ideally. Relates to an idea I had about "batching" actions - let's discuss some time...
"""


@runtime_checkable
class _SupportsSetControl(Protocol):
    def _get_value_from_trigger(self, action: set_control, trigger: JsonValue) -> JsonValue: ...


@runtime_checkable
class _ControlWithCategoricalSelector(Protocol):
    selector: Union[vm.Dropdown, vm.RadioItems, vm.Checklist]
    show_in_url: bool


@experimental(
    "The `set_control` action is experimental. We hope that it will be a stable part of Vizro in future, "
    "but until then it may change or be removed without warning. If you have feedback on the feature then "
    "[let us know](https://github.com/mckinsey/vizro/issues)."
)
class set_control(_AbstractAction):
    """Sets the value of a control based on data from the trigger.

    Args:
        target (ModelID): Filter or Parameter component id to be affected by the trigger. If the target is on a
            different page to the trigger then it must have `show_in_url=True`.
        value (str): # TODO AM+PP: ADD DESCRIPTION
    """

    type: Literal["set_control"] = "set_control"
    target: ModelID = Field(
        description="Filter or Parameter component id to be affected by the trigger."
        "If the target is on a different page to the trigger then it must have `show_in_url=True`."
    )
    value: str

    @_log_call
    def pre_build(self):
        # Validate that action's parent model supports `set_control` action.
        if not isinstance(model_manager[self._parent_model], _SupportsSetControl):
            raise ValueError(
                f"`set_control` action was added to the model with ID `{self._parent_model}`, but this action can only "
                f"be used with models that support it (e.g. Graph, AgGrid)."
            )

        # Validate that action's target control exists in the dashboard.
        target_model = cast(ControlType, model_manager[self.target]) if self.target in model_manager else None
        target_model_page = model_manager._get_model_page(target_model) if target_model else None
        if target_model is None or target_model_page is None:
            raise ValueError(
                f"Model with ID `{self.target}` used as a `target` in `set_control` action not found in the dashboard. "
                f"Please provide a valid control ID that exists in the dashboard."
            )

        # Validate that target is control that has a categorical selector.
        if not isinstance(target_model, (vm.Filter, vm.Parameter)) or not isinstance(
            target_model.selector, (vm.Dropdown, vm.Checklist, vm.RadioItems)
        ):
            raise TypeError(
                f"Model with ID `{self.target}` used as a `target` in `set_control` action must be a control model "
                f"(e.g. Filter, Parameter) that uses a categorical selector (e.g. Dropdown, Checklist or RadioItems)."
            )

        if target_model_page == model_manager._get_model_page(self):
            self._same_page = True
        else:
            # Validate that target control on different page has `show_in_url=True`.
            if not target_model.show_in_url:
                raise ValueError(
                    f"Model with ID `{self.target}` used as a `target` in `set_control` action is on a different page "
                    f"than the trigger and must have `show_in_url=True`."
                )
            self._same_page = False

    def function(self, _trigger):
        value = model_manager[self._parent_model]._get_value_from_trigger(  # type: ignore[attr-defined]
            self, trigger=_trigger
        )

        if self._same_page:
            # Returning a single element value works for both single and multi select selectors.
            return value
        else:

            def encode_to_base64(value):
                json_bytes = json.dumps(value, separators=(",", ":")).encode("utf-8")
                b64_bytes = base64.urlsafe_b64encode(json_bytes)
                return f"b64_{b64_bytes.decode('utf-8').rstrip('=')}"

            page_path = model_manager._get_model_page(model_manager[self.target]).path
            # ideally this shouldn't overwrite all the URL params but just append to existing ones.
            # What's the best way to do that? If it does override then that's ok - we can fix the bug later.
            #  Alternative approach is maybe don't send directly to vizro_url but instead to some proxy
            #  object and then update vizro_url with cs callback that does encoding.
            # This is nice idea so then b64 logic not needed in Python (yet anyway).
            # And same page vs. different looks more similar.
            # Then do change page as another action in the chain? Would be an extra callback but work with chain.
            # Not sure if good idea.
            # Currently not sure whether this should actually change page or not in case that target is on another page.
            # Probably it should change page by default anyway.
            # Need to make url safe the target id (though not base64).
            url_query_params = f"?{self.target}={encode_to_base64(value)}"
            return get_relative_path(page_path), url_query_params

    @property
    def outputs(self):  # type: ignore[override]
        if self._same_page:
            return self.target  # Should target underlying selector.value.
        else:
            # return ["vizro_url_proxy"]
            # vizro_url_proxy is dcc.Store
            # which takes in {"self.target": value} and does encodeUrlParams to it in a clientside callback
            # then sends result to vizro_url
            return ["vizro_url.pathname", "vizro_url.search"]
