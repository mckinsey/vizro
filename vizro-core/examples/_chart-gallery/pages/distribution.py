import vizro.models as vm
import vizro.plotly.express as px
from pages._factories import butterfly_factory
from utils._page_utils import DATA_DICT, PAGE_GRID, make_code_clipboard_from_py_file

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

            #### When to use it?

            Use this chart to go beyond the simple box plot and show the distribution shape of the data, the
            inter-quartile range, the confidence intervals and the median.
        """
        ),
        vm.Graph(
            figure=px.violin(
                data_frame=DATA_DICT["tips"],
                y="total_bill",
                x="day",
                color="day",
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

            #### When to use it?

            Choose a box plot when you need to summarize distributions between many groups or datasets. It takes up
            less space than many other charts.

            Create boxes to display the median, and the upper and lower quartiles. Add `whiskers` to highlight
            variability outside the upper and lower quartiles. You can add outliers as dots beyond, but in line with
            the whiskers.
        """
        ),
        vm.Graph(
            figure=px.box(
                data_frame=DATA_DICT["tips"],
                y="total_bill",
                x="day",
                color="day",
            )
        ),
        make_code_clipboard_from_py_file("boxplot.py"),
    ],
)

butterfly = butterfly_factory("distribution")

pages = [violin, boxplot, butterfly]
