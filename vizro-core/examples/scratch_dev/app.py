"""Dev app to try things out."""

import json
import vizro.models as vm
from typing import Literal
from dash import dcc, Input, Output, callback, Patch
from dash_ag_grid import AgGrid

from vizro import Vizro
from vizro.tables import dash_ag_grid
from vizro.models.types import capture
from vizro.figures import kpi_card, kpi_card_reference
import vizro.plotly.express as px

from data import (
    scenario_data,
    wip_waterfall,
    wip_by_equipment,
    kpi_summary_production,
    kpi_summary_lead,
    kpi_summary_average,
    daily_data,
    kpis_per_product_type,
)


@capture("ag_grid")
def scenarios_ag_grid(data_frame=None, **kwargs):
    """Custom AgGrid with a 'Scenario action' column containing a button per row."""
    column_defs = []
    for col in data_frame.columns:
        if col == "Scenario action":
            column_defs.append(
                {
                    "field": col,
                    "cellRenderer": "Button",
                    "cellRendererParams": {"className": "btn btn-scenario"},
                }
            )
        else:
            column_defs.append({"field": col})

    dashGridOptions = {
        "animateRows": False,
        "domLayout": "autoHeight",
        "pagination": True,
        "paginationPageSize": 20,
        "theme": {"function": "vizroTheme(themeQuartz, agGrid)"},
    }
    return AgGrid(
        columnDefs=column_defs, rowData=data_frame.to_dict("records"), dashGridOptions=dashGridOptions, **kwargs
    )


class CustomInput(vm.VizroBaseModel):
    type: Literal["custom_input"] = "custom_input"

    def build(self):
        return dcc.Input(
            placeholder="🔍   Search",
            style={"maxWidth": "300px", "position": "relative", "top": "24px", "border": "1px solid gray"},
        )


@capture("graph")
def plot_total_production_volume(data_frame):
    fig = px.line(
        data_frame,
        x="date_label",
        y="total_production_volume_ton",
        markers=True,
        labels={"date_label": "", "total_production_volume_ton": "ton"},
        title="Total production volume",
    )
    return fig


vm.Container.add_type("controls", CustomInput)
vm.Container.add_type("components", CustomInput)


page_1 = vm.Page(
    title="SCENARIO ANALYSIS TOOL",
    components=[
        # vm.Card(text="**Scenario Analysis** — Compare and analyze different business scenarios below."),
        vm.Container(
            title="List of Scenarios",
            components=[vm.AgGrid(figure=scenarios_ag_grid(data_frame=scenario_data, id="custom_ag_grid"))],
            controls=[
                vm.Filter(
                    column="baseline",
                    selector=vm.Checklist(
                        options=[{"label": "True", "value": True}, {"label": "False", "value": False}]
                    ),
                ),
                CustomInput(id="quick-filter-search"),
            ],
        )
    ],
)

page_2 = vm.Page(
    title="Scenario details",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="KPIs",
                    components=[
                        vm.Figure(
                            figure=kpi_card_reference(
                                data_frame=kpi_summary_production,
                                value_column="value",
                                reference_column="baseline_value",
                                title="The total production volume",
                            )
                        ),
                        vm.Figure(
                            figure=kpi_card_reference(
                                data_frame=kpi_summary_average,
                                value_column="value",
                                reference_column="baseline_value",
                                title="Daily average WIP",
                            )
                        ),
                        vm.Figure(
                            figure=kpi_card_reference(
                                data_frame=kpi_summary_lead,
                                value_column="value",
                                reference_column="baseline_value",
                                title="Average lead time",
                            )
                        ),
                        vm.Tabs(
                            tabs=[
                                vm.Container(
                                    title="Total production volume",
                                    components=[vm.Graph(figure=plot_total_production_volume(daily_data))],
                                ),
                                vm.Container(title="WIP by equipment", components=[vm.Card(text="placeholder")]),
                                vm.Container(title="WIP waterfall", components=[vm.Card(text="placeholder")]),
                            ]
                        ),
                        vm.Container(
                            title="KPI per product type",
                            components=[
                                CustomInput(id="quick-filter-search-2"),
                                vm.AgGrid(figure=dash_ag_grid(kpis_per_product_type)),
                            ],
                            layout=vm.Flex(),
                        ),
                    ],
                    layout=vm.Grid(
                        grid=[
                            [0, 3, 3, 3],
                            [1, 3, 3, 3],
                            [2, 3, 3, 3],
                            [4, 4, 4, 4],
                            [4, 4, 4, 4],
                        ],
                        row_min_height="150px",
                    ),
                )
            ]
        )
    ],
)


dashboard = vm.Dashboard(
    pages=[page_1, page_2],
    title="QB",
)


@callback(Output("custom_ag_grid", "dashGridOptions"), Input("quick-filter-search", "value"), prevent_initial_call=True)
def update_filter(filter_value):
    newFilter = Patch()
    newFilter["quickFilterText"] = filter_value
    return newFilter


if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
