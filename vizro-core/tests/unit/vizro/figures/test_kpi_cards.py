import dash_bootstrap_components as dbc
import pandas as pd
import pytest
from asserts import assert_component_equal
from dash import html
from vizro.figures import kpi_card, kpi_card_reference

df = pd.DataFrame({"Actual": [1, 2, 3], "Reference": [2, 4, 6]})


class TestKPICard:
    def test_kpi_card_mandatory(self):
        result = kpi_card(data_frame=df, value_column="Actual")()
        assert_component_equal(
            result,
            dbc.Card(
                [dbc.CardHeader([None, html.H2("Sum Actual")]), dbc.CardBody("6")],
                className="card-kpi",
            ),
        )

    def test_kpi_card_mandatory_and_optional(self):
        result = kpi_card(
            data_frame=df,
            value_column="Actual",
            icon="shopping_cart",
            title="sales",
            value_format="${value:0.2f}",
            agg_func="mean",
        )()
        assert_component_equal(
            result,
            dbc.Card(
                [
                    dbc.CardHeader([html.P("shopping_cart", className="material-symbols-outlined"), html.H2("sales")]),
                    dbc.CardBody("$2.00"),
                ],
                className="card-kpi",
            ),
        )

    def test_value_format_missing_placeholder(self):
        with pytest.raises(
            IndexError,
            match="Replacement index 0 out of range for positional args tuple",
        ):
            kpi_card(data_frame=df, value_column="Actual", value_format="{.2f}}")()


class TestKPICardReference:
    def test_kpi_card_reference_mandatory(self):
        result = kpi_card_reference(data_frame=df, value_column="Actual", reference_column="Reference")()
        expected = dbc.Card(
            [
                dbc.CardHeader(
                    [
                        None,
                        html.H2("Sum Actual"),
                    ]
                ),
                dbc.CardBody("6"),
                dbc.CardFooter(
                    [
                        html.Span("arrow_circle_down", className="material-symbols-outlined"),
                        html.Span("-50.0% vs. reference (12)"),
                    ],
                    className="color-neg",
                ),
            ],
            className="card-kpi",
        )

        assert_component_equal(result, expected)

    def test_kpi_card_reference_mandatory_and_optional(self):
        result = kpi_card_reference(
            data_frame=df,
            value_column="Actual",
            reference_column="Reference",
            icon="shopping_cart",
            title="sales",
            value_format="${value:0.2f}",
            reference_format="{delta:.1f} vs. {reference:.1f}",
            agg_func="mean",
        )()
        expected = dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.P("shopping_cart", className="material-symbols-outlined"),
                        html.H2("sales"),
                    ]
                ),
                dbc.CardBody("$2.00"),
                dbc.CardFooter(
                    [
                        html.Span("arrow_circle_down", className="material-symbols-outlined"),
                        html.Span("-2.0 vs. 4.0"),
                    ],
                    className="color-neg",
                ),
            ],
            className="card-kpi",
        )

        assert_component_equal(result, expected)
