"""Dev app to try things out."""

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, html
from vizro.figures.undecorated import kpi_card, kpi_card_reference

df_kpi = pd.DataFrame({"Actual": [100, 200, 700], "Reference": [100, 300, 500], "Category": ["A", "B", "C"]})

# Add single CSS file figures.css or
vizro_css = "https://raw.githubusercontent.com/mckinsey/vizro/main/vizro-core/src/vizro/static/css/figures.css"

# Add entire assets folder from Vizro
app = Dash(
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined",
        vizro_css,
    ],
)

app.layout = [
    html.H1(children="Title of Dash App", style={"textAlign": "center"}),
    html.Div(
        children=[
            kpi_card(
                data_frame=df_kpi,
                value_column="Actual",
                value_format="${value:.2f}",
                icon="shopping_cart",
                title="KPI Card I",
            ),
            kpi_card_reference(
                data_frame=df_kpi,
                value_column="Actual",
                reference_column="Reference",
                icon="payment",
                title="KPI Card II",
            ),
        ]
    ),
]

if __name__ == "__main__":
    app.run()
