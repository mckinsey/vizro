import pytest

from vizro.actions._actions_utils import _get_target_dot_separated_strings, _update_nested_figure_properties


class TestUpdateNestedGraphProperties:
    def test_update_nested_figure_properties_single_level(self):
        graph = {"color": "blue"}
        result = _update_nested_figure_properties(graph, "color", "red")
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
    def test_update_nested_figure_properties_multiple_levels(self, graph, dot_separated_strings, value, expected):
        result = _update_nested_figure_properties(graph, dot_separated_strings, value)
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
    def test_update_nested_figure_properties_add_or_overwrite_keys(self, graph, dot_separated_strings, value, expected):
        result = _update_nested_figure_properties(graph, dot_separated_strings, value)
        assert result == expected

    def test_update_nested_figure_properties_invalid_type(self):
        graph = {"color": "blue"}
        with pytest.raises(TypeError, match="'str' object does not support item assignment"):
            _update_nested_figure_properties(graph, "color.value", "42")


class TestFilterDotSeparatedStrings:
    @pytest.mark.parametrize(
        "dot_separated_strings, expected",
        [
            ([], []),
            (["component1.argument1", "component1.data_frame.x"], ["data_frame.x"]),
            (
                [
                    "component1.argument1",
                    "component1.data_frame.x",
                    "component1.data_frame.y",
                    "component2.argument2",
                    "component2.data_frame.z",
                    "component1.argument3",
                ],
                ["data_frame.x", "data_frame.y"],
            ),
            (["component1.argument1.extra", "component1.data_frame.x"], ["data_frame.x"]),
        ],
    )
    def test_filter_data_frame_parameters(self, dot_separated_strings, expected):
        assert _get_target_dot_separated_strings(dot_separated_strings, "component1", data_frame=True) == expected

    @pytest.mark.parametrize(
        "dot_separated_strings, expected",
        [
            ([], []),
            (["component1.argument1", "component1.data_frame.x"], ["argument1"]),
            (
                [
                    "component1.argument1",
                    "component1.data_frame.x",
                    "component1.data_frame.y",
                    "component2.argument2",
                    "component2.data_frame.z",
                    "component1.argument3",
                ],
                ["argument1", "argument3"],
            ),
            (["component1.argument1.extra", "component1.data_frame.x"], ["argument1.extra"]),
        ],
    )
    def test_filter_non_data_frame_parameters(self, dot_separated_strings, expected):
        assert _get_target_dot_separated_strings(dot_separated_strings, "component1", data_frame=False) == expected
