"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
from vizro import Vizro
from vizro.figures import kpi_card, kpi_card_reference

df = pd.DataFrame([[67434, 65553, "A"], [6434, 6553, "B"], [34, 53, "C"]], columns=["Actual", "Reference", "Category"])

page = vm.Page(
    title="KPI Indicators",
    layout=vm.Layout(grid=[[0, 1, 2, 3], [4, 5, 6, 7], [-1, -1, -1, -1]]),
    components=[
        # Style 1: `kpi_card`
        vm.Figure(figure=kpi_card(data_frame=df, value_column="Actual", title="KPI Card I")),
        vm.Figure(figure=kpi_card(data_frame=df, value_column="Actual", title="KPI Card II", agg_func="mean")),
        vm.Figure(figure=kpi_card(data_frame=df, value_column="Actual", title="KPI Card III", agg_func="mean",
                                  value_format="${value:.2f}", )),
        vm.Figure(figure=kpi_card(data_frame=df, value_column="Actual", title="KPI Card IV", agg_func="mean", value_format="${value:.2f}", icon="shopping_cart")),
        # Style 2: Value and reference value
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=df,
                value_column="Reference",
                reference_column="Actual",
                title="KPI Ref. Card I",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=df,
                value_column="Actual",
                reference_column="Reference",
                title="KPI Ref. Card I",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=df,
                value_column="Reference",
                reference_column="Actual",
                title="KPI Ref. Card I",
                value_format="{value:.2f}$",
                reference_format="{delta:.2f}$ vs. last year ({reference:.2f}$)",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=df,
                value_column="Actual",
                reference_column="Reference",
                value_format="${value:.2f}",
                reference_format="${delta:.2f} vs. reference (${reference:.2f})",
                icon="shopping_cart",
            ),
        ),
    ],
    controls=[vm.Filter(column="Category")],
)


dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
