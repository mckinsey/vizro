"""Contains custom components and charts used inside the dashboard."""

import vizro.models as vm
import vizro.plotly.express as px

from ._charts import CodeClipboard, FlexContainer, HtmlIntro

gapminder = px.data.gapminder()
vm.Page.add_type("components", CodeClipboard)
vm.Page.add_type("components", FlexContainer)
vm.Container.add_type("components", HtmlIntro)
vm.Container.add_type("components", FlexContainer)


DEVIATION_CHARTS = ["line", "scatter", "slope", "lollipop", "diverging-bar"]
CORRELATION_CHARTS = ["scatter"]
RANKING_CHARTS = [
    "column",
    "stacked-column",
    "ordered-bubble",
    "column-line",
    "bar",
    "donut",
    "arc",
    "lollipop",
    "waterfall",
    "diverging-bar",
    "boxplot",
]
DISTRIBUTION_CHARTS = [
    "histogram",
    "butterfly",
    "pie",
    "donut",
    "arc",
    "violin",
    "lollipop",
    "cumulative-curve",
    "waterfall",
    "treemap",
    "venn",
    "barcode",
]
MAGNITUDE_CHARTS = [
    "column",
    "marimekko",
    "stacked-column",
    "ordered-bubble",
    "column-line",
    "surplus",
    "butterfly",
    "bubble-timeline",
    "bar",
    "pie",
    "donut",
    "arc",
    "violin",
    "slope",
    "lollipop",
    "cumulative-curve",
    "waterfall",
    "treemap",
    "venn",
    "diverging-bar",
    "bullet",
    "dot-plot",
]
TIME_CHARTS = [
    "column",
    "gantt",
    "column-line",
    "bubble-timeline",
    "bar",
    "line",
    "scatter",
    "lollipop",
    "diverging-bar",
    "stepped-line",
    "sparkline",
]
PART_TO_WHOLE_CHARTS = [
    "marimekko",
    "stacked-column",
    "column-line",
    "pie",
    "donut",
    "arc",
    "waterfall",
    "treemap",
    "venn",
]
FLOW_CHARTS = ["gantt", "line", "slope", "stepped-line"]
SPATIAL_CHARTS = ["choropleth", "dot-density", "flow-map"]

ALL_CHARTS = (
    DEVIATION_CHARTS
    + CORRELATION_CHARTS
    + RANKING_CHARTS
    + DISTRIBUTION_CHARTS
    + MAGNITUDE_CHARTS
    + TIME_CHARTS
    + PART_TO_WHOLE_CHARTS
    + FLOW_CHARTS
    + SPATIAL_CHARTS
)


# HOMEPAGE -------------------------------------------------------------
home_all = vm.Container(
    title="All",
    components=[
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {chart.replace("-", " ").title()}
                            """
                )
                for chart in set(ALL_CHARTS)
            ],
        )
    ],
)

home_deviation = vm.Container(
    title="Deviation",
    layout=vm.Layout(grid=[[0, 1, 1, 1]], col_gap="40px"),
    components=[
        HtmlIntro(
            text="""
            Deviation enables you to draw attention to variations (+/-) from a fixed reference point.
            Often this reference point is zero, but you might also show a target or a long-term average.
            You can also use deviation to express a positive, neutral or negative sentiment.
            """
        ),
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {chart.replace("-", " ").title()}
                            """
                )
                for chart in DEVIATION_CHARTS
            ],
        ),
    ],
)

home_correlation = vm.Container(
    title="Correlation",
    layout=vm.Layout(grid=[[0, 1, 1, 1]], col_gap="40px"),
    components=[
        HtmlIntro(
            text="""
            Correlation helps you show the relationship between two or more variables. It is important that you
            make it clear to your audience whether or not the relationship is causal, i.e., whether one causes the
            other.
            """
        ),
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {chart.replace("-", " ").title()}
                            """
                )
                for chart in CORRELATION_CHARTS
            ],
        ),
    ],
)

home_ranking = vm.Container(
    title="Ranking",
    layout=vm.Layout(grid=[[0, 1, 1, 1]], col_gap="40px"),
    components=[
        HtmlIntro(
            text="""
            Ranking enables you to present items in an ordered list. You will use this when you want to highlight the
            position of an item rather than its absolute or relative value. You might want to emphasise the most
            interesting points with highlighting or labels to ensure the reader understands what matters most.
            """
        ),
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {chart.replace("-", " ").title()}
                            """
                )
                for chart in RANKING_CHARTS
            ],
        ),
    ],
)

home_distribution = vm.Container(
    title="Distribution",
    layout=vm.Layout(grid=[[0, 1, 1, 1]], col_gap="40px"),
    components=[
        HtmlIntro(
            text="""
            Distribution helps you to present all the possible values (or intervals) of your data and how often they
            occur. You can organise the data to show the number or percentage of items in a specified group, what shape
            the group takes, where the centre lies, and how much variability there is in the data. This shape
            (or ‘skew’) of a distribution can be a powerful way for you to highlight either the existence or lack of
            uniformity or equality in the data.
            """
        ),
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {chart.replace("-", " ").title()}
                            """
                )
                for chart in DISTRIBUTION_CHARTS
            ],
        ),
    ],
)

home_magnitude = vm.Container(
    title="Magnitude",
    layout=vm.Layout(grid=[[0, 1, 1, 1]], col_gap="40px"),
    components=[
        HtmlIntro(
            text="""
            Magnitude allows you to emphasise size comparisons of ‘counted’ items in your data set. You can show
            relative comparisons (whether something is larger or smaller) or absolute differences (where the nuances
            are most interesting). Typically, you will use magnitude for actual numbers versus calculated rates or
            percentages.
            """
        ),
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {chart.replace("-", " ").title()}
                            """,
                    href=f"/{chart}",
                )
                for chart in MAGNITUDE_CHARTS
            ],
        ),
    ],
)

home_time = vm.Container(
    title="Time",
    layout=vm.Layout(grid=[[0, 1, 1, 1]], col_gap="40px"),
    components=[
        HtmlIntro(
            text="""
            Time helps you draw attention to important trends emerging over a specified period. The time period you
            select could be as short as seconds or as long as centuries. What matters most is selecting the correct
            period of time to best show your audience the message they need to take away.
            """
        ),
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {chart.replace("-", " ").title()}
                            """
                )
                for chart in TIME_CHARTS
            ],
        ),
    ],
)

home_part = vm.Container(
    title="Part-to-whole",
    layout=vm.Layout(grid=[[0, 1, 1, 1]], col_gap="40px"),
    components=[
        HtmlIntro(
            text="""
            Part-to-whole helps you show how one whole item breaks down into its component parts. If you consider the
            size of the parts to be most important, a magnitude chart may be more appropriate.
            """
        ),
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {chart.replace("-", " ").title()}
                            """
                )
                for chart in PART_TO_WHOLE_CHARTS
            ],
        ),
    ],
)

home_flow = vm.Container(
    title="Flow",
    layout=vm.Layout(grid=[[0, 1, 1, 1]], col_gap="40px"),
    components=[
        HtmlIntro(
            text="""
            With flow charts, you can highlight the quantity or the intensity of the movement between more than one
            state or condition. The flow might be steps in a logical sequence or movement between different geographical
            locations.
            """
        ),
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {chart.replace("-", " ").title()}
                            """
                )
                for chart in FLOW_CHARTS
            ],
        ),
    ],
)

home_spatial = vm.Container(
    title="Spatial",
    layout=vm.Layout(grid=[[0, 1, 1, 1]], col_gap="40px"),
    components=[
        HtmlIntro(
            text="""
            Spatial charts allow you to demonstrate precise locations or geographical patterns in your data.
            """
        ),
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {chart.replace("-", " ").title()}
                            """
                )
                for chart in SPATIAL_CHARTS
            ],
        ),
    ],
)
