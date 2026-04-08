from time import sleep

import e2e.vizro.constants as cnst
from dash import no_update
from dash.exceptions import PreventUpdate

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import show_notification
from vizro.models.types import capture

iris = px.data.iris()


def raise_exception(exception):
    raise exception


@capture("action")
def notifications_pipeline(exit_path_slider) -> str:
    """Simulates a pipeline which can have different exit paths based on the value of the slider.

    The different exit paths will trigger different types of notifications (error, success, info, warning)
    which can be configured on the buttons that trigger this pipeline.
    """
    match exit_path_slider:
        # error
        case 1:
            raise Exception(
                cnst.CONDITIONAL_NOTIFICATION_CUSTOM_ERROR_MSG,
                ("error", cnst.CONDITIONAL_NOTIFICATION_CUSTOM_ERROR_RESULT),
            )
        # success default
        case 2:
            return None
        # success with custom message
        case 3:
            return ("success", cnst.CONDITIONAL_NOTIFICATION_CUSTOM_SUCCESS_MSG)
        # info
        case 4:
            return ("my_info", cnst.CONDITIONAL_NOTIFICATION_CUSTOM_INFO_MSG)
        # warning
        case 5:
            return ("my_warning", cnst.CONDITIONAL_NOTIFICATION_CUSTOM_WARNING_MSG)

    return None


vm.Page.add_type("components", vm.Slider)

conditional_notifications_page = vm.Page(
    title=cnst.CONDITIONAL_NOTIFICATIONS_PAGE,
    layout=vm.Flex(),
    components=[
        vm.Slider(
            id=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID,
            title="Choose exit path",
            min=1,
            max=5,
            step=1,
            value=1,
            marks={1: "error", 2: "success default", 3: "success with msg", 4: "info", 5: "warning"},
        ),
        vm.Button(
            text="Default error notification",
            id=cnst.CONDITIONAL_NOTIFICATION_ERROR_BUTTON_DEFAULT,
            actions=[
                vm.Action(
                    function=notifications_pipeline(exit_path_slider=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID),
                )
            ],
        ),
        vm.Button(
            text="Default error notification not shown",
            id=cnst.CONDITIONAL_NOTIFICATION_ERROR_BUTTON_NOTIFICATION_NONE,
            actions=[
                vm.Action(
                    function=notifications_pipeline(exit_path_slider=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID),
                    notifications={"error": None},
                )
            ],
        ),
        vm.Button(
            text="Default error notification with error message and result",
            id=cnst.CONDITIONAL_NOTIFICATION_ERROR_BUTTON_NOTIFICATION_WITH_ERROR_MSG_AND_RESULT,
            actions=[
                vm.Action(
                    function=notifications_pipeline(exit_path_slider=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID),
                    notifications={"error": "{{error_msg}}{{result}}"},
                )
            ],
        ),
        vm.Button(
            text="Success notification",
            id=cnst.CONDITIONAL_NOTIFICATION_SUCCESS_BUTTON,
            actions=[
                vm.Action(
                    function=notifications_pipeline(exit_path_slider=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID),
                    notifications={"success": cnst.CONDITIONAL_NOTIFICATION_SUCCESS_MSG + "{{result}}"},
                )
            ],
        ),
        vm.Button(
            text="Progress notification",
            id=cnst.CONDITIONAL_NOTIFICATION_PROGRESS_BUTTON,
            actions=[
                vm.Action(
                    function=notifications_pipeline(exit_path_slider=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID),
                    notifications={"progress": cnst.CONDITIONAL_NOTIFICATION_PROGRESS_MSG + "-{{exit_path_slider}}"},
                )
            ],
        ),
        vm.Button(
            text="Info notification",
            id=cnst.CONDITIONAL_NOTIFICATION_INFO_BUTTON,
            actions=[
                vm.Action(
                    function=notifications_pipeline(exit_path_slider=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID),
                    notifications={"my_info": cnst.CONDITIONAL_NOTIFICATION_INFO_MSG + "{{result}}"},
                )
            ],
        ),
        vm.Button(
            text="Warning notification",
            id=cnst.CONDITIONAL_NOTIFICATION_WARNING_BUTTON,
            actions=[
                vm.Action(
                    function=notifications_pipeline(exit_path_slider=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID),
                    notifications={
                        "my_warning": show_notification(
                            text=cnst.CONDITIONAL_NOTIFICATION_WARNING_MSG + "{{result}}", variant="warning"
                        )
                    },
                )
            ],
        ),
        vm.Button(
            text="3 Success notifications",
            id=cnst.CONDITIONAL_NOTIFICATION_MULTIPLE_SUCCESS_BUTTON,
            actions=[
                show_notification(text=cnst.CONDITIONAL_NOTIFICATION_SUCCESS_MSG_BEFORE_ACTION, variant="success"),
                vm.Action(
                    function=notifications_pipeline(exit_path_slider=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID),
                    notifications={"success": cnst.CONDITIONAL_NOTIFICATION_SUCCESS_MSG_INSIDE_ACTION},
                ),
                show_notification(text=cnst.CONDITIONAL_NOTIFICATION_SUCCESS_MSG_AFTER_ACTION, variant="success"),
            ],
        ),
        vm.Button(
            text="Two Notifications in one action",
            id=cnst.CONDITIONAL_NOTIFICATION_IN_ONE_ACTION_BUTTON,
            actions=[
                vm.Action(
                    function=notifications_pipeline(exit_path_slider=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID),
                    notifications={
                        "success": "Custom pipeline completed!",
                        "my_info": cnst.CONDITIONAL_NOTIFICATION_INFO_MSG + "{{result}}",
                    },
                )
            ],
        ),
        vm.Button(
            text="Progress + Success notifications",
            id=cnst.CONDITIONAL_NOTIFICATION_PROGRESS_AND_SUCCESS_BUTTON,
            actions=[
                vm.Action(
                    function=capture("action")(lambda: sleep(1))(),
                    notifications={
                        "progress": cnst.CONDITIONAL_NOTIFICATION_PROGRESS_MSG,
                        "success": cnst.CONDITIONAL_NOTIFICATION_SUCCESS_MSG,
                    },
                )
            ],
        ),
        vm.Button(
            text="2 no_update actions in a chain.",
            id=cnst.CONDITIONAL_NOTIFICATION_MULTIPLE_NO_UPDATE_BUTTON,
            actions=[
                vm.Action(
                    function=capture("action")(lambda: no_update)(),
                    notifications={"success": "Finished 1 no_update action"},
                    outputs="text",
                ),
                vm.Action(
                    function=capture("action")(lambda: no_update)(),
                    notifications={"success": "Finished 2 no_update action"},
                    outputs="text",
                ),
            ],
        ),
        vm.Button(
            text="2 PreventUpdate actions in a chain.",
            id=cnst.CONDITIONAL_NOTIFICATION_MULTIPLE_PREVENT_UPDATE_BUTTON,
            actions=[
                vm.Action(
                    function=capture("action")(lambda: raise_exception(PreventUpdate))(),
                    notifications={"success": "Finished 1st PreventUpdate action"},
                ),
                vm.Action(
                    function=capture("action")(lambda: raise_exception(PreventUpdate))(),
                    notifications={"success": "Finished 2nd PreventUpdate action"},
                ),
            ],
        ),
        vm.Button(
            text="2 ValueError actions in a chain.",
            id=cnst.CONDITIONAL_NOTIFICATION_MULTIPLE_VALUE_ERROR_BUTTON,
            actions=[
                vm.Action(
                    function=capture("action")(lambda: raise_exception(ValueError))(),
                    notifications={"success": "Finished 1st ValueError action"},
                ),
                vm.Action(
                    function=capture("action")(lambda: raise_exception(ValueError))(),
                    notifications={"success": "Finished 2nd ValueError action"},
                ),
            ],
        ),
        vm.Text(id="text", text="Click the button to run action."),
        vm.Graph(
            figure=px.scatter(
                iris,
                x="sepal_length",
                y="petal_width",
                color="sepal_width",
            ),
        ),
    ],
)
