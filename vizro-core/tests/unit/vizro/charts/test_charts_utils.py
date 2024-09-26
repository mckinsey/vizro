from copy import deepcopy

import plotly.graph_objects as go
import pytest

from vizro.models.types import capture


@pytest.fixture
def minimal_capture_chart(gapminder):
    @capture("graph")
    def _minimal_capture_chart(data_frame):
        return go.Figure()

    return _minimal_capture_chart(gapminder)


@pytest.mark.parametrize("chart_type", ["standard_px_chart", "minimal_capture_chart"])
def test_deepcopy_DashboardReadyFigure(chart_type, request):
    original = request.getfixturevalue(chart_type)
    copy = deepcopy(original)

    assert hasattr(copy, "_captured_callable")
    assert original._captured_callable is not copy._captured_callable
    assert original._captured_callable() == copy._captured_callable()
