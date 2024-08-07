"""Distribution charts."""

import vizro.models as vm
import vizro.plotly.express as px

from pages._factories import butterfly_factory
from pages._pages_utils import PAGE_GRID, make_code_clipboard_from_py_file, tips

violin = vm.Page(
    title="Violin",
    path="distribution/violin",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a violin chart?

            A violin chart is similar to a box plot, but works better for visualizing more complex distributions and
            their probability density at different values.

            &nbsp;

            #### When should I use it?

            Use this chart to go beyond the simple box plot and show the distribution shape of the data, the
            inter-quartile range, the confidence intervals and the median.
        """
        ),
        vm.Graph(
            figure=px.violin(
                tips,
                y="total_bill",
                x="day",
                color="day",
                box=True,
            )
        ),
        make_code_clipboard_from_py_file("violin.py"),
    ],
)

boxplot = vm.Page(
    title="Boxplot",
    path="distribution/boxplot",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a boxplot?

            A box plot (also known as whisker plot) provides a visual display of multiple datasets,
            indicating the median (center) and the range of the data for each.

            &nbsp;

            #### When should I use it?

            Choose a box plot when you need to summarize distributions between many groups or datasets. It takes up
            less space than many other charts.

            Create boxes to display the median, and the upper and lower quartiles. Add whiskers to highlight
            variability outside the upper and lower quartiles. You can add outliers as dots beyond, but in line with
            the whiskers.
        """
        ),
        vm.Graph(
            figure=px.box(
                tips,
                y="total_bill",
                x="day",
                color="day",
            )
        ),
        make_code_clipboard_from_py_file("boxplot.py"),
    ],
)

butterfly = butterfly_factory("distribution")

histogram = vm.Page(
    title="Histogram",
    path="distribution/histogram",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""
            #### What is a histogram?

            A histogram organizes numerical data into columns, with the size of each column representing how frequently
            values fall within specified ranges. It visualizes data across a continuous interval.

            &nbsp;

            #### When should I use it?

            A histogram is useful for showing your audience where specific values are concentrated, identifying the
            extremes, and spotting any gaps or outliers. It can also help you visualize a rough probability
            distribution. Ensure that the gaps between columns are minimal to make the 'shape' of your data
            immediately clear.
        """
        ),
        vm.Graph(figure=px.histogram(tips, x="total_bill")),
        make_code_clipboard_from_py_file("histogram.py"),
    ],
)


pages = [violin, boxplot, butterfly, histogram]
