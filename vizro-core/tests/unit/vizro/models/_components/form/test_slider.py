"""Unit tests for hyphen.models.slider."""
import json

import plotly
import pytest
from dash import dcc, html
from pydantic import ValidationError

import vizro.models as vm


@pytest.fixture()
def expected_slider():
    return html.Div(
        [
            dcc.Store(
                "slider_id_callback_data",
                data={
                    "id": "slider_id",
                    "min": 0,
                    "max": 10,
                },
            ),
            html.P("Test title"),
            html.Div(
                [
                    dcc.Slider(
                        id="slider_id",
                        min=0,
                        max=10,
                        step=1,
                        marks={},
                        value=5,
                        included=False,
                        persistence=True,
                        className="slider_control",
                    ),
                    dcc.Input(
                        id="slider_id_text_value",
                        type="number",
                        placeholder="end",
                        min=0,
                        step=1,
                        max=10,
                        value=5,
                        persistence=True,
                        className="slider_input_field_right",
                    ),
                    dcc.Store(id="slider_id_temp_store", storage_type="local"),
                ],
                className="slider_inner_container",
            ),
        ],
        className="selector_container",
        id="slider_id_outer",
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
        assert slider.title is None
        assert slider.actions == []

    @pytest.mark.parametrize(
        "min, max",
        [
            (0, None),
            (None, 10),
            (0, 10),
        ],
    )
    def test_valid_min_max(self, min, max):
        slider = vm.Slider(min=min, max=max)

        assert slider.min == min
        assert slider.max == max

    def test_validate_max_invalid(self):
        with pytest.raises(
            ValidationError,
            match="Maximum value of slider is required to be larger than minimum value.",
        ):
            vm.Slider(min=10, max=0)

    @pytest.mark.parametrize(
        "value",
        [
            5,
            -5,
            0,
            6.5,
            -10,
            10,
        ],
    )
    def test_validate_slider_value_valid(self, value):
        slider = vm.Slider(min=-10, max=10, value=value)

        assert slider.value == value

    @pytest.mark.parametrize(
        "value",
        [
            11,
            -1,
        ],
    )
    def test_validate_slider_value_invalid(self, value):
        with pytest.raises(
            ValidationError,
            match="Please provide a valid value between the min and max value.",
        ):
            vm.Slider(min=0, max=10, value=value)

    @pytest.mark.parametrize(
        "step, expected",
        [(1, 1), (2.5, 2.5), (10, 10), (None, None), ("1", 1.0)],
    )
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
        with pytest.raises(
            ValidationError,
            match="2 validation errors for Slider",
        ):
            vm.Slider(min=1, max=10, marks={"start": 0, "end": 10})

    @pytest.mark.parametrize("step, expected", [(1, {}), (None, None)])
    def test_set_default_marks(self, step, expected):
        slider = vm.Slider(min=0, max=10, step=step)
        assert slider.marks == expected

    @pytest.mark.parametrize(
        "step, marks, expected",
        [
            (1, None, None),
            (None, {1: "1", 2: "2"}, {1: "1", 2: "2"}),
            (2, {1: "1", 2: "2"}, {1: "1", 2: "2"}),
            (None, {}, None),
        ],
    )
    def test_set_step_and_marks(self, step, marks, expected):
        slider = vm.Slider(min=0, max=10, step=step, marks=marks)
        assert slider.marks == expected

    @pytest.mark.parametrize(
        "title",
        [
            "test",
            1,
            1.0,
            """## Test header""",
            "",
        ],
    )
    def test_valid_title(self, title):
        slider = vm.Slider(title=title)

        assert slider.title == str(title)

    def test_set_action_via_validator(self, test_action_function):
        slider = vm.Slider(actions=[vm.Action(function=test_action_function)])
        actions_chain = slider.actions[0]

        assert actions_chain.trigger.component_property == "value"


class TestBuildMethod:
    def test_slider_build(self, expected_slider):
        slider = vm.Slider(min=0, max=10, step=1, value=5, id="slider_id", title="Test title")
        slider = slider.build()

        result = json.loads(json.dumps(slider, cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(expected_slider, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected
