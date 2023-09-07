"""Unit tests for vizro.models.Graph."""
import json

import plotly
import pytest
from pydantic import ValidationError

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import export_data
from vizro.managers import data_manager
from vizro.models._action._actions_chain import ActionsChain
from vizro.models._components.graph import create_empty_fig


class TestGraphInstantiation:
    def test_create_graph_mandatory_only(self, standard_px_chart):
        graph = vm.Graph(figure=standard_px_chart)

        assert hasattr(graph, "id")
        assert graph.type == "graph"
        assert graph.figure == standard_px_chart._captured_callable
        assert graph.actions == []

    @pytest.mark.parametrize("id", ["id_1", "id_2"])
    def test_create_graph_mandatory_and_optional(self, standard_px_chart, id):
        graph = vm.Graph(
            figure=standard_px_chart,
            id=id,
            actions=[
                vm.Action(function=export_data()),
            ],
        )
        actions_chain = graph.actions[0]

        assert graph.id == id
        assert graph.type == "graph"
        assert graph.figure == standard_px_chart._captured_callable
        assert isinstance(actions_chain, ActionsChain)

    def test_mandatory_figure_missing(self):
        with pytest.raises(ValidationError, match="field required"):
            vm.Graph()

    def test_failed_graph_with_wrong_figure(self, standard_go_chart):
        with pytest.raises(ValidationError, match="must provide a valid CapturedCallable object"):
            vm.Graph(
                figure=standard_go_chart,
            )

    @pytest.mark.parametrize("title, expected", [(None, 24), ("Test", None)])
    def test_title_margin_adjustment(self, gapminder, title, expected):
        figure = vm.Graph(figure=px.bar(data_frame=gapminder, x="year", y="pop", title=title)).__call__()

        assert figure.layout.margin.t == expected
        assert figure.layout.template.layout.margin.t == 64
        assert figure.layout.template.layout.margin.l == 80
        assert figure.layout.template.layout.margin.b == 64
        assert figure.layout.template.layout.margin.r == 12


class TestProcessFigureDataFrame:
    def test_process_figure_data_frame_str_df(self, standard_px_chart_with_str_dataframe, gapminder):
        data_manager["gapminder"] = gapminder
        graph_with_str_df = vm.Graph(
            id="text_graph",
            figure=standard_px_chart_with_str_dataframe,
        )
        assert data_manager._get_component_data("text_graph").equals(gapminder)
        assert graph_with_str_df.figure["data_frame"] == "gapminder"

    def test_process_figure_data_frame_df(self, standard_px_chart, gapminder):
        graph_with_df = vm.Graph(
            id="text_graph",
            figure=standard_px_chart,
        )
        assert data_manager._get_component_data("text_graph").equals(gapminder)
        with pytest.raises(KeyError, match="'data_frame'"):
            graph_with_df.figure["data_frame"]


class TestBuild:
    def test_create_empty_fig(self, expected_empty_chart):
        result = create_empty_fig("NO DATA")
        assert result == expected_empty_chart

    def test_graph_build(self, standard_px_chart, expected_graph):
        graph = vm.Graph(
            id="text_graph",
            figure=standard_px_chart,
        )

        result = json.loads(json.dumps(graph.build(), cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(expected_graph, cls=plotly.utils.PlotlyJSONEncoder))
        assert result == expected
