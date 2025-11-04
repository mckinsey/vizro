"""Dev app to try things out."""

import vizro.plotly.express as px
import vizro.models as vm
from vizro import Vizro
import vizro.actions as va
from vizro.figures import kpi_card, kpi_card_reference
import pandas as pd
import dash_bootstrap_components as dbc


df_kpi = pd.DataFrame({"Actual": [100, 200, 700], "Reference": [100, 300, 500], "Category": ["A", "B", "C"]})

gapminder = px.data.gapminder()

page = vm.Page(
    title="Test page",
    components=[
        vm.Card(
            text="Lorem Ipsum is simply dummy text. ",
            header="### This is card header",
            footer="##### This is card footer",
            description="Tooltip",
        ),
        vm.Card(
            header="## This is card header",
            text="Lorem Ipsum is simply dummy text of the printing and typesetting industry. "
            "Lorem Ipsum has been the industry's standard dummy text ever since the 1500s.",
            description="Tooltip",
        ),
        vm.Card(
            text="Card with text and header and footer",
            header="#### This is card header",
            footer="##### This is card footer",
            description="Tooltip",
        ),
        vm.Card(
            text="### Card with just text title",
            description="Tooltip",
        ),
        vm.Card(
            text="Card without header",
            footer="This is card footer",
            description="Tooltip",
        ),
        vm.Card(
            text="Regular card with only text: Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum is simply dummy text of the printing and typesetting industry. ",
            description="Tooltip",
        ),
        vm.Graph(figure=px.bar(gapminder, x="country", y="pop", color="continent")),
        vm.Card(
            text="Card with action: Filter Europe",
            actions=va.set_control(control="filter-id-1", value="Europe"),
        ),
        vm.Card(
            text="Navigate to page",
            href="/dummy-page",
        ),
    ],
    controls=[vm.Filter(id="filter-id-1", column="continent", selector=vm.RadioItems())],
    layout=vm.Grid(
        grid=[
            [0, 1, 2, 3],
            [4, 5, 7, 8],
            [6, 6, -1, -1],
            [6, 6, -1, -1],
        ]
    ),
)

page_2 = vm.Page(title="Dummy page", components=[vm.Card(text="This is plain old card.")])

page_3 = vm.Page(
    title="KPI indicator cards",
    components=[
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=df_kpi,
                value_column="Actual",
                reference_column="Reference",
                title="KPI reference (pos)",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=df_kpi,
                value_column="Actual",
                reference_column="Reference",
                title="KPI reference with icon",
                icon="Shopping Cart",
            )
        ),
        vm.Figure(
            figure=kpi_card_reference(
                data_frame=df_kpi,
                value_column="Actual",
                reference_column="Reference",
                title="KPI reference (reverse color)",
                reverse_color=True,
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=df_kpi,
                value_column="Actual",
                title="KPI with icon",
                icon="Shopping Cart",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=df_kpi,
                value_column="Actual",
                title="KPI with formatting",
                value_format="${value:.2f}",
            )
        ),
        vm.Figure(
            figure=kpi_card(data_frame=df_kpi, value_column="Actual", title="KPI with value"),
        ),
    ],
    layout=vm.Grid(grid=[[0, 1, 2], [3, 4, 5]]),
)

dashboard = vm.Dashboard(pages=[page, page_2, page_3])

if __name__ == "__main__":
    Vizro(external_stylesheets=[dbc.themes.BOOTSTRAP]).build(dashboard).run()
