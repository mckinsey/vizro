# How to use navigation
This guide shows you how to add custom navigation to your dashboard.

A [`Navigation`][hyphen.models.Navigation] lets you arrange and group your pages. In many cases grouping the pages within the dashboard might be necessary. This can easily be achieved by providing `navigation` argument to your dashboard. 

## Using the default navigation

By default, the navigation comes as an accordion that has default title of 'SELECT PAGE'. You don't have to configure anything for this type of navigation. 

!!! example "Adding custom navigation"
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

        dashboard = vm.Dashboard(
                        pages=[page_1],
                    )

        Vizro().build(dashboard).run()
        ```
    === "app.yaml"
        ```yaml
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration - see from_yaml example
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
        ```

## Using custom navigation 

You can customize navigation of your dashboard by adding the [`Navigation`][hyphen.models.Navigation] model into the `navigation` argument of the [`Dashboard`][hyphen.models.Dashboard] model. 

#### 1. Customising accordion title: 
[`Navigation`][hyphen.models.Navigation] requires only the `pages` argument, which denotes the grouping of pages in the Accordion. For more information about Accordion component, please refer to the official documentation [here](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/accordion/). 

- To group the pages under different sections, provide `pages` in a dictionary format, where each key will act as the section title of the accordion.


!!! example "Adding custom navigation"
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
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration - see from_yaml example
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
After running the dashboard, you can access the dashboard via `localhost:8050`.