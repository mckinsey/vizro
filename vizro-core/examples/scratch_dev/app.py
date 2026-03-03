import random

from time import sleep

import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va
from vizro import Vizro
from vizro.actions import export_data, show_notification, update_notification
from vizro.models.types import capture


# TODO:
#  ALMOST DONE - Refactor output return value in _action.py
#  DONE - If we enable `text -> va.show_notification(...)` conversion, this would look like:
#  DONE - Clean notifications from the notification panel when the same action is triggered again.
#    - See whether we should introduce hideNotification so that users can hide it before showing explicit notification.
#      Or to do so even before every show_notification action. With it hiding the progress would be automatically solved
#  DONE - Refactor and merge validators in types.
#  Enable providing a second argument of exception containing results.
#  Test by assigning a warning notif to the progress key.
#  Pass through todos and done or open question.
#  See ticket issue and cover other edge cases if any.
#  Check other actions like filter/parameter. What happens if they fail.
#     One pros of introducing update_figures is that we don't have to copy-paste similar code for many actions.
#  Check what happens with the actions chain when no_update, PreventUpdate, or Exception is raised.
#  See whether everything works for export_data as it works for custom action.
#  "page_1_8", action with different output type [None, data, [data], {"output_id": data}] Make sure that all the combinations are covered.
#  hrl
#  tests
#  schema
#  docs

df = px.data.iris().iloc[[0, 1, 50, 51, 100, 101]]
SPECIES_COLORS = {"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"}


# Custom mock pipeline with set or random success/failure
@capture("action")
def random_pipeline(switch_successfulness: bool = False, exit_path_slider: int = 1) -> str:
    sleep(sleep_duration := random.uniform(a=1, b=2))

    if switch_successfulness:
        match exit_path_slider:
            # TODO OQ: Should we enable propagating results from the exception cases as well?
            #  It's possible to enable the following syntax and to parse it internally:
            #   1. raise Exception("Error!", "my_error_1")
            #     ~ raises the `my_error_1` notification if it exists.
            #   2. raise ValueError("Error!", ("my_error_2", result))
            #     ~ raises the `my_error_2` notification if it exists with `result` as {{result}} variable.
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
            return f"Pipeline completed successfully! Execution duration: {sleep_duration:.2f}", ("success", f"Duration: {sleep_duration:.2f}s")
        case 3:
            return f"Pipeline completed, neither success nor failure! Duration: {sleep_duration:.2f}s", "my_custom_success"
        case 4:
            return f"Pipeline completed, neither success nor failure! Duration: {sleep_duration:.2f}s", ("my_custom_success", f"Duration: {sleep_duration:.2f}s")

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
                                    function=random_pipeline(f"{pre}_raise_exc_switch"),
                                    outputs=f"{pre}_text",
                                    notifications={
                                        "progress": va.show_notification(
                                            id=f"{pre}_progress_2",
                                            text="Running custom pipeline. Exception will happen: {{switch_successfulness}}.",
                                            variant="progress",
                                        ),
                                        "success": va.update_notification(
                                            notification=f"{pre}_progress_2",
                                            text="Custom pipeline completed! {{result}}",
                                            variant="success",
                                        ),
                                        "error": va.update_notification(
                                            notification=f"{pre}_progress_2",
                                            # TODO OQ: Should we use {{error_msg}}, {{result}} or something else here?
                                            text="Custom pipeline failed! Exception: {{error_msg}}",
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
                                        # TODO OQ: To show for example how many rows were exported, users should rewrite the
                                        #  export_data.function method to return that info as additional output, and then
                                        #  use {{result}} template variable here. Is that ok?
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
                                            text="Running custom pipeline.\n\n Exception will happen: {{switch_successfulness}}.\n\n Exit path: {{exit_path_slider}}",
                                            variant="progress",
                                        ),
                                        # TODO OQ: We might need to introduce the hide_notification(notification=modelId).
                                        #  Could be useful if users don't want success message after progress for example.
                                        "success": va.update_notification(
                                            notification=f"{pre}_progress_2",
                                            text="Custom pipeline completed! {{result}}",
                                            variant="success",
                                        ),
                                        "my_custom_success": va.update_notification(
                                            notification=f"{pre}_progress_2",
                                            text="Pipeline completed, neither success nor failure! {{result}}",
                                            variant="warning",
                                            title="My warning",
                                        ),
                                        "error": va.update_notification(
                                            notification=f"{pre}_progress_2",
                                            text="Custom pipeline failed! Exception: {{error_msg}} {{result}}",
                                            variant="error",
                                        ),
                                        "my_custom_err": va.update_notification(
                                            notification=f"{pre}_progress_2",
                                            text="Custom pipeline failed! \n\n Error Message: {{error_msg}} {{result}}",
                                            variant="error",
                                            title="My custom error",
                                        )
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
                                        "progress": "Running custom pipeline.\n\n Exception will happen: {{switch_successfulness}}.\n\n Exit path: {{exit_path_slider}}",
                                        "success": "Custom pipeline completed! {{result}}",
                                        "my_custom_success": "Pipeline completed, neither success nor failure! {{result}}",
                                        "error": "Custom pipeline failed! Exception: {{error_msg}}",
                                        "my_custom_err": "Custom pipeline failed! \n\n Error Message: {{error_msg}} {{result}}",
                                    }
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


dashboard = vm.Dashboard(pages=[
    page_0,
    page_1,
    page_2,
    page_3,
    page_4,
    page_5,
    page_6,
])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
