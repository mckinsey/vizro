"""Unit tests for hyphen.models.slider."""

import dash_bootstrap_components as dbc
import pytest
import vizro_dash_components as vdc
from asserts import assert_component_equal
from dash import dcc, html
from pydantic import ValidationError

import vizro.models as vm


@pytest.fixture()
def expected_slider():
    return html.Div(
        [
            dbc.Label([html.Span("Title", id="slider_id_title"), None], html_for="slider_id"),
            dcc.Slider(
                id="slider_id",
                min=0.0,
                max=10.0,
                step=1.0,
                marks={0.0: "0", 10.0: "10"},
                value=5.0,
                persistence=True,
                persistence_type="session",
                dots=True,
            ),
        ]
    )


@pytest.fixture()
def expected_slider_with_marks_none():
    return html.Div(
        [
            dbc.Label([html.Span("Title", id="slider_id_title"), None], html_for="slider_id"),
            dcc.Slider(
                id="slider_id",
                min=0.0,
                max=10.0,
                step=1.0,
                marks=None,
                value=5.0,
                persistence=True,
                persistence_type="session",
                dots=True,
            ),
        ]
    )


@pytest.fixture()
def expected_slider_with_extra():
    return html.Div(
        [
            dbc.Label([html.Span("Title", id="slider_id_title"), None], html_for="slider_id"),
            dcc.Slider(
                id="overridden_id",
                min=0.0,
                max=10.0,
                step=1.0,
                marks={0.0: "0", 10.0: "10"},
                value=5.0,
                persistence=True,
                persistence_type="session",
                dots=True,
                tooltip={"placement": "bottom", "always_visible": True},
            ),
        ]
    )


@pytest.fixture()
def expected_slider_with_description():
    expected_description = [
        html.Span("info", id="info-icon", className="material-symbols-outlined tooltip-icon"),
        dbc.Tooltip(
            children=vdc.Markdown("Test description", id="info-text", className="card-text"),
            id="info",
            target="info-icon",
            autohide=False,
        ),
    ]
    return html.Div(
        [
            dbc.Label(
                [html.Span("Title", id="slider_id_title"), *expected_description],
                html_for="slider_id",
            ),
            dcc.Slider(
                id="slider_id",
                min=0.0,
                max=10.0,
                step=1.0,
                marks={0.0: "0", 10.0: "10"},
                value=5.0,
                persistence=True,
                persistence_type="session",
                dots=True,
            ),
        ]
    )


class TestSliderInstantiation:
    """Tests model instantiation."""

    def test_create_slider_mandatory_only(self):
        slider = vm.Slider()

        assert hasattr(slider, "id")
        assert slider.type == "slider"
        assert slider.step is None
        assert slider.min is None
        assert slider.max is None
        assert slider.marks == {}
        assert slider.value is None
        assert slider.title == ""
        assert slider.description is None
        assert slider.actions == []
        assert slider._action_triggers == {"__default__": f"{slider.id}.value"}
        assert slider._action_outputs == {"__default__": f"{slider.id}.value"}
        assert slider._action_inputs == {"__default__": f"{slider.id}.value"}

    def test_create_slider_mandatory_and_optional(self):
        slider = vm.Slider(
            id="slider_id",
            min=0,
            max=10,
            step=1,
            marks={1: "1", 5: "5", 10: "10"},
            value=1,
            title="Title",
            description=vm.Tooltip(id="tooltip-id", text="Test description", icon="info"),
        )
        assert slider.id == "slider_id"
        assert slider.type == "slider"
        assert slider.min == 0
        assert slider.max == 10
        assert slider.value == 1
        assert slider.step == 1
        assert slider.marks == {1: "1", 5: "5", 10: "10"}
        assert slider.title == "Title"
        assert slider.actions == []
        assert isinstance(slider.description, vm.Tooltip)
        assert slider._action_triggers == {"__default__": "slider_id.value"}
        assert slider._action_outputs == {
            "__default__": "slider_id.value",
            "title": "slider_id_title.children",
            "description": "tooltip-id-text.children",
        }
        assert slider._action_inputs == {"__default__": "slider_id.value"}

    @pytest.mark.parametrize("min, max", [(0, None), (None, 10), (0, 10)])
    def test_valid_min_max(self, min, max):
        slider = vm.Slider(min=min, max=max)

        assert slider.min == min
        assert slider.max == max

    def test_validate_max_invalid(self):
        with pytest.raises(
            ValidationError, match=r"Maximum value of selector is required to be larger than minimum value."
        ):
            vm.Slider(min=10, max=0)

    @pytest.mark.parametrize("value", [5, -5, 0, 6.5, -10, 10])
    def test_validate_slider_value_valid(self, value):
        slider = vm.Slider(min=-10, max=10, value=value)

        assert slider.value == value

    @pytest.mark.parametrize("value", [11, -1])
    def test_validate_slider_value_invalid(self, value):
        with pytest.raises(ValidationError, match=r"Please provide a valid value between the min and max value."):
            vm.Slider(min=0, max=10, value=value)

    @pytest.mark.parametrize("step, expected", [(1, 1), (2.5, 2.5), (10, 10), (None, None), ("1", 1.0)])
    def test_validate_step_valid(self, step, expected):
        slider = vm.Slider(min=0, max=10, step=step)

        assert slider.step == expected

    @pytest.mark.parametrize("min, max", [(None, 10), (0, None), (None, None)])
    def test_validate_step_without_min_or_max(self, min, max):
        # There is nothing to compare the step against unless both bounds are given.
        slider = vm.Slider(min=min, max=max, step=1)

        assert slider.step == 1

    def test_validate_step_invalid(self):
        with pytest.raises(
            ValidationError,
            match=r"The step value of the slider must be less than or equal to the difference between max and min.",
        ):
            vm.Slider(min=0, max=10, step=11)

    @pytest.mark.parametrize(
        "marks, expected",
        [
            (None, None),
            ({0: "0", 1: "1", 2: "2"}, {0: "0", 1: "1", 2: "2"}),  # int - str
            ({1.0: "1.0", 1.5: "1.5"}, {1: "1.0", 1.5: "1.5"}),  # float - str
        ],
    )
    def test_valid_marks(self, marks, expected):
        slider = vm.Slider(min=0, max=10, marks=marks)
        assert slider.marks == expected

    @pytest.mark.parametrize("title", ["test", """## Test header""", ""])
    def test_valid_title(self, title):
        slider = vm.Slider(title=title)

        assert slider.title == str(title)

    def test_slider_trigger(self, identity_action_function):
        slider = vm.Slider(id="slider-id", actions=[vm.Action(function=identity_action_function())])
        [action] = slider.actions
        assert action._trigger == "slider-id.value"


class TestBuildMethod:
    def test_slider_build(self, expected_slider):
        slider = vm.Slider(id="slider_id", min=0, max=10, step=1, value=5, title="Title").build()

        assert_component_equal(slider, expected_slider)

    def test_slider_build_with_marks_none(self, expected_slider_with_marks_none):
        slider = vm.Slider(id="slider_id", min=0, max=10, step=1, value=5, title="Title", marks=None).build()

        assert_component_equal(slider, expected_slider_with_marks_none)

    def test_slider_build_with_extra(self, expected_slider_with_extra):
        """Test that extra arguments correctly override defaults."""
        slider = vm.Slider(
            id="slider_id",
            min=0,
            max=10,
            step=1,
            value=5,
            title="Title",
            extra={
                "tooltip": {"placement": "bottom", "always_visible": True},
                "id": "overridden_id",
            },
        ).build()

        assert_component_equal(slider, expected_slider_with_extra)

    def test_slider_build_with_description(self, expected_slider_with_description):
        slider = vm.Slider(
            id="slider_id",
            min=0,
            max=10,
            step=1,
            value=5,
            title="Title",
            description=vm.Tooltip(text="Test description", icon="Info", id="info"),
        ).build()

        assert_component_equal(slider, expected_slider_with_description)


class TestSliderGetValueFromTrigger:
    """Tests _get_value_from_trigger models method."""

    @pytest.mark.parametrize("trigger", [5, None])
    def test_get_value_from_trigger_returns_trigger(self, trigger):
        # A selector already holds the value to propagate, so _get_value_from_trigger ignores `value` and returns the
        # raw trigger value unchanged (this is what powers syncing controls that target another control).
        slider = vm.Slider()
        assert slider._get_value_from_trigger(value="ignored", trigger=trigger) == trigger


class TestSliderRange:
    """Tests for Slider(range=True), which replaces the deprecated RangeSlider."""

    def test_range_defaults_to_false(self):
        assert vm.Slider().range is False

    def test_range_true_builds_range_slider(self):
        slider = vm.Slider(id="s", min=0, max=10, range=True)
        component = slider.build().children[1]
        assert isinstance(component, dcc.RangeSlider)
        assert component.value == [0, 10]

    def test_range_false_builds_slider(self):
        component = vm.Slider(id="s", min=0, max=10).build().children[1]
        assert isinstance(component, dcc.Slider)
        assert not isinstance(component, dcc.RangeSlider)

    def test_range_true_with_list_value(self):
        assert vm.Slider(min=0, max=10, value=[2, 8], range=True).value == [2, 8]

    def test_range_true_inner_component_properties(self):
        # dcc.RangeSlider exposes extra properties (allowCross, count, pushable) that must be forwardable.
        assert "allowCross" in vm.Slider(range=True)._inner_component_properties
        assert "allowCross" not in vm.Slider()._inner_component_properties

    def test_list_value_without_range_raises(self):
        with pytest.raises(ValidationError, match="Please set range=True if providing a list of values"):
            vm.Slider(min=0, max=10, value=[2, 8])

    def test_single_value_with_range_raises(self):
        with pytest.raises(ValidationError, match="Please set range=False if providing a single value"):
            vm.Slider(min=0, max=10, value=5, range=True)

    def test_value_reassignment_enforces_range_shape(self):
        # The value/range consistency check must also run on assignment (validate_assignment=True), not only at
        # construction, so a scalar cannot leak into a range slider (or a list into a single-handle slider). The check
        # runs in "before" mode, so a rejected assignment must leave the original value untouched (no partial mutation).
        slider = vm.Slider(min=0, max=10, value=[2, 8], range=True)
        with pytest.raises(ValidationError, match="Please set range=False if providing a single value"):
            slider.value = 5
        assert slider.value == [2, 8]

        slider = vm.Slider(min=0, max=10, value=3)
        with pytest.raises(ValidationError, match="Please set range=True if providing a list of values"):
            slider.value = [2, 8]
        assert slider.value == 3

    def test_range_reassignment_enforces_range_shape(self):
        # Flipping `range` so it no longer matches the current `value` is rejected, and the rejected assignment must not
        # mutate the model (range stays as it was).
        slider = vm.Slider(min=0, max=10, value=3)
        with pytest.raises(ValidationError, match="Please set range=False if providing a single value"):
            slider.range = True
        assert slider.range is False
        assert slider.value == 3
