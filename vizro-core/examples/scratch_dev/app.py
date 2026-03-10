import random

from time import sleep

import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va
from vizro import Vizro
from vizro.actions import export_data, show_notification, update_notification
from vizro.models.types import capture

df = px.data.iris().iloc[[0, 1, 50, 51, 100, 101]]
SPECIES_COLORS = {"setosa": "#097DFE", "versicolor": "#6F39E3", "virginica": "#05D0F0"}


# Custom mock pipeline with set or random success/failure
@capture("action")
def random_pipeline(switch_successfulness: bool = False, exit_path_slider: int = 1) -> str:
    sleep(sleep_duration := random.uniform(a=1, b=2))

    if switch_successfulness:
        match exit_path_slider:
            case 1:
                raise Exception("Random error occurred!")
            case 2:
                raise Exception("Random error occurred!", ("error", f"Duration: {sleep_duration:.2f}s"))
            case 3:
                raise ValueError("It's value error!", "my_custom_err")
            case 4:
                raise IndexError("Index error occurred!", ("my_custom_err", f"Duration: {sleep_duration:.2f}s"))

    match exit_path_slider:
        case 1:
            return f"Pipeline completed successfully! Execution duration: {sleep_duration:.2f}"
        case 2:
            return f"Pipeline completed successfully! Execution duration: {sleep_duration:.2f}", (
                "success",
                f"Duration: {sleep_duration:.2f}s",
            )
        case 3:
            return (
                f"Pipeline completed, neither success nor failure! Duration: {sleep_duration:.2f}s",
                "my_custom_success",
            )
        case 4:
            return f"Pipeline completed, neither success nor failure! Duration: {sleep_duration:.2f}s", (
                "my_custom_success",
                f"Duration: {sleep_duration:.2f}s",
            )

    return None


vm.Container.add_type("components", vm.Switch)
vm.Container.add_type("components", vm.Slider)

pre = "p0"
page_0 = vm.Page(
    title="Action without notifications",
    id="page_0",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Pipeline (1->2s) (Choose to fail)",
                    layout=vm.Flex(),
                    components=[
                        vm.Switch(id=f"{pre}_raise_exc_switch", value=False, title="Raise exception from the pipeline"),
                        vm.Button(
                            text="Run pipeline",
                            actions=vm.Action(
                                function=random_pipeline(f"{pre}_raise_exc_switch"),
                                outputs=f"{pre}_text",
                            ),
                        ),
                        vm.Text(id=f"{pre}_text", text="Click the button to run action."),
                    ],
                ),
                vm.Container(
                    title="Export (2s) (50% to fail)",
                    components=[
                        vm.Graph(
                            figure=px.scatter(
                                df,
                                x="sepal_width",
                                y="sepal_length",
                                color="species",
                                color_discrete_map=SPECIES_COLORS,
                            )
                        ),
                        vm.Button(text="Export data", actions=export_data()),
                    ],
                ),
            ]
        )
    ],
)


pre = "p1"
page_1 = vm.Page(
    id="page_1",
    title="show_notification -> action -> update_notification",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Progress - Pipeline (1->2s) (Choose to fail) -> Info",
                    layout=vm.Flex(),
                    components=[
                        vm.Switch(id=f"{pre}_raise_exc_switch", value=False, title="Raise exception from the pipeline"),
                        vm.Button(
                            text="Run pipeline",
                            actions=[
                                show_notification(
                                    id=f"{pre}_progress_2", variant="progress", text="Running pipeline..."
                                ),
                                vm.Action(function=random_pipeline(f"{pre}_raise_exc_switch"), outputs=f"{pre}_text"),
                                update_notification(
                                    notification=f"{pre}_progress_2",
                                    variant="info",
                                    text="Pipeline action finished. No results about action's successfulness",
                                ),
                            ],
                        ),
                        vm.Text(id=f"{pre}_text", text="Click the button to run action."),
                    ],
                ),
                vm.Container(
                    title="Progress - Export (2s) (50% to fail) - Info",
                    components=[
                        vm.Graph(
                            figure=px.scatter(
                                df,
                                x="sepal_width",
                                y="sepal_length",
                                color="species",
                                color_discrete_map=SPECIES_COLORS,
                            )
                        ),
                        vm.Button(
                            text="Export data",
                            actions=[
                                show_notification(id=f"{pre}_progress_1", variant="progress", text="Exporting data..."),
                                export_data(),
                                update_notification(
                                    notification=f"{pre}_progress_1",
                                    variant="info",
                                    text="Exporting action finished. No results about action's successfulness",
                                ),
                            ],
                        ),
                    ],
                ),
            ]
        )
    ],
    controls=[vm.Filter(column="species")],
)


pre = "p2"
page_2 = vm.Page(
    id="page_2",
    title="show_notification -> action (silent default error notif) -> update_notification",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Progress - Pipeline (1->2s) (Choose to fail) -> Info",
                    layout=vm.Flex(),
                    components=[
                        vm.Switch(id=f"{pre}_raise_exc_switch", value=False, title="Raise exception from the pipeline"),
                        vm.Button(
                            text="Run pipeline",
                            actions=[
                                show_notification(
                                    id=f"{pre}_progress_2", variant="progress", text="Running pipeline..."
                                ),
                                vm.Action(
                                    function=random_pipeline(f"{pre}_raise_exc_switch"),
                                    outputs=f"{pre}_text",
                                    notifications={"error": None},
                                ),
                                update_notification(
                                    notification=f"{pre}_progress_2",
                                    variant="info",
                                    text="Pipeline action finished. No results about action's successfulness",
                                ),
                            ],
                        ),
                        vm.Text(id=f"{pre}_text", text="Click the button to run action."),
                    ],
                ),
                vm.Container(
                    title="Progress - Export (2s) (50% to fail) - Info",
                    components=[
                        vm.Graph(
                            figure=px.scatter(
                                df,
                                x="sepal_width",
                                y="sepal_length",
                                color="species",
                                color_discrete_map=SPECIES_COLORS,
                            )
                        ),
                        vm.Button(
                            text="Export data",
                            actions=[
                                show_notification(id=f"{pre}_progress_1", variant="progress", text="Exporting data..."),
                                export_data(notifications={"error": None}),
                                update_notification(
                                    notification=f"{pre}_progress_1",
                                    variant="info",
                                    text="Exporting action finished. No results about action's successfulness",
                                ),
                            ],
                        ),
                    ],
                ),
            ]
        )
    ],
    controls=[vm.Filter(column="species")],
)


pre = "p3"
page_3 = vm.Page(
    id="page_3",
    title="Progress -> Action -> Success/Error",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Progress - Pipeline (1->2s) (Choose to fail) -> Success/Error",
                    layout=vm.Flex(),
                    components=[
                        vm.Switch(id=f"{pre}_raise_exc_switch", value=False, title="Raise exception from the pipeline"),
                        vm.Button(
                            text="Run pipeline",
                            actions=[
                                vm.Action(
                                    function=random_pipeline(f"{pre}_raise_exc_switch"),
                                    outputs=f"{pre}_text",
                                    notifications={
                                        "progress": va.show_notification(
                                            id=f"{pre}_progress_2",
                                            text="Running custom pipeline...",
                                            variant="progress",
                                        ),
                                        "success": va.update_notification(
                                            notification=f"{pre}_progress_2",
                                            text="Custom pipeline completed!",
                                            variant="success",
                                        ),
                                        "error": va.update_notification(
                                            notification=f"{pre}_progress_2",
                                            text="Custom pipeline failed!",
                                            variant="error",
                                        ),
                                    },
                                )
                            ],
                        ),
                        vm.Text(id=f"{pre}_text", text="Click the button to run action."),
                    ],
                ),
                vm.Container(
                    title="Progress - Export (2s) (50% to fail) - Success/Error",
                    components=[
                        vm.Graph(
                            figure=px.scatter(
                                df,
                                x="sepal_width",
                                y="sepal_length",
                                color="species",
                                color_discrete_map=SPECIES_COLORS,
                            )
                        ),
                        vm.Button(
                            text="Export data",
                            actions=[
                                va.export_data(
                                    notifications={
                                        "progress": va.show_notification(
                                            id=f"{pre}_progress_1",
                                            text="Exporting data...",
                                            variant="progress",
                                        ),
                                        "success": va.update_notification(
                                            notification=f"{pre}_progress_1",
                                            text="Data exported successfully!",
                                            variant="success",
                                        ),
                                        "error": va.update_notification(
                                            notification=f"{pre}_progress_1",
                                            text="Export failed!",
                                            variant="error",
                                        ),
                                    }
                                )
                            ],
                        ),
                    ],
                ),
            ]
        )
    ],
    controls=[vm.Filter(column="species")],
)

pre = "p4"
page_4 = vm.Page(
    id="page_4",
    title="Progress{{action function argument}} -> Action -> Success{{result}}/Error{{error_msg}}",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Progress{{switch_successfulness}} - Pipeline (1->2s) (Choose to fail) -> Success{{result}}/Error{{error_msg}}",
                    layout=vm.Flex(),
                    components=[
                        vm.Switch(id=f"{pre}_raise_exc_switch", value=False, title="Raise exception from the pipeline"),
                        vm.Button(
                            text="Run pipeline",
                            actions=[
                                vm.Action(
                                    function=random_pipeline(f"{pre}_raise_exc_switch", f"{pre}_exit_path_slider"),
                                    outputs=f"{pre}_text",
                                    notifications={
                                        "progress": va.show_notification(
                                            id=f"{pre}_progress_2",
                                            text="Running custom pipeline.\n\nException will happen: {{switch_successfulness}}.",
                                            variant="progress",
                                        ),
                                        "success": va.update_notification(
                                            notification=f"{pre}_progress_2",
                                            text="Custom pipeline completed!\n\n{{result}}",
                                            variant="success",
                                        ),
                                        "error": va.update_notification(
                                            notification=f"{pre}_progress_2",
                                            text="Custom pipeline failed! Exception:\n\n{{error_msg}}",
                                            variant="error",
                                        ),
                                    },
                                )
                            ],
                        ),
                        vm.Text(id=f"{pre}_text", text="Click the button to run action."),
                        vm.Slider(
                            id=f"{pre}_exit_path_slider", min=1, max=4, value=2,
                            extra=dict(className="cond-notification-slider"),
                        ),
                    ],
                ),
                vm.Container(
                    title="Progress - Export (2s) (50% to fail) - Success/Error{{error_msg}}",
                    components=[
                        vm.Graph(
                            figure=px.scatter(
                                df,
                                x="sepal_width",
                                y="sepal_length",
                                color="species",
                                color_discrete_map=SPECIES_COLORS,
                            )
                        ),
                        vm.Button(
                            text="Export data",
                            actions=[
                                va.export_data(
                                    notifications={
                                        "progress": va.show_notification(
                                            id=f"{pre}_progress_1",
                                            text="Exporting data...",
                                            variant="progress",
                                        ),
                                        "success": va.update_notification(
                                            notification=f"{pre}_progress_1",
                                            text="Data exported successfully!",
                                            variant="success",
                                        ),
                                        "error": va.update_notification(
                                            notification=f"{pre}_progress_1",
                                            text="Export failed!\n\n{{error_msg}}",
                                            variant="error",
                                        ),
                                    }
                                )
                            ],
                        ),
                    ],
                ),
            ]
        )
    ],
    controls=[vm.Filter(column="species")],
)

pre = "p5"
page_5 = vm.Page(
    id="page_5",
    title="Progress{{}}-> Action-> Success{1-4}/Error{1-4}",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Progress{{switch_successfulness}}{{exit_path}} - Pipeline (1->2s) (Choose to fail) -> Success{1-4}/Error{1-4}",
                    layout=vm.Flex(),
                    components=[
                        vm.Slider(
                            id=f"{pre}_exit_path_slider",
                            title="Choose exit path",
                            min=1,
                            max=4,
                            step=1,
                            value=1,
                            marks={1: "1", 2: "2", 3: "3", 4: "4"},
                            extra=dict(className="cond-notification-slider"),
                        ),
                        vm.Switch(id=f"{pre}_raise_exc_switch", value=False, title="Raise exception from the pipeline"),
                        vm.Button(
                            text="Run pipeline",
                            actions=[
                                vm.Action(
                                    function=random_pipeline(
                                        switch_successfulness=f"{pre}_raise_exc_switch",
                                        exit_path_slider=f"{pre}_exit_path_slider",
                                    ),
                                    outputs=f"{pre}_text",
                                    notifications={
                                        "progress": va.show_notification(
                                            id=f"{pre}_progress_2",
                                            text="Running custom pipeline.\n\nException will happen: {{switch_successfulness}}.\n\nExit path: {{exit_path_slider}}",
                                            variant="progress",
                                        ),
                                        "success": va.update_notification(
                                            notification=f"{pre}_progress_2",
                                            text="Custom pipeline completed!\n\n{{result}}",
                                            variant="success",
                                        ),
                                        "my_custom_success": va.update_notification(
                                            notification=f"{pre}_progress_2",
                                            text="Pipeline completed, neither success nor failure!\n\n{{result}}",
                                            variant="warning",
                                            title="My warning",
                                        ),
                                        "error": va.update_notification(
                                            notification=f"{pre}_progress_2",
                                            text="Custom pipeline failed!\n\nException: {{error_msg}}\n\n{{result}}",
                                            variant="error",
                                        ),
                                        "my_custom_err": va.update_notification(
                                            notification=f"{pre}_progress_2",
                                            text="Custom pipeline failed!\n\nError Message: {{error_msg}}\n\n{{result}}",
                                            variant="warning",
                                            title="My custom Warning",
                                        ),
                                    },
                                )
                            ],
                        ),
                        vm.Text(id=f"{pre}_text", text="Click the button to run action."),
                    ],
                ),
                vm.Container(
                    title="Progress - Export (2s) (50% to fail) - Success/Error{{error_msg}}",
                    components=[
                        vm.Graph(
                            figure=px.scatter(
                                df,
                                x="sepal_width",
                                y="sepal_length",
                                color="species",
                                color_discrete_map=SPECIES_COLORS,
                            )
                        ),
                        vm.Button(
                            text="Export data",
                            actions=[
                                va.export_data(
                                    notifications={
                                        "progress": va.show_notification(
                                            id=f"{pre}_progress_1",
                                            text="Exporting data...",
                                            variant="progress",
                                        ),
                                        "success": va.update_notification(
                                            notification=f"{pre}_progress_1",
                                            text="Data exported successfully!",
                                            variant="success",
                                        ),
                                        "error": va.update_notification(
                                            notification=f"{pre}_progress_1",
                                            text="Export failed! {{error_msg}}",
                                            variant="error",
                                        ),
                                    }
                                )
                            ],
                        ),
                    ],
                ),
            ]
        )
    ],
    controls=[vm.Filter(column="species")],
)

pre = "p6"
page_6 = vm.Page(
    id="page_6",
    title="(str)Progress{{}}-> Action-> (str)Success{1-4}/(str)Error{1-4}",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="(str)Progress{{switch_successfulness}}{{exit_path}} - Pipeline (1->2s) (Choose to fail) -> (str)Success{1-4}/(str)Error{1-4}",
                    layout=vm.Flex(),
                    components=[
                        vm.Slider(
                            id=f"{pre}_exit_path_slider",
                            title="Choose exit path",
                            min=1,
                            max=4,
                            step=1,
                            value=1,
                            marks={1: "1", 2: "2", 3: "3", 4: "4"},
                            extra=dict(className="cond-notification-slider"),
                        ),
                        vm.Switch(id=f"{pre}_raise_exc_switch", value=False, title="Raise exception from the pipeline"),
                        vm.Button(
                            text="Run pipeline",
                            actions=[
                                vm.Action(
                                    function=random_pipeline(
                                        switch_successfulness=f"{pre}_raise_exc_switch",
                                        exit_path_slider=f"{pre}_exit_path_slider",
                                    ),
                                    outputs=f"{pre}_text",
                                    notifications={
                                        "progress": "Running custom pipeline.\n\nException will happen: {{switch_successfulness}}.\n\nExit path: {{exit_path_slider}}",
                                        "success": "Custom pipeline completed!\n\n{{result}}",
                                        "my_custom_success": "Pipeline completed, neither success nor failure!\n\n{{result}}",
                                        "error": "Custom pipeline failed!\n\nException: {{error_msg}}",
                                        "my_custom_err": "Custom pipeline failed!\n\nError Message: {{error_msg}}\n\n{{result}}",
                                    },
                                )
                            ],
                        ),
                        vm.Text(id=f"{pre}_text", text="Click the button to run action."),
                    ],
                ),
                vm.Container(
                    title="Progress - Export (2s) (50% to fail) - Success/Error{{error_msg}}",
                    components=[
                        vm.Graph(
                            figure=px.scatter(
                                df,
                                x="sepal_width",
                                y="sepal_length",
                                color="species",
                                color_discrete_map=SPECIES_COLORS,
                            )
                        ),
                        vm.Button(
                            text="Export data",
                            actions=[
                                va.export_data(
                                    notifications={
                                        "progress": "Exporting data...",
                                        "success": "Data exported successfully!",
                                        "error": "Export failed! {{error_msg}}",
                                    }
                                )
                            ],
                        ),
                    ],
                ),
            ]
        )
    ],
    controls=[vm.Filter(column="species")],
)


# ========== Weird edge case examples ========== #

from vizro.managers import data_manager
from vizro.actions._parameter_action import _parameter

data_manager["dynamic_df"] = lambda number_of_points=10: px.data.iris().sample(number_of_points)


pre = "p7"
page_7 = vm.Page(
    id="page_7",
    title="Warning progress | (50% to fail) Parameter Action | Error{{error_msg}}/Success",
    components=[
        vm.Graph(
            id="graph_7",
            figure=px.scatter(
                "dynamic_df",
                x="sepal_width",
                y="sepal_length",
                color="species",
                color_discrete_map=SPECIES_COLORS,
            )
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["graph_7.data_frame.number_of_points"],
            selector=vm.Slider(
                title="Trigger slow data loading", min=10, max=150, step=10, value=10,
                actions=_parameter(
                    targets=["graph_7.data_frame.number_of_points"],
                    notifications={
                        "progress": va.show_notification(
                            variant="warning",
                            text="Loading heavy data. Do not close the app!",
                            auto_close=False,
                        ),
                        "error": "{{error_msg}}",
                        "success": "Data loaded successfully",
                    }
                )
            ),
        )
    ]
)

from dash import no_update
from dash.exceptions import PreventUpdate


def raise_exception(exception):
    raise exception


pre = "p8"
page_8 = vm.Page(
    id="page_8",
    title="no_update / PreventUpdate in action chains",
    components=[
        vm.Button(
            text="3 no_update actions in a chain.",
            actions=[
                vm.Action(
                    function=capture("action")(lambda: no_update)(),
                    outputs=f"{pre}_text_output",
                    notifications={"success": "Finished 1st no_update action"},
                ),
                vm.Action(
                    function=capture("action")(lambda: no_update)(),
                    outputs=f"{pre}_text_output",
                    notifications={"success": "Finished 2st no_update action"},
                ),
                vm.Action(
                    function=capture("action")(lambda: no_update)(),
                    outputs=f"{pre}_text_output",
                    notifications={"success": "Finished 3st no_update action"},
                )
            ]
        ),
        vm.Button(
            text="3 PreventUpdate actions in a chain.",
            actions=[
                vm.Action(
                    function=capture("action")(lambda: raise_exception(PreventUpdate))(),
                    outputs=f"{pre}_text_output",
                    notifications={"success": "Finished 1st no_update action"},
                ),
                vm.Action(
                    function=capture("action")(lambda: raise_exception(PreventUpdate))(),
                    outputs=f"{pre}_text_output",
                    notifications={"success": "Finished 2st no_update action"},
                ),
                vm.Action(
                    function=capture("action")(lambda: raise_exception(PreventUpdate))(),
                    outputs=f"{pre}_text_output",
                    notifications={"success": "Finished 3st no_update action"},
                )
            ]
        ),
        vm.Button(
            text="3 ValueError actions in a chain.",
            actions=[
                vm.Action(
                    function=capture("action")(lambda: raise_exception(ValueError))(),
                    outputs=f"{pre}_text_output",
                    notifications={"success": "Finished 1st no_update action"},
                ),
                vm.Action(
                    function=capture("action")(lambda: raise_exception(ValueError))(),
                    outputs=f"{pre}_text_output",
                    notifications={"success": "Finished 2st no_update action"},
                ),
                vm.Action(
                    function=capture("action")(lambda: raise_exception(ValueError))(),
                    outputs=f"{pre}_text_output",
                    notifications={"success": "Finished 3st no_update action"},
                )
            ]
        ),
        vm.Text(
            id=f"{pre}_text_output",
            text="Action not triggered yet."
        )
    ]
)

dashboard = vm.Dashboard(
    pages=[
        page_0,
        page_1,
        page_2,
        page_3,
        page_4,
        page_5,
        page_6,
        page_7,
        page_8,
    ]
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
