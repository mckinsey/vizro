import pandas as pd
import pytest

import vizro.models as vm
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
            (
                [1.1, 2.2, 3.3, 4.4, 5.5],
                [2.1, 4.5],
                [False, True, True, True, False],
            ),  # Test with float data
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
            ([1, 2, 3, 4, 5], [2, 4], [False, True, False, True, False]),  # Test for integers
            (["apple", "banana", "orange"], ["banana", "grape"], [False, True, False]),  # Test for strings
            (
                [1.1, 2.2, 3.3, 4.4, 5.5],
                [2.2, 4.4],  # Test for float values
                [False, True, False, True, False],
            ),
            ([1, 2, 3, 4, 5], [], [False, False, False, False, False]),  # Test for empty value list
        ],
    )
    def test_filter_isin(self, data, value, expected):
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
        "test_input,expected", [("country", "categorical"), ("year", "numerical"), ("lifeExp", "numerical")]
    )
    def test_set_column_type(self, test_input, expected, managers_one_page_two_graphs):
        filter = vm.Filter(column=test_input)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter._column_type == expected

    @pytest.mark.parametrize(
        "test_input,expected", [("country", vm.Dropdown), ("year", vm.RangeSlider), ("lifeExp", vm.RangeSlider)]
    )
    def test_set_selector(self, test_input, expected, managers_one_page_two_graphs):
        filter = vm.Filter(column=test_input)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert isinstance(filter.selector, expected)
        assert filter.selector.title == test_input.title()

    @pytest.mark.parametrize("test_input", [vm.Slider(), vm.RangeSlider()])
    def test_set_slider_values_incompatible_column_type(self, test_input, managers_one_page_two_graphs):
        filter = vm.Filter(column="country", selector=test_input)
        model_manager["test_page"].controls = [filter]
        with pytest.raises(
            ValueError,
            match=f"Chosen selector {test_input.type} is not compatible with categorical column '{filter.column}'.",
        ):
            filter.pre_build()

    @pytest.mark.parametrize("test_input", [vm.Slider(), vm.RangeSlider()])
    def test_set_slider_values_shared_column_inconsistent_dtype(
        self, test_input, managers_shared_column_different_dtype
    ):
        filter = vm.Filter(column="shared_column", selector=test_input)
        model_manager["graphs_with_shared_column"].controls = [filter]
        with pytest.raises(
            ValueError,
            match=f"Non-numeric values detected in the shared data column '{filter.column}' for targeted charts. "
            f"Please ensure that the data column contains the same data type across all targeted charts.",
        ):
            filter.pre_build()

    @pytest.mark.parametrize("test_input", [vm.Slider(), vm.RangeSlider()])
    def test_set_slider_values_defaults_min_max_none(self, test_input, gapminder, managers_one_page_two_graphs):
        filter = vm.Filter(column="lifeExp", selector=test_input)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.selector.min == gapminder.lifeExp.min()
        assert filter.selector.max == gapminder.lifeExp.max()

    @pytest.mark.parametrize("test_input", [vm.Slider(min=3, max=5), vm.RangeSlider(min=3, max=5)])
    def test_set_slider_values_defaults_min_max_fix(self, test_input, managers_one_page_two_graphs):
        filter = vm.Filter(column="lifeExp", selector=test_input)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.selector.min == 3
        assert filter.selector.max == 5

    @pytest.mark.parametrize("test_input", [vm.Checklist(), vm.Dropdown(), vm.RadioItems()])
    def test_set_categorical_selectors_options_defaults_options_none(
        self, test_input, gapminder, managers_one_page_two_graphs
    ):
        filter = vm.Filter(column="continent", selector=test_input)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.selector.options == sorted(set(gapminder["continent"]))

    @pytest.mark.parametrize(
        "test_input",
        [
            vm.Checklist(options=["Africa", "Europe"]),
            vm.Dropdown(options=["Africa", "Europe"]),
            vm.RadioItems(options=["Africa", "Europe"]),
        ],
    )
    def test_set_categorical_selectors_options_defaults_options_fix(self, test_input, managers_one_page_two_graphs):
        filter = vm.Filter(column="continent", selector=test_input)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        assert filter.selector.options == ["Africa", "Europe"]

    @pytest.mark.parametrize("test_input", ["country", "year", "lifeExp"])
    def test_set_actions(self, test_input, managers_one_page_two_graphs):
        filter = vm.Filter(column=test_input)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        default_action = filter.selector.actions[0]
        assert isinstance(default_action, ActionsChain)
        assert isinstance(default_action.actions[0].function, CapturedCallable)
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
        ],
    )
    def test_filter_build(self, test_column, test_selector):
        filter = vm.Filter(column=test_column, selector=test_selector)
        model_manager["test_page"].controls = [filter]
        filter.pre_build()
        result = str(filter.build())
        expected = str(test_selector.build())
        assert result == expected
