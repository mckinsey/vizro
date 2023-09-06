"""Unit tests for hyphen.models.slider."""
import json

import plotly
import pytest
from dash import dcc

import vizro.models as vm
from vizro.actions import export_data
from vizro.models._action._actions_chain import ActionsChain


class TestSliderInstantiation:
    """Tests model instantiation."""

    def test_create_default_slider(self):
        slider = vm.Slider()

        assert hasattr(slider, "id")
        assert slider.type == "slider"
        assert slider.min is None
        assert slider.max is None
        assert slider.step is None
        assert slider.marks is None
        assert slider.value is None
        assert slider.title is None
        assert slider.actions == []

    @pytest.mark.parametrize(
        "min, max, step, marks, value, title",
        [
            (0, 10, 1, {}, 3, "Test text"),
            (100, 200, 50, {}, 100, """## Test header"""),
            (1.23, 6.78, 0.01, {}, None, 1.23),
            (10, 0, 1, {}, None, True),  # reverse order
            (0, 10, None, {str(i): i for i in range(0, 10, 1)}, 5, ""),  # add marks
        ],
    )
    def test_create_slider_with_optional(self, min, max, step, marks, value, title):  # noqa
        slider = vm.Slider(min=min, max=max, step=step, marks=marks, value=value, title=title)

        assert slider.min == min
        assert slider.max == max
        assert slider.step == step
        assert slider.marks == marks
        assert slider.value == value
        assert slider.title == str(title)

    def test_set_default_marks(self):
        slider = vm.Slider(min=0, max=10, step=1)
        assert slider.marks == {}

    def test_create_slider_with_action(self):
        slider = vm.Slider(actions=[vm.Action(function=export_data())])
        slider_tac = slider.actions[0]
        assert hasattr(slider, "id")
        assert slider.type == "slider"
        assert len(slider.actions) == 1
        assert isinstance(slider_tac, ActionsChain)
        assert slider_tac.trigger.component_property == "value"


class TestBuildMethod:
    def test_slider_build(self):
        slider = vm.Slider(id="slider_id", title="Test title")
        component = slider.build()

        expected_slider = dcc.Slider(
            included=False, className="slider_control_no_space", id="slider_id", persistence=True
        )

        result = json.loads(json.dumps(component["slider_id"], cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(expected_slider, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected
        assert component["slider_title"].children == "Test title"


class TestCallbackMethod:
    @pytest.mark.parametrize(
        "trigger, start_value, slider_value, input_store_value, expected_value",
        [
            ("_text_value", 3, 1, 1, 3),  # set new value by start
            ("", 1, 4, 1, 4),  # set new value by slider
            ("_input_store", 1, 1, 5, 5),  # set new value by input store
            ("_text_value", 0, 1, 1, 0),  # set to minimum value
            ("_text_value", 12, 1, 1, 10),  # set outside of possible range
            ("_text_value", -1, 1, 1, 0),  # set outside of possible range
            ("_text_value", 1, 8, 1, 1),  # triggerdID value is only used
        ],
    )
    def test_update_slider_value_triggered(  # noqa
        self, trigger, start_value, slider_value, input_store_value, expected_value
    ):
        slider = vm.Slider(min=0, max=10, value=1)
        result = slider.update_slider_value(f"{slider.id}{trigger}", start_value, slider_value, input_store_value)

        assert result == (expected_value,) * 3

    @pytest.mark.parametrize(
        "trigger, start_value, slider_value, input_store_value, expected_value",
        [
            ("_text_value", 3, 1, 1, 0),  # set new value by start
        ],
    )
    def test_update_slider_reversed(  # noqa
        self, trigger, start_value, slider_value, input_store_value, expected_value
    ):
        slider = vm.Slider(min=10, max=0, value=1)
        result = slider.update_slider_value(f"{slider.id}{trigger}", start_value, slider_value, input_store_value)

        assert result == (expected_value,) * 3

    @pytest.mark.parametrize(
        "trigger, start_value, slider_value, input_store_value",
        [
            ("_text_value", None, 1, 1),  # set new value by start
        ],
    )
    def test_update_slider_invalid(self, trigger, start_value, slider_value, input_store_value):
        slider = vm.Slider(min=10, max=0, value=1)

        with pytest.raises(TypeError, match="'>' not supported between instances of 'NoneType' and 'float'"):
            slider.update_slider_value(f"{slider.id}{trigger}", start_value, slider_value, input_store_value)
