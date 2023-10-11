import pytest

from vizro.actions._actions_utils import _create_target_arg_mapping, _update_nested_graph_properties


@pytest.fixture
def fake_graph_property_dict():
    return {"nodes": {"A": {"color": "blue"}, "B": {"color": "green"}}}


class TestUpdateNestedGraphProperties:
    def test_update_nested_graph_properties_single_level(self):
        graph = {"color": "blue"}
        result = _update_nested_graph_properties(graph, "color", "red")
        expected = {"color": "red"}
        assert result == expected

    def test_update_nested_graph_properties_multiple_levels(self):
        graph = {"node": {"label": "A", "color": "blue"}}
        result = _update_nested_graph_properties(graph, "node.color", 2)
        expected = {"node": {"label": "A", "color": 2}}
        assert result == expected

    def test_update_nested_graph_properties_nested_dict(self):
        graph = {"nodes": {"A": {"color": "blue"}, "B": {"color": "green"}}}
        result = _update_nested_graph_properties(graph, "nodes.A.color", "red")
        expected = {"nodes": {"A": {"color": "red"}, "B": {"color": "green"}}}
        assert result == expected

    def test_update_nested_graph_properties_invalid_key(self, fake_graph_property_dict):
        with pytest.raises(KeyError, match="C"):
            _update_nested_graph_properties(fake_graph_property_dict, "nodes.C.color", "red")

    def test_update_nested_graph_properties_invalid_type(self):
        graph = {"color": "blue"}
        with pytest.raises(TypeError, match="'str' object does not support item assignment"):
            _update_nested_graph_properties(graph, "color.value", 42)


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
