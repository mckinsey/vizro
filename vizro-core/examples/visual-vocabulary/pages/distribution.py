"""Distribution charts."""

import vizro.models as vm

from pages._factories import butterfly_factory
from pages._pages_utils import PAGE_GRID, make_code_clipboard_from_py_file
from pages.examples import boxplot, dumbbell, histogram, violin

violin_page = vm.Page(
    title="Violin",
    path="distribution/violin",
    layout=vm.Grid(grid=PAGE_GRID),
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
        vm.Graph(figure=violin.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard", components=[make_code_clipboard_from_py_file("violin.py", mode="vizro")]
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("violin.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

boxplot_page = vm.Page(
    title="Boxplot",
    path="distribution/boxplot",
    layout=vm.Grid(grid=PAGE_GRID),
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
        vm.Graph(figure=boxplot.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard", components=[make_code_clipboard_from_py_file("boxplot.py", mode="vizro")]
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("boxplot.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

butterfly_page = butterfly_factory("distribution")

histogram_page = vm.Page(
    title="Histogram",
    path="distribution/histogram",
    layout=vm.Grid(grid=PAGE_GRID),
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
        vm.Graph(figure=histogram.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard", components=[make_code_clipboard_from_py_file("histogram.py", mode="vizro")]
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("histogram.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

dumbbell_page = vm.Page(
    title="Dumbbell",
    path="distribution/dumbbell",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""
            #### What is a dumbbell chart?
            A dumbbell chart emphasizes the gap between two categorical groups. Each data point is depicted by a
            symbol, typically a circle, representing its quantitative value. These symbols are connected by a line,
            visually indicating the gap between the two points. Categories or groups are displayed along one axis,
            while quantitative values are plotted along the other.

            &nbsp;

            #### When should I use it?
            Dumbbell charts are ideal for illustrating differences or gaps between two points. They are less cluttered
            than bar charts, making it easier to compare groups. Common uses include comparing groups, such as showing
            differences in performance metrics across various categories. Colors can be used to emphasize the direction
            of changes or to distinguish between categories.
        """
        ),
        vm.Graph(figure=dumbbell.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard", components=[make_code_clipboard_from_py_file("dumbbell.py", mode="vizro")]
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("dumbbell.py", mode="plotly")],
                ),
            ]
        ),
    ],
)


pages = [violin_page, boxplot_page, butterfly_page, dumbbell_page, histogram_page]
