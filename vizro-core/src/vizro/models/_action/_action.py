import importlib.util
import logging
from collections.abc import Collection, Mapping
from typing import Any, Dict, List, Union, Collection, Mapping

from dash import Input, Output, State, callback, html
from pydantic import Field, validator

import vizro.actions
from vizro.managers._model_manager import ModelID
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable

logger = logging.getLogger(__name__)


class Action(VizroBaseModel):
    """Action to be inserted into `actions` of relevant component.

    Args:
        function (CapturedCallable): See [`CapturedCallable`][vizro.models.types.CapturedCallable].
        inputs (List[str]): Inputs in the form `<component_id>.<property>` passed to the action function.
            Defaults to `[]`.
        outputs (List[str]): Outputs in the form `<component_id>.<property>` changed by the action function.
            Defaults to `[]`.
    """

    function: CapturedCallable = Field(..., import_path=vizro.actions)
    inputs: List[str] = Field(
        [],
        description="Inputs in the form `<component_id>.<property>` passed to the action function.",
        regex="^[a-zA-Z0-9_]+[.][a-zA-Z_]+$",
    )
    outputs: List[str] = Field(
        [],
        description="Outputs in the form `<component_id>.<property>` changed by the action function.",
        regex="^[a-zA-Z0-9_]+[.][a-zA-Z_]+$",
    )

    # TODO: Problem: generic Action model shouldn't depend on details of particular actions like export_data.
    # Possible solutions: make a generic mapping of action functions to validation functions or the imports they
    # require, and make the code here look up the appropriate validation using the function as key
    # This could then also involve other validations currently only carried out at run-time in pre-defined actions, such
    # as e.g. checking if the correct arguments have been provided to the file_format in export_data.
    @validator("function")
    def validate_predefined_actions(cls, function):
        if function._function.__name__ == "export_data":
            file_format = function._arguments.get("file_format")
            if file_format not in [None, "csv", "xlsx"]:
                raise ValueError(f'Unknown "file_format": {file_format}.' f' Known file formats: "csv", "xlsx".')
            if file_format == "xlsx":
                if importlib.util.find_spec("openpyxl") is None and importlib.util.find_spec("xlsxwriter") is None:
                    raise ModuleNotFoundError(
                        "You must install either openpyxl or xlsxwriter to export to xlsx format."
                    )
        return function

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

        if self.inputs:
            callback_inputs: Dict[str, Any] = [State(input.split(".")[0], input.split(".")[1]) for input in self.inputs]
        else:
            callback_inputs = _get_action_callback_mapping(action_id=ModelID(str(self.id)), argument="inputs") or []

        if self.outputs:
            callback_outputs = [
                Output(output.split(".")[0], output.split(".")[1], allow_duplicate=True) for output in self.outputs
            ]
        else:
            callback_outputs = _get_action_callback_mapping(action_id=ModelID(str(self.id)), argument="outputs") or []

        action_components = _get_action_callback_mapping(action_id=ModelID(str(self.id)), argument="components")

        return callback_inputs, callback_outputs, action_components

    def _action_callback_function(
        self, inputs: Union[Dict[str, Any], List[str]], outputs: Union[Dict[str, Any], List[str]]
    ) -> Union[Collection, Mapping, None]:
        logger.debug("=============== ACTION ===============")
        logger.debug(f'Action ID: "{self.id}"')
        logger.debug(f'Action name: "{self.function._function.__name__}"')
        logger.debug(f"Action inputs: {inputs}")
        logger.debug(f"Action outputs: {outputs}")

        if isinstance(inputs, Mapping):
            return_value = self.function(**inputs)
        else:
            return_value = self.function(*inputs)

        if not outputs and return_value is not None:
            raise ValueError("Action function has returned a value but the action has no defined outputs.")
        elif isinstance(outputs, Mapping):
            if not isinstance(return_value, Mapping):
                raise ValueError(
                    "Action function has not returned a dictionary or similar but the action's defined outputs are a dictionary."
                )
            if set(outputs) != set(return_value):
                raise ValueError(
                    f"Keys of action's returned value ({set(return_value) or {}}) do not match the action's defined outputs"
                    f" ({set(outputs) or {}})."
                )
        elif isinstance(outputs, Collection) and len(outputs) > 1:
            # If len(outputs) == 1 then we just return the return_value with no need for further checks.
            if not isinstance(return_value, Collection):
                raise ValueError(
                    "Action function has not returned a list or similar but the action's defined outputs are a list."
                )
            if len(return_value) != len(outputs):
                raise ValueError(
                    f"Number of action's returned elements ({len(return_value)}) does not match the number"
                    f" of action's defined outputs ({len(outputs)})."
                )

        # If no error has been raised then the return_value is good and is returned as it is - this could be a list, dictionary or None.
        return return_value
        # if return_value is None and len(outputs) == 0:
        #     # Action has no outputs and the custom action function returns None.
        #     # Special case results with no exception.
        #     return_dict = {}
        # elif len(outputs) == 1:
        #     # If the action has only one output, so assign the entire return_value to the output.
        #     # This ensures consistent handling regardless of the type or structure of the return_value.
        #     return_dict = {outputs[0]: return_value}
        # elif isinstance(return_value, Mapping) and return_value:
        #     # We exclude the empty dictionary case here so that it raises the invalid number of elements error raised
        #     # in the else clause.
        #     if set(outputs) != set(return_value):
        #         raise ValueError(
        #             f"Keys of action's returned value ({set(return_value)}) do not match the action's defined outputs"
        #             f" ({set(outputs)})."
        #         )
        #     return_dict = return_value
        # else:
        #     if not isinstance(return_value, Collection) or len(return_value) == 0:
        #         # If return_value is not a collection or is an empty collection,
        #         # create a new collection from it. This ensures handling of return values like None, True, 1 etc.
        #         # and treats an empty collection as a 1-length collection.
        #         # Note that if this clause runs then the below invalid number of elements error is always raised,
        #         # because we already know that len(return_value) == 1 and len(outputs) != 1 (from above elif clause).
        #         return_value = [return_value]
        #
        #     if len(return_value) != len(outputs):
        #         raise ValueError(
        #             f"Number of action's returned elements ({len(return_value)}) does not match the number"
        #             f" of action's defined outputs ({len(outputs)})."
        #         )
        #     return_dict = dict(zip(outputs, return_value))
        #
        # return return_dict

    @_log_call
    def build(self):
        """Builds a callback for the Action model and returns required components for the callback.

        Returns:
            List of required components (e.g. dcc.Download) for the Action model added to the `Dashboard` container.
        """
        external_callback_inputs, external_callback_outputs, action_components = self._get_callback_mapping()
        callback_inputs = {
            "external": external_callback_inputs,
            "internal": {"trigger": Input({"type": "action_trigger", "action_name": self.id}, "data")},
        }
        callback_outputs = {
            "external": external_callback_outputs,
            "internal": {"action_finished": Output("action_finished", "data", allow_duplicate=True)},
        }

        logger.debug(
            f"Creating Callback mapping for Action ID {self.id} with "
            f"function name: {self.function._function.__name__}"
        )
        logger.debug("---------- INPUTS ----------")
        # for name, object in callback_inputs["external"].items():
        #     logger.debug(f"--> {name}: {object}")
        logger.debug("---------- OUTPUTS ---------")
        # for name, object in callback_outputs["external"].items():
        #     logger.debug(f"--> {name}: {object}")
        logger.debug("============================")

        @callback(output=callback_outputs, inputs=callback_inputs, prevent_initial_call=True)
        def callback_wrapper(external: Union[List[str], Dict[str, Any]], internal: Dict[str, Any]) -> Dict[str, Any]:
            return_value = self._action_callback_function(inputs=external, outputs=callback_outputs["external"])
            return {"internal": {"action_finished": None}, "external": return_value}

        return html.Div(children=action_components, id=f"{self.id}_action_model_components_div", hidden=True)
