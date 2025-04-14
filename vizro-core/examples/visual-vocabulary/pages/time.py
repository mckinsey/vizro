"""Time charts."""

import vizro.models as vm

from pages._factories import column_and_line_factory, connected_scatter_factory
from pages._pages_utils import (
    PAGE_GRID,
    make_code_clipboard_from_py_file,
)
from pages.examples import area, gantt, heatmap, line, sparkline, stepped_line, time_column

line_page = vm.Page(
    title="Line",
    path="time/line",
    layout=vm.Grid(grid=PAGE_GRID),
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
        vm.Graph(figure=line.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard", components=[make_code_clipboard_from_py_file("line.py", mode="vizro")]
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("line.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

# Note: Code example for magnitude/column differs from time/column. The text description is the same.
column_page = vm.Page(
    id="time-column",
    path="time/column",
    title="Column",
    layout=vm.Grid(grid=PAGE_GRID),
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
        vm.Graph(figure=time_column.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard",
                    components=[make_code_clipboard_from_py_file("time_column.py", mode="vizro")],
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("time_column.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

area_page = vm.Page(
    title="Area",
    path="time/area",
    layout=vm.Grid(grid=PAGE_GRID),
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
        vm.Graph(figure=area.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard", components=[make_code_clipboard_from_py_file("area.py", mode="vizro")]
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("area.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

connected_scatter_page = connected_scatter_factory("time")
column_and_line_page = column_and_line_factory("time")

stepped_line_page = vm.Page(
    title="Stepped line",
    path="time/stepped-line",
    layout=vm.Grid(grid=PAGE_GRID),
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
        vm.Graph(figure=stepped_line.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard",
                    components=[make_code_clipboard_from_py_file("stepped_line.py", mode="vizro")],
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("stepped_line.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

heatmap_page = vm.Page(
    title="Heatmap",
    path="time/heatmap",
    layout=vm.Grid(grid=PAGE_GRID),
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
        vm.Graph(figure=heatmap.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard", components=[make_code_clipboard_from_py_file("heatmap.py", mode="vizro")]
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("heatmap.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

gantt_page = vm.Page(
    title="Gantt",
    path="time/gantt",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""
                #### What is a gantt chart?

                A gantt chart is a type of bar chart that visualizes a project schedule.
                It shows the start and end dates of a project element, such as tasks, activities, or
                events, in a timeline format. Each element is represented by a bar whose length indicates
                its duration.

                &nbsp;

                #### When should I use it?

                Gantt charts are ideal for visualizing project timelines, tracking
                progress, and managing dependencies. They clearly display task start and end dates, making
                it easy to monitor project status and manage interdependencies. However, they can become
                complex if not regularly updated, especially for large projects.
            """
        ),
        vm.Graph(figure=gantt.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard", components=[make_code_clipboard_from_py_file("gantt.py", mode="vizro")]
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("gantt.py", mode="plotly")],
                ),
            ]
        ),
    ],
)


sparkline_page = vm.Page(
    title="Sparkline",
    path="time/sparkline",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""
                #### What is a sparkline chart?

                A sparkline chart is a compact line or area chart that displays multiple time series over a continuous
                period. Without visible axes or labels, they are ideal for embedding within text, tables, or dashboards,
                highlighting relative movement rather than precise values for a quick visual summary of trends.

                &nbsp;

                #### When should I use it?

                Use sparkline charts to show trends for multiple time series sharing the same y-axis quantity over the
                same x-axis time range. They emphasize relative movement rather than precise values. To keep them
                effective, ensure simplicity by avoiding clutter. Use consistent scales and distinct colors for
                different series. Remove labels and gridlines, limit annotations, and place sparklines near relevant
                text or data.
            """
        ),
        vm.Graph(figure=sparkline.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard", components=[make_code_clipboard_from_py_file("sparkline.py", mode="vizro")]
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("sparkline.py", mode="plotly")],
                ),
            ]
        ),
    ],
)
pages = [
    line_page,
    column_page,
    area_page,
    connected_scatter_page,
    column_and_line_page,
    stepped_line_page,
    heatmap_page,
    gantt_page,
    sparkline_page,
]
