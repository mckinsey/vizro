"""Deviation charts."""

import plotly.io as pio
import vizro.models as vm
import vizro.plotly.express as px
from custom_charts import diverging_stacked_bar

from pages._factories import butterfly_factory
from pages._pages_utils import PAGE_GRID, make_code_clipboard_from_py_file, pastries

butterfly = butterfly_factory("deviation")


diverging_bar = vm.Page(
    title="Diverging bar",
    path="deviation/diverging-bar",
    layout=vm.Layout(grid=PAGE_GRID),
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
        vm.Graph(
            figure=px.bar(
                pastries.sort_values("Profit Ratio"),
                orientation="h",
                x="Profit Ratio",
                y="pastry",
                color="Profit Ratio",
                color_continuous_scale=pio.templates["vizro_dark"].layout.colorscale.diverging,
                color_continuous_midpoint=0,
            ),
        ),
        make_code_clipboard_from_py_file("diverging_bar.py"),
    ],
)

diverging_stacked_bar = vm.Page(
    title="Diverging stacked bar",
    path="deviation/diverging-stacked-bar",
    layout=vm.Layout(grid=PAGE_GRID),
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
        vm.Graph(
            title="Would you recommend the pastry to your friends?",
            figure=diverging_stacked_bar(
                data_frame=pastries,
                y="pastry",
                category_pos=["Agree", "Strongly Agree"],
                category_neg=["Disagree", "Strongly Disagree"],
                color_discrete_map={
                    "Strongly Agree": "#1a85ff",
                    "Agree": "#70a1ff",
                    "Disagree": "#ff5584",
                    "Strongly Disagree": "#d41159",
                },
            ),
        ),
        make_code_clipboard_from_py_file("diverging_stacked_bar.py"),
    ],
)

pages = [butterfly, diverging_bar, diverging_stacked_bar]
