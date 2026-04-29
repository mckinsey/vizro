from __future__ import annotations

from collections.abc import Callable, Iterable
from contextlib import suppress
from typing import Any, Literal, cast

import pandas as pd
from dash import dcc, html
from pandas.api.types import is_bool_dtype, is_datetime64_any_dtype, is_numeric_dtype
from pydantic import Field, PrivateAttr, model_validator

from vizro._constants import FILTER_ACTION_PREFIX
from vizro.actions import set_control, update_figures
from vizro.managers import data_manager, model_manager
from vizro.managers._data_manager import DataSourceName, _DynamicData
from vizro.managers._model_manager import FIGURE_MODELS
from vizro.models import VizroBaseModel
from vizro.models._components.form import Checklist, DatePicker, Dropdown, RangeSlider, Switch
from vizro.models._components.form.cascader import Cascader
from vizro.models._controls._controls_utils import (
    SELECTORS,
    _is_boolean_selector,
    _is_categorical_selector,
    _is_hierarchical_selector,
    _is_numerical_temporal_selector,
    check_control_targets,
    get_control_parent,
    get_selector_default_value,
    warn_missing_id_for_url_control,
)
from vizro.models._models_utils import _log_call
from vizro.models.types import FigureType, ModelID, MultiValueType, SelectorType, SingleValueType, _IdProperty

DEFAULT_SELECTORS = {
    "numerical": RangeSlider,
    "categorical": Dropdown,
    "temporal": DatePicker,
    "boolean": Switch,
    "hierarchical": Cascader,
}

# This disallowed selectors for each column type map is based on the discussion at the following link:
# See https://github.com/mckinsey/vizro/pull/319#discussion_r1524888171
# Really numerical data should also disallow SELECTORS["boolean"], but we allow it so that a column
# of 0s and 1s can be interpreted as boolean data. We could modify the detection of data type in
# validate_column_type to check for this case, but this would mean checking actual data values. This is
# something we should avoid at least until we have moved to narwhals since maybe it's an unnecessary
# performance hit.
DISALLOWED_SELECTORS = {
    "numerical": SELECTORS["temporal"],
    "temporal": SELECTORS["numerical"] + SELECTORS["boolean"],
    "categorical": SELECTORS["numerical"] + SELECTORS["temporal"] + SELECTORS["boolean"],
    "boolean": SELECTORS["numerical"] + SELECTORS["temporal"],
    "hierarchical": SELECTORS["numerical"] + SELECTORS["categorical"] + SELECTORS["temporal"] + SELECTORS["boolean"],
}


def _filter_between(series: pd.Series, value: list[float] | list[str]) -> pd.Series:
    if is_datetime64_any_dtype(series):
        # Each value will always have time 00:00:00. In order for the filter to include all times during
        # the end date value[1] we need to remove the time part of every value in series so that it's 00:00:00.
        value = pd.to_datetime(value)
        series = pd.to_datetime(series.dt.date)
    return series.between(value[0], value[1], inclusive="both")


def _dataframe_path_to_cascader_options(df: pd.DataFrame, path_columns: list[str]) -> dict[str, Any]:
    """Build nested Cascader options from unique rows via groupby then nested dict (str keys, list leaves).

    Callers must pass at least two column names (hierarchical filter path + leaf); see `Filter.column`.
    """
    sub = df[path_columns].drop_duplicates()
    if sub.empty:
        raise ValueError("Cannot build cascader options from empty path data.")

    branch_cols = path_columns[:-1]
    leaf_col = path_columns[-1]

    def _sorted_unique_leaves(s: pd.Series) -> list[Any]:
        return sorted(s.dropna().unique().tolist())

    leaves_by_branch = sub.groupby(branch_cols, observed=True, sort=True)[leaf_col].apply(_sorted_unique_leaves)

    def _assign_nested(root: dict[str, Any], branch_key: Any, leaves: list[Any]) -> None:
        parts = branch_key if isinstance(branch_key, tuple) else (branch_key,)
        node = root
        for k in parts[:-1]:
            node = node.setdefault(str(k), {})
        node[str(parts[-1])] = leaves

    out: dict[str, Any] = {}
    for branch_key, leaves in leaves_by_branch.items():
        _assign_nested(out, branch_key, leaves)
    return out


def _filter_isin(series: pd.Series, value: MultiValueType) -> pd.Series:
    """Filter using .isin() - works with boolean/categorical data.

    Switch selectors work with 0/1 columns due to pandas automatic type conversion:
    >>> pd.Series([0, 1]).isin([False])  # [True, False]
    >>> pd.Series([False, True]).isin([1])  # [False, True]
    """
    if is_datetime64_any_dtype(series):
        # Value will always have time 00:00:00. In order for the filter to include all times during
        # the end date value we need to remove the time part of every value in series so that it's 00:00:00.
        value = pd.to_datetime(value)
        series = pd.to_datetime(series.dt.date)
    return series.isin(value)


class Filter(VizroBaseModel):
    """Filter the data supplied to `targets`.

    Abstract: Usage documentation
        [How to use filters](../user-guides/filters.md)

    Example:
        ```python
        import vizro.models as vm

        vm.Filter(column="species")
        vm.Filter(column=["continent", "country"])
        ```
    """

    type: Literal["filter"] = "filter"
    column: str | list[str] = Field(
        description="Name of the column to filter, or an ordered list of column names for a hierarchical filter."
    )
    targets: list[ModelID] = Field(
        default=[],
        description="Target component to be affected by filter. "
        "If none are given then target all components on the page that use `column`.",
    )
    selector: SelectorType | None = None
    show_in_url: bool = Field(
        default=False,
        description=(
            "Whether the filter should be included in the URL query string. "
            "Useful for bookmarking or sharing dashboards with specific filter values pre-set."
        ),
    )
    visible: bool = Field(
        default=True,
        description="Whether the filter should be visible.",
    )

    _dynamic: bool = PrivateAttr(False)
    _filter_function: Callable[[pd.Series, Any], pd.Series] = PrivateAttr()
    _selector_properties: set[str] = PrivateAttr(set())
    _column_type: Literal["numerical", "categorical", "temporal", "boolean"] = PrivateAttr()

    @model_validator(mode="after")
    def check_id_set_for_url_control(self):
        """Check that the filter has an `id` set if it is shown in the URL."""
        # If the filter is shown in the URL, it should have an `id` set to ensure stable and readable URLs.
        warn_missing_id_for_url_control(control=self)
        return self

    @model_validator(mode="after")
    def _validate_column_and_selector_pairing(self):
        if isinstance(self.column, list) and len(self.column) <= 1:
            raise ValueError("When column is a list, provide at least two column names.")
        elif isinstance(self.column, str) and self.selector is not None and _is_hierarchical_selector(self.selector):
            raise TypeError("For a hierarchical selector, `column` must be a list of column names.")
        return self

    @property
    def _single_filter_column(self) -> str:
        return self.column if isinstance(self.column, str) else self.column[-1]

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        # Note this relies on the fact that filters are pre-built upfront in Vizro._pre_build. Otherwise,
        # control.selector might not be set. Cast is justified as the selector is set in pre_build and is not None.
        selector = cast(SelectorType, self.selector)
        return {
            "selector": f"{self.id}.children",
            **selector._action_outputs,
            **(
                {selector_prop: f"{selector.id}.{selector_prop}" for selector_prop in self._selector_properties}
                if self._selector_properties
                else {}
            ),
        }

    @property
    def _action_triggers(self) -> dict[str, _IdProperty]:
        # Note this relies on the fact that filters are pre-built upfront in Vizro._pre_build. Otherwise,
        # control.selector might not be set. Cast is justified as the selector is set in pre_build and is not None.
        selector = cast(SelectorType, self.selector)
        return selector._action_triggers

    @property
    def _action_inputs(self) -> dict[str, _IdProperty]:
        # Note this relies on the fact that filters are pre-built upfront in Vizro._pre_build. Otherwise,
        # control.selector might not be set. Cast is justified as the selector is set in pre_build and is not None.
        selector = cast(SelectorType, self.selector)
        return {
            **selector._action_inputs,
            **(
                {selector_prop: f"{selector.id}.{selector_prop}" for selector_prop in self._selector_properties}
                if self._selector_properties
                else {}
            ),
        }

    def __call__(self, target_to_data_frame: dict[ModelID, pd.DataFrame], current_value: Any):
        # Only relevant for a dynamic filter and non-boolean selectors. Boolean selectors don't need to be dynamic,
        # as their options are always set to True/False.
        # Although targets are fixed at build time, the validation logic is repeated during runtime, so if a column
        # is missing then it will raise an error. We could change this if we wanted.
        targeted_data = self._validate_targeted_data(
            {target: data_frame for target, data_frame in target_to_data_frame.items() if target in self.targets},
            eagerly_raise_column_not_found_error=True,
        )

        if (column_type := self._validate_column_type(targeted_data)) != self._column_type:
            raise ValueError(
                f"{self._single_filter_column} has changed type from {self._column_type} to {column_type}. "
                "A filtered column cannot change type while the dashboard is running."
            )

        # Cast is justified as the selector is set in pre_build and is not None.
        selector = cast(SelectorType, self.selector)

        if _is_categorical_selector(selector):
            selector_call_obj = selector(options=self._get_options(targeted_data, current_value))
        elif _is_numerical_temporal_selector(selector):
            _min, _max = self._get_min_max(targeted_data, current_value)
            selector_call_obj = selector(min=_min, max=_max)
        else:
            # Hierarchical filters cannot yet be dynamic.
            selector_call_obj = selector.build()

        # The filter is dynamic, so a guard component (data=True) needs to be added to prevent unexpected action firing.
        selector_call_obj = html.Div(
            children=[
                selector_call_obj,
                dcc.Store(id=f"{selector.id}_guard_actions_chain", data=True),
            ]
        )

        return selector_call_obj

    @_log_call
    def pre_build(self):  # noqa: PLR0912
        # TODO NOW PP: Refactor this
        # Extract filter.targets that are not figure models.
        targeted_controls = []
        for target in list(self.targets):
            if target in model_manager and not hasattr(model_manager[target], "figure"):
                self.targets.remove(target)
                targeted_controls.append(target)

        # If page filter validate that targets present on the page where the filter is defined.
        # If container filter validate that targets present in the container where the filter is defined.
        # Validation has to be triggered in pre_build because all targets are not initialized until then.
        check_control_targets(control=self)

        # If targets aren't explicitly provided then try to target all figures on the page. In this case we don't
        # want to raise an error if the column is not found in a figure's data_frame, it will just be ignored.
        # This is the case when bool(self.targets) is False.
        # If filter used within container and if targets aren't explicitly provided it will target all figures within
        # that container. Possibly in future this will change (which would be breaking change).
        proposed_targets = self.targets or [
            model.id
            for model in cast(
                Iterable[FigureType], model_manager._get_models(FIGURE_MODELS, get_control_parent(control=self))
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
            (cast(FigureType, model_manager[target])["data_frame"], {})
            for target in proposed_targets
            if hasattr(model_manager[target], "figure")
        ]

        target_to_data_frame = dict(zip(proposed_targets, data_manager._multi_load(multi_data_source_name_load_kwargs)))
        targeted_data = self._validate_targeted_data(
            target_to_data_frame, eagerly_raise_column_not_found_error=bool(self.targets)
        )
        self.targets = list(targeted_data.columns)

        # Set default selector according to column type and whether it's a hierarchical filter.
        self._column_type = self._validate_column_type(targeted_data)
        is_hierarchical_column = isinstance(self.column, list)
        selector_kind: Literal["hierarchical", "numerical", "categorical", "temporal", "boolean"] = (
            "hierarchical" if is_hierarchical_column else self._column_type
        )
        self.selector = self.selector or DEFAULT_SELECTORS[selector_kind]()
        self.selector.title = self.selector.title or self._single_filter_column.title()

        if isinstance(self.selector, DISALLOWED_SELECTORS[selector_kind]):
            raise ValueError(
                f"Chosen selector {type(self.selector).__name__} is not compatible with {selector_kind} column "
                f"'{self._single_filter_column}'."
            )

        # Check if the filter is dynamic. Dynamic filter means that the filter is updated when the page is refreshed
        # which causes "options" for categorical or "min" and "max" for numerical/temporal selectors to be updated.
        # The filter is dynamic if mentioned attributes ("options"/"min"/"max") are not explicitly provided and
        # filter targets at least one figure that uses dynamic data source. Note that min or max = 0 are Falsey values
        # but should still count as manually set. Hierarchical and boolean filters are always static.
        if (
            not _is_hierarchical_selector(self.selector)
            and not _is_boolean_selector(self.selector)
            and not getattr(self.selector, "options", [])
            and getattr(self.selector, "min", None) is None
            and getattr(self.selector, "max", None) is None
        ):
            for target_id in self.targets:
                data_source_name = cast(FigureType, model_manager[target_id])["data_frame"]
                if isinstance(data_manager[data_source_name], _DynamicData):
                    self._dynamic = True
                    self.selector._dynamic = True
                    break

        if _is_numerical_temporal_selector(self.selector):
            _min, _max = self._get_min_max(targeted_data)
            # Note that manually set self.selector.min/max = 0 are Falsey and should not be overwritten.
            if self.selector.min is None:
                self.selector.min = _min
            if self.selector.max is None:
                self.selector.max = _max
        elif _is_categorical_selector(self.selector):
            self.selector.options = self.selector.options or self._get_options(targeted_data)
        elif _is_hierarchical_selector(self.selector):
            if not self.selector.options and any(
                isinstance(data_manager[cast(FigureType, model_manager[target])["data_frame"]], _DynamicData)
                for target in self.targets
            ):
                raise ValueError(
                    "Hierarchical filters cannot derive Cascader options from dynamic data. "
                    "Set explicit `selector=vm.Cascader(options=...)` or use a static `data_frame`. "
                )
            self.selector.options = self.selector.options or self._get_hierarchical_options(target_to_data_frame)

        # Set default value for the selector if not explicitly provided.
        self.selector.value = get_selector_default_value(self.selector)

        # Set the filter function according to the selector type.
        if isinstance(self.selector, RangeSlider) or (isinstance(self.selector, DatePicker) and self.selector.range):
            self._filter_function = _filter_between
        else:
            self._filter_function = _filter_isin

        # TODO AM-PP: If [] or None is set make that the actions are not overwritten. Could be tricky, but doable.
        if not self.selector.actions:
            update_figures_action = update_figures(id=f"{FILTER_ACTION_PREFIX}_{self.id}", targets=self.targets)
            set_control_actions = []
            for control_id in targeted_controls:
                set_control_actions.append(set_control(control=control_id, value=None))

            # Post assignment to trigger the _make_actions_chain pydantic validator.
            self.selector.actions = [update_figures_action, *set_control_actions]
            for set_control_action in set_control_actions:
                set_control_action.pre_build()

        # A set of properties unique to selector (inner object) that are not present in html.Div (outer build wrapper).
        # Creates _action_outputs and _action_inputs for forwarding properties to the underlying selector.
        # Example: "filter-id.options" is forwarded to "checklist.options".
        if selector_inner_component_properties := getattr(self.selector, "_inner_component_properties", None):
            self._selector_properties = set(selector_inner_component_properties) - set(html.Div().available_properties)

    @_log_call
    def build(self):
        # Cast is justified as the selector is set in pre_build and is not None.
        selector = cast(SelectorType, self.selector)

        # Wrap the selector in a Div so that the "guard" component can be added.
        selector_build_obj = html.Div(children=[selector.build()])

        # Add the guard component and set it to False. Let clientside callbacks to update it to True when needed.
        # For example when the filter value comes from the URL or when reset button is clicked.
        selector_build_obj.children.append(dcc.Store(id=f"{selector.id}_guard_actions_chain", data=False))

        if not self._dynamic:
            return html.Div(id=self.id, children=selector_build_obj, hidden=not self.visible)

        # Temporarily hide the selector during the filter reloading process. Other components, such as the title,
        # remain visible because of the configuration: overlay_style={"visibility": "visible"} in dcc.Loading.
        # If the selector is a Checklist with show_select_all=True, then hide the select all checkbox too.
        selector_build_obj[selector.id].className = "invisible"
        if isinstance(selector, Checklist) and selector.show_select_all:
            selector_build_obj[f"{selector.id}_select_all"].className = "invisible"

        # TODO: Align the (dynamic) object's return structure with the figure's components when the Dash bug is fixed.
        #  This means returning an empty "html.Div(id=self.id, className=...)" as a placeholder from Filter.build().
        #  Also, make selector.title visible when the filter is reloading.
        return dcc.Loading(
            id=self.id,
            children=selector_build_obj,
            color="grey",
            overlay_style={"visibility": "visible"},
            className="d-none" if not self.visible else "",
        )

    def _validate_targeted_data(
        self, target_to_data_frame: dict[ModelID, pd.DataFrame], eagerly_raise_column_not_found_error
    ) -> pd.DataFrame:
        target_to_series = {}

        # One code path for flat and hierarchical filters: `path_or_leaf` is always a list (a single name when
        # `column` is a str, or the ordered path when `column` is a list). We require every path name on the dataframe,
        # then take the leaf column `path_or_leaf[-1]` for the series used downstream.
        path_or_leaf = [self.column] if isinstance(self.column, str) else self.column
        leaf = path_or_leaf[-1]
        for target, data_frame in target_to_data_frame.items():
            missing = [c for c in path_or_leaf if c not in data_frame.columns]
            if not missing:
                # reset_index so that when we make a DataFrame out of all these pd.Series pandas doesn't try to align
                # the columns by index.
                target_to_series[target] = data_frame[leaf].reset_index(drop=True)
            elif eagerly_raise_column_not_found_error:
                if len(path_or_leaf) == 1:
                    raise ValueError(f"Selected column {path_or_leaf[0]} not found in dataframe for {target}.")
                raise ValueError(f"Selected column(s) {missing} not found in dataframe for {target}.")

        targeted_data = pd.DataFrame(target_to_series)
        if targeted_data.columns.empty:
            # Still raised when eagerly_raise_column_not_found_error=False.
            raise ValueError(
                f"Selected column {self._single_filter_column} not found in any dataframe for "
                f"{', '.join(target_to_data_frame.keys())}."
            )
        # TODO: Enable empty data_frame handling
        if targeted_data.empty:
            raise ValueError(
                f"Selected column {self._single_filter_column} does not contain anything in any dataframe for "
                f"{', '.join(target_to_data_frame.keys())}."
            )

        return targeted_data

    def _validate_column_type(
        self, targeted_data: pd.DataFrame
    ) -> Literal["numerical", "categorical", "temporal", "boolean"]:
        is_boolean = targeted_data.apply(is_bool_dtype)
        is_numerical = targeted_data.apply(is_numeric_dtype)
        is_temporal = targeted_data.apply(is_datetime64_any_dtype)
        is_categorical = ~(is_boolean | is_numerical | is_temporal)

        if is_boolean.all():
            return "boolean"
        elif is_numerical.all():
            return "numerical"
        elif is_temporal.all():
            return "temporal"
        elif is_categorical.all():
            return "categorical"
        else:
            raise ValueError(
                f"Inconsistent types detected in column {self._single_filter_column}. "
                "This column must have the same type for all targets."
            )

    @staticmethod
    def _get_min_max(
        targeted_data: pd.DataFrame,
        current_value: SingleValueType | MultiValueType | None = None,
    ) -> tuple[float, float] | tuple[pd.Timestamp, pd.Timestamp]:
        # Try to convert the current value to a datetime object. If it fails (like value=123), it will be left as is.
        # By default, DatePicker produces inputs in the following format: "YYYY-MM-DD".
        # "ISO8601" is used to enable the conversion process for custom DatePicker components and custom formats.
        if targeted_data.apply(is_datetime64_any_dtype).all():
            with suppress(ValueError):
                current_value = pd.to_datetime(current_value, format="ISO8601")

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
    def _get_options(
        targeted_data: pd.DataFrame,
        current_value: SingleValueType | MultiValueType | None = None,
    ) -> list[Any]:
        # Try to convert the current value to a datetime object. If it fails (like value=123), it will be left as is.
        # By default, DatePicker produces inputs in the following format: "YYYY-MM-DD".
        # "ISO8601" is used to enable the conversion process for custom DatePicker components and custom formats.
        if targeted_data.apply(is_datetime64_any_dtype).all():
            with suppress(ValueError):
                current_value = pd.to_datetime(current_value, format="ISO8601")

        # The dropna() isn't strictly required here but will be in future pandas versions when the behavior of stack
        # changes. See https://pandas.pydata.org/docs/whatsnew/v2.1.0.html#whatsnew-210-enhancements-new-stack.
        targeted_data = pd.concat([targeted_data, pd.Series(current_value)]).stack().dropna()  # noqa: PD013
        return sorted(set(targeted_data))

    def _get_hierarchical_options(self, target_to_data_frame: dict[ModelID, pd.DataFrame]) -> dict[str, Any]:
        """Build Cascader options from path columns; needs full dataframes (not the leaf-only `targeted_data`)."""
        path_cols = list(cast(list[str], self.column))
        combined = pd.concat(
            [target_to_data_frame[target_id][path_cols] for target_id in self.targets],
            ignore_index=True,
        ).drop_duplicates()
        return _dataframe_path_to_cascader_options(combined, path_cols)
