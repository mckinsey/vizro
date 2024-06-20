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


@capture("figure")
def custom_kpi_card(
    data_frame: pd.DataFrame,
    value_column: str,
    *,
    value_format: str = "{value}",
    agg_func: str = "sum",
    title: Optional[str] = None,
    icon: Optional[str] = None,
) -> dbc.Card:
    """Creates a custom KPI Card."""
    title = title or f"{agg_func} {value_column}".title()
    value = data_frame[value_column].agg(agg_func)

    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.H2(title),
                    html.P(icon, className="material-symbols-outlined") if icon else None,
                ],
            ),
            dbc.CardBody([value_format.format(value=value)]),
        ],
        className="card-kpi",
    )


page = vm.Page(
    title="Create your own KPI Card",
    layout=vm.Layout(grid=[[0, 1, -1, -1]] + [[-1, -1, -1, -1]] * 3),
    components=[
        vm.Figure(
            figure=kpi_card(
                data_frame=tips,
                value_column="tip",
                value_format="${value:.2f}",
                icon="shopping_cart",
                title="Default KPI Card",
            )
        ),
        vm.Figure(
            figure=custom_kpi_card(
                data_frame=tips,
                value_column="tip",
                value_format="${value:.2f}",
                icon="payment",
                title="Custom KPI Card",
            )
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
