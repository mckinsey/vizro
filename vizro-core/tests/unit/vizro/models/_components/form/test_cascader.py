"""Unit tests for vizro.models.Cascader."""

import dash_bootstrap_components as dbc
import pytest
import vizro_dash_components as vdc
from asserts import assert_component_equal
from dash import html
from pydantic import ValidationError

from vizro.models import Tooltip
from vizro.models._action._action import Action
from vizro.models._components.form import Cascader
from vizro.models._components.form.cascader import (
    _iter_cascader_leaves_depth_first,
    get_cascader_default_value,
)


class TestCascaderInstantiation:
    """Tests model instantiation."""

    def test_cascader_empty_options_allowed_for_deferred_fill(self):
        cascader = Cascader(options={})
        assert cascader.options == {}

    def test_get_cascader_default_value_empty_options_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            get_cascader_default_value({}, multi=False)

    def test_create_cascader_mandatory_only(self):
        cascader = Cascader(options={"L": ["a"]})

        assert hasattr(cascader, "id")
        assert cascader.type == "cascader"
        assert cascader.options == {"L": ["a"]}
        assert cascader.value is None
        assert cascader.multi is True
        assert cascader.title == ""
        assert cascader.description is None
        assert cascader.actions == []
        assert cascader._action_triggers == {"__default__": f"{cascader.id}.value"}
        assert cascader._action_outputs == {"__default__": f"{cascader.id}.value"}
        assert cascader._action_inputs == {"__default__": f"{cascader.id}.value"}

    def test_create_cascader_mandatory_and_optional(self):
        options = {"Region": {"East": [1, 2], "West": [3]}}
        cascader = Cascader(
            id="cascader-id",
            options=options,
            value=2,
            multi=False,
            title="Title",
            description=Tooltip(id="tooltip-id", text="Test description", icon="info"),
        )

        assert cascader.id == "cascader-id"
        assert cascader.type == "cascader"
        assert cascader.options == options
        assert cascader.value == 2
        assert cascader.multi is False
        assert cascader.title == "Title"
        assert cascader.actions == []
        assert isinstance(cascader.description, Tooltip)
        assert cascader._action_triggers == {"__default__": "cascader-id.value"}
        assert cascader._action_outputs == {
            "__default__": "cascader-id.value",
            "title": "cascader-id_title.children",
            "description": "tooltip-id-text.children",
        }
        assert cascader._action_inputs == {"__default__": "cascader-id.value"}

    @pytest.mark.parametrize(
        "test_options, expected",
        [
            ({"R": [1, 2]}, {"R": [1, 2]}),
            ({"R": {"S": [True]}}, {"R": {"S": [True]}}),
            ({"A": ["x"], "B": ["y"]}, {"A": ["x"], "B": ["y"]}),
        ],
    )
    def test_create_cascader_valid_options(self, test_options, expected):
        cascader = Cascader(options=test_options)

        assert hasattr(cascader, "id")
        assert cascader.type == "cascader"
        assert cascader.options == expected
        assert cascader.value is None
        assert cascader.multi is True
        assert cascader.title == ""
        assert cascader.actions == []

    @pytest.mark.parametrize(
        "test_options, match",
        [
            ([], "nested dictionary"),
            ({"x": []}, "empty leaf list"),
            ({"x": 1}, "nested dict or a list of scalars"),
            ({"x": {}}, "at least one leaf"),
            ({"x": [{"a": 1}]}, "scalar values"),
            ({"R": ["a", "a"]}, "duplicate leaf"),
            ({"A": ["x"], "B": ["x"]}, "duplicate leaf"),
        ],
    )
    def test_create_cascader_invalid_options(self, test_options, match):
        with pytest.raises(ValidationError, match=match):
            Cascader(options=test_options)

    @pytest.mark.parametrize(
        "test_value, options, multi",
        [
            ("a", {"L": ["a", "b"]}, False),
            (1, {"N": [1, 2, 3]}, False),
            (False, {"B": [True, False]}, True),
            ("b", {"L": ["a", "b"]}, True),
            (["a", "b"], {"L": ["a", "b", "c"]}, True),
            ([1, 3], {"N": [1, 2, 3]}, True),
        ],
    )
    def test_create_cascader_valid_value(self, test_value, options, multi):
        cascader = Cascader(options=options, value=test_value, multi=multi)

        assert hasattr(cascader, "id")
        assert cascader.type == "cascader"
        assert cascader.value == test_value
        assert cascader.multi == multi
        assert cascader.title == ""
        assert cascader.actions == []

    @pytest.mark.parametrize(
        "test_value, options",
        [
            ("z", {"L": ["a", "b"]}),
            (99, {"N": [1, 2, 3]}),
            (["a", "z"], {"L": ["a", "b", "c"]}),
        ],
    )
    def test_create_cascader_invalid_value(self, test_value, options):
        with pytest.raises(ValidationError, match=r"Please provide a valid value from `options`."):
            Cascader(value=test_value, options=options)

    def test_create_cascader_invalid_multi(self):
        with pytest.raises(ValidationError, match=r"Please set multi=True if providing a list of default values."):
            Cascader(value=[1, 2], multi=False, options={"N": [1, 2, 3, 4, 5]})

    def test_cascader_trigger(self, identity_action_function):
        cascader = Cascader(
            id="cascader-id",
            options={"L": ["a"]},
            actions=[Action(function=identity_action_function())],
        )
        [action] = cascader.actions
        assert action._trigger == "cascader-id.value"


class TestCascaderHelpers:
    """Tests module-level helpers used by parameters and validation."""

    def test_iter_cascader_leaves_depth_first_order(self):
        options = {"A": [1, 2], "B": [3]}
        assert _iter_cascader_leaves_depth_first(options) == [1, 2, 3]

    @pytest.mark.parametrize(
        "options, multi, expected",
        [
            ({"K": [10, 20, 30]}, False, 10),
            ({"K": [10, 20, 30]}, True, [10, 20, 30]),
            ({"Outer": {"Inner": [7, 8]}}, False, 7),
            ({"Outer": {"Inner": [7, 8]}}, True, [7, 8]),
        ],
    )
    def test_get_cascader_default_value(self, options, multi, expected):
        assert get_cascader_default_value(options, multi=multi) == expected


class TestCascaderBuild:
    """Tests model build method."""

    def test_cascader_build(self):
        options = {"Region": {"East": [1, 2], "West": [3]}}
        built = Cascader(id="cascader_id", options=options, multi=False, title="Title", value=None).build()
        expected = html.Div(
            [
                dbc.Label(
                    [html.Span("Title", id="cascader_id_title"), None],
                    html_for="cascader_id",
                ),
                vdc.Cascader(
                    id="cascader_id",
                    options=options,
                    value=None,
                    multi=False,
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                    clearable=False,
                ),
            ]
        )
        assert_component_equal(built, expected)

    def test_cascader_build_with_extra(self):
        options = {"L": ["a", "b", "c"]}
        built = Cascader(
            options=options,
            title="Title",
            id="cascader_id",
            multi=False,
            extra={"clearable": True, "id": "overridden_id"},
        ).build()
        expected = html.Div(
            [
                dbc.Label([html.Span("Title", id="cascader_id_title"), None], html_for="cascader_id"),
                vdc.Cascader(
                    id="overridden_id",
                    options=options,
                    value=None,
                    multi=False,
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                    clearable=True,
                ),
            ]
        )
        assert_component_equal(built, expected)

    def test_cascader_with_description(self):
        options = {"L": ["a", "b", "c"]}
        built = Cascader(
            options=options,
            multi=False,
            title="Title",
            id="cascader_id",
            description=Tooltip(text="Test description", icon="Info", id="info"),
        ).build()

        expected_description = [
            html.Span("info", id="info-icon", className="material-symbols-outlined tooltip-icon"),
            dbc.Tooltip(
                children=vdc.Markdown("Test description", id="info-text", className="card-text"),
                id="info",
                target="info-icon",
                autohide=False,
            ),
        ]

        expected = html.Div(
            [
                dbc.Label(
                    [html.Span("Title", id="cascader_id_title"), *expected_description],
                    html_for="cascader_id",
                ),
                vdc.Cascader(
                    id="cascader_id",
                    options=options,
                    value=None,
                    multi=False,
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                    clearable=False,
                ),
            ]
        )
        assert_component_equal(built, expected)

    def test_cascader_build_no_title(self):
        options = {"L": ["a"]}
        built = Cascader(id="cascader_id", options=options, title="").build()
        expected = html.Div(
            [
                None,
                vdc.Cascader(
                    id="cascader_id",
                    options=options,
                    value=None,
                    multi=True,
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                    clearable=True,
                ),
            ]
        )
        assert_component_equal(built, expected)

    def test_cascader_build_multi_coerces_scalar_value_to_list(self):
        options = {"L": ["a", "b"]}
        built = Cascader(id="cascader_id", options=options, multi=True, value="b", title="").build()
        expected = html.Div(
            [
                None,
                vdc.Cascader(
                    id="cascader_id",
                    options=options,
                    value=["b"],
                    multi=True,
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                    clearable=True,
                ),
            ]
        )
        assert_component_equal(built, expected)
