"""Unit tests for vizro.models.Graph."""
import json

import plotly
import plotly.graph_objects as go
import pytest
from dash import dcc
from dash._callback_context import context_value
from dash._utils import AttributeDict

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions._actions_utils import CallbackTriggerDict
from vizro.managers import data_manager
from vizro.models._action._action import Action


@pytest.fixture
def standard_px_chart_with_str_dataframe():
    return px.scatter(
        data_frame="gapminder",
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        color="continent",
        hover_name="country",
        size_max=60,
    )


@pytest.fixture
def expected_graph():
    return dcc.Loading(
        dcc.Graph(
            id="text_graph",
            figure=go.Figure(
                layout={
                    "paper_bgcolor": "rgba(0,0,0,0)",
                    "plot_bgcolor": "rgba(0,0,0,0)",
                    "xaxis": {"visible": False},
                    "yaxis": {"visible": False},
                }
            ),
            config={
                "autosizable": True,
                "frameMargins": 0,
                "responsive": True,
            },
            className="chart_container",
        ),
        color="grey",
        parent_className="loading-container",
    )


class TestDunderMethodsGraph:
    def test_create_graph_mandatory_only(self, standard_px_chart):
        graph = vm.Graph(figure=standard_px_chart)

        assert hasattr(graph, "id")
        assert graph.type == "graph"
        assert graph.figure == standard_px_chart._captured_callable
        assert graph.actions == []

    @pytest.mark.parametrize("id", ["id_1", "id_2"])
    def test_create_graph_mandatory_and_optional(self, standard_px_chart, id):
        graph = vm.Graph(figure=standard_px_chart, id=id, actions=[])

        assert graph.id == id
        assert graph.type == "graph"
        assert graph.figure == standard_px_chart._captured_callable

    def test_mandatory_figure_missing(self):
        with pytest.raises(ValidationError, match="field required"):
            vm.Graph()

    def test_failed_graph_with_wrong_figure(self, standard_go_chart):
        with pytest.raises(ValidationError, match="must provide a valid CapturedCallable object"):
            vm.Graph(figure=standard_go_chart)

    def test_getitem_known_args(self, standard_px_chart):
        graph = vm.Graph(figure=standard_px_chart)

        assert graph["x"] == "gdpPercap"
        assert graph["type"] == "graph"

    def test_getitem_unknown_args(self, standard_px_chart):
        graph = vm.Graph(figure=standard_px_chart)
        with pytest.raises(KeyError):
            graph["unknown_args"]

    @pytest.mark.parametrize("title, expected", [(None, 24), ("Test", None)])
    def test_title_margin_adjustment(self, gapminder, title, expected):
        graph = vm.Graph(figure=px.bar(data_frame=gapminder, x="year", y="pop", title=title)).__call__()

        assert graph.layout.margin.t == expected
        assert graph.layout.template.layout.margin.t == 64
        assert graph.layout.template.layout.margin.l == 80
        assert graph.layout.template.layout.margin.b == 64
        assert graph.layout.template.layout.margin.r == 12

    def test_update_theme_outside_callback(self, standard_px_chart):
        graph = vm.Graph(figure=standard_px_chart).__call__()
        assert graph == standard_px_chart.update_layout(margin_t=24, template="vizro_dark")

    @pytest.mark.parametrize("template", ["vizro_dark", "vizro_light"])
    def test_update_theme_inside_callback(self, standard_px_chart, template):
        mock_callback_context = {
            "args_grouping": {
                "external": {
                    "theme_selector": CallbackTriggerDict(
                        id="theme_selector",
                        property="on",
                        value=template == "vizro_dark",
                        str_id="theme_selector",
                        triggered=False,
                    )
                }
            }
        }
        context_value.set(AttributeDict(**mock_callback_context))
        graph = vm.Graph(figure=standard_px_chart).__call__()
        assert graph == standard_px_chart.update_layout(margin_t=24, template=template)

    def test_set_action_via_validator(self, standard_px_chart, identity_action_function):
        graph = vm.Graph(figure=standard_px_chart, actions=[Action(function=identity_action_function())])
        actions_chain = graph.actions[0]
        assert actions_chain.trigger.component_property == "clickData"


class TestProcessFigureDataFrame:
    def test_process_figure_data_frame_str_df(self, standard_px_chart_with_str_dataframe, gapminder):
        data_manager["gapminder"] = gapminder
        graph_with_str_df = vm.Graph(id="text_graph", figure=standard_px_chart_with_str_dataframe)
        assert data_manager._get_component_data("text_graph").equals(gapminder)
        assert graph_with_str_df["data_frame"] == "gapminder"

    def test_process_figure_data_frame_df(self, standard_px_chart, gapminder):
        graph_with_df = vm.Graph(id="text_graph", figure=standard_px_chart)
        assert data_manager._get_component_data("text_graph").equals(gapminder)
        with pytest.raises(KeyError, match="'data_frame'"):
            graph_with_df.figure["data_frame"]


class TestBuild:
    def test_graph_build(self, standard_px_chart, expected_graph):
        graph = vm.Graph(id="text_graph", figure=standard_px_chart)

        result = json.loads(json.dumps(graph.build(), cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(expected_graph, cls=plotly.utils.PlotlyJSONEncoder))
        assert result == expected
