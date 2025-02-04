"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
from vizro import Vizro
from vizro.figures import kpi_card_reference

df_kpi = pd.DataFrame({"Actual": [100, 200, 700], "Reference": [100, 300, 500], "Category": ["A", "B", "C"]})

page = vm.Page(
    title="KPI card I",
    components=[
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=df_kpi,
                value_column="Actual",
                reference_column="Reference",
                title="KPI reference with icon",
                icon="folder_check_2",
            )
        )
    ],
)

page_two = vm.Page(
    title="KPI card II",
    components=[
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=df_kpi,
                value_column="Actual",
                reference_column="Reference",
                title="KPI reference with icon",
                icon="folder_check",
            )
        )
    ],
)

dashboard = vm.Dashboard(pages=[page, page_two], navigation=vm.Navigation(nav_selector=vm.NavBar()))

if __name__ == "__main__":
    Vizro().build(dashboard).run()
