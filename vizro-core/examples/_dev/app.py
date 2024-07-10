"""Dev app to try things out."""

import pandas as pd
from dash import Dash, html
from vizro.figures.undecorated import kpi_card, kpi_card_reference

df_kpi = pd.DataFrame({"Actual": [100, 200, 700], "Reference": [100, 300, 500], "Category": ["A", "B", "C"]})

# Add single CSS file figures.css or
vizro_bootstrap = (
    "https://raw.githubusercontent.com/mckinsey/vizro/main/vizro-core/src/vizro/static/css/vizro-bootstrap.min.css"
)
vizro_css = "https://raw.githubusercontent.com/mckinsey/vizro/main/vizro-core/src/vizro/static/css/figures.css"
vizro_tokens = "https://raw.githubusercontent.com/mckinsey/vizro/main/vizro-core/src/vizro/static/css/token_names.css"
vizro_variables = "https://raw.githubusercontent.com/mckinsey/vizro/main/vizro-core/src/vizro/static/css/variables.css"

# Add entire assets folder from Vizro
app = Dash(
    external_stylesheets=[
        # dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined",
        vizro_tokens,
        vizro_variables,
        vizro_bootstrap,
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
        ],
        className="vizro_dark",
    ),
]

if __name__ == "__main__":
    app.run()
