import plotly.express as px

import vizro.plotly.express as vpx


def test_non_chart_unchanged():
    assert vpx.data is px.data


def test_chart_wrapped():
    graph = vpx.scatter(px.data.iris(), x="petal_width", y="petal_length")
    assert graph._captured_callable._function is px.scatter
    assert vpx.scatter is not px.scatter
