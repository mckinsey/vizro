"""Contains reusable page functions to create identical content with a different `id`.

Note: Since each page can only belong to one navigation group, we need a new page with a unique ID for
each chart type used in different groups.
"""

import vizro.models as vm
import vizro.plotly.express as px
from custom_charts import butterfly

from pages._pages_utils import PAGE_GRID, ages, gapminder, make_code_clipboard_from_py_file


def column_factory(group: str):
    """Reusable function to create the page content for the column chart with a unique ID."""
    return vm.Page(
        id=f"{group}-column",
        path=f"{group}/column",
        title="Column",
        layout=vm.Layout(grid=PAGE_GRID),
        components=[
            vm.Card(
                text="""
                #### What is a column chart?

                A column chart is a vertical bar chart with column lengths varying by the categorical value they
                represent, using a y-axis scale starting from zero.

                &nbsp;

                #### When should I use it?

                Use a column chart to help your audience compare sizes and identify patterns in categorical data,
                such as **how many?** in each category. Arrange the columns in any order to fit the message you want
                to emphasize. Ensure clear labeling, especially with many columns, and consider using a legend or
                abbreviations with fuller descriptions below.
        """
            ),
            vm.Graph(
                figure=px.bar(
                    gapminder.query(
                        "year == 2007 and country.isin(['United States', 'Pakistan', 'India', 'China', 'Indonesia'])"
                    ),
                    y="pop",
                    x="country",
                )
            ),
            make_code_clipboard_from_py_file("column.py"),
        ],
    )


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
                within the same parameters. You can also **stack** two bars on each side if you wish to divide your
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
