import vizro.models as vm
import vizro.plotly.express as px
from utils._page_utils import DATA_DICT, PAGE_GRID, make_code_clipboard_from_py_file

line = vm.Page(
    title="Line",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a line chart?

            A line chart presents a series of data points over a continuous interval or time period, joined together
            with straight lines.

            &nbsp;

            #### When to use it?

            You should select a line chart when you want to show trends over time. Usually, your y-axis will show a
            quantitative value and your x-axis will be marked as a timescale or a sequence of intervals. You can also
            display negative values below the x-axis. If you wish to group several lines (different data series) in the
            same chart, try to limit yourself to 3-4 to avoid cluttering up your chart.
        """
        ),
        vm.Graph(figure=px.line(DATA_DICT["stocks"], x="date", y="GOOG")),
        make_code_clipboard_from_py_file("line.py"),
    ],
)

pages = [line]
# column
