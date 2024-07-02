"""Contains custom components and charts used inside the dashboard."""

import vizro.models as vm

from ._charts import HtmlIntro

vm.Container.add_type("components", HtmlIntro)

# HOMEPAGE -------------------------------------------------------------
home_all = vm.Container(title="All", components=[vm.Card(text="""Placeholder""")])
home_deviation = vm.Container(
    title="Deviation",
    components=[
        HtmlIntro(
            text="""
            Deviation enables you to draw attention to variations (+/-) from a fixed reference point.
            Often this reference point is zero, but you might also show a target or a long-term average.
            You can also use deviation to express a positive, neutral or negative sentiment.
            """
        )
    ],
)

home_correlation = vm.Container(
    title="Correlation",
    components=[
        HtmlIntro(
            text="""
            Correlation helps you show the relationship between two or more variables. It is important that you
            make it clear to your audience whether or not the relationship is causal, i.e., whether one causes the
            other.
            """
        )
    ],
)

home_ranking = vm.Container(
    title="Ranking",
    components=[
        HtmlIntro(
            text="""
            Ranking enables you to present items in an ordered list. You will use this when you want to highlight the
            position of an item rather than its absolute or relative value. You might want to emphasise the most
            interesting points with highlighting or labels to ensure the reader understands what matters most.
            """
        )
    ],
)

home_distribution = vm.Container(
    title="Distribution",
    components=[
        HtmlIntro(
            text="""
            Distribution helps you to present all the possible values (or intervals) of your data and how often they
            occur. You can organise the data to show the number or percentage of items in a specified group, what shape
            the group takes, where the centre lies, and how much variability there is in the data. This shape
            (or ‘skew’) of a distribution can be a powerful way for you to highlight either the existence or lack of
            uniformity or equality in the data.
            """
        )
    ],
)

home_magnitude = vm.Container(
    title="Magnitude",
    components=[
        HtmlIntro(
            text="""
            Magnitude allows you to emphasise size comparisons of ‘counted’ items in your data set. You can show
            relative comparisons (whether something is larger or smaller) or absolute differences (where the nuances
            are most interesting). Typically, you will use magnitude for actual numbers versus calculated rates or
            percentages.
            """
        )
    ],
)

home_time = vm.Container(
    title="Time",
    components=[
        HtmlIntro(
            text="""
            Time helps you draw attention to important trends emerging over a specified period. The time period you
            select could be as short as seconds or as long as centuries. What matters most is selecting the correct
            period of time to best show your audience the message they need to take away.
            """
        )
    ],
)

home_part = vm.Container(
    title="Part-to-whole",
    components=[
        HtmlIntro(
            text="""
            Part-to-whole helps you show how one whole item breaks down into its component parts. If you consider the
            size of the parts to be most important, a magnitude chart may be more appropriate.
            """
        )
    ],
)

home_flow = vm.Container(
    title="Flow",
    components=[
        HtmlIntro(
            text="""
            With flow charts, you can highlight the quantity or the intensity of the movement between more than one
            state or condition. The flow might be steps in a logical sequence or movement between different geographical
            locations.
            """
        )
    ],
)

home_spatial = vm.Container(
    title="Spatial",
    components=[
        HtmlIntro(
            text="""
            Spatial charts allow you to demonstrate precise locations or geographical patterns in your data.
            """
        )
    ],
)
