"""Contains reusable page functions to create identical content with a different `id`.

Note: Since each page can only belong to one navigation group, we need a new page with a unique ID for
each chart type used in different groups.
"""

import vizro.models as vm
import vizro.plotly.express as px
from custom_charts import butterfly, column_and_line

from pages._pages_utils import PAGE_GRID, ages, gapminder, make_code_clipboard_from_py_file


def butterfly_factory(group: str):
    """Reusable function to create the page content for the butterfly chart with a unique ID."""
    return vm.Page(
        id=f"{group}-butterfly",
        path=f"{group}/butterfly",
        title="Butterfly",
        layout=vm.Layout(grid=PAGE_GRID),
        components=[
            vm.Card(
                text="""

                #### What is a butterfly chart?

                A butterfly chart (also called a tornado chart) is a bar chart for displaying two sets of data series
                side by side.

                &nbsp;

                #### When should I use it?

                Use a butterfly chart when you wish to emphasize the comparison between two data sets sharing the same
                parameters. Sharing this chart with your audience will help them see at a glance how two groups differ
                within the same parameters. You can also **stack** two bars on each side To divide your
                categories.
            """
            ),
            vm.Graph(figure=butterfly(ages, x1="Male", x2="Female", y="Age")),
            make_code_clipboard_from_py_file("butterfly.py"),
        ],
    )


def connected_scatter_factory(group: str):
    """Reusable function to create the page content for the column chart with a unique ID."""
    return vm.Page(
        id=f"{group}-connected-scatter",
        path=f"{group}/connected-scatter",
        title="Connected scatter",
        layout=vm.Layout(grid=PAGE_GRID),
        components=[
            vm.Card(
                text="""
                #### What is a connected scatter chart?

                A connected scatter chart visualizes two variables (x and y) using dots, with lines connecting the dots
                in the order of the data points. One variable is plotted along the x-axis and the other along the
                y-axis, showing both the relationship and a sequence of the data.

                &nbsp;

                #### When should I use it?

                Use connected scatter charts to show the relationship between two variables and the sequence of data
                points. They are ideal for paired numerical data, helping to reveal trends and patterns over time or in
                a specific order. Remember, correlation is not causation, so ensure your audience understands this to
                avoid misinterpretation.
        """
            ),
            vm.Graph(figure=px.line(gapminder.query("country == 'Australia'"), x="year", y="lifeExp", markers=True)),
            make_code_clipboard_from_py_file("connected_scatter.py"),
        ],
    )


def column_and_line_factory(group: str):
    """Reusable function to create the page content for the column+line chart with a unique ID."""
    return vm.Page(
        id=f"{group}-column-and-line",
        path=f"{group}/column-and-line",
        title="Column and line",
        layout=vm.Layout(grid=PAGE_GRID),
        components=[
            vm.Card(
                text="""
                #### What is a column and line chart?

                A combined column and line chart helps you demonstrate the relationship between an amount
                (displayed in columns) and a trend or rate (displayed as a line running across the columns).

                &nbsp;

                #### When should I use it?

                Use this type of chart when you wish to compare quantities of one item with changes in another item.
                It's ideal for showing patterns over time (e.g., monthly sales and growth rates) but can also be used
                for other types of data comparisons.
        """
            ),
            vm.Graph(
                figure=column_and_line(
                    gapminder.query("country == 'Vietnam'"),
                    y_column="gdpPercap",
                    y_line="lifeExp",
                    x="year",
                )
            ),
            make_code_clipboard_from_py_file("column_and_line.py"),
        ],
    )
