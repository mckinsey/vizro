import logging
from typing import Any, Dict, List

from dash import Input, Output, State, callback, ctx
from pydantic import Field

import vizro.actions
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

    def _get_callback_mapping(self):
        from vizro.actions._callback_mapping._get_action_callback_mapping import _get_action_callback_mapping

        callback_inputs: Dict[str, Any] = {
            **_get_action_callback_mapping(action_id=self.id, argument="inputs"),  # type: ignore[arg-type]
            **{
                f'{input.split(".")[0]}_{input.split(".")[1]}': State(input.split(".")[0], input.split(".")[1])
                for input in self.inputs
            },
            "trigger": Input({"type": "action_trigger", "action_name": self.id}, "data"),
        }

        callback_outputs: Dict[str, Any] = {
            **_get_action_callback_mapping(action_id=self.id, argument="outputs"),  # type: ignore[arg-type]
            **{
                f'{output.split(".")[0]}_{output.split(".")[1]}': Output(
                    output.split(".")[0], output.split(".")[1], allow_duplicate=True
                )
                for output in self.outputs
            },
            "action_finished": Output("action_finished", "data", allow_duplicate=True),
        }

        action_components = _get_action_callback_mapping(
            action_id=self.id, argument="components"  # type: ignore[arg-type]
        )

        return callback_inputs, callback_outputs, action_components

    def _action_callback_function(self, **inputs: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug("=============== ACTION ===============")
        logger.debug(f'Action ID: "{self.id}"')
        logger.debug(f'Action name: "{self.function._function.__name__}"')
        logger.debug(f"Action inputs: {inputs}")

        # Invoking the action's function
        return_value = self.function(**inputs) or {}

        # Raising the custom exception if return value length doesn't match the number of outputs
        return_value_len = (
            1 if not hasattr(return_value, "__len__") or isinstance(return_value, str) else len(return_value)
        )
        outputs = list(ctx.outputs_grouping.keys())
        outputs.remove("action_finished")
        if len(outputs) != return_value_len:
            raise ValueError(
                f"Number of action's returned elements: {return_value_len} does not match the number"
                f" of action's defined outputs: {len(outputs)}."
            )

        if isinstance(return_value, dict):
            return {"action_finished": None, **return_value}

        # If return_value is a single element, ensure return_value is a list
        if not isinstance(return_value, (list, tuple)):
            return_value = [return_value]

        # Map returned values to dictionary format where None belongs to the "action_finished" output
        return {"action_finished": None, **dict(zip(outputs, return_value))}

    @_log_call
    def build(self):
        """Builds a callback for the Action model and returns required components for the callback.

        Returns:
            List of required components for the Action model added in the `Dashboard` level e.g. List[dcc.Download].
        """
        # callback_inputs, and callback_outputs are "dash.State" and "dash.Output" objects made of three parts:
        # 1. User configured inputs/outputs - for custom actions,
        # 2. Vizro configured inputs/outputs - for predefined actions,
        # 3. Hardcoded inputs/outputs - for custom and predefined actions (enable callbacks to live inside Action loop).
        # action_components represents return value of the build method.
        callback_inputs, callback_outputs, action_components = self._get_callback_mapping()

        logger.debug(
            f"Creating Callback mapping for Action ID {self.id} with "
            f"function name: {self.function._function.__name__}"
        )
        logger.debug("---------- INPUTS ----------")
        for name, object in callback_inputs.items():
            logger.debug(f"--> {name}: {object}")
        logger.debug("---------- OUTPUTS ---------")
        for name, object in callback_outputs.items():
            logger.debug(f"--> {name}: {object}")
        logger.debug("============================")

        @callback(output=callback_outputs, inputs=callback_inputs, prevent_initial_call=True)
        def callback_wrapper(trigger: None, **inputs: Dict[str, Any]) -> Dict[str, Any]:
            return self._action_callback_function(**inputs)

        return action_components
