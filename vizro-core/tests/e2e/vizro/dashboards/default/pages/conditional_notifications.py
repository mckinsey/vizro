import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import export_data, show_notification, update_notification
from vizro.models.types import capture

iris = px.data.iris()


@capture("action")
def notifications_pipeline(exit_path_slider) -> str:
    match exit_path_slider:
        # error
        case 1:
            raise Exception(cnst.CONDITIONAL_NOTIFICATION_CUSTOM_ERROR_MSG)
        # success
        case 2:
            return "", ("success", cnst.CONDITIONAL_NOTIFICATION_CUSTOM_SUCCESS_MSG)
        # info
        case 3:
            return "", ("my_info", cnst.CONDITIONAL_NOTIFICATION_CUSTOM_INFO_MSG)
        # warning
        case 4:
            return "", ("my_warning", cnst.CONDITIONAL_NOTIFICATION_CUSTOM_WARNING_MSG)

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
            max=4,
            step=1,
            value=1,
            marks={1: "error", 2: "success", 3: "info", 4: "warning"},
            extra=dict(className="cond-notification-slider"),
        ),
        vm.Button(
            text="Default error notification",
            id=cnst.CONDITIONAL_NOTIFICATION_ERROR_BUTTON,
            actions=[
                vm.Action(
                    function=notifications_pipeline(exit_path_slider=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID),
                    outputs="text",
                )
            ],
        ),
        vm.Button(
            text="Defualt error notification not shown",
            id=cnst.CONDITIONAL_NOTIFICATION_ERROR_BUTTON_NO_MSG,
            actions=[
                vm.Action(
                    function=notifications_pipeline(exit_path_slider=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID),
                    outputs="text",
                    notifications={"error": None},
                )
            ],
        ),
        vm.Button(
            text="Default error notification with error message",
            id=cnst.CONDITIONAL_NOTIFICATION_ERROR_BUTTON_WITH_MSG,
            actions=[
                vm.Action(
                    function=notifications_pipeline(exit_path_slider=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID),
                    outputs="text",
                    notifications={"error": "{{error_msg}}"},
                )
            ],
        ),
        vm.Button(
            text="Success notification",
            id=cnst.CONDITIONAL_NOTIFICATION_SUCCESS_BUTTON,
            actions=[
                vm.Action(
                    function=notifications_pipeline(exit_path_slider=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID),
                    outputs="text",
                    notifications={"success": f"{cnst.CONDITIONAL_NOTIFICATION_SUCCESS_MSG}" + "{{result}}"},
                )
            ],
        ),
        vm.Button(
            text="Progress notification",
            id=cnst.CONDITIONAL_NOTIFICATION_PROGRESS_BUTTON,
            actions=[
                vm.Action(
                    function=notifications_pipeline(exit_path_slider=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID),
                    outputs="text",
                    notifications={
                        "progress": f"{cnst.CONDITIONAL_NOTIFICATION_PROGRESS_MSG}" + "{{exit_path_slider}}"
                    },
                )
            ],
        ),
        vm.Button(
            text="Info notification",
            id=cnst.CONDITIONAL_NOTIFICATION_INFO_BUTTON,
            actions=[
                vm.Action(
                    function=notifications_pipeline(exit_path_slider=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID),
                    outputs="text",
                    notifications={"my_info": f"{cnst.CONDITIONAL_NOTIFICATION_INFO_MSG}" + "{{result}}"},
                )
            ],
        ),
        vm.Button(
            text="Warning notification",
            id=cnst.CONDITIONAL_NOTIFICATION_WARNING_BUTTON,
            actions=[
                vm.Action(
                    function=notifications_pipeline(exit_path_slider=cnst.CONDITIONAL_NOTIFICATION_SLIDER_ID),
                    outputs="text",
                    notifications={
                        "my_warning": show_notification(
                            text=f"{cnst.CONDITIONAL_NOTIFICATION_WARNING_MSG}" + "{{result}}", variant="warning"
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
                    outputs="text",
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
                    outputs="text",
                    notifications={
                        "success": "Custom pipeline completed!",
                        "my_info": f"{cnst.CONDITIONAL_NOTIFICATION_INFO_MSG}" + "{{result}}",
                    },
                )
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
        vm.Button(
            text="Export page",
            id=cnst.CONDITIONAL_NOTIFICATION_EXPORT_BUTTON,
            actions=export_data(
                file_format="csv",
                notifications={
                    "progress": show_notification(
                        id=cnst.CONDITIONAL_NOTIFICATION_PROGRESS_NOTIFICATION_ID,
                        text=cnst.CONDITIONAL_NOTIFICATION_PROGRESS_MSG,
                        variant="progress",
                    ),
                    "success": update_notification(
                        notification=cnst.CONDITIONAL_NOTIFICATION_PROGRESS_NOTIFICATION_ID,
                        text=cnst.CONDITIONAL_NOTIFICATION_SUCCESS_MSG,
                        variant="success",
                    ),
                },
            ),
        ),
    ],
)
