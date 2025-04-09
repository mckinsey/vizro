"""Correlation charts."""

import vizro.models as vm

from pages._factories import column_and_line_factory, connected_scatter_factory
from pages._pages_utils import PAGE_GRID, make_code_clipboard_from_py_file
from pages.examples import bubble, scatter, scatter_matrix

scatter_page = vm.Page(
    title="Scatter",
    path="correlation/scatter",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a scatter chart?

            A scatter plot is a two-dimensional data visualization using dots to represent the values obtained for two
            different variables - one plotted along the x-axis and the other plotted along the y-axis.

            &nbsp;

            #### When should I use it?

            Use scatter plots when you want to show the relationship between two variables. Scatter plots are sometimes
            called _Correlation plots_ because they show how two variables are correlated. Scatter plots are ideal when
            you have paired numerical data and you want to see if one variable impacts the other. However, do remember
            that correlation is not causation. Make sure your audience does not draw the wrong conclusions.
        """
        ),
        vm.Graph(figure=scatter.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard", components=[make_code_clipboard_from_py_file("scatter.py", mode="vizro")]
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("scatter.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

connected_scatter_page = connected_scatter_factory("correlation")

scatter_matrix_page = vm.Page(
    title="Scatter matrix",
    path="correlation/scatter-matrix",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a scatter matrix?

            A scatter matrix, also known as a SPLOM chart, is a multi-dimensional data visualization that displays
            scatter plots for every pair of variables in a dataset. Each scatter plot is positioned in a matrix format,
            where rows and columns represent different variables.

            &nbsp;

            #### When should I use it?

            Use a scatter matrix when you want to explore relationships between multiple pairs of variables
            simultaneously. They are particularly useful for identifying correlations, patterns, and potential outliers
            within a dataset containing multiple numerical variables. Carefully select the most relevant variables to
            ensure clarity and readability of the chart.
        """
        ),
        vm.Graph(figure=scatter_matrix.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard",
                    components=[make_code_clipboard_from_py_file("scatter_matrix.py", mode="vizro")],
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("scatter_matrix.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

bubble_page = vm.Page(
    title="Bubble",
    path="correlation/bubble",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a bubble chart?

            A bubble chart is a type of data visualization that displays three dimensions of data. Each point on the
            chart is represented by a bubble, where the x-axis and y-axis denote two of the data dimensions, and the
            size of the bubble represents the third dimension.

            &nbsp;

            #### When should I use it?

            Use a bubble chart when you want to explore and compare relationships between three variables
            simultaneously. They are particularly useful for identifying patterns, trends, and outliers in
            multi-dimensional data. Bubble charts can help you visualize the impact of a third variable,
            providing deeper insights than a standard scatter plot.
        """
        ),
        vm.Graph(figure=bubble.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard", components=[make_code_clipboard_from_py_file("bubble.py", mode="vizro")]
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("bubble.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

column_and_line_page = column_and_line_factory("correlation")

pages = [scatter_page, connected_scatter_page, scatter_matrix_page, bubble_page, column_and_line_page]
