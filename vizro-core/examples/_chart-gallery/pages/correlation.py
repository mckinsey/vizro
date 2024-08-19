"""Correlation charts."""

import vizro.models as vm
import vizro.plotly.express as px

from pages._factories import column_and_line_factory, connected_scatter_factory
from pages._pages_utils import PAGE_GRID, gapminder, iris, make_code_clipboard_from_py_file

scatter = vm.Page(
    title="Scatter",
    path="correlation/scatter",
    layout=vm.Layout(grid=PAGE_GRID),
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
        vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species")),
        make_code_clipboard_from_py_file("scatter.py"),
    ],
)

connected_scatter = connected_scatter_factory("correlation")

scatter_matrix = vm.Page(
    title="Scatter matrix",
    path="correlation/scatter-matrix",
    layout=vm.Layout(grid=PAGE_GRID),
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
        vm.Graph(
            figure=px.scatter_matrix(iris, dimensions=["sepal_length", "sepal_width", "petal_length", "petal_width"])
        ),
        make_code_clipboard_from_py_file("scatter_matrix.py"),
    ],
)

bubble = vm.Page(
    title="Bubble",
    path="correlation/bubble",
    layout=vm.Layout(grid=PAGE_GRID),
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
        vm.Graph(figure=px.scatter(gapminder.query("year==2007"), x="gdpPercap", y="lifeExp", size="pop", size_max=60)),
        make_code_clipboard_from_py_file("bubble.py"),
    ],
)

column_and_line = column_and_line_factory("correlation")
pages = [scatter, connected_scatter, scatter_matrix, bubble, column_and_line]
