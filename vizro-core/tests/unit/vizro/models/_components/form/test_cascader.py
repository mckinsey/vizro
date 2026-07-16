"""Unit tests for vizro.models.Cascader."""

from datetime import date

import dash_bootstrap_components as dbc
import pandas as pd
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
        assert cascader._dynamic is False
        assert cascader._action_triggers == {"__default__": f"{cascader.id}.value"}
        assert cascader._action_outputs == {"__default__": f"{cascader.id}.value"}
        assert cascader._action_inputs == {"__default__": f"{cascader.id}.value"}

    def test_create_cascader_mandatory_and_optional(self):
        options = {"Region": {"East": [1, 2], "West": [3]}}
        cascader = Cascader(
            id="cascader-id",
            options=options,
            value=["Region", "East", 2],
            multi=False,
            title="Title",
            description=Tooltip(id="tooltip-id", text="Test description", icon="info"),
        )

        assert cascader.id == "cascader-id"
        assert cascader.type == "cascader"
        assert cascader.options == options
        assert cascader.value == ["Region", "East", 2]
        assert cascader.multi is False
        assert cascader.title == "Title"
        assert cascader.actions == []
        assert isinstance(cascader.description, Tooltip)
        assert cascader._dynamic is False
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
            # Duplicate leaf labels across branches are allowed: each selection is addressed by full path.
            ({"A": ["x"], "B": ["x"]}, {"A": ["x"], "B": ["x"]}),
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
        ],
    )
    def test_create_cascader_invalid_options(self, test_options, match):
        with pytest.raises(ValidationError, match=match):
            Cascader(options=test_options)

    @pytest.mark.parametrize(
        "test_value, options, multi",
        [
            # Single-select: `value` is one root-to-leaf path.
            (["L", "a"], {"L": ["a", "b"]}, False),
            (["N", 1], {"N": [1, 2, 3]}, False),
            (["Region", "East", 2], {"Region": {"East": [1, 2], "West": [3]}}, False),
            # Multi-select: `value` is a list of paths.
            ([["B", False]], {"B": [True, False]}, True),
            ([["L", "b"]], {"L": ["a", "b"]}, True),
            ([["L", "a"], ["L", "b"]], {"L": ["a", "b", "c"]}, True),
            ([["N", 1], ["N", 3]], {"N": [1, 2, 3]}, True),
            # Duplicate leaf labels across branches select independently via their full path.
            (["A", "x"], {"A": ["x"], "B": ["x"]}, False),
            ([["A", "x"], ["B", "x"]], {"A": ["x"], "B": ["x"]}, True),
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
            # Invalid leaf under a valid branch.
            (["L", "z"], {"L": ["a", "b"]}),
            (["N", 99], {"N": [1, 2, 3]}),
            # Non-existent branch.
            (["X", "a"], {"L": ["a", "b", "c"]}),
            # A list of paths where one path is invalid.
            ([["L", "a"], ["L", "z"]], {"L": ["a", "b", "c"]}),
        ],
    )
    def test_create_cascader_invalid_value(self, test_value, options):
        with pytest.raises(ValidationError, match=r"Please provide a valid value from `options`."):
            Cascader(value=test_value, options=options)

    def test_create_cascader_invalid_multi(self):
        with pytest.raises(ValidationError, match=r"Please set multi=True if providing a list of paths."):
            Cascader(value=[["N", 1], ["N", 2]], multi=False, options={"N": [1, 2, 3, 4, 5]})

    def test_create_cascader_coerces_datetime_leaves_to_date(self):
        ts = pd.Timestamp("2024-03-30")
        cascader = Cascader(options={"Asia": [ts]}, value=[["Asia", ts]], multi=True)
        assert cascader.options == {"Asia": [date(2024, 3, 30)]}
        assert cascader.value == [["Asia", date(2024, 3, 30)]]

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
            ({"K": [10, 20, 30]}, False, ["K", 10]),
            ({"K": [10, 20, 30]}, True, [["K", 10], ["K", 20], ["K", 30]]),
            ({"Outer": {"Inner": [7, 8]}}, False, ["Outer", "Inner", 7]),
            ({"Outer": {"Inner": [7, 8]}}, True, [["Outer", "Inner", 7], ["Outer", "Inner", 8]]),
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
                    # value=None fills the first leaf's full path by default (mirrors Dropdown).
                    value=["Region", "East", 1],
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
                    value=["L", "a"],
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
                    value=["L", "a"],
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
                    # multi=True default value is a list of paths.
                    value=[["L", "a"]],
                    multi=True,
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                    clearable=True,
                ),
            ]
        )
        assert_component_equal(built, expected)

    def test_cascader_build_multi_coerces_legacy_leaves_to_paths(self):
        # Under multi=True a flat scalar list is the legacy list-of-leaves form; each leaf resolves to its path.
        options = {"L": ["a", "b"]}
        built = Cascader(id="cascader_id", options=options, multi=True, value=["a", "b"], title="").build()
        expected = html.Div(
            [
                None,
                vdc.Cascader(
                    id="cascader_id",
                    options=options,
                    value=[["L", "a"], ["L", "b"]],
                    multi=True,
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                    clearable=True,
                ),
            ]
        )
        assert_component_equal(built, expected)

    def test_cascader_build_multi_passes_list_of_paths_through(self):
        # An already-correctly-shaped list-of-paths value passes straight through unchanged.
        options = {"L": ["a", "b", "c"]}
        built = Cascader(
            id="cascader_id", options=options, multi=True, value=[["L", "a"], ["L", "c"]], title=""
        ).build()
        expected = html.Div(
            [
                None,
                vdc.Cascader(
                    id="cascader_id",
                    options=options,
                    value=[["L", "a"], ["L", "c"]],
                    multi=True,
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                    clearable=True,
                ),
            ]
        )
        assert_component_equal(built, expected)

    @pytest.mark.parametrize(
        "value, multi",
        [
            (["Region", "East", 2], False),
            ([["Region", "East", 2], ["Region", "West", 3]], True),
        ],
    )
    def test_cascader_value_json_round_trip(self, value, multi):
        # The path-shaped `value` survives a model_dump()/reconstruct round-trip (guards the widened field).
        options = {"Region": {"East": [1, 2], "West": [3]}}
        cascader = Cascader(options=options, value=value, multi=multi)
        dumped = cascader.model_dump()
        rebuilt = Cascader(options=dumped["options"], value=dumped["value"], multi=dumped["multi"])
        assert rebuilt.value == cascader.value == value


class TestCascaderCall:
    """Tests model __call__ method — the runtime rebuild entry point used by Filter.__call__ on dynamic reloads."""

    def test_cascader_call_uses_supplied_options(self):
        cascader = Cascader(id="cascader_id", options={"L": ["a"]}, multi=False, value=None, title="")
        new_options = {"Region": {"East": [1, 2], "West": [3]}}
        built = cascader(new_options)
        expected = html.Div(
            [
                None,
                vdc.Cascader(
                    id="cascader_id",
                    options=new_options,
                    # value=None fills the first leaf's full path from the supplied options.
                    value=["Region", "East", 1],
                    multi=False,
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                    clearable=False,
                ),
            ]
        )
        assert_component_equal(built, expected)

    def test_cascader_build_equals_call_with_self_options(self):
        # build() delegates to __call__(self.options); guard that they produce equivalent output.
        options = {"L": ["a", "b"]}
        cascader = Cascader(id="cascader_id", options=options, multi=False, value=["L", "a"], title="Title")
        assert_component_equal(cascader.build(), cascader(options))
