from __future__ import annotations

from dash import dcc, html

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
from vizro.models._components.form._form_utils import get_options_and_default
from vizro.managers._data_manager import _DynamicData

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

# TODO: Remove this check because all vizro selectors support dynamic mode
# Tuple of filter selectors that support dynamic mode
DYNAMIC_SELECTORS = (Dropdown, Checklist, RadioItems, Slider, RangeSlider)


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

    _dynamic: bool = PrivateAttr(None)

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
        self._set_dynamic()
        self._set_numerical_and_temporal_selectors_values()
        self._set_categorical_selectors_options()
        self._set_actions()

    @_log_call
    def build(self):
        selector_build_obj = self.selector.build()
        return dcc.Loading(id=self.id, children=selector_build_obj) if self._dynamic else selector_build_obj

    def _set_targets(self):
        if not self.targets:
            for component_id in model_manager._get_page_model_ids_with_figure(
                page_id=model_manager._get_model_page_id(model_id=ModelID(str(self.id)))
            ):
                # TODO: consider making a helper method in data_manager or elsewhere to reduce this operation being
                #  duplicated across Filter so much, and/or consider storing the result to avoid repeating it.
                #  Need to think about this in connection with how to update filters on the fly and duplicated calls
                #  issue outlined in https://github.com/mckinsey/vizro/pull/398#discussion_r1559120849.
                data_source_name = model_manager[component_id]["data_frame"]
                data_frame = data_manager[data_source_name].load()
                if self.column in data_frame.columns:
                    self.targets.append(component_id)
            if not self.targets:
                raise ValueError(f"Selected column {self.column} not found in any dataframe on this page.")

    def _set_column_type(self):
        data_source_name = model_manager[self.targets[0]]["data_frame"]
        data_frame = data_manager[data_source_name].load()

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

    def _set_dynamic(self):
        self._dynamic = False

        # Selector can't be dynamic if:
        # Selector doesn't support dynamic mode
        # Selector is categorical and "options" is defined
        # Selector is numerical/Temporal and "min" and "max" are defined
        if (
            not isinstance(self.selector, DYNAMIC_SELECTORS)
            or getattr(self.selector, "options", False)
            or any(getattr(self.selector, attr, False) for attr in ["min", "max"])
        ):
            return

        for target_id in self.targets:
            data_source_name = model_manager[target_id]["data_frame"]
            if isinstance(data_manager[data_source_name], _DynamicData):
                self._dynamic = True
                self.selector._dynamic = True
                return

    def _set_numerical_and_temporal_selectors_values(self, force=False, current_value=None):
        # If the selector is a numerical or temporal selector, and the min and max values are not set, then set them
        # N.B. All custom selectors inherit from numerical or temporal selector should also pass this check
        if isinstance(self.selector, SELECTORS["numerical"] + SELECTORS["temporal"]):
            lvalue, hvalue = (
                (current_value[0], current_value[1])
                if isinstance(current_value, list) and len(current_value) == 2
                else (current_value[0], current_value[0])
                if isinstance(current_value, list) and len(current_value) == 1
                else (current_value, current_value)
            )

            min_values = [] if lvalue is None else [lvalue]
            max_values = [] if hvalue is None else [hvalue]
            for target_id in self.targets:
                data_source_name = model_manager[target_id]["data_frame"]
                data_frame = data_manager[data_source_name].load()
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

            if self.selector.min is None or force:
                self.selector.min = min(min_values)
            if self.selector.max is None or force:
                self.selector.max = max(max_values)

    def _set_categorical_selectors_options(self, force=False, current_value=None):
        # If the selector is a categorical selector, and the options are not set, then set them
        # N.B. All custom selectors inherit from categorical selector should also pass this check
        if isinstance(self.selector, SELECTORS["categorical"]) and (not self.selector.options or force):
            current_value = current_value or []
            current_value = current_value if isinstance(current_value, list) else [current_value]
            options = set(current_value)
            for target_id in self.targets:
                data_source_name = model_manager[target_id]["data_frame"]
                data_frame = data_manager[data_source_name].load()
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
                    id=f"{FILTER_ACTION_PREFIX}_{self.id}",
                    function=_filter(filter_column=self.column, targets=self.targets, filter_function=filter_function),
                )
            ]
