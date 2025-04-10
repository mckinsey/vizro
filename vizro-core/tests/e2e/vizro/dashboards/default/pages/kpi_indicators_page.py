import e2e.vizro.constants as cnst
import pandas as pd

import vizro.models as vm
from vizro.figures import kpi_card, kpi_card_reference

kpi_df = pd.DataFrame(
    [[67434, 65553, "A"], [6434, 6553, "B"], [34, 53, "C"]],
    columns=["Actual", "Reference", "Category"],
)

kpi_indicators_page = vm.Page(
    title=cnst.KPI_INDICATORS_PAGE,
    layout=vm.Grid(grid=[[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, -1]]),
    components=[
        # Style 1: Value Only
        vm.Figure(
            figure=kpi_card(
                data_frame=kpi_df,
                value_column="Actual",
                title="Value I",
                agg_func="sum",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=kpi_df,
                value_column="Actual",
                title="Value II",
                agg_func="mean",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=kpi_df,
                value_column="Actual",
                title="Value III",
                agg_func="median",
            )
        ),
        # Style 2: Value and reference value
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=kpi_df,
                value_column="Reference",
                reference_column="Actual",
                title="Ref. Value II",
                agg_func="sum",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=kpi_df,
                value_column="Actual",
                reference_column="Reference",
                title="Ref. Value I",
                agg_func="sum",
            )
        ),
        vm.Figure(
            id="kpi-card-reverse-coloring",
            figure=kpi_card_reference(
                data_frame=kpi_df,
                value_column="Actual",
                reference_column="Reference",
                title="Ref. Value III",
                agg_func="median",
                icon="shopping_cart",
            ),
        ),
        # Style 3: Value and icon
        vm.Figure(
            figure=kpi_card(
                data_frame=kpi_df,
                value_column="Actual",
                icon="shopping_cart",
                title="Icon I",
                agg_func="sum",
                value_format="${value:.2f}",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=kpi_df,
                value_column="Actual",
                icon="payment",
                title="Icon II",
                agg_func="mean",
                value_format="{value:.0f}€",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=kpi_df,
                value_column="Actual",
                icon="monitoring",
                title="Icon III",
                agg_func="median",
            )
        ),
        # Style 4: Reference value and reverse coloring
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=kpi_df,
                value_column="Actual",
                reference_column="Reference",
                title="Ref. Value (pos-reverse)",
                reverse_color=True,
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=kpi_df,
                value_column="Reference",
                reference_column="Actual",
                title="Ref. Value (neg-reverse)",
                reverse_color=True,
            ),
        ),
    ],
    controls=[vm.Filter(column="Category", selector=vm.Dropdown(id=cnst.DROPDOWN_FILTER_KPI_PAGE))],
)
