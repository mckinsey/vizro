# How to use figures

This guide shows you how to add any [Dash component](https://dash.plotly.com/#open-source-component-libraries) that needs to be reactive to [filter](filters.md) and [parameter](parameters.md) controls.
If you want to add a static Dash component to your page, use [custom components](custom-components.md) instead.

[`Figure`][vizro.models.Figure] provides a flexible foundation for all types of reactive Dash components in Vizro.
The [`Graph`][vizro.models.Graph], [`Table`][vizro.models.Table] and [`AgGrid`][vizro.models.AgGrid] components are
specific implementations of `Figure`. They serve as intuitive shortcuts, embedding behaviors and interactions specific
to their purposes.

If these more specific models already achieve what you need then they should be used in preference to
the more generic `Figure`. Remember that it is possible to supply [custom charts](custom-charts.md) to `Graph`
and [custom tables](custom-tables.md) to `Table`.

There are already a few figure functions you can reuse, see the section on [KPI cards](#key-performance-indicator-kpi-cards)
for more details:

- [`kpi_card`][vizro.figures.kpi_card]
- [`kpi_card_reference`][vizro.figures.kpi_card_reference]

The following flowchart shows what you need to consider when choosing which model to use:

``` mermaid
graph TD
  first["`Does your desired component exist in Vizro, e.g. Graph, Table or AgGrid?`"]
  specific-component([Use the specific component])
  second["`Does your component need to be reactive to controls?`"]
  second-static([Use custom components])
  second-reactive([Use Figure])

  first -- Yes --> specific-component
  first -- No --> second
  second -- No --> second-static
  second -- Yes --> second-reactive

  click specific-component href "../components/"
  click second-static href "../custom-components/"
  click second-reactive href "#how-to-use-figures"

  classDef clickable color:#4051b5;
```


To add a `Figure` to your page:

1. Add the `Figure` model to the components argument of the [Page][vizro.models.Page] model.
2. Use an existing figure function from [`vizro.figures`](../API-reference/figure-callables.md) and pass it to the `figure` argument of the `Figure` model.

!!! example "Use existing figure functions"

    === "app.py"
        ```{.python pycafe-link}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.figures import kpi_card

        tips = px.data.tips

        # Create a layout with five rows and four columns. The KPI card is positioned in the first cell, while the remaining cells are empty.
        page = vm.Page(
            title="KPI card",
            layout=vm.Layout(grid=[[0, -1, -1, -1]] + [[-1, -1, -1, -1]] * 4),
            components=[
                vm.Figure(
                    figure=kpi_card( # For more information, refer to the API reference for kpi_card
                        data_frame=tips,
                        value_column="tip",
                        value_format="${value:.2f}",
                        icon="shopping_cart",
                        title="KPI card I",
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
                  title: KPI card I
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
            title: KPI card
        ```
    === "Result"
        [![Figure]][Figure]

    [Figure]: ../../assets/user_guides/figure/figure.png


### Key Performance Indicator (KPI) cards
A KPI card is a dynamic card that can display a single value, but optionally, can also include a title, icon, and reference value.
It is a common visual component to display key metrics in a dashboard. Vizro supports two pre-defined KPI card functions:

- [`kpi_card`](../API-reference/figure-callables.md#vizro.figures.kpi_card): A KPI card that shows a single value found
by performing an aggregation function (by default, `sum`) over a specified column.
Required arguments are `data_frame` and `value_column`.

- [`kpi_card_with_reference`](../API-reference/figure-callables.md#vizro.figures.kpi_card_reference): A KPI card that shows a single value
and a delta comparison to a reference value found by performing an aggregation function (by default, `sum`) over the specified columns.
Required arguments are `data_frame`, `value_column` and `reference_column`.

As described in the [API reference](../API-reference/figure-callables.md) and illustrated in the below example, these
functions have several arguments to customize your KPI cards. If you require a level of customization that is not
possible with the built-in functions then you can create a [custom figure](custom-figures.md).

!!! example "KPI card variations"

    === "app.py"
        ```{.python pycafe-link}
        import pandas as pd
        import vizro.models as vm
        from vizro import Vizro
        # For more information, refer to the API reference for kpi_card and kpi_card_reference
        from vizro.figures import kpi_card, kpi_card_reference

        df_kpi = pd.DataFrame({"Actual": [100, 200, 700], "Reference": [100, 300, 500], "Category": ["A", "B", "C"]})

        example_cards = [
            kpi_card(data_frame=df_kpi, value_column="Actual", title="KPI with value"),
            kpi_card(data_frame=df_kpi, value_column="Actual", title="KPI with aggregation", agg_func="median"),
            kpi_card(
                data_frame=df_kpi,
                value_column="Actual",
                title="KPI with formatting",
                value_format="${value:.2f}",
            ),
            kpi_card(
                data_frame=df_kpi,
                value_column="Actual",
                title="KPI with icon",
                icon="shopping_cart",
            ),
        ]

        example_reference_cards = [
            kpi_card_reference(
                data_frame=df_kpi,
                value_column="Actual",
                reference_column="Reference",
                title="KPI reference (pos)",
            ),
            kpi_card_reference(
                data_frame=df_kpi,
                value_column="Actual",
                reference_column="Reference",
                agg_func="median",
                title="KPI reference (neg)",
            ),
            kpi_card_reference(
                data_frame=df_kpi,
                value_column="Actual",
                reference_column="Reference",
                title="KPI reference with formatting",
                value_format="{value:.2f}€",
                reference_format="{delta:+.2f}€ vs. last year ({reference:.2f}€)",
            ),
            kpi_card_reference(
                data_frame=df_kpi,
                value_column="Actual",
                reference_column="Reference",
                title="KPI reference with icon",
                icon="shopping_cart",
            ),
        ]

        # Create a layout with four rows and columns. The KPI cards are positioned in the first eight cells, while the remaining cells are empty.
        page = vm.Page(
            title="KPI cards",
            layout=vm.Layout(grid=[[0, 1, 2, 3], [4, 5, 6, 7], [-1, -1, -1, -1], [-1, -1, -1, -1]]),

            components=[vm.Figure(figure=figure) for figure in example_cards + example_reference_cards],
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
                  data_frame: df_kpi
                  value_column: Actual
                  title: KPI with value
                type: figure
              - figure:
                  _target_: kpi_card
                  data_frame: df_kpi
                  value_column: Actual
                  title: KPI with aggregation
                  agg_func: median
                type: figure
              - figure:
                  _target_: kpi_card
                  data_frame: df_kpi
                  value_column: Actual
                  title: KPI with formatting
                  value_format: ${value:.2f}
                type: figure
              - figure:
                  _target_: kpi_card
                  data_frame: df_kpi
                  value_column: Actual
                  title: KPI with icon
                  icon: shopping_cart
                type: figure
              - figure:
                  _target_: kpi_card_reference
                  data_frame: df_kpi
                  value_column: Actual
                  reference_column: Reference
                  title: KPI reference (pos)
                type: figure
              - figure:
                  _target_: kpi_card_reference
                  data_frame: df_kpi
                  value_column: Actual
                  reference_column: Reference
                  agg_func: median
                  title: KPI reference (neg)
                type: figure
              - figure:
                  _target_: kpi_card_reference
                  data_frame: df_kpi
                  value_column: Actual
                  reference_column: Reference
                  title: KPI reference with formatting
                  value_format: "{value:.2f}€"
                  reference_format: "{delta:+.2f}€ vs. last year ({reference:.2f}€)"
                type: figure
              - figure:
                  _target_: kpi_card_reference
                  data_frame: df_kpi
                  value_column: Actual
                  reference_column: Reference
                  title: KPI reference with icon
                  icon: shopping_cart
                type: figure
            controls:
              - column: Category
                type: filter
            layout:
              grid: [[0, 1, 2, 3], [4, 5, 6, 7], [-1, -1, -1, -1], [-1, -1, -1, -1]]
            title: KPI cards
        ```
    === "Result"
        [![KPICards]][KPICards]

    [KPICards]: ../../assets/user_guides/figure/kpi_cards.png
