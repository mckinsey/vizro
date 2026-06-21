"""Magnitude charts."""

import vizro.models as vm

from pages._factories import lollipop_factory
from pages._pages_utils import PAGE_GRID, make_code_clipboard_from_py_file
from pages.examples import (
    bar,
    magnitude_column,
    paired_bar,
    paired_column,
    parallel_coordinates,
    pictogram,
    radar,
    radial,
)

bar_page = vm.Page(
    title="Bar",
    path="magnitude/bar",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a bar chart?

            A bar chart displays bars with lengths proportional to the values they represent. One axis shows the
            categories to compare, and the other provides a value scale starting from zero.

            &nbsp;

            #### When should I use it?

            Use a bar chart to help your audience compare sizes and identify patterns in categorical data, such as
            **how many?** in each category. Arrange the bars in any order to fit the message you want to emphasize.
            Ensure clear labeling, especially with many bars, and consider using a legend or abbreviations with fuller
            descriptions below.
        """
        ),
        vm.Graph(figure=bar.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard", components=[make_code_clipboard_from_py_file("bar.py", mode="vizro")]
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("bar.py", mode="plotly")],
                ),
            ]
        ),
    ],
)


# Note: Code example for magnitude/column differs from time/column. The text description is the same.
column_page = vm.Page(
    id="magnitude-column",
    path="magnitude/column",
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
        vm.Graph(figure=magnitude_column.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard",
                    components=[make_code_clipboard_from_py_file("magnitude_column.py", mode="vizro")],
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("magnitude_column.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

paired_bar_page = vm.Page(
    title="Paired bar",
    path="magnitude/paired-bar",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a paired bar chart?

            A paired bar chart, also known as a grouped bar chart, displays bars grouped together in pairs for each
            category, with the lengths of the bars proportional to the values they represent. One axis shows the
            categories to compare, while the other provides a value scale starting from zero.

            &nbsp;

            #### When should I use it?

            Use a paired bar chart to compare multiple sets of data within the same categories. This type of chart is
            particularly useful for highlighting differences and similarities between groups, such as **how many?** in
            each category across different groups. Arrange the paired bars clearly to fit the message you want to
            emphasize. Ensure clear labeling, especially with many bars, and consider using a legend or abbreviations
            with fuller descriptions below.
        """
        ),
        vm.Graph(figure=paired_bar.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard",
                    components=[make_code_clipboard_from_py_file("paired_bar.py", mode="vizro")],
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("paired_bar.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

paired_column_page = vm.Page(
    title="Paired column",
    path="magnitude/paired-column",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a paired column chart?

            A paired column chart, also known as a grouped column chart, displays columns grouped together in pairs for
            each category, with the heights of the columns proportional to the values they represent. One axis shows the
            categories to compare, while the other provides a value scale starting from zero.

            &nbsp;

            #### When should I use it?

            Use a paired column chart to compare multiple sets of data within the same categories. This type of chart is
            particularly useful for highlighting differences and similarities between groups, such as **how many?** in
            each category across different groups. Arrange the paired columns clearly to fit the message you want to
            emphasize. Ensure clear labeling, especially with many columns, and consider using a legend or abbreviations
            with fuller descriptions below.
        """
        ),
        vm.Graph(figure=paired_column.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard",
                    components=[make_code_clipboard_from_py_file("paired_column.py", mode="vizro")],
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("paired_column.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

parallel_coordinates_page = vm.Page(
    path="magnitude/parallel-coordinates ",
    title="Parallel coordinates",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""
                #### What is a parallel coordinates chart?

                A parallel coordinates chart is a type of data visualization used to plot multivariate numerical data.
                Each axis represents a different variable, and lines connecting the axes indicate the values of
                individual data points across these variables.

                &nbsp;

                #### When should I use it?

                Use a parallel coordinates chart to explore relationships and patterns in high-dimensional data.
                This chart is particularly useful for comparing multiple variables simultaneously and identifying
                correlations or clusters within the data. Ensure clear labeling of each axis and consider using color
                coding to distinguish between different data points or groups.
        """
        ),
        vm.Graph(figure=parallel_coordinates.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard",
                    components=[make_code_clipboard_from_py_file("parallel_coordinates.py", mode="vizro")],
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("parallel_coordinates.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

radar_page = vm.Page(
    path="magnitude/radar",
    title="Radar",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""
                #### What is a radar chart?
                A radar chart, also known as a spider plot or star plot, is a type of data visualization
                used to display multivariate data. It consists of three or more variables represented
                on axes that originate from the same central point.

                #### When should I use it?
                Use a radar chart to compare performance or characteristics across multiple variables.
                The chart effectively highlights strengths, weaknesses, patterns, and outliers.
                To maintain clarity, use consistent scales for all axes and clearly mark labels and data points.
        """
        ),
        vm.Graph(figure=radar.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard", components=[make_code_clipboard_from_py_file("radar.py", mode="vizro")]
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("radar.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

radial_page = vm.Page(
    path="magnitude/radial",
    title="Radial",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""
                #### What is a radial chart?

                A radial chart displays values as bars arranged around a circular axis. Each bar's length represents
                the magnitude of a value, while its angle or segment identifies the category.

                &nbsp;

                #### When should I use it?

                Use a radial chart to compare magnitudes across cyclic categories, such as compass directions, hours,
                days, or seasons. It works best when the circular structure is meaningful to the data. For categories
                without a natural cycle, use a standard bar or column chart for easier comparison.
        """
        ),
        vm.Graph(figure=radial.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard", components=[make_code_clipboard_from_py_file("radial.py", mode="vizro")]
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("radial.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

pictogram_page = vm.Page(
    path="magnitude/pictogram",
    title="Pictogram",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""
                #### What is a pictogram chart?

                A pictogram uses repeated icons to represent data values. Each icon represents a specific quantity,
                and the total number of icons shows the magnitude for each category. In this example, each
                circle represents 100 million people.

                &nbsp;

                #### When should I use it?

                Use a pictogram to make data more engaging and accessible, especially for a non-technical audience.
                It is most effective for showing countable items where each icon intuitively represents one unit,
                helping viewers grasp relative sizes at a glance. Avoid using it when precise comparisons are
                needed, as continuous bars are easier to read accurately.
        """
        ),
        vm.Graph(figure=pictogram.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard",
                    components=[make_code_clipboard_from_py_file("pictogram.py", mode="vizro")],
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("pictogram.py", mode="plotly")],
                ),
            ]
        ),
    ],
)


lollipop_page = lollipop_factory("magnitude")
pages = [
    bar_page,
    column_page,
    paired_bar_page,
    paired_column_page,
    parallel_coordinates_page,
    radar_page,
    radial_page,
    pictogram_page,
    lollipop_page,
]
