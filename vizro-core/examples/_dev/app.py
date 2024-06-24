"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
from vizro import Vizro
from vizro.figures import kpi_card, kpi_card_reference

df_kpi = pd.DataFrame(
    {"Actual": [100, 200, 700], "Reference": [100, 300, 500], "Reference Zero": [0, 0, 0], "Category": ["A", "B", "C"]}
)

example_cards = [
    kpi_card(data_frame=df_kpi, value_column="Actual", title="KPI with value"),
    kpi_card(data_frame=df_kpi, value_column="Actual", title="KPI with aggregation", agg_func="median"),
    kpi_card(
        data_frame=df_kpi,
        value_column="Actual",
        title="KPI with formatting",
        value_format="${value:.2f}",
    ),
    kpi_card(
        data_frame=df_kpi,
        value_column="Actual",
        title="KPI with icon",
        icon="shopping_cart",
    ),
]

example_reference_cards = [
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        title="Delta Positive",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference",
        agg_func="median",
        title="Delta Negative",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Actual",
        title="Delta Zero",
        value_format="{value:.2f}$",
        reference_format="{delta:.2f}$ vs. last year ({reference:.2f}$)",
    ),
    kpi_card_reference(
        data_frame=df_kpi,
        value_column="Actual",
        reference_column="Reference Zero",
        title="Reference Zero",
        icon="shopping_cart",
    ),
]

page = vm.Page(
    title="KPI Indicators",
    layout=vm.Layout(grid=[[0, 1, 2, 3], [4, 5, 6, 7], [-1, -1, -1, -1], [-1, -1, -1, -1]]),
    components=[vm.Figure(figure=figure) for figure in example_cards + example_reference_cards],
    controls=[vm.Filter(column="Category")],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
