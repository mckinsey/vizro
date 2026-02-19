"""Unit tests for hyphen.models.slider."""

import dash_bootstrap_components as dbc
import pytest
from asserts import assert_component_equal
from dash import dcc, html
from pydantic import ValidationError

import vizro.models as vm


@pytest.fixture()
def expected_range_slider_default():
    return html.Div(
        [
            None,
            dcc.RangeSlider(
                id="range_slider",
                min=None,
                max=None,
                marks={},
                dots=True,
                value=[None, None],
                persistence=True,
                persistence_type="session",
            ),
        ]
    )


@pytest.fixture()
def expected_range_slider_with_optional():
    return html.Div(
        [
            dbc.Label([html.Span("Title", id="range_slider_title"), None], html_for="range_slider"),
            dcc.RangeSlider(
                id="range_slider",
                min=0.0,
                max=10.0,
                step=2.0,
                marks={1.0: "1", 5.0: "5", 10.0: "10"},
                value=[0, 10],
                persistence=True,
                persistence_type="session",
                dots=True,
            ),
        ]
    )


@pytest.fixture()
def expected_range_slider_with_extra():
    return html.Div(
        [
            dbc.Label([html.Span("Title", id="range_slider_title"), None], html_for="range_slider"),
            dcc.RangeSlider(
                id="overridden_id",
                min=0.0,
                max=10.0,
                step=2.0,
                marks={1.0: "1", 5.0: "5", 10.0: "10"},
                value=[0, 10],
                persistence=True,
                persistence_type="session",
                dots=True,
                tooltip={"placement": "bottom", "always_visible": True},
                pushable=20,
            ),
        ]
    )


@pytest.fixture()
def expected_range_slider_with_description():
    expected_description = [
        html.Span("info", id="info-icon", className="material-symbols-outlined tooltip-icon"),
        dbc.Tooltip(
            children=dcc.Markdown("Test description", id="info-text", className="card-text"),
            id="info",
            target="info-icon",
            autohide=False,
        ),
    ]
    return html.Div(
        [
            dbc.Label(
                [html.Span("Title", id="range_slider_title"), *expected_description],
                html_for="range_slider",
            ),
            dcc.RangeSlider(
                id="range_slider",
                min=0.0,
                max=10.0,
                step=2.0,
                marks={1.0: "1", 5.0: "5", 10.0: "10"},
                value=[0, 10],
                dots=True,
                persistence=True,
                persistence_type="session",
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
        assert range_slider.marks == {}
        assert range_slider.value is None
        assert range_slider.title == ""
        assert range_slider.description is None
        assert range_slider.actions == []
        assert range_slider._action_triggers == {"__default__": f"{range_slider.id}.value"}
        assert range_slider._action_outputs == {"__default__": f"{range_slider.id}.value"}
        assert range_slider._action_inputs == {"__default__": f"{range_slider.id}.value"}

    def test_create_range_slider_mandatory_and_optional(self):
        range_slider = vm.RangeSlider(
            id="range_slider_id",
            min=0,
            max=10,
            step=1,
            marks={1: "1", 5: "5", 10: "10"},
            value=[1, 9],
            title="Test title",
            description=vm.Tooltip(id="tooltip-id", text="Test description", icon="info"),
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
        assert isinstance(range_slider.description, vm.Tooltip)
        assert range_slider._action_triggers == {"__default__": "range_slider_id.value"}
        assert range_slider._action_outputs == {
            "__default__": "range_slider_id.value",
            "title": "range_slider_id_title.children",
            "description": "tooltip-id-text.children",
        }
        assert range_slider._action_inputs == {"__default__": "range_slider_id.value"}

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
            ValidationError, match=r"Maximum value of selector is required to be larger than minimum value."
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
            ([0], "List should have at least 2 items after validation"),
            ([], "List should have at least 2 items after validation"),
            (2, "Input should be a valid list"),
            ([0, None], "Input should be a valid number"),
            ([None, None], "2 validation errors for RangeSlider"),
            ([-1, 11], "Please provide a valid value between the min and max value."),
            ([1, 2, 3], "List should have at most 2 items after validation, not 3"),
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
            match=r"The step value of the slider must be less than or equal to the difference between max and min.",
        ):
            vm.RangeSlider(min=0, max=10, step=11)

    @pytest.mark.parametrize(
        "marks, expected",
        [
            (None, None),
            ({0: "0", 1: "1", 2: "2"}, {0: "0", 1: "1", 2: "2"}),  # int - str
            ({1.0: "1.0", 1.5: "1.5"}, {1: "1.0", 1.5: "1.5"}),  # float - str
        ],
    )
    def test_valid_marks(self, marks, expected):
        range_slider = vm.RangeSlider(min=0, max=10, marks=marks)
        assert range_slider.marks == expected

    @pytest.mark.parametrize("title", ["test", """## Test header""", ""])
    def test_valid_title(self, title):
        slider = vm.RangeSlider(title=title)

        assert slider.title == str(title)

    def test_range_slider_trigger(self, identity_action_function):
        range_slider = vm.Slider(id="range-slider-id", actions=[vm.Action(function=identity_action_function())])
        [action] = range_slider.actions
        assert action._trigger == "range-slider-id.value"


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

    def test_range_slider_build_with_extra(self, expected_range_slider_with_extra):
        """Test that extra arguments correctly override defaults."""
        range_slider = vm.RangeSlider(
            id="range_slider",
            min=0.0,
            max=10.0,
            step=2,
            marks={1: "1", 5: "5", 10: "10"},
            value=[0, 10],
            title="Title",
            extra={
                "tooltip": {"placement": "bottom", "always_visible": True},
                "pushable": 20,
                "id": "overridden_id",
            },
        ).build()

        assert_component_equal(range_slider, expected_range_slider_with_extra)

    def test_range_slider_build_with_description(self, expected_range_slider_with_description):
        """Test that description arguments correctly builds icon and tooltip."""
        range_slider = vm.RangeSlider(
            id="range_slider",
            min=0.0,
            max=10.0,
            step=2,
            marks={1: "1", 5: "5", 10: "10"},
            value=[0, 10],
            title="Title",
            description=vm.Tooltip(text="Test description", icon="Info", id="info"),
        ).build()

        assert_component_equal(range_slider, expected_range_slider_with_description)
