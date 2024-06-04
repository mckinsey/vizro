import re
from datetime import date, datetime
from typing import Literal

import pandas as pd
import pytest
import vizro.models as vm
from asserts import assert_component_equal
from vizro.managers import model_manager
from vizro.models._action._actions_chain import ActionsChain
from vizro.models._controls.filter import Filter, _filter_between, _filter_isin
from vizro.models.types import CapturedCallable


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


@pytest.mark.usefixtures("managers_one_page_two_graphs")
class TestFilterInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_create_filter_mandatory_only(self):
        filter = Filter(column="foo")
        assert filter.type == "filter"
        assert filter.column == "foo"
        assert filter.targets == []

    def test_create_filter_mandatory_and_optional(self):
        filter = Filter(column="foo", targets=["scatter_chart", "bar_chart"], selector=vm.RadioItems())
        assert filter.type == "filter"
        assert filter.column == "foo"
        assert filter.targets == ["scatter_chart", "bar_chart"]
        assert isinstance(filter.selector, vm.RadioItems)

    def test_check_target_present_valid(self):
        Filter(column="foo", targets=["scatter_chart", "bar_chart"])

    def test_check_target_present_invalid(self):
        with pytest.raises(ValueError, match="Target invalid_target not found in model_manager."):
            Filter(column="foo", targets=["invalid_target"])


class TestPreBuildMethod:
    def test_set_targets_valid(self, managers_one_page_two_graphs):
        # Core of tests is still interface level
        filter = vm.Filter(column="country")
        # Special case - need filter in the context of page in order to run filter.pre_build
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert set(filter.targets) == {"scatter_chart", "bar_chart"}

    def test_set_targets_invalid(self, managers_one_page_two_graphs):
        filter = vm.Filter(column="invalid_choice")
        model_manager["test_page"].controls = [filter]

        with pytest.raises(ValueError, match="Selected column invalid_choice not found in any dataframe on this page."):
            filter.pre_build()

    @pytest.mark.parametrize(
        "filtered_column, expected_column_type",
        [("country", "categorical"), ("year", "temporal"), ("lifeExp", "numerical")],
    )
    def test_set_column_type(self, filtered_column, expected_column_type, managers_one_page_two_graphs):
        filter = vm.Filter(column=filtered_column)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter._column_type == expected_column_type

    @pytest.mark.parametrize(
        "filtered_column, expected_selector",
        [("country", vm.Dropdown), ("year", vm.DatePicker), ("lifeExp", vm.RangeSlider)],
    )
    def test_set_selector_default_selector(self, filtered_column, expected_selector, managers_one_page_two_graphs):
        filter = vm.Filter(column=filtered_column)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert isinstance(filter.selector, expected_selector)
        assert filter.selector.title == filtered_column.title()

    @pytest.mark.parametrize("filtered_column", ["country", "year", "lifeExp"])
    def test_set_selector_specific_selector(self, filtered_column, managers_one_page_two_graphs):
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
        "filtered_column, selector",
        [
            ("country", vm.Slider),
            ("country", vm.RangeSlider),
            ("country", vm.DatePicker),
            ("lifeExp", vm.DatePicker),
            ("year", vm.Slider),
            ("year", vm.RangeSlider),
        ],
    )
    def test_disallowed_selectors_per_column_type(self, filtered_column, selector, managers_one_page_two_graphs):
        filter = vm.Filter(column=filtered_column, selector=selector())
        model_manager["test_page"].controls = [filter]
        with pytest.raises(
            ValueError,
            match=f"Chosen selector {selector().type} is not compatible with .* column '{filtered_column}'. ",
        ):
            filter.pre_build()

    @pytest.mark.parametrize(
        "targets",
        [
            ["id_shared_column_numerical", "id_shared_column_temporal"],
            ["id_shared_column_numerical", "id_shared_column_categorical"],
            ["id_shared_column_temporal", "id_shared_column_categorical"],
        ],
    )
    def test_set_slider_values_shared_column_inconsistent_dtype(self, targets, managers_shared_column_different_dtype):
        filter = vm.Filter(column="shared_column", targets=targets)
        model_manager["graphs_with_shared_column"].controls = [filter]
        with pytest.raises(
            ValueError,
            match=re.escape(
                f"Inconsistent types detected in the shared data column 'shared_column' for targeted charts {targets}. "
                f"Please ensure that the data column contains the same data type across all targeted charts."
            ),
        ):
            filter.pre_build()

    @pytest.mark.parametrize("selector", [vm.Slider, vm.RangeSlider])
    def test_set_numerical_selectors_values_min_max_default(self, selector, gapminder, managers_one_page_two_graphs):
        filter = vm.Filter(column="lifeExp", selector=selector())
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.selector.min == gapminder.lifeExp.min()
        assert filter.selector.max == gapminder.lifeExp.max()

    def test_set_temporal_selectors_values_min_max_default(self, gapminder, managers_one_page_two_graphs):
        filter = vm.Filter(column="year", selector=vm.DatePicker())
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.selector.min == gapminder.year.min().to_pydatetime().date()
        assert filter.selector.max == gapminder.year.max().to_pydatetime().date()

    @pytest.mark.parametrize("selector", [vm.Slider, vm.RangeSlider])
    def test_set_numerical_selectors_values_min_max_specific(self, selector, managers_one_page_two_graphs):
        filter = vm.Filter(column="lifeExp", selector=selector(min=3, max=5))
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.selector.min == 3
        assert filter.selector.max == 5

    def test_set_temporal_selectors_values_min_max_specific(self, managers_one_page_two_graphs):
        filter = vm.Filter(column="year", selector=vm.DatePicker(min="1952-01-01", max="2007-01-01"))
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.selector.min == date(1952, 1, 1)
        assert filter.selector.max == date(2007, 1, 1)

    @pytest.mark.parametrize("selector", [vm.Checklist, vm.Dropdown, vm.RadioItems])
    def test_set_categorical_selectors_options_default(self, selector, gapminder, managers_one_page_two_graphs):
        filter = vm.Filter(column="continent", selector=selector())
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.selector.options == sorted(set(gapminder["continent"]))

    @pytest.mark.parametrize("selector", [vm.Checklist, vm.Dropdown, vm.RadioItems])
    def test_set_categorical_selectors_options_specific(self, selector, managers_one_page_two_graphs):
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
        default_action = filter.selector.actions[0]
        assert isinstance(default_action, ActionsChain)
        assert isinstance(default_action.actions[0].function, CapturedCallable)
        assert default_action.actions[0].function["filter_function"] == filter_function
        assert default_action.actions[0].id == f"filter_action_{filter.id}"

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

        default_action = filter.selector.actions[0]
        assert isinstance(default_action, ActionsChain)
        assert isinstance(default_action.actions[0].function, CapturedCallable)
        assert default_action.actions[0].function["filter_function"] == _filter_between
        assert default_action.actions[0].id == f"filter_action_{filter.id}"


@pytest.mark.usefixtures("managers_one_page_two_graphs")
class TestFilterBuild:
    """Tests filter build method."""

    @pytest.mark.parametrize(
        "test_column,test_selector",
        [
            ("continent", vm.Checklist()),
            ("continent", vm.Dropdown()),
            ("continent", vm.RadioItems()),
            ("pop", vm.RangeSlider()),
            ("pop", vm.Slider()),
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
