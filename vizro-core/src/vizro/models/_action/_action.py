import importlib.util
import logging
from collections.abc import Collection, Mapping
from pprint import pformat
from typing import Annotated, Any, Union

from dash import Input, Output, State, callback, html
from pydantic import AfterValidator, Field, StringConstraints, field_validator
from pydantic.json_schema import SkipJsonSchema

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable, validate_captured_callable

logger = logging.getLogger(__name__)


# TODO: Problem: generic Action model shouldn't depend on details of particular actions like export_data.
# Possible solutions: make a generic mapping of action functions to validation functions or the imports they
# require, and make the code here look up the appropriate validation using the function as key
# This could then also involve other validations currently only carried out at run-time in pre-defined actions, such
# as e.g. checking if the correct arguments have been provided to the file_format in export_data.
def validate_predefined_actions(function):
    if function._function.__name__ == "export_data":
        file_format = function._arguments.get("file_format")
        if file_format not in [None, "csv", "xlsx"]:
            raise ValueError(f'Unknown "file_format": {file_format}. Known file formats: "csv", "xlsx".')
        if file_format == "xlsx":
            if importlib.util.find_spec("openpyxl") is None and importlib.util.find_spec("xlsxwriter") is None:
                raise ModuleNotFoundError("You must install either openpyxl or xlsxwriter to export to xlsx format.")
    return function


class Action(VizroBaseModel):
    """Action to be inserted into `actions` of relevant component.

    Args:
        function (CapturedCallable): Action function. See [`vizro.actions`][vizro.actions].
        inputs (list[str]): Inputs in the form `<component_id>.<property>` passed to the action function.
            Defaults to `[]`.
        outputs (list[str]): Outputs in the form `<component_id>.<property>` changed by the action function.
            Defaults to `[]`.

    """

    function: Annotated[
        SkipJsonSchema[CapturedCallable],
        AfterValidator(validate_predefined_actions),
        Field(json_schema_extra={"mode": "action", "import_path": "vizro.actions"}, description="Action function."),
    ]
    inputs: list[Annotated[str, StringConstraints(pattern="^[^.]+[.][^.]+$")]] = Field(
        [],
        description="Inputs in the form `<component_id>.<property>` passed to the action function.",
    )
    outputs: list[Annotated[str, StringConstraints(pattern="^[^.]+[.][^.]+$")]] = Field(
        [],
        description="Outputs in the form `<component_id>.<property>` changed by the action function.",
    )

    _validate_function = field_validator("function", mode="before")(validate_captured_callable)

    def _get_callback_mapping(self):
        """Builds callback inputs and outputs for the Action model callback, and returns action required components.

        callback_inputs, and callback_outputs are "dash.State" and "dash.Output" objects made of three parts:
            1. User configured inputs/outputs - for custom actions,
            2. Vizro configured inputs/outputs - for predefined actions,
            3. Hardcoded inputs/outputs - for custom and predefined actions
                (enable callbacks to live inside the Action loop).

        Returns: List of required components (e.g. dcc.Download) for the Action model added to the `Dashboard`
            container. Those components represent the return value of the Action build method.
        """
        from vizro.actions._callback_mapping._get_action_callback_mapping import _get_action_callback_mapping

        callback_inputs: Union[list[State], dict[str, State]]
        if self.inputs:
            callback_inputs = [State(*input.split(".")) for input in self.inputs]
        else:
            callback_inputs = _get_action_callback_mapping(self, argument="inputs")

        callback_outputs: Union[list[Output], dict[str, Output]]
        if self.outputs:
            callback_outputs = [Output(*output.split("."), allow_duplicate=True) for output in self.outputs]

            # Need to use a single Output in the @callback decorator rather than a single element list for the case
            # of a single output. This means the action function can return a single value (e.g. "text") rather than a
            # single element list (e.g. ["text"]).
            if len(callback_outputs) == 1:
                callback_outputs = callback_outputs[0]
        else:
            callback_outputs = _get_action_callback_mapping(self, argument="outputs")

        action_components = _get_action_callback_mapping(self, argument="components")

        return callback_inputs, callback_outputs, action_components

    def _action_callback_function(
        self,
        inputs: Union[dict[str, Any], list[Any]],
        outputs: Union[dict[str, Output], list[Output], Output, None],
    ) -> Any:
        logger.debug("===== Running action with id %s, function %s =====", self.id, self.function._function.__name__)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Action inputs:\n%s", pformat(inputs, depth=3, width=200))
            logger.debug("Action outputs:\n%s", pformat(outputs, width=200))

        if isinstance(inputs, Mapping):
            return_value = self.function(**inputs)
        else:
            return_value = self.function(*inputs)

        # Delegate all handling of the return_value and mapping to appropriate outputs to Dash - we don't modify
        # return_value to reshape it in any way. All we do is do some error checking to raise clearer error messages.
        if not outputs:
            if return_value is not None:
                raise ValueError("Action function has returned a value but the action has no defined outputs.")
        elif isinstance(outputs, dict):
            if not isinstance(return_value, Mapping):
                raise ValueError(
                    "Action function has not returned a dictionary-like object "
                    "but the action's defined outputs are a dictionary."
                )
            if set(outputs) != set(return_value):
                raise ValueError(
                    f"Keys of action's returned value {set(return_value) or {}} "
                    f"do not match the action's defined outputs {set(outputs) or {}})."
                )
        elif isinstance(outputs, list):
            if not isinstance(return_value, Collection):
                raise ValueError(
                    "Action function has not returned a list-like object but the action's defined outputs are a list."
                )
            if len(return_value) != len(outputs):
                raise ValueError(
                    f"Number of action's returned elements {len(return_value)} does not match the number"
                    f" of action's defined outputs {len(outputs)}."
                )

        # If no error has been raised then the return_value is good and is returned as it is.
        # This could be a list of outputs, dictionary of outputs or any single value including None.
        return return_value

    @_log_call
    def build(self) -> html.Div:
        """Builds a callback for the Action model and returns required components for the callback.

        Returns:
            Div containing a list of required components (e.g. dcc.Download) for the Action model

        """
        external_callback_inputs, external_callback_outputs, action_components = self._get_callback_mapping()
        callback_inputs = {
            "external": external_callback_inputs,
            "internal": {"trigger": Input({"type": "action_trigger", "action_name": self.id}, "data")},
        }
        callback_outputs = {
            "internal": {"action_finished": Output("action_finished", "data", allow_duplicate=True)},
        }

        # If there are no outputs then we don't want the external part of callback_outputs to exist at all.
        # This allows the action function to return None and match correctly on to the callback_outputs dictionary
        # The (probably better) alternative to this would be just to define a dummy output for all such functions
        # so that the external key always exists.
        # Note that it's still possible to explicitly return None as a value when an output is specified.
        if external_callback_outputs:
            callback_outputs["external"] = external_callback_outputs

        logger.debug(
            "===== Building callback for Action with id %s, function %s =====",
            self.id,
            self.function._function.__name__,
        )
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Callback inputs:\n%s", pformat(callback_inputs["external"], width=200))
            logger.debug("Callback outputs:\n%s", pformat(callback_outputs.get("external"), width=200))

        @callback(output=callback_outputs, inputs=callback_inputs, prevent_initial_call=True)
        def callback_wrapper(external: Union[list[Any], dict[str, Any]], internal: dict[str, Any]) -> dict[str, Any]:
            return_value = self._action_callback_function(inputs=external, outputs=callback_outputs.get("external"))
            if "external" in callback_outputs:
                return {"internal": {"action_finished": None}, "external": return_value}
            return {"internal": {"action_finished": None}}

        return html.Div(id=f"{self.id}_action_model_components_div", children=action_components, hidden=True)
