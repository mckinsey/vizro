"""Example app to show all features of Vizro."""

from time import sleep
from typing import Literal, Optional

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from dash import dash_table, dcc, get_asset_url, html
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.figures import kpi_card, kpi_card_reference
from vizro.models.types import capture
from vizro.tables import dash_ag_grid, dash_data_table

iris = px.data.iris()
tips = px.data.tips()
stocks = px.data.stocks(datetimes=True)
gapminder = px.data.gapminder()
gapminder_2007 = px.data.gapminder().query("year == 2007")
gapminder_2007["is_europe"] = gapminder["continent"] == "Europe"
waterfall_df = pd.DataFrame(
    {
        "measure": ["relative", "relative", "total", "relative", "relative", "total"],
        "x": ["Sales", "Consulting", "Net revenue", "Purchases", "Other expenses", "Profit before tax"],
        "text": ["+60", "+80", "", "-40", "-20", "Total"],
        "y": [60, 80, 0, -40, -20, 0],
    }
)
custom_fig_df = pd.DataFrame(
    {
        "text": [
            "Lorem ipsum dolor sit amet, consetetur sadipscing no sea elitr sed diam nonumy.",
            "Sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat.",
            "Sed diam voluptua. At vero eos et accusam et justo no duo dolores et ea rebum.",
            "Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
            "Lorem ipsum dolor sit amet, consetetur sadipscing no sea est elitr dolor sit amet.",
            "Sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat.",
        ]
        * 2
    }
)


chart_interaction = vm.Page(
    title="Chart interaction",
    components=[
        vm.Graph(
            figure=px.box(
                gapminder_2007,
                x="continent",
                y="lifeExp",
                color="continent",
                custom_data=["continent"],
            ),
            # actions=[vm.Action(function=filter_interaction(targets=["scatter_relation_2007"]))],
        ),
        vm.Graph(
            id="scatter_relation_2007",
            figure=px.scatter(
                gapminder_2007,
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
            ),
        ),
    ],
)
