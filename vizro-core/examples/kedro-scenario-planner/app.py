"""Vizro dashboard that parametrizes, runs and explores a Kedro pipeline."""

import vizro.actions as va
import vizro.models as vm
import vizro.plotly.express as px
from data_generation import CATEGORIES, REGIONS, ensure_orders_data, ensure_scenario_results_file
from kedro_pipeline import build_static_catalog, load_breakdown_data, run_scenario
from vizro import Vizro
from vizro.integrations import kedro as kedro_integration
from vizro.managers import data_manager
from vizro.models._components.form._user_input import UserInput
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

ensure_orders_data()
ensure_scenario_results_file()

static_catalog = build_static_catalog()
for dataset_name, dataset_loader in kedro_integration.datasets_from_catalog(static_catalog).items():
    data_manager[dataset_name] = dataset_loader

data_manager["breakdown"] = load_breakdown_data


@capture("action")
def run_kedro_scenario(scenario_name, region, categories, min_order_value):
    """Runs kedro scenario."""
    result = run_scenario(
        scenario_name=scenario_name,
        region=region,
        categories=categories,
        min_order_value=min_order_value,
    )
    message = (
        f"{result['n_orders']} orders, ${result['total_revenue']:,.0f} total revenue "
        f"(avg ${result['avg_order_value']:,.0f} per order)."
    )
    return message, ("success", message)


vm.Container.add_type("components", UserInput)
vm.Container.add_type("components", vm.Slider)
vm.Container.add_type("components", vm.RadioItems)
vm.Container.add_type("components", vm.Checklist)


page = vm.Page(
    title="Kedro scenario planner",
    layout=vm.Grid(
        grid=[
            [0, 0, 2, 2],
            [0, 0, 2, 2],
            [1, 1, 2, 2],
            [1, 1, 2, 2],
        ]
    ),
    components=[
        vm.Container(
            title="Configure scenario",
            components=[
                UserInput(
                    id="scenario_name_input",
                    title="Scenario name",
                    placeholder="e.g. west-electronics-push",
                ),
                vm.RadioItems(id="region_input", title="Region", options=REGIONS, value=REGIONS[0]),
                vm.Checklist(
                    id="categories_input",
                    title="Categories to include",
                    options=CATEGORIES,
                    value=CATEGORIES,
                ),
                vm.Slider(
                    id="min_order_value_input",
                    title="Minimum order value ($)",
                    min=0,
                    max=500,
                    step=25,
                    value=0,
                ),
                vm.Button(
                    text="Run scenario",
                    actions=[
                        vm.Action(
                            function=run_kedro_scenario(
                                scenario_name="scenario_name_input",
                                region="region_input",
                                categories="categories_input",
                                min_order_value="min_order_value_input",
                            ),
                            outputs="pipeline_status",
                            notifications={
                                "progress": "Running scenario '{scenario_name}'...",
                                "success": "Scenario completed: {result}",
                                "error": "Scenario failed: {error_msg}",
                                "invalid_name": "{error_msg}",
                                "no_categories": "{error_msg}",
                                "duplicate_name": "{error_msg}",
                                "no_matching_orders": "{error_msg}",
                            },
                        ),
                        va.update_targets(targets=["scenario_table"]),
                    ],
                ),
                vm.Text(id="pipeline_status", text="Configure a scenario and click 'Run scenario'."),
            ],
            layout=vm.Grid(
                grid=[[0, 0, 1, 2], [0, 0, 1, 2], [3, 3, 1, 2], [3, 3, 1, 2], [5, 5, 5, -1], [4, -1, -1, -1]]
            ),
            variant="outlined",
        ),
        vm.Container(
            title="Load & explore existing scenarios",
            components=[
                vm.AgGrid(
                    id="scenario_table",
                    figure=dash_ag_grid(
                        "scenario_results",
                        dashGridOptions={"rowSelection": {"mode": "singleRow"}},
                    ),
                    actions=va.set_control(control="scenario_name_param", value="scenario_name"),
                ),
                vm.Button(
                    text="Load Scenario",
                    actions=va.update_targets(targets=["revenue_chart", "orders_chart"]),
                ),
            ],
            layout=vm.Grid(grid=[[0], [0], [1]]),
        ),
        vm.Container(
            title="Selected scenario breakdown",
            layout=vm.Grid(grid=[[0], [1]]),
            components=[
                vm.Graph(
                    id="revenue_chart",
                    figure=px.bar("breakdown", x="category", y="total_revenue", title="Revenue by category"),
                ),
                vm.Graph(
                    id="orders_chart",
                    figure=px.bar("breakdown", x="category", y="n_orders", title="Orders by category"),
                ),
            ],
        ),
    ],
    controls=[
        vm.Parameter(
            id="scenario_name_param",
            targets=["revenue_chart.data_frame.scenario_name", "orders_chart.data_frame.scenario_name"],
            selector=vm.Dropdown(
                options=["(select a scenario)"], value="(select a scenario)", multi=False, actions=None
            ),
            visible=False,
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
