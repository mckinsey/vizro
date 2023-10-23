# How to use cards & buttons

This guide shows you how to use cards and buttons to visualize and interact with your data in the dashboard.

The [`Page`][vizro.models.Page] models accepts the `components` argument, where you can enter your visual content e.g.
[`Graph`][vizro.models.Graph], [`Table`][vizro.models.Table], [`Card`][vizro.models.Card] or [`Button`][vizro.models.Button].

## Card

The [`Card`][vizro.models.Card] is a flexible and extensible component, allowing for customization via Markdown text.
For a basic guide on markdown text, please refer to the documentation [here](https://markdown-guide.readthedocs.io/en/latest/).

You can add a [`Card`][vizro.models.Card] to your dashboard by inserting the [`Card`][vizro.models.Card] into the `components` argument of the [`Page`][vizro.models.Page].


!!! example "Card"
    === "app.py"
        ```py
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Card",
            components=[
                vm.Card(
                    text="""
                        ### Card Title
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
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
        # See from_yaml example
        pages:
        - components:
            - text: |
                Commodi repudiandae consequuntur voluptatum.
              title: Card Title
              type: card
          title: Card
        ```
    === "Result"
        [![Card]][Card]

    [Card]: ../../assets/user_guides/components/card.png

### Customizing text

The [`Card`][vizro.models.Card] utilizes the `dcc.Markdown` component from Dash as its underlying text component.
For more details on customizing the markdown text, refer to the `dcc.Markdown` component documentation [here](https://dash.plotly.com/dash-core-components/markdown).
Based on the provided examples from Dash, the [`Card`][vizro.models.Card] model supports the following:

- Headers
- Emphasis
- Lists
- Block Quotes
- Links

!!! example "Card with custom text"
    === "app.py"
        ```py
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Customizing Text",
            components=[
                vm.Card(
                    text="""
                        # Header level 1 <h1>

                        ## Header level 2 <h2>

                        ### Header level 3 <h3>

                        #### Header level 4 <h4>
                    """,
                ),
                vm.Card(
                    text="""
                         ### Paragraphs
                         Commodi repudiandae consequuntur voluptatum laborum numquam blanditiis harum quisquam eius sed odit.

                         Fugiat iusto fuga praesentium option, eaque rerum! Provident similique accusantium nemo autem.

                         Obcaecati tenetur iure eius earum ut molestias architecto voluptate aliquam nihil, eveniet aliquid.

                         Culpa officia aut! Impedit sit sunt quaerat, odit, tenetur error, harum nesciunt ipsum debitis quas.
                    """,
                ),
                vm.Card(
                    text="""
                        ### Block Quotes

                        >
                        > A block quote is a long quotation, indented to create a separate block of text.
                        >
                    """,
                ),
                vm.Card(
                    text="""
                        ### Lists

                        * Item A
                            * Sub Item 1
                            * Sub Item 2
                        * Item B
                    """,
                ),
                vm.Card(
                    text="""
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
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
        # See from_yaml example
        pages:
        - components:
          - text: |
              # Header level 1 <h1>

              ## Header level 2 <h2>

              ### Header level 3 <h3>

              #### Header level 4 <h4>
            type: card
          - text: |
              Commodi repudiandae consequuntur voluptatum laborum numquam blanditiis harum quisquam eius sed odit.

              Fugiat iusto fuga praesentium option, eaque rerum! Provident similique accusantium nemo autem.

              Obcaecati tenetur iure eius earum ut molestias architecto voluptate aliquam nihil, eveniet aliquid.

              Culpa officia aut! Impedit sit sunt quaerat, odit, tenetur error, harum nesciunt ipsum debitis quas.
            title: Paragraphs
            type: card
          - text: |
              >
              > A block quote is a long quotation, indented to create a separate block of text.
              >
            title: Block Quotes
            type: card
          - text: |
              * Item A
                * Sub Item 1
                * Sub Item 2
              * Item B
            title: Lists
            type: card
          - text: |
              This word will be *italic*

              This word will be **bold**

              This word will be _**bold and italic**_
            title: Emphasis
            type: card
          title: Customizing Text
        ```
    === "Result"
        [![CardText]][CardText]

    [CardText]: ../../assets/user_guides/components/card_text.png

### Placing images

Images can be added to the `text` parameter by using the standard markdown syntax:

`![Image ALT text](Image URL)`

An image ALT text provides a description to your image and serves e.g. as a text placeholder or to improve the
accessibility of your app. Providing an image ALT text is optional.

1. To use a relative Image URL, place an image of your choice into your `assets` folder first
2. Use markdown to render your image by using one of the following syntax:
    - Relative Image URL: `![Image ALT text](/path/to/image.png)`
    - Absolute Image URL: `![Image ALT text](https://XXXXXX)`

!!! example "Card with image"
    === "app.py"
        ```py
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
                title="Placing Images",
                components=[
                    vm.Card(
                        text="""
                        ### My card with image!

                        ![continent](assets/images/continents/africa.svg)

                         Commodi repudiandae consequuntur voluptatum laborum numquam blanditiis harum quisquam eius sed odit.

                         Fugiat iusto fuga praesentium option, eaque rerum! Provident similique accusantium nemo autem.

                         Obcaecati tenetur iure eius earum ut molestias architecto voluptate aliquam nihil, eveniet aliquid.
                    """,
                    ),
                ],
            )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```
    === "app.yaml"
        ```yaml
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
        # See from_yaml example
        pages:
        - components:
            - text: |
                ![continent](assets/images/continents/africa.svg)

                Commodi repudiandae consequuntur voluptatum laborum numquam blanditiis harum quisquam eius sed odit.

                Fugiat iusto fuga praesentium option, eaque rerum! Provident similique accusantium nemo autem.

                Obcaecati tenetur iure eius earum ut molestias architecto voluptate aliquam nihil, eveniet aliquid.
              title: My card with image!
              type: card
          title: Placing Images
        ```
    === "Result"
         [![CardImageDefault]][CardImageDefault]

    [CardImageDefault]: ../../assets/user_guides/components/card_image_default.png

!!! note

    Note that inserting images using html is by default turned off by the `dcc.Markdown` to prevent users being exposed
    to cross-site scripting attacks. If you need to turn it on, a custom component would have to be created.

You might notice that the image is quite large, find out how to style images (e.g. position and size) in the next section!

### Styling images

To change the styling of the image (e.g. size or position), add a URL hash to your image like this:

`![Image ALT text](Image URL#my-image)`

Note the added URL hash `#my-image`. Now create a CSS file placed in your `assets` folder
and provide an attribute selector to select images with that matching URL hash.

!!! example "Card with styled image"
    === "images.css"
    ```css
    img[src*="#my-image"] {
      width: 120px;
      height: 120px;
    }
    ```
    === "app.py"
        ```py
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
                title="Styling Images",
                components=[
                    vm.Card(
                        text="""
                        ### My card with image!

                        ![](assets/images/continents/africa.svg#my-image)

                         Commodi repudiandae consequuntur voluptatum laborum numquam blanditiis harum quisquam eius sed odit.

                         Fugiat iusto fuga praesentium option, eaque rerum! Provident similique accusantium nemo autem.

                         Obcaecati tenetur iure eius earum ut molestias architecto voluptate aliquam nihil, eveniet aliquid.
                    """,
                    ),
                ],
            )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```
    === "app.yaml"
        ```yaml
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
        # See from_yaml example
        pages:
        - components:
            - text: |
                ![](assets/images/continents/africa.svg#my-image)

                Commodi repudiandae consequuntur voluptatum laborum numquam blanditiis harum quisquam eius sed odit.

                Fugiat iusto fuga praesentium option, eaque rerum! Provident similique accusantium nemo autem.

                Obcaecati tenetur iure eius earum ut molestias architecto voluptate aliquam nihil, eveniet aliquid.
              title: My card with image!
              type: card
          title: Styling Images
        ```
    === "Result"
         [![CardImageStyled]][CardImageStyled]

    [CardImageStyled]: ../../assets/user_guides/components/card_image_styled.png

???+ tip

    Use the following pre-defined URL hashes in your image path to have the image float next to the text:

    - floating-left: `![](my_image.png#floating-left)`
    - floating-right: `![](my_image.png#floating-right)`
    - floating-center: `![](my_image.png#floating-center)`

!!! example "Card with floating image"
    === "app.py"
        ```py
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
                title="Floating Images",
                components=[
                    vm.Card(
                        text="""
                        ### My card with image!

                        ![](assets/images/continents/africa.svg#my-image#floating-right)

                         Commodi repudiandae consequuntur voluptatum laborum numquam blanditiis harum quisquam eius sed odit.

                         Fugiat iusto fuga praesentium option, eaque rerum! Provident similique accusantium nemo autem.

                         Obcaecati tenetur iure eius earum ut molestias architecto voluptate aliquam nihil, eveniet aliquid.

                         Culpa officia aut! Impedit sit sunt quaerat, odit, tenetur error, harum nesciunt ipsum debitis quas.

                         Obcaecati tenetur iure eius earum ut molestias architecto voluptate aliquam nihil, eveniet aliquid.

                        Culpa officia aut! Impedit sit sunt quaerat, odit, tenetur error, harum nesciunt ipsum debitis quas.
                    """,
                    ),
                ],
            )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```
    === "app.yaml"
        ```yaml
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
        # See from_yaml example
        pages:
        - components:
            - text: |
                ![](assets/images/continents/africa.svg#my-image#floating-right)

                Commodi repudiandae consequuntur voluptatum laborum numquam blanditiis harum quisquam eius sed odit.

                Fugiat iusto fuga praesentium option, eaque rerum! Provident similique accusantium nemo autem.

                Obcaecati tenetur iure eius earum ut molestias architecto voluptate aliquam nihil, eveniet aliquid.

                Culpa officia aut! Impedit sit sunt quaerat, odit, tenetur error, harum nesciunt ipsum debitis quas.

                Obcaecati tenetur iure eius earum ut molestias architecto voluptate aliquam nihil, eveniet aliquid.

                Culpa officia aut! Impedit sit sunt quaerat, odit, tenetur error, harum nesciunt ipsum debitis quas.
              title: My card with image!
              type: card
          title: Floating Images
        ```
    === "Result"
         [![CardImageFloating]][CardImageFloating]

    [CardImageFloating]: ../../assets/user_guides/components/card_image_floating.png

### Creating navigation

A navigation card allows you to navigate to a different page via a click on the card area.
To create a navigation card, do the following:

- Insert the [`Card`][vizro.models.Card] into the `components` argument of the [`Page`][vizro.models.Page]
- Provide the `text` parameter with a title and some description
- Provide the `href` parameter (relative or absolute URL)

!!! example "Navigation Card"
    === "app.py"
        ```py
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        iris = px.data.iris()

        page_1 = vm.Page(
            title="Homepage",
            components=[
                vm.Card(
                    text="""
                    ### Filters and parameters

                    Leads to the first page on click.
                    """,
                    href="/filters-and-parameters",
                ),
                vm.Card(
                    text="""
                    ### Google - External Link

                    Leads to an external link on click.
                    """,
                    href="https://google.com",
                ),
            ],
        )

        page_2 = vm.Page(
            title="Filters and parameters",
            path="filters-and-parameters",
            components=[
                vm.Graph(id="scatter", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="sepal_width")),
            ],
        )

        dashboard = vm.Dashboard(pages=[page_1, page_2])

        Vizro().build(dashboard).run()
        ```
    === "app.yaml"
        ```yaml
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
        # See from_yaml example
        pages:
        - components:
            - text: |
                ### Filters and parameters

                Leads to the first page on click
              href: /filters-and-parameters
              type: card
            - text: |
                ### Google - External Link

                Leads to an external link on click.
              href: https://google.com
              type: card
          title: Homepage
        - components:
            - figure:
                _target_: scatter
                color: sepal_width
                data_frame: iris
                x: sepal_length
                y: petal_width
              id: scatter
              type: graph
          title: Filters and parameters
        ```
    === "Result"
           [![NavCard]][NavCard]

       [NavCard]: ../../assets/user_guides/components/nav_card.png

If you now click on the card area, you should automatically be redirected to the relevant `href`.

???+ note

    When using the [`Card`][vizro.models.Card], keep the following considerations in mind:

    - If the href provided is a relative URL, it should match the `path` of the [`Page`][vizro.models.Page] that the [`Card`][vizro.models.Card] should navigate to.
    - If the href provided is an absolute link, it should start with `https://` or an equivalent protocol.

### Adding an icon
If you want to add an icon to your card, just add your image as described in the [previous section](#placing-images)
If you use the image URL hash `icon-top`, the image will be styled according to our default icon styling.

!!! example "Navigation Card with Icon"
    === "app.py"
        ```py hl_lines="12 23"
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        iris = px.data.iris()

        page_1 = vm.Page(
            title="Homepage",
            components=[
                vm.Card(
                    text="""
                    ![](assets/images/icons/content/hypotheses.svg#icon-top)

                    ### Filters and parameters

                    Leads to the first page on click.
                    """,
                    href="/filters-and-parameters",
                ),

                vm.Card(
                    text="""
                    ![](assets/images/icons/content/features.svg#icon-top)

                    ### Google - External Link

                    Leads to an external link on click.
                    """,
                    href="https://google.com",
                ),
            ],
        )

        page_2 = vm.Page(
            title="Filters and parameters",
            path="filters-and-parameters",
            components=[
                vm.Graph(id="scatter", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="sepal_width")),
            ],
        )

        dashboard = vm.Dashboard(pages=[page_1, page_2])

        Vizro().build(dashboard).run()
        ```
    === "app.yaml"
        ```yaml hl_lines="5 13"
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
        # See from_yaml example
        pages:
        - components:
            - text: |
                ![](assets/images/icons/content/hypotheses.svg#icon-top)

                ### Filters and parameters

                Leads to the first page on click
              href: /filters-and-parameters
              type: card
            - text: |
                ![](assets/images/icons/content/features.svg#icon-top)

                ### Google - External Link

                Leads to an external link on click.
              href: https://google.com
              type: card
          title: Homepage
        - components:
            - figure:
                _target_: scatter
                color: sepal_width
                data_frame: iris
                x: sepal_length
                y: petal_width
              id: scatter
              type: graph
          title: Filters and parameters
        ```
    === "Result"
           [![NavCardIcon]][NavCardIcon]

       [NavCardIcon]: ../../assets/user_guides/components/nav_card_icon.png

Note that in the above example the first [`Card`][vizro.models.Card] navigates to an existing [`Page`][vizro.models.Page]
in the app with `path = filters-and-parameters` and the second one to an external link.

## Button

To enhance dashboard interactions, you can use the [`Button`][vizro.models.Button] component to trigger any pre-defined
action functions such as e.g. exporting chart data. Please refer to the [user guide][vizro.actions] on
[`Actions`][vizro.models.Action] for currently available options.

To add a [`Button`][vizro.models.Button], simply insert it into the `components` argument of the
[`Page`][vizro.models.Page].

You can configure the `text` argument to alter the display text of the [`Button`][vizro.models.Button] and the
`actions` argument to define which action function should be executed on button click.

In the below example we show how to configure a button to export the filtered data of a target chart using
[export_data][vizro.actions.export_data], a pre-defined action function.


!!! example "Button"
    === "app.py"
        ```py
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.actions import export_data

        df = px.data.iris()

        page = vm.Page(
            title="My first page",
            layout=vm.Layout(grid=[[0], [0], [0], [0], [1]]),
            components=[
                vm.Graph(
                    id="scatter_chart",
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
                    actions=[vm.Action(function=export_data(targets=["scatter_chart"]))],
                ),
            ],
            controls=[vm.Filter(column="species", selector=vm.Dropdown(title="Species"))],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```
    === "app.yaml"
        ```yaml
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
        # See from_yaml example
        pages:
          - components:
            - figure:
                _target_: scatter
                x: sepal_width
                y: sepal_length
                color: species
                size: petal_length
                data_frame: iris
              id: scatter_chart
              type: graph
            - type: button
              text: Export data
              id: export_data
              actions:
                - function:
                    _target_: export_data
                    targets:
                      - scatter_chart
            controls:
              - column: species
                selector:
                  title: Species
                  type: dropdown
                type: filter
            layout:
              grid:
                - [0]
                - [0]
                - [0]
                - [0]
                - [1]
            title: My first page
        ```
    === "Result"
        [![Button]][Button]

    [Button]: ../../assets/user_guides/components/button.png

The [`Button`][vizro.models.Button] component is currently reserved to be used inside the main panel (right-side) of the dashboard.
However, there might be use cases where one would like to place the `Button` inside the control panel (left-side) with the other controls.

In this case, simply follow the user-guide outlined for [custom components](custom_components.md) and manually add the `Button` as a valid type to the `controls` argument by running the following lines before your dashboard configurations:

```python
from vizro import Vizro
import vizro.models as vm

vm.Page.add_type("controls", vm.Button)

# Add dashboard configurations below
...
```
