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

CSS properties will be applied with the last served file taking precedence. The order of serving is:

1. Dash built-in stylesheets
2. Vizro built-in stylesheets
3. User assets folder stylesheets

Within each of these categories, individual files are served in alphanumeric order.

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



## Overwrite CSS properties in selective components
To adjust CSS properties for specific components, like altering the appearance of a selected [Card][vizro.models.Card] rather than all Cards,
you'll need to target the correct CSS selector based on the component hierarchy.
If you're unfamiliar with CSS selectors, you can refer to this [tutorial](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_selectors/Selector_structure) for guidance.

Here's how you can do it:
1. Assign a unique `id` to the relevant `Card`, for example: `Card(id="my-card", ...)`
2. Review the component's source code to find the appropriate CSS class or element you need to target.
It's essential to understand the relationship between the targeted CSS class or element and the component assigned the `id:
   - The `id` is provided to the `dcc.Markdown` component inside the `Card`.
   - The `dcc.Markdown` component is wrapped inside a parent container with the class name `"card"`.
   - The text is wrapped inside `<p>` elements that are descendants of the `dcc.Markdown` component.

For instance, if you aim to modify the background and font color of a specific card, you'll need to target the parent
container with the class "card" and the `<p>` elements, which are children of the `dcc.Markdown` with the `id`.

!!! example "Customizing CSS properties in selective components"
    === "my_css_file.css"
    ```css
    /* Apply styling to parent */
    .card:has(#my-card) {
      background-color: red;
    }

    /* Apply styling to children */
    #my-card p {
      color: black;
    }
    ```
    === "app.py"
        ```py
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Changing the card color",
            components=[
                vm.Card(id="my-card", text="""Lorem ipsum dolor sit amet consectetur adipisicing elit."""),
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
              id: my-card
            - text: |
                Lorem ipsum dolor sit amet consectetur adipisicing elit.
              type: card
          title: Changing the card color
        ```
    === "Result"
         [![CardCSS]][CardCSS]

    [CardCSS]: ../../assets/user_guides/assets/css_change_card.png


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
