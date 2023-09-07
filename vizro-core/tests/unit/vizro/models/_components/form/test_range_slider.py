"""Unit tests for hyphen.models.slider."""
import json

import plotly
import pytest
from dash import dcc, html

import vizro.models as vm
from vizro.actions.filter_interaction_action import filter_interaction
from vizro.models._action._actions_chain import ActionsChain
from pydantic import ValidationError


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
                            dcc.Store(id=f"temp-store-range_slider-range_slider", storage_type="local"),
                        ],
                        className="slider_input_container",
                    ),
                ],
                className="range_slider_inner_container",
            ),
        ],
        className="selector_container",
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
                            dcc.Store(id=f"temp-store-range_slider-range_slider", storage_type="local"),
                        ],
                        className="slider_input_container",
                    ),
                ],
                className="range_slider_inner_container",
            ),
        ],
        className="selector_container",
    )


class TestRangeSliderInstantiation:
    """Tests model instantiation"""

    def test_create_range_slider_default(self):
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

    @pytest.mark.parametrize(
        "step, expected",
        [
            (1, {}),
            (None, None)
        ]
    )
    def test_set_default_marks(self, step, expected):
        slider = vm.RangeSlider(min=0, max=10, step=step)
        assert slider.marks == expected

    def test_create_range_slider_with_action(self):
        range_slider = vm.RangeSlider(actions=[vm.Action(function=filter_interaction())])
        range_slider_action = range_slider.actions[0]

        assert len(range_slider.actions) == 1
        assert isinstance(range_slider_action, ActionsChain)
        assert range_slider_action.trigger.component_property == "value"

    @pytest.mark.parametrize(
        "min, max, step, marks, value, title",
        [
            (0, 10, 2, {}, [1, 3], "Test title"),
            (-1, -2, 0.5, {}, [-1, -2], "Test title"),
            (0, 10, 2, {}, None, "!test")
        ]
    )
    def test_create_range_slider_valid_options(self, min, max, step, marks, value, title):
        range_slider = vm.RangeSlider(min=min, max=max, step=step, marks=marks, value=value, title=title)

        assert range_slider.min == min
        assert range_slider.max == max
        assert range_slider.step == step
        assert range_slider.marks == marks
        assert range_slider.value == value
        assert range_slider.title == title


    @pytest.mark.parametrize(
        "min, max, value, match",
        [
            (0, 10, [0], "ensure this value has at least 2 items"),
            (0, 2, [], "ensure this value has at least 2 items"),
            (0, 2, 2, "value is not a valid list")
        ]
    )
    def test_create_range_slider_invalid_value_options(self, min, max, value, match):
        with pytest.raises(ValidationError, match=match):
            vm.RangeSlider(min=min, max=max, value=value)


class TestRangeSliderBuild:
    """Tests model build method"""

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
    """Tests model callback method"""

    @pytest.mark.parametrize(
        "trigger_id, min, max, input_store, value, expected_value",
        [
            ("_start_value", 0, 10, [1, 9], [2, 3], (0, 10, [0, 10], (0, 10))),
            ("_input_store", 0, 10, [1, 9], [2, 3], (1, 9, [1, 9], (1, 9))),
            ("_end_value", 2, 8, [1, 9], [2, 3], (2, 8, [2, 8], (2, 8))),
            ("", 2, 8, [1, 9], [2, 3], (2, 8, [2, 8], (2, 8))),
            ("_start_value", 0, 0, [1, 9], [2, 3], (0, 0, [0, 0], (0, 0))),
            ("_start_value", 0, 10, [1, 9], [-2, 12], (0, 10, [0, 10], (0, 10))),
        ]
    )
    def test_update_slider_value_valid(self, trigger_id, min, max, input_store, value, expected_value):
        range_slider = vm.RangeSlider(min=min, max=max)

        result = range_slider.update_slider_values(
            trigger_id=f"{range_slider.id}{trigger_id}", start=min, end=max, input_store=input_store, value=value, slider=[min, max]
        )
        assert result == expected_value


    def test_update_slider_value_invalid(self):
        pass
