"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
from vizro import Vizro
from vizro.figures import kpi_card, kpi_card_reference

df = pd.DataFrame([[67434, 65553, "A"], [6434, 6553, "B"], [34, 53, "C"]], columns=["Actual", "Reference", "Category"])

page = vm.Page(
    title="KPI Indicators",
    layout=vm.Layout(grid=[[0, 1, 2, 3], [4, 5, 6, 7], [-1, -1, -1, -1], [-1, -1, -1, -1]]),
    components=[
        vm.Figure(figure=kpi_card(data_frame=df, value_column="Actual", title="KPI with value")),
        vm.Figure(figure=kpi_card(data_frame=df, value_column="Actual", title="KPI with aggregation", agg_func="mean")),
        vm.Figure(
            figure=kpi_card(
                data_frame=df,
                value_column="Actual",
                title="KPI with custom formatting",
                value_format="${value:.2f}",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=df,
                value_column="Actual",
                title="KPI with icon",
                icon="shopping_cart",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=df,
                value_column="Reference",
                reference_column="Actual",
                title="KPI with reference (neg)",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=df,
                value_column="Actual",
                reference_column="Reference",
                title="KPI with reference (pos)",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=df,
                value_column="Reference",
                reference_column="Actual",
                title="KPI with reference and custom formatting",
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
                title="KPI with reference and icon",
                icon="shopping_cart",
            ),
        ),
    ],
    controls=[vm.Filter(column="Category")],
)


dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
