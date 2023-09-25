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

    @_log_call
    def build(self):
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
        def callback_wrapper(trigger: None, **inputs: Dict[str, Any]):
            logger.debug(f"Inputs to Action: {inputs}")
            return_value = self.function(**inputs) or {}
            if isinstance(return_value, dict):
                return {"action_finished": None, **return_value}

            if not isinstance(return_value, list) and not isinstance(return_value, tuple):
                return_value = [return_value]

            # Map returned values to dictionary format where None belongs to the "action_finished" output
            return dict(zip(ctx.outputs_grouping.keys(), [None, *return_value]))

        return _get_action_callback_mapping(action_id=self.id, argument="components")  # type: ignore[arg-type]
