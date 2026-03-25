"""Unit tests for vizro.models.TreeSelect."""

import dash_bootstrap_components as dbc
import feffery_antd_components as fac
import pytest
from asserts import assert_component_equal
from dash import dcc, html
from pydantic import ValidationError

from vizro.models import Tooltip
from vizro.models._action._action import Action
from vizro.models._components.form import TreeSelect
from vizro.models._components.form.tree_select import _convert_options, _extract_leaf_keys

SIMPLE_OPTIONS = {"Fruits": ["Apple", "Banana"], "Vegetables": ["Carrot"]}
NESTED_OPTIONS = {
    "Electronics": {
        "Phones": ["iPhone", "Android"],
        "Laptops": ["MacBook"],
    }
}


class TestTreeSelectInstantiation:
    """Tests model instantiation."""

    def test_create_tree_select_mandatory_only(self):
        ts = TreeSelect(options=SIMPLE_OPTIONS)

        assert hasattr(ts, "id")
        assert ts.type == "tree_select"
        assert ts.multi is True
        assert ts.value is None
        assert ts.title == ""
        assert ts.description is None
        assert ts.actions == []
        assert ts.extra == {}

    def test_create_tree_select_mandatory_and_optional(self):
        ts = TreeSelect(
            id="tree-select-id",
            options=SIMPLE_OPTIONS,
            value=["Apple"],
            multi=True,
            title="Title",
        )

        assert ts.id == "tree-select-id"
        assert ts.type == "tree_select"
        assert ts.options == SIMPLE_OPTIONS
        assert ts.value == ["Apple"]
        assert ts.title == "Title"
        assert ts.actions == []

    def test_create_tree_select_no_args(self):
        ts = TreeSelect()
        assert ts.options == {}
        assert ts.value is None

    def test_duplicate_leaf_values_raises(self):
        with pytest.raises(ValidationError, match="Duplicate leaf values"):
            TreeSelect(options={"France": ["Bruges"], "Belgium": ["Bruges"]})

    def test_valid_flat_options(self):
        ts = TreeSelect(options={"A": ["x", "y"]})
        assert ts.options == {"A": ["x", "y"]}

    def test_valid_nested_options(self):
        ts = TreeSelect(options=NESTED_OPTIONS)
        assert ts.options == NESTED_OPTIONS

    def test_empty_options(self):
        ts = TreeSelect(options={})
        assert ts.options == {}

    def test_invalid_options_not_dict(self):
        with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
            TreeSelect(options=["a", "b"])

    def test_invalid_options_non_string_leaf(self):
        with pytest.raises(ValidationError, match="Leaf values must be strings"):
            TreeSelect(options={"A": [1, 2]})

    def test_invalid_options_invalid_value_type(self):
        with pytest.raises(ValidationError):
            TreeSelect(options={"A": 42})

    def test_valid_value(self):
        ts = TreeSelect(options=SIMPLE_OPTIONS, value=["Apple"])
        assert ts.value == ["Apple"]

    def test_valid_value_nested(self):
        ts = TreeSelect(options=NESTED_OPTIONS, value=["iPhone", "MacBook"])
        assert ts.value == ["iPhone", "MacBook"]

    def test_invalid_value_not_in_options(self):
        with pytest.raises(ValidationError, match="valid value from `options`"):
            TreeSelect(options=SIMPLE_OPTIONS, value=["NotAFruit"])

    def test_multi_false_with_single_value(self):
        ts = TreeSelect(options=SIMPLE_OPTIONS, value="Apple", multi=False)
        assert ts.value == "Apple"

    def test_multi_false_with_list_value_raises(self):
        with pytest.raises(ValidationError, match="multi=True"):
            TreeSelect(options=SIMPLE_OPTIONS, value=["Apple"], multi=False)

    def test_valid_single_value(self):
        ts = TreeSelect(options=SIMPLE_OPTIONS, value="Apple", multi=False)
        assert ts.value == "Apple"

    def test_invalid_single_value_not_in_options(self):
        with pytest.raises(ValidationError, match="valid value from `options`"):
            TreeSelect(options=SIMPLE_OPTIONS, value="NotAFruit", multi=False)

    def test_action_triggers(self):
        ts = TreeSelect(id="tree-select-id", options=SIMPLE_OPTIONS)
        assert ts._action_triggers == {"__default__": "tree-select-id.value"}

    def test_action_outputs_no_title(self):
        ts = TreeSelect(id="tree-select-id", options=SIMPLE_OPTIONS)
        assert ts._action_outputs == {"__default__": "tree-select-id.value"}

    def test_action_outputs_with_title(self):
        ts = TreeSelect(id="tree-select-id", options=SIMPLE_OPTIONS, title="My Title")
        assert ts._action_outputs == {
            "__default__": "tree-select-id.value",
            "title": "tree-select-id_title.children",
        }

    def test_action_inputs(self):
        ts = TreeSelect(id="tree-select-id", options=SIMPLE_OPTIONS)
        assert ts._action_inputs == {"__default__": "tree-select-id.value"}

    def test_tree_select_trigger(self, identity_action_function):
        ts = TreeSelect(
            id="tree-select-id", options=SIMPLE_OPTIONS, actions=[Action(function=identity_action_function())]
        )
        [action] = ts.actions
        assert action._trigger == "tree-select-id.value"


class TestTreeSelectBuild:
    """Tests model build method."""

    def test_build_no_title(self):
        ts = TreeSelect(id="tree_select_id", options=SIMPLE_OPTIONS)
        result = ts.build()
        expected = html.Div(
            children=[
                None,
                fac.AntdTreeSelect(
                    id="tree_select_id",
                    treeData=_convert_options(SIMPLE_OPTIONS),
                    value=[],
                    treeCheckable=True,
                    multiple=True,
                    allowClear=True,
                    showCheckedStrategy="show-child",
                    maxTagCount="responsive",
                    listHeight=300,
                    locale="en-us",
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                ),
            ]
        )
        assert_component_equal(result, expected)

    def test_build_with_title(self):
        ts = TreeSelect(id="tree_select_id", options=SIMPLE_OPTIONS, title="Pick a fruit")
        result = ts.build()
        expected = html.Div(
            children=[
                dbc.Label(
                    children=[html.Span(id="tree_select_id_title", children="Pick a fruit"), None],
                    html_for="tree_select_id",
                ),
                fac.AntdTreeSelect(
                    id="tree_select_id",
                    treeData=_convert_options(SIMPLE_OPTIONS),
                    value=[],
                    treeCheckable=True,
                    multiple=True,
                    allowClear=True,
                    showCheckedStrategy="show-child",
                    maxTagCount="responsive",
                    listHeight=300,
                    locale="en-us",
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                ),
            ]
        )
        assert_component_equal(result, expected)

    def test_build_multi_false(self):
        ts = TreeSelect(id="tree_select_id", options=SIMPLE_OPTIONS, multi=False)
        result = ts.build()
        expected = html.Div(
            children=[
                None,
                fac.AntdTreeSelect(
                    id="tree_select_id",
                    treeData=_convert_options(SIMPLE_OPTIONS),
                    value=None,
                    treeCheckable=False,
                    multiple=False,
                    allowClear=False,
                    listHeight=300,
                    locale="en-us",
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                ),
            ]
        )
        assert_component_equal(result, expected)

    def test_build_with_value(self):
        ts = TreeSelect(id="tree_select_id", options=SIMPLE_OPTIONS, value=["Apple"])
        result = ts.build()
        expected = html.Div(
            children=[
                None,
                fac.AntdTreeSelect(
                    id="tree_select_id",
                    treeData=_convert_options(SIMPLE_OPTIONS),
                    value=["Apple"],
                    treeCheckable=True,
                    multiple=True,
                    allowClear=True,
                    showCheckedStrategy="show-child",
                    maxTagCount="responsive",
                    listHeight=300,
                    locale="en-us",
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                ),
            ]
        )
        assert_component_equal(result, expected)

    def test_build_with_description(self):
        ts = TreeSelect(
            id="tree_select_id",
            options=SIMPLE_OPTIONS,
            title="Pick a fruit",
            description=Tooltip(text="Test description", icon="Info", id="info"),
        )
        result = ts.build()

        expected_description = [
            html.Span("info", id="info-icon", className="material-symbols-outlined tooltip-icon"),
            dbc.Tooltip(
                children=dcc.Markdown("Test description", id="info-text", className="card-text"),
                id="info",
                target="info-icon",
                autohide=False,
            ),
        ]
        expected = html.Div(
            children=[
                dbc.Label(
                    children=[html.Span(id="tree_select_id_title", children="Pick a fruit"), *expected_description],
                    html_for="tree_select_id",
                ),
                fac.AntdTreeSelect(
                    id="tree_select_id",
                    treeData=_convert_options(SIMPLE_OPTIONS),
                    value=[],
                    treeCheckable=True,
                    multiple=True,
                    allowClear=True,
                    showCheckedStrategy="show-child",
                    maxTagCount="responsive",
                    listHeight=300,
                    locale="en-us",
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                ),
            ]
        )
        assert_component_equal(result, expected)

    def test_build_extra_overrides(self):
        ts = TreeSelect(id="tree_select_id", options=SIMPLE_OPTIONS, extra={"listHeight": 500})
        result = ts.build()
        expected = html.Div(
            children=[
                None,
                fac.AntdTreeSelect(
                    id="tree_select_id",
                    treeData=_convert_options(SIMPLE_OPTIONS),
                    value=[],
                    treeCheckable=True,
                    multiple=True,
                    allowClear=True,
                    showCheckedStrategy="show-child",
                    maxTagCount="responsive",
                    listHeight=500,
                    locale="en-us",
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                ),
            ]
        )
        assert_component_equal(result, expected)


class TestConvertOptions:
    """Tests for the _convert_options helper function."""

    def test_convert_options_flat(self):
        result = _convert_options({"A": ["x", "y"]})
        assert result == [
            {
                "title": "A",
                "key": "A",
                "value": "A",
                "children": [
                    {"title": "x", "key": "x", "value": "x"},
                    {"title": "y", "key": "y", "value": "y"},
                ],
            }
        ]

    def test_convert_options_nested(self):
        result = _convert_options({"A": {"B": ["x"]}})
        assert result == [
            {
                "title": "A",
                "key": "A",
                "value": "A",
                "children": [
                    {
                        "title": "B",
                        "key": "B",
                        "value": "B",
                        "children": [
                            {"title": "x", "key": "x", "value": "x"},
                        ],
                    }
                ],
            }
        ]

    def test_convert_options_list(self):
        result = _convert_options(["x", "y"])
        assert result == [
            {"title": "x", "key": "x", "value": "x"},
            {"title": "y", "key": "y", "value": "y"},
        ]

    def test_convert_options_multiple_groups(self):
        result = _convert_options(SIMPLE_OPTIONS)
        assert len(result) == 2
        assert result[0]["title"] == "Fruits"
        assert len(result[0]["children"]) == 2
        assert result[1]["title"] == "Vegetables"
        assert len(result[1]["children"]) == 1


class TestExtractLeafKeys:
    """Tests for the _extract_leaf_keys helper function."""

    def test_extract_leaf_keys_flat(self):
        result = _extract_leaf_keys({"A": ["x", "y"]})
        assert result == {"x", "y"}

    def test_extract_leaf_keys_nested(self):
        result = _extract_leaf_keys(NESTED_OPTIONS)
        assert result == {"iPhone", "Android", "MacBook"}

    def test_extract_leaf_keys_list(self):
        result = _extract_leaf_keys(["a", "b", "c"])
        assert result == {"a", "b", "c"}

    def test_extract_leaf_keys_simple(self):
        result = _extract_leaf_keys(SIMPLE_OPTIONS)
        assert result == {"Apple", "Banana", "Carrot"}


class TestTreeSelectCall:
    def test_call_with_options_param_overrides_self_options(self):
        ts = TreeSelect(options={"A": ["x"]})
        result = ts(options={"B": ["y"]})
        # title is "" (falsy) so children[0] is None, children[1] is AntdTreeSelect
        tree_select_component = result.children[1]
        assert tree_select_component.treeData == [
            {"title": "B", "key": "B", "value": "B", "children": [{"title": "y", "key": "y", "value": "y"}]}
        ]

    def test_call_without_options_param_uses_self_options(self):
        ts = TreeSelect(options={"A": ["x"]})
        result = ts()
        # title is "" (falsy) so children[0] is None, children[1] is AntdTreeSelect
        tree_select_component = result.children[1]
        assert tree_select_component.treeData == [
            {"title": "A", "key": "A", "value": "A", "children": [{"title": "x", "key": "x", "value": "x"}]}
        ]
