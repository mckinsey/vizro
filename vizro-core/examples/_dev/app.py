"""Dev app to try things out."""

from typing import Optional

import dash_bootstrap_components as dbc
import pandas as pd
import vizro.models as vm
from dash import html
from vizro import Vizro
from vizro.models.types import capture

df = pd.DataFrame([[67434, 65553, "A"], [6434, 6553, "B"], [34, 53, "C"]], columns=["Actual", "Reference", "Category"])


@capture("figure")
def kpi_card_custom(  # noqa: PLR0913
    data_frame: pd.DataFrame,
    value_column: str,
    *,
    value_format: str = "{value}",
    agg_func: str = "sum",
    title: Optional[str] = None,
    icon: Optional[str] = None,
) -> dbc.Card:
    """Creates a styled KPI (Key Performance Indicator) card displaying a value."""
    title = title or f"{agg_func} {value_column}".title()
    value = data_frame[value_column].agg(agg_func)

    return dbc.Card(
        [
            html.P(icon, className="material-symbols-outlined") if icon else None,
            html.Div(
                [html.H2(value_format.format(value=value), className="value"), html.H3(title, className="title")],
                className="value-and-title",
            ),
        ],
        className="card-kpi-custom",
    )


page = vm.Page(
    title="KPI Indicators",
    layout=vm.Layout(grid=[[0, 1, 2]] + [[-1, -1, -1]] * 3),
    components=[
        vm.Figure(
            figure=kpi_card_custom(
                data_frame=df, value_column="Actual", agg_func="sum", title="Revenue", icon="shopping_cart"
            )
        ),
        vm.Figure(
            figure=kpi_card_custom(
                data_frame=df, value_column="Actual", agg_func="mean", title="Sales", icon="payments"
            )
        ),
        vm.Figure(
            figure=kpi_card_custom(
                data_frame=df, value_column="Actual", agg_func="median", title="Profit", icon="shopping_bag"
            )
        ),
    ],
    controls=[vm.Filter(column="Category")],
)


dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
