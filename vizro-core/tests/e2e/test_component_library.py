import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, html
from e2e_asserts import assert_image_equal, make_screenshot_and_paths

from vizro.figures.library import kpi_card, kpi_card_reference

df_kpi = pd.DataFrame(
    {
        "Actual": [100, 200, 700],
        "Reference": [100, 300, 500],
        "Category": ["A", "B", "C"],
    }
)

example_cards = [
    kpi_card(data_frame=df_kpi, value_column="Actual", title="KPI with value"),
    kpi_card(
        data_frame=df_kpi,
        value_column="Actual",
        title="KPI with aggregation",
        agg_func="median",
    ),
    kpi_card(
        data_frame=df_kpi,
        value_column="Actual",
        title="KPI formatted",
        value_format="${value:.2f}",
    ),
    kpi_card(
        data_frame=df_kpi,
        value_column="Actual",
        title="KPI with icon",
        icon="shopping_cart",
    ),
]

example_reference_cards = [
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        title="KPI ref. (pos)",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        agg_func="median",
        title="KPI ref. (neg)",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        title="KPI ref. formatted",
        value_format="{value}€",
        reference_format="{delta}€ vs. last year ({reference}€)",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        title="KPI ref. with icon",
        icon="shopping_cart",
    ),
]


def test_kpi_card_component_library(dash_duo, request):
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = dbc.Container(
        [
            html.H1(children="KPI Cards"),
            dbc.Stack(
                children=[
                    dbc.Row([dbc.Col(kpi_card) for kpi_card in example_cards]),
                    dbc.Row([dbc.Col(kpi_card) for kpi_card in example_reference_cards]),
                ],
                gap=4,
            ),
        ]
    )
    dash_duo.start_server(app)
    dash_duo.wait_for_page(timeout=20)
    dash_duo.wait_for_element("div[class='card-kpi card']")
    result_image_path, expected_image_path = make_screenshot_and_paths(dash_duo.driver, request.node.name)
    assert_image_equal(result_image_path, expected_image_path)
    assert dash_duo.get_logs() == [], "browser console should contain no error"
