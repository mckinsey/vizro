"""Creates action_callback_mapping to map callback arguments to action functions."""

from typing import Any, Dict, Union

from dash import Input, Output, State

from vizro.actions import export_data, filter_interaction
from vizro.actions._callback_mapping._callback_mapping_utils import (
    _get_action_callback_inputs,
    _get_action_callback_outputs,
    _get_export_data_callback_components,
    _get_export_data_callback_outputs,
)
from vizro.actions._filter_action import _filter
from vizro.actions._on_page_load_action import _on_page_load
from vizro.actions._parameter_action import _parameter
from vizro.managers import model_manager
from vizro.managers._model_manager import ModelID


def _get_action_callback_mapping(action_id: ModelID, argument: str) -> Union[Dict[str, Union[Input, State, Output]]]:
    """Creates mapping of action name and required callback input/output."""
    action_function = model_manager[action_id].function._function  # type: ignore[attr-defined]

    action_callback_mapping: Dict[str, Any] = {
        export_data.__wrapped__: {
            "inputs": _get_action_callback_inputs,
            "components": _get_export_data_callback_components,
            "outputs": _get_export_data_callback_outputs,
        },
        _filter.__wrapped__: {
            "inputs": _get_action_callback_inputs,
            "outputs": _get_action_callback_outputs,
        },
        filter_interaction.__wrapped__: {
            "inputs": _get_action_callback_inputs,
            "outputs": _get_action_callback_outputs,
        },
        _parameter.__wrapped__: {
            "inputs": _get_action_callback_inputs,
            "outputs": _get_action_callback_outputs,
        },
        _on_page_load.__wrapped__: {"inputs": _get_action_callback_inputs, "outputs": _get_action_callback_outputs},
    }
    action_call = action_callback_mapping.get(action_function, {}).get(argument, {})
    return action_call if isinstance(action_call, dict) else action_call(action_id=action_id)
