# How to use figures

This guide shows you how to add any dash component to Vizro that needs to be reactive to controls or actions in your page.
If you want to add a static Dash component to your page, use [custom components](custom-components.md) instead.

In essence, `Figure` is a higher-level abstraction, providing a flexible foundation for all types of reactive Dash
components in Vizro. The [`Graph`][vizro.models.Graph], [`Table`][vizro.models.Table] and [`AgGrid`][vizro.models.AgGrid]
are specific implementations of the `Figure`. They serve as intuitive shortcuts, embedding behaviors and
interactions specific to their purposes.

The following flowchart shows what you need to consider when choosing which model to use:

``` mermaid
graph TD
  first["`Does the dash component you want to add exist in our components library already?`"]
  extend-component([Use our existing components and enhance them if required])
  second["`Does the new dash component need to be reactive to controls or actions?`"]
  second-static([Use custom components])
  second-reactive([Use Figure and provide a custom function])

  first -- Yes --> extend-component
  first -- No --> second
  second -- No --> second-static
  second -- Yes --> second-reactive

  click extend-component href "../custom-components/#extend-an-existing-component"
  click second-static href "../custom-components/#create-a-new-component"
  click second-reactive href "#how-to-use-figures"

  classDef clickable color:#4051b5;
```


To add a `Figure` to your page, do the following:

- add the `Figure` model to the components argument of the [Page][vizro.models.Page] model.
- use an existing figure function from [`vizro.figures`](../API-reference/figure-callables.md) and pass it to the `figure` argument of the `Figure` model.

!!! example "Use existing figure functions"

    === "app.py"
        ```py
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.figures import kpi_card

        tips = px.data.tips

        page = vm.Page(
            title="KPI Indicators",
            layout=vm.Layout(grid=[[0, -1, -1, -1]] + [[-1, -1, -1, -1]] * 4),
            components=[
                vm.Figure(
                    figure=kpi_card(
                        data_frame=tips,
                        value_column="tip",
                        value_format="${value:.2f}",
                        icon="shopping_cart",
                        title="KPI Card I",
                    )
                )
            ],
            controls=[vm.Filter(column="day", selector=vm.RadioItems())],
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
              - figure:
                  _target_: kpi_card
                  data_frame: tips
                  value_column: tip
                  value_format: ${value:.2f}
                  icon: shopping_cart
                  title: KPI Card I
                type: figure
            controls:
              - column: day
                type: filter
                selector:
                  type: radio_items
            layout:
              grid:
                [
                  [0, -1, -1, -1],
                  [-1, -1, -1, -1],
                  [-1, -1, -1, -1],
                  [-1, -1, -1, -1],
                  [-1, -1, -1, -1],
                ]
            title: KPI Indicators
        ```
    === "Result"
        [![Figure]][Figure]

    [Figure]: ../../assets/user_guides/figure/figure.png


If the existing figure functions from [`vizro.figures`](../API-reference/figure-callables.md) do not serve your purpose,
there is always the option to create a [custom Figure](custom-figures.md).
