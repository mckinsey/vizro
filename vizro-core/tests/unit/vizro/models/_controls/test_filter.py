from datetime import date, datetime
from typing import Literal

import pandas as pd
import pytest
from asserts import assert_component_equal
from dash import dcc

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions._abstract_action import _AbstractAction
from vizro.managers import data_manager, model_manager
from vizro.models._action._actions_chain import ActionsChain
from vizro.models._controls.filter import Filter, _filter_between, _filter_isin


@pytest.fixture
def managers_column_different_type():
    """Instantiates the managers with a page and two graphs sharing the same column but of different data types."""
    df_numerical = pd.DataFrame({"shared_column": [1]})
    df_temporal = pd.DataFrame({"shared_column": [datetime(2024, 1, 1)]})
    df_categorical = pd.DataFrame({"shared_column": ["a"]})

    vm.Page(
        id="test_page",
        title="Page Title",
        components=[
            vm.Graph(id="column_numerical", figure=px.scatter(df_numerical)),
            vm.Graph(id="column_temporal", figure=px.scatter(df_temporal)),
            vm.Graph(id="column_categorical", figure=px.scatter(df_categorical)),
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
        targeted_data = pd.DataFrame({f"target_{i}": pd.Series(data) for i, data in enumerate(data_columns)})
        result = Filter._get_options(targeted_data)
        assert result == expected

    @pytest.mark.parametrize(
        "data_columns, current_value, expected",
        [
            ([[]], None, []),
            ([[]], "ALL", []),
            ([[]], ["ALL", "A"], ["A"]),
            ([["A"]], ["ALL", "B"], ["A", "B"]),
            ([[]], "A", ["A"]),
            ([[]], ["A", "B"], ["A", "B"]),
            ([["A"]], "B", ["A", "B"]),
            ([["A"]], ["B", "C"], ["A", "B", "C"]),
            ([[1]], 2, [1, 2]),
            ([[1]], [2, 3], [1, 2, 3]),
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
        targeted_data = pd.DataFrame({f"target_{i}": pd.Series(data) for i, data in enumerate(data_columns)})
        result = Filter._get_options(targeted_data, current_value)
        assert result == expected

    @pytest.mark.parametrize(
        "data_columns, expected",
        [
            ([[1, 2, 1]], (1, 2)),
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


@pytest.mark.usefixtures("managers_one_page_two_graphs")
class TestFilterInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_create_filter_mandatory_only(self):
        filter = Filter(column="foo")
        assert filter.type == "filter"
        assert filter.column == "foo"
        assert filter.targets == []
        assert filter.selector is None
        assert filter._action_outputs == {"__default__": f"{filter.id}.children"}

    def test_create_filter_mandatory_and_optional(self):
        filter = Filter(column="foo", targets=["scatter_chart", "bar_chart"], selector=vm.RadioItems())
        assert filter.type == "filter"
        assert filter.column == "foo"
        assert filter.targets == ["scatter_chart", "bar_chart"]
        assert isinstance(filter.selector, vm.RadioItems)

    def test_check_target_present_valid(self):
        Filter(column="foo", targets=["scatter_chart", "bar_chart"])


@pytest.mark.usefixtures("managers_column_only_exists_in_some")
class TestFilterCall:
    """Test Filter.__call__() method with target_to_data_frame and current_value inputs."""

    def test_filter_call_categorical_valid(self, target_to_data_frame):
        filter = vm.Filter(
            column="column_categorical",
            targets=["column_categorical_exists_1", "column_categorical_exists_2"],
            selector=vm.Checklist(id="test_selector_id"),
        )
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        selector_build = filter(target_to_data_frame=target_to_data_frame, current_value=["c", "d"])["test_selector_id"]
        assert selector_build.options == ["ALL", "a", "b", "c", "d"]

    def test_filter_call_numerical_valid(self, target_to_data_frame):
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

    def test_filter_call_temporal_valid(self, target_to_data_frame):
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

    def test_filter_call_column_is_changed(self, target_to_data_frame):
        filter = vm.Filter(
            column="column_categorical", targets=["column_categorical_exists_1", "column_categorical_exists_2"]
        )
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        filter._column_type = "numerical"

        with pytest.raises(
            ValueError,
            match="column_categorical has changed type from numerical to categorical. "
            "A filtered column cannot change type while the dashboard is running.",
        ):
            filter(target_to_data_frame=target_to_data_frame, current_value=["a", "b"])

    def test_filter_call_selected_column_not_found_in_target(self):
        filter = vm.Filter(column="column_categorical", targets=["column_categorical_exists_1"])
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        with pytest.raises(
            ValueError,
            match="Selected column column_categorical not found in dataframe for column_categorical_exists_1.",
        ):
            filter(target_to_data_frame={"column_categorical_exists_1": pd.DataFrame()}, current_value=["a", "b"])

    def test_filter_call_targeted_data_empty(self):
        filter = vm.Filter(column="column_categorical", targets=["column_categorical_exists_1"])
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        with pytest.raises(
            ValueError,
            match="Selected column column_categorical does not contain anything in any dataframe "
            "for column_categorical_exists_1.",
        ):
            filter(
                target_to_data_frame={"column_categorical_exists_1": pd.DataFrame({"column_categorical": []})},
                current_value=["a", "b"],
            )


class TestPreBuildMethod:
    def test_filter_not_in_page(self):
        with pytest.raises(ValueError, match="Control filter_id should be defined within a Page object"):
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

    def test_targets_specific_valid(self, managers_column_only_exists_in_some):
        filter = vm.Filter(column="column_numerical", targets=["column_numerical_exists_1"])
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.targets == ["column_numerical_exists_1"]

    def test_targets_specific_present_invalid(self, managers_column_only_exists_in_some):
        filter = vm.Filter(column="column_numerical", targets=["invalid_target"])
        model_manager["test_page"].controls = [filter]

        with pytest.raises(ValueError, match="Target invalid_target not found within the test_page."):
            filter.pre_build()

    def test_targets_default_invalid(self, managers_column_only_exists_in_some):
        filter = vm.Filter(column="invalid_choice")
        model_manager["test_page"].controls = [filter]

        with pytest.raises(
            ValueError,
            match="Selected column invalid_choice not found in any dataframe for column_numerical_exists_1, "
            "column_numerical_exists_2, column_numerical_exists_empty, column_categorical_exists_1, "
            "column_categorical_exists_2.",
        ):
            filter.pre_build()

    def test_targets_specific_invalid(self, managers_column_only_exists_in_some):
        filter = vm.Filter(column="column_numerical", targets=["column_categorical_exists_1"])
        model_manager["test_page"].controls = [filter]

        with pytest.raises(
            ValueError,
            match="Selected column column_numerical not found in dataframe for column_categorical_exists_1.",
        ):
            filter.pre_build()

    def test_targets_empty(self, managers_column_only_exists_in_some):
        filter = vm.Filter(column="column_numerical", targets=["column_numerical_exists_empty"])
        model_manager["test_page"].controls = [filter]

        with pytest.raises(
            ValueError,
            match="Selected column column_numerical does not contain anything in any dataframe for "
            "column_numerical_exists_empty.",
        ):
            filter.pre_build()

    @pytest.mark.parametrize(
        "filtered_column, expected_column_type",
        [("country", "categorical"), ("year", "temporal"), ("lifeExp", "numerical")],
    )
    def test_column_type(self, filtered_column, expected_column_type, managers_one_page_two_graphs):
        filter = vm.Filter(column=filtered_column)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter._column_type == expected_column_type

    @pytest.mark.parametrize(
        "filtered_column, expected_selector",
        [("country", vm.Dropdown), ("year", vm.DatePicker), ("lifeExp", vm.RangeSlider)],
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
        ],
    )
    def test_validate_column_type(self, targets, managers_column_different_type):
        filter = vm.Filter(column="shared_column", targets=targets)
        model_manager["test_page"].controls = [filter]
        with pytest.raises(
            ValueError,
            match="Inconsistent types detected in column shared_column.",
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
            ("pop", vm.Slider(min=2002)),
            ("pop", vm.Slider(max=2007)),
            ("pop", vm.Slider(min=2002, max=2007)),
            ("pop", vm.RangeSlider(min=2002)),
            ("pop", vm.RangeSlider(max=2007)),
            ("pop", vm.RangeSlider(min=2002, max=2007)),
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
        ],
    )
    def test_set_actions(self, filtered_column, selector, filter_function, managers_one_page_two_graphs):
        filter = vm.Filter(column=filtered_column, selector=selector)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        default_actions_chain = filter.selector.actions[0]
        default_action = default_actions_chain.actions[0]

        assert isinstance(default_actions_chain, ActionsChain)
        assert isinstance(default_action, _AbstractAction)
        assert default_action.filter_function == filter_function
        assert default_action.id == f"__filter_action_{filter.id}"

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

        default_actions_chain = filter.selector.actions[0]
        default_action = default_actions_chain.actions[0]

        assert isinstance(default_actions_chain, ActionsChain)
        assert isinstance(default_action, _AbstractAction)
        assert default_action.filter_function == _filter_between
        assert default_action.id == f"__filter_action_{filter.id}"

    @pytest.mark.usefixtures("managers_one_page_container_controls")
    def test_container_filter_defaults(self):
        filter = model_manager["container_filter"]
        filter.pre_build()

        assert filter.selector.extra == {"inline": True}

    @pytest.mark.usefixtures("managers_one_page_container_controls")
    def test_container_filter_default_targets(self):
        filter = model_manager["container_filter"]
        filter.pre_build()

        assert filter.targets == ["scatter_chart"]

    @pytest.mark.usefixtures("managers_one_page_container_controls_invalid")
    def test_container_filter_targets_specific_invalid(self):
        filter = model_manager["container_filter_2"]
        with pytest.raises(
            ValueError,
            match="Target bar_chart not found within the container_1",
        ):
            filter.pre_build()

    def test_set_custom_action(self, managers_one_page_two_graphs, identity_action_function):
        action_function = identity_action_function()

        filter = vm.Filter(
            column="country",
            selector=vm.RadioItems(
                actions=[vm.Action(function=action_function)],
            ),
        )
        model_manager["test_page"].controls = [filter]
        filter.pre_build()

        default_actions_chain = filter.selector.actions[0]
        default_action = default_actions_chain.actions[0]

        assert isinstance(default_actions_chain, ActionsChain)
        assert default_action.function is action_function


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
        ],
    )
    def test_filter_build(self, test_column, test_selector):
        filter = vm.Filter(column=test_column, selector=test_selector)
        model_manager["test_page"].controls = [filter]

        filter.pre_build()
        result = filter.build()
        expected = test_selector.build()

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
            children=test_selector.build(),
            color="grey",
            overlay_style={"visibility": "visible"},
        )

        assert_component_equal(result, expected, keys_to_strip={"className"})
