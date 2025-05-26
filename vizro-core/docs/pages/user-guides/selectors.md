# How to use selectors

This guide highlights different selectors that can be used in a dashboard. Selectors do not serve a purpose on their own, but they enable you to change how the input is given to other models, for example, the [`Filter`][vizro.models.Filter] or the [`Parameter`][vizro.models.Parameter] model.

The [`Filter`][vizro.models.Filter] or the [`Parameter`][vizro.models.Parameter] model accept the `selector` argument, where a selector model can be entered to choose how the user should input their choices for the respective models.

## Categorical selectors

Within the categorical selectors, a clear distinction exists between multi-option and single-option selectors. For instance, the [`Checklist`][vizro.models.Checklist] functions as a multi-option selector by default while the [`RadioItem`][vizro.models.RadioItems] serves as a single-option selector by default. However, the [`Dropdown`][vizro.models.Dropdown] can function as both a multi-option or single-option selector.

For more information, refer to the API reference of the selector, or the documentation of its underlying Dash component:

- [`Dropdown`][vizro.models.Dropdown] based on [`dcc.Dropdown`](https://dash.plotly.com/dash-core-components/dropdown)
- [`Checklist`][vizro.models.Checklist] based on [`dcc.Checklist`](https://dash.plotly.com/dash-core-components/checklist)
- [`RadioItems`][vizro.models.RadioItems] based on [`dcc.RadioItems`](https://dash.plotly.com/dash-core-components/radioitems)

!!! note "Configuring `options`"

    When configuring the `options` of the categorical selectors, you can either give:

    - a list of values `options = ['Value A', 'Value B', 'Value C']`
    - or a dictionary of label-value mappings `options=[{'label': 'True', 'value': True}, {'label': 'False', 'value': False}]`

    The later is required if you want to provide different display labels to your option values or in case you want to provide boolean values as options. In this case, you need to provide a string label for your boolean values as boolean values cannot be displayed properly as labels in the underlying Dash components.

## Numerical selectors

For more information, refer to the API reference of the selector, or the documentation of its underlying Dash component:

- [`Slider`][vizro.models.Slider] based on [`dcc.Slider`](https://dash.plotly.com/dash-core-components/slider)
- [`RangeSlider`][vizro.models.RangeSlider] based on [`dcc.RangeSlider`](https://dash.plotly.com/dash-core-components/rangeslider)

!!! note "Using float values and `step` with an integer value"

    When configuring the [`Slider`][vizro.models.Slider] and the [`RangeSlider`][vizro.models.RangeSlider] with float values, and using `step` with an integer value, you may notice unexpected behavior, such as the drag value being outside its indicated marks. To our knowledge, this is a current bug in the underlying [`dcc.Slider`](https://dash.plotly.com/dash-core-components/slider) and [`dcc.RangeSlider`](https://dash.plotly.com/dash-core-components/rangeslider) component, which you can circumvent by adapting the `step` size as needed.

## Temporal selectors

For more information, refer to the API reference of the selector, or the documentation of its underlying Dash component:

- [`DatePicker`][vizro.models.DatePicker] based on [`dmc.DatePickerInput`](https://www.dash-mantine-components.com/components/datepickerinput)

!!! note

    When configuring the [`DatePicker`][vizro.models.DatePicker] make sure to provide your dates for `min`, `max` and `value` arguments in `"yyyy-mm-dd"` format or as `datetime` type (for example, `datetime.datetime(2024, 01, 01)`).

## Add a tooltip

The `description` argument enables you to add helpful context to your selector by displaying an info icon next to its title. Hovering over the icon shows a tooltip with your provided text.

You can provide [Markdown text](https://markdown-guide.readthedocs.io/) as a string to use the default info icon or a [`Tooltip`][vizro.models.Tooltip] model to use any icon from the [Google Material Icons library](https://fonts.google.com/icons).

!!! example "Selectors with tooltip"

    === "app.py"

        ```{.python pycafe-link hl_lines="19-23"}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        iris = px.data.iris()

        page = vm.Page(
            title="Selectors with icons",
            components=[
                vm.Graph(
                    figure=px.scatter(iris, x="sepal_length", y="sepal_width")
                ),
            ],
            controls=[
                vm.Filter(
                    column="species",
                    selector=vm.Checklist(
                        title="Select Species",
                        description="""
                            Select which species of iris you like.

                            [Click here](https://en.wikipedia.org/wiki/Iris_flower_data_set)
                            to learn more about flowers.""",
                    )
                ),
            ]
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"

        ```{.yaml hl_lines="16-19"}
        pages:
          - title: Selectors with icons
            components:
              - type: graph
                figure:
                  _target_: scatter
                  data_frame: iris
                  x: sepal_length
                  y: sepal_width
            controls:
              - column: species
                type: filter
                selector:
                  type: checklist
                  title: Select Species
                  description: |
                        Select which species of iris you like.

                        [Click here](https://en.wikipedia.org/wiki/Iris_flower_data_set) to learn more about flowers.
        ```

    === "Result"

        [![InfoIconSelector]][infoiconselector]

## The `extra` argument

Currently each selector is based on an underlying Dash component as mentioned in the sections above. Using the `extra` argument you can pass extra arguments to the underlying object in order to alter it beyond the chosen defaults. The available arguments can be found in the documentation of each underlying component that was linked in the respective sections above.

!!! note

    Using `extra` is a quick and flexible way to alter a component beyond what Vizro offers. However, [it is not a part of the official Vizro schema](../explanation/schema.md#what-is-the-vizro-json-schema) and the underlying implementation details may change. If you want to guarantee that your apps keep running, we recommend that you pin your Vizro version.

An example would be to make the [`RadioItem`][vizro.models.RadioItems] display inline instead of stacked vertically. For this you can use `extra={"inline": True}` argument:

!!! example "Inline Radio Items"

    === "app.py"

        ```{.python pycafe-link hl_lines="19"}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        iris = px.data.iris()

        page = vm.Page(
            title="Inline Radio Items",
            components=[
                vm.Graph(
                    figure=px.scatter(iris, x="sepal_length", y="sepal_width")
                ),
            ],
            controls=[
                vm.Filter(
                    column="species",
                    selector=vm.RadioItems(
                        title="Select Species",
                        extra={"inline": True}
                    )
                )
            ]
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"

        ```{.yaml hl_lines="16 17"}
        pages:
          - title: Inline Radio Items
            components:
              - type: graph
                figure:
                  _target_: scatter
                  data_frame: iris
                  x: sepal_length
                  y: sepal_width
            controls:
              - column: species
                type: filter
                selector:
                  type: radio_items
                  title: Select Species
                  extra:
                    inline: true
        ```

    === "Result"

        [![InlineRadio]][inlineradio]

[infoiconselector]: ../../assets/user_guides/selectors/info_icon_selector.png
[inlineradio]: ../../assets/user_guides/selectors/inlineradio.png
