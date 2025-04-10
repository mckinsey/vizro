"""Deviation charts."""

import vizro.models as vm

from pages._factories import butterfly_factory
from pages._pages_utils import PAGE_GRID, make_code_clipboard_from_py_file
from pages.examples import diverging_bar, diverging_stacked_bar

butterfly_page = butterfly_factory("deviation")


diverging_bar_page = vm.Page(
    title="Diverging bar",
    path="deviation/diverging-bar",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a diverging bar?

            A diverging bar chart is a version of a bar chart used to display both positive and negative values across
            a common baseline. Bars extend either to the left or right of the central axis, indicating negative or
            positive values, respectively. This allows for easy comparison of data points that deviate in opposite
            directions.

            &nbsp;

            #### When should I use it?

            Use a diverging bar chart to compare positive and negative values from a central baseline. These charts are
            suitable for visualizing profit and loss, survey results, and performance metrics. Apply color coding
            effectively, using distinct colors for positive and negative values to quickly distinguish categories.
            Alternatively, use a continuous diverging color scale for a more nuanced view, especially with a wide range
            of values. Ensure a consistent scale on both sides of the baseline to avoid misleading interpretations.
        """
        ),
        vm.Graph(figure=diverging_bar.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard",
                    components=[make_code_clipboard_from_py_file("diverging_bar.py", mode="vizro")],
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("diverging_bar.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

diverging_stacked_bar_page = vm.Page(
    title="Diverging stacked bar",
    path="deviation/diverging-stacked-bar",
    layout=vm.Grid(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a diverging stacked bar?

            A diverging stacked bar chart is like a stacked bar chart but aligns bars on a central baseline instead of
            the left or right. It displays positive and negative values, with each bar divided into segments for
            different categories. This type of chart is commonly used for percentage shares, especially in survey
            results using Likert scales (e.g., Strongly Disagree, Disagree, Agree, Strongly Agree).

            &nbsp;

            #### When should I use it?

            A diverging stacked bar chart is useful for comparing positive and negative values and showing the
            composition of each bar. However, use this chart with caution: since none of the segments share a
            common baseline, direct comparisons can be more challenging. For clearer comparisons, consider using a
            100% stacked bar chart with a baseline starting from the left or right. For more insights on the potential
            pitfalls, we recommend reading the article from
            [Datawrapper on diverging stacked bar charts](https://blog.datawrapper.de/divergingbars/).
        """
        ),
        vm.Graph(figure=diverging_stacked_bar.fig),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Vizro dashboard",
                    components=[make_code_clipboard_from_py_file("diverging_stacked_bar.py", mode="vizro")],
                ),
                vm.Container(
                    title="Plotly figure",
                    components=[make_code_clipboard_from_py_file("diverging_stacked_bar.py", mode="plotly")],
                ),
            ]
        ),
    ],
)

pages = [butterfly_page, diverging_bar_page, diverging_stacked_bar_page]
