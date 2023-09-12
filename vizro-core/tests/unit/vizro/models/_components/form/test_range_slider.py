"""Unit tests for hyphen.models.slider."""
import json

import plotly
import pytest
from dash import dcc, html
from pydantic import ValidationError

import vizro.models as vm


@pytest.fixture()
def expected_range_slider_default():
    return html.Div(
        [
            None,
            html.Div(
                [
                    dcc.RangeSlider(
                        id="range_slider",
                        className="range_slider_control_no_space",
                        persistence=True,
                        min=None,
                        max=None,
                        marks=None,
                        value=[None, None],
                        step=None,
                    ),
                    html.Div(
                        [
                            dcc.Input(
                                id="range_slider_start_value",
                                type="number",
                                placeholder="start",
                                className="slider_input_field_no_space_left",
                                size="24px",
                                persistence=True,
                                min=None,
                                max=None,
                                value=None,
                            ),
                            dcc.Input(
                                id="range_slider_end_value",
                                type="number",
                                placeholder="end",
                                className="slider_input_field_no_space_right",
                                persistence=True,
                                min=None,
                                max=None,
                                value=None,
                            ),
                            dcc.Store(id="temp-store-range_slider-range_slider", storage_type="local"),
                        ],
                        className="slider_input_container",
                    ),
                ],
                className="range_slider_inner_container",
            ),
        ],
        className="selector_container",
        id="range_slider_outer"
    )


@pytest.fixture()
def expected_range_slider_with_optional():
    return html.Div(
        [
            html.P("Title", id="range_slider_title"),
            html.Div(
                [
                    dcc.RangeSlider(
                        id="range_slider",
                        min=0,
                        max=10,
                        step=1,
                        marks={},
                        className="range_slider_control",
                        value=[0, 10],
                        persistence=True,
                    ),
                    html.Div(
                        [
                            dcc.Input(
                                id="range_slider_start_value",
                                type="number",
                                placeholder="start",
                                min=0,
                                max=10,
                                className="slider_input_field_left",
                                value=0,
                                size="24px",
                                persistence=True,
                            ),
                            dcc.Input(
                                id="range_slider_end_value",
                                type="number",
                                placeholder="end",
                                min=0,
                                max=10,
                                className="slider_input_field_right",
                                value=10,
                                persistence=True,
                            ),
                            dcc.Store(id="temp-store-range_slider-range_slider", storage_type="local"),
                        ],
                        className="slider_input_container",
                    ),
                ],
                className="range_slider_inner_container",
            ),
        ],
        className="selector_container",
        id="range_slider_outer"
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
        assert range_slider.title is None
        assert range_slider.actions == []

    def test_create_range_slider_mandatory_and_optional(self):
        range_slider = vm.RangeSlider(min=0, max=10, step=1, marks={}, value=[1, 9], title="Test title")

        assert range_slider.min == 0
        assert range_slider.max == 10
        assert range_slider.step == 1
        assert range_slider.value == [1, 9]
        assert range_slider.title == "Test title"
        assert range_slider.actions == []

    @pytest.mark.parametrize(
        "min, max",
        [
            (0, None),
            (None, 10),
            (0, 10),
        ],
    )
    def test_valid_min_max(self, min, max):
        range_slider = vm.RangeSlider(min=min, max=max)
        min = int(min) if isinstance(min, str) else min
        max = int(max) if isinstance(max, str) else max

        assert range_slider.min == min
        assert range_slider.max == max

    def test_invalid_min_max(self):
        with pytest.raises(
            ValidationError, match="Maximum value of slider is required to be larger than minimum value."
        ):
            vm.RangeSlider(min=10, max=0)

    @pytest.mark.parametrize("value", [None, [1, 2], [0.1, 1.1], [-10, 10], [10, 10]])
    def test_valid_value(self, value):
        range_slider = vm.RangeSlider(min=-10, max=10, value=value)

        assert range_slider.value == value

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
    def test_invalid_value(self, value, match):
        with pytest.raises(ValidationError, match=match):
            vm.RangeSlider(min=0, max=10, value=value)

    @pytest.mark.parametrize(
        "step",
        [1, 2.5, 10, None],
    )
    def test_valid_step(self, step):
        range_slider = vm.RangeSlider(min=0, max=10, step=step)

        assert range_slider.step == step

    def test_invalid_step(self):
        with pytest.raises(ValidationError, match="The step value of the slider must be less than the max value."):
            vm.RangeSlider(min=0, max=10, step=11)

    @pytest.mark.parametrize(
        "marks, step, expected_marks",
        [
            ({2: "2", 4: "4", 6: "6"}, 1, {}),
            ({2: "2", 4: "4", 6: "6"}, None, {2: "2", 4: "4", 6: "6"}),
            ({}, 1, {}),
        ],
    )
    def test_step_precedence_over_marks(self, marks, step, expected_marks):
        slider = vm.RangeSlider(min=0, max=10, marks=marks, step=step)

        assert slider.marks == expected_marks
        assert slider.step == step

    @pytest.mark.parametrize(
        "marks, expected",
        [
            ({i: str(i) for i in range(0, 10, 5)}, {i: str(i) for i in range(0, 10, 5)}),
            ({15: 15, 25: 25}, {15.0: "15", 25.0: "25"}),
            (None, None),
        ],
    )
    def test_valid_marks(self, marks, expected):
        range_slider = vm.RangeSlider(min=0, max=10, marks=marks)

        assert range_slider.marks == expected

    def test_invalid_marks(self):
        with pytest.raises(
            ValidationError,
            match="2 validation errors for RangeSlider",
        ):
            vm.RangeSlider(min=1, max=10, marks={"start": 0, "end": 10})

    @pytest.mark.parametrize("step, expected", [(1, {}), (None, None)])
    def test_set_default_marks(self, step, expected):
        slider = vm.RangeSlider(min=0, max=10, step=step)
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
        slider = vm.RangeSlider(title=title)

        assert slider.title == str(title)

    def test_set_action_via_validator(self, test_action_function):
        range_slider = vm.RangeSlider(actions=[vm.Action(function=test_action_function)])
        actions_chain = range_slider.actions[0]

        assert actions_chain.trigger.component_property == "value"


class TestRangeSliderBuild:
    """Tests model build method."""

    def test_range_slider_build_default(self, expected_range_slider_default):
        range_slider = vm.RangeSlider(id="range_slider")
        component = range_slider.build()

        result = json.loads(json.dumps(component, cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(expected_range_slider_default, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected

    def test_range_slider_build_with_optional(self, expected_range_slider_with_optional):
        range_slider = vm.RangeSlider(min=0, max=10, step=1, value=[0, 10], id="range_slider", title="Title")
        component = range_slider.build()

        result = json.loads(json.dumps(component, cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(expected_range_slider_with_optional, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected


class TestCallbackMethod:
    """Tests model callback method."""

    @pytest.mark.parametrize(
        "trigger_id, min, max, input_store, value, expected_value",
        [
            ("_start_value", 0, 10, [1, 9], [2, 3], (0, 10, [0, 10], (0, 10))),
            ("_input_store", 0, 10, [1, 9], [2, 3], (1, 9, [1, 9], (1, 9))),
            ("_end_value", 2, 8, [1, 9], [2, 3], (2, 8, [2, 8], (2, 8))),
            ("", 2, 8, [1, 9], [2, 3], (2, 8, [2, 8], (2, 8))),
            ("_start_value", 0, 0, [1, 9], [2, 3], (0, 0, [0, 0], (0, 0))),
            ("_start_value", 0, 10, [1, 9], [-2, 12], (0, 10, [0, 10], (0, 10))),
        ],
    )
    def test_update_slider_value_valid(self, trigger_id, min, max, input_store, value, expected_value):
        range_slider = vm.RangeSlider(min=min, max=max)

        result = range_slider._update_slider_values(
            trigger_id=f"{range_slider.id}{trigger_id}",
            start=min,
            end=max,
            input_store=input_store,
            value=value,
            slider=[min, max],
        )
        assert result == expected_value

    @pytest.mark.parametrize(
        "trigger, start_value, end_value, slider_value, input_store_value",
        [
            ("_text_value", None, 9, [1, 9], [1, 9]),
        ],
    )
    def test_update_slider_invalid(self, trigger, start_value, end_value, slider_value, input_store_value):
        range_slider = vm.RangeSlider(min=start_value, max=10, value=[1, 9])

        with pytest.raises(
            TypeError,
            match="'>' not supported between instances of 'int' and 'NoneType'",
        ):
            range_slider._update_slider_values(
                trigger_id=f"{range_slider.id}{trigger}",
                start=start_value,
                slider=slider_value,
                input_store=input_store_value,
                value=[1, 9],
                end=end_value,
            )
