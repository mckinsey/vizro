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
def expected_slider():
    return html.Div(
        [
            dcc.Store(id="slider_id_callback_data", data={"id": "slider_id", "min": 0.0, "max": 10.0}),
            html.Div(
                [
                    dbc.Label("Test title", html_for="slider_id"),
                    html.Div(
                        [
                            dcc.Input(
                                id="slider_id_end_value",
                                type="number",
                                placeholder="max",
                                min=0.0,
                                max=10.0,
                                step=1.0,
                                value=5.0,
                                persistence=True,
                                persistence_type="session",
                                className="slider-text-input-field",
                            ),
                            dcc.Store(id="slider_id_input_store", storage_type="session", data=5.0),
                        ],
                        className="slider-text-input-container",
                    ),
                ],
                className="slider-label-input",
            ),
            dcc.Slider(
                id="slider_id",
                min=0.0,
                max=10.0,
                step=1.0,
                marks={},
                value=5.0,
                included=False,
                persistence=True,
                persistence_type="session",
                className="slider-track-with-marks",
            ),
        ]
    )


class TestSliderInstantiation:
    """Tests model instantiation."""

    def test_create_slider_mandatory(self):
        slider = vm.Slider()

        assert hasattr(slider, "id")
        assert slider.type == "slider"
        assert slider.step is None
        assert slider.min is None
        assert slider.max is None
        assert slider.marks is None
        assert slider.value is None
        assert slider.title == ""
        assert slider.actions == []

    @pytest.mark.parametrize("min, max", [(0, None), (None, 10), (0, 10)])
    def test_valid_min_max(self, min, max):
        slider = vm.Slider(min=min, max=max)

        assert slider.min == min
        assert slider.max == max

    def test_validate_max_invalid(self):
        with pytest.raises(
            ValidationError, match="Maximum value of selector is required to be larger than minimum value."
        ):
            vm.Slider(min=10, max=0)

    @pytest.mark.parametrize("value", [5, -5, 0, 6.5, -10, 10])
    def test_validate_slider_value_valid(self, value):
        slider = vm.Slider(min=-10, max=10, value=value)

        assert slider.value == value

    @pytest.mark.parametrize("value", [11, -1])
    def test_validate_slider_value_invalid(self, value):
        with pytest.raises(ValidationError, match="Please provide a valid value between the min and max value."):
            vm.Slider(min=0, max=10, value=value)

    @pytest.mark.parametrize("step, expected", [(1, 1), (2.5, 2.5), (10, 10), (None, None), ("1", 1.0)])
    def test_validate_step_valid(self, step, expected):
        slider = vm.Slider(min=0, max=10, step=step)

        assert slider.step == expected

    def test_validate_step_invalid(self):
        with pytest.raises(
            ValidationError,
            match="The step value of the slider must be less than or equal to the difference between max and min.",
        ):
            vm.Slider(min=0, max=10, step=11)

    def test_valid_marks_with_step(self):
        slider = vm.Slider(min=0, max=10, step=2)

        assert slider.marks == {}

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
        slider = vm.Slider(min=0, max=10, marks=marks)

        assert slider.marks == expected

    def test_invalid_marks(self):
        with pytest.raises(ValidationError, match="2 validation errors for Slider"):
            vm.Slider(min=1, max=10, marks={"start": 0, "end": 10})

    @pytest.mark.parametrize("step, expected", [(1, {}), (None, None)])
    def test_set_default_marks(self, step, expected):
        slider = vm.Slider(min=0, max=10, step=step)
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
        slider = vm.Slider(min=0, max=10, step=step, marks=marks, id="slider-id").build()
        assert slider["slider-id"].marks == expected_marks
        assert slider["slider-id"].className == expected_class

    @pytest.mark.parametrize("title", ["test", 1, 1.0, """## Test header""", ""])
    def test_valid_title(self, title):
        slider = vm.Slider(title=title)

        assert slider.title == str(title)

    def test_set_action_via_validator(self, identity_action_function):
        slider = vm.Slider(actions=[vm.Action(function=identity_action_function())])
        actions_chain = slider.actions[0]

        assert actions_chain.trigger.component_property == "value"


class TestBuildMethod:
    def test_slider_build(self, expected_slider):
        slider = vm.Slider(id="slider_id", min=0, max=10, step=1, value=5, title="Test title").build()

        assert_component_equal(slider, expected_slider)
