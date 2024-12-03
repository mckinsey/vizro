from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Literal, Union, cast

import pandas as pd
from dash import dcc
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype

from vizro.managers._data_manager import DataSourceName

try:
    from pydantic.v1 import Field, PrivateAttr, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, PrivateAttr, validator

from vizro._constants import ALL_OPTION, FILTER_ACTION_PREFIX
from vizro.actions import _filter
from vizro.managers import data_manager, model_manager
from vizro.managers._data_manager import _DynamicData
from vizro.managers._model_manager import FIGURE_MODELS, ModelID
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

# TODO: Remove DYNAMIC_SELECTORS along with its validation check when support dynamic mode for the DatePicker selector.
# Tuple of filter selectors that support dynamic mode
DYNAMIC_SELECTORS = (Dropdown, Checklist, RadioItems, Slider, RangeSlider)


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

    _dynamic: bool = PrivateAttr(False)

    # Component properties for actions and interactions
    _output_component_property: str = PrivateAttr("children")

    _column_type: Literal["numerical", "categorical", "temporal"] = PrivateAttr()

    @validator("targets", each_item=True)
    def check_target_present(cls, target):
        if target not in model_manager:
            raise ValueError(f"Target {target} not found in model_manager.")
        return target

    def __call__(self, target_to_data_frame: dict[ModelID, pd.DataFrame], current_value: Any):
        # Only relevant for a dynamic filter.
        # Although targets are fixed at build time, the validation logic is repeated during runtime, so if a column
        # is missing then it will raise an error. We could change this if we wanted.
        targeted_data = self._validate_targeted_data(
            {target: data_frame for target, data_frame in target_to_data_frame.items() if target in self.targets},
            eagerly_raise_column_not_found_error=True,
        )

        if (column_type := self._validate_column_type(targeted_data)) != self._column_type:
            raise ValueError(
                f"{self.column} has changed type from {self._column_type} to {column_type}. A filtered column cannot "
                "change type while the dashboard is running."
            )

        if isinstance(self.selector, SELECTORS["categorical"]):
            return self.selector(options=self._get_options(targeted_data, current_value))
        else:
            _min, _max = self._get_min_max(targeted_data, current_value)
            # "current_value" is propagated only to support dcc.Input and dcc.Store components in numerical selectors
            # to work with a dynamic selector. This can be removed when dash persistence bug is fixed.
            return self.selector(min=_min, max=_max, current_value=current_value)

    @_log_call
    def pre_build(self):
        # If targets aren't explicitly provided then try to target all figures on the page. In this case we don't
        # want to raise an error if the column is not found in a figure's data_frame, it will just be ignored.
        # This is the case when bool(self.targets) is False.
        # Possibly in future this will change (which would be breaking change).
        proposed_targets = self.targets or [
            cast(ModelID, model.id)
            for model in cast(
                Iterable[VizroBaseModel], model_manager._get_models(FIGURE_MODELS, model_manager._get_model_page(self))
            )
        ]
        # TODO: Currently dynamic data functions require a default value for every argument. Even when there is a
        #  dataframe parameter, the default value is used when pre-build the filter e.g. to find the targets,
        #  column type (and hence selector) and initial values. There are three ways to handle this:
        #  1. (Current approach) - Propagate {} and use only default arguments value in the dynamic data function.
        #  2. Propagate values from the model_manager and relax the limitation of requiring argument default values.
        #  3. Skip the pre-build and do everything in the build method (if possible).
        #  Find more about the mentioned limitation at: https://github.com/mckinsey/vizro/pull/879/files#r1846609956
        # Even if the solution changes for dynamic data, static data should still use {} as the arguments here.
        multi_data_source_name_load_kwargs: list[tuple[DataSourceName, dict[str, Any]]] = [
            (model_manager[target]["data_frame"], {}) for target in proposed_targets
        ]

        target_to_data_frame = dict(zip(proposed_targets, data_manager._multi_load(multi_data_source_name_load_kwargs)))
        targeted_data = self._validate_targeted_data(
            target_to_data_frame, eagerly_raise_column_not_found_error=bool(self.targets)
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

        # Check if the filter is dynamic. Dynamic filter means that the filter is updated when the page is refreshed
        # which causes "options" for categorical or "min" and "max" for numerical/temporal selectors to be updated.
        # The filter is dynamic iff mentioned attributes ("options"/"min"/"max") are not explicitly provided and
        # filter targets at least one figure that uses dynamic data source. Note that min or max = 0 are Falsey values
        # but should still count as manually set.
        if isinstance(self.selector, DYNAMIC_SELECTORS) and (
            not getattr(self.selector, "options", [])
            and getattr(self.selector, "min", None) is None
            and getattr(self.selector, "max", None) is None
        ):
            for target_id in self.targets:
                data_source_name = model_manager[target_id]["data_frame"]
                if isinstance(data_manager[data_source_name], _DynamicData):
                    self._dynamic = True
                    self.selector._dynamic = True
                    break

        # Set appropriate properties for the selector.
        if isinstance(self.selector, SELECTORS["numerical"] + SELECTORS["temporal"]):
            _min, _max = self._get_min_max(targeted_data)
            # Note that manually set self.selector.min/max = 0 are Falsey but should not be overwritten.
            if self.selector.min is None:
                self.selector.min = _min
            if self.selector.max is None:
                self.selector.max = _max
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

    @_log_call
    def build(self):
        selector_build_obj = self.selector.build()
        # TODO: Align the (dynamic) object's return structure with the figure's components when the Dash bug is fixed.
        #  This means returning an empty "html.Div(id=self.id, className=...)" as a placeholder from Filter.build().
        #  Also, make selector.title visible when the filter is reloading.
        if not self._dynamic:
            return selector_build_obj

        # Temporarily hide the selector and numeric dcc.Input components during the filter reloading process.
        # Other components, such as the title, remain visible because of the configuration:
        # overlay_style={"visibility": "visible"} in dcc.Loading.
        # Note: dcc.Slider and dcc.RangeSlider do not support the "style" property directly,
        # so the "className" attribute is used to apply custom CSS for visibility control.
        # Reference for Dash class names: https://dashcheatsheet.pythonanywhere.com/
        selector_build_obj[self.selector.id].className = "invisible"
        if f"{self.selector.id}_start_value" in selector_build_obj:
            selector_build_obj[f"{self.selector.id}_start_value"].className = "d-none"
        if f"{self.selector.id}_end_value" in selector_build_obj:
            selector_build_obj[f"{self.selector.id}_end_value"].className = "d-none"

        return dcc.Loading(
            id=self.id,
            children=selector_build_obj,
            color="grey",
            overlay_style={"visibility": "visible"},
        )

    def _validate_targeted_data(
        self, target_to_data_frame: dict[ModelID, pd.DataFrame], eagerly_raise_column_not_found_error
    ) -> pd.DataFrame:
        target_to_series = {}

        for target, data_frame in target_to_data_frame.items():
            if self.column in data_frame.columns:
                # reset_index so that when we make a DataFrame out of all these pd.Series pandas doesn't try to align
                # the columns by index.
                target_to_series[target] = data_frame[self.column].reset_index(drop=True)
            elif eagerly_raise_column_not_found_error:
                raise ValueError(f"Selected column {self.column} not found in dataframe for {target}.")

        targeted_data = pd.DataFrame(target_to_series)
        if targeted_data.columns.empty:
            # Still raised when eagerly_raise_column_not_found_error=False.
            raise ValueError(
                f"Selected column {self.column} not found in any dataframe for "
                f"{', '.join(target_to_data_frame.keys())}."
            )
        # TODO: Enable empty data_frame handling
        if targeted_data.empty:
            raise ValueError(
                f"Selected column {self.column} does not contain anything in any dataframe for "
                f"{', '.join(target_to_data_frame.keys())}."
            )

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
                f"Inconsistent types detected in column {self.column}. This column must have the same type for all "
                "targets."
            )

    @staticmethod
    def _get_min_max(targeted_data: pd.DataFrame, current_value=None) -> tuple[float, float]:
        targeted_data = pd.concat([targeted_data, pd.Series(current_value)]).stack().dropna()  # noqa: PD013

        _min = targeted_data.min(axis=None)
        _max = targeted_data.max(axis=None)

        # Use item() to convert to convert scalar from numpy to Python type. This isn't needed during pre_build because
        # pydantic will coerce the type, but it is necessary in __call__ where we don't update model field values
        # and instead just pass straight to the Dash component.
        # However, in some cases _min and _max are already Python types and so item() call is not required.
        _min = _min if not hasattr(_min, "item") else _min.item()
        _max = _max if not hasattr(_max, "item") else _max.item()

        return _min, _max

    @staticmethod
    def _get_options(targeted_data: pd.DataFrame, current_value=None) -> list[Any]:
        # The dropna() isn't strictly required here but will be in future pandas versions when the behavior of stack
        # changes. See https://pandas.pydata.org/docs/whatsnew/v2.1.0.html#whatsnew-210-enhancements-new-stack.
        targeted_data = pd.concat([targeted_data, pd.Series(current_value)]).stack().dropna()  # noqa: PD013
        return sorted(set(targeted_data) - {ALL_OPTION})
