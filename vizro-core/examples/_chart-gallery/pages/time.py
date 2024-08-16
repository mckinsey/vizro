"""Time charts."""

import vizro.models as vm
import vizro.plotly.express as px

from pages._factories import column_factory, connected_scatter_factory
from pages._pages_utils import PAGE_GRID, make_code_clipboard_from_py_file, stocks

line = vm.Page(
    title="Line",
    path="time/line",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a line chart?

            A line chart presents a series of data points over a continuous interval or time period, joined together
            with straight lines.

            &nbsp;

            #### When should I use it?

            You should select a line chart when you want to show trends over time. Usually, your y-axis will show a
            quantitative value and your x-axis will be marked as a timescale or a sequence of intervals. You can also
            display negative values below the x-axis. If you wish to group several lines (different data series) in the
            same chart, try to limit yourself to 3-4 to avoid cluttering up your chart.
        """
        ),
        vm.Graph(figure=px.line(stocks, x="date", y="GOOG")),
        make_code_clipboard_from_py_file("line.py"),
    ],
)

column = column_factory("time")

area = vm.Page(
    title="Area",
    path="time/area",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is an area chart?

            An area chart displays data points over a continuous interval or time period, with the area between the line
            and the axis filled in to emphasize the magnitude of the values.

            &nbsp;

            #### When should I use it?

            An area chart is ideal for showing trends over time and emphasizing the volume of data. Typically,
            the y-axis represents a quantitative value, while the x-axis is marked with a timescale or sequence of
            intervals. Area charts can also display negative values below the x-axis. If you need to compare multiple
            data series in the same chart, try to limit yourself to 3-4 to maintain clarity and avoid clutter.
        """
        ),
        vm.Graph(figure=px.area(stocks, x="date", y="GOOG")),
        make_code_clipboard_from_py_file("area.py"),
    ],
)

connected_scatter = connected_scatter_factory("time")
pages = [line, column, area, connected_scatter]
