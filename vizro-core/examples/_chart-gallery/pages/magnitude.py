"""Magnitude charts."""

import vizro.models as vm
import vizro.plotly.express as px

from pages._factories import column_factory
from pages._pages_utils import PAGE_GRID, gapminder, make_code_clipboard_from_py_file, tips

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
                gapminder.query(
                    "year == 2007 and country.isin(['United States', 'Pakistan', 'India', 'China', 'Indonesia'])"
                ),
                x="pop",
                y="country",
                orientation="h",
            )
        ),
        make_code_clipboard_from_py_file("bar.py"),
    ],
)


column = column_factory("magnitude")

paired_bar = vm.Page(
    title="Paired bar",
    path="magnitude/paired-bar",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a paired bar chart?

            A paired bar chart, also known as a grouped bar chart, displays bars grouped together in pairs for each
            category, with the lengths of the bars proportional to the values they represent. One axis shows the
            categories to compare, while the other provides a value scale starting from zero.

            &nbsp;

            #### When should I use it?

            Use a paired bar chart to compare multiple sets of data within the same categories. This type of chart is
            particularly useful for highlighting differences and similarities between groups, such as **how many?** in
            each category across different groups. Arrange the paired bars clearly to fit the message you want to
            emphasize. Ensure clear labeling, especially with many bars, and consider using a legend or abbreviations
            with fuller descriptions below.
        """
        ),
        vm.Graph(
            figure=px.histogram(
                tips,
                y="day",
                x="total_bill",
                color="sex",
                barmode="group",
                orientation="h",
                category_orders={"day": ["Thur", "Fri", "Sat", "Sun"]},
            ),
        ),
        make_code_clipboard_from_py_file("paired_bar.py"),
    ],
)

paired_column = vm.Page(
    title="Paired column",
    path="magnitude/paired-column",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a paired column chart?

            A paired column chart, also known as a grouped column chart, displays columns grouped together in pairs for
            each category, with the heights of the columns proportional to the values they represent. One axis shows the
            categories to compare, while the other provides a value scale starting from zero.

            &nbsp;

            #### When should I use it?

            Use a paired column chart to compare multiple sets of data within the same categories. This type of chart is
            particularly useful for highlighting differences and similarities between groups, such as **how many?** in
            each category across different groups. Arrange the paired columns clearly to fit the message you want to
            emphasize. Ensure clear labeling, especially with many columns, and consider using a legend or abbreviations
            with fuller descriptions below.
        """
        ),
        vm.Graph(
            figure=px.histogram(
                tips,
                x="day",
                y="total_bill",
                color="sex",
                barmode="group",
                category_orders={"day": ["Thur", "Fri", "Sat", "Sun"]},
            ),
        ),
        make_code_clipboard_from_py_file("paired_column.py"),
    ],
)

pages = [bar, column, paired_bar, paired_column]
