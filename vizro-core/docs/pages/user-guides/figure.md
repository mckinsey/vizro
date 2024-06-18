# How to use figures

This guide shows you how to add any Dash component to Vizro that needs to be reactive to controls or actions in your page.
If you want to add a static Dash component to your page, use [custom components](custom-components.md) instead.

In essence, `Figure` is a higher-level abstraction, providing a flexible foundation for all types of reactive Dash
components in Vizro. The [`Graph`][vizro.models.Graph], [`Table`][vizro.models.Table] and [`AgGrid`][vizro.models.AgGrid]
components are specific implementations of `Figure`. They serve as intuitive shortcuts, embedding behaviors and
interactions specific to their purposes.

The following flowchart shows what you need to consider when choosing which model to use:

``` mermaid
graph TD
  first["`Does the Dash component you want to add exist in Vizro's components library already?`"]
  extend-component([Use an existing component and enhance it if required])
  second["`Does the new Dash component need to be reactive to controls or actions?`"]
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


To add a `Figure` to your page:

1. Add the `Figure` model to the components argument of the [Page][vizro.models.Page] model.
2. Use an existing figure function from [`vizro.figures`](../API-reference/figure-callables.md) and pass it to the `figure` argument of the `Figure` model.

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


### KPI Cards
A KPI card is a dynamic card that can display a single value. Optionally, a title, icon and reference value can be added.
It is a common visual component to display key metrics in a dashboard. Vizro supports two pre-defined KPI card functions:

- [`kpi_card`](../API-reference/figure-callables.md#kpi_card): A KPI card with a single value.
- [`kpi_card_with_reference`](../API-reference/figure-callables.md#kpi_card_with_reference): A KPI card with a single value and a reference value.

#### Existing KPI Card functions
!!! example "KPI Card Variations"

    === "app.py"
        ```py
        import pandas as pd
        import vizro.models as vm
        from vizro import Vizro
        from vizro.figures import kpi_card, kpi_card_reference

        df = pd.DataFrame([[67434, 65553, "A"], [6434, 6553, "B"], [34, 53, "C"]], columns=["Actual", "Reference", "Category"])

        page = vm.Page(
            title="KPI Indicators",
            layout=vm.Layout(grid=[[0, 1, 2, 3], [4, 5, 6, 7], [-1, -1, -1, -1], [-1, -1, -1, -1]]),
            components=[
                vm.Figure(figure=kpi_card(data_frame=df, value_column="Actual", title="KPI with value")),
                vm.Figure(figure=kpi_card(data_frame=df, value_column="Actual", title="KPI with aggregation", agg_func="mean")),
                vm.Figure(
                    figure=kpi_card(
                        data_frame=df,
                        value_column="Actual",
                        title="KPI with custom formatting",
                        value_format="${value:.2f}",
                    )
                ),
                vm.Figure(
                    figure=kpi_card(
                        data_frame=df,
                        value_column="Actual",
                        title="KPI with icon",
                        icon="shopping_cart",
                    )
                ),
                vm.Figure(
                    figure=kpi_card_reference(
                        data_frame=df,
                        value_column="Reference",
                        reference_column="Actual",
                        title="KPI with reference (neg)",
                    )
                ),
                vm.Figure(
                    figure=kpi_card_reference(
                        data_frame=df,
                        value_column="Actual",
                        reference_column="Reference",
                        title="KPI with reference (pos)",
                    )
                ),
                vm.Figure(
                    figure=kpi_card_reference(
                        data_frame=df,
                        value_column="Reference",
                        reference_column="Actual",
                        title="KPI with reference and custom formatting",
                        value_format="{value:.2f}$",
                        reference_format="{delta:.2f}$ vs. last year ({reference:.2f}$)",
                    )
                ),
                vm.Figure(
                    figure=kpi_card_reference(
                        data_frame=df,
                        value_column="Actual",
                        reference_column="Reference",
                        value_format="${value:.2f}",
                        title="KPI with reference and icon",
                        icon="shopping_cart",
                    ),
                ),
            ],
            controls=[vm.Filter(column="Category")],
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
        [![KPICards]][KPICards]

    [KPICards]: ../../assets/user_guides/figure/kpi_cards.png


#### Custom KPI Card function
!!! example "KPI Card Variations"

    === "app.py"
        ```py
        import pandas as pd
        import vizro.models as vm
        from vizro import Vizro
        from vizro.figures import kpi_card, kpi_card_reference

        df = pd.DataFrame([[67434, 65553, "A"], [6434, 6553, "B"], [34, 53, "C"]], columns=["Actual", "Reference", "Category"])

        page = vm.Page(
            title="KPI Indicators",
            layout=vm.Layout(grid=[[0, 1, 2, 3], [4, 5, 6, 7], [-1, -1, -1, -1], [-1, -1, -1, -1]]),
            components=[
                vm.Figure(figure=kpi_card(data_frame=df, value_column="Actual", title="KPI with value")),
                vm.Figure(figure=kpi_card(data_frame=df, value_column="Actual", title="KPI with aggregation", agg_func="mean")),
                vm.Figure(
                    figure=kpi_card(
                        data_frame=df,
                        value_column="Actual",
                        title="KPI with custom formatting",
                        value_format="${value:.2f}",
                    )
                ),
                vm.Figure(
                    figure=kpi_card(
                        data_frame=df,
                        value_column="Actual",
                        title="KPI with icon",
                        icon="shopping_cart",
                    )
                ),
                vm.Figure(
                    figure=kpi_card_reference(
                        data_frame=df,
                        value_column="Reference",
                        reference_column="Actual",
                        title="KPI with reference (neg)",
                    )
                ),
                vm.Figure(
                    figure=kpi_card_reference(
                        data_frame=df,
                        value_column="Actual",
                        reference_column="Reference",
                        title="KPI with reference (pos)",
                    )
                ),
                vm.Figure(
                    figure=kpi_card_reference(
                        data_frame=df,
                        value_column="Reference",
                        reference_column="Actual",
                        title="KPI with reference and custom formatting",
                        value_format="{value:.2f}$",
                        reference_format="{delta:.2f}$ vs. last year ({reference:.2f}$)",
                    )
                ),
                vm.Figure(
                    figure=kpi_card_reference(
                        data_frame=df,
                        value_column="Actual",
                        reference_column="Reference",
                        value_format="${value:.2f}",
                        title="KPI with reference and icon",
                        icon="shopping_cart",
                    ),
                ),
            ],
            controls=[vm.Filter(column="Category")],
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
        [![KPICards]][KPICards]

    [KPICards]: ../../assets/user_guides/figure/kpi_cards.png
