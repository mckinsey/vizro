from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal, Optional

import pandas as pd
from pandas.api.types import is_numeric_dtype, is_period_dtype
from pydantic import Field, PrivateAttr, validator

from vizro._constants import FILTER_ACTION_PREFIX
from vizro.actions import _filter
from vizro.managers import data_manager, model_manager
from vizro.models import Action, VizroBaseModel
from vizro.models._components.form import (
    Checklist,
    Dropdown,
    RadioItems,
    RangeSlider,
    Slider,
)
from vizro.models._models_utils import _log_call
from vizro.models.types import MultiValueType, SelectorType

if TYPE_CHECKING:
    from vizro.models import Page


# TODO: Add temporal when relevant component is available
SELECTOR_DEFAULTS = {"numerical": RangeSlider, "categorical": Dropdown}

# Ideally we might define these as NumericalSelectorType = Union[RangeSlider, Slider] etc., but that will not work
# with isinstance checks.
SELECTORS = {"numerical": (RangeSlider, Slider), "categorical": (Checklist, Dropdown, RadioItems)}


def _filter_between(series: pd.Series, value: List[float]) -> pd.Series:
    return series.between(value[0], value[1], inclusive="both")


def _filter_isin(series: pd.Series, value: MultiValueType) -> pd.Series:
    return series.isin(value)


def _get_component_page(component_id: str) -> Page:  # type: ignore[return]
    from vizro.models import Page

    for page_id, page in model_manager._items_with_type(Page):
        if any(control.id == component_id for control in page.controls):
            return page


class Filter(VizroBaseModel):
    """Filter the data supplied to `targets` on the [`Page`][vizro.models.Page].

    Examples:
        >>> print(repr(Filter(column="species")))

    Args:
        type (Literal["filter"]): Defaults to `"filter"`.
        column (str): Column of `DataFrame` to filter.
        targets (List[str]): Target component to be affected by filter. If none are given then target all components on
            the page that use `column`.
        selector (Optional[SelectorType]): See [SelectorType][vizro.models.types.SelectorType]. Defaults to `None`.
    """

    type: Literal["filter"] = "filter"
    column: str = Field(..., description="Column of DataFrame to filter.")
    targets: List[str] = Field(
        [],
        description="Target component to be affected by filter. "
        "If none are given then target all components on the page that use `column`.",
    )
    selector: Optional[SelectorType]
    _column_type: Optional[Literal["numerical", "categorical"]] = PrivateAttr()

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
        self._set_slider_values()
        self._set_categorical_selectors_options()
        self._set_actions()

    @_log_call
    def build(self):
        return self.selector.build()  # type: ignore[union-attr]

    def _set_targets(self):
        if not self.targets:
            for component in _get_component_page(self.id).components:  # type: ignore[arg-type]
                if data_manager._has_registered_data(component.id):
                    data_frame = data_manager._get_component_data(component.id)
                    if self.column in data_frame.columns:
                        self.targets.append(component.id)
            if not self.targets:
                raise ValueError(f"Selected column {self.column} not found in any dataframe on this page.")

    def _set_column_type(self):
        data_frame = data_manager._get_component_data(self.targets[0])
        if is_period_dtype(data_frame[self.column]) or is_numeric_dtype(data_frame[self.column]):
            self._column_type = "numerical"
        else:
            self._column_type = "categorical"

    def _set_selector(self):
        if self.selector is None:
            self.selector = SELECTOR_DEFAULTS[self._column_type](title=self.column.title())  # type: ignore[index]
        elif not self.selector.title:
            self.selector.title = self.column.title()

    def _set_slider_values(self):
        self.selector: SelectorType
        if isinstance(self.selector, SELECTORS["numerical"]):
            if self._column_type != "numerical":
                raise ValueError(
                    f"Chosen selector {self.selector.type} is not compatible with column_type {self._column_type}."
                )
            min_values = []
            max_values = []
            for target_id in self.targets:
                data_frame = data_manager._get_component_data(target_id)
                min_values.append(data_frame[self.column].min())
                max_values.append(data_frame[self.column].max())
            if not is_numeric_dtype(min(min_values)) or not is_numeric_dtype(max(max_values)):
                raise ValueError(f"No numeric value detected in chosen column {self.column} for numerical selector.")
            if self.selector.min is None:
                self.selector.min = min(min_values)
            if self.selector.max is None:
                self.selector.max = max(max_values)

    def _set_categorical_selectors_options(self):
        self.selector: SelectorType
        if isinstance(self.selector, SELECTORS["categorical"]) and not self.selector.options:
            options = set()
            for target_id in self.targets:
                data_frame = data_manager._get_component_data(target_id)
                options |= set(data_frame[self.column])

            self.selector.options = sorted(options)

    def _set_actions(self):
        self.selector: SelectorType
        if not self.selector.actions:
            filter_function = _filter_between if isinstance(self.selector, RangeSlider) else _filter_isin
            self.selector.actions = [
                Action(
                    function=_filter(
                        filter_column=self.column,
                        targets=self.targets,
                        filter_function=filter_function,
                    ),
                    id=f"{FILTER_ACTION_PREFIX}_{self.id}",
                )
            ]
