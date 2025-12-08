import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va
from vizro import Vizro

df = px.data.iris()

page_1 = vm.Page(
    title="Test dmc notification system",
    layout=vm.Flex(),
    components=[
        vm.Button(
            icon="check_circle",
            text="Success Notification",
            actions=[
                va.show_notification(
                    text="Operation completed successfully!",
                    variant="success",
                )
            ],
        ),
        vm.Button(
            icon="warning",
            text="Warning Notification",
            actions=[
                va.show_notification(
                    text="Please review this warning message.",
                    variant="warning",
                )
            ],
        ),
        vm.Button(
            text="Error Notification",
            icon="error",
            actions=[
                va.show_notification(
                    text="An error occurred during the operation.",
                    variant="error",
                )
            ],
        ),
        vm.Button(
            text="Info Notification",
            icon="info",
            actions=[
                va.show_notification(
                    text="Here's some useful information for you.",
                    variant="info",
                )
            ],
        ),
        vm.Button(
            text="Loading Notification",
            icon="hourglass_empty",
            actions=[
                va.show_notification(
                    text="Processing your request...",
                    variant="progress",
                )
            ],
        ),
        vm.Button(
            text="No Auto-Close",
            icon="close",
            actions=[
                va.show_notification(
                    text="This notification will stay until you close it manually.",
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
                    text="A simple notification with default title and variant.",
                    variant="info",
                )
            ],
        ),
        vm.Button(
            text="Custom Icon",
            icon="celebration",
            actions=[
                va.show_notification(
                    text="Check out this new feature!",
                    title="New Feature",
                    variant="success",
                    icon="celebration",
                )
            ],
        ),
        vm.Button(
            text="Markdown with Link",
            icon="link",
            actions=[
                va.show_notification(
                    text="Visit the [Vizro documentation](https://vizro.readthedocs.io/en/stable/) for more details!",
                    title="Learn More",
                    auto_close=False,
                )
            ],
        ),
        vm.Button(
            text="1. Show Loading",
            icon="hourglass_empty",
            actions=[
                va.show_notification(
                    id="update-demo",
                    text="Processing your request...",
                    title="Processing",
                    variant="progress",
                )
            ],
        ),
        vm.Button(
            text="2. Update to Complete",
            icon="done",
            actions=[
                va.update_notification(
                    notification="update-demo",
                    text="Your request has been processed successfully!",
                    title="Complete",
                    variant="success",
                )
            ],
        ),
        vm.Button(
            text="Show Navigation Notification",
            icon="arrow_forward",
            actions=[
                va.show_notification(
                    text="Click [here](/page-two) to go to **Page 2** and explore more features!",
                    title="Ready to explore?",
                    variant="info",
                    auto_close=False,
                )
            ],
        ),
    ],
)


page_two = vm.Page(
    id="page-two",
    title="Page Two",
    controls=[vm.Filter(column="species")],
    components=[
        vm.Graph(figure=px.histogram(df, x="sepal_length")),
        vm.Button(
            icon="check_circle",
            text="Success Notification",
            actions=[
                va.show_notification(
                    text="Operation completed successfully!",
                    variant="success",
                )
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page_1, page_two])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
