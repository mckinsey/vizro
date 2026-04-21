# How to use conditional notifications

Conditional notifications are messages that are displayed automatically based on the outcome of an action. For example, a notification can indicate whether an action was completed successfully or failed.

The following sections cover how conditional notifications can represent different outcomes, such as success and error states, display progress indicators while actions are running, and support more specific scenarios and dynamic content.

## Conditional notifications for custom actions

This section focuses on conditional notifications used with actions defined via `@capture("action")`. If you're not familiar with custom actions, see [How to create custom actions](custom-actions.md) first.

### Success and error notifications

Two common types of conditional notifications are **"success"** and **"error"**. A **"success"** notification is shown when an action completes as expected. An **"error"** notification is shown automatically if the action raises an exception, indicating that something went wrong during execution.

!!! example "Success and error notifications"

    === "app.py"

        ```{.python hl_lines="8-12 24-27"}
        import random

        import vizro.models as vm
        from vizro import Vizro
        from vizro.models.types import capture


        @capture("action")  # (1)!
        def run_pipeline():
            if random.random() < 0.5:
                raise Exception("Random error.")
            return "Metrics updated"


        page = vm.Page(
            title="Success and error notifications",
            layout=vm.Flex(),
            components=[
                vm.Button(
                    text="Run pipeline",
                    actions=vm.Action(
                        function=run_pipeline(),
                        outputs="pipeline_output",
                        notifications={
                            "success": "Pipeline completed.",  # (2)!
                            "error": "Pipeline failed.",  # (3)!
                        },
                    ),
                ),
                vm.Text(id="pipeline_output", text="Click the button to run the pipeline."),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. Define a custom action function `run_pipeline` that randomly either returns a success message or raises an exception to simulate an error.
        1. A `success` notification with the "Pipeline completed." text is shown when the action returns successfully.
        1. An `error` notification with the "Pipeline failed." text is shown when the action raises an exception.


### Progress notifications

A `"progress"` notification is shown while an action is running. It appears before the action starts and is automatically replaced by a `"success"` or `"error"` notification once the action completes.

This is useful for long-running actions where you want to indicate that work is in progress and provide feedback to the user.

!!! example "Progress notification"

    === "app.py"

        ```{.python hl_lines="11 27"}
        import random
        from time import sleep

        import vizro.models as vm
        from vizro import Vizro
        from vizro.models.types import capture


        @capture("action")
        def run_pipeline():
            sleep(random.uniform(1, 2))  # (1)!
            if random.random() < 0.5:
                raise Exception("Random error.")
            return "Metrics updated"


        page = vm.Page(
            title="Progress notification",
            layout=vm.Flex(),
            components=[
                vm.Button(
                    text="Run pipeline",
                    actions=vm.Action(
                        function=run_pipeline(),
                        outputs="pipeline_output",
                        notifications={
                            "progress": "Running pipeline...",  # (2)!
                            "success": "Pipeline completed.",
                            "error": "Pipeline failed.",
                        },
                    ),
                ),
                vm.Text(id="pipeline_output", text="Click the button to run the pipeline."),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. Add a `sleep` call in the action function to simulate a long-running operation.
        1. A `"progress"` notification with the "Running pipeline..." text is shown immediately when the action starts, and then replaced by either the `"success"` or `"error"` notification once the action completes.


### Custom notification keys

In addition to the built-in keys (`progress`, `success`, `error`), you can define your own custom notification keys. These allow you to handle more specific outcomes beyond just `success` or `error`.

Custom notifications are only shown when the action explicitly selects them. This happens when the action function either returns a key or raises an exception with a key that matches one defined in notifications.

To show a custom notification on success, return the key alongside the result:

```python
return result_text, "pipeline_partial_success"
```

To show a custom notification on error, include the key when raising an exception:

```python
raise Exception("Pipeline failed.", "pipeline_partial_error")
```

If no custom key is provided, the default behavior applies: a "success" notification is shown when the action completes, and an "error" notification is shown if an exception is raised (if these are defined).

Custom notifications use the "info" style by default, unless configured otherwise (see our user guide on [customizing notifications](#customizing-notification-appearance-and-behavior)).

!!! example "Custom notification keys"

    === "app.py"

        ```{.python hl_lines="17 21 37-38"}
        import random
        from time import sleep

        import vizro.models as vm
        from vizro import Vizro
        from vizro.models.types import capture


        @capture("action")
        def run_pipeline():
            sleep(random.uniform(1, 2))

            roll = random.random()
            if roll < 0.25:
                raise Exception("Random error.")  # (1)!
            if roll < 0.5:
                raise Exception("Random error.", "pipeline_partial_error")  # (2)!
            if roll < 0.75:
                return "Metrics updated"  # (3)!
            if roll <= 1:
                return "Metrics updated", "pipeline_partial_success"  # (4)!


        page = vm.Page(
            title="Custom notification keys",
            layout=vm.Flex(),
            components=[
                vm.Button(
                    text="Run pipeline",
                    actions=vm.Action(
                        function=run_pipeline(),
                        outputs="pipeline_output",
                        notifications={
                            "progress": "Running pipeline...",
                            "success": "Pipeline completed.",
                            "error": "Pipeline failed.",
                            "pipeline_partial_success": "Pipeline partially completed.",  # (5)!
                            "pipeline_partial_error": "Pipeline partially failed.",  # (6)!
                        },
                    ),
                ),
                vm.Text(id="pipeline_output", text="Click the button to run the pipeline."),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. Default `"error"` key is raised to show the "Pipeline failed." notification.
        1. Custom `"pipeline_partial_error"` key is raised to show the "Pipeline partially failed." notification.
        1. Default `"success"` key is returned to show the "Pipeline completed." notification.
        1. Custom `"pipeline_partial_success"` key is returned to show the "Pipeline partially completed." notification.
        1. Definition of the custom notification for the `"pipeline_partial_success"` key.
        1. Definition of the custom notification for the `"pipeline_partial_error"` key.


### Dynamic notification content

Notification messages can include **template variables** that are filled in with values from the action at runtime. This allows you to display dynamic information, such as results or error details, directly in the notification.

Two templates are supported:
  - `**{{result}}**`: Replaced with additional information returned by the action. This value is optional and can be included in the tuple alongside the notification key when the action completes or raises an exception. If no value is provided, it resolves to an empty string.
  - `**{{error_msg}}**`: Replaced with the error message from an exception. If no error message is available, it resolves to an empty string.

These templates make it possible to provide more informative and contextual feedback to users without hardcoding the message content.

!!! example "Templating with `{{result}}` and `{{error_msg}}`"

    === "app.py"

        ```{.python hl_lines="17 19 21 23 37-40"}
        import random
        from time import sleep

        import vizro.models as vm
        from vizro import Vizro
        from vizro.models.types import capture


        @capture("action")
        def run_pipeline():
            duration = random.uniform(1, 2)
            duration_result = f"Duration: {duration:.1f}s"
            sleep(duration)

            roll = random.random()
            if roll < 0.25:
                raise Exception("Random error.", ("error", duration_result))  # (1)!
            if roll < 0.5:
                raise Exception("Random error.", ("pipeline_partial_error", duration_result))  # (2)!
            if roll < 0.75:
                return "Metrics updated", ("success", duration_result)  # (3)!
            if roll <= 1:
                return "Metrics updated", ("pipeline_partial_success", duration_result)  # (4)!


        page = vm.Page(
            title="Templated notifications",
            layout=vm.Flex(),
            components=[
                vm.Button(
                    text="Run pipeline",
                    actions=vm.Action(
                        function=run_pipeline(),
                        outputs="pipeline_output",
                        notifications={
                            "progress": "Running pipeline...",
                            "success": "Pipeline done. {{result}}",  # (5)!
                            "error": "Pipeline failed: {{error_msg}} \n {{result}}",  # (6)!
                            "pipeline_partial_success": "Pipeline partially completed. {{result}}",  # (7)!
                            "pipeline_partial_error": "Pipeline partially failed: {{error_msg}} \n {{result}}",  # (8)!
                        },
                    ),
                ),
                vm.Text(id="pipeline_output", text="Click the button to run the pipeline."),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. Propagating dynamic value `duration_result` to the `"error"` notification text that replaces the `{{results}}` template.
        1. Propagating dynamic value `duration_result` to the `"pipeline_partial_error"` notification text that replaces the `{{results}}` template.
        1. Propagating dynamic value `duration_result` to the `"success"` notification text that replaces the `{{results}}` template.
        1. Propagating dynamic value `duration_result` to the `"pipeline_partial_success"` notification text that replaces the `{{results}}` template.
        1. Defining the `"success"` notification text with the `{{result}}` template.
        1. Defining the `"error"` notification text with both `{{error_msg}}` and `{{result}}` templates.
        1. Defining the `"pipeline_partial_success"` notification text with the `{{result}}` template.
        1. Defining the `"pipeline_partial_error"` notification text with both `{{error_msg}}` and `{{result}}` templates.


In this example, `**{{result}}**` is filled with the additional detail returned by the action (for example, the duration of the pipeline run).

The `**{{error_msg}}**` template is filled with the error message from the exception (for example, "Random error.").

### Using action inputs in progress notifications

Progress notifications can also include template variables based on the runtime action's input values. These variables are referenced using the parameter names, for example `{{param_name}}`.

This allows the progress message to reflect the current inputs of the action, making it more informative. For example, you can display the number of retries configured while the action is running.

!!! example "Dynamic progress text"

    === "app.py"

        ```{.python hl_lines="12 35 39 42"}
        import random
        from time import sleep

        import vizro.models as vm
        from vizro import Vizro
        from vizro.models.types import capture

        vm.Page.add_type("components", vm.Slider)


        @capture("action")
        def run_pipeline(max_retries: int = 1):  # (1)!
            for _ in range(max_retries + 1):
                duration = random.uniform(1, 2)
                duration_result = f"Duration: {duration:.1f}s"
                sleep(duration)

                roll = random.uniform(0, 2)
                if roll < 0.25:
                    raise Exception("Random error.", ("error", duration_result))
                if roll < 0.5:
                    raise Exception("Random error.", ("pipeline_partial_error", duration_result))
                if roll < 0.75:
                    return "Metrics updated", ("success", duration_result)
                if roll <= 1:
                    return "Metrics updated", ("pipeline_partial_success", duration_result)

            raise Exception("Random error.", ("pipeline_max_retries_error", max_retries))


        page = vm.Page(
            title="Templated notifications",
            layout=vm.Flex(),
            components=[
                vm.Slider(id="slider_id", min=1, max=3, step=1, value=1, title="Max retries"),
                vm.Button(
                    text="Run pipeline",
                    actions=vm.Action(
                        function=run_pipeline(max_retries="slider_id"),
                        outputs="pipeline_output",
                        notifications={
                            "progress": "Running pipeline... (max retries: {{max_retries}})...",  # (2)!
                            "success": "Pipeline done. {{result}}",
                            "error": "Pipeline failed: {{error_msg}} - {{result}}",
                            "pipeline_partial_success": "Pipeline partially completed. {{result}}",
                            "pipeline_partial_error": "Pipeline partially failed: {{error_msg}} - {{result}}",
                            "pipeline_max_retries_error": "Pipeline failed after {{result}} retries.",
                        },
                    ),
                ),
                vm.Text(id="pipeline_output", text="Click the button to run the pipeline."),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. Action's input argument `max_retries` which dynamic value shows in the `"progress"` notification text.
        1. Defining the `"progress"` notification text with the `{{max_retries}}` template that gets replaced by the runtime value of the `max_retries` argument when the action runs.


### Customizing notification appearance and behavior

Notifications don't have to be limited to plain text. You can customize how they look and behave, for example, by adjusting the variant, adding a title or icon, or controlling whether they close automatically. See the [notifications guide](notification-actions.md) for a full list of available options.

To do this, use the [show_notification][vizro.actions.show_notification] or [update_notification][vizro.actions.update_notification] models instead of plain text when defining notifications. This allows notifications to be tailored to different scenarios, such as highlighting important errors or distinguishing partial successes from full successes. Template variables like `{{result}}` can still be used within customized notification text.

!!! example "Customized notification with `show_notification`"

    === "app.py"

        ```{.python hl_lines="43 46-48"}
        import random
        from time import sleep

        import vizro.actions as va
        import vizro.models as vm
        from vizro import Vizro
        from vizro.models.types import capture

        vm.Page.add_type("components", vm.Slider)


        @capture("action")
        def run_pipeline(max_retries: int = 1):
            for _ in range(max_retries + 1):
                duration = random.uniform(1, 2)
                duration_result = f"Duration: {duration:.1f}s"
                sleep(duration)

                roll = random.uniform(0, 5)
                if roll < 0.25:
                    raise Exception("Random error.", ("error", duration_result))
                if roll < 0.5:
                    raise Exception("Random error.", ("pipeline_partial_error", duration_result))
                if roll < 0.75:
                    return "Metrics updated", ("success", duration_result)
                if roll <= 1:
                    return "Metrics updated", ("pipeline_partial_success", duration_result)

            raise Exception("Random error.", ("pipeline_max_retries_error", max_retries))


        page = vm.Page(
            title="Templated notifications",
            layout=vm.Flex(),
            components=[
                vm.Slider(id="slider_id", min=1, max=3, step=1, value=1, title="Max retries"),
                vm.Button(
                    text="Run pipeline",
                    actions=vm.Action(
                        function=run_pipeline(max_retries="slider_id"),
                        outputs="pipeline_output",
                        notifications={
                            "progress": va.show_notification(id="progress_id", variant="progress", text="Running pipeline... (max retries: {{max_retries}})..."),  # (1)!
                            "success": "Pipeline done. {{result}}",
                            "error": "Pipeline failed: {{error_msg}} - {{result}}",
                            "pipeline_partial_success": va.update_notification(variant="success", notification="progress_id", text="Pipeline partially completed. {{result}}"),   # (2)!
                            "pipeline_partial_error": va.update_notification(variant="error", notification="progress_id", text="Pipeline partially failed: {{error_msg}} - {{result}}"),  # (3)!
                            "pipeline_max_retries_error": va.update_notification(variant="error", notification="progress_id", text="Pipeline failed after {{result}} retries."),  # (4)!
                        },
                    ),
                ),
                vm.Text(id="pipeline_output", text="Click the button to run the pipeline."),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. Using `va.show_notification` to define the `"progress"` notification with an `id` that can be referenced by other notifications.
        1. Using `va.update_notification` to update the `"progress"` notification with new text and variant when the `"pipeline_partial_success"` key is returned.
        1. Using `va.update_notification` to update the `"progress"` notification with new text and variant when the `"pipeline_partial_error"` key is raised.
        1. Using `va.update_notification` to update the `"progress"` notification with new text and variant when the `"pipeline_max_retries_error"` key is raised.


### Debugging and error handling

By default, every custom action shows a generic error notification ("Action failed.") if something goes wrong. You can override this with a more specific message, or disable error notifications entirely by setting `"error": None`.

If error notifications are disabled and the app is running in debug mode `(Vizro().build(dashboard).run(debug=True))`, any unhandled exceptions are shown in the [Dash Dev Tools](https://dash.plotly.com/devtools) debugger instead of in the app. If an "error" notification is defined, the exception is caught and displayed as a notification within the app.

All exceptions (except `PreventUpdate`) are always logged to the server console, regardless of how notifications are configured.

!!! example "Default error vs disabled error"

    === "app.py"

        ```{.python hl_lines="29 36"}
        from time import sleep

        import vizro.models as vm
        from vizro import Vizro
        from vizro.models.types import capture


        @capture("action")  # (1)!
        def run_pipeline_always_fails():
            sleep(1)
            raise Exception("Pipeline failed.")


        page = vm.Page(
            title="Error handling",
            layout=vm.Flex(),
            layout=vm.Flex(direction="row"),
            components=[
                vm.Button(
                    text="Run pipeline (default error)",
                    actions=vm.Action(
                        function=run_pipeline_always_fails(),  # (2)!
                    ),
                ),
                vm.Button(
                    text="Run pipeline (no error notification)",
                    actions=vm.Action(
                        function=run_pipeline_always_fails(),
                        notifications={"error": None},  # (3)!
                    ),
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run(debug=True)  # (4)!
        ```

        1. Define a custom action function `run_pipeline` that raises an exception to simulate an error.
        1. There's a default `"Action failed."` error notification shown when the first button is clicked.
        1. There's no `"error"` notification shown when the second button is clicked, and the exception is forwarded to the Dash Dev Tools debugger instead since the app is running in debug mode.
        1. Running the app in debug mode to enable forwarding unhandled exceptions to the Dash Dev Tools debugger when `"error"` notifications are disabled.


Other important behaviors:

- **`PreventUpdate`**: raising `PreventUpdate` is treated as a success (shows the `"success"` notification if defined) but **stops** the action chain from continuing to execute.
- **`dash.no_update`**: returning `no_update` is also treated as success and **allows** the action chain to continue.

## Conditional notifications for built-in actions

Conditional notifications for Vizro's built-in actions (such as [`export_data`][vizro.actions.export_data]) are not yet supported. This will be added in a future release.
