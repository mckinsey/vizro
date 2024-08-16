"""Correlation charts."""

import vizro.models as vm
import vizro.plotly.express as px

from pages._factories import connected_scatter_factory
from pages._pages_utils import PAGE_GRID, iris, make_code_clipboard_from_py_file

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
pages = [scatter, connected_scatter]
