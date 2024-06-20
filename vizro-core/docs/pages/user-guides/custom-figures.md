# How to create custom figures

This guide explains how to create custom figures, which is useful when you need a component that reacts to
[filter](filters.md) and [parameter](parameters.md) controls.

### When to use a custom figure
You should use custom figures if **both** of the following conditions are met:

- You need a figure that doesn't fit into the existing predefined components ([`Graph`][vizro.models.Graph], [`Table`][vizro.models.Table] or [`AgGrid`][vizro.models.AgGrid]).
- You need a figure that isn't available in our pre-defined figure functions [`vizro.figures`](../API-reference/figure-callables.md).


### Steps to create a custom figure

1. Define a function that returns a [Dash component](https://dash.plotly.com/#open-source-component-libraries).
2. Decorate it with `@capture("figure")`.
3. The function must accept a `data_frame` argument (of type `pandas.DataFrame`).
4. The figure should be derived from and require only one `pandas.DataFrame`. Dataframes from other arguments
will not react to dashboard controls such as [`Filter`](filters.md).

The below examples can be used as a base to build more sophisticated figures.

### Examples of custom figures

#### Custom KPI card
If you wish to change the design or content of our existing KPI (key performance indicator) cards from
[`vizro.figures`](../API-reference/figure-callables.md), you can do so by following the steps described above.

For instance, if you prefer the icon to be positioned on the right side of the title instead of the left,
adjust the return statement of the function decorated with `@capture("figure")`.

<!-- vale off -->
!!! example "Custom KPI card"
    === "app.py"
        ```py
        from typing import Optional

        import dash_bootstrap_components as dbc
        import pandas as pd
        import vizro.models as vm
        import vizro.plotly.express as px
        from dash import html
        from vizro import Vizro
        from vizro.figures import kpi_card
        from vizro.models.types import capture

        tips = px.data.tips


        @capture("figure")  # (1)!
        def custom_kpi_card(
            data_frame: pd.DataFrame,
            value_column: str,
            *,
            value_format: str = "{value}",
            agg_func: str = "sum",
            title: Optional[str] = None,
            icon: Optional[str] = None,
        ) -> dbc.Card:  # (2)!
            """Creates a custom KPI Card."""
            title = title or f"{agg_func} {value_column}".title()
            value = data_frame[value_column].agg(agg_func)

            return dbc.Card(
                [
                    dbc.CardHeader(
                        [
                            html.H2(title),
                            html.P(icon, className="material-symbols-outlined") if icon else None,  # (3)!
                        ],
                    ),
                    dbc.CardBody([value_format.format(value=value)]),
                ],
                className="card-kpi",
            )


        page = vm.Page(
            title="Create your own KPI Card",
            layout=vm.Layout(grid=[[0, 1, -1, -1]] + [[-1, -1, -1, -1]] * 3),  # (4)!
            components=[
                vm.Figure(
                    figure=kpi_card(  # (5)!
                        data_frame=tips,
                        value_column="tip",
                        value_format="${value:.2f}",
                        icon="shopping_cart",
                        title="Default KPI Card",
                    )
                ),
                vm.Figure(
                    figure=custom_kpi_card(  # (6)!
                        data_frame=tips,
                        value_column="tip",
                        value_format="${value:.2f}",
                        icon="payment",
                        title="Custom KPI Card",
                    )
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. Here we decorate our custom figure function with the `@capture("figure")` decorator.
        2. The custom figure function needs to have a `data_frame` argument and return a `Dash` component.
        3. We adjust the return statement to include the icon on the right side of the title.
        4. This creates a [`layout`](layouts.md) with four rows and columns. The KPI cards are positioned in the first two cells, while the remaining cells are empty.
        5. For more information, refer to the API reference for the  [`kpi_card`](../API-reference/figure-callables.md#kpi_card).
        6. Our custom figure function `custom_kpi_card` now needs to be passed on to the `vm.Figure`.

    === "app.yaml"
        ```yaml
        # Custom figures are currently only possible via python configuration
        ```
    === "Result"
        [![CustomKPI]][CustomKPI]

    [CustomKPI]: ../../assets/user_guides/figure/custom_kpi.png

<!-- vale on -->

#### Dynamic number of cards
The example below shows how to create multiple cards created from a `pandas.DataFrame` where the
number of cards displayed dynamically adjusts based on a `vm.Parameter`.

<!-- vale off -->
!!! example "Dynamic number of cards"
    === "app.py"
        ```py
        from typing import Optional

        import dash_bootstrap_components as dbc
        import pandas as pd
        import vizro.models as vm
        from dash import dcc, html
        from vizro import Vizro
        from vizro.models.types import capture

        df = pd.DataFrame(
            {
                "text": [
                            "Lorem ipsum dolor sit amet, consetetur sadipscing no sea elitr sed diam nonumy.",
                            "Sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat.",
                            "Sed diam voluptua. At vero eos et accusam et justo no duo dolores et ea rebum.",
                            "Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
                            "Lorem ipsum dolor sit amet, consetetur sadipscing no sea est elitr dolor sit amet.",
                            "Sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat.",
                        ]
                        * 2
            }
        )


        @capture("figure")  # (1)!
        def multiple_cards(data_frame: pd.DataFrame, n_rows: Optional[int] = 1) -> html.Div:  # (2)!
            """Creates a list with a variable number of `vm.Card` components from the provided data_frame.

            Args:
                data_frame: Data frame containing the data.
                n_rows: Number of rows to use from the data_frame. Defaults to 1.

            Returns:
                html.Div with a list of dbc.Card objects generated from the data.

            """
            texts = data_frame.head(n_rows)["text"]
            return html.Div(
                [dbc.Card(dcc.Markdown(f"### Card #{i + 1}\n{text}")) for i, text in enumerate(texts)],
                className="multiple-cards-container",
            )


        page = vm.Page(
            title="Page with variable number of cards",
            components=[vm.Figure(id="my-figure", figure=multiple_cards(data_frame=df))],  # (3)!
            controls=[
                vm.Parameter(
                    targets=["my-figure.n_rows"],  # (4)!
                    selector=vm.Slider(min=2, max=12, step=2, value=8, title="Number of cards to display"),
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. Here we decorate our custom figure function with the `@capture("figure")` decorator.
        2. The custom figure function needs to have a `data_frame` argument and return a `Dash` component.
        3. Our decorated figure function `multiple_cards` now needs to be passed on to the `vm.Figure`.
        4. We add a [`vm.Parameter`](parameters.md) to dynamically adjust the number of cards displayed.
           The parameter targets the `n_rows` argument of the `multiple_cards` function, determining the number of rows
           taken from the data.

    === "css"
        ```css
        .multiple-cards-container {
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
        }

        .figure-container {
          height: unset;
          width: unset;
        }

        .figure-container .card {
          height: 210px;
          width: 240px;
        }
        ```
    === "app.yaml"
        ```yaml
        # Custom figures are currently only possible via python configuration
        ```
    === "Result"
        [![CustomFigure]][CustomFigure]

    [CustomFigure]: ../../assets/user_guides/figure/custom_multiple_cards.png


<!-- vale on -->
