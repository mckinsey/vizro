from datetime import date, datetime
from typing import Literal

import dash_bootstrap_components as dbc
import pandas as pd
import pytest
from asserts import assert_component_equal
from dash import dcc, html
from pydantic import ValidationError

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions._filter_action import _filter
from vizro.managers import data_manager, model_manager
from vizro.models._components.form import Cascader
from vizro.models._controls._controls_utils import get_selector_default_value
from vizro.models._controls.filter import Filter, _filter_between, _filter_isin


@pytest.fixture
def managers_column_different_type():
    """Instantiates the managers with a page and two graphs sharing the same column but of different data types."""
    df_numerical = pd.DataFrame({"shared_column": [1]})
    df_temporal = pd.DataFrame({"shared_column": [datetime(2024, 1, 1)]})
    df_categorical = pd.DataFrame({"shared_column": ["a"]})
    df_boolean = pd.DataFrame({"shared_column": [False]})

    vm.Page(
        id="test_page",
        title="Page Title",
        components=[
            vm.Graph(id="column_numerical", figure=px.scatter(df_numerical)),
            vm.Graph(id="column_temporal", figure=px.scatter(df_temporal)),
            vm.Graph(id="column_categorical", figure=px.scatter(df_categorical)),
            vm.Graph(id="column_boolean", figure=px.scatter(df_boolean)),
        ],
    )
    Vizro._pre_build()


@pytest.fixture
def managers_column_only_exists_in_some():
    """Dataframes with column_numerical and column_categorical, which can be different lengths."""
    vm.Page(
        id="test_page",
        title="Page Title",
        components=[
            vm.Graph(id="column_numerical_exists_1", figure=px.scatter(pd.DataFrame({"column_numerical": [1]}))),
            vm.Graph(id="column_numerical_exists_2", figure=px.scatter(pd.DataFrame({"column_numerical": [1, 2]}))),
            vm.Graph(id="column_numerical_exists_empty", figure=px.scatter(pd.DataFrame({"column_numerical": []}))),
            vm.Graph(id="column_categorical_exists_1", figure=px.scatter(pd.DataFrame({"column_categorical": ["a"]}))),
            vm.Graph(
                id="column_categorical_exists_2", figure=px.scatter(pd.DataFrame({"column_categorical": ["a", "b"]}))
            ),
            vm.Graph(
                id="column_temporal_exists_1",
                figure=px.scatter(pd.DataFrame({"column_temporal": [datetime(2024, 1, 1)]})),
            ),
            vm.Graph(
                id="column_temporal_exists_2",
                figure=px.scatter(pd.DataFrame({"column_temporal": [datetime(2024, 1, 1), datetime(2024, 1, 2)]})),
            ),
            vm.Graph(id="column_boolean_exists_1", figure=px.scatter(pd.DataFrame({"column_boolean": [True]}))),
            vm.Graph(id="column_boolean_exists_2", figure=px.scatter(pd.DataFrame({"column_boolean": [True, False]}))),
        ],
    )
    Vizro._pre_build()


@pytest.fixture
def target_to_data_frame():
    return {
        "column_numerical_exists_1": pd.DataFrame(
            {
                "column_numerical": [1, 2],
            }
        ),
        "column_numerical_exists_2": pd.DataFrame(
            {
                "column_numerical": [2, 3],
            }
        ),
        "column_categorical_exists_1": pd.DataFrame(
            {
                "column_categorical": ["a", "b"],
            }
        ),
        "column_categorical_exists_2": pd.DataFrame(
            {
                "column_categorical": ["b", "c"],
            }
        ),
        "column_temporal_exists_1": pd.DataFrame(
            {
                "column_temporal": [datetime(2024, 1, 1), datetime(2024, 1, 2)],
            }
        ),
        "column_temporal_exists_2": pd.DataFrame(
            {
                "column_temporal": [datetime(2024, 1, 2), datetime(2024, 1, 3)],
            }
        ),
        "column_boolean_exists_1": pd.DataFrame(
            {
                "column_boolean": [True, False],
            }
        ),
        "column_boolean_exists_2": pd.DataFrame(
            {
                "column_boolean": [False, True],
            }
        ),
    }


class TestFilterFunctions:
    @pytest.mark.parametrize(
        "data, value, expected",
        [
            ([1, 2, 3, 4, 5], [2.5, 3.5], [False, False, True, False, False]),  # Standard test
            ([1, 2, 3, 4, 5], [2, 4], [False, True, True, True, False]),  # Test for inclusive both ends
            ([1, 2, 3, 4, 5], [1, 5], [True, True, True, True, True]),  # Test for inclusive all
            ([1, 2, 3, 4, 5], [4, 2], [False, False, False, False, False]),  # Test for inverted values
            ([], [2, 4], pd.Series([], dtype=bool)),  # Test for empty series
            ([1.1, 2.2, 3.3, 4.4, 5.5], [2.1, 4.5], [False, True, True, True, False]),  # Test with float data
        ],
    )
    def test_filter_between(self, data, value, expected):
        series = pd.Series(data)
        expected = pd.Series(expected)
        result = _filter_between(series, value)
        pd.testing.assert_series_equal(result, expected)

    @pytest.mark.parametrize(
        "data, value, expected",
        [
            (
                [
                    datetime(2024, 1, 1),
                    datetime(2024, 2, 1),
                    datetime(2024, 3, 1),
                    datetime(2024, 4, 1),
                    datetime(2024, 5, 1),
                ],
                ["2024-02-01", "2024-03-01"],
                [False, True, True, False, False],
            ),  # Standard test
            (
                [
                    datetime(2024, 1, 1),
                    datetime(2024, 2, 1),
                    datetime(2024, 3, 1),
                    datetime(2024, 4, 1),
                    datetime(2024, 5, 1),
                ],
                ["2024-01-01", "2024-05-01"],
                [True, True, True, True, True],
            ),  # Test with dates for inclusive both ends
            (
                [
                    datetime(2024, 1, 1),
                    datetime(2024, 2, 1),
                    datetime(2024, 3, 1),
                    datetime(2024, 4, 1),
                    datetime(2024, 5, 1),
                ],
                ["2024-06-01", "2024-07-01"],
                [False, False, False, False, False],
            ),  # Test with no result
            (
                [
                    datetime(2024, 1, 1),
                    datetime(2024, 2, 1),
                    datetime(2024, 3, 1),
                    datetime(2024, 4, 1),
                    datetime(2024, 5, 1),
                ],
                ["2024-03-01", "2024-02-01"],
                [False, False, False, False, False],
            ),  # Test for inverted values
            ([], ["2024-02-01", "2024-03-01"], pd.Series([], dtype=bool)),  # Test for empty series
            (
                [
                    datetime(2024, 1, 1, 20, 20, 20),
                    datetime(2024, 2, 1, 20, 20, 20),
                    datetime(2024, 3, 1, 20, 20, 20),
                    datetime(2024, 4, 1, 20, 20, 20),
                    datetime(2024, 5, 1, 20, 20, 20),
                ],
                ["2024-02-01", "2024-03-01"],
                [False, True, True, False, False],
            ),  # Test with time part in the date
        ],
    )
    def test_filter_between_date(self, data, value, expected):
        series = pd.Series(data)
        expected = pd.Series(expected)
        result = _filter_between(series, value)
        pd.testing.assert_series_equal(result, expected)

    @pytest.mark.parametrize(
        "data, value, expected",
        [
            ([1, 2, 3, 4, 5], [2, 4], [False, True, False, True, False]),  # Test for integers
            (["apple", "banana", "orange"], ["banana", "grape"], [False, True, False]),  # Test for strings
            ([1.1, 2.2, 3.3, 4.4, 5.5], [2.2, 4.4], [False, True, False, True, False]),  # Test for float values
            ([1, 2, 3, 4, 5], [], [False, False, False, False, False]),  # Test for empty value list
            ([True, False, True, False], [True], [True, False, True, False]),  # Test for boolean True/False values
            ([True, False, True, False], [False], [False, True, False, True]),  # Test for boolean True/False values
            ([True, False, True, False], [True, False], [True, True, True, True]),  # Test for boolean both values
            ([True, False, True, False], [], [False, False, False, False]),  # Test for boolean empty value list
            ([1, 0, 1, 0], [1], [True, False, True, False]),  # Test for boolean 0/1 values
            ([1, 0, 1, 0], [0], [False, True, False, True]),  # Test for boolean 0/1 values
            ([1, 0, 1, 0], [1, 0], [True, True, True, True]),  # Test for boolean 0/1 both values
            ([1, 0, 1, 0], [], [False, False, False, False]),  # Test for boolean 0/1 empty value list
            # Test pandas automatic boolean/numeric conversion (crucial for Switch with 0/1 columns)
            ([0, 1, 0, 1], [False], [True, False, True, False]),  # 0/1 data filtered with False
            ([0, 1, 0, 1], [True], [False, True, False, True]),  # 0/1 data filtered with True
            ([False, True, False, True], [0], [True, False, True, False]),  # True/False data filtered with 0
            ([False, True, False, True], [1], [False, True, False, True]),  # True/False data filtered with 1
        ],
    )
    def test_filter_isin(self, data, value, expected):
        series = pd.Series(data)
        expected = pd.Series(expected)
        result = _filter_isin(series, value)
        pd.testing.assert_series_equal(result, expected)

    @pytest.mark.parametrize(
        "data, value, expected",
        [
            (
                [
                    datetime(2024, 1, 1),
                    datetime(2024, 2, 1),
                    datetime(2024, 3, 1),
                    datetime(2024, 4, 1),
                    datetime(2024, 5, 1),
                ],
                ["2024-02-01"],
                [False, True, False, False, False],
            ),  # Standard test
            (
                [
                    datetime(2024, 1, 1),
                    datetime(2024, 2, 1),
                    datetime(2024, 3, 1),
                    datetime(2024, 2, 1),
                    datetime(2024, 2, 1),
                ],
                ["2024-02-01"],
                [False, True, False, True, True],
            ),  # Multiple values
            (
                [
                    datetime(2024, 1, 1),
                    datetime(2024, 2, 1),
                    datetime(2024, 3, 1),
                    datetime(2024, 4, 1),
                    datetime(2024, 5, 1),
                ],
                ["2024-06-01"],
                [False, False, False, False, False],
            ),  # Test with no result
            (
                [
                    datetime(2024, 1, 1),
                    datetime(2024, 2, 1),
                    datetime(2024, 3, 1),
                    datetime(2024, 4, 1),
                    datetime(2024, 5, 1),
                ],
                [],
                [False, False, False, False, False],
            ),  # Test for empty value list
            (
                [
                    datetime(2024, 1, 1, 20, 20, 20),
                    datetime(2024, 2, 1, 20, 20, 20),
                    datetime(2024, 3, 1, 20, 20, 20),
                    datetime(2024, 4, 1, 20, 20, 20),
                    datetime(2024, 5, 1, 20, 20, 20),
                ],
                ["2024-02-01"],
                [False, True, False, False, False],
            ),  # Test with time part in the date
        ],
    )
    def test_filter_isin_date(self, data, value, expected):
        series = pd.Series(data)
        expected = pd.Series(expected)
        result = _filter_isin(series, value)
        pd.testing.assert_series_equal(result, expected)


class TestFilterStaticMethods:
    """Tests static methods of the Filter class."""

    @pytest.mark.parametrize(
        "data_columns, expected",
        [
            ([[]], []),
            ([["A", "B", "A"]], ["A", "B"]),
            ([[1, 2, 1]], [1, 2]),
            ([[1990, 2025, 1990]], [1990, 2025]),
            ([[1.1, 2.2, 1.1]], [1.1, 2.2]),
            (
                [
                    [
                        datetime(2024, 1, 1),
                        datetime(2024, 1, 2),
                        datetime(2024, 1, 1),
                    ]
                ],
                [
                    datetime(2024, 1, 1),
                    datetime(2024, 1, 2),
                ],
            ),
            ([[], []], []),
            ([["A"], []], ["A"]),
            ([[], ["A"]], ["A"]),
            ([["A"], ["B"]], ["A", "B"]),
            ([["A", "B"], ["B", "C"]], ["A", "B", "C"]),
        ],
    )
    def test_get_options(self, data_columns, expected):
        """Check that the options are correctly set.

        Does not apply to boolean selectors as the options are always set to True/False.
        """
        targeted_data = pd.DataFrame({f"target_{i}": pd.Series(data) for i, data in enumerate(data_columns)})
        result = Filter._get_options(targeted_data)
        assert result == expected

    @pytest.mark.parametrize(
        "data_columns, current_value, expected",
        [
            ([[]], None, []),
            ([[]], "A", ["A"]),
            ([[]], ["A", "B"], ["A", "B"]),
            ([["A"]], "B", ["A", "B"]),
            ([["A"]], ["B", "C"], ["A", "B", "C"]),
            ([[1]], 2, [1, 2]),
            ([[1]], [2, 3], [1, 2, 3]),
            ([[1990]], 2025, [1990, 2025]),
            ([[1990]], [2015, 2025], [1990, 2015, 2025]),
            ([[1.1]], 2.2, [1.1, 2.2]),
            ([[1.1]], [2.2, 3.3], [1.1, 2.2, 3.3]),
            (
                [
                    [
                        datetime(2024, 1, 1),
                    ]
                ],
                "2024-01-02",
                [
                    datetime(2024, 1, 1),
                    datetime(2024, 1, 2),
                ],
            ),
            (
                [
                    [
                        datetime(2024, 1, 1),
                    ]
                ],
                [
                    "2024-01-02",
                    "2024-01-03",
                ],
                [
                    datetime(2024, 1, 1),
                    datetime(2024, 1, 2),
                    datetime(2024, 1, 3),
                ],
            ),
        ],
    )
    def test_get_options_with_current_value(self, data_columns, current_value, expected):
        """Check that the options are correctly set with current value.

        Does not apply to boolean selectors as the options are always set to True/False.
        """
        targeted_data = pd.DataFrame({f"target_{i}": pd.Series(data) for i, data in enumerate(data_columns)})
        result = Filter._get_options(targeted_data, current_value)
        assert result == expected

    @pytest.mark.parametrize(
        "data_columns, expected",
        [
            ([[1, 2, 1]], (1, 2)),
            ([[1990, 2025, 1990]], (1990, 2025)),
            ([[1.1, 2.2, 1.1]], (1.1, 2.2)),
            (
                [
                    [
                        datetime(2024, 1, 1),
                        datetime(2024, 1, 2),
                        datetime(2024, 1, 1),
                    ]
                ],
                (
                    datetime(2024, 1, 1),
                    datetime(2024, 1, 2),
                ),
            ),
            ([[1], []], (1, 1)),
            ([[1, 2], []], (1, 2)),
            ([[1, 2], [2, 3]], (1, 3)),
        ],
    )
    def test_get_min_max(self, data_columns, expected):
        targeted_data = pd.DataFrame({f"target_{i}": pd.Series(data) for i, data in enumerate(data_columns)})
        result = Filter._get_min_max(targeted_data)
        assert result == expected

    @pytest.mark.parametrize(
        "data_columns, current_value, expected",
        [
            ([[1, 2]], 3, (1, 3)),
            ([[1, 2]], [3, 4], (1, 4)),
            ([[1990]], 2025, (1990, 2025)),
            ([[1990]], [2015, 2025], (1990, 2025)),
            ([[1.1, 2.2]], 3.3, (1.1, 3.3)),
            ([[1.1, 2.2]], [3.3, 4.4], (1.1, 4.4)),
            (
                [
                    [
                        datetime(2024, 1, 1),
                        datetime(2024, 1, 2),
                    ]
                ],
                "2024-01-03",
                (
                    datetime(2024, 1, 1),
                    datetime(2024, 1, 3),
                ),
            ),
            (
                [
                    [
                        datetime(2024, 1, 1),
                        datetime(2024, 1, 2),
                    ]
                ],
                [
                    "2024-01-03",
                    "2024-01-04",
                ],
                (
                    datetime(2024, 1, 1),
                    datetime(2024, 1, 4),
                ),
            ),
            ([[1], []], 2, (1, 2)),
            ([[1], []], [2, 3], (1, 3)),
            ([[1], [2]], 3, (1, 3)),
            ([[1], [2]], [3, 4], (1, 4)),
        ],
    )
    def test_get_min_max_with_current_value(self, data_columns, current_value, expected):
        targeted_data = pd.DataFrame({f"target_{i}": pd.Series(data) for i, data in enumerate(data_columns)})
        result = Filter._get_min_max(targeted_data, current_value)
        assert result == expected


class TestFilterInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_create_filter_mandatory_only(self):
        filter = Filter(column="foo")
        assert filter.type == "filter"
        assert filter.column == "foo"
        assert filter.targets == []

    def test_create_filter_mandatory_and_optional(self):
        filter = Filter(
            id="filter_id",
            column="foo",
            targets=["scatter_chart", "bar_chart"],
            selector=vm.RadioItems(
                id="selector_id",
                title="Test Title",
                description=vm.Tooltip(id="tooltip-id", text="Test description", icon="info"),
            ),
            show_in_url=True,
        )

        assert filter.id == "filter_id"
        assert filter.type == "filter"
        assert filter.column == "foo"
        assert filter.targets == ["scatter_chart", "bar_chart"]
        assert isinstance(filter.selector, vm.RadioItems)
        assert filter.show_in_url is True
        assert isinstance(filter.selector.description, vm.Tooltip)
        assert filter._action_triggers == {"__default__": "selector_id.value"}
        assert filter._action_outputs == {
            "__default__": "selector_id.value",
            "selector": "filter_id.children",
            "title": "selector_id_title.children",
            "description": "tooltip-id-text.children",
        }
        assert filter._action_inputs == {"__default__": "selector_id.value"}

    def test_missing_id_for_url_control_warning_raised(self):
        with pytest.warns(
            UserWarning,
            match="`show_in_url=True` is set but no `id` was provided. "
            "Shareable URLs might be unreliable if your dashboard configuration changes in future. "
            "If you want to ensure that links continue working, set a fixed `id`.",
        ):
            Filter(column="column_numerical", show_in_url=True)


@pytest.mark.usefixtures("managers_column_only_exists_in_some")
class TestFilterCall:
    """Test Filter.__call__() method with target_to_data_frame and current_value inputs.

    Boolean selectors don't have dynamic behavior like other selectors, as their options are always set to True/False.
    """

    def test_filter_call_categorical_selector_valid(self, target_to_data_frame):
        filter = vm.Filter(
            column="column_categorical",
            targets=["column_categorical_exists_1", "column_categorical_exists_2"],
            selector=vm.Checklist(id="test_selector_id"),
        )
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        selector_build = filter(target_to_data_frame=target_to_data_frame, current_value=["c", "d"])["test_selector_id"]
        assert selector_build.options == [
            {"label": "a", "value": "a"},
            {"label": "b", "value": "b"},
            {"label": "c", "value": "c"},
            {"label": "d", "value": "d"},
        ]

    def test_filter_call_numerical_selector_valid(self, target_to_data_frame):
        filter = vm.Filter(
            column="column_numerical",
            targets=["column_numerical_exists_1", "column_numerical_exists_2"],
            selector=vm.RangeSlider(id="test_selector_id"),
        )
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        selector_build = filter(target_to_data_frame=target_to_data_frame, current_value=[3, 4])["test_selector_id"]
        assert selector_build.min == 1
        assert selector_build.max == 4

    def test_filter_call_temporal_selector_valid(self, target_to_data_frame):
        filter = vm.Filter(
            column="column_temporal",
            targets=["column_temporal_exists_1", "column_temporal_exists_2"],
            selector=vm.DatePicker(id="test_selector_id"),
        )
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        selector_build = filter(target_to_data_frame=target_to_data_frame, current_value=["2024-01-03", "2024-01-04"])[
            "test_selector_id"
        ]
        assert selector_build.minDate == datetime(2024, 1, 1)
        assert selector_build.maxDate == datetime(2024, 1, 4)

    def test_dynamic_filter_call_guard_component_is_true(self, target_to_data_frame):
        filter = vm.Filter(
            column="column_categorical",
            targets=["column_categorical_exists_1", "column_categorical_exists_2"],
            selector=vm.Dropdown(id="test_selector_id"),
        )
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        filter_call_obj = filter(target_to_data_frame=target_to_data_frame, current_value=["c", "d"])

        result_guard_component = filter_call_obj["test_selector_id_guard_actions_chain"]
        expected_guard_component = dcc.Store(id="test_selector_id_guard_actions_chain", data=True)

        assert_component_equal(result_guard_component, expected_guard_component)

    def test_filter_call_column_is_changed(self, target_to_data_frame):
        filter = vm.Filter(
            column="column_categorical", targets=["column_categorical_exists_1", "column_categorical_exists_2"]
        )
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        filter._column_type = "numerical"

        with pytest.raises(
            ValueError,
            match=r"column_categorical has changed type from numerical to categorical. "
            r"A filtered column cannot change type while the dashboard is running.",
        ):
            filter(target_to_data_frame=target_to_data_frame, current_value=["a", "b"])

    def test_filter_call_selected_column_not_found_in_target(self):
        filter = vm.Filter(column="column_categorical", targets=["column_categorical_exists_1"])
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        with pytest.raises(
            ValueError,
            match=r"Selected column column_categorical not found in dataframe for column_categorical_exists_1.",
        ):
            filter(target_to_data_frame={"column_categorical_exists_1": pd.DataFrame()}, current_value=["a", "b"])

    def test_filter_call_targeted_data_empty(self):
        filter = vm.Filter(column="column_categorical", targets=["column_categorical_exists_1"])
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        with pytest.raises(
            ValueError,
            match=r"Selected column column_categorical does not contain anything in any dataframe "
            r"for column_categorical_exists_1.",
        ):
            filter(
                target_to_data_frame={"column_categorical_exists_1": pd.DataFrame({"column_categorical": []})},
                current_value=["a", "b"],
            )


class TestFilterPreBuildMethod:
    def test_filter_not_in_page(self):
        with pytest.raises(
            ValueError, match=r"Control filter_id should be defined within Page.controls or Container.controls."
        ):
            vm.Filter(id="filter_id", column="column_numerical").pre_build()

    def test_targets_default_valid(self, managers_column_only_exists_in_some):
        # Core of tests is still interface level
        filter = vm.Filter(column="column_numerical")
        # Special case - need filter in the context of page in order to run filter.pre_build
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.targets == [
            "column_numerical_exists_1",
            "column_numerical_exists_2",
            "column_numerical_exists_empty",
        ]

    def test_targets_wrapped_filter_valid(self, managers_column_only_exists_in_some, MockControlWrapper):
        filter = vm.Filter(column="column_numerical")
        model_manager["test_page"].controls = [MockControlWrapper(control=filter)]
        filter.pre_build()

        assert filter.targets == [
            "column_numerical_exists_1",
            "column_numerical_exists_2",
            "column_numerical_exists_empty",
        ]

    def test_targets_specific_valid(self, managers_column_only_exists_in_some):
        filter = vm.Filter(column="column_numerical", targets=["column_numerical_exists_1"])
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.targets == ["column_numerical_exists_1"]

    def test_targets_specific_present_invalid(self, managers_column_only_exists_in_some):
        filter = vm.Filter(column="column_numerical", targets=["invalid_target"])
        model_manager["test_page"].controls = [filter]

        with pytest.raises(ValueError, match=r"Target invalid_target not found within the test_page."):
            filter.pre_build()

    def test_targets_default_invalid(self, managers_column_only_exists_in_some):
        filter = vm.Filter(column="invalid_choice")
        model_manager["test_page"].controls = [filter]

        with pytest.raises(
            ValueError,
            match=r"Selected column invalid_choice not found in any dataframe for column_numerical_exists_1, "
            "column_numerical_exists_2, column_numerical_exists_empty, column_categorical_exists_1, "
            r"column_categorical_exists_2.",
        ):
            filter.pre_build()

    def test_targets_specific_invalid(self, managers_column_only_exists_in_some):
        filter = vm.Filter(column="column_numerical", targets=["column_categorical_exists_1"])
        model_manager["test_page"].controls = [filter]

        with pytest.raises(
            ValueError,
            match=r"Selected column column_numerical not found in dataframe for column_categorical_exists_1.",
        ):
            filter.pre_build()

    def test_targets_empty(self, managers_column_only_exists_in_some):
        filter = vm.Filter(column="column_numerical", targets=["column_numerical_exists_empty"])
        model_manager["test_page"].controls = [filter]

        with pytest.raises(
            ValueError,
            match=r"Selected column column_numerical does not contain anything in any dataframe for "
            r"column_numerical_exists_empty.",
        ):
            filter.pre_build()

    @pytest.mark.parametrize(
        "filtered_column, expected_column_type",
        [("country", "categorical"), ("year", "temporal"), ("lifeExp", "numerical"), ("is_europe", "boolean")],
    )
    def test_column_type(self, filtered_column, expected_column_type, managers_one_page_two_graphs):
        filter = vm.Filter(column=filtered_column)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter._column_type == expected_column_type

    @pytest.mark.parametrize(
        "filtered_column, expected_selector",
        [("country", vm.Dropdown), ("year", vm.DatePicker), ("lifeExp", vm.RangeSlider), ("is_europe", vm.Switch)],
    )
    def test_selector_default_selector(self, filtered_column, expected_selector, managers_one_page_two_graphs):
        filter = vm.Filter(column=filtered_column)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert isinstance(filter.selector, expected_selector)
        assert filter.selector.title == filtered_column.title()

    @pytest.mark.parametrize("filtered_column", ["country", "year", "lifeExp"])
    def test_selector_specific_selector(self, filtered_column, managers_one_page_two_graphs):
        filter = vm.Filter(column=filtered_column, selector=vm.RadioItems(title="Title"))
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert isinstance(filter.selector, vm.RadioItems)
        assert filter.selector.title == "Title"

    @pytest.mark.parametrize(
        "filtered_column, selector",
        [
            ("country", vm.Dropdown),
            ("country", vm.RadioItems),
            ("country", vm.Checklist),
            ("lifeExp", vm.Slider),
            ("lifeExp", vm.RangeSlider),
            ("lifeExp", vm.Dropdown),
            ("lifeExp", vm.RadioItems),
            ("lifeExp", vm.Checklist),
            ("year", vm.Dropdown),
            ("year", vm.RadioItems),
            ("year", vm.Checklist),
            ("year", vm.DatePicker),
            ("is_europe", vm.Switch),
            ("is_europe", vm.Dropdown),
            ("is_europe", vm.RadioItems),
            ("is_europe", vm.Checklist),
            # Covers numerical columns with 0/1 data. See detailed comment in filter.py
            # on disallowing boolean selectors for numerical columns.
            ("lifeExp", vm.Switch),
        ],
    )
    def test_allowed_selectors_per_column_type(self, filtered_column, selector, managers_one_page_two_graphs):
        filter = vm.Filter(column=filtered_column, selector=selector())
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert isinstance(filter.selector, selector)

    @pytest.mark.parametrize(
        "filtered_column, selector, selector_name, column_type",
        [
            ("country", vm.Slider, "Slider", "categorical"),
            ("country", vm.RangeSlider, "RangeSlider", "categorical"),
            ("country", vm.DatePicker, "DatePicker", "categorical"),
            ("lifeExp", vm.DatePicker, "DatePicker", "numerical"),
            ("year", vm.Slider, "Slider", "temporal"),
            ("year", vm.RangeSlider, "RangeSlider", "temporal"),
            ("is_europe", vm.Slider, "Slider", "boolean"),
            ("is_europe", vm.RangeSlider, "RangeSlider", "boolean"),
            ("is_europe", vm.DatePicker, "DatePicker", "boolean"),
            ("year", vm.Switch, "Switch", "temporal"),
            # Also disallowed for categorical binary columns such as Off/On etc.
            ("country", vm.Switch, "Switch", "categorical"),
        ],
    )
    def test_disallowed_selectors_per_column_type(
        self, filtered_column, selector, selector_name, column_type, managers_one_page_two_graphs
    ):
        filter = vm.Filter(column=filtered_column, selector=selector())
        model_manager["test_page"].controls = [filter]
        with pytest.raises(
            ValueError,
            match=f"Chosen selector {selector_name} is not compatible with {column_type} column '{filtered_column}'.",
        ):
            filter.pre_build()

    @pytest.mark.parametrize(
        "targets",
        [
            ["column_numerical", "column_temporal"],
            ["column_numerical", "column_categorical"],
            ["column_temporal", "column_categorical"],
            ["column_boolean", "column_temporal"],
            ["column_boolean", "column_categorical"],
        ],
    )
    def test_validate_column_type(self, targets, managers_column_different_type):
        filter = vm.Filter(column="shared_column", targets=targets)
        model_manager["test_page"].controls = [filter]
        with pytest.raises(
            ValueError,
            match=r"Inconsistent types detected in column shared_column.",
        ):
            filter.pre_build()

    @pytest.mark.usefixtures("managers_one_page_two_graphs")
    def test_filter_is_not_dynamic(self):
        filter = vm.Filter(column="continent")
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        # Filter is not dynamic because it does not target a figure that uses dynamic data
        assert not filter._dynamic
        assert not filter.selector._dynamic

    @pytest.mark.usefixtures("managers_one_page_two_graphs_with_dynamic_data")
    @pytest.mark.parametrize(
        "test_column, test_selector",
        [
            ("continent", vm.Checklist()),
            ("continent", vm.Dropdown()),
            ("continent", vm.RadioItems()),
            ("pop", vm.Slider()),
            ("pop", vm.RangeSlider()),
            ("year", vm.DatePicker()),
        ],
    )
    def test_filter_is_dynamic_with_dynamic_selectors(
        self, test_column, test_selector, gapminder_dynamic_first_n_last_n_function
    ):
        data_manager["gapminder_dynamic_first_n_last_n"] = gapminder_dynamic_first_n_last_n_function
        filter = vm.Filter(column=test_column, selector=test_selector)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        # Filter is dynamic because it targets a figure that uses dynamic data
        assert filter._dynamic
        assert filter.selector._dynamic

    @pytest.mark.usefixtures("managers_one_page_two_graphs_with_dynamic_data")
    @pytest.mark.parametrize(
        "test_column ,test_selector",
        [
            ("continent", vm.Checklist(options=["Africa", "Europe"])),
            ("continent", vm.Dropdown(options=["Africa", "Europe"])),
            ("continent", vm.RadioItems(options=["Africa", "Europe"])),
            ("pop", vm.Slider(min=10**6)),
            ("pop", vm.Slider(max=10**7)),
            ("pop", vm.Slider(min=10**6, max=10**7)),
            ("pop", vm.RangeSlider(min=10**6)),
            ("pop", vm.RangeSlider(max=10**7)),
            ("pop", vm.RangeSlider(min=10**6, max=10**7)),
            ("year", vm.DatePicker(min="2002-01-01")),
            ("year", vm.DatePicker(max="2007-01-01")),
            ("year", vm.DatePicker(min="2002-01-01", max="2007-01-01")),
        ],
    )
    def test_filter_is_not_dynamic_with_options_min_max_specified(
        self, test_column, test_selector, gapminder_dynamic_first_n_last_n_function
    ):
        data_manager["gapminder_dynamic_first_n_last_n"] = gapminder_dynamic_first_n_last_n_function
        filter = vm.Filter(column=test_column, selector=test_selector)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert not filter._dynamic
        assert not filter.selector._dynamic

    @pytest.mark.parametrize("selector", [vm.Slider, vm.RangeSlider])
    def test_numerical_min_max_default(self, selector, gapminder, managers_one_page_two_graphs):
        filter = vm.Filter(column="lifeExp", selector=selector())
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.selector.min == gapminder.lifeExp.min()
        assert filter.selector.max == gapminder.lifeExp.max()

    def test_numerical_min_max_different_column_lengths(self, gapminder, managers_column_only_exists_in_some):
        filter = vm.Filter(column="column_numerical", selector=vm.Slider())
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.selector.min == 1
        assert filter.selector.max == 2

    def test_temporal_min_max_default(self, gapminder, managers_one_page_two_graphs):
        filter = vm.Filter(column="year", selector=vm.DatePicker())
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.selector.min == gapminder.year.min().to_pydatetime().date()
        assert filter.selector.max == gapminder.year.max().to_pydatetime().date()

    @pytest.mark.parametrize("selector", [vm.Slider, vm.RangeSlider])
    @pytest.mark.parametrize("min, max", [(3, 5), (0, 5), (-5, 0)])
    def test_numerical_min_max_specific(self, selector, min, max, managers_one_page_two_graphs):
        filter = vm.Filter(column="lifeExp", selector=selector(min=min, max=max))
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.selector.min == min
        assert filter.selector.max == max

    def test_temporal_min_max_specific(self, managers_one_page_two_graphs):
        filter = vm.Filter(column="year", selector=vm.DatePicker(min="1952-01-01", max="2007-01-01"))
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.selector.min == date(1952, 1, 1)
        assert filter.selector.max == date(2007, 1, 1)

    @pytest.mark.parametrize("selector", [vm.Checklist, vm.Dropdown, vm.RadioItems])
    def test_categorical_options_default(self, selector, gapminder, managers_one_page_two_graphs):
        filter = vm.Filter(column="continent", selector=selector())
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.selector.options == sorted(set(gapminder["continent"]))

    def test_categorical_options_different_column_lengths(self, gapminder, managers_column_only_exists_in_some):
        filter = vm.Filter(column="column_categorical", selector=vm.Checklist())
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.selector.options == ["a", "b"]

    @pytest.mark.parametrize("selector", [vm.Checklist, vm.Dropdown, vm.RadioItems])
    def test_categorical_options_specific(self, selector, managers_one_page_two_graphs):
        filter = vm.Filter(column="continent", selector=selector(options=["Africa", "Europe"]))
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.selector.options == ["Africa", "Europe"]

    @pytest.mark.parametrize(
        "filtered_column, selector, filter_function",
        [
            ("lifeExp", None, _filter_between),
            ("country", None, _filter_isin),
            ("year", None, _filter_between),
            ("year", vm.DatePicker(range=False), _filter_isin),
            ("is_europe", None, _filter_isin),
        ],
    )
    def test_set_actions(self, filtered_column, selector, filter_function, managers_one_page_two_graphs):
        filter = vm.Filter(column=filtered_column, selector=selector)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        [default_action] = filter.selector.actions

        assert isinstance(default_action, _filter)
        assert default_action.id == f"__filter_action_{filter.id}"
        assert default_action.filter_function == filter_function
        assert default_action.column == filtered_column
        assert default_action.targets == ["scatter_chart", "bar_chart"]

    # TODO: Add tests for custom temporal and categorical selectors too. Probably inside the conftest file and reused in
    #       all other tests. Also add tests for the custom selector that is an entirely new component and adjust docs.
    # This test does add_type so ideally we would clean up after this to restore vizro.models to its previous state.
    # This is difficult to fix fully by un-importing vizro.models though, since we use `import vizro.models as vm` - see
    # https://stackoverflow.com/questions/437589/how-do-i-unload-reload-a-python-module.
    def test_numerical_custom_selector(self, gapminder, managers_one_page_two_graphs):
        class RangeSliderNonCross(vm.RangeSlider):
            """Custom numerical multi-selector `RangeSliderNonCross` to be provided to `Filter`."""

            type: Literal["range_slider_non_cross"] = "range_slider_non_cross"

            def build(self):
                range_slider_build_obj = super().build()
                range_slider_build_obj[self.id].allowCross = False
                return range_slider_build_obj

        filtered_column = "lifeExp"
        selector = RangeSliderNonCross
        vm.Filter.add_type("selector", selector)

        filter = vm.Filter(column=filtered_column, selector=selector())
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        assert isinstance(filter.selector, selector)
        assert filter.selector.title == filtered_column.title()
        assert filter.selector.min == gapminder.lifeExp.min()
        assert filter.selector.max == gapminder.lifeExp.max()

        [default_action] = filter.selector.actions

        assert isinstance(default_action, _filter)
        assert default_action.id == f"__filter_action_{filter.id}"
        assert default_action.column == "lifeExp"
        assert default_action.filter_function == _filter_between
        assert default_action.targets == ["scatter_chart", "bar_chart"]

    @pytest.mark.usefixtures("managers_one_page_container_controls")
    def test_container_filter_default_targets(self):
        filter = model_manager["container_filter"]
        filter.pre_build()

        assert filter.targets == ["scatter_chart"]

    @pytest.mark.usefixtures("managers_one_page_container_controls")
    def test_container_wrapped_filter_default_targets(self, MockControlWrapper):
        filter = vm.Filter(column="continent")
        model_manager["test_container"].controls = [MockControlWrapper(control=filter)]
        filter.pre_build()

        assert filter.targets == ["scatter_chart"]

    @pytest.mark.usefixtures("managers_one_page_container_controls_invalid")
    def test_container_filter_targets_specific_invalid(self):
        filter = model_manager["container_filter"]
        with pytest.raises(
            ValueError,
            match="Target bar_chart not found within the container_1",
        ):
            filter.pre_build()

    def test_set_custom_action(self, managers_one_page_two_graphs, identity_action_function):
        action_function = identity_action_function()
        custom_action = vm.Action(function=action_function)

        filter = vm.Filter(
            column="country",
            selector=vm.RadioItems(
                actions=[custom_action],
            ),
        )
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        assert filter.selector.actions == [custom_action]

    def test_filter_action_properties(self, managers_column_only_exists_in_some):
        filter = Filter(
            id="filter_id",
            column="column_categorical",
            selector=vm.RadioItems(
                id="selector_id",
                title="Test Title",
                description=vm.Tooltip(id="selector_tooltip_id", text="Test", icon="info"),
            ),
        )
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        radio_items_properties = dbc.RadioItems().available_properties
        filter_selector_properties = set(radio_items_properties) - set(html.Div().available_properties)

        assert filter._action_triggers == {"__default__": "selector_id.value"}
        assert filter._action_outputs == {
            "__default__": "selector_id.value",
            "selector": "filter_id.children",
            "title": "selector_id_title.children",
            "description": "selector_tooltip_id-text.children",
            **{prop: f"selector_id.{prop}" for prop in filter_selector_properties},
        }
        assert filter._action_inputs == {
            "__default__": "selector_id.value",
            **{prop: f"selector_id.{prop}" for prop in filter_selector_properties},
        }


class TestFilterBuild:
    """Tests filter build method."""

    @pytest.mark.usefixtures("managers_one_page_two_graphs")
    @pytest.mark.parametrize(
        "test_column ,test_selector",
        [
            ("continent", vm.Checklist()),
            ("continent", vm.Dropdown()),
            ("continent", vm.Dropdown(multi=False)),
            ("continent", vm.RadioItems()),
            ("pop", vm.Slider()),
            ("pop", vm.RangeSlider()),
            ("year", vm.DatePicker()),
            ("year", vm.DatePicker(range=False)),
            ("is_europe", vm.Switch()),
            ("is_europe", vm.Switch(value=True)),
        ],
    )
    def test_filter_build(self, test_column, test_selector):
        filter = vm.Filter(id="filter-id", column=test_column, selector=test_selector)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        result = filter.build()
        expected = html.Div(
            id="filter-id",
            children=html.Div(
                children=[test_selector.build(), dcc.Store(id=f"{test_selector.id}_guard_actions_chain", data=False)]
            ),
            hidden=False,
        )

        assert_component_equal(result, expected)

    @pytest.mark.usefixtures("managers_one_page_two_graphs_with_dynamic_data")
    @pytest.mark.parametrize(
        "test_column, test_selector",
        [
            ("continent", vm.Checklist()),
            ("continent", vm.Dropdown()),
            ("continent", vm.Dropdown(multi=False)),
            ("continent", vm.RadioItems()),
            ("pop", vm.Slider()),
            ("pop", vm.RangeSlider()),
            ("year", vm.DatePicker()),
            ("year", vm.DatePicker(range=False)),
        ],
    )
    def test_dynamic_filter_build(self, test_column, test_selector, gapminder_dynamic_first_n_last_n_function):
        # Adding dynamic data_frame to data_manager
        data_manager["gapminder_dynamic_first_n_last_n"] = gapminder_dynamic_first_n_last_n_function
        filter = vm.Filter(id="filter_id", column=test_column, selector=test_selector)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        result = filter.build()
        expected = dcc.Loading(
            id="filter_id",
            children=html.Div(
                children=[test_selector.build(), dcc.Store(id=f"{test_selector.id}_guard_actions_chain", data=False)]
            ),
            color="grey",
            overlay_style={"visibility": "visible"},
        )

        assert_component_equal(result, expected, keys_to_strip={"className"})

    @pytest.mark.usefixtures("managers_one_page_two_graphs")
    @pytest.mark.parametrize("visible", [True, False])
    def test_filter_build_visible(self, visible):
        filter = vm.Filter(id="filter-id", column="continent", visible=visible)
        model_manager["test_page"].controls = [filter]

        filter.pre_build()
        result = filter.build()
        expected = html.Div(id="filter-id", hidden=not visible)

        assert_component_equal(result, expected, keys_to_strip={"children"})

    @pytest.mark.usefixtures("managers_one_page_two_graphs_with_dynamic_data")
    @pytest.mark.parametrize("visible", [True, False])
    def test_dynamic_filter_build_visible(self, gapminder_dynamic_first_n_last_n_function, visible):
        data_manager["gapminder_dynamic_first_n_last_n"] = gapminder_dynamic_first_n_last_n_function
        filter = vm.Filter(id="filter_id", column="continent", visible=visible)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        result = filter.build()
        expected = dcc.Loading(
            id="filter_id",
            color="grey",
            overlay_style={"visibility": "visible"},
            className="d-none" if not visible else "",
        )

        assert_component_equal(result, expected, keys_to_strip={"children"})


class TestGetSelectorDefaultValueCascader:
    def test_tree_select_multi_true_default_is_empty_list(self):
        ts = Cascader(multi=True)
        assert get_selector_default_value(ts) == []

    def test_tree_select_multi_false_default_is_none(self):
        ts = Cascader(multi=False)
        assert get_selector_default_value(ts) is None

    def test_tree_select_with_value_returns_value(self):
        # This test passes BEFORE the new branch is added (early-return handles it),
        # but it documents the expected contract so is worth keeping.
        ts = Cascader(options={"A": ["x"]}, value=["x"])
        assert get_selector_default_value(ts) == ["x"]


class TestFilterColumnHierarchyValidation:
    def test_both_column_and_column_hierarchy_raises(self):
        with pytest.raises(ValidationError, match="Only one of"):
            vm.Filter(column="species", column_hierarchy=["a", "b"])

    def test_neither_column_nor_column_hierarchy_raises(self):
        with pytest.raises(ValidationError, match="One of"):
            vm.Filter()

    def test_column_hierarchy_sets_field(self):
        f = vm.Filter(column_hierarchy=["continent", "country", "city"])
        assert f.column_hierarchy == ["continent", "country", "city"]
        # column is None at construction; set to column_hierarchy[-1] in pre_build
        assert f.column is None

    def test_column_alone_still_works(self):
        f = vm.Filter(column="species")
        assert f.column == "species"
        assert f.column_hierarchy == []


class TestGetTreeOptions:
    def test_three_level_hierarchy(self):
        wide_df = pd.DataFrame(
            {
                "continent": ["Americas", "Europe", "Europe", "Europe"],
                "country": ["USA", "France", "France", "Germany"],
                "city": ["New York", "Lyon", "Paris", "Berlin"],
            }
        )
        result = Filter._get_tree_options(wide_df, ["continent", "country", "city"])
        assert result == {
            "Americas": {"USA": ["New York"]},
            "Europe": {
                "France": ["Lyon", "Paris"],  # sorted alphabetically
                "Germany": ["Berlin"],
            },
        }

    def test_two_level_hierarchy(self):
        wide_df = pd.DataFrame(
            {
                "continent": ["Americas", "Europe", "Europe"],
                "city": ["New York", "Lyon", "Paris"],
            }
        )
        result = Filter._get_tree_options(wide_df, ["continent", "city"])
        assert result == {
            "Americas": ["New York"],
            "Europe": ["Lyon", "Paris"],
        }

    def test_duplicate_rows_deduplicated(self):
        wide_df = pd.DataFrame(
            {
                "continent": ["Europe", "Europe", "Europe"],
                "country": ["France", "France", "Germany"],
                "city": ["Paris", "Paris", "Berlin"],  # Paris appears twice
            }
        )
        result = Filter._get_tree_options(wide_df, ["continent", "country", "city"])
        assert result == {
            "Europe": {
                "France": ["Paris"],  # deduped
                "Germany": ["Berlin"],
            },
        }


@pytest.fixture
def managers_column_hierarchy():
    """Page with two graphs sharing continent/country/city columns."""
    df1 = pd.DataFrame(
        {
            "continent": ["Europe", "Europe", "Americas"],
            "country": ["France", "France", "USA"],
            "city": ["Paris", "Lyon", "New York"],
        }
    )
    df2 = pd.DataFrame(
        {
            "continent": ["Europe", "Asia"],
            "country": ["Germany", "Japan"],
            "city": ["Berlin", "Tokyo"],
        }
    )
    vm.Page(
        id="test_page",
        title="Page Title",
        components=[
            vm.Graph(id="fig_1", figure=px.scatter(df1, x="city", y="city")),
            vm.Graph(id="fig_2", figure=px.scatter(df2, x="city", y="city")),
        ],
    )
    Vizro._pre_build()


class TestFilterHierarchyPreBuild:
    def test_default_selector_is_tree_select(self, managers_column_hierarchy):
        from vizro.models._components.form import Cascader

        f = vm.Filter(column_hierarchy=["continent", "country", "city"])
        model_manager["test_page"].controls = [f]
        f.pre_build()
        assert isinstance(f.selector, Cascader)

    def test_column_set_to_leaf(self, managers_column_hierarchy):
        f = vm.Filter(column_hierarchy=["continent", "country", "city"])
        model_manager["test_page"].controls = [f]
        f.pre_build()
        assert f.column == "city"

    def test_title_defaults_to_leaf_column_name(self, managers_column_hierarchy):
        f = vm.Filter(column_hierarchy=["continent", "country", "city"])
        model_manager["test_page"].controls = [f]
        f.pre_build()
        assert f.selector.title == "City"

    def test_options_built_from_data(self, managers_column_hierarchy):
        f = vm.Filter(column_hierarchy=["continent", "country", "city"])
        model_manager["test_page"].controls = [f]
        f.pre_build()
        options = f.selector.options
        assert "Europe" in options
        assert "France" in options["Europe"]
        assert "Paris" in options["Europe"]["France"]
        assert "Berlin" in options["Europe"]["Germany"]
        assert "Japan" in options["Asia"]
        assert "Tokyo" in options["Asia"]["Japan"]

    def test_custom_tree_select_config_respected(self, managers_column_hierarchy):

        f = vm.Filter(
            column_hierarchy=["continent", "country", "city"],
            selector=vm.Cascader(multi=False, title="Location"),
        )
        model_manager["test_page"].controls = [f]
        f.pre_build()
        assert f.selector.multi is False
        assert f.selector.title == "Location"

    def test_non_tree_select_selector_raises(self, managers_column_hierarchy):
        f = vm.Filter(
            column_hierarchy=["continent", "country", "city"],
            selector=vm.Dropdown(),
        )
        model_manager["test_page"].controls = [f]
        with pytest.raises(ValueError, match="Cascader"):
            f.pre_build()

    def test_duplicate_leaf_values_in_data_raises(self):
        # Creates its own page inline; conftest autouse clears model_manager between tests
        df = pd.DataFrame(
            {
                "continent": ["Europe", "Europe"],
                "country": ["France", "Belgium"],
                "city": ["Bruges", "Bruges"],
            }
        )
        vm.Page(
            id="test_page_dup",
            title="Page",
            components=[vm.Graph(id="fig_dup", figure=px.scatter(df, x="city", y="city"))],
        )
        Vizro._pre_build()
        f = vm.Filter(column_hierarchy=["continent", "country", "city"])
        model_manager["test_page_dup"].controls = [f]
        with pytest.raises(ValueError, match="Duplicate leaf values"):
            f.pre_build()

    def test_figure_missing_intermediate_column_excluded(self):
        df_full = pd.DataFrame({"continent": ["Europe"], "country": ["France"], "city": ["Paris"]})
        df_missing = pd.DataFrame({"continent": ["Asia"], "city": ["Tokyo"]})  # no "country"
        vm.Page(
            id="test_page_missing",
            title="Page",
            components=[
                vm.Graph(id="fig_full", figure=px.scatter(df_full, x="city", y="city")),
                vm.Graph(id="fig_missing", figure=px.scatter(df_missing, x="city", y="city")),
            ],
        )
        Vizro._pre_build()
        f = vm.Filter(column_hierarchy=["continent", "country", "city"])
        model_manager["test_page_missing"].controls = [f]
        f.pre_build()
        assert "fig_full" in f.targets
        assert "fig_missing" not in f.targets

    def test_filter_action_uses_leaf_column(self, managers_column_hierarchy):
        f = vm.Filter(column_hierarchy=["continent", "country", "city"])
        model_manager["test_page"].controls = [f]
        f.pre_build()
        # f.selector.actions[0] is a _filter action instance with a .column field
        assert f.selector.actions[0].column == "city"


@pytest.fixture
def managers_column_hierarchy_dynamic(gapminder_dynamic_first_n_last_n_function):
    """Page with one graph using dynamic gapminder data (has continent and country columns)."""
    data_manager["gapminder_dynamic_first_n_last_n"] = gapminder_dynamic_first_n_last_n_function
    vm.Page(
        id="test_page",
        title="Page Title",
        components=[
            vm.Graph(
                id="fig_dynamic", figure=px.scatter("gapminder_dynamic_first_n_last_n", x="continent", y="country")
            )
        ],
    )
    Vizro._pre_build()


class TestFilterHierarchyPreBuildDynamic:
    def test_dynamic_flag_set(self, managers_column_hierarchy_dynamic):
        f = vm.Filter(column_hierarchy=["continent", "country"])
        model_manager["test_page"].controls = [f]
        f.pre_build()
        assert f._dynamic is True
        assert f.selector._dynamic is True

    def test_options_not_set_for_dynamic_filter(self, managers_column_hierarchy_dynamic):
        f = vm.Filter(column_hierarchy=["continent", "country"])
        model_manager["test_page"].controls = [f]
        f.pre_build()
        assert f.selector.options == {}

    def test_dynamic_flag_not_set_for_static_data(self, managers_column_hierarchy):
        # managers_column_hierarchy uses static data frames
        f = vm.Filter(column_hierarchy=["continent", "country", "city"])
        model_manager["test_page"].controls = [f]
        f.pre_build()
        assert f._dynamic is False
        assert f.selector._dynamic is False

    def test_user_supplied_options_prevent_dynamic(self, managers_column_hierarchy_dynamic):
        # User-supplied options → treated as static regardless of data source
        f = vm.Filter(
            column_hierarchy=["continent", "country"],
            selector=vm.Cascader(options={"Europe": ["France", "Germany"]}),
        )
        model_manager["test_page"].controls = [f]
        f.pre_build()
        assert f._dynamic is False
        assert f.selector._dynamic is False


@pytest.fixture
def tree_filter_pre_built(managers_column_hierarchy_dynamic):
    """Pre-built dynamic tree filter targeting fig_dynamic."""
    f = vm.Filter(
        column_hierarchy=["continent", "country"],
        targets=["fig_dynamic"],
        selector=vm.Cascader(id="tree_selector_id"),
    )
    model_manager["test_page"].controls = [f]
    f.pre_build()
    return f


class TestFilterCallTree:
    def test_call_returns_fresh_options(self, tree_filter_pre_built):
        fresh_df = pd.DataFrame({"continent": ["Europe", "Asia"], "country": ["France", "Japan"]})
        result = tree_filter_pre_built(
            target_to_data_frame={"fig_dynamic": fresh_df},
            current_value=[],
        )
        tree_component = result["tree_selector_id"]
        # Options should reflect fresh data: Europe and Asia as top-level groups
        assert "Europe" in tree_component.options
        assert "Asia" in tree_component.options
        assert "(Stale selection)" not in tree_component.options

    def test_call_injects_stale_values(self, tree_filter_pre_built):
        fresh_df = pd.DataFrame({"continent": ["Europe"], "country": ["France"]})
        # "OldCountry" was previously selected but is no longer in the data
        result = tree_filter_pre_built(
            target_to_data_frame={"fig_dynamic": fresh_df},
            current_value=["OldCountry"],
        )
        tree_component = result["tree_selector_id"]
        assert "(Stale selection)" in tree_component.options
        assert "OldCountry" in tree_component.options["(Stale selection)"]

    def test_call_multi_false_stale_string(self, managers_column_hierarchy_dynamic):
        f = vm.Filter(
            column_hierarchy=["continent", "country"],
            targets=["fig_dynamic"],
            selector=vm.Cascader(id="tree_selector_id_single", multi=False),
        )
        model_manager["test_page"].controls = [f]
        f.pre_build()
        fresh_df = pd.DataFrame({"continent": ["Europe"], "country": ["France"]})
        result = f(
            target_to_data_frame={"fig_dynamic": fresh_df},
            current_value="Atlantis",
        )
        tree_component = result["tree_selector_id_single"]
        assert "(Stale selection)" in tree_component.options

    def test_call_no_stale_when_current_value_empty(self, tree_filter_pre_built):
        fresh_df = pd.DataFrame({"continent": ["Europe"], "country": ["France"]})
        result = tree_filter_pre_built(
            target_to_data_frame={"fig_dynamic": fresh_df},
            current_value=[],
        )
        tree_component = result["tree_selector_id"]
        assert "(Stale selection)" not in tree_component.options

    def test_call_target_missing_hierarchy_column_excluded(self, tree_filter_pre_built):
        # DataFrame missing "country" column → silently excluded, options empty
        bad_df = pd.DataFrame({"continent": ["Europe"]})
        result = tree_filter_pre_built(
            target_to_data_frame={"fig_dynamic": bad_df},
            current_value=[],
        )
        tree_component = result["tree_selector_id"]
        assert tree_component.options == {}

    def test_call_guard_component_is_true(self, tree_filter_pre_built):
        fresh_df = pd.DataFrame({"continent": ["Europe"], "country": ["France"]})
        result = tree_filter_pre_built(
            target_to_data_frame={"fig_dynamic": fresh_df},
            current_value=[],
        )
        guard = result["tree_selector_id_guard_actions_chain"]
        assert guard.data is True
