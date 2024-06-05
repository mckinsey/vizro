"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
from vizro import Vizro
from vizro.figures import kpi_card, kpi_card_reference

df = pd.DataFrame([[67434, 65553, "A"], [6434, 6553, "B"], [34, 53, "C"]], columns=["Actual", "Reference", "Category"])

page = vm.Page(
    title="KPI Indicators",
    layout=vm.Layout(grid=[[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, -1]]),
    components=[
        # Style 1: Value Only
        vm.Figure(figure=kpi_card(data_frame=df, column="Actual", title="Value I", agg_func="sum")),
        vm.Figure(figure=kpi_card(data_frame=df, column="Actual", title="Value II", agg_func="mean")),
        vm.Figure(figure=kpi_card(data_frame=df, column="Actual", title="Value III", agg_func="median")),
        # Style 2: Value and reference value
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=df,
                column="Reference",
                reference_column="Actual",
                title="Ref. Value II",
                agg_func="sum",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=df,
                column="Actual",
                reference_column="Reference",
                title="Ref. Value I",
                agg_func="sum",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=df,
                column="Actual",
                reference_column="Reference",
                title="Ref. Value III",
                agg_func="median",
                icon="shopping_cart",
            )
        ),
        # Style 3: Value and icon
        vm.Figure(
            figure=kpi_card(
                data_frame=df,
                column="Actual",
                icon="shopping_cart",
                title="Icon I",
                agg_func="sum",
                value_format="${value:.2f}",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=df,
                column="Actual",
                icon="payment",
                title="Icon II",
                agg_func="mean",
                value_format="{value:.0f}€",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=df,
                column="Actual",
                icon="monitoring",
                title="Icon III",
                agg_func="median",
            )
        ),
        # This should still work without a figure argument
        vm.Card(
            text="""
                # Text Card
                Hello, this is a text card.
            """
        ),
        vm.Card(
            text="""
                # Nav Card
                Hello, this is a nav card.
            """,
            href="https://www.google.com",
        ),
    ],
    controls=[vm.Filter(column="Category")],
)


dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
