# How to use buttons

This guide shows you how to use buttons to interact with your data in the dashboard.

The Button component is commonly used for interactive dashboard interactions such as form submissions, navigation links, and other action triggers. It is based on the underlying Dash component [`dbc.Button`](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/button/).

To add a [`Button`][vizro.models.Button], insert it into the `components` argument of the [`Page`][vizro.models.Page].

## Customize button text

You can configure the `text` argument to alter the display text of the [`Button`][vizro.models.Button].

!!! example "Customize text"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Button with text",
            components=[vm.Button(text="I'm a button!")],
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
                text: I'm a button!
            title: Button with text
        ```

    === "Result"

        [![ButtonText]][buttontext]

## Create a link button

To navigate to a different page using a button with an anchor tag, assign an absolute or relative URL to the `Button.href`.

```python
import vizro.models as vm

vm.Button(text="Leave us a star! ⭐", href="https://github.com/mckinsey/vizro")
```

## Attach an action

You can use the [`Button`][vizro.models.Button] to trigger an action function, such as exporting data. To explore the available options for [`Actions`][vizro.models.Action], refer to our [API reference][vizro.actions]. Use the `Button.actions` argument to specify which action function executes when the button is clicked.

The example below demonstrates how to configure a button to export the filtered data of a target chart using the [export_data][vizro.actions.export_data] action function.

!!! example "Button with action"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.actions import export_data

        df = px.data.iris()

        page = vm.Page(
            title="My first page",
            layout=vm.Flex(),  # (1)!
            components=[
                vm.Graph(
                    figure=px.scatter(
                        df,
                        x="sepal_width",
                        y="sepal_length",
                        color="species",
                        size="petal_length",
                    ),
                ),
                vm.Button(
                    text="Export data",
                    actions=[vm.Action(function=export_data())],
                ),
            ]
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. We use a [`Flex`][vizro.models.Flex] layout to make sure the `Graph` and `Button` only occupy as much space as they need, rather than being distributed evenly.

    === "app.yaml"

        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - figure:
                  _target_: scatter
                  x: sepal_width
                  y: sepal_length
                  color: species
                  size: petal_length
                  data_frame: iris
                type: graph
              - type: button
                text: Export data
                id: export_data
                actions:
                  - function:
                      _target_: export_data
            layout:
              type: flex
            title: My first page
        ```

    === "Result"

        [![Button]][button]

## Use as a control

The [`Button`][vizro.models.Button] component is currently reserved to be used inside the main panel (right-side) of the dashboard. However, there might be use cases where one would like to place the `Button` inside the control panel (left-side) with the other controls.

In this case, follow the user-guide outlined for [creating custom components](custom-components.md) and manually add the `Button` as a valid type to the `controls` argument by running the following lines before your dashboard configurations:

```python
from vizro import Vizro
import vizro.models as vm

vm.Page.add_type("controls", vm.Button)

# Add dashboard configurations below
...
```

## Styled buttons

There are three predefined button styles that can be customized using the `variant` argument. If no `variant` is specified, the default style applied is `variant="filled"`.

!!! example "Button with different styles"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Buttons with different styles",
            layout=vm.Flex(direction="row"),  # (1)!
            components=[
                vm.Button(text="filled"),
                vm.Button(text="outlined", variant="outlined"),
                vm.Button(text="plain", variant="plain"),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. We use a [`Flex`][vizro.models.Flex] layout with `direction="row"` to ensure the `Button` components are placed side by side and only take up as much space as needed.

    === "app.yaml"

        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - title: Buttons with different styles
            layout:
              direction: row
              type: flex
            components:
              - type: button
                text: filled
              - type: button
                text: outlined
                variant: outlined
              - type: button
                text: plain
                variant: plain

        ```

    === "Result"

        [![ButtonVariant]][buttonvariant]

## The `extra` argument

The `Button` is based on the underlying Dash component [`dbc.Button`](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/button/). Using the `extra` argument you can pass more arguments to `dbc.Button` in order to alter it beyond the chosen defaults.

!!! warning

    Using `extra` is a quick and flexible way to alter a component beyond what Vizro offers. However, [it is not a part of the official Vizro schema](../explanation/schema.md#what-is-the-vizro-json-schema) and the underlying implementation details may change. If you want to guarantee that your apps keep running, we recommend that you pin your Vizro version.

An example use would be to create an outlined success button. For this, you can use `extra={"color": "success", "outline": True}`. This would be a shortcut to using custom CSS in the assets folder as explained in [our guide on CSS](../user-guides/custom-css.md).

!!! example "Button with custom style"

    === "app.py"

        ```{.python pycafe-link hl_lines="9"}
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Button with custom style",
            components=[
                vm.Button(
                    text="Success button",
                    extra={"color": "success", "outline": True},
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"

        ```{.yaml hl_lines="6-8"}
        pages:
          - title: Button with custom style
            components:
              - type: button
                text: Success button
                extra:
                  color: success
                  outline: true
        ```

    === "Result"

        [![ButtonExtra]][buttonextra]

[button]: ../../assets/user_guides/components/button.png
[buttonextra]: ../../assets/user_guides/components/button_style_extra.png
[buttontext]: ../../assets/user_guides/components/button_text.png
[buttonvariant]: ../../assets/user_guides/components/button_style_variants.png
