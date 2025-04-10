"""Ranking charts."""

import vizro.models as vm

from pages._factories import lollipop_factory
from pages._pages_utils import PAGE_GRID, make_code_clipboard_from_py_file
from pages.examples import ordered_bar, ordered_column

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


lollipop_page = lollipop_factory("deviation")

pages = [ordered_bar_page, ordered_column_page, lollipop_page]
