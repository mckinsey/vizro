"""Ranking charts."""

import vizro.models as vm
import vizro.plotly.express as px

from pages._pages_utils import PAGE_GRID, gapminder, make_code_clipboard_from_py_file

ordered_bar = vm.Page(
    title="Ordered bar",
    path="ranking/ordered-bar",
    layout=vm.Layout(grid=PAGE_GRID),
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
        vm.Graph(
            figure=px.bar(
                gapminder.query(
                    "year == 2007 and country.isin(['United States', 'Pakistan', 'India', 'China', 'Indonesia'])"
                ).sort_values("pop"),
                x="pop",
                y="country",
                orientation="h",
            )
        ),
        make_code_clipboard_from_py_file("ordered_bar.py"),
    ],
)

ordered_column = vm.Page(
    title="Ordered column",
    path="ranking/ordered-column",
    layout=vm.Layout(grid=PAGE_GRID),
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
        vm.Graph(
            figure=px.bar(
                gapminder.query(
                    "year == 2007 and country.isin(['United States', 'Pakistan', 'India', 'China', 'Indonesia'])"
                ).sort_values("pop"),
                y="pop",
                x="country",
            )
        ),
        make_code_clipboard_from_py_file("ordered_column.py"),
    ],
)


pages = [ordered_bar, ordered_column]
