from __future__ import annotations

from typing import Literal, Union

import numpy as np
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype

try:
    from pydantic.v1 import Field, PrivateAttr, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, PrivateAttr, validator

from vizro._constants import FILTER_ACTION_PREFIX
from vizro.actions import _filter
from vizro.managers import data_manager, model_manager
from vizro.managers._model_manager import ModelID
from vizro.models import Action, VizroBaseModel
from vizro.models._components.form import (
    Checklist,
    DatePicker,
    Dropdown,
    RadioItems,
    RangeSlider,
    Slider,
)
from vizro.models._models_utils import _log_call
from vizro.models.types import MultiValueType, SelectorType

# Ideally we might define these as NumericalSelectorType = Union[RangeSlider, Slider] etc., but that will not work
# with isinstance checks.
# First entry in each tuple is the default selector for that column type.
SELECTORS = {
    "numerical": (RangeSlider, Slider),
    "categorical": (Dropdown, Checklist, RadioItems),
    "temporal": (DatePicker,),
}

# This disallowed selectors for each column type map is based on the discussion at the following link:
# See https://github.com/mckinsey/vizro/pull/319#discussion_r1524888171
DISALLOWED_SELECTORS = {
    "numerical": SELECTORS["temporal"],
    "temporal": SELECTORS["numerical"],
    "categorical": SELECTORS["numerical"] + SELECTORS["temporal"],
}


def _filter_between(series: pd.Series, value: Union[list[float], list[str]]) -> pd.Series:
    if is_datetime64_any_dtype(series):
        # Each value will always have time 00:00:00. In order for the filter to include all times during
        # the end date value[1] we need to remove the time part of every value in series so that it's 00:00:00.
        value = pd.to_datetime(value)
        series = pd.to_datetime(series.dt.date)
    return series.between(value[0], value[1], inclusive="both")


def _filter_isin(series: pd.Series, value: MultiValueType) -> pd.Series:
    if is_datetime64_any_dtype(series):
        # Value will always have time 00:00:00. In order for the filter to include all times during
        # the end date value we need to remove the time part of every value in series so that it's 00:00:00.
        value = pd.to_datetime(value)
        series = pd.to_datetime(series.dt.date)
    return series.isin(value)


class Filter(VizroBaseModel):
    """Filter the data supplied to `targets` on the [`Page`][vizro.models.Page].

    Examples:
        >>> print(repr(Filter(column="species")))

    Args:
        type (Literal["filter"]): Defaults to `"filter"`.
        column (str): Column of `DataFrame` to filter.
        targets (list[ModelID]): Target component to be affected by filter. If none are given then target all components
            on the page that use `column`.
        selector (SelectorType): See [SelectorType][vizro.models.types.SelectorType]. Defaults to `None`.

    """

    type: Literal["filter"] = "filter"
    column: str = Field(..., description="Column of DataFrame to filter.")
    targets: list[ModelID] = Field(
        [],
        description="Target component to be affected by filter. "
        "If none are given then target all components on the page that use `column`.",
    )
    selector: SelectorType = None
    _column_type: Literal["numerical", "categorical", "temporal"] = PrivateAttr()

    @validator("targets", each_item=True)
    def check_target_present(cls, target):
        if target not in model_manager:
            raise ValueError(f"Target {target} not found in model_manager.")
        return target

    @_log_call
    def pre_build(self):
        if self.targets:
            targeted_data = self._validate_targeted_data(targets=self.targets)
        else:
            # If targets aren't explicitly provided then try to target all figures on the page. In this case we don't
            # want to raise an error if the column is not found in a figure's data_frame, it will just be ignored.
            # Possibly in future this will change (which would be breaking change).
            targeted_data = self._validate_targeted_data(
                targets=model_manager._get_page_model_ids_with_figure(
                    page_id=model_manager._get_model_page_id(model_id=ModelID(str(self.id)))
                ),
                eagerly_raise_column_not_found_error=False,
            )
            self.targets = list(targeted_data.columns)

        # Set default selector according to column type.
        self._column_type = self._validate_column_type(targeted_data)
        self.selector = self.selector or SELECTORS[self._column_type][0]()
        self.selector.title = self.selector.title or self.column.title()

        if isinstance(self.selector, DISALLOWED_SELECTORS.get(self._column_type, ())):
            raise ValueError(
                f"Chosen selector {type(self.selector).__name__} is not compatible with {self._column_type} column "
                f"'{self.column}'."
            )

        # Set appropriate properties for the selector.
        if isinstance(self.selector, SELECTORS["numerical"] + SELECTORS["temporal"]):
            _min, _max = self._get_min_max(targeted_data)
            self.selector.min = self.selector.min or _min
            self.selector.max = self.selector.max or _max
        else:
            # Categorical selector.
            self.selector.options = self.selector.options or self._get_options(targeted_data)

        if not self.selector.actions:
            if isinstance(self.selector, RangeSlider) or (
                isinstance(self.selector, DatePicker) and self.selector.range
            ):
                filter_function = _filter_between
            else:
                filter_function = _filter_isin

            self.selector.actions = [
                Action(
                    id=f"{FILTER_ACTION_PREFIX}_{self.id}",
                    function=_filter(filter_column=self.column, targets=self.targets, filter_function=filter_function),
                )
            ]

    def __call__(self, **kwargs):
        # Only relevant for a dynamic filter.
        # TODO: this will need to pass parametrised data_frame arguments through to _validate_targeted_data.
        # Although targets are fixed at build time, the validation logic is repeated during runtime, so if a column
        # is missing then it will raise an error. We could change this if we wanted.
        targeted_data = self._validate_targeted_data(targets=self.targets)

        if (column_type := self._validate_column_type(targeted_data)) != self._column_type:
            raise ValueError(
                f"{self.column} has changed type from {self._column_type} to {column_type}. A filtered column cannot "
                "change type while the dashboard is running."
            )

        # TODO: when implement dynamic, will need to do something with this e.g. pass to selector.__call__.
        # if isinstance(self.selector, SELECTORS["numerical"] + SELECTORS["temporal"]):
        #     options = self._get_options(targeted_data)
        # else:
        #     # Categorical selector.
        #     _min, _max = self._get_min_max(targeted_data)

    @_log_call
    def build(self):
        return self.selector.build()

    def _validate_targeted_data(
        self, targets: list[ModelID], eagerly_raise_column_not_found_error=True
    ) -> pd.DataFrame:
        # TODO: consider moving some of this logic to data_manager when implement dynamic filter. Make sure
        #  get_modified_figures and stuff in _actions_utils.py is as efficient as code here.

        # When loading data_frame there are possible keys:
        #  1. target. In worst case scenario this is needed but can lead to unnecessary repeated data loading.
        #  2. data_source_name. No repeated data loading but won't work when applying data_frame parameters at runtime.
        #  3. target + data_frame parameters keyword-argument pairs. This is the correct key to use at runtime.
        # For now we follow scheme 2 for data loading (due to set() below) and 1 for the returned targeted_data
        # pd.DataFrame, i.e. a separate column for each target even if some data is repeated.
        # TODO: when this works with data_frame parameters load() will need to take arguments and the structures here
        #  might change a bit.
        target_to_data_source_name = {target: model_manager[target]["data_frame"] for target in targets}
        data_source_name_to_data = {
            data_source_name: data_manager[data_source_name].load()
            for data_source_name in set(target_to_data_source_name.values())
        }
        target_to_series = dict()

        for target, data_source_name in target_to_data_source_name.items():
            data_frame = data_source_name_to_data[data_source_name]

            if self.column in data_frame.columns:
                # reset_index so that when we make a DataFrame out of all these pd.Series pandas doesn't try to align
                # the columns by index.
                target_to_series[target] = data_frame[self.column].reset_index(drop=True)
            elif eagerly_raise_column_not_found_error:
                raise ValueError(f"Selected column {self.column} not found in dataframe for {target}.")

        targeted_data = pd.DataFrame(target_to_series)
        if targeted_data.columns.empty:
            # Still raised when eagerly_raise_column_not_found_error=False.
            raise ValueError(f"Selected column {self.column} not found in any dataframe for {', '.join(targets)}.")
        if targeted_data.empty:
            raise ValueError(f"Selected column {self.column} does not contain any data.")

        return targeted_data

    def _validate_column_type(self, targeted_data: pd.DataFrame) -> Literal["numerical", "categorical", "temporal"]:
        is_numerical = targeted_data.apply(is_numeric_dtype)
        is_temporal = targeted_data.apply(is_datetime64_any_dtype)
        is_categorical = ~is_numerical & ~is_temporal

        if is_numerical.all():
            return "numerical"
        elif is_temporal.all():
            return "temporal"
        elif is_categorical.all():
            return "categorical"
        else:
            raise ValueError(
                f"Inconsistent types detected in the shared data column {self.column}. This column must "
                "have the same type for all targets."
            )

    # TODO: write tests. Include N/A
    # TODO: block all update of models during runtime
    def _get_min_max(self, targeted_data: pd.DataFrame) -> tuple[float, float]:
        # Use item() to convert to convert scalar from numpy to Python type. This isn't needed during pre_build because
        # pydantic will coerce the type, but it is necessary in __call__ where we don't update model field values
        # and instead just pass straight to the Dash component.
        return targeted_data.min(axis=None).item(), targeted_data.max(axis=None).item()

    def _get_options(self, targeted_data: pd.DataFrame) -> list:
        # Use tolist() to convert to convert scalar from numpy to Python type. This isn't needed during pre_build
        # because pydantic will coerce the type, but it is necessary in __call__ where we don't update model field values
        # and instead just pass straight to the Dash component.
        return np.unique(targeted_data.stack().dropna()).tolist()
