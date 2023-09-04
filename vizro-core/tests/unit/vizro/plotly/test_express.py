import plotly.express as px

import vizro.plotly.express as hpx


def test_non_chart_unchanged():
    assert hpx.data is px.data


def test_chart_wrapped():
    graph = hpx.scatter(px.data.iris(), x="petal_width", y="petal_length")
    assert graph._captured_callable._function is px.scatter
    assert hpx.scatter is not px.scatter
