"""Magnitude charts."""

import vizro.models as vm
import vizro.plotly.express as px

from pages._factories import column_factory
from pages._pages_utils import PAGE_GRID, make_code_clipboard_from_py_file, tips_agg

# TODO: this is currently identical to ordered bar. It should be:
#  - unordered (currently ordering is done in tips_agg)
#  - different svg
#  - slightly different text
#  - slightly different example
bar = vm.Page(
    title="Bar",
    path="magnitude/bar",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a bar chart?

            A bar chart displays bars in lengths proportional to the values they represent. One axis of
            the chart shows the categories to compare and the other axis provides a value scale,
            starting with zero.

            &nbsp;

            #### When should I use it?

            Select a bar chart when you want to help your audience draw size comparisons and identify
            patterns between categorical data, i.e., data that presents **how many?** in each category. You can
            arrange your bars in any order to fit the message you wish to emphasize. Be mindful of labeling
            clearly when you have a large number of bars. You may need to include a legend,
            or use abbreviations in the chart with fuller descriptions below of the terms used.
        """
        ),
        vm.Graph(
            figure=px.bar(
                tips_agg,
                x="total_bill",
                y="day",
                orientation="h",
            )
        ),
        make_code_clipboard_from_py_file("bar.py"),
    ],
)


column = column_factory("magnitude")

pages = [bar, column]
