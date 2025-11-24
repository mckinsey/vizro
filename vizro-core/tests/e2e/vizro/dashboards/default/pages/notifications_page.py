import e2e.vizro.constants as cnst

import vizro.actions as va
import vizro.models as vm
import vizro.plotly.express as px

df = px.data.iris()

static_notifications_page = vm.Page(
    title=cnst.STATIC_NOTIFICATIONS_PAGE,
    layout=vm.Flex(),
    components=[
        vm.Button(
            id=cnst.SUCCESS_NOTIFICATION_BUTTON,
            icon=cnst.SUCCESS_NOTIFICATION_ICON,
            text="Success Notification",
            actions=[
                va.show_notification(
                    notification_id=cnst.SUCCESS_NOTIFICATION_ID,
                    message=cnst.SUCCESS_NOTIFICATION_MESSAGE,
                    variant="success",
                    auto_close=False,
                )
            ],
        ),
        vm.Button(
            id=cnst.WARNING_NOTIFICATION_BUTTON,
            icon=cnst.WARNING_NOTIFICATION_ICON,
            text="Warning Notification",
            actions=[
                va.show_notification(
                    notification_id=cnst.WARNING_NOTIFICATION_ID,
                    message=cnst.WARNING_NOTIFICATION_MESSAGE,
                    variant="warning",
                    auto_close=False,
                )
            ],
        ),
        vm.Button(
            id=cnst.ERROR_NOTIFICATION_BUTTON,
            icon=cnst.ERROR_NOTIFICATION_ICON,
            text="Error Notification",
            actions=[
                va.show_notification(
                    notification_id=cnst.ERROR_NOTIFICATION_ID,
                    message=cnst.ERROR_NOTIFICATION_MESSAGE,
                    variant="error",
                    auto_close=False,
                )
            ],
        ),
        vm.Button(
            id=cnst.INFO_NOTIFICATION_BUTTON,
            icon=cnst.INFO_NOTIFICATION_ICON,
            text="Info Notification",
            actions=[
                va.show_notification(
                    notification_id=cnst.INFO_NOTIFICATION_ID,
                    message=cnst.INFO_NOTIFICATION_MESSAGE,
                    variant="info",
                    auto_close=False,
                )
            ],
        ),
        vm.Button(
            id=cnst.CUSTOM_NOTIFICATION_BUTTON,
            icon=cnst.CUSTOM_NOTIFICATION_ICON,
            text="Custom Notification",
            actions=[
                va.show_notification(
                    notification_id=cnst.CUSTOM_NOTIFICATION_ID,
                    message=cnst.CUSTOM_NOTIFICATION_MESSAGE,
                    title=cnst.CUSTOM_NOTIFICATION_TITLE,
                    variant="success",
                    icon=cnst.CUSTOM_NOTIFICATION_ICON,
                    auto_close=False,
                )
            ],
        ),
        vm.Button(
            id=cnst.PROGRESS_NOTIFICATION_BUTTON,
            text="1. Show Loading",
            icon="hourglass_empty",
            actions=[
                va.show_notification(
                    notification_id=cnst.UPDATE_NOTIFICATION_ID,
                    message=cnst.PROGRESS_NOTIFICATION_MESSAGE,
                    title=cnst.PROGRESS_NOTIFICATION_TITLE,
                    variant="progress",
                )
            ],
        ),
        vm.Button(
            id=cnst.UPDATE_NOTIFICATION_BUTTON,
            text="2. Update to Complete",
            icon="check_circle",
            actions=[
                va.show_notification(
                    notification_id=cnst.UPDATE_NOTIFICATION_ID,
                    message=cnst.UPDATE_NOTIFICATION_MESSAGE,
                    title=cnst.UPDATE_NOTIFICATION_TITLE,
                    variant="success",
                    action="update",
                    auto_close=False,
                )
            ],
        ),
        vm.Button(
            id=cnst.LINK_NOTIFICATION_BUTTON,
            text="Markdown with Link",
            icon="link",
            actions=[
                va.show_notification(
                    notification_id=cnst.LINK_NOTIFICATION_ID,
                    message=cnst.LINK_NOTIFICATION_MESSAGE,
                    title=cnst.LINK_NOTIFICATION_TITLE,
                    auto_close=False,
                )
            ],
        ),
        vm.Button(
            id=cnst.AUTO_CLOSE_NOTIFICATION_BUTTON,
            text="Auto-Close",
            icon="close",
            actions=[
                va.show_notification(
                    notification_id=cnst.AUTO_CLOSE_NOTIFICATION_ID,
                    message=cnst.AUTO_CLOSE_NOTIFICATION_MESSAGE,
                    title=cnst.AUTO_CLOSE_NOTIFICATION_TITLE,
                    variant="info",
                )
            ],
        ),
    ],
)
