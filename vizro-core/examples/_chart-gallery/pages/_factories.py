"""Contains reusable page functions to create identical content with a different `id`.

Note: Since each page can only belong to one navigation group, we need a new page with a unique ID for
each chart type used in different groups.
"""

import vizro.models as vm
import vizro.plotly.express as px
from custom_charts import butterfly

from pages._pages_utils import PAGE_GRID, ages, make_code_clipboard_from_py_file, tips_agg


# TODO: this is currently identical to ordered column. It should be:
#  - unordered (currently ordering is done in tips_agg)
#  - different svg
#  - slightly different text
#  - slightly different example
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

                A column chart is a vertical bar chart, with column lengths varying according to the
                categorical value they represent. The scale is presented on the y-axis, starting with zero.

                &nbsp;

                #### When should I use it?

                Select a column chart when you want to help your audience draw size comparisons and identify
                patterns between categorical data, i.e., data that presents **how many?** in each category. You can
                arrange your columns in any order to fit the message you wish to emphasize. Be mindful of
                labeling clearly when you have a large number of columns. You may need to include a legend,
                or use abbreviations in the chart with fuller descriptions below of the terms used.
        """
            ),
            vm.Graph(
                figure=px.bar(
                    tips_agg,
                    y="total_bill",
                    x="day",
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