# How to use actions to show notifications

This guide shows you how to display notifications/alerts in your dashboard to provide feedback to users about their actions or the state of the application.

## Show notification

The [`show_notification`][vizro.actions.show_notification] action displays a temporary message to the user. Notifications are useful for:

- Confirming that an action completed successfully
- Alerting users to warnings or errors
- Providing informational messages
- Showing loading states during long-running operations

Notifications appear at the top-right of the screen and are customizable with options for styling (variants and icons), timing (auto-close duration), behavior (loading states and updates), and more.

!!! note "Under the hood"

    Vizro uses the [dmc.NotificationContainer](https://www.dash-mantine-components.com/components/notifications) to display notifications. The `show_notification` action sends a configuration to this container, which handles rendering and managing the notifications.

### Basic usage

To display a notification, call [`show_notification`][vizro.actions.show_notification] in the `actions` argument of any component that supports actions. Most Vizro components such as [buttons](button.md), [graphs](graph.md), and [cards](card.md) have an `actions` argument that can trigger notifications.

!!! example "Basic notification"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.actions as va
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        df = px.data.iris()

        page = vm.Page(
            title="Basic notification",
            components=[
                vm.Button(
                    text="Show notification",
                    actions=[va.show_notification(message="This is a default notification!")],
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"

        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - type: button
                text: Show notification
                actions:
                  - type: show_notification
                    message: This is a default notification!
            title: Basic notification
        ```

    === "Result"

        [![BasicNotification]][basicnotification]

When you click the button, a notification appears on the top right. Since only the `message` is provided, the notification uses the default `variant="info"` styling with a blue color scheme and an info icon.

### Notification variants

The `variant` argument controls the visual style and semantic meaning of the notification. Five variants are available:

- `"info"` (default): For general informational messages
- `"success"`: For successful operations
- `"warning"`: For warnings or cautionary messages
- `"error"`: For errors or critical issues
- `"progress"`: For loading states - displays a spinner instead of an icon. Useful for indicating long-running operations. It's recommended to also set `auto_close=False` so the notification remains visible until the operation completes.

Each variant has its own color scheme and default icon (except `"progress"` which shows a loading spinner).

!!! example "Notification variants"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.actions as va
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Notification variants",
            layout=vm.Flex(direction="row"),
            components=[
                vm.Button(
                    text="Info",
                    actions=[va.show_notification(message="This is an info message", variant="info")],
                ),
                vm.Button(
                    text="Success",
                    actions=[va.show_notification(message="Operation completed!", variant="success")],
                ),
                vm.Button(
                    text="Warning",
                    actions=[va.show_notification(message="Please review your inputs", variant="warning")],
                ),
                vm.Button(
                    text="Error",
                    actions=[va.show_notification(message="Something went wrong", variant="error")],
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"

        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - type: button
                text: Info
                actions:
                  - type: show_notification
                    message: This is an info message
                    variant: info
              - type: button
                text: Success
                actions:
                  - type: show_notification
                    message: Operation completed!
                    variant: success
              - type: button
                text: Warning
                actions:
                  - type: show_notification
                    message: Please review your inputs
                    variant: warning
              - type: button
                text: Error
                actions:
                  - type: show_notification
                    message: Something went wrong
                    variant: error
            title: Notification variants
            layout:
              type: flex
              direction: row
        ```

    === "Result"

        [![NotificationVariants]][notificationvariants]

### Custom title and icon

By default, notifications use the capitalized variant name as the title (e.g., "Info", "Success", "Warning", "Error"). You can customize both the title and icon. The `icon` argument accepts any icon name from the [Google Material Icons library](https://fonts.google.com/icons):

!!! example "Custom title and icon"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.actions as va
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Custom notification",
            components=[
                vm.Button(
                    text="Download data",
                    actions=[
                        va.show_notification(
                            title="Download Complete",
                            message="Your data has been exported successfully",
                            variant="success",
                            icon="download",
                        )
                    ],
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"

        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - type: button
                text: Download data
                actions:
                  - type: show_notification
                    title: Download Complete
                    message: Your data has been exported successfully
                    variant: success
                    icon: download
            title: Custom notification
        ```

    === "Result"

        [![CustomNotification]][customnotification]

### Auto-close duration

By default, notifications auto-dismiss after 4 seconds (4000 milliseconds). You can customize this duration or disable auto-close entirely. Set `auto_close=False` for important messages that require user acknowledgment.

!!! example "Auto-close settings"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.actions as va
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Auto-close settings",
            layout=vm.Flex(direction="row"),
            components=[
                vm.Button(
                    text="Quick message (2s)",
                    actions=[
                        va.show_notification(
                            message="This will disappear quickly",
                            auto_close=2000,
                        )
                    ],
                ),
                vm.Button(
                    text="Long message (10s)",
                    actions=[
                        va.show_notification(
                            message="This message stays longer to ensure you see it",
                            auto_close=10000,
                        )
                    ],
                ),
                vm.Button(
                    text="Manual close",
                    actions=[
                        va.show_notification(
                            message="Click the X to close this notification",
                            auto_close=False,
                        )
                    ],
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"

        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - type: button
                text: Quick message (2s)
                actions:
                  - type: show_notification
                    message: This will disappear quickly
                    auto_close: 2000
              - type: button
                text: Long message (10s)
                actions:
                  - type: show_notification
                    message: This message stays longer to ensure you see it
                    auto_close: 10000
              - type: button
                text: Manual close
                actions:
                  - type: show_notification
                    message: Click the X to close this notification
                    auto_close: false
            title: Auto-close settings
            layout:
              type: flex
              direction: row
        ```

    === "Result"

        [![AutoCloseNotification]][autoclosenotification]

### Combine with other actions

Notifications can be combined with other actions to provide user feedback. For example, you can display a success notification after [exporting data](data-actions.md#export-data) to confirm the action completed.

!!! example "Notification with export"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.actions as va
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        df = px.data.iris()

        page = vm.Page(
            title="Export with notification",
            layout=vm.Flex(),
            components=[
                vm.Graph(figure=px.histogram(df, x="sepal_length")),
                vm.Button(
                    text="Export data",
                    actions=[
                        va.export_data(),
                        va.show_notification(
                            message="Data exported successfully!",
                            variant="success",
                            icon="download",
                        ),
                    ],
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"

        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - type: graph
                figure:
                  _target_: histogram
                  x: sepal_length
              - type: button
                text: Export data
                actions:
                  - type: export_data
                  - type: show_notification
                    message: Data exported successfully!
                    variant: success
                    icon: download
            title: Export with notification
            layout:
              type: flex
        ```

    === "Result"

        [![ExportNotification]][exportnotification]

### Update existing notification

You can update an existing notification by using `action="update"` and providing a matching `notification_id`. This is useful for showing progress updates or state changes for the same logical operation without creating multiple notifications.

!!! example "Update notification"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.actions as va
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Update notification example",
            layout=vm.Flex(direction="row"),
            components=[
                vm.Button(
                    text="Start process",
                    actions=[
                        va.show_notification(
                            notification_id="process_status",
                            message="Processing started...",
                            variant="progress",
                            auto_close=False,
                        )
                    ],
                ),
                vm.Button(
                    text="Complete process",
                    actions=[
                        va.show_notification(
                            notification_id="process_status",
                            action="update",
                            title="Complete",
                            message="Processing finished successfully!",
                            variant="success",
                        )
                    ],
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"

        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - type: button
                text: Start process
                actions:
                  - type: show_notification
                    notification_id: process_status
                    message: Processing started...
                    variant: progress
                    auto_close: false
              - type: button
                text: Complete process
                actions:
                  - type: show_notification
                    notification_id: process_status
                    action: update
                    title: Complete
                    message: Processing finished successfully!
                    variant: success
            title: Update notification example
            layout:
              type: flex
              direction: row
        ```

    === "Result"

        [![UpdateNotification]][updatenotification]

[autoclosenotification]: ../../assets/user_guides/notification_actions/auto_close_notification.gif
[basicnotification]: ../../assets/user_guides/notification_actions/basic_notification.gif
[customnotification]: ../../assets/user_guides/notification_actions/custom_notification.png
[exportnotification]: ../../assets/user_guides/notification_actions/export_notification.gif
[notificationvariants]: ../../assets/user_guides/notification_actions/notification_variants.gif
[updatenotification]: ../../assets/user_guides/notification_actions/update_notification.gif
