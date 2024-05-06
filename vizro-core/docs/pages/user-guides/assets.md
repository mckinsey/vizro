# How to add static assets

This guide shows you how to add static assets to your dashboard. Static assets are images that you would like to show in your dashboard, or custom CSS and JS files
with which you would like to enhance/change the appearance of your dashboard.

To add images, custom CSS or JS files, create a folder named `assets` in the root of your app directory and insert your files.
Assets included in that folder are automatically served after serving Vizro's static files via the `external_stylesheets`  and `external_scripts` arguments of [Dash](https://dash.plotly.com/external-resources#adding-external-css/javascript).
The user's `assets` folder thus always takes precedence.

```text title="Example folder structure"
├── app.py
├── assets
│   ├── css
│       ├── **/*.css
│   ├── images
│       ├── icons
│           ├── collections.svg
│       ├── app.svg
│       ├── logo.svg
│   ├── favicon.ico
```

!!! warning "Dash Bootstrap Themes"

    Note that Vizro is currently not compatible with [Dash Bootstrap Themes](https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/).
    Adding a Bootstrap stylesheet will have no visual effect on the [components](https://vizro.readthedocs.io/en/stable/pages/user_guides/components/) included in Vizro.

## Change the favicon
To change the default favicon (website icon appearing in the browser tab), add a file named `favicon.ico` to your `assets` folder.
For more information, see the [Dash documentation](https://dash.plotly.com/external-resources#changing-the-favicon).

## Overwrite global CSS properties
To overwrite any global CSS properties of existing components, target the right CSS property and place your CSS files in the `assets` folder. This will overwrite any existing defaults for that CSS property.
For reference, see the [Vizro CSS files](https://github.com/mckinsey/vizro/tree/main/vizro-core/src/vizro/static/css).

!!! example "Customizing global CSS properties"
    === "my_css_file.css"
    ```css
    h1, h2 {
     color: hotpink;
    }
    ```
    === "app.py"
        ```py
        import os
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
                title="Changing the header color",
                components=[
                    vm.Card(
                        text="""

                            # This is an <h1> tag

                            ## This is an <h2> tag

                            ###### This is an <h6> tag
                        """)
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
                # This is an <h1> tag

                ## This is an <h2> tag

                ###### This is an <h6> tag
              type: card
          title: Changing the header color
        ```
    === "Result"
         [![AssetsCSS]][AssetsCSS]

    [AssetsCSS]: ../../assets/user_guides/assets/css_change.png


## Overwrite CSS properties for specific pages
Each page is assigned a unique identifier (`page.id`), which is sanitized and then stored as the ID of an outer `<div>` element.
This identifier is formatted according to CSS naming conventions by removing non-alphanumeric characters and replacing spaces with dashes.
For instance, if a `page.id` is "Variable Analysis," it will be stored as a CSS ID of "variable-analysis."

This unique identifier enables you to use CSS selectors to target specific pages and their components for styling.

!!! note "Default Page ID"

    If a page's ID is not explicitly set, it defaults to the page title.
    Refer to our [user-guide on pages](pages.md) for more information on setting the page ID.


Suppose you want to hide the page title on one page only. Here's how you can achieve this:

1. Identify the CSS class or ID you need to target. For example, to hide the page title, you need to hide its parent container with the ID `right-header`.
2. Use the unique identifier to target only the page you want to modify.


!!! example "Hide page title on selected pages"
    === "my_css_file.css"
    ```css
    #page-with-hidden-title #right-header {
      display: none;
    }
    ```
    === "app.py"
        ```py
        import vizro.models as vm
        from vizro import Vizro

        page_one = vm.Page(
            title="Page with hidden title",
            components=[vm.Card(text="""# Placeholder""")]
        )

        page_two = vm.Page(
            title="Page with shown title",
            components=[vm.Card(text="""# Placeholder""")]
        )

        dashboard = vm.Dashboard(pages=[page_one, page_two])
        Vizro().build(dashboard).run()
        ```
    === "app.yaml"
        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
        - components:
            - text: |
                # Placeholder
              type: card
          title: Page with hidden title
        - components:
            - text: |
                # Placeholder
              type: card
          title: Page with shown title
        ```
    === "Result"
         [![PageTitle]][PageTile]

    [CardCSS]: ../../assets/user_guides/assets/css_page_title.png


## Overwrite CSS properties in selective components
To overwrite CSS properties of selective components, pass an ID to the relevant component and target the right CSS property.

For more information, see this [CSS selectors tutorial](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_selectors/Selector_structure).

Let's say we want to change the background and font-color of one [`Card`][vizro.models.Card] instead of all existing Cards in the Dashboard.
We can use the ID of the outermost Div to target the inner sub-components of the card. Note that all our components have an ID attached to the outermost Div,
following the pattern `"{component_id}_outer"`.

To achieve this, do the following:

1. Pass a custom `id` to the relevant `Card`, for example: `Card(id="my_card", ...)`
2. Take a look at the source code of the component to see which CSS Class you need to target such as `"card"`
3. Use CSS selectors to target the right property by using the ID of the outermost Div `"my_card_outer"`


!!! example "Customizing CSS properties in selective components"
    === "my_css_file.css"
    ```css
    #my_card_outer.card {
      background-color: white;
    }

    #my_card_outer .card_text p {
      color: black;
    }
    ```
    === "app.py"
        ```py
        import os
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Changing the card color",
            components=[
                vm.Card(id="my_card", text="""Lorem ipsum dolor sit amet consectetur adipisicing elit."""),
                vm.Card(text="""Lorem ipsum dolor sit amet consectetur adipisicing elit.""")
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
                Lorem ipsum dolor sit amet consectetur adipisicing elit.
              type: card
              id: my_card
            - text: |
                Lorem ipsum dolor sit amet consectetur adipisicing elit.
              type: card
          title: Changing the card color
        ```
    === "Result"
         [![CardCSS]][CardCSS]

    [CardCSS]: ../../assets/user_guides/assets/css_change_card.png


CSS properties will be applied with the last served file taking precedence. The order of serving is:

1. Dash built-in stylesheets
2. Vizro built-in stylesheets
3. User assets folder stylesheets

Within each of these categories, individual files are served in alphanumeric order.

## Change the `assets` folder path
If you do not want to place your `assets` folder in the root directory of your app, you can
specify an alternative path through the `assets_folder` argument of the [`Vizro`][vizro.Vizro] class.

```python
from vizro import Vizro
import vizro.models as vm

page = <INSERT CONFIGURATION HERE>
dashboard = vm.Dashboard(pages=[page])

app = Vizro(assets_folder="path/to/assets/folder").build(dashboard).run()

```

Note that in the example above, you still need to configure your [`Page`][vizro.models.Page].
See more information in the [Pages User Guide](pages.md).


## Include a meta tags image

Vizro automatically adds [meta tags](https://metatags.io/) to display a preview card when your app is shared on social media and chat
clients. To include an image in the preview, place an image file in the assets folder named `app.<extension>`  or
`logo.<extension>`. Vizro searches the assets folder and uses the first one it finds.

Image types of `apng`, `avif`, `gif`, `jpeg`, `jpg`, `png`, `svg`, and `webp` are supported.

## Add a logo image

Vizro will automatically incorporate the dashboard logo in the top-left corner of each page if an image named `logo.<extension>` is present within the assets folder.

Image types of `apng`, `avif`, `gif`, `jpeg`, `jpg`, `png`, `svg`, and `webp` are supported.
