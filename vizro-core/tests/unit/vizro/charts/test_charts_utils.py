from copy import deepcopy

import pytest


@pytest.mark.parametrize("chart_type", ["standard_px_chart", "minimal_capture_chart"])
def test_deepcopy_DashboardReadyFigure(chart_type, request):
    original = request.getfixturevalue(chart_type)
    copy = deepcopy(original)

    assert hasattr(copy, "_captured_callable")
    assert original._captured_callable is not copy._captured_callable
    assert original._captured_callable() == copy._captured_callable()
