"""Unit tests for hyphen.models.slider."""

import dash_bootstrap_components as dbc
import pytest
from asserts import assert_component_equal
from dash import dcc, html

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

import vizro.models as vm


@pytest.fixture()
def expected_range_slider_default():
    return html.Div(
        [
            dcc.Store(id="range_slider_callback_data", data={"id": "range_slider", "min": None, "max": None}),
            html.Div(
                [
                    None,
                    html.Div(
                        [
                            dcc.Input(
                                id="range_slider_start_value",
                                type="number",
                                placeholder="min",
                                min=None,
                                max=None,
                                step=None,
                                value=None,
                                persistence=True,
                                persistence_type="session",
                                className="slider-text-input-field",
                            ),
                            html.Span("-", className="slider-text-input-range-separator"),
                            dcc.Input(
                                id="range_slider_end_value",
                                type="number",
                                placeholder="max",
                                min=None,
                                max=None,
                                step=None,
                                value=None,
                                persistence=True,
                                persistence_type="session",
                                className="slider-text-input-field",
                            ),
                            dcc.Store(id="range_slider_input_store", storage_type="session", data=[None, None]),
                        ],
                        className="slider-text-input-container",
                    ),
                ],
                className="slider-label-input",
            ),
            dcc.RangeSlider(
                id="range_slider",
                min=None,
                max=None,
                step=None,
                marks=None,
                value=[None, None],
                persistence=True,
                persistence_type="session",
                className="slider-track-without-marks",
            ),
        ]
    )


@pytest.fixture()
def expected_range_slider_with_optional():
    return html.Div(
        [
            dcc.Store(id="range_slider_callback_data", data={"id": "range_slider", "min": 0.0, "max": 10.0}),
            html.Div(
                [
                    dbc.Label("Title", html_for="range_slider"),
                    html.Div(
                        [
                            dcc.Input(
                                id="range_slider_start_value",
                                type="number",
                                placeholder="min",
                                min=0.0,
                                max=10.0,
                                step=2.0,
                                value=[0, 10][0],
                                persistence=True,
                                persistence_type="session",
                                className="slider-text-input-field",
                            ),
                            html.Span("-", className="slider-text-input-range-separator"),
                            dcc.Input(
                                id="range_slider_end_value",
                                type="number",
                                placeholder="max",
                                min=0.0,
                                max=10.0,
                                step=2.0,
                                value=[0, 10][1],
                                persistence=True,
                                persistence_type="session",
                                className="slider-text-input-field",
                            ),
                            dcc.Store(id="range_slider_input_store", storage_type="session", data=[0, 10]),
                        ],
                        className="slider-text-input-container",
                    ),
                ],
                className="slider-label-input",
            ),
            dcc.RangeSlider(
                id="range_slider",
                min=0.0,
                max=10.0,
                step=2.0,
                marks={1: "1", 5: "5", 10: "10"},
                value=[0, 10],
                persistence=True,
                persistence_type="session",
                className="slider-track-with-marks",
            ),
        ]
    )


class TestRangeSliderInstantiation:
    """Tests model instantiation."""

    def test_create_range_slider_mandatory_only(self):
        range_slider = vm.RangeSlider()

        assert hasattr(range_slider, "id")
        assert range_slider.type == "range_slider"
        assert range_slider.min is None
        assert range_slider.max is None
        assert range_slider.step is None
        assert range_slider.marks is None
        assert range_slider.value is None
        assert range_slider.title == ""
        assert range_slider.actions == []

    def test_create_range_slider_mandatory_and_optional(self):
        range_slider = vm.RangeSlider(
            id="range_slider_id",
            min=0,
            max=10,
            step=1,
            marks={1: "1", 5: "5", 10: "10"},
            value=[1, 9],
            title="Test title",
        )

        assert range_slider.id == "range_slider_id"
        assert range_slider.type == "range_slider"
        assert range_slider.min == 0
        assert range_slider.max == 10
        assert range_slider.step == 1
        assert range_slider.marks == {1: "1", 5: "5", 10: "10"}
        assert range_slider.value == [1, 9]
        assert range_slider.title == "Test title"
        assert range_slider.actions == []

    @pytest.mark.parametrize(
        "min, max, expected_min, expected_max",
        [(0, None, 0, None), (None, 10, None, 10), (0, 10, 0, 10), ("1", "10", 1, 10)],
    )
    def test_valid_min_max(self, min, max, expected_min, expected_max):
        range_slider = vm.RangeSlider(min=min, max=max)

        assert range_slider.min == expected_min
        assert range_slider.max == expected_max

    def test_validate_max_invalid(self):
        with pytest.raises(
            ValidationError, match="Maximum value of selector is required to be larger than minimum value."
        ):
            vm.RangeSlider(min=10, max=0)

    @pytest.mark.parametrize(
        "value, expected",
        [
            (None, None),
            ([1, 2], [1, 2]),
            ([0.1, 1.1], [0.1, 1.1]),
            ([-10, 10], [-10, 10]),
            ([10, 10], [10, 10]),
            (["1", "10"], [1, 10]),
        ],
    )
    def test_validate_slider_value_valid(self, value, expected):
        range_slider = vm.RangeSlider(min=-10, max=10, value=value)

        assert range_slider.value == expected

    @pytest.mark.parametrize(
        "value, match",
        [
            ([0], "ensure this value has at least 2 items"),
            ([], "ensure this value has at least 2 items"),
            (2, "value is not a valid list"),
            ([0, None], "1 validation error for RangeSlider"),
            ([None, None], "2 validation errors for RangeSlider"),
            ([-1, 11], "Please provide a valid value between the min and max value."),
            ([1, 2, 3], "ensure this value has at most 2 items"),
        ],
    )
    def test_validate_slider_value_invalid(self, value, match):
        with pytest.raises(ValidationError, match=match):
            vm.RangeSlider(min=0, max=10, value=value)

    @pytest.mark.parametrize("step, expected", [(1, 1), (2.5, 2.5), (10, 10), (None, None), ("1", 1.0)])
    def test_validate_step_valid(self, step, expected):
        range_slider = vm.RangeSlider(min=0, max=10, step=step)

        assert range_slider.step == expected

    def test_validate_step_invalid(self):
        with pytest.raises(
            ValidationError,
            match="The step value of the slider must be less than or equal to the difference between max and min.",
        ):
            vm.RangeSlider(min=0, max=10, step=11)

    @pytest.mark.parametrize(
        "marks, expected",
        [
            ({i: str(i) for i in range(0, 10, 5)}, {i: str(i) for i in range(0, 10, 5)}),
            ({15: 15, 25: 25}, {15.0: "15", 25.0: "25"}),
            ({"15": 15, "25": 25}, {15.0: "15", 25.0: "25"}),
            (None, None),
        ],
    )
    def test_valid_marks(self, marks, expected):
        range_slider = vm.RangeSlider(min=0, max=10, marks=marks)

        assert range_slider.marks == expected

    def test_invalid_marks(self):
        with pytest.raises(ValidationError, match="2 validation errors for RangeSlider"):
            vm.RangeSlider(min=1, max=10, marks={"start": 0, "end": 10})

    @pytest.mark.parametrize("step, expected", [(1, {}), (None, None)])
    def test_set_default_marks(self, step, expected):
        slider = vm.RangeSlider(min=0, max=10, step=step)
        assert slider.marks == expected

    @pytest.mark.parametrize(
        "step, marks, expected_marks, expected_class",
        [
            (1, None, None, "slider-track-without-marks"),
            (None, {}, None, "slider-track-without-marks"),
            (None, None, None, "slider-track-without-marks"),
            (None, {1: "1", 2: "2"}, {1: "1", 2: "2"}, "slider-track-with-marks"),
            (2, {1: "1", 2: "2"}, {1: "1", 2: "2"}, "slider-track-with-marks"),
            # This case might be unintuitive, as the resulting marks are an empty dict. However, marks will
            # be drawn by the dash component, so we need to check for the className here on top.
            (1, {}, {}, "slider-track-with-marks"),
        ],
    )
    def test_set_step_and_marks(self, step, marks, expected_marks, expected_class):
        slider = vm.RangeSlider(min=0, max=10, step=step, marks=marks, id="slider-id").build()
        assert slider["slider-id"].marks == expected_marks
        assert slider["slider-id"].className == expected_class

    @pytest.mark.parametrize("title", ["test", 1, 1.0, """## Test header""", ""])
    def test_valid_title(self, title):
        slider = vm.RangeSlider(title=title)

        assert slider.title == str(title)

    def test_set_action_via_validator(self, identity_action_function):
        range_slider = vm.RangeSlider(actions=[vm.Action(function=identity_action_function())])
        actions_chain = range_slider.actions[0]

        assert actions_chain.trigger.component_property == "value"


class TestRangeSliderBuild:
    """Tests model build method."""

    def test_range_slider_build_default(self, expected_range_slider_default):
        range_slider = vm.RangeSlider(id="range_slider").build()

        assert_component_equal(range_slider, expected_range_slider_default)

    def test_range_slider_build_with_optional(self, expected_range_slider_with_optional):
        range_slider = vm.RangeSlider(
            id="range_slider",
            min=0,
            max=10,
            step=2,
            marks={1: "1", 5: "5", 10: "10"},
            value=[0, 10],
            title="Title",
        ).build()

        assert_component_equal(range_slider, expected_range_slider_with_optional)
