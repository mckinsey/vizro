"""Dev app to try things out."""

from typing import Optional

import dash_bootstrap_components as dbc
import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from dash import html
from vizro import Vizro
from vizro.figures import kpi_card
from vizro.models.types import capture

tips = px.data.tips


@capture("figure")  # (1)!
def custom_kpi_card(
    data_frame: pd.DataFrame,
    value_column: str,
    *,
    value_format: str = "{value}",
    agg_func: str = "sum",
    title: Optional[str] = None,
    icon: Optional[str] = None,
) -> dbc.Card:  # (2)!
    """Creates a custom KPI card."""
    title = title or f"{agg_func} {value_column}".title()
    value = data_frame[value_column].agg(agg_func)

    header = dbc.CardHeader(
        [
            html.H2(title),
            html.P(icon, className="material-symbols-outlined") if icon else None,  # (3)!
        ]
    )
    body = dbc.CardBody([value_format.format(value=value)])
    return dbc.Card([header, body], className="card-kpi")


page = vm.Page(
    title="Create your own KPI card",
    layout=vm.Layout(grid=[[0, 1, -1, -1]] + [[-1, -1, -1, -1]] * 3),  # (4)!
    components=[
        vm.Figure(
            figure=kpi_card(  # (5)!
                data_frame=tips,
                value_column="tip",
                value_format="${value:.2f}",
                icon="shopping_cart",
                title="Default KPI card",
            )
        ),
        vm.Figure(
            figure=custom_kpi_card(  # (6)!
                data_frame=tips,
                value_column="tip",
                value_format="${value:.2f}",
                icon="payment",
                title="Custom KPI card",
            )
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
