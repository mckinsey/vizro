"""Dev app to try things out."""

import vizro.models as vm
from vizro.actions import set_control

from vizro import Vizro
from vizro.tables import dash_ag_grid

from vizro.managers import data_manager

from data import (
    scenario_data,
    daily_data_baseline,
    daily_data_scenario_a,
    daily_data_scenario_b,
    daily_data_scenario_c,
    daily_data_scenario_d,
    kpis_per_product_type,
    daily_baseline,
    daily_scenario_a,
    daily_scenario_b,
    daily_scenario_c,
    daily_scenario_d,
    kpi_comparison_baseline,
    kpi_comparison_scenario_a,
    kpi_comparison_scenario_b,
    kpi_comparison_scenario_c,
    kpi_comparison_scenario_d,
)

from custom_charts import (
    scenarios_ag_grid,
    plot_total_production_volume,
    plot_comparison_total_production_volume,
    custom_kpi_card_reference,
)


def load_data(scenario_name="Baseline"):
    scenario_df = {
        "Increased high-end product": daily_scenario_a,
        "Reduced pricing tier": daily_scenario_b,
        "Bundle promotion strategy": daily_scenario_c,
        "Aggressive discounting": daily_scenario_d,
    }

    return scenario_df.get(scenario_name, daily_baseline)


def load_kpi_data(scenario_name="Baseline"):
    scenario_df_kpi = {
        "Increased high-end product": kpi_comparison_scenario_a,
        "Reduced pricing tier": kpi_comparison_scenario_b,
        "Bundle promotion strategy": kpi_comparison_scenario_c,
        "Aggressive discounting": kpi_comparison_scenario_d,
    }

    return scenario_df_kpi.get(scenario_name, kpi_comparison_baseline)


def load_data_daily(scenario_name="Baseline"):
    scenario_df = {
        "Increased high-end product": daily_data_scenario_a,
        "Reduced pricing tier": daily_data_scenario_b,
        "Bundle promotion strategy": daily_data_scenario_c,
        "Aggressive discounting": daily_data_scenario_d,
    }

    return scenario_df.get(scenario_name, daily_data_baseline)


data_manager["scenario_compare"] = load_data
data_manager["scenario_compare_kpi"] = load_kpi_data
data_manager["scenario_daily_data"] = load_data_daily


page_1 = vm.Page(
    title="SCENARIO ANALYSIS TOOL",
    components=[
        vm.Container(
            title="List of Scenarios",
            components=[
                vm.AgGrid(
                    figure=scenarios_ag_grid(data_frame=scenario_data, id="custom_ag_grid"),
                    actions=[
                        set_control(control="comparison-param", value="scenario_name"),
                        set_control(control="comparison-param-1", value="scenario_name"),
                    ],
                ),
            ],
        ),
        vm.Container(
            title="Comparison View",
            components=[
                vm.Figure(
                    id="kpi_card_1",
                    figure=custom_kpi_card_reference(
                        data_frame="scenario_compare_kpi",
                        data_frame_reference=kpi_comparison_baseline,
                        title="The total production volume",
                        value_column="production_volume",
                        reference_column="production_volume",
                    ),
                ),
                vm.Figure(
                    id="kpi_card_2",
                    figure=custom_kpi_card_reference(
                        data_frame="scenario_compare_kpi",
                        data_frame_reference=kpi_comparison_baseline,
                        title="The daily average WIP for all equipment",
                        value_column="average_wip",
                        reference_column="average_wip",
                    ),
                ),
                vm.Figure(
                    id="kpi_card_3",
                    figure=custom_kpi_card_reference(
                        data_frame="scenario_compare_kpi",
                        data_frame_reference=kpi_comparison_baseline,
                        title="The average lead time for all product types",
                        value_column="average_lead",
                        reference_column="average_lead",
                    ),
                ),
                vm.Tabs(
                    tabs=[
                        vm.Container(
                            title="Total production volume",
                            components=[
                                vm.Graph(
                                    id="comparison-graph-1",
                                    figure=plot_comparison_total_production_volume(
                                        data_frame="scenario_compare",
                                        data_frame_scenario_2=daily_baseline,
                                        scenario_1_label="Baseline",
                                        scenario_2_label="Scenario a",
                                        value_column="ton",
                                        date_label_column="date_label",
                                    ),
                                ),
                            ],
                        )
                    ]
                ),
            ],
            layout=vm.Grid(
                grid=[
                    [0, 3, 3, 3],
                    [1, 3, 3, 3],
                    [2, 3, 3, 3],
                ]
            ),
        ),
    ],
    layout=vm.Flex(),
    controls=[
        vm.Parameter(
            id="comparison-param",
            targets=["comparison-graph-1.data_frame.scenario_name"],
            selector=vm.Dropdown(
                options=["Increased high-end product", "Baseline", "Reduced pricing tier", "Bundle promotion strategy"],
                value="Baseline",
                multi=False,
            ),
            visible=False,
        ),
        vm.Parameter(
            id="comparison-param-1",
            targets=[
                "kpi_card_1.data_frame.scenario_name",
                "kpi_card_2.data_frame.scenario_name",
                "kpi_card_3.data_frame.scenario_name",
            ],
            selector=vm.Dropdown(
                options=["Increased high-end product", "Baseline", "Reduced pricing tier", "Bundle promotion strategy"],
                value="Baseline",
                multi=False,
            ),
            visible=False,
        ),
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
                            id="kpi_card_4",
                            figure=custom_kpi_card_reference(
                                data_frame="scenario_compare_kpi",
                                data_frame_reference=kpi_comparison_baseline,
                                title="The total production volume",
                                value_column="production_volume",
                                reference_column="production_volume",
                            ),
                        ),
                        vm.Figure(
                            id="kpi_card_5",
                            figure=custom_kpi_card_reference(
                                data_frame="scenario_compare_kpi",
                                data_frame_reference=kpi_comparison_baseline,
                                title="The daily average WIP for all equipment",
                                value_column="average_wip",
                                reference_column="average_wip",
                            ),
                        ),
                        vm.Figure(
                            id="kpi_card_6",
                            figure=custom_kpi_card_reference(
                                data_frame="scenario_compare_kpi",
                                data_frame_reference=kpi_comparison_baseline,
                                title="The average lead time for all product types",
                                value_column="average_lead",
                                reference_column="average_lead",
                            ),
                        ),
                        vm.Tabs(
                            tabs=[
                                vm.Container(
                                    title="Total production volume",
                                    components=[
                                        vm.Graph(
                                            id="graph-2",
                                            figure=plot_total_production_volume(
                                                data_frame="scenario_daily_data",
                                                metric="total_production_volume_ton",
                                            ),
                                        )
                                    ],
                                ),
                                vm.Container(
                                    title="WIP by equipment",
                                    components=[
                                        vm.Graph(
                                            id="graph-3",
                                            figure=plot_total_production_volume(
                                                data_frame="scenario_daily_data",
                                                metric="daily_avg_wip_ton",
                                            ),
                                        )
                                    ],
                                ),
                                vm.Container(
                                    title="WIP waterfall",
                                    components=[
                                        vm.Graph(
                                            id="graph-4",
                                            figure=plot_total_production_volume(
                                                data_frame="scenario_daily_data",
                                                metric="avg_lead_time_day",
                                            ),
                                        )
                                    ],
                                ),
                            ]
                        ),
                        vm.Container(
                            title="KPI per product type",
                            components=[
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
                            [4, 4, 4, 4],
                        ],
                        row_min_height="150px",
                    ),
                    controls=[
                        vm.Parameter(
                            id="comparison-param-2",
                            targets=[
                                "kpi_card_4.data_frame.scenario_name",
                                "kpi_card_5.data_frame.scenario_name",
                                "kpi_card_6.data_frame.scenario_name",
                                "graph-2.data_frame.scenario_name",
                                "graph-3.data_frame.scenario_name",
                                "graph-4.data_frame.scenario_name",
                            ],
                            selector=vm.Dropdown(
                                options=[
                                    "Increased high-end product",
                                    "Baseline",
                                    "Reduced pricing tier",
                                    "Bundle promotion strategy",
                                ],
                                value="Baseline",
                                multi=False,
                                title="Choose scenario",
                            ),
                        )
                    ],
                ),
            ]
        )
    ],
)


dashboard = vm.Dashboard(
    pages=[page_1, page_2],
    title="QB",
)


if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
