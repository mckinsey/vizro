# How to use the navigation panel

This guide shows you how to use and customize the left navigation panel in your dashboard.

The [`Dashboard`][vizro.models.Dashboard] model also accepts a `navigation` argument, where you can enter the [`Navigation`][vizro.models.Navigation] model. A [`Navigation`][vizro.models.Navigation] in your dashboard facilitates grouping and navigating through your pages.

## Using the default navigation

By default, a navigation panel with an accordion item per page and a default title of `SELECT PAGE` is added to your dashboard. To leverage the navigation panel, you do not need to configure anything on top.

!!! example "Default navigation"
    === "app.py"
        ```py
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm

        iris = px.data.iris()

        page_1 = vm.Page(
                    title="My first page",
                    components=[
                        vm.Graph(id="scatter_chart", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                    ],
                )
        page_2 = vm.Page(
                    title="My second page",
                    components=[
                        vm.Graph(id="line_chart", figure=px.line(iris, x="sepal_length", y="petal_width", color="species")),
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
        ```
    === "Result"
        [![DefaultNavigation]][DefaultNavigation]

    [DefaultNavigation]: ../../assets/user_guides/navigation/default_navigation.png

## Customizing your navigation panel

If you want to deviate from the default title `SELECT PAGE` and instead provide a title for a group of selected pages, do the following steps:

1. Provide a `dict` mapping of the page group title and a list of page IDs to the `pages` argument of the [`Navigation`][vizro.models.Navigation] model

    ```
    Navigation(pages={
        "First title": ["My first page"],
        "Second title": ["My second page"]})
    ```

2. Insert the [Navigation][vizro.models.Navigation] model into the `navigation` argument of the [Dashboard][vizro.models.Dashboard] model

    ```
    Dashboard(
        pages=[page_1, page_2],
        navigation=Navigation(pages={
            "First title": ["My first page"],
            "Second title": ["My second page"]})
    )
    ```

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
                        vm.Graph(id="scatter_chart", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                    ],
        )
        page_2 = vm.Page(
                    title="My second page",
                    components=[
                        vm.Graph(id="line_chart", figure=px.line(iris, x="sepal_length", y="petal_width", color="species")),
                    ],
                )

        dashboard = vm.Dashboard(
                        pages=[page_1, page_2],
                        navigation=vm.Navigation(pages={"First title": ["My first page"], "Second title": ["My second page"]})
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
Currently available selectors are [`NavBar`][vizro.models.NavBar] and [`Accordion`][vizro.models.Accordion]. If `selector` is not defined it defaults to `Accordion`.

If you want to add icons to your dashboard, you have to provide [`NavBar`][vizro.models.NavBar] model

   ```
    Dashboard(
        pages=[page_1, page_2],
        navigation=Navigation(
            pages=["My first page", "My second page"]
            selector=NavBar()
        )
    )
   ```

!!! example "Adding navigation icons"
    === "app.py"
        ```py
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm

        iris = px.data.iris()

        page_1 = vm.Page(
                    title="My first page",
                    components=[
                        vm.Graph(id="scatter_chart", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                    ],
        )
        page_2 = vm.Page(
                    title="My second page",
                    components=[
                        vm.Graph(id="line_chart", figure=px.line(iris, x="sepal_length", y="petal_width", color="species")),
                    ],
                )

        dashboard = vm.Dashboard(
                        pages=[page_1, page_2],
                        navigation=vm.Navigation(pages=["My first page", "My second page"], selector=vm.NavBar())
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
                type: navbar

        ```
    === "Result"
        [![NavigationIcons]][NavigationIcons]

    [NavigationIcons]: ../../assets/user_guides/navigation/navigation_icons.png


## Further customization

For further customizations of icons, you can always refer to the [`NavItem`][vizro.models.NavItem] reference. Some popular choices are:

- customize icon image by providing name of Google icon to `icon` argument of `NavItem` model
- provide additional text string to be displayed below the icon by using `text`argument of `NavItem` model
- provide text to be displayed in the icon tooltip on hover by using `tooltip` argument of `NavItem` model

If you want to customize icons in your dashboard, and do the following steps:

1. To be able to perform any of the customizations mentioned above, we need to build a list of `NavItem` models and provide it to the `items` argument of the `NavBar`.

   ```
    NavBar(
        items=[
            NavItem(pages=["My first page"], icon="dashboard", text="Dashboard"),
            NavItem(pages=["My second page"], icon="summarize", tooltip="Summarization page"),
       ]
    )
   ```

2. Insert the [NavBar][vizro.models.NavBar] model into the `selector` argument of the [Navigation]

   ```
    Navigation(
        selector=NavBar(
            items=[
                NavItem(pages=["My first page"], icon="dashboard", text="Dashboard"),
                NavItem(pages=["My second page"], icon="summarize", tooltip="Summarization page"),
            ]
        )
    )
   ```
3. Insert the [Navigation][vizro.models.Navigation] model into the `navigation` argument of the [Dashboard][vizro.models.Dashboard] model

   ```
    Dashboard(
        pages=[page_1, page_2],
        navigation=Navigation(
            selector=NavBar(
                items=[
                    NavItem(pages=["My first page"], icon="dashboard", text="Dashboard"),
                    NavItem(pages=["My second page"], icon="summarize", tooltip="Summarization page"),
               ]
           )
       )
   )
   ```

!!! example "Customizing navigation icons"
    === "app.py"
        ```py
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm

        iris = px.data.iris()

        page_1 = vm.Page(
                    title="My first page",
                    components=[
                        vm.Graph(id="scatter_chart", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                    ],
        )
        page_2 = vm.Page(
                    title="My second page",
                    components=[
                        vm.Graph(id="line_chart", figure=px.line(iris, x="sepal_length", y="petal_width", color="species")),
                    ],
                )

        dashboard = vm.Dashboard(
            pages=[page_1, page_2],
            navigation=vm.Navigation(
                selector=vm.NavBar(
                    items=[
                        vm.NavItem(pages=["My first page"], icon="dashboard"),
                        vm.NavItem(pages=["My second page"], icon="summarize"),
                    ]
                )
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
                type: navbar
                items:
                    - type: navitem
                        icon: dashboard
                        text: Dashboard
                        pages:
                            - My first page
                    - type: navitem
                        icon: summarize
                        tooltip: Summarization page
        ```
    === "Result"
        [![CustomIcons]][CustomIcons]

    [CustomIcons]: ../../assets/user_guides/navigation/icons_customized.png

!!! tip
    If you would like to turn off icon images you can specify the empty string `""` in the `icon` argument.

## Navigation options

##### Accordion navigation

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


##### Navigation icons

<table>
<tr>
<td><h3 style="width:350px" align="center"><img align="center" height="450" width="350" src="../../../assets/user_guides/navigation/table_nav1.png"></h3></td>
<td style="width:360px">

```py

vm.Navigation(
    selector=vm.NavBar(
        items=[
            vm.NavItem(
                pages=[
                    "My first page",
                    "My third page"]),
            vm.NavItem(
                pages=["My second page"])
        ]
    )
)

```

</td>
</tr>

</table>



##### Customizing navigation icons

<table>
<tr>
<td><h3 style="width:350px" align="center"><img align="center" height="450" width="350" src="../../../assets/user_guides/navigation/tb_nav_1.png"></h3></td>
<td style="width:360px">

```py

vm.Navigation(
    selector=vm.NavBar(
        items=[
            vm.NavItem(
                pages=[
                    "My first page",
                    "My third page"
                ],
                icon="dashboard"),
            vm.NavItem(
                pages=["My second page"],
                icon="summarize"),
        ]
)
)

```

</td>
</tr>

</table>
