# How to add static assets

This guide shows you how to add static assets to your dashboard. Static assets are images that you would like to show in your dashboard, or custom CSS and JS files
with which you would like to enhance/change the appearance of your dashboard.

To add images, custom CSS or JS files, create a folder named `assets` in the root of your app directory and insert your files.
Assets included in that folder are automatically served after serving Vizro's static files via the `external_stylesheets`  and `external_scripts` arguments of [Dash](https://dash.plotly.com/external-resources#adding-external-css/javascript).
The user-provided `assets` folder thus always takes precedence.

```text title="Example folder structure"
├── app.py
├── assets
│   ├── css
│       ├── **/*.css
│   ├── images
│       ├── icons
│           ├── collections.svg
├── favicon.ico
```

## Changing the favicon
To change the default favicon (website icon appearing in the browser tab), add a file named `favicon.ico` to your `assets` folder.
For more information, see [here](https://dash.plotly.com/external-resources#changing-the-favicon).

## Overwriting global CSS properties
To overwrite any global CSS properties of existing components, target the right CSS property and place your CSS files in the `assets` folder. This will overwrite any existing defaults for that CSS property.
For reference, all Vizro CSS files can be found [here](https://github.com/mckinsey/vizro/tree/main/vizro-core/src/vizro/static/css).

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
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
        # See from_yaml example
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


## Overwriting CSS properties in selective components
To overwrite CSS properties of selective components, provide an ID to the relevant component and target the right CSS property.
For more information on how CSS selectors work, see [here](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_selectors/Selector_structure).

Let's say we want to change the background and font-color of one [`Card`][vizro.models.Card] instead of all existing Cards in the Dashboard.
We can use the ID of the outermost Div to target the inner sub-components of the card. Note that all our components have an ID attached to the outermost Div,
following the pattern `"{component_id}_outer"`.

To achieve this, do the following:

1. Provide a custom `id` to the relevant `Card` e.g `Card(id="my_card", ...)`
2. Take a look at the source code of the component to see which CSS Class you need to target e.g. `"card_container"` or `"card_text"`
3. Use CSS selectors to target the right property e.g. by leveraging the ID of the outermost Div `"my_card_outer"`


!!! example "Customizing CSS properties in selective components"
    === "my_css_file.css"
    ```css
    #my_card_outer.card_container {
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
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
        # See from_yaml example
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

Within each of these categories, individual files are served in alphanumerical order.

## Changing the `assets` folder path
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
A guide on how to do that you can find [here](pages.md).
