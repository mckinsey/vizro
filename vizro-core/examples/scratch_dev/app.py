"""Example app to show all features of Vizro."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.figures import kpi_card

gapminder = px.data.gapminder()

# data from the demo app
df_kpi = pd.DataFrame(
    {
        "Actual": [100, 200, 700],
        "Reference": [100, 300, 500],
        "Category": ["A", "B", "C"],
    }
)


home = vm.Page(
    title="Page Title",
    components=[
        # kpi_card(data_frame=df_kpi, value_column="Actual", title="KPI with value"),
        vm.Figure(figure=kpi_card(data_frame=df_kpi, value_column="Actual", title="KPI with value")),
    ],
)


dashboard = vm.Dashboard(pages=[home])


if __name__ == "__main__":
    Vizro().build(dashboard).run()
