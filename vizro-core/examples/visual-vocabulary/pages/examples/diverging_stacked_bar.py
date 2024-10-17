from typing import Optional

import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture

pastries = pd.DataFrame(
    {
        "pastry": [
            "Scones",
            "Bagels",
            "Muffins",
            "Cakes",
            "Donuts",
            "Cookies",
            "Croissants",
            "Eclairs",
            "Brownies",
            "Tarts",
            "Macarons",
            "Pies",
        ],
        "Profit Ratio": [-0.10, -0.15, -0.05, 0.10, 0.05, 0.20, 0.15, -0.08, 0.08, -0.12, 0.02, -0.07],
        "Strongly Disagree": [20, 30, 10, 5, 15, 5, 10, 25, 8, 20, 5, 10],
        "Disagree": [30, 25, 20, 10, 20, 10, 15, 30, 12, 30, 10, 15],
        "Agree": [30, 25, 40, 40, 45, 40, 40, 25, 40, 30, 45, 35],
        "Strongly Agree": [20, 20, 30, 45, 20, 45, 35, 20, 40, 20, 40, 40],
    }
)


@capture("graph")
def diverging_stacked_bar(
    data_frame,
    y: str,
    category_pos: List[str],
    category_neg: List[str],
    color_discrete_map: Optional[dict[str, str]] = None,
) -> go.Figure:
    """Creates a horizontal diverging stacked bar chart (with positive and negative values only) using Plotly's go.Bar.

    This type of chart is a variant of the standard stacked bar chart, with bars aligned on a central baseline to
    show both positive and negative values. Each bar is segmented to represent different categories.

    This function is not suitable for diverging stacked bar charts that include a neutral category.

    Inspired by: https://community.plotly.com/t/need-help-in-making-diverging-stacked-bar-charts/34023

    Args:
       data_frame (pd.DataFrame): The data frame for the chart.
       y (str): The name of the categorical column in the data frame to be used for the y-axis (categories)
       category_pos (List[str]): List of column names in the data frame representing positive values. Columns should be
            ordered from least to most positive.
       category_neg (List[str]): List of column names in the DataFrame representing negative values. Columns should be
            ordered from least to most negative.
       color_discrete_map: Optional[dict[str, str]]: A dictionary mapping category names to color strings.

    Returns:
       go.Figure: A Plotly Figure object representing the horizontal diverging stacked bar chart.
    """
    fig = go.Figure()

    # Add traces for negative categories
    for column in category_neg:
        fig.add_trace(
            go.Bar(
                x=-data_frame[column].values,
                y=data_frame[y],
                orientation="h",
                name=column,
                marker_color=color_discrete_map.get(column, None) if color_discrete_map else None,
            )
        )

    # Add traces for positive categories
    for column in category_pos:
        fig.add_trace(
            go.Bar(
                x=data_frame[column],
                y=data_frame[y],
                orientation="h",
                name=column,
                marker_color=color_discrete_map.get(column, None) if color_discrete_map else None,
            )
        )

    # Update layout and add central baseline
    fig.update_layout(barmode="relative")
    fig.add_vline(x=0, line_width=2, line_color="grey")

    # Update legend order to go from most negative to most positive
    category_order = category_neg[::-1] + category_pos
    for i, category in enumerate(category_order):
        fig.update_traces(legendrank=i, selector=({"name": category}))

    return fig


page = vm.Page(
    title="Diverging stacked bar",
    components=[
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
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
