"""Contains reusable page functions to create identical content with a different `id`.

Note: Since each page can only belong to one navigation group, we need a new page with a unique ID for
each chart type used in different groups.
"""

import vizro.models as vm

from pages._pages_utils import PAGE_GRID, make_code_clipboard_from_py_file
from pages.examples import butterfly, column_and_line, connected_scatter, lollipop, waterfall


def butterfly_factory(group: str):
    """Reusable function to create the page content for the butterfly chart with a unique ID."""
    return vm.Page(
        id=f"{group}-butterfly",
        path=f"{group}/butterfly",
        title="Butterfly",
        layout=vm.Grid(grid=PAGE_GRID),
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
                within the same parameters. You can also **stack** two bars on each side to divide your
                categories.
            """
            ),
            vm.Graph(figure=butterfly.fig),
            vm.Tabs(
                tabs=[
                    vm.Container(
                        title="Vizro dashboard",
                        components=[make_code_clipboard_from_py_file("butterfly.py", mode="vizro")],
                    ),
                    vm.Container(
                        title="Plotly figure",
                        components=[make_code_clipboard_from_py_file("butterfly.py", mode="plotly")],
                    ),
                ]
            ),
        ],
    )


def connected_scatter_factory(group: str):
    """Reusable function to create the page content for the column chart with a unique ID."""
    return vm.Page(
        id=f"{group}-connected-scatter",
        path=f"{group}/connected-scatter",
        title="Connected scatter",
        layout=vm.Grid(grid=PAGE_GRID),
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
            vm.Graph(figure=connected_scatter.fig),
            vm.Tabs(
                tabs=[
                    vm.Container(
                        title="Vizro dashboard",
                        components=[make_code_clipboard_from_py_file("connected_scatter.py", mode="vizro")],
                    ),
                    vm.Container(
                        title="Plotly figure",
                        components=[make_code_clipboard_from_py_file("connected_scatter.py", mode="plotly")],
                    ),
                ]
            ),
        ],
    )


def column_and_line_factory(group: str):
    """Reusable function to create the page content for the column+line chart with a unique ID."""
    return vm.Page(
        id=f"{group}-column-and-line",
        path=f"{group}/column-and-line",
        title="Column and line",
        layout=vm.Grid(grid=PAGE_GRID),
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
            vm.Graph(figure=column_and_line.fig),
            vm.Tabs(
                tabs=[
                    vm.Container(
                        title="Vizro dashboard",
                        components=[make_code_clipboard_from_py_file("column_and_line.py", mode="vizro")],
                    ),
                    vm.Container(
                        title="Plotly figure",
                        components=[make_code_clipboard_from_py_file("column_and_line.py", mode="plotly")],
                    ),
                ]
            ),
        ],
    )


def waterfall_factory(group: str):
    """Reusable function to create the page content for the column chart with a unique ID."""
    return vm.Page(
        id=f"{group}-waterfall",
        path=f"{group}/waterfall",
        title="Waterfall",
        layout=vm.Grid(grid=PAGE_GRID),
        components=[
            vm.Card(
                text="""

                #### What is a waterfall chart?

                A waterfall chart is a bar chart that shows the cumulative effect of sequential positive or negative
                values. It starts with an initial value, displays individual changes as steps, and ends with the
                final total.

                &nbsp;

                #### When should I use it?

                Use a waterfall chart to visualize how individual factors contribute to a total, such as changes in
                revenue or costs by category. It helps you understand the incremental impact of each factor, making
                data analysis and interpretation easier. Ensure all bars and changes are clearly labeled, use consistent
                colors for positive and negative values, and arrange categories logically to tell a coherent story.
            """
            ),
            vm.Graph(figure=waterfall.fig),
            vm.Tabs(
                tabs=[
                    vm.Container(
                        title="Vizro dashboard",
                        components=[make_code_clipboard_from_py_file("waterfall.py", mode="vizro")],
                    ),
                    vm.Container(
                        title="Plotly figure",
                        components=[make_code_clipboard_from_py_file("waterfall.py", mode="plotly")],
                    ),
                ]
            ),
        ],
    )


def lollipop_factory(group: str):
    """Reusable function to create the page content for the lollipop chart with a unique ID."""
    return vm.Page(
        id=f"{group}-lollipop",
        path=f"{group}/lollipop",
        title="Lollipop",
        layout=vm.Grid(grid=PAGE_GRID),
        components=[
            vm.Card(
                text="""

                #### What is a lollipop chart?

                A lollipop chart is a variation of a bar chart where each data point is represented by a line and a
                dot at the end to mark the value. It functions like a bar chart but offers a cleaner visual,
                especially useful when dealing with a large number of high values, to avoid the clutter of tall columns.
                However, it can be less precise due to the difficulty in judging the exact center of the circle.

                &nbsp;

                #### When should I use it?

                Use a lollipop chart to compare values across categories, especially when dealing with many high values.
                It highlights differences and trends clearly without the visual bulk of a bar chart. Ensure clarity by
                limiting categories, using consistent scales, and clearly labeling axes. Consider alternatives if
                precise value representation is crucial.
            """
            ),
            vm.Graph(figure=lollipop.fig),
            vm.Tabs(
                tabs=[
                    vm.Container(
                        title="Vizro dashboard",
                        components=[make_code_clipboard_from_py_file("lollipop.py", mode="vizro")],
                    ),
                    vm.Container(
                        title="Plotly figure",
                        components=[make_code_clipboard_from_py_file("lollipop.py", mode="plotly")],
                    ),
                ]
            ),
        ],
    )
