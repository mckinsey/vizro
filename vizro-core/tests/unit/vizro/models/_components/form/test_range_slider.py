"""Unit tests for hyphen.models.slider."""
import json

import plotly
import pytest
from dash import dcc

import vizro.models as vm
from vizro.actions.filter_interaction_action import filter_interaction
from vizro.models._action._actions_chain import ActionsChain
from pydantic import ValidationError


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
            (0, 2, 2, {}, [2, 2], "Test title"),
            (-1, -2, 0.5, {}, [-1, -2], "Test title"),
            (2, 10, 11, {}, None, "Test title")
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
            # (-1, -2, [1, 2]),
        ]
    )
    def test_create_range_slider_invalid_value_options(self, min, max, value, match):
        with pytest.raises(ValidationError, match=match):
            vm.RangeSlider(min=min, max=max, value=value)


class TestRangeSliderBuild:
    """Tests model build method"""

    def test_range_slider_build_default(self):
        range_slider = vm.RangeSlider(id="range_slider")
        component = range_slider.build()

        expected_range_slider = dcc.RangeSlider(
            className="range_slider_control_no_space",
            persistence=True,
            id="range_slider",
            step=None,
            value=[None, None],
            marks=None,
            min=None,
            max=None,
        )

        result = json.loads(json.dumps(component["range_slider"], cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(expected_range_slider, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected
