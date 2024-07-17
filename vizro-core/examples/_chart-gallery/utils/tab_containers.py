"""Contains custom components and charts used inside the dashboard."""

import re

import vizro.models as vm

from .custom_charts_comp import FlexContainer, Markdown

vm.Container.add_type("components", Markdown)
vm.Container.add_type("components", FlexContainer)


def tidy_chart_title(chart: str) -> str:
    """Tidy up the chart title by removing prefixes and unwanted characters.

    Note: The pre-fixes are previously given to uniquely create a page ID.
    """
    prefixes_to_remove = [
        "time-",
        "magnitude-",
        "deviation-",
        "distribution-",
        "correlation-",
        "ranking-",
        "flow-",
        "spatial-",
        "part-",
    ]
    pattern = "^(" + "|".join(prefixes_to_remove) + ")"
    chart_without_prefix = re.sub(pattern, "", chart)
    return chart_without_prefix.replace("-", " ").title()


DEVIATION_CHARTS = sorted(
    [
        "diverging-bar",
        # "diverging-stacked-bar",
        "butterfly",
        "surplus",
    ]
)
CORRELATION_CHARTS = [
    "scatter",
    "scatter-matrix",
    "column-line",
    # "connected-scatter",
    "heatmap-matrix",
    "bubble",
]
RANKING_CHARTS = sorted(
    [
        "ordered-bar",
        "ordered-column",
        "ordered-bubble",
        "slope",
        "lollipop",
        "stepped-line",
    ]
)
DISTRIBUTION_CHARTS = sorted(
    [
        "histogram",
        "dot-plot",
        "barcode",
        "boxplot",
        "violin",
        "distribution-butterfly",
        "cumulative-curve",
        # "beeswarm",
    ]
)
MAGNITUDE_CHARTS = sorted(
    [
        "column",
        "bar",
        # "paired-column",
        # "paired-bar",
        "marimekko",
        "bubble",
        "lollipop",
        "radar",
        "parallel",
        "pictogram",
        "bullet",
        "radial",
    ]
)
TIME_CHARTS = sorted(
    [
        "time-line",
        "time-column",
        "gantt",
        "column-line",
        "slope",
        "fan",
        # "area",
        # "connected-scatter",
        "heatmap",
        "bubble-timeline",
        "sparkline",
    ]
)
PART_TO_WHOLE_CHARTS = sorted(
    [
        "stacked-bar",
        "stacked-column",
        "marimekko",
        "funnel",
        "pie",
        "donut",
        "treemap",
        "arc",
        "venn",
        "waterfall",
    ]
)
FLOW_CHARTS = sorted(["sankey", "waterfall", "chord", "network"])
SPATIAL_CHARTS = sorted(["choropleth", "dot-map", "flow-map", "bubble-map"])

ALL_CHARTS = sorted(
    set(
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
)


container_all = vm.Container(
    title="All",
    components=[
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {tidy_chart_title(chart)}
                            """,
                    href=f"/{chart}",
                )
                for chart in ALL_CHARTS
            ],
        )
    ],
)

container_deviation = vm.Container(
    title="Deviation",
    layout=vm.Layout(grid=[[0, 1, 1, 1]], col_gap="40px"),
    components=[
        Markdown(
            text="""
            Deviation enables you to draw attention to variations (+/-) from a fixed reference point.
            Often this reference point is zero, but you might also show a target or a long-term average.
            You can also use deviation to express a positive, neutral or negative sentiment.
            """,
            classname="intro-text",
        ),
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {tidy_chart_title(chart)}
                            """,
                    href=f"/{chart}",
                )
                for chart in DEVIATION_CHARTS
            ],
        ),
    ],
)

container_correlation = vm.Container(
    title="Correlation",
    layout=vm.Layout(grid=[[0, 1, 1, 1]], col_gap="40px"),
    components=[
        Markdown(
            text="""
            Correlation helps you show the relationship between two or more variables. It is important that you
            make it clear to your audience whether or not the relationship is causal, i.e., whether one causes the
            other.
            """,
            classname="intro-text",
        ),
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {tidy_chart_title(chart)}
                            """,
                    href=f"/{chart}",
                )
                for chart in CORRELATION_CHARTS
            ],
        ),
    ],
)

container_ranking = vm.Container(
    title="Ranking",
    layout=vm.Layout(grid=[[0, 1, 1, 1]], col_gap="40px"),
    components=[
        Markdown(
            text="""
            Ranking enables you to present items in an ordered list. You will use this when you want to highlight the
            position of an item rather than its absolute or relative value. You might want to emphasize the most
            interesting points with highlighting or labels to ensure the reader understands what matters most.
            """,
            classname="intro-text",
        ),
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {tidy_chart_title(chart)}
                            """,
                    href=f"/{chart}",
                )
                for chart in RANKING_CHARTS
            ],
        ),
    ],
)

container_distribution = vm.Container(
    title="Distribution",
    layout=vm.Layout(grid=[[0, 1, 1, 1]], col_gap="40px"),
    components=[
        Markdown(
            text="""
            Distribution helps you to present all the possible values (or intervals) of your data and how often they
            occur. You can organize the data to show the number or percentage of items in a specified group, what shape
            the group takes, where the center lies, and how much variability there is in the data. This shape
            (or **skew**) of a distribution can be a powerful way for you to highlight either the existence or lack of
            uniformity or equality in the data.
            """,
            classname="intro-text",
        ),
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {tidy_chart_title(chart)}
                            """,
                    href=f"/{chart}",
                )
                for chart in DISTRIBUTION_CHARTS
            ],
        ),
    ],
)

container_magnitude = vm.Container(
    title="Magnitude",
    layout=vm.Layout(grid=[[0, 1, 1, 1]], col_gap="40px"),
    components=[
        Markdown(
            text="""
            Magnitude allows you to emphasize size comparisons of **counted** items in your data set. You can show
            relative comparisons (whether something is larger or smaller) or absolute differences (where the nuances
            are most interesting). Typically, you will use magnitude for actual numbers versus calculated rates or
            percentages.
            """,
            classname="intro-text",
        ),
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {tidy_chart_title(chart)}
                            """,
                    href=f"/{chart}",
                )
                for chart in MAGNITUDE_CHARTS
            ],
        ),
    ],
)

container_time = vm.Container(
    title="Time",
    layout=vm.Layout(grid=[[0, 1, 1, 1]], col_gap="40px"),
    components=[
        Markdown(
            text="""
            Time helps you draw attention to important trends emerging over a specified period. The time period you
            select could be as short as seconds or as long as centuries. What matters most is selecting the correct
            period of time to best show your audience the message they need to take away.
            """,
            classname="intro-text",
        ),
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {tidy_chart_title(chart)}
                            """,
                    href=f"/{chart}",
                )
                for chart in TIME_CHARTS
            ],
        ),
    ],
)

container_part = vm.Container(
    title="Part-to-whole",
    layout=vm.Layout(grid=[[0, 1, 1, 1]], col_gap="40px"),
    components=[
        Markdown(
            text="""
            Part-to-whole helps you show how one whole item breaks down into its component parts. If you consider the
            size of the parts to be most important, a magnitude chart may be more appropriate.
            """,
            classname="intro-text",
        ),
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {tidy_chart_title(chart)}
                            """,
                    href=f"/{chart}",
                )
                for chart in PART_TO_WHOLE_CHARTS
            ],
        ),
    ],
)

container_flow = vm.Container(
    title="Flow",
    layout=vm.Layout(grid=[[0, 1, 1, 1]], col_gap="40px"),
    components=[
        Markdown(
            text="""
            With flow charts, you can highlight the quantity or the intensity of the movement between more than one
            state or condition. The flow might be steps in a logical sequence or movement between different geographical
            locations.
            """,
            classname="intro-text",
        ),
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {tidy_chart_title(chart)}
                            """,
                    href=f"/{chart}",
                )
                for chart in FLOW_CHARTS
            ],
        ),
    ],
)

container_spatial = vm.Container(
    title="Spatial",
    layout=vm.Layout(grid=[[0, 1, 1, 1]], col_gap="40px"),
    components=[
        Markdown(
            text="""
            Spatial charts allow you to demonstrate precise locations or geographical patterns in your data.
            """,
            classname="intro-text",
        ),
        FlexContainer(
            title="",
            components=[
                vm.Card(
                    text=f"""
                            ![](assets/images/charts/{chart}.svg#chart-icon)

                            #### {tidy_chart_title(chart)}
                            """,
                    href=f"/{chart}",
                )
                for chart in SPATIAL_CHARTS
            ],
        ),
    ],
)
