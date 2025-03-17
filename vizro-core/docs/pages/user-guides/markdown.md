# How to use markdown

This guide shows you how to use markdown to display plain text without any additional styling like borders or background in the dashboard.

The [`Markdown` component][vizro.models.Markdown] is used for displaying plain text. It is flexible and extensible due to its underlying usage of Markdown syntax. To find out more about basic Markdown syntax, refer to [this or any other online guide](https://markdown-guide.readthedocs.io/en/latest/).

The `Markdown` component is based on the underlying Dash component [`dcc.Markdown`](https://dash.plotly.com/dash-core-components/markdown/). You can add a [`Markdown`][vizro.models.Markdown] component to your dashboard by inserting [`Markdown`][vizro.models.Markdown] into the `components` argument of the [`Page`][vizro.models.Page] or the [`Container`][vizro.models.Container] model.

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

## Customize Markdown text

The [`Markdown`][vizro.models.Markdown] component uses the `dcc.Markdown` component from Dash as its underlying text component. For more details on customizing markdown text, refer to the [`dcc.Markdown` component documentation](https://dash.plotly.com/dash-core-components/markdown/). It supports (among other things) the following features:

- Headers
- Emphasis
- Lists
- Block Quotes
- Images
- Links

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

## The `extra` argument

The `Markdown` is based on the underlying Dash component [`dcc.Markdown`](https://dash.plotly.com/dash-core-components/markdown/). Using the `extra` argument you can pass additional arguments to `dcc.Markdown` in order to alter it beyond the chosen defaults.

!!! note
    Using `extra` is a quick and flexible way to alter a component beyond what Vizro offers. However, [it is not a part of the official Vizro schema](../explanation/schema.md#what-is-the-vizro-json-schema) and the underlying implementation details may change. If you want to guarantee that your apps keep running, we recommend that you pin your Vizro version.

An example use would be to set `Markdown` `mathjax=True` (defaults to `False`) to display the mathematical equations. For this, you can use `extra={"mathjax": True}`.

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
