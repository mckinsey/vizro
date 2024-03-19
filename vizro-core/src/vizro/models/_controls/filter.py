from __future__ import annotations

from typing import List, Literal, Union

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


def _filter_between(series: pd.Series, value: Union[List[float], List[str]]) -> pd.Series:
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
        targets (List[ModelID]): Target component to be affected by filter. If none are given then target all components
            on the page that use `column`.
        selector (SelectorType): See [SelectorType][vizro.models.types.SelectorType]. Defaults to `None`.

    """

    type: Literal["filter"] = "filter"
    column: str = Field(..., description="Column of DataFrame to filter.")
    targets: List[ModelID] = Field(
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
        self._set_targets()
        self._set_column_type()
        self._set_selector()
        self._validate_disallowed_selector()
        self._set_numerical_and_temporal_selectors_values()
        self._set_categorical_selectors_options()
        self._set_actions()

    @_log_call
    def build(self):
        return self.selector.build()

    def _set_targets(self):
        if not self.targets:
            for component_id in model_manager._get_page_model_ids_with_figure(
                page_id=model_manager._get_model_page_id(model_id=ModelID(str(self.id)))
            ):
                data_frame = data_manager._get_component_data(component_id)
                if self.column in data_frame.columns:
                    self.targets.append(component_id)
            if not self.targets:
                raise ValueError(f"Selected column {self.column} not found in any dataframe on this page.")

    def _set_column_type(self):
        data_frame = data_manager._get_component_data(self.targets[0])

        if is_numeric_dtype(data_frame[self.column]):
            self._column_type = "numerical"
        elif is_datetime64_any_dtype(data_frame[self.column]):
            self._column_type = "temporal"
        else:
            self._column_type = "categorical"

    def _set_selector(self):
        self.selector = self.selector or SELECTORS[self._column_type][0]()
        self.selector.title = self.selector.title or self.column.title()

    def _validate_disallowed_selector(self):
        if isinstance(self.selector, DISALLOWED_SELECTORS.get(self._column_type, ())):
            raise ValueError(
                f"Chosen selector {self.selector.type} is not compatible "
                f"with {self._column_type} column '{self.column}'. "
            )

    def _set_numerical_and_temporal_selectors_values(self):
        # If the selector is a numerical or temporal selector, and the min and max values are not set, then set them
        # N.B. All custom selectors inherit from numerical or temporal selector should also pass this check
        if isinstance(self.selector, SELECTORS["numerical"] + SELECTORS["temporal"]):
            min_values = []
            max_values = []
            for target_id in self.targets:
                data_frame = data_manager._get_component_data(target_id)
                min_values.append(data_frame[self.column].min())
                max_values.append(data_frame[self.column].max())

            if not (
                is_numeric_dtype(pd.Series(min_values))
                and is_numeric_dtype(pd.Series(max_values))
                or is_datetime64_any_dtype(pd.Series(min_values))
                and is_datetime64_any_dtype(pd.Series(max_values))
            ):
                raise ValueError(
                    f"Inconsistent types detected in the shared data column '{self.column}' for targeted charts "
                    f"{self.targets}. Please ensure that the data column contains the same data type across all "
                    f"targeted charts."
                )

            if self.selector.min is None:
                self.selector.min = min(min_values)
            if self.selector.max is None:
                self.selector.max = max(max_values)

    def _set_categorical_selectors_options(self):
        # If the selector is a categorical selector, and the options are not set, then set them
        # N.B. All custom selectors inherit from categorical selector should also pass this check
        if isinstance(self.selector, SELECTORS["categorical"]) and not self.selector.options:
            options = set()
            for target_id in self.targets:
                data_frame = data_manager._get_component_data(target_id)
                options |= set(data_frame[self.column])

            self.selector.options = sorted(options)

    def _set_actions(self):
        if not self.selector.actions:
            if isinstance(self.selector, RangeSlider) or (
                isinstance(self.selector, DatePicker) and self.selector.range
            ):
                filter_function = _filter_between
            else:
                filter_function = _filter_isin

            self.selector.actions = [
                Action(
                    function=_filter(filter_column=self.column, targets=self.targets, filter_function=filter_function),
                    id=f"{FILTER_ACTION_PREFIX}_{self.id}",
                )
            ]
