"""Unit tests for hyphen.models.slider."""

import dash_bootstrap_components as dbc
import pytest
from asserts import assert_component_equal
from dash import dcc, html
from pydantic import ValidationError

import vizro.models as vm


@pytest.fixture()
def expected_slider():
    return html.Div(
        [
            dcc.Store(id="slider_id_callback_data", data={"id": "slider_id", "min": 0.0, "max": 10.0}),
            html.Div(
                [
                    dbc.Label([html.Span("Title", id="slider_id_title"), None], html_for="slider_id"),
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
                            dcc.Store(id="slider_id_input_store", storage_type="session"),
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


@pytest.fixture()
def expected_slider_extra():
    return html.Div(
        [
            dcc.Store(id="slider_id_callback_data", data={"id": "slider_id", "min": 0.0, "max": 10.0}),
            html.Div(
                [
                    dbc.Label([html.Span("Title", id="slider_id_title"), None], html_for="slider_id"),
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
                            dcc.Store(id="slider_id_input_store", storage_type="session"),
                        ],
                        className="slider-text-input-container",
                    ),
                ],
                className="slider-label-input",
            ),
            dcc.Slider(
                id="overridden_id",
                min=0.0,
                max=10.0,
                step=1.0,
                marks={},
                value=5.0,
                included=False,
                persistence=True,
                persistence_type="session",
                className="slider-track-with-marks",
                tooltip={"placement": "bottom", "always_visible": True},
            ),
        ]
    )


@pytest.fixture()
def expected_slider_with_description():
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
            dcc.Store(id="slider_id_callback_data", data={"id": "slider_id", "min": 0.0, "max": 10.0}),
            html.Div(
                [
                    dbc.Label(
                        [html.Span("Title", id="slider_id_title"), *expected_description],
                        html_for="slider_id",
                    ),
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
                            dcc.Store(id="slider_id_input_store", storage_type="session"),
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

    def test_create_slider_mandatory_only(self):
        slider = vm.Slider()

        assert hasattr(slider, "id")
        assert slider.type == "slider"
        assert slider.step is None
        assert slider.min is None
        assert slider.max is None
        assert slider.marks is None
        assert slider.value is None
        assert slider.title == ""
        assert slider.description is None
        assert slider.actions == []
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
            description="Test description",
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
        assert slider._action_outputs == {
            "__default__": f"{slider.id}.value",
            "title": f"{slider.id}_title.children",
            "description": f"{slider.description.id}-text.children",
        }
        assert slider._action_inputs == {"__default__": f"{slider.id}.value"}

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
            # TODO[MS]: why is this not failing, should it not be converted to float?
            ({i: str(i) for i in range(0, 10, 5)}, {i: str(i) for i in range(0, 10, 5)}),  # int - str
            ({1.0: "1", 1.5: "1.5"}, {1: "1", 1.5: "1.5"}),  # float - str (but see validator)
            (None, None),
        ],
    )
    def test_valid_marks(self, marks, expected):
        slider = vm.Slider(min=0, max=10, marks=marks)
        assert slider.marks == expected

        if marks:
            assert [type(result_key) for result_key in slider.marks] == [
                type(expected_key) for expected_key in expected
            ]

    def test_invalid_marks(self):
        with pytest.raises(ValidationError, match="4 validation errors for Slider"):
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

    @pytest.mark.parametrize("title", ["test", """## Test header""", ""])
    def test_valid_title(self, title):
        slider = vm.Slider(title=title)

        assert slider.title == str(title)

    def test_set_action_via_validator(self, identity_action_function):
        slider = vm.Slider(actions=[vm.Action(function=identity_action_function())])
        actions_chain = slider.actions[0]

        assert actions_chain.trigger.component_property == "value"


class TestBuildMethod:
    def test_slider_build(self, expected_slider):
        slider = vm.Slider(id="slider_id", min=0, max=10, step=1, value=5, title="Title").build()

        assert_component_equal(slider, expected_slider)

    def test_slider_build_with_extra(self, expected_slider_extra):
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

        assert_component_equal(slider, expected_slider_extra)

    def test_slider_build_with_description(self, expected_slider_with_description):
        slider = vm.Slider(
            id="slider_id",
            min=0,
            max=10,
            step=1,
            value=5,
            title="Title",
            description=vm.Tooltip(text="Test description", icon="info", id="info"),
        ).build()

        assert_component_equal(slider, expected_slider_with_description)
