import dash_bootstrap_components as dbc
import pandas as pd
import pytest
from asserts import assert_component_equal
from dash import html

from vizro.figures import kpi_card, kpi_card_reference

df = pd.DataFrame({"Actual": [1, 2, 3], "Reference": [2, 4, 6], "Reference Zero": [0, 0, 0]})


class TestKPICard:
    def test_kpi_card_mandatory(self):
        result = kpi_card(data_frame=df, value_column="Actual")()
        assert_component_equal(
            result,
            dbc.Card(
                [dbc.CardHeader([None, html.H4("Sum Actual", className="card-kpi-title")]), dbc.CardBody("6")],
                class_name="card-kpi",
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
                    dbc.CardHeader(
                        [
                            html.P("shopping_cart", className="material-symbols-outlined"),
                            html.H4("sales", className="card-kpi-title"),
                        ]
                    ),
                    dbc.CardBody("$2.00"),
                ],
                class_name="card-kpi",
            ),
        )

    def test_value_format_missing_placeholder(self):
        with pytest.raises(
            IndexError,
            match="Replacement index 0 out of range for positional args tuple",
        ):
            kpi_card(data_frame=df, value_column="Actual", value_format="{.2f}}")()

    def test_value_format_nonexisting_placeholder(self):
        with pytest.raises(KeyError, match="reference"):
            kpi_card(data_frame=df, value_column="Actual", value_format="{reference.2f}}")()


class TestKPICardReference:
    def test_kpi_card_reference_mandatory_delta_negative(self):
        result = kpi_card_reference(data_frame=df, value_column="Actual", reference_column="Reference")()
        expected = dbc.Card(
            [
                dbc.CardHeader([None, html.H4("Sum Actual", className="card-kpi-title")]),
                dbc.CardBody("6"),
                dbc.CardFooter(
                    [
                        html.Span("arrow_circle_down", className="material-symbols-outlined"),
                        html.Span("-50.0% vs. reference (12)"),
                    ],
                    class_name="color-neg",
                ),
            ],
            class_name="card-kpi",
        )
        assert_component_equal(result, expected)

    def test_kpi_card_reference_mandatory_delta_positive(self):
        result = kpi_card_reference(data_frame=df, value_column="Reference", reference_column="Actual")()
        expected = dbc.Card(
            [
                dbc.CardHeader([None, html.H4("Sum Reference", className="card-kpi-title")]),
                dbc.CardBody("12"),
                dbc.CardFooter(
                    [
                        html.Span("arrow_circle_up", className="material-symbols-outlined"),
                        html.Span("+100.0% vs. reference (6)"),
                    ],
                    class_name="color-pos",
                ),
            ],
            class_name="card-kpi",
        )
        assert_component_equal(result, expected)

    def test_kpi_card_reference_mandatory_delta_zero(self):
        result = kpi_card_reference(data_frame=df, value_column="Actual", reference_column="Actual")()
        expected = dbc.Card(
            [
                dbc.CardHeader([None, html.H4("Sum Actual", className="card-kpi-title")]),
                dbc.CardBody("6"),
                dbc.CardFooter(
                    [
                        html.Span("arrow_circle_right", className="material-symbols-outlined"),
                        html.Span("+0.0% vs. reference (6)"),
                    ],
                    class_name="",
                ),
            ],
            class_name="card-kpi",
        )
        assert_component_equal(result, expected)

    def test_kpi_card_reference_mandatory_reference_zero(self):
        result = kpi_card_reference(data_frame=df, value_column="Actual", reference_column="Reference Zero")()
        expected = dbc.Card(
            [
                dbc.CardHeader([None, html.H4("Sum Actual", className="card-kpi-title")]),
                dbc.CardBody("6"),
                dbc.CardFooter(
                    [
                        html.Span("arrow_circle_up", className="material-symbols-outlined"),
                        html.Span("+nan% vs. reference (0)"),
                    ],
                    class_name="color-pos",
                ),
            ],
            class_name="card-kpi",
        )
        assert_component_equal(result, expected)

    def test_kpi_card_reference_mandatory_and_optional(self):
        result = kpi_card_reference(
            data_frame=df,
            value_column="Actual",
            reference_column="Reference",
            icon="shopping_cart",
            title="sales",
            # A and B distinguish the two strings to make sure the kpi_card_reference function isn't mixing them up
            value_format="A {value} is +{delta:.1f} ({delta_relative}:%) vs. {reference:.1f}",
            reference_format="B {value} is +{delta:.1f} ({delta_relative}:%) vs. {reference:.1f}",
            agg_func="mean",
            reverse_color=True,
        )()
        expected = dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.P("shopping_cart", className="material-symbols-outlined"),
                        html.H4("sales", className="card-kpi-title"),
                    ]
                ),
                dbc.CardBody("A 2.0 is +-2.0 (-0.5:%) vs. 4.0"),
                dbc.CardFooter(
                    [
                        html.Span("arrow_circle_down", className="material-symbols-outlined"),
                        html.Span("B 2.0 is +-2.0 (-0.5:%) vs. 4.0"),
                    ],
                    class_name="color-pos",
                ),
            ],
            class_name="card-kpi",
        )

        assert_component_equal(result, expected)

    def test_reference_format_missing_placeholder(self):
        with pytest.raises(
            IndexError,
            match="Replacement index 0 out of range for positional args tuple",
        ):
            kpi_card_reference(
                data_frame=df, value_column="Actual", reference_column="Reference", reference_format="{.2f}}"
            )()

    def test_reference_format_non_existing_placeholder(self):
        with pytest.raises(KeyError, match="delta_absolute"):
            kpi_card_reference(
                data_frame=df,
                value_column="Actual",
                reference_column="Reference",
                reference_format="{delta_absolute.2f}}",
            )()
