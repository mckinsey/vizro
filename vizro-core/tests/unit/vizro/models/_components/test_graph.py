"""Unit tests for vizro.models.Graph."""
import plotly.graph_objects as go
import pytest
from pydantic import ValidationError

import vizro.models as vm
import vizro.plotly.express as px


@pytest.fixture
def standard_go_chart(gapminder):
    return go.Figure(data=go.Scatter(x=gapminder["gdpPercap"], y=gapminder["lifeExp"], mode="markers"))


def test_create_graph(standard_px_chart):
    graph = vm.Graph(figure=standard_px_chart)

    assert hasattr(graph, "id")
    assert graph.type == "graph"
    assert graph.figure == standard_px_chart._captured_callable
    assert graph.actions == []


def test_failed_graph_with_wrong_figure(standard_go_chart):
    with pytest.raises(ValidationError, match="must provide a valid CapturedCallable object"):
        vm.Graph(
            figure=standard_go_chart,
        )


@pytest.mark.parametrize("title, expected", [(None, 24), ("Test", None)])
def test_title_margin_adjustment(gapminder, title, expected):
    figure = vm.Graph(figure=px.bar(data_frame=gapminder, x="year", y="pop", title=title)).__call__()

    assert figure.layout.margin.t == expected
    assert figure.layout.template.layout.margin.t == 64
    assert figure.layout.template.layout.margin.l == 80
    assert figure.layout.template.layout.margin.b == 64
    assert figure.layout.template.layout.margin.r == 12
