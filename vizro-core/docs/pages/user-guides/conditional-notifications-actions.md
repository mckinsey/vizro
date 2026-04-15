# How to use conditional notifications

This guide shows you how to use **conditional notifications** that show automatically based on a [custom action's](custom-actions.md) outcome. Instead of manually calling [`show_notification`][vizro.actions.show_notification] or [`update_notification`][vizro.actions.update_notification], you define a `notifications` argument as a dictionary in the [`vm.Action`][vizro.models.Action] upfront, and Vizro dispatches the right notification for you.

This section explains how to handle **success** and **error** outcomes of custom actions, show **progress** indicators while actions run, define custom notification keys for more specific scenarios, and template notification text with runtime values.

## Conditional notifications for custom actions

This section covers actions defined with `@capture("action")`. If you are new to custom actions, see [How to create custom actions](custom-actions.md) first.

### Success and error notifications

The two most common built-in keys are `"success"` and `"error"`. If a `"success"` notification is defined, it shows when the action returns normally (without raising an exception), and if an `"error"` notification is defined, it shows when the action raises an exception.

!!! example "Success and error notifications"

    === "app.py"

        ```{.python hl_lines="8-12 24-27"}
        import random

        import vizro.models as vm
        from vizro import Vizro
        from vizro.models.types import capture


        @capture("action")
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

### Progress notifications

Defined `"progress"` notification shows **before** the action starts and is automatically replaced by the success or error notification once the action completes. This is useful for long-running operations where you want to show a loading indicator.

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
            sleep(random.uniform(1, 2))
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
                            "progress": "Running pipeline...",
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

### Custom notification keys

Beyond the three built-in keys (`progress`, `success`, `error`), you can add **custom keys** to `notifications`. These custom notifications are not shown automatically though, but they show only when the action function explicitly **returns** or **raises** with a matching key.

To select a custom notification on success, append the key after the return value:

```python
return result_text, "pipeline_partial_success"
```

To select a custom notification on error, pass the key as a second argument to the exception:

```python
raise Exception("Pipeline failed.", "pipeline_partial_error")
```

The key must match an entry in the defined `notifications` dictionary. If no key is returned from the action, the `"success"` notification shows on return (if defined), and the `"error"` notification shows on exception (if defined).

Custom keys default to `variant="info"` unless overridden with a `show_notification` object (see [Full notification customization](#full-notification-customization)).

!!! note

    You can explicitly return built-in keys like `"success"` or `"error"` from your action function, but this is rarely needed since they are handled by default.

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
                raise Exception("Random error.")
            if roll < 0.5:
                raise Exception("Random error.", "pipeline_partial_error")
            if roll < 0.75:
                return "Metrics updated"
            if roll <= 1:
                return "Metrics updated", "pipeline_partial_success"


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
                            "pipeline_partial_success": "Pipeline partially completed.",
                            "pipeline_partial_error": "Pipeline partially failed.",
                        },
                    ),
                ),
                vm.Text(id="pipeline_output", text="Click the button to run the pipeline."),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

### Templating notification text

Notification messages support **template variables** that are replaced with action's runtime values:

- **`{{result}}`**: template within the notification's text that's replaced with an extra value that's returned from the action's function as the second element of a tuple.

    - Example for return values: `return output, ("key", "detail text")`.
    - Example for exceptions: `raise Exception("error message", ("key", "detail text"))`.

    The second element of the tuples replace the `{{result}}` textual template. Resolves to an empty string if not provided.

- **`{{error_msg}}`**: template within the notification's text that's replaced with the first argument of the exception. Resolves to an empty string if not provided.

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
                raise Exception("Random error.", ("error", duration_result))
            if roll < 0.5:
                raise Exception("Random error.", ("pipeline_partial_error", duration_result))
            if roll < 0.75:
                return "Metrics updated", ("success", duration_result)
            if roll <= 1:
                return "Metrics updated", ("pipeline_partial_success", duration_result)


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
                            "success": "Pipeline done. {{result}}",
                            "error": "Pipeline failed: {{error_msg}} \n {{result}}",
                            "pipeline_partial_success": "Pipeline partially completed. {{result}}",
                            "pipeline_partial_error": "Pipeline partially failed: {{error_msg}} \n {{result}}",
                        },
                    ),
                ),
                vm.Text(id="pipeline_output", text="Click the button to run the pipeline."),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

The `{{result}}` template is populated from the **second** element of the tuple passed alongside a return value or exception. It's `duration_result"` in the example above.

The `{{error_msg}}` template is populated from the **first** argument of the exception. It's `"Random error."` in the example above.

### Templating progress text with action inputs

Progress notification text can also be templated with **action runtime input arguments** referenced by their parameter names `{{param_name}}`.

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
        def run_pipeline(max_retries: int = 1):
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
                            "progress": "Running pipeline... (max retries: {{max_retries}})...",
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

### Full notification customization

Instead of plain text, a notification dictionary value can be a [`show_notification`][vizro.actions.show_notification] or [`update_notification`][vizro.actions.update_notification] model, giving full control over `variant`, `title`, `icon`, `auto_close` and more. See the [notifications guide](notification-actions.md) for all available parameters. Template variables like `{{result}}` still work inside the `text` argument. This might be useful when you want to change the default `variant="info"` for custom keys.

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
                            "progress": va.show_notification(id="progress_id", variant="progress", text="Running pipeline... (max retries: {{max_retries}})..."),
                            "success": "Pipeline done. {{result}}",
                            "error": "Pipeline failed: {{error_msg}} - {{result}}",
                            "pipeline_partial_success": va.update_notification(variant="success", notification="progress_id", text="Pipeline partially completed. {{result}}"),
                            "pipeline_partial_error": va.update_notification(variant="error", notification="progress_id", text="Pipeline partially failed: {{error_msg}} - {{result}}"),
                            "pipeline_max_retries_error": va.update_notification(variant="error", notification="progress_id", text="Pipeline failed after {{result}} retries."),
                        },
                    ),
                ),
                vm.Text(id="pipeline_output", text="Click the button to run the pipeline."),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

### Debugging and error handling

Every custom action has a default `notifications={"error": "Action failed."}`. You can override this with a more specific message or set it to `None` to disable it entirely.

When the error notification is disabled (`notifications={"error": None}`) and the app runs in debug mode (`Vizro().build(dashboard).run(debug=True)`), unhandled exceptions are forwarded to the [Dash Dev Tools](https://dash.plotly.com/devtools) debugger. When an `"error"` notification **is** defined, the exception is caught and shown as an in-app notification instead.

All exceptions (except `PreventUpdate`) are always logged to the server console, regardless of notification configuration.

!!! example "Default error vs disabled error"

    === "app.py"

        ```{.python hl_lines="29 36"}
        from time import sleep

        import vizro.models as vm
        from vizro import Vizro
        from vizro.models.types import capture


        @capture("action")
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
                        function=run_pipeline_always_fails(),
                    ),
                ),
                vm.Button(
                    text="Run pipeline (no error notification)",
                    actions=vm.Action(
                        function=run_pipeline_always_fails(),
                        notifications={"error": None},
                    ),
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run(debug=True)
        ```

Other important behaviors:

- **`PreventUpdate`**: raising `PreventUpdate` is treated as a success (shows the `"success"` notification if defined) but **stops** the action chain from continuing to execute.
- **`dash.no_update`**: returning `no_update` is also treated as success and **allows** the action chain to continue.

## Conditional notifications for built-in actions

Conditional notifications for Vizro's built-in actions (such as [`export_data`][vizro.actions.export_data]) are not yet supported. This will be added in a future release.
