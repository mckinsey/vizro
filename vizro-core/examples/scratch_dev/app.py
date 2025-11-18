import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va
from vizro import Vizro

df = px.data.iris()

page_1 = vm.Page(
    title="Test dmc notification system",
    layout=vm.Flex(direction="row"),
    components=[
        vm.Button(
            text="✅ Success Notification",
            actions=[
                va.show_notification(
                    message="Operation completed successfully!",
                    title="Success",
                    kind="success",
                )
            ],
        ),
        vm.Button(
            text="⚠️ Warning Notification",
            actions=[
                va.show_notification(
                    message="Please review this warning message.",
                    title="Warning",
                    kind="warning",
                    auto_close=5000,
                )
            ],
        ),
        vm.Button(
            text="❌ Error Notification",
            actions=[
                va.show_notification(
                    message="An error occurred during the operation.",
                    title="Error",
                    kind="error",
                    auto_close=6000,
                )
            ],
        ),
        vm.Button(
            text="ℹ️ Info Notification",
            actions=[
                va.show_notification(
                    message="Here's some useful information for you.",
                    title="Info",
                    kind="info",
                )
            ],
        ),
        vm.Button(
            text="🔔 No Auto-Close",
            actions=[
                va.show_notification(
                    message="This notification will stay until you close it manually.",
                    title="Persistent",
                    kind="info",
                    auto_close=False,
                )
            ],
        ),
        vm.Button(
            text="📊 Simple Message (no title)",
            actions=[
                va.show_notification(
                    message="A simple notification without a title.",
                    kind="info",
                )
            ],
        ),
        vm.Button(
            text="🎉 Custom Icon",
            actions=[
                va.show_notification(
                    message="Check out this new feature!",
                    title="New Feature",
                    kind="success",
                    icon="celebration",  # Custom Google Material icon
                )
            ],
        ),
        vm.Button(
            text="⏳ Loading Notification",
            actions=[
                va.show_notification(
                    message="Processing your request...",
                    title="Loading",
                    kind="info",
                    loading=True,
                    auto_close=False,
                )
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page_1])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
