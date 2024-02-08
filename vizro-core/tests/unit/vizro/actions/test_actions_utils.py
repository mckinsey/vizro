import pytest
from vizro.actions._actions_utils import _create_target_arg_mapping, _update_nested_graph_properties


class TestUpdateNestedGraphProperties:
    def test_update_nested_graph_properties_single_level(self):
        graph = {"color": "blue"}
        result = _update_nested_graph_properties(graph, "color", "red")
        expected = {"color": "red"}
        assert result == expected

    @pytest.mark.parametrize(
        "graph, dot_separated_strings, value, expected",
        [
            ({"node": {"label": "A", "color": "blue"}}, "node.color", "red", {"node": {"label": "A", "color": "red"}}),
            (
                {"nodes": {"A": {"color": "blue"}, "B": {"color": "green"}}},
                "nodes.A.color",
                "red",
                {"nodes": {"A": {"color": "red"}, "B": {"color": "green"}}},
            ),
        ],
    )
    def test_update_nested_graph_properties_multiple_levels(self, graph, dot_separated_strings, value, expected):
        result = _update_nested_graph_properties(graph, dot_separated_strings, value)
        assert result == expected

    @pytest.mark.parametrize(
        "graph, dot_separated_strings, value, expected",
        [
            (
                {"nodes": {"A": {"color": "blue"}, "B": {"color": "green"}}},
                "nodes.C.color",
                "red",
                {"nodes": {"A": {"color": "blue"}, "B": {"color": "green"}, "C": {"color": "red"}}},
            ),
            (
                {"nodes": {"A": {"color": "blue"}, "B": {"color": "red"}}},
                "nodes.B.value",
                "red",
                {"nodes": {"A": {"color": "blue"}, "B": {"color": "red", "value": "red"}}},
            ),
            (
                {"nodes": {"A": {"color": "blue"}, "B": {"color": "green"}}},
                "nodes.B",
                "red",
                {"nodes": {"A": {"color": "blue"}, "B": "red"}},
            ),
            ({}, "color", "red", {"color": "red"}),
        ],
    )
    def test_update_nested_graph_properties_add_or_overwrite_keys(self, graph, dot_separated_strings, value, expected):
        result = _update_nested_graph_properties(graph, dot_separated_strings, value)
        assert result == expected

    def test_update_nested_graph_properties_invalid_type(self):
        graph = {"color": "blue"}
        with pytest.raises(TypeError, match="'str' object does not support item assignment"):
            _update_nested_graph_properties(graph, "color.value", "42")


class TestCreateTargetArgMapping:
    def test_single_string_one_component(self):
        input_strings = ["component1.argument1"]
        expected = {"component1": ["argument1"]}
        result = _create_target_arg_mapping(input_strings)
        assert result == expected

    def test_multiple_strings_different_components(self):
        input_strings = ["component1.argument1", "component2.argument2", "component1.argument3"]
        expected = {"component1": ["argument1", "argument3"], "component2": ["argument2"]}
        result = _create_target_arg_mapping(input_strings)
        assert result == expected

    def test_multiple_strings_same_component(self):
        input_strings = ["component1.argument1", "component1.argument2", "component1.argument3"]
        expected = {"component1": ["argument1", "argument2", "argument3"]}
        result = _create_target_arg_mapping(input_strings)
        assert result == expected

    def test_empty_input_list(self):
        input_strings = []
        expected = {}
        result = _create_target_arg_mapping(input_strings)
        assert result == expected

    def test_strings_without_separator(self):
        input_strings = ["component1_argument1", "component2_argument2"]
        with pytest.raises(ValueError, match="must contain a '.'"):
            _create_target_arg_mapping(input_strings)

    def test_strings_with_multiple_separators(self):
        input_strings = ["component1.argument1.extra", "component2.argument2.extra"]
        expected = {"component1": ["argument1.extra"], "component2": ["argument2.extra"]}
        assert _create_target_arg_mapping(input_strings) == expected
