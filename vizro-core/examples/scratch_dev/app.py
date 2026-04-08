import random

from time import sleep

import vizro.models as vm
import vizro.actions as va
from vizro import Vizro
from vizro.actions import show_notification, update_notification
from vizro.models.types import capture

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
    ],
)

pre = "p1"
page_1 = vm.Page(
    id="page_1",
    title="show_notification -> action -> update_notification",
    components=[
        vm.Container(
            title="Progress - Pipeline (1->2s) (Choose to fail) -> Info",
            layout=vm.Flex(),
            components=[
                vm.Switch(id=f"{pre}_raise_exc_switch", value=False, title="Raise exception from the pipeline"),
                vm.Button(
                    text="Run pipeline",
                    actions=[
                        show_notification(id=f"{pre}_progress_2", variant="progress", text="Running pipeline..."),
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
    ],
)


pre = "p2"
page_2 = vm.Page(
    id="page_2",
    title="show_notification -> action (silent default error notif) -> update_notification",
    components=[
        vm.Container(
            title="Progress - Pipeline (1->2s) (Choose to fail) -> Info",
            layout=vm.Flex(),
            components=[
                vm.Switch(id=f"{pre}_raise_exc_switch", value=False, title="Raise exception from the pipeline"),
                vm.Button(
                    text="Run pipeline",
                    actions=[
                        show_notification(id=f"{pre}_progress_2", variant="progress", text="Running pipeline..."),
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
    ],
)


pre = "p3"
page_3 = vm.Page(
    id="page_3",
    title="Progress -> Action -> Success/Error",
    components=[
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
    ],
)

pre = "p4"
page_4 = vm.Page(
    id="page_4",
    title="Progress{{action function argument}} -> Action -> Success{{result}}/Error{{error_msg}}",
    components=[
        vm.Container(
            title="Progress{{switch_successfulness}} - Pipeline (1->2s) (Choose to fail) -> Success{{result}}/Error{{error_msg}}",
            layout=vm.Flex(),
            components=[
                vm.Switch(id=f"{pre}_raise_exc_switch", value=False, title="Raise exception from the pipeline"),
                vm.Button(
                    text="Run pipeline",
                    actions=[
                        vm.Action(
                            function=random_pipeline(f"{pre}_raise_exc_switch", f"{pre}-exit-path-slider"),
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
                    id=f"{pre}-exit-path-slider",
                    min=1,
                    max=4,
                    value=2,
                    extra=dict(className="cond-notification-slider"),
                ),
            ],
        ),
    ],
)

pre = "p5"
page_5 = vm.Page(
    id="page_5",
    title="Progress{{}}-> Action-> Success{1-4}/Error{1-4}",
    components=[
        vm.Container(
            title="Progress{{switch_successfulness}}{{exit_path}} - Pipeline (1->2s) (Choose to fail) -> Success{1-4}/Error{1-4}",
            layout=vm.Flex(),
            components=[
                vm.Slider(
                    id=f"{pre}-exit-path-slider",
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
                                exit_path_slider=f"{pre}-exit-path-slider",
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
    ],
)

pre = "p6"
page_6 = vm.Page(
    id="page_6",
    title="(str)Progress{{}}-> Action-> (str)Success{1-4}/(str)Error{1-4}",
    components=[
        vm.Container(
            title="(str)Progress{{switch_successfulness}}{{exit_path}} - Pipeline (1->2s) (Choose to fail) -> (str)Success{1-4}/(str)Error{1-4}",
            layout=vm.Flex(),
            components=[
                vm.Slider(
                    id=f"{pre}-exit-path-slider",
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
                                exit_path_slider=f"{pre}-exit-path-slider",
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
    ],
)


from dash import no_update
from dash.exceptions import PreventUpdate


def raise_exception(exception):
    raise exception


pre = "p7"
page_7 = vm.Page(
    id="page_7",
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
                    notifications={"success": "Finished 2nd no_update action"},
                ),
                vm.Action(
                    function=capture("action")(lambda: no_update)(),
                    outputs=f"{pre}_text_output",
                    notifications={"success": "Finished 3rd no_update action"},
                ),
            ],
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
                    notifications={"success": "Finished 2nd no_update action"},
                ),
                vm.Action(
                    function=capture("action")(lambda: raise_exception(PreventUpdate))(),
                    outputs=f"{pre}_text_output",
                    notifications={"success": "Finished 3rd no_update action"},
                ),
            ],
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
                    notifications={"success": "Finished 2nd no_update action"},
                ),
                vm.Action(
                    function=capture("action")(lambda: raise_exception(ValueError))(),
                    outputs=f"{pre}_text_output",
                    notifications={"success": "Finished 3rd no_update action"},
                ),
            ],
        ),
        vm.Text(id=f"{pre}_text_output", text="Action not triggered yet."),
    ],
)

pre = "p8"
page_8 = vm.Page(
    id="page_8",
    title="Different action output structure",
    layout=vm.Flex(),
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Success Actions without notifications",
                    layout=vm.Flex(),
                    components=[
                        vm.Button(
                            text="Action with no output",
                            actions=vm.Action(
                                function=capture("action")(lambda: print("Action with no output executed"))(),
                            ),
                        ),
                        vm.Button(
                            text="Action with single output",
                            actions=vm.Action(
                                function=capture("action")(lambda _trigger: f"Button clicked {_trigger} times.")(),
                                outputs=f"{pre}_text",
                            ),
                        ),
                        vm.Button(
                            text="Action with list outputs",
                            actions=vm.Action(
                                function=capture("action")(lambda _trigger: f"Button clicked {_trigger} times.")(),
                                outputs=[f"{pre}_text"],
                            ),
                        ),
                        vm.Button(
                            text="Action with dict outputs",
                            actions=vm.Action(
                                function=capture("action")(
                                    lambda _trigger: {f"p8_text_key": f"Button clicked {_trigger} times."}
                                )(),
                                outputs={f"{pre}_text_key": f"{pre}_text"},
                            ),
                        ),
                    ],
                ),
                vm.Container(
                    title="Success Actions with notifications",
                    layout=vm.Flex(),
                    components=[
                        vm.Button(
                            text="Action with no output",
                            actions=vm.Action(
                                function=capture("action")(lambda: "my_success")(),
                                notifications={"my_success": "Action with no output executed successfully!"},
                            ),
                        ),
                        vm.Button(
                            text="Action with single output",
                            actions=vm.Action(
                                function=capture("action")(
                                    lambda _trigger: (f"Button clicked {_trigger} times.", "my_success")
                                )(),
                                outputs=f"{pre}_text",
                                notifications={"my_success": "Action with single output executed successfully!"},
                            ),
                        ),
                        vm.Button(
                            text="Action with list outputs",
                            actions=vm.Action(
                                function=capture("action")(
                                    lambda _trigger: (f"Button clicked {_trigger} times.", "my_success")
                                )(),
                                outputs=[f"{pre}_text"],
                                notifications={"my_success": "Action with list outputs executed successfully!"},
                            ),
                        ),
                        vm.Button(
                            text="Action with dict outputs",
                            actions=vm.Action(
                                function=capture("action")(
                                    lambda _trigger: (
                                        {f"p8_text_key": f"Button clicked {_trigger} times."},
                                        "my_success",
                                    )
                                )(),
                                outputs={f"{pre}_text_key": f"{pre}_text"},
                                notifications={"my_success": "Action with dict outputs executed successfully!"},
                            ),
                        ),
                    ],
                ),
                vm.Container(
                    title="Error Actions without notifications",
                    layout=vm.Flex(),
                    components=[
                        vm.Button(
                            text="Action with no output",
                            actions=vm.Action(
                                function=capture("action")(lambda: raise_exception(ValueError))(),
                            ),
                        ),
                        vm.Button(
                            text="Action with single output",
                            actions=vm.Action(
                                function=capture("action")(lambda: raise_exception(ValueError))(),
                                outputs=f"{pre}_text",
                            ),
                        ),
                        vm.Button(
                            text="Action with list outputs",
                            actions=vm.Action(
                                function=capture("action")(lambda: raise_exception(ValueError))(),
                                outputs=[f"{pre}_text"],
                            ),
                        ),
                        vm.Button(
                            text="Action with dict outputs",
                            actions=vm.Action(
                                function=capture("action")(lambda: raise_exception(ValueError))(),
                                outputs={f"{pre}_text_key": f"{pre}_text"},
                            ),
                        ),
                    ],
                ),
            ]
        ),
        vm.Text(id=f"{pre}_text", text="Action not triggered yet."),
    ],
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
    Vizro().build(dashboard).run(debug=True)
