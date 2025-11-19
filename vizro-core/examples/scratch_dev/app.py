import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va
from vizro import Vizro

df = px.data.iris()

page_1 = vm.Page(
    title="Test dmc notification system",
    layout=vm.Flex(direction="row"),
    actions=[
        va.show_notification(
            message="Welcome to the notification demo! Click on the buttons to see different notification types.",
            title="Welcome",
            icon="handshake",
            auto_close=False,
        )
    ],
    components=[
        vm.Button(
            icon="check_circle",
            text="Success Notification",
            actions=[
                va.show_notification(
                    message="Operation completed successfully!",
                    title="Success",
                    variant="success",
                )
            ],
        ),
        vm.Button(
            icon="warning",
            text="Warning Notification",
            actions=[
                va.show_notification(
                    message="Please review this warning message.",
                    title="Warning",
                    variant="warning",
                )
            ],
        ),
        vm.Button(
            text="Error Notification",
            icon="error",
            actions=[
                va.show_notification(
                    message="An error occurred during the operation.",
                    title="Error",
                    variant="error",
                )
            ],
        ),
        vm.Button(
            text="Info Notification",
            icon="info",
            actions=[
                va.show_notification(
                    message="Here's some useful information for you.",
                    title="Info",
                    variant="info",
                )
            ],
        ),
        vm.Button(
            text="No Auto-Close",
            icon="close",
            actions=[
                va.show_notification(
                    message="This notification will stay until you close it manually.",
                    title="Persistent",
                    variant="info",
                    auto_close=False,
                )
            ],
        ),
        vm.Button(
            text="Simple Message (default title)",
            icon="info",
            actions=[
                va.show_notification(
                    message="A simple notification with default title and variant.",
                    variant="info",
                )
            ],
        ),
        vm.Button(
            text="Custom Icon",
            icon="celebration",
            actions=[
                va.show_notification(
                    message="Check out this new feature!",
                    title="New Feature",
                    variant="success",
                    icon="celebration",
                )
            ],
        ),
        vm.Button(
            text="1. Show Loading",
            icon="hourglass_empty",
            actions=[
                va.show_notification(
                    notification_id="update-demo",
                    message="Processing your request...",
                    title="Processing",
                    variant="info",
                    loading=True,
                    auto_close=False,
                )
            ],
        ),
        vm.Button(
            text="2. Update to Complete",
            icon="done",
            actions=[
                va.show_notification(
                    notification_id="update-demo",
                    message="Your request has been processed successfully!",
                    title="Complete",
                    variant="success",
                    action="update",
                )
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page_1])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
