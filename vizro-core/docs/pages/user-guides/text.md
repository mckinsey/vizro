# How to add text to your page

This guide shows you how to display text in your dashboard with the [`Text` component][vizro.models.Text].

!!! note "Card and Text components"

    The [`Card` component](card.md) and `Text` component both enable you to add text to your page using [Markdown syntax](https://markdown-guide.readthedocs.io/en/latest/) through the underlying Dash component [`dcc.Markdown`](https://dash.plotly.com/dash-core-components/markdown/).

    You should use `Text` to display plain Markdown text without any extra styling like borders or background, for example to add an introductory paragraph to your page.

    You should use `Card` to display Markdown text that needs attention drawn to it. Generally, this would be relatively short portions of text. Unlike `Text`, a `Card` can also be [used for navigation](card.md#create-a-navigation-card).

You can add a [`Text`][vizro.models.Text] component to your dashboard by inserting [`Text`][vizro.models.Text] into the `components` argument of the [`Page`][vizro.models.Page] or the [`Container`][vizro.models.Container] model.

!!! example "Text"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Text example",
            components=[
                vm.Text(
                    text="Commodi repudiandae consequuntur voluptatum."
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
              - text: Commodi repudiandae consequuntur voluptatum.
                type: text
            title: Text example
        ```

    === "Result"

        [![Text]][text]

## Customize text

The [`Text`][vizro.models.Text] uses the `dcc.Markdown` component from Dash as its underlying text component. For more details on customizing the [Markdown text](https://markdown-guide.readthedocs.io/), refer to the [`dcc.Markdown` component documentation](https://dash.plotly.com/dash-core-components/markdown). Based on examples from Dash, the [`Text`][vizro.models.Text] model supports the following:

- Headers
- Emphasis
- Lists
- Block Quotes
- Images
- Links

!!! example "Text using markdown"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Customizing Text",
            components=[
                vm.Text(
                    text="""
                        # Header level 1 <h1>

                        ## Header level 2 <h2>

                        ### Header level 3 <h3>

                        #### Header level 4 <h4>

                        Commodi repudiandae consequuntur voluptatum laborum numquam blanditiis harum quisquam eius sed odit.

                        Fugiat iusto fuga praesentium option, eaque rerum! Provident similique accusantium nemo autem.

                        Obcaecati tenetur iure eius earum ut molestias architecto voluptate aliquam nihil, eveniet aliquid.

                        Culpa officia aut! Impedit sit sunt quaerat, odit, tenetur error, harum nesciunt ipsum debitis quas.

                        ### Block Quotes

                        >
                        > A block quote is a long quotation, indented to create a separate block of text.
                        >

                        ### Lists

                        * Item A
                            * Sub Item 1
                            * Sub Item 2
                        * Item B

                        ### Emphasis

                        This word will be *italic*

                        This word will be **bold**

                        This word will be _**bold and italic**_
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
        # See yaml_version example
        pages:
          - components:
              - title: Customizing Text
                text: |
                  # Header level 1 <h1>

                  ## Header level 2 <h2>

                  ### Header level 3 <h3>

                  #### Header level 4 <h4>

                  Commodi repudiandae consequuntur voluptatum laborum numquam blanditiis harum quisquam eius sed odit.

                  Fugiat iusto fuga praesentium option, eaque rerum! Provident similique accusantium nemo autem.

                  Obcaecati tenetur iure eius earum ut molestias architecto voluptate aliquam nihil, eveniet aliquid.

                  Culpa officia aut! Impedit sit sunt quaerat, odit, tenetur error, harum nesciunt ipsum debitis quas.

                  ### Block Quotes

                  >
                  > A block quote is a long quotation, indented to create a separate block of text.
                  >

                  ### Lists

                  * Item A
                      * Sub Item 1
                      * Sub Item 2
                  * Item B

                  ### Emphasis

                  This word will be *italic*

                  This word will be **bold**

                  This word will be _**bold and italic**_
        ```

    === "Result"

        [![TextMarkdown]][textmarkdown]

## The `extra` argument

The `Text` is based on the underlying Dash component [`dcc.Markdown`](https://dash.plotly.com/dash-core-components/markdown/). Using the `extra` argument you can pass extra arguments to `dcc.Markdown` in order to alter it beyond the chosen defaults.

!!! note

    Using `extra` is a quick and flexible way to alter a component beyond what Vizro offers. However, [it is not a part of the official Vizro schema](../explanation/schema.md#what-is-the-vizro-json-schema) and the underlying implementation details may change. If you want to guarantee that your apps keep running, we recommend that you pin your Vizro version.

An example use would be to set `mathjax=True` (defaults to `False`) to display mathematical equations. For this, you can use `extra={"mathjax": True}`.

!!! example "Text with extra argument"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Text with extra argument",
            components=[
                vm.Text(
                    text="""
                      This example uses the block delimiter:
                      $$
                      \\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}
                      $$

                      This example uses the inline delimiter:
                      $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$
                    """,
                    extra={"mathjax": True}
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
              - text: |
                  This example uses the block delimiter:
                  $$
                  \\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}
                  $$

                  This example uses the inline delimiter:
                  $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$
                type: text
            title: Text with extra argument
        ```

    === "Result"

        [![TextExtra]][textextra]

[text]: ../../assets/user_guides/components/text.png
[textextra]: ../../assets/user_guides/components/text_extra.png
[textmarkdown]: ../../assets/user_guides/components/text_markdown.png
