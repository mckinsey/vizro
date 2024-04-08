"""Contains utilities for the implementation of action functions."""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, TypedDict, Union

import pandas as pd

from vizro._constants import ALL_OPTION, NONE_OPTION
from vizro.managers import data_manager, model_manager
from vizro.managers._model_manager import ModelID
from vizro.models.types import MultiValueType, SelectorType, SingleValueType

if TYPE_CHECKING:
    from vizro.models import Action, VizroBaseModel

ValidatedNoneValueType = Union[SingleValueType, MultiValueType, None, List[None]]


class CallbackTriggerDict(TypedDict):
    """Represent dash.ctx.args_grouping item. Shortened as 'ctd' in the code.

    Args:
        id: The component ID. If it`s a pattern matching ID, it will be a dict.
        property: The component property used in the callback.
        value: The value of the component property at the time the callback was fired.
        str_id: For pattern matching IDs, it's the stringified dict ID without white spaces.
        triggered: A boolean indicating whether this input triggered the callback.

    """

    id: ModelID
    property: Literal["clickData", "value", "n_clicks", "active_cell", "derived_viewport_data"]
    value: Optional[Any]
    str_id: str
    triggered: bool


# Utility functions for helper functions used in pre-defined actions ----
def _get_component_actions(component) -> List[Action]:
    return (
        [action for actions_chain in component.actions for action in actions_chain.actions]
        if hasattr(component, "actions")
        else []
    )


def _apply_filters(data_frame: pd.DataFrame, ctds_filters: List[CallbackTriggerDict], target: str) -> pd.DataFrame:
    for ctd in ctds_filters:
        selector_value = ctd["value"]
        selector_value = selector_value if isinstance(selector_value, list) else [selector_value]
        selector_actions = _get_component_actions(model_manager[ctd["id"]])

        for action in selector_actions:
            if (
                action.function._function.__name__ != "_filter"
                or target not in action.function["targets"]
                or ALL_OPTION in selector_value
            ):
                continue

            _filter_function = action.function["filter_function"]
            _filter_column = action.function["filter_column"]
            _filter_value = selector_value
            data_frame = data_frame[_filter_function(data_frame[_filter_column], _filter_value)]

    return data_frame


def _get_parent_vizro_model(_underlying_callable_object_id: str) -> VizroBaseModel:
    from vizro.models import VizroBaseModel

    for _, vizro_base_model in model_manager._items_with_type(VizroBaseModel):
        if (
            hasattr(vizro_base_model, "_input_component_id")
            and vizro_base_model._input_component_id == _underlying_callable_object_id
        ):
            return vizro_base_model
    raise KeyError(
        f"No parent Vizro model found for underlying callable object with id: {_underlying_callable_object_id}."
    )


def _apply_filter_interaction(
    data_frame: pd.DataFrame, ctds_filter_interaction: List[Dict[str, CallbackTriggerDict]], target: str
) -> pd.DataFrame:
    for ctd_filter_interaction in ctds_filter_interaction:
        triggered_model = model_manager[ctd_filter_interaction["modelID"]["id"]]
        data_frame = triggered_model._filter_interaction(
            data_frame=data_frame,
            target=target,
            ctd_filter_interaction=ctd_filter_interaction,
        )

    return data_frame


def _validate_selector_value_none(value: Union[SingleValueType, MultiValueType]) -> ValidatedNoneValueType:
    if value == NONE_OPTION:
        return None
    elif isinstance(value, list):
        return [i for i in value if i != NONE_OPTION] or [None]
    return value


def _create_target_arg_mapping(dot_separated_strings: List[str]) -> Dict[str, List[str]]:
    results = defaultdict(list)
    for string in dot_separated_strings:
        if "." not in string:
            raise ValueError(f"Provided string {string} must contain a '.'")
        component, arg = string.split(".", 1)
        results[component].append(arg)
    return results


def _update_nested_graph_properties(
    graph_config: Dict[str, Any], dot_separated_string: str, value: Any
) -> Dict[str, Any]:
    keys = dot_separated_string.split(".")
    current_property = graph_config

    for key in keys[:-1]:
        current_property = current_property.setdefault(key, {})

    current_property[keys[-1]] = value
    return graph_config


def _get_parametrized_config(
    targets: List[ModelID], parameters: List[CallbackTriggerDict]
) -> Dict[ModelID, Dict[str, Any]]:
    parameterized_config = {}
    for target in targets:
        # TODO - avoid calling _captured_callable. Once we have done this we can remove _arguments from
        #  CapturedCallable entirely.
        graph_config = deepcopy(model_manager[target].figure._arguments)
        if "data_frame" in graph_config:
            graph_config.pop("data_frame")

        for ctd in parameters:
            selector_value = ctd[
                "value"
            ]  # TODO: needs to be refactored so that it is independent of implementation details
            if hasattr(selector_value, "__iter__") and ALL_OPTION in selector_value:  # type: ignore[operator]
                selector: SelectorType = model_manager[ctd["id"]]
                selector_value = selector.options
            selector_value = _validate_selector_value_none(selector_value)
            selector_actions = _get_component_actions(model_manager[ctd["id"]])

            for action in selector_actions:
                action_targets = _create_target_arg_mapping(action.function["targets"])

                if action.function._function.__name__ != "_parameter" or target not in action_targets:
                    continue

                for action_targets_arg in action_targets[target]:
                    graph_config = _update_nested_graph_properties(
                        graph_config=graph_config, dot_separated_string=action_targets_arg, value=selector_value
                    )

        parameterized_config[target] = graph_config

    return parameterized_config


# Helper functions used in pre-defined actions ----
def _get_filtered_data(
    targets: List[ModelID],
    ctds_filters: List[CallbackTriggerDict],
    ctds_filter_interaction: List[Dict[str, CallbackTriggerDict]],
) -> Dict[ModelID, pd.DataFrame]:
    filtered_data = {}
    for target in targets:
        data_frame = data_manager._get_component_data(target)

        data_frame = _apply_filters(data_frame=data_frame, ctds_filters=ctds_filters, target=target)
        data_frame = _apply_filter_interaction(
            data_frame=data_frame, ctds_filter_interaction=ctds_filter_interaction, target=target
        )

        filtered_data[target] = data_frame

    return filtered_data


def _get_modified_page_figures(
    ctds_filter: List[CallbackTriggerDict],
    ctds_filter_interaction: List[Dict[str, CallbackTriggerDict]],
    ctds_parameters: List[CallbackTriggerDict],
    targets: Optional[List[ModelID]] = None,
) -> Dict[str, Any]:
    if not targets:
        targets = []
    filtered_data = _get_filtered_data(
        targets=targets, ctds_filters=ctds_filter, ctds_filter_interaction=ctds_filter_interaction
    )

    parameterized_config = _get_parametrized_config(targets=targets, parameters=ctds_parameters)

    outputs: Dict[str, Any] = {}
    for target in targets:
        outputs[target] = model_manager[target](data_frame=filtered_data[target], **parameterized_config[target])

    return outputs
