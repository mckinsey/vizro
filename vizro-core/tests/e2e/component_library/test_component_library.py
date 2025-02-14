import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash
from e2e.asserts import assert_image_equal, make_screenshot_and_paths

from vizro.figures.library import kpi_card, kpi_card_reference

df_kpi = pd.DataFrame(
    {
        "Actual": [100, 200, 700],
        "Reference": [100, 300, 500],
        "Reference_2": [100, 300, 500],
        "Category": ["A", "B", "C"],
    }
)

example_cards = [
    kpi_card(data_frame=df_kpi, value_column="Actual", title="KPI (default)"),
    kpi_card(
        data_frame=df_kpi,
        value_column="Actual",
        title="KPI (agg, icon, format)",
        agg_func="median",
        icon="folder_check_2",
        value_format="${value:.2f}",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        title="KPI ref. (pos-default)",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Reference",
        reference_column="Actual",
        title="KPI ref. (neg-default)",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Reference",
        reference_column="Reference_2",
        title="KPI ref. (zero-default)",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        agg_func="median",
        title="KPI ref. (agg, icon, format)",
        value_format="{value}€",
        reference_format="{delta}€ vs. last year ({reference}€)",
        icon="shopping_cart",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        title="KPI ref. (color-reverse)",
        reverse_color=True,
    ),
]


def test_kpi_card_component_library(dash_duo, request):
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = dbc.Container(
        [
            dbc.Stack(
                children=[
                    dbc.Row([dbc.Col(kpi_card) for kpi_card in example_cards[:4]]),
                    dbc.Row([dbc.Col(kpi_card) for kpi_card in example_cards[4:]]),
                ],
                gap=4,
            ),
        ]
    )
    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal(
        "div[class='vstack gap-4'] div:nth-of-type(1) div:nth-of-type(2) p[class='material-symbols-outlined']",
        "folder_check_2",
    )
    dash_duo.wait_for_text_to_equal(
        "div[class='vstack gap-4'] div:nth-of-type(1) div:nth-of-type(2) div[class='card-body']", "$200.00"
    )
    dash_duo.wait_for_text_to_equal(
        "div[class='vstack gap-4'] div:nth-of-type(2) div:nth-of-type(2) p[class='material-symbols-outlined']",
        "shopping_cart",
    )
    dash_duo.wait_for_text_to_equal(
        "div[class='vstack gap-4'] div:nth-of-type(2) div:nth-of-type(3) div[class='card-body']", "1000"
    )
    result_image_path, expected_image_path = make_screenshot_and_paths(dash_duo.driver, request.node.name)
    assert_image_equal(result_image_path, expected_image_path)
    assert dash_duo.get_logs() == [], "browser console should contain no error"
