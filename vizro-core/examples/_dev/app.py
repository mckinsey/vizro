"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.figures import kpi_card
from vizro.models.types import capture

df_kpi = pd.DataFrame(
    {"Actual": [100, 200, 700], "Reference": [100, 300, 500], "Reference Zero": [0, 0, 0], "Category": ["A", "B", "C"]}
)


@capture("graph")
def f(data_frame):
    return px.bar(data_frame, "Actual").update_layout(title="x")


page = vm.Page(
    title="KPI Indicators",
    components=[
        vm.Graph(
            figure=f(df_kpi),
        ),
        vm.Figure(figure=kpi_card(data_frame=df_kpi, value_column="Actual", title="KPI with value")),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
