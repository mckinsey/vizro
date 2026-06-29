"""Ranking charts."""

import vizro.models as vm

from pages._factories import lollipop_factory, slope_factory
from pages._pages_utils import PAGE_GRID, make_code_clipboard_from_py_file
from pages.examples import bump, ordered_bar, ordered_column

ordered_bar_page = vm.Page(
    title="Ordered bar",
    path="ranking/ordered-bar",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is an ordered bar chart?

            An ordered bar chart displays bars with lengths proportional to their values, arranged in descending or
            ascending order. One axis shows the categories, and the other provides a value scale starting from zero.

            &nbsp;

            #### When should I use it?

            Use an ordered bar chart to help your audience compare sizes and identify patterns in categorical data,
            emphasizing the order of categories. This is ideal for showing rankings or priorities.
            Ensure clear labeling, especially with many bars, and consider using a legend or abbreviations with fuller
            descriptions below.
        """
        ),
        vm.Graph(figure=ordered_bar.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard",
                    components=[make_code_clipboard_from_py_file("ordered_bar.py", mode="vizro")],
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("ordered_bar.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

ordered_column_page = vm.Page(
    title="Ordered column",
    path="ranking/ordered-column",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is an ordered column chart?

            An ordered column chart is a vertical bar chart where columns are arranged in descending or ascending order
            based on their values. The column lengths vary according to the categorical value they represent, with the
            scale on the y-axis starting from zero.

            &nbsp;

            #### When should I use it?

            Use an ordered column chart to help your audience compare sizes and identify patterns in categorical data,
            emphasizing the order of categories. This is ideal for showing rankings or progressions. Ensure clear
            labeling, especially with many columns, and consider using a legend or abbreviations with fuller
            descriptions below.
        """
        ),
        vm.Graph(figure=ordered_column.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard",
                    components=[make_code_clipboard_from_py_file("ordered_column.py", mode="vizro")],
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("ordered_column.py", mode="plotly")],
                ),
            ]
        ),
    ],
)


bump_page = vm.Page(
    title="Bump",
    path="ranking/bump",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a bump chart?

            A bump chart (also known as a ranking chart) is a line chart that shows how the rank of several items
            changes over time. Each line connects an item's rank across consecutive periods, with rank one at the
            top, making it easy to see which items moved up or down and where they overtook one another.

            &nbsp;

            #### When should I use it?

            Use a bump chart when you wish to emphasize relative position over time rather than absolute values, for
            example league tables, standings, or competitive positioning. It helps your audience see who rose and who
            fell at a glance. Avoid using it when there are too many categories, as the lines become cluttered, or
            when the exact values matter more than the ranking.
        """
        ),
        vm.Graph(figure=bump.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard",
                    components=[make_code_clipboard_from_py_file("bump.py", mode="vizro")],
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("bump.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

lollipop_page = lollipop_factory("deviation")

slope_page = slope_factory("ranking")

pages = [ordered_bar_page, ordered_column_page, bump_page, lollipop_page, slope_page]
