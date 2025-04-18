# How to create custom figures

This guide explains how to create custom figures, which is useful when you need a component that reacts to [filter](filters.md) and [parameter](parameters.md) controls.

The [`Figure`][vizro.models.Figure] model accepts the `figure` argument, where you can enter _any_ custom figure function as explained in the [user guide on figures](figure.md).

## When to use a custom figure

As described in the flowchart detailing [when to use `Figure`](figure.md), custom figures should be used if **both** of the following conditions are met:

- You need a figure that doesn't fit into the existing built-in components ([`Graph`][vizro.models.Graph], [`Table`][vizro.models.Table] or [`AgGrid`][vizro.models.AgGrid]).
- You need a figure that isn't available in our built-in figure functions [`vizro.figures`](../API-reference/figure-callables.md).

## Steps to create a custom figure

1. Define a function that returns a [Dash component](https://dash.plotly.com/#open-source-component-libraries). This can, but does not need to, be based on code in our pre-defined figure functions in [`vizro.figures`](../API-reference/figure-callables.md).
1. Decorate it with `@capture("figure")`.
1. The function must accept a `data_frame` argument (of type `pandas.DataFrame`).
1. The figure should be derived from and require only one `pandas.DataFrame`. Dataframes from other arguments will not react to dashboard controls such as [`Filter`](filters.md).
1. Pass your function to the `figure` argument of the [`Figure`][vizro.models.Figure] model.

The following examples can be used as a base to build more sophisticated figures.

## Examples of custom figures

### Custom KPI card

To change the design or content of our existing KPI (key performance indicator) cards from [`vizro.figures`](../API-reference/figure-callables.md), you can do so by following the steps described above.

For instance, to make a KPI card with the icon positioned on the right side of the title instead of the left, copy and paste the [source code of `kpi_card`](../API-reference/figure-callables.md#vizro.figures.kpi_card) and adjust the return statement of the function.

<!-- vale off -->

!!! example "Custom KPI card"

    === "app.py"

        ```{.python pycafe-link}
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
            """Creates a custom KPI card."""
            title = title or f"{agg_func} {value_column}".title()
            value = data_frame[value_column].agg(agg_func)

            header = dbc.CardHeader(
                    [

                        html.H4(title, className="card-kpi-title"),
                        html.P(icon, className="material-symbols-outlined") if icon else None,  # (3)!
                    ]
                )
            body = dbc.CardBody([value_format.format(value=value)])
            return dbc.Card([header, body], class_name="card-kpi")


        page = vm.Page(
            title="Create your own KPI card",
            layout=vm.Flex(direction="row"),  # (4)!
            components=[
                vm.Figure(
                    figure=kpi_card(  # (5)!
                        data_frame=tips,
                        value_column="tip",
                        value_format="${value:.2f}",
                        icon="shopping_cart",
                        title="Default KPI card",
                    )
                ),
                vm.Figure(
                    figure=custom_kpi_card(  # (6)!
                        data_frame=tips,
                        value_column="tip",
                        value_format="${value:.2f}",
                        icon="payment",
                        title="Custom KPI card",
                    )
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. Here we decorate our custom figure function with the `@capture("figure")` decorator.
        1. The custom figure function needs to have a `data_frame` argument and return a `Dash` component.
        1. We adjust the return statement to include the icon on the right side of the title. This is achieved by swapping the order of the `html.H2` and `html.P` compared to the original `kpi_card`.
        1. We use a [`Flex`][vizro.models.Flex] layout with `direction="row"` to ensure the KPI cards are placed side by side and only take up as much space as needed.
        1. For more information, refer to the API reference for the [`kpi_card`](../API-reference/figure-callables.md#vizro.figures.kpi_card).
        1. Our custom figure function `custom_kpi_card` now needs to be passed on to the `vm.Figure`.

    === "app.yaml"

        Custom figures are currently only possible via Python configuration.

    === "Result"

        [![CustomKPI]][customkpi]

<!-- vale on -->

### Dynamic HTML header

You can create a custom figure for any [Dash component](https://dash.plotly.com/#open-source-component-libraries). Below is an example of a custom figure that returns a `html.H2` component that dynamically updates based on the selected name from a filter.

<!-- vale off -->

!!! example "Dynamic HTML header"

    === "app.py"

        ```{.python pycafe-link}
        import pandas as pd
        import vizro.models as vm
        from dash import html
        from vizro import Vizro
        from vizro.models.types import capture

        df = pd.DataFrame({"names": ["Emma", "Jack", "Sophia", "Ethan", "Mia"]})


        @capture("figure")  # (1)!
        def dynamic_html_header(data_frame: pd.DataFrame, column: str) -> html.H2:  # (2)!
            """Creates a HTML header that dynamically updates based on controls."""
            return html.H2(f"Good morning, {data_frame[column].iloc[0]}! ☕ ⛅")  # (3)!


        page = vm.Page(
            title="Dynamic HTML header",
            components=[vm.Figure(figure=dynamic_html_header(data_frame=df, column="names"))],  # (4)!
            controls=[vm.Filter(column="names", selector=vm.RadioItems(title="Select a name"))],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. Here we decorate our custom figure function with the `@capture("figure")` decorator.
        1. The custom figure function needs to have a `data_frame` argument and return a `Dash` component.
        1. We return a `html.H2` component that dynamically updates based on the selected name from the filter.
        1. Our custom figure function `dynamic_html_header` now needs to be passed on to the `vm.Figure`.

    === "app.yaml"

        Custom figures are currently only possible via Python configuration.

    === "Result"

        [![CustomHTML]][customhtml]

<!-- vale on -->

### Dynamic number of cards

The example below shows how to create multiple cards created from a `pandas.DataFrame` where the number of cards displayed dynamically adjusts based on a `vm.Parameter`.

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

        text = [
            "Lorem ipsum dolor sit amet, consetetur sadipscing no sea elitr sed diam nonumy.",
            "Sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat.",
            "Sed diam voluptua. At vero eos et accusam et justo no duo dolores et ea rebum.",
            "Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
            "Lorem ipsum dolor sit amet, consetetur sadipscing no sea est elitr dolor sit amet.",
            "Sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat.",
        ]

        df = pd.DataFrame({"text": text * 2})


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
                [dbc.Card(dcc.Markdown(f"### Card #{i}\n{text}")) for i, text in enumerate(texts, 1)],
                className="multiple-cards-container",
            )


        page = vm.Page(
            title="Page with variable number of cards",
            components=[vm.Figure(id="my-figure", figure=multiple_cards(data_frame=df))],  # (3)!
            controls=[
                vm.Parameter(
                    targets=["my-figure.n_rows"],  # (4)!
                    selector=vm.Slider(min=2, max=12, step=2, value=10, title="Number of cards to display"),
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. Here we decorate our custom figure function with the `@capture("figure")` decorator.
        1. The custom figure function needs to have a `data_frame` argument and return a `Dash` component.
        1. Our decorated figure function `multiple_cards` now needs to be passed on to the `vm.Figure`.
        1. We add a [`vm.Parameter`](parameters.md) to dynamically adjust the number of cards displayed. The parameter targets the `n_rows` argument of the `multiple_cards` function, determining the number of rows taken from the data.

        <img src=https://py.cafe/logo.png alt="PyCafe logo" width="30"><b><a target="_blank" href="https://py.cafe/vizro-official/vizro-dynamic-cards">Run and edit this code in PyCafe</a></b>

    === "styling.css"

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

        Custom figures are currently only possible via Python configuration.

    === "Result"

        [![CustomFigure]][customfigure]

<!-- vale on -->

[customfigure]: ../../assets/user_guides/figure/custom_multiple_cards.png
[customhtml]: ../../assets/user_guides/figure/custom_html.png
[customkpi]: ../../assets/user_guides/figure/custom_kpi.png
