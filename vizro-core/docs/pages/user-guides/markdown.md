# How to use markdown

This guide shows you how to use markdown to visualize your data in the dashboard.

The [`Markdown`][vizro.models.Markdown] is a flexible and extensible component that enables customization via markdown text. Refer to any online guide for [basic markdown usage](https://markdown-guide.readthedocs.io/en/latest/). It is based on the underlying Dash component [`dcc.Markdown`](https://dash.plotly.com/dash-core-components/markdown/).

You can add a [`Markdown`][vizro.models.Markdown] to your dashboard by inserting the [`Markdown`][vizro.models.Markdown] into the `components` argument of the [`Page`][vizro.models.Page] or of the [`Container`][vizro.models.Container] model.

!!! example "Markdown"
    === "app.py"
        ```{.python pycafe-link}
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Markdown",
            components=[
                vm.Markdown(
                    text="""
                        ### Markdown Title
                        Commodi repudiandae consequuntur voluptatum.
                    """,
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```

    === "app.yaml"
        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See from_yaml example
        pages:
          - components:
              - text: |
                  Commodi repudiandae consequuntur voluptatum.
                title: Markdown Title
                type: markdown
            title: Markdown
        ```

    === "Result"
        [![Markdown]][markdown]

### Customize Markdown text

The [`Markdown`][vizro.models.Markdown] uses the `dcc.Markdown` component from Dash as its underlying text component. For more details on customizing the markdown text, refer to the [`dcc.Markdown` component documentation](https://dash.plotly.com/dash-core-components/markdown). Based on examples from Dash, the [`Markdown`][vizro.models.Markdown] model supports the following:

- Headers
- Emphasis
- Lists
- Block Quotes

!!! example "Markdown with custom text"
    === "app.py"
        ```{.python pycafe-link}
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Customizing Text",
            components=[
                vm.Markdown(
                    text="""
                        # Header level 1 <h1>

                        ## Header level 2 <h2>

                        ### Header level 3 <h3>

                        #### Header level 4 <h4>
                    """,
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```

    === "app.yaml"
        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See from_yaml example
        pages:
          - components:
              - text: |
                  # Header level 1 <h1>

                  ## Header level 2 <h2>

                  ### Header level 3 <h3>

                  #### Header level 4 <h4>
                type: markdown
            title: Customizing Text
        ```

    === "Result"
        [![MarkdownText]][markdowntext]

### The `extra` argument

The `Markdown` is based on the underlying Dash component [`dcc.Markdown`](https://dash.plotly.com/dash-core-components/markdown/). Using the `extra` argument you can pass additional arguments to `dcc.Markdown` in order to alter it beyond the chosen defaults.

!!! note
    Using `extra` is a quick and flexible way to alter a component beyond what Vizro offers. However, [it is not a part of the official Vizro schema](../explanation/schema.md#what-is-the-vizro-json-schema) and the underlying implementation details may change. If you want to guarantee that your apps keep running, we recommend that you pin your Vizro version.

An example use would be to extend the `Markdown` height to only take as much space as the content, and not to take up all the available height (default). For this, you can use `extra={"style": {"height": "unset"}}`. This would be a shortcut to using custom CSS in the assets folder as explained in [our guide on CSS](../user-guides/custom-css.md).

!!! example "Markdown with extra argument"
    === "app.py"
        ```{.python pycafe-link}
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Customizing Markdown",
            components=[
                vm.Markdown(
                    text="""
                      This example uses the block delimiter:
                      $$
                      \\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}
                      $$

                      This example uses the inline delimiter:
                      $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$
                    """, extra={"matjax": True}
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```

    === "app.yaml"
        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See from_yaml example
        pages:
          - components:
              - text: |
                  This example uses the block delimiter:
                  $$
                  \\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}
                  $$

                  This example uses the inline delimiter:
                  $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$
                type: markdown
            title: Customizing Markdown
        ```

    === "Result"
        [![MarkdownCustom]][markdowncustom]

[markdown]: ../../assets/user_guides/components/markdown.png
[markdowncustom]: ../../assets/user_guides/components/markdowncustom.png
[markdowntext]: ../../assets/user_guides/components/markdowntext.png
