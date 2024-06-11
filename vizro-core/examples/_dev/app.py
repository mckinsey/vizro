"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
from vizro import Vizro
from vizro.figures import kpi_card, kpi_card_reference

df = pd.DataFrame([[67434, 65553, "A"], [6434, 6553, "B"], [34, 53, "C"]], columns=["Actual", "Reference", "Category"])

page = vm.Page(
    title="KPI Indicators",
    layout=vm.Layout(grid=[[0,1,-1]] + [[-1, -1, -1]]*4),
    components=[
        vm.Figure(
            figure=kpi_card(
                data_frame=df,
                value_column="Actual",
                icon="shopping_cart",
                title="KPI Card I",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=df,
                value_column="Actual",
                reference_column="Reference",
                title="KPI Card II",
            )
        ),
    ],
    controls=[vm.Filter(column="Category", selector=vm.RadioItems())],
)


dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
