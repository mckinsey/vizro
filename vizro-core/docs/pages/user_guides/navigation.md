# How to use the navigation panel

This guide shows you how to use and customize the left navigation panel in your dashboard.

The [`Dashboard`][vizro.models.Dashboard] model also accepts a `navigation` argument, where you can enter the [`Navigation`][vizro.models.Navigation] model. A [`Navigation`][vizro.models.Navigation] in your dashboard facilitates grouping and navigating through your pages.

## Using the default navigation

By default, a navigation panel with an accordion item per page and a default title of `SELECT PAGE` is added to your dashboard. To leverage the navigation panel, you do not need to configure anything on top.

## Customizing your navigation panel

If you want to deviate from the default title `SELECT PAGE` and instead provide a title for a group of selected pages, do the following steps:

1. Provide a `dict` mapping of the page group title and a list of page IDs to the `pages` argument of the [`Navigation`][vizro.models.Navigation] model

    ```
    Navigation(pages={
        "First title": ["My first page"],
        "Second title": ["My second page"]})
    ```

2. Insert the [Navigation][vizro.models.Navigation] model into the `navigation` argument of the [Dashboard][vizro.models.Dashboard] model

!!! example "Customizing the navigation panel"
    === "app.py"
        ```py
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm

        iris = px.data.iris()

        page_1 = vm.Page(
                    title="My first page",
                    components=[
                        vm.Graph(
                            id="scatter_chart",
                            figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")
                        ),
                    ],
        )
        page_2 = vm.Page(
                    title="My second page",
                    components=[
                        vm.Graph(
                            id="line_chart",
                            figure=px.line(iris, x="sepal_length", y="petal_width", color="species")
                        ),
                    ],
                )

        dashboard = vm.Dashboard(
                        pages=[page_1, page_2],
                        navigation=vm.Navigation(
                            pages={"First title": ["My first page"], "Second title": ["My second page"]}
                        )
                    )

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
                  data_frame: iris
                  x: sepal_length
                  y: petal_width
                  color: species
                id: scatter_chart
                type: graph
            title: My first page
        - components:
             - figure:
                  _target_: line
                  data_frame: iris
                  x: sepal_length
                  y: petal_width
                  color: species
                id: line_chart
                type: graph
            title: My second page
        navigation:
            pages:
             First title:
                - My first page
             Second title:
                - My second page
        ```
    === "Result"
        [![CustomNavigation]][CustomNavigation]

    [CustomNavigation]: ../../assets/user_guides/navigation/custom_navigation.png


## Changing Selectors
If you want to have a different selector for dashboard navigation you have to provide the `selector` argument of the [`Navigation`][vizro.models.Navigation] with a different selector.

   ```
    Navigation(
        pages=["My first page", "My second page"]
        selector=NavBar()
    )
   ```

Currently available selectors are [`NavBar`][vizro.models.NavBar] and [`Accordion`][vizro.models.Accordion]. If `selector` is not defined it defaults to `Accordion`.


!!! example "Using `NavBar` selector"
    === "app.py"
        ```py
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm

        iris = px.data.iris()

        page_1 = vm.Page(
                    title="My first page",
                    components=[
                        vm.Graph(
                            id="scatter_chart",
                            figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")
                        ),
                    ],
        )
        page_2 = vm.Page(
                    title="My second page",
                    components=[
                        vm.Graph(
                            id="line_chart",
                            figure=px.line(iris, x="sepal_length", y="petal_width", color="species")
                        ),
                    ],
                )

        dashboard = vm.Dashboard(
                        pages=[page_1, page_2],
                        navigation=vm.Navigation(
                            pages=["My first page", "My second page"],
                            selector=vm.NavBar()
                        )
                    )

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
                  data_frame: iris
                  x: sepal_length
                  y: petal_width
                  color: species
                id: scatter_chart
                type: graph
            title: My first page
        - components:
             - figure:
                  _target_: line
                  data_frame: iris
                  x: sepal_length
                  y: petal_width
                  color: species
                id: line_chart
                type: graph
            title: My second page
        navigation:
            pages:
             First title:
                - My first page
             Second title:
                - My second page
            selector:
                type: nav_bar

        ```
    === "Result"
        [![NavigationIcons]][NavigationIcons]

    [NavigationIcons]: ../../assets/user_guides/navigation/navigation_icons.png


## Customizing Selectors

### Accordion
To customize default accordion provide a `dict` mapping of the page group title and a list of page IDs to the `pages` argument of the [`Accordion`][vizro.models.Accordion] model.

   ```
    Navigation(
        selector=Accordion(pages={"Title": ["My first page", "My second page"]})
    )
   ```
#### Accordion examples

- Simple Accordion

<table>
<tr>
<td><h3 style="width:350px" align="center"><img align="center" height="450" width="350" src="../../../assets/user_guides/navigation/simple_nav.png"></h3></td>
<td style="width:360px">

    ```py
    vm.Navigation(
        selector=vm.Accordion(
            pages=[
                "My first page",
                "My second page"
            ]
        )
    )
    ```

</td>
</tr>
</table>

- Customized Accordion

<table>
<tr>
<td><h3 style="width:350px" align="center"><img align="center" height="450" width="350" src="../../../assets/user_guides/navigation/simple_nav.png"></h3></td>
<td style="width:360px">

    ```py
    vm.Navigation(
        selector=vm.Accordion(
            pages={"Accordion title": [
                "My first page",
                "My second page"
            ]}
        )
    )
    ```

</td>
</tr>
</table>

### NavBar
To add navigation bar with icons to your dashboard provide [`NavBar`][vizro.models.NavBar] model to the `selector` argument of the `Navigation`.

NavBar model has two arguments `pages` and `items`.

- **`NavBar.pages`**

Use `pages` for default icon image and configuration.
   ```
    Navigation(
        selector=NavBar(pages=["My first page", "My second page"])
    )
   ```

- **`NavBar.items`**

Use `items` to add customization to the icons. `NavBar.items` is provided as list of `NavLink` models. `NavLink` model is responsible for building individual icons within navigation bar.

For further customizations of icons, you can refer to the [`NavLink`][vizro.models.NavLink] reference. Some popular choices are:

- customize icon image by providing name of the icon from the [Google Material Icon library](https://fonts.google.com/icons) to `icon` argument of `NavLink` model
- provide text string to be displayed in the icon tooltip on hover by using `text` argument of `NavLink` model

```
Navigation(
    selector=NavBar(
        items=[
            vm.NavLink(
                pages=["My first page"], icon="dashboard", text="Pages"
            ),
            vm.NavLink(
                pages=["My second page"], icon="summarize", text="Summary"
            ),
        ]
    )
)
```

!!! tip
    If you would like to turn off icon images you can specify the empty string `""` in the `icon` argument.

#### NavBar examples

- Navigation icons
<table>
<tr>
<td><h3 style="width:350px" align="center"><img align="center" height="450" width="350" src="../../../assets/user_guides/navigation/table_nav1.png"></h3></td>
<td style="width:360px">

    ```py

    vm.Navigation(
        selector=vm.NavBar(
            pages={
                "First icon": [
                    "My first page",
                    "My second page"
                ],
                "Second icon": [
                    "My third page"
                ]
            }
        )
    )

    ```

</td>
</tr>
</table>

- Customizing navigation icons

<table>
<tr>
<td><h3 style="width:350px" align="center"><img align="center" height="450" width="350" src="../../../assets/user_guides/navigation/tb_nav_1.png"></h3></td>
<td style="width:360px">

    ```py

    vm.Navigation(
        selector=vm.NavBar(
            items=[
                vm.NavLink(
                    pages=[
                        "My first page",
                        "My second page"
                    ],
                    icon="dashboard"),
                vm.NavLink(
                    pages=["My third page"],
                    icon="summarize"),
            ]
        )
    )

    ```
 </td>
 </tr>
 </table>
