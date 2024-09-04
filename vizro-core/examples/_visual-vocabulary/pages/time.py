"""Time charts."""

import vizro.models as vm
import vizro.plotly.express as px
from custom_charts import categorical_column

from pages._factories import column_and_line_factory, connected_scatter_factory
from pages._pages_utils import PAGE_GRID, gapminder, make_code_clipboard_from_py_file, stepped_line_data, stocks, tips

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
            display negative values below the x-axis. To group several lines (different data series) in the
            same chart, try to limit yourself to 3-4 to avoid cluttering up your chart.
        """
        ),
        vm.Graph(figure=px.line(stocks, x="date", y="GOOG")),
        make_code_clipboard_from_py_file("line.py"),
    ],
)

# Note: Code example for magnitude/column differs from time/column. The text description is the same.
column = vm.Page(
    id="time-column",
    path="time/column",
    title="Column",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""
                #### What is a column chart?

                A column chart is a type of bar chart where data is represented with vertical columns. Each
                column's height corresponds to the value it represents, with the y-axis starting from zero.

                &nbsp;

                #### When should I use it?

                Use a column chart to compare sizes and identify patterns in categorical data, including time-based
                data. Arrange columns to fit your message, and for time-based data, order them chronologically to
                highlight trends. Ensure clear labeling, especially with many categories, and consider using a legend
                or abbreviations with fuller descriptions below.
        """
        ),
        vm.Graph(
            figure=categorical_column(
                gapminder.query("country == 'Nigeria' and year > 1970"),
                y="gdpPercap",
                x="year",
            )
        ),
        make_code_clipboard_from_py_file("time_column.py"),
    ],
)

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
column_and_line = column_and_line_factory("time")

stepped_line = vm.Page(
    title="Stepped line",
    path="time/stepped-line",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a stepped line chart?

            A stepped line chart is much like a standard line chart but, instead of connecting two points with the
            shortest line, the line forms a series of steps between data points.

            &nbsp;

            #### When should I use it?

            You should use a stepped line chart when you wish to draw attention to changes occurring at specific points.
            By contrast, a line chart would suggest that changes occur gradually.
        """
        ),
        vm.Graph(
            figure=px.line(
                data_frame=stepped_line_data,
                x="year",
                y="rate",
                line_shape="vh",
            ),
        ),
        make_code_clipboard_from_py_file("stepped_line.py"),
    ],
)

heatmap = vm.Page(
    title="Heatmap",
    path="time/heatmap",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""
            #### What is a heatmap?
            A heatmap chart depicts values for a main variable of interest across two axis variables as a grid of
            colored squares. The color intensity of each cell represents the value of the main variable within a
            specific range.

            &nbsp;

            #### When should I use it?

            Use a heatmap chart to visualize time patterns and identify trends between two variables.
            Typically, the x-axis represents time intervals (e.g., hours, days, months), while the y-axis represents
            categories or different variables. By observing color changes across the grid, you can easily spot
            patterns and correlations.
        """
        ),
        vm.Graph(figure=px.density_heatmap(tips, x="day", y="size", z="tip", histfunc="avg", text_auto="$.2f")),
        make_code_clipboard_from_py_file("heatmap.py"),
    ],
)
pages = [line, column, area, connected_scatter, column_and_line, stepped_line, heatmap]
