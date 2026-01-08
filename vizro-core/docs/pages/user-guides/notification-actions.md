# How to use actions to show notifications

This guide shows you how to display notifications and alerts in your dashboard to provide feedback to users about their interactions with the UI.

## Show a notification

The [`show_notification`][vizro.actions.show_notification] action displays a temporary message to the user. Notifications are useful to:

- Confirm that an action completed successfully
- Alert users to warnings or errors
- Provide information messages
- Show loading states during long-running operations

Notifications appear at the top-right of the screen and are customizable with options for content (title and text) and styling (variants and icons).

!!! note "Under the hood"

    Vizro uses [`dmc.NotificationContainer`](https://www.dash-mantine-components.com/components/notifications) to display notifications. The `show_notification` action sends a configuration to this container, which handles rendering and managing the notifications.

### Basic usage

To display a notification, call [`show_notification`][vizro.actions.show_notification] in the `actions` argument of any component that supports actions. Most Vizro components such as [buttons](button.md), [graphs](graph.md), and [cards](card.md) have an `actions` argument that can trigger notifications.

!!! example "Basic notification"

    === "app.py"

        ```{.python pycafe-link hl_lines="13"}
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
                    actions=va.show_notification(text="This is a default notification!"),
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
                  type: show_notification
                  text: This is a default notification!
            title: Basic notification
        ```

    === "Result"

        [![BasicNotification]][basicnotification]

When you click the button, a notification appears in the top-right corner of the screen. Since only `text` is provided, the notification uses the default `variant="info"` styling with a blue color scheme and an info icon. The `text` field accepts [Markdown text](https://markdown-guide.readthedocs.io/).

### Notification variants

The `variant` argument controls the visual style and semantic meaning of the notification. Five variants are available as described in the [API docs of `show_notification`][vizro.actions.show_notification]:

- `"info"` (default): For general information messages
- `"success"`: For successful operations
- `"warning"`: For warnings or cautionary messages
- `"error"`: For errors or critical issues
- `"progress"`: For loading states - displays a spinner instead of an icon. Useful for indicating long-running operations. This variant automatically has `auto_close=False` so the notification remains visible until the operation completes.

### Custom title, text and icon

By default, notifications use the capitalized variant name as the title (e.g., "Info", "Success", "Warning", "Error"). You can customize the title, text and icon. The `icon` argument accepts any icon name from the [Google Material Icons library](https://fonts.google.com/icons):

!!! example "Custom content"

    === "app.py"

        ```{.python pycafe-link hl_lines="11-13"}
        import vizro.actions as va
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Custom notification",
            components=[
                vm.Button(
                    text="Download data",
                    actions=va.show_notification(
                        title="Download Complete",
                        text="Your data has been exported successfully",
                        icon="download",
                        variant="success",
                    ),
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
                  type: show_notification
                  title: Download Complete
                  text: Your data has been exported successfully
                  variant: success
                  icon: download
            title: Custom notification
        ```

    === "Result"

        [![CustomNotification]][customnotification]

### Auto-close duration

By default, notifications auto-dismiss after 4 seconds (4000 milliseconds). You can customize this duration or disable auto-close entirely.

!!! tip "When to disable auto-close"

    Use `auto_close=False` sparingly - only for critical situations where users must take action:

    - Errors requiring immediate attention
    - Security warnings or permission requests
    - Confirmations before irreversible operations

    For everything else (informational messages, success confirmations, general warnings), let notifications auto-dismiss. Manual dismissal disrupts workflow and can worsen the user experience when overused, so only use it when truly necessary. Ask yourself: **"Is this important enough to interrupt their task?"**

!!! example "Auto-close settings"

    === "app.py"

        ```{.python pycafe-link hl_lines="13 20 27"}
        import vizro.actions as va
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Auto-close settings",
            layout=vm.Flex(direction="row"),
            components=[
                vm.Button(
                    text="Quick message (2s)",
                    actions=va.show_notification(
                        text="This will disappear quickly",
                        auto_close=2000,
                    ),
                ),
                vm.Button(
                    text="Long message (10s)",
                    actions=va.show_notification(
                        text="This message stays longer to ensure you see it",
                        auto_close=10000,
                    ),
                ),
                vm.Button(
                    text="Manual close",
                    actions=va.show_notification(
                        text="Click the X to close this notification",
                        auto_close=False,
                    ),
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
                  type: show_notification
                  text: This will disappear quickly
                  auto_close: 2000
              - type: button
                text: Long message (10s)
                actions:
                  type: show_notification
                  text: This message stays longer to ensure you see it
                  auto_close: 10000
              - type: button
                text: Manual close
                actions:
                  type: show_notification
                  text: Click the X to close this notification
                  auto_close: false
            title: Auto-close settings
            layout:
              type: flex
              direction: row
        ```

    === "Result"

        [![AutoCloseNotification]][autoclosenotification]

### Chain with other actions

Notifications can be chained with other actions to provide user feedback. For example, you can display a success notification after [exporting data](data-actions.md#export-data) to confirm the action completed. [Actions in the `actions` list run sequentially](actions.md#multiple-actions), and the notification will display after the export action completes successfully.

!!! example "Notification with export"

    === "app.py"

        ```{.python pycafe-link hl_lines="15-22"}
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
                            text="Data exported successfully!",
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
                    text: Data exported successfully!
                    variant: success
                    icon: download
            title: Export with notification
            layout:
              type: flex
        ```

    === "Result"

        [![ExportNotification]][exportnotification]

## Update existing notification

You can update an existing notification with the [`update_notification`][vizro.actions.update_notification] action and providing a matching `notification` ID that references the original `show_notification` action. This is useful for showing progress updates or state changes for the same logical operation without creating multiple notifications.

!!! example "Update notification"

    === "app.py"

        ```{.python pycafe-link hl_lines="11-12 19-20"}
        import vizro.actions as va
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Update notification example",
            layout=vm.Flex(direction="row"),
            components=[
                vm.Button(
                    text="Start process",
                    actions=va.show_notification(  # (1)!
                        id="process_status",  # (2)!
                        text="Processing started...",
                        variant="progress",
                    ),
                ),
                vm.Button(
                    text="Complete process",
                    actions=va.update_notification(  # (3)!
                        notification="process_status",  # (4)!
                        title="Complete",
                        text="Processing finished successfully!",
                        variant="success",
                    ),
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. Use `show_notification` to display an initial notification
        1. Give the notification an explicit `id` so it can be targeted by `update_notification`
        1. Use `update_notification` to modify an existing notification
        1. Set `notification` to the `id` of the `show_notification` you want to update.

    === "app.yaml"

        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - type: button
                text: Start process
                actions:
                  type: show_notification
                  id: process_status
                  text: Processing started...
                  variant: progress
              - type: button
                text: Complete process
                actions:
                  type: update_notification
                  notification: process_status
                  title: Complete
                  text: Processing finished successfully!
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
[updatenotification]: ../../assets/user_guides/notification_actions/update_notification.gif
