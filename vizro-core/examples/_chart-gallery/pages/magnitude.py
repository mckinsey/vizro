"""Magnitude charts."""

import vizro.models as vm
import vizro.plotly.express as px

from pages._factories import column_factory
from pages._pages_utils import PAGE_GRID, make_code_clipboard_from_py_file, tips_agg

bar = vm.Page(
    title="Bar",
    path="magnitude/bar",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a bar chart?

            A bar chart displays bars with lengths proportional to the values they represent. One axis shows the
            categories to compare, and the other provides a value scale starting from zero.

            &nbsp;

            #### When should I use it?

            Use a bar chart to help your audience compare sizes and identify patterns in categorical data, such as
            **how many?** in each category. Arrange the bars in any order to fit the message you want to emphasize.
            Ensure clear labeling, especially with many bars, and consider using a legend or abbreviations with fuller
            descriptions below.
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
