"""Contains utilities for the implementation of action functions."""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any, Literal, Optional, TypedDict, Union

import pandas as pd

from vizro._constants import ALL_OPTION, NONE_OPTION
from vizro.managers import data_manager, model_manager
from vizro.managers._model_manager import ModelID
from vizro.models.types import MultiValueType, SelectorType, SingleValueType

if TYPE_CHECKING:
    from vizro.models import Action, VizroBaseModel, Filter

ValidatedNoneValueType = Union[SingleValueType, MultiValueType, None, list[None]]


class CallbackTriggerDict(TypedDict):
    """Represent dash.ctx.args_grouping item. Shortened as 'ctd' in the code.

    Args:
        id: The component ID. If it's a pattern matching ID, it will be a dict.
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
def _get_component_actions(component) -> list[Action]:
    return (
        [action for actions_chain in component.actions for action in actions_chain.actions]
        if hasattr(component, "actions")
        else []
    )


def _apply_control_filters(
    data_frame: pd.DataFrame, ctds_filters: list[CallbackTriggerDict], target: str
) -> pd.DataFrame:
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
    data_frame: pd.DataFrame, ctds_filter_interaction: list[dict[str, CallbackTriggerDict]], target: str
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


def _filter_dot_separated_strings(dot_separated_strings: list[str], target: str, data_frame: bool) -> list[str]:
    result = []

    for dot_separated_string_with_target in dot_separated_strings:
        if dot_separated_string_with_target.startswith(f"{target}."):
            dot_separated_string = dot_separated_string_with_target.removeprefix(f"{target}.")
            if (data_frame and dot_separated_string.startswith("data_frame.")) or (
                not data_frame and not dot_separated_string.startswith("data_frame.")
            ):
                result.append(dot_separated_string)
    return result


def _update_nested_figure_properties(
    figure_config: dict[str, Any], dot_separated_string: str, value: Any
) -> dict[str, Any]:
    keys = dot_separated_string.split(".")
    current_property = figure_config

    for key in keys[:-1]:
        current_property = current_property.setdefault(key, {})

    current_property[keys[-1]] = value
    return figure_config


def _get_parametrized_config(
    ctd_parameters: list[CallbackTriggerDict], target: ModelID, data_frame: bool
) -> dict[str, Any]:
    if data_frame:
        # It's not possible to address nested argument of data_frame like data_frame.x.y, just top-level ones like
        # data_frame.x.
        config: dict[str, Any] = {"data_frame": {}}
    else:
        # TODO - avoid calling _captured_callable. Once we have done this we can remove _arguments from
        #  CapturedCallable entirely. This might mean not being able to address nested parameters.
        config = deepcopy(model_manager[target].figure._arguments)
        del config["data_frame"]

    for ctd in ctd_parameters:
        # TODO: needs to be refactored so that it is independent of implementation details
        selector_value = ctd["value"]

        if hasattr(selector_value, "__iter__") and ALL_OPTION in selector_value:  # type: ignore[operator]
            selector: SelectorType = model_manager[ctd["id"]]

            # Even if options are provided as list[dict], the Dash component only returns a list of values.
            # So we need to ensure that we always return a list only as well to provide consistent types.
            if all(isinstance(option, dict) for option in selector.options):
                selector_value = [option["value"] for option in selector.options]
            else:
                selector_value = selector.options

        selector_value = _validate_selector_value_none(selector_value)

        for action in _get_component_actions(model_manager[ctd["id"]]):
            if action.function._function.__name__ != "_parameter":
                continue

            for dot_separated_string in _filter_dot_separated_strings(action.function["targets"], target, data_frame):
                config = _update_nested_figure_properties(
                    figure_config=config, dot_separated_string=dot_separated_string, value=selector_value
                )

    return config


# Helper functions used in pre-defined actions ----
def _apply_filters(
    data: pd.DataFrame,
    ctds_filter: list[CallbackTriggerDict],
    ctds_filter_interaction: list[dict[str, CallbackTriggerDict]],
    target: ModelID,
):
    # Takes in just one target, so dataframe is filtered repeatedly for every target that uses it.
    # Potentially this could be de-duplicated but it's not so important since filtering is a relatively fast
    # operation (compared to data loading).
    filtered_data = _apply_control_filters(data_frame=data, ctds_filters=ctds_filter, target=target)
    filtered_data = _apply_filter_interaction(
        data_frame=filtered_data, ctds_filter_interaction=ctds_filter_interaction, target=target
    )
    return filtered_data


def _get_unfiltered_data(
    ctds_parameter: list[CallbackTriggerDict], targets: list[ModelID]
) -> dict[ModelID, pd.DataFrame]:
    # Takes in multiple targets to ensure that data can be loaded efficiently using _multi_load and not repeated for
    # every single target.
    # Getting unfiltered data requires data frame parameters. We pass in all ctd_parameters and then find the
    # data_frame ones by passing data_frame=True in the call to _get_paramaterized_config.
    multi_data_source_name_load_kwargs = []
    for target in targets:
        dynamic_data_load_params = _get_parametrized_config(
            ctd_parameters=ctds_parameter, target=target, data_frame=True
        )
        # This works for the figure objects but not for the Filter objects. Ideally, we should or enable multiple
        # data_frame-s from figure objects or limit Filter to use a single data_frame object. Filter with a single
        # data_frame object sounds like a better idea (although it's a breaking change).
        data_source_name = model_manager[target]["data_frame"]
        multi_data_source_name_load_kwargs.append((data_source_name, dynamic_data_load_params["data_frame"]))

    return dict(zip(targets, data_manager._multi_load(multi_data_source_name_load_kwargs)))


def _get_modified_page_figures(
    ctds_filter: list[CallbackTriggerDict],
    ctds_filter_interaction: list[dict[str, CallbackTriggerDict]],
    ctds_parameter: list[CallbackTriggerDict],
    targets: list[ModelID],
) -> dict[ModelID, Any]:
    outputs: dict[ModelID, Any] = {}

    # TODO: the structure here would be nicer if we could get just the ctds for a single target at one time,
    #  so you could do apply_filters on a target a pass only the ctds relevant for that target.
    #  Consider restructuring ctds to a more convenient form to make this possible.

    from vizro.models import Filter

    control_targets = []
    control_targets_targets = []
    figure_targets = []

    for target in targets:
        target_obj = model_manager[target]
        if isinstance(target_obj, Filter):
            control_targets.append(target)
            control_targets_targets.extend(target_obj.targets)
        else:
            figure_targets.append(target)

    # Retrieving only figure_targets data_frames from multi_load is not the best solution. We assume that Filter.targets
    # are the subset of the action's targets. This works for the on_page_load, but will not work if explicitly set.
    # Also, it was a good decision to return action output as key: value pairs for the predefined actions.
    _get_unfiltered_data_targets = list(set(figure_targets + control_targets_targets))

    figure_targets_unfiltered_data: dict[ModelID, pd.DataFrame] = _get_unfiltered_data(ctds_parameter, _get_unfiltered_data_targets)

    for target, unfiltered_data in figure_targets_unfiltered_data.items():
        if target in figure_targets:
            filtered_data = _apply_filters(unfiltered_data, ctds_filter, ctds_filter_interaction, target)
            outputs[target] = model_manager[target](
                data_frame=filtered_data,
                **_get_parametrized_config(ctd_parameters=ctds_parameter, target=target, data_frame=False),
            )

    for target in control_targets:
        current_value = [item for item in ctds_filter if item["id"] == model_manager[target].selector.id]
        current_value = current_value if not current_value else current_value[0]["value"]
        if hasattr(current_value, "__iter__") and ALL_OPTION in current_value:
            current_value = []

        outputs[target] = model_manager[target](
            target_to_data_frame=figure_targets_unfiltered_data,
            current_value=current_value
        )

    return outputs
