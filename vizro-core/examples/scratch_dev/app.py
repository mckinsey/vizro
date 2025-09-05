"""This is a test app to test the dashboard layout."""

import vizro.models as vm
from vizro import Vizro
from vizro.figures import kpi_card
import pandas as pd
from data import market_industry_data, map_chart_data, market_category_data, market_summary_data, aggrid_data
from charts import (
    custom_market_industry_bar_chart,
    custom_map_chart,
    custom_market_category_bar_chart,
    custom_market_summary_bar_chart,
    custom_waterfall_chart
)

from dash import callback, Input, Output
from vizro.actions import filter_interaction
from vizro.tables import dash_ag_grid

df_kpi = pd.DataFrame({"Actual": [100, 200, 700], "Reference": [100, 300, 500], "Category": ["A", "B", "C"]})

vm.Page.add_type("components", vm.Slider)
vm.Container.add_type("components", vm.Slider)

cellStyle = {
    "styleConditions": [
        {
            "condition": "params.value == 'High'",
            "style": {"backgroundColor": "#143771"},
        },
        {
            "condition": "params.value == 'Medium'",
            "style": {"backgroundColor": "#408CCB"},
        },
        {
            "condition": "params.value == 'Low'",
            "style": {"backgroundColor": "#BBE5F7"},
        },
    ]
}

columnDefs = [
    {"field": "Business Name"},
    {"field": "Tier", "cellRenderer": "ColorCellRenderer"},
    {"field": "Current Sales"},
    {"field": "Potential Opportunity"},
    {"field": "Likelihood Score", "cellStyle": cellStyle},
    {"field": "Industry Priority"},
    {"field": "Growth Opportunity"},
    {"field": "Price Opportunity"},
    {"field": "Churn Risk"},
    {"field": "Industry"},
]


page = vm.Page(
    title="Vizro dashboard",
    components=[
        vm.Slider(
            id="slider-component-1",
            marks={0: "Market Map", 1: "Leads", 2: "Summary"},
            step=1,
            min=0,
            max=2,
            extra={"included": True},
        ),
        vm.Tabs(
            id="page-tab",
            tabs=[
                vm.Container(
                    title="Market Map",
                    components=[
                        vm.Figure(
                            figure=kpi_card(
                                data_frame=df_kpi,
                                value_column="Actual",
                                title="Number of Leads",
                                icon="Groups",
                            ),
                        ),
                        vm.Figure(
                            figure=kpi_card(
                                data_frame=df_kpi,
                                value_column="Actual",
                                title="Serviceable Available Market",
                                icon="Finance mode",
                            ),
                        ),
                        vm.Container(
                            components=[
                                vm.Graph(
                                    id="market-industry-bar-chart",
                                    figure=custom_market_industry_bar_chart(
                                        market_industry_data, custom_data=["Industry"]
                                    ),
                                    actions=[
                                        vm.Action(function=filter_interaction(targets=["market-category-bar-chart"]))
                                    ],
                                    title="Serviceable Addressable Market by Industry Vertical",
                                )
                            ],
                            variant="filled",
                        ),
                        vm.Container(
                            components=[
                                vm.Graph(
                                    figure=custom_map_chart(map_chart_data),
                                )
                            ],
                            variant="filled",
                        ),
                        vm.Container(
                            components=[
                                vm.Graph(
                                    id="market-category-bar-chart",
                                    figure=custom_market_category_bar_chart(
                                        market_category_data, custom_data=["Industry"]
                                    ),
                                    actions=[
                                        vm.Action(function=filter_interaction(targets=["market-industry-bar-chart"]))
                                    ],
                                )
                            ],
                            variant="filled",
                        ),
                    ],
                    layout=vm.Grid(
                        grid=[
                            [0, 0, 1, 1],
                            [2, 2, 3, 3],
                            [2, 2, 3, 3],
                            [2, 2, 4, 4],
                            [2, 2, 4, 4],
                            [2, 2, 4, 4],
                        ],
                    ),
                ),
                vm.Container(
                    title="Leads",
                    components=[
                        vm.Figure(
                            figure=kpi_card(
                                data_frame=df_kpi,
                                value_column="Actual",
                                title="Number of Leads",
                                icon="Groups",
                            ),
                        ),
                        vm.Figure(
                            figure=kpi_card(
                                data_frame=df_kpi,
                                value_column="Actual",
                                title="Serviceable Available Market",
                                icon="Finance mode",
                            ),
                        ),
                        vm.Container(
                            variant="filled",
                            components=[
                                vm.AgGrid(
                                    id="tab_2_aggrid",
                                    figure=dash_ag_grid(
                                        data_frame=aggrid_data,
                                        columnSize="autoSize",
                                        columnDefs=columnDefs,
                                    ),
                                    actions=[vm.Action(function=filter_interaction(targets=["tab_2_market_category"]))],
                                ),
                            ],
                        ),
                        vm.Container(
                            variant="filled",
                            components=[
                                vm.Graph(
                                    figure=custom_map_chart(map_chart_data),
                                ),
                            ],
                        ),
                        vm.Container(
                            variant="filled",
                            components=[
                                vm.Graph(
                                    id="tab_2_market_category",
                                    figure=custom_market_category_bar_chart(
                                        market_category_data, custom_data=["Industry"]
                                    ),
                                    actions=[vm.Action(function=filter_interaction(targets=["tab_2_aggrid"]))],
                                ),
                            ],
                        ),
                    ],
                    controls=[vm.Filter(column="Industry", selector=vm.Checklist())],
                    layout=vm.Grid(
                        grid=[
                            [0, 0, 1, 1],
                            [2, 2, 3, 3],
                            [2, 2, 3, 3],
                            [2, 2, 4, 4],
                            [2, 2, 4, 4],
                            [2, 2, 4, 4],
                        ],
                    ),
                ),
                vm.Container(
                    title="Summary",
                    components=[
                        vm.Figure(
                            figure=kpi_card(
                                data_frame=df_kpi,
                                value_column="Actual",
                                title="Number of Leads",
                                icon="Groups",
                            ),
                        ),
                        vm.Figure(
                            figure=kpi_card(
                                data_frame=df_kpi,
                                value_column="Actual",
                                title="Serviceable Available Market",
                                icon="Finance mode",
                            ),
                        ),
                        vm.Container(
                            title="",
                            components=[vm.Graph(figure=custom_waterfall_chart(market_summary_data))],
                        ),
                        vm.Container(
                            title="",
                            components=[
                                vm.Graph(figure=custom_market_summary_bar_chart(market_summary_data)),
                            ],
                        ),
                    ],
                    layout=vm.Grid(
                        grid=[
                            [0, 0, 1, 1],
                            [2, 2, 3, 3],
                            [2, 2, 3, 3],
                            [2, 2, 3, 3],
                            [2, 2, 3, 3],
                        ],
                    ),
                ),
            ],
        ),
    ],
    layout=vm.Grid(
        grid=[
            [0],
            [1],
            [1],
            [1],
            [1],
            [1],
            [1],
            [1],
            [1],
        ],
    ),
)


dashboard = vm.Dashboard(pages=[page], title="CustomerOne")


@callback(
    Output("page-tab", "active_tab", allow_duplicate=True),
    Input("slider-component-1", "value"),
    prevent_initial_call=True,
)
def change_location(value):
    if value:
        return f"tab-{value}"
    else:
        return "tab-0"


if __name__ == "__main__":
    Vizro().build(dashboard).run()
