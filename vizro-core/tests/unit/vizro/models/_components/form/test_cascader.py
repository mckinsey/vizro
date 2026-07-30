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
        assert cascader.full_path is False
        assert cascader.title == ""
        assert cascader.description is None
        assert cascader.actions == []
        assert cascader._dynamic is False
        assert cascader._action_triggers == {"__default__": f"{cascader.id}.value"}
        assert cascader._action_outputs == {"__default__": f"{cascader.id}.value"}
        assert cascader._action_inputs == {"__default__": f"{cascader.id}.value"}

    def test_create_cascader_leaf_mandatory_and_optional(self):
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
        assert cascader.full_path is False
        assert cascader.title == "Title"
        assert cascader.actions == []
        assert isinstance(cascader.description, Tooltip)
        assert cascader._action_outputs == {
            "__default__": "cascader-id.value",
            "title": "cascader-id_title.children",
            "description": "tooltip-id-text.children",
        }

    def test_create_cascader_path_mandatory_and_optional(self):
        options = {"Region": {"East": [1, 2], "West": [3]}}
        cascader = Cascader(id="cascader-id", options=options, value=["Region", "East", 2], multi=False, full_path=True)

        assert cascader.value == ["Region", "East", 2]
        assert cascader.multi is False
        assert cascader.full_path is True

    def test_full_path_is_frozen(self):
        cascader = Cascader(options={"L": ["a"]}, value="a", multi=False)
        with pytest.raises(ValidationError, match="frozen"):
            cascader.full_path = True

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
        assert cascader.options == expected
        assert cascader.value is None

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

    # --- Leaf mode (full_path=False, default) -------------------------------------------------------------------

    @pytest.mark.parametrize(
        "test_value, options, multi",
        [
            # Single-select: `value` is a bare leaf scalar.
            ("a", {"L": ["a", "b"]}, False),
            (1, {"N": [1, 2, 3]}, False),
            (2, {"Region": {"East": [1, 2], "West": [3]}}, False),
            # Multi-select: `value` is a list of leaf scalars.
            ([False], {"B": [True, False]}, True),
            (["a", "b"], {"L": ["a", "b", "c"]}, True),
            ([1, 3], {"N": [1, 2, 3]}, True),
        ],
    )
    def test_create_cascader_leaf_valid_value(self, test_value, options, multi):
        cascader = Cascader(options=options, value=test_value, multi=multi)
        assert cascader.value == test_value
        assert cascader.multi == multi

    def test_create_cascader_leaf_multi_scalar_normalized_to_list(self):
        # A bare scalar under multi=True is normalized to a single-element list so the stored value (and the
        # "Reset controls" original value) matches the multi component shape.
        cascader = Cascader(options={"L": ["a", "b"]}, value="a", multi=True)
        assert cascader.value == ["a"]

    @pytest.mark.parametrize(
        "test_value, options, multi",
        [
            # Invalid leaf.
            ("z", {"L": ["a", "b"]}, False),
            (99, {"N": [1, 2, 3]}, False),
            (["a", "z"], {"L": ["a", "b", "c"]}, True),
        ],
    )
    def test_create_cascader_leaf_invalid_value(self, test_value, options, multi):
        with pytest.raises(ValidationError, match=r"Please provide a valid value from `options`."):
            Cascader(value=test_value, options=options, multi=multi)

    def test_create_cascader_leaf_duplicate_leaves_raises(self):
        # In leaf mode, duplicate leaf labels are ambiguous and rejected regardless of value.
        with pytest.raises(ValidationError, match="must not contain duplicate leaf values"):
            Cascader(options={"A": ["x"], "B": ["x"]}, multi=True)

    @pytest.mark.parametrize(
        "test_value, multi, match",
        [
            # A path (list) for a single-select leaf cascader is the wrong shape.
            (["L", "a"], False, "expects a leaf value"),
            # A list of paths for a multi-select leaf cascader is the wrong shape.
            ([["L", "a"]], True, "expects a list of leaf values"),
        ],
    )
    def test_create_cascader_leaf_rejects_path_shape(self, test_value, multi, match):
        with pytest.raises(ValidationError, match=match):
            Cascader(value=test_value, options={"L": ["a", "b"]}, multi=multi)

    # --- Path mode (full_path=True) -----------------------------------------------------------------------------

    @pytest.mark.parametrize(
        "test_value, options, multi",
        [
            # Single-select: `value` is one root-to-leaf path.
            (["L", "a"], {"L": ["a", "b"]}, False),
            (["Region", "East", 2], {"Region": {"East": [1, 2], "West": [3]}}, False),
            # Multi-select: `value` is a list of paths.
            ([["L", "a"], ["L", "b"]], {"L": ["a", "b", "c"]}, True),
            ([["N", 1], ["N", 3]], {"N": [1, 2, 3]}, True),
            # Duplicate leaf labels across branches select independently via their full path.
            (["A", "x"], {"A": ["x"], "B": ["x"]}, False),
            ([["A", "x"], ["B", "x"]], {"A": ["x"], "B": ["x"]}, True),
        ],
    )
    def test_create_cascader_path_valid_value(self, test_value, options, multi):
        cascader = Cascader(options=options, value=test_value, multi=multi, full_path=True)
        assert cascader.value == test_value
        assert cascader.multi == multi
        assert cascader.full_path is True

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
    def test_create_cascader_path_invalid_value(self, test_value, options):
        multi = isinstance(test_value[0], list)
        with pytest.raises(ValidationError, match=r"Please provide a valid value from `options`."):
            Cascader(value=test_value, options=options, multi=multi, full_path=True)

    @pytest.mark.parametrize(
        "test_value, multi, match",
        [
            # A bare leaf scalar for a single-select path cascader is the wrong shape.
            ("a", False, "expects a full root-to-leaf path"),
            # A list of bare leaves for a multi-select path cascader is the wrong shape.
            (["a", "b"], True, "not bare leaves"),
        ],
    )
    def test_create_cascader_path_rejects_leaf_shape(self, test_value, multi, match):
        with pytest.raises(ValidationError, match=match):
            Cascader(value=test_value, options={"L": ["a", "b"]}, multi=multi, full_path=True)

    def test_create_cascader_path_list_of_paths_single_select_raises(self):
        with pytest.raises(ValidationError, match=r"Please set multi=True if providing a list of paths."):
            Cascader(value=[["N", 1], ["N", 2]], multi=False, full_path=True, options={"N": [1, 2, 3, 4, 5]})

    def test_create_cascader_path_allows_duplicate_leaves(self):
        cascader = Cascader(options={"A": ["x"], "B": ["x"]}, multi=True, full_path=True)
        assert cascader.options == {"A": ["x"], "B": ["x"]}

    # --- Mode-agnostic ------------------------------------------------------------------------------------------

    def test_create_cascader_empty_list_value_passthrough(self):
        # An empty list means "no selection" and passes through unchanged (not filled with a default).
        cascader = Cascader(value=[], options={"L": ["a", "b"]}, multi=True)
        assert cascader.value == []

    def test_create_cascader_leaf_coerces_datetime_leaves_to_date(self):
        ts = pd.Timestamp("2024-03-30")
        cascader = Cascader(options={"Asia": [ts]}, value=ts, multi=True)
        assert cascader.options == {"Asia": [date(2024, 3, 30)]}
        # Leaf coerced to date like the options leaves, and the bare multi scalar normalized to a list.
        assert cascader.value == [date(2024, 3, 30)]

    def test_create_cascader_path_coerces_datetime_leaves_to_date(self):
        ts = pd.Timestamp("2024-03-30")
        cascader = Cascader(options={"Asia": [ts]}, value=[["Asia", ts]], multi=True, full_path=True)
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
        "options, multi, full_path, expected",
        [
            # Leaf mode: single takes first leaf, multi takes the list of leaves under the first root key.
            ({"K": [10, 20, 30]}, False, False, 10),
            ({"K": [10, 20, 30]}, True, False, [10, 20, 30]),
            ({"Outer": {"Inner": [7, 8]}}, False, False, 7),
            ({"Outer": {"Inner": [7, 8]}}, True, False, [7, 8]),
            # Path mode: single takes the first path, multi takes all paths under the first root key.
            ({"K": [10, 20, 30]}, False, True, ["K", 10]),
            ({"K": [10, 20, 30]}, True, True, [["K", 10], ["K", 20], ["K", 30]]),
            ({"Outer": {"Inner": [7, 8]}}, False, True, ["Outer", "Inner", 7]),
            ({"Outer": {"Inner": [7, 8]}}, True, True, [["Outer", "Inner", 7], ["Outer", "Inner", 8]]),
        ],
    )
    def test_get_cascader_default_value(self, options, multi, full_path, expected):
        assert get_cascader_default_value(options, multi=multi, full_path=full_path) == expected


class TestCascaderBuild:
    """Tests model build method."""

    def test_cascader_build_leaf_single(self):
        options = {"Region": {"East": [1, 2], "West": [3]}}
        built = Cascader(id="cascader_id", options=options, multi=False, title="Title", value=None).build()
        expected = html.Div(
            [
                dbc.Label([html.Span("Title", id="cascader_id_title"), None], html_for="cascader_id"),
                vdc.Cascader(
                    id="cascader_id",
                    options=options,
                    # value=None fills the first leaf by default (mirrors Dropdown).
                    value=1,
                    multi=False,
                    full_path=False,
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                    clearable=False,
                ),
            ]
        )
        assert_component_equal(built, expected)

    def test_cascader_build_path_single(self):
        options = {"Region": {"East": [1, 2], "West": [3]}}
        built = Cascader(
            id="cascader_id", options=options, multi=False, title="Title", value=None, full_path=True
        ).build()
        expected = html.Div(
            [
                dbc.Label([html.Span("Title", id="cascader_id_title"), None], html_for="cascader_id"),
                vdc.Cascader(
                    id="cascader_id",
                    options=options,
                    value=["Region", "East", 1],
                    multi=False,
                    full_path=True,
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
                    value="a",
                    multi=False,
                    full_path=False,
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
                dbc.Label([html.Span("Title", id="cascader_id_title"), *expected_description], html_for="cascader_id"),
                vdc.Cascader(
                    id="cascader_id",
                    options=options,
                    value="a",
                    multi=False,
                    full_path=False,
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                    clearable=False,
                ),
            ]
        )
        assert_component_equal(built, expected)

    def test_cascader_build_no_title_leaf_multi(self):
        options = {"L": ["a"]}
        built = Cascader(id="cascader_id", options=options, title="").build()
        expected = html.Div(
            [
                None,
                vdc.Cascader(
                    id="cascader_id",
                    options=options,
                    # multi=True default value is a list of leaves.
                    value=["a"],
                    multi=True,
                    full_path=False,
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                    clearable=True,
                ),
            ]
        )
        assert_component_equal(built, expected)

    def test_cascader_build_leaf_multi_wraps_scalar(self):
        # A bare scalar under multi=True is wrapped into a single-element list in __call__.
        options = {"L": ["a", "b"]}
        built = Cascader(id="cascader_id", options=options, multi=True, value="a", title="").build()
        expected = html.Div(
            [
                None,
                vdc.Cascader(
                    id="cascader_id",
                    options=options,
                    value=["a"],
                    multi=True,
                    full_path=False,
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                    clearable=True,
                ),
            ]
        )
        assert_component_equal(built, expected)

    @pytest.mark.parametrize(
        "value, multi, full_path",
        [
            (2, False, False),
            ([1, 3], True, False),
            (["Region", "East", 2], False, True),
            ([["Region", "East", 2], ["Region", "West", 3]], True, True),
        ],
    )
    def test_cascader_value_json_round_trip(self, value, multi, full_path):
        # The `value` survives a model_dump()/reconstruct round-trip (guards the widened field, both modes).
        options = {"Region": {"East": [1, 2], "West": [3]}}
        cascader = Cascader(options=options, value=value, multi=multi, full_path=full_path)
        dumped = cascader.model_dump()
        rebuilt = Cascader(
            options=dumped["options"], value=dumped["value"], multi=dumped["multi"], full_path=dumped["full_path"]
        )
        assert rebuilt.value == cascader.value == value


class TestCascaderCall:
    """Tests model __call__ method — the runtime rebuild entry point used by Filter.__call__ on dynamic reloads."""

    def test_cascader_call_uses_supplied_options_leaf(self):
        cascader = Cascader(id="cascader_id", options={"L": ["a"]}, multi=False, value=None, title="")
        new_options = {"Region": {"East": [1, 2], "West": [3]}}
        built = cascader(new_options)
        expected = html.Div(
            [
                None,
                vdc.Cascader(
                    id="cascader_id",
                    options=new_options,
                    # value=None fills the first leaf from the supplied options.
                    value=1,
                    multi=False,
                    full_path=False,
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
        cascader = Cascader(id="cascader_id", options=options, multi=False, value="a", title="Title")
        assert_component_equal(cascader.build(), cascader(options))
