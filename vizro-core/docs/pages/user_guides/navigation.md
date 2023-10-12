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
