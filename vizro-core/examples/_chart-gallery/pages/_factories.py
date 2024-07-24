"""Contains reusable page functions to create identical content with a different `id`.

Note: Since each page can only belong to one navigation group, we need a new page with a unique ID for
each chart type used in different groups.
"""

from utils._page_utils import DATA_DICT, PAGE_GRID, make_code_clipboard_from_py_file

import vizro.models as vm
import vizro.plotly.express as px
from utils.custom_extensions import butterfly


# TODO: this is currently identical to ordered column. It should be:
#  - unordered
#  - different svg
#  - slightly different text
#  - slightly different example
def column_factory(id_prefix: str):
    """Reusable function to create the page content for the column chart with a unique ID."""
    return vm.Page(
        id=f"{id_prefix}-column",
        title="Column",
        layout=vm.Layout(grid=PAGE_GRID),
        components=[
            vm.Card(
                text="""
                #### What is a column chart?
    
                A column chart is a vertical bar chart, with column lengths varying according to the
                categorical value they represent. The scale is presented on the y-axis, starting with zero.
    
                &nbsp;
    
                #### When to use it?
    
                Select a column chart when you want to help your audience draw size comparisons and identify
                patterns between categorical data, i.e., data that presents **how many?** in each category. You can
                arrange your columns in any order to fit the message you wish to emphasize. Be mindful of
                labeling clearly when you have a large number of columns. You may need to include a legend,
                or use abbreviations in the chart with fuller descriptions below of the terms used.
        """
            ),
            vm.Graph(
                figure=px.bar(
                    data_frame=DATA_DICT["tips_agg"],
                    y="total_bill",
                    x="day",
                )
            ),
            make_code_clipboard_from_py_file("column.py"),
        ],
    )


def treemap_factory(id_prefix: str):
    """Reusable function to create the page content for the treemap chart with a unique ID."""
    return vm.Page(
        id=f"{id_prefix}-treemap",
        title="Treemap",
        layout=vm.Layout(grid=PAGE_GRID),
        components=[
            vm.Card(
                text="""

                #### What is a treemap?

                A treemap shows hierarchical data arranged as a set of nested rectangles: rectangles are sized
                proportionately to the quantity they represent, combined together to form larger parent category
                rectangles.

                &nbsp;

                #### When to use it?

                It's helpful to use a treemap when you wish to display hierarchical part-to-whole relationships. You can
                compare groups and single elements nested within them. Consider using them instead of Pie charts when
                you have a higher number of categories. Treemaps are very compact and allow audiences to get a quick
                overview of the data.
            """
            ),
            vm.Graph(
                figure=px.treemap(
                    DATA_DICT["gapminder_2007"],
                    path=[px.Constant("world"), "continent", "country"],
                    values="pop",
                    color="lifeExp",
                )
            ),
            make_code_clipboard_from_py_file("treemap.py"),
        ],
    )


def butterfly_factory(id_prefix: str):
    """Reusable function to create the page content for the butterfly chart with a unique ID."""
    return vm.Page(
        id=f"{id_prefix}-butterfly",
        title="Butterfly",
        layout=vm.Layout(grid=PAGE_GRID),
        components=[
            vm.Card(
                text="""

                #### What is a butterfly chart?

                A butterfly chart (also called a tornado chart) is a bar chart for displaying two sets of data series
                side by side.

                &nbsp;

                #### When to use it?

                Use a butterfly chart when you wish to emphasize the comparison between two data sets sharing the same
                parameters. Sharing this chart with your audience will help them see at a glance how two groups differ
                within the same parameters. You can also **stack** two bars on each side if you wish to divide your
                categories.
            """
            ),
            vm.Graph(figure=butterfly(DATA_DICT["ages"], x1="Male", x2="Female", y="Age")),
            make_code_clipboard_from_py_file("butterfly.py"),
        ],
    )
