"""Contains variables that store each chart page."""

import vizro.models as vm
import vizro.plotly.express as px

from ._page_utils import DATA_DICT, PAGE_GRID
from .chart_factory import (
    bar_factory,
    butterfly_factory,
    column_factory,
    line_factory,
    scatter_factory,
    treemap_factory,
)
from .custom_extensions import CodeClipboard, FlexContainer, Markdown, sankey

# COMPONENTS --------------------------------------------------------
vm.Page.add_type("components", CodeClipboard)
vm.Page.add_type("components", FlexContainer)
vm.Container.add_type("components", Markdown)


# PAGES -------------------------------------------------------------
line = line_factory("Line", "Line")
time_line = line_factory("Time-Line", "Line")
time_column = column_factory("Time-Column", "Column")
scatter = scatter_factory("Scatter", "Scatter")
bar = bar_factory("Bar", "Bar")
ordered_bar = bar_factory("Ordered Bar", "Ordered Bar")
column = column_factory("Column", "Column")
ordered_column = column_factory("Ordered Column", "Ordered Column")
treemap = treemap_factory("Treemap", "Treemap")
magnitude_treemap = treemap_factory("Magnitude-Treemap", "Treemap")
butterfly_page = butterfly_factory("Butterfly", "Butterfly")
distribution_butterfly = butterfly_factory("Distribution-Butterfly", "Butterfly")


pie = vm.Page(
    title="Pie",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a pie chart?

            A pie chart is a circular chart divided into segments to show proportions and percentages between
            categories. The circle represents the whole.

            &nbsp;

            #### When to use it?

            Use the pie chart when you need to show your audience a quick view of how data is distributed
            proportionately, with percentages highlighted. The different values you present must add up to a total and
            equal 100%.

            The downsides are that pie charts tend to occupy more space than other charts, they don`t
            work well with more than a few values because labeling small segments is challenging, and it can be
            difficult to accurately compare the sizes of the segments.
        """
        ),
        vm.Graph(
            figure=px.pie(
                data_frame=DATA_DICT["tips"],
                values="tip",
                names="day",
            )
        ),
        CodeClipboard(
            text="""
                ```python
                import vizro.models as vm
                import vizro.plotly.express as px
                from vizro import Vizro

                tips = px.data.tips()

                page = vm.Page(
                    title="Pie",
                    components=[
                        vm.Graph(
                            figure=px.pie(
                                data_frame=tips,
                                values="tip",
                                names="day",
                            )
                        )
                    ],
                )

                dashboard = vm.Dashboard(pages=[page])
                Vizro().build(dashboard).run()
                ```
                """
        ),
    ],
)


donut = vm.Page(
    title="Donut",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""

            #### What is a donut chart?

            A donut chart looks like a pie chart, but has a blank space in the center which may contain additional
            information.

            &nbsp;

            #### When to use it?

            A donut chart can be used in place of a pie chart, particularly when you are short of space or have extra
            information you would like to share about the data. It may also be more effective if you wish your audience
            to focus on the length of the arcs of the sections instead of the proportions of the segment sizes.
        """
        ),
        vm.Graph(
            figure=px.pie(
                data_frame=DATA_DICT["tips"],
                values="tip",
                names="day",
                hole=0.4,
            )
        ),
        CodeClipboard(
            text="""
                ```python
                import vizro.models as vm
                import vizro.plotly.express as px
                from vizro import Vizro

                tips = px.data.tips()

                page = vm.Page(
                    title="Donut",
                    components=[
                        vm.Graph(
                            figure=px.pie(
                                data_frame=tips,
                                values="tip",
                                names="day",
                                hole=0.4,
                            )
                        )
                    ],
                )

                dashboard = vm.Dashboard(pages=[page])
                Vizro().build(dashboard).run()
                ```
                """
        ),
    ],
)


boxplot = vm.Page(
    title="Boxplot",
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
        CodeClipboard(
            text="""
                ```python
                import vizro.models as vm
                import vizro.plotly.express as px
                from vizro import Vizro

                tips = px.data.tips()

                page = vm.Page(
                    title="Boxplot",
                    components=[
                        vm.Graph(
                            figure=px.boxplot(
                                data_frame=tips,
                                y="total_bill",
                                x="day",
                                color="day",
                            )
                        ),
                    ],
                )

                dashboard = vm.Dashboard(pages=[page])
                Vizro().build(dashboard).run()
                ```
                """
        ),
    ],
)


violin = vm.Page(
    title="Violin",
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
        CodeClipboard(
            text="""
                ```python
                import vizro.models as vm
                import vizro.plotly.express as px
                from vizro import Vizro

                tips = px.data.tips()

                page = vm.Page(
                    title="Violin",
                    components=[
                        vm.Graph(
                            figure=px.violin(
                                data_frame=tips,
                                y="total_bill",
                                x="day",
                                color="day",
                            )
                        ),
                    ],
                )

                dashboard = vm.Dashboard(pages=[page])
                Vizro().build(dashboard).run()
                ```
                """
        ),
    ],
)

choropleth = vm.Page(
    title="Choropleth",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""
            #### What is a choropleth map?

            A choropleth map is a map in which geographical areas are colored, shaded or patterned in relation to a
            specific data variable.

            &nbsp;

            #### When to use it?

            Use a chloropleth map when you wish to show how a measurement varies across a geographic area, or to show
            variability or patterns within a region. Typically, you will blend one color into another, take a color
            shade from light to dark, or introduce patterns to depict the variation in the data.

            Be aware that it may be difficult for your audience to accurately read or compare values on the map
            depicted by color.

        """
        ),
        vm.Graph(
            figure=px.choropleth(
                DATA_DICT["fips_unemp"],
                geojson=DATA_DICT["counties"],
                locations="fips",
                color="unemp",
                range_color=(0, 12),
                scope="usa",
            )
        ),
        CodeClipboard(
            text="""
                ```python
                import json
                from urllib.request import urlopen

                import pandas as pd
                import vizro.models as vm
                import vizro.plotly.express as px
                from vizro import Vizro

                with urlopen(
                    "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
                ) as response:
                    counties = json.load(response)

                fips_unemp = pd.read_csv(
                    "https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                    dtype={"fips": str},
                )


                page = vm.Page(
                    title="Choropleth",
                    components=[
                        vm.Graph(
                            figure=px.choropleth(
                                fips_unemp,
                                geojson=counties,
                                locations="fips",
                                color="unemp",
                                range_color=(0, 12),
                                scope="usa",
                            )
                        ),
                    ],
                )

                dashboard = vm.Dashboard(pages=[page])
                Vizro().build(dashboard).run()
                ```
                """
        ),
    ],
)


sankey_page = vm.Page(
    title="Sankey",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""
            #### What is a sankey chart?

            A Sankey chart is a type of flow diagram that illustrates how resources or values move between different
            stages or entities. The width of the arrows in the chart is proportional to the quantity of the flow,
            making it easy to see where the largest movements occur.

            &nbsp;

            #### When to use it?

            Use a Sankey chart when you want to visualize the flow of resources, energy, money, or other values from
            one point to another. It is particularly useful for showing distributions and transfers within a system,
            such as energy usage, cost breakdowns, or material flows.

            Be mindful that Sankey charts can become cluttered if there are too many nodes or flows.
            To maintain clarity, focus on highlighting the most significant flows and keep the chart as simple as
            possible.
        """
        ),
        vm.Graph(
            figure=sankey(
                data_frame=DATA_DICT["sankey_data"],
                labels=["A1", "A2", "B1", "B2", "C1", "C2", "D1"],
                source="Origin",
                target="Destination",
                value="Value",
            ),
        ),
        CodeClipboard(
            text="""
                ```python
                import pandas as pd
                import plotly.graph_objects as go
                import vizro.models as vm
                from vizro import Vizro
                from vizro.models.types import capture
                from typing import List

                sankey_data = pd.DataFrame(
                    {
                        "Origin": [0, 1, 2, 1, 2, 4, 0],  # indices inside labels
                        "Destination": [1, 2, 3, 4, 5, 5, 6],  # indices inside labels
                        "Value": [10, 4, 8, 6, 4, 8, 8],
                    }
                )


                @capture("graph")
                def sankey(
                    data_frame: pd.DataFrame,
                    source: str,
                    target: str,
                    value: str,
                    labels: List[str],
                ):
                    fig = go.Figure(
                        data=[
                            go.Sankey(
                                node=dict(pad=16, thickness=16, label=labels,),
                                link=dict(
                                    source=data_frame[source],
                                    target=data_frame[target],
                                    value=data_frame[value],
                                    label=labels,
                                    color="rgba(205, 209, 228, 0.4)",
                                ),
                            )
                        ]
                    )
                    fig.update_layout(barmode="relative")
                    return fig


                page = vm.Page(
                    title="Sankey",
                    components=[
                        vm.Graph(
                            figure=sankey(
                                data_frame=sankey_data,
                                labels=["A1", "A2", "B1", "B2", "C1", "C2", "D1"],
                                source="Origin",
                                target="Destination",
                                value="Value",
                            ),
                        ),
                    ],
                )

                dashboard = vm.Dashboard(pages=[page])
                Vizro().build(dashboard).run()
                ```
                """
        ),
    ],
)
