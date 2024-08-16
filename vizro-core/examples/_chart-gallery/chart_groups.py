"""Defines chart groups."""

import itertools
from dataclasses import dataclass
from typing import List

import pages.correlation
import pages.deviation
import pages.distribution
import pages.flow
import pages.magnitude
import pages.part_to_whole
import pages.ranking
import pages.spatial
import pages.time
import vizro.models as vm


class IncompletePage:
    """Fake vm.Page-like class.

    This has the properties required to make it function sufficiently like a page when generating the navigation cards.
    Only the title is configurable; path is fixed to "".
    """

    def __init__(self, title):  # noqa: D107
        self.title = title

    @property
    def path(self):  # noqa: D102
        return ""


@dataclass
class ChartGroup:
    """Represents a group of charts like "Deviation"."""

    name: str
    pages: List[vm.Page]
    incomplete_pages: List[IncompletePage]
    intro_text: str
    icon: str = ""  # ALL_CHART_GROUP is the only one that doesn't require an icon.


deviation_intro_text = """
Deviation enables you to draw attention to variations (+/-) from a fixed reference point.
Often this reference point is zero, but you might also show a target or a long term average.
You can also use deviation to express a positive, neutral or negative sentiment.
"""
deviation_chart_group = ChartGroup(
    name="Deviation",
    pages=pages.deviation.pages,
    incomplete_pages=[
        IncompletePage(title="Diverging bar"),
        IncompletePage("Diverging stacked bar"),
        IncompletePage(title="Surplus deficit filled line"),
    ],
    icon="Contrast Square",
    intro_text=deviation_intro_text,
)


correlation_intro_text = """
Correlation helps you show the relationship between two or more variables. It is important that you
make it clear to your audience whether or not the relationship is causal, i.e., whether one causes the
other.
"""
correlation_chart_group = ChartGroup(
    name="Correlation",
    pages=pages.correlation.pages,
    incomplete_pages=[
        IncompletePage("Scatter matrix"),
        IncompletePage("Column line"),
        IncompletePage("Heatmap matrix"),
        IncompletePage("Bubble"),
    ],
    icon="Bubble Chart",
    intro_text=correlation_intro_text,
)


ranking_intro_text = """
Ranking enables you to present items in an ordered list. Use this when you want to highlight the
position of an item rather than its absolute or relative value. You might want to emphasize the most
interesting points with highlighting or labels to ensure the reader understands what matters most.
"""
ranking_chart_group = ChartGroup(
    name="Ranking",
    pages=pages.ranking.pages,
    incomplete_pages=[
        IncompletePage("Ordered bubble"),
        IncompletePage("Slope"),
        IncompletePage("Lollipop"),
        IncompletePage("Stepped line"),
        IncompletePage("Bump"),
    ],
    icon="Stacked Bar Chart",
    intro_text=ranking_intro_text,
)


distribution_intro_text = """
Distribution helps you to present all the possible values (or intervals) of your data and how often they
occur. You can organize the data to show the number or percentage of items in a specified group, what shape
the group takes, where the center lies, and how much variability there is in the data. This shape
(or _skew_) of a distribution can be a powerful way for you to highlight either the existence or lack of
uniformity or equality in the data.
"""
distribution_chart_group = ChartGroup(
    name="Distribution",
    pages=pages.distribution.pages,
    incomplete_pages=[
        IncompletePage("Dot plot"),
        IncompletePage("Barcode"),
        IncompletePage("Cumulative curve"),
        IncompletePage("Beeswarm"),
    ],
    icon="Waterfall Chart",
    intro_text=distribution_intro_text,
)

magnitude_intro_text = """
Magnitude allows you to emphasize size comparisons of **counted** items in your data set. You can show
relative comparisons (whether something is larger or smaller) or absolute differences (where the nuances
are most interesting). Typically, you will use magnitude for actual numbers versus calculated rates or
percentages.
"""
magnitude_chart_group = ChartGroup(
    name="Magnitude",
    pages=pages.magnitude.pages,
    incomplete_pages=[
        IncompletePage("Marimekko"),
        IncompletePage("Bubble"),
        IncompletePage("Lollipop"),
        IncompletePage("Radar"),
        IncompletePage("Parallel coordinates"),
        IncompletePage("Pictogram"),
        IncompletePage("Bullet"),
        IncompletePage("Radial"),
    ],
    icon="Bar Chart",
    intro_text=magnitude_intro_text,
)

time_intro_text = """
Time helps you draw attention to important trends emerging over a specified period. The time period you
select could be as short as seconds or as long as centuries. What matters most is selecting the correct
period of time to best show your audience the message they need to take away.
"""
time_chart_group = ChartGroup(
    name="Time",
    pages=pages.time.pages,
    incomplete_pages=[
        IncompletePage("Gantt"),
        IncompletePage("Column line"),
        IncompletePage("Slope"),
        IncompletePage("Fan"),
        IncompletePage("Heatmap"),
        IncompletePage("Bubble timeline"),
        IncompletePage("Sparkline"),
    ],
    icon="Timeline",
    intro_text=time_intro_text,
)


part_to_whole_intro_text = """
Part-to-whole helps you show how one whole item breaks down into its component parts. If you consider the
size of the parts to be most important, a magnitude chart may be more appropriate.
"""
part_to_whole_chart_group = ChartGroup(
    name="Part-to-whole",
    pages=pages.part_to_whole.pages,
    incomplete_pages=[
        IncompletePage("Marimekko"),
        IncompletePage("Funnel"),
        IncompletePage("Arc"),
        IncompletePage("Gridplot"),
        IncompletePage("Venn"),
        IncompletePage("Waterfall"),
    ],
    icon="Donut Small",
    intro_text=part_to_whole_intro_text,
)

flow_intro_text = """
With flow charts, you can highlight the quantity or the intensity of the movement between more than one
state or condition. The flow might be steps in a logical sequence or movement between different geographical
locations.
"""
flow_chart_group = ChartGroup(
    name="Flow",
    pages=pages.flow.pages,
    incomplete_pages=[
        IncompletePage("Waterfall"),
        IncompletePage("Chord"),
        IncompletePage("Network"),
    ],
    icon="Air",
    intro_text=flow_intro_text,
)

spatial_intro_text = """
Spatial charts allow you to demonstrate precise locations or geographical patterns in your data.
"""
spatial_chart_group = ChartGroup(
    name="Spatial",
    pages=pages.spatial.pages,
    incomplete_pages=[
        IncompletePage("Dot map"),
        IncompletePage("Flow map"),
        IncompletePage("Bubble map"),
    ],
    icon="Map",
    intro_text=spatial_intro_text,
)


CHART_GROUPS = [
    deviation_chart_group,
    correlation_chart_group,
    ranking_chart_group,
    distribution_chart_group,
    magnitude_chart_group,
    time_chart_group,
    part_to_whole_chart_group,
    flow_chart_group,
    spatial_chart_group,
]

all_intro_text = """
This dashboard shows a gallery of charts. It includes guidance on when to use each chart type and sample Python code
to create them using [Plotly](https://plotly.com/python/) and [Vizro](https://github.com/mckinsey/vizro).

Inspired by the
[FT Visual Vocabulary](https://github.com/Financial-Times/chart-doctor/blob/main/visual-vocabulary/README.md)
and [the Graphic Continuum](https://www.informationisbeautifulawards.com/showcase/611-the-graphic-continuum):

- FT Graphic: Alan Smith, Chris Campbell, Ian Bott, Liz Faunce, Graham Parrish, Billy Ehrenberg, Paul McCallum,
Martin Stabe.

- The Graphic Continuum: Jon Swabish and Severino Ribecca


"""


# This contains all pages used across all chart groups, without de-duplicating. De-duplication is done where required
# by remove_duplicates.
ALL_CHART_GROUP = ChartGroup(
    name="All",
    pages=list(itertools.chain(*(chart_group.pages for chart_group in CHART_GROUPS))),
    incomplete_pages=list(itertools.chain(*(chart_group.incomplete_pages for chart_group in CHART_GROUPS))),
    intro_text=all_intro_text,
)
