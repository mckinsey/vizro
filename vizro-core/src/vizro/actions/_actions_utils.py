"""Contains utilities for the implementation of action functions."""

from __future__ import annotations

from collections.abc import Iterable
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Literal, Optional, TypedDict, Union, cast

import pandas as pd

from vizro._constants import ALL_OPTION, NONE_OPTION
from vizro.managers import data_manager, model_manager
from vizro.managers._data_manager import DataSourceName
from vizro.models.types import (
    FigureType,
    FigureWithFilterInteractionType,
    ModelID,
    MultiValueType,
    SelectorType,
    SingleValueType,
)

if TYPE_CHECKING:
    from vizro.models import VizroBaseModel
    from vizro.models.types import ActionType

ValidatedNoneValueType = Union[SingleValueType, MultiValueType, None, list[None], list[SingleValueType]]


# TODO-AV2 A 2: go through and finish tidying bits that weren't already. Potentially there won't be much code left here
#  at all. Think about where it should live so it might become public in future. Is it just apply_controls and helper
#  functions for that? Do we want public vizro.actions.utils/helpers?


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
def _get_component_actions(component) -> list[ActionType]:
    return (
        [action for actions_chain in component.actions for action in actions_chain.actions]
        if hasattr(component, "actions")
        else []
    )


def _apply_filter_controls(
    data_frame: pd.DataFrame, ctds_filter: list[CallbackTriggerDict], target: ModelID
) -> pd.DataFrame:
    """Applies filters from a vm.Filter model in the controls.

    Args:
        data_frame: unfiltered DataFrame.
        ctds_filter: list of CallbackTriggerDict for filters.
        target: id of targeted Figure.

    Returns: filtered DataFrame.
    """
    from vizro.actions._filter_action import _filter

    for ctd in ctds_filter:
        selector_value = ctd["value"]
        selector_value = selector_value if isinstance(selector_value, list) else [selector_value]
        selector_actions = _get_component_actions(model_manager[ctd["id"]])

        for action in selector_actions:
            # TODO-AV2 A 1: simplify this as in
            #  https://github.com/mckinsey/vizro/pull/1054/commits/f4c8c5b153f3a71b93c018e9f8c6f1b918ca52f6
            if not isinstance(action, _filter) or target not in action.targets or ALL_OPTION in selector_value:
                continue

            mask = action.filter_function(data_frame[action.column], selector_value)
            data_frame = data_frame[mask]

    return data_frame


def _get_parent_model(_underlying_callable_object_id: str) -> VizroBaseModel:
    from vizro.models import VizroBaseModel

    for model in cast(Iterable[VizroBaseModel], model_manager._get_models()):
        if hasattr(model, "_inner_component_id") and model._inner_component_id == _underlying_callable_object_id:
            return model
    raise KeyError(
        f"No parent Vizro model found for underlying callable object with id: {_underlying_callable_object_id}."
    )


def _apply_filter_interaction(
    data_frame: pd.DataFrame, ctds_filter_interaction: list[dict[str, CallbackTriggerDict]], target: ModelID
) -> pd.DataFrame:
    """Applies filters from a filter_interaction.

    This will be removed in future when filter interactions are implemented using controls.

    Args:
        data_frame: unfiltered DataFrame.
        ctds_filter_interaction: structure containing CallbackTriggerDict for filter interactions.
        target: id of targeted Figure.

    Returns: filtered DataFrame.
    """
    for ctd_filter_interaction in ctds_filter_interaction:
        triggered_model = model_manager[ctd_filter_interaction["modelID"]["id"]]
        data_frame = cast(FigureWithFilterInteractionType, triggered_model)._filter_interaction(
            data_frame=data_frame,
            target=target,
            ctd_filter_interaction=ctd_filter_interaction,
        )

    return data_frame


def _validate_selector_value_none(value: Union[SingleValueType, MultiValueType]) -> ValidatedNoneValueType:
    if value == NONE_OPTION:
        return None
    if isinstance(value, list) and len(value):
        return [i for i in value if i != NONE_OPTION] or [None]  # type: ignore[list-item]
    return value


def _get_target_dot_separated_strings(dot_separated_strings: list[str], target: ModelID, data_frame: bool) -> list[str]:
    """Filters list of dot separated strings to get just those relevant for a single target.

    Args:
        dot_separated_strings: list of dot separated strings that can be targeted by a vm.Parameter,
            e.g. ["target_name.data_frame.arg", "target_name.x"]
        target: id of targeted Figure.
        data_frame: whether to return only DataFrame parameters starting "data_frame." or only non-DataFrame parameters.

    Returns:
        List of dot separated strings for target.
    """
    result = []

    for dot_separated_string_with_target in dot_separated_strings:
        if dot_separated_string_with_target.startswith(f"{target}."):
            dot_separated_string = dot_separated_string_with_target.removeprefix(f"{target}.")
            # We only want data_frame parameters when data_frame = True.
            if dot_separated_string.startswith("data_frame.") == data_frame:
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
    ctds_parameter: list[CallbackTriggerDict], target: ModelID, data_frame: bool
) -> dict[str, Any]:
    """Convert parameters into a keyword-argument dictionary.

    Args:
        ctds_parameter: list of CallbackTriggerDicts for vm.Parameter.
        target: id of targeted figure.
        data_frame: whether to return only DataFrame parameters starting "data_frame." or only non-DataFrame parameters.

    Returns: keyword-argument dictionary.

    """
    from vizro.actions._parameter_action import _parameter

    if data_frame:
        # This entry is inserted (but will always be empty) even for static data so that the load/_multi_load calls
        # look identical for dynamic data with no arguments and static data. Note it's not possible to address nested
        # argument of data_frame like data_frame.x.y, just top-level ones like data_frame.x.
        config: dict[str, Any] = {"data_frame": {}}
    else:
        # TODO - avoid calling _captured_callable. Once we have done this we can remove _arguments from
        #  CapturedCallable entirely. This might mean not being able to address nested parameters.
        config = deepcopy(cast(FigureType, model_manager[target]).figure._arguments)
        del config["data_frame"]

    for ctd in ctds_parameter:
        # TODO: needs to be refactored so that it is independent of implementation details
        parameter_value = ctd["value"]

        selector = cast(SelectorType, model_manager[ctd["id"]])
        if hasattr(parameter_value, "__iter__") and ALL_OPTION in parameter_value:  # type: ignore[operator]
            # Even if an option is provided as list[dict], the Dash component only returns a list of values.
            # So we need to ensure that we always return a list only as well to provide consistent types.
            parameter_value = [option["value"] if isinstance(option, dict) else option for option in selector.options]

        parameter_value = _validate_selector_value_none(parameter_value)  # type: ignore[arg-type]

        for action in _get_component_actions(selector):
            # TODO-AV2 A 1: simplify this as in
            #  https://github.com/mckinsey/vizro/pull/1054/commits/f4c8c5b153f3a71b93c018e9f8c6f1b918ca52f6
            #  Potentially this function would move to the filter_interaction action. That will be deprecated so
            #  no need to worry too much if it doesn't work well, but we'll need to do something similar for the
            #  new interaction functionality anyway.
            if not isinstance(action, _parameter):
                continue

            for dot_separated_string in _get_target_dot_separated_strings(action.targets, target, data_frame):
                config = _update_nested_figure_properties(
                    figure_config=config, dot_separated_string=dot_separated_string, value=parameter_value
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
    filtered_data = _apply_filter_controls(data_frame=data, ctds_filter=ctds_filter, target=target)
    filtered_data = _apply_filter_interaction(
        data_frame=filtered_data, ctds_filter_interaction=ctds_filter_interaction, target=target
    )
    return filtered_data


def _get_unfiltered_data(
    ctds_parameter: list[CallbackTriggerDict], targets: list[ModelID]
) -> dict[ModelID, pd.DataFrame]:
    # Takes in multiple targets to ensure that data can be loaded efficiently using _multi_load and not repeated for
    # every single target.
    # Getting unfiltered data requires data frame parameters. We pass in all ctds_parameter and then find the
    # data_frame ones by passing data_frame=True in the call to _get_paramaterized_config. Static data is also
    # handled here and will just have empty dictionary for its kwargs.
    multi_data_source_name_load_kwargs: list[tuple[DataSourceName, dict[str, Any]]] = []
    for target in targets:
        dynamic_data_load_params = _get_parametrized_config(
            ctds_parameter=ctds_parameter, target=target, data_frame=True
        )
        data_source_name = cast(FigureType, model_manager[target])["data_frame"]
        multi_data_source_name_load_kwargs.append((data_source_name, dynamic_data_load_params["data_frame"]))

    return dict(zip(targets, data_manager._multi_load(multi_data_source_name_load_kwargs)))


# TODO-AV2 A 2: rename this, make sure it could become public in future but don't make public yet. Probably take in
#  controls + filter_interaction only once have worked out structure of filters/parameters. Then make public once
#  have removed filter_interaction.
def _get_modified_page_figures(
    ctds_filter: list[CallbackTriggerDict],
    ctds_filter_interaction: list[dict[str, CallbackTriggerDict]],
    ctds_parameter: list[CallbackTriggerDict],
    targets: list[ModelID],
) -> dict[ModelID, Any]:
    from vizro.models import Filter

    outputs: dict[ModelID, Any] = {}

    control_targets = []
    figure_targets = []
    for target in targets:
        if isinstance(model_manager[target], Filter):
            control_targets.append(target)
        else:
            figure_targets.append(target)

    target_to_data_frame = _get_unfiltered_data(ctds_parameter=ctds_parameter, targets=figure_targets)

    # TODO: the structure here would be nicer if we could get just the ctds for a single target at one time,
    #  so you could do apply_filters on a target a pass only the ctds relevant for that target.
    #  Consider restructuring ctds to a more convenient form to make this possible.
    for target, unfiltered_data in target_to_data_frame.items():
        filtered_data = _apply_filters(unfiltered_data, ctds_filter, ctds_filter_interaction, target)
        outputs[target] = cast(FigureType, model_manager[target])(
            data_frame=filtered_data,
            **_get_parametrized_config(ctds_parameter=ctds_parameter, target=target, data_frame=False),
        )

    for target in control_targets:
        target_model = cast(Filter, model_manager[target])
        ctd_filter = [item for item in ctds_filter if item["id"] == cast(SelectorType, target_model.selector).id]

        # This only covers the case of cross-page actions when Filter in an output, but is not an input of the action.
        current_value = ctd_filter[0]["value"] if ctd_filter else None

        # target_to_data_frame contains all targets, including some which might not be relevant for the filter in
        # question. We filter to use just the relevant targets in Filter.__call__.
        outputs[target] = target_model(target_to_data_frame=target_to_data_frame, current_value=current_value)

    return outputs
