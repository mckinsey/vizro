import dash_bootstrap_components as dbc
import pandas as pd
import pytest
from asserts import assert_component_equal
from dash import html
from vizro.figures import kpi_card, kpi_card_reference

df = pd.DataFrame([[67434, 65553, "A"], [6434, 6553, "B"], [34, 53, "C"]], columns=["Actual", "Reference", "Category"])


class TestKPICardBuild:
    def test_kpi_card_mandatory(self):
        result = kpi_card(data_frame=df, value_column="Actual")()
        assert_component_equal(
            result,
            dbc.Card(
                [dbc.CardHeader([None, html.H2("Sum Actual")]), dbc.CardBody("73902")],
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
                    dbc.CardBody("$24634.00"),
                ],
                className="card-kpi",
            ),
        )

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
                dbc.CardBody("73902"),
                dbc.CardFooter(
                    [
                        html.Span("arrow_circle_up", className="material-symbols-outlined"),
                        html.Span("2.4% vs. reference (72159)"),
                    ],
                    className="color-pos",
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
            reference_format="+{delta:.1f} vs. {reference:.1f}",
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
                dbc.CardBody("$24634.00"),
                dbc.CardFooter(
                    [
                        html.Span("arrow_circle_up", className="material-symbols-outlined"),
                        html.Span("+581.0 vs. 24053.0"),
                    ],
                    className="color-pos",
                ),
            ],
            className="card-kpi",
        )

        assert_component_equal(result, expected)

    def test_value_format_missing_placeholder(self):
        with pytest.raises(
            IndexError,
            match="Replacement index 0 out of range for positional args tuple",
        ):
            kpi_card(data_frame=df, value_column="Actual", value_format="{.2f}}")()
