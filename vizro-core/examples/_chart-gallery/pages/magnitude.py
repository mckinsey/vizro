"""Magnitude charts."""

import vizro.models as vm
import vizro.plotly.express as px

from pages._pages_utils import PAGE_GRID, gapminder, iris, make_code_clipboard_from_py_file, tips

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

# Note: Code example for magnitude/column differs from time/column. The text description is the same.
column = vm.Page(
    id="magnitude-column",
    path="magnitude/column",
    title="Column",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""
                #### What is a column chart?

                A column chart is a type of bar chart where data is represented with vertical columns. Each
                column's height corresponds to the value it represents, with the y-axis starting from zero.

                &nbsp;

                #### When should I use it?

                Use a column chart to compare sizes and identify patterns in categorical data, including time-based
                data. Arrange columns to fit your message, and for time-based data, order them chronologically to
                highlight trends. Ensure clear labeling, especially with many categories, and consider using a legend
                or abbreviations with fuller descriptions below.
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
        make_code_clipboard_from_py_file("magnitude_column.py"),
    ],
)

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

parallel_coordinates = vm.Page(
    path="magnitude/parallel-coordinates ",
    title="Parallel coordinates",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""
                #### What is a parallel coordinates chart?

                A parallel coordinates chart is a type of data visualization used to plot multivariate numerical data.
                Each axis represents a different variable, and lines connecting the axes indicate the values of
                individual data points across these variables.

                &nbsp;

                #### When should I use it?

                Use a parallel coordinates chart to explore relationships and patterns in high-dimensional data.
                This chart is particularly useful for comparing multiple variables simultaneously and identifying
                correlations or clusters within the data. Ensure clear labeling of each axis and consider using color
                coding to distinguish between different data points or groups.
        """
        ),
        vm.Graph(
            figure=px.parallel_coordinates(
                iris, color="species_id", dimensions=["sepal_width", "sepal_length", "petal_width", "petal_length"]
            )
        ),
        make_code_clipboard_from_py_file("parallel_coordinates.py"),
    ],
)

pages = [bar, column, paired_bar, paired_column, parallel_coordinates]
